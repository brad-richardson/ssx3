# E16 exact commands and retained execution records

| Context | Value |
|---|---|
| Workspace | `/Users/bradrichardson/dev/ssx3` |
| SSD environment | `export COPYFILE_DISABLE=1`; wrapper assigns the per-tool SSD `TMPDIR` recorded in each start receipt |
| Scope | Historical command ledger; the E16 boot marker is spent. Replaying analysis does not authorize another title boot |
| Shell representation | Arguments below use Python `shlex.join`; exact structured argv, cwd, environment, and result are retained in linked JSON |

| Phase | Exact wrapper command | Result receipt |
|---|---|---|
| configure | `python3 -B local/research/E16/e16_bounded.py configure 1800 -- cmake -S '/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp' -B /tmp/p1-link/runtime -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=/opt/homebrew/opt/llvm/bin/clang -DCMAKE_CXX_COMPILER=/opt/homebrew/opt/llvm/bin/clang++ -DCMAKE_OSX_ARCHITECTURES=arm64 -DPS2X_BUILD_STUDIO=OFF -DPS2X_BUILD_RUNTIME=ON -DPS2X_BUILD_TEST=ON -DPS2X_ENABLE_RUNTIME_LOGS=ON -DPS2X_ENABLE_AGRESSIVE_LOGS=ON -DPS2X_ENABLE_IOP_RPC_TRACE=ON -DPS2X_STRICT_RETURN_DIAGNOSTICS=OFF -DPS2X_ENABLE_FFMPEG=ON` | [configure-bounded-result.json](configure-bounded-result.json) |
| rebuild | `python3 -B local/research/E16/e16_bounded.py rebuild 7200 -- ninja -C /tmp/p1-link/runtime -j2 ps2EntryRunner ps2x_tests` | [rebuild-bounded-result.json](rebuild-bounded-result.json) |
| ssd-fixture-reuse | `python3 -B local/research/E16/e16_bounded.py ssd-fixture-reuse 300 -- python3 -B local/research/E16/e16_validate.py ssd-reuse '/Volumes/Extreme SSD/ps2recomp-spike/P1/e15-binding-tests/entry/binding-test' prior` | [ssd-fixture-reuse-bounded-result.json](ssd-fixture-reuse-bounded-result.json) |
| rebuilt-suite | `python3 -B local/research/E16/e16_bounded.py rebuilt-suite 300 -- python3 -B local/research/E16/e16_validate.py rebuilt suite` | [rebuilt-suite-bounded-result.json](rebuilt-suite-bounded-result.json) |
| rebuilt-suite-cwd | `python3 -B local/research/E16/e16_bounded.py rebuilt-suite-cwd 300 -- python3 -B local/research/E16/e16_validate.py rebuilt-cwd suite` | [rebuilt-suite-cwd-bounded-result.json](rebuilt-suite-cwd-bounded-result.json) |
| fixture-before-link | `python3 -B local/research/E16/e16_bounded.py fixture-before-link 1200 -- python3 -B local/research/E16/e16_link_test.py before` | [fixture-before-link-bounded-result.json](fixture-before-link-bounded-result.json) |
| closure-fail-before | `python3 -B local/research/E16/e16_bounded.py closure-fail-before 300 -- python3 -B local/research/E16/e16_validate.py closure-before '/Volumes/Extreme SSD/ps2recomp-spike/P1/e16-fixtures/before/binding-test' before` | [closure-fail-before-bounded-result.json](closure-fail-before-bounded-result.json) |
| repair-build | `python3 -B local/research/E16/e16_bounded.py repair-build 1800 -- ninja -C /tmp/p1-link/runtime -j2 ps2EntryRunner ps2x_tests` | [repair-build-bounded-result.json](repair-build-bounded-result.json) |
| repaired-suite | `python3 -B local/research/E16/e16_bounded.py repaired-suite 300 -- python3 -B local/research/E16/e16_validate.py repaired suite` | [repaired-suite-bounded-result.json](repaired-suite-bounded-result.json) |
| fixture-after-link | `python3 -B local/research/E16/e16_bounded.py fixture-after-link 1200 -- python3 -B local/research/E16/e16_link_test.py after` | [fixture-after-link-bounded-result.json](fixture-after-link-bounded-result.json) |
| closure-pass-after | `python3 -B local/research/E16/e16_bounded.py closure-pass-after 300 -- python3 -B local/research/E16/e16_validate.py closure-after '/Volumes/Extreme SSD/ps2recomp-spike/P1/e16-fixtures/after/binding-test' after` | [closure-pass-after-bounded-result.json](closure-pass-after-bounded-result.json) |
| current-binding-tests | `python3 -B local/research/E16/e16_bounded.py current-binding-tests 300 -- python3 -B local/research/E16/e16_validate.py current-binding '/Volumes/Extreme SSD/ps2recomp-spike/P1/e16-fixtures/after/binding-test' prior` | [current-binding-tests-bounded-result.json](current-binding-tests-bounded-result.json) |
| boot-join-analysis | `python3 -B local/research/E16/e16_bounded.py boot-join-analysis 300 -- python3 -B local/research/E16/e16_mine.py` | [boot-join-analysis-bounded-result.json](boot-join-analysis-bounded-result.json) |
| retention | `python3 -B local/research/E16/e16_bounded.py retention 300 -- python3 -B local/research/E16/e16_retain.py a` | [retention-bounded-result.json](retention-bounded-result.json) |
| canonical-replay | `E16_CANONICAL_ONLY=1 python3 -B local/research/E16/e16_bounded.py canonical-replay 300 -- python3 -B local/research/E16/e16_replay.py` | [canonical-replay-bounded-result.json](canonical-replay-bounded-result.json) |
| canonical-replay-final | `E16_CANONICAL_ONLY=1 python3 -B local/research/E16/e16_bounded.py canonical-replay-final 300 -- python3 -B local/research/E16/e16_replay.py` | [canonical-replay-final-bounded-result.json](canonical-replay-final-bounded-result.json) |

| Additional action | Exact command / complete receipt |
|---|---|
| Checkpoint identities | `python3 -B local/research/E16/e16_checkpoint.py before` and `python3 -B local/research/E16/e16_checkpoint.py final`; [before-fork.json](before-fork.json), [final-fork.json](final-fork.json) retain git argv/stdout including `ls-remote fork refs/heads/ssx3` |
| Repaired checkpoint | `python3 -B local/research/E16/e16_checkpoint.py repaired` |
| Actual fixture compile/link | [before-fixture-link.json](before-fixture-link.json), [after-fixture-link.json](after-fixture-link.json): exact compiler/PCH/define flags, all runner objects, original link argv, alternate `_e16_binding_main` entry, cwd, and source hashes |
| Individual fixture commands | [ssd-reuse-validation.json](ssd-reuse-validation.json), [closure-before-validation.json](closure-before-validation.json), [closure-after-validation.json](closure-after-validation.json), [current-binding-validation.json](current-binding-validation.json): exact case argv/cwd/environment/timeouts/results |
| Initial suite cwd adaptation | The first `rebuilt-suite` execution used APFS scratch cwd and failed the relative-header test; subsequent `rebuilt-suite-cwd` used fork cwd with APFS TMPDIR. Historical argv/cwd in [suite-cwd-gap.json](suite-cwd-gap.json) and suite JSON; current validator contains the corrected cwd |
| Dry-run build receipts | `ninja -C /tmp/p1-link/runtime -n -j2 ps2EntryRunner ps2x_tests`; [rebuild-dry-run.txt](rebuild-dry-run.txt), [repair-dry-run.txt](repair-dry-run.txt). Completed build logs and object hashes determine actual compilation scope |
| One-time handwritten repair | `python3 -B local/research/E16/e16_repair.py`; [repair.json](repair.json), [observation-repair.diff](observation-repair.diff). Do not rerun on the repaired source |
| Fork observation commit | `python3 -B local/research/E16/e16_commit_fork.py`; [fork-commit-commands.json](fork-commit-commands.json) retains exact named `git add -f`, commit with body file, and verification commands; [fork-commit-message.txt](fork-commit-message.txt) |
| Fresh probe preparation | `python3 -B local/research/E16/e16_prepare_probe.py`; [entry-preflight.json](entry-preflight.json), [e16a-build.json](e16a-build.json) |
| Single title probe, already spent | `python3 -B local/research/E16/e16_capture.py a --report-all --wall 90`; exact child argv/cwd/env in [e16a-config.json](e16a-config.json); preclaims, caps, lease, signal, and release in [e16a-preflight.json](e16a-preflight.json), [e16a-result.json](e16a-result.json) |
| Closed capture accounting | `python3 -B local/research/E16/e16_close_capture.py`; read-only process check retried elevated after default sandbox pgrep failed; [post-exit-process-check-retry.json](post-exit-process-check-retry.json) |
| Other initial miners | `python3 -B local/research/E16/e16_card.py a`; `python3 -B local/research/E16/e16_lifetime.py`; `python3 -B local/research/E16/e16_progress.py a`; `python3 -B local/research/E16/e16_alias_audit.py` |
| Canonical-only replay | `E16_CANONICAL_ONLY=1 python3 -B local/research/E16/e16_replay.py`; exact five subprocess commands in [canonical-replay.json](canonical-replay.json). Final replay adds registration/exit-identity assertions without changing the nine output hashes |
| Final source/capture/resource audit | `E16_CANONICAL_ONLY=1 python3 -B local/research/E16/e16_final_audit.py`; [final-audit.json](final-audit.json) |
| Authored-file and tail validation | `python3 -B local/research/E16/e16_stage.py`; `python3 -B local/research/E16/e16_hygiene.py`; staged scope, allocated growth, Python AST, authored whitespace, local links, report chunks, tail hashes, and inventory receipts |
| Evidence staging / commit | `git add -f -- local/research/E16`; `git diff --cached --name-only`; `git commit -F /private/tmp/e16-evidence-commit-message.txt`; exact prefix/trailer pinned in the final report. No push command is run |

**E16 COMMANDS TAIL COMPLETE — exact commands and full argv receipts retained; boot allowance spent.**
