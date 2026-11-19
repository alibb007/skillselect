#!/usr/bin/env python3
"""Draws the README pictures as SVG, one light and one dark file each. Every number is read from evidence/."""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..", "assets"); EV = os.path.join(HERE, "..", "evidence")
T = {"light": dict(ink="#101A2B", mute="#5B6A80", line="#D5DCE8", soft="#E8EDF4", panel="#F6F8FB", blue="#2A78D6", orange="#C9521F", grey="#9AA6B8", green="#178A63", on="#FFFFFF",
                   bsoft="#E3EDFB", osoft="#FBE9E0", gsoft="#E1F3EA", card="#FFFFFF"),
     "dark": dict(ink="#E7EDF6", mute="#94A3B8", line="#28364A", soft="#1B2838", panel="#141E2C", blue="#5B9FEA", orange="#F08A5D", grey="#66758A", green="#3FD1A2", on="#0C131E",
                  bsoft="#1A2C47", osoft="#3A2519", gsoft="#143326", card="#0F1826")}
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
WIDE = []  # (picture, text, estimated width, room) for every label that has a box to fit in


def svg(w, h, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img">{body}</svg>\n'


def t(x, y, s, size=16, fill="", weight=400, anchor="start", font=SANS, ls=0, room=None, pic=""):
    if room:
        est = len(s) * size * (0.6 if font == MONO else 0.54 if weight >= 600 else 0.5) + len(s) * ls
        WIDE.append((pic, s, round(est), room))
    s = s.replace("&", "&amp;").replace("<", "&lt;")
    return f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" letter-spacing="{ls}">{s}</text>'


def r(x, y, w, h, fill, rx=8, stroke=None, sw=1):
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{st}/>'


def pct(a, b):
    return round((1 - b / a) * 100)


def mins(sec):
    sec = round(sec)
    return f"{sec // 60} min {sec % 60} s" if sec >= 60 else f"{sec} s"


# ---------- numbers, read from the evidence files ----------
R10 = json.load(open(EV + "/round10/results.json")); WITH, WITHOUT = R10["with_plugin"], R10["without"]
S9 = json.load(open(EV + "/round9/score9_sealed.json"))
J05 = json.load(open(EV + "/round9/raw9_tune.json"))["J05"]["B"]
REPOS, FILES = map(int, re.search(r"(\d+) repositories looked at, (\d+) skill folders read", J05["notes"][-1]).groups())
INSTALLED = len(json.load(open(EV + "/round6/sandbox-50.json")))
R3 = json.load(open(EV + "/round3/results.json"))


def step_card(c, x, y, w, n, title, sub, col):
    return (r(x, y, w, 92, c["soft"], 14, col) + f'<circle cx="{x + 34}" cy="{y + 46}" r="17" fill="{col}"/>' + t(x + 34, y + 52, str(n), 17, c["on"], 800, "middle")
            + t(x + 64, y + 42, title, 20, c["ink"], 800, ls=-.3, room=w - 76, pic="hero") + t(x + 64, y + 66, sub, 14, c["mute"], room=w - 76, pic="hero"))


def hero(c):
    b = r(0.5, 0.5, 1199, 419, c["panel"], 20, c["line"])
    b += t(64, 96, "CLAUDE CODE PLUGIN", 15, c["mute"], 600, font=MONO, ls=2)
    b += t(62, 178, "SkillSelect", 72, c["ink"], 800, ls=-2)
    b += t(64, 236, "Which of your skills to use, when and how.", 28, c["ink"], 500, room=650, pic="hero")
    b += t(64, 274, "Finds more on GitHub. Never installs anything.", 28, c["mute"], 500, room=650, pic="hero")
    b += r(64, 316, 190, 44, c["blue"], 22) + t(159, 344, "/skillselect", 17, c["on"], 700, "middle", font=MONO, room=170, pic="hero")
    b += t(274, 344, "then what you want to build", 17, c["mute"], 500)
    b += step_card(c, 740, 52, 410, 1, "Reads every skill you have", "scores each one against your request", c["blue"])
    b += step_card(c, 740, 164, 410, 2, "Finds more on GitHub", "ranked by fit and stars together", c["blue"])
    b += step_card(c, 740, 276, 410, 3, "When and how to use each", "one line and one command per skill", c["green"])
    return svg(1200, 420, b)


def flow(c):
    def box(x, y, w, s1, s2, col=None):
        return (r(x, y, w, 70, col or c["soft"], 12, None if col else c["line"]) + t(x + w / 2, y + 31, s1, 16, c["on"] if col else c["ink"], 700, "middle", room=w - 16, pic="flow")
                + t(x + w / 2, y + 53, s2, 13, c["on"] if col else c["mute"], 400, "middle", room=w - 16, pic="flow"))

    def arrow(x1, x2, y):
        return f'<line x1="{x1}" x2="{x2 - 8}" y1="{y}" y2="{y}" stroke="{c["grey"]}" stroke-width="2"/><path d="M{x2 - 10} {y - 6} L{x2} {y} L{x2 - 10} {y + 6} Z" fill="{c["grey"]}"/>'
    b = r(.5, .5, 1199, 299, c["panel"], 16, c["line"])
    b += t(32, 44, "WHEN YOU HAVE A JOB", 13, c["mute"], 700, font=MONO, ls=1)
    b += (box(32, 60, 236, "You type the job", "/skillselect build a landing page") + arrow(268, 316, 95) + box(316, 60, 252, "1  Scores your skills", "every installed skill, by fit", c["blue"]) + arrow(568, 616, 95)
          + box(616, 60, 252, "2  Adds GitHub skills", "ranked by fit and stars together", c["blue"]) + arrow(868, 916, 95) + box(916, 60, 252, "3  Keeps what does the job", "when and how for each", c["green"]))
    b += t(32, 178, "ON EVERY REQUEST", 13, c["mute"], 700, font=MONO, ls=1)
    b += box(32, 194, 236, "You ask", "as you always do") + arrow(268, 316, 229) + box(316, 194, 400, "One sentence is added for you", "short, finished, your own facts") + arrow(716, 764, 229) + box(764, 194, 404, "A short answer you can use as it is", "no blanks, nothing extra")
    return svg(1200, 300, b)


SHORT = [("Half the words", "words per answer", R3["A"]["words"], R3["S"]["words"], str(R3["A"]["words"]), str(R3["S"]["words"]), f"Shorter in {R3['shorter_in']} of {R3['n']} requests"),
         ("Nothing left to fill in", "answers with a blank like [Name]", R3["A"]["answers_with_placeholder"], R3["S"]["answers_with_placeholder"], f"{R3['A']['answers_with_placeholder']} of {R3['n']}", f"{R3['S']['answers_with_placeholder']} of {R3['n']}", "Blanks counted with one fixed pattern"),
         ("A quarter cheaper", "output tokens per answer", R3["A"]["tok_out"], R3["S"]["tok_out"], f"{R3['A']['tok_out']:,}", f"{R3['S']['tok_out']:,}", f"{pct(R3['A']['tok_out'], R3['S']['tok_out'])}% fewer tokens to pay for")]


def proof(c):
    b = ""
    for i, (h, sub, a, s, la, ls, cap) in enumerate(SHORT):
        x = 12 + i * 396
        b += r(x + .5, .5, 383, 299, c["panel"], 16, c["line"])
        b += t(x + 26, 48, h, 24, c["ink"], 800, ls=-.5, room=340, pic="proof") + t(x + 26, 74, sub, 15, c["mute"], room=340, pic="proof")
        full = 240
        b += t(x + 26, 118, "Plain request", 14, c["mute"]) + r(x + 26, 128, full, 24, c["orange"], 6) + t(x + 26 + full + 12, 146, la, 18, c["ink"], 800)
        sw = round(full * s / a)
        b += t(x + 26, 190, "With SkillSelect", 14, c["mute"]) + r(x + 26, 200, full, 24, c["soft"], 6) + (r(x + 26, 200, sw, 24, c["blue"], 6) if sw else "") + t(x + 26 + full + 12, 218, ls, 18, c["ink"], 800)
        b += t(x + 26, 268, cap, 14, c["mute"], room=340, pic="proof")
    return svg(1200, 300, b)


def pipeline(c):
    out = [r(.5, .5, 1259, 371, c["panel"], 16, c["line"])]

    def lane(y, label):
        out.append(r(8, y, 1244, 110, c["card"], 10, c["line"]) + t(22, y + 20, label, 12, c["mute"], 700, font=MONO, ls=1))

    def node(x, y, w, title, mono, kind="math"):
        fill, stroke = {"math": (c["panel"], c["ink"]), "llm": (c["osoft"], c["orange"]), "io": (c["gsoft"], c["green"])}[kind]
        s = r(x, y, w, 68, fill, 7, stroke, 1.4) + t(x + 10, y + 22, title, 14, c["ink"], 700, room=w - 14, pic="pipeline")
        for i, m in enumerate(mono):
            s += t(x + 10, y + 41 + 15 * i, m, 12, c["mute"], font=MONO, room=w - 16, pic="pipeline")
        out.append(s)

    def edge(points, pill=None, px=0, py=0):
        d = "M" + " L".join(f"{x} {y}" for x, y in points); (x1, y1), (x2, y2) = points[-2], points[-1]
        if x2 != x1:
            s = 1 if x2 > x1 else -1; head = f"M{x2 - 9 * s} {y2 - 5} L{x2} {y2} L{x2 - 9 * s} {y2 + 5} Z"
        else:
            s = 1 if y2 > y1 else -1; head = f"M{x2 - 5} {y2 - 9 * s} L{x2} {y2} L{x2 + 5} {y2 - 9 * s} Z"
        out.append(f'<path d="{d}" fill="none" stroke="{c["grey"]}" stroke-width="1.6"/><path d="{head}" fill="{c["grey"]}"/>')
        if pill:
            w = 14 + 7.4 * len(pill)
            out.append(r(round(px - w / 2), py - 11, round(w), 21, c["bsoft"], 10.5, c["blue"]) + t(px, py + 4, pill, 12, c["blue"], 700, "middle", font=MONO))

    YA, YB, YC = 12, 130, 248
    lane(YA, "LLM LAYER · CLAUDE"); lane(YB, "LOCAL INDEX · INSTALLED SKILLS"); lane(YC, "REMOTE INDEX · GITHUB")
    a, b, cc = YA + 32, YB + 32, YC + 32
    node(20, a, 150, "Request", ['"build a', 'landing page"'], "io")
    node(210, a, 200, "1 · Query expansion", ["topic: landing page", "close: html css …"], "llm")
    node(210, b, 200, "2 · Term model", ["stems + bigrams", "weights 1 / 1 / 0.5"])
    node(490, b, 190, "3 · Candidate gate", ["Σ w(shared) ≥ 1.5", "drops 1-word overlap"])
    node(760, b, 190, "4 · BM25F fit score", ["k1 1.5 · b 0.75", "name field ×3"])
    XC = [210, 442, 674, 906]
    node(XC[0], cc, 152, "3 · GitHub Search", ["up to 13 queries", "sorted by stars"])
    node(XC[1], cc, 152, "4 · Fetch SKILL.md", ["tree API + raw", "nothing installed"])
    node(XC[2], cc, 152, "5 · Gate + BM25F", ["same term model", "on fetched pool"])
    node(XC[3], cc, 152, "6 · Rank fusion", ["1/(60+r_fit)", "+ 1/(60+r_stars)"])
    node(930, a, 170, "7 · LLM re-rank", ["reads descriptions", "keeps ≤ 5 per list"], "llm")
    node(1130, a, 118, "Answer", ["4 + 5 skills", "when · how"], "io")
    edge([(170, a + 34), (208, a + 34)])
    edge([(310, a + 68), (310, b - 2)])
    edge([(310, b + 68), (310, cc - 2)])
    edge([(410, b + 34), (488, b + 34)], f"{INSTALLED} skills", 449, b + 14)
    edge([(680, b + 34), (758, b + 34)], f"{len(J05['local'])} pass", 719, b + 14)
    edge([(950, b + 34), (990, b + 34), (990, a + 70)], "top 8", 990, b - 14)
    for i, lab in enumerate([f"{REPOS} repos", f"{FILES} files", f"{len(J05['pool'])} pass"]):
        edge([(XC[i] + 152, cc + 34), (XC[i + 1] - 2, cc + 34)], lab, XC[i] + 152 + 40, cc + 14)
    edge([(1058, cc + 34), (1076, cc + 34), (1076, a + 70)], "top 12", 1076, cc - 14)
    edge([(1100, a + 34), (1128, a + 34)])
    return svg(1260, 372, "".join(out))


def lift(c):
    A, B, C = S9["A"], S9["B_rrf"], S9["C"]
    cards = [("PLUGIN 2.2.0", A, "word overlap, ordered by stars", c["orange"]), ("+ RETRIEVAL MATH", B, "more good candidates, same share", c["blue"]), ("+ LLM RE-RANK", C, "Claude keeps what does the job", c["green"])]
    b = t(14, 22, f"GITHUB PICKS THAT DO THE JOB · {A['jobs']} SEALED REQUESTS", 13, c["mute"], 700, font=MONO, ls=1)
    for i, (name, v, sub, col) in enumerate(cards):
        x = 12 + i * 396; share = v["gh_on"] / v["gh_listed"]
        b += r(x + .5, 36.5, 383, 283, c["panel"], 16, c["line"])
        b += t(x + 26, 70, name, 13, c["mute"], 700, font=MONO, ls=1)
        b += t(x + 24, 132, f"{round(share * 100)}%", 60, c["ink"], 800, ls=-2) + t(x + 170, 110, f"{v['gh_on']} of {v['gh_listed']} picks", 16, c["ink"], 700) + t(x + 170, 132, sub, 12.5, c["mute"], room=205, pic="lift")
        b += r(x + 26, 152, 330, 16, c["soft"], 8) + r(x + 26, 152, round(330 * share), 16, col, 8)
        for k, (lab, num, den) in enumerate([("Installed picks that do the job", v["loc_on"], v["loc_listed"]), ("Installed fits found", v["rec_num"], v["rec_den"])]):
            y = 206 + k * 50
            b += t(x + 26, y, lab, 14, c["mute"], room=240, pic="lift") + t(x + 356, y, f"{num} of {den}", 16, c["ink"], 800, "end")
            b += r(x + 26, y + 10, 330, 8, c["soft"], 4) + r(x + 26, y + 10, round(330 * num / den), 8, col, 4)
    return svg(1200, 332, b)


def numbers(c):
    rows = [("Token Usage", WITHOUT["tokens"], WITH["tokens"], f"{WITHOUT['tokens']:,}", f"{WITH['tokens']:,}", "fewer tokens"),
            ("Time to get the answer", WITHOUT["sec"], WITH["sec"], mins(WITHOUT["sec"]), mins(WITH["sec"]), "less time"),
            ("Steps to find your skills", WITHOUT["steps"], WITH["steps"], str(WITHOUT["steps"]), str(WITH["steps"]), "fewer steps")]
    b = r(.5, .5, 1199, 30 + 112 * len(rows) + 9, c["panel"], 16, c["line"])
    for i, (name, a, w, la, lw, unit) in enumerate(rows):
        y = 28 + i * 112; full = 620
        b += t(32, y + 22, name, 20, c["ink"], 800, ls=-.3)
        b += t(32, y + 52, "Without SkillSelect", 14, c["mute"]) + r(190, y + 37, full, 22, c["orange"], 6) + t(190 + full + 14, y + 54, la, 17, c["orange"], 800, font=MONO)
        b += t(32, y + 84, "With SkillSelect", 14, c["mute"]) + r(190, y + 69, full, 22, c["soft"], 6) + r(190, y + 69, max(6, round(full * w / a)), 22, c["blue"], 6) + t(190 + full + 14, y + 86, lw, 17, c["blue"], 800, font=MONO)
        b += t(1168, y + 66, f"−{pct(a, w)}%", 54, c["green"], 800, "end", ls=-2) + t(1168, y + 90, unit, 14, c["mute"], 400, "end")
    return svg(1200, 30 + 112 * len(rows) + 10, b)


os.makedirs(OUT, exist_ok=True)
for name, fn in (("hero", hero), ("flow", flow), ("proof", proof), ("pipeline", pipeline), ("lift", lift), ("numbers", numbers)):
    for mode, c in T.items():
        open(os.path.join(OUT, f"{name}-{mode}.svg"), "w").write(fn(c))
tight = sorted({x for x in WIDE if x[2] > x[3]})
print("wrote", sorted(f for f in os.listdir(OUT) if f.endswith(".svg")))
print("labels wider than their box (estimate):", tight or "none")
