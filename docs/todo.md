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
- [x] Snow Jam's 99 % loading stall is gone on `0ed07c4` (SJ1 R2 loads and races).
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

- [ ] **GB8 paraLLEl as the Mac's standard backend (Brad, 09-24; muse, running):** speed CPU vs
      GPU, determinism (det-hash equal?), frame parity, host threads. Then switch the default so
      Mac boots are faster and exercise the Odin's renderer. `local/muse/prompts/GB8.md`.
- [ ] **GB9 align the Mac's paraLLEl paths with the Odin's (Brad, 09-24; queued after the GB8 gate).**
      Goal: every GPU-path choice the Odin makes, the Mac makes too, so Odin-only questions shrink
      to driver/rounding/speed/thermals. Part 1: inventory each `[gs-path]` field (hier rule,
      subgroup sizes, descriptor path, sampler feedback) Mac vs Odin, why each differs (e.g. the
      `#ifdef __APPLE__` flat-always binning; Apple SIMD width 32 vs wave64; descriptor buffers on
      MoltenVK), and whether a default-off env knob can force the Odin choice on the Mac. Part 2:
      add the feasible knobs in the paraLLEl fork, replay-check Mac(knobs) vs Odin on TL1's
      `odin_replay.py` rows. Remaining gaps go in `docs/facts.md`.

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

- [x] **First stock race finished** (FR1, 09-25): Happiness 2nd 04:18 → results screen; Snow Jam + Metro-City
      load and race. Route FR1-R1 = I26-FAST minus the 30 s down-hold (down brakes).
- [x] Post-race jump fixed (PF1 `3c037ab`: checkpoint unwind at a recursive call misread as a return; folds in F5).
- [ ] Odin thermals: back-to-back runs reach thermal status 4–5 with cpu5 at 1.79 GHz (N10); space
      speed runs or record status, and consider it in the 120 Hz budget.
- [ ] The game image doesn't fill the Odin screen (margins on all sides in
      N9's 1920×1080 screencaps); check the presenter's scale/aspect on
      Android. `local/research/N9/`.
- [x] Odin stripes gone in the F2 Odin build (8/8 screencaps).
- [ ] Manifest `android:showWhenLocked` + `android:turnScreenOn` on the
      NativeActivity: N4 had them on `n2-android`, the fork manifest at
      `fb11e18` doesn't. Decide whether to port (the lockscreen check in
      `AGENTS.md` stays either way). `local/research/N4/REPORT.md`.
- [ ] Brad, 2 min hands-on: physical X/Y button positions on the Odin
      controller (N6 §5). `local/research/N6/`.

## A — audio

- [ ] Turn sound on in the shipped envs (`PS2X_SOUND=1` in the iOS bundle env: done in I30; the
      Odin `ps2x.env` and N-lane launchers next). Brad confirmed AU8's planar fix sounds exactly right (09-24).
- [ ] **Race SFX (AU9, Opus, running): confirmed right by Brad (09-24 clips).** Cause: the recompiler's
      BLTZ/BGTZ family tests 32 bits, so the game's file-table bsearch misses `BANKS.INF` and the sound
      banks never load. AU9 fork `au9-spu`: runtime override of `0x3E3968` + SPU2 voice layer (531
      uploads as PCSX2, menu SFX NCC 0.9997, music unchanged). Gate, then fold. The global emitter fix
      (`a46fb2e`) is NOT validated: E54E's boot with it went black; separate lane to find the
      non-sign-extended register it exposes.

## I — iOS

- [ ] **Brad 09-25 (iPhone, paraLLEl build):** main menu "basically perfect"; picture ~50 % too dark
      (DK1 fixed: PS2 alpha blended at present); pad v2: stick
      ×1.5, D-pad at 80 % of the face-button cluster, below-left of it like a PS2 pad (I34 done, Brad OK'd). One combined
      iPhone build after both.

- [ ] iOS paraLLEl: no CPU fallback when Vulkan init fails (black game frame, app alive; I33 §3).
      Add a fallback to the CPU backend or a visible error.

- [ ] Brad's feedback on the I32 controls (stick left, D-pad right; on his iPhone since 09-24).
- [ ] Brad (09-24, iPhone I30): UI elements flash in and out every few seconds and many 3D assets
      pop in and out. RR1: no draw dropout in the Mac stream; likely the PATH3 wrong-texture effect. Re-check on his phone after the RR1 fold.
- [ ] iPad in portrait: the virtual-pad layout collides (SELECT/START overlap; D-pad and face buttons over the picture; F2 Part 3 shot). Fold into I28.
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

- [ ] **N12 (queued after F5 Part 2, Brad 09-25):** Odin race + menu re-profile on the F5 play build (`local/muse/prompts/N12.md`): VU1 ms left on GameThread after VR1/VB1 sizes the parked VU1-thread decision.
- [ ] **PX2 (queued):** why PCSX2-GL won't rasterize the race-world tristrips from our stream (menus and HUD
      replay fine): per-draw state probe vs PCSX2-SW (`local/research/PX1/REPORT.md` §3). Until then, race
      pixels are judged against PCSX2's own runs, not replays.

- [ ] **F5 fold (queued, onto `8559ab9`):** VB1 d4 (`1f51e48..9638b3d`, Mac 1.15× over stage A), HR1 (`cf7c0df` knobs, `4825123` pipelined present,
      `4a591d3` rate log, zero-copy `fb3dca0`+`d929048` default off; iOS/Mac default 4×+hi-res + pipelined; Odin
      pipelined + a 1× vs 4×+hi-res measurement), LX1 TZ/x86/fenv (`lx1-tz`: `5f32212 20377a3 b4cb476 fc0cc67`; Mac↔bradflix det-hash equal to t2400), PF1 `3c037ab` (post-race unwind fix), RP1 `9bfd4aa` (VU MAX/MINI raw bits: carve trail); codegen promotion of the F4 regen
      once lanes on the current codegen finish; then device builds (4×+hi-res default TBD by HR1's report).
- [ ] VU1 usage-table gap: OPMULA/OPMSUB read fs.xyz but declare fs lanes = dest (unused in SSX 3; VB1).

- [ ] **Running (09-25 afternoon):** VB1 (VU1 stage B, Opus), FR1 (race to the finish + more events; R1
      ≤ 1,800 s approved), PX1 (PCSX2 gsrunner as pixel reference + gallery), TC1 (per-thread state
      audit, vf0 read-only), F3 (fold → iPhone/Odin), LX1 1b, Q2. Queued: F4 (VR1 + NP1 + x86 fixes),
      Q1 after Q2, Odin menu-side Turnip/allocator churn after F4's Odin profile.

- [x] Rider fix folded (F3 `ec2dbf1`); TC1 audit done (vf0 read-only + VU0 R → F4). Gaps: FCR0 unmodelled, VU0 macro flags not modelled.
- [ ] **F4 fold (after F3), base fork `ssx3` `ec2dbf1`:** VR1 VU1 stage A (`0ed07c4..1f51e48` + `6c2de6f`;
      `~/dev/ssx3-work/vu1gen-ssx3`, private copy to bytesize; iOS/Android builds pass the dir) + NP1 Part 2
      (`e5654f3 7caf516 125c9e5`) + LX1 Part 1c (TZ pin/DST, x86 build fixes) + TC1 (`e29e4975` vf0
      read-only emitter, needs a **codegen regen + promotion**; plus a one-line VU0 R ctor fix). Odin
      pair vs F3; iPhone + Odin play builds. Later: dump VU1 images on other courses (FR1).
- [ ] **Host split after F5 (LX1 parity + headless GPU on bradflix done 09-25; Brad):** first cut bradflix's ~50 min full build (one slow `-O3` unity batch). bradflix gets **4 boot slots** for correctness
      work (det-hash, frames, counters, suites, builds; CPU and paraLLEl if LX1 Part 2 works); the
      mini drops to **1 slot** reserved for performance benchmarks and Apple-only checks; the Odin
      stays 1. Tooling: `p_lane_lease.py --host bradflix|mini`, `local/tooling/remote/bradflix_boot.sh`,
      brief template default = bradflix; then update AGENTS.md Leases + the runbook.

- [ ] **Running 09-25:** FP1 (guest pacing to 59.94, `PS2X_UNPACED=1` for speed runs), SJ1 (full race to
      the finish + Snow Jam 99 % re-test; R1 ≤ 1,000 s and R2 ≤ 700 s wall approved), UV1 (VIF UNPACK
      formats vs PCSX2 + DMA stall/REFS probe), VR1 (VU1 static recompile stage A, Opus), NP1 Part 2
      (Odin link/memset/handoff).

- [ ] **F2 folded** (fork `ssx3` `96e9f45`, codegen promoted): Part 3 iOS running; Part 2 Odin waits for
      the Odin back on USB. Then NP1.
- [x] Stripes fixed (ST1, fork `92f9991`: progressive scanout); confirm on the Odin and iPhone builds.
- [ ] **AU10 (running): folded tip hangs on the title with sound off** (GA1). Voice state must advance
      on guest time; det-hash must match sound on vs off. Until fixed, boots on `56a5e8a` need
      `PS2X_SOUND=1` (the device play envs already have it).

- [ ] **IN1 INTC 5 (VIF1) / 7 (VU1) never dispatched (CT1):** the VIF1 handler `0x362340` counts
      i-bit interrupts at `0x5059d8+0x80` and cancels stalls (VIF1_FBRST STC); the VU1 handler
      is a no-op. Check whether `sub_00375A08`/`sub_00376938` read that counter (frame pacing?)
      and whether SSX 3's VIFcodes set the i-bit; if yes, raise INTC 5 at i-bit VIFcodes (+ the
      M6 stall) and A/B on the det boot. Fold CT1's default-off `PS2X_COVERAGE_TICK` /
      `PS2X_INTC_LOG` with it. Overlay (`SLUSOVF.BIG` = DNAS/online module) only matters if the
      online menus are ever in scope.

- [ ] **RV3 Fable review adopted (09-25, `docs/research/review-2026-09-25-fable.md`).** Running:
      SB1 (sign-branch tripwire), GA1 (arbiter drain-order inversions), CT1 (coverage, VU1 caps,
      INTC, the SLUSOVF overlay), GB9 P1 (hier binning on the Mac). Queued: **NP1** Odin
      call-graph profile + `-Wl,-Bsymbolic`/arbiter copies (after F1 Part 2 frees the Odin);
      `PGS_DESC_PATH=plain` one-replay check on the Odin; VU1 static recompile stage A only if
      the Odin still spends ≥ 60 ms in VU1 after E57; VIF UNPACK V2/V3 z/w check vs PCSX2
      `Vif_Unpack.cpp`; REFS / D_CTRL STS-STD counter; fix `rr1_cap2gs.py` blank frames after
      tick 1608 (PCSX2 gsrunner is the pixel reference); `sbr-census.py` after each regen;
      lease FIFO for exclusive claims + builds that wait on an exclusive lease; read
      `noteVuRun`/`noteUnhandledRpc`/coverage at every device gate.

- [ ] **F3 fold (queued):** FP1 pacing `51e730f4` (default on; `PS2X_UNPACED=1` for speed runs) + DK1 brightness `6cba433` + I34 pad v2 + IN2 tap latch + UV1 Part 2 + NP1 Part 2 + VR1 as each gates; then iPhone + Odin builds; Android compile before calling it folded.
- [ ] **Brad offline 09-24 night; decisions:** (1) Fable frontier review once RR1/AU9/E57 have
      reported (steer fold order, the sign-extension bug class, the speed plan); (2) after gates,
      fold to fork `ssx3` and install one combined build: iPhone install only, iPad test, Odin as his
      play build, save + manual-play env re-applied and verified.

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
- [ ] 120 Hz simulation: RV6 (`docs/research/review-2026-09-26-astra-120hz.md`) recovered the timing model (app manager
      rate/dt/multiplier fields, VBlank-end → producer ring → consumer → app update, catch-up). TM1–TM3 done: chain
      confirmed; rider integrators `0x1380b4`/`0x13e0dc` (`pos += delta`, no manager dt); the rate-120 probe gives
      2 updates/VBlank but full-size steps (1.89×) and a 2× HUD clock. **TM4 (running):** find the
      per-update step constants behind `delta` and the HUD `/60`, then one coherent probe. Older notes: X3's
      map: counted step loop in `sub_00316F00`, `$s1` vs `lw 0x20($s0)`,
      back-edge `0x317190 → 0x317128`; the published patch-site increment at
      `0x317184` is the delay slot of `jal checkHalt`; metro sites clear the
      frame-skip flag `[*(gp+0x2A74)+0x34]`. Measure with the E55 hash tap.
      `local/research/X3/`, `X2/`.
- [ ] Save states (SS1, folded `5474956`): lanes use `baseline.py get-state` + `ssx3_boot.py --load` (Mac or bradflix; states are per host: SS2). For device
      play: Android runner-SHA via `dladdr`, a save/load button, non-det loads (SS1 report § Dropping det).
- [ ] Run-speed tooling (Brad OK'd 09-25): **RS1** shared ccache + `local/tooling/build/mac_build.sh`;
      **RS2** cached baselines + shared boot driver `local/tooling/boot/`. Host split to bradflix
      follows F5 Part 2 (Brad 09-25).
- [ ] VU1 blocks: decide `PS2X_VU1_BLOCKS` default from the next Odin pair (Mac 1.067× on, ~1 % cost off). Next VU1 levers: register residency across block iterations (RV4 §2), VU0 recompile (VR3).
- [ ] **MT1 (running, Brad 09-26: un-parked under PCSX2 parity):** MTVU, deterministic by design (fixed guest-time VU1 semantics, worker thread; threaded det-hash = synchronous).
- [ ] **SS3 (running):** RV5 S2–S5 save-state holes: paraLLEl palette indices on load, partial GS transfer / vertex state at the
      save point (defer or serialize), card directories + timestamps, Android runner identity via `dladdr`.
- [ ] **CP1 (running; RV4 rank 1 measurement):** matched-window Odin critical-path timeline: per-thread running vs
      blocked, GS queue waits, GPU timestamps, frequency residency, `flush_submit` split (submit / submit_empty / compile
      drain; was FS1: the 4× cost is GsWorker time blocked there, VK1 2A). Attribute the 'profiler unwind' bucket.
- [ ] Android `-march` quirk (BA1 §1): root CMake's crypto/crc `-march` is overridden by a later plain `armv8-a+fp+simd`; decide which is intended (Odin supports both).
- [ ] **Android immersive mode (small):** the gesture-bar handle shows over the game on the Odin (F6 screencaps); hide system bars.
- [ ] **GL fallback aspect (small):** Android GL fallback still letterboxes into raylib's 640×448 canvas (1544×868 box);
      start raylib at the display size so it follows Brad's max-fit rule too.
- [ ] Idle-loop / event fast-forward census for loading and menus (RV7 rank 7): find hot guest polling loops
      first; one exact candidate only if a loop is found (timer/side effects preserved).
- [ ] Reference read of ARMSX2's ARM64 VU/EE core (RV7 §5; GPL: techniques only) once VR2's block design settles.
- [ ] VU0 recompile: decide `PS2X_VU0_RECOMP`/`PS2X_VU0_DIRECT` defaults from F7's Odin pair (Mac +5.4 %).
- [ ] HS1 follow-ups: cold bradflix build 400 s (nine -O3 unity TUs > 60 s; accept or PCH); unify the
      `vu1_images` pin scheme (RS2 vs HS1 differ; fold into `baseline.py pins`); delete LX1's retired
      `BRADFLIX_LEASE` dir; bradflix ccache cap 5 GB.
- [ ] RS1 follow-up: canonical paraLLEl checkout `~/dev/ssx3-work/parallel-gs-ssx3` (fork `19d93b2`) as
      `mac_build.sh`'s default instead of F2's scratch; ccache on bradflix in the host split.
- [ ] RS2 follow-up: `baseline.py pins` computes the pins JSON (VU1 set hash included); first real
      `make` on the next fork tip.
- [ ] Update `docs/route-criteria.md` for the 120 Hz simulation preference
      and drop its stale GameCube-era work-queue snapshot.
- [ ] Brad: bradflix (x86_64, 14 cores, 62 GB) as the Android build host,
      freeing bytesize for PCSX2? Proposed 09-23; confirm it's still wanted.

## Parked

- **Present with Vulkan directly (option B; Brad 09-25 evening: un-parked as the VK1 Opus spike, Odin first).** Granite WSI swapchain
  (SDL / CAMetalLayer / ANativeWindow) for the game image, virtual pad redrawn in Vulkan, raylib kept
  only for input/audio (or SDL). Buys: no copies, no deprecated GL on Apple, precise present timing for
  120 Hz. Revisit when 120 Hz work starts; HR1 may investigate if its time box allows.

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
- **Adreno driver filing** (Brad, 09-22): paused. Any rewrite drops the
  withdrawn sampling inference.
- **E55 ExternalWake placement policy:** no production poster exists at
  `ddaee78` (E55D1); revisit if one appears. `local/research/E55D1/`.
- **GameCube/Dolphin route:** reserve, `docs/reserve.md`.
