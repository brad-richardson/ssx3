# N8D7M12 Part 5M4 — one corrected Mac OFF control run (EXECUTED)

**State: ACCEPTED (acceptance PASS), classification `flag-unperturbed`. One
released Mac OFF replay ran on the exact reviewed driver SHA with the pinned
Part 1 binary/stream. The binary exited 0, the suite passed 585/585/0, the
tick2050 summary/frame and the exact 41 ordered rows 50…2050 were produced,
and both the OFF `parallel.hashes` and the OFF `vq-002050.ppm` are
byte-identical to the pinned Mac ON — so the Mac output is insensitive to
the three tick2050 capture flags on this stream. No source/binary/stream/
fork edit, no build, no device action, no push. No graphics root cause is
established; the 3.0 s diagnostic wall is control only, never speed.**

Brief: `local/muse/prompts/N8D7M12P5M4.md`. Goal: run the one corrected Mac
OFF replay on released driver SHA `1056304d…6738`, holding the Part 1 Mac ON
binary `2a0446e8…68ae5` and stream `f6a78f71…a593` fixed, dropping exactly
the three tick2050 capture flags, then compare all 41 rows and the tick2050
PPM against the pinned Mac ON. Hypotheses: flag effects at tick2050 may
change output; otherwise OFF rows/PPM match ON. Any difference before
tick2050 voids that causal comparison.

## 1. Pins (preflight re-verified before the run and by `check.py` after)

| Item | Path | Size | SHA-256 |
| --- | --- | --- | --- |
| Driver (released) | `local/research/N8D7M12P5M3/mac_off.py` | — | `1056304d3f2d559936f56ae189c419813581bb46f7cf35ae26d0dc7ad12d6738` |
| Binary (Part 1) | `~/dev/ssx3-work/N8D7M12/build/ps2xTest/ps2x_tests` | 8,369,016 B | `2a0446e89f8fc0cec621cd1f53adf81c1ba8b95940f8ac2cc041729887268ae5` |
| Stream | `~/dev/ssx3-work/N8D7M6/n8d7m6.gs` | 1,100,696,462 B | `f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593` |
| Mac ON hashes | `~/dev/ssx3-work/N8D7M12/mac-parallel/parallel.hashes` | 2,686 B | `94b433dfcbebc3b7a9fd57e85c8ce049969a1d8314e2d2d0b1a357773a10c290` |
| Mac ON PPM | `~/dev/ssx3-work/N8D7M12/mac-parallel/vq-002050.ppm` | 688,143 B | `9490484c50ff604d709c7c429f50af10f8da28ee9c0ccb2c7fde2619a14fce3e` |
| Fork HEAD | `~/dev/ssx3-work/N8D7M12/PS2Recomp` (`n8d7m12-replay-core`) | — | `24801bcfa42611e5e36c8990183b793d28b4e5e8` |
| Fork header | `…/ps2xRecomp/include/ps2recomp/instructions.h` | 31,244 B | `b8de8745e16d6a814763f69b0e8d1d54d957bf427f94ec2bc57f63e509f970cd` |
| **OFF hashes (produced)** | `~/dev/ssx3-work/N8D7M12P5M3/mac-off/parallel.hashes` | 2,686 B | `94b433dfcbebc3b7a9fd57e85c8ce049969a1d8314e2d2d0b1a357773a10c290` (== ON) |
| **OFF PPM (produced)** | `~/dev/ssx3-work/N8D7M12P5M3/mac-off/frames/vq-002050.ppm` | 688,143 B | `9490484c50ff604d709c7c429f50af10f8da28ee9c0ccb2c7fde2619a14fce3e` (== ON) |

## 2. Preflight (all green before the single run)

| # | Preflight | Result |
| --- | --- | --- |
| 1 | Released driver SHA == `1056304d…6738` | PASS |
| 2 | `check.py --self-check` (P5M3) | PASS **A 39/39** |
| 3 | `py_compile` driver + checker | PASS |
| 4 | Two-read SHA/size pins (binary, stream, ON hashes, ON PPM, fork HEAD, header) | PASS (all 2× match) |
| 5 | Private OFF output absent | PASS (scratch did not exist) |
| 6 | Disk <200 GB, ≥1 GB headroom | PASS, 150.4 GB of 200 GB cap, 99 GiB free |
| 7 | One mini P-lane slot free, no heavy host build | PASS (both slots free; only clangd LSP) |

Full preflight: `preflight.txt`. One released command, once, from repo root:

```sh
python3 -u local/research/N8D7M12P5M3/mac_off.py --released-sha 1056304d3f2d559936f56ae189c419813581bb46f7cf35ae26d0dc7ad12d6738
```

## 3. Run result — acceptance PASS

| Gate | Required | Observed | Verdict |
| --- | --- | --- | --- |
| exit 0 | 0 | **0** | PASS |
| suite 585/585/0 | yes | `Total Tests: 585 / Passed: 585 / Failed: 0`, no `[Failed]`/`[Error]` | PASS |
| `GB4_REPLAY_SUMMARY` (parallel, markers=2050) | yes | `mode=queue backend=parallel packets=862958 priv=11499 transfers=25445 markers=2050 samples=41` | PASS |
| `GB4_FRAME tick=2050` | yes | `backend=parallel pmode=ff21 present=d19b96fe` | PASS |
| exact 41 ordered ticks 50…2050 | yes | 41 rows, exact sequence | PASS |
| `vq-002050.ppm` present | yes | 688,143 B | PASS |
| no parse/backend error | yes | none | PASS |
| bounded outputs | ≤16 MiB log / ≤64 MiB tree | 4,800,871 B log; tree 5.24 MiB | PASS |
| child stopped, lease free | yes | exit_code=0 (self-exit); slot released; both slot files absent | PASS |
| pins unchanged | yes | binary/stream/ON hashes/ON PPM all match pins | PASS |
| cwd fixture only pinned fork | yes | `cwd/ps2xRecomp` → pinned `…/PS2Recomp/ps2xRecomp` | PASS |

Driver verdict: `PROVISIONAL PASS`. `check.py` independently recomputed all
17 acceptance checks from the raw log/result/rows/PPM: **acceptance PASS,
final run verdict PASS, 17/17** (`check-result.json`).

The Part 5M2 failure is fixed by the Part 5M3 private-cwd fixture: the
CodeGenerator test found `instructions.h` and the suite ran 585/585/0.
`elapsed_s = 3.05` is a diagnostic control time, **not** a speed number.

## 4. OFF vs pinned Mac ON — 41 rows and PPM

All comparison fields are **byte-equal**:

| Field | OFF | pinned Mac ON | Match |
| --- | --- | --- | --- |
| `parallel.hashes` SHA-256 | `94b433df…10c290` | `94b433df…10c290` | identical (2,686 B) |
| 41 rows, tick sequence | 50…2050 exact | 50…2050 exact | 41/41 rows byte-equal |
| `vq-002050.ppm` SHA-256 | `9490484c…14fce3e` | `9490484c…14fce3e` | identical (688,143 B) |
| tick2050 present | `d19b96fe` | `d19b96fe` | identical |
| parser counts | packets 862958, priv 11499, transfers 25445, markers 2050, samples 41 | same | identical |

Full row list: `row-comparison.txt` (all 41 marked `==`). Predeclared
classifier reading: **`flag-unperturbed`** (41/41 rows equal AND PPM
byte-equal) — the Mac output is insensitive to the three removed tick2050
capture flags on this stream. `void-pre2050` and `tick2050-only` did not
occur; no pre2050 difference exists to void the comparison.

**Bounded reading (do not over-lift):** this is a control comparison on one
pinned binary and one stream. It establishes that OFF rows/PPM match Mac
ON; it does not by itself attribute either artifact to current source, and
no graphics root cause is established.

## 5. Absolute OFF PPM for orchestrator viewing

```
/Users/brad/dev/ssx3-work/N8D7M12P5M3/mac-off/frames/vq-002050.ppm
SHA-256 9490484c50ff604d709c7c429f50af10f8da28ee9c0ccb2c7fde2619a14fce3e  (688,143 B)
```

## 6. Cleanup

| Item | State |
| --- | --- |
| Lease | slot 1 claimed dynamically, released in `finally`; both slot files absent |
| Child | self-exited (exit_code=0); PID 92827 gone |
| Stop | own PID only; no `pkill`/`pgrep`/`killall` |
| Outputs | log 4,800,871 B (≤16 MiB), tree 5.24 MiB (≤64 MiB) |
| Retry | none — exactly one released command was issued |

## 7. Handback table

| Condition | Outcome | Next action |
| --- | --- | --- |
| One released replay, exit 0, suite 585/585/0, artifacts byte-equal to Mac ON | **acceptance PASS, `flag-unperturbed`** | Orchestrator decides whether a `flag-unperturbed` Mac OFF control is sufficient; no further run needed under this brief |
| Any pre2050 row difference | not observed | would have been `void-pre2050`; none |

## 8. Receipts (committed, explicit paths only)

| File | Content |
| --- | --- |
| `local/research/N8D7M12P5M4/REPORT.md` | this report |
| `local/research/N8D7M12P5M4/check.py` | read-only independent receipt checker |
| `local/research/N8D7M12P5M4/check-result.json` | checker output, acceptance PASS, 17/17, `flag-unperturbed` |
| `local/research/N8D7M12P5M4/preflight.txt` | bounded preflight/pin receipt |
| `local/research/N8D7M12P5M4/driver.log` | bounded driver stdout (14 lines) |
| `local/research/N8D7M12P5M4/off-result.json` | driver `result.json` (pins, env diff, 41 rows) |
| `local/research/N8D7M12P5M4/off-parallel.hashes` | produced OFF 41-row hash file |
| `local/research/N8D7M12P5M4/row-comparison.txt` | 41 OFF rows vs ON, all `==` |
| `local/research/N8D7M12P5M4/markers.txt` | GB4 summary/frame/stats/tick2050 rows |
| `local/research/N8D7M12P5M4/first-failure.txt` | suite totals excerpt (no failure) |

Commit `[N8D7M12] Part 5M4` with `Orchestrated-By: opencode`, explicit
paths only, no push. Private scratch (not committed, outside git):
`~/dev/ssx3-work/N8D7M12P5M3/{driver.log,result.json,mac-off/}`.
