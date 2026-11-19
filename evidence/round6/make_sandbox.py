"""Round 6 test folder: 50 public skills from six public repositories, copied into one project.
Usage: python3 make_sandbox.py <folder with the cloned repositories> <target project folder>"""
import json, os, shutil, sys
SRC, DST = sys.argv[1], sys.argv[2]
PICK = {
 "alirezarezvani/claude-skills": ["landing-page-generator", "landing", "epic-design", "page-cro", "copywriting", "code-reviewer", "stock-analysis", "data-quality-auditor", "financial-health", "content-production", "pr-review-expert", "seo-auditor"],
 "anthropics/skills": ["docx", "pdf", "pptx", "xlsx", "mcp-builder", "skill-creator", "claude-api", "internal-comms", "slack-gif-creator", "doc-coauthoring", "algorithmic-art", "webapp-testing"],
 "obra/superpowers": ["brainstorming", "systematic-debugging", "test-driven-development", "writing-plans", "executing-plans", "requesting-code-review", "receiving-code-review", "using-git-worktrees", "verification-before-completion", "dispatching-parallel-agents"],
 "vercel-labs/agent-skills": ["deploy-to-vercel", "vercel-react-best-practices", "vercel-optimize", "vercel-cli-with-tokens"],
 "ComposioHQ/awesome-claude-skills": ["changelog-generator", "file-organizer", "image-enhancer", "invoice-organizer", "meeting-insights-analyzer", "raffle-winner-picker", "tailored-resume-generator", "domain-name-brainstormer", "youtube-downloader", "langsmith-fetch"],
 "lawve/legal-skills": ["gdpr-compliance", "dpdpa"],
}
DIRS = {"alirezarezvani/claude-skills": "alirezarezvani-claude-skills", "anthropics/skills": "anthropics-skills", "obra/superpowers": "obra-superpowers", "vercel-labs/agent-skills": "vercel-agent-skills",
        "ComposioHQ/awesome-claude-skills": "composio-awesome-claude-skills", "lawve/legal-skills": "lawve-legal-skills"}


def name_of(p):
    for line in open(p, errors="replace").read(4000).split("\n"):
        if line.startswith("name:"):
            return line[5:].strip().strip("\"'")
    return ""


out = os.path.join(DST, ".claude", "skills"); os.makedirs(out, exist_ok=True); done = []
for repo, names in PICK.items():
    found = {}
    for dp, dn, fn in os.walk(os.path.join(SRC, DIRS[repo])):
        dn[:] = [d for d in dn if d not in ("node_modules", ".git")]
        if "SKILL.md" in fn:
            n = name_of(os.path.join(dp, "SKILL.md"))
            if n in names and (n not in found or len(dp) < len(found[n])):
                found[n] = dp
    for n in names:
        assert n in found, (repo, n)
        if not os.path.isdir(os.path.join(out, n)):
            shutil.copytree(found[n], os.path.join(out, n))
        done.append(dict(skill=n, repo=repo))
json.dump({"claudeMdExcludes": [os.path.expanduser("~/.claude/CLAUDE.md"), "**/.claude/CLAUDE.md"]}, open(os.path.join(DST, ".claude", "settings.json"), "w"))
json.dump(done, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "sandbox-50.json"), "w"), indent=1)
print(len(done), "skills in", out)
