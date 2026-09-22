# I23 — Cause-B shape A (owner-authorized): minimal FFmpeg 7.1.1 for iOS, integrated + proven on device vs P1–P10

- Date: 2026-09-21. Tables, no verdicts.
- `local/research/I22/REPORT.md` read first (all of it: spike recipe + archives + stub inventory S1–S4/W1–W5/T1–T8 + parity P1–P10 + V1–V5 + sufficiency counts + 252-vs-254 drift + H1–H5 handoff).
- `local/research/I21/REPORT.md` read (all of it: build/install/probe shape reused — worktree + ports + wiring + C17 reuse + overwrite-install + 90 s probe + steady-state/census baselines). `local/research/E18/REPORT.md` + `r1-r6-results.txt` + `regression-frame-provenance.json` read (R3 receipts: feedES size=240 first4=000001b3, feed parsed240/packets3/newFrames2, FRAME 16x16, resumed=1 rc0 pixel!=0; V1 240 B sha `25c353b5…`, brew-9.0.1 RGBA sha `a2256d49…`).
- Authorized decision (owner, via this brief — not re-litigated): shape A (FFmpeg-build); pin 7.1.x BOTH sides (device 7.1.1 now + host parity vs locally-built 7.1.1; shared host/brew/CI pin tabled for E-lane concurrence, untouched); LGPL-2.1 static-link obligations accepted (I22 §licenses is fact; notice shipped + relink-provision pointer tabled, no legal interpretation).
- Target: Brad's iPad, iPad Air 11-inch (M2) (`iPad14,9`), UDID `P` — pre-state = I22's baseline exactly (I21 install UUID `AAA5E829-…` still installed AND running, PID 4679, 8th brief with a relaunched occupant; untouched until the authorized overwrite-install).
- BASE: `3adc0478` (E18 BEHAVIOR — verified by `ls-remote` at recon AND end; E-lane advanced 0 during I23; PINNED regardless with cause: the I21 receipts this brief diffs against were taken there).
- Product: fork branch `i23-ffmpeg-ios` (5 commits: CMake iOS block + iOS-default-ON + env-gated V1 diagnostic + LGPL notice + env-gated feed trace; pushed, no force-push; `fork/ssx3` unmoved) + device Release REBUILD at branch+4 local ports (C17 game objects reused read-only, lib byte-identical) + OVERWRITE reinstall (12th) + probes with `PS2X_MPEG_VECTOR_PATH` (V1, then V4) + host-7.1.1 parity anchors + P1–P10 row-by-row table.
- Rules honored: branch `i23-ffmpeg-ios` ONLY, zero commits to `ssx3`; E-lane pane never prompted/steered (V3 request tabled for the orchestrator); rebuild/reinstall/probe AUTHORIZED this brief; no PS2 boots → no lease; no `adb`; every device-scoped `devicectl` with explicit `--timeout`; `export COPYFILE_DISABLE=1` on SSD steps + `._*` purges (before staging + evidence); byte caps declared up front + tracked (FFmpeg prefixes rebuilt on `/tmp` APFS, peak 121M, tree removed; SSD prefixes kept); evidence `local/research/I23/` standalone, `[I23]` commit, no push.
- Outcome shape: H-d — INTEGRATED + PROVEN: the 7.1.1 subset links in-app (+1.15MB) and executes on device; V1 yields P1 field-exact + 4 frames byte-exact vs host-7.1.1 (retrieved bytes, cmp clean); V4 likewise at 320×240; the title holds (parsed5040/packets0) in exact host agreement with main still parked — the remaining wall is the title input shape (V3), not the decoder.

Path shorthands: `W` = `/Volumes/Extreme SSD/ps2x-i23/`, `WT` = `W/fork-wt` (detached @branch+4 locals), `C17` = `/Volumes/Extreme SSD/ps2x-i17/codegen-output/` (reused read-only; NO `W/codegen-output/`), `P` = iPad UDID `00008112-001224302184A01E`, `FORK` = shared clone (branch ref added + pushed; checkout untouched), `V1` = `local/research/E18/regression-frames.m2v` (240 B), `V4` = `logs/i23-v4.m2v` (3442 B, authored this brief).

## Experiment contract

| Item | Content |
|---|---|
| Hypothesis H | The device build with the minimal 7.1.1 subset linked and `PS2X_ENABLE_FFMPEG=ON` reproduces host FFmpeg-ON decode behavior: the V1 vector yields P1 counters (parsed240/packets3+1/frames2+2) and P2 frames (16x16, nonzero, byte-exact vs host 7.1.1) through the REAL `MpegFfmpegDecoder` class, and title-path `[MPEG:*]` taps show device/host agreement for the same input |
| Observable | Branch diff (4 commits + push receipts); FFmpeg prefix builds (exits + arch + symbol identity vs I22); device build (exits/errors/size delta vs I21); probe consoles (vector lines, `[MPEG:feed/FRAME]` taps, wait advance or researched hold, screenshot, steady-state + census diffs); host-7.1.1 anchors (7× runs + RGBA digests); P1–P10 row table with receipts |
| Alternatives | H-a full parity on every measurable row (observed TBD). H-b integration fails to build/link (exact errors tabled, spike ends at the 6 h cap regardless). H-c vector mismatch (device counts/bytes differ from host 7.1.1 — both sides tabled, no smoothing). H-d title still parked with 0 frames while V1 decodes (host-agreeing hold — tabled as parity-with-host-hold; V3 capture still needed, not conflated) |
| Stop | All bars tabled, or any cap (6 h / SSD / evidence / /tmp), or any FORK/E-lane conflict (none encountered). Contract outcome: H-d on every row — vectors decode byte-exact, title holds host-agreeing |
| Time box | 6 h (used ~2 h wall: recon ~25 min → prefixes ~10 min → branch ~20 min → builds ~30 min → install/probes ~15 min → analysis/evidence/report ~30 min) |
| V1-host anchor | Fresh host-7.1.1 prefix + I22's `i22-decode.c` VERBATIM (7× runs, exit 0, `in=240 parsed=240 packets=4 frames=4 rgba=4096`, RGBA sha `0a8d7973…` = I22's byte-exact; feed/drain split 2+2 from per-frame lines). Full host-suite rebuild against 7.1.1 NOT run (would touch shared config — explicitly out of scope; counts are version-independent per I22 §sufficiency, and the class source is identical both sides) |

## Caps (declared up front, tracked)

| Cap | Declared | Used | Receipt |
|---|---|---|---|
| `W` SSD allocated bytes (ExFAT) | ≤ 14 GB | 9.6 GB (69%) — prefixes 165M+165M (3.7M+3.7M logical) + WT 383M + build tree 5.5G + signed app 2.9G + logs 421M (incl. aggressive binary + 2 full consoles) | `du -sh W` after evidence step |
| `/tmp` transient (APFS) | ≤ 2 GB | PEAK 121M (extract+build), final 1.4M (probe + scripts; tree removed) | `du -sh` before/after `rm -rf` |
| Evidence `local/research/I23/` | ≤ 5 MB | 4.0 MB logs + REPORT, 41 files + REPORT | `du -sh` + file count |
| Screenshots committed | 1 | 1 (`i23-shot1.png`, 2.0 MB, black content viewed) | logs dir |
| Build parallelism | `-j2` / `-jobs 2` max | `-j2` everywhere (both FFmpeg builds + device build) | exact commands + build logs |
| Fork writes | branch `i23-ffmpeg-ios` ONLY (push, no force-push); zero commits to `ssx3` | 5 branch commits pushed (C1–C5), 4 local port commits unpushed, remote `ssx3` at `3adc0478` recon AND end | §Task 1 + `ls-remote` |
| Device ops | rebuild + reinstall + probes (AUTHORIZED) | 2 builds (1 rejected aggressive + 1 final) + 1 install (exit 0, 12th overwrite) + 2 probes (V1 PID 4777 + V4 PID 4778, both exit 2 alive, both cleaned) + 1 screenshot + 2 crashlog checks (0 files) | §Task 2 |
| Host runs | FFmpeg builds + decode probes ONLY (no PS2 boots, no repo builds) | 0 PS2 boots, 0 repo builds; 7 V1 runs + 1 V4 run + 1 V4 authoring | §Task 1 |
| E-lane contact | read-only inspection, never prompt/steer | Clone: `worktree add` + `branch` + `push` (new ref only) + read-only `log/ls-remote/status/diff/show/grep`; checkout never moved; pane untouched | §Task 1 |

## Task 1 — FFmpeg 7.1.1 prefixes + branch + build stack (no device until §Task 2)

### Prefixes: iOS + host rebuilt from the reused tarball (I22 recipe, `/tmp` APFS)

| Item | Receipt |
|---|---|
| Input reuse | Tarball `ffmpeg-7.1.1.tar.xz` copied from `ps2x-i22/spike/`; sha `73398439…` verified BEFORE and AFTER copy (matches I22). I22's `libs-ios/` kept untouched as the comparison baseline |
| Extract | Synchronous `tar -xf` on `/tmp` (no background race — I22's self-inflicted failure mode avoided by construction); `configure` present before proceeding |
| iOS configure | Exit 0, `License: LGPL version 2.1 or later` (`logs/ffmpeg-configure-ios.log`, full). Same flags as I22 + `--prefix=W/ffmpeg-ios-7.1.1`. SDK iPhoneOS27.0, `-mios-version-min=17.0` (I22's spike choice, unchanged) |
| iOS build | `make -j2`, exit 0, wall 7.5 s (delta vs I22 19.3 s = APFS vs ExFAT), `grep -ci "error:"` = 0 (`logs/ffmpeg-build-ios.log`, full) |
| iOS install | `make install` exit 0 → `W/ffmpeg-ios-7.1.1/` (`logs/ffmpeg-install-ios.log`); `lib/` 3 archives + `include/` with generated `avconfig.h` + `ffversion.h` (the headers I22 never staged — the install prefix is what `PS2X_FFMPEG_IOS_ROOT` points at) |
| iOS archives | `libavcodec.a` 677,728 B (I22: 677,720, +8 = ar member-header variance) + `libavutil.a` 926,952 B (same) + `libswscale.a` 895,632 B (same); `lipo -info`: arm64 ×3; global symbols (`nm -g`, sorted) IDENTICAL ×3 vs I22's archives |
| Host configure/build/install | `make distclean` exit 0 → configure exit 0 → `make -j2` exit 0, 7.6 s, 0 errors → install exit 0 (`logs/ffmpeg-configure-host.log`, `ffmpeg-build-host.log`, `ffmpeg-install-host.log`) |
| Prefix sizes | iOS 3,729,641 B logical (165M allocated); host 3,722,064 B logical (165M allocated) — ExFAT 1 MB clusters × ~165 header/lib files |
| `/tmp` disposition | Extracted tree + tarball copy + RGBA bins removed after the install + probes; peak 121M, final 1.4M (probe binary + `fnv.py` + run files). Rebuild cost from the kept SSD tarball: ~15 s |
| Re-verify standing | I22's "re-verify from a fresh tree" gap is CLOSED for the archives (fresh-tree symbols identical); the I22 `libs-ios/` originals remain the pinned comparison set |

### Host-7.1.1 parity anchors (I22's `i22-decode.c` VERBATIM + V4 authoring)

| Run | Receipt |
|---|---|
| Probe link | `clang -arch arm64` + host-install 3 archives + CoreFoundation/CoreVideo/VideoToolbox: exit 0 (same darwin-autodetect delta I22 tabled for host) |
| V1 input fingerprint | `len=240 fnv64=54b07fc845a0494d sha256=25c353b5…` (committed V1 — the device diagnostic must read these same bytes) |
| V1 runs 1–7 | exit 0 ×7, `in=240 parsed=240 packets=4 frames=4 rgba=4096` identical (`logs/decode-runs-host.log`); per-frame lines: frame0+frame1 in-loop, frame2+frame3 drain (the 2+2 split; pre-flush 3/2 per E18 R3's `[MPEG:feed]` line, unchanged) |
| V1 RGBA digest | `len=4096 fnv64=0f0e27e5c1328325 sha256=0a8d7973…` = I22's probe sha BYTE-EXACT; first64/last64 = `fc0000ff` ×16 (R=252, the 7.1 rounding — I22's drift row reconfirmed on the fresh prefix) |
| SIGSEGV re-observe | 0/7 (I22: 1/7 harness-side, never reproduced). The harness was reused per the brief; the fault did not recur — tabled as observation, not a library verdict |
| V4 authoring (cheap → authored) | `color=c=blue:s=320x240:r=25`, 8 frames, `-c:v mpeg2video -threads 1 -g 4 -bf 2` (P/B-frames, non-16x16): exit 0 → `logs/i23-v4.m2v`, 3442 B, `fnv64=40d79ba7d05b8b82 sha256=0cbd0557…` |
| V4 host probe | exit 0, `in=3442 parsed=3442 packets=8 frames=8 rgba=2457600` (frame0–5 in-loop, frame6–7 drain; 320x240 ×8); RGBA `fnv64=6010883bd7f92325 sha256=68b1753f…` first64/last64 = `0000fdff` ×16 |
| Anchors kept | `W/logs/rgba-host-7.1.1.bin` (4096 B) + `v4-rgba-host-7.1.1.bin` (2,457,600 B) on SSD; digests committed in evidence (`logs/rgba-host-fnv.txt`, `v4-*-fnv.txt`, `decode-*.txt`) |

### Branch `i23-ffmpeg-ios` (4 commits, pushed, no force-push; `fork/ssx3` unmoved)

| Commit | Content | Lines |
|---|---|---|
| `696a968` (C1) | CMake iOS block: `elseif(PS2X_IS_IOS)` — 3 IMPORTED archives + include dir from `PS2X_FFMPEG_IOS_ROOT`, loud `FATAL_ERROR` when unset/missing (no silent stub fallback). 3 libs only (avformat/swresample never called by `MPEG.cpp` — deliberate delta vs the 5-lib WIN32 template) | +37 |
| `d5e101f` (C2) | Default flip: `PS2X_IS_IOS` removed from the `OFF` condition — iOS now defaults ON like host; Android stays OFF. One-line condition change | +1/−1 |
| `29633ee` (C3) | Env-gated V1 diagnostic (`MPEG.cpp`): `PS2X_MPEG_VECTOR_PATH`, when set, decodes the named file once through an ISOLATED `MpegFfmpegDecoder` on first real `feed()` input; prints UNGATED `[MPEG:vector]` lines (input digest, feed/flush counts, per-frame dims, RGBA digest, TMPDIR write receipt). Never touches the playback queue or guest state (E18 no-fabrication constraint preserved); env unset = zero behavior change (early return behind a once-flag set before the isolated run, so re-entrant `feed()` calls terminate) | +135 |
| `1aafca7` (C4) | `ps2xRuntime/cmake/iOS-FFmpeg-7.1.1.md`: version + source sha + configure flags + wired-subset rationale + LGPL-2.1 notice (fact) + relink-provision pointer (fulfillment = owner's call) | +55 (new) |
| `aa73dbc` (C5) | Env-gated feed trace (`PS2X_MPEG_FEED_TRACE`): same inSize/parsed/packets/newFrames/totalFrames fields as `[MPEG:feed]` under a distinct `[MPEG:feed-trace]` tag, capped at 32, default off. Added AFTER the AGRESSIVE autopsy below proved the coupled tracker unprobeable — surgical tracing replaces it | +18 |
| Push | `git push fork i23-ffmpeg-ios` → `[new branch]` @`1aafca7`, then fast-forward `1aafca7..aa73dbc` (plain push, never force); remote tip verified by `ls-remote` after each push; `fork/ssx3` = `3adc0478` at recon AND end (E-lane advanced 0) | — |
| Shared-clone contact | `worktree add --detach` + `branch` (new ref) + `push` (new ref) + read-only `log/ls-remote/status/diff/show/grep`; E-lane checkout never moved (`ssx3` @`3adc047` throughout); `?? ps2_log.txt` pre-existing, untouched; pane never prompted/steered | — |
| Design record | Standalone probe-app alternative REJECTED (devicectl cannot launch bare executables; non-UI bundle wrapping is fragile vs the proven runner path; and only the in-app diagnostic exercises the REAL decoder class). Full host-suite rebuild vs 7.1.1 REJECTED (touches shared config — tabled for E-lane instead). Title-path V1 injection REJECTED (would violate no-fabrication — diagnostic is isolated by construction) | — |

### Build stack (branch + 4 local ports, unpushed) + configure

| Item | Receipt |
|---|---|
| Ports | `c474047` (I8 plist, clean) + `eb3fb16` (I10 CMake wiring, auto-merged with the C1 block — disjoint regions) + `df66a1d` (I18 tap, auto-merged into the P1c block, re-verified @`:474`) + `153648b` (I21 wiring extension, auto-merged). Originals picked (same SHAs as I21), zero hand conflicts |
| Worktree | Detached @`193451a` (= C5 + 4 re-picked ports; first stack `153648b` = C4 + ports, superseded by the C5 dance), `status` clean; branch ref = `aa73dbc` (verified by `ls-remote` + local `log`); CSV sha `7c827add…` = I17/I18/I21 (codegen SKIPPED, 0 runs; C17 reused read-only, 0 `._*`) |
| Negative guard test | Configure WITHOUT `PS2X_FFMPEG_IOS_ROOT` (and without `-DPS2X_ENABLE_FFMPEG`, proving the C2 default is ON): exit 1 with the explicit `FATAL_ERROR` recipe pointer (`logs/ios-neg-configure.log`). Scratch dir removed after |
| Configure (final) | Exit 0, wall 1m23s, `PS2X: game objects: 9455 sources` + `dropped 5 in-tree game sources`; cache `CMakeCache.txt:429 PS2X_ENABLE_FFMPEG:BOOL=ON` (I21: OFF at the same line — the flip receipt) + `:423 PS2X_ENABLE_AGRESSIVE_LOGS:BOOL=OFF`. Flags: I21 recipe + `-DPS2X_ENABLE_FFMPEG=ON` (explicit belt) + `-DPS2X_FFMPEG_IOS_ROOT=W/ffmpeg-ios-7.1.1` (`logs/ios-runtime-configure-final.log`, full). NO AGRESSIVE (autopsy below); observation via the C3/C5 env-gated surgical traces |
| Toolchain/deltas | Toolchain byte-identical to I9's; CC Homebrew clang; RECOMP/ANALYZER/TEST/STUDIO OFF, SCCACHE OFF; SDL2/raylib same paths. Only deltas vs I21: base branch (C1–C5), FFmpeg ON |

### AGRESSIVE-build autopsy (built, measured, REJECTED — never installed)

| Finding | Receipt |
|---|---|
| Build | First device build WITH `-DPS2X_ENABLE_AGRESSIVE_LOGS=ON`: `BUILD SUCCEEDED`, exit 0, 0 errors, 8m17s (after a 44 s sidecar failure + purge + re-configure — same ExFAT class as I21, receipted in `logs/ios-runtime-build.log`) |
| Binary | 130,982,600 B / sha `f4dd1382…` vs I21 121,249,160 B → +9,733,440 B (+9.3MB, 8× the expected FFmpeg delta). `__TEXT` +9,289,728; game-objects lib +14,977,712 (170,305,696 vs 155,327,984) with a CHANGED sha (tracker compiled in — I21's byte-identical-lib receipt broken) |
| Cause | `ps2_game_objects` links `PUBLIC ps2_runtime`, inheriting `AGRESSIVE_LOGS=1` + `PS2_FUNCTION_LOG_TRACKER=1` into all 9455 game objects (the "tracker prebuilt-OFF" assumption was WRONG — the lib rebuilds from C17 sources with the new flags). Every guest function entry/exit then does 2 flushed file writes (`ps2_log::log_entry/log_exit` → `ps2_log.txt`) + `RUNTIME_LOG` → console. Unbounded device-side file I/O + console flood + timing destruction |
| Audit correction | The recon audit covered the 43 `PS2_IF_AGRESSIVE_LOGS` taps (all capped ≤128 — that part stands) but NOT the tracker's per-call flushed file I/O. The built binary's size + the `ps2_log.h:240-256` bodies are the receipt |
| Disposition | Binary preserved (`W/logs/ps2EntryRunner-aggressive-130982600B`, never staged/signed/installed). Branch amended with C5 (surgical trace); build tree wiped; final build WITHOUT aggressive (next section). The brief's "enable observation if the build change allows it" resolves to: taps exist, but only the C3/C5 surgical traces are probeable — tabled, not forced |

## Task 2 — Final build + install + probes (V1 then V4)

### Final build record (FFmpeg ON, AGRESSIVE OFF)

| Item | Receipt |
|---|---|
| Build | Exit 0, `BUILD SUCCEEDED`, `-jobs 2`, 10m00s wall, 0 `error:` lines (`logs/ios-runtime-build-final-tail.log` in evidence, full log on SSD) |
| Binary | `W/ios-runtime-device/ps2xRuntime/Release-iphoneos/ps2EntryRunner.app/ps2EntryRunner`, Mach-O 64-bit arm64, 122,458,696 B / sha `edb3eadc…` vs I21 121,249,160 B → **+1,209,536 B (+1.15MB ≈ the expected +1.2MB)**; `__TEXT` +1,048,576 (+1.0MB text) |
| lib | `libps2_game_objects.a` sha `f356aaa7…` = I17's = I18's = I21's (BYTE-IDENTICAL — the probe tests the E18 runtime + FFmpeg, not new game code) |
| Table proof | 9454 `T …_0x…` game syms (same as I21); FFmpeg syms linked ×1 each (`ff_mpeg2video_decoder`, `ff_mpegvideo_parser`, `sws_scale`, `avcodec_send_packet`) — **in-app link of the exact API surface PROVEN** (closes I22 G2's link half; execution is §probes) |
| Tap/diagnostic proof | `diag:frame` ×1, `MPEG:vector` ×9, `feed-trace` ×1 in strings; `without FFmpeg` ×0 (stub branch compiled OUT) |
| Size decomposition (3 binaries) | I21 121,249,160 (__TEXT 109,920,256) → I23-final 122,458,696 (__TEXT 110,968,832, +1.0MB text = FFmpeg+surgical) → I23-aggressive 130,982,600 (__TEXT 119,209,984, +9.3MB = tracker-in-game-objects). The FFmpeg delta matches I22's dead-strip estimate; the aggressive delta is the rejected tracker |

### Stage + sign + install (I21 mechanism + V1/V4 vectors; every delta tabled)

| Step | Receipt |
|---|---|
| Stage | `cp -R` app + ELF + ISO + `regression-frames.m2v` (V1, 240 B) + `i23-v4.m2v` (V4, 3442 B); sidecars 0 after purge. NEW vs I21: the 2 vector files only |
| Bytes | ELF `1b49d05c…` (identical), ISO 3005415424 B `3c2f8eb1…` (identical), V1 `25c353b5…` (committed), V4 `0cbd0557…` (as authored §Task 1) |
| Profile/identity/entitlements | Same wildcard profile `f0793278-…`, same identity `295EFB42…`, entitlements byte-identical to I9's; bundle id unchanged |
| Sign | `codesign --force --sign FP --timestamp=none --entitlements` exit 0 (26.7s), `codesign --verify --strict` exit 0 |
| Install (OVERWRITE) | Pre: PID 4679 (I21 UUID `AAA5E829-…`, I22's baseline exactly). Plain install exit 0 in 67.5s, clean replace → new UUID `C163D3F5-…`; live occupant reaped BY the install (0 `ps2` after). **Twelfth clean overwrite** |
| Presence proof | App's own open (no `devicectl` bundle-listing domain): `Failed to open ELF` ×0; ISO by BEHAVIOR (`sceCdRead unresolved` ×0, K1/install/lookup/handshake identical, same 4 RPC sids, PVD bytes `0143443030310100` in first `[diag:cd]` payload, 1103 reads ending `lbn=0x13bb13`) |

### Probe 1 — V1 vector (`PS2X_MPEG_VECTOR_PATH` + `PS2X_MPEG_FEED_TRACE`, 90 s)

| Item | Receipt |
|---|---|
| Shape | I21 env + 2 vector keys; `--console --timeout 90 --terminate-existing` → exit 2 (alive, PID 4777), 45701 lines / sha `31a95d1b…` (`W/logs/launch-v1-console.log` full on SSD; evidence: deterministic diag-extract + COMPLETE create-extract + sema-extract + delivery-extract + frame lines + sizes) |
| Liveness | 39 create + 5 frame + 5 threads + 30 thread + 5 stubs + 82 stub + 5 syscalls + 28 syscall + 1103 cd + 1062 callback + 15600 dormant + 22373 sema + 130 stacks + 11 vector/trace — every predicted class present; `guest-branch/missing-target` ×0 |
| **V1 on device (lines 15163–15172)** | `path=…/regression-frames.m2v inSize=240 inputFnv64=54b07fc845a0494d` (input = committed V1, FNV exact) → `[MPEG:feed-trace] inSize=240 parsed=240 packets=3 newFrames=2 totalFrames=2` (**P1's E18 R3 line, field-exact**) → `feed: ok=1 newFrames=2` → `flush: ok=1 newFrames=2 totalFrames=4` (the +1/+2 drain split) → frame0–3 `16x16 rgba=1024` → `rgba=4096 fnv64=f0e27e5c1328325 first64/last64=fc0000ff×16` (console prints the unpadded form of `0x0f0e27e5c1328325` — same value as host, §P10) → `wrote=…/tmp//i23-vector-rgba.bin bytes=4096` (double slash = TMPDIR trailing slash, cosmetic) |
| **Title on device (line 15173)** | `[MPEG:feed-trace] inSize=5040 parsed=5040 packets=0 newFrames=0 totalFrames=0` — E18's host title receipt REPRODUCED EXACTLY on device (parser holds the single-shot 5040 B on BOTH sides; H-d live) |
| **P10 retrieval** | `device copy from … tmp/i23-vector-rgba.bin` exit 0 → 4096 B, sha `0a8d7973…` = host-7.1.1 byte-exact; `cmp` clean (`RGBA-BYTE-IDENTICAL`); FNV zero-padded form matches host (`logs/rgba-compare.txt`) |
| Delivery | Callback→producer→release→AddBs order in tails lines 15174–15185 (scheduled 398–403, I21's window +10 lines for the vector block); `0x4029d0` ×6, `0x3b0b10/0x3b0b40/0x3b06b0` ×2, `0x3b1028` ×10 (all = I21) |
| Threads | Main `waitReason=6 waitId=0 pc=0x3b1028` all 5 blocks, `scheduled=8255→0,0,0,0` (still parked — title yields 0 frames); block-0 row **byte-identical to I21** (8255/206/260/859/411/1); pump `900,900,900,900` |
| Frames | 5/5 readable, vsync 900→4500, all counters BIT-IDENTICAL to I21 (submission frozen — 0 title frames served) |
| Screenshot | 1 capture, internal path first then `mv` (owner warning only): `i23-shot1.png`, 2360×1640, 2.0MB, window foreground, `ps2EntryRunner` in status bar, full-black content (viewed) |
| Crash logs | Sleep + `ls`: **0 files** (I21's 5 priors are GONE — device-side rotation/cleanup, not investigated; NO new `.ips` for I23 at check1 AND post-terminate check2) |

### Probe 2 — V4 vector (same shape, V4 path, 90 s)

| Item | Receipt |
|---|---|
| Shape | `--terminate-existing` reaped PID 4777; exit 2 (alive, PID 4778), 45531 lines / sha `7114b79b…` (full on SSD; evidence: vector-extract + sizes only — probe 1 carries the census) |
| **V4 on device** | `inSize=3442 inputFnv64=40d79ba7d05b8b82` (V4 input exact) → `feed-trace inSize=3442 parsed=3442 packets=7 newFrames=6 totalFrames=6` → `feed: ok=1 newFrames=6` → `flush: ok=1 newFrames=2 totalFrames=8` (packets 7+1=8, frames 6+2=8 = host V4 split exactly) → frame0–7 `320x240 rgba=307200` → `rgba=2457600 fnv64=6010883bd7f92325 first64/last64=0000fdff×16` (FNV exact vs host) → `wrote=… bytes=2457600` |
| Title determinism | Second `[MPEG:feed-trace] inSize=5040 parsed=5040 packets=0 newFrames=0` — title hold reproduces across probes |
| **V4 retrieval** | `device copy from` exit 0 → 2,457,600 B, `cmp` vs host V4 RGBA clean (`V4-RGBA-BYTE-IDENTICAL`) |
| Cleanup | Only OUR PID signaled (4778 via `process terminate`); post-cleanup grep = 0; app left installed (I23 build + ISO + vectors; precedent kept) |

### Sema Census III + steady-state diff (probe 1 vs I21 — drift tabled, never smoothed)

| Sema | I23 waits / signals | vs I21 | Standing |
|---|---|---|---|
| 26 | 737 / 736 (531×2 + 183×3 + 22×1, no splice) | Total IDENTICAL; I21's split was 531+182+22+1 spliced line (splice landed on wait↔signal differently — splice-class variance, counts equal) | HELD |
| 30 | 5 / 4 (4×1) | IDENTICAL split | HELD |
| 31 | 5292 / 5291 (5260×−1 + 29×3 + 1×1 + 1 unparsed splice-class) | −1 signal = one fewer vsync pump tick in-window (wall variance; same class as I21's +368) | DRIFT (receipted) |
| 32 | 616 / 615 (206×1 + 205×5 + 175×−1 + 29×3) | IDENTICAL split | HELD |
| 36 | 1 / 0 | IDENTICAL | HELD |
| Part C | 1:4, 4:3586, 5:2824, 6–25:2 ea, 29:414, 33:1640, 34:4, 35:404, 39:160 | id-4 +1 (boot lock traffic — same class as I21's +1/+1/+6); ALL others identical | DRIFT +1 (receipted) |
| Closure | Part C sums 22373 = `diag:sema]` count → **0 destroyed-id lines** (I21: 2) | Cleaner than I21 (splice absence, not a code change) | CLOSED |

| Check | I23 receipt | vs I21 |
|---|---|---|
| Thread rows (30) | Block-0 byte-identical incl. t4 `scheduled=859`; steady pump 900×4 | IDENTICAL (t4 matches I21's 859 exactly this run) |
| Stub sets | block-0 `distinct=1491`, steady `13` ×4; FULL 82-line sets `diff` exit 0 (a mid-brief "top changed" scare was my own head/tail off-by-header arithmetic — the sets never differed; method note kept as a hygiene receipt) | IDENTICAL |
| Syscall sets | block-0 `distinct=30`, steady `2` ×4 (`0x44`/`-0x43` ×900); FULL 28-line sets `diff` exit 0; `0x40`=39 cross-checks the census | IDENTICAL |
| Creators (39) | 39/39 as a sorted set identical to I21's (= I20's — third byte-identical re-check) | IDENTICAL |
| Frame counters | 5/5 bit-identical values, submission frozen | IDENTICAL |
| CD timing | 1103 + 1062; all reads precede dump (last-read 15109 < dump 18963); same first/last lbn | IDENTICAL (dump +8 lines for the vector block) |
| MPEG dispatch | Same order, same counts (AddBs ×6 tails, producer ×2) | IDENTICAL |
| Stub tripwire | `without FFmpeg` ×0 (was ×1) — stub compiled OUT, REPLACED by `[MPEG:feed-trace]` (title 5040/0/0) | CHANGED (the integration, as designed) |
| St tripwire | `sceCdSt` ×0 | IDENTICAL |
| Boot prefix / RPC | K1 `armed` + install#1–8 + lookup#1–6 + handshake + same 4 RPC sids; open-fail ×0, unresolved ×0, teardown ×0 | IDENTICAL |
| Line bridge | 45701 vs 45697 = **+4 CLOSED**: +11 vector/trace −1 warning −2 sema (pump tick) −4 dormant (window); WARNING 5145=5145 absolute (I21's "274" was the I21-vs-I20 delta, verified against I21's full log) | CLOSED |

## Task 3 — Parity P1–P10 row by row + brief gaps + concurrence + handoff

### Parity checklist (device vs host receipts; grade per row with receipts)

| # | Bar (I22) | Device receipt (this brief) | Grade |
|---|---|---|---|
| P1 | SAME counters for V1 (parsed240/packets3/newFrames2) | `[MPEG:feed-trace] inSize=240 parsed=240 packets=3 newFrames=2 totalFrames=2` — E18 R3's `[MPEG:feed]` line field-exact, from the REAL class on device; flush split +1/+2 → 4/4 = host-7.1.1 probe | PASS |
| P2a | Frame decoded: size/queue/nonzero | 4× `16x16 rgba=1024`, RGBA nonzero (`fc0000ff`, retrieved bytes), queue shape 2→4 across feed/flush | PASS |
| P2b | FRAME served + resume-once + guest image nonzero | NOT OBSERVED on device: title yields 0 frames (main still parked, no resume — host-agreeing); V1 frames are isolated by design (no-fabrication forbids injecting them into the guest queue, so no guest waiter exists for V1) | NOT OBSERVED (cause tabled) |
| P3 | AddBs accepts the full title count | `inSize=5040 parsed=5040` at the decoder — the full 5040 flowed end-to-end (no short/partial); first4/header-shape NOT observed (no `feedES`-equivalent in the surgical set) | PASS (accept) + first4 NOT OBSERVED |
| P4 | NOT a match-target: device must produce title FRAMES, not reproduce the hold | Device reproduces the hold shape exactly (`parsed=5040 packets=0 newFrames=0`, both probes) — the parser is bit-identical to host, and the input shape is unchanged (single 5040 B shot, guest sends no more). Bar's precondition (V3/further-input resolution) is outstanding | NOT MET — precondition outstanding (V3) |
| P5 | No-input semantics (v0 alone wakes nothing) | Shape NOT DRIVEN on device (guest drives real input; no no-input callback observed). Host R4 green on the identical class source (E18, 458/458 suite) | Host-held; device N/A |
| P6 | AddBs re-entry without deadlock; wait retained sans frame | AddBs dispatched in callback scope (tail order), probe alive (no wedge), typed Mpeg wait retained with 0 frames. Byte-count of the re-entrant copy unobserved (no return tap) | PARTIAL (scope + no-deadlock + wait observed; count not) |
| P7 | EOS-without-header holds (no frame, still waits) | Shape NOT DRIVEN (title carries a sequence header per host first4). Host E15-input row green on the identical class source | Host-held; device N/A |
| P8 | Guest frame layout + pacing | Served-frame path SHARED (identical source both sides); V1/V4 pixel-layout bytes verified on device (correct dims/strides: 1024/307200 B per frame). Guest-write + vsync pacing unexercised (0 title frames; blank-strip fallback untouched and untriggered) | SHARED-PATH + LAYOUT PASS; guest-write NOT OBSERVED |
| P9a | Parser-flush drain produces the last frames | V1 `flush: ok=1 newFrames=2 totalFrames=4` + V4 `flush: ok=1 newFrames=2 totalFrames=8` through the REAL class — the drain requirement (I22 run-A-vs-B) proven on device | PASS |
| P9b | IsEnd true only when ended + queue empty + presentation complete | NOT OBSERVED (guest never drives flush/IsEnd to completion on the title path) | NOT OBSERVED |
| P10 | Byte-exactness via the 7.1.x pin | V1 device sha `0a8d7973…` == host-7.1.1 (cmp clean, 4096 B retrieved); V4 likewise (2,457,600 B, cmp clean). The ±2 LSB cross-version drift is GONE under the pin | PASS |

Contract outcome: **H-d** — V1/V4 decode fully on device with byte-exact host parity; the title holds (0 frames, still parked) in exact host agreement. On-device FFmpeg EXECUTION is proven (closes I22 G2's execution half); the remaining device wall is the title input shape (V3), not the decoder.

### Brief gaps (table, not necessarily close)

| # | Gap | Standing |
|---|---|---|
| V3 | Full 5040 B title payload (E18 never retained it) | OPEN — E-lane capture requested (request text in §handoff; relayed via orchestrator, pane untouched). Blocks P4's bar only; nothing else |
| V4 | Larger-frame vectors | **CLOSED beyond the brief** ("author if cheap" → authored + host-proved + device-proved byte-identical: 320×240 P/B-frames, 8/8 frames, 2.4MB RGBA) |
| SIGSEGV | I22's 1/7 host harness fault | RE-OBSERVED clean: 0/7 on the fresh prefix with the verbatim harness. Stays an observation, not a verdict |
| AGRESSIVE taps | `[MPEG:*]` observation | RESOLVED via C3/C5 surgical traces (ungated vector + env-gated feed-trace). The AGRESSIVE build itself was built, measured (+9.3MB tracker), and REJECTED with autopsy (§Task 1) — the taps exist for host/debug use but are not probeable on device |

### E-lane concurrence table (shared host/brew/CI pin — NOT touched, exact change tabled)

| # | Shared config | Current | Required end-state for the 7.1.x pin (E-lane's call on mechanism) |
|---|---|---|---|
| E1 | `.github/workflows/build.yml:22` (Linux CI) | Unpinned distro `libavcodec-dev libavformat-dev libavutil-dev libswresample-dev libswscale-dev` | Resolve libavcodec 60.x (7.1.x) in CI — e.g. build the I22/I23 recipe subset as a CI step, or pin a distro snapshot carrying 7.1.x |
| E2 | Host macOS dev env (no repo file) | brew ffmpeg 9.0.1 (E18's suite ran against it; ±2 LSB drift vs 7.1.1 measured) | Host resolves 7.1.x for parity runs (versioned formula / local prefix / container — E-lane's call) |
| E3 | WIN32 prebuilt (`FFMPEG_PREBUILT_TAG n7.1-241205`) | Already 7.1 family | No change (aligned) |
| E4 | `vita/build.sh` (vdpm ffmpeg) | Vita lane | No change (unaffected lane) |
| E5 | This brief's scope | Device 7.1.1 + local host-7.1.1 prefix (both built, both proven) | Shared files above: zero I23 edits (verified: branch touches only `ps2xRuntime/CMakeLists.txt` iOS regions + `MPEG.cpp` + `ps2xRuntime/cmake/iOS-FFmpeg-7.1.1.md`) |

### Handoff (what the next briefs consume / what stays)

| # | Item | Disposition |
|---|---|---|
| H1 | Branch `i23-ffmpeg-ios` @`aa73dbc` (pushed) + this parity table + V1/V4 device receipts | CONSUMED by the follow-up that sequences the title wall (V3-gated) or merges the branch (E-lane review) |
| H2 | V3 capture request (exact text for orchestrator relay — E-lane pane never prompted): "E-lane: please capture the full 5040 B title payload (the bytes AddBs accepted at E18 tick-249, FNV64 `0xd2a9588f0e0fd358`, first4 `000001b3`) as a standalone replayable vector, plus the title movie dims if derivable, via a guarded host probe. Needed for the title-faithful device vector (I22 V3 / I23 P4 precondition)." | RELAY via orchestrator |
| H3 | `W/ffmpeg-ios-7.1.1/` + `W/host-7.1.1/` (install prefixes) + `W/libs` comparison + tarball in `ps2x-i22/spike/` | STAYS on SSD for the follow-up (rebuild cost without them: ~15 s + recipe) |
| H4 | I23 device baseline (installed build UUID `C163D3F5-…`, app left installed but NOT running post-cleanup; probe-1 steady-state + Census III) | STAYS — the next re-probe diffs against it |
| H5 | E-lane fork ownership + remote moves | E-lane ONLY — I23 moved only the new branch ref (remote `ssx3` at `3adc0478` recon AND end; 0 pushes to it) |
| H6 | 4 local port commits (`193451a` stack, unpushed) + aggressive binary + full consoles/build logs on SSD | STAYS worktree/SSD-local (ports are device-build-only; aggressive binary is the rejection receipt) |

## Exact commands

```sh
# --- Recon (E-lane live; read-only until the authorized branch work) ---
FORK="/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp"; W="/Volumes/Extreme SSD/ps2x-i23"
git -C "$FORK" ls-remote fork ssx3          # 3adc0478 at recon AND end
git -C "$FORK" log --oneline -5             # 3adc047 at top ([E18])
git -C "$FORK" status --short               # ?? ps2_log.txt only (recon AND end)
P="00008112-001224302184A01E"
xcrun devicectl list devices --timeout 30   # iPad connected
xcrun devicectl device info apps --device "$P" --timeout 60 | grep -iE "ps2|MF1"
xcrun devicectl device info processes --device "$P" --timeout 60  # PID 4679 = I21/I22 baseline
# --- FFmpeg prefixes (tarball reused; /tmp APFS; I22 recipe) ---
export COPYFILE_DISABLE=1; mkdir -p "$W/logs" local/research/I23/logs
S=/tmp/ps2x-i23-ffmpeg; cp "/Volumes/Extreme SSD/ps2x-i22/spike/ffmpeg-7.1.1.tar.xz" "$S/"
shasum -a 256 "$S/ffmpeg-7.1.1.tar.xz"      # 73398439... (matches I22)
cd "$S" && tar -xf ffmpeg-7.1.1.tar.xz     # synchronous (no I22-style race)
cd "$S/ffmpeg-7.1.1"; SDK=$(xcrun --sdk iphoneos --show-sdk-path)
./configure --target-os=darwin --arch=aarch64 --cpu=generic --enable-cross-compile \
  --cc="xcrun -sdk iphoneos clang" --sysroot="$SDK" \
  --extra-cflags="-arch arm64 -mios-version-min=17.0 -isysroot $SDK -Os" \
  --extra-ldflags="-arch arm64 -mios-version-min=17.0 -isysroot $SDK" \
  --disable-everything --disable-programs --disable-doc --disable-avdevice --disable-avfilter \
  --disable-avformat --disable-swresample --disable-network --disable-iconv --disable-bzlib \
  --disable-lzma --disable-zlib --enable-decoder=mpeg2video --enable-parser=mpegvideo \
  --enable-swscale --disable-asm --enable-static --disable-shared --disable-debug \
  --prefix="$W/ffmpeg-ios-7.1.1"            # exit 0 (LGPL 2.1)
make -j2 && make install                    # exit 0 / exit 0 (7.5 s, 0 errors)
lipo -info "$W/ffmpeg-ios-7.1.1/lib/"*.a    # arm64 x3
make distclean; ./configure --cc=clang --extra-cflags="-arch arm64 -Os" \
  --extra-ldflags="-arch arm64" [same --disable/--enable set] --prefix="$W/host-7.1.1"  # exit 0
make -j2 && make install                    # exit 0 / exit 0 (7.6 s, 0 errors)
# --- Host parity anchors (verbatim harness + V4) ---
clang -arch arm64 -Os -I"$W/host-7.1.1/include" local/research/I22/logs/i22-decode.c \
  "$W/host-7.1.1/lib/"*.a -framework CoreFoundation -framework CoreVideo -framework VideoToolbox \
  -o /tmp/ps2x-i23-ffmpeg/i23-decode       # exit 0
for i in 1 2 3 4 5 6 7; do /tmp/ps2x-i23-ffmpeg/i23-decode local/research/E18/regression-frames.m2v /tmp/x.bin; done  # 7x exit 0, 240/240/4/4/4096
/opt/homebrew/bin/ffmpeg -hide_banner -loglevel error -f lavfi -i "color=c=blue:s=320x240:r=25" \
  -frames:v 8 -c:v mpeg2video -threads 1 -g 4 -bf 2 -f mpeg2video "$W/logs/i23-v4.m2v"  # exit 0, 3442 B
/tmp/ps2x-i23-ffmpeg/i23-decode "$W/logs/i23-v4.m2v" /tmp/x4.bin  # exit 0, 3442/3442/8/8/2457600
python3 /tmp/ps2x-i23-ffmpeg/fnv.py <inputs/outputs>  # FNV64+sha+first64/last64 anchors
rm -rf /tmp/ps2x-i23-ffmpeg/ffmpeg-7.1.1 /tmp/ps2x-i23-ffmpeg/ffmpeg-7.1.1.tar.xz  # /tmp 121M -> 1.4M
# --- Branch (worktree; E-lane checkout never moved) ---
git -C "$FORK" worktree add --detach "$W/fork-wt" 3adc0478
WT="$W/fork-wt"; find "$WT" -name "._*" -delete
# (C1 CMake iOS block; C2 default flip; C3 vector diagnostic; C4 notice — see i23-branch.diff)
git -C "$WT" branch i23-ffmpeg-ios; git -C "$WT" push fork i23-ffmpeg-ios  # [new branch] @1aafca7
# (C5 feed trace @detached-1aafca7; branch -f; push fast-forward 1aafca7..aa73dbc)
for c in c474047 eb3fb16 df66a1d 153648b; do git -C "$WT" cherry-pick $c; done  # -> 193451a, all clean
# --- Guard test + configure + builds ---
cmake [I21 recipe] -S "$WT" -B "$W/ios-neg-test"  # exit 1, explicit FATAL_ERROR (proves C2 default ON); dir removed
cmake [I21 recipe] -DPS2X_ENABLE_FFMPEG=ON -DPS2X_ENABLE_AGRESSIVE_LOGS=ON \
  -DPS2X_FFMPEG_IOS_ROOT="$W/ffmpeg-ios-7.1.1" -S "$WT" -B "$W/ios-runtime-device"  # exit 0, 1m24s
cmake --build "$W/ios-runtime-device" --config Release -- -jobs 2  # exit 65 (._EeScheduler sidecar, 44 s)
find "$WT" -name "._*" -delete; cmake -S "$WT" -B "$W/ios-runtime-device"  # re-generate, exit 0
cmake --build ... # BUILD SUCCEEDED, 8m17s, 0 errors -> 130982600 B (AGRESSIVE; REJECTED, preserved)
rm -rf "$W/ios-runtime-device"
cmake [I21 recipe] -DPS2X_ENABLE_FFMPEG=ON -DPS2X_FFMPEG_IOS_ROOT="$W/ffmpeg-ios-7.1.1" ...  # exit 0, 1m23s, AGRESSIVE OFF
cmake --build ... # BUILD SUCCEEDED, 10m00s, 0 errors -> 122458696 B (+1.15MB)
# --- Stage/sign/install/probes ---
SAPP="$W/signed-app/ps2EntryRunner.app"; cp -R app + SLUS_207.72 + SSX3.iso + V1 + V4; purge sidecars
codesign --force --sign 295EFB42... --timestamp=none --entitlements ...  # exit 0; verify exit 0
xcrun devicectl device install app --device "$P" --timeout 1200 "$SAPP"  # exit 0 OVERWRITE, 67.5s -> C163D3F5
B="/private/var/containers/Bundle/Application/C163D3F5-5F6E-4BF3-AAF4-4640AC95F8C3/ps2EntryRunner.app"
xcrun devicectl device process launch --device "$P" --timeout 90 --console --terminate-existing \
  -e '{"PS2X_CD_IMAGE":"'"$B"'/SSX3.iso","PS2X_DIAG_PERIOD_MS":"15000","PS2X_DIAG_SEMA":"1","PS2X_DIAG_SEMA_CREATE":"1","PS2X_MPEG_VECTOR_PATH":"'"$B"'/regression-frames.m2v","PS2X_MPEG_FEED_TRACE":"1"}' \
  org.ps2x.ps2entryrunner "$B/SLUS_207.72"  # exit 2 (alive, PID 4777), 45701 lines
xcrun devicectl device info files --device "$P" --timeout 60 --domain-type appDataContainer \
  --domain-identifier org.ps2x.ps2entryrunner --subdirectory tmp --no-recurse  # i23-vector-rgba.bin 4 KB
xcrun devicectl device copy from --device "$P" --timeout 60 --domain-type appDataContainer \
  --domain-identifier org.ps2x.ps2entryrunner --source tmp/i23-vector-rgba.bin --destination /tmp/...  # exit 0
cmp /tmp/i23-vector-rgba-device.bin "$W/logs/rgba-host-7.1.1.bin"  # RGBA-BYTE-IDENTICAL
# (probe 2: same with i23-v4.m2v -> exit 2, PID 4778, 45531 lines; V4 cmp clean)
xcrun devicectl device capture screenshot --device "$P" --timeout 60 --destination /tmp/i23-shot1.png
xcrun devicectl device process terminate --device "$P" --timeout 30 --pid 4778  # cleanup only
```

## New gap rows (each with the exact next brief it needs)

| # | Gap | Proving line | Exact next brief needed |
|---|---|---|---|
| G1 | V3 (full 5040 B title payload + title dims) still uncaptured — blocks P4's bar only | P4 row (hold reproduced; precondition outstanding) + H2 request text | E-lane guarded host probe (their lane/lease); device V3-vector probe rides after it lands |
| G2 | Guest-visible serve path (P2b/P9b: FRAME-through-GetPicture + resume + IsEnd) unobserved on device | P2b/P9b rows (0 title frames; V1 isolated by constraint) | Same V3-gated device brief (title-shaped input that yields frames exercises serve/resume/end) |
| G3 | Shared host/brew/CI 7.1.x pin untabled-into-action (E1/E2 tabled, not moved) | §concurrence (zero I23 edits by design) | E-lane concurrence + pin implementation (their config) |
| G4 | `without FFmpeg` tripwire GONE (×0) — future stub-regressions have no on-device signal | Probe-1 tripwire row (expected: stub compiled out) | Informational — the feed-trace + vector diagnostics are the replacement signals; no brief |
| G5 | I21's 5 prior `.ips` vanished (0 files at both checks) + I23 filed none (8 briefs running without a filing) | `logs/crashlog-check*.log` | Informational — device-side rotation; next brief's first `ls` confirms I23; no brief unless action-taken appears |
| G6 | Branch `i23-ffmpeg-ios` unmerged (E-lane owns the fork; review is theirs) | 5 pushed commits, 0 to `ssx3` | Merge/rebase conversation when the E-line allows (ports stay local regardless — device-build-only) |
| G7 | `decoderFailed` still never fires loudly (retry path untouched — shape A needs no S3 change) | I22 W4 row, unchanged (C1–C5 touch no retry logic) | No brief (informational carry — relevant only if a future shape touches S3) |

## Receipt paths

- `local/research/I23/REPORT.md` (this file)
- `local/research/I23/logs/i23-branch.diff` (310-line C1–C5 diff) + `worktree-log.txt` (9-commit stack) + `fork-pin.txt` + `ipad-prestate-i23.log`
- `local/research/I23/logs/ffmpeg-configure-ios.log` + `ffmpeg-build-ios.log` + `ffmpeg-install-ios.log` (full) + host triple + `ffmpeg-distclean.log`
- `local/research/I23/logs/decode-runs-host.log` (7× runs) + `decode-run1-full.txt` + `rgba-host-fnv.txt` + `decode-v4-host.txt` + `decode-v4-stderr.txt` + `v4-input-fnv.txt` + `v4-rgba-host-fnv.txt` + `fnv.py`
- `local/research/I23/logs/i23-v4.m2v` (3442 B authored vector) + `rgba-compare.txt` (P10 cmp receipts + FNV-format note)
- `local/research/I23/logs/ios-device.toolchain.cmake` + `ios-neg-configure.log` (guard proof) + `ios-runtime-configure.log` + `ios-runtime-configure-final.log` (full) + `ios-runtime-reconfigure.log` + `ios-runtime-build-final-tail.log`
- `local/research/I23/logs/launch-v1-console.diag-extract.log` + `.create-extract.log` (COMPLETE 39) + `.sema-extract.log` + `launch-v1-delivery.log` (vector + traces + tails) + `launch-v1-frame.log` + `launch-v1-console.sizes` + `launch-v4-vector.log` + `i23-extracts.sh`
- `local/research/I23/logs/install.log` + `elf-device-path.txt` + `crashlog-check1.log` + `crashlog-check2.log` (0 files) + `screenshot.log` + `i23-shot1.png` (black content, viewed)
- `W/ffmpeg-ios-7.1.1/` + `W/host-7.1.1/` (install prefixes) + `W/logs/` (full consoles 45701/45531 lines + full build logs + aggressive binary + RGBA bins) + `W/fork-wt/` (@`193451a`, clean) + `W/ios-runtime-device/` + `W/signed-app/` (installed bits)
- Fork push this brief: branch `i23-ffmpeg-ios` (`1aafca7` then `aa73dbc`), plain pushes, never force; `fork/ssx3` unmoved

## What I could not do

- Serve a guest-visible FRAME on device — title yields 0 frames on both sides (host-agreeing hold); V1/V4 frames are isolated by the no-fabrication constraint, so no guest waiter exists for them (P2b/P9b).
- Meet P4's bar (title FRAMES, not the hold) — the bar's precondition (V3/further-input) is outstanding; the device reproduces the hold because the parser and input are host-identical (G1).
- Observe first4/header-shape or AddBs return values on device — no `feedES`/return tap in the surgical set (P3-partial/P6-partial).
- Drive the P5/P7 input shapes on device — the guest drives one shape (5040 B with header); host rows stand on the identical class source.
- Exercise guest-write/vsync-pacing — 0 title frames served; the shared path + layout bytes are proven, the write path awaits frames (P8-partial).
- Use the AGRESSIVE build for probing — the coupled per-call flushed file tracker (+9.3MB, timing destruction) forced rejection with autopsy; surgical traces replace it.
- Pin the shared host/brew/CI config — explicitly out of scope; the exact change is tabled for E-lane concurrence (E1–E5).
- Capture V3 (full 5040 B payload) — E-lane's lane/lease; requested via the orchestrator with exact text (H2).
- File or explain crash-log rotation — I21's 5 priors vanished device-side; I23 filed none (G5).
- Present a guest frame — window stays black with 0 title frames decoded and submission frozen since boot; first presented content awaits the V3-gated brief (G2).
- Merge the branch — E-lane owns the fork; 5 commits pushed for review, 0 to `ssx3` (G6).
- Re-run a third probe for vector determinism — two probes (V1+V4) + host 7× runs; title-hold reproduced across both probes and hosts are the determinism receipts.
- Name the launcher of pre-install PID 4679 — the I21 bundle was running though I21 signaled only its own probe PID at cleanup (eighth brief running with a relaunched occupant); it was reaped by the install without investigation.

## TAIL RECEIPT

Report written in 6 chunks (header + contract + caps; Task 1 prefixes + anchors + branch + stack; AGRESSIVE autopsy + C5 corrections; Task 2 build + install + probes + census; Task 3 parity + gaps + concurrence + handoff; commands + gaps + receipts + could-not-do). Pre-receipt measure: 345 lines total, sha256 `fd4e0014b07b3083c388a666bafa2c2fa03b7407eff8b089848d545277828e41` over lines 1–345 (everything before this `## TAIL RECEIPT` section).
Tail content line: "Name the launcher of pre-install PID 4679 — the I21 bundle was running though I21 signaled only its own probe PID at cleanup (eighth brief running with a relaunched occupant); it was reaped by the install without investigation." This receipt line ends the report. END-I23-REPORT.
