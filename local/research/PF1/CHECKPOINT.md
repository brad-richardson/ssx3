# PF1 CHECKPOINT (paused 2026-09-22 ~19:21Z, orchestrator pause)

Brief: `local/muse/prompts/PF1.md`. Clean perf baseline, Odin (+ Mac after E31).

## Done

- **Odin title baseline (2 valid launches, N3 APK `69a79e29…`, clean env
  CD_IMAGE+SKIP_MOVIE only):**
  - Presents = **~60/s** both runs (run1: 59.95/s over 19 polls;
    run2: 60.4/s over 12 polls; SF `--latency` in-history density —
    the 128-entry ring + 5 s poll spacing makes naive union-counting
    WRONG, ~26/s artifact; see `scripts/presents.py` + method note).
  - **Presents ≠ guest vsyncs**: main loop is decoupled (present thread
    `UploadFrame`+`EndDrawing` paced by `SetTargetFPS(60)`; GameThread
    runs `EeScheduler`, wall-paced VBlank 16667 µs via condvar wait —
    read in `ps2_runtime.cpp`, `EeScheduler.cpp`).
  - Guest rate: N3's `[frame:dump]` is **tick-gated** (one per new guest
    vsync — verified `UploadFrame` latches only on tick change), so N3's
    tick range 0→6671 over 309.7 s = **21.54 guest vsyncs/s (35.9% of
    59.94)** stands for the clean build too: dump work is
    present-thread-only and holds no guest lock (source-verified).
    Corroborated: GameThread **99.3%** + ~10 voluntary ctxt/s (never
    VBlank-sleeps) = saturated at the same work/vsync.
  - CPU-ms/guest frame ≈ **46.4 ms** (GameThread). Thread table:
    GameThread 99.3%, main 11.9%, app ~111.8% steady thirds.
    cpu6/7 pegged 4.32 GHz; thermal oscillates 80–104 °C (hottest zone
    mean ~92 °C). Battery 63→65→69%, charging throughout.
  - simpleperf: **BLOCKED** device-wide (`perf_event_open: Permission
    denied`; user build, non-profileable APK, no root). Perfetto
    traced_perf: config accepted, **0 samples** (840 B trace). No Odin
    symbols possible without a profileable/debuggable build (N-lane).
  - `dumpsys SurfaceFlinger --timestats` prints **0 bytes** on this
    device; `--latency` on the exact BufferStateLayer works (must
    exclude InputSink/leash layers from `--list` match).
  - screenrecord+decode-hash for guest-rate: **INVALID** (static-launcher
    control shows identical periodic diff pattern — encoder temporal-layer
    artifact). Do not reuse.
- **E31 inputs:** E31 REPORT draft read (title ~23 ticks/s Mac, menus
  1–3/s, Snow Jam loading 99% stall; e31k ended on Happiness pre-race,
  no race script exists). Reconstructed e31h Snow Jam script from
  `[padscript] press` lines (masks verified vs e31i cmdline:
  0x0008=start, 0x4000=cross, 0x0040=down). Launch-5 script = e31h
  trimmed at 255 s (presses after affect nothing: loading takes no input).
- **Void launches:** 3 (backgrounded ~15:13), 4 (lockscreen) — keyguard
  `showing=true` pauses NativeActivity within seconds. Orchestrator
  voided both, extended budget. Lockscreen root cause, not Brad's tap.
- P-lane lease: E31 owns (currently `e31l`, boot to ~19:25Z). Never held
  by PF1. Odin lease: claimed 18:45:43Z, **released at pause**.
- Data mirrored: `/Volumes/Extreme SSD/pf1/` (~22 MB logical) + text in
  `local/research/PF1/logs|scripts/` (this commit). Derived
  `fr-*.png`/`st-*.png` deleted (repro: `ffmpeg -i rectitle.mp4
  -fps_mode passthrough fr-%04d.png`); source mp4s kept.
- App force-stopped; no PF1 processes left on Mac (E31's e31l untouched).

## In flight (interrupted by pause)

- **Launch 5** (pid 5311, scripted Snow Jam path, env SHA `846d12b6…`,
  started 19:17:25Z): main menu reached by t+30 s (screencap verified),
  chain caps c1+c2 pulled, then pause hit mid-tracking. App
  force-stopped → launch 5 is **dead**; needs a fresh launch (call it 6)
  running the full chain + loading measurement (~520 s, ≤600 s cap).
- E31 still open (no `[E31]` commit; worktree on `e29-movie-bypass`).
  Mission 2 (Mac) blocked until E31 closes + lease free.

## Resume steps

1. Claim Odin lease (`echo "PF1 $(date -u +%FT%TZ)" >
   /data/local/tmp/mg/LEASE`); check keyguard `showing=false` first —
   if locked, `wm dismiss-keyguard` or wait for PIN (do NOT launch
   while locked; the launch voids).
2. Verify env on device = `846d12b6…` (scripted), clean frames dir,
   `logcat -c`, `am start`, start filtered logcat capture.
3. Track chain (screencap every ~35 s to ~t+310, focus+keyguard guards),
   then at loading: sampler 120 ticks + `top -H` ×2 + latency polls
   (fixed `{com.ps2x.runner…` matcher) + thermal pre/end.
4. Guest rate on loading screen from `[frame:dump] tick=` progression.
5. Force-stop app, release lease, `rm -rf /data/local/tmp/pf1`.
6. If E31 closed: Mission 2 (new SSD build dir, E18 recipe,
   RUNTIME_LOGS=OFF + AGGRESSIVE=OFF, 1 build + ≤2 boots ≤300 s).
7. Write `REPORT.md`, `[PF1]` commit (no push).
