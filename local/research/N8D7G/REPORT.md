# N8D7G worker receipt — pinned Mac OFF/ON capture replay

Verdict is the orchestrator's. Scripted acceptance result: **PASS** (24/24 checks). No Odin,
iOS, Android, build, source edit, or push was done. The two replays were executed once each;
neither was rerun after the checker fix.

## Commands run (from `/Users/brad/dev/ssx3`)

```sh
git -C ~/dev/ssx3-work/N8D7F/PS2Recomp rev-parse HEAD
python3 local/tooling/p_lane_lease.py status
python3 local/tooling/orch/run_n8d7g.py
python3 local/tooling/orch/check_n8d7g.py ~/dev/ssx3-work/N8D7F > local/research/N8D7G/result.json
```

`run_n8d7g.py` exited 0 (lease slot 1 claimed, both replays exit 0, lease released).
The final `check_n8d7g.py` exited 0 (`verdict: PASS`, `failed: []`).

## Source pins

| Item | Value |
| --- | --- |
| Private fork HEAD | `0678dd96e496a65bbb09af5467f17240ae2bbdc8` (expected `0678dd9`) |
| Binary `N8D7F/build/ps2xTest/ps2x_tests` | `66457eb47ac6c29a8ffca38795d88122fb1c03e4e19e4f55e977f716eb70a804` (2 reads match) |
| N8D4 stream `N8D4/n8d4.gs` | `38ace1a3e8e99e1d5d7d24e611dfa9cedd6e6d44a45c800223991401cd93f97d` (2 reads match) |
| Codegen `codegen-ssx3/register_functions.cpp` | `8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3` (2 reads match) |

All three pins are double-hashed by `run_n8d7g.py` and matched the expected values.

## Lease

`p_lane_lease.py status` before: `slot 1: free`, `slot 2: free`. `run_n8d7g.py` claimed
**slot 1** and set `lease_released: true`; status after is free.

## Runs (from `~/dev/ssx3-work/N8D7F/run-receipt.json`)

| Run | PID | Exit | Seconds | Log bytes | Log SHA-256 | Hashes SHA-256 |
| --- | --- | --- | --- | --- | --- | --- |
| OFF | 20268 | 0 | 6.02 | 4,805,696 | `3fa7d45e318416410ba3a29b9dad7beafff6e3373ab432999fab7a064e7b201c` | `f038cde992d13f868b06a7acf6cee922a3096345dda39f72761d5326f67fcdfb` |
| ON | 20373 | 0 | 6.03 | 4,810,553 | `a96a3105409bdb4e651416eaf4c1b7eeae8a2b41b6cbf157aa2fccb04a5c34e0` | `f038cde992d13f868b06a7acf6cee922a3096345dda39f72761d5326f67fcdfb` |

No cap fired (600 s wall, 180 s no-progress, 64 MiB log all clear).

## Result table (predeclared checks, `check_n8d7g.py`)

| Observable | OFF | ON | Expected | Check |
| --- | --- | --- | --- | --- |
| alignment tick/fbp/pmode/w/h | 2050/112/ff21/512/448 | 2050/112/ff21/512/448 | same | PASS |
| circuit1 stage tiles/h/control | 448 / 224 / 128 (active 300) | 448 / 224 / 128 (active 300) | 448 / 224 / 128 | PASS |
| pre_deinterlace_merged tiles/h/control | 448 / 224 / 128 (active 300) | 448 / 224 / 128 (active 300) | 448 / 224 / 128 | PASS |
| final stage tiles/h/control | 896 / 448 / 128 (active 567) | 896 / 448 / 128 (active 567) | 896 / 448 / 128, active ≥ 500 | PASS |
| checkerboard control | PASS (128) | PASS (128) | PASS | PASS |
| `[n8d7f]` rows present | no (flag silent) | yes | OFF silent | PASS |
| selected metadata | n/a | tick 2050, fbp 112, samples 1, promoted 0, extent/valid 512x224, status 2, mask 4194303 | same | PASS |
| selected geometry | n/a | dbx 0, dby 0, phase 0, stride 2 | in-bounds | PASS |
| capture bytes | n/a | `bytes=5177344` | ≤ 6 MiB boundary | PASS |
| input / circuit / stage vectors | n/a | 448 tiles each, occupied 64374, active 300 | input/circuit active ≥ 224 | PASS |
| input == circuit, circuit == stage | n/a | equal (448/448, 448/448) | equal | PASS |
| final present hash | `7bf5c012` | `7bf5c012` | `7bf5c012` | PASS |
| error scan (both logs) | 0 | 0 | 0 | PASS |

`result.json`: `verdict: PASS`, `failed: []`, all 24 boolean checks `true`.

## Frames (private, for orchestrator visual inspection — identical SHAs)

| Frame | Bytes | SHA-256 |
| --- | --- | --- |
| `/Users/brad/dev/ssx3-work/N8D7F/off-ppm/vq-002050.ppm` | 688,143 | `8c85489e242eb8a24f96e21495728ec7c80efdd7747b40a8fb0c5e4ffea25d4d` |
| `/Users/brad/dev/ssx3-work/N8D7F/on-ppm/vq-002050.ppm` | 688,143 | `8c85489e242eb8a24f96e21495728ec7c80efdd7747b40a8fb0c5e4ffea25d4d` |

## Notes and gaps

- First checker invocation (before the orchestrator fix) returned `OTHER` with
  `error: "'packed_sha256'"`: the old `fields()` regex `[a-z_]+` could not capture
  digit-bearing field names. The orchestrator fixed `check_n8d7g.py` to
  `[a-z_][a-z0-9_]*`; the checker was then rerun **on the same saved logs** (no replay
  rerun). This receipt records both states: `result.json` now holds the PASS.
- Both frame PPMs are byte-identical (same size and SHA-256), consistent with the
  identical final present hash and equal tile vectors.
- Full logs and PPMs stay private under `~/dev/ssx3-work/N8D7F/` and are not committed.
  Receipt dir is ~4 KiB (≤ 1 MiB cap); lane added ~11 MB of private logs/PPMs.
- No Odin/device action and no GS-cause conclusion were made or are implied by this worker.
  This is Mac host calibration only.

## Next-action recommendation

The Mac calibration gate is green; no worker rerun is needed. Orchestrator can treat this
pinned-stream replay as the Mac-side precondition for the next packaged step. Any verdict,
including whether to package for Odin, remains with the orchestrator.
