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

