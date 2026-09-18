# P1 report — Mac (arm64) PS2Recomp re-spike

Stopped at the Step 1 gate (ISO sha1 mismatch). No verdicts are given below;
each table reports the recorded value or states the step was not run.

## 0. Gate outcome

| Item | Value |
|---|---|
| Brief ISO source path | `/Volumes/share/brad/games/SSX 3 (USA).iso` |
| Brief path exists | No (`No such file or directory`) |
| Actual source used | `/Volumes/share/brad/games/ps2/SSX 3 (USA).iso` (only `SSX 3 (USA).iso` found on the share) |
| SSD copy | `/Volumes/Extreme SSD/ps2recomp-spike/SSX 3 (USA).iso` |
| Copy size (SSD) | 3005415424 bytes |
| Copy size (share original) | 3005415424 bytes |
| Spike transcript ISO size ([0]) | 3005415424 bytes |
| `file` on SSD copy | `UDF filesystem data (version 1.5) 'SSX3'` |
| Expected sha1 (brief) | `77114dfd1205eaccf1ccc18c5f9650097fa78bd8` |
| Actual sha1, run 1 (SSD copy) | `667c9b2bbfef45ca3f89a55aab296701916120f6` |
| Actual sha1, run 2 (SSD copy, re-read) | `667c9b2bbfef45ca3f89a55aab296701916120f6` |
| Gate action | Stopped. Steps 2–7 not run. |

## 1. Environment table

| Item | Value |
|---|---|
| Host | `Darwin brads.macbook.air.lan 27.0.0 Darwin Kernel Version 27.0.0 … RELEASE_ARM64_T8132 arm64` |
| OS | macOS 27.0 (Build 26A428) |
| CPU | Apple M4 (`hw.optional.arm64 = 1`) |
| `cmake --version` | `cmake version 4.4.3` |
| `clang --version` | `Apple clang version 21.0.0 (clang-2100.3.34.2), Target: arm64-apple-darwin27.0.0` |
| `ninja --version` | `1.13.2` |
| Repo HEAD (ssx3) | `c7150168840576528b3ca64c397e4bbbbdb95691` |
| Work dir (SSD) | `/Volumes/Extreme SSD/ps2recomp-spike/` (`P1/` subdirectory created, empty) |
| Link dir | `/tmp/p1-link/` (created, unused — no build was started) |
| Host lease | Never acquired (no build or boot was started); `/tmp/ssx3-host-lease` absent during all P1 work; at 12:28 EDT, after the P1 commit, a foreign lease `S2b-build` was observed and left untouched; no waits, no `waits.log` |
| Wall start | 2026-09-18 16:26:07 UTC (Fri Sep 18 12:26:07 EDT 2026) |
| Homebrew installs | None (cmake/ninja present, nothing installed) |
| `adb` | Not used |

## 2. Census table (Step 4 — not run)

| Item | Expected (brief) | Actual |
|---|---|---|
| Microprograms | 7 | Not run (stopped at Step 1) |
| Instructions | 7,305 | Not run |
| Unimplemented encodings | 0 | Not run |
| Distinct ops | 85 | Not run |
| Receipt `vu1-census.txt` | `$W/P1/vu1-census.txt` | Not produced |

## 3. Recompile summary table (Step 5 — not run)

| Item | Expected (brief) | Actual |
|---|---|---|
| Functions discovered | 8143 | Not run |
| Functions processed | 8143 | Not run |
| Recompiled | 8017 | Not run |
| Stubs | 126 | Not run |
| Skipped | 0 | Not run |
| Decode failures | 0 | Not run |
| Unhandled instructions | 0 | Not run |
| `unresolved JR/JALR` warnings | 3,594 | Not run |
| Promoted fallback entries | 724,768 (spike [49]) | Not run |
| Receipts (`analyzer.log`, `recomp.log`, output listing, stub list) | `$W/P1/` | Not produced |
| Tool receipts (`file`, sha256, `$W/P1/bin/`) | Step 3 | Not produced (no build) |

## 4. Runtime build outcome (Step 6 — not attempted)

Not attempted. No configure, no build, no `configure-runtime.log` /
`build-runtime.log`, no `ps2xTest` run, no boot attempt, no `boot.log`.
No lease was taken. No runtime or TOML changes were made; there is no diff.

## 5. Boot ladder (Step 6 — not reached)

| Rung | Reached |
|---|---|
| Process start | No (no binary built) |
| First syscall | No |
| First CD read | No |
| First `MSCAL` | No |
| First GS kick | No |
| First presented frame | No |
| First crash message | None (nothing launched) |

## 6. Diff of any changes

None. No file outside `local/research/P1/` was modified; no file under
`/Volumes/Extreme SSD/ps2recomp-spike/` besides the ISO copy and the empty
`P1/` directory was written.

## 7. GS inventory (Step 7 — not run, read-only step blocked on Step 2 clone)

| File | Size | Public functions | TODO/unimplemented strings |
|---|---|---|---|
| `ps2xRuntime/src/lib/gs/gs_frontend.cpp` | Not read (repo not cloned) | Not listed | Not listed |
| `ps2xRuntime/src/lib/gs/gs_cpu_backend.cpp` | Not read | Not listed | Not listed |
| `ps2xRuntime/src/lib/gs/ps2_gs_memory.cpp` | Not read | Not listed | Not listed |
| `ps2xRuntime/src/lib/gs/ps2_gif_arbiter.cpp` | Not read | Not listed | Not listed |

## 8. Exact commands used

From `/Users/bradrichardson/dev/ssx3`:

```
mkdir -p "local/research/P1"
mkdir -p "/Volumes/Extreme SSD/ps2recomp-spike/P1"
mkdir -p /tmp/p1-link
ls -la "/Volumes/Extreme SSD/"
ls -la /Volumes/
ls -lh "/Volumes/share/brad/games/"
ls -lhR "/Volumes/share/brad/games/ps2"
ls -lhR "/Volumes/share/brad/games/ssx3-workbench"
find "/Volumes/share" -maxdepth 4 -iname "*ssx*"
ls -lh "/Volumes/share/brad/games/SSX 3 (USA).iso"   # not found
cp "/Volumes/share/brad/games/ps2/SSX 3 (USA).iso" "/Volumes/Extreme SSD/ps2recomp-spike/SSX 3 (USA).iso"
ls -lh "/Volumes/Extreme SSD/ps2recomp-spike/SSX 3 (USA).iso"
shasum -a 1 "/Volumes/Extreme SSD/ps2recomp-spike/SSX 3 (USA).iso"   # run twice, same result
ls -l "/Volumes/Extreme SSD/ps2recomp-spike/SSX 3 (USA).iso" "/Volumes/share/brad/games/ps2/SSX 3 (USA).iso"
stat -f "%z %N" "/Volumes/Extreme SSD/ps2recomp-spike/SSX 3 (USA).iso" "/Volumes/share/brad/games/ps2/SSX 3 (USA).iso"
file "/Volumes/Extreme SSD/ps2recomp-spike/SSX 3 (USA).iso"
uname -a; sw_vers; sysctl -n machdep.cpu.brand_string; sysctl -n hw.optional.arm64
cmake --version; clang --version; ninja --version
git log -1 --format="%H %s"
git status --porcelain
cat /tmp/ssx3-host-lease   # absent
```

Transcript reads (no writes): `local/muse/prompts/P1.md`,
`docs/research/ps2recomp-spike-2026-09-12/commands-and-outputs.md`,
`docs/research/ps2recomp-spike-2026-09-12/README.md`,
`docs/research/ps2recomp-spike-2026-09-12/scripts/{final_census,census,parse_vif,histogram}.py`.

## 9. Receipts paths and shas

| Path | Kind | Hash / value |
|---|---|---|
| `/Volumes/Extreme SSD/ps2recomp-spike/SSX 3 (USA).iso` | ISO copy (3,005,415,424 B) | sha1 `667c9b2bbfef45ca3f89a55aab296701916120f6` (two runs) |
| `/Volumes/Extreme SSD/ps2recomp-spike/P1/` | Work dir | Empty (no receipts; stopped before Step 2) |
| `local/research/P1/REPORT.md` | This report | Committed under `[P1]` (see git log) |
| `/tmp/p1-link/` | Link dir | Created, unused |
| `/tmp/ssx3-host-lease` | Lease | Absent during P1 work (never acquired, nothing to release); foreign `S2b-build` seen post-commit, untouched |

## 10. What I could not do

- Step 2 (clone + pin `14b1e5cb`), Step 3 (build `ps2_recomp`/`ps2_analyzer`),
  Step 4 (extract `SLUS_207.72` + VU1 census), Step 5 (analyze + recompile),
  Step 6 (runtime build + `ps2xTest` + boot), Step 7 (GS inventory): all
  not run because the Step 1 gate (`Stop if it differs`) triggered on the
  sha1 mismatch recorded in section 0.
- Two deviations from the brief text are recorded, not resolved:
  (a) the brief's ISO source path does not exist; the ISO was copied from
  `ps2/` subdirectory; (b) the measured sha1 differs from the expected sha1.
- The SSD copy (3,005,415,424 bytes, UDF label `SSX3`) matches the spike
  transcript's ISO byte size ([0]); the share original has the identical
  byte size. The SSD copy was not hashed before copying (the share was read
  once, per the brief's note that the SMB share is slow to read twice).

---

# P1 report — Part 2 (resumed steps 2–8, 2026-09-18)

Resume note: Step 1 corrected — the measured ISO sha1 `667c9b2b…` is the
right ISO hash; `77114dfd…` is the `SLUS_207.72` sha1, checked in Step 4.
The SSD ISO copy was reused as-is. Wall for Part 2: 12:45 → 13:40 EDT
(2026-09-18 16:45 → 17:40 UTC). Step 6 used ~50 min of its 90-min box.
No verdicts are given; tables report recorded values.

## P2-0. Step 1 correction check

| Item | Value |
|---|---|
| `$W/P1/SLUS_207.72` sha1 | `77114dfd1205eaccf1ccc18c5f9650097fa78bd8` (matches corrected hash) |
| `$W/P1/SLUS_207.72` sha256 | `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc` |
| `$W/P1/SLUS_207.72` size | 3,890,784 bytes |
| `$W/P1/SYSTEM.CNF` size | 49 bytes, `BOOT2=cdrom0:\SLUS_207.72;1`, `VER=1.00`, `VMODE=NTSC` |
| ELF header | entry `0x00100008`, 1 program header (type 1, off `0x1000`, vaddr `0x00100000`, filesz 3820532, memsz 4451036, flags 7) |

## P2-1. Environment addendum (Step 2)

| Item | Value |
|---|---|
| Clone | `git clone https://github.com/ran-j/PS2Recomp.git "$W/PS2Recomp"`, exit 0 |
| Pin | `git checkout 14b1e5cb` → `14b1e5cb39b4af7e6fc12f9a29fdc751efde49d7` ("Start the main thread with COP0 Status.IE set (#214)", 2026-08-19) |
| `cmake --version` | `cmake version 4.4.3` |
| `clang --version` | `Apple clang version 21.0.0 (clang-2100.3.34.2)` |
| `ninja --version` | `1.13.2` |
| Homebrew installs | None |
| ExFAT note | The SSD volume creates AppleDouble `._*` sidecars on file write; CMake/Ninja globs (`*.cpp`) match `._*.cpp`, which broke the first tools build (12 failed targets, "source file is not valid UTF-8"). Fix: `find … -name "._*" -delete` under `$W/PS2Recomp` (+ `COPYFILE_DISABLE=1`, `cp -X` for copies), reconfigure, rebuild. Sidecars were purged again before each subsequent build and at the end. No source file was edited for this. |

## P2-2. Lease record (Steps 3–6)

| Event | Value |
|---|---|
| Pre-build check | `/tmp/ssx3-host-lease` absent |
| Acquired | `printf 'P1-build' > /tmp/ssx3-host-lease` before Step 3 build |
| Boot | `printf 'P1' > /tmp/ssx3-host-lease` before boot attempts |
| Released | `rm /tmp/ssx3-host-lease` after last run; verified absent |
| Foreign leases | None encountered during Part 2; no waits, no `waits.log` |
| `adb` | Not used |

## P2-3. Tools build receipts (Step 3)

| Item | Value |
|---|---|
| Configure | `cmake -S "$W/PS2Recomp" -B /tmp/p1-link/tools -G Ninja -DPS2X_BUILD_STUDIO=OFF -DPS2X_BUILD_RUNTIME=OFF -DPS2X_BUILD_TEST=OFF -DCMAKE_BUILD_TYPE=Release`, exit 0 (`configure-tools.log`; attempt 1 + attempt 2 after sidecar purge appended in one file) |
| Build | `cmake --build /tmp/p1-link/tools`, exit 0 (`build-tools.log`) |
| `file ps2_recomp` | `Mach-O 64-bit executable arm64` |
| `file ps2_analyzer` | `Mach-O 64-bit executable arm64` |
| sha256 `/tmp/p1-link/tools/ps2xRecomp/ps2_recomp` | `7654e7fe4a7316476dfcc00a418c850bd8ecffeb301b345624500304e22e826f` |
| sha256 `/tmp/p1-link/tools/ps2xAnalyzer/ps2_analyzer` | `4bf4ba2bdb5af44c002013ef26ca9d65aab696228dfbb22b305708bd8b3e699f` |
| Copied to `$W/P1/bin/`, re-sha | Identical shas on both sides (13M `ps2_analyzer`, 1.5M `ps2_recomp`) |

## P2-4. Census table (Step 4)

Decoder note: the recovered `scripts/histogram.py` is the spike's
`edit_file` JSON fragment, not the decoder body (the `/tmp/ssx3vu` tree was
lost and the transcript never reprints the classifier). `census.py`,
`final_census.py`, `parse_vif.py` were copied unmodified to
`$W/P1/ssx3vu/` (with `/tmp/ssx3vu` symlinked to that dir so their hardcoded
paths resolve onto the SSD); the recovered fragment is kept alongside as
`histogram-recovered-fragment.py`. `histogram.py` was reconstructed as an
I-bit-aware mirror of the pinned `VU1Interpreter` (`execUpper`,
`execLower`, `decodeUpperUsage`, `decodeInstructionPair` in
`ps2xRuntime/src/lib/vu/`; I-bit = upper bit 31, E-bit = upper bit 30;
explicit lower NOP for `0x00000000`/`0x8000033C`; upper zero-word → `U:NOP`).
Section dump (spike command [19]) reproduced exactly: `.vutext` 59,360 B,
`.vudata` 0 B, `.DVP` 1,557 B, 32 `.DVP.overlay.*` sections (all verified
zero-length content listing identical to the spike).

| Item | Expected | Actual |
|---|---|---|
| Microprograms | 7 | 7 |
| MPG packets | 32 (spike) | 32 |
| Instructions | 7,305 | 7,305 |
| Unimplemented encodings | 0 | 0 |
| Distinct ops | 85 | 85 |
| Per-program (instr / E-bits / LOI / reserved / distinct) | spike [33] | P0 1172/15/1/0/53, P1 2005/7/1/0/61, P2 576/9/4/0/44, P3 1985/13/5/0/71, P4 804/9/28/0/52, P5 275/2/4/0/41, P6 488/17/1/0/40 — all match |
| VU1-specialty counts | spike [33] | XGKICK 47, XTOP 62, XITOP 2, CLIP 120, DIV 125, RSQRT 31, RNEXT 53, RINIT 29, ERLENG 1, ESIN 9, WAITP 2, WAITQ 37, MFP 11 — all match |
| Full 85-tag table | spike [33] | Programmatic diff of all 85 tag counts: 0 missing, 0 extra, 0 count diffs — MATCH |
| Receipt | `$W/P1/vu1-census.txt` | Written (tee of `final_census.py` output) |

## P2-5. Recompile summary table (Step 5)

Commands (from `$W/P1`): `"$W/P1/bin/ps2_analyzer" SLUS_207.72 ssx3.toml`
(`analyzer.log`, exit 0); `"$W/P1/bin/ps2_recomp" ssx3.toml` (`recomp.log`,
exit 0). Analyzer console: 180 library functions to stub, 359 detected
without runtime handlers, 0 patches, 0 jump tables — as the spike.

| Item | Expected | Actual |
|---|---|---|
| Functions discovered | 8143 | 8143 |
| Functions processed | 8143 | 8143 |
| Recompiled | 8017 | 8017 |
| Stubs | 126 | 126 |
| Skipped | 0 | 0 |
| Decode failures | 0 | 0 |
| Unhandled instructions | 0 | 0 |
| Additional entrypoints | 391,176 (spike [49]) | 391,176 |
| `unresolved JR/JALR` warnings | 3,594 | 3,594 |
| Promoted fallback entries | 724,768 (spike [49]) | 724,768 |
| TOML `stubs` entries | 180 (spike console) | 180 (`sceGsResetGraph@0x003FD910` … `InitTLB@0x0042CD58`) |
| TOML `untracked_stubs` entries | — | 391 (informational; recompiled normally) |
| TOML `skip` entries | — | 0 |
| Total `@0x` bindings | 571 (spike [46]) | 571 |
| Output files | 8,146 (spike [48]) | 8,146 (8,143 `sub_*.cpp` + `ps2_recompiled_functions.h` + `ps2_recompiled_stubs.h` + `register_functions.cpp`); 8,144 `.cpp` files; 1 file with TODO (`register_functions.cpp`, the generated dup-comment) |
| Output dir size | — | `du -sh` 16G on ExFAT (cluster slack; largest: `register_functions.cpp` 31M) |
| Receipts | `$W/P1/` | `ssx3.toml` (1,618 lines), `analyzer.log`, `recomp.log`, `output/` |

## P2-6. Runtime build outcome (Step 6)

| Item | Value |
|---|---|
| Configure | `cmake -S "$W/PS2Recomp" -B /tmp/p1-link/runtime -G Ninja -DPS2X_BUILD_STUDIO=OFF -DPS2X_BUILD_RUNTIME=ON -DPS2X_BUILD_TEST=ON -DCMAKE_BUILD_TYPE=Release`, exit 0 (`configure-runtime.log`, 62s; raylib/GLFW configured on macOS with no X11 error; system ffmpeg libs found) |
| Documented fixes for configure/build failure | None needed (0 of the allowed 2 used) |
| Build | `cmake --build /tmp/p1-link/runtime`, exit 0 (`build-runtime.log`): `ps2EntryRunner`, `ps2_recomp`, `ps2x_tests` linked |
| `ps2x_tests` (CWD `$W/PS2Recomp`, needed for `instructions.h` lookup) | Total 425, Passed 425, Failed 0 (`ps2x-tests.log`); suite runs: CodeGenerator 56, ElfAnalyzerHeuristics 6, PS2GS 71, PS2IopSubsystem 7, PS2Memory 45, PS2Recompiler 17, PS2RuntimeExpansion 31, PS2RuntimeIO 11, PS2RuntimeInterrupt 8, PS2RuntimeKernel 31, PS2SifDma 16, PS2SifRpc 15, PS2VU0Math 44, PS2VU1 40, PadInput 12, R5900Decoder 15 (8 individual lines carry interleaved trace output but the binary summary counts them passed) |
| CWD note | One `CodeGenerator` test fails when run from `/tmp` (`instructions.h` not found); passes from the source root. No code change; run location recorded. |

## P2-7. Port build and boot ladder (Step 6, continued)

README path used: "Then build generated output and link with `ps2xRuntime`"
(README `### Usage` + `ps2_runtime.h`: "Generated by ps2xRecomp in
`ps2xRuntime/src/runner/register_functions.cpp"). The runner takes the guest
ELF as argv[1] (`ps2xRuntime/src/main.cpp`: "Using argv boot path" →
`runtime.loadELF` → `runtime.run()`); IO roots (`hostRoot`, `cdRoot`) are set
to the ELF directory (`configureIoPathsFromElf`), so the ISO was supplied as
the extracted ELF in `$W/P1/` (the ISO file itself was not mounted; no
ISO-mount step exists in this path).

| Item | Value |
|---|---|
| Port assembly | `cp -X` of all 8,144 generated `.cpp` + 2 generated `.h` from `$W/P1/output/` into `$W/PS2Recomp/ps2xRuntime/src/runner/` (replacing the 438-byte stub `register_functions.cpp`; stub copy saved as `$W/P1/runner-stub-register_functions.cpp.orig`); `cp -X` still produced `._*` sidecars on this volume, purged before building |
| Port build | `cmake --build /tmp/p1-link/runtime --target ps2EntryRunner`, exit 0 (`build-port.log`; CMake `CONFIGURE_DEPENDS` glob picked up the new sources; unity build) |
| Runtime C++ patches | None (0 one-line stubs used) |
| TOML / IOP-profile changes for boot | None |
| Instrumentation (documented CMake options, not behavior fixes) | Reconfigure + rebuild with `-DPS2X_ENABLE_RUNTIME_LOGS=ON`, then also `-DPS2X_ENABLE_AGRESSIVE_LOGS=ON` (tick ladder); `PS2_FUNCTION_LOG_TRACKER` is defined by that option but consumed nowhere, so no log flood |
| Boot runs | run 1 `boot.log` (48 lines, logs off); run 2 `boot-run2.log` (48 lines, unbuffered re-run); run 3 `boot-run3.log` (49 lines, logs on, ~4 min); run 4 `boot-run4.log` (133 lines: 48 raylib + 6 startup + `[SetupHeap]` + 83 tick lines, ~5.5 min, aggressive logs). Runs 1–4 performed no CD reads and mounted nothing beyond the ELF. Each run was terminated by the operator while the process was healthy (no exit code); no stray `ps2EntryRunner` left running |
| Boot log excerpt (run 4, unbuffered) | `Using argv boot path` / `Loading segment: 0x100000 - 0x53eadc (filesz: 0x3a4bf4, memsz: 0x43eadc)` / `Registered code region: 100000 - 4a4bf4` / `ELF file loaded successfully. Entry point: 0x100008` / `Starting execution at address 0x100008` / `[SetupHeap] base=0x53f115 alignedBase=0x53f120 size=0xffffffff runtimeBase=0x53f120 runtimeEnd=0x53f120` |

Boot ladder:

| Rung | Reached | Evidence |
|---|---|---|
| Process start | Yes | raylib/Cocoa display + audio init in every run |
| ELF load | Yes | `ELF file loaded successfully. Entry point: 0x100008` |
| Execution start | Yes | `Starting execution at address 0x100008`, `[SetupHeap]` |
| First syscall (in code) | Partial | Game thread spins in `sub_0042C1F0` (`0x42c1f0–0x42c2f0`) at `0x42c278 beqz $v0` / `0x42c284 jal func_42C1A8` / `0x42c28c daddu $s3,$v0,$zero`; the JAL path (pc `0x42c28c` sampled) runs `sub_0042C1A8`, whose body issues `syscall 0` (`$v1=0x83`) then `jr $ra` or calls `func_42C120`; `handleSyscall` emits no log line at this log level, so dispatch is unconfirmed in the log |
| First CD read | No | `dma=0` on all 83 ticks; no CD log lines |
| First `MSCAL` | No | `vif=0` on all 83 ticks |
| First GS kick | No | `gif=0`, `gsw=0` on all 83 ticks |
| First presented (game) frame | No | Host window presents blank frames only |
| First crash | None | 83/83 ticks pc ∈ {`0x42c278` (52×), `0x42c28c` (31×)}, `ra=0x42c28c sp=0x1ffff70 gp=0x4a30f0`, 1 active thread, all counters zero; no exception/crash line in any run |

## P2-8. Diff of changes

- `$W/PS2Recomp/ps2xRuntime/src/runner/`: added 8,144 generated `.cpp` + 2 generated `.h`; replaced stub `register_functions.cpp` (original saved at `$W/P1/runner-stub-register_functions.cpp.orig`). No hand edit to any upstream C++ file (a unified diff would be ~8,146 added generated files; omitted for size — file list is `ls $W/P1/output/`).
- No TOML, IOP-profile, or runtime-source change of any kind.
- Build-dir-only flag changes for instrumentation: `PS2X_ENABLE_RUNTIME_LOGS=ON`, then also `PS2X_ENABLE_AGRESSIVE_LOGS=ON` (documented CMake options in `ps2xRuntime/CMakeLists.txt`).

## P2-9. GS inventory (Step 7, read-only; paths `ps2xRuntime/src/lib/gs/`)

| File | Bytes | Lines | Top-level function definitions (grep, `name:line`) |
|---|---|---|---|
| `gs_frontend.cpp` | 57,300 | 1,733 | `GS::GS:108`, `init:114`, `reset:125`, `activeContext:193`, `snapshotVRAM:198`, `lockDisplaySnapshot:213`, `getDebugSnapshot:226`, `getDebugHistory:266`, `clearDebugHistory:280`, `isDebugHistoryPaused:290`, `setDebugHistoryPaused:296`, `makeDebugEventUnlocked:302`, `recordDebugEventUnlocked:323`, `recordGifTagDebugEventUnlocked:353`, `recordRegisterDebugEventUnlocked:368`, `recordDrawDebugEventUnlocked:411`, `recordTransferDebugEventUnlocked:448`, `recordPresentDebugEventUnlocked:460`, `getPreferredDisplaySource:476`, `unlockDisplaySnapshot:491`, `getLastDisplayBaseBytes:496`, `refreshDisplaySnapshot:501`, `buildPresentationRequestUnlocked:506`, `latchHostPresentationFrame:527`, `copyLatchedHostPresentationFrame:578`, `processGIFPacket:641`, `processNativePackedGIFPacket:739`, `uploadImageNative:779`, `uploadImageNativeUnlocked:790`, `tryProcessNativeImageUploadPacket:808`, `writeRegisterPacked:878`, `writeRegister:1062`, `writeRegisterUnlocked:1068`, `vertexKick:1525`, `processImageData:1608`, `clearFramebufferContext:1615`, `clearActiveFramebuffer:1621`, `consumeLocalToHostBytes:1627`, `setRasterBackend:1633`, `ReadVram:1662`, `WriteVram:1668`, `buildDrawBatch:1675`, `updatePreferredDisplaySourceForDraw:1702` |
| `gs_cpu_backend.cpp` | 72,320 | 1,894 | `GSCpuBackend:471`, `Initialize:542`, `Reset:550`, `ResetUnlocked:556`, `Submit:566`, `Flush:574`, `TextureFlush:579`, `Sync:585`, `ReadVram:590`, `ReadVramUnlocked:596`, `WriteVram:603`, `WriteVramUnlocked:609`, `SnapshotVram:616`, `GetTransferSnapshot:628`, `DrawPrimitive:638`, `WritePixel:776`, `LookupCLUT:942`, `SampleTexture:972`, `DrawSprite:1076`, `DrawTriangle:1192`, `DrawLine:1310`, `BeginTransfer:1377`, `UploadImage:1394`, `PerformLocalToLocalTransfer:1501`, `PerformLocalToHostTransfer:1541`, `ConsumeLocalToHostBytes:1611`, `ClearFramebuffer:1623`, `CopyFrameToHostRgba:1682`, `Present:1760`, `PresentFromLocalMemory:1774` |
| `ps2_gs_memory.cpp` | 15,226 | 363 | Namespace `GSMem` pixel-store helpers, no `Class::` definitions: `InitLookupTables:204`, `WriteCT32:223`, `WriteCT24:228`, `WriteZ32:233`, `WriteZ24:238`, `WriteCT16:243`, `WriteCT16S:248`, `WriteZ16:253`, `WriteZ16S:258`, `WriteP8:263`, `WriteP8H:268`, `WriteP4:273`, `WriteP4HL:278`, `WriteP4HH:283`, `WriteNull:288` (+ further per-format read/write helpers below line 288) |
| `ps2_gif_arbiter.cpp` | 2,088 | 68 | `GifArbiter:5`, `isImagePacket:10`, `submit:21`, `drain:35`, `pathPriority:65` |

Marker strings (`TODO|unimplemented|not supported`, case-insensitive, with line numbers):

| File | Hits |
|---|---|
| `gs_frontend.cpp` | 0 |
| `gs_cpu_backend.cpp` | 2 — `284: // TODO: clut cache`, `813: // TODO: only one address lookup for rmw` |
| `ps2_gs_memory.cpp` | 0 |
| `ps2_gif_arbiter.cpp` | 0 |

## P2-10. Exact commands used (Part 2)

```
git clone https://github.com/ran-j/PS2Recomp.git "$W/PS2Recomp"
git -C "$W/PS2Recomp" checkout 14b1e5cb
git -C "$W/PS2Recomp" log -1 --format="%H %ad %s"
cmake --version; clang --version; ninja --version
printf 'P1-build' > /tmp/ssx3-host-lease
cmake -S "$W/PS2Recomp" -B /tmp/p1-link/tools -G Ninja -DPS2X_BUILD_STUDIO=OFF -DPS2X_BUILD_RUNTIME=OFF -DPS2X_BUILD_TEST=OFF -DCMAKE_BUILD_TYPE=Release | tee "$W/P1/configure-tools.log"
cmake --build /tmp/p1-link/tools | tee "$W/P1/build-tools.log"
find "$W/PS2Recomp" -name "._*" -delete   # ExFAT sidecar fix; reconfigure+rebuild repeated
file /tmp/p1-link/tools/ps2xRecomp/ps2_recomp /tmp/p1-link/tools/ps2xAnalyzer/ps2_analyzer
shasum -a 256 (both tools, /tmp and $W/P1/bin copies)
cp (tools to $W/P1/bin/); shasum -a 256 ($W/P1/bin copies)
python3 ISO-extract heredoc (extents 484/483) -> $W/P1/SLUS_207.72 + $W/P1/SYSTEM.CNF
shasum -a 1/-a 256 $W/P1/SLUS_207.72; stat sizes
cp -X docs/.../scripts/{census,final_census,parse_vif}.py $W/P1/ssx3vu/; ln -sfn "$W/P1/ssx3vu" /tmp/ssx3vu
(histogram.py reconstructed mirror written to $W/P1/ssx3vu/histogram.py)
python3 section-dump heredoc (spike [19]) -> /tmp/ssx3vu/sec*.bin
python3 /tmp/ssx3vu/final_census.py | tee $W/P1/vu1-census.txt
python3 85-tag diff heredoc (MATCH)
cd $W/P1 && $W/P1/bin/ps2_analyzer SLUS_207.72 ssx3.toml | tee analyzer.log
$W/P1/bin/ps2_recomp ssx3.toml | tee recomp.log
(summary greps: report block, unresolved JR/JALR count, fallback sum, @0x counts, output listing)
cmake -S ... -B /tmp/p1-link/runtime -G Ninja -DPS2X_BUILD_STUDIO=OFF -DPS2X_BUILD_RUNTIME=ON -DPS2X_BUILD_TEST=ON -DCMAKE_BUILD_TYPE=Release | tee $W/P1/configure-runtime.log
cmake --build /tmp/p1-link/runtime | tee $W/P1/build-runtime.log
/tmp/p1-link/runtime/ps2xTest/ps2x_tests --help (runs suite; CWD artifact noted)
cd $W/PS2Recomp && /tmp/p1-link/runtime/ps2xTest/ps2x_tests | sed strip-colors | tee $W/P1/ps2x-tests.log
(suite-count python heredocs)
/tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner --help (launched window; SIGPIPE exit; pkill/pgrep cleanup)
README reads; main.cpp/loadELF/configureIoPathsFromElf/runner-CMake reads (grep/sed)
cp -X stub register_functions.cpp -> $W/P1/runner-stub-register_functions.cpp.orig
cp -X $W/P1/output/*.{cpp,h} -> $W/PS2Recomp/ps2xRuntime/src/runner/; sidecar purge
cmake --build /tmp/p1-link/runtime --target ps2EntryRunner | tee $W/P1/build-port.log
printf 'P1' > /tmp/ssx3-host-lease
stdbuf -o0 -e0 /tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner "$W/P1/SLUS_207.72" > $W/P1/boot[-run2|-run3|-run4].log 2>&1  (foreground, bounded; terminated while healthy)
cmake reconfigure + rebuild --target ps2EntryRunner with -DPS2X_ENABLE_RUNTIME_LOGS=ON, then + -DPS2X_ENABLE_AGRESSIVE_LOGS=ON
(spin-loop forensics: ELF word reads, register-table/output greps, generated-code reads)
GS inventory greps (sizes, function lists, marker scan)
find $W/P1 -name "._*" -delete; rm /tmp/ssx3-host-lease
```

## P2-11. Receipts paths and shas

| Path | Kind | Hash / value |
|---|---|---|
| `$W/PS2Recomp` (git) | Source @ `14b1e5cb39b4af7e6fc12f9a29fdc751efde49d7` | Pin recorded; `src/runner/` holds added generated files (untracked) |
| `$W/P1/bin/ps2_recomp` | Tool (arm64) | sha256 `7654e7fe…e826f` (= /tmp copy) |
| `$W/P1/bin/ps2_analyzer` | Tool (arm64) | sha256 `4bf4ba2b…3e699f` (= /tmp copy) |
| `$W/P1/SLUS_207.72` | Boot ELF | sha1 `77114dfd…78bd8`, sha256 `1b49d05c…67af7bc`, 3,890,784 B |
| `$W/P1/ssx3vu/` | Decoders + section bins | `census.py`, `final_census.py`, `parse_vif.py` (unmodified copies), `histogram-recovered-fragment.py`, `histogram.py` (reconstruction, documented above), `sec*.bin` (via `/tmp/ssx3vu` symlink) |
| `$W/P1/vu1-census.txt` | Census receipt | 7 prog / 7,305 instr / 0 reserved / 85 ops |
| `$W/P1/ssx3.toml`, `analyzer.log`, `recomp.log`, `output/` | Recomp receipts | 8143/8143/8017/126/0/0/0; 3,594 warnings; 724,768 fallbacks |
| `$W/P1/configure-tools.log`, `build-tools.log`, `configure-runtime.log`, `build-runtime.log`, `build-port.log`, `ps2x-tests.log` | Build/test logs | Tools exit 0; runtime exit 0; tests 425/425/0 |
| `$W/P1/boot.log`, `boot-run2.log`, `boot-run3.log`, `boot-run4.log` | Boot logs | 48/48/49/133 lines; ladder in P2-7 |
| `$W/P1/runner-stub-register_functions.cpp.orig` | Replaced stub | 438-byte original |
| `/tmp/p1-link/{tools,runtime}` | APFS build dirs | Not receipts; link outputs stayed on APFS per brief |
| `/tmp/ssx3-host-lease` | Lease | Released (absent, verified) |
| `local/research/P1/REPORT.md` | This report | Part 1 (frozen) + Part 2 (appended) |

## P2-12. What I could not do

- Ghidra-export path (README preferred workflow): not attempted; the analyzer fallback was used as in the spike.
- ISO mount / extracted-file CD layout: the runner maps `cdRoot` to the ELF directory; no CD content was staged and none was requested by the run (dma=0).
- Boot fixes: none applied (no TOML stub remap, no IOP profile, no C++ change). The stall is a poll loop in `sub_0042C1F0` on `sub_0042C1A8` (`syscall 0`, `$v1=0x83`); characterizing the correct Deci2/IOP HLE response needs analysis beyond the remaining box.
- Run 4 was terminated by the operator after ticks passed 9,960 (~5.5 min) with the process healthy; no exit code was captured.
- `waits.log`: no waits occurred (no foreign lease during Part 2).

## P2-13. Function-trace receipt and corrections (appended pre-commit)

Correction to P2-7: `PS2_FUNCTION_LOG_TRACKER` is consumed by `PS_LOG_ENTRY`
in the generated `sub_*.cpp` files. Run 4 (aggressive-log build) wrote
`ps2_log.txt` (2.7 GB, 92,887,045 lines) to the process working directory,
which was the repo root — outside the allowed work dirs. Both strays were
moved into `$W/P1/`: `ps2_log.txt` → `$W/P1/ps2-function-trace.log`,
`imgui.ini` (243 B, raylib/imgui window state) → `$W/P1/imgui.ini`. Repo root
verified clean afterward. Streaming analysis of the trace:

| Item | Value |
|---|---|
| Lines | 92,887,045 |
| Distinct functions | 7 |
| Boot call order (first appearance) | `sub_00100008` (entry) → `sub_0042C300` → `sub_0042C0D8` → `sub_00423DA0` (×2) → `sub_0042C1F0` → `sub_0042C2F0` (×2) → `sub_0042C1A8` (steady state) |
| `sub_0042C1A8` enters / exits | 46,442,759 / 46,442,759 (balanced; the poll-loop body) |
| `sub_0042C1F0` enters / exits | 757 / 756 (deficit 1 = the live frame at termination) |
| Others | `sub_00100008`, `sub_0042C300`, `sub_0042C0D8`: 1/1; `sub_00423DA0`: 2/2; `sub_0042C2F0`: 2/2 |
| No other function ever entered | No stub, syscall-handler, GS, or CD function appears in the trace |

Ladder addendum: the steady state is 46.4M balanced executions of
`sub_0042C1A8`, whose recompiled body unconditionally reaches
`runtime->handleSyscall(rdram, ctx, 0x0u)` (`$v1=0x83`) on its return path;
`handleSyscall` itself emits no log line, so dispatch stays unconfirmed in
the log. "First syscall (in code)" remains Partial as stated in P2-7.
