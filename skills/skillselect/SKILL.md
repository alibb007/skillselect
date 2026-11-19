---
name: skillselect
description: Use when the user wants to do a task and it is not clear which installed skill covers it, or asks which skill to use, when or how to use a skill, or to find or recommend a skill ("which skill do I use for slide decks?", "find me a skill for X"), or asks what skills they have ("categorize my skills"). Reads every skill installed on this computer, scores each against the request, adds the best-fitting ones on public GitHub, keeps only the ones that do the job, and says when and how to use each. Never installs anything.
argument-hint: <what you want to do> | categorize
---

# SkillSelect

Run the finder by its full path (this skill's base directory + `scripts/find_skills.py`). Do not `cd` first.

## If the user typed `categorize`, typed nothing, or asked what skills they have

1. Run `python3 "<base directory>/scripts/find_skills.py" --mine`
2. Answer under the heading **Your N skills by category** (N = the number the finder printed).
   - Group the skills by the job they do, with a plain category name (web pages, documents, code quality, writing, and so on).
   - In each category, one line per skill: its command, then what it is for in under 12 words, taken from its own description.
   - With more than 40 skills, show each category with its count and its three most useful commands, and say they can ask for one category in full.
   - Pass on the "In more than one place" line as written: copies of one skill can disagree.
3. Change nothing. Never delete, move or edit a skill. Stop here.

## Otherwise: the user wants to do something

1. Put what the user wants into 2 to 4 topic words that name the kind of thing or the kind of work they are asking for, in the order people say them, not what their own project is about (for "turn my quarterly sales numbers into a slide deck": `slide deck`; for "review my pull request that changes our session cache": `code review`; for "connect our assistant to our ticket system": `mcp server`). Then add up to 6 close words: other common names for that same kind of thing, and the file types or tools it usually means (`presentation pptx powerpoint slides`; `pull request pr diff`). No words about their particular problem, product or data.
2. Run `python3 "<base directory>/scripts/find_skills.py" "<topic words>" --also "<close words>"`
3. From the finder's two lists keep only the skills whose own description says they do what the person asked: they make the thing, or a named part of it. Drop skills that only sit next to the job (hosting, screenshots, checking some other kind of work), skills written for one repository or one product's own code, and general collections. Keep at most 5 from each list, in the finder's order. If fewer than 5 do the job, keep fewer; an empty list is a fine answer.
4. Show the result short, in this shape:

   **On your computer** (K of N installed fit)
   - **skill-name**
     When: one sentence on when to use it for this request, taken from its own description.
     How: its `how` line as the finder printed it.
     Needs: only when the finder printed a `needs` line.

   **On GitHub** (K you do not have)
   - **skill-name** · repository · stars · license · last update · link
     When: one sentence on when to use it for this request.
     Add: its `add` line as the finder printed it.
     How: its `how` line.
     Needs: only when the finder printed one.

   **Start with** one skill and one short reason. A skill they already have wins over a download.

   Pass on the finder's warnings as written ("no license", "archived", "no update for a year"). If you dropped candidates, say how many in one line.
5. Stop there. Never install, clone, download or copy a skill yourself. The user runs the add command, or tells you to.

The finder contacts GitHub only: it sends the search words to api.github.com and reads public skill files from raw.githubusercontent.com. If the `gh` command is signed in or `GITHUB_TOKEN` is set, it sends that token to GitHub's API with its searches. It reads the skills on this computer locally and sends nothing about them. No account is needed; without a GitHub token, GitHub allows 60 API calls an hour, enough for a few requests.
