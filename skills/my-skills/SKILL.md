---
name: my-skills
description: Use when the user asks what skills they have, which of their own skills to use for something, when to use a skill they installed, or says they have too many skills to keep track of ("what skills do I have?", "which of my skills is for PDFs?", "I installed a lot of skills and forgot what they do"). Lists the skills on this computer with the command for each and when to use it. Sends nothing anywhere.
argument-hint: [topic]
---

# What you have, and when to use it

1. Run the finder that ships with this plugin by its full path. It sits in the `find-skill` skill next to this one (this skill's base directory, then `../find-skill/scripts/find_skills.py`). Do not `cd` first:

   `python3 "<base directory>/../find-skill/scripts/find_skills.py" --mine`

   If the user named a topic, add it as 2 to 4 topic words: `--mine pdf forms`.
2. Show the result short:
   - First line: how many skills are installed.
   - Group them by the job they do (documents, slides, data, design, code, writing, and so on), with a plain group name. In each group, one line per skill: its command, then when to use it in under 12 words taken from its own description.
   - With more than 40 skills, show each group with its count and its three most useful commands, and say they can ask for one group in full.
   - Pass on the "in more than one place" line as written: copies of one skill can disagree.
3. For one skill in detail (what it needs, what it covers): `python3 "<base directory>/../find-skill/scripts/find_skills.py" --how "<skill name>"`.
4. Change nothing. Never delete, move or edit a skill.

Everything is read on this computer. Nothing is sent anywhere.
