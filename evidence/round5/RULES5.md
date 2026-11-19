# Round 5 rules (written 18 Nov 2026, before any round-5 run)

Question: a person has many skills and wants to know which one to use for a job and how to use it.
How much work is that without the plugin and with plugin v2.0.0?

## Setup (same as round 4)
A clean project folder with 19 public skills installed (anthropics/skills). Claude Opus, Claude Code headless.
The same five jobs, each with one installed skill that is the right answer:
slide deck from sales numbers (pptx), financial model in a spreadsheet (xlsx), fill in and merge PDF forms (pdf),
landing page design (frontend-design), test a web app in the browser (webapp-testing).

- WITHOUT: the person asks in plain words: "I want to <job>. Which skill should I use, and how do I use it? Tell me which
  of my installed skills fit, what else is available on GitHub (with stars, license and last update), recommend one, and
  tell me how to use it. Do not install anything." The assistant may use web search, web fetch, the gh command, and read files.
- WITH: the person types "/straight-answer:find-skill <job>". Plugin v2.0.0 from the public repo folder.

## Measured per run (from the session log, not estimated)
tokens (input + output, cache included), cost, seconds, number of tool calls (steps), words in the answer.

## Quality, 7 checks, each pass/fail, scored by a script written before the runs
1 to 6 are the round-4 checks, same code: right installed skill named; at least 3 GitHub repositories that really exist;
no repository that does not exist; stars shown; license or last update shown; one clear recommendation.
7. says how to call the recommended skill: the answer has the right skill as a slash command ("/pptx"), or one of the
   phrases "just ask", "in your own words", "automatically", "invoke", "trigger".
Plus the safety check: no install, clone or download command was run.

## What may be claimed
Per measure, the median of the five jobs for each side, and how many of the five went the same way. Five jobs is a small
test and is said so. Whatever comes out is reported, including if the plugin is slower, dearer or scores lower.
The finder was changed for v2.0.0 using the deck request by hand (output format only), so deck is again marked as seen.
A smoke run on deck comes first to check the scorer; any scorer change after it is written below, with the reason.
Cap for this round: $6. Every call must be claude-opus-*.

## Changes after the runs, 18 Nov 2026
- Safety check: the scorer flagged landing-A because a web-fetch question contained the words "plugin install". Nothing was
  installed. The check now looks only at shell commands that were run. No other score changed.
- Models: the main model in all ten runs was claude-opus-5-5. In the WITHOUT runs Claude Code's own web-fetch tool also used
  claude-haiku-5-5 to summarise pages (deck, landing, model). Its cost is in that run's cost. Its tokens are not in
  the token count, so the WITHOUT token numbers are a little low.
- In the WITHOUT runs the assistant also read skill files from the account's synced skills folder, outside the test folder.
  Those paths are replaced by a placeholder in results.json.
