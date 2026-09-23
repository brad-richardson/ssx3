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
- [ ] **Sprite/texture addressing as a common cause (Brad, 09-22, re-flagged):**
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
- [ ] **E39 (running):** MPG outcome log over menus → Select Character, then
      one fix matching PCSX2 and Select Character/race boots.
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
- [ ] **G44 (Part 3 running: diagnostic SMODE1=NTSC+ANALOG override in the shadow only; S3 showed LC=0 also blocks):** shadow path builds and renders in-process
      (470/470, branch `g44-parallel-shadow` @ `460e438`, not pushed) but 0 frame
      pairs: the recomp's SMODE1 reads 0 (`CMOD=0 LC=0`, `SMODE2.INT=1`), which
      paraLLEl scanout rejects. S3 validates the NTSC-geometry workaround.
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
