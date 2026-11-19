# Evidence

| Folder | Sentence tested | Requests | Files |
|---|---|---|---|
| [round3](round3) | The one the plugin uses (short, finished) | 42 | `RULES3.md` (written first), `CONCLUSION3.md`, `requests.json`, `answers.json`, `verdicts.json`, `results.json`, scripts |
| [round2](round2) | Earlier sentence, without "short" | 60 | `RULES2.md` (written first), `CONCLUSION2.md`, `requests.json`, `answers.json`, `checks.json`, `verdicts.json`, `results.json`, scripts |
| [round6](round6) | Plugin 2.1.0: the worked example in the clip, one run without the plugin and one with it | 1 job | `RULES6.md` (written first, with every change after), `sandbox-50.json` (the 50 public skills), `results.json`, `landing-B-session.json` (the session the clip is drawn from), scripts |
| [round5](round5) | Plugin 2.0.0: which skill and how to use it, without the plugin and with it | 5 jobs | `RULES5.md` (written first), `results.json` (tokens, seconds, steps, 7 quality checks per run), `deck-B-session.json` (the session the demo clip is drawn from), scripts |
| [round4](round4) | Plugin 1.1.0: which skill, without the plugin and with it | 5 jobs | `RULES4.md` (written first), `results.json` (tokens, seconds, steps, 6 quality checks per run), `finder-deck.json`, scripts |
| [harness](harness) | | | `lab.py`: one model call, model check, spend log |

| Key in the data | Meaning |
|---|---|
| `A` | request as written |
| `S` | request + the short sentence (round 3) |
| `B` | request + the round-2 sentence |
| `C` | request + a generic "be thorough" line (round 2) |
| `A2` | request as written, second run (round 2, noise check) |

| Note | |
|---|---|
| Model | every call answered by `claude-opus-5-5`; in round 5, Claude Code's own web-fetch tool also used `claude-haiku-5-5` in three of the runs without the plugin (see `round5/RULES5.md`) |
| Names | some drafted messages are signed "Ali": the account name the model could see |
| Ledgers | `ledger-round2.jsonl`, `ledger-round3.jsonl`: one line per model call with cost and tokens |
