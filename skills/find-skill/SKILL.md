---
name: find-skill
description: Use when the user wants to do a task and no skill already loaded clearly covers it, or when they ask to find, suggest or recommend a skill for something ("I want to create a motion graphic video", "is there a skill for slide decks?", "find me a skill for X"). Checks the skills already on this computer first, then searches public GitHub and lists the skills that fit with the most stars first, each with its license and last update. Never installs anything.
---

# Find a skill

1. Put what the user wants into 3 to 8 plain words, in their own terms.
2. Run the finder by its full path (this skill's base directory + `scripts/find_skills.py`). Do not `cd` first:

   `python3 "<base directory>/scripts/find_skills.py" "<those words>"`

3. Show the user what came back, short:
   - **Already on this computer**: if one fits, say so first and offer to use it now. Do not send them to GitHub for something they own.
   - **On GitHub**: keep the order (most stars first). For each: name, repository, stars, license, last update, link. Drop any result that is plainly about something else (the search matches words, not meaning) and say you dropped it.
   - Pass on the warnings as written: "no license", "archived", "no update for a year".
4. Stop there. Never install, clone, download or copy a skill yourself. The user picks; then they add it, or tell you to.

The finder sends only the search words to api.github.com. It reads the skills on this computer locally and sends nothing about them. No account is needed; without a GitHub token it can run about two searches an hour.
