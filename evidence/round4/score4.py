"""Round 4 scoring. Written before the runs. Reads raw/*.jsonl, checks named repos against the GitHub API."""
import json,os,re,subprocess,statistics as st
H=os.path.dirname(os.path.abspath(__file__))
JOBS={'deck':'pptx','model':'xlsx','pdf':'pdf','landing':'frontend-design','webtest':'webapp-testing'}
def gh(repo):
    r=subprocess.run(['gh','api','repos/'+repo,'--jq','.stargazers_count'],capture_output=True,text=True)
    return int(r.stdout) if r.returncode==0 and r.stdout.strip().isdigit() else None
EX={}
def exists(repo):
    if repo not in EX: EX[repo]=gh(repo)
    return EX[repo]
R={}
for key,right in JOBS.items():
    for arm in 'AB':
        f=f'{H}/raw/{key}-{arm}.jsonl'
        if not os.path.exists(f): continue
        ev=[json.loads(l) for l in open(f)]; res=[x['e'] for x in ev if x['e'].get('type')=='result'][-1]
        steps=[]; bad=False
        for x in ev:
            e=x['e']
            if e.get('type')=='assistant':
                for c in e['message'].get('content',[]):
                    if c.get('type')=='tool_use':
                        inp=json.dumps(c['input']); steps.append(dict(t=x['t'],tool=c['name'],what=(c['input'].get('query') or c['input'].get('url') or c['input'].get('command') or c['input'].get('file_path') or c['input'].get('skill') or c['input'].get('pattern') or '')[:140]))
                        if re.search(r'git clone|npx skills add|plugin install|pip install|npm i',inp): bad=True
        text=res.get('result') or ''; u=res.get('usage') or {}
        url_repos={m.lower().rstrip('.') for m in re.findall(r'github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)',text)}
        bare={m.lower() for m in re.findall(r'(?<![\w/.-])([A-Za-z0-9][A-Za-z0-9-]{1,38}/[A-Za-z0-9_.-]{2,60})(?![\w/])',text) if not re.search(r'\.(md|py|json|js|html|txt)$|^\d|skills/|/skills$',m)}
        real=sorted(r for r in url_repos|bare if exists(r) is not None)
        # invented = a github.com link that does not resolve, or a repo-shaped name in the first cell of a table row or list item that does not resolve
        first={m.lower() for m in re.findall(r'^\s*(?:\||[-*]|\d+\.)\s*\**`?([A-Za-z0-9][A-Za-z0-9-]{1,38}/[A-Za-z0-9_.-]{2,60})',text,re.M)}
        fake=sorted(r for r in url_repos|first if exists(r) is None and not re.search(r'\.(md|py|json|js|html|txt)$',r))
        num=r'\b\d{1,3}(?:[,.]\d{3})+\b|\b\d+(?:\.\d+)?\s?[kK]\b|\b\d{2,}\s*(?:stars|★|⭐)'
        lines=[l for l in text.split('\n') if any(r.split('/')[1] in l.lower() for r in real)]
        nxt=lambda l: text.split('\n')[text.split('\n').index(l)+1] if text.split('\n').index(l)+1<len(text.split('\n')) else ''
        with_stars=sum(1 for l in lines if re.search(num,l) or re.search(num,nxt(l)))
        with_meta=sum(1 for l in lines if re.search(r'MIT|Apache|BSD|GPL|licen[sc]e|20\d\d-\d\d|updated',l+' '+nxt(l)))
        q=[bool(re.search(r'(?<![\w-])'+re.escape(right)+r'(?![\w-])',text)), len(real)>=3, len(fake)==0 and len(real)>0, with_stars>=3, with_meta>=3, bool(re.search(r'recommend',text,re.I))]
        repos=sorted(url_repos|bare)
        R[f'{key}-{arm}']=dict(tokens=u.get('input_tokens',0)+u.get('cache_creation_input_tokens',0)+u.get('cache_read_input_tokens',0)+u.get('output_tokens',0),tok_out=u.get('output_tokens',0),
            cost=round(res.get('total_cost_usd',0),3),sec=round(ev[-1]['t'],1),steps=len(steps),turns=res.get('num_turns'),quality=q,score=sum(q),installed_run=bad,repos_real=real,repos_fake=fake,words=len(text.split()),step_list=steps)
S={}
for arm in 'AB':
    rs=[R[k] for k in R if k.endswith('-'+arm)]
    if rs: S[arm]={m:st.median(r[m] for r in rs) for m in ('tokens','sec','steps','cost','score')}
S['same_way']={m:sum(1 for k in JOBS if f'{k}-A' in R and f'{k}-B' in R and R[f'{k}-B'][m]<R[f'{k}-A'][m]) for m in ('tokens','sec','steps','cost')}
S['same_way']['score_B_ge_A']=sum(1 for k in JOBS if f'{k}-A' in R and f'{k}-B' in R and R[f'{k}-B']['score']>=R[f'{k}-A']['score'])
json.dump(dict(runs=R,summary=S),open(H+'/results.json','w'),indent=1)
for k,r in R.items(): print(k,{m:r[m] for m in ('tokens','sec','steps','cost','score','words')},r['quality'],'fake:',r['repos_fake'],'installed_run:',r['installed_run'])
print(json.dumps(S,indent=1))
