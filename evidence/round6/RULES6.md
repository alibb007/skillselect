# Round 6 rules (written 19 Nov 2026 UTC, before the run)

Purpose: one worked example for the demo clip. It is a demonstration, not a test: one job, one run per side.

Setup: a project folder with 50 public skills from six public repositories (`sandbox-50.json`, built by `make_sandbox.py`).
The set was put together by hand so that several installed skills fit the job. Claude Opus, Claude Code headless, plugin v2.1.0.
Job: "build a landing page for my product".
- WITHOUT: the round-5 plain question with this job.
- WITH: "/straight-answer:find-skill build a landing page for my product".
Measured from the session log: tokens, seconds, tool calls, cost, words. No quality score in this round.
What may be claimed: what this one run showed, named as one run. The five-job numbers stay those of round 5 (plugin 2.0.0).
Cap: $2. Main model must be claude-opus-*.

## Changes after the first run of the WITH side
- The first run (kept as raw/landing-B-first.jsonl) listed 5 installed skills of 50, and only 3 GitHub skills: the assistant's
  topic words were "landing page website html" and few skill repositories name those words.
- Finder changed before the rerun (v2.1.0): it shows up to five installed fits, leaves GitHub skills you already have out of
  the list, opens more repositories whose own description names two key words, and may show a second fitting skill from one
  repository. The skill file now asks for the field of the job among the topic words (its example is a different job).
- So this job was used to tune the finder. The WITH side is run again once; that run is the one shown.
- Second run (kept as raw/landing-B-second.jsonl): 5 installed, 5 on GitHub, but the GitHub list put closer fits before
  higher stars, under a heading that says "most stars first". The list is now sorted by stars only (and shows only close fits
  when there are enough of them). Run a third time; that run is the one shown.
- Third run (kept as raw/landing-B-third.jsonl): the finder returned 4 GitHub skills. One repository's two best fits were
  skills already installed, and the finder dropped the repository instead of taking its next fit. Fixed. Run a fourth time;
  that run is the one shown. Four runs of one job: this is a worked example, tuned on this job, and is said so.

## Plugin 2.2.0, 19 Nov 2026 UTC
- The plugin now gives, for every skill it lists, when to use it for the request and its command (and for a GitHub skill the
  command to add it). The fourth run is kept as raw/landing-B-fourth.jsonl. The WITH side is run a fifth time on 2.2.0; that
  run is the one shown. The WITHOUT side is the same run as before.
- The spend guard stopped the fifth run before it started: round 7 ($2.80) had been counted against round 6's $2 cap. Nothing
  ran. The round-6 counter was reset to the current total, with a new $2 cap for this one rerun.
- Fifth run (kept as raw/landing-B-fifth.jsonl): every skill came with when to use it and its command, but the finder returned
  4 GitHub skills for the words "landing page website html". The finder now fills a short list from the repositories it has
  already read (repositories with 50 stars or more), most stars first. Run a sixth time; that run is the one shown.
