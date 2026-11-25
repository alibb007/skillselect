"""Shared helpers: load the finder from its file, and build a throwaway home folder with skills in it."""
import importlib.util
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FINDER = os.path.join(ROOT, "skills", "skillselect", "scripts", "find_skills.py")
HOOK = os.path.join(ROOT, "hooks", "short_answer.py")


def load(path=FINDER, name="find_skills"):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def fs():
    return load()


def skill(folder, name, desc, extra=""):
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "SKILL.md"), "w") as f:
        f.write("---\nname: %s\ndescription: %s\n%s---\n\n# %s\n\nbody\n" % (name, desc, extra, name))


@pytest.fixture()
def home(tmp_path, monkeypatch):
    """A fake home: 1 personal skill, 1 plugin switched on, 1 switched off, 1 only in a catalog, 1 old copy, Codex and Cursor skills."""
    h = tmp_path / "home"
    proj = tmp_path / "project"
    proj.mkdir(parents=True)
    c = h / ".claude"
    skill(str(c / "skills" / "alpha"), "alpha", "Builds a landing page as one HTML file.")
    cache = c / "plugins" / "cache" / "m1"
    skill(str(cache / "p1" / "1.0" / "skills" / "beta"), "beta", "Writes a slide deck presentation.")
    skill(str(cache / "p1" / "0.9" / "skills" / "beta-old"), "beta-old", "An older copy of the slide deck skill.")
    skill(str(cache / "p2" / "2.0" / "skills" / "zeta"), "zeta", "Reviews a pull request diff.")
    for p, v in (("p1", "1.0"), ("p1", "0.9"), ("p2", "2.0")):
        d = cache / p / v / ".claude-plugin"
        d.mkdir(parents=True, exist_ok=True)
        (d / "plugin.json").write_text(json.dumps({"name": p}))
    market = c / "plugins" / "marketplaces" / "m1" / "plugins"
    skill(str(market / "p3" / "skills" / "gamma"), "gamma", "Designs a landing page hero section.")
    (market / "p3" / ".claude-plugin").mkdir(parents=True)
    (market / "p3" / ".claude-plugin" / "plugin.json").write_text(json.dumps({"name": "p3"}))
    skill(str(market / "p1" / "skills" / "beta"), "beta", "Writes a slide deck presentation.")
    (market / "p1" / ".claude-plugin").mkdir(parents=True)
    (market / "p1" / ".claude-plugin" / "plugin.json").write_text(json.dumps({"name": "p1"}))
    (c / "plugins" / "installed_plugins.json").write_text(json.dumps({"version": 2, "plugins": {
        "p1@m1": [{"scope": "user", "installPath": str(cache / "p1" / "1.0"), "version": "1.0"}],
        "p2@m1": [{"scope": "user", "installPath": str(cache / "p2" / "2.0"), "version": "2.0"}]}}))
    (c / "settings.json").write_text(json.dumps({"enabledPlugins": {"p1@m1": True, "p2@m1": False}}))
    skill(str(h / ".codex" / "skills" / "delta"), "delta", "Makes a spreadsheet from a CSV file.")
    skill(str(h / ".cursor" / "skills" / "eps"), "eps", "Explains a stack trace.")
    monkeypatch.setenv("HOME", str(h))
    monkeypatch.delenv("SKILL_FINDER_ONLY", raising=False)
    monkeypatch.delenv("SKILL_FINDER_DIRS", raising=False)
    monkeypatch.delenv("SKILLSELECT_SHORT", raising=False)
    monkeypatch.delenv("SKILLSELECT_HINT", raising=False)
    monkeypatch.delenv("SKILLSELECT_CONFIG", raising=False)
    monkeypatch.chdir(proj)
    return h
