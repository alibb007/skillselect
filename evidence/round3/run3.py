"""Round 3 runner. Usage: run3.py smoke | run3.py all. Cached in answers.json and verdicts.json."""
import json,os,sys,threading
from concurrent.futures import ThreadPoolExecutor
H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.dirname(H)); import lab
SHORT="Use my exact facts and numbers, and give me a short, finished answer I can use as it is, with no placeholders, no generic templates and nothing I did not ask for."
LONG="Use my exact facts and numbers, and give me a finished answer I can use as it is, with no placeholders or generic templates."
SYS="You are a helpful AI assistant."
CAP3=25.0; START=115.62; LK=threading.Lock()
def cap():
    if lab.spent()-START>CAP3: lab.stop(f'round-3 cap ${CAP3} reached')
def load(n):
    try: return json.load(open(f'{H}/{n}.json'))
    except OSError: return {}
def put(n,d,k,val):
    with LK:
        d[k]=val; tmp=f'{H}/{n}.json.tmp'; json.dump(d,open(tmp,'w'),indent=1,ensure_ascii=False); os.replace(tmp,f'{H}/{n}.json')
RS=json.load(open(H+'/requests.json')); ANS=load('answers'); VER=load('verdicts')
def prompt(r,arm): return r['prompt'].strip()+({'A':'','S':'\n\n'+SHORT,'B':'\n\n'+LONG}[arm])
def answer(job):
    r,arm=job; k=r['id']+'-'+arm
    if k in ANS: return
    cap(); meta={'id':r['id'],'arm':arm}
    txt=lab.bare(SYS,prompt(r,arm),'v3_answer',meta)
    tok=None
    for l in reversed(open(lab.L+'/ledger.jsonl').read().splitlines()[-400:]):
        d=json.loads(l)
        if d.get('kind')=='v3_answer' and d.get('meta')==meta: tok=d.get('tok_out'); break
    put('answers',ANS,k,dict(text=txt,chars=len(txt),words=len(txt.split()),tok_out=tok)); print('ans',k,len(txt.split()),'words',flush=True)
JS=("You are the person described below and you sent the message below to an AI assistant. Two assistants replied. Decide which reply serves you better: "
    "correct, useful for your exact situation, the right amount of detail, and it does what you asked. Judge only the words on the page. A longer reply is not better for being longer. "
    'Reply with JSON only: {"winner": "1" or "2" or "tie", "why": "<at most 14 words>"}')
def judge(job):
    r,x,y=job; k=r['id']+'-'+x+'v'+y
    if k in VER or r['id']+'-'+x not in ANS or r['id']+'-'+y not in ANS: return
    votes=[]
    for first,second in ((x,y),(y,x)):
        cap(); a1=ANS[r['id']+'-'+first]['text'][:20000]; a2=ANS[r['id']+'-'+second]['text'][:20000]
        j=lab.jparse(lab.bare(JS,f"WHO YOU ARE: {r['persona']}\n\nYOUR MESSAGE:\n{r['prompt']}\n\nREPLY 1:\n{a1}\n\nREPLY 2:\n{a2}",'v3_judge',{'id':r['id'],'pair':x+'v'+y,'first':first})) or {}
        w=str(j.get('winner','tie')).strip(); votes.append((first if w=='1' else second if w=='2' else 'tie',str(j.get('why',''))[:140]))
    put('verdicts',VER,k,dict(winner=votes[0][0] if votes[0][0]==votes[1][0] else 'tie',votes=[v[0] for v in votes],why=[v[1] for v in votes])); print('ver',k,VER[k]['winner'],flush=True)
def run(rs,workers=12):
    with ThreadPoolExecutor(workers) as ex: list(ex.map(answer,[(r,a) for r in rs for a in ('A','S','B')]))
    with ThreadPoolExecutor(workers) as ex: list(ex.map(judge,[(r,'S','A') for r in rs]+[(r,'S','B') for r in rs]))
if __name__=='__main__':
    try: run(RS[:2] if sys.argv[1]=='smoke' else RS)
    except lab.Stop as e: print('STOPPED:',e)
    print('answers',len(ANS),'verdicts',len(VER),'round-3 spend $%.2f'%(lab.spent()-START),'STOP' if lab.stopped() else 'no STOP')
