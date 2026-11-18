---
name: find-skill
description: Use when the user wants to do a task and no skill already loaded clearly covers it, or when they ask to find, suggest or recommend a skill for something ("I want to create a motion graphic video", "is there a skill for slide decks?", "find me a skill for X"). Lists the skills already installed on this computer that fit, then the ones available on public GitHub with the most stars first, and recommends one. Never installs anything.
---

# Find a skill

1. Put what the user wants into 3 to 8 plain words, in their own terms.
2. Run the finder by its full path (this skill's base directory + `scripts/find_skills.py`). Do not `cd` first:

   `python3 "<base directory>/scripts/find_skills.py" "<those words>"`

3. Show the user what came back, short, in this order:
   - **Installed on this computer**: the skills they already have that fit, and how many are installed in total.
   - **Available on GitHub**: keep the order (most stars first). For each: name, repository, stars, license, last update, link. Pass on the warnings as written: "no license", "archived", "no update for a year".
   - **Recommended**: the finder's one pick and its reason. A skill they already have wins over a download. If the pick is plainly about something else (the search matches words, not meaning), say so and name the next one that fits.
4. Stop there. Never install, clone, download or copy a skill yourself. The user picks; then they add it, or tell you to.

The finder sends only the search words to api.github.com. It reads the skills on this computer locally and sends nothing about them. No account is needed; without a GitHub token it can run about two searches an hour.
