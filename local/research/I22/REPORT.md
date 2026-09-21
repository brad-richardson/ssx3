# I22 — Cause-B feasibility: FFmpeg-for-iOS buildability + stub-completion interface inventory (NO behavior change, NO fork commits)

- Date: 2026-09-21. Tables, no verdicts.
- `local/research/I21/REPORT.md` read first (all of it: delivery lands on device — callback/producer/AddBs dispatched, stub `feed()` entered per the ungated warning — but the FFmpeg-OFF stub returns `false` and enqueues nothing, so main stays parked at `0x3b1028` with 0 frames; G2 names this wall and offers two candidate shapes).
- `local/research/E18/NEXT-BRIEF.md` read (all of it: host parser-output is the E-lane's separate wall — 5040 B in, 0 packets out — NOT conflated; the device wall stands on its own receipts). `local/research/E18/REPORT.md` read (all of it: R1–R6, provenance, sole-probe joins).
- Target: Brad's iPad, iPad Air 11-inch (M2) (`iPad14,9`), UDID `P` — READ-ONLY pre-state only (reachable, apps listed, 1 `ps2` PID reported, never touched). NO rebuild, NO reinstall, NO probe (the I21 build stays installed AND running, untouched).
- BASE: `3adc0478` (E18 BEHAVIOR — verified by `ls-remote` at recon; E-lane advanced 0 during I22; PINNED regardless with cause: the I21 receipts this brief builds on were taken there).
- Product: time-boxed FFmpeg-subset iOS build spike (scratch dir OUTSIDE any repo, capped) + static stub-interface inventory + host-parity checklist + recommendation row. Implements nothing, changes no behavior, ZERO fork commits (0 pushes, remote unmoved; shared clone touched read-only: `log`/`ls-remote`/`show`/`grep` only).
- Rules honored: E-lane pane never prompted/steered; no PS2 boots → no lease; no `adb`; every device-scoped `devicectl` with explicit `--timeout`; `export COPYFILE_DISABLE=1` on SSD steps (note: `cp` of xattr'd files still emitted `._*` — purged after); byte caps declared up front + tracked (spike scratch ≤10 GB: PEAK 9.2G during build, final 31M after tree removal — tabled); evidence `local/research/I22/` standalone, `[I22]` commit, no push.
- Outcome shape: BUILDS — minimal FFmpeg 7.1.1 subset (mpeg2video decoder + mpegvideo parser + swscale + avutil) configures AND compiles for iOS arm64 (exit 0, 19.3 s, 0 errors, no gas-preprocessor/nasm); the COMPLETE MPEG.cpp-used API surface (20 calls) links bare into a Mach-O arm64 executable (exit 0, zero extra frameworks); dead-stripped linked delta ≈1.2 MB (~1% of the 121 MB app); the same subset built for host decodes E18's 240 B vector with counts IDENTICAL to E18's full-FFmpeg receipts (parsed240/packets3+1/frames2+2, 16×16 RGBA) with one characterized pixel drift (R=252 vs 254, 7.1-vs-9.0 rounding, flags-independent). License: LGPL-2.1-or-later, zero GPL components. Stub inventory + parity checklist + recommendation row tabled; the decision is the follow-up's, not this report's.

Path shorthands: `W` = `/Volumes/Extreme SSD/ps2x-i22/`, `P` = iPad UDID `00008112-001224302184A01E`, `FORK` = shared clone (E-lane-owned, read-only), `MPEG` = `MPEG.cpp` @`3adc0478` (2784 lines, extracted to `/tmp/i22-mpeg.cpp` for line-numbered reading — never edited, never compiled).

## Experiment contract

| Item | Content |
|---|---|
| Hypothesis H | The smallest sufficient FFmpeg subset (MPEG-1/2 video decoder + parser + scaler) builds for iOS arm64 in this repo's toolchain (Xcode 27, iPhoneOS 27.0 SDK, Homebrew clang) and links bare; the stub-completion touch set is confined to `MPEG.cpp`; E18's committed receipts suffice for a device parity checklist |
| Observable | Spike log (fetch/configure/build/link with exits + exact errors if any); `.a` sizes + linked-size delta; license finding; stub entries + wait-condition terms + touch set + test vectors; parity checklist rows; recommendation row |
| Alternatives | H-a builds + links, subset sufficient (observed). H-b builds but fails to link (missing symbols/frameworks — tabled with the exact errors). H-c blocked (configure/compile errors — tabled, spike ends at the 2 h cap regardless). H-d subset builds but cannot decode the E18 vector (sufficiency fails — tabled) |
| Stop | All bars tabled, or any cap (2 h spike cap / 10 GB scratch / 5 MB evidence), or any FORK/E-lane conflict (none encountered). Contract outcome: H-a on every row |
| Time box | 4 h (used ~1 h wall: recon → reads → spike ~35 min → probes → report) |
| Spike cap | 2 h (used ~35 min: fetch 1 min + configure/build/link ~10 min + host-subset decode proof ~15 min + audits ~9 min). The cap did NOT bind |

## Caps (declared up front, tracked)

| Cap | Declared | Used | Receipt |
|---|---|---|---|
| `W` SSD allocated bytes (ExFAT, 1 MB clusters) | ≤ 10 GB | PEAK 9.2 GB (92%) during build; FINAL 31 MB after tree removal (tarball 11 MB + libs-ios 3 MB + logs) | `du -sh` before/after `rm -rf` |
| Evidence `local/research/I22/` | ≤ 5 MB | 112 KB logs + REPORT (17 files + REPORT) | `du -sh` + file count |
| Build parallelism | `-j2` max | `-j2` everywhere (both FFmpeg builds) | exact commands + build logs |
| Fork writes | zero fork commits, read-only clone contact | 0 commits, 0 pushes; `log`/`ls-remote`/`show`/`grep` only | §Task 1 |
| Device ops | read-only pre-state ONLY (reachability/apps/PIDs) | 3 `devicectl` calls (list/apps/processes), all with `--timeout` | `logs/ipad-prestate.txt` |
| Host runs | spike-local compiles + decode probe ONLY (no PS2 boots, no repo builds) | 0 PS2 boots, 0 repo builds; 7 decode-probe runs + 2 CLI reproductions | §spike log |
| E-lane contact | read-only inspection, never prompt/steer | E18 evidence read from committed `local/research/E18/` only; pane untouched | §Task 2 |

## Task 1 — buildability spike + stub inventory

### Spike: fetch (scratch `W/spike/`, OUTSIDE any repo)

| Item | Receipt |
|---|---|
| Tarball | `ffmpeg-7.1.1.tar.xz`, 11,019,500 B, sha256 `733984395e0dbbe5c046abda2dc49a5544e7e0e1e2366bba849222ae9e3a03b1`, via `curl --max-time 240` from `https://ffmpeg.org/releases/` (exit 0) |
| Version choice | 7.1.1 — matches the repo's pinned Windows-prebuilt family (`n7.1-241205`, `ps2xRuntime/CMakeLists.txt:285` @base). Host brew is 9.0.1 (E18's FFmpeg-ON ran against 9.0.1 — skew tabled in §sufficiency, not resolved here) |
| Tree | 8646 tarball entries; extracted 8.5 GB ALLOCATED on ExFAT (1 MB allocation blocks — `diskutil`: `Allocation Block Size: 1048576`) for ~60 MB logical. 6288 `._*` emitted by extraction despite `COPYFILE_DISABLE=1` → purged → 0 |
| Race (self-inflicted, receipted) | First `configure`+`make` ran while the background `tar` was still in flight (checked `configure` exists, not tree-complete): 2 `make` attempts failed with `tests/fate/*.mak: No such file` + `No rule to make target 'tests/checkasm/Makefile'` (log kept: `logs/spike-failed-make-partial-tree.log`). NOT a source/config defect — re-ran on the complete tree; a redundant re-extract was terminated mid-flight |

### Spike: configure for iOS arm64 (exit 0)

Full flags in §Exact commands. Salient: `--target-os=darwin --arch=aarch64 --cpu=generic --enable-cross-compile --cc="xcrun -sdk iphoneos clang" --sysroot=$SDK` + `-arch arm64 -mios-version-min=17.0 -Os`; `--disable-everything --disable-programs --disable-doc --disable-avdevice --disable-avfilter --disable-avformat --disable-swresample --disable-network --disable-iconv --disable-bzlib --disable-lzma --disable-zlib --enable-decoder=mpeg2video --enable-parser=mpegvideo --enable-swscale --disable-asm --enable-static --disable-shared --disable-debug`.

| Item | Receipt |
|---|---|
| Exit | 0 (re-run on the complete tree; `logs/spike-configure-ios.log`, full) |
| Enabled | decoders: `mpeg2video` only; parsers: `mpegvideo` only; encoders/hwaccels/demuxers/muxers/protocols/filters/bsfs/indevs/outdevs: ALL EMPTY |
| License line | `License: LGPL version 2.1 or later` — zero `--enable-gpl`, zero external libs (native decoder only) |
| Subset rationale | `MPEG.cpp` includes only `libavcodec/avcodec.h`, `libavutil/error.h`, `libavutil/log.h`, `libswscale/swscale.h`; `grep` for `avformat|swresample|swr_|avformat_` in `MPEG.cpp` = EMPTY (avformat+swresample are LINKED by CMake but never called — follow-up may drop two more libs) |
| Cosmetic | `ffbuild/config.sh: line 4: SSD/ps2x-i22/spike/install: No such file or directory` (space-in-path artifact in generated echo; exit unaffected) |
| Toolchain gaps | NO `gas-preprocessor.pl`, NO `nasm` on PATH (`which` receipt) — unneeded via `--disable-asm`. Xcode 27.0 (`27A266a`), iPhoneOS 27.0 SDK, `-mios-version-min=17.0` spike choice (app pins NO deployment target — Xcode default; tabled, not matched) |

### Spike: build for iOS arm64 (exit 0, 19.3 s, 0 errors)

| Item | Receipt |
|---|---|
| Build | `make -j2`, exit 0, wall 19.319 s (user 13.0 s), `grep -ci "error:"` = 0 (`logs/spike-build-ios.log`, full) |
| Archives | `libavcodec.a` 677,720 B + `libavutil.a` 926,952 B + `libswscale.a` 895,632 B = 2,500,304 B logical (preserved: `W/libs-ios/`) |
| Arch | `lipo -info`: all three `Non-fat file ... architecture: arm64`; `libavcodec/mpeg12dec.o: Mach-O 64-bit object arm64` |
| Symbols | 49 global `T _avcodec*`; `_ff_mpeg2video_decoder` DEFINED; `_ff_mpegvideo_parser` DEFINED (`logs/ios-libs.txt`) |
| `W` after build | 9.2 GB (92% of cap — ~700 one-cluster files added). No cap breach; tree removed after (§disposition) |

### Spike: link for iOS arm64 (exit 0, bare — zero frameworks)

| Item | Receipt |
|---|---|
| Smoke link | `xcrun -sdk iphoneos clang -arch arm64 -mios-version-min=17.0 -Os -Wl,-dead_strip` + 3 archives, NO `-framework`, NO extra libs: exit 0 → Mach-O 64-bit executable arm64, 1,117,048 B (`logs/i22-linktest.c`) |
| Full-surface link | Same bare command referencing ALL 20 FFmpeg APIs `MPEG.cpp` uses (`find_decoder/parser_init/alloc_context3/frame_alloc/packet_alloc/open2/parser_parse2(x2 incl. NULL-flush)/new_packet/send_packet(x2 incl. NULL)/receive_frame/packet_unref/frame_unref/sws_getContext/sws_scale/sws_freeContext/strerror/av_log/frame_free/packet_free/free_context/parser_close`): exit 0 → Mach-O arm64, 1,258,152 B (`logs/i22-linkfull.c`) |
| Baseline | Empty `main`: 32,944 B file, `__TEXT` 32,768 B. Smoke `__TEXT` 983,040 B. Deltas: smoke ≈1.08 MB file / 950 KB `__TEXT`; full-surface ≈1.23 MB file |
| Size impact | 1.23 MB ≈ 1.0% of the I21 app binary (121,249,160 B). Dead-stripped; the `.a` logical sum (2.5 MB) is the ceiling, not the cost |
| U-symbol audit | 732 undefined refs across the 3 archives (`logs/i22-undef.txt`). CF/CM/CV/VideoToolbox refs EXIST but are confined to `hwcontext_videotoolbox.o`, which the decoder/parser/sws path does NOT pull (bare-link exit 0 is the proof). First audit attempt used a broken `nm -u | grep " U "` pipeline (reported 0 — INVALID, tabled); corrected with plain `nm`. Fallbacks if the app link ever pulls it: `--disable-videotoolbox`, or link CoreFoundation+CoreVideo+VideoToolbox (all on-iOS, zero cost) |
| NOT proven | On-device EXECUTION (no install/probe this brief by rule) and in-app link (no integration by rule). Proven: arch-correct static libs + bare link of the exact API surface |

### Spike: subset sufficiency (same subset rebuilt for host, decodes E18's vector)

Same flags, `--cc=clang`, host arch: configure exit 0, `make -j2` exit 0, 19.0 s (`logs/spike-configure-host.log`, `logs/spike-build-host.log`; host link needed `-framework CoreFoundation -framework CoreVideo -framework VideoToolbox` — darwin-autodetect delta vs the bare iOS link, tabled). Probe `logs/i22-decode.c` mirrors `MPEG.cpp` feed/receive/convert/flush against `local/research/E18/regression-frames.m2v` (240 B, sha `25c353b5…`).

| Run | Receipt |
|---|---|
| A (feed + codec drain, no parser flush) | `in=240 parsed=240 packets=3 frames=3 rgba=3072`, exit 0. Pre-drain newFrames=2 = E18 R3's `newFrames=2` EXACTLY (`logs/decode-runs.log`) |
| B1 (parser flush added, mirrors `MPEG.cpp` `flush()`) | exit=139 SIGSEGV, no stdout. SINGLE occurrence — 1 of 7 runs; never reproduced (below). Tabled as observation, NOT a library verdict |
| B2 (same binary under lldb) + B3–B7 (5× direct) | `in=240 parsed=240 packets=4 frames=4 rgba=4096`, exit 0, ×6 identical. Counts match E18's full-9.0.1 receipts exactly (R3: parsed240/packets3/newFrames2 pre-flush; CLI provenance: 4 frames post-flush) |
| Pixel bytes | Probe sha `0a8d7973…` vs E18 CLI sha `a2256d49…`: 1024/4096 bytes differ — R channel 252 vs 254 (G=B=0, A=255 identical). CLI re-run REPRODUCED E18's sha (receipt in `logs/rgba-compare.txt`); CLI + `-sws_flags bilinear` STILL yields 254 → drift is 7.1-vs-9.0 swscale ROUNDING, not scaler flags (`logs/rgba-compare.txt`) |
| Sufficiency standing | COUNTS and SHAPES identical (packets/frames/dims/RGBA); PIXELS drift ±2 LSB across FFmpeg major versions. `MPEG.cpp` pins `SWS_BILINEAR`, so the flag side is already deterministic — version pinning is the follow-up's byte-parity lever |

### Spike: licenses touched

| Item | Receipt |
|---|---|
| FFmpeg subset | LGPL-2.1-or-later (`License: LGPL version 2.1 or later`, configure log). Components: native `mpeg2video` decoder (LGPL) + `mpegvideo` parser (LGPL) + libswscale (LGPL) + libavutil (LGPL). No GPL: no `--enable-gpl`, no x264/x265 (present in brew but NOT in this build), no external libs at all |
| Compliance row (fact, not advice) | Static LGPL into an App-Store-distributed binary carries the LGPL's relink/provision obligations (object files / written offer + license notice). Dynamic linking or `--disable-*` alternatives do not change LGPL-ness of THESE libs; they change only size. The follow-up owns the compliance decision |
| Other licenses | None touched (no new vendored code; spike consumed only the FFmpeg tarball + SDK headers) |

### Spike: disposition (tabled per brief)

| Item | Receipt |
|---|---|
| Removed | Extracted `ffmpeg-7.1.1/` tree (~8.5 GB allocated) — reproducible in ~5 min from the tarball + this report's recipe (re-verify cost: 1 configure + 19 s build) |
| Kept | `W/spike/ffmpeg-7.1.1.tar.xz` (11 MB, sha above) + `W/libs-ios/` (3 arm64 `.a`, 2.5 MB logical) + `W/logs/` (all configure/build logs + link sources). Final `W` = 31 MB |
| Cause | The follow-up needs the RECIPE (in REPORT + evidence) and the built ARCHIVES (kept), not the tree. Nothing kept inside any repo |

### Stub inventory (static + I21 probe receipts; no code changes)

Line numbers are `MPEG.cpp` @`3adc0478`. The brief's `:447-469` / `:1107-1114` were approximate — exact lines measured below (table the correction, keep both).

| # | Entry point | Exact lines | What it does today (FFmpeg-OFF) |
|---|---|---|---|
| S1 | Stub `MpegFfmpegDecoder::feed` | :451-463 (class :449-472) | Ignores all input; fires the ungated `[MPEG] runtime built without FFmpeg...` warning ONCE (`static bool`); returns `false` ALWAYS. I21 probe: warning ×1 @line 15163 = `feed()` ENTERED, bytes reached the stub |
| S2 | Stub `flush` / `reset` | :465-470 | `flush` returns `true` (no-op); `reset` empty. No frames ever appended to `decodedFrames` |
| S3 | Retry-later path | :1126-1133 (inside `feedElementaryStream` :1041-1137) | `if (!decoder->feed(...))`: `decoder.reset()` + `waitingForVideoSequenceHeader=true` + `videoSequenceSyncBuffer.clear()` + `decoderFailed=false`, then `return` — SILENT retry (no wake, no error, no EOF). Brief's `:1107-1114` is the adjacent sequence-header-sync RESET block (:1107-1113: re-arm timing, `decodedFrames.clear()`), not the retry itself |
| S4 | Gating macro | `MPEG.cpp:6-7` (`PS2X_HAS_FFMPEG` defaults 1) + `ps2xRuntime/CMakeLists.txt:453` (`PS2X_HAS_FFMPEG=$<BOOL:${PS2X_ENABLE_FFMPEG}>`); iOS default OFF (`CMakeLists:271-272`); device cache line `PS2X_ENABLE_FFMPEG=OFF` (I21 receipt) | The #else branch (:449) selects the stub at COMPILE time — a stub-completion change edits the stub branch with zero CMake movement; an FFmpeg-build change flips the option + provides iOS libs |

| # | `getMpegPicture` wait-condition term | Lines | Value on device today (I21) |
|---|---|---|---|
| W1 | `playback.decodedFrames.empty()` | :2498 (+ input gate :2467) | TRUE forever — stub enqueues nothing |
| W2 | `!g_mpeg_stub_state.currentCdStreamEofSeen` | :2499 (+ :2468) | TRUE — guest never enters streaming EOF (`sceCdSt` ×0, I21) |
| W3 | `!playback.streamEnded` | :2500 (+ :2468) | TRUE — nothing sets it on this path (set only :1303/:1459 stream/EOF paths) |
| W4 | `!playback.decoderFailed` | :2501 (+ :2468) | TRUE — retry path RESETS it to false (:1131); stub never fails loudly |
| W5 | Consequence | :2503-2526 | All-true → `waitExternal(EeWaitReason::Mpeg, kMpegPictureWaitType=1, mpegAddr)` → main parked at `0x3b1028` (I21: `waitReason=6 waitId=0` all 5 blocks). ANY term flipping wakes: non-empty queue, EOF-seen, streamEnded, or decoderFailed |

| # | Completion-shaped touch set (file/function) | Why |
|---|---|---|
| T1 | `MPEG.cpp` stub `feed` (:451-463) | Must return `true` AND append ≥1 `MpegDecodedFrame` (:31-38: `width/height/repeatPict/pts90k/rgba`) for the wait to break via W1 |
| T2 | `feedElementaryStream` retry path (:1126-1133) | A `true`-returning stub SKIPS this path (no reset/re-arm) — verify no other caller depends on the reset side effects |
| T3 | `sceMpegAddBs` wake (:2053-2059) | ALREADY wakes on `decodedFrames.size() != framesBefore` — a completing stub inherits the wake with ZERO edits here (same for `sceMpegFlush` :2017-2024) |
| T4 | `getMpegPicture` serve path (:2528-2586) + guest write (:2595-2621) | Consumes `decodedFrames.front()` + `writeDecodedFrameToGuest` (:1834+) + vsync-presentation gating (:2536-2562) — shared with the FFmpeg-ON path, no stub-specific edits expected; `frameCount`/`picturesServed` advance here |
| T5 | Presentation/timing state (`MpegPlaybackState` :490-518) | `nextPictureTickQ32`/`pictureIntervalQ32`/`firstPresentedPts90k` gate pacing; a stub frame with `pts90k=-1` takes the default-interval branch — table, don't assume |
| T6 | `writeBlankMpegFrame` (:1798-1832) | frameCount==0 no-frame fallback (align16 macroblock strips, RGBA 0,0,0,0x80) — UNTOUCHED by completion (still the haveFrame=false path :2618-2621) |
| T7 | Tests `ps2xTest/src/ps2_runtime_expansion_tests.cpp` | R3-pattern regression (E18 +284) is the template: authored-bytes → AddBs → FRAME assertion. New vectors tabled below |
| T8 | NOT touched | Scheduler, main, CSV/generated, semaphores, CD/ISO path, CMake (stub shape needs no build changes), `MPEG.h` (37 lines, no decoder decls) |

| # | Test vector that would prove a completion | Source / status |
|---|---|---|
| V1 | `regression-frames.m2v` (240 B, 4 red 16×16 I-frames, sha `25c353b5…`) | COMMITTED `local/research/E18/` — host R3's vector; counts known (parsed240/packets3/newFrames2). A device FFmpeg build must reproduce §sufficiency counts |
| V2 | First64 title bytes + FNV64 `0xd2a9588f0e0fd358` | COMMITTED (`logs/first64-title.txt` ← E18 `e18a-mpeg.json:409`) — header-shape check ONLY; E18 limit: full 5040 B NOT retained, no standalone replay |
| V3 | Full 5040 B title payload | NOT retained anywhere (E18 explicit limit) — needs a fresh guarded host probe (E-lane's lane, NOT this brief) to capture; required for a title-faithful device vector |
| V4 | Authored larger-frame vectors (e.g. 320×240 / title-guess dims, P/B-frames, seq-end) | NOT authored — title movie dims are UNKNOWN (host never decoded one; stub default 320×240 is a guess). Needed to prove non-16×16 + multi-type + flush paths |
| V5 | On-device observable | I21 tap set: `[MPEG:GetPicture:FRAME]` (AGRESSIVE-gated — needs a gated-tap brief to observe), `0x3b1028` advance, `[diag:frame]` counters unfreezing, screen non-black. None observable with today's taps except indirectly |

## Task 2 — parity checklist + recommendation

### Host-parity checklist (from committed E18 evidence, read-only — no host runs)

"Host FFmpeg-ON path produces X" → "device decoder must satisfy Y". E18's host ran brew FFmpeg 9.0.1 (`ffmpeg 9.0.1_1`, Cellar date Sep 8 — predates E18; `libavcodec 63.1.101`); this spike built 7.1.1 (§sufficiency drift applies to every pixel row).

| # | Host receipt (E18) | Device parity bar | Source |
|---|---|---|---|
| P1 | R3 feed counters: `inSize=240 parsed=240 packets=3 newFrames=2 totalFrames=2` | SAME counters for the SAME 240 B vector (V1). Minimal-7.1.1 already reproduces them host-side (§sufficiency run A) | `logs/r3-receipt.txt` ← `r1-r6-results.txt:8-11` |
| P2 | R3 serve: `[MPEG:GetPicture:FRAME] ... frame=0 queued=1 size=16x16`, caller resumed ONCE with rc0, guest image NONZERO | Frame served with matching size/queue/frameCount; resume-once; guest image bytes nonzero (not the blank-strip pattern) | E18 REPORT R3 row + `r1-r6-results.txt` |
| P3 | Title input accepted: 5040 requested = 5040 returned, FNV64 `0xd2a9588f0e0fd358`, first4 `000001b3` | Device AddBs must accept the full count (return = requested) for title-shaped input; first64 header-shape check (V2) | `logs/first64-title.txt` ← `e18a-mpeg.json` mpeg-input id 10 |
| P4 | Host parser HOLDS title bytes: `parsed=5040 packets=0 newFrames=0 totalFrames=0 decoderFailed=0` (E-lane's wall) | NOT a match-target — the device bar is FRAMES from title bytes once the E-lane resolves further-input (V3 vector needed). Device must NOT reproduce the hold; it must reproduce the eventual R3-shape output for V3 | E18 NEXT-BRIEF edge row (separation preserved) |
| P5 | No-input semantics (R4): callback v0 ∈ {0, 1, 0xffffffff} with NO AddBs → callback once, NO resume, typed MPEG wait retained, data released | Identical: v0 discarded, no fabricated wake. A stub-completion MUST NOT wake on empty input (E18 scope constraint carries) | E18 REPORT R4 row |
| P6 | AddBs re-entry (R2): delivered callback re-entered AddBs, copied 16 B, returned WITHOUT deadlock; no frame → typed wait retained | Same re-entrancy (MPEG mutex recursive-safe path); partial/short input must not wedge | E18 REPORT R2 row |
| P7 | EOS-without-header (E15 input): 16 EOS bytes, no sequence header → NO frame, still waits | Device must hold (not fail, not wake) on headerless input; `waitingForVideoSequenceHeader` stays armed | E18 REPORT E15-input row |
| P8 | Guest frame layout: `writeDecodedFrameToGuest` align16 macroblock strips (RGBA), `frameCount`/`picturesServed` advance, vsync-presentation gating (`waitVSync` when early) | Byte-layout parity for served frames (modulo the ±2 LSB scaler drift until versions pin); pacing: no frame served before its presentation tick | `MPEG.cpp` :1834+/:2528-2586 (shared path — both shapes inherit it) |
| P9 | Flush/IsEnd: `sceMpegFlush` drains parser+codec and wakes on new frames; IsEnd true only when ended + queue empty + presentation complete | Same drain-then-wake; no premature end. Parser-flush is REQUIRED for the last frame (run A vs B: 3 vs 4 frames — measured) | `MPEG.cpp` :2004-2026/:2675-2699 + §sufficiency |
| P10 | Pixel tolerance | ±2 LSB on the R channel (7.1-vs-9.0 rounding, version-not-flags) is the MEASURED cross-version drift. Byte-exact host/device parity needs the SAME FFmpeg version both sides (7.1.1 for iOS + pin host to 7.1.x, or build 9.0.x for iOS — unspiked) | `logs/rgba-compare.txt` |

### Recommendation row (shapes + costs/risks + follow-up consumption — decision left to the follow-up)

| Shape | What it is | Cost receipts (this brief) | Risk receipts (this brief) | Follow-up consumes |
|---|---|---|---|---|
| A. FFmpeg-build | Build the minimal subset for iOS (this spike's recipe), wire 3 archives into CMake for the iOS target, flip `PS2X_ENABLE_FFMPEG` ON for device | Build: 19 s, zero errors; link: bare exit 0; size +1.2 MB (~1%); CMake touch: iOS branch for 3 IMPORTED libs + include dir (≈40 lines by the WIN32-block template :282-376); host tests already green on the SAME code path (R1–R6, 458/458) | LGPL-2.1 static-link obligations (rel provision — the only NEW legal surface); version pin (7.1.1 vs 9.0.1 pixel drift — measured); in-app link + on-device execution UNPROVEN (spike boundary); one-off SIGSEGV 1/7 in the host probe harness (unroot-caused, harness-side) | Recipe + archives (`W/libs-ios/`) + U-audit + P1–P10 checklist + V1 vector (immediate device-vector); V3 capture request to the E-lane |
| B. Stub-completion | Complete the FFmpeg-OFF stub: `feed` returns `true` + enqueues authored/decoded `MpegDecodedFrame`s (T1–T5), no FFmpeg anywhere | Zero build movement (no CMake, no libs, no license change); touch set ≈1 function + tests (T7); wake path already wired (T3) | Fabricated-frame risk (E18 scope constraint FORBIDS fabricated frames/EOF — a stub frame for TITLE bytes must come from a REAL decode or an explicitly-sanctioned authored shape, else it violates the E-lane's carried constraint); title dims/pacing UNKNOWN (V4 un-authored); still needs a REAL MPEG-1/2 decode core from somewhere (a hand-rolled decoder >> FFmpeg-subset cost) OR an acknowledged placeholder semantic | S1–S4/W1–W5/T1–T8 inventory + V1–V5 vectors; the E18 "no fabricated frame" constraint as the design gate |
| C. Hybrid | FFmpeg-build for the decode core (shape A) + stub-branch completion ONLY as a degraded fallback (e.g. headerless-input hold already exists; explicit `decoderFailed` wake instead of silent retry) | A-costs + a SMALL stub-branch edit (S3 retry → loud-fail option). Smallest total delta that keeps every path honest | Same as A + one semantic decision: what `decoderFailed=true` MEANS to the guest (error return vs wait-forever — needs E-lane concurrence; today NOTHING sets it loudly on this path) | Both columns above + the W4 row (the retry path currently guarantees `decoderFailed` never fires) |

What the table does NOT do: pick a shape. The facts that would pick it — LGPL posture (owner call), E-lane concurrence on stub semantics (their lane), V3 capture (their probe) — are all outside this brief's authority.

### Handoff: the exact first question the Cause-B implementation brief answers

> **Given I22's receipts (minimal FFmpeg 7.1.1 subset builds+links bare for iOS arm64 at +1.2 MB LGPL-2.1; stub touch set T1–T8 with the wake already wired; parity bars P1–P10; title dims + full 5040 B payload still unknown), which Cause-B shape does the owner authorize — A (FFmpeg-build), B (stub-completion within E18's no-fabrication constraint), or C (hybrid) — and, for A/C, which FFmpeg version is pinned for byte-parity (7.1.x both sides, or spike 9.0.x for iOS)?**

| # | Item | Disposition |
|---|---|---|
| H1 | This feasibility (spike recipe + archives + inventory + checklist + recommendation) | CONSUMED by the Cause-B implementation brief (its Q1 is quoted above) |
| H2 | E18's host parser-output dependency (5040 B in, 0 packets out) | STAYS E-lane (their E20+ line per the E18 NEXT-BRIEF; never conflated with the device wall) |
| H3 | `W/libs-ios/` (3 arm64 `.a`) + `W/spike/ffmpeg-7.1.1.tar.xz` + `W/logs/` (31 MB total) | STAYS on SSD for the follow-up (re-verify cost without them: ~5 min rebuild) |
| H4 | I21 device baseline (installed build, PID 4679 running, steady-state + census) | STAYS — the next re-probe diffs against it; I22 moved nothing on-device |
| H5 | E-lane fork ownership + remote moves | E-lane ONLY — I22 moved nothing (remote `3adc0478` at recon; 0 pushes) |

## Exact commands

```sh
# --- Recon (E-lane live; read-only) ---
FORK="/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp"; W="/Volumes/Extreme SSD/ps2x-i22"
git -C "$FORK" log --oneline -5                       # 3adc047 [E18] at top
git -C "$FORK" ls-remote fork ssx3                    # 3adc0478b6d2260acdd28a249466f2eef9a20176 (recon)
git -C "$FORK" show 3adc0478:ps2xRuntime/src/lib/Kernel/Stubs/MPEG.cpp > /tmp/i22-mpeg.cpp  # 2784 lines
git -C "$FORK" grep -n "PS2X_HAS_FFMPEG" 3adc0478 | grep -v MPEG.cpp   # CMakeLists:453 only
git -C "$FORK" grep -ln "libavcodec|libswscale|PS2X_HAS_FFMPEG" 3adc0478  # MPEG.cpp + CMake + workflow + vita
P="00008112-001224302184A01E"
xcrun devicectl list devices --timeout 30              # iPad connected
xcrun devicectl device info apps --device "$P" --timeout 60 | grep -iE "ps2|MF1"
xcrun devicectl device info processes --device "$P" --timeout 60 | grep -i ps2  # PID 4679, I21 UUID
diskutil info "/Volumes/Extreme SSD" | grep -iE "block size|allocation"  # 1 MB clusters
# --- Spike fetch ---
export COPYFILE_DISABLE=1; mkdir -p "$W/spike" "$W/logs" local/research/I22/logs
cd "$W/spike" && curl -sSL -o ffmpeg-7.1.1.tar.xz https://ffmpeg.org/releases/ffmpeg-7.1.1.tar.xz --max-time 240
shasum -a 256 ffmpeg-7.1.1.tar.xz                     # 73398439...
tar -xf ffmpeg-7.1.1.tar.xz; find ffmpeg-7.1.1 -name "._*" -delete
# --- Spike configure (iOS arm64) ---
cd "$W/spike/ffmpeg-7.1.1"; SDK=$(xcrun --sdk iphoneos --show-sdk-path)
./configure --target-os=darwin --arch=aarch64 --cpu=generic --enable-cross-compile \
  --cc="xcrun -sdk iphoneos clang" --sysroot="$SDK" \
  --extra-cflags="-arch arm64 -mios-version-min=17.0 -isysroot $SDK -Os" \
  --extra-ldflags="-arch arm64 -mios-version-min=17.0 -isysroot $SDK" \
  --disable-everything --disable-programs --disable-doc --disable-avdevice --disable-avfilter \
  --disable-avformat --disable-swresample --disable-network --disable-iconv --disable-bzlib \
  --disable-lzma --disable-zlib --enable-decoder=mpeg2video --enable-parser=mpegvideo \
  --enable-swscale --disable-asm --enable-static --disable-shared --disable-debug \
  --prefix="$W/spike/install" > "$W/logs/configure2.log" 2>&1   # exit 0
make -j2 > "$W/logs/build2.log" 2>&1                  # exit 0, 19.3 s
lipo -info libavcodec/libavcodec.a libavutil/libavutil.a libswscale/libswscale.a  # arm64 x3
mkdir -p "$W/libs-ios" && cp libavcodec/libavcodec.a libavutil/libavutil.a \
  libswscale/libswscale.a "$W/libs-ios/"; find "$W" -name "._*" -delete
# --- Spike link (bare; full surface) ---
xcrun -sdk iphoneos clang -arch arm64 -mios-version-min=17.0 -isysroot "$SDK" \
  -I"$W/spike/ffmpeg-7.1.1" -Os -Wl,-dead_strip /tmp/i22-linkfull.c \
  "$W/libs-ios/libavcodec.a" "$W/libs-ios/libswscale.a" "$W/libs-ios/libavutil.a" \
  -o /tmp/i22-linkfull                             # exit 0, Mach-O arm64, 1258152 B
nm "$W/libs-ios/libavcodec.a" "$W/libs-ios/libavutil.a" "$W/libs-ios/libswscale.a" \
  | grep -E "^ +U " | sort -u > /tmp/i22-undef.txt  # 732 lines
# --- Spike sufficiency (host subset + decode probe) ---
make distclean; ./configure --cc=clang --extra-cflags="-arch arm64 -Os" \
  --extra-ldflags="-arch arm64" --disable-everything --disable-programs --disable-doc \
  --disable-avdevice --disable-avfilter --disable-avformat --disable-swresample --disable-network \
  --disable-iconv --disable-bzlib --disable-lzma --disable-zlib --enable-decoder=mpeg2video \
  --enable-parser=mpegvideo --enable-swscale --disable-asm --enable-static --disable-shared \
  --disable-debug > "$W/logs/configure-host.log" 2>&1  # exit 0
make -j2 > "$W/logs/build-host.log" 2>&1              # exit 0, 19.0 s
clang -arch arm64 -Os -I"$W/spike/ffmpeg-7.1.1" /tmp/i22-decode.c libavcodec/libavcodec.a \
  libswscale/libswscale.a libavutil/libavutil.a -framework CoreFoundation -framework CoreVideo \
  -framework VideoToolbox -o /tmp/i22-decode       # exit 0
/tmp/i22-decode local/research/E18/regression-frames.m2v /tmp/i22-rgba.bin  # counts + sha
/opt/homebrew/bin/ffmpeg -hide_banner -loglevel error -i local/research/E18/regression-frames.m2v \
  -f rawvideo -pix_fmt rgba /tmp/i22-cli-rgba.bin   # reproduces E18 sha a2256d49
# --- Disposition + evidence ---
rm -rf "$W/spike/ffmpeg-7.1.1"; du -sh "$W"          # 9.2G -> 31M
find local/research/I22 -name "._*" -delete; du -sh local/research/I22/logs  # 112K
```

## New gap rows (each with the exact next brief it needs)

| # | Gap | Proving line | Exact next brief needed |
|---|---|---|---|
| G1 | Cause-B shape UNDECIDED (A/B/C tabled, none picked) | §recommendation (decision needs LGPL posture + E-lane concurrence — outside I22 authority) | The Cause-B implementation brief (its Q1 is quoted in §handoff) |
| G2 | In-app link + on-device execution unproven | §spike-link NOT-proven row (bare link of the exact API surface is proven; app integration was out of scope by rule) | Same Cause-B brief (first build+probe after integration) |
| G3 | FFmpeg version unpinned (7.1.1 spiked; host is 9.0.1; ±2 LSB drift measured) | `logs/rgba-compare.txt` (version-not-flags) | Same Cause-B brief (pin 7.1.x both sides, or spike 9.0.x for iOS first) |
| G4 | Full 5040 B title payload + title movie dims UNKNOWN | V3/V4 rows (E18 explicit limit; stub 320×240 is a guess) | E-lane guarded host probe (their lane/lease) to capture V3; V4 authoring rides with it |
| G5 | One-off SIGSEGV 1/7 in the host decode harness (B1) | `logs/decode-runs.log` (6/6 clean after, incl. lldb; harness-side, unroot-caused) | Informational — re-observe if the follow-up reuses the harness; no brief unless it reproduces under the app |
| G6 | `decoderFailed` can never fire loudly on this path (retry resets it) | W4 row (:1131) | Fold into the Cause-B brief IFF shape B/C touches S3 (needs E-lane concurrence on guest-visible meaning) |
| G7 | I21 build still installed AND running (PID 4679); I22 moved nothing | `logs/ipad-prestate.txt` (7th brief with a relaunched occupant) | No brief — next re-probe's pre-state re-checks; overwrite-install precedent (11×) covers replace |

## Receipt paths

- `local/research/I22/REPORT.md` (this file)
- `local/research/I22/logs/spike-configure-ios.log` (full) + `spike-build-ios.log` (full, exit 0, 19.3 s, 0 errors)
- `local/research/I22/logs/spike-configure-host.log` + `spike-build-host.log` (full, exit 0, 19.0 s)
- `local/research/I22/logs/spike-failed-make-partial-tree.log` (the 2 failed makes on the incomplete tree — race receipt)
- `local/research/I22/logs/i22-linktest.c` (smoke) + `i22-linkfull.c` (20-API full surface) + `i22-baseline.c` + `i22-decode.c` (sufficiency probe)
- `local/research/I22/logs/decode-runs.log` (transcribed runs A/B1/B2–B7) + `rgba-compare.txt` (252-vs-254 + bilinear control)
- `local/research/I22/logs/i22-undef.txt` (732-line U-symbol audit) + `ios-libs.txt` (sizes/arch/link receipts)
- `local/research/I22/logs/fork-pin.txt` + `ipad-prestate.txt` + `r3-receipt.txt` + `first64-title.txt`
- `W/libs-ios/` (3 arm64 `.a`, 2.5 MB) + `W/spike/ffmpeg-7.1.1.tar.xz` (11 MB, sha `73398439…`) + `W/logs/` (all raw logs); final `W` = 31 MB
- No fork push this brief (nothing to push — zero fork commits by design)

## What I could not do

- Pick a Cause-B shape — LGPL posture is an owner call, stub semantics need E-lane concurrence (G1; the handoff Q1 is quoted, not answered).
- Prove in-app link or on-device execution — integration + install/probe were out of scope by rule (G2; arch-correct libs + bare full-surface link are proven).
- Pin the FFmpeg version — 7.1.1 spiked, host is 9.0.1, drift measured but the pin is the follow-up's (G3).
- Produce a title-faithful device vector — full 5040 B payload was never retained and title dims are unknown (G4; E-lane capture needed).
- Root-cause the single SIGSEGV — 1 of 7 harness runs, never reproduced, harness-side by elimination (G5).
- Make `decoderFailed` fire — the retry path guarantees it never does on this input shape (G6; semantic change needs E-lane concurrence).
- Observe device-side decode counters — today's taps gate `[MPEG:*]` under AGRESSIVE; the I21 build stays installed for the next re-probe (V5).
- Re-verify the iOS archives from a fresh tree — the extracted tree was removed per the disposition rule (re-verify cost ~5 min from the kept tarball + recipe).
- Explain PID 4679's launcher — the I21 bundle was running though I21 signaled only its own probe PID at cleanup (7th brief running with a relaunched occupant, G7).
- Touch the E-lane, the fork remote, or the device state — read-only by rule (0 pushes; app fate: installed + running, untouched).

## TAIL RECEIPT

Report written in 5 chunks (header + contract + caps; Task 1 spike log + stub inventory; Task 2 checklist + recommendation + handoff; commands + gaps + receipts + could-not-do; this receipt). Pre-receipt measure: 286 lines total, sha256 `bec7b7cb54e3910a8e6f0ca8f713dea80a98b090e1658f9e720a6545b5409e47` over lines 1–286 (everything before this `## TAIL RECEIPT` section).
Tail content line: "Touch the E-lane, the fork remote, or the device state — read-only by rule (0 pushes; app fate: installed + running, untouched)." This receipt line ends the report. END-I22-REPORT.
