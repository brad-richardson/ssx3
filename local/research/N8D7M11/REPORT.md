# N8D7M11 — minimal Odin GS-stream replay harness design (read-only)

**State: design COMPLETE, outcome A, choice (A) dev-only NativeActivity
replay mode. Read-only: no source edit, build, replay, boot, stream
copy, device/lease action, push, board/global edit, or upstream contact.
No Turnip/shader/barrier/driver cause is claimed. The orchestrator gates
any implementation or Odin run. Cited source strings cannot prove
Android runtime behavior; `check.py` verifies pins, cited rows, and
table invariants only.**

Brief: `local/muse/prompts/N8D7M11.md`. Question: what is the smallest
Android path that replays the same closed N8D7M6 stream inside the Odin
app process using its bundled Turnip backend, without launching the
live EE game thread — (A) a dev-only NativeActivity replay mode or (B)
a headless arm64 executable?

Facts to start from: N8D7L fork `a8cfefa`, paraLLEl `3a66c19`, N8D7M6
capture SHA `f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593`
(1,100,696,462 B), N8D7M1 APK `e077bef8a7ba8aab44f46c515f79fade1ae045cc337bf7285e7b652e739758a1`.
N8D7M10 verdict B: the parser lives only in desktop `ps2x_tests` and
the APK builds tests OFF (`local/research/N8D7M10/REPORT.md` §2,
`ORCH-GATE.md`). N8D7M6 verdict A: Mac paraLLEl replay of those exact
bytes gives selected input 300/448 vs live Odin 23/448 with all 11
descriptor fields equal (`local/research/N8D7M6/REPORT.md` §§3–4,
`ORCH-GATE.md`). N8D7M1 packages arm64 runner + Turnip + HAL shim and
nothing else native (`local/research/N8D7M1/REPORT.md` §§1–4).

Direct reads throughout at the pinned revs (fork worktree
`~/dev/ssx3-work/N8D7L/PS2Recomp`, parallel worktree
`~/dev/ssx3-work/N8D7F/parallel-gs`). LSP hover was attempted for this
file class in N8D7M10 and returned no server (N8D7M10 REPORT §1,
same basis as N8D7M7 §1); every code link below rests on direct reads.

## 1. Pins read in this design

| Item | Pin |
| --- | --- |
| Fork worktree | `~/dev/ssx3-work/N8D7L/PS2Recomp`, branch `n8d7l-oracle`, HEAD `a8cfefad109134767b0810b7707b4b58a5dfcca7` |
| Parallel-GS worktree | `~/dev/ssx3-work/N8D7F/parallel-gs`, HEAD `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd` |
| Reference stream | N8D7M6 `n8d7m6.gs`, SHA `f6a78f71…a593`, 1,100,696,462 B, `PS2XGSC1`, 862,958 packets / 11,499 priv / 25,445 transfers / 2,050 markers / 0 readbacks / 0 clears, EOF marker tick 2050 (N8D7M6 REPORT §2, `comparison.json` `last=[4,2050]`, ORCH-GATE) |
| Mac replay binary | N8D7M5 `ps2x_tests` (N8D7M6 REPORT §3 cites `d06ff1aa…0b77f`; `accept.py:240-250` env) |
| Android APK | N8D7M1 `e077bef8…758a1`, 153,736,732 B; arm64 runner `f3de999a…81e3c1bf` (139,497,400 B); Turnip `717812c3…1ac29d` (14,188,488 B); HAL `1b49d27c…fc387` (7,112 B) (N8D7M1 REPORT §§1,4) |
| Repo HEAD (receipts only) | read at commit time by `check.py` (not pinned here) |

## 2. Option matrix — (A) NativeActivity replay mode vs (B) headless arm64 executable

| Row | (A) dev-only NativeActivity replay mode — CHOSEN | (B) headless arm64 executable — REJECTED |
| --- | --- | --- |
| Binary form | No new binary form. Same `ps2EntryRunner` SHARED lib (`ps2xRuntime/CMakeLists.txt:579-581`); Android Gradle builds only target `ps2EntryRunner` (`android/app/build.gradle:42`) | New `add_executable` arm64 target. `ps2xRuntime/CMakeLists.txt:584-588` builds an executable only when NOT Android; Android gets only the SHARED lib. No executable target, PIE wiring, or packaging rule exists today |
| Entrypoint | The one proven launch path: manifest `android.app.NativeActivity` with `android.app.lib_name = ps2EntryRunner` (`android/app/src/main/AndroidManifest.xml:9-19`). N8D7M6 proved this path reaches tick 2050 on the Odin (PID 6028, N8D7M6 REPORT §2). Change = a dev-only env-gated branch at the top of `main()` (`ps2xRuntime/src/main.cpp:193-197`, after `redirectStdioToLogcat`, before `runtime.initialize()` at `:246`), running replay instead of `loadELF`/`run` (`:252-280`) when the new key is set; key absent = byte-identical boot path (default off) | No entrypoint exists: no `android_main`, no second activity, no shell entry in the APK (A1/A2/A5 per N8D7M10 §2). APK native members are exactly the three `.so` files (N8D7M1 REPORT §4); executables cannot ride in `lib/arm64-v8a/`. Delivery would need assets + copy + chmod + exec from the files dir — no precedent in tree or receipts |
| NDK link set | Unchanged: `ps2EntryRunner` links `ps2_runtime` (+ game objects) (`ps2xRuntime/CMakeLists.txt:635-654`); `PS2X_HAS_PARALLEL_SHADOW=1` is PUBLIC on `ps2_gs_shadow` when `PS2X_GS_SHADOW_PARALLEL=ON` (`:510-521`), and the N8D7M1 cache confirms ON (N8D7M1 REPORT §4). Replay core moves into `ps2_runtime`, so both `ps2x_tests` and the app link it with zero new third-party deps | Unproven link closure: a standalone executable would need Granite + paraLLEl + Turnip-HAL link lines that exist today only inside the app `.so` graph (shadow links `parallel-gs` at `:517-518`; Turnip is `dlopen`ed at runtime, not linked). No source row shows an executable linking this graph on Android |
| ABI | arm64-v8a only, already enforced (`android/app/build.gradle:46-48`); Turnip `HalDevice` asserts arm64 layout (`ps2_gs_parallel_backend.cpp:315-320`) | Same ABI requirement, but no built artifact proves an executable satisfies it on-device |
| Input path | Proven app-readable/writable FILES dir `/storage/emulated/0/Android/data/com.ps2x.runner/files` (`local/research/N8D7M6/launch.py:31-32`): the live run wrote the 1.10 GB capture there (`CAPTURE`, `:32,571-572`), pushed `ps2x.env` there (`:582`), and pulled frames from a subdir there (`:436-461`). Replay input = same dir (`n8d7m6.gs`), opened with the same `fopen(path,"rb")` + `PS2XGSC1` check the desktop replay uses (`ps2xTest/src/ps2_gs_replay_tests.cpp:147-166`) | Same FILES dir would be the only candidate, but exec-from-files-dir (NX/SELinux) plus `adb shell` launch identity are both unproved from source strings alone. Flagged, not invented: no push/copy path is specified beyond "the proven FILES channel" (§5) |
| Env / permission | Proven: `<files dir>/ps2x.env` (`KEY=VALUE`, `#` comments) read by static init before `main()` reads anything (`ps2xRuntime/src/lib/ps2_android_runtime.cpp:13-36`), path derived from `PS2X_DEFAULT_BOOT_ELF`'s dir (`ps2xRuntime/include/ps2_android_env.h:76-91`, parser `:42-74`). N8D7M6 drove every flag (incl. `PS2X_GS_CAPTURE`, `PS2X_GS_TURNIP=1`, selected/oracle) through it (`launch.py:573-580`). Manifest declares zero `uses-permission` (whole `AndroidManifest.xml`, 27 lines) yet the live run wrote 1.10 GB + frames there — app-specific storage needs no permission, proved by execution | Env delivery unproved: no NativeActivity means no intent, and the `ps2x.env` shim keys off the boot-ELF dir which an executable would not share. Would need new argv/env plumbing with no precedent |
| Turnip loader reuse | Identical in-process path the gated live run already executed: `PS2X_GS_TURNIP=1` → `initTurnipLoader()` (`ps2_gs_parallel_backend.cpp:927-933`) → `dlopen("libvulkan_freedreno.so")` (`:324`) → `dlsym(HMI)` (`:332`) → HAL `open(hmi,"vulkan0")` (`:355`) → `Context::init_loader(getInstanceProcAddr)` (`:379`), then `init_instance_and_device` (`:944`) and `GSInterface::init` (`:949-951`). Same APK members (N8D7M1 §4). Desktop contrast only: Mac shadow uses system loader `init_loader(nullptr)` (`ps2_gs_shadow.cpp:144-151`); Android uses the Turnip branch | Loader context unproved outside the app process (N8D7M10 gap G3, carried): whether `dlopen("libvulkan_freedreno.so")` + HMI resolves identically from a files-dir executable is not answerable from source strings |
| Nonperturbation gate | Trivial and exact: new key absent → `main()` falls through to the existing `initialize`/`loadELF`/`run` sequence unchanged; key present → EE thread never spawns. Same-binary ON/OFF control within each platform (§6) | Cannot gate nonperturbation: a new binary is a different binary; "OFF" would mean shipping the old APK, which proves nothing about the harness |
| Verdict | **Implementable, bounded, grounded on all four points** (entrypoint, source split §3, input §5, loader above) → outcome A | **Three of four points unproved** (entrypoint, link/loader, env/exec) → rejected; smallest validation that could revive it is a read-only packaging probe (§8 G3), not a boot |

## 3. Parser factoring — what moves, what stays (no MiniTest import)

The only replay implementation is `ps2xTest/src/ps2_gs_replay_tests.cpp`
(721 lines) driven by MiniTest (`:693-721`, registered at
`ps2xTest/src/main.cpp:22,67`, run at `:89`). Its includes are
`MiniTest.h`, `gs_frontend.h`, `gs_cpu_backend.h`,
`ps2_gs_parallel_backend.h`, `ps2_memory.h`, `ps2_vq.h` (`:1-6`).
`MiniTest.h` itself is 211 lines — small, but it must not ship in the
app: the file's only test-harness uses are `t.IsTrue(...)` asserts and
the `replay(TestCase &t)` signature (`:145`), plus the two unit checks
(`:697-717`) and the `MiniTest::Case` wrapper (`:693-696`).

Factorable core (pure stdlib + `GS` frontend + parallel backend, no
MiniTest symbol):

| Piece | Lines | Moves? |
| --- | --- | --- |
| `readEvent` (length-prefixed record framing, EOF vs Invalid) | `:32-44` | Moves verbatim |
| `setPriv` / `privHash` / `presentHash` / `dumpTick` | `:66-102`, `:104-123`, `:125-143` | Move verbatim |
| `ScopedReplayRtz` (RTZ scope for PATH1/all) | `:46-64` | Moves verbatim |
| Env intake: `PS2X_GS_REPLAY_CAPTURE`, `PS2XGSC1` magic, `PS2X_GS_REPLAY_MODE/BACKEND/DROP_PRIV/RTZ/PATH_FILE/STEP` | `:145-208` | Moves; on-device the new mode key selects this instead of `PS2X_GS_REPLAY_BACKEND=parallel` + `MODE=queue` split (queued forced true when parallel, `:168-171`) |
| GS setup: `GS::init`, `setQueueEnabled`, `ps2x_gs_parallel::available/create` gate | `:210-226` (backend API `ps2_gs_parallel_backend.h:26-37`, impl `ps2_gs_parallel_backend.cpp:1028-1054`) | Moves; identical call sequence on-device |
| Record loop kinds 1/2/3/4/5/6/7 incl. recorded-path use (`rec[9]` unless `PATH_FILE` override, `:346-347`), priv apply (`:402-408`), transfer audit (`:410-420`), marker + `drainQueue` + `vsyncTick` store + sampled/named presents (`:421-499`), native upload (`:500-553`), readback compare (`:554-577`), clear (`:578-611`) | `:317-617` | Moves verbatim; the N8D7M5 watch/`PS2X_GS_REPLAY_WORDS` block (`:238-315`, `:357-387`, `:619-632`) is desktop-only and stays out (guarded off by unset env) |
| Summary + stats + OUT/EXPECT compare | `:634-690` | Moves with `t.IsTrue` replaced by a result struct + stderr lines (`GB4_REPLAY_SUMMARY` format kept so Mac controls compare line-for-line) |
| `MiniTest::Case` + tmpfile unit test + `replay(TestCase&)` wrapper | `:693-721` | Stays in `ps2xTest`; thin wrapper calls the moved core |

New files (unexecuted plan, §7): `ps2xRuntime/.../gs_replay_core.{h,cpp}`
returning `{packets, priv, transfers, markers, readbacks, clears,
parseOk, rows}` and writing existing `GB4_*`/`[n8d7f]`/`[n8d7l]` lines
to stderr (logcat on-device); `main.cpp` gains ~15 lines branching on
the new key. No game-thread, EE, VIF, VU, or presenter code is touched.

## 4. Backend + tick2050 invocation (unchanged code, same env)

- Backend object: `ps2x_gs_parallel::create(&regs)` returns the live
  `GSParallelBackend` under `PS2X_HAS_PARALLEL_SHADOW` (`ps2_gs_parallel_backend.cpp:1046-1054`),
  attached via `GS::setRasterBackend` (`gs_frontend.h:127`); `GS`
  exposes `processGIFPacket`, `uploadImageNative`, `privWrite`,
  `drainQueue`, `presentForDiagnostics` (`gs_frontend.h:133-199`).
- Tick2050 gate: `Present` sets `selectedRequested` iff
  `request.vsyncTick == 2050` and `PS2X_N8D7F_SELECTED_CAPTURE==1`
  (`ps2_gs_parallel_backend.cpp:439-446`); the replay stores each
  marker tick into `regs.vsyncTick` (`ps2_gs_replay_tests.cpp:428-430`),
  so the recorded EOF marker at 2050 fires the identical path that
  produced the gated Mac/Odin censuses.
- Census preserved: selected 11-field line + `bytes=/vram_sha256/input_sha256/circuit_sha256`
  (`:603-613`, `:647-651`), `input/circuit/stage` 448-vectors
  (`selectedTileCounts` `:64-81`, log `:83-98`), shared decoder
  `selectedDecode` (`:100-156`), oracle gated by `PS2X_N8D7L_ORACLE==1`
  (`:667-668`) with `oracleDecodeCensus`, 8 controls, `oracle_input_equal`
  (`:669-729`). Full 4 MiB mapped snapshot + 448-tile census, same-source
  decoder on both platforms.
- Stream fidelity preserved: recorded path byte per packet
  (capture writes it at `gs_stream_capture.cpp:153-161`; replay honors
  it at `ps2_gs_replay_tests.cpp:346-347` with no `PATH_FILE` override
  in the gated run — N8D7M10 §2), priv/transfer/marker order and kinds
  (`:336-617`), original `GSPresentationRequest` descriptor
  (`gs_types.h:277-291`, priv synced in-stream at
  `ps2_gs_parallel_backend.cpp:985-1012`).

## 5. Data staging (app-readable, outside git, budgeted)

- Input: the exact `f6a78f71…a593` bytes as `n8d7m6.gs` in the FILES dir
  (§2 row 5). Outside git (never committed; N8D7M6 kept it in
  `~/dev/ssx3-work/N8D7M6/` scratch, REPORT §6).
- Proof of channel: capture written there, `ps2x.env` pushed there,
  frames pulled from there (cites in §2). Manifest needs no new
  permission (zero `uses-permission`, proved sufficient by the 1.10 GB
  live write).
- Integrity: two matching SHA reads before use on-device and two after
  pull, following `launch.py:123-130` (`check_device_sha`) and
  `:463-481` (`pull_capture`); any pair mismatch voids the run.
- Budget: stream 1,100,696,462 B + ~5 MiB census text + one 512×448
  frame; device gate keeps N8D7M6's `free ≥ 10 GiB`
  (`launch.py:113,118-120`; preflight saw ~25.9 GB, N8D7M6 REPORT §2).
  No `adb push` path is invented here: the staging command is listed
  unexecuted in §7 and no copy was made in this part (brief stop rule).
- Run caps (prospective, from `launch.py` precedent): one Odin lease
  (`/data/local/tmp/mg/LEASE`), battery ≥20% + charging (status 2/5),
  keyguard `showing=false` before launch, `install -r` every run, one
  launch, BACK once for the USB dialog, ≤600 s wall cap, `am force-stop`
  + lease-free + logcat close after each run, logs ≤16 MiB, text
  receipts <512 KiB.

## 6. Prospective diagnostic comparison (conditional, not run)

Conditional on the §3–§5 harness, identical `f6a78f71…a593` bytes (two
matching SHAs), identical 11-field descriptor + Odin input byte hash,
same-source decoder both sides, same-binary ON/OFF control within each
platform (replay binary with selected/oracle flags on vs off; Mac
`ps2x_tests` same pair), and a viewed tick2050 Odin frame. Active =
448-tile active count; no speed number from any diagnostic replay
(AGENTS.md speed rule; N8D7M6 REPORT §5).

| Branch | Predeclared requirement | Lead (not a proved cause) | Cannot conclude |
| --- | --- | --- | --- |
| Odin offline broad ≥250/448, near Mac 300 | All conditionals above hold | Live-only EE→GS scheduling/interleave becomes a lead | Faulty packet, copy timing, per-draw completion (N8D7M8 M5, N8D7M9 §4), 120 Hz speed |
| Odin offline sparse ≤100/448, near live 23 | Same | Device/backend/driver path (Turnip/Granite/Adreno execution of this stream) becomes a lead; no shader/barrier cause claimed | Same four |
| 101–249, or descriptor/hash/path mismatch, or harness difference | Any | OTHER: void; diagnose harness/descriptor first | Nothing |

Controls/stop table (prospective run): stop at first complete tick2050
receipt + frame + closed census; void on any tile-probe error, control
≠128/128 PASS, `GB4_REPLAY_PARSE_ERROR`, marker ≠2050, or elapsed >600 s.
Mac same-binary control must stay broad or the comparison is OTHER.

## 7. Unexecuted patch/command plan (exact, not executed)

Patch (no implementation authorized here):

1. New `ps2xRuntime/src/lib/gs/gs_replay_core.{h,cpp}`: §3 "moves"
   rows verbatim, `MiniTest` asserts → result struct + stderr lines.
2. `ps2xRuntime/CMakeLists.txt`: compile the core into `ps2_runtime`
   (one `target_sources` hunk, no flag changes; `PS2X_GS_SHADOW_PARALLEL`
   wiring at `:510-524` untouched).
3. `ps2xRuntime/src/main.cpp`: after `redirectStdioToLogcat()`
   (`:195-197`), `if (getenv("PS2X_GS_REPLAY_ONDEVICE")==1) {
   return ps2x_gs_replay_run(); }` before `runtime.initialize()`
   (`:246`); default off (unset → existing path untouched).
4. `ps2xTest/src/ps2_gs_replay_tests.cpp`: `replay()` becomes a wrapper
   over the core (keeps `MiniTest::Case`, `:693-721`).
5. No manifest, Gradle, Turnip, HAL, or game-code change.

Commands (prospective, none executed):

```sh
# build (bytesize WSL, N8D7M1 build.sh shape; DIAG_TAPS/RUNTIME_LOGS/
# AGRESSIVE_LOGS/IOP_RPC_TRACE/DEBUG_UI OFF for any quoted number)
# stage exact bytes to FILES (two SHA reads each side before use)
# install -r app-release.apk; preflight (keyguard/battery≥20%/free≥10GiB/lease);
# one launch; stop at tick2050 receipt+frame+census; pull; force-stop; free lease
```

## 8. Costs, gaps, outcome

Costs: this part = reads only, text <512 KiB (see `check-result.json`);
a future implementation = one code review + one diagnostics-off build;
a future device run = one install + one launch ≤600 s (§5 caps).

Gaps:

- G1 (carried, N8D7M10 G3): source strings cannot prove the Turnip/HMI
  loader behaves identically in replay-mode process startup vs the
  proven game-boot path — same `.so`, same call sequence, but runtime
  proof needs the gated run. Forces OTHER for any comparison until the
  ON/OFF control passes.
- G2 (staging unproved): the 1.10 GB stream has never been staged back
  to the FILES dir; two-matching-SHA staging is a plan, not a receipt.
- G3 (option-B-only, closed by rejection): executable packaging,
  files-dir exec permission, linker/loader reuse, and non-app env
  delivery are unproved; smallest read-only validation if ever revived
  = cite an NDK executable target + APK asset→exec precedent, still no
  device action.
- G4 (inherited, not needed for this verdict): N8D7M9 G5 prim-array
  bound, M4 Turnip timestamp support; per-draw completion stays
  unattributed even after a faithful replay (N8D7M8/N8D7M9 gates).

**Outcome A**: implementable bounded harness = choice (A), dev-only
NativeActivity replay mode, with grounded entrypoint (§2), source split
(§3), app-readable input + Turnip loader path (§§2,5), and
predeclared controls/stops (§6). Neither branch proves the faulty
packet, copy timing, or 120 Hz speed.

## 9. Receipts / commands (all read-only, repo root unless noted)

Reads: this brief; `~/dev/AGENTS.md`; repo `AGENTS.md`;
`local/AGENTS.local.md`; N8D7M6 `REPORT.md` + `ORCH-GATE.md` +
`comparison.json` + `launch.py` + `accept.py`; N8D7M10 `REPORT.md` +
`ORCH-GATE.md`; N8D7M1 `REPORT.md`; `docs/todo.md` N8D7M11 row. Sources
(direct reads at `a8cfefa` / `3a66c19`): `ps2xTest/src/ps2_gs_replay_tests.cpp:1-16,32-143,145-229,238-499,500-617,634-721`,
`ps2xTest/src/main.cpp:22,67,89`, `ps2xTest/CMakeLists.txt:154-178`,
`ps2xTest/include/MiniTest.h` (211 lines),
`ps2xRuntime/include/runtime/gs/gs_frontend.h:103-199`,
`ps2xRuntime/include/runtime/gs/gs_types.h:277-306`,
`ps2xRuntime/include/runtime/gs/gs_backend.h:8-52`,
`ps2xRuntime/include/runtime/gs/ps2_gs_parallel_backend.h:26-37`,
`ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp:60-156,300-379,430-446,600-729,900-963,985-1054`,
`ps2xRuntime/src/lib/gs/gs_stream_capture.cpp:27-42,135-161,242-265`,
`ps2xRuntime/src/lib/gs/ps2_gs_shadow.cpp:140-151`,
`ps2xRuntime/src/lib/ps2_android_runtime.cpp:13-48`,
`ps2xRuntime/include/ps2_android_env.h:42-91`,
`ps2xRuntime/src/main.cpp:160-280`, `ps2xRuntime/CMakeLists.txt:500-524,578-588,635-655`,
`android/app/build.gradle:1-75`,
`android/app/src/main/AndroidManifest.xml` (all 27 lines). `git
rev-parse` in both worktrees for pins. New text <512 KiB (see
`check-result.json`).

(End of file)
