"""Round 4: same goal with and without the plugin. Logs every stream line with its arrival time."""
import json,os,subprocess,sys,time,shutil
from concurrent.futures import ThreadPoolExecutor
H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.dirname(H)); import lab
SB='/tmp/straight-answer-round4'; PLUG=os.path.join(H,'..','..'); SRC=os.environ['PUBLIC_SKILLS_DIR']  # a clone of anthropics/skills, folder skills/
JOBS=[('deck','turn my quarterly sales numbers into a slide deck','pptx'),('model','build a financial model in a spreadsheet','xlsx'),('pdf','fill in and merge PDF forms','pdf'),
      ('landing','design a landing page for my product','frontend-design'),('webtest','test my web app in the browser','webapp-testing')]
ASK="I want to {job}. Which skill should I use? Tell me which of my installed skills fit, what else is available on GitHub (with stars, license and last update), and recommend one. Do not install anything."
def setup():
    if os.path.isdir(SB+'/proj/.claude/skills'): return
    os.makedirs(SB+'/proj/.claude',exist_ok=True); shutil.copytree(SRC,SB+'/proj/.claude/skills')
    json.dump({"claudeMdExcludes":[os.path.expanduser("~/.claude/CLAUDE.md"),"**/.claude/CLAUDE.md"]},open(SB+'/proj/.claude/settings.json','w'))
def run(job):
    key,need,_=job[0],job[1],job[2]; arm=job[3]; out=f'{H}/raw/{key}-{arm}.jsonl'
    if os.path.exists(out) and '"type":"result"' in open(out).read().replace(' ',''): return
    lab.guard()
    if lab.spent()-START>18: lab.stop('round-4 cap reached')
    common=['--model','opus','--setting-sources','project','--max-turns','40','--no-session-persistence','--strict-mcp-config','--mcp-config',lab.L+'/nomcp.json','--output-format','stream-json','--verbose',
            '--disallowedTools','Write','Edit','NotebookEdit','Agent','Task','Artifact']
    if arm=='A': cmd=[lab.CL,'-p',ASK.format(job=need)]+common+['--allowedTools','WebSearch','WebFetch','Bash(gh:*)','Bash(ls:*)','Bash(cat:*)','Bash(head:*)','Bash(curl:*)','Read','Glob','Grep','Skill']
    else: cmd=[lab.CL,'-p','/straight-answer:find-skill '+need,'--plugin-dir',PLUG]+common+['--allowedTools','Skill','Bash(python3:*)','Read']
    env=dict(os.environ,SKILL_FINDER_ONLY=SB+'/proj/.claude/skills',SKILL_FINDER_CACHE=f'{SB}/cache-{key}')
    t0=time.time(); p=subprocess.Popen(cmd,cwd=SB+'/proj',stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,stdin=subprocess.DEVNULL,text=True,env=env)
    res=None
    with open(out,'w') as f:
        for line in p.stdout:
            line=line.strip()
            if not line: continue
            try: d=json.loads(line)
            except ValueError: continue
            f.write(json.dumps({'t':round(time.time()-t0,2),'e':d},ensure_ascii=False)+'\n')
            if d.get('type')=='result': res=d
    p.wait()
    if not res: lab.stop(f'r4 {key}-{arm}: no result')
    models=list((res.get('modelUsage') or {}).keys()); main=[m for m in models if 'opus' in m]
    if not main or 'Not logged in' in (res.get('result') or '')[:40] or 'session limit' in (res.get('result') or '')[:80]: lab.stop(f'r4 {key}-{arm}: not Opus or limit: {models} {(res.get("result") or "")[:80]!r}')
    u=res.get('usage') or {}
    lab.log(dict(kind='v4_run',meta={'job':key,'arm':arm},models=models,cost=res.get('total_cost_usd',0),sec=round(time.time()-t0,1),tok_in=u.get('input_tokens',0)+u.get('cache_creation_input_tokens',0)+u.get('cache_read_input_tokens',0),tok_out=u.get('output_tokens',0)))
    print(key,arm,'done',round(time.time()-t0),'s $%.2f'%res.get('total_cost_usd',0),flush=True)
if __name__=='__main__':
    setup(); START=float(open(H+'/start.txt').read()) if os.path.exists(H+'/start.txt') else lab.spent(); open(H+'/start.txt','w').write(str(START))
    jobs=JOBS[:1] if sys.argv[1]=='smoke' else JOBS
    try:
        with ThreadPoolExecutor(3) as ex: list(ex.map(run,[j+('A',) for j in jobs]))
        for j in jobs:
            run(j+("B",)); time.sleep(45 if len(jobs)>1 else 0)
    except lab.Stop as e: print('STOPPED:',e)
    print('round-4 spend $%.2f'%(lab.spent()-START),'STOP' if lab.stopped() else 'no STOP')
