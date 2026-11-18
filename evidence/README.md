# Evidence

| Folder | Sentence tested | Requests | Files |
|---|---|---|---|
| [round3](round3) | The one the plugin uses (short, finished) | 42 | `RULES3.md` (written first), `CONCLUSION3.md`, `requests.json`, `answers.json`, `verdicts.json`, `results.json`, scripts |
| [round2](round2) | Earlier sentence, without "short" | 60 | `RULES2.md` (written first), `CONCLUSION2.md`, `requests.json`, `answers.json`, `checks.json`, `verdicts.json`, `results.json`, scripts |
| [round4](round4) | The finder: same question without the plugin and with it | 5 jobs | `RULES4.md` (written first), `results.json` (tokens, seconds, steps, 6 quality checks per run), `finder-deck.json`, scripts |
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
| Model | every call answered by `claude-opus-5-5` |
| Names | some drafted messages are signed "Ali": the account name the model could see |
| Ledgers | `ledger-round2.jsonl`, `ledger-round3.jsonl`: one line per model call with cost and tokens |
