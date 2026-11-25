"""Round 12. usage: run12.py find|keep|label|score   (see RULES12.md)"""
import importlib.util, json, os, random, subprocess, sys, tempfile, time
from concurrent.futures import ThreadPoolExecutor
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(H)); WHAT = sys.argv[1]
jobs = [j for j in json.load(open(H + '/../round9/jobs.json')) if j['set'] == 'sealed']; W = json.load(open(H + '/../round9/wordsB.json'))
HAVE = {s['skill'].lower() for s in json.load(open(H + '/../round6/sandbox-50.json'))}
load = lambda p, d: json.load(open(p)) if os.path.exists(p) else d
slim = lambda o: dict(skill=o['skill'], repo=o['repo'], stars=o['stars'], desc=(o['desc'] or '')[:300], src=o.get('src', 'live'))

if WHAT == 'find':
    os.environ['SKILL_FINDER_CACHE'] = H + '/cache'; os.environ['SKILL_FINDER_ONLY'] = '/nonexistent'
    old = tempfile.NamedTemporaryFile('w', suffix='.py', delete=False); old.write(subprocess.run(['git', '-C', ROOT, 'show', 'a688e60:skills/skillselect/scripts/find_skills.py'], capture_output=True, text=True, check=True).stdout); old.close()
    def mod(path, name):
        sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
    A = mod(old.name, 'f300'); B = mod(ROOT + '/skills/skillselect/scripts/find_skills.py', 'f310'); tok = B.token(True); assert tok, 'needs a GitHub login'
    out = load(H + '/raw12.json', {})
    for j in jobs:
        w = W[j['id']]
        if j['id'] in out and not any('turned away' in n for n in out[j['id']]['notes']):
            continue
        a, na, _ = A.search_github(w['topic'], w['also'], tok, 12, HAVE)
        b, nb, cb = B.search_github(w['topic'], w['also'], tok, 12, HAVE)
        c, nc, cc = B.search_github(w['topic'], w['also'], None, 12, HAVE, offline=True)
        out[j['id']] = dict(A=[slim(o) for o in a], B=[slim(o) for o in b], C=[slim(o) for o in c], notes=na + nb, counts=dict(B=cb, C=cc))
        json.dump(out, open(H + '/raw12.json', 'w'), indent=1, ensure_ascii=False)
        print(j['id'], w['topic'], '| A', len(a), '| B', len(b), 'from list', sum(1 for o in b if o.get('src') == 'list'), '| C', len(c), '|', [n for n in na + nb if 'turned away' in n], flush=True)
        time.sleep(32)  # GitHub allows 30 searches a minute; one request makes up to 13 (B reuses A's from the cache)
    sys.exit(0)

sys.path.insert(0, os.environ.get('SKILLSELECT_LAB') or os.path.join(os.path.dirname(H), 'harness')); import lab
START = float(open(H + '/start.txt').read()) if os.path.exists(H + '/start.txt') else lab.spent(); open(H + '/start.txt', 'w').write(str(START))
raw = json.load(open(H + '/raw12.json'))
KEEP = ("You are a coding assistant following one step of a skill's instructions.\nThe step: From the finder's two lists keep only the skills whose own description says they do what the person asked: "
        "they make the thing, or a named part of it. Drop skills that only sit next to the job (hosting, screenshots, checking some other kind of work), skills written for one repository or one product's own code, "
        "and general collections. Keep at most 5 from each list, in the finder's order. If fewer than 5 do the job, keep fewer; an empty list is a fine answer.\n"
        "Return only JSON: {\"installed\": [names kept], \"github\": [numbers kept]}.")
LABEL = ("You judge which skills would help with a request. A skill is ON when its own description says it makes or does the thing the person asked for, or a named part of it. "
         "It is OFF when it only sits next to the job, is one repository's or one product's private helper, is hosting, or is a general collection. Judge from the text given, nothing else.\n"
         "Return only JSON: {\"installed\": [names of the installed skills that are ON], \"github\": [numbers of the GitHub skills that are ON]}.")
def cap():
    if lab.spent() - START > 4.0: lab.stop('round 12 cap')

if WHAT == 'keep':
    out = load(H + '/keep12.json', {})
    def one(x):
        j, arm = x; k = j['id'] + arm
        if k in out: return
        cap(); gh = raw[j['id']][arm]
        if not gh: out[k] = []; return
        p = "Request: " + j['request'] + "\n\nINSTALLED (finder's order):\n(none)\n\nGITHUB (finder's order):\n" + "\n".join(f"{i + 1}. {o['skill']} ({o['repo']}, {o['stars']:,} stars): {o['desc']}" for i, o in enumerate(gh))
        d = lab.jparse(lab.bare(KEEP, p, 'v12_keep', {'job': j['id'], 'arm': arm})) or {}
        out[k] = [[gh[i - 1]['repo'], gh[i - 1]['skill']] for i in d.get('github', []) if isinstance(i, int) and 0 < i <= len(gh)][:5]
    with ThreadPoolExecutor(4) as ex: list(ex.map(one, [(j, a) for j in jobs for a in 'ABC']))
    json.dump(out, open(H + '/keep12.json', 'w'), indent=1); print('kept', {a: sum(len(out[j['id'] + a]) for j in jobs) for a in 'ABC'}, '| spend $', round(lab.spent() - START, 2))

if WHAT == 'label':
    keep = json.load(open(H + '/keep12.json')); out = load(H + '/label12.json', {})
    def one(j):
        if j['id'] in out: return
        cap(); desc = {(o['repo'], o['skill']): o['desc'] for a in 'ABC' for o in raw[j['id']][a]}
        cands = sorted({tuple(x) for a in 'ABC' for x in keep[j['id'] + a]}); random.Random(j['id']).shuffle(cands)
        if not cands: out[j['id']] = dict(on=[], judged=[]); return
        p = "Request: " + j['request'] + "\n\nINSTALLED:\n(none)\n\nGITHUB:\n" + "\n".join(f"{i + 1}. {s} ({r}): {desc[(r, s)]}" for i, (r, s) in enumerate(cands))
        d = lab.jparse(lab.bare(LABEL, p, 'v12_label', {'job': j['id']})) or {}
        out[j['id']] = dict(on=[list(cands[i - 1]) for i in d.get('github', []) if isinstance(i, int) and 0 < i <= len(cands)], judged=[list(c) for c in cands])
    with ThreadPoolExecutor(4) as ex: list(ex.map(one, jobs))
    json.dump(out, open(H + '/label12.json', 'w'), indent=1); print('labelled', sum(len(v['judged']) for v in out.values()), 'on', sum(len(v['on']) for v in out.values()), '| spend $', round(lab.spent() - START, 2))

if WHAT == 'score':
    keep = json.load(open(H + '/keep12.json')); lab_ = json.load(open(H + '/label12.json')); res = {}
    for a in 'ABC':
        kept = sum(len(keep[j['id'] + a]) for j in jobs); on = sum(1 for j in jobs for x in keep[j['id'] + a] if x in lab_[j['id']]['on'])
        res[a] = dict(kept=kept, on=on, share=round(100 * on / kept, 1) if kept else 0, on_per_request=round(on / len(jobs), 2), requests_with_no_pick=sum(1 for j in jobs if not keep[j['id'] + a]),
                      listed=sum(len(raw[j['id']][a]) for j in jobs), listed_from_list=sum(1 for j in jobs for o in raw[j['id']][a] if o.get('src') == 'list'))
        print(a, res[a])
    res['spend'] = round(lab.spent() - START, 2); json.dump(res, open(H + '/score12.json', 'w'), indent=1); print('spend $', res['spend'])
