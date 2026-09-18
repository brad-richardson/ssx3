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
