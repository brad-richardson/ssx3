# E14 executed command record

Workspace `/Users/bradrichardson/dev/ssx3`. Every SSD step exported
`COPYFILE_DISABLE=1`. These are completed commands, not instructions to
rerun destructive steps.

| Phase | Command / complete receipt |
|---|---|
| Update | `git pull --ff-only` → already current; E14 brief read in full, E13 REPORT read in full, E13 cross-check and I11–I15 row tables read |
| Snapshot | `python3 -B local/research/E14/e14_manifest.py before` → `before-manifest.log`, complete `before/` manifests/configs/bindings |
| Checkpoint | `python3 -B local/research/E14/e14_checkpoint.py` → `checkpoint-driver.txt`; complete suite and prior fixture argv/return codes in `checkpoint.json`, raw outputs in `checkpoint-suite.txt` and `checkpoint-prior-binding.txt` |
| New baseline fixture | `python3 -B local/research/E14/e14_bounded.py baseline-link 1200 -- python3 -B local/research/E14/e14_link_test.py baseline` → complete compiler/linker/object argv in `baseline-binding-link.json`; start/result/liveness and raw log retained |
| Row verification | `python3 -B local/research/E14/e14_rows.py` → `row-verification.json/.txt`; raw guest bytes and pinned baseline/I-lane sources in `row-sources/` |
| Five fail-befores | `python3 -B local/research/E14/e14_fail_before.py` → `fail-before-driver.txt`; for each PC, actual fixture `check-absent PC` rc0 followed by `check-present PC` rc1, exact argv in `baseline-binding-results.json`; ten complete logs retained |
| Fresh admission | After fail-befores, Python `shutil.disk_usage('/private/tmp').free`; 3,489,660,928 B admission and 4,026,531,840 B headroom target persisted in `admission-before-edit-initial.json`. Inventory uses `/private/tmp/*-link` lstat/stat ownership and birth time |
| Lane board | `herdr api snapshot` → `board-snapshot.json`; completed T12 gate excerpt in `retired-lane-receipts.txt` |
| Ownership proof | `python3 -B local/research/E14/e14_reclaim.py probe t12-dev-link` → full board/cache/size/handle proof JSON; `lsof -nP +D /private/tmp/t12-dev-link` rc1, empty stdout/stderr |
| Scoped reclaim | `python3 -B local/research/E14/e14_reclaim.py remove t12-dev-link` → fresh board/handle recheck, before/after df, single-tree removal receipt |
| Admission stop | Fresh `shutil.disk_usage` plus `df -k /private/tmp '/Volumes/Extreme SSD/ps2recomp-spike'` → `admission-after-reclamation.json`, then `stop.json`; no CSV mutation or generator spawn |
| Final identity | `python3 -B local/research/E14/e14_manifest.py after`; exact before/after parsed manifest and full generated-list equality, `pgrep -x ps2EntryRunner`, fork status/staged check and df → `closeout.json` |
| Standalone replay | `python3 -B local/research/E14/e14_verify_retained.py` → `retained-verification.txt`; all five raw/owner/exact-entry/bound checks pass using only retained E14 files |
| Retention | `python3 -B local/research/E14/e14_pack_evidence.py` → `retention.txt`, 23 hash-verified compression/local-alias dispositions |

The baseline fixture is
`/Volumes/Extreme SSD/ps2recomp-spike/P1/e14-binding-tests/baseline/binding-test`.
The prior full fixture is E13's unchanged
`e13-binding-tests/entry/binding-test present`; its hash is in
`checkpoint.json`. These fixtures do not boot an ELF.

Read-only byte verification can be repeated against this unchanged checkpoint:

```sh
export COPYFILE_DISABLE=1
python3 -B local/research/E14/e14_rows.py
```

Do not rerun the reclamation driver on a removed path. No generation,
installation, build, fork commit/push or boot command was executed. The only
link was the fresh baseline presence fixture.

Evidence staging: `git add -f -- local/research/E14`; `[E14]` commit with
`Orchestrated-By: Muse Code`. No main push.

**E14 COMMANDS TAIL COMPLETE — complete long argv and raw outputs retained.**
