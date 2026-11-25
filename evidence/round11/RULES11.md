# Round 11: does reading every installed skill find the fits the word match misses? (written before any run, 24 Nov 2026)

## The problem
On the 24 sealed requests of round 9, the word match listed 14 of the 19 installed skills the judge had marked as fits.
The 5 it missed share no topic word with the request (for "cli app": brainstorming, test-driven-development).
A check-up on 24 Nov found the same on a real computer: "landing page" missed frontend-design, 0 shared words.

## What is compared
- **C = round 9's keep step, as saved** (`../round9/keep9_*.json`): Claude sees the finder's top 8 installed skills and keeps up to 5. No new call.
- **D = 3.1's keep step.** Claude sees the same top list as the 3.1 finder prints it, plus every other installed skill in one line (name and the first 110 characters of its description), and may add up to 3 of those, marked "found by reading". One Opus call per request, no tools. The system prompt is step 3 of the 3.1 SKILL.md, word for word.

Same 36 requests, same topic and close words (`../round9/wordsB.json`), same 50-skill test folder, same labels (`../round9/label9_*.json`).

## What counts as better (set now)
On the sealed 24, D against C:
- fits found: at least 2 more of the 19 (16 or more), and
- kept skills that are fits: 85% or more (C: 14 of 14).
If D fails, the page says so and the list stays only as an option.

## Guard against overfitting
1. Wording of step 3 may change after the 12 tuning requests only. Every change is logged below.
2. Before the sealed run, the sha256 of the finder and of the step-3 text is written here. The sealed 24 run once.
3. The labels are round 9's. No relabelling.

## Known limits, before the run
- The labels were written by Opus reading all 50 descriptions. D lets Opus read all 50 one-liners. The two may agree because they are the same model, so a high score flatters D. No person labelled anything.
- The sealed 24 were used once before, in round 9, for a different change. This is their second use.
- 50 skills is a small folder. With 300 installed skills the list is cut to 150 lines.
- D can keep up to 8 skills where C kept up to 5. No request has more than 5 fits.
- Spend cap for this round: $4. Every call must be answered by Opus or the run stops.

## Tuning log
- Before any run I had already seen which installed fits the word match misses on BOTH sets (the offline check prints them). Five of the sealed misses are planning and debugging skills. That is why the first wording of step 3 let Claude add "the way of working this job plainly needs". It is a leak from the sealed set into the wording, and it is written here so nobody has to find it.
- Iteration 1 (tuning 12, first wording): D found 11 of 12 fits (C: 9), but kept 18 skills of which 11 are fits (61%; C: 9 of 11, 82%). Reading added 7 skills and 2 were fits. Four of the five wrong ones were brainstorming or test-driven-development added to "landing page", "mcp server" and "browser game". Spend $0.41.
  Change: the clause about ways of working is taken out, and the step now says not to add one unless the request asks for that kind of help. This follows the tuning set and goes against what the sealed misses would reward.
- Iteration 2 (tuning 12, second wording): D found 12 of 12 fits, kept 15 of which 12 are fits (80%; C: 82%). Reading added 4 skills and 3 were fits. Spend $0.40. No further change.
- FROZEN before the sealed run, 2026-11-25T04:13Z. sha256:
find_skills.py: bcab0afee85b395e59ba1c74ab54c24b2cb0be63912dd5bcc9696bfa9a9293d7
step 3 of SKILL.md: f9ac9981953eaa57f80f9db750d2f5f078bf94675d05e779011598f66e3129c5
run11.py: e869a4b94eb04c5dee1c99566d7b02c86d084ed8609dcb8049f030f4dead7e8e

## Result on the sealed 24 (run once, 24 Nov 2026; the three checksums unchanged after the run)
| | C · round 9 keep step | D · 3.1 keep step with the one-line list |
|---|---|---|
| Installed fits found | 14 of 19 | 15 of 19 |
| Kept skills that are fits | 14 of 14 (100%) | 15 of 16 (94%) |
| Added by reading | | 2, of which 1 is a fit |
Tuning 12 for comparison: C 9 of 12 (9 of 11 kept), D 12 of 12 (12 of 15 kept).

**D did not clear the bar set above** (16 or more fits found; it found 15). Its kept share passed (94% against 85%).
The four fits still missed are brainstorming (3 requests) and test-driven-development (1): ways of working, which the tuned step leaves out on purpose.
As written before the run, the list is an option and not the default: `--list` on one request, or `read on` for all.
Spend: $1.57 for 48 calls (12 + 12 tuning, 24 sealed), all answered by Opus.

## Before publishing (24 Nov 2026)
One line of `run11.py` changed after the run: it now loads the harness from `../harness` (or `$SKILLSELECT_LAB`) and no longer from a folder on my computer. Nothing else changed. Its checksum is now 0ba0a81c43f98d6e75e04bb19398022b735320cba04789d7913a48af12a5b1ec, so it no longer matches the one frozen above.
