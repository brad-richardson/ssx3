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
      Android (GB1 step c).
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
- [ ] N5: Odin race with E33's vsync-keyed pad script (after E33), plus a
      dumps-off build for a quotable speed number.
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

## I — iOS recomp (parked)

- [ ] Re-probe on the iPad only after a relevant runtime change (E30's
      MPEG fix or the E29 bypass path). Branch `i23-ffmpeg-ios` @ `aa73dbc`.

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
- [ ] PS2 120 Hz simulation: the game-side timestep patch sites are
      published for the PS2 build. Scope this once a stock race runs.
