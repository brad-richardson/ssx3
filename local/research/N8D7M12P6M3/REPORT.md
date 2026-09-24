# N8D7M12 Part 6M3 — prune excluded cache trees in source snapshot (worker receipt)

Worker receipt. Owns only `local/tooling/orch/source_manifest.py`,
`local/research/N8D7M12P6M2/check.py` (fixture case added) and
`local/research/N8D7M12P6M3/`. Brief: `local/muse/prompts/N8D7M12P6M3.md`.
Prior: `local/research/N8D7M12P6M2/{REPORT.md,ORCH-GATE.md}`.
No board/ledger/fork/config edit, package, device, emulator, network, mini
lease or push. No binary/game bytes in receipts.

Gate finding (P6M2 ORCH-GATE): `scan_scope` skips excluded names, but
pre/post `list_tree` walked inside them — `list_tree` contained
`build/volatile.o`. A live cache change could falsely invalidate a manifest
and large build trees still cost a metadata walk.

## 1. Fix (minimal, in `list_tree` only)

`local/tooling/orch/source_manifest.py:106-147`: `list_tree` now filters
`dirnames` in place (pruning excluded dirs before descent, so `os.walk`
never enters them) and skips excluded filenames, using the existing
`is_excluded` rule on scope-relative POSIX paths. `followlinks=False`
unchanged (never follows symlinks); sorted-dirname/filename ordering
unchanged; manifest entry and aggregate behavior unchanged. No other
function touched.

Reproduced the gate demo after the fix: temp root with `build/volatile.o`
+ `keep.txt` → `list_tree` returns `['keep.txt']` only (`prune-ok`).

## 2. Fixture (`check.py` 16/16, verdict A)

Exact command from `~/dev/ssx3`:

```sh
python3 local/research/N8D7M12P6M2/check.py   # temp four-root fixture, drives the CLI, writes check-result.json
```

All 13 pre-existing cases still pass unchanged; 3 new P6M3 cases:

| Case | Result |
| --- | --- |
| `list_tree_omits_excluded` — `list_tree` on fixture fork omits every excluded-component path | pass, `leaked=[] keys=8`, `build/ignored.o` absent, `README.md` present |
| `excluded_race_does_not_fail` — excluded `fork/build/ignored.o` mutated inside an included file's two-read phase; `build_manifest` still succeeds | pass, `aggregate=27aeddc223b1333e` (same prefix as the P6M2 fixture aggregate `27aeddc2…`, entry/aggregate behavior unchanged) |
| `included_race_still_fails` — included `fork:ps2xRuntime/src/lib/gs/gs_frontend.cpp` mutated while `README.md` is read (two reads consistent, pre/post differs); snapshot fails | pass, `SnapshotError: source root changed during snapshot … changed=['ps2xRuntime/src/lib/gs/gs_frontend.cpp']` |

The included-race case discriminates the exact mechanism: failure comes
from the pre/post lstat comparison naming the file, not from a two-read
mismatch. Full row list in `check-result.json` (this dir): 16 rows,
`"verdict": "A"`, `"failing": []`.

## 3. Bounded read-only real-source sample

Four small existing source directories (not the full fork/codegen trees),
explicit caps `--max-files 500 --max-bytes 50000000`:

```sh
python3 local/tooling/orch/source_manifest.py snapshot --fork local/tooling/ee --parallel tools/macos --codegen tools/course_presets --jni native/diagnostics --out local/research/N8D7M12P6M3/sample-manifest.json --max-files 500 --max-bytes 50000000
python3 local/tooling/orch/source_manifest.py verify --manifest local/research/N8D7M12P6M3/sample-manifest.json --fork local/tooling/ee --parallel tools/macos --codegen tools/course_presets --jni native/diagnostics --max-files 500 --max-bytes 50000000
```

| Scope | Path | Files | Bytes |
| --- | --- | --- | --- |
| fork | `local/tooling/ee` | 6 | 13784 |
| parallel | `tools/macos` | 8 | 12728 |
| codegen | `tools/course_presets` | 2 | 3199 |
| jni | `native/diagnostics` | 25 | 158777 |
| total | | 41 | 188488 |

Snapshot `status: ok`, verify `status: match`, rc=0 both.
Aggregate `029bec991f9e32b962ed84267e52205ffd485d01cb32f2fdd89cf51305fdf83e`
(snapshot and verify agree). Exclusions live-proven: `fork:__pycache__`
skipped (per-scope skips 1/0/0/0). No caps hit, no runner hits (sample
roots contain no `ps2xRuntime/src/runner/`).

## 4. Receipts

- `local/tooling/orch/source_manifest.py` (sha256 `7bd6b501…a192ece`, pre-commit; see commit for final)
- `local/research/N8D7M12P6M2/check.py` (sha256 `a15bcdd6…b1c4ea`, pre-commit; see commit for final)
- `local/research/N8D7M12P6M3/{REPORT.md,check-result.json,sample-manifest.json}` (~12 KiB total, under the 128 KiB cap)
- Base commit `3ecea522` (`[orch] Queue source snapshot cache exclusion fix`)

## 5. Gaps (hand-back, no package/GPU verdict)

1. Full fork/codegen roots still never scanned with this tool; wall-time on
   a codegen-scale tree (~9.5k files) remains unmeasured (carried from P6M2
   gap 1). Whether full-root use is ready is the orchestrator's call.
2. The race cases use an in-process `read_file_twice` wrapper that mutates
   a second file mid-scan — deterministic, but not a live racing writer
   thread/process; a change that lands and fully reverts between the two
   `list_tree` calls would still rest on the per-file double-read (P6M2
   gap 2, unchanged).
3. Symlink-through-excluded-dir edge (e.g. a symlink named `build` pointing
   out): `is_excluded` matches the link's own rel path, so it is omitted
   like any excluded name; not separately fixture-proven.
4. P6M2 `local/research/N8D7M12P6M2/check-result.json` was rewritten as a
   side effect of rerunning the checker; reverted before commit so the
   commit holds only allowed paths — the canonical P6M3 result is
   `local/research/N8D7M12P6M3/check-result.json`.
