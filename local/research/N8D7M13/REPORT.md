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

---

# Part 13B — one Odin STEP=1 run + comparison (COMPLETE)

Released launcher SHA `50abff3da0e2af7a83c9cc01021589417506cf817e2812219bf67d961791a557`
(2 matching reads; orchestrator amendment at `d6f4c318`, PKTSEQ gate
best-effort, REPLAY gate kept). Checker re-read against the amended launcher:
B 35/38 with exactly the 3 expected amendment flags
(`gates_2050_both_rows`, `diff_only_allowed_changes` with the 9-line
amendment hunk unmatched, `report_records_launch_sha` until this section
records the released SHA); all self-tests pass. (Post-run re-execution reads
B 33/38: the SHA check flips to pass while the three scratch-untouched
self-tests fail on the real `step1/` receipt by design. The committed
`check-result.json` is the pre-run read.) Launcher not edited further.

**Headline: first VRAM departure Odin-vs-Mac at STEP=1 is tick44**
(leading equal run ticks 1..43; 96/2050 VRAM-equal). priv is 2050/2050
equal. PKTSEQ seq/commands are equal on every Mac-intact row (2026/2026
co-present for seq; the 2 apparent commands diffs are Mac-side truncation
artifacts, see §13B.4). The logcat REPLAY gate failed on 88 dropped lines
(two spans), so per the release instruction there was no retry and no
launcher pull; the on-device `parallel.hashes` was pulled manually with
pull-equivalent verification and has all 2050 rows.

## 13B.1. Preflight (all PASS)

| # | Gate | Value |
| --- | --- | --- |
| 1 | Script SHA == released | `50abff3d…a557` exact, 2 reads |
| 2 | No `step1/result.json`/`driver.log` | scratch has only `mac/` + `run_mac.py` |
| 3 | Serial / state | `622c49b1`, `device` |
| 4 | Odin lease free | `LEASE_FREE N8D7M12P7 run2 done` |
| 5 | No app run | `pidof` empty |
| 6 | Battery | 100%, status 3, AC powered (amended gate) |
| 7 | Free | 24,205,172 KiB (~23.1 GiB) on /storage (≥10 GiB) |
| 8 | Keyguard | launcher-parse `showing=false` |
| 9 | No mini heavy job | slots 1+2 free, no build/boot procs; slot 1 claimed for the run, released after |

## 13B.2. Run receipts (one install + one launch, no retry)

| Field | Value |
| --- | --- |
| Launch SHA | `50abff3d…a557` |
| Lease | `N8D7M13 step1 replay` claimed → `LEASE_FREE N8D7M13 step1 done` |
| Install | one `adb install -r`, Success; device APK `da9a41a8…e6ef262` ×2 |
| Device stream (verify only) | `f6a78f71…a593` ×2, 1,100,696,462 B |
| Env preserve | `176eff84…cef32d` 2+2 match; replay env `02ce77de…2cf8187` (STEP=1) |
| Launch | one `am start`, PID 16253; BACK once |
| Stop | complete tick2050 receipt, elapsed 79.611 s (control only, not speed) |
| Progress | one line: 1962 `GB4_REPLAY` rows at 78.5 s (bulk flush at end) |
| Markers | SUMMARY queue/parallel 862958/11499/25445/2050; FRAME 2050 parallel ff21 `ae8c4201`; `replay ok` 862958/2050; no errors |
| PKTSEQ (best-effort) | exact=True, lines=2050, ticks 1..2050 |
| REPLAY gate | **FAIL**: 1962/2050 logcat rows; missing spans 297–350 (54) + 895–928 (34); no dupes, no corruption |
| Caps | logcat gzip 86,994 B (≤16 MiB); no launcher pull (gate raised first) |
| Postrun | force-stop, PID absent; env restored 2+2; lease released; no `cleanup_errors` |
| `first_failure` / `verdict` | `GB4_REPLAY rows not exactly 2050 ticks 1..2050 in order` / `not found` |

Manual post-run pull (read-only; Odin lease claimed as `N8D7M13 step1
manual-pull`, app re-verified stopped, force-stop repeated, lease released;
transcript `step1/manual-pull.log`): `vq-002050.ppm` 688,143 B
`1a339d84…17b0ff` (2 device + 2 local match);
`parallel.hashes` 134,193 B `c4195281…ed096a` (2+2 match). Total pulled
822,336 B (≤64 MiB). **Pulled `parallel.hashes` has 2050 rows** (ticks
1..2050 in order). Odin logcat's 1962 REPLAY rows all agree with the hashes
file (0 disagreements), so the loss is logcat-side drops of the end-of-run
bulk flush, not replay-side.

## 13B.3. Artifacts (private scratch `~/dev/ssx3-work/N8D7M13/`)

| File | SHA-256 | Size |
| --- | --- | --- |
| `step1/vq-002050.ppm` | `1a339d8447d37725b5381ae85e2adaa02b757f005f662bb3bb3597d60417b0ff` | 688,143 B |
| `step1/parallel.hashes` | `c41952811ece37f873a821742564acf2aba430bd8e00178d44d0b5f3f2ed096a` | 134,193 B |
| `mac/frames/vq-002050.ppm` | `e64a98028b80bfcc44897fed3edf4da82c45805dc4660f80877709a766d8e337` | 688,143 B |
| `mac/parallel.hashes` | (13A input; unchanged) | 134,193 B |

Absolute PPM path for viewing:
`/Users/brad/dev/ssx3-work/N8D7M13/step1/vq-002050.ppm`
(Mac STEP=1: `…/N8D7M13/mac/frames/vq-002050.ppm`; P7 PPMs in `compare-output.txt`).

## 13B.4. Primary comparison (`compare.py`, `compare-output.txt`)

Odin STEP=1 vs Mac STEP=1, per tick 1..2050 (REPLAY from both
`parallel.hashes` files; PKTSEQ from Odin `pktseq.txt` vs Mac `replay.log`,
search-parsed so the glued tick1 row counts):

| Field | Equal/2050 | First diff | Missing |
| --- | --- | --- | --- |
| VRAM | **96** | **tick44** | 0 / 0 |
| priv | **2050** | none | 0 / 0 |
| present | 97 | tick45 | 0 / 0 |
| PKTSEQ seq | 2026 (all co-present) | none intact (tick82 = first Mac gap) | 0 Odin / 24 Mac |
| PKTSEQ commands | 2024 + 2 truncated | none intact (same) | 0 Odin / 24 Mac |

- Longest leading VRAM-equal run: ticks 1..43 (43 ticks); first departure tick44.
- VRAM-equal spans: 1-43, 67, 72-73, 78, 93-109, 246-257, 1457, 1588-1606.
- Departure neighborhood: tick43 identical in all fields
  (`5b42533a/78ee303b/019921c5` priv/vram/present); tick44 priv+present
  equal, vram `e11bfd7c` vs `97b13124`; from tick45 vram+present differ,
  priv always equal.
- The 2 apparent PKTSEQ-commands diffs are Mac-side interleave truncations:
  tick672 Mac `commands=117` vs Odin 117114 (seq equal `93f2b798811e26cd`),
  tick1043 Mac `commands=3542` vs Odin 354279 (seq equal `412345161d172e60`).
  No genuine PKTSEQ difference anywhere intact; tick2050
  `16ec2f720458cd5f`/1741514 identical on both.
- Mac PKTSEQ-missing spans (24): 82, 157, 232, 374, 447, 520, 593, 744, 816,
  888, 972, 1114, 1185, 1271, 1342, 1412, 1483, 1571, 1642, 1712, 1783, 1870,
  1939, 2009 (13A §4 gaps; 672/1043 parse via command-count prefix).

## 13B.5. Secondary: Odin STEP=1 vs P7 STEP=50 pair (ticks 50..2050)

| Field | odin==run1 | odin==run2 |
| --- | --- | --- |
| PKTSEQ seq / commands | 0/41, first tick50 | 0/41, first tick50 |
| priv | 41/41, none | 41/41, none |
| VRAM | 17/41, first tick700 | 20/41, first tick700 |
| present | 0/41, first tick50 | 0/41, first tick50 |

Per-tick readback changes the Odin result: Odin STEP=1 VRAM departs from
both STEP=50 runs at tick700 (at 50-tick sampling), while the two STEP=50
runs agreed with each other through tick800. PKTSEQ/present differ as
expected (sampling-cadence-dependent, cf. 13A §3).

tick2050 rows: odin `3c3c4aee/6621fe06/ae8c4201`, mac
`c883a705/6621fe06/6bd96542`, run1 `8a80c3fd/6621fe06/5d5972bc`, run2
`6c2e01c3/6621fe06/00883449` (vram/priv/present). All four PPMs differ.

## 13B.6. Predeclared-reading evidence rows (orchestrator decides)

| Predeclared condition | Evidence in this run |
| --- | --- |
| First VRAM departure at tick T ≤ 50 | **Condition met**: T=44, leading run 1..43, priv equal throughout |
| Odin VRAM matches Mac through tick850+ (sync implicated) | Not observed: 96/2050 equal, departures from tick44 |
| PKTSEQ differs anywhere (contradicts Part 7) | Not observed on intact rows: 2026/2026 seq equal; 2 Mac truncations + 24 Mac gaps only |
| Preflight/cleanup failure voids the run | No preflight/cleanup failure; logcat REPLAY gate failed (88 dropped lines) with file-based comparison substituted per release instruction |

## 13B.7. Gaps / handback

- Frame content unviewed by this worker; PPM path in §13B.3.
- Odin logcat lost 88/2050 REPLAY lines (two spans); comparison uses the
  complete on-device hashes file (0 logcat-vs-file disagreements).
- One Mac-side PKTSEQ tick fully unattributed (13A §4); Mac PKTSEQ gaps are
  Mac-log artifacts, not Odin differences.
- Budgets: 1 install, 1 launch, 0 builds; active 79.611 s (control only);
  receipts < 512 KiB text; outputs ≤ 64 MiB.
- Recommended next action (orchestrator decision): read §13B.6 against the
  predeclared rule (T=44 ≤ 50 → packet-level bisect inside tick44 per the
  brief's first arm).

Receipts: `REPORT.md` (this file), `compare.py`, `compare-output.txt`,
`check-result.json` — commit `[N8D7M13] Part B` with `Orchestrated-By: Muse
Code`, explicit paths only, no push. (`launch.py` is the released
`50abff3d…a557`, committed at the 13A gate; the 13A `check.py` flags the
amendment as expected and is left untouched.)
