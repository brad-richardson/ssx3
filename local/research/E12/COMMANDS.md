# E12 exact command record

Working directory `/Users/bradrichardson/dev/ssx3`. Every SSD step exported
`COPYFILE_DISABLE=1`. Commands below describe the completed experiment;
mutation/capture drivers enforce ownership and refuse repeated runs.

| Phase | Executed command / complete argv receipt |
|---|---|
| Update/read-in | `git pull --ff-only`; E12 brief and E11 REPORT/NEXT-BRIEF in full |
| Before snapshot | `python3 -B local/research/E12/e12_manifest.py before`; expected E11 snapshots copied into standalone E12 evidence |
| Checkpoint checks | Actual test binary and E11 fixture argv in `checkpoint.json`; suite/output retained verbatim |
| Baseline relink | `python3 -B local/research/E12/e12_bounded.py baseline-link 1200 -- python3 -B local/research/E12/e12_link_test.py baseline`; full compiler/linker object argv in `baseline-binding-link.json` |
| Fail-before | `/Volumes/Extreme SSD/ps2recomp-spike/P1/e12-binding-tests/baseline/binding-test absent`, then `present`; rc0/1 |
| Per-tree proof/removal | `python3 -B local/research/E12/e12_reclaim.py probe <tree>`, then `remove <tree>`; actual script/each proof and removal JSON retain checks. Named order: t1-link,t5-link before edit; t5-base-link,t5-rule-link during build |
| CSV edit | `python3 -B local/research/E12/e12_add_entry.py`; persisted fresh admission first |
| Generation | `python3 -B local/research/E12/e12_generate.py entry`; exact generator/config/cwd argv and all input hashes in `entry-generation.json` |
| Verifier correction | `python3 -B local/research/E12/e12_verify_output.py`; read-only replay, no generator repeat |
| Installation | `python3 -B local/research/E12/e12_install.py entry` |
| Scratch cleanup | `python3 -B local/research/E12/e12_cleanup_scratch.py`; installed-byte verification before owned removal |
| Observation extension | `python3 -B local/research/E12/e12_observe.py`; exact diff in `handwritten.patch`, no guest-state change |
| Rebuild | `python3 -B local/research/E12/e12_bounded.py entry-build 1800 -- cmake --build /tmp/p1-link/runtime --target ps2EntryRunner ps2x_tests -j4` |
| Suite | `/tmp/p1-link/runtime/ps2xTest/ps2x_tests` from fork cwd; full `entry-suite.txt` |
| New fixture relink | `python3 -B local/research/E12/e12_bounded.py entry-link 1200 -- python3 -B local/research/E12/e12_link_test.py entry`; full actual-object argv in `entry-binding-link.json` |
| Truth table | `/Volumes/Extreme SSD/ps2recomp-spike/P1/e12-binding-tests/entry/binding-test present`; `entry-binding-result.json` + full stdout/stderr |
| Fork commit/push | `git add -- games/ssx3/ssx3-functions.sweep.csv ps2xRuntime/include/ps2_e7.h ps2xRuntime/src/lib/ps2_runtime.cpp`; `git commit -m 'SSX3: restore the exact card status predicate'`; `git push fork HEAD:ssx3`; remote SHA verified; full receipt `fork-commit.json` |
| Single boot | `python3 -B local/research/E12/e12_capture.py a --report-all --arm 600 --wall 90`; full argv/env/watch/caps in `e12a-config.json`, fresh checks in `e12a-preflight.json` |
| Close caps | `python3 -B local/research/E12/e12_close_capture.py`; released lease/pgrep checked with host visibility |
| Raw retention | `python3 -B local/research/E12/e12_retain.py a`; hash verification before raw removal |
| After snapshot | `python3 -B local/research/E12/e12_manifest.py after` |

Use the retained scripts for exact option syntax; resource/mutation drivers
must not be rerun as casual verification after scope closes. Complete shell
driver outputs and bounded-start/result records are retained alongside them.

The following reproduces analysis **without boots, builds or regeneration**:

```sh
export COPYFILE_DISABLE=1
python3 -B local/research/E12/e12_mine.py a
python3 -B local/research/E12/e12_card.py a
python3 -B local/research/E12/e12_progress.py a
python3 -B local/research/E12/e12_frame.py a
python3 -B local/research/E12/e12_join.py
python3 -B local/research/E12/e12_residual.py
```

`e12_io.py` resolves removed original capture paths through
`e12a-retained.json`. Raw ELF disassemblies were produced with
`e12_static.py dis START END` (end exclusive); exact ranges appear in the
committed disassembly files. Trusted R5900 SQ decoding is retained.

Evidence staging uses `git add -f -- local/research/E12` and a `[E12]` commit
with trailer `Orchestrated-By: Muse Code`. No ssx3 push; orchestrator gates it.

**E12 COMMANDS TAIL COMPLETE — exact long argv retained in JSON, not truncated.**
