# Round 7 rules (written 19 Nov 2026 UTC, before any run)

Question: when a person just asks for the job, how many of the installed skills that fit does Claude use on its own?

Setup: the round-6 test folder (50 public skills; five fit a landing page: landing-page-generator, landing, epic-design,
copywriting, page-cro). Claude Opus, Claude Code headless, no plugin. The session also lists skills that come with the
account and the app (21 in round 6); they are counted separately.
Request, the same in every run: "Build a landing page for my product. It is Papertrail, a note-taking app for students,
$4 a month. Use whatever skills you have that help."  (run P)  and the same without the last sentence (run Q).
3 runs of each. Tools: Skill, Read, Glob, Grep. No writing tools, at most 10 turns: the count is of skills loaded, not of
the page built.
Counted from the session log: the skills loaded with the Skill tool, and how many of the five fits are among them.
What may be claimed: the counts, per run, for this one request. Six runs is small and is said so.
Cap: $5. Main model must be claude-opus-*.
