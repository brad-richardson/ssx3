# E13 exact command record

Working directory `/Users/bradrichardson/dev/ssx3`. Every SSD step exported
`COPYFILE_DISABLE=1`. Commands below describe the completed experiment;
mutation/capture drivers enforce ownership and refuse repeated runs.

| Phase | Executed command / complete argv receipt |
|---|---|
| Update/read-in | `git pull --ff-only`; E13 brief and E12 REPORT/NEXT-BRIEF in full |
| Before snapshot | `python3 -B local/research/E13/e13_manifest.py before`; expected E12 snapshots copied into standalone E13 evidence |
| Independent row derivation | `python3 -B local/research/E13/e13_derive_row.py`; ELF words and emitted owner checked before the I17 comparison |
| Checkpoint checks | Actual test binary and E12 fixture argv in `checkpoint.json`; suite/output retained verbatim |
| Baseline relink | `python3 -B local/research/E13/e13_bounded.py baseline-link 1200 -- python3 -B local/research/E13/e13_link_test.py baseline`; full compiler/linker object argv in `baseline-binding-link.json` |
| Fail-before | `/Volumes/Extreme SSD/ps2recomp-spike/P1/e13-binding-tests/baseline/binding-test absent`, then `present`; rc0/1 |
| Per-tree proof/removal | `python3 -B local/research/E13/e13_reclaim.py probe <tree>`, then `remove <tree>`; actual script/each proof and removal JSON retain checks. Named order: t6-link,t12-link after fresh per-tree proofs, restoring build/link headroom; no pre-edit reclamation was needed |
| CSV edit | `python3 -B local/research/E13/e13_add_entry.py`; persisted fresh admission first |
| Generation | `python3 -B local/research/E13/e13_generate.py entry`; exact generator/config/cwd argv and all input hashes in `entry-generation.json` |
| Complete output audit | `python3 -B local/research/E13/e13_verify_output.py`; read-only verification, no generator repeat |
| Installation | `python3 -B local/research/E13/e13_install.py entry` |
| Scratch cleanup | `python3 -B local/research/E13/e13_cleanup_scratch.py`; installed-byte verification before owned removal |
| Observation extension | `python3 -B local/research/E13/e13_observe.py`; exact diff in `handwritten.patch`, no guest-state change |
| Rebuild | `python3 -B local/research/E13/e13_bounded.py entry-build 1800 -- cmake --build /tmp/p1-link/runtime --target ps2EntryRunner ps2x_tests -j4` |
| Suite | `/tmp/p1-link/runtime/ps2xTest/ps2x_tests` from fork cwd; full `entry-suite.txt`; `e13_validate_entry.py` records both fixture and suite |
| New fixture relink | `python3 -B local/research/E13/e13_bounded.py entry-link 1200 -- python3 -B local/research/E13/e13_link_test.py entry`; full actual-object argv in `entry-binding-link.json` |
| Truth table | `/Volumes/Extreme SSD/ps2recomp-spike/P1/e13-binding-tests/entry/binding-test present`; `entry-validation-results.json`, `entry-preflight.json` + full stdout/stderr |
| Validation driver | `python3 -B local/research/E13/e13_validate_entry.py`; records fixture and suite commands, return codes and identities |
| Fork commit/push | `git add -- games/ssx3/ssx3-functions.sweep.csv ps2xRuntime/include/ps2_e7.h ps2xRuntime/src/lib/ps2_runtime.cpp`; `git commit -m 'SSX3: restore the exact card-result leaf'`; `git push fork HEAD:ssx3`; remote SHA verified; full receipt `fork-commit.json` |
| Single boot | `python3 -B local/research/E13/e13_capture.py a --report-all --arm 600 --wall 90`; full argv/env/watch/caps in `e13a-config.json`, fresh checks in `e13a-preflight.json` |
| Close caps | `python3 -B local/research/E13/e13_close_capture.py`; released lease/pgrep checked with host visibility |
| Raw retention | `python3 -B local/research/E13/e13_retain.py a`; hash verification before raw removal |
| After snapshot | `python3 -B local/research/E13/e13_manifest.py after` |
| Binary record | `python3 -B local/research/E13/e13_build_record.py`; capture driver verifies this identity before boot |
| Observation closure | `python3 -B local/research/E13/e13_observation_audit.py`; unchanged raw and bounded formats explain the absent event-driven footer |
| Reproduction | `python3 -B local/research/E13/e13_reproduce.py`; seven analysis steps, eight byte-identical joined outputs |

Use the retained scripts for exact option syntax; resource/mutation drivers
must not be rerun as casual verification after scope closes. Complete shell
driver outputs and bounded-start/result records are retained alongside them.

The following reproduces analysis **without boots, builds or regeneration**:

```sh
export COPYFILE_DISABLE=1
python3 -B local/research/E13/e13_observation_audit.py
python3 -B local/research/E13/e13_mine.py a
python3 -B local/research/E13/e13_card.py a
python3 -B local/research/E13/e13_progress.py a
python3 -B local/research/E13/e13_frame.py a
python3 -B local/research/E13/e13_join.py
python3 -B local/research/E13/e13_residual.py
```

`e13_io.py` resolves removed original capture paths through
`e13a-retained.json`. Raw ELF disassemblies were produced with
`e13_static.py dis START END` (end exclusive); exact ranges appear in the
committed disassembly files. Trusted R5900 SQ decoding is retained.

Final retention uses `python3 -B local/research/E13/e13_pack_evidence.py`:
closed tool logs are compressed and identical snapshots have local relative
aliases, with round-trip hashes in `evidence-retention.json`. Final read-only
identity/process/storage checks use `e13_closeout.py`; `closeout.json` includes
complete command results. Neither closeout step executes the guest.

Evidence staging uses `git add -f -- local/research/E13` and a `[E13]` commit
with trailer `Orchestrated-By: Muse Code`. No ssx3 push; orchestrator gates it.

**E13 COMMANDS TAIL COMPLETE — exact long argv retained in JSON, not truncated.**
