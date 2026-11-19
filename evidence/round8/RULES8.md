# Round 8: how often the finder's picks are on topic (written before the run, 18 Nov 2026)

No model call. The finder script (plugin 2.2.0) runs on 8 jobs in the round-6 test folder (50 public skills).

Jobs (the topic words the skill passes to the finder):
1. landing page website marketing html (the words the saved round-6 session passed; changed before the run from "landing page product")
2. slide deck presentation
3. blog post writing
4. code review pull request
5. short video animation
6. spreadsheet excel analysis
7. unit tests python
8. logo design brand

For each job the script saves:
- the installed skills the finder lists (up to 5)
- the GitHub list as the plugin prints it (limit 5)
- a wider GitHub pool (limit 15) from the same searches, to try other orderings on the same candidates

Rule for "on topic", fixed now:
- ON = the skill's own name or description says it makes or does the thing the job names.
- OFF = it does something next to the job (hosting, screenshots, psychology, a general collection, another file type) or the description does not name the job.
- Judge: one AI assistant, reading name + description. Not blind, one judge. This is a reading check, not proof of quality: nobody ran the skills.

Orderings compared on the wider pool (top 5 each):
- A stars: most stars first (what 2.2.0 does)
- B fit, then stars: most key words matched first, stars break ties
- C fit x log10(stars): share of key words matched times log10(stars + 10)

Reported: on-topic count out of the skills shown, per job and in total, for the installed list and for each GitHub ordering.
Limits known before the run: 8 jobs chosen before the run, not sampled; GitHub search results change by the day; one judge.
