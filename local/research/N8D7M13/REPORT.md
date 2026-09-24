# N8D7M13 — first tick where Odin VRAM departs from Mac (Part 13A COMPLETE)

Brief: `local/muse/prompts/N8D7M13.md`. Part 13A only: Mac STEP=1 control run
+ Odin launcher/checker. No device action, no adb, no install/launch, no
lease beyond one mini slot, no source/fork/APK/stream/build edit, no push,
no board/ledger edit, no upstream contact, no subagents. No graphics verdict;
tables and receipts only.

**Headline: the Mac control FAILED — STEP=1 perturbs the Mac.** At the 41
control ticks, vram 41/41 and priv 41/41 equal the P5F4P2 Mac rows, but
present 0/41 and PKTSEQ seq/commands 0/41 differ (first diff tick50), the
tick2050 PPM differs, and the PKTSEQ stream has gaps plus stdout-interleaved
corrupt lines (2023 strict-valid rows of 2050). Per brief step 1 this is a
stop-and-report control outcome; the step1 launcher below is prepared exactly
per the brief's allowed changes but its strict 2050-row PKTSEQ gate conflicts
with the observed Mac behavior (see §6) and must not be released as-is for
13B without an orchestrator amendment.

## 1. Pins (two matching SHA reads before use)

| Item | Value |
| --- | --- |
| Mac binary `~/dev/ssx3-work/N8D7M12P5F4/build/ps2xTest/ps2x_tests` | `3b21ce6149b3e4b6ddb6757589cb0b6a688c553d016d53bcd8fb2221cbd56153` ×2 (matches brief) |
| Stream `~/dev/ssx3-work/N8D7M6/n8d7m6.gs` | `f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593` ×2 (matches brief) |
| P7 launcher anchor `local/research/N8D7M12P7/launch.py` | `5983f315982ea08eb41c8fe0593e57e7b59c272faad7ae516a4300ac78b934aa` ×2 (released SHA) |
| New launcher `local/research/N8D7M13/launch.py` | `f70f8ae1cadfa5d3a7f649b8633988222ade8bb1435b473cc301da9d7d0cc99c` ×2 (unreleased) |
| P5F4P2 Mac rows `local/research/N8D7M12P5F4P2/replay-excerpt.txt` | 85 lines: 41 PKTSEQ + 41 REPLAY + summary lines |
| cwd / Vulkan | `/Users/brad/dev/ssx3-work/N8D7M12P5F4/PS2Recomp` (P5F4P3 worktree), `GRANITE_VULKAN_LIBRARY=/opt/homebrew/lib/libvulkan.1.dylib` |

## 2. Mac STEP=1 run (one mini-lease slot, rc=0)

| Field | Value |
| --- | --- |
| Lease | slot 1 claimed `n8d7m13a`, released after (both slots free) |
| Env | P5F4P2 ON env verbatim except `PS2X_GS_REPLAY_STEP=1`; outputs under `~/dev/ssx3-work/N8D7M13/mac/` |
| Wall cap | 600 s via Python `Popen.wait(timeout=600)` driver (`run_mac.py` in private scratch); no `timeout(1)` on macOS |
| Exit | rc=0; suite tail `Passed: 586 Failed: 0`; output tree 6.8 MiB (≤64 MiB/run) |
| `GB4_REPLAY` rows | **2050**, ticks 1..2050 in order, no dupes, all strict-grammar |
| `GB4_PKTSEQ` rows | **2023 strict-valid of 2050** (see §4); brief required 2050 — NOT met |
| Summary | `packets=862958 priv=11499 transfers=25445 markers=2050 samples=2050` (counts equal P5F4P2) |
| tick2050 PPM | `e64a98028b80bfcc44897fed3edf4da82c45805dc4660f80877709a766d8e337`, 688,143 B — DIFFERS from pinned Mac ON `9490484c…14fce3e` |

Exact command (env from §1, cwd the P5F4 worktree, PID-owned, 600 s cap):

```sh
python3 /Users/brad/dev/ssx3-work/N8D7M13/run_mac.py  # sets the 11 env vars, Popen + wait(600)
```

(`timeout(1)` missing and shell `&` backgrounding refused are tooling notes,
not brief-step failures; the first real run is the one reported here.)

## 3. Control: STEP=1 rows at ticks 50..2050 vs P5F4P2 Mac rows — FAILED

| Field | Equal/41 | First diff |
| --- | --- | --- |
| PKTSEQ `seq` | **0/41** | tick50 |
| PKTSEQ `commands` | **0/41** | tick50 |
| REPLAY `vram` | 41/41 | none |
| REPLAY `priv` | 41/41 | none |
| REPLAY `present` | **0/41** | tick50 |

Examples (step1 vs P5F4P2):

- tick50 PKTSEQ: `seq=962395a2686a6207 commands=349` vs `seq=408d8fbb43ad4cb6 commands=251`
- tick50 REPLAY: `vram=1edcff3d priv=af58b6ee present=84f5f2a1` vs `vram=1edcff3d priv=af58b6ee present=c5b577f5` (vram+priv equal, present differs)
- tick2050 PKTSEQ: `seq=16ec2f720458cd5f commands=1741514` vs `seq=79ee00a3024bfb44 commands=1737496`
- tick2050 REPLAY: `vram=c883a705 priv=6621fe06 present=6bd96542` vs `vram=c883a705 priv=6621fe06 present=d19b96fe`

Reading per the brief's stop rule: STEP=1 perturbs the Mac in `present` and
in worker-consumption seq/commands (cumulative counts differ too, e.g. +4018
by tick2050), while vram/priv are unperturbed at all 41 sampled ticks.

## 4. PKTSEQ stream accounting (Mac STEP=1 log)

2050 expected emissions, `tick % stride == 0` with stride=1
(`gs_replay_core.cpp:209-214,451`):

| Class | Count | Detail |
| --- | --- | --- |
| Strict-valid `GB4_PKTSEQ tick=N seq=%016x commands=N` | 2023 | — |
| Corrupt but tick recoverable (mid-line `[INFO]: G11: flush()…` interleave) | 19 | e.g. ticks 82, 157, 520, …, 1939 |
| Tick field destroyed (`tick=[INFO]…`) | 2 | unattributed |
| Prefix destroyed (`GB4_PKTSEQ [INFO]…`, `GB4_PKTSEQ tic[INFO]…`) | 3 | unattributed |
| `GB4_` prefix clobbered, values intact | 1 | tick232 `seq=bd4dc9cb75a895e4 commands=6921` |
| Glued to suite `[Run]:` line, values intact | 1 | tick1 `seq=af63c94c8601cc43 commands=1` |
| No emission found | 1 | one of {374, 447, 1185, 1342, 1642, 2009}; unidentified |
| **Total** | **2050** | 2049 line-occurrences + 1 absent |

Mechanism (code-grounded, no fix attempted): PKTSEQ emits via
`std::cout << seqLine << '\n'` (`gs_replay_core.cpp:466`, two insertions)
while the render thread logs `[INFO]: G11: flush()…` to the same stdout —
4100 such lines at STEP=1 (2/sample, same rate as the 82 at STEP=50, where
41/41 rows happened to survive). REPLAY rows are immune because they
accumulate in a vector (`rows.emplace_back`, `:532`) and flush in bulk.

## 5. Odin launcher `step1` (prepared, UNRELEASED)

Copied from the released P7 launcher (`5983f315…b934aa`, byte-identical copy
verified with `cmp` before editing). SHA
`f70f8ae1cadfa5d3a7f649b8633988222ade8bb1435b473cc301da9d7d0cc99c` (×2 reads).
Allowed changes only, per brief step 2:

| # | Change |
| --- | --- |
| 1 | `PS2X_GS_REPLAY_STEP=50` → `=1` (one line; env block otherwise byte-identical) |
| 2a | PKTSEQ gate: `range(50, 2051, 50)` → `range(1, 2051)`; messages `41 ticks 50..2050` → `2050 ticks 1..2050` |
| 2b | New `replay_tick_rows` gate mirroring `pktseq_rows`: ordered (tick, vram, priv, present), None unless exactly ticks 1..2050; enforced in `run()` before force-stop |
| 3 | Single run label `step1`: `--run step1` required; scratch `…/N8D7M13/step1`; lease tag `N8D7M13 step1 replay`; remote basenames `n8d7m13-step1-frames-…` / `n8d7m13-step1-…`; brief id `N8D7M13` throughout |
| 4 | Progress cap 180 s and wall cap 600 s unchanged (verified in file) |

Pins (APK/runner/Turnip/HAL/stream), census gate, serial pin, keyguard
blocker, env preserve/restore, force-stop/lease `finally`, drain bound, and
provisional marking are untouched. No `run1`/`run2`/`STEP=50`/P7 residue
(grep clean). `py_compile` OK.

`check.py`: diff-vs-P7 allowlist gate (classes step/gates/runid + exact added
lines; every changed line classified, all classes fired), pins/env/caps/
safety presence checks, no-device self-tests (arg shape incl. `run1`
rejection, wrong-SHA hold, one-run guard on `step1/`, synthetic 2050-row
PKTSEQ positive + drop/swap/dup/malformed/empty negatives, real Mac STEP=1
log as PKTSEQ-negative (documents the §4 gaps) and REPLAY-positive 2050/2050
with tick2050 spot-check), `py_compile` of both files, single-subprocess-site
rule. Result: **A 38/38**, `launch_sha=f70f8ae1…0cc99c` (see §7).

## 6. Conflict for the orchestrator (13B cannot run as briefed)

The brief's prescribed strict 2050-row exact-tick PKTSEQ gate cannot pass on
a Mac-like Odin: the Mac produced 2023 strict-valid rows with 8 unattributed
ticks and 24 interleaved lines. If the Odin behaves the same way, the
released launcher would FAIL at the PKTSEQ gate after a full device run
(device left clean by `finally`, but the run void). Separately, STEP=1
perturbs `present` and PKTSEQ values vs STEP=50, so an Odin-vs-Mac STEP=1
comparison measures first-tick departure only if both sides are perturbed the
same way — the brief's predeclared 13B readings assume an unperturbed Mac
baseline that §3 refutes. Recommended next action (orchestrator decision):
amend the brief (e.g. gate on the 2050 REPLAY rows + best-effort PKTSEQ, or
serialize the PKTSEQ emission first) before any 13B release. No OFF control
is run or claimed here.

## 7. Receipts

- `local/research/N8D7M13/{REPORT.md,launch.py,check.py,check-result.json}` —
  commit `[N8D7M13] Part A` with `Orchestrated-By: Muse Code`, explicit paths
  only, no push. `check.py` verdict A 38/38; diff 68 changed lines / 13 hunks,
  21/21 exact new-gate lines consumed, classes step+gates+gates_exact+runid
  all fired, zero unmatched.
- Private scratch (not committed): `~/dev/ssx3-work/N8D7M13/{mac/{replay.log,
  parallel.hashes,frames/vq-002050.ppm},run_mac.py}` (6.8 MiB).
- Gaps: suite `[Run]:` line gluing shows test-harness stdout shares the
  replay fd; one PKTSEQ tick fully unattributed; emission-race mechanism is
  code-read, not experimentally confirmed; no second Mac run (one-run
  budget); no OFF control.
- Budgets: 13A one Mac run, 0 installs, 0 launches, 0 builds; receipts < 512
  KiB text; outputs ≤ 64 MiB.
