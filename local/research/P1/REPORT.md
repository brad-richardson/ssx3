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

