# Round 9: a better matcher, tested so it cannot overfit (written before any run, 19 Nov 2026)

Goal: a more advanced matcher that really picks better, tested so it cannot overfit.

## What is compared
- **A = plugin 2.2.0 as shipped.** Claude turns the request into 3 to 5 topic words (the text of SKILL.md step 1). Finder: 2 shared key words needed, word score for installed skills, stars for GitHub. Top 5 each.
- **B = matcher 3, finder only.** Claude writes topic words plus up to 6 close words (other names, file types). Finder: word pairs count as terms ("landing page"), close words count half, BM25 with the usual constants (k1 1.5, b 0.75), GitHub order = reciprocal rank fusion of fit rank and stars rank (k 60). Top 5 each.
- **C = matcher 3 + keep step.** The finder hands Claude up to 8 installed and 12 GitHub skills; Claude keeps the ones whose description does the job, at most 5 each, in the finder's order.

## Jobs
- 36 requests written by Opus in one call. It is given 36 fields in everyday words (24 where the 50-skill test folder has a skill, 12 where it has none) and never sees a skill name or description.
- Split by a seeded shuffle (seed 9): 12 tuning jobs, 24 sealed jobs.
- The 8 round-8 jobs are "seen" jobs and are not counted in this round.

## Labels (the truth each arm is scored against)
- One Opus judge call per job for installed skills: it sees the request and all 50 skills (name + description) and lists the ones that would directly help do the request. It never sees any finder output.
- One Opus judge call per job for GitHub: it sees the request and every GitHub skill any arm listed (name + description, shuffled, no stars, no arm label) and marks each ON or OFF. ON = its own description says it makes or does the thing asked, or a named part of it. OFF = next to the job, one repository's private helper, hosting, a general collection.

## Guard against overfitting
1. Choices are made on the 12 tuning jobs only: the GitHub order (fit only, stars only, or the fusion), and bug fixes.
2. No word list, synonym table or job name goes into the code. Close words come from Claude at run time.
3. Constants are the textbook ones, fixed above, not searched.
4. Before the sealed run the matcher file's sha256 is written into this file. The sealed 24 are run once. No change after.
5. If a bug stops the sealed run, the fix and the rerun are logged here.

## What counts as better (set now)
On the sealed 24, C against A:
- GitHub on-topic share (ON / listed) up by 10 points or more, and ON picks per job not lower.
- Installed recall at 5 (fits listed / min(5, fits)) not lower, and installed on-topic share not lower by more than 5 points.
- Overfit flag: if the tuning-set gain in GitHub on-topic share is more than 15 points above the sealed gain, say so.
If these fail, 2.2.0 stays and the page says so. B is reported beside C to show how much comes from the math alone.

## Known limits, before the run
- The judge and the keep step are the same model (Opus). The keep step may agree with the judge because they think alike. B has no model in it and shows the gain without that.
- Opus writes the requests. The field names are mine, taken from the test folder's contents in everyday words.
- One judge, no human labels. GitHub results change by the day; all arms run the same hour and share one cache.
- Topic words are written in one batched call per arm, not one call per job.
- Spend cap for this round: $7. Every call must be answered by Opus or the run stops.

## Tuning log
- Iteration 1 (tuning 12 only; files kept as iter1_*): A GitHub on-topic 8/26, B 13/37 (fit order and fusion equal, stars order 10/37). Installed: A 10/16 on topic, recall 10/14; B 9/14, recall 9/14.
  Seen on the tuning jobs: (a) Claude put the user's product in the topic ("jira integration") and the kind of thing ("mcp server") in the close words, and the rule "one topic word must hit" then dropped mcp-builder; (b) close words carried the user's problem ("caching concurrency") and pulled in unrelated skills; (c) "deploy" did not match "deployment", "slide" did not match "slides".
  Changes, all general: step-1 wording (name the kind of thing, no words about their own problem), match rule = two topic words, or one topic word + one close word, or three close words, and a stemmer with more endings. No job word in the code.
- Iteration 2 (tuning 12, after the three changes; labels redone): GitHub on-topic A 6/26 (23%), B fusion 22/50 (44%), B fit order 24/50 (48%), B stars order 16/50 (32%), C 25/33 (76%). ON picks per job: A 0.50, B 1.83, C 2.08. Installed on-topic: A 9/16, B 9/16, C 9/11; recall at 5: 9/12 in all three.
  The same A lists scored 8/26 in the first labelling and 6/26 in the second: the judge moves by about 2 picks between runs.
  Order chosen: the fusion. Fit order was 2 picks ahead of it on 50, inside that judge noise, and the fusion keeps stars in the order (stars are the only trust signal the list has; the judge does not score trust).
- FROZEN before the sealed run, 2026-11-19T03:26Z. sha256:
find3.py: dcda6cc21e2cc9bddb7b7691a403f1944d7cdb138cb5d2403b840fc53501a59c
judge9.py: 075ddb4a307e94c2827870c336dfaf87353b61606b3a7deec10aa878dd2fea64
gen9.py: 0b1a3607aacf6bc05991b98f42a4300f3048528be2e2fb44ad7c47c9ac72839a

## Result on the sealed 24 (run once, 19 Nov 2026; sha256 of the three files unchanged after the run; no search was turned away)
| | A · 2.2.0 | B · matcher 3, math only | C · matcher 3 + keep step |
|---|---|---|---|
| GitHub picks on topic | 26/65 (40%) | 40/101 (40%) | 49/56 (88%) |
| On-topic GitHub picks per job | 1.08 | 1.67 | 2.04 |
| Jobs with no GitHub pick | 6 | 1 | 5 |
| Installed picks on topic | 12/20 (60%) | 14/28 (50%) | 14/14 (100%) |
| Installed fits found (recall at 5) | 12/19 (63%) | 14/19 (74%) | 14/19 (74%) |
Job by job, on-topic GitHub picks, C against A: better 13, worse 2, same 9.

Against the rule set before the run: GitHub on-topic share +48 points (needed +10), ON picks per job higher, installed recall higher, installed on-topic share higher. PASSED.
Overfit check: tuning gain 53 points (23% to 76%), sealed gain 48 points (40% to 88%); 5 points apart, under the 15-point flag.

What did not hold:
- The math alone (B) did not raise the on-topic share on the sealed jobs: 40% and 40%. On the tuning jobs it had looked like +21 points (23% to 44%). What B does on sealed jobs: more on-topic picks per job (1.08 to 1.67), more installed fits found (12 to 14 of 19), fewer jobs with an empty GitHub list (6 to 1), and more off-topic installed picks (8 to 14) until the keep step removes them.
- 5 of 19 installed fits are still missed (J25, J28, J31, J35).
- The judge and the keep step are both Opus. The 88% and the 100% may be flattered by that. No human labels.
Spend: $3.70 (75 Opus calls).
