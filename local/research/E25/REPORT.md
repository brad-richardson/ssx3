| E25 | Receipt |
|---|---|
| Stop point | **All missions executed; nothing blocked.** The fork gate ran first and passed, the loss was inventoried, the runner and suite were rebuilt from `3adc0478` with the EXACT E18 recipe, verified without a boot, and the re-baseline evidence assembled. The headline: the rebuild is **bit-identical**. `ps2EntryRunner` returns at **163,529,696 B / `e462e448…67e22`** and `ps2x_tests` at **5,695,128 B / `2152e5ad…f04c0`** — the very pins E24 declared lost. **No re-baseline is needed for either binary.** Fix gate: **N/A** (no diagnosis, no code change). |
| Checkpoint | Fork triple-agreed at `3adc0478…` at open and close; `status --short` exactly `?? ps2_log.txt`. 9,457 generated names/hashes equal; 21 E18 input/behaviour source hashes equal; both SSD fixture binaries and the reused observer sha-equal. **Restored:** 458/458 UNLOADED, 458/458 observer-LOADED, E15 rc0s, E16 closure 6, prior 24/3/14/4/DROP, absorbed 8, E18 R1–R6 present and byte-identical. **567/575** protected pins in the rebuilt tree return byte-identical. |
| Questions reached | H1 realised, H0 falsified: the build is reproducible, not merely equivalent. The 8 pins that did move have a **measured** cause with no exception. The two trees E25 did not rebuild are proven **irreproducible at this fork** — they are pre-E18 output. |
| Mutations / launches | Zero fork source edits, zero fork commits, zero pushes, zero regeneration, zero observer rebuilds, **zero title boots, zero lease claims, zero deletions**. One configure, one `ninja` invocation. |
| Next dependency | **E26 can spend E24's designed e24a boot unchanged.** The boot argv's exact path is populated, E24's capture preflight hash gate passes on all five pins as written, and `PS2X_DIAG_SEMA` is compiled into the rebuilt runner. Nothing in E24's boot design needs re-pinning. |

| Experiment contract | Bound / observable |
|---|---|
| Time box | Start `2026-09-22T12:03:15Z`; deadline `2026-09-22T20:03:15Z`; eight hours. Final audit `2026-09-22T12:28:10Z`. **Actual time used: 24 min 55 s** (open → final audit), well inside the box. |
| Required reads | E25 prompt; E24 REPORT 166 lines; E23 REPORT 144 lines; E18 NEXT-BRIEF 41 lines; and E18's build records — `configure-command.json`, `e18_configure.py`, `e18_common.py`, `build-driver.txt`, `build-source-only-driver.txt`, `built-binaries.json`, `configure.log`, `e18_retain_sidecars.py` — all read in full before the first copy, rename or configure. |
| Hypothesis | **H0**: the rebuild is behaviourally identical but the SHA differs (derived output). **H1**: the rebuild is bit-identical and no re-baseline is needed. **H2**: behaviour differs → red, nothing re-baselined. |
| Result | **H1 held, H0 falsified for the two binaries that matter.** The runner and the suite are byte-for-byte the lost pins; all 552 pinned `.o` objects reproduce exactly; 8 of 575 pinned files differ and every one is an ar-timestamped archive or the PCH. H2 never arose — every behavioural comparison matched. |
| Alternatives | (a) bit-identical; (b) SHA differs / behaviour identical; (c) behaviour differs; (d) recipe ambiguous or build fails. **(a) realised.** (b) survives only in the 7 archives + 1 PCH, with the cause measured; (c) excluded by two full suite transcripts, 10 observer footers, 18 fixture cases and 8 absorbed controls; (d) did not arise — the recipe was loaded from E18's own receipt and asserted equal to a literal transcription before a byte was configured. |
| Observable | Per-path present/missing; fork triple-agree; 9,457 + 21 source audits; 575 protected pins re-hashed old-vs-new; every build command with argv, rc, elapsed, stdout; configure log diffed line by line; build graph diffed edge by edge; suite transcripts diffed line by line unloaded and loaded; observer footers diffed field by field; snapshot manifest with per-file SHA256. |
| Strict order | Contract → toolchain audit + admission → **fork gate (first)** → loss inventory → hex-safe rename + proof → intentional tooling changes → configure → build → pins → delta cause → unloaded regression → observer-LOADED regression → behaviour compare → cadence control → E26 readiness → durability snapshot → re-baseline table → close. Opened in order; no gate tripped. |
| Fix gate | **N/A, recorded not skipped.** E25 performs no diagnosis and changes no source. `fix-gate.json`. |
| Preserved constraints (E18 ABI, BINDING) | Caller-owned synchronous dispatch; word0-only cbData; `v0` discarded; valid-no-input waits; dispatch outside the MPEG mutex; delete/reset cancellation. **Preserved by construction** — E25 edited no source at all and built from the unmodified fork tree; and preserved by *measurement*, since the resulting binaries are byte-identical to the ones every prior lane's receipts were taken on. |
| Contract source | `CONTRACT.md`, written before the first copy, rename, configure or build. **No amendment declared.** The internal reservation is 3 GiB, declared up front in the contract, not amended mid-run: E23's amendment A1 shrank it to 512 MiB precisely because E23 ran no full build, and E25 must. Floor and guard unchanged at 2 GiB + 0.5 GiB. |

| **Mission 1 — the loss, inventoried** | Receipt |
|---|---|
| Fork gate, run FIRST | `e25_fork_gate.py` — a standalone tool that exits non-zero on any disagreement, so no later step can run on a moved fork. **GREEN**: `HEAD`, `refs/remotes/fork/ssx3` and `ls-remote` all `3adc0478b6d2260acdd28a249466f2eef9a20176`; `status --short` exactly `?? ps2_log.txt`; the pre-existing AppleDouble Git-index warning retained on stderr only. `fork-gate.json`. |
| The three protected paths | `/tmp/p1-link/runtime`, `/tmp/e17-map-link/runtime`, `/tmp/e18-mpeg-link/runtime` — **all three absent at open**, allocated 0. |
| Per-tree loss | p1-link **575 / 526,188,690 B**; e17-map-link **575 / 526,234,570 B**; e18-mpeg-link **575 / 526,573,522 B**. **1,725 of 1,725 missing, 1,578,996,782 B, zero present.** E25 re-measured this independently and **agrees with E24's §1 table exactly** (`e25_agrees_with_e24: true`). |
| 9,457-name audit | **9,457 / 9,457**, every SHA256 equal to E18's manifest. Expected green, and green. |
| 21 E18 input/behaviour sources | **21 / 21** sha-equal. |
| Survived | Both SSD fixture binaries (`42d9f4f3…87326`, `3136f3ca…79a2`) and the E21 observer dylib (`e4d88fdc…b38e6be`, 52,472 B) sha-equal; all eight retained e23a title artifacts present. **Reused by copy + re-sha, never rebuilt** (`instrument-reuse.json`). |
| Posture at open | Lease absent, `pgrep -x ps2EntryRunner` rc 1. |

| **Mission 2 — the rebuild, on E18's exact recipe** | Receipt |
|---|---|
| Recipe provenance | The cmake argv is **loaded from `local/research/E18/configure-command.json`** and asserted equal to a literal transcription in `e25_configure.py` before anything is configured. Both agree; `jobs == 2` asserted. A rebuild that does not use E18's flags would refuse rather than improvise. |
| Configure | `cmake -S …/PS2Recomp -B /tmp/e18-mpeg-link/runtime -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=/opt/homebrew/opt/llvm/bin/clang -DCMAKE_CXX_COMPILER=…/clang++ -DCMAKE_OSX_ARCHITECTURES=arm64 -DPS2X_BUILD_STUDIO=OFF -DPS2X_BUILD_RUNTIME=ON -DPS2X_BUILD_TEST=ON -DPS2X_ENABLE_RUNTIME_LOGS=ON -DPS2X_ENABLE_AGRESSIVE_LOGS=ON -DPS2X_ENABLE_IOP_RPC_TRACE=ON -DPS2X_STRICT_RETURN_DIAGNOSTICS=OFF -DPS2X_ENABLE_FFMPEG=ON`. **rc 0, 72.5 s** (E18: 74.5 s), stdout 31,900 B. E18's own `assert not NEWB.exists()` kept and satisfied. |
| **Same build directory** | `/tmp/e18-mpeg-link/runtime` — the brief's "same paths". Every downstream driver, pin and boot argv names that path, so rebuilding in place makes the re-baseline a pure question about bytes rather than bytes *and* location. |
| Configure log, compared | **Line-for-line identical to E18's**: 214 substantive lines each, `identical: true`, zero lines on either side. Only git transfer progress was dropped and `(N.Ns)` / `[n/m]` masked. `configure-compare.json`. |
| FetchContent dependency HEADs | **All three byte-identical** to E18's: raylib `c1ab645c` (tag 5.5), imgui `b1bcb12` (v1.92.7-docking), rlImGui `118221c` (Raylib_5_5). The one part of a FetchContent configure that could silently move, measured and unmoved. |
| Build | `ninja -C /tmp/e18-mpeg-link/runtime -j2 ps2EntryRunner ps2x_tests` — **the same argv E18 ran**. **rc 0, bound null, 530.8 s, 543/543 edges, stdout 72,514 B, not truncated.** One invocation. |
| Why E18 needed two | E18's own source edits created two AppleDouble sidecars on the ExFAT volume; CMake's glob compiled `._MPEG.cpp`, clang echoed its binary contents, and E18's first `ninja` died on the 15 MB stdout cap at edge 195/544. E18 **retained** both sidecars by rename (no deletion) and re-ran. E25 needed one invocation because those two files have been out of the source tree since. `compile_commands.json` has **0** AppleDouble entries. |
| Build graph, compared | E18's union of logged edges 566; E25's 543. **Edges only in E25: 0.** The 23 E18-only entries are its extra AppleDouble compile edge, 21 FetchContent sub-steps (which in E25 ran during configure) and one `Re-running CMake...` forced by the sidecar rename. E25 ran nothing E18 did not. `build-compare.json`. |
| Ambiguity encountered | **None.** No flag was guessed; no line was stopped. |

| **Mission 3 — verified without a boot** | Receipt |
|---|---|
| Suite, UNLOADED | **rc 0, 458 passed / 0 failed.** Transcript **1,137 lines / 458 runs**, identical to E23's. |
| Suite, observer-LOADED | **rc 0, 458 passed / 0 failed** with the REUSED dylib. Transcript **1,137 lines / 458 runs**, identical to E23's. |
| The only difference in either transcript | **8 raw lines across the two runs — the four `mc0` tests, which echo their own `TMPDIR` scratch path.** That path carries the lane directory name (`E23`→`E25`) and a monotonic-clock nonce. Masking exactly that span and nothing else leaves **residual 0** in both runs. Declared as a free field and named, not silently normalised. `suite-compare-checkpoint.json`, `suite-compare-observer.json`. |
| **E18 R1–R6** | **6/6 present and byte-identical** in both the unloaded and the loaded transcript. |
| E15 | no-input and input both **rc 0**, `saved128=1 waitReason=6 callbackCalls=1 resumes=0`, unloaded and loaded. |
| E16 closure | six modes **rc 0**, unloaded and loaded. |
| Prior actual bindings | **24 / 3 / 14 / 4 / DROP**, unloaded and loaded. |
| Absorbed entries | 5 presence checks + 3 ownership controls, **all rc 0**. |
| Observer closures | **10/10** receipt-verified, `pending=0` and `bindingChecks=4` on every one, real `# E21 PARSER CLOSURE` footers. The suite's own observer directory is once more the loaded run that **reaches the parser** — `parseCalls=8`, exactly E23's. |
| Field-by-field compare | All ten observer footers, all 18 fixture cases and all 8 absorbed controls **MATCH** against E23's receipts. Two fields are declared free and **named**: `ns` (the observer's own wall clock) and `eventBytes` (the event-text length, which embeds the lane path). Every other counter — `events 38, parseCalls 8, offered 624, consumed 264, packets 4, packetBytes 188, sendCalls 5, sendEof 1, receiveCalls 7, frames 2, errors 0, returned 20, pending 0, bindingChecks 4` — is equal. `behavior-compare.json`. |
| Carried control (beyond mission 3) | The complete-feed cadence reference re-run on the **surviving** E23 fixture with the reused observer: 60 → STALLED, 120 → STALLED, 180 → SERVED, 240 → SERVED; `producerFirings=1`, `addBs=1` on all four; `matched=0` on both served branches; all `pending=0 errors=0 bindingChecks=4`. **All four cases match E24's run field for field**, on a binary sha-equal to the one E24 used. `cadence-compare.json`. |
| **Named limit** | The suite exercises the runtime/MPEG layer the runner shares, **not** the 9,457 generated guest sources that only the runner links. That half is covered here by **binary identity** — the rebuilt runner *is* the binary E23 booted — and not by execution. Running the runner would be a boot, which this brief forbids. Stated as a limit, not papered over. |

| **Mission 4 — the OLD-vs-NEW pin table** | Receipt |
|---|---|
| Scale | **34 pins: 29 MATCH, 4 MATCH\*, 1 DELTA, 0 BLOCKED.** `rebaseline.json` carries every row with old value, new value and cause. `MATCH*` means the pin matches once a field this lane **declared and named** free is set aside; it is not a softened DELTA. |
| **Runner** | bytes `163,529,696` → **`163,529,696`**; SHA256 `e462e4482fbf5b3fe0902e793f9d677e51c56b220022bca619305f1f69967e22` → **identical**. |
| **Suite** | bytes `5,695,128` → **`5,695,128`**; SHA256 `2152e5ad53f19741788aa3051e26184a9c5e831857114ce74407f199de5f04c0` → **identical**. |
| 575 protected pins in the rebuilt tree | **567 IDENTICAL**, 7 same-size-different-SHA, 1 different-size, **0 missing**. All **552** pinned `.o` objects reproduced bit-for-bit. 0 files produced that E23 had not pinned. |
| **The 7 archives — cause, measured** | `libfmt.a`, `libdwarf.a`, `libraylib.a`, `libps2_iop.a`, `librabbitizer.a`, `libimgui.a`, `librlImGui.a`. **Every archive that did NOT reproduce carries ar member dates written by THIS build** (epoch 1790079024–1790079081); **every archive that DID reproduce carries either deterministic dates (0, or a small index) or the frozen dates of a vendored prebuilt** (`libglfw3.a`, 2022). **The split has no exception in either direction.** Cause = **ar member timestamps → rebuild nondeterminism**; *not* toolchain drift, *not* a path change. |
| The 7 archives — impact, bounded | Each differing archive's members were parsed out and matched against the pinned `.o` files: **every member except the archive's own `__.SYMDEF` index is one of the objects that reproduced bit-for-bit** (61/62, 32/33, 28/29, 11/12, 5/6, 2/3, 1/2). The content is identical; only the headers move. And the binaries these archives link into are byte-identical to their pins, so the delta is provably inert. `delta-cause.json`. |
| The 1 PCH | `cmake_pch.hxx.pch`, 31,713,456 → **31,713,452 B (−4)**. No embedded ISO date or ctime string was found in it. **The original bytes were wiped with the tree, so the 4-byte difference cannot be located by diff and is not guessed.** Its impact is bounded instead by measurement: **every object compiled through this PCH reproduced exactly**, and so did the runner it feeds. |
| Toolchain drift | **None.** clang 23.1.1 (both C and C++, at E18's exact paths), cmake 4.4.3, pkg-config 3.0.7, libavcodec/libavformat 63.1.101, libavutil 61.1.101, libswresample 7.1.101, libswscale 10.1.101 — every value equal to E18's own configure log and P1's REPORT. Ninja's version (1.13.2) was **not recorded by any prior lane** and is noted as unpinnable rather than claimed as matching. `toolchain-audit.json`. |
| **The single DELTA** | The `1,725 protected build hashes` pin. E25 rebuilt **one** of the three trees. 1,150 files in `/tmp/p1-link` and `/tmp/e17-map-link` remain absent. |
| Why those two were not rebuilt — reason 1, **irreproducible** | All 575 relative paths are shared with the E18 tree, but **336 hashes differ in each**. The decisive probe: `MPEG.cpp.o` and `ps2_runtime_expansion_tests.cpp.o` — the two files E18's commit changed (+189/−3 and +284) — are **identical between p1-link and e17-map-link and different in the E18 tree**. Both trees are therefore **pre-E18 output**. A build at `3adc0478` would reproduce the E18 tree again under another directory name; it **cannot** reproduce their pins. |
| Why those two were not rebuilt — reason 2, **cost** | E25 measured one tree at **603.2 s and 1,766,981,632 B**. Two more would need **3,533,963,264 B against a 3,221,225,472 B internal reservation** (does not fit) and would leave free space below the 2.5 GiB floor+guard (headroom at the time: 3,046,993,920 B; also does not fit). |
| What is lost with them | The P1 and E17 build trees. **No E15–E23 receipt was taken on either runner.** E23 booted, and E18/E21/E22/E23 measured, the `e18-mpeg-link` binaries — which E25 reproduced bit-for-bit. `other-trees.json`. |
| **The decision** | **Not made here.** The table is tabled. The orchestrator gates it. |

| **Mission 5 — durability** | Receipt |
|---|---|
| Why a tar | The SSD is ExFAT with ~1 MiB clusters, so copying 7,342 files individually would allocate gigabytes of slack; and large writes to this volume have previously read back as zeros. The tree is stored as **one** tar and every artifact is **re-read and re-hashed after it lands**. |
| Tree snapshot | `P1/e25-snapshot/e18-mpeg-link.tar` — **1,762,803,200 B**, SHA256 `9ded8065…`, re-read hash **equal**. `tar -tf` lists **7,342 file members**, which **equals the manifest count exactly**. |
| Standalone binaries | `ps2EntryRunner` 163,529,696 B and `ps2x_tests` 5,695,128 B copied with `cp -p`, each re-sha'd twice and matching both the source and the historical pin. A two-binary restore is enough to boot and to run the 458 tests. |
| Per-file manifest | `snapshot-manifest.json` — **7,342 files, 1,748,192,253 B**, each with its own SHA256, computed on the internal volume before the tar. |
| Restore procedure | `RESTORE.md` — full-tree restore, two-binary restore, per-file verification script, and the rebuild-from-fork fallback with E25's measured 72.5 s + 530.8 s. |
| **Not exercised** | The restore was **not tested**; testing it would mean deleting the live tree, which the brief forbids. Stated in `RESTORE.md` itself. |
| Deletions | **Zero**, here and everywhere in the lane. |

| What E26 inherits, checked | Receipt |
|---|---|
| Boot argv | Both paths of E23's argv exist: `/tmp/e18-mpeg-link/runtime/ps2xRuntime/ps2EntryRunner` and `…/P1/cd/SLUS_207.72`. |
| Identity | The rebuilt runner **is** the binary E23 booted (SHA equal). Every property E15–E23 measured on that binary transfers **by identity**, not by re-measurement. |
| E24's capture preflight gate | Run as written against all five pins it checks — runner, suite, both ELF copies (`1b49d05c…7af7bc`, 3,890,784 B) and the observer dylib. **All five pass.** E24's driver needs **no re-pinning**. |
| Second instrument | `PS2X_DIAG_SEMA` present in `EeScheduler.cpp` at `3adc0478` and **compiled into the rebuilt runner** (verified in the binary's strings, alongside `PS2X_DIAG_SEMA_S0` and `PS2X_DIAG_PERIOD_MS`). E24's boot design depends on it. |
| Posture | Lease absent, `pgrep` rc 1, **no `boot-attempt.json` written by E25**. `e26-readiness.json`, all nine checks PASS. |

| Storage / execution budget | Admission and accounting |
|---|---|
| Internal reservation | **3 GiB**, declared in `CONTRACT.md` before the first action (E23's A1 512 MiB applied to a lane that ran no build). Floor 2 GiB + 0.5 GiB guard **unchanged**. |
| SSD reservation | 16 GiB in NEW `e25-*` paths; same floor/guard. |
| Initial admission | `2026-09-22T12:04Z`: internal 7,281,795,072 B free / SSD 148,472,070,144 B free. Both reservations fit. |
| Final audit | Internal owned **1,770,418,176 B** of 3,221,225,472 reserved, free 5,728,362,496; SSD owned **2,301,624,320 B** of 17,179,869,184 reserved, free 144,399,400,960; **fork growth 0**. Every cap within bounds, both floors clear. |
| The E23 hazard, re-measured | E23 measured a thin-LTO **relink** costing 2.93 GB of internal volume that was never returned. E25's full build moved `build_allocated` +530,452,480 B while internal free fell only **82,948,096 B** — the system returned the rest. **The hazard did not recur**, and the floor gate was never approached. |
| Accounting | `st_blocks × 512`, incl. ExFAT directory/AppleDouble allocation; `COPYFILE_DISABLE=1` on every SSD step. **No reclaim, no deletion.** |
| Boot cap utilisation | **None — no boot.** |

| Tooling provenance | Receipt |
|---|---|
| Pure rename (9 files) | `io / bounded / validate / closed_events / parser_receipt / baseline / observer_regression / mine / cadence`, E24 → E25. Hex-safe normalized diff **byte-empty for all nine**; every hex run byte-equal; **and** a new **protected-token count check** asserting each protected token appears the same number of times before and after — a check E24 made only implicitly. `rename-proof-hexsafe.json`. |
| Errata E23-E1 honoured | Runs of ≥16 hex characters are masked **before** renaming, so a digest cannot be rewritten. |
| Protected tokens | The five E21 instrument tokens; `e23-fixtures/complete` and `# E23 COMPLETE FEED FIXTURE TAIL COMPLETE` (the surviving cadence fixture binary and its footer); **E25 adds** `e18-fixtures/after` and `/tmp/e18-mpeg-link/runtime` — E18-spelled by necessity, since the brief requires the exact E18 paths. |
| Intentional changes (5, all recorded) | Three E24 `CHANGE` blocks exist only because E24 had no suite binary. E25 rebuilt it, so they are reverted to the E23 shape they describe: the 458-test gate runs again unloaded and loaded, and the suite's own observer directory returns as the parser-reach receipt. Each edit is a literal before/after pair applied idempotently, with full diffs in `tooling-diff.md` and data in `tooling-changes.json`. The presence short-circuit in `suite()` is **kept** — it is the gate that would catch a failed rebuild — but is no longer expected to fire, and both callers now assert it did not. |
| `e25_common.py` | Written fresh, not renamed: internal reservation 3 GiB; `NEWB = B0`, i.e. the rebuild target **is** the E18 path; comments name why one tree and not three. |
| New files | `e25_fork_gate.py`, `e25_inventory.py`, `e25_open.py`, `e25_configure.py`, `e25_configure_compare.py`, `e25_build_compare.py`, `e25_pins.py`, `e25_delta_cause.py`, `e25_suite_compare.py`, `e25_behavior_compare.py`, `e25_cadence_compare.py`, `e25_other_trees.py`, `e25_instrument.py`, `e25_snapshot.py`, `e25_rebaseline.py`, `e25_e26_readiness.py`, `e25_patch.py`, `e25_rename.py`, `e25_close.py`. |
| `stdbuf` in E25 | Absent from every argv. No boot argv was ever built; no capture driver was created in this lane at all. |

| Fix gate | Receipt |
|---|---|
| Applicability | **N/A.** E25 performs no diagnosis and proposes no code change; the brief sets the fix gate to N/A for this lane. Recorded with its receipt rather than skipped silently. |
| Demonstrated edges | None sought. The lane's findings are about the *build*, not the target: the recipe is reproducible; the 8 moving pins are ar timestamps and a PCH; the other two trees are pre-E18 output. |
| Mutations | Zero fork source edits, zero fork commits, zero pushes. `fix-gate.json`. |
| X, unchanged | E24 left X as: the feed is one structurally complete picture missing only its terminating start code — **why does the guest stop one start code short?** — and, separately, why does semaphore 36's only signaller never run. E25 moves neither; it restores the instrument that can answer them. |

| Exact command record | Invocation / artifact |
|---|---|
| Environment | `export COPYFILE_DISABLE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=…/E25`; the bounded wrapper sets a task-specific `TMPDIR` on the SSD and `CMAKE_BUILD_PARALLEL_LEVEL=2`. |
| Rename + patch + instrument | `python3 …/e25_rename.py io bounded validate closed_events parser_receipt baseline observer_regression mine cadence` → `rename-proof-hexsafe.json`; `python3 …/e25_patch.py`; `python3 …/e25_instrument.py` → `instrument-reuse.json`. |
| Gate 1 (first) | `python3 …/e25_fork_gate.py` → `fork-gate.json`, green. |
| Open / inventory | `python3 …/e25_open.py` → `toolchain-audit.json`, `admission-open.json`; `python3 …/e25_inventory.py` → `inventory.json`, `generated-audit.json`. |
| Configure | `… e25_bounded.py configure 1800 -- python3 …/e25_configure.py`; rc 0, 72.5 s. Then `python3 …/e25_configure_compare.py`. |
| Build | `… e25_bounded.py build 7200 -- ninja -C /tmp/e18-mpeg-link/runtime -j2 ps2EntryRunner ps2x_tests`; rc 0, 530.8 s, bound null. Then `python3 …/e25_build_compare.py`. |
| Pins / cause | `python3 …/e25_pins.py` → `pins.json`; `python3 …/e25_delta_cause.py` → `delta-cause.json`; `python3 …/e25_other_trees.py` → `other-trees.json`. |
| Unloaded regression | `… e25_bounded.py checkpoint-regression 1200 -- python3 …/e25_baseline.py`; rc 0, 458/458. |
| Loaded regression | `… e25_bounded.py observer-regression 1200 -- python3 …/e25_observer_regression.py`; rc 0, 458/458, 10/10 closures. |
| Cadence control | `… e25_bounded.py cadence 900 -- python3 …/e25_cadence.py`; rc 0, four cases plus nine carried controls. |
| Compares | `python3 …/e25_suite_compare.py checkpoint`; `… observer`; `python3 …/e25_behavior_compare.py`; `python3 …/e25_cadence_compare.py`. |
| Readiness / durability | `python3 …/e25_e26_readiness.py`; `… e25_bounded.py snapshot 1800 -- python3 …/e25_snapshot.py`. |
| Re-baseline / close | `python3 …/e25_rebaseline.py` → `rebaseline.json`; `python3 …/e25_close.py` → `final-audit.json`, all green. |
| Never executed | Any fork edit, commit or push; any regeneration or CSV work; any observer rebuild; any title boot; any lease claim; `stdbuf` in any argv; any deletion or reclaim; any test of the restore procedure. |

| Evidence hygiene / handoff | Receipt |
|---|---|
| Standalone data | Contract; toolchain audit; open admission; fork gate; loss inventory with per-tree table; rename/protected-token/tooling proofs; configure command, log and line-by-line compare; build log, bounded result and edge-by-edge compare; 575-pin old-vs-new table; measured delta cause; unloaded and loaded regression logs and receipts; two suite transcript compares; field-by-field behaviour compare; cadence control and its compare; other-trees analysis; E26 readiness; snapshot manifest and receipts; restore procedure; the 34-pin re-baseline table; fix gate; final audit. |
| Retained copies | `parser/e21-parser-observer.dylib` (reused, re-sha'd), `observer-receipts/`, `cadence-*-events.txt`, `checkpoint-*.txt`, `observer-*.txt`. |
| `.suite-*` scratch | `.suite-checkpoint` and `.suite-observer` created and retained on disk; **left unstaged**, matching E23's convention. The loaded suite's observer receipts are preserved canonically under `observer-receipts/` (20 files, committed). |
| Tail qualification | Every bounded tool, suite, fixture, receipt and compare ends with its real `TAIL COMPLETE` footer; counts re-verified, never appended. |
| Errata carried | **E21-E1, E23-E1, E23-E2, E24-E1, E24-E2, E24-E3 carried forward unchanged and not re-fixed.** E24-E2 is honoured operationally: the tail receipt below was recomputed **after** the last edit to this file. **E25 adds no errata.** |
| Publication | `[E25]` evidence commit with `Orchestrated-By: Muse Code`, `git add -f`. Scope: E25 evidence only; no fork files, no generated sources. **Not pushed** — the orchestrator pushes at poll. |

| Tail receipt | Value |
|---|---|
| Complete prefix | Lines 1–145; 27055 B; SHA256 `dec185027d5965567c9e770062682ef318cdc091ac7fead2f89ac7900aef0ed3` (the prefix is every line ABOVE the `| Tail receipt | Value |` header, so this row lives after the boundary and cannot invalidate itself — errata E24-E2) |
| Source-tail gap | **None, and one named limit.** Every E25 capture carries its real footer. The limit is that the runner's generated-code half is verified by **binary identity** rather than by execution, because executing it is a boot and the brief forbids one; it is stated as a limit, not inferred away. The PCH's 4-byte delta is likewise declared unlocatable — the original bytes are gone — and bounded by measurement rather than explained by guess. |
| E25 REPORT TAIL COMPLETE | The fork gate passed first, so the rebuild was safe to start; the E18 recipe was loaded from E18's own receipt rather than retyped, and it **reproduced the lost binaries exactly** — `ps2EntryRunner` `e462e448…67e22` and `ps2x_tests` `2152e5ad…f04c0`, both byte-identical, with 567 of 575 protected pins and all 552 objects returning unchanged. The 8 that moved are 7 ar-timestamped archives and one PCH, cause measured with no exception and impact bounded to zero by the binaries they feed. Two full suite transcripts, ten observer footers, eighteen fixture cases, eight absorbed controls and the four-point cadence reference all reproduce E23 exactly, modulo two named free fields. The two unrebuilt trees are proven pre-E18 output and unreproducible at this fork. The tree is snapshotted to the SSD with a 7,342-file manifest and a tabled, untested restore. **E26 can spend E24's designed boot unchanged: the argv path is populated, the preflight gate passes as written, and the runner is the very binary E23 booted.** 0 boots, 0 lease claims, 0 fork edits/commits/pushes, 0 deletions, 0 amendments, 0 new errata. |
