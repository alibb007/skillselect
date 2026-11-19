<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/hero-dark.svg">
    <img src="assets/hero-light.svg" alt="Straight Answer: which skill to use, and how to use it. Short, finished answers too." width="100%">
  </picture>
</p>

<p align="center">
  <img src="assets/demo.gif" alt="Film: 50 installed skills pile into a mess when a person asks Claude to build a landing page. Plain Claude pulls out one skill, and four that fit stay unused. With the plugin, all 50 are read and scored, the 5 that fit are shown with when and how to use each, and 5 more are found on GitHub by stars (118,427 down to 61,257). Before and after: 1 of 5 fitting skills against 5 of 5, 27 steps against 1, 111 seconds against 24, 528,087 tokens against 46,725." width="100%">
</p>

<p align="center"><sub>The film is drawn from saved sessions in a test folder with 50 public skills. Asked to build a landing page, plain Claude loaded 1 of the 5 skills that fit in five of six runs. The plugin listed all 5 and 5 more from GitHub, each with when to use it and its command, in 1 step, 24 seconds and 46,725 tokens. Asking plain Claude the same question took 27 steps, 111 seconds and 528,087 tokens, one run each side. <a href="assets/demo.mp4">Download the clip</a>.</sub></p>

<p align="center">
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-2A78D6?style=flat-square"></a>
  <img alt="Claude Code plugin" src="https://img.shields.io/badge/Claude_Code-plugin-101A2B?style=flat-square">
  <img alt="Python 3, standard library only" src="https://img.shields.io/badge/python-3_·_standard_library_only-178A63?style=flat-square">
  <img alt="No telemetry" src="https://img.shields.io/badge/telemetry-none-5B6A80?style=flat-square">
</p>

You install a lot of skills, and then you forget which one does what. A better one may already be on GitHub, and you have no quick way to check. **Straight Answer** is a Claude Code plugin that tells you which skill to use for a job and how to use it. It also keeps every answer short.

## What it does

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/flow-dark.svg">
  <img src="assets/flow-light.svg" alt="When you have a job: you say it, the plugin checks what you have, then the best on GitHub, then tells you how to use the one it picks. On every request: one sentence is added for you, and you get a short answer you can use as it is." width="100%">
</picture>

Say the job. The plugin answers in three steps.

1. **What you have.** It reads the skills on your computer and names the ones that fit. Nothing about them leaves your machine.
2. **The best on GitHub.** It lists the skills that fit, with the most stars first. Each one shows its license and last update, with a warning when the repository is archived, has no license, or has had no update for a year.
3. **When and how to use each.** Every skill it lists comes with one line on when to use it for your request, and its command. A GitHub skill also gets the command to add it. Then it names one to start with, and a skill you already have wins over a download. The plugin never installs anything itself.

**Short, finished answers.** It also adds one sentence to every request for you:

> Use my exact facts and numbers, and give me a short, finished answer I can use as it is, with no placeholders, no generic templates and nothing I did not ask for.

## Use it

| You type | You get |
|---|---|
| `/straight-answer:find-skill turn my sales numbers into a slide deck` | The three steps for that job |
| `/straight-answer:my-skills` | Every skill you have, grouped by job, with its command and when to use it |
| `/straight-answer:my-skills pdf` | Only your skills that fit a topic |
| Nothing extra | A short, finished answer to every request |

## Install

In Claude Code:

```
/plugin marketplace add alibb007/straight-answer
/plugin install straight-answer@straight-answer
```

To try it without installing, clone the repository and start Claude Code with the folder:

```bash
git clone https://github.com/alibb007/straight-answer
claude --plugin-dir straight-answer
```

It needs Python 3. There is no account, no API key and no telemetry.

## One real run

This run is from 18 Nov 2026, in a test folder with 50 public skills from six repositories. I picked the 50 so that several fit the job. The plugin named the 5 that fit, listed 5 GitHub skills the folder did not have, and said when and how to use each. It took 24 seconds and one tool call.

<p align="center">
  <img src="assets/example-have.png" alt="Five cards, one for each installed skill that fits: landing-page-generator, landing, epic-design, copywriting and page-cro, each with when to use it and its command." width="100%">
</p>

<p align="center">
  <img src="assets/example-github.png" alt="Five GitHub skills by stars: design-taste-frontend 118,427, paperclip-page 114,811, screenshots-marketing 108,338, kami-landing 108,338, marketing-psychology 61,257, each with its license and when to use it." width="100%">
</p>

It matches your own skills by what each skill says about itself and shows up to five. On GitHub it opens the repositories that mention your topic and the largest skill collections, reads the skill folders inside them, keeps the ones that fit at least two of your key words, leaves out the ones you already have, and sorts the rest by stars. The how-to lines come from the skill's own file: its command, the packages and keys its instructions name, and its section titles.

Only the search words leave your machine, and they go to api.github.com. Nothing about your own skills is sent.

I also asked plain Claude to build a landing page in that folder, six times, without the plugin. It loaded 1 of the 5 skills that fit in five runs and 2 in one.

### What other finders miss

| Tool | Looks at what you already have | Names the skill inside a big repository | Leaves the installing to you |
|---|---|---|---|
| `npx skills find` | No | Searches its own hosted list, ranked by installs | Installs on select |
| skills-janitor discover | By folder name only | No, finds whole repositories | Yes |
| deep-skill-finder | No | Hosted market | Installs for you |
| **Straight Answer** | **Yes, by what the skill says** | **Yes** | **Yes** |

From their own docs and code, read on 18 Nov 2026. I did not run them.

## Proof

### Which skill, and how

I asked Claude Opus the same question for five jobs, once in plain words and once through the plugin: which skill should I use, and how do I use it? In the plain run Claude could search the web, use the `gh` command and read files.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/speed-dark.svg">
  <img src="assets/speed-light.svg" alt="Middle value of five jobs. Tokens per question: 179,393 without the plugin, 39,354 with it. Seconds to an answer: 93 without, 19 with. Tool calls: 14 without, 1 with. The plugin was lower in 5 of 5 jobs on all three." width="100%">
</picture>

The plugin passed 34 of 35 quality checks and plain Claude passed 33 of 35. The checks are: the right installed skill, three real repositories, no invented repository, stars, license or date, one recommendation, and how to call it. Plain Claude answers this question well. It needs 14 steps, 93 seconds and 179,393 tokens to get there, and the plugin needs 1 step, 19 seconds and 39,354 tokens.

### Short answers

I ran 42 everyday requests, and Claude Opus answered each one twice: once as written and once with the plugin's sentence added.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/proof-dark.svg">
  <img src="assets/proof-light.svg" alt="Words per answer 488 plain, 245 with the plugin. Answers with a blank: 6 of 42 plain, 0 of 42 with the plugin. Output tokens 1,946 plain, 1,447 with the plugin." width="100%">
</picture>

## Evidence

Everything behind the numbers is in the [evidence](evidence) folder: the rules written before each test, the requests, the answers, the verdicts and the scripts. Round 6 is the worked example in the clip. Round 7 counts the skills plain Claude loads on its own. Round 5 tested version 2.0.0 on the five jobs. Round 3 tested the sentence the plugin uses. Round 2 tested an earlier sentence without the word "short": the AI judge preferred it over a plain request 39 times to 8, and it cost 50% more output tokens.

## Limits

- I tested on one model, Claude Opus. The 42 requests were written by the same model.
- The five-job test is small, it ran on version 2.0.0, and I looked at the slide deck job while building the finder.
- The example in the clip is one run on each side. I ran the plugin side six times while fixing the finder, and the clip shows the sixth.
- The count of skills Claude loads on its own comes from six runs of one request. Those runs could not write files and stopped after ten turns.
- The finder runs when you call it by name. Asked in plain words, Claude did not always start it.
- The finder matches words. In the clip's example, three of the five GitHub skills do not build landing pages, and the plugin says so in each one's line. Read a skill before you add it.
- "It needs" lists what the skill's instructions name, found with fixed patterns. It can miss a requirement or list an optional one.
- An AI judge read all 42 short-answer pairs and preferred the longer answer 29 times to 7. In its notes it praises the extra advice. So the short answers are for people who want them short.
- Without a GitHub token the finder can run about two searches an hour.

## License

[MIT](LICENSE)
