#!/usr/bin/env python3
"""Writes src/data.json for the film from the saved sessions. No number on screen is typed in by hand:
- installed skills: evidence/round6/sandbox-50.json (the test folder)
- the fit score of each installed skill: the finder's own BM25 score on the test folder (set SANDBOX to its skills folder;
  without it the scores already in data.json are kept)
- the skills kept, when to use each, how, and what they need: the session in evidence/round10/landing-session.json
- what plain Claude loaded on its own: evidence/round7/results.json
- tokens, seconds, steps: evidence/round10/results.json (with: the middle of three first-use runs; without: the round-6 run)"""
import json, os, re, sys
H = os.path.dirname(os.path.abspath(__file__)); EV = os.path.join(H, "..", "..", "evidence")
ses = json.load(open(EV + "/round10/landing-session.json")); res = json.load(open(EV + "/round10/results.json")); r7 = json.load(open(EV + "/round7/results.json"))
box = sorted((s["skill"] for s in json.load(open(EV + "/round6/sandbox-50.json"))), key=str.lower)
cmd = [e for e in ses["events"] if e["kind"] == "tool"][0]["command"]; tool = [e for e in ses["events"] if e["kind"] == "tool_result"][0]["text"]; ans = ses["result"]
topic, also = re.search(r'find_skills\.py"\s+"([^"]+)"\s+--also\s+"([^"]*)"', cmd).groups()
sent = lambda s: s.strip().rstrip(".") + "."
cap = lambda s: s[0].upper() + s[1:]

have = re.search(r"ON THIS COMPUTER \((\d+) of (\d+) installed skills passed", tool)
assert int(have.group(2)) == len(box), (have.group(2), len(box))
local, online = ans.split("**On GitHub**")[0], ans.split("**On GitHub**")[1].split("**Start with**")[0]
item = r"^- \*\*([\w.-]+)\*\*(.*)\n((?:  .+\n?)+)"
field = lambda body, k: (re.search(rf"^\s+{k}:\s*(.+)$", body, re.M) or [None, ""])[1].strip().strip("`")
fits = [dict(name=n, when=cap(sent(field(b, "When"))), how=field(b, "How"), needs=field(b, "Needs")) for n, _, b in re.findall(item, local, re.M)]
kept = re.search(r"\*\*On your computer\*\* \((\d+) of (\d+)", ans); assert kept and int(kept.group(1)) == len(fits), (kept and kept.group(0), len(fits))
github = []
for n, head, b in re.findall(item, online, re.M):
    p = [x.strip() for x in head.split("·") if x.strip()]
    github.append(dict(skill=n, repo=p[0], stars=int(re.sub(r"\D", "", p[1])), license=p[2], updated=p[3], when=cap(sent(field(b, "When"))), needs=field(b, "Needs")))
assert len(github) == int(re.search(r"\*\*On GitHub\*\* \((\d+)", ans).group(1)), len(github)
gh = re.search(r"(\d+) repositories looked at, (\d+) skill files read, (\d+) passed the match rule, (\d+) listed", tool)

old = json.load(open(H + "/src/data.json")) if os.path.exists(H + "/src/data.json") else {}
scores = old.get("scores") if old.get("topic") == topic and old.get("also") == also else None
if os.environ.get("SANDBOX"):
    sys.path.insert(0, os.path.join(H, "..", "..", "skills", "skillselect", "scripts")); import find_skills as F
    sk = []
    for n in box:
        name, desc = F.front(open(os.path.join(os.environ["SANDBOX"], n, "SKILL.md"), errors="replace").read(8000)); sk.append(dict(name=name or n, desc=desc))
    core, extra, w = F.query(topic, also); docs = [F.terms(s["name"]) * 3 + F.terms(s["desc"]) for s in sk]
    scores = {n: round(x, 2) for n, x in zip(box, F.bm25(docs, w))}
assert scores and len(scores) == len(box), "set SANDBOX to the test folder's .claude/skills to score the 50 skills"
names = [f["name"] for f in fits]; runs = r7["runs"]
loaded = [[s for s in v["skills_loaded"] if s in names] for v in runs.values()]
plain = dict(used=max(loaded, key=loaded.count), runs=len(runs), one=sum(1 for l in loaded if len(l) == 1), more=sum(1 for l in loaded if len(l) > 1), none=sum(1 for l in loaded if not l))
pick = lambda d: dict(tokens=d["tokens"], sec=d["sec"], steps=d["steps"])
data = dict(name="SkillSelect", slug="skillselect", ask=res["job"], topic=topic, also=also, installed=box, scores=scores, passed=int(have.group(1)), fits=fits, github=github,
            gh=dict(repos=int(gh.group(1)), files=int(gh.group(2)), passed=int(gh.group(3)), listed=int(gh.group(4))), plain=plain, after=pick(res["with_plugin"]), before=pick(res["without"]))
json.dump(data, open(H + "/src/data.json", "w"), indent=1, ensure_ascii=False)
print(len(box), "installed | topic", topic, "+", also, "| passed", data["passed"], "| kept", names, "| plain", plain, "| gh", data["gh"], "| before", data["before"], "| after", data["after"])
for f in fits: print("  ", f["name"], "|", f["when"], "|", f["how"], "|", f["needs"])
for g in github: print("  ", g["skill"], g["stars"], g["license"], "|", g["when"], "|", g["needs"])
