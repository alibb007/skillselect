# Round 3 rules (written 18 Nov 2026, before any round-3 request or answer exists)

Why: The author opened the round-2 judging page and judged nothing. The answers were too long to read (plain answers averaged 532
words, with the round-2 sentence 660). He asked for the other half of the idea: less verbose, to the point.

## What is tested
One sentence pasted under the request (wording fixed now):

    Use my exact facts and numbers, and give me a short, finished answer I can use as it is, with no placeholders, no generic templates and nothing I did not ask for.

## Steps
1. Opus writes 42 new requests (6 areas x 7), 4 personal details each. None reused from round 2.
2. Each is answered by Opus, no tools, system prompt "You are a helpful AI assistant.":
   A = as written; S = with the new short sentence; B = with the round-2 sentence (the longer-answer version).
3. Blind pairs by the round-2 judge prompt, both orders, win only when both orders agree: S-A and S-B.
4. The author judges S-A pairs blind on the page. Reported next to the AI judge, never merged.

## What may be claimed (decided now)
- T1 "shorter": mean words in S are at most 70% of the mean in A.
- T2 "and still better than a plain request": S wins more S-A pairs than A, sign test p < 0.05.
- T3 "cheaper": S's mean output tokens are below A's.
- T4 S against the round-2 sentence: reported whichever way. "As good as the longer version" only if S wins at least as
  many S-B pairs as B.
- Blanks ([Name] and the like) counted with the round-2 pattern, reported whichever way.
- Dropped on purpose: the detail check (round 2 hit a ceiling, 97% vs 99%) and the same-request-twice luck check
  (round 2: 5-6-9; that figure is quoted, not re-measured).
- 42 requests, not 60: every call comes out of the author's own usage limit, which round 2 exhausted.
- Anything that fails is reported as failed. No rewording on this set.

## Guards
Every call must report claude-opus-*; anything else, or a usage-limit error, writes STOP and ends the run. Round cap $25.
Calls logged in the run ledger with kind v3_*.
