<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/hero-dark.svg">
    <img src="assets/hero-light.svg" alt="SkillSelect: which of your skills to use, when and how. Finds more on GitHub. Never installs anything." width="100%">
  </picture>
</p>

**You install many skills and Claude uses one.** SkillSelect is a Claude Code plugin that reads every skill on your computer, scores each one against what you asked for, and tells you which to use, when and how. It also finds skills on GitHub that fit your request. It never installs anything. It also runs from any terminal, so it works beside Codex and Cursor too.

<p align="center">
  <img src="assets/demo.gif" alt="Film: installed skills pile up. A person asks Claude to build a landing page and Claude picks one skill. SkillSelect reads all 50 installed skills, scores them, shows the 4 that fit with when and how to use each, and finds 5 more on GitHub. Then token usage, time and steps, with and without SkillSelect." width="100%">
</p>

<p align="center"><sub>The film is drawn from saved runs in a test folder with 50 public skills. Asked to build a landing page, plain Claude loaded 1 of the skills that fit in 5 of 6 runs. SkillSelect listed 4 installed skills and 5 from GitHub, each with when and how to use it. <a href="assets/demo.mp4">Download the clip</a>.</sub></p>

<p align="center">
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-2A78D6?style=flat-square"></a>
  <img alt="Claude Code plugin" src="https://img.shields.io/badge/Claude_Code-plugin-101A2B?style=flat-square">
  <img alt="Python 3, standard library only" src="https://img.shields.io/badge/python-3_·_standard_library_only-178A63?style=flat-square">
  <a href="https://github.com/alibb007/skillselect/actions/workflows/tests.yml"><img alt="Tests" src="https://github.com/alibb007/skillselect/actions/workflows/tests.yml/badge.svg"></a>
  <img alt="No telemetry" src="https://img.shields.io/badge/telemetry-none-5B6A80?style=flat-square">
</p>

> - **Problem.** People install dozens of agent skills. Asked for a job, the assistant loads one and leaves the rest unused.
> - **What it does.** You type what you want to build. SkillSelect tells you which of your installed skills fit, when to use each one and the exact command. It adds up to 5 public skills from GitHub.
> - **How it works.** A two-stage retrieval pipeline in plain Python: query expansion, BM25 with field weights, rank fusion of fit and GitHub stars, then a re-rank step by the model.
> - **Result.** On 24 sealed requests, 15 of the 16 installed skills it suggested did the job. One real request used 90% fewer tokens than asking without the plugin.

## Start in 3 steps

**1. Install it with one line.** This needs Claude Code 2.1.275 or later.

```
/plugin install skillselect --marketplace alibb007/skillselect
```

On an older version, use two lines:

```
/plugin marketplace add alibb007/skillselect
/plugin install skillselect@skillselect
```

**2. Type what you want to build.**

```
/skillselect build a landing page
```

**3. Read which of your skills fit, and when and how to use each.** You also get up to 5 more from GitHub, each with the command to add it. You run that command yourself.

A second command sorts the skills you already have into categories:

```
/skillselect categorize
```

It needs Python 3.9 or later. SkillSelect never uploads your skills and never installs or deletes anything. There is no login, no paid API and no telemetry. It contacts GitHub only: the search words go to api.github.com, and public skill files are read from raw.githubusercontent.com. If the `gh` command is signed in or `GITHUB_TOKEN` is set, the finder sends that token to GitHub's API with its searches, as `gh` itself would. With `--offline` it sends nothing.

To try it without installing, clone the repository and start Claude Code with the folder:

```bash
git clone https://github.com/alibb007/skillselect
claude --plugin-dir skillselect
```

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/flow-dark.svg">
  <img src="assets/flow-light.svg" alt="When you have a job: you type /skillselect and the job, SkillSelect scores your skills, adds GitHub skills, and keeps what does the job with when and how for each. On every request: one sentence is added for you, and you get a short answer you can use as it is." width="100%">
</picture>

## What you get

- **Only what is installed.** The finder reads Claude Code's install record and the list of plugins that are switched on. A skill in a switched-off plugin, or in a plugin list you never installed from, is shown apart with the line that gets it. Skills of Codex and Cursor carry their agent's name.
- **A reason for every pick.** Each skill shows the words of your request it shares.
- **When and how.** One line on when to use the skill, the command that calls it, and what it needs when its own file names a requirement.
- **Skills on GitHub.** Up to 5 that you do not have, each with its stars, license, last update and the line that adds it. You run that line yourself.
- **No GitHub login needed.** A list of 4,136 public skills from 80 repositories ships with SkillSelect. With `--offline` it answers from that list and sends nothing.
- **Skill text is treated as data.** Descriptions are printed as quotes. A GitHub skill whose text gives orders to the assistant is left out, and an installed one is flagged. In a test with a planted order it warned the person in 3 of 3 runs.
- **Short answers.** One sentence is added to every request, so the answer comes back short and finished. `/skillselect short off` turns it off, and `/skillselect settings` shows the switch.

## Without Claude Code

```bash
pipx install git+https://github.com/alibb007/skillselect
skillselect "landing page" --also "html hero" --for codex
```

The command prints the same two lists. `--for codex` or `--for cursor` writes the add lines for that assistant's skill folder. `--offline` sends nothing and answers from the shipped list. To use it as a skill there, copy the `skills/skillselect` folder into `~/.codex/skills` or `~/.cursor/skills`.

## How it picks

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/pipeline-dark.svg">
  <img src="assets/pipeline-light.svg" alt="Retrieval pipeline in four lanes. LLM layer: request, query expansion. Local index: term model, candidate gate, BM25F score, top 8. Remote index: GitHub search, fetch skills, gate and BM25F, rank fusion, top 12. LLM layer: re-rank, answer. Counts on the arrows: 50 skills, 5 pass, 73 repos, 106 files, 30 pass." width="100%">
</picture>

Read it as a U. The request goes in at the top left and the answer comes out at the bottom left. The counts on the arrows are from one run of "landing page" in the 50-skill test folder. 5 of the 50 installed skills passed the gate. On GitHub, 73 repositories led to 106 skill files, and 30 of them passed.

1. **Query expansion.** Claude turns your request into 2 to 4 topic words and up to 6 close words: other names for the same thing, and its file types.
2. **Term model.** Words are cut to their stems. Two words side by side also count as a pair, so "landing page" is a term of its own. A topic word or a pair has weight $w = 1$, and a close word has $w = 0.5$.
3. **Candidate gate.** A skill becomes a candidate when it shares two topic words with the request, or one topic word and one close word, or three close words. A request has $C$ topic words and $E$ close words. A skill that shares $c$ and $e$ of them passes when $c + 0.5e \ge \min(1.5, C + 0.5E)$. The gate skips skills. It never skips your request. A skill that shares one common word, such as "page", would only add noise.
4. **Fit score.** Each candidate gets a BM25 score. A rare word counts more than a common one, repeating a word helps less each time, and a word in the skill's name counts 3 times.
5. **GitHub.** The finder sends up to 13 searches to the GitHub API. It opens the repositories that mention your topic and the largest skill collections, and reads the skill files inside them. Those skills pass the same gate and get the same score.
   **The shipped list.** 4,136 skills from the 80 most-starred skill collections ship with the plugin: name, 240 characters of description, stars, license and last update on the build day. With a login the list is merged into the live search. Without one, the finder opens at most 3 repositories live and takes the rest from the list.
6. **Rank fusion.** Each GitHub skill has a place by fit and a place by stars, and the two places are fused into one number. A famous repository with a weak fit cannot lead, and a perfect fit that nobody has starred cannot lead either. At most 2 skills per repository are listed.
7. **Re-rank.** Claude reads the top 8 installed and the top 12 GitHub descriptions. It keeps at most 5 from each list, and only skills whose own description says they do the job.
   The finder also prints every other installed skill in one line. Claude may add up to 3 of them when a skill's own line says it does the job, because a skill can fit and share no word with the request.
8. **Text is data.** Names and descriptions are cleaned of hidden characters and printed as quotes. A skill whose text talks to the assistant, or whose name mixes alphabets to look like another name, is left out of the GitHub list. Skill files inside test folders are skipped. On 6,414 public descriptions this check flagged 2: a poisoned test skill from a security scanner's own test folder (NVIDIA/SkillSpector), and one false alarm.

```math
\mathrm{fit}(s) \;=\; \sum_{t \in q} w_t \cdot \mathrm{idf}(t) \cdot \frac{\mathrm{tf}(t,s)\,(k_1 + 1)}{\mathrm{tf}(t,s) + k_1 \left(1 - b + b\,\dfrac{|s|}{\mathrm{avgdl}}\right)}
```

```math
\mathrm{idf}(t) \;=\; \ln\left(1 + \frac{N - \mathrm{df}(t) + 0.5}{\mathrm{df}(t) + 0.5}\right)
```

```math
\mathrm{order}(s) \;=\; \frac{1}{k + r_{\mathrm{fit}}(s)} + \frac{1}{k + r_{\mathrm{stars}}(s)}
```

Here $q$ is the request's terms and $w_t$ is the weight of term $t$. $`\mathrm{tf}(t,s)`$ is how often $t$ occurs in the text of skill $s$, with its name counted 3 times. $|s|$ is the length of that text and $`\mathrm{avgdl}`$ is the average length. $N$ is the number of skills and $`\mathrm{df}(t)`$ is how many of them contain $t$. $`r_{\mathrm{fit}}(s)`$ and $`r_{\mathrm{stars}}(s)`$ are the skill's place by fit and its place by stars. The constants are the textbook ones: $k_1 = 1.5$, $b = 0.75$ and $k = 60$.

BM25 with field weights follows Robertson and Zaragoza (2009). Reciprocal rank fusion with $k = 60$ follows Cormack, Clarke and Büttcher (2009). The design is the usual retrieve, then re-rank. The finder is Python 3 with the standard library only, and the matcher holds no topic word list and no tuned number.

## Tested

Claude Opus wrote 36 everyday requests without seeing any skill name or description. 12 were for tuning and 24 were sealed. Each test had its pass rule written first, and the sealed requests ran once per test. Four AI models then judged which skills do each job: Claude Opus, Fable, Sonnet and Haiku. The rules, requests, lists, labels and scripts are in [evidence](evidence).

| Judge | Installed skills it suggested that do the job | Installed fits it found | GitHub skills it suggested that do the job | GitHub, per request | Offline, per request |
|---|---|---|---|---|---|
| Opus | 15 of 16 | 15 of 19 | 68 of 81 (84%) | 2.83 | 2.04 |
| Fable | 15 of 16 | 15 of 21 | 61 of 81 (75%) | 2.54 | 1.75 |
| Sonnet | 15 of 16 | 15 of 24 | 56 of 81 (69%) | 2.33 | 1.79 |
| Haiku | 14 of 16 | 14 of 15 | 71 of 81 (88%) | 2.96 | 2.29 |

Each judge counts the fits its own way, so the third column has four different totals.

### What one request costs

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/numbers-dark.svg">
  <img src="assets/numbers-light.svg" alt="Token usage: 528,087 without SkillSelect, 54,512 with it, 90% fewer. Time to get the answer: 1 min 51 s without, 34 s with, 69% less. Steps to find your skills: 27 without, 1 with, 96% fewer." width="100%">
</picture>

I ran `/skillselect build a landing page for my product` in a test folder with 50 public skills. It took 1 step, 34.5 seconds and 54,512 tokens.

The side without the plugin is one run. Plain Claude was asked which skills to use and how, with web search and the `gh` command. It took 27 steps, 111 seconds and 528,087 tokens.

I also asked plain Claude to build the landing page in that folder six times, without the plugin. It loaded 1 skill in five runs and 2 in one.

### Short answers

SkillSelect also adds one sentence to every request, so the answer comes back short and finished. In a test of 42 requests the answers had half the words (245 against 488), and none had a blank left to fill in (0 of 42 against 6 of 42).

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/proof-dark.svg">
  <img src="assets/proof-light.svg" alt="Words per answer: 488 for a plain request, 245 with SkillSelect. Answers with a blank: 6 of 42 plain, 0 of 42 with SkillSelect. Output tokens per answer: 1,946 plain, 1,447 with SkillSelect." width="100%">
</picture>

## Limits

- No person has labelled the test requests. All four judges are Claude models, and Claude Opus also does the re-rank step.
- 4 of the 19 installed skills that fit were still missed. By Fable's count it is 6 of 21, by Sonnet's 9 of 24 and by Haiku's 1 of 15.
- Claude Opus wrote the 36 test requests, and I chose the fields they cover.
- The cost numbers are one run on each side, on one request. The seconds depend on GitHub.
- The GitHub lists changed a little after they were judged. 79 of the 81 judged picks are still listed, and 12 listed skills have not been judged.
- The finder runs when you call it by name. Asked in plain words, Claude does not always start it.
- "Needs" lists what a skill's instructions name, found with fixed patterns. It can miss a requirement or list an optional one.
- The terminal command and the skill folder were tested from a terminal. I have not run them inside Codex or Cursor.
- With more than 150 other skills installed, the one-line list is cut at 150.
- Nothing is installed for you. Read a skill before you add it, because it is text your assistant will trust.
- Without a GitHub login the finder takes most of the GitHub list from the shipped list, and that list is as old as its build day.

## License and credit

SkillSelect is free to use, copy and change under the [MIT license](LICENSE). Keep the license notice with its copyright line when you copy or reuse it. A mention of SkillSelect or of Ali B.B with a link to this repository is welcome too.

The shipped list holds the names and short descriptions of 4,136 public skills, each with its repository, license and link. Those texts belong to their authors. 3 of the 80 repositories state no license and 5 are unclear, and the finder marks their skills that way.

The evidence files quote short descriptions of public skills so the tests can be checked. Each one is named with its repository, and those texts belong to their authors. This repository does not include any of those skills.

Claude and Claude Code are trademarks of Anthropic, and GitHub is a trademark of GitHub, Inc. SkillSelect is an independent project. It is not affiliated with or endorsed by either company.

The software comes without warranty, as the license says. The numbers on this page are from the tests in [evidence](evidence), and they describe those tests only.
