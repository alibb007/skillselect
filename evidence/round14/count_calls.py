"""How many GitHub API calls does one request cost a person with NO GitHub login?
The finder runs its no-login path (token = None). To count without being cut off by the 60-an-hour limit, the wrapper adds a login
to each call behind the finder's back: the finder still decides as if it had none. One cache is kept across the 8 requests, as on a real computer."""
import hashlib, importlib.util, json, os, shutil, sys, time
finder, label, cache = sys.argv[1], sys.argv[2], sys.argv[3]
shutil.rmtree(cache, ignore_errors=True); os.environ['SKILL_FINDER_CACHE'] = cache; os.environ['SKILL_FINDER_ONLY'] = '/nonexistent'
sp = importlib.util.spec_from_file_location('f_' + label, finder); F = importlib.util.module_from_spec(sp); sp.loader.exec_module(F)
TOK = F.token(True); real = F.get; n = {'search': 0, 'core': 0}
def get(url, tok, raw=False):
    if 'api.github.com' in url:
        cf = os.path.join(F.CACHE, hashlib.sha1(url.encode()).hexdigest() + '.json')
        if not (os.path.exists(cf) and time.time() - os.path.getmtime(cf) < 86400):
            n['search' if '/search/' in url else 'core'] += 1
        return real(url, TOK, raw)
    return real(url, tok, raw)
F.get = get
ASKS = [("landing page", "website web html hero marketing conversion"), ("slide deck", "presentation pptx powerpoint slides"), ("code review", "pull request pr diff"), ("meeting notes", "summary transcript minutes agenda"),
        ("spreadsheet excel analysis", "xlsx csv data pivot formula"), ("word document", "docx doc report headings table"), ("unit tests", "pytest jest testing coverage"), ("database migration", "sql schema postgres migrate")]
rows = []
for t, a in ASKS:
    n['search'] = n['core'] = 0; t0 = time.time()
    res, notes, counts = F.search_github(t, a, None, 12, set())
    rows.append(dict(topic=t, searches=n['search'], core=n['core'], listed=len(res), from_list=sum(1 for o in res if o.get('src') == 'list'), sec=round(time.time() - t0, 1)))
    print(label, rows[-1], flush=True); time.sleep(20)
core = [r['core'] for r in rows]
print(label, 'core calls per request: first', core[0], '| mean', round(sum(core) / len(core), 1), '| max', max(core), '| requests an hour on 60 calls (mean):', int(60 // (sum(core) / len(core))) if sum(core) else 'no limit')
json.dump(rows, open(os.path.join(os.path.dirname(cache), f'calls_{label}.json'), 'w'), indent=1)
