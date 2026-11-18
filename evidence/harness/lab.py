"""Shared helpers. Every model call must be answered by Opus; anything else writes STOP and raises."""
import json,os,subprocess,threading,time
L=os.path.dirname(os.path.abspath(__file__)); CL=os.path.expanduser('~/.local/bin/claude'); LOCK=threading.Lock(); CAP=150.0
DENY='Bash Edit Write NotebookEdit WebFetch WebSearch Agent Task Artifact ArtifactComments ArtifactData CronCreate CronDelete CronList DesignSync EnterWorktree ExitWorktree ListAgents Monitor PushNotification RemoteTrigger ReportFindings ScheduleWakeup SendMessage TaskStop ToolSearch Workflow'.split()
class Stop(Exception): pass
def stop(why):
    with LOCK: open(L+'/STOP','a').write(time.strftime('%Y-%m-%dT%H:%M:%S ')+why+'\n')
    raise Stop(why)
def stopped(): return os.path.exists(L+'/STOP')
def log(rec):
    rec['at']=time.strftime('%Y-%m-%dT%H:%M:%S')
    with LOCK: open(L+'/ledger.jsonl','a').write(json.dumps(rec,ensure_ascii=False)+'\n')
def spent():
    try: return sum(json.loads(l).get('cost',0) or 0 for l in open(L+'/ledger.jsonl'))
    except OSError: return 0.0
def guard():
    if stopped(): raise Stop('STOP file present')
    if spent()>CAP: stop(f'budget cap ${CAP} reached')
def bare(system,prompt,kind,meta=None,timeout=240):
    """One Opus call with no tools and its own system prompt. Returns the text."""
    guard()
    cmd=[CL,'-p',prompt,'--model','opus','--system-prompt',system,'--tools','','--setting-sources','project','--output-format','json','--no-session-persistence','--strict-mcp-config','--mcp-config',L+'/nomcp.json']
    t0=time.time(); p=subprocess.run(cmd,cwd=L+'/bare',capture_output=True,text=True,timeout=timeout,stdin=subprocess.DEVNULL)
    try: r=json.loads(p.stdout)
    except ValueError: stop(f'{kind}: no JSON from claude: {p.stdout[:120]!r} {p.stderr[:120]!r}')
    models=list((r.get('modelUsage') or {}).keys()); text=r.get('result') or ''
    if not models or not all(m.startswith('claude-opus') for m in models) or 'Not logged in' in text[:40]: stop(f'{kind}: not Opus or not logged in: models={models} text={text[:60]!r}')
    u=r.get('usage') or {}
    log(dict(kind=kind,meta=meta or {},models=models,cost=r.get('total_cost_usd',0),sec=round(time.time()-t0,1),tok_in=u.get('input_tokens',0)+u.get('cache_creation_input_tokens',0)+u.get('cache_read_input_tokens',0),tok_out=u.get('output_tokens',0)))
    return text
def jparse(text):
    a=min([i for i in (text.find('{'),text.find('[')) if i>=0],default=-1)
    if a<0: return None
    for b in range(len(text),a,-1):
        try: return json.loads(text[a:b])
        except ValueError: continue
