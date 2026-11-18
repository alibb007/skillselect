<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/hero-dark.svg">
    <img src="assets/hero-light.svg" alt="Straight Answer: short, finished AI answers, and the right skill for the job" width="100%">
  </picture>
</p>

<p align="center">
  <img src="assets/demo.gif" alt="Demo: a user asks which skill to use for a slide deck. Without the plugin the assistant takes 10 steps, 44 seconds and 158,088 tokens. With Straight Answer it takes 1 step, 19 seconds and 38,622 tokens, lists pptx as installed, shows GitHub options by stars and recommends pptx. Across five jobs it used 5.1 times fewer tokens, was 3 times faster, and passed 29 of 30 quality checks against 30 of 30." width="100%">
</p>

<p align="center"><sub>This is one question, asked without the plugin and with it, on the same clock. Across five jobs the plugin used 5 times fewer tokens (38,622 against 198,288) and answered 3 times faster (19 seconds against 55), in 1 step instead of 10. It passed 29 of 30 quality checks, and plain Claude passed 30 of 30. <a href="assets/demo.mp4">Download the clip</a>.</sub></p>

<p align="center">
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-2A78D6?style=flat-square"></a>
  <img alt="Claude Code plugin" src="https://img.shields.io/badge/Claude_Code-plugin-101A2B?style=flat-square">
  <img alt="Python 3, standard library only" src="https://img.shields.io/badge/python-3_·_standard_library_only-178A63?style=flat-square">
  <img alt="No telemetry" src="https://img.shields.io/badge/telemetry-none-5B6A80?style=flat-square">
</p>

AI answers are too long, and the right skill is hard to find. **Straight Answer** is one Claude Code plugin that fixes both. Install it once and keep asking the way you already do.

## What it does

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/flow-dark.svg">
  <img src="assets/flow-light.svg" alt="Every request gets one sentence added for a short, finished answer. When you need a skill, the plugin checks your own skills, then GitHub, and gives you a list." width="100%">
</picture>

**Short, finished answers.** It adds one sentence to every request for you:

> Use my exact facts and numbers, and give me a short, finished answer I can use as it is, with no placeholders, no generic templates and nothing I did not ask for.

**Finds a skill for the job.** Say what you want to make. It checks the skills you already have, then lists the ones on GitHub with the most stars first, each with its license and last update. It installs nothing.

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

## Proof

I ran 42 everyday requests, and Claude Opus answered each one twice: once as written and once with the plugin's sentence added.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/proof-dark.svg">
  <img src="assets/proof-light.svg" alt="Words per answer 488 plain, 245 with the plugin. Answers with a blank: 6 of 42 plain, 0 of 42 with the plugin. Output tokens 1,946 plain, 1,447 with the plugin." width="100%">
</picture>

## The finder

This is a real run from 18 Nov 2026. Ask in your own words, or call it by name with `/straight-answer:find-skill`.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/finder-dark.svg">
  <img src="assets/finder-light.svg" alt="Request: I want to create a video motion graphic. Results from GitHub, most stars first: heygen-com/hyperframes 86,483, nexu-io/openmotion 11,769, Vincentwei1021/anything2explainer 3,398, alchaincyf/huashu-motion 2,874, Tejashmakwana/motionmaxxing 1,663, each with license and last update. Nothing installed." width="100%">
</picture>

It looks at your own skills first and matches them by what each skill says about itself. Then it searches GitHub: it opens the repositories that mention your topic and the largest skill collections, reads the skill folders inside them, keeps the ones that fit at least half of your key words, and sorts them by stars. Each result shows the license and the last update, with a warning when a repository is archived, has no license, or has had no update for a year. It ends with one recommendation, and a skill you already have wins over a download.

Only the search words leave your machine, and they go to api.github.com. Nothing about your own skills is sent.

### What other finders miss

| Tool | Looks at what you already have | Names the skill inside a big repository | Leaves the installing to you |
|---|---|---|---|
| `npx skills find` | No | Searches its own hosted list, ranked by installs | Installs on select |
| skills-janitor discover | By folder name only | No, finds whole repositories | Yes |
| deep-skill-finder | No | Hosted market | Installs for you |
| **Straight Answer** | **Yes, by what the skill says** | **Yes** | **Yes** |

From their own docs and code, read on 18 Nov 2026. I did not run them.

## Evidence

Everything behind the numbers is in the [evidence](evidence) folder: the rules written before each test, all requests, every answer, every verdict, and the scripts. Round 3 tested the sentence the plugin uses. Round 2 tested an earlier sentence without the word "short": the AI judge preferred it over a plain request 39 times to 8, and it cost 50% more output tokens.

## Limits

- Tested on one model, Claude Opus, with requests written by the same model.
- An AI judge read all 42 pairs and preferred the longer answer 29 times to 7. In its notes it praises the extra advice. So this plugin is for people who want the short answer.
- The finder matches words, so a search for a legal contract review also returned smart-contract skills. Read a skill before you add it.
- Without a GitHub token the finder can run about two searches an hour.
- The speed and token test covers five jobs on one model, and the first job was also used to tune the finder.

## License

[MIT](LICENSE)
