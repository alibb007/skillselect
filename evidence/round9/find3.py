"""Matcher 3 (lab copy, standard library only). Reuses the 2.2.0 finder's reading and GitHub code; changes how skills are matched and ordered.
- word pairs count as terms ("landing page" is one term next to "landing" and "page")
- close words (other names, file types) count half
- BM25 with the textbook constants
- GitHub order: reciprocal rank fusion of fit rank and stars rank
No word list and no job name lives in this file."""
import math, os, sys, time, urllib.parse
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.expanduser('~/skillselect-2.2.0/skills/find-skill/scripts'))  # a checkout of this repo at commit e70f08b (plugin 2.2.0)
import find_skills as F
K1, B, RRF_K, ALSO_W = 1.5, 0.75, 60, 0.5


SUF = ("ations", "ation", "ments", "ment", "ings", "ing", "ers", "er", "ed", "es", "s")


def stem(w):
    for suf in SUF:  # longest ending first; at least 4 letters stay
        if w.endswith(suf) and len(w) - len(suf) >= 4:
            w = w[: -len(suf)]; break
    return w[:-1] if len(w) > 4 and w.endswith("e") else w  # slide / slides, write / writing


def toks(s):
    return [stem(w) for w in F.words(s)]


def terms(s):
    w = toks(s)
    return w + [a + "_" + b for a, b in zip(w, w[1:])]


def query(topic, also=""):
    t = toks(topic); core = list(dict.fromkeys(t))
    pairs = list(dict.fromkeys(a + "_" + b for a, b in zip(t, t[1:])))
    extra = [x for x in dict.fromkeys(toks(also)) if x not in core]
    w = {x: 1.0 for x in core}; w.update({p: 1.0 for p in pairs}); w.update({x: ALSO_W for x in extra})
    return core, extra, w


def bm25(docs, w):
    N = len(docs)
    if not N:
        return []
    avg = sum(map(len, docs)) / N or 1
    df = {t: sum(1 for d in docs if t in d) for t in w}
    out = []
    for d in docs:
        s = 0.0
        for t, wt in w.items():
            tf = d.count(t)
            if tf:
                s += wt * math.log(1 + (N - df[t] + 0.5) / (df[t] + 0.5)) * tf * (K1 + 1) / (tf + K1 * (1 - B + B * len(d) / avg))
        out.append(s)
    return out


def hit(d, core, extra):
    ds = set(d); c = [t for t in core if t in ds]; e = [t for t in extra if t in ds]
    return c, e, (len(c) + ALSO_W * len(e) >= min(1.5, len(core) + ALSO_W * len(extra)))  # two topic words, or one topic word + one close word, or three close words


def rank_local3(topic, also, skills, k=8):
    core, extra, w = query(topic, also)
    if not core or not skills:
        return []
    docs = [terms(s["name"]) * 3 + terms(s["desc"]) for s in skills]
    res = []
    for s, d, x in zip(skills, docs, bm25(docs, w)):
        c, e, ok = hit(d, core, extra)
        if ok:
            res.append((x, s, len(c) + len(e)))
    res.sort(key=lambda r: -r[0])
    names, out = set(), []
    for x, s, h in res:
        if s["name"] not in names:
            names.add(s["name"]); out.append(dict(s, fit=round(x, 3), matched=h))
    return out[:k]


def pool_github3(topic, also, tok, have=()):
    """Every GitHub skill read that passes the match rule, with its fit score and stars. Ordering is done by order()."""
    kw = list(dict.fromkeys(F.words(topic)))[:4]
    al = [x for x in dict.fromkeys(F.words(also)) if x not in kw][:3]
    core, extra, w = query(topic, also); q = core + extra
    if not kw:
        return [], []
    notes, cand = [], {}
    two = ("skill in:name,description,readme", "topic:agent-skills")
    kk = kw[:4] if tok else kw[:3]
    queries = [(kw, e) for e in two]
    if len(kw) > 2:
        queries += [([kk[i], kk[j]], two[0]) for i in range(len(kk)) for j in range(i + 1, len(kk))]
    queries += [([a], two[0]) for a in al]  # each close word by itself: finds skills named after a file type or another name
    queries += [(["topic:" + t], "") for t in ("agent-skills", "claude-skills")]
    limited = []

    def one(qq):
        tm, extra_q = qq
        n = 12 if not extra_q else 20
        try:
            return F.get("https://api.github.com/search/repositories?q=" + urllib.parse.quote((" ".join(tm) + " " + extra_q).strip()) + f"&sort=stars&order=desc&per_page={n}", tok).get("items", [])
        except F.Limit:
            limited.append(1); return []

    with ThreadPoolExecutor(3 if tok else 2) as ex:
        found = list(ex.map(one, queries))
    big = {}
    for (tm, extra_q), items in zip(queries, found):
        for it in items:
            (big if not extra_q else cand).setdefault(it["full_name"], it)
    scored = []
    for it in cand.values():
        topics = set(t.lower() for t in it.get("topics") or [])
        text = " ".join([it["name"], it.get("description") or "", " ".join(topics)])
        if not (topics & F.SKILL_TOPICS or "skill" in text.lower()):
            continue
        tt = toks(text)
        scored.append((sum(1 for t in q if t in tt), it["stargazers_count"], it))
    scored = sorted([x for x in scored if x[0] >= 1], key=lambda x: -x[1])
    n_c, n_big = (14, 12) if tok else (8, 6)
    big = sorted(big.values(), key=lambda it: -it["stargazers_count"])[:n_big]
    todo = scored[:n_c] + [x for x in scored[n_c:] if x[0] >= min(2, len(q))][: n_c // 2 + 1]
    todo += [(0, it["stargazers_count"], it) for it in big if it["full_name"] not in {x[2]["full_name"] for x in todo}]

    def repo(job):
        rel, stars, it = job
        out = []
        try:
            tree = F.get(f"https://api.github.com/repos/{it['full_name']}/git/trees/{urllib.parse.quote(it['default_branch'])}?recursive=1", tok)
        except ValueError:
            return out
        paths = [p["path"] for p in tree.get("tree", []) if p["path"] == "SKILL.md" or p["path"].endswith("/SKILL.md")]
        if not paths:
            return out
        best = sorted(paths, key=lambda p: (-sum(1 for t in q if t in toks(os.path.dirname(p) or it["name"])), len(p)))[:8]
        if rel == 0 and not any(t in toks(os.path.dirname(best[0]) or it["name"]) for t in q):
            return out
        for p in best:
            raw = F.get(f"https://raw.githubusercontent.com/{it['full_name']}/{urllib.parse.quote(it['default_branch'])}/{urllib.parse.quote(p)}", None, raw=True)
            name, desc = F.front(raw[:8000]); folder = os.path.dirname(p)
            skill = name or os.path.basename(folder) or it["name"]
            out.append(dict(skill=skill, repo=it["full_name"], stars=stars, desc=desc or (it.get("description") or ""), folder=folder,
                            doc=terms(" ".join([name, os.path.basename(folder) or it["name"]])) * 3 + terms(desc),
                            license=(it.get("license") or {}).get("spdx_id") or "none", updated=(it.get("pushed_at") or "")[:10], archived=bool(it.get("archived")),
                            url=f"https://github.com/{it['full_name']}" + (f"/tree/{it['default_branch']}/{folder}" if folder else "")))
        return out

    with ThreadPoolExecutor(8 if tok else 3) as ex:
        read = [o for part in ex.map(repo, todo) for o in part]
    fits = bm25([o["doc"] for o in read], w)
    pool, owned, seen = [], set(), set()
    for o, x in zip(read, fits):
        c, e, ok = hit(o["doc"], core, extra)
        if not ok or (o["repo"], o["skill"]) in seen:
            continue
        seen.add((o["repo"], o["skill"]))
        if o["skill"].lower() in have:
            owned.add(o["skill"]); continue
        pool.append(dict({k: v for k, v in o.items() if k != "doc"}, fit=round(x, 3), matched=len(c) + len(e)))
    if sum(1 for o in pool if o["stars"] >= 10) >= 3:  # same rule as 2.2.0: drop near-unknown repos when there is enough choice
        pool = [o for o in pool if o["stars"] >= 10]
    if limited:
        notes.append(f"GitHub turned away {len(limited)} of {len(queries)} searches.")
    if owned:
        notes.append(f"{len(owned)} GitHub skills left out because you already have a skill of that name.")
    notes.append(f"{len(cand) + len(big)} repositories looked at, {len(read)} skill folders read, {len(pool)} pass the match rule.")
    return pool, notes


def order(pool, how="rrf", limit=12, per_repo=2):
    """how: 'rrf' (fit rank fused with stars rank), 'fit', or 'stars'."""
    by_fit = sorted(pool, key=lambda o: -o["fit"]); star_vals = sorted({o["stars"] for o in pool}, reverse=True)
    rf = {id(o): i + 1 for i, o in enumerate(by_fit)}; rs = {id(o): star_vals.index(o["stars"]) + 1 for o in pool}
    key = {"rrf": lambda o: -(1 / (RRF_K + rf[id(o)]) + 1 / (RRF_K + rs[id(o)])), "fit": lambda o: rf[id(o)], "stars": lambda o: (rs[id(o)], rf[id(o)])}[how]
    out, n = [], {}
    for o in sorted(pool, key=key):
        if n.get(o["repo"], 0) < per_repo:
            n[o["repo"]] = n.get(o["repo"], 0) + 1; out.append(o)
    return out[:limit]
