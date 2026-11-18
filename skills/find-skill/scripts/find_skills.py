#!/usr/bin/env python3
"""find_skills.py "<what you want to do>" [--json] [--no-online] [--no-token] [--limit N]

1. Looks at the skills already on this computer. Nothing about them leaves the machine.
2. Searches public GitHub for skills that fit and lists them with the most stars first.

It never installs, clones or downloads a skill. The only thing sent out is the search words, to api.github.com.
Python 3 standard library only."""
import hashlib, json, math, os, re, subprocess, sys, time, urllib.error, urllib.parse, urllib.request

STOP = set("a an and are as at be but by for from has have i if in into is it its me my of on or so that the then this to use used using was what when where which who why will with you your "
           "want need create make making build new one some any please help can could would like get do does how find skill skills tool plugin before after first then sign just really good best".split())
SKILL_TOPICS = {"claude-skills", "agent-skills", "claude-code-skills", "claude-skill", "agent-skill", "skills", "claude-code", "codex-skills", "ai-skills", "anthropic-skills"}
CACHE = os.environ.get("SKILL_FINDER_CACHE") or os.path.expanduser("~/.cache/skill-finder")


def words(s):
    return [w for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in STOP and len(w) > 1]


def stem(w):
    for suf in ("ing", "ics", "es", "s"):
        if len(w) > 4 and w.endswith(suf):
            return w[: -len(suf)]
    return w


def toks(s):
    return [stem(w) for w in words(s)]


def front(text):
    m = re.match(r"---\s*\n(.*?)\n---", text, re.S)
    fm = m.group(1) if m else ""
    n = re.search(r"^name:\s*(.+)$", fm, re.M)
    d = re.search(r"^description:\s*(.*?)(?=\n[A-Za-z_-]+:|\Z)", fm, re.S | re.M)
    desc = re.sub(r"\s+", " ", d.group(1)).strip().strip("\"'>|") if d else ""
    return (n.group(1).strip().strip("\"'") if n else ""), desc.strip()


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


def rank_local(need, skills, k=3):
    q = list(dict.fromkeys(toks(need)))
    if not q or not skills:
        return []
    docs = [toks(s["name"]) * 3 + toks(s["desc"]) for s in skills]
    N = len(docs); avg = sum(map(len, docs)) / N or 1
    df = {t: sum(1 for d in docs if t in d) for t in q}
    res = []
    for s, d in zip(skills, docs):
        hit = [t for t in q if t in d]
        if len(hit) < min(len(q), max(2, math.ceil(len(q) / 2))):
            continue
        sc = sum(math.log(1 + (N - df[t] + 0.5) / (df[t] + 0.5)) * d.count(t) * 2.5 / (d.count(t) + 1.5 * (0.25 + 0.75 * len(d) / avg)) for t in hit)
        res.append((len(hit), sc, s))
    res.sort(key=lambda x: (-x[0], -x[1]))
    names, out = set(), []
    for h, sc, s in res:
        if s["name"] in names:
            continue
        names.add(s["name"]); out.append(dict(s, matched=h, of=len(q)))
    return out[:k]


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
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=20) as r:
            t = r.read(400000 if raw else 40000000).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        if e.code in (403, 429):
            raise Limit("GitHub says too many requests. Wait a minute, or set GITHUB_TOKEN.")
        if e.code in (404, 409, 422, 451):
            return "" if raw else {}
        raise
    open(cf, "w").write(t)
    return t if raw else json.loads(t)


def search_github(need, tok, limit=5):
    kw = list(dict.fromkeys(words(need)))[:4]
    q = list(dict.fromkeys(toks(need)))
    if not kw:
        return [], []
    notes, cand = [], {}

    def run(terms, extras):
        for extra in extras:
            url = "https://api.github.com/search/repositories?q=" + urllib.parse.quote(" ".join(terms) + " " + extra) + "&sort=stars&order=desc&per_page=20"
            for it in get(url, tok).get("items", []):
                cand.setdefault(it["full_name"], it)

    # all key words together, then pairs of them, so the order you say them in does not decide the result.
    # With a token: every pair of the first four (14 searches at most; GitHub allows 30 a minute).
    # Without one: pairs of the first three with one query each (5 searches; the limit is 10 a minute).
    two = ("skill in:name,description,readme", "topic:agent-skills")
    run(kw, two)
    kk = kw[:4] if tok else kw[:3]
    for i in range(len(kk)):
        for j in range(i + 1, len(kk)):
            if len(kw) > 2:
                run([kk[i], kk[j]], two if tok else two[:1])
    scored = []
    for it in cand.values():
        topics = set(t.lower() for t in it.get("topics") or [])
        text = " ".join([it["name"], it.get("description") or "", " ".join(topics)])
        if not (topics & SKILL_TOPICS or "skill" in text.lower()):
            continue
        rel = sum(1 for t in q if t in toks(text))
        scored.append((rel, it["stargazers_count"], it))
    # repositories that mention the topic at all, most stars first: stars decide which ones get opened
    scored = sorted([x for x in scored if x[0] >= 1], key=lambda x: -x[1])
    n_c, n_big = (14, 12) if tok else (8, 6)
    # the big skill collections: their own description never names your topic, so they are always opened
    big = {}
    for topic in ("agent-skills", "claude-skills"):
        for it in get("https://api.github.com/search/repositories?q=" + urllib.parse.quote("topic:" + topic) + "&sort=stars&order=desc&per_page=12", tok).get("items", []):
            big.setdefault(it["full_name"], it)
    big = sorted(big.values(), key=lambda it: -it["stargazers_count"])[:n_big]
    todo = scored[:n_c] + [(0, it["stargazers_count"], it) for it in big if it["full_name"] not in {x[2]["full_name"] for x in scored[:n_c]}]
    out = []
    for rel, stars, it in todo:
        try:
            tree = get(f"https://api.github.com/repos/{it['full_name']}/git/trees/{urllib.parse.quote(it['default_branch'])}?recursive=1", tok)
        except ValueError:
            continue  # a file list too large to read: skip this repository, keep the rest
        paths = [t["path"] for t in tree.get("tree", []) if t["path"] == "SKILL.md" or t["path"].endswith("/SKILL.md")]
        if not paths:
            continue
        # up to 8 folders per repo, best folder-name match first; the description then decides which one is shown
        best = sorted(paths, key=lambda p: (-sum(1 for t in q if t in toks(os.path.dirname(p) or it["name"])), len(p)))[:8]
        if rel == 0 and not any(t in toks(os.path.dirname(best[0]) or it["name"]) for t in q):
            continue  # a big collection with no folder named after your topic
        picks = []
        for p in best:
            raw = get(f"https://raw.githubusercontent.com/{it['full_name']}/{urllib.parse.quote(it['default_branch'])}/{urllib.parse.quote(p)}", None, raw=True)
            name, desc = front(raw[:8000])
            nm = set(toks(" ".join([name, os.path.dirname(p) or it["name"]])))
            mt = nm | set(toks(desc))
            picks.append((sum(1 for t in q if t in mt), sum(1 for t in q if t in nm), -len(p), p, name, desc))
        picks.sort(reverse=True)
        for matched, _, _, p, name, desc in picks[:1]:
            folder = os.path.dirname(p)
            flags = []
            if not it.get("license"):
                flags.append("no license")
            if it.get("archived"):
                flags.append("archived")
            if (it.get("pushed_at") or "9999") < time.strftime("%Y-%m-%d", time.gmtime(time.time() - 365 * 86400)):
                flags.append("no update for a year")
            out.append(dict(skill=name or os.path.basename(folder) or it["name"], repo=it["full_name"], stars=stars, license={"NOASSERTION": "unclear"}.get((it.get("license") or {}).get("spdx_id"), (it.get("license") or {}).get("spdx_id") or "none"),
                            updated=(it.get("pushed_at") or "")[:10], desc=desc or (it.get("description") or ""), matched=matched, of=len(q), skills_in_repo=len(paths), flags=flags,
                            url=f"https://github.com/{it['full_name']}" + (f"/tree/{it['default_branch']}/{folder}" if folder else "")))
    need_hits = max(1, math.ceil(len(q) / 2))
    fit = [o for o in out if o["matched"] >= need_hits]
    if sum(1 for o in fit if o["stars"] >= 10) >= 3:  # drop near-unknown repos when there is enough choice
        fit = [o for o in fit if o["stars"] >= 10]
    fit.sort(key=lambda o: (-o["stars"], -o["matched"]))
    seen, res = set(), []
    for o in fit:
        if (o["repo"], o["skill"]) in seen:
            continue
        seen.add((o["repo"], o["skill"])); res.append(o)
    notes.append(f"{len(cand) + len(big)} repositories looked at, {len(out)} skill folders read, {len(res)} fit at least {need_hits} of your {len(q)} key words.")
    return res[:limit], notes


def recommend(res):
    """One pick. A skill you already have wins: nothing to download and nothing new to trust."""
    if res["local"]:
        s = res["local"][0]
        return dict(name=s["name"], where="installed", why="You already have it, so there is nothing to download.", path=s["path"])
    if res["online"]:
        full = [o for o in res["online"] if o["matched"] == o["of"]]
        o = (full or res["online"])[0]
        why = "Most stars among the skills that fit every key word." if full else "Most stars among the skills that fit."
        return dict(name=o["skill"], where=f"GitHub, {o['repo']}, {o['stars']:,} stars", why=why, url=o["url"])
    return None


def main():
    a = sys.argv[1:]
    flags = {x for x in a if x.startswith("--")}
    lim = 5
    if "--limit" in a:
        i = a.index("--limit"); lim = int(a[i + 1]); a = a[:i] + a[i + 2:]
    need = " ".join(x for x in a if not x.startswith("--")).strip()
    if not need:
        print(__doc__); return 2
    mine = local_skills()
    res = dict(need=need, key_words=list(dict.fromkeys(words(need)))[:4], installed_total=len({s["name"] for s in mine}), local=rank_local(need, mine), online=[], notes=[])
    if "--no-online" not in flags:
        try:
            res["online"], res["notes"] = search_github(need, token("--no-token" not in flags), lim)
        except Limit as e:
            res["notes"].append(str(e))
        except (urllib.error.URLError, OSError, ValueError) as e:
            res["notes"].append("GitHub could not be reached: " + str(e)[:80])
    res["recommended"] = recommend(res)
    if "--json" in flags:
        print(json.dumps(res, indent=1)); return 0
    cut = lambda s, n=150: s if len(s) <= n else s[: n - 1].rstrip() + "…"
    print(f"You asked for: {need}\nKey words used: {', '.join(res['key_words'])}\n")
    print(f"INSTALLED ON THIS COMPUTER ({len(res['local'])} fit, of {res['installed_total']} installed)")
    for s in res["local"]:
        print(f"  {s['name']}  ({s['matched']} of {s['of']} key words)\n     {cut(s['desc'])}\n     {s['path']}")
    if not res["local"]:
        print("  nothing that fits")
    print(f"\nAVAILABLE ON GITHUB, MOST STARS FIRST ({len(res['online'])})")
    for i, o in enumerate(res["online"], 1):
        fl = ("  ! " + ", ".join(o["flags"])) if o["flags"] else ""
        more = f", one of {o['skills_in_repo']} skills in this repo" if o["skills_in_repo"] > 1 else ""
        print(f"  {i}. {o['stars']:,} stars  {o['skill']}  [{o['repo']}{more}]\n     license {o['license']} · updated {o['updated']} · {o['matched']} of {o['of']} key words{fl}\n     {cut(o['desc'])}\n     {o['url']}")
    if not res["online"] and "--no-online" not in flags:
        print("  nothing found that fits")
    r = res["recommended"]
    print("\nRECOMMENDED")
    print(f"  {r['name']}  ({r['where']})\n     {r['why']}" if r else "  nothing fits well enough to recommend")
    for n in res["notes"]:
        print("\n" + n)
    print("\nNothing was installed. Read a skill before you add it: it is text your assistant will trust.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
