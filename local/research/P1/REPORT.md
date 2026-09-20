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
| Host | `Darwin <mac> 27.0.0 Darwin Kernel Version 27.0.0 … RELEASE_ARM64_T8132 arm64` |
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

From `~/dev/ssx3`:

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

---

# P1b report — Part 3 (brief local/muse/prompts/P1b.md + 2 amendments + workflow change)

Run wall: 2026-09-18 18:02 → 20:58 UTC (14:02 → 16:58 EDT). No verdicts.
`W` = `/Volumes/Extreme SSD/ps2recomp-spike`.

## P3-0. Lease record

| Event | Value |
|---|---|
| Start | `/tmp/ssx3-host-lease` absent |
| Builds | `printf 'P1b-build' > /tmp/ssx3-host-lease` before each build |
| Boots | `printf 'P1b' > /tmp/ssx3-host-lease` before each boot |
| End | `rm /tmp/ssx3-host-lease`, verified absent |
| Foreign leases / waits | None during P1b; no `waits.log` |
| `adb` | Not used |

## P3-1. Disc staging + path-resolution table (Step 1)

Staged with `hdiutil` (no Python fallback needed). macOS mounted the ISO
as `cd9660` (ISO9660 bridge, not UDF).

| Item | Value |
|---|---|
| Mount | `hdiutil attach -readonly -nobrowse -mountpoint /tmp/p1-iso "$W/SSX 3 (USA).iso"`, exit 0 (`/dev/disk11`) |
| Copy | `cp -R /tmp/p1-iso/. $W/P1/cd/`, exit 0; `hdiutil detach /tmp/p1-iso`, exit 0 |
| Files | 163 (after purging 181 AppleDouble `._*` sidecars the copy created) |
| Bytes | 3,004,221,507 |
| Top level | `CNF DATA NETGUI PAD0.000 PAD1.000 SLUS_207.72 SYSTEM.CNF` |
| `$W/P1/cd/SLUS_207.72` sha1 | `77114dfd1205eaccf1ccc18c5f9650097fa78bd8` (matches) |
| `$W/P1/cd/SYSTEM.CNF` | Present, `BOOT2=cdrom0:\SLUS_207.72;1`, `VER=1.00`, `VMODE=NTSC` |

Path resolution (`Syscalls/Helpers/Runtime.h:117-149`, `Stubs/Helpers/Support.h:160-175`):

| Guest pattern | Prefix match | Root | Rest rewrite |
|---|---|---|---|
| `host0:` / `host:` | case-insensitive, 6/5 chars | `hostRoot` (= ELF dir) | `\`→`/`, trailing `;`+digits stripped, leading slashes stripped, case preserved |
| `cdrom0:` / `cdrom:` | case-insensitive, 7/6 chars | `cdRoot` (= ELF dir) | same as above |
| `mc0:` / `mc:` | exact `mc` starts, 4/3 chars | `mcRoot` (= ELF dir `/mc0`) | same as above |
| leading `/` or `\` | — | `cdRoot` | same rewrite |
| `X:` (any other letter) | — | passed through unchanged | — |
| bare relative | — | `cdRoot` | same rewrite |

CD HLE (`Support.h`): `normalizeCdPathNoPrefix` lowercases drive/dir/file
for cd9660 matching; raw LBN reads need a sector→file map or `cdImage`
(`Support.h:430-480`); `IoPaths.cdImage` is set by nothing in the runner
(confirmed by grep over `main.cpp`/`ps2_runtime.*`: no env var, no flag).

## P3-2. Stub the scanner (Step 2)

| Item | Value |
|---|---|
| TOML edit | One line appended to `general.stubs`: `"ret0@0x0042c1f0",` (diff `203a204`, all other entries kept) |
| Recompile | `ps2_recomp ssx3.toml` → `recomp-p1b.log`, exit 0: discovered 8143, processed 8143, recompiled 8016, stubs 127, skipped 0, decode failures 0, unhandled 0; entrypoints 391,169; warnings 3,594; fallbacks 724,768 |
| Wrapper | `output/sub_0042C1F0_0x42c1f0.cpp` is exactly the ret0 stub (`ctx->pc = getRegU32(ctx,31); ps2_stubs::ret0(...)`) |
| Runner refresh | `cp -X output/*.{cpp,h}` → `PS2Recomp/ps2xRuntime/src/runner/` (8,146 files; sidecars purged) |
| Rebuild | `cmake --build … --target ps2EntryRunner` with `RUNTIME_LOGS=ON`, aggressive/tracker OFF, exit 0 (`build-port-p1b.log`); binary sha256 `98dba1e59bbf16710c63c2b1d8eb91c28c054268b9c78982b4b0d631830fd91d` |

## P3-3. Boot ladders (Steps 3–4, one table per boot)

Common setup: CWD `$W/P1/run` (strays `imgui.ini`, `mc0/`, `mc1/` land there
as required), ELF `$W/P1/cd/SLUS_207.72` as argv[1]. All logs < 5 KB
(200 MB cap respected trivially). No boot crashed.

| Boot | Binary (fixes in tree) | Log | Ladder |
|---|---|---|---|
| 1 `boot-p1b-1.log` | ret0 stub, no image | 0 lines (brief's `timeout` missing on macOS; `head -c` pipe used, its block buffer hid all output on kill) | No ladder (void). Strays prove it ran. Command deviated, recorded below. |
| 2 `boot-p1b-2.log` | same as 1 | 58 lines | Entry `0x100008` → trace `…0x42c1f0→0x42c7c8…→0x414728` → `missing-target IndirectCall JALR 0x40fc6c→0x3b07b8` (non-fatal) → `SifInitRpc Initialized` → 6 SIF module loads (`SIO2MAN PADMAN LIBSD SNDDRV MCMAN MCSERV`, uppercase+`;1` resolved) → `sceCdRead unresolved LBN 0x10 sectors=1 (no mapped file and no configured CD image)` pc=`0x3e3694` (in `sub_003E3618`); then static. First syscall id seen in log: none (no dispatch lines). cdrom0 paths opened: the 6 module paths. VIF MPG/MSCAL: none. GIF kick: none. Presented frame: none. Crash: none. |
| 3 `boot-p1b-3.log` | + Fix A, `PS2X_CD_IMAGE` set | 56 lines | Same path through module 6; LBN error line gone (raw read served silently); then static, no new lines in 7 min. |
| 4 `boot-p1b-4.log` | + map split 1 (`0x3b07b8`) | 50 lines | New: `missing-target DirectCall JAL 0x42c310→0x42c1f0` (map dropped stub rows); trace dies after `0x423da0`. Fix ordered per orchestrator note. |
| 5 `boot-p1b-5.log` | + full map (189 stub rows; binary also contains Fix C, see P3-6) | 56 lines | `0x42c1f0` resolved; `0x3b07b8` split works (trace `→0x3b07b8→0x3b0770→0x3b0410`); modules 1–6; new `missing-target IndirectCall JALR 0x40fc6c→0x3adda0`. |
| 6 `boot-p1b-6.log` | + split `0x3adda0` | 56 lines | `→0x3adda0→0x3ad290`; new `missing-target IndirectCall JALR 0x40fc6c→0x3a6648`. |
| 7 `boot-p1b-7.log` | + split `0x3a6648` | 56 lines | `→0x3a6648→0x3a3f48→0x39e288`; new `missing-target IndirectCall JALR 0x40fc6c→0x3970f8`; modules 1–6. |
| 8 `boot-p1b-8.log` | + batch 35 splits + Fix D (binary `a72fff15…`) | 55 lines, 10 min | No missing-target lines at all (all 39 constructor entries resolved); modules 1–6; no LBN error; no `ee:idle` dump (scheduler never >3 s without a runnable thread); no VIF MPG/MSCAL; no GIF kick; no presented game frame; no crash. Runner at ~10% CPU (render loop). |

Boot-2 firsts: first SIF/IOP request = the 6 module loads above (in order);
first CD read = `sceCdRead` LBN `0x10` (ISO9660 PVD), unresolved without image.

## P3-4. Constructor table (one walk routine, 39 entries)

Walk: `sub_0040FB88` @ `0x40fbe0`: `$a3=0x440000`, table base
`0x440000-0x31C8=0x43ce38`; word[0]=`0x27`=39 is an explicit count
(non-`-1` path jumps to `0x40fc44` with count in `$a1`); `$s0` starts at
`0x43ce38+39*4=0x43ced4`; calls words[39]…words[1] in reverse via
`jalr` at `0x40fc6c`. Word[40] = `0x00000000` (terminator, not called).
Every entry verified as prologue two ways: ELF word
(`addiu $sp,$sp,-0x10` = `0x27bdfff0`, once `0x27bdffe0`) AND the
`// 0xADDR: ENC mnemonic` comment in `output/` (all `addiu`).

| # | Address | Prior map state | Split row added |
|---|---|---|---|
| 1 | `0x1448b8` | in `sub_001448A8` | `sub_001448B8` |
| 2 | `0x15c8f0` | in `sub_0015C228` | `sub_0015C8F0` |
| 3 | `0x168298` | in `sub_00168150` | `sub_00168298` |
| 4 | `0x176a28` | in `sub_00176890` | `sub_00176A28` |
| 5 | `0x177e30` | in `sub_00177650` | `sub_00177E30` |
| 6 | `0x179738` | in `sub_00178F58` | `sub_00179738` |
| 7 | `0x179fa8` | in `sub_00179798` | `sub_00179FA8` |
| 8 | `0x1e12b0` | in `sub_001E1090` | `sub_001E12B0` |
| 9 | `0x222428` | in `sub_00220AD0` | `sub_00222428` |
| 10 | `0x2267f0` | in `sub_00226628` | `sub_002267F0` |
| 11 | `0x247e20` | in `sub_00247AB0` | `sub_00247E20` |
| 12 | `0x2501a8` | in `sub_0024E8D8` | `sub_002501A8` |
| 13 | `0x251690` | in `sub_00250CB0` | `sub_00251690` |
| 14 | `0x254330` | in `sub_00253B58` | `sub_00254330` |
| 15 | `0x2557c0` | in `sub_00254E60` | `sub_002557C0` |
| 16 | `0x269ea0` | in `sub_00269CF0` | `sub_00269EA0` |
| 17 | `0x26c438` | in `sub_0026BAE8` | `sub_0026C438` |
| 18 | `0x2722c0` | in `sub_00272288` | `sub_002722C0` |
| 19 | `0x284b80` | in `sub_00283E60` | `sub_00284B80` |
| 20 | `0x2baee8` | in `sub_002BADD0` | `sub_002BAEE8` |
| 21 | `0x2bb0e0` | in `sub_002BAFB0` | `sub_002BB0E0` |
| 22 | `0x2bc4e0` | in `sub_002BBC38` | `sub_002BC4E0` |
| 23 | `0x2c1688` | in `sub_002C0B70` | `sub_002C1688` |
| 24 | `0x2d4060` | in `sub_002D2988` | `sub_002D4060` |
| 25 | `0x2d48d0` | in `sub_002D40C0` | `sub_002D48D0` |
| 26 | `0x2f8370` | in `sub_002F7BE0` | `sub_002F8370` |
| 27 | `0x2f9818` | in `sub_002F9040` | `sub_002F9818` |
| 28 | `0x2fae18` | in `sub_002FA640` | `sub_002FAE18` |
| 29 | `0x30d498` | in `sub_0030C8D8` | `sub_0030D498` |
| 30 | `0x315a00` | in `sub_003150F8` | `sub_00315A00` |
| 31 | `0x316878` | in `sub_00315A20` | `sub_00316878` |
| 32 | `0x320b28` | in `sub_00320550` | `sub_00320B28` |
| 33 | `0x341368` | in `sub_003411B8` | `sub_00341368` |
| 34 | `0x361e10` | in `sub_003612C0` | `sub_00361E10` |
| 35 | `0x3970f8` | exact (split earlier) | — (already `sub_003970F8`) |
| 36 | `0x3a6648` | exact (split earlier) | — (already `sub_003A6648`) |
| 37 | `0x3adda0` | exact (split earlier) | — (already `sub_003ADDA0`) |
| 38 | `0x3b07b8` | exact (split earlier) | — (already `sub_003B07B8`) |
| 39 | `0x1001d8` | in `sub_001001C8` | `sub_001001D8` |

Non-prologue entries: none (0 recorded, 0 skipped). Map: 8,209 → 8,244
data rows. Batch recompile (`recomp-p1b-batch.log`): discovered 8,243
(map loads 8,244, one subsumed), recompiled 8,067, stubs 176, skipped 0,
decode failures 0, unhandled 0; entrypoints 391,298; warnings 3,596;
fallbacks 724,860. Note: `stubs:` reads 176 in map mode (all 176 gap stub
rows bind), not 126 as the orchestrator note expected — 126 was the
analyzer-mode count (P1). `ret0` wrapper for `sub_0042C1F0` verified intact
after every recompile.

## P3-5. Patch files (upstream PR candidates, quoted in full)

All three live under `$W/P1/` and are committed on `ssx3` (see P3-6).

### cd-image-env.patch (/Volumes/Extreme SSD/ps2recomp-spike/P1/cd-image-env.patch)

```diff
diff --git a/ps2xRuntime/src/main.cpp b/ps2xRuntime/src/main.cpp
index 563bcbd..5ecba2a 100644
--- a/ps2xRuntime/src/main.cpp
+++ b/ps2xRuntime/src/main.cpp
@@ -226,6 +226,16 @@ int main(int argc, char *argv[])
             return 1;
         }
 
+        if (const char *cdImageEnv = std::getenv("PS2X_CD_IMAGE"))
+        {
+            if (cdImageEnv[0] != '\0')
+            {
+                PS2Runtime::IoPaths ioPaths = PS2Runtime::getIoPaths();
+                ioPaths.cdImage = std::filesystem::path(cdImageEnv);
+                PS2Runtime::setIoPaths(ioPaths);
+            }
+        }
+
         runtime.run();
 
 #ifdef _DEBUG
```

### idle-dump.patch (/Volumes/Extreme SSD/ps2recomp-spike/P1/idle-dump.patch)

```diff
diff --git a/ps2xRuntime/src/lib/Kernel/EeScheduler.cpp b/ps2xRuntime/src/lib/Kernel/EeScheduler.cpp
index 3a6ec7d..a9786bb 100644
--- a/ps2xRuntime/src/lib/Kernel/EeScheduler.cpp
+++ b/ps2xRuntime/src/lib/Kernel/EeScheduler.cpp
@@ -5,7 +5,9 @@
 
 #include <algorithm>
 #include <cassert>
+#include <chrono>
 #include <cstring>
+#include <iostream>
 #include <limits>
 #include <stdexcept>
 
@@ -168,12 +170,42 @@ void EeScheduler::run()
         if (m_currentThreadId == 0)
         {
             GuestThread *next = selectReady();
+            // Diagnostic idle dump (function statics keep this to run()).
+            static auto idleSince = std::chrono::steady_clock::time_point{};
+            static bool idleDumpPrinted = false;
             if (!next && m_pendingInvocations.empty())
             {
                 publishSnapshot();
+                const auto idleNow = std::chrono::steady_clock::now();
+                if (idleSince == std::chrono::steady_clock::time_point{})
+                {
+                    idleSince = idleNow;
+                }
+                else if (!idleDumpPrinted &&
+                         idleNow - idleSince >= std::chrono::seconds(3))
+                {
+                    idleDumpPrinted = true;
+                    const EeKernelSnapshot idleSnap = snapshot();
+                    std::cerr << "[ee:idle] no runnable thread for 3s; threads="
+                              << idleSnap.threads.size() << std::endl;
+                    for (const EeThreadSnapshot &idleThread : idleSnap.threads)
+                    {
+                        std::cerr << "[ee:idle] id=" << idleThread.id
+                                  << " status="
+                                  << static_cast<int>(idleThread.status)
+                                  << " waitReason="
+                                  << static_cast<int>(idleThread.waitReason)
+                                  << " waitId=" << idleThread.waitId << " pc=0x"
+                                  << std::hex << idleThread.pc << std::dec
+                                  << " entry=0x" << std::hex << idleThread.entry
+                                  << std::dec << std::endl;
+                    }
+                }
                 waitForEvent();
                 continue;
             }
+            idleSince = std::chrono::steady_clock::time_point{};
+            idleDumpPrinted = false;
             if (next)
             {
                 makeRunning(*next);
```

### cd-callback.patch (/Volumes/Extreme SSD/ps2recomp-spike/P1/cd-callback.patch)

```diff
diff --git a/ps2xRuntime/src/lib/Kernel/Stubs/CD.cpp b/ps2xRuntime/src/lib/Kernel/Stubs/CD.cpp
index 56a978e..9a7507b 100644
--- a/ps2xRuntime/src/lib/Kernel/Stubs/CD.cpp
+++ b/ps2xRuntime/src/lib/Kernel/Stubs/CD.cpp
@@ -31,6 +31,31 @@ namespace ps2_stubs
         uint32_t g_cdStReadTraceCount = 0u;
         CdStreamTimingState g_cdStreamTiming;
 
+        // Async CD callback (sceCdCallback / sceCdInitEeCB HLE). The game
+        // registers a CD completion callback whose invocation signals the
+        // semaphore its thread waits on.
+        uint32_t g_cdCallbackFn = 0u;
+        uint32_t g_cdCallbackGp = 0u;
+        uint32_t g_cdCallbackStackTop = 0u;
+
+        void queueCdCallback(R5900Context *ctx, PS2Runtime *runtime, uint32_t func)
+        {
+            (void)ctx;
+            if (g_cdCallbackFn == 0u || runtime == nullptr)
+            {
+                return;
+            }
+            GuestInvocation invocation{};
+            invocation.kind = GuestInvocationKind::Interrupt;
+            invocation.context.pc = g_cdCallbackFn;
+            SET_GPR_U32(&invocation.context, 4, func);
+            SET_GPR_U32(&invocation.context, 5, 0u);
+            SET_GPR_U32(&invocation.context, 28, g_cdCallbackGp);
+            SET_GPR_U32(&invocation.context, 29, g_cdCallbackStackTop);
+            SET_GPR_U32(&invocation.context, 31, 0u);
+            runtime->eeScheduler().queueInvocation(std::move(invocation));
+        }
+
         uint64_t currentCdStreamTick(PS2Runtime *runtime)
         {
             return runtime != nullptr ? runtime->eeScheduler().currentVSyncTick() : 0u;
@@ -317,6 +342,7 @@ namespace ps2_stubs
         {
             g_cdStreamingLbn = selected.lbn + selected.sectors;
             setReturnS32(ctx, 1); // command accepted/success
+            queueCdCallback(ctx, runtime, 1u); // SCECdFuncRead
             return;
         }
 
@@ -355,7 +381,12 @@ namespace ps2_stubs
 
     void sceCdCallback(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
     {
-        setReturnS32(ctx, 0);
+        (void)rdram;
+        (void)runtime;
+        const uint32_t previous = g_cdCallbackFn;
+        g_cdCallbackFn = getRegU32(ctx, 4);
+        g_cdCallbackGp = getRegU32(ctx, 28);
+        setReturnS32(ctx, static_cast<int32_t>(previous));
     }
 
     void sceCdChangeThreadPriority(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
@@ -404,6 +435,11 @@ namespace ps2_stubs
 
     void sceCdInitEeCB(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
     {
+        (void)rdram;
+        (void)runtime;
+        const uint32_t stackAddr = getRegU32(ctx, 5);
+        const uint32_t stackSize = getRegU32(ctx, 6);
+        g_cdCallbackStackTop = stackAddr + stackSize;
         setReturnS32(ctx, 1);
     }
 
@@ -445,6 +481,7 @@ namespace ps2_stubs
     void sceCdPause(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
     {
         setReturnS32(ctx, 1);
+        queueCdCallback(ctx, runtime, 5u); // SCECdFuncPause
     }
 
     void sceCdPosToInt(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
@@ -657,6 +694,7 @@ namespace ps2_stubs
     void sceCdStandby(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
     {
         setReturnS32(ctx, 1);
+        queueCdCallback(ctx, runtime, 3u); // SCECdFuncStandby
     }
 
     void sceCdStatus(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
@@ -689,6 +727,7 @@ namespace ps2_stubs
     void sceCdStop(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
     {
         setReturnS32(ctx, 1);
+        queueCdCallback(ctx, runtime, 4u); // SCECdFuncStop
     }
 
     void sceCdStPause(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
```

## P3-6. Ordering deviations, binaries, commits

| Item | Value |
|---|---|
| Boot-1 command | `timeout` does not exist on macOS; used foreground run + terminate (equivalent of the brief's background+sleep+kill fallback). The `head -c` pipe was then dropped from boot 2 on (direct-to-file) because its block buffer hid all output on kill; the 200 MB cap was enforced by log sizes instead (all < 5 KB). |
| Fix C in boot-5 binary | `EeScheduler.cpp` was edited while the split-1 rebuild was still compiling, so boot 5's binary (`bcdfa765…`) contains A + B + C. C is diagnostic-only (no behavior change); recorded here. |
| `._EeScheduler.cpp` build break | The edit tool creates AppleDouble sidecars on this volume; the lib glob compiled `._EeScheduler.cpp` and failed one build. Purged; all subsequent edits were followed by purges. No source harmed. |
| Split-4 build (binary `12dd42ed…`) | Built but never booted: the batch-splits instruction superseded it. |
| `stubs: 176` vs expected 126 | In map mode every gap stub row binds (176); 126 was the analyzer-mode count. `ret0@0x0042c1f0` verified firing (boot-5 trace passes through `0x42c1f0`). |
| CSV row math | 8,017 (8,016 + `0x3b07b8` split) → 8,206 (+189 stub rows; 155 contained skipped: 5 stubs + 150 untracked, recorded) → 8,207/8,208/8,209 (single splits) → 8,244 (+35 batch). Recompiles: `recomp-p1b.log` 8143/8016/127, `recomp-p1b-map.log` 8017/8017/0(count artifact; bindings verified in files), `recomp-p1b-map2.log` 8205/8029/176, `map3` 8206/8030/176, `map4` 8207/8031/176, `map5` 8208/8032/176, `batch` 8243/8067/176; all 0 decode failures, 0 unhandled. |

Binaries (`/tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner` sha256):

| Binary | Fixes in tree | Foreground boots |
|---|---|---|
| `98dba1e5…` | ret0 stub, RUNTIME_LOGS on | 1, 2 |
| `9d84b59f…` | + Fix A | 3 |
| `d1babad2…` | + map split 1 (`0x3b07b8`) | 4 |
| `bcdfa765…` | + full map (189 stub rows) + Fix C | 5 |
| `fba4f584…` | + split `0x3adda0` | 6 |
| `12dd42ed…` | + split `0x3a6648` | 7 |
| `a72fff15…` | + split `0x3970f8` + batch 35 + Fix D | 8 |

Attribution is by build order cross-checked against each boot log's trace
(each log shows exactly which splits are present); per-launch shas were not
captured. The split-`0x3970f8` (map5) intermediate binary was superseded by
the batch+D rebuild before any boot ran on it (no sha recorded).

`ssx3` commits (pushed `fork ssx3`, verified `git show --stat` each time —
one file each, no `runner/` or `._` files):

| Commit | File | Push |
|---|---|---|
| `c0af340` ignore generated guest sources + `._*` | `.gitignore` (+4/-1) | `14b1e5c..cf06e36` (with A) |
| `cf06e36` Fix A: PS2X_CD_IMAGE hook | `ps2xRuntime/src/main.cpp` (+10) | same push |
| `fc5cf72` Fix C: idle-thread dump | `…/Kernel/EeScheduler.cpp` (+32) | `cf06e36..fc5cf72` |
| `04905db` Fix D: CD callback HLE | `…/Kernel/Stubs/CD.cpp` (+40/-1) | `fc5cf72..04905db` |

`register_functions.cpp` (generated replacement) left as a local
modification, never added. All trailers present on each commit.

## P3-7. Exact commands used (Part 3, abridged to the load-bearing ones)

```
hdiutil attach -readonly -nobrowse -mountpoint /tmp/p1-iso "$W/SSX 3 (USA).iso"
mkdir -p $W/P1/cd && cp -R /tmp/p1-iso/. $W/P1/cd/; hdiutil detach /tmp/p1-iso
find $W/P1/cd -name "._*" -delete; find $W/P1/cd -type f | wc -l; shasum -a 1 $W/P1/cd/SLUS_207.72
grep cdRoot/hostRoot (scoped, runner/ excluded); reads of Path.h, Runtime.h, Support.h, CD.cpp
printf 'P1b-build' > /tmp/ssx3-host-lease   (before each build; 'P1b' before each boot; rm at end)
cp -X $W/P1/ssx3.toml $W/P1/ssx3.toml.p1-orig; python3 TOML insert (ret0 row); diff
cd $W/P1 && $W/P1/bin/ps2_recomp $W/P1/ssx3.toml | tee recomp-p1b.log
cat output/sub_0042C1F0_0x42c1f0.cpp (wrapper quote)
cp -X $W/P1/output/*.{cpp,h} $W/PS2Recomp/ps2xRuntime/src/runner/  (+ sidecar purges)
cmake --build /tmp/p1-link/runtime --target ps2EntryRunner | tee build-port-p1b.log; shasum -a 256 (binary)
mkdir -p $W/P1/run; cd $W/P1/run && PS2X_CD_IMAGE=... stdbuf -o0 -e0 runner $W/P1/cd/SLUS_207.72 > boot-p1b-N.log 2>&1  (N=1..8; N=1 with | head -c pipe)
ELF word reads (table base, entries, prologues); CSV generators (split-only backup, stub rows, batch splits)
python TOML ghidra_output set; recompiles map/map2/map3/map4/map5/batch (tee logs)
main.cpp hunk (edit_file); git diff > $W/P1/cd-image-env.patch
EeScheduler.cpp hunks (edit_file); git diff > $W/P1/idle-dump.patch
CD.cpp hunks (edit_file x5); git diff > $W/P1/cd-callback.patch
git add <specific files>; git commit (4x, trailers); git show --stat; git push fork ssx3 (3x)
strings binary | grep -c ee:idle (C-in-binary check)
trace/ladder greps per boot; constructor-table prologue verification via output/ comments
find $W/P1 -name "._*" -delete (repeated); mv repo-root strays (none this round)
```

## P3-8. What I could not do

- Ghidra-export path: the CSV map is derived from analyzer output, not Ghidra.
- `stubs: 126` in map mode: reads 176 (see P3-6); bindings verified per-file instead.
- Boot 8 emits no `ee:idle` dump (scheduler never >3 s idle) and no VIF/GIF/crash lines; per amendment 2, nothing further implemented — parked-on-different-wait dump did not occur either (no dump at all).
- IOP profile table for the 6 modules: the background grep did not return a complete table before report time; no profiles were modified; module-load success (6/6) recorded instead.
- `waits.log`: no waits (no foreign lease during P1b).
- Time boxes: P1b base box + 2 h (amendment 1) + 2 h (amendment 2) were not exhausted.
# P1c report — Part 4 (brief local/muse/prompts/P1c.md)

Run wall: 2026-09-18 21:00 → 22:05 UTC (17:00 → 18:05 EDT), inside the
5-hour box. `W` = `/Volumes/Extreme SSD/ps2recomp-spike`. No verdicts.

## P4-0. Lease record

| Event | Value |
|---|---|
| Start | `/tmp/ssx3-host-lease` held `P1c` (written when absent) |
| Builds/boots | Lease kept as `P1c` across all builds and boots 1–3 |
| Foreign leases / waits | None observed; no `waits.log` |
| `adb` | Not used |
| End | Removed after the `[P1c]` push, verified absent |

## P4-1. Diagnostics diff + boot-1 period blocks

Step 1 design (all gated on `PS2X_DIAG_PERIOD_MS`; unset = compiled in,
nothing printed, per-iteration cost one counter increment plus a cached
static check):

| Item | Location | Behavior |
|---|---|---|
| Thread dump | `EeScheduler.cpp` `EeScheduler::run()` (~line 240); print helper in anonymous namespace (~line 88) | Every period: Fix C table for all threads + `priority` + `scheduled` count since last dump; counts cleared after print |
| Syscall histogram | `Syscalls/Dispatcher.cpp` `dispatchNumericSyscall()` (line 89); flusher `diagSyscallsPeriodicFlush()` (line 55) | Per id: count, first/last `ctx->pc`; top 20 every period, then reset |
| Call-target histogram | `ps2_runtime.cpp` `dispatchGuestBranch()`, hook before the binding lookup (line 1452; lookup at line 1455) | Per call target: count, first/last `$ra`; top 30 every period, then reset |
| CD queued receipt | `Stubs/CD.cpp` `queueCdCallback()` (line ~60) | One `[cd:callback] queued` line (func id, callback pc); tags the invocation `0x43444342…|func` |
| CD start receipt | `EeScheduler.cpp` `run()`, both invocation pop sites (lines ~328, ~407) | One `[cd:callback] start` line when the tagged invocation starts |
| CD entry logs | `Stubs/CD.cpp` `sceCdRead` (line 268), `sceCdCallback` (line 481), `sceCdInitEeCB` (line 483) | One `[diag:cd]` line per guest call (added for the Step 2 CD question) |

The HLE stub histogram site is `PS2Runtime::dispatchGuestBranch()` in
`ps2xRuntime/src/lib/ps2_runtime.cpp`: the `lookupFunction(targetPc)` call
at line 1455 is where the `register_functions.cpp` bindings are looked up
at call time; the counting hook sits directly above it (line 1452).
Fix C printing is reused via `printEeThreadDiagLine()` (same field order;
the `[ee:idle]` call site output is byte-identical, the periodic block
appends `priority` and `scheduled`).
Flush correction: histograms first flushed only on later events, which
dropped the startup burst when the guest went quiet before the first
boundary; the scheduler tick now calls both flushers every period, so
quiet stretches emit empty blocks.

Diff `04905db..dbf0080` (4 files, +368/-9):

```
diff --git a/ps2xRuntime/src/lib/Kernel/EeScheduler.cpp b/ps2xRuntime/src/lib/Kernel/EeScheduler.cpp
index a9786bb..bb6b1e0 100644
--- a/ps2xRuntime/src/lib/Kernel/EeScheduler.cpp
+++ b/ps2xRuntime/src/lib/Kernel/EeScheduler.cpp
@@ -6,10 +6,21 @@
 #include <algorithm>
 #include <cassert>
 #include <chrono>
+#include <cstdlib>
 #include <cstring>
 #include <iostream>
 #include <limits>
 #include <stdexcept>
+#include <unordered_map>
+
+// P1c histogram flushers owned by other translation units (defined in
+// Kernel/Syscalls/Dispatcher.cpp and ps2_runtime.cpp). Called from the
+// periodic tick below so quiet periods still emit blocks.
+namespace ps2_syscalls
+{
+    void diagSyscallsPeriodicFlush();
+}
+void diagCallsPeriodicFlush();
 
 namespace
 {
@@ -72,6 +83,63 @@ namespace
         } while (candidate != first);
         return 0;
     }
+
+    // P1c steady-state diagnostics. Everything below is gated on
+    // PS2X_DIAG_PERIOD_MS: unset/empty/0 means compiled in, nothing printed,
+    // and callers pay only a counter increment plus a cached static check.
+    uint64_t diagPeriodMs()
+    {
+        static const uint64_t period = [] {
+            if (const char *env = std::getenv("PS2X_DIAG_PERIOD_MS"))
+            {
+                if (env[0] != '\0')
+                {
+                    char *end = nullptr;
+                    const unsigned long long parsed = std::strtoull(env, &end, 10);
+                    if (end != env)
+                    {
+                        return static_cast<uint64_t>(parsed);
+                    }
+                }
+            }
+            return static_cast<uint64_t>(0);
+        }();
+        return period;
+    }
+
+    uint64_t diagNowMs()
+    {
+        return static_cast<uint64_t>(std::chrono::duration_cast<std::chrono::milliseconds>(
+                                         std::chrono::steady_clock::now().time_since_epoch())
+                                         .count());
+    }
+
+    // Shared printer for the Fix C thread table. Fix C callers pass "ee:idle";
+    // the periodic P1c dump passes "diag:thread" and appends priority plus
+    // the per-thread schedule count.
+    void printEeThreadDiagLine(std::ostream &os, const char *prefix, const EeThreadSnapshot &thread)
+    {
+        os << "[" << prefix << "] id=" << thread.id
+           << " status=" << static_cast<int>(thread.status)
+           << " waitReason=" << static_cast<int>(thread.waitReason)
+           << " waitId=" << thread.waitId << " pc=0x"
+           << std::hex << thread.pc << std::dec
+           << " entry=0x" << std::hex << thread.entry << std::dec;
+    }
+
+    // Tag mark for CD-completion invocations queued by queueCdCallback
+    // (Kernel/Stubs/CD.cpp). Upper 32 bits are the 'CDCB' magic, lower 32
+    // bits are the SCE callback function id.
+    constexpr uint64_t kCdCallbackDiagTagBase = 0x4344434200000000ULL;
+    constexpr uint64_t kCdCallbackDiagTagMask = 0xFFFFFFFF00000000ULL;
+
+    bool isCdCallbackDiagTag(uint64_t tag)
+    {
+        return (tag & kCdCallbackDiagTagMask) == kCdCallbackDiagTagBase;
+    }
+
+    // Per-thread schedule counts since the last periodic dump.
+    std::unordered_map<int, uint64_t> g_diagSchedCounts;
 }
 
 EeScheduler::EeScheduler(PS2Runtime &runtime)
@@ -159,6 +227,12 @@ void EeScheduler::run()
     assertExecutor();
     m_running.store(true, std::memory_order_release);
 
+    // P1c steady-state diagnostics state. When PS2X_DIAG_PERIOD_MS is unset
+    // the per-iteration cost below is one counter increment plus a check.
+    static uint64_t s_diagTick = 0;
+    static uint64_t s_diagLastMs = 0;
+    static uint64_t s_diagBlock = 0;
+
     while (!m_stopRequested.load(std::memory_order_acquire))
     {
         processPendingEvents();
@@ -167,6 +241,40 @@ void EeScheduler::run()
             break;
         }
 
+        ++s_diagTick;
+        const uint64_t diagPeriod = diagPeriodMs();
+        if (diagPeriod != 0u)
+        {
+            const uint64_t diagNow = diagNowMs();
+            if (s_diagLastMs == 0u)
+            {
+                s_diagLastMs = diagNow;
+            }
+            else if (diagNow - s_diagLastMs >= diagPeriod)
+            {
+                s_diagLastMs = diagNow;
+                publishSnapshot();
+                const EeKernelSnapshot diagSnap = snapshot();
+                std::cerr << "[diag:threads] block=" << s_diagBlock++
+                          << " threads=" << diagSnap.threads.size()
+                          << " period_ms=" << diagPeriod << std::endl;
+                for (const EeThreadSnapshot &diagThread : diagSnap.threads)
+                {
+                    uint64_t scheduled = 0u;
+                    if (auto it = g_diagSchedCounts.find(diagThread.id); it != g_diagSchedCounts.end())
+                    {
+                        scheduled = it->second;
+                    }
+                    printEeThreadDiagLine(std::cerr, "diag:thread", diagThread);
+                    std::cerr << " priority=" << diagThread.currentPriority
+                              << " scheduled=" << scheduled << std::endl;
+                }
+                g_diagSchedCounts.clear();
+                ps2_syscalls::diagSyscallsPeriodicFlush();
+                diagCallsPeriodicFlush();
+            }
+        }
+
         if (m_currentThreadId == 0)
         {
             GuestThread *next = selectReady();
@@ -190,15 +298,8 @@ void EeScheduler::run()
                               << idleSnap.threads.size() << std::endl;
                     for (const EeThreadSnapshot &idleThread : idleSnap.threads)
                     {
-                        std::cerr << "[ee:idle] id=" << idleThread.id
-                                  << " status="
-                                  << static_cast<int>(idleThread.status)
-                                  << " waitReason="
-                                  << static_cast<int>(idleThread.waitReason)
-                                  << " waitId=" << idleThread.waitId << " pc=0x"
-                                  << std::hex << idleThread.pc << std::dec
-                                  << " entry=0x" << std::hex << idleThread.entry
-                                  << std::dec << std::endl;
+                        printEeThreadDiagLine(std::cerr, "ee:idle", idleThread);
+                        std::cerr << std::endl;
                     }
                 }
                 waitForEvent();
@@ -209,12 +310,25 @@ void EeScheduler::run()
             if (next)
             {
                 makeRunning(*next);
+                if (diagPeriod != 0u)
+                {
+                    ++g_diagSchedCounts[next->id];
+                }
             }
             else
             {
                 GuestThread *owner = &acquireInvocationThread();
                 GuestInvocation invocation = std::move(m_pendingInvocations.front());
                 m_pendingInvocations.pop_front();
+                if (diagPeriod != 0u)
+                {
+                    ++g_diagSchedCounts[owner->id];
+                    if (isCdCallbackDiagTag(invocation.tag))
+                    {
+                        std::cerr << "[cd:callback] start func=" << (invocation.tag & 0xFFFFFFFFu)
+                                  << " cb=0x" << std::hex << invocation.context.pc << std::dec << std::endl;
+                    }
+                }
                 owner->status = EeThreadStatus::Running;
                 m_currentThreadId = owner->id;
                 renewTimeSlice();
@@ -288,6 +402,11 @@ void EeScheduler::run()
         {
             GuestInvocation invocation = std::move(m_pendingInvocations.front());
             m_pendingInvocations.pop_front();
+            if (diagPeriod != 0u && isCdCallbackDiagTag(invocation.tag))
+            {
+                std::cerr << "[cd:callback] start func=" << (invocation.tag & 0xFFFFFFFFu)
+                          << " cb=0x" << std::hex << invocation.context.pc << std::dec << std::endl;
+            }
             if (getRegU32(&invocation.context, 29) == 0u)
             {
                 SET_GPR_U32(&invocation.context, 29, invocationStackTop());
diff --git a/ps2xRuntime/src/lib/Kernel/Stubs/CD.cpp b/ps2xRuntime/src/lib/Kernel/Stubs/CD.cpp
index 9a7507b..aa9aa89 100644
--- a/ps2xRuntime/src/lib/Kernel/Stubs/CD.cpp
+++ b/ps2xRuntime/src/lib/Kernel/Stubs/CD.cpp
@@ -38,6 +38,31 @@ namespace ps2_stubs
         uint32_t g_cdCallbackGp = 0u;
         uint32_t g_cdCallbackStackTop = 0u;
 
+        // P1c steady-state diagnostics, gated on PS2X_DIAG_PERIOD_MS (unset =
+        // compiled in, nothing printed). The tag mark lets the scheduler log
+        // when it starts the queued invocation (see EeScheduler::run()).
+        constexpr uint64_t kCdCallbackDiagTagBase = 0x4344434200000000ULL;
+
+        uint64_t diagPeriodMs()
+        {
+            static const uint64_t period = [] {
+                if (const char *env = std::getenv("PS2X_DIAG_PERIOD_MS"))
+                {
+                    if (env[0] != '\0')
+                    {
+                        char *end = nullptr;
+                        const unsigned long long parsed = std::strtoull(env, &end, 10);
+                        if (end != env)
+                        {
+                            return static_cast<uint64_t>(parsed);
+                        }
+                    }
+                }
+                return static_cast<uint64_t>(0);
+            }();
+            return period;
+        }
+
         void queueCdCallback(R5900Context *ctx, PS2Runtime *runtime, uint32_t func)
         {
             (void)ctx;
@@ -47,12 +72,18 @@ namespace ps2_stubs
             }
             GuestInvocation invocation{};
             invocation.kind = GuestInvocationKind::Interrupt;
+            invocation.tag = kCdCallbackDiagTagBase | static_cast<uint64_t>(func);
             invocation.context.pc = g_cdCallbackFn;
             SET_GPR_U32(&invocation.context, 4, func);
             SET_GPR_U32(&invocation.context, 5, 0u);
             SET_GPR_U32(&invocation.context, 28, g_cdCallbackGp);
             SET_GPR_U32(&invocation.context, 29, g_cdCallbackStackTop);
             SET_GPR_U32(&invocation.context, 31, 0u);
+            if (diagPeriodMs() != 0u)
+            {
+                std::cerr << "[cd:callback] queued func=" << func
+                          << " cb=0x" << std::hex << g_cdCallbackFn << std::dec << std::endl;
+            }
             runtime->eeScheduler().queueInvocation(std::move(invocation));
         }
 
@@ -234,6 +265,13 @@ namespace ps2_stubs
         const uint32_t a0 = getRegU32(ctx, 4); // usually lbn
         const uint32_t a1 = getRegU32(ctx, 5); // usually sector count
         const uint32_t a2 = getRegU32(ctx, 6); // usually destination buffer
+        if (diagPeriodMs() != 0u)
+        {
+            std::cerr << "[diag:cd] sceCdRead lbn=0x" << std::hex << a0
+                      << " sectors=" << std::dec << a1
+                      << " buf=0x" << std::hex << a2
+                      << " ret=0x" << ctx->pc << std::dec << std::endl;
+        }
 
         struct CdReadArgs
         {
@@ -440,6 +478,12 @@ namespace ps2_stubs
         const uint32_t stackAddr = getRegU32(ctx, 5);
         const uint32_t stackSize = getRegU32(ctx, 6);
         g_cdCallbackStackTop = stackAddr + stackSize;
+        if (diagPeriodMs() != 0u)
+        {
+            std::cerr << "[diag:cd] sceCdInitEeCB stack=0x" << std::hex << stackAddr
+                      << " size=0x" << stackSize
+                      << " ret=0x" << ctx->pc << std::dec << std::endl;
+        }
         setReturnS32(ctx, 1);
     }
 
@@ -1026,3 +1070,4 @@ namespace ps2_stubs
         setReturnS32(ctx, 1);
     }
 }
+
diff --git a/ps2xRuntime/src/lib/Kernel/Syscalls/Dispatcher.cpp b/ps2xRuntime/src/lib/Kernel/Syscalls/Dispatcher.cpp
index 89de596..2c5a8ed 100644
--- a/ps2xRuntime/src/lib/Kernel/Syscalls/Dispatcher.cpp
+++ b/ps2xRuntime/src/lib/Kernel/Syscalls/Dispatcher.cpp
@@ -2,10 +2,107 @@
 #include "Dispatcher.h"
 #include "System.h"
 
+#include <cstdlib>
+
+namespace
+{
+    // P1c steady-state diagnostics, gated on PS2X_DIAG_PERIOD_MS (unset =
+    // compiled in, nothing printed, callers pay only a counter increment).
+    uint64_t diagPeriodMs()
+    {
+        static const uint64_t period = [] {
+            if (const char *env = std::getenv("PS2X_DIAG_PERIOD_MS"))
+            {
+                if (env[0] != '\0')
+                {
+                    char *end = nullptr;
+                    const unsigned long long parsed = std::strtoull(env, &end, 10);
+                    if (end != env)
+                    {
+                        return static_cast<uint64_t>(parsed);
+                    }
+                }
+            }
+            return static_cast<uint64_t>(0);
+        }();
+        return period;
+    }
+
+    uint64_t diagNowMs()
+    {
+        return static_cast<uint64_t>(std::chrono::duration_cast<std::chrono::milliseconds>(
+                                         std::chrono::steady_clock::now().time_since_epoch())
+                                         .count());
+    }
+
+    struct SyscallDiagEntry
+    {
+        uint64_t count = 0;
+        uint32_t firstPc = 0;
+        uint32_t lastPc = 0;
+    };
+
+    std::unordered_map<uint32_t, SyscallDiagEntry> g_diagSyscallCounts;
+    uint64_t g_diagSyscallLastMs = 0;
+    uint64_t g_diagSyscallBlock = 0;
+}
+
 namespace ps2_syscalls
 {
+    // Flushes the pending syscall histogram when a period boundary has
+    // passed. Called from the dispatch hook below and from the scheduler
+    // tick so a quiet steady state still emits (possibly empty) blocks.
+    void diagSyscallsPeriodicFlush()
+    {
+        const uint64_t period = diagPeriodMs();
+        if (period == 0u)
+        {
+            return;
+        }
+        const uint64_t now = diagNowMs();
+        if (g_diagSyscallLastMs == 0u)
+        {
+            g_diagSyscallLastMs = now;
+            return;
+        }
+        if (now - g_diagSyscallLastMs < period)
+        {
+            return;
+        }
+        g_diagSyscallLastMs = now;
+        std::vector<std::pair<uint32_t, SyscallDiagEntry>> sorted(g_diagSyscallCounts.begin(), g_diagSyscallCounts.end());
+        std::sort(sorted.begin(), sorted.end(),
+                  [](const auto &a, const auto &b) { return a.second.count > b.second.count; });
+        std::cerr << "[diag:syscalls] block=" << g_diagSyscallBlock++
+                  << " distinct=" << sorted.size()
+                  << " period_ms=" << period << std::endl;
+        for (size_t i = 0; i < sorted.size() && i < 20u; ++i)
+        {
+            std::cerr << "[diag:syscall] id=0x" << std::hex << sorted[i].first << std::dec
+                      << " count=" << sorted[i].second.count
+                      << " first=0x" << std::hex << sorted[i].second.firstPc
+                      << " last=0x" << std::hex << sorted[i].second.lastPc << std::dec << std::endl;
+        }
+        g_diagSyscallCounts.clear();
+    }
+
     bool dispatchNumericSyscall(uint32_t syscallNumber, uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
     {
+        static uint64_t s_diagTick = 0;
+        ++s_diagTick;
+        if (diagPeriodMs() != 0u)
+        {
+            const uint32_t callerPc = (ctx != nullptr) ? ctx->pc : 0u;
+            SyscallDiagEntry &entry = g_diagSyscallCounts[syscallNumber];
+            if (entry.count == 0u)
+            {
+                entry.firstPc = callerPc;
+            }
+            entry.lastPc = callerPc;
+            ++entry.count;
+            diagSyscallsPeriodicFlush();
+        }
+
         if (dispatchSyscallOverride(syscallNumber, rdram, ctx, runtime))
         {
             return true;
diff --git a/ps2xRuntime/src/lib/ps2_runtime.cpp b/ps2xRuntime/src/lib/ps2_runtime.cpp
index 0e8471e..2ccc4a5 100644
--- a/ps2xRuntime/src/lib/ps2_runtime.cpp
+++ b/ps2xRuntime/src/lib/ps2_runtime.cpp
@@ -19,6 +19,7 @@
 #include <algorithm>
 #include <array>
 #include <cctype>
+#include <cstdlib>
 #include <cstring>
 #include <limits>
 #include <chrono>
@@ -26,6 +27,7 @@
 #include <thread>
 #include <unordered_map>
 #include <sstream>
+#include <vector>
 
 namespace ps2_stubs
 {
@@ -1031,6 +1033,46 @@ void PS2Runtime::configureIoPathsFromElf(const std::string &elfPath)
 
 namespace
 {
+    // P1c steady-state diagnostics, gated on PS2X_DIAG_PERIOD_MS (unset =
+    // compiled in, nothing printed, callers pay only a counter increment).
+    uint64_t diagPeriodMs()
+    {
+        static const uint64_t period = [] {
+            if (const char *env = std::getenv("PS2X_DIAG_PERIOD_MS"))
+            {
+                if (env[0] != '\0')
+                {
+                    char *end = nullptr;
+                    const unsigned long long parsed = std::strtoull(env, &end, 10);
+                    if (end != env)
+                    {
+                        return static_cast<uint64_t>(parsed);
+                    }
+                }
+            }
+            return static_cast<uint64_t>(0);
+        }();
+        return period;
+    }
+
+    uint64_t diagNowMs()
+    {
+        return static_cast<uint64_t>(std::chrono::duration_cast<std::chrono::milliseconds>(
+                                         std::chrono::steady_clock::now().time_since_epoch())
+                                         .count());
+    }
+
+    struct CallDiagEntry
+    {
+        uint64_t count = 0;
+        uint32_t firstRa = 0;
+        uint32_t lastRa = 0;
+    };
+
+    std::unordered_map<uint32_t, CallDiagEntry> g_diagCallCounts;
+    uint64_t g_diagCallLastMs = 0;
+    uint64_t g_diagCallBlock = 0;
+
     bool generatedFunctionTableSlot(uint32_t address, uint32_t &slot)
     {
         if ((address & 3u) != 0u || g_ps2RecompiledFunctionTableSlotCount == 0u)
@@ -1049,6 +1091,44 @@ namespace
     }
 }
 
+// Flushes the pending call-target histogram when a period boundary has
+// passed. Called from the dispatchGuestBranch hook below and from the
+// scheduler tick so a quiet steady state still emits (possibly empty)
+// blocks.
+void diagCallsPeriodicFlush()
+{
+    const uint64_t period = diagPeriodMs();
+    if (period == 0u)
+    {
+        return;
+    }
+    const uint64_t now = diagNowMs();
+    if (g_diagCallLastMs == 0u)
+    {
+        g_diagCallLastMs = now;
+        return;
+    }
+    if (now - g_diagCallLastMs < period)
+    {
+        return;
+    }
+    g_diagCallLastMs = now;
+    std::vector<std::pair<uint32_t, CallDiagEntry>> sorted(g_diagCallCounts.begin(), g_diagCallCounts.end());
+    std::sort(sorted.begin(), sorted.end(),
+              [](const auto &a, const auto &b) { return a.second.count > b.second.count; });
+    std::cerr << "[diag:stubs] block=" << g_diagCallBlock++
+              << " distinct=" << sorted.size()
+              << " period_ms=" << period << std::endl;
+    for (size_t i = 0; i < sorted.size() && i < 30u; ++i)
+    {
+        std::cerr << "[diag:stub] target=0x" << std::hex << sorted[i].first << std::dec
+                  << " count=" << sorted[i].second.count
+                  << " firstRa=0x" << std::hex << sorted[i].second.firstRa
+                  << " lastRa=0x" << std::hex << sorted[i].second.lastRa << std::dec << std::endl;
+    }
+    g_diagCallCounts.clear();
+}
+
 bool PS2Runtime::replaceFunction(uint32_t address, RecompiledFunction func)
 {
     uint32_t slot = 0u;
@@ -1354,6 +1434,24 @@ bool PS2Runtime::dispatchGuestBranch(uint8_t *rdram,
         return false;
     }
 
+    // P1c HLE stub/call histogram at the register_functions.cpp binding
+    // lookup (lookupFunction below resolves the guest call target to the
+    // registered host function). Counts per call target with first/last $ra.
+    static uint64_t s_diagCallTick = 0;
+    ++s_diagCallTick;
+    if (diagPeriodMs() != 0u)
+    {
+        const uint32_t callerRa = (ctx != nullptr) ? getRegU32(ctx, 31) : 0u;
+        CallDiagEntry &entry = g_diagCallCounts[targetPc];
+        if (entry.count == 0u)
+        {
+            entry.firstRa = callerRa;
+        }
+        entry.lastRa = callerRa;
+        ++entry.count;
+        diagCallsPeriodicFlush();
+    }
+
     RecompiledFunction targetFn = lookupFunction(targetPc);
     const uint32_t entryPc = ctx->pc;
     targetFn(rdram, ctx, this);
```

Binary shas (`/tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner`, sha256):

| Binary | Content | Boots |
|---|---|---|
| `ea4b352b…97b52c` | First Diag commit only (superseded before any boot) | none |
| `4ccb9c1e…79999` | + histogram flush fix | 1 |
| `381008af…21b906` | + CD entry logs; runner refreshed with `sub_003E3588` split | 2 |
| `b7fff2c5…289ee89` | runner refreshed with `sub_003E3968` split (no code change) | 3 |

Boot-1 last three period blocks, verbatim (`boot-p1c-1.log` tail):

```
[diag:threads] block=15 threads=1 period_ms=5000
[diag:thread] id=1 status=2 waitReason=2 waitId=6 pc=0x423de8 entry=0x100008 priority=100 scheduled=0
[diag:syscalls] block=14 distinct=0 period_ms=5000
[diag:stubs] block=14 distinct=0 period_ms=5000
[diag:threads] block=16 threads=1 period_ms=5000
[diag:thread] id=1 status=2 waitReason=2 waitId=6 pc=0x423de8 entry=0x100008 priority=100 scheduled=0
[diag:syscalls] block=15 distinct=0 period_ms=5000
[diag:stubs] block=15 distinct=0 period_ms=5000
[diag:threads] block=17 threads=1 period_ms=5000
[diag:thread] id=1 status=2 waitReason=2 waitId=6 pc=0x423de8 entry=0x100008 priority=100 scheduled=0
[diag:syscalls] block=16 distinct=0 period_ms=5000
[diag:stubs] block=16 distinct=0 period_ms=5000
```

Note: `[diag:threads]` block N pairs with `[diag:syscalls]`/`[diag:stubs]`
block N-1 (flushers arm on the first scheduler tick, one period later).

## P4-2. Loop table with quoted bodies

### Thread table (boot 1, all 18 dumps)

One thread in every dump: `id=1 status=2 (Waiting) waitReason=2
(Semaphore) waitId=6 pc=0x423de8 entry=0x100008 priority=100`.
`scheduled`: 1 in block 0 (initial scheduling), 0 in blocks 1–17.
pc is `0x423de8` in all 18 dumps.

### Syscall top 20 (boot 1, block 0, distinct=17)

| id | count | first | last |
|---|---|---|---|
| 0x2f | 32 | 0x423c98 | 0x423c98 |
| 0x44 | 12 | 0x423de8 | 0x423de8 |
| 0x42 | 11 | 0x423dc8 | 0x423dc8 |
| 0x74 | 8 | 0x42cbc8 | 0x42cbc8 |
| 0x5b | 6 | 0x42cbb8 | 0x42cbb8 |
| 0x40 | 6 | 0x423da8 | 0x423da8 |
| 0x64 | 4 | 0x424028 | 0x424028 |
| 0x3e | 3 | 0x423d88 | 0x423d88 |
| 0x4a | 2 | 0x423e48 | 0x423e48 |
| 0x4b | 2 | 0x423e58 | 0x423e58 |
| 0x14 | 1 | 0x423ae8 | 0x423ae8 |
| 0x10 | 1 | 0x423a88 | 0x423a88 |
| 0xfc | 1 | 0x423b28 | 0x423b28 |
| 0x5a | 1 | 0x42cb70 | 0x42cb70 |
| 0x29 | 1 | 0x423c38 | 0x423c38 |
| 0x3d | 1 | 0x100198 | 0x100198 |
| 0x3c | 1 | 0x10017c | 0x10017c |

Trampoline map for the syscall caller pcs: `0x423c98`→`sub_00423C90`
(GetThreadId 0x2F), `0x423de8`→`sub_00423DE0` (WaitSema 0x44),
`0x423dc8`→`sub_00423DC0` (SignalSema 0x42), `0x423da8`→`sub_00423DA0`
(CreateSema 0x40), `0x423d88`→`sub_00423D80` (EndOfHeap 0x3E),
`0x423b28`→`sub_00423B20` (SetAlarm 0xFC), `0x423dd8`→`sub_00423DD0`
(iSignalSema -0x43; zero calls in boot 1), `0x423db8`→`sub_00423DB0`
(DeleteSema 0x41; zero calls in boot 1). Each is a 3-instruction wrapper
(`addiu $v1,$zero,imm`; `syscall 0`; `jr $ra`).

### Stub top 30 (boot 1, block 0, distinct=251)

| target | fn | count | firstRa | lastRa |
|---|---|---|---|---|
| 0x31bf60 | sub_0031BF60 | 640 | 0x392e2c | 0x392e2c |
| 0x317618 | sub_00317618 | 583 | 0x317684 | 0x317684 |
| 0x317670 | sub_00317670 | 583 | 0x284770 | 0x21c5ac |
| 0x2cbcc8 | sub_002CBCC8 | 414 | 0x250784 | 0x24d2b4 |
| 0x2ca258 | sub_002CA258 | 414 | 0x2cd2c0 | 0x2cd92c |
| 0x416210 | sub_00416210 | 342 | 0x393958 | 0x21c5a0 |
| 0x2cdce8 | sub_002CDCE8 | 202 | 0x25033c | 0x24d154 |
| 0x416810 | sub_00416810 | 162 | 0x318308 | 0x4189ac |
| 0x2cd8f8 | sub_002CD8F8 | 134 | 0x2502d8 | 0x24d194 |
| 0x418958 | sub_00418958 | 133 | 0x41cae8 | 0x41cae8 |
| 0x370b60 | sub_00370B60 | 64 | 0x3714cc | 0x3714cc |
| 0x3714b8 | sub_003714B8 | 64 | 0x2f758c | 0x2f758c |
| 0x2f7a68 | sub_002F7A68 | 64 | 0x370b90 | 0x370b90 |
| 0x2cf908 | sub_002CF908 | 35 | 0x2cf8c0 | 0x2d03a0 |
| 0x41605c | sub_0041605C | 35 | 0x41d71c | 0x41d71c |
| 0x423c90 | sub_00423C90 | 32 | 0x3e5028 | 0x3e5774 |
| 0x2ced20 | sub_002CED20 | 28 | 0x2d0320 | 0x2d0350 |
| 0x2caa58 | sub_002CAA58 | 25 | 0x250254 | 0x24cf14 |
| 0x2cd2a0 | sub_002CD2A0 | 18 | 0x250294 | 0x24cf44 |
| 0x2cd350 | sub_002CD350 | 18 | 0x2502a8 | 0x24cf58 |
| 0x41ca70 | sub_0041CA70 | 14 | 0x41b718 | 0x41b718 |
| 0x31ed60 | sub_0031ED60 | 14 | 0x31f470 | 0x31f4c4 |
| 0x417828 | sub_00417828 | 14 | 0x319680 | 0x319700 |
| 0x41b658 | sub_0041B658 | 14 | 0x417894 | 0x417894 |
| 0x423de0 | sub_00423DE0 | 12 | 0x418ce0 | 0x3e35fc |
| 0x423dc0 | sub_00423DC0 | 11 | 0x418d3c | 0x3e57bc |
| 0x31ffd8 | sub_0031FFD8 | 10 | 0x31e3d8 | 0x31e3d8 |
| 0x3e6448 | sub_003E6448 | 10 | 0x2268cc | 0x3e6234 |
| 0x31e2d8 | sub_0031E2D8 | 9 | 0x31eca0 | 0x31eca0 |
| 0x31f2c8 | sub_0031F2C8 | 9 | 0x320068 | 0x320068 |

Caller-ra enclosures (first→last): `0x392e2c`→`sub_00392DF0`;
`0x317684`→`sub_00317670` (self-return); `0x284770`→`sub_00283E60`,
`0x21c5ac`→`sub_002127E8`; `0x250784`/`0x24d2b4`→`sub_002501E8`/
`sub_0024CEB0`; `0x2cd2c0`→`sub_002CD2A0`, `0x2cd92c`→`sub_002CD8F8`;
`0x393958`→`sub_00393048`, `0x21c5a0`→`sub_002127E8`; the sema-cluster
ras resolve in the semaphore table below.

### Quoted bodies (≤40 lines each, MIPS in comments)

Park site `sub_00423DE0` (WaitSema 0x44; thread pc `0x423de8` is the
resume point after the syscall):

```cpp
// Function: sub_00423DE0
// Address: 0x423de0 - 0x423df0
void sub_00423DE0_0x423de0(uint8_t* rdram, R5900Context* ctx, PS2Runtime *runtime) {
#ifdef PS2_FUNCTION_LOG_TRACKER
    PS_LOG_ENTRY("sub_00423DE0_0x423de0");
#endif

    switch (ctx->pc) {
        case 0x423de8u: goto label_423de8;
        default: break;
    }

    ctx->pc = 0x423de0u;

    // 0x423de0: 0x24030044  addiu       $v1, $zero, 0x44
    ctx->pc = 0x423de0u;
    SET_GPR_S32(ctx, 3, (int32_t)ADD32(GPR_U32(ctx, 0), 68));
    // 0x423de4: 0xc  syscall     0
    ctx->pc = 0x423de4u;
    ctx->pc = 0x423DE8u;
runtime->handleSyscall(rdram, ctx, 0x0u);
label_423de8:
    // 0x423de8: 0x3e00008  jr          $ra
    ctx->pc = 0x423DE8u;
    {
        const uint32_t jumpTarget = GPR_U32(ctx, 31);
        ctx->pc = jumpTarget;
        #if defined(PS2X_STRICT_RETURN_DIAGNOSTICS) && PS2X_STRICT_RETURN_DIAGNOSTICS
        (void)runtime->dispatchGuestBranch(rdram, ctx, jumpTarget, 0x423DE8u, 0u, PS2Runtime::GuestBranchKind::Return, "JR $ra");
        return;
        #else
        ctx->pc = jumpTarget;
```

`sub_00423DC0` (SignalSema 0x42), `sub_00423DA0` (CreateSema 0x40),
`sub_00423C90` (GetThreadId 0x2F) are the identical 3-instruction shape
with immediates `0x42`, `0x40`, `0x2F`.

Wait chain in `sub_003E35B0` (CreateSema→SetAlarm→WaitSema→DeleteSema;
parks at the `func_423DE0` call, ra `0x3e35fc`):

```cpp
    // 0x3e35ec: 0xc108ec8  jal         func_423B20
    ctx->pc = 0x3E35ECu;
    SET_GPR_U32(ctx, 31, 0x3E35F4u);
    ctx->pc = 0x3E35F0u;
    ctx->in_delay_slot = true;
    ctx->branch_pc = 0x3E35ECu;
    // 0x3e35f0: 0x220202d  daddu       $a0, $s1, $zero (Delay Slot)
    SET_GPR_U64(ctx, 4, (uint64_t)GPR_U64(ctx, 17) + (uint64_t)GPR_U64(ctx, 0));
    ctx->in_delay_slot = false;
    ctx->pc = 0x423B20u;
    if (!runtime->dispatchGuestBranch(rdram, ctx, 0x423B20u, 0x3E35ECu, 0x3E35F4u, PS2Runtime::GuestBranchKind::DirectCall, "JAL")) {
        return;
    }
    ctx->pc = 0x3E35F4u;
label_3e35f4:
    // 0x3e35f4: 0xc108f78  jal         func_423DE0
    ctx->pc = 0x3E35F4u;
    SET_GPR_U32(ctx, 31, 0x3E35FCu);
    ctx->pc = 0x3E35F8u;
    ctx->in_delay_slot = true;
    ctx->branch_pc = 0x3E35F4u;
    // 0x3e35f8: 0x200202d  daddu       $a0, $s0, $zero (Delay Slot)
    SET_GPR_U64(ctx, 4, (uint64_t)GPR_U64(ctx, 16) + (uint64_t)GPR_U64(ctx, 0));
    ctx->in_delay_slot = false;
    ctx->pc = 0x423DE0u;
    if (!runtime->dispatchGuestBranch(rdram, ctx, 0x423DE0u, 0x3E35F4u, 0x3E35FCu, PS2Runtime::GuestBranchKind::DirectCall, "JAL")) {
        return;
    }
    ctx->pc = 0x3E35FCu;
label_3e35fc:
    // 0x3e35fc: 0xc108f6c  jal         func_423DB0
```

Alarm callback entry `0x3E3588` in `sub_003E3538` (calls `func_423DD0`
= iSignalSema with `$a0=$a2`):

```cpp
        #endif
    }
    ctx->pc = 0x3E3584u;
    // 0x3e3584: 0x0  nop
    ctx->pc = 0x3e3584u;
    // NOP
    // 0x3e3588: 0x27bdfff0  addiu       $sp, $sp, -0x10
    ctx->pc = 0x3e3588u;
    SET_GPR_S32(ctx, 29, (int32_t)ADD32(GPR_U32(ctx, 29), 4294967280));
    // 0x3e358c: 0xffbf0000  sd          $ra, 0x0($sp)
    ctx->pc = 0x3e358cu;
    WRITE64(ADD32(GPR_U32(ctx, 29), 0), GPR_U64(ctx, 31));
    // 0x3e3590: 0xc108f74  jal         func_423DD0
    ctx->pc = 0x3E3590u;
    SET_GPR_U32(ctx, 31, 0x3E3598u);
    ctx->pc = 0x3E3594u;
    ctx->in_delay_slot = true;
    ctx->branch_pc = 0x3E3590u;
    // 0x3e3594: 0xc0202d  daddu       $a0, $a2, $zero (Delay Slot)
    SET_GPR_U64(ctx, 4, (uint64_t)GPR_U64(ctx, 6) + (uint64_t)GPR_U64(ctx, 0));
    ctx->in_delay_slot = false;
    ctx->pc = 0x423DD0u;
    if (!runtime->dispatchGuestBranch(rdram, ctx, 0x423DD0u, 0x3E3590u, 0x3E3598u, PS2Runtime::GuestBranchKind::DirectCall, "JAL")) {
        return;
    }
    ctx->pc = 0x3E3598u;
label_3e3598:
    // 0x3e3598: 0xf  sync
    ctx->pc = 0x3e3598u;
    // SYNC instruction - memory barrier
```

Comparator leaf at `0x3e3968` in `sub_003E3758` (frameless, `jr $ra`
exits at `0x3e3990/0x3e3998/0x3e39a0`):

```cpp
        ctx->pc = jumpTarget;
        return;
        #endif
    }
    ctx->pc = 0x3E3968u;
    // 0x3e3968: 0x9c830000  lwu         $v1, 0x0($a0)
    ctx->pc = 0x3e3968u;
    SET_GPR_U32(ctx, 3, READ32(ADD32(GPR_U32(ctx, 4), 0)));
    // 0x3e396c: 0x9ca20000  lwu         $v0, 0x0($a1)
    ctx->pc = 0x3e396cu;
    SET_GPR_U32(ctx, 2, READ32(ADD32(GPR_U32(ctx, 5), 0)));
    // 0x3e3970: 0x62182f  dsubu       $v1, $v1, $v0
    ctx->pc = 0x3e3970u;
    SET_GPR_U64(ctx, 3, GPR_U64(ctx, 3) - GPR_U64(ctx, 2));
    // 0x3e3974: 0x460000a  bltz        $v1, . + 4 + (0xA << 2)
    ctx->pc = 0x3E3974u;
    {
        const bool branch_taken_0x3e3974 = (GPR_S32(ctx, 3) < 0);
        ctx->pc = 0x3E3978u;
        ctx->in_delay_slot = true;
        ctx->branch_pc = 0x3E3974u;
        // 0x3e3978: 0x2402ffff  addiu       $v0, $zero, -0x1 (Delay Slot)
        SET_GPR_S32(ctx, 2, (int32_t)ADD32(GPR_U32(ctx, 0), 4294967295));
        ctx->in_delay_slot = false;
        if (branch_taken_0x3e3974) {
            ctx->pc = 0x3E39A0u;
            goto label_3e39a0;
        }
    }
    ctx->pc = 0x3E397Cu;
    // 0x3e397c: 0x1c600006  bgtz        $v1, . + 4 + (0x6 << 2)
    ctx->pc = 0x3E397Cu;
    {
        const bool branch_taken_0x3e397c = (GPR_S32(ctx, 3) > 0);
        ctx->pc = 0x3E3980u;
```

Top-5 startup callees (constructor phase, not the wait):

`sub_0031BF60` (float compare/select):

```cpp
// Address: 0x31bf60 - 0x31c040
void sub_0031BF60_0x31bf60(uint8_t* rdram, R5900Context* ctx, PS2Runtime *runtime) {
#ifdef PS2_FUNCTION_LOG_TRACKER
    PS_LOG_ENTRY("sub_0031BF60_0x31bf60");
#endif

    ctx->pc = 0x31bf60u;

    // 0x31bf60: 0x44800800  mtc1        $zero, $f1
    ctx->pc = 0x31bf60u;
    { uint32_t bits = GPR_U32(ctx, 0); std::memcpy(&ctx->f[1], &bits, sizeof(bits)); }
    // 0x31bf64: 0xc780d158  lwc1        $f0, -0x2EA8($gp)
    ctx->pc = 0x31bf64u;
    { uint32_t bits = READ32(ADD32(GPR_U32(ctx, 28), 4294955352)); float f; std::memcpy(&f, &bits, sizeof(f)); ctx->f[0] = f; }
    // 0x31bf68: 0x46016034  c.lt.s      $f12, $f1
    ctx->pc = 0x31bf68u;
    ctx->fcr31 = (FPU_C_OLT_S(ctx->f[12], ctx->f[1])) ? (ctx->fcr31 | 0x800000) : (ctx->fcr31 & ~0x800000);
    // 0x31bf6c: 0x0  nop
    ctx->pc = 0x31bf6cu;
    // NOP
    // 0x31bf70: 0x45000005  bc1f        . + 4 + (0x5 << 2)
    ctx->pc = 0x31BF70u;
    {
        const bool branch_taken_0x31bf70 = (!(ctx->fcr31 & 0x800000));
        ctx->pc = 0x31BF74u;
        ctx->in_delay_slot = true;
        ctx->branch_pc = 0x31BF70u;
        // 0x31bf74: 0x46006042  mul.s       $f1, $f12, $f0 (Delay Slot)
        ctx->f[1] = FPU_MUL_S(ctx->f[12], ctx->f[0]);
        ctx->in_delay_slot = false;
        if (branch_taken_0x31bf70) {
            ctx->pc = 0x31BF88u;
            goto label_31bf88;
        }
    }
    ctx->pc = 0x31BF78u;
    // 0x31bf78: 0x3c013f00  lui         $at, 0x3F00
    ctx->pc = 0x31bf78u;
    SET_GPR_S32(ctx, 1, (int32_t)((uint32_t)16128 << 16));
    // 0x31bf7c: 0x44810000  mtc1        $at, $f0
```

`sub_00317670` (calls `func_317618`, ra `0x317684`):

```cpp
// Function: sub_00317670
// Address: 0x317670 - 0x317690
void sub_00317670_0x317670(uint8_t* rdram, R5900Context* ctx, PS2Runtime *runtime) {
#ifdef PS2_FUNCTION_LOG_TRACKER
    PS_LOG_ENTRY("sub_00317670_0x317670");
#endif

    switch (ctx->pc) {
        case 0x317684u: goto label_317684;
        default: break;
    }

    ctx->pc = 0x317670u;

    // 0x317670: 0x27bdffe0  addiu       $sp, $sp, -0x20
    ctx->pc = 0x317670u;
    SET_GPR_S32(ctx, 29, (int32_t)ADD32(GPR_U32(ctx, 29), 4294967264));
    // 0x317674: 0x80282d  daddu       $a1, $a0, $zero
    ctx->pc = 0x317674u;
    SET_GPR_U64(ctx, 5, (uint64_t)GPR_U64(ctx, 4) + (uint64_t)GPR_U64(ctx, 0));
    // 0x317678: 0xffbf0010  sd          $ra, 0x10($sp)
    ctx->pc = 0x317678u;
    WRITE64(ADD32(GPR_U32(ctx, 29), 16), GPR_U64(ctx, 31));
    // 0x31767c: 0xc0c5d86  jal         func_317618
    ctx->pc = 0x31767Cu;
    SET_GPR_U32(ctx, 31, 0x317684u);
    ctx->pc = 0x317680u;
    ctx->in_delay_slot = true;
    ctx->branch_pc = 0x31767Cu;
    // 0x317680: 0x3a0202d  daddu       $a0, $sp, $zero (Delay Slot)
    SET_GPR_U64(ctx, 4, (uint64_t)GPR_U64(ctx, 29) + (uint64_t)GPR_U64(ctx, 0));
    ctx->in_delay_slot = false;
    ctx->pc = 0x317618u;
    if (!runtime->dispatchGuestBranch(rdram, ctx, 0x317618u, 0x31767Cu, 0x317684u, PS2Runtime::GuestBranchKind::DirectCall, "JAL")) {
        return;
    }
    ctx->pc = 0x317684u;
label_317684:
    // 0x317684: 0xdfbf0010  ld          $ra, 0x10($sp)
    ctx->pc = 0x317684u;
```

`sub_00317618` (byte loop over `$a1`):

```cpp
// Address: 0x317618 - 0x317670
void sub_00317618_0x317618(uint8_t* rdram, R5900Context* ctx, PS2Runtime *runtime) {
#ifdef PS2_FUNCTION_LOG_TRACKER
    PS_LOG_ENTRY("sub_00317618_0x317618");
#endif

    switch (ctx->pc) {
        case 0x317630u: goto label_317630;
        default: break;
    }

    ctx->pc = 0x317618u;

    // 0x317618: 0x80a20000  lb          $v0, 0x0($a1)
    ctx->pc = 0x317618u;
    SET_GPR_S32(ctx, 2, (int8_t)READ8(ADD32(GPR_U32(ctx, 5), 0)));
    // 0x31761c: 0x182d  daddu       $v1, $zero, $zero
    ctx->pc = 0x31761cu;
    SET_GPR_U64(ctx, 3, (uint64_t)GPR_U64(ctx, 0) + (uint64_t)GPR_U64(ctx, 0));
    // 0x317620: 0x10400010  beqz        $v0, . + 4 + (0x10 << 2)
    ctx->pc = 0x317620u;
    {
        const bool branch_taken_0x317620 = (GPR_U64(ctx, 2) == GPR_U64(ctx, 0));
        ctx->pc = 0x317624u;
        ctx->in_delay_slot = true;
        ctx->branch_pc = 0x317620u;
        // 0x317624: 0x90a60000  lbu         $a2, 0x0($a1) (Delay Slot)
        SET_GPR_U32(ctx, 6, (uint8_t)READ8(ADD32(GPR_U32(ctx, 5), 0)));
        ctx->in_delay_slot = false;
        if (branch_taken_0x317620) {
            ctx->pc = 0x317664u;
            goto label_317664;
        }
    }
    ctx->pc = 0x317628u;
    // 0x317628: 0x3c07f000  lui         $a3, 0xF000
    ctx->pc = 0x317628u;
    SET_GPR_S32(ctx, 7, (int32_t)((uint32_t)61440 << 16));
    // 0x31762c: 0x0  nop
    ctx->pc = 0x31762cu;
```

`sub_002CBCC8` (store/compare chain):

```cpp
// Address: 0x2cbcc8 - 0x2cbd50
void sub_002CBCC8_0x2cbcc8(uint8_t* rdram, R5900Context* ctx, PS2Runtime *runtime) {
#ifdef PS2_FUNCTION_LOG_TRACKER
    PS_LOG_ENTRY("sub_002CBCC8_0x2cbcc8");
#endif

    switch (ctx->pc) {
        case 0x2cbcf0u: goto label_2cbcf0;
        default: break;
    }

    ctx->pc = 0x2cbcc8u;

    // 0x2cbcc8: 0x4c10002  bgez        $a2, . + 4 + (0x2 << 2)
    ctx->pc = 0x2CBCC8u;
    {
        const bool branch_taken_0x2cbcc8 = (GPR_S32(ctx, 6) >= 0);
        ctx->pc = 0x2CBCCCu;
        ctx->in_delay_slot = true;
        ctx->branch_pc = 0x2CBCC8u;
        // 0x2cbccc: 0xaca40000  sw          $a0, 0x0($a1) (Delay Slot)
        WRITE32(ADD32(GPR_U32(ctx, 5), 0), GPR_U32(ctx, 4));
        ctx->in_delay_slot = false;
        if (branch_taken_0x2cbcc8) {
            ctx->pc = 0x2CBCD4u;
            goto label_2cbcd4;
        }
    }
    ctx->pc = 0x2CBCD0u;
    // 0x2cbcd0: 0x8c860000  lw          $a2, 0x0($a0)
    ctx->pc = 0x2cbcd0u;
    SET_GPR_S32(ctx, 6, (int32_t)READ32(ADD32(GPR_U32(ctx, 4), 0)));
label_2cbcd4:
    // 0x2cbcd4: 0x8c880000  lw          $t0, 0x0($a0)
    ctx->pc = 0x2cbcd4u;
    SET_GPR_S32(ctx, 8, (int32_t)READ32(ADD32(GPR_U32(ctx, 4), 0)));
    // 0x2cbcd8: 0x2489000c  addiu       $t1, $a0, 0xC
    ctx->pc = 0x2cbcd8u;
    SET_GPR_S32(ctx, 9, (int32_t)ADD32(GPR_U32(ctx, 4), 12));
    // 0x2cbcdc: 0xc8102a  slt         $v0, $a2, $t0
```

`sub_002CA258` (struct init, `$v0=0x486F28`):

```cpp
// Function: sub_002CA258
// Address: 0x2ca258 - 0x2ca280
void sub_002CA258_0x2ca258(uint8_t* rdram, R5900Context* ctx, PS2Runtime *runtime) {
#ifdef PS2_FUNCTION_LOG_TRACKER
    PS_LOG_ENTRY("sub_002CA258_0x2ca258");
#endif

    ctx->pc = 0x2ca258u;

    // 0x2ca258: 0x3c020048  lui         $v0, 0x48
    ctx->pc = 0x2ca258u;
    SET_GPR_S32(ctx, 2, (int32_t)((uint32_t)72 << 16));
    // 0x2ca25c: 0x24030001  addiu       $v1, $zero, 0x1
    ctx->pc = 0x2ca25cu;
    SET_GPR_S32(ctx, 3, (int32_t)ADD32(GPR_U32(ctx, 0), 1));
    // 0x2ca260: 0x24426f28  addiu       $v0, $v0, 0x6F28
    ctx->pc = 0x2ca260u;
    SET_GPR_S32(ctx, 2, (int32_t)ADD32(GPR_U32(ctx, 2), 28456));
    // 0x2ca264: 0xac830004  sw          $v1, 0x4($a0)
    ctx->pc = 0x2ca264u;
    WRITE32(ADD32(GPR_U32(ctx, 4), 4), GPR_U32(ctx, 3));
    // 0x2ca268: 0xac820010  sw          $v0, 0x10($a0)
    ctx->pc = 0x2ca268u;
    WRITE32(ADD32(GPR_U32(ctx, 4), 16), GPR_U32(ctx, 2));
    // 0x2ca26c: 0x80102d  daddu       $v0, $a0, $zero
    ctx->pc = 0x2ca26cu;
    SET_GPR_U64(ctx, 2, (uint64_t)GPR_U64(ctx, 4) + (uint64_t)GPR_U64(ctx, 0));
    // 0x2ca270: 0xac850008  sw          $a1, 0x8($a0)
    ctx->pc = 0x2ca270u;
    WRITE32(ADD32(GPR_U32(ctx, 4), 8), GPR_U32(ctx, 5));
    // 0x2ca274: 0x3e00008  jr          $ra
    ctx->pc = 0x2CA274u;
    {
        const uint32_t jumpTarget = GPR_U32(ctx, 31);
        ctx->pc = 0x2CA278u;
        ctx->in_delay_slot = true;
        ctx->branch_pc = 0x2CA274u;
        // 0x2ca278: 0xac80000c  sw          $zero, 0xC($a0) (Delay Slot)
        WRITE32(ADD32(GPR_U32(ctx, 4), 12), GPR_U32(ctx, 0));
        ctx->in_delay_slot = false;
```

Waited object: kernel semaphore id 6 (`EeScheduler` semaphore object;
`waitReason=2` Semaphore, `waitId=6`). Writers: `SignalSema` (0x42) and
`iSignalSema` (-0x43). Boot-1 steady state: zero syscalls after block 0,
so nothing writes it after startup; the 12th `WaitSema` (from `0x3e35fc`)
has no matching signal (11 `SignalSema`, 0 `iSignalSema` in boot 1).

### INTC registration (single AddIntcHandler + single EnableIntc)

Runtime dispatch sites (`EeScheduler.cpp`): cause 2 on `VBlankStart`
(line 2046), cause 3 on `VBlankEnd` (line 2052), causes 9+timer on EE
timer interrupts (line 1896), `dispatchIrq` at line 1403. The `Dmac`
event case performs no dispatch.

| Static JAL site | $a0 (cause) | $a1 (handler) |
|---|---|---|
| `0x361FD0` (`sub_00361F98`) | `$s0` (saved reg) | `$s2` (saved reg) |
| `0x3C2170` (`sub_003C1B80`) | `2` | `0x3C1980` |
| `0x3E4C50` (`sub_003E4AF0`) | `0xA` (10) | `0x3E4DB8` |
| `0x40C1C4` (`sub_0040C028`) | `3` | `0x40CF88` |
| EnableIntc at `0x424918` (`sub_004248E8`) | `$s1` = incoming `$a0` of `sub_004248E8` | — |

The dynamic ra for the single `AddIntcHandler`/`EnableIntc` calls fell
below the top-30 stub print cutoff (count 1 each), so the firing site is
one of the rows above (not distinguished in this log).

### Semaphore order and id flow

| Fact | Value |
|---|---|
| `CreateSema` calls (boot 1) | 6, all via `0x423da8` (`sub_00423DA0`); dynamic ras below top-30 cutoff |
| Certain create | `sub_003E35B0`: stack struct (`+4=1`, `+8=0`, `+0x14=0`), `$a0=$sp`; id returned in `$v0`, stored to `$s0` |
| `WaitSema` calls (boot 1) | 12 via `0x423de0`; firstRa `0x418ce0` (`sub_00418CA8`, `$a0` = `lw 0x5248($v0)`), lastRa `0x3e35fc` (`sub_003E35B0`, `$a0=$s0`) |
| `SignalSema` calls (boot 1) | 11 via `0x423dc0`; firstRa `0x418d3c` (`sub_00418D08`, `$a0` = `lw 0x5248($v0)`), lastRa `0x3e57bc` (`sub_003E5760`, `$a0` = `lw 0xC($s0)`) |
| `iSignalSema` calls (boot 1) | 0 |
| Parked id | 6 = last of the six created ids; waited by the 12th `WaitSema` |
| Static `CreateSema` JAL sites | `sub_00319930`, `sub_0031A6B8`, `sub_00375A08`, `sub_003C1B80`, `sub_003C3300`, `sub_003E35B0`, `sub_003E4040`, `sub_003E5698`, `sub_003F5000`, `sub_00400C00`, `sub_0040B400`, `sub_0040C028` (≥12 static, 6 fired) |
| Signaller in boots 2–3 | Alarm callback `0x3E3588` via `func_423DD0` (iSignalSema): `target=0x423dd0` count=20, firstRa=lastRa=`0x3e3598` |

### CD registration and reads

| Fact | Value |
|---|---|
| TOML CD stubs | `sceCdCallback@0x4008A0`, `sceCdInitEeCB@0x400A78`, `sceCdRead@0x401DF8`, `sceCdSync@0x4013E8`, among others |
| Boot 1 `[cd:callback]` lines | 0 queued, 0 started |
| Boot 1 `sceCdCallback`/`sceCdInitEeCB`/`sceCdRead` invocations | Not determinable from the top-30 histogram (below cutoff or zero); entry logs added for boots 2–3 |
| Boots 2–3 `[diag:cd]` | `sceCdInitEeCB` 1x (`stack=0x51a480 size=0x800 ret=0x3e442c`); `sceCdRead` 20x (`buf=0x519c80 ret=0x3e3694`; lbn `0x10`,`0x105`–`0x117`,`0x108`); `sceCdCallback` 0x |

## P4-3. Fixes + ladders per boot

Map splits do not count against the three completion fixes (orchestrator
note); both fixes below are CSV map splits in the P3-4 class, changing no
tracked repo file, hence no `Pad:`/`MC:`/`CD:`/`SIF:` commit exists for
them. No HLE stub completion was implemented: the waited semaphore is
written by the guest alarm callback (iSignalSema), not by an HLE stub.

### Fix 1 — alarm-callback split (`sub_003E3588`)

| Item | Value |
|---|---|
| Cause | `SetAlarm` (`Sync.cpp` via `EeScheduler::setAlarm`, `EeScheduler.cpp:1208`) rejects handler `0x3E3588`: no `register_functions.cpp` slot (0 hits), so it returns `KE_ERROR`, no alarm is queued, and the 12th `WaitSema` (sema 6, from `0x3e35fc`) parks forever |
| Evidence | ELF word at `0x3E3588` = `0x27bdfff0` (`addiu $sp,$sp,-0x10`, prologue); callback body calls `func_423DD0` (iSignalSema) with `$a0=$a2` |
| CSV edit | `sub_003E3538,0x3e3538,0x3e35b0,0x78` → `sub_003E3538,0x3e3538,0x3e3588,0x50` + `sub_003E3588,0x3e3588,0x3e35b0,0x28` (row 7210; 8244→8245 data rows) |
| Recompile | `recomp-p1c-alarm.log`: discovered 8244 (one subsumed), recompiled 8068, stubs 176, skipped 0, decode failures 0, unhandled 0; entrypoints 391,299; warnings 3,596; fallbacks 724,860; `ret0@0x42c1f0` intact |
| Binary | `381008af…21b906` (runner refreshed, sidecars purged) |
| Boot | `boot-p1c-2.log`, 3 min, `PS2X_DIAG_PERIOD_MS=5000` |

Boot-2 ladder (new rung vs boot 1 in bold):

| Rung | Boot 2 |
|---|---|
| Process start / ELF load / exec start | Same as boot 8 |
| **First new syscall ids** | **0x20 CreateThread, 0x22 StartThread, 0x41 DeleteSema, 0xffffffbd iSignalSema** (block 0 distinct 17→21) |
| **WaitSema balance** | **32 = SignalSema 12 + iSignalSema 20** (park cleared) |
| **Second thread** | **id 2, entry `0x3e3be0` (in `sub_003E3B00`), priority 12** |
| **First CD reads** | **20x `sceCdRead` (`buf=0x519c80 ret=0x3e3694`) + 1x `sceCdInitEeCB`** |
| **First missing-target** | **IndirectCall JALR `0x4190b8`→`0x3e3968` (once; skipped, policy 1)** |
| First VIF MPG/MSCAL | None |
| First GIF kick | None |
| First presented frame | None (host window blank) |
| Crash | None |
| End state | Threads 1+2 Dormant (status 5, pc 0); quiet after block 0 |

Boot-1 → boot-2 delta: the only repo change between the boots is CD.cpp
entry logs (diagnostic-only); the behavioral change is the CSV split row
for `0x3E3588` plus recompile and runner refresh (untracked outputs). The guest site that signalled the semaphore is the alarm callback at
`0x3E3588`: all 20 `iSignalSema` calls come from ra `0x3e3598` (the JAL
at `0x3e3590` inside the callback). `sceCdCallback` was never invoked by
the guest (0 `[diag:cd]` lines), so Fix D queued nothing in any boot.

### Fix 2 — comparator-callback split (`sub_003E3968`)

| Item | Value |
|---|---|
| Cause | Boot-2 missing-target: JALR at `0x4190b8` (`sub_00418EF8`, target passed in `$a3`) to `0x3e3968`; no table slot (0 hits); skipped call stalls the CD state machine |
| Evidence | `0x3e3968` follows a `jr $ra` (0x3e3960) and starts a frameless compare leaf (`lwu $v1,0($a0)` … `jr $ra` exits); next prologue at `0x3e39a8` |
| CSV edit | `sub_003E3758,0x3e3758,0x3e39a8,0x250` → `sub_003E3758,0x3e3758,0x3e3968,0x210` + `sub_003E3968,0x3e3968,0x3e39a8,0x40` (8245→8246 data rows) |
| Recompile | `recomp-p1c-cmp.log`: discovered 8245 (one subsumed), recompiled 8069, stubs 176, skipped 0, decode failures 0, unhandled 0; entrypoints 391,299; warnings 3,596; fallbacks 724,860 |
| Binary | `b7fff2c5…289ee89` (runner refreshed, sidecars purged) |
| Boot | `boot-p1c-3.log`, 3 min, `PS2X_DIAG_PERIOD_MS=5000` |

Boot-3 ladder (new rung vs boot 2 in bold):

| Rung | Boot 3 |
|---|---|
| **Missing-target lines** | **None (gap closed)** |
| **Comparator calls** | **`target=0x3e3968` count=1135, ras `0x4190c0`→`0x41903c`** |
| Stub distinct (block 0) | 275 (vs 274) |
| Syscall ids | Same 21 as boot 2 (no new ids) |
| CD lines | Same 21 `[diag:cd]` lines as boot 2 |
| First VIF MPG/MSCAL | None |
| First GIF kick | None |
| First presented frame | None |
| Crash | None |
| End state | Threads 1+2 Dormant (status 5, pc 0); quiet after block 0 |

Missing-target sweep over all three `boot-p1c-*.log` files: exactly one
(`0x3e3968`, boot 2), fixed; boot 3 reports none, so no further splits
were made. No third completion iteration was run: the end state has no
Waiting thread (nothing for an HLE stub to complete).

Threads went Dormant through return, not through a syscall: boot-2 and
boot-3 block-0 id sets contain no `ExitThread` (0x04/0x23),
`ExitDeleteThread` (0x24), `TerminateThread` (0x25), `DeleteThread`
(0x21) or `ReferThreadStatus`-adjacent exits; both threads show `pc=0x0`
with empty invocation stacks (`makeDormant` on `pc==0` in
`EeScheduler::run()`).

## P4-4. Binaries and commits

| Commit | Files | Push |
|---|---|---|
| `25eaf77` Diag: steady-state stall diagnostics | `EeScheduler.cpp`, `CD.cpp`, `Dispatcher.cpp`, `ps2_runtime.cpp` (+313/-9) | `04905db..25eaf77` |
| `3a1156b` Diag: flush histograms on scheduler tick | `EeScheduler.cpp`, `Dispatcher.cpp`, `ps2_runtime.cpp` (+94/-53) | `25eaf77..3a1156b` |
| `dbf0080` Diag: CD entry logs | `CD.cpp` (+14) | `3a1156b..dbf0080` |
| Map splits (2x) | `$W/P1/ssx3-functions.csv` only (outside the repo; 8244→8245→8246 rows); runner outputs refreshed locally, never added | no commit (no tracked file changed) |
| This report | `local/research/P1/REPORT.md` (`[P1c]` prefix, same trailers) | after commit |

All pushes to `fork ssx3`, verified via `git show --stat`.
`register_functions.cpp` remains a local modification, never added.
Trailers on every commit: `Co-Authored-By: Claude Fable 5.1
<noreply@anthropic.com>`, `Claude-Session:
https://claude.ai/code/session_01H9JEyNpHtANpAU2dB1YuC7`.

## P4-5. Exact commands

```
printf 'P1c\n' > /tmp/ssx3-host-lease   (absent before; removed at end)
cmake --build /tmp/p1-link/runtime --target ps2EntryRunner   (x3: Diag, flush fix, CD logs)
shasum -a 256 /tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner   (after each build)
git add <the 4 files>; git commit -m "Diag: …" (trailers); git push fork ssx3   (x3)
cd "$W/P1/run" && PS2X_CD_IMAGE="$W/SSX 3 (USA).iso" PS2X_DIAG_PERIOD_MS=5000 stdbuf -o0 -e0 /tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner "$W/P1/cd/SLUS_207.72" > boot-p1c-N.log 2>&1   (N=1: 90 s; N=2,3: 180 s; foreground, killed by timeout)
python3 CSV split edits (2x); cp ssx3-functions.csv /tmp/ssx3-functions.csv.p1c-bak (before first split)
cd "$W/P1" && ./bin/ps2_recomp ssx3.toml | tee recomp-p1c-alarm.log / recomp-p1c-cmp.log
cp -X $W/P1/output/*.{cpp,h} $W/PS2Recomp/ps2xRuntime/src/runner/; sidecar purges
log reads: grep/awk/sed/tail on closed logs only (never piped through head while running)
ELF word reads: python3 struct reads at file offset 0x1000 + (va - 0x100000)
```

## P4-6. What I could not do

- Boot-1 `sceCdCallback`/`sceCdInitEeCB`/`sceCdRead` counts: not in the
  top-30 print (below cutoff or zero); answered for boots 2–3 by entry logs.
- Dynamic ra for the single `AddIntcHandler`/`EnableIntc` calls: below the
  top-30 cutoff; reported as static candidate sites instead.
- Dynamic ras for the six boot-1 `CreateSema` calls: below the cutoff;
  only the `sub_003E35B0` instance is exactly placed.
- No `Pad:`/`MC:`/`CD:`/`SIF:` completion fix: the semaphore writer is the
  guest alarm callback, not an HLE stub; nothing was implemented in
  `Kernel/Stubs/` or `Syscalls/` beyond diagnostics.
- No VIF MPG/MSCAL, GIF kick, presented frame, or crash in any P1c boot;
  the post-fix park (two Dormant threads, no waiters) was not chased — no
  waiter exists for an HLE stub to complete.
- Time box: about 1 h 10 min of the 5 h box used.

# P1d report — Part 5 (brief local/muse/prompts/P1d.md)

Run wall: lease `P1d` acquired with `/tmp/ssx3-host-lease` absent;
sweep script written ~18:14, sweep recompile + runner refresh + normal
rebuild, boot 1 (`boot-p1d-1.log`, ~18:29–18:32, 185 s), CD payload
`Diag:` commit `f0b5040` + push, strict configure + build, boot 2
(`boot-p1d-2.log`, ~18:43–18:46, 185 s). Inside the 5-hour box.
`W` = `/Volumes/Extreme SSD/ps2recomp-spike`. No verdicts.

## P5-0. Lease record

| Event | Value |
|---|---|
| Start | `/tmp/ssx3-host-lease` absent; wrote `P1d` |
| Builds/boots | Lease kept as `P1d` across sweep recompile, normal rebuild, boot 1, payload commit, strict configure/build, boot 2 |
| Foreign leases / waits | None observed; no `waits.log` |
| `adb` | Not used |
| End | Removed after the `[P1d]` push, verified absent |

## P5-1. Thread-entry table (Step 1, no build)

`Kernel/Syscalls/Thread.cpp:269` (`StartThread`): returns `KE_ERROR`
when `!runtime->hasFunction(target->entry)`. `hasFunction` is a dense
per-address slot check (`ps2_runtime.cpp:1153-1157`): only exact map
starts have non-null slots.

| Address | Map row (`ssx3-functions.csv`, pre-sweep) | Prologue evidence (ELF words `0x3e3bd8–0x3e3be8`) | Verdict-free note |
|---|---|---|---|
| `0x3e3be0` | Not a map start; contained in line 7217 `sub_003E3B00,0x3e3b00,0x3e3d78,0x278` | `0x3e3bd8=0x27bd0070` (`addiu $sp,$sp,+0x70`), `0x3e3bdc=0x00000000` (`nop`), `0x3e3be0=0x27bdffa0` (`addiu $sp,$sp,-0x60`), `0x3e3be4=0x3c020052` (`lui $v0,0x52`), `0x3e3be8=0x7fb00050` (`sq $s0,0x50($sp)`); `T-8`/`T-4` are not `jr $ra`, `T-4` is not `j`/`jr` | Boot-p1c-3 block 0–34: thread 2 `entry=0x3e3be0 priority=12 scheduled=0`, status Dormant; block-0 syscall ids include `0x20 CreateThread` + `0x22 StartThread`; generated `sub_003E3B00` holds `0x3e3be0` as sequential code with no `case 0x3e3be0u` / `label_3e3be0` |

## P5-2. Sweep script + count table + recompile + boot-1 ladder

Script: `$W/P1/tools/codeptr_sweep.py` (kept in `$W/P1/tools/`, not
committed under `docs/research/`; quoted in full below). Inputs: ELF
`$W/P1/cd/SLUS_207.72`, CSV `$W/P1/ssx3-functions.csv`. `.text`
from ELF section headers: `[0x100000,0x42e020)`; loaded segments: one
`PT_LOAD` (`vaddr=0x100000 filesz=0x3a4bf4 memsz=0x43eadc
off=0x1000`). `j`/`jr` = opcode `0x02` / `SPECIAL` funct `0x08`;
branch = opcodes `0x01–0x07`, `SPECIAL 0x08/0x09`, COP1 `BC`
(fmt `0x08`). Collision check reads only the enclosing function's
`output/sub_*.cpp` (AppleDouble `._*` skipped) for lowercase
`case 0x<T>u` / `label_<T>`.

Count table (`$W/P1/sweep-counts.log`):

| Item | Value |
|---|---|
| Source (a) distinct / refs | 7995 / 20820 |
| Source (b) distinct / refs | 269 / 336 |
| Source (c) distinct | 42 (specials 3 + ctors 39) |
| Self-check ctors in (a) / in (b) | 39/39 / 0/39 |
| Self-check specials in (a) / in (b) | 0/3 / 3/3 |
| Self-check combined | all 39 ctors + 3 specials present in (a)/(b)/(c) |
| Map rows / starts (pre-sweep) | 8246 / 8245 |
| Already-mapped candidates | 462 |
| Proposed pre-collision / rejected | 3663 / 4124 |
| Collisions (internal branch target) | 2639 |
| Split | 1024 |
| New CSV | `$W/P1/ssx3-functions.sweep.csv`: 9270 data rows (+1024 splits) |

Top 20 rejected by frequency (address, refs, instruction word at T):

| Address | Freq | Instr |
|---|---|---|
| `0x1ce138` | 94 | `0x8e030008` |
| `0x417dd0` | 87 | `0x3c02004a` |
| `0x101880` | 79 | `0x03e00008` |
| `0x101080` | 71 | `0x4480a800` |
| `0x1cdb80` | 66 | `0x7bb00040` |
| `0x17da0c` | 63 | `0x7bb00060` |
| `0x1cc4f0` | 62 | `0x0c0731f2` |
| `0x1cd2a4` | 62 | `0x3c020044` |
| `0x425bd8` | 62 | `0x26520001` |
| `0x41d134` | 56 | `0x12a00200` |
| `0x1adc04` | 53 | `0x0c06a390` |
| `0x4182c8` | 52 | `0x32620080` |
| `0x37bc8c` | 51 | `0x0000382d` |
| `0x37bcd4` | 51 | `0x0000182d` |
| `0x37bd88` | 51 | `0x0000102d` |
| `0x37bf2c` | 51 | `0x8e235a3c` |
| `0x37bf80` | 51 | `0x8e235a40` |
| `0x108080` | 50 | `0x7bb000e0` |
| `0x1a8f7c` | 50 | `0x7bb00030` |
| `0x41bf28` | 50 | `0x12c00201` |

Collision list head (2639 total, first 50):
`0x1009e0, 0x100b90, 0x100f88, 0x1036a0, 0x103918, 0x108fa8,
0x10a768, 0x10a898, 0x10a8e8, 0x10c498, 0x10c4c0, 0x10c4dc,
0x10e770, 0x10e7d0, 0x10e830, 0x113b94, 0x113cc0, 0x113ce0,
0x113ce8, 0x113cf0, 0x113d10, 0x113d18, 0x113d30, 0x113d38,
0x113d48, 0x113d80, 0x113d88, 0x113db0, 0x113e18, 0x113e48,
0x113e50, 0x113e78, 0x123210, 0x1234d0, 0x1278c0, 0x1278e0,
0x1278e8, 0x127998, 0x128660, 0x128680, 0x1287b8, 0x128818,
0x1291e0, 0x1298e0, 0x12b7f0, 0x12b948, 0x131600, 0x145844,
0x14584c, 0x145854 ...`

Thread-entry split in the sweep CSV (lines 8155–8158):

| Line | Row |
|---|---|
| 8155 | `sub_003E39A8,0x3e39a8,0x3e3b00,0x158` |
| 8156 | `sub_003E3B00,0x3e3b00,0x3e3be0,0xe0` |
| 8157 | `sub_003E3BE0,0x3e3be0,0x3e3d78,0x198` |
| 8158 | `sub_003E3D78,0x3e3d78,0x3e4000,0x288` |

Recompile (`$W/P1/recomp-p1d-sweep.log`, CWD `$W/P1`,
`ghidra_output = "ssx3-functions.sweep.csv"`, `ret0@0x42c1f0` intact):

| Item | Value |
|---|---|
| Map loaded | 9270 functions from Ghidra map (one subsumed) |
| Functions discovered / processed | 9269 / 9269 |
| Recompiled / stubs / skipped | 9092 / 177 / 0 |
| Decode failures / unhandled | 0 / 0 |
| Additional entrypoints | 393727 |
| Warnings (unresolved JR/JALR) | 3598 |
| Fallback entries | 724964 |
| New output file | `output/sub_003E3BE0_0x3e3be0.cpp` (`0x3e3be0–0x3e3d78`) |
| Runner refresh | `cp -X output/*.{cpp,h}` to `ps2xRuntime/src/runner/` (9273 files), sidecars purged |
| Rebuild | `cmake --build /tmp/p1-link/runtime --target ps2EntryRunner`, exit 0 |
| Binary sha256 (boot 1) | `3a70f0f94eb3108054bdd1962adb28a45a4798878140e4d12f5b20bb4a39ac06` |

Boot-1 ladder (`$W/P1/run/boot-p1d-1.log`, 516 lines, 34807 B, 185 s,
`PS2X_DIAG_PERIOD_MS=5000`):

| Rung | Boot 1 |
|---|---|
| Process start / ELF load / exec start | Same as boot-p1c-3 (`0x100008`) |
| First new syscall ids vs boot-p1c-3 | None (block 0 distinct=21, same id set; top-20 print lists 20 of 21) |
| Second thread (block 0) | `id=2 entry=0x3e3be0 priority=12 scheduled=1 status=2 (Waiting) waitReason=2 (Semaphore) waitId=26 pc=0x423de8` (boot-p1c-3: `scheduled=0`, Dormant) |
| Thread table at last dump (block 77) | `id=1 status=5 waitReason=0 waitId=0 pc=0x0 entry=0x100008 priority=100 scheduled=0`; `id=2 status=2 waitReason=2 waitId=26 pc=0x423de8 entry=0x3e3be0 priority=12 scheduled=0` |
| CD lines | 20x `sceCdRead` (`buf=0x519c80 ret=0x3e3694`; lbn `0x10,0x105,0x106,0x107,0x109–0x117,0x108,0x117` order with `0x108` second-last) + 1x `sceCdInitEeCB` (`stack=0x51a480 size=0x800 ret=0x3e442c`) |
| Stub block 0 distinct | 275 (new vs boot-p1c-3 top rows: `0x4166f4` count=543 ras `0x3e38cc→0x3e3a3c`, `0x416810` 325, `0x3e6574` 205, `0x4162d0` 181, `0x3e36f8` 163; `0x3e3968` still 1135) |
| Missing targets | None (0 `missing-target` lines) |
| First VIF MPG/MSCAL | None |
| First GIF kick | None |
| First presented frame | None (host window blank) |
| Crash | None |

Sweep script `$W/P1/tools/codeptr_sweep.py`, quoted in full:

```python
#!/usr/bin/env python3
"""P1d code-pointer sweep (brief Step 2).

Inputs: ELF $W/P1/cd/SLUS_207.72, CSV map $W/P1/ssx3-functions.csv.
Collects every candidate code address T in .text from:
  (a) every 32-bit aligned word in every loaded segment whose value lies
      in [text_start, text_end) and is word-aligned,
  (b) every `lui rX, hi` followed within 4 instructions by
      `addiu rX, rX, lo` or `ori rX, rX, lo` whose composed value lies
      in .text,
  (c) the a1/handler arguments already seen: 0x3e3588 (SetAlarm),
      0x3e3968 (comparator), 0x3e3be0 (thread entry), the 39
      constructors (self-check: the script must find all of them).

A candidate becomes a split when T is not already a map start AND at
least one of:
  - instruction at T is `addiu $sp,$sp,-N`,
  - instruction at T-8 is `jr $ra` (0x03e00008) or at T-4 is `jr $ra`,
  - instruction at T-4 is `j`/`jr` and T-8 is not a branch.
Everything else is listed but not split.

Sanity: never split inside a function whose generated source shows the
address as an internal branch target (grep output/sub_*.cpp for
`case 0x<T>` / `L_<T>` labels; list collisions instead of splitting).

Output: new CSV (ssx3-functions.sweep.csv), and a table of counts
printed to stdout.
"""
import argparse
import bisect
import csv
import os
import struct
import sys
from collections import Counter, defaultdict

JR_RA = 0x03E00008

# 39 constructor entries from REPORT P3-4 (walk routine sub_0040FB88).
CONSTRUCTORS = [
    0x1448B8, 0x15C8F0, 0x168298, 0x176A28, 0x177E30, 0x179738,
    0x179FA8, 0x1E12B0, 0x222428, 0x2267F0, 0x247E20, 0x2501A8,
    0x251690, 0x254330, 0x2557C0, 0x269EA0, 0x26C438, 0x2722C0,
    0x284B80, 0x2BAEE8, 0x2BB0E0, 0x2BC4E0, 0x2C1688, 0x2D4060,
    0x2D48D0, 0x2F8370, 0x2F9818, 0x2FAE18, 0x30D498, 0x315A00,
    0x316878, 0x320B28, 0x341368, 0x361E10, 0x3970F8, 0x3A6648,
    0x3ADDA0, 0x3B07B8, 0x1001D8,
]
SPECIALS = [0x3E3588, 0x3E3968, 0x3E3BE0]


def parse_elf(elf_path):
    with open(elf_path, "rb") as f:
        hdr = f.read(52)
        e_phoff = struct.unpack("<I", hdr[0x1C:0x20])[0]
        e_phentsize = struct.unpack("<H", hdr[0x2A:0x2C])[0]
        e_phnum = struct.unpack("<H", hdr[0x2C:0x2E])[0]
        e_shoff = struct.unpack("<I", hdr[0x20:0x24])[0]
        e_shentsize = struct.unpack("<H", hdr[0x2E:0x30])[0]
        e_shnum = struct.unpack("<H", hdr[0x30:0x32])[0]
        e_shstrndx = struct.unpack("<H", hdr[0x32:0x34])[0]
        # program headers
        f.seek(e_phoff)
        segments = []
        for _ in range(e_phnum):
            vals = struct.unpack("<IIIIIIII", f.read(32))
            ptype, poff, pvaddr, ppaddr, pfilesz, pmemsz, pflags, palign = vals
            segments.append(
                dict(type=ptype, off=poff, vaddr=pvaddr,
                     filesz=pfilesz, memsz=pmemsz, flags=pflags))
        # section headers: find .text for [text_start, text_end)
        text_start = text_end = None
        if e_shoff != 0 and e_shnum != 0:
            def parse_sh(i):
                f.seek(e_shoff + i * e_shentsize)
                return struct.unpack("<IIIIIIIIII", f.read(40))
            str_vals = parse_sh(e_shstrndx)
            str_off, str_size = str_vals[4], str_vals[5]
            f.seek(str_off)
            strtab = f.read(str_size)

            def getname(ni):
                return strtab[ni:].split(b"\x00")[0].decode(errors="replace")
            for i in range(e_shnum):
                v = parse_sh(i)
                if getname(v[0]) == ".text":
                    text_start, text_end = v[3], v[3] + v[5]
        # file bytes
        f.seek(0)
        whole = f.read()
    loads = [s for s in segments if s["type"] == 1]
    return whole, loads, text_start, text_end


def read_word(whole, loads, va):
    for s in loads:
        if s["vaddr"] <= va < s["vaddr"] + s["filesz"] - 3:
            off = s["off"] + (va - s["vaddr"])
            return struct.unpack_from("<I", whole, off)[0]
    return None


def is_addiu_sp_neg(w):
    return (w is not None and (w & 0xFFFF0000) == 0x27BD0000
            and (w & 0x8000) != 0 and (w & 0xFFFF) != 0)


def is_j_or_jr(w):
    if w is None:
        return False
    op = (w >> 26) & 0x3F
    if op == 0x02:  # j
        return True
    if op == 0x00 and (w & 0x3F) == 0x08:  # jr (any rs)
        return True
    return False


def is_branch(w):
    if w is None:
        return False
    op = (w >> 26) & 0x3F
    if op in (0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07):
        return True
    if op == 0x00 and (w & 0x3F) in (0x08, 0x09):  # jr/jalr
        return True
    if op == 0x11 and ((w >> 21) & 0x1F) == 0x08:  # bc1f/bc1t
        return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("elf")
    ap.add_argument("csv_in")
    ap.add_argument("csv_out")
    ap.add_argument("--output-dir", default=None,
                    help="generated sub_*.cpp dir for collision check")
    args = ap.parse_args()

    whole, loads, text_start, text_end = parse_elf(args.elf)
    if text_start is None:
        print("no .text section", file=sys.stderr)
        sys.exit(1)
    print(f"text range: [{text_start:#010x},{text_end:#010x})")
    for s in loads:
        print(f"load: vaddr={s['vaddr']:#010x} filesz={s['filesz']:#x} "
              f"memsz={s['memsz']:#x} off={s['off']:#x}")

    # ---- (a) every aligned word in every loaded segment ----
    freq_a = Counter()
    for s in loads:
        base = s["off"]
        for off_in_seg in range(0, s["filesz"] - 3, 4):
            w = struct.unpack_from("<I", whole, base + off_in_seg)[0]
            if text_start <= w < text_end and (w & 3) == 0:
                freq_a[w] += 1
    set_a = set(freq_a.keys())
    print(f"source (a) distinct: {len(set_a)} refs: {sum(freq_a.values())}")

    # ---- (b) lui + addiu/ori within 4 ----
    # Build flat word list over the first load (contains .text); lui sites
    # restricted to .text.
    seg0 = loads[0]
    nwords = seg0["filesz"] // 4
    words = [struct.unpack_from("<I", whole, seg0["off"] + i * 4)[0]
             for i in range(nwords)]

    def va_of_index(i):
        return seg0["vaddr"] + i * 4
    text_i0 = (text_start - seg0["vaddr"]) // 4
    text_i1 = (text_end - seg0["vaddr"]) // 4
    text_i0 = max(text_i0, 0)
    text_i1 = min(text_i1, nwords)
    freq_b = Counter()
    sites_b = defaultdict(list)
    for i in range(text_i0, text_i1):
        w = words[i]
        if ((w >> 26) & 0x3F) != 0x0F:
            continue
        rt = (w >> 16) & 0x1F
        hi = w & 0xFFFF
        lui_va = va_of_index(i)
        for j in range(1, 5):
            if i + j >= nwords:
                break
            w2 = words[i + j]
            op = (w2 >> 26) & 0x3F
            comp = None
            kind = None
            if op == 0x09:  # addiu
                rs = (w2 >> 21) & 0x1F
                rtd = (w2 >> 16) & 0x1F
                if rs == rt and rtd == rt:
                    lo = w2 & 0xFFFF
                    slo = lo if lo < 0x8000 else lo - 0x10000
                    comp = ((hi << 16) + slo) & 0xFFFFFFFF
                    kind = "addiu"
            elif op == 0x0D:  # ori
                rs = (w2 >> 21) & 0x1F
                rtd = (w2 >> 16) & 0x1F
                if rs == rt and rtd == rt:
                    comp = ((hi << 16) | (w2 & 0xFFFF)) & 0xFFFFFFFF
                    kind = "ori"
            if comp is not None and text_start <= comp < text_end \
                    and (comp & 3) == 0:
                freq_b[comp] += 1
                sites_b[comp].append((lui_va, j, kind))
    set_b = set(freq_b.keys())
    print(f"source (b) distinct: {len(set_b)} refs: {sum(freq_b.values())}")

    # ---- (c) explicit ----
    set_c = set(SPECIALS + CONSTRUCTORS)
    print(f"source (c) distinct: {len(set_c)} "
          f"(specials={len(SPECIALS)} ctors={len(CONSTRUCTORS)})")

    # ---- self-check: script must find all 39 ctors + 3 specials ----
    combined = set_a | set_b | set_c
    missing_ctors = [a for a in CONSTRUCTORS if a not in combined]
    missing_specials = [a for a in SPECIALS if a not in combined]
    print(f"self-check ctors in (a): "
          f"{sum(1 for a in CONSTRUCTORS if a in set_a)}/39")
    print(f"self-check ctors in (b): "
          f"{sum(1 for a in CONSTRUCTORS if a in set_b)}/39")
    print(f"self-check specials in (a): "
          f"{sum(1 for a in SPECIALS if a in set_a)}/3")
    print(f"self-check specials in (b): "
          f"{sum(1 for a in SPECIALS if a in set_b)}/3")
    if missing_ctors or missing_specials:
        print(f"SELF-CHECK FAIL missing_ctors="
              f"{[hex(x) for x in missing_ctors]} missing_specials="
              f"{[hex(x) for x in missing_specials]}", file=sys.stderr)
        sys.exit(1)
    print("self-check: all 39 ctors + 3 specials present in (a)|(b)|(c)")

    # ---- map starts ----
    with open(args.csv_in, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    starts = set(int(r["start"], 16) for r in rows)
    print(f"map rows: {len(rows)} starts: {len(starts)}")

    # ---- split predicate ----
    cands = set_a | set_b | set_c
    # frequency for top-rejected: (a) refs, plus (b) refs
    freq_all = Counter()
    for k, v in freq_a.items():
        freq_all[k] += v
    for k, v in freq_b.items():
        freq_all[k] += v
    for k in set_c:
        freq_all.setdefault(k, 1)

    proposed = []
    rejected = []  # (T, reason)
    for T in sorted(cands):
        if T in starts:
            continue
        wT = read_word(whole, loads, T)
        wM4 = read_word(whole, loads, T - 4)
        wM8 = read_word(whole, loads, T - 8)
        c1 = is_addiu_sp_neg(wT)
        c2 = (wM8 == JR_RA) or (wM4 == JR_RA)
        c3 = is_j_or_jr(wM4) and not is_branch(wM8)
        if c1 or c2 or c3:
            proposed.append(T)
        else:
            rejected.append(T)
    print(f"already-mapped: {len(cands & starts)}")
    print(f"proposed pre-collision: {len(proposed)} "
          f"rejected: {len(rejected)}")

    # ---- collision check against generated sources ----
    outdir = args.output_dir
    if outdir is None:
        # sibling output/ next to the CSV
        outdir = os.path.join(os.path.dirname(
            os.path.abspath(args.csv_in)), "output")
    # enclosing-function lookup
    by_start = {int(r["start"], 16): (r["name"], int(r["end"], 16))
                for r in rows}
    sorted_starts = sorted(by_start.keys())

    def enclosing(T):
        i = bisect.bisect_right(sorted_starts, T) - 1
        if i < 0:
            return None
        s = sorted_starts[i]
        name, end = by_start[s]
        if T < end:
            return (s, name, end)
        return None

    cache = {}
    collisions = []
    survivors = []

    def file_text_for(start):
        if start in cache:
            return cache[start]
        try:
            names = os.listdir(outdir)
        except FileNotFoundError:
            cache[start] = None
            return None
        want = f"sub_{start:08x}_"
        hit = None
        for fn in names:
            if fn.startswith("._"):
                continue
            if fn.lower().startswith(want):
                hit = fn
                break
        if hit is None:
            cache[start] = None
            return None
        try:
            with open(os.path.join(outdir, hit), errors="ignore") as f:
                cache[start] = f.read().lower()
        except OSError:
            cache[start] = None
        return cache[start]

    for T in proposed:
        enc = enclosing(T)
        if enc is None:
            survivors.append(T)
            continue
        s, name, end = enc
        txt = file_text_for(s)
        if txt is None:
            survivors.append(T)
            continue
        if (f"case 0x{T:x}u" in txt) or (f"label_{T:x}" in txt):
            collisions.append(T)
        else:
            survivors.append(T)
    print(f"collisions (internal branch target): {len(collisions)}")
    print(f"split: {len(survivors)}")

    # ---- top 20 rejected by frequency ----
    rej_sorted = sorted(rejected, key=lambda t: (-freq_all.get(t, 0), t))
    print("top 20 rejected by frequency:")
    for T in rej_sorted[:20]:
        wT = read_word(whole, loads, T)
        print(f"  {T:#010x} freq={freq_all.get(T,0)} "
              f"instr={('none' if wT is None else f'{wT:#010x}')}")

    # ---- emit new CSV ----
    split_set = set(survivors)
    # group splits by enclosing original row
    splits_by_row = defaultdict(list)
    for T in survivors:
        enc = enclosing(T)
        if enc is None:
            print(f"warn: split {T:#x} has no enclosing row; skipping",
                  file=sys.stderr)
            continue
        splits_by_row[enc[0]].append(T)
    new_rows = []
    for r in rows:
        s = int(r["start"], 16)
        e = int(r["end"], 16)
        if s not in splits_by_row:
            new_rows.append((s, r["name"], e))
            continue
        cuts = sorted(splits_by_row[s])
        # sanity: cuts must lie strictly inside (s, e)
        cuts = [c for c in cuts if s < c < e]
        bounds = [s] + cuts + [e]
        for a, b in zip(bounds, bounds[1:]):
            nm = f"sub_{a:08X}"
            new_rows.append((a, nm, b))
    new_rows.sort()
    with open(args.csv_out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["name", "start", "end", "size"])
        for s, nm, e in new_rows:
            w.writerow([nm, f"{s:#x}", f"{e:#x}", f"{e - s:#x}"])
    print(f"wrote {args.csv_out}: {len(new_rows)} data rows "
          f"(+{len(new_rows) - len(rows)} splits)")
    if collisions:
        print(f"collision list ({len(collisions)}): "
              + ", ".join(f"{x:#x}" for x in sorted(collisions)[:50])
              + (" ..." if len(collisions) > 50 else ""))


if __name__ == "__main__":
    main()
```

## P5-3. Strict-return receipt + quoted body (Step 3, one build, one boot)

Strict plumbing: `ps2xRuntime/CMakeLists.txt:16`
(`option(PS2X_STRICT_RETURN_DIAGNOSTICS ... OFF)`) → `:420-424`
(`target_compile_definitions(ps2_runtime PUBLIC
PS2X_STRICT_RETURN_DIAGNOSTICS=1)`); consumed in
`ps2xRecomp/src/lib/control_flow_emitter.cpp:257-269`
(`emitExternalRegisterJumpDispatch`: `JR $ra` returns route through
`dispatchGuestBranch(..., GuestBranchKind::Return, "JR $ra")` instead
of a direct `ctx->pc` assignment). Non-call targets with no slot
report via `reportMissingFunction` (`ps2_runtime.cpp:1228-1384`).

Second build dir `/tmp/p1-link-strict` configured with
`-DPS2X_BUILD_STUDIO=OFF -DPS2X_BUILD_RUNTIME=ON
-DPS2X_BUILD_TEST=ON -DCMAKE_BUILD_TYPE=Release
-DPS2X_ENABLE_RUNTIME_LOGS=ON -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF
-DPS2X_ENABLE_IOP_RPC_TRACE=ON
-DPS2X_STRICT_RETURN_DIAGNOSTICS=ON` (configure exit 0, ~65 s);
same runner sources as boot 1 (sweep output, shared
`ps2xRuntime/src/runner/`). Build
`cmake --build /tmp/p1-link-strict --target ps2EntryRunner`, exit 0
(387 targets). Binary sha256:
`8da15c0c558d230c34dd0bd8cd47a41569e3bc1fdb9bf1a3420fb9ace99d4f21`
(normal binary for comparison:
`3a70f0f94eb3108054bdd1962adb28a45a4798878140e4d12f5b20bb4a39ac06`).

Boot 2 (`$W/P1/run/boot-p1d-2.log`, 537 lines, 37011 B, 185 s,
`PS2X_DIAG_PERIOD_MS=5000`, strict binary): the first diagnostic is
line 49, a Return to 0 before any stub/call histogram line exists.

| Item | Value |
|---|---|
| First diagnostic | `[guest-branch:missing-target] kind=Return op=JR $ra source=0x42cba8 target=0x0 pc=0x0 ra=0x0 sp=0x1fffff0 gp=0x4a30f0 ... codeRegion=no policy=1 trace=0x100008 -> 0x42c300 -> 0x42c0d8 -> 0x423da0 -> 0x423da0 -> 0x42c1f0 -> 0x42c7c8 -> 0x424b78 -> 0x42c410 -> 0x42c3a8 -> 0x423e50 -> 0x423e40 -> 0x423e50 -> 0x423e40 -> 0x42cbd0 -> 0x42cc00 -> 0x42cb68 -> 0x42cb78` |
| Function | `sub_0042CB78` (sweep CSV line 9262: `sub_0042CB78,0x42cb78,0x42cbb0,0x38`; pre-sweep line 8238 the address was inside `sub_0042CB68,0x42cb68,0x42cbb0,0x48`) |
| pc / ra / sp | `0x0` / `0x0` / `0x1fffff0` |
| Last 5 stub/call lines before it | None exist: lines 44–48 are `INFO: ... Sample rate`, `INFO: ... Periods size`, `INFO: TIMER`, `Loading segment ...`, `Registered code region ... / ELF file loaded ... / Starting execution ...`; line 50 is `INFO: TEXTURE: [ID 4] ...`; stub histogram starts at block 0 (line 122, distinct=275) |
| ELF at source | `0x42cba0=0x1440fff9` (`bnez`), `0x42cba4=0x00000000` (`nop`), `0x42cba8=0x03e00008` (`jr $ra`), `0x42cbac=0x0000102d` (`daddu $v0,$zero,$zero`, delay slot), `0x42cbb0=0x2403005b` (next function) |

Generated body around the return
(`$W/P1/output/sub_0042CB78_0x42cb78.cpp`, lines 63–102, 40 lines):

```cpp
    // 0x42cb98: 0xac830000  sw          $v1, 0x0($a0)
    ctx->pc = 0x42cb98u;
    WRITE32(ADD32(GPR_U32(ctx, 4), 0), GPR_U32(ctx, 3));
    // 0x42cb9c: 0x24840004  addiu       $a0, $a0, 0x4
    ctx->pc = 0x42cb9cu;
    SET_GPR_S32(ctx, 4, (int32_t)ADD32(GPR_U32(ctx, 4), 4));
    // 0x42cba0: 0x1440fff9  bnez        $v0, . + 4 + (-0x7 << 2)
    ctx->pc = 0x42CBA0u;
    {
        const bool branch_taken_0x42cba0 = (GPR_U64(ctx, 2) != GPR_U64(ctx, 0));
        if (branch_taken_0x42cba0) {
            ctx->pc = 0x42CB88u;
            if (runtime->eeCheckpointDue()) {
                return;
            }
            goto label_42cb88;
        }
    }
    ctx->pc = 0x42CBA8u;
label_42cba8:
    // 0x42cba8: 0x3e00008  jr          $ra
    ctx->pc = 0x42CBA8u;
    {
        const uint32_t jumpTarget = GPR_U32(ctx, 31);
        ctx->pc = 0x42CBACu;
        ctx->in_delay_slot = true;
        ctx->branch_pc = 0x42CBA8u;
        // 0x42cbac: 0x102d  daddu       $v0, $zero, $zero (Delay Slot)
        SET_GPR_U64(ctx, 2, (uint64_t)GPR_U64(ctx, 0) + (uint64_t)GPR_U64(ctx, 0));
        ctx->in_delay_slot = false;
        ctx->pc = jumpTarget;
        #if defined(PS2X_STRICT_RETURN_DIAGNOSTICS) && PS2X_STRICT_RETURN_DIAGNOSTICS
        (void)runtime->dispatchGuestBranch(rdram, ctx, jumpTarget, 0x42CBA8u, 0u, PS2Runtime::GuestBranchKind::Return, "JR $ra");
        return;
        #else
        ctx->pc = jumpTarget;
        return;
        #endif
    }
    ctx->pc = 0x42CBB0u;
```

Boot-2 ladder (remainder identical to boot 1 unless noted):

| Rung | Boot 2 |
|---|---|
| First diagnostic | Return to 0 above (1 `missing-target` line total; boot 1 had 0) |
| Syscalls block 0 | distinct=21, same id set as boot 1 |
| Stubs block 0 | distinct=275, same top rows as boot 1 |
| Threads first/last dump | block 0 `id=1 Dormant scheduled=22`, `id=2 Waiting sema 26 scheduled=1`; last block 77 same park as boot 1 (`id=2 status=2 waitReason=2 waitId=26 pc=0x423de8`) |
| CD lines | 21 entry + 20 payload lines (see P5-4) |
| First VIF MPG/MSCAL | None |
| First GIF kick | None |
| First presented frame | None |
| Crash | None |

No boot 3: the brief's `makeDormant`-caller logging fallback applies
only if no diagnostic fires; a diagnostic fired on line 49.

## P5-4. CD payload lines (Step 4, folded into boot 2)

Change: in `sceCdRead`'s `if (ok)` block (`Kernel/Stubs/CD.cpp`),
after the read is served, print the first 8 bytes of the destination
buffer in hex (`selected.buf & PS2_RAM_MASK`, `PS2_RAM_SIZE`-guarded),
gated on `PS2X_DIAG_PERIOD_MS`, committed as `Diag:` (`f0b5040`),
present in the strict binary only (boot 1 predates it).

| LBN | Entry line | Payload line |
|---|---|---|
| `0x10` (PVD) | `[diag:cd] sceCdRead lbn=0x10 sectors=1 buf=0x519c80 ret=0x3e3694` | `[diag:cd] sceCdRead payload lbn=0x10 buf=0x519c80 bytes=0143443030310100` (bytes `01 43 44 30 30 31` = PVD `01 CD001`) |
| `0x105` (first directory-content sector after the PVD) | `[diag:cd] sceCdRead lbn=0x105 sectors=1 buf=0x519c80 ret=0x3e3694` | `[diag:cd] sceCdRead payload lbn=0x105 buf=0x519c80 bytes=3000050100000000` |

All 20 payload lines pair 1:1 with the 20 entry lines in read order.

## P5-5. Binaries and commits

| Binary | sha256 | Sources |
|---|---|---|
| `/tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner` (boot 1) | `3a70f0f94eb3108054bdd1962adb28a45a4798878140e4d12f5b20bb4a39ac06` | Sweep runner sources, pre-payload `CD.cpp` |
| `/tmp/p1-link-strict/ps2xRuntime/ps2EntryRunner` (boot 2) | `8da15c0c558d230c34dd0bd8cd47a41569e3bc1fdb9bf1a3420fb9ace99d4f21` | Same runner sources + payload `Diag:` + `STRICT_RETURN_DIAGNOSTICS=ON` |

`ssx3` commits (pushed `fork ssx3`, one file each, no `runner/` or
`._` files; trailers on each):

| Commit | File | Push |
|---|---|---|
| `f0b5040` Diag: log first 8 bytes of sceCdRead destination after serve | `ps2xRuntime/src/lib/Kernel/Stubs/CD.cpp` (+20) | `dbf0080..f0b5040` |
| Map sweep (no commit) | `$W/P1/ssx3-functions.sweep.csv` only (outside the repo; 8246 rows incl. header → 9271 lines incl. header); `TOML ghidra_output` retarget in `$W/P1/ssx3.toml` (outside the repo; backup `$W/P1/ssx3.toml.p1d-orig`); runner outputs refreshed locally, never added | no commit (no tracked file changed) |
| This report | `local/research/P1/REPORT.md` (`[P1d]` prefix, same trailers) | after commit |

`register_functions.cpp` (generated replacement) remains a local
modification, never added.

## P5-6. Exact commands

```
printf 'P1d\n' > /tmp/ssx3-host-lease   (absent before; removed at end)
python3 ELF word reads (file offset 0x1000 + (va - 0x100000)) for 0x3e3bd8-0x3e3be8, 0x42cba0-0x42cbb0
grep/ssx3-functions.csv lookups (0x3e3be0 container row; 0x42cbxx rows)
mkdir -p $W/P1/tools
python3 $W/P1/tools/codeptr_sweep.py $W/P1/cd/SLUS_207.72 $W/P1/ssx3-functions.csv $W/P1/ssx3-functions.sweep.csv --output-dir $W/P1/output | tee $W/P1/sweep-counts.log
cp -X $W/P1/ssx3.toml $W/P1/ssx3.toml.p1d-orig; python3 TOML ghidra_output set to ssx3-functions.sweep.csv
cd $W/P1 && ./bin/ps2_recomp ssx3.toml | tee recomp-p1d-sweep.log
cp -X $W/P1/output/*.cpp $W/PS2Recomp/ps2xRuntime/src/runner/; cp -X $W/P1/output/*.h $W/PS2Recomp/ps2xRuntime/src/runner/; sidecar purges
cmake --build /tmp/p1-link/runtime --target ps2EntryRunner; shasum -a 256 (binary)
cd $W/P1/run && PS2X_CD_IMAGE="$W/SSX 3 (USA).iso" PS2X_DIAG_PERIOD_MS=5000 stdbuf -o0 -e0 /tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner $W/P1/cd/SLUS_207.72 > boot-p1d-1.log 2>&1   (foreground, 185 s, terminated)
CD.cpp payload hunk (edit_file); sidecar purge
git add ps2xRuntime/src/lib/Kernel/Stubs/CD.cpp; git commit -m "Diag: ..." (trailers); git show --stat; git push fork ssx3
cmake -S $W/PS2Recomp -B /tmp/p1-link-strict -G Ninja -DPS2X_BUILD_STUDIO=OFF -DPS2X_BUILD_RUNTIME=ON -DPS2X_BUILD_TEST=ON -DCMAKE_BUILD_TYPE=Release -DPS2X_ENABLE_RUNTIME_LOGS=ON -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF -DPS2X_ENABLE_IOP_RPC_TRACE=ON -DPS2X_STRICT_RETURN_DIAGNOSTICS=ON
cmake --build /tmp/p1-link-strict --target ps2EntryRunner; shasum -a 256 (both binaries)
cd $W/P1/run && PS2X_CD_IMAGE="$W/SSX 3 (USA).iso" PS2X_DIAG_PERIOD_MS=5000 stdbuf -o0 -e0 /tmp/p1-link-strict/ps2xRuntime/ps2EntryRunner $W/P1/cd/SLUS_207.72 > boot-p1d-2.log 2>&1   (foreground, 185 s, terminated)
log reads: grep/sed/tail on closed logs only (never piped through head while running)
git add -f local/research/P1/REPORT.md; git commit -m "[P1d] ..." (trailers); git push fork ssx3
rm /tmp/ssx3-host-lease (verified absent)
find <dir> -name '._*' -delete (after every edit/copy)
```

## P5-7. What I could not do

- `stubs: 176` in map mode: reads 177 (`recomp-p1d-sweep.log`;
  discovered 9269 vs map 9270, one subsumed). The extra stub row vs
  the brief's expectation was not chased; `ret0@0x42c1f0` verified
  intact and the new `sub_003E3BE0` file verified present.
- CSV line endings: the sweep writer's default `\r\n` was normalized
  to the repo-CSV `\n` before recompile.
- No VIF MPG/MSCAL, GIF kick, presented frame, or crash in either P1d
  boot; thread 2 parks on semaphore 26 (`pc=0x423de8`) after one
  scheduling; thread 1 is Dormant with `pc=0`.
- The `0x42cba8` Return-to-0 diagnostic fires during startup before
  any stub/call histogram line exists, so no 5-line stub/call
  preamble precedes it; the dispatch trace field is recorded instead.
- No boot 3: per the brief, the `makeDormant`-caller logging fallback
  runs only when no diagnostic fires.
- `waits.log`: no waits (no foreign lease during P1d).
- Time box: about 50 min of the 5 h box used.

---

# P1e report — Part 6 (brief local/muse/prompts/P1e.md)

Run wall: lease `P1e` acquired with `/tmp/ssx3-host-lease` absent;
`Diag:` commit `b15aff0` + push, strict rebuild, boot 1
(`boot-p1e-1.log`, ~19:12–19:15 EDT, 180 s, terminated by the operator
while healthy, exit -15/SIGTERM), Steps 2–3 (no build), Step 4 gate not
met (implement nothing, no boot 2). Inside the 4-hour box.
`W` = `/Volumes/Extreme SSD/ps2recomp-spike`. No verdicts.

## P6-0. Lease record

| Event | Value |
|---|---|
| Start | `/tmp/ssx3-host-lease` absent; wrote `P1e` |
| Build/boot | Lease kept as `P1e` across diag commit, strict rebuild, boot 1 |
| Foreign leases / waits | None observed; no `waits.log` |
| `adb` | Not used |
| End | Removed after the `[P1e]` push, verified absent |

## P6-1. Diagnostics diff + dormant/return lines (Step 1, one commit, one build, one boot)

Diff (`b15aff0`, 3 files, no `runner/` or `._*` files):

| File | Change |
|---|---|
| `ps2xRuntime/include/ps2_runtime.h` | +1: `std::string formatDispatchHistory() const;` |
| `ps2xRuntime/src/lib/ps2_runtime.cpp` | Internal `formatDispatchHistory()` renamed to `formatDispatchHistoryImpl()` (3 call sites updated); new `PS2Runtime::formatDispatchHistory()` wrapper; new `diagReportAll()` (`PS2X_DIAG_REPORT_ALL=1`, cached static, same pattern as `diagPeriodMs`); `reportMissingFunction` prints when `firstReport \|\| diagReportAll()` (break-once logic still `firstReport`-only; default behaviour unchanged when unset) |
| `ps2xRuntime/src/lib/Kernel/EeScheduler.cpp` | At both `makeDormant` sites in `run()` (pc==0 site, no-function-slot site): when `diagPeriod != 0u`, print `[diag:dormant]` with thread id, entry, pc, ra, sp, gp, v0, a0, `g_diagSchedCounts[id]`, `m_runtime.formatDispatchHistory()` |

De-dup finding: `reportMissingFunction` suppression is a single global
once-flag (`m_missingFunctionReported`, `ps2_runtime.cpp:1236`); no
per-target set exists anywhere in `ps2xRuntime/`. With
`PS2X_DIAG_REPORT_ALL=1` every occurrence prints. The `trace=` field was
already emitted on every printed report of any kind, so every
Return-kind report carries its dispatch history.

Boot 1 (`$W/P1/run/boot-p1e-1.log`, 21,751 lines, 22,539,130 B, strict
binary `a660c92b62c61ca26c7c1049e8fe94def756bb8ddc211d375524fe7aebb0eaec`,
env `PS2X_DIAG_PERIOD_MS=5000 PS2X_DIAG_REPORT_ALL=1`):

| Receipt | Value |
|---|---|
| `[diag:dormant]` total | 10,705 |
| `[diag:dormant] id=-1 entry=0x0` (ephemeral invocation threads) | 10,704 |
| `[diag:dormant] id=1` (thread 1) | 1 (line 200, quoted below) |
| `missing-target` total | 10,725, all `kind=Return op=JR $ra target=0x0` |
| Return-to-0 by source | `0x3e4e8c` ×10,703; `0x3e35a4` ×20; `0x42cba8` ×1 (startup `sub_0042CB78`); `0x3dcc7c` ×1 (thread-1 returner) |
| Returns immediately followed by a dormant line | 10,705 (every dormant is preceded by its Return) |
| Returns NOT followed by dormant | 20: 19× `0x3e4e8c` (each followed by a `0x3e35a4` Return, then one dormant: nested invocation pairs) + 1× `0x42cba8` (startup; execution continued, no dormant) |

Thread-1 Return (line 199, in full):

```
[guest-branch:missing-target] kind=Return op=JR $ra source=0x3dcc7c target=0x0 pc=0x0 ra=0x0 sp=0x1ffff60 gp=0x4a30f0 a0=0x450000 a1=0x51eda8 a2=0x51eda8 a3=0x51eda8 s0=0x1ffff70 s1=0x0 v0=0x1 v1=0x1 a0Readable=yes a0[0]=0x0 a0[4]=0x0 a0[8]=0x0 a0[c]=0x0 s0Readable=yes s0[0]=0x24 s0[4]=0x252fa0 s0[8]=0x2523a8 s0[c]=0x2 recordReadable=yes record[0]=0x27bdfff0 record[4]=0xc0402d record[8]=0xffbf0000 record[c]=0x24060080 vtableReadable=no vtbl[0]=0x0 vtbl[4]=0x0 vtbl[8]=0x0 vtbl[c]=0x0 codeRegion=no policy=1 trace=0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x419878 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3a7c -> 0x3e438c -> 0x2523a8 -> 0x317e98 -> 0x3e5700 -> 0x423c90 -> 0x423de0 -> 0x423c90 -> 0x319b48 -> 0x31a088 -> 0x3200c0 -> 0x31ed60 -> 0x31eee8 -> 0x31e6d8 -> 0x40fcb0 -> 0x4114d0 -> 0x31ffd8 -> 0x31ffd8 -> 0x31ffd8 -> 0x3e5760 -> 0x423c90 -> 0x423dc0 -> 0x423da0 -> 0x423ba0 -> 0x423bc0 -> 0x3e3be0 -> 0x423de0 -> 0x423bc8 -> 0x3e4418 -> 0x400a78 -> 0x4008a0 -> 0x3e57f8 -> 0x3dcd4c -> 0x3e3020 -> 0x3e57f8 -> 0x3dcc64
```

Thread-1 dormant (line 200, in full):

```
[diag:dormant] id=1 entry=0x100008 pc=0x0 ra=0x0 sp=0x1ffff60 gp=0x4a30f0 v0=0x1 a0=0x450000 scheduled=22 trace=0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x419878 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3a7c -> 0x3e438c -> 0x2523a8 -> 0x317e98 -> 0x3e5700 -> 0x423c90 -> 0x423de0 -> 0x423c90 -> 0x319b48 -> 0x31a088 -> 0x3200c0 -> 0x31ed60 -> 0x31eee8 -> 0x31e6d8 -> 0x40fcb0 -> 0x4114d0 -> 0x31ffd8 -> 0x31ffd8 -> 0x31ffd8 -> 0x3e5760 -> 0x423c90 -> 0x423dc0 -> 0x423da0 -> 0x423ba0 -> 0x423bc0 -> 0x3e3be0 -> 0x423de0 -> 0x423bc8 -> 0x3e4418 -> 0x400a78 -> 0x4008a0 -> 0x3e57f8 -> 0x3dcd4c -> 0x3e3020 -> 0x3e57f8 -> 0x3dcc64
```

## P6-2. Returner table + quoted body (Step 2, no build)

| Item | Value |
|---|---|
| Final `jr $ra` with ra 0 | `0x3dcc7c` (`jr $ra`, delay slot `addiu $sp,$sp,0x60`) |
| Enclosing function | `sub_003DCBD8`, sweep CSV line 8036: `sub_003DCBD8,0x3dcbd8,0x3dcc88,0xb0` |
| Entry path | Mid-function entry at `0x3dcc64` (trace last hop; generated entry-switch `case 0x3dcc64u: goto label_3dcc64`, skipping the `0x3dcbd8` prologue and the `sd $ra,0($sp)` delay slot at `0x3dcc08`) |
| Only `ra=0x3dcc64` setter in generated sources | `sub_003DCBD8:296` (`SET_GPR_U32(ctx, 31, 0x3DCC64u)`, the JAL at `0x3dcc5c` calling `0x3dcc88`); no constant call/jump edge targets `0x3dcc64` anywhere in `output/` |
| Condition (registers on the line) | `ld $ra,0($sp)` loaded `0x0` (slot never written on this entry path); `sp=0x1ffff60 gp=0x4a30f0 v0=0x1 a0=0x450000`; `jr $ra` unconditional |
| Role | Prologue (`sp-0x60`, save s-regs, `s4=a0 s2=a1 s3=a2`, flag `lw [0x520000-0x6550]`), branch on flag (`beqz` to the `0x3dcc14` pointer-building path vs JAL `0x3dcc88`/epilogue path), epilogue (`lq s0–s4`, `ld ra`, `jr ra`, `sp+=0x60`). No `sceSif*`/`sceCd*`/`scePad*`/`sceMc*`/`sceGs*`/`_start` pattern recognisable in the returner; `0x423xxx` hops are EE-syscall thunks (`0x423ba0` CreateThread site `0x423ba8`, `0x423bc0` StartThread site `0x423bc8`, `0x423da0` CreateSema site `0x423da8`, `0x423dc0` SignalSema site `0x423dc8`, `0x423de0` WaitSema site `0x423de8`); `0x3e3588`/`0x3e3968` are the alarm/comparator callbacks; `0x400a78`/`0x4008a0` are the TOML `sceCdInitEeCB`/`sceCdCallback` stubs |
| Game `main` clause | Not applicable (returner is `sub_003DCBD8`, not `main`) |

Caller chain: 64 hops, 32 distinct (ring mixes executor-thread activity
from thread 1, thread 2, and callback invocations):

| Hops | Address | CSV row |
|---|---|---|
| ×17 | `0x3e3968` START | `sub_003E3968,0x3e3968,0x3e39a8` |
| ×1 | `0x419878` mid+0x980 | `sub_00418EF8,0x418ef8,0x4198d8` |
| ×10 | `0x3e3968` START | `sub_003E3968,0x3e3968,0x3e39a8` |
| ×1 | `0x3e3a7c` mid+0xd4 | `sub_003E39A8,0x3e39a8,0x3e3b00` |
| ×1 | `0x3e438c` mid+0x34c | `sub_003E4040,0x3e4040,0x3e44b0` |
| ×1 | `0x2523a8` START | `sub_002523A8,0x2523a8,0x252658` |
| ×1 | `0x317e98` START | `sub_00317E98,0x317e98,0x317f38` |
| ×1 | `0x3e5700` START | `sub_003E5700,0x3e5700,0x3e5760` |
| ×1 | `0x423c90` START | `sub_00423C90,0x423c90,0x423ca0` |
| ×1 | `0x423de0` START | `sub_00423DE0,0x423de0,0x423df0` (WaitSema thunk) |
| ×1 | `0x423c90` START | `sub_00423C90,0x423c90,0x423ca0` |
| ×1 | `0x319b48` START | `sub_00319B48,0x319b48,0x319b98` |
| ×1 | `0x31a088` START | `sub_0031A088,0x31a088,0x31a130` |
| ×1 | `0x3200c0` START | `sub_003200C0,0x3200c0,0x3200e8` |
| ×1 | `0x31ed60` START | `sub_0031ED60,0x31ed60,0x31eee8` |
| ×1 | `0x31eee8` START | `sub_0031EEE8,0x31eee8,0x31f2c8` |
| ×1 | `0x31e6d8` START | `sub_0031E6D8,0x31e6d8,0x31e818` |
| ×1 | `0x40fcb0` START | `sub_0040FCB0,0x40fcb0,0x4103a0` |
| ×1 | `0x4114d0` START | `sub_004114D0,0x4114d0,0x411530` |
| ×3 | `0x31ffd8` START | `sub_0031FFD8,0x31ffd8,0x320034` |
| ×1 | `0x3e5760` START | `sub_003E5760,0x3e5760,0x3e57f8` |
| ×1 | `0x423c90` START | `sub_00423C90,0x423c90,0x423ca0` |
| ×1 | `0x423dc0` START | `sub_00423DC0,0x423dc0,0x423dd0` (SignalSema thunk) |
| ×1 | `0x423da0` START | `sub_00423DA0,0x423da0,0x423db0` (CreateSema thunk) |
| ×1 | `0x423ba0` START | `sub_00423BA0` range (CreateThread site `0x423ba8`) |
| ×1 | `0x423bc0` START | `sub_00423BC0,0x423bc0,0x423be0` (StartThread site `0x423bc8`) |
| ×1 | `0x3e3be0` START | `sub_003E3BE0,0x3e3be0,0x3e3d78` (thread-2 entry) |
| ×1 | `0x423de0` START | `sub_00423DE0,0x423de0,0x423df0` (thread-2 WaitSema call) |
| ×1 | `0x423bc8` mid+0x8 | `sub_00423BC0,0x423bc0,0x423be0` (thread-1 resumption) |
| ×1 | `0x3e4418` mid+0x3d8 | `sub_003E4040,0x3e4040,0x3e44b0` |
| ×1 | `0x400a78` START | `sceCdInitEeCB` stub (`[diag:cd]` line 198 fires just before line 199) |
| ×1 | `0x4008a0` START | `sceCdCallback` stub |
| ×1 | `0x3e57f8` START | `sub_003E57F8,0x3e57f8,0x3e58c8` (exits via its own `jr $ra` at `0x3e58bc`; the silent valid-slot return that dispatched `0x3dcc64`) |
| ×1 | `0x3dcd4c` mid+0xc4 | `sub_003DCC88,0x3dcc88,0x3dcd98` (fallthrough of the JAL at `0x3dcd44` calling `0x3e4040`) |
| ×1 | `0x3e3020` START | `sub_003E3020,0x3e3020,0x3e3098` |
| ×1 | `0x3e57f8` START | `sub_003E57F8,0x3e57f8,0x3e58c8` (second dispatch) |
| ×1 | `0x3dcc64` mid+0x8c | `sub_003DCBD8,0x3dcbd8,0x3dcc88` (epilogue entry; dense-table slot `register_functions.cpp:377984` maps `0x3dcc64` to `sub_003DCBD8_0x3dcbd8`) |

Quoted body (`$W/P1/output/sub_003DCBD8_0x3dcbd8.cpp`, lines 324–363, 40 lines):

```cpp
label_3dcc74:
    // 0x3dcc74: 0x7bb40010  lq          $s4, 0x10($sp)
    ctx->pc = 0x3dcc74u;
    SET_GPR_VEC(ctx, 20, READ128(ADD32(GPR_U32(ctx, 29), 16)));
label_3dcc78:
    // 0x3dcc78: 0xdfbf0000  ld          $ra, 0x0($sp)
    ctx->pc = 0x3dcc78u;
    SET_GPR_U64(ctx, 31, READ64(ADD32(GPR_U32(ctx, 29), 0)));
label_3dcc7c:
    // 0x3dcc7c: 0x3e00008  jr          $ra
label_3dcc80:
    if (ctx->pc == 0x3DCC80u) {
        ctx->pc = 0x3DCC80u;
        ctx->in_delay_slot = true;
        ctx->branch_pc = 0x3DCC7Cu;
        // 0x3dcc80: 0x27bd0060  addiu       $sp, $sp, 0x60 (Delay Slot)
        SET_GPR_S32(ctx, 29, (int32_t)ADD32(GPR_U32(ctx, 29), 96));
        ctx->in_delay_slot = false;
        ctx->pc = 0x3DCC84u;
        goto label_3dcc84;
    }
    ctx->pc = 0x3DCC7Cu;
    {
        const uint32_t jumpTarget = GPR_U32(ctx, 31);
        ctx->pc = 0x3DCC80u;
        ctx->in_delay_slot = true;
        ctx->branch_pc = 0x3DCC7Cu;
        // 0x3dcc80: 0x27bd0060  addiu       $sp, $sp, 0x60 (Delay Slot)
        SET_GPR_S32(ctx, 29, (int32_t)ADD32(GPR_U32(ctx, 29), 96));
        ctx->in_delay_slot = false;
        ctx->pc = jumpTarget;
        #if defined(PS2X_STRICT_RETURN_DIAGNOSTICS) && PS2X_STRICT_RETURN_DIAGNOSTICS
        (void)runtime->dispatchGuestBranch(rdram, ctx, jumpTarget, 0x3DCC7Cu, 0u, PS2Runtime::GuestBranchKind::Return, "JR $ra");
        return;
        #else
        ctx->pc = jumpTarget;
        return;
        #endif
    }
    ctx->pc = 0x3DCC84u;
```

## P6-3. Semaphore 26 table (Step 3, no build)

Syscall ids (`Dispatcher.cpp`): `0x40` CreateSema, `0x41` DeleteSema,
`0x42` SignalSema, `-0x43` (`0xffffffbd`) iSignalSema, `0x44` WaitSema,
`0xFC` SetAlarm. Boot-1 block-0 counts: CreateSema 26 (thunk site
`0x423da8`), DeleteSema 20 (site `0x423db8`), SignalSema 12 (site
`0x423dc8`), iSignalSema 20 (site `0x423dd8`), WaitSema 33 (site
`0x423de8`), SetAlarm 20 (site `0x423b28`); blocks 1+ empty. Ids allocate
from 1 via `allocatePositiveId` starting at `m_nextSemaphoreId` (never
reuses freed low ids), so 26 creates yield ids 1–26 in call order and id
26 is the 26th (last) create.

| Item | Value |
|---|---|
| CreateSema→id 26 | 26th of 26 calls, all via `0x423da8` (`sub_00423DA0`, `$v1=0x40`); stub row `target=0x423da0 count=26 firstRa=0x42c0fc lastRa=0x3e43c4` |
| First create (id 1) | `0x42c0f4` (`sub_0042C0D8`): JAL `func_423DA0`, ra `0x42c0fc`, `a0=$sp` (stack struct `+4=1 +8=1 +0x24=1 +0x28=1`) |
| Last create (id 26) | `0x3e43bc` (`sub_003E4040`): JAL `func_423DA0`, ra `0x3e43c4`, `a0=$sp+0x30` (stack struct `[+0x34]=0x20 [+0x38]=0`) |
| Ephemeral creates (20 of the 26) | `0x3e35d4` (`sub_003E35B0`): JAL `func_423DA0`, ra `0x3e35dc`, `a0=$sp` (stack struct `+4=1 +8=0 +0x14=0`); id→`$s0`; paired 1:1 with 20 DeleteSema at `0x3e35fc` (ra `0x3e3604`, `a0=$s0`) |
| SignalSema sites (12 calls) | `0x418d34` (`sub_00418D08`): JAL `func_423DC0`, ra `0x418d3c`, `a0=[0x455248]` (global); `0x3e57b4` (`sub_003E5760`): JAL `func_423DC0`, ra `0x3e57bc`, delay slot `a0=[$s0+0xC]`; 21 static JAL sites exist, per-site split of the 12 is below the stub top-30 cutoff (no row) |
| iSignalSema sites (20 calls) | Single site `0x3e3590` (`sub_003E3588` alarm handler): JAL `func_423DD0` (`$v1=-0x43`), ra `0x3e3598`, delay slot `a0=a2` (alarm argument = the ephemeral sema id armed by `sub_003E35B0` at `0x3e35e4` via SetAlarm `a1=0x3e3588 a2=$s0`); 20 handler exits (`0x3e35a4` Returns) = 20 calls, straight-line code |
| WaitSema sites (33 = 20 ephemeral + 12 + 1 park) | `0x3e35f4` ×20 (`sub_003E35B0`, `a0=$s0`); `0x418ce0` (`sub_00418CA8`, stub firstRa); `0x3e3c20` (`sub_003E3BE0`, stub lastRa): JAL `func_423DE0` at `0x3e3c18`, ra `0x3e3c20`, delay slot `a0=[$s2+0xC]`, `$s2=$s0-0x20` — thread 2's park (`waitId=26`) |

| Site | Thread |
|---|---|
| `0x42c0fc`, `0x3e43c4` creates; `0x418d34`, `0x3e57b4` signals; `0x418ce0` waits; `0x3e35d4/0x3e35f4/0x3e35fc` ephemeral loop | Thread 1 (main, entry `0x100008`; thread 2 runs only `0x3e3be0–0x3e3c20` in its single scheduling; alarm/comparator subtrees contain only the `0x423dd0` call) |
| `0x3e3c20` wait (id 26) | Thread 2 (entry `0x3e3be0`, one scheduling, parked `WaitSema` on 26) |
| `0x3e3590` iSignalSema ×20 | Alarm invocation thread (`id=-1`; `0x3e3588→0x423dd0` present on id=-1 dormant traces, absent from thread-1 window; handler `ra=0` from invocation setup) |

## P6-4. Artefact record, no fix (Step 4)

Step 2 names game code (`sub_003DCBD8` epilogue), not an HLE stub or
syscall value: the returning branch (`jr $ra` at `0x3dcc7c`) is
unconditional and tests nothing; `ra=0` is stale stack residue (the
`0x3dcc08` `sd $ra` never ran on the `0x3dcc64` mid-function entry path).
No `Kernel/Stubs/` or `Syscalls/` value selected the return, so nothing
was implemented and there is no boot 2 and no ladder.

Record (recompilation-shape note): the return pair is `0x3dcc78
ld $ra,0($sp)` + `0x3dcc7c jr $ra` (delay slot `0x3dcc80
addiu $sp,$sp,0x60`); generated code for both sides is the P6-2 quote
(lines 324–363: `label_3dcc78` load, `label_3dcc7c` jump, strict
`dispatchGuestBranch(..., Return, "JR $ra")` + `return`). The function was
entered at `0x3dcc64` through the dense-table fallback slot
(`register_functions.cpp:377984`) and entry-switch `goto label_3dcc64`,
which skips the prologue ra-save; the preceding edge (`0x3e57f8`→`0x3dcc64`)
is the silent valid-slot return from `sub_003E57F8`'s own `jr $ra` at
`0x3e58bc` (no constant call/jump edge targets `0x3dcc64` in `output/`; the
only `ra=0x3dcc64` setter is the `0x3dcc5c` JAL).

## P6-5. Binaries and commits

| Binary | sha256 | Sources |
|---|---|---|
| `/tmp/p1-link-strict/ps2xRuntime/ps2EntryRunner` (boot 1) | `a660c92b62c61ca26c7c1049e8fe94def756bb8ddc211d375524fe7aebb0eaec` | Sweep runner sources + `b15aff0` diag + `STRICT_RETURN_DIAGNOSTICS=ON` |
| `/tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner` (normal, untouched) | `3a70f0f94eb3108054bdd1962adb28a45a4798878140e4d12f5b20bb4a39ac06` | Unchanged since P1d |

`ssx3` commits (pushed `fork ssx3`, no `runner/` or `._` files; trailers on each):

| Commit | File(s) | Push |
|---|---|---|
| `b15aff0` Diag: dormant lines at both makeDormant sites plus PS2X_DIAG_REPORT_ALL | `ps2xRuntime/include/ps2_runtime.h` (+1), `ps2xRuntime/src/lib/ps2_runtime.cpp`, `ps2xRuntime/src/lib/Kernel/EeScheduler.cpp` | `f0b5040..b15aff0` |
| This report | `local/research/P1/REPORT.md` (`[P1e]` prefix, same trailers) | after commit |

`register_functions.cpp` (generated replacement) remains a local
modification, never added.

## P6-6. Exact commands

```
printf 'P1e\n' > /tmp/ssx3-host-lease   (absent before; removed at end)
git log/show (trailer format), ELF/CSV/grep reads for P5 facts
(edit_file) ps2_runtime.h: +formatDispatchHistory decl
(edit_file) ps2_runtime.cpp: impl rename + wrapper + diagReportAll + shouldPrint
(edit_file) EeScheduler.cpp: [diag:dormant] at both makeDormant sites
find ps2xRuntime /tmp/p1-link-strict -name '._*' -delete (after every edit)
git add ps2xRuntime/include/ps2_runtime.h ps2xRuntime/src/lib/ps2_runtime.cpp ps2xRuntime/src/lib/Kernel/EeScheduler.cpp; git commit -m "Diag: ..." (trailers); git push fork ssx3
cmake --build /tmp/p1-link-strict --target ps2EntryRunner; shasum -a 256 (binary)
python3 /tmp/p1e-boot1.py (foreground 180 s, CWD $W/P1/run, PS2X_CD_IMAGE + PS2X_DIAG_PERIOD_MS=5000 + PS2X_DIAG_REPORT_ALL=1, stdbuf -o0 -e0, log direct to boot-p1e-1.log, SIGTERM)
log reads: grep/sed/python3 on the closed log only (never piped while running)
CSV resolutions (python3 csv+bisect over ssx3-functions.sweep.csv); generated-source greps/seds in $W/P1/output
git add -f local/research/P1/REPORT.md; git commit -m "[P1e] ..." (trailers); git push origin main
rm /tmp/ssx3-host-lease (verified absent)
```

## P6-7. What I could not do

- Per-site split of the 12 SignalSema calls: below the stub top-30
  cutoff (no `target=0x423dc0` row); two firing sites verified in source
  (`0x418d34`, `0x3e57b4`), 21 static JAL sites total.
- Full `ra=0x3dcc64` provenance across the tail-jump chain
  (`0x3dcd4c`→`0x3e3020`→`0x3e57f8`→`0x3dcc64`): only the setter (JAL at
  `0x3dcc5c`) and the absence of constant edges are established; the
  register-indirect hop in between is not traced per-instruction.
- No Step-4 boot 2 or ladder: the gate named game code, so per the brief
  nothing was implemented and Step 5 follows directly.
- The 10,704 `id=-1` dormant lines are invocation-thread ephemera (one
  per callback completion); only the single `id=1` line answers Step 1.
- `waits.log`: no waits (no foreign lease during P1e).
- Time box: about 35 min of the 4 h box used.

---

# P1f report — Part 7 (brief local/muse/prompts/P1f.md)

## P7-0. Lease record

| Event | Value |
|---|---|
| Start | `/tmp/ssx3-host-lease` absent; wrote `P1f` |
| Builds/boots | Lease kept as `P1f` across diag commits, normal rebuild, boot 1 (superseded slot), boot 1b (corrected slot), Kernel fix, rebuild, boot 2 |
| Foreign leases / waits | None observed; no `waits.log` |
| `adb` | Not used |
| End | Removed after the `[P1f]` push, verified absent |

## P7-1. Diag diff + watch/stacks/StartThread lines (Step 1, two commits, two builds, three boots)

Commits (`ssx3`, pushed `fork ssx3`, no `runner/` or `._*` files; trailers on each):

| Commit | File(s) |
|---|---|
| `8d203d1` Diag: P1f watchpoint on guest RAM plus stack map and StartThread line | `ps2xRuntime/include/ps2_runtime.h` (+22: `ps2DiagWatch*` decls), `ps2xRuntime/include/ps2_runtime_macros.h` (WRITE8/16/32/64/128 call `ps2DiagWatchReport` behind `ps2DiagWatchEnabled()`), `ps2xRuntime/src/lib/ps2_runtime.cpp` (+151: `PS2X_DIAG_WATCH` parse, `diagWatchEmit`, `ps2DiagWatch*` impl, Store8/16/32/64/128 hooks), `ps2xRuntime/src/lib/Kernel/EeScheduler.cpp` (+113: `[diag:stacks]` block, `[diag:start-thread]` line, watch-thread setter before guest dispatch, `writeGuestU32`/`setVSyncFlag` direct watch), `ps2xRuntime/src/lib/Kernel/Stubs/CD.cpp` (+5: `getCdCallbackStackTop()`), `ps2xRuntime/src/lib/Kernel/Stubs/CD.h` (+1: decl) |
| `a44b101` Diag: forward-declare PS2Runtime for watch helpers | `ps2xRuntime/include/ps2_runtime.h` (+1: build fix, decls precede class) |

Watch format: `[diag:watch] addr=0x<writeAddr hex> width=<bytes dec> value=0x<hex; 128-bit as 32 zero-padded hex hi+lo> pc=0x<ctx pc hex> thread=<m_currentThreadId dec> ra=0x<hex> sp=0x<hex>`. `PS2X_DIAG_WATCH` is a comma list parsed with base 0; each entry names `[addr, addr+8)`. Thread id is the scheduler's current thread at dispatch (`-1` for invocation threads); invocations running on their owner share the owner id. Covered writers: generated-code WRITE8/16/32/64/128 (fast + special paths), `Store8/16/32/64/128`, `EeScheduler::writeGuestU32`, vsync tick `memcpy`. HLE `getMemPtr`/`memcpy`/`memset` stubs are not covered (see P7-6).

Boot 1 (`$W/P1/run/boot-p1f-1.log`, 11,366 lines, normal binary `3c9dbe8cba53dc7be6bf69d8df6be19485d3eabb3df9dfa9aa4d044b037058c4`, env `PS2X_DIAG_WATCH=0x1ffff60`) is superseded: the dormant line prints the context after the epilogue delay slot (`addiu $sp,$sp,0x60`) ran, so `sp=0x1ffff60` is the caller frame and the 36 writes caught there are thread-1 init saves, not the answer. Boot 1b re-runs the same binary watching the true frame slots.

Boot 1b (`$W/P1/run/boot-p1f-1b.log`, 44,094 lines, 13,264,174 B, same `3c9dbe8c` binary, env `PS2X_CD_IMAGE` + `PS2X_DIAG_PERIOD_MS=5000` + `PS2X_DIAG_WATCH=0x1ffff00,0x1ffff08,0x1ffff10`, foreground 180 s, SIGTERM):

| Receipt | Value |
|---|---|
| `[diag:watch]` total | 32,682 parsed (thread=1: 153, thread=-1: 32,529; 99 distinct pc/width/value/thread/sp groups) |
| `[diag:start-thread]` total | 1 (line 410, quoted below) |
| `[diag:dormant] id=1` total | 1 (line 412, quoted below) |
| `[diag:dormant] id=-1` total | 10,844 |
| `[diag:stacks]` total | 245 |

WRITE64 coverage: the `WRITE64` macro (`ps2xRuntime/include/ps2_runtime_macros.h`) calls `ps2DiagWatchReport(rdram, _addr, 8u, ...)` behind `ps2DiagWatchEnabled()`, and `PS2Runtime::Store64` (`ps2_runtime.cpp`) does the same; the prologue `sd $ra` store is observed as line 208 below (`width=8 ... pc=0x3dcc08`).

Log lines 205–213 (prologue save, then the first overwrites; `cut -c1-220`):

```
[diag:watch] addr=0x1ffff00 width=8 value=0x450000 pc=0x4248ec thread=1 ra=0x3e4c64 sp=0x1fffef0
[diag:watch] addr=0x1ffff10 width=8 value=0x3e4c64 pc=0x4248f0 thread=1 ra=0x3e4c64 sp=0x1fffef0
[diag:watch] addr=0x1ffff10 width=16 value=0x00000000000000000000000000000000 pc=0x3dcbec thread=1 ra=0x31af34 sp=0x1ffff00
[diag:watch] addr=0x1ffff00 width=8 value=0x31af34 pc=0x3dcc08 thread=1 ra=0x31af34 sp=0x1ffff00
[diag:cd] sceCdRead lbn=0x10 sectors=1 buf=0x519c80 ret=0x3e3694
[diag:cd] sceCdRead payload lbn=0x10 buf=0x519c80 bytes=0143443030310100
[diag:watch] addr=0x1ffff10 width=16 value=0x00000000000000000000000000000000 pc=0x3e4dc0 thread=-1 ra=0x0 sp=0x1fffed0
[diag:watch] addr=0x1ffff00 width=16 value=0x00000000000000000000000000000000 pc=0x3e4dc8 thread=-1 ra=0x0 sp=0x1fffed0
[diag:watch] addr=0x1ffff00 width=16 value=0x00000000000000000000000000000000 pc=0x3e4dc8 thread=-1 ra=0x0 sp=0x1fffed0
```

No `thread=1` write appears after line 208 (count 0 past line 211); the overwrites run lines 211–44093 while thread 1 is parked.

Overwrite counts by pc (all `width=16 value=0x0...0 ra=0x0 sp=0x1fffed0 thread=-1`):

| pc | CSV row | ELF word / instruction | addr | Count |
|---|---|---|---|---|
| `0x3e4dc0` | `sub_003E4AF0,[0x3e4af0,0x3e4e98)` | `0x7fb00040` / `sq $s0,0x40($sp)` (`0x1fffed0+0x40=0x1ffff10`) | `0x1ffff10` | 10,843 |
| `0x3e4dc8` | `sub_003E4AF0,[0x3e4af0,0x3e4e98)` | `0x7fb10030` / `sq $s1,0x30($sp)` (`0x1fffed0+0x30=0x1ffff00`) | `0x1ffff00` | 21,686 |

Handler entry `0x3e4db8 = 0x27bdffb0` (`addiu $sp,$sp,-0x50`): stored `sp=0x1ffff20` minus `0x50` is the observed `sp=0x1fffed0`. Entry `0x3e4db8` is `0xc8` past the sweep row start, i.e. the registered INTC handler for cause 10. Generated prologue (`$W/P1/output/sub_003E4AF0_0x3e4af0.cpp` lines 1488–1509):

```cpp
label_3e4db8:
    // 0x3e4db8: 0x27bdffb0  addiu       $sp, $sp, -0x50
    ...
label_3e4dc0:
    // 0x3e4dc0: 0x7fb00040  sq          $s0, 0x40($sp)
    ...
    WRITE128(ADD32(GPR_U32(ctx, 29), 64), GPR_VEC(ctx, 16));
    ...
label_3e4dc8:
    // 0x3e4dc8: 0x7fb10030  sq          $s1, 0x30($sp)
    ...
    WRITE128(ADD32(GPR_U32(ctx, 29), 48), GPR_VEC(ctx, 17));
```

StartThread line (line 410):

```
[diag:start-thread] id=2 func=0x3e3be0 stack=0x51ac80 stack_size=0x4000 gp=0x4a30f0 priority=12 attr=0x0 initial_sp=0x51ec80
```

Thread-1 dormant (line 412, `sp=0x1ffff60` post-delay-slot, same P6-1 trace ending `0x3e57f8 -> 0x3dcc64`):

```
[diag:dormant] id=1 entry=0x100008 pc=0x0 ra=0x0 sp=0x1ffff60 gp=0x4a30f0 v0=0x1 a0=0x450000 scheduled=22 trace=0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x419878 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3968 -> 0x3e3a7c -> 0x3e438c -> 0x2523a8 -> 0x317e98 -> 0x3e5700 -> 0x423c90 -> 0x423de0 -> 0x423c90 -> 0x319b48 -> 0x31a088 -> 0x3200c0 -> 0x31ed60 -> 0x31eee8 -> 0x31e6d8 -> 0x40fcb0 -> 0x4114d0 -> 0x31ffd8 -> 0x31ffd8 -> 0x31ffd8 -> 0x3e5760 -> 0x423c90 -> 0x423dc0 -> 0x423da0 -> 0x423ba0 -> 0x423bc0 -> 0x3e3be0 -> 0x423de0 -> 0x423bc8 -> 0x3e4418 -> 0x400a78 -> 0x4008a0 -> 0x3e57f8 -> 0x3dcd4c -> 0x3e3020 -> 0x3e57f8 -> 0x3dcc64
```

`[diag:stacks]` block nearest the thread-1 Dormant line (block 0, lines 1444–1450):

```
[diag:stacks] block=0 thread id=2 stack=0x51ac80 stackSize=0x4000 sp=0x51ec20 entry=0x3e3be0 pc=0x423de8
[diag:stacks] block=0 thread id=-1 stack=0x0 stackSize=0x0 sp=0x0 entry=0x0 pc=0x0
[diag:stacks] block=0 thread id=1 stack=0x1fe0000 stackSize=0x20000 sp=0x1ffff60 entry=0x100008 pc=0x0
[diag:stacks] block=0 invocation key=0x100000000 thread=1 depth=0 top=0x1fffff0
[diag:stacks] block=0 cdCallbackStackTop=0x51ac80
[diag:stacks] block=0 intc id=1 cause=10 handler=0x3e4db8 sp=0x1ffff20
[diag:stacks] block=0 pending kind=0 pc=0x3e4db8 sp=0x1ffff20
```

Reserves-from record: `reserveAsyncCallbackStack(0x4000)` allocates down from `PS2_RAM_SIZE` (`0x2000000`) while `m_asyncCallbackStackTop` stays above `m_asyncCallbackStackFloor`; the first top returned is `0x2000000 - 0x10 = 0x1fffff0` (block-0 `top=0x1fffff0`). Thread-2 initial sp `0x51ec80 = 0x51ac80 + 0x4000` masked to 16 (`EeScheduler::startThread`). Thread-1 stack descriptor (`stack=0x1fe0000 stackSize=0x20000`, range `[0x1fe0000, 0x2000000)`) is the live main-thread descriptor read from the scheduler at the dump. `sceCdInitEeCB` line in this boot: `[diag:cd] sceCdInitEeCB stack=0x51a480 size=0x800 ret=0x3e442c`, so `g_cdCallbackStackTop = 0x51a480 + 0x800 = 0x51ac80`. INTC `handler.sp` comes from the `AddIntcHandler` sp argument; the alarm sp comes from `SetAlarm`'s caller sp (`getRegU32(ctx, 29)`); no alarm rows are present in any `[diag:stacks]` output.

## P7-2. Writer table (Step 2, no build; from boot 1b)

Writes to the true ra slot `0x1ffff00` (`0($sp)` with prologue `sp=0x1ffff00`) and its neighbours, in log order. The slot's own writer rows first; the remaining 151 thread-1 writes (97 groups, all log lines <208: init-sequence `sq` pairs and post-init frame saves at `0x317d94`/`0x317da0`/`0x319738`/`0x31ff84`/`0x3e56a4`/`0x3e56c0`/`0x3e64bc`/`0x3e64c0`/`0x418cb0`/`0x418cb4`/`0x41dc10`/`0x41dc14`/`0x41e348`/`0x41e350`/`0x4248ec`/`0x4248f0` plus the constructor pairs) precede the prologue save and never recur after line 208.

| # | Value | Width | pc → CSV row → ELF word / instruction | Thread / invocation, sp/ra | Order |
|---|---|---|---|---|---|
| 1 | `0x31af34` | 8 | `0x3dcc08` → `sub_003DCBD8,[0x3dcbd8,0x3dcc88)` → `0xffbf0000` `sd $ra,0($sp)` (delay slot of `beqz` at `0x3dcc04`) | Thread 1, `sp=0x1ffff00` `ra=0x31af34` | Log line 208; the prologue save (WRITE64 hook observed) |
| 2 | `0x0` | 16 | `0x3dcbec` → `sub_003DCBD8,[0x3dcbd8,0x3dcc88)` → `0x7fb40010` `sq $s4,0x10($sp)` (`0x1ffff00+0x10=0x1ffff10`) | Thread 1, `sp=0x1ffff00` `ra=0x31af34` | Log line 207, same prologue |
| 3 | `0x0` | 16 | `0x3e4dc0` → `sub_003E4AF0,[0x3e4af0,0x3e4e98)` → `0x7fb00040` `sq $s0,0x40($sp)` (`0x1fffed0+0x40=0x1ffff10`) | Invocation (`thread=-1`, `ra=0x0`), `sp=0x1fffed0` | ×10,843, lines 211–44091 |
| 4 | `0x0` | 16 | `0x3e4dc8` → `sub_003E4AF0,[0x3e4af0,0x3e4e98)` → `0x7fb10030` `sq $s1,0x30($sp)` (`0x1fffed0+0x30=0x1ffff00`) | Invocation (`thread=-1`, `ra=0x0`), `sp=0x1fffed0` | ×21,686, lines 212–44093 |

Rows 3–4 are the INTC cause-10 handler prologue (`0x3e4db8 = 0x27bdffb0 addiu $sp,$sp,-0x50`; stored `sp=0x1ffff20` minus `0x50` is the observed `sp=0x1fffed0`). The fresh invocation context zeroes the s-regs, so the `sq` stores write 0 over thread 1's parked frame, including the ra slot `0x1ffff00` (row 4). Row 4 is the write that left the 0 the epilogue (`0x3dcc78 ld $ra,0($sp)` + `0x3dcc7c jr $ra`) read: the prologue saved `0x31af34` at line 208, the first overwrite lands at line 212, no `thread=1` write recurs after line 208, and the thread-1 Dormant line follows at 412. An invocation prologue, as listed in the brief's writer kinds.

## P7-3. Fix + ladder (Step 3, one commit `Kernel:`, rebuild, boot 2)

Fix (`6046260`, `Kernel:` prefix, 3 files): `EeScheduler::dispatchIrq` and the `Alarm` event queued handler invocations with the registration-time thread sp (`handler.sp` / `alarm.sp`, `EeScheduler.cpp`). That stack belongs to a live guest thread: the `0x3e4db8` prologue stored zeros over thread 1's ra slot (P7-2 rows 3–4). Both sites now queue with `sp=0`, so the `run()` dequeue path (`sp==0` → `invocationStackTop()`) assigns a reserved top. `reserveAsyncCallbackStack` (`ps2_runtime.cpp`, header member inits, and the `loadELF` reset) no longer hands out the RAM top: it allocates down from `0x00100000` with floor `0x00080000`.

Region and why it is free: `[0x80000, 0x100000)` sits inside the EE kernel-reserved `0x00000000–0x000fffff` area. ELF program headers (single `PT_LOAD`, `vaddr=0x00100000 filesz=0x3a4bf4 memsz=0x43eadc`) load no image below `0x100000`. Guest heap base defaults to `0x00100000` (`kGuestHeapDefaultBase`) and `SetupHeap`/`EndOfHeap` cap the limit at `0x01F00000`, so heap blocks grow up from at or above `0x100000` while these stacks grow down from it. Guest thread stacks (`[0x51ac80,0x51ec80)`, `[0x1fe0000,0x2000000)`, plus boot-2 `[0x6048c0,0x6088c0)` / `[0x6088d0,0x6188d0)`), the CD stack (`[0x51a480,0x51ac80)`), and the old invocation tops (`0x1fffff0`) all sit at or above `0x100000`. Capacity `[0x80000,0x100000)` is 512 KB for `0x4000` stacks; exhaustion keeps the existing throw.

Boot 2 (`$W/P1/run/boot-p1f-2.log`, 1,464 lines, 151,824 B, fixed binary `f4d16b988d319cd8751350d0cf2554895ef1b7b2f732526d33b01615ec372fba`, same watch env, foreground 180 s, SIGTERM):

| Rung | Boot 2 |
|---|---|
| `[diag:watch]` total | 165 (`thread=-1`: 0; `pc=0x3e4dc8`: 0; prologue save `pc=0x3dcc08 value=0x31af34` still present) |
| `[diag:dormant] id=1` | 0 (thread 1 runs past the old point) |
| Thread table at last dump (block 34, 4 threads) | `id=1 status=0 waitReason=0 waitId=0 pc=0x391330 entry=0x100008 priority=100 scheduled=306`; `id=2 status=2 waitReason=2 waitId=26 pc=0x423de8 entry=0x3e3be0 priority=12 scheduled=0`; `id=3 status=1 waitReason=0 waitId=0 pc=0x31ac60 entry=0x31ac60 priority=101 scheduled=0`; `id=4 status=2 waitReason=2 waitId=29 pc=0x423de8 entry=0x31ac08 priority=99 scheduled=306` |
| New park | Thread 1 `Running` at `pc=0x391330` (in `sub_003912A8,[0x3912a8,0x391360)`), `scheduled` 302→304→306 across the last blocks with stable pc; threads 3 (`sub_0031AAF0` entry `0x31ac60`) and 4 (`sub_0031AAF0` entry `0x31ac08`, parked `WaitSema` on 29) exist only after the fix |
| First new syscall ids (block 0 `distinct=24`) | `0x44,0xffffffbd,0x2f,0x40,0x41,0xfc,0x42,0x4b,0x74,0x5b,0x64,0x22,0x20,0x3e,0x6f,0x4a,0x14,0x10,0x30,0x29` (20 of 24 shown; block-0 count was 21 pre-fix; per-id baseline diff tabled in P7-6 as not performed) |
| Stubs block 0 | `distinct=334` (top `0x3e3968` count=1135) |
| Invocation tops (block 0) | `key=0xffffffff00000000 top=0xfbff0`, `key=0xffffffff00000001 top=0xf7ff0`, `key=0x100000000 top=0xffff0` (all inside `[0x80000,0x100000)`) |
| Pending (blocks 13/17/19) | `kind=0 pc=0x3e4db8 sp=0x0` (queued with sp=0, assigned at dequeue) |
| CD | `sceCdInitEeCB stack=0x51a480 size=0x800` + 20 `sceCdRead` payload lines (`buf=0x519c80`) |
| First VIF MPG/MSCAL | None |
| First GIF kick | None |
| First presented frame | None (host window blank) |
| Crash | None |
| Missing targets | 0 (normal build) |

No further boot or fix: thread 1 is still executing at the end of boot 2 (`Running`, `scheduled` advancing); an identical third boot would repeat the observation.

## P7-4. Binaries and commits

| Binary | sha256 | Sources |
|---|---|---|
| `/tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner` (boots 1/1b) | `3c9dbe8cba53dc7be6bf69d8df6be19485d3eabb3df9dfa9aa4d044b037058c4` | Sweep runner sources + `8d203d1` + `a44b101` diag |
| `/tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner` (boot 2) | `f4d16b988d319cd8751350d0cf2554895ef1b7b2f732526d33b01615ec372fba` | Above + `6046260` fix |
| `/tmp/p1-link-strict/ps2xRuntime/ps2EntryRunner` (untouched) | `a660c92b62c61ca26c7c1049e8fe94def756bb8ddc211d375524fe7aebb0eaec` | Unchanged since P1e |

`ssx3` commits (pushed `fork ssx3`, no `runner/` or `._` files; trailers on each): `8d203d1` Diag watch/stacks/StartThread (`b15aff0..8d203d1`), `a44b101` Diag forward-declare fix (`8d203d1..a44b101`), `6046260` Kernel INTC/DMAC/alarm reserved stacks (`a44b101..6046260`). `register_functions.cpp` (generated replacement) remains a local modification, never added.

## P7-5. Exact commands

```
printf 'P1f\n' > /tmp/ssx3-host-lease   (absent before; removed at end)
ELF/CSV/python3 reads for P6 facts; sed on $W/P1/output/sub_003DCBD8_0x3dcbd8.cpp lines 116-144
(edit_file) ps2_runtime.h: ps2DiagWatch* decls + forward declare
(edit_file) ps2_runtime.cpp: watch parse/emit/report + Store8/16/32/64/128 hooks
(edit_file) ps2_runtime_macros.h: WRITE8/16/32/64/128 watch hooks
(edit_file) EeScheduler.cpp: stacks block + start-thread line + watch-thread setter + writeGuestU32/vsync watch
(edit_file) CD.h/CD.cpp: getCdCallbackStackTop decl/impl
find ps2xRuntime /tmp/p1-link -name '._*' -delete (after every edit)
git add <6 diag files>; git commit -m "Diag: ..." (trailers); git push fork ssx3   (8d203d1)
git add ps2xRuntime/include/ps2_runtime.h; git commit -m "Diag: ..." (trailers); git push fork ssx3   (a44b101)
cmake --build /tmp/p1-link/runtime --target ps2EntryRunner; shasum -a 256 (3c9dbe8c)
python3 /tmp/p1f-boot1.py (foreground 180 s, CWD $W/P1/run, PS2X_CD_IMAGE + PS2X_DIAG_PERIOD_MS=5000 + PS2X_DIAG_WATCH=0x1ffff60, stdbuf -o0 -e0, log direct to boot-p1f-1.log, SIGTERM)
python3 /tmp/p1f-boot1b.py (same, PS2X_DIAG_WATCH=0x1ffff00,0x1ffff08,0x1ffff10, log to boot-p1f-1b.log)
log reads: grep/sed/python3 grouping on closed logs only (never piped while running)
ELF words at 0x1000+(va-0x100000); csv+bisect over ssx3-functions.sweep.csv; seds in $W/P1/output (sub_003E4AF0_0x3e4af0.cpp)
ELF program headers via python3 struct over SLUS_207.72; SetupHeap/EndOfHeap reads in System.cpp
(edit_file) ps2_runtime.h + ps2_runtime.cpp: async stacks to [0x80000,0x100000)
(edit_file) EeScheduler.cpp: dispatchIrq + Alarm queue with sp=0
git add <3 fix files>; git commit -m "Kernel: ..." (trailers); git push fork ssx3   (6046260)
cmake --build /tmp/p1-link/runtime --target ps2EntryRunner; shasum -a 256 (f4d16b98)
python3 /tmp/p1f-boot2.py (same watch env as 1b, log to boot-p1f-2.log)
git add -f local/research/P1/REPORT.md; git commit -m "[P1f] ..." (trailers); git push fork ssx3
rm /tmp/ssx3-host-lease (verified absent)
```

## P7-6. What I could not do

- HLE `getMemPtr`/`memcpy`/`memset` stubs write guest RAM without passing the watch hooks; boot-2's zero `thread=-1` count covers only the hooked writers (the 165 remaining boot-2 watch lines are `thread=1`).
- Watch thread id is the scheduler's current thread at dispatch; invocations running on their owner share the owner id (only `id=-1` invocation threads are distinct).
- Step 1 took two commits instead of one (`a44b101` repairs the `8d203d1` build break); all three `ssx3` commits are tabled in P7-1/P7-3.
- Per-id new-syscall baseline diff vs the pre-fix 21-id set not performed (the 20 listed boot-2 block-0 ids are given without the old set beside them).
- Full `ra=0x3dcc64` provenance across the tail-jump chain (`0x3dcd4c`→`0x3e3020`→`0x3e57f8`→`0x3dcc64`) remains at the P6-7 state; boot 1b shows the prologue save did run this time (line 208), so the skipped-save path is boot-dependent.
- No boot 3: thread 1 is still executing at the end of boot 2, and an identical boot would repeat the observation; no further fix per the brief.
- `waits.log`: no waits (no foreign lease during P1f).
- Time box: about 2 h of the 4 h box used.

# P1g report — Part 8 (brief local/muse/prompts/P1g.md)

## P8-0. Lease record

| Event | Value |
|---|---|
| Start | `/tmp/ssx3-host-lease` read `M5` (foreign, host-lease priority); not taken, not overwritten |
| Step 1 | No lease needed (closed `boot-p1f-2.log` + ELF + checked-in sources only); no polling, no `p1g-waits.log` |
| Step 2 | Skipped: Step 1 answers the park (P8-1d), so no boot, no lease hold at all |
| `adb` | Not used |
| End | Lease still `M5`; left untouched; no `boot-p1g-*.log` produced |
| Push note | No `PS2Recomp` commit in this brief (diagnose only); the lease/push rules for `fork ssx3` therefore move no code. This report commit goes to the `ssx3` repo (`origin/main`, where `[P1e]`/`[P1f]` already sit); nothing is pushed to the `ran-j` upstream |

## P8-1. Park diagnosis (Step 1 only; Step 2 skipped per P8-1d)

### P8-1a. ELF hand disassembly of `sub_003912A8` (`SLUS_207.72`, `off=0x1000+(va-0x100000)`)

`mipsel-linux-gnu-objdump` is not installed (`command not found`); no install per the brief. Each word below was decoded by hand from the opcode table and cross-checked against the recomp comments in `$W/P1/output/sub_003912A8_0x3912a8.cpp` (identical bytes in `ps2xRuntime/src/runner/`, `diff -q` clean). `beq $r,$zero`/`bne $r,$zero` are the `beqz`/`bnez` the recomp prints.

| va | word | mnemonic | what it does |
|---|---|---|---|
| 0x3912a8 | 0x27bdfff0 | addiu $sp,$sp,-0x10 | frame: sp-=16 |
| 0x3912ac | 0x3c021000 | lui $v0,0x1000 | $v0=0x10000000 |
| 0x3912b0 | 0xffbf0000 | sd $ra,0($sp) | save ra |
| 0x3912b4 | 0x34428000 | ori $v0,$v0,0x8000 | $v0=0x10008000 (VIF0_CHCR) |
| 0x3912b8 | 0x8c430000 | lw $v1,0($v0) | $v1=\*0x10008000 |
| 0x3912bc | 0x30630100 | andi $v1,$v1,0x100 | isolate bit 8 (STR) |
| 0x3912c0 | 0x1060000a | beq $v1,$zero→0x3912ec | skip loop 1 if STR clear (DS next) |
| 0x3912c4 | 0x3c031000 | lui $v1,0x1000 (DS) | $v1=0x10000000 (always runs) |
| 0x3912c8 | 0x34638000 | ori $v1,$v1,0x8000 | $v1=0x10008000 |
| 0x3912cc | 0x00000000 | nop | |
| 0x3912d0 | 0x8c620000 | lw $v0,0($v1) | loop 1: $v0=\*0x10008000 |
| 0x3912d4 | 0x30420100 | andi $v0,$v0,0x100 | |
| 0x3912d8 | 0x00000000 | nop | |
| 0x3912dc | 0x00000000 | nop | |
| 0x3912e0 | 0x00000000 | nop | |
| 0x3912e4 | 0x1440fffa | bne $v0,$zero→0x3912d0 | spin while STR set |
| 0x3912e8 | 0x00000000 | nop (DS) | |
| 0x3912ec | 0x3c041000 | lui $a0,0x1000 | $a0=0x10000000 |
| 0x3912f0 | 0x3c020044 | lui $v0,0x44 | $v0=0x00440000 |
| 0x3912f4 | 0x2442bd00 | addiu $v0,$v0,-0x4300 | $v0=0x0043bd00 |
| 0x3912f8 | 0x34848030 | ori $a0,$a0,0x8030 | $a0=0x10008030 (VIF0_TADR) |
| 0x3912fc | 0x3c031000 | lui $v1,0x1000 | $v1=0x10000000 |
| 0x391300 | 0xac820000 | sw $v0,0($a0) | \*0x10008030=0x43bd00 (TADR) |
| 0x391304 | 0x34638020 | ori $v1,$v1,0x8020 | $v1=0x10008020 (VIF0_QWC) |
| 0x391308 | 0x3c041000 | lui $a0,0x1000 | $a0=0x10000000 |
| 0x39130c | 0xac600000 | sw $zero,0($v1) | \*0x10008020=0 (QWC) |
| 0x391310 | 0x34848000 | ori $a0,$a0,0x8000 | $a0=0x10008000 (VIF0_CHCR) |
| 0x391314 | 0x24030104 | addiu $v1,$zero,0x104 | $v1=0x104 (STR bit 8 + chain mode bit 2) |
| 0x391318 | 0xac830000 | sw $v1,0($a0) | \*0x10008000=0x104 (DMA kick) |
| 0x39131c | 0x8c820000 | lw $v0,0($a0) | $v0=\*0x10008000 |
| 0x391320 | 0x30420100 | andi $v0,$v0,0x100 | |
| 0x391324 | 0x10400009 | beq $v0,$zero→0x39134c | skip loop 2 if STR clear (DS next) |
| 0x391328 | 0x3c031000 | lui $v1,0x1000 (DS) | $v1=0x10000000 |
| 0x39132c | 0x34638000 | ori $v1,$v1,0x8000 | $v1=0x10008000 |
| 0x391330 | 0x8c620000 | lw $v0,0($v1) | PARK: loop 2 head, $v0=\*0x10008000 |
| 0x391334 | 0x30420100 | andi $v0,$v0,0x100 | |
| 0x391338 | 0x00000000 | nop | |
| 0x39133c | 0x00000000 | nop | |
| 0x391340 | 0x00000000 | nop | |
| 0x391344 | 0x1440fffa | bne $v0,$zero→0x391330 | spin while STR set (park) |
| 0x391348 | 0x00000000 | nop (DS) | |
| 0x39134c | 0x0c109008 | jal 0x424020 | FlushCache trampoline (never reached while parked; DS next) |
| 0x391350 | 0x0000202d | daddu $a0,$zero,$zero (DS) | $a0=0 |
| 0x391354 | 0xdfbf0000 | ld $ra,0($sp) | restore ra |
| 0x391358 | 0x03e00008 | jr $ra | return (DS next) |
| 0x39135c | 0x27bd0010 | addiu $sp,$sp,0x10 (DS) | pop frame |

Branch targets: `0x3912c0→0x3912ec` (else `0x3912c8`); `0x3912e4→0x3912d0` (else `0x3912ec`); `0x391324→0x39134c` (else `0x39132c`); `0x391344→0x391330` (else `0x39134c`); `0x39134c→0x424020` (ret `0x391354`); `0x391358→$ra`. Enclosing block of the park = `0x39132c–0x391348`. Register names for `0x10008000/20/30`: `ps2_debug_panel.cpp:1918-1921` (`VIF0_CHCR`, `VIF0_MADR`, `VIF0_QWC`, `VIF0_TADR`); DMA channel bases incl. `0x10008000u`: `Support.h:1233`; `VIF0_CHANNEL = 0x10008000`: `ps2_memory.cpp:1749`.

True MMIO address per access (hand decode, LUI+ORI+offset) vs the folded constant the recompiled code actually uses:

| pc | true address | recomp constant (`sub_003912A8_0x3912a8.cpp` line) | `$W/P1/ssx3.toml` `[mmio]` line |
|---|---|---|---|
| 0x3912b8 (lw) | 0x10008000 | 0x10000000u (:44) | 767 |
| 0x3912d0 (lw) | 0x10008000 | 0x10000000u (:73) | 716 |
| 0x391300 (sw TADR) | 0x10008030 | 0x10000000u (:117) | 760 |
| 0x39130c (sw QWC) | 0x10008020 | 0x10000000u (:126) | 715 |
| 0x391318 (sw CHCR) | 0x10008000 | 0x10000000u (:135) | 695 |
| 0x39131c (lw) | 0x10008000 | 0x10000000u (:138) | 714 |
| 0x391330 (lw, park) | 0x10008000 | 0x10000000u (:164) | 737 |

All 7 map to `0x10000000`: the TOML `[mmio]` map holds 273 entries, 249 of them `0x10000000` (only 24 specific, e.g. `0x371b04→0x10008000`). The analyzer's detector (`ps2xAnalyzer/src/elf_analyzer.cpp:424-456`) scans back ≤5 instructions for the LUI, takes `baseAddr = IMM<<16`, and adds only the `int16` load/store offset — the ORI low half (`ori $v,$v,0x8000/0x8020/0x8030`) is never read, so every LUI+ORI+`0($r)` access folds to the page base.

### P8-1b. Function bounds + callers

| Item | Value |
|---|---|
| Sweep row (`ssx3-functions.sweep.csv:6968`) | `sub_003912A8,0x3912a8,0x391360,0xb8` (46 instructions, tabled above) |
| Neighbours | `sub_00390EF8,[0x390ef8,0x3912a8)` ends `jr $ra` at `0x3912a0` (no fallthrough); `sub_00391360,[0x391360,0x391418)` follows |
| Direct J/JAL into `[0x3912a8,0x391360)` (full `.text` scan, `vaddr=0x100000 off=0x1000 filesz=0x3a4bf4`) | 1: `0x375a8c: 0x0c0e44aa jal` → field `0x0e44aa<<2 = 0x3912a8` (function entry; no J, no mid-range target) |
| Caller delay slot + return | `0x375a90: 0x0200202d daddu $a0,$s0,$zero` ($a0=$s0; callee clobbers $a0 at `0x3912ec`, arg unused); ret `0x375a94: 0x0c0e44d8 jal 0x391360` (next function, same $a0) |
| Caller function | `sub_00375A08,[0x375a08,0x376938)` (sweep); recomp `sub_00375A08_0x375a08.cpp:1209-1231` (`label_375a8c`, `dispatchGuestBranch(...,0x3912A8u,0x375A8Cu,0x375A94u,...)`); same bytes in `runner/` (3 `3912A8` refs) |
| Branches into range (BEQ/BNE/BLEZ/BGTZ/REGIMM, outside→inside) | 0 |
| Indirect (JR/JALR via register, function tables) | Not enumerable from the closed log + ELF; no runtime trace of the call was recorded |
| Other recomp refs to `3912A8` | `ps2_recompiled_functions.h`, `register_functions.cpp`, own file, predecessor file (fallthrough check only) |
| Tail callee | `0x39134c jal 0x424020`: `sub_00424020,[0x424020,0x424050)` = 3 syscall trampolines (`0x424020: addiu $v1,0x64; syscall` = FlushCache; `0x424030: $v1=0x66`; `0x424040: $v1=-0x67`); park never reaches it |

### P8-1c. Closed-log receipts (`boot-p1f-2.log`, 1464 lines)

The log contains no literal `dispatch` lines (`grep -ci dispatch` = 0). The per-dispatch receipt is the `[diag:thread] ... scheduled=N` line (one per thread per 5 s block). Last 30 such lines (log lines 1212–1213 + 1242–1437 = block-27 tail + blocks 28–34):

| log line | block | id | pc | scheduled |
|---|---|---|---|---|
| 1212–1213 | 27 (tail) | 3, 4 | 0x31ac60, 0x423de8 | 0, 303 |
| 1242–1245 | 28 | 1, 2, 3, 4 | 0x391330, 0x423de8, 0x31ac60, 0x423de8 | 302, 0, 0, 302 |
| 1274–1277 | 29 | 1, 2, 3, 4 | 0x391330, 0x423de8, 0x31ac60, 0x423de8 | 303, 0, 0, 303 |
| 1306–1309 | 30 | 1, 2, 3, 4 | 0x391330, 0x423de8, 0x31ac60, 0x423de8 | 300, 0, 0, 300 |
| 1338–1341 | 31 | 1, 2, 3, 4 | 0x391330, 0x423de8, 0x31ac60, 0x423de8 | 305, 0, 0, 305 |
| 1370–1373 | 32 | 1, 2, 3, 4 | 0x391330, 0x423de8, 0x31ac60, 0x423de8 | 304, 0, 0, 304 |
| 1402–1405 | 33 | 1, 2, 3, 4 | 0x391330, 0x423de8, 0x31ac60, 0x423de8 | 302, 0, 0, 302 |
| 1434–1437 | 34 | 1, 2, 3, 4 | 0x391330, 0x423de8, 0x31ac60, 0x423de8 | 306, 0, 0, 306 |

Thread 1 pc is `0x391330` in all 35 blocks (lines 307–1434, first at block 0 `scheduled=280`): one stable stop sampled every 5 s over ~175 s with ~300 scheduler passes per period re-entering the same pc — a tight spin, not one stop among many. Mechanism in the recomp: `label_391330` takes `if (eeCheckpointDue()) return` on the back edge (`sub_003912A8_0x3912a8.cpp:182-186`), and re-entry lands on `case 0x391330u: goto label_391330` (:23), so each checkpoint yields to the scheduler (`scheduled++`) and resumes at the same pc.

Last block (34) full thread table (lines 1433–1448; status/wait enums `ee_scheduler.h:25-44`: status 0=Running 1=Ready 2=Waiting; reason 0=None 2=Semaphore):

| id | status | waitReason | waitId | pc | entry | priority | scheduled | stack (sp) |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 Running | 0 None | 0 | 0x391330 | 0x100008 | 100 | 306 | [0x1fe0000,0x2000000) sp=0x1fffd80 |
| 2 | 2 Waiting | 2 Semaphore | 26 | 0x423de8 | 0x3e3be0 | 12 | 0 | [0x51ac80,0x51ec80) sp=0x51ec20 |
| 3 | 1 Ready | 0 None | 0 | 0x31ac60 | 0x31ac60 | 101 | 0 | [0x6088d0,0x6188d0) sp=0x6188d0 |
| 4 | 2 Waiting | 2 Semaphore | 29 | 0x423de8 | 0x31ac08 | 99 | 306 | [0x6048c0,0x6088c0) sp=0x6088a0 |

Block-34 companions: invocation tops `0xfbff0/0xf7ff0/0xffff0` (in `[0x80000,0x100000)`); `cdCallbackStackTop=0x51ac80`; `intc id=2 cause=3 handler=0x31a490 sp=0x1fffe30`; `intc id=1 cause=10 handler=0x3e4db8 sp=0x1ffff20`; no `pending` row in block 34 (pending `kind=0 pc=0x3e4db8 sp=0x0` appears only at blocks 13/17/19, lines 774/903/968); no vsync/alarm rows in any block.

Syscalls (names from `Dispatcher.cpp` case list; histogram prints top 20, `distinct` is exact):

| block | distinct | ids (count, first/last pc) |
|---|---|---|
| 0 (lines 322–342) | 24 (20 shown, 4 unprinted — not recoverable from the closed log) | 0x44 WaitSema (298, 0x423de8); 0xffffffbd iSignalSema/-0x43 (277, 0x423dd8); 0x2f unhandled→TODO/default (57, 0x423c98); 0x40 CreateSema (31); 0x41 DeleteSema (20); 0xfc SetAlarm (20); 0x42 SignalSema (19); 0x4b GetOsdConfigParam (9); 0x74 SetSyscall (8); 0x5b GetEntryAddress (6); 0x64 FlushCache (4, 0x424028); 0x22 StartThread (3); 0x20 CreateThread (3); 0x3e EndOfHeap (3); 0x6f GetOsdConfigParam2 (3); 0x4a SetOsdConfigParam (2); 0x14 EnableIntc (2); 0x10 AddIntcHandler (2); 0x30 ReferThreadStatus (1); 0x29 ChangeThreadPriority (1) |
| 1–34 | 2 each | 0x44 WaitSema + 0xffffffbd iSignalSema only, counts equal to the period's thread-1/4 `scheduled` (300–306); first=last=0x423de8 / 0x423dd8 every block |

Trampolines (ELF): `0x423dd0: addiu $v1,$zero,-0x43; syscall; jr $ra` (post-syscall pc `0x423dd8`); `0x423de0: addiu $v1,$zero,0x44; syscall; jr $ra` (post-syscall pc `0x423de8`). Both steady-state syscall pcs are thread 4's (and thread 2's) parked pc — never `0x391330`: thread 1 issues no syscall while parked. Block-34 stubs (`distinct=12`, lines 1452–1464): counts 306 (612 for the 3 double-hit: `0x3ffa58/0x3ffbc0/0x326eb0`), `firstRa=lastRa` per target (`0x3271e8/0x326f24/0x326bf8/0x31ac30/0x3173e4/0x227f70/0x3173c4/0x317514/0x31ac28/0x31abf8/0x31abe0/0x31a5a0`), none in `0x391xxx` — thread 4's WaitSema/iSignalSema ping-pong (`sub_0031AAF0` loop via `0x423dd0/0x423de0`), no thread-1 stub activity.

CD/VIF/GIF/frame/crash (last activity):

| rung | receipt |
|---|---|
| Last CD | line 291 `[diag:cd] sceCdInitEeCB stack=0x51a480 size=0x800`; 20 `sceCdRead`+payload pairs lines 209–287 (lbns `0x10,0x105-0x107,0x109-0x117`); nothing after line 291 |
| `[cd:callback]` (Fix D receipt) | 0 lines in the whole log |
| VIF / GIF / MPG / MSCAL (case-insensitive) | 0 / 0 / 0 / 0 lines; the only `frame` hit is raylib line 46 (`Target time per frame`); the only `DMA` hit is the `PADMAN.IRX` substring (line 161) |
| Presented frame / crash / `Missing targets` | 0 / 0 / 0 lines |
| Dormant | 41 lines, all `id=-1`, lines 211–289; zero `id=1`; none after line 289 |
| Watch | 164 lines start with `[diag:watch]`, 165 contain it (line 158 is `[SifInitRpc] Initialized[diag:watch]...`); all `thread=1`, last at line 305 — none during the park |
| StartThread | 3 lines: 290 (`id=2`), 303 (`id=3`), 304 (`id=4`) |
| SIF modules | 6 loads, lines 159–169 (`SIO2MAN/PADMAN/LIBSD/SNDDRV/MCMAN/MCSERV`) |

What thread 1 is waiting on (elimination table):

| candidate | log evidence | held? |
|---|---|---|
| Sema id 26/29 | thread 1 `waitReason=0 waitId=0` every block; sema waits belong to threads 2 (id 26) and 4 (id 29) | no |
| VSync / alarm | no vsync/alarm wait rows in any `[diag:stacks]` block; `SetAlarm` appears only in block-0 syscalls | no |
| CD callback | last CD line 291; zero `[cd:callback]` lines; `cdCallbackStackTop` static | no |
| VIF MPG/MSCAL completion | zero VIF/GIF lines; the polled bit never clears for a different reason (P8-1d) | no (nothing VIF-side is in flight) |
| Kernel object of any kind | status `Running`, `scheduled` advancing ~300/period, no syscall/stub from `0x391xxx` | no |
| MMIO bit 8 (0x100) at true `0x10008000` (VIF0_CHCR STR), read as `m_ioRegisters[0x10000000]` | P8-1d proof chain | **yes** |

### P8-1d. Wait object + proof (Step 1d answer; Step 2 skipped)

Wait object: bit 8 (`0x100`, the CHCR start bit the runtime tests at `ps2_memory.cpp:1270` and clears at `:1779/:2230`) of the VIF0 DMA channel control register at true address `0x10008000`, polled by the `0x391330` loop. Under the shipped recomp the loop reads `m_ioRegisters[0x10000000]` instead, which holds `0x104` (the last of the three folded stores), so the bit reads set on every pass and `bnez` never falls through. Exact proof chain:

| # | fact | exact line / word |
|---|---|---|
| 1 | Guest programs TADR/QWC/CHCR then polls CHCR bit 8 | ELF `0x391300 sw→0x10008030`, `0x39130c sw 0→0x10008020`, `0x391318 sw 0x104→0x10008000`, `0x391330 lw` + `0x391334 andi 0x100` + `0x391344 bnez→0x391330` (P8-1a) |
| 2 | Recomp folds all 7 accesses to `0x10000000u` | `sub_003912A8_0x3912a8.cpp:44,73,117,126,135,138,164` (output == runner, `diff -q` clean) |
| 3 | Fold values come from the TOML map | `ssx3.toml:695,714,715,716,737,760,767` (`"0x3913xx" = "0x10000000"`); map read at `config_manager.cpp:129-146`, applied at `ps2_recompiler.cpp:1972-1977` |
| 4 | The map is wrong because the detector ignores ORI | `elf_analyzer.cpp:427-447` (LUI-only `baseAddr`, `+ int16(offset)`); `0x10008000` needs the `ori 0x8000` the detector never reads |
| 5 | Folded stores persist `0x104` at `0x10000000`, kick path never runs | `writeIORegister`: unconditional `m_ioRegisters[address]=value` (`ps2_memory.cpp:1198`); DMA block requires `address≥0x10008000` (`:1268`), so the three stores land in order `0x43bd00, 0, 0x104` with no transfer, no STR clear |
| 6 | Folded reads return `0x104` forever (no auto-clear off-range) | `readIORegister`: CHCR auto-clear (`:2230`) only inside `[0x10008000,0x1000F000)` (`:2226`); `0x10000000` falls to the generic `m_ioRegisters` lookup (`:2255-2258`) → `0x104`, bit set every pass |
| 7 | Hence pc-stable + scheduled-advancing, no kernel wait | log lines 307–1434 (`pc=0x391330` × 35 blocks, `scheduled` 280→306/period); `status=0/reason=0`; zero syscalls/stubs from `0x391xxx` (P8-1c) |

No further receipt is needed: the closed log plus the ELF plus the checked-in sources fully determine the park, so Step 2 (lease-poll + ≤90 s boot) is skipped with no missing receipt.

## P8-2. Ladder delta vs boot 2 (no new boot)

Step 2 was skipped, so there is no `boot-p1g-1.log` and no ladder delta. Boot-2 ladder (from `boot-p1f-2.log`, fixed binary `f4d16b98`) restated as the baseline P1g starts from:

| Rung | Boot 2 (unchanged by P1g) |
|---|---|
| Thread 1 | `Running` at `pc=0x391330` in all blocks 0–34, `scheduled` ~300/period |
| Threads 2 / 3 / 4 | WaitSema-26 (`scheduled=0` after block 0) / Ready (`scheduled=0`) / WaitSema-29 (`scheduled` tracks thread 1) |
| New syscall ids | Block-0 set only (P8-1c); blocks 1–34 add none |
| First VIF MPG/MSCAL | None |
| First GIF kick | None |
| First presented frame | None |
| Crash | None |
| CD | Idle since line 291 |

## P8-3. Binaries and commits

| Binary / ref | sha256 / sha | sources / state |
|---|---|---|
| `/tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner` | `f4d16b988d319cd8751350d0cf2554895ef1b7b2f732526d33b01615ec372fba` | Unchanged since P1f boot 2 (re-verified this session); no rebuild in P1g |
| `PS2Recomp` branch `ssx3` HEAD | `6046260` (`Kernel: run INTC/DMAC/alarm handlers on reserved stacks, not thread sp`) | No new commit (diagnose only); worktree has only the pre-existing local `M ps2xRuntime/src/runner/register_functions.cpp`, never added |
| This report | `[P1g]` commit on `ssx3` repo `main` (trailers below) | The sole new commit of this brief; no `runner/`, log, or `._*` file added |

No `fork ssx3` push moves code (nothing committed there); the report commit is pushed to the `ssx3` repo's `origin/main`, matching `[P1e]`/`[P1f]`.

## P8-4. Exact commands

```
cat /tmp/ssx3-host-lease   (M5 at start and end; never written, never removed)
git -C <PS2Recomp> branch --show-current; git remote -v   (ssx3; fork + origin)
git -C /Users/bradrichardson/dev/ssx3 log --oneline -12; git status --short   (HEAD 5a6b9d3, clean)
shasum -a 256 /tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner   (f4d16b98…)
which mipsel-linux-gnu-objdump   (not found; hand decode, no install)
python3 struct over $W/P1/SLUS_207.72 at off=0x1000+(va-0x100000): words 0x3912a8–0x391360, caller 0x375a8c–0x375a94, trampolines 0x423dd0–0x423dec + 0x424020–0x424050; hand MIPS decode per word
grep -n sub_003912A8 $W/P1/ssx3-functions.sweep.csv   (line 6968) + neighbours; csv enclosing-function lookups for caller/pc/stub pcs
full-.text J/JAL + branch-target scan into [0x3912a8,0x391360)   (1 JAL at 0x375a8c, 0 branches)
diff -q runner/sub_003912A8_0x3912a8.cpp $W/P1/output/sub_003912A8_0x3912a8.cpp   (clean); grep Load32/Store32 MMIO lines in both
grep -n '"0x391...' $W/P1/ssx3.toml   ([mmio] lines 695,714-716,737,760,767); python3 Counter over [mmio] (273 entries, 249 × 0x10000000)
reads (no edits): ps2_memory.cpp:941-999,1104-1200,1262-1560,1748-1789,2203-2262; ps2_runtime.cpp:2257-2268,2330-2346,2447-2450; elf_analyzer.cpp:423-456; config_manager.cpp:129-146; Dispatcher.cpp case list + :81 top-20 cap; ee_scheduler.h:25-44; ps2_debug_panel.cpp:1910-1922
python3 over boot-p1f-2.log (closed log only): line-kind Counter; last-30 [diag:thread]; all id=1 pcs; all [diag:syscalls/syscall]; block-0 vs block-34 stubs; cd lines; case-insensitive counts for vif/gif/mpg/mscal/frame/crash/missing; dormant/watch/start-thread/SIF surveys
grep -c 'cd:callback' boot-p1f-2.log   (0)
git -C /Users/bradrichardson/dev/ssx3 add -f local/research/P1/REPORT.md; commit -m "[P1g] ..." (trailers); push origin main
```

## P8-5. What I could not do

- No boot in this brief: Step 1 answered the park, so Step 2 was skipped by design; the M5 lease was never touched and no `p1g-waits.log` / `boot-p1g-*.log` exists.
- Block-0's 4 unprinted syscall ids (`distinct=24`, top-20 print cap at `Dispatcher.cpp:81`) are not recoverable from the closed log; only the 20 shown are tabled.
- The other 242 TOML `[mmio]` entries folding to `0x10000000` were not audited: truncation is proven only for this function's 7 pcs (P8-1a table).
- Indirect callers (JR/JALR, function tables) into `[0x3912a8,0x391360)` are not enumerable from ELF + closed log; the direct J/JAL/branch scan is exhaustive, the indirect set is unknown.
- No disassembler: all mnemonics are hand-decoded (cross-checked against recomp comments, which agree on every word).
- No runtime fix per the brief: the next rung (correct LUI+ORI MMIO addresses, or dynamic MMIO dispatch) is named in P8-1d and left for a later brief.
- Watch-count note: P7-3's `165` counts lines *containing* `[diag:watch]` (incl. line 158's `[SifInitRpc]`-prefixed line); `164` lines *start* with it. Both numbers are correct under their count.
- `0x2f` (57 hits, block 0) has no `Dispatcher.cpp` case and falls to `TODO()` via `handleSyscall`; its guest meaning was not pursued (boot-time only, absent from steady state).
- Time box: well under the 2 h box (single session, no boots, no builds).

# P1h report — Part 9 (brief local/muse/prompts/P1h.md)

Run wall: 2026-09-18 21:05 → 21:40 EDT (Fri). `W` = `/Volumes/Extreme SSD/ps2recomp-spike`.
No verdicts. Step 1 (analyzer fix + commit + push) and Step 2 (regen + audit)
ran without the lease; Step 3 (rebuild + one boot) took the lease while absent.

## P9-0. Lease record

| Event | Value |
|---|---|
| Start | `/tmp/ssx3-host-lease` read `M5` (foreign, priority); not taken, not overwritten |
| Steps 1–2 + rebuild | No lease (analyzer build, regen file-to-file, runtime rebuild need none) |
| 21:21 EDT | Lease absent (M5's hold gone; never overwritten) |
| 21:26 EDT | Lease absent; wrote `P1h`; booted 21:26–21:29 EDT |
| Foreign waits | None; no poll loop ran, no `$W/P1/run/p1h-waits.log` exists |
| `adb` | Not used |
| End | Removed after the report commit, verified absent |

## P9-1. Analyzer rule + diff (Step 1, one commit)

Scan first (all 273 current-TOML `[mmio]` pcs, ELF words at `0x1000+(va-0x100000)`):

| Item | Value |
|---|---|
| pcs with nearest LUI to the base reg within 5 back | 273/273 |
| pcs with ≥1 intervening writer to the base reg | 245, each exactly one |
| intervening opcode | Same-register `ORI $r,$r,imm` in all 245; zero `ADDIU`, zero any other opcode |
| pcs with no intervening writer | 28 (24 specific-offset + the 4 genuine-`0x10000000` of P9-2) |

Exact rule (covers `ORI` + `ADDIU` per the brief; the `ADDIU` arm is unobservable
in this game — no `ADDIU` low-half writer occurs in the 273): keep the nearest-LUI
≤5 scanback unchanged; then apply, in program order, every same-register
(`rt==rs==base`) `ORI` (`base |= imm`, zero-extended) and `ADDIU`
(`base += sign_extend(imm)`, 32-bit wrap) strictly between the LUI and the
access; `target = base + sign_extend(offset)`. No LUI found keeps the old
behavior (no entry). Other intervening writers are ignored (none occur in the
273). Composition mirrors the sibling `addSignedImm16`/`orUnsignedImm16`
convention (`analysis_passes.cpp:101-109,291-303`).

```diff
--- a/ps2xAnalyzer/src/elf_analyzer.cpp
+++ b/ps2xAnalyzer/src/elf_analyzer.cpp
@@ -425,6 +425,7 @@
                         // Look for the LUI instruction that sets up the high bits
                         uint32_t baseAddr = 0;
+                        uint32_t luiAddr = 0;
                         for (int i = 1; i <= 5 && ...) // unchanged scanback
@@ -438,10 +439,37 @@
                             if (OPCODE(prevInst) == OPCODE_LUI && RT(prevInst) == inst.rs)
                             {
                                 baseAddr = IMMEDIATE(prevInst) << 16;
+                                luiAddr = prevAddr;
                                 break;
                             }
                         }
+
+                        // Account for the low half: apply same-register ORI/ADDIU
+                        // writers between the LUI and the access, in program order.
+                        if (luiAddr != 0)
+                        {
+                            for (uint32_t midAddr = luiAddr + 4; midAddr < inst.address; midAddr += 4)
+                            {
+                                uint32_t midInst = 0;
+                                if (!tryReadWord(m_elfParser.get(), midAddr, midInst))
+                                    continue;
+                                if (RT(midInst) == inst.rs && RS(midInst) == inst.rs)
+                                {
+                                    if (OPCODE(midInst) == OPCODE_ORI)
+                                        baseAddr |= IMMEDIATE(midInst);
+                                    else if (OPCODE(midInst) == OPCODE_ADDIU)
+                                        baseAddr += (uint32_t)(int32_t)(int16_t)IMMEDIATE(midInst);
+                                }
+                            }
+                        }
```

| Receipt | Value |
|---|---|
| Commit | `f2149e7` `Analyzer: fold LUI low half from ORI/ADDIU into MMIO target` (1 file, +28; trailers) |
| Push | `fork ssx3` `6046260..f2149e7` |
| Analyzer rebuild | `cmake --build /tmp/p1-link/tools --target ps2_analyzer -j4`, exit 0 |
| New analyzer sha256 | `900660c98aba33ace85152586bdf922e92629eaf8c04d3bbdf0d91ba746720d4` (`/tmp/p1-link/tools/ps2xAnalyzer/ps2_analyzer`) |

## P9-2. Regen audit (Step 2, no lease)

Regen: new analyzer → `ssx3.toml.p1h-new` (raw), then the two standing deltas
re-applied (`ghidra_output = "ssx3-functions.sweep.csv"`, `"ret0@0x0042c1f0",`
after `InitTLB@0x0042CD58`); final `ssx3.toml` differs from `ssx3.toml.p1h-orig`
only in `[mmio]` (backup kept). Raw-new vs analyzer-pristine `ssx3.toml.p1-orig`:
all 494 diff lines are `[mmio]` entries, no other section changed.
`$W/P1/bin/ps2_analyzer` left at the old build (`4bf4ba2b…`); the new analyzer
ran from the `/tmp` build path. Recomp binary unchanged (`7654e7fe…` both paths).

| Item | Value |
|---|---|
| `[mmio]` entries old → new | 273 → 273 (0 added, 0 removed) |
| Entries changed | 245 |
| Entries still `0x10000000` | 4 (tabled below) |
| Hand cross-check | Independent python model of the new rule vs all 273 new targets: 0 mismatches |
| Recomp summary (`recomp-p1h.log`) | discovered 9269 / processed 9269 / recompiled 9092 / stubs 177 / skipped 0 / decode failures 0 / unhandled 0; entrypoints 393727; warnings 3598; fallbacks 724964 (identical to `recomp-p1d-sweep.log`) |
| Runner-source diff (`output/` vs pre-regen `runner/`) | 57 files, 263 insertions / 263 deletions; every changed line is an MMIO-constant line; old side all `0x10000000u`; new side real targets (`0x10008000/20/30`, `0x10009000/10/20/30`, `0x1000A000/10/20/30`, timers, `0x1000F000/130/520`, `0x10002000/10/20`, etc.); MMIO code lines 346 both sides; folded code lines 267 → 4. Never committed. |

Remaining folded entries, one line each (hand decode; all folds correct):

| pc | True address | Why the new rule still folds it |
|---|---|---|
| `0x3e4cd0` (lw `$v1,0($v0)`) | `0x10000000` | `LUI $v0,0x1000` @`0x3e4ccc`, no writer to `$v0`, offset 0 |
| `0x3e4cd4` (sw `$a2,0($v0)`) | `0x10000000` | Same LUI, no writer, offset 0 |
| `0x3e4cd8` (sw `$a3,0($v0)`) | `0x10000000` | Same LUI, no writer, offset 0 |
| `0x3e4c78` (lw `$a2,0($v1)`) | `0x10000000` | `LUI $v1,0x1000` @`0x3e4c70`, no writer to `$v1` (the `ORI` @`0x3e4c7c` targets `$v0`), offset 0 |

The 7 `sub_003912A8` pcs (TOML old → new; regenerated `.cpp` lines):

| pc | TOML before | TOML after | `output/sub_003912A8_0x3912a8.cpp` |
|---|---|---|---|
| `0x3912b8` (lw) | `0x10000000` | `0x10008000` | `:44 Load32 … 0x10008000u` |
| `0x3912d0` (lw) | `0x10000000` | `0x10008000` | `:73 Load32 … 0x10008000u` |
| `0x391300` (sw TADR) | `0x10000000` | `0x10008030` | `:117 Store32 … 0x10008030u` |
| `0x39130c` (sw QWC) | `0x10000000` | `0x10008020` | `:126 Store32 … 0x10008020u` |
| `0x391318` (sw CHCR) | `0x10000000` | `0x10008000` | `:135 Store32 … 0x10008000u` |
| `0x39131c` (lw) | `0x10000000` | `0x10008000` | `:138 Load32 … 0x10008000u` |
| `0x391330` (lw, ex-park) | `0x10000000` | `0x10008000` | `:164 Load32 … 0x10008000u` |

Only one regenerated file still contains `MMIO: 0x10000000`
(`output/sub_003E4AF0_0x3e4af0.cpp`, the 4 genuine pcs).

## P9-3. Boot ladder (Step 3: rebuild `/tmp/p1-link`, boot 1)

Runner refresh: `cp -X output/*.{cpp,h}` → `ps2xRuntime/src/runner/` (9273 files,
`diff -rq` clean after), sidecars purged. Rebuild
`cmake --build /tmp/p1-link/runtime --target ps2EntryRunner -j4`, exit 0.
Boot 1 (`$W/P1/run/boot-p1h-1.log`, 1298 lines, 132689 B, CWD `$W/P1/run`,
env `PS2X_CD_IMAGE` + `PS2X_DIAG_PERIOD_MS=5000`, no `WATCH`/`REPORT_ALL`,
foreground 180 s, SIGTERM, exit -15, no stray left):

| Rung | Boot 1 |
|---|---|
| Binary sha256 | `43aba129a36e4c1626463175f86f52f5d68053e05d93e0898d57e0051cf95314` |
| Thread-1 pc past `0x391344`? | Yes: `0x375d10` in all 35 blocks (returned via `0x375a94`, +`0x27c` into caller `sub_00375A08,[0x375a08,0x376938)`) |
| Thread table, last dump (block 34, lines 1268–1271) | `id=1 status=0 Running waitReason=0 waitId=0 pc=0x375d10 entry=0x100008 pri=100 scheduled=300`; `id=2 status=2 Waiting sema 26 pc=0x423de8 entry=0x3e3be0 pri=12 scheduled=0`; `id=3 status=1 Ready pc=0x31ac60 entry=0x31ac60 pri=101 scheduled=0`; `id=4 status=2 Waiting sema 29 pc=0x423de8 entry=0x31ac08 pri=99 scheduled=300` |
| Thread-1 stack (block-34 `[diag:stacks]`) | `[0x1fe0000,0x2000000)` `sp=0x1fffd90` (vs `0x1fffd80` at the P8 park: +`0x10`, the `sub_003912A8` frame popped) |
| Last dispatch lines | No literal `dispatch` lines in the log (`grep -ci dispatch` = 0, as in P8-1c); per-dispatch receipt is the `[diag:thread] … scheduled=N` line: block 34 `id=1/4 scheduled=300`, `id=2/3 scheduled=0` |
| First new syscall ids | None: block-0 same id set as boot-p1f-2 block 0 (`distinct=24`, same 20 shown; counts `0x44` 301/`0xffffffbd` 278/`0x2f` 63/`0x40` 31/`0x42` 21/`0x41` 20/`0xfc` 20/`0x4b` 9/`0x74` 8/`0x5b` 6/`0x64` 6/`0x22,0x20,0x3e,0x6f` 3/`0x4a,0x14,0x10` 2/`0x30,0x29` 1); blocks 1–34 only `0x44` + `0xffffffbd` (block 34: 305/305) |
| First VIF MPG/MSCAL | None (0 `vif`/`mpg`/`mscal` lines) |
| First GIF kick | None (0 `gif` lines) |
| First presented frame | None (sole `frame` hit is the raylib `Target time per frame` line) |
| Crash | None (0 `crash` lines) |
| Missing targets | 0 |
| CD | 41 lines (20 `sceCdRead`+payload pairs + `sceCdInitEeCB`); idle after; 6 SIF modules |
| Dormant / StartThread / stubs-34 | 42 `id=-1` dormant, 0 `id=1`; 3 StartThread (ids 2,3,4); stubs `distinct=12`, same target/`ra` pattern as P8 block 34 |

New park (recorded, no fix per the brief): `sub_00375A08` loop `0x375d10–0x375d28`
(`output/sub_00375A08_0x375a08.cpp:2106-2156`):

```
0x375d04: lui  $v1,0x1200        ($v1=0x12000000)
0x375d08: addiu $a0,$zero,0x4000 ($a0=0x4000)
0x375d0c: ori  $v1,$v1,0x1000    ($v1=0x12001000 = GS priv base + CSR off)
0x375d10: ld   $v0,0($v1)        PARK HEAD
0x375d14: andi $v0,$v0,0xC000
0x375d18-0x375d20: nop ×3
0x375d24: bne  $v0,$a0→0x375d10  (spin while (CSR&0xC000)!=0x4000)
```

Read path: `ld` → `READ64` → `PS2Memory::read64`, which returns
`gs_regs.csr.load()` for CSR offset `0x1000` (`ps2_memory.cpp:787-796`;
`PS2_GS_BASE 0x12000000` / `kGsCsrRegOffset 0x1000`: `ps2_memory.h:48-49` /
`ps2_memory.cpp:100`). CSR value and exit condition not pursued (stop).

## P9-4. Binaries and commits

| Binary / ref | sha256 / sha | Sources / state |
|---|---|---|
| `/tmp/p1-link/tools/ps2xAnalyzer/ps2_analyzer` | `900660c98aba33ace85152586bdf922e92629eaf8c04d3bbdf0d91ba746720d4` | `f2149e7` tree |
| `$W/P1/bin/ps2_analyzer` | `4bf4ba2bdb5af44c002013ef26ca9d65aab696228dfbb22b305708bd8b3e699f` | Old build, deliberately untouched |
| `ps2_recomp` (`$W/P1/bin` and `/tmp` build) | `7654e7fe4a7316476dfcc00a418c850bd8ecffeb301b345624500304e22e826f` | Unchanged since P2 (both paths agree) |
| `/tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner` (boot 1) | `43aba129a36e4c1626463175f86f52f5d68053e05d93e0898d57e0051cf95314` | Regen runner sources on `f2149e7` tree (replaces `f4d16b98`) |
| `PS2Recomp` branch `ssx3` HEAD | `f2149e7` (`Analyzer: fold LUI low half …`) | Pushed `fork ssx3` (`6046260..f2149e7`); worktree keeps only the pre-existing local `M ps2xRuntime/src/runner/register_functions.cpp`, never added |
| This report | `[P1h]` commit on `/Users/bradrichardson/dev/ssx3` (trailers; local only — no push there per the push rule) | Sole ssx3-repo commit of this brief; no `runner/`, log, or `._*` file added |

## P9-5. Exact commands

```
cat /tmp/ssx3-host-lease   (M5 at start; absent 21:21; P1h 21:26–21:40; removed at end)
python3 /tmp/p1h-scan.py   (273-TOML-pc low-half scan: 245× ORI, 0 ADDIU, 0 other)
python3 /tmp/p1h-scanall.py   (broad .text scan, context only)
python3 /tmp/p1h-dump4.py   (hand words for the 4 no-writer pcs)
(edit_file) ps2xAnalyzer/src/elf_analyzer.cpp (+28 low-half fold)
cmake --build /tmp/p1-link/tools --target ps2_analyzer -j4; shasum -a 256 (900660c9…)
git -C <fork> add ps2xAnalyzer/src/elf_analyzer.cpp; commit -m "Analyzer: ..." (trailers); show --stat; push fork ssx3   (f2149e7)
cp -X $W/P1/ssx3.toml $W/P1/ssx3.toml.p1h-orig
cd $W/P1 && /tmp/p1-link/tools/ps2xAnalyzer/ps2_analyzer SLUS_207.72 ssx3.toml.p1h-new | tee analyzer-p1h.log   (exit 0)
diff ssx3.toml.p1-orig ssx3.toml.p1h-new   (494 lines, all [mmio])
python3 TOML delta re-apply (sweep csv + ret0) → ssx3.toml; diff vs p1h-orig (mmio only)
cd $W/P1 && ./bin/ps2_recomp ssx3.toml | tee recomp-p1h.log   (exit 0; counts = P1d-sweep)
python3 /tmp/p1h-verify.py   (new-rule hand model vs 273 new targets: 0 mismatches)
diff -rq $W/P1/output <runner>   (57 files; 263+/263-, all MMIO-constant lines)
cp -X $W/P1/output/*.{cpp,h} → ps2xRuntime/src/runner/; sidecar purges; diff -rq clean
cmake --build /tmp/p1-link/runtime --target ps2EntryRunner -j4; shasum -a 256 (43aba129…)
printf 'P1h\n' > /tmp/ssx3-host-lease   (absent before)
python3 /tmp/p1h-boot1.py   (CWD $W/P1/run, PS2X_CD_IMAGE + PS2X_DIAG_PERIOD_MS=5000, stdbuf -o0 -e0, log direct to boot-p1h-1.log, foreground 180 s, SIGTERM)
log reads: grep/awk/python3 on the closed boot-p1h-1.log only (never piped while running)
reads (no edits): ps2_memory.cpp:780-825,941-999; ps2_memory.h:48-49; ps2_runtime_macros.h:344-348; output/sub_00375A08_0x375a08.cpp:2100-2159
git -C /Users/bradrichardson/dev/ssx3 add -f local/research/P1/REPORT.md; commit -m "[P1h] ..." (trailers; NO push there)
git -C <fork> push fork ssx3   (up-to-date check; the only push allowed)
rm /tmp/ssx3-host-lease (verified absent)
find <dir> -name '._*' -delete (after every edit/copy)
```

## P9-6. What I could not do

- No `p1h-waits.log`: no waits occurred (M5's start-of-session lease was gone by 21:21; the lease was absent when the boot was ready, so no poll loop ran).
- Block-0's 4 unprinted syscall ids (`distinct=24`, top-20 cap) still unrecovered — same gap as P8.
- 263 changed emission lines vs 245 changed TOML entries: 16 MMIO pcs are emitted twice across overlapping sweep outputs (346 MMIO code lines from 273 pcs both sides); recorded, not chased.
- The new `0x375d10` GS-CSR park is recorded only (thread table + loop + read path); the CSR value and exit condition were not pursued — brief says stop, no further fix.
- `$W/P1/bin/ps2_analyzer` was left at the old build (the fixed analyzer ran from `/tmp/p1-link/tools`); `$W/P1/output/` vs `runner/` are identical post-refresh.
- Sibling LUI-only scans (`analysis_passes.cpp:63-72` self-modifying signal) were left untouched — out of brief scope.
- Time box: about 35 min of the 4 h box used.

---

# P1i report — Part 10 (brief local/muse/prompts/P1i.md)

Run wall: 2026-09-18 21:40 → 21:50 EDT (Fri). `W` = `/Volumes/Extreme SSD/ps2recomp-spike`.
No verdicts. Step 1 answered from the closed `boot-p1h-1.log` + ELF + sources;
Step 2 skipped (no boot, no lease action). No runtime fix per the brief.

## P10-0. Lease record

| Event | Value |
|---|---|
| Checks | `/tmp/ssx3-host-lease` read `M6` (foreign) at the Step-1 start and end checks; never written, never removed |
| Steps 1–3 | No lease (reads only; Step 2 skipped so no boot needed one) |
| Foreign waits | None; no poll loop ran, no `$W/P1/run/p1i-waits.log` exists |
| `adb` | Not used |
| End | Lease untouched (`M6` still holds it); nothing of mine to release |

## P10-1. Park diagnosis (Step 1, no lease, no boot)

### a. CSR-bit table (bits 15:14 and `0x4000`)

| Bit(s) | In-tree meaning | Cite |
|---|---|---|
| 0 | SIGNAL: set by SIGNAL-reg write; guest write-one-to-clear | `ps2_memory.cpp:100-101` (W1C comment); `gs_frontend.cpp:1462-1471`; `gs_types.h:98` (`GS_REG_SIGNAL = 0x60`); `ps2_gs_tests.cpp:2105,2110` (`CSR.SIGNAL`) |
| 1 | FINISH: set by FINISH-reg write; guest write-one-to-clear | `ps2_memory.cpp:100-101`; `gs_frontend.cpp:1475-1483`; `gs_types.h:99` (`GS_REG_FINISH = 0x61`); `ps2_gs_tests.cpp:2106,2114` (`CSR.FINISH`) |
| 13 (`0x2000`) | FIELD: set on odd vsync tick, cleared on even tick | `ps2_memory.cpp:106` ("vsync worker (FIELD bit)"); `EeScheduler.cpp:2154-2161` |
| 15:14 (`0xC000`) | No name in tree | `0xC000`/`0xc000`: 0 hits in `ps2xRuntime/src/lib` + `ps2xRuntime/include` + `ps2xRecomp` + `ps2xAnalyzer` (only KSEG2/`0xC0000000` and COP0-EntryHi hits); `REV`/`ID`/`FIFO`/`NFIELD`: 0 hits in `gs/` + `ps2_memory.*` + `EeScheduler.cpp`; ssx3 docs name CSR only in `docs/numbers-ledger.md:84`, `docs/todo.md:14-15,36` (no layout) |
| `0x4000` (bit 14 set, bit 15 clear) | Unnamed in tree; it is the game's exit state, not a runtime constant | ELF `0x375d08` `addiu $a0,$zero,0x4000` vs `0x375d14` `andi $v0,$v0,0xC000` (words tabled in §c) |

### b. Producer table (every `gs_regs.csr` writer — exhaustive `csr` grep over `ps2xRuntime/src/lib` + `ps2xRuntime/include`)

| # | Site | Op / bits | Condition | Fired in boot-p1h-1? |
|---|---|---|---|---|
| 1 | `ps2_memory.cpp:363` `gs_regs.csr.store(0)` | all bits → 0 | `PS2Memory` init (after `memset`, `:360-363`) | Yes: boot reached execution (`Starting execution at address 0x100008`) |
| 2 | `EeScheduler.cpp:2156` `fetch_or(0x2000)` | bit 13 set | `processEvent(VBlankStart)`, odd `m_vsyncTick` | Pump live (row below); no log line or counter records firings (0 `vsync`/`vblank`/`VSync` lines in 1298); effect outside the `0xC000` mask in all cases |
| 3 | `EeScheduler.cpp:2160` `fetch_and(~0x2000)` | bit 13 clear | `processEvent(VBlankStart)`, even `m_vsyncTick` | Same as #2 |
| 4 | `gs_frontend.cpp:1471` `fetch_or(0x1)` | bit 0 set | `writeRegister(GS_REG_SIGNAL)`: GIF packets (`:709`,`:766`) or GS HLE stubs (`GS.cpp:117-122`,`:782`,`:1165-1208` via `Support.h:1893-1900`) | No: 0 `gif` lines whole log; 30 distinct `[diag:stub]` targets whole log, 0 at the 3 sceGs addrs (`0x3FD910`/`0x3FDAB0`/`0x3FDB18`, `ssx3.toml:24-26`); clear path writes testa/prim/rgbaq/xyz/test only |
| 5 | `gs_frontend.cpp:1483` `fetch_or(0x2)` | bit 1 set | `writeRegister(GS_REG_FINISH)`, same callers as #4 | No: same evidence as #4 |
| 6 | `ps2_memory.cpp:956` `writeCsrHalf` ← `write32` | guest merge (bits ≥2 plain, bits 0–1 W1C; `:108-128`) | guest store to `0x12001000` | Unobservable (CSR write paths emit no log); park loop body contains no store (gen `:2119-2156`); 35-block stable park proves masked value ≠ `0x4000` at every dump |
| 7 | `ps2_memory.cpp:1015` `writeCsrFull` ← `write64` | guest merge (bits ≥2 plain, bits 0–1 W1C; `:132-141`) | guest store to `0x12001000` | Same as #6 |
| 8 | `ps2_memory.cpp:1150` `writeCsrHalf` ← `writeIORegister` | same merge | direct callers only (`:1141-1143`: unreachable from `write8/16/32/64`) | No caller in this boot (dead path) |

Vsync worker / present path / timer paths (brief coverage):

| Path | CSR writes | Wiring + boot evidence |
|---|---|---|
| Vsync worker | Bit 13 only (#2–#3 above) | Pump: `run()` `:242,575` → `processPendingEvents` (`:2025`) → `processDueDeadlines` (`:2059`; due = cycle + host deadlines, `:2096-2099`) → `VBlankStart` (`:2151`; seeded at reset `:223-225`, 16667 µs; reseeded `:2130-2137`); `m_eeCycle` advances via `checkpointDue`→`accountCycles` (`:617-618`,`:650-659`), and the spin itself calls `eeCheckpointDue` each iteration (gen `:2151-2153`) |
| Present path | None (`csr`: 0 refs in `gs_cpu_backend.cpp`; frontend present `:506-578` reads pmode/dispfb/vsyncTick, not csr) | Host tick `UploadFrame` (`ps2_runtime.cpp:378-397`) latches on vsync-tick change; log: 0 present/game-frame lines (sole `frame` hit = raylib target-time line) |
| Timer paths | None (exhaustive grep) | `accountCycles :654` → `advanceEeTimers` (`ps2_memory.cpp:407`) → `dispatchIrq(9+t)` (`:2027-2034`); log: 0 `timer`/`Timer`/`interrupt`/`Interrupt` lines |
| Frontend↔memory wiring | (not a writer; proves #4–#5 land in the read atomic) | `m_gs.init(…, &m_memory.gs())` (`ps2_runtime.cpp:626`); `GS::init` stores `m_privRegs` (`gs_frontend.cpp:114-123`) |

P4 §5 candidate-producer context (skimmed, not prescription):

| Row | Mechanism | CSR relevance |
|---|---|---|
| S4 | Empty-transfer completion (TheTharin `7f29bbd`, DMAC STR rule) | None: touches CHCR.STR/`queueCompletedDmacCause`, not CSR; its rung (VIF0 park) is past |
| S12 | EE-timer HLE (phmdacosta `e465b4d`) | None: delivers causes 9–12 via `dispatchIrq`; our `advanceEeTimers` likewise CSR-free |
| S17 | Guest tick-function pump pattern (bt3 `4b8a766`) | None: park is a CSR-value spin, not an undriven guest queue |

### c. Consumer routing (`0x375d10 ld`)

| Item | Value |
|---|---|
| `0x375d10` in `[mmio]`? | No: 0 hits for `375d`/`375D` in `ssx3.toml` (`[mmio]` §`:607`, 273 entries) |
| Generated line | `output/sub_00375A08_0x375a08.cpp:2122`: `SET_GPR_U64(ctx, 2, READ64(ADD32(GPR_U32(ctx, 3), 0)));` — address computed from `$v1` (built `:2110` `lui` + `:2118` `ori` → `0x12001000`); no baked constant; runner copy identical (`diff -q`) |
| Routing | `READ64` (`ps2_runtime_macros.h:344-348`) → `isSpecialAddress` true (GS range, `ps2_address.h:43-48`; `ps2_runtime.h:442-445`) → `Load64` → `m_memory.read64` (`ps2_runtime.cpp:2270-2273`) → `isGsPrivReg` (`ps2_memory.cpp:39-42`) → `kGsCsrRegOffset` (`:100`) → `gs_regs.csr.load()` (`:789-795`, load at `:792`) |
| Base cites | `PS2_GS_BASE 0x12000000` (`ps2_memory.h:48`); `PS2_GS_PRIV_REG_BASE/SIZE 0x12000000/0x2000` (`:49-50`); `csr` decl (`:208`); sibling loads: `read32 :745`, direct-caller `read :2194` |

ELF words (file off `0x1000+(va-0x100000)`, `SLUS_207.72`), confirming the P9-3 decode:

| va | word | disasm |
|---|---|---|
| `0x375d04` | `0x3c031200` | `lui $v1,0x1200` |
| `0x375d08` | `0x24044000` | `addiu $a0,$zero,0x4000` |
| `0x375d0c` | `0x34631000` | `ori $v1,$v1,0x1000` |
| `0x375d10` | `0xdc620000` | `ld $v0,0($v1)` — park head |
| `0x375d14` | `0x3042c000` | `andi $v0,$v0,0xC000` |
| `0x375d18` | `0x00000000` | `nop` |
| `0x375d1c` | `0x00000000` | `nop` |
| `0x375d20` | `0x00000000` | `nop` |
| `0x375d24` | `0x1444fffa` | `bne $v0,$a0→0x375d10` |
| `0x375d28` | `0x00000000` | delay-slot `nop` |

### d. Missing producer (Step 1d)

| Question | Answer (exact lines/words) |
|---|---|
| Exit requirement | `(CSR&0xC000)==0x4000`, i.e. bit 14 = 1 and bit 15 = 0 (ELF `0x375d14` + `0x375d08`/`0x375d24`) |
| Runtime writers to bit 14 | None (producer table §b: bits touched = {0, 1, 13} + init-0 + guest merge) |
| Runtime writers to bit 15 | None (same table) |
| Init value | `0` (`ps2_memory.cpp:363`) |
| Only in-tree path that could set bit 14 | A guest CSR store with bit 14 = 1 / bit 15 = 0 (plain merge for bits ≥2, `ps2_memory.cpp:108-141`); the loop performs no store |
| Log receipt that it never held | `id=1 pc=0x375d10` in 35/35 blocks, no other value (`grep -c` on `[diag:thread] id=1`); park-caller return via `0x375a94` and `sp=0x1fffd90` per P9-3 |
| Step 2 | Skipped: the closed log + ELF + sources answer; no missing receipt |

## P10-2. Ladder delta vs boot-p1h-1 (Step 2 skipped — no new boot)

| Rung | boot-p1h-1 (P9-3) | boot-p1i-1 | Delta |
|---|---|---|---|
| Thread-1 pc | `0x375d10` all 35 blocks | Not run | None (no new ladder) |
| First new syscall ids | None | Not run | None |
| First VIF MPG/MSCAL | None | Not run | None |
| First GIF kick | None | Not run | None |
| First presented frame | None | Not run | None |
| Crash | None | Not run | None |

## P10-3. Binaries and commits

| Binary / ref | sha256 / sha | Sources / state |
|---|---|---|
| `/tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner` (read-only `shasum`, no rebuild) | `43aba129a36e4c1626463175f86f52f5d68053e05d93e0898d57e0051cf95314` | Identical to the boot-p1h-1 binary; not stale (no source change since `f2149e7`) |
| `PS2Recomp` branch `ssx3` HEAD | `f2149e7` (unchanged) | No fork commit (diagnose-only); worktree keeps only the pre-existing local `M ps2xRuntime/src/runner/register_functions.cpp`, never added |
| This report | `[P1i]` commit on `/Users/bradrichardson/dev/ssx3` (trailer; local only — no push there per the push rule) | Sole ssx3-repo change of this brief; no `runner/`, log, or `._*` file added |
| Push | `git push fork ssx3` from the fork clone only (up-to-date check; the only push allowed) | No push in `/Users/bradrichardson/dev/ssx3` |

## P10-4. Exact commands

```
cat /tmp/ssx3-host-lease   (M6 foreign at start and end; never written/removed)
grep -n "375d|375D" $W/P1/ssx3.toml   (0 hits); awk [mmio] count (273)
grep -rn "csr" <fork>/ps2xRuntime/src/lib <fork>/ps2xRuntime/include   (exhaustive writer/load table)
grep -rn -i "REV|HSINT|VSINT|NFIELD|EDWINT|..." gs+include   (layout search, ~0 hits)
grep -rn "0xC000|0xc000" src/lib include ps2xRecomp ps2xAnalyzer   (0 relevant hits)
sed -n reads: ps2_memory.cpp:39-42,80-145,350-370,735-800,935-1020,1140-1160,2180-2198
sed -n reads: EeScheduler.cpp:188-228,605-660,1990-2180,2340-2355; ee_scheduler.h:420
sed -n reads: gs_frontend.cpp:108-125,1440-1500; gs_types.h:95-100; GS.cpp:110-125,775-800,1160-1210
sed -n reads: ps2_runtime.cpp:378-400,620-630,2270-2290; ps2_memory.h:40-60,190-230
sed -n reads: ps2_runtime_macros.h:340-352; ps2_runtime.h:438-445; ps2_address.h:1-60
sed -n reads: ps2_gs_tests.cpp:420-430,2095-2115; ps2_runtime_interrupt_tests.cpp:120-200
python3 ELF words 0x375d04-0x375d28 (file off 0x1000+(va-0x100000))
grep -n "375d10|..." output/sub_00375A08_0x375a08.cpp; diff -q output/ runner/ (identical)
log: wc -l (1298); keyword counts (vsync/vblank/VSync/gs:/present/csr/gif/vif/timer/interrupt/callback/dispatch = 0; frame = 1)
log: grep -o target=... sort -u (30 distinct); sceGs targets grep -c (0)
log: id=1 pc values (35x 0x375d10); tail -45 block 34; diag prefix census
grep -rn "csr" ps2xTest/src (tests); grep -rn "0x12001000|12001000" src/lib include README (0 hits)
grep -rli "csr" /Users/bradrichardson/dev/ssx3/docs (numbers-ledger.md, todo.md only)
shasum -a 256 /tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner (43aba129..., read-only)
git -C /Users/bradrichardson/dev/ssx3 add -f local/research/P1/REPORT.md; commit -m "[P1i] ..." (trailer; NO push there)
git -C <fork> push fork ssx3   (up-to-date check; the only push allowed)
find <dir> -name '._*' -delete (after every edit/copy; nothing created this session)
```

## P10-5. What I could not do

- Bits 15:14 have no in-tree meaning to report: no runtime comment, test, or doc names them, so per the brief's no-guess rule the hardware meaning is recorded as unidentified-from-tree (the diagnosis does not need it: no writer sets bit 14 regardless of its name).
- VBlankStart firings are uncounted: this build emits no vsync-marked log line and keeps no exposed vsync counter (only the silent `m_vsyncTick`/`vsyncTick` stores at `EeScheduler.cpp:2152-2153`).
- Guest CSR stores are unobservable: all three CSR write paths (`:956`,`:1015`,`:1150`) emit no log line; only the loop's read-only body + the stable park bound them.
- No boot was run and no `/tmp/p1-link` file was written; `$W/P1/run/boot-p1i-1.log` does not exist (Step 2 skipped by the brief's own gate).
- P4 S4/S12/S17 were skimmed as context only; none was applied or verified by boot (out of brief scope).
- Time box: about 10 min of the 2 h box used.

## Part 11 (P1j): CSR bits 15:14 identified as FIFO; exit state produced; thread 1 past `0x375d24`

## P11-0. Lease record

| Event | Value |
|---|---|
| Lease at session start | Absent (`cat /tmp/ssx3-host-lease`: no such file) |
| Claim | `printf 'P1j\n' > /tmp/ssx3-host-lease`, after pre-boot checks, before boot-p1j-1 |
| Foreign holder seen | None this session (no poll loop ran) |
| Waits log | `$W/P1/run/p1j-waits.log` does not exist (no waits) |
| Release | `rm -f /tmp/ssx3-host-lease` immediately after boot-p1j-1 SIGTERM; verified absent |
| Stray runner check | `pgrep ps2EntryRunner` exit 1 (none) before claiming |

## P11-1. Bit table, producer, cheat row

### a. Bits 15:14 from public sources (Step 1, no code)

| Bit | Name | Set-by | Cleared-by | Reset value | Exact cite |
|---|---|---|---|---|---|
| 14 | FIFO bit 0 (LSB of 2-bit GS FIFO status; read-only) | GIF-path FIFO occupancy reaching empty (field value `01`); DobieStation: drained path queue + FINISH assert, GIF reset, path-deactivation stall | FIFO leaving empty (data arriving / FQC > 0 drives `00`/`10`); DobieStation: `feed_GIF` on new tag data | `1` (field `01` = empty) | DobieStation `src/core/gsregisters.cpp:319` (`FIFO_status << 14`), `:428` (`= 0x1; //Empty` in `GS_REGISTERS::reset`), `src/core/gif.cpp:33` (reset), `:253` (`0x2 //FIFO Full`), `:295` (`0x1 //FIFO Empty`), `:410`; `src/core/gs.cpp:105-108` (`set_CSR_FIFO`) |
| 15 | FIFO bit 1 (MSB of 2-bit GS FIFO status; read-only) | FIFO reaching almost-full (field value `10`); PCSX2: GIF STAT FQC ≥ 15 | FIFO draining below almost-full; PCSX2: FQC = 0 → empty, else normal | `0` (field `01` = empty) | PCSX2 `pcsx2/GS.h:16-22` (`CSR_FifoState`: 0 normal / 1 empty / 2 full / 3 reserved), `:106-113` (FIFO field doc), `:140-146` (`tGS_CSR::Reset`: FIFO = EMPTY, REV `0x1B`, ID `0x55`); `pcsx2/Gif.cpp:30-51` (`clearFIFOstuff`, `CalculateFIFOCSR`), `pcsx2/Gif_Unit.h:576`; layout `pcsx2/GS/GSRegs.h:300` (`rFIFO : 2`) |

Field-value cross-checks (online, URL + section):

| Source | Section | Values |
|---|---|---|
| `https://github.com/ps2dev/gsKit` `ee/gs/include/gsInit.h`, `struct gsRegisters` | `u64 FIFO: 2 /* ro */` after NFIELD:1 (bit 12) + FIELD:1 (bit 13); `GS_CSR` at `0x12001000` | Layout only (no value semantics in header) |
| `https://github.com/jpd002/Play-` `Source/gs/GSHandler.h`, `CGSHandler` CSR enum | `CSR_FIFO_STATUS = 0xC000`, `CSR_FIFO_NEITHER = 0x0000`, `CSR_FIFO_EMPTY = 0x4000`, `CSR_FIFO_FULL = 0x8000` | `00` neither / `01` empty / `10` full; reset `Source/gs/GSHandler.cpp:166` (`ResetBase`: `m_nCSR = CSR_FIFO_EMPTY \| REV << 16`, `GS_REVISION 7`) |

Hardware event sequence producing `0x4000`: reset (all four sources reset the field to `01`), or GIF FIFO drained to empty (FQC = 0 / path queue drained). No vsync, FIELD, or FINISH involvement: FIFO is GIF-occupancy only. Every cell above is cited; nothing marked open.

### b. Producer (Step 2, one commit)

Lifecycle point: init value (not vsync worker, not finish-event path). Why from Step 1: all sources set FIFO = empty at reset; the dynamic producer (GIF-path occupancy) is a whole unbuilt subsystem in this runtime (0 `gif` lines in every boot log; no GIF FIFO exists). So the minimal producer is the reset value, guarded against guest clobbering because the game provably writes CSR with `00` in bits 15:14 (writer table below) and FIFO is read-only on hardware (gsKit `/* ro */`, PCSX2 "read-only", DobieStation: no CSR-write path touches `FIFO_status`).

Static guest CSR writers (from `$W/P1/output` MIPS comments; all target `0x12001000`):

| va | Insn | Value written | Bits 15:14 | Effect on plain merge |
|---|---|---|---|---|
| `0x2ec6cc` | `sd $v0,0($s0)`, `$v0`=2 | `2` (FINISH) | `00` | Clears exit state |
| `0x2ec728` | `sd $v1,0($v0)`, `$v1`=2 | `2` (FINISH) | `00` | Clears exit state |
| `0x37c0dc` | `sd $a0,0($v0)`, `$a0`=8 | `8` (VSINT) | `00` | Clears exit state |
| `0x382c5c` | `sd $a0,0($v0)`, `$a0`=8 | `8` (VSINT) | `00` | Clears exit state |

FIFO-wait sites sharing the `(CSR&0xC000)==0x4000` idiom (`lui 0x1200` + `ori 0x1000` + `ld` + `andi 0xC000` + compare `0x4000`): `0x2ec694`, `0x2ec82c` (sub_002EC418), `0x375d04` (sub_00375A08, thread-1 park), `0x3828d4`, `0x3829c4`, `0x382a8c` (sub_00382760), `0x382c24` (sub_00382AF0).

Producer diff (commit `8fad69e`, 2 files, `+43/-7`):

| File:lines | Change |
|---|---|
| `ps2xRuntime/src/lib/ps2_memory.cpp:102-121` | Comment (Step 1 cites + HLE note) + `kGsCsrFifoMask 0xC000` + `kGsCsrFifoEmpty 0x4000` |
| `ps2_memory.cpp:141-142` | `writeCsrHalf` low dword: force `(desired & ~mask) \| 0x4000` after W1C |
| `ps2_memory.cpp:163-164` | `writeCsrFull`: same force after W1C |
| `ps2_memory.cpp:387-388` | Init: `gs_regs.csr.store(kGsCsrFifoEmpty)` instead of `store(0)` |
| `ps2xTest/src/ps2_gs_tests.cpp:425-446` | Round-trip expectations updated for read-only FIFO (contract change, see row below) + init-`0x4000` + `write64(8)→0x4008` + `write64(2)→0x4000` assertions |

Cheat row:

| What was faked | What would replace it |
|---|---|
| FIFO occupancy hard-wired EMPTY: constant at init, guest writes to bits 15:14 ignored (documented in code comment at `ps2_memory.cpp:102-117`) | GIF-path/FIFO occupancy tracking that sets EMPTY/FULL/NORMAL from transfer state (cf. PCSX2 `CalculateFIFOCSR` from GIF STAT FQC; DobieStation `feed_GIF`/path-queue drain) |

Contract-change decision (test update, not a silent rewrite): the old test asserted plain-RAM round-trip of all CSR bits, which contradicts all four hardware sources (FIFO is read-only) and is incompatible with the game's proven CSR writes carrying `00` in bits 15:14 — no producer satisfying both the old test and the game exists (read-path OR, worker re-assert, and preserve-old all break the old exact-match or the exit state). Expectation deltas: `write64(pat)→0xA1B2C3D4E5F64718` (was `...0718`), `read32 lo→0xE5F64718`, `write32 lo→0xA1B2C3D411227344`, `write32 hi→0x5566778811227344`. FIELD/vsync tests untouched (they assert bit 13 only).

### c. Test receipts

| Run | Total | Passed | Failed |
|---|---|---|---|
| With fix (`ps2x_tests` rebuilt from `8fad69e` tree) | 425 | 424 | 1: `sceGsSyncVCallback runs as a scheduler invocation on its callback stack` (`callback invocation should use the reserved async stack pool`, `ps2_gs_tests.cpp:4041`) |
| At unmodified HEAD `f2149e7` (fix stashed, rebuilt) | 425 | 424 | Same single test, same assertion |

The failing test asserts callback SP placement in the reserved async stack pool; it does not touch CSR. Identical failure with and without the fix.

## P11-2. Boot ladder (boot-p1j-1 vs boot-p1h-1)

Boot 1: `$W/P1/run/boot-p1j-1.log`, 1789 lines, 173100 B, 35 period blocks, CWD `$W/P1/run`, env `PS2X_CD_IMAGE` + `PS2X_DIAG_PERIOD_MS=5000`, no `WATCH`/`REPORT_ALL`, foreground 180 s, SIGTERM, binary `e5f81397...`.

| Rung | boot-p1h-1 (P9-3/P10-2) | boot-p1j-1 | Delta |
|---|---|---|---|
| Thread-1 pc | `0x375d10` all 35 blocks | `0x3e5980` ×31, `0x423c90` ×2, `0x3dd278` ×2; 0 hits at `0x375d10` | Past `0x375d24` |
| First new syscall ids | None | `0x15` (count 4, caller `0x423af8`), `0x17` (count 1, caller `0x423b18`) | 2 new ids |
| First VIF MPG/MSCAL | None | None (0 `vif` lines) | None |
| First GIF kick | None | None (0 `gif` lines) | None |
| First presented frame | None | None (sole `frame` hit = raylib target-time line) | None |
| Crash | None | None (0 `crash`/`FATAL`/`assert` lines) | None |
| Missing targets | 0 lines | 1 line (log:146): `[guest-branch:missing-target] kind=IndirectCall op=JALR source=0x3760d0 target=0x395cf0 pc=0x395cf0 ra=0x3760d8 sp=0x1fffd90` (+ register/memory readability fields verbatim in log) | 1 new |
| Distinct stub targets | 30 | 31 (8 new: `0x31ad20`, `0x3825f8`, `0x395cf0`, `0x3e33b0`, `0x3e5440`, `0x3e5928`, `0x411c38`, `0x423c90`; 7 from h absent) | Net +1 |
| CD callback | None | First queued+start: log:149-150 `[cd:callback] queued func=1 cb=0x3e3ad8`, `start func=1 cb=0x3e3ad8` | New |
| Threads | 4 (ids 1-4) | 5 (new id=5: status=2 waitReason=2 waitId=30 pc=`0x423de8` entry=`0x382740` stack `0x621540`/`0x1000` sp `0x622480`) | +1 thread |

New park, recorded only (thread table + loop). Thread table, block 0 (representative; ids 2/4/5 at `0x423de8` all 35 blocks, id 3 at `0x31ac60` all 35):

```
[diag:thread] id=1 status=0 waitReason=0 waitId=0 pc=0x3e5980 entry=0x100008 priority=100 scheduled=283
[diag:thread] id=2 status=2 waitReason=2 waitId=26 pc=0x423de8 entry=0x3e3be0 priority=12 scheduled=2
[diag:thread] id=3 status=1 waitReason=0 waitId=0 pc=0x31ac60 entry=0x31ac60 priority=101 scheduled=0
[diag:thread] id=4 status=2 waitReason=2 waitId=29 pc=0x423de8 entry=0x31ac08 priority=99 scheduled=259
[diag:thread] id=5 status=2 waitReason=2 waitId=30 pc=0x423de8 entry=0x382740 priority=5 scheduled=1
```

Thread-1 stack at park: `[diag:stacks] block=0 thread id=1 stack=0x1fe0000 stackSize=0x20000 sp=0x1fffd80 entry=0x100008 pc=0x3e5980`. Scheduled counts stay ~300/block (spinning, not blocked).

Loop: `0x3e5980` is inside sub_003E5928 (`0x3e5928-0x3e5a78`, `ssx3-functions.csv`), a 16-slot dispatch loop (`$s1` from `0xF`, `$s0 += 0x10`, back edge `0x3e59dc: bgez $s1 → 0x3e5980`):

```
0x3e5980: lw   $a2, -0xC($s0)     # loop head: load slot fn pointer (park pc)
0x3e5984: beql $a2, $zero → 0x3e59dc
0x3e598c: lw   $v0, 0xDD0($s6)
0x3e5990: lw   $v1, -0x4($s0)
0x3e5994: slt  $v0, $v0, $v1
0x3e5998: bnel $v0, $zero → 0x3e59dc
0x3e59a0: lw   $v0, 0x0($s0)
0x3e59a4: bnel $v0, $zero → 0x3e59dc
0x3e59b8: jalr $a2                # indirect call; ra=0x3e59c0 matches stub firstRa
0x3e59c0: or   $s2, $s2, $v0
0x3e59d8: addiu $s1, $s1, -0x1
0x3e59dc: bgez $s1 → 0x3e5980     # (delay slot: addiu $s0, $s0, 0x10)
```

Mid driver in sub_003DD1D8 (`0x3dd1d8-0x3dd310`):

```
0x3dd278: jal  func_3E5440        # stub 0x3e5440 count=2369599 firstRa=0x3dd280
0x3dd280: beqz $v0 → +5
0x3dd288: jal  func_3E5928        # stub 0x3e5928 count=2369619 firstRa=0x3dd290
0x3dd290: b    → +4
```

Stub `0x423c90` count=2369833 (firstRa `0x3e5028`, lastRa `0x3e5454`) matches the same ~2.3M-iteration outer spin. sub_003DD1D8 itself returns (`0x3dd308: jr $ra`); its spinning caller is not identified (many `jal func_3DD1D8` sites; recorded open, no fix per brief).

## P11-3. Binaries and commits

| Binary / ref | sha256 / sha | Sources / state |
|---|---|---|
| `/tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner` (boot-p1j-1 binary) | `e5f8139772efe522aeb344e59692fecf04b175d0e695838bc714e134fcdbc1ca` | Rebuilt from `8fad69e` tree (`ninja: no work to do` at boot time) |
| `PS2Recomp` branch `ssx3` HEAD | `8fad69e` (`GS: hard-wire CSR FIFO bits to EMPTY ...`, 2 files `+43/-7`, two trailers) | Pushed `fork ssx3` (`f2149e7..8fad69e`); worktree keeps only the pre-existing local `M ps2xRuntime/src/runner/register_functions.cpp`, never added |
| HEAD-baseline test binary | Same path, rebuilt from stashed (unmodified `f2149e7`) tree, then rebuilt again after pop | 424/425 with the identical single failure (receipt for pre-existing status) |
| This report | `[P1j]` commit on `/Users/bradrichardson/dev/ssx3` (trailers; local only — no push there per the push rule) | Sole ssx3-repo change of this brief; no `runner/`, log, or `._*` file added |
| Push | `git push fork ssx3` from the fork clone only | No push in `/Users/bradrichardson/dev/ssx3` |

## P11-4. Exact commands

```
cat /tmp/ssx3-host-lease   (absent at start; claimed P1j pre-boot; removed post-boot; verified absent)
grep -rn -i "csr" dobiestation src (layout search) ; sed reads gsregisters.hpp:100-170, gsregisters.cpp:169-271,300-330,420-450, gs.cpp:60-140, gif.cpp:20-45,240-300,395-415
grep -rn "set_CSR_FIFO" dobiestation src (4 GIF writers + decl)
grep -rn -i "csr|fifo" pcsx2-ref/pcsx2/GS/GSRegs.h ; sed GSRegs.h:270-340 ; grep -rn CSR pcsx2/GS (read/write paths) ; sed GSState.cpp:100-130,151-230 GS.cpp:395-415 GSState.h:510-530
grep -rn NFIELD pcsx2 tree ; sed pcsx2/GS.h:1-200 (CSR_FifoState, tGS_CSR, Reset) ; sed pcsx2/Gif.cpp:1-70 Gif_Unit.h:565-585 ; grep -rn clearFIFOstuff|CalculateFIFOCSR pcsx2 (8 call sites)
web: ps2dev/gsKit ee/gs/include/gsInit.h (struct gsRegisters, GS_CSR 0x12001000) ; jpd002/Play- Source/gs/GSHandler.h (CSR_FIFO_*) + GSHandler.cpp (ResetBase:166) ; israpps/ps2tek PS2/GS listing (no CSR page)
grep -rn "lui.*0x1200" $W/P1/output (10 files) ; per-site MIPS dump (guest CSR writers + FIFO-wait idiom table)
grep -rn -i csr fork ps2xTest/src (impact) ; sed ps2_runtime_interrupt_tests.cpp:150-175,425-470 ps2_gs_tests.cpp:410-436,4041-4110
4 sequential muse.edit_file on ps2_memory.cpp (constants, half-merge, full-merge, init) ; 1 on ps2_gs_tests.cpp (expectations + regress shapes)
find <lib|test src> -name '._*' -delete (after edits)
cmake --build /tmp/p1-link/runtime --target ps2EntryRunner ps2x_tests -j4 (one mid-session corruption from parallel same-file edits: restored via git checkout, re-applied sequentially, verified 4 hunks + intact tail)
ps2x_tests full run (425/424-1) ; stash push 2 files + rebuild + run at HEAD (same 425/424-1) ; stash pop + rebuild both targets + re-run (425/424-1)
git -C fork add <2 files only> ; commit -m "GS: ..." (trailers) ; push fork ssx3 (f2149e7..8fad69e)
sed /tmp/p1h-boot1.py -> /tmp/p1j-boot1.py (LOG=boot-p1j-1.log) ; pgrep ps2EntryRunner (none) ; printf P1j lease ; cmake --build (no-op) ; shasum runner (e5f81397...)
python3 /tmp/p1j-boot1.py (foreground 180 s, SIGTERM, 173100 B) ; rm lease
log: wc -l (1789); thread-pc census (id=1: 31x 0x3e5980, 2x 0x423c90, 2x 0x3dd278); keyword counts j-vs-h; target= comm (8 new, 7 gone); syscall id= comm (0x15, 0x17 new); missing-target (1, log:146); cd:callback (log:149-150)
ssx3-functions.csv + output/sub_003E5928 + sub_003DD1D8 reads (park loop + driver + back-edge search)
git -C /Users/bradrichardson/dev/ssx3 add -f local/research/P1/REPORT.md; commit -m "[P1j] ..." (trailers; NO push there)
git -C <fork> push fork ssx3 (up-to-date check; the only push allowed)
find <dir> -name '._*' -delete (after every edit/copy)
```

## P11-5. What I could not do

- GIF-occupancy-driven FIFO: the field is hard-wired EMPTY (cheat row above); a real GIF FIFO with FQC-like tracking would replace it. No in-between/almost-full state is reachable.
- REV/ID bits (16-31) left zero: DobieStation/PCSX2 use REV `0x1B` ID `0x55`, Play! uses REV 7 ("fairly arbitrary"); the game masks `0xC000` so they are irrelevant to this wait — recorded, not implemented.
- The one failing test (`sceGsSyncVCallback ... callback stack`) fails identically at unmodified HEAD; fixing it is out of this brief's scope (recorded only).
- The spinning caller of sub_003DD1D8 (outer back edge above `0x3dd278`) is unidentified: many `jal func_3DD1D8` sites exist and no RA/stack receipt names the live one. The new park is recorded, not fixed, per the brief.
- VBlankStart firings remain uncounted (no vsync-marked log line, same as P10); guest CSR stores remain log-silent (all write paths emit no line).
- Time box: about 2 h of the 4 h box used (Step 1 sources + static scan ~60 min, implement/corruption-repair/test ~40 min, boot + ladder + report ~25 min).

---

## Part 12 (P1k): 0x3e5980 dispatch-loop park diagnosed, slot fills captured, caller narrowed to 8, 0x395cf0 = unsplit leaf

Brief `local/muse/prompts/P1k.md`. Diagnose only; no runtime fix. Tables, no verdicts.
P6 names file WAS present (`local/research/P6/ssx3-decomp-names.csv`, 802 lines = header + 801 names, dated Sep 18 22:40, i.e. after boot-p1j-1): P6 names used below, `sub_*` where P6 has no row.

P6 addr→name rows cited in this Part (exact CSV text):

| addr | name |
|---|---|
| `0x3e5928` | `SYNCTASK_run` |
| `0x3e57f8` | `SYNCTASK_add` |
| `0x3e57d0` | `SYNCTASK_init` |
| `0x3e58c8` | `SYNCTASK_del` |
| `0x3e5700` | `MUTEX_lock` |
| `0x3e5760` | `MUTEX_unlock` |
| `0x31adb0` | `systemInit` |
| `0x3df9d8` | `ASYNCFILE_release` |
| `0x3dee70` | `queueadd` |
| `0x3defc0` | `releaserequest` |
| `0x3de420` | `iFILESYS_CommandCompleteCallback` |
| `0x3de4d0` | `FILESYS_bypassqueuefileinfo` |
| `0x3dddf0` | `FILESYS_atomic` |
| `0x3ddfa8` | `iFILESYS_ExecCommand` |

P6 absence (0 rows each, verified by grep): `0x395*`, `0x376*`, `0x375*`, `0x423*`, `0x382*`, `0x411*`; no row for `0x3dd1d8`, `0x3e4040`, `0x3e3020`, `0x3e3350`/`0x3e33b0`, `0x31ad18`/`0x31ad20`, `0x3e3ad8`, `0x3e3be0`, `0x31ac08`, `0x382740`, seven of the eight §P12-1 caller sites' functions.

## P12-0. Lease record

| Event | Value |
|---|---|
| Lease at session start | Absent (`cat /tmp/ssx3-host-lease`: no such file) |
| Pre-boot checks | `pgrep -f ps2EntryRunner` exit 1 (none); binary sha matches boot-p1j-1 (no rebuild, see P12-5) |
| Claim | `printf 'P1k\n' > /tmp/ssx3-host-lease` immediately before boot-p1k-1 |
| Foreign holder seen | None (no poll loop ran) |
| Waits log | `$W/P1/run/p1k-waits.log` does not exist (no waits) |
| Release | `rm -f /tmp/ssx3-host-lease` in the same command as the boot return; verified absent after |
| `adb` | Not used |
| Post-boot volume state | From ~23:05 UTC all data reads under `/Volumes/Extreme SSD/` fail with `Operation not permitted` (EPERM; `ls` metadata still works; `/Users` and `/tmp` unaffected; no stray runner — PID seen once by `pgrep` was gone on `ps`). All P12 receipts below were captured before the failure except where marked `NOT RE-CHECKED`. |

## P12-1. Park + driver + caller (Steps 1a/1b)

Park function is `SYNCTASK_run` (P6 `0x3e5928`; sweep `sub_003E5928 0x3e5928-0x3e5a78`).

### a. Slot table layout (static; init/add/del/run agree)

Base `0x51ED98` (`lui 0x52` + `-0x1268`), stride `0x10`, 16 slots. Only 4 guest files reference `-0x1268` (`sub_003E5760` init, `sub_003E57F8` add, `sub_003E58C8` del, `sub_003E5928` run); no other writer exists.

| Word | Add writes (`0x3e5898`-`0x3e58b0`) | Run reads (`$s0`=base+`0xC`+i*`0x10`) |
|---|---|---|
| `[0]` fn | `$t1`=$a0 (fn) | `-0xC($s0)` → `jalr $a2` (`0x3e59b8`) |
| `[4]` period | `$t0` ($a1, with 0→1, -1→0) | `-0x8($s0)`, added to tick after fire (`0x3e59d0`) |
| `[8]` next-tick | tick+`$a2` (tick=`*(0x450DD0)`) | `-0x4($s0)`; skip slot if tick < next (`0x3e598c`-`0x3e5998`) |
| `[C]` busy | 0 | `0x0($s0)`; skip if nonzero; set 1 before call (`0x3e59b4`), clear after (`0x3e59cc`) |

Init (`SYNCTASK_init`, `0x3e57d0`, inside sweep file `sub_003E5760`): `func_3E6448(0x51ED98, 0, 0x100)` = zero 256 B = all 16 slots. Region is BSS (ELF file covers va–`0x4A4BF4`; `0x51ED98` above it), so zero at load too.

### b. Slot values + fillers + run evidence (Step-2 WATCH receipts, boot-p1k-1)

`PS2X_DIAG_WATCH` slots 0–3 + `0x1ffe010` + `0x519c4c`; 32,077 watch lines (32,050 w4, 25 w16, 2 w8).

| Slot | fn | period | next@fill | Filled by (watch ra → static site) | Fires/5 s (p1j, `firstRa=0x3e59c0`) |
|---|---|---|---|---|---|
| 0 | `0x31ad20` | 1 | `0x27` | add `ra=0x31af60` = site `0x31af58` (`lui 0x32; addiu -0x52E0` → $a0=`0x31AD20`, $a1=0, $a2=0) in `sub_0031ADB0` = P6 `systemInit`; sp=`0x1ffff60` | ~300, 35/35 blocks |
| 1 | `0x3e33b0` | 1 | `0x27` | add `ra=0x3e3050` = site `0x3e3048` (`lui 0x3E; addiu 0x33B0` → $a0=`0x3E33B0`) in `sub_003E3020`; sp=`0x1fffe60` | ~300, 35/35 blocks |
| 0 (earlier) | `0x3e4000` | 1 | `0x27` | add `ra=0x3e4458` = site `0x3e4450` ($a0=`0x3E4000`) in `sub_003E4040`; sp=`0x1ffec80`; then `del` (`pc=0x3e591c`, `ra=0x31af4c`, the `jal SYNCTASK_del(0x3e4000)` 2 insns before site 2) zeroed slot 0, and `0x31ad20` reused it | 0 (del'd before firing; no stub line) |
| 2–15 | 0 | 0 | 0 | — (init/BSS zeros; only zero-writes observed on slots 2–3 watches; e.g. `pc=0x10012c` w16 entry-BSS clear) | 0 |

The two other static add sites never filled a watched slot in this boot: `0x2ae0b0` (fn `0x2AE020`, $a1=5, $a2=`0x64`, in `sub_002AE048`) and `0x3b54ac` (fn `0x3B5450`, in `sub_003B5478`); no stub line for either target with `firstRa=0x3e59c0` in any of 35 p1j blocks. Steady-state w4 volume (~32K lines/90 s on slot words 2–3) is consistent with per-fire busy/next updates (`0x3e59b4`/`0x3e59cc`/`0x3e59d4`); per-pc split of the remainder was NOT RE-CHECKED (volume EPERM).

### c. Exit conditions (which loop never exits, and why)

| Loop | Exit condition | Holds? | Evidence |
|---|---|---|---|
| 16-slot scan (`0x3e5980`–`0x3e59dc`, `$s1` 15→−1) | `$s1 < 0` after 16 slots | Yes, every pass (returns OR-accumulator `$s2`) | Bounded countdown; 2.75M dispatches/block each return (driver re-calls) |
| Per-slot fire | fn≠0 ∧ tick ≥ next ∧ busy=0 | Holds ~600×/5 s (slots 0–1) | Stub counts `0x31ad20`/`0x3e33b0` ~300/block each |
| Driver `sub_003DD1D8` inner loop (`0x3dd278`→`0x3dd2e0`) | `*( $s1+8 ) ≠ 0` at `0x3dd2e0` (`$s1` = `*(0x519AD8)` + byte·`0x30`) | **Never** (35/35 p1j blocks, 17/17 p1k blocks parked) | `0x3e5440` count == `0x3e5928` count every block (always takes run path: `*(0x450DFC)`≠0); park pcs `0x3e5980`/`0x3dd278`/`0x423c90` only |
| Outer caller (one frame above `0x3dd1d8`) | `sub_003DD1D8` returns | Never (same park) | Thread 1 never sampled above `0x3dd278` |

Wait object: the `+8` flag of the `*(0x519AD8)` table entry selected by `sub_003DD1D8`'s `$a0` byte. Its writer is unidentified (address is dynamic; no static writer found; no watch was placed — address not known until `$a0` is). Tick `*(0x450DD0)` producer likewise untraced (lead, unverified: `EeScheduler.cpp:1587` writes a `tickAddress` to guest RAM). Next fix class per item: 16-scan — none (bounded); slot fire — none (fires); driver flag — trace producer of `*(entry+8)` (one level up: the 8 callers below select the entry).

### d. Outer caller: narrowed to 8, not named (receipt missed)

Closed log has no RA/stack receipt for the live caller: thread dumps carry no `ra`; stub histogram is hard-capped at top 30 (`ps2_runtime.cpp:1127`, `i < 30u`, no REPORT_ALL override — block 0 prints 30 entries + header for distinct=485); all 8 sites + entries have 0 hits in boot-p1j-1; P6 names only one containing function. Back-edge search (`jal func_3DD1D8` over `$W/P1/output`):

| # | Site | File (= sweep start) | ra | Delay `$a0` | Pre-context | P6 in function |
|---|---|---|---|---|---|---|
| 1 | `0x3dec20` | `sub_003DEBF0` | `0x3dec24` | `$s0` (null-checked) | `$s0`=$v0; `beql $s0,0` skip | — |
| 2 | `0x3debc0` | `sub_003DEB50` | `0x3debc4` | `lw $a0,0x20($sp)` | after `jal func_3DCF70` | — |
| 3 | `0x3decc8` | `sub_003DECA0` | `0x3deccc` | `$s0` (null-checked) | `$s0`=$v0; `beqz` skip | — |
| 4 | `0x3dee40` | `sub_003DEE18` | `0x3dee44` | `$s0` (null-checked) | `$s0`=$v0; `beqz` skip | — |
| 5 | `0x3dede8` | `sub_003DEDC0` | `0x3debec` | `$s0` (null-checked) | `$s0`=$v0; `beqz` skip | — |
| 6 | `0x3ded80` | `sub_003DED50` | `0x3ded84` | `$s0` (null-checked) | `$s0`=$v0; `beql` skip | — |
| 7 | `0x3ded20` | `sub_003DECF8` | `0x3ded24` | `$s0` (null-checked) | `$s0`=$v0; `beqz` skip | — |
| 8 | `0x3dfa5c` | `sub_003DF9D8` | `0x3dfa60` | (site+4 insn; not re-read) | `lw $a0,0x1C($s1)` after null-check | `0x3df9d8 ASYNCFILE_release` (exact start) |

All 8 are straight-line wrappers (`$s0`=$v0 from a prior call, null-check, `jal 3DD1D8`); none sits in a loop, so static shape does not distinguish the live one. What the caller waits on (one level): the `sub_003DD1D8` call itself. Step-2 receipt attempted: WATCH `0x1ffe010` (= park_sp `0x1fffd80`+`0x90`, the `sd $ra,0x10($sp)` save at `0x3dd214`) — MISSED: 15 w16 zero-writes from `pc=0x3e65b0` (pre-park stack reuse) and zero `pc=0x3dd214` lines; only 2 w8 lines in all 32,077 (both `value=0x0` at `0x519c48`/`0x519c50`, `pc=0x3e64d0`/`0x3e64d8`), consistent with the P1f watchpoint not covering the guest `sd` path while covering `sw`/`sq` — source re-check blocked by volume EPERM (see P12-7). Single next receipt for a future brief: w4-watch `0x1ffe000` (the `sw $a0,0($sp)` at `0x3dd1e0`, same frame, `ra`=caller).

## P12-2. Missing-target analysis (Step 1c)

### a. Target `0x395cf0`: unsplit frameless leaf inside `sub_003956B0`

| Item | Value |
|---|---|
| Containing function (sweep CSV) | `sub_003956B0,0x3956b0,0x396128,0xa78` (current `output/sub_003956B0_0x3956b0.cpp` agrees; no `sub_00395CF0` file) |
| P6 name | None (0 `0x395*` rows) |
| Target block (ELF-verified) | `0x395cf0: lui $v0,0x50` (`0x3c020050`); `0x395cf4: lw $v1,0x13E4($a0)`; `0x395cf8: addiu $v0,-0xE60`; 4×`lqc2` + 4×`sqc2` (matrix copy `$v0[0x50F1A0]`→`$v1`); `0x395d1c: jr $ra` (`0x3e00008`); delay `sw $zero,0x6B90($a0)`; `0x395d24: nop` |
| Preceding boundary (ELF-verified) | `0x395ce4: jr $ra` (`0x03e00008`); `0x395ce8` delay `sw`; `0x395cec: nop` (`0x00000000`) — textbook function boundary the sweep did not split |
| Registration | `output/register_functions.cpp`: **0 lines** for `0x395cf0` (vs 3 for containing `0x3956b0`) |
| Sibling unsplit leaves in same sweep function (same jr/nop/prologue pattern, none split, none registered — NOT RE-CHECKED individually post-volume-failure except by the earlier listing read) | `0x395c38` (`lw $v0,0x13E4($a0)`…), `0x395c68` (`jr $ra` + delay-load), `0x395c70`, `0x395d28` |
| Why no slot | `dispatchGuestBranch` (`ps2_runtime.cpp:1544-1593`) exact-matches `hasFunction(targetPc)`; indirect JALR targets are never promoted (cf. 3,594 `unresolved JR/JALR` analyzer warnings); `0x395cf0` was never a direct-call target (0 `func_395CF0` refs in `output/`) and never split into its own function, so no table entry exists |
| Effect at runtime | `reportMissingFunction` prints once; policy=1 = `ContinueToTarget` (`ps2_runtime.h:333-339`: log once, `ctx->pc`=target, caller unwinds); for `isCall` the generated JALR wrapper then falls through to `ra` — the call is skipped, non-fatal (boot continues to the park) |
| One-line fix class | **split** (analyzer: split `sub_003956B0` at `0x395cf0` — and sibling leaves — with entrypoint registration, mirroring the existing splits below) |

Control pair (same unsplit-prologue pattern, but the analyzer DID split and register these — which is why slot dispatch to them resolves):

| Addr | Split file exists | `register_functions.cpp` lines | Direct `func_*` refs in `output/` |
|---|---|---|---|
| `0x31ad20` | `sub_0031AD20_0x31ad20.cpp` (overlaps `sub_0031AD18`, which starts with a 2-insn `jr $ra` stub) | 4 (`0x31ad20`/`54`/`74`/`98` → `sub_0031AD20`, e.g. line 296302) | 0 |
| `0x3e33b0` | `sub_003E33B0_0x3e33b0.cpp` | 4 (`0x3e33b0`/`0x3e3418`/`0x3e342c`/`0x3e3458`, lines 380337-380340) | 0 |
| `0x395cf0` | none | 0 | 0 |

Note: entries `0x31ad20`/`0x3e33b0` resolve despite 0 direct refs, so promotion is not direct-call-only; the discriminator the evidence supports is split-vs-unsplit. The sweep CSV (`ssx3-functions.csv`, Sep 18 17:48) predates the p1h recompile (`output/`, Sep 18 21:15+) and still shows the unsplit rows (`sub_0031AD18 0x31ad18-0x31adb0`, `sub_003E3350 0x3e3350-0x3e3478`); current `output/` + `register_functions.cpp` above are authoritative.

### b. JALR site `0x3760d0` (ELF-verified)

| Item | Value |
|---|---|
| Insns | `0x3760c4: lw $v1,0x10D8($s2)`; `0x3760c8: lh $a0,0x128($v1)`; `0x3760cc: lw $v0,0x12C($v1)` (`0x8c62012c`); `0x3760d0: jalr $v0` (`0x0040f809`); delay `addu $a0,$s2,$a0`; `0x3760d8` (`ra`) `: lwc1 $f4,-0x27EC($gp)` |
| Loads | `$v0` = object-table dispatch: `*( *( $s2+0x10D8 ) + 0x12C )`; target `0x395cf0` is a data-seated code pointer (vtable-style slot), reached with `a0=0x61ba60` (=`$s0`, readable, all-zero first 16 B) |
| Containing function | Sweep `sub_00375A08 0x375a08-0x376938` (the old CSR-park function; park was at `0x375d10`); no P6 name (0 `0x375*`/`0x376*` rows) |
| Thread | 1 (`sp=0x1fffd90` ∈ T1 stack `0x1fe0000/0x20000`); pre-park, log:146 (p1j) / log:187 (p1k), byte-identical incl. regs + 64-entry dispatch trace (`0x411c38…→0x3760c4`) |

### c. Other new stubs: called-from, returns-or-parks

(`called-from` = stub-histogram `firstRa`/`lastRa`; `returns` = `jr $ra` reachable + balanced counts; park = none of these park.)

| Target | Called-from (log) | Shape (output/) | Returns-or-parks | Block presence (p1j) |
|---|---|---|---|---|
| `0x31ad20` | `0x3e59c0` (slot dispatch in `SYNCTASK_run`) | frame `-0x40`, `jr $ra` @`0x31ada8` (`$v0`=0) | returns | 35/35, ~300/block |
| `0x3825f8` | `0x3825dc` (ret of `jal func_3825F8` @`0x3825d4` in INTC cause-2 handler entry `0x3825c0` = stacks `intc id=3 cause=2 handler=0x3825c0`; the `sync` at `0x3825dc` is the return slot) | `jr $ra` @`0x38267c` (`$v0`=1) | returns | 35/35, ~300/block (60/s ≈ vsync rate) |
| `0x3e33b0` | `0x3e59c0` (slot dispatch) | frame `-0x50`, `jr $ra` @`0x3e3470` | returns | 35/35, ~300/block |
| `0x3e5440` | `0x3dd280` (driver) | `jal GetThreadId` @`0x3e544c`; `$a0`=0 path returns `*(0x450DFC)` (always nonzero here: run-path counts equal) | returns | 35/35, ~2.75M/block |
| `0x3e5928` (`SYNCTASK_run`) | `0x3dd290` (driver) | 16-scan, `jr $ra` @`0x3e5a08` (`$v0`=`$s2` OR) | returns | 35/35, ~2.75M/block |
| `0x411c38` | `0x412520`/`0x4126b8` = `sub_00412500+0x20` / `sub_004126A0+0x18` | frameless 64-bit leaf, `jr $ra` @`0x411ccc` | returns | block 0 only (392) → early-boot-only |
| (`0x423c90`, 8th new in P11) | `0x3e5454` steady (= ret of `jal` @`0x3e544c`), `0x3e5028` boot | `syscall 0x2F` = `GetThreadId`, `jr $ra` @`0x423c98` | returns | 35/35, ~2.75M/block |

## P12-3. CD + syscall deltas (Steps 1d/1e)

### a. First CD callback

| Item | Value |
|---|---|
| What queued it | `sceCdRead lbn=0x5f1a3 sectors=1 buf=0x9d0800 ret=0x3e3b8c` (p1j log:147-148; HLE completes synchronously: `CD.cpp:402-403` `setReturnS32(ctx,1)` + `queueCdCallback(ctx,runtime,1u)` = `SCECdFuncRead`) |
| Why earlier reads didn't queue | Reads at lbn `0x10`,`0x105`-`0x117`,`0x108` (log:58-138) pre-date callback registration (`sceCdInitEeCB` log:142 → `sceCdCallback` setter `CD.cpp:445` sets `g_cdCallbackFn=0x3e3ad8`); `queueCdCallback` early-returns while `g_cdCallbackFn==0` (`CD.cpp:69`) |
| Start line | Present (log:149-150 p1j; log:192-193 p1k): `queued func=1 cb=0x3e3ad8`, `start func=1 cb=0x3e3ad8` |
| Completion/finish line | **None exists in sources** (emits are only `queued` `CD.cpp:84` + `start` `EeScheduler.cpp:398,495`); completion is unobservable by design |
| Callback body (`0x3e3ad8` ∈ `sub_003E39A8`) | `$a0`= `*(0x519C4C)`; `jal func_423DD0` = syscall `-0x43` = `iSignalSema`; `jr $ra` |
| `*(0x519C4C)` value (Step-2 WATCH) | `0x1a` = **26**, written once (`pc=0x3e43fc`, `ra=0x3e43c4`, thread 1, `sp=0x1ffec80`) |
| Bearing on thread 2 (sema 26) | Direct: T2 (`entry 0x3e3be0`) issued this read (`jal func_401DF8` ret `0x3e3b8c`, `$v0`=1 accepted, `beqz` not taken) and parks in `WaitSema(*($s2+0xC))` @`0x3e3c18` (`ra=0x3e3c1c`); the callback signals sema 26 — but T2 is still parked at block 34 (`scheduled`≈0), so the signal did not land within 180 s (callback completion unconfirmed — no finish line) |
| Bearing on thread 4 (sema 29) | None via CD: T4 (`entry 0x31ac08`) loops `func_317500($s0)` + `WaitSema(*($s0+0x4034))` @`0x31ac28` (`ra=0x31ac30` = steady-state `firstRa` of stub `0x423de0`), waking ~300/block from a non-CD source |
| Bearing on thread 5 (sema 30) | None via CD: T5 (`entry 0x382740` → `jal func_382760`) parks in `WaitSema` @`0x3827d8` (`ra=0x3827e0`), `scheduled`≈0 |

### b. Syscalls `0x15`/`0x17`

| Item | `0x15` | `0x17` |
|---|---|---|
| Name (`Dispatcher.cpp:137/143`) | `DisableIntc` | `DisableDmac` |
| Purpose | `setCauseEnabled(…,dmac=false,…)` (`Interrupt.cpp:108-111`): clear bit `$a0` in INTC enable mask | Same for DMAC mask (`Interrupt.cpp:178-181`) |
| Return value (source-derived; `EeScheduler.cpp:1506-1522`, `State.h:24`) | `KE_OK` = 0, always (previous state NOT returned) | `KE_OK` = 0, always |
| Caller stub (output/) | `sub_00423AF0`: `addiu $v1,0x15; syscall; jr $ra` — log `first=0x423af8` is the `jr $ra` edge | `sub_00423B10`: same shape for `0x17`; `first=0x423b18` |
| Counts (p1j block 0; p1k block 0 identical) | 4 | 1 |
| `$a0` cause args / observed `$v0` | Not in log (histogram records count + caller pc only); a boot cannot capture them either (no per-syscall arg/return diag; enables live in host masks, no guest-RAM write to watch) — source-derived values only | Same |

Wait object / next fix class: none for either (one-shot disables returning constant 0; no wait). Related wrappers decoded for context: `0x423c90`=`GetThreadId` (`0x2F`), `0x423de0`=`WaitSema` (`0x44`), `0x423dd0`=`iSignalSema` (`-0x43`), `0x423dc0`=`SignalSema` (`0x42`), `0x423da0`=`CreateSema` (`0x40`).

## P12-4. Ladder delta vs boot-p1j-1

Boot-p1k-1: `$W/P1/run/boot-p1k-1.log`, 33,038 lines, 3,052,064 B, 17 period blocks, CWD `$W/P1/run`, env = p1j env + `PS2X_DIAG_WATCH` (10 addrs; see P12-6), foreground 90 s, SIGTERM rc=-15. Binary identical to p1j (see P12-5), so deltas below are run-to-run determinism, not code change.

| Rung | boot-p1j-1 (180 s, 35 blocks) | boot-p1k-1 (90 s, 17 blocks) | Delta |
|---|---|---|---|
| Thread-1 pc | `0x3e5980` ×31, `0x423c90` ×2, `0x3dd278` ×2 | `0x3e5980` ×15, `0x3dd278` ×1, `0x423c90` ×1 | Same park, same 3 pcs |
| Thread-1 sp at park | `0x1fffd80` | `0x1fffd80` (block 0) | Same |
| Stub top-3 block 0 | `0x423c90` 2369833, `0x3e5928` 2369619, `0x3e5440` 2369599 (firstRa `0x3e5028`/`0x3dd290`/`0x3dd280`) | Identical counts + ras | None (deterministic) |
| Missing target | 1 line, log:146 | 1 line, log:187, byte-identical (regs + trace) | None |
| CD callback | queued+start log:149-150 | queued+start log:192-193 | None |
| Syscalls `0x15`/`0x17` block 0 | 4 / 1 | 4 / 1 | None |
| Threads 2/4/5 states | sema-parked 26/29/30 | NOT RE-CHECKED (volume EPERM) | Unknown |
| VIF/GIF/frame/crash | 0/0/0/0 | NOT RE-CHECKED (volume EPERM) | Unknown |

ELF decode check for every block cited in P12-1–P12-3 (`SLUS_207.72`, file_off = va−`0x100000`+`0x1000`):

| va | word | disasm | match |
|---|---|---|---|
| `0x3760cc` | `0x8c62012c` | `lw $v0,0x12C($v1)` | OK |
| `0x3760d0` | `0x0040f809` | `jalr $v0` | OK |
| `0x395ce4` | `0x03e00008` | `jr $ra` | OK |
| `0x395cec` | `0x00000000` | `nop` | OK |
| `0x395cf0` | `0x3c020050` | `lui $v0,0x50` | OK |
| `0x3e5980` | `0x8e06fff4` | `lw $a2,-0xC($s0)` | OK |
| `0x3e59b8` | `0x00c0f809` | `jalr $a2` | OK |
| `0x3dd278` | `0x0c0f9510` | `jal 0x3E5440` | OK |
| `0x3dd288` | `0x0c0f964a` | `jal 0x3E5928` | OK |
| `0x31af54` | `0x2484ad20` | `addiu $a0,$a0,-0x52E0` (→`0x31AD20`) | OK |
| `0x3e304c` | `0x0000302d` | `daddu $a2,$zero,$zero` (delay of add-site jal) | OK |

## P12-5. Binaries and commits

| Binary / ref | sha256 / sha | Sources / state |
|---|---|---|
| `/tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner` (boot-p1k-1 binary) | `e5f8139772efe522aeb344e59692fecf04b175d0e695838bc714e134fcdbc1ca` | Identical to boot-p1j-1 binary → fresh, no rebuild (brief: rebuild only if stale) |
| `PS2Recomp` branch `ssx3` HEAD | `8fad69e` (last verified pre-boot; post-boot NOT RE-CHECKED) | Worktree: only pre-existing local `M ps2xRuntime/src/runner/register_functions.cpp`, never added |
| Fork commits this brief | None (diagnose only; no source, TOML, or test change) | Nothing to push from the fork clone; push rule (`git push` only in fork clone) satisfied vacuously; no push run anywhere |
| This report | `[P1k]` commit on `/Users/bradrichardson/dev/ssx3` (two trailers; local only — no push there per the push rule) | Sole ssx3-repo change; no `runner/`, log, or `._*` file added |

## P12-6. Exact commands

From `/Users/bradrichardson` (cwd) unless noted; `$W=/Volumes/Extreme SSD/ps2recomp-spike`, `$O=$W/P1/output`, `$R=$W/PS2Recomp`:

```
# Step 1 (no lease, no boot)
ls -l local/research/P6/ssx3-decomp-names.csv            # present -> P6 names used
grep -n "^# P1\|P11-" local/research/P1/REPORT.md         # locate Part 11 (lines 3862-4035)
grep -n "missing-target" $W/P1/run/boot-p1j-1.log        # log:146
grep -n "cd:callback" $W/P1/run/boot-p1j-1.log           # log:149-150
grep "diag:thread.*id=1 " log | sed pc-census            # 31/2/2 split
grep "diag:syscall\|diag:stub\|diag:stacks" log          # histograms + stacks (top-30 truncation found)
python3 sweep-map: 26 addrs -> ssx3-functions.csv rows   # containing functions
grep -o "// 0x..." $O/sub_*.cpp                          # MIPS listings: 003E5928, 003DD1D8, 003E5440,
                                                         # 003E57F8/58C8/5760(init), 00375A08, 003956B0,
                                                         # 00423AF0/B10/C90/DE0/DD0/DC0/DA0, 0031AD18,
                                                         # 003E3350, 003825F8, 00411C38, 003E3B00,
                                                         # 0031AAF0, 00382730, 003E39A8, 0037E120 tail
grep -rn "jal         func_3DD1D8" $O                    # 8 caller sites
grep -rn "jal         func_3E57F8" $O                    # 5 add sites (+ $a0 decode each)
grep -c "func_31AD20|func_3E33B0|func_395CF0" $O/sub_*.cpp  # 0/0/0 direct refs
grep -c "31ad20|3e33b0|395cf0" $O/register_functions.cpp # 4/4/0 registration lines
Dispatcher.cpp:137/143 (0x15/0x17), 0x2F/0x40/0x42/-0x43/0x44 names
Interrupt.cpp DisableIntc/Dmac; EeScheduler.cpp:1506 setIrqCauseEnabled (KE_OK=0)
ps2_runtime.cpp:1384-1626 dispatchGuestBranch/missing-target/policy; :1098-1133 top-30;
  :1137-1240 + :2301-2372 WATCH parse/hooks; ps2_runtime.h:333-339 policy enum
CD.cpp:66-90 queue, :402-403 read+queue, :445 setter; EeScheduler.cpp:398,495 starts
python3 ELF word check x11 (all OK) + BSS check (0x51ED98 above file end 0x4A4BF4)
shasum -a 256 /tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner   # e5f81397 (fresh)
git -C $R log --oneline -1; git -C $R status --short            # 8fad69e + pre-existing M
# Step 2 (lease protocol)
cat /tmp/ssx3-host-lease                                        # absent
pgrep -f ps2EntryRunner                                         # none
sed /tmp/p1j-boot1.py -> /tmp/p1k-boot1.py                     # LOG boot-p1k-1, SECS 90,
                                                              # + PS2X_DIAG_WATCH=0x51ed98,0x51eda0,
                                                              # 0x51eda8,0x51edb0,0x51edb8,0x51edc0,
                                                              # 0x51edc8,0x51edd0,0x1ffe010,0x519c4c
printf 'P1k\n' > /tmp/ssx3-host-lease
python3 /tmp/p1k-boot1.py                                       # foreground 90 s, SIGTERM rc=-15, 3052064 B
rm -f /tmp/ssx3-host-lease; ls /tmp/ssx3-host-lease            # released, verified absent
grep "diag:watch" log harvest: fills (3e5898 x3), del (3e591c), sema (519c4c=0x1a),
  stack (1ffe010: 15x w16 zeros, 0x 3dd214), widths (32050/25/2), slot0 pcs
grep ladder: thread-1 census 15/1/1, stub b0 top-3 identical, missing-target :187
  identical, callback :192-193, syscall 0x15 x4 / 0x17 x1
# Step 3
(edit_file append Part 12; commit below)
git -C /Users/bradrichardson/dev/ssx3 add -f local/research/P1/REPORT.md
git -C /Users/bradrichardson/dev/ssx3 commit -m "[P1k] ..." (two trailers; NO push there)
```

Env delta vs boot-p1j-1 (recorded deviation): `+PS2X_DIAG_WATCH` (the Step-2 capture mechanism for the three named missing receipts: slot-fill values/writers, `0x1ffe010` ra-save, `*(0x519C4C)` sema id) and `SECS 90` (brief max) vs 180. No other env change; no rebuild; no source change.

## P12-7. What I could not do

- Name the live outer caller of `sub_003DD1D8` (Step 1b): the single Step-2 boot (brief allows one) missed the `0x3dd214` `sd` receipt — 15 pre-park `sq` zero-writes fired on `0x1ffe010` but zero `pc=0x3dd214` lines, with only 2 w8 lines in 32,077, consistent with the P1f watchpoint covering `sw`/`sq` but not the guest `sd` path. 8 candidates tabled (§P12-1d); next receipt for a future brief: w4-watch `0x1ffe000` (`sw` at `0x3dd1e0`, same frame).
- Trace the producers of the driver-flag `*(entry+8)` (`$s1`=`*(0x519AD8)`+byte·`0x30`), the SYNCTASK tick `*(0x450DD0)`, and the run-gate `*(0x450DFC)`: all dynamic/host-side, no static writer identified, no watch placed (addresses unknown until `$a0`/scheduler mapping is known). Nearest P6 lead (unverified): `0x3de420 iFILESYS_CommandCompleteCallback` for a FILESYS-family completion flag.
- Re-verify in boot-p1k-1 (volume EPERM after ~23:05 UTC, all SSD data reads fail): threads 2/4/5 states, VIF/GIF/frame/crash zeros, per-pc split of the ~32K steady-state slot w4 remainder, sibling-leaf (`0x395c38`/`0x395c68`/`0x395c70`/`0x395d28`) split-file/registration exclusion greps, and fork post-boot state (git status, stray files, sidecar check — last known pre-boot: `8fad69e` + pre-existing `M`, no strays created by this brief's own commands).
- Push-collateral verification: nothing to push from the fork (no fork commit this brief); fork-clone `git push` up-to-date check could not run (volume EPERM). No push was run in `/Users/bradrichardson/dev/ssx3` (forbidden).
- No runtime fix (per the brief): park, missing target, and sema-26 non-delivery are diagnosed, not changed.

---

## Part 13 (P1l): 0x395cf0 + 3 siblings split, missing target gone, park unchanged, outer-caller receipt missed again

Brief `local/muse/prompts/P1l.md`. Splits + ladder only; no runtime fix. Tables, no verdicts.
P6: 0 `0x395*` rows (re-verified 09-19) → `sub_*` names below.

## P13-0. Lease record

| Event | Value |
|---|---|
| Lease at session start | `M6` (foreign; `/tmp/ssx3-host-lease` dated Sep 18 23:30) |
| Steps 1–2 + rebuild + tests | No lease (CSV edit, recomp file-to-file, fresh configure+build need none) |
| 03:39 UTC | Lease absent (M6 hold gone; never overwritten) |
| Pre-boot checks (04:01 UTC) | `pgrep -f ps2EntryRunner` exit 1 (none); binary `0b38f7b6` fresh (just built); ISO + ELF present |
| Claim | `printf 'P1l\n' > /tmp/ssx3-host-lease` 04:01:07 UTC, immediately before boot-p1l-1 |
| Release | `rm -f /tmp/ssx3-host-lease` in the same command as the boot return; verified absent 04:02:38 UTC |
| Waits | None (no poll loop ran; `$W/P1/run/p1l-waits.log` does not exist) |
| `adb` | Not used |

## P13-1. Splits + regen audit

### a. CSV (`ssx3-functions.sweep.csv`; TOML `ghidra_output` unchanged)

| Item | Value |
|---|---|
| Rows before | 9271 lines = header + 9270 data |
| Rows after | 9275 lines = header + 9274 data (+4, as expected) |
| Backup | `ssx3-functions.sweep.csv.p1l-orig` (9271 lines, pre-edit bytes) |
| Line endings | LF only before and after (0 CR) |
| Duplicate starts | `0x42c1f0` ×2 before and after (pre-existing `ret0` row; no new dup) |
| `0x395c70` pre-existing row (before, line 7007) | `sub_00395C70,0x395c70,0x395d60,0xf0` — no new row needed |
| `0x395c70` split file + reg (pre-regen) | `sub_00395C70_0x395c70.cpp` present; 1 reg line (`:352206`); not re-split |

Replaced 2 rows (lines 7006–7007) with 6 (lines 7006–7011):

| Line | Row |
|---|---|
| 7006 | `sub_00395750,0x395750,0x395c38,0x4e8` |
| 7007 | `sub_00395C38,0x395c38,0x395c68,0x30` |
| 7008 | `sub_00395C68,0x395c68,0x395c70,0x8` |
| 7009 | `sub_00395C70,0x395c70,0x395cf0,0x80` |
| 7010 | `sub_00395CF0,0x395cf0,0x395d28,0x38` |
| 7011 | `sub_00395D28,0x395d28,0x395d60,0x38` |

Contiguity: `0x4e8+0x30+0x8=0x520`, `0x80+0x38+0x38=0xf0` (both parents' sizes preserved).

ELF boundary words (`SLUS_207.72`, file off `0x1000+(va-0x100000)`):

| T | T−12 | T−8 | T−4 | T | T+4 |
|---|---|---|---|---|---|
| `0x395c38` | `0x03e00008` (jr $ra) | `0x27bd00e0` (addiu sp,+N, delay) | `0x00000000` (nop) | `0x8c8213e4` (lw) | `0xd8a10000` (lqc2) |
| `0x395c68` | `0x03e00008` (jr $ra) | `0xac806b90` (sw, delay) | `0x00000000` (nop) | `0x03e00008` (jr $ra; 2-insn stub + delay-load) | `0x8c8213e4` (lw, delay) |
| `0x395cf0` | `0x03e00008` (jr $ra) | `0xac806b90` (sw, delay) | `0x00000000` (nop) | `0x3c020050` (lui $v0,0x50) | `0x8c8313e4` (lw) |
| `0x395d28` | `0x03e00008` (jr $ra) | `0xac806b90` (sw, delay) | `0x00000000` (nop) | `0x8c8213e4` (lw) | `0xd8440000` (lqc2) |

Collision check (Part-5 predicate: `case 0x<T>u` / `label_<T>` in enclosing file): 0 for all 4
(`0x395c38`/`0x395c68` in `sub_00395750`, `0x395cf0`/`0x395d28` in `sub_00395C70`).
Pre-regen: 0 split files + 0 reg lines for all 4 addrs.

### b. Regen (`recomp-p1l.log`, CWD `$W/P1`, `./bin/ps2_recomp ssx3.toml`, exit 0)

Analyzer not re-run: no analyzer source change, no TOML change — `ps2_recomp` only, mirroring P1d.
Recomp binary `7654e7fe…e826f` (unchanged since P2).

| Item | p1h (`recomp-p1h.log`) | p1l (`recomp-p1l.log`) |
|---|---|---|
| Discovered / processed | 9269 / 9269 | 9273 / 9273 (+4) |
| Recompiled / stubs / skipped | 9092 / 177 / 0 | 9096 / 177 / 0 (+4 recompiled) |
| Decode failures / unhandled | 0 / 0 | 0 / 0 |
| Entrypoints | 393727 | 393727 (same) |
| Warnings (unresolved JR/JALR) / fallbacks | 3598 / 724964 | 3598 / 724964 (same) |

| Addr | New split file (bytes) | `register_functions.cpp` line |
|---|---|---|
| `0x395c38` | `sub_00395C38_0x395c38.cpp` (2793) | `:352206` → `sub_00395C38_0x395c38` |
| `0x395c68` | `sub_00395C68_0x395c68.cpp` (1300; jr $ra + delay-load only) | `:352207` → `sub_00395C68_0x395c68` |
| `0x395cf0` | `sub_00395CF0_0x395cf0.cpp` (3031; `lui $v0,0x50` head) | `:352209` → `sub_00395CF0_0x395cf0` |
| `0x395d28` | `sub_00395D28_0x395d28.cpp` (3855) | `:352210` → `sub_00395D28_0x395d28` |
| `0x395c70` | (retained, truncated to `0x395c70–0x395cf0`) | `:352208` retained |

Runner refresh: `cp -X output/*.{cpp,h}` → `ps2xRuntime/src/runner/` (9273 → 9277 files),
sidecars purged, `diff -rq output/ runner/` clean (exit 0). Never added/committed.

### c. Fresh `/tmp/p1-link` (old dir gone with `/tmp`; all `/tmp/p1*` absent at session start)

| Item | Value |
|---|---|
| Configure | `cmake -S $W/PS2Recomp -B /tmp/p1-link/runtime -G Ninja -DPS2X_BUILD_STUDIO=OFF -DPS2X_BUILD_RUNTIME=ON -DPS2X_BUILD_TEST=ON -DCMAKE_BUILD_TYPE=Release -DPS2X_ENABLE_RUNTIME_LOGS=ON -DPS2X_ENABLE_AGRESSIVE_LOGS=ON` (P2 flags), exit 0, 84 s (`configure-runtime-p1l.log`) |
| Build | `cmake --build /tmp/p1-link/runtime --target ps2EntryRunner ps2x_tests -j4`, exit 0, 534 targets (`build-runtime-p1l.log`; unity build) |
| `ps2EntryRunner` sha256 | `0b38f7b68d4adb1e0ef722b1ff9d0c077631e787cd7d1c14063bdc64c7266a18` (163,329,408 B; differs from p1k `e5f81397` — fresh dir, same sources+flags) |
| `ps2x_tests` sha256 | `7f0102cebc4718b98f482f68cb9e6cf311817b65c0452367f8c3781f15b57155` |

### d. Test receipts (`ps2x_tests`, CWD fork root; full log `$W/P1/ps2x-tests-p1l.log`)

| Run | Total | Passed | Failed |
|---|---|---|---|
| Regen tree (HEAD `8fad69e` + refreshed runner glue) | 425 | 424 | 1: `sceGsSyncVCallback runs as a scheduler invocation on its callback stack` (`callback invocation should use the reserved async stack pool`) — same test + assertion as P1j |

Pre-existing-status receipts (no stash A/B re-run: no tracked source changed this brief):

| Item | Value |
|---|---|
| Tracked tree vs P1j with-fix run | Identical HEAD (`8fad69e`); identical `git status` (sole `M ps2xRuntime/src/runner/register_functions.cpp`, generated, never added) |
| Runner symbols in `ps2x_tests` | 0 (`sub_00395C70`/`sub_0031AD20`/`sub_003E5928`/`sub_00395CF0` all 0 hits via `strings`; control: `sub_00395CF0` 1 hit in `ps2EntryRunner`) |
| Table definition linked by tests | `ps2xRuntime/src/lib/ps2_runtime.cpp` (non-runner; unchanged this brief) |

## P13-2. Boot ladder delta vs boot-p1k-1

Boot-p1l-1: `$W/P1/run/boot-p1l-1.log`, 9,137 lines, 855,709 B, 17 blocks, CWD `$W/P1/run`,
env = p1k env + `0x1ffe000` appended to `PS2X_DIAG_WATCH` (11 addrs), foreground 90 s, SIGTERM rc=-15.
Binary `0b38f7b6` (fresh; §P13-1c).

| Rung | boot-p1k-1 (33,038 lines, 3,052,064 B) | boot-p1l-1 | Delta |
|---|---|---|---|
| Thread-1 pc | `0x3e5980` ×15, `0x3dd278` ×1, `0x423c90` ×1 | `0x3e5980` ×14, `0x3e5440` ×3 | Same park family (per-block table below); no new park |
| Missing target | 1 line (`0x3760d0→0x395cf0`, log:187) | 0 lines (`395cf0`/`395CF0`: 0 hits anywhere) | Gone |
| Stub distinct b0 / b1–16 | 485 / 18 | 486 / 18 | +1 in b0 (below-cutoff member unnameable; top-30 truncation) |
| Syscall distinct b0 / b1+ | 27 / 3 | 27 / 3 | None; printed b0 id sets identical (20 ids incl `0x15`/`0x17`); first new ids: none |
| CD callback | queued+start log:192-193 | queued+start log:434-435 | Same pair, later lines |
| Threads 2/4/5 | sema-parked 26/29/30 (p1j; p1k not re-checked) | `pc=0x423de8` sema 26/29/30 all 17 blocks | Confirmed |
| Threads (block 0) | ids 1–5 | ids 1–5 (same entries/priorities/stacks) | None |
| VIF MPG/MSCAL | 0 | 0 (`mpg`/`mscal`: 0 hits; 7 `vif` hits are all `[run:tick]` counters) | None |
| GIF kick | 0 `gif` lines | First `[gs:kick]` log:216 (`idx=0 drawing=1 prim=6 vtxCount=1`); totals `gs:gif` 2, `gs:kick` 66, `gs:reg` 122, `gs:prim` 33, `gs:copy-reg` 8 | Visibility-only (gating table below) |
| Presented frame | None (raylib line only) | None (sole `frame` hit = raylib target-time line) | None |
| Crash | 0 | 0 (`crash`/`FATAL`/`assert`: 0) | None |
| Watch lines | 32,077 | 7,942 (~4×; per-addr census below) | Rate (see below) |
| Dormant / StartThread | 45 / 4 (ids 2,3,4,5) | 40 / 4 (ids 2,3,4,5) | −5 dormant |
| Literal `dispatch` lines | 0 | 0 | None (per-dispatch receipt = `scheduled=N`) |
| Slot fills | fn/period/next `0x27`, writers `0x3e4458`/`0x3e3050`/`0x31af60`, del `0x31af4c` | Same fns/writers/sp; next `0x28`; `*(0x519C4C)=0x1a` (`pc=0x3e43fc ra=0x3e43c4`) same | Tick +1 |

Per-block table (both boots, 17 blocks; `sch` = id1/id4 `scheduled`; `stub` = `target=0x423c90` count):

| blk | p1k pc | p1k sch | p1k stub | p1l pc | p1l sch | p1l stub |
|---|---|---|---|---|---|---|
| 0 | `0x3e5980` | 283/259 | 2369833 | `0x3e5440` | 78/54 | 484849 |
| 1 | `0x3dd278` | 300/300 | 2750793 | `0x3e5440` | 79/79 | 722340 |
| 2 | `0x3e5980` | 301/301 | 2759963 | `0x3e5980` | 74/74 | 679267 |
| 3 | `0x3e5980` | 301/301 | 2759964 | `0x3e5980` | 73/73 | 664939 |
| 4 | `0x3e5980` | 300/300 | 2750793 | `0x3e5980` | 71/71 | 651414 |
| 5 | `0x3e5980` | 302/302 | 2769132 | `0x3e5980` | 72/72 | 657899 |
| 6 | `0x3e5980` | 301/301 | 2759964 | `0x3e5440` | 62/62 | 563060 |
| 7 | `0x3e5980` | 302/302 | 2769131 | `0x3e5980` | 78/78 | 712451 |
| 8 | `0x3e5980` | 300/300 | 2750795 | `0x3e5980` | 80/80 | 733748 |
| 9 | `0x3e5980` | 300/300 | 2750793 | `0x3e5980` | 79/79 | 724724 |
| 10 | `0x3e5980` | 301/301 | 2754287 | `0x3e5980` | 75/75 | 687329 |
| 11 | `0x423c90` | 301/301 | 2765640 | `0x3e5980` | 77/77 | 705702 |
| 12 | `0x3e5980` | 301/301 | 2754870 | `0x3e5980` | 68/68 | 615412 |
| 13 | `0x3e5980` | 301/301 | 2759923 | `0x3e5980` | 79/79 | 726712 |
| 14 | `0x3e5980` | 299/299 | 2746756 | `0x3e5980` | 80/80 | 729929 |
| 15 | `0x3e5980` | 301/301 | 2759965 | `0x3e5980` | 80/80 | 731936 |
| 16 | `0x3e5980` | 300/300 | 2750793 | `0x3e5980` | 79/79 | 717806 |

Rate rows (p1k → p1l): `scheduled` ~300 → ~75 (4.0×); steady stub ~2.75M → ~0.69M (~4.0×);
watch 32,077 → 7,942 (4.0×). Cause open (§P13-6).

Byte-identical block-0 one-time stub rows (count + firstRa + lastRa equal in both boots):

| Target | Count | firstRa | lastRa |
|---|---|---|---|
| `0x416210` | 3985 | `0x393958` | `0x237d4c` |
| `0x3e3968` | 1149 | `0x4190c0` | `0x418868` |
| `0x31bf60` | 640 | `0x392e2c` | `0x392e2c` |
| `0x317670` | 583 | `0x284770` | `0x21c5ac` |
| `0x317618` | 583 | `0x317684` | `0x317684` |
| `0x4166f4` | 550 | `0x3e38cc` | `0x4163f0` |
| `0x416810` | 425 | `0x318308` | `0x3e3714` |
| `0x2ca258` | 414 | `0x2cd2c0` | `0x2cd92c` |
| `0x2cbcc8` | 414 | `0x250784` | `0x24d2b4` |
| `0x411c38` | 392 | `0x412520` | `0x4126b8` |
| `0x418958` | 221 | `0x41cae8` | `0x41b7a8` |
| `0x3e6574` | 208 | `0x317948` | `0x37c820` |

Block-0 top-30 set diff (10 out, 10 in; cutoffs 208 → 68):
out: `0x227f58`,`0x317348`,`0x317500`,`0x317520`,`0x31aac8`,`0x31abd0`,`0x31ad20`(259),`0x326b88`,`0x3825f8`,`0x3e33b0`(259)
(all p1k count 258–259 = per-period recurring work, below p1l cutoff 68 at p1l rates);
in: `0x2cd8f8`,`0x2cdce8`,`0x3e36f8`,`0x3e5700`,`0x3e5760`,`0x411b08`,`0x412500`,`0x41605c`,`0x4162d0`,`0x423dc0`.

Aggressive-gating table (all `gs:*` + `[run:tick]` sites wrapped in `PS2_IF_AGRESSIVE_LOGS:
`ps2_runtime.cpp:2625` (run:tick), `gs_frontend.cpp:650` (gs:gif), `:1530` (gs:kick)):

| Boot log | `run:tick` | `gs:gif` | `gs:kick` | `gs:reg` | `gs:prim` | `gs:copy` |
|---|---|---|---|---|---|---|
| p1b-8, p1c-3, p1d-2, p1f-2, p1h-1, p1j-1, p1k-1 (each) | 0 | 0 | 0 | 0 | 0 | 0 |
| p1l-1 | 7 (ticks 120–840; `dma=7 gif=2 gsw=0 vif=2` constant) | 2 | 66 | 122 | 33 | 8 |

Watch per-addr census (one-timers identical; steady-state ~4×):

| addr + width | p1k | p1l |
|---|---|---|
| `0x1ffe000` w16 | — (not watched) | 15 (all `pc=0x3e65dc`, zeros) |
| `0x1ffe010` w16 | 15 (all `pc=0x3e65b0`, zeros) | 15 (all `pc=0x3e65b0`, zeros) |
| `0x519c40` w16 / `0x519c48` w8 / `0x519c4c` w4 / `0x519c50` w16+w4×2+w8 | 1/1/1/1+2+1 | 1/1/1/1+2+1 (identical) |
| `0x51ed90` w16 / `0x51ed98` w4 / `0x51ed9c` w4 / `0x51eda0` w16 | 1/3/2/2 | 1/3/2/2 (identical) |
| `0x51eda0` w4 (next-tick updates `pc=0x3e59d4`) | 5341 | 1316 |
| `0x51eda4` w4 (busy 1/0 `pc=0x3e59b4`/`0x3e59cc`) | 10680 | 2630 |
| `0x51eda8` w4 / `0x51edac` w4 / `0x51edb0` w16 | 1/1/2 | 1/1/2 (identical) |
| `0x51edb0` w4 | 5340 | 1315 |
| `0x51edb4` w4 | 10679 | 2629 |
| `0x51edc0` w16 / `0x51edd0` w16 | 2/1 | 2/1 (identical) |

## P13-3. Outer-caller receipt

| Item | Value |
|---|---|
| `0x1ffe000` lines | 15 total, all `pc=0x3e65dc` w16 zeros (pre-park `sq` clears, `ra=0x3e382c sp=0x1ffd900`); **0 `pc=0x3dd1e0`** |
| `0x1ffe010` lines | 15 total, all `pc=0x3e65b0` w16 zeros; **0 `pc=0x3dd214`** (same as p1k) |
| `pc=0x3dd1e0` / `pc=0x3dd214` anywhere in log | 0 / 0 |
| Receipt | **Missed again** — no candidate of the P12-1d 8-table named; the 8 stand |

Derivation audit (static; watched addrs are arithmetically correct for the observed park):

| Item | Value |
|---|---|
| Driver frame (`0x3dd1d8` `addiu sp,-0x80`) | `0x80`; `sw $a0,0($sp)` at `0x3dd1e0`, `sd $ra,0x10($sp)` at `0x3dd214` (both after alloc) |
| Run frame (`0x3e5928` `addiu sp,-0x80`) | `0x80`; sampled at loop head (no further allocs) |
| Park sp `0x1fffd80` | 14/17 blocks p1l, 15/17 p1k |
| Derived `sw` addr | `0x1fffd80+0x80` = `0x1ffe000` ✓ watched |
| Derived `sd` addr | `0x1fffd80+0x90` = `0x1ffe010` ✓ watched |
| Run callers | Only the driver (`firstRa=lastRa=0x3dd290` for `0x3e5928`, all 17 blocks both boots) |
| Steady-state busy/next pcs (fills the P12 per-pc gap) | `0x3e59b4` (busy=1, `ra=0x3dd290`), `0x3e59cc` (busy=0, `ra=0x3e59c0`), `0x3e59d4` (next+=period, `ra=0x3e59c0`) |

Park sp is a function of sampled pc in both boots (no frame shift):

| pc | sp | p1l blocks | p1k blocks |
|---|---|---|---|
| `0x3e5980` | `0x1fffd80` | 14 (all except 0,1,6) | 15 (all except 1,11) |
| `0x3e5440` / `0x3dd278` | `0x1fffe00` | 0,1,6 | 1 |
| `0x423c90` | `0x1fffde0` | — | 11 |

## P13-4. Binaries and commits

| Binary / ref | sha256 / sha | Sources / state |
|---|---|---|
| `/tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner` (boot-p1l-1) | `0b38f7b68d4adb1e0ef722b1ff9d0c077631e787cd7d1c14063bdc64c7266a18` | Fresh `/tmp/p1-link` from `8fad69e` tree + regen runner sources |
| `/tmp/p1-link/runtime/ps2xTest/ps2x_tests` | `7f0102cebc4718b98f482f68cb9e6cf311817b65c0452367f8c3781f15b57155` | Same tree; 424/425 (§P13-1d) |
| `$W/P1/bin/ps2_recomp` | `7654e7fe4a7316476dfcc00a418c850bd8ecffeb301b345624500304e22e826f` | Unchanged since P2 |
| `PS2Recomp` branch `ssx3` HEAD | `8fad69e` | No fork commit (CSV untracked, no source change); worktree sole `M` = pre-existing generated `runner/register_functions.cpp`, never added |
| Fork push | `git push fork ssx3` from fork clone only (up-to-date check) | Nothing to push; verified up-to-date; no push in `/Users/bradrichardson/dev/ssx3` |
| This report | `[P1l]` commit (two trailers; local only) | Sole ssx3-repo change; no `runner/`, log, or `._*` added |

## P13-5. Exact commands

From `$W/PS2Recomp` (fork) unless noted; `$W=/Volumes/Extreme SSD/ps2recomp-spike`, `$O=$W/P1/output`:

```
# Step 1 (no lease)
grep -n ghidra_output $W/P1/ssx3.toml                        # sweep CSV is the live map
wc -l $W/P1/ssx3-functions.sweep.csv                         # 9271 = header + 9270
grep 395 region rows; ls $O | grep -i 395C70/CF0/C38/C68/D28 # 0x395c70 file present, 4 absent
grep -c 395c70/cf0/c38/c68/d28 $O/register_functions.cpp     # 1/0/0/0/0
python3 ELF words T-12..T+4 x4 + T=0x395c70                   # boundary table
grep -ci "case 0x<T>u|label_<T>" enclosing files x4          # 0 each (no collision)
cp -X sweep.csv sweep.csv.p1l-orig                           # backup
python3 replace 2 rows -> 6 rows (LF, sizes rechecked)       # 9275 lines = header + 9274
python3 sortedness/dup audit (dup 0x42c1f0 x2 pre-existing)  # edit introduces no dup
find $W/P1 -maxdepth 1 -name '._*' -delete
# Step 2 (no lease)
./bin/ps2_recomp ssx3.toml | tee recomp-p1l.log              # CWD $W/P1, exit 0
grep discovered/processed/recompiled/stubs/decode/unhandled/entrypoints/warnings
ls new sub_*.cpp x4; grep -n reg lines (352206/07/09/10)
cp -X $O/*.{cpp,h} -> runner/; sidecar purges; diff -rq clean # 9273 -> 9277
cmake -S $W/PS2Recomp -B /tmp/p1-link/runtime (P2 flags) | tee configure-runtime-p1l.log  # exit 0
cmake --build /tmp/p1-link/runtime --target ps2EntryRunner ps2x_tests -j4 | tee build-runtime-p1l.log  # 534 targets, exit 0
shasum -a 256 (both binaries)
cd $R && ps2x_tests (x3; 3rd tee $W/P1/ps2x-tests-p1l.log)   # 425/424/1, same single failure
nm/strings runner-symbol checks on ps2x_tests (0 hits)       # test/runner independence
# Step 3 (lease protocol)
cat /tmp/ssx3-host-lease (M6 at start; absent 03:39 UTC); pgrep (none)
printf 'P1l\n' > /tmp/ssx3-host-lease (04:01:07 UTC)
python3 /tmp/p1l-boot1.py (CWD $W/P1/run, p1k env + 0x1ffe000, 90 s, SIGTERM rc=-15)
rm -f /tmp/ssx3-host-lease; ls (absent 04:02:38 UTC)
log greps: missing-target 0; thread census; watch census; syscall/stub comms;
  run:tick/gs: sweep over p1b..p1k logs (all 0); prologue frame greps; pgrep (none)
# Step 4
(edit_file append Part 13; commit below)
git -C /Users/bradrichardson/dev/ssx3 add -f local/research/P1/REPORT.md
git -C /Users/bradrichardson/dev/ssx3 commit -m "[P1l] ..." (two trailers; NO push there)
git -C $W/PS2Recomp push fork ssx3 (up-to-date check; the only push allowed)
```

Env delta vs boot-p1k-1: `+0x1ffe000` in `PS2X_DIAG_WATCH` (11 addrs) only. Plus the
fresh-build confound (§P13-6): same sources, same flags, new build dir.

## P13-6. What I could not do

- Name the live outer caller of `sub_003DD1D8`: the w4 `0x1ffe000` watch missed again
  (15 pre-park `sq` clears, 0 `pc=0x3dd1e0`), as did `0x1ffe010` (0 `pc=0x3dd214`, same as p1k).
  The P12 `sd`-path theory is now insufficient (the `sw` is covered yet also missed), and the
  derivation audit (§P13-3) confirms the addrs are arithmetically correct for the observed park —
  so the open question is the miss mechanism, not the addr. 8 candidates stand (P12-1d).
- Explain the ~4× wall-clock execution rate (scheduled ~300→~75, steady stub ~2.75M→~0.69M,
  watch 32,077→7,942, all per equal 90 s / 17 blocks): candidates include shared-host contention
  (M6 holds no boot lease during my boot but builds are unleased), post-build thermal state
  (boot ran 5 min after a `-j4` full build), and fresh-build codegen differences; no host-load
  record was kept, and the brief allows one boot (no A/B).
- Attribute the stub-distinct +1 (485→486, block 0) to `0x395cf0`: the histogram prints top 30
  (cutoff 68) of 486, so a count-1 target is unprintable; the +1 is a net over unobserved churn.
- Recover what the old binary would have printed for `gs:*`/`run:tick`: all those sites are
  `PS2_IF_AGRESSIVE_LOGS`-gated and every boot p1b→p1k shows 0 such lines, so the old build had
  aggressive logging effectively off — contradicting P2's recorded `+AGRESSIVE_LOGS=ON`
  reconfigure. The old build dir is gone with `/tmp`, so the contradiction is unresolved; the p1l
  `gs:`/`run:tick` lines are therefore a visibility delta with no p1k counterpart.
- No runtime fix (per the brief): splits + ladder only. Thread 1 did not advance to a new park
  (still the driver/`SYNCTASK_run` loop), so no further fix was owed or attempted.

---

## Part 14 (P1m): watch-miss mechanism is frame-elsewhere; driver entered 3940x, 7 of 8 candidates never ran, Step 2 skipped

Brief `local/muse/prompts/P1m.md`. Miss mechanism only; no runtime fix. Tables, no verdicts.
P6: driver `0x3dd1d8` has no row (P12 absence list, unchanged) → `sub_*` below; only
candidate #8 has a P6 row (`0x3df9d8 ASYNCFILE_release`, P12).

## P14-0. Lease record

| Event | Value |
|---|---|
| Lease at session start | `M7` (foreign; shared-host lease, M7 agent active) |
| Step 1 (coverage + census + frames) | No lease (closed logs + sources only, no boot, no build) |
| Step 2 | Skipped per Step 1d (mechanism from closed sources; 0 boots, no lease needed) |
| Poll loops / waits | None (no boot attempted, nothing to poll for; `$W/P1/run/p1m-waits.log` does not exist) |
| Lease at session end | `M7` (foreign, left untouched; never overwritten, never forced) |
| Leases held by P1m | None (nothing to remove) |
| `adb` | Not used |

## P14-1. Coverage audit + entry census + frame table (Step 1, no lease, no boot)

### a. Watchpoint coverage audit (which store paths fire `PS2X_DIAG_WATCH`)

`R=$W/PS2Recomp`. Overlap test `ps2_runtime.cpp:1202`
(`writeAddr < w+8 && w < writeAddr+width`); each watch entry covers `[w,w+8)`.

| # | Store path (guest op → emitted code) | Fires | File:line |
|---|---|---|---|
| 1 | `sb` dynamic → `WRITE8` (report before segment check) | fires | `ps2_runtime_macros.h:356` (report `:361`) |
| 2 | `sh` dynamic → `WRITE16` | fires | `ps2_runtime_macros.h:372` (report `:377`) |
| 3 | `sw`/`swc1` dynamic → `WRITE32`; driver `sw $a0,0($sp)` at `0x3dd1e0` uses this | fires | `ps2_runtime_macros.h:388` (report `:393`); driver `sub_003DD1D8_0x3dd1d8.cpp:39` |
| 4 | `sd` dynamic → `WRITE64`; driver `sd $ra,0x10($sp)` at `0x3dd214` uses this | fires | `ps2_runtime_macros.h:404` (report `:409`); driver `:78` |
| 5 | `sq`/`sqc2`/`sdc2` dynamic → `WRITE128` (pre-park `sq` clears observed, P13-3) | fires | `ps2_runtime_macros.h:420` (report `:427`) |
| 6 | `Store8/16/32/64/128` (const special/MMIO target, `runtime->Store*`) | fires | `ps2_runtime.cpp:2296/2313/2330/2348/2365` (reports `:2301/2318/2335/2353/2372`) |
| 7 | Special-addr via `WRITE*` (report) then `Store*` (report again) | fires twice | `ps2_runtime_macros.h:393-396` + `ps2_runtime.cpp:2333-2335`; stack is non-special → single fire, N/A to miss |
| 8 | Const non-special addr → `genFastWrite` → `FAST_WRITE*` (trace only, no watch call); 138 files in `$O`, e.g. `sub_0013FB20` `swc1` to `0x4A5E70` | never-fires | `instruction_translator.cpp:42-63` (gen), `:119` (const call site); driver uses no `FAST_WRITE` |
| 9 | `swl`/`swr`/`sdl`/`sdr` (aligned read-modify-write via `genRead`+`genWrite`) | fires if dynamic, never if const | `instruction_translator.cpp:295/307/319/331` |
| 10 | `sc` (conditional `WRITE32` on `llbit` match, else no write) | fires if taken | `instruction_translator.cpp:352-359` |
| 11 | `sb`/`sh` const non-special → `FAST_WRITE8/16` (same const split as #8) | never-fires | `instruction_translator.cpp:198/200` via `:105-119` |
| 12 | HLE direct (`getMemPtr` + `memcpy`/`memset`, e.g. `sceCdGetToc` 1024 B clear) | never-fires | `Stubs/CD.cpp:479-481` (example; P7-6 class) |
| 13 | Scheduler `writeGuestU32` (report then `memcpy`) | fires | `EeScheduler.cpp:2290` (report), `:2292` (write) |
| 14 | `setVSyncFlag` tick zero (init path) | fires | `EeScheduler.cpp:1587` (report), `:1589` (write) |
| 15 | Steady-state vsync tick update (`memcpy`, no watch) | never-fires | `EeScheduler.cpp:2168` |
| 16 | KSEG-aliased write (`0x80000000+`) vs KUSEG watch (raw `vaddr` compare, no normalization) | never-fires (no match) | `ps2_runtime.cpp:1202`; driver sp is KUSEG (`0x1f…`), N/A |
| 17 | Cached vs uncached segment (`WRITE*` reports before `isSpecialAddress`) | fires (segment-independent) | `ps2_runtime_macros.h:393-395`; `ps2_address.h:53`; `ps2_runtime.h:442` |

Driver `sw`/`sd` take FIRES paths (#3/#4, dynamic `WRITE32`/`WRITE64`); no never-fire
path covers them. The P12 `sd`-path theory is excluded by source (#4 fires; P7-1
observed `width=8` at `pc=0x3dcc08`).

### b. Driver-entry census (`0x3dd1d8` per-period, not once)

Trace `$W/P1/run/ps2_log.txt` is p1l-only (2.1 GB, 72,315,942 lines, Sep 19 00:02);
p1k ran the old binary with no tracker (no p1k trace exists).

| Item | p1l | p1k |
|---|---|---|
| `>> sub_003DD1D8` enters / `<<` exits | 3940 / 3939 (deficit 1 = live frame at termination) | no trace |
| First enter / first exit (trace lines) | 18930 (nested under `003DED50`) / 42491 | — |
| Last enter (trace lines, total 72315942) | 72315349 (depth 0, no guest parent) | — |
| Rate over 90 s | ~44/s (per-period re-entry, not once-at-setup) | — |
| Stub-histogram `target=0x3dd1d8` hits | 0 (all 17 blocks; top-30 truncation does not explain: 44/s ≈ 220/block exceeds p1l cutoff 68) | 0 (all 17 blocks) |
| `0x3e5928`/`0x3e5440` every block, `firstRa=lastRa=0x3dd290`/`0x3dd280` | yes (driver live in steady state) | yes (P13-3) |
| `pc=0x3dd1e0` / `pc=0x3dd214` anywhere in boot log | 0 / 0 | 0 / 0 (P13-3) |
| Watch lines with `pc=0x3dd*` | 0 of 7,942 | 0 of 32,077 |

Dispatch note (why 0 stub hits with 3940 enters): every guest call goes through
`dispatchGuestBranch` (`ps2_runtime.cpp:1544-1626`), which records the histogram
(`:1590-1605`) then calls `targetFn` directly (nested). On `checkpointDue` it
returns false before both (caller unwinds; central loop dispatches at depth 0,
uncounted). The 3939 sibling (depth-0) enters are checkpointed calls/resumes;
only the first enter nests (non-checkpointed direct call).

### c. Frame placement (sp at driver entry vs park sp `0x1fffd80`)

Run frame `0x80` (`sub_003E5928_0x3e5928.cpp:112` `-0x80`; loop head `0x3e5980`
after alloc, no further allocs per P13-3). Park `0x1fffd80` + `0x80` =
watched driver frame `0x1ffe000` (`sw`) / `0x1ffe010` (`sd`), same derivation
as P13-3. Each candidate has a single prologue alloc and no further `sp`
write before its `jal` (verified per file). `entry_sp` = candidate's entry
`sp` (unknown absolute); `sp@jal` = `entry_sp − alloc`;
driver frame = `sp@jal − 0x80`.

| # | Site | File (= sweep start) | Alloc | `sp@jal` | Driver frame | `entry_sp` for watched frame | Trace enters | Places watched frame |
|---|---|---|---|---|---|---|---|---|
| 1 | `0x3dec20` | `sub_003DEBF0` | `0x40` | entry−`0x40` | entry−`0xC0` | `0x1ffe0c0` | 0 | no (never entered) |
| 2 | `0x3debc0` | `sub_003DEB50` | `0x40` | entry−`0x40` | entry−`0xC0` | `0x1ffe0c0` | 0 | no (never entered) |
| 3 | `0x3decc8` | `sub_003DECA0` | `0x30` | entry−`0x30` | entry−`0xB0` | `0x1ffe0b0` | 0 | no (never entered) |
| 4 | `0x3dee40` | `sub_003DEE18` | `0x30` | entry−`0x30` | entry−`0xB0` | `0x1ffe0b0` | 0 | no (never entered) |
| 5 | `0x3dede8` | `sub_003DEDC0` | `0x30` | entry−`0x30` | entry−`0xB0` | `0x1ffe0b0` | 0 | no (never entered) |
| 6 | `0x3ded80` | `sub_003DED50` | `0x40` | entry−`0x40` | entry−`0xC0` | `0x1ffe0c0` | 2 (called driver once, trace :18930; 0 watch hits → its frame was elsewhere) | no (elsewhere for the observed call) |
| 7 | `0x3ded20` | `sub_003DECF8` | `0x30` | entry−`0x30` | entry−`0xB0` | `0x1ffe0b0` | 0 | no (never entered) |
| 8 | `0x3dfa5c` | `sub_003DF9D8` | `0x60` | entry−`0x60` | entry−`0xE0` | `0x1ffe0e0` | 0 | no (never entered) |
| live | (3940th enter, trace :72315349) | caller unknown (depth 0, no guest parent; `003DED50` exited at :42492, long before end) | — | unknown | unknown (0 hits → not watched) | — | 1 (no exit) | no (missed) |

All 8 direct-`jal` sites confirmed as `dispatchGuestBranch(…,0x3DD1D8u,…DirectCall…)`
(one line each, `sub_003D*.cpp:89-268`); no other direct refs to `3dd1d8` exist
in `$O` (case-insensitive grep over `*.cpp`: 8 caller files + driver + headers
+ `register_functions.cpp` only). The 3939 non-`003DED50` enters therefore come
from checkpointed/indirect dispatch, not the 8 direct sites.

### d. Step-1d statement + designed Step-2 receipt (not run)

| Item | Value |
|---|---|
| Single most likely miss mechanism (Step 1d) | Frame-elsewhere: the driver's actual frames (including the live one) are not at the watched `0x1ffe000`/`0x1ffe010`; the watched addrs assume caller `sp=0x1fffe80`, but 7 candidates never ran, the 8th's one observed call wrote elsewhere (0 hits), and the live caller is unknown with unknown `sp` |
| Why not coverage | Driver `sw`/`sd` emit `WRITE32`/`WRITE64` on the dynamic (fires) path (§a #3/#4) |
| Why not entered-once-before-watch | 3940 enters over 90 s; watch env is process-lifetime (§b) |
| Step 2 skipped | Yes: mechanism determined from closed sources per Step 1d (0 hits + fires-paths + fresh enter proven by nesting at trace :18930) |
| Designed ONE receipt (for a future brief) | Env-gated driver-entry probe in `dispatchGuestBranch` for `targetPc==0x3dd1d8`: log `[diag:driver-entry] sp ra sourcePc checkpointed` on BOTH the checkpoint path (before `return false`) and the call path (before `targetFn`), one line per fresh enter (~3940 lines); actual entry `sp` values name the true frames and the live caller via `ra`, distinguishing frame-elsewhere from any residual coverage doubt |

## P14-2. Boot + mechanism answer (Step 2 skipped)

| Item | Value |
|---|---|
| Boots | 0 (`$W/P1/run/boot-p1m-*.log`: none; Step 2 skipped per Step 1d) |
| Mechanism answer | Frame-elsewhere (§P14-1d): watched addrs are arithmetically correct for park `sp` but the driver's frames are not there — 7 of 8 direct-jal candidates never entered in 72.3M trace lines, the 8th wrote elsewhere, live caller unknown |
| Caller named | No (live caller is a depth-0 dispatch with no guest parent in trace) |
| Next receipt | Driver-entry `sp`/`ra` probe (§P14-1d) to capture actual frames + live caller |
| Standard ladder row | N/A (no boot; park/threads/CD/syscalls unchanged from boot-p1l-1 by construction) |

## P14-3. Binaries and commits

| Binary / ref | sha256 / sha | Sources / state |
|---|---|---|
| `/tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner` (current, NOT booted) | `0b38f7b68d4adb1e0ef722b1ff9d0c077631e787cd7d1c14063bdc64c7266a18` | Identical to boot-p1l-1 binary → fresh, no rebuild (no source change, no boot) |
| `PS2Recomp` branch `ssx3` HEAD | `8fad69e` | Same as P1l; worktree sole `M ps2xRuntime/src/runner/register_functions.cpp` (pre-existing generated, never added) |
| Fork commits this brief | None (diagnose only; no source, TOML, CSV, or test change) | Nothing to push from the fork clone |
| Fork push | `git push fork ssx3` from the fork clone only (up-to-date check) | Verified up-to-date; no push in `/Users/bradrichardson/dev/ssx3` (forbidden) |
| This report | `[P1m]` commit (two trailers; local only) | Sole ssx3-repo change; no `runner/`, log, or `._*` added |

## P14-4. Exact commands

From `/Users/bradrichardson/dev/ssx3` unless noted; `W=/Volumes/Extreme SSD/ps2recomp-spike`,
`O=$W/P1/output`, `R=$W/PS2Recomp`:

```
# Step 1a (no lease, no boot; sources only)
grep -n "DiagWatch|DIAG_WATCH|ps2DiagWatch" $R/ps2xRuntime/src/lib/ps2_runtime.cpp
sed -n '1130,1290p;2280,2385p' $R/ps2xRuntime/src/lib/ps2_runtime.cpp   # parse/emit/Store hooks
sed -n '300,440p' $R/ps2xRuntime/include/ps2_runtime_macros.h           # WRITE*/FAST_* macros
sed -n '1,120p;120,200p;200,360p' $R/ps2xRecomp/src/lib/instruction_translator.cpp  # genFastWrite, SB/SW/SD/SQ/SWL/SWR/SDL/SDR/SC
cat $R/ps2xRuntime/include/runtime/ps2_address.h                        # KSEG/special map
grep -rn "FAST_WRITE" $O --include="*.cpp" -l | wc -l                   # 138 const-addr files
grep -n "WRITE|FAST_WRITE|Store" $O/sub_003DD1D8_0x3dd1d8.cpp           # driver :39 WRITE32, :78 WRITE64
grep -rn "getMemPtr|m_memory.write" $R/ps2xRuntime/src/lib/Kernel/ | head  # HLE uncovered class
sed -n '2267,2300p;1563,1600p;2160,2172p' $R/ps2xRuntime/src/lib/Kernel/EeScheduler.cpp  # writeGuestU32/vsync covered+uncovered
sed -n '1544,1626p;1090,1136p' $R/ps2xRuntime/src/lib/ps2_runtime.cpp   # dispatchGuestBranch + stub histogram
# Step 1b (closed logs only)
grep -c "diag:stub" $W/P1/run/boot-p1l-1.log                            # 335
grep "diag:stub" $W/P1/run/boot-p1l-1.log | grep -E "target=0x3dd1d8|target=0x3e5928|target=0x3e5440"
grep -c "3dd1d8" $W/P1/run/boot-p1l-1.log $W/P1/run/boot-p1k-1.log       # 0 / 0
grep -c ">> sub_003DD1D8" $W/P1/run/ps2_log.txt                         # 3940 enters
grep -c "<< sub_003DD1D8" $W/P1/run/ps2_log.txt                         # 3939 exits
grep -n ">> sub_003DD1D8" $W/P1/run/ps2_log.txt | head/tail             # :18930 first, :72315349 last
sed -n '42480,42510p' $W/P1/run/ps2_log.txt                             # sibling (depth-0) context
grep -c "diag:watch.*addr=0x1ffe000|addr=0x1ffe010" boot-p1l-1.log      # 15 / 15 (all sq clears)
grep -c "diag:watch.*pc=0x3dd" $W/P1/run/boot-p1l-1.log                 # 0
# Step 1c (sources + trace)
grep -rn "dispatchGuestBranch.*0x3DD1D8" $O --include="*.cpp"           # 8 direct-jal lines
grep -n "addiu.*sp" $O/sub_003D*.cpp (8 files) $O/sub_003E5928_0x3e5928.cpp  # allocs 0x40/0x40/0x30/0x30/0x30/0x40/0x30/0x60, run 0x80
for f in 003DEBF0 ... 003DF9D8; do grep -c ">> sub_${f}_" ps2_log.txt; done  # 0/0/0/0/0/2/0/0
grep -rni "3dd1d8" $O --include="*.cpp" -l                              # 8 callers + driver + headers + register only
# Step 3
cat /tmp/ssx3-host-lease                                                # M7 (foreign, untouched)
shasum -a 256 /tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner           # 0b38f7b6 (fresh)
git -C $R log --oneline -1; git -C $R status --short                    # 8fad69e + pre-existing M
(edit_file append Part 14; commit below)
git -C /Users/bradrichardson/dev/ssx3 add -f local/research/P1/REPORT.md
git -C /Users/bradrichardson/dev/ssx3 commit -m "[P1m] ..." (two trailers; NO push there)
git -C $R push fork ssx3 (up-to-date check; the only push allowed)
```

Env delta vs boot-p1l-1: none (no boot). Source delta: none (no commit).

## P14-5. What I could not do

- Name the live outer caller of `sub_003DD1D8`: it enters at trace :72315349 as a
  depth-0 dispatch with no guest parent; the 8 direct-jal candidates are excluded
  for the live invocation (7 × 0 enters, `003DED50` exited at :42492). The 3939
  sibling enters come from checkpointed/indirect dispatch, whose call-site `sp`
  is not in closed logs.
- Capture actual driver-entry `sp` values (the true frames): requires the §P14-1d
  probe (a `Diag:` commit + rebuild + 1 boot); Step 2 was skipped per Step 1d
  since the frame-elsewhere mechanism is already determined (0 hits on fires-paths
  + fresh enter proven by nesting).
- Distinguish fresh (prologue runs, frame written) vs resume (prologue skipped)
  among the 3940 enters: the trace logs function names only (no `pc`/regs); at
  least 1 fresh is proven (nested :18930); the rest are consistent with either.
- Explain the exact park-sp derivation error (park `0x1fffd80` + `0x80` is
  arithmetically watched, yet 0 hits): the live frame's true `sp` is unknown
  without the probe, so which derivation premise fails (run frame, park sampling,
  or caller chain) is open.
- No boot this brief (Step 2 skipped): no new ladder row, no `boot-p1m-*.log`,
  no revisit of the P13-6 ~4× rate question or the stub-distinct +1.
- No runtime fix (per the brief): miss mechanism only. The `*(entry+8)`
  driver-flag writer and sema-26 non-delivery remain out of scope, untouched.

---

## Part 15 (P1n): probe fires once — fresh caller is 0x3ded80, 4037 steady-state enters are scheduler resumes

Brief `local/muse/prompts/P1n.md`. Probe + caller only; no runtime fix. Tables, no verdicts.

## P15-0. Lease record

| Event | Value |
|---|---|
| Lease at session start | Absent (`/tmp/ssx3-host-lease` missing, 11:31:57 UTC) |
| Step 1 + rebuild + tests | No lease (source edit, commit, push, `-j4` build, tests need none) |
| Pre-boot checks (11:35:11 UTC) | Lease absent; `pgrep -f ps2EntryRunner` exit 1 (none); binary `7a7d4b64` fresh (just built); ISO (2.8 GB) + ELF (3.7 MB) present |
| Claim | `printf 'P1n\n' > /tmp/ssx3-host-lease` 11:35:18 UTC, immediately before boot-p1n-1 |
| Boot | 90 s foreground, SIGTERM rc=-15, returned 11:36:49 UTC |
| Release | `rm -f /tmp/ssx3-host-lease` 11:36:54 UTC; verified absent; `pgrep` exit 1 |
| Foreign holds (M8) | None during claim window (no poll loop ran; `$W/P1/run/p1n-waits.log` does not exist); `M8` claimed 11:43 UTC, after P1n release — left untouched |
| Leases held at end | None (P1n released 11:36:54 UTC; `M8` holds at session end) |
| `adb` | Not used |

## P15-1. Probe diff + build + tests

### a. Diff (one commit, one file, +37/−0)

`ps2xRuntime/src/lib/ps2_runtime.cpp` only (`R=$W/PS2Recomp`):

| Line | Code |
|---|---|
| 1385–1395 | `diagDriverProbeEnabled()`: cached `PS2X_DIAG_DRIVER_PROBE=1` check (`env[0]=='1' && env[1]=='\0'`), same shape as `diagReportAll()` |
| 1397–1404 | `diagDriverEntryEmit(sp, ra, sourcePc, checkpointed)`: prints `[diag:driver-entry] sp=0x… ra=0x… sourcePc=0x… checkpointed=0/1` |
| 1582–1586 | Checkpoint arm: inside `checkpointDue` block, before `return false`, `if (targetPc == 0x3DD1D8u && …)` → emit `checkpointed=1` |
| 1642–1646 | Call arm: after the stub histogram, before `lookupFunction(targetPc)`/`targetFn(…)` → emit `checkpointed=0` |

`sp`/`ra` = `getRegU32(ctx, 29/31)` at dispatch; `sourcePc` = dispatch arg. Default off (one bool check per dispatch to `0x3dd1d8`).

| Item | Value |
|---|---|
| Commit | `e73e36a83bd962ac28daa0198b7de50c930f2924` `Diag: P1n driver-entry probe for 0x3dd1d8 (P14-1d)` (two trailers) |
| Push | `git push fork ssx3` from fork clone only: `8fad69e..e73e36a ssx3 -> ssx3`, exit 0 |
| Worktree after | Sole `M ps2xRuntime/src/runner/register_functions.cpp` (pre-existing generated, never added) |

### b. Rebuild (no lease, `-j4`)

| Item | Value |
|---|---|
| Build | `cmake --build /tmp/p1-link/runtime --target ps2EntryRunner ps2x_tests -j4`, exit 0 (incremental, 5 steps) |
| `ps2EntryRunner` sha256 | `7a7d4b645094d3ad82746a7d420b223422bf6444e5d06f6e56998e9057f5b4cd` (163,329,504 B) |
| `ps2x_tests` sha256 | `c72bf50f139d60946f656adaae08f50cd81d39e3a39c92ea7bc6f26097f0e4cb` |

### c. Test receipts (`ps2x_tests`, CWD fork root; full log `$W/P1/ps2x-tests-p1n.log`)

| Run | Total | Passed | Failed |
|---|---|---|---|
| Probe tree (`e73e36a`) | 425 | 424 | 1: `sceGsSyncVCallback runs as a scheduler invocation on its callback stack` (`callback invocation should use the reserved async stack pool`), log :526/:528 — same test + assertion + lines as P1l (`ps2x-tests-p1l.log` :526/:528) |

Not fixed (per the brief).

## P15-2. Boot + caller answer

Boot-p1n-1: `$W/P1/run/boot-p1n-1.log`, 9,330 lines, 873,388 B, 17 blocks, CWD `$W/P1/run`,
env = p1l env + `PS2X_DIAG_DRIVER_PROBE=1` (WATCH unchanged, 11 addrs), foreground 90 s, SIGTERM rc=-15.
Binary `7a7d4b64` (fresh; §P15-1b). Trace `$W/P1/run/ps2_log.txt` fresh (2.2 GB, 74,114,872 lines, Sep 19 07:36).

### a. Probe lines: 1 (P14-1d expected ~3940)

| Item | Value |
|---|---|
| Count | 1 (boot log :436; between `[cd:callback]` :434–435 and block-0 flush) |
| Line | `[diag:driver-entry] sp=0x1fffe80 ra=0x3ded88 sourcePc=0x3ded80 checkpointed=0` |
| Distinct `sp` | `0x1fffe80` ×1 |
| Distinct `ra` | `0x3ded88` ×1 |
| Distinct `sourcePc` | `0x3ded80` ×1 |
| `checkpointed` split | 1 × `checkpointed=0`, 0 × `checkpointed=1` |

Both probe arms were live (env on); `dispatchGuestBranch` was called with `targetPc==0x3dd1d8` exactly once in 90 s.

### b. Caller named + true frames vs watched addrs

| Item | Value |
|---|---|
| Fresh-call caller (NAMED) | `sub_003DED50` @ `0x3ded80` (P12 candidate #6), `ra=0x3ded88`, entry `sp=0x1fffe80` |
| Trace cross-check | First driver enter trace :18930, depth 1, nested under `>> sub_003DED50` :18929 (depth 0); `003DED50` enters=2 (:18623 depth-2, :18929 depth-0) |
| True frame (fresh call) | Entry `sp` `0x1fffe80` − `0x80` = base `0x1fffe00`: `sw` @ `0x1fffe00`, `sd` @ `0x1fffe10` |
| Independent `sp` | 7× `[run:tick]` `pc=0x3dd290 ra=0x3dd290 sp=0x1fffe00` (driver post-alloc `sp` at the run-call fallthrough) |
| Park chain | `sp` `0x1fffd80` @ `0x3e5980` = `0x1fffe00`−`0x80` (run post-alloc); blk4 `sp` `0x1fffe00` @ `0x3dd278` (driver post-alloc) |
| Watched addrs | `0x1ffe000` / `0x1ffe010` (15 + 15 lines, all pre-park `sq` zeros, `pc=0x3e65dc`/`0x3e65b0`; 0 `pc=0x3dd1e0`/`0x3dd214`; 0 `pc=0x3dd*` of 8,134) |
| True − watched | `0x1fffe00` − `0x1ffe000` = `0x1e00` (both `sw` and `sd` addrs) |
| P13-3 equation recomputed | `0x1fffd80+0x80` = `0x1fffe00` (true frame base); P13-3 wrote `0x1ffe000` |
| Park `sp` every boot | p1k 15× / p1l 14× / p1n 16× `0x1fffd80` (+ `0x1fffe00`/`0x1fffde0` at other sampled pcs; §P15-2e) |

### c. Residue: the other 4037 enters (no guest caller; scheduler resumes)

| Item | Value |
|---|---|
| Trace enters/exits | Driver 4038/4037 (deficit 1 = live frame); run `003E5928` 12341879/12341878; `003E5440` 12338277/12338277; `003E5398` 0/0 |
| Last driver enter | Trace :74107619, depth 0 (no guest parent), after `<< sub_0031AAF0`; same shape as p1l :72315349 |
| Fresh vs resume (P14-5 open question) | 1 fresh (probed call; prologue runs) + 4037 resumes (prologue skipped); trace `>>` fires for both (`PS_LOG_ENTRY` precedes the resume switch) |

Resume path sites (sources + generated):

| Step | Site |
|---|---|
| Backward edge sets `ctx->pc=<loop head>`, `if (eeCheckpointDue()) return;` | Driver `sub_003DD1D8_0x3dd1d8.cpp:331` (`0x3dd278`); run `:396` (`0x3e5980`), `:635` |
| Unwind: `if (!dispatchGuestBranch(…)) return;` | Driver `:193` (`0x3e5440`), `:218` (`0x3e5928`), `:250` (`0x3e5398`); run `:339` |
| `dispatchGuestBranch` returns false (`ctx->pc` ≠ entry, ≠ fallthrough) | `ps2_runtime.cpp:1649-1664` region (post-`targetFn` checks) |
| Scheduler catches, loops, re-dispatches at `context.pc` | `EeScheduler.cpp:562` (`catch EeDispatcherTransfer`), `:543` `lookupFunction(context.pc)`, `:558` `function(…)` — no `dispatchGuestBranch`, no probe |
| Table maps loop heads to containing fns | `register_functions.cpp`: `0x3dd278`→`sub_003DD1D8` (slot 750748); `0x3e5980`→`sub_003E5928` (slot 759390) |
| Resume switch skips prologue | Driver `:21-27` (`0x3dd278/0x3dd280/0x3dd290/0x3dd2a0`); run `:22+` (`0x3e5928…0x3e5980…`); trace entry `:18` before switch |

### d. Watch per-addr census (p1l → p1n)

| addr + width | p1l | p1n |
|---|---|---|
| `0x51eda4` w4 (busy) / `0x51edb4` w4 | 2630 / 2629 | 2694 / 2693 |
| `0x51eda0` w4 / `0x51edb0` w4 (next-tick `pc=0x3e59d4`) | 1316 / 1315 | 1348 / 1347 |
| `0x1ffe000` w16 / `0x1ffe010` w16 (pre-park `sq` zeros) | 15 / 15 | 15 / 15 |
| One-timers (`0x519c40` w16, `0x519c48` w8, `0x519c4c` w4, `0x519c50` w16+w4×2+w8, `0x51ed90` w16, `0x51ed98` w4×3, `0x51ed9c` w4×2, `0x51eda0` w16×2, `0x51eda8` w4, `0x51edac` w4, `0x51edb0` w16×2, `0x51edc0` w16×2, `0x51edd0` w16) | 1/1/1/1+2+1, 1/3/2/2, 1/1/2, 2/1 | Identical counts |
| Total | 7,942 | 8,134 (+192, steady-state only) |

### e. Ladder delta vs boot-p1l-1

| Rung | boot-p1l-1 (9,137 lines, 855,709 B) | boot-p1n-1 (9,330 lines, 873,388 B) | Delta |
|---|---|---|---|
| Thread-1 pc | `0x3e5980` ×14, `0x3e5440` ×3 | `0x3e5980` ×16, `0x3dd278` ×1 (blk4) | Same park family (per-block table below) |
| Thread-1 sp | `0x1fffd80` ×14, `0x1fffe00` ×3 | `0x1fffd80` ×16, `0x1fffe00` ×1 | Same values (pc↔sp mapping holds) |
| Missing target | 0 (`395cf0`: 0 hits) | 0 (`missing`/`No exact`: 0; `395cf0`: 0) | None |
| Stub distinct b0 / b1–16 | 486 / 18 | 486 / 18 | None |
| Syscall distinct b0 / b1+ | 27 / 3 | 27 / 3; printed id sets identical (20 ids incl `0x15`/`0x17`; comm clean) | None |
| CD callback | queued+start log:434-435 | queued+start log:434-435 | Same lines |
| Threads 2/4/5 | sema-parked 26/29/30 @ `0x423de8` | Same (ids/entries/priorities/stacks identical; blk0 ids 1–5) | None |
| VIF MPG/MSCAL | 0 | 0 | None |
| GIF/GS | `gs:gif` 2, `gs:kick` 66, `gs:reg` 122, `gs:prim` 33, `gs:copy-reg` 8; first kick log:216 | 2 / 66 / 122 / 33 / 8; first kick log:216 (`idx=0 drawing=1 prim=6 vtxCount=1`) | None (all counts + line equal) |
| `run:tick` | 7 (ticks 120–840) | 7 | None |
| Presented frame | None (raylib line only) | None (sole `frame` hit = raylib line) | None |
| Crash | 0 | 0 | None |
| Dormant / StartThread | 40 / 4 (ids 2,3,4,5) | 40 / 4 (ids 2,3,4,5; same addrs) | None |
| Literal `dispatch` lines | 0 | 0 | None |
| Slot fills | fn `0x3e4000`/`0x0`/`0x31ad20`, writers `0x3e4458`/`0x31af4c`(del)/`0x31af60`, init next `0x28` | Byte-identical 3 lines (same pcs/ras/sps); init next `0x28` | None |
| Slot next last | `0x54b` (1316 ticks) | `0x56b` (1348 ticks; +32 ticks = +`0x20`) | Tick count |
| `*(0x519C4C)` | `0x1a` (`pc=0x3e43fc ra=0x3e43c4`) | `0x1a` (same pc/ra/sp) | None |

Per-block table (17 blocks; `sch` = id1/id4 `scheduled`; `stub` = `target=0x423c90` count):

| blk | p1l pc | p1l sch | p1l stub | p1n pc | p1n sch | p1n stub |
|---|---|---|---|---|---|---|
| 0 | `0x3e5440` | 78/54 | 484849 | `0x3e5980` | 83/59 | 535656 |
| 1 | `0x3e5440` | 79/79 | 722340 | `0x3e5980` | 80/80 | 725335 |
| 2 | `0x3e5980` | 74/74 | 679267 | `0x3e5980` | 80/80 | 730612 |
| 3 | `0x3e5980` | 73/73 | 664939 | `0x3e5980` | 80/80 | 733844 |
| 4 | `0x3e5980` | 71/71 | 651414 | `0x3dd278` | 68/68 | 620570 |
| 5 | `0x3e5980` | 72/72 | 657899 | `0x3e5980` | 81/81 | 736170 |
| 6 | `0x3e5440` | 62/62 | 563060 | `0x3e5980` | 79/79 | 724123 |
| 7 | `0x3e5980` | 78/78 | 712451 | `0x3e5980` | 74/74 | 682261 |
| 8 | `0x3e5980` | 80/80 | 733748 | `0x3e5980` | 78/78 | 709438 |
| 9 | `0x3e5980` | 79/79 | 724724 | `0x3e5980` | 77/77 | 703159 |
| 10 | `0x3e5980` | 75/75 | 687329 | `0x3e5980` | 68/68 | 619512 |
| 11 | `0x3e5980` | 77/77 | 705702 | `0x3e5980` | 81/81 | 738237 |
| 12 | `0x3e5980` | 68/68 | 615412 | `0x3e5980` | 81/81 | 737659 |
| 13 | `0x3e5980` | 79/79 | 726712 | `0x3e5980` | 80/80 | 734618 |
| 14 | `0x3e5980` | 80/80 | 729929 | `0x3e5980` | 78/78 | 718217 |
| 15 | `0x3e5980` | 80/80 | 731936 | `0x3e5980` | 77/77 | 706211 |
| 16 | `0x3e5980` | 79/79 | 717806 | `0x3e5980` | 69/69 | 617855 |

Rate rows (p1l → p1n): `scheduled` ~75 → ~77; steady stub ~0.69M → ~0.70M; watch 7,942 → 8,134. Same regime.

Block-0 stub comm (32 printed lines each): 23 byte-identical; 9 differ in `count` only (same `firstRa`/`lastRa`,
incl `0x3e5928`/`0x3e5440`/`0x423c90` recurring); 1 cutoff swap (`0x412500` count=68 in p1l vs `0x4123e8`
count=68 in p1n). `firstRa=lastRa=0x3dd290` (`0x3e5928`) and `0x3dd280` (`0x3e5440`) every block, both boots.

## P15-3. Binaries and commits

| Binary / ref | sha256 / sha | Sources / state |
|---|---|---|
| `/tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner` (boot-p1n-1) | `7a7d4b645094d3ad82746a7d420b223422bf6444e5d06f6e56998e9057f5b4cd` | `e73e36a` tree + regen runner sources (unchanged since p1l) |
| `/tmp/p1-link/runtime/ps2xTest/ps2x_tests` | `c72bf50f139d60946f656adaae08f50cd81d39e3a39c92ea7bc6f26097f0e4cb` | Same tree; 424/425 (§P15-1c) |
| `PS2Recomp` branch `ssx3` HEAD | `e73e36a` | One `Diag:` commit this brief (§P15-1a); worktree sole `M` = pre-existing generated `runner/register_functions.cpp`, never added |
| Fork push | `git push fork ssx3` from fork clone only (`8fad69e..e73e36a`) | Verified pushed; no push in `/Users/bradrichardson/dev/ssx3` |
| This report | `[P1n]` commit (two trailers; local only) | Sole ssx3-repo change; no `runner/`, log, or `._*` added |

## P15-4. Exact commands

From `$W/PS2Recomp` (fork) unless noted; `$W=/Volumes/Extreme SSD/ps2recomp-spike`, `$O=$W/P1/output`,
`$R=$W/PS2Recomp`, `$LOG=$W/P1/run/boot-p1n-1.log`:

```
# Step 1 (no lease)
sed -n '1544,1630p' $R/ps2xRuntime/src/lib/ps2_runtime.cpp      # dispatchGuestBranch shape
sed -n '1040,1300p' ditto; grep getenv PS2X_DIAG (x3 sites)     # diag gate patterns
(edit_file: +37 lines probe; find -name '._*' -delete)
git -C $R diff --stat; git -C $R add ps2xRuntime/src/lib/ps2_runtime.cpp
git -C $R commit -m "Diag: P1n driver-entry probe ..." (two trailers)  # e73e36a, 1 file
git -C $R push fork ssx3                                        # 8fad69e..e73e36a, exit 0
cmake --build /tmp/p1-link/runtime --target ps2EntryRunner ps2x_tests -j4  # exit 0
shasum -a 256 (both binaries)
cd $R && ps2x_tests | tee $W/P1/ps2x-tests-p1n.log              # 425/424/1, same lines 526/528
# Step 2 (lease protocol)
cat /tmp/ssx3-host-lease (absent); pgrep -f ps2EntryRunner (none)
shasum ps2EntryRunner (7a7d4b64 fresh); ls ISO + ELF
printf 'P1n\n' > /tmp/ssx3-host-lease (11:35:18 UTC)
python3 /tmp/p1n-boot1.py (CWD $W/P1/run, p1l env + PROBE=1, 90 s, SIGTERM rc=-15)
rm -f /tmp/ssx3-host-lease; ls (absent 11:36:54 UTC); pgrep (none)
log greps: driver-entry 1 (:436); watch census; thread/stub/syscall comms;
  gs:/run:tick/frame/crash/dormant/missing-target sweeps; slot fills
trace greps: enters 4038/12341879/12338277/0/2; sed :18920-18935, :74107610-74107625
source greps: lookupFunction callers (2); table slots 750748/759390; resume switches
python3 hex recompute (0x1fffd80+0x80 = 0x1fffe00)
# Step 3
(edit_file append Part 15; commit below)
git -C /Users/bradrichardson/dev/ssx3 add -f local/research/P1/REPORT.md
git -C /Users/bradrichardson/dev/ssx3 commit -m "[P1n] ..." (two trailers; NO push there)
```

Env delta vs boot-p1l-1: `+PS2X_DIAG_DRIVER_PROBE=1` only. Source delta: §P15-1a only.

## P15-5. What I could not do

- Capture steady-state driver-entry `sp` values: the 4037 resumes bypass `dispatchGuestBranch`
  (§P15-2c), so the P14-1d probe is blind there by construction; a scheduler-loop probe
  (`EeScheduler.cpp:543/558`) would be a new `Diag:` commit, outside this brief — not implemented.
- Re-census the 8 direct-jal candidates in the p1n trace: unnecessary — the probe is exhaustive
  for the guest-call path (both arms live, env on), and exactly 1 guest call occurred.
- No runtime fix (per the brief): probe + caller only. The `*(entry+8)` driver-flag writer and
  sema-26 non-delivery remain out of scope, untouched.
- No new data on the P13-6 ~4× rate question (p1n runs at the p1l rate, ~77 scheduled/block)
  or the stub-distinct +1 (p1n b0 distinct is also 486; top-30 truncation unchanged).
- One boot only (per the brief): no A/B on any rung.

---

## Part 16 (P1o): true-frame hits land (caller saga CLOSED) + driver-flag writers named statically (3DE420/3DD7E0/3DDC30)

Brief `local/muse/prompts/P1o.md`. Watch confirm + writer hunt; no runtime fix. Tables, no verdicts.
Stale-reading guard: Part 15 (P15-2b true frames, P13-3 hex slip, P15-2c resume path) + Part 12 §P12-1
(driver flag `*(entry+8)`, `$s1` = `*(0x519AD8)`+byte·`0x30`, P6 lead `0x3de420`) re-read before acting.

## P16-0. Lease record

| Event | Value |
|---|---|
| Lease at session start | `M8` (foreign; 11:59:17 UTC) → logged to `$W/P1/run/p1o-waits.log`; boot deferred, lease-free static work (§P16-2) + boot-script prep first |
| Poll | 12:03:06 UTC: lease absent (M8 hold gone; never overwritten) |
| Pre-boot checks (12:03:18 UTC) | `pgrep -f ps2EntryRunner` exit 1 (none); binary `7a7d4b64` fresh (matches P15-1b, no rebuild); ISO (2.8 GB) + ELF (3.7 MB) present |
| Claim | `printf 'P1o\n' > /tmp/ssx3-host-lease` 12:03:18 UTC, immediately before boot-p1o-1 |
| Boot | 90 s foreground, SIGTERM rc=-15, returned 12:05:02 UTC |
| Release | `rm -f /tmp/ssx3-host-lease` 12:05:07 UTC; verified absent; `pgrep` exit 1 |
| Waits log | `$W/P1/run/p1o-waits.log`, 2 lines (start-hold + poll/claim/boot/release) |
| Second boot | None (static named the writers; Step 2b moot) → no re-claim |
| `adb` | Not used |

## P16-1. Watch confirm (caller saga CLOSED)

Boot-p1o-1: `$W/P1/run/boot-p1o-1.log`, 9,638 lines, 906,252 B, 17 blocks, CWD `$W/P1/run`,
env = p1n env with WATCH frame addrs swapped (`0x1ffe000`→`0x1fffe00`, `0x1ffe010`→`0x1fffe10`;
other 9 addrs unchanged; 11 total), `PS2X_DIAG_DRIVER_PROBE=1` kept on. Binary `7a7d4b64` (fresh; §P16-3).

### a. Expectation (machine-checked)

`python3 -c "print(hex(0x1fffe80-0x80), hex(0x1fffe00+0x10), hex(0x1fffe00-0x1ffe000))"`
→ `0x1fffe00 0x1fffe10 0x1e00`: entry `sp` `0x1fffe80`−`0x80` = `sw` addr `0x1fffe00`
(`0x3dd1e0`), +`0x10` = `sd` addr `0x1fffe10` (`0x3dd214`); `0x1e00` above the p1l/p1n watches.

### b. Probe line: 1 (same bytes as P15-2a)

| Item | Value |
|---|---|
| Count | 1 (boot log :687; between `[cd:callback]` :685–686 and block-0 flush, same position as p1n :434–436, shifted by frame-watch volume) |
| Line | `[diag:driver-entry] sp=0x1fffe80 ra=0x3ded88 sourcePc=0x3ded80 checkpointed=0` |
| Delta vs p1n :436 | Line number only; `sp`/`ra`/`sourcePc`/`checkpointed` byte-identical |

### c. True-frame hits: exactly 1 each (expectation met)

| Line | addr + width | value | pc | ra | sp |
|---|---|---|---|---|---|
| :688 | `0x1fffe00` w4 | `0x900001` (= `$a0`; top byte `0x00` → entry 0; §P16-2b) | `0x3dd1e0` | `0x3ded88` | `0x1fffe00` |
| :689 | `0x1fffe10` w8 | `0x3ded88` (= `$ra`) | `0x3dd214` | `0x3ded88` | `0x1fffe00` |

`pc=0x3dd1e0` / `pc=0x3dd214` counts anywhere in log: 1 / 1. The caller saga is CLOSED:
fresh caller `0x3ded80` (#6) writes its prologue frame exactly at the P15-2b true addrs.

### d. Frame-addr reuse (pre-probe stack traffic; 0 lines after :689)

| addr | Lines | Width split | pc-prefix split | Last pre-probe | Post-:689 |
|---|---|---|---|---|---|
| `0x1fffe00` | 164 | 84×w16 / 38×w4 / 42×w8 | — (joint below) | :680 (`pc=0x3dcf8c ra=0x3ddbd8 sp=0x1fffdf0`) | 0 |
| `0x1fffe10` | 95 | 67×w16 / 14×w4 / 14×w8 | — | :675 (`pc=0x3ddaf0 ra=0x3ded74 sp=0x1fffe10`, fresh-call chain) | 0 |
| Joint 259 | 164+95 | 151×w16 / 52×w4 / 56×w8 | 107×`0x2*` / 135×`0x3*` / 17×`0x4*` | :680 | 0 |

All 259 lines are :60–:680 (early-boot stack reuse through the same addrs); nothing touches the
true frame after the driver prologue runs — consistent with the park (`sp` `0x1fffd80`) never
returning up. (p1n frame addrs: 15 + 15 pre-park `sq` zeros.)

### e. Watch per-addr census (p1n → p1o)

| addr + width | p1n | p1o |
|---|---|---|
| `0x51eda4` w4 (busy) / `0x51edb4` w4 | 2694 / 2693 | 2712 / 2711 (+18/+18 = +9 ticks) |
| `0x51eda0` w4 / `0x51edb0` w4 (next-tick `pc=0x3e59d4`) | 1348 / 1347 | 1357 / 1356 (+9/+9) |
| Frame addrs (old `0x1ffe000`/`0x1ffe010` → new `0x1fffe00`/`0x1fffe10`) | 15 / 15 | 164 / 95 |
| One-timers (`0x519c40` w16, `0x519c48` w8, `0x519c4c` w4, `0x519c50` w16+w4×2+w8, `0x51ed90` w16, `0x51ed98` w4×3, `0x51ed9c` w4×2, `0x51eda0` w16×2, `0x51eda8` w4, `0x51edac` w4, `0x51edb0` w16×2, `0x51edc0` w16×2, `0x51edd0` w16) | §P15-2d counts | Identical counts (each re-grepped) |
| Total (`^` anchored; :188 shares `[SifInitRpc]`+watch on one line) | 8,134 | 8,441 (8,442 unanchored) |

### f. Ladder delta vs boot-p1n-1

| Rung | boot-p1n-1 (9,330 lines, 873,388 B) | boot-p1o-1 (9,638 lines, 906,252 B) | Delta |
|---|---|---|---|
| Thread-1 pc | `0x3e5980` ×16, `0x3dd278` ×1 (blk4) | `0x3e5980` ×16, `0x423c90` ×1 (blk11) | Same park family (per-block table below) |
| Thread-1 sp | `0x1fffd80` ×16, `0x1fffe00` ×1 | `0x1fffd80` ×16, `0x1fffde0` ×1 | pc↔sp mapping holds |
| Missing target | 0 | 0 (`missing`/`No exact`/`395cf0`: 0) | None |
| Stub distinct b0 / b1–16 | 486 / 18 | 486 / 18 | None |
| Syscall distinct b0 / b1+ | 27 / 3; 20 printed ids | 27 / 3; same 20 ids incl `0x15`/`0x17` (sort-compared) | None |
| CD callback | queued+start :434–435 | queued+start :685–686 | Same pair, later lines |
| Threads 2/4/5 | sema-parked 26/29/30 @ `0x423de8` | Same (ids/entries/priorities/stacks identical; blk0 ids 1–5) | None |
| VIF MPG/MSCAL | 0 | 0 | None |
| GIF/GS | `gs:gif` 2, `gs:kick` 66, `gs:reg` 122, `gs:prim` 33, `gs:copy-reg` 8; first kick :216 | 2 / 66 / 122 / 33 / 8; first kick :410 (same content) | Line shift only |
| `run:tick` | 7 (ticks 120–840) | 7 (same ticks/counters) | None |
| Presented frame | None (raylib line only) | None (sole `frame` hit = raylib line) | None |
| Crash | 0 | 0 | None |
| Dormant / start-thread | 40 / 4 (`diag:dormant`/`diag:start-thread`) | 40 / 4 | None |
| Literal `dispatch` lines | 0 | 0 | None |
| Slot fills | fn `0x3e4000`/`0x3e33b0`/`0x31ad20`, writers `0x3e4458`/`0x3e3050`/`0x31af60`, del `0x31af4c`, init next `0x28` | Byte-identical pcs/ras/sps/values (log :340–351); init next `0x28` | None |
| Slot next last | `0x56b` (1348 ticks) | `0x574` (1357 ticks; +9 = `0x574`−`0x56b`, check §P16-2l) | Tick count |
| `*(0x519C4C)` | `0x1a` (`pc=0x3e43fc ra=0x3e43c4 sp=0x1ffec80`) | `0x1a` (same pc/ra/sp; log :337) | None |
| SIF modules | 6 (id 1 line shares `[SifInitRpc]`) | 6, same order/paths (:192–207) | Line-merge artifact only |
| Prefix census | Not tabulated in P15 | p1o counts equal p1n on every prefix except watch total (above) + SIF line split | Compared |

Per-block table (17 blocks; `sch` = id1/id4 `scheduled`; `stub` = `target=0x423c90` count):

| blk | p1n pc | p1n sch | p1n stub | p1o pc | p1o sch | p1o stub |
|---|---|---|---|---|---|---|
| 0 | `0x3e5980` | 83/59 | 535656 | `0x3e5980` | 82/58 | 526397 |
| 1 | `0x3e5980` | 80/80 | 725335 | `0x3e5980` | 79/79 | 720012 |
| 2 | `0x3e5980` | 80/80 | 730612 | `0x3e5980` | 75/75 | 679645 |
| 3 | `0x3e5980` | 80/80 | 733844 | `0x3e5980` | 80/80 | 731297 |
| 4 | `0x3dd278` | 68/68 | 620570 | `0x3e5980` | 80/80 | 732107 |
| 5 | `0x3e5980` | 81/81 | 736170 | `0x3e5980` | 79/79 | 729072 |
| 6 | `0x3e5980` | 79/79 | 724123 | `0x3e5980` | 76/76 | 690312 |
| 7 | `0x3e5980` | 74/74 | 682261 | `0x3e5980` | 75/75 | 692411 |
| 8 | `0x3e5980` | 78/78 | 709438 | `0x3e5980` | 69/69 | 624039 |
| 9 | `0x3e5980` | 77/77 | 703159 | `0x3e5980` | 79/79 | 722822 |
| 10 | `0x3e5980` | 68/68 | 619512 | `0x3e5980` | 74/74 | 675935 |
| 11 | `0x3e5980` | 81/81 | 738237 | `0x423c90` | 78/78 | 717207 |
| 12 | `0x3e5980` | 81/81 | 737659 | `0x3e5980` | 76/76 | 693804 |
| 13 | `0x3e5980` | 80/80 | 734618 | `0x3e5980` | 76/76 | 689663 |
| 14 | `0x3e5980` | 78/78 | 718217 | `0x3e5980` | 70/70 | 637415 |
| 15 | `0x3e5980` | 77/77 | 706211 | `0x3e5980` | 79/79 | 727083 |
| 16 | `0x3e5980` | 69/69 | 617855 | `0x3e5980` | 80/80 | 729788 |

Rate rows (p1n → p1o): `scheduled` ~77 → ~77; steady stub ~0.70M → ~0.70M. Same regime.

Block-0 stub comm (30 rows each): same 30 targets; 22 byte-identical; 8 differ in `count` only
(same `firstRa`/`lastRa`: `0x326eb0`,`0x3e5440`,`0x3e5928`,`0x3ffa58`,`0x3ffbc0`,`0x423c90`,
`0x423dd0`,`0x423de0`); 0 `ra` diffs; no cutoff swap. `firstRa=lastRa=0x3dd290` (`0x3e5928`)
and `0x3dd280` (`0x3e5440`) all 17 blocks, both boots (17/17 re-grepped in p1o).

## P16-2. Flag-writer hunt (static + ELF; no second boot)

### a. Driver flag recap (sources + checks)

`sub_003DD1D8`: `$t0` = `0x52<<16` − `0x6550`; `lw $a2,0x28($t0)` → `$a2` = `*(0x519AD8)`;
`$v0` = top byte of `$a0` × `0x30`; `$s1` = `$a2`+`$v0`. Flag reads `lw $v0,8($s1)` at
`0x3dd258` (pre-check), `0x3dd2dc` + `beqz` `0x3dd2e0` (SYNCTASK-wait loop), `0x3dd2e8` (exit read).

`python3 -c "print(hex(0x520000-0x6550), hex(0x519AB0+0x28), hex(0x520000-0x6550+0x28))"`
→ `0x519ab0 0x519ad8 0x519ad8`.

### b. Parked entry index (from the :688 value)

`python3 -c "print(hex(0x574-0x56b), hex(9*0x30), hex(0x900001>>24), hex(0x900001&0xFFFFF))"`
→ `0x9 0x1b0 0x0 0x1`: slot-next delta +9 ticks (§P16-1f); `$a0` = `0x900001` top byte =
`0x00` (the check, not the hand read, rules: `0x900001` is 6 hex digits, bits 24–31 are `0x00`).

`python3 -c "print(hex(0x900001>>24), hex(0*0x30), hex(0x519AB0+0x28))"`
→ `0x0 0x0 0x519ad8`: parked byte 0 → entry offset `0x0` → the wait is on table-entry 0,
`*( *(0x519AD8) + 8 )`. Low-20 of `$a0` = `0x1` (entry+0 id-compare half).

### c. Writers to `0x519AD8` (the `$s1` base): exactly 1

| pc | Insn (ELF ✓) | Base proof | Value | Owning function | P6 |
|---|---|---|---|---|---|
| `0x3dccfc` (delay) | `sw $s3,0x28($s0)` = `0xae130028` | `$s0` = `0x520000`−`0x6550` = `0x519AB0` (`0x3dccb4`); +`0x28` = `0x519AD8` | `$s3` = `$a3` (set :73, no clobber before use; epilogue restore only) = fresh table from `sub_003DCBD8` | `sub_003DCC88` | — (no row) |

Table-source chain: `sub_003DCBD8` (sole caller: `0x31af2c` in `sub_0031ADB0` = P6 `systemInit`)
jalr-allocs (`$a0`=`0x495D28`, `$a1`=ret(`func_3DCD98`), `$a2`=`0x100`; target `*(`0x450C10`+4)`)
→ `$v0` = table; `0x3dcc50` `sw $v0,-0x6518($v1)` (`$v1`=`0x520000`) also stores it to `*(0x519AE8)`;
delay `0x3dcc60` passes `$a3`=`$v0` to `func_3DCC88`.

`python3 -c "print(hex(0x450C10+4), hex(0x520000-0x6518))"` → `0x450c14 0x519ae8`.
`python3 -c "print(hex(0x520000-0x6518), hex(0x100//0x30), hex(0x100%0x30))"` → `0x519ae8 0x5 0x10`.
ELF: `0x3dcc50` = `0xac629ae8` ✓, `0x3dccfc` = `0xae130028` ✓.

Exclusion: no `sw -0x6528` / `sw -0x652C` anywhere in `$O` (all `-0x6528` hits are `lw`);
every other `sw *,0x28($s0)` site's `$s0` ≠ `0x519AB0` (`3D11B8` `$s0`=`$a1`;
`3DF028`/`3DF690`/`3DF748`/`3E06D8` arg/return-derived; §P16-2h).

### d. Writers to `*(entry+8)` (the flag): 3

| # | pc | Insn (ELF ✓) | Entry provenance | Value | Owning function | P6 |
|---|---|---|---|---|---|---|
| W1 | `0x3de468` | `sw $v0,8($a1)` = `0xaca20008` | `$a1` = `*(0x519AB0+0x24)` = `*(0x519AD4)` (current entry; read `0x3de43c`) | −1 if `*(entry+4)`≠0 else (−2, or 1 if `$a0`≠0) | `sub_003DE420` | `iFILESYS_CommandCompleteCallback` |
| W2 | `0x3dd83c` | `sw $v0,8($s2)` = `0xae420008` | `$s2` = ret(`func_3DE670`) = table+idx·`0x30` (jal `0x3dd800`) | 1 | `sub_003DD7E0` | — (no row) |
| W3 | `0x3ddd30` | `sw $v0,8($s3)` = `0xae620008` | `$s3` = ret(`func_3DE670`) (jal `0x3ddc70`) | −2 | `sub_003DDC30` | — (no row) |

`sub_003DE670` returns table entries: scan loop `0x3de740`–`0x3de748` counts `$s1` with
`$a3`+=`0x30` delay; exit `$v0`=`0x30` (delay `0x3de764`), `mult $v0,$s1,$v0` (`0x3de788`),
`$v1` = `*(`0x519AB0`+`0x28`)` = `*(0x519AD8)` (`0x3de78c`), return `$v1`+`$v0` (`0x3de7a0`).

`python3 -c "print(hex(0x519AB0+0x10), hex(0x519AB0+0x24), hex(0x519AB0+0x28), hex(0x520000-0x519AD4))"`
→ `0x519ac0 0x519ad4 0x519ad8 0x652c`.
`python3 -c "print(hex(0x520000-0x653C), hex(0x519AC4-0x14))"` → `0x519ac4 0x519ab0`
(`3DE670` mutex/unlock path addrs). ELF: `0x3de7a0` = `0x621021` ✓.

Callers of `func_3DE670` (10 jal sites): `0x3dd458` (`3DD438`), `0x3dd510` (`3DD4E8`),
`0x3dd5c0` (`3DD5A0`), `0x3dd680`+`0x3dd758` (`3DD648`), `0x3dd758` (`3DD720` overlap),
`0x3dd800`+`0x3dd890` (`3DD7E0`), `0x3ddaf4` (`3DDAC0`), `0x3ddc70` (`3DDC30`).

W1 context (`3DE420`): `*(0x519AC0)`++ (`0x3de444`); early return if current entry null;
flag store; `*(0x519AD4)` = 0 (`0x3de470`); chained `jalr *($a1+0x28)` if set;
`*(0x519AC0)`−− (`0x3de49c`); if zero, `jal func_3DDFA8` (`0x3de4ac`, P6 `iFILESYS_ExecCommand`).

### e. Writers to `0x519AD4` (current entry): set + clear

| pc | Insn (ELF ✓) | Effect | Owning function | P6 |
|---|---|---|---|---|
| `0x3de0b0` (delay) | `sw $s1,0x24($v0)` = `0xac510024` (`$v0` = `$s4`−`0x6550`, `$s4`=`0x520000` unclobbered) | `*(0x519AD4)` = `$s1` = `$a0` request | `sub_003DDFA8` | `iFILESYS_ExecCommand` |
| `0x3de470` | `sw $zero,0x24($s0)` = `0xae000024` (`$s0`=`0x519AB0`) | `*(0x519AD4)` = 0 | `sub_003DE420` | `iFILESYS_CommandCompleteCallback` |

### f. P6 lead `0x3de420` check

| Item | Value |
|---|---|
| Exists | Yes: `sub_003DE420_0x3de420.cpp` (379 lines, 13,688 B); ELF `0x3de420` = `0x27bdffe0` ✓ |
| P6 row | `0x3de420,iFILESYS_CommandCompleteCallback,config/symbol_addrs.txt` (:735) |
| Called from (10 jal sites) | `0x3de0c8`/`0x3de2f8`/`0x3de340`/`0x3de3a4`/`0x3de3e0`/`0x3de3f4` (all in `3DDFA8`); `0x3e3450` (in `3E3350`+`3E33B0` overlap — same pc, count once); `0x3e34c0` (`3E3478`); `0x3e3d64` (`3E3B00`) |
| Near the flag | It writes the flag: W1 `0x3de468` (§P16-2d) |
| Ran in boot-p1o-1 | 0 `target=0x3de420` stub lines (absent from printed b1–16, distinct 18 each; b0 below-cutoff unobservable per P13-6); `target=0x3ddfa8` also 0 |

### g. SYNCTASK slot array (brief formula recomputed)

Brief shorthand `0x51ED98+8·slot` hits the wrong words:

`python3 -c "print([hex(0x51ED98+8*i) for i in range(4)])"`
→ `['0x51ed98', '0x51eda0', '0x51eda8', '0x51edb0']`
(= slot0-fn / slot0-next / slot0-busy / slot1-next — NOT one word across slots).

Correct (stride `0x10`, §P12-1a):

`python3 -c "print(hex(0x520000-0x1268)); print([hex(0x51ED98+8+i*0x10) for i in range(4)]); print(hex(0x51ED98+8+15*0x10), hex(0x51ED98+0x100))"`
→ `0x51ed98 ['0x51eda0', '0x51edb0', '0x51edc0', '0x51edd0'] 0x51ee90 0x51ee98`.

Writers (only 4 guest files reference `-0x1268`, re-verified — same files as P12):

| Function (P6) | Store pcs | Words |
|---|---|---|
| `SYNCTASK_init` (`0x3e57d0`, in `3E5760` file) | None inline (zeroes via `func_3E6448(0x51ED98,0,0x100)` call); nearby inline `0x3e578c`-region stores belong to `MUTEX_unlock` (`0x3e5760`) | — |
| `SYNCTASK_add` (`0x3e57f8`) | `0x3e5898` fn / `0x3e58a0` period / `0x3e58a8` next / `0x3e58b0` busy=0 | slot `i`×4 |
| `SYNCTASK_del` (`0x3e58c8`) | `0x3e591c` (delay; single word) | fn = 0 only |
| `SYNCTASK_run` (`0x3e5928`) | `0x3e59b4` busy=1 / `0x3e59cc` busy=0 / `0x3e59d4` next+=period | steady-state |

(`3E57F8` also `FAST_WRITE32(0x450E00)` + `$t5`+`0xE00` tick bookkeeping — not slots.
`python3 -c "print(hex(0x450000+3088), hex(3584), hex(3588))"` → `0x450c10 0xe00 0xe04`.)

### h. Excluded `+8` writers (base provenance ≠ entry table)

Complete census: every `sw *,0x8(` in `3DC*`–`3DF*` + the sole non-`sw` (`sh`); every
`0x24`/`0x28` store in `3DC*`–`3DF*` for the global-struct question.

| Site | Base provenance | Reason excluded |
|---|---|---|
| `3DDFA8:0x3de2bc` `sw $v0,8($a0)` | `$a0` = `*($s1+0x24)`, `$s1` = `$a0` request | Request-relative, not table/current entry (aliasing unproven) |
| `3DDFA8:0x3de338` `sw $zero,0x24($s1)` | `$s1` = `$a0` request | Clears req→`0x24`, not `0x519AD4` |
| `3DDAC0:0x3ddb9c` `sw $s4,8($s1)` | `$s1` = `jalr *($s0+4)` return (`$s0`=`$a3` arg) | Allocator-return base; no table path |
| `3DE9B8:0x3dea3c` + `:0x3dea80` | `$s1`/`$a0` = `0x450000`-based (`0x450C10`) | Different region (`0x450008`-family) |
| `3DE8C0:0x3de918` / `3DFE18:0x3dfe54` / `3DFED0:0x3dffc0` | Arg/heap-derived; 0 table refs in function | No `519AD8`/`3DE670`/`-0x6528`/`-0x651C` in file |
| `3DF028` ×4 (`0x3df1a0`-fam `+8`) | `$s0` = `0x519C08` early (→`0x519C10`, CD region) else `*($a0+16)`/`$a2`/restored; 0 table refs | `python3 -c "print(hex(0x519C08+8), hex(0x519C08+0x24), hex(0x519C08+0x28))"` → `0x519c10 0x519c2c 0x519c30` |
| `3DF690` / `3DF748` ×3 / `3E06D8` / `3D11B8` ×2 | `$s0` = `$v0`-return / `$a3` / `$a1` | Arg/return-derived; 0 table refs |
| `3DC450`(`USTR_vsprintf`):`0x3dc988` `sh $t0,8($v0)` | `$v0` small-int/return-derived; 0 table refs | Sole non-`sw` +8 store; vsprintf scratch |
| `3DD7E0:0x3dd798` + `0x3dd938` (`+0x24`) | `$s1` = `$a1`/`$a2` args; `$a1` = `*($s1+16)` | Request-relative, not `0x519AD4` |
| `0x3dcfa0`/`0x3dd498`/`0x3dd54c`/`0x3dd5fc`/`0x3dd6c4`/`0x3ddb54` (`+0x24`/`+0x28`) | Owning files have 0 `lui *,0x51` | Cannot construct `0x519AB0`; entry/request-relative |

`python3 -c "print(hex(0x520000-0x63F8), hex(4294967296-4294941704), hex(4294967296-4294941360), hex(4294967296-4294941412))"`
→ `0x519c08 0x63f8 0x6550 0x651c` (two's-complement decodes used above).
P6: `0x3dc450,USTR_vsprintf` (:732); no rows for any other §P16-2h/2d site function
(re-grepped 30 addrs, 1 hit).

### i. Neighbor writers in the `0x519AB0` struct (not the flag)

`python3 -c "print(hex(0x520000-0x6550), hex(0x520000-0x651C), hex(0x519AD8-0x519AB0))"`
→ `0x519ab0 0x519ae4 0x28`.
`python3 -c "print(hex(0x519AB0+8), hex(0x519AB0+4), hex(0x519AB0+0x14), hex(0x520000-0x6528))"`
→ `0x519ab8 0x519ab4 0x519ac4 0x519ad8`.

| pc | Effect | Owning function | P6 |
|---|---|---|---|
| `3DCC88:0x3dccdc` / `:0x3dcce0` / `:0x3dcce8`(delay) | `*(0x519AB8)`=`0xFF` / `*(0x519AB0)`=`$s1` / `*(0x519AB4)`=`$s5` (init) | `sub_003DCC88` | — |
| `3DCBD8:0x3dcc50` | `*(0x519AE8)` = table (dup of `0x519AD8`) | `sub_003DCBD8` | — |
| `3DDDF0:0x3dde20`(delay) / `:0x3dde24` | `*(0x519AB8)` = `$a2`, then restored (swap around indirect call) | `sub_003DDDF0` | `FILESYS_atomic` |
| `3DE420:0x3de444` / `:0x3de49c` | `*(0x519AC0)`++ / −− (inflight counter) | `sub_003DE420` | `iFILESYS_CommandCompleteCallback` |

Readers of `*(0x519AD8)` (`lw -0x6528`, base `0x520000`): `3DCE90` ×3 (`0x3dceec`/`0x3dcf20`/
`0x3dcf50` + `0x3dcebc`), `3DCF70:0x3dcf80`, `3DD148` ×2, `3DD310:0x3dd328`,
`3DD7E0:0x3dda20`, driver `0x3dd218` (via `$t0`+`0x28`). Readers of `*(0x519AE4)`
(`-0x651C`): `3DCD98:0x3dce00`, `3DD5A0:0x3dd5e4`, `3DDAC0:0x3ddaf8`, `3DE4D0:0x3de5dc`.

### j. ELF verification words (`SLUS_207.72`, file off = va−`0x100000`+`0x1000`)

| va | word | disasm | match |
|---|---|---|---|
| `0x3dd1e0` | `0xafa40000` | `sw $a0,0($sp)` | OK |
| `0x3dd214` | `0xffbf0010` | `sd $ra,0x10($sp)` | OK |
| `0x3de420` | `0x27bdffe0` | `addiu $sp,-0x20` | OK |
| `0x3de444` | `0xac620010` | `sw $v0,0x10($v1)` | OK |
| `0x3de468` | `0xaca20008` | `sw $v0,8($a1)` (W1) | OK |
| `0x3de470` | `0xae000024` | `sw $zero,0x24($s0)` | OK |
| `0x3de49c` | `0xae020010` | `sw $v0,0x10($s0)` | OK |
| `0x3dcc50` | `0xac629ae8` | `sw $v0,-0x6518($v1)` | OK |
| `0x3dccfc` | `0xae130028` | `sw $s3,0x28($s0)` (`0x519AD8` writer) | OK |
| `0x3de0b0` | `0xac510024` | `sw $s1,0x24($v0)` (current-entry set) | OK |
| `0x3de2bc` | `0xac820008` | `sw $v0,8($a0)` (request-relative) | OK |
| `0x3dd83c` | `0xae420008` | `sw $v0,8($s2)` (W2) | OK |
| `0x3ddd30` | `0xae620008` | `sw $v0,8($s3)` (W3) | OK |
| `0x3de7a0` | `0x00621021` | `addu $v0,$v1,$v0` (lookup return) | OK |

### k. Step 2b (not run — static succeeded)

Static named the writers (§P16-2c–2e), so no dynamic receipt was needed and no second boot
ran. Residue: which of W1/W2/W3 fires for entry 0 at runtime (W1 has 0 printed stub hits;
W2/W3 indexes resolve at runtime). Exact next receipt for a future brief (not run): one ≤90 s
boot with `PS2X_DIAG_WATCH=0x519AD8,0x519AD4` (learn table base + current entry; both are
w4 single words, zero steady-state traffic expected), then a targeted entry-0+8 watch.

### l. Machine-check paste block (every hand computation above)

```
0x519ab0 0x519ad8 0x519ad8
0x51ed98 ['0x51eda0', '0x51edb0', '0x51edc0', '0x51edd0'] 0x51ee90 0x51ee98
['0x51ed98', '0x51eda0', '0x51eda8', '0x51edb0']
0x519ab0 0x519ae4 0x28
0x519ab8 0x519ab4 0x519ac4 0x519ad8
0x519ac0 0x519ad4 0x519ad8 0x652c
0x519c08 0x63f8 0x6550 0x651c
0x519ae8 0x5 0x10
0x1fffe00 0x1fffe10 0x1e00
0x9 0x1b0 0x0 0x1
0x0 0x0 0x519ad8
0x450c14 0x519ae8
0x519ac4 0x519ab0
0x450c10 0xe00 0xe04
0x519c10 0x519c2c 0x519c30
```

## P16-3. Binaries and commits

| Binary / ref | sha256 / sha | Sources / state |
|---|---|---|
| `/tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner` (boot-p1o-1) | `7a7d4b645094d3ad82746a7d420b223422bf6444e5d06f6e56998e9057f5b4cd` | `e73e36a` tree, no rebuild (fresh; §P16-0 pre-boot check) |
| `ps2x_tests` | Not re-run (no source change; P15-1c 424/425 stands for this tree) | Same tree `e73e36a` |
| `PS2Recomp` branch `ssx3` HEAD | `e73e36a` | No fork commit (env-only boot; worktree sole `M` = pre-existing generated `runner/register_functions.cpp`, never added) |
| Fork push | `git push fork ssx3` from fork clone only | Up-to-date check (expect nothing to push) |
| This report | `[P1o]` commit (two trailers; local only) | Sole ssx3-repo change; no `runner/`, log, or `._*` added |

## P16-4. Exact commands

From `$W/PS2Recomp` (fork) unless noted; `$W=/Volumes/Extreme SSD/ps2recomp-spike`, `$O=$W/P1/output`,
`$R=$W/PS2Recomp`, `$LOG=$W/P1/run/boot-p1o-1.log`:

```
# Step 2-first (lease held by M8; no lease needed)
cat /tmp/ssx3-host-lease (M8 11:59:17 UTC); log to $W/P1/run/p1o-waits.log
shasum ps2EntryRunner (7a7d4b64 fresh); git log/status; ls ISO + ELF; pgrep (none)
sed/grep $O/sub_003DD1D8 (flag reads); python3 hex checks (§P16-2l, each pasted)
grep -rn "519AD8|-0x6528|-0x651C|-0x6550|-0x1268|sw .*,0x8(|sw .*,0x24(|sw .*,0x28(" $O
sed regions: 3DCC88, 3DCBD8, 3DDFA8 (x3), 3DE420 (full), 3DE670 (loop+tail),
  3DD7E0/3DDC30/3DDAC0/3DDDF0 provenances; P6 grep (30 addrs); ELF words x14
# Step 1 (lease protocol)
cat /tmp/ssx3-host-lease (absent 12:03:06 UTC)
printf 'P1o\n' > /tmp/ssx3-host-lease (12:03:18 UTC)
python3 hex recompute (0x1fffe80-0x80 = 0x1fffe00)
(write /tmp/p1o-boot1.py: p1n env, WATCH frame swap, probe on)
python3 /tmp/p1o-boot1.py (CWD $W/P1/run, 90 s, SIGTERM rc=-15, 906252 B)
rm -f /tmp/ssx3-host-lease (12:05:07 UTC); ls (absent); pgrep (none)
log greps: driver-entry 1 (:687); frame hits :688/:689; watch census; thread/stub/syscall comms;
  gs:/run:tick/frame/crash/dormant/start-thread/missing-target sweeps; slot fills; SIF merge check
# Step 3
(edit_file append Part 16; commit below)
git -C /Users/bradrichardson/dev/ssx3 add -f local/research/P1/REPORT.md
git -C /Users/bradrichardson/dev/ssx3 commit -m "[P1o] ..." (two trailers; NO push there)
git -C $R push fork ssx3 (up-to-date check; the only push allowed)
```

Env delta vs boot-p1n-1: WATCH `0x1ffe000`→`0x1fffe00`, `0x1ffe010`→`0x1fffe10` only.
Source delta: none.

## P16-5. What I could not do

- Confirm which of W1/W2/W3 fires for entry 0 at runtime: W1 (`3DE420`) has 0 printed stub
  hits (§P16-2f) and W2/W3 indexes resolve at runtime; the §P16-2k receipt (WATCH
  `0x519AD8`+`0x519AD4`) is designed but not run — Step 1 used the boot, Step 2b needs none.
- Read the table base / entry-0 absolute address: `0x519AD8` was never watched (value unknown).
- No runtime fix (per the brief): watch confirm + writer hunt only. The sema-26 non-delivery
  remains out of scope, untouched.
- One boot only (per the brief): no A/B on any rung.

---

## Part 17 (P1p): table base 0x5e0080 learned, entry-0+8 = 0x5e0088, sole runtime writer is init-time sd at 0x3e64d0 (W1/W2/W3 silent)

Brief `local/muse/prompts/P1p.md`. Table learn + writer catch; no runtime fix. Tables, no verdicts.
Stale-reading guard: Part 16 (P16-2c–2e writers W1/W2/W3 + table writer, P16-2k designed
receipt, P16-2l machine-check block) re-read before acting.

## P17-0. Lease record

| Event | Value |
|---|---|
| Lease at session start | Absent (`/tmp/ssx3-host-lease` missing; checked 14:31:32 UTC and pre-claim 14:31:50 UTC) |
| Pre-boot checks (14:31:44 UTC) | `pgrep -f "[p]s2EntryRunner"` exit 1 (none); binary `7a7d4b64` fresh (matches P16-3, no rebuild); fork HEAD `e73e36a`; ISO (2.8 GB) + ELF (3.7 MB) present |
| Claim | `printf 'P1p\n' > /tmp/ssx3-host-lease` 14:31:50 UTC, immediately before boot-p1p-1 |
| Boot 1 | 90 s foreground, SIGTERM rc=-15, returned 14:33:32 UTC |
| Boot 2 | 90 s foreground, SIGTERM rc=-15, returned 14:36:04 UTC (lease still `P1p`, verified 14:34:31 UTC) |
| Release | `rm -f /tmp/ssx3-host-lease` 14:38:24 UTC; verified absent; `pgrep` exit 1 |
| Foreign holds (M9) | None observed during the session; no poll waits; `$W/P1/run/p1p-waits.log` does not exist |
| `adb` | Not used |

## P17-1. Table addrs (Boot 1)

Boot-p1p-1: `$W/P1/run/boot-p1p-1.log`, 1,205 lines, 127,906 B, 17 blocks, CWD `$W/P1/run`,
env = p1o env with WATCH swapped to `0x519AD8,0x519AD4` (2 addrs; PROBE=1 kept on),
foreground 90 s, SIGTERM rc=-15. Binary `7a7d4b64` (fresh; §P17-3).

### a. All 9 watch lines (7 distinct stores; `diagWatchEmit` prints one line per overlapping WATCH entry, `ps2_runtime.cpp:1200-1204`)

| Line | addr + width | value | pc | ra | sp |
|---|---|---|---|---|---|
| :49–50 | `0x519ad0` w16 | `0x0` (128-bit zeros) | `0x10012c` | `0x0` | `0x0` |
| :58–59 | `0x519ad8` w4 | `0x5e0080` | `0x3dccfc` | `0x3dcd00` | `0x1fffe90` |
| :60 | `0x519adc` w4 | `0x5e0680` | `0x3dcd30` | `0x3dcd10` | `0x1fffe90` |
| :379 | `0x519ad4` w4 | `0x5e00b0` | `0x3de0b0` | `0x3de0b4` | `0x1fffb40` |
| :380 | `0x519ad4` w4 | `0x0` | `0x3de470` | `0x3de300` | `0x1fffb20` |
| :381 | `0x519ad4` w4 | `0x0` | `0x3de0b0` | `0x3de0b4` | `0x1fff8b0` |
| :382 | `0x519ad4` w4 | `0x5e00b0` | `0x3de0b0` | `0x3de0b4` | `0x1fffab0` |

(thread=1 on all 9 lines. :49–50 / :58–59 double because the write overlaps both
`[0x519AD4,0x519ADC)` and `[0x519AD8,0x519AE0)` ranges; :60 / :379–382 single.)

### b. Receipts

| Receipt | Value |
|---|---|
| Table base `*(0x519AD8)` | `0x5e0080` (:58–59; writer pc `0x3dccfc`, the P16-2c pc) |
| Current entry `*(0x519AD4)` | `0x5e00b0` set @ `0x3de0b0` (:379), `0x0` clear @ `0x3de470` (:380), `0x0` set @ `0x3de0b0` (:381), `0x5e00b0` set @ `0x3de0b0` (:382) — set/clear pcs are the P16-2e pcs |
| Current entry index | `0x5e00b0` − `0x5e0080` = `0x30` → entry 1 (check §P17-1d) |
| Entry-0+8 absolute addr | `0x5e0088` = `0x5e0080`+8 (check §P17-1d) |
| Neighbor `*(0x519ADC)` | `0x5e0680` = table+`0x600` = table+`0x20` entries (:60 @ `0x3dcd30`, `sub_003DCC88`, `sw $a2,0x2C($s0)` delay slot, ELF `0xae06002c` ✓) |
| Zero-init `:49–50` | `sq $zero,0($v0)` @ `0x10012c` (`sub_00100008`, ELF `0x7c400000` ✓) |

### c. Ladder delta vs boot-p1o-1

| Rung | boot-p1o-1 (9,638 lines, 906,252 B) | boot-p1p-1 (1,205 lines, 127,906 B) | Delta |
|---|---|---|---|
| Thread-1 pc | `0x3e5980` ×16, `0x423c90` ×1 (blk11) | `0x3e5980` ×16, `0x423c90` ×1 (blk14) | Same family, other block |
| Thread-1 sp | `0x1fffd80` ×16, `0x1fffde0` ×1 | `0x1fffd80` ×16, `0x1fffde0` ×1 | Same values (pc↔sp mapping holds) |
| Missing target | 0 | 0 | None |
| Stub distinct b0 / b1–16 | 486 / 18 | 486 / 18 | None |
| Syscall distinct b0 / b1+ | 27 / 3; 20 printed ids | 27 / 3; same 20 ids (sort-compared) | None |
| CD callback | queued+start :685–686 | queued+start :385–386 (func=1 cb=`0x3e3ad8`) | Same pair, earlier lines |
| Probe | 1 (:687, `sp=0x1fffe80 ra=0x3ded88 sourcePc=0x3ded80 checkpointed=0`) | 1 (:387, same bytes) | Line number only |
| Threads 2/4/5 | sema-parked 26/29/30 @ `0x423de8` | Same (blk0 ids/entries/priorities/stacks identical) | None |
| VIF MPG/MSCAL | 0 | 0 | None |
| GIF/GS | `gs:gif` 2, `gs:kick` 66, `gs:reg` 122, `gs:prim` 33, `gs:copy-reg` 8; first kick :410 | 2 / 66 / 122 / 33 / 8; first kick :165 (same content `idx=0 drawing=1 prim=6 vtxCount=1`) | Line shift only |
| `run:tick` | 7 (ticks 120–840) | 7 (same ticks/counters) | None |
| Presented frame | None (raylib line only) | None (sole `frame` hit = raylib TIMER line :46) | None |
| Crash | 0 | 0 | None |
| Dormant / start-thread | 40 / 4 | 40 / 4 | None |
| Slot fills | init next `0x28` etc. (slot WATCH addrs) | Not observed (slot addrs not watched) | Coverage, not behavior |
| `target=0x3de420` / `0x3ddfa8` | 0 / 0 | 0 / 0 | None |
| `firstRa=0x3dd290` / `0x3dd280` | 17 / 17 | 17 / 17 | None |

Per-block thread-1 (p1p-1; `sch` = id1 `scheduled`): blk0–13 `0x3e5980`
(84/82/77/82/82/81/80/79/72/82/82/82/79/77), blk14 `0x423c90` (71), blk15–16
`0x3e5980` (83/82).

### d. Machine-check paste block (every hand computation in §P17-1)

```
python3 -c "print(hex(0x5e0080+8), hex(0x5e00b0-0x5e0080), hex((0x5e00b0-0x5e0080)//0x30), hex(0x5e0080+0*0x30+8))"
→ 0x5e0088 0x30 0x1 0x5e0088
python3 -c "print(hex(0x5e0680-0x5e0080), hex((0x5e0680-0x5e0080)//0x30), hex(0x519adc-0x519ab0))"
→ 0x600 0x20 0x2c
```

## P17-2. Runtime writer answer (Boot 2)

Boot-p1p-2: `$W/P1/run/boot-p1p-2.log`, 1,197 lines, 127,111 B, 17 blocks, CWD `$W/P1/run`,
env = p1p-1 env with WATCH swapped to the §P17-1 addr `0x5e0088` (1 addr; PROBE=1 kept on),
foreground 90 s, SIGTERM rc=-15. Binary `7a7d4b64` (fresh; §P17-3).

### a. Watch: exactly 1 line

| Line | addr + width | value | pc | ra | sp |
|---|---|---|---|---|---|
| :57 | `0x5e0088` w8 | `0x0` | `0x3e64d0` | `0x3dcd10` | `0x1fffe80` |

(thread=1.)

### b. W1/W2/W3: 0 hits

| pc | Occurrences anywhere in boot-p1p-2.log |
|---|---|
| W1 `0x3de468` | 0 |
| W2 `0x3dd83c` | 0 |
| W3 `0x3ddd30` | 0 |

(`target=0x3de420`: 0; `target=0x3ddfa8`: 0 — same as boot 1.)

### c. Fourth writer (residue per Step 2)

| Item | Value |
|---|---|
| pc | `0x3e64d0` |
| Insn (ELF ✓) | `sd $v1, 0x8($a0)` = `0xfc830008` |
| Owning function | `sub_003E6448` (`0x3e6448`–`0x3e6574` per `ssx3-functions.csv`) |
| P6 | — (no row for `0x3e6448`; re-grepped `local/research/P6/ssx3-decomp-names.csv`, 802 lines) |
| Value / width | `0x0` / w8 (covers entry-0+8 and +12) |
| Caller | `jal func_3E6448` @ `0x3dcd08` in `sub_003DCC88` (ra `0x3dcd10` = return addr) |
| Loop context | `addiu $a2,$a2,-0x40` @ `0x3e64cc` immediately precedes the `sd` |
| Position | Log :57 (early init; before SIF/CD/probe :377–379) |

### d. Ladder delta vs boot-p1p-1

| Rung | boot-p1p-1 | boot-p1p-2 | Delta |
|---|---|---|---|
| Thread-1 pc | `0x3e5980` ×16, `0x423c90` ×1 (blk14) | `0x3e5980` ×15, `0x423c90` ×1 (blk0), `0x3dd278` ×1 (blk11) | Same park family |
| Thread-1 sp | `0x1fffd80` ×16, `0x1fffde0` ×1 | `0x1fffd80` ×15, `0x1fffde0` ×1, `0x1fffe00` ×1 | pc↔sp mapping holds |
| Missing target | 0 | 0 | None |
| Stub distinct b0 / b1–16 | 486 / 18 | 486 / 18 | None |
| Syscall distinct b0 / b1+ | 27 / 3; same 20 ids as p1o | 27 / 3; same 20 ids (sort-compared vs p1o) | None |
| CD callback | :385–386 | :377–378 (same func/cb) | Same pair, earlier lines |
| Probe | 1 (:387, p1o bytes) | 1 (:379, p1o bytes) | Line number only |
| Threads 2/4/5 | sema-parked 26/29/30 @ `0x423de8` | Same | None |
| GIF/GS | 2 / 66 / 122 / 33 / 8; first kick :165 | 2 / 66 / 122 / 33 / 8; first kick :161 | Line shift only |
| `run:tick` | 7 | 7 | None |
| Presented frame | None | None (sole `frame` hit = raylib TIMER line :46) | None |
| Crash | 0 | 0 | None |
| Dormant / start-thread | 40 / 4 | 40 / 4 | None |
| `firstRa=0x3dd290` / `0x3dd280` | 17 / 17 | 17 / 17 | None |

Per-block thread-1 (p1p-2): blk0 `0x423c90` (81), blk1–10 `0x3e5980`
(77/82/82/82/80/79/69/82/82/81), blk11 `0x3dd278` (79), blk12–16 `0x3e5980`
(77/68/81/82/82).

## P17-3. Binaries and commits

| Binary / ref | sha256 / sha | Sources / state |
|---|---|---|
| `/tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner` (boot-p1p-1 + boot-p1p-2) | `7a7d4b645094d3ad82746a7d420b223422bf6444e5d06f6e56998e9057f5b4cd` | `e73e36a` tree, no rebuild (fresh; §P17-0 pre-boot check) |
| `ps2x_tests` | Not re-run (no source change; P15-1c 424/425 stands for this tree) | Same tree `e73e36a` |
| `PS2Recomp` branch `ssx3` HEAD | `e73e36a` | No fork commit (env-only boots; worktree sole `M` = pre-existing generated `runner/register_functions.cpp`, never added) |
| Fork push | `git push fork ssx3` from fork clone only | Up-to-date check (expect nothing to push) |
| This report | `[P1p]` commit (two trailers; local only) | Sole ssx3-repo change; no `runner/`, log, or `._*` added |

## P17-4. Exact commands

From `$W/PS2Recomp` (fork) unless noted; `$W=/Volumes/Extreme SSD/ps2recomp-spike`, `$O=$W/P1/output`,
`$R=$W/PS2Recomp`:

```
# Pre-boot (lease protocol)
cat /tmp/ssx3-host-lease (absent 14:31:32 UTC); pgrep -f "[p]s2EntryRunner" (exit 1)
shasum ps2EntryRunner (7a7d4b64 fresh); git log/status (e73e36a); ls ISO + ELF
cat /tmp/ssx3-host-lease (absent); printf 'P1p\n' > /tmp/ssx3-host-lease (14:31:50 UTC)
# Step 1
(write /tmp/p1p-boot1.py: p1o env, WATCH 0x519AD8,0x519AD4, probe on; diff vs p1o-boot1.py)
python3 /tmp/p1p-boot1.py (CWD $W/P1/run, 90 s, SIGTERM rc=-15, 127906 B; returned 14:33:32 UTC)
log greps: driver-entry 1 (:387); watch 9 (:49/:50/:58/:59/:60/:379-:382); watch census
python3 hex checks (§P17-1d, each pasted)
ladder greps: thread/stub/syscall comms; syscall b0 sort-compare vs p1o (identical);
  gs:/run:tick/frame/crash/dormant/start-thread/missing-target sweeps; SIF count
P6 grep (ssx3-decomp-names.csv); ELF words (0x3dcd30, 0x10012c); gen MIPS quotes
# Step 2 (lease still P1p, verified 14:34:31 UTC)
(sed /tmp/p1p-boot1.py -> /tmp/p1p-boot2.py: LOG boot-p1p-2, WATCH 0x5e0088; diff shown)
python3 /tmp/p1p-boot2.py (CWD $W/P1/run, 90 s, SIGTERM rc=-15, 127111 B; returned 14:36:04 UTC)
log greps: driver-entry 1 (:379); watch 1 (:57); W1/W2/W3 pc counts 0/0/0; ladder (same sweeps)
python3 range lookup (0x3e64d0/0x3dcd10); P6 grep (no rows); ELF words; gen MIPS quotes;
  diagWatchEmit source read (ps2_runtime.cpp:1200-1204)
# Step 3
rm -f /tmp/ssx3-host-lease (14:38:24 UTC); ls (absent); pgrep (none)
(edit_file append Part 17; commit below)
git -C /Users/bradrichardson/dev/ssx3 add -f local/research/P1/REPORT.md
git -C /Users/bradrichardson/dev/ssx3 commit -m "[P1p] ..." (two trailers; NO push there)
git -C $R push fork ssx3 (up-to-date check; the only push allowed)
```

Env delta vs boot-p1o-1: WATCH `11 addrs`→`0x519AD8,0x519AD4` (boot 1) →`0x5e0088` (boot 2) only.
Source delta: none.

## P17-5. What I could not do

- Observe a W1/W2/W3 write to entry-0+8 at runtime: 0 hits in the 90 s boot-2 window
  (§P17-2b), and `target=0x3de420`/`0x3ddfa8` printed 0 lines in both p1p boots (boot 1
  did not watch entry-0+8). No longer-than-90 s watch and no completion-driving stimulus
  was run (outside the brief's 2-boot box — both used).
- Re-read the table base in boot 2: `0x519AD8` was not watched there (per the brief), so the
  `0x5e0080` base rests on the boot-1 read alone (the boot-2 :57 hit at the derived addr is
  the only cross-boot evidence).
- No runtime fix (per the brief): table learn + writer catch only. The sema-26 non-delivery
  remains out of scope, untouched.
- Two boots used (the brief's max): no A/B on any rung.

---

## Part 18 (P1q): entry 0 never queued (3DDAC0 path B) + current stuck at recycled slot (nibble-4 CD read); the entry-1 "re-select" is slot reuse (id 3)

Brief `local/muse/prompts/P1q.md`. Static selection/completion analysis + 1 dynamic receipt
boot; no fix. Tables, no verdicts. Stale-reading guard: Part 17 (P17-1 table base +
current-entry transitions, P17-2 sole init hit + W1/W2/W3 silence) + Part 16 §P16-2d–2f
re-read before acting.

## P18-0. Lease record

| Event | Value |
|---|---|
| Lease at session start | Absent (`/tmp/ssx3-host-lease` missing; checked 15:32:35 UTC and pre-claim) |
| Pre-boot checks | `pgrep -f "[p]s2EntryRunner"` exit 1 (none); binary `7a7d4b64` fresh (matches P17-3, no rebuild); fork HEAD `e73e36a`; ISO (3005415424 B) + ELF (3890784 B) present |
| Claim | `printf 'P1q\n' > /tmp/ssx3-host-lease` 15:33:22 UTC, immediately before boot-p1q-1 |
| Boot 1 | 90 s foreground, SIGTERM rc=-15, returned 15:34:53 UTC |
| Release | `rm -f /tmp/ssx3-host-lease` 15:35:58 UTC; verified absent; `pgrep` exit 1 |
| Foreign holds (M10) | None observed during the session; no poll waits; `$W/P1/run/p1q-waits.log` does not exist |
| Second boot | None (Step 1 residue closed by boot 1; reserve unused) |
| `adb` | Not used |

## P18-1. Entry-0 + selection + completion analysis (static + boot-1 reads)

### a. Entry-0's request (3DED50 → 3DDAC0 path B)

| Step | Value |
|---|---|
| Driver caller | `sub_003DED50` (`0x3ded50`–`0x3dedc0`), no P6 row; `jal func_3DDAC0` @ `0x3ded6c` (ELF `0xc0f76b0` ✓), `jal func_3DD1D8` @ `0x3ded80` (ELF `0xc0f7476` ✓, JAL→`0x3dd1d8` ✓) with `$a0` = ret(`3DDAC0`) |
| Allocator | `sub_003DDAC0`, lookup site `0x3ddaf4`; `$s2` = entry 0 (`0x5e0080`) |
| Fill (watched, §P18-2a :388–390) | `+0x14` = `$a3` = `0x0` @ `0x3ddb10` (ELF `0xae500014` ✓); `+0x10` = `$a2` = `0x64` @ `0x3ddb18` (ELF `0xae550010` ✓); `+0` = `(old & 0xFF0FFFFF) \| 0x00900000` = `0x900001` @ `0x3ddb24` (ELF `0xae420000` ✓; mask `0x3ddb00`/`0x3ddb08` = `0x3c03ff0f`/`0x3463ffff` ✓, const `0x3ddb0c` = `0x3c040090` ✓) |
| Path branch | `0x3ddb20` `beqz $s1` (ELF `0x12200011` ✓) → `0x3ddb68` = path B (check §P18-1h); `$s1` = `*(0x519AE4)` (devlist head, read `0x3ddaf8` delay) |
| Path A (not taken) | Device-list walk + `str*` match; `+0x24` = device word (delay `0x3ddb54`, ELF `0xae420024` ✓); enqueue @ `0x3ddb50` (ELF `0xc0f77ea` ✓, JAL→`0x3ddfa8` ✓) |
| Path B (taken) | Node alloc via `jalr *(0x450C14)`; `jal func_3DD4E8` @ `0x3ddbc0` (entry-1 alloc+enqueue); `jal func_3DCF70` @ `0x3ddbd0` with `$a1` = `0x3E0000`−`0x25F0` = `0x3DDA10` (ELF `0x24a5da10` ✓); `$s2` (entry 0) never touched again |
| Discriminator | Entry-0 `+0x24`: zero writes in 90 s (§P18-2a) → path B; entry 0 never enqueued |

### b. `0x30`-byte table-entry layout (all 12 words; ELF ✓ = word matches disasm comment)

| Off | Readers | Writers | Entry-0 value (watched unless noted) |
|---|---|---|---|
| `+0x0` id = idx≪24 \| nibble≪20 \| counter | Driver low-20 cmp `0x3dd240` (ELF `0x8c620000` ✓); dispatch nibble `0x3de0d8`/`0x3de0dc` (ELF `0x21502`/`0x3042000f` ✓); W1 chained `$a0` `0x3de484`; allocator returns | Lookup: state:=1 `0x3de6f8` (ELF `0xaca30000` ✓), `sb` idx `0x3de704` (ELF `0xa0510003` ✓), id `0x3de72c` (ELF `0xac820000` ✓); allocators nibble-OR; clearer `3DE7B0` zeros | `0x900001` (idx 0, nibble 9, id 1; check §P18-1h) |
| `+0x4` | W1 `0x3de450` (≠0 → flag −1); Exec `0x3de0bc` (ELF `0x8e220004` ✓; ≠0 → immediate W1) | NONE found (census: 7 allocator files + Exec + W1; `3DD7E0:0x3dd988` + `3DDAC0:0x3ddb94` are node stores, bases are not entries) | `0x0` (init zero, never written) |
| `+0x8` flag | Driver `0x3dd258`/`0x3dd2dc`/`0x3dd2e8` (all ELF `0x8e220008` ✓); `3DCF70` `0x3dcf98` (ELF `0x8c650008` ✓); W1 chained `$a1` `0x3de488` | W1 `0x3de468`, W2 `0x3dd83c`, W3 `0x3ddd30` (P16-2d); init `sd` | `0x0` (init `:60` only) |
| `+0xC` case predicate | Cases 1/5/7/8: `$a0` = (`+0xC` < 1) `0x3de344`/`0x3de3f8` (both ELF `0x2c840001` ✓) | `3DD4E8` =2 (`0x3dd55c` ELF `0xae62000c` ✓), `3DD7E0` =6, `3DD438` =2, `0x3dda10`-fail =4 (`0x3dda64` ELF `0xac62000c` ✓), W3-path =8 (`0x3ddd38` ELF `0xae63000c` ✓), case-1 handler | `0x0` |
| `+0x10` prio/key | Enqueue sort `0x3ddff4`/`0x3de014`; P4 gate `0x3de07c` (ELF `0x8e230010` ✓) vs `*(0x519AB8)` | Allocators from `$a2`/`$t0`/`$s1` (`3DDAC0:0x3ddb18`, `3DD4E8:0x3dd53c` ELF `0xae720010` ✓, `3DD648:0x3dd6a4`, …) | `0x64` = 100 (would pass P4 vs init `0xFF`) |
| `+0x14` node/cb-arg | W1 chained `$a2` `0x3de480`; `3DCF70`-invoke `$a2`; callbacks' `$s1` | Allocators from `$a3`/`$t1`/node (`3DDAC0:0x3ddb10`, `3DD4E8:0x3dd52c` ELF `0xae700014` ✓, …) | `0x0` (`$a3` = 0 in this call) |
| `+0x18` | Case 0 `&1` `0x3de19c`; cases 2/3 pass as `$a2` | `3DD4E8` from `$a1` (`0x3dd534` ELF `0xae710018` ✓); `3DD438` =1 (`0x3dd490` delay); W2-path = `*($a0+4)` (`0x3dd844` ELF `0xae430018` ✓); case 0 terminal =`$s2` (`0x3de2f4` ELF `0xae320018` ✓); case 4 (delay `0x3de3e4` ELF `0xae220018` ✓) | `0x0` |
| `+0x1C` case-2 predicate | `blez` @ `0x3de354` (ELF `0x18e00013` ✓) → sync W1 `0x3de3a4`; case 3 passes as `$a3` | `3DD648` site 1 (`0x3dd6ec` delay) / site 2 (`0x3dd7a4`) only | `0x0` |
| `+0x20` | Cases 2/3 pass as `$a1` | `3DD648` from `$a2` (`0x3dd6d4`/`0x3dd7b0`) only | `0x0` |
| `+0x24` device/path node | Case-0 string ops + device fns; case 1 | Path-A `0x3ddb54`; `3DD4E8:0x3dd54c` (ELF `0xae620024` ✓) / `3DD438:0x3dd498` = ret(`3DE800` node pool); `3DD5A0:0x3dd5fc`; `3DD648:0x3dd6c4` | `0x0` (path-B discriminator) |
| `+0x28` completion cb | W1 chained `jalr` (`0x3de474` read, `0x3de48c` call) | `3DCF70:0x3dcfa0` delay ONLY (ELF `0xac680028` ✓, unconditional); cleared by `3DE7B0`. Zero `sw *,0x28(` in all 7 allocator files | `0x0` (no `3DCF70` call names entry 0) |
| `+0x2C` queue link | Dequeue `0x3de094`/`0x3de0a0` (ELF `0xac830030` ✓) | Enqueue `0x3ddfec` (ELF `0xae22002c` ✓) / `0x3de030` (ELF `0xac91002c` ✓) | `0x0` (never linked) |

`3DE800` = node-pool allocator (scans `*(0x519ADC)`-based pool at stride `0x110`, marks used);
`3DE7B0` = entry clearer (`MUTEX_lock`, `memset(entry,0,0x30)` @ `0x3de7dc` ELF `0xc0f9912` ✓ JAL→`0x3e6448` ✓
with `$a2` = `0x30` @ `0x3de7e0` ELF `0x24060030` ✓, `MUTEX_unlock`), called from `3DD310` @ `0x3dd414`
(ELF `0xc0f79ec` ✓ JAL→`0x3de7b0` ✓); `3DE668` = no-op stub (`jr $ra`/`nop`, ELF `0x3e00008`/`0x0` ✓).

### c. Allocator survey (7 functions, 9 lookup sites, nibbles 2–10)

| Fn (P6: none) | Lookup site | Nibble (`lui $a0`, ELF ✓) | `+0x10` / `+0x14` sources | Enqueue? |
|---|---|---|---|---|
| `3DD438` | `0x3dd458` | 8 (`0x3dd464` `0x3c040080`) | `$s1` / `$s0` (arg regs; mapping not traced) | Yes `0x3dd4c0` |
| `3DD4E8` | `0x3dd510` | 2 (`0x3dd51c` `0x3c040020`) | `$a2` / `$a3` (= node in path B) | Yes `0x3dd574` |
| `3DD5A0` | `0x3dd5c0` | 3 (`0x3dd5dc` `0x3c040030`) | `$s0` / `$s1` (arg regs; mapping not traced) | Yes `0x3dd620` |
| `3DD648` site 1 | `0x3dd680` | 4 (`0x3dd698` `0x3c040040`) | `$t0` / `$t1` (= prio / node in `0x3dda10`-success) | Yes `0x3dd6e8` |
| `3DD648` site 2 | `0x3dd758` | 5 (`0x3dd770` `0x3c040050`) | Not read (fill outside Step-1 need) | Yes `0x3dd7ac` |
| `3DD7E0` site 1 | `0x3dd800` | 6 (`0x3dd818` `0x3c040060`) | `$a1` / `$s0` | NO — W2 sync: `$a0`≠0 (`0x3dd82c` ELF `0x12600006` ✓) → flag=1 + `+0x18`=`*($a0+4)` (`0x3dd834` ELF `0x8e630004` ✓); else `+0xC`=6 + `3DE668` no-op |
| `3DD7E0` site 2 | `0x3dd890` | 7 (`0x3dd89c` `0x3c040070`) | `$a1` / `$a2` | Yes `0x3dd8c0` |
| `3DDAC0` | `0x3ddaf4` | 9 (`0x3ddb0c` `0x3c040090`) | `$a2` (=`0x64`) / `$a3` (=0) | Path A yes `0x3ddb50`; path B NO |
| `3DDC30` | `0x3ddc70` | 10 (`0x3ddc7c` `0x3c0400a0`) | `$s7` / `$s1` (arg regs; mapping not traced) | NO — W3 sync: pool-scan match → flag=−2 (`0x3ddd30` ELF `0xae620008` ✓, −2 const `0x3ddd28` ELF `0x2402fffe` ✓), `+0xC`=8 |

Non-allocator enqueue sources: none — `3DDDF0` (`FILESYS_atomic`) issues dequeue-only
`ExecCommand(0)` calls (`0x3dde2c`/`0x3dde60`, `$a0`=0 delay `0x3dde30`); the `0x3ddc00`
trampoline (`jal 3DD310` @ `0x3ddc0c` ELF `0xc0f74c4` ✓, `jal ExecCommand` @ `0x3ddc14` ELF
`0xc0f77ea` ✓) has no `jal` caller (`0x0c0f7700` absent tree-wide) — residue §P18-5.

### d. Selection: enqueue + 5 dequeue predicates (one row per predicate/site)

Enqueue (`0x3ddfdc`–`0x3de044`, when `$a0`≠0): priority-insert by `+0x10` into the
`*(0x519AE0)`-headed chain via `+0x2C` links; count `*(0x519ABC)`++ @ `0x3de044`
(ELF `0xac62000c` ✓); head write @ `0x3de034` (ELF `0xac510030` ✓). Then falls through to
the dequeue below (same call selects when the predicates pass).

| # | pc (ELF ✓) | Predicate (fail → effect) | This boot |
|---|---|---|---|
| P1 | `0x3de050` (`0x14400004`; read `0x3de04c` `0x8c820024` = `*(0x519AD4)`) | Current == null, else unlock + exit (no select, no store) | FAILS after :411: current stuck at recycled slot → every later pump exits here |
| P2 | `0x3de05c` (read `0x3de058` `0x8c820010` = `*(0x519AC0)` inflight) | Inflight == 0, else unlock + exit | Passed at both dequeues (selects happened); value not directly watched |
| P3 | `0x3de074` (head `0x3de060` `0x8c910030` = `*(0x519AE0)`) | Head != null, else current := 0 (the `0x3de0b0` store) | :400 fired with head provably 0 (`:396` `head:=0`, no write between) → empty-store, not P4 |
| P4 | `0x3de088` (`0x54400006`; `0x3de07c` `0x8e230010` = head→`+0x10`, `0x3de080` `0x8c820008` = `*(0x519AB8)`, `slt` `0x3de084` `0x43102a`) | head→`+0x10` ≤ `*(0x519AB8)`, else current := 0 (same store shape; head NOT advanced) | Never fired (both heads selected first try); entry 0's `0x64` ≤ init `0xFF` would pass |
| P5 | `0x3de0bc` (`0x8e220004` = `*(entry+4)`) | `+4` == 0, else immediate W1 @ `0x3de0c8` (`$a0`=0 → flag −1) | Never taken (`+4` unwritten everywhere, §P18-1b) |

Select store @ `0x3de0b0` (delay of unlock `jal`, P16-2e) + dispatch on `( +0≫20)&0xF`
(`0x3de0d8`–`0x3de0e4` ELF ✓; range check `0x3de0e4` `0x2c830009`, fail exit → `0x3de3fc`
via `0x3de0e8` `0x106000c4`, check §P18-1h; table base `0x3de0f4` `0x24425d80` = `0x495D80`).

Why the slot and never entry 0: entry 0 is never in the queue (§P18-1a: path B, no
`+0x24`, no enqueue line, `+0x2C` stays 0), so no dequeue can name it; after :411 P1
additionally blocks every pump while current stays non-null.

### e. Dispatch (nibble → case; jump table `0x495D80` + 9 words ELF-verified, §P18-1h)

| Nibble (from) | Case entry | Body | W1 site(s) | Sync? event |
|---|---|---|---|---|
| 2 (`3DD4E8`) / 8 (`3DD438`) | `0x3de108` | `strchr`/`strcpy`/`strncpy` path prep + `3E3208` + device fns + `BIG_locateentryz` (`0x3e2768`, P6) device walk; `$s2` = (nibble≠8) | Terminal `0x3de2f8` (`$a0`=`$s2`; delay `0x3de2fc` ELF `0x240202d` ✓); every branch target re-verified to reach it (`0x3de1c8`→`0x3de23c`, `0x3de1e4`→`0x3de23c`, `0x3de23c`-taken→`0x3de2d8`, `0x3de2cc`-loop→`0x3de260`, `0x3de2e4`-taken→`0x3de2f8`; delay `0x3de2e8` = `nop` ELF `0x0` ✓) | SYNC, no wait. Reached: YES (`:398` `ra`=`0x3de300` = site+8 ✓) |
| 3 (`3DD5A0`) | `0x3de308` | `+0xC` protocol + `3E32F8`/`3DE8C0`; clears `+0x24` | Terminal `0x3de340` (`$a0`=(`+0xC`<1)) | SYNC. Reached: no (no nibble-3 alloc watched) |
| 4 (`3DD648`/1) | `0x3de350` | `+0x1C`≤0 → sync W1; else `3E3350` async variants | `0x3de3a4` (`$a0`=1; delay `0x3de3a8` ELF `0x24040001` ✓) or via `3E3350` | Reached: YES via recycled slot (`:411`→`:412` CD read); the `+0x1C`>0 branch (no `0x3de3a4` clear watched; `+0x1C` itself unwatched — inferred) |
| 5 (`3DD648`/2) | `0x3de3b4` | `3E3478` inline RPC-ish pair + W1 | `0x3e34c0` (`$a0`=1) | SYNC. Reached: no (no nibble-5 alloc watched) |
| 6 (`3DD7E0`/1) | `0x3de3d4` | `+0x18` = `*(*(+0x24)+4)` | Terminal `0x3de3e0` (`$a0`=1) | SYNC but DISPATCH-DEAD: nibble-6 never enqueued (§P18-1c), `3DDDF0` dequeues-only, trampoline callerless |
| 7 (`3DD7E0`/2) / 9 (`3DDAC0`) / 10 (`3DDC30`) | `0x3de3f0` | `$a0` = (`+0xC`<1) | Terminal `0x3de3f4` | SYNC. Entry 0's case: `+0xC`=0 → `$a0`=1 → flag would be 1 (`+4`=0). Never selected |
| 0/1/11–15 | `0x3de3fc` exit | Epilogue restore, no W1 | None — current STAYS set | Not taken (both selects had nibbles 2, 4) |

### f. W1 (`iFILESYS_CommandCompleteCallback`) — 10 unique `jal` sites

(P16-2f listed 9 unique pcs + 1 overlap dup; the true 10th unique pc is `0x3e4888` in
`sub_003E4648`. All 10 words are `0xc0f7908` ✓: 6 in Exec + `0x3e3450`/`0x3e34c0`/`0x3e3d64`/`0x3e4888`.)

| # | Site (`ra` = site+8, check §P18-1h) | Host | Sync/async; event waited on | Reached in this boot? |
|---|---|---|---|---|
| 1 | `0x3de0c8` (`0x3de0d0`) | Exec `+4`≠0 path | Sync, none (immediate, `$a0`=0 → flag −1) | No (`+4`==0 everywhere) |
| 2 | `0x3de2f8` (`0x3de300`) | Case 0/6 terminal | Sync, none (`$a0`=`$s2`) | YES — `:398` flag=1 + `:399` clear, `ra`=`0x3de300` |
| 3 | `0x3de340` (`0x3de348`) | Case 1 terminal | Sync, none (`$a0`=(`+0xC`<1)) | No (no nibble-3) |
| 4 | `0x3de3a4` (`0x3de3ac`) | Case 2 `+0x1C`≤0 | Sync, none (`$a0`=1) | No (recycled slot took `+0x1C`>0 branch) |
| 5 | `0x3de3e0` (`0x3de3e8`) | Case 4 terminal | Sync, none (`$a0`=1) | No (case 4 dispatch-dead) |
| 6 | `0x3de3f4` (`0x3de3fc`) | Case 5/7/8 terminal | Sync, none (`$a0`=(`+0xC`<1)) | No (entry 0 unselected; no nibble-7/10 select) |
| 7 | `0x3e3450` (`0x3e3458`) | `0x3e33b0` poll (folded in `3E3350` range) | Async: `*(0x519C20)` flag (`0x520000`−`0x63E0`, check §P18-1h; test `0x3e33d4` ELF `0x10600020` ✓) + `0x450C40`/`0x450C4C` counter match; calls `0x428168` (`0x3e3410` ELF `0xc10a05a` ✓) + `0x4283A0` (`0x3e3424` ELF `0xc10a0e8` ✓); clears flag (`0x3e344c` ELF `0xae409c20` ✓) | No (no `jal` caller of `0x3e33b0` found tree-wide — residue; flag never watched) |
| 8 | `0x3e34c0` (`0x3e34c8`) | `3E3478` (case-3 callee) | Sync, none: `0x428168` (`0x3e34a8` ✓) + `0x428600` (`0x3e34b8` ELF `0xc10a180` ✓) inline, `$a0`=1 (`0x3e34c4` ELF `0x24040001` ✓) | No (no nibble-5) |
| 9 | `0x3e3d64` (`0x3e3d6c`) | `3E3B00` CD worker (no `jal` caller; device-table/indirect — `sceCdRead ret=0x3e3b8c` proves it ran) | Async: CD-transfer completion (`$a0`=1 `0x3e3d5c` ELF `0x24040001` ✓; state `&~2` writeback `0x3e3d68` ELF `0xae229c40` ✓) | Host RAN, site NOT reached: CD callback queued+started (`:414`–`:415`) but no current-clear after `:411` |
| 10 | `0x3e4888` (`0x3e4890`) | `3E4648` CD worker (caller: `3E3350`-topbyte==1 @ `0x3e3398` ELF `0xc0f9192` ✓ JAL→`0x3e4648` ✓; gate `0x3e3368` ELF `0x1088000b` ✓) | Async: CD-transfer completion (same idiom: `$a0`=1 `0x3e4880` ✓, `0x3e488c` ✓) | No (needs case 2 via `3E3350` topbyte-1 arm; no evidence) |

`0x428168`/`0x4283A0`/`0x428600` = `sub_00428168`/`sub_004283A0`/`sub_00428600`, no P6 rows
(JAL targets verified §P18-1h; roles not traced — residue). No-`jal`-caller functions
(`0x3e33b0`, `3E3B00`) are reached via pointers/tables (residue: exact registration sites).

### g. Entry-0's completion chain (traced statically, broken at the CD→W1 link)

| Link | Evidence |
|---|---|
| `3DCF70`(handle1, `0x3dda10`) sees flag1=1 (`:398`) → immediate `jalr 0x3dda10` (`0x3dcfac` ELF `0x100f809` ✓) | `:387`–`:398` order; `3DCF70` flag test `0x3dcf9c` + always-set `+0x28` `0x3dcfa0` |
| `0x3dda10` success (`$s0`==1 @ `0x3dda58` ELF `0x12020007` ✓): `3DD310` → `3DE7B0` clears slot (`:401`–`:404`, `ra`=`0x3de7e4` = memset-`jal`+8 ✓); `3DD648`-site1 re-allocs slot as nibble 4/id 3 (`:405`–`:408`); `3DCF70`(handle2, `0x3dd8e8`) (`0x3dda9c` ELF `0xc0f73dc` ✓; `0x3E0000`−`0x2718` = `0x3dd8e8` ✓) | `:401`–`:408` watched; fail path (`+0xC`=4 + `ExecCommand(entry0)` @ `0x3dda68` ELF `0xc0f77ea` ✓) NOT taken — no entry-0 enqueue watched |
| Recycled slot selected (`:409`–`:411`), case 2 dispatches CD read (`:412` `lbn=0x5f1a3`, `ret=0x3e3b8c`, `BIGF` payload) | `:411` select + `:412` CD line + `:414`–`:415` callback pair, all before probe `:416` |
| BREAK: callback fired, W1 never ran (no clear after `:411`) → chained `0x3dd8e8` never runs → its fast path (`ExecCommand(*($s1+0x10))` = entry 0 @ `0x3dd9e8`) never fires | Zero `0x519AD4` lines after `:411`; entry-0 `+8`/`+0x2C` never written |
| Entry 0 therefore never selected (P1 would also block it now) and its sync case-7 completion (`0x3de3f4`) never fires | `0x5e0080` never a `0x519AD4` value (grep: sole `value=0x5e0080` is the `:58` table-base store) |

### h. ELF verification words + machine-check paste block

Jump table `0x495D80` (file off = va−`0x100000`+`0x1000`): case→entry
`0→0x3de108`, `1→0x3de308`, `2→0x3de350`, `3→0x3de3b4`, `4→0x3de3d4`, `5→0x3de3f0`,
`6→0x3de108`, `7→0x3de3f0`, `8→0x3de3f0` (words read from `0x495D80`–`0x495DA0`, check §P18-1h).

Batch word check (101 addrs; every word matched its disassembly comment in `$O`):

```
0x3ddb00 0x3c03ff0f / 0x3ddb08 0x3463ffff / 0x3ddb0c 0x3c040090 / 0x3ddb10 0xae500014
0x3ddb14 0x431024 / 0x3ddb18 0xae550010 / 0x3ddb1c 0x441025 / 0x3ddb20 0x12200011
0x3ddb24 0xae420000 / 0x3ddb50 0xc0f77ea / 0x3ddb54 0xae420024
0x3dd51c 0x3c040020 / 0x3dd52c 0xae700014 / 0x3dd534 0xae710018 / 0x3dd53c 0xae720010
0x3dd544 0xae630000 / 0x3dd54c 0xae620024 / 0x3dd55c 0xae62000c / 0x3dd574 0xc0f77ea
0x3dd464 0x3c040080 / 0x3dd5dc 0x3c040030 / 0x3dd698 0x3c040040 / 0x3dd770 0x3c040050
0x3dd818 0x3c040060 / 0x3dd89c 0x3c040070 / 0x3ddc7c 0x3c0400a0
0x3dd82c 0x12600006 / 0x3dd834 0x8e630004 / 0x3dd844 0xae430018
0x3ddd28 0x2402fffe / 0x3ddd30 0xae620008 / 0x3ddd38 0xae63000c
0x3de6f8 0xaca30000 / 0x3de704 0xa0510003 / 0x3de72c 0xac820000
0x3de6dc 0x31502 / 0x3de6e0 0x3042000f
0x3de7dc 0xc0f9912 / 0x3de7e0 0x24060030 / 0x3dd414 0xc0f79ec
0x3dcfa0 0xac680028 / 0x3dcf98 0x8c650008 / 0x3dcfac 0x100f809
0x3dda58 0x12020007 / 0x3dda5c 0x24020004 / 0x3dda64 0xac62000c / 0x3dda68 0xc0f77ea
0x3dda6c 0x8e240010 / 0x3dda48 0xc0f74c4 / 0x3dda9c 0xc0f73dc
0x3de04c 0x8c820024 / 0x3de050 0x14400004 / 0x3de058 0x8c820010 / 0x3de060 0x8c910030
0x3de07c 0x8e230010 / 0x3de080 0x8c820008 / 0x3de084 0x43102a / 0x3de09c 0xac82000c
0x3de0a0 0xac830030 / 0x3de0bc 0x8e220004 / 0x3de0d8 0x21502 / 0x3de0dc 0x3042000f
0x3de0e0 0x2444fffe / 0x3de0e4 0x2c830009 / 0x3de0e8 0x106000c4 / 0x3de0f4 0x24425d80
0x3de0fc 0x8c640000 / 0x3de100 0x800008
0x3de2f4 0xae320018 / 0x3de2fc 0x240202d / 0x3de344 0x2c840001 / 0x3de3a8 0x24040001
0x3de3e4 0xae220018 / 0x3de3f8 0x2c840001 / 0x3de354 0x18e00013
0x3e344c 0xae409c20 / 0x3e3454 0xae230c4c / 0x3e34c4 0x24040001 / 0x3e3d5c 0x24040001
0x3e3d68 0xae229c40 / 0x3e4880 0x24040001 / 0x3e488c 0xae229c40
0x3e3368 0x1088000b / 0x3e3398 0xc0f9192 / 0x3e33d4 0x10600020 / 0x3e3410 0xc10a05a
0x3e3424 0xc10a0e8 / 0x3e34a8 0xc10a05a / 0x3e34b8 0xc10a180
0x3ded6c 0xc0f76b0 / 0x3ded80 0xc0f7476 / 0x3dd218 0x8d060028 / 0x3dd240 0x8c620000
0x3dd258 0x8e220008 / 0x3dd2dc 0x8e220008 / 0x3dd2e8 0x8e220008
0x3ddfec 0xae22002c / 0x3de030 0xac91002c / 0x3de034 0xac510030 / 0x3de044 0xac62000c
0x3ddc0c 0xc0f74c4 / 0x3ddc14 0xc0f77ea / 0x3de2e4 0x14430004 / 0x3de2e8 0x0
0x3de1c8 0x1040001c / 0x3de1e4 0x10400015 / 0x3de23c 0x56400026 / 0x3de2cc 0x1240ffe4
```

Machine-check paste block (every hand computation in §P18-1; command then `→` output):

```
python3 -c "print(hex(0x5e0080+0x30), hex(0x5e0080+0x24), hex(0x5e0080+0x28), hex(0x5e00b0+8), hex(0x5e00b0+0x28))"
→ 0x5e00b0 0x5e00a4 0x5e00a8 0x5e00b8 0x5e00d8
python3 -c "print(hex(0x520000-0x6550), hex(0x519AB0+0x24), hex(0x519AB0+0x30), hex(0x519AB0+0x34), hex(0x520000-0x653C), hex(0x519AC4+0x1C), hex(0x520000-0x63E0), hex(0x520000-0x63C0))"
→ 0x519ab0 0x519ad4 0x519ae0 0x519ae4 0x519ac4 0x519ae0 0x519c20 0x519c40
python3 -c "print(hex(0x3E0000-0x25F0), hex(0x3E0000-0x2718))"
→ 0x3dda10 0x3dd8e8
python3 -c "print(hex(0x3de354+4+0x13*4), hex(0x3de1c8+4+0x1C*4), hex(0x3de1e4+4+0x15*4), hex(0x3de2e4+4+0x4*4), hex(0x3de23c+4+0x26*4), hex(0x3de2cc+4-0x1C*4), hex(0x3de0e8+4+0xC4*4), hex(0x3ddb20+4+0x11*4))"
→ 0x3de3a4 0x3de23c 0x3de23c 0x3de2f8 0x3de2d8 0x3de260 0x3de3fc 0x3ddb68
python3 -c "print(hex(0x900001>>24), hex((0x900001>>20)&0xF), hex(0x900001&0xFFFFF), hex(0x1200002>>24), hex((0x1200002>>20)&0xF), hex(0x1200002&0xFFFFF), hex(0x1400003>>24), hex((0x1400003>>20)&0xF), hex(0x1400003&0xFFFFF))"
→ 0x0 0x9 0x1 0x1 0x2 0x2 0x1 0x4 0x3
python3 -c "print([hex(0x495D80+i*4) for i in range(9)])"
→ ['0x495d80', '0x495d84', '0x495d88', '0x495d8c', '0x495d90', '0x495d94', '0x495d98', '0x495d9c', '0x495da0']
python3 -c "jal decode: ((pc+4)&0xF0000000)|((w&0x3FFFFFF)<<2)"
→ 0x3ddb50:0xc0f77ea→0x3ddfa8 0x3de0c8:0xc0f7908→0x3de420 0x3dd458:0xc0f799c→0x3de670
  0x3dd558:0xc0f799a→0x3de668 0x3de7dc:0xc0f9912→0x3e6448 0x3dd414:0xc0f79ec→0x3de7b0
  0x3ded80:0xc0f7476→0x3dd1d8 0x3e3398:0xc0f9192→0x3e4648 0x3e3410:0xc10a05a→0x428168
  0x3e3424:0xc10a0e8→0x4283a0 0x3e34b8:0xc10a180→0x428600
python3 -c "print([hex(s+8) for s in [0x3de0c8,0x3de2f8,0x3de340,0x3de3a4,0x3de3e0,0x3de3f4,0x3e3450,0x3e34c0,0x3e3d64,0x3e4888]])"
→ ['0x3de0d0', '0x3de300', '0x3de348', '0x3de3ac', '0x3de3e8', '0x3de3fc', '0x3e3458', '0x3e34c8', '0x3e3d6c', '0x3e4890']
```

## P18-2. Dynamic receipts (boot-p1q-1, 1 boot)

`$W/P1/run/boot-p1q-1.log`, 1,234 lines, 130,595 B, 17 blocks, CWD `$W/P1/run`,
env = p1p-2 env with WATCH = 10 addrs (`0x5e0080,88,90,98,a0,a8,b0,b8` +
`0x519ad4,0x519ae0`; 8B spacing per P17-1a range semantics), PROBE=1 kept on,
foreground 90 s, SIGTERM rc=-15. Binary `7a7d4b64` (fresh; §P18-3). Design note:
the brief's "targeted stub observation of `0x3ddfa8`/`0x3de420`" is executed as the
`0x5e00b8` W1-write `ra` receipt + `0x519AD4` select pcs (direct JALs bypass the HLE
stub histogram, P16-2f; `target=0x3de420`/`0x3ddfa8` print 0 lines again, §P18-2c).

### a. All 38 watch lines (thread=1 on all; no double-prints: 8B spacing, no overlap)

Init (11 lines):

| Line | addr + width | value | pc | ra | sp |
|---|---|---|---|---|---|
| :49–50 | `0x519ad0`/`0x519ae0` w16 | zeros | `0x10012c` | `0x0` | `0x0` |
| :58 | `0x519ad8` w4 | `0x5e0080` (table base; single print — overlaps only the `0x519ad4` range) | `0x3dccfc` | `0x3dcd00` | `0x1fffe90` |
| :59–66 | `0x5e0080`–`0x5e00b8` w8 ×8 | `0x0` | `0x3e64c8`–`0x3e64ec` step 4 (memset 64-loop) | `0x3dcd10` | `0x1fffe80` |

Entry-0 alloc + fill (6 lines; first life of the table):

| Line | addr + width | value | pc | ra | sp | Decodes to |
|---|---|---|---|---|---|---|
| :385 | `0x5e0080` w4 | `0x100000` | `0x3de6f8` | `0x3de69c` | `0x1fffdc0` | Lookup: state nibble := 1 |
| :386 | `0x5e0083` w1 | `0x0` | `0x3de704` | `0x3de69c` | `0x1fffdc0` | Lookup: index byte := 0 |
| :387 | `0x5e0080` w4 | `0x100001` | `0x3de72c` | `0x3de69c` | `0x1fffdc0` | Lookup: id := counter = 1 (first alloc → id 1) |
| :388 | `0x5e0094` w4 | `0x0` | `0x3ddb10` | `0x3ddafc` | `0x1fffe10` | `3DDAC0`: `+0x14` = `$a3` = 0 |
| :389 | `0x5e0090` w4 | `0x64` | `0x3ddb18` | `0x3ddafc` | `0x1fffe10` | `3DDAC0`: `+0x10` = `$a2` = 100 |
| :390 | `0x5e0080` w4 | `0x900001` | `0x3ddb24` | `0x3ddafc` | `0x1fffe10` | `3DDAC0`: nibble := 9 (parked `$a0` ✓) |

Entry-1 first life + select + complete (10 lines):

| Line | addr + width | value | pc | ra | sp | Decodes to |
|---|---|---|---|---|---|---|
| :391 | `0x5e00b0` w4 | `0x100000` | `0x3de6f8` | `0x3de69c` | `0x1fffd60` | Lookup: state := 1 |
| :392 | `0x5e00b3` w1 | `0x1` | `0x3de704` | `0x3de69c` | `0x1fffd60` | Lookup: index := 1 |
| :393 | `0x5e00b0` w4 | `0x1100002` | `0x3de72c` | `0x3de69c` | `0x1fffd60` | Lookup: id := 2 (counter now 2) |
| :394 | `0x5e00b0` w4 | `0x1200002` | `0x3dd544` | `0x3dd548` | `0x1fffdb0` | `3DD4E8`: nibble := 2 (delay of `jal 3DE800`) |
| :395 | `0x519ae0` w4 | `0x5e00b0` | `0x3de034` | `0x3ddfdc` | `0x1fffb40` | Enqueue: head := entry 1 |
| :396 | `0x519ae0` w4 | `0x0` | `0x3de0a0` | `0x3ddfdc` | `0x1fffb40` | Dequeue: head := 0 (queue empty) |
| :397 | `0x519ad4` w4 | `0x5e00b0` | `0x3de0b0` | `0x3de0b4` | `0x1fffb40` | Select entry 1 (= p1p-1 `:379`) |
| :398 | `0x5e00b8` w4 | `0x1` | `0x3de468` | `0x3de300` | `0x1fffb20` | W1 from site `0x3de2f8` (`ra`−8 ✓): `+4`==0, `$a0`=`$s2`=1 → flag 1 |
| :399 | `0x519ad4` w4 | `0x0` | `0x3de470` | `0x3de300` | `0x1fffb20` | W1 clears current (= p1p-1 `:380`) |
| :400 | `0x519ad4` w4 | `0x0` | `0x3de0b0` | `0x3de0b4` | `0x1fff8b0` | Tail-dequeue P3 empty-store (= p1p-1 `:381`; head provably 0) |

Slot clear + re-alloc (nibble 4/id 3) + re-select (11 lines):

| Line | addr + width | value | pc | ra | sp | Decodes to |
|---|---|---|---|---|---|---|
| :401–404 | `0x5e00b0`/`b4`/`b8`/`bc` w4 | `0x0` | `0x3e6508`/`0x3e6510`/`0x3e6518`/`0x3e651c` (memset 16-loop) | `0x3de7e4` | `0x1fffd20` | `3DE7B0` clears slot (`ra` = `0x3de7dc`+8 ✓; iters 2–3 at `+0x10`…`+0x2C` unwatched but implied by `$a2`=`0x30`) |
| :405 | `0x5e00b0` w4 | `0x100000` | `0x3de6f8` | `0x3de69c` | `0x1fffcd0` | Re-alloc: state := 1 (slot free: idx 0 still nibble 9) |
| :406 | `0x5e00b3` w1 | `0x1` | `0x3de704` | `0x3de69c` | `0x1fffcd0` | Re-alloc: index := 1 (same slot) |
| :407 | `0x5e00b0` w4 | `0x1100003` | `0x3de72c` | `0x3de69c` | `0x1fffcd0` | Re-alloc: id := 3 (counter monotonic) |
| :408 | `0x5e00b0` w4 | `0x1400003` | `0x3dd6b0` | `0x3dd688` | `0x1fffd20` | `3DD648`-site1: nibble := 4 (delay of `bnez $s4`) |
| :409 | `0x519ae0` w4 | `0x5e00b0` | `0x3de034` | `0x3ddfdc` | `0x1fffab0` | Enqueue: head := slot |
| :410 | `0x519ae0` w4 | `0x0` | `0x3de0a0` | `0x3ddfdc` | `0x1fffab0` | Dequeue: head := 0 |
| :411 | `0x519ad4` w4 | `0x5e00b0` | `0x3de0b0` | `0x3de0b4` | `0x1fffab0` | Select recycled slot (= p1p-1 `:382`; SAME addr, NEW request id 3/nibble 4) |

After `:411`: zero watch lines (28th transition never comes); then `:412`–`:413`
`sceCdRead lbn=0x5f1a3 ret=0x3e3b8c` (`BIGF` payload), `:414`–`:415` CD callback
pair, `:416` driver probe (p1o bytes).

### b. Derived tables

Current entry (`*(0x519AD4)`): 4 lines, same shape as p1p-1 (`entry1/clear/empty/slot`;
`0x5e0080` never a value — entry 0 never selected, not even transiently).
Queue head (`*(0x519AE0)`): 5 lines (`:50` init zero, `:395`/`409` in, `:396`/`410` out;
empty at `:400` and at end). Entry-0 `+8`: init `:60` only (never completed).
Entry-0 final words (watched): `+0`=`0x900001`, `+4`=`+8`=`+0xC`=0, `+0x10`=`0x64`,
`+0x14`=0, `+0x18`/`+0x1C`/`+0x20`/`+0x24`/`+0x28`/`+0x2C`=0 (zero writes after init).
Counter: ids 1→2→3 across the three allocs (lookup `$a1` = pre-increment counter).

### c. Ladder delta vs boot-p1p-2 (1,197 lines, 127,111 B)

| Rung | boot-p1p-2 | boot-p1q-1 (1,234 lines, 130,595 B) | Delta |
|---|---|---|---|
| Thread-1 pc | `0x3e5980` ×15, `0x423c90` ×1 (blk0), `0x3dd278` ×1 (blk11) | `0x3e5980` ×16 (blk0–15), `0x0` ×1 (blk16, status=1; teardown-race shape, plus `id=-1` zero stack line) | Same park family; last-block teardown line |
| Thread-1 sch | 81/77/82/82/82/80/79/69/82/82/81/79/77/68/81/82/82 | 84/82/81/80/81/81/81/80/78/68/81/82/81/79/78/68/81 | Same regime (~77–84) |
| Missing target | 0 | 0 | None |
| Stub distinct b0 / b1–16 | 486 / 18 | 486 / 18; b0 30/30 rows identical modulo `count` | None |
| Syscall distinct b0 / b1+ | 27 / 3; 20 printed ids | 27 / 3; same 20 ids (sort-compared, identical incl. `0x15`/`0x17`) | None |
| CD callback | :377–378 | :414–415 (same func/cb) | Line shift only |
| Probe | 1 (:379, p1o bytes) | 1 (:416, p1o bytes) | Line number only |
| Threads 2/4/5 | sema-parked 26/29/30 @ `0x423de8` | Same (blk0 ids/entries/priorities/stacks identical) | None |
| VIF MPG/MSCAL | 0 | 0 | None |
| GIF/GS | 2 / 66 / 122 / 33 / 8 | 2 / 66 / 122 / 33 / 8 | None |
| `run:tick` | 7 | 7 | None |
| Presented frame | None | None (sole `frame` hit = raylib TIMER line :46) | None |
| Crash | 0 | 0 | None |
| Dormant / start-thread | 40 / 4 | 40 / 4 | None |
| SIF module lines | 6 (`irx` grep) | 6 | None |
| `firstRa=0x3dd290` / `0x3dd280` | 17 / 17 | 17 / 17 | None |
| `target=0x3de420` / `0x3ddfa8` | 0 / 0 | 0 / 0 | None (direct JALs; receipt via §P18-2a instead) |

## P18-3. Binaries and commits

| Binary / ref | sha256 / sha | Sources / state |
|---|---|---|
| `/tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner` (boot-p1q-1) | `7a7d4b645094d3ad82746a7d420b223422bf6444e5d06f6e56998e9057f5b4cd` | `e73e36a` tree, no rebuild (fresh; §P18-0 pre-boot check) |
| `ps2x_tests` | Not re-run (no source change; P15-1c 424/425 stands for this tree) | Same tree `e73e36a` |
| `PS2Recomp` branch `ssx3` HEAD | `e73e36a` | No fork commit (env-only boot; worktree sole `M` = pre-existing generated `runner/register_functions.cpp`, never added) |
| Fork push | `git push fork ssx3` from fork clone only | Up-to-date check (expect nothing to push) |
| This report | `[P1q]` commit (two trailers; local only) | Sole ssx3-repo change; no `runner/`, log, or `._*` added |

## P18-4. Exact commands

From `$W/PS2Recomp` (fork) unless noted; `$W=/Volumes/Extreme SSD/ps2recomp-spike`, `$O=$W/P1/output`,
`$R=$W/PS2Recomp`, `$LOG=$W/P1/run/boot-p1q-1.log`:

```
# Step 1 (lease-free static; lease absent throughout)
re-read REPORT Part 17 + Part 16 P16-2d-2f (paged reads)
grep -rn "jal func_3DDFA8/3DE420/3DE670" $O (caller pcs); python3 range lookups (ssx3-functions.csv)
read $O/sub_003D{CC88,CBD8,DD1D8,DDAC0,DED50,DD4E8,DCF70,DE670,DE420,DDFA8(dequeue+dispatch),E6448,DE7B0,DE800,DDDF0}
grep regions: 3DD438/3DD5A0/3DD648/3DD7E0/3DDC30 fills, W2 (0x3dd82c) + W3 (0x3ddd20) predicates,
  3E3350/3E3478/3E3B00/3E4648 W1 neighborhoods, 3ED678 (ruled out), 0x3ddc00 trampoline (callerless)
P6 grep (ssx3-decomp-names.csv: BIG_*/str*/MUTEX/SYNCTASK/FILESYS/iFILESYS rows)
python3 ELF batch (101 words + jump table 9 + nibble luis + JAL decodes); python3 hex checks (each pasted §P18-1h)
# Step 2 (lease protocol)
cat /tmp/ssx3-host-lease (absent 15:32:35 UTC); pgrep -f "[p]s2EntryRunner" (exit 1)
shasum ps2EntryRunner (7a7d4b64 fresh); git log/status (e73e36a); ls ISO + ELF
printf 'P1q\n' > /tmp/ssx3-host-lease (15:33:22 UTC)
(write /tmp/p1q-boot1.py: p1p-2 env, WATCH 10 addrs, probe on; diff vs p1p-boot2.py)
python3 /tmp/p1q-boot1.py (CWD $W/P1/run, 90 s, SIGTERM rc=-15, 130595 B; returned 15:34:53 UTC)
log greps: watch 38 (:49/:50/:58-:66/:385-:411); driver-entry 1 (:416); cd pair (:414-415);
  cd reads (early ret=0x3e3694 + :412 ret=0x3e3b8c); value=0x5e0080 census (only :58)
ladder sweeps: thread pcs/sch per block; stub 486/18 + b0 30-row comm; syscall 27/3 + 20-id
  sort-compare (identical); gs:/run:tick/frame/crash/dormant/start-thread/missing-target;
  firstRa 17/17; SIF 6; Blk16 teardown line noted
rm -f /tmp/ssx3-host-lease (15:35:58 UTC); ls (absent); pgrep (none)
# Step 3
(edit_file append Part 18 in 4 chunks; commit below)
git -C /Users/bradrichardson/dev/ssx3 add -f local/research/P1/REPORT.md
git -C /Users/bradrichardson/dev/ssx3 commit -m "[P1q] ..." (two trailers; NO push there)
git -C $R push fork ssx3 (up-to-date check; the only push allowed)
```

Env delta vs boot-p1p-2: WATCH `0x5e0088`→10 addrs (`0x5e0080,88,90,98,a0,a8,b0,b8`,
`0x519ad4,0x519ae0`) only. Source delta: none.

## P18-5. What I could not do

- Run the reserve 2nd boot (not needed): still-unwatched words it could close directly —
  recycled-slot `+0x10`…`+0x2C` (fill predicted from `3DD648`-site1 reads, only `+0` watched),
  `*(0x519AC0)`/`*(0x519AB8)` (P2/P4 values; passed-at-dequeues inferred, not traced),
  recycled-slot `+0x1C` (branch inferred from absent `0x3de3a4` clear), `*(0x519AE4)`
  (path-A/B branch value; path B proven by absent `+0x24` write instead).
- Name the `0x3e33b0`-poll caller (no `jal` found tree-wide) or the `0x3ddc00`-trampoline
  caller (word `0x0c0f7700` absent); both are pointer-reached (registration sites unknown).
- ID `0x428168`/`0x4283A0`/`0x428600` (no P6 rows; JAL targets verified, roles not traced).
- Read `3DD648`-site2 fill sources (nibble + enqueue pc recorded; `+0x10`/`+0x14` not traced).
- Trace the CD-completion→W1 gap (callback `0x3e3ad8` queued+started, W1 site `0x3e3d64`
  never reached): poll-vs-lost-wake undetermined. Entry 0 needs selection first anyway
  (its case-7 completion is synchronous), so this gap sits behind, not beside, the P1q question.
- No runtime fix (per the brief): selection/completion analysis + receipts only. The
  sema-26 non-delivery remains out of scope, untouched.
- One boot used (of the brief's max two): no A/B on any rung.

---

## Part 19 (P1r): worker wakes once on 3E4648's signal, issues the CD read, re-parks before the callback's signal; site #9 never reached

Brief `local/muse/prompts/P1r.md`. Static worker-path + registration analysis, then 1
dynamic receipt boot; no fix. Tables, no verdicts. Stale-reading guard: Part 18
(P18-1f sites #7/#9/#10, P18-1g CD→W1 break, P18-2a :411–:416, P18-5 poll-vs-lost-wake
residue) + Part 17 §P17-1 (sema-26 context, out of scope) re-read before acting.

## P19-0. Lease record

| Event | Value |
|---|---|
| Lease at session start | `M10` (observed 16:11:44Z) |
| Polls (no boot attempted yet) | 16:16:53Z absent; 16:20:22Z `M10`; 16:23:22Z absent |
| Waits log | `$W/P1/run/p1r-waits.log` (6 lines: 3 holds/absent polls + claim + release) |
| Pre-boot checks (16:23:32Z) | `pgrep -f "[p]s2EntryRunner"` exit 1 (none); binary `7a7d4b64` fresh (matches P18-3, no rebuild); fork HEAD `e73e36a`; ISO 3005415424 B + ELF 3890784 B present |
| Claim | `printf 'P1r\n' > /tmp/ssx3-host-lease` 16:23:32Z (file absent, verified twice), immediately before boot-p1r-1 |
| Boot 1 | 90 s foreground, SIGTERM rc=-15 |
| Release | `rm -f /tmp/ssx3-host-lease` 16:27:31Z; verified absent; `pgrep` exit 1 |
| Second boot | None (Step-1 question closed by boot 1; reserve unused) |
| `adb` | Not used |

## P19-1. Static: worker path, gates, registration (no lease, no boot)

Conventions: `3E3B00` fused file `sub_003E3B00` (`0x3e3b00`–`0x3e3d78`, build map
`ssx3-functions.csv`); `3E33B0` = `0x3e33b0` label inside fused `sub_003E3350`
(`0x3e3350`–`0x3e3478`); stale split duplicates (`sub_003E3BE0`, `sub_003E33B0`,
`sub_003E4000`) exist in `$O` but are NOT in the build map (sweep-only). All words
ELF-verified §P19-1e; all hand hex machine-checked §P19-1e.

### a. Callback → worker wake link

| Item | Value |
|---|---|
| Callback | `0x3e3ad8` (in `sub_003E39A8`): `lui $v0,0x52` + `lw $a0,-0x63B4($v0)` = `*(0x519C4C)` + `jal 0x423DD0` (iSignalSema, v1=`-0x43`) |
| Worker wait | `0x3e3c18` (in worker loop `0x3e3be0`): `jal 0x423DE0` (WaitSema, v1=`0x44`) with `$a0` = `*(0x519C4C)` (`lw $a0,0xC($s2)`, s2=`0x519C40`) |
| Sema id | `*(0x519C4C)` = `0x1A` = 26 (boot-1 :175 @ `0x3e43fc` = CreateSema ret; thread 2 `waitId=26` every block) |
| Sema create | `0x3e43bc` `jal 0x423DA0` (CreateSema) in `0x3e4040`; block `$a0`=`$sp+0x30`: `[+4]`=max `0x20` (`0x3e43b8`), `[+8]`=init 0 (`0x3e43b4`); attr/option (`[+16]`/`[+20]`) have no store anywhere in the function (stale stack words; runtime observed `attr=0x0` in start-thread line) |

### b. Worker-loop gates (second half `0x3e3be0`, thread 2)

One row per predicate between wake and W1 `jal 0x3e3d64`. s1=`0x520000`
(`-0x63C0`→`0x519C40` state), s2=`0x519C40`, s0=`0x519C60` (checks §P19-1e).

| # | pc (word ✓) | Condition (fail → effect) | Pass → effect |
|---|---|---|---|
| G0 | `0x3e3c18` (`0xc108f78`) | WaitSema(`*(0x519C4C)`) blocks | Returns to `0x3e3c20` |
| G1 | `0x3e3c20` (`0xc1008c0`) + `0x3e3c28` (`0x14400004`) | `sceCdGetError()`==0 → fall to G2 (delay always loads state→`$v1`) | ≠0 → `0x3e3c3c` (G3 error path) |
| G2 | `0x3e3c30`/`0x3e3c34` (`0x30620008`/`0x10400011`) | state&8==0 → `0x3e3c7c` (G4; delay precomputes state&1) | ≠0 → `0x3e3c3c` (G3) |
| G3 | `0x3e3c3c`–`0x3e3c48` (`0x2402fff7`/`0x622024`/`0x30630002`/`0x1060fff3`) | state&2==0 → store `state&~8` (delay `0x3e3c4c`) + loop to G0 | ≠0 → `0x3e3c50` (G5) |
| G4 | `0x3e3c7c` (`0x1040000a`) | state&1==0 → `0x3e3ca8` (G6; delay `v1=state&~2`) | ≠0 → memcpy block + `jal 0x3E6574` @ `0x3e3ca0`, state:=`state&~1` (`0x3e3c9c`), then G6 |
| G5 | `0x3e3c50`–`0x3e3c58` (`0x8e420010`/`0x2442ffff`/`0x18400005`) | `--*(0x519C50)`≤0 (stored `0x3e3c5c`) → `0x3e3c70`: state:=`(old&~8)\|4`, loop to G0 | >0 → `jal 0x3E3B00` @ `0x3e3c60` (ISSUE), loop to G0 |
| G6 | `0x3e3ca8`/`0x3e3cac` (`0x8e070004`/`0x18e00029`) | `*(0x519C64)`≤0 → `0x3e3d54` = W1 PRELUDE (load state, `&~2`, `$a0`=1, `jal 0x3DE420` @ `0x3e3d64`, delay store) | >0 → size-split S1/S2 below (never reaches #9 this pass; issues @ `0x3e3d44`, loops to G0) |

Size-split (remaining>0 only): S1 `0x3e3cd4` (`0x10c00007`, `$a2`=`rem<0x800`):
taken→`0x3e3cf4`; not-taken→`0x3e3cdc` block (state\|=1) →`0x3e3d38`. S2 `0x3e3cf8`
(`0x10400007`, `(rem-base)&0x3F`): taken→`0x3e3d18` (state&=−2); not-taken→`0x3e3d00`
block (state\|=1) →`0x3e3d38`. Join `0x3e3d38`: `*(0x519C64)`−=`*(0x519C60)`,
`jal 0x3E3B00` @ `0x3e3d44`, loop to G0.

Issuer retry gates (first half `0x3e3b00`, runs on whichever thread calls it):
R1 `0x3e3b70` (`0x1040000c`, `$s2`<3): exhausted→`0x3e3ba4`.
R2 `0x3e3b8c` (`0x1040fff2`, `sceCdRead` ret @ `0x3e3b84`): 0→retry via `0x3e3b58`
(delay `$v0`=`$s2`+1; `0x3E35B0` sleep + `sceCdSync` @ `0x3e3b64`); ≠0→success:
`$s4`=1, state\|=2 (`0x3e3b9c`/`0x3e3ba0`, s0−0x1C=`0x519C40`).
R3 `0x3e3ba4` (`0x16800005`, `$s4`): 0→state\|=6 (`0x3e3bb4`/`0x3e3bb8`,
retry-exhausted pattern); ≠0→return.

Site-#7 gates (`0x3e33b0` poll, runs on thread 1 via §P19-1c): A1 `0x3e33d4`
(`0x10600020`, `*(0x519C20)`): 0→exit `0x3e3458`. A2 `0x3e33ec` (`0x14640005`,
`*(0x450C40)` vs `*(0x519C24)`): ≠→`0x3e3404` (`0x428168` path); ==→A3 `0x3e33fc`
(`0x10620006`, `*(0x450C4C)` vs `*(0x519C2C)`): ==→`0x3e3418` (skip `0x428168`);
≠→`0x3e3404`. Join: `0x4283A0` @ `0x3e3424`, `*(0x450C40)`:=old `*(0x519C24)`,
`*(0x450C4C)`:=`*(0x519C2C)`+`*(0x519C30)`, flag:=0 (`0x3e344c`), W1 @ `0x3e3450`.
Arm (case-2 non-1 path, `0x3e3350`): `*(0x519C20)`:=1 + args→`0x519C24`/`28`/`2C`/`30`
(`0x3e3378`–`0x3e338c`, contiguous, no branch between). Topbyte==1 path instead
`jal 0x3E4648` @ `0x3e3398` (gate `0x3e3368`, inline, same thread).

### c. Poll registration + worker trigger (P18-1f residues closed statically)

| Target | Registration (word ✓) | Dispatch / trigger |
|---|---|---|
| `0x3e33b0` poll (site #7) | `0x3e3024`/`0x3e302c` (`lui $a0,0x3E`+`addiu 0x33B0`) → `$a0`=`0x3e33b0`, `$a1`=`$a2`=0 → `jal 0x3E57F8` @ `0x3e3048`; `0x3e3020` ← `jal` @ `0x3dcd5c` (init `sub_003DCC88`, delay `$a0`=`$s5`, `$a1`=`$v0`: 0 if `*(0x450C60)`==0 else computed) | `0x3E57F8` inserts into 16-slot table `0x51ED98` (`0x520000`−`0x1268`, stride `0x10`: +0 func, +4 flag, +8 due, +0xC busy; guard `*(0x450E00)`++/−−; clear `memset(.,0,0x100)` @ `0x3e57d0`; unregister `0x3E58C8` zeroes match); swept by thread-1 park loop `0x3E5928` (`$s0`=table+`0xC`, 16 iters): skip if func==0 (`0x3e5984`), `*(0x450DD0)`<due (`0x3e5998`), busy≠0 (`0x3e59a4`); else busy:=1 + `jalr` @ `0x3e59b8` (`0xc0f809` ✓) |
| `0x3e4000` poll (second slot) | `0x3e443c`/`0x3e4444` (`lui`+`addiu 0x4000`) → `$a0`=`0x3e4000`, `$a1`=0 → `jal 0x3E57F8` @ `0x3e4450` (in `0x3e4040`) | Same table/`jalr`; body: if (`*(0x519C40)`&6)==6 (`0x3e4014`) clear bits 1–2 (`0x3e401c`/`0x3e4020`/`0x3e4028`) + `jal 0x3E3D78` @ `0x3e4024`, else return 0 |
| Worker thread `0x3e3be0` (site #9 host) | `0x3e43c4`/`0x3e43d0` (`lui $v1,0x3E`+`addiu 0x3BE0`) → `$v1`=`0x3e3be0`; CreateThread block `$a0`=`$sp` (`0x3e43e8`): `[+4]`=entry (`0x3e43e4`), `[+8]`=stack `0x51AC80` (`0x3e43ec`), `[+0xC]`=size `0x4000` (`0x3e43f4`), `[+0x10]`=gp `0x4A30F0` (`0x3e43f0`), `[+0x14]`=prio `0xC` (`0x3e43f8`), `[+0x20]`=0 (delay `0x3e4404`); `jal 0x423BA0` (CreateThread) @ `0x3e4400`, `jal 0x423BC0` (StartThread) @ `0x3e4410`; `0x3e4040` ← `jal` @ `0x3dcd44` (init) | Boot-1 start-thread line matches exactly: `id=2 func=0x3e3be0 stack=0x51ac80 stack_size=0x4000 gp=0x4a30f0 priority=12`; `*(0x519C48)`=2 @ `0x3e4414` (StartThread ret = tid) |
| First half `0x3e3b00` (issuer) | Direct `jal` ONLY from worker loop: @ `0x3e3c60` (G5) and @ `0x3e3d44` (size-join); JAL word `0xc0f8ec0` absent tree-wide otherwise; `jal`-words to `0x3e33b0` (`0xc0f8cec`), `0x3e3be0` (`0xc0f8ef8`), `0x3e3ad8` (`0xc0f8eb6`) absent tree-wide (pointer/thread/callback-reached only) | Runs on the caller's thread (boot-1: thread 2, :430 `:433` sp=`0x51exxx`) |
| Callback `0x3e3ad8` | `sceCdCallback`(`0x4008A0`) sites: clear `$a0`=0 @ `0x3e3dac` (head `0x3e3d78`); set `$a0`=`0x3e3ad8` @ `0x3e3fb4` (tail `0x3e3d78` ← `jal` @ `0x31ad90` AND ← `jal` @ `0x3e4024` poll path) and @ `0x3e4430` (in `0x3e4040` init); `sceCdInitEeCB`(`0x400A78`) before each set: stack `0x51A480`+`0x800` → top `0x51AC80` (= worker stack base) | Runtime `queueCdCallback` → scheduler invocation `func=1 cb=0x3e3ad8` (boot-1 :432/:434) |
| `0x3e3d78` prime (SignalSema) | `jal 0x423DC0` (SignalSema) @ `0x3e3fc4` with `$a0`=`*(0x519C4C)` (delay `lw $a0,0xC($v1)`, v1=`0x519C40`) | Boot-1: tail never ran (no `sceCdInitEeCB ... ret=0x3e3fb0` print; `0x3e3d78` single-exit via tail `jr` @ `0x3e3ff8`; no thread inside it) → prime never fired; :428 wake is 3E4648 @ `0x3e48b0` instead (§P19-2b) |

### d. Lost-wake candidates (flag/counter × writer pc × timing)

| # | Flag/counter | Writer pc(s) | Timing vs waiter | Shape |
|---|---|---|---|---|
| L1 | Sema-26 count (host-side, unwatchable) | init 0 @ `0x3e43bc`-block; +1 @ `0x3e48b0` (3E4648, thread 1, boot-1 :426–:427 window); +1 @ `0x3e3ae8` (callback, post-:434); prime @ `0x3e3fc4` never fired (this boot) | W1: `0x3e48b0` signal lands while worker parked (first wait) → wake :428. W2: callback signal lands while worker RE-parked (:433→:434 order) → no wake (delivery mechanism = out-of-scope sema-26 item; ORDER is the in-scope receipt) | Signal-during-park, not signal-before-wait |
| L2 | `*(0x519C50)` retry counter | `3` @ `0x3e48ac` (3E4648, thread 1, :426); `3→2` @ `0x3e3c5c` (worker, :429) | Set (thread 1) strictly before worker's G5 read (order :426→:429); same-epoch handoff, no pre-arm staleness | Consumed once, then worker re-parks; no second fill |
| L3 | `*(0x519C64)` remaining (G6 predicate) | `0` @ `0x3e4790` (3E4648, thread 1, :424) | Set before any worker G6 read; worker never reaches G6 (re-parks at G0) | Gate would pass (`0≤0`→W1); unreached |
| X1 (excluded) | `*(0x519C20)` async flag + `0x450C40`/`0x450C4C` | Arm @ `0x3e3378`–`0x3e338c` (thread 1); test+clear @ `0x3e33d4`/`0x3e344c` (thread 1 park sweep) | Same-thread arm/poll; and boot-1: zero writes (site #7 never armed — case 2 took topbyte==1 path A) | No cross-thread race; not taken |
| X2 (excluded) | State bits 1/3/0/8 in worker loop | Set by issuer synchronously in worker thread (`0x3e3ba0`/`0x3e3bb8`) or worker itself (`0x3e3c4c`/`0x3e3c78`/`0x3e3c9c`) | Synchronous, no race | Except cross-thread clear of pattern 6 by `0x3e4000` poll (thread 1): pattern 6 never occurred (states observed: 0, `0xA`, 2) |

### e. ELF verification words + machine-check paste block

Batch word check (77 addrs; every word matched its disassembly comment in `$O`;
ELF `$W/P1/SLUS_207.72` = `$W/P1/cd/SLUS_207.72`, sha256 `1b49d05c…af7bc`, equal;
mapping file-off = va−`0x100000`+`0x1000`):

```
0x3e3c18 0xc108f78 / 0x3e3c1c 0x8e44000c / 0x3e3c20 0xc1008c0 / 0x3e3c28 0x14400004
0x3e3c2c 0x8e239c40 / 0x3e3c30 0x30620008 / 0x3e3c34 0x10400011 / 0x3e3c38 0x30620001
0x3e3c3c 0x2402fff7 / 0x3e3c40 0x622024 / 0x3e3c44 0x30630002 / 0x3e3c48 0x1060fff3
0x3e3c4c 0xae249c40 / 0x3e3c50 0x8e420010 / 0x3e3c54 0x2442ffff / 0x3e3c58 0x18400005
0x3e3c5c 0xae420010 / 0x3e3c60 0xc0f8ec0 / 0x3e3c70 0x34820004 / 0x3e3c78 0xae229c40
0x3e3c7c 0x1040000a / 0x3e3c80 0x741824 / 0x3e3c9c 0xae239c40 / 0x3e3ca0 0xc0f995d
0x3e3ca8 0x8e070004 / 0x3e3cac 0x18e00029 / 0x3e3cb0 0x28e60800 / 0x3e3cd4 0x10c00007
0x3e3cf8 0x10400007 / 0x3e3d44 0xc0f8ec0 / 0x3e3d54 0x8e229c40 / 0x3e3d58 0x2403fffd
0x3e3d5c 0x24040001 / 0x3e3d60 0x431024 / 0x3e3d64 0xc0f7908 / 0x3e3d68 0xae229c40
0x3e3b6c 0x2a420003 / 0x3e3b70 0x1040000c / 0x3e3b84 0xc10077e / 0x3e3b8c 0x1040fff2
0x3e3b9c 0x34420002 / 0x3e3ba0 0xae02ffe4 / 0x3e3ba4 0x16800005 / 0x3e3bb4 0x34420006
0x3e3bb8 0xac629c40 / 0x3e3ad8 0x3c020052 / 0x3e3ae0 0x8c449c4c / 0x3e3ae8 0xc108f74
0x3e3024 0x3c04003e / 0x3e302c 0x248433b0 / 0x3e3048 0xc0f95fe / 0x3e3fb0 0x3c04003e
0x3e3fb4 0xc100228 / 0x3e3fb8 0x24843ad8 / 0x3e3fc4 0xc108f70 / 0x3e43c4 0x3c03003e
0x3e43d0 0x24633be0 / 0x3e43bc 0xc108f68 / 0x3e43fc 0xae02000c / 0x3e4400 0xc108ee8
0x3e4410 0xc108ef0 / 0x3e4430 0xc100228 / 0x3e4434 0x24843ad8 / 0x3e4450 0xc0f95fe
0x3dcd44 0xc0f9010 / 0x3dcd5c 0xc0f8c08 / 0x3e4024 0xc0f8f5e / 0x3e59b8 0xc0f809
0x3e33d4 0x10600020 / 0x3e33ec 0x14640005 / 0x3e33fc 0x10620006 / 0x3e3378 0xac689c20
0x3e48ac 0xaca30010 / 0x3e4790 0xae020004 / 0x3de380 0xc0f8cd4 / 0x3de394 0xc0f8cd4
0x3de364 0x5080000a
```

Machine-check paste block (every hand computation in §P19-1; command then `→` output):

```
python3 -c "branch targets: pc+4+off*4 ..."
→ 0x3e3c3c 0x3e3c7c 0x3e3c18 0x3e3c70 / 0x3e3ca8 0x3e3d54 0x3e3cf4 0x3e3d18
→ 0x3e3ba4 0x3e3b58 0x3e3bbc 0x3e402c / 0x3e3458 0x3e3404 0x3e3418 0x3de3a4 0x3de390
python3 -c "print(hex(0x520000-0x63C0), hex(0x520000-0x63A0), hex(0x520000-0x63A4), hex(0x520000-0x63E0), hex(0x520000-0x63B4))"
→ 0x519c40 0x519c60 0x519c5c 0x519c20 0x519c4c
python3 -c "print(hex(0x520000-0x1268), hex(0x520000-0x5B80), hex(0x51A480+0x800), hex(0x520000-0x5380), hex(0x4A0000+0x30F0))"
→ 0x51ed98 0x51a480 0x51ac80 0x51ac80 0x4a30f0
python3 -c "print(s2/s0 offsets...)"
→ 0x519c4c 0x519c50 0x519c7c 0x519c54 0x519c60 / 0x519c64 0x519c60 0x519c68 0x519c6c 0x519c70 0x519c74
python3 -c "masks -9/-2/-3/-7 and ~8/~2"
→ 0xfffffff7 0xfffffffe 0xfffffffd 0xfffffff9 (+ ~8=0x8 ~2=0x2)
python3 -c "jal decode: ((pc+4)&0xF0000000)|((w&0x3FFFFFF)<<2)"
→ 0x3e3c18→0x423de0 0x3e3c20→0x402300 0x3e3ca0→0x3e6574 0x3e3c60/0x3e3d44→0x3e3b00
  0x3e3d64→0x3de420 0x3e3b84→0x401df8 0x3e3ae8→0x423dd0 0x3e3048/0x3e4450→0x3e57f8
  0x3e3fb4/0x3e4430→0x4008a0 0x3e3fc4→0x423dc0 0x3e43bc→0x423da0 0x3e4400→0x423ba0
  0x3e4410→0x423bc0 0x3dcd44→0x3e4040 0x3dcd5c→0x3e3020 0x3e4024→0x3e3d78 0x3de380→0x3e3350
python3 -c "jal words for 0x3e33b0/0x3e3b00/0x3e3be0/0x3e3ad8/0x3e3020/0x3e3d78/0x3e4040 (absence search)"
→ 0xc0f8cec 0xc0f8ec0 0xc0f8ef8 0xc0f8eb6 / 0xc0f8c08 0xc0f8f5e 0xc0f9010
```

### f. P6 names

No rows for any touched function (`3E3020`/`3350`/`33B0`/`3B00`/`3BE0`/`3D78`/
`4040`/`4000`/`57F8`/`58C8`/`5928`/`4648`/`39A8`/`35B0`/`6574`; re-grepped
`local/research/P6/ssx3-decomp-names.csv`, 802 lines).

## P19-2. Dynamic receipt (boot-p1r-1, 1 boot)

`$W/P1/run/boot-p1r-1.log`, 1,253 lines, 132,454 B, 17 blocks, CWD `$W/P1/run`,
env = p1q env with WATCH = 11 addrs (`0x519c40,48,50,60,68,70,78,0x519c20,28`,
`0x450c40,48`; 8B spacing, no overlap), PROBE=1 kept on, foreground 90 s, SIGTERM
rc=-15. Binary `7a7d4b64` (fresh; §P19-3). Design: §P19-1 gates G0–G6/R1–R3/A1–A3
plus init stores; `0x519C30` covered by implication (contiguous arm block), table
`0x51ED98` not watched (slot index unknown statically).

### a. All 57 watch lines

Zero-init (9 lines, 5 writes; w16 overlap doubles per P17-1a range semantics):

| Line | addr + width | value | pc | thread |
|---|---|---|---|---|
| :49–50 | `0x519c20` w16 ×2 | zeros | `0x10012c` | 1 |
| :51–52 | `0x519c40` w16 ×2 | zeros | `0x10012c` | 1 |
| :53 | `0x519c50` w16 | zeros | `0x10012c` | 1 |
| :54–55 | `0x519c60` w16 ×2 | zeros | `0x10012c` | 1 |
| :56–57 | `0x519c70` w16 ×2 | zeros | `0x10012c` | 1 |

Memset 64-loop (7 lines, `ra`=`0x3e4098` = in `0x3e4040`, thread 1, sp=`0x1ffec70`):

| Line | addr + width | value | pc |
|---|---|---|---|
| :65–71 | `0x519c40`/`48`/`50`/`60`/`68`/`70`/`78` w8 | `0x0` | `0x3e64c8`–`0x3e64ec` |

Early lbn register (20 lines, thread 1; `0x519c6c` = lbn for the `ret=0x3e3694`
early reader, pairs with :73–:167 CD reads):

| Line | value | pc | ra | sp |
|---|---|---|---|---|
| :72 | `0x10` | `0x3e4138` | `0x3e4128` | `0x1ffec80` |
| :86 | `0x105` | `0x3e3938` | `0x3e38d8` | `0x1ffd900` |
| :95–:160 (14 lines) | `0x107` | `0x3e3938` | `0x3e38d8` | `0x1ffcf40` |
| :161 | `0x105` | `0x3e3938` | `0x3e3864` | `0x1ffd900` |
| :170 | `0x108` | `0x3e3938` | `0x3e38d8` | `0x1ffcf40` |
| :171 | `0x105` | `0x3e3938` | `0x3e38d8` | `0x1ffd900` |
| :172 | `0x10` | `0x3e3938` | `0x3e3864` | `0x1ffe2c0` |

Init stores (9 lines, thread 1):

| Line | addr + width | value | pc | ra | Decodes to |
|---|---|---|---|---|---|
| :173 | `0x519c78` w4 | `0x5e3980` | `0x3e4380` | `0x3e4350` | `sw $a1,0x38($s0)` |
| :174 | `0x519c44` w4 | `0xa3` | `0x3e4388` | `0x3e438c` | delay of `jal 0x3E39A8` |
| :175 | `0x519c4c` w4 | `0x1a` (26) | `0x3e43fc` | `0x3e43c4` | CreateSema ret = sema id |
| :176 | `0x519c48` w4 | `0x2` | `0x3e4414` | `0x3e4418` | StartThread ret = tid 2 |
| :179 | `0x519c7c` w4 | `0x519c80` | `0x3e4448` | `0x3e4438` | pointer init |
| :180 | `0x450c48` w4 | `0x2` | `0x3e305c` | `0x3e3050` | `0x3e3020` unconditional (delay) |
| :181 | `0x450c48` w4 | `0x3` | `0x3e306c` | `0x3e3050` | `$a1`≠0 path taken → `*(0x450C60)`≠0 at init |
| :182 | `0x450c44` w4 | `0x1` | `0x3e3074` | `0x3e3050` | same path |
| :183 | `0x450c44` w4 | `0x1` | `0x3ddedc` | `0x3ddeb8` | second writer (`3DDDF0`), same value |

Completion-epoch fills + worker progress (12 lines; NO watch line after :433):

| Line | addr + width | value | pc | thread | ra | sp | Decodes to |
|---|---|---|---|---|---|---|---|
| :419 | `0x519c68` w4 | `0x0` | `0x3e46c0` | 1 | `0x3e33a0` | `0x1fffa50` | 3E4648 fill (topbyte==1 path A) |
| :420 | `0x519c74` w4 | `0x9d0800` | `0x3e46cc` | 1 | `0x3e33a0` | `0x1fffa50` | buf (later CD buf) |
| :421 | `0x519c40` w4 | `0x0` | `0x3e4768` | 1 | `0x3e33a0` | `0x1fffa50` | state clear |
| :422 | `0x519c60` w4 | `0x800` | `0x3e4770` | 1 | `0x3e33a0` | `0x1fffa50` | base/chunk |
| :423 | `0x519c70` w4 | `0x1` | `0x3e4774` | 1 | `0x3e33a0` | `0x1fffa50` | — |
| :424 | `0x519c64` w4 | `0x0` | `0x3e4790` | 1 | `0x3e33a0` | `0x1fffa50` | remaining = 0 (G6 would pass) |
| :425 | `0x519c6c` w4 | `0x5f1a3` | `0x3e47a8` | 1 | `0x3e33a0` | `0x1fffa50` | lbn (later CD lbn) |
| :426 | `0x519c50` w4 | `0x3` | `0x3e48ac` | 1 | `0x3e33a0` | `0x1fffa50` | retry counter = 3 |
| :427 | `0x519c40` w4 | `0xa` | `0x3e48b4` | 1 | `0x3e48b8` | `0x1fffa50` | state = 10 (after `0x3e48b0` SignalSema(26), silent syscall) |
| :428 | `0x519c40` w4 | `0x2` | `0x3e3c4c` | 2 | `0x3e3c28` | `0x51ec20` | WORKER wake: G1(0)→G2(8)→G3: `0xA&~8`=2, bit1 set → G5 |
| :429 | `0x519c50` w4 | `0x2` | `0x3e3c5c` | 2 | `0x3e3c28` | `0x51ec20` | WORKER G5: `3→2` >0 → ISSUE @ `0x3e3c60` |
| :433 | `0x519c40` w4 | `0x2` | `0x3e3ba0` | 2 | `0x3e3b8c` | `0x51ebb0` | WORKER issuer success (R2, state\|=2, no-op) |

Interleaved CD/callback/probe: :430–:431 `sceCdRead lbn=0x5f1a3 sectors=1
buf=0x9d0800 ret=0x3e3b8c` + `BIGF` payload (`42494746147c1a00`); :432 queued
`func=1 cb=0x3e3ad8`; :434 start (same); :435 driver probe (p1o bytes,
`sp=0x1fffe80 ra=0x3ded88 sourcePc=0x3ded80 checkpointed=0`). Order: :429 (issue
call) → :430 (read) → :432 (queued) → :433 (issuer store) → :434 (callback
start). Early reads: 20 `ret=0x3e3694` lines (:73–:167, lbn `0x10`/`0x105`–`0x117`
buf `0x519c80`); :178 `sceCdInitEeCB stack=0x51a480 size=0x800 ret=0x3e442c`
(init site; NO `ret=0x3e3fb0` line = §P19-1c prime never fired).

Zero-count addrs (no line beyond zero-init): `0x519C20` (site-#7 flag — never
armed), `0x519C28`, `0x450C40` (zero lines at all). Coverage gaps (in no 8B
window): `0x519C30`–`0x3F`, `0x519C58`–`0x5F`, `0x519C80`+.

### b. Derived answer (Step-2 question: stall ON a gate, or never advance?)

| Item | Value |
|---|---|
| Wake source for :428 | 3E4648 `SignalSema(26)` @ `0x3e48b0` (thread 1, between :426 and :427; silent syscall; order :427→:428; alternatives excluded: `0x3e3d78` prime never fired — no `ret=0x3e3fb0` print + single-exit; pump `0x3E5760` signals a non-26 sema — steady-state pumps never wake the worker) |
| Gates passed (values) | G0 wake → G1 `GetError`=0 (fallthrough) → G2 `0xA`&8≠0 (fallthrough) → G3 bit1 set (fallthrough, store :428) → G5 `3→2`>0 (:429) → ISSUE |
| Last observed progress | :433 `0x519c40`=`0x2` @ `0x3e3ba0` thread 2 (issuer R2 success); then silent epilogue → `0x3e3c68` → G0 re-park |
| Re-park vs signal order | Worker re-parks (WaitSema @ `0x3e3c18`) BEFORE callback signals: :433 (thread 2, still running issuer) → :434 callback START (scheduler dispatches it only after thread 2 blocks); thread 2 `scheduled=0` blocks 1–16, `pc=0x423de8` all 17 blocks |
| Site #9 (`0x3e3d64`) | Never reached: zero watch lines after :433; G6 (`*(0x519C64)`=`0`→W1) unreached; NOT an on-gate stall (no gate held the worker — it cycled to G0 and the completion wake never landed) |
| Site #7 (`0x3e3450`) | Never armed this boot: case-2 took path A topbyte==1 (`ra`=`0x3e33a0` on :419–:426 ⟹ via `0x3e3398`); `*(0x519C20)` zero writes; `0x450C40`/`0x450C4C` init-only |
| Shape | Signal-during-park (L1/W2): completion signal arrived while worker parked and did not wake it. Delivery mechanism = out-of-scope sema-26 item (not chased); ORDER + last-progress point = this receipt |

### c. Ladder delta vs boot-p1q-1 (1,234 lines, 130,595 B)

Boot-p1r-1: 1,253 lines, 132,454 B, 17 blocks.

| Rung | boot-p1q-1 | boot-p1r-1 | Delta |
|---|---|---|---|
| Thread-1 pc | `0x3e5980` ×16, `0x0` ×1 (blk16 teardown) | `0x3e5980` ×17 (all blocks) | No teardown line this boot |
| Thread-1 sch | 84/82/81/80/81/81/81/80/78/68/81/82/81/79/78/68/81 | 82/82/82/81/80/78/68/82/81/82/79/79/68/81/81/81/80 | Same regime (~68–84) |
| Thread-2 (worker) | parked sema 26 @ `0x423de8`, sch 2 then 0 ×16 | Same bytes (`:490` sch 2, `:536`–`:1232` sch 0) | None |
| Threads 4/5 | sema-parked 29/30 @ `0x423de8` | Same ids/pcs/entries (4: sch 58 b0; 5: sch 1 b0) | Counts regime only |
| Missing target | 0 | 0 | None |
| Stub distinct b0 / b1–16 | 486 / 18 | 486 / 18; b0 30/30 targets identical (sort-compared) | None |
| Syscall distinct b0 / b1+ | 27 / 3; 20 printed ids | 27 / 3; same 20 ids (sort-compared, identical) | None |
| Syscall sema counts | b0: Wait 159 / Sig 77 / iSig 79; steady Wait==iSig/block, Sig absent | b0: Wait 157 / Sig 77 / iSig 77; steady Wait==iSig/block (82/82,81/81,…,68/68), Sig absent | b0 counts −2/0/−2; same lockstep shape |
| CD callback | :414–:415 queued+start | :432 + :434 (same func/cb; :433 issuer store between) | Line shift + interleave |
| CD read | :412 `lbn=0x5f1a3 ret=0x3e3b8c` + payload | :430 same lbn/ret/buf/payload bytes | Line number only |
| Probe | 1 (:416, p1o bytes) | 1 (:435, p1o bytes) | Line number only |
| VIF MPG/MSCAL | 0 | 0 | None |
| GIF/GS | 2 / 66 / 122 / 33 / 8 | 2 / 66 / 122 / 33 / 8 | None |
| `run:tick` | 7 | 7 | None |
| Presented frame | None | None (sole `frame` hit = raylib TIMER line :46) | None |
| Crash | 0 | 0 | None |
| Dormant / start-thread | 40 / 4 | 40 / 4 | None |
| SIF module lines | 6 (`IRX` grep) | 6 | None |
| `firstRa=0x3dd290` / `0x3dd280` | 17 / 17 | 17 / 17 | None |
| `target=0x3de420` / `0x3ddfa8` | 0 / 0 | 0 / 0 | None (direct JALs) |

## P19-3. Binaries and commits

| Binary / ref | sha256 / sha | Sources / state |
|---|---|---|
| `/tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner` (boot-p1r-1) | `7a7d4b645094d3ad82746a7d420b223422bf6444e5d06f6e56998e9057f5b4cd` | `e73e36a` tree, no rebuild (fresh; §P19-0 pre-boot check) |
| `ps2x_tests` | Not re-run (no source change; P15-1c 424/425 stands for this tree) | Same tree `e73e36a` |
| `PS2Recomp` branch `ssx3` HEAD | `e73e36a` | No fork commit (env-only boot; worktree sole `M` = pre-existing generated `runner/register_functions.cpp`, never added) |
| Fork push | `git push fork ssx3` from fork clone only | Up-to-date check (expect nothing to push) |
| This report | `[P1r]` commit (two trailers; local only) | Sole ssx3-repo change; no `runner/`, log, or `._*` added |

## P19-4. Exact commands

From `$W/PS2Recomp` (fork) unless noted; `$W=/Volumes/Extreme SSD/ps2recomp-spike`,
`$O=$W/P1/output`, `$R=$W/PS2Recomp`, `$LOG=$W/P1/run/boot-p1r-1.log`:

```
# Step 1 (lease-free static; M10 holds observed at start, flapping mid-step)
re-read REPORT Part 18 + Part 17 P17-1 (paged reads)
read $O/sub_003E3B00 (worker both halves) + sub_003E33B0/3350 (site 7) + sub_003E39A8 (callback)
read $O/sub_00401DF8 (sceCdRead) / 4013E8 (sceCdSync) / 402300 (sceCdGetError) / 423DD0 (iSignalSema) / 423DE0 (WaitSema) / 423DC0/3BA0/3BC0/3DA0/3B20 (syscall id decodes)
read CD.cpp (sceCdRead/sync/getError/callback/InitEeCB, g_lastCdError init 0) + Dispatcher.cpp (0x20/22/40/42/-43/44/FC) + Sync.cpp/State.h (ee_sema_t layout)
pointer search: JAL-word absence (0xc0f8cec/ef8/eb6) + lui/addiu pairs -> 0x3e3020 (poll reg), 0x3e3fb4/0x3e4430 (cb reg), 0x3e43c4 block (thread+cb+poll reg)
read $O/sub_003E57F8 (table insert) / 3E58C8 (unregister) / 3E5928 (park sweep + jalr 0x3e59b8) / 3E5760 (unlock helper + table clear) / 3E3D78 + 3E4040 (init chain) / 3E4648 (fills) / 3DDFA8 case-2 prelude
ELF batch: python3 struct check 77 words (0 mismatches); hex machine-checks (each pasted §P19-1e)
P6 grep (ssx3-decomp-names.csv, 802 lines, no rows); old-log harvest (thread-2 rows, :412-:416, syscall hist)
# Step 2 (lease protocol)
cat /tmp/ssx3-host-lease (M10 16:11:44Z; absent 16:16:53Z; M10 16:20:22Z; absent 16:23:22Z); pgrep (exit 1)
shasum ps2EntryRunner (7a7d4b64 fresh); git log/status (e73e36a); ls ISO + ELF
printf 'P1r\n' > /tmp/ssx3-host-lease (16:23:32Z, absent verified twice)
(write /tmp/p1r-boot1.py: p1q env, WATCH 11 addrs, probe on; diff vs p1q-boot1.py = docstring + LOG + WATCH only)
python3 /tmp/p1r-boot1.py (CWD $W/P1/run, 90 s, SIGTERM rc=-15, 132454 B)
log greps: watch 57 (zero-init doubles + memset + lbn reg + init + fills + worker :428/:429/:433, none after);
  cd reads (20 early ret=0x3e3694 + :430 ret=0x3e3b8c); InitEeCB 1 (:178 ret=0x3e442c, no ret=0x3e3fb0);
  callback pair (:432/:434 with :433 between); probe 1 (:435); thread-2 17 rows (sch 2 then 0)
ladder sweeps: thread pcs/sch per block; stub 486/18 + b0 30-target comm; syscall 27/3 + 20-id
  sort-compare (identical) + sema counts per block; gs:/run:tick/frame/crash/dormant/start-thread/missing-target;
  firstRa 17/17; SIF 6; thread-4 sch noted (58/82, parked pc, not chased)
rm -f /tmp/ssx3-host-lease (16:27:31Z); ls (absent); pgrep (none)
# Step 3
(edit_file append Part 19 in 3 chunks; commit below)
git -C /Users/bradrichardson/dev/ssx3 add -f local/research/P1/REPORT.md
git -C /Users/bradrichardson/dev/ssx3 commit -m "[P1r] ..." (two trailers; NO push there)
git -C $R push fork ssx3 (up-to-date check; the only push allowed)
```

Env delta vs boot-p1q-1: WATCH 10 addrs → 11 addrs (Step-1 gate set) only.
Source delta: none.

## P19-5. What I could not do

- Run the reserve 2nd boot (not needed): still-unwatched words it could close directly —
  site-#10 W1 observability (`0x5e00b8` flag + `0x519AD4` current: did 3E4648's `0x3e4888`
  run? P18's stuck-current receipt rests on the p1q boot), `0x519C30` (arm +0x10 datum,
  implied by contiguous block), `0x519C58`–`0x5F` (in no 8B window), `0x51ED98` poll-table
  slots (index unknown statically).
- Observe sema-26 count transitions (host-side `EeScheduler` state, not RDRAM — unwarchable);
  the W1/W2 signal ORDER is the receipt, the delivery mechanism stays out of scope (per brief).
- Name the pump `0x3E5760`'s signaled sema id (`*(mutex+0xC)` value unobserved; excluded as
  the :428 waker by steady-state non-wake, §P19-2b).
- Read `*(0x450C60)` (init branch value; inferred ≠0 from the taken `$a1`≠0 path, :181–:182).
- Determine whether `0x3e3d78`'s head ran without completing (completed-no is proven: no
  `ret=0x3e3fb0` print + single-exit + no thread inside; a partial run leaving no watched
  trace cannot be excluded).
- Explain thread 4's `scheduled=58/82` with parked pc (observed, not chased — different sema).
- No runtime fix (per the brief): worker-path + registration + receipts only. The sema-26
  non-delivery mechanism remains out of scope, untouched.
- One boot used (of the brief's max two): no A/B on any rung.

---

## Part 20 (P1s): sema-26 signal path intact; callback body never runs (0x3e3ad8 has no table entry, invocation pc zeroed silently); pump semas are 4 + 5

Brief `local/muse/prompts/P1s.md`. Static signal/wait paths + 1 `Diag:` commit +
1 dynamic receipt boot; no fix. Tables, no verdicts. Stale-reading guard: Part 19
(P19-1a callback→wake link, P19-2b :433→:434 order, P19-5 unwarchable-count +
pump-sema residues) + Part 17 §P17-1 (sema-26 history) re-read before acting.
`W=/Volumes/Extreme SSD/ps2recomp-spike`, `R=$W/PS2Recomp` (fork, branch `ssx3`),
`O=$W/P1/output`, `LOG=$W/P1/run/boot-p1s-1.log`. File:line refs below are
`ps2xRuntime/src/lib/` unless noted.

## P20-0. Lease record

| Event | Value |
|---|---|
| Lease at session start | `M11` (observed 16:50:31Z) |
| Polls (5 min, logged) | 16:50:35Z `M11`; 16:55:56Z `M11` (absent 16:55:44Z, re-claimed by M11 before claim); 17:00:53Z `M11`; 17:05:53Z `M11`; 17:10:51Z `M11`; 17:15:41Z absent |
| Waits log | `$W/P1/run/p1s-waits.log` (7 lines: 5 holds + claim + release) |
| pgrep note (16:55:56Z) | `pgrep -f "[p]s2EntryRunner"` matched 11 clang++ PIDs (I2 unity-build compile lines mentioning ps2EntryRunner paths); `pgrep -x ps2EntryRunner` exit 1 (no runner process). Recorded, nothing touched |
| Pre-claim checks (17:15:4xZ) | `pgrep -x ps2EntryRunner` exit 1; lease absent (verified twice); binary `6ac8e6c1` (P1s Diag build); fork HEAD `be01146`; ISO 3005415424 B + ELF 3890784 B present |
| Claim | `printf 'P1s\n' > /tmp/ssx3-host-lease` 17:15:46Z, immediately before boot-p1s-1 |
| Boot 1 | 90 s foreground, SIGTERM rc=-15, returned 17:17:21Z |
| Release | `rm -f /tmp/ssx3-host-lease` 17:19:15Z; verified absent; `pgrep -x` exit 1 |
| Second boot | None (Step-2 question closed by boot 1; reserve unused) |
| `adb` | Not used |

## P20-1. Paths + differences (static, no lease, no boot)

Conventions: `Sync.cpp` = `Kernel/Syscalls/Sync.cpp`; `Sched` =
`Kernel/EeScheduler.cpp` (+ `ps2xRuntime/include/runtime/ee_scheduler.h`);
`Dispatch` = `Kernel/Syscalls/Dispatcher.cpp`. Guest trampolines `$O/sub_00423D*.cpp`.
All words ELF-verified §P20-1e; all hand hex machine-checked §P20-1e.

### a. Wait path (WaitSema `0x423DE0` → scheduler)

| Step | Location | Value |
|---|---|---|
| Guest call | Worker `0x3e3c18` `jal 0x423DE0` | `$a0` = `*(0x519C4C)` = 26 |
| Trampoline | `$O/sub_00423DE0` | `$v1`=`0x44`, `syscall 0` @ `0x423de4`, post-syscall pc `0x423de8` (the parked pc in every thread-2 row) |
| Dispatch | `Dispatch:268-270` | `case 0x44: WaitSema(...)` |
| Syscall layer | `Sync.cpp:109-112` | `scheduler(...).waitSemaphore(a0)`; no return-value write here (set inside scheduler or on wake) |
| Fast path | `Sched:1190-1198` | `count!=0` → `--count`, `setReturnS32(activeContext,id)`, NO block |
| Unknown id | `Sched:1183-1189` | `setReturnS32(KE_UNKNOWN_SEMID=-408)`, NO block |
| Park | `Sched:1199-1202` | `count==0` → `waiters.push_back(self->id)` then `blockCurrent(Semaphore,id)` |
| Block | `Sched:1965-1974` | `wait`=payload, status=`Waiting` (`suspendCount==0`) else `WaitingSuspended`, `m_currentThreadId=0`, `publishSnapshot`, `throw EeDispatcherTransfer` |
| Wake requires | `Sched:1143-1152` | `signalSemaphore(id)`: `waiters` nonempty → pop FRONT, `makeReady(waiter,id,…)`; count untouched |
| Ready | `Sched:1976-1989` | `wait={}`, `setReturnS32(activeContext,result)`; `suspendCount!=0` → `Suspended` (NOT runnable); else `enqueueReady` + `requestPreemptionIfHigher` |
| Selection | `Sched:1896-1912` | `selectReady` scans `m_readyQueues[0..127]` low→high: lower number = higher priority |
| Preemption | `Sched:1991-2003` | Only if woken prio STRICTLY lower number than running; worker 12 vs thread-1/invocation-thread 0 → never preempts |
| Timeslice | `Sched:639-647` + `2386-2397` | Preempts only for ready-at-or-above (number ≤) running prio; worker 12 never qualifies against prio 0 |

### b. Signal paths: `SignalSema` (`0x423DC0`) vs `iSignalSema` (`0x423DD0`)

Guest + dispatch rows:

| Item | Thread path (`SignalSema`) | Callback path (`iSignalSema`) |
|---|---|---|
| Guest trampoline | `$v1`=`0x42` @ `0x423dc0`, post pc `0x423dc8` | `$v1`=`-0x43` @ `0x423dd0`, post pc `0x423dd8` |
| Dispatch | `Dispatch:262-264` `case 0x42` | `Dispatch:265-267` `case -0x43` |
| Syscall layer | `Sync.cpp:99-102` → `signalSemaphoreImpl(…,false)` | `Sync.cpp:104-107` → `signalSemaphoreImpl(…,true)` |
| Shared impl | `Sync.cpp:33-42`: `ee.signalSemaphore(a0,interruptSafe)`, `setReturnS32`, `ee.transferIfRequested(interruptSafe)` — same code | Same code |

`signalSemaphore` (`Sched:1135-1160`) — NO branch on `interruptSafe` in the wake decision:

| Branch | Code | Both paths |
|---|---|---|
| Unknown id | `:1138-1142` → `KE_UNKNOWN_SEMID` | Identical |
| Waiters nonempty | `:1143-1152` pop front + `makeReady(waiter,id,interruptSafe)` | Identical (no callback guard, no deferred queue, no dropped-if-not-waiting branch) |
| `count==max` | `:1153-1156` → `KE_SEMA_OVF` | Identical |
| Else | `:1157-1159` `++count` | Identical |

Downstream `interruptSafe` differences (post-wake only):

| Item | `false` (thread) | `true` (callback/interrupt) |
|---|---|---|
| `requestPreemptionIfHigher` (`Sched:1991-2003`) | `m_rescheduleRequested=true` only (when woken prio higher) | Same + `m_checkpointPending=true` |
| `transferIfRequested` (`Sched:1070-1088`) | Throws (immediate preempt) when reschedule requested and not in interrupt | Returns (preemption deferred to `processPendingEvents`→`applyPendingPreemption` after guest fn returns) |
| When woken prio LOWER than running (this boot: 12 vs 0) | `requestPreemptionIfHigher` no-ops; `transferIfRequested` no-ops (`!m_rescheduleRequested`) | Same no-ops — ZERO behavioral difference |

Other `signalSemaphore` callers (census): `RPC.cpp:142-149` `signalRpcCompletionSema`
(`interruptSafe=true`, id = guest SIF-RPC `endParameter`), called at `RPC.cpp:543`
(nowait completion), `:547` (completion), `:657` (missing-callback fallback). No
other callers tree-wide (grep over `ps2xRuntime/src` excl. `EeScheduler.cpp`,
`ee_scheduler.h`, `Sync.cpp`).

Callback invocation context (for §P20-2):

| Item | Location | Value |
|---|---|---|
| Queue | `Stubs/CD.cpp:66-88` | `kind=Interrupt`, `tag=0x43444342…\|func`, `pc=g_cdCallbackFn`, `sp=g_cdCallbackStackTop`, `ra=0` |
| Attach (running) | `Sched:489-504` | Pushed onto RUNNING thread's `invocations`; `[cd:callback] start` printed at `:493-497` (attach ≠ execution) |
| Attach (idle) | `Sched:388-410` | Negative-id invocation thread (prio 0); `start` printed at `:396-401` |
| `m_insideInterrupt` | `Sched:552` | Set iff back invocation `kind==Interrupt` (CD callbacks qualify) |
| No-function + invocation | `Sched:506-512` | `!hasFunction(pc)` + nonempty invocations → `context.pc=0` SILENTLY (no `reportMissingFunction`; that call is only in the empty-invocations else-branch `:513-540`) |
| Pop | `Sched:448-465` | `pc==0` + nonempty → pop, run `onComplete` (CD callbacks register none), thread resumes own context |
| Table rule | `ps2_runtime.cpp:1081-1096,1289-1293` | Per-word slot `(addr-base)>>2`; populated at registered entries only; `lookupFunction` errors "No EXACT recompiled function" |
| `0x3e3ad8` entry? | `$W/P1/ssx3-functions.csv` | NO row starts at `0x3e3ad8` (mid-`sub_003E39A8`, `0x3e39a8`–`0x3e3b00`) → `hasFunction(0x3e3ad8)` is false |

Callback body (`$O/sub_003E39A8`, `0x3e3ad8`–`0x3e3af8`): straight-line —
`lui $v0,0x52`; `lw $a0,-0x63B4($v0)` (`*(0x519C4C)`); `jal 0x423DD0` @ `0x3e3ae8`
(ra `0x3e3af0`); `jr $ra`. No branch: IF it ran, the signal would always fire.

### c. Pump `0x3E5760` (P6 `MUTEX_unlock`) + lock `0x3E5700` (P6 `MUTEX_lock`)

| Item | Value |
|---|---|
| Lock (`$O/sub_003E5700`) | `jal WaitSema(0x423DE0)` @ `0x3e5730` (delay `lw $a0,0xC($s0)` @ `0x3e5734`; ra `0x3e5738`); ELF `0xc108f78`/`0x8e04000c` ✓ |
| Unlock gates | `GetThreadId` (syscall `0x2F`, `Dispatch:211-214`) @ `0x3e576c`; owner check `0x3e5778`; recursion `0x3e5780`–`0x3e5788`; clear `0x3e5790` |
| Unlock-i | `jal iSignalSema` @ `0x3e57a4` (delay `lw $a0,0xC($s0)` @ `0x3e57a8`; ra `0x3e57ac`) iff `*(0x450DE4)!=0` (read @ `0x3e5798`); ELF `0xc108f74`/`0x8e04000c`/`0x8c430de4` ✓ |
| Unlock-thread | `jal SignalSema` @ `0x3e57b4` (delay @ `0x3e57b8`; ra `0x3e57bc`); ELF `0xc108f70`/`0x8e04000c` ✓ |
| Selector `*(0x450DE4)` writer | `lui $s2,0x45` @ `0x3e4e04` (ELF `0x3c120045` ✓; no `$s2` write before the stores); `sw $s3,0xDE4($s2)` @ `0x3e4e58` delay-of-`jalr $v0` (ELF `0xae530de4` ✓), `$s3`=1 (`addiu` @ `0x3e4e1c`, ELF `0x24130001` ✓); `sw $zero,0xDE4($s2)` @ `0x3e4e5c` (ELF `0xae400de4` ✓) |
| Other absolute writers | NONE among all 419 files containing `lui *,0x45`: 7 also contain `3556` (`0xDE4`), all struct-relative (`$a0`/`$a2`/`$s1` bases; one `23556` false positive) except the `3E4AF0` hit above (full-file census, no `head` truncation) |
| Direct JAL sites (ELF word `0x0c0f95d8`, 50) | `0x19d098 0x19d950 0x2525d0 0x252628 0x2526f4 0x252928 0x252f14 0x255e98 0x255efc 0x2c299c 0x2c2bc0 0x2c2e0c 0x317e04 0x317e7c 0x317ec4 0x317efc 0x319a0c 0x319c3c 0x319c64 0x319c94 0x319cec 0x3dd120 0x3de064 0x3de0ac 0x3de754 0x3de7e4 0x3de860 0x3de8f4 0x3deeb8 0x3def18 0x3df064 0x3df944 0x3df9b8 0x3dfa34 0x3dfb5c 0x3dfc80 0x3dfd38 0x3dfdb0 0x3dff70 0x3dfff8 0x3e022c 0x3e02e8 0x3e0490 0x3e0d28 0x3e0e4c 0x3e0f74 0x3e103c 0x3e1354 0x3e147c 0x3e1684` |
| Static id? | Unresolvable statically (50 sites × own mutex); folded into Step 2 (§P20-2c: ids 4 + 5) |
| Steady iSig source (old-log harvest) | `boot-p1r-1.log`: `id=0xffffffbd` every block, `first=last=0x423dd8` (trampoline pc; no ra recorded) — source unidentified statically; §P20-2c names it (`0x31abf8`) |

### d. P6 names

| Addr | P6 row (`local/research/P6/ssx3-decomp-names.csv`, 802 lines) |
|---|---|
| `0x3e5700` | `MUTEX_lock` (line 749) |
| `0x3e5760` | `MUTEX_unlock` (line 750) |
| `0x31aaf0` / `0x3e39a8` / `0x3e4648` / `0x3e4e04` region | No rows |

### e. ELF verification words + machine-check paste block

Batch word check (20 addrs; every word matched its disassembly comment in `$O`;
ELF `$W/P1/SLUS_207.72`, mapping file-off = va−`0x100000`+`0x1000`):

```
0x3e4e04 0x3c120045 / 0x3e4e1c 0x24130001 / 0x3e4e54 0x40f809 / 0x3e4e58 0xae530de4
0x3e4e5c 0xae400de4 / 0x3e5798 0x8c430de4 / 0x3e57a4 0xc108f74 / 0x3e57a8 0x8e04000c
0x3e57b4 0xc108f70 / 0x3e57b8 0x8e04000c / 0x423c90 0x2403002f / 0x3e5730 0xc108f78
0x3e5734 0x8e04000c / 0x31abf0 0xc108f74 / 0x31abf4 0x8c644034 / 0x31ac28 0xc108f78
0x31ac2c 0x8e044034
```

Machine-check paste block (every hand computation in §P20-1; command then `→` output):

```
python3 -c "print(hex(0x0C000000|((0x3E5760>>2)&0x3FFFFFF)), hex(0x0C000000|((0x423DA0>>2)&0x3FFFFFF)))"
→ 0xc0f95d8 0xc108f68
python3 -c "jal decode: ((pc+4)&0xF0000000)|((w&0x3FFFFFF)<<2)"
→ 0x31abf0→0x423dd0 0x31ac28→0x423de0 0x3e5730→0x423de0
  0x3e57a4→0x423dd0 0x3e57b4→0x423dc0 0x3e576c→0x423c90
python3 -c "print(hex(0x450000+0xDE4), hex(0x31ac28+8), hex(0x3e5730+8), hex(0x31abf0+8))"
→ 0x450de4 0x31ac30 0x3e5738 0x31abf8
```

## P20-2. Dynamic answer (boot-p1s-1, 1 boot)

`$W/P1/run/boot-p1s-1.log`, 4,119 lines, 566,220 B, 17 blocks, CWD `$W/P1/run`,
env = p1r env with WATCH = 2 addrs (`0x519C40`, `0x450DE4`) + `PS2X_DIAG_SEMA=1`
(new `Diag:` commit `be01146`), PROBE=1 kept on, foreground 90 s, SIGTERM rc=-15.
Binary `6ac8e6c1` (§P20-3). `PS2X_DIAG_SEMA` format: `op` signal|wait, `id`,
`count` before→after, `waiters` before→after, waker tid/`pc`/`ra`, `inInt`
(`m_insideInterrupt`), `iSafe` (`interruptSafe`), `invKind`/`invDepth`/`cbFunc`
(back-invocation kind/depth/tag), wake `target` + pre-wake `tStatus`/`tSusp`/
`tWaitReason`/`tWaitId`, `result`. Status ints: 0 Running, 1 Ready, 2 Waiting,
3 WaitingSuspended, 4 Suspended, 5 Dormant; waitReason 2 = Semaphore.

### a. sema-26: the complete signal/wake record (3 lines, whole boot)

| Line | Line content (abridged) |
|---|---|
| :205 | `op=wait id=26 count=0->0 parked=1 waker=2 pc=0x423de8 ra=0x3e3c20` (first park) |
| :574 | `op=signal id=26 count=0->0 waiters=1->0 waker=1 pc=0x423dc8 ra=0x3e48b8 inInt=0 iSafe=0 invKind=-1 invDepth=0 target=2 tStatus=2 tSusp=0 tWaitReason=2 tWaitId=26 result=26` (thread-1 first signal wakes thread 2) |
| :581 | `op=wait id=26 count=0->0 parked=1 waker=2 pc=0x423de8 ra=0x3e3c20` (re-park) |

Absence rows (counts over all 4,119 lines):

| Query | Count |
|---|---|
| `op=signal id=26` total | 1 (:574 only) |
| `ra=0x3e3af0` (callback's `jal iSignalSema` return) | 0 |
| `pc=0x3e3ad8` (callback body dispatched) | 0 |
| `op=signal` with `cbFunc=0x43444342…` (CD-callback-tagged invocation) | 0 |
| `missing-target` / `No exact recompiled function` | 0 |

Order around the callback (:572–:582):

| Line | Event |
|---|---|
| :572–:573 | `0x519c40` = `0x0` → `0xA` (thread 1, `0x3e4768`/`0x3e48b4`) |
| :574 | signal id=26 → thread 2 (above) |
| :575 | `0x519c40` = `0x2` (thread 2, `0x3e3c4c` — worker wake) |
| :576–:577 | `sceCdRead lbn=0x5f1a3 sectors=1 buf=0x9d0800 ret=0x3e3b8c` + `BIGF` payload (`42494746147c1a00`) |
| :578 | `[cd:callback] queued func=1 cb=0x3e3ad8` |
| :579 | `0x519c40` = `0x2` (thread 2, `0x3e3ba0` — issuer success) |
| :580 | `[cd:callback] start func=1 cb=0x3e3ad8` (attach; thread 2 still running) |
| :581 | worker re-park (`op=wait id=26`, above) |
| :582 | driver probe (p1o bytes) |

Thread-2 rows: parked sema 26 @ `0x423de8` all 17 blocks (`:490`-area sch 2, then
sch 0 ×16 — same bytes as p1r). No signal ever names `target=2` again after :574.

### b. The break, as named by the receipts (§P20-1b + §P20-2a)

| # | Receipt | Value |
|---|---|---|
| 1 | Wake path works | :574 signal (waiters 1→0, `target=2`, `tStatus=2`, `tSusp=0`) + 1,360 id-29 wake pairs (§P20-2c) + 74 pump count-pairs: `signalSemaphore` wakes whenever it is CALLED with a waiter parked |
| 2 | Callback attached, never dispatched | :580 `start` (= attach, `Sched:493-497`) with thread 2 running → invocation pushed onto thread 2; next dispatch: `hasFunction(0x3e3ad8)` false (no table entry, §P20-1b) → `Sched:506-512` zeroes invocation pc SILENTLY → pop (`:448-465`) → thread 2 resumes own context → :581 re-park |
| 3 | Silence is total | 0 `ra=0x3e3af0` signals, 0 `pc=0x3e3ad8` dispatches, 0 missing-target lines, 0 `No exact` errors — the invocation left no trace between :580 and :581 except thread 2 continuing |
| 4 | ORDER refinement vs P19-2b | P19 inferred re-park-before-callback-start from `:433`→`:434` adjacency; the wait line (:581) now shows thread 2's re-park call arrives AFTER callback attach (:580) — the attach-while-running + silent-drop sequence above |

### c. Pump sema ids + steady-state signal census (P19-5 residue closed)

All `op=signal` lines grouped by (`ra`, `id`) — full census (1,457 signal + 1,460 wait = 2,917 `[diag:sema]` lines):

| Count | `ra` (site) | `id` | Site decodes to |
|---|---|---|---|
| 1360 | `0x31abf8` | 29 | `jal iSignalSema` @ `0x31abf0` in `sub_0031AAF0` (delay `lw $a0,0x4034($v1)`); all `waker=1 inInt=1 iSafe=1 invKind=0 invDepth=1 cbFunc=0` (Interrupt-kind invocation, tag 0 — NOT a CD callback) |
| 66 | `0x3e57bc` | 4 | Pump thread-site (`MUTEX_unlock` @ `0x3e57b4`); all `waker=1 inInt=0 iSafe=0` |
| 8 | `0x3e57bc` | 5 | Same site, second mutex; all `waker=1 inInt=0 iSafe=0` |
| 20 | `0x3e3598` | 6–25 (1 each) | One-shot drainer (early boot) |
| 2 | `0x418d3c` | 1 | Count-path pair (`0->1`, no waiters; waits at `ra=0x418ce0` consume `1->0`) |
| 1 | `0x3e48b8` | 26 | First signal (:574) |
| 0 | `0x3e57ac` | — | Pump i-site NEVER taken this boot |
| 0 | `0x3e3af0` | — | Callback site NEVER executed (§P20-2a) |

Matching waits: id 29: 1,361 parks (`ra=0x31ac30` ← `jal WaitSema` @ `0x31ac28`,
delay `lw $a0,0x4034($s0)`; thread 4, `entry=0x31ac08 prio=99`); id 4: 66 ×
`count=1->0 parked=0` (`ra=0x3e5738`, `MUTEX_lock`, waker=1); id 5: 8 × same.
Signal `result` census: every signal returned its id (no `-408`, no `-420`).

`*(0x450DE4)` (pump selector): 0 watch writes in 90 s (value never changed from
zero-init; consistent with 0 pump-i lines). `0x519C40` watch: 7 lines (:49
zero-init, :77 memset, :201 neighbor `0x519c44`, :572/:573/:575/:579 §P20-2a).

### d. Ladder delta vs boot-p1r-1 (1,253 lines, 132,454 B)

Boot-p1s-1: 4,119 lines, 566,220 B, 17 blocks (+2,966 lines = 2,917 `[diag:sema]`
+ 49-line env/watch/probe shift).

| Rung | boot-p1r-1 | boot-p1s-1 | Delta |
|---|---|---|---|
| Thread-1 pc | `0x3e5980` ×17 | `0x3e5980` ×17 | None |
| Thread-1 sch | 82/82/82/81/80/78/68/82/81/82/79/79/68/81/81/81/80 | 84/81/81/80/70/81/81/81/78/77/69/81/81/81/78/78/70 | Same regime (~68–84) |
| Thread-2 | parked 26 @ `0x423de8`, sch 2 then 0 ×16 | Same bytes | None |
| Thread-4 | sema-parked 29 @ `0x423de8` (sch 58 b0) | Same ids/pcs/entries (`entry=0x31ac08 prio=99`; sch 60 b0) | b0 count regime only |
| Thread-5 | sema-parked 30 @ `0x423de8` (sch 1 b0) | Same (`entry=0x382740 prio=5`; sch 1 b0) | None |
| Missing target | 0 | 0 | None |
| Stub distinct b0 / b1–16 | 486 / 18 | 486 / 18; b0 30/30 targets identical (sort-compared) | None |
| Syscall distinct b0 / b1+ | 27 / 3; 20 printed ids | 27 / 3; same 20 ids (sort-compared, identical) | None |
| CD callback | :432 + :434 (same func/cb) | :578 + :580 (same func/cb) | Line shift only |
| CD read | :430 same lbn/ret/buf/payload | :576 same lbn/ret/buf/payload bytes | Line number only |
| Probe | 1 (:435, p1o bytes) | 1 (:582, p1o bytes) | Line number only |
| VIF MPG/MSCAL | 0 | 0 | None |
| GIF/GS | gif 2 / kick 66 / reg 122 / prim 33 / copy-reg 8 / texa 1 | 2 / 66 / 122 / 33 / 8 / 1 | None |
| `run:tick` | 7 | 6 | −1 (timing regime) |
| Presented frame | None | None (sole `frame` hit = raylib TIMER line :46) | None |
| Crash | 0 | 0 | None |
| Dormant / start-thread | 40 / 4 | 40 / 4 | None |
| SIF module lines | 6 | 6 | None |
| `firstRa=0x3dd290` / `0x3dd280` | 17 / 17 | 17 / 17 | None |
| `target=0x3de420` / `0x3ddfa8` | 0 / 0 | 0 / 0 | None |

## P20-3. Binaries and commits

| Binary / ref | sha256 / sha | Sources / state |
|---|---|---|
| `/tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner` (boot-p1s-1) | `6ac8e6c13552a4bfd11bd4b404634c92ddbc45fe3077be0cf45a66f3aae9cba1` | `be01146` tree (P1s `Diag:` + I2 `66d992c`/`d62c4b5` parents; rebuilt `-j4`, exit 0) |
| `ps2x_tests` (CWD `$R`, rebuilt) | Total 425, Passed 424, Failed 1 (`GS alpha-test AFAIL independently masks framebuffer and depth`) | P15-1c 424/425 baseline re-confirmed; failure pre-existing, unrelated, not fixed |
| `PS2Recomp` branch `ssx3` HEAD | `be01146` (`Diag: P1s sema signal/wait trace gated on PS2X_DIAG_SEMA (P20-2)`, 1 file, +97, two trailers) | Sole P1s fork commit; worktree sole `M` = pre-existing generated `runner/register_functions.cpp`, never added |
| I2 commits in history | `66d992c` (I2-G5), `d62c4b5` (I2-G6) | Other agent's; present at session start, untouched |
| Fork push | `git push fork ssx3` from fork clone only (pull-`--rebase` + retry-once rule armed; §P20-4) | The only push allowed |
| This report | `[P1s]` commit (two trailers; local only) | Sole ssx3-repo change; no `runner/`, log, or `._*` added |

`Diag:` diff shape (`Sched` only): `diagSemaEnabled()` (`PS2X_DIAG_SEMA`
non-empty; cached static; default off) + `[diag:sema]` emit on all 4
`signalSemaphore` return paths (waker tid/pc/ra, `inInt`, `iSafe`,
`invKind`/`invDepth`/`cbFunc`, `count`/`waiters` before→after, pre-wake
`tStatus`/`tSusp`/`tWaitReason`/`tWaitId`, `result`) + all 3 `waitSemaphore`
paths (`parked`, same context fields). No behavior change when unset (one cached
bool check per call).

## P20-4. Exact commands

From `$R` (fork) unless noted; `$W=/Volumes/Extreme SSD/ps2recomp-spike`,
`$O=$W/P1/output`, `$LOG=$W/P1/run/boot-p1s-1.log`:

```
# Step 1 (lease-free static)
re-read REPORT Part 19 + Part 17 P17-1 (paged reads)
read Sync.cpp (all) + Sync.h + Dispatcher.cpp (sema cases, diag head) + ee_scheduler.h (all)
read EeScheduler.cpp: wait/signal (1060-1210), invocations (1370-1450), run loop
  (280-585), block/makeReady/preempt (1851-2024), snapshot/helpers (1744-1810, 2254-2260, 2386-2412)
read Stubs/CD.cpp queueCdCallback (30-88); RPC.cpp signalRpcCompletionSema (142-149, 520-560, 630-660)
read $O/sub_00423DC0/3DD0/3DE0/3C90 (trampolines) + sub_003E5760 (pump) + sub_003E39A8:370-400 (callback)
  + sub_003E5700:85-115 (lock) + sub_0031AAF0 lockstep windows + sub_003E5928 jal census
ELF JAL-word sweeps: 0x0c0f95d8 (pump, 50 sites) + 0x0c108f68 (CreateSema word, computed only)
lui-0x45 census: 419 files; intersect 3556 -> 8 files; provenance check ($s2 @ 0x3e4e04 live to stores)
ELF batch: python3 struct check 20 words (0 mismatches); hex machine-checks (each pasted §P20-1e)
P6 grep (ssx3-decomp-names.csv, 802 lines: MUTEX_lock/unlock rows 749-750)
old-log harvest: boot-p1r-1.log iSig first/last (0x423dd8, all blocks)
# Step 2 (Diag commit + build + tests, no lease needed)
(edit_file: diagSemaEnabled + signal/wait emits, EeScheduler.cpp only)
find ps2xRuntime/src/lib/Kernel -name '._*' -delete
cmake --build /tmp/p1-link/runtime --target ps2EntryRunner -j4 (exit 0)
/tmp/p1-link/runtime/ps2xTest/ps2x_tests rebuilt; run CWD $R (425/424/1, GS AFAIL; re-run for name)
shasum -a 256 ps2EntryRunner (6ac8e6c1)
git add ps2xRuntime/src/lib/Kernel/EeScheduler.cpp (NAMED file only; I2 files + runner/ left alone)
git commit -m "Diag: ..." (two trailers; NO push yet) -> be01146
(write /tmp/p1s-boot1.py: p1r env + PS2X_DIAG_SEMA=1, WATCH 2 addrs; diff vs p1r-boot1.py = docstring + LOG + SEMA + WATCH only)
# Step 2 (lease protocol + boot 1)
cat /tmp/ssx3-host-lease (M11 16:50:31Z ... absent 17:15:41Z; 5-min polls, each >> p1s-waits.log)
pgrep -x ps2EntryRunner (exit 1); shasum (6ac8e6c1 fresh); git log/status (be01146); ls ISO + ELF
printf 'P1s\n' > /tmp/ssx3-host-lease (17:15:46Z, absent verified twice)
python3 /tmp/p1s-boot1.py (CWD $W/P1/run, 90 s, SIGTERM rc=-15, 566220 B; returned 17:17:21Z)
rm -f /tmp/ssx3-host-lease (17:19:15Z); ls (absent); pgrep -x (exit 1)
# Step 2 (log analysis, lease-free)
sema census: 2917 lines (1457 signal + 1460 wait); id-26 3-line record; ra=0x3e3af0 0; pc=0x3e3ad8 0
signal group-by (ra,id): 1360x29 / 66x4 / 8x5 / 20x(6-25) / 2x1 / 1x26; pump-i 0; result census (all = id)
watch: 0x450DE4 0 writes; 0x519C40 7 lines; callback pair :578/:580; probe :582
ladder sweeps: thread pcs/sch per block; stub 486/18 + b0 30-target comm (identical);
  syscall 27/3 + 20-id sort-compare (identical); gs:/run:tick/frame/crash/dormant/start-thread/
  missing-target/SIF/firstRa/target/VIF sweeps; gs:texa + run:tick cross-checks vs p1r
hasFunction/lookupFunction/slot reads (ps2_runtime.cpp:1075-1096, 1289-1347); csv entry check (no 0x3e3ad8 row)
# Step 3
(edit_file append Part 20 in 3 chunks + 2 count fixes; commit below)
git -C /Users/bradrichardson/dev/ssx3 add -f local/research/P1/REPORT.md
git -C /Users/bradrichardson/dev/ssx3 commit -m "[P1s] ..." (two trailers; NO push there)
git -C $R push fork ssx3 (the only push allowed; rebase-retry rule per brief on reject)
```

Env delta vs boot-p1r-1: WATCH 11 addrs → 2 addrs (`0x519C40`, `0x450DE4`) +
`PS2X_DIAG_SEMA=1` only. Source delta: `EeScheduler.cpp` (+97 diag lines).

## P20-5. What I could not do

- Attribute pump sema 4 vs 5 to specific mutex objects / JAL call sites: the
  `[diag:sema]` line records the pump return `ra` (`0x3e57bc`) but not `$a0`
  (mutex addr). Both mutexes live on thread 1 (all 148 pump lines `waker=1`).
  Closing this needs `$a0` in the line (another `Diag:` + boot; reserve boot
  unused, time remains in the 4 h box).
- Identify the Interrupt-kind tag-0 invoker behind the 1,360 id-29 signals
  (`sub_0031AAF0`, thread-4 waiter): `invKind=0 invDepth=1 cbFunc=0` fits the
  INTC/DMAC `dispatchIrq` path (tagless) but the handler pc was not logged.
  Not chased (different sema).
- Run the reserve 2nd boot (not needed): still-unwatched words it could close
  directly — `*(0x519C4C)` rewrite check (callback would have read it; body
  never ran, so moot), `0x51ED98` poll-table slots, `0x519C30`/`0x519C58`.
- Observe sema-26 count transitions other than logged: all transitions ARE now
  logged (host-side state made visible; P19-5 unwarchable residue closed for
  sema ops).
- No runtime fix (per the brief): paths + receipts only. The mid-label
  invocation-drop (`Sched:506-512`) is diagnosed, untouched.
- One boot used (of the brief's max two): no A/B on any rung.

---

## Part 21 (P1t): FIX — 0x3e3ad8 callback dispatched via host shim; worker passes G6, issues site #9, driver runs; thread 1 now spins on WaitSema(-1); entry-0 cycled 0→1→0

Brief `local/muse/prompts/P1t.md`. First behavior fix on the critical path:
1 `Fix:` commit (1 file, +46) + 2 boots. Tables, no verdicts. Stale-reading
guard: Part 20 (P20-1b invocation context + table rule, P20-2a–2b the
silent-drop receipts, P20-5 diagnosed-untouched note) re-read before acting.
`W=/Volumes/Extreme SSD/ps2recomp-spike`, `R=$W/PS2Recomp` (fork, branch
`ssx3`), `O=$W/P1/output`, `LOG1=$W/P1/run/boot-p1t-1.log`,
`LOG2=$W/P1/run/boot-p1t-2.log`. File:line refs below are
`ps2xRuntime/src/lib/` unless noted. All hand hex machine-checked §P21-1e.

## P21-0. Lease record

| Event | Value |
|---|---|
| Lease at session start | Absent (verified before Step 1; no claim — static work needs none) |
| M12 hold | Observed once mid-session (between build start and 18:54:25Z; exact minute not recorded); absent at 18:54:25Z and at claim-check 18:55:02Z — no poll loop ran |
| Waits log | `$W/P1/run/p1t-waits.log` (1 line: the claim record; zero wait polls) |
| Pre-claim checks (18:55:02Z) | `pgrep -x ps2EntryRunner` exit 1; lease absent (verified twice); binary `7c67f285` (P1t Fix build); fork HEAD `58c9144`; ISO 3005415424 B + ELF 3890784 B present |
| Claim | `printf 'P1t\n' > /tmp/ssx3-host-lease` 18:55:07Z, immediately before boot-p1t-1 |
| Boot 1 | 90 s foreground, SIGTERM rc=-15, LOG1 139,001,723 B (exceeds the 50 MB soft cap; §P21-5) |
| Boot 2 | 90 s foreground, SIGTERM rc=-15 (lease still `P1t`, verified 19:03:02Z pre-boot; `pgrep -x` exit 1) |
| Release | `rm -f /tmp/ssx3-host-lease` after Step 3 push; verified absent; `pgrep -x` exit 1 |
| `adb` | Not used |

## P21-1. Fix diff + choice + tests

### a. Why (a)-as-written and (b) were not chosen (code evidence)

| Option | Finding | Receipt |
|---|---|---|
| (a) exact entry → containing function | `sub_003E39A8` pc switch (`$O/sub_003E39A8_0x3e39a8.cpp:21-29`) has cases only for `0x3e39f0/0x3e3a08/0x3e3a14/0x3e3a3c/0x3e3a7c/0x3e3af0`; NO `case 0x3e3ad8`, NO `label_3e3ad8` anywhere in the file; `default: break` falls through to `ctx->pc = 0x3e39a8` (function top). Registering `0x3e3ad8` → containing fn would run the parent from its prologue, not the callback body | File excerpt above; table slots `:380392-380398` in `register_functions.cpp` mirror exactly the entry + 6 switch cases |
| (b) backward-scan to registered range | Scan finds `0x3e39a8` → same run-from-top mis-execution; MORE code than (a); changes miss semantics for EVERY mid-range pc; no range table exists in the runtime (sparse slots only — a scan has no principled bound) | `ps2_runtime.cpp:1289-1293` (`hasFunction` = one slot test); no range API in `ps2_runtime.h` |
| CSV split (P1l mechanism; not a brief option) | Functionally correct: `0x3e3ad8` sits on a clean `jr $ra` @ `0x3e3acc` / delay @ `0x3e3ad0` / `nop` @ `0x3e3ad4` boundary, body ends `jr $ra` @ `0x3e3af4` / delay @ `0x3e3af8` / `nop` @ `0x3e3afc`; collision predicate (`case`/`label_` in enclosing file) = 0. NOT chosen: both CSVs live in `$W/P1` (untracked — `git ls-files` shows no CSV), so a split yields no tracked diff and fails the brief's `Fix:`-commit + `the diff` receipt | `$O/sub_003E39A8:351-374,394-419`; `git ls-files \| grep csv` = analyzer sources only |
| (c) chosen shape | Exact table entry for `0x3e3ad8` pointing at a faithful host shim of the 8 straight-line insns (not at the containing function). Pc-keyed (`== 0x3E3AD8u`): zero effect on any other pc/game. `!hasFunction` guard: yields to any future real entry (CSV split overrides the shim with no code change) | Diff §P21-1b |

### b. The diff (`58c9144`, 1 file, +46, both trailers)

`Stubs/CD.cpp` anonymous namespace (shim) + 4-line hook in `queueCdCallback`
(after the `g_cdCallbackFn == 0u` early return). Registration runs lazily at
first qualifying callback (post-table-init; a static-init registration would
race table setup). Test-linkable: calls lib APIs only (`dispatchGuestBranch`,
table APIs, `SET_GPR_*`/`READ*`/`WRITE64`/`FAST_READ32` via `Common.h` →
`ps2_runtime_macros.h`); no generated symbols (tests link without runner).

```
+        // P1t: SSX3 registers its CD-completion callback at 0x3E3AD8, which
+        // sits mid-function (inside sub_003E39A8's range) with no exact table
+        // entry, so the scheduler silently drops the invocation (!hasFunction
+        // + nonempty invocations zeroes pc). The containing recompiled
+        // function cannot enter mid-block (its pc switch has no 0x3E3AD8
+        // case; default falls through to the function top), so the exact
+        // entry points at this faithful host emulation of the 8 straight-line
+        // MIPS insns instead. Yields to any real recompiled entry (CSV split).
+        constexpr uint32_t kSsx3CdCallbackPc = 0x3E3AD8u;
+
+        void ssx3CdCallbackSemaSignal(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
+        {
+            // 0x3e3ad8: lui $v0,0x52
+            SET_GPR_S32(ctx, 2, 0x00520000);
+            // 0x3e3adc: addiu $sp,$sp,-0x10
+            SET_GPR_S32(ctx, 29, (int32_t)ADD32(GPR_U32(ctx, 29), 4294967280));
+            // 0x3e3ae0: lw $a0,-0x63B4($v0) ($a0 = *(0x519C4C))
+            SET_GPR_S32(ctx, 4, (int32_t)FAST_READ32(0x519C4Cu));
+            // 0x3e3ae4: sd $ra,0x0($sp)
+            WRITE64(ADD32(GPR_U32(ctx, 29), 0), GPR_U64(ctx, 31));
+            // 0x3e3ae8: jal 0x423DD0 (iSignalSema; ra = 0x3E3AF0)
+            SET_GPR_U32(ctx, 31, 0x3E3AF0u);
+            ctx->pc = 0x423DD0u;
+            if (!runtime->dispatchGuestBranch(rdram,
+                                              ctx,
+                                              0x423DD0u,
+                                              0x3E3AE8u,
+                                              0x3E3AF0u,
+                                              PS2Runtime::GuestBranchKind::DirectCall,
+                                              "JAL"))
+            {
+                return;
+            }
+            ctx->pc = 0x3E3AF0u;
+            // 0x3e3af0: ld $ra,0x0($sp)
+            SET_GPR_U64(ctx, 31, READ64(ADD32(GPR_U32(ctx, 29), 0)));
+            // 0x3e3af4: jr $ra / 0x3e3af8 (delay): addiu $sp,$sp,+0x10
+            const uint32_t target = GPR_U32(ctx, 31);
+            SET_GPR_S32(ctx, 29, (int32_t)ADD32(GPR_U32(ctx, 29), 16));
+            ctx->pc = target;
+        }
+
             if (g_cdCallbackFn == kSsx3CdCallbackPc && !runtime->hasFunction(g_cdCallbackFn))
             {
                 runtime->registerFunction(g_cdCallbackFn, ssx3CdCallbackSemaSignal);
             }
```

(Hook shown abridged: 4 added lines inside `queueCdCallback` + blank; the
`void queueCdCallback...` context lines are unchanged.)

### c. Shim fidelity (each guest insn → shim line)

| Guest @ pc | Effect | Shim line | Same-as-recompiled check |
|---|---|---|---|
| `lui $v0,0x52` @ `0x3e3ad8` | `$v0`=`0x520000` | `SET_GPR_S32(ctx, 2, 0x00520000)` | Literal copy of `$O:376` |
| `addiu $sp,-0x10` @ `0x3e3adc` | `sp`-16 | `ADD32(sp, 4294967280)` | `4294967280`=`0xFFFFFFF0`=-16 (check §P21-1e); mirrors `$O:379` |
| `lw $a0,-0x63B4($v0)` @ `0x3e3ae0` | `$a0`=`*(0x519C4C)` | `FAST_READ32(0x519C4Cu)` | `0x520000-0x63B4`=`0x519C4C` (check); `FAST_` matches `$O:382` (const addr, no special check) |
| `sd $ra,0(sp)` @ `0x3e3ae4` | stack spill | `WRITE64(ADD32(sp, 0), GPR_U64(ra))` | Token-identical to `$O:385` (watch/trace/special handling included) |
| `jal 0x423DD0` @ `0x3e3ae8` | `ra`=`0x3e3af0`, call | `SET_GPR_U32(ra, 0x3E3AF0u)` + `ctx->pc=0x423DD0` + `dispatchGuestBranch(…,0x423DD0,0x3E3AE8,0x3E3AF0,DirectCall,"JAL")` + `if(!…)return; ctx->pc=0x3E3AF0` | Token-identical to `$O:388-393`; trampoline sets `pc`=`0x423DD8`/`$v1`=`-0x43`, so the `[diag:sema]` emit sees `pc`=`0x423DD8` `ra`=`0x3e3af0` exactly as the compiled path would |
| `ld $ra,0(sp)` @ `0x3e3af0` | restore `ra` (0) | `SET_GPR_U64(ra, READ64(ADD32(sp,0)))` | Token-identical to `$O:397` |
| `jr $ra` @ `0x3e3af4` + delay `addiu sp,+0x10` @ `0x3e3af8` | `pc`=`ra`=0 (invocation pops), `sp` net-zero | `target=GPR_U32(ra); sp+=16; ctx->pc=target; return` | Same order as `$O:401-415` (delay before `pc` write); `pc`=0 → scheduler pop path (`Sched:461-478`) unchanged |
| `EeDispatcherTransfer` from the signal path | — | No catch in shim (same as any recompiled caller) → propagates to the scheduler's catch identically | `dispatchGuestBranch` has no catch (`ps2_runtime.cpp:1649-1663`); scheduler catches at `Sched:575-579` |

Net register/memory effect at return: `$v0`=signal result, `$v1`=`-0x43`,
`$a0`=sema id, `sp`/`$ra` restored, one 8-byte stack slot written, `pc`=0 —
the same state the compiled body would leave.

### d. Tests + build (before/after A/B with stash)

| Run | Tree | Total | Passed | Failed |
|---|---|---|---|---|
| Baseline (fix stashed, sidecars purged, rebuilt) | `be01146` | 425 | 424 | 1: `sceGsSyncVCallback runs as a scheduler invocation on its callback stack` (`callback invocation should use the reserved async stack pool`) |
| Fixed (8 pre-stash runs + 1 post-restore run, sidecars purged, rebuilt) | `be01146` + CD.cpp | 425 | 424 | 1: same test + same assertion (9/9 fixed runs; 11/11 runs session-wide identical) |

| Item | Value |
|---|---|
| New failures from the fix | 0 (before/after identical: same totals, same single test, same assertion) |
| P1s-baseline mismatch note | P20-3 recorded the 1 failure as `GS alpha-test AFAIL…`; this session's BASELINE rebuild (same `be01146` tracked tree, fix stashed) fails `sceGsSyncVCallback` instead — the AFAIL↔GsSyncV flip predates this session (same sources, different failing test across builds; P13-1d also recorded GsSyncV failing at P1l). Out of scope; §P21-5 |
| Rebuild | `cmake --build /tmp/p1-link/runtime --target ps2EntryRunner ps2x_tests -j4`, exit 0 (final, post-purge) |
| Sidecar incident | `._CD.cpp` AppleDouble re-created on the volume after edits; globbed as a TU → `3968 warnings and 13 errors`. Fixed by repo-wide `find . -name '._*' -delete` before every build (3 purges this session); never committed |
| Binary | `7c67f28588ef679bdb08f2d72e6a5ba49e6f63274a624894a5056e552a81e414` (`ps2EntryRunner`, 163 MB class) |

### e. Machine-check paste block (every hand computation in Part 21)

```
python3 -c "print(hex(4294967280), hex((0x520000-0x63B4)&0xFFFFFFFF), hex(0x3e3ae8+8), 757352+(0x3e3ad8-0x3e39a8)//4)"
→ 0xfffffff0 0x519c4c 0x3e3af0 757428
python3 -c "print(hex(0xFFFFFFFF & -1), hex(0x31aa84+8), hex(0x31aadc+8), hex(0x31acec+8), 1389653-4119, 139001723-566220, round(237/17,2), round(1387579/90))"
→ 0xffffffff 0x31aa8c 0x31aae4 0x31acf4 1385534 138435503 13.94 15418
python3 -c "print(1388287-2917, 1385534-(1388287-2917))"
→ 1385370 164
```

Row 1: addiu `-16` word; `lw` address; callback `jal` ra; table slot of
`0x3e3ad8` (slot(`0x3e39a8`)=757352 from `register_functions.cpp:380392`).
Row 2: sema id `-1` word; the three `jal`→`ra` checks (§P21-2c); LOG1−p1s
line delta (+1,385,534) and byte delta (+138,435,503); id-29 signals/block
(~14); `-1` waits/second (~15,418).
Row 3: `[diag:sema]` line delta (LOG1 1,388,287 − p1s 2,917) and the misc
remainder (+164).

## P21-2. Boot + chain answer (2 boots)

### a. Boot headers

| Item | Boot 1 (LOG1) | Boot 2 (LOG2) |
|---|---|---|
| Log | `$W/P1/run/boot-p1t-1.log`, 1,389,653 lines, 139,001,723 B, 17 blocks | `$W/P1/run/boot-p1t-2.log`, 1,370 lines, 139,914 B, 17 blocks |
| Env | p1s env byte-identical (`/tmp/p1t-boot1.py` differs from `/tmp/p1s-boot1.py` in docstring + LOG only): `PS2X_DIAG_PERIOD_MS=5000`, probe on, `PS2X_DIAG_SEMA=1`, WATCH `0x519c40,0x450de4` | p1s env MINUS `PS2X_DIAG_SEMA` (boot-1's 1.39M-line `-1` flood would repeat; entry-0 needs only WATCH — matches the p1p-2 entry-0 method), WATCH `0x5e0088,0x519c40` |
| Run | Foreground 90 s, SIGTERM rc=-15, CWD `$W/P1/run`, binary `7c67f285` | Same harness, SIGTERM rc=-15, same binary |
| Boot-2 justification (brief's rule) | — | Fix fired + chain stalling at a NEW point (worker re-parked post-#9; thread 1 in `-1` spin) + entry-0 is a brief-required receipt only obtainable with swapped WATCH |

### b. The fix fired: callback signal + epoch order (LOG1)

`ra=0x3e3af0` lines: **1** (LOG1:581; p1s: 0). CD-tagged (`cbFunc=43444342…`)
signals: **1** (same line; p1s: 0). `pc=0x3e3ad8` dispatches: 0 both boots
(the shim emits no pc line; the signal line IS the dispatch proof).

| Line | Content (abridged) |
|---|---|
| :205 | `op=wait id=26 … parked=1 waker=2 pc=0x423de8 ra=0x3e3c20` (first park; same as p1s) |
| :574 | `op=signal id=26 … waiters=1->0 waker=1 pc=0x423dc8 ra=0x3e48b8 … target=2 … result=26` (first signal; same bytes as p1s) |
| :581 | `op=signal id=26 count=0->1 waiters=0->0 waker=2 pc=0x423dd8 ra=0x3e3af0 inInt=1 iSafe=1 invKind=0 invDepth=1 cbFunc=4344434200000001 target=- … result=26` (**NEW**: the callback body ran; count path — worker had not yet re-parked) |
| :582 | `op=wait id=26 count=1->0 parked=0 waker=2 … ra=0x3e3c20 … result=26` (**NEW**: worker consumed the callback's signal, no park) |
| :586 | `op=wait id=26 count=0->0 parked=1 waker=2 … result=park` (worker re-park; same shape as p1s :581) |

Full epoch order (:570–:597; :570–:580 byte-identical to p1s :570–:580,
same line numbers — divergence starts :581):

| Line | Event |
|---|---|
| :572–:573 | `0x519c40` = `0x0` → `0xA` (thread 1, `0x3e4768`/`0x3e48b4`) |
| :574 | first signal 26 → thread 2 |
| :575 | `0x519c40` = `0x2` (thread 2, `0x3e3c4c` — worker wake) |
| :576–:577 | `sceCdRead lbn=0x5f1a3 sectors=1 buf=0x9d0800 ret=0x3e3b8c` + `BIGF` payload (`42494746147c1a00`; same bytes as p1s) |
| :578 | `[cd:callback] queued func=1 cb=0x3e3ad8` |
| :579 | `0x519c40` = `0x2` (thread 2, `0x3e3ba0` — issuer success) |
| :580 | `[cd:callback] start func=1 cb=0x3e3ad8` (attach; thread 2 still running) |
| :581 | **callback signal** (table above; replaces p1s's silent drop) |
| :582 | worker wait consumes `1->0`, no park |
| :583 | `0x519c40` = `0x0` (thread 2, `pc=0x3e3d68 ra=0x3e3d6c` — the site-#9 `jal 0x3DE420` delay-slot store; G6 passed, W1 issued) |
| :584–:585 | worker pump id-5 lock/unlock pair (`waker=2`, `ra=0x3e5738`/`0x3e57bc`) |
| :586 | worker re-parks on 26 |
| :587–:592 | thread-1 id-5 pairs |
| :593 | `[diag:driver-entry] sp=0x1fffe80 ra=0x3ded88 sourcePc=0x3ded80 checkpointed=0` (same bytes as p1s :582 — the driver ran downstream of #9) |
| :594–:595 | thread-1 id-5 pair |
| :596 | `op=signal id=28 count=0->1 … waker=1 pc=0x423dc8 ra=0x31acf4 … result=28` (**NEW** id; `jal SignalSema` @ `0x31acec`, delay `lw $a0,0x4044($v1)`, `sub_0031AAF0`) |
| :597 → :1389654 | thread-1 `WaitSema(-1)` spin begins (§P21-2c) |

Chain answer rows (brief's Step-2 list):

| Receipt | Value |
|---|---|
| `ra=0x3e3af0` signal lines | 1 (:581 — the callback body RAN) |
| Thread-2 wake past the epoch | None: thread-2 `scheduled` = 2 (b0) then 0 ×16 (same bytes as p1s); worker did its pass inside b0 and re-parked :586; nothing re-signaled 26 after |
| Site #9 / G6 | **REACHED**: G6 passed (W1 prelude ran), site-#9 `jal` issued (:583 delay store), driver entered (:593 probe). No new residue at #9 — the worker cycled to G0 and re-parked awaiting the next completion |
| Entry-0 flag at park | **Still 0** (LOG2: set `0x1` @ `0x3de468` :387, cleared @ `0x3e6518` :389; §P21-2e). Thread 1 has no single new park (samples spread; §P21-2d) — the chain did not settle |

### c. New stall point: `WaitSema(-1)` spin (LOG1 :597 → end)

| Item | Value |
|---|---|
| Shape | `op=wait id=-1 count=-1->-1 parked=0 waker=1 pc=0x423de8 ra=0x31aa8c inInt=0 result=-408` (`KE_UNKNOWN_SEMID`; never blocks → hot guest loop) |
| Count | 1,387,579 waits (1,387,578 at `ra=0x31aa8c` + 1 stderr-interleaved line :549183); ~15,418/s over 90 s |
| Call site | `jal WaitSema` @ `0x31aa84` (delay `lw $a0,0x18($s0)` → `$a0`=`*($s0+0x18)`=`-1` = `0xFFFFFFFF`), `sub_0031A6B8` (`0x31a6b8`–`0x31aaf0`); post-call `sw $zero,0x1C($s0)` @ `0x31aa8c` (`$O/sub_0031A6B8:2105-2133`) |
| Sibling signals | 24 × `op=signal id=-1 … waker=4 pc=0x423dc8 ra=0x31aae4 inInt=0 … result=-408` (`jal SignalSema` @ `0x31aadc`, delay `lw $a0,0x18($a0)`, same function `$O:2305-2331`) |
| Steady stub cluster (b1, all blocks same regime) | `0x31a9d8`/`0x31a268`/`0x31aa18`/`0x31a308`/`0x31a3c0` @174,669; `0x423de0` (WaitSema) @87,349 `firstRa=0x31aa8c`; `0x423df0` (PollSema, syscall `0x45` — NEW id) @87,335 `firstRa=0x31aa98`; `0x3174a8`/`0x31ad00`/`0x3e5928`/`0x31aa58`/`0x317328` @87,334 (outer loop via `0x316e0c`/`0x316e3c`/`0x316e44`/`0x316e5c`, `sub_00316D60`; tick pc `0x316e3c` = `jal func_317328`) |
| Steady syscalls (b1) | `0x44` @87,350, `0x45` @87,335, `0xffffffbd` @15, `0x42` @1 (p1s b1: `0x2f` @740,054, `0x44` @80, `0xffffffbd` @80) |
| Old-loop absence | `firstRa=0x3dd280`/`0x3dd290`: 17/17 (p1s) → 0/0; `0x3e5440` 536K–740K/block (p1s) → unprinted all blocks (a 740K entry would print #1; truly unhit, not cutoff) |

P1s comparison: ZERO `id=-1` lines in p1s (P20-2c: every signal returned
its id, no `-408`). The spin starts :597, immediately after the :593 driver
probe — new behavior downstream of the chain progress.

### d. Per-block threads (LOG1, all 17; `sch` = `scheduled`)

Thread 1 and thread 4 dispatch in lockstep b1+ (identical counts every
block); thread 2 sch 2 then 0 ×16; thread 3 Ready @ `0x31ac60` sch 0
(always; same as p1s); thread 5 sch 1 (b0) then 0 ×16 (same as p1s).

| blk | id1 pc | id1 sch | id2 sch | id4 sch | blk | id1 pc | id1 sch | id2 sch | id4 sch |
|---|---|---|---|---|---|---|---|---|---|
| 0 | `0x317328` | 36 | 2 | 12 | 9 | `0x3e5980` | 14 | 0 | 14 |
| 1 | `0x3e5980` | 15 | 0 | 15 | 10 | `0x3e5980` | 14 | 0 | 14 |
| 2 | `0x3e5980` | 14 | 0 | 14 | 11 | `0x31ad00` | 14 | 0 | 14 |
| 3 | `0x31a278` | 13 | 0 | 13 | 12 | `0x31a278` | 12 | 0 | 12 |
| 4 | `0x3e5928` | 14 | 0 | 14 | 13 | `0x31a278` | 15 | 0 | 15 |
| 5 | `0x3e5980` | 13 | 0 | 13 | 14 | `0x3e5980` | 14 | 0 | 14 |
| 6 | `0x3e5980` | 12 | 0 | 12 | 15 | `0x3e5980` | 14 | 0 | 14 |
| 7 | `0x3e5980` | 14 | 0 | 14 | 16 | `0x31a278` | 14 | 0 | 14 |
| 8 | `0x423df0` | 14 | 0 | 14 | | | | | |

(Threads 2/4/5 pcs `0x423de8` all blocks; waitIds 26/29/30; entries
`0x3e3be0`/`0x31ac08`/`0x382740`; priorities 12/99/5 — all same as p1s.
New-pc resolutions: `0x317328` = entry `sub_00317328`; `0x31a278` in
`sub_0031A268`; `0x31ad00` in `sub_0031AAF0`; `0x3e5928` = entry
`sub_003E5928`; `0x423df0` = entry `sub_00423DF0` (PollSema trampoline).)

### e. Boot 2: entry-0 + epoch reproduce (LOG2, 1,370 lines)

| Line | addr + width | value | pc | thread | ra | sp |
|---|---|---|---|---|---|---|
| :58 | `0x5e0088` w8 | `0x0` | `0x3e64d0` | 1 | `0x3dcd10` | `0x1fffe80` (init-time `sd`; same bytes as p1p-2 :57) |
| :387 | `0x5e0088` w4 | `0x1` | `0x3de468` | 1 | `0x3de3fc` | `0x1fffa90` (**SET**; in `sub_003DE420` range) |
| :389 | `0x5e0088` w4 | `0x0` | `0x3e6518` | 1 | `0x3de7e4` | `0x1fffe00` (**CLEARED**; last write — final value 0) |

Order around the cycle: :386 worker #9 delay store (`0x519c40`=`0x0` @
`0x3e3d68`, thread 2 — the :583-equivalent) → :387 entry-0 SET (thread 1)
→ :388 driver probe (same bytes as LOG1 :593) → :389 entry-0 CLEAR
(thread 1). Epoch control fully reproduced: :378/:379 (`0`→`0xA`),
:380 (wake `0x2`), :383 queued, :384 (issuer `0x2`), :385 start, :386 (#9),
:388 (probe). `0x450DE4`: 0 writes (LOG1; same as p1s).

Boot-2 thread-1 pcs: `0x3e5980` ×12, `0x31a278` ×4, `0x31a268` ×1 (LOG1:
`0x3e5980` ×8, `0x31a278` ×4, `0x317328`/`0x3e5928`/`0x423df0`/`0x31ad00`
×1) — both boots sample a cycle, not a point.

### f. Before/after: dispatch behaviors the fix must not change (LOG1 vs p1s)

No scheduler/dispatch/table code changed (the fix only ADDS table slot
757428 at runtime); these receipts confirm the addition leaked nowhere.

| Behavior | Before (p1s) | After (LOG1) | Reading |
|---|---|---|---|
| Exact-entry hits (stub b0 top-30) | 30 printed (486 distinct) | 30 printed (496 distinct); 20/30 shared with p1s b0 | 10 dropped from b0 top-30, 10 added (§below) |
| Dropped from b0 top-30 | — | `0x326eb0`/`0x3ffa58`/`0x3ffbc0`/`0x423dc0`/`0x423dd0` reappear in LOG1 b1+ blocks (below b0 cutoff=134, still dispatched); `0x3e5700`/`0x3e5760` (pump; p1s b0 count 74 < 134) proven still dispatched by the sema trace (66 id-4 + 13 id-5 pairs with pump `ra`s); `0x4123e8`/`0x41605c` (p1s b0 counts 68/117 < 134) unobservable below cutoff; `0x3e5440` (p1s 536K–740K/block) truly unhit — thread 1 left that loop (the fix's effect, §P21-2c) | Cutoff effects + 1 genuine (intended) path change |
| Added to b0 top-30 | — | `0x317328`/`0x3174a8`/`0x31a268`/`0x31a308`/`0x31a3c0`/`0x31a9d8`/`0x31aa18`/`0x31aa58`/`0x31ad00`/`0x423df0` (the `-1`-spin cluster; counts 134–129,855) | New code reached, not new dispatch rules |
| All-block printed sets | 40 targets | 49 targets (5 p1s-only listed above; 14 LOG1-only = the 10 + `0x3ffcd8`/`0x3ffd60`/`0x400190`/`0x400250`) | Same story at full-boot scope |
| Syscall ids printed | 20 ids (b0 27 distinct, b1+ 3) | 19 p1s ids + `0x45` NEW (PollSema; the spin loop), `0x17` unobserved (p1s: count 1, b0-only boot call — below cutoff or path change) | `0x2f` (740K/block p1s steady) gone from steady with the old loop; `0x44`/`0xffffffbd` still hit (new rates) |
| Miss diagnostics | `missing-target` 0; `No exact recompiled function` 0 | 0; 0 | Silent paths exactly as before |
| Empty-invocations path | `[diag:dormant]` 40; `[diag:start-thread]` 4 | 40; 4 (same counts) | Same code, same counts |
| Sema result census | Every signal returned its id (no `-408`) | Same EXCEPT the NEW `id=-1` class (1,387,579 waits + 24 signals, all `-408` — guest passing a bad id, not a path change) | Path behavior identical; new guest input class |

Full signal census (LOG1; `waits/sigs`):

| Waits | Sigs | `ra` (site) | `id` | Decodes to |
|---|---|---|---|---|
| 1,387,579 | 24 | `0x31aa8c` / `0x31aae4` | -1 | `jal WaitSema` @ `0x31aa84` / `jal SignalSema` @ `0x31aadc` (`sub_0031A6B8`); all `result=-408`; waits `waker=1`, sigs `waker=4 inInt=0 iSafe=0` |
| 238 | 237 | `0x31ac30` / `0x31abf8` | 29 | Same shape as p1s (`waker=1 inInt=1 iSafe=1 invKind=0 invDepth=1 cbFunc=0`, `target=4`; byte-identical line shape) — count only changed (1,360→237) |
| 66 | 66 | `0x3e5738` / `0x3e57bc` | 4 | Pump thread-site; same counts as p1s |
| 13 | 13 | `0x3e5738` / `0x3e57bc` | 5 | Same site (12× `waker=1` + 1× `waker=2` worker pair :584–:585); p1s was 8/8 |
| 3 | 2 | `0x3e3c20` / `0x3e48b8`+`0x3e3af0` | 26 | §P21-2b (first + callback signals; first park + consume + re-park) |
| 1 each | 1 each | `0x3e3598` | 6–25 | One-shot drainer (same as p1s) |
| 2 | 2 | `0x418ce0` / `0x418d3c` | 1 | Count-path pair (same as p1s) |
| 0 | 1 | `0x31acf4` | 28 | NEW single (`jal SignalSema` @ `0x31acec`, `sub_0031AAF0`; :596) |
| 0 | 0 | `0x3e57ac` | — | Pump i-site never taken (same as p1s) |
| 1 | — | `0x316e3c` bleed | — | NOT a site: 1 wait line (:549183) interleaved mid-line with a `[run:tick]` line (concurrent stderr; `pc=0x316e3c` belongs to the tick). A 2nd wait line ends `…inInt=0` (truncated twin). Both counted in the `-1` total; neither is a sema-path variant |

### g. Ladder delta vs boot-p1s-1 (4,119 lines, 566,220 B)

LOG1: 1,389,653 lines, 139,001,723 B, 17 blocks (+1,385,534 lines =
+1,385,370 `[diag:sema]` + 164 misc; check row 3 §P21-1e).

| Rung | boot-p1s-1 | LOG1 | Delta |
|---|---|---|---|
| Thread-1 pc | `0x3e5980` ×17 | `0x3e5980` ×8, `0x31a278` ×4, 4 others ×1 (§P21-2d) | Left the static park; cycles |
| Thread-1 sch | 84/81/81/80/70/81/81/81/78/77/69/81/81/81/78/78/70 | 36/15/14/13/14/13/12/14/14/14/14/14/12/15/14/14/14 | New regime (~12–15 + b0 36) |
| Thread-2 | parked 26 @ `0x423de8`, sch 2 then 0 ×16 | Same bytes | None |
| Thread-3 | Ready @ `0x31ac60`, sch 0 | Same | None |
| Thread-4 | parked 29 @ `0x423de8` (sch 60 b0) | Same ids/pcs/entries (sch 12 b0, 12–15 steady) | Count regime only |
| Thread-5 | parked 30 @ `0x423de8` (sch 1 b0) | Same (sch 1 b0) | None |
| Missing target / `No exact` | 0 / 0 | 0 / 0 | None |
| Stub distinct b0 / b1–16 | 486 / 18 | 496 / 31,27 ×15 | +10 / +13,+9 (new paths) |
| Syscall distinct b0 / b1+ | 27 / 3; 20 printed ids | 28 / 4; 19 shared + `0x45`, minus `0x17` | §P21-2f |
| CD callback | :578 + :580 (func=1 cb=`0x3e3ad8`) | :578 + :580 (same func/cb/lines) | None |
| CD read | :576 same lbn/ret/buf/payload | Same line, same bytes | None |
| CD reads total | 21 | 21 | None |
| Probe | 1 (:582, p1o bytes) | 1 (:593, same bytes) | Line number only |
| Watch `0x519C40` | 7 lines | 8 lines (+:583 #9 store) | The progress receipt |
| Watch `0x450DE4` | 0 writes | 0 writes | None |
| VIF MPG/MSCAL | 0 | 0 | None |
| GIF/GS | gif 2 / kick 66 / reg 122 / prim 33 / copy-reg 8 / texa 1 | 2 / 66 / 122 / 33 / 8 / 1 | None |
| `run:tick` | 6 | 7 (sampled `pc=0x316e3c`) | +1 (timing regime) |
| Presented frame | None | None (sole `frame` hit = raylib TIMER line) | None |
| Crash / FATAL | 0 / 0 | 0 / 0 | None |
| Dormant / start-thread | 40 / 4 | 40 / 4 | None |
| SIF module lines | 6 | 6 | None |
| `firstRa=0x3dd290` / `0x3dd280` | 17 / 17 | 0 / 0 | Old loop gone |
| `target=0x3de420` / `0x3ddfa8` | 0 / 0 | 0 / 0 | None (the #9 `jal 0x3DE420` executed — :583 + :593 prove it — but count 1 sits below the print cutoff; `0x3de420` has a CSV row + 44 reg lines, so dispatch was exact, not missed) |

## P21-3. Binaries and commits

| Binary / ref | sha256 / sha | Sources / state |
|---|---|---|
| `/tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner` (both boots) | `7c67f28588ef679bdb08f2d72e6a5ba49e6f63274a624894a5056e552a81e414` | `58c9144` tree (P1t `Fix:` on `be01146`; incremental `-j4` rebuild, exit 0) |
| `ps2x_tests` (CWD `$R`, rebuilt) | Total 425, Passed 424, Failed 1 (`sceGsSyncVCallback … reserved async stack pool`) | Before/after A/B identical (§P21-1d); failure pre-existing (also P1l/P1j), unrelated, not fixed |
| `PS2Recomp` branch `ssx3` HEAD | `58c9144` (`Fix: dispatch the mid-label CD callback at 0x3E3AD8 via a faithful host shim (P21-1)`, 1 file, +46, two trailers) | Sole P1t fork commit; worktree sole `M` = pre-existing generated `runner/register_functions.cpp`, never added |
| I2 commits in history | `66d992c` (I2-G5), `d62c4b5` (I2-G6) | Other agent's; present at session start, untouched |
| Fork push | `git push fork ssx3` from fork clone only (§P21-4) | The only push allowed (no push in ssx3) |
| This report | `[P1t]` commit (two trailers; local only) | Sole ssx3-repo change; no `runner/`, log, or `._*` added |

## P21-4. Exact commands

From `$R` (fork) unless noted; `$W=/Volumes/Extreme SSD/ps2recomp-spike`,
`$O=$W/P1/output`, `LOG1`/`LOG2` as above:

```
# Step 1 (static; no lease)
re-read REPORT Part 20 (paged reads)
read EeScheduler.cpp run loop (280-585) + ps2_runtime.cpp table/slot/dispatch
  (1060-1096, 1240-1293, 1314-1347, 1580-1664) + Stubs/CD.cpp queueCdCallback (1-88)
  + Sync.cpp (all) + ps2_runtime.h API decls + trampoline sub_00423DD0
read $O/sub_003E39A8 (switch 1-30, callback 330-419) + csv rows (7215-7216)
python3 hex checks (row 1 §P21-1e); slot/label census (register_functions.cpp:380392-8)
(edit_file: kSsx3CdCallbackPc + ssx3CdCallbackSemaSignal + queueCdCallback hook, CD.cpp only)
find ps2xRuntime/src/lib/Kernel -name '._*' -delete   (re-run repo-wide before EVERY build)
cmake --build /tmp/p1-link/runtime --target ps2EntryRunner -j4 (exit 0)
cmake --build /tmp/p1-link/runtime --target ps2x_tests -j4 (exit 0)
ps2x_tests CWD $R (8 runs: 425/424/1 GsSyncV each; named via [Failed] grep)
git stash push -- <CD.cpp>; purge; rebuild; ps2x_tests x2 (baseline 425/424/1 GsSyncV)
git stash pop; purge; rebuild both targets (exit 0); ps2x_tests (425/424/1)
shasum -a 256 ps2EntryRunner (7c67f285)
git add ps2xRuntime/src/lib/Kernel/Stubs/CD.cpp (NAMED file only; runner/ left alone)
git commit -m "Fix: ..." (two trailers; NO push yet) -> 58c9144
(write /tmp/p1t-boot1.py; diff vs p1s-boot1.py = docstring + LOG only)
# Step 2 (lease protocol + boot 1)
cat /tmp/ssx3-host-lease (M12 once mid-session; absent 18:54:25Z + 18:55:02Z; no polls)
pgrep -x ps2EntryRunner (exit 1); shasum (7c67f285 fresh); git log (58c9144); ls ISO + ELF
printf 'P1t\n' > /tmp/ssx3-host-lease (18:55:07Z, absent verified twice) + >> p1t-waits.log
python3 /tmp/p1t-boot1.py (CWD $W/P1/run, 90 s, SIGTERM rc=-15, 139001723 B)
# Step 2 (log analysis, lease-free; lease still held)
sema census: 1388287 lines; id-26 5-line record; ra=0x3e3af0 x1; cbFunc-tagged x1
epoch order :570-:597; per-block thread table (17x5); watch/probe/cd sweeps
-1 census: waits by ra/waker/result; sigs by ra/waker; ra-resolution via csv + $O excerpts
  (sub_0031A6B8:2095-2133 + :2305-2331, sub_0031AAF0:1235-1266, sub_00316D60:491-531)
stub b0 sort-compare (comm) + all-block set compare + cutoff + b1 steady table
syscall id-set compare + b1 lists; dormant/start-thread/VIF/GIF/frame/crash/
  missing-target/No-exact/SIF/firstRa/target sweeps; p1p-2 entry-0 method re-read (P17-1/2)
# Step 2 (boot 2)
(write /tmp/p1t-boot2.py: SEMA unset, WATCH 0x5e0088,0x519c40, LOG2)
cat lease (P1t); pgrep -x (exit 1)
python3 /tmp/p1t-boot2.py (90 s, SIGTERM rc=-15, 139914 B)
entry-0 3-line record (:58/:387/:389) + epoch-control check (:378-:388) + pc sample lists
python3 hex checks (row 2 §P21-1e)
# Step 3
(edit_file append Part 21 in 3 chunks)
git -C /Users/bradrichardson/dev/ssx3 add -f local/research/P1/REPORT.md
git -C /Users/bradrichardson/dev/ssx3 commit -m "[P1t] ..." (two trailers; NO push there)
git -C $R push fork ssx3 (the only push allowed)
rm -f /tmp/ssx3-host-lease; ls (absent); pgrep -x (exit 1)
```

Env delta boot 1 vs boot-p1s-1: NONE (script diff = docstring + LOG).
Env delta boot 2 vs boot 1: `PS2X_DIAG_SEMA` unset + WATCH swapped to
`0x5e0088,0x519c40`. Source delta: `Stubs/CD.cpp` (+46).

## P21-5. What I could not do

- Attribute the `-1` sema slot to a writer: `$a0`=`*($s0+0x18)` at the
  `0x31aa84` call (thread 1) and `$a0`=`*($a0+0x18)` at `0x31aadc`
  (thread 4) read `-1` constantly (1.39M identical reads; nothing wrote the
  slot this boot). The next brief owns the `-1` stall (CreateSema failure?
  uninitialized slot? deleted sema?).
- Observe `0x4123e8`/`0x41605c` in LOG1 (below the b0 print cutoff of 134;
  p1s b0 counts were boot-phase 68/117). Presence neither confirmed nor
  denied — the histogram cannot see below cutoff.
- Explain the AFAIL↔GsSyncV single-failure flip across builds (same
  `be01146` tree fails different single tests in different build/run
  sessions). Within-session before/after is identical (11/11 runs), so it
  does not touch this fix; the GS-test order/state dependence is untouched.
- Add a committed unit test for the shim: the runbook's Step-1 receipt list
  is closed (diff + `ps2xTest` baseline + rebuild green) and demands a
  minimal one-file diff; a scheduler+callback harness would be a second
  file of substantial line count. The two boots are the behavior receipts.
- Keep LOG1 under the 50 MB soft cap: the brief mandates the p1s env
  (`PS2X_DIAG_SEMA=1`), and the `-1` spin (guest behavior unlocked by the
  fix) emits 1.39M trace lines under it. Under the 200 MB hard cap (139 MB).
  Boot 2 ran SEMA-off for the entry-0 receipt.
- Settle thread 1 on a single park: both boots sample a cycle
  (`0x3e5980`/`0x31a278`/others), and entry-0 ended at 0 — the chain
  advanced (worker full pass + driver run) but did not complete.
- Run a third boot (reserve exhausted at two by the brief's max).
- One `.[._*]`-class note: two LOG1 sema lines are malformed by concurrent-
  stderr interleaving (:549183 tick-bleed + 1 truncated twin); both counted
  in the `-1` total, neither a sema-path variant.

---

## Part 22 (P1u): the WaitSema(-1) slot attributed — CreateSema#2 zero-param return (-1) stored unchecked; singleton object 0x604890; thread 3 (flag-clearer) starved by the no-block spin

Brief `local/muse/prompts/P1u.md`. Static slot+writers+loop analysis, 1
`Diag:` commit (2 files, +51/-7) + 1 boot. Tables, no verdicts.
Stale-reading guard: Part 21 (P21-2c the `-1` spin shape + call sites,
P21-2f census, P21-5 the unattributed-slot residue) + Part 20 §P20-1 (sema
signal/wait paths, id-validation read) re-read before acting.
`W=/Volumes/Extreme SSD/ps2recomp-spike`, `R=$W/PS2Recomp` (fork, branch
`ssx3`), `O=$W/P1/output`, `LOG=$W/P1/run/boot-p1u-1.log`. File:line refs
below are `ps2xRuntime/src/lib/` unless noted. All hand hex
machine-checked §P22-1f; all cited MIPS words ELF-verified §P22-1g.

## P22-0. Lease record

| Event | Value |
|---|---|
| Lease at session start | Absent (verified before Step 1; static work claimed none) |
| M13 hold | Never observed this session; no poll loop ran, zero wait polls |
| Waits log | `$W/P1/run/p1u-waits.log` (2 lines: claim timestamp + claim record) |
| Pre-claim checks (20:01:01Z) | `pgrep -x ps2EntryRunner` exit 1; lease absent (verified twice); binary `559521a6` (P1u Diag build); fork HEAD `de7ff17`; ISO 3005415424 B + ELF 3890784 B present |
| Claim | `printf 'P1u\n' > /tmp/ssx3-host-lease` 20:01:10Z, immediately before boot-p1u-1 |
| Boot 1 | 90 s foreground, SIGTERM rc=-15, end ≈20:02:41Z (log mtime; ExFAT local clock), LOG 28,980,295 B, 258,784 lines, 16 blocks |
| Second boot | None (Step-2 question closed by boot 1; reserve unused) |
| Release | After Step 3 push (below); verified absent; `pgrep -x` exit 1 |
| `adb` | Not used |

## P22-1. Slot + writers + loop intent (static, no lease, no boot)

Conventions: `Sched` = `Kernel/EeScheduler.cpp`; `Sync.cpp` =
`Kernel/Syscalls/Sync.cpp`; `Dispatch` = `Kernel/Syscalls/Dispatcher.cpp`.
`$O/sub_0031A6B8` = analyzer-merged `0x31a6b8`–`0x31aaf0` (CSV single row
`sub_0031A6B8,0x31a6b8,0x31aaf0,0x438`); `$O/sub_0031AAF0` =
`0x31aaf0`–`0x31ad18`. Method shorthands F1–F7 (table §P22-1a).

### a. The object + its method table (F2 = ctor, F3 = dtor, F6 = wait, F7 = signal)

Zero direct JALs to any of `0x31a6d8/0x31a920/0x31a9d8/0x31aa18/0x31aa58/
0x31aac8` exist in the ELF (full-word sweep; JAL words check row A
§P22-1f; sweep validity: 73 hits for the WaitSema JAL word, 1 hit for
`0x31a6b8` at `0x22863c`). All six addresses appear once each as RAW data
words in one pointer table at `0x48db7c` (8-byte `{code-ptr, 0}` slots;
offsets check row G):

| Table+ | Entry | Block | Role (static shape) |
|---|---|---|---|
| `+0x00` | `0x31a6d8` | F2 | ctor: sp-`0x150`, `$s0`=`$a0`, 4× CreateSema, 2× CreateThread+StartThread, AddIntcHandler; straight-line, ends `jr $ra` @ `0x31a914` |
| `+0x08` | `0x31a920` | F3 | dtor: mirrors F2 (RemoveIntcHandler, Terminate+DeleteThread ×2, SignalSema ×2, DeleteSema ×4); ends @ `0x31a9cc` |
| `+0x10` | `0x31aa58` | F6 | wait: flag=1, vcall, WaitSema(`+0x18`), flag=0, PollSema drain, vcall; ends @ `0x31aac0` |
| `+0x18` | `0x31aac8` | F7 | signal: `if (*(obj+0x1C)) SignalSema(*(obj+0x18))`; ends @ `0x31aae8` |
| `+0x20` | `0x320b08` | — | Outside both method files (not read) |
| `+0x28` | `0x31abc0` | — | `jr $ra` (bare return) |
| `+0x30` | `0x31abc8` | — | `jr $ra`, delay `$v0`=`0x3C` |
| `+0x38` | `0x31acd8` | — | `*(obj+0x14048)`=`$a1`, then SignalSema(`*(obj+0x14044)`) @ `0x31acec` (`ra`=`0x31acf4`) |
| `+0x40` | `0x31ad00` | — | predicate: return (`*(obj+0x14048)`<`1`) |
| `+0x48` | `0x31a9d8` | F4 | `if (*(obj+0x14048)) jal 0x31a3c0(obj+0x14080)` |
| `+0x50` | `0x31aa18` | F5 | `if (*(obj+0x14048)) jal 0x31a308(obj+0x14080)` |
| `+0x58` | `0x31ab30` | — | `*(obj+0x4038)`=1 + GetThreadId + compares (head read) |
| `+0x60` | `0x31ab10` | — | SignalSema(`+0x0C`) @ `0x31ab18`, then SleepThread forever |

Adjacent-but-not-a-member: F1 @ `0x31a6b8` (loads thread id from `gp`+`0xDDC`
— the cell F2's first StartThread stores @ `0x31a834` — then
ChangeThreadPriority(tid,`0x65`)); sole direct JAL @ `0x22863c`.

Instance size ≥ `0x14080` + sub-object (`s3`=`s0`+`0x10000` throughout F2;
sub-object methods take `s0`+`0x14080`; checks row D).

### b. Field layout around `+0x18` (every access ELF-verified §P22-1g)

| Offset | Content | Writers (ELF word) | Readers |
|---|---|---|---|
| `+0x00`/`+0x04` | Untouched by either method file (no access in-file) | None found | None |
| `+0x08` | Iface pointer (F6 dereferences → fnptr at `+0x5C`/`+0x64`, halfword arg-offs at `+0x58`/`+0x60`) | None in either method file (set by the table-external instantiation path) | F6 @ `0x31aa70`/`0x31aaa4` (`0x8e030008`/`0x8e020008`); AAF0 @ `0x31ab7c` |
| `+0x0C` | Sema id A (= -1 this boot, §P22-1d) | F2 CreateSema#1 store @ `0x31a794` (`0xae02000c`, delay slot) | F3 DeleteSema @ `0x31a9b8` (delay `0x8e24000c`); `0x31ab10` SignalSema @ `0x31ab18` (delay `0x8c84000c`; never ran this boot — 0 `ra`=`0x31ab20` lines §P22-2c) |
| `+0x10` | Thread id (GetThreadId result) | F2 @ `0x31a744` (`0xae020010`) | F2 ReferThreadStatus arg @ `0x31a750`; thread-4 WakeupThread arg @ `0x31ac40`; AAF0 @ `0x31ab68`/`0x31ab74`/`0x31acb4` |
| `+0x14` | Thread-status word (`*(sp+0x18)` of ReferThreadStatus) = 100 (thread-1 prio; §P22-2c) | F2 @ `0x31a76c` (`0xae030014`) | Priority derivation ±1 @ `0x31a7f4`/`0x31a87c` → threads at prio 101/99 |
| `+0x18` | **Sema id B = -1 (THE SLOT)** | **F2 CreateSema#2 store @ `0x31a7b8` (`0xae020018`, delay slot) — sole writer (§P22-1c)** | F6 WaitSema @ `0x31aa84` (delay `0x8e040018`), PollSema @ `0x31aa90` (delay `0x8e040018`), compare @ `0x31aa98` (`0x8e030018`); F7 SignalSema @ `0x31aadc` (delay `0x8c840018`); F3 DeleteSema @ `0x31a9b0` (delay `0x8e240018`) |
| `+0x1C` | Flag (0 = idle) | F2 init 0 @ `0x31a7a4` (`0xae00001c`); F6 set 1 @ `0x31aa6c` (`0xae02001c`), clear @ `0x31aa8c` (`0xae00001c`) | F7 gate @ `0x31aad0` (`0x8c82001c`; `beqz`→`0x31aae8` skips the signal) |
| `+0x20` | Done word (0 = run) | F2 init 0 @ `0x31a720` (`0xae000020`); F3 set 1 @ `0x31a95c` (`0xae230020`) | Thread-4 exit test @ `0x31ac30` (`0x8e030020`; nonzero → WakeupThread+SleepThread) |
| `+0x30` | Address-taken once | — (address `s0`+`0x30` passed to 2nd CreateThread @ `0x31a874`) | — |
| `+0x4030` | Thread id B (CreateThread#2) | F2 @ `0x31a8bc` (`0xae024030`, delay) | F3 Terminate+DeleteThread @ `0x31a980`/`0x31a988` |
| `+0x4034` | Sema id D (= 29, valid) | F2 CreateSema#4 store @ `0x31a868` (`0xae024034`, delay) | Thread-4 WaitSema @ `0x31ac28` (delay `0x8e044034`); F3 signal+delete; INTC-tail iSignalSema @ `0x31abf0` |
| `+0x4038` | Kick-enable (0 = kick) | F2 init 0 @ `0x31a838` (`0xae004038`); `0x31ab30` set 1 @ `0x31ab48` (`0xae024038`) | INTC-tail gate @ `0x31abe4` (`bnez` skips the id-29 kick) |
| `+0x4040` | Thread id A (CreateThread#1) | F2 @ `0x31a824` (`0xae624040`) | F3 Terminate+DeleteThread @ `0x31a990`/`0x31a998` |
| `+0x4048` (`s0` frame) | Zero (AAF0 `s0`-frame slot; thread-3's frame differs — see sub-row) | AAF0 @ `0x31ac98` (`0xae004048`) | AAF0 @ `0x31ac80` |
| `+0x14040`/`+0x14044`/`+0x14048`/`+0x14290` (via `s3`=`s0`+`0x10000`) | Thread id A alias / sema id C (= 28, valid) / **completion flag** / INTC-handler id | F2: #3 store @ `0x31a7e0` (`0xae624044`, delay), flag init 0 @ `0x31a7cc` (`0xae604048`), handler id @ `0x31a8e4` (`0xae624290`); `0x31acd8` sets flag=`$a1` @ `0x31ace8` | F4/F5 flag guards; predicate `0x31ad00` flag test; `0x31acd8` id-28 signal; thread-3 (`s0`=obj+`0x10000`) waits id-28, clears flag |

### c. Every writer to the `+0x18` slot

| # | Writer | Evidence |
|---|---|---|
| 1 | F2 CreateSema#2 store @ `0x31a7b8` (`sw $v0,0x18($s0)`, delay of the `memset` jal @ `0x31a7b4`) | Sole `+0x18` store in `$O/sub_0031A6B8` (census of all `s0`/`a0`-relative `0x18` accesses) AND in `$O/sub_0031AAF0` (same-object methods: only READS @ `0x31ab1c`/`0x31ac2c`/etc., zero `+0x18`/`+0x0C` stores) |
| 2 | DeleteSema clears | NONE: F3 reads the slot for DeleteSema @ `0x31a9b0` but stores nothing back (no `sw *,0x18` in F3's range) |
| 3 | `-1` sentinels | NONE: no `addiu *,−1`/`0xFFFFFFFF` store to the slot in either method file (sole `-1` constant in-file is the thread-priority `addiu` @ `0x31a87c`, unrelated) |
| 4 | Init memsets | NONE touch the slot: F2 memsets only STACK sema params (`sp`+`0x30`/`0x50`/`0x70`, `0x18` bytes each) and thread params; object fields are stored individually |
| 5 | Tree-wide cross-check (rare-offset family) | `sw` to `+0x4034`/`+0x4044`/`+0x4030`/`+0x4040`/`+0x4290`: ONLY F2's five stores tree-wide (each ×2 = delay-slot dual print); other-width stores to those offsets are all `($sp)`-relative frames (`0x3378c8`/`0x38fef8`/…), never object stores — so F2's stores are the sole instance writers, and the valid id-29 in `+0x4034` proves F2 RAN (straight-line ⇒ the `+0x18` store executed too) |

F2 is branch-free (`0x31a6d8`–`0x31a914`: zero branch mnemonics; zero
`branch_taken_` predicates) with no `$v0` test between any CreateSema and
its store — all four returns are stored raw and unchecked. `s1` is written
only at `0x31a760`/`0x31a780`/`0x31a7a0` (`sp`+`0x30`/`0x50`/`0x70`); `s5`
only at `0x31a70c` (=`0x400`).

### d. The `-1` source (one row per candidate)

F2's four CreateSema params (`ee_sema_t` = `{count, max_count, init_count,
wait_threads, attr, option}` = `0x18` bytes, `State.h:129-139`; `memset`
HLE verified `LibC.cpp:132-154`: `$a0`=dest, `$a1`&`0xFF`=value,
`$a2`=size, returns dest):

| Call | Param (`s1`) | Post-`memset` field store? | Effective `{init, max, attr, option}` | Host result (`Sched:1103-1125`) |
|---|---|---|---|---|
| #1 @ `0x31a778` (`ra`=`0x31a780`) → `+0x0C` | `sp`+`0x30`, `memset`(_,0,`0x18`) @ `0x31a770` | NONE (adjacent jals; delays only move `$a0`) | {0, 0, 0, 0} | `maxCount`≤0 → `KE_ERROR` = **-1** (`Sched:32,1106-1109`) |
| #2 @ `0x31a798` (`ra`=`0x31a7a0`) → **`+0x18`** | `sp`+`0x50`, `memset` @ `0x31a790` | NONE (same; delay stores #1's `$v0` to the OBJECT, not the param) | {0, 0, 0, 0} | **-1** (same rule) |
| #3 @ `0x31a7c0` (`ra`=`0x31a7c8`) → `+0x14044` | `sp`+`0x70`, `memset` @ `0x31a7b4` | YES: `sw s5,0x74(sp)` @ `0x31a7bc` = param+4 = `max_count`=`0x400` (offset check row E) | {0, 1024, 0, 0} | Valid id (**28** observed §P22-2a) |
| #4 @ `0x31a850` (`ra`=`0x31a858`) → `+0x4034` | `sp`+`0x70` reused, `memset` @ `0x31a844` | YES: `sw s5,0x74(sp)` @ `0x31a84c` = `max_count`=`0x400` | {0, 1024, 0, 0} | Valid id (**29** observed) |

| Candidate (brief's list) | Standing |
|---|---|
| CreateSema failure return propagated | **Confirmed**: #2's all-zero param deterministically fails the host check; the `−1` is stored unchecked by the slot's sole writer. Boot receipt: exactly the 2 all-zero creates fail game-wide (33 creates, §P22-2a) |
| Init path never ran | **Excluded**: F2 ran — `+0x4034` holds working id 29 whose sole tree-wide writer is F2's #4 store (§P22-1c row 5); F2 straight-line ⇒ #2's store executed. (Direct caller unresolvable statically — zero JALs, table dispatch — but execution is proven by the artifact.) |
| Delete-then-reuse | **Excluded**: F3 never ran this boot (0 DeleteSema lines for `+0x18`/`+0x0C`/`+0x4034`/`+0x4044` ras; no teardown marker), and F3 clears nothing anyway |
| Stale object / uninitialized slot | **Excluded**: the slot is deterministically written at init (above), and reads back `-1` constantly (1.39M identical reads P21; 257,125 here, single `s0` §P22-2b) |

Guest bug vs host-side init (brief's Step-1c question), as named by the receipts:

| Reading | Evidence |
|---|---|
| The game expects CreateSema(`max_count`=0) to SUCCEED | Shipped code performs no error check and cannot function if #1/#2 fail (F6's wait + the outer completion loop assume a blocking-capable sema); #3/#4 show the game sets `max_count`=`0x400` where it wants a bound — the #1/#2 zero is the configuration the game ships, so the real kernel must accept it (as unlimited or clamped — beyond repo evidence) |
| The host rejects what the game requires | `createSemaphore` (`Sched:1106-1109`) returns `KE_ERROR` (-1) for `maxCount`≤0; `Sync.cpp:69-87` passes the game's zeros straight through. No other host init is missing (threads, INTC, params all valid — the 29 sibling creates succeed) |
| Net | A host-parity gap on one validation rule, not a guest logic bug: the game is "accidentally correct on hardware" (zero-max accepted there) and deterministically broken here |

### e. The loop's intent (F6 + F4/F5 + PollSema + outer `beql`)

Per-outer-iteration call graph (all `jalr` targets resolved dynamically via
`firstRa`/`lastRa` = call-site+8, `ps2_runtime.cpp:1623-1639`, §P22-2c;
ra checks row B):

| Site | Call | Rate | Role |
|---|---|---|---|
| `jalr` @ `0x316dfc` (`ra`=`0x316e04`, +`0x5C`) | F4 (`0x31a9d8`) | 2×/iter (with F6's `+0x5C` call) | `if (flag) jal 0x31a3c0(obj+0x14080)` |
| `jal` @ `0x316e04` | `0x3E5928`(0) | 1× | Unchanged legacy rung (P21-2g) |
| `jalr` @ `0x316e1c` (`ra`=`0x316e24`, +`0x64`) | F5 (`0x31aa18`) | 2×/iter (with F6's `+0x64` call) | `if (flag) jal 0x31a308(obj+0x14080)` |
| `jalr` @ `0x316e34` (`ra`=`0x316e3c`, +`0x24`) | **F6** (`0x31aa58`) | 1×/iter (sole caller both ways) | The wait (below) |
| `jal` @ `0x316e3c` | `0x317328`→`0x3174a8` | 1× | Trampoline + `jalr`-only fan-out (no direct JALs) |
| `jalr` @ `0x316e54` (`ra`=`0x316e5c`, +`0x54`) | `0x31ad00` predicate | 1×/iter (sole caller both ways) | Returns (`*(obj+0x14048)`<`1`); `beql $v0,$zero` @ `0x316e5c` loops back to `0x316df0` while nonzero-flag (target check row C) |

F6 per call with `-1` in the slot (`s0` = object): flag=1; vcall
(`*(iface+0x5C)` = F4); WaitSema(-1) → `KE_UNKNOWN_SEMID` (-408), NO block
(`Sched:1248-1267`, the P20-1 id-validation read); flag=0; PollSema(-1) →
-408 ≠ -1 → drain loop (`beq` @ `0x31aa9c` → `0x31aa90`) exits after
EXACTLY ONE poll (dynamic 1:1:1 F6:Wait:Poll §P22-2c; with a valid id the
loop drains `count`+1 polls, exiting on `KE_SEMA_ZERO` -419); vcall
(`*(iface+0x64)` = F5); return. Net: with `-1`, a designed BLOCKING wait
degrades to a straight-line no-op, and the outer iteration — which on
hardware parks inside F6 until worker completion — free-spins.

The completion handshake that never completes: once, pre-spin, thread 1
calls `0x31acd8` (flag=`$a1` + the single id-28 signal @ `ra`=`0x31acf4`,
§P22-2b) submitting to thread 3 (`entry`=`0x31ac60`, prio 101, `s0`=obj+`0x10000`,
waits id-28, clears the flag).
Thread 3 NEVER executes (`status`=Ready, `pc`=entry, `sch`=0 all blocks
incl. b0): starved, because the never-blocking thread-1 spin (prio 100)
beats prio 101 at every `selectReady` scan (low-number-first, §P20-1a).
Thread 4 (prio 99) does run (40 F7 calls via `0x3173dc`-`jalr`, §P22-2c)
but its 4 in-window signals hit the `-1` slot (`result`=-408, lost). So
the `-1` breaks completion twice: directly (F6/F7 handshake on a dead id)
and indirectly (busy spin starves the flag-clearer). F2's prio derivation
(`*(s0+0x14)`=100 ±1 → 101/99, check row I) shows the design ASSUMES
thread 1 blocks.

### f. Machine-check paste block (every hand computation in Part 22)

```
python3 -c "…rows A–I…"
→ A: 0xc0c69b6 0xc0c6a48 0xc0c6a76 0xc0c6a86 0xc0c6a96 0xc0c6ab2 0xc0c69ae
→ B: 0x31a780 0x31a7a0 0x31a7c8 0x31a858 0x31aa8c 0x31aae4 0x3173e4 0x316e3c 0x316e24 0x31aab8 0x316e04 0x31aa84 0x316e5c 0x31aa08 0x31aa48 0x31ac30 0x31ab20
→ C: 0x31aa90 0x31aae8 0x31ac20 0x316df0
→ D: 0x31ac60 0x31ac08 0x31a490 0x31abd0 0x14080 0x14044 0x14040 0x14048 0x14290
→ E: 0x20 0x20 0x1fffe30 0x4 1024
→ F: 0x6048a8
→ G: 0x8 0x10 0x18 0x48 0x50
→ H: 1130869 110021428 1130454 5.4 5.39 2857 2.8
→ I: 10130 100 100 10
```

Row A: JAL words for `0x31a6d8/0x31a920/0x31a9d8/0x31aa18/0x31aa58/0x31aac8/
0x31a6b8` (caller sweeps). Row B: 17 `jal`/`jalr`→`ra` (+8) checks in the
order cited (4 CreateSema sites, F6/F7, F7-caller, 6 outer/virtual
callers, F4/F5 inner jals, worker wait, `0x31ab10` signal). Row C: 4 branch
targets (PollSema loop-back, F7 skip, worker loop-back, outer loop-back).
Row D: thread entries (`0x320000`−`0x53A0`/`0x53F8`), INTC handler/arg
(`0x320000`−`0x5B70`/`0x5430`), sub-object + `s3`-relative offsets. Row E:
CreateSema param spacing (`sp`=`0x1fffe30`), `max_count` field offset (4),
`0x400`=1024. Row F: slot absolute addr (`s0`+`0x18`). Row G: method-table
entry offsets from `0x48db7c`. Row H: LOG1−LOG line/byte deltas, wait
delta, `-1`-wait ratio (5.4×), id-29 ratio (5.39×), `-1`/s (2857),
id-29/block (2.8). Row I: stub-tail gap (10130), prio back-derivation
(100/100), F7 signal hit rate (10%).

### g. ELF verification words (46 addrs, 0 mismatches; mapping file-off = va−`0x100000`+`0x1000`)

```
0x31a6d8 0x27bdfeb0 / 0x31a6e0 0x80802d / 0x31a70c 0x24150400 / 0x31a720 0xae000020
0x31a744 0xae020010 / 0x31a76c 0xae030014 / 0x31a778 0xc108f68 / 0x31a794 0xae02000c
0x31a798 0xc108f68 / 0x31a7a4 0xae00001c / 0x31a7b8 0xae020018 / 0x31a7bc 0xafb50074
0x31a7c0 0xc108f68 / 0x31a7cc 0xae604048 / 0x31a7e0 0xae624044 / 0x31a7f8 0x2442ac60
0x31a824 0xae624040 / 0x31a834 0xaf820ddc / 0x31a838 0xae004038 / 0x31a84c 0xafb50074
0x31a850 0xc108f68 / 0x31a868 0xae024034 / 0x31a880 0x2442ac08 / 0x31a8e4 0xae624290
0x31a9a4 0x8e244034 / 0x31a9ac 0x8e044044 / 0x31a9b4 0x8e240018 / 0x31a9bc 0x8e24000c
0x31aa6c 0xae02001c / 0x31aa70 0x8e030008 / 0x31aa84 0xc108f78 / 0x31aa88 0x8e040018
0x31aa8c 0xae00001c / 0x31aa90 0xc108f7c / 0x31aa94 0x8e040018 / 0x31aa98 0x8e030018
0x31aa9c 0x1043fffc / 0x31aad0 0x8c82001c / 0x31aadc 0xc108f70 / 0x31aae0 0x8c840018
0x31ab1c 0x8c84000c / 0x31ab48 0xae024038 / 0x31ac2c 0x8e044034 / 0x31ac30 0x8e030020
0x31ac98 0xae004048 / 0x316e5c 0x5040ffe4
```

(Method-table words `0x48db60`–`0x48dc0c` were dumped from the ELF directly
§P22-1a; no separate verification needed.)

## P22-2. Dynamic answer (boot-p1u-1, 1 boot)

LOG 258,784 lines, 28,980,295 B, 16 blocks, CWD `$W/P1/run`, env = p1t-boot1
+ `PS2X_DIAG_SEMA_CREATE=1` + `PS2X_DIAG_SEMA_S0=1` (script diff = docstring
+ LOG + those 2 vars only), WATCH `0x519c40,0x450de4`, foreground 90 s,
SIGTERM rc=-15. Binary `559521a6` (§P22-3). New-line formats:
`[diag:sema-create] tid pc ra param count max init wait attr option ret`
(`Sync.cpp` emit, `pc`=`0x423da8` = post-syscall trampoline pc on all 33
lines); unknown-id waits gain a trailing `s0=0x…` iff `PS2X_DIAG_SEMA_S0`
is set (else byte-identical to P1s).

### a. CreateSema census: F2 ran; exactly its 2 zero-param calls fail (2 of 33)

| Line(s) | `ra` (site) | `{count,max,init,wait,attr,option}` | `ret` |
|---|---|---|---|
| F2 #1 + #2 | `0x31a780` / `0x31a7a0` | {0,**0**,0,0,0,0} / same | **-1** / **-1** |
| F2 #3 + #4 | `0x31a7c8` / `0x31a858` | {0,**1024**,0,0,0,0} / same | **28** / **29** |
| 2 | `0x42c0fc`/`0x42c10c` | max=1,init=1 | 1 / 2 |
| 3 | `0x3e56c4` (×3) | max=1,init=1 | 3 / 4 / 5 |
| 20 | `0x3e35dc` (one-shot drainer ×20) | max=1,init=0 | 6–25 |
| 1 | `0x3e43c4` | max=32,init=0 | 26 |
| 1 | `0x3e56c4` | max=1,init=1 | 27 |
| 2 | `0x375d74`/`0x375d88` | max=16,init=0 / max=1,init=1 | 30 / 31 |

Verbatim F2 lines (all `tid`=1, `pc`=`0x423da8`):

```
[diag:sema-create] tid=1 pc=0x423da8 ra=0x31a780 param=0x1fffe60 count=0 max=0 init=0 wait=0 attr=0 option=0 ret=-1
[diag:sema-create] tid=1 pc=0x423da8 ra=0x31a7a0 param=0x1fffe80 count=0 max=0 init=0 wait=0 attr=0 option=0 ret=-1
[diag:sema-create] tid=1 pc=0x423da8 ra=0x31a7c8 param=0x1fffea0 count=0 max=1024 init=0 wait=0 attr=0 option=0 ret=28
[diag:sema-create] tid=1 pc=0x423da8 ra=0x31a858 param=0x1fffea0 count=0 max=1024 init=0 wait=0 attr=0 option=0 ret=29
```

Params confirm the static layout: `sp`=`0x1fffe30`, #1=`sp`+`0x30`,
#2=`sp`+`0x50`, #3=#4=`sp`+`0x70` (spacing check row E). F2's are the
ONLY `max`=0 params game-wide; all 31 other creates pass `max`≥1 and
succeed. `ret` sequence 1–31 with exactly the 2 F2 holes as -1.

### b. The slot, first wait, and epoch position

| Receipt | Value |
|---|---|
| `s0` on `-1` waits | **Single value `0x604890` on all 257,125 waits** → one singleton instance; slot absolute addr **`0x6048a8`** (check row F) |
| `-1` waits / signals | 257,125 waits (`ra`=`0x31aa8c`, `waker`=1, `result`=-408) / 4 signals (`ra`=`0x31aae4`, `waker`=4, `result`=-408) |
| First `-1` wait | :630 (P21 :597; +33 = the 33 new create lines shifting the log) |
| Epoch order (:605–:630) | :605/:606 `0x519c40`=`0x0`→`0xA` → :607 first signal 26→thread 2 → :608 wake `0x2` → :609/:610 cdread+`BIGF` payload (same bytes) → :611 queued → :612 issuer `0x2` → :613 start → :614 callback signal (`ra`=`0x3e3af0`, fix still firing) → :615 worker consume → :616 #9 store → :617/:618 worker id-5 pair → :619 worker re-park → :620–:625 thread-1 id-5 pairs → :626 driver probe (same bytes) → :627/:628 id-5 pair → :629 id-28 signal (`ra`=`0x31acf4`, the `0x31acd8` once-call) → :630 spin begins |
| Same-vs-shared instance | SHARED singleton: every F6 execution is thread 1 (all `-1` waits `waker`=1, and F6 unconditionally executes the wait), so the `+0x1C`=1 that thread 4's F7 observed 4× was set by thread 1's F6 — plus the single dynamic `s0` |
| `+0x0C` sibling (`ra`=`0x31ab20` signals) | 0 (method `0x31ab10` never ran; the slot is write-once, delete-never-this-boot) |
| id-26 record | 5 lines (first park, first signal, callback signal, consume, re-park — same shapes as P21-2b) |
| Watch lines | `0x519c40` ×7 (:49 width-16 zero-init, :83 width-8, :605/:606/:608/:612/:616) + neighbor `0x519c44` ×1 (:226) = 8 total, same kinds as LOG1; `0x450de4` 0 writes |

### c. Virtual-target resolutions + ratios (the `firstRa`/`lastRa` receipts)

| Target | Count(total) | `firstRa` / `lastRa` | Resolves to |
|---|---|---|---|
| F6 `0x31aa58` | 246,995 | `0x316e3c` / same, all blocks | Sole caller: outer `jalr` @ `0x316e34` (+`0x24` slot) |
| F4 `0x31a9d8` | 2×/iter (b0 22,880) | `0x316e04` / `0x31aa84` | Two callers: outer `jalr` @ `0x316dfc` (+`0x5C`) + F6's vcall @ `0x31aa7c` (sole `lastRa`=`0x31aa84` target, 13 blocks) |
| F5 `0x31aa18` | 2×/iter (b0 22,879) | `0x316e24`+`0x31aab8` across blocks | Two callers: outer `jalr` @ `0x316e1c` (+`0x64`) + F6's vcall @ `0x31aab0` |
| `0x31ad00` predicate | 246,996 | `0x316e5c` / same, all blocks | Sole caller: outer `jalr` @ `0x316e54` (+`0x54` slot) |
| F7 `0x31aac8` | 40 (all 16 blocks) | `0x3173e4` / same, all blocks | Sole caller: `jalr` @ `0x3173dc` in `0x317348` (+`0x2C` slot); thread-4 path `0x31ac20`→`0x317500`→`0x317348`→F7 |
| PollSema `0x423df0` | = F6 b0 (11,440) | `0x31aa98` | Exactly 1 poll per F6 (drain exits first try) |

F6:Wait:Poll = 1:1:1 per iteration (b0 11,440/11,547/11,440 — the +107
WaitSema are non-F6 waits, `firstRa`=`0x418ce0`). F7 40 calls → 4 signals
(10% hit the `+0x1C` race window, check row I). Stub-total vs sema-line
gap (F6 246,995 vs waits 257,125 = 10,130) = the unflushed tail after the
last period flush (SIGTERM kills before flush; sema lines are per-call and
complete) — a method note, not a path difference.

### d. Ladder delta vs LOG1 (boot-p1t-1: 1,389,653 lines, 139,001,723 B, 17 blocks)

LOG: 258,784 lines (−1,130,869), 28,980,295 B (−110,021,428), 16 blocks.
Rate uniformly ~5.4× lower (`-1` waits 1,387,579→257,125; id-29 237→44
signals / 238→45 waits; thread-1 sch steady 12–15→2–3 with b0 36→27):
independent paths (thread-1 spin AND INTC-driven id-29) scale together ⇒
host-speed effect (shared-host contention), not a guest-path change.

| Rung | LOG1 | LOG | Delta |
|---|---|---|---|
| Thread-1 pc | `0x3e5980` ×8, `0x31a278` ×4, 4 others ×1 | `0x3e5980` ×9, `0x31a278` ×3, `0x317328` ×2, `0x316df0` ×1 | Same cycle (loop-top `0x316df0` sampled once) |
| Thread-1 sch | 36/15/14/13/14/13/12/14/14/14/14/14/12/15/14/14/14 | 27/3/3/3/3/3/2/3/3/2/3/2/3/2/3/3 | Rate only (16 blocks: one fewer period elapsed) |
| Thread-2 | parked 26 @ `0x423de8`, sch 2 then 0 ×16 | Same bytes | None |
| Thread-3 | Ready @ `0x31ac60`, sch 0 | Same + prio 101 (derivation §P22-1e) | None (+prio recorded) |
| Thread-4 | parked 29 @ `0x423de8` (sch 12 b0) | Same ids/pcs/entries, prio 99 (sch 3 b0) | Count regime only |
| Thread-5 | parked 30 (sch 1 b0) | Same (sch 1 b0; 1 wait `ra`=`0x3827e0`) | None |
| Missing / `No exact` | 0 / 0 | 0 / 0 | None |
| `firstRa` old loop | 0 / 0 | 0 / 0 | None |
| `0x3e5440` | Unhit | 0 hits | None |
| CD callback / read | :578/:580, :576 same bytes | :611/:613, :609/:610 same bytes | Line shift only |
| CD reads total | 21 | 21 | None |
| Probe | 1 (same bytes) | 1 (:626, same bytes) | Line number only |
| Watch | 8 lines | 8 lines (same kinds) | None |
| `run:tick` | 7 (`pc`=`0x316e3c`) | 9 (`pc`=`0x316e04`/`0x316e0c`, `gp`=`0x4a30f0`, `dma`=7, 5 threads) | Timing regime |
| GIF/GS | 2/66/122/33/8/1 | Same sweep values (gif/kick/reg/prim/copy-reg/texa as LOG1) | None |
| Presented frame | None (TIMER line only) | None (:46 TIMER line only) | None |
| Crash / FATAL | 0 / 0 | 0 / 0 | None |
| Dormant / start-thread | 40 / 4 | 40 / 4 | None |
| SIF modules | 6 | 6 | None |

## P22-3. Binaries and commits

| Binary / ref | sha256 / sha | Sources / state |
|---|---|---|
| `/tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner` (boot 1) | `559521a6280cbd623b43222ee6bf74aef8549ab814452ba07335c53479cce404` | `de7ff17` tree (P1u `Diag:` on `58c9144`; `-j4` rebuild, exit 0) |
| `ps2x_tests` (CWD `$R`, rebuilt) | Total 425, Passed 424, Failed 1 (`sceGsSyncVCallback … reserved async stack pool`, same test+assertion as P21) | No new failure from the `Diag:` change (pure emit additions); pre-existing, unrelated, not fixed |
| `PS2Recomp` branch `ssx3` HEAD | `de7ff17` (`Diag: P1u CreateSema param/return census + s0 capture on unknown-id waits (P22-2)`, 2 files, +51/-7, two trailers) | Sole P1u fork commit; worktree sole `M` = pre-existing generated `runner/register_functions.cpp`, never added |
| Fork push | `git push fork ssx3` from fork clone only (§P22-4; pull-`--rebase` + retry-once rule armed for the shared tree) | The only push allowed (no push in ssx3) |
| This report | `[P1u]` commit (two trailers; local only) | Sole ssx3-repo change; no `runner/`, log, or `._*` added |

`Diag:` diff shape: `Sync.cpp`: `diagSemaCreateEnabled()` (`PS2X_DIAG_SEMA_CREATE`,
cached static, default off) + `[diag:sema-create]` emit on both `CreateSema`
return paths (tid/pc/ra, param addr + all 6 `ee_sema_t` fields, `ret`;
`noparam` variant for the null path). `Sched`: `diagSemaS0Enabled()`
(`PS2X_DIAG_SEMA_S0`, cached static, default off) + trailing `s0=0x…`
(reg 16) on the unknown-id wait emit only. Zero behavior change when unset
(cached bool checks; wait lines byte-identical to P1s without the new var).

## P22-4. Exact commands

From `$R` (fork) unless noted; `$W=/Volumes/Extreme SSD/ps2recomp-spike`,
`$O=$W/P1/output`, `LOG=$W/P1/run/boot-p1u-1.log`:

```
# Step 1 (lease-free static)
re-read REPORT Part 21 + Part 20 P20-1 (paged reads)
read $O/sub_0031A6B8 (F1/F2/F3/F4/F5/F6/F7 windows) + trampolines 0x423DA0-0x423DF0
  + 12 surrounding trampolines ($v1 map) + Dispatcher names + Sync.cpp + State.h ee_sema_t
  + Sched create/delete/signal/poll/wait (1095-1290) + KE codes (28-50)
  + LibC memset (132-154) + Interrupt addHandler (26-40)
read $O/sub_0031AAF0 (0x31ab10/0x31ab30/0x31abc0/0x31abc8/0x31abd0/threads/0x31acd8/0x31ad00)
  + sub_00316D60 (loop 0x316df0-0x316e64) + sub_00317328 (all) + sub_0031A268 (all)
  + sub_00317500 (all) + sub_00317348 (jalr ctx) + sub_0031A3C0 (0x31a490 head)
  + sub_00424880/0x4248E8 (calls) + ps2_runtime.cpp stub-hist emit (1623-1639)
ELF sweeps (python3 struct): 6 JAL words (0 hits each) + J-opcode (0) + raw words
  (1 hit each @ 0x48db7c cluster) + table dump 0x48db60-0x48dc0c + lui-0x48 census
censuses: F2 branches (0) + $v0 checks (0) + s1/s5 dests; sw-to-rare-offsets tree-wide
  (F2's 5 only) + other-width stores (sp-frames only); AAF0 slot accesses
python3 hex checks (rows A-I §P22-1f); ELF batch 46 words (0 mismatches §P22-1g)
P6 grep (no rows for 0x31a6b8 region; 0x31adb0/0x31af80 only nearby)
# Step 2 (Diag commit + build + tests, no lease needed)
(edit_file: Sync.cpp helper + CreateSema emits; Sched helper + s0 field)
find ps2xRuntime/src/lib/Kernel -name '._*' -delete (repo-wide before build)
cmake --build /tmp/p1-link/runtime --target ps2EntryRunner -j4 (exit 0)
cmake --build /tmp/p1-link/runtime --target ps2x_tests -j4 (exit 0)
ps2x_tests CWD $R (425/424/1 GsSyncV, same as P21; named via [Failed] grep)
shasum -a 256 ps2EntryRunner (559521a6)
git add <2 NAMED lib files>; git commit -m "Diag: ..." (two trailers) -> de7ff17
(write /tmp/p1u-boot1.py; diff vs p1t-boot1.py = docstring + LOG + 2 env vars)
# Step 2 (lease protocol + boot 1)
cat /tmp/ssx3-host-lease (absent 20:01:01Z; M13 never seen; no polls)
pgrep -x ps2EntryRunner (exit 1); shasum fresh; git log (de7ff17); ls ISO + ELF
printf 'P1u\n' > /tmp/ssx3-host-lease (20:01:10Z, absent verified twice) + >> p1u-waits.log
python3 /tmp/p1u-boot1.py (CWD $W/P1/run, 90 s, SIGTERM rc=-15, 28980295 B)
# Step 2 (log analysis, lease-free; lease still held)
sema-create census (33; F2 4 verbatim; 2 ret=-1); -1 waits (257125, s0 singleton)
  + signals (4) + first-wait :630; epoch order :605-:630; id-26 5-line record
signal group-by (ra): 4x-1 / 44x29 / 1x28 / 20x(6-25) / 2x26 / 79x(4/5) / 2x1
wait group-by (ra): 257125x-1 / 45x29 / 79xpump / 20xdrainer / 3x26 / 2x1 / 1x30-park
virtual resolutions via firstRa/lastRa (F6/F4/F5/predicate/F7); F7 total 40
per-block thread table (16x5); watch/probe/cd sweeps; ladder delta vs LOG1
GIF/GS sweep (2/66/122/33/8/1 exact); python3 checks rows F/H/I
# Step 3
(edit_file append Part 22 in 4 chunks + 1 typo fix; commit below)
git -C /Users/bradrichardson/dev/ssx3 add -f local/research/P1/REPORT.md
git -C /Users/bradrichardson/dev/ssx3 commit -m "[P1u] ..." (two trailers; NO push there)
git -C $R push fork ssx3 (the only push allowed; rebase-retry rule on reject)
rm -f /tmp/ssx3-host-lease; ls (absent); pgrep -x (exit 1)
```

Env delta boot 1 vs boot-p1t-1: `PS2X_DIAG_SEMA_CREATE=1` +
`PS2X_DIAG_SEMA_S0=1` only. Source delta: `Sync.cpp` + `EeScheduler.cpp`
(+51/-7 diag emits).

## P22-5. What I could not do

- Watch the slot's absolute addr (`0x6048a8`) across a boot: the addr was
  learned FROM boot 1 (s0 capture), so watching it needs boot 2 — unused
  because boot 1 closed the attribution (F2 ran + #2→-1 + sole writer +
  singleton s0). A watch would re-confirm the `0x31a7b8` store pc only.
- Name `0x31acd8`'s once-caller (below the stub-histogram top-30 cutoff at
  count 1) and the `+0x08` iface-pointer writer (outside both method files;
  set by the table-external instantiation path, whose vptr/table-plumbing
  was not chased).
- Read `0x31a308`/`0x31a3c0` bodies (F4/F5 sub-methods), `0x320b08` (table
  +`0x20`), and thread 3's full consume/clear sequence past its `s0` base —
  the flag-clearer role is inferred from slot accesses + starvation, with
  that boundary stated.
- Close P20-5's INTC residue fully: cause-3 handler = `0x31a490`
  (FPU-saving prologue, registered by F2) but its link to the id-29
  `iSignalSema` @ `0x31abf0` (no direct JAL; likely `jalr`) was not traced.
- Run the reserve 2nd boot (not needed); no A/B on any rung. The ~5.4× rate
  delta vs LOG1 is attributed to shared-host contention (uniform across
  independent paths), not measured against isolated hardware.

---

## Part 23 (P1v): FIX — zero-max CreateSema accepted as binary sema; WaitSema(-1) spin gone, thread 3 runs, old outer loop exits; new stall is thread-3's poll on the unwritten word 0x52BE04

Brief `local/muse/prompts/P1v.md`. The second behavior fix, 1 `Fix:`
commit (2 files, +46/-2, of which 38 test) + 2 boots. Tables, no
verdicts. Stale-reading guard: Part 22 re-read before acting (P22-1a the
F-table + F2 ctor shape, P22-1b/1c the `+0x18` slot + sole writer @
`0x31a7b8`, P22-1d the F2 zero-param #1/#2 → -1 table, P22-1e the
handshake + starvation chain, P22-2a the 33-create census, P22-2b the
`s0`=`0x604890` singleton + epoch order). `W=/Volumes/Extreme
SSD/ps2recomp-spike`, `R=$W/PS2Recomp` (fork, branch `ssx3`),
`O=$W/P1/output`, `LOG=$W/P1/run/boot-p1v-1.log`,
`LOG2=$W/P1/run/boot-p1v-2.log`. File:line refs below are
`ps2xRuntime/src/lib/` unless noted. Every hand hex machine-checked
§P23-1h; all cited MIPS words ELF-verified §P23-1i.

## P23-0. Lease record

| Event | Value |
|---|---|
| Lease at session start | M14 (another agent; briefed share — poll every 5 min, never force) |
| Waits log | `$W/P1/run/p1v-waits.log` (4 lines: start, poll 1, claim, release) |
| Poll 1 (23:35:05Z) | M14 still holds, `pgrep -x ps2EntryRunner` absent; logged, continued wait |
| Poll 2 (23:40:16Z) | Lease absent, runner absent |
| Pre-claim checks (23:41:01Z) | Absent verified twice; `pgrep -x` exit 1; binary `52f766a5` (P1v Fix build); fork HEAD `8d10619`; ISO 3005415424 B + ELF 3890784 B present |
| Claim | `printf 'P1v\n' > /tmp/ssx3-host-lease` 23:41:01Z, immediately before boot 1 |
| Boot 1 | 90 s foreground, SIGTERM rc=-15, LOG 7,852 lines, 1,053,739 B, 17 blocks |
| Boot 2 | 90 s foreground, SIGTERM rc=-15, LOG2 7,915 lines, 1,063,718 B (WATCH swap only) |
| Release | After Step 3 push (below); verified absent; `pgrep -x` exit 1 |
| `adb` | Not used |

## P23-1. Evidence + fix + choice + tests

Conventions: `Sched` = `Kernel/EeScheduler.cpp`; `Sync.cpp` =
`Kernel/Syscalls/Sync.cpp`; `macros.h` = `ps2xRuntime/include/ps2_runtime_macros.h`.

### a. Step-0: what a real PS2 does with max_count=0 (reference clones read-only)

| # | Source | Finding |
|---|---|---|
| 1 | `pcsx2-ref/pcsx2/R5900OpcodeImpl.cpp:107` | `CreateSema` appears ONLY in the EE syscall-name table (`//0x40` row); no kernel HLE, no validation — PCSX2 boots the Sony BIOS (LLE), silent on max=0 |
| 2 | `pcsx2-ref/pcsx2/IopBios.cpp` | Zero `Sema` matches (grep over the file): IOP HLE covers modules, not semaphores — silent |
| 3 | `pcsx2-ref/pcsx2/ps2/BiosTools.cpp` (388 lines) | IRX loading only — silent |
| 4 | `dobiestation-q4/src/core/ee/emotion.cpp:68` | `CreateSema` again ONLY a syscall-name-table row (`//0x40`); LLE, silent on max=0 |
| 5 | ps2tek EE_Syscalls `40h` | "Creates a semaphore. Returns the semaphore's id if successful and `-1` if not. Only `s->init_count` and `s->max_count` need to be specified." — return convention only, silent on max=0 validity |
| 6 | ps2tek EE_Threading (`SemaParam`/`sema` structs + scheduler) | Internal layout (`count`/`max_count`/`attr`/`option`/`wait_threads`) + wait/signal behavior; no create-time validation documented — silent |
| 7 | ps2sdk `ee/kernel/include/kernel.h` (`t_ee_sema`, `s32 CreateSema(ee_sema_t *)`) | Struct + syscall-stub prototype only; validation lives in the Sony BIOS — silent |
| 8 | Host rule provenance | `git log -L` → upstream `f4309cd` ("refactor: from guest threads to EE scheduler (#184)"); the `maxCount<=0 → KE_ERROR` check arrived with the refactor, no hardware citation |
| 9 | Game-as-oracle (decisive) | SSX 3 is a shipped title that runs on real PS2s; F2's ctor runs at boot (id-29 artifact, P22-1c row 5) and stores two unchecked all-zero creates; on hardware the boot proceeds past F6's blocking wait — so the real BIOS returns a usable id for max_count=0 |

Net per the brief's ground rule: written sources are silent or LLE (rows
1–7 say so explicitly), the host rule is uncited (row 8), and the
artifact itself (row 9) proves acceptance. Stored-max semantics (clamped
vs stored-0) are NOT pinned by any source → the fix below is recorded as
PROVISIONAL.

### b. The fix (one `Fix:` commit, `8d10619`; non-test diff 8+/2−)

Single choke point `EeScheduler::createSemaphore` (`Sched:1115`);
`Sync.cpp:84` `CreateSema` stays a pure pass-through (`ee_sema_t` =
`Syscalls/Helpers/State.h:129-137`). `KE_ERROR`/`KE_UNKNOWN_SEMID`/
`KE_SEMA_ZERO` = `Sched:32/36/43` (-1/-408/-419).

```diff
 int EeScheduler::createSemaphore(int initCount, int maxCount, uint32_t attr, uint32_t option)
 {
     assertExecutor();
-    if (maxCount <= 0 || initCount < 0 || initCount > maxCount)
+    // P1v: real PS2 hardware accepts max_count=0 (SSX 3 ships two unchecked
+    // all-zero creates at boot and runs on hardware), so treat an exact zero
+    // max as a binary semaphore. Provisional: reference emulators are LLE
+    // and ps2tek/ps2sdk are silent on the stored-max semantics; a negative
+    // max stays rejected and init is validated against the effective max.
+    const int effectiveMax = (maxCount == 0) ? 1 : maxCount;
+    if (effectiveMax <= 0 || initCount < 0 || initCount > effectiveMax)
     {
         return KE_ERROR;
     }
@@
-    semaphore.maxCount = maxCount;
+    semaphore.maxCount = effectiveMax;
```

Choice: exact-zero → binary sema (max stored as 1). Alternatives rejected:

| Alt | Rule | Rejected because |
|---|---|---|
| A | Bypass validation, store max=0 as-is | Waiter-less signals then always hit `count==maxCount → KE_SEMA_OVF` (signal path, `Sched:1214` pre-fix numbering) and are LOST; the F6/F7 handshake has a flag-set-but-not-yet-waiting race window, so this risks wedging iterations on a lost signal |
| B | Clamp ALL max≤0 → 1 | No evidence for negative max; blast radius larger than the game's exact-0 case |
| C | Unlimited max (INT_MAX) | Changes OVF semantics broadly with zero evidence |
| D | Fix in `Sync.cpp` instead | Scheduler is the single choke point; syscall layer stays a pure pass-through |

Why clamp-1 satisfies the game's pattern: F6 WaitSema blocks at count 0
(real block → thread 1 yields → thread 3 can run); F7 SignalSema with a
waiter wakes it (waiters-first branch, no max check); waiter-less signals
store count 0→1 instead of being lost; the PollSema drain behaves as a
normal binary sema.

### c. BEFORE/AFTER receipts (same new test, unfixed vs fixed tree)

New test `PS2RuntimeKernel / CreateSema with zero max_count returns a
usable binary semaphore (P1v)` (`ps2xTest/src/ps2_runtime_kernel_tests.cpp`,
+38, through the real `CreateSema` syscall with an all-zero `EeSemaStatus`):

| Receipt | Unfixed tree | Fixed tree (`8d10619`) |
|---|---|---|
| Zero-max create returns | `KE_ERROR` (-1), no object (test FAILS: "must return a usable id", "must create an object") | id > 0, object exists, `maxCount`=1, `count`=0 (test PASSES) |
| Valid create (max=7, init=3) | Unchanged (same assertions pass both runs) | id > 0, `maxCount`=7, `count`=3 |
| Negative max (-2) | Rejected (`KE_ERROR`) | Rejected (`KE_ERROR`) |
| Full suite | 426 total / 424 pass / 2 fail (new test + known GsSyncV) | 426 total / 425 pass / 1 fail |
| Sole remaining failure | — | `sceGsSyncVCallback ... reserved async stack pool` (same test+assertion as the P21/P22 baseline; pre-existing, unrelated) |
| Baseline before the new test | 425 / 424 / 1 (same GsSyncV) — confirms no test-harness drift | — |
| Rebuild | `ps2x_tests` exit 0 | `ps2x_tests` exit 0 + `ps2EntryRunner` exit 0 |

### h. Machine-check paste block (every hand computation in Part 23)

```
python3 -c "…rows A–G…"
→ A-mbox-base: 0x52be00 0x52be04
→ B-beqz-tgt: 0x40b1d0
→ C2-index-shl2: 0x425cf0 0x4261b0 0x3e5928
→ D-ra: 0x40b1d8 0x316f50 0x316f70
→ E-base2: 0x52bcd8
→ F-316f-br: 0x316fac 0x316f94 0x317140 0x3171c8
→ G-logdelta: 250932 27926556 796.1 27.5
```

Row A: mailbox base (`0x530000`−`0x4200`) + polled word (`+1<<2`).
Row B: `beqz` @ `0x40b1d8` loop-back target. Row C2: analyzer JAL
convention (target = index<<2, NOT OR'd with the region nibble — the
textbook OR would give `0x40425cf0`; the log/recomp/ELF all speak
index<<2, verified on 3 samples: `0x10973c`→`0x425cf0`,
`0x10986c`→`0x4261b0`, `0x0f964a`→`0x3e5928`). Row D: 3 `jal`/`jalr`→`ra`
(+8) checks. Row E: setter-file base-2 getter (`0x530000`−`0x4328`).
Row F: 4 `sub_316F00` branch targets (`beq`/`beqz`/`beql`/`b`). Row G:
LOG-vs-P22 line/byte deltas, `-1`-wait→29-wait ratio (796.1×), byte
ratio (27.5×).

### i. ELF verification words (12 addrs, 0 mismatches; mapping file-off = va−`0x100000`+`0x1000`)

```
0x40b1d0 0xc10973c / 0x40b1d4 0x24040001 / 0x40b1d8 0x1040fffd
0x425cf0 0x3c020053 / 0x425cf4 0x42080 / 0x425cf8 0x2442be00
0x425cfc 0x822021 / 0x425d04 0x8c820000
0x316f48 0x60f809 / 0x316f50 0xc0f964a / 0x316f68 0x60f809 / 0x316f70 0x8e030058
```

## P23-2. Dynamic answer (boot-p1v-1 + boot-p1v-2, 2 boots)

LOG 7,852 lines, 1,053,739 B, 17 blocks, CWD `$W/P1/run`, env = p1u-boot1
unchanged (`PS2X_DIAG_SEMA` + `SEMA_CREATE` + `SEMA_S0` already on;
script diff = docstring + LOG only), WATCH `0x519c40,0x450de4`,
foreground 90 s, SIGTERM rc=-15. LOG2 7,915 lines, 1,063,718 B, same env
except WATCH `0x52BE04,0x450de4` (script diff = docstring + LOG + the one
watch addr). Binary `52f766a5` (§P23-3) both boots.

### a. CreateSema census: all 33 succeed, F2's zero-param pair returns ids 28/29

| Line(s) | `ra` (site) | `{count,max,init,wait,attr,option}` | `ret` |
|---|---|---|---|
| F2 #1 + #2 | `0x31a780` / `0x31a7a0` | {0,**0**,0,0,0,0} / same | **28** / **29** (was -1/-1) |
| F2 #3 + #4 | `0x31a7c8` / `0x31a858` | {0,**1024**,0,0,0,0} / same | **30** / **31** (shifted +2) |
| Rest of game | unchanged sites/pcs | unchanged params | 1–27, 32, 33 contiguous |

Verbatim F2 lines (all `tid`=1, `pc`=`0x423da8`):

```
[diag:sema-create] tid=1 pc=0x423da8 ra=0x31a780 param=0x1fffe60 count=0 max=0 init=0 wait=0 attr=0 option=0 ret=28
[diag:sema-create] tid=1 pc=0x423da8 ra=0x31a7a0 param=0x1fffe80 count=0 max=0 init=0 wait=0 attr=0 option=0 ret=29
[diag:sema-create] tid=1 pc=0x423da8 ra=0x31a7c8 param=0x1fffea0 count=0 max=1024 init=0 wait=0 attr=0 option=0 ret=30
[diag:sema-create] tid=1 pc=0x423da8 ra=0x31a858 param=0x1fffea0 count=0 max=1024 init=0 wait=0 attr=0 option=0 ret=31
```

Id-shift map (this boot vs P22): `+0x0C` 28 (was -1), **`+0x18` 29 (was
-1, THE SLOT)**, `+0x14044` 30 (was 28), `+0x4034` 31 (was 29), thread-5
park 32 (was 30), its mate 33 (was 31). `ret` sequence 1–33 contiguous,
zero failures game-wide. `op=wait id=-1` count: **0** (was 257,125).

### b. Steady-state thread table (all 17 blocks; sch series in full)

Every block: t1 WAIT 29 @ `0x423de8`; t2 WAIT 26 @ `0x423de8`; t3
status=0 (running) pc `0x40b1d0`/`0x425cf0`; t4 WAIT 31 @ `0x423de8`; t5
WAIT 32 @ `0x423de8`.

| Thread | sch b0–b16 | pc pattern |
|---|---|---|
| t1 (prio 100) | 72,36,38,36,36,36,36,38,36,38,36,36,30,38,36,38,36 | `0x423de8` ×17 (parks inside F6 every sample) |
| t2 (prio 12) | 2,0 ×16 | `0x423de8` ×17 (parked 26, same as P22) |
| t3 (prio 101) | 27,36,38,36,36,36,36,38,36,38,36,36,30,38,36,38,36 | `0x40b1d0` ×8 (b0,b1,b5,b6,b9,b10,b12,b14), `0x425cf0` ×9 |
| t4 (prio 99) | 25,18,19,18,18,18,18,19,18,19,18,18,15,19,18,19,18 | `0x423de8` ×17 (parked 31) |
| t5 (prio 5) | 46,36,38,36,36,36,36,38,36,38,36,36,30,38,36,38,36 | `0x423de8` ×17 (parked 32) |

t3/t5 sch = t1 sch from b1 on (b0 differs: warmup). t4 sch = t1 sch / 2
from b1 on (36/18, 38/19, 30/15 exact). Thread 3 scheduled≠0 in ALL 17
blocks (was sch=0 in all 16 P22 blocks). Thread 1's sch≠0 while WAITing
= wake/block cycling (322 F7 wakes §P23-2c).

### c. Signal/wait group-bys (balanced — the system cycles)

| id | signals | waits | Sites (waker, `ra`) |
|---|---|---|---|
| 29 (`+0x18`) | 322 | 323 | waits: 323× t1 `0x31aa8c` (F6); signals: 322× t4 `0x31aae4` (F7, target=1 woken every line) |
| 30 (`+0x14044`) | 2 | 2 | signals: 2× t1 `0x31acf4` (`0x31acd8`, :629/:680); waits: 2× t3 `0x31aca4` (:631 consume, :632 park → :680 woken) |
| 31 (`+0x4034`) | 322 | 323 | waits: 323× t4 `0x31ac30`; signals: 310× t3 + 12× waker=-1, all `ra`=`0x31abf8` (INTC-tail iSignal, `+8` of `0x31abf0`) |
| 32 (t5 park) | 963 | 964 | waits: 964× t5 `0x3827e0`; signals: 321× t1 `0x377b6c` + 321× t5 `0x3826b4` + 311× t3 `0x382640` + 10× waker=-1 |
| 33 | 1284 | 1284 | waits: 963× t5 `0x3827e8` + 321× t1 `0x377b24`; signals: 963× t5 `0x382ae8` + 321× t1 `0x377b64` |
| 4 / 5 (pump) | 67 / 13 | 67 / 13 | unchanged `0x3e5738`/`0x3e57bc` shapes |
| 26 | 2 | 3 | first park + callback signal + consume + re-park (same shapes as P22) |
| 1 | 2 | 2 | — |
| 6–25 (drainer) | 1 each | 1 each | signals carry waker=-1, iSafe=1, invKind=1 (interrupt context) |

`waker=-1` total: 42 lines, all INTC-context iSignals. F6/F7 handshake
alive: 322 wakes of thread 1, `count=0->0 waiters=1->0` every line.
F6's PollSema trampoline (`0x423df0`): 0 printed stub lines (323 total
F6 iters sit below the top-30 cutoff — a display cutoff, not an absence).

### d. Epoch order (:604–:640; same skeleton as P22, new ending)

| Line(s) | Event |
|---|---|
| :604 | id-5 pair (pump) |
| :605/:606 | `0x519c40`=`0x0`→`0xA` (same pcs/values as P22) |
| :607 | first signal 26→thread 2 (`ra`=`0x3e48b8`) |
| :608 | wake `0x2` (watch) |
| :609/:610 | cdread `lbn=0x5f1a3` + `BIGF` payload (same bytes: `42494746147c1a00`) |
| :611 | queued (`func=1 cb=0x3e3ad8`) |
| :612 | watch `0x2` |
| :613 | start (`func=1 cb=0x3e3ad8`, P1t fix still firing) |
| :614 | callback signal (`ra`=`0x3e3af0`, inInt=1) |
| :615 | worker consume (wait 26) + :616 watch `0x0` + :617–:625 id-5 pairs + worker 26 re-park |
| :626 | driver-entry (`sp=0x1fffe80 ra=0x3ded88 sourcePc=0x3ded80 checkpointed=0` — byte-identical in all 3 boots P22/P23-1/P23-2, :626/:626/:620) |
| :629 | id-30 signal (`ra`=`0x31acf4`, the `0x31acd8` submit — 1st of 2 this boot) |
| :630 | **first 29-wait parks thread 1** (`ra`=`0x31aa8c`, `result=park` — the P22 spin-begin line is now a park) |
| :631 | thread 3 consumes 30 (count 1→0, `ra`=`0x31aca4`) |
| :632 | thread 3 parks on 30 |
| :634 | id-31 INTC kick wakes thread 4 (waker=-1, `ra`=`0x31abf8`) |
| :636 | **F7 wakes thread 1** (first of 322; target=1) |
| :637/:638 | threads 4/1 re-park (31/29) |
| :640 | id-31 kick again |
| :680 | 2nd id-30 signal wakes thread 3 (target=3) — thread 3 never waits again |

### e. The new thread-3 park: `while (*(0x52BE04)==0)` (≈2.2M calls/block)

`[diag:stub] target=0x425cf0` all 17 blocks, sole `ra`=`0x40b1d8`:
1,486,763 (b0), then 2,179,378 / 2,251,023 / 2,244,471 / 2,197,159 /
2,168,489 / 2,158,029 / 1,971,444 / 2,239,744 / 2,242,324 / 2,196,821 /
2,165,927 / 2,167,895 / 1,947,855 / 2,243,643 / 2,250,663 / 2,212,551
(≈36.3M total). Caller `0x40b1d0` ∈ `sub_0040B130`
(`0x40b130`–`0x40b1f8`); target = `sub_00425CF0` (`0x425cf0`–`0x425d38`).

Caller loop (`$O/sub_0040B130`, MIPS + recomp agreement; branch check row B):

```
0x40b1d0: jal  0x425cf0        (delay: $a0 = 1)
0x40b1d8: beqz $v0 → 0x40b1d0  (loops while the callee returns 0)
```

Polled function (`$O/sub_00425CF0`, entry only; ELF batch §P23-1i; base check row A):

```
0x425cf0: lui   $v0, 0x53      ($v0 = 0x530000)
0x425cf4: sll   $a0, $a0, 2    (arg 1 → 4)
0x425cf8: addiu $v0, $v0, -0x4200  ($v0 = 0x52BE00)
0x425cfc: addu  $a0, $a0, $v0  ($a0 = 0x52BE04)
0x425d00: jr    $ra            (delay: $v0 = *(u32 *)0x52BE04)
```

Net: thread 3 spins on `*(0x52BE04) != 0`. Same file holds two more
entries: `0x425d08` (setter: `*(base+arg<<2) = $a1`) and `0x425d28`
(returns `0x52BCD8`, check row E) — 0 printed stub lines each (below the
top-30 cutoff if called at all; no JAL sweep run — §P23-5).

### f. The new thread-1 park: WAIT 29 inside F6, outer phase advanced to sub_316F00

Old outer loop (`sub_00316D60`) is GONE: 0 stub lines carry the old ras
(`0x316e04`/`0x316e24`/`0x316e3c`/`0x316e5c`); F6/F7/predicate
(`0x31aa58`/`0x31aac8`/`0x31ad00`) all below the top-30 cutoff. F4/F5
(`0x31a9d8`/`0x31aa18`) run ~48–57/block from NEW outer ras `0x316f50`
/ `0x316f70` (23 lines) ∈ `sub_00316F00` (`0x316f00`–`0x317328`), plus
F6's vcalls (`0x31aa84`/`0x31aab8`); F4/F5 sub-methods `0x31a3c0`/
`0x31a308` ~54/block (sole ras `0x31aa08`/`0x31aa48`); `0x317328`
trampoline ~72/block.

New outer window (`$O/sub_00316F00`; ra checks row D, branch targets row F):

```
0x316f48: jalr $v1 (= F4, iface+0x5C)   ra = 0x316f50
0x316f50: jal  0x3E5928                 (legacy rung, as in the old loop)
0x316f68: jalr $v1 (= F5, iface+0x64)   ra = 0x316f70
0x316f70: lw   $v1, 0x58($s0)
0x316f74: beq  $v1, $s2 → 0x316fac
0x316f7c: beqz $v0 → 0x316f94
0x316f84: beql $v1, $zero → 0x317140
0x316f8c: b → 0x3171c8
```

Thread 1 parks inside F6's WaitSema (323 waits, `ra`=`0x31aa8c`) every
block; F6's exact `jalr` site inside `sub_316F00` is unpinned (F6 below
stub cutoff — §P23-5).

### g. Chain answer (fix fires; completion lands; stall moves)

| Link | Receipt |
|---|---|
| Zero-max creates fixed | 28/29 returned (§P23-2a); -1 waits 257,125 → 0 |
| Thread 1 genuinely blocks | 323 F6 waits / 322 F7 wakes, balanced; WAIT 29 @ `0x423de8` all 17 samples |
| Thread 3 (flag-clearer) runs | sch≠0 all 17 blocks (27–38); consumed id-30 twice (:631/:680), then runs free |
| Old outer loop exits | 0 old-ras; phase advanced `sub_316D60` → `sub_316F00` (F4/F5 outer ras move) |
| Boot advances | GS kicks 66→96, prims 33→64 (textured prim=6, `drawing=1`); `run:tick` dma 888→4992, gif 50→278 over 6 ticks; pump/drainer/INTC paths all cycle |
| NEW stall | Thread 3's `*(0x52BE04)` poll (≈36.3M calls) — the word is never written (§P23-2i) |

### h. Ladder delta vs P22 LOG (boot-p1u-1: 258,784 lines, 28,980,295 B, 16 blocks)

LOG: 7,852 lines (−250,932), 1,053,739 B (−27,926,556), 17 blocks.

| Rung | P22 LOG | LOG | Delta |
|---|---|---|---|
| Thread-1 pc | `0x3e5980` ×9 + cycle | `0x423de8` (WAIT 29) ×17 | Parks in F6 (was free-spin) |
| Thread-1 sch | 27/3 ×16 | 72,36–38 ×16, 30 ×1 | Wake/block cycling regime |
| Thread-2 | parked 26, sch 2 then 0 | Same bytes | None |
| Thread-3 | Ready @ `0x31ac60`, sch 0 | Running, sch 27–38, pc `0x40b1d0`/`0x425cf0` | Starvation lifted |
| Thread-4 | parked 29, sch 3 b0 | parked 31, sch 25/18/19/15 | Id shift + cycling |
| Thread-5 | parked 30, sch 1 b0 | parked 32, sch 46/36/38 | Cycling (964 waits) |
| Missing / `No exact` | 0 / 0 | 0 / 0 | None |
| Old-loop ras | dominant | 0 | Old loop exited |
| `0x425cf0` spin | 0 | ~2.2M/block ×17 | NEW stall (thread 3) |
| CD reads total | 21 | 21 | None |
| CD callback | :611/:613, same bytes | :611/:613, same bytes | None (P1t fix firing) |
| Driver-entry | :626 | :626, byte-identical | None |
| Watch | 8 lines | 8 lines (same addrs/pcs) | None |
| `run:tick` | 9 (`pc`=`0x316e04`/`0x316e0c`) | 6 (`pc`=`0x40b1d0` ×5 + `0x3827e0` ×1) | New pcs; dma/gif climb |
| GIF/GS sweep | 2/66/122/33/8/1 | 48/96/128/64/64/30 | Drawing advances |
| Presented frame | None (TIMER only) | None (:46 TIMER only) | None |
| Crash / FATAL | 0 / 0 | 0 / 0 | None |
| Dormant / start-thread | 40 / 4 | 65 / 4 | Count only |
| SIF modules | 6 | 6 | None |
| `0x3e5440` | 0 hits | 0 hits | None |

### i. Boot 2: the polled word is never written (the one receipt)

LOG2 (WATCH `0x52BE04,0x450de4`): exactly **1** watch line —
`:50 addr=0x52be00 width=16 value=0x0… pc=0x10012c thread=1` (loader
zero-init, same init pattern as `0x519c40`'s line). Zero CPU-store
writes to `[0x52BE04,0x52BE0C)` across 90 s. Steady state otherwise
reproduces: 33 creates, `0x425cf0` 1.54M/2.15M/2.25M (b0–b2),
`op=wait id=-1` = 0, driver-entry byte-identical (:620, −6 line shift
from the missing `0x519c40` lines). Watch coverage: guest
WRITE8/16/32/64 macros all report when enabled (`macros.h:361-410`);
overlap rule `writeAddr < w+8 && w < writeAddr+width`
(`ps2_runtime.cpp:1196-1200`); the init line proves the watch armed on
this range.

## P23-3. Binaries and commits

| Binary / ref | sha256 / sha | Sources / state |
|---|---|---|
| `/tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner` (both boots) | `52f766a5c64024d145e10a306e37f141aa1b95173bf748b6afb2471ce9f34af7` | `8d10619` tree (P1v `Fix:` on `53bac61`; `-j4` rebuild, exit 0) |
| `ps2x_tests` (CWD `$R`, rebuilt) | Total 426, Passed 425, Failed 1 (`sceGsSyncVCallback … reserved async stack pool`, same test+assertion as P21/P22) | No new failure from the `Fix:` (new P1v test passes; pre-existing stands) |
| `PS2Recomp` branch `ssx3` HEAD | `8d10619` (`Fix: accept zero-max CreateSema as a binary semaphore (P23-1)`, 2 files, +46/-2, two trailers) | Sole P1v fork commit; worktree `M` = generated `runner/register_functions.cpp` only, never added |
| Post-script (shared tree) | Peer `bdae295` (I6, iOS-only CMake, desktop-inert) landed on `8d10619` during Step-2 analysis, pushed by its author; `8d10619` is on `fork/ssx3` as its parent; my `push fork ssx3` returned up-to-date | Boots/binary used the `8d10619` tree; peer change touches neither file nor the Darwin build |
| Fork push | `git push fork ssx3` from fork clone only (§P23-4) | The only push allowed (no push in ssx3) |
| This report | `[P1v]` commit (two trailers; local only) | Sole ssx3-repo change; no `runner/`, log, or `._*` added |

## P23-4. Exact commands

From `$R` (fork) unless noted; `$W=/Volumes/Extreme SSD/ps2recomp-spike`,
`$O=$W/P1/output`, `LOG=$W/P1/run/boot-p1v-1.log`,
`LOG2=$W/P1/run/boot-p1v-2.log`:

```
# Step 0 (lease-free evidence; reference clones read-only)
re-read REPORT Part 22 (paged reads)
read Sched create/delete/signal/poll/wait + KE codes + Sync.cpp CreateSema
  + ee_sema_t (Syscalls/Helpers/State.h) + MiniTest harness + kernel tests
grep CreateSema/max_count/maxCount pcsx2-ref (R5900OpcodeImpl:107 only) +
  IopBios (0) + BiosTools (IRX only); dobiestation emotion.cpp:68 (name table)
git log -L (host rule <- f4309cd #184 refactor, no citation)
web: ps2tek EE_Syscalls 40h + EE_Threading + ps2sdk kernel.h (all silent on max=0)
# Step 1 (Fix commit + builds + tests, no lease needed)
cmake --build /tmp/p1-link/runtime --target ps2x_tests -j4 (exit 0, HEAD unmodified)
ps2x_tests CWD $R (425/424/1 GsSyncV baseline; named via [Failed] grep)
(edit_file: add P1v zero-max test to ps2_runtime_kernel_tests.cpp only)
find ps2xTest -name '._*' -delete; rebuild ps2x_tests (exit 0)
ps2x_tests (426/424/2: BEFORE — new test fails ret=-1, valid asserts pass)
(edit_file: Sched effectiveMax clamp + store; 8+/2-)
find ps2xRuntime ps2xTest -name '._*' -delete
rebuild ps2x_tests + ps2EntryRunner (exit 0 both)
ps2x_tests (426/425/1 GsSyncV: AFTER — new test passes)
shasum -a 256 ps2EntryRunner (52f766a5)
git add <2 NAMED lib/test files>; git commit -m "Fix: ..." (two trailers) -> 8d10619
(write /tmp/p1v-boot1.py; diff vs p1u-boot1.py = docstring + LOG only)
# Step 2 (lease protocol + boot 1)
cat /tmp/ssx3-host-lease (M14 held; briefed share)
sleep/poll 5 min x2 (23:35:05Z M14; 23:40:16Z absent) + >> p1v-waits.log
pgrep -x ps2EntryRunner (exit 1); shasum fresh; git log (8d10619); ls ISO + ELF
printf 'P1v\n' > /tmp/ssx3-host-lease (23:41:01Z, absent verified twice) + >> p1v-waits.log
python3 /tmp/p1v-boot1.py (CWD $W/P1/run, 90 s, SIGTERM rc=-15, 1053739 B)
# Step 2 (log analysis, lease held)
sema-create census (33; F2 4 verbatim; ret 1-33 contiguous); -1 waits (0)
per-block thread table (17x5, sch series); signal/wait group-bys (id + ra/waker)
stub hist (0x425cf0 17/17; F4/F5 new ras; F6/F7/pred below cutoff; old ras 0)
resolve 0x40b1d0/0x425cf0/0x316f50/0x316f70 via ssx3-functions.csv (python3)
read $O/sub_0040B130 (loop) + sub_00425CF0 (whole) + sub_00316F00 (window)
epoch :604-:640 + :680; driver-entry bytes x3 boots; watch/probe/cd/dormant/SIF
GIF/GS sweep (48/96/128/64/64/30); python3 checks rows A-G; ELF batch 12 (0 bad)
read watch impl (macros.h:361-410; ps2_runtime.cpp emit + overlap + callers)
# Step 2 (boot 2: NEW stall worth one receipt)
(sed /tmp/p1v-boot1.py -> /tmp/p1v-boot2.py: LOG + WATCH 0x52BE04; docstring edit)
cat lease (P1v); pgrep -x (exit 1)
python3 /tmp/p1v-boot2.py (CWD $W/P1/run, 90 s, SIGTERM rc=-15, 1063718 B)
watch grep (1 line: loader init only); steady-state sanity (33/1.5M+/0)
# Step 3
(edit_file append Part 23 in 4 chunks)
git -C /Users/bradrichardson/dev/ssx3 add -f local/research/P1/REPORT.md
git -C /Users/bradrichardson/dev/ssx3 commit -m "[P1v] ..." (two trailers; NO push there)
git -C $R push fork ssx3 (the only push allowed)
rm -f /tmp/ssx3-host-lease; ls (absent); pgrep -x (exit 1)
```

Env delta boot 1 vs boot-p1u-1: none (script diff = docstring + LOG).
Env delta boot 2 vs boot 1: WATCH `0x519c40` → `0x52BE04` only. Source
delta: `EeScheduler.cpp` (8+/2− behavior) + `ps2_runtime_kernel_tests.cpp`
(+38 test).

## P23-5. What I could not do

- Pin the stored-max semantics from a written source: all references
  silent/LLE (§P23-1a rows 1–7) → clamp recorded as provisional pending
  real-BIOS evidence.
- Name the `0x52BE04` writer statically: no JAL/word sweep for the
  setter entry `0x425d08` (0 printed stub lines = below top-30 cutoff,
  not proof of absence); boot 2 answers it dynamically for CPU stores
  (none in 90 s) but host-side memcpy/DMA/SIF blits that bypass the
  `macros.h` report path would not emit — not excluded.
- Pin F6's exact `jalr` site inside `sub_316F00` (F6 below stub cutoff;
  only its WaitSema `ra`=`0x31aa8c` is observed) and read the rest of
  `sub_316F00` past the quoted window.
- Resolve the analyzer JAL convention (§P23-1h row C2): log/recomp/ELF
  agree on target = index<<2 (3 samples), while the textbook
  region-nibble OR gives `0x40425cf0` for the `0x40b1d0` call — tabled
  as observed, not adjudicated.
- Dump `0x52BE04`'s ELF section/initial bytes beyond the loader-init
  zeros, and chase why `run:tick` fired 6× (vs 9× in P22) — timing
  regime, unmeasured.
- Run a 3rd boot (max 2 used; both receipts closed).

---

## Part 24 (P1w): TOOLING — game config tracked in the fork + no-silent-drops census (179 sites); boot reaches the `0x52BE04` stall with a 6-line census

Brief `local/muse/prompts/P1w.md`. Two `fork`-only commits
(`Config:` + `Diag:`) + 2 boots. Tables, no verdicts.
Stale-reading guard: Part 23 re-read before acting (P23-0 the lease
protocol, P23-1h/1i the machine-check/ELF discipline, P23-2 the stall
receipts, P23-4 the command shapes), plus review §4.2 (the three
silent drops), §7.2 (the `[drop]` rule), §7.4 (CSV home).
`W=/Volumes/Extreme SSD/ps2recomp-spike`, `R=$W/PS2Recomp` (fork,
branch `ssx3`), `O=$W/P1/output`, `LOG=$W/P1/run/boot-p1w-1.log`,
`LOG2=$W/P1/run/boot-p1w-2.log`. File:line refs below are
`$R`-relative unless noted.

## P24-0. Lease record

| Event | Value |
|---|---|
| Lease at session start (00:06:02Z) | M14 (another agent; boots-only rule — poll, never force) |
| Waits log | `$W/P1/run/p1w-waits.log` (9 lines: start, 5 polls, correction, claim, release) |
| Poll 00:12:44Z | M14 still holds; no boot attempted |
| Poll 00:19:17Z | Lease file ABSENT (poll line's parenthetical wrongly said M14; correction appended 00:19:45Z) |
| Polls 00:27:33Z / 00:44:26Z / 00:50:32Z | Absent; not claimed until boot-ready per boots-only rule |
| Pre-claim checks (00:52:22Z) | Absent verified twice; `pgrep -x` exit 1; binary `156f493b` (P1w Diag build); fork HEAD `ed387c7` (pushed); ISO 3005415424 B + ELF 3890784 B present |
| Claim | `printf 'P1w\n' > /tmp/ssx3-host-lease` 00:52:33Z, immediately before boot 1 |
| Boot 1 | 90 s foreground, SIGTERM rc=-15, LOG 6,588 lines, 874,915 B, 17 blocks |
| Boot 2 | 90 s foreground, SIGTERM rc=-15, LOG2 6,133 lines, 811,146 B, 17 blocks |
| Release | 00:57:38Z, right after boot 2 (analysis needs no lease); verified absent; `pgrep -x` exit 1 |
| `adb` | Not used |

## P24-1. Config tracking + drop census + tests

### a. Paths (SSD exact, per the brief's do-not-assume rule)

| File | Exact path | Size / rows | sha256 (short) |
|---|---|---|---|
| SSD TOML (was also untracked) | `$W/P1/ssx3.toml` | 1619 lines | `d97cf953` |
| SSD active CSV | `$W/P1/ssx3-functions.sweep.csv` | 9275 lines / 9274 data rows | `6d231e81` |
| SSD pre-sweep CSV (untracked remainder) | `$W/P1/ssx3-functions.csv` | 8247 lines | — (not tracked, §P24-5) |
| Fork TOML (canonical) | `$R/games/ssx3/ssx3.toml` | 1622 lines | tracked `5b5ac3d` |
| Fork CSV (canonical, byte-identical) | `$R/games/ssx3/ssx3-functions.sweep.csv` | 9275 lines (`cmp` clean) | tracked `5b5ac3d` |

The brief assumed the TOML already lived in the fork branch; it did
not (`git ls-files` shows no TOML/CSV anywhere in the fork). Both were
moved side by side so "alongside the TOML" is literally true.

### b. Tracked-TOML diff vs the SSD original (4 hunks, nothing else)

```diff
-# Generated by ElfAnalyzer
+# Generated by ElfAnalyzer; tracked canonical copy (P1w).
+# Drive recomp from any CWD: ps2_recomp <this file>; all three paths below
+# are absolute because the loader resolves them CWD-relative (no TOML-dir
+# anchoring in config_manager/elf_parser).
-input = "SLUS_207.72"
+input = "/Volumes/Extreme SSD/ps2recomp-spike/P1/SLUS_207.72"
-ghidra_output = "ssx3-functions.sweep.csv"
+ghidra_output = "/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp/games/ssx3/ssx3-functions.sweep.csv"
-output = "./output/"
+output = "/Volumes/Extreme SSD/ps2recomp-spike/P1/output/"
```

Loader evidence: `ps2xRecomp/src/lib/config_manager.cpp:41`
(`ghidra_output` passed through verbatim) and
`ps2xRecomp/src/lib/elf_parser.cpp:959` (`std::ifstream file(mapPath)`
— CWD-relative, no TOML-dir join). Absolute paths need no loader
change, so no gap row.

### c. End-to-end resolution proof (tracked TOML drives recomp)

`cd $W/P1 && $W/P1/bin/ps2_recomp $R/games/ssx3/ssx3.toml`
(`$W/P1/run/recomp-p1w-tracked.log`, rc=0, 93 s) vs baseline
`$W/P1/recomp-p1l.log`:

| Check | Baseline (P1l) | Tracked-config run | Match |
|---|---|---|---|
| Parsing toml file | `ssx3.toml` | `$R/games/ssx3/ssx3.toml` (the tracked bytes drove the run) | — |
| Ghidra map | Loaded 9274 | Loaded 9274 | Yes |
| Discovered / processed / recompiled / stubs | 9273 / 9273 / 9096 / 177 | same | Yes |
| Entrypoints / fallbacks / warnings / errors | 393727 / 3598 / 3598 / 0 | same | Yes |
| Output entries | 9277 | 9277 | Yes |
| `register_functions.cpp` sha | `69ae3866…` | `69ae3866…` | Yes |
| `ps2_recompiled_functions.h` sha | `ec05c4d8…` | `ec05c4d8…` | Yes |
| `sub_00425CF0_0x425cf0.cpp` sha | `46340e17…` | `46340e17…` | Yes |
| `sub_0040B130_0x40b130.cpp` sha | `06b879c7…` | `06b879c7…` | Yes |

Regen is deterministic: all four spot hashes identical.

### d. `Config:` commit + push

| Item | Value |
|---|---|
| Commit | `5b5ac3d` (`Config: track SSX3 game config (TOML + function-map CSV) in games/ssx3 (P24-1)`, 2 files, +10897, two Muse trailers) |
| `pull --rebase` | Refused: unstaged `ps2xRuntime/src/runner/register_functions.cpp` (generated, never committable); pre-fetch showed `fork/ssx3 == HEAD`, so nothing to rebase |
| Push | `git push fork ssx3` from the fork clone only: `bdae295..5b5ac3d`, fast-forward |
| SSD originals | Left in place deliberately (working fallbacks; fork copies declared canonical here) |

### e. Drop-helper design (`ps2xRuntime/include/ps2_log.h`, +38)

| Decision | Value |
|---|---|
| Home | `ps2_log.h`: public, header-only, already included by all three runtime areas and reachable from the analyzer (`ps2xRuntime/include` is on its include path) and the tests — zero CMake changes |
| API | `dropsMuted()`, `formatDropLine(site, reason, args)`, `emitDropTo(ostream&, …)`, `emitDrop(…)` (delegates to cerr) |
| Format | `[drop] <site> <reason> <args>`, empty args render `-` |
| Default | ON in every build including the runner; kill-switch is a non-empty `PS2X_DROP_SILENCE` (name recorded here) |
| Env read | Fresh `getenv` per call, no cached static: drops are exceptional (no hot-path cost) and the switch stays testable + honors late-set env |
| Channels | Runtime → stderr (its diag channel); analyzer → stdout via `emitDropTo` (its import-summary channel; `ps2_analyzer … | tee` captures stdout only) |
| Ring | cerr/cout only — no runtime-log ring append, so a drop flood cannot evict ring entries |
| Rate limits | None: the census counts occurrences, and a spinning drop is the diagnosis; the kill-switch handles noise |
| Reason vocabulary | The `KE_` code for scheduler/syscall rejections; errno core (`EFAULT`…) where the code comments name one, else `error` for `-1`s; kebab tokens (`no-table-entry`, `unknown-syscall`…) for branches |

### f. Call-site census (179 total: 48 + 82 + 44 + 5)

Method: a mechanical script inserted 151 one-liners at standalone
`return KE_*` / `setReturnS32(ctx, KE_*|-1)` statements (site +
reason, args `-`); 28 hand sites add branch coverage and args
(snprintf'd ids, pcs, modes). Every hand edit verified by a
marker-count script (all 32 markers exactly-once after repair, §P24-1i).

| Area | File | Sites | Notes |
|---|---|---|---|
| sched | `Kernel/EeScheduler.cpp` | 48 | 40 error returns + pc-zero, vsync-cb, IRQ ×2, cause-range, addr-range, remove/enable-ignored |
| syscall | `Syscalls/FileIO.cpp` | 33 | incl. fioClose ternary rewrite |
| syscall | `Syscalls/Sync.cpp` | 16 | incl. CreateSema-noparam args |
| syscall | `Syscalls/Thread.cpp` | 11 | — |
| syscall | `Syscalls/System.cpp` | 10 | incl. syscall-layer `TODO` (capped-log sibling) |
| syscall | `Syscalls/RPC.cpp` | 6 | incl. SifCallRpc missing-client args |
| syscall | `Syscalls/Deci2.cpp` | 4 | 3 ternary rewrites + unknown-code default (capped-log sibling) |
| syscall | `Syscalls/Dispatcher.cpp` | 1 | numeric-dispatcher `default` with id+pc args |
| syscall | `Syscalls/Interrupt.cpp` | 1 | — |
| stub | `Stubs/GS.cpp` | 20 | read/alloc/sync validations |
| stub | `Stubs/SIF.cpp` | 5 | incl. 2 free-heap ternary rewrites |
| stub | `Stubs/FileIO.cpp` | 3 | — |
| stub | `Stubs/Pad.cpp` | 3 | incl. unknown-info-mode default |
| stub | `Stubs/DMA.cpp` | 2 | — |
| stub | `Stubs/LibC.cpp` | 2 | incl. puts-addr ternary |
| stub | `Stubs/IPU.cpp` | 2 | — |
| stub | `Stubs/CD.cpp` | 2 | incl. unknown-spin-mode default |
| stub | `Stubs/Compatibility.cpp` | 1 | — |
| stub | `Stubs/Font.cpp` | 1 | — |
| stub | `Stubs/MemoryCard.cpp` | 1 | — |
| stub | `Stubs/MPEG.cpp` | 1 | unknown-frame-rate default |
| stub | `Stubs/Unimplemented.cpp` | 1 | `TODO_NAMED` entry: every call counted (the warning below is rate-limited) |
| analyzer | `ps2xAnalyzer/src/elf_analyzer.cpp` | 5 | SCE-overflow, decode-gap, empty-range split, CSV malformed/invalid rows |

### g. Deliberate exclusions (rule + instances)

Uniform rule: every guest-visible error RETURN emits; every SILENT
discard-branch emits; normal answers, queries, by-design filters, and
already-LOUD branches do not.

| # | Excluded path | Rule |
|---|---|---|
| 1 | `pollSemaphore` → `KE_SEMA_ZERO`, `pollEventFlag` → `KE_EVF_COND` | Normal poll-miss answers, not rejections (would also flood) |
| 2 | `waitObjectId` default | Returns 0 for the 5 id-less reasons (None/Sleep/VSync/External/Mpeg) by design — attempted, then reverted when the suite showed reason=0/4 hits from a passing test |
| 3 | `dispatchIrq` masked-cause early return | Specified hardware behavior (masked IRQs do not run); hot |
| 4 | Stale alarm event (`it == end → break`) | Cancel-won race; ~unreachable since `cancelAlarm` erases the deadline |
| 5 | `writeGuestU32` null-address / null-rdram guards | Deliberate "no output" convention / unbound env (only the out-of-range guard emits) |
| 6 | `hasInvocation` false, `thread()` queries | Queries, not rejections |
| 7 | Stub/success-canned `0`/`KE_OK` returns | Answers (possibly wrong), not discards |
| 8 | SIF `shouldTraceSifReg` + MPEG stream-id predicate defaults | Internal classifiers |
| 9 | MPEG "unknown FFmpeg error" + Pad "UNKNOWN" | Diagnostic-string fallbacks |
| 10 | Analyzer MMIO no-LUI path | Cannot distinguish RAM from MMIO without the base; per-access emission would flood on normal stack accesses |
| 11 | Analyzer JALR skip, lib-function skips, unreliable-name skips, `try*` resolvers, CSV header skip | Documented static-analysis bounds / by-design filters / query pattern (recomp already reports unresolved JR/JALR) |
| 12 | Analyzer ELF-parse / SCE-DB-load / CSV-open failures | Already print; not silent |

Boundary (not triaged, §P24-5): analyzer files other than
`elf_analyzer.cpp`.

### h. Suite (`ps2x_tests`, CWD `$R`)

| Check | Value |
|---|---|
| Totals | 427 total / 426 pass / 1 fail |
| New P1w test | `Drop census lines format exactly and the kill-switch gates emission` — PASSES (format ×2, default-on, emit-on, mute-on, empty-value-emits, env save/restore) |
| P1v test | Passes; its negative-max case observably emits `[drop] sched/createSemaphore KE_ERROR init=0 max=-2 effmax=-2` (args upgrade proven end-to-end) |
| Sole failure | `sceGsSyncVCallback runs as a scheduler invocation on its callback stack` — "callback invocation should use the reserved async stack pool": same test+assertion as the P21/P22/P23 baseline (GsSyncV face; pre-existing, unrelated) |
| `[drop]` lines in suite output | 12 total, all from tests intentionally exercising error paths (2× `syscall/CreateThread`, 1× each: `StartThread`, `wakeupThread`, `deleteThread`, `createSemaphore`, `signalSemaphore` OVF, `pollSemaphore`, `cancelAlarm`, `sceSifDmaStat`, `sceSifGetOtherData`, `sceMcSync`) |
| First-run anomaly | 431× `sched/waitObjectId unknown-wait-reason` from passing tests → exclusion #2 above (reverted, rebuilt, re-verified 0) |

### i. Self-corrections during implementation

| # | Find | Catch | Fix |
|---|---|---|---|
| 1 | Typo'd flag (`kSifRpcModeNowait` → `kSifRpcDebugFlagNowait`) in the RPC hand-edit | Full-diff removal audit before building | Restored; removal list re-audited (8 removals, all intended restructures) |
| 2 | 7 batched edits silently lost (pc-zero, write-guard, OVF, createThread-id, setAlarm-id, Deci2-lock, SCE-match — one per 4-edit same-file batch) | Per-file marker-count script (counts mismatch) | Re-applied via asserting script/single edits; all 32 markers verified exactly-once; rule adopted: one same-file edit per turn |
| 3 | `waitObjectId` false positive (431 suite lines) | Suite output census | Reverted to a by-design comment (§P24-1g #2) |
| 4 | `._EeScheduler.cpp` sidecar globbed as a build source (13 errors) | Build failure | Repo-wide `._*` purge; purge repeated before every build |
| 5 | Stray `;` + braces at `elf_analyzer.cpp` EOF | Build failure | Removed (2-line restoration) |
| 6 | Commit message says "180 call sites"; audited count is 179 (RPC has 6, not 7) | Final count script, after push | Message stands (one-commit rule); this table is authoritative |

## P24-2. Boots + census + ladder check (regression check, not a diagnosis)

LOG 6,588 lines / 874,915 B / 17 blocks; LOG2 6,133 lines / 811,146 B /
17 blocks. CWD `$W/P1/run`, env = p1v-boot2 unchanged
(`PS2X_DIAG_SEMA` + `CREATE` + `S0` + WATCH `0x52BE04,0x450de4`;
boot-1 script diff = docstring + LOG + explicit `PS2X_DROP_SILENCE`
unset; boot-2 diff = docstring + LOG + `PS2X_DROP_SILENCE=1` only).
Binary `156f493b` both boots.

### a. The `[drop]` census (site × count — the whole table)

| # | Site | Reason | Count | Lines |
|---|---|---|---|---|
| 1 | `syscall/dispatchSyscallOverride` | `KE_ERROR` | 6 | LOG:53–58 (all bare `-`: script site, no args upgrade) |
| Total | — | — | **6** | — |

The 6 fire in early init, between `SetupHeap` + sema-creates #1–2
(all `tid=1`) and the rest of boot; nothing else in the 179 sites
fires across 90 s. Attribution attempt: block-0 histogram shows
`0x74` (SetSyscall) ×8 installs from `pc=0x42cbc8` and `0x5b`
(GetEntryAddress) ×6 from the adjacent `pc=0x42cbb8` — a
count-6 match that is suggestive but NOT proof (other ids sit below
the top-20 cutoff, and the 6 could span numbers). The override
handler lacks a table entry, so each of the 6 calls returns
`KE_ERROR` without running its normal handler. Which number(s) and
which handler address are unrecorded — args gap, §P24-5.

LOG2 (kill-switch on): **0** `[drop]` lines — the switch is proven
in the runner, not just the unit test.

### b. Ladder check vs P23-boot2 (one table — the boot still parks on `*(0x52BE04)`)

P23-boot2 baseline: 7,915 lines / 1,063,718 B / 17 blocks, WATCH
`0x52BE04,0x450de4`.

| Rung | P23-boot2 | LOG (boot 1) | Delta |
|---|---|---|---|
| Blocks | 17 | 17 | None |
| Thread-1 | WAIT 29 @ `0x423de8` ×17 | WAIT 29 @ `0x423de8` ×16 (b16 flush carries no thread lines) | None |
| Thread-1 sch b0–b15 | 72,36–38s | 32,24,22,24,28,28,26,30,28,28,30,30,28,30,28,30 | Lower absolute (~0.7–0.9×); regime same (wake/block cycling) |
| Thread-2 | parked 26, sch 0 | parked 26 @ `0x423de8`, sch 0 ×16 | None |
| Thread-3 | running, pc `0x40b1d0`/`0x425cf0`, sch=t1 | running, pc `0x40b1d0`×9/`0x425cf0`×7, sch=t1 (b9/b10 off-by-one sampling jitter) | None |
| Thread-4 | parked 31, sch=t1/2 | parked 31 @ `0x423de8`, sch=t1/2 exact (16,12,11,12,14,14,13,15,…) | None |
| Thread-5 | parked 32, sch=t1 | parked 32 @ `0x423de8`, sch=t1 | None |
| 29-handshake | 323 waits / 322 signals, F6 `ra=0x31aa8c` / F7 `ra=0x31aae4` | 253 / 252, same ras, same park/wake shapes | Balanced regime; lower iterations (throughput) |
| Creates / `-1` waits | 33 / 0 | 33 / 0 | None (P1v fix holds) |
| Driver-entry | byte-identical (`:620`) | byte-identical (`:625`; line shift only) | None |
| Watch | 1 line (loader init `0x52be00`) | 1 line (`:49`, same bytes) | None — word still never CPU-written |
| `0x425cf0` spin | 17/17 blocks, sole `ra=0x40b1d8`, ~2.2M/block | 17/17, sole `ra=0x40b1d8`, 1.26M–1.87M/block | Same stall; lower counts (throughput) |
| GS kicks / copy-reg / gs:gif / drawing=1 | 96 / 64 / 48 / 96 | 96 / 64 / 48 / 96 | None — exact |
| `run:tick` | 6 ticks, pcs `0x40b1d0`/`0x3827e0`, dma→4992 gif→278 | 7 ticks, pcs `0x40b1d0`/`0x40b1d8`, dma 762→4236 gif 43→236 | Same pcs/climb; lower totals (throughput) |
| CD `lbn=` lines / SIF loads | 42 / 18 | 42 / 18 | None — exact |
| Dormant / start-thread | 65 / 4 | 65 / 4 | None — exact |
| Missing / `No exact` | 0 / 0 | 0 / 0 | None |
| Presented frame | None | None | None |
| Crash / FATAL | 0 / 0 | 0 / 0 | None |

Throughput note: every absolute count (sch, handshake, stub
counts, dma/gif) runs ~0.7–0.9× of P23 while every relation,
shape, park, and byte-comparable is identical. The drop
instrumentation cannot explain it (6 emissions in 90 s, all on
cold error paths); P1x (PCSX2 reference trace) ran concurrently
in another pane on the same host. Recorded as contention, not a
regression — and it is a finding about the environment, not the
deliverable.

LOG2 steady-state spot check (silence on): 17 blocks, 33 creates,
0 `-1` waits, 17/17 `0x425cf0` blocks — reproduces with the
census muted.

## P24-3. Binaries and commits

| Binary / ref | sha256 / sha | Sources / state |
|---|---|---|
| `/tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner` (both boots) | `156f493b1bb42e6b35b9624a80047b7f5f8885ba4792a3a871029b38999c9ade` | `ed387c7` tree (P1w `Diag:` on `5b5ac3d`; `-j4` rebuild, exit 0) |
| `ps2x_tests` (CWD `$R`, rebuilt) | Total 427, Passed 426, Failed 1 (`sceGsSyncVCallback … reserved async stack pool`, same test+assertion as P21/P22/P23) | No new failure from the `Diag:` (new P1w test passes; pre-existing stands) |
| `PS2Recomp` branch `ssx3` HEAD | `ed387c7` (`Diag: P1w no-silent-drops census … (P24-2)`, 25 files, +453/-8, two trailers) | Second P1w fork commit; worktree `M` = generated `runner/register_functions.cpp` only, never added |
| Parent | `5b5ac3d` (`Config: track SSX3 game config … (P24-1)`, 2 files, +10897, two trailers) | First P1w fork commit |
| Fork pushes | `git push fork ssx3` from fork clone only, twice (`bdae295..5b5ac3d`, `5b5ac3d..ed387c7`, both fast-forward) | The only pushes allowed (no push in ssx3); each `pull --rebase` refused on the unstageable generated runner file with a clean pre-fetch, recorded §P24-1d |
| This report | `[P1w]` commit (two trailers; local only) | Sole ssx3-repo change; no `runner/`, log, or `._*` added |

## P24-4. Exact commands

From `$R` (fork) unless noted; `$W=/Volumes/Extreme SSD/ps2recomp-spike`,
`$O=$W/P1/output`, `LOG=$W/P1/run/boot-p1w-1.log`,
`LOG2=$W/P1/run/boot-p1w-2.log`:

```
# Step 0 (context reads; lease-free)
re-read REPORT Part 23 + review §4.2/§7.2/§7.4 (paged reads)
cat /tmp/ssx3-host-lease (M14) + >> p1w-waits.log (start line)
ls $W/P1 (*.toml + *.csv); read ssx3.toml head (ghidra_output = sweep CSV)
read config_manager.cpp + elf_parser.cpp loadGhidraFunctionMap (CWD-relative proof)
# Step 1 (CSV tracking + verification recomp, no lease needed)
mkdir $R/games/ssx3; cp -X ssx3.toml + ssx3-functions.sweep.csv; find -delete ._* (ExFAT)
(edit_file: tracked TOML header comment + 3 absolutized paths)
diff SSD-vs-tracked TOML (4 hunks); cmp CSVs (identical)
snapshot $O (9277 entries; 4 spot shas)
cd $W/P1 && $W/P1/bin/ps2_recomp $R/games/ssx3/ssx3.toml (93 s, rc=0, recomp-p1w-tracked.log)
compare summary + counts + 4 shas vs recomp-p1l.log (all identical)
git add <2 NAMED game-config files>; git commit -m "Config: ..." (two trailers) -> 5b5ac3d
git fetch fork ssx3; git pull --rebase fork ssx3 (refused: unstaged generated runner file)
git push fork ssx3 (bdae295..5b5ac3d fast-forward)
# Step 2 (drop census: survey + helper + 151 mechanical + 28 hand + test)
grep inventories: KE_ returns (sched 40 + impls), setReturn -1s (stubs incl. GS 20),
  default: branches (5 stubs + dispatcher + Deci2 + FileIO), analyzer continues (25)
(edit_file: ps2_log.h dropsMuted/formatDropLine/emitDropTo/emitDrop + <cstdlib>)
(python /tmp/p1w-drop-insert.py: dry-run review, errno fix, HAND_ONLY RPC:469, --apply = 151)
28 hand sites (8 sched-special + dispatcher + syscall-TODO + Deci2-default +
  8 ternary/RPC rewrites + TODO_NAMED + 3 stub defaults + 5 analyzer) +
  13 arg-upgrades (12 sched + CreateSema) + MiniTest (+ includes)
(marker-count script: 7 lost edits found -> asserting-script repair -> 32/32 markers)
(find $R -name '._*' -delete before EVERY build: sidecar-glob breakage)
cmake --build /tmp/p1-link/runtime --target ps2x_tests -j4 (exit 0 after 2 sidecar/brace fixes)
ps2x_tests CWD $R (427/426/1 GsSyncV; P1w passes; waitObjectId 431-line revert; rerun clean)
cmake --build /tmp/p1-link/runtime --target ps2EntryRunner -j4 (exit 0)
shasum -a 256 ps2EntryRunner (156f493b)
git add <25 NAMED lib/test/analyzer files>; git commit -m "Diag: ..." (two trailers) -> ed387c7
git fetch fork ssx3; git pull --rebase fork ssx3 (same generated-file refusal)
git push fork ssx3 (5b5ac3d..ed387c7 fast-forward)
(write /tmp/p1w-boot1.py + /tmp/p1w-boot2.py; diffs vs p1v-boot2.py = docstring + LOG + silence handling)
# Step 3 (lease protocol + boot 1)
polls 00:12:44Z (M14) / 00:19:17Z (absent + correction) / 00:27:33Z / 00:44:26Z / 00:50:32Z (absent) + >> p1w-waits.log
lease absent x2; pgrep -x (exit 1); shasum fresh; git log (ed387c7); ls ISO + ELF
printf 'P1w\n' > /tmp/ssx3-host-lease (00:52:33Z) + >> p1w-waits.log
python3 /tmp/p1w-boot1.py (CWD $W/P1/run, 90 s, SIGTERM rc=-15, 874915 B)
# Step 3 (log analysis, lease held)
[drop] census (6x one site, :53-58); block-0 histogram attribution attempt (0x74 x8 / 0x5b x6)
per-block thread table (17x5 python extract); 29-handshake balance; F6/F7 ras
driver-entry bytes; watch (1 line); 0x425cf0 17/17 + sole ra; GS/GIF/CD/SIF/dormant group-bys
P23-boot2 apples-to-apples diffs (same-pattern greps both logs)
# Step 3 (boot 2: kill-switch proof)
cat lease (P1w); pgrep -x (exit 1)
python3 /tmp/p1w-boot2.py (CWD $W/P1/run, 90 s, SIGTERM rc=-15, 811146 B)
[drop] count (0); steady-state spot (17/33/0/17)
rm -f /tmp/ssx3-host-lease (00:57:38Z); ls (absent); pgrep -x (exit 1); + >> p1w-waits.log
# Step 4 (this report; lease already released)
(edit_file append Part 24 in 4 chunks + 1 correction)
git -C /Users/bradrichardson/dev/ssx3 add -f local/research/P1/REPORT.md
git -C /Users/bradrichardson/dev/ssx3 commit -m "[P1w] ..." (two trailers; NO push there)
```

Env delta boot 1 vs boot-p1v-2: none (drops ride the default-on
channel; script diff = docstring + LOG + explicit silence-unset).
Env delta boot 2 vs boot 1: `PS2X_DROP_SILENCE=1` only. Source
delta: `ps2_log.h` (+38 helper) + 179 call sites + 1 test.

## P24-5. What I could not do

- Attribute the 6 `dispatchSyscallOverride` drops to a syscall
  number/handler: the site is a bare script insert (args `-`), and a
  post-boot args upgrade would need a second `Diag:` commit against
  the brief's one-commit rule. Recommended follow-up is a one-line
  args addition (`syscallNumber` + `handler` are both in scope) —
  NOT done here.
- Correct the `ed387c7` message count ("180" vs audited 179):
  left standing per the one-commit rule; §P24-1f is authoritative.
- Triage analyzer files beyond `elf_analyzer.cpp`
  (`analysis_passes`, `function_classifier`, `sce_symbol_scanner`,
  `toml_generator`, `analyzer_main`, `elf_analysis_context`) or
  `ps2xRecomp`'s `elf_parser` map-skip warnings (already loud, out
  of the named scope).
- Track the pre-sweep CSV (`ssx3-functions.csv`), the sweep script
  (`$W/P1/tools/codeptr_sweep.py`), or retire the SSD TOML: the
  consumed artifact (sweep CSV) is what is tracked; SSD originals
  stay as working fallbacks.
- Explain the ~0.7–0.9× throughput vs P23 beyond the P1x-contention
  note (§P24-2b): no profiling run; relations/shapes/parks all
  identical, so not pursued.
- Run a 3rd boot (max 2 used; census + silence-proof + ladder all closed).
- Session wall time ≈ 00:06–01:00Z (~1 h), inside the 4 h box.

---

## Part 25 (P1aa): FIX — P1z kernel-true sema amendment (A1–A3: store-as-is creates + unbounded signals); boot still parks on `0x52BE04`

Brief `local/muse/prompts/P1aa.md`. One `fork`-only commit
(`Fix:`) + 2 boots. Tables, no verdicts.
Stale-reading guard: Part 23 §P23-1a/b re-read before acting (P1v's
clamp-1 rule + its recorded-as-PROVISIONAL note) and
`local/research/P1z/REPORT.md` §P1z-4/§P1z-5 (verdict AMENDED + the
exact A1–A3 amendment), plus Part 24 (P24-0 the lease protocol, P24-2
the ladder receipts, P24-4 the command shapes).
`W=/Volumes/Extreme SSD/ps2recomp-spike`, `R=$W/PS2Recomp` (fork,
branch `ssx3`), `LOG=$W/P1/run/boot-p1aa-1.log`,
`LOG2=$W/P1/run/boot-p1aa-2.log`. File:line refs below are
`$R`-relative unless noted.

## P25-0. Lease record

| Event | Value |
|---|---|
| Lease at session start (01:48:10Z) | Absent (no `/tmp/ssx3-host-lease`); no waits, no polls needed |
| Waits log | `$W/P1/run/p1aa-waits.log` (3 lines: start, claim, release) |
| Pre-claim checks (01:54:39Z) | Absent verified twice; `pgrep -x` exit 1; binary `ae8e7b3d` (P1aa `Fix:` build); fork HEAD `f26f273` (pushed); ISO 3005415424 B + ELF 3890784 B present |
| Claim | `printf 'P1aa\n' > /tmp/ssx3-host-lease` 01:54:39Z, immediately before boot 1 |
| Boot 1 | 90 s foreground, SIGTERM rc=-15, LOG 3,507 lines, 443,852 B, 17 stub blocks |
| Boot 2 | 90 s foreground, SIGTERM rc=-15, LOG2 3,459 lines, 435,497 B, 17 stub blocks |
| Release | 01:58:03Z, right after boot 2 (analysis needs no lease); verified absent; `pgrep -x` exit 1 |
| `adb` | Not used |

## P25-1. Diff + BEFORE/AFTER + tests

### a. Pre-edit sync (lease-free, no conflicts)

| Item | Value |
|---|---|
| `fetch fork ssx3` | `2caf17c..c41efce`: P1y test fix (`2caf17c`, 1 file `ps2_gs_tests.cpp`) + rebased I7b (`c41efce`); local `2655264` was the pre-rebase I7b |
| Tree delta `2655264..c41efce` | Exactly the P1y 1-file diff (verified `diff --stat`) — the sync target is the green 427/427/0 baseline |
| Rebase | `git stash push -- <generated runner>` → `git rebase fork/ssx3` ("skipped previously applied commit 2655264", clean) → `git stash pop`; HEAD == `c41efce` |
| P7 | Concurrent pane (movie stub); its 2 untracked `Stubs/Ssx3Movie.*` files present in the clone, never staged or touched; nothing from P7 on `fork/ssx3` at push time |

### b. The amendment (one `Fix:` commit, `f26f273`)

| # | Location | Change |
|---|---|---|
| A1 | `ps2xRuntime/src/lib/Kernel/EeScheduler.cpp:1149` `createSemaphore` | Deleted the `effectiveMax` clamp + comment; reject ONLY `initCount < 0` (+ existing id-exhaustion); `semaphore.maxCount = maxCount` as-is; `dropArgs` format loses `effmax` (`init=%d max=%d`) |
| A2 | same file `:1205` `signalSemaphore` | Deleted the `count == maxCount → KE_SEMA_OVF` block incl. its diag/`emitDrop`; waiter-less signals always `++count` and return id; waiters-first branch untouched |
| A3 | `ps2xTest/src/ps2_runtime_kernel_tests.cpp:613` P1v test | Zero-max asserts `maxCount==0`; negative-max + init>max now asserted ACCEPTED (stored as-is); init<0 still asserted rejected; added two-waiter-less-signals-then-two-waits (count reaches 2, all succeed, no OVF) |
| — | `:45` `KE_SEMA_OVF` constexpr | Kept, unused on this path (brief's discretion) |
| — | wait / poll / `ReferSemaStatus` | No change (already count-only / report-max) |

Numstat: `EeScheduler.cpp` 9+/28−, `ps2_runtime_kernel_tests.cpp`
52+/3− (2 files, +61/−31). Staged set verified = the 2 named files
only (generated `runner/register_functions.cpp` + P7's untracked
`Stubs/Ssx3Movie.*` left out).

### c. BEFORE/AFTER receipts (same amended test, unfixed vs fixed tree)

| Receipt | Unfixed tree (`c41efce` + A3 test only) | Fixed tree (`f26f273`) |
|---|---|---|
| Suite | 427 total / 426 pass / 1 fail (`/tmp/p1aa-before.log`, rc=1) | 427 / 427 / 0 (`/tmp/p1aa-after.log`, rc=0) |
| Failing face | Sole failure = the amended P1aa test: `[Error]: <unknown>` (5 buffered assertion failures + uncaught park of the 2nd wait — see mechanism) | — (all green; P1y GsSyncV face stays fixed) |
| Zero-max create | id > 0 but `maxCount`=1 (stored-as-is assertion fails) | id > 0, `maxCount`=0, `count`=0 |
| Negative max (−2) | Rejected (`KE_ERROR` + `[drop] … init=0 max=-2 effmax=-2`) | id > 0, stored −2 |
| init>max (5>3) | Rejected (`KE_ERROR` + `[drop] … init=5 max=3 effmax=3`) | id > 0, `maxCount`=3, `count`=5 |
| init<0 | Rejected (`KE_ERROR`) | Rejected (`KE_ERROR` + `[drop] … init=-1 max=4`, no `effmax`) |
| 2 waiter-less signals | 2nd returns `KE_SEMA_OVF` (`[drop] … id=1 count=1 max=1`), count stays 1 | Both return id, count reaches 2 |
| 2 waits after | 1st consumes; 2nd parks (throws `EeDispatcherTransfer`) — the lost-signal wedge | Both consume, count back to 0, no throw |
| Suite `[drop]` lines | 16 | 12 (−4: the 2 create rejections + 2 OVF emissions the amendment removes; init<0 line remains in the new format) |
| Rebuild | `ps2x_tests` exit 0 | `ps2x_tests` exit 0 + `ps2EntryRunner` exit 0 |

BEFORE mechanism (all three evidences in `/tmp/p1aa-before.log`):
MiniTest assertions record-and-continue (execution reaches the OVF
`[drop]` past the 5 earlier failing assertions, whose buffered reasons
never print), then the 2nd wait parks at count 0 and its uncaught
`EeDispatcherTransfer` (non-`std::exception`) trips MiniTest's
`catch (...)` → `  [Error]: <unknown>` (`MiniTest.h:188`). The wedge
is P1v's own race window made visible: clamp-1 + OVF loses the second
signal and the second wait blocks.

No other test depends on the removed behavior: every other
`createSemaphore` call in `ps2xTest/src` uses valid init=0/max=1, no
test names `KE_SEMA_OVF` in an assertion, and the snddrv RPC test that
emitted the OVF `[drop]` as a side effect asserts only returned
addresses (still passes — count now accumulates instead of overflowing).

## P25-2. Boots + ladder check (regression proof, not a diagnosis)

LOG 3,507 lines / 443,852 B / 17 stub blocks; LOG2 3,459 lines /
435,497 B / 17 stub blocks. CWD `$W/P1/run`, env = p1w-boot1
unchanged (`PS2X_DIAG_SEMA` + `CREATE` + `S0` + WATCH
`0x52BE04,0x450de4`, drops ON; script diffs = docstring + LOG only).
Binary `ae8e7b3d` both boots.

### a. The `[drop]` census (P1w's tooling intact)

| # | Site | Reason | Count | Lines |
|---|---|---|---|---|
| 1 | `syscall/dispatchSyscallOverride` | `KE_ERROR` | 6 | LOG :53–58 (same lines as P24-boot1; all bare `-`); LOG2 :54–59 (1-line shift, same 6 bare lines) |
| Total | — | — | **6** | — |

Same single site × 6 as P24-boot1; nothing else in the 179 sites
fires. No `KE_SEMA_OVF` site exists anymore (A2 deleted its only
emitter); no `effmax` arg appears anywhere (A1's format change).

### b. Ladder check vs P24-boot1 (one table — the boot still parks on `*(0x52BE04)`)

P24-boot1 baseline: 6,588 lines / 874,915 B / 17 stub blocks. All
rungs below re-extracted from both logs with the same script
(`/tmp/p1aa-ladder.py`).

| Rung | P24-boot1 | LOG (boot 1) | Delta |
|---|---|---|---|
| Stub blocks | b0–b16 (17) | b0–b16 (17) | None |
| Thread blocks | 17 headers (b0–b16) | 16 headers (b0–b15; b16 stubs-only — SIGTERM cut the flush between dumps) | Timing artifact; LOG2 has 17/17 |
| Thread-1 | WAIT 29 @ `0x423de8` ×17, sch 70,32,24,22,24,28,… | WAIT 29 @ `0x423de8` ×16, sch 54,10,8,10,8,10,8,10,8,10,8,8,8,8,10,8 | Same park; cycling regime; lower absolute |
| Thread-2 | parked 26, sch 2 then 0 | parked 26 @ `0x423de8`, sch 2 then 0 | None |
| Thread-3 | running, pc `0x40b1d0`×10/`0x425cf0`×7, sch=t1 (±1 jitter b10/b11) | running, pc `0x40b1d0`×11/`0x425cf0`×5, sch=t1 (±1 jitter b13/b14) | None (same sampling-jitter phenomenon) |
| Thread-4 | parked 31, sch=t1/2 exact from b1 | parked 31 @ `0x423de8`, sch=t1/2 exact from b1 (10/5, 8/4, …) | None |
| Thread-5 | parked 32, sch=t1 | parked 32 @ `0x423de8`, sch=t1 (same ±1 jitter) | None |
| 29-handshake | 253 waits / 252 signals, F6 `ra=0x31aa8c` / F7 `ra=0x31aae4` | 86 / 85, same ras, same park/wake shapes | Balanced regime; lower iterations |
| 30-handshake | 2 waits / 2 signals | 2 / 2 | None — exact |
| 31-handshake | 253 / 252 | 86 / 85 | Balanced regime; lower iterations |
| Creates / `-1` waits | 33 / 0 | 33 / 0 | None |
| F2 zero-param pair | ret=28/29 | ret=28/29, same sites/pcs | None |
| Driver-entry | byte-identical (`:625`) | byte-identical (`:625`; same line) | None |
| Watch | 1 line (`:49`, loader init `0x52be00`) | 1 line (`:49`, same bytes) | None — word still never CPU-written |
| `0x425cf0` spin | 17/17, sole `ra=0x40b1d8`, 1.26M–1.87M/block | 17/17, sole `ra=0x40b1d8`, 373K–591K/block | Same stall; lower counts |
| GS kicks / copy-reg / gs:gif / drawing=1 | 96 / 64 / 48 / 96 | 96 / 64 / 48 / 96 | None — exact |
| `run:tick` | 7 ticks, pcs `0x40b1d0`/`0x40b1d8`, dma→4236 gif→236 | 9 ticks, pcs `0x40b1d0`/`0x40b1d8`/`0x3827e0`, dma→1500 gif→84 | Same pcs/climb; lower totals |
| CD `lbn=` lines / SIF loads | 42 / 18 | 42 / 18 | None — exact |
| Dormant / start-thread | 65 / 4 | 65 / 4 | None — exact |
| Missing / `No exact` | 0 / 0 | 0 / 0 | None |
| Presented frame | None | None | None |
| Crash / FATAL | 0 / 0 | 0 / 0 | None |

Throughput note: every absolute count (sch, handshakes, stub
counts, dma/gif) runs ~0.3–0.4× of P24 while every relation,
shape, park, and byte-comparable is identical. The amendment
removes branches (it cannot slow anything); P7 ran concurrently
in another pane per the brief. Recorded as contention, not a
regression — and it is a finding about the environment, not the
deliverable.

LOG2 steady-state spot check: 17/17 thread+stub blocks, 33
creates, 0 `-1` waits, 82/81 balanced 29-handshake (boot1: 86/85), 6-line
census, 17/17 `0x425cf0` blocks with the sole `ra`, GS
96/64/48/96, CD 42 / SIF 18, dormant 65 — reproduces. One
sampling artifact: a single t3 row in block 2 reads status=1
(Ready) pc=`0x0` (thread caught mid-switch; 1 of 17 rows).

## P25-3. Binaries and commits

| Binary / ref | sha256 / sha | Sources / state |
|---|---|---|
| `/tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner` (both boots) | `ae8e7b3d7d7fe2dfb3570515bea0f75490e2f112e8188df1e30ceb3e058c4ac6` | `f26f273` tree (P1aa `Fix:` on `c41efce`; `-j4` rebuild, exit 0) |
| `ps2x_tests` (CWD `$R`, rebuilt) | Total 427, Passed 427, Failed 0 | All green (new P1aa test passes; P1y baseline preserved; no failure face to name) |
| `PS2Recomp` branch `ssx3` HEAD | `f26f273` (`Fix: kernel-true CreateSema store-as-is plus unbounded waiter-less signals (P25-1)`, 2 files, +61/−31, three trailers) | Sole P1aa fork commit; worktree `M` = generated `runner/register_functions.cpp` only, never added |
| Parent | `c41efce` (`Entry: add iOS scene manifest … (I7b)`, on P1y `2caf17c`) | Pre-edit sync target (§P25-1a) |
| Fork push | `git push fork ssx3` from the fork clone only (`c41efce..f26f273`, fast-forward) | The only push allowed (no push in ssx3); `pull --rebase` refused on the unstageable generated runner file with a clean pre-fetch, recorded §P25-4 |
| This report | `[P1aa]` commit (two trailers; local only) | Sole ssx3-repo change; no `runner/`, log, or `._*` added |

## P25-4. Exact commands

From `$R` (fork) unless noted; `$W=/Volumes/Extreme SSD/ps2recomp-spike`,
`LOG=$W/P1/run/boot-p1aa-1.log`, `LOG2=$W/P1/run/boot-p1aa-2.log`:

```
# Step 0 (context reads; lease-free)
re-read REPORT Part 23 §P23-1a/b + P1z REPORT §P1z-4/§P1z-5 (amendment table)
cat /tmp/ssx3-host-lease (absent) + tee p1aa-waits.log (start line)
git fetch fork ssx3 (2caf17c..c41efce: P1y + rebased I7b); diff --stat 2655264..c41efce (P1y 1-file only)
git stash push -- <generated runner>; git rebase fork/ssx3 (skipped dup 2655264, clean); git stash pop
grep OVF/max-validation dependents in ps2xTest/src (none: valid-only creates, no OVF assertions)
# Step 1 (A3 test first, BEFORE receipts on the unfixed tree)
(edit_file: P1v test -> P1aa test, same tc.Run, +52/-3)
find $R -name '._*' -delete (ExFAT sidecars)
cmake --build /tmp/p1-link/runtime --target ps2x_tests -j4 (exit 0)
ps2x_tests CWD $R > /tmp/p1aa-before.log (427/426/1, P1aa face, OVF + wedge)
# Step 1 (A1+A2 fix, AFTER receipts)
(edit_file: createSemaphore clamp delete + store-as-is; signalSemaphore OVF block delete)
grep effectiveMax (gone); grep KE_SEMA_OVF (constexpr :45 only)
cmake --build /tmp/p1-link/runtime --target ps2x_tests -j4 (exit 0)
ps2x_tests CWD $R > /tmp/p1aa-after.log (427/427/0, rc=0; drops 16 -> 12)
cmake --build /tmp/p1-link/runtime --target ps2EntryRunner -j4 (exit 0)
shasum -a 256 ps2EntryRunner (ae8e7b3d)
git add <2 NAMED lib/test files>; git commit -m "Fix: ..." (three trailers) -> f26f273
git fetch fork ssx3; git pull --rebase fork ssx3 (refused: unstaged generated runner file)
git push fork ssx3 (c41efce..f26f273 fast-forward)
(write /tmp/p1aa-boot1.py + /tmp/p1aa-boot2.py; diffs vs p1w-boot1.py = docstring + LOG only)
# Step 2 (lease protocol + boot 1)
lease absent x2; pgrep -x (exit 1); shasum fresh; git log (f26f273); ls ISO + ELF
printf 'P1aa\n' > /tmp/ssx3-host-lease (01:54:39Z) + >> p1aa-waits.log
python3 /tmp/p1aa-boot1.py (CWD $W/P1/run, 90 s, SIGTERM rc=-15, 443852 B)
# Step 2 (boot 2: steady-state repro)
cat lease (P1aa); pgrep -x (exit 1)
python3 /tmp/p1aa-boot2.py (CWD $W/P1/run, 90 s, SIGTERM rc=-15, 435497 B)
rm -f /tmp/ssx3-host-lease (01:58:03Z); ls (absent); pgrep -x (exit 1); + >> p1aa-waits.log
# Step 2 (log analysis, lease already released)
(write /tmp/p1aa-ladder.py; same-script rungs x3: boot1 + boot2 + P24-boot1)
[drop] census (6x one site, :53-58 same lines); per-block thread table; handshake balances
driver-entry bytes; watch (1 line :49); 0x425cf0 17/17 + sole ra; GS/GIF/CD/SIF/dormant group-bys
# Step 3 (this report; lease already released)
(edit_file append Part 25)
git -C /Users/bradrichardson/dev/ssx3 add -f local/research/P1/REPORT.md
git -C /Users/bradrichardson/dev/ssx3 commit -m "[P1aa] ..." (two trailers; NO push there)
```

Env delta boots vs boot-p1w-1: none (drops ride the default-on
channel; script diff = docstring + LOG only). Source delta:
`EeScheduler.cpp` (9+/28−) + 1 test (52+/3−).

## P25-5. What I could not do

- Fix the kernel PollSema returns-`-1` vs fork `KE_SEMA_ZERO` (`-419`)
  divergence (P1z-7 observed-not-fixed; a separate brief owns it) —
  untouched per the brief.
- Attribute the 6 `dispatchSyscallOverride` drops (P24's args gap,
  unchanged) or correct the `ed387c7` message count ("180" vs 179):
  both pre-existing, out of the amendment's named files.
- Explain the ~0.3–0.4× throughput vs P24 beyond the contention note
  (§P25-2b): no profiling run; relations/shapes/parks all
  identical, so not pursued.
- Run a 3rd boot (max 2 used; ladder + repro both closed).
- Session wall time ≈ 01:48–02:02Z (~15 min), inside the 4 h box.

---

## Part 26 (P1ab): DIAGNOSIS — `0x52BE04` is SIF sregs[1]; the writer is the IOP's SET_SREG reply via EE set_sreg, and the HLE has no IOP SIF peer (SendCmd no-op, handler map write-only, no SIF0)

Brief `local/muse/prompts/P1ab.md`. Diagnosis only: 0 fork
commits + 2 boots. Tables, no verdicts. Stale-reading guard: Part 23
§P23-2e/i re-read before acting (the stall shape + boot-2 never-written
receipt), Part 25 §P25-2 (ladder baseline + 6-line census), Part 24
§P24-1f/g (census coverage + exclusion rules).
`W=/Volumes/Extreme SSD/ps2recomp-spike`, `R=$W/PS2Recomp` (fork, branch
`ssx3`), `O=$W/P1/output`, `LOG=$W/P1/run/boot-p1ab-1.log`,
`LOG2=$W/P1/run/boot-p1ab-2.log`. File:line refs below are `$R`-relative
unless noted. Every hand hex machine-checked §P26-1i; cited MIPS words
ELF-verified §P26-1i.

## P26-0. Lease record

| Event | Value |
|---|---|
| Lease at session start (02:43Z) | Absent; no polls needed |
| Waits log | `$W/P1/run/p1ab-waits.log` (3 lines: start, claim, release) |
| Pre-claim checks (03:00:52Z) | Absent verified twice; `pgrep -x` exit 1; binary `ae8e7b3d` (P1aa build, no rebuild — see below); ISO 3005415424 B + ELF 3890784 B present |
| Claim | `printf 'P1ab\n' > /tmp/ssx3-host-lease` 03:00:57Z, immediately before boot 1 |
| Boot 1 | 90 s foreground, SIGTERM rc=-15, LOG 7,827 lines, 1,049,583 B, 17 blocks |
| Boot 2 | 90 s foreground, SIGTERM rc=-15, LOG2 6,945 lines, 924,930 B, 17 blocks |
| Release | 03:04:07Z, right after boot 2 (analysis needs no lease); verified absent; `pgrep -x` exit 1 |
| `adb` | Not used |

No-rebuild note: fork HEAD at boot time was `69bb1ff` (P10
PollSema fix, landed during my static phase) with foreign uncommitted
mods (`CD.cpp`, sweep CSV — concurrent P9 pane) in the worktree. Per the
read-only rule I built nothing and booted the pre-existing `ae8e7b3d`
(`f26f273` tree): it reproduces the stall, keeps the P25 ladder
apples-to-apples, and P10's change (PollSema miss `-419`→`-1`) is
orthogonal to the SIF-handshake stall mechanism (§P26-5).

## P26-1. Static evidence

### a. `0x52BE04`'s ELF section + initial bytes (open thread (c) closed)

| Item | Value |
|---|---|
| Section | sec45 `.bss`, type 8 (NOBITS), flags `0x3`, addr `0x4a5c00`, size `0x98edc` |
| Offset in section | `+0x86204` |
| Program header | ph0 type 1, vaddr `0x100000`, filesz `0x3a4bf4`, memsz `0x43eadc` (single PT_LOAD) |
| File bytes | None: fileoff `0x42ce04` is past filesz (NOBITS zero-fill) |
| Initial value | `0x0` (loader zero-init; the boot watch lines confirm: `value=0x0…`, `pc=0x10012c`) |

### b. The full mailbox file (open thread (d) closed)

`$O/sub_00425CF0_0x425cf0.cpp` (`0x425cf0`–`0x425d38`) holds three Sony
SIF entries (shape-matched to ps2sdk `ee/kernel/src/sifcmd.c`: `static
int sregs[32]` + `struct cmd_data`, whose comment states binary
compatibility with the SCE libs):

| Entry | Address | Semantics | Live callers |
|---|---|---|---|
| `sceSifGetSreg` | `0x425cf0` | `v0 = *(0x52BE00 + a0<<2)` | 1: `0x40b1d0` (thread-3 poll, `a0=1`) |
| `sceSifSetSreg` | `0x425d08` | `*(0x52BE00 + a0<<2) = a1`, returns `a1` | 0 (§P26-1c) |
| cmd-data accessor | `0x425d28` | returns `0x52BCD8` (`&_sif_cmd_data`) | 0 (§P26-1c) |

`0x52BE04` = `sregs[1]` (EE-side SIF software register 1).
`0x52BCD8` = `_sif_cmd_data`: guest SIF-init writes verified at
`+0x00`=iopbuf-src, `+0x04`, `+0x08`=0, `+0x0C`=0x52BD00 (sys handlers),
`+0x10`=`0x20` (nr_sys=32), `+0x14`=0, `+0x18`=0, `+0x1C`=`0x52BE00`
(sregs pointer) — all 8 words match ps2sdk's `struct cmd_data` layout.

### c. Setter-entry JAL/word sweep (open thread (a) closed)

Whole-file sweep over the loadable range (`0x100000`, filesz `0x3a4bf4`):

| Target | JAL word | JAL hits | Raw-word hits | lui-formed hits |
|---|---|---|---|---|
| getter `0x425cf0` | `0x0c10973c` | 2: `0x40b1d0` (live poll), `0x426560` (dead: inside stubbed Sony InitRpc) | 0 | — |
| setter `0x425d08` | `0x0c109742` | 0 | 0 | 0 (`addiu`/`ori` imm `0x5d08`: none) |
| base2 `0x425d28` | `0x0c10974a` | 0 | 0 | 1 base2-lo coincidence at `0x3dcc20` (rs=17, not address formation) |

Direct stores to the word: `sw`/`sb`/`sh` with imm `0xBE04`: none.
`gp`-relative: `gp=0x4a30f0` on all threads (every `run:tick`);
`0x52BE04-0x4a30f0=0x88D14` exceeds ±32 K — excluded.
`register_functions.cpp` holds only the `0x425cf0` entry (line 397717);
the CSV has no `0x425d08`/`0x425d28` function starts.

### d. Mailbox-immediate users (all `-0x4200`/`-0x4328` sites triaged)

| Site | Base | Disposition |
|---|---|---|
| `0x425cf8`, `0x425d10` | `0x530000` | getter/setter proper (live, §P26-1b) |
| `0x425dc0`, `0x425e14` | `0x530000` | dead: inside stubbed `sceSifInitCmd` (`0x425d38`, TOML:150) |
| `0x425db0`, `0x425e50`, `0x425f48` | `$s2=0x530000` | dead: same stubbed region |
| `0x425ff4`, `0x42600c` | `0x530000` | live `sub_00425FF0`, but struct fields only (`0x52BCE4`–`0x52BCF0`, `+0xC`/`+0x10`/`+0x14`/`+0x18`) — never `+0x12C` |
| `0x42624c` | `$v1` | dead: inside stubbed `isceSifSendCmd` (`0x4261f0`, TOML:533) |
| `0x2459e8`, `0x24574c` | `0x480000` | coincidence: same immediates, `lui 0x48` base (`0x48BDE8`-family, game data) |

### e. The stubbed Sony SIF-init zero loops (the word's initializer on HW)

Decoded from intact ELF bytes in stubbed `sceSifInitCmd` (`0x425d38`–`0x425fb8`):

| Loop | Range written (value 0) | Bound check |
|---|---|---|
| 1 (`0x425df4`–`0x425e08`) | `0x52BD04 + 8k`, k=0..30 | max `0x52BDF4` (below the mailbox) |
| 2 (`0x425e0c`–`0x425e38`) | `0x52BE7C − 4k`, k=0..30 | min **`0x52BE04`** — the last word zeroed is the polled word; slots 1..31 |

So on HW the array reads `sregs[1..31]=0` after init; slot 0 is not
zeroed here. In the HLE this code never runs (stub); the host
`sceSifInitCmd` (`Stubs/SIF.cpp:679-684`) sets a flag only and writes no
rdram — same observable zeros via the `.bss` loader fill.

### f. The poller's handshake prologue + `_request_end` (why the poll exists)

`sub_0040B130` (`0x40b130`–`0x40b1f8`), sole JAL site `0x2290e0`
(`sub_00228EE0`, thread-3 init path), one-shot guard `*(0x4533E0)`:

| Step | Code | Decoded |
|---|---|---|
| 1 | `jal 0x42C078` (DIntr) | interrupts off |
| 2 | `jal 0x426020` (TOML:152) | `sceSifAddCmdHandler(0x80000018, 0x40B2D0, 0x528FC0)` — registers game `_request_end` (TOML:369) + handler-data struct (`+0x0`=1, `+0x4`=`0x225287C0`, `+0x8`=`0x20`, `+0xC`/`+0x10`=0) |
| 3 | `jal 0x42C0C0` (EIntr) | interrupts on |
| 4 | `jal 0x4261B0` (TOML:155) | `sceSifSendCmd(0x80000001`=SET_SREG, `0x528800`, `0x18`, 0,0,0) with payload words `*(0x528810)=1, *(0x528814)=1` (sreg index 1, value 1) |
| 5 | `0x40b1d0: jal getter; 0x40b1d8: beqz` | `while (sregs[1]==0)` — the stall |

`_request_end` (`0x40b2d0`, in `sub_0040B2B0`): dispatches on
`*(packet+0x20)` (the REND `cid` word): `0x1A→0x40B340`
(end-function + `SignalSema`), `0x19→0x40B368` (bind-fill + signal),
`0x1D→0x40B390`, `0x1C→0x40B3A4`, else `→0x40B3A8`. Every store is
`*($s0+off)` with `$s0=*(packet+0x1C)` (the client struct, an
EE-controlled pointer echoed by the IOP) — never a fixed sregs address;
0 JAL to `0x40B2D0` exist, so it fires only via SIF dispatch.

Sibling raw-`SendCmd` cids (same `0x40B` RPC-client module):
`0x19`@`0x40B52C` (BIND), `0x1D`@`0x40B670`, `0x1A`@`0x40B85C`/`0x40B8C8`
(CALL); user-cid `1`@`0x3F4988`/`0x3F4F98`/`0x3F52E0` (other module);
`0x3C45C0` cid unread (§P26-5). Post-poll path (`0x2290E8+`): repeated
`jal 0x319718` config calls — no sregs use.

### g. Sony's own InitRpc guest bytes (the sregs[0] control case)

Decoded from intact ELF bytes in stubbed `sceSifInitRpc`
(`0x426408`–`0x4265a8`) — ps2sdk's `sceSifInitRpc` shape exactly:

| Step | Code |
|---|---|
| Register | `AddCmdHandler` cids `8/9/A/C` → handlers `0x426708/0x426A98/0x426C88/0x426820` (`0x4264cc/4e4/4fc/514`) |
| Skip check | `sceSifGetReg(0x80000002)` (`jal 0x4241B0`); nonzero → return |
| Init send | `SendCmd(INIT_CMD=2, 0x52BDC0, 0x10, 0,0,0)` with word[3] (`0x52BDCC`) `=1` (`0x426554`) |
| Poll | `jal getter(0)` (`0x426560`, delay `$a0=0`); `beqz → 0x426560` — spins on **`sregs[0]`** |
| Finish | tail-`j` to `sceSifSetReg` (`0x4241A0`) with (`0x80000002`, 1) |

Consequence: Sony's RPC uses cids `8/9/A/C` + `sregs[0]` (RPCINIT).
The game's `0x18/0x19/0x1A/0x1C/0x1D` + `sregs[1]` protocol is NOT
Sony's RPC — it is a separate (EA-custom or Sony-extended) EE↔IOP
ready-handshake whose IOP peer is narrowed but not closed (§P26-3a).

### h. Host write-path audit (open thread (b) closed)

Every host path that writes guest rdram bypasses the `macros.h` watch.
Enumerated with disposition for `0x52BE04`:

| # | Site | Behavior | Why it cannot be the exit writer |
|---|---|---|---|
| 1 | `Syscalls/RPC.cpp:987` (`sceSifSendCmd`, the serving impl — the §P26-2 log line comes from `:993`) | extra-copy iff `sizeExtra>0`; returns 1 | handshake has `sizeExtra=0` (delay `$t1=0`); otherwise no-op, no dispatch |
| 2 | `Stubs/SIF.cpp:24-47` (duplicate `sceSifSendCmd`) | same extra-copy shape | not the serving impl (no log line); same no-op character |
| 3 | `Syscalls/RPC.cpp:164` (`SifStopModule`), `:257/302/315` (`SifBindRpc`), `:455/505/520/595/599` (`SifCallRpc`) | struct fills + `rpcCopyToRdram` to guest-provided client/server/receive addrs | targets are caller-passed structs/buffers, never the lib-static sregs word; game JALs these stubs (15/94/9 sites) but any nonzero sregs write would end the stall, which persists |
| 4 | `Stubs/SIF.cpp:591/610-614` (`sceSifGetOtherData`), `:882` (`sceSifSetDma` via `:275-360` `copyGuestByteRange`), `Stubs/DMA.cpp:62-65` | guest-driven copies | never invoked this boot (no log lines; SetDma/DMA not in TOML); same persistence argument |
| 5 | `Stubs/SIF.cpp:439-446` (`sceSifAddCmdHandler`) | records `g_sifCmdHandlers[cid]=handler` | **write-only map**: only refs are `:63` decl, `:82` clear, `:444` insert, `:741` erase — the registered `_request_end` can never be invoked |
| 6 | SIF0 DMA from IOP | — | **no emulation exists**: zero `SIF0`/`sif0` refs under `src/lib/`; all guest SIF-DMA programming is stubbed out |
| 7 | `sceSifSetReg` (`Stubs/SIF.cpp:926`) / `sceSifGetReg` (`:631`) | host-side `g_sifRegs` map only | not in TOML (unmapped); touch no rdram; the game uses the guest sregs array instead |

Net: no host path addresses the sregs array (the HLE never learns its
address — `InitCmd` is stubbed), and the stall's persistence proves no
channel wrote nonzero to any sreg in 90 s. A zero-valued host write
would be unobservable and irrelevant to a `beqz` poll.

### i. Machine-check paste block + ELF batch

```
mbox: 0x52be00 0x52be04 | loop2min: 0x52be04 | loop1max: 0x52bdf4
hdata: 0x528fc0 | pkt: 0x528800 | handler: 0x40b2d0
s2: 0x52bd80 | s0: 0x52d680 | a2b: 0x52c680 | a3b: 0x52ce80
initpkt: 0x52bdc0 0x52bdcc
arms: 0x40b340 0x40b368 0x40b3a4 0x40b390
beqz-g: 0x426560 | beqz-t3: 0x40b1d0
gp-gap: 0x88d14 (> 0x7fff, gp-relative excluded)
b1 total 36055000 | b2 total 30176440 | p25 total 8640642
```

Rows: mailbox base/index; SIF-init loop bounds; poller
handler-data/packet/handler immediates; Sony InitRpc struct immediates;
INIT packet + word[3]; `_request_end` arm targets; both `beqz` loop
targets; gp gap; per-boot `0x425cf0` totals.
ELF batch (all words read from `SLUS_207.72`, 0 mismatches): full
18-word mailbox (`0x425cf0`–`0x425d34`, §P26-1b); SIF-init stores +
both loops (`0x425d38`–`0x425fb8` spot: prologue, struct writes, loop
words); Sony InitRpc (`0x426408`–`0x4265a8`: AddCmdHandler cids,
`0x426554` send, `0x426560`/`0x426568` poll); poller args + sibling
cids (`0x40b1a8`–`0x40b1d8`, `0x40b51c/660/854/8c0`,
`0x3f4974/8c/e4`).

## P26-2. Boots + census + ladder check

LOG 7,827 lines / 1,049,583 B / 17 blocks; LOG2 6,945 lines / 924,930 B
/ 17 blocks. CWD `$W/P1/run`, env = p1aa-boot1 unchanged
(`PS2X_DIAG_SEMA` + `CREATE` + `S0`, drops ON) except WATCH covers all
32 sregs (`0x52BE00`–`0x52BE78` in 8 B windows + legacy `0x450de4`;
script diffs = docstring + LOG + WATCH). Binary `ae8e7b3d` both boots.

### a. Receipts (the stall, the census, the silence)

| # | Receipt | Boot 1 | Boot 2 |
|---|---|---|---|
| 1 | `[drop]` census | 6 lines, sole site `syscall/dispatchSyscallOverride` `KE_ERROR` (`:69-74`; +16-line shift vs P25 from the 15 extra watch lines + 1 texture line) | same 6 (`:68-73`) |
| 2 | Census correlation | `[diag:syscall] id=0x5b count=6 first=0x42cbb8 last=0x42cbb8` — the only count-6 syscall; `0x5B`=`GetEntryAddress` (`Dispatcher.cpp:325-327`), skipped by the override's `KE_ERROR` (`System.cpp:441`) | same line, same values |
| 3 | Handshake send | 1× `[sceSifSendCmd] cid=0x80000001 packet=0x528800 psize=0x18 extra=0x4a29f0` (`:1047`; byte-identical to P25 `:1040`) | same bytes (`:1049`) |
| 4 | sregs watch | 16 lines, all loader zero-init (`pc=0x10012c`, value 0) across `0x52BE00`–`0x52BE80`; **0 post-init writes to any of the 32 slots** | same 16 + 0 |
| 5 | Poll steady state | `0x425cf0` 17/17 blocks, sole `ra=0x40b1d8`, 1.45M–2.25M/block, total 36,055,000 | 17/17, sole ra, 1.33M–2.21M/block, total 30,176,440 |
| 6 | Setter/base2 dynamic | `target=0x425d08`: 0 lines; `target=0x425d28`: 0 lines — consistent with 0 static callers (§P26-1c), not proof alone | same 0/0 |
| 7 | Creates / `-1` waits | 33 / 0 (P1v/P1aa fixes hold) | 33 / 0 |

### b. Ladder check vs P25-boot1 (one table — same stall, faster host)

P25-boot1 baseline: 3,507 lines / 443,852 B / 17 stub blocks.

| Rung | P25-boot1 | LOG (boot 1) | Delta |
|---|---|---|---|
| Stub / thread blocks | 17 / 16 (b16 stubs-only) | 17 / 17 | None (full flush both P1ab boots) |
| Thread-1 | WAIT 29 @ `0x423de8` ×16, sch 54,10,8,… | WAIT 29 @ `0x423de8` ×17, sch 72,36,34,38,… | Same park; cycling regime; P23-shaped counts |
| Thread-2/4/5 | parked 26/31/32 | 17/17 each, same ids/pcs; t4 sch=t1/2 exact from b1 | None |
| Thread-3 | running, pc `0x40b1d0`×11/`0x425cf0`×5, sch=t1 | running, pc `0x40b1d0`×6/`0x425cf0`×11, sch=t1 exact from b1 | Same two pcs (sampling jitter); same regime |
| 29/31 handshakes | 86/85, same ras | 321/320, same F6/F7 ras + park/wake shapes | Balanced regime; 3.7× iterations (throughput) |
| 30-handshake | 2 / 2 | 2 / 2 | None — exact |
| Driver-entry | byte-identical (`:625`) | byte-identical (`:641`; shift only) | None |
| `[drop]` census | 6× override site | 6× same site | None — §P26-2a |
| SendCmd | 1× SET_SREG line | 1× same bytes | None — exact |
| `0x425cf0` spin | 17/17 sole ra, 373K–591K/block | 17/17 sole ra, 1.45M–2.25M/block | Same stall; 4.17× counts (throughput) |
| GS kicks / copy / gif / drawing=1 | 96 / 64 / 48 / 96 | 96 / 64 / 48 / 96 | None — exact |
| `run:tick` | 9 ticks, dma→1500 gif→84 | 7 ticks, dma→5568 gif→310, same pc family/sp/gp | Same pcs/climb; higher totals (throughput) |
| CD `lbn=` / SIF loads | 42 / 18 | 42 / 18 | None — exact |
| Dormant / start-thread | 65 / 4 | 65 / 4 | None — exact |
| Missing / `No exact` | 1 / 0 (byte-identical JALR `0x2322d4→0x395730` line in all three logs) | 1 / 0, same bytes | None — exact (P25's "0" was its counting convention; the line exists in P25-boot1 too) |
| Presented frame | None | None | None |
| Crash / FATAL | 0 / 0 | 0 / 0 | None |

LOG2 spot check: 17/17 blocks, 33 creates, 0 `-1` waits, 272/271
balanced handshake, same 6-line census, 17/17 `0x425cf0` sole-ra
blocks, GS 96/64/48/96, CD 42 / SIF 18, dormant 65 — reproduces.
Throughput note: absolute counts run 3.5–4.2× of P25 while every
relation, shape, park, and byte-comparable is identical; no concurrent
pane was active this time (P25 noted P7 contention). Environment
finding, not a regression.

## P26-3. Attribution + named fix brief

### a. Candidate-writer table (every channel closed or narrowed)

| # | Candidate | For | Against | Status |
|---|---|---|---|---|
| 1 | Local setter `0x425d08` (Sony `sceSifSetSreg`) | the designated local writer | 0 JAL / 0 raw words / 0 lui-formed (§P26-1c); watch silence (§P26-2a#4) | EXCLUDED |
| 2 | SIF-init zero loops | last word written is `0x52BE04` (§P26-1e) | stubbed (never runs); writes 0, which cannot exit a `beqz` poll | EXCLUDED (as exiter) |
| 3 | `_request_end` (`0x40B2D0`) | registered for `0x18`; runs at INTC-tail on HW | stores only `*(client+off)`, never fixed sregs (§P26-1f); HLE never dispatches it (write-only map, §P26-1h#5) | EXCLUDED as sregs writer (but REQUIRED for later RPC progress — see fix brief) |
| 4 | Other guest CPU store | — | no formation exists (no `0xBE04` stores, no gp range, no `+0x12C` struct store — §P26-1c/d) + 0 post-init watch lines on all 32 slots across 2 boots (§P26-2a#4) | EXCLUDED |
| 5 | Host memcpy/DMA/SIF blits | bypass the watch (§P26-1h) | enumerated sites write only caller-passed structs/buffers; several never invoked; above all, the stall's persistence proves no channel wrote nonzero to any sreg in 90 s (and the HLE never learns the array address) | EXCLUDED as exit writer |
| 6 | SIF0 DMA from IOP + EE `set_sreg` sys-handler[1] | Sony's only sregs write path (`sregs[pkt->sreg]=pkt->val`, ps2sdk `sifcmd.c:208-214`; binary-compatible `cmd_data` verified §P26-1b); game's send/poll pair matches Sony's RPCINIT handshake shape (§P26-1g); the EE→IOP `SET_SREG(1,1)` + EE `sregs[1]` poll is a two-sided ready-flag | the IOP-side announcer (which module sends the reply, on what trigger, with what value) is not identified from EE-side evidence | ATTRIBUTED (mechanism); responder NARROWED, not closed |

### b. Attribution

On HW the poll exits when the IOP's `SET_SREG(1,x)` reply packet
arrives via SIF0 DMA and EE `set_sreg` writes `sregs[1]=x`. It never
fires in the HLE for three conjoint, file-cited reasons: (i) the
outbound send is a no-op — `sceSifSendCmd` (`Syscalls/RPC.cpp:972-1002`)
returns 1 without delivering anything to any IOP peer; (ii) the inbound
path does not exist — no SIF0 emulation (§P26-1h#6), no incoming-packet
queue, no guest SIF dispatch (that code is stubbed out); (iii) the
registered guest completion handler is unreachable —
`g_sifCmdHandlers` is write-only (`Stubs/SIF.cpp:63/82/444/741`). The
guest side is correct: a one-shot EE↔IOP ready-handshake that a real
IOP answers. This is an HLE-completeness stall, not guest-correct
waiting on an upstream thread (no thread, sema, or callback in the boot
can produce the write — candidates 1–5).

The narrowed-but-open item is the IOP announcer's identity: Sony-side
evidence bounds it to "the IOP's RPC-subsystem ready announcement"
(ps2sdk's IOP `sceSifInitRpc` sends `SET_SREG` to the EE at
`iop/system/sifcmd/src/sifrpc.c:80`; the EE's Sony `sceSifInitRpc`
polls `sregs[0]` for it), but the game's slot (`1`, not `0`) and cids
(`0x18+`, not `8+`) mark a distinct handshake, plausibly tied to the
just-loaded `MSIFRPC`/`LIBNET` pair (loads 17–18 at `:1038-1039`,
immediately before the `:1047` send). The fix below does not need the
announcer's name — only its contract (one-shot nonzero).

### c. Named fix brief: P1ac (proposed) — complete the SIF ready-handshake in the HLE

| Item | Value |
|---|---|
| File | `ps2xRuntime/src/lib/Kernel/Syscalls/RPC.cpp`, in `sceSifSendCmd` (`:972-1002`) |
| Hunk shape | After the extra-copy block: if the game is SSX3 (gate via the existing `ps2_game_overrides` descriptor registry, SLUS-keyed per `games_database.cpp`) AND `cid==0x80000001` (SET_SREG) AND the guest packet's word[4] (sreg index) `==1`: write u32 `1` to guest `0x52BE04` via `getMemPtr`+`memcpy` (same bypass channel as `:520/595/599`; emits no watch line — note it) + one stderr receipt line (`[sif-handshake] sregs[1]=1`, capped like `:990-998`); return stays 1 |
| Value | `1`: any nonzero exits the `beqz` poll; mirrors the sent value and Sony's `SetReg(RPCINIT,1)` convention (§P26-1g) |
| Safety case | One-shot flag: setter has 0 callers (§P26-1c), no other guest store can form the address (§P26-1c/d), `getter(1)`'s only live caller is the poll (§P26-1c) — writing it is unobservable except via the poll; idempotent if the handshake repeats |
| Proof boots | 2× 90 s: expect the `0x425cf0` counts to collapse (poll exits), thread-3 pc to leave `0x40b1d0`/`0x425cf0`, thread 3 to advance past `0x2290E8`, and the new park/RPC traffic catalogued; the sregs watch stays silent (bypass write) so the receipt line + poll-exit are the proof rows |
| Predicted next stall (must-read for P1ac) | The game's BIND (`sub_0040B400` → `SendCmd(0x19)` → `WaitSema($s2)` at `0x40B55C`) parks on an RPC sema that only `_request_end` can signal — which needs HLE RPC completion. Follow-up brief sketch (P1ad): on `SendCmd` BIND/CALL/RDATA (cids `0x19/0x1A/0x1C/0x1D`), craft the IOP's `END(0x18)` response in guest memory and invoke the `g_sifCmdHandlers[0x18]` guest address via the scheduler's `GuestInvocation` machinery (cf. `System.cpp:447-461`) |
| Proper long-term fix (not briefed) | Un-stub the EE SIF cmd system + emulate the IOP SIF peer (incoming packets, SIF0 DMA/interrupt, guest dispatch). P1ac is the minimal faithful completion; it does not substitute for this |

Ride-along (separate, pre-existing): the 6 `dispatchSyscallOverride`
drops are now narrowed to 6× `GetEntryAddress` (`0x5B`) from
`pc=0x42cbb8` whose game-installed override handler has no registered
function (`System.cpp:438-445`). Recommended one-line close-out (P24's
proposal, still open): add `syscallNumber`+`handler` args at the
`:441` `emitDrop` (both in scope). Early-init only, benign w.r.t. this
stall (drops at `:69-74`, handshake at `:1047`).

## P26-4. Exact commands

From `$R` (fork, read-only — no edits, no add, no commit, no push) unless
noted; `$W=/Volumes/Extreme SSD/ps2recomp-spike`, `LOG`/`LOG2` as above:

```
# Step 0 (context reads; lease-free)
re-read REPORT Part 23 §P23-2e/i + Part 25 §P25-2 + Part 24 §P24-1f/g (paged reads)
cat /tmp/ssx3-host-lease (absent); pgrep -x ps2EntryRunner (exit 1)
git -C $R log --oneline -5 + status (HEAD e235c4b P7, then 69bb1ff P10 + foreign P9 mods; untouched)
git -C $R show --stat e235c4b (P7 deliberately unwired); shasum binary (ae8e7b3d, kept, no rebuild)
# Step 1 (static: ELF + mailbox + sweeps; lease-free)
python3 ELF header/section script (.bss sec45, NOBITS, +0x86204, past-filesz)
cat $O/sub_00425CF0 (full mailbox file) + $O/sub_00425D38 (sceSifInitCmd stub shell)
python3 JAL/word sweeps (getter 2 / setter 0 / base2 0; raw words 0/0/0)
grep register_functions.cpp + headers + sweep CSV (only 0x425cf0 registered)
python3 lui-0x52/0x53 + addiu-imm sweeps (-0x4200 x5, -0x4328 x8, all triaged)
python3 0x425d38-region store list + 0x425df4-0x425fb8 dump (zero loops decoded)
cat $O/sub_0040B130 (poller, 260 lines) + sed $O/sub_0040B2B0 (handler arms)
python3 JAL sweeps (0x40b130:1 / 0x40b2d0:0 / 0x426020:9 / 0x4261b0:17 / 0x4261f0:3 / 0x423dd0:20)
cat $O/sub_0042C0C0 (EIntr) + $O/sub_00426408 (InitRpc stub) + $O/sub_00425FF0 (struct-only)
python3 imm-0x5D08/0x5CF0/0x5D28 + store-imm-0xBE04 sweeps (setter: none; direct: none)
grep boot-p1aa-1.log (syscall hist 0x5b x6; thread entries; SendCmd :1040; SIF loads)
read Stubs/SIF.cpp (SendCmd :24, AddCmdHandler :439, GetReg :631, InitCmd :679, SetDma :794, SetReg :926)
read Syscalls/RPC.cpp SendCmd :972-1002 + Dispatcher/System.cpp override :422-461 + :496-503
grep g_sifCmdHandlers (4 refs, write-only) + copyGuestByteRange/getMemPtr writers (audit table)
grep SIF0/sif0 under src/lib (zero refs)
git clone --depth 1 --filter=blob:none --sparse ps2sdk /tmp/ps2sdk-ref; sparse-checkout ee/kernel/{src/{sifcmd,sifrpc,iopcontrol}.c,include}, common/include, iop/system/{sifcmd,sifman,sifinit,msifrpc}
read ps2sdk sifcmd.c (sregs/set_sreg/cmd_data), sifrpc.c (_request_end/InitRpc poll), sifcmd-common.h (cids), iop sifrpc.c:80 (IOP SET_SREG send), msifrpc/sifman (no 0x18 cids)
python3 Sony InitRpc dump 0x426408-0x4265a8 (cids 8/9/A/C, INIT send, sregs[0] poll decoded)
python3 sibling SendCmd windows (cids 0x19/0x1D/0x1A/user-1) + CSV name grep (none)
read $O/sub_0040B400 post-send (WaitSema $s2 @0x40b55c); ELF strings 0x48AAxx (post-poll config keys)
python3 JAL sweep Sony RPC stubs (BindRpc 15 / CallRpc 94 / CheckStat 9 / InitRpc 14 / InitCmd 2)
# Step 2 (boots; lease P1ab held 03:00:57Z-03:04:07Z only)
(write /tmp/p1ab-boot1.py; WATCH = 16 sregs addrs + 0x450de4; sed -> /tmp/p1ab-boot2.py, LOG-only diff)
pre-claim checks (lease absent x2; pgrep exit 1; shasum ae8e7b3d; HEAD 69bb1ff; ISO + ELF sizes)
printf 'P1ab' > lease + >> p1ab-waits.log; python3 /tmp/p1ab-boot1.py (90 s, SIGTERM rc=-15)
watch/drop/SendCmd/cf0 spot greps; cat lease (P1ab); pgrep (exit 1)
python3 /tmp/p1ab-boot2.py (90 s, SIGTERM rc=-15)
rm lease; verify absent; pgrep exit 1; >> p1ab-waits.log (release line)
# Step 2 (analysis, lease released)
(write /tmp/p1ab-ladder.py; same-pattern rungs x3: P25-boot1 + both P1ab boots)
drops shell-verified 6/6/6; missing-target byte-identity x3; t1/t3 sch series; cf0 totals; machine-check block
# Step 3 (this report; lease released)
(edit_file append Part 26 in 3 chunks)
git -C /Users/bradrichardson/dev/ssx3 add -f local/research/P1/REPORT.md
git -C /Users/bradrichardson/dev/ssx3 commit -m "[P1ab] ..." (Orchestrated-By trailer; NO push there)
```

Env delta boots vs boot-p1aa-1: WATCH widened to all 32 sregs (+15
watch lines, +1 texture line shifts); script diffs = docstring + LOG +
WATCH. Source delta: none (0 fork commits, 0 fork edits).

## P26-5. What I could not do

- Name the IOP announcer (which module sends the EE its
  `SET_SREG(1,x)`, on what trigger, with what exact value): EE-side
  evidence bounds it to the IOP's RPC-ready announcement (§P26-3b) but
  cannot identify the module. Exact next probes: (i) `strings` + SIF-send
  pattern grep over the disc's `MSIFRPC.IRX`/`LIBNET.IRX` (loads 17–18,
  immediately pre-handshake); (ii) a HW/LLE SIF0 packet trace (P1x asks
  for this); (iii) P1ac's proof boots (if `sregs[1]=1` unblocks the
  thread past `0x2290E8` into RPC traffic, the contract is confirmed
  without the name).
- Decode the `0x3C45C0` `SendCmd` cid (`$a0` set outside the read
  window) and the `0x40B670` (`0x1D`) / `0x40B3A4` (`0x1C`) arm
  semantics beyond their targets — sibling-protocol details, not needed
  for this poll.
- Prove the game reaches RPC BIND after the poll (the P1ad prediction
  rests on the post-poll `0x319718` path being unexamined past its first
  calls); P1ac's boots decide it.
- Re-baseline under the P10 binary (boots ran pre-P10 `ae8e7b3d`;
  P10's PollSema `-1` changes handshake iteration counts at most —
  orthogonal mechanism, recorded §P26-0).
- Attribute the 6 override drops to a handler address (needs the
  one-line args addition at `System.cpp:441` — a fork edit outside a
  diagnosis brief) or judge their benign-ness beyond phase separation.
- Run a 3rd boot (max 2 used; census + silence + ladder all closed).
- Session wall time ≈ 02:43–03:35Z (~55 min), inside the 4 h box.

## Part 27 (P1ac): FIX — SIF ready-handshake completed host-side (`sregs[1]=1`); the `0x425cf0` poll collapses to a single getter call, thread 3 advances to a sema-30 wait, main parks in `sub_00394ED0`; the BIND prediction is refuted

Brief `local/muse/prompts/P1ac.md`. FIX brief: 2 fork commits + 2
boots. Tables, no verdicts. Stale-reading guard: Part 26 §P26-3 (the
attribution + this fix's exact spec), §P26-1f (poller sequence),
§P26-1h (host audit), §P26-2 (ladder baseline).
`W=/Volumes/Extreme SSD/ps2recomp-spike`, `R=$W/PS2Recomp` (fork,
branch `ssx3`), `O=$W/P1/output`,
`LOG=$W/P1/run/boot-p1ac-1.log`, `LOG2=$W/P1/run/boot-p1ac-2.log`.
File:line refs below are `$R`-relative unless noted. Every cited
guest word re-read from `SLUS_207.72` with the corrected segment map
(fileoff = vaddr − `0x100000` + `0x1000`); one decode pass with the
`+0x1000` missing was caught against the recompiled file and redone.

## P27-0. Lease record

| Event | Value |
|---|---|
| Lease at session start | Absent; no polls needed |
| Waits log | `$W/P1/run/p1ac-waits.log` (3 lines: start, claim, release) |
| Pre-claim checks (03:34:06Z) | Absent verified twice; `pgrep -x` exit 1; binary `5878ad69` (P1ac build); ISO 3005415424 B + ELF 3890784 B present |
| Claim | `printf 'P1ac\n' > /tmp/ssx3-host-lease` 03:34:10Z, immediately before boot 1 |
| Boot 1 | 90 s foreground, SIGTERM rc=-15, LOG 19,150 lines, 2,643,773 B |
| Boot 2 | 90 s foreground, SIGTERM rc=-15, LOG2 19,281 lines, 2,667,056 B |
| Release | 03:37:28Z, right after boot 2 (analysis needs no lease); verified absent; `pgrep -x` exit 1 |
| `adb` | Not used |

## P27-1. Diff + BEFORE/AFTER + tests

### a. Changed files + commit split (recorded)

| File | Delta | Commit |
|---|---|---|
| `ps2xRuntime/src/lib/Kernel/Syscalls/RPC.cpp` | +63 (gate + descriptor + handshake hunk + test reset) | `6447d8b` (fix + test, one commit) |
| `ps2xTest/src/ps2_runtime_kernel_tests.cpp` | +86 (3 focused tests) | `6447d8b` (with the fix it pins) |
| `ps2xRuntime/src/lib/Kernel/Syscalls/System.cpp` | +3/−1 (ride-along) | `45da174` (second commit — my call per the brief) |

Named `git add` only; the pre-existing worktree mod to the generated
`ps2xRuntime/src/runner/register_functions.cpp` was never staged,
committed, or touched. No `._*` in source dirs (purged after edits;
sidecars observed only under `.git/`).

### b. Handshake hunk shape (§P26-3c, implemented exactly)

| Item | Value |
|---|---|
| Gate | `ps2_game_overrides` descriptor `ssx3-sif-handshake`, elfName `SLUS_207.72`, entry `0x00100008`, crc32 0 (don't-care); sets a process-wide atomic at `loadELF` time |
| Site | `sceSifSendCmd`, after the extra-copy block, before the log-cap block |
| Condition | gate set AND `cid==0x80000001` AND guest packet word[4]==1 (range-checked via `getEeGuestStruct`, `packetSize>=20`, overflow guard) |
| Write | u32 `1` to guest `0x52BE04` via `getMemPtr`+`memcpy` (bypass channel — emits no watch line, noted) |
| Receipt | `[sif-handshake] sregs[1]=1` on stderr, capped at 5 (file's `logCount` convention) |
| Return | Stays 1 (untouched) |
| Test hook | `resetSsx3SifHandshakeForTesting()` in `RPC.cpp`, TU-local forward declaration in the test (the `resetSifState` precedent in `ps2_runtime.cpp:34`) |

### c. Ride-along (`System.cpp:441`)

`emitDrop("syscall/dispatchSyscallOverride", "KE_ERROR")` gains a
third arg, `syscall=0x%x handler=0x%x` from the in-scope
`syscallNumber`+`handler` (64-byte stack buffer, the `:415` style).
Format-only; `setReturnS32(ctx, KE_ERROR)` + `return true` unchanged.

### d. BEFORE/AFTER receipts

| # | Receipt | BEFORE (P26 logs) | AFTER (P1ac boots) |
|---|---|---|---|
| 1 | `[drop]` census | 6× `[drop] syscall/dispatchSyscallOverride KE_ERROR -` (`:69-74` boot-p1ab-1) | 6× `... KE_ERROR syscall=0x5b handler=0x80075000` (`:68-73` LOG, `:69-74` LOG2 — +1-line shift in boot 2 from an early `[frame:upload]` line) |
| 2 | Census correlation | `[diag:syscall] id=0x5b count=6 first=0x42cbb8 last=0x42cbb8` | Same line, same values (both boots) |
| 3 | Handshake receipt | 0 in both P26 logs | 1× `[sif-handshake] sregs[1]=1` (`:1049` LOG, `:1054` LOG2), immediately before the SendCmd line |
| 4 | SendCmd line | 1× `cid=0x80000001 packet=0x528800 psize=0x18 extra=0x4a29f0` (`:1047`) | Same bytes (`:1050` LOG, `:1055` LOG2) |
| 5 | Override apply (new) | Absent | `[game_overrides] applying 'ssx3-sif-handshake'` + `applied 1 matching override(s)` (`:48`, merged-line) |
| 6 | SendCmd call total | 1 line (< 5 cap) | 1 line (< 5 cap) → exactly one `sceSifSendCmd` call all boot, both boots |

Row 1 closes the P26-5 open item: the 6 drops are `GetEntryAddress`
(`0x5B`) from `pc=0x42cbb8` whose game-installed override handler is
`0x80075000` (kernel address, no recompiled entry — hence the drop).
Early-init only (`:68-73`, handshake at `:1049`).

### e. Suite (stays all-green, no other face)

| Run | Binary (sha256, 8) | Tree | Total / Passed / Failed |
|---|---|---|---|
| BEFORE | `bfe534e9` (`ps2x_tests`) | `69bb1ff` + 4 foreign worktree mods (P9 `CD.cpp`+sweep, P11 sif-test — both uncommitted at the time) | 428 / 428 / 0 |
| AFTER | `daf0b63f` (`ps2x_tests`) | `4326926` + my 3 files (P9 `4326926` + P11 `bfa0213` committed mid-session, before my build) | 431 / 431 / 0 |

The +3 are the new `PS2RuntimeKernel` sub-cases, all passing by name:
`SIF handshake stays off without the SSX3 override (P1ac gate)`,
`SIF handshake writes sregs[1]=1 for SSX3 SET_SREG(1,1) (P1ac)`,
`SIF handshake ignores other cids and sreg slots (P1ac)`. Each resets
the gate first and last (order-independent). CWD `$R` for both runs
(the `instructions.h` lookup note, §P2-6). No existing test changed
result.

## P27-2. Boots + poll-exit proof + new park

Env = p1ab-boot scripts verbatim except LOG names (`PS2X_DIAG_SEMA`
+ `CREATE` + `S0`, drops ON, WATCH = 16 sregs addrs + `0x450de4`).
CWD `$W/P1/run` both boots. Boot binary `5878ad69` (P27-3).

### a. Poll-exit proof rows

| # | Proof | Boot 1 | Boot 2 |
|---|---|---|---|
| 1 | Receipt + send | `:1049` receipt, `:1050` same-bytes SendCmd | `:1054` receipt, `:1055` same-bytes SendCmd |
| 2 | Stub `0x425cf0` blocks | 0/17 (was 17/17 sole-ra) | 0/17 |
| 3 | Getter trace (`sub_00425CF0`) | — (trace is boot 2's) | 1 enter / 1 exit — a single read saw `1` |
| 4 | Poller trace (`sub_0040B130`) | — | 1 / 1 — entered and returned |
| 5 | Thread-3 pc | 17/17 WAIT @`0x423de8` (sema 30) | 17/17 WAIT @`0x423de8` (sema 30) |
| 6 | sregs watch | 16 loader lines (`:49-64`, `pc=0x10012c`), 0 post-init | 16 + 0 (same) |

Rows 1+3: the host write lands synchronously inside step-4 `SendCmd`,
before the step-5 poll's first read — hence exactly one getter call.
Row 6 is the predicted bypass silence (proof is rows 1–5, not the
watch). Trace = `$W/P1/run/ps2_log.txt` (boot 2's, 109,497,883 B).

### b. Thread 3 advanced past `0x2290E8` (downstream-only executions)

The `beqz`-to-self poll at `0x40b1d0` has no other exit; every row
below is reachable only past it (`0x2290e0: jal 0x40b130` returns to
`0x2290e8: lw a0,0xda4(gp)` — the config path):

| # | Row (boot 1; boot 2 same unless noted) |
|---|---|
| 1 | 4 new semaphores from tid=3 (ret=34..37; P26 ended at ret=33): ra `0x40c0c0` (`jal 0x423DA0` ret in `sub_0040C028`), `0x3c3344`, `0x3c1e04`, `0x3e56c4` |
| 2 | `0x40Cxx` RPC-client waits (no park): sema 34 from ra `0x40c314` (`jal 0x423DE0` ret) and ra `0x40c85c` (`jal 0x423DE0` ret; the following `jal 0x40c8c0` is a local call, not SendCmd) |
| 3 | 1 unhandled host RPC: `[IOP/RPC trace:unhandled] sid=0x80000211 rpc=0x1 pc=0x40c34c` via `jal sceSifCallRpc@0x00426D18` (TOML:163) at `0x40c344` |
| 4 | Park: WAIT sema 30 @`0x423de8`, ra=`0x31aca4` (`jal 0x423DE0` ret in `sub_0031AAF0`); w30=4/s30=3, signals from tid=1 ra=`0x31acf4` (`jal 0x423DC0` ret); ends parked |
| 5 | Supporting: 1 dormant trace passes `0x228a0c` (thread-init region) |

### c. New park catalogue

| Thread | State (17/17 blocks, both boots) |
|---|---|
| 1 (main, entry `0x100008`) | RUNNING 14/17 (boot1: 7+7; boot2: 9+7) inside `sub_00394ED0` @`0x394f08`/`0x394f3c`, ra=`0x363240` (`jal 0x394ED0` ret at `0x363238` in `sub_00362DE8`); leaf = 4-word memcmp (`0x394f18-30`) + list-walk retry (`bnez *(a2+0x14) -> 0x394f08` @`0x394f7c`); trace 15,989/15,989 balanced (repeat-called, returns each call); `dma`/`gif` frozen at 1166/65 on all 19–20 ticks |
| 2 / 5 | Unchanged parks: WAIT 26 / 32 @`0x423de8` |
| 3 | WAIT 30 (row §P27-2b#4) |
| 4 | sema-31 INTC pump: waits ra=`0x31ac30`, signals `inInt=1` ra=`0x31abf8` (`jal 0x423DD0` ret); w31/s31 = 5287/5286 (boot1), 5349/5348 (boot2), balanced |
| 6 (new, entry `0x3c19a8`) | WAIT 36 @`0x423de8` |

| Traffic | Boot 1 | Boot 2 |
|---|---|---|
| `sceSifSendCmd` calls | Exactly 1 (the handshake; §P27-1d#6) | Exactly 1 |
| SIF module loads | 21 (+3: `DRTYSCKF`/`LGAUD`/`VOIPF.IRX`, ids 19–21) | 21, same |
| CD `lbn=` reads | 810 (`0x10`→`0x4311f`, first/last byte-identical across boots) | 810 |
| `_request_end` (`0x40B2D0`) trace | — | 0 / 0 (still never dispatched) |
| Presented frame / FATAL / crash | None / 0 / 0 | None / 0 / 0 |

Stub profile: 57 distinct targets (vs the single-target P26 spin);
top counts are one-block transients (`0x41ea18` 953,379 ×1 block);
steady-state targets (`0x326eb0`, `0x3ffbc0`, `0x3ffa58`, …) run
~10k over 16 blocks each.

### d. BIND prediction (§P26-3c): REFUTED, with line receipts

| Predicted sub-row | Observed | Status |
|---|---|---|
| Game's BIND sends raw `SendCmd(0x19)` | SendCmd called exactly once all boot (the SET_SREG); no `cid=0x19` line (cap is 5, only 1 line exists) | REFUTED |
| Park at `WaitSema($s2)` `0x40B55C` | Zero `0x40b` bytes anywhere in either log; thread 3 parks at ra `0x31aca4` on sema 30 | REFUTED |
| `sub_0040B400` reached | Trace 0 / 0 | REFUTED |

Nuance (not a partial pass): the game's `0x40Cxx` RPC-client code DID
run (sema-34 create, two waits, one `sceSifCallRpc` via the Sony stub
at `0x426D18`) — the game used the host RPC path, not a raw-SendCmd
BIND, then moved on. `_request_end` remains undispatched (0/0), so an
HLE-RPC-completion stall of the predicted *shape* may still lie ahead;
it is not the observed park.

### e. Ladder vs P26-boot1 (one table)

P26-boot1: 7,827 lines / 1,049,583 B / 17 stub blocks.

| Rung | P26-boot1 | P1ac-boot1 | P1ac-boot2 |
|---|---|---|---|
| Lines / bytes | 7,827 / 1,049,583 | 19,150 / 2,643,773 | 19,281 / 2,667,056 |
| Stub / thread blocks | 17 / 17 | 17 / 17 | 17 / 17 |
| Thread-1 | WAIT 29 @`0x423de8` ×17 | RUNNING @`0x394f08`/`0x394f3c` ×14 (+1 WAIT, 2 transients) | RUNNING ×16 (+1 WAIT) |
| Thread-3 | running, `0x40b1d0`/`0x425cf0` | WAIT 30 @`0x423de8` ×17 | WAIT 30 ×17 |
| Thread-2/4/5 | parked 26/31/32 | same ids/pcs; t4 sch ~300 steady | same |
| Thread-6 | Absent (5 threads) | WAIT 36 (6 threads) | same |
| 29-handshake w/s | 321 / 320 | 65 / 65 | 65 / 65 |
| 30-handshake w/s | 2 / 2 | 4 / 3 (ends parked) | 4 / 3 |
| 31-handshake w/s | 321 / 320 | 5287 / 5286 (INTC pump) | 5349 / 5348 |
| Creates / `-1` waits | 33 / 0 | 37 / 0 (+34..37, all tid=3) | 37 / 0 |
| Driver-entry | 1 line | 98 lines (driver re-entered; later lines carry the `0x618520` sp) | 98 lines |
| `[drop]` census | 6× same site, no args | 6× same site + `syscall=0x5b handler=0x80075000` | 6× same + args |
| SendCmd | 1× SET_SREG line | 1× same bytes + 1× handshake receipt | same |
| `0x425cf0` spin | 17/17 sole ra, 36.1M total | 0 blocks; trace getter 1/1 | 0 blocks |
| GS kicks / copy / gif / drawing=1 | 96 / 64 / 48 / 96 | 96 / 64 / 48 / 96 (exact) | exact |
| `run:tick` | 7 ticks, pc `0x40b1d0`-family, dma climbing to 5568 | 19 ticks, pc `0x394f08`-family, dma/gif frozen 1166/65 | 20 ticks, same freeze |
| CD `lbn=` / SIF loads | 42 / 18 | 810 / 21 | 810 / 21 |
| Dormant / start-thread | 65 / 4 | 121 / 5 | 126 / 5 |
| Missing / `No exact` | 1 / 0 (byte-identical JALR `0x2322d4→0x395730`) | 1 / 0, same bytes | same |
| Presented frame | None | None | None |
| Crash / FATAL | 0 / 0 | 0 / 0 | 0 / 0 |

Attribution note: the baseline binary (`ae8e7b3d`, `f26f273` tree)
predates P9/P10/P11; the P1ac binary (`5878ad69`) contains all four
change-sets. The poll-exit rows (receipt, getter 1/1, poller 1/1,
`0x425cf0` 0 blocks, thread-3 migration) are mechanism-exclusive to
P1ac — only this change writes `sregs[1]`. Downstream volume rows (CD
810, dormant counts, `0x3e3ad8` ×770/boot) are joint with P9's
CD-callback change (`4326926`; `sub_003E3AD8` file present in `O`),
which is live in this binary.

## P27-3. Binaries and commits

| Item | Value |
|---|---|
| BEFORE `ps2x_tests` | sha256 `bfe534e9…` (full: `bfe534e92924766a3cfba0c117080285831181b85eb2bf1666fd4cbaeeebb311`), built Sep 19 23:14 from `69bb1ff` + 4 foreign worktree mods |
| BEFORE `ps2EntryRunner` | sha256 `950675bb…` (full: `950675bb75585a9ec1fb2f56c906df25293ed669728094b31382190ef2b94d20`) |
| AFTER `ps2x_tests` | sha256 `daf0b63f…` (full: `daf0b63fb7d6133cd1ffdbccc0d719e64a610e5eca86158019536888f7b7eab4`), built from `4326926` + my 3 files |
| AFTER `ps2EntryRunner` | sha256 `5878ad69…` (full: `5878ad6969b79759a19c218471a9479e02a97f319969f454b592d9ab257bae04`) — both boot binary and pre-claim check |
| Build | `cmake --build /tmp/p1-link/runtime --target ps2x_tests ps2EntryRunner -j4`, exit 0, 8 steps; 1 `ld` duplicate-library warning (`ps2xRecomp/libps2_recomp_lib.a`, observed as-is) |
| Build flags (cache) | Release, `PS2X_ENABLE_RUNTIME_LOGS=ON`, `PS2X_ENABLE_AGRESSIVE_LOGS=ON`, `PS2X_BUILD_TEST=ON`, Ninja |
| Fork commit 1 | `6447d8b` Fix: complete the SSX3 SIF ready-handshake in `sceSifSendCmd` (P1ac) — `RPC.cpp` + test |
| Fork commit 2 | `45da174` Diag: attribute `dispatchSyscallOverride` drops with syscall+handler (P1ac ride-along) — `System.cpp` |
| Push | `git push fork ssx3` → `4326926..45da174`, exit 0; `HEAD...fork/ssx3` = 0/0 after |
| Pull --rebase | Refused: pre-existing unstaged generated `runner/register_functions.cpp` (not mine; never touched). `fetch` + `rev-list` showed behind 0 (nothing to replay), so the push integrated no foreign history; no foreign rebase conflict occurred |
| Concurrent commits | `bfa0213` (P11 test 1-liner) + `4326926` (P9 CD-shim removal + CSV split) landed mid-session, before my build; both are in the boot binary (P27-2e attribution note) |

## P27-4. Exact commands

From `$R` (fork) unless noted; `$W=/Volumes/Extreme SSD/ps2recomp-spike`,
`LOG`/`LOG2` as above:

```
# Step 0 (context reads; lease-free)
re-read REPORT Part 26 (full) + brief local/muse/prompts/P1ac.md
cat /tmp/ssx3-host-lease (absent); git -C $R status/log/remote/branch
git -C $R diff --stat (4 foreign worktree mods at session start)
read Syscalls/RPC.cpp sceSifSendCmd :972-1002 + System.cpp :422-461
read game_overrides.h/games_database.h + game_overrides.cpp + builtin_profiles.cpp
read ps2_log.h emitDrop + MiniTest.h + RPC.h + ps2_syscalls.h declarations
# Step 1 (BEFORE receipts; lease-free)
shasum -a 256 /tmp/p1-link/runtime/ps2xTest/ps2x_tests /tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner
cd $R && /tmp/p1-link/runtime/ps2xTest/ps2x_tests | tail (428/428/0)
grep P26 logs: 6 census lines :69-74, sif-handshake count 0/0, SendCmd :1047
# Step 1 (implement; lease-free)
edit RPC.cpp (include + gate/descriptor/reset + SendCmd hunk)
edit System.cpp (:441 emitDrop args)
edit ps2xTest/src/ps2_runtime_kernel_tests.cpp (include + forward decl + 3 tests)
find $R ... -name "._*" -delete (source dirs); git diff verify (mine only)
(mid-session: HEAD moved 69bb1ff -> bfa0213 -> 4326926, P11+P9; verified
 my 3 files untouched by them, diffs intact)
cmake --build /tmp/p1-link/runtime --target ps2x_tests ps2EntryRunner -j4 (exit 0)
shasum both binaries (daf0b63f / 5878ad69)
cd $R && ps2x_tests (431/431/0) + by-name handshake grep (3/3 pass)
sed /tmp/p1ab-boot{1,2}.py -> /tmp/p1ac-boot{1,2}.py (docstring + LOG only)
# Step 2 (boots; lease P1ac held 03:34:10Z-03:37:28Z only)
pre-claim checks (lease absent x2; pgrep exit 1; shasum 5878ad69; ISO + ELF sizes)
printf 'P1ac' > lease + >> p1ac-waits.log; python3 /tmp/p1ac-boot1.py (90 s, SIGTERM rc=-15)
spot greps (receipt/census/override/cf0); cat lease (P1ac); pgrep (exit 1)
python3 /tmp/p1ac-boot2.py (90 s, SIGTERM rc=-15)
>> p1ac-waits.log (release line); rm lease; verify absent; pgrep exit 1
# Step 2 (analysis, lease released)
(write /tmp/p1ac-ladder.py; same-pattern rungs x3: P26-boot1 + both P1ac boots)
(write /tmp/p1ac-park.py: thread pcs, stub profile, BIND rows, SIF loads)
(write /tmp/p1ac-steady.py: stub sums, t1 pcs, frames, CD, creates)
(write /tmp/p1ac-decode.py: ELF windows + CSV ranges; +0x1000 map fix, rerun)
reads: $O/sub_0031AAF0 + sub_00394ED0 + sub_00362DE8 + sub_0040C028-family +
  sub_00426D18 + TOML 426 map; ps2_log.txt enter/exit greps (6 functions)
# Step 3 (fork commits + push; lease released)
git add RPC.cpp + kernel_tests; verify staged; commit 6447d8b (trailer)
git add System.cpp; verify staged diff; commit 45da174 (trailer)
git fetch fork; rev-list HEAD...fork/ssx3 (2/0); pull --rebase (refused, dirty
  generated file — recorded §P27-3); git push fork ssx3 (4326926..45da174)
# Step 3 (this report; lease released)
(edit_file append Part 27 in 3 chunks + 2 row fixes)
git -C /Users/bradrichardson/dev/ssx3 add -f local/research/P1/REPORT.md
git -C /Users/bradrichardson/dev/ssx3 commit -m "[P1ac] ..." (trailer; NO push there)
```

Env delta boots vs boot-p1ab-1: none (scripts differ only in docstring
+ LOG name). Source delta: my 2 fork commits on `4326926` (+ the
P9/P11 confounders, §P27-3).

## P27-5. What I could not do

- Name the IOP announcer (carried from §P26-5; the fix confirms the
  contract — one-shot nonzero unblocks the thread past `0x2290E8` —
  without the module name).
- Decide bounded-vs-circular for the new main-thread park (the
  `sub_00394ED0` list-walk: 15,989 balanced calls, frozen dma/gif —
  needs a guest-memory trace over the walked list; follow-up brief
  material, with the sema-30 thread-3 park as its second row).
- Identify the outer loop above `sub_00362DE8` (the repeat driver for
  the 16k calls) — same follow-up.
- Decode the `0x3C45C0` `SendCmd` cid and the `0x1C`/`0x1D` arm
  semantics (carried from §P26-5, untouched).
- Run a 3rd boot (max 2 used; poll-exit + park + ladder all closed).
- Re-baseline the ladder against a P9/P10/P11-only binary (the
  mechanism-exclusive rows don't need it; the joint volume rows are
  marked as such in §P27-2e).
- Session wall time ≈ 03:05–03:50Z (~45 min), inside the 4 h box.

## Part 28 (P1ad): DIAGNOSIS — the `sub_00394ED0` park is a self-looped hash chain (`0x85aabc→self`): the HLE's SPR_FROM DMA completes without moving data, so `sub_00362CC8` re-inits reset the pool count but never re-zero the buckets; fix brief names the SPR transfer emulation

Brief `local/muse/prompts/P1ad.md`. DIAGNOSIS brief: 1 fork
commit (read-only diag probe) + 2 boots. Tables, no verdicts.
Stale-reading guard: Part 27 §P27-2b/c/d (the new park catalogue),
§P27-5 (the open items this brief owns), §P27-2e (ladder).
`W=/Volumes/Extreme SSD/ps2recomp-spike`, `R=$W/PS2Recomp` (fork,
branch `ssx3`), `O=$W/P1/output`,
`LOG=$W/P1/run/boot-p1ad-1.log`, `LOG2=$W/P1/run/boot-p1ad-2.log`,
`T1=$W/P1/run/ps2_log-p1ad-1.txt`, `T2=$W/P1/run/ps2_log-p1ad-2.txt`
(own copies; the shared `ps2_log.txt` had been overwritten by a
foreign run before this session, so P27's quoted trace counts are
cited, not re-read). File:line refs below are `$R`-relative unless
noted with `$O` (recompiled) or `$W/P1/run` (logs).

Headline receipts: 137 fresh `0x394ED0` dispatches per boot (all
`ra=0x363240`, one arena `a0=0x8095f0`, 63 `sub_00362DE8`
invocations × 63 `sub_00362CC8` re-inits); the last fresh call
(`n=136`) walks `head=0x85aabc` whose `next` is itself (slot 3
reused after a count reset onto a stale head). P27's "15,989
balanced calls" are 137 fresh + ~15.4–15.7k checkpoint slices of
the one stuck call. The buckets are re-zeroed only by an SPR_FROM
DMA that the HLE completes without moving a byte.

## P28-0. Lease record

| Event | Value |
|---|---|
| Lease at session start | Absent (`start 04:05:27Z` in waits log) |
| Waits log | `$W/P1/run/p1ad-waits.log` (6 lines: start, 3 waits, claim, release) |
| Waits | `wait1 04:09:57Z`, `wait2 04:17:20Z`, `wait3 04:23:21Z`, all `lease=M16 pgrep=1` (5-min polls per the brief) |
| Pre-claim checks (04:28:38Z) | Lease absent; `pgrep -x ps2EntryRunner` exit 1; binary `ead11aa1` (P1ad build); ISO 3005415424 B + ELF 3890784 B present |
| Claim | `printf 'P1ad\n' > /tmp/ssx3-host-lease` 04:28:38Z, immediately before boot 1 |
| Boot 1 | 90 s foreground, SIGTERM rc=-15, LOG 19,145 lines, 2,640,817 B; trace copied to T1 (109,147,867 B) |
| Boot 2 | 90 s foreground, SIGTERM rc=-15, LOG2 19,316 lines, 2,667,013 B; trace copied to T2 (109,264,534 B) |
| Release | 04:32:37Z, right after boot 2 (analysis needs no lease); verified absent; `pgrep -x` exit 1 |
| Rule switch (received post-boots, pre-commit) | P-lane boots now coordinate via `/tmp/ssx3-p-lane-lease` (M lane keeps `/tmp/ssx3-host-lease`). My boots ran 04:28–04:32Z under the host-lease rule; max 2 used, so no P-lane lease action taken. Throughput rows below are marked contended accordingly |
| `adb` | Not used |

## P28-1. Static evidence

### a. `sub_00394ED0` fully decoded (`$O/sub_00394ED0_0x394ed0.cpp`)

Hash-intern with move-to-front. `a0`=table base, `a1`=16-byte
key, `a2`=hash byte.

| Item | Decode (instr refs) |
|---|---|
| Buckets | 256 × u32 at `base+0x674A0+(a2&0xFF)*4` (`0x394ed0-e8`) |
| Walk | `t1`=link addr (head, then `node+0x14`); per node a 4-word memcmp vs key (`0x394f08-30`, bounded: counter `t0` exits at 4) |
| Match | Returns node; if not head, unlinks + pushes front (`0x394f3c-70`) |
| Miss-to-end | `next==0` falls to the insert path (`0x394f78-84`) |
| Insert | Slot = `base+0x51484+24*count`, `count` at `base+0x51480` (`0x394f84-b4`); copies 20 key bytes, `new->next=old head`, pushes front, returns new node |
| Intra-call exits | Match / full-walk-miss-insert only — the walk is infinite iff the chain has a cycle (finite memory) |

### b. Outer loop above `sub_00362DE8` (`$O/sub_00362DE8_0x362de8.cpp`)

`s6`=`a0`=arena base. Two phases; both call `0x394ED0` once per
record (`0x362f68` phase 1, `0x363238` phase 2, observed
`ra=0x363240`).

| Item | Decode |
|---|---|
| Phase 1 (`0x362e98-363190`) | Outer `a1=1..(*(s6)/v0)`, inner `s7=v0` records of `0x80` B (`s1+=0x80`) |
| Phase 2 (`0x363198-363454`) | `s7=0; while (s7 < *(s6)-spC*sp10)` = the remainder `*(s6) mod v0`; `s1+=0x80`, `s7++` per iter |
| `*(s6)` mutated in-loop? | NO (loop-invariant bound): `0x394ED0` touches buckets/pool only; `0x395000` is lookup + move-to-front (§c); `0x364240` has no WRITEs/calls (pure); `0x362978` writes only the `s5` node + HW-ish `sd`; own body writes `fp+0x7494`/`s4+0x7CA4` counters only |
| Caller chain | `0x363238 ← sub_00362DE8 ← sub_00363490:0x3634cc (a0 passthrough) ← sub_00376938:0x377b14 (a0=*(s3+0x18F0), heap)`; after return main `WaitSema(*(s3+0x5ACC))` at `0x377b1c` |

### c. Sibling routines (same arena / same init)

| Function | Role (offsets are `base`-relative) |
|---|---|
| `sub_00395000` | Pure lookup + move-to-front over buckets `+0x678A0`, links `+0x1C`, 3-key match; NEVER inserts (returns 0 on miss). Same latent stale-bucket exposure as `0x394ED0` |
| `sub_00362CC8` | THE INIT (called by `0x3629B8` + `0x376938:0x377c00`): `*(s0)=0`, fp-count `+0x57494=0`, pool `+0x51480=*(+0x57484)` preset; `s4`-array count `+0x67CA4=0`. Bucket arrays re-zeroed ONLY via two `0x38F738` calls (`+0x674A0`/`+0x678A0`, `0x400`, `2`); tail has no bucket stores (surveyed `0x362d68`-end) |
| `sub_0038F738` | `sub_00371DD8(ctx, dst, 64, 2)`: SPR_FROM DMA, 64 quads (`0x400` B = one bucket array) |
| `sub_00371DD8` | Programs SPR_FROM `CHCR=0x1000D000` (`STR`), `MADR=0x1000D010=dst`, `QWC=0x1000D020=64`, `SADR=0x1000D080=*(gp+0x2A94)&0x3FFF`, then polls `D000&0x100` to clear |
| `sub_003E6448` | Plain CPU memset (`sb/sh/sw` ladder, no calls): `362CC8` zeroes the DMA source `(*(gp+0x2A94), 0, 0x400)` — works under HLE (no MMIO involved) |
| `*(gp+0x2A94)` | `= 0x70000000+(v0<<4)` (`$O/sub_0038F300_0x38f300.cpp:0x38f430-3c`): scratchpad + small offset. SADR is a BYTE offset (14-bit field spans exactly the 16 KB scratchpad) |
| `sub_004247D8` | Cache writeback over the bucket ranges (mfc0/CU0/`0x42C078`/line-align), NOT a clearer |

### d. Sema-30 chain map (`$O/sub_0031AAF0_0x31aaf0.cpp` lump)

| Role | Site | Shape |
|---|---|---|
| Creator | `sub_0031A6B8:0x31a7c0`, `ra=0x31a7c8`, tid=1 | `CreateSema(max=1024, init=0)` → id 30 (`:259` boot-p1ac-1) |
| Consumer | `0x31ac60` loop, tid=3 | `WaitSema(*(s0+0x4044))` (`ra=0x31aca4`); flag `*(s1+0x20)`; work item `*(s0+0x4048)` dispatched via JALR |
| Producer | `0x31acd8`, tid=1 | `*(v1+0x4048)=a1; SignalSema(*(v1+0x4044))` (`ra=0x31acf4`) |
| Poller | `0x31ad00` | `*(a0+0x10000+0x4048) < 1` |
| Boot-1 events (P1ac) | `:643,:645,:646,:694,:6850,:6897,:7099` | 3 signals / 4 waits; last signal `:6897`, terminal park `:7099`; 12k subsequent lines carry no sema-30 traffic |
| Sema-36 (thread 6, catalogue) | Created tid=3 `ra=0x3c1e04` (`:5121`, max=1 init=0); waiter tid=6 `ra=0x3c19f0` (`:5123`); ZERO signals all boot — parked from birth, separate chain |

### e. Pre-boot proof the walk is circular (P1ac logs + scheduler source)

| # | Evidence | Receipt |
|---|---|---|
| 1 | Park-phase histograms are COMPLETE and silent | P1ac blocks 2–16: `distinct=13` (< 30 print cap, nothing cut); all 13 = INTC/sema-pump targets; zero dispatches to `0x394ED0`/`0x362DE8`/`0x395000` for 75 s |
| 2 | Entry-checkpoint cannot hide 14k main-thread dispatches | `EeScheduler::checkpointDue` charges global `m_eeCycle`, global slice/pending (`EeScheduler.cpp:648-680`); pump-thread dispatches in the SAME blocks proceed and are counted — main's would be too |
| 3 | Scope-guard exits include checkpoint slices | `PS_LOG_ENTRY` (`ps2_log.h:223-226`) logs exit on every C++ return, incl. `eeCheckpointDue()` unwinds; resume re-invokes only the yielding function (`EeScheduler.cpp:574` `lookupFunction(context.pc)`), never re-dispatching |
| 4 | Therefore | Balanced trace pairs + zero fresh dispatches + pc sampled in the walk = ONE stuck call; infinite walk over finite memory = CYCLE. Boots confirmed it directly (§P28-2) |
| 5 | P27 wording superseded | "15,989 balanced (repeat-called, returns each call)" mixed fresh calls with slices; "outer loop driving 16k calls" is 63 small invocations (137 fresh) + one hung call |

### f. HLE mechanism: SPR DMA completes without moving data

| # | Evidence | Receipt |
|---|---|---|
| 1 | No SPR transfer emulation exists | No `SADR`/`0xD080`/`SPR_FROM`/`SPR_TO` handling anywhere in `ps2xRuntime/src/lib/`; `writeIORegister` stores channel regs; only VIF0/VIF1/GIF (`0x10008000/0x10009000/0x1000A000`) get transfer emulation (`ps2_memory.cpp:1298-1420`) |
| 2 | Status auto-completes | `readIORegister` clears `STR` on ANY channel-CHCR read (`ps2_memory.cpp:2248-2256`: `(address&0xFF)==0x00` → `& ~0x100u`), incl. `0x1000D000` — the game observes "DMA done" with zero bytes moved |
| 3 | CPU paths around it work | memset `0x3E6448` is pure CPU (source IS zeroed); scratchpad is a real zero-init 16 KB store (`ps2_memory.cpp:366-369`); game reads scratchpad records fine |

### g. Candidate causes (for / against, with receipts)

| Candidate | For | Against → status |
|---|---|---|
| C4 slot-reuse + stale head → self-loop | Pool resets 4→3/5→3 with heads intact (n=2, n=105…); `CYCLE@0x85aabc` at entry (n=111…); slot-3 arithmetics exact (§P28-2) | — → CONFIRMED mechanism |
| C6 garbage/unwritten heads | Would also cycle (random-graph) | Every bucket's first touch is NULL (n=0,102,103,104,106,109,133) → arena fresh-zero → REFUTED |
| C7 pool overflow (≥1025 inserts) | Tight arena packing (pools/buckets/arrays adjacent) | Pool never exceeds 5 → REFUTED |
| C5 s1-record/pool overlap | Would corrupt chains | s1=`0x70000000+` (scratchpad), pool=`0x85AA74+` (RAM) → REFUTED |
| Broken-HLE-memset | Would leave buckets stale | `0x3E6448` is pure CPU, no MMIO → REFUTED |
| SPR_FROM no-data (host) | Stale heads across 63 inits + §f rows 1–2 | — → CONFIRMED root cause |
| SPR_TO broken (records) | Same missing emulation as FROM | Record bytes vary per round (fits working-TO or varying-memset-window) → UNRESOLVED, co-fix recommended (§P28-3) |

## P28-1append. Exact commands (static phase)

```
W="/Volumes/Extreme SSD/ps2recomp-spike"; O="$W/P1/output"; R="$W/PS2Recomp"
# decode: cat $O/sub_00394ED0* $O/sub_00395000* ; sed windows of sub_00362DE8/
#   sub_0031AAF0/sub_00376938/sub_0038F4F8/sub_0038F6A8/sub_0038F7B0/
#   sub_00362CC8/sub_004247D8/sub_0038F738/sub_00371DD8/sub_003E6448/
#   sub_0038F460/sub_00371D10/sub_0031A6B8/sub_003629B8
# callers: grep -l func_362DE8/func_362CC8/func_3629B8/func_395000 $O/*.cpp
# offsets: grep -h "ori.*0x74[Aa]0" $O/sub_*.cpp  # only 394ED0 + 362CC8
# logs: /tmp/p1ad-mine1.py (sema30/drops/RPC/ticks), stub-block dumps,
#   scheduler reads (EeScheduler.cpp:574,648-680; ps2_runtime.cpp:1565+,
#   2248-2256,2821; ps2_log.h:223-226; Stubs/DMA.cpp; ps2_memory.h:29-31)
```

## P28-2. Boots + probe + census

Env = P1ac scripts verbatim + `PS2X_DIAG_394ED0=1`
(`diff /tmp/p1ac-boot1.py /tmp/p1ad-boot1.py`: docstring + LOG
name + the one env line). Binary `ead11aa1` (P1ad probe build).
CWD `$W/P1/run` both boots.

### a. Fork diag (the one allowed file)

`ps2xRuntime/src/lib/ps2_runtime.cpp` +143, commit `5001830`
(pushed `da6a2d5..5001830`, `HEAD...fork/ssx3`=0/0 after).
Env-gated dispatch tap in the `diagDriverProbeEnabled` style:
one `[diag:394ed0]` line per FRESH guest dispatch to `0x394ED0`
(checkpoint resumes never re-dispatch, so the probe counts true
calls): `n ra src a0 a1 a2 total pool head key[4] chain[8 hops]`
with `NULL`/`WILD`/`CYCLE@` termination. Read-only (GPRs +
range-checked masked RAM reads; scratchpad addrs print WILD by
design — see §P28-5), capped at 20000 lines, off by default.
Justification (brief's "otherwise unattributable" bar): the
arena base is a dynamic heap object (`*(s3+0x18F0)`); no existing
facility logs guest regs/memory at dynamic addresses
(`PS2X_DIAG_WATCH` needs static addrs); static analysis
exhausted at "bounded loop, unknown bound / circular chain,
unknown maker". No new tests (diag-only, env-off default; the
driver-entry probe it mirrors has none either); suite stays
431/431/0 (§P28-3 binaries).

### b. Probe summary (both boots; guest bytes identical)

| Item | Boot 1 | Boot 2 |
|---|---|---|
| Probe lines | 137 (`n=0..136`, `:661`–`:8111`) | 137 (`:661`–`:8110`-area) |
| `ra` / `src` | 137/137 `0x363240` / `0x363238` (phase-2 site; phase 1 never calls it in this boot) | Same |
| `a0` (arena) | `0x8095f0` all 137 (ONE reused arena) | Same |
| `total` (`*(s6)`) | `0x2` (n=0..101) → `0x3` (n=102..136) | Same |
| `pool` | `0x3`×119, `0x4`×12, `0x5`×6; 12 drops (re-inits), e.g. idx 2,105,108,…,129 | Same |
| `a1` (records) | `0x70000000/80(/100)` — scratchpad ⇒ `key=[WILD×4]` (probe range gate) | Same |
| First touches | NULL at n=0 (bkt 0), 102 (bkt 2), 103 (`0x15`), 104 (`0x23`), 106 (`0xcb`), 109 (`0x60`), 133 (`0x6b`) | Same |
| First `CYCLE@` | n=111 `:7904` (`head=0x85aabc`, self) | n=111 `:7903` |
| Cycle flicker | Broken n=130 (NULL-head insert at slot 3), re-created n=132 (mismatch insert onto stale head) | Same |
| `CYCLE@` lines | 6 (n=111,117,123,129,135 + n=136) | 6, same n |
| n=135 / n=136 | n=135 key matched → returned; n=136 (`a1=0x70000080`,`a2=0x0`) mismatched → STUCK (last fresh call; zero dispatches after) | Same, byte-identical lines |
| Interleave truncations | 3 (`n=13,105,130`), tails recovered as orphans (`:958`,`:7851`,`:8059`) | 3 (`n=2,18,73`), same states intact in boot 1 |
| Cap line | None (137 ≪ 20000) | None |

Slot arithmetics: pool base `0x8095f0+0x51484=0x85AA74`;
slot 3 = `0x85AA74+24*3` = **`0x85AABC`** = the cycle node.
Insert rule `new->next = stale head` + `head == slot` ⇒ self-loop.
n=0 inserts slot 3 (pool 3→4); first re-init (→n=2, pool→3)
orphans the head; n=132's mismatch-insert rewrites slot 3 with
`next=self`; n=136 walks it forever.

### c. Trace decomposition (own T1/T2)

| Function | Boot 1 enter/exit | Boot 2 enter/exit | Reading |
|---|---|---|---|
| `sub_00394ED0` | 15,576 / 15,576 | 15,837 / 15,837 | 137 fresh + ~15.4–15.7k slices of n=136 (slice count varies with wall timing, as expected) |
| `sub_00362DE8` | 63 / 63 | 63 / 63 | 62 normal returns + 1 checkpoint-unwind exit; resumes bypass it (go straight to `0x394ED0`) |
| `sub_00362CC8` | 63 / 63 | 63 / 63 | One re-init per invocation — init→use pairing confirmed |
| `sub_00395000` | 113 / 113 | 113 / 113 | Second table healthy this boot (latent same-defect noted §P28-3) |

### d. Census + sema + RPC (both boots)

| Item | Boot 1 | Boot 2 |
|---|---|---|
| `[drop]` | 6× same early `GetEntryAddress` site `:68-73` | 6× same `:69-74` (+1-line frame shift, same as P1ac b1-vs-b2) |
| Sema-30 events | 7-shape `:643,645,646,696,7193,7244,7446` (3 sig / 4 wait, ends parked) | 7-shape `:643,645,646,696,7120,7172,7374` |
| Unhandled RPC | 4 sightings, same sids/bytes as P1ac (table below) | Same 4 |
| `SendCmd` / handshake | 1 same-bytes `cid=0x80000001` `:1078` / 1 `:1077` | Same `:1078`/`:1077` |
| `0x3C45C0` | 0 sightings — P27-5 item (d) closed for this boot | 0 |
| Creates | 37 (max id 37) | 37 |

Unhandled-RPC shape table (boot 1 lines; boot 2 same bytes):

| # | sid | rpc | pc | send/recv | sendBytes head |
|---|---|---|---|---|---|
| 1 `:701` | `0x80000006` | `0xff` | `0x42b0e8` | `0x0/0`, `0x52f080/4` | `[]` |
| 2 `:1082` | `0x237` | `0x0` | `0x3f6a04` | `0x526080/128`, `0x526140/128` | `C0 61 52 20 …` |
| 3 `:1088` | `0x80000211` | `0x1` | `0x40c34c` | `0x529100/16`, `0x529140/144` | all `00` |
| 4 `:5387` | `0x534e44` | `0x0` | `0x3c0bc4` | `0x50ad00/20`, `0x0/0` | `03 03 08 00 …` |

### e. Ladder vs P27-boot1 (regression check, not the deliverable)

P27-boot1: 19,150 lines / 2,643,773 B / 17 stub blocks.

| Rung | P27-boot1 | P1ad-boot1 | P1ad-boot2 |
|---|---|---|---|
| Lines / bytes | 19,150 / 2,643,773 | 19,145 / 2,640,817 | 19,316 / 2,667,013 |
| Stub / thread blocks | 17 / 17 | 17 / 17 | 17 / 17 |
| Park onset (first all-13 stub block) | block 2 | block 5 (wall-clock boundaries; same guest point n=136) | block 5 (b2 pre-park distinct: 682/244/170/620/229) |
| Thread-1 | RUNNING walk ×14 (+1 WAIT, 2 transients) | walk ×12 (+4 WAIT, 1 null) | walk ×12 (+4 WAIT, 1 null) |
| Thread-3 | WAIT 30 ×17 | WAIT ×13–14 + early game-code transients | WAIT ×14 + transients |
| Thread-6 | WAIT 36 ×17 | WAIT ×14 (absent from 3 early blocks; created later in wall-time) | WAIT ×14 |
| 29-handshake w/s | 65 / 65 | 64 / 64 | 64 / 64 |
| 30-handshake w/s | 4 / 3 (ends parked) | 4 / 3 (ends parked) | 4 / 3 (ends parked) |
| 31-handshake w/s | 5287 / 5286 | 5210 / 5210 | 5297 / 5297 |
| Creates / `-1` waits | 37 / 0 | 37 / 0 | 37 / 0 |
| Driver-entry | 98 | 98 | 98 |
| `[drop]` census | 6× same site + args | 6× same | 6× same |
| SendCmd / handshake | 1 + 1 | 1 + 1, same bytes | 1 + 1 |
| `0x394ED0` trace | 15,989 / 15,989 | 15,576 / 15,576 (= 137 + 15,439 slices) | 15,837 / 15,837 |
| `0x362DE8`/`0x362CC8` trace | (not quoted) | 63 / 63 | 63 / 63 |
| GS kicks / copy / gif / drawing=1 | 96 / 64 / 48 / 96 | 96 / 64 / 48 / 96 (exact) | exact |
| `run:tick` | 19–20 ticks, pc walk-family, dma/gif 1166/65 frozen | 13 ticks (host render loop emits 1/120 frames; 17 fps vs 25 fps = host-load artifact), same frozen dma/gif | 13 ticks |
| CD `lbn=` / first-last | 810 / `0x10`→`0x4311f` | 810 / identical | 810 / identical |
| SIF loads | 21 | 21 | 21 |
| Dormant / start-thread | 121 / 5 | 121 / 5 | 121 / 5 |
| Missing / `No exact` | 1 / 0 (JALR `0x2322d4→0x395730`) | 1 / 0, same bytes | same |
| Presented frame | None | None | None |
| Crash / FATAL | 0 / 0 | 0 / 0 | 0 / 0 |

CONTENDED (wall-throughput) rows — M-lane runs may coincide
under the split-lease rule, so treat as host-load-sensitive, not
regressions: park-onset block, `run:tick` counts, `0x394ED0`
slice counts, sema-31 w/s, stub `distinct` values, and
thread-sample mixes. Guest-event rows (probe, census, sema-30
shape, CD/SIF/GS/RPC) are deterministic and unaffected.

## P28-3. Attribution + named fix brief

### a. Cause chain (each link receipted)

| # | Link | Receipt |
|---|---|---|
| 1 | HLE completes SPR_FROM DMA without moving data | §P28-1f (no transfer emu; STR auto-clear on CHCR read) |
| 2 | `0x362CC8` re-inits reset counts but buckets stay stale | 63 inits, pool ∈ {3,4,5} with 12+ resets; heads persist across resets (e.g. `0x85aabc` n=1→n=136) |
| 3 | Post-reset inserts reuse live node slots | n=132 (pool 3) rewrites slot 3 = `0x85aabc` while two buckets still head at it |
| 4 | Insert rule `new->next = stale head` + `head == slot` ⇒ SELF-LOOP | `CYCLE@0x85aabc` at entry from n=111; flickers with reuse (break n=130, re-create n=132) |
| 5 | First key-mismatch in an aliased bucket walks forever | n=135 matched → returned; n=136 mismatched → last fresh call ever (137 total both boots) |
| 6 | Main frozen ⟹ sema-30's 4th signal never sent | 3 signals only (`:643`,`:694`-area,`:6897`-area; tid=1 `ra=0x31acf4`); terminal thread-3 park needs one more |
| 7 | Thread 3 correctly parked; DMAs idle; no frame | `WAIT 30 @0x423de8`; dma/gif frozen 1166/65; GS row exact-but-static |

WHY the game can't proceed: main is the only producer-side
driver past this point — it must return from `0x362DE8` (hence
`0x376938`) to reach the next `0x31acd8` signal and the post-load
phases. A single guest call never returning wedges the whole
boot; the scheduler, pumps, and other threads are all healthy
(sema-31 balanced 5210/5210 and 5297/5297).

### b. Exact fix brief (the deliverable)

Title: `P1ae — Emulate SPR normal-mode DMA data movement
(SPR_FROM first); unstick the SSX3 hash-table re-init`.

| Item | Content |
|---|---|
| File | `ps2xRuntime/src/lib/ps2_memory.cpp` (one file; mirror the VIF0/VIF1/GIF channel section ~:1298-1420) |
| Hunk P0 (the hang) | On `CHCR` STR write to `0x1000D000` (SPR_FROM) with `MOD`=NORMAL: synchronously copy `QWC` quads (16 B each) from scratchpad host store + `SADR` to RAM `MADR&0x01FFFFFF`; then update `MADR`/`QWC`/`SADR`, clear `STR`, set the channel's `D_STAT` CIS. Observed op: `MADR`=bucket array, `QWC`=64, `SADR`=scratchpad byte offset (`*(gp+0x2A94)&0x3FFF`; byte-addressed per §P28-1c), `CHCR`=`0x100` |
| Hunk P1 (same area, recommended co-fix) | SPR_TO (`0x1000D400`) mirror (RAM→scratchpad): same missing emulation feeds the s1 records; record bytes are currently untrustworthy (fits working-TO or varying-memset-window — §P28-1g). Fixing TO changes all hashes/table contents (expected, hardware-faithful); resolving which model holds is part of the brief (scratchpad dump or hash comparison) |
| Keep the auto-clear? | The STR auto-clear-on-read (`:2248-2256`) stays valid once transfers run synchronously (status already clear at first poll); keep, do not re-time |
| Tests | New `PS2Memory` unit test(s) beside the existing memory tests: program `MADR`/`QWC`/`SADR`+`STR` for FROM (and TO), assert bytes landed + regs updated + `STR` clear + `D_STAT` set; suite must stay 431+/0 |
| Proof boots (2 × 90 s) | Reuse `/tmp/p1ad-boot{1,2}.py` + `PS2X_DIAG_394ED0=1`: (1) probe shows `head=0x0` after every re-init and `n` advancing past 136 with pool cycling cleanly; (2) a 4th sema-30 signal appears and thread 3 leaves `WAIT 30`; (3) main leaves `0x394ED0` (park gone); (4) census/drops/RPC/ladder show no other face |
| Probe disposition | Keep `5001830` (env-off, zero-cost) or remove in the fix commit — either is fine; the proof above needs it if kept off-by-default |
| Second-table note | `0x395000` shares the stale-bucket exposure (113/113 healthy this boot by luck: lookup-only + no aliasing hit yet); the same DMA fix cures it — no separate hunk |
| Out of scope | SIF/RPC sightings (§P28-2d), GetEntryAddress drops, sema-36 chain — all unchanged, none blocking |

### c. Binaries and commits

| Item | Value |
|---|---|
| BEFORE `ps2x_tests` / runner | `daf0b63f…` / `5878ad69…` (= P27 AFTER pair; suite 431/431/0, CWD `$R`) |
| AFTER `ps2x_tests` / runner | `4b2625bc…` / `ead11aa1…` (full shas in §P28-4 log); suite 431/431/0, no new tests (§P28-2a rationale) |
| Build | `cmake --build /tmp/p1-link/runtime --target ps2x_tests ps2EntryRunner -j4`, exit 0; same `ld` duplicate-library warning as P1ac (observed as-is) |
| Tree note | P12 `da6a2d5` (kernel-true KE_ERROR sema paths) landed + pushed mid-session AFTER my build (00:14 EDT): boots ran `45da174`+diag; my commit sits on `da6a2d5`; no interaction (all sema ids valid, census unchanged) |
| Fork commit | `5001830` Diag: SPR_FROM-blind park probe for SSX3 0x394ED0 hash walk (P1ad) — `ps2_runtime.cpp` +143 only, trailer `Orchestrated-By: Muse Code` |
| Push | `git push fork ssx3` → `da6a2d5..5001830`, exit 0; `HEAD...fork/ssx3` = 0/0 after; integrated no foreign history |
| Pull --rebase | Refused (pre-existing unstaged generated `runner/register_functions.cpp`, mtime 22:50 EDT, never staged/committed/touched — same as P1ac); behind 0, nothing to replay; no foreign rebase conflict |
| `._*` | Purged under `ps2xRuntime/src` + `include` before staging (4 sidecars); named `git add` of the one file only |

## P28-4. Exact commands

From `$R` (fork) unless noted; `$W`, `LOG`/`LOG2`, `T1`/`T2` as above:

```
# Step 0 (context; lease-free)
re-read REPORT Part 27 (full) + brief local/muse/prompts/P1ad.md
cat /tmp/ssx3-host-lease (absent at start); git -C $R status/log (45da174 + generated-file mod)
# Step 1 (static; lease-free; details §P28-1append)
decode $O functions (394ED0/362DE8/395000/362CC8/38F738/371DD8/3E6448/4247D8/
  38F460/371D10/31AAF0/31A6B8/3629B8/376938-windows) + callers + ori-74A0 users
/tmp/p1ad-mine1.py over boot-p1ac-{1,2}.log (sema30/drops/RPC/ticks/creates)
stub-block dumps (blocks 0/1/2/16) + scheduler reads (checkpoint/slice/resume/guard)
# Step 1 (diag; lease-free)
edit ps2xRuntime/src/lib/ps2_runtime.cpp (+143: gate/read/word/emit + dispatch hook)
shasum BEFORE pair; cd $R && ps2x_tests (431/431/0)
cmake --build /tmp/p1-link/runtime --target ps2x_tests ps2EntryRunner -j4 (exit 0)
shasum AFTER pair: runner ead11aa17e3f2ba10d5904138e6aeeb8a682960dc1f3c4e17e47048b8904f32f
  tests 4b2625bc86d50396e6a8317841b881edff4de173a0db6a8d3fb4fbd86672bf53
cd $R && ps2x_tests (431/431/0)
sed /tmp/p1ac-boot{1,2}.py -> /tmp/p1ad-boot{1,2}.py (docstring + LOG + PS2X_DIAG_394ED0=1)
write /tmp/p1ad-mine2.py (probe/sema/census miner)
# Step 2 (boots; lease P1ad held 04:28:38Z-04:32:37Z only)
pre-claim checks (lease absent; pgrep exit 1; shasum ead11aa1; ISO + ELF sizes)
printf 'P1ad' > lease + >> p1ad-waits.log; python3 /tmp/p1ad-boot1.py (90 s, SIGTERM rc=-15)
cp ps2_log.txt ps2_log-p1ad-1.txt; spot greps (137 probe, n=136 CYCLE tail)
cat lease (P1ad); pgrep (exit 1); python3 /tmp/p1ad-boot2.py (90 s, SIGTERM rc=-15)
cp ps2_log.txt ps2_log-p1ad-2.txt; >> p1ad-waits.log (release); rm lease; verify absent
# Step 2 (analysis, lease released)
/tmp/p1ad-mine2.py both boots; probe determinism diff (131 clean-identical + 3+3 interleaves)
trace counts (394ED0/362DE8/362CC8/395000 × T1/T2); ladder rows; orphan-fragment recovery
HLE reads (Stubs/DMA.cpp; ps2_memory.cpp writeIO/readIO/channel sections; scratchpad store)
# Step 3 (fork commit + push; lease released)
find ._*-delete (src+include); git add ps2xRuntime/src/lib/ps2_runtime.cpp (named, verified)
commit 5001830 (trailer); fetch fork; rev-list (1/0); pull --rebase (refused, recorded)
push fork ssx3 (da6a2d5..5001830); rev-list 0/0
# Step 3 (this report; lease released)
(edit_file append Part 28 in 3 chunks + 6 row fixes)
git -C /Users/bradrichardson/dev/ssx3 add -f local/research/P1/REPORT.md
git -C /Users/bradrichardson/dev/ssx3 commit -m "[P1ad] ..." (trailer; NO push there)
```

Env delta boots vs boot-p1ac-1: `+PS2X_DIAG_394ED0=1` only.
Source delta: my 1 fork commit on `da6a2d5` (boots ran
`45da174`+diag; P12 landed between build and commit, §P28-3c).

## P28-5. What I could not do

- Read scratchpad key bytes: `a1` points at `0x70000000+` and the
  probe prints `key=[WILD×4]` by its RAM-only range gate (a
  masked read would alias RAM — deliberately refused). The cycle
  verdict never needed keys (chain pointers suffice). Two-line
  probe extension for the fix brief if keys become relevant:
  branch `diag394Ed0Read` on `ps2IsScratchpadAddress` and read
  via `ps2GetScratchpadHostPtr()+ps2ScratchpadOffset`.
- Settle SPR_TO's status (working vs varying-memset-window —
  §P28-1g): both models fit the per-round record variation, and
  the fix brief resolves it empirically. No boot left to probe it
  (max 2 used).
- Name the IOP announcer / decode `0x3C45C0`'s `0x1C`/`0x1D` arm
  semantics (carried from §P26-5/§P27-5; `0x3C45C0` had 0
  sightings in both P1ad boots).
- Run a 3rd boot (max 2 used; probe + repro + ladder all closed).
- Avoid 3 `[frame:upload]` interleave truncations per boot log
  (stdout/stderr share one fd; positions jitter). All tails
  recovered via orphan fragments; every truncated line duplicates
  a state intact in the other boot. A `2>`-split or line-buffered
  emit would end it (not my call inside the box).
- Re-baseline against a P9/P10/P11/P12-only binary (same
  reasoning as §P27-5: the mechanism rows — probe, slot
  arithmetics, DMA gap — are exclusive to this diagnosis).
- Session wall time ≈ 04:05–04:48Z (~45 min incl. ~19 min M16
  lease waits), inside the 4 h box.

---

## Part 29 (P1af): FIX — SPR normal-mode DMA data movement emulated (FROM + TO co-fix); the `sub_00394ED0` park is gone (104k balanced calls, 0 cycles), main RUNNING at 90 s with no new park; the 4th sema-30 signal stays downstream of the 90 s window

Brief `local/muse/prompts/P1af.md`. FIX brief implementing
§P28-3b (P0 SPR_FROM + P1 SPR_TO co-fix): 1 fork commit (2
files) + 2 boots. Tables, no verdicts. Stale-reading guard:
Part 28 §P28-1f/g (the HLE gap + candidate table), §P28-2b
(probe proof), §P28-3b (this brief's exact spec).
`W=/Volumes/Extreme SSD/ps2recomp-spike`, `R=$W/PS2Recomp` (fork,
branch `ssx3`), `O=$W/P1/output`,
`LOG=$W/P1/run/boot-p1af-1.log`, `LOG2=$W/P1/run/boot-p1af-2.log`,
`T1=$W/P1/run/ps2_log-p1af-1.txt`, `T2=$W/P1/run/ps2_log-p1af-2.txt`
(own copies). File:line refs are `$R`-relative unless noted.

Headline receipts: probe hit its 20000-line cap in both boots
with ZERO `CYCLE@` (n=0..19999, `head=0x0` after every re-init,
pool cycling 3→4→3…); traces show 104,442/105,582 balanced
`0x394ED0` pairs, 5,289/5,346 balanced `0x362DE8` invocations
(every invocation RETURNS — vs 63 + 1 hung in P1ad), and
99,153/100,236 balanced `0x395000` pairs. Stub blocks hold 222
distinct in ALL blocks 2–16 (no all-13 park phase anywhere);
thread 1 is RUNNING game code (`0x39b72c`) at end of boot;
`dma`/`gif` tick counters advance (22k→171k / 641→4674, were
frozen 1166/65). Sema-30 stays 3 signals / 4 waits ending parked
— the predicted 4th signal is downstream of the still-running
hash phase, not reached inside 90 s. TO status resolved: record
bytes are TO-fed (identical record addresses hash differently
once TO moves data — "working TO" refuted). No new park; nothing
else changed face (drops/RPC/CD/SIF/GS/creates/driver/missing all
exact).

## P29-0. Lease record

| Event | Value |
|---|---|
| Lease at session start | `/tmp/ssx3-p-lane-lease` absent |
| Waits log | `$W/P1/run/p1af-waits.log` (3 lines: start, claim, release) |
| Waits | None (no foreign P-lane holder all session; no polls needed) |
| Pre-claim checks (04:57:33Z) | Lease absent; `pgrep -x ps2EntryRunner` exit 1; binary `40467623` (P1af build); ISO 3005415424 B + ELF 3890784 B present |
| Claim | `printf 'P1af\n' > /tmp/ssx3-p-lane-lease` 04:57:33Z, immediately before boot 1 |
| Boot 1 | 90 s foreground, SIGTERM rc=-15, LOG 207,189 lines, 36,650,891 B; trace copied to T1 (572,136,194 B) |
| Boot 2 | 90 s foreground, SIGTERM rc=-15, LOG2 208,858 lines, 36,778,835 B; trace copied to T2 (577,260,368 B) |
| Release | 05:00:57Z, right after boot 2 (analysis needs no lease); verified absent; `pgrep -x` exit 1 |
| Lane rule | P-lane lease held for boots only; builds/analysis lease-free; `adb` not used |

## P29-1. Diff + BEFORE/AFTER + tests

### a. Fork diff (2 files, +142/−0, all mine — verified by review)

`ps2xRuntime/src/lib/ps2_memory.cpp` +58: inside the CHCR
STR-write handler (`writeIORegister`, after the VIF0/VIF1/GIF
section), a `channelBase == 0x1000D000u ‖ 0x1000D400u` block.
On `MOD`=NORMAL with live stores: synchronously copy `QWC`
quads (16 B each) SPR→RAM (FROM) or RAM→SPR (TO) with
32 MB / 16 KB wraparound chunking (codebase chunk-loop style);
access RAM at `MADR&PS2_RAM_MASK` (=`&0x01FFFFFF`) and SPR at
`SADR&0x3FFF`; write back `MADR=MADR+bytes` (full 32-bit
increment, hardware-faithful — upper bits preserved),
`QWC=0`, `SADR=(SADR+bytes)&0x3FFF`, STR clear; raise `D_STAT`
CIS bit 8 (FROM) / 9 (TO) with the same status&mask summary-bit
logic as the GIF/VIF path; `queueCompletedDmacCause(8/9)`.
Decisions recorded: `QWC=0` completes trivially (regs/CIS, no
bytes — codebase `qwc>0` convention, no 64K-quad path);
non-normal MOD keeps previous behavior (falls through, STR set
until first read); STR auto-clear-on-read (`:2248-2256` area)
kept — already clear at first poll since completion is
synchronous; sits inside the existing `D_CTRL.DMAE` gate and
`dmaStartCount` increment. Observed game op covered:
`MADR`=bucket array, `QWC`=64, `SADR`=scratchpad byte offset,
`CHCR`=`0x100`.

`ps2xTest/src/ps2_memory_tests.cpp` +84: two `PS2Memory` cases
in the existing `MiniTest` style (byte-pattern loops +
register assertions, mirroring the neighboring DMAC tests):
"SPR_FROM normal-mode DMA copies scratchpad to RAM and
completes the channel" (64 quads, KSEG0-style MADR proving the
`&0x01FFFFFF` access path, asserts bytes + MADR increment +
`QWC=0` + SADR advance + STR clear + `D_STAT` bit 8) and
"SPR_TO normal-mode DMA copies RAM to scratchpad with SADR
wraparound" (4 quads across the 16 KB boundary, asserts wrapped
bytes + regs + `D_STAT` bit 9).

### b. BEFORE/AFTER receipts

| Item | BEFORE | AFTER |
|---|---|---|
| Suite (P1ad binary, pre-change) | 431 / 431 / 0 (CWD `$R`) | — |
| Suite + 2 new tests, no fix | 434 total, 432 pass, **2 fail** (both SPR cases: bytes-moved, MADR/QWC/SADR, D_STAT assertions fail; STR-clear sub-assertions pass via the read-side auto-clear — the HLE gap receipted exactly) | — |
| Suite + fix | — | **434 / 434 / 0** (CWD `$R`), both SPR cases pass |
| Face counts (AFTER) | — | CodeGenerator 56, ElfAnalyzerHeuristics 6, PS2GS 71, PS2IopSubsystem 7, **PS2Memory 47** (45 + my 2), PS2Recompiler 17, PS2RuntimeExpansion 31, PS2RuntimeIO 11, PS2RuntimeInterrupt 8, **PS2RuntimeKernel 38** (incl. P12 `da6a2d5`'s "unknown semaphore ids return KE_ERROR…" case, newly compiled into this build — the +1 peer test), PS2SifDma 16, PS2SifRpc 15, PS2VU0Math 44, PS2VU1 40, PadInput 12, R5900Decoder 15 |
| Total accounting | 431 + 1 (P12, newly compiled) + 2 (P1af) = 434, all green | — |

## P29-2. Boots + unstick proof + new park (none)

Env = P1ad scripts verbatim except LOG names
(`diff /tmp/p1ad-boot1.py /tmp/p1af-boot1.py`: docstring + LOG
only; `PS2X_DIAG_394ED0=1` kept). Binary `40467623` (P1af
build). CWD `$W/P1/run` both boots. Miner `/tmp/p1af-mine.py`
(+ per-n determinism join).

### a. Probe summary (both boots; guest bytes identical)

| Item | Boot 1 | Boot 2 |
|---|---|---|
| Probe lines | 20000 (`n=0..19999`, cap line at :62125) | 20000 (cap line, same) |
| `ra` / `src` / `a0` | 19999/19999 `0x363240` / `0x363238` / one arena `0x8095f0` (1 line is an interleave artifact) | 20000/20000/20000, single arena (no artifact) |
| `total` | `0x2` early → `0x14` late | Same |
| `pool` | Cycles 3→4→3… early; 1066 drops | Same, 1066 drops |
| `head` after every re-init | `0x0` (1065/1066 clean; 1 apparent miss is boot-1 line :24548, a `[frame:upload]` truncation of n=6182's pool field — boot 2's n=6182 is intact: pool=`0x3` head=`0x0`, and n=6183's live head is n=6182's own insert) | `0x0` at all 1066 drops, 0 bad |
| `CYCLE@` | 0 | 0 |
| NULL-head first touches | 3135 | 3136 |
| Distinct `a2` buckets | 5 | 5 |
| Determinism (per-n join, interleaves excluded) | 19,980 common n-values, **0 diffs**; 11 n-values clean-only-in-b1 / 9 clean-only-in-b2 (truncated in the other boot; positions jitter) | — |
| `[frame:upload]` splices | 128 | 128 |

### b. Trace decomposition (own T1/T2; the probe cap hides true counts)

| Function | Boot 1 enter/exit | Boot 2 enter/exit | Reading |
|---|---|---|---|
| `sub_00394ED0` | 104,442 / 104,442 | 105,582 / 105,582 | All fresh, all returned — the stuck call is gone (P1ad: 137 fresh + ~15.7k slices of one hung call) |
| `sub_00362DE8` | 5,289 / 5,289 | 5,346 / 5,346 | Every invocation RETURNS (P1ad: 63 + 1 checkpoint-unwind exit) |
| `sub_00362CC8` | 5,290 / 5,290 | 5,347 / 5,347 | Re-init per invocation + 1 (in-flight pairing at SIGTERM) |
| `sub_00395000` | 99,153 / 99,153 | 100,236 / 100,236 | Second table healthy at scale (P1ad: 113/113) — same DMA fix cures the latent exposure, no separate hunk |

Trace sizes: T1 16,103,012 lines / 572,136,194 B; T2
16,247,288 lines / 577,260,368 B (P1ad: 109 MB — the game
executes ~5× more calls instead of parking).

### c. TO status resolved (the P1 co-fix question)

Same game path (same `ra`/`src`/`a0`/`a1`/`total` sequences),
different record bytes once TO moves data:

| n | a1 (both boots, both eras) | P1ad `a2` | P1af `a2` | P1ad pool | P1af pool |
|---|---|---|---|---|---|
| 0,2,4,6 | `0x70000000` | `0x0` | `0x9d` | 3,3,3,3 | 3,3,3,3 |
| 1,3,5,7 | `0x70000080` | `0x0` | `0x26` | 4,3,3,3 | 4,4,4,4 |

"Working TO" is refuted (bytes change with TO emulation —
pre-fix TO delivered nothing, matching the code inspection that
no `0xD400` handling existed); pre-fix bytes were CPU-side
artifacts (zeros early; varying later per §P28-2b); post-fix
records are TO-delivered and the table functions correctly on
them across 104k calls (0 cycles). P1af pool dynamics show the
clean cycle (insert→re-init→insert) where P1ad's pool stuck at
3 on stale-bucket matches.

### d. Census + sema + RPC (both boots)

| Item | Boot 1 | Boot 2 |
|---|---|---|
| `[drop]` | 6× same early `GetEntryAddress` site `:68-73` | 6× same `:69-74` (+1-line frame shift, same as P1ad b1-vs-b2) |
| Sema-30 events | 7-shape `:643,645,646,706,6975,7025,7227` (3 sig / 4 wait, ends parked) | 7-shape `:644,646,647,707,6972,7022,7224` (same) |
| 4th sema-30 signal | NOT in window (main still in the hash phase — 5.3k `0x362DE8` invocations in 90 s, all returning; the signal is downstream of phase completion) | Same |
| Thread 3 at end | WAIT 30 (16/17 samples + 1 RUNNING transient) | WAIT 30 (16/17 + 1 transient) |
| Unhandled RPC | 4 sightings, same sids/bytes/pcs as P1ad | Same 4 |
| `SendCmd` / handshake | 1 same-bytes `cid=0x80000001` `:1052` / 1 | Same |
| `0x3C45C0` | 0 sightings (P28-5 item stays closed) | 0 |
| Creates | 37 (max id 37) | 37 |

### e. End of boot: NO new park

Last threads block (b1 block 16): thread 1 (main)
`status=0` RUNNING game code `pc=0x39b72c`
(`sub_0039AE98+0x894`), `scheduled=601`; threads 2/3/4/5/6 all
`status=2` WAIT at `0x423de8` on semas 26/30/31/32/36
(thread 5 `entry=0x382740`, `scheduled=601` — active, sampled
waiting). 17-block census: t1 b1 = 6 RUNNING + 11 WAIT (game
pcs `0x39e72c/0x186c04/0x38f364/0x2c6074/0x39b72c`); b2 = 4
RUNNING + 7 sampled mid-syscall (`status=1 pc=0x423dc8`,
`waitReason=0` — runnable, contended sample mix) + 6 WAIT.
Tick pcs (all driver/game code, never the `0x394Fxx` walk):
b1 `0x317244` (`sub_00316F00+0x344`), `0x36356c`
(`sub_00363490+0xdc` — the direct caller of `0x362DE8`),
`0x3827e0` (`sub_00382760+0x80`); b2 adds `0x1d8efc`
(`sub_001D8DE0+0x11c`) and `0x382650` (function entry).

### f. Ladder vs P28-boot1 (regression check + progress proof)

P28-boot1: 19,145 lines / 2,640,817 B / 17 stub+thread blocks /
park at block 5.

| Rung | P28-boot1 | P1af-boot1 | P1af-boot2 |
|---|---|---|---|
| Lines / bytes | 19,145 / 2,640,817 | 207,189 / 36,650,891 | 208,858 / 36,778,835 |
| Stub / thread / syscall blocks | 17 / 17 | 17 / 17 / 17 | 17 / 17 / 17 |
| Park onset | block 5 (first all-13) | NONE (blocks 2–16 steady 222 distinct; b0=973, b1=491) | NONE (b0=697, b1=798, then 222×15) |
| Thread-1 | walk ×12 (+4 WAIT, 1 null) | 6 RUNNING + 11 WAIT, game pcs | 4 RUN + 7 mid-syscall + 6 WAIT |
| Thread-3 | WAIT ×13–14 + transients | WAIT-30 ×16 + 1 RUN | WAIT-30 ×16 + 1 RUN |
| Thread-6 | WAIT ×14 (3 early absences) | WAIT-36 ×17 | WAIT-36 ×16 (created later in wall-time) |
| 29-handshake w/s | 64 / 64 | 5291 / 5290 | 5348 / 5347 |
| 30-handshake w/s | 4 / 3 (ends parked) | 4 / 3 (ends parked) | 4 / 3 (ends parked) |
| 31-handshake w/s | 5210 / 5210 | 5291 / 5290 | 5348 / 5347 |
| Creates / `-1` waits | 37 / 0 | 37 / 0 | 37 / 0 |
| Driver-entry | 98 | 98 | 98 |
| `[drop]` census | 6× same site + args | 6× same | 6× same |
| SendCmd / handshake | 1 + 1 | 1 + 1, same bytes | 1 + 1 |
| `0x394ED0` trace | 15,576 / 15,576 (137 + slices) | 104,442 / 104,442 (all fresh) | 105,582 / 105,582 |
| `0x362DE8`/`0x362CC8` trace | 63 / 63 | 5289 / 5290 | 5346 / 5347 |
| `0x395000` trace | 113 / 113 | 99153 / 99153 | 100236 / 100236 |
| GS kicks / copy / gif / drawing=1 | 96 / 64 / 48 / 96 | 96 / 64 / 48 / 96 (exact) | exact |
| `run:tick` | 13 ticks, walk-family, dma/gif frozen 1166/65 | 7 ticks, driver-code pcs, dma 22188→171405, gif 641→4674 | 8 ticks, same advancing (dma→191796, gif→5225) |
| CD `lbn=` / first-last | 810 / `0x10`→`0x4311f` | 810 / identical | 810 / identical |
| SIF loads | 21 (id 1–21, same order) | 21, same | 21, same |
| Dormant / start-thread | 121 / 5 | 11160 / 5 | 11019 / 5 |
| Missing / `No exact` | 1 / 0 (JALR `0x2322d4→0x395730`) | 1 / 0, same bytes | same |
| Presented frame | None | None | None |
| Crash / FATAL | 0 / 0 | 0 / 0 | 0 / 0 |

CONTENDED (wall-throughput) rows — treat as host-load-sensitive,
not regressions: lines/bytes, trace sizes + call counts (balance
is the signal), stub `distinct` values, tick counts/pcs,
thread-sample mixes, 29/31 w/s volumes (balanced throughout),
dormant counts (all `id=-1` schedule traces — active-game volume
vs parked-boot volume; b1≠b2 proves wall-clock-period sampling),
sema-30 line numbers. Guest-event rows (probe bodies, census,
sema-30 shape, CD/SIF/GS/RPC, creates, driver-entry, missing) are
deterministic and unaffected. Dormant 121→11k and 29-handshake
64→5.3k are progress signatures (scheduler + pump cycling instead
of parked), not new faces: shapes benign, everything balanced,
zero errors.

## P29-3. Binaries and commits

| Item | Value |
|---|---|
| BEFORE `ps2x_tests` / runner | `4b2625bc…` / `ead11aa1…` (= P28 AFTER pair; suite 431/431/0, CWD `$R`) |
| AFTER `ps2x_tests` / runner | `2b353fd2…` / `40467623…` (full shas in §P29-4 log; suite 434/434/0) |
| Build | `cmake --build /tmp/p1-link/runtime --target ps2x_tests ps2EntryRunner -j4`, exit 0; same `ld` duplicate-library warning as P1ad (observed as-is) |
| Fork commit | `e483d8d` Fix: emulate SPR normal-mode DMA data movement (SPR_FROM + SPR_TO) (P1af) — `ps2_memory.cpp` +58, `ps2_memory_tests.cpp` +84 only, trailer `Orchestrated-By: Muse Code` |
| Push | `git push fork ssx3` → `5001830..e483d8d`, exit 0; `HEAD...fork/ssx3` = 0/0 after; no foreign history integrated |
| Pull --rebase | Refused (`cannot pull with rebase: You have unstaged changes` — foreign in-tree work, see below); behind 0, nothing to replay; no foreign rebase conflict |
| Concurrent-tree note | A foreign agent edited `$R` mid-session (first new mtimes 01:04–01:06 EDT: `ps2_log.h`, `EeScheduler.cpp`, `RPC.cpp`, `ps2_runtime.cpp`, new `ps2_park_snapshot.h`; later `gs_frontend.cpp`, `ps2_runtime_kernel_tests.cpp`); all AFTER my last build finished (00:56 EDT) — binaries built from `5001830` + my 2 files only, receipts uncontaminated. Named `git add` of my 2 files only; foreign files never staged/committed/touched |
| `._*` | Purged under `ps2xRuntime/src` + `include` before staging; named `git add` of the two files only; staged diff verified (+142/−0, all mine) |

## P29-4. Exact commands

From `$R` (fork) unless noted; `$W`, `LOG`/`LOG2`, `T1`/`T2` as above:

```
# Step 0 (context; lease-free)
re-read REPORT Part 28 (full) + brief local/muse/prompts/P1af.md
cat /tmp/ssx3-p-lane-lease (absent at start); git -C $R status/log (5001830 + generated-file mod)
# Step 1 (tests first = BEFORE receipt; lease-free)
append 2 SPR cases to ps2xTest/src/ps2_memory_tests.cpp
cmake --build /tmp/p1-link/runtime --target ps2x_tests -j4 (exit 0)
cd $R && ps2x_tests (434 total, 432 pass, 2 fail — the gap receipted)
# Step 1 (fix; lease-free)
edit ps2xRuntime/src/lib/ps2_memory.cpp (+58 SPR block; MADR writeback madr+bytes)
cmake --build /tmp/p1-link/runtime --target ps2x_tests ps2EntryRunner -j4 (exit 0)
shasum AFTER pair: runner 404676232900a28f5fb194895111282b3feeb4f9c3b9a4cd43674aaedeed25b6
  tests 2b353fd2c6d046e106cb0b3a16049f6ebce5b58296a11652915983f5468b12a5
cd $R && ps2x_tests (434/434/0) + per-face counts + P12 +1-test check (git show da6a2d5)
sed /tmp/p1ad-boot{1,2}.py -> /tmp/p1af-boot{1,2}.py (docstring + LOG only; diff-verified)
write /tmp/p1af-mine.py (probe/sema/census/blocks/GS/CD miner)
# Step 2 (boots; lease P1af held 04:57:33Z-05:00:57Z only)
pre-claim checks (lease absent; pgrep exit 1; shasum 40467623; ISO + ELF sizes)
printf 'P1af' > lease + >> p1af-waits.log; python3 /tmp/p1af-boot1.py (90 s, SIGTERM rc=-15)
cp ps2_log.txt ps2_log-p1af-1.txt; spot greps (20000 probe, 0 CYCLE)
cat lease (P1af); pgrep (exit 1); python3 /tmp/p1af-boot2.py (90 s, SIGTERM rc=-15)
cp ps2_log.txt ps2_log-p1af-2.txt; >> p1af-waits.log (release); rm lease; verify absent
# Step 2 (analysis, lease released)
/tmp/p1af-mine.py both boots; per-n probe determinism join (19980/19980 identical)
trace counts (394ED0/362DE8/362CC8/395000 × T1/T2); pool-drop head audit + b2 cross-check of n=6182
PC attribution (0x317244/0x36356c/0x3827e0/0x1d8efc/0x382650/0x39b72c); P1ad-vs-P1af a2 table
ladder rows (blocks/threads/handshakes/GS/CD/SIF/dormant/missing); status=1 sample check
# Step 3 (fork commit + push; lease released)
find ._*-delete (src+include); foreign-tree mtimes audit (clean-binary proof)
git add ps2xRuntime/src/lib/ps2_memory.cpp ps2xTest/src/ps2_memory_tests.cpp (named, verified)
commit e483d8d (trailer); fetch fork; rev-list (1/0); pull --rebase (refused, recorded)
push fork ssx3 (5001830..e483d8d); rev-list 0/0
# Step 3 (this report; lease released)
(edit_file append Part 29 in 1 chunk)
git -C /Users/bradrichardson/dev/ssx3 add -f local/research/P1/REPORT.md
git -C /Users/bradrichardson/dev/ssx3 commit -m "[P1af] ..." (trailer; NO push there)
```

Env delta boots vs boot-p1ad-1: LOG names only (probe env kept).
Source delta: my 1 fork commit on `5001830`; boots ran
`e483d8d`-equivalent tree (built pre-commit from identical
sources; foreign edits landed post-build, §P29-3).

## P29-5. What I could not do

- Produce the 4th sema-30 signal / thread-3 release inside the
  window: main is still in the hash phase at 90 s (5.3k
  returning invocations and going). The mechanism prediction
  (§P28-3a link 6) stands — the signal is downstream of phase
  completion — but the proof needs a longer boot than this
  brief's 2×90 s box allows. No boots left (max 2 used).
- Raise the 20000-line probe cap (hit at ~1/3 boot in both
  runs): the probe lives in `ps2_runtime.cpp`, outside this
  brief's fork-allowed files (`ps2_memory.cpp` + tests ONLY).
  Probe disposition: KEEP `5001830` (env-off, zero-cost).
  Follow-ups needing full fresh-call counts should raise the cap
  or sample (trace enter/exit gives totals: 104k/106k here).
- Recover ~20 interleave-truncated probe tails per boot
  (stdout/stderr share one fd; positions jitter; 128
  `[frame:upload]` splices per boot now that the game runs).
  Every audited truncation duplicates a state intact in the other
  boot (n=6182 cross-check). A `2>`-split or line-buffered emit
  would end it (not my call inside the box).
- Name the IOP announcer / decode `0x3C45C0`'s `0x1C`/`0x1D` arm
  semantics (carried from §P26-5/§P27-5; `0x3C45C0` had 0
  sightings in both P1af boots).
- Run a 3rd boot (max 2 used; unstick + TO + ladder all closed).
- Re-baseline against a P9/P10/P11/P12-only binary (same
  reasoning as §P27-5/§P28-5: the mechanism rows — probe,
  re-init zeroing, TO-fed records, balanced traces — are
  exclusive to this fix).
- Session wall time ≈ 04:35–05:30Z (~55 min, zero lease waits),
  inside the 4 h box.

---

## Part 30 (P1ag): Long-boot proof — 300 s, 4th sema-30 signal ABSENT; hash phase still running (13,108 balanced `0x362DE8` invocations), thread 3 WAIT-30 ×56 straight, no new park

Brief `local/muse/prompts/P1ag.md`. DIAG brief (ZERO fork
changes): 1 rebuild + 1 long boot ≤300 s (confirm boot not run,
§P30-6). Tables, no verdicts. Stale-reading guard: Part 29
(P1af) full — SPR fix, 104k balanced `0x394ED0`, main RUNNING at
90 s, 4th signal predicted downstream of the hash phase.
`W=/Volumes/Extreme SSD/ps2recomp-spike`, `R=$W/PS2Recomp` (fork,
branch `ssx3`), `LOG=$W/P1/run/boot-p1ag-1.log`,
`T=$W/P1/run/ps2_log-p1ag-1.txt` (own copy).

Headline receipts: 300 s foreground, SIGTERM rc=-15. Sema-30
keeps the P1af 7-shape (3 signals / 4 waits, ends parked) —
signal #4 is NOT in the 300 s window either. Thread 3 is WAIT-30
in blocks 3–58 (56 consecutive samples; RUNNING only at blocks
0–1, pre-pump). The hash phase is still running at 300 s:
13,108/13,108 balanced `0x362DE8` invocations (≈43.7/s),
260,822/260,822 `0x394ED0`, 247,714/247,714 `0x395000`.
Stubs hold 222 distinct in blocks 5–58 (×54, no new phase, no
all-N park); main is RUNNING game code in 41/59 samples;
`dma`/`gif` advance (259→455,579 / 16→12,355); 0 crash/FATAL.
Guest-event rows (probe bodies, census, sema-30 shape, CD/SIF/GS/
RPC, creates, driver-entry, missing) match P1af exactly.

## P30-0. Lease record

| Event | Value |
|---|---|
| Lease at session start | `/tmp/ssx3-p-lane-lease` absent (05:13Z and at 05:28:07Z pre-claim) |
| Waits log | `$W/P1/run/p1ag-waits.log` (3 lines: start, claim, release) |
| Waits | None (no foreign P-lane holder all session; T1 was building in a separate tree `/tmp/t1-clean` + `/tmp/t1-link`, never booting — contended CPU, not lease) |
| Pre-claim checks (05:28:02Z) | Lease absent; `pgrep -x ps2EntryRunner` exit 1; binary `81bee6c5…` (P1ag build); ISO 3005415424 B + ELF 3890784 B present; 548 Gi free |
| Claim | `printf 'P1ag\n' > /tmp/ssx3-p-lane-lease` 05:28:08Z, immediately before boot |
| Boot | 300 s foreground, SIGTERM rc=-15 (script exit 241); LOG 475,304 lines, 84,053,701 B; trace copied to T (35,916,072 lines, 1,275,797,618 B) |
| Release | 05:33:24Z, right after boot (analysis needs no lease); verified absent; `pgrep -x` exit 1 |
| Lane rule | P-lane lease held for the boot only (~316 s); build/analysis lease-free; `adb` not used |

## P30-1. Tree-state-at-build + binary (ZERO fork changes)

| Item | Value |
|---|---|
| `git log --oneline -3` | `e483d8d` Fix: emulate SPR normal-mode DMA … (P1af) / `5001830` Diag: SPR_FROM-blind park probe … (P1ad) / `da6a2d5` Fix: kernel-true KE_ERROR … (P12); branch `ssx3`, HEAD `e483d8d6726…` |
| `git status --short` | 7 modified (`ps2_log.h`, `EeScheduler.cpp`, `RPC.cpp`, `gs_frontend.cpp`, `ps2_runtime.cpp`, `runner/register_functions.cpp`, `ps2_runtime_kernel_tests.cpp`) + 2 untracked (`ps2_park_snapshot.h`, `tools/`) — all foreign (T1 emitter work + pre-existing generated-file state, P1af §P29-3 precedent) |
| `git diff --stat` | 399,207 insertions, 5 deletions; dominated by `register_functions.cpp` (generated-file worktree state); T1 files: `ps2_log.h` +40, `EeScheduler.cpp` +189, `RPC.cpp` +74, `gs_frontend.cpp` +11, `ps2_runtime.cpp` +4 (incl `ps2_park_snapshot.h` include + `tallyDispatch` call), `ps2_runtime_kernel_tests.cpp` +115 |
| mtimes at build | `register_functions.cpp` Sep 19 22:50; `ps2_log.h`/`EeScheduler.cpp`/`ps2_runtime.cpp`/`park_snapshot.h` Sep 20 01:04–01:05; `RPC.cpp`/`gs_frontend.cpp`/`tools/ladder_diff.py` 01:06–01:09; `ps2_runtime_kernel_tests.cpp` 01:13 (EDT) |
| Emitter env | `PS2X_DIAG_PARK` unset in boot env (header: unset = compiled in, nothing written); boot env = P1af verbatim except LOG/SECS (diff-verified: docstring + LOG + `SECS=300`) |
| Foreign files | Never staged, touched, or committed (no fork commit, no push) |
| First build | FAILED: `._RPC.cpp` AppleDouble sidecar "source file is not valid UTF-8" (ExFAT precedent, §P2-1) |
| Sidecar purge | `find $R -name "._*" -delete` (111 files, incl `.git` shadows); `git status` unchanged after |
| Rebuild | `cmake --build /tmp/p1-link/runtime --target ps2EntryRunner -j4`, exit 0 (`/tmp/p1ag-build.log`, 18 warning lines); link ran concurrently with T1's separate-tree `-j4` build |
| Binary | `81bee6c5c0740dafbb910fdfd9c62de8185b816372a0658603dc38c41252d40f`, 163,460,272 B (P1af's `40467623…`, 163,381,632 B, superseded) |

## P30-2. Boot receipt + sema-30 table (signal #4: absent)

### a. Probe (cap hit; guest bytes identical to P1af)

| Item | Value |
|---|---|
| Probe lines | 20000 (`n=0..19999`) + cap line at :62604 |
| `CYCLE@` / pool drops / bad drop-heads | 0 / 1066 / 0 |
| NULL-head first touches | 3135 |
| Arenas / distinct `a2` buckets | 1 (`0x8095f0`) / 5 |
| `[frame:upload]` splices | 128 |

### b. Sema-30: the 7-shape again, 4th signal absent

| Line | op | count transition | waker | pc / ra | result |
|---|---|---|---|---|---|
| 643 | signal | 0→1 | 1 | `0x423dc8` / `0x31acf4` | 30 |
| 645 | wait | 1→0 | 3 | `0x423de8` / `0x31aca4` | 30 |
| 646 | wait | 0→0 | 3 | `0x423de8` / `0x31aca4` | park |
| 706 | signal | 0→0, waiters 1→0 | 1 | `0x423dc8` / `0x31acf4` | target=3 |
| 7116 | wait | 0→0 | 3 | `0x423de8` / `0x31aca4` | park |
| 7167 | signal | 0→0, waiters 1→0 | 1 | `0x423dc8` / `0x31acf4` | target=3 |
| 7369 | wait | 0→0 | 3 | `0x423de8` / `0x31aca4` | park |

3 signals / 4 waits, ending parked — same shape as P1af
(first 4 lines identical; last 3 shifted by pump volume:
P1af-boot1 `:6975,7025,7227`). No further `id=30` line in the
remaining 467,936 lines. Handshake totals: 29: 13109/13109,
30: 4/3, 31: 13110/13109 (in-flight +1 at SIGTERM).

### c. Thread 3: first RUNNING + post-90 s record

| Block | status | waitId | pc | Note |
|---|---|---|---|---|
| 0 | 0 RUNNING | 0 | `0x3232b8` (`sub_00323268+0x50`) | First RUNNING sample (pre-pump) |
| 1 | 0 RUNNING | 0 | `0x323ebc` (`sub_00323BD8+0x2e4`) | Pre-pump |
| 2 | 1 mid-syscall | 0 | `0x423dc8` | — |
| 3–58 | 2 WAIT | 30 | `0x423de8` ×56 | Consecutive; blocks 18–58 cover post-90 s — never RUNNING |

Thread 6: blocks 2–58 all WAIT-36 at `0x423de8` (×57).

## P30-3. Phase-exit / new-park table (main still in hash phase)

### a. Main pc-sample histogram (59 samples, blocks 0–58)

| status | pc | n | Attribution |
|---|---|---|---|
| 0 RUNNING | `0x186c04` | 15 | `sub_00186A08+0x1fc` |
| 0 RUNNING | `0x2c6074` | 7 | `sub_002C5570+0xb04` |
| 0 RUNNING | `0x39b72c` | 7 | `sub_0039AE98+0x894` (P1af end-pc) |
| 0 RUNNING | `0x38f364` | 4 | `sub_0038F300+0x64` |
| 0 RUNNING | `0x38f354` | 2 | `sub_0038F300+0x54` |
| 0 RUNNING | `0x39e72c` | 2 | `sub_0039E6B8+0x74` |
| 0 RUNNING | `0x3a0714` | 1 | `sub_003A04F0+0x224` |
| 0 RUNNING | `0x39f114` | 1 | `sub_0039F100+0x14` |
| 0 RUNNING | `0x3171bc` | 1 | `sub_00316F00+0x2bc` |
| 0 RUNNING | `0x23d688` | 1 | `sub_0023D660+0x28` |
| 1 mid-syscall | `0x423dc8` | 10 | syscall entry |
| 1 mid-syscall | `0x423de8` | 2 | syscall wait addr |
| 2 WAIT-29 | `0x423de8` | 6 | pump sample (blocks 0,1,2,39,41,58; block 58 = end of boot) |

41 RUNNING + 12 mid-syscall + 6 WAIT-29. `0x362DE8`
does NOT stop growing (trace below); nothing replaces the hash
phase inside 300 s.

### b. Trace totals + growth rate (T: 35,916,072 lines)

| Function | enter / exit | vs P1af-boot1 | Rate |
|---|---|---|---|
| `sub_00394ED0` | 260,822 / 260,822 | 104,442 (2.50×) | — |
| `sub_00362DE8` | 13,108 / 13,108 | 5,289 (2.48×) | 43.7 invoc/s over 300 s (P1af: 58.8/s — contended with T1's parallel build) |
| `sub_00362CC8` | 13,108 / 13,108 | 5,290 | — |
| `sub_00395000` | 247,714 / 247,714 | 99,153 (2.50×) | — |

Every invocation returns (no hung call, no checkpoint-unwind
exit). Projected phase-exit time: not projectable — total phase
work is unknown; tabled rate only.

### c. Stub-distinct series + new-park check

| Item | Value |
|---|---|
| Blocks | 59 (`[diag:stubs]` + `[diag:threads]` + `[diag:syscalls]` each ×59) |
| distinct series | b0=687, b1=250, b2=283, b3=674, b4=268, b5–b58=222 ×54 |
| New phase | None (no new distinct count after block 5) |
| New park | None: no all-N stub phase, no hung call (all traces balanced), no frozen counters (`dma` 259→455,579, `gif` 16→12,355 across 37 ticks) |
| Tick pcs | All driver/game code, never the `0x394Fxx` walk: `0x3230c0` (`sub_00323098+0x28`), `0x3827e0`, `0x1d8efc`, `0x3172e0`/`0x317244`/`0x3171bc` (all `sub_00316F00`+off), `0x377ae8`/`0x377b1c` (`sub_00376938`+`0x11b0`/`0x11e4`), `0x382650` (entry), `0x36356c`, `0x423dc0`, `0x3a0714`, `0x2c6074`, `0x31a490` (`sub_0031A3C0+0xd0`), `0x3825c0` (`sub_0037E120+0x44a0`) |

### d. Drop / RPC / CD / SIF / GS deltas vs P1af

| Item | P1ag | P1af-boot1 | Delta |
|---|---|---|---|
| `[drop]` | 6× same early `GetEntryAddress` site `:68-73` | 6× same | None |
| Unhandled RPC | 4, same sids/bytes/pcs | 4 | None |
| `SendCmd` / handshake | 1 `cid=0x80000001` / 2 | 1 / 1 | +1 handshake substring line (same event; miner counts `handshake` case-insensitively) |
| `0x3C45C0` | 0 | 0 | None |
| CD `lbn=` / first-last | 810 / `0x10`→`0x4311f` | 810 / identical | None |
| SIF loads | 21 (id 1–21, same order) | 21 | None |
| Creates / `-1` waits | 37 / 0 | 37 / 0 | None |
| Driver-entry | 98 | 98 | None |
| GS kicks / copy / gif / drawing=1 | 96 / 64 / 48 / 96 | 96 / 64 / 48 / 96 | None |
| Missing / `No exact` | 1 / 0 (JALR `0x2322d4→0x395730`) | 1 / 0, same bytes | None |
| Presented frame | None | None | None |
| Crash / FATAL | 0 / 0 | 0 / 0 | None |

## P30-4. Ladder vs P1af-boot1

| Rung | P1af-boot1 (90 s) | P1ag (300 s) |
|---|---|---|
| Lines / bytes | 207,189 / 36,650,891 | 475,304 / 84,053,701 |
| Stub / thread / syscall blocks | 17 / 17 / 17 | 59 / 59 / 59 |
| Park onset | NONE (222 ×15) | NONE (222 ×54) |
| Thread-1 | 6 RUNNING + 11 WAIT, game pcs | 41 RUN + 12 mid-syscall + 6 WAIT-29 (end: WAIT-29) |
| Thread-3 | WAIT-30 ×16 + 1 RUN transient | WAIT-30 ×56 (b3–58) + RUN b0–b1 (pre-pump) |
| Thread-6 | WAIT-36 ×17 | WAIT-36 ×57 (b2–58) |
| 29-handshake w/s | 5291 / 5290 | 13109 / 13109 |
| 30-handshake w/s | 4 / 3 (ends parked) | 4 / 3 (ends parked) |
| 31-handshake w/s | 5291 / 5290 | 13110 / 13109 |
| 4th sema-30 signal | Absent | Absent |
| `0x394ED0` trace | 104,442 / 104,442 | 260,822 / 260,822 |
| `0x362DE8`/`0x362CC8` trace | 5289 / 5290 | 13108 / 13108 |
| `0x395000` trace | 99153 / 99153 | 247714 / 247714 |
| `run:tick` | 7 ticks, dma 22188→171405, gif 641→4674 | 37 ticks, dma 259→455579, gif 16→12355 |
| Dormant / start-thread | 11160 / 5 | 26209 / 5 |

CONTENDED rows (host-load-sensitive, T1's `-j4` build ran
through the whole boot — not regressions): lines/bytes, trace
sizes + call counts (balance is the signal), 29/31 volumes,
dormant counts, thread-sample mixes, tick counts/pcs, sema-30
late line numbers, stub b0–b4 values. Guest-event rows (§P30-3d,
probe bodies, sema-30 shape) are deterministic and unaffected.

## P30-5. Exact commands

From `/Users/bradrichardson/dev/ssx3` unless noted; `$W`, `R`,
`LOG`, `T` as above:

```
# Tree state + rebuild (lease-free)
git -C $R log --oneline -5; git -C $R status --short; git -C $R diff --stat
ls -lT (7 modified + 1 new header); ls $R/tools/; git -C $R diff (ps2_runtime.cpp, ps2_log.h)
grep PS2X_ $R/ps2xRuntime/include/ps2_park_snapshot.h (emitter env name)
cmake --build /tmp/p1-link/runtime --target ps2EntryRunner -j4 (FAIL: ._RPC.cpp)
find $R -name "._*" -delete (111 files); git -C $R status --short (unchanged)
cmake --build /tmp/p1-link/runtime --target ps2EntryRunner -j4 > /tmp/p1ag-build.log 2>&1 (exit 0)
shasum -a 256 /tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner (81bee6c5...)
sed /tmp/p1af-boot1.py -> /tmp/p1ag-boot1.py (LOG + SECS=300 + docstring; diff-verified)
cp /tmp/p1af-mine.py /tmp/p1ag-mine.py
# Boot (lease P1ag held 05:28:08Z-05:33:24Z only)
pre-claim checks (lease absent; pgrep exit 1; shasum 81bee6c5; ISO + ELF sizes; df)
printf 'P1ag' > lease + >> p1ag-waits.log; python3 /tmp/p1ag-boot1.py (300 s, SIGTERM rc=-15)
cp ps2_log.txt ps2_log-p1ag-1.txt; >> p1ag-waits.log (release); rm lease; verify absent
# Analysis (lease released)
python3 /tmp/p1ag-mine.py boot-p1ag-1.log (probe/sema/drops/census/threads/ticks)
write + run /tmp/p1ag-blocks.py (stub series, t1/t3/t6 series, handshakes)
grep -c sub_00394ED0/00362DE8/00362CC8/00395000 enter/exit on T (4×2 counts)
grep rows (SendCmd/SIF/dormant/gif/copy/crash/missing/frame:upload); PC attribution via $W/P1/output sub_ listing
# Report (lease released)
(edit_file append Part 30 in 1 chunk)
git -C /Users/bradrichardson/dev/ssx3 add -f local/research/P1/REPORT.md
git -C /Users/bradrichardson/dev/ssx3 commit -m "[P1ag] ..." (trailer; NO push there)
```

Env delta vs boot-p1af-1: LOG name + SECS only (probe env
kept, `PS2X_DIAG_PARK` unset). Source delta: none — zero fork
changes; binary built from `e483d8d` + foreign T1 tree state
(recorded, env-off).

## P30-6. What I could not do

- Produce the 4th sema-30 signal / thread-3 release inside 300 s:
  main is still in the hash phase at 300 s (13,108 returning
  invocations and going, stubs steady 222, no exit signature).
  The mechanism prediction (§P28-3a link 6) is still unreached,
  not refuted — the signal stays downstream of phase completion.
- Project the phase-exit time: total phase work is unknown, so
  only the growth rate (43.7 invoc/s, contended) is tabled.
- Run the optional ≤90 s confirm boot (1 of 2 boots used):
  the 300 s absence + all-balanced traces + exact guest-event
  match to P1af's 2×90 s already span three consistent windows;
  a shorter re-boot adds no new window, and the lease was freed
  for T1's priority proof boot.
- Raise the 20000-line probe cap (hit at :62604): the probe
  lives in `ps2_runtime.cpp`, outside this diag brief's zero-
  change rule. Trace enter/exit gives totals (260k here).
- Name the IOP announcer / decode `0x3C45C0`'s `0x1C`/`0x1D` arm
  semantics (carried from §P26-5/§P27-5/§P29-5; 0 sightings).
- Session wall time ≈ 05:13–05:45Z (~32 min active + analysis),
  inside the 4 h box; zero lease waits.

---

## Part 31 (P1ah): Hash-phase work census — progress-indicator hunt over the P1ag 300 s trace+log (no boot, no fork changes)

Brief `local/muse/prompts/P1ah.md`. Census brief (ZERO fork
changes, NO boots): mine the EXISTING P1ag receipts for
phase-progress indicators. Tables, no verdicts. Stale-reading
guard: Part 29 (P1af) full + Part 30 (P1ag) full — SPR fix, main
RUNNING, 4th sema-30 signal absent at 300 s, 13,108 balanced
`0x362DE8` invocations, stubs steady 222, phase-exit "not
projectable — total phase work unknown".
`W=/Volumes/Extreme SSD/ps2recomp-spike`,
`LOG=$W/P1/run/boot-p1ag-1.log` (475,304 lines),
`T=$W/P1/run/ps2_log-p1ag-1.txt` (35,916,072 lines),
P1af pair (`boot-p1af-1.log`, `ps2_log-p1af-1.txt`) for rate
comparison. Miners are /tmp scratch (`/tmp/p1ah-*.py`, uncommitted);
this Part is the only evidence.

Headline receipts: per-invocation guest work is EXACTLY constant
from invocation 75 to 13,106 (20× `0x394ED0` + 19× `0x395000` +
1× `0x362CC8` + 2,534 trace lines per invocation, machine-identical
across 12 consecutive 1,000-chunks and across the P1af/P1ag boots);
the only shape in the phase is the ramp (inv 0–74: 2/3/2 then
20/inv, lockstep with the probe `total→0x14` at n=162). Wall-rate
tables are flat at 33–37 invoc/s (slices 1–3) with a uniform
3–5× step at blocks 49–50 (~245–250 s) across handshake, dormant,
dma, and gif counters while every guest-denominated ratio holds
fixed (dormant/pump 2.000, 394/inv 20.00, 395/inv 19.00,
d_gif/d_dma 0.0270, stubs 222, single caller). Probe `total`
saturates at 0x14 by n=162 (slope 0 over the remaining 19,838
samples); arena/records/buckets are fixed sets by n=181 with zero
growth after. CD/SIF/GS/RPC last events all sit in blocks 0–2;
zero new events in blocks 3–58. Examined-and-absent table + ONE
deciding receipt (driver-loop index+bound at call site `0x36356c`)
in §P31-6.

## P31-0. Lease / rule record (no lease, no boots, no fork changes)

| Item | Value |
|---|---|
| P-lane lease | Never touched (no boots; `/tmp/ssx3-p-lane-lease` never created/checked-for-write) |
| Boots | 0 (read-only mining of existing receipts) |
| Fork changes | 0 (no source edits, no fork commits, no push; fork tree never staged) |
| `adb` | Not used |
| Other agents' dirs / ISO | Read-only (no writes outside `local/research/P1/REPORT.md` + /tmp scratch) |
| ssx3 files changed | `local/research/P1/REPORT.md` ONLY (this Part); commit prefix `[P1ah]`; NO push |

## P31-1. Invocation-rate shape (Task 1.1)

### a. Method (trace has no timestamps)

| Item | Value |
|---|---|
| Trace line census | 35,916,072 / 35,916,072 lines end in `enter`/`exit` (0 timestamp lines) |
| Wall grid | 59 `[diag:stubs]` blocks, `period_ms=5000` → 5 s samples, blocks 0–58 |
| Rate proxy | Pump handshakes `29w+31w` per block interval (1 pump cycle : 1 `0x362DE8` invocation) |
| Proxy validation | In-block invoc proxy 13,094 + pre-block-0 14 = 13,108 = trace `0x362DE8` enters exactly |
| `0x394ED0`/`0x395000` per-slice | Derived: 20×/19× invocation counts (§P31-1d multiplier), ramp-adjusted in slice 0; totals reconcile to ±19 (1-inv boundary tolerance) |

### b. Pump rate per 60 s slice (P1ag, wall-grounded)

| Slice | Blocks | Wall (≈) | Pump waits (29w+31w) | Invoc proxy | Rate (/s) |
|---|---|---|---|---|---|
| Pre-block-0 | — | 0–~5 s | 14 | 14 | — (boot) |
| 0 | 0–11 | 0–60 s | 2,751 | 1,375 | 22.93 |
| 1 | 12–23 | 60–120 s | 4,448 | 2,224 | 37.07 |
| 2 | 24–35 | 120–180 s | 4,284 | 2,142 | 35.70 |
| 3 | 36–47 | 180–240 s | 3,963 | 1,981 | 33.02 |
| 4 | 48–58 | 240–300 s | 10,745 | 5,372 | 89.54 |

Slice 0 is depressed by the boot preamble (blocks 0–4 ramp:
2/2/36/111/165 per 5 s; blocks 5–11: 134–165). Slices 1–3 span
33.02–37.07/s. Slice 4 contains the blocks-49–50 step (§P31-3c)
and the SIGTERM-truncated block 58 (355 vs 627 in block 57).

### c. P1af rate comparison (same method, 17 blocks)

| Slice | Blocks | Wall (≈) | Pump waits | Invoc proxy | Rate (/s) |
|---|---|---|---|---|---|
| P1af 0 | 0–11 | 0–60 s | 7,670 | 3,835 | 63.92 |
| P1af 1 | 12–16 | 60–85 s | 2,846 | 1,423 | 56.92 |

P1af per-block series: b0=526 (ramp), b1–b15 flat 297–303 per
5 s, b16=221 (SIGTERM-truncated). P1af wall rate ≈ 60/s steady;
P1ag slices 1–3 run 0.55–0.62× that, slice 4 runs 1.49× that.

### d. Per-invocation work (trace, exact — the projection-relevant shape)

Per-1,000-invocation chunks of `0x362DE8` (P1ag; chunk k covers
the trace interval of invocations 1000k…1000k+999 ±1 boundary):

| Chunk (inv) | 394ED0 | 395000 | 362CC8 | Trace lines | 394/inv | 395/inv |
|---|---|---|---|---|---|---|
| 0–999 | 18,642 | 17,643 | 1,000 | 5,234,034 | 18.64 | 17.64 |
| 1000–1999 … 12000–12999 (×12) | 20,000 each | 19,000 each | 1,000 each | 2,534,000 each | 20.00 | 19.00 |
| 13000–13107 (108 + in-flight) | 2,180 | 2,071 | 108 | 274,038 | 20.19 | 19.18 |

The 12 middle chunks are machine-identical (including chunks
8000–12999, which fall in the wall-rate surge window). Tail
+20/+19 = the SIGTERM-interrupted invocation #13108, which
completed its 39 hash calls (tail-verified: 20×/19× enters in the
365 post-enter lines) before the process died mid-frame. P1af
chunks are identical: chunk 0 = 18642/17643/1000/5234034
(bit-exact), chunks 1–4 = 20000/19000/1000/2534000, tail
5800/5510/290 (+20/+19 same structure).

### e. Ramp fine profile (first 120 invocations, enter-line join)

| Invocations | 394ED0/inv | 395000/inv |
|---|---|---|
| 0–51 | 2 | 1 |
| 52–63 | 3 | 2 |
| 64–74 | 2 | 1 |
| 75–13106 | 20 | 19 |

Ramp arithmetic: 52×2+12×3+11×2 = 162 `0x394ED0` calls in inv
0–74 → probe n=162 (`total→0x14`, §P31-4) is the first call of
invocation 75, the first steady-state invocation. Slice-0 ramp
adjustment: 75×20−162 = 1,338 (394); 75×19−87 = 1,338 (395).

### f. Derived 394ED0/395000 per-60 s slice (20×/19× §P31-1b)

| Slice | Invoc | 394ED0 (derived) | 395000 (derived) |
|---|---|---|---|
| Pre-block-0 | 14 | 280 | 266 |
| 0 | 1,375 | 26,162 | 24,787 |
| 1 | 2,224 | 44,480 | 42,256 |
| 2 | 2,142 | 42,840 | 40,698 |
| 3 | 1,981 | 39,620 | 37,658 |
| 4 | 5,372 | 107,440 | 102,068 |
| Sum vs trace | 13,108 | 260,822 / 260,822 (exact) | 247,733 / 247,714 (−19 tol.) |

### g. Enters per trace-tenth (POSITION proxy — explicitly not wall time)

| Tenth | 362DE8 | 394ED0 | 395000 | 362CC8 |
|---|---|---|---|---|
| 0 | 351 | 5,682 | 5,331 | 352 |
| 1–9 (each) | 1417–1418 | 28340–28360 | 26923–26942 | 1417–1418 |

Tenth 0 holds the boot preamble (first `0x362DE8` enter at trace
line 19,385); tenths 1–9 are flat to ±20 (±0.07%), mirroring §P31-1d.

## P31-2. Caller confirmation at 300 s scale (Task 1.2)

Indent-stack parent census over the full 35,916,072-line trace
(single streaming pass; every `0x362DE8` enter attributed):

| Caller (parent frame) | P1ag enters | P1af enters |
|---|---|---|
| `sub_00363490_0x363490` (call site `0x36356c` = +0xdc, per P1af ticks) | 13,108 / 13,108 | 5,289 / 5,289 |
| Any other caller | 0 | 0 |

New phase edges via new callers: none tabled (zero sightings).

## P31-3. Counter slopes (Task 1.3)

### a. dma/gif tick deltas (37 ticks; tick→block mapped)

| Tick | Block | pc | d_dma | d_gif | d_gif/d_dma |
|---|---|---|---|---|---|
| 120 | 0 | `0x3230c0` | 259 | 16 | — (boot) |
| 240 | 2 | `0x3827e0` | 701 | 40 | 0.05706 |
| 360 | 4 | `0x1d8efc` | 7,206 | 207 | 0.02873 |
| 480 | 5 | `0x3172e0` | 7,178 | 194 | 0.02703 |
| 600–960 (×4) | 7–11 | driver pcs | 8,066–9,171 | 218–247 | 0.02693–0.02711 |
| 1080–1560 (×5) | 13–19 | driver pcs | 9,731–10,845 | 263–293 | 0.02695–0.02711 |
| 1680–2400 (×7) | 20–29 | driver pcs | 9,514–10,399 | 258–281 | 0.02694–0.02713 |
| 2520–3000 (×5) | 31–37 | driver pcs | 9,547–10,179 | 259–275 | 0.02693–0.02713 |
| 3120–3600 (×5) | 38–44 | driver pcs | 8,362–9,134 | 226–246 | 0.02693–0.02713 |
| 3720–3960 (×3) | 46–49 | driver pcs | 8,771–9,502 | 237–256 | 0.02694–0.02703 |
| 4080 | 50 | `0x382650` | 14,948 | 404 | 0.02703 |
| 4200 | 52 | `0x3172e0` | 47,032 | 1,272 | 0.02705 |
| 4320 | 54 | `0x3825c0` | 47,618 | 1,286 | 0.02701 |
| 4440 | 57 | `0x3a0714` | 54,474 | 1,473 | 0.02704 |

Full per-tick (dma, gif) series in §P31-7 miner output (kept in
/tmp scratch, reproducible). d_dma shape: ramp (259→7.2k), flat
8.1k–10.8k over ticks 360–3960 with a shallow dip at ticks
3120–3600 (8.4k–9.1k, blocks 38–44 — same window as the handshake
dip in §P31-3d), transitional 14,948 at tick 4080, 47k–54k at
ticks 4200–4440. d_gif/d_dma holds 0.0270 ± 0.0002 across all 35
steady ticks including the surge ticks. P1af comparison deltas:
22,188 / 23,495 / 25,376 / 25,462 / 25,116 / 24,982 / 24,786
(dma), 635–688 (gif), ratio 0.0273 overall — flat, no step.

### b. Dormant-count slope (dormant per 60 s slice)

| Slice | 29w | Dormant | Dormant/29w |
|---|---|---|---|
| P1ag pre-block-0 | — | — | — |
| P1ag 0 | 1,375 | 2,704 | 1.9665 (blocks 0–1 pre-pump: 0 dormant) |
| P1ag 1 | 2,224 | 4,448 | 2.0000 |
| P1ag 2 | 2,142 | 4,284 | 2.0000 |
| P1ag 3 | 1,982 | 3,962 | 1.9990 |
| P1ag 4 | 5,372 | 10,746 | 2.0004 |
| P1af 0 | 3,835 | 8,067 | 2.1035 |
| P1af 1 | 1,423 | 3,028 | 2.1279 |

Per-block, P1ag dormant = 2×29w in 55/59 blocks (±1 in-flight in
blocks 37/40/47/48/54/55). Within-boot slope: flat 2.000 across
all slices including the surge slice.

### c. Slope break at blocks 49–50 (candidate tabled with evidence)

| Counter | Blocks 45–48 (/5 s or /tick) | Block 49 | Blocks 50–57 | Step |
|---|---|---|---|---|
| 29w per 5 s | 163–178 | 211 | 452–630 | ~3.4× |
| Dormant per 5 s | 324–356 | 422 | 904–1,260 | ~3.4× |
| d_dma per tick | 8,771–9,502 | (tick 3960 in blk 49) | 14,948 → 47,032–54,474 | ~5.1× |
| d_gif per tick | 237–256 | (237) | 404 → 1,272–1,473 | ~5.0× |

Onset evidence: handshake transitional at block 49 (211 vs
~170 baseline), full step at block 50 (452); dma transitional at
tick 4080 (block 50; 14,948 vs ~9.5k baseline), full step at tick
4200 (block 52; 47,032).

### d. Uniform-scaling check across the break (wall rates vs guest ratios)

| Quantity | Kind | Pre-break (slices 1–3) | Post-break (slice 4) | Factor |
|---|---|---|---|---|
| Handshake / 5 s | wall rate | ~170–190 | ~560–630 | ~3.4× |
| Dormant / 5 s | wall rate | ~340–380 | ~1,120–1,260 | ~3.4× |
| d_dma / tick | wall rate | ~8.5k–10.8k | ~47k–54k | ~5.1× |
| d_gif / tick | wall rate | ~230–290 | ~1,270–1,470 | ~5.0× |
| Dormant / pump | guest ratio | 2.000 | 2.000 | 1.00× |
| 394ED0 / invoc | guest ratio | 20.00 | 20.00 | 1.00× |
| 395000 / invoc | guest ratio | 19.00 | 19.00 | 1.00× |
| Trace lines / invoc | guest ratio | 2,534 | 2,534 | 1.00× |
| d_gif / d_dma | guest ratio | 0.0270 | 0.0270 | 1.00× |
| Stub distinct | guest state | 222 | 222 | same |
| `0x362DE8` caller set | guest state | {`0x363490`} | {`0x363490`} | same |
| Sema-30 shape | guest state | parked (4w/3s) | parked (4w/3s) | same |

Mid dip (blocks 38–44 handshake ~159–163/5 s; ticks 3240–3600
d_dma 8.4k–9.1k): correlated across handshake + dma + gif with
ratios fixed — same uniform-scaling signature at smaller amplitude.

## P31-4. Early-phase probe trend (Task 1.4, capped 20k window)

Probe cap hit at LOG :62604 (block-10 interval, ~50–55 s wall);
n=0..19999 covers `0x394ED0` calls 0–19999 ≈ invocations 0–~1067.

### a. total-vs-n (change points + fit + residuals)

| n range | total | Note |
|---|---|---|
| 0–103 | 0x2 | — |
| 104–139 | 0x3 | — |
| 140–161 | 0x2 | dip-back; coincides with new a1s `0x70001c00`@140, `0x70001c80`@141 |
| 162–19999 | 0x14 (=20) | saturated; n=162 = first call of invocation 75 (§P31-1e) |

Fit: total(n) = 2 (n<104), 3 (104≤n<140), 2 (140≤n<162), 20
(n≥162). Residuals: 0 mismatches over 19,996 parsed probe lines
(4 lines unparseable interleave truncations; 1 additional
truncated `total=0x` empty field at n=934 excluded as artifact —
same class as §P29-2a). P1af change points identical (104/140/162).

### b. Arena / record / bucket / key growth

| Field | Distinct | First-sighting span | Growth after |
|---|---|---|---|
| a0 (arena) | 1 (`0x8095f0`) | n=0 | zero |
| a1 (record addr) | 23 (`0x70000000`–`0x70002580`) | all first-seen by n=181 | zero (20/chunk cycling, §P29-2a pattern) |
| a2 (bucket) | 5 (`0x26/0x34/0x9d/0xb0/0xd0`) | all first-seen by n=162 | zero |
| key | 1 (`[WILD WILD WILD WILD]`, 19,998 + 2 truncated) | n=0 | zero (no key information emitted) |
| chain | 2 (`[ NULL]`×3136, `[0x85aabc NULL]`×16862, +2 truncated) | — | — |
| pool | 3 values {3:1067, 4:17926, 5:1003} | — | cycling, no trend |

P1af values identical modulo truncation counts (pool {4:17926,
3:1066, 5:1003}; head `0x0`×3135 both boots).

### c. Extrapolation rows (fit only, no bare projection)

| Item | Value |
|---|---|
| Steady fit (n≥162) | total = 20, slope 0 over 19,838 samples |
| Residual distribution | all zero (exact constant) |
| Finite-n completion event expressible by the fit | none (constant has no intercept) |
| Records/buckets/arena trend slope past n=181 | 0 (fixed sets, cycling) |

## P31-5. CD/SIF/GS silence audit (Task 1.5)

P1af-window end in the P1ag log: block 17 @ :112019 (≈90 s).
All last events sit at lines ≤7,369 (blocks 0–2).

| Source | n (P1ag) | n (P1af) | First line | Last line | Last block (≈wall) | First new past P1af window (:112019+, blks 18–58) |
|---|---|---|---|---|---|---|
| CD `lbn=` (`0x10`→`0x4311f`) | 810 | 810 | 106 | 7,319 | 2 (~10–15 s) | none |
| SIF module loads (id 1–21) | 21 | 21 | 75 | 1,055 | 0 (~0–5 s) | none |
| GS kicks | 96 | 96 | 304 | 2,778 | 1 (~5–10 s) | none |
| RPC `trace:unhandled` (:711, :1056, :1062, :5315) | 4 | 4 | 711 | 5,315 | 2 (~10–15 s) | none |
| `SendCmd` (`cid=0x80000001`) | 1 | 1 | 1,052 | 1,052 | 0 | none |
| Sema-30 events (shape 4w/3s, §P30-2b) | 7 | 7 | 643 | 7,369 | 2 | none |

Event sets identical to P1af (§P30-3d); P1af last lines differ
only by pump-volume shift (CD 7,177; RPC 4th @ 5,143; sema-30
last @ 7,227). Zero new CD/SIF/RPC/GS work past block 2, and
zero past the P1af window.

## P31-6. Projection-or-receipt + 600 s table (Task 2)

### a. Examined-and-absent list (indicator, where looked, reading)

| # | Indicator | Where looked | Reading |
|---|---|---|---|
| 1 | Invocation wall rate | Handshake proxy per 60 s (§P31-1b) | flat 33–37/s slices 1–3; slice-4 step scales uniformly (§P31-3d) |
| 2 | Per-invocation work | Trace 1,000-chunks (§P31-1d) | exactly 20/19/1/2534, inv 75–13106 |
| 3 | Work-list shrinkage | 394/395 per-inv ramp (§P31-1e) | ramp ends inv 75; zero slope after |
| 4 | Caller set | Full-trace indent census (§P31-2) | single caller, 0 new |
| 5 | dma/gif slopes | 37-tick deltas (§P31-3a) | flat + uniform 5× step; ratio 0.0270 fixed |
| 6 | Dormant slope | Per-slice dormant/29w (§P31-3b) | 2.000 flat all slices |
| 7 | 29/31 handshake slope | Per-block w/s (§P31-1b/3c) | balanced every block; same series as #1 |
| 8 | Table fill (`total`) | Probe n=0..19999 (§P31-4a) | saturates n=162, slope 0 after |
| 9 | Arena growth (a0) | Probe (§P31-4b) | 1 value, zero growth |
| 10 | Record/bucket growth (a1/a2/keys) | Probe (§P31-4b) | fixed sets by n=181; keys always WILD |
| 11 | CD/SIF/GS/RPC resumption | Silence audit (§P31-5) | silent since ≤block 2 |
| 12 | Stub-phase change / sema-30 release | P30 (carried) | 222 ×54 blocks; 4th signal absent |

### b. ONE minimal deciding receipt (no progress indicator exists above)

| Item | Value |
|---|---|
| Receipt | Driver-loop position + bound `(i, N)` for the loop issuing the `0x362DE8` invocations via call site `0x36356c` (`sub_00363490+0xdc`), sampled per invocation (or per 5 s block) |
| Trend it would show | `i/N` → completion fraction; `N−i` → remaining invocations; constant-work rate (§P31-1b) converts remainder to wall time |
| Why this one | Every cheaper candidate is flat/silent per §P31-6a; the loop bound is the only unobserved quantity in the projection equation `t_exit = (N−i) / rate` |
| Owner | T1's snapshot emitter (owns in-tree periodic capture); fallback a P1ad-style probe brief if the emitter cannot read guest regs — named, not built |

### c. First-post-phase-event signatures (for the next boot brief to check)

| Signal | Trace/log signature that would mark phase exit |
|---|---|
| Sema-30 signal #4 | 8th `id=30` line: `op=signal`, `waiters 1→0`, `target=3` (shape of §P30-2b row 4/6) |
| Per-invocation break | Any 1,000-chunk ≠ 20000/19000/1000/2534000, or any inv ≠ 20/19 (§P31-1d baseline) |
| New caller | Any `0x362DE8` enter whose indent parent ≠ `sub_00363490` (§P31-2 baseline: 0) |
| Stub-phase change | Any `[diag:stubs]` block with distinct ≠ 222 after block 5 (§P30-3c baseline) |
| IO resumption | Any `lbn=`/SIF-load/GS-kick/RPC-unhandled past the §P31-5 last lines |

### d. 600 s boot cost table (no verdict)

| Item | Value |
|---|---|
| Lease cost | ~10 min P-lane lease + T1 contention (per brief) |
| Value if the phase exits inside 600 s | 4th sema-30 signal + thread-3 release captured; exit invocation index recorded (gives `N` empirically); §P31-6c signatures confirmed against baselines |
| Value if the phase continues past 600 s | Rate/work tables extended to 600 s at ~33–90/s wall rate (≈ +10k–30k invocations); per-invocation constancy re-tested over ~2× samples; still no `N` without the §P31-6b receipt |
| What 600 s cannot supply | The driver-loop bound `N` (no existing emitter records it); probe bodies past n=19999 (cap) |

## P31-7. Exact commands

From `/Users/bradrichardson/dev/ssx3` unless noted; `W`,
`LOG`, `T` as above. All receipt accesses read-only (grep/sed/
python reads; `head`/`tail`/`wc`); no lease, no boots, no builds:

```
# Format recon (lease-free; receipts read-only)
ls -lh LOG T + P1af pair; head -c 2000 T; sed -n '18000000,18000005p' T
head -30 LOG; grep -n "run:tick" LOG | head -5
grep -vc -e "enter$" -e "exit$" T  (0: trace is 100% enter/exit)
grep -c "sub_00362DE8_0x362de8 enter" T  (13108)
grep -c "diag:stubs/threads/syscalls" LOG (59/59/59); block line spans
# Miners (written to /tmp, uncommitted; two IndexError fixes on group refs)
write /tmp/p1ah-log.py (blocks/ticks/sema/dormant/probe/CD miner)
python3 /tmp/p1ah-log.py LOG > /tmp/p1ah-p1ag-log.txt
python3 /tmp/p1ah-log.py boot-p1af-1.log > /tmp/p1ah-p1af-log.txt
wc -l T + P1af trace (35916072 / 16103012)
write /tmp/p1ah-trace.py (single-pass caller census + chunks + tenths + balance)
python3 /tmp/p1ah-trace.py T 35916072 > /tmp/p1ah-p1ag-trace.txt
python3 /tmp/p1ah-trace.py ps2_log-p1af-1.txt 16103012 > /tmp/p1ah-p1af-trace.txt
# Ramp + tail forensics (read-only)
grep -n 362DE8/394ED0/395000 enters T | cut -d: -f1 > /tmp/p1ah-{362,394,395}-lines.txt
per-inv join (bisect) for inv 0-1099 (394) and 0-119 (395)
sed -n '35915707,35916072p' T tail forensics (in-flight invocation #13108)
# Final tables
write /tmp/p1ah-final.py (60 s slices, tick deltas, probe deep-dive, silence audit)
python3 /tmp/p1ah-final.py LOG > /tmp/p1ah-p1ag-final.txt
python3 /tmp/p1ah-final.py boot-p1af-1.log > /tmp/p1ah-p1af-final.txt
grep probe total change points + key/chain shapes; gif/dma ratio check
/tmp/p1ah-ratio.py (dormant/29w per slice)
# Report (this Part)
(edit_file append Part 31 in 3 chunks)
git add -f local/research/P1/REPORT.md
git commit -m "[P1ah] ..." (trailer Orchestrated-By: Muse Code; NO push)
```

## P31-8. What I could not do (gap rows)

- Project a phase-exit time: no progress indicator exists in the
  receipts (§P31-6a all flat/silent); the deciding receipt is
  specified, not built (§P31-6b).
- Time-resolve individual invocations inside a 5 s block: the
  trace carries no timestamps, so per-slice 394/395 counts are
  derived via the exact 20/19 multiplier, not directly observed.
- See probe bodies past n=19999 (cap at :62604, §P31-4) or
  function args anywhere (trace enter/exit only).
- Attribute the wall-rate step's host cause from inside the
  receipts (no host-load log was in scope); tabled as uniform
  scaling of wall rates with fixed guest ratios (§P31-3d).
- Session wall time ≈ 05:40–05:55Z (~15 min active), inside the
  4 h box; zero lease waits (no lease taken).

## Part 32 (P1ai): Post-exit diagnosis — main-return, 31-drain, freeze sequencing + next-park spec (no boot)

Brief `local/muse/prompts/P1ai.md`. DIAGNOSIS brief on committed
logs — no boot, no lease of any kind, no fork changes, no `adb`.
Tables, no verdicts. Stale-reading guard: `local/research/T13/REPORT.md`
(all of it — phase EXITED at block 235, N = 72,176) + P1 REPORT Part 31
(pre-exit ladder) + Part 24 §P24-1f/g (`[drop]` census conventions).
`W=/Volumes/Extreme SSD/ps2recomp-spike`,
`LOG=$W/P1/run/boot-t13-1.log` (2,493,828 lines),
`T=$W/P1/run/ps2_log-t13-1.txt` (185,293,022 lines, 6,581,094,749 B),
T13's `blocks.tsv` (242) + `ticks.tsv` (166). Scratch `/tmp/p1ai/`
(miners kept there, uncommitted); this Part is the only evidence.
Trace never copied — one full streaming pass + EOF seeks only.

Headline receipts: main returns through the pc==0 dormant site
(exactly 1 `[diag:dormant] id=1` line @2489892, ra=0x1d8efc,
sp=0x1fffdc0, scheduled=213 — same SITE as the P1e precedent, all
register state different); the driver loop unwinds in-trace 73 lines
after the last `0x362DE8` exit (`363490`@185265063, `376938`@185265064);
T13's 4,049-frame unwind reconciles EXACTLY to 4,049 post-exit depth-0
dispatches (20 distinct roots, tabled complete); the 31-drain is a
781-iteration pump subprocess (3 root chains/iter + 31AAF0-subtree,
2 HLE pad calls/iter via the stub path, zero trace lines by design);
29 halts mid-block-239 (@2489890, 74.1% by lines) with the
29-signal→31-wait→main-dormant trio on 3 adjacent lines; handshakes
reproduce exactly (29 72178/72178, 30 4/3, 31 72959/72958) with the +1
31-inflight localized to EOF line 2493828 and the +2 29-edge bounded
(max in-flight 2, never negative) but not localizable (no timestamps);
dma/gif freeze same-tick (partial 8658/234 @19800, 0/0 @19920);
b241 residue = 13 connected call-targets (call-histogram, complete —
distinct 13 ≤ 30 print cap); silence re-audit clean (0/0/0/0/0 in exit
region, all lasts in blocks 0–2).

## P32-0. Rule record (no lease, no boots, no fork changes)

| Item | Value |
|---|---|
| P-lane lease | Never touched (no boots; lease file never created/checked-for-write) |
| Boots / harness runs | 0 (read-only mining of T13's committed receipts) |
| Fork changes | 0 (fork sources read read-only for site/id semantics; no edits, no commits, no push/pull) |
| `adb` | Not used |
| Other agents' dirs / ISO | Read-only (`/tmp/t13-*.py` read for pattern conventions only; no writes outside `local/research/P1/REPORT.md` + `/tmp/p1ai/`) |
| 6.5 GB trace | Streamed (1 full pass) + `tail -c` seeks; never copied |
| ssx3 files changed | `local/research/P1/REPORT.md` ONLY (this Part, appended); commit prefix `[P1ai]`; NO push |

## P32-1. Main-return mechanics (Task 1)

### a. Status-5 table (every sample — full-log scan, 2 total, none elsewhere)

| # | Log line | Threads block | id | status | waitReason/waitId | pc | entry | scheduled |
|---|---|---|---|---|---|---|---|---|
| 1 | 2490884 | 240 | 1 | 5 | 0/0 | 0x0 | 0x100008 | 213 |
| 2 | 2492423 | 241 | 1 | 5 | 0/0 | 0x0 | 0x100008 | 0 |

`ra` is NOT a `[diag:thread]` field (format carries no ra —
`id/status/waitReason/waitId/pc/entry/priority/scheduled` only); the
return-register state comes from the §P32-1f dormant line (ra=0x1d8efc)
and §P32-1b stacks (sp=0x1fffdc0). Tail extension: full-log
`status=5` scan = exactly these 2; zero status-5 for any other thread,
zero status-5 after block 241 (log ends 2493828).

### b. Thread-1 + stacks exit series (blocks 234–241)

| Block | t1 line | t1 status | t1 waitId/pc | t1 scheduled | stacks sp | stacks pc |
|---|---|---|---|---|---|---|
| 234 | 2444114 | 2 WAIT | 29 / 0x423de8 | 602 | 0x1ffff20 | 0x423de8 |
| 235 | 2453906 | 2 WAIT | 29 / 0x423de8 | 598 | 0x1ffff20 | 0x423de8 |
| 236 | 2464009 | 2 WAIT | 29 / 0x423de8 | 610 | 0x1ffff20 | 0x423de8 |
| 237 | 2473989 | 0 RUN | — / 0x2c6074 | 603 | 0x1fffce0 | 0x2c6074 |
| 238 | 2481225 | 2 WAIT | 29 / 0x423de8 | 593 | 0x1ffff20 | 0x423de8 |
| 239 | 2487630 | 2 WAIT | 29 / 0x423de8 | 608 | 0x1ffff20 | 0x423de8 |
| 240 | 2490884 | 5 DORMANT | 0 / 0x0 | 213 | 0x1fffdc0 | 0x0 |
| 241 | 2492423 | 5 DORMANT | 0 / 0x0 | 0 | 0x1fffdc0 | 0x0 |

t1 holds WAIT-29/sp 0x1ffff20 through b239 (one RUN sample b237),
then dormant/pc 0x0/sp 0x1fffdc0 at b240–241. scheduled 213 at b240 =
§P32-1f dormant `scheduled=213` exactly; 0 at b241 (never rescheduled).

### c. Return-path table (ordered exits, last `0x362DE8` exit → driver unwind)

Last `0x362DE8` enter @185264851 (depth 2, parent `00363490_0x363490`,
single caller reconfirmed); last exit @185264990 (depth 2, live stack
after = [`00376938_0x376938`, `00363490_0x363490`]). Unwind order:

| Order | Trace line | Function | Depth | Role in unwind |
|---|---|---|---|---|
| 0 | 185264990 | `00362DE8_0x362de8` exit | 2 | last invocation exit (70-enter steady-state invocation: 394ED0×20 + 362978×20 + 395000×19 + 364240×2 + 8 singles — §P32-1d note) |
| 1–10 | 185264993–185265011 | 364CD0, 3625C0, 362478, 362660, 3626D8, 3625C0, 362478, 362660, 3626D8, 3627A8 exits | 3 | leaves under sibling 364360 |
| 11 | 185265012 | `00364360_0x364360` exit | 2 | depth-2 sibling frame |
| 12–14 | 185265015–185265019 | 38F460, 3E6448, 38F6A8 exits | 3 | leaves under sibling 364050 |
| 15 | 185265020 | `00364050_0x364050` exit | 2 | depth-2 sibling frame |
| 16–18 | 185265024–185265027 | 42C078, 42C0C0, 4247D8 exits | 4/4/3 | sub-chain under sibling 3666F8 |
| 19–34 | 185265030–185265059 | 38F738→371DD8 ×8 pairs | 3/4 | 8 repeated pairs under sibling 3666F8 |
| 35 | 185265060 | `003666F8_0x3666f8` exit | 2 | depth-2 sibling frame |
| 36 | 185265062 | `0038F300_0x38f300` exit | 2 | depth-2 sibling frame (2-line leaf frame) |
| 37 | 185265063 | `00363490_0x363490` exit | 1 | DRIVER-LOOP frame unwinds (73 lines after order 0) |
| 38 | 185265064 | `00376938_0x376938` exit | 0 | TOP frame unwinds — main's call chain fully returned |

Post-exit depth profile: min 0, max 13. Post-exit enters = 14,015,
exits = 14,017 (net +2 = the two live frames above; EOF stack empty).
Window [last-enter 185264851, EOF]: 28,172 recs, 14,085 enters
(= 14,015 + 70 last-invocation enters: 20/20/19/2/1×8 itemized above —
steady-state shape, no tail-off).

### d. 4,049-frame unwind itemized (depth-0 dispatches — reconciles T13 exactly)

T13's "post-last-rep 4,049 frames" (`t13-cycle.py:184`, depth-0-seq
entries after last rep) = this miner's post-exit depth-0 enters =
4,049 EXACTLY. All 20 rows (complete — no pool):

| # | Root function | Enters | Share of 4,049 |
|---|---|---|---|
| 1 | `00423DE0_0x423de0` | 784 | 19.36% |
| 2 | `0037E120_0x37e120` | 781 | 19.29% |
| 3 | `003C1638_0x3c1638` | 781 | 19.29% |
| 4 | `0031A3C0_0x31a3c0` | 781 | 19.29% |
| 5 | `0031AAF0_0x31aaf0` | 781 | 19.29% |
| 6 | `003E4AF0_0x3e4af0` | 115 | 2.84% |
| 7 | `00376938_0x376938` | 4 | 0.10% |
| 8 | `00382760_0x382760` | 4 | 0.10% |
| 9 | `00423DC0_0x423dc0` | 3 | 0.07% |
| 10 | `0038F300_0x38f300` | 2 | 0.05% |
| 11 | `00363490_0x363490` | 2 | 0.05% |
| 12 | `00382650_0x382650` | 2 | 0.05% |
| 13 | `00316F00_0x316f00` | 2 | 0.05% |
| 14–20 | `00395288` / `00232AE0` / `0031A6B8` / `002C5570` / `0023D660` / `0023D618` / `001D8DE0` | 1 each | 0.02% each |

Check: 784 + 781×4 + 115 + 4 + 4 + 3 + 2×4 + 1×7 = 4,049. The driver
pair re-enters post-phase at depth 0 (`376938`×5 enters / ×6 exits,
`363490`×2 / ×3 — the +1 exits are the §P32-1c live frames).

### e. Dormant-precedent table (P1e §P6-1 vs this return)

Site evidence (fork `ps2xRuntime/src/lib/Kernel/EeScheduler.cpp`,
read-only): pc==0 site @~642 (`if (context.pc == 0u)` + empty
invocations → `[diag:dormant]` print + `makeDormant`); no-function-slot
site @~695 (`!hasFunction(pc)`, pc≠0). Both dormants below have pc=0x0
→ both fired at the pc==0 site.

| Row | P1e precedent (boot-p1e-1.log :200) | T13 return (line 2489892) | Match |
|---|---|---|---|
| Dormant site | pc==0 site (pc=0x0) | pc==0 site (pc=0x0) | SAME site |
| id / entry | 1 / 0x100008 | 1 / 0x100008 | SAME |
| pc | 0x0 | 0x0 | SAME |
| ra | 0x0 | 0x1d8efc (= sub_001D8DE0+0x11c) | DIFFER |
| sp | 0x1ffff60 | 0x1fffdc0 | DIFFER |
| gp | 0x4a30f0 | 0x4a30f0 | SAME |
| v0 / a0 | 0x1 / 0x450000 | 0x467960 / 0x0 | DIFFER |
| scheduled | 22 | 213 (= t1 b240 scheduled) | DIFFER |
| Returner | 0x3dcc7c `JR $ra` (ra=0) | dispatch tail …→0x23d654→0x1d8efc (ra≠0) | DIFFER path |
| Invocation stack | empty (dormant printed) | empty (dormant printed; trace EOF empty) | SAME |
| Count in boot | id=1 ×1 of 10,705 | id=1 ×1 of 149,339 | SAME shape |

### f. Dormant id=1 full receipt (the main-return line)

Line 2489892 (block-239 span, 2 lines after last 29-signal @2489890,
1 line after first post-halt 31-wait @2489891):

```
[diag:dormant] id=1 entry=0x100008 pc=0x0 ra=0x1d8efc sp=0x1fffdc0
gp=0x4a30f0 v0=0x467960 a0=0x0 scheduled=213
trace=0x3252e8 -> 0x325260 -> … (325260/3252f8/320c48/321108/325250/325450
cycle ×~6) … -> 0x227f80 -> 0x23c808 -> 0x23d618 -> 0x23d660 -> 0x2c55d8
-> 0x3e6448 -> 0x2c6074 -> 0x2c51d0 -> 0x2c51d0 -> 0x2c51d0 -> 0x2c51d0
-> 0x23d688 -> 0x23d654 -> 0x1d8efc
```

Cross-note: tick 19440 (line 2445707, block 234) already samples
pc=0x1d8efc/sp=0x1fffdc0 — main's final pc/sp pair is visible 41,185
log lines before the dormant line.

## P32-2. 31-drain family + 29-halt split (Task 2)

### a. Drain-family table (9 funcs × 781 — header decls + body structure + trace edges)

Header: `$W/P1/output/ps2_recompiled_functions.h` (decls carry `sub_`
names only — no roles; roles below are structural: body size/range +
exact trace parent/children). All 9: post enter=exit=781.

| Func | Header line | Body (lines / range / switch-ifs) | Trace parents | Trace children | Per-iter structural role |
|---|---|---|---|---|---|
| `0031A3C0` | :5989 | 1054 / 0x31a3c0–0x31a6b8 / 190c+8if | root ×781 | 31AAF0 ×781 | root driver → pump-branch entry (mid-entry 0x31abd0) |
| `0037E120` | :6865 | 27814 / 0x37e120–0x3825f8 / 4406c+638if | root ×781 | 3825F8 ×781 | root driver → single-leaf branch (abuts 3825F8) |
| `003C1638` | :7669 | 2412 / 0x3c1638–0x3c1b80 / 338c+91if | root ×781 | — (leaf) | root top-level handler, no subcalls |
| `00317520` | :5906 | 50 / 0x317520–0x317530 / getter | 31AAF0 ×781 | — (leaf) | `v0=*(v1+8)` field load (`lw $v1,gp+0x2A74; jr $ra`) |
| `00317500` | :5905 | 69 / 0x317500–0x317520 | 31AAF0 ×781 | 317348 ×781 | trampoline |
| `00317348` | :5900 | 367 / 0x317348–0x317400 | 317500 ×781 | 227F58 ×781 + 31A6B8 ×781 | fan-out (mid-entry 0x31aac8 for 31A6B8) |
| `00227F58` | :2628 | 86 / 0x227f58–0x227f80 | 317348 ×781 | 326B88 ×781 | trampoline |
| `00326B88` | :6138 | 406 / 0x326b88–0x326c60 | 227F58 ×781 | 326EB0 ×1562 (2×/iter) | double-dispatch to pad-poll leaf |
| `003825F8` | :6866 | 217 / 0x3825f8–0x382688 | 37E120 ×781 | — (+1 stray 423DD0) | leaf handler under 37E120 |

(c=cases, if=ifs in generated entry-switch; loop=0 in all 7 probed.)

### b. Drain-chain edge table (exact post-exit parent→child counts)

| # | Edge | n | /iter |
|---|---|---|---|
| 1 | root → 31A3C0 → 31AAF0 | 781 | 1 |
| 2 | root → 31AAF0 (direct) | 781 | 1 |
| 3 | 31AAF0 → 317500 → 317348 → 227F58 → 326B88 | 781 each | 1 |
| 4 | 326B88 → 326EB0 | 1562 | 2 |
| 5 | 317348 → 31A6B8 (mid-entry 0x31aac8) | 781 | 1 |
| 6 | 31AAF0 → 317520 / 423DD0 / 423DE0 | 781 each | 1 |
| 7 | root → 37E120 → 3825F8 | 781 | 1 |
| 8 | root → 3C1638 (leaf) | 781 | 1 |
| 9 | root → 423DE0 | 784 (= 781 + 3) | ~1 |
| 10 | 326EB0 → 3FFBC0 → 3FFA58 (HLE `scePadGetState`/`scePadRead`, stub path ×2/iter, ZERO trace lines by design — HLE shims log only under `_DEBUG`) | stub 606 each/b241 | 2 |

31AAF0 total 1562 = 781 (via 31A3C0) + 781 (root-direct). 423DE0 total
1573 = 784 (root) + 781 (via 31AAF0) + 6 (via 382760) + 1 (via 376938)
+ 1 (via 31A6B8). 423DD0 total 783 = 781 (via 31AAF0) + 1 (via 382688)
+ 1 (via 3825F8). 31A6B8 total 789 = 781 (drain) + 5 (via 316F00) + 2
(self) + 1 (root). EOF ends inside the chain (…317348→317500 exits,
423DE0 pair, 31AAF0@0 exit @185293022).

### c. Drain-vs-tail split (repeating pump vs finite post-phase tails)

| Class | Members (post enter counts) | Shape |
|---|---|---|
| 781-pump (repeating) | 9-family ×781; 31AAF0 ×1562; 326EB0 ×1562; 423DE0 ×1573; 423DD0 ×783 | identical every iteration; 31-coupled (below) |
| 31 coupling | signal: `waker=-1 inInt=1 pc=0x423dd8 ra=0x31abf8` (= 31AAF0+0x108, iSignalSema 0xffffffbd); wait: `waker=4 pc=0x423de8 ra=0x31ac30` (= 31AAF0+0x140, WaitSema 0x44) | interrupt→t4 handshake; syscall b241 = WaitSema×303 + iSignalSema×303 ONLY |
| Finite tails (non-repeating) | 3E4AF0 ×115 (root leaf); 325260 ×80; 3252F8 ×48; 411C38/320C48/321108/325250/3252E8/325450 ×32; 411B08 ×16; 362660/3626D8 ×12; 38F738/371DD8 ×11; 88 pooled funcs ×256 exits | drain-adjacent teardown-ish chains (e.g. 325450→325260→3252F8, 411F38→411C38 fans); all balanced, all pre-existing funcs |
| In-phase gone | 394ED0/395000 ×0 post; 362DE8 ×0 post enters; 362CC8 ×1 | hash phase fully absent post-exit |

### d. Halt-split table (where 29 stops while 31 continues, b239–241)

Block spans: b239 2487366–2490771, b240 2490772–2492321, b241
2492322–2493828(EOF). Per-interval counts: b239 w29/s29/w31/s31 =
117/118/298/298; b240 = 0/0/303/303; b241 = 0/0/297/297.

| Order | Log line | Block | Event | Detail |
|---|---|---|---|---|
| … | … | 239 | 29 wait/signal pairs continue | wait `waker=1 ra=0x31aa8c` (= 31A6B8+0x3d4) / signal `waker=4 ra=0x31aae4` (= 31A6B8+0x42c), target=1 |
| LAST-1 | 2489876 | 239 | LAST 29 wait | `waker=1 pc=0x423de8 ra=0x31aa8c result=park` |
| LAST | 2489890 | 239 | LAST 29 signal (line 2524/3406 = 74.1% through b239) | `waker=4 … target=1 tStatus=2 … result=29` — wakes t1 |
| +1 | 2489891 | 239 | first 31 after last-29 (ADJACENT line) | `op=wait id=31 waker=4 ra=0x31ac30 result=park` |
| +2 | 2489892 | 239 | main dormant (ADJACENT line) | §P32-1f id=1 line — t1 returns 2 lines after its last wake |
| … | 2489893–2493828 | 239–241 | 31 continues alone (898-… waits+signals, no gap) | alternating wait/signal to EOF |
| EOF | 2493828 | 241 | LAST 31 wait = log EOF (trailing newline intact) | `waker=4 ra=0x31ac30 result=park` — never answered (+1 in-flight) |

29-signal side (t4, waker=4) also stops: t4's 29-branch ends with
main's return while its 31-branch (WAIT-31, scheduled ~300/block
through b241) continues — observed pattern, mechanism tabled as is.

### e. Handshake-balance table (totals + edges + artifacts)

| Row | 29 | 31 | 30 |
|---|---|---|---|
| waits / signals (reproduced) | 72178 / 72178 | 72959 / 72958 | 4 / 3 |
| vs N=72,176 | N+2 | N+783 | parked (no 4th signal) |
| Δ(31−29) | — | 781 = drain iters (§P32-2b) | — |
| pre-block-0 (T13) | 25 / 25 | 25 / 25 | — |
| blocks 0–238 | 72036 w / 72035 s | balanced | — |
| block 239 interval | 117 w / 118 s (+1 signal = answer to a b238 wait; boundary pairing) | 298 / 298 | — |
| blocks 240–241 | 0 / 0 | 600 / 600 | — |
| running balance (wait−signal) | min 0 / max 2 / final 0 | final +1 (EOF wait) | ends parked (wait @7224) |
| +2 29-edge localization | BOUNDED (in-flight ≤ 2, never negative) but NOT LOCALIZED — trace has no timestamps (same gap as T13 §T13-7) | — | — |
| +1 31-inflight localization | — | line 2493828 (EOF): thread-4 wait parked, no later signal | — |
| truncated-line artifacts (interleaved, counts unaffected) | 1: :1019100 signal fused with `[run:tick] tick=5640` | 2: :11171 signal fused with `[frame:upload]`; :944189 signal fused with `[run:tick] tick=4920` | 0 |
| first events | wait :644 (waker=1) / signal :650 (waker=4) | wait :263 (waker=4) / signal :648 (waker=-1) | signal :643 (waker=1) |

Sema-30 all 7 lines reproduced verbatim: :643 signal 0→1 / :645 wait
1→0 / :646 wait park / :706 signal wake t3 / :6972 wait park / :7022
signal wake t3 / :7224 wait park (4w/3s, t3 WAIT-30 ×241 + RUN b0).

## P32-3. Freeze sequencing + residue (Task 3a/b)

### a. Freeze table (last 5 tick pairs — T13 reproduced + block mapping)

Tick semantics: `[run:tick]` every 120 units; dma/gif = cumulative
counters. Full-run: 166 ticks (gapless, step 120) — counted via
SUBSTRING match; 23 tick lines are interleaved (fused with truncated
sema/dormant lines, e.g. tick 19200 @2399754 fused with an id=32
signal) and missed by line-prefix match (143).

| Tick | Log line | Block | pc | dma | gif | d_dma | d_gif | d_gif/d_dma |
|---|---|---|---|---|---|---|---|---|
| 19320 | 2423069 | 235 | 0x3827e0 | 2586548 | 69949 | 25124 | 680 | 0.02707 |
| 19440 | 2445707 | 234* | 0x1d8efc | 2611264 | 70617 | 24716 | 668 | 0.02703 |
| 19560 | 2467990 | 236 | 0x317244 | 2636275 | 71292 | 25011 | 675 | 0.02699 |
| 19680 | 2484929 | 238 | 0x3172e0 | 2660474 | 71947 | 24199 | 655 | 0.02707 |
| 19800 | 2491454 | 240 | 0x31ac30 | 2669132 | 72181 | 8658 | 234 | 0.02703 |
| 19920 | 2493756 | 241 | 0x31ac30 | 2669132 | 72181 | 0 | 0 | FROZEN |

*Tick/block grids are independent timers (tick 19440 lands in b234's
line span while 19320 lands in b235's — tabled as observed.)
Which stops first: NEITHER — same-tick freeze. Partial step (8658/234,
ratio held 0.02703) @19800 for BOTH, then 0/0 @19920 for BOTH. Tick pc
settles at 0x31ac30 (= 31AAF0+0x140, the 31-wait ra) with t4 sp
0x6088a0 for the final pair. No tick after 19920 (SIGTERM 30 s grace).

### b. Residue table (b241: 13/13 call-targets — COMPLETE list)

`[diag:stub]` semantics (fork `ps2_runtime.cpp:1106-1132`, read-only):
per-5 s-block guest CALL-target histogram via the dispatchGuestBranch
hook; `distinct` = total distinct targets; only TOP 30 rows printed.
b241 distinct=13 ≤ 30 → all 13 rows below are the COMPLETE block
footprint (b235–240 rows are top-30 truncations — §P32-3c). Counts:
606×3 + 303×10 = 4,848. All firstRa == lastRa (single call site each).

| # | Target | Count | /iter | firstRa=lastRa | Target in | Caller (ra in) | Body class | Post trace enters |
|---|---|---|---|---|---|---|---|---|
| 1 | 0x3ffa58 | 606 | 2 | 0x3271e8 | sub_003FFA58 | 326EB0+0x338 | HLE `scePadRead` (14-line shim) | 0 (HLE untraced by design) |
| 2 | 0x3ffbc0 | 606 | 2 | 0x326f24 | sub_003FFBC0 | 326EB0+0x74 | HLE `scePadGetState` (14-line shim) | 0 (HLE untraversed in trace) |
| 3 | 0x326eb0 | 606 | 2 | 0x326bf8 | sub_00326EB0 | 326B88+0x70 | recompiled (2580 lines) | 1562 |
| 4 | 0x3825f8 | 303 | 1 | 0x3825dc | sub_003825F8 | 37E120+0x44bc | recompiled (217 lines) | 781 |
| 5 | 0x423de0 | 303 | 1 | 0x31ac30 | sub_00423DE0 | 31AAF0+0x140 (= 31-wait ra) | recompiled (50 lines) | 1573 |
| 6 | 0x31aac8 | 303 | 1 | 0x3173e4 | sub_0031A6B8+0x410 (mid-entry) | 317348+0x9c | mid-function entry (no own file) | (31A6B8: 789) |
| 7 | 0x326b88 | 303 | 1 | 0x227f70 | sub_00326B88 | 227F58+0x18 | recompiled (406 lines) | 781 |
| 8 | 0x227f58 | 303 | 1 | 0x3173c4 | sub_00227F58 | 317348+0x7c | recompiled (86 lines) | 781 |
| 9 | 0x317348 | 303 | 1 | 0x317514 | sub_00317348 | 317500+0x14 | recompiled (367 lines) | 781 |
| 10 | 0x317500 | 303 | 1 | 0x31ac28 | sub_00317500 | 31AAF0+0x138 | recompiled (69 lines) | 781 |
| 11 | 0x423dd0 | 303 | 1 | 0x31abf8 | sub_00423DD0 | 31AAF0+0x108 (= 31-signal ra) | recompiled (50 lines) | 783 |
| 12 | 0x317520 | 303 | 1 | 0x31abe0 | sub_00317520 | 31AAF0+0xf0 | recompiled leaf getter (50 lines) | 781 |
| 13 | 0x31abd0 | 303 | 1 | 0x31a5a0 | sub_0031AAF0+0xe0 (mid-entry) | 31A3C0+0x1e0 | mid-function entry (no own file) | (31AAF0: 1562) |

The 13 form ONE connected chain (ra links close the loop through
31AAF0/31A3C0/37E120 — the drain footprint, §P32-2b). What REMAINS
after the collapse: the 31-pump call chain + its 2 HLE pad calls.
Dormant-trace cycle receipt (b241 @2492335, repeats): `0x3c1980 ->
0x31a490 -> 0x31abd0 -> 0x317520 -> 0x423dd0 -> 0x423de8 -> 0x31ac30 ->
0x317500 -> 0x317348 -> 0x227f58 -> 0x326b88 -> 0x326eb0 -> 0x3ffbc0 ->
0x3ffa58 -> 0x326eb0 -> 0x3ffbc0 -> 0x3ffa58 -> 0x31aac8 -> 0x423de0 ->
0x3825c0 -> 0x3825f8 -> 0x3c1980` (23 hops/iter, 326EB0→pad-pair ×2).

### c. Stub-collapse series (blocks 235–241)

| Block | Log line | distinct | Printed rows | Top-30 sum | Note |
|---|---|---|---|---|---|
| 235 | 2453403 | 218 | 30 (truncated) | 243,969 | FIRST EXIT EVENT |
| 236 | 2463459 | 211 | 30 (truncated) | 249,286 | — |
| 237 | 2473456 | 211 | 30 (truncated) | 248,192 | — |
| 238 | 2480949 | 211 | 30 (truncated) | 214,653 | — |
| 239 | 2487366 | 189 | 30 (truncated) | 205,504 | 29 halts mid-block |
| 240 | 2490772 | 189 | 30 (truncated) | 79,625 | main dormant; 29 gone |
| 241 | 2492322 | 13 | 13 (COMPLETE) | 4,848 | §P32-3b residue |

## P32-4. Silence re-audit over the exit region (Task 3c)

Region: log lines ≥ 2453403 (block 235 header) / trace lines ≥
185264991 (post-phase). Conventions per Part 24 §P24-1f/g (`[drop]`
single-site census + 12 exclusion rules — no new sites observed, no
rule changes proposed).

| Source | Marker | Total | Exit-region | Last before exit | First after exit |
|---|---|---|---|---|---|
| Drops | `[drop]` | 6 | 0 | :73 `[drop] syscall/dispatchSyscallOverride KE_ERROR syscall=0x5b …` (block 0) | none |
| RPC | `trace:unhandled` | 4 | 0 | :5143 `[IOP/RPC trace:unhandled] sid=0x534e44 …` (block 2) | none |
| CD | `lbn=` | 810 | 0 | :7174 `[diag:cd] sceCdRead payload lbn=0x4311f …` (block 2) | none |
| SIF | `SIF…load` | 21 | 0 | :1055 `[SIF module] load id=21 … VOIPF.IRX` (block 0) | none |
| GS kicks | `gs:kick` | 96 | 0 | :2638 `[gs:kick] idx=95 drawing=1 …` (block 1) | none |
| gif (broad) | `[gif` | 214 full-log (T13) | 0 | — | none |
| Trace 394/395 | enters | 0 post | 0 | last in-phase (inv 72175) | none |
| New guest funcs | post-only | 0 of 113 | 0 | — | none |

All T13 silence readings reproduce to the line number.

## P32-5. Post-exit state table (von-Neumann snapshot — Task 4.1)

State at EOF (log 2493828 / trace 185293022). "Next-boot invariant"
= what the reboot must reproduce at the same landmarks (T15 checks).

### a. Per-thread state (@ block 241)

| Thread | Entry | status | waitId | pc | sp | scheduled b241 (b240) | State |
|---|---|---|---|---|---|---|---|
| t1 (main) | 0x100008 | 5 DORMANT | 0 | 0x0 | 0x1fffdc0 | 0 (213) | RETURNED (dormant @2489892, empty invocations) |
| t2 | 0x3e3be0 | 2 WAIT | 26 | 0x423de8 | 0x51ec20 | 0 (0) | parked (never scheduled post-boot) |
| t3 | 0x31ac60 | 2 WAIT | 30 | 0x423de8 | 0x6188a0 | 0 (0) | parked (4w/3s, no release at exit) |
| t4 | 0x31ac08 | 2 WAIT | 31 | 0x423de8 | 0x6088a0 | 303 (304) | LIVE — 31-drain pump (sole scheduled thread) |
| t5 | 0x382740 | 2 WAIT | 32 | 0x423de8 | 0x622480 | 0 (213) | parked (scheduled series == t1's exactly, b234–241: 602/598/610/603/593/608/213/0 — coupled to main, winds down with it) |
| t6 | 0x3c19a8 | 2 WAIT | 36 | 0x423de8 | 0x512aa0 | 0 (0) | parked (WAIT-36 ×242) |

### b. Per-device state

| Device | State | Receipt |
|---|---|---|
| sema-29 | HALTED, balanced 72178/72178, balance 0 | last signal @2489890; 0 events b240–241 |
| sema-30 | PARKED 4w/3s (waiters=1) | 7 lines, last @7224 (wait, waker=3) |
| sema-31 | LIVE, 72959/72958, +1 in-flight | EOF = parked wait @2493828 (waker=4); b241 297/297 |
| sema-32 | QUIET (t5 parked, scheduled 0) | interleaved signal line @2399754 (tick-fused artifact) |
| dma/gif | FROZEN same-tick @ 2669132/72181 | 0/0 deltas ticks 19800→19920; pc settled 0x31ac30 |
| call footprint | 13-target drain chain (§P32-3b) | distinct 13, counts 606×3+303×10 |
| syscalls | WaitSema×303 + iSignalSema×303 ONLY (b241) | PollSema/FlushCache/SignalSema gone with 29 (b239: 5 ids; b240: 5 ids; b241: 2 ids) |
| trace stack | EMPTY (0 live frames) | all 1,073 funcs enter=exit; 113 post funcs balanced (±1 on driver pair netting the 2 live frames) |
| dormant id=1 | DONE (×1 @2489892) | scheduled=213; no second firing |
| CD/SIF/GS/RPC/drops | SILENT since ≤ block 2 | §P32-4 |

### c. Next-boot invariants (reboot must reproduce at the same landmarks)

| # | Landmark | Invariant value |
|---|---|---|
| 1 | First `0x362DE8` enter | trace line 19,385 |
| 2 | Stub preamble | b0/b1 distinct 897/588 (T13; T11 differed 961/497 — preamble NOT invariant, steady-@-b2 is) |
| 3 | In-phase distinct | 222 ×233 (blocks 2–234) |
| 4 | FIRST EXIT EVENT | block 235 distinct 218 @ ~line 2453403 |
| 5 | Collapse | 218 → 211×3 → 189×2 → 13 (blocks 235–241) |
| 6 | N | 72,176 balanced enters=exits (preamble variance may shift N by tens — T15 records N2) |
| 7 | 29-halt | last 29-signal mid-b239, then 31-only |
| 8 | Main dormant | id=1 ×1, pc=0x0, 2 lines after last 29-signal |
| 9 | Freeze | dma/gif partial-step then 0/0 same-tick pair |
| 10 | EOF shape | 31-wait parked; trace stack empty; 0 post-only |

## P32-6. Next-park spec for T15 (Task 4.2/4.3 — signature watchlist + miner rows)

### a. Watchlist table (monitor-pollable triggers; T13 baseline = "absent unless noted")

| # | Signal | Trigger predicate (poll each 15 s like T13's monitor) | T13 baseline |
|---|---|---|---|
| W1 | New stub phase after residue | any `[diag:stubs]` block with distinct ∉ {222, 218, 211, 189, 13} after block 5 | absent (exit = 222→218→211→189→13) |
| W2 | Residue break | any post-b241 block with distinct ≠ 13 (if boot runs past) | n/a (EOF @b241) |
| W3 | Main wake from dormant | any `[diag:thread] id=1` with status ≠ 5 after a status=5 sample | absent (5,5 @b240–241) |
| W4 | Second dormant firing | 2nd `[diag:dormant] id=1` line | absent (×1 @2489892) |
| W5 | First new guest event | any `lbn=` past :7174 / SIF-load past :1055 / GS-kick past :2638 / `trace:unhandled` past :5143 / `[drop]` past :73 | absent (all silent ≤ block 2) |
| W6 | New caller | any `0x362DE8` enter whose indent parent ≠ `sub_00363490` (trace) | absent (×72,176 single caller) |
| W7 | dma/gif unfreeze | any `[run:tick]` with dma ≠ 2669132 or gif ≠ 72181 after a frozen pair | absent (frozen @19920) |
| W8 | Second exit (31-halt) | any post-exit block with w31 = 0, or new status-5 for id ∈ {4, 5, 6} | absent (31 live to EOF) |
| W9 | 4th sema-30 signal | 8th `id=30` line (`op=signal`, `waiters 1→0`, `target=3`) | absent (7 lines, parked) |
| W10 | New stub-print shape | any `[diag:stub]` row with firstRa ≠ lastRa in a ≤30-distinct block | absent (all 13 equal) |
| W11 | Rate-shape deviation | any 60 s slice with dormant/inv ≠ 2.0000 in-phase or d_gif/d_dma outside 0.02703±0.0002 | T13: 2.0000 slices 7–17; ratio ±0.0001/164 |
| W12 | Trace-stall trip | trace bytes unchanged 120 s (T13's monitor rule, kept) | n/a (monotonic to EOF) |

### b. Miner-row table (10 rows T15's analysis MUST emit)

| # | Row | Spec | T13 value (comparison) |
|---|---|---|---|
| M1 | Block of next event | first post-b241 `[diag:stubs]` block # with distinct ≠ 13 (or "none — EOF @b241") | none (exit @235, EOF @241) |
| M2 | N2 count | `0x362DE8` enters = exits on the new boot (± preamble note) | N = 72,176 |
| M3 | Handshake deltas | 29w−N2, 31w−N2, s29−w29, s31−w31 at exit | +2, +783, 0, −1 |
| M4 | Main-return line | `[diag:dormant] id=1` line # + (ra, sp, v0, a0, scheduled) | :2489892, 0x1d8efc/0x1fffdc0/0x467960/0x0/213 |
| M5 | Halt-split lines | last-29 line, first-post-31 line, dormant line, adjacency? | 2489890/2489891/2489892 adjacent |
| M6 | Drain iters | Δ(31−29) + 9-func post counts (each = iters?) | 781; 9 ×781 |
| M7 | Freeze pair | last two ticks (dma/gif/deltas), same-tick? | (8658/234) → (0/0) same-tick |
| M8 | Residue rows | b-last distinct + per-target (count, firstRa==lastRa?) | 13; 606×3+303×10; all equal |
| M9 | Stack at next cap | live frames at EOF + post-only func count | 0 live; 0 post-only of 113 |
| M10 | Silence lasts | last-line-before-exit per source (drop/RPC/CD/SIF/GS) + exit-region counts | 73/5143/7174/1055/2638; 0/0/0/0/0 |

## P32-7. Exact commands + receipt paths

From `/Users/bradrichardson/dev/ssx3` unless noted; `W`, `LOG`, `T`
as above. All receipt accesses read-only (grep/sed/python reads,
`tail -c` seeks); no lease, no boots, no builds, no fork writes:

```
# Reads (lease-free; T13 + P31 + P24-1f/g + /tmp/t13-{mine,blocks,trace,cycle}.py patterns)
read local/research/T13/REPORT.md (all); REPORT.md Part 31 + P24-1f/g
read /tmp/t13-mine.py /tmp/t13-blocks.py /tmp/t13-trace.py (pattern conventions only)
# Miners (written to /tmp/p1ai/, uncommitted; one IndexError-class fix: post-exit
#   sequence must anchor on LAST 362DE8 exit — full-pass v1 stored 92M rows, superseded
#   by tail-seek v2; v1 headline counts kept, v1 order list discarded)
mkdir -p /tmp/p1ai
write /tmp/p1ai/log_exit.py (single-pass: status-5/t1/stacks/handshakes/sema30/dormant/
  stubs-235-241/ticks/syscalls/silence/tail)
python3 /tmp/p1ai/log_exit.py LOG > /tmp/p1ai/log_exit.txt (164 lines)
write /tmp/p1ai/log_follow.py (first-events/ boundary-31/tick-substring/t4-t5/dormant-full/ balance)
python3 /tmp/p1ai/log_follow.py LOG > /tmp/p1ai/log_follow.txt
write /tmp/p1ai/trace_post.py (single full streaming pass: last362 enter/exit, pre/post sets,
  post-only, per-func counts, live frames; ~5 min wall)
python3 /tmp/p1ai/trace_post.py T > /tmp/p1ai/trace_post.txt
write /tmp/p1ai/tail_unwind.py (tail -c 6MB seek: unwind order, depth profile, window counts)
python3 /tmp/p1ai/tail_unwind.py T > /tmp/p1ai/tail_unwind.txt
write /tmp/p1ai/callgraph.py (seeded-stack edge census + sweep-CSV ra mapping)
python3 /tmp/p1ai/callgraph.py > /tmp/p1ai/callgraph.txt (root total 4049 verified)
# Targeted receipts (read-only)
grep -n "status=5" LOG (2); sed b241 stub block; sed threads b239-241
grep -c 003FFBC0/003FFA58 T (0/0 — full-stream C greps)
grep header decls (drain+residue+1D8DE0 addrs)
sed EeScheduler.cpp:630-745 (dormant sites); sed Dispatcher.cpp:253-300,345-360 (id names)
grep "diag:stub]" ps2_runtime.cpp + sed :1090-1132 (histogram+top30 semantics)
cat HLE shim bodies (3FFA58/3FFBC0); structural grep of 7 big bodies (case/goto/if/loop)
# Report (this Part)
(edit_file append Part 32 in 1 chunk)
git add -f local/research/P1/REPORT.md
git commit -m "[P1ai] ..." (trailer Orchestrated-By: Muse Code; NO push)
```

Receipt paths: `/tmp/p1ai/log_exit.py|.txt`, `/tmp/p1ai/log_follow.py|.txt`,
`/tmp/p1ai/trace_post.py|.txt`, `/tmp/p1ai/tail_unwind.py|.txt`,
`/tmp/p1ai/callgraph.py|.txt` (all uncommitted scratch; tables above
are the evidence).

## P32-8. What I could not do (gap rows)

- Localize WHICH 2 log lines form the +2 29-edge (29w = N+2): the
  trace carries no timestamps, so pump-cycle↔invocation mapping past
  the proxy is derived, not observed (same gap as T13 §T13-7; bounded
  here: running in-flight min 0 / max 2 / final 0).
- Time-resolve individual 31-drain iterations inside a 5 s block or
  attribute the 303-vs-297 stub-vs-handshake per-block skew beyond
  window-boundary attribution (both counters' windows tabled as is).
- Name guest-level roles (source names) for the 9 drain funcs beyond
  structural roles: the header carries `sub_` names only, and bodies
  call through dispatchGuestBranch/JALR (zero static `sub_` refs in
  all 9 .cpps) — callee structure came from the trace, not the text.
- See HLE pad-shim internals beyond the 14-line trampolines
  (`ps2_stubs::scePadRead/scePadGetState` bodies live outside this
  diag brief's read scope needs; zero trace lines is by `_DEBUG`-only
  logging design).
- Attribute the t5≡t1 scheduled-coupling host/guest cause beyond the
  exact series match (602/598/610/603/593/608/213/0 both, b234–241).
- Session wall time ≈ 09:40–11:00Z (~80 min active), inside the 4 h box.

## Part 33 (P1aj): Drain-termination diagnosis — what ends the 31-drain + next-experiment spec (no boot)

Brief `local/muse/prompts/P1aj.md`. DIAGNOSIS brief on committed
logs — no boot, no lease of any kind, no fork changes, no `adb`.
Tables, no verdicts. Stale-reading guard: `local/research/T15/REPORT.md`
(all of it) + P1 REPORT Part 32 (P1ai's post-exit diagnosis) +
`local/research/T13/REPORT.md` §T13-1 (exit table).
`W=/Volumes/Extreme SSD/ps2recomp-spike`,
`LOG=$W/P1/run/boot-t15-1.log` (2,857,096 lines),
`T=$W/P1/run/ps2_log-t15-1.txt` (187,727,172 lines, 6,659,595,180 B),
T15's `blocks.tsv` (477) + `ticks.tsv` (267), T13's logs + TSVs.
Scratch `/tmp/p1aj/` (miners kept there, uncommitted); this Part is
the only evidence. Trace never copied — one full streaming pass +
`tail -c` seeks + `grep -c` streaming counts only.

Headline receipts: the drain is VBLANK-paced (1 iter/VBLANK, ~60/s):
4 INTC-handler entries (cause 2 → 0x3c1980 counter++ and 0x3825c0 →
3825F8; cause 3 → 0x31a490 FPU-wrap → iSignalSema; cause 10 = TIMER1 →
0x3e4db8 every ~6.8 VBLANKs) + t4's pump leg (WaitSema → spin while
`*(s0+0x20)==0`). Fixed point from iter 2 (iter 1 carries all 340
finite-tail lines; iters 2–71,761 identical 15-func/34.29-line shape;
iter 71,762 SIGTERM-cut at 28 lines, all balanced). Three live
signal/loop guards could end it (`31AAF0@0x31abe8` skip-signal,
`31AAF0@0x31ac34` t4 loop-exit → Wakeup+Sleep, `31A6B8@0x31aad4`
29-skip — the 29-halt is branch-suppression, not death) + 3825F8's
saturating counter (fire path needs state==4, never observed);
all fixed 71,762×. Monotonic counters are write-only or never-fire
(no finite horizon under ~2.2 yr). Missing signals: 4th sema-30
needs main's signal leaf (main dormant); IOP reply needs
`_request_end` (0× all boot); `0x3C45C0` needs callers that never
execute (0× all boot) + caller-state s2==0. Block-N sections cover
window N−1 (4 exact lag matches — dissolves P32-8's stub skew).

## P33-0. Rule record (no lease, no boots, no fork changes)

| Item | Value |
|---|---|
| P-lane lease | Never touched (no boots; lease file never created/checked) |
| Boots / harness runs | 0 (read-only mining of T15's + T13's committed receipts) |
| Fork changes | 0 (fork + `$W/P1/output` sources read read-only; no edits/commits/push/pull) |
| `adb` | Not used |
| Other agents' dirs | Read-only (`local/research/T13|T15`, `/tmp/t13-*.py` patterns only) |
| 6.6 GB trace | 1 full streaming pass + `tail -c` seeks + streaming `grep -c`; never copied |
| ssx3 files changed | `local/research/P1/REPORT.md` ONLY (this Part, appended); commit prefix `[P1aj]`; NO push |

## P33-1. P32-6 reconciliation (Task 1 — what did T15 answer?)

### a. Watch table (P1ai W1–W12 vs T15's 7 generic + 2 gated)

T15 generic watches (T15-0): main-wake, stub-post, guest-event,
dma-gif-unfreeze, pump-idle, trace-stall-120s, new-caller (trace-only
post-hoc) + gated extras sema30-8th, thread3-release.

| W# | P1ai predicate | T15 coverage | Post-hoc (P1aj) | State |
|---|---|---|---|---|
| W1 | distinct ∉ {222,218,211,189,13} after b5 | stub-post (13 ×236, same 13) | — | covered, silent |
| W2 | post-b241 distinct ≠ 13 | stub-post (same predicate) | — | covered, silent |
| W3 | id=1 status ≠ 5 after a 5 | main-wake (5 ×237, b240–476) | — | covered, silent |
| W4 | 2nd `[diag:dormant] id=1` | NONE (no dormant-count watch) | total id=1 = 1 (@2494024) | open-in-T15, answered-here: absent |
| W5 | new lbn=/SIF/GS/RPC/drop | guest-event (0 of each ≥2461202) | region re-audit 0/0/0/0/0 (§P33-3b) | covered, silent |
| W6 | new 362DE8 caller | new-caller (single ×72,176) | post 362DE8 enters = 0 (§P33-2a) | covered, silent |
| W7 | dma/gif unfreeze | dma-gif-unfreeze (160× 0/0 @2669132/72181) | — | covered, silent |
| W8 | w31=0 block, or new status-5 id∈{4,5,6} | pump-idle (31w 295–307/post block, never 0) | status=5 ×237, ALL id=1 (0 for ids 2–6; §P33-3a) | covered, silent |
| W9 | 8th id=30 line | sema30-8th gated (n=7, last @7225) | 7 lines tabled (§P33-3b) | covered, silent |
| W10 | firstRa≠lastRa in ≤30-distinct block | NONE | b241+b476: all 13 equal (§P33-3a) | open-in-T15, answered-here: absent |
| W11 | dormant/inv ≠ 2.0000 in-phase, or gif/dma outside 0.02703±0.0002 | NONE as watch (rate table only) | T15-2: 2.062–2.123 all in-phase slices (never 2.0000); ratio 0.02703±0.0001 | open-in-T15, WOULD HAVE FIRED in-phase |
| W12 | trace stall 120 s | trace-stall-120s (monotonic to EOF) | — | covered, silent |

Covered live: 9 of 12 (W1,2,3,5,6,7,8,9,12). Silent: all 9.
Answered only post-hoc here: W4 (absent), W10 (absent), W11 (fired).

### b. Miner table (P1ai M1–M10 vs T15 §T15-2/3)

| M# | P1ai row spec | T13 value | T15 value (§T15-2/3 or P1aj) | State |
|---|---|---|---|---|
| M1 | Block of next event | none (EOF @b241) | none (no post-241 event to cap b476) | answered |
| M2 | N2 (362DE8 enters=exits) | 72,176 | 72,176 (first @19385, last exit @185264990) | answered, exact |
| M3 | 29w−N2, 31w−N2, s29−w29, s31−w31 | +2,+783,0,−1 | +2,+71,764,0,−1 (72178/72178, 143940/143939 — totals §P33-3a) | answered (derived) |
| M4 | Main-return line + (ra,sp,v0,a0,sched) | :2489892, 1d8efc/1fffdc0/467960/0/213 | T15: NOT emitted → P1aj: :2494024, SAME ra/sp/v0/a0, sched=11 | open-in-T15, closed-here |
| M5 | last-29, first-post-31, dormant, adjacency? | 2489890/2489891/2489892 adjacent | T15: last-29 @2494022 only → P1aj: 2494022/2494023/2494024 adjacent (§P33-3c) | open-in-T15, closed-here |
| M6 | Δ(31−29) + 9-func post counts | 781; 9×781 | 71,762; 9× 71762/71762 each (§P33-2a) | answered |
| M7 | Last two ticks, same-tick? | (8658/234)→(0/0) same-tick | frozen pair (0/0)→(0/0) @2669132/72181; partial→frozen transition earlier (13802/374 @ticks 12720→12840, then 160 frozen) | answered (transition + hold) |
| M8 | b-last distinct + per-target counts, ra=? | 13; 606×3+303×10; all equal | T15: "SAME 13 @598/299" → P1aj: full rows b241 (610×3+305×10) + b476 (598×3+299×10), all firstRa==lastRa (§P33-3a) | partial-in-T15, completed-here |
| M9 | Live frames at EOF + post-only | 0 live; 0 of 113 | 0 live (empty stack); 0 post-only of 113 (preset 1072 +362DE8; §P33-2a) | answered |
| M10 | Silence lasts + exit-region counts | 73/5143/7174/1055/2638; 0s | 73/5144/7175/1056/2639 (@+1 shifts); region ≥2461202: 0/0/0/0/0 re-audited (§P33-3b) | answered |

Got values from T15: M1, M2, M3, M6, M7, M9, M10 (+M8 partial).
Stayed open past T15, closed by P1aj: M4, M5 (+M8 full rows).

### c. Invariant table (P1ai §P32-5c 10 invariants vs T15 §T15-1)

| # | Invariant (landmark) | T13 (P32) | T15 observed | P1aj check |
|---|---|---|---|---|
| 1 | First 362DE8 enter @19385 | @19385 | @19385 | bound_ok=True in stream pass (§P33-2a) |
| 2 | Preamble b0/b1 (NOT invariant; steady-@-b2 is) | 897/588 | 887/603 (third pair; steady @b2) | blocks.tsv b0/b1; deviation-as-expected |
| 3 | In-phase distinct 222 ×233 (b2–234) | ×233 | ×233 | blocks.tsv |
| 4 | FIRST EXIT @b235 distinct 218 | @line 2453403 | @line 2461202 (~1,183 s wall) | reproduced (line shifted +17,799) |
| 5 | Collapse 218→211×3→189×2→13 (b235–241) | 211×3, 189×2 | 211×2, 189×3 (b238 reads 189) | DEVIATED: one-block transitional shift |
| 6 | N = 72,176 | 72,176 | 72,176 (75-ramp + 72,101 steady, bit-exact chunks) | reproduced to the digit |
| 7 | 29-halt mid-b239, then 31-only | 74.1% (117/298) | 9.1% (5/296, last-29 @2494022) | shape reproduced, position differs (§P33-3c) |
| 8 | Dormant id=1 ×1, 2 lines after last-29 | :2489892, sched 213 | :2494024, sched 11, same ra/sp/v0/a0 | adjacency reproduced; sched differs (11 = window-239 mains) |
| 9 | Freeze partial-step then 0/0 same-tick | (8658/234)→(0/0) | (13802/374)→160× (0/0) @same 2669132/72181 | reproduced (extended hold) |
| 10 | EOF: 31-wait parked; empty stack; 0 post-only | wait @2493828; empty; 0 | wait @2857096 (EOF); empty; 0 of 113 | reproduced (tail = signal, dormant id=-1, wait) |

Reproduced: 1, 3, 4, 6, 7(shape), 8(adjacency), 9, 10. Deviated: 2
(expected), 5 (boundary shift). Quantitative deltas: 4 (line), 7
(position), 8 (sched).

## P33-2. Drain fixed-point analysis (Task 2 — 71,762 iters)

Method: single streaming pass (`/tmp/p1aj/trace_drain.py`):
provisional post boundary = T15's last-362DE8-exit 185264990,
verified at EOF (`bound_ok=True`, 0 post 362DE8 lines). Iteration
marker = depth-0 enter of `0031A3C0` (P32-2b root, 1×/iter).
`tail -c` passes for residuals/decay/edge iters. Trace never copied.

### a. Iteration table (per-1000 chunks — fixed point from iter 2)

72 chunks (71×1000 + 762). Steady-15 = 9-family + 31AAF0 + 326EB0 +
423DE0 + 423DD0 + 31A6B8 + 3E4AF0. Full table:
`/tmp/p1aj/drain_chunks.tsv` (uncommitted scratch).

| Chunk | Iters | Trace lines | Lines/iter | 9-fam/iter | 31AAF0/326EB0/423DE0/423DD0/31A6B8/iter | 3E4AF0 | Distinct |
|---|---|---|---|---|---|---|---|
| 0 | 1–1000 | 185265557–185300538 (34,982) | 34.982 | 1.0000 ×9 | 2/2/2.001/1/1.004 | 146 | 55 (15 + 40 resid, ALL in iter 1) |
| 1–70 | steady ×70 | — | 34.286–34.294 | 1.0000 ×9 | 2/2/2/1/1 exact | 146/147 alternating | 15 |
| 71 | 71001–71762 | 187701047–187727172 (26,126) | 34.286 | 1.0000 ×9 | 2/2/2/1/1 exact | 112 (/762) | 15 |

- Residuum: pre-marker unwind = 566 lines / 282 enters / 74 distinct
  (top: 411C38×32, 411B08×16, 362660/3626D8×12, 38F738/371DD8×11;
  incl. 362CC8×1, 376938×5, 363490×2 — the N+1 + driver re-enters,
  all pre-marker). Chunk-0 residual = 340 enters / 40 distinct, ALL
  in iter 1 (buckets 101–1000: 0; last resid iter 1 @185266273):
  325260×80, 3252F8×48, 320C48/321108/325250/325450/3252E8×32
  (P32's T13 finite tails, exact counts) + 33 small strays.
- Strays vs exact multiples (identical across runs — fixed structure):
  423DE0 +11 (10 pre-marker + 1 chunk-0; T13: same +11),
  423DD0 +2 (both pre-marker; T13: same +2),
  31A6B8 +8 (4 pre-marker + 4 chunk-0; T13: same +8).
- 3E4AF0 cadence: 10,513 post enters (21,026 lines, matches T15);
  per-1000: 146/147 (T13: 115/781 = 0.1472/iter vs T15 0.1465/iter);
  inter-arrival gaps (iters): 6×1823 + 7×8688, min 6 max 7 —
  strictly periodic, no drift.
- Depth-0 roots post: 369,352 total / 20 distinct — the SAME 20 rows
  as P32-1d's T13 4,049 (423DE0 71765=+3; 37E120/3C1638/31A3C0/31AAF0
  71762; 3E4AF0 10513; 376938 4; 382760 4; 423DC0 3; 38F300/363490/
  382650/316F00 2; 7×1: 395288/232AE0/31A6B8/2C5570/23D660/23D618/
  1D8DE0). Post depth min/max = 0/13. 394ED0/395000 = 0/0 post.
- First vs last iteration: iter 1 = steady-15 + 340-line finite tail
  (transitional; `/tmp/p1aj/drain_edge_iters.txt`); iters 2–71,761 =
  pure fixed point; iter 71,762 = 28 lines (31A3C0-leg + 423DE0 +
  31AAF0-direct leg complete; 37E120/3825F8/3C1638 pairs missing —
  SIGTERM landed between root dispatches; every enter balanced →
  empty stack at EOF holds).
- Sema values (no per-iter join exists — trace has no timestamps):
  id=31 `count=0->0` on 287,878/287,879 lines (1 tick-fused
  truncation artifact @tick 5040); all 143,940 waits identical
  (`waker=4 pc=0x423de8 ra=0x31ac30 waiters 0->1`); all 143,938
  non-fused signals identical (`waker=-1 pc=0x423dd8 ra=0x31abf8
  inInt=1 target=4 invKind=0 invDepth=1`); per-block w31/s31 =
  blocks.tsv col (295–307/post block). Sema state is a fixed point.

### b. Input table (per-iteration INPUTS of the live path)

Roots are scheduler-dispatched, NOT guest-called (history hops at
mid-pcs with no histogram row): `dispatchIrq` sets a0=cause,
a1=handler.argument (registered constants), ra=0
(EeScheduler.cpp:1919–1972). Handler table (all 477 blocks,
unchanged): id=1 cause=10→0x3e4db8 (TIMER1, 9+timer site :2446);
id=2 cause=3→0x31a490 (VBLANK-end, :2611); id=3 cause=2→0x3825c0
(VBLANK-start, :2605); id=6 cause=2→0x3c1980; (id=4,5 causes 5,7:
no raise site in build — dead); dmac-1→0x382650 (fires 0× post-exit).

| Func (entry/iter) | Inputs read per iter | Changed across 71,762? |
|---|---|---|
| 31A3C0 @0x31a490 (VBLANK-end) | a1 = 0x31abd0 (host-registered arg); FPU f0–f31 (saved/restored, untested) | NO (a1 const; no branches) |
| 37E120 @0x3825c0 (VBLANK-start) | a0 = 2 (host-set cause); a1 = struct ptr (registered const) | NO (only the 9-insn tail entry executes; 27k body off-path) |
| 3C1638 @0x3c1980 (VBLANK-start) | `*(0x50AAA8)` (++, write-back) | YES-monotonic (unread anywhere; 2^32 horizon ≈2.2 yr @60Hz) |
| 3E4AF0 @0x3e4db8 (TIMER1, ~1/6.8) | T1 COUNT/COMP/MODE (0x10000800/820/810); `*(0x450DE0)`; `*(0x450DA8)` (JALR vector); ctrs 0x450DCC/DD0 (++) | periodic (T1 re-armed; ctrs ++; vector stays 0) |
| 317520 (nested) | `*(gp+0x2A74)`, `*(ptr+8)` (return v1) | NO (same addrs; values unprobed) |
| 317500 (nested) | `*(gp+0x2A74)` → a0 for 317348 | NO |
| 317348 (nested) | s1+0x18 ctr (++, write-back); s1+0x24/0x28 floats (s0 deriv); vtbl `*(s1+0x5C)`/`*(s1+8)` (+0x38/0x3C/+0x28/0x2C JALR ptrs) | ctr YES-monotonic (write-only); s0==0 fixed; JALR targets fixed (227F58, 31A6B8@0x31aac8) |
| 227F58 (nested) | `*(gp-0x850)` (a0; null-test) | NO (nonzero all 71,762) |
| 326B88 (nested) | N=`*(s0+0x2EE8)`(=2); i=`*(s0+0x2EE4)` (mod-30++); array s0+0x2EEC; JALR vtbl | i YES-periodic (30-cycle; feeds addr math only, no branch); N==2 fixed |
| 3825F8 (nested) | a1+0x5ABC ctr (++ always); a1+0x5A8C state; a1+0x5AB8 limit; a1+0x5AC8 arg | ctr YES-monotonic; state/limit: fire ×0 (state≠4 OR ctr<limit — undetermined) |
| 31AAF0-leg1 @0x31abd0 (in-IRQ) | v1=317520 ret; guard `*(v1+0x4038)`; sema id `*(v1+0x4034)`(=31) | NO (guard 0 all 71,762 → signal always fires) |
| 31AAF0-leg2 (t4, resume @0x31ac30) | s0+0x4034 (sema 31); loop flag `*(s0+0x20)`; s0 (t4 ctx, pump-entry provenance) | NO (flag 0 all 71,762 → loop always repeats) |
| 31A6B8 @0x31aac8 (nested) | a0+0x1C (signal gate); a0+0x18 (sema id) | gate NO (0 post-halt → 29-skip; was ≠0 in-phase) |
| 326EB0 ×2 (nested) | s0+0x48 (≠0); s0+8 (pad handle); pad HLE returns (3FFBC0/3FFA58: fixed — HLE digital mode 0x41, Pad.cpp:8,48); ~25 live-span branches | NO (pad-pair 2×/iter exact; 11 other HLE targets dormant) |
| Sema-31 (syscall pair) | count 0, waiters flip 0↔1, waker/target fixed | NO (287,878 identical) |

Changed-but-harmless: 4 monotonic write-only/never-fire counters +
2 periodic cycles (mod-30, T1 re-arm) + 2 slow ++ (0x450DCC/DD0).
No input drifts toward any guard threshold observably.

### c. Terminator table (live-path guards — which func COULD end the drain?)

Static reads only (`$W/P1/output/sub_*.cpp`); directions below are
PROVEN by exact per-iter trace/log counts (any flip changes
children/handshakes). "Ends how" = the first observable break.

| # | Func | Guard pc + condition | Fixed direction (71,762×) | If flipped, ends how (first break) |
|---|---|---|---|---|
| T1 | 31AAF0-leg1 | 0x31abe8 `bnez *(v1+0x4038)` → skip iSignal | NOT taken (v1-word 0; 143,938 signals) | signal skipped → t4 starves → W8 (w31=0 block) |
| T2 | 31AAF0-leg2 | 0x31ac34 `beqz *(s0+0x20)` → repeat wait | TAKEN (flag 0; loop never exits) | t4 exits pump → WakeupThread(423CD0)+SleepThread(423CC0) → W8 from waiter side |
| T3 | 31A6B8 | 0x31aad4 `beqz *(a0+0x1C)` → skip SignalSema | TAKEN post-halt (0; was ≠0 in-phase) | 29-signal resumes (main still dormant — dormant ≠ waiting; W5-silent) |
| T4 | 3825F8 | 0x382614 `bne *(a1+0x5A8C),4` → skip; 0x382624 `v1<limit` → skip fire | fire ×0 (state≠4 OR ctr<limit) | JAL 423DD0 fires + state→5 + ctr reset (extra signal/iter) |
| T5 | 227F58 | 0x227f60 `beqz *(gp-0x850)` → skip 326B88 | NOT taken (nonzero) | pad leg skipped 1 iter (residue dip, not halt) |
| T6 | 317348 | 0x3173a0 `beq s0,-1` → skip loop; 0x3173c4 loop (trips = s0+1) | NOT taken; exactly 1 round (s0==0) | 0/2+ ×227F58 (shape break, W2/W10) |
| T7 | 326B88 | 0x326bac `blez N` → skip; loop while s3<N | NOT taken; exactly 2 rounds (N==2) | 0/3+ ×326EB0 (pad-pair ratio break) |
| T8 | 326EB0 | entry 0x326ed4/0x326ef4 + ~25 live-span branches; dormant: JAL 3FF708 + 11 HLE + 3FFBC0@0x327080 | fixed (pad-pair 2×/iter exact) | new HLE target in residue (W2/W10); per-branch taken/nt NOT individually simulated (gap) |
| T9 | 37E120-hdlr | 0x3825c8 `beq a0,2` else BREAK | TAKEN (a0=cause, host-set) | BREAK fault (0 observed; unbreakable w/o re-registration) |
| T10 | 3E4AF0-hdlr | 0x3e4e4c `beql *(0x450DA8),0` → skip JALR; 8-round loop | TAKEN (vector 0; loop 8 fixed) | JALR `*(0x450DA8)` fires (latent callback; new caller/shape) |
| T11 | 31A3C0-hdlr | none (JALR $a1; a1=0x31abd0 host-set) | — (FPU wrap + ei) | cannot (no branch; needs re-registration) |
| T12 | 3C1638-hdlr | none (`*(0x50AAA8)++`; sync; ei; ret 0) | — | cannot (no branch; 2.2-yr overflow horizon) |
| T13 | host VBLANK | EeScheduler:2605/:2611 raise causes 2/3 @60Hz | 71,762 consecutive (1 iter/VBLANK) | host stops → all 4 handlers + pump freeze (W8/W12) |

Question row: (a) terminator in family? T1/T2 end the drain by
starvation/loop-exit; T4/T10 fire latent calls; all fixed 71,762×.
(b) a counter? monotonic 4 (write-only/never-fire, ≥2.2-yr
horizons); periodic 3 (mod-30/T1/8-loop, reset by construction).
(c) external signal never comes? VBLANK continues; pad-state change,
IOP reply, main action, *(guard) writers never come (Section 3).

## P33-3. Park-break census (Task 3 — what never comes?)

### a. Waiter table (every parked waiter at cap + residue + section-lag note)

Threads (full-log miner: all 477 blocks; post = b242–475 complete,
b476 partial). NOTE (new): block-N sections cover window N−1 —
stubs-N counts == w31(N−1) exactly (T15: b241←b240 305,
b240←b239 592=2×296, b476←b475 299; T13: b241←b240 303),
syscalls-475 (298) == w31(b474), threads-475 t4 (298) == w31(b474);
status fields are live-at-tick, scheduled/histograms trail one
window. P32-8's 303-vs-297 skew dissolves (was same-window
misattribution); T13-b240's 325260×9440 top = in-phase tail of its
74%-in-phase window-239.

| Thread | Entry | Cap state (b476 @2856696–701) | Scheduled (post b242–475) | Note |
|---|---|---|---|---|
| t1 main | 0x100008 | status 5 pc 0x0 (×237, b240–476) | 0 every block (11 @b240 = window-239 wind-down) | RETURNED :2494024 (ra 1d8efc/sp 1fffdc0/v0 467960/a0 0/sched 11) |
| t2 | 0x3e3be0 | WAIT-26 (2/26 @0x423de8) | 0 all post | parked since boot; never scheduled |
| t3 | 0x31ac60 | WAIT-30 (2/30 @0x423de8, ×476) | 0 all post | parked 4w/3s; release needs main's leaf (§P33-3b) |
| t4 | 0x31ac08 | WAIT-31 (2/31 @0x423de8, sched 299) | 296–305 EVERY block (sole nonzero; 0 exceptions) | LIVE pump (P1ai re-verified on T15) |
| t5 | 0x382740 | WAIT-32 (2/32 @0x423de8) | 0 all post (11 @b240, winds down with t1) | t5≡t1 coupling: b234–242 t5=t1 except b237/238 (600/599, 609/610 — off-by-one; T13 exact) |
| t6 | 0x3c19a8 | WAIT-36 (2/36 @0x423de8, ×477) | 0 all post | parked (entry = fn after id-6 handler) |
| idle | 0x0 | id=-1 dormant ~2/VBLANK (d/31w 2.014–2.021) | — | pc==0 site, empty invocations (EeScheduler.cpp:641–680) |

t1/t5 scheduled b234–242: t1 = 604/607/590/599/610/604/11/0/0;
t5 = 604/607/590/600/609/604/11/0/0. Residue (same 13 tgts + ras as
T13; all firstRa==lastRa): b241 = 610×3+305×10; b476 =
598×3+299×10. Syscalls @cap (b475): 0x44 WaitSema×298 +
0xffffffbd iSignalSema×298 ONLY. status=5 ×237, all id=1
(@2495442–@2856696, b240–b476 samples; 0 for ids 2–6 — W8's second
half silent).

### b. Missing-signal table (sema-30's 4th, IOP announcer, 0x3C45C0)

| # | Missing signal | Parked state (T15) | Who SHOULD send (code path tamped) | Where it would appear | Sightings |
|---|---|---|---|---|---|
| S1 | sema-30 4th signal | 7 lines 4w/3s, last @7225 (wait); waits waker=3 ra=0x31aca4; signals waker=1 ra=0x31acf4 (@643/706/7023) | MAIN's signal leaf `31AAF0@0x31ace0`: `*(v1+0x4048)=a1; JAL SignalSema(423DC0)@0x31acec` (branch-free; a0=`*(v1+0x4044)`) — main dormant, never re-enters. t3's wait site `JAL WaitSema@0x31ac9c` + `beqz *(s1+0x20)` respin (t3 spins 4 waits, parks) | 8th `id=30` line (`signal waiters 1→0 target=3`) + t3 RUN sample | 0 (W9 silent to cap) |
| S2 | IOP announcer (SIF reply) | `_request_end` (0x40B2D0) never dispatched; sregs[1] stays 0 (t3's `while(sregs[1]==0)` never passes — §P26-5f) | IOP peer of the EE `SET_SREG(1,1)`+poll handshake (identity open since §P26-5); host path would be dmac-cause completion → handler 0x382650 | `sub_0040B2D0` trace enters; dmac-1 handler hits (extra 3825F8 enters); SIF/RPC log lines | 0 (40B2D0 ×0 FULL boot; dmac-1 ×0 post; SIF region ≥2461202: 0) |
| S3 | 0x3C45C0 (SendCmd cid=0 site) | site = `JAL sceSifSendCmd(0x4261B0)@0x3c45c0` in sub_003C4450 (a0=0,a1=t1,a2=0x30 — args decoded here); armed by beqz s2==0 @0x3c4580 (s2 = caller state, ZERO writes in-func) | callers JAL @0x3C4640 (in 3C45E8) / @0x3C48EC (in 3C4898) with s2==0 | `sub_003C4450` trace enters; 2nd `[sceSifSendCmd]` log line (only 1 all boot: cid 0x80000001 @:1053) | 0 (3C4450/3C45E8/3C4898/4261B0 ×0 FULL boot — HLE stub untraced by design; armless, not just unfired) |

Silence re-audit (exit region ≥2461202): lbn= 0, SIF-load/SendCmd 0,
GS-kick 0, RPC-unhandled 0, drops 0. Lasts: 7175/1056/2639/5144/73
(CD/SIF/GS/RPC/drop). T15 watch-3 reproduced + SIF added.

### c. Halt-split table (block-239 5/296 vs 117/298 — bound tighter)

Block spans (stub-header ticks): T15 b239 = 2493878–2495478 (1,601
lines); T13 b239 = 2487366–2490771 (3,406 lines). T15 b239 holds 11
id-29 lines (5w+6s); T13 b239 holds 235 (117w+118s).

| Order | T13 (boot-t13-1.log) | T15 (boot-t15-1.log) |
|---|---|---|
| b239 29-events | 235 lines, 2487366–span | 11 lines: s@2493916, w@2493928, s@2493936, w@2493948, s@2493956, w@2493968, s@2493976, w@2493988, s@2493996, w@2494008, s@2494022 (strict alternation from a carried wait) |
| LAST 29 wait | 2489876 (`waker=1 ra=0x31aa8c park`) | 2494008 (same shape) |
| LAST 29 signal | 2489890 (line 2525/3406 = 74.1%) | 2494022 (line 145/1601 = 9.1%) |
| +1 | 2489891 31-wait (ADJACENT) | 2494023 31-wait (ADJACENT) |
| +2 | 2489892 dormant id=1 (ADJACENT) | 2494024 dormant id=1 (ADJACENT) |
| 29-signal→… shape | wait `waker=1 ra=0x31aa8c` / signal `waker=4 ra=0x31aae4 target=1` | IDENTICAL pcs/roles (all 11 lines) |
| b240 sched t1/t5 | 213/213 (window-239: halt late → 213 mains) | 11/11 (window-239: halt early → 11 mains) |

Tighter bound (both runs): the halt is NOT block-aligned — last-29
falls 9.1%–74.1% through window 239 (run-dependent wall alignment);
the signal→wait→dormant ADJACENT trio reproduces exactly (offsets
+0/+1/+2); post-trio, 29 = 0/0 forever (T15: 237 blocks) while 31
continues gapless (alternating wait/signal to EOF wait @2857096).
Mechanism (static): 29 doesn't die — `31A6B8@0x31aad4` takes the
skip arm every VBLANK once `*(a0+0x1C)` reads 0 (T3 row).

## P33-4. Next-experiment spec (Task 4 — the follower reads this)

Follower = the boot brief after this diagnosis. All rows executable
as written. Baseline cadence: 1 drain iter/VBLANK @60Hz (300–307
iters/block); 3E4AF0 gaps ∈ {6,7}; d/31w 2.014–2.021; residue 13
fixed; sema-31 count≡0.

### a. Experiment table (3 candidates + exact rows)

| # | Experiment | Trigger rows (monitor, 15 s polls) | Success rows (park breaks) | Miner rows (analysis must emit) |
|---|---|---|---|---|
| E1 | LONGER BOOT (bound 7,200 s; T15 scripts + rows below) | keep T15's 7 + add W4 (2nd dormant id=1), W10 (firstRa≠lastRa), W11 (d/inv + gif/dma bands); stall-trip 120 s kept | ANY of W1–W12 fires (esp. W8 w31=0, W3 main status≠5, W7 unfreeze, W9 8th id=30, new caller) | M1–M10 verbatim (P32-6b) + drain iters Δ(31−29) + 3E4AF0 gap histogram (any gap ∉{6,7} = break) + last-29-split trio lines + bLast residue full rows + per-1000 chunk table (§P33-2a schema) |
| E2 | STIMULUS (needs fork work first — pick one): (a) pad-state injection via HLE Pad.cpp (flip buttons/analog mid-drain); (b) host SIF0-reply injection (drive dmac-1 → 0x382650); (c) debug `SignalSema(30)` poke (no main needed) | E1 triggers + stimulus-armed watch: new HLE target in stubs (E2a); 3825F8 enters > iters (E2b); t3 RUN sample (E2c) | (a) 326EB0 dormant HLE arm fires (residue ≠13 / W2+W10); (b) 0x382650 handler executes (ei-entry side effects); (c) t3 wakes + respin flag read (4th wait resolves or 5th parks) | E1 miners + pre/post-stimulus residue diff + pad/HLE call census + t3 state series + guard-word values if probed (E3 rows) |
| E3 | PROBE (read-only diag; fork + rebuild; boot 1,800–2,400 s to exit + drain sample) | E1 triggers (no new behavior) | probe lands numbers (no park-break required): guard words + counters per §P33-2b/c | per-VBLANK (or per-100): `*(v1+0x4038)`+`*(v1+0x4034)` (T1), `*(s0+0x20)` (T2), `*(a0+0x1C)`+`*(a0+0x18)` (T3), `*(a1+0x5A8C/5ABC/5AB8)` (T4), `*(gp±off)` pointers, N/i (326B88), s0 (317348), `*(0x50AAA8)`, T1 COMP/COUNT, `*(0x450DA8/DCC/DD0)`, a1 args (id-2/id-3), branch-hit counts for T1–T10 guards, handler-entry hits (VBLANK:iter 1:1 proof), pad HLE return values |

E1 discriminates "terminator with count > 71,762" (fires) from
"no unmodeled terminator to ~6× bound" (silent). E2a directly
attacks the largest live-branch surface (326EB0, T8). E2b/E2c test
whether the parked waiters (dmac-1/t3) are revivable. E3 closes
every P1aj gap row (T4 state, T8 directions, input values).

### b. Bound table (longer-boot math — what falsifies "infinite")

N (72,176) is FIXED at exit (0 post 362DE8 enters over 71,762
VBLANKs) — a longer boot can only extend the DRAIN count, not N2.
"Iters" = Δ(31−29) = VBLANKs survived post-exit.

| Item | Value |
|---|---|
| T15 bound (current) | 71,762 iters / 237 blocks / 2,400 s cap (no event) |
| Measured cadence | 300–307 iters/block (≈60/s; 1/VBLANK) |
| E1 cap → expected iters | 7,200 s → ~430,000 (≈6.0× T15) |
| Falsify "infinite" (ANY) | W8 (any w31=0 post block); W3/W4 (main moves); W7 (tick delta ≠0); W9 (8th id=30); new 362DE8 enter/caller; 3E4AF0 gap ∉{6,7}; residue ≠13; firstRa≠lastRa |
| Counter horizons (NOT falsifiable by E1) | `*(0x50AAA8)`/`s1+0x18`/3825F8-ctr 32-bit @60Hz ≈ 2.26 yr; mod-30/T1/8-loop periodic by construction; 3825F8 fire needs state==4 (never observed — E3 reads it) |
| E1-silent reading | no unmodeled terminator below ~430k VBLANKs; park stands to 6× bound (table, don't verdict) |

### c. Lease table (which experiments need the P-lane lease)

| Exp | Lease? | Boots/caps | Script derivation (T15's + rows to change) |
|---|---|---|---|
| E1 | YES (P-lane) | 1 boot, SECS=7200 | `/tmp/t15-boot1.py` → LOG name + `SECS=7200`; `/tmp/t15-monitor.py` + W4/W10/W11 predicates (P32-6a text) + M-row grep patterns; miners `/tmp/t15-{trace,mine,blocks,rates,cycle,tail}.py` verbatim + `/tmp/p1aj/trace_drain{,2,3}.py` (chunk schema) |
| E2 | YES + fork diff | 1–3 boots (stimulus timing runs), 1,800–2,400 s caps | E1 scripts + stimulus hook (Pad.cpp/SIF/dbg-sema — fork change, rebuild, sha-record like T13 §T13-0) + armed-watch predicates (§P33-4a) |
| E3 | YES + fork diff | 1 boot, 1,800–2,400 s | E1 scripts + read-only probe (guard/counter reads §P33-4a; rebuild; prove zero behavior delta: N + chunk-0 + residue identical to T15) |

All: claim/release via `/tmp/ssx3-p-lane-lease` + waits log;
`git add -f` evidence; prefix + `Orchestrated-By: Muse Code` trailer;
NEVER `git push` in ssx3 (brief rule).

## P33-5. Exact commands + receipt paths

From `/Users/bradrichardson/dev/ssx3` unless noted. All receipt
accesses read-only (grep/sed/python reads, `tail -c` seeks); no
lease, no boots, no builds, no fork writes:

```text
# Reads (lease-free; T15 + P32 + T13-1 + statics)
read local/research/T15/REPORT.md (all); P1 REPORT Part 32 (P32-6 spec);
  local/research/T13/REPORT.md §T13-1; header decls
  $W/P1/output/ps2_recompiled_functions.h (:2628/5900/5905/5906/5989-5991/6138/6146/6865-6866/7669/8180)
# Miners (written to /tmp/p1aj/, uncommitted)
mkdir -p /tmp/p1aj
write /tmp/p1aj/trace_drain.py (single streaming pass: boundary verify,
  post census, 31A3C0 markers, per-1000 chunks, edge iters)
python3 -m py_compile; python3 /tmp/p1aj/trace_drain.py T
  -> drain_summary.txt, drain_chunks.tsv (72), drain_edge_iters.txt
  (done 187727172 71762)
write+run /tmp/p1aj/trace_drain2.py (tail -c 120MB residual/3E4AF0 gaps)
write+run /tmp/p1aj/trace_drain3.py (chunk-0 decay buckets + final iter)
# Boot-log receipts (read-only greps/awk/python)
sema formats + dormant id=1 (:2494024) + last-29 @2494022/2494008 + tail;
  b239-span 29 events (11, T15) vs 235 (T13); sema-30 7 lines;
  id=31 invariance (287878 + 1 fused) + totals 72178/72178 143940/143939;
  per-block threads miner (t4 sole sched b242-475; t1/t5 series);
  b241/b476/b240/b0/b1 stub rows (residue + lag); syscalls b475 (2 ids);
  exit-region silence (0/0/0/0/0 incl SIF); SendCmd (1, cid 0x80000001);
  intc/dmac stacks census (6 handlers ×477); threads b476 tail
# Trace counts (streaming grep -c; never copied)
003C4450/003C45E8/003C4898/004261B0/0040B2D0 enters = 0/0/0/0/0 (full boot)
# Static reads (read-only bodies + fork sites)
full: 317520/317500/227F58/317348/326B88/3825F8/31A3C0;
  spans: 31AAF0 legs+sema30 paths, 31A6B8@0x31aac8, 37E120@0x3825c0,
  3C1638@0x3c1980, 3E4AF0@0x3e4db8+tail, 326EB0 entry/mid/tail,
  423DB0/423DC0/423DD0/423DE0/423DF0/423CB0/423CC0/423CD0 shims,
  3C4450@0x3c45c0 + callers; fork: Dispatcher.cpp:200-359 (syscall names),
  EeScheduler.cpp:641-680/742/1919-1972/2446/2605/2611 (dormant/dispatch/
  dispatchIrq/VBLANK/TIMER1), ps2_runtime.cpp:157-190/1100-1134/1315-1348/
  1740-1811 (history/histogram/lookup/hook), ps2_log.h:241-266 (ENTRY/exit),
  Interrupt.cpp, RPC.cpp:131, Loader.h:70, Pad.cpp:8,48
# Report (this Part)
(edit_file append Part 33 in 2 chunks)
git add -f local/research/P1/REPORT.md
git commit -m "[P1aj] ..." (trailer Orchestrated-By: Muse Code; NO push)
```

Receipt paths: `/tmp/p1aj/trace_drain.py|_summary.txt|_chunks.tsv|
_edge_iters.txt`, `/tmp/p1aj/trace_drain2.py`, `/tmp/p1aj/
trace_drain3.py` (all uncommitted scratch; tables above are the
evidence).

## P33-6. What I could not do (gap rows)

- Simulate each of 326EB0's ~25 live-span branches individually
  (taken/not-taken per branch): directions are jointly fixed by the
  exact 2×/iter pad-pair, but per-branch proof needs symbolic
  execution or an E3 hit-count probe (same for 3E4AF0's pre-0x3e4db8
  body — off the handler path, unexamined).
- Read 3825F8's `*(a1+0x5A8C)` state (T4's first arm): fire ×0 is
  consistent with both state≠4 and counter<limit (E3 reads it).
- Read any guard-word VALUES (`*(v1+0x4038)`, `*(s0+0x20)`,
  `*(a0+0x1C)`, N/i, pad returns): fixed-by-count, values unprobed
  (E3 rows specified).
- Name the id-2/id-3 handler `argument` (a1) constants beyond the
  observed 0x31abd0 (id-2): registration values live in the host
  handler table, not in the receipts (E3 reads them).
- Join trace chunks to log blocks (no timestamps in either stream):
  chunk↔block correspondence is rate-inferred (≈60/s both), not
  observed (same gap as T13 §T13-7/T15 §T15-7).
- Attribute the T13-vs-T15 halt-position spread (74.1% vs 9.1%
  through window 239) or the wall-rate shape differences from inside
  the receipts (no host-load log in scope; tabled as guest-fixed
  wall variation, sixth datum: T15 flat ~60 + proxy ~30.2).
- Session wall time ≈ 4 h box (this turn), inside the box; zero
  lease touches (no contention possible).

## Part 34 (P1ak): E1 long-window diagnosis — fixed point holds over 359,749 iters (no boot)

Brief `local/muse/prompts/P1ak.md`. DIAGNOSIS brief on committed
logs — no boot, no lease of any kind, no fork changes, no `adb`.
Tables, no verdicts. Stale-reading guard: `local/research/T16/REPORT.md`
(all of it — E1's 7200 s run: NO drain break, 359,748 iters,
N = 72,176 exact, 887 frozen pairs, 4 disclosed deviations) + P1
REPORT Part 33 (P1aj's drain-termination analysis: fixed point from
iter 2, 13-row terminator table, E2/E3 spec — the baseline) +
`local/research/T16/blocks.tsv` + `ticks.tsv` (per-block/per-tick
rows, read as input, re-verified below by independent miners).
`W=/Volumes/Extreme SSD/ps2recomp-spike`,
`LOG=$W/P1/run/boot-t16-1.log` (4,315,920 lines),
`T=$W/P1/run/ps2_log-t16-1.txt` (197,603,104 lines, 6,978,090,314 B).
Scratch `/tmp/p1ak/` (miners kept there, uncommitted); this Part is
the only evidence. Both logs read-only: streaming passes + seeks;
never copied whole.

Headline receipts: the §P33-2a fixed point holds over all 359,749
drain iters (chunk-0 = 340-line finite tail ALL in iter 1, buckets
101–1000 = 0; chunks 1–358 identical 15-func/34.292–34.294-line
shape, 9-fam 1.0000/iter, 0 residual; iter 359,749 = 28-line SIGTERM
cut, all balanced). 3E4AF0 gaps = 6:9140 + 7:43557 (n=52,697, none
outside {6,7}); per-1000 cadence 146×184 + 147×174 over chunks
1–358. All 13 terminator rows re-polled over blocks 242–1429 hold
their P33 direction; per-block extremes over the 5× sample: w31
294–308, s31−w31 ≤ +1, d/w31 1.9966–2.0502. The 5 deviations
reproduce digit-exact; the exit-tail singleton-58 and the chunk-71
span +2 coincide positionally (rep 71526 ∈ inv-chunk 71) with exact
+1-frame = +2-line arithmetic. Monotonic counters advance +359,749
increments (≈0.0084% of 2^32 each; horizons evidence-invariant).
E2a/E2b/E2c + E3 rows below are brief-shaped (guard PCs re-verified
in `$W/P1/output` read-only this turn).

## P34-0. Rule record (no lease, no boots, no fork changes)

| Item | Value |
|---|---|
| P-lane lease | Never touched (no boots; lease file never created/checked) |
| Boots / harness runs | 0 (read-only mining of T16's committed logs) |
| Fork changes | 0 (fork + `$W/P1/output` sources read read-only; no edits/commits/push/pull) |
| `adb` | Not used |
| Other agents' dirs | Read-only (`local/research/T13|T15|T16`, `/tmp/t16-*.py` patterns only) |
| 7.0 GB trace | 2 full streaming passes (1 new combined + 1 cycle re-run) + streaming `grep -c`/`-n`; never copied |
| 1.2 GB boot log | 3 streaming passes (log/tick/sched) + seeks; never copied |
| ssx3 files changed | `local/research/P1/REPORT.md` ONLY (this Part, appended); commit prefix `[P1ak]`; NO push |

## P34-1. Fixed-point reconfirmation (Task 1 — 359,749 iters)

Method: one new streaming pass (`/tmp/p1ak/trace_pass.py`: N/caller/
balance + drain markers/chunks + residual/gaps + per-inv join data +
guard-count rows) + one cycle re-run (`/tmp/p1ak/cycle_repro.py` =
`/tmp/t16-cycle.py` verbatim, output paths only) + boot-log passes
(`/tmp/p1ak/log_pass.py`, `tick_pass.py`, sched census). Provisional
post boundary = T16's last-362DE8-exit 185264992, verified at EOF.

### a. Chunk table (per-1000 §P33-2a schema, iters 1–359,749)

360 chunks (359×1000 + 749). Steady-15 = 9-family + 31AAF0 + 326EB0 +
423DE0 + 423DD0 + 31A6B8 + 3E4AF0. Full table: `/tmp/p1ak/
trace_chunks.tsv` (uncommitted scratch).

| Chunk | Iters | Trace lines | Lines/iter | 9-fam/iter | 31AAF0/326EB0/423DE0/423DD0/31A6B8/iter | 3E4AF0 | Distinct |
|---|---|---|---|---|---|---|---|
| 0 | 1–1000 | 185265559–185300540 (34,982) | 34.982 | 1.0000 ×9 | 2/2/2.001/1/1.004 | 146 | 55 (15 + 40 resid, ALL in iter 1) |
| 1–358 | steady ×358 | — | 34.292–34.294 | 1.0000 ×9 | 2/2/2/1/1 exact | 146×184 + 147×174 | 15, 0 resid |
| 359 | 359001–359749 | 197577425–197603104 (25,680) | 34.286 | 1.0000 ×6, 0.9987 ×3 (37E120/3C1638/3825F8 = 748) | 2/2/2/1/1 exact | 110 (/749) | 15, 0 resid |

- Residuum: pre-marker unwind = 566 lines / 282 enters (top:
  411C38×32, 411B08×16, 362660/3626D8×12, 38F738/371DD8×11,
  423DE0×10 — T16's top-12 exact). Chunk-0 residual = 340 enters /
  40 distinct, ALL in iter 1 (per-100 buckets: 340,0,0,0,0,0,0,0,0,0;
  last resid = iter 1 @185266275 `001D8DE0`; resid iters = {1}).
- Strays vs exact multiples (T13/T15 structure reproduced): 423DE0
  +11 (10 pre-marker + 1 chunk-0), 423DD0 +2 (both pre-marker),
  31A6B8 +8 (4 pre-marker + 4 chunk-0).
- Post census: 12,338,112 lines over 113 functions (preset 1072),
  0 post-only; 394ED0/395000 = 0/0 post; 362CC8 = 1/1 (the N+1);
  376938 = 5/6, 363490 = 2/3 (one pre-bound-enter each, exits post).
- Depth-0 roots post: 1,851,473 total / 20 distinct — T16's 20 rows
  exact (423DE0 359752=+3; 37E120/3C1638/31A3C0/31AAF0 359749;
  3E4AF0 52699; 376938 4; 382760 4; 423DC0 3;
  38F300/363490/382650/316F00 2;
  395288/232AE0/31A6B8/2C5570/23D660/23D618/1D8DE0 1). Post depth
  min/max = 0/13.
- First vs last iteration: iter 1 = 724 lines (steady-15 + 340-line
  finite tail); iter 2 = 34 lines; iters 2–359,748 = pure fixed
  point (iter 359748 = 34 lines); iter 359,749 = 28 lines
  (31A3C0-leg + 423DE0 + 31AAF0-direct leg complete;
  37E120/3825F8/3C1638 pairs missing — SIGTERM between root
  dispatches; every enter balanced).
- N rows: 362DE8 = 72,176/72,176 (first @19,385, last enter
  @185,264,853, last exit @185,264,992, bound_ok=True, 0 post);
  caller single `00363490` ×72,176; 394ED0 = 1,442,182 (= 20N−1338);
  395000 = 1,370,006 (= 19N−1338); 363490 = 216,528/216,528 (= 3N).
- Per-inv join (bisect over full enter-line arrays): non-20/19 =
  exactly ordinals 0–74 (n=75): ords 0–51 @2/1, ords 52–63 @3/2,
  ords 64–74 @2/1; ordinals 75–72,175 (72,101 invs) ALL exactly
  20/19.
- Stack: mismatches 0, max depth 29, live frames at EOF = 0 (empty
  stack — SIGTERM landed between root dispatches, as T13/T15/T16).

### b. Cadence table (3E4AF0 gaps + per-1000 alternation, full window)

| Row | Value |
|---|---|
| Gap histogram (inter-arrival iters) | 6:9140 + 7:43557 (n=52,697; min 6, max 7; outside {6,7} = NONE) |
| Per-1000 over chunks 1–358 | 146 ×184 chunks + 147 ×174 chunks (no other value) |
| Chunk 0 / chunk 359 | 146 / 110 (= 0.1468/iter over 749) |
| Post total | 52,699 enters = 52,698 in-iter + 1 pre-marker |
| Cadence drift, chunks 72–359 | none (146/147 alternation continues; chunk-359 rate in-band) |

### c. Guard table (T1–T13 re-polled over blocks 242–1429 / iters 1–359,749)

"Direction" = P33 fixed direction; "T16 re-poll" = this turn's
receipt; "nearer trip?" compares T15-scale extremes to T16-scale.

| # | Guard (P33-2c) | P33 direction | T16 re-poll (this turn) | Nearer trip vs T15? |
|---|---|---|---|---|
| T1 | 31AAF0@0x31abe8 skip-signal | NOT taken (signal always fires) | 423DD0 post = 359,751 = iters+2 (both pre-marker); s31 post-239 = 359,728; 0 skip events over 359,749 iters | no (0 skips both scales) |
| T2 | 31AAF0@0x31ac34 loop-exit | TAKEN (flag 0; loop repeats) | Wakeup/Sleep log lines 0; 423CD0 ×0 boot; 423CC0 ×2 early-boot only (@21198/@29109); t4 sched 294–308 EVERY post block, 0 exceptions | no (t4 never 0; trip = w31 0) |
| T3 | 31A6B8@0x31aad4 29-skip | TAKEN post-halt (gate 0) | 29w = 0 every block 239–1429; last-29 @2,494,970 (`waker=4 ra=0x31aae4`); last-29-wait @2,494,956 (`waker=1 ra=0x31aa8c`) | no (0 both scales) |
| T4 | 3825F8 fire (state==4 AND ctr≥limit) | fire ×0 | 423DD0 == iters+2 (no extra fire); state/ctr still unread (E3) | no (×0 both scales) |
| T5 | 227F58 null-skip | NOT taken (nonzero) | 326B88 == 359,749 = iters (leg never skipped) | no |
| T6 | 317348 s0==0 (1 round) | NOT taken; 1 round | 227F58 == 359,749 = iters | no |
| T7 | 326B88 N==2 (2 rounds) | NOT taken; 2 rounds | 326EB0 == 719,498 = 2×iters exact | no |
| T8 | 326EB0 live-span branches | fixed (pad-pair 2×/iter) | pad-pair 2×/iter exact; residue 13 same; 3FF708 ×0 boot; per-branch taken/nt still unprobed (gap carried) | no (jointly fixed both scales) |
| T9 | 37E120 `beq a0,2` | TAKEN (a0 = host cause) | intc table identical all 1430 blocks; crash/FATAL/BREAK 0 | no |
| T10 | 3E4AF0 vector `*(0x450DA8)` | TAKEN (vector 0; 8 fixed) | gaps {6,7} only; post-only 0; no new caller | no |
| T11 | 31A3C0 (no branch; a1 host) | — | markers = 359,749; a1 const (handler table, all blocks) | no |
| T12 | 3C1638 (no branch; ++ctr) | — | ++ctr unread; +359,749 increments this window | horizon-invariant (below) |
| T13 | host VBLANK @60Hz | 71,762 consecutive | 359,749 consecutive (≈60.1/s over ~5,990 s post window) | no |

Monotonic/periodic inputs (advanced how far this window):

| Counter | Advance (this window) | Horizon |
|---|---|---|
| `*(0x50AAA8)` (T12) | +359,749 | 2^32 @60Hz ≈ 2.26 yr (≈0.0084% consumed this window) |
| s1+0x18 (317348) | +359,749 | same class (≈2.26 yr) |
| 3825F8 a1+0x5ABC ctr | +359,749 | same class (fire needs state==4, unread) |
| 0x450DCC/DD0 (3E4AF0) | +52,699 (per-fire) | same class |
| 326B88 mod-30 index | 359,749 ÷ 30 cycles (periodic by construction) | none (resets) |
| T1 COUNT/COMP re-arm | 52,699 re-arms (periodic by construction) | none (resets) |

Per-block extremes (5× sample vs T15-scale):

| Band | T15 scale (234 blocks) | T16 scale (1187 blocks, this turn) |
|---|---|---|
| w31/post block | 295–307 | 294–308 (min @325/329/712/745/1329; b1429 partial 47) |
| s31−w31/post block | max +1 (@b251) | max +1 (@251 first; also 295/313/340/497/557), min −1 |
| dormant/w31/post block | 2.014–2.021 (per-slice) | 1.9966–2.0502 (@314/@581; monitor POST d31 1.997–2.050) |

Sema-31 shape census (fixed-point input table): waits 431,926 =
431,923 identical (`waker=4 pc=0x423de8 ra=0x31ac30 waiters 0→1`)
+ 3 tick-fused truncations (1 missed by strict match @3330853
`id=31[run:tick]`, reconciled); signals 431,925 = 431,897 waker=-1
identical + 25 waker=3 (ALL ≤ line 6782, pre-steady: 13 pre-block-0
+ 12 block-0 window) + 7 tick-fused truncations; count ≡ 0→0 on all
non-fused lines (0 exceptions).

## P34-2. Deviations + bounds + E2/E3 (Task 2)

### a. Deviation table (5 reproduced + recurrence + drain-touch)

| # | Deviation | T16 reproduced (this turn) | T13 | T15 | Recurs? | Drain-touch? |
|---|---|---|---|---|---|---|
| D1 | Collapse tail one block shorter | 211×2 (b236–237) + 189×2 (b238–239), residue-13 from b240 (×1190) | 211×3 + 189×2, residue @b241 | 211×2 + 189×3, residue @b241 | new shape (3rd variant; endpoints 218/residue same) | NO — transitional blocks only; chunk-0 resid 340 = T15's 340; unwind 566/282 identical |
| D2 | Stub preamble b0/b1 | 961/497, steady @b2 | 897/588 | 887/603 | YES — T11-exact repeat (4th pair, 2nd distinct value) | NO — blocks 0–1, ~235 blocks pre-exit |
| D3 | Probe NULL-head | 3135 (−1 vs 3136) | 3136 | 3136 | new value (= P1ag's 3135; T11/T13/T15 held 3136) | NO — probe ends @62119 « exit @2463373; N/ramp/chunk-0 bit-exact |
| D4 | Exit-tail 3rd singleton | len 58 @rep 71526 (58/56/58) | 57 (58/56/57) | 57 (58/56/57) | new value (first_rep + reps identical; len +1) | NO — rep frames contain 362DE8 by construction (all pre-exit); see D4+D5 arithmetic |
| D5 | Inv-chunk-71 span +2 | 2302066 (enters same 20000/19000/1000) | 2302064 | 2302064 | new value (+2 lines) | NO — in-phase span; drain chunks unaffected (c1–358 exact) |

D4+D5 positional + arithmetic table (one mechanism, two rows):

| Row | Value |
|---|---|
| Rep↔inv correspondence | rep frames = 72,176 = N; reps defined as ≥1 362DE8 ⟹ exactly 1 inv/rep (pigeonhole) |
| Singleton position | rep 71526 (0-based) ↔ inv ordinal 71526 ∈ inv-chunk 71 (71001–72000) |
| Gap-71526 frames | strictly between rep 71526 ⊃ de8[71526] and rep 71527 ⊃ de8[71527] ⟹ inside ic71's tiled span |
| D4 delta vs T13/T15 | +1 depth-0 frame (len 58 vs 57) |
| D5 delta vs T13/T15 | +2 trace lines (2302066 vs 2302064) = +1 frame × (enter+exit) |
| Other ic71 deltas | none (enters 20000/19000/1000 identical; ic70 span 2520494 identical) |

Halt-position envelope (boundary-shift family, third datum):

| Run | Last-29 | Position | Window |
|---|---|---|---|
| T13 | @2,489,890 | 74.1% | window 239 (117/298) |
| T15 | @2,494,022 | 9.1% | window 239 (5/296) |
| T16 (this turn) | @2,494,970 | 97.85% | window 238 (279/299; span 2,489,103–2,495,099) |

Halt-split trio reproduced: 2,494,970 / 2,494,971 / 2,494,972
(+0/+1/+2 ADJACENT); dormant sched=559 = b239 t1 scheduled
(b234–242 t1/t5: 603/604, 596/595, 601/601, 607/607, 598/598,
559/559, 0/0, 0/0, 0/0).

### b. Bound table (terminator-horizon recompute at 359,749-iter evidence)

| Bound | P33-4b (T15 evidence) | P34 (T16 evidence) | Tightens? |
|---|---|---|---|
| No-event drain iters | 71,762 / 237 blocks / 2,400 s | 359,748 / 1188 blocks / 7,200 s (5.01×; P33 projected ~430k ≈6.0× — in-phase ~1,190 s non-contributing) | YES (count) |
| w31 floor (trip needs 0) | 295 min over 234 samples | 294 min over 1187 samples | YES (sample; floor −1 observed) |
| w31 ceiling | 307 | 308 | YES (sample; +1 observed) |
| s31−w31 (trip needs >+2) | max +1 | max +1 (6 blocks: 251/295/313/340/497/557) | YES (sample; max same) |
| d/w31 band | 2.014–2.021 per-slice | 1.9966–2.0502 per-block | YES (sample; band wider, inside [1.9,2.2]) |
| Frozen pairs | 160 @2669132/72181 | 887 @same counters | YES (5.5× hold) |
| Halt-position envelope | 9.1%–74.1% (w239) | + 97.85% (w238) — first sub-240 halt | YES (3rd datum; envelope widens) |
| 32-bit counter horizons | ≈2.26 yr @60Hz | ≈2.26 yr (consumed +359,749 ≈ 0.0084% this window) | NO (evidence-invariant claim) |
| Periodic cycles (mod-30/T1/8-loop) | reset by construction | reset by construction (11,991+ full mod-30 cycles) | NO (invariant) |
| T4 state==4 | unread (fire ×0) | unread (fire ×0 over 359,749) | NO (needs E3 read) |
| 326EB0 per-branch dirs | jointly fixed, unprobed | jointly fixed over 719,498 pairs, unprobed | NO (needs E3/symbolic) |
| +2 29-side edge (72,178 vs 72,176) | unattributed (no timestamps) | unattributed (same +2; +1 in-phase window +1 markers-vs-Δ) | NO (invariant) |
| Chunk↔block join | rate-inferred ≈60/s | rate-inferred ≈60.1/s (no timestamps either stream) | NO (invariant) |
| Residue-13 addresses | same 13 (b241/b476) | same 13 (b240/b241/b1429, all firstRa==lastRa) | YES (sample; 1190 blocks) |
| Post-241 syscall ids | {0x44, 0xffffffbd} | same 2 ids, all 1189 sections b241–1429 | YES (sample) |

### c. E2/E3 table (brief-shape promotion rows)

All guard PCs below re-verified present in `$W/P1/output`
read-only this turn (31AAF0: `case 0x31abe8/0x31ac34` + `bnez
$v0` body; 3825F8: `lw $a0,0x5A8C($a1)` + `bne` @0x382614;
31A6B8: `beqz $v0` @0x31aad4; 3E4AF0: `beql` @0x3e4e4c; 326EB0:
live `dispatchGuestBranch(0x3FFBC0@0x326F1C, 0x3FFA58@0x3271E0)`,
dormant `0x3FF708@0x326EE4` + `0x3FFBC0@0x327080`). Pad stimulus
surface: `ps2xRuntime/src/lib/Kernel/Stubs/Pad.cpp` (buttons
active-low, default 0xFFFF; analog center 0x80; digital mode 0x41).

| # | Experiment (brief-shape) | Trigger rows (15 s polls; T16-calibrated) | Success rows | Miner rows | Inputs needed? | Lease? | Boots? |
|---|---|---|---|---|---|---|---|
| E2a | STIMULUS pad-state (flip buttons/analog in `Pad.cpp` mid-drain, post-exit) | E1 triggers (P34-1c bands: w31 294–308, d/w31 [1.9,2.2], gaps {6,7}) + armed: residue ≠13 OR new HLE target in stubs OR 326EB0/iter ≠2 | dormant 326EB0 arm fires (0x3FF708@0x326EE4 or 0x3FFBC0@0x327080 executes; residue ≠13 / W2+W10) | E1 miners (P33-4a M1–M10 + P34-1a/b/c) + pre/post-stimulus residue diff + pad/HLE call census + T8 branch split if fired | fork diff (stimulus hook + arming tick) + rebuild + sha-record (T13 §T13-0 style) | YES (P-lane) | 1–2 (1,800–2,400 s; 2nd only if timing missed) |
| E2b | STIMULUS SIF0-reply (drive dmac-1 → 0x382650 mid-drain) | E1 triggers + armed: 3825F8 enters > iters (baseline == iters exact + 2 unwind) OR 382650 in-iter enters >0 (baseline 0; unwind 2 @pre-marker) | 0x382650 handler executes in-iter (ei-entry side effects; extra 3825F8/drain shape change) | E1 miners + 382650/3825F8 enter census (pre/in/post-stimulus) + drain-chunk diff | fork diff (host SIF0-reply injection) + rebuild + sha-record | YES (P-lane) | 1–2 (same caps) |
| E2c | STIMULUS debug SignalSema(30) (no main needed) | E1 triggers + armed: 8th `id=30` line OR t3 RUN sample (baselines: 7 lines @643–7226; t3 WAIT-30 ×1429 + RUN b0) | t3 wakes (4th wait resolves or 5th parks; `beqz *(s1+0x20)` respin read) | E1 miners + t3 state series + sema-30 line shapes + `*(s1+0x20)` if probed | fork diff (debug sema poke, post-exit timed) + rebuild + sha-record | YES (P-lane) | 1 (1,800–2,400 s) |
| E3 | PROBE read-only diag (guard words + counters; no behavior change) | E1 triggers (no new behavior) | probe lands numbers (no park-break required): all rows below, per-VBLANK or per-100 | per-VBLANK (or per-100): `*(v1+0x4038)`+`*(v1+0x4034)` (T1@0x31abe8), `*(s0+0x20)` (T2@0x31ac34), `*(a0+0x1C)`+`*(a0+0x18)` (T3@0x31aad4), `*(a1+0x5A8C/5ABC/5AB8)` (T4@0x382614/0x382624), `*(gp±off)` ptrs, N/i (326B88), s0 (317348), `*(0x50AAA8)`, T1 COMP/COUNT, `*(0x450DA8/DCC/DD0)`, a1 args (id-2/id-3), branch-hit counts T1–T10, handler-entry hits (VBLANK:iter 1:1 proof), pad HLE return values | fork diff (read-only probe) + rebuild + zero-delta proof (N + chunk-0 + residue identical to T16) + sha-record | YES (P-lane) | 1 (1,800–2,400 s to exit + drain sample) |

Why-not rows: none — every §P33-4a stimulus/probe row promotes
(above); no row is blocked on missing inputs (all PCs/regs verified
present; all baselines T16-calibrated). E2a attacks the largest
live-branch surface (T8, still jointly-fixed-only after 719,498
pairs); E2b/E2c test parked-waiter revivability (dmac-1: 2 unwind +
0 in-iter; t3: 0 post-b0 RUN); E3 closes every P34-4 gap row.

## P34-3. Exact commands + receipt paths

From `/Users/bradrichardson/dev/ssx3` unless noted. All receipt
accesses read-only (streaming python/grep/sed, `tail -c` seeks); no
lease, no boots, no builds, no fork writes:

```text
# Reads (lease-free; T16 + P33 + TSVs + T13/T15/T11 cites)
read local/research/T16/REPORT.md (all); P1 REPORT Part 33 (P33-2/3/4 spec);
  local/research/T16/blocks.tsv + ticks.tsv (headers + extremes)
# Miners (written to /tmp/p1ak/, uncommitted)
mkdir -p /tmp/p1ak
write /tmp/p1ak/log_pass.py (single streaming pass: stub series, per-block
  29/31/dormant, t1/t3/t6, halt trio, sema30, syscalls post-241, residue rows,
  probe census, silence audit, sema-31 shapes)
python3 /tmp/p1ak/log_pass.py LOG -> log_summary.txt (done 4315920)
write+run /tmp/p1ak/tick_pass.py (ticks/deltas/freeze/t4) (994 ticks, 887 frozen)
sched census (heredoc python: t1-t6 scheduled post242-1428; t4 sole nonzero)
write /tmp/p1ak/trace_pass.py (ONE streaming pass: N/callers/balance,
  per-1000-inv chunks, per-inv join arrays, markers, per-1000 drain chunks,
  3E4AF0 gaps, chunk-0 buckets, edge iters, post census, guard counts)
python3 /tmp/p1ak/trace_pass.py T 197603104 -> trace_summary.txt,
  trace_chunks.tsv (360), trace_edge.txt (done 197603104 359749)
sed /tmp/t16-cycle.py -> /tmp/p1ak/cycle_repro.py (output paths only;
  diff = 3 TSV/TXT paths); python3 /tmp/p1ak/cycle_repro.py T
  -> cyc-stdout.txt (singletons 58/56/58 @70857/71014/71526), cyc-d0seq.tsv
# Boot-log receipts (streaming greps; never copied)
fused id=31 line (@3330853) + waker=3 signals (25x, all <=6782) + cap @62119;
  probe change n=104/140/162 (@7592/7981/8272) + total->0x14 saturation;
  stacks table identical x1430; Wakeup/Sleep 0; pre-b0 s31 = 25 (13+12)
# Trace receipts (streaming greps; never copied)
382650 post enters (@185265229/@185265243, unwind pre-marker);
  423CC0 x2 (@21198/@29109 early-boot); 423CD0 x0
# Static reads (read-only bodies; E2/E3 firm-up)
$W/P1/output/sub_0031AAF0/003825F8/0031A6B8/003E4AF0/00326EB0.cpp
  (guard PCs + call sites); $R/ps2xRuntime/src/lib/Kernel/Stubs/Pad.cpp
# Report (this Part)
(edit_file append Part 34 in 2 chunks)
git add -f local/research/P1/REPORT.md
git commit -m "[P1ak] ..." (trailer Orchestrated-By: Muse Code; NO push)
```

Receipt paths: `/tmp/p1ak/log_pass.py|log_summary.txt`,
`/tmp/p1ak/tick_pass.py`, `/tmp/p1ak/trace_pass.py|
trace_summary.txt|trace_chunks.tsv|trace_edge.txt`,
`/tmp/p1ak/cycle_repro.py|cyc-stdout.txt|cyc-d0seq.tsv|
cyc-repidx.txt` (all uncommitted scratch; tables above are the
evidence).

## P34-4. What I could not do (gap rows)

- Read 3825F8's `*(a1+0x5A8C)` state (T4's first arm): fire ×0 over
  359,749 iters is consistent with both state≠4 and counter<limit
  (E3 reads it; brief-shaped §P34-2c).
- Read any guard-word VALUES (`*(v1+0x4038)`, `*(s0+0x20)`,
  `*(a0+0x1C)`, N/i, pad returns): fixed-by-count over 359,749
  iters, values unprobed (E3 rows specified).
- Simulate each of 326EB0's ~25 live-span branches individually:
  jointly fixed by the exact 2×/iter pad-pair over 719,498 pairs,
  per-branch proof needs symbolic execution or an E3 hit-count
  probe (same for 3E4AF0's pre-0x3e4db8 body — off the handler
  path, unexamined).
- Name the id-2/id-3 handler `argument` (a1) constants beyond the
  observed 0x31abd0 (id-2): registration values live in the host
  handler table, not in the receipts (E3 reads them).
- Join trace chunks to log blocks (no timestamps in either stream):
  chunk↔block correspondence is rate-inferred (≈60.1/s both), not
  observed (same gap as T13 §T13-7/T15 §T15-7/P1aj §P33-6).
- Attribute the halt-position spread (T13 74.1% w239, T15 9.1%
  w239, T16 97.85% w238), the wall-rate flatness, or the
  dormant-ratio surplus from inside the receipts (no host-load log
  in scope; tabled as guest-fixed wall variation, third datum:
  first sub-240 halt + second flat→30.2 shape).
- Attribute the +2 29-side edge (72,178 waits vs 72,176
  invocations): the trace carries no timestamps (carried from
  T13/T15/T16). The +1 in-phase 29-side window effect (blocks
  0–237: 71,873/71,872), the +1 markers-vs-Δ effect (359,749 vs
  359,748), and the 25 pre-block-0 s31 lines (13 waker=3 + 12
  waker=-1) are tabled by exact count, not derived.
- Re-mine T13/T15 traces for D4/D5 recurrence (6.6 GB each, out of
  the 4 h box): T13/T15 singleton/chunk values are cited from
  committed REPORTs (§T13-4/§T15-4 rows quoted); T16 values are
  independently reproduced here.
- Session wall time inside the 4 h box; zero lease touches (no
  contention possible).


