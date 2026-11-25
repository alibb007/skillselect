"""Offline, no model: the hint on the 36 round-9 requests as people wrote them (50-skill test folder), scored against the judge's labels,
and on 24 messages that are not a job for any skill (written for this check)."""
import importlib.util, json, os, sys
finder, SB, EV = sys.argv[1:4]
sp = importlib.util.spec_from_file_location('f', finder); F = importlib.util.module_from_spec(sp); sp.loader.exec_module(F)
os.environ['SKILL_FINDER_ONLY'] = SB; skills = F.installed(F.local_skills())
jobs = json.load(open(EV + '/jobs.json'))
# The hint was taken out of the finder in round 15 (it never ran in a live session). Its code is kept here, as it was, so this check still runs.
HINT_STOP = set("file files code project app work thing things user users data way time step steps run running add change changes changing fix issue problem question example line lines text page pages name names type list item items".split())
def hint_for(prompt, skills, k=3):
    ws = [w for w in dict.fromkeys(F.words(prompt)) if w not in HINT_STOP and len(w) > 2]
    if len(ws) < 2 or len(prompt) > 4000: return ""
    st = {F.stem(w) for w in ws}; pairs = {F.stem(a) + "_" + F.stem(b) for a, b in zip(F.words(prompt), F.words(prompt)[1:])}; got = []
    for s in skills:
        if s["name"].lower() == F.SELF or F.gives_orders(s["desc"]) or F.gives_orders(s["name"]): continue
        nm = set(F.toks(s["name"].replace("-", " "))); ds = set(F.terms(s["desc"])); in_name = st & nm; in_desc = (st & ds) - in_name; pair = pairs & ds
        if len(in_name) >= 2 or (len(in_name) == 1 and len(in_desc) >= 2) or (pair and len(in_desc | in_name) >= 3): got.append((-(3 * len(in_name) + len(in_desc) + 2 * len(pair)), s["name"]))
    names = list(dict.fromkeys(n for _, n in sorted(got)))[:k]
    return "SkillSelect hint: installed skills that may fit this request: " + ", ".join(names) + ". For when and how to use each, run /skillselect with the job in a few words." if names else ""
import re
def named(line): return [x.strip() for x in re.search(r'request: (.*?)\. For when', line).group(1).split(',')] if line else []
for SET in ('tune', 'sealed'):
    L = json.load(open(EV + f'/label9_{SET}.json')); n = spoke = right = said = fitjobs = hitjobs = 0; wrong = []
    for j in jobs:
        if j['set'] != SET: continue
        n += 1; lab = set(L[j['id']]['installed']); names = named(hint_for(j['request'], skills))
        fitjobs += bool(lab); spoke += bool(names); said += len(names); right += len(lab & set(names)); hitjobs += bool(lab & set(names))
        wrong += [(j['id'], x) for x in names if x not in lab]
    print(f'{SET}: {n} requests | hint spoke on {spoke} | skills named {said}, labelled fits among them {right} | requests with a fit {fitjobs}, hint named a fit on {hitjobs}')
    print('   named but not a labelled fit:', wrong)
CHAT = ["thanks, that works", "what time is it in Tokyo right now?", "ok do it", "why is the sky blue?", "yes", "can you explain that again more simply", "run the tests again", "go ahead and commit", "what did you change in the last step?",
        "hmm that looks wrong", "how old is the universe", "translate 'good morning' to Spanish", "what does this error mean: KeyError 'id'", "undo that", "continue", "is 17 a prime number?", "summarise what we did today",
        "which file has the login function?", "rename the variable to total_count", "what's the capital of Australia", "show me the diff", "stop", "make it shorter", "who wrote Pride and Prejudice?"]
talk = [(c, named(hint_for(c, skills))) for c in CHAT]
print(f'not-a-job messages: {len(CHAT)} | hint spoke on {sum(1 for _, x in talk if x)}', [t for t in talk if t[1]])
