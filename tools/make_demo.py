#!/usr/bin/env python3
"""Builds the README demo clip from one real pair in evidence/round3 (request S20):
the same request answered without the plugin and with it. Needs playwright (with Chrome) and ffmpeg.
Usage: python3 tools/make_demo.py            -> assets/demo.mp4 and assets/demo.gif"""
import html, json, os, re, shutil, subprocess, sys, tempfile
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
EV = os.path.join(ROOT, "evidence", "round3"); RID = "S20"
A = json.load(open(EV + "/answers.json")); R = {r["id"]: r for r in json.load(open(EV + "/requests.json"))}[RID]
FPS, DUR = 24, 16.0


def words_html(text):
    """Markdown-light text -> paragraphs of word spans. Returns (html, number of words)."""
    n, out = 0, []
    for line in text.strip().split("\n"):
        line = line.rstrip()
        if not line:
            continue
        if line.strip() == "---":
            out.append(f'<div class="p hr" data-i="{n}"></div>'); continue
        cls = "p"
        m = re.match(r"^(\d+\.|-)\s+(.*)$", line)
        if m:
            cls += " li"; line = m.group(1).replace("-", "•") + " " + m.group(2)
        parts, bold, blank, first = [], False, False, n
        for seg in re.split(r"(\*\*)", line):
            if seg == "**":
                bold = not bold; continue
            for w in seg.split():
                if w.startswith("["):
                    blank = True
                c = "w" + (" b" if bold else "") + (" blank" if blank else "")
                parts.append(f'<span class="{c}" data-i="{n}">{html.escape(w)}</span>'); n += 1
                if "]" in w:
                    blank = False
        out.append(f'<div class="{cls}" data-i="{first}">' + " ".join(parts) + "</div>")
    return "\n".join(out), n


plain, n_plain = words_html(A[RID + "-A"]["text"]); short, n_short = words_html(A[RID + "-S"]["text"])
W_PLAIN, W_SHORT = A[RID + "-A"]["words"], A[RID + "-S"]["words"]
PAGE = """<!doctype html><meta charset="utf-8"><style>
*{box-sizing:border-box}html,body{margin:0;width:960px;height:540px;overflow:hidden;background:#0C131E;color:#E7EDF6;font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Helvetica Neue",Arial,sans-serif}
.win{position:absolute;inset:14px;background:#141E2C;border:1px solid #28364A;border-radius:14px;overflow:hidden}
.bar{height:34px;background:#1B2838;display:flex;align-items:center;gap:7px;padding:0 14px;font:600 12px ui-monospace,"SF Mono",Menlo,monospace;color:#94A3B8}
.bar i{width:11px;height:11px;border-radius:50%;display:block}.bar span{margin-left:auto;margin-right:auto;transform:translateX(-24px)}
.ask{display:flex;gap:12px;padding:14px 18px 12px;border-bottom:1px solid #28364A;height:92px}
.av{width:34px;height:34px;border-radius:50%;background:#5B9FEA;color:#0C131E;font:800 14px -apple-system,sans-serif;display:grid;place-items:center;flex:none}
.ask b{display:block;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:#94A3B8;margin-bottom:3px}
.req{font-size:13.5px;line-height:1.42;color:#E7EDF6}.caret{display:inline-block;width:7px;height:15px;background:#5B9FEA;vertical-align:-2px;margin-left:1px}
.cols{position:absolute;left:0;right:0;top:127px;bottom:0;display:grid;grid-template-columns:1fr 1fr;gap:0}
.col{position:relative;padding:12px 18px 0;overflow:hidden}.col+.col{border-left:1px solid #28364A}
.head{display:flex;justify-content:space-between;align-items:center;font:700 11px ui-monospace,"SF Mono",Menlo,monospace;letter-spacing:.08em;margin-bottom:8px}
.col.a .head{color:#F08A5D}.col.s .head{color:#5B9FEA}.head em{font-style:normal;color:#E7EDF6;font-size:12px}
.body{position:absolute;left:18px;right:18px;top:38px;bottom:40px;overflow:hidden}
.txt{font-size:12.4px;line-height:1.5}.p{margin:0 0 7px}.p.li{padding-left:10px}.p.hr{border-top:1px solid #28364A;margin:9px 0}
.w.b{font-weight:700}.w.blank{background:#F08A5D;color:#0C131E;border-radius:3px;padding:0 3px;font-weight:700}
.foot{position:absolute;left:18px;right:18px;bottom:10px;height:24px;display:flex;align-items:center;gap:8px;font-size:12px;color:#94A3B8}
.tag{border-radius:99px;padding:3px 10px;font-weight:700;font-size:11.5px}.tag.o{background:#F08A5D;color:#0C131E}.tag.g{background:#3FD1A2;color:#0C131E}
.fade{position:absolute;left:0;right:0;bottom:40px;height:26px;background:linear-gradient(#141E2C00,#141E2C)}
.end{position:absolute;inset:0;background:#0C131EF2;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px;text-align:center}
.end h1{margin:0;font:800 54px -apple-system,sans-serif;letter-spacing:-1.5px}.end p{margin:0;font-size:21px;color:#94A3B8}
.nums{display:flex;gap:18px;align-items:center;font:800 30px -apple-system,sans-serif}.nums .o{color:#F08A5D}.nums .s{color:#5B9FEA}.nums small{display:block;font:500 13px -apple-system,sans-serif;color:#94A3B8}
.url{font:600 15px ui-monospace,"SF Mono",Menlo,monospace;color:#E7EDF6;background:#1B2838;border:1px solid #28364A;border-radius:8px;padding:8px 14px;margin-top:6px}
[hidden]{display:none!important}
</style>
<div class="win"><div class="bar"><i style="background:#F08A5D"></i><i style="background:#66758A"></i><i style="background:#3FD1A2"></i><span>Claude Code</span></div>
<div class="ask"><div class="av">Y</div><div><b>You</b><div class="req"><span id="req"></span><span class="caret" id="caret"></span></div></div></div>
<div class="cols" id="cols" hidden>
 <div class="col a"><div class="head"><span>WITHOUT THE PLUGIN</span><em id="ca"></em></div><div class="body"><div class="txt" id="ta">__PLAIN__</div></div><div class="fade"></div><div class="foot"><span class="tag o" id="fa" hidden>blanks left to fill in</span></div></div>
 <div class="col s"><div class="head"><span>WITH STRAIGHT ANSWER</span><em id="cs"></em></div><div class="body"><div class="txt" id="ts">__SHORT__</div></div><div class="foot"><span class="tag g" id="fs" hidden>ready to send</span></div></div>
</div></div>
<div class="end" id="end" hidden><div class="nums"><div class="o">__WP__<small>words without</small></div><div style="color:#66758A">→</div><div class="s">__WS__<small>words with</small></div></div><h1>Straight Answer</h1><p>Short, finished AI answers.</p><div class="url">github.com/alibb007/straight-answer</div></div>
<script>
const REQ=__REQ__,NP=__NP__,NS=__NS__,WP=__WP__,WS=__WS__,RATE=42,T0=4.4;
function reveal(root,n){root.querySelectorAll('.w').forEach(e=>e.hidden=+e.dataset.i>=n);root.querySelectorAll('.p').forEach(e=>e.hidden=+e.dataset.i>=n);const b=root.parentElement;root.style.transform='translateY('+Math.min(0,b.clientHeight-root.scrollHeight)+'px)'}
window.setT=function(t){
  const k=Math.max(0,Math.min(1,(t-0.4)/3.2));document.getElementById('req').textContent=REQ.slice(0,Math.round(REQ.length*k));
  document.getElementById('caret').hidden=t>3.9;document.getElementById('cols').hidden=t<T0;
  const n=Math.max(0,Math.floor((t-T0)*RATE)),na=Math.min(NP,n),ns=Math.min(NS,n);
  reveal(document.getElementById('ta'),na);reveal(document.getElementById('ts'),ns);
  document.getElementById('ca').textContent=Math.round(WP*na/NP)+' words';document.getElementById('cs').textContent=Math.round(WS*ns/NS)+' words';
  document.getElementById('fs').hidden=ns<NS;document.getElementById('fa').hidden=na<NP;
  const e=document.getElementById('end');e.hidden=t<13;e.style.opacity=Math.max(0,Math.min(1,(t-13)/0.4));
};setT(0);
</script>"""
page = (PAGE.replace("__PLAIN__", plain).replace("__SHORT__", short).replace("__REQ__", json.dumps(R["prompt"].strip()))
        .replace("__NP__", str(n_plain)).replace("__NS__", str(n_short)).replace("__WP__", str(W_PLAIN)).replace("__WS__", str(W_SHORT)))
tmp = tempfile.mkdtemp(); open(tmp + "/demo.html", "w").write(page)
if "--html-only" in sys.argv:
    print(tmp + "/demo.html"); sys.exit()
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)
    pg = b.new_page(viewport={"width": 960, "height": 540}, device_scale_factor=2)
    pg.goto("file://" + tmp + "/demo.html")
    stills = {5.6: "s1", 9.0: "s2", 12.5: "s3", 14.5: "s4"}
    for f in range(int(FPS * DUR)):
        pg.evaluate(f"setT({f / FPS})"); pg.screenshot(path=f"{tmp}/f{f:04d}.png")
    for t, name in stills.items():
        pg.evaluate(f"setT({t})"); pg.screenshot(path=f"{tmp}/{name}.png")
    b.close()
out = os.path.join(ROOT, "assets")
run = lambda *a: subprocess.run(a, check=True, capture_output=True)
run("ffmpeg", "-y", "-framerate", str(FPS), "-i", tmp + "/f%04d.png", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-movflags", "+faststart", out + "/demo.mp4")
run("ffmpeg", "-y", "-i", out + "/demo.mp4", "-vf", "fps=12,scale=960:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96:stats_mode=diff[p];[b][p]paletteuse=dither=none:diff_mode=rectangle", out + "/demo.gif")
for name in stills.values():
    shutil.copy(f"{tmp}/{name}.png", f"/tmp/claude-501/sa_prev/demo-{name}.png") if os.path.isdir("/tmp/claude-501/sa_prev") else None
print("plain words", W_PLAIN, "spans", n_plain, "| short words", W_SHORT, "spans", n_short)
print({f: os.path.getsize(os.path.join(out, f)) // 1024 for f in ("demo.mp4", "demo.gif")}, "KB")
shutil.rmtree(tmp)
