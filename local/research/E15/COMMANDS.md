# E15 exact execution and replay commands

Paths below are literal argv, quoted for zsh. All SSD steps used `export COPYFILE_DISABLE=1`. The capture driver enforces the already-spent one-boot limit; these are historical commands, not new authorization.

## Checkpoint and source work

```sh
cd /Users/bradrichardson/dev/ssx3
git pull --ff-only
export COPYFILE_DISABLE=1
python3 local/research/E15/e15_manifest.py before
python3 local/research/E15/e15_checkpoint.py
python3 local/research/E15/e15_install_taps.py
python3 local/research/E15/e15_source_audit.py
```

The retained checkpoint/install/static scripts and `before/manifest.json` pin inputs. The installer applies observation-only named-file edits; the final Present/label changes are also pinned in `observation-tracked.diff` and `sources/*.gz`.

## Bounded build and fixture invocations

The following command lines are reconstructed exactly from their persisted argv and caps; results and stdout are in the matching `*-bounded-result.json` and logs. Failed attempts are retained.

`2026-09-21T12:56:37.961391+00:00` — `configure-bounded-start.json`

```sh
python3 local/research/E15/e15_bounded.py configure 1800 -- cmake -S '/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp' -B /tmp/p1-link/runtime
```

`2026-09-21T12:57:22.466527+00:00` — `build-bounded-start.json`

```sh
python3 local/research/E15/e15_bounded.py build 1800 -- ninja -C /tmp/p1-link/runtime -j2 ps2EntryRunner ps2x_tests
```

`2026-09-21T13:01:20.095469+00:00` — `build-retry-bounded-start.json`

```sh
python3 local/research/E15/e15_bounded.py build-retry 1800 -- ninja -C /tmp/p1-link/runtime -j2 ps2EntryRunner ps2x_tests
```

`2026-09-21T13:04:15.113907+00:00` — `fixture-link-bounded-start.json`

```sh
python3 local/research/E15/e15_bounded.py fixture-link 1200 -- python3 local/research/E15/e15_link_test.py entry
```

`2026-09-21T13:04:50.672602+00:00` — `fixture-link-retry-bounded-start.json`

```sh
python3 local/research/E15/e15_bounded.py fixture-link-retry 1200 -- python3 local/research/E15/e15_link_test.py entry
```

`2026-09-21T13:08:34.119856+00:00` — `preliminary-tests-bounded-start.json`

```sh
python3 local/research/E15/e15_bounded.py preliminary-tests 300 -- python3 local/research/E15/e15_validate.py preliminary
```

`2026-09-21T13:09:39.502000+00:00` — `build-aligned-upload-bounded-start.json`

```sh
python3 local/research/E15/e15_bounded.py build-aligned-upload 1800 -- ninja -C /tmp/p1-link/runtime -j2 ps2EntryRunner ps2x_tests
```

`2026-09-21T13:13:21.650032+00:00` — `fixture-final-link-bounded-start.json`

```sh
python3 local/research/E15/e15_bounded.py fixture-final-link 1200 -- python3 local/research/E15/e15_link_test.py entry
```

`2026-09-21T13:18:14.938920+00:00` — `actual-wrapper-tests-bounded-start.json`

```sh
python3 local/research/E15/e15_bounded.py actual-wrapper-tests 300 -- python3 local/research/E15/e15_validate.py actual
```

`2026-09-21T13:20:19.818091+00:00` — `suite-apfs-check-bounded-start.json`

```sh
python3 local/research/E15/e15_bounded.py suite-apfs-check 300 -- python3 local/research/E15/e15_suite.py apfs-control
```

`2026-09-21T13:21:24.923086+00:00` — `build-final-bounded-start.json`

```sh
python3 local/research/E15/e15_bounded.py build-final 1800 -- ninja -C /tmp/p1-link/runtime -j2 ps2EntryRunner ps2x_tests
```

`2026-09-21T13:25:52.339535+00:00` — `fixture-complete-link-bounded-start.json`

```sh
python3 local/research/E15/e15_bounded.py fixture-complete-link 1200 -- python3 local/research/E15/e15_link_test.py entry
```

`2026-09-21T13:30:11.785554+00:00` — `final-validation-bounded-start.json`

```sh
python3 local/research/E15/e15_bounded.py final-validation 300 -- python3 local/research/E15/e15_validate.py final
```

`2026-09-21T13:43:26.971563+00:00` — `retention-bounded-start.json`

```sh
python3 local/research/E15/e15_bounded.py retention 120 -- python3 local/research/E15/e15_retain.py a
```

## Single historical capture

```sh
export COPYFILE_DISABLE=1
python3 local/research/E15/e15_capture.py a --report-all --wall 90
```

Actual child argv, cwd `/Volumes/Extreme SSD/ps2recomp-spike/P1/run`:

```sh
stdbuf -o0 -e0 /tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner '/Volumes/Extreme SSD/ps2recomp-spike/P1/cd/SLUS_207.72'
```

The driver cleared inherited PS2X variables and set exactly:

```sh
export PS2X_CD_IMAGE='/Volumes/Extreme SSD/ps2recomp-spike/SSX 3 (USA).iso'
export PS2X_DIAG_PARK=1
export PS2X_DIAG_PARK_DIR='/Volumes/Extreme SSD/ps2recomp-spike/P1/run/park-e15a-1'
export PS2X_DIAG_PERIOD_MS=5000
export PS2X_DIAG_REPORT_ALL=1
export PS2X_DIAG_WATCH=0x4a289c,0x12000000,0x12000020,0x12000070,0x12000080,0x12000090,0x120000a0,0x120000e0,0x6214d8,0x6214dc,0x6214e4,0x6214e8,0x6214d4,0x61c9a4,0x621448,0x10005000,0x1000a000,0x1000a010,0x1000a020,0xb851a0,0xb851a4,0xb851ac,0xb851e0,0xb84e84,0xb84d88,0x4a3938,0x4a393c,0x4a3940,0x4a3944
export PS2X_E15_ALIGN=1
export PS2X_E15_TRACE=1
export PS2X_E4_DIR='/Volumes/Extreme SSD/ps2recomp-spike/P1/run/e15a-1'
export PS2X_E7_DIR='/Volumes/Extreme SSD/ps2recomp-spike/P1/run/e15a-join'
export PS2X_FRAME_DUMP_DIR='/Volumes/Extreme SSD/ps2recomp-spike/P1/run/frames-e15a-1'
export PS2X_TRACE_SYSCALLS='/Volumes/Extreme SSD/ps2recomp-spike/P1/run/syscalls-e15a-on.txt'
export PS2X_TRACE_SYSCALLS_PC=1
```

No PS2X_E4_ARM_TICK/FREEZE_TICK environment was set; the UI guard supplies arm/freeze. Candidate absolute WATCH addresses are guarded by same-run singleton/constructor/UI tap receipts.

## Closed capture retention and replay

```sh
export COPYFILE_DISABLE=1
python3 local/research/E15/e15_close_capture.py
python3 local/research/E15/e15_retain.py a
python3 local/research/E15/e15_retention_audit.py
python3 local/research/E15/e15_exit_audit.py
python3 local/research/E15/e15_mine.py
python3 local/research/E15/e15_card.py a
python3 local/research/E15/e15_progress.py a
python3 local/research/E15/e15_final_audit.py
python3 local/research/E15/e15_source_audit.py
```

Retention ran within the bounded wrapper above. Its monitor hit the documented list/stat race after the retention manifest completed. The audit verified every canonical hash and cleaned only its own temporary. Retention/final-cleanup scripts are one-shot mutation records; replay the **join/card/progression/exit** miners against canonical retained files. Strict `e15_closed_events.tap(path)` still fails on the absent runtime footer; partial miners explicitly retain that gap.

## Commits

Fork commit and remote verification:

```sh
git -C '/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp' add -- ps2xRuntime/include/ps2_e4.h ps2xRuntime/include/ps2_e7.h ps2xRuntime/include/ps2_e15.h ps2xRuntime/src/lib/ps2_runtime.cpp ps2xRuntime/src/lib/Kernel/EeScheduler.cpp
git -C '/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp' commit -m 'Diagnostics: trace MPEG requests and align UI captures'
git -C '/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp' push fork HEAD:ssx3
git -C '/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp' ls-remote fork refs/heads/ssx3
```

Main evidence: force-add E15 files only, excluding Python cache; commit `[E15] Probe MPEG delivery and record shutdown closure gap` with trailer `Orchestrated-By: Muse Code`. No main push.

**E15 COMMANDS TAIL COMPLETE — exact argv/env, failures and replay limits retained.**
