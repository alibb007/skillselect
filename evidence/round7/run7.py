"""Round 7: which skills does plain Claude load when asked for the job itself?"""
import json,os,subprocess,sys,time
from concurrent.futures import ThreadPoolExecutor
H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.dirname(H)); import lab
SB='/tmp/straight-answer-round6'  # the round-6 test folder
BASE="Build a landing page for my product. It is Papertrail, a note-taking app for students, $4 a month."
ASK={'P':BASE+" Use whatever skills you have that help.",'Q':BASE}
def run(key):
    out=f'{H}/raw/{key}.jsonl'
    if os.path.exists(out) and '"type":"result"' in open(out).read().replace(' ',''): return
    lab.guard()
    if lab.spent()-START>5: lab.stop('round-7 cap reached')
    cmd=[lab.CL,'-p',ASK[key[0]],'--model','opus','--setting-sources','project','--max-turns','10','--no-session-persistence','--strict-mcp-config','--mcp-config',lab.L+'/nomcp.json','--output-format','stream-json','--verbose',
         '--allowedTools','Skill','Read','Glob','Grep','--disallowedTools','Write','Edit','NotebookEdit','Agent','Task','Artifact','Bash','WebSearch','WebFetch']
    t0=time.time(); p=subprocess.Popen(cmd,cwd=SB+'/proj',stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,stdin=subprocess.DEVNULL,text=True)
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
    if not res: lab.stop(f'r7 {key}: no result')
    models=list((res.get('modelUsage') or {}).keys())
    if not any('opus' in m for m in models) or 'session limit' in (res.get('result') or '')[:80]: lab.stop(f'r7 {key}: not Opus or limit: {models}')
    u=res.get('usage') or {}
    lab.log(dict(kind='v7_run',meta={'run':key},models=models,cost=res.get('total_cost_usd',0),sec=round(time.time()-t0,1),tok_in=u.get('input_tokens',0)+u.get('cache_creation_input_tokens',0)+u.get('cache_read_input_tokens',0),tok_out=u.get('output_tokens',0)))
    print(key,'done',round(time.time()-t0),'s $%.2f'%res.get('total_cost_usd',0),flush=True)
if __name__=='__main__':
    START=float(open(H+'/start.txt').read()) if os.path.exists(H+'/start.txt') else lab.spent(); open(H+'/start.txt','w').write(str(START))
    try:
        with ThreadPoolExecutor(3) as ex: list(ex.map(run,['P1','P2','P3','Q1','Q2','Q3']))
    except lab.Stop as e: print('STOPPED:',e)
    print('round-7 spend $%.2f'%(lab.spent()-START),'STOP' if lab.stopped() else 'no STOP')
