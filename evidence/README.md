# Evidence

| Folder | What was tested | Size | Files |
|---|---|---|---|
| [round15](round15) | Three other judges (Claude Fable, Sonnet, Haiku) on the saved picks of rounds 9, 11 and 12; `read` merged into the default and `hint` removed by rules set first; one real session with the merged list | 24 requests, 3 judges, 135 judge calls | `RULES15.md` (written first, cost decision, result), `label15_fable.json`, `label15_sonnet.json`, `label15_haiku.json`, `score15.json`, `printout_size.json`, `live15.json`, `offline_recheck.json`, scripts |
| [round14](round14) | 3.0.0 against 3.1 on public material: install count, hostile folder names, planted text, false alarms, GitHub calls without a login, tests | 6 checks, no model call | `checks.py`, `checks.json`, `count_calls.py` with both call logs, `hint_check.py` (the hint was removed in round 15; the script keeps its code) |
| [round13](round13) | 3.1 in real sessions, and a planted order, 3 runs a side | 9 runs | `RULES13.md` (written first, result at the end), `results.json`, script |
| [round12](round12) | GitHub picks: 3.0.0 with a login, 3.1 with a login, 3.1 offline, on the 24 sealed requests | 24 requests, 3 arms | `RULES12.md` (written first, checksums, result), `raw12.json`, `keep12.json`, `label12.json`, `score12.json`, script |
| [round11](round11) | Reading every installed skill in one line, against round 9's keep step | 36 requests | `RULES11.md` (written first, tuning log, checksums, result: bar not cleared), `keep11_tune.json`, `keep11_sealed.json`, scores, script |
| [round10](round10) | SkillSelect 3.0.0: the short command and `categorize`, real runs in the 50-skill test folder | 4 runs | `RULES10.md` (written first, with one addition after the first run), `results.json`, `landing-session.json` (the session the film is drawn from), `categorize-session.json`, script |
| [round9](round9) | The new matcher against plugin 2.2.0, scored on labelled requests: 12 for tuning, 24 sealed | 36 requests | `RULES9.md` (written first, with the tuning log, the frozen checksums and the result), `jobs.json`, the words, the raw lists, the labels, the kept lists, the scores, scripts |
| [round8](round8) | Plugin 2.2.0, finder alone: how many listed skills are on topic | 8 jobs | `RULES8.md` (written first), `raw8.json`, `judged8.json`, script |
| [round3](round3) | The sentence SkillSelect adds to every request (short, finished) | 42 | `RULES3.md` (written first), `CONCLUSION3.md`, `requests.json`, `answers.json`, `verdicts.json`, `results.json`, scripts |
| [round2](round2) | Earlier sentence, without "short" | 60 | `RULES2.md` (written first), `CONCLUSION2.md`, `requests.json`, `answers.json`, `checks.json`, `verdicts.json`, `results.json`, scripts |
| [round7](round7) | No plugin: which installed skills plain Claude loads when asked to build a landing page | 6 runs | `RULES7.md` (written first), `results.json`, script |
| [round6](round6) | Plugin 2.2.0: the worked example in the clip, one run without the plugin and one with it | 1 job | `RULES6.md` (written first, with every change after), `sandbox-50.json` (the 50 public skills), `results.json`, `landing-B-session.json` (the session the clip is drawn from), scripts |
| [round5](round5) | Plugin 2.0.0: which skill and how to use it, without the plugin and with it | 5 jobs | `RULES5.md` (written first), `results.json` (tokens, seconds, steps, 7 quality checks per run), `deck-B-session.json` (the session the demo clip is drawn from), scripts |
| [round4](round4) | Plugin 1.1.0: which skill, without the plugin and with it | 5 jobs | `RULES4.md` (written first), `results.json` (tokens, seconds, steps, 6 quality checks per run), `finder-deck.json`, scripts |
| [harness](harness) | | | `lab.py`: one model call, model check, spend log |

Rounds 4 to 7 ran when the plugin was called Straight Answer. Their files keep that name and its old command.


| Key in the data | Meaning |
|---|---|
| `A` | request as written |
| `S` | request + the short sentence (round 3) |
| `B` | request + the round-2 sentence |
| `C` | request + a generic "be thorough" line (round 2) |
| `A2` | request as written, second run (round 2, noise check) |

| Note | |
|---|---|
| Model | round 15: judges `claude-fable-5-2`, `claude-sonnet-5-5`, `claude-haiku-5-5`, the id saved with every label. All other rounds: every call answered by `claude-opus-5-5`; in round 5, Claude Code's own web-fetch tool also used `claude-haiku-5-5` in three of the runs without the plugin (see `round5/RULES5.md`) |
| Names | some drafted messages are signed "Ali": the account name the model could see |
| Ledgers | `ledger-round2.jsonl`, `ledger-round3.jsonl`: one line per model call with cost and tokens |
