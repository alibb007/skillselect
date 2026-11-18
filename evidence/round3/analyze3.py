"""Round 3 analysis against RULES3.md. Writes results.json."""
import json,re,os,math,statistics as st
H=os.path.dirname(os.path.abspath(__file__)); RS=json.load(open(H+'/requests.json')); A=json.load(open(H+'/answers.json')); V=json.load(open(H+'/verdicts.json'))
def sign_p(a,b):
    n=a+b
    if n==0: return 1.0
    k=min(a,b); return min(1.0,2*sum(math.comb(n,i) for i in range(k+1))/2**n)
PH=re.compile(r'\[(?![xX ]\])[A-Za-z][^\]\n]{1,40}\](?!\()')
ids=[r['id'] for r in RS]; R={'n':len(ids)}
for arm in ('A','S','B'):
    ks=[i+'-'+arm for i in ids]
    R[arm]=dict(n=len(ks),words=round(st.mean(A[k]['words'] for k in ks)),words_median=st.median(A[k]['words'] for k in ks),chars=round(st.mean(A[k]['chars'] for k in ks)),tok_out=round(st.mean(A[k]['tok_out'] for k in ks)),
                placeholders=sum(len(PH.findall(A[k]['text'])) for k in ks),answers_with_placeholder=sum(1 for k in ks if PH.search(A[k]['text'])))
for x,y in (('S','A'),('S','B')):
    vs=[V[i+f'-{x}v{y}'] for i in ids]
    wx=sum(v['winner']==x for v in vs); wy=sum(v['winner']==y for v in vs)
    R[f'pairs_{x}{y}']={'n':len(vs),x:wx,y:wy,'tie':len(vs)-wx-wy,'p':round(sign_p(wx,wy),5)}
R['shorter_in']=sum(1 for i in ids if A[i+'-S']['words']<A[i+'-A']['words'])
a,s,b=R['A'],R['S'],R['B']; sa=R['pairs_SA']; sb=R['pairs_SB']
R['rules']=dict(
 T1=dict(S_words=s['words'],A_words=a['words'],ratio=round(s['words']/a['words'],3),passed=bool(s['words']<=0.70*a['words'])),
 T2=dict(S=sa['S'],A=sa['A'],tie=sa['tie'],p=sa['p'],passed=bool(sa['S']>sa['A'] and sa['p']<0.05)),
 T3=dict(S_tok=s['tok_out'],A_tok=a['tok_out'],ratio=round(s['tok_out']/a['tok_out'],3),passed=bool(s['tok_out']<a['tok_out'])),
 T4=dict(S=sb['S'],B=sb['B'],tie=sb['tie'],p=sb['p'],passed=bool(sb['S']>=sb['B'])))
json.dump(R,open(H+'/results.json','w'),indent=1); print(json.dumps(R,indent=1))
