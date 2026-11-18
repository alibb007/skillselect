# Round 3 conclusion (18 Nov 2026)

300 model calls, all claude-opus-5-5, $11.03, no STOP. Rules: RULES3.md, written before the first request existed.

Short sentence, pasted under the request:
"Use my exact facts and numbers, and give me a short, finished answer I can use as it is, with no placeholders, no generic
templates and nothing I did not ask for."

| Rule | Result | Verdict |
|---|---|---|
| T1 shorter | 245 words against 488 as written (50% less). Shorter in 42 of 42 requests | holds |
| T3 cheaper | 1,447 output tokens against 1,946 (26% less) | holds |
| T2 still preferred over a plain request (AI judge) | 7 short, 29 as written, 6 no clear winner (p = 0.0003): the other way | does not hold |
| T4 as good as the round-2 sentence (AI judge) | 6 short, 29 round-2 sentence, 7 no clear winner | does not hold |

Blanks such as [Name]: 6 of 42 answers as written, 0 of 42 with the short sentence, 0 of 42 with the round-2 sentence.
Round-2 sentence on this new set: 541 words, 2,573 output tokens.

Reading: the short sentence does what it says (half the words, a quarter fewer tokens, no blanks). The AI judge still
picks the longer answer, and its notes say why: "plus VAT, contingency and validity notes", "adds practical alternatives".
It rewards extra advice. Whether a person prefers the short answer is not known. Step 4 of the rules (a person's blind votes) is not
reported here.

So there are two sentences with two different effects, and no single one that is both shorter and judged better:
- round-2 sentence: judged better than plain (39-8-13 in round 2), costs about 50% more output tokens;
- short sentence: half the length and cheaper, judged worse than plain by the AI judge (7-29-6).

Limits: Opus judged Opus, Opus wrote the requests, one model, text only, 42 requests.
