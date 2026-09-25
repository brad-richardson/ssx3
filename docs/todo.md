# Working todo

Open work only, grouped by lane; only the orchestrator edits this file.
Closed items and the full gate history live in git history; the
pre-consolidation snapshot is `git show dfadb56a:docs/todo.md`. A gate is
recorded as a `## Orchestrator gate` section in the lane's
`local/research/<ID>/REPORT.md` (older gates: `ORCH-GATE*.md`); when an item
closes, delete it. Rules: `AGENTS.md`. Board and current pins:
`docs/status.md`. Numbers: `docs/numbers-ledger.md`. Verified mechanisms to
consult when writing briefs: `docs/facts.md`. Parked GameCube work:
`docs/reserve.md`.

**Milestone:** stock SSX 3 gameplay through the PS2 static recomp on the
Odin (menu → input → stock race advancing), then measured Odin budgets,
then 120 Hz simulation.

## E — PS2 runtime (PS2Recomp fork `ssx3`)

- [ ] **Race rendering gaps (top correctness item; RR1 Opus exploratory running).** The race world draws
      (terrain, rider, HUD since E50 Part 3 / E53 Part 2), but the sky and
      sun are gone, there's no foliage, textures look flat and a dark GS
      region occludes part of the screen. Leads: sky-like packet TBP0 11017
      has ALPHA `0x1`/CBP 10756 here vs `0x2a`/14473 in PCSX2 (unmatched
      scenes); 60 IMAGE uploads/vsync vs 73–74, 13 vs 23 mip chains;
      zero-area prims ~15× T65; 9 vsyncs with 33 capped VU1 programs.
      FPMODE=ieee, the EFU revert and `sceVu0MemReadQ` are ruled out (E59,
      E60). Next: same-scene frames/packets under `PS2X_DETERMINISTIC=1`,
      then the first ALPHA/CBP or texture-state divergence vs PCSX2.
      `local/research/E59/`, `E60/`, `E53/`, `E51/`.
- [ ] **Sprite/atlas artifacts and square snowflakes** (Brad's iPhone
      feedback 09-23, stray corner glyphs): all three renderers draw them
      from our stream and PCSX2 doesn't, so they are wrong texture-page
      contents upstream of the GS (G44, G46; includes the Select Peak photo
      panel, the "Peak 1 background" Brad asked about). Lead (RR1, 09-24): a
      PATH3 packet runs before the PATH1 draw it should follow, so pages can hold
      another screen's contents at draw time. RR1 re-checks the menus with its fix
      candidate. `local/research/G46/`, `RR1/`.
- [ ] **E61 menu/loading speed (muse, running):** menus 0.54×, loading 0.17× on the Mac (E58) and
      ~0.5× / ~0.17× on the Odin; Part 1 profiles where that time goes (CPU work vs waiting vs
      guest spin vs CD I/O). Faster menus shorten every boot and Brad's play.
- [ ] **E57 VU1 speed (top performance item; Opus, running).** VU1 interpreter is 39–50%
      of race time (hazard bookkeeping ~30% on the Odin, N5). Options: (a)
      host-float FMAC fast path with PS2 clamping behind a flag, A/B vs the
      exact path; (b) static recompilation of SSX 3's 7 VU1 microprograms
      (7,305 instructions). Validate with the E55 hash tap. E45's
      `VuWide=double` is already folded. `local/research/N5/`, `E53/`, `E45/`.
- [ ] **E54E signed 64-bit branches:** the PCSX2 low-64 oracle and suites
      support the candidate, but its one boot went black (8,000 GIF packets
      by tick 830 vs 92,728; first payload difference at packet 352). Don't
      ship; revisit with a deterministic trace and a targeted branch-value
      probe. Candidate is local/uncommitted. `local/research/E54E/`.
- [ ] **Remaining frontier-review semantics** not yet fixed: H10 INTC 5
      (VIF1) / 7 (VU1) never dispatched and DI not honoured; M1 VIF1 DIR=0
      readback parsed as VIFcodes; M6 I-bit stall; M7 split GIF packet /
      DIRECT-via-FIFO / PATH3 mask; Compare interrupt timing and exact
      GS-blank/FIELD rules (E54B, E54F1). Check each against the fork before
      briefing. `docs/research/review-2026-09-23-frontier-2.md`.
- [ ] **Snow Jam stalls at 99%** (E31): the recomp's `_sceCdSC` read loop
      stops at ~478 s while PCSX2 keeps reading (X1, T47). The suspected
      missing sound driver now exists (AU7 fold), so re-test on the current
      fork first; if it still stalls, one boot with CD/SIF RPC tracing vs
      T47's healthy sequence. `local/research/X1/`, `T47/`.
- [ ] **E34 faithful movie playback:** apply E30's two diffs
      (`e30-fix.diff`, `e30-regression.diff`), suite, then an A/B boot with
      `PS2X_SKIP_MOVIE` off vs the bypass. With the bypass off, E49 stalls in
      movie 1's GetPicture wait (the E30 shape). Watch `round=`: an
      empty-queue `sequence_end` spins to the 4097 cap; a mid-movie CD refill
      can't wake a dry park. Android also needs an FFmpeg build (N1 H2; off
      today). `local/research/E30/`, `E49/`.
- [ ] Unhandled RPC pairs at the end of a full route: SID/FNO `80000211/1`,
      `237/0`, `534e44/0`, `80000006/ff` (one hit each, pre-sound-fold).
      Re-count on the current fork; name any that matter.
      `local/research/E56/`.
- [ ] VU0/VIF0/SPR gaps, low priority: VIF0 has no MSCAL/MSCALF/MSCNT/
      BASE/OFFSET branch (still true at `fb11e18`); VU0 runs with a 4,096-
      cycle silent budget; SPR DMA implements normal mode only. PCSX2 runs
      no VU0 micro-programs or VIF0 kicks at settled SC (T57, T58), so fix
      only if a path reaches them. `local/research/E44/`.
- [ ] Deferred FPU edge: G2 Inf/NaN bit patterns as operands (3 assertions
      behind `PS2X_TEST_DEFERRED=1`). `local/research/E53/`.
- [ ] Multi Play/Online are enabled in the recomp's Main Menu but greyed
      out in PCSX2 (network/multitap state differs). `local/research/G44/`.
- [ ] K1: retire the `ret0@0x0042c1f0` stub (InitSystemCallTableAddress
      scanner) in `games/ssx3/ssx3.toml`, held since 09-20 for a
      convergence boot. Check it's still wanted before briefing.

## G — GS composite / GPU backend (paraLLEl-GS + Granite forks `ssx3`)

- [ ] **GB7C9 same-stream GPU comparison** for the damaged title/HUD
      glyphs on paraLLEl (Mac): rebuild the pinned G43 source, then compare
      CPU/paraLLEl packet input, the watched texture word (`63353341` at
      `0x000bae74`, packet 5470/batch 10) and destination words, crop and
      frame at marker 260, same binary for ON/OFF controls. A mismatch
      still can't pin packet 5470 alone. Check first whether N8X1's
      bilinear rounding explains it. `local/research/GB7C7P2/`, `GB7C8/`.
- [ ] **Exact bilinear** in `ubershader.comp` so Adreno matches Mac (N8X1:
      the ~9% of pixels outside ±2 are hardware bilinear rounding). Needs a
      shader regen and a Mac re-baseline. `local/research/N8X1/`.
- [ ] Wave128 subgroup probe: name the Turnip fault behind the hierarchical
      binner mis-bin (wave64 is the shipped workaround). No upstream
      contact. `local/research/N8X1/`.
- [ ] GS bridge step (d): GPU-resident presentation (queue-on presents were
      sparser; avoid the VRAM readback per present). Steps (a)–(c) done or in
      N9. `local/research/GB1/DESIGN.md`, `GB2/`.

## N — Android app (Odin)

- [ ] **N11 per-stage time budget (muse, running):** ms per guest frame
      by stage (guest, EE helpers, VU1, VIF/DMA, GS submit, audio, waits) for the race and a menu
      on the play build with sound on, plus one GameThread-pinned-to-cpu7 run.
      `local/muse/prompts/N11.md`.

- [ ] **Rider idle at race start:** on the Odin (N10) the rider sits at 0–1 MPH with a RECOVER
      prompt from ~00:00:06 to ~00:00:40, then rides at 43–44 MPH. First check the Mac on the same
      I26-FAST route (route input vs runtime). Then a simpleperf race profile on the N10 APK.
      `local/research/N10/`, `N7/`.
- [ ] Odin thermals: back-to-back runs reach thermal status 4–5 with cpu5 at 1.79 GHz (N10); space
      speed runs or record status, and consider it in the 120 Hz budget.
- [ ] The game image doesn't fill the Odin screen (margins on all sides in
      N9's 1920×1080 screencaps); check the presenter's scale/aspect on
      Android. `local/research/N9/`.
- [ ] Horizontal stripes on Odin screens (seen since N8D1, still on N9's
      fork-tip APK). `local/research/N9/`.
- [ ] Manifest `android:showWhenLocked` + `android:turnScreenOn` on the
      NativeActivity: N4 had them on `n2-android`, the fork manifest at
      `fb11e18` doesn't. Decide whether to port (the lockscreen check in
      `AGENTS.md` stays either way). `local/research/N4/REPORT.md`.
- [ ] Brad, 2 min hands-on: physical X/Y button positions on the Odin
      controller (N6 §5). `local/research/N6/`.

## A — audio

- [ ] Turn sound on in the shipped envs (`PS2X_SOUND=1` in the iOS bundle env: done in I30; the
      Odin `ps2x.env` and N-lane launchers next). Brad confirmed AU8's planar fix sounds exactly right (09-24).
- [ ] **Race SFX on SPU2 hardware voices (AU8 E10; AU9 Opus exploratory running):** in a PCSX2 Snow Jam race, SPU2 voices carry
      an intermittent, near-mono layer (dry 625/545 RMS, −15.5 dB of output, 94% < 1 kHz; likely SFX
      after T47's 1.75 MB SPU upload). Our HLE has no SPU voices, so races lack it. Needs cid-0
      uploads (`sceSdVoiceTrans`), tag-3 `updatevoices` and an SPU2 ADPCM voice mixer. Clips
      `~/dev/ssx3-work/AU8/AU8-R-race-*.m4a`. `local/research/AU8/NOTEBOOK.md` E10.

## I — iOS

- [ ] **I32 (running): virtual analog stick on the left, D-pad on the right** (Brad, 09-24).
      Part 1 Simulator screenshots go to Brad for approval before the phone install.
- [ ] Brad (09-24, iPhone I30): UI elements flash in and out every few seconds and many 3D assets
      pop in and out. Relayed to RR1; check on the Mac deterministic boot too.
- [ ] **I28 iPad-native presentation** (low priority, behind Odin): add the
      iPad device family + landscape and lay the virtual pad in the
      letterbox margins; Simulator iPad, then Brad's iPad. IPAD1 ran as an
      iPhone-compat portrait window (`~/dev/ssx3-work/IPAD1/`).
- [ ] Brad listens to I30 on the iPhone (fixed music, sound on; expect gaps below full speed).
- [ ] Physical controller check by hand on the iPad (I25 G1).
      `local/research/I25/`.
- [ ] Guest font detail is still coarse (source image is low resolution,
      I27B); only if Brad asks.

## W — widescreen

- [ ] Nothing open. Anamorphic 16:9 is the default; a 2D/HUD correction for
      the ~33% widening happens only if Brad asks. `local/research/W1/`.

## T — PCSX2 reference (bytesize)

- [ ] Keep T tied to named E/G/A questions (same-scene sky/texture packets
      for the race rendering gaps; race/SFX audio reference).

## V — storage and hosts

- [ ] Brad decides the remaining SSD folders: `laptop-evacuated-0918`
      (28 GB), `glimmer-ize` (18 GB), `bradflix-ps2recomp`. Personal
      folders were kept by his call (V2 tier 3). `local/research/V2/`.

## Cross-lane

- [ ] **Tooling from the 09-24 review** (`docs/research/review-2026-09-24-time-and-bottlenecks.md`):
      - Done (TL1): `local/tooling/odin/odin_replay.py` + `stream_tools.py`; `[gs-path]` logger
        on fork `ssx3`. Audio-side path logging still open.
      - `gate` helper for the orchestrator: append the REPORT gate section, update the todo
        line, commit with explicit paths, push, close the pane.
      - Worker permission preflight in the launchers: dry-run the edits/SSH a brief needs.
      - Nightly (or per-fold) Android + Mac build from the three fork tips to catch drift.
- [ ] UP1 leftover: upstream `gs_cache` swizzle goldens (Rank 2, tests only) adapted to our
      CPU backend. `local/research/UP1/`.
- [ ] Speed re-baseline after the sound fold (sound HLE is default-on):
      clean Mac numbers at `fb11e18` before quoting any speed.
- [ ] 120 Hz simulation: scope once the Odin stock race is stable. X3's
      map: counted step loop in `sub_00316F00`, `$s1` vs `lw 0x20($s0)`,
      back-edge `0x317190 → 0x317128`; the published patch-site increment at
      `0x317184` is the delay slot of `jal checkHalt`; metro sites clear the
      frame-skip flag `[*(gp+0x2A74)+0x34]`. Measure with the E55 hash tap.
      `local/research/X3/`, `X2/`.
- [ ] Save states for the recomp runtime (global/static state is the
      obstacle); would cut boot-to-race time for every probe. Queue.
- [ ] Update `docs/route-criteria.md` for the 120 Hz simulation preference
      and drop its stale GameCube-era work-queue snapshot.
- [ ] Brad: bradflix (x86_64, 14 cores, 62 GB) as the Android build host,
      freeing bytesize for PCSX2? Proposed 09-23; confirm it's still wanted.

## Parked

- **VU1 on its own thread** (MTVU-style; Brad, 09-24: parked until the game works, too much
  complexity for now). Could roughly halve GameThread time after E57, but EE↔VU1 handoff ordering
  must be exact (RR1's PATH3 ordering bug is the same class). Size it with N11's numbers first.

- **Audio below full speed (Brad, 09-24):** stutter for now (current behaviour, typical of
  emulators). Plain slowdown drops pitch with speed (0.5× = an octave), so no. **When menus reach
  ~0.8×, add pitch-preserving time-stretch** (SoundTouch, LGPL; PCSX2's default), driven by guest
  vsync rate vs wall clock, so music and SFX stay in sync with the game.
- **Rebase onto upstream for upstreaming** (Brad, 09-24): when Brad has
  spare quota. Never rewrite `ssx3`: replay our product commits onto
  upstream `main` in topic batches (CPU semantics, kernel/scheduler, GS,
  sound, iOS, Android) on a new branch (e.g. `ssx3-upstream`), drop
  diagnostic taps and upstream-superseded fixes, regenerate codegen, re-run
  the gates (Mac menu→race, sound mid/side vs PCSX2, iOS Simulator, live
  Odin race), switch only at parity. Multi-day. No upstream contact until
  Brad says.
- **W2 upscaled internal resolution** (Brad, 09-23): don't schedule. If
  picked up: paraLLEl-GS upscale once it's the live backend, a PCSX2 2×/3×
  preview of which SSX 3 effects break, source-level fixes, then an
  integer-multiple default per device.
- **Adreno driver filing** (Brad, 09-22): paused. Any rewrite drops the
  withdrawn sampling inference.
- **E55 ExternalWake placement policy:** no production poster exists at
  `ddaee78` (E55D1); revisit if one appears. `local/research/E55D1/`.
- **GameCube/Dolphin route:** reserve, `docs/reserve.md`.
