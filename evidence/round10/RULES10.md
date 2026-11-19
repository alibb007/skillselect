# Round 10: the renamed plugin (SkillSelect 3.0.0), real runs (written before the runs, 19 Nov 2026)

- Same test folder as round 6 (50 public skills), same request: "build a landing page for my product". Model: Opus; any other model stops the run.
- Run B: the user types the short command `/skillselect build a landing page for my product` with the plugin loaded by `--plugin-dir`. This also tests the docs' claim that a plugin skill answers to its bare name. If the short command is not recognised, that is recorded and the run is repeated with `/skillselect:skillselect`.
- Run K: `/skillselect categorize`.
- The GitHub cache is a new empty folder, so the seconds are a first-use number (round 6 ran with a warm cache).
- The side without the plugin is not run again: plain Claude did not change. Its numbers stay those of round 6 (27 steps, 111.4 s, 528,087 tokens, 18 Nov).
- One run each. Tokens, seconds, steps and cost are read from the run's own result line.
- Cap for this round: $2.
- Added after run B (19 Nov): in run B the finder call took 62 s of the 86 s; the same finder call alone on an empty cache took 7 s a few minutes later (GitHub was slow or asked the finder to wait). One run is too thin for a seconds number, so B is run two more times, each on its own empty cache (Bb, Bc). The film and page use the middle run of the three for seconds, tokens and cost, and all three are kept.
