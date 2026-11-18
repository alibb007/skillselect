#!/usr/bin/env python3
"""Builds the README demo clip from two real runs kept in evidence/demo:
before.json  - the same request with no plugin (reply from Claude Opus)
finder.json  - what the plugin's finder returned on a machine with 19 public skills installed
Needs playwright (with Chrome) and ffmpeg.   Usage: python3 tools/make_demo.py"""
import html, json, os, re, shutil, subprocess, sys, tempfile
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
B = json.load(open(ROOT + "/evidence/demo/before.json")); F = json.load(open(ROOT + "/evidence/demo/finder.json"))
FPS, DUR = 24, 16.5
esc = html.escape


def words_html(text):
    n, out = 0, []
    for line in text.strip().split("\n"):
        line = line.rstrip()
        if not line:
            continue
        cls = "p"
        m = re.match(r"^(\d+\.|-)\s+(.*)$", line)
        if m:
            cls += " li"; line = m.group(1).replace("-", "•") + " " + m.group(2)
        parts, bold, first = [], False, n
        for seg in re.split(r"(\*\*)", line):
            if seg == "**":
                bold = not bold; continue
            for w in seg.split():
                parts.append(f'<span class="w{" b" if bold else ""}" data-i="{n}">{esc(w)}</span>'); n += 1
        out.append(f'<div class="{cls}" data-i="{first}">' + " ".join(parts) + "</div>")
    return "\n".join(out), n


plain, n_plain = words_html(B["reply"])
loc = F["local"][0]; rec = F["recommended"]
rows, t = "", 6.6
for o in F["online"]:
    lic = o["license"] if o["license"] != "unclear" else "license unclear"
    rows += f'<div class="row" data-t="{t:.2f}"><b>{o["stars"]:,}</b><span>{esc(o["repo"])}</span><em>{esc(lic)}</em></div>'; t += 0.42
RIGHT = f'''<div class="cmd" data-t="3.0"><span id="cmd"></span></div>
<div class="sec" data-t="5.3"><div class="lab">INSTALLED ON THIS COMPUTER <i>{len(F["local"])} fits, of {F["installed_total"]} installed</i></div>
  <div class="row own"><b>✓</b><span>{esc(loc["name"])}</span><em>creates and edits slide decks</em></div></div>
<div class="sec" data-t="6.3"><div class="lab">AVAILABLE ON GITHUB <i>most stars first</i></div>{rows}</div>
<div class="rec" data-t="{t + 0.7:.2f}"><div class="lab">RECOMMENDED</div><div class="pick">{esc(rec["name"])}</div><div class="why">{esc(rec["why"])}</div></div>'''
PAGE = """<!doctype html><meta charset="utf-8"><style>
*{box-sizing:border-box}html,body{margin:0;width:960px;height:540px;overflow:hidden;background:#0C131E;color:#E7EDF6;font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Helvetica Neue",Arial,sans-serif}
.win{position:absolute;inset:14px;background:#141E2C;border:1px solid #28364A;border-radius:14px;overflow:hidden}
.bar{height:34px;background:#1B2838;display:flex;align-items:center;gap:7px;padding:0 14px;font:600 12px ui-monospace,"SF Mono",Menlo,monospace;color:#94A3B8}
.bar i{width:11px;height:11px;border-radius:50%;display:block}.bar span{margin:0 auto;transform:translateX(-24px)}
.ask{display:flex;gap:12px;padding:14px 18px 12px;border-bottom:1px solid #28364A;height:74px}
.av{width:34px;height:34px;border-radius:50%;background:#5B9FEA;color:#0C131E;font:800 14px -apple-system,sans-serif;display:grid;place-items:center;flex:none}
.ask b{display:block;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:#94A3B8;margin-bottom:3px}
.req{font-size:15px;line-height:1.42}.caret{display:inline-block;width:7px;height:16px;background:#5B9FEA;vertical-align:-2px;margin-left:1px}
.cols{position:absolute;left:0;right:0;top:109px;bottom:0;display:grid;grid-template-columns:1fr 1fr}
.col{position:relative;padding:12px 18px 0;overflow:hidden}.col+.col{border-left:1px solid #28364A}
.head{font:700 11px ui-monospace,"SF Mono",Menlo,monospace;letter-spacing:.08em;margin-bottom:8px}
.col.a .head{color:#F08A5D}.col.s .head{color:#5B9FEA}
.body{position:absolute;left:18px;right:18px;top:38px;bottom:40px;overflow:hidden}
.txt{font-size:12.4px;line-height:1.5}.p{margin:0 0 7px}.p.li{padding-left:10px}.w.b{font-weight:700}
.foot{position:absolute;left:18px;right:18px;bottom:10px;height:24px;display:flex;align-items:center}
.tag{border-radius:99px;padding:3px 10px;font-weight:700;font-size:11.5px;background:#F08A5D;color:#0C131E}
.fade{position:absolute;left:0;right:0;bottom:40px;height:26px;background:linear-gradient(#141E2C00,#141E2C)}
.right{position:absolute;left:18px;right:18px;top:36px;bottom:10px;display:flex;flex-direction:column;gap:9px}
.cmd{font:600 12.5px ui-monospace,"SF Mono",Menlo,monospace;background:#1B2838;border:1px solid #28364A;border-radius:7px;padding:6px 10px;color:#E7EDF6;min-height:30px}
.lab{font:700 10.5px ui-monospace,"SF Mono",Menlo,monospace;letter-spacing:.08em;color:#94A3B8;margin-bottom:4px}.lab i{font-style:normal;font-weight:500;letter-spacing:0;color:#66758A;margin-left:6px}
.row{display:grid;grid-template-columns:62px 1fr auto;gap:10px;align-items:baseline;padding:3.5px 0;border-bottom:1px solid #28364A;font-size:12.5px}
.row b{text-align:right;font:800 13.5px -apple-system,sans-serif;font-variant-numeric:tabular-nums}.row span{font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.row em{font-style:normal;color:#94A3B8;font:500 11px ui-monospace,"SF Mono",Menlo,monospace}.row.own b{color:#3FD1A2}.row.own{border-bottom:0}
.rec{background:#3FD1A2;color:#0C131E;border-radius:10px;padding:9px 12px;margin-top:auto}.rec .lab{color:#0C131E;margin-bottom:1px}
.pick{font:800 22px -apple-system,sans-serif;letter-spacing:-.5px}.why{font-size:12.5px;font-weight:600}
.end{position:absolute;inset:0;background:#0C131EF5;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px;text-align:center}
.end h1{margin:0;font:800 54px -apple-system,sans-serif;letter-spacing:-1.5px}.end p{margin:0;font-size:21px;color:#94A3B8}
.url{font:600 15px ui-monospace,"SF Mono",Menlo,monospace;background:#1B2838;border:1px solid #28364A;border-radius:8px;padding:8px 14px;margin-top:6px}
[hidden]{display:none!important}
</style>
<div class="win"><div class="bar"><i style="background:#F08A5D"></i><i style="background:#66758A"></i><i style="background:#3FD1A2"></i><span>Claude Code</span></div>
<div class="ask"><div class="av">Y</div><div><b>You</b><div class="req"><span id="req"></span><span class="caret" id="caret"></span></div></div></div>
<div class="cols" id="cols" hidden>
 <div class="col a"><div class="head">WITHOUT THE PLUGIN</div><div class="body"><div class="txt" id="ta">__PLAIN__</div></div><div class="fade"></div><div class="foot"><span class="tag" id="fa" hidden>no skill mentioned</span></div></div>
 <div class="col s"><div class="head">WITH STRAIGHT ANSWER</div><div class="right">__RIGHT__</div></div>
</div></div>
<div class="end" id="end" hidden><h1>Straight Answer</h1><p>The right skill for the job.</p><div class="url">github.com/alibb007/straight-answer</div></div>
<script>
const REQ=__REQ__,NP=__NP__,CMD="/straight-answer:find-skill",RATE=42,T0=2.9;
window.setT=function(t){
  const k=Math.max(0,Math.min(1,(t-0.3)/2.2));document.getElementById('req').textContent=REQ.slice(0,Math.round(REQ.length*k));
  document.getElementById('caret').hidden=t>2.7;document.getElementById('cols').hidden=t<T0;
  const root=document.getElementById('ta'),n=Math.min(NP,Math.max(0,Math.floor((t-T0)*RATE)));
  root.querySelectorAll('.w,.p').forEach(e=>e.hidden=+e.dataset.i>=n);root.style.transform='translateY('+Math.min(0,root.parentElement.clientHeight-root.scrollHeight)+'px)';
  document.getElementById('fa').hidden=n<NP;
  document.querySelectorAll('[data-t]').forEach(e=>{const a=+e.dataset.t;e.hidden=t<a;e.style.opacity=Math.max(0,Math.min(1,(t-a)/0.3))});
  const c=Math.max(0,Math.min(1,(t-3.1)/1.0));document.getElementById('cmd').textContent=CMD.slice(0,Math.round(CMD.length*c))+(t>4.3&&t<5.3?'   searching…':'');
  const e=document.getElementById('end');e.hidden=t<13.6;e.style.opacity=Math.max(0,Math.min(1,(t-13.6)/0.4));
};setT(0);
</script>"""
page = PAGE.replace("__PLAIN__", plain).replace("__RIGHT__", RIGHT).replace("__REQ__", json.dumps(B["request"])).replace("__NP__", str(n_plain))
tmp = tempfile.mkdtemp(); open(tmp + "/demo.html", "w").write(page)
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)
    pg = b.new_page(viewport={"width": 960, "height": 540}, device_scale_factor=2)
    pg.goto("file://" + tmp + "/demo.html")
    for f in range(int(FPS * DUR)):
        pg.evaluate(f"setT({f / FPS})"); pg.screenshot(path=f"{tmp}/f{f:04d}.png")
    prev = os.environ.get("DEMO_PREVIEW_DIR")
    if prev:
        for name, tt in (("s1", 4.8), ("s2", 7.6), ("s3", 12.5), ("s4", 15.0)):
            pg.evaluate(f"setT({tt})"); pg.screenshot(path=f"{prev}/demo-{name}.png")
    b.close()
out = os.path.join(ROOT, "assets")
run = lambda *a: subprocess.run(a, check=True, capture_output=True)
run("ffmpeg", "-y", "-framerate", str(FPS), "-i", tmp + "/f%04d.png", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-movflags", "+faststart", out + "/demo.mp4")
run("ffmpeg", "-y", "-i", out + "/demo.mp4", "-vf", "fps=12,scale=960:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96:stats_mode=diff[p];[b][p]paletteuse=dither=none:diff_mode=rectangle", out + "/demo.gif")
print("reply words", len(B["reply"].split()), "| github rows", len(F["online"]), "|", {f: os.path.getsize(os.path.join(out, f)) // 1024 for f in ("demo.mp4", "demo.gif")}, "KB")
shutil.rmtree(tmp)
