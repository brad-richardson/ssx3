# RS2 — cached baselines + one shared boot driver

Worker: muse. Brief: `local/muse/prompts/RS2.md`. No push.

**Verdict: done. One shared driver, one seeded `a3efbfe` det baseline,
self-test `compare` → IDENTICAL.** 1 boot used (of ≤ 2), 0 builds,
store 165 MB (of 3 GB), no fork touch, text only in git, no `docs/` edit.

## Delivered (text only)

| File | What |
| --- | --- |
| `local/tooling/boot/ssx3_boot.py` | F5's driver promoted verbatim + `--out DIR` |
| `local/tooling/boot/baseline.py` | `put`/`get`/`list`/`compare`/`make` over `~/dev/ssx3-work/baselines/` |
| `local/tooling/boot/README.md` | 27-line lane how-to |
| `local/research/RS2/pins-a3efbfe-det.json` | Seed pins (F5 B1 control) |
| `local/research/RS2/REPORT.md` | This file |

`ssx3_boot.py` vs `f5_boot.py` (`diff`, F5's copy untouched): docstring
promotion note, `--out DIR` (default keeps F5's run dir), lease label
`F5-` → `boot-`, held-slot env `SSX3_HELD_SLOT` (falls back to
`F5_HELD_SLOT`). Boot semantics, caps, env and pins byte-identical.

Key shape: readable prefix + 8 hex of canonical pins JSON, e.g.
`a3efbfe-det-fr1r1-t2400-snd1-1x-a5f2f32d` (the brief's example is the
prefix half; the hash suffix disambiguates full pins).

## Seed: `a3efbfe-det-fr1r1-t2400-snd1-1x-a5f2f32d`

`put --runner F5/bin/runner-det --run F5/run/B1 --pins pins-a3efbfe-det.json
--extra-frames F5/run/B1b/frames`. B1b's frames stored as `b1b-*`
(B1b t2100 keep byte-identical to B1's `upload-latest.png`, confirmed `cmp`).

| Pin | Value |
| --- | --- |
| fork | `a3efbfe94663…` (= `fork/ssx3`) |
| codegen register / changed (`sub_003FE828…`) | `8ea8ed43…` / `89953ba2…` |
| vu1_images (sha256 of sorted `vu1gen.sha` lines) | `17335933…` |
| parallel_gs / granite | `19d93b2d…` / `166ba21a…` |
| build / route / stop / sound / backend | det / fr1r1 / t2400 / on / parallel |
| ssaa / hires / pipeline | 1 / 0 / 0 |
| iso / elf | `3c2f8eb1…` / `1b49d05c…` |
| dump_ticks / hash_every / coverage / vu1_stats | 1090,1800,2100 / 1 / 2400 / on |

Store layout (17 files + manifest): `runner` 162 MB (exec bit kept,
SHA `119389a7…` = F5 pin, two matching reads), `boot.log` 489 K,
`snd.log` 404 K, `result.json`, `trace.jsonl`, `frames/` 12 PNG/TXT
(B1's 6 + B1b's 6). Total 165 MB.

## Self-test: S1 re-boot → IDENTICAL

`ssx3_boot.py --mode det --backend parallel --runner F5/bin/runner-det
--label RS2-S1 --out ~/dev/ssx3-work/RS2/run/S1 --stop-tick 2400
--route fr1r1 --vu1-stats --dump-ticks 1090,1800,2100`:
bound=target, slot 1 (released after), 73.6 s wall, last_tick 2405
(B1: 2405), FATAL 0, same `[gs-path]` line.

`compare --key <seed> --cand …/RS2/run/S1` → rc=0:
`hash IDENTICAL ticks 1..2400 missing=0/0 first_diff=None`
(stored 2485 lines vs cand 2467: settle-overrun tails only, as in F5);
`snd/coverage: IDENTICAL` (coverage `targets=0 ids=0 pairs=4`;
snd guest `cycle=11846455777 ticks=3666 cid0=531 dmq=531 done=531`).

Fix during the run: the first compare said DIFFER on the snd line
because the host wall-clock `underruns=` counter differs run to run
(982432 vs 1506112) for guest-identical boots. `compare` now strips
`underruns/overflows` before the snd comparison (full lines still
printed). No extra boot needed — same S1 run re-compared green.

## Validation matrix (no extra boots)

| Check | Result |
| --- | --- |
| `get <key>` / `get --pins` | dir printed, rc=0, SHAs verified (runner ×2) |
| `get doesnotexist` | `MISSING doesnotexist`, rc=2 |
| `list` | 1 row + totals |
| `compare` vs 1-char-corrupted boot.log copy (`/tmp/rs2-neg`) | `first_diff=1500`, rc=1 |
| `make` with key present | `EXISTS …`, no boot, rc=0 |
| `make` boot-then-put path | NOT exercised (would spend boot 2 for a 2nd key); code path is `ssx3_boot.py` + `put`, both proven separately |

## Exact commands

```sh
cp local/research/F5/f5_boot.py local/tooling/boot/ssx3_boot.py  # + --out/label/held-slot edits
python3 local/tooling/boot/baseline.py put --runner ~/dev/ssx3-work/F5/bin/runner-det --run ~/dev/ssx3-work/F5/run/B1 --pins local/research/RS2/pins-a3efbfe-det.json --extra-frames ~/dev/ssx3-work/F5/run/B1b/frames
python3 local/tooling/boot/ssx3_boot.py --mode det --backend parallel --runner ~/dev/ssx3-work/F5/bin/runner-det --label RS2-S1 --out ~/dev/ssx3-work/RS2/run/S1 --stop-tick 2400 --route fr1r1 --vu1-stats --dump-ticks 1090,1800,2100
python3 local/tooling/boot/baseline.py compare --key a3efbfe-det-fr1r1-t2400-snd1-1x-a5f2f32d --cand ~/dev/ssx3-work/RS2/run/S1
```

## Proposed runbook / brief-template text (for `docs/`, not edited)

> Controls are cached: `local/tooling/boot/baseline.py get --pins PINS`
> prints the control dir (rc=2 `MISSING <key>` if absent). If missing,
> `make --pins PINS --runner R` boots it once (det, one mini slot), then
> the lane boots only its candidate with `local/tooling/boot/ssx3_boot.py
> --out CANDIR` and runs `compare --key KEY --cand CANDIR`. Never copy a
> boot driver into a lane dir. Pins files live next to the lane report;
> the runner binary stays in lane scratch or the baseline store, never git.

Brief template line: `Control: baseline key <K> (pins <path>);
if MISSING, make it first. Candidate: one ssx3_boot.py boot + compare.`

## Budgets and gaps

- Boots: 1 (S1, 74 s, slot 1, ≤600 s). Builds: 0. Fork: read-only
  (`rev-parse` only). Time ~40 min of the 2 h box.
- Disk: store 165 MB / 3 GB; RS2 scratch 2.2 MB; global mini
  139.5 → 142.0 / 200 GB (remainder is concurrent RS1/SS1 lanes, not mine).
- Gaps:
  - G1. `make`'s boot-then-put path untested end to end (no second key
    wanted on this brief); first real `make` on a new fork tip is the test.
  - G2. `vu1_images` set-hash convention (sha256 of sorted `.sha` lines)
    is RS2-defined; lanes must use the same command (`sort FILE | shasum`).
  - G3. Speed (non-det) baselines: `make` refuses them (exclusive lease);
    `put`/`compare` would still work if a lane boots one by hand.
  - G4. `compare --min-tick` defaults to the pins' `stop_tick`; overrun
    tails beyond it are ignored by design (F5's settle shape).

## Orchestrator gate (2026-09-25)

**Pass.** Re-ran `list` and `compare` myself: S1 → IDENTICAL (rc 0), and F5's B4 (4×+hi-res+pipelined)
→ IDENTICAL against the 1× key, as F5 found. Adopted the runbook text into `docs/orchestration.md`.
Follow-up (small, queued): `baseline.py pins --fork-wt … --build-flags …` that computes the pins JSON
(including the VU1 set hash, G2) so lanes never hand-write it; exercise `make` on the next fork tip (G1).
