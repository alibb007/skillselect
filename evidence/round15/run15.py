"""Round 15. usage: run15.py label fable|sonnet|haiku [first] | score   (see RULES15.md)
The lab folder (ledger, budget cap, the claude command) is $SKILLSELECT_LAB, or ../harness."""
import importlib.util, json, os, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(H))
sys.path.insert(0, os.environ.get('SKILLSELECT_LAB') or os.path.join(os.path.dirname(H), 'harness')); import lab
WHAT = sys.argv[1]
JUDGES = dict(fable='claude-fable-5-2', sonnet='claude-sonnet-5-5', haiku='claude-haiku-5-5')
jobs = [j for j in json.load(open(H + '/../round9/jobs.json')) if j['set'] == 'sealed']
raw9 = json.load(open(H + '/../round9/raw9_sealed.json')); L9 = json.load(open(H + '/../round9/label9_sealed.json'))
raw12 = json.load(open(H + '/../round12/raw12.json')); L12 = json.load(open(H + '/../round12/label12.json')); K12 = json.load(open(H + '/../round12/keep12.json'))
K9 = json.load(open(H + '/../round9/keep9_sealed.json')); K11 = json.load(open(H + '/../round11/keep11_sealed.json'))
START = float(open(H + '/start.txt').read()) if os.path.exists(H + '/start.txt') else lab.spent(); open(H + '/start.txt', 'w').write(str(START))
CAP = 5.5
# round 9's and round 12's label prompt, word for word
LABEL = ("You judge which skills would help with a request. A skill is ON when its own description says it makes or does the thing the person asked for, or a named part of it. "
         "It is OFF when it only sits next to the job, is one repository's or one product's private helper, is hosting, or is a general collection. Judge from the text given, nothing else.\n"
         "Return only JSON: {\"installed\": [names of the installed skills that are ON], \"github\": [numbers of the GitHub skills that are ON]}.")
LOCK = threading.Lock()


def installed_skills():
    sb = os.environ['SANDBOX50']; sp = importlib.util.spec_from_file_location('f310', ROOT + '/skills/skillselect/scripts/find_skills.py'); F = importlib.util.module_from_spec(sp); sp.loader.exec_module(F)
    out = []
    for n in sorted(os.listdir(sb)):
        name, desc = F.front(open(os.path.join(sb, n, 'SKILL.md'), errors='replace').read(8000)); out.append(dict(name=name or n, desc=desc[:400]))
    return out


def ask(judge, prompt, kind, meta):
    """One call with no tools, answered by the judge's own model family or the run stops. Returns the parsed JSON, or None after two answers that are not JSON."""
    for attempt in (1, 2):
        lab.guard()
        if lab.spent() - START > CAP: lab.stop('round 15 cap')
        cmd = [lab.CL, '-p', prompt, '--model', JUDGES[judge], '--system-prompt', LABEL, '--tools', '', '--setting-sources', 'project', '--output-format', 'json', '--no-session-persistence', '--strict-mcp-config', '--mcp-config', lab.L + '/nomcp.json']
        t0 = time.time(); p = subprocess.run(cmd, cwd=lab.L + '/bare', capture_output=True, text=True, timeout=300, stdin=subprocess.DEVNULL)
        try: r = json.loads(p.stdout)
        except ValueError: lab.stop(f'{kind}: no JSON from claude: {p.stdout[:120]!r} {p.stderr[:120]!r}')
        models = list((r.get('modelUsage') or {}).keys()); text = r.get('result') or ''
        if not models or not all(m.startswith('claude-' + judge) for m in models) or 'Not logged in' in text[:40]: lab.stop(f'{kind}: not {judge} or not logged in: models={models} text={text[:60]!r}')
        u = r.get('usage') or {}
        lab.log(dict(kind=kind, meta=dict(meta, judge=judge, attempt=attempt), models=models, cost=r.get('total_cost_usd', 0), sec=round(time.time() - t0, 1), tok_in=u.get('input_tokens', 0) + u.get('cache_creation_input_tokens', 0) + u.get('cache_read_input_tokens', 0), tok_out=u.get('output_tokens', 0)))
        d = lab.jparse(text)
        if isinstance(d, dict) and isinstance(d.get('installed', []), list) and isinstance(d.get('github', []), list): return d, models
    return None, models


if WHAT == 'label':
    judge = sys.argv[2]; first = len(sys.argv) > 3 and sys.argv[3] == 'first'; skills = installed_skills(); names = {s['name'] for s in skills}; assert len(skills) == 50
    outp = H + f'/label15_{judge}.json'; out = json.load(open(outp)) if os.path.exists(outp) else {}
    def one(j):
        v = out.get(j['id']) or {}
        if 'p1' not in v:
            desc = {(o['repo'], o['skill']): o['desc'] for o in raw9[j['id']]['A']['github'] + raw9[j['id']]['B']['pool']}; cands = [tuple(x) for x in L9[j['id']]['github_judged']]
            p = ("Request: " + j['request'] + "\n\nINSTALLED SKILLS:\n" + "\n".join(f"- {s['name']}: {s['desc']}" for s in skills) +
                 "\n\nGITHUB SKILLS:\n" + ("\n".join(f"{i + 1}. {s}: {desc[(r, s)]}" for i, (r, s) in enumerate(cands)) or "(none)"))
            d, models = ask(judge, p, 'v15_label_p1', {'job': j['id']})
            v['p1'] = dict(failed=True) if d is None else dict(installed=[n for n in d.get('installed', []) if n in names], github_on=[list(cands[i - 1]) for i in d.get('github', []) if isinstance(i, int) and 0 < i <= len(cands)])
            v['model'] = models
        if 'p2' not in v and not (first or os.environ.get('SKIP_P2')):
            cands = [tuple(x) for x in L12[j['id']]['judged']]; desc = {(o['repo'], o['skill']): o['desc'] for a in 'ABC' for o in raw12[j['id']][a]}
            if not cands: v['p2'] = dict(on=[])
            else:
                p = "Request: " + j['request'] + "\n\nINSTALLED:\n(none)\n\nGITHUB:\n" + "\n".join(f"{i + 1}. {s} ({r}): {desc[(r, s)]}" for i, (r, s) in enumerate(cands))
                d, models = ask(judge, p, 'v15_label_p2', {'job': j['id']})
                v['p2'] = dict(failed=True) if d is None else dict(on=[list(cands[i - 1]) for i in d.get('github', []) if isinstance(i, int) and 0 < i <= len(cands)])
        with LOCK:
            out[j['id']] = v; json.dump(out, open(outp, 'w'), indent=1, ensure_ascii=False)
    todo = jobs[:1] if first else jobs
    with ThreadPoolExecutor(1 if first else 4) as ex: list(ex.map(one, todo))
    rows = [json.loads(l) for l in open(lab.L + '/ledger.jsonl')]; mine = [r for r in rows if r.get('kind', '').startswith('v15_label') and (r.get('meta') or {}).get('judge') == judge]
    print(judge, sorted({m for v in out.values() for m in v.get('model', [])}), '| requests', len(out), '| calls', len(mine), '| $', round(sum(r['cost'] or 0 for r in mine), 3),
          '| p1 $/call', round(sum(r['cost'] or 0 for r in mine if r['kind'].endswith('p1')) / max(1, sum(1 for r in mine if r['kind'].endswith('p1'))), 4),
          '| failed', sum(1 for v in out.values() for k in ('p1', 'p2') if (v.get(k) or {}).get('failed')), '| round spend $', round(lab.spent() - START, 2))

if WHAT == 'score':
    skills = installed_skills(); names = [s['name'] for s in skills]; res = dict(judges={}, agreement={}, round11={}, round12={}, round9_keep={})
    labels = dict(opus={j['id']: dict(p1=dict(installed=L9[j['id']]['installed'], github_on=L9[j['id']]['github_on']), p2=dict(on=L12[j['id']]['on'])) for j in jobs})
    for judge in JUDGES:
        p = H + f'/label15_{judge}.json'
        if os.path.exists(p):
            labels[judge] = json.load(open(p)); res['judges'][judge] = dict(model=sorted({m for v in labels[judge].values() for m in v.get('model', [])}), failed_p1=sum(1 for v in labels[judge].values() if v.get('p1', {}).get('failed')), failed_p2=sum(1 for v in labels[judge].values() if v.get('p2', {}).get('failed')))
    ok = lambda lab_, jid, part: part in lab_.get(jid, {}) and not lab_[jid][part].get('failed')

    def vec(lab_, jid, part):  # every judged item of one request as 0/1
        v = lab_[jid][part]
        if part == 'p1': return [int(n in v['installed']) for n in names] + [int(x in v['github_on']) for x in L9[jid]['github_judged']]
        return [int(x in v['on']) for x in L12[jid]['judged']]

    def kappa(a, b):
        n = len(a); po = sum(x == y for x, y in zip(a, b)) / n; pa, pb = sum(a) / n, sum(b) / n; pe = pa * pb + (1 - pa) * (1 - pb)
        return round(100 * po, 1), round((po - pe) / (1 - pe), 2) if pe < 1 else 1.0

    for judge in [k for k in labels if k != 'opus']:
        for part, tag in (('p1', 'installed and round 9 GitHub'), ('p2', 'round 12 GitHub picks')):
            a, b = [], []
            for j in jobs:
                if ok(labels[judge], j['id'], part): a += vec(labels['opus'], j['id'], part); b += vec(labels[judge], j['id'], part)
            if a:
                same, k = kappa(a, b); res['agreement'][f'{judge} vs opus, {tag}'] = dict(items=len(a), opus_on=sum(a), judge_on=sum(b), both_on=sum(x and y for x, y in zip(a, b)), same_pct=same, kappa=k)
    for judge, lab_ in labels.items():
        js = [j for j in jobs if ok(lab_, j['id'], 'p1')]; fits = {j['id']: set(lab_[j['id']]['p1']['installed']) for j in js}
        C = {j['id']: K9[j['id']]['installed'] for j in js}; D = {j['id']: K11[j['id']]['installed'] + K11[j['id']]['found_by_reading'] for j in js}; R = {j['id']: K11[j['id']]['found_by_reading'] for j in js}
        r = dict(requests=len(js), fits=sum(len(f) for f in fits.values()))
        for arm, kept in (('C', C), ('D', D)):
            r[arm] = dict(found=sum(len(fits[k] & set(v)) for k, v in kept.items()), kept=sum(len(v) for v in kept.values()))
        r['by_reading'] = dict(added=sum(len(v) for v in R.values()), added_that_fit=sum(len(fits[k] & set(v)) for k, v in R.items()), which=[[k, n, n in fits[k]] for k, v in R.items() for n in v])
        res['round11'][judge] = r
        on9 = {j['id']: [tuple(x) for x in lab_[j['id']]['p1']['github_on']] for j in js}; kept9 = sum(len(K9[j['id']]['github']) for j in js)
        res['round9_keep'][judge] = dict(github_kept=kept9, github_on=sum(1 for j in js for x in K9[j['id']]['github'] if tuple(x) in on9[j['id']]), installed_kept=r['C']['kept'], installed_fit=r['C']['found'])
        js2 = [j for j in jobs if ok(lab_, j['id'], 'p2')]; r2 = dict(requests=len(js2))
        for a in 'ABC':
            kept = sum(len(K12[j['id'] + a]) for j in js2); on = sum(1 for j in js2 for x in K12[j['id'] + a] if x in lab_[j['id']]['p2']['on'])
            r2[a] = dict(kept=kept, on=on, share=round(100 * on / kept, 1) if kept else 0, on_per_request=round(on / len(js2), 2) if js2 else 0)
        if js2:
            r2['B_passes'] = r2['B']['share'] >= r2['A']['share'] - 5 and r2['B']['on_per_request'] >= r2['A']['on_per_request'] - 0.25; r2['C_passes'] = r2['C']['on_per_request'] >= 0.7 * r2['A']['on_per_request']
        res['round12'][judge] = r2
    if all(k in res['round11'] for k in JUDGES):
        f, s, h = (res['round11'][k] for k in ('fable', 'sonnet', 'haiku'))
        rule = [f['D']['found'] > f['C']['found'], f['by_reading']['added'] > 0 and 2 * f['by_reading']['added_that_fit'] >= f['by_reading']['added'], s['D']['found'] >= s['C']['found'] and h['D']['found'] >= h['C']['found']]
        res['read_rule'] = dict(fable_D_finds_more=rule[0], fable_half_of_added_fit=rule[1], sonnet_and_haiku_not_fewer=rule[2], verdict='merge' if all(rule) else 'remove')
    rows = [json.loads(l) for l in open(lab.L + '/ledger.jsonl')]; mine = [r for r in rows if r.get('kind', '').startswith('v15')]
    res['spend'] = dict(calls=len(mine), usd=round(sum(r.get('cost') or 0 for r in mine), 2), by_judge={k: [sum(1 for r in mine if (r.get('meta') or {}).get('judge') == k), round(sum(r.get('cost') or 0 for r in mine if (r.get('meta') or {}).get('judge') == k), 2)] for k in JUDGES})
    json.dump(res, open(H + '/score15.json', 'w'), indent=1, ensure_ascii=False)
    for k in ('judges', 'agreement', 'round11', 'round12', 'round9_keep'):
        print('\n' + k)
        for a, b in res[k].items(): print(' ', a, json.dumps(b, ensure_ascii=False))
    print('\nread rule', res.get('read_rule')); print('spend', res['spend'])
