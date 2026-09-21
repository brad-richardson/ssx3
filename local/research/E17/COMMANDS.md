# E17 exact command receipts

| Context | Setting |
|---|---|
| Working directory | `/Users/bradrichardson/dev/ssx3` unless the linked structured receipt names another cwd |
| SSD operations | `export COPYFILE_DISABLE=1`; allocated bytes tracked by `st_blocks*512` |
| Baseline selection | `E17_BUILD_DIR=/tmp/p1-link/runtime` for baseline suite/link/fixture steps; fresh E17 phases use default `/tmp/e17-map-link/runtime` |
| Host parallelism | `CMAKE_BUILD_PARALLEL_LEVEL=2`; Ninja command explicitly `-j2` |
| Replay | `E17_CANONICAL_ONLY=1` for canonical replay and final audit; no title launch |
| Recorded boot | Command below is historical; the E17 allowance is spent |

| Phase | Exact command / structured receipt |
|---|---|
| Initial checkpoint | `python3 -B local/research/E17/e17_checkpoint.py`; [checkpoint.json](checkpoint.json), [opening-git.json](opening-git.json) |
| Five-row reverify | `python3 -B local/research/E17/e17_rows.py`; [row-verification.json](row-verification.json) |
| Retained-only row proof | `python3 -B local/research/E17/e17_verify_retained.py`; [retained-row-verification.txt](retained-row-verification.txt) |
| CSV edit | `python3 -B local/research/E17/e17_absorb.py edit`; [map-edit.json](map-edit.json) |
| Output verification / installation | `python3 -B local/research/E17/e17_absorb.py verify` then `python3 -B local/research/E17/e17_absorb.py install`; [generation-scope.json](generation-scope.json), [installation.json](installation.json) |
| baseline-suite | `python3 -B local/research/E17/e17_bounded.py baseline-suite 300 -- python3 -B local/research/E17/e17_validate.py baseline suite`; [baseline-suite-bounded-start.json](baseline-suite-bounded-start.json) |
| baseline-closure | `python3 -B local/research/E17/e17_bounded.py baseline-closure 300 -- python3 -B local/research/E17/e17_validate.py baseline-closure '/Volumes/Extreme SSD/ps2recomp-spike/P1/e16-fixtures/after/binding-test' after`; [baseline-closure-bounded-start.json](baseline-closure-bounded-start.json) |
| baseline-prior | `python3 -B local/research/E17/e17_bounded.py baseline-prior 300 -- python3 -B local/research/E17/e17_validate.py baseline-prior '/Volumes/Extreme SSD/ps2recomp-spike/P1/e16-fixtures/after/binding-test' prior`; [baseline-prior-bounded-start.json](baseline-prior-bounded-start.json) |
| baseline-link | `python3 -B local/research/E17/e17_bounded.py baseline-link 1200 -- python3 -B local/research/E17/e17_link_test.py before`; [baseline-link-bounded-start.json](baseline-link-bounded-start.json) |
| five-fail-before | `python3 -B local/research/E17/e17_bounded.py five-fail-before 300 -- python3 -B local/research/E17/e17_presence.py before`; [five-fail-before-bounded-start.json](five-fail-before-bounded-start.json) |
| five-fail-before-complete | `python3 -B local/research/E17/e17_bounded.py five-fail-before-complete 300 -- python3 -B local/research/E17/e17_presence.py before complete`; [five-fail-before-complete-bounded-start.json](five-fail-before-complete-bounded-start.json) |
| generation | `python3 -B local/research/E17/e17_bounded.py generation 1200 -- python3 -B local/research/E17/e17_absorb.py generate`; [generation-bounded-start.json](generation-bounded-start.json) |
| configure | `python3 -B local/research/E17/e17_bounded.py configure 1800 -- cmake -S '/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp' -B /tmp/e17-map-link/runtime -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=/opt/homebrew/opt/llvm/bin/clang -DCMAKE_CXX_COMPILER=/opt/homebrew/opt/llvm/bin/clang++ -DCMAKE_OSX_ARCHITECTURES=arm64 -DPS2X_BUILD_STUDIO=OFF -DPS2X_BUILD_RUNTIME=ON -DPS2X_BUILD_TEST=ON -DPS2X_ENABLE_RUNTIME_LOGS=ON -DPS2X_ENABLE_AGRESSIVE_LOGS=ON -DPS2X_ENABLE_IOP_RPC_TRACE=ON -DPS2X_STRICT_RETURN_DIAGNOSTICS=OFF -DPS2X_ENABLE_FFMPEG=ON`; [configure-bounded-start.json](configure-bounded-start.json) |
| build | `python3 -B local/research/E17/e17_bounded.py build 7200 -- ninja -C /tmp/e17-map-link/runtime -j2 ps2EntryRunner ps2x_tests`; [build-bounded-start.json](build-bounded-start.json) |
| current-suite | `python3 -B local/research/E17/e17_bounded.py current-suite 300 -- python3 -B local/research/E17/e17_validate.py current suite`; [current-suite-bounded-start.json](current-suite-bounded-start.json) |
| current-link | `python3 -B local/research/E17/e17_bounded.py current-link 1200 -- python3 -B local/research/E17/e17_link_test.py after`; [current-link-bounded-start.json](current-link-bounded-start.json) |
| five-present | `python3 -B local/research/E17/e17_bounded.py five-present 300 -- python3 -B local/research/E17/e17_presence.py after`; [five-present-bounded-start.json](five-present-bounded-start.json) |
| current-binding | `python3 -B local/research/E17/e17_bounded.py current-binding 300 -- python3 -B local/research/E17/e17_validate.py current-binding '/Volumes/Extreme SSD/ps2recomp-spike/P1/e17-fixtures/after/binding-test' prior`; [current-binding-bounded-start.json](current-binding-bounded-start.json) |
| current-closure | `python3 -B local/research/E17/e17_bounded.py current-closure 300 -- python3 -B local/research/E17/e17_validate.py current-closure '/Volumes/Extreme SSD/ps2recomp-spike/P1/e17-fixtures/after/binding-test' after`; [current-closure-bounded-start.json](current-closure-bounded-start.json) |
| boot-analysis | `python3 -B local/research/E17/e17_bounded.py boot-analysis 300 -- python3 -B local/research/E17/e17_analyze.py`; [boot-analysis-bounded-start.json](boot-analysis-bounded-start.json) |
| retention | `python3 -B local/research/E17/e17_bounded.py retention 300 -- python3 -B local/research/E17/e17_retain.py a`; [retention-bounded-start.json](retention-bounded-start.json) |
| canonical-replay | `python3 -B local/research/E17/e17_bounded.py canonical-replay 300 -- python3 -B local/research/E17/e17_replay.py`; [canonical-replay-bounded-start.json](canonical-replay-bounded-start.json) |
| fork-map-commit | `python3 -B local/research/E17/e17_bounded.py fork-map-commit 600 -- python3 -B local/research/E17/e17_commit_fork.py`; [fork-map-commit-bounded-start.json](fork-map-commit-bounded-start.json) |
| Title boot (once) | `python3 -B local/research/E17/e17_capture.py a --report-all --wall 90`; exact child argv,cwd,environment/caps in [e17a-config.json](e17a-config.json) |
| Closed capture | `python3 -B local/research/E17/e17_close_capture.py`; [e17a-closed-caps.json](e17a-closed-caps.json) |
| Actual non-title linker commands | [before-fixture-link.json](before-fixture-link.json), [after-fixture-link.json](after-fixture-link.json); alternate entry and current runner objects, no synthetic binding implementation |
| Source audits | `python3 -B local/research/E17/e17_source_audit.py installed` / `regressed` / `precommit` / `final`; corresponding source-audit JSON receipts |
| Alias source / dispatch audit | `python3 -B local/research/E17/e17_alias_audit.py`; [function-owner-alias-source.json](function-owner-alias-source.json), [function-owner-alias-audit.json](function-owner-alias-audit.json) |
| Final audit | `E17_CANONICAL_ONLY=1 python3 -B local/research/E17/e17_final_audit.py`; [final-audit.json](final-audit.json) |
| Fork staging/commit/push | Exact argv/stdout/stderr in [fork-commit-commands.json](fork-commit-commands.json); message in [fork-commit-message.txt](fork-commit-message.txt) |
| Evidence staging | `python3 -B local/research/E17/e17_stage.py`; named path `git add -f -- local/research/E17`; [staging-receipt.json](staging-receipt.json) |
| Evidence hygiene | `python3 -B local/research/E17/e17_hygiene.py`; complete document tails and hash inventory |
| Evidence commit | `git commit -F local/research/E17/evidence-commit-message.txt`; no main ssx3 push |

**E17 COMMANDS TAIL COMPLETE — argv arrays retain exact quoting, cwd, environment and stdout/stderr receipts.**
