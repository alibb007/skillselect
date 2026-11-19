"""Round 9, step 5: score the arms against the labels. usage: score9.py tune|sealed [order for B]"""
import json, os, sys
H = os.path.dirname(os.path.abspath(__file__)); SET = sys.argv[1]; ORDER = sys.argv[2] if len(sys.argv) > 2 else 'rrf'
import find3 as M
jobs = [j for j in json.load(open(H + '/jobs.json')) if j['set'] == SET]
raw = json.load(open(H + f'/raw9_{SET}.json')); lab_ = json.load(open(H + f'/label9_{SET}.json'))
keep = json.load(open(H + f'/keep9_{SET}.json')) if os.path.exists(H + f'/keep9_{SET}.json') else {}


def arms(j):
    r = raw[j['id']]; pool = r['B']['pool']
    a = dict(A=([s for s in r['A']['local']], [(o['repo'], o['skill']) for o in r['A']['github']]))
    for how in ('rrf', 'fit', 'stars'):
        a['B_' + how] = ([s['name'] for s in r['B']['local'][:5]], [(o['repo'], o['skill']) for o in M.order(pool, how, 5)])
    if j['id'] in keep:
        a['C'] = (keep[j['id']]['installed'], [tuple(x) for x in keep[j['id']]['github']])
    return a


tot = {}
for j in jobs:
    if j['id'] not in lab_:
        continue
    L = lab_[j['id']]; fits = set(L['installed']); on = {tuple(x) for x in L['github_on']}; judged = {tuple(x) for x in L['github_judged']}
    for k, (loc, gh) in arms(j).items():
        t = tot.setdefault(k, dict(jobs=0, loc_listed=0, loc_on=0, rec_num=0, rec_den=0, gh_listed=0, gh_on=0, gh_unjudged=0, gh_zero=0, per_job=[]))
        t['jobs'] += 1; t['loc_listed'] += len(loc); t['loc_on'] += len(set(loc) & fits)
        t['rec_num'] += len(set(loc) & fits); t['rec_den'] += min(5, len(fits))
        t['gh_listed'] += len(gh); g_on = len([g for g in gh if g in on]); t['gh_on'] += g_on; t['gh_unjudged'] += len([g for g in gh if g not in judged]); t['gh_zero'] += 0 if gh else 1
        t['per_job'].append((j['id'], len(set(loc) & fits), len(loc), min(5, len(fits)), g_on, len(gh)))
pct = lambda a, b: f"{a}/{b} ({round(100 * a / b) if b else 0}%)"
print(f"{SET}: {len([j for j in jobs if j['id'] in lab_])} jobs")
for k, t in tot.items():
    print(f"{k:8} installed on-topic {pct(t['loc_on'], t['loc_listed']):>14} | recall@5 {pct(t['rec_num'], t['rec_den']):>14} | github on-topic {pct(t['gh_on'], t['gh_listed']):>14} | ON per job {t['gh_on'] / t['jobs']:.2f} | jobs with no github pick {t['gh_zero']} | unjudged {t['gh_unjudged']}")
json.dump(tot, open(H + f'/score9_{SET}.json', 'w'), indent=1)
