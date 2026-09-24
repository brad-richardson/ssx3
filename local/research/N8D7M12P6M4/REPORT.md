# N8D7M12 Part 6M4 — permit the exact upstream runner stub (worker receipt)

Worker receipt. Owns only `local/tooling/orch/source_manifest.py`,
`local/research/N8D7M12P6M2/check.py` and `local/research/N8D7M12P6M4/`
REPORT/check result. Brief: `local/muse/prompts/N8D7M12P6M4.md`.
Prior: `local/research/N8D7M12P6M3/{REPORT.md,ORCH-GATE.md}`.
No board/ledger/fork/config edit, package, device, emulator, network, mini
lease or push. No binary/game bytes in receipts.

Gate correction (P6M3 ORCH-GATE): the blanket `ps2xRuntime/src/runner/`
rejection cannot work on the real fork. The private fork
`/Users/brad/dev/ssx3-work/N8D7M12P5F4/PS2Recomp` tracks exactly one
upstream file there, `ps2xRuntime/src/runner/register_functions.cpp`
(438 B, SHA-256 `cf62c485072f07c230e60296b77afd733f130f587955fe608322939ebb87f068`;
`git ls-tree -r 14b1e5cb` and HEAD both name blob
`85cc2e348d60cfae0a4f220fc2a0535f7a756fa2`; `git diff --stat 14b1e5cb
HEAD -- ps2xRuntime/src/runner/` empty; working tree has no tracked
modifications — only untracked `local/receipts`, 336 KiB). The project
forbids generated/changed in-tree runner files, not this exact stub.

## 1. Fix (in `source_manifest.py` only)

- New pins `RUNNER_STUB_PATH/_SIZE/_SHA256` (lines 56-58) and one shared
  `check_runner_entries(entries)` (lines 288-321): a fork entry at or
  under `ps2xRuntime/src/runner/` passes only if it is exactly the stub
  path as a regular file (`kind == "file"`) with exactly the pinned size
  and SHA-256; it then stays in the manifest and aggregate. Any other
  runner path fails as generated; a stub byte/kind change fails with an
  explicit `fork runner stub changed (expected …)` message. Git status is
  never consulted, so ignored/untracked generated files still fail.
- `build_manifest` and `rescan_for_verify` both call the shared function,
  replacing their duplicated inline blanket-rejection blocks. Docstring
  fatal-error rule updated to match.
- Code relationships confirmed via LSP on
  `local/tooling/orch/source_manifest.py`: `documentSymbol` lists
  `scan_scope`, `build_manifest`, `rescan_for_verify` as distinct
  functions; `findReferences` on `scan_scope` returns exactly the
  definition plus the two call sites inside `build_manifest` and
  `rescan_for_verify` — the two places the shared gate now sits
  (current lines per `rg`: `scan_scope` def 156,
  `check_runner_entries` def 288, `build_manifest` def 324,
  `rescan_for_verify` def 392, `scan_scope` calls at 330 and 401,
  `check_runner_entries` calls at 337 and 404).

## 2. Fixture (`check.py` 23/23, verdict A)

Exact command from `~/dev/ssx3`:

```sh
python3 local/research/N8D7M12P6M2/check.py   # temp four-root fixture, drives the CLI, writes check-result.json
```

All 16 pre-existing cases pass unchanged (P6M3 race rows reproduce the
same `27aeddc223b1333e` aggregate prefix; the P6M4 block runs after them
and removes its stub file, so their fixture bytes are untouched). 7 new
P6M4 rows:

| Case | Result |
| --- | --- |
| `runner_stub_bytes_match_pinned` — embedded 438 B fixture bytes hash to the pinned SHA | pass, `len=438 sha=cf62c485072f07c2` |
| `runner_stub_snapshot_passes` — exact stub snapshots; manifest holds it as `file`, 438 B, pinned SHA | pass |
| `runner_stub_verify_matches` — verify against the stub manifest | pass, `match`, rc=0 |
| `runner_extra_with_stub_snapshot_fails` — `gen.cpp` beside the exact stub fails snapshot | pass, rc=1, names `ps2xRuntime/src/runner` |
| `runner_extra_with_stub_verify_fails` — same tree fails verify | pass, rc=1 |
| `runner_stub_changed_snapshot_fails` — stub +1 line fails snapshot | pass, rc=1, `runner stub changed` |
| `runner_stub_changed_verify_fails` — changed stub fails verify | pass, rc=1, `runner stub changed` |

Full row list in `local/research/N8D7M12P6M4/check-result.json`: 23 rows,
`"verdict": "A"`, `"failing": []`. (`local/research/N8D7M12P6M2/check-result.json`
was rewritten as a rerun side effect and reverted before commit; the
canonical P6M4 result is the copy in this dir.)

## 3. Bounded real fork-only probe (read-only; fork NOT edited)

Real fork as `--fork`, three small existing repo dirs for the other
scopes, explicit caps `--max-files 5000 --max-bytes 500000000`. No full
codegen/renderer scan.

```sh
python3 local/tooling/orch/source_manifest.py snapshot --fork /Users/brad/dev/ssx3-work/N8D7M12P5F4/PS2Recomp --parallel tools/macos --codegen tools/course_presets --jni native/diagnostics --out local/research/N8D7M12P6M4/real-probe-manifest.json --max-files 5000 --max-bytes 500000000
python3 local/tooling/orch/source_manifest.py verify --manifest local/research/N8D7M12P6M4/real-probe-manifest.json --fork /Users/brad/dev/ssx3-work/N8D7M12P5F4/PS2Recomp --parallel tools/macos --codegen tools/course_presets --jni native/diagnostics --max-files 5000 --max-bytes 500000000
```

| Scope | Files | Bytes |
| --- | --- | --- |
| fork (real fork @ `4fa0df1`, status `?? local/` only) | 336 | 22634053 |
| parallel (`tools/macos`) | 8 | 12728 |
| codegen (`tools/course_presets`) | 2 | 3199 |
| jni (`native/diagnostics`) | 25 | 158777 |
| total (371 entries) | 371 | 22808757 |

Snapshot `status: ok`, verify `status: match`, rc=0 both.
Aggregate `70a31d1df4f4fecc467b4a09093a192242fc9b467cccf957780a05eb498331e4`
(snapshot and verify agree). Runner entry in the manifest: exactly one
under `ps2xRuntime/src/runner/` —
`fork:ps2xRuntime/src/runner/register_functions.cpp`, `file`, 438 B,
`cf62c485…f068` (matches the pin). (`fork:ps2xRecomp/src/runner/main.cpp`
is a different prefix and correctly ungated.) Fork exclusion: `.git`
skipped (per-scope skips 1/0/0/0). No caps hit. The probe manifest stays
private and uncommitted under ignored `local/research/N8D7M12P6M4/`.

## 4. Receipts

- `local/tooling/orch/source_manifest.py`
- `local/research/N8D7M12P6M2/check.py`
- `local/research/N8D7M12P6M4/{REPORT.md,check-result.json}` (~7 KiB
  committed, under the 128 KiB cap; `real-probe-manifest.json` ~90 KiB
  stays private/uncommitted)
- Base commit `230d7d3f` (`[orch] Correct source collector readiness and
  queue runner stub fix`)

## 5. Gaps (hand-back, no package/GPU/APK verdict)

1. Full codegen/renderer roots still never scanned with this tool;
   wall-time on a codegen-scale tree (~9.5k files) remains unmeasured
   (carried from P6M3 gap 1). Whether full-root use is ready is the
   orchestrator's call.
2. Fixture stub bytes are embedded in `check.py` rather than read from
   the fork; if upstream ever changes the stub, the pin and the embedded
   bytes must be updated together (the `runner_stub_bytes_match_pinned`
   row asserts they agree, so drift fails loudly, not silently).
3. The real-probe fork root contains untracked `local/receipts` (336 KiB,
   P5F4 lane files); their bytes are inside the private probe manifest.
   A package manifest must decide whether that dir belongs in the build
   inputs or must be removed first.
4. Symlink-at-stub-path edge (a symlink instead of the regular file) is
   rejected by the `kind == "file"` rule but has no dedicated fixture
   row — only the changed-bytes and extra-file rows.
