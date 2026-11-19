#!/usr/bin/env python3
"""Writes src/data.json for the film from the saved sessions. Nothing on screen is typed in by hand:
- installed skills: evidence/round6/sandbox-50.json (the test folder)
- the score of each installed skill: the finder's own word match, run on the test folder (set SANDBOX to its skills folder;
  without it the scores already in data.json are kept)
- the five that fit, when to use each, and their commands: the session in evidence/round6/landing-B-session.json
- the GitHub skills, stars, licenses and when to use each: the same session
- what plain Claude loaded on its own: evidence/round7/results.json
- steps, seconds, tokens: evidence/round6/results.json (one run with the plugin, one without)"""
import json, os, re, sys
H = os.path.dirname(os.path.abspath(__file__)); EV = os.path.join(H, "..", "..", "evidence")
ses = json.load(open(EV + "/round6/landing-B-session.json")); res = json.load(open(EV + "/round6/results.json")); r7 = json.load(open(EV + "/round7/results.json"))
box = sorted((s["skill"] for s in json.load(open(EV + "/round6/sandbox-50.json"))), key=str.lower)
tool = [e for e in ses["events"] if e["kind"] == "tool_result"][0]["text"]; ans = ses["result"]
first = lambda s: re.split(r"(?<=[a-z0-9)])\. ", s.strip())[0].rstrip(".") + "."

have = re.search(r"WHAT YOU HAVE \((\d+) fit, of (\d+) installed", tool)
assert int(have.group(2)) == len(box), (have.group(2), len(box))
calls = dict(re.findall(r"^  ([\w-]+)  \(\d+ of \d+ key words\)\n[^\n]*\n\s+call: (/\S+)", tool, re.M))
said = dict(re.findall(r"^- \*\*([\w-]+)\*\*: (.+)$", ans, re.M))  # the assistant's line per installed skill, in its order
fits = [dict(name=n, when=first(said[n]), call=calls[n]) for n in said if n in calls]
assert len(fits) == int(have.group(1)), (len(fits), have.group(1))
rows = re.findall(r"^\s+\d\. ([\d,]+) stars\s+(\S+)\s+\[([^\],]+)[^\n]*\n\s+license (\S+) · updated (\S+)", tool, re.M)
why = {m[0]: m[1] for m in re.findall(r"^\d\. \*\*([\w-]+)\*\* \([^)]+\): [^\n]*? updated \S+?\. (.+)$", ans, re.M)}
github = [dict(stars=int(a.replace(",", "")), skill=b, repo=c, license="no license" if d == "none" else d, updated=e, when=first(why[b])) for a, b, c, d, e in rows]
pick = re.search(r"START WITH THIS ONE\n\s+(\S+)", tool).group(1)
query = re.search(r"^You asked for: (.+)$", tool, re.M).group(1)

old = json.load(open(H + "/src/data.json")) if os.path.exists(H + "/src/data.json") else {}
scores = old.get("scores") if old.get("query") == query else None
if os.environ.get("SANDBOX"):
    sys.path.insert(0, os.path.join(H, "..", "..", "skills", "find-skill", "scripts")); import find_skills as F
    q = list(dict.fromkeys(F.toks(query))); scores = {}
    for n in box:
        name, desc = F.front(open(os.path.join(os.environ["SANDBOX"], n, "SKILL.md"), errors="replace").read(8000))
        doc = F.toks(name or n) + F.toks(desc); scores[n] = sum(1 for t in q if t in doc)
assert scores and len(scores) == len(box), "set SANDBOX to the test folder's .claude/skills to score the 50 skills"
runs = r7["runs"]; plain = [v for k, v in runs.items() if k.startswith("Q")][0]
data = dict(
    ask=res["job"], query=query, key_words=len(list(dict.fromkeys(query.split()))), installed=box, scores=scores, fits=fits, github=github, pick=pick,
    plain=dict(used=plain["skills_loaded"], runs=len(runs), one=sum(1 for v in runs.values() if v["of_the_five_fits"] == 1), two=sum(1 for v in runs.values() if v["of_the_five_fits"] == 2)),
    after=dict(tokens=res["with_plugin"]["tokens"], sec=res["with_plugin"]["sec"], steps=res["with_plugin"]["steps"]),
    before=dict(tokens=res["without"]["tokens"], sec=res["without"]["sec"], steps=res["without"]["steps"]))
json.dump(data, open(H + "/src/data.json", "w"), indent=1)
print(len(box), "installed | fits", [(f["name"], scores[f["name"]]) for f in fits], "| github", [(g["skill"], g["stars"]) for g in github], "| pick", pick, "| plain", data["plain"], "| top scores", sorted(scores.items(), key=lambda x: -x[1])[:8])
for f in fits: print("  ", f["name"], "|", f["when"], "|", f["call"])
for g in github: print("  ", g["skill"], "|", g["when"])
