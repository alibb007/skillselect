"""Fix 1: count only what is really installed, and say which agent each skill belongs to."""
import json
import subprocess
import sys

from conftest import FINDER


def by_name(skills):
    return {s["name"]: s for s in skills}


def test_states_and_agents(fs, home):
    got = by_name(fs.local_skills())
    assert got["alpha"]["state"] == "installed" and got["alpha"]["agent"] == "Claude Code"
    assert got["beta"]["state"] == "installed" and got["beta"]["plugin"] == "p1"
    assert got["zeta"]["state"] == "off"            # the plugin is installed and switched off
    assert got["gamma"]["state"] == "catalog"        # only in a marketplace list
    assert got["delta"]["agent"] == "Codex" and got["delta"]["state"] == "installed"
    assert got["eps"]["agent"] == "Cursor"
    assert "beta-old" not in got                     # an old version folder left in the cache


def test_catalog_copy_of_an_installed_plugin_is_not_listed_twice(fs, home):
    betas = [s for s in fs.local_skills() if s["name"] == "beta"]
    assert len(betas) == 1 and betas[0]["state"] == "installed"


def test_installed_total_counts_only_installed(fs, home):
    out = subprocess.run([sys.executable, FINDER, "--mine", "--json"], capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    assert d["installed_total"] == 4                 # alpha, beta, delta, eps
    assert d["by_agent"] == {"Claude Code": 2, "Codex": 1, "Cursor": 1}
    assert d["switched_off"] == 1 and d["in_catalogs"] == 1
    assert {s["name"] for s in d["skills"]} == {"alpha", "beta", "delta", "eps"}


def test_rank_uses_installed_only_and_lists_the_rest_apart(fs, home):
    out = subprocess.run([sys.executable, FINDER, "landing page", "--also", "html hero", "--no-online", "--json"],
                         capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    assert d["installed_total"] == 4
    assert [s["name"] for s in d["local"]] == ["alpha"]
    assert [s["name"] for s in d["nearby"]] == ["gamma"]
    assert d["nearby"][0]["get"] == "/plugin install p3@m1"


def test_switched_off_plugin_says_how_to_turn_it_on(fs, home):
    out = subprocess.run([sys.executable, FINDER, "pull request", "--also", "diff review", "--no-online", "--json"],
                         capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    assert d["local"] == []
    assert d["nearby"][0]["name"] == "zeta" and d["nearby"][0]["get"] == "/plugin enable p2@m1"


def test_without_the_install_record_only_the_newest_cache_copy_counts(fs, home):
    (home / ".claude" / "plugins" / "installed_plugins.json").unlink()
    got = by_name(fs.local_skills())
    assert "beta" in got and "beta-old" not in got


def test_text_output_names_the_agent_and_the_real_count(fs, home):
    out = subprocess.run([sys.executable, FINDER, "spreadsheet csv", "--no-online"], capture_output=True, text=True, check=True).stdout
    assert "of 4 installed skills" in out
    assert "agent: Codex" in out
