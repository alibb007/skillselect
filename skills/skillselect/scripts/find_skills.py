#!/usr/bin/env python3
"""find_skills.py "<topic words>" [--also "<close words>"] [--json] [--no-online] [--no-token]
find_skills.py --mine [--json]       every skill on this computer, with its command and what it is for

1. Scores the skills already on this computer against the topic. Nothing about them leaves the machine.
2. Searches public GitHub, reads the skill files it finds, and orders them by fit and stars together.
3. Prints both lists with how to call each skill, what it needs, and for a GitHub skill the command to add it.
The assistant then keeps the skills that do the job. This script never installs, clones or downloads a skill.
The only thing sent out is the search words, to api.github.com. Python 3 standard library only.

Matching: stems and word pairs, close words at half weight, BM25 (k1 1.5, b 0.75, name counted 3 times),
GitHub order = reciprocal rank fusion of the fit rank and the stars rank (k 60). No word list lives in this file."""
import hashlib, json, math, os, re, subprocess, sys, time, urllib.error, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

STOP = set("a an and are as at be but by for from has have i if in into is it its me my of on or so that the then this to use used using was what when where which who why will with you your "
           "want need create make making build new one some any please help can could would like get do does how find skill skills tool plugin before after first then sign just really good best".split())
SKILL_TOPICS = {"claude-skills", "agent-skills", "claude-code-skills", "claude-skill", "agent-skill", "skills", "claude-code", "codex-skills", "ai-skills", "anthropic-skills"}
CACHE = os.environ.get("SKILL_FINDER_CACHE") or os.path.expanduser("~/.cache/skill-finder")


K1, B, RRF_K, ALSO_W = 1.5, 0.75, 60, 0.5
SUF = ("ations", "ation", "ments", "ment", "ings", "ing", "ers", "er", "ed", "es", "s")


def words(s):
    return [w for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in STOP and len(w) > 1]


def stem(w):
    for suf in SUF:  # longest ending first; at least 4 letters stay
        if w.endswith(suf) and len(w) - len(suf) >= 4:
            w = w[: -len(suf)]; break
    return w[:-1] if len(w) > 4 and w.endswith("e") else w  # slide / slides, write / writing


def toks(s):
    return [stem(w) for w in words(s)]


def terms(s):
    """Stems plus adjacent pairs, so "landing page" is a term of its own."""
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


def gate(d, core, extra):
    """A skill is a candidate with two topic words, or one topic word and one close word, or three close words."""
    ds = set(d); c = [t for t in core if t in ds]; e = [t for t in extra if t in ds]
    return len(c) + len(e), (len(c) + ALSO_W * len(e) >= min(1.5, len(core) + ALSO_W * len(extra)))


def front(text):
    m = re.match(r"---\s*\n(.*?)\n---", text, re.S)
    fm = m.group(1) if m else ""
    n = re.search(r"^name:\s*(.+)$", fm, re.M)
    d = re.search(r"^description:\s*(.*?)(?=\n[A-Za-z_-]+:|\Z)", fm, re.S | re.M)
    desc = re.sub(r"\s+", " ", d.group(1)).strip().strip("\"'>|") if d else ""
    return (n.group(1).strip().strip("\"'") if n else ""), desc.strip()


def split_fm(text):
    m = re.match(r"---\s*\n(.*?)\n---\s*\n?(.*)", text, re.S)
    return (m.group(1), m.group(2)) if m else ("", text)


def field(fm, k):
    m = re.search(rf"^{k}:\s*(.+)$", fm, re.M)
    return m.group(1).strip().strip("\"'") if m else ""


def pkgs(body, pat, ok=r"@?[A-Za-z0-9][A-Za-z0-9_.\-/\[\]]*"):
    out = []
    for line in re.findall(pat, body):
        for w in line.replace('"', " ").replace("'", " ").split():
            w = w.strip("`,.;)(")
            if w.startswith("-") or w.endswith((".txt", ".toml", ".json")) or w in (".", "install") or not re.fullmatch(ok, w):
                continue
            if w not in out:
                out.append(w)
    return out[:6]


def howto(text, name, plugin=""):
    """How to use one skill, read from its own SKILL.md. Nothing is guessed: a line is left out when the file does not say."""
    fm, body = split_fm(text)
    prose = re.sub(r"```.*?```", "", body, flags=re.S)
    hint = field(fm, "argument-hint")
    h = dict(call="/" + (plugin + ":" if plugin else "") + name + " " + (hint or "<what you want>"),
             by_name=field(fm, "user-invocable").lower() != "false", auto=field(fm, "disable-model-invocation").lower() != "true")
    need = []
    for label, pat in (("pip", r"(?:pip3?|uv pip) install\s+([^\n`&|;#]+)"), ("npm", r"npm (?:install|i)\s+([^\n`&|;#]+)"), ("brew", r"brew install\s+([^\n`&|;#]+)")):
        got = pkgs(body, pat)
        if got:
            need.append(label + ": " + ", ".join(got))
    npx = list(dict.fromkeys(re.findall(r"npx\s+(?:-y\s+|--yes\s+)?(@?[A-Za-z0-9][A-Za-z0-9_.\-/]*)", body)))[:4]
    if npx:
        need.append("npx: " + ", ".join(npx))
    keys = list(dict.fromkeys(re.findall(r"\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*_(?:API_KEY|TOKEN|SECRET)\b", body)))[:4]
    if keys:
        need.append("keys: " + ", ".join(keys))
    h["needs"] = need
    heads = [re.sub(r"[`*_]", "", x).strip() for x in re.findall(r"^#{2,3}\s+(.+?)\s*#*$", prose, re.M)]
    h["covers"] = [x if len(x) <= 44 else x[:43].rstrip() + "…" for x in heads if x][:5]
    return h


def plugin_of(path):
    """The plugin a local skill folder belongs to, or "" for a plain skill."""
    parts = path.split("/")
    if "skills" not in parts:
        return ""
    i = len(parts) - 1 - parts[::-1].index("skills")
    try:
        return json.load(open("/".join(parts[:i]) + "/.claude-plugin/plugin.json")).get("name", "")
    except (OSError, ValueError):
        return ""


def add_command(repo, folder, has_market):
    short = repo.split("/")[1]
    if folder:
        cmd = f"git clone --depth 1 https://github.com/{repo} /tmp/{short} && mkdir -p ~/.claude/skills && cp -R /tmp/{short}/{folder} ~/.claude/skills/"
    else:
        cmd = f"git clone --depth 1 https://github.com/{repo} ~/.claude/skills/{short}"
    return dict(copy=cmd, market=f"/plugin marketplace add {repo}" if has_market else "")


# ---------- skills already on this computer ----------
def local_dirs():
    only = [d for d in os.environ.get("SKILL_FINDER_ONLY", "").split(os.pathsep) if d]
    if only:  # look in these folders and nowhere else
        return [d for d in only if os.path.isdir(d)]
    h = os.path.expanduser("~")
    ds = [h + "/.claude/skills", h + "/.claude/plugins", os.getcwd() + "/.claude/skills", h + "/.codex/skills", h + "/.cursor/skills", h + "/.agents/skills"]
    ds += [d for d in os.environ.get("SKILL_FINDER_DIRS", "").split(os.pathsep) if d]
    return [d for d in ds if os.path.isdir(d)]


def local_skills():
    seen, out = set(), []
    for root in local_dirs():
        base = root.rstrip("/").count("/")
        for dp, dn, fn in os.walk(root, followlinks=True):
            dn[:] = [d for d in dn if d not in ("node_modules", ".git", ".trash", "__pycache__")]
            if dp.count("/") - base > 7:
                dn[:] = []
            if "SKILL.md" in fn:
                p = os.path.join(dp, "SKILL.md"); rp = os.path.realpath(p)
                if rp in seen:
                    continue
                seen.add(rp)
                try:
                    name, desc = front(open(p, errors="replace").read(8000))
                except OSError:
                    continue
                out.append(dict(name=name or os.path.basename(dp), desc=desc, path=dp))
            if len(out) > 4000:
                return out
    return out


def rank_local(topic, also, skills, k=8):
    """Installed skills that pass the gate, best fit first. Returns (the top k, how many passed)."""
    core, extra, w = query(topic, also)
    if not core or not skills:
        return [], 0
    docs = [terms(s["name"]) * 3 + terms(s["desc"]) for s in skills]
    res = []
    for s, d, x in zip(skills, docs, bm25(docs, w)):
        n, ok = gate(d, core, extra)
        if ok:
            res.append((x, s, n))
    res.sort(key=lambda r: -r[0])
    names, out = set(), []
    for x, s, n in res:
        if s["name"] not in names:
            names.add(s["name"]); out.append(dict(s, fit=round(x, 2), matched=n))
    return out[:k], len(out)


# ---------- public GitHub ----------
def token(use):
    if not use:
        return None
    t = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if t:
        return t
    try:
        return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, timeout=5).stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


class Limit(Exception):
    pass


def get(url, tok, raw=False):
    os.makedirs(CACHE, exist_ok=True)
    cf = os.path.join(CACHE, hashlib.sha1(url.encode()).hexdigest() + (".txt" if raw else ".json"))
    if os.path.exists(cf) and time.time() - os.path.getmtime(cf) < 86400:
        t = open(cf, errors="replace").read()
        return t if raw else json.loads(t)
    h = {"User-Agent": "skill-finder", "Accept": "application/vnd.github+json"}
    if tok and "api.github.com" in url:
        h["Authorization"] = "Bearer " + tok
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=20) as r:
                t = r.read(400000 if raw else 40000000).decode("utf-8", "replace")
            break
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):
                if attempt < 2 and (e.headers.get("Retry-After") or e.headers.get("X-RateLimit-Remaining") != "0"):
                    time.sleep(min(8, int(e.headers.get("Retry-After") or 2) + attempt * 2)); continue  # asked to slow down, not out of quota
                raise Limit("GitHub says too many requests. Wait a minute, or set GITHUB_TOKEN.")
            if e.code in (404, 409, 422, 451):
                return "" if raw else {}
            raise
    open(cf, "w").write(t)
    return t if raw else json.loads(t)


def search_github(topic, also, tok, limit=12, have=(), per_repo=2):
    """GitHub skills that pass the gate, ordered by fit rank and stars rank fused. Returns (list, notes, counts)."""
    kw = list(dict.fromkeys(words(topic)))[:4]
    al = [x for x in dict.fromkeys(words(also)) if x not in kw][:3]
    core, extra, w = query(topic, also); q = core + extra
    if not kw:
        return [], [], {}
    notes, cand = [], {}
    # all topic words together, then pairs of them, then each close word by itself, then the two skill topics.
    # With a token at most 13 searches (GitHub allows 30 a minute); without one fewer pairs (the limit is 10 a minute).
    two = ("skill in:name,description,readme", "topic:agent-skills")
    kk = kw[:4] if tok else kw[:3]
    queries = [(kw, e) for e in two]
    if len(kw) > 2:
        queries += [([kk[i], kk[j]], two[0]) for i in range(len(kk)) for j in range(i + 1, len(kk))]
    queries += [([a], two[0]) for a in (al if tok else al[:1])]
    queries += [(["topic:" + t], "") for t in ("agent-skills", "claude-skills")]
    limited = []

    def one(qq):
        tm, ex_q = qq
        n = 12 if not ex_q else 20
        try:
            return get("https://api.github.com/search/repositories?q=" + urllib.parse.quote((" ".join(tm) + " " + ex_q).strip()) + f"&sort=stars&order=desc&per_page={n}", tok).get("items", [])
        except Limit:
            limited.append(1); return []  # keep what the other searches found

    with ThreadPoolExecutor(3 if tok else 2) as ex:  # GitHub turns away many searches at once
        found = list(ex.map(one, queries))
    big = {}
    for (tm, ex_q), items in zip(queries, found):
        for it in items:
            (big if not ex_q else cand).setdefault(it["full_name"], it)
    scored = []
    for it in cand.values():
        topics = set(t.lower() for t in it.get("topics") or [])
        text = " ".join([it["name"], it.get("description") or "", " ".join(topics)])
        if not (topics & SKILL_TOPICS or "skill" in text.lower()):
            continue
        tt = toks(text)
        scored.append((sum(1 for t in q if t in tt), it["stargazers_count"], it))
    # repositories that mention the topic at all, most stars first: stars decide which ones get opened
    scored = sorted([x for x in scored if x[0] >= 1], key=lambda x: -x[1])
    n_c, n_big = (14, 12) if tok else (8, 6)
    # the big skill collections: their own description never names your topic, so they are always opened
    big = sorted(big.values(), key=lambda it: -it["stargazers_count"])[:n_big]
    todo = scored[:n_c] + [x for x in scored[n_c:] if x[0] >= min(2, len(q))][: n_c // 2 + 1]
    todo += [(0, it["stargazers_count"], it) for it in big if it["full_name"] not in {x[2]["full_name"] for x in todo}]

    def repo(job):
        rel, stars, it = job
        out = []
        try:
            tree = get(f"https://api.github.com/repos/{it['full_name']}/git/trees/{urllib.parse.quote(it['default_branch'])}?recursive=1", tok)
        except ValueError:
            return out  # a file list too large to read: skip this repository, keep the rest
        allp = {t["path"] for t in tree.get("tree", [])}
        paths = [p for p in allp if p == "SKILL.md" or p.endswith("/SKILL.md")]
        if not paths:
            return out
        # up to 8 folders per repo, best folder-name match first
        best = sorted(paths, key=lambda p: (-sum(1 for t in q if t in toks(os.path.dirname(p) or it["name"])), len(p)))[:8]
        if rel == 0 and not any(t in toks(os.path.dirname(best[0]) or it["name"]) for t in q):
            return out  # a big collection with no folder named after your topic
        flags = []
        if not it.get("license"):
            flags.append("no license")
        if it.get("archived"):
            flags.append("archived")
        if (it.get("pushed_at") or "9999") < time.strftime("%Y-%m-%d", time.gmtime(time.time() - 365 * 86400)):
            flags.append("no update for a year")
        for p in best:
            raw = get(f"https://raw.githubusercontent.com/{it['full_name']}/{urllib.parse.quote(it['default_branch'])}/{urllib.parse.quote(p)}", None, raw=True)
            name, desc = front(raw[:8000]); folder = os.path.dirname(p)
            skill = name or os.path.basename(folder) or it["name"]
            out.append(dict(skill=skill, repo=it["full_name"], stars=stars, desc=desc or (it.get("description") or ""), folder=folder, raw=raw, market=".claude-plugin/marketplace.json" in allp,
                            doc=terms(" ".join([name, os.path.basename(folder) or it["name"]])) * 3 + terms(desc), skills_in_repo=len(paths), flags=flags,
                            license={"NOASSERTION": "unclear"}.get((it.get("license") or {}).get("spdx_id"), (it.get("license") or {}).get("spdx_id") or "none"), updated=(it.get("pushed_at") or "")[:10],
                            url=f"https://github.com/{it['full_name']}" + (f"/tree/{it['default_branch']}/{folder}" if folder else "")))
        return out

    with ThreadPoolExecutor(8 if tok else 3) as ex:
        read = [o for part in ex.map(repo, todo) for o in part]
    pool, owned, seen = [], set(), set()
    for o, x in zip(read, bm25([o["doc"] for o in read], w)):
        n, ok = gate(o["doc"], core, extra)
        if not ok or (o["repo"], o["skill"]) in seen:
            continue
        seen.add((o["repo"], o["skill"]))
        if o["skill"].lower() in have:
            owned.add(o["skill"]); continue  # you already have a skill of this name: the first list shows it
        pool.append(dict(o, fit=round(x, 2), matched=n))
    if sum(1 for o in pool if o["stars"] >= 10) >= 3:  # drop near-unknown repos when there is enough choice
        pool = [o for o in pool if o["stars"] >= 10]
    by_fit = sorted(pool, key=lambda o: -o["fit"]); star_vals = sorted({o["stars"] for o in pool}, reverse=True)
    for i, o in enumerate(by_fit):
        o["r_fit"] = i + 1; o["r_stars"] = star_vals.index(o["stars"]) + 1; o["fused"] = round(1 / (RRF_K + o["r_fit"]) + 1 / (RRF_K + o["r_stars"]), 5)
    res, per = [], {}
    for o in sorted(pool, key=lambda o: -o["fused"]):
        if per.get(o["repo"], 0) < per_repo and len(res) < limit:
            per[o["repo"]] = per.get(o["repo"], 0) + 1
            how = howto(o["raw"], o["skill"]); how["add"] = add_command(o["repo"], o["folder"], o["market"])
            res.append(dict({k: v for k, v in o.items() if k not in ("raw", "doc", "market", "folder")}, how=how))
    if limited:
        notes.append(f"GitHub turned away {len(limited)} of {len(queries)} searches (too many requests), so this list may be short. Wait a minute and ask again.")
    if owned:
        notes.append(f"{len(owned)} GitHub {'skill' if len(owned) == 1 else 'skills'} left out because you already have a skill of that name.")
    counts = dict(searches=len(queries), repos=len(cand) + len(big), files_read=len(read), passed=len(pool), listed=len(res))
    notes.append(f"{counts['repos']} repositories looked at, {counts['files_read']} skill files read, {counts['passed']} passed the match rule, {counts['listed']} listed.")
    return res, notes, counts


cut = lambda s, n=150: s if len(s) <= n else s[: n - 1].rstrip() + "…"


def local_how(s):
    try:
        text = open(os.path.join(s["path"], "SKILL.md"), errors="replace").read(400000)
    except OSError:
        text = ""
    return howto(text, s["name"], plugin_of(s["path"]))


def mine(skills, as_json):
    """Every skill on this computer: its command and what it is for."""
    by = {}
    for s in skills:
        by.setdefault(s["name"], []).append(s)
    rows = [dict(name=n, call="/" + (plugin_of(by[n][0]["path"]) + ":" if plugin_of(by[n][0]["path"]) else "") + n, when=by[n][0]["desc"], copies=len(by[n]), path=by[n][0]["path"]) for n in sorted(by, key=str.lower)]
    twice = {n: len(v) for n, v in by.items() if len(v) > 1}
    if as_json:
        print(json.dumps(dict(installed_total=len(by), skills=rows, more_than_one_copy=twice), indent=1)); return 0
    print(f"YOUR SKILLS ({len(by)} on this computer)")
    for r in rows:
        print(f"  {r['call']}\n     {cut(r['when'], 130) or 'no description in the skill file'}")
    if twice:
        print("\nIn more than one place: " + ", ".join(f"{n} ({c})" for n, c in sorted(twice.items())))
    print("\nNothing was sent anywhere and nothing was changed.")
    return 0


def main():
    a = sys.argv[1:]; also = ""
    if "--also" in a:
        i = a.index("--also"); also = a[i + 1] if i + 1 < len(a) else ""; a = a[:i] + a[i + 2:]
    flags = {x for x in a if x.startswith("--")}
    topic = " ".join(x for x in a if not x.startswith("--")).strip()
    if "--mine" in flags:
        return mine(local_skills(), "--json" in flags)
    if not topic:
        print(__doc__); return 2
    have = local_skills(); total = len({s["name"] for s in have})
    local, passed = rank_local(topic, also, have)
    res = dict(topic=topic, also=also, installed_total=total, local_passed=passed, local=local, online=[], notes=[], github={})
    if "--no-online" not in flags:
        try:
            res["online"], res["notes"], res["github"] = search_github(topic, also, token("--no-token" not in flags), 12, {s["name"].lower() for s in have})
        except Limit as e:
            res["notes"].append(str(e))
        except (urllib.error.URLError, OSError, ValueError) as e:
            res["notes"].append("GitHub could not be reached: " + str(e)[:80])
    for s in res["local"]:
        s["how"] = local_how(s)
    if "--json" in flags:
        print(json.dumps(res, indent=1)); return 0
    print(f"Topic: {topic}\nClose words: {also or 'none given'}\n")
    print(f"1. ON THIS COMPUTER ({passed} of {total} installed skills passed the match rule; best fit first)")
    for s in res["local"]:
        h = s["how"]
        print(f"  {s['name']}  (fit {s['fit']})\n     {cut(s['desc'], 240)}\n     how: {h['call'] if h['by_name'] else 'just ask, it has no command'}" + (f"\n     needs: {' · '.join(h['needs'])}" if h["needs"] else ""))
    if not res["local"]:
        print("  nothing passed")
    print("\n2. ON GITHUB: not searched" if "--no-online" in flags else f"\n2. ON GITHUB ({len(res['online'])} candidates you do not have; fit and stars fused, best first)")
    for i, o in enumerate(res["online"], 1):
        fl = ("  ! " + ", ".join(o["flags"])) if o["flags"] else ""
        more = f", one of {o['skills_in_repo']} skills in this repo" if o["skills_in_repo"] > 1 else ""
        print(f"  {i}. {o['skill']}  [{o['repo']}, {o['stars']:,} stars{more}]\n     fit place {o['r_fit']} · stars place {o['r_stars']} · license {o['license']} · updated {o['updated']}{fl}\n     {cut(o['desc'], 240)}\n     {o['url']}\n     add: {o['how']['add']['copy']}\n     how: {o['how']['call']}" + (f"\n     needs: {' · '.join(o['how']['needs'])}" if o["how"]["needs"] else ""))
    if not res["online"] and "--no-online" not in flags:
        print("  nothing passed")
    for n in res["notes"]:
        print("\n" + n)
    print("\nThese are candidates, matched by words. Keep only the ones whose description does the job. Nothing was installed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
