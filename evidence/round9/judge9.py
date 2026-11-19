"""Round 9, steps 3 and 4. usage: judge9.py keep|label tune|sealed [order]
keep  = arm C: Opus keeps the skills that do the job, from matcher 3's lists (order = rrf|fit|stars, default rrf)
label = the truth: Opus marks every installed skill and every GitHub skill any arm listed. It never sees which arm listed what."""
import json, os, random, sys
from concurrent.futures import ThreadPoolExecutor
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(os.path.dirname(H), 'harness')); import lab
import find3 as M
F = M.F
WHAT, SET = sys.argv[1], sys.argv[2]; ORDER = sys.argv[3] if len(sys.argv) > 3 else 'rrf'
START = float(open(H + '/start.txt').read())
SB = '/tmp/skillselect-round6/proj/.claude/skills'
jobs = [j for j in json.load(open(H + '/jobs.json')) if j['set'] == SET]
raw = json.load(open(H + f'/raw9_{SET}.json'))
skills = []
for n in sorted(os.listdir(SB)):
    name, desc = F.front(open(os.path.join(SB, n, 'SKILL.md'), errors='replace').read(8000)); skills.append(dict(name=name or n, desc=desc[:400]))
LOCK = __import__('threading').Lock()
outp = H + f'/{WHAT}9_{SET}.json'; out = json.load(open(outp)) if os.path.exists(outp) else {}
KEEP = ("You are a coding assistant following one step of a skill's instructions.\nThe step: From the finder's two lists keep only the skills whose own description says they do what the person asked: "
        "they make the thing, or a named part of it. Drop skills that only sit next to the job (hosting, screenshots, checking some other kind of work), skills written for one repository or one product's own code, "
        "and general collections. Keep at most 5 from each list, in the finder's order. If fewer than 5 do the job, keep fewer; an empty list is a fine answer.\n"
        "Return only JSON: {\"installed\": [names kept], \"github\": [numbers kept]}.")
LABEL = ("You judge which skills would help with a request. A skill is ON when its own description says it makes or does the thing the person asked for, or a named part of it. "
         "It is OFF when it only sits next to the job, is one repository's or one product's private helper, is hosting, or is a general collection. Judge from the text given, nothing else.\n"
         "Return only JSON: {\"installed\": [names of the installed skills that are ON], \"github\": [numbers of the GitHub skills that are ON]}.")


def keep(j):
    r = raw[j['id']]['B']; gh = M.order(r['pool'], ORDER, 12)
    p = ("Request: " + j['request'] + "\n\nINSTALLED (finder's order):\n" + "\n".join(f"- {s['name']}: {next(x['desc'] for x in skills if x['name'] == s['name'])}" for s in r['local']) +
         "\n\nGITHUB (finder's order):\n" + "\n".join(f"{i + 1}. {o['skill']} ({o['repo']}, {o['stars']:,} stars): {o['desc']}" for i, o in enumerate(gh)))
    d = lab.jparse(lab.bare(KEEP, p, 'v9_keep', {'job': j['id']}))
    names = {s['name'] for s in r['local']}
    return dict(installed=[n for n in d.get('installed', []) if n in names][:5], github=[[gh[i - 1]['repo'], gh[i - 1]['skill']] for i in d.get('github', []) if isinstance(i, int) and 0 < i <= len(gh)][:5], order=ORDER)


def label(j):
    r = raw[j['id']]; seen, cands = set(), []
    for o in r['A']['github'] + M.order(r['B']['pool'], 'rrf', 12) + M.order(r['B']['pool'], 'fit', 12) + M.order(r['B']['pool'], 'stars', 12):
        k = (o['repo'], o['skill'])
        if k not in seen:
            seen.add(k); cands.append(dict(repo=o['repo'], skill=o['skill'], desc=o['desc']))
    random.Random(j['id']).shuffle(cands)
    p = ("Request: " + j['request'] + "\n\nINSTALLED SKILLS:\n" + "\n".join(f"- {s['name']}: {s['desc']}" for s in skills) +
         "\n\nGITHUB SKILLS:\n" + ("\n".join(f"{i + 1}. {c['skill']}: {c['desc']}" for i, c in enumerate(cands)) or "(none)"))
    d = lab.jparse(lab.bare(LABEL, p, 'v9_label', {'job': j['id']}))
    names = {s['name'] for s in skills}
    return dict(installed=[n for n in d.get('installed', []) if n in names], github_on=[[cands[i - 1]['repo'], cands[i - 1]['skill']] for i in d.get('github', []) if isinstance(i, int) and 0 < i <= len(cands)], github_judged=[[c['repo'], c['skill']] for c in cands])


def one(j):
    if j['id'] in out:
        return
    if lab.spent() - START > 7:
        lab.stop('round-9 cap reached')
    v = (keep if WHAT == 'keep' else label)(j)
    with LOCK:
        out[j['id']] = v; json.dump(out, open(outp, 'w'), indent=1, ensure_ascii=False)
    print(j['id'], WHAT, len(v.get('installed', [])), len(v.get('github', v.get('github_on', []))), flush=True)


try:
    with ThreadPoolExecutor(4) as ex:
        list(ex.map(one, jobs))
except lab.Stop as e:
    print('STOPPED:', e)
print(WHAT, SET, 'done', len(out), 'spend $%.2f' % (lab.spent() - START), 'STOP' if lab.stopped() else 'no STOP')
