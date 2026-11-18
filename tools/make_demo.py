#!/usr/bin/env python3
"""Builds the 30 s README clip from evidence/round4/results.json (five jobs, each done without the plugin and with it).
Every number and every step on screen comes from that file. Needs playwright (with Chrome) and ffmpeg.
Usage: python3 tools/make_demo.py"""
import json, os, shutil, statistics as st, subprocess, tempfile
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
D = json.load(open(ROOT + "/evidence/round4/results.json")); R = D["runs"]
JOBS = [("deck", "slide deck"), ("model", "financial model"), ("pdf", "PDF forms"), ("landing", "landing page"), ("webtest", "web app test")]
JOBS = [j for j in JOBS if j[0] + "-A" in R and j[0] + "-B" in R]
FPS, DUR = 24, 30.0


def kind(s):
    w = (s["tool"] + " " + s["what"]).lower()
    if "find_skills" in w: return "finder"
    if "gh search" in w or s["tool"] == "WebSearch": return "search"
    if s["tool"] == "WebFetch" or "gh api" in w or "gh repo" in w or "curl" in w: return "open"
    return "read"


med = lambda arm, m: st.median(R[k + "-" + arm][m] for k, _ in JOBS)
data = dict(
    ask="I want to turn my quarterly sales numbers into a slide deck. Which skill should I use?",
    a=dict(sec=R["deck-A"]["sec"], tokens=R["deck-A"]["tokens"], steps=[dict(t=s["t"], k=kind(s)) for s in R["deck-A"]["step_list"]], words=R["deck-A"]["words"]),
    b=dict(sec=R["deck-B"]["sec"], tokens=R["deck-B"]["tokens"], steps=[dict(t=s["t"], k=kind(s)) for s in R["deck-B"]["step_list"]], words=R["deck-B"]["words"]),
    finder=json.load(open(ROOT + "/evidence/round4/finder-deck.json")),
    med=dict(tokA=med("A", "tokens"), tokB=med("B", "tokens"), secA=med("A", "sec"), secB=med("B", "sec"), stA=med("A", "steps"), stB=med("B", "steps"), costA=med("A", "cost"), costB=med("B", "cost")),
    jobs=[dict(name=n, qa=R[k + "-A"]["quality"], qb=R[k + "-B"]["quality"]) for k, n in JOBS],
    checks=["right installed skill", "3+ real GitHub options", "no invented repository", "stars shown", "license or date shown", "one recommendation"])
PAGE = r"""<!doctype html><meta charset="utf-8"><style>
*{box-sizing:border-box}html,body{margin:0;width:960px;height:540px;overflow:hidden;background:#0C131E;color:#E7EDF6;font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Helvetica Neue",Arial,sans-serif}
.mono{font-family:ui-monospace,"SF Mono",Menlo,monospace}
.scene{position:absolute;inset:0;padding:26px 30px}
.ask{display:flex;gap:14px;align-items:center;background:#141E2C;border:1px solid #28364A;border-radius:14px;padding:14px 18px;height:68px}
.av{width:38px;height:38px;border-radius:50%;background:#5B9FEA;color:#0C131E;font-weight:800;font-size:15px;display:grid;place-items:center;flex:none}
.req{font-size:17px;font-weight:600}.caret{display:inline-block;width:8px;height:18px;background:#5B9FEA;vertical-align:-3px;margin-left:2px}
.lane{position:absolute;left:30px;right:30px;height:150px;background:#141E2C;border:1px solid #28364A;border-radius:14px;padding:14px 18px}
.lane h3{margin:0;font:700 12px ui-monospace,"SF Mono",Menlo,monospace;letter-spacing:.09em}
.track{position:absolute;left:18px;right:232px;top:72px;height:6px;border-radius:3px;background:#1B2838}
.fill{position:absolute;left:0;top:0;bottom:0;border-radius:3px}
.step{position:absolute;top:-17px;width:40px;height:40px;margin-left:-20px;border-radius:12px;display:grid;place-items:center;border:2px solid #0C131E}
.step svg{width:20px;height:20px}.tick{position:absolute;top:22px;font:500 10.5px ui-monospace,"SF Mono",Menlo,monospace;color:#66758A;transform:translateX(-50%)}
.count{position:absolute;right:18px;top:14px;width:196px;text-align:right}
.count b{display:block;font-weight:800;font-size:34px;letter-spacing:-1px;font-variant-numeric:tabular-nums;line-height:1}
.count small{font-size:12px;color:#94A3B8}.count .sec{font-size:22px;margin-top:10px}
.note{position:absolute;left:18px;bottom:12px;font-size:13px;color:#94A3B8}.done{font-weight:700;border-radius:99px;padding:3px 10px;font-size:12px;color:#0C131E;margin-right:8px}
.cards{position:absolute;left:30px;right:30px;top:432px;display:grid;grid-template-columns:1fr 1.5fr 1fr;gap:12px}
.card{background:#141E2C;border:1px solid #28364A;border-radius:12px;padding:10px 14px;height:86px}
.card h4{margin:0 0 6px;font:700 10.5px ui-monospace,"SF Mono",Menlo,monospace;letter-spacing:.08em;color:#94A3B8}
.big{font-weight:800;font-size:24px;letter-spacing:-.5px}.sub{font-size:12px;color:#94A3B8}
.sb{display:grid;grid-template-columns:84px 1fr 62px;gap:8px;align-items:center;font-size:11.5px;margin-bottom:4px}.sb i{display:block;height:9px;border-radius:5px;background:#5B9FEA}.sb b{font-variant-numeric:tabular-nums;text-align:right}
.sb span{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:#94A3B8}
.rec{background:#3FD1A2;color:#0C131E;border-color:#3FD1A2}.rec h4,.rec .sub{color:#0C131E}
h1.t{margin:0 0 16px;font-size:26px;font-weight:800;letter-spacing:-.5px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.m{background:#141E2C;border:1px solid #28364A;border-radius:14px;padding:16px 18px;height:196px;position:relative}
.m h4{margin:0 0 12px;font:700 12px ui-monospace,"SF Mono",Menlo,monospace;letter-spacing:.09em;color:#94A3B8}
.bar{display:grid;grid-template-columns:78px 1fr 92px;gap:10px;align-items:center;margin-bottom:10px;font-size:13px;color:#94A3B8}
.bar div{height:26px;border-radius:7px;background:#1B2838;overflow:hidden}.bar i{display:block;height:100%;border-radius:7px}
.bar b{font-weight:800;font-size:19px;color:#E7EDF6;font-variant-numeric:tabular-nums;text-align:right}
.claim{position:absolute;left:18px;bottom:14px;font-weight:800;font-size:20px;letter-spacing:-.3px}
.qg{display:grid;grid-template-columns:1fr 1fr;gap:12px}.qs h5{margin:0 0 5px;font:700 11px ui-monospace,"SF Mono",Menlo,monospace;letter-spacing:.08em}
.qr{display:flex;gap:5px;margin-bottom:5px}.qr i{width:17px;height:17px;border-radius:5px;display:block;background:#1B2838}
.end{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px;text-align:center;background:#0C131E}
.end h1{margin:0;font-weight:800;font-size:60px;letter-spacing:-1.5px}.end p{margin:0;font-size:22px;color:#94A3B8}
.three{display:flex;gap:34px;margin-bottom:10px}.three div{font-weight:800;font-size:34px;letter-spacing:-1px}.three small{display:block;font:500 13px -apple-system,sans-serif;color:#94A3B8;letter-spacing:0}
.url{font:600 16px ui-monospace,"SF Mono",Menlo,monospace;background:#1B2838;border:1px solid #28364A;border-radius:8px;padding:9px 16px;margin-top:6px}
[hidden]{display:none!important}
</style>
<div class="scene" id="race">
 <div class="ask"><div class="av">Y</div><div class="req"><span id="req"></span><span class="caret" id="caret"></span></div></div>
 <div class="lane" id="la" style="top:108px"><h3 style="color:#F08A5D">WITHOUT THE PLUGIN</h3><div class="track"><div class="fill" id="fa" style="background:#F08A5D"></div><span id="sa"></span><span id="ticks"></span></div>
  <div class="count"><b id="ta" style="color:#F08A5D">0</b><small>tokens</small><b class="sec" id="ca">0 s</b></div><div class="note" id="na"></div></div>
 <div class="lane" id="lb" style="top:270px"><h3 style="color:#5B9FEA">WITH STRAIGHT ANSWER</h3><div class="track"><div class="fill" id="fb" style="background:#5B9FEA"></div><span id="sb"></span><span id="ticks2"></span></div>
  <div class="count"><b id="tb" style="color:#5B9FEA">0</b><small>tokens</small><b class="sec" id="cb">0 s</b></div><div class="note" id="nb"></div></div>
 <div class="cards" id="cards"></div>
</div>
<div class="scene" id="score" hidden><h1 class="t" id="st"></h1><div class="grid" id="grid"></div></div>
<div class="scene end" id="end" hidden><div class="three" id="three"></div><h1>Straight Answer</h1><p>The right skill for the job.</p><div class="url mono">github.com/alibb007/straight-answer</div></div>
<script>
const D=__DATA__,$=s=>document.querySelector(s),fmt=n=>Math.round(n).toLocaleString('en-US'),cl=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
const IC={search:'<circle cx="9" cy="9" r="5.5" fill="none" stroke="currentColor" stroke-width="2.4"/><path d="M13.5 13.5L18 18" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/>',
 open:'<rect x="3" y="4" width="14" height="12" rx="2.5" fill="none" stroke="currentColor" stroke-width="2.2"/><path d="M3 8h14" stroke="currentColor" stroke-width="2.2"/>',
 read:'<path d="M5 3h7l4 4v10H5z" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round"/><path d="M8 11h5M8 14h5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
 finder:'<path d="M10 2l2.3 5.2 5.7.6-4.2 3.8 1.2 5.6L10 14.4 5 17.2l1.2-5.6L2 7.8l5.7-.6z" fill="currentColor"/>'};
const LAB={search:'search',open:'open a page',read:'read files',finder:'finder'};
const TMAX=Math.max(D.a.sec,D.b.sec),RS=3.4,RE=13.0,X=t=>100*t/TMAX;
function lane(id,L,col){$(id).innerHTML=L.steps.map(s=>'<div class="step" data-t="'+s.t+'" style="left:'+X(s.t)+'%;background:'+col+';color:#0C131E"><svg viewBox="0 0 20 20">'+IC[s.k]+'</svg></div>').join('')}
lane('#sa',D.a,'#F08A5D');lane('#sb',D.b,'#5B9FEA');
let tk='';for(let s=0;s<=TMAX;s+=10)tk+='<span class="tick" style="left:'+X(s)+'%">'+s+' s</span>';$('#ticks').innerHTML=tk;$('#ticks2').innerHTML=tk;
const F=D.finder,mx=Math.max(...F.online.map(o=>o.stars),1);
$('#cards').innerHTML='<div class="card" data-c="0"><h4>INSTALLED ON YOUR COMPUTER</h4><div class="big">'+F.local.map(s=>s.name).join(', ')+'</div><div class="sub">'+F.local.length+' fits, of '+F.installed_total+' installed</div></div>'
 +'<div class="card" data-c="1"><h4>AVAILABLE ON GITHUB · STARS</h4>'+F.online.slice(0,3).map(o=>'<div class="sb"><span>'+o.repo.split('/')[1]+'</span><div><i style="width:'+Math.max(3,100*o.stars/mx)+'%"></i></div><b>'+fmt(o.stars)+'</b></div>').join('')+'</div>'
 +'<div class="card rec" data-c="2"><h4>RECOMMENDED</h4><div class="big">'+F.recommended.name+'</div><div class="sub">already installed</div></div>';
const M=D.med,ratio=(a,b)=>a/b,say=(a,b,less,more,same)=>{const r=a/b;return r>=1.15?(r>=2?r.toFixed(1).replace('.0','')+'× ':Math.round((1-b/a)*100)+'% ')+less:r<=0.87?(1/r>=2?(1/r).toFixed(1).replace('.0','')+'× ':Math.round((b/a-1)*100)+'% ')+more:same};
const bars=(h,a,b,unit,claim,id)=>'<div class="m" data-m="'+id+'"><h4>'+h+'</h4><div class="bar"><span>Without</span><div><i data-w="'+100*a/Math.max(a,b)+'" style="background:#F08A5D"></i></div><b>'+unit(a)+'</b></div><div class="bar"><span>With</span><div><i data-w="'+100*b/Math.max(a,b)+'" style="background:#5B9FEA"></i></div><b>'+unit(b)+'</b></div><div class="claim">'+claim+'</div></div>';
const qrow=(q,col)=>'<div class="qr">'+q.map(v=>'<i style="'+(v?'background:'+col:'')+'"></i>').join('')+'</div>';
const qa=D.jobs.reduce((s,j)=>s+j.qa.filter(Boolean).length,0),qb=D.jobs.reduce((s,j)=>s+j.qb.filter(Boolean).length,0),qt=D.jobs.length*6;
$('#st').textContent='Same question, '+D.jobs.length+' different jobs';
$('#grid').innerHTML=bars('TOKENS USED',M.tokA,M.tokB,fmt,say(M.tokA,M.tokB,'fewer tokens','more tokens','about the same tokens'),0)
 +bars('TIME TO AN ANSWER',M.secA,M.secB,v=>Math.round(v)+' s',say(M.secA,M.secB,'faster','slower','about the same time'),1)
 +bars('STEPS THE ASSISTANT TOOK',M.stA,M.stB,v=>Math.round(v),Math.round(M.stB)+(Math.round(M.stB)===1?' step':' steps')+' instead of '+Math.round(M.stA),2)
 +'<div class="m" data-m="3"><h4>QUALITY · 6 CHECKS × '+D.jobs.length+' JOBS</h4><div class="qg"><div class="qs"><h5 style="color:#F08A5D">WITHOUT · '+qa+' of '+qt+'</h5>'+D.jobs.map(j=>qrow(j.qa,'#F08A5D')).join('')+'</div><div class="qs"><h5 style="color:#5B9FEA">WITH · '+qb+' of '+qt+'</h5>'+D.jobs.map(j=>qrow(j.qb,'#5B9FEA')).join('')+'</div></div></div>';
$('#three').innerHTML='<div style="color:#5B9FEA">'+fmt(M.tokB)+'<small>tokens, was '+fmt(M.tokA)+'</small></div><div style="color:#5B9FEA">'+Math.round(M.secB)+' s<small>was '+Math.round(M.secA)+' s</small></div><div style="color:#5B9FEA">'+qb+' / '+qt+'<small>quality checks, without '+qa+'</small></div>';
window.setT=function(t){
  const k=cl((t-0.3)/2.6);$('#req').textContent=D.ask.slice(0,Math.round(D.ask.length*k));$('#caret').hidden=t>3.1;
  const rt=cl((t-RS)/(RE-RS))*TMAX;                       // real seconds shown on the shared clock
  [['a',D.a,'#F08A5D'],['b',D.b,'#5B9FEA']].forEach(([x,L,col])=>{const r=Math.min(rt,L.sec);
    $('#f'+x).style.width=X(r)+'%';$('#t'+x).textContent=fmt(L.tokens*r/L.sec);$('#c'+x).textContent=Math.round(r)+' s';
    document.querySelectorAll('#s'+x+' .step').forEach(e=>{const a=+e.dataset.t;e.hidden=rt<a;e.style.transform='scale('+cl((rt-a)/(TMAX*0.02),0.4,1)+')'});
    const n=L.steps.filter(s=>s.t<=rt).length,done=rt>=L.sec;
    $('#n'+x).innerHTML=(done?'<span class="done" style="background:'+col+'">done</span>':'')+n+(n===1?' step':' steps')+(done?' · answer of '+L.words+' words':'')});
  $('#la').style.opacity=$('#lb').style.opacity=cl((t-3.0)/0.4);
  document.querySelectorAll('#cards .card').forEach(e=>{const a=RS+(RE-RS)*D.b.sec/TMAX+0.3+0.45*(+e.dataset.c);e.style.opacity=cl((t-a)/0.35);e.style.transform='translateY('+(1-cl((t-a)/0.35))*10+'px)'});
  $('#race').hidden=t>=14.6;$('#race').style.opacity=cl((14.6-t)/0.4);
  $('#score').hidden=t<14.6||t>=25.6;$('#score').style.opacity=Math.min(cl((t-14.6)/0.4),cl((25.6-t)/0.4));
  document.querySelectorAll('#grid .m').forEach(e=>{const a=15.0+2.3*(+e.dataset.m);e.style.opacity=cl((t-a)/0.4);e.querySelectorAll('.bar i').forEach(i=>i.style.width=(+i.dataset.w)*cl((t-a-0.2)/0.9)+'%');
    e.querySelectorAll('.qr i').forEach((i,n)=>i.style.opacity=cl((t-a-0.2-n*0.03)/0.2));const c=e.querySelector('.claim');if(c)c.style.opacity=cl((t-a-1.1)/0.3)});
  $('#end').hidden=t<25.6;$('#end').style.opacity=cl((t-25.6)/0.4);
};setT(0);
</script>"""
tmp = tempfile.mkdtemp(); open(tmp + "/demo.html", "w").write(PAGE.replace("__DATA__", json.dumps(data)))
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)
    pg = b.new_page(viewport={"width": 960, "height": 540}, device_scale_factor=2)
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("file://" + tmp + "/demo.html")
    prev = os.environ.get("DEMO_PREVIEW_DIR")
    if prev:
        for name, tt in (("s1", 8.0), ("s2", 13.8), ("s3", 20.2), ("s4", 24.8), ("s5", 28.5), ("s6", 2.0)):
            pg.evaluate(f"setT({tt})"); pg.screenshot(path=f"{prev}/demo-{name}.png")
    if not os.environ.get("DEMO_STILLS_ONLY"):
        for f in range(int(FPS * DUR)):
            pg.evaluate(f"setT({f / FPS})"); pg.screenshot(path=f"{tmp}/f{f:04d}.png")
    b.close()
print("page errors:", errs or "none")
if not os.environ.get("DEMO_STILLS_ONLY"):
    out = os.path.join(ROOT, "assets"); run = lambda *a: subprocess.run(a, check=True, capture_output=True)
    run("ffmpeg", "-y", "-framerate", str(FPS), "-i", tmp + "/f%04d.png", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-movflags", "+faststart", out + "/demo.mp4")
    run("ffmpeg", "-y", "-i", out + "/demo.mp4", "-vf", "fps=12,scale=960:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128:stats_mode=diff[p];[b][p]paletteuse=dither=none:diff_mode=rectangle", out + "/demo.gif")
    print({f: os.path.getsize(os.path.join(out, f)) // 1024 for f in ("demo.mp4", "demo.gif")}, "KB")
shutil.rmtree(tmp)
