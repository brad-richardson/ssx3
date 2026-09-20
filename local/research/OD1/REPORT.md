# OD1 — Odin port readiness of the synth path: REPORT

Brief: `local/muse/prompts/OD1.md` (Part 4 decision 4b, 4 h box; used
about 1). Method: read-only except this dir — no lease claimed, no
device run, no install, no settings change, no builds, no fork changes,
no game content moves. `export COPYFILE_DISABLE=1` on every SSD step.
Tables, no verdicts; no route recommendation (RC1's no-verdict rule
carries over). The device run itself is a successor brief; this doc is
the readiness half (W-G6).

Read first, per the brief: `docs/route-criteria.md` (all of it),
`local/research/M15/REPORT.md` (all of it, incl. the M14→M15 header
diff), and the synth-path sources the M15 report cites. The path being
ported: M15 3-phase capture (v0/mid/full renders through the slot-0
seam) + offline warp/blend synth vs truth (synth==blend, residual
13418 B = 2.34%, 87% |d|=1, static 95.67% exact).

## Sources read (exact files + entry points)

| # | File | Entry points read | Lines used |
| --- | --- | --- | --- |
| S1 | `local/research/M15/m15_replay_context.h` (`910163fa…`, verified below) | `NativeReplay::Step`, `Enabled`, `D2Window`, `Event`, `XfbRange`+`PeMaskWalk::OnBP`, `s_m15_scale`, `m15_mid` gate, stash/live/dump blocks, `m10_copy` | :103-116, :417-490, :1176-1194, :1381-1440, :1282, :1343, :2060-2074, :2344-2347, :2592-2640, :3327-3338, :3431-3518 |
| S2 | `local/research/M15/synth.py` | `main`, `load_dump`, `split_planes`, `join_planes`, `sad_shift`, `xdiff`, PNG writer | :25-27, :38-59, :80-105, :108-224 |
| S3 | `local/research/M15/analyze.py` | CLI usage, `m15_win`/`m15_ref2` parse + tables | :1-8, :149-150, :712-728 |
| S4 | `local/research/M15/build_replay_player.py` | `main` (header swap, injection, compile_copy, relink, launchers, receipt) | :23, :62-80, :84-110 |
| S5 | `local/research/M15/DESIGN.md` | method choice, arm table, header delta, compare plan | all (:1-71) |
| S6 | `local/research/M15/REPORT.md` | runs, wall tables, step-2/step-3 tables, exact commands, dumps | all (:1-695) |
| S7 | `tools/android_trial.py` | `build`, `run`, `analyze`, `launch_command`, `launch_env`, `apply_affinity`, sampler hookup, pulls | :51, :218-269, :320-331, :405-455, :498-600, :689-702 |
| S8 | `local/research/S2/build_android_trial.py` | `build` (S2 header swap, STEP_CALL, D5 patch, `-DSSX_D2_REPLAY_ALWAYS=1`, aarch64 gate) | :28-37, :48-105, :108-189 |
| S9 | `local/research/S2/arm.py` | `main` (lease/battery/thermal gates, run, tombstone pull, kill-rule read) | :120-173, :176-267 |
| S10 | `local/research/S2/REPORT.md` | EGL capacity arms, device code path (`det=1 dual=1`), build recipe, Vulkan block | :294-325, :473-600, :776-786, :841-890 |
| S11 | `tools/gamecube_schedule_check.py` | `main` (player-dir, `--immediate-xfb`, `--resolution`, profile seed) | :127-176 |
| S12 | `native/diagnostics/native_callback_trace.h` | `Now`, `RefreshNow`, `Output` (`SSX_NATIVE_PROBE`) | :79-86, :212-217 |
| S13 | `tools/gamecube_draw_trace.py` | `compile_copy`, `BUILD`/`VENDOR`, ninja commands | :17-19, :26-46 |
| S14 | `tools/odin_sampler.sh` | on-device sampler (cpufreq/thermal/gpuclk ticks) | all (:1-67) |
| S15 | `docs/route-criteria.md` | B1–B8 / C1–C5 / W-table rows, source + blank tables | all (:1-152) |
| S16 | `docs/numbers-ledger.md` | M15 row, M16–M63 close row, S2b/Vulkan row, D6 rows | :71, :97-102, :220-225 |
| S17 | `docs/research/120hz-pacing-acceptance.md` | pacing bars, 25 s window rule | :16-22, :27-38 |
| S18 | SSD `/Volumes/Extreme SSD/android-spike/D6/REPORT.md` | update/render medians | :63, :197-198 |
| S19 | SSD `/Volumes/Extreme SSD/android-spike/D4/part3/sfstats.sh` | SF timestats sampler (W-G5 tool, not the M15 path) | :1-15 |
| S20 | SSD compile DBs | EGL TU flags, VK TU flags + TU origin | `core-egl-d5-build/compile_commands.json`, `core-vk-build/compile_commands.json` (StaticRecompCore_Run.cpp entries) |

M15 header sha (trust `shasum`, not memory):
`910163fa413995a487e16ff43e4fdf7ccfe388ceb76bf1f71c39eea92aeb87de`
(matches the M15 report's committed sha, S6 :28).

## Deliverable 1 — named interface

### 1a. Entry points (capture → synth → analyze)

| ID | Element | File + line or OPEN | Shape / notes |
| --- | --- | --- | --- |
| E1 | Dispatch entry `NativeReplay::Step` | S1 :1381 (`static inline void Step(CPUState& c)`) | Called per dispatch from the instrumented TU; desktop injection S4 :62-63, device shape S8 :36-37 + :151 |
| E2 | Enable gate `Enabled()` | S1 :103-116 | Device TU: `SSX_D2_REPLAY_ALWAYS` → always true (launch env fixed). Desktop: `SSX_NATIVE_REPLAY=1` env |
| E3 | Record window `D2Window()` | S1 :1189-1194 | Device: `Now()` in [100.0, 200.0) wall s (inside the movie race). Desktop: `ExperimentalWindow()` |
| E4 | Record seam | S1 :1428-1440 | `recorder.StartRecording(1, …)` + `record_start fc=` event; disabled-mode marker S1 :1386-1399 |
| E5 | Probe emit `Event()` | S1 :1176-1184 | JSONL `{"event":"replay","schema":2,"action":…,"wall":…,"replay":N,"bytes":frame.size(),"detail":…}`, fflush per row |
| E6 | Probe clock/sink `Now`/`Output`/`RefreshNow` | S12 :79, :212-217, :85-86 | Sink path from `SSX_NATIVE_PROBE` env (S12 :217); on device set by `launch_env` (S7 :447-455) |
| E7 | M15 arm gate `m15_mid` | S1 :2060-2065 | `m10_ramref && !autoscan && !perreplay && SSX_M15_MID==1`; `m15_kfull=150` (:2065); phases v0 0–99 / mid 100–149 / full 150–199 |
| E8 | Mid-scale seam `s_m15_scale` | S1 :1282 (decl, default 1.0), :1343 (`*f += 0.1f * s_m15_scale`), :2235 reset, :2344 mid→0.5 (+0.05), :2347 full→1.0 (+0.1) | Mid matrix is the truth render through the same seam (S5 :18-20) |
| E9 | v0 stash + live rows + dump capture | S1 :2592-2594 (stash), :2631-2640 (live `m15_*` rows; mid dump @149, full dump @199) | Reference = replay 99 scratch (`m10_ref2`, S1 :2599-2601) |
| E10 | Post-loop diff + file dumps | S1 :3431-3518 | v0 diffed post-loop (:3436-3460); dumps via `fopen/fwrite` to `$SSX_M15_DUMP_DIR/m15-{r000,v0,mid,full}.bin` (:3460-3493); `m15_win` (:3507), 200× `m15_ref2` (:3518) |
| E11 | XFB geometry decode | S1 :417-425 (`XfbRange`), :448-490 (`OnBP`: w=(WH&0x3ff)+1, h=1+hsrc·yscale, addr=dest<<5, stride=stride<<5, bytes=h·stride) | `r.found=(bytes>0 && addr!=0)` (:489); scratch retarget offsets (:490-493) |
| E12 | Copy-table receipt `m10_copy` | S1 :3327-3338 | `n=… xfb=addr/bytes` + per-copy `draw,dest,bytes,xfb,clear,tl,w,h,ovl` — carries the w/h the decode needs |
| E13 | Offline synth `synth.py main` | S2 :108-224 | Args `DUMP_DIR OUT_DIR [PROBE]` (S2 :4, :109-111); dump-vs-probe FNV cross-check S2 :121-141 |
| E14 | Synth kernels | S2 :44-50 `split_planes`, :53-59 `join_planes`, :72-77 `shift_plane`, :80-95 `sad_shift`, :98-105 `xdiff` | Masked SAD ±24 on Y (S2 :148-150); half-shift split S2 :151-161; synth=mean of half-warped planes (S2 :162-168); blend=byte mean (S2 :169-171) |
| E15 | Analyzer `analyze.py` | S3 :1-8 (CLI `LABEL=probe.jsonl`), :149-150 (`m15_win`/`m15_ref2` parse), :712-728 (guard + per-replay + distribution tables) | Missing keys print n/a (S3 :8) |
| E16 | Desktop run driver | S11 :127-176 | `--player-dir` (must be under `local/`, receipt-checked :134-140), `--immediate-xfb`, `--resolution {640x528,1920x1080}`; seeds GFX `[Hacks]` + `backend=Vulkan` (:150-157) |
| E17 | Desktop build driver | S4 :27-110 | Header S4 :23; injection S4 :62-63; `compile_copy` S4 :74-75; relink shadow S4 :76-80; launchers S4 :84-107; `build.json` receipt S4 :109 |
| E18 | Device build driver (S2 shape; M15 variant OPEN) | S8 :108-189; M15 variant = OPEN O1 | Headers S8 :28-35; `STEP_CALL` S8 :36-37; `-DSSX_D2_REPLAY_ALWAYS=1` S8 :165-168; aarch64 gate S8 :181-186 |
| E19 | Device run driver | S7 :498-600 (`run`), :218-269 (`build`), :689-702 (`analyze`) | Launch line S7 :320-331; env S7 :447-455; affinity S7 :405-444; sampler S7 :552-570; pulls S7 :580-595 |
| E20 | Device arm gates | S9 :176-267 | Lease S9 :191-210; battery S9 :198-205; thermal S9 :120-138; kill rule S9 :140-173; crash pull S9 :239 |

### 1b. Buffers: inputs/outputs with shapes + formats

| ID | Buffer | Shape + format | Producer → consumer |
| --- | --- | --- | --- |
| B1 | XFB frame (`mask.xfb`) | `bytes = h·stride` (S1 :485); M15 run: 573440 B = 640×448×2, YUYV 2 B/px (S6 :233-236); addr `0x004dc660` (S6 :74) | Stream decode (E11) → scratch renders → dumps |
| B2 | Decoded planes | Y 640×448 u8; U/V 320×448 u8 (S2 :44-50); wire order per 4 B: Y0 U Y1 V (S2 :53-59) | `split_planes` → SAD/warp → `join_planes` |
| B3 | Phase dumps `m15-{r000,v0,mid,full}.bin` | `mask.xfb.bytes` each (573440 B on desktop, S6 :413-414); `fopen/fwrite` to `$SSX_M15_DUMP_DIR` (S1 :3460-3493); fail-soft flags `d0/dv/dm/df` + FNV hashes in `m15_win` (S1 :3495-3507) | Device path + pull = OPEN O2/O3 |
| B4 | Synth outputs | `m15-synth.bin` 573440 B (S2 :172); `blend` = byte mean (S2 :169-171); 4 PNGs 320×224 BILINEAR, 497999 B total, 5 MiB budget (S2 :217-224; S6 :278-281) | Host-only; no device component |
| B5 | Probe JSONL | Schema-2 `replay` events (E5); `m15_win` detail string (S1 :3495-3506); 200 `m15_ref2` rows `r/phase/ok/xd2/xdmax/xdmean/hash/refhash` (S1 :3510-3517); desktop probe 20781764 B (S6 :135) | `SSX_NATIVE_PROBE` file → `adb pull` (S7 :580-595) → S3/S2 |
| B6 | In-sequence RAM | `m15_prist` = 100 × `xfb.bytes` ≈ 57 MB (S1 :2066-2074); `m15_mid_dump` + `m15_full_dump` one frame each (S1 :2067); per-replay `m15_xd2/xdmax/xdmean/hash/have` ×200 (S1 :2068-2072) | Allocated at sequence start; freed at TU scope end |

### 1c. Build flags

| ID | Flag / define | File + line or OPEN | Notes |
| --- | --- | --- | --- |
| F1 | `-DSSX_NATIVE_TRIAL_APP=1` | S7 :51, applied S7 :150 | Marks the Android trial TU; changes `D2Window`/window semantics (S1 :1189-1194) |
| F2 | `-DSSX_D2_REPLAY_ALWAYS=1` | S8 :165-168 (receipted `:168`) | Device replay enable (E2); desktop never defines it |
| F3 | M15 device enable (compile-time) | OPEN O2 | No equivalent of F2 exists for `SSX_M15_MID`/`SSX_M15_DUMP_DIR`; device launch env is fixed (S10 :420-422) |
| F4 | EGL TU compile | S20 `core-egl-d5-build/compile_commands.json` (StaticRecompCore_Run.cpp entry) | `--target=aarch64-none-linux-android35 -std=c++23 -O3 -fPIC -march=armv8.2-a+crc+lse`, NDK sysroot; defines include `HAS_OPENGL`/`HAVE_EGL`; `HAS_VULKAN` ABSENT |
| F5 | VK TU compile | S20 `core-vk-build/compile_commands.json` | F4 + `-DHAS_VULKAN`; TU origin = repo tree (`third_party/ModernGekko/…`), unlike EGL's `m4-src` origin |
| F6 | Relink shadow | S7 :179-192 | `trial.o` ahead of the first `.a` shadows the original TU member; receipt `trial_binary_sha256` verified before launch (S7 :510-512) and on device after push (S7 :523-525) |
| F7 | Desktop retarget | S13 :26-46 | `compile_copy` retargets `-c`/`-o`, strips `-MF`/`-MT`; commands from `local/tooling/ninja -t commands moderngekko-run` in `BUILD` |
| F8 | Desktop M15 env | S6 :390 | `SSX_M10_SLOT=0 SSX_M10_RAMREF=1 SSX_M9_SURV=1 SSX_M15_MID=1 SSX_M15_DUMP_DIR=…` + `SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE=…`, dual core + `--cpu-thread` |

### 1d. Toolchains

| ID | Toolchain | File + line or OPEN | Notes |
| --- | --- | --- | --- |
| T1 | Host (desktop player) | S13 :17-19 (`BUILD=local/native/runtime-build`, `VENDOR=third_party/ModernGekko`), S4 :66-67 (`local/tooling/ninja`) | Output: `players/m15-mid/player` + `build.json` + launchers (S6 :417-422); Metal backend |
| T2 | Device EGL | S20 + NDK `source.properties` (`Pkg.Revision = 30.0.16248370`, r30): `toolchains/llvm/prebuilt/darwin-x86_64/bin/clang++` | Build dir `core-egl-d5-build`; links `libvideo{null,ogl,software,common}.a`, NO `libvideovulkan.a` (S10 :776-786; re-verified by find) |
| T3 | Device VK | S20 `core-vk-build` (has `libvideovulkan.a`) | STALE: predates `TryHleFpUnavailable` — current TU fails to link, m4-src TU binary SIGSEGVs ~20 s into boot (S16 ledger :71); fresh build needed (W-G4, S15 :57) |
| T4 | Offline synth/analyze | S2 :22-23 (`numpy`, `PIL`) | Host `python3`, runs on the Mac against pulled dumps + probe; no device component |

### 1e. Device-side dependencies

| ID | Dependency | File + line or OPEN | Present on device (read-only `ls`, this brief) |
| --- | --- | --- | --- |
| D1 | `/data/local/tmp/mg/game` (GXBE69 extraction) | S7 :504-506 (DOL pin `b92162d6…` checked via `sha256sum` on device) | present |
| D2 | `/data/local/tmp/mg/user-d2single` (template) | S9 :182 (`--template d2single`); copied to `user-<tag>` + shots cleared + idle asserted + GFX seeded (S7 :527-539) | present |
| D3 | `/data/local/tmp/mg/gGXBE69_recomp.so` (module) | S7 :320-331 (`--module`); default `gGXBE69_recomp.so` (S7 :720) | present |
| D4 | `/data/local/tmp/mg/m3-snow-jam-3min.dtm` (movie) | S9 :183; movie+dual-core ⇒ `det=1 dual=1` (S10 :138-145) | present |
| D5 | GFX seed `ImmediateXFBEnable=True`, `CapImmediateXFB=False` | S7 :106-141 (`seed_gfx_ini`), applied S7 :532-539; M15 needs the immediate-XFB path the same way the schedule does | seeded per run; post-run copy pulled (S7 :582) |
| D6 | Launch line | S7 :320-331 (`timeout N ./moderngekko-run-trial --headless --graphics {OGL,Vulkan,Null} --game … --user-dir … --module …`) + env (S7 :447-455) | EGL (`OGL`) is the runnable backend (T2); Vulkan needs T3 refresh |
| D7 | Affinity `emu=80,video=40` | S7 :349-373 (roles; `80`=cpu7, `40`=cpu6), applied + verified S7 :405-444 | S2 precedent both arms (S10 :548-552) |
| D8 | Sampler `tools/odin_sampler.sh` | Pushed + sha-verified, 1 s ticks vs the real PID (S7 :552-570); tick content S14 :19-65 | host copy S14; device copy pushed per run |
| D9 | Run gates | Lease absent + `printf` claim + `finally` remove (S9 :191-210, :260-263); no `moderngekko` (S9 :194-196); battery ≥20 + status 2/5, `low_power`≠1 (S9 :198-205); thermal <60 °C or 5-min wait (S9 :120-138); post-hoc kill rule: any zone ≥110 °C or cpu7 <2 GHz ×5+ ticks (S9 :140-173); `logcat -d -b crash` pull (S9 :239) | state this brief: lease absent, no process, 100%/5, 41.8 °C (§4) |
| D10 | Screenshots / race proof | Cadence env (S7 :92-103); S2 arms produced none (`ScreenShots/GXBE69` empty, S10 :597); substitution receipt (capture wall + emu busy + race-sized frame, S16 ledger :71) | same shape expected for the M15 arm |
| D11 | `m15-*.bin` dump pull | OPEN O3 | `android_trial.py` pull list (S7 :580-595) has no dump entries; successor adds them or a fallback pull like S9 :243-254 |
| D12 | Onscreen proof (`sfstats.sh` + analyzer) | S19 (`D4/part3/sfstats.sh` :1-15); W-G5 (S15 :58) | NOT part of the M15 sequence (presentation suppressed); tabled so the checklist does not silently absorb W-G5 |

### 1f. OPEN rows (named, not hand-waved)

| ID | Gap | Where it bites | What closes it |
| --- | --- | --- | --- |
| O1 | No M15 Android trial build driver | Build time: S8 hardcodes the S2 header (S8 :26), header set (S8 :28-35), and step calls (S8 :36-37) | Successor brief writes `build_m15_trial.py` (S8 pattern, M15 header + `NativeReplay::Step` only) |
| O2 | No device enablement for `SSX_M15_MID` / `SSX_M15_DUMP_DIR` | Sequence config: `m15_mid` reads env (S1 :2060-2065) but the device launch env is fixed (S10 :420-422), so the 3-phase capture never arms on device | Compile-time define (F2 pattern, e.g. `SSX_M15_ALWAYS`) + device dump dir (`/data/local/tmp/mg/…`); M15 header delta, env default unchanged on desktop |
| O3 | No dump pull for `m15-*.bin` | Receipts: dumps land on device (O2's dir) but the pull list (S7 :580-595) omits them | Successor extends the pull list or the arm fallback (S9 :243-254 pattern) |
| O4 | `synth.py` hardcodes `W,H = 640,448` | Offline analysis: `load_dump` asserts 573440 B (S2 :25-27, :38-41); a device XFB of any other geometry aborts the synth | Read w/h from the `m10_copy` receipt (E12) or `m15_win xfbbytes` + stride; assert `len == w·h·2` |
| O5 | No Vulkan M15 arm possible | Backend choice: T3 stale (S16 ledger :71) | W-G4 fresh `core-vk-build` first; M15 EGL arm does not wait for it |
| O6 | Device XFB geometry unknown | Decode + buffer sizes (B1–B3): desktop 640×448 is one template's geometry, not a contract | First device run's `m10_copy`/`m15_win` receipts name it; O4 consumes it |
| O7 | M15 header Android-TU portability unproven | Compile time: `getenv`/`fopen`/`snprintf`/vector use (S1 :3460-3493 e.g.) is expected-fine on bionic but never compiled there | O1's build attempt is the proof; failures tabled, not forced |

## Task 1.2 — gaps between "builds/runs here" and "builds/runs on Odin"

Each row: what the gap is + where it bites + what closes it.
Frame-dependent numbers (residual bytes, medians) are NOT gaps: every
run records its own frame (S6 :109-110), so the device arm reproduces
the method and the receipt shapes, not desktop's constants.

| ID | Gap (what) | Where it bites | What closes it |
| --- | --- | --- | --- |
| G1 | No M15 Android trial build (O1) | `moderngekko-run-trial` cannot carry the M15 header; S8 builds S2-only | `build_m15_trial.py` + receipted trial dir on the SSD (S8 pattern) |
| G2 | M15 env has no device passthrough (O2) | `m15_mid=0` on device → v0-only sequence, no mid/full, no dumps | Compile-time enable + device dump dir (F2 pattern) |
| G3 | Dumps not pulled (O3) | Synth inputs stay on the device even after a green sequence | Pull-list extension (S9 :243-254 pattern) |
| G4 | `synth.py` geometry assert (O4) | First non-640×448 device XFB aborts offline analysis | w/h from `m10_copy` (E12) before the first device synth |
| G5 | Vulkan unavailable (O5) | `--graphics Vulkan` cannot run the M15 TU anywhere | W-G4 fresh `core-vk-build`; EGL arm proceeds independently |
| G6 | Portability unproven (O7) | Unknown until the O1 build attempt | The attempt itself, tabled either way |
| G7 | Window semantics differ (E3) | Desktop `ExperimentalWindow()` vs device wall [100,200) s: the device frame is a different race moment, so no byte-level desktop↔device comparison is meaningful | Nothing to fix: checklist bars are shape/receipt bars (K1–K15), with desktop constants cited as method precedent only |
| G8 | No screenshots expected (D10) | HUD-verified racing is unavailable the same way it was for S2 (S10 :597) | Substitution receipt per S16 ledger :71 (capture wall + emu busy + race-sized frame) |
| G9 | Trial link not byte-reproducible | Two links of the same sources differ (S10 :800-807); a stale receipt aborts the run (S7 :510-512) | Verify receipt-vs-disk before every arm (S10 :878-880 pattern) |

## Deliverable 2 — device-run checklist

Check × pass bar × landing slot. Bars citing `docs/route-criteria.md`
name the B/C row; NEW bars carry an exact threshold + one-line why.
Frame-dependent cells say TABLED (method receipt, no desktop constant).

| ID | Check | Pass bar | Bar source | Landing slot |
| --- | --- | --- | --- | --- |
| K1 | Sequence completes | `done` present; 200 `m15_ref2` rows, `ok=1` on all 200 | NEW (exact: 200/200; why: the M15 desktop shape, S6 :342 — anything less is a partial capture) | Ledger new row "M15-on-Odin"; W-G6 successor receipts |
| K2 | Per-phase determinism | mid: 1 distinct `xd2` + 1 distinct hash over n=50; full: same over n=50; v0: ≤2 distinct `xd2` (99×0 + r0) | NEW (exact: 1/1/≤2; why: determinism is the precondition for synth-vs-truth, S5 :22-23) | Same ledger row; C1 GC addendum |
| K3 | Dumps complete + authentic | `m15_win`: `d0=dv=dm=df=1`; dump-vs-probe FNV match 4/4 (S2 :136-141) | NEW (exact: 4/4; why: proves the analyzed bytes are the rendered bytes) | Same ledger row (hashes) |
| K4 | XFB geometry consistent | `m10_copy` w/h + `xfbbytes`: `len(dump) == xfbbytes == h·stride`; decode succeeds (S6 :233-236 shape) | NEW (exact: equality; why: decode-correctness precondition; feeds O4/O6) | Same ledger row (w/h/bytes) |
| K5 | Shift estimate receipted | Masked-SAD minimum (dx,dy) + SAD + full 3×3 neighborhood tabled (S2 :201-208 shape) | NEW (exact: tabled, no fixed shift; why: the synth==blend claim rests on the minimum, S6 :248-251) | Same ledger row; C1 GC addendum |
| K6 | Synth-vs-truth diffs | 5-pair `xd/xdmax/xdmean/frac` + Y-\|d\| hist + vertical bands tabled (S2 :178-200 shape) | C1 method (S15 :39); residual fraction computed, no fixed bar (frame differs) | C1 GC addendum; ledger row |
| K7 | Static share | `v0==mid==full` byte-exact share tabled (desktop 95.67%, S6 :274) | C1 method; TABLED (frame differs) | C1 GC addendum |
| K8 | Motion exists | `full-vs-v0 xd > 0` | NEW (exact: >0; why: zero motion makes the synth test vacuous) | Ledger row |
| K9 | Per-replay cost | Wall med/p95 + `mem/cp/pre/run/sync` medians tabled; B1 gate ≤ 6 ms/replay (S15 :26) | B1 (S2 gate, S15 :26) | B1 GC cell (4th arm); ledger row |
| K10 | Guest-clean | `xfb_equal` N/N, `pediff=0`, `vidiff=0`, `live_xfb_untouched=1`, continuation hash recorded (S6 :364-372 shape) | NEW (exact: 0/0/1; why: S2 item-5 honesty gate, S6 :361-372) | Ledger row; C5 GC addendum |
| K11 | Thermal guard | Hottest `cpu-*` < 110 °C every tick; cpu7 ≥ 2.0 GHz (kill rule, S9 :140-173); launch <60 °C or 5-min wait (S9 :120-138) | B8 (S15 :33) + S9 op rule | B8 GC cell; sampler log on SSD |
| K12 | Battery gate | Level ≥ 20 + status 2/5, `low_power` ≠ 1 at launch (S9 :198-205) | S9 op rule | Arm pre-json on SSD |
| K13 | No crash | `logcat -b crash` shows no entry for the run PID (S9 :239) | NEW (exact: 0; why: tombstones rotate fast; absence is the receipt) | Arm receipts on SSD |
| K14 | Race proof | Shots pulled, OR substitution receipt (capture wall + prior-10 s emu busy + race-sized frame, S16 ledger :71) | S10 :597-600 precedent | Ledger row |
| K15 | Synth artifacts | `m15-synth.bin` FNV + 4 PNGs (base/synth/truth/diffmap) ≤ 5 MiB total (S2 :224; S6 :278-281) | C1 method (S6 :344) | Evidence dir (committed PNGs) |

Out of scope for the first M15 arm (tabled so nothing is silently
absorbed): 25 s warmed window (B4), pacing bars (B5), per-combo splits
(B3), onscreen display proof (W-G5/D12), Vulkan arm (O5/G5), autoscan
carrier scan (arm B is desktop-only; S6 :60-67).

## Reachability probe (read-only; no install, no run, no settings changes)

Odin 3 reachable over USB (`622c49b1`). Serial-file note: repo
`local/odin-serial` reads `622c49b1` (matches this probe); SSD
`android-spike/ODIN_SERIAL` reads `192.168.1.53:5555` (stale Wi-Fi
entry from the S2 era) — the successor arm must confirm which transport
answers before launch (S7 :277-294 sole-device fallback covers it).

| # | Command (read-only) | Output (2026-09-20, UTC evening) |
| --- | --- | --- |
| R1 | `adb devices -l` | `622c49b1 device usb:… product:sun model:Odin3 device:sun transport_id:1` |
| R2 | `dumpsys battery` (head) | level 100, status 5 (full), AC powered true, USB powered false, temp 240 (deci-C), health 2 |
| R3 | `settings get global low_power` / `system performance_mode` / `system fan_mode` | `0` / `1` / `4` (matches S2 arms, S10 :590-595) |
| R4 | `scaling_max_freq` cpu0 / cpu7; kgsl governor | `3532800` / `4320000` kHz; `msm-adreno-tz` (matches S10 :590-595; no underclock) |
| R5 | `getprop` release / model | `15` / `Odin3` |
| R6 | thermal zones (all, milli-C) | Hottest `cpu-*`: `cpu-1-1-1 41800` (41.8 °C, idle); `gpuss-*` 28–29 °C; `aoss-*` ~28 °C — below the 60 °C launch gate (S9 :120-138) |
| R7 | `df -h /data` | 78 G size, 50 G used, 29 G avail (64%) — dumps + probe + trial binary fit by orders of magnitude |
| R8 | `cat /data/local/tmp/mg/LEASE` | absent (`rc=1`) — no lease held |
| R9 | `ps -A \| grep -i moderngekko` | empty (`rc=1`) — nothing running |
| R10 | `ls -d` game / template / module / movies | `game`, `user-d2single`, `gGXBE69_recomp.so`, `m3-snow-jam-3min.dtm` (+ siblings) all present |

## Exact commands (re-derivation; SSD steps with `COPYFILE_DISABLE=1`)

```sh
export COPYFILE_DISABLE=1
shasum -a 256 local/research/M15/m15_replay_context.h   # 910163fa… (S1)
grep -n "s_m15_scale\|m15_mid\|m15_win\|m15_ref2\|SSX_M15_MID\|SSX_M15_DUMP_DIR" local/research/M15/m15_replay_context.h
python3 -c "import json;cc=json.load(open('/Volumes/Extreme SSD/android-spike/core-egl-d5-build/compile_commands.json'));print([e for e in cc if e['file'].endswith('StaticRecompCore_Run.cpp')][0]['command'])"  # F4
find "/Volumes/Extreme SSD/android-spike/core-egl-d5-build" -name "libvideo*.a"   # T2: no vulkan
find "/Volumes/Extreme SSD/android-spike/core-vk-build" -maxdepth 8 -name "libvideo*.a"  # T3: has vulkan
adb devices -l; adb -s 622c49b1 shell 'dumpsys battery | head -20'
adb -s 622c49b1 shell 'for z in /sys/class/thermal/thermal_zone*; do echo "$z $(cat $z/type 2>/dev/null) $(cat $z/temp 2>/dev/null)"; done'
adb -s 622c49b1 shell 'df -h /data; ls -d /data/local/tmp/mg/game /data/local/tmp/mg/user-d2single /data/local/tmp/mg/gGXBE69_recomp.so /data/local/tmp/mg/m3-snow-jam-3min.dtm'
ls "/Volumes/Extreme SSD/android-spike/D4/part3/"   # sfstats.sh + sfstats_analyze.py (S19)
```

## What I could not do (gaps for the successor)

1. O1–O3 need a build/run brief (device lease + trial build + arm);
   this brief claimed no lease and ran nothing by design.
2. O4/O6 close only after the first device `m10_copy` names the
   device XFB geometry.
3. O5/G5 (Vulkan) waits on W-G4, independent of the EGL arm.
4. No PS2 numbers: this brief fills the readiness half only (W-G6),
   per the brief's scope note.

## Files

Committed under `local/research/OD1/` (STANDALONE, nothing else
touched): `REPORT.md` (this file).

Tail receipt follows in the commit message trailer block; `tail -3`
verified before commit.
