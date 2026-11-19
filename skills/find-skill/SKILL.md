---
name: find-skill
description: Use when the user wants to do a task and no skill already loaded clearly covers it, or when they ask which skill to use, how to use a skill, or to find, suggest or recommend a skill for something ("I want to create a motion graphic video", "which skill do I use for slide decks?", "find me a skill for X"). Checks the skills already installed on this computer, then the ones on public GitHub with the most stars first, recommends one, and says how to use it. Never installs anything.
argument-hint: <what you want to do>
---

# Find a skill, and how to use it

1. Put what the user wants into 3 to 5 topic words: the kind of thing they want, plus one or two other common names or the file type for it (for "turn my quarterly sales numbers into a slide deck": `slide deck presentation pptx`). Leave out their own details such as dates, amounts and names.
2. Run the finder by its full path (this skill's base directory + `scripts/find_skills.py`). Do not `cd` first:

   `python3 "<base directory>/scripts/find_skills.py" "<those words>"`

3. Show the user what came back, short, in the finder's three steps:
   - **1. What you have**: the installed skills that fit, and how many are installed in total.
   - **2. On GitHub**: keep the order (most stars first). For each: name, repository, stars, license, last update, link. Pass on the warnings as written: "no license", "archived", "no update for a year".
   - **3. Recommended, and how to use it**: the finder's one pick and its reason, then its how-to lines as written: the command to call it, what it needs, and for a GitHub skill the command to add it. A skill they already have wins over a download. If the pick is plainly about something else (the search matches words, not meaning), say so and name the next one that fits.
4. If the user picks a different one, get its how-to: `python3 "<base directory>/scripts/find_skills.py" --how "<its name, or its GitHub link>"`.
5. Stop there. Never install, clone, download or copy a skill yourself. The user runs the add command, or tells you to.

The finder sends only the search words to api.github.com. It reads the skills on this computer locally and sends nothing about them. No account is needed; without a GitHub token it can run about two searches an hour.
