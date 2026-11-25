# Round 12: is the GitHub half still as good with the shipped list, and how good is it with no network at all? (written before any run, 24 Nov 2026)

## Why
3.1 adds a list of public skills from 80 repositories (4,191 when this round ran, built 25 Nov 2026 UTC) so the finder answers without a GitHub login.
With a login the list is merged into the live search. Offline the list is all there is. Both could make the GitHub picks worse. This round checks.

## What is compared, on the 24 sealed requests of round 9
- **A = 3.0.0 as published** (commit a688e60), with a GitHub login.
- **B = 3.1, with a GitHub login**: live search plus the shipped list.
- **C = 3.1 with `--offline`**: the shipped list only. No call to GitHub.
Same topic and close words for all three (`../round9/wordsB.json`). The same 50 skill names count as "already installed". A and B run back to back on one cache, so they see the same GitHub answers.

## Steps
1. `run12.py find`: the three finders on the 24 requests. No model call.
2. `run12.py keep`: for each arm and request, one Opus call keeps up to 5 of the finder's GitHub list. The prompt is round 9's keep prompt, word for word, for all three arms, so only the finder differs.
3. `run12.py label`: for each request, one Opus call marks every skill any arm kept as ON or OFF. Round 9's label prompt, word for word. The list is shuffled and carries no stars and no arm name.

## What counts (set now)
- **B against A:** share of kept picks that are ON not lower by more than 5 points, and ON picks per request not lower by more than 0.25. Round 9 measured the judge moving by about 2 picks in 12 requests between two runs, which is 0.17 a request.
- **C against A:** it is a fallback. It passes if its ON picks per request are at least 70% of A's.
If B fails, the list is used only when there is no login. If C fails, the page says how much worse offline is.

## Known limits, before the run
- The keep step and the judge are the same model, Opus, as in round 9. No person labelled anything.
- This is the third use of the sealed 24. Nothing in the finder is tuned on them in this round: the code is frozen below before step 1.
- GitHub changes by the day. A and B share one cache; C has no live part.
- Spend cap for this round: $4. Every call must be answered by Opus or the run stops.

## Frozen before step 1, 2026-11-25T04:26Z. sha256:
find_skills.py: c30f70ab1348b66b42a0173fd1f328fbc86f227043f8bb29f3a2e542febe4f48
index.json.gz: 3115f8bd8163e8ed2f4b0f50761cb001279b666737ac87fba5718798273f9da9
run12.py: da19cb42c7c4fb35391862ebe182419da62a633e8568fe3ce8b6b183ac5399e4

## Result on the sealed 24 (run once, 24 Nov 2026; the finder's checksum was the same after step 1; no search was turned away)
| | A · 3.0.0, login | B · 3.1, login | C · 3.1, offline |
|---|---|---|---|
| GitHub skills listed by the finder | 170 | 241 (137 from the shipped list) | 208 (all from the list) |
| Kept by the keep step | 59 | 81 | 58 |
| Kept picks that are ON | 49 (83.1%) | 68 (84.0%) | 49 (84.5%) |
| ON picks per request | 2.04 | 2.83 | 2.04 |
| Requests with no pick | 5 | 3 | 6 |
| GitHub calls made | live | live | 0 |

**B passed:** the share is level (84.0% against 83.1%) and it keeps 0.79 more ON picks per request, well above the 0.17 the judge moves by.
**C passed:** with no call to GitHub it keeps as many ON picks per request as 3.0.0 does with a login (2.04 and 2.04; the bar was 70% of A).
91 Opus calls (70 keep: two lists were empty; 21 label: three requests had nothing kept), $1.78. 112 skills were labelled, 91 ON.

## After the run: the finder changed, so the lists were made again (recheck12.json, no model call)
Three changes went into the finder after step 1: it no longer lists itself, a skill name that mixes alphabets is left out, and skill files inside test folders are skipped. The shipped list was rebuilt without the 56 test-folder files (4,136 skills).
Arms B and C were run again on the same 24 requests against the same cache (30 calls were not in it any more and went to GitHub).
- B: the same list on 21 of 24 requests. C: on 22 of 24.
- Of the picks the judge scored, 1 of B's 81 and 0 of C's 58 are no longer listed.
The numbers above are from the frozen finder. The shipped one differs from it by one judged pick.

## Before publishing (24 Nov 2026)
One line of `run12.py` changed after the run: it now loads the harness from `../harness` (or `$SKILLSELECT_LAB`) and no longer from a folder on my computer. Nothing else changed. Its checksum is now 21f431f0a89818ac4c8f7ba53ade6c5bd8417b399bd007a1f3a7c565159589fd, so it no longer matches the one frozen above.

## After a code review (24 Nov 2026, `../round15/login_recheck.json`, no model call)
A review before release changed how the shipped list joins the live search: a repository opened live used to lose all its list entries, and now loses only the skills that were read live. Arm B was run again on the 24 requests with a login (7 calls were not in the cache).
- 79 of B's 81 judged picks are still listed (the 2 that are not were both ON). 12 skills are listed that were not before; no judge has seen them.
- The list is the same, in the same order, on 10 of 24 requests.
- Arm C (offline) is unchanged: the same list on 24 of 24.
The numbers in the result table above are from the frozen finder.
