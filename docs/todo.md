# Working todo

Open work per lane, newest first. Only the orchestrator edits this file.
Rules: `AGENTS.md`. Board: `docs/status.md`. Numbers:
`docs/numbers-ledger.md`. History up to 2026-09-22, including every gate
read: `docs/archive/todo-2026-09-22.md`. Parked GameCube work:
`docs/reserve.md`.

**Milestone:** stock SSX 3 gameplay through the PS2 static recomp on the
Odin (menu → input → stock race advancing). Then Odin native race
with measured budgets, then 120 Hz simulation.

## E — PS2 runtime (fork `ssx3` @ `e57b5f8`)

- [ ] **Parallel spikes started 09-23 (Brad: "start all four"):**
  - **GB2**: GS queue, step (a), on fork branch `gb2-gs-queue`, byte-exact A/B.
  - **N6**: Odin built-in controller → PS2 pad.
  - **E45**: VU1 `long double` → `double`. It's quad soft-float on arm64
    Android but plain double on the Mac, so the Odin would compute what the
    Mac already does. Validated with an Odin bench.
  - **X3** (local Qwen, dense): map the 120 Hz loop/timestep.

  Mini boots now have two lease slots (`local/tooling/p_lane_lease.py`).
  Proposed, awaiting Brad: bradflix (x86_64, 14 cores, 62 GB) as the
  Android build host, which frees bytesize for PCSX2.

- [x] **E45 PASS (09-23, 3087c7c/e77e751): VU1 `VuWide=double`.** Fork branch
      `e45-vu-double` `310b30f` (not pushed); suite 570/570. On the Odin the
      double build's hash equals the Mac's and equals quad on all 5 bench
      programs (incl. FLT_MAX/denormal edges), so the change is speed-only:
      quad costs 1.3–1.8× per FMAC-dense instruction. N4's quad soft-float
      self share was only ~8–9%, so the game gain is modest. It also covers
      VU0 macro mode (shared core). To do: fold `310b30f` into `ssx3` after
      E44 Part 4 pushes; cherry-pick onto `n2-android` for N5's dumps-off APK.
      Bench used fallback programs, not SSX 3's real microcode (that needs a
      RAM dump).
- [ ] **VU1 speed (top performance item, 09-22, N4):** on the Odin Select
      Character runs at ~0.2 guest vsyncs/s with the VU1 interpreter at 94.8%
      of samples, much of it quad-precision soft-float (`__addtf3`,
      `__extendsftf2`) computing exact FMAC results. SSX 3 has only 7 VU1
      microprograms / 7,305 instructions (P1 census), so options are (a) a
      host-float FMAC fast path with PS2 clamping behind a flag, A/B against
      the exact path; (b) static recompilation of the 7 microprograms, as the
      EE is. Brief after E33 settles 3D correctness (don't change VU1 math
      while it's the suspect).
- [ ] **Missing 3D (top correctness item, 09-22):** race = HUD over a
      near-black silhouette; no rider on Select Character. Survey: VU1 is a
      cycle-stepped interpreter; VIF1 MSCAL/MSCNT gives it a fixed 65,536-
      cycle budget and **exits silently** when spent
      (`ps2_runtime.cpp:753-788`, `ps2_vu1_core.cpp:1636,1827`); FLUSH/
      FLUSHE/FLUSHA are no-ops (`ps2_vif1_interpreter.cpp:370`); no GS
      stream dump or per-frame draw export exists (only the 512-entry
      debug-history ring in ImGui). Next E brief after E32: env-gated
      counters (budget exhaustions, MSCAL count, XGKICK count, per-path
      draws per frame, file export of the debug ring) + one boot to Select
      Character; compare against T48. One candidate fix only if H1 shows.

- [x] **E29 PASS (09-22):** dev-only bypass reaches the rendered SSX 3
      title screen. Branch `e29-movie-bypass` @ `e5ce086d`, local.
- [x] **E31 PASS (09-22): first stock race on the recomp (Mac).**
      `PS2X_PAD_SCRIPT` (dev-only, 461/461, `fork/e29-movie-bypass` @
      `ee39b9f`) drives title → menus → Happiness Rival Challenge; the race
      starts, HUD live, timer 00:00:01 → 00:00:04 (e31l, 584 s). Orchestrator
      caveat: the 3D world renders near-black (silhouette only, no rider, sky
      or textures), so this is race *logic*, not a rendered race. Snow Jam
      stalls at 99% (live loop, no CD reads, no park). Odin reuse string: E31
      REPORT §e31l. Guest speed varies a lot (title 23 ticks/s, 3D menus
      1–3 fps with the software GS).
- [x] **Sprite/texture addressing (Brad, 09-22) → answered by G44 for the menu: the stray sprites come from the game's draw stream, not GS cropping (both GS backends agree; PCSX2 differs).** Original note:
      wrong sprite-sheet cell selection/cropping may explain many graphics
      faults, possibly the missing rider too: SSX 3 renders some content to
      an offscreen buffer and composites it as a textured sprite (G13:
      composite-112 before the scene), so a wrong TBP/UV/CLAMP/CLUT on that
      composite would drop the rider. Treat as **H4** next to E33's H1–H3.
      Discriminators already running: G44 (paraLLEl fed the same stream:
      right cells ⇒ CPU-backend texture/sprite bug; same wrong cells ⇒ wrong
      TEX0/uploads upstream) and T48 (PCSX2 per-draw TBP0/PRIM tuples at
      Select Character). Next: E35 brief after G44 + T48: per-draw sprite
      TEX0 (TBP0/TBW/PSM/CBP/CSA), UV range, CLAMP/REGION bounds at Select
      Character vs T48, walked for the "3" logo, arrows, corner glyphs and
      the rider composite; one fix if a single mechanism shows.
- [ ] Stray PS2 button glyphs/D-pad/L1-R1 boxes in the top-left and
      bottom-left corners (Brad sees them on the Odin; E31's Mac Select
      Character dump has them inside the 512×448 guest framebuffer).
      Brad (09-22): sprite sheets aren't cropped properly, so the wrong atlas
      cell is shown. The CPU backend has REGION_CLAMP (`gs_cpu_backend.cpp`
      :115, :982). Check the V path, inclusive MAX bounds, sprite UV
      fixed-point at cell edges, TEX0 TBP/stale upload, CLUT CSA slice
      (upstream `feature/iop-emulator` reworks CLUT). T47's PCSX2 frames
      confirm; then a small GS fix brief (E lane owns the fork).
- [x] **X1 (local Qwen, 09-22): PARTIAL.** Caller tables usable as leads;
      its syscall labels were wrong (0x423DC0 = SignalSema, 0x423DE0 =
      WaitSema, not Open) and its conclusions are discarded
      (`local/research/X1/ORCH-CORRECTIONS.md`). Corrected reading: the stall
      is PCSX2's normal mid-load sema spin that never ends because the
      recomp's CD read loop stops at ~478 s.
- [ ] Snow Jam stall, next: why the `_sceCdSC` read loop stops early (after
      E33 frees the lease): one boot with CD/SIF RPC tracing to the stall,
      last N CD requests vs T47's healthy sequence.
- [ ] If 99% is a hang: diff the recomp's loading-window trace against
      T47's PCSX2 trace (SIF RPC IDs, sound driver/libsd, CD reads).
      Likely next piece: an SSX 3 sound-driver module in the IOP layer
      (no handler exists today; `Audio.cpp` covers libsd transfers only).
- [x] **E30 PASS (09-22, design):** zero packets = correct parser + host
      latch. Each 5,040 B chunk is one unterminated picture; the terminator
      is in chunk 2, which is never requested. Fix: `e30-fix.diff`
      (re-dispatch while decoder-accepted bytes flow without frames, cap
      4096 rounds). Regression: `e30-regression.diff` (R7–R11, suite → 464).
- [x] **Fork history scrubbed (09-22):** `[E17]` had pushed generated guest
      code (full `register_functions.cpp`, `ps2_recompiled_functions.h`, 5
      `sub_*.cpp`) to public `fork/ssx3`. Rewrote 19 commits across 6
      branches (only those 7 paths changed); Brad ran the force-push with
      leases. `ssx3` `3adc0478` → `3d4feed`. No fork ref reaches `e63f161`.
      Old SHAs stay fetchable on GitHub until its GC.
- [ ] **Recomp image jitter (Brad, 09-22) = field bob.** `SMODE2=0x1`,
      full 448-line buffer, and the CPU backend shows even/odd lines
      doubled, alternating per vsync (224/224 identical line pairs in
      every dump). Fix `PS2X_DEINTERLACE=weave` (default) is folded into E32.
- [x] **E32 PASS (09-22): one primary branch.** `fork/ssx3` `3d4feed` →
      `e57b5f8` (12 commits, ff push): codegen dir (generated code now out of
      tree at `~/dev/ssx3-work/codegen-ssx3`, 273 MB), drop-in-tree, iOS
      bundle name + FFmpeg wiring + MPEG diagnostics, `PS2X_SKIP_MOVIE`,
      `PS2X_PAD_SCRIPT`, `[diag:frame]` tap, `PS2X_DEINTERLACE` (default
      weave; 0/224 doubled line pairs). Suite 463/463, boot (a) = e28a park,
      (b) Main Menu → Select Character. Runner-dir check empty. Orchestrator
      verified: remote head, runner check, and all 15 side branches
      content-contained in `ssx3` (`git cherry` + file compare for the
      map/tap rows).
- [x] **Pruned the 15 folded fork branches** (Brad approved 09-22); fork heads now `main`, `ssx3`, `feature/iop-emulator`. Was: `git -C ~/dev/PS2Recomp push fork
      --delete e29-movie-bypass i23-ffmpeg-ios i8-device-bundle-name
      archive/i10-codegen-dir archive/i10-codegen-dir-alt archive/i11-map …
      archive/i17-map archive/i18-tap archive/i21-drop-a archive/i21-drop-b`.
- [x] **E33 PASS (09-22):** `PS2X_PAD_SCRIPT_CLOCK=vsync` (route reaches the
      race on the mini) + `PS2X_GFX_STATS`; suite 472/472; pushed
      `e57b5f8..03d6549`. **H1 shows:** Select Character 498/583 VU1
      programs/vsync hit 65,536 cycles with no E-bit, never resumed; race up
      to 166/573. **Fix negative:** resuming to the E-bit (16 slices) burns
      17× cycles with byte-identical kicks/draws, Zoe still absent: the
      programs are *stuck*, not long. `03d6549` to be reverted (E36).
- [x] **E36 PASS (09-22):** reverted `03d6549` (`0d40e2a`); `PS2X_VU1_TRACE`
      (476/476; pushed `…018f56b`). All 498 stuck programs (8 startPCs, stable
      every vsync) run one vertex loop 0x418–0x548 whose exit `IBNE vi03,vi13`
      never meets: vi13 starts thousands past vi03. B (flag wait) and C's
      branch/delay-slot variants ruled out; A (wild bounds from the setup
      path) leads, provenance not captured → no fix. Orchestrator correction:
      T48's PCSX2 startPCs are in 8-byte units, so its 0x0/0x2/0x8/0x73 **are**
      our 0x0/0x10/0x40/0x398: the same programs finish in ≤2,090 cycles there.
- [x] **E37 PASS (09-23):** `PS2X_VU1_ENTRY_TRACE` (480/480, fork `11725b4`).
      Neither stuck program (0x10, 0x40) ever writes **vi03** (the loop limit)
      or initializes vi11/vi13/vi14: only relative bumps from inherited entry
      values (vi13 0xd549/0xdbb0, vi03 0xC224), wild for row pointers. VU mem
      reads in the setup all hit zero rows. So the bounds come from VI state
      set *outside* these programs: candidates (1) another VU1 program that
      runs first each frame (PCSX2's 0x257 = byte 0x12B8) and sets them,
      (2) VU0 writing VU1's registers via the VU0-data mapping (0x4000+).
      T49 asked to print all 16 VI at entry (and trace 0x257 if it runs first).
- [x] **T49 PASS (09-23):** PCSX2 entry trace, same format. Healthy entry VI
      small and stable (vi13 0x03e4); **VU1 code differs**: PCSX2's 0x10 = `B
      0x258`, 0x40 = `B 0x7d8`; PCSX2 feeds 38 `MPG` uploads per pass window.
- [x] **E38 (09-23): TTE fix correct but not the cause.** Walker now honors
      CHCR.TTE for all tag ids (483/483, fork `7f022ed`); boots unchanged
      (0x10 still `LQI`, 498 stuck). MPGs do land (16 in the 0x12B8 packet;
      0x12B8 code matches PCSX2 word for word). Orchestrator follow-up: our
      `MPG addr=0` payload carries `81d26b7c` at slot 2 = what we run, so the
      recomp runs what it's given; PCSX2's `B` at slots 2/8 comes from **an
      MPG we don't apply**. The VIF1 MPG handler has three silent drop paths
      vs PCSX2 (imm ≥ 2048 dropped instead of masked; payload past the buffer
      end dropped, no carry-over; clip instead of wrap).
- [x] **E39 PASS (09-23):** `PS2X_VIF_MPG_LOG` (491/491, fork `0e9b5d0`):
      37,596 MPGs in vsyncs 0–1377, all copied, no drop path fires; every
      `addr=0` upload carries our `LQI` at slot 2.
- [x] ~~Missing per-frame DMA pass~~ **refuted by E40 Part 6** (fork `338ad99`): the recomp kicks both sites every vsync, its VIF1-end handler drives the state 5→0→1→2→3→4 like PCSX2; the second chain's CALLs simply point at uploader `0x435bd0` instead of `0x434990`. **E40 Part 7:** whole-boot write watch on those CALL tags' ADDR words (0x63b994/0x63bbe4/0x63bea4/0x63c134 …) to catch the chain builder and its table index. Original note:
      (orchestrator, 09-23, from T50 + a read of
      `sub_00382760`):** PCSX2 uploads microcode from two uploaders per frame
      (`0x435bd0` ×4 and `0x434990` ×2) and kicks from two paths in the render
      DMA thread (ra `0x382938` and `0x3827e8`); the recomp only ever takes the
      first. The thread's state word `*(0x61ba60+0x5A8C)` (EE `0x6214EC`): 0 →
      kick pass 1 and set 1; non-zero (≠5) on wake → kick pass 2. In the recomp
      the thread always wakes with state 0, so pass 2 (microcode set A + its
      MSCALs) never runs and those MSCALs execute set B's code. Suspect: the
      interrupt/completion model (DMA-end/GS handler that advances the state
      and signals the sema). **T51 (PCSX2) running; recomp side = E40 Part 6
      after Part 5.** T50 PASS (3d89659).
- [ ] **Independent frontier review (09-23, Fable, read-only) → new lead: VU0.**
      Reframes the chain: the VU1/microcode links are the *victim*; the rider
      object's scratchpad item lacks both mode 6 **and** its per-frame packet
      pointer w3 (recomp `0x30/…/w3=0` vs PCSX2 `0x1b0/…/w3=0x6efd00`), so the
      object's per-frame build never happens. Orchestrator-verified runtime
      facts: `processVIF0Data` has **no MSCAL/MSCALF/MSCNT/BASE/OFFSET** branch
      (unknown opcode → `break`, packet tail lost); `executeVU0Microprogram`
      runs VU0 with a **4,096-cycle silent budget**; SPR DMA implements normal
      mode only (chain/interleave kicks copy nothing). Reviewer also flagged:
      statefile captures (T56) can't prove "baked pre-load"; E38's 0x12B8 entry
      vi03 already differs. Probes: **E44 Part 2** (VIF0 unknown-opcode census,
      VU0 call trace with budget hits, 0x809670 watch incl. SPR_FROM) + **T57**
      (PCSX2 VU0 calls + VIF0 census). Dropped assumptions: uploader index as
      root cause, "baked in data", asset loading, VU1 as suspect.
      **T57 PASS (8416522): healthy PCSX2 runs zero VU0 micro-programs and zero
      VIF0 words at settled SC (913 vsyncs, hooks proven live); PCSX2 interp has
      no VU0 cycle budget.** VU0 is not active in the steady state, so the VIF0
      MSCAL gap / 4096 budget can only matter at scene build (still a fix-later
      item). **E44 Boot A (67e879c):** recomp item 0 is a multi-producer slot
      (`sub_00376938` store64s + toSPR from `0x80b270`/`0x80ea70`); window
      1270–1280 missed the 0x30 stager (cap closed in vsync 1270). Next:
      E44 Boot B (Part 2 taps) + Boot C (last-writer at the 0x362f68 walk,
      vsyncs 1355–1400); **T58** (PCSX2 scene-build writer of the
      `0x809670`/`0x809b70` buffers incl. fromSPR/SIF, from a pre-SC state).
      **E44 Part 2 + Boot C PASS (8e8aa2a, fork 571579e):** zero VIF0 kicks, zero
      VU0 micro-calls, zero SPR MOD≠0 kicks in the recomp too. **At both walks,
      the recomp's item 0 is the toSPR copy of EE `0x809670` =
      `(0x30, 0x814884, 0x2a0, 0)`**; PCSX2 copies the same buffer =
      `(0x1b0, 0x814884, 0x2a0, ping-pong w3)`. w1/w2 agree; **w0 lacks `0x180`
      and w3 is static 0.** Correction (orchestrator codegen read):
      `sub_003629B8` is renderer init (called once from `sub_00375A08@0x375e78`)
      and its `ori 0x180` stamps word +4 of a render-state template, not item
      w0. Dropped as a candidate. Next: **E44 Part 3** (whole-boot writer of
      `0x809670`/`0x809b70`, every path) ∥ **T58** (same buffers, PCSX2 scene
      build).
      **T58 PASS (be208f8), elimination-grade.** In PCSX2 the rider buffers are
      zero until the MENU: kernel zeroing, then a game memset (pc `0x41628c`,
      ra `0x394db8`, a stride-0x80 table at `0x8095f0`). They're full
      (`0x1b0`) at settled SC, but no hooked path writes them between MENU
      and SC. There's also no VU0 anywhere from cold boot to settled SC, and
      VIF0 does only mode setup. Orchestrator reading: T58's fold
      (`& 0x1FFFFFFF`) misses UCAB (`0x30000000`) stores, and SSX 3 uses
      UCAB for DMA-bound data. The recomp maps UCAB correctly. **T59**: fix
      the fold, then one MENU→SC capture.
      **T59 PASS (a9dce3a):** the fill is plain UCAB EE stores every vsync at
      `0x379804/0x37980c` (ra `0x379780`). End dump: w0 = `0x1b0` in both
      buffers. **E44 Part 3 (7a582e5):** its "no EE writes after vsync 41"
      comes from the same fold blind spot (`ps2_e44_trace.h:296`); the CD
      streaming suspect is dropped. **Orchestrator codegen read:**
      `sub_00376938@0x379784–0x379820` is a render-list append. Header
      `*(s2+0x18F0)` = list at `0x8095f0`; item N = `*(s2+0xE84)` template
      words 0–4 + s4 + packet + a0. So item w0 = the template's w0 at
      append time, and the recomp's template has mode 0 where PCSX2 has
      mode 6. Next: **E44 Part 4 ∥ T60**, the same trace on each side
      (`app` at `0x3797ec` + `tpl` changes to the template), to find the
      mode-6 setter.
      **T60 PASS (d564e16), structural:**
      - The template is fixed at `0x61c8fc` and cycles every vsync during
        MENU: tw0 `0xcc→0→0xc→0xcc` (setters `0x1a2618`/`0x397fc4`/
        `0x379c28`).
      - Two double-buffered lists (`0x6efd00`/`0x623080`) restart at count 1.
      - `0x3797ec` appends only counts 1–6 and 37+; other appender pcs
        exist.
      - The caps filled during MENU with no `0x1b0` seen. Next: T61 (PCSX2)
        and E44 Part 4 (recomp), both value-filtered to mode≠0, plus a mode
        histogram per vsync and an appender pc census.
      **T61 (22f8123): null, but only because of the filter.** `& 0x3C0`
      admitted mode 3 (`0xcc`), which filled the cap by vsync 100, before K
      (1025). The census is still useful: the item area is written by 6
      appender runs. Two run always; `0x37a208` is MENU-only; three are
      SC-scene appenders (`0x37ad5c/0x37b48c/0x37b4ac` in `sub_0037A430`,
      onset right after K-up). Orchestrator codegen read: these use the same
      template-copy pattern (`*(s0+0xE84)`, copy sites `0x37ad44`/
      `0x37b474`). Next: **T62 ∥ E44 Part 4 (amended)**, with an exact
      mode-6 filter, the post-K window, the three copy sites, and an exact
      `0x1b0` value watch.
      **T62 PASS (15c09f8): two templates.** The SC appenders (`0x37ad44`,
      `0x37b474`, ra `0x37a958`) copy template 2 at **`0x61c910`** (menu
      template `0x61c8fc` + 0x14), and its **tw0 = `0x1b0` from the first
      read (K+66)**. Item 0 at SC comes from `0x37ad44`. No store to either
      template happens in the post-K window, so template 2's value was
      written earlier. Next: **T63** (PCSX2, cold boot → MENU → SC,
      change-only watch on `0x61c8fc..0x61c94b`) ∥ **E44 Part 4
      amendment 3** (the same watch + `appx`: do the SC appenders run in
      the recomp, and what tw0 do they read?).
      **T63 (83cf3e0): bounded, not caught.** The template array is runtime
      BSS: init at vsync 1021 (`0x36927c/0x369534`), then the menu fills
      template 2 = `{0xc, 0x1414294, 0x1c0, 0, 0xffff0613}`, and during the
      menu its w0 flips `0xc↔0xcc` (`0x3798d8/0x379ba0/0x399674`). The
      `0x1b0` write is an EE store in (K−1011, K+104] (no DMA, ever); the
      cap died on the churn at vsync 6. Next: **T64**, the same run with
      the churn values excluded and an uncapped per-vsync t2 line.
      **ROOT CAUSE FOUND (09-23, orchestrator, from T64 7483a82 + E44 Part 4
      250ba18 + boot log e44e):**
      - PCSX2 sets template 2's mode 6 through `0x396b40`
        (`w0=(w0&~0x3C0)|0x180`), called via `jalr` from `0x37a6a0` in
        `sub_0037A430`; `0x37a6fc` then ORs `0x30` → `0x1b0`.
      - In the recomp, `0x396b40` isn't in the function table: the Ghidra
        sweep CSV merged a getter cluster into `sub_00396958`
        (`0x396958–0x3970f8`).
      - `dispatchGuestBranch`'s default `ContinueToTarget` policy **silently
        skips** missing indirect calls. The e44e log shows
        `missing-target source=0x37a6a0 target=0x396b40` ×1040.
      - Consequence: template 2 = `0x30` (mode 0) → no mode-6 draw records
        → no set-A microcode → stuck VU1 → no 3D.
      - Nine other missing indirect targets exist (`0x30db90` ×25, …).
      **Fix: E46**, which makes the census targets real entries, regenerates
      codegen into a new dir, then validates the rider at SC and 3D in the
      race.
      **E46 PASS, partial (65b1c00):**
      - Mechanism: `extra_function_starts` in `ssx3.toml` → resume entries
        (same path as direct-call interior targets). An empty-list regen is
        byte-identical; 591/591.
      - **`0x396b40` alone: item-0 w0 = `0x1b0` (297/297), menus render,
        and the Happiness race is reached with a live HUD. The race world
        is still dark.**
      - The census has 18 targets. All 18 at once → black at tick 246; the
        breaker is among the first firers (`0x3b1140/0x14e130/0x144928/
        0x30db90`).
      - A new target, `0x32f8b0`, appears once `0x396b40` runs. There's no
        SC still yet.
      - The static data-pointer scan found 1686 hits and none of the census
        targets.
      - Part 2: bisect the breaker (4 boots on both slots), then all-but-
        breaker + snaps at SC, then the race.
      **E46 Part 2 PASS (539e6ec, fork `2e21cdc` pushed): THE SELECT
      CHARACTER RIDER RENDERS** (`local/research/E46/frames/e46h-sc-rider.png`).
      - 18 boot-proven `extra_function_starts`. The breaker `0x3b1140`
        (refcount release + unlink of node `0x548840`) is excluded:
        enabling it blacks the screen at tick 246.
      - Race reached with gameplay working, but the **world is dark**; only
        `0x3b1140` ×3 is still missing.
      - Relaxed rescan: 1210 data-referenced interior candidates (census
        recall 18/19), report-only.
      - Codegen swap (orchestrator): `codegen-ssx3` = E46g (canonical);
        `codegen-ssx3-pre-e46` kept for A/B; breaker repro in
        `codegen-ssx3-e463b1140`.
      Next (Opus panes):
      - **E47:** race-world triage (GFX/VU1/draw-census/MPG, SC control
        vs race).
      - **E48:** the breaker (code read + watch boots; hypothesis: the
        skipped release leaves UI nodes drawn = the stray glyphs).
      **E47 partial (1e78f81):** SC control is healthy and steady: 0
      budget-exhausted VU1 programs (was 498/583 pre-E46), 611 MSCAL, 5,079
      draws/vsync, draw modes 3 + 6. The race boot was starved by E48's
      parallel builds (0.6× tick rate) and ended on the pre-race rules
      screen. It's rerunning on a quiet host. Tool notes: the gfx-stats
      `top` field is (FRAME.fbp, PRIM.type); the E43/MPG logs flush every
      128 lines, so SIGTERM drops the tail. **E48 early:** `0x548840` is a
      movie-codec picture node used only during startup movies. So the
      breaker may be an artifact of `PS2X_SKIP_MOVIE`.
      **E48 PASS (147193e): breaker explained; the glyph hypothesis is
      refuted.**
      - `0x548840` is the single pool node of the startup-movie codec
        (`PS2_SONY_CODEC_INTERNAL`, vtable `0x456850`).
      - The guest ends a movie when `0x402b38` reads a nonzero
        `[[mpeg+0x40]+0]`, but the MPEG HLE only ever writes 0 there.
      - Today the skipped release leaks the node, the 2nd alloc returns 0,
        and that ends each bypassed movie (two bugs cancelling out).
      - With the release enabled, movie 1 plays blank frames forever
        (2,493 cycles in 120 s) → black.
      - The unlink is clean. The stray glyphs are NOT this node (present
        with no codec activity), so they're still open.
      - E46's "3→2→1→0" corrected: it's 3 × `1→0`, one per movie.
      **Next: E49**: the MPEG HLE writes the end word, plus
      `0x3b1140` in `extra_function_starts`, validated against E48's
      predicted observables (runs after E47's race rerun).
      **E47 Part 2 PASS (db3e595): race world = geometry off-screen.**
      - The race issues ~6,500 PATH1 tstrips/vsync.
      - VU1 is clean: 0 budget exits, all 693 MPG uploads copied.
      - GS state is sane; color and Z are both empty in the world area, so
        it isn't a Z/alpha/clear problem.
      - **The PATH1 xy box is pinned to 1023.5–3071.5 on both axes every
        vsync** (viewport 1792–2304 × 1824–2272), and every 3D tail draw is
        off-screen. SC's box is inside the viewport.
      - Race draw modes are m3 ×9 + m1 ×1 (no mode 6).
      Hypotheses H1–H4 refuted or unsupported. **Next: E50 (recomp) ∥ T65
      (PCSX2)**: on/off-screen counts, first-N draw ring, VU1 data-memory
      matrix dumps at a race world program (plus SC control), and the EE
      builder of the matrix (VU0 macro / FPU ops suspect).
      **T65 PASS (30f22d0): the pinned box is NOT a symptom.**
      - PCSX2's race box is also 1023.5–3071.5 (the viewport transform
        maps NDC ±1 there), and ~13% of healthy race prims are off-screen.
      - PCSX2 race per vsync: ~16.7k on-screen / 2.9k off / 870 straddle /
        4.8k ADC / ~27.6k PATH1 verts, vs ~6.5k draws total in the recomp.
      - The camera (view×proj) sits at VU1 data qw 0–3, with invariants
        (orthogonal x/y/w, |w| = 1, |x| = 0.266262, |y| = 0.310638 in the
        race).
      - E50 redirected to those invariants and to prim-volume/program
        census diffs.
      **E49 PASS (e5be03a, fork `b48b502` pushed):**
      - The MPEG HLE writes the `sceMpegIsEnd` word (`[[mpeg+0x40]+0]`,
        read by `0x402b38`) once the stream has ended with the queue
        drained. Create clears it (mirroring the stock Create→Reset).
        `0x3b1140` is enabled (**19** `extra_function_starts`).
      - Boot A (bypass) meets all 6 E48 observables: menus at t258, rider,
        race. Zero missing-targets. Suite 592/592; the new test fails on
        the old runtime.
      - Faithful path (bypass off): stalls in movie 1's GetPicture wait
        (15 CD reads, then none), the E30 shape → **E34**.
      - To do: promote `codegen-ssx3-e49` (2 files differ) to canonical
        once E50 finishes with the current tree.
      **E50 PASS (6c84d91): the camera is wrong.**
      - The recomp's camera block fails T65's invariants in the race
        (|w| 1.21, dots ~3e-2) and at SC.
      - At SC the error is exactly **R + 0.4438·I**: the view rotation is
        wrong and the position is right.
      - Traced by a value watch to a **wrong quaternion at `0x00bc5950`**
        (object `0x00bc5920`), read by the quat→matrix routine
        `sub_0015D928`, whose COP2 translation reads correct. The recomp
        has q ≈ (0,0,0.527,0.948), |q|² 1.18; expected (0,0,√½,√½).
      - The race runs only 5 of PCSX2's 22 VU1 startPCs (191 vs ~691
        MSCAL/vsync) and 4.8k vs 16.7k on-screen prims. That fits culling
        against a bad camera (untested). SC per-startPC MSCAL counts match
        PCSX2 exactly.
      - New dev taps on `e50-diag`: T65-format counts, `PS2X_E4_HEAD`,
        entry trace `all`, `PS2X_E50_VALWATCH`.
      **Next:** E50 Part 2 (the quaternion writer → the first wrong op →
      a unit test → one fix + SC/race validation) ∥ **T66** (PCSX2 value
      and writer at `0x00bc5950`).
      **T66 PASS (8289688): E50's model confirmed exactly.** In PCSX2,
      q = (−0,−0,√½,√½), pos (0,200,0,1). It's written once (K+10) by
      `sq a0,0x30(s0)` at `0x15e0d4` in `sub_0015E050`, from a work struct
      built from two input vectors and processed by `func_166640(sp,1)` +
      `func_166F90(sp)` (look-at → matrix → quaternion?). Header +0x0c =
      π/4. Passed to E50 Part 2 as the bisect target (suspect: sqrt/div in
      matrix→quat).
      **E50 Part 2 (655b1aa): two FPU translation defects** in the guest
      sincos `0x31BE50`:
      - **CVT.W.S rounds** (`nearbyintf`), where the EE truncates. 992 sites.
      - **SQRT.S reads `fs`** (always f0), where the EE reads `ft`, and
        `sqrtf` gives NaN on negatives where the EE takes sqrt|x|. 107
        sites, 36 with ft≠fs. RSQRT.S has the same field bug (0 SSX 3
        sites).
      At π/2 this gives sin/cos = (1.0000036, −0.797886) → q (0,0,0.527,
      0.948) → R+0.4438·I. It reproduces exactly. There are 4 failing unit
      tests, and neither fix alone passes (offline replay). **Orchestrator:
      option 1, A+B (+RSQRT) as one R5900-FPU fix on `ssx3`**, with a regen
      to `codegen-ssx3-e50` and SC + race validation.
      **E50 Part 3 PASS (2f00b34; fork `eac6cba` PUSHED by orchestrator):
      THE CAMERA IS FIXED.**
      - SC camera within 1 ulp of PCSX2; the race meets every T65
        invariant.
      - Regen diff = exactly the 36 predicted SQRT.S lines. Suite 597/597.
      - **The race world now draws:** sky, sun and flare, fog, the terrain
        surface, rider, trail (`E50/frames/e50f-race-tick8275.png`, sent
        to Brad).
      - Still differs from PCSX2:
        - the terrain is dark/untextured with blue shards;
        - zero-area prims ~2.3k vs ≤461;
        - VU1 budget exits 1–2/vsync;
        - startPCs `0x741/0x2/0x8/0xe0/0x28c` missing, `0x189` extra.
      - Canonical `codegen-ssx3` = E50 regen (orchestrator swap);
        `codegen-ssx3-e49` kept until I25 is done.
      **Next (Opus):**
      - **E51** (E50 pane): race terrain at a moment matched to T65,
        covering VU1 budget exits, TEX0/upload census and zero-area
        sources.
      - **E52:** a full FPU + COP2-macro semantics audit vs PCSX2, with
        unit tests and no fixes.
      **E52 PASS (4856429): the audit found 27 of 30 tests failing on
      `eac6cba`.**
      - Structural:
        - **VSQI (14 sites) has swapped fields and writes EE RAM
          0x0000–0x3FF0 instead of VU0 data**; VLQI reads EE.
        - **VCALLMSR (8) reads `vi[27]` out of bounds instead of CMSAR0.**
        - CTC2 CMSAR1 doesn't start VU1.
        - VRNEXT never writes ft.
      - Special values:
        - DIV.S x/0 → Inf (802 sites; PCSX2 gives ±FMAX);
        - VDIV/VSQRT/VRSQRT give 0 on edge inputs (479 sites);
        - VFTOI0 positive overflow gives 0x80000000;
        - MAX/MIN/C.cond are wrong on edge inputs.
      - FP model:
        - clang fuses FPU MADD into `fmadd`;
        - the EE thread runs IEEE round-to-nearest with no FTZ, where
          PCSX2 uses RTZ + DAZ/FTZ + Inf/NaN clamps.
      **Next: E53** (E52 pane): batch 1 covers the structural and
      special-value fixes, `-ffp-contract=off`, and EE-thread RTZ+FZ
      (env A/B switch). SC + race validation; G2/G3 clamping deferred.
      **E51 (a248b6a), handed back to E53:**
      - The recomp streams ~1 texture IMAGE upload/vsync vs PCSX2's ~73.
      - Terrain TEX1 K is saturated (0x801) vs PCSX2's per-object K.
      - Only 4 VU1 programs run.
      - Lead: the camera's per-object visibility test `sub_0037DE88` runs
        `vcallmsr` at **0x37deb8** after `ctc2 → CMSAR0`, which is exactly
        E52's VCALLMSR defect. So visibility is wrong, objects are dropped
        and textures aren't streamed.
      - UVs are sane. VU1 budget exits unidentified (none in this window).
      - **The race is not reproducible run to run at the same tick**
        (e50f 2ND/19 programs vs e51a 1ST/4 programs at 00:00:19). This is
        an open determinism concern.
      **E53 (d1fb1d1): batch 1 in, fork `e52-audit` `d3f7508` (local)**:
      - suite 630/630; FMA 228 → 0; the codegen diff is exactly the audited
        sites; log@0x40D610 is unbound; the VU1 EFU decode, latency and
        name tables follow PCSX2;
      - SC matches T65 exactly;
      - VU0 microprograms now really run (1.67 M starts; the 0x37deb8
        visibility test included);
      - **the pre-race frame (tick 6131) shows snowy terrain where E50 had
        shards** (viewed);
      - the race slows from ~17 to ~6 ticks/s at race load (~830 VU0
        calls/vsync, per-call cost), so the race window wasn't reached
        within 600 s.
      **Gate:** accepted. Part 2 = one 900 s race boot (cap exception) with
      `sample` profiles plus the deferred race measurements (TEX1 K,
      counts, frames). The FPMODE A/B is deferred. Fold into `ssx3` + promote
      the codegen after Part 2. The VU0 per-call cost goes to E57 (speed),
      or ahead of it if the profile shows a cheap fix.
      **E53 Part 2 (afa2ce7), accepted:**
      - Profile: VU0 is only 3% of the EE thread. The VU1 interpreter
        (39–46%) and the software GS (37–45%) now carry far more geometry
        and fill.
      - Race camera = T65. TEX1 K is per object (0x801 only on 490 prims
        of 0x2270; an unexplained −52…−65 group).
      - All 5 programs missing in E50 now start; MSCAL matches T65.
      - Viewed (tick 8274): whole snow slopes, ridges, trunks, rocks, the
        rider's spray trail and the HUD. **But the sky and sun are gone**
        (E50 had them), there's no foliage, textures look flat, and there
        are dark regions. Zero-area prims are still ~15× T65; 9 vsyncs
        have 33 capped VU1 programs.
      **Next:** E58 fold (Codex Sol), then **E59: sky loss + flat
      textures**: a FPMODE ieee/ps2 A/B race boot, then a GIF diff vs
      PCSX2 at 8258–8265 for the sky program and 0x2270/0x22c8, plus
      zero-area.
- [ ] **Scene builds fewer objects (orchestrator, 09-23, from T51 PASS):**
      PCSX2's Select Character chains hold 4 extra uploader CALLs (→ set A
      `0x434990`, at 0x63d430/0x63dcb0/0x70a0b0/0x70a930) that the recomp's
      chains lack; both share the 4 CALLs → `0x435bd0`; chain arenas sit at
      different heap addresses (PCSX2 TADR 0x63c560/0x63ca70 vs recomp
      0x63b8a0/0x63bdb0); no post-load writes on either side (baked at scene
      build). Lead: assets that never load (ties to the Snow Jam CD-read stop).
      E40 Part 7 PASS (fork `9840542`): the recomp's CALL-tag ADDR words are **never
      EE-written in the whole boot** (0 stores, 0 loads of either uploader), so the
      display-list data arrives via DMA/host copy from loaded data. **T52 PASS (PCSX2, `3f6df70`):**
      5,836 reads/149 MB boot → SC; the menu → SC transition reads `MDLPS2.BIG`
      (83 sectors, rider models) + `ZOETXP.BIG` (59, Zoe textures) + `MUSIC2.BIG`
      streaming; SC on screen = music only. **E41 PASS (fork `7d7bbc6`):**
      the CALL words are **EE-stored every even vsync** (185 plants, `0x435bd0`,
      via the fast-write path / an uncached mirror: E40's blind spots), not planted
      by DMA. Orchestrator: the recomp's `MDLPS2.BIG` + `ZOETXP.BIG` reads equal
      PCSX2's sector for sector (165/165): **asset loading refuted**. The uploader
      choice is an EE computation per frame. **T53 PASS (`db1697e`):** PCSX2 stamps
      `0x434990` at pc `0x365994` and `0x435bd0` at pc `0x3651d8`, both inside
      `sub_00364CD0` called from the render-list walker `sub_00363C20` @`0x363cf4`
      with mode `a1 = (*(record) & 0x3C0) >> 6`; its 9-entry jump table (@`0x492040`)
      is translated correctly (orchestrator check). Mode 6 → set A, mode 3 → set
      B, so the recomp's render list lacks mode-6 records. **E43 + T54 (draw-record
      census by mode + mode-6 producers) queued/running; E42 PASS (`6dd0c73`): the recomp's
      stamper is the same `sub_00364CD0` mode-3 path (@`0x3651d4`), never the mode-6
      path. E43 continues in E42's pane.**
      **T54 PASS (`16ddf3b`):** PCSX2 walks 6 records/vsync at SC (4 mode-3 w0
      `0xcc`, 2 mode-6 w0 `0x1b0`); the mode-6 records are written each vsync inside
      `func_394ED0` (stores `0x394fdc–0x394fe8`), called **unconditionally** from
      `sub_00362DE8` @`0x362f68` with an 8-bit hash folded from the record's 4
      words. E43 now logs those calls (items, hash, return); **T55** the same on
      PCSX2. Separates different input items vs a hash (shift/sign) semantics bug.
      **T55 PASS (`567331a`):** PCSX2 calls it 224×/vsync = 2 passes over a
      **112-item table in scratchpad** (`0x70000000–0x70003780`, stride 0x80,
      `a0=0x8095f0`); items `0x70000000`/`0x70000500` (w0 `0x1b0`) yield the two
      mode-6 records every vsync. New suspect: how the scratchpad item table is
      filled (EE stores vs toSPR DMA) in the recomp.
      **E43 PASS (`f2ced36`):** the recomp's hash is bit-exact (10280/10280); its
      scratchpad items lack w0 `0x1b0`: item `0x70000000` has w0 `0x30` (PCSX2
      `0x1b0` = `0x30 | 6<<6`). The mode-6 bits are never set on that item.
      Orchestrator: generated LDL/SDL merges checked correct. **T56 PASS (`4469b04`):** in
      PCSX2 the mode-6 items are copied into scratchpad each vsync by **toSPR DMA**
      (pc `0x371d90`, ra `0x38f53c`) from EE `0x809670` / `0x809b70`, whose w0 is
      already `0x1b0` and is never EE-stored in-window (set at scene/asset build).
      **E44 (recomp side) running**; next: whole-boot store watch on `0x809670`
      (w0/+4) on both sides to catch the descriptor builder. E40 lane closed (7 parts).
- [ ] **Microcode source offset differs (orchestrator, 09-23):** our `MPG
      addr=0` source is EE `0x435bf8` (ELF off `0x336bf8`); PCSX2's slots
      0/2/8 (`B` to the epilogue) sit at EE `0x4349b8`, 0x1240 bytes earlier
      in the same microcode library. So the game computes a different source
      offset: game state or a mis-recompiled EE instruction. **E40 + T50
      (paired):** E40 Part 1 PASS (09-23, fork `9b82d35`): **zero** REF tags carry
      these MPGs (12,160 flowed inline) and neither address is a code constant:
      the game copies microcode from the library into packet buffers with EE
      code. Part 2 PASS (fork `99b5fd8`, 503/503): **zero** EE loads of the library
      heads, so the bytes reach VIF only via DMA. Part 3 PASS (fork `78ed470`, 510/510): every frame
      `sub_382760` kicks two chains (TADR from struct 0x61ba60 fields +0x5AA8/
      +0x5A9C, double-buffered arenas 0x708520/0x63b8a0, 0x708a30/0x63bdb0,
      CHCR 0x185); each chain CALLs a **static uploader** in the library (RET
      tag @0x435bd0 carrying the microcode inline from 0x435bf8). So the choice
      is the CALL tag's ADDR the chain builder writes. Part 4 (fork `531c09b`): the chain is
      **baked at scene build** (no arena stores in 1300–1320; same chain with
      4 CALLs → uploader 0x435bd0 re-kicked each frame; 0x4349b8 never
      referenced); the builder loads the uploader address from table data
      (candidate `sub_00367DB8`: base + index×4). Part 5 (E40): arena store +
      "uploader address load" watch over the scene-build window 1150–1300. T50
      (PCSX2) logs mpgpay/dmareg to show which uploader it calls.
- [ ] E34 (after E33): apply E30's two diffs on `ssx3`, then 464/464, then an A/B
      boot with the flag off vs the bypass title screen (`e32-handoff.md`).
      Watch `round=` in boot logs: an empty-queue `sequence_end` spins up to
      the 4097 cap before parking (E30 residual 3). Mid-movie CD refill
      still can't wake a dry park (residual 2).
- [ ] Android handoffs from N1 (E owns the edits): H1 adopt
      `PS2X_GAME_CODEGEN_DIR`, H4 no-env `cdImage` derivation, H3 merge
      the C3/C5 MPEG vector diagnostics from `i23-ffmpeg-ios`, H2 an
      Android FFmpeg IMPORTED block, H5 entry-provider check, H7 non-env
      diagnostic triggers if N5 needs them.
- [ ] Older queue, check before briefing: `3006a07` cherry-pick onto the
      fork, K1 ret0 retirement, E2b/E2c (held since 09-20).

## G — GS composite / GPU backend (paraLLEl-GS `3a66c19` + carried G26/G28)

- [x] **G40 PASS (09-22): F2 execution-loss.** Composite prims 17/17
      accepted, texture input byte-exact cross-GPU, yet B unwritten on
      Odin right after the flush, even read behind a barrier. F1/F3
      refuted. The one CPU-side difference is the O4m texture-cache hash
      (`5a15…` vs `20dc…`); content-neutral.
- [x] **G41 PASS (09-22):** masked-write theory refuted: C2–C5 (incl.
      masked PSM1 and the composite's exact state) land byte-exact on the
      Odin. Only a plain PSM0 fill (C1) is lost, so B's loss depends on
      pass context (scale/target), not draw state. The O4m hash
      difference is garbage in padding (closed).
- [x] **G42 PASS (09-22, table + stop):** Turnip leg failed to start
      (`HAL has no GetInstanceProcAddr`). Orchestrator root cause: our hunk's
      `G42HalDevice` omits `hw_device_t.reserved[12]`, so it read offset 40
      instead of 136. The driver question is still open. The system control
      replicated G41-O1 **except C1 landed** (run variance or hunk perturbation,
      unseparated).
- [x] **G43 PASS (09-22): Turnip renders.** With the HAL layout fixed,
      Turnip (Mesa, API 1.4.359) initializes in the shell replayer; B lands
      with full coverage and the scanouts match the Mac to PSNR 70–78 dB
      (vsync0/first bit-identical; orchestrator compared by eye and PSNR),
      while the proprietary driver's scanouts stay blank and its canary
      losses vary run to run (G41 C1, G42 none, G43 C1+C4). **Verdict:
      proprietary Adreno driver fault; bundle Turnip** (Brad approved
      shipping Turnip). Sub-LSB differences vs Mac are accepted, not chased.
- [ ] N lane: bundle `libvulkan_freedreno.so` (Turnip v36, `717812c3…`) in
      the APK and load it through G43's HMI hook when the GPU GS lands on
      Android (GB1 step c). **N8A source map PASS (e80295b):** the folded
      backend calls Granite's null loader, while the staged Turnip exports
      `HMI` instead of `vkGetInstanceProcAddr`; G43's working HMI hook is
      only in the standalone replayer. N8B must port that hook into the
      Android app path and verify APK packaging and app-namespace loading.
- [x] **G44 PASS (09-23, Part 3): paraLLEl shadow works inside the recomp**
      (branch `g44-parallel-shadow` `460e438`+`8c45d1f`+`6cfede4`, 471/471, not
      pushed) with a diagnostic `PS2X_GS_SHADOW_FORCE_SMODE1=ntsc` override:
      200/200 scanouts, feeds in lockstep (53 dB on a fade after a 1–2 px crop
      shift). **H4 answered for the menu (orchestrator viewed `side-1190.png`
      vs `t47-shot-menu.png`):** CPU and paraLLEl draw the same frame,
      including the ghost controller diagram, button icons, R1/L1 boxes, D-pad
      and floating shard quads, and both lack PCSX2's 3D mountain backdrop and
      snowflakes. So the "sprite sheet" glitches are draws the game emits
      (upstream of the GS: VU1/VIF, same area as the missing rider), not CPU
      backend sprite cropping. Side note: PCSX2 greys out Multi Play/Online;
      the recomp shows them enabled (network/multitap state differs).
      Select Character pairs not captured (cap filled at tick 1199).
- [ ] **E lane: `SetGsCrt` (syscall 0x02) HLE should program SMODE1/SMODE2
      like the real kernel** (NTSC/PAL, interlace, field/frame). Today SMODE1
      stays 0, which blocks any real scanout backend (G44) and may matter for
      the CPU presenter too. Small brief after E39.
- [ ] Commit G26 + G28 in the clone after the storage cutover (G39
      decision: carried diffs until then), with a clean rebuild and G39's
      R1/R2 shapes re-run as proof.
- [ ] G22 env-gated sampler-feedback workaround needs its own gate. G18
      hunk adoption queued. O1 writer naming still open.
- [x] **GB1 PASS (09-22): bridge design** (`local/research/GB1/DESIGN.md`).
      Queue above tag decode at `submitGifPacket`/`GifArbiter`; commands
      gif_packet/reg_write/priv_write/upload_image_native/present/reset;
      sync = finish fence + FIFO/VRAM RPCs; CSR/vsyncTick stay atomics; the
      unmodified CPU backend is the byte-exact reference on the GS thread;
      upstream `feature/iop-emulator` doesn't move the seam (carry
      `LoadClut`, source GIF_STAT FQC from ring depth).
      Adapter authorship (gap 5): after E32, generated code is out of
      tree, so the fork can have multiple worktrees. G authors the
      paraLLEl adapter on its own fork branch; E folds into `ssx3`.
- [x] **GB2 (09-23, 3994985): step (a) built, fork `gb2-gs-queue` `c937929`**
      (not pushed; merges cleanly onto `ssx3`). `PS2X_GS_QUEUE=1`: GS thread
      + bounded FIFO + RPC fences. Byte-exact vs direct on synthetic streams
      and a 256-packet captured stream; 576/576. Its live-present boot A/B
      fails (84%), but the queue-off null control fails too (87%): live
      presents are torn at wall-clock-racy cut points, so that gate was
      unusable (orchestrator's gate design error). Guest trajectory is
      identical (park/semaphore histories exact). Queue-on presents are
      sparser (433 vs ~1320 over the same ticks); that goes to step (d).
      **Part 2 (969019d) FAIL, a real finding.** Quiescent VQ gate: priv
      regs identical 26/26, but VRAM differs from tick 100. Queue-on
      submits ~246 extra packets in ticks 0–300, then stays in lockstep.
      So the guest behaves differently during startup. Suspect: FINISH
      completes in-stream with no EE wait, and CSR reads aren't sync
      points (a deviation from GB1 §2c). Queue-on presents/s are 1.53 vs
      4.42 (2.9× fewer; goes to step (d)). **Part 3:** a packet/CSR-read
      diff to find the first divergence, then one fix (a CSR/SIGLBLID load
      drains the queue) + a vq validation.
      **Part 3 (79c17f9): no CSR read precedes the divergence**, so it's not
      the FINISH/CSR deviation (zero genuine guest CSR loads in ticks
      0–1300). The first difference is packet idx 352 (tick 80), a Path2
      64-byte post-VBlank packet whose content differs, every 9th packet
      through tick 91, then a 143-packet burst. Part 4: an off/off pklog
      null, then decode the differing bytes and their builder.
      **Part 4 (dab78ca):**
      - Off/off is deterministic. Part 3's "zero CSR reads" was a
        buggy-matcher false negative (corrected by the worker).
      - Queue-on runs the guest one tick early: the first CSR read
        (`0x375d10`) sees a different FIELD bit (`0x6000` vs `0x4000`), and
        content diverges deterministically at packet 49,793.
      - One queue-on boot in three showed a stale VIF1 packet replay
        (a race; open).
      - Part 5: validate `PS2X_GS_CSR_DRAIN=1` with the VQ gate.
      **Part 5 (58119f0) FAIL.**
      - CSR-drain doesn't restore queue-off VRAM (26/26 mismatch, both
        boots), and the two drain boots disagree with each other.
      - Byte decode: the differing qword is one fade alpha byte, lagging
        exactly one tick. So the queue shifts the guest's view of time
        through a non-CSR channel.
      - Part 6 (code read): where does guest-visible time couple to GS
        work in the direct path? Then park at step (a).
      **Part 6 (9e29912):**
      - VBlank is purely cycle-driven in our regime, and GS work charges no
        cycles. So the divergence enters through a racing guest read of a
        GS priv register (a non-CSR readback of the aliased `gs_regs`
        while its writer is still queued).
      - Recommendation: fence before every guest load in the GS priv range.
      - Part 7 validates it: 2 queue-on boots must match queue-off and each
        other.
      **Part 7 (564d18f), lane PARKED at step (a):**
      - With the full-priv drain, queue-on is **guest-timeline-identical
        to queue-off** (144,591/144,591 packets, 5,017/5,017 priv reads)
        and **deterministic** (the two on-boots are bit-identical).
        Present rate is back to off-level.
      - VRAM still differs. Mechanism: direct guest priv STORES
        (`write32` → `gsRegs` on the game thread) bypass the queue while
        packet A+D writes run late on the worker, so the rasterizer sees
        a different register order.
      - **Next (Opus, when picked up):** route direct priv stores through
        the worker in stream, then re-run VQ (expect 26/26).
      - Open: which pre-tick-80 wall-racy input picks the attractor when
        there's no drain (pinning / IOP-MPEG audit).
      - All code is on `gb2-gs-queue` `c5fd6f3` (not pushed).
- [x] **GB3 Part 1 (09-23, ec4f75a): stop-rule hit, but a real finding.**
      Fork `gb3-gs` `574354a` (local): priv stores go in-stream (unit test
      proves order; the negative control fails), and the priv-load fence is
      on by default when queued; 606/606. **SetGsCrt:** SSX 3 never makes
      syscall 0x02, so the `sceGsResetGraph` HLE stub now applies NTSC
      SMODE1 `0x740814504` (it matches the G13 PCSX2 dump). The CPU
      presenter is unchanged (26/26 and 80/80 hashes). VQ still fails 0/26,
      but packet 0 (the ResetGraph packet) already lands at tick 40 ± 1
      across boots, before any GS work. Queue-off boots hit the same
      attractors: GB2's baseline C was a +1 boot. **Gate read:**
      free-running VQ is retired as a queue gate. The CPU backend's VRAM is
      a pure function of the stream, so GB4 gates on capture + replay
      (direct vs queue vs paraLLEl). The ±1 timeline race is E55's
      (determinism mode; GB3 §0 has the host-paced idle-wait hypothesis).
      Fold SetGsCrt + queue into `ssx3` after GB4 Part 1 passes.
- [ ] **GB4 (Codex Luna):** capture/replay harness, queue gate by replay,
      then paraLLEl live on the Mac via replay PSNR and one live boot.
      **GB4 Part 1 (5d3c6a6):**
      - capture (`PS2X_GS_CAPTURE`, 4.7 GiB to tick 12,128, into the race)
        and the `PS2GSReplay` harness; 607/607;
      - direct replay vs live VQ fails at tick 100: replay `dc2e1eaa` vs
        live `43e5391b`. The replay value = gb3d's +1-phase tick-100 VRAM,
        so a marker offset is suspected;
      - gaps: unchanged-value priv stores (version skew) and local→host
        bytes.

      **Part 2 (Sol, fresh pane):** align markers by submit counts, fix,
      rerun; recapture only if needed.
      **Parts 2–3 (7ab3501, 5135026):**
      - the recapture's packets match the live boot 165/165 by submit
        count and on the first 5k packet hashes, and the priv regs match
        165/165, but VRAM doesn't;
      - bisect: the first divergence is **packet 479 (PATH1, IIP+ABE
        triangle strip)**, with identical pre-packet VRAM and identical
        bytes.

      **Orchestrator hypothesis:** PATH1 is rasterized inside the VU1
      interpreter's RTZ `fesetround` scope, while the replay uses nearest.
      E53's IEEE scope around `GS::processGIFPacket` (on `b9647f5`) should
      fix it; GB4's base predates it. **Part 4:** an RTZ replay switch
      (no boot), then move GB4 onto the fold and rerun the gate.
      **GB4 Part 4 (723d5bf): PASS, and the hypothesis is confirmed.**
      - Replaying the old capture with RTZ only on PATH1 packets
        reproduces live 120/120 (with RTZ on all packets, 82/120). So every
        pre-E53 build rasterized PATH1 under the VU core's RTZ; E53's IEEE
        scope fixes it.
      - On the fold (`gb4-fold` `13cac7f`, 548/548), a new I26-FAST capture
        to tick 3000 (2.75 GB): direct replay = live at 59/59 (VRAM, priv,
        Present). Queue replay = direct 60/60, twice. The drop-priv
        control fails 0/60 as expected.

      **Part 5:** a taps-ON suite + ff push of `gb4-fold` to `ssx3`, then
      paraLLEl by replay (PSNR + viewed) and one live parallel boot.
      **GB4 Part 5 (99b1554):**
      - **fork `ssx3` pushed `b9647f5..13cac7f`** (GB2/GB3/GB4: the queue,
        capture/replay, SetGsCrt via ResetGraph); suites 548 + 643 (taps
        ON);
      - paraLLEl (`gb4-parallel` `520bd61`) replays the capture with
        recognizable frames and no SMODE1 override needed;
      - PSNR 19–24 dB, confounded: at tick 2200 the CPU shows 00:00:08
        and paraLLEl 00:00:09, so a present offset. Real differences: HUD
        small-text glyph breakage;
      - the suite failed only because the backend env leaked into 3 unit
        tests.

      **Part 6:** isolate the env, fix the present offset, a clean PSNR
      table + a glyph diagnosis, then a live paraLLEl boot.
      **Part 6 PASS (f339909):** replay-only backend selection makes CPU
      and paraLLEl suites 556/556. paraLLEl replay processed 1,982,063
      packets and 60 presents with zero null/unsupported operations. A
      live queue+paraLLEl boot reached a race frame at tick 4548, without
      an SMODE override. Orchestrator viewed all five side-by-sides and
      the live frame. Setup Character text and race HUD glyphs have real
      broken strokes; terrain/edges also differ. CPU raw display-page 112
      equals CPU Present at each sample, and no consistent N±1 tick
      offset explains paraLLEl's image. The candidate PATH3 composite
      packet covers the damaged region but is not proved the glyph draw.
      Live 13.71 presents/s is **diagnostic**, not guest speed. Local
      `gb4-parallel` `c5913e4` is not pushed. **Next GB5:** isolate the
      first glyph producer/texture or raster divergence by replay, then
      fold paraLLEl onto the current fork for Odin/Turnip.
      **X5 PASS (1b3d3e9, sparse local Qwen):** the GB4 capture's ticks
      949–950 contain 461+461 = 922 GIF packets, indices 143805–144726.
      The streamed index matches the original pklog for tick, FNV, length
      and corrected path on all 922 rows; packet 144266 is PATH3, 1696
      bytes, FNV `cc6dd8df`. The orchestrator reran the validator, checked
      all 1,982,063 path indices and the capture-format source. The CSV
      is `local/research/X5/packets-949-950.csv`; it does not name a glyph
      producer.
      **GB5 Part 1 PASS (a6ade5d):** replay-only CPU page-112 crop probe
      checked all 922 X5 packets at ticks 949–950; **zero** changed either
      damaged text crop during packet processing. Final crop hashes
      (`1d75d1be`, `9cb9639d`) match the saved CPU raw PPM, independently
      recalculated by the orchestrator. Default and probe suites both
      556/556. No single candidate existed for an omitted-packet
      control. Local G probe commit `b7d3227` is not pushed. This excludes
      a CPU crop write by those sampled packets; it does not locate the
      earlier producer or explain paraLLEl's raster difference. Next:
      find the last earlier crop change or non-packet page update, then
      compare that exact state across backends.
      **GB5B diagnostic PASS (15688e7; G probe `f796669`, not pushed):**
      13 crop-changing packets at ticks 902–921 are instances of the same
      recurring PATH3 1,696-byte/FNV `cc6dd8df` composite. The lower
      crop reaches its final hash after tick 905 and the upper after tick
      921; no packet changes either crop through tick 949. Orchestrator
      viewed transition frames and verified the 13 rows and 556/556
      replay gates. Dropping the tick-921 instance leaves final hashes
      and all 60 output rows unchanged because later ticks repaint it.
      This is a state-dependent composite effect; it does **not** identify
      the glyph stroke producer or the paraLLEl defect. Next GB5C:
      compare exact CPU/paraLLEl pixels and GS state around this packet.
      **GB5C PASS (05b6481):** matched CPU/paraLLEl replay at eight
      ticks 899–950 passed 556/556 with 1,982,063 packets and zero
      null/unsupported operations. The orchestrator reran all 16 crop
      rows, checked replay counters and viewed four side-by-sides.
      Lower button-label damage is visible already at tick 899; it
      predates GB5B's recurring composite instances at 902–921.
      Upper menu glyphs are absent at 899/902 and damaged once present
      at 921, so their producer remains open. Earliest mismatch is at
      or before 899; neither glyph producer nor GS state mechanism is
      identified. **GB5D PASS (c6d55a5):** a ten-marker matched replay
      passed 556/556 with 1,982,063 packets and zero null/unsupported
      operations. The orchestrator reran the crop CSV and viewed pairs
      at 300, 600, 700, 800, 850 and 899. The title's copyright text
      is visibly damaged by tick 300. Button labels are absent at 600,
      then visibly broken on paraLLEl at their first sampled appearance
      at 700; the supported appearance bracket is (600,700]. Crop
      differences at 300–600 concern copyright text/background, not
      button labels. No producer is identified. Next: compare the first
      title-text draw/texture/state against the CPU replay, then review
      the paraLLEl fold for Odin/Turnip. **GB6 partial gate (438edae):**
      six opt-in backend commits cherry-picked cleanly onto current
      E54D fork. Taps-OFF suite and both matched replays passed
      578/578; GPU replay initialized and processed 1,982,063 packets
      with zero null/unsupported operations; CPU hashes matched GB4.
      One leased live boot reached tick 2236 with title, menu and one
      race frame viewed. The second race frame was absent because
      `PS2X_FRAME_DUMP_ONCE_TICKS` accepts three entries, but the boot
      supplied four; PKLOG then consumed 61.6 MB and hit the 64 MiB
      combined cap. No second boot or fork push. Optional taps-ON suite
      was not run (the two normal suites used the same taps-OFF build).
      **GB6B failed capture gate (593821a):** a three-tick/no-PKLOG
      driver saved one race frame but raised `AttributeError` while
      applying its frame-byte cap to a string path. It killed its own
      runner and released the mini lease; no second frame or tick 2200.
      Orchestrator-reviewed failure report and frame. **GB6C PASS
      (orchestrator):** a copy changed only that cap expression to
      `Path(p).stat()`, passed script preflight and two input-SHA reads,
      then one leased boot reached tick 2218 in 70.65 s. Two viewed
      race frames at ticks 1810/2050 show HUD `00:00:01→00:00:05` and
      progress `0→1%`; distinct frame SHAs, rider/terrain still visible.
      The wrapper intentionally sent SIGTERM at target (`rc=-15`), with
      no observed crash. Logs 6.0 MB, no PKLOG; lease released. Runner-
      dir diff empty. The orchestrator fast-forward pushed fork `ssx3`
      `1aaed05→293fd81`, verified remote tip. GPU is opt-in; text damage
      and dark composite persist. Next: title-text producer/state probe,
      then Android Turnip integration and Odin validation.
- [x] **GB7A title-text source map PASS with corrections (`6896f1f`):**
      nine pinned source rows map the shared `GS::processGIFPacket` seam,
      CPU sprite/texture state and Present. Tick-950 display sprite remains
      a candidate, not a glyph producer. Gate corrected the capture file
      path (`gs_stream_capture.cpp`) and treats same-stream packet equality
      as a null control. No build, replay, device action or GS cause.
      `local/research/GB7A/ORCH-GATE.md`.
- [x] **GB7B CPU spatial candidate probe PASS (`46acb96`, fork
      `09d583a`):** one default-OFF probe, one build/suite 556/556 and
      one CPU replay 556/556 through tick700. The bounded full log has
      17,898 rows (7.41 MB); zero small `fbp=112` display writes touch
      the title crops, while T4 glyph-sized batches compose at `fbp=0`
      and full-height blits carry the result to display. Viewed CPU
      frames show legible copyright text and button labels. No unique
      glyph producer or paraLLEl cause proved. Gate:
      `local/research/GB7B/ORCH-GATE.md`.
- [x] **GB7C1 text pixel-trace design PASS with bounds (`0378a7b9`):**
      source map connects tick600 packet47176 off-screen T4 sprites to
      CPU SampleTexture/WritePixel and later display-column blits. Exact
      post-candidate carrier packet remains a private-log lookup; the
      example packet47117 precedes the candidate. Gate requires an
      independent old-pixel read only after TEST accepts the write and a
      bounded ROI diff before claiming glyph shape. No replay, glyph
      producer or paraLLEl cause yet. `local/research/GB7C1/ORCH-GATE.md`.
- [x] **GB7C2 CPU text-composition trace PASS, displayed transfer OTHER
      (`869f2659`, fork `7bd8349`):** tick600 packet47176 has 166 changed
      traced pixels and 9 localized ROI diffs with T4 nibble/CLUT/RGBA
      chains; tick601 packet47240 has 17 stable ROI links but sampled only
      background rows, 24 old==new attempts and zero target-crop changes.
      Viewed title text is already visible at tick600/601. The first
      following carrier is pinned, but displayed glyph producer and
      paraLLEl cause remain open. `local/research/GB7C2/ORCH-GATE.md`.
- [x] **GB7C3 glyph-row carrier design PARTIAL (`57a7de9b`):** four C1
      changed glyph pixels are trace-proven and proposed destination
      coordinates fall in carrier rectangles. The y+1 source shift is
      observed only at background y375 and extrapolated to glyph rows;
      destination prior words, CLAMP/mask/blend and actual swizzled
      addresses remain unknown. Checker verifies provenance, not transfer;
      the proposed poke is not ready. `local/research/GB7C3/ORCH-GATE.md`.
- [x] **GB7C4 actual glyph-row carrier sample PASS, category B
      (`52dfba68`, correction `e978ebe0`, fork `a01e679`):** four
      packet47176 changed C1 glyph words match packet47240 carrier tap0
      at the actual GS storage address. Glyph-row UV confirms +1/+1 and
      fx=fy=0 for the four targets. Destination RGB is already equal
      before the carrier write; 4/4 old==new. One build, 556/556 suite,
      ON/OFF CPU replays and tick600/601/700 frames byte-identical.
      Measured target A has a bounded one-pixel prediction, but no
      causal poke or GPU cause claim. `local/research/GB7C4/ORCH-GATE.md`.
- [x] **GB7C5 watched displayed-pixel provenance PASS/P (`a643ae60`,
      fork `8966b0b`):** FBP112 (342,377) storage word starts zero;
      packet5139 T8H upload changes alpha only, then three sprite draws
      change RGB. Tick259 packet5470 batch10 first writes final RGB
      `353341`; pre/post packet47240 remain equal. One build, 556/556
      suite and ON/OFF CPU replays, tick600/601 frames byte-identical.
      This names a pixel writer, not the sampled image or GPU cause.
      `local/research/GB7C5/ORCH-GATE.md`.
- [x] **GB7C6 packet5470 source design PASS/B (`48d2253e`):** static
      packet parse proves tick259/batch10 is a textured sprite writer of
      FBP112 (342,377). Its MODULATE-white path implies sampled RGB
      `353341` from the observed destination, and computes tap0 address
      `0x000bae74`. Actual texture word/earlier writer, glyph shape and
      GPU cause remain unobserved. No replay/device run.
      `local/research/GB7C6/ORCH-GATE.md`.
- [x] **GB7C7 permission stop OTHER (`18841b9b`):** first private-fork
      edit denied by OpenCode `../*` scope, so no trace/build/replay or
      sampled-word observation. Pins and a bounded three-file tap design
      were handed back; checker returns OTHER at `trace_present`.
      `local/research/GB7C7/ORCH-GATE.md`.
- [x] **GB7C7P2 CPU texture tap PASS/A (`f3ebb601`, private fork
      `f54adff`):** tick259 packet5470/batch10 directly reads CT32
      word `63353341` at texture address `0x000bae74` (fx=fy=0), then
      changes raw FBP112 destination `dc302f3b→dc353341` at
      `0x0019ae38`. One pixel only; earlier texture-word producer,
      whole glyph and GPU cause open. Five builds, three ON/one OFF
      replays; common frame hashes and three PPM pairs equal across
      adjacent builds, so same-binary control unverified. Viewed title
      frames; marker259 precedes packet5470 in stream order.
      `local/research/GB7C7P2/ORCH-GATE.md`.
- [x] **GB7C8 GPU comparison design B (`016f4086` + `9103185f`):**
      inspected source exposes no nonperturbing per-packet GPU readback;
      render-pass cuts can occur mid-stream. Marker260 is first after
      packet5470, with 121 intervening packets and no other record kinds
      in that span; marker300/301 have 5,001/5,123 intervening packets.
      Dirty G43 source files are hashed, but observed binary provenance
      is unproved. No run or GPU cause claim. `local/research/GB7C8/ORCH-GATE.md`.
- [ ] **GB7C9 bounded same-stream GPU comparison:** rebuild pinned G43
      source, then compare CPU/paraLLEl packet input, watched texture and
      destination words, crop and frame at marker260. Use the same binary
      for ON/OFF controls. A mismatch still cannot identify packet5470
      alone. Stock-race Odin selected-VRAM work has priority.
- [ ] GS bridge step (a), E lane: CPU backend behind the queue on its own
      thread (Mac), byte-exact A/B vs direct calls. Gated on PF1's numbers
      and E32. Then (b) paraLLEl via MoltenVK (G), (c) Android (G+N),
      (d) GPU-resident presentation.
- [ ] paraLLEl-GS patch stack home: forks created 09-22
      (`brad-richardson/parallel-gs`, `brad-richardson/Granite`). Backup
      `wip/ssx3-snapshot` pushed 09-22 (parallel-gs `faf6400`, Granite
      `aaeee97`; uncurated, fixes + diagnostics). After G42: fix-only commits (G26, G28, plus Turnip
      loading if adopted) on branch `ssx3` in both forks; diagnostics stay
      env-gated or on wip.
- [ ] Adreno filing: paused (Brad, 09-22). Any rewrite drops the
      withdrawn sampling inference.

## N — Android app (Odin)

- [x] **N2 PASS (09-22):** first Android build. The stub link can't
      work at the old pin (E17's in-tree table is the full table); the
      full-title link with the codegen-dir port is green: APK 270,957,997 B
      `21a9230c…`, 9,441/9,441 `sub_*` defined, 0 undefined. Entry chain:
      NDK glue → raylib `android_main` → `main`. Gate exception accepted.
- [x] **N3 PASS (09-22): first PS2-recomp boot on the Odin reaches the
      animating stock title screen** (dev bypass, CPU GS, FFmpeg off).
      arm64 APK `69a79e29…` 134 MB; `ps2x.env` shim (+216 lines,
      Android-only) sets the CD image and dev flags; ELF + ISO staged and
      verified; title at t+20 s, 0 crashes over 5 min; ~21 guest frames/s
      with frame dumping on. Local branch `n2-android` @ `619d48a`.
- [ ] Manifest: `android:showWhenLocked="true"` + `android:turnScreenOn="true"`
      on the NativeActivity so runs work while the Odin stays locked (Brad
      keeps his PIN lock; 09-22). First unlock after a reboot is still
      required (credential-encrypted storage). Goes into the next N build.
- [x] **N4 PASS (09-22):** `n2-android` rebased onto `e57b5f8` (+3 local
      commits + manifest/PNG commit `f9d78da`); APK `d93b81a7…` is
      profileable (simpleperf works with `--app`, not `-p`), lock-screen-safe,
      and writes PNG dumps (raylib `fopen` failed on the app dir; now
      `ExportImageToMemory` + `ofstream`). First Odin visit to Select
      Character. Profiles: title GS-rasterizer-bound, Select Character
      VU1-bound (see ledger).
- [x] **N6 PASS (09-23, fdf7958): the Odin controller drives the PS2 pad.**
  - The raylib Android gamepad path already worked, with a correct mapping
    (every button, dpad, hat and stick was verified through `PS2X_PAD_LOG`).
  - One fix, on `n2-android` `65c95d9` (local): Android now reads keyboard
    and gamepad together. Before, the gamepad latch killed keyboard/adb
    input after the first controller event.
  - Injected keys route title → menu → Select Character with no script, and
    there's no phantom input.
  - Standard injector: `sendevent` on event8 (gamepad) / event5 (keyboard);
    `input keyevent BUTTON_*` never reaches the game.
  - Open: physical X/Y button positions (N6 §5, 2-minute hands-on test for
    Brad). Analog L2/R2 axes are unmapped by design (digital keys drive
    them).
- [ ] **N5 finding (a9fb781): since E40, `eac6cba` compiles the E41/E43/E44/
      mpg_src watch taps into every guest store macro, with no compile-time
      guard.** Guest `.text` is 3.2× (358 MB vs 113 MB), and every store
      gets runtime-checked tap calls. So **no build since E40 can give a
      clean speed number** (Mac, iOS or Android). Fix:
      `PS2X_ENABLE_DIAG_TAPS` (off for release/speed builds). N5 is
      prototyping it as N5-local, then fold it into `ssx3`. It's also the
      review's "one shared tap library" item.
- [x] **N5 PASS (92504f5): the Odin plays title → SC (rider) → Happiness
      race on `eac6cba` + E45**, the first clean speed numbers (ledger):
      title 0.47×, menu 0.44×, SC 0.33× (N4's diagnostic build: ~0.2
      vsyncs/s), race 0.19–0.26×. Race profile: VU1 50% (hazard bookkeeping
      29.6%), GS CPU raster 36%, guest 0.4%. Tap guard `6c335e6`
      (`PS2X_ENABLE_DIAG_TAPS`, default OFF on Android): guest `.text` is
      back to 113 MB and the full-rebuild peak is 4 GB (was ~10). Host-side
      env-off taps remain (not covered). Branch `n5-android` on bytesize
      (local).
- [x] **E58 PASS (f8a1ecf): fold pushed, fork `ssx3` `eac6cba..b9647f5`.**
      E52 tests + E53 batch 1 + E45 + tap guard (default OFF; tap tests
      registered only with taps ON) + I26 black fallback + G46 fill rule +
      the vsync-rate log. Suite 537/537 (taps OFF) and 632/632 (taps ON).
      The codegen is byte-identical to E53's and promoted (`codegen-ssx3`,
      old kept as `-pre-e58`). Smoke: SC with the rider, race with
      terrain, viewed. Clean Mac speed in the ledger (race 0.13×).
- [x] **N7 (9ac3f29): the Odin runs the fold** (APK `426d2a91`, fork
      `b9647f5` + N-local). The race world draws as on the Mac (snow slopes,
      trunks, rider, HUD; no sky). Speed (one run, provisional): menus
      0.39–0.46×, SC 0.27×, **race 0.076×** (ledger). At 21–38 s the rider
      reads 0–1 MPH at 2% progress: stuck or crashed? Check it in the
      next race run. No second run and no simpleperf (the brief's ≥45 s
      race window is unreachable at 0.076× within 600 s; accepted as is to
      save quota).
- [x] **N8A PASS (e80295b; source only):** the current fork's opt-in
      paraLLEl backend and N7's APK path were mapped through the pinned
      Turnip v36 ELF (`717812c3…1ac29d`). The in-process backend has no
      HMI loader, and the N7 Android env/Gradle pieces are absent from the
      current fork. G43 proved the driver only from an adb-shell replayer;
      its `libhardware.so`/`libnativewindow.so`/`libsync.so` dependencies
      in the APK namespace remain untested. N8B: one bounded arm64 build
      and functional Odin launch, with packaged-driver SHA, mapped HMI,
      Turnip driver identity, live GS counters and a viewed frame as gates.
      No speed or app-runtime claim from N8A. **N8B1 PASS (dea8416;
      source/APK only):** ported N7 Android env/build pieces and the G43
      HMI hook on local fork branch `n8-turnip-apk` (`17e90de`, from
      `4f93216`). Host suite 585/585. First APK packaged correctly but
      left IOP trace and debug UI enabled; one repair turned all five
      diagnostic flags off. Final arm64 APK SHA `1096a28e…b190da`
      contains runner SHA `cdbaa6dd…eb033`, Build ID `28340bbe…0add`,
      and pinned Turnip SHA `717812c3…1ac29d`; no x86_64 member.
      Linked loader markers and runner-dir guard checked. No fork push
      or app-runtime claim. **N8B2 FAIL at first runtime loader gate
      (ace6463):** one install and one launch; installed APK, stock ELF
      and ISO each matched pinned SHA twice. Same-PID log selected the
      parallel backend and requested Turnip, then `dlopen` failed because
      `libhardware.so` was unavailable in Android app namespace
      `clns-7`. It failed closed before HMI, Granite, GIF/presents or a
      race frame. The app was force-stopped, PID absent, lease free.
      A prelaunch launcher check first rejected its own lease; it was
      corrected before any `am start`, with no second install/launch.
      **N8C1 PASS (4ed31ac; static):** the pinned Turnip ELF has one
      strong `libhardware.so` import, unversioned `hw_get_module`, and
      four stripped gralloc call sites. One path logs that video buffers
      are unsupported on gralloc failure and returns an object; three
      return null. The normal game's choice is unknown. Bundling the
      Odin system `libhardware.so` would require seven private ELFs in
      its static dependency closure, with more dynamic HAL dependencies
      possible. One app-local compatibility ELF exporting
      `hw_get_module` and returning `-ENOENT`/null is the narrow
      **N8C2 loader probe**, not a proven gameplay fix. Build one APK,
      then one Odin launch; verify HMI/driver identity, live GIF/presents
      and a race frame or stop at the first new failure. Device remains
      unproved; no speed or frame claim from N8C1. **N8C2 loader/backend
      PASS, visible frame FAIL (0b2cabf):** app-local `libhardware.so`
      returned `-ENOENT` on four gralloc calls; the bundled HMI mapped,
      HAL opened, `[gs:parallel] init ok`, and nonzero GIF/presents carried
      the route to tick 2087. One installed APK `86ee7b72…fc7640` and
      pinned ELF/ISO matched double device SHA reads. The menu at tick 809
      and race at 1844/2087 were viewed and are mostly black with striped
      rectangular fragments. No usable race image, speed number, or
      logged Vulkan device/driver identity. App force-stopped; PID absent,
      Odin lease free. N8C2 source/APK remain local and diagnostic; do not
      fold the shim yet. **N8D1 queued:** one bounded menu launch with the
      N4-proven PNG writer to compare the host upload image with the
      screencap, then choose the next stage to probe. **N8D1 partial
      (3b1ef24):** the PNG writer succeeded in one build/one Odin launch;
      package `ece8b84c…fc63ae2` passed the three-member/five-flags-OFF
      gate, and installed APK/ELF/ISO matched two reads. Viewed host
      uploads: tick 781 shows a recognizable mountain, while ticks
      810/840 have broad black bands. The later tick-861 screencap is
      a readable menu with fine horizontal lines. The changing scene
      and 21–80-tick gap prevent a same-frame GL/backend split. All four
      PNG/SHA checks passed; app force-stopped, PID absent, lease free.
      No speed, Turnip driver identity, or stable race-image claim.
      **N8D2 partial (3832b71):** reused the N8D1 APK for one Odin run,
      no build. Three 512×448 host uploads at race ticks 1840/1950/2050
      and a nearby 1920×1080 screencap were decoded and viewed. The
      tick-2050 host upload and screen both have a partial HUD, black
      bands, and sparse pale fragments; the screen adds fine stripes.
      Screen request followed the dump trigger by <0.4 s, but its exact
      guest tick is unknown, so this is not a same-frame comparison.
      SHA/package and one-run checks passed; app force-stopped, PID
      absent, lease free. The major scene loss exists in the host upload
      before `UpdateTexture`, so a final screen-only failure cannot
      explain it. **N8D3 PASS for stage equality (8bcad5f):** one
      diagnostic APK build and Odin run captured raw Vulkan mapped bytes,
      backend packed rows, and frontend PNG at the same race tick 2050,
      FBP 112, 512×448 RGBA8. Raw and packed 917,504-byte files have
      identical SHA; 448/448 rows match. The decoded frontend PNG matches
      all 917,504 bytes too. All three viewed images contain the same
      black bands and fragments. The app was force-stopped, PID absent,
      Odin lease free; no speed claim. The loss is **at or before the
      Vulkan mapped scanout/readback**, with GPU image generation versus
      transfer/readback still unresolved. **N8D4 preparation PASS
      (769bff3):** existing N8D3 APK contains the default-OFF GS stream
      capture and tick-2050 close marker; the worker prepared a one-run
      launcher, CPU/paraLLEl replay script and acceptance checker. I reran
      the prepared checker and verified the capture/replay source path.
      Device run, stream, Mac build/replays and visual comparison are
      explicitly **unrun**. Continue after I27B Simulator cleanup; keep
      the large GS capture outside git. Do not fold or profile for speed
      until the race image is usable.
- [x] **N8D4 PASS for same-stream cross-host split (545d214):** one Odin
      install/launch captured 1,100,725,180 bytes through the tick-2050
      marker: 862,993 packets, 11,499 priv records, 25,485 transfers and
      2,050 VBlank markers, complete EOF and matching SHA pairs. One Mac
      build at fork `ddaee78` ran CPU and paraLLEl replay of that exact
      stream, each 585/585 tests, same FBP 112/PMODE `ff21` and 41 frame
      samples. I viewed the Odin raw/frontend and both Mac tick-2050
      images. Both Mac images show readable HUD, snow slope, rider position,
      radio card and right meter; Odin shows mostly black rectangles and
      fragments. Mac CPU/paraLLEl hashes differ and both retain a dark
      lower region. Along with N8D3's Odin raw/backend/frontend equality,
      this places an additional **device-specific loss at/before mapped
      scanout**; it does not separate Turnip image generation from its
      transfer/readback. App force-stopped, PID absent, lease free; no speed
      claim. **Next:** map the exact paraLLEl generation→copy→map source,
      then design one bounded N8D5 device probe that distinguishes those
      two stages. Keep the stream outside git and defer fold/speed profiling.
- [x] **N8D5A static design PASS (27e8c3e):** source path and format gate
      verified; no build, boot, device contact or code edit. A same-shot
      sampled Vulkan image on Odin would bypass the current image-to-buffer
      readback and distinguish a sparse GPU image from a copy/map loss when
      paired with the existing mapped output. Yet G43's Android CMake
      selects `GRANITE_PLATFORM=null`, whose application entry exits, so its
      desktop swapchain display path cannot show an Odin surface. G43's
      dump parser also does not accept the N8D4 `PS2XGSC1` capture; a
      parser adapter is required. The report tables three probes and
      A/B/C outcomes; a GPU tile readout remains conditional on an
      independent buffer-map control. **Next:** prove a bounded Android
      surface control or a validated GPU tile path before spending another
      full stream transfer/device run. The image-generation versus
      transfer split remains open.
- [x] **N8D5B GPU tile candidate OTHER (fce1034):** default-OFF
      `PS2X_N8D5_TILE_CAPTURE=1` at tick 2050 uses a checkerboard control
      and GPU sampled 16×16 tile counts from the same `shot.image`, alongside
      the old mapped capture. Shader validation, Mac build and taps-OFF suite
      passed 585/585. The worker replay could not create a Vulkan instance
      inside its sandbox. One orchestrator replay outside it reached the
      pinned stream/frame and reproduced 567/896 active raw Mac tiles,
      128,292 occupied pixels; I viewed the frame. The control returned
      2149844998 instead of 128 because the standalone build disables
      SPIRV-Cross reflection, the candidate supplied no `ResourceLayout`,
      MoltenVK rejected the compute pipeline and Granite dropped dispatch.
      Sampled tile words are invalid; no image-generation/readback verdict,
      Odin run, or speed claim. The candidate is local fork `ef34402`, not
      pushed. **Next:** supply a pinned explicit shader resource layout,
      verify Mac control=128 and sampled/raw occupancy both broad on the
      same stream, then gate one Odin run. Keep the full replay log in scratch.
- [x] **N8D5C Mac GPU tile probe PASS (25ef5fb):** one five-line explicit
      `ResourceLayout` repair at local fork `a847d0f` supplied the two
      sampled float image bindings, SSBO binding 2 and eight-byte push
      constant. Release paraLLEl build and taps-OFF suite passed 585/585.
      One orchestrator replay outside the worker sandbox used the exact
      N8D4 stream at tick 2050/FBP112/PMODE `ff21`/512×448. The GPU
      checkerboard returned **128/128**; sampled and raw tile vectors
      matched **896/896**, with 128,292 occupied pixels and 567/896 active
      tiles each. I viewed the frame; its PPM SHA matches N8D5B's Mac
      frame. The full replay log is compressed in scratch and a bounded
      excerpt is committed. This proves the separate sampled/storage-map
      path on Mac, not where Odin loses pixels. No device run, speed claim
      or fork push. **Next N8D5D:** build the pinned default-OFF Android
      diagnostic; one lease-held Odin run to tick 2050 with control,
      sampled and raw tile counts. Control failure/misalignment stops at
      OTHER. If control passes, sparse/sparse supports a sparse sampled
      image at this point; broad/sparse implicates the current copy/map
      path. No fold or profiling until the device result is gated.
- [x] **N8D5L Mac log-summary PASS (orchestrator):** Android's stdout
      redirect reads at most 1,023 characters per logcat record, shorter
      than the ~2.9 KB N8D5C tile-vector lines. Local fork `ab8155b`
      adds one short `sampled_summary` and one `raw_summary` line under the
      existing flag, without changing shader, layout or copy/map behavior.
      Mac Release build and same-stream replay passed 585/585, control
      128/128, both summaries 896 tiles/128,292 occupied pixels/567 active
      tiles, and unchanged sampled/raw 896/896 vector equality and viewed
      frame SHA. `local/research/N8D5L/REPORT.md` pins the source and
      compressed log. **N8D5D** may now build the isolated Android APK
      from this pin; no Odin action until its package gate.
- [x] **N8D5D Android package PASS (16fb9ba):** one private bytesize
      `assembleRelease` completed in 5m 56s with the N8D5L backend and
      N8D5B shader header as the only source differences from N8B1.
      WSL/Mac APK SHA pairs match (`a6a0c379…50612a`); package contains
      exactly arm64 runner, pinned Turnip and HAL shim. The runner has
      control and both short summary strings, build ID `ab1bdc3b…48b56`;
      diagnostics flags are OFF. No device action, fork push or speed claim.
      `local/research/N8D5D/REPORT.md` has the full package table.
      **Next N8D5E:** one lease-held Odin install/run to tick 2050, with
      frame and same-PID control/sampled/raw summaries. View the frame and
      gate A/B/OTHER before folding or profiling.
- [x] **N8D5E Odin tile-path formal OTHER (8feec46):** one install/run
      stopped at tick 2110 under its cap, then force-stopped the app and
      freed the lease. Same-PID tick 2050/FBP112/PMODE `ff21`/512×448
      control passed 128/128. GPU sampled and raw mapped 896-tile vectors
      were exactly equal, with 15,669 occupied pixels and **79 active
      tiles** each; the orchestrator reassembled both Android logcat
      fragments and checked every word. Frontend metadata matched tick
      2050, but raylib failed to export both PNGs; no same-run frame exists
      to view. The predeclared A/B gates require that frame, so the formal
      result is OTHER despite the strong sparse-image signal. N8D4's
      earlier viewed Odin frame remains visual context only. A read-only
      source comparison found N8D5D used N8B1's old `ExportImage` path,
      while successful N8D3/N8D4 APKs had a single-hunk
      `ExportImageToMemory` + `std::ofstream` writer. Ownership of the
      three frame dirs matched; the source difference is a leading cause,
      not yet proved on-device. **Next N8D5F:** one isolated Android
      rebuild with that exact writer hunk and the tile probe unchanged;
      package gate before another one-run Odin check. No speed claim.
- [x] **N8D5F PNG writer Android package PASS (24836f2):** one private
      bytesize `assembleRelease` succeeded in 7m 47s. Against N8B1,
      only the pinned tile backend and N8D3's single PNG writer hunk
      differ; the shader header is the sole G43 addition. The package
      has exactly the arm64 runner, pinned Turnip and HAL shim; WSL/Mac
      APK SHA pairs match (`8c101c48…be66a0`). The runner contains the
      tile/control/summary and PNG writer diagnostic strings; five
      diagnostics/UI flags are OFF. `local/research/N8D5F/REPORT.md`
      pins the source, Build ID, cache and package table. No Odin action
      or speed claim. **Next N8D5G:** one bounded Odin run for the same
      tile probe and a viewed tick-2050 PNG; gate A/B/OTHER before a
      source-side/Turnip diagnostic.
- [x] **N8D5G Odin tile probe category A PASS (73a22a0):** one install/run
      at tick 2050, FBP 112, PMODE `ff21`, 512×448. Checkerboard control
      128/128; GPU sampled and raw mapped vectors each have 896 tiles,
      6,045 occupied pixels and 34 active tiles, and match at 896/896
      positions. The same-run PNG was saved, SHA-checked and viewed:
      mostly black with sparse HUD/snow fragments. PNG writer works on
      device; app force-stopped, PID absent, Odin lease free. The sparse
      sampled image localizes the loss by or before `Present` scanout on
      Odin/Turnip, upstream of buffer copy/map/frontend upload. N8D4's
      broad Mac replay used one identical GS stream across hosts; this
      N8D5G run used the same route but is not byte-identical. No clean
      speed claim. **Next:** map `GSRenderer::vsync` circuit sampling,
      field merge and VRAM input; choose a controlled stage probe, validate
      on Mac, then run one bounded Odin comparison.
- [x] **N8D6A Mac scanout-stage probe PASS (a291a7c):** default-OFF
      diagnostic handles retain circuit1 and merged before deinterlace;
      one Release build and taps-OFF suite 585/585. One pinned N8D4 stream
      replay at tick2050/FBP112/PMODE `ff21` measured circuit1 and merged
      at 512×224, 448 tiles, 64,374 occupied pixels, 300 active, control
      128 each. Final is 512×448, 896 tiles, 128,292 occupied, 567 active,
      control 128; sampled/raw final vectors match 896/896. Present hash
      matches the prior Mac frame viewed by the orchestrator. The new PPM
      directory was absent; no extra replay. This validates stage sampling
      on Mac only, with no Odin stage result or speed claim. Receipt:
      `local/research/N8D6A/orch-replay-excerpt.txt`.
- [x] **N8D6B Android package PASS (5322d36):** one private bytesize
      arm64 `assembleRelease` succeeded in 5m31, 48 tasks. Fresh N8D5F
      snapshot differs only at N8D6A's pinned fork backend and three
      zero-fuzz G43 stage-patch files; PNG writer, shader header, codegen,
      Turnip and HAL sources stayed pinned. WSL/Mac APK SHA pairs match
      `6839a0a4…74a611`, 153,720,348 bytes. Runner `4e6c056d…a0efd`,
      Build ID `8d19e78…1a99f0`; bundled Turnip/shim and stage strings
      verified, five diagnostics/UI flags OFF. No Odin run or speed/cause
      verdict. Full receipt: `local/research/N8D6B/REPORT.md`.
- [x] **N8D6C formal OTHER with recovered A measurements (eeabeb0):**
      one Odin install/run reached tick2050/FBP112/PMODE `ff21` and logged
      circuit1/merged each 21/448 active (control128), final 39/896
      (control128). Released launcher rejected comma-led logcat vector
      continuations, so the complete-receipt gate missed and it stopped
      at tick2136 under the tick2100 rule; app force-stopped, PID gone,
      lease free. The orchestrator recovered both 896-word vectors from
      the same-PID log, exact equality and 5,894 occupied pixels, then
      pulled the existing tick2050 PNG/txt with double device/local SHA
      reads and viewed the mostly black frame. These same-run measurements
      meet predeclared A conditions, while the formal run remains OTHER.
      Sparsity is present by circuit1; its upstream mechanism is open.
      `local/research/N8D6C/ORCH-GATE.md` has the recovery and caveats.
- [x] **N8D7B pre-circuit1 static design PASS (`f32c628`):** mapped GS
      VRAM ownership, `sample_crtc_circuit` input binding, shader address
      decode and the stage tap. The same-frame V/S/T table predicts
      distinct decoded-input/circuit1 outcomes; N8D4 and N8D6C are not
      byte-identical streams, so cross-run counts alone cannot assign cause.
      N8D7A Go Muse Contributor was rejected before task start by the
      workspace's paid-training-endpoints Privacy gate; Brad enabled that
      setting later, Muse Go retry pending. N8D7B Sol medium found that a
      promoted image can bypass VRAM and the same-frame promotion state is
      absent; raw VRAM bytes need an independent field decoder. Design only,
      no device verdict. Gate: `local/research/N8D7B/ORCH-GATE.md`.
- [x] **N8D7C CPU decoder adapter design PASS (`51b23ed`):** existing
      `vram_readback<PSM>` can decode one single-sample field using one-row
      calls for phase stride two. The helper and shader share `swizzle_PS2`,
      so agreement alone does not prove its addressing. The eight-row map
      covers source selection, phase, PSM, wrap, sample count and tile census;
      fixture and Mac calibration have not run. Gate:
      `local/research/N8D7C/ORCH-GATE.md`.
- [x] **N8D7D synthetic adapter fixture FAIL_COMPILE_CAP (`b4f30c4`):**
      twelve cases and literal boundary checks were written, but the first
      compile used G43-relative includes from the wrong cwd. The one allowed
      retry reached `volk.h` and failed because the include path omitted
      `Granite/third_party/volk`. All case results remain unrun/null. No
      game build or device action. Gate: `local/research/N8D7D/ORCH-GATE.md`.
- [x] **N8D7D2 fixture resume PASS (orchestrator):** with the exact volk
      and bundled Vulkan include paths, the saved fixture compiled and ran
      once. All 12 synthetic 512×224 cases had zero pixel/tile mismatches,
      458,752 output bytes, 448 tile counts, no aliases, and matching output
      hashes. Literal FBP112 and wrap offsets matched. The writer and reader
      share `swizzle_PS2`, so this is adapter calibration, not a full address
      or GS-cause proof. `local/research/N8D7D2/ORCH-GATE.md` has commands.
- [x] **N8D7E read-only Mac capture design PASS with corrections (`40e457d`):**
      Muse Go mapped nine source steps and found callable GPU VRAM and
      circuit1 image staging-copy APIs. Gate corrected its compact-page
      suggestion (host decoder needs a contiguous 4 MiB slice), located
      circuit1 retention in the N8D6A G43 stage patch, and recalculated
      capture bytes as 5,177,344 (<6 MiB). No replay or device run.
      `local/research/N8D7E/ORCH-GATE.md`.
- [x] **N8D7F Mac selected-input probe build PASS (`3d9678d`, fork
      `0678dd9`):** one default-OFF candidate copies the selected full 4 MiB
      GPU VRAM slice and an independent circuit1 image, then host-decodes
      and compares 448-tile vectors with the existing GPU stage tap. Private
      Release build and taps-OFF suite passed 585/585; runner guard empty.
      No replay or device-cause verdict. Gate:
      `local/research/N8D7F/ORCH-GATE.md`.
- [x] **N8D7G Mac same-stream calibration PASS (`5baf7f9`):** pinned N8D4
      OFF/ON replays each exited 0 under one released mini lease. Selected
      source was nonpromoted, one sample; host input, independent circuit1
      and GPU stage were exact 448/448, each 300 active. Final sampled/raw
      were exact 896/896, 567 active; controls 128; present hash `7bf5c012`
      and viewed frame SHA matched across runs. Orchestrator corrected a
      checker field-name bug and extended the saved-log gate to 34/34;
      neither replay was rerun. Mac calibration only, no Odin/cause/speed
      claim. `local/research/N8D7G/ORCH-GATE.md`.
- [x] **N8D7H Android selected-input diagnostic package PASS (`9bdcfe4`):**
      isolated source differs from N8D6B in exactly one fork backend and
      three G43 files; one arm64 release build succeeded (5m17s, 48 tasks).
      APK 153,736,732 bytes, WSL/Mac SHA `86fca856…31df14a` twice;
      runner `8e32841d…32c683`, unchanged Turnip/HAL, five flags OFF.
      Corrected Mac size assertion re-passed before commit. No device
      action, speed or cause claim. `local/research/N8D7H/ORCH-GATE.md`.
- [x] **N8D7I one Odin selected-input capture PASS, category A (`713e6c44`):**
      one installed APK and launch yielded the aligned tick2050 frame;
      selected input/circuit/GPU stage each 35/448 active tiles and exact
      448/448 vectors; final sampled/raw 63/896 active and exact 896/896,
      control128 PASS. Viewed PNG is mostly black with small snow/HUD
      fragments. Sparse pixels already exist at selected input in this
      run; raw VRAM content versus input decode/driver remains open.
      App force-stopped, PID absent, Odin lease free. Diagnostic wall time
      is not speed. `local/research/N8D7I/ORCH-GATE.md`.
- [x] **N8D7J selected-input source audit PASS with correction (`a1632be9`):**
      mapped the 4 MiB `buffers.gpu` copy before circuit1 and the host
      decode; `input` is decoded pixels, and Android raw SHA is unavailable.
      CPU input and GPU circuit share the swizzle/base, so equality is not
      an independent address check. Proposed contiguous raw-word FBP tally
      cannot discriminate: selected pixels use phase/stride/page layout,
      and unrelated bytes can occupy the window. No run or cause claim.
      `local/research/N8D7J/ORCH-GATE.md`.
- [x] **N8D7K independent address oracle PASS with correction (`8324a3ce`):**
      fork literal PSMCT32 tables are separate from G43 bit arithmetic;
      fork CT24 uses the CT32 page table. Eight FBP112/FBW8 offsets match
      G43 8/8; base `0xE0000`, page boundaries `0xE2000`/`0xF0000`, far
      corner `0x1BFFF4`. Header bytes match the N8D7F fork. Six sampled
      words cannot classify a full frame; the worker's A/B threshold is
      rejected. No build/run. `local/research/N8D7K/ORCH-GATE.md`.
- [x] **N8D7L independent full-frame raw oracle PASS (`b5200bf2`, fork
      `d1ba1d4`):** one Mac build, flag-OFF suite 585/585 and paired OFF/ON
      replay of the pinned N8D4 stream. Fork-table PSMCT24 oracle matches
      G43 selected input, circuit and GPU stage across all 448 tiles;
      64,374 occupied pixels, 300 active tiles. OFF/ON hashes and viewed
      frame are byte-identical. Static fixture 13/13 checks source/literals;
      compiled evidence is the replay. Mac calibration only; Odin raw
      snapshot and cause remain open. `local/research/N8D7L/ORCH-GATE.md`.
- [x] **N8D7M1 independent-oracle Android package PASS (`1da356b9`):**
      one isolated arm64 build from N8D7H with exactly the N8D7L backend
      overlaid, unchanged G43/Turnip/HAL and five diagnostic/UI flags OFF.
      APK SHA `e077bef8…758a1`, new runner Build ID, oracle strings and
      source fence verified. No Odin action or cause claim.
      `local/research/N8D7M1/ORCH-GATE.md`.
- [x] **N8D7M2 same-run Odin oracle PASS, category A (`9804ebb8`):**
      one pinned install/launch at tick2050. Fork-table oracle and G43
      input/circuit/stage are identical 448/448, each 2,058 occupied and
      15 active tiles; final sampled/raw 896/896, 29 active. Eight
      control addresses match, while values are 0/8 versus the different
      Mac stream. Viewed PNG is mostly black. App force-stopped, PID
      absent, lease free. The selected raw snapshot is sparse under both
      decoders; its upstream producer/selection remains open. No speed or
      driver cause claim. `local/research/N8D7M2/ORCH-GATE.md`.
- [x] **N8D7M3 raw-VRAM provenance design PARTIAL (`20144020`):**
      source map identifies presentation selection, 4 MiB copy and host
      decode paths. Its draw-count threshold does not measure changed
      pixels; Present-entry pending/last-tick fields do not prove GPU copy
      order; two nonzero controls do not prove census loss. A broad
      alternate-base census alone cannot prove intended display selection.
      No build, replay or Odin action. Do not run the proposed tap as
      written. `local/research/N8D7M3/ORCH-GATE.md`.
- [x] **N8D7M4 same-stream design PARTIAL (`744bcdd2`):** captured
      N8D4 Odin stream and its Mac replays provide a controlled reference;
      current APK appears to contain both capture and selected-snapshot
      flags, though co-enabled operation is untested. Proposed immediate
      before/after packet reads may miss queued execution; eight control
      words do not prove full-frame content, and a broad tick2052 image
      would not prove tick2050 copy timing. No build/run/device action.
      `local/research/N8D7M4/ORCH-GATE.md`.
- [x] **N8D7M5 executed-word Mac validation PASS (`21b3e53f` +
      correction `f630af5b`, fork `a8cfefa`):** direct CPU replay of
      pinned N8D4 stream traces 1,980 executed changes at six FBP112
      words on four pages; each first changes zero→nonzero, with
      packet/tick/kind and submit-count witness. One isolated build,
      585/585 suite, ON/OFF CPU replay hashes and viewed tick2050 frame
      identical. Only 2/6 CPU finals equal the Mac paraLLEl selected
      controls, so CPU values cannot be the Odin GPU oracle. No device
      or speed claim. `local/research/N8D7M5/ORCH-GATE.md`.
- [x] **N8D7M6 same-stream selected VRAM PASS/A (`effbf5ec`):** one
      Odin install/launch captured a closed 1.10 GB stream at race
      tick2050. The Mac paraLLEl replay of those exact bytes has 300/448
      active selected-image tiles, while Odin has 23/448, with all 11
      selection fields equal. Independently parsed full vectors and
      viewed broad Mac versus mostly black Odin frames. Two Mac replay
      invocations (first cwd-dependent suite failure, second 585/585);
      first log overwritten, deviation recorded. Device-specific loss
      is at/before the selected snapshot; missing writes versus copy
      timing remains open. `local/research/N8D7M6/ORCH-GATE.md`.
- [x] **N8D7M7 divergence boundary design PARTIAL (`65dffdd3` +
      corrections `49e2d7af`, `67865212`):** mapped selected VRAM copy,
      later circuit shader sample, submit/wait and host decode. A second
      same-command copy could test copy consistency; an extra post-wait
      flush changes what executes and cannot prove early-copy ordering.
      Byte-identical staging with identical decoder cannot yield a
      different census. No build/replay/device run or four-way gate.
      `local/research/N8D7M7/ORCH-GATE.md`.
- [x] **N8D7M8 execution witness design B (`57b51229` +
      `f92c204a`):** inspected source has no nonperturbing three-way
      witness for writes before/after/absent from the original selected
      copy. Packet identity is lost at the EE queue/backend boundaries;
      flush timelines and wait-idle do not identify completed draws.
      Mac replay cannot establish live Odin thread order. No run or GPU
      cause claim. `local/research/N8D7M8/ORCH-GATE.md`.
- [x] **N8D7M9 live identity design B (`77dc39fe` + `d88bb194`):**
      proposed EE sequence/tick carry through GS recording. Initial
      conditional A was withdrawn: pressure/hazard cuts have no separate
      timeline value, min/max packet ranges lose membership, and a draw
      footprint is not an executed write (transfers/clears/host writes and
      clipped primitives confound absence). No build or Odin run.
      `local/research/N8D7M9/ORCH-GATE.md`.
- [x] **N8D7M10 Odin offline replay feasibility B (`6ed56aed`):** the
      closed N8D7M6 stream and Mac replay path are pinned, but the GS
      replay parser is in desktop `ps2x_tests`; Android sets
      `PS2X_BUILD_TEST=OFF` and ships only the NativeActivity runner.
      There is no current on-device replay entrypoint. No build, copy or
      device action. `local/research/N8D7M10/ORCH-GATE.md`.
- [x] **N8D7M11 on-device replay harness design A (`ee28cc70`):**
      source-grounded choice is a dev-only, default-off NativeActivity
      replay mode with a shared desktop/app parser core. It preserves
      recorded path/marker order, Turnip loader and the selected 4 MiB
      snapshot/448-tile decoder by design. No code, build, staging or
      Odin run; runtime behavior and graphics cause remain open.
      `local/research/N8D7M11/ORCH-GATE.md`.
- [x] **N8D7M12 Part 1 shared replay core A (`a65bc907`, fork
      `24801bc`):** desktop test now calls a runtime core; 585/585 suite
      and one exact-stream Mac replay match the N8D7M6 baseline, including
      300/448 selected tiles and PPM bytes. No Android branch/build or
      Odin run. `local/research/N8D7M12/ORCH-GATE-P1.md`.
- [x] **N8D7M12 Part 2 Android entrypoint source A (`33fba2ef`,
      private fork `a608ed1`):** one Android-only, default-off branch
      enters the shared replay core with strict capture/backend/Turnip
      flags and drains logcat before exit. Static checker50/50; no build,
      APK or device action. `local/research/N8D7M12P2/ORCH-GATE.md`.
- [x] **N8D7M12 Part 3 Android package A (`fd1c3739`):** one isolated
      `assembleRelease` passed in 5m18s; source gates show the intended
      seven-file overlay, and the 153,753,116-byte arm64 APK contains the
      new replay runner plus unchanged Turnip/HAL. APK SHA `caa11102…f512`
      matched on WSL and Mac. No Odin action or runtime default-off proof.
      `local/research/N8D7M12P3/ORCH-GATE.md`.
- [x] **N8D7M12 Part 4 exact-input/device staging A (`cd13e5cb`+
      `661949c7`):** the already-present Odin FILES stream matched the
      1,100,696,462-byte `f6a78f71…a593` pin twice; zero pushes. Mac APK
      `caa11102…f512` and stream matched twice. Odin was unlocked, AC
      powered at 100%, ~23.1 GiB free, app stopped; lease released. No
      install/launch. `local/research/N8D7M12P4/ORCH-GATE.md`.
- [x] **N8D7M12 Part 5A replay script A (`92fe35f9`+`f8330b3f`):**
      reviewed-SHA-held one-run launcher prepared, checker24/24 and
      `py_compile` pass. It rechecks device/input pins, parses full
      numeric controls, handles process exit with bounded drain, and
      verifies env restoration/force-stop/lease cleanup. Script SHA
      `287140bf…1334e`; no device action. `local/research/N8D7M12P5A/ORCH-GATE.md`.
- [x] **N8D7M12 Part 5B offline Odin replay A (`41d279e7`):** one
      install/launch of the pinned APK and stream reached tick2050 with
      full numeric controls and intact cleanup. Orchestrator viewed a
      mostly black Odin PPM versus a much fuller Mac frame. Selected
      active tiles are 14/448 on Odin versus 300/448 on Mac; all 41
      sampled priv hashes match, while VRAM matches 3/41 and present
      0/41. This is a sparse offline device result, not a root-cause or
      speed verdict. `local/research/N8D7M12P5B/ORCH-GATE.md`.
- [x] **N8D7M12 Part 5C same-APK control design A (`a4253320`+
      `5cf99f70`):** OFF removes only the three tick-2050 capture flags,
      keeping the same APK/stream/backend and 41 replay rows plus PPM.
      Before-2050 mismatch voids the comparison; equal OFF strengthens
      persistent device divergence; tick-2050-only difference implicates
      instrumentation. Checker16/16; corrected dynamic mini lease plan.
      No run or cause verdict. `local/research/N8D7M12P5C/ORCH-GATE.md`.
- [x] **N8D7M12 Part 5D1 OFF launcher A (`2df02d31`+
      `dda8fa99`):** same APK/stream/backend with three tick-2050
      capture flags absent; exact 41-tick replay sequence and PPM still
      required. Final script SHA `223fd15e…03170`, checker30/30.
      No device run or graphics verdict. `local/research/N8D7M12P5D1/ORCH-GATE.md`.
- [x] **N8D7M12 Part 5D2 OFF Odin replay (`34a9c6c5`):** one exact
      APK/stream install/launch PASS with 41 ordered rows, clean app/env/
      lease cleanup. Orchestrator viewed another sparse PPM. ON/OFF
      priv hashes match 41/41, VRAM 19/41, present 25/41; first GPU
      difference at tick850, before the removed flags act. **Causal
      comparison VOID**, no speed or root-cause verdict.
      `local/research/N8D7M12P5D2/ORCH-GATE.md`.
- [ ] **N8D7M12 same-env repeat:** characterize Odin GPU hash/PPM
      run-to-run variance with one separately gated OFF repeat before
      another ON/OFF comparison.
- [ ] **N8D7M12 Mac OFF replay:** run a separately gated same-binary
      Mac control with the exact stream after the Odin OFF result.
- [ ] After N3: rebase `n2-android` onto the folded `ssx3` (E32 lands the
      codegen dir); the env shim goes onto `ssx3` through E. Input: pad
      script now, touch/controller H8 later.

## T — PCSX2 reference traces (bytesize)

- [x] **T47 PASS (09-22):** PCSX2 v2.9.75 reference frames (HW + SW,
      agree 0.7–1.8) for title → menu → Select Character → Setup → Select
      Event, diffed against the recomp. Orchestrator read by eye (SC): the
      recomp **misses the 3D Zoe model**, the big orange "3", the
      snowflakes and the ◀ ▶ arrows, and draws PS2 button-glyph cells in
      the TL/BL corners instead: wrong atlas cells plus a missing-3D
      problem. Select Event shows a blue graphic where PCSX2 has a map
      photo. Healthy Snow Jam load (T46 R3 trace): ENTER → race in ~109
      emu-s, one continuous 990-iteration `_sceCdSC` read loop, 1.75 MB
      SPU voice upload, EE semaphore spin only while CD reads continue.
      Gaps: LBN and RPC payload IDs not in trace.
- [x] **T48 PASS (09-22):** 11,591 healthy VU1 programs, 0 over 65,536 (SC max 2,090, race max 23,540); per-draw path tags + dumps at SC and race. Was: PCSX2 per-draw census by GIF path + VU1 program
      cycle lengths + `.gs` dumps at Select Character and race start
      (Happiness). Healthy side for the recomp's missing-3D hypotheses
      H1 VU1 65,536-cycle budget truncation / H2 GS-side / H3 VU1 math.
- [ ] Keep T tied to named E/G questions (reference captures for
      menu/race timing once E reaches them).

## I — iOS recomp

- [x] **Frontier review round 2 (Fable, 09-23):**
      `docs/research/review-2026-09-23-frontier-2.md`. Top items:
      1. the `log@0x40D610` stub uses the float ABI for a double routine →
         TEX1 K = 0x801 (verified);
      2. the VU1 EFU table is shifted (ERSQRT runs as ESIN in the hot
         vertex loop; verified);
      3. ~4,045 interior prologues are unregistered (858
         data-referenced), and the missing-target policy can't fail;
      4. COP0 Count is frozen;
      5. PINTEH has the wrong lanes;
      6. **the RNG is seeded from host time via `sceCdReadClock`**, which
         causes the run-to-run divergence;
      7. CSR isn't W1C and VSINT/FIELD are clobbered;
      8. a VIF1 DIR=0 readback is parsed as VIFcodes;
      9. the FPCR scope.

      Plan: E53 (+ items 1–2 added) → **E54** semantics batch 2 → **E55**
      determinism mode + hash tap → **E56** function-boundary closure
      (auto interior prologues, `stop` policy) → N7 Odin → E57 VU1 speed.
- [x] **E56 (801bada; Part 2 9c9b424): function-boundary closure works and is folded.**
      - The recompiler rule (interior `addiu sp,-N` after a `jr $ra`, plus
        data-referenced leaf starts) adds 2,049 resume entries (3,717
        prologues accepted / 404 rejected); E46 19/19 and AU5 3/3 are
        found.
      - Code +0.07% generated, `.text` +2.2%; 537/537.
      - `PS2X_MISSING_FUNCTION_POLICY` (dev = stop) plus counters: zero
        misses through tick 2378 (into the race).
      - The stop came from the SC frame-hash gate, the orchestrator's
        error: free-running boots aren't frame-deterministic before E55.

      **Part 2 PASS:** folded onto `13cac7f`, pushed fork `ssx3` to
      `8e2864a`, and promoted the E56 regen as canonical codegen.
      Taps-OFF 548/548, taps-ON 643/643. The bounded stop-policy boot
      reached tick 5353 (60.71 guest seconds after race start) with zero
      missing function targets and zero unknown syscalls; four unhandled
      RPC pairs remain counted. Orchestrator viewed the SC and two race
      frames: Zoe, terrain and HUD render, with the known dark GS
      composite occlusion. Runner-dir diff from upstream empty. This was
      a diagnostic boot, so it adds no speed row to the ledger.
      **Next:** W1F fold; E60 sky; then E54/E55/E57.
- [x] **E59 (8528a43): sky mechanism remains unproved.**
      - FPMODE=ieee and the EFU revert had no visible sun. One full-VU0
        revert boot showed a sun/flare at tick 2103; the narrower VCALLMSR,
        VSQI and combined reverts did not. These were different race scenes,
        so the one frame is a lead, not proof that E53 introduced a second
        sky bug. E53's new VU0 semantics match PCSX2 on their unit inputs.
      - A sky-like packet (TBP0 11017) has ALPHA 0x1/CBP 10756 here vs
        0x2a/14473 in PCSX2, but the scenes are unmatched and the texture
        identity is inferred. No writer or causal packet defect is proved.
      - Flat textures: 60 IMAGE uploads/vsync vs PCSX2's 73–74, 13 vs 23
        mip chains.

      **E60 PASS as a negative discriminator (47bbbbf):** local taps from
      boot through race ticks 2110/2116 and PCSX2 hooks from boot/race
      entry through the sampled race logged **zero `sceVu0MemReadQ` calls**.
      PCSX2 replay preservation passed 7/7 PNG hashes and exact HWSTAT.
      No VU0 qword differential, writer, or candidate fix exists on this
      route. Next sky step: E55 deterministic same-scene frames/packets,
      then trace the first ALPHA/CBP or texture-state divergence.
      **E54A Part 1 PASS (9686951):** current code already handles
      SIGNAL/FINISH bits 0–1 as W1C, but a guest write sets VSINT bit 3
      and can overwrite FIELD; VBlankStart flips FIELD without raising
      VSINT. PCSX2 acknowledges VSINT on write and raises it at a later
      GS-blank event; the named guest wait sites have **unknown reach** in
      existing receipts. **E54B PASS (9030a8f; fork `aa20d4a` pushed):**
      one CSR-status fix with W1C VSINT and timing-owned FIELD passed
      560/560 taps-OFF and 655/655 taps-ON tests. One bounded diagnostic
      I26-FAST boot reached race tick 2062; the live `0x37c0e0` read was
      `0x4000` after acknowledge at tick 40, and the poll saw `0x6008` at
      tick 41. Orchestrator viewed the character and two advancing race
      frames; the dark GS region remains. `0x396090` reach is unknown.
      VBlankStart raising VSINT is a timing approximation; exact GS-blank
      scheduling and FIELD video-mode rules stay open. Next E54 work:
      **E54C PASS (da6c2f1; fork `89bec9b` pushed):** the old PINTEH and
      PINTH macros selected wrong halfword lanes against pinned PCSX2.
      Distinct/zero/alias vector cases now match; taps-OFF 566/566 and
      taps-ON 661/661. One diagnostic I26-FAST boot reached race tick
      2057 with 0→1% HUD progress; orchestrator viewed character and
      two race frames. The four generated PINTEH guest sites have
      unproved boot reach; no generated PINTH site was found. Next E54:
      **E54D PASS (dbaeac9; fork `1aaed05` pushed):** decoded LWU
      now zero extends high-bit words against pinned PCSX2; before-fix
      snippet tests failed only LWU, after-fix suites 570/570 OFF and
      665/665 ON. One E54D regeneration made 96 occurrences at 92
      unique guest addresses; the orchestrator promoted its 9,457
      generated files to canonical `codegen-ssx3`. One diagnostic
      I26-FAST boot reached race tick 2069 in 112 s with SC/race frames
      viewed; the dark GS region remains. Static LWU boot reach is
      unknown. Next: 64-bit sign branches, COP0 Count and INTC 5/7
      before E55. **E54E running:** full-width signed branch predicate
      gate. X7's narrow dense-Qwen trial stopped at its 12-minute
      cap without a completed worker table; orchestrator source check
      in `local/research/X7/REPORT.md` is no branch fix verdict.
      **E54E FAIL (orchestrator gate):** the PCSX2 low-64 oracle and
      572/572 OFF, 667/667 ON suites support the candidate, but its
      single diagnostic boot showed one near-black SC frame and two
      black race captures. All three frame SHA reads match; only 8,000
      GIF packets by tick 830 versus E54D's 92,728. The first packet
      payload difference is index 352 (ticks 82/83). Orchestrator
      viewed frames and independently checked packet counts/FNVs.
      Runner/codegen paths and generated diffs match the intended
      change; no named repair was found, so no second boot. Fork
      candidate remains local/uncommitted, fork `ssx3` and canonical
      codegen stay at E54D. Revisit with E55 deterministic trace and
      a targeted branch-value probe; do not ship E54E now. Continue
      E54 with COP0 Count and INTC 5/7. **E54F1 source audit PASS
      (3be2747):** pinned PCSX2 Count advances one tick per EE cycle,
      rebases on MTC0 Count, wraps at 32 bits and increments by one for
      a same-cycle MFC0. Our four static Count-read PCs yield five
      generated expressions (one overlapping function); no dynamic
      reach is proved. The runtime Count field stays frozen despite
      a shared scheduler cycle clock. The orchestrator checked the
      pinned source excerpts, generated sites and receipt SHA. Next
      E54F Part 2: one shared Count clock/epoch with focused value tests
      and a functional race boot. Keep Compare interrupt policy separate:
      pinned PCSX2's event-test window is labeled a hack, and its
      interpreter Compare write differs from our emitted Cause clear.
      **E54F2 PASS (0cab7d7; fork pushed):** shared EE scheduler Count
      clock/write epoch and explicit MFC0 `$zero` helper. The first OFF
      suite was 579/580 because its test macro skipped the helper;
      the orchestrator authorized one test-only repair, then OFF 580/580
      and ON 675/675 passed. One diagnostic I26-FAST boot reached race
      tick 2079 with three viewed frames, HUD 00:00:01→00:00:05 and
      progress 0→1%. Five generated Count reads in four files; canonical
      codegen promoted, E54D kept for A/B. No Count-site dynamic reach
      or speed claim. Compare/interrupt timing, signed branches and
      INTC 5/7 remain open; no additional boot was used.
      **E55A1 source audit PASS (65652ff):** the current `sceCdReadClock`
      HLE returns eight BCD clock bytes from host local time; a prior
      I26-FAST park snapshot reaches its generated shim twice, including
      the guest `0x31ae80` caller. That caller combines two returned
      words into an input for six writes at `0x4ff018..0x4ff02c`.
      Their downstream identity as RNG state and the exact live reply
      bytes are unproved. A narrow `PS2X_DETERMINISTIC=1` fixed UTC
      clock is ready for implementation; default clock behavior remains
      real-time. The orchestrator checked the HLE/shim/guest code, prior
      reach receipt and BCD arithmetic. Idle event order, pad and memory
      card state remain separate E55 work. **E55B1 scheduler source audit
      PASS (799655a):** host deadlines gate which cycle-due events enter a
      batch and select idle timer versus scheduled-event target; within a
      batch the order is guest cycle, type, ID, sequence. The orchestrator
      checked the pinned source and 7,153-byte receipt SHA. A cycle-only
      option needs focused same-cycle, crossed-cycle and timer tests;
      ExternalWake has no guest-cycle timestamp and remains a separate
      placement policy. No implementation or speed claim yet.
      **E55A2 PASS (6232cf1):** exact `PS2X_DETERMINISTIC=1` now returns
      fixed UTC RTC bytes `00 56 34 12 00 16 07 04`; other values use
      host-local time. The actual-stub test covers repeated calls, TZ
      changes, invalid guest pointer and host fallback. OFF 581/581 and
      ON 676/676 passed. One I26-FAST diagnostic boot reached tick 2054
      in 101.976 s; three frames were viewed and race HUD progressed
      00:00:01→00:00:05, 0→1%. The guest clock shim was reached twice.
      Fork `4f93216` was pushed after the runner-dir guard. Reply bytes
      were not captured in the live boot, and full-frame determinism is
      unproved. **E55B2 PASS (70ee130):** exact deterministic flag now
      selects all cycle-due scheduled events and the idle timer target
      by guest cycle; default host-deadline selection is retained. Three
      focused source tests cover reversed host deadlines, same/different
      cycles, timer 80 versus event 100, equality, exact flag and legacy
      contrast. One test-only compile repair preceded OFF 584/584 and ON
      679/679. One I26-FAST diagnostic boot reached tick 2053 in
      122.12 s with three viewed frames; race HUD advanced 00:00:01→
      00:00:05 and 0→1%. Early/late race PNG hashes match E55A2; SC
      hash differs. Fork `779e804` was pushed after the runner-dir guard.
      This is not a clean speed or repeatability measurement. ExternalWake
      needs a guest-cycle placement policy; pad/card isolation and a
      frame-hash tap remain separate E55 work. **E55C1 PASS (3f0c0d9;
      static only):** the hash point is after the tick/guest flag writes
      and callback/IRQ queueing at `EeScheduler.cpp:2739`, before guest
      handlers run. Direct pointers cover 32 MiB RDRAM and three 16 KiB
      regions (scratchpad, VU1 data/code). A per-runtime VU1 `execute`
      start count and XXH64 are absent at that pin; concurrency safety
      was inferred from the source. **E55C2 PASS (c1a02a7; bounded
      hashed-state repeatability):** fork source `ddaee78` (pushed)
      adds a default-OFF VBlank XXH64 tap and per-VU1 `execute` count.
      OFF suite 585/585; ON first 683/684 from a zero-filled test-order
      premise, then 684/684 after one test-only repair. Two idle boots
      matched in tick, EE cycle, RDRAM, scratchpad, VU1 data/code,
      combined hash and VU1 count through tick 2053. A four-CPU-loaded
      boot matched through its complete tick 2052 prefix. Each boot
      started with the same empty card manifest and pinned inputs; no
      hash/log cap. Diagnostic only: no clean speed, full-frame,
      later-tick or other-platform claim. Nondefault RDRAM allocation
      size lacks a tap-visible size accessor; production and test use
      the default 32 MiB. Pad merge, nonempty card state and
      ExternalWake timing remain open.
- [x] **E55D1 ExternalWake/pad/card source audit PASS (`4313690`):**
      pinned `ddaee78` has no in-tree production caller of `postEvent` or
      `postEeEvent`; direct MPEG waiter completion is separate. The
      external FIFO carries no guest cycle and is outside scheduled-event
      ordering. Pad data enters RDRAM at `scePadRead`; card reads and
      directory entries also enter RDRAM, including host timestamps.
      No boot or determinism claim. `local/research/E55D1/ORCH-GATE.md`.
- [x] **E55D2 pad/card hook audit PASS with correction (`388ff9ed`):**
      eight source rows show no existing default-OFF, bounded hook covers
      every successful 32-byte pad read and card guest write in order.
      E3 has a narrow arming/window filter; E44 mc-read is nested under
      E3; the guest-range hook is a no-op. Fixed E41 watch words do not
      provide general coverage, but zero possible overlap was not proved.
      No build, boot or determinism claim. `local/research/E55D2/ORCH-GATE.md`.
- [x] **E55D3 bounded pad/card write tap PASS (`0dca034e`, fork `bab6eb3`):**
      default-OFF shared sequence covers pad read, card directory copy and
      card read guest writes, including positive `fread` bytes with `ferror`.
      First build and semantic repair rebuild passed; 3 new structural
      tests passed. Worker suite from wrong cwd was 686/687; orchestrator
      reran the unchanged binary from fork root, flag unset, **687/687**.
      No boot or determinism claim. `local/research/E55D3/ORCH-GATE.md`.
- [x] **E55D4 pinned pad/card A/A PASS (`df99252f`):** two sequential
      I26-FAST race boots with the default-OFF tap enabled bound at tick2058;
      hash rows 1..2053 equal 2053/2053 and ordered pad guest-write lines
      through tick2053 equal 3996/3996 including payloads. Each log has a
      complete flush-proof line after the window. Empty card manifests
      match; no getdir/mcread path executed. The sole `Controller` HID
      match is an internal NAND sensor, not a gamepad. Bounded A/A
      repeatability only, no full determinism or speed claim.
      `local/research/E55D4/ORCH-GATE.md`.
- [x] **E55D5 one-change pad comparison PASS (`e80163eb`):** exactly one
      I26-FAST entry changed from Cross to Square at 33517 ms. One B1
      boot against E55D4 A1 first differs at ordered pad guest-write
      seq3909/vsync2010, with metadata identical and button bytes changed;
      hashes match through tick2010 and first diverge at tick2011.
      Both traces complete through tick2053 with flush proof, empty
      cards and no live gamepad. This is a bounded input/write/hash
      discriminator, not full determinism or speed. Gate:
      `local/research/E55D5/ORCH-GATE.md`.
- [x] **E55D6 card-path reach design PARTIAL (`5f1401a9`, correction
      `db2a3455`):** mapped three game `sceMcRead` and five
      `sceMcGetDir` call sites in the save-manager cluster, but neither
      seeded-title nor save-menu trigger has a proven menu route or tick.
      Empty-card E55D4/D5 traces have zero calls. GetDir writes are
      conditional on query match, max count and mapped destination;
      host timestamps may enter returned entries. No card comparison run.
      `local/research/E55D6/ORCH-GATE.md`.
- [x] **E55D7 card-path ingress PARTIAL (`586f41af`):** EE xrefs prove
      the static caller chain from three unlabeled game functions through
      the save-manager cluster to mapped GetDir/Read wrappers. String-xref
      title/login/save handlers do not give a menu-to-cluster edge; virtual
      dispatch and screen/input route remain unknown. Repeating the
      empty-card I26-FAST boot would repeat E55D4/D5's zero-call result.
      `local/research/E55D7/ORCH-GATE.md`.
- [x] **E55D8 bounded route inventory PASS/outcome C (`1ad99679`):**
      15 reviewed files and two EE xref expansions show only the
      title-to-race I26-FAST screen path; no observed save/login screen or
      supported button detour in this bounded survey. Checker rerun passed,
      with one cited-only row exempt from SHA re-read. No build/boot/card
      action. `local/research/E55D8/ORCH-GATE.md`.
- [x] **E55D9 Part 1 menu-run preparation approved (`e4801547` +
      `5b678ea9`):** final script SHA `c72e5893…10c39f4` checks pins,
      claims a mini slot and records bounded snapshots around START and
      four separated Down pulses. Orchestrator caught and corrected an
      output-directory setup bug and missing final-frame proof. Self-check
      21/21, checker 33/33; **no boot/menu verdict yet**.
      `local/research/E55D9/ORCH-GATE-P1.md`.
- [x] **E55D9 Part 2 Main Menu B (`9982a2cf` + `5dd59a9d`):** one
      lease-held Mac boot, five orchestrator-viewed frames and exact
      padscript markers show Single Event → Conquer The Mountain →
      Multi Play → Previews → Online after four Down pulses. Every frame
      shows Square: Options in the footer, but Square was unpressed; no
      Options/Save screen or GetDir/Read reachability is proved. Runner
      stopped, mini slots free, no speed claim.
      `local/research/E55D9/ORCH-GATE-P2.md`.
- [x] **E55D10 Part 1 Square-detour script approved (`55f91f88`):**
      script SHA `03536b0c…4447e3f` has START tick636, one Square at
      tick820, pre/post full-frame proof, pinned inputs and mini lease.
      Self-check 25/25, checker 35/35; no boot or screen verdict.
      `local/research/E55D10/ORCH-GATE-P1.md`.
- [x] **E55D10 Part 2 Options opened A (`64841c22`):** one Square at
      the settled Main Menu opens a readable Options screen. Viewed
      post-press frames list Game Options, Sound Options, Controller
      Settings, HUD Options, **Save/Load**, Enter Cheat, Credits and DONE;
      Triangle: Previous is visible. Save/Load was not selected, and no
      card API reach is proved. One bounded Mac boot, cards unchanged,
      mini slots free; no speed claim. `local/research/E55D10/ORCH-GATE-P2.md`.
- [x] **E55D11 Part 1 script approved (`9724d596`):** prepared Start,
      Square, four Down pulses, one Cross, pre/post frames and the E55D3
      GetDir/mcRead probe. Self-check 31/31, checker 42/42; no boot,
      screen or card-API verdict. `local/research/E55D11/ORCH-GATE-P1.md`.
- [x] **E55D11 Part 2 submenu opened B (`7c8d6228`+`693d8d66`):**
      viewed Save/Load highlighted before Cross and its six-item submenu
      afterwards. Four GetDir calls at ticks118/122/126/223 were early
      empty-card checks, with no copied bytes; none occurred after the
      Cross at1360, and no mcRead occurred. One bounded Mac boot, cards
      unchanged, mini slots free; no speed claim.
      `local/research/E55D11/ORCH-GATE-P2.md`.
- [x] **E55D12 Part 1 script approved (`d9c41ef6`+`edc951b3`):**
      prepared the E55D11 menu spine plus one Down at1540, pre-choice
      Load game highlight target1620, one Cross1700 and final frame≥1800.
      Probe distinguishes any post-choice GetDir/mcRead from early calls;
      self-check33/33, checker46/46. No boot or card verdict.
      `local/research/E55D12/ORCH-GATE-P1.md`.
- [x] **E55D12 Part 2 Load game API reach A (`c558992d`+`63a34f91`):**
      viewed Load game highlighted before Cross and a six-empty-slot
      MEMORY CARD screen afterward. A new GetDir at tick1740 followed
      the choice at1700; it returned empty, with no copied table bytes
      or mcRead. Early four empty GetDir calls are separate. One bounded
      Mac boot, cards unchanged, mini slots free; no speed or saved-game
      compatibility claim. `local/research/E55D12/ORCH-GATE-P2.md`.
- [x] **E55D13 seeded-card design B (`de495dc8`):** the tick1740 GetDir
      returned empty, but the existing probe omits the requested path and
      pattern. `BASLUS-20772` is a name-only string; no valid save bytes
      are pinned. The read-only design proposes a default-off sibling
      path record without changing guest results. No seed, build or boot.
      `local/research/E55D13/ORCH-GATE.md`.
- [x] **E55D14 Part 1 OTHER (`daacf343`):** OpenCode denied its first
      source edit in the new private worktree; its `../*` edit rule won
      over the scoped allow while the pane started in ssx3. Worktree
      remains clean at `bab6eb3`; no patch/build/boot or card verdict.
      `local/research/E55D14P1/ORCH-GATE.md`.
- [x] **E55D14 Part 1B path tap source A (fork `80777cb`):** launched
      inside the private worktree; one default-off `getdirpath` sibling
      adds escaped raw/normalized query, parent, pattern and host without
      changing guest results or existing status rows. One new tiny-cap
      test failed, then one header repair passed; final suite 693/693,
      runner `d8fa114d…ef04`, 12/12 receipt checks. No boot/guest query.
      `local/research/E55D14P1B/ORCH-GATE.md`.
- [x] **E55D14 Part 2A path-run script A (`079b57a5`):** exact E55D12
      pad route, new runner/fork/lane pins, `.work/`-aware precheck and
      500+100 s maximum active/grace cap; self-check38/38 and
      checker57/57. Script SHA `fa9444a9…85694`. No boot or card query.
      `local/research/E55D14P2A/ORCH-GATE.md`.
- [x] **E55D14 Part 2B empty-card path A (`dae3007e`):** one bounded
      Mac boot viewed Load game selected and its six EMPTY slots;
      five paired path/status rows include post-choice tick1740 raw
      `BASLUS-20772-GAM*`, query `/BASLUS-20772-GAM*`, empty parent,
      same pattern and private mc0 root. Cards stayed empty, no copied
      bytes or mcRead, checker68/68; no save or speed verdict.
      `local/research/E55D14P2B/ORCH-GATE.md`.
- [x] **E55D15 Part 1 save inventory B (`18475d49`):** the observed
      wildcard maps to entries directly under mc0, but local run cards
      are empty and no valid save export/image was found in the bounded
      project inventory. Bytesize PCSX2 cards were traced UNFORMATTED;
      the named remote directory and PCSX2 memcard dir contain no
      candidate. Share is unmounted. No seed, card read or speed result.
      `local/research/E55D15P1/ORCH-GATE.md`.
- [ ] **E55D15 seed follow-up (parked):** resume only with a
      provenance-pinned SSX 3 (USA) save export/card image and verified
      contents; no invented wildcard-matching file.
      Park ExternalWake policy until a production poster is found.
- [x] **W1 (f55696d): widescreen works.** Mode 2 (anamorphic) is forced by
      `PS2X_WIDESCREEN` (default on) at the game's display apply;
      `PS2X_ASPECT` overrides it; 545/545. The 3D keeps its proportions;
      2D title/menu/HUD widen ~33% (the game doesn't squeeze 2D in
      anamorphic mode). **Brad accepted the stretch for now (09-24)** as
      the 16:9 default. The `w1-wide` branch includes I26's presenter/vpad
      (`8a357ac`). Fold it into `ssx3` after E56's push, then reinstall
      the iPhone (install only).
- [ ] **Brad's iPhone check-in feedback (09-23 evening, Select Mode/Peak
      screenshots):**
      1. fonts look off (kerning);
      2. snowflakes sometimes show a square texture;
      3. many sprite-sheet artifacts (ghost layers, boxes, stray glyphs);
      4. the auto-run waits too long (cut ~90%);
      5. virtual touch controls wanted;
      6. a pink screen for ~1 s at startup (= the `MAGENTA` no-frame
         placeholder, `ps2_runtime.cpp:535`).

      **G46 PASS (464bebf):**
      - Items 3–9 (sprite-sheet atlas cells, striped "snowflake" quads,
        ghost LEVEL/icons, glyph bars, controller diagram): all three
        renderers (CPU, paraLLEl, PCSX2 gsrunner) draw them from our
        stream, and PCSX2's own run doesn't, so they're **upstream: wrong
        texture-page contents** (E51 streaming → E53/E54).
      - **Fonts = host presentation** (POINT filter at a ×2.95 non-integer
        scale + 8:7 instead of 4:3) → added to I26.
      - One CPU-backend bug fixed: a triangle fill rule (a shared-edge
        double blend made a dotted diagonal seam). `g46-gs` `104dd7f` +
        test; to fold into `ssx3`.
      - Tool: a `.gs` converter for PCSX2 gsrunner replay of our streams
        (`local/research/G46/g46_rec2gs.py`).
      → **I26** (items 4, 5 and 6) and **G46** (items 1–3: replay our GS
      stream through paraLLEl/PCSX2 to classify each artifact as backend,
      upstream or authentic).

- [ ] **I25 (09-23, Brad: iPhone check-in builds):** iOS to parity with
      Android on Brad's iPhone:
      - env shim;
      - an auto-route pad script as the default no-controller check-in
        mode;
      - controller union;
      - aspect-fit landscape;
      - dumps off;
      - a one-script rebuild.

      Base: fork `b48b502` + `codegen-ssx3-e49`, branch `i25-ios`.
      **Blocked on Brad (09-23 17:16):** the mini has no provisioning profile
      for `org.ps2x.ps2entryrunner`, and Xcode has no account ("No Accounts").
      The fix is Xcode → Settings → Accounts → add the Apple ID for team
      LQ3V7772Q2. Meanwhile I25 builds the prefixes and code up to signing
      and polls for the profile. The SSD iOS prefixes were deleted in V2
      tier 2 and are rebuilt from recipes.
      **Unblocked 17:19 (Brad: copy from the laptop):** wildcard profile
      `f0793278-…` (team `*`, expires 2027-09-16, lists the iPhone) copied
      to the mini's `~/Library/Developer/Xcode/UserData/Provisioning
      Profiles/`; SHA matches the laptop.
      **I25 PASS (dc4d85c): installed on Brad's iPhone (install only).**
      - The Simulator plays itself: title → SC (rider) → Happiness race
        (HUD live).
      - Env shim + Settings.bundle auto-route toggle; controller union;
        landscape aspect-fit.
      - Fixed an iOS 27 present-path bug (window-scene attach) and
        excluded the imgui debug panel.
      - `build-install.sh` + `sim-run.sh` in `local/research/I25/`.
      - The iPad is installed, but the launch was refused while locked.
      - Open: G1 controller by hand, and G2–G4/G6 on real hardware (an iPad
        run when it's unlocked).
      - Part 2: rebuild on `eac6cba` (FPU fix) with canonical codegen and
        reinstall.
      **I25 Part 2 PASS (7b58fbe):** the iPhone has the `eac6cba` +
      canonical-codegen build (install only), and the Simulator race draws
      the world. First iOS lane ever to show rendered frames (the
      UIWindowScene fix). `codegen-ssx3-e49` deleted.
      **I26 PASS (c514c8c), iPhone reinstalled (install only):**
      - black startup, not pink (`73b8b3a`; its fold conflicts with I25's
        test registration, so it rides the E53 fold);
      - **I26-FAST** reaches the race HUD at tick 1714 (was ~7100): 21% of
        the guest time and 31% on the Simulator wall clock. The 10% target
        is under the game's floor with a 1 s margin, and the floor analysis
        is accepted;
      - **found: the Rival card ignores X while down is held** (E33's 45 s
        wait was an accident of that);
      - 4:3 + bilinear by default (`PS2X_ASPECT`, `PS2X_PRESENT_FILTER`);
      - virtual controls (hidden once a controller is used; Settings
        toggle), exercised with synthetic touches only; 608/608.
      Fork `i26-qol` `8a357ac` (local).
- [x] **I27A partial (23d6f29): iOS HiDPI transport works; native render fails.**
      One local fork candidate `i27-hidpi` `4ebb2ac` sets SDL's HiDPI flag
      only on iOS. Mac taps-OFF suite 585/585; one Simulator build/install
      and I26-FAST run reached race tick 2372 within 161 s. Drawable grew
      from 874×402 to 2622×1206, but raylib screen/render stayed 874×402.
      All four viewed 2622×1206 screenshots confine the game to the
      lower-left 874×402 region; full HiDPI gate FAIL. Pinned raylib's
      SDL2 `GetWindowScaleDPI()` returns 1, so its viewport uses point
      dimensions. Candidate remains local; no device install or fork push.
      **I27B next:** fix the SDL2 drawable/window scale in the pinned
      raylib path, verify full-viewport rendering and font appearance on
      the Simulator before any fold or device install. iPad still locked.
- [x] **I27B PASS for native viewport (69ed7de):** local fork candidate
      `04f3ace` adds a checked-in, pinned-raylib SDL2 DPI patch hook on top
      of I27A. Mac taps-OFF suite 585/585. After stopping an invalid O0
      partial-cache build, a fresh verified `-O3 -DNDEBUG` Simulator build
      installed and ran I26-FAST to tick 2363. Window stayed 874×402 points;
      drawable and raylib render both became 2622×1206 pixels. The four
      SHA-paired frames were viewed: title, Select Peak and advancing race
      fill the intended viewport. Guest font detail is visually unchanged
      from W1F2 because the source image is still low resolution; native
      virtual-pad edges are smoother. Dark GS race geometry remains. No
      touch test, device install, speed claim or fork push. Runner-dir guard
      empty; lease free. **Orchestrator fold:** `04f3ace` fast-forward pushed
      to fork `ssx3` after the N8D4 pinned replay completed, with empty
      runner-dir diff. **Next: build/sign current fork and install on iPhone
      only; recheck Simulator if build configuration differs.** iPad run
      awaits Brad unlocking it.
- [x] **I27C PASS for signed iPhone install (ed49b74):** exact folded fork
      `04f3ace` with runner guard empty, canonical E54F2 codegen and pinned
      private raylib patch. One fresh optimized iphoneos build succeeded;
      compiler response contains `-O3 -DNDEBUG` and diagnostic flags are
      OFF. Staged ELF/ISO and signed arm64 binary passed SHA pairs;
      `codesign --verify --strict` passed. `devicectl device install app`
      exited zero on Brad's paired iPhone 16 Pro Max. Signed binary
      `30bdafdc…2d01b68`; no launch, test, screenshot, iPad action or
      device-rendering/speed claim. Scratch 3.5 GiB, global 130.6/200 GB.
      **Next iOS device gate:** install and run on iPad after Brad unlocks it.
- [x] **W1F2 PASS for Simulator + iPhone install (2fc2242):** restored
      I25's bundled `ps2x.env`/`PS2X_BOOT_ELF` and UIWindowScene wiring
      on the W1F fold, retaining I26 controls and W1 presentation. Fork
      `ssx3` pushed to `bc1c70f`; host tests 559/559. Simulator title,
      Setup Character and race HUD through 00:00:08 viewed; iPhone signed
      app installed, never launched. **iPad run pending Brad unlock**:
      `passcodeRequired: true` on repeated checks, so no install/launch.
      I26 presentation and virtual pad are folded.

- [ ] Re-probe on the iPad only after a relevant runtime change (E30's
      MPEG fix or the E29 bypass path). Branch `i23-ffmpeg-ios` @ `aa73dbc`.

## W — widescreen (backlog, Brad 09-23)

- [x] **W1 validated (Codex Sol, `local/muse/prompts/W1.md`): 16:9 by default; Mac fold pushed.** Lead: on the GC build the game's own Options > Widescreen rendered anamorphic and the host stretched it (old `native/ios/App.mm`).
      **W1 Part 1 (ce2018c):** the native option exists (`kT_19Widescreen`,
      `…169`, `…Animorphic`). The flag is bits 20–21 of the options block at
      `0x535610` (0 off / 1 16:9 / 2 anamorphic), applied by `0x228c08` →
      vtable method `0x377950` (mode 2 = horizontal scale 0.75). Profile
      loads re-apply it (`0x152bb0` → `0x228c08`). The candidate
      (`PS2X_WIDESCREEN=1` → mode 2 before the apply, presenter 16:9) is
      built. It stopped on a wrong-cwd suite run; resumed for boots.
      1. Find how SSX 3 PS2 enables widescreen:
         - a native options/profile flag, vs a patch (the NetherSX2 Odin
           gate used a "widescreen patch", see the ledger);
         - what the GameCube version's enablement changed (`docs/reserve.md`
           / the archive).
      2. Enable it by default: a flag default, or a boot-time patch set (not
         an ELF edit).
      3. The presenter follows the mode (16:9 when on, 4:3 otherwise;
         `PS2X_ASPECT` override).
      4. Validate menus, SC and race on the Mac/Simulator vs PCSX2
         widescreen; check 2D/HUD stretching.

      **W1F Mac/fork PASS, iOS BLOCKED (185fc72):** folded I26/W1 onto
      E56 and pushed fork `ssx3` `8acb4b3` after the runner-dir check.
      Release suites 556/556 taps OFF and 651/651 taps ON; Mac I26-FAST
      boot reached race tick 2057 and three frames were viewed. The
      Simulator app built and installed, then exited before title because
      the fold lacked I25's `prepareEnvironment`/`PS2X_BOOT_ELF` startup
      path. iPad and iPhone steps were not run. W1F2 repairs this path;
      preserve Brad's iPhone install-only rule.

- [ ] **W2 PARKED (Brad, 09-23): upscaled internal resolution.** Don't
      schedule it. Brad prefers widescreen (W1, a known supported mode) and
      the 120 Hz sim over fighting upscale artifacts: framebuffer-as-texture
      post effects, half-pixel offsets, sprite-atlas bleed, VRAM
      reinterpretation and CPU readbacks. If it's picked up later:
      paraLLEl-GS upscale once it's the live backend, a PCSX2 2×/3× preview
      of which SSX 3 effects break, then source-level fixes in the recomp
      and an integer-multiple default per device.

## A — audio (new 09-23)

- [x] **AU1 PASS (7f6c09f):** no sound code runs today.
      - The EE loads SNDDRV.IRX (EA SND, symbols kept) and LIBSD.IRX, and
        binds SND `0x534E44` (one init RPC, unhandled).
      - The EE sound thread sleeps on sema 36, waiting for a **SIF cmd-1
        tick from the IOP that never comes**. The runtime stores
        `sceSifAddCmdHandler` handlers but never calls them, and
        `sceSifSendCmd` drops its packets.
      - The EE still reads `charsel.mus` (menu music) and then stalls.
      - Routes: (a) HLE SND + host mixer; (b) upstream iop-emulator (no
        SPU2, stubs sifcmd; not recommended wholesale); (c) run SNDDRV on
        a small R3000 core + capture libsd AutoDMA.
      - **AU2 spike running:** the protocol table + a delivered tick,
        answering whether the music is EE-mixed PCM or IOP-side XA.
- [x] **AU2 PASS (823c613): the music is EE-mixed PCM.** EA SND decodes
      EA-XA and mixes on the EE (36 kHz stereo). Each tick it hands the IOP
      384 finished frames in tag 1 of a tag buffer; the IOP only resamples
      36→48 kHz for the SPU2 AutoDMA. No SPU uploads and no voice records
      over menus and race start.
      - A per-vblank spike tick wakes the sound thread (9,228 signals). The
        menu and race music stream from disc.
      - A 149 s lldb capture of the mix is continuous music: a beat grid,
        and a section change at the track switch. Its race-section tempo
        fingerprint matches `poorleno.mus`.
      - Real tick rate = 93.75 Hz (the spike's 59.94 ran the sound clock at
        0.64×).
      - Latent runtime bug: `_sceSifSendCmd` 0x426078 is bound to the wrong
        argument layout.
      - **Incident:** the lldb-attached boot ran ~10.5 min unleased and
        over the cap (the harness lost the child). Other lanes' timings
        from ~23:59–00:10Z are suspect. Rule: no debugger attached to
        harness children.
      - The capture was sent to Brad to listen to (G1).
- [ ] **AU3 (Codex Luna):** SND HLE: a tick on the guest cycle clock at
      93.75 Hz, tag-1 PCM → ring → raylib AudioStream, the `_sceSifSendCmd`
      binding fix, a WAV tap and an underrun count; Mac first. Then
      Simulator/Odin.
- [ ] **AU4 (Codex Sol): PCSX2 reference capture of the EE tag-1 mix.**
      Brad: AU2's capture is "recognizable but distorted". The orchestrator's
      stats: no clipping or duplicates, but the |Δ| at the 384-frame seams
      is 1.56× the rest, and ~3,940 zero crossings/s. Separates (1) the tick
      rate (59.94 vs 93.75 Hz) at the seams, (2) decode/mix arithmetic
      (broadband), (3) a capture artefact. Also a listenable PCSX2 file.
      **AU4 Part 1 (72c09c9):** the hook filter used the wrong address
      (orchestrator brief error: `0x512E40` is the tag-1 record inside the
      `0x512B80` DMA buffer), so no records were written. The partial PCSX2
      video audio (menus, 119 s) **sounds clean to Brad**, so the distortion
      is ours, not the source material. Part 2 (approved): the corrected
      filter + a full capture + the comparison.
      **AU4 Parts 2–3 (b866a0f, cbcfdb9):** the menu mix aligns with PCSX2 at
      NCC 0.975 and the **lag is constant to within 1 sample over 32 s**
      (no jumps), so it isn't timing (the orchestrator's tick-rate guess
      was wrong). After per-window correction the residual is 0.23 of the
      PCSX2 RMS, rising with frequency (0.19 → 1.06 at 12–18 kHz): an
      **arithmetic** difference in the decode/mix.
- [x] **AU3 Part 2 (d6e947e):**
      - SendCmd ABI fixed (`c19a5d6`, 601/601);
      - the sound tick runs at exactly 93.75 Hz of guest time;
      - sema 36 is signalled and waited 15.6k times;
      - the race starts and advances;
      - host-stream underruns run 1.1–1.7 M frames/min, a speed symptom
        (the guest is ~0.3×);
      - the WAV wasn't written (`_Exit` skips the destructor).

      **Orchestrator find in its log:** the only missing target,
      `0x3cb7a8 → 0x3c9520` (26k×, also in AU2): the sound library's
      function-pointer table entries `0x3c9520`/`0x3c95f0` (plus the leaf
      `0x3c9518`) are merged into `sub_003C9420`. That is the prime suspect
      for the distortion. Folded into AU5.
- [ ] **AU5 (queued; launch after E58 pushes):** re-capture on the folded
      tree (E53 semantics), which may fix it outright; else an instruction
      census of the XA decoder + mixer, a decoder-vs-`au2_eaxa.py`
      differential, and one named fix.
      **AU5 (3ec947c):**
      - on `b9647f5` + AU3, with 0x3c9518/0x3c9520/0x3c95f0 as function
        starts: **0 missing targets**;
      - also fixed the host tag-1 PCM offset (+8 → +16) and made the WAV
        save incrementally;
      - only a 3.35 s menu overlap with PCSX2 (I26-FAST skips the menus
        fast). In it, the band residuals fell (0–2k 0.19→0.10, 2–6k
        0.52→0.20, 6–12k 0.57→0.39, 12–18k 1.06→0.77);
      - the decoder matches a float XA model to within 0.017 (no decoder
        bug);
      - census: untested MMI on candidate mixer paths (PINTEH ×4 in
        0x3CB538, PPACH/PEXTLH/PSRAW, VU0 transfers).

      Sent to Brad to listen. Fork `au5-snd` `ddf4f66` (local).
      **Next:** a longer-overlap capture (E33 route, or sit on the menu) if
      it still sounds off.

- [x] **AU6 (02c9204): menu EE loudness deficit refuted on matched content.**
      E33-route tag-1 PCM aligns with PCSX2 for 59 s: RMS 5,010 ours vs
      5,002 PCSX2 (+0.014 dB). AU5's ~1,300 RMS capture had no pad route;
      AU6 rises after the route input. Both snapshots have six active
      type-2 voices (slots 10–15) with matching levels/source callbacks;
      PCSX2's extra status-block fields did not change menu gain. The
      waveform still has a 9.3% residual, and neither race nor host
      output was pairwise captured. No volume fix is justified by this
      gate. Brad listens to `~/dev/ssx3-work/AU6/AU6-menu-tag1.m4a`;
      follow up on the exact audible scene if the symptom persists.

- [ ] (superseded) AU1 (Opus, scoping): the IOP module and SIF RPC census, the
      runtime's current handling, the sound data on the ISO, and the routes
      (HLE driver + host mixer vs LLE IOP/SPU2 vs hybrid) with costs, plus
      the smallest audible milestone.

## V — storage and hosts

- [ ] Mac mini cutover per `local/research/V1/CUTOVER.md`. Blocked:
      the mini isn't set up (Brad). Waits for active leases.
- [x] Pruned 2 stale ssx3 + 7 stale fork worktree entries (09-22, dirs were
      already gone). Keep the SSD `ps2x-i*/fork-wt` worktrees: they are
      the only refs holding the branchless I10–I21 commits until the fold.
- [x] **V2 PASS (09-22): SSD inventory** (`local/research/V2/INVENTORY.md`).
- [x] **SSD cleanup tier 1 done (Brad approved 09-22):** 99 deletions, 0 failures, free 27 → 369 GB (`local/research/V2/delete-tier1.log`).
      Was: 59 entries in
      `local/research/V2/delete-tier1.txt` (closed build trees, public
      clones, stale closed-lane scratch, `ps2x-p1y` whose commits are on
      `fork/archive/*`) plus the 40 `ps2x-t4` logs that the share holds at the
      same size (never `emulog-t46r3.txt`). ≈ 350 GB. Kept: `mini-transfer-0922`
      (a few days), `ps2x-e30`, live lane dirs.
- [x] **SSD tier 2 done (Brad approved 09-22):** 22 parked I-lane dirs deleted after checking no uncommitted tracked changes and every worktree head's content on folded `ssx3` (map rows ⊆ ssx3 CSV; the pre-scrub generated-code commit is intentionally gone); 15 dangling worktree entries pruned; SSD free 369 → 610 GB.
- [ ] SSD personal copies look like partial duplicates of the share (takeout parts 1–5 smaller on the SSD, aggiemail 4.6k vs 53k files): Brad to confirm before any delete.
- [x] **SSD tier 3 done (Brad approved 09-22):** GameCube reserve material
      deleted (`upstream-review`, `ssx3-archive`, `android-spike`); D1–D8/M4
      report text preserved in `local/research/reserve-gc/`. Log:
      `local/research/V2/delete-tier3.log`. Kept by Brad's call: personal
      folders (intentional partial duplicates). Not decided:
      `laptop-evacuated-0918` 28 GB, `glimmer-ize` 18 GB, `bradflix-ps2recomp`.
- [x] V1 follow-up: `emulog-t46r3.txt` mirrored to `/Volumes/share/ssx3/ps2x-t4/` (09-22; SSD + 2 share reads = `19c1b583…`, the V1 pin).
- [ ] Mac internal disk ~3 GB free: keep builds on the SSD or bytesize.

## Cross-lane

- [x] **PF1 PASS (09-22): Odin clean baseline** (N3 APK, logs off):
      title 21.5 guest vsyncs/s (0.36×), My Rules 25.5/s (0.43×), 3D menus
      down to ~1/s; GameThread saturated (36–46 ms per guest frame vs a
      16.7 ms budget); simpleperf/Perfetto blocked on the user build (needs
      a profileable APK). Launch 6 (first Odin race attempt) reached My
      Rules, **no race**: the wall-clock e31l script desyncs because Odin
      menus run ~280 s slower. Battery drains 3%/15 min on the charger.
- [ ] **Pad script keyed on guest vsyncs** (`PS2X_PAD_SCRIPT_CLOCK=vsync`)
      so one script replays the same on Mac and Odin. Goes into the E33
      instrumentation brief; then N4 carries it to the Odin.
- [x] **X2 (local Qwen, 09-22): PARTIAL.** Confirmed the counted step loop at
      0x317184 (`$s1++` per `func_317328` call vs limit `state+0x20`, in
      `sub_00316F00`), matching the published patch site; its "WaitVSync"
      sites are SetSyscall (0x74) and its "VU microcode" is EE code
      (`local/research/X2/ORCH-CORRECTIONS.md`). Next: runtime read of the
      per-frame iteration count and `state+0x20` (E lane, after E33).
- [ ] Save states for the recomp runtime (global/static state is the
      obstacle). Would cut ~10 min boots to the loading screen. Queue.

- [ ] Update `docs/route-criteria.md` for the 120 Hz simulation
      preference, and drop its stale work-queue snapshot.
- [ ] Update `docs/plan-gs-gpu-backend-2026-09-18.md` to the paraLLEl-GS
      path the G lane actually uses (it still describes a greenfield
      backend).
- [x] **X3 PASS (2823cbf, local Qwen dense; orchestrator check in
      `local/research/X3/ORCH-CORRECTIONS.md`):** 120 Hz loop map.
      - cAppMan_mainLoop: 16 jals (8 checkHalt), 19 vtable jalrs,
        4 back-edges.
      - Counted step loop: `$s1` vs `lw 0x20($s0)`, with the back-edge at
        0x317190 → 0x317128. The patch-site increment at 0x317184 is the
        **delay slot of `jal checkHalt`**.
      - Metro sites clear the frame-skip flag `[*(gp+0x2A74)+0x34]`.
      The early stalls were the 16k output cap (dev-71 added an 8k
      thinking budget).
- [ ] **X4 incomplete (local Qwen dense):** the E55 source-map read reached
      about 70k context without writing its report. A same-session resume
      produced no tokens before the orchestrator stopped it. No X4 code
      claims have been accepted; rebrief in smaller source categories if
      still needed for E55. X5's separate sparse extraction passed.
      **X4B incomplete (dense, 25-minute cap):** reached about 37.7k
      context and found the `0x31ae80` → generated `0x402520` →
      `sceCdReadClock` call and a following `0x3177c8` state-init call,
      but stopped producing output before replacing its placeholder
      report. No worker verdict or commit. The orchestrator verified the
      source anchors in `local/research/X4B/REPORT.md`; runtime reach,
      LSP confirmation and the PRNG label remain open. **X6 incomplete
      (sparse):** exceeded its 25k context cap in ~5 minutes without
      writing the named parser or any report. The worker searched for
      non-existent helper/output files despite the source shape supplied
      in its brief. Closed and marked as a failed model trial; the
      orchestrator will make the static LWU index if E54 needs it.
      **X7 incomplete (dense):** a narrow sign-branch source audit spent
      7m35s reasoning after the first brief read, wrote a placeholder,
      and still lacked a verified table or LSP check at its 12-minute
      cap. The orchestrator corrected a stale checkout pin in the brief,
      closed the pane, and independently checked the relevant source
      lines in `local/research/X7/REPORT.md`. No worker verdict/commit.
      **X8 incomplete (dense, low thinking budget):** first reasoning
      step fell from X7's 7m35s to 45s, but broad source reads took
      context to 43.8k against an 18k cap without a report. Closed at
      about four minutes. `local/research/X8/REPORT.md` is an
      orchestrator audit, not a worker table. Next trial will provide
      exact source excerpts and fixed commands.
      **X9 partial (dense, excerpt/skeleton):** the model stayed inside
      a 3.7 KiB pinned excerpt and filled four cited source rows, but
      got BLEZ/BGTZ truth values wrong. After feedback and a Python
      check it fixed the table, then wrote new false arithmetic prose.
      Closed at 20.5k context against a 20k cap, no worker commit.
      The independently verified table and model audit are in
      `local/research/X9/REPORT.md`. Use local Qwen for bounded source
      extraction with scripted numeric acceptance; keep semantic
      verdicts with the orchestrator.
      **X10 queued (sparse):** 7 KiB fork-`293fd81` source excerpt and
      six-row INTC/DMAC/VU-status table. The format checker verifies
      completeness; the orchestrator checks every classification and
      citation. This tests bounded extraction after X9's arithmetic
      failures, with no source edit or E54 verdict. **X10 INVALID:** the
      orchestrator selected line ranges from a different fork checkout,
      so three intended behaviors were absent from the pinned excerpt.
      Sparse Qwen passed the format-only checker but inferred two domains
      unsupported by the excerpt and exceeded its 18k context cap at
      about 27k. The corrected table and audit are in
      `local/research/X10/REPORT.md`; this does not score model accuracy.
      Retry as X10B with pinned symbol-located excerpts and a semantic
      checker that permits explicit gaps. **X10B queued:** the corrected
      3,581-byte excerpt includes all nine asserted source anchors from
      fork `293fd81`; the semantic checker verifies six domain/cause rows.
      **X10B PASS for bounded extraction (1851df6):** six rows and all
      nine source anchors matched; checker caught a `9..12` shorthand,
      one correction passed. Completed in 1m34s at about 20.4k context
      under the 24k cap, with only the three named reads. The orchestrator
      expanded one VU citation to cover both status bits. Interpretive
      review and dynamic reach remain untested.
      **X11 incomplete (default dense Qwen):** with a 7,345-byte fork
      `4f93216` excerpt, the model read its three named files then spent
      approximately 10 minutes in the first reasoning step. It wrote
      no row, made no LSP call and left its nudge queued; the pane was
      stopped at cap. `local/research/X11/REPORT.md` is the orchestrator
      audit, not a worker verdict. **X11B partial (low-thinking dense):**
      same excerpt with thinking budget 512 produced four cited rows and
      one LSP call, but used three forbidden Globs, missed the 3-minute
      write target, and stopped at ~24.3k context/8 minutes with no
      checker run or worker commit. LSP returned no references at the
      correct file/position, an indexing gap rather than caller absence.
      The orchestrator corrected one unsupported pool-scope claim and
      two uint32 arithmetic errors, then fixed the checker to accept
      citations whose line ranges cover the required anchors; the
      corrected table passes that checker. `X11B/REPORT.md` is an
      orchestrator audit. Use sparse Qwen for bounded, scripted
      extraction; dense source interpretation is still unproved.
      **X12 PASS for exact source-line extraction (5ce779b):** sparse
      Qwen produced seven rows from pinned N8B1 `17e90de`; the
      exact-line checker and orchestrator rerun passed 7/7. It first
      looked in the unrelated old fork checkout and then ran seven
      searches from the wrong cwd before correcting the path. Its seven
      LSP reference calls returned empty, so they establish no call
      relationship. The verified table names the Vulkan readback and
      host texture-copy sites for N8D1; it does not diagnose the black
      Android frame. Keep local Qwen on small scripted extraction jobs.
- [x] **X13 dense partial / X13B sparse PASS (09c2930):** same 4,310-byte
      pinned N8B1 excerpt and seven ordered scanout→barrier→copy→submit→
      wait→map→pack source lines. Both tables passed the exact checker 7/7.
      Dense took about eight minutes to write rows, exceeded its 15k
      context target (~21.7k visible), and its LSP call/report were still
      pending at the cap; `X13/REPORT.md` is an orchestrator audit, not a
      worker verdict. Sparse completed in 1m38 (~19.2k visible), returned
      an empty LSP result and committed the table/report. It read the small
      checker despite the two-file read limit; no other source file was
      read. The worker's 30 s, context and index explanations in its
      initial report were corrected at gate. Neither trial identifies
      whether Odin loses pixels while generating the scanout image or
      transferring it to host memory. Use sparse for exact scripted
      extraction; treat empty LSP as an unresolved tooling result.
- [x] **X14 sparse trial stopped (orchestrator audit):** a pinned 5,468-byte
      shader/Granite excerpt produced four independently correct layout
      values in about 85 s, but the worker searched for, read, and edited
      the checker outside its allowed write scope. It used prose evidence,
      the wrong fifth-field name, and a fork directory for its single LSP
      call. The orchestrator closed the pane, restored the committed
      checker, and reran it; the original 5/5 acceptance failed at row 1.
      No worker commit or engineering verdict. `local/research/X14/REPORT.md`
      preserves the raw table and audit. The next local-model trial needs an
      immutable checker boundary; N8D5B's layout repair stays with a
      standard reasoning worker/orchestrator.
- [x] **X15 dense trial incomplete (orchestrator audit):** the first pane
      was stopped before its excerpt read when the orchestrator corrected
      missing source anchors. A second pane read the corrected 11,013-byte
      excerpt but wrote no early table/report and made no LSP call before
      stop. No model accuracy or engineering claim; see
      `local/research/X15/REPORT.md`. A smaller thinking budget is the
      next local-model tuning variable.
- [x] **X16 Space Bunny Free bounded pilot (627dc06):** OpenCode Go produced
      the required eight-row TSV, all anchors resolve in the pinned excerpt,
      and one LSP definition call returned empty. EN1/EN2/INT/FFMD are
      correct; it marked four downstream branch values `unknown` because
      the excerpt omits part of `GSInterface::vsync`. The orchestrator read
      the complete interface path: the actual downstream values are 0/1/0/1,
      but those values are not all proved by the excerpt alone. The report's
      approximate elapsed time differs from the pane's 2m46 display, and
      visible context reached 40.4k versus the <18k target. No source,
      build, boot, device or GS verdict from this model trial.
- [x] **X15B local dense Qwen retry rejected (orchestrator audit):** eight
      rows and anchors present, four register fields correct, but the report
      misreads MMOD bit 5 of `0xff21` as zero and overlooks backend
      `VSyncInfo vsync = {}`. Its `raw_circuit_early_return=0` matches the
      full source only coincidentally; the given derivation is false. One
      LSP call empty. The pane exceeded five minutes and 18k context without
      a worker commit. `local/research/X15B/ORCH-AUDIT.md` preserves the
      gate and unaltered worker receipts. No GS verdict.
- [x] **X17 DeepSeek V4.1 Flash Go pilot blocked before task start:**
      provider says the workspace must enable Global regions in Privacy
      settings. Orchestrator stopped retries. Brad later enabled Global
      regions; X18 reached the model. No X17 model-quality result or config
      edit; see `local/research/X17/REPORT.md`.
- [x] **X18 DeepSeek Flash Go parser pilot (`a72172d`) partial gate:**
      saved sampled/raw vectors parse with exact 896-word SHA and numeric
      receipt; worker fixed a copied hash-object error after its first
      checker failure. Independent orchestrator check found that doubled
      commas split across two logcat segments are accepted, violating the
      brief. Expanded checker now fails. Pane used 5m25 and 65.5k context
      versus <18k target. Gate: `local/research/X18/ORCH-GATE.md`.
- [x] **X18B parser boundary fix PASS (`c71d6c7`):** the expanded checker
      accepts exactly one separator across logcat segments and rejects zero,
      two, double trailing/leading, malformed and interrupted inputs; saved
      sampled/raw vectors retain exact 896-word SHA and counts. `py_compile`
      passed. Pane 1m05 and 25.1k context, above the brief's <18k target
      despite its report saying otherwise. Helper is not yet in a future
      launcher; N8D6C released evidence unchanged. Gate:
      `local/research/X18B/ORCH-GATE.md`.
- [ ] PS2 120 Hz simulation: the game-side timestep patch sites are
      published for the PS2 build. Scope this once a stock race runs.
