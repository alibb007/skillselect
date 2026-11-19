#!/usr/bin/env python3
"""Draws the README pictures as SVG, one light and one dark file each. Numbers come from evidence/."""
import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
T = {"light": dict(ink="#101A2B", mute="#5B6A80", line="#D5DCE8", soft="#E8EDF4", panel="#F6F8FB", blue="#2A78D6", orange="#EB6834", grey="#9AA6B8", green="#178A63", on="#FFFFFF"),
     "dark": dict(ink="#E7EDF6", mute="#94A3B8", line="#28364A", soft="#1B2838", panel="#141E2C", blue="#5B9FEA", orange="#F08A5D", grey="#66758A", green="#3FD1A2", on="#0C131E")}
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"


def svg(w, h, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img">{body}</svg>\n'


def t(x, y, s, size=16, fill="", weight=400, anchor="start", font=SANS, ls=0):
    s = s.replace("&", "&amp;").replace("<", "&lt;")
    return f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" letter-spacing="{ls}">{s}</text>'


def r(x, y, w, h, fill, rx=8, stroke=None):
    st = f' stroke="{stroke}" stroke-width="1"' if stroke else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{st}/>'


def step_card(c, x, y, w, n, title, sub, col):
    return (r(x, y, w, 92, c["soft"], 14, col) + f'<circle cx="{x + 34}" cy="{y + 46}" r="17" fill="{col}"/>' + t(x + 34, y + 52, str(n), 17, c["on"], 800, "middle")
            + t(x + 64, y + 42, title, 20, c["ink"], 800, ls=-.3) + t(x + 64, y + 66, sub, 14, c["mute"]))


def hero(c):
    b = r(0.5, 0.5, 1199, 419, c["panel"], 20, c["line"])
    b += t(64, 96, "CLAUDE CODE PLUGIN", 15, c["mute"], 600, font=MONO, ls=2)
    b += t(62, 178, "Straight Answer", 72, c["ink"], 800, ls=-2)
    b += t(64, 236, "Which skill to use, and how to use it.", 28, c["ink"], 500)
    b += t(64, 274, "Short, finished answers too.", 28, c["mute"], 500)
    b += r(64, 316, 190, 44, c["blue"], 22) + t(159, 344, "Install once", 17, c["on"], 700, "middle")
    b += t(274, 344, "then say the job", 17, c["mute"], 500)
    b += step_card(c, 740, 52, 410, 1, "What you have", "the skills on your computer that fit", c["blue"])
    b += step_card(c, 740, 164, 410, 2, "The best on GitHub", "most stars first, license, last update", c["blue"])
    b += step_card(c, 740, 276, 410, 3, "How to use it", "the command, what it needs, how to add it", c["green"])
    return svg(1200, 420, b)


SHORT = [("Half the words", "words per answer", 488, 245, "488", "245", "Shorter in 42 of 42 requests"),
         ("Nothing left to fill in", "answers with a blank like [Name]", 6, 0, "6 of 42", "0 of 42", "Blanks counted with one fixed pattern"),
         ("A quarter cheaper", "output tokens per answer", 1946, 1447, "1,946", "1,447", "26% fewer tokens to pay for")]


def proof(c, cards=SHORT, la_="Plain request", lb_="With the plugin"):
    b = ""
    for i, (h, sub, a, s, la, ls, cap) in enumerate(cards):
        x = 12 + i * 396
        b += r(x + .5, .5, 383, 299, c["panel"], 16, c["line"])
        b += t(x + 26, 48, h, 24, c["ink"], 800, ls=-.5) + t(x + 26, 74, sub, 15, c["mute"])
        full = 240
        b += t(x + 26, 118, la_, 14, c["mute"]) + r(x + 26, 128, full, 24, c["orange"], 6) + t(x + 26 + full + 12, 146, la, 18, c["ink"], 800)
        sw = round(full * s / a)
        b += t(x + 26, 190, lb_, 14, c["mute"]) + r(x + 26, 200, full, 24, c["soft"], 6) + (r(x + 26, 200, sw, 24, c["blue"], 6) if sw else "") + t(x + 26 + full + 12, 218, ls, 18, c["ink"], 800)
        b += t(x + 26, 268, cap, 14, c["mute"])
    return svg(1200, 300, b)


import json, re, statistics as st
EV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "evidence", "round5")
RES = json.load(open(EV + "/results.json"))["runs"]; SES = json.load(open(EV + "/deck-B-session.json"))
KEYS = [k[:-2] for k in RES if k.endswith("-A") and k[:-2] + "-B" in RES]
med = lambda arm, m: st.median(RES[k + "-" + arm][m] for k in KEYS)
up = lambda x: int(x + 0.5)  # halves go up, the same as the clip
times = lambda a, b: (f"{a / b:.1f}".rstrip("0").rstrip(".") + " times") if a / b >= 2 else f"{round((1 - b / a) * 100)}%"
same = lambda m: sum(1 for k in KEYS if RES[k + "-B"][m] < RES[k + "-A"][m])
SPEED = [(times(med("A", "tokens"), med("B", "tokens")) + " fewer tokens", "tokens per question", med("A", "tokens"), med("B", "tokens"), f"{up(med('A', 'tokens')):,}", f"{up(med('B', 'tokens')):,}", f"Fewer in {same('tokens')} of {len(KEYS)} jobs"),
         (times(med("A", "sec"), med("B", "sec")) + " faster", "seconds to an answer", med("A", "sec"), med("B", "sec"), f"{up(med('A', 'sec'))} s", f"{up(med('B', 'sec'))} s", f"Faster in {same('sec')} of {len(KEYS)} jobs"),
         (f"{round(med('B', 'steps'))} step, not {round(med('A', 'steps'))}", "tool calls the assistant made", med("A", "steps"), med("B", "steps"), str(round(med("A", "steps"))), str(round(med("B", "steps"))), f"Fewer in {same('steps')} of {len(KEYS)} jobs")]


def finder(c):
    out = [e for e in SES["events"] if e["kind"] == "tool_result"][0]["text"]
    have = re.search(r"WHAT YOU HAVE \((\d+) fit, of (\d+) installed", out)
    rows = re.findall(r"^\s+\d\. ([\d,]+) stars\s+(\S+)\s+\[([^\],]+)[^\n]*\n\s+license (\S+) · updated (\S+)", out, re.M)
    pick = re.search(r"RECOMMENDED, AND HOW TO USE IT\n\s+(\S+)", out).group(1)
    call = re.search(r"Call it:\s+(.+)", out).group(1).strip()
    needs = re.search(r"It needs:\s+(.+?)\s+\(named", out)
    note = re.search(r"^(\d+) repositories looked at, (\d+) skill folders read", out, re.M)
    H = 636
    b = r(.5, .5, 1199, H - 1, c["panel"], 16, c["line"]) + r(.5, .5, 1199, 46, c["soft"], 16) + r(.5, 30, 1199, 17, c["soft"], 0)
    for i, col in enumerate((c["orange"], c["grey"], c["green"])):
        b += f'<circle cx="{28 + i * 22}" cy="24" r="6.5" fill="{col}"/>'
    b += t(600, 29, "claude", 14, c["mute"], 600, "middle", MONO)
    b += t(32, 84, ">", 16, c["mute"], 600, font=MONO) + t(54, 84, SES["ask"], 16, c["ink"], 600, font=MONO)
    b += t(32, 128, "1  WHAT YOU HAVE", 13, c["blue"], 700, font=MONO, ls=1)
    b += t(54, 160, pick, 20, c["ink"], 800) + t(54 + 12 * len(pick) + 14, 160, f"fits · {have.group(1)} of {have.group(2)} installed · read on your computer, nothing sent", 14, c["mute"], font=MONO)
    b += f'<line x1="32" x2="1168" y1="180" y2="180" stroke="{c["line"]}" stroke-width="1"/>'
    b += t(32, 214, "2  ON GITHUB, MOST STARS FIRST", 13, c["blue"], 700, font=MONO, ls=1)
    y = 250
    for stars, skill, repo, lic, upd in rows:
        b += t(150, y, stars, 19, c["ink"], 800, "end") + t(158, y, "stars", 12, c["mute"], font=MONO) + t(224, y, skill, 17, c["ink"], 700) + t(224 + 9.6 * len(skill) + 14, y, repo, 14, c["mute"], font=MONO)
        b += t(1168, y, ("no license" if lic == "none" else lic) + " · updated " + upd, 13, c["orange"] if lic == "none" else c["mute"], anchor="end", font=MONO); y += 36
    b += f'<line x1="32" x2="1168" y1="{y - 12}" y2="{y - 12}" stroke="{c["line"]}" stroke-width="1"/>'
    y += 22
    b += t(32, y, "3  RECOMMENDED, AND HOW TO USE IT", 13, c["green"], 700, font=MONO, ls=1)
    b += t(54, y + 34, pick, 20, c["ink"], 800) + t(54 + 12 * len(pick) + 14, y + 34, "you already have it, so there is nothing to download", 14, c["mute"], font=MONO)
    b += r(54, y + 50, 330, 36, c["soft"], 8, c["green"]) + t(68, y + 74, call, 16, c["green"], 700, font=MONO)
    b += t(400, y + 74, "or just ask in your own words", 14, c["mute"], font=MONO)
    if needs:
        b += t(54, y + 112, "It needs  " + needs.group(1), 14, c["mute"], font=MONO)
    b += t(32, H - 22, f"{note.group(1)} repositories looked at · {note.group(2)} skill folders read · nothing installed", 13, c["mute"], font=MONO)
    return svg(1200, H, b)


def flow(c):
    def box(x, y, w, s1, s2, col=None):
        return r(x, y, w, 70, col or c["soft"], 12, None if col else c["line"]) + t(x + w / 2, y + 31, s1, 16, c["on"] if col else c["ink"], 700, "middle") + t(x + w / 2, y + 53, s2, 13, c["on"] if col else c["mute"], 400, "middle")
    def arrow(x1, x2, y):
        return f'<line x1="{x1}" x2="{x2 - 8}" y1="{y}" y2="{y}" stroke="{c["grey"]}" stroke-width="2"/><path d="M{x2 - 10} {y - 6} L{x2} {y} L{x2 - 10} {y + 6} Z" fill="{c["grey"]}"/>'
    b = r(.5, .5, 1199, 299, c["panel"], 16, c["line"])
    b += t(32, 44, "WHEN YOU HAVE A JOB", 13, c["mute"], 700, font=MONO, ls=1)
    b += box(32, 60, 236, "You say the job", "in your own words") + arrow(268, 316, 95) + box(316, 60, 252, "1  What you have", "your own skills, checked first", c["blue"]) + arrow(568, 616, 95) + box(616, 60, 252, "2  The best on GitHub", "most stars first", c["blue"]) + arrow(868, 916, 95) + box(916, 60, 252, "3  How to use it", "one pick, and its command", c["green"])
    b += t(32, 178, "ON EVERY REQUEST", 13, c["mute"], 700, font=MONO, ls=1)
    b += box(32, 194, 236, "You ask", "as you always do") + arrow(268, 316, 229) + box(316, 194, 400, "One sentence is added for you", "short, finished, your own facts") + arrow(716, 764, 229) + box(764, 194, 404, "A short answer you can use as it is", "no blanks, nothing extra")
    return svg(1200, 300, b)


os.makedirs(OUT, exist_ok=True)
for name, fn in (("hero", hero), ("proof", proof), ("speed", lambda c: proof(c, SPEED, "Without the plugin", "With the plugin")), ("finder", finder), ("flow", flow)):
    for mode, c in T.items():
        open(os.path.join(OUT, f"{name}-{mode}.svg"), "w").write(fn(c))
print("wrote", sorted(os.listdir(OUT)))
