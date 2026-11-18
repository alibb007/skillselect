"""Round 2 runner. Usage: run2.py smoke | run2.py all. Results cached in answers.json, checks.json, verdicts.json."""
import json,os,sys,threading,re
from concurrent.futures import ThreadPoolExecutor
H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.dirname(H)); import lab
SENT="Use my exact facts and numbers, and give me a finished answer I can use as it is, with no placeholders or generic templates."
CTRL="Please think it through carefully and give me a thorough, detailed, high-quality answer that covers everything important."
SYS="You are a helpful AI assistant."
CAP2=55.0; START=82.40; LK=threading.Lock()
def cap():
    if lab.spent()-START>CAP2: lab.stop(f'round-2 cap ${CAP2} reached')
def load(n):
    try: return json.load(open(f'{H}/{n}.json'))
    except OSError: return {}
def put(n,d,k,val):
    # set and write under one lock: a dump while another thread adds a key crashed the first full run
    with LK:
        d[k]=val; tmp=f'{H}/{n}.json.tmp'; json.dump(d,open(tmp,'w'),indent=1,ensure_ascii=False); os.replace(tmp,f'{H}/{n}.json')
RS=json.load(open(H+'/requests.json')); ANS=load('answers'); CHK=load('checks'); VER=load('verdicts')
def prompt(r,arm): return r['prompt'].strip()+({'A':'','A2':'','B':'\n\n'+SENT,'C':'\n\n'+CTRL}[arm])
def answer(job):
    r,arm=job; k=r['id']+'-'+arm
    if k in ANS: return
    cap(); n0=sum(1 for _ in open(lab.L+'/ledger.jsonl'))
    txt=lab.bare(SYS,prompt(r,arm),'v2_answer',{'id':r['id'],'arm':arm})
    tok=None
    for l in reversed(open(lab.L+'/ledger.jsonl').read().splitlines()[n0:]):
        d=json.loads(l)
        if d.get('kind')=='v2_answer' and d.get('meta')=={'id':r['id'],'arm':arm}: tok=d.get('tok_out'); break
    put('answers',ANS,k,dict(text=txt,chars=len(txt),tok_out=tok)); print('ans',k,len(txt),flush=True)
CK=("You check one AI reply against the details a person gave in their message. For each numbered detail decide: "
    '"used" = the reply clearly takes this detail into account and respects it; "ignored" = the reply does not use it or stays generic about it; '
    '"wrong" = the reply contradicts it or gets it wrong. Judge only the words on the page. '
    'Reply with JSON only: {"marks": ["used"|"ignored"|"wrong", ...]} with one mark per detail, in order.')
def check(job):
    r,arm=job; k=r['id']+'-'+arm
    if k in CHK or k not in ANS: return
    cap(); ds='\n'.join(f'{i+1}. {d}' for i,d in enumerate(r['details']))
    j=lab.jparse(lab.bare(CK,f"THE PERSON'S MESSAGE:\n{r['prompt']}\n\nDETAILS TO CHECK:\n{ds}\n\nTHE REPLY:\n{ANS[k]['text'][:20000]}",'v2_check',{'id':r['id']})) or {}
    m=[str(x).lower() for x in (j.get('marks') or [])][:4]
    if len(m)==4 and all(x in('used','ignored','wrong') for x in m): put('checks',CHK,k,m); print('chk',k,m,flush=True)
    else: print('chk BAD',k,j,flush=True)
JS=("You are the person described below and you sent the message below to an AI assistant. Two assistants replied. Decide which reply serves you better: "
    "correct, useful for your exact situation, the right amount of detail, and it does what you asked. Judge only the words on the page. A longer reply is not better for being longer. "
    'Reply with JSON only: {"winner": "1" or "2" or "tie", "why": "<at most 14 words>"}')
def judge(job):
    r,x,y=job; k=r['id']+'-'+x+'v'+y
    if k in VER or r['id']+'-'+x not in ANS or r['id']+'-'+y not in ANS: return
    votes=[]
    for first,second in ((x,y),(y,x)):
        cap(); a1=ANS[r['id']+'-'+first]['text'][:20000]; a2=ANS[r['id']+'-'+second]['text'][:20000]
        j=lab.jparse(lab.bare(JS,f"WHO YOU ARE: {r['persona']}\n\nYOUR MESSAGE:\n{r['prompt']}\n\nREPLY 1:\n{a1}\n\nREPLY 2:\n{a2}",'v2_judge',{'id':r['id'],'pair':x+'v'+y,'first':first})) or {}
        w=str(j.get('winner','tie')).strip(); votes.append((first if w=='1' else second if w=='2' else 'tie',str(j.get('why',''))[:140]))
    put('verdicts',VER,k,dict(winner=votes[0][0] if votes[0][0]==votes[1][0] else 'tie',votes=[v[0] for v in votes],why=[v[1] for v in votes])); print('ver',k,VER[k]['winner'],flush=True)
def run(rs,workers=14):
    aj=[(r,a) for r in rs for a in ('A','B','C')]+[(r,'A2') for r in rs if int(r['id'][1:])<=20]
    with ThreadPoolExecutor(workers) as ex: list(ex.map(answer,aj))
    with ThreadPoolExecutor(workers) as ex: list(ex.map(check,aj))
    jj=[(r,'A','B') for r in rs]+[(r,'B','C') for r in rs]+[(r,'A','A2') for r in rs if int(r['id'][1:])<=20]
    with ThreadPoolExecutor(workers) as ex: list(ex.map(judge,jj))
if __name__=='__main__':
    try:
        run(RS[:1] if sys.argv[1]=='smoke' else RS)
    except lab.Stop as e: print('STOPPED:',e)
    print('answers',len(ANS),'checks',len(CHK),'verdicts',len(VER),'round-2 spend $%.2f'%(lab.spent()-START),'STOP' if lab.stopped() else 'no STOP')
