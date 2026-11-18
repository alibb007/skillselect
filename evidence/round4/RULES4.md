# Round 4 rules (written 18 Nov 2026, before any round-4 run)

Question: a person wants to know which skill to use for a job. How much work is that without the plugin and with it?

## Setup
A clean project folder with 19 public skills installed (anthropics/skills). Claude Opus, Claude Code headless.
Five jobs, each with one installed skill that is the right answer:
slide deck from sales numbers (pptx), financial model in a spreadsheet (xlsx), fill in and merge PDF forms (pdf),
landing page design (frontend-design), test a web app in the browser (webapp-testing).

- WITHOUT: the person asks in plain words: "I want to <job>. Which skill should I use? Tell me which of my installed skills
  fit, what else is available on GitHub (with stars, license and last update), and recommend one. Do not install anything."
  The assistant may use web search, web fetch, the gh command, and read files.
- WITH: the person types "/straight-answer:find-skill <job>". Plugin v1.0.x from the public repo.

## Measured per run (from the session log, not estimated)
tokens (input + output, cache included), cost, seconds, number of tool calls (steps).

## Quality, 6 checks, each pass/fail, scored by a script written before the runs
1. names the right installed skill
2. names at least 3 GitHub repositories that really exist (checked with the GitHub API)
3. names no repository that does not exist
4. shows stars for the options
5. shows license or last update for the options
6. gives one clear recommendation
Plus a safety check: no install, clone or download command was run.

## What may be claimed
Per measure, the median of the five jobs for each side, and how many of the five went the same way. Five jobs is a small
test and is said so. Whatever comes out is reported, including if the plugin is slower, dearer or scores lower.
Cap for this round: $18. Every call must be claude-opus-*.

## Changes after the smoke run on the first job (deck), 18 Nov 2026, before the other four jobs ran
- The scorer miscounted: it called "color/font" an invented repository and missed star counts written as "32.5k" in a table.
  Checks 2 to 5 now work line by line on the repositories that really exist. Check 3 only counts a github.com link or a
  repo-shaped name at the start of a table row or list item.
- The smoke run showed two plugin faults, fixed in v1.1.0 before the full run: the finder returned nothing when the request
  carried extra detail words ("quarterly sales numbers"), and it took about 40 s. Now two key words are enough to fit,
  the skill tells the assistant to pass topic words, and requests run in parallel (9 s cold).
- So the deck job was used for tuning. It is still reported, and marked.
- 45 s pause between plugin runs, to stay under GitHub's 30 searches a minute.
- finder v1.1.0 also retries when GitHub asks it to slow down and runs 3 searches at a time; first fixed deck-B run was refused 8 of 10 searches because my own manual tests had used the minute's quota. deck-B is rerun with the others.
