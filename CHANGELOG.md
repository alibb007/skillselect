# Changelog

## 1.0.0

First public release.

- `/skillselect <what you want to build>` lists the installed skills that fit, with when and how to use each, and up to 5 public skills from GitHub with the line that adds each one.
- `/skillselect categorize` sorts the skills you have into categories.
- Counts only skills that are installed and switched on, and names the agent each belongs to (Claude Code, Codex, Cursor).
- Works without a GitHub login: a list of 4,136 public skills from 80 repositories ships with it, and `--offline` sends nothing.
- Treats skill text as data: descriptions are quoted, and a skill whose text gives orders to the assistant is left out or flagged.
- A `skillselect` command for any terminal (`pip install`), with add lines for Codex and Cursor (`--for codex|cursor`).
- One sentence added to every request for short, finished answers. `/skillselect short off` turns it off.
- 81 tests, run on Python 3.9, 3.11 and 3.13.
