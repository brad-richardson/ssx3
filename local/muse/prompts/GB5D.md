# GB5D Part 1 — earlier lower-label divergence bracket

You are a Codex worker in `~/dev/ssx3`. Follow `~/dev/AGENTS.md` and
`AGENTS.md`. Read `local/research/GB5C/REPORT.md` and GB5B's report.
Hand back the table; the orchestrator decides the gate. Replay-only
evidence gathering, no renderer fix. No mini, Odin, iOS, live boot,
source edit or fork push.

Use the clean local G worktree `~/dev/ssx3-work/GB4/PS2Recomp` branch
`gb4-parallel` at `f796669` (verify). New output only under
`~/dev/ssx3-work/GB4/run/gb5d/`, report under
`local/research/GB5D/`. Reuse the capture/path sidecar from GB5C,
never copy them: `run/gb4p4.capture.bin` SHA-256
`a6f75fb34fceccf6fd92ad65950d16f05a140cf38a3cc2f028be32e56ad51851`
on two reads. CPU raw P6 frames already exist at ticks
100,200,300,400,500,600,700,800,850,899 in
`run/gb5b-periodic-raw-ppm/`.

GB5C found visible paraLLEl lower-label damage at tick 899, before
the 902–921 recurring composite. The CPU Select Character screen
already has the lower button labels by tick 800 and 850; at tick 899
it is transitioning to Setup Character. Correct comparison: same
capture and true path sidecar, same marker, CPU raw page 112 versus
paraLLEl Present. If the label pixels already differ at 800, the first
damaging input/state is earlier; if those pixels match then, the
interval is `(800,899]`. Whole-crop differences from a changed
background are not proof of glyph damage.

1. Verify pin, ten CPU raw inputs and capture SHA twice. Use the
   existing test binary (one rebuild only if absent/stale). One
   paraLLEl replay with `PS2X_GS_REPLAY_PPM_TICKS` set to the ten
   ticks above, `PS2X_GS_REPLAY_BACKEND=parallel`, same capture and
   `paths.txt`, step 50, outputs under `run/gb5d/parallel-ppm`.
   Require **init_ok=1**, all ten PPMs, 556/556 and zero
   null/unsupported operations; a suite pass with init_ok=0 is a
   failed replay. Use escalation if Vulkan init is blocked by the
   sandbox as in GB5C.
2. Reuse GB5C's P6 comparison method without editing its files.
   Write a small script/CSV under `run/gb5d/` comparing the lower
   `(340,360)-(430,420)` crop at all ten ticks (differing pixels,
   RGB MAE, each FNV-1a hash) and full-frame differing pixels.
   Validate dimensions and byte lengths. Identify the first tick
   where the lower **label glyphs are visible in CPU** and the first
   tick where their strokes visibly differ in paraLLEl; do not equate
   a crop hash difference with glyph-stroke damage.
3. Make and view side-by-side PNGs for 700,800,850,899 with marked
   lower crop and 4× enlargement. Record whether the same specific
   label strokes are broken at each tick. State the narrowest marker
   interval supported and a targeted next replay question; do not
   name a packet/texture/state mechanism without direct evidence.

Budget: one successful GPU replay plus one setup correction, ≤1
build, ≤90 min, ≤1 GiB new data, PPMs ≤100 MiB, PNGs ≤25 MiB. No
speed number. Stop after one failed repair, no tuning loop. Deliver
`local/research/GB5D/REPORT.md` with pins, exact commands, ten-row
table, counters, viewed frames, interval, data cap and gaps. Commit
only the explicit report `[GB5D]` with trailer
`Orchestrated-By: Codex`; no source commit or push. The orchestrator
decides the next probe.
