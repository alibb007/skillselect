# Round 2 rules (written 18 Nov 2026, before any round-2 request or answer exists)

Why a second round: the round-1 sentence ("Answer this person's exact request...") is worded for a machine, was added by a
hook, was judged only by the same AI model, and the test had four setups. Round 2 is one plain thing a reader can repeat.

## What is tested
A sentence a person pastes under their own request:

    Use my exact facts and numbers, and give me a finished answer I can use as it is, with no placeholders or generic templates.

Control sentence (a generic "try harder" line, to see whether any extra line does the same):

    Please think it through carefully and give me a thorough, detailed, high-quality answer that covers everything important.

Neither wording changes after this file is written.

## Steps
1. Opus writes 60 everyday requests from 60 different people. Each request carries 4 concrete details of the person's own
   (numbers, limits, dates, names). The 4 details are listed with the request, before any answer exists.
2. Each request is answered by Opus with no tools and the system prompt "You are a helpful AI assistant.":
   A = the request as written; B = request + the sentence; C = request + the control sentence; A2 = A again (first 20 only).
3. Detail check: a checker (Opus, does not know the setup) marks each of the 4 details in each answer: used / ignored / wrong.
4. Blind pairs: a judge (Opus, same prompt as round 1 plus "a longer reply is not better for being longer") compares A-B, B-C
   and A-A2, each pair in both orders. A side wins a pair only when both orders agree; otherwise no clear winner.
5. The author judges A-B pairs blind on a page. His votes are stored and reported next to the AI judge's, never merged.

## What may be claimed (decided now)
- R1 "uses more of your details": share of details used in B is at least 5 points above A, and the paired sign test over
  requests (B used more vs A used more) has p < 0.05.
- R2 "better answers, by the AI judge": B wins more A-B pairs than A, sign test p < 0.05, and B's win share of decided pairs
  is above the larger side's share in A-A2.
- R3 "the wording matters": B wins more B-C pairs than C, sign test p < 0.05. If not, say plainly that a generic line did as well.
- R4 "no extra cost": B's mean output tokens are at most 10% above A's. Otherwise report the extra.
- R5 The author's votes: reported as counts and as agreement with the AI judge. One person is not "people prefer it".
- Placeholders: square-bracket blanks per answer are counted by a fixed pattern and reported whichever way they go.
- Anything that fails is reported as failed. No request is dropped after answers exist. No second wording is tried on this set.

## Guards
Every model call must report claude-opus-*; anything else writes STOP and ends the run. Round-2 budget cap: $55.
Every call is logged in the run ledger with kind v2_*.
