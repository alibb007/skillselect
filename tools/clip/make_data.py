#!/usr/bin/env python3
"""Writes src/data.json for the clip from the saved round-6 session. Nothing on screen is typed in by hand:
- installed skills: evidence/round6/sandbox-50.json (the test folder)
- the five that fit and what each is for: the assistant's own answer in landing-B-session.json
- the GitHub skills, stars and licenses: the finder's output in that session
- the pick and its command: the finder's output in that session
- tokens, seconds, steps: evidence/round6/results.json (one run with the plugin, one without)"""
import json, os, re
H = os.path.dirname(os.path.abspath(__file__)); EV = os.path.join(H, "..", "..", "evidence", "round6")
ses = json.load(open(EV + "/landing-B-session.json")); res = json.load(open(EV + "/results.json"))
box = sorted((s["skill"] for s in json.load(open(EV + "/sandbox-50.json"))), key=str.lower)
tool = [e for e in ses["events"] if e["kind"] == "tool_result"][0]["text"]

have = re.search(r"WHAT YOU HAVE \((\d+) fit, of (\d+) installed", tool)
assert int(have.group(2)) == len(box), (have.group(2), len(box))
fit_names = re.findall(r"^  (\S+)  \(\d+ of \d+ key words\)", tool, re.M)
said = dict(re.findall(r"^- [`*]+([\w-]+)[`*]+:\s*(.+)$", ses["result"], re.M))  # the assistant's one line per skill
fits = [dict(name=n, use=said[n].rstrip(".")) for n in fit_names]
rows = re.findall(r"^\s+\d\. ([\d,]+) stars\s+(\S+)\s+\[([^\],]+)[^\n]*\n\s+license (\S+) · updated (\S+)", tool, re.M)
github = [dict(stars=int(a.replace(",", "")), skill=b, repo=c, license="no license" if d == "none" else d, updated=e) for a, b, c, d, e in rows]
pick = re.search(r"RECOMMENDED, AND HOW TO USE IT\n\s+(\S+)\s+\((.+?)\)\n\s+(.+)", tool)
call = re.search(r"Call it:\s+(.+)", tool).group(1).strip()
needs = re.search(r"It needs:\s+(.+?)(?:\s+\(named in its instructions\))?$", tool, re.M).group(1).strip()
data = dict(
    ask=res["job"], installed=box, fits=fits, github=github,
    pick=dict(name=pick.group(1), where="already installed" if pick.group(2) == "installed" else pick.group(2), call=call,
              why="nothing to download" if pick.group(2) == "installed" else "most stars among the fits",
              needs="needs nothing extra" if needs.startswith("nothing") else "needs " + needs),
    run=dict(tokens=res["with_plugin"]["tokens"], sec=res["with_plugin"]["sec"], steps=res["with_plugin"]["steps"]),
    plain=dict(tokens=res["without"]["tokens"], sec=res["without"]["sec"], steps=res["without"]["steps"]))
assert len(fits) == int(have.group(1)) and len(github) >= 3, (len(fits), len(github))
json.dump(data, open(H + "/src/data.json", "w"), indent=1)
print(len(box), "installed,", [f["name"] for f in fits], "|", [(g["skill"], g["stars"]) for g in github], "|", data["pick"], data["run"], data["plain"])
