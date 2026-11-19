"""Round 8: the finder alone on 8 jobs. No model call. Saves what it lists so each line can be read and judged."""
import json, math, os, sys, time
H = os.path.dirname(os.path.abspath(__file__))
SB = '/tmp/skillselect-round6/proj/.claude/skills'
os.environ['SKILL_FINDER_DIRS'] = SB
os.environ['SKILL_FINDER_CACHE'] = H + '/cache'
sys.path.insert(0, os.path.expanduser('~/skillselect-2.2.0/skills/find-skill/scripts'))  # a checkout of this repo at commit e70f08b (plugin 2.2.0)
import find_skills as F

JOBS = ['landing page website marketing html', 'slide deck presentation', 'blog post writing', 'code review pull request', 'short video animation',
        'spreadsheet excel analysis', 'unit tests python', 'logo design brand']
skills = []
for n in sorted(os.listdir(SB)):
    p = os.path.join(SB, n, 'SKILL.md')
    if os.path.exists(p):
        name, desc = F.front(open(p, errors='replace').read(8000)); skills.append(dict(name=name or n, desc=desc, path=p))
tok = F.token(True); have = {s['name'].lower() for s in skills}; out = {}
slim = lambda o: dict(skill=o['skill'], repo=o['repo'], stars=o['stars'], matched=o['matched'], of=o['of'], desc=(o['desc'] or '')[:220])
for j in JOBS:
    loc = F.rank_local(j, skills)
    shown, notes = F.search_github(j, tok, 5, have)
    time.sleep(1)
    pool, _ = F.search_github(j, tok, 15, have)
    out[j] = dict(local=[dict(name=s['name'], matched=s['matched'], of=s['of'], desc=s['desc'][:220]) for s in loc], shown=[slim(o) for o in shown], pool=[slim(o) for o in pool], notes=notes)
    print(j, '| local', len(loc), '| shown', len(shown), '| pool', len(pool), '|', notes[-1], flush=True)
    time.sleep(20)  # GitHub allows 30 searches a minute
json.dump(dict(installed=len(skills), jobs=out), open(H + '/raw8.json', 'w'), indent=1)
