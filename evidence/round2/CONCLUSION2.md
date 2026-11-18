# Round 2 conclusion (18 Nov 2026)

686 model calls, all claude-opus-5-5, $33.53, no STOP. Rules: RULES2.md, written before the first request existed.

The sentence, pasted under the request:
"Use my exact facts and numbers, and give me a finished answer I can use as it is, with no placeholders or generic templates."

| Rule | Result | Verdict |
|---|---|---|
| R2 AI judge prefers answers with the sentence | 39 with, 8 as written, 13 no clear winner (sign test p = 0.00001). Two plain runs against each other: 5 - 6 - 9 | holds |
| R3 the wording matters (vs a generic "be thorough" line) | 37 sentence, 14 generic line, 9 no clear winner (p = 0.002) | holds |
| R1 uses more of the person's details | 232 of 240 as written (96.7%), 237 of 240 with the sentence (98.8%). Gap 2.1 points, needed 5 (p = 0.29) | does not hold |
| R4 no extra cost | 3,018 output tokens against 2,014 (+50%). Answers 21% longer in characters (3,559 vs 2,946) | does not hold |

Reported whichever way (fixed pattern): answers that left a square-bracket blank such as [Name] or [Invoice #]:
11 of 60 as written (32 blanks), 1 of 60 with the sentence (3 blanks), 13 of 60 with the generic line (58 blanks).

By area (with / no clear winner / as written): office 6-2-2, small business 6-2-2, home 7-2-1, money and travel 5-3-2,
study 6-4-0, health and hobbies 9-0-1.

What may be said: with the sentence the AI judge preferred the answer 39 times to 8, a generic "try harder" line did not do
the same, and blanks left to fill in almost disappeared. What may not be said: that it makes the model use more of your
details (it already used 97%), or that it is free (about 50% more output tokens).

Limits: Opus judged Opus. Opus wrote the requests. Text only, no tools. One model. The author's own blind votes are collected on
the judging page and are not in this file yet.

Round 1's "no extra cost" does not carry over: that was a different wording, added by a hook inside Claude Code.
