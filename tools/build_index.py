#!/usr/bin/env python3
"""Build the list of public skills that ships with SkillSelect (skills/skillselect/scripts/index.json.gz).

Why: without a GitHub login, GitHub allows 60 API calls an hour, and one request to the finder can use most of them.
With this list the finder can answer from the largest public skill collections with no API call at all.

What goes in: for the most-starred repositories tagged as skill collections, each skill's name, the first 240
characters of its description, its folder, and the repository's stars, license and last update on the build day.
No skill body is copied. A skill whose text gives orders to the assistant is left out.

Run by the maintainer before a release (needs `gh auth login` or GITHUB_TOKEN):
    python3 tools/build_index.py [--repos 80] [--per-repo 300]
"""
import gzip
import json
import os
import sys
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "skills", "skillselect", "scripts"))
import find_skills as F  # noqa: E402

TOPICS = ("agent-skills", "claude-skills", "claude-code-skills", "codex-skills", "anthropic-skills", "ai-skills", "claude-skill", "agent-skill")
MIN_STARS = 200


def arg(name, default):
    return int(sys.argv[sys.argv.index(name) + 1]) if name in sys.argv else default


def main():
    n_repos, per_repo = arg("--repos", 80), arg("--per-repo", 300)
    tok = F.token(True)
    if not tok:
        print("needs a GitHub login: run `gh auth login` or set GITHUB_TOKEN"); return 2
    found = {}
    for t in TOPICS:
        for page in (1, 2):
            q = urllib.parse.quote(f"topic:{t} stars:>={MIN_STARS}")
            items = F.get(f"https://api.github.com/search/repositories?q={q}&sort=stars&order=desc&per_page=50&page={page}", tok).get("items", [])
            for it in items:
                found.setdefault(it["full_name"], it)
            time.sleep(2.2)  # 30 searches a minute
            if len(items) < 50:
                break
    repos = sorted(found.values(), key=lambda it: -it["stargazers_count"])
    print(len(repos), "repositories tagged as skill collections with", MIN_STARS, "stars or more")

    def read(it):
        if it.get("archived") or it.get("fork"):
            return None
        try:
            tree = F.get(f"https://api.github.com/repos/{it['full_name']}/git/trees/{urllib.parse.quote(it['default_branch'])}?recursive=1", tok)
        except ValueError:
            return None
        allp = [t["path"] for t in tree.get("tree", [])]
        paths = sorted((p for p in allp if (p == "SKILL.md" or p.endswith("/SKILL.md")) and not F.TEST_DIRS & set(p.split("/"))), key=lambda p: (p.count("/"), p))
        if not paths:
            return None
        rows, seen = [], set()
        for p in paths[:per_repo]:
            folder = os.path.dirname(p)
            if folder and (not F.SAFE_PATH.match(folder) or any(x.startswith("-") or x in (".", "..") for x in folder.split("/"))):
                continue  # a folder name the add line would refuse
            raw = F.get(f"https://raw.githubusercontent.com/{it['full_name']}/{urllib.parse.quote(it['default_branch'])}/{urllib.parse.quote(p)}", None, raw=True)
            name, desc = F.front(raw[:8000]); name = F.clean(name, 60) or os.path.basename(folder) or it["name"]; desc = F.clean(desc, 240)
            if not desc or F.gives_orders(desc) or F.gives_orders(name) or F.odd_name(name) or name.lower() in seen:
                continue
            seen.add(name.lower()); h = F.howto(raw, name)
            rows.append([name, folder, desc, h["call"], h["needs"], h["by_name"]])
        if not rows:
            return None
        lic = (it.get("license") or {}).get("spdx_id") or "none"
        return dict(repo=it["full_name"], stars=it["stargazers_count"], license={"NOASSERTION": "unclear"}.get(lic, lic), updated=(it.get("pushed_at") or "")[:10],
                    branch=it["default_branch"], market=".claude-plugin/marketplace.json" in allp, files=len(paths), skills=rows)

    out = []
    with ThreadPoolExecutor(8) as ex:
        for r in ex.map(read, repos[: n_repos * 2]):
            if r and SAFE(r["repo"]) and len(out) < n_repos:
                out.append(r)
    index = dict(built=time.strftime("%Y-%m-%d", time.gmtime()), min_stars=MIN_STARS, topics=list(TOPICS), repos=out)
    path = os.path.join(ROOT, "skills", "skillselect", "scripts", "index.json.gz")
    with gzip.GzipFile(path, "wb", mtime=0) as f:
        f.write(json.dumps(index, ensure_ascii=False, separators=(",", ":")).encode())
    n = sum(len(r["skills"]) for r in out)
    print(f"{n} skills from {len(out)} repositories -> {path} ({os.path.getsize(path) // 1024} KB)")
    return 0


def SAFE(repo):
    return bool(F.SAFE_REPO.match(repo))


if __name__ == "__main__":
    sys.exit(main())
