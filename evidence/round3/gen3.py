"""Round 3: Opus writes 42 new requests (6 areas x 7), 4 details each, none like round 2."""
import json,os,sys
from concurrent.futures import ThreadPoolExecutor
H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.dirname(H)); import lab
OLD=json.load(open(H+'/../v2/requests.json'))
AREAS=["office work: reports, emails to a boss or client, meeting plans, hiring, schedules","running a small shop, cafe, trade or freelance business: prices, staff rotas, customer messages, stock","home and family: moving, renovation, meals for the week, childcare schedules, a family event","personal money and travel: a monthly budget, a trip plan, comparing two offers, paying off a debt","study and teaching: a study timetable, a lesson plan, a thesis or exam plan, a course choice","health habits, sport, hobbies and volunteering: a training plan, a club event, a garden, a fundraiser"]
WR=("You write realistic test messages for an AI assistant. Write 7 messages from 7 different people (different ages, jobs and countries) in this area: {area}. "
    "Each person asks for something they will use directly: a plan, a schedule, a message to send, a calculation, a checklist or a decision. "
    "Each message is 2 to 5 sentences in the person's own everyday words and carries exactly 4 concrete details of their own situation that a good answer has to use "
    "(numbers, amounts, dates, limits, names, what they have or cannot do). The message must be answerable in text with no file or link. "
    "Do not reuse any of these people or situations: {old}. "
    'Reply with JSON only: [{{"persona": "<who, 3-8 words>", "message": "...", "details": ["<detail 1 as a short fact>", "<detail 2>", "<detail 3>", "<detail 4>"]}}, ...]')
def batch(i):
    old='; '.join(r['persona'] for r in OLD if r['area']==i)
    j=lab.jparse(lab.bare(WR.format(area=AREAS[i],old=old),'Write the 7 messages now.','v3_write',{'area':i},timeout=400)) or []
    return [dict(area=i,persona=x.get('persona',''),prompt=x.get('message',''),details=[str(d) for d in x.get('details',[])][:4]) for x in j if x.get('message') and len(x.get('details',[]))>=4][:7]
out=H+'/requests.json'
if os.path.exists(out): print('requests.json exists, not rewriting'); sys.exit()
with ThreadPoolExecutor(3) as ex: bs=list(ex.map(batch,range(6)))
rs=[b[k] for k in range(7) for b in bs if len(b)>k]
for n,r in enumerate(rs,1): r['id']=f'S{n:02d}'
json.dump(rs,open(out,'w'),indent=1,ensure_ascii=False); print('requests',len(rs),[len(b) for b in bs],'spent $%.2f'%lab.spent())
