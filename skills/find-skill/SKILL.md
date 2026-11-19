---
name: find-skill
description: Use when the user wants to do a task and no skill already loaded clearly covers it, or when they ask which skill to use, how to use a skill, or to find, suggest or recommend a skill for something ("I want to create a motion graphic video", "which skill do I use for slide decks?", "find me a skill for X"). Reads every skill installed on this computer and picks the ones that fit, adds the best ones on public GitHub by stars, and says when and how to use each. Never installs anything.
argument-hint: <what you want to do>
---

# Find a skill, and how to use it

1. Put what the user wants into 3 to 5 topic words: the kind of thing they want, another common name for it, and the field or file type it belongs to (for "turn my quarterly sales numbers into a slide deck": `slide deck presentation pptx`; for "write a blog post about our launch": `blog post article writing`). Leave out their own details such as dates, amounts and names.
2. Run the finder by its full path (this skill's base directory + `scripts/find_skills.py`). Do not `cd` first:

   `python3 "<base directory>/scripts/find_skills.py" "<those words>"`

3. Show the user what came back, short, in the finder's three steps. For every skill you list, add one line on when to use it for what they asked, taken from the skill's own description, and its command as the finder printed it:
   - **1. What you have**: the installed skills that fit, and how many are installed in total. Per skill: when to use it for this request, then its `call` line.
   - **2. On GitHub**: keep the order (most stars first). Per skill: name, repository, stars, license, last update, link, when to use it for this request, then its `add` and `call` lines. Pass on the warnings as written: "no license", "archived", "no update for a year". If a skill is plainly about something else (the search matches words, not meaning), say so in its line.
   - **3. Start with this one**: the finder's one pick and its reason, then what it needs. A skill they already have wins over a download.
4. If the user picks a different one, get its how-to: `python3 "<base directory>/scripts/find_skills.py" --how "<its name, or its GitHub link>"`.
5. Stop there. Never install, clone, download or copy a skill yourself. The user runs the add command, or tells you to.

The finder sends only the search words to api.github.com. It reads the skills on this computer locally and sends nothing about them. No account is needed; without a GitHub token it can run about two searches an hour.
