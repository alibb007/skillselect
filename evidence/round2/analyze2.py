"""Round 2 analysis against RULES2.md. Writes results.json."""
import json,re,os,math
H=os.path.dirname(os.path.abspath(__file__)); RS=json.load(open(H+'/requests.json'))
A=json.load(open(H+'/answers.json')); C=json.load(open(H+'/checks.json')); V=json.load(open(H+'/verdicts.json'))
def sign_p(a,b):
    n=a+b
    if n==0: return 1.0
    k=min(a,b); return min(1.0,2*sum(math.comb(n,i) for i in range(k+1))/2**n)
PH=re.compile(r'\[(?![xX ]\])[A-Za-z][^\]\n]{1,40}\](?!\()')
ids=[r['id'] for r in RS]; R={'n':len(ids)}
for arm in ('A','B','C','A2'):
    ks=[i+'-'+arm for i in ids if i+'-'+arm in A]
    marks=[m for k in ks for m in C.get(k,[])]
    R[arm]=dict(n=len(ks),checked=sum(1 for k in ks if k in C),details=len(marks),used=marks.count('used'),ignored=marks.count('ignored'),wrong=marks.count('wrong'),
                chars=round(sum(A[k]['chars'] for k in ks)/max(1,len(ks))),tok_out=round(sum((A[k]['tok_out'] or 0) for k in ks)/max(1,len(ks))),
                placeholders=sum(len(PH.findall(A[k]['text'])) for k in ks),answers_with_placeholder=sum(1 for k in ks if PH.search(A[k]['text'])))
def used(i,arm): return C.get(i+'-'+arm,[]).count('used') if i+'-'+arm in C else None
for x,y in (('A','B'),('B','C')):
    more=sum(1 for i in ids if used(i,x) is not None and used(i,y) is not None and used(i,y)>used(i,x)); less=sum(1 for i in ids if used(i,x) is not None and used(i,y) is not None and used(i,y)<used(i,x))
    R[f'details_{x}{y}']=dict(y_more=more,x_more=less,p=round(sign_p(more,less),4))
for x,y in (('A','B'),('B','C'),('A','A2')):
    vs=[V[i+f'-{x}v{y}'] for i in ids if i+f'-{x}v{y}' in V]
    wx=sum(1 for v in vs if v['winner']==x); wy=sum(1 for v in vs if v['winner']==y); t=len(vs)-wx-wy
    R[f'pairs_{x}{y}']={'n':len(vs),x:wx,y:wy,'tie':t,'p':round(sign_p(wx,wy),5),'split_orders':sum(1 for v in vs if v['votes'][0]!=v['votes'][1])}
a,b=R['A'],R['B']; ab=R['pairs_AB']; bc=R['pairs_BC']; n2=R['pairs_AA2']
pa=100*a['used']/max(1,a['details']); pb=100*b['used']/max(1,b['details']); noise=max(n2['A'],n2['A2'])/max(1,n2['A']+n2['A2'])
R['rules']=dict(
 R1=dict(A_pct=round(pa,1),B_pct=round(pb,1),diff=round(pb-pa,1),p=R['details_AB']['p'],passed=bool(pb-pa>=5 and R['details_AB']['p']<0.05)),
 R2=dict(B=ab['B'],A=ab['A'],tie=ab['tie'],p=ab['p'],B_share=round(ab['B']/max(1,ab['A']+ab['B']),3),noise_share=round(noise,3),passed=bool(ab['B']>ab['A'] and ab['p']<0.05 and ab['B']/max(1,ab['A']+ab['B'])>noise)),
 R3=dict(B=bc['B'],C=bc['C'],tie=bc['tie'],p=bc['p'],passed=bool(bc['B']>bc['C'] and bc['p']<0.05)),
 R4=dict(A_tok=a['tok_out'],B_tok=b['tok_out'],ratio=round(b['tok_out']/max(1,a['tok_out']),3),passed=bool(b['tok_out']<=1.10*a['tok_out'])))
json.dump(R,open(H+'/results.json','w'),indent=1); print(json.dumps(R,indent=1))
