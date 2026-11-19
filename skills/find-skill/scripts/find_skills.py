#!/usr/bin/env python3
"""find_skills.py "<what you want to do>" [--json] [--no-online] [--no-token] [--limit N]
find_skills.py --mine [words] [--json]       every skill on this computer: how to call it and when to use it
find_skills.py --how <skill name | github link>   how to use one skill

1. Looks at the skills already on this computer. Nothing about them leaves the machine.
2. Searches public GitHub for skills that fit and lists them with the most stars first.
3. Says how to use the one it recommends: how to call it, what it needs, and for a GitHub skill the command to add it.

It never installs, clones or downloads a skill. The only thing sent out is the search words, to api.github.com.
Python 3 standard library only."""
import hashlib, json, math, os, re, subprocess, sys, time, urllib.error, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

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


def show_how(h, pad="  "):
    out = []
    if h.get("add"):
        out.append(pad + "Add it first. You run this, the plugin never does:")
        out.append(pad + "   " + h["add"]["copy"])
        if h["add"]["market"]:
            out.append(pad + "   or, as a Claude Code plugin:  " + h["add"]["market"] + "  (then pick it under /plugin)")
        out.append(pad + "Read it before you add it: " + h.get("url", ""))
    if h["by_name"]:
        out.append(pad + "Call it:    " + h["call"])
        if h["auto"]:
            out.append(pad + "            or just ask in your own words. Claude loads it when the request fits.")
    else:
        out.append(pad + "Call it:    just ask in your own words. Claude loads it itself; it has no command.")
    if h.get("when"):
        out.append(pad + "Use it for: " + h["when"])
    out.append(pad + "It needs:   " + (" · ".join(h["needs"]) + "  (named in its instructions)" if h["needs"] else "nothing named in its instructions"))
    if h["covers"]:
        out.append(pad + "It covers:  " + " · ".join(h["covers"]))
    return "\n".join(out)


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


def rank_local(need, skills, k=5):
    q = list(dict.fromkeys(toks(need)))
    if not q or not skills:
        return []
    docs = [toks(s["name"]) * 3 + toks(s["desc"]) for s in skills]
    N = len(docs); avg = sum(map(len, docs)) / N or 1
    df = {t: sum(1 for d in docs if t in d) for t in q}
    res = []
    for s, d in zip(skills, docs):
        hit = [t for t in q if t in d]
        if len(hit) < min(2, len(q)):
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


def search_github(need, tok, limit=5, have=()):
    kw = list(dict.fromkeys(words(need)))[:4]
    q = list(dict.fromkeys(toks(need)))
    if not kw:
        return [], []
    notes, cand = [], {}

    # all key words together, then pairs of them, so the order you say them in does not decide the result.
    # With a token: every pair of the first four (10 searches; GitHub allows 30 a minute).
    # Without one: pairs of the first three (7 searches; the limit is 10 a minute).
    two = ("skill in:name,description,readme", "topic:agent-skills")
    kk = kw[:4] if tok else kw[:3]
    queries = [(kw, e) for e in two]
    if len(kw) > 2:
        queries += [([kk[i], kk[j]], two[0]) for i in range(len(kk)) for j in range(i + 1, len(kk))]
    queries += [(["topic:" + t], "") for t in ("agent-skills", "claude-skills")]
    limited = []

    def one(q):
        terms, extra = q
        n = 12 if not extra else 20
        try:
            return get("https://api.github.com/search/repositories?q=" + urllib.parse.quote((" ".join(terms) + " " + extra).strip()) + f"&sort=stars&order=desc&per_page={n}", tok).get("items", [])
        except Limit:
            limited.append(1); return []  # keep what the other searches found

    with ThreadPoolExecutor(3 if tok else 2) as ex:  # GitHub turns away many searches at once
        found = list(ex.map(one, queries))
    big = {}
    for (terms, extra), items in zip(queries, found):
        for it in items:
            (big if not extra else cand).setdefault(it["full_name"], it)
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
    big = sorted(big.values(), key=lambda it: -it["stargazers_count"])[:n_big]
    todo = scored[:n_c]
    # plus the repositories whose own name or description names two of your key words: fewer stars, closer to the job
    close = [x for x in scored[n_c:] if x[0] >= min(2, len(q))][: n_c // 2 + 1]
    todo += close
    todo += [(0, it["stargazers_count"], it) for it in big if it["full_name"] not in {x[2]["full_name"] for x in todo}]
    skipped = []

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
        # up to 8 folders per repo, best folder-name match first; the description then decides which one is shown
        best = sorted(paths, key=lambda p: (-sum(1 for t in q if t in toks(os.path.dirname(p) or it["name"])), len(p)))[:8]
        if rel == 0 and not any(t in toks(os.path.dirname(best[0]) or it["name"]) for t in q):
            return out  # a big collection with no folder named after your topic
        picks = []
        for p in best:
            raw = get(f"https://raw.githubusercontent.com/{it['full_name']}/{urllib.parse.quote(it['default_branch'])}/{urllib.parse.quote(p)}", None, raw=True)
            name, desc = front(raw[:8000])
            nm = set(toks(" ".join([name, os.path.dirname(p) or it["name"]])))
            mt = nm | set(toks(desc))
            picks.append((sum(1 for t in q if t in mt), sum(1 for t in q if t in nm), -len(p), p, name, desc, raw))
        picks.sort(reverse=True)
        mine_here = [x for x in picks if (x[4] or os.path.basename(os.path.dirname(x[3]))).lower() in have]
        if mine_here:  # you already have these: step 1 shows them, so take this repository's next fit instead
            skipped.extend(x[4] for x in mine_here if x[0] >= min(2, len(q))); picks = [x for x in picks if x not in mine_here]
        # the best folder of the repository, and a second one when it is named after your topic too
        first = picks[:1] + [x for x in picks[1:2] if x[1] >= 1 and x[0] >= min(2, len(q))]
        spare = [x for x in picks[len(first):] if x[1] >= 1 and x[0] >= min(2, len(q))]
        for matched, _, _, p, name, desc, raw in first + spare:
            folder = os.path.dirname(p)
            how = howto(raw, name or os.path.basename(folder) or it["name"])
            how["add"] = add_command(it["full_name"], folder, ".claude-plugin/marketplace.json" in allp)
            flags = []
            if not it.get("license"):
                flags.append("no license")
            if it.get("archived"):
                flags.append("archived")
            if (it.get("pushed_at") or "9999") < time.strftime("%Y-%m-%d", time.gmtime(time.time() - 365 * 86400)):
                flags.append("no update for a year")
            out.append(dict(skill=name or os.path.basename(folder) or it["name"], repo=it["full_name"], stars=stars, license={"NOASSERTION": "unclear"}.get((it.get("license") or {}).get("spdx_id"), (it.get("license") or {}).get("spdx_id") or "none"),
                            updated=(it.get("pushed_at") or "")[:10], desc=desc or (it.get("description") or ""), matched=matched, of=len(q), skills_in_repo=len(paths), flags=flags,
                            url=f"https://github.com/{it['full_name']}" + (f"/tree/{it['default_branch']}/{folder}" if folder else ""), how=how, spare=len(out) >= len(first)))
        return out

    with ThreadPoolExecutor(8 if tok else 3) as ex:
        out = [o for part in ex.map(repo, todo) for o in part]
    need_hits = min(2, len(q))
    fit = [o for o in out if o["matched"] >= need_hits and not o["spare"]]
    spares = sorted([o for o in out if o["matched"] >= need_hits and o["spare"] and o["stars"] >= 50], key=lambda o: (-o["stars"], -o["matched"]))
    if sum(1 for o in fit if o["stars"] >= 10) >= 3:  # drop near-unknown repos when there is enough choice
        fit = [o for o in fit if o["stars"] >= 10]
    half = math.ceil(len(q) / 2)  # skills that fit at least half of the key words come before the looser fits
    close = [o for o in fit if o["matched"] >= half and o["skill"].lower() not in have]
    if len({(o["repo"], o["skill"]) for o in close}) >= limit:  # enough close fits: show only those
        fit = close
    fit.sort(key=lambda o: (-o["stars"], -o["matched"]))  # the list is by stars, as its heading says
    seen, res, owned = set(), [], len(set(skipped))
    for o in fit:
        if (o["repo"], o["skill"]) in seen:
            continue
        seen.add((o["repo"], o["skill"])); res.append(o)
    for o in spares:  # a short list is filled from the repositories already read, most stars first
        if len(res) >= limit:
            break
        if (o["repo"], o["skill"]) not in seen:
            seen.add((o["repo"], o["skill"])); res.append(o)
    res.sort(key=lambda o: (-o["stars"], -o["matched"]))
    if limited:
        notes.append(f"GitHub turned away {len(limited)} of {len(queries)} searches (too many requests), so this list may be short. Wait a minute and ask again.")
    if owned:
        notes.append(f"{owned} GitHub {'skill' if owned == 1 else 'skills'} left out of the list because you already have a skill of that name.")
    notes.append(f"{len(cand) + len(big)} repositories looked at, {len(out)} skill folders read, {len(res)} fit at least {need_hits} of your {len(q)} key words.")
    return res[:limit], notes


cut = lambda s, n=150: s if len(s) <= n else s[: n - 1].rstrip() + "…"


def local_how(s):
    try:
        text = open(os.path.join(s["path"], "SKILL.md"), errors="replace").read(400000)
    except OSError:
        text = ""
    return dict(howto(text, s["name"], plugin_of(s["path"])), when=cut(s["desc"], 170))


def mine(need, skills, as_json):
    """Every skill on this computer: its command and when to use it. With words, only the ones that fit."""
    by = {}
    for s in skills:
        by.setdefault(s["name"], []).append(s)
    names = [s["name"] for s in rank_local(need, skills, k=40)] if need else sorted(by, key=str.lower)
    rows = [dict(name=n, call="/" + (plugin_of(by[n][0]["path"]) + ":" if plugin_of(by[n][0]["path"]) else "") + n, when=by[n][0]["desc"], copies=len(by[n]), path=by[n][0]["path"]) for n in names]
    twice = {n: len(v) for n, v in by.items() if len(v) > 1}
    if as_json:
        print(json.dumps(dict(installed_total=len(by), shown=len(rows), skills=rows, more_than_one_copy=twice), indent=1)); return 0
    print(f"YOUR SKILLS ({len(by)} on this computer" + (f", {len(rows)} fit \"{need}\"" if need else "") + ")")
    for r in rows:
        print(f"  {r['call']}\n     {cut(r['when'], 130) or 'no description in the skill file'}")
    if twice:
        print("\nIn more than one place: " + ", ".join(f"{n} ({c})" for n, c in sorted(twice.items())))
    print("\nNothing was sent anywhere. To use one, type its command, or just ask: Claude loads a skill when the request fits its description.")
    return 0


def how_one(target, skills, tok):
    """How to use one skill: a name on this computer, or a github.com link to a skill folder or repository."""
    m = re.search(r"github\.com/([\w.-]+/[\w.-]+?)(?:\.git)?(?:/tree/([^/]+)/(.+?))?/?$", target)
    if not m:
        hit = [s for s in skills if s["name"].lower() == target.lower().lstrip("/").split(":")[-1]]
        if not hit:
            print(f"No skill named {target} on this computer. Give a github.com link to look at one online."); return 1
        print(f"HOW TO USE {hit[0]['name']}  (installed)\n" + show_how(local_how(hit[0])) + f"\n  {hit[0]['path']}"); return 0
    repo, branch, folder = m.group(1), m.group(2), (m.group(3) or "").strip("/")
    info = get(f"https://api.github.com/repos/{repo}", tok)
    if not info:
        print(f"GitHub has no public repository {repo}."); return 1
    branch = branch or info["default_branch"]
    tree = get(f"https://api.github.com/repos/{repo}/git/trees/{urllib.parse.quote(branch)}?recursive=1", tok)
    allp = {t["path"] for t in tree.get("tree", [])}
    p = (folder + "/SKILL.md") if folder else "SKILL.md"
    if p not in allp:
        inside = sorted(os.path.dirname(x) for x in allp if x.endswith("/SKILL.md"))
        print(f"No SKILL.md at {p} in {repo}." + (f" Skill folders there: {', '.join(inside[:12])}" if inside else "")); return 1
    raw = get(f"https://raw.githubusercontent.com/{repo}/{urllib.parse.quote(branch)}/{urllib.parse.quote(p)}", None, raw=True)
    name, desc = front(raw[:8000])
    h = dict(howto(raw, name or os.path.basename(folder) or repo.split("/")[1]), when=cut(desc, 170), url=f"https://github.com/{repo}" + (f"/tree/{branch}/{folder}" if folder else ""))
    h["add"] = add_command(repo, folder, ".claude-plugin/marketplace.json" in allp)
    lic = (info.get("license") or {}).get("spdx_id") or "none"
    print(f"HOW TO USE {name or folder}  (GitHub, {repo}, {info.get('stargazers_count', 0):,} stars, license {lic}, updated {(info.get('pushed_at') or '')[:10]})\n" + show_how(h))
    print("\nNothing was installed."); return 0


def recommend(res):
    """One pick. A skill you already have wins: nothing to download and nothing new to trust."""
    if res["local"]:
        s = res["local"][0]
        return dict(name=s["name"], where="installed", why="You already have it, so there is nothing to download.", path=s["path"], how=dict(local_how(s), when=""))
    if res["online"]:
        full = [o for o in res["online"] if o["matched"] == o["of"]]
        o = (full or res["online"])[0]
        why = "Most stars among the skills that fit every key word." if full else "Most stars among the skills that fit."
        return dict(name=o["skill"], where=f"GitHub, {o['repo']}, {o['stars']:,} stars", why=why, url=o["url"], how=dict(o["how"], url=o["url"]))
    return None


def main():
    a = sys.argv[1:]
    flags = {x for x in a if x.startswith("--")}
    lim = 5
    if "--limit" in a:
        i = a.index("--limit"); lim = int(a[i + 1]); a = a[:i] + a[i + 2:]
    need = " ".join(x for x in a if not x.startswith("--")).strip()
    if "--mine" in flags:
        return mine(need, local_skills(), "--json" in flags)
    if not need:
        print(__doc__); return 2
    if "--how" in flags:
        try:
            return how_one(need, local_skills(), token("--no-token" not in flags))
        except Limit as e:
            print(e); return 1
        except (urllib.error.URLError, OSError, ValueError) as e:
            print("GitHub could not be reached: " + str(e)[:80]); return 1
    have = local_skills()
    res = dict(need=need, key_words=list(dict.fromkeys(words(need)))[:4], installed_total=len({s["name"] for s in have}), local=rank_local(need, have), online=[], notes=[])
    if "--no-online" not in flags:
        try:
            res["online"], res["notes"] = search_github(need, token("--no-token" not in flags), lim, {s["name"].lower() for s in have})
        except Limit as e:
            res["notes"].append(str(e))
        except (urllib.error.URLError, OSError, ValueError) as e:
            res["notes"].append("GitHub could not be reached: " + str(e)[:80])
    for s in res["local"]:
        s["how"] = local_how(s)
    res["recommended"] = recommend(res)
    if "--json" in flags:
        print(json.dumps(res, indent=1)); return 0
    print(f"You asked for: {need}\nKey words used: {', '.join(res['key_words'])}\n")
    print(f"1. WHAT YOU HAVE ({len(res['local'])} fit, of {res['installed_total']} installed on this computer)")
    for s in res["local"]:
        h = s["how"]
        print(f"  {s['name']}  ({s['matched']} of {s['of']} key words)\n     {cut(s['desc'])}\n     call: {h['call'] if h['by_name'] else 'just ask, it has no command'}" + (f"\n     needs: {' · '.join(h['needs'])}" if h["needs"] else ""))
    if not res["local"]:
        print("  nothing that fits")
    print("\n2. ON GITHUB: not searched" if "--no-online" in flags else f"\n2. ON GITHUB, MOST STARS FIRST ({len(res['online'])} you do not have)")
    for i, o in enumerate(res["online"], 1):
        fl = ("  ! " + ", ".join(o["flags"])) if o["flags"] else ""
        more = f", one of {o['skills_in_repo']} skills in this repo" if o["skills_in_repo"] > 1 else ""
        print(f"  {i}. {o['stars']:,} stars  {o['skill']}  [{o['repo']}{more}]\n     license {o['license']} · updated {o['updated']} · {o['matched']} of {o['of']} key words{fl}\n     {cut(o['desc'])}\n     {o['url']}\n     add: {o['how']['add']['copy']}\n     call: {o['how']['call']}" + (f"\n     needs: {' · '.join(o['how']['needs'])}" if o["how"]["needs"] else ""))
    if not res["online"] and "--no-online" not in flags:
        print("  nothing found that fits")
    r = res["recommended"]
    print("\n3. START WITH THIS ONE")
    print(f"  {r['name']}  ({r['where']})\n  {r['why']}\n" + show_how(r["how"]) if r else "  nothing fits well enough to recommend")
    for n in res["notes"]:
        print("\n" + n)
    print("\nNothing was installed. Read a skill before you add it: it is text your assistant will trust.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
