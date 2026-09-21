# E18 exact-command index

| Working directory / environment | Value |
|---|---|
| Root | `/Users/bradrichardson/dev/ssx3` |
| SSD operations | `export COPYFILE_DISABLE=1` |
| Default E18 build | `/tmp/e18-mpeg-link/runtime` |
| Baseline override | `E18_BUILD_DIR=/tmp/e17-map-link/runtime` |
| Bounded child | `CMAKE_BUILD_PARALLEL_LEVEL=2`; exact TMPDIR, argv, cwd, caps in each `*-bounded-start.json` |

| Step | Exact command / structured receipt |
|---|---|
| Opening git | `opening-git.json` retains git HEAD/tracking/ls-remote commands and results |
| Checkpoint | `python3 local/research/E18/e18_checkpoint.py` |
| Baseline suite | `E18_BUILD_DIR=/tmp/e17-map-link/runtime python3 local/research/E18/e18_bounded.py baseline-suite 300 -- python3 -B local/research/E18/e18_validate.py baseline suite` |
| Baseline closure / prior | Exact argv in `baseline-closure-bounded-start.json` and `baseline-prior-bounded-start.json`; binary reused from SSD E17 |
| Ownership fixture link | Exact compile/link argv in `before-fixture-link.json`; bounded wrapper `ownership-link-bounded-start.json` |
| Ownership execution | Binary modes `ownership-queued-ready`, `ownership-queued-park`, `ownership-current`; exact argv/cwd in `ownership-dynamic.json` |
| MPEG mutation | `python3 local/research/E18/e18_edit_mpeg.py`; single-use baseline-hash guard |
| Tests mutation | `python3 local/research/E18/e18_edit_tests.py`; single-use baseline-byte guard |
| Scope | `python3 local/research/E18/e18_scope.py before-build` (initial helper allowlist corrected); then `after-sidecars`, `after-build` |
| Configure | `python3 local/research/E18/e18_bounded.py configure 1800 -- python3 local/research/E18/e18_configure.py`; exact CMake argv in `configure-command.json` |
| Initial build | `python3 local/research/E18/e18_bounded.py build 7200 -- ninja -C /tmp/e18-mpeg-link/runtime -j2 ps2EntryRunner ps2x_tests` (AppleDouble input/stdout cap) |
| Metadata retention | `python3 local/research/E18/e18_retain_sidecars.py`; two hash-checked owned renames, no deletion |
| Source-only build | `python3 local/research/E18/e18_bounded.py build-source-only 7200 -- ninja -C /tmp/e18-mpeg-link/runtime -j2 ps2EntryRunner ps2x_tests` |
| Postbuild audit | `python3 local/research/E18/e18_after_build.py` |
| Full regression suite | `python3 local/research/E18/e18_bounded.py current-suite 180 -- python3 local/research/E18/e18_validate.py current suite` |
| Actual current-object link | `python3 local/research/E18/e18_bounded.py current-fixture-link 1200 -- python3 local/research/E18/e18_link_test.py after`; exact compile/link in `after-fixture-link.json` |
| Authored MPEG fixture | Exact FFmpeg command and independent decode hash in `regression-frame-provenance.json` |



| Later step | Exact command / receipt |
|---|---|
| current-binding | `python3 local/research/E18/e18_validate.py current-binding '/Volumes/Extreme SSD/ps2recomp-spike/P1/e18-fixtures/after/binding-test' prior`; bounded wall 300s |
| current-closure | `python3 local/research/E18/e18_validate.py current-closure '/Volumes/Extreme SSD/ps2recomp-spike/P1/e18-fixtures/after/binding-test' closure`; bounded wall 300s |
| current-extra | `python3 local/research/E18/e18_extra.py`; bounded wall 300s |
| boot-analysis | `python3 local/research/E18/e18_analyze.py`; bounded wall 300s |
| retention | `python3 local/research/E18/e18_retain.py a`; bounded wall 300s |
| Prepare probe | `python3 local/research/E18/e18_prepare_probe.py` |
| Single probe | `python3 local/research/E18/e18_capture.py a --report-all --wall 90` |
| Closed caps | `python3 local/research/E18/e18_close_capture.py` |
| Handoff receipt | `python3 local/research/E18/e18_handoff_receipt.py` |
| Fork commit/push | `python3 local/research/E18/e18_commit_fork.py` |
| Standalone verify | `python3 local/research/E18/e18_verify_retained.py` |
| Canonical analysis | `E18_CANONICAL_ONLY=1 python3 local/research/E18/e18_analyze.py` |
| Final audit | `python3 local/research/E18/e18_final_audit.py` |

| Authoritative argv storage | Content |
|---|---|
| `commands-all-bounded.json` | Every bounded child argv, cwd, UTC, TMPDIR and wall cap |
| `fork-commit-commands.json` | Every named-file add, staged check, commit, fork push and ls-remote command with rc/stdout/stderr |
| `e18a-config.json` / `e18a-preflight.json` | Exact title argv/environment, all fresh T13 commands and lease/cap checks |

**E18 COMMAND INDEX TAIL COMPLETE.**
