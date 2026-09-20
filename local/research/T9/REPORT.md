# T9 report — ladder_diff waiter-phase rule: waiter presence SAMPLED, histories the signal

Brief `local/muse/prompts/T9.md`. TOOLING brief: 1 fork commit
(rule + unit tests) + 0 boots (re-verdict existing snapshots only).
Tables, no verdicts. Stale-reading guard: `local/research/T5/REPORT.md`
§T5-7 (the D verdict: 1054 exact / 245 tol-ok / 2 KEY_DELTAs on
`sema.29.table` + `sema.32.table` waiter presence, 0 COUNT_DELTAs) +
`local/research/T1/REPORT.md` §T1-3 (verdict-class semantics extended
here) re-read first.

`R=/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp` (fork, branch
`ssx3`), `W=/Volumes/Extreme SSD/ps2recomp-spike`. Peer lanes run
concurrently — read-only on other agents' files; named adds only.

Headline receipts: D BEFORE exit 1, byte-identical to `T5/D.txt`
(1054/245/3 info/2 KEY_DELTA); D AFTER exit 0 (1054/245/5 info/0
deltas; BEFORE-vs-AFTER diff = 2 rows + ladder line); D1/D2
byte-identical before/after (exit 0 both); test file 6/6 green from
both invocation forms.

## T9-0. Tree state at start

| Event | Value |
|---|---|
| ssx3 HEAD observed | `31979dc` (peers advance main concurrently; T9 touches `local/research/T9/` only) |
| Fork HEAD at start | `1a76df4` == brief's base (no peer commits; `fork/ssx3 == 1a76df4` at pre-push fetch) |
| Fork `M` at start | `ps2xRuntime/src/runner/register_functions.cpp` (pre-existing generated, never staged) |
| Lease | None (0 boots — re-verdict existing snapshots only) |
| `adb` | Not used |
| Snapshots | Committed, read-only: `local/research/T5/park-snapshot-{base,rule}.json` |

## T9-1. BEFORE receipts (unmodified tool)

| Diff | Sides | Exit | Ladder line | vs committed |
|---|---|---|---|---|
| D (`T9/D-before.txt`) | T5 base-vs-rule | 1 | 1054 exact, 245 tol-ok, 3 info, 2 deltas → DELTA | `diff` vs `T5/D.txt` clean |
| D1 | T1 emitter-vs-miner (same boot) | 0 | 97 exact, 8 tol-ok, 1184 info, 0 deltas → OK | `diff` vs `T1/D1.txt` clean |
| D2 | re-mined p1ad1-vs-p1ad2 (committed miner, read-only logs) | 0 | 116 exact, 11 tol-ok, 63 info, 0 deltas → OK | `diff` vs `T1/D2.txt` clean |

The 2 KEY_DELTA rows (BEFORE), exactly as printed:

| Row | BASE | RULE | Verdict |
|---|---|---|---|
| `sema.29.table` | `(0, 0, 0, 1)` | `(0, 0, 0, 0)` | KEY_DELTA |
| `sema.32.table` | `(0, 16, 0, 0)` | `(0, 16, 0, 1)` | KEY_DELTA |

## T9-2. Rule spec (as implemented)

Wait-set per side: `{tid : status == 2 (Waiting), wait_reason == 2
(Semaphore), wait_id == sid}`. Applies inside the both-tables branch
only (miner pairs keep the single `semaphores.table` BLIND row).

| Condition (`sema.{sid}.table`) | Verdict | Note |
|---|---|---|
| Tuples equal, wait-sets agree | EXACT | — |
| `count`/`max`/`init` differ (rule scoped to waiter presence) | KEY_DELTA | — |
| Wait-sets differ (`count`/`max`/`init` agree) | SAMPLED | `waiters sampled: {A} {t…->semaN \| none} vs {B} {…}` |
| Wait-sets agree but waiter counts differ | KEY_DELTA | `waiters disagree despite agreed wait-set` |

Equal tuples with differing wait-sets read SAMPLED (count equality is
coincidence; exact only when the sampled thread states agree on the
wait). Cumulative wait/signal histories stay throughput-gated
(unchanged code path).

## T9-3. Tests first (`tools/test_ladder_diff.py`, stdlib unittest)

| Test | BEFORE (unmodified tool) | AFTER |
|---|---|---|
| Waiter rows SAMPLED + correlation when sets differ (T5-shape pair) | FAIL (`KEY_DELTA`) | Pass |
| Waiter rows EXACT when sets agree (snapshot vs itself, all rows) | Pass | Pass |
| Count mismatch with agreed set is KEY_DELTA (exit 1) | Pass | Pass |
| Equal count with differing set is SAMPLED | FAIL (`EXACT`) | Pass |
| Non-waiter sema fields stay exact (count diff → KEY_DELTA) | Pass | Pass |
| Histories stay TOL-gated (small → TOL_OK, large → COUNT_DELTA) | Pass | Pass |
| Total | 4/6 | 6/6 |

| Item | Value |
|---|---|
| Call (recorded) | `python3 tools/test_ladder_diff.py` from the fork root — 6/6; `python3 test_ladder_diff.py` from `tools/` — 6/6 |
| Fixture scope | Inline copies of T5's governing thread/sema values (t1/t5 phases, sema 29/32 tuples, agreeing sema-26 anchor) — copied, never modified. Named-adds allows no fixture files and the fork cannot reference ssx3 paths, so the full committed pairs are re-verdicted as evidence (§T9-5) instead of asserted in-fork |

## T9-4. Fork commit + push

| Item | Value |
|---|---|
| Commit | `935a4eb` (`Tool: ladder_diff waiter-phase rule -- waiter presence SAMPLED (T9)`, 2 files +215/−6, `Orchestrated-By: Muse Code`) |
| Staged set | `tools/ladder_diff.py` + `tools/test_ladder_diff.py` — named files only, verified; generated `M` never staged |
| `._*` / `__pycache__` | Purged before staging / removed after test runs; neither staged (ExFAT precedent) |
| `pull --rebase` | Refused on the unstaged generated runner file (T5/P9 precedent); pre-fetch clean (`fork/ssx3 == 1a76df4`, no peer commits, nothing to replay) |
| Push | `git push fork ssx3` from the fork clone only (`1a76df4..935a4eb`, fast-forward); `fork/ssx3 == 935a4eb` |
| NEVER in ssx3 | No `git push` in ssx3 (evidence commit local only, §T9-8) |

## T9-5. AFTER re-verdicts

D AFTER (`T9/D-after.txt`): exit 0; `1054 exact, 245 tol-ok, 5 info,
0 deltas → OK`.

| Row | BASE | RULE | Verdict | Note |
|---|---|---|---|---|
| `sema.29.table` | `(0, 0, 0, 1)` | `(0, 0, 0, 0)` | SAMPLED | `waiters sampled: base t1->sema29 vs rule none` |
| `sema.32.table` | `(0, 16, 0, 0)` | `(0, 16, 0, 1)` | SAMPLED | `waiters sampled: base none vs rule t5->sema32` |

BEFORE-vs-AFTER scope (`diff T9/D-before.txt T9/D-after.txt`): lines
22 + 25 (verdict + note) and 1306 (ladder line) only — all other 1303
rows byte-identical; 0 verdict changes outside the waiter class
(SAMPLED 3→5, KEY_DELTA 2→0, every other class equal).

T1 D1 old-vs-new, per row-class (AFTER exit 0, bytes identical to BEFORE):

| Class | BEFORE | AFTER |
|---|---|---|
| EXACT | 97 | 97 |
| TOL_OK (worst 4.1%) | 8 | 8 |
| SAMPLED | 3 | 3 |
| SATURATED | 4 | 4 |
| STALE | 2 | 2 |
| BLIND | 5 | 5 |
| TRUNC | 1170 | 1170 |
| KEY_DELTA / COUNT_DELTA | 0 / 0 | 0 / 0 |

T1 D2 old-vs-new, per row-class (AFTER exit 0, bytes identical to BEFORE):

| Class | BEFORE | AFTER |
|---|---|---|
| EXACT | 116 | 116 |
| TOL_OK (worst 3.8%) | 11 | 11 |
| SAMPLED | 1 | 1 |
| BLIND | 2 | 2 |
| TRUNC | 60 | 60 |
| KEY_DELTA / COUNT_DELTA | 0 / 0 | 0 / 0 |

Miner pairs carry no sema table (single BLIND row), so the rule's
branch evaluates 0 rows on D1/D2 — the identical bytes are structural,
not coincidental.

## T9-6. T5-proof closure (numbers only)

| Row | Value |
|---|---|
| Rule | Waiter SAMPLED iff wait-sets differ (+ `t->sema` correlation); EXACT iff agree |
| Counts | D: 1054 exact / 245 tol-ok / 5 info / 0 deltas (was 3 info / 2 deltas) |
| Suite | `tools/test_ladder_diff.py` 6/6 (stdlib-only tool + tests; no build refs) |
| Behavior rows | `thread.1/5.status` SAMPLED (unchanged); 29/32 wait+signal histories TOL_OK ≤0.2% (unchanged); hot-pc 966 exact + 222 tol-ok, drops/rpc/gs/sched rows all unchanged |
| New D | Exit 0 (`T9/D-after.txt`) |

## T9-7. Gaps

| # | Gap | Why unresolved |
|---|---|---|
| 1 | Correlation note uses `--names` labels; default path-names make long notes | Cosmetic; every T9 call passes `--names` |
| 2 | Full T5 snapshots as fork fixtures | Named-adds allows no fixture files; full pairs re-verdicted as evidence (§T9-5) |
| 3 | C++ suite not run | Tool is stdlib-only with no build refs (T1-commit-2 precedent) |
| 4 | `count`/`max`/`init` sampled-phase question | Untouched: rule scoped to waiter presence per the brief |

## T9-8. Exact commands

```
# BEFORE (unmodified tool @ 1a76df4)
python3 $R/tools/ladder_diff.py local/research/T5/park-snapshot-base.json \
  local/research/T5/park-snapshot-rule.json --names base,rule   # exit 1, diff vs T5/D.txt clean
python3 $R/tools/ladder_diff.py local/research/T1/park-snapshot.json \
  local/research/T1/mined-proof.json --names emitter,miner      # exit 0, diff vs T1/D1.txt clean
python3 local/research/T1/mine_snapshot.py $W/P1/run/boot-p1ad-1.log -o /tmp/t9-mined-p1ad1.json
python3 local/research/T1/mine_snapshot.py $W/P1/run/boot-p1ad-2.log -o /tmp/t9-mined-p1ad2.json
python3 $R/tools/ladder_diff.py /tmp/t9-mined-p1ad1.json \
  /tmp/t9-mined-p1ad2.json --names p1ad1,p1ad2                 # exit 0, diff vs T1/D2.txt clean
# tests first (fork clone)
python3 tools/test_ladder_diff.py                               # BEFORE 4/6 (2 rule tests fail)
# (edit tools/ladder_diff.py)
python3 tools/test_ladder_diff.py                               # AFTER 6/6; also 6/6 from tools/
# AFTER re-verdicts: same five diff calls; diff BEFORE-vs-AFTER per pair
# fork commit + push (fork clone only)
git add tools/ladder_diff.py tools/test_ladder_diff.py
git commit -- <2 files> -m "Tool: ... (T9)"                     # 935a4eb
git fetch fork ssx3; git pull --rebase fork ssx3                # refused (generated M), pre-fetch clean
git push fork ssx3                                              # 1a76df4..935a4eb
# evidence (ssx3, no push)
git add -f local/research/T9/D-before.txt local/research/T9/D-after.txt local/research/T9/REPORT.md
git commit -m "[T9] ..."                                        # local only
```

Receipt paths: `local/research/T5/park-snapshot-{base,rule}.json`
(read-only inputs), `local/research/T9/{REPORT.md,D-before.txt,D-after.txt}`,
`/tmp/t9-{D,D1,D2}-{before,after}.txt`, `/tmp/t9-mined-p1ad{1,2}.json`.

## T9-9. What I could not do

- Run a proof boot (0-boot brief; re-verdicts only, lease never needed).
- One session, inside the 4 h box.
