# Round 15: three other judges, and no more switches that start off (written before any run, 24 Nov 2026)

## Why
1. In every round so far one model, Claude Opus, did both jobs: it kept the picks and it judged them. A model may agree with itself.
   This round judges the saved picks again with three other models: Claude Fable, Claude Sonnet and Claude Haiku.
2. 3.1 has two features that are off until someone switches them on: `read` and `hint`. A feature nobody switches on helps nobody.
   Each one is either merged into the default or taken out. The rules for that are set here, before the new labels exist.

## What is judged again
Only the judge step. Every saved pick stays as it is (`../round9/keep9_sealed.json`, `../round11/keep11_sealed.json`, `../round12/keep12.json`). No keep call is made.
- **Part 1, installed skills and round 9's GitHub skills, sealed 24.** Round 9's label prompt, word for word: all 50 installed skills (name and 400 characters of description) and the same GitHub candidates in the same shuffled order (`label9_sealed.json`, `github_judged`). One call per request per judge.
- **Part 2, round 12's GitHub picks.** Round 12's label prompt, word for word, the same candidates in the same shuffled order (`label12.json`, `judged`). One call per request that had a pick, per judge.
The judge sees no stars, no arm name and no earlier label.

Judges: Fable is the main one. Sonnet and Haiku run beside it. The model id that answered is saved with every label; a call answered by another model family stops the run.
Opus's saved labels are shown next to them. They are not run again.

## What counts (set now)
- **Agreement.** For every skill judged, each new judge against Opus: the share with the same ON/OFF and Cohen's kappa. No bar. It is reported.
- **Round 12's claims** hold under a judge when they pass round 12's own bars with that judge's labels: 3.1 with a login against 3.0.0, share of kept picks that are ON not lower by more than 5 points and ON picks per request not lower by more than 0.25; 3.1 offline at 70% of 3.0.0's ON picks per request or more.
- **Round 11's bar is not moved.** With Opus's labels reading found 15 of 19 fits and the bar was 16. That stays written as missed, whatever the new judges say. The number of fits is each judge's own, so 19 will change.

## `read`: merge or remove (set now)
`read` prints every other installed skill in one line so the keep step can add a fit that uses other words (round 11, arm D). Without it the keep step sees the word match's top list only (arm C).
- **Merge** (always printed, no switch) when all three hold on the sealed 24:
  1. by Fable's labels D finds more fits than C;
  2. by Fable's labels at least half of the skills added by reading are fits;
  3. by Sonnet's labels and by Haiku's labels D does not find fewer fits than C.
- **Otherwise remove** it: the code, the switch and the step in SKILL.md.
Known before the run: by Opus's labels D found 15 and C 14, and reading added 2 skills of which 1 is a fit. Two added skills is a thin base and the page will say so.
If merged, the size of the finder's printout with and without the list is measured on the 50-skill folder (no model call) and reported.

## `hint`: merge or remove (set now)
`hint` runs on every message and names installed skills that fit. It has never run in a live session.
- If less than $1.50 of the budget is left after the judging, it is **removed** without a live run and the page says it was never run live.
- Otherwise one live test decides. The 8 requests on which the hint speaks (round 14: 2 tuning, 6 sealed), each run twice with the hint and twice without, 32 sessions. Each is a real `claude -p` session on Claude Sonnet with plugin 3.1 loaded and the 50-skill folder, stopped after the assistant's first turn. The request is typed as a person would, without `/skillselect`.
  Counted: sessions whose first turn calls a skill that round 9's labels mark as a fit for that request.
  **Merge** (on by default, `hint off` turns it off) when the hint arm has at least 3 more such sessions than the no-hint arm, of 16. **Otherwise remove.**
The short-answer sentence is not part of this round. It stays as it is.

## Order of cuts if the money runs short
Budget left when this was written: $6.37 of the lab's $150. Cap for this round: $5.50.
After the first request of each judge the cost of the whole judging is worked out. If it is over $3.60: first the hint's live test is dropped, then part 2 for Haiku, then part 2 for Sonnet. Fable's two parts are never dropped.

## A failed answer is not an OFF
An answer that is not JSON is asked for once more. If it fails again, that request is left out for that judge and counted in the results. It is never scored as "nothing fits".

## Known limits, before the run
- Three Claude models are not a person. All four judges come from one maker. "No person has judged anything" stays on the page.
- The keep step is still Opus. What changes is that the judge is no longer the same model.
- This is the fourth use of the sealed 24. Nothing is tuned on them here.
- Rounds 1 to 8 and round 10 are not judged again. The token and time numbers on the front page still rest on round 10.
- The live hint test is 16 sessions a side on one model with 8 requests. It can show a large effect only.

## Frozen before the first call, 2026-11-25T06:30Z. sha256:
run15.py: a8b29a7c0ce93a2ad206d72f675ba0facd38f77f68ec4f53355a3c9a2945be11

## After the first request of each judge (before the rest ran)
Part 1 cost $0.122 a call on Fable, $0.025 on Sonnet, $0.002 on Haiku. Worked out for all of it: about $4.65, over the $3.60 line.
By the order of cuts the hint's live test is dropped. Haiku's and Sonnet's part 2 together cost about $0.25, so dropping them would not bring the total under the line; they stay, and the round's $5.50 cap is what stops the run.
`hint` is therefore removed without a live run.

## Result (run once, 24 Nov 2026; run15.py's checksum was the same after the run)
135 judge calls, none failed to parse: Fable `claude-fable-5-2` 45 calls $4.01, Sonnet `claude-sonnet-5-5` 45 calls $0.81, Haiku `claude-haiku-5-5` 45 calls $0.06. Before them, 3 one-word probes ($0.02) checked that each model answers. With one real session at the end ($0.22) the round cost $5.11. `score15.json` holds every number below.

### Agreement with Opus
| Judge | Installed and round 9 GitHub skills (1,419) | Round 12 picks (112) |
|---|---|---|
| Fable | 99.2% the same, kappa 0.94 | 89.3%, kappa 0.69 |
| Sonnet | 98.1%, kappa 0.83 | 81.2%, kappa 0.49 |
| Haiku | 98.2%, kappa 0.86 | 86.6%, kappa 0.50 |
The second set is harder by construction: every skill in it had already been kept by the keep step.

### Round 12 under each judge (kept picks: 3.0.0 59, 3.1 with a login 81, 3.1 offline 58)
| Judge | 3.0.0 ON, share, per request | 3.1 login | 3.1 offline | 3.1 login passes | offline passes |
|---|---|---|---|---|---|
| Opus (saved) | 49, 83.1%, 2.04 | 68, 84.0%, 2.83 | 49, 84.5%, 2.04 | yes | yes |
| Fable | 47, 79.7%, 1.96 | 61, 75.3%, 2.54 | 42, 72.4%, 1.75 | yes | yes |
| Sonnet | 44, 74.6%, 1.83 | 56, 69.1%, 2.33 | 43, 74.1%, 1.79 | **no**: share 5.5 points lower, bar 5 | yes |
| Haiku | 51, 86.4%, 2.12 | 71, 87.7%, 2.96 | 55, 94.8%, 2.29 | yes | yes |
3.1 with a login keeps more ON picks per request under all four (0.50 to 0.84 more) and more picks that are OFF as well (Fable: 20 against 12). By the main judge, Fable, it passes. By Sonnet it misses the share bar by half a point.
"Offline matches 3.0.0" holds for Opus only. Under Fable offline keeps 1.75 against 1.96.

### Round 9's keep step (3.0.0's front-page numbers) under each judge
GitHub picks that are ON, of 56 kept: Opus 49 (88%), Fable 48 (86%), Sonnet 40 (71%), Haiku 53 (95%). Installed picks that are fits: 14 of 14 under all four.

### Round 11 under each judge, and the `read` verdict
| Judge | Fits (its own count) | C found | D found | Added by reading that fit |
|---|---|---|---|---|
| Opus (saved) | 19 | 14 | 15 | 1 of 2 |
| Fable | 21 | 14 | 15 | 1 of 2 |
| Sonnet | 24 | 14 | 15 | 1 of 2 |
| Haiku | 15 | 14 | 14 | 0 of 2 |
Rule 1 (Fable: D finds more) yes. Rule 2 (Fable: half of the added skills fit) yes, 1 of 2. Rule 3 (Sonnet and Haiku: not fewer) yes. **Verdict: merge.**
The list is now always printed and the switch is gone. Step 3 of SKILL.md is back to the wording frozen in round 11 (sha256 f9ac9981…; the "When the finder printed" wording was added after that round, when the list became a switch).
The base is as thin as said above: one fit gained (`systematic-debugging` on J31, a fit for Opus, Fable and Sonnet) and one skill added that no judge calls a fit (`file-organizer` on J12).
Round 11's bar of 16 of 19 stays missed.

### `hint`: removed
The order of cuts dropped the live test after the first request of each judge, and $1.49 was left when the judging ended, under the $1.50 line. The hint was taken out without a live run. `../round14/hint_check.py` keeps its code and still gives the same numbers (9 skills named on 36 requests, 8 fits, silent on 24 small-talk lines).

### What the merged list costs (`printout_size.json`, `live15.json`)
- 36 requests, 50-skill folder, no model call: the finder's local printout is 925 characters on average without the list and 7,332 with it (the list: 6,407 characters, about 50 lines).
- One real session, same request and command as round 13's run B31: 34.5 s, 54,512 tokens, 1 tool call, $0.219. Round 13 without the list: 33.9 s, 52,381 tokens, $0.197. One run each. Nothing in that answer was marked "found by reading".

### Not done
- No keep step was run again, so nothing here says how Fable, Sonnet or Haiku would do as the model that follows the skill.
- The live GitHub lists were not made again. The change in this round touches the installed half only (the list and the removed hint). The offline arm was run again on the 24 requests and gives the same list as `../round12/recheck12.json` on 24 of 24 (`offline_recheck.json`, no network, no model). `../round14/checks.py` was run again end to end and every check but the test count (62, now 61) is unchanged.
- The planted-order runs of round 13 were made before the list was always printed.
- Lab ledger after this round: $148.72 of $150.
