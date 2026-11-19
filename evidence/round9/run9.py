"""Round 9, step 2: run both finders on one set of jobs. No model call. usage: run9.py tune|sealed"""
import json, os, sys, time
H = os.path.dirname(os.path.abspath(__file__)); SET = sys.argv[1]
SB = '/tmp/skillselect-round6/proj/.claude/skills'
os.environ['SKILL_FINDER_CACHE'] = H + '/cache'
import find3 as M
F = M.F
jobs = [j for j in json.load(open(H + '/jobs.json')) if j['set'] == SET]
A = json.load(open(H + '/wordsA.json')); B = json.load(open(H + '/wordsB.json'))
skills = []
for n in sorted(os.listdir(SB)):
    p = os.path.join(SB, n, 'SKILL.md')
    if os.path.exists(p):
        name, desc = F.front(open(p, errors='replace').read(8000)); skills.append(dict(name=name or n, desc=desc, path=p))
assert len(skills) == 50, len(skills)
tok = F.token(True); have = {s['name'].lower() for s in skills}
outp = H + f'/raw9_{SET}.json'; out = json.load(open(outp)) if os.path.exists(outp) else {}
slimA = lambda o: dict(skill=o['skill'], repo=o['repo'], stars=o['stars'], desc=(o['desc'] or '')[:300])
for j in jobs:
    if j['id'] in out and not any('turned away' in n for n in out[j['id']]['A']['notes'] + out[j['id']]['B']['notes']):
        continue  # a job where GitHub turned searches away is run again (answered searches are cached)
    a, b = A[j['id']], B[j['id']]
    la = F.rank_local(a['topic'], skills); ga, na = F.search_github(a['topic'], tok, 5, have)
    time.sleep(2)
    lb = M.rank_local3(b['topic'], b['also'], skills, 8); pool, nb = M.pool_github3(b['topic'], b['also'], tok, have)
    out[j['id']] = dict(A=dict(local=[s['name'] for s in la], github=[slimA(o) for o in ga], notes=na),
                        B=dict(local=[dict(name=s['name'], fit=s['fit']) for s in lb], pool=[dict(o, desc=(o['desc'] or '')[:300]) for o in pool], notes=nb))
    json.dump(out, open(outp, 'w'), indent=1, ensure_ascii=False)
    print(j['id'], '| A local', len(la), 'gh', len(ga), '| B local', len(lb), 'pool', len(pool), '|', nb[-1], '|', [n for n in na + nb if 'turned away' in n], flush=True)
    time.sleep(32)  # GitHub allows 30 searches a minute; one job makes up to 23
