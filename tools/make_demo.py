#!/usr/bin/env python3
"""Builds the 30 s README clip.
- The Claude Code window is redrawn from a real session log (evidence/round5/deck-B-session.json): the command, the tool call,
  the finder's output and the answer are the logged text, with links cut for space. The clock shows the real seconds.
- The scoreboard comes from evidence/round5/results.json (five jobs, each asked without the plugin and with it).
- The short-answer numbers come from evidence/round3.
Needs playwright (with Chrome) and ffmpeg. Usage: python3 tools/make_demo.py"""
import html, json, os, re, shutil, statistics as st, subprocess, tempfile
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
D = json.load(open(ROOT + "/evidence/round5/results.json")); R = D["runs"]
S = json.load(open(ROOT + "/evidence/round5/deck-B-session.json"))
JOBS = [("deck", "slide deck"), ("model", "financial model"), ("pdf", "PDF forms"), ("landing", "landing page"), ("webtest", "web app test")]
JOBS = [j for j in JOBS if j[0] + "-A" in R and j[0] + "-B" in R]
FPS, DUR = 24, 24.0
INSTALLED = ["academy-guide", "algorithmic-art", "brand-guidelines", "canvas-design", "claude-api", "discernment-nudge", "doc-coauthoring", "docx", "frontend-design", "internal-comms",
             "mcp-builder", "pdf", "pptx", "skill-creator", "slack-gif-creator", "theme-factory", "web-artifacts-builder", "webapp-testing", "xlsx"]  # the 19 public skills in the test folder


def answer_lines(text):
    """The logged answer, line by line, links and the folder path cut so it fits the window. Returns [(section, html)]."""
    out, sec = [], 0
    for ln in text.split("\n"):
        if not ln.strip():
            continue
        m = re.match(r"\*\*(\d)\.", ln)
        if m:
            sec = int(m.group(1))
        if ln.startswith("For the charts") or ln.startswith("Nothing was installed"):
            sec = 4
        ln = re.sub(r" · https://\S+", "", ln)
        ln = re.sub(r" It's installed at `[^`]+`\.", "", ln)
        h = html.escape(ln)
        h = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", h)
        h = re.sub(r"`(.+?)`", r"<i>\1</i>", h)
        out.append((sec, h))
    return [x for x in out if x[0] in (1, 2, 3)]


def finder_facts(text):
    """Numbers for the three side cards, read from the finder output in the log."""
    have = re.search(r"WHAT YOU HAVE \((\d+) fit, of (\d+) installed", text)
    rows = re.findall(r"^\s+\d\. ([\d,]+) stars\s+(\S+)\s+\[([^\],]+)", text, re.M)
    pick = re.search(r"RECOMMENDED, AND HOW TO USE IT\n\s+(\S+)\s+\((.+?)\)", text)
    call = re.search(r"Call it:\s+(.+)", text)
    needs = re.search(r"It needs:\s+(.+?)(?:\s+\(named in its instructions\))?$", text, re.M)
    return dict(fit=int(have.group(1)), total=int(have.group(2)), rows=[dict(stars=int(a.replace(",", "")), skill=b, repo=c) for a, b, c in rows],
                pick=pick.group(1), where=pick.group(2), call=call.group(1).strip(), needs=[x.strip() for x in re.split(r"[:,·]", needs.group(1)) if x.strip() and x.strip() not in ("npm", "pip", "npx", "brew", "keys")] if needs else [])


ev = {e["kind"]: e for e in S["events"]}
med = lambda arm, m: st.median(R[k + "-" + arm][m] for k, _ in JOBS)
data = dict(
    ask=S["ask"], tool=re.sub(r'python3 "<plugin>/skills/find-skill/scripts/', "python3 …/", ev["tool"]["command"]).replace('.py" "', '.py "'),
    t_tool=ev["tool"]["t"], t_res=ev["tool_result"]["t"], t_ans=ev["answer"]["t"], t_done=S["done"], tokens=S["tokens"],
    res_head=ev["tool_result"]["text"].split("\n")[3].strip(), res_more=len(ev["tool_result"]["text"].split("\n")) - 1,
    lines=answer_lines(S["result"]), f=finder_facts(ev["tool_result"]["text"]), installed=INSTALLED,
    med=dict(tokA=med("A", "tokens"), tokB=med("B", "tokens"), secA=med("A", "sec"), secB=med("B", "sec"), stA=med("A", "steps"), stB=med("B", "steps")),
    jobs=[dict(name=n, qa=R[k + "-A"]["quality"], qb=R[k + "-B"]["quality"]) for k, n in JOBS])
PAGE = r"""<!doctype html><meta charset="utf-8"><style>
*{box-sizing:border-box}html,body{margin:0;width:960px;height:540px;overflow:hidden;background:#0B111B;color:#E7EDF6;font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Helvetica Neue",Arial,sans-serif}
.mono{font-family:"SF Mono",ui-monospace,Menlo,monospace}
.scene{position:absolute;inset:0;padding:26px 30px}
[hidden]{display:none!important}
/* 1 problem */
#s1 h1{margin:6px 0 0;font-size:46px;font-weight:800;letter-spacing:-1.4px}#s1 p{margin:6px 0 0;font-size:19px;color:#94A3B8}
.chips{position:absolute;left:30px;right:30px;top:150px;display:flex;flex-wrap:wrap;gap:10px}
.chip{display:flex;align-items:center;gap:8px;background:#141E2C;border:1px solid #28364A;border-radius:11px;padding:9px 13px;font:600 14.5px "SF Mono",ui-monospace,Menlo,monospace;color:#C9D5E6}
.chip svg{width:15px;height:15px;color:#5B9FEA;flex:none}
.qs{position:absolute;left:0;right:0;top:378px;display:flex;justify-content:center;gap:16px}
.q{background:#F08A5D;color:#0B111B;font-weight:800;font-size:23px;letter-spacing:-.4px;border-radius:16px 16px 16px 4px;padding:14px 20px;box-shadow:0 12px 30px rgba(0,0,0,.45)}
/* 2 claude code window + three steps */
.win{position:absolute;left:24px;top:22px;width:616px;height:496px;background:#10161F;border:1px solid #2A3648;border-radius:12px;overflow:hidden;box-shadow:0 18px 44px rgba(0,0,0,.5)}
.bar{height:30px;background:#1A2230;border-bottom:1px solid #2A3648;display:flex;align-items:center;padding:0 12px;gap:7px}
.bar u{width:11px;height:11px;border-radius:50%;display:block}.bar span{flex:1;text-align:center;font:500 12px "SF Mono",ui-monospace,Menlo,monospace;color:#8291A6;margin-right:44px}
.cc{padding:10px 14px 0;font:500 11.6px/1.52 "SF Mono",ui-monospace,Menlo,monospace;color:#C9D5E6}
.cc .hd{color:#E0875F;font-weight:700}.cc .hd em{font-style:normal;color:#66758A;font-weight:500}
.cc .me{color:#8291A6;margin-top:7px}.cc .me b{color:#E7EDF6;font-weight:600}
.cc .tl{margin-top:7px}.cc .dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:7px}
.cc .sub{color:#8291A6;padding-left:15px}.cc .ans{margin-top:7px}
.cc .ln{padding-left:15px;text-indent:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.cc .ln.h{padding-left:0;margin-top:5px}
.cc .ln b{color:#fff;font-weight:700}.cc .ln i{font-style:normal;color:#7FB5F0}
.cc .ln.h b{color:#7FB5F0}.cc .ln{border-radius:3px}.cc .ln.on1,.cc .ln.on2{background:rgba(91,159,234,.14);box-shadow:-3px 0 0 #5B9FEA}.cc .ln.on3{background:rgba(63,209,162,.14);box-shadow:-3px 0 0 #3FD1A2}.cc .ln.on3.h b{color:#3FD1A2}
.inp{position:absolute;left:12px;right:12px;bottom:28px;border:1px solid #3A4A61;border-radius:8px;padding:8px 11px;font:500 12px "SF Mono",ui-monospace,Menlo,monospace;color:#E7EDF6;background:#10161F}
.inp s{text-decoration:none;color:#66758A;margin-right:8px}.caret{display:inline-block;width:7px;height:14px;background:#E7EDF6;vertical-align:-2px;margin-left:1px}
.hint{position:absolute;left:14px;right:14px;bottom:8px;font:500 10.5px "SF Mono",ui-monospace,Menlo,monospace;color:#56657A;display:flex;justify-content:space-between}
.rail{position:absolute;left:656px;top:22px;width:280px;display:flex;flex-direction:column;gap:11px}
.st{transform-origin:left center;height:158px;background:#141E2C;border:1.5px solid #28364A;border-radius:14px;padding:12px 14px;position:relative}
.st h4{margin:0;display:flex;align-items:center;gap:9px;font-size:15px;font-weight:800;letter-spacing:-.2px}
.st h4 em{font-style:normal;width:24px;height:24px;border-radius:50%;display:grid;place-items:center;font-size:13px;background:#28364A;color:#94A3B8}
.st .body{margin-top:10px}
.dots{display:grid;grid-template-columns:repeat(10,1fr);gap:6px}.dots i{height:18px;border-radius:5px;background:#28364A;display:block}
.sm{font-size:12.5px;color:#94A3B8;margin-top:9px}.sm b{color:#E7EDF6}
.sb{display:grid;grid-template-columns:96px 1fr 58px;gap:7px;align-items:center;font-size:11.5px;margin-bottom:5px}.sb u{display:block;height:10px;border-radius:5px;background:#1B2838;text-decoration:none}
.sb i{display:block;height:100%;border-radius:5px;background:#5B9FEA}.sb b{font-variant-numeric:tabular-nums;text-align:right}.sb span{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:#C9D5E6}
.cmd{font:700 15px "SF Mono",ui-monospace,Menlo,monospace;background:#0B111B;border:1px solid #3FD1A2;color:#3FD1A2;border-radius:8px;padding:8px 10px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tags{display:flex;flex-wrap:wrap;gap:5px;margin-top:8px}.tags span{font:600 10.5px "SF Mono",ui-monospace,Menlo,monospace;background:#1B2838;border-radius:6px;padding:3px 7px;color:#C9D5E6}
.tags .ok{background:#3FD1A2;color:#0B111B}
.clock{position:absolute;right:12px;top:40px;font:700 12px "SF Mono",ui-monospace,Menlo,monospace;color:#0B111B;background:#E7EDF6;border-radius:99px;padding:3px 10px}
/* 3 scoreboard */
h1.t{margin:0 0 16px;font-size:27px;font-weight:800;letter-spacing:-.5px}h1.t small{font-size:15px;font-weight:500;color:#94A3B8;letter-spacing:0;margin-left:10px}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.m{background:#141E2C;border:1px solid #28364A;border-radius:14px;padding:20px 20px;height:300px;position:relative}
.m h4{margin:14px 0 14px;font:700 12px "SF Mono",ui-monospace,Menlo,monospace;letter-spacing:.09em;color:#94A3B8}
.br{display:grid;grid-template-columns:58px 1fr 82px;gap:10px;align-items:center;margin-bottom:10px;font-size:13px;color:#94A3B8}
.br div{height:26px;border-radius:7px;background:#1B2838;overflow:hidden}.br i{display:block;height:100%;border-radius:7px}
.br b{font-weight:800;font-size:19px;color:#E7EDF6;font-variant-numeric:tabular-nums;text-align:right}
.claim b{display:block;font-weight:800;font-size:64px;letter-spacing:-2.5px;color:#5B9FEA;line-height:1}.claim span{font-weight:700;font-size:21px;letter-spacing:-.3px}
.ql{margin-top:14px;background:#141E2C;border:1px solid #28364A;border-radius:14px;padding:16px 20px;font-size:18px;display:flex;justify-content:space-between;align-items:center}.ql b{font-weight:800}.ql span{color:#94A3B8}
.qg{display:grid;grid-template-columns:1fr 1fr;gap:12px}.qsx h5{margin:0 0 5px;font:700 11px "SF Mono",ui-monospace,Menlo,monospace;letter-spacing:.06em}
.qr{display:flex;gap:4px;margin-bottom:5px}.qr i{width:15px;height:15px;border-radius:4px;display:block;background:#1B2838}
/* 4 short answers */
.docs{position:absolute;left:30px;top:96px;display:flex;gap:16px}
.doc{width:262px;height:390px;background:#141E2C;border:1px solid #28364A;border-radius:14px;padding:16px 18px;position:relative;overflow:hidden}
.doc h4{margin:0 0 12px;font:700 12px "SF Mono",ui-monospace,Menlo,monospace;letter-spacing:.09em}
.doc u{display:block;height:8px;border-radius:4px;margin-bottom:9px;background:#3A4A61}.doc u.x{background:#F08A5D}
.doc .w{position:absolute;left:18px;bottom:14px;font-weight:800;font-size:26px;letter-spacing:-.6px}.doc .w small{font-size:13px;font-weight:500;color:#94A3B8;letter-spacing:0;margin-left:6px}
.facts{position:absolute;left:602px;right:30px;top:96px;display:flex;flex-direction:column;gap:12px}
.fact{background:#141E2C;border:1px solid #28364A;border-radius:14px;padding:24px 22px;height:189px}
.fact b{display:block;font-weight:800;font-size:56px;letter-spacing:-1.2px;color:#5B9FEA;line-height:1.05}.fact span{font-size:18px;color:#C9D5E6}.fact small{display:block;font-size:12px;color:#8291A6;margin-top:3px}
/* 5 end */
.end{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;text-align:center}
.end h1{margin:0;font-weight:800;font-size:62px;letter-spacing:-1.6px}.end p{margin:0;font-size:22px;color:#94A3B8}
.flow{display:flex;align-items:center;gap:12px;margin-bottom:14px}.flow div{background:#141E2C;border:1px solid #28364A;border-radius:12px;padding:10px 16px;font-weight:700;font-size:17px;display:flex;gap:9px;align-items:center}
.flow div em{font-style:normal;width:24px;height:24px;border-radius:50%;display:grid;place-items:center;font-size:13px;background:#5B9FEA;color:#0B111B}.flow svg{width:22px;height:22px;color:#56657A}
.url{font:600 16px "SF Mono",ui-monospace,Menlo,monospace;background:#1B2838;border:1px solid #28364A;border-radius:8px;padding:9px 16px;margin-top:8px}
</style>
<div class="scene" id="s1"><h1>So many skills.</h1><p id="s1p"></p><div class="chips" id="chips"></div>
 <div class="qs"><div class="q" data-q="0">Which one do I use?</div><div class="q" data-q="1">Is there a better one out there?</div><div class="q" data-q="2">How do I use it?</div></div></div>
<div class="scene" id="s2" hidden>
 <div class="win"><div class="bar"><u style="background:#EC6A5E"></u><u style="background:#F4BF4F"></u><u style="background:#61C554"></u><span>claude · ~/my-project</span></div>
  <div class="cc" id="cc"></div><div class="clock" id="clock" hidden></div>
  <div class="inp"><s>&gt;</s><span id="typed"></span><span class="caret" id="caret"></span></div>
  <div class="hint"><span>plugin: straight-answer 2.0.0</span><span>Opus</span></div></div>
 <div class="rail" id="rail"></div></div>
<div class="scene" id="s3" hidden><h1 class="t" id="t3"></h1><div class="grid" id="grid"></div><div class="ql" id="ql"></div></div>
<div class="scene" id="s4" hidden><h1 class="t">And every answer comes back short and finished<small>42 everyday requests</small></h1>
 <div class="docs"><div class="doc" id="da"><h4 style="color:#F08A5D">PLAIN REQUEST</h4><span id="la"></span><div class="w" style="color:#F08A5D">488<small>words</small></div></div>
  <div class="doc" id="db" style="border-color:#5B9FEA"><h4 style="color:#5B9FEA">WITH THE PLUGIN</h4><span id="lb"></span><div class="w" style="color:#5B9FEA">245<small>words</small></div></div></div>
 <div class="facts"><div class="fact" data-f="0"><b>half</b><span>the words per answer</span><small>245 against 488, shorter in 42 of 42</small></div>
  <div class="fact" data-f="1"><b>0 of 42</b><span>answers left a blank like [Name]</span><small>plain requests: 6 of 42</small></div></div></div>
<div class="scene end" id="s5" hidden><div class="flow" id="flow"></div><h1>Straight Answer</h1><p id="endp"></p><div class="url">github.com/alibb007/straight-answer</div></div>
<script>
const D=__DATA__,$=s=>document.querySelector(s),$$=s=>document.querySelectorAll(s),fmt=n=>Math.round(n).toLocaleString('en-US'),cl=(x,a=0,b=1)=>Math.max(a,Math.min(b,x)),ease=x=>1-Math.pow(1-cl(x),3);
const DOC='<svg viewBox="0 0 20 20"><path d="M5 2.5h7l4 4v11H5z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M8 11h5M8 14h5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>';
$('#s1p').textContent=D.installed.length+' on this computer, and many more on GitHub.';
$('#chips').innerHTML=D.installed.map((n,i)=>'<div class="chip" data-i="'+i+'">'+DOC+n+'</div>').join('');
// scene 2
const F=D.f,mx=Math.max(...F.rows.map(o=>o.stars),1),pickAt=D.installed.indexOf(F.pick);
$('#rail').innerHTML='<div class="st" data-s="1"><h4><em>1</em>What you have</h4><div class="body"><div class="dots">'+D.installed.map((n,i)=>'<i data-d="'+i+'"></i>').join('')+'</div><div class="sm"><b>'+F.pick+'</b> fits · '+F.fit+' of '+F.total+' installed</div><div class="sm" style="margin-top:3px">checked on your computer, nothing sent</div></div></div>'
 +'<div class="st" data-s="2"><h4><em>2</em>The best on GitHub</h4><div class="body">'+F.rows.slice(0,4).map(o=>'<div class="sb"><span>'+o.skill+'</span><u><i data-w="'+Math.max(4,100*o.stars/mx)+'"></i></u><b>'+fmt(o.stars)+'</b></div>').join('')+'<div class="sm" style="margin-top:6px">most stars first · license · last update</div></div></div>'
 +'<div class="st" data-s="3"><h4><em>3</em>How to use it</h4><div class="body"><div class="cmd">'+F.call.replace(/</g,'&lt;')+'</div><div class="tags">'+F.needs.slice(0,3).map(n=>'<span>needs '+n+'</span>').join('')+'<span class="ok">nothing installed</span></div></div></div>';
const T0=4.3,TT=4.55,TR=5.6,S=[0,5.75,7.75,9.95],T1=11.2;   // sent, tool call, tool result, the three steps, done
// the clock shows the session's real seconds: the wait for the tool is sped up, the rest runs to the logged end
const realS=t=>t<T0?0:t<TR?D.t_res*(t-T0)/(TR-T0):Math.min(D.t_done,D.t_res+(D.t_done-D.t_res)*(t-TR)/(T1-TR));
const cur=t=>t>=S[3]?3:t>=S[2]?2:t>=S[1]?1:0;
function cc(t){
  let h='<div class="hd">✻ Claude Code <em>· skills: '+D.installed.length+' installed</em></div>';
  if(t>=T0){h+='<div class="me">&gt; <b>'+D.ask+'</b></div>';
    if(t>=TT){const run=t<TR;h+='<div class="tl"><span class="dot" style="background:'+(run?(Math.floor(t*4)%2?'#56657A':'#C9D5E6'):'#3FD1A2')+'"></span><b style="color:#fff">Bash</b>('+D.tool.replace(/</g,'&lt;')+')</div>'
      +'<div class="sub">⎿ '+(run?'Running… checking your skills, then GitHub':D.res_head+' <span style="color:#56657A">… +'+D.res_more+' lines</span>')+'</div>';}
    if(t>=S[1]){const c=cur(t);h+='<div class="ans">';D.lines.forEach((l,i)=>{if(t>=S[l[0]])h+='<div class="ln s'+l[0]+(l[1].startsWith('<b>'+l[0])?' h':'')+(c===l[0]?' on'+c:'')+'" style="opacity:'+(c===l[0]?1:0.38)*cl((t-S[l[0]])/0.2)+'">'+(i===0?'<span class="dot" style="background:#C9D5E6"></span>':'')+l[1]+'</div>'});h+='</div>';}}
  $('#cc').innerHTML=h;}
// scene 3
const M=D.med,xr=(a,b)=>(a/b).toFixed(1).replace('.0','')+'×';
const bars=(big,small,h,a,b,unit,id)=>'<div class="m" data-m="'+id+'"><div class="claim"><b>'+big+'</b><span>'+small+'</span></div><h4>'+h+'</h4><div class="br"><span>Without</span><div><i data-w="'+100*a/Math.max(a,b)+'" style="background:#F08A5D"></i></div><b>'+unit(a)+'</b></div><div class="br"><span>With</span><div><i data-w="'+100*b/Math.max(a,b)+'" style="background:#5B9FEA"></i></div><b>'+unit(b)+'</b></div></div>';
const nq=D.jobs[0].qa.length,qa=D.jobs.reduce((s,j)=>s+j.qa.filter(Boolean).length,0),qb=D.jobs.reduce((s,j)=>s+j.qb.filter(Boolean).length,0),qt=D.jobs.length*nq;
$('#t3').innerHTML='Without the plugin, and with it<small>same question · '+D.jobs.length+' jobs · middle value</small>';
$('#grid').innerHTML=bars(xr(M.tokA,M.tokB),'fewer tokens','TOKENS',M.tokA,M.tokB,fmt,0)+bars(xr(M.secA,M.secB),'faster','TIME TO AN ANSWER',M.secA,M.secB,v=>Math.round(v)+' s',1)
 +bars(Math.round(M.stB)+(Math.round(M.stB)===1?' step':' steps'),'instead of '+Math.round(M.stA),'STEPS',M.stA,M.stB,v=>Math.round(v),2);
$('#ql').innerHTML='<b>Same quality</b><span>checks passed: <b style="color:#5B9FEA">'+qb+' of '+qt+'</b> with the plugin · <b style="color:#F08A5D">'+qa+' of '+qt+'</b> without</span>';
// scene 4
const LA=[212,190,226,150,205,226,120,196,226,176,226,140,200,164,226,186],LB=[212,190,226,150,205,226,120,196];
$('#la').innerHTML=LA.map((w,i)=>'<u class="'+([3,9,14].includes(i)?'x':'')+'" data-n="'+i+'" style="width:'+w+'px"></u>').join('');
$('#lb').innerHTML=LB.map((w,i)=>'<u data-n="'+i+'" style="width:'+w+'px;background:#5B9FEA"></u>').join('');
const AR='<svg viewBox="0 0 20 20"><path d="M3 10h13M11 5l5 5-5 5" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>';
$('#flow').innerHTML='<div><em>1</em>What you have</div>'+AR+'<div><em>2</em>The best on GitHub</div>'+AR+'<div><em>3</em>How to use it</div>';$('#endp').textContent='Which skill to use, and how. Short answers, too.';
const A=3.0,B=12.6,Cc=17.6,E=21.2,fade=(t,a,b)=>Math.min(cl((t-a)/0.35),cl((b-t)/0.35));
window.setT=function(t){
  $('#s1').hidden=t>=A;$('#s1').style.opacity=cl((A-t)/0.35);
  $$('#chips .chip').forEach(e=>{const a=0.1+0.03*(+e.dataset.i);e.style.opacity=cl((t-a)/0.15)*(t>1.05?1-0.72*cl((t-1.05)/0.3):1);e.style.transform='scale('+(0.7+0.3*ease((t-a)/0.25))+')'});
  $$('.q').forEach(e=>{const a=1.15+0.3*(+e.dataset.q);e.style.opacity=cl((t-a)/0.2);e.style.transform='translateY('+(1-ease((t-a)/0.3))*14+'px) scale('+(0.9+0.1*ease((t-a)/0.3))+')'});
  $('#s2').hidden=t<A||t>=B;$('#s2').style.opacity=fade(t,A,B);
  const k=cl((t-A-0.2)/0.95);$('#typed').textContent=t<T0?D.ask.slice(0,Math.round(D.ask.length*k)):'';$('#caret').hidden=t>=T0&&Math.floor(t*2)%2===1;
  cc(t);$('#clock').hidden=t<T0;$('#clock').textContent=(t>=T1?'done in ':t<TR?'» ':'')+Math.round(realS(t))+' s'+(t>=T1?' · '+fmt(D.tokens)+' tokens':'');
  $$('.st').forEach(e=>{const s=+e.dataset.s,a=S[s],on=cl((t-a)/0.25),act=cur(t)===s;e.style.borderColor=act?(s===3?'#3FD1A2':'#5B9FEA'):'#28364A';e.querySelector('.body').style.opacity=on;e.style.opacity=on<=0?0.32:(act?1:0.5);e.style.transform='scale('+(act?1.025:1)+')';
    e.querySelector('h4 em').style.background=on>0.5?(s===3?'#3FD1A2':'#5B9FEA'):'#28364A';e.querySelector('h4 em').style.color=on>0.5?'#0B111B':'#94A3B8';
    e.querySelectorAll('.dots i').forEach(d=>{const i=+d.dataset.d,b=a+0.02*i;d.style.background=(t>b+0.35&&i===D.installed.indexOf(D.f.pick))?'#5B9FEA':(t>b?'#3A4A61':'#28364A')});
    e.querySelectorAll('.sb i').forEach((b,i)=>b.style.width=(+b.dataset.w)*ease((t-a-0.1-0.07*i)/0.45)+'%')});
  $('#s3').hidden=t<B||t>=Cc;$('#s3').style.opacity=fade(t,B,Cc);
  $$('#grid .m').forEach(e=>{const a=B+0.25+0.85*(+e.dataset.m);e.style.opacity=cl((t-a)/0.2);e.style.transform='translateY('+(1-ease((t-a)/0.3))*12+'px)';e.querySelectorAll('.br i').forEach(i=>i.style.width=(+i.dataset.w)*ease((t-a-0.1)/0.5)+'%')});
  $('#ql').style.opacity=cl((t-B-2.9)/0.25);
  $('#s4').hidden=t<Cc||t>=E;$('#s4').style.opacity=fade(t,Cc,E);
  $$('#la u').forEach(e=>e.style.opacity=cl((t-Cc-0.2-0.02*(+e.dataset.n))/0.1));$$('#lb u').forEach(e=>e.style.opacity=cl((t-Cc-0.2-0.02*(+e.dataset.n))/0.1));
  $$('.fact').forEach(e=>{const a=Cc+0.7+0.8*(+e.dataset.f);e.style.opacity=cl((t-a)/0.3);e.style.transform='translateX('+(1-ease((t-a)/0.35))*16+'px)'});
  $('#s5').hidden=t<E;$('#s5').style.opacity=cl((t-E)/0.35);
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
        for name, tt in (("a", 0.9), ("b", 2.4), ("c", 5.2), ("d", 6.6), ("e", 8.8), ("f", 11.6), ("g", 14.4), ("h", 16.9), ("i", 20.4)):
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
