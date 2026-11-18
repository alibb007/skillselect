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


def hero(c):
    b = r(0.5, 0.5, 1199, 419, c["panel"], 20, c["line"])
    b += t(64, 96, "CLAUDE CODE PLUGIN", 15, c["mute"], 600, font=MONO, ls=2)
    b += t(62, 178, "Straight Answer", 72, c["ink"], 800, ls=-2)
    b += t(64, 236, "Short, finished AI answers.", 28, c["ink"], 500)
    b += t(64, 274, "And the right skill for the job.", 28, c["mute"], 500)
    b += r(64, 316, 190, 44, c["blue"], 22) + t(159, 344, "Install once", 17, c["on"], 700, "middle")
    b += t(274, 344, "then ask the way you already do", 17, c["mute"], 500)
    # right: the same answer, before and after
    x = 720
    b += r(x, 50, 200, 320, c["soft"], 14) + t(x + 18, 82, "PLAIN REQUEST", 12, c["mute"], 600, font=MONO, ls=1)
    y = 102
    for i, w in enumerate([164, 150, 164, 120, 158, 164, 96, 150, 164, 140, 164, 110, 156, 130]):
        blank = i in (3, 9)
        b += r(x + 18, y, w, 9, c["orange"] if blank else c["grey"], 4); y += 18
    b += t(x + 18, 360, "488 words", 15, c["ink"], 700)
    x2 = 950
    b += r(x2, 50, 200, 320, c["soft"], 14, c["blue"]) + t(x2 + 18, 82, "WITH THE PLUGIN", 12, c["blue"], 600, font=MONO, ls=1)
    y = 102
    for w in [164, 150, 164, 120, 158, 164, 96]:
        b += r(x2 + 18, y, w, 9, c["blue"], 4); y += 18
    b += t(x2 + 18, 360, "245 words", 15, c["ink"], 700)
    return svg(1200, 420, b)


def proof(c):
    b = ""
    cards = [("Half the words", "words per answer", 488, 245, "488", "245", "Shorter in 42 of 42 requests"),
             ("Nothing left to fill in", "answers with a blank like [Name]", 6, 0, "6 of 42", "0 of 42", "Blanks counted with one fixed pattern"),
             ("A quarter cheaper", "output tokens per answer", 1946, 1447, "1,946", "1,447", "26% fewer tokens to pay for")]
    for i, (h, sub, a, s, la, ls, cap) in enumerate(cards):
        x = 12 + i * 396
        b += r(x + .5, .5, 383, 299, c["panel"], 16, c["line"])
        b += t(x + 26, 48, h, 24, c["ink"], 800, ls=-.5) + t(x + 26, 74, sub, 15, c["mute"])
        full = 240
        b += t(x + 26, 118, "Plain request", 14, c["mute"]) + r(x + 26, 128, full, 24, c["orange"], 6) + t(x + 26 + full + 12, 146, la, 18, c["ink"], 800)
        sw = round(full * s / a)
        b += t(x + 26, 190, "With the plugin", 14, c["mute"]) + r(x + 26, 200, full, 24, c["soft"], 6) + (r(x + 26, 200, sw, 24, c["blue"], 6) if sw else "") + t(x + 26 + full + 12, 218, ls, 18, c["ink"], 800)
        b += t(x + 26, 268, cap, 14, c["mute"])
    return svg(1200, 300, b)


def split(c, x, y, w, parts):
    tot = sum(v for v, _ in parts); b = ""; cx = x
    for v, col in parts:
        pw = (w - 2 * (len(parts) - 1)) * v / tot
        b += r(round(cx, 1), y, round(pw, 1), 44, col, 6) + t(round(cx + pw / 2, 1), y + 29, str(v), 19, c["on"], 800, "middle"); cx += pw + 2
    return b


def vote(c):
    b = r(.5, .5, 1199, 259, c["panel"], 16, c["line"])
    b += t(32, 48, "Who prefers the short answer?", 24, c["ink"], 800, ls=-.5)
    b += t(32, 96, "A person, 21 pairs, blind", 16, c["ink"], 600) + split(c, 330, 68, 838, [(13, c["blue"]), (2, c["grey"]), (6, c["orange"])])
    b += t(32, 162, "An AI judge, 42 pairs", 16, c["ink"], 600) + split(c, 330, 134, 838, [(7, c["blue"]), (6, c["grey"]), (29, c["orange"])])
    lx = 330
    for col, lab in ((c["blue"], "short answer, with the plugin"), (c["grey"], "no clear winner"), (c["orange"], "plain answer")):
        b += r(lx, 208, 14, 14, col, 3) + t(lx + 22, 220, lab, 14, c["mute"]); lx += 60 + len(lab) * 8
    b += t(32, 220, "They disagree.", 14, c["mute"])
    return svg(1200, 260, b)


def finder(c):
    rows = [("86,483", "heygen-com/hyperframes", "Apache-2.0 · updated 18 Nov 2026"), ("11,769", "nexu-io/openmotion", "Apache-2.0 · updated 18 Nov 2026"),
            ("3,398", "Vincentwei1021/anything2explainer", "license unclear · updated 18 Nov 2026"), ("2,874", "alchaincyf/huashu-motion", "MIT · updated 16 Nov 2026"),
            ("1,663", "Tejashmakwana/motionmaxxing", "Apache-2.0 · updated 6 Oct 2026")]
    b = r(.5, .5, 1199, 479, c["panel"], 16, c["line"]) + r(.5, .5, 1199, 46, c["soft"], 16) + r(.5, 30, 1199, 17, c["soft"], 0)
    for i, col in enumerate((c["orange"], c["grey"], c["green"])):
        b += f'<circle cx="{28 + i * 22}" cy="24" r="6.5" fill="{col}"/>'
    b += t(600, 29, "find-skill", 14, c["mute"], 600, "middle", MONO)
    b += t(32, 88, "you", 14, c["mute"], 600, font=MONO) + t(92, 88, "I want to create a video motion graphic. Create me a new one.", 17, c["ink"], 600, font=MONO)
    b += t(32, 128, "ON GITHUB, MOST STARS FIRST", 13, c["blue"], 700, font=MONO, ls=1)
    y = 170
    for st, repo, meta in rows:
        b += t(150, y, st, 22, c["ink"], 800, "end") + t(158, y, "stars", 13, c["mute"], font=MONO) + t(230, y, repo, 19, c["ink"], 700) + t(1168, y, meta, 14, c["mute"], anchor="end", font=MONO)
        b += f'<line x1="32" x2="1168" y1="{y + 20}" y2="{y + 20}" stroke="{c["line"]}" stroke-width="1"/>'; y += 52
    b += t(32, 452, "81 repositories looked at · 12 skill folders read · 5 kept · nothing installed", 14, c["mute"], font=MONO)
    return svg(1200, 480, b)


def flow(c):
    def box(x, y, w, s1, s2, col=None):
        return r(x, y, w, 70, col or c["soft"], 12, None if col else c["line"]) + t(x + w / 2, y + 31, s1, 16, c["on"] if col else c["ink"], 700, "middle") + t(x + w / 2, y + 53, s2, 13, c["on"] if col else c["mute"], 400, "middle")
    def arrow(x1, x2, y):
        return f'<line x1="{x1}" x2="{x2 - 8}" y1="{y}" y2="{y}" stroke="{c["grey"]}" stroke-width="2"/><path d="M{x2 - 10} {y - 6} L{x2} {y} L{x2 - 10} {y + 6} Z" fill="{c["grey"]}"/>'
    b = r(.5, .5, 1199, 299, c["panel"], 16, c["line"])
    b += t(32, 44, "EVERY REQUEST", 13, c["mute"], 700, font=MONO, ls=1)
    b += box(32, 60, 250, "You ask", "as you always do") + arrow(282, 330, 95) + box(330, 60, 380, "One sentence is added for you", "short, finished, your own facts", c["blue"]) + arrow(710, 758, 95) + box(758, 60, 410, "A short answer you can use as it is", "no blanks, nothing extra")
    b += t(32, 178, "WHEN YOU NEED A SKILL", 13, c["mute"], 700, font=MONO, ls=1)
    b += box(32, 194, 250, "Say what you want to make", "in your own words") + arrow(282, 330, 229) + box(330, 194, 250, "Your own skills", "checked first, on your machine", c["blue"]) + arrow(580, 628, 229) + box(628, 194, 250, "GitHub", "most stars first", c["blue"]) + arrow(878, 926, 229) + box(926, 194, 242, "A list to choose from", "nothing installed")
    return svg(1200, 300, b)


os.makedirs(OUT, exist_ok=True)
for name, fn in (("hero", hero), ("proof", proof), ("vote", vote), ("finder", finder), ("flow", flow)):
    for mode, c in T.items():
        open(os.path.join(OUT, f"{name}-{mode}.svg"), "w").write(fn(c))
print("wrote", sorted(os.listdir(OUT)))
