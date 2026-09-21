# E11 executed commands and replay boundary

Commands below ran from `/Users/bradrichardson/dev/ssx3` unless recorded
otherwise. Every SSD step used `export COPYFILE_DISABLE=1`. JSON receipts
preserve full argv, cwd, timestamps, input hashes and outputs; the generation,
build, fixture and boot commands below are historical, not a replay request.

## Checkpoint and reclamation

```sh
git pull --ff-only
python3 -B local/research/E11/e11_manifest.py before
/tmp/p1-link/runtime/ps2xTest/ps2x_tests
'/Volumes/Extreme SSD/ps2recomp-spike/P1/e10-binding-tests/drop/binding-test' absent
'/Volumes/Extreme SSD/ps2recomp-spike/P1/e10-binding-tests/drop/binding-test' present
/opt/homebrew/bin/herdr api snapshot
/opt/homebrew/bin/herdr pane list
```

The last fixture command was the required expected-present fail-before (rc1).
Per-tree `reclaim-*-proof.json` / `-removal.json` record exact board and
`/usr/sbin/lsof -nP +D /private/tmp/<tree>` argv, repeated before removal.
`e11_reclaim.py` enforced oldest-first, protected paths, ownership, fresh
admission/target and exact owned-tree removal. P10 was removed before edit;
P11 then P12 restored headroom after the subsequent build-time space dip.
No pane messages were sent. The board/pane reads were read-only.

```sh
python3 -B local/research/E11/e11_reclaim.py probe p10-link
python3 -B local/research/E11/e11_reclaim.py remove p10-link
```

The later build-time reclamation used the same two commands for `p11-link`,
then `p12-link`, in that order, each with its own persisted proof and recheck.

## Mutation / generation / build / test

```sh
python3 -B local/research/E11/e11_static.py dis 0x2c5140 0x2c5168
python3 -B local/research/E11/e11_add_entry.py
python3 -B local/research/E11/e11_generate.py entry
python3 -B local/research/E11/e11_install.py entry
python3 -B local/research/E11/e11_observe.py
cmake --build /tmp/p1-link/runtime --target ps2EntryRunner ps2x_tests -j4
/tmp/p1-link/runtime/ps2xTest/ps2x_tests
python3 -B local/research/E11/e11_link_test.py entry
```

Generator argv was the pinned
`/Volumes/Extreme SSD/ps2x-i10/host-recomp/ps2xRecomp/ps2_recomp`
with absolute `local/research/E11/entry-used.toml`, cwd the fork. The derived
config changed only `general.output` to the owned APFS scratch. Exact fixture
link command and object list are in `entry-binding-link.json`; actual fixture
argv is in `entry-binding-results.json`. Cleanup used content-hash equality
against every installed emitted file before removing the owned scratch;
`scratch-cleanup.json` retains those copies and both df samples.

Fork cwd `/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp`:

```sh
git add -- games/ssx3/ssx3-functions.sweep.csv ps2xRuntime/include/ps2_e7.h ps2xRuntime/src/lib/ps2_runtime.cpp
git commit -m 'SSX3: restore the exact card busy-query entry'
git push fork HEAD:ssx3
```

Generated sources were never staged. Push receipt confirms
`be0c9ee..ffdf58c HEAD -> ssx3` at the fork URL. Existing AppleDouble pack-index
warnings were recorded; commands returned success. Unrelated `.git` metadata
was not cleaned.

## One boot and closed-capture handling

```sh
python3 -B local/research/E11/e11_capture.py a --report-all --arm 600 --wall 90
python3 -B local/research/E11/e11_close_capture.py
python3 -B local/research/E11/e11_retain.py a
python3 -B local/research/E11/e11_manifest.py after
```

`e11_capture.py` owns the atomic lease, repeats suite/selftest/pre-claim checks,
runs the foreground process, samples caps, sends SIGTERM at the first guard,
waits for exit and releases immediately. It refuses a second E11 result file.
`e11a-config.json` is the exact runner argv/env/cwd; `e11a-result.json` is the
signal/exit/release receipt. A sandboxed post-run process query returned rc3
(`sysmond` unavailable); the permitted host query was rerun and returned rc1
before retention. It did not trigger another boot or change any cap.

## Safe read-only reproduction from retained captures

```sh
python3 -B local/research/E11/e11_mine.py a
python3 -B local/research/E11/e11_card.py a
python3 -B local/research/E11/e11_frame.py a
python3 -B local/research/E11/e11_progress.py a
python3 -B local/research/E11/e11_join.py
```

All five were rerun after retention, using `e11_io.py` and the canonical
capture manifest. They write only analysis outputs under E11. `e11_frame.py`
deliberately retains the original uniform-offset comparison (two differences);
`e11_join.py` supersedes it with the packet's full per-sprite calculation.

Static residual commands (ELF reads only):

```sh
python3 -B local/research/E11/e11_static.py dis 0x2c5300 0x2c53b0
python3 -B local/research/E11/e11_static.py dis 0x242078 0x242270
python3 -B local/research/E11/e11_static.py dis 0x2d37d0 0x2d3890
python3 -B local/research/E11/e11_static.py words 0x4870f8 0x487178
```

Runtime sampling, missing-call policy and card API excerpts are retained in
`runtime-source-receipts.txt`; complete relevant generated owner/caller bytes
are compressed with their hashes in `residual-source-manifest.json`.

Evidence is force-added only under `local/research/E11/`, committed with
`[E11]` and `Orchestrated-By: Muse Code`. No ssx3 push. No adb. No further
regeneration, build or boot after scope closure.

**E11 COMMANDS TAIL COMPLETE.**
