# T12 — Dev build config: ThinLTO-off variant + suite + ladder-identical proof (no adoption)

Tables, no verdicts. Brief `local/muse/prompts/T12.md`.
`local/research/T6/REPORT.md` re-read first (all of it): T6 gap 4 is
this brief — the miss is the ThinLTO runner link (313–397 s of every
incremental), and T6's allowed fix class could not touch it. This
brief measures whether a dev config (ThinLTO off; unity settings
unchanged) recovers incremental builds WITHOUT changing guest
behavior. It does NOT adopt anything: adoption is an
orchestrator/user decision the numbers below inform.

`R=/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp` (fork, branch
`ssx3`), `W=/Volumes/Extreme SSD/ps2recomp-spike`, `RUN=$W/P1/run`.
Peer lanes concurrent; build etiquette observed throughout (§T12-7).

Headline receipts: option `PS2X_DEV_NO_THINLTO` (default OFF, +10
lines, one file); Release runner link line byte-identical
with/without the commit (20,294 B, `diff` clean, zero
normalization); with-commit Release runner binary bit-identical to
T6's no-commit binary (`81bee6c5…`, full-sha match); full builds
rel 710 s / dev 559 s; cell (a) dev 5.9 s (T6 Release: 315 s);
suite 439/439/0 BOTH configs (faces identical); D exit 0 —
1059 exact / 245 tol-ok (worst 1.4%) / 0 info / 0 deltas.

## T12-0. Setup

| Item | Value |
|---|---|
| Date / window | 2026-09-20 07:48–08:35Z (≈47 min, inside the 4 h box) |
| Host | Apple M4, 10 CPUs, macOS; ninja 1.13.2; `/opt/homebrew/opt/llvm/bin/clang(++)` |
| ssx3 HEAD | `6e32383` (start; untouched until the evidence commit) |
| Fork HEAD start | `935a4ebf6db16c4057c30f5dd5cdba23af0ff3b6` (T9 ladder_diff) |
| Fork HEAD end | `7eed783` (T12 config, pushed `fork/ssx3 == 7eed783`) |
| Fork worktree | `M ps2xRuntime/CMakeLists.txt` (T12, staged+committed); `M ps2xRuntime/src/runner/register_functions.cpp` (pre-existing generated, never staged); `?? tools/__pycache__/` removed before staging, never staged |
| Build dirs | `/tmp/t12-link/runtime` (Release), `/tmp/t12-dev-link/runtime` (dev), `/tmp/t12-nocommit` (configure-only base @HEAD — no T12 change), `/tmp/t12-base` (detached worktree @`935a4eb` + rsynced `runner/`, T1 precedent) |
| Sources | `-S $R` for both measured configs (T6 precedent); base worktree differs from `$R` by the CMakeLists edit ONLY (worktree carries `$R`'s working-tree `runner/`, rsynced) |
| Targets | `ps2x_tests ps2EntryRunner` (T1's line), `-j4` MAX, all builds |
| No-lease rule | Boots only under lease (§T12-6); no `adb`; no `git push` in ssx3 |

## T12-1. Config spec (one option, default OFF)

File: `ps2xRuntime/CMakeLists.txt` (+10/−0, the only fork change).
Convention follows the sibling `PS2X_ENABLE_*` options at the top of
the same file.

| Row | Value |
|---|---|
| Name | `PS2X_DEV_NO_THINLTO` |
| Declaration | `option(PS2X_DEV_NO_THINLTO "Dev builds only: skip ThinLTO IPO on the runner link chain (ps2_runtime, ps2EntryRunner) for faster incremental links; Release untouched" OFF)` |
| Mechanism | After the two `EnableFastReleaseMode` calls: `if(PS2X_DEV_NO_THINLTO)` sets `INTERPROCEDURAL_OPTIMIZATION_RELEASE FALSE` on `ps2_runtime` + `ps2EntryRunner`, undoing the `TRUE` set inside `EnableFastReleaseMode` (`ps2xRuntime/cmake/ReleaseMode.cmake:38`). Last-set wins; when OFF the block is a no-op |
| Scope | Runner link chain only: both the static lib (its objects' compile flags) and the executable (its unity compiles + the link). Every other target (`ps2x_tests`, `ps2_recomp`, `ps2_analyzer`, …) keeps IPO in BOTH configs |
| Unity/PCH | Unchanged (batch size 32 both configs; 290 unity objects both link lines) |
| MSVC note | The option gates the portable IPO property only; the MSVC-only `/GL` + `/LTCG` flags in `EnableFastReleaseMode` are untouched (this host is clang; MSVC path unmeasured — gap row) |

Effect table (`ninja -t commands`, `-O3` present in all four cells):

| Line | Release (OFF) | Dev (ON) |
|---|---|---|
| Runner unity compile (`ps2EntryRunner.dir/Unity/unity_0`) | `-flto=thin` | absent |
| Lib compile (`ps2_runtime.dir/.../ps2_runtime.cpp.o`) | `-flto=thin` | absent |
| Runner link (`ps2xRuntime/ps2EntryRunner`) | `-flto=thin` | absent (only delta vs Release: the 11 B ` -flto=thin`) |
| Tests link (`ps2xTest/ps2x_tests`) | `-flto=thin` | `-flto=thin` (unchanged — outside the runner chain) |

## T12-2. Release-flags proof (Release provably untouched)

| Check | Receipt |
|---|---|
| Runner link line, base-worktree (@HEAD, no T12 change) vs with-commit Release | Byte-identical: 20,294 B each, `diff` clean, ZERO normalization (evidence `t12-linkline-nocommit.txt`, `t12-linkline-rel.txt`) |
| `^PS2X_` cache lines, base vs with-commit Release | Exactly one added line: `PS2X_DEV_NO_THINLTO:BOOL=OFF` (evidence `t12-cache-nocommit.txt`, `t12-cache-rel.txt`) |
| With-commit Release runner binary vs T6's no-commit Release binary | Bit-identical: `81bee6c5c0740dafbb910fdfd9c62de8185b816372a0658603dc38c41252d40f`, 163,460,272 B both (`/tmp/t6-link/` binary vs `/tmp/t12-link/` binary) |
| Dev cache line | `PS2X_DEV_NO_THINLTO:BOOL=ON` in `/tmp/t12-dev-link/` only |

## T12-3. Full configure + full build walls (uncontended windows only)

Configure walls (T1/T6 flag line verbatim; dev adds
`-DPS2X_DEV_NO_THINLTO=ON`):

| Configure | Wall | Exit |
|---|---|---|
| `/tmp/t12-nocommit` (base, configure-only) | 74.6 s | 0 |
| `/tmp/t12-link/runtime` (Release) | 89.2 s | 0 |
| `/tmp/t12-dev-link/runtime` (dev, attempt 1 — discarded, §T12-7) | 75.2 s | 0 |
| `/tmp/t12-dev-link/runtime` (dev, clean reconfigure after wipe) | 76.6 s | 0 |

Full-build walls side by side (535 edges each, `-j4`, exit 0 both):

| Step | Release | Dev |
|---|---|---|
| Full build wall | 710.0 s (11.8 min; start 07:53:58Z, last edge `[534/535 710.034]`) | 558.6 s (9.3 min; start 08:14:59Z, last edge `[534/535 558.625]`) |
| Runner link edge (`.ninja_log`) | 390.6 s | 0.5 s |
| Σ compile-edge time / 4 | 312.8 s | 551.1 s |
| Slowest edges | link 390.6 / `unity_176` 37.1 / `unity_73` 36.9 / `unity_214` 29.8 / `unity_78` 17.0 | `unity_73` 89.0 / `unity_176` 84.5 / `unity_214` 72.1 / `unity_78` 46.4 / `unity_195` 29.9 |
| Runner binary | 163,460,272 B `81bee6c5…` (= T6 bit-identical) | 138,787,392 B `758b1dc5…` |
| Tests binary | 5,433,640 B `a750bd53…` | 5,409,512 B `6c44db5d…` (links non-LTO `ps2_runtime`) |
| Contention | none (nearest peer write 03:42 local, 12 min before start) | none for the kept build (p1-link last write 04:12, 3 min before start) |
| Warnings | same `ld` duplicate-library warning + pre-existing `-Wswitch` as T1/T6 | same |

T6-baseline reproduce-or-explain (same flags, my own dirs):

| T6 cell | T6 | T12 Release | Disposition |
|---|---|---|---|
| Full build | 472 s | 710 s | Same flags, bit-identical output, slower wall. No peer edges in window (§T12-7). Unattributed environmental spread — extends T6 gaps 1–2 (same-batch compiles 2×: `unity_73` 18.6 s T6 vs 36.9 s here; link 330.4 s T6 vs 390.6 s here, inside T6's 313–397 incremental spread at the top edge) |
| (a) hot-cpp | 315 s (link 312.8 s) | not re-run on Release | Superseded by the dev measurement below (brief: cells on dev only) |
| (b) header | 658 s clean | not run | Skipped on both configs per the brief (dev (b) allowed to skip; tabled as not-run) |
| (c) test-cpp | 8 s | not re-run on Release | Superseded by the dev measurement below |
| (d) no-op | 0 s | not run | Floor unchanged by a link-flag config; not re-measured |

## T12-4. Incremental cells on dev ((a)+(c) only, per the brief)

Touches are mtime-only (content verified unchanged — same method as
T6): (a) `ps2xRuntime/src/lib/ps2_runtime.cpp`,
(c) `ps2xTest/src/ps2_memory_tests.cpp`.

| Cell | Dev wall | Exit | Rebuilt (timestamped edges) | T6 Release (same cell) |
|---|---|---|---|---|
| (a) hot `.cpp` | 5.9 s | 0 | 1 compile (1.4 s) + 1 `ar` + runner link (0.4 s) + tests link (4.0 s; keeps ThinLTO) — 5 edges | 315 s (runner link 312.8 s) |
| (c) test `.cpp` | 7.2 s | 0 | 1 compile (1.8 s) + 1 `ar` + tests link (5.3 s; no runner relink) — 4 edges | 8 s |
| (b) wide header | not run | — | — (brief allows skip; no dev (b) sample exists) | 658 s clean |

3-minute gate (180 s) on dev: (a) 5.9 s — under; (c) 7.2 s —
under. (b) unmeasured on dev.

## T12-5. Suite green on BOTH configs (total/passed/failed per config)

CWD `$R` both runs (T5 precedent), exit 0 both. Parsed per-face
table `diff`s clean between configs (`FACES_IDENTICAL`); raw logs
differ in 4 lines only (randomized `ps2recomp-mc0-*` tmpdir
suffixes, `t12-suite-{rel,dev}.log:708-711`).

| Face | Release | Dev |
|---|---|---|
| CodeGenerator | 56/56/0 | 56/56/0 |
| ElfAnalyzerHeuristics | 6/6/0 | 6/6/0 |
| PS2GS | 71/71/0 | 71/71/0 |
| PS2IopSubsystem | 7/7/0 | 7/7/0 |
| PS2Memory | 47/47/0 | 47/47/0 |
| PS2Recompiler | 20/20/0 | 20/20/0 |
| PS2RuntimeExpansion | 31/31/0 | 31/31/0 |
| PS2RuntimeIO | 11/11/0 | 11/11/0 |
| PS2RuntimeInterrupt | 8/8/0 | 8/8/0 |
| PS2RuntimeKernel | 40/40/0 | 40/40/0 |
| PS2SifDma | 16/16/0 | 16/16/0 |
| PS2SifRpc | 15/15/0 | 15/15/0 |
| PS2VU0Math | 44/44/0 | 44/44/0 |
| PS2VU1 | 40/40/0 | 40/40/0 |
| PadInput | 12/12/0 | 12/12/0 |
| R5900Decoder | 15/15/0 | 15/15/0 |
| **Total** | **439/439/0** | **439/439/0** |

Both match T5 AFTER (439/439/0) face-for-face. Zero dev-only
failures — no divergence to table from the suite.

## T12-6. Fork commit + push

| Item | Value |
|---|---|
| Commit | `7eed783` (`Config: PS2X_DEV_NO_THINLTO dev-build option skips ThinLTO on runner link chain (T12)`, +10/−0, `Orchestrated-By: Muse Code`) |
| Staged set | `ps2xRuntime/CMakeLists.txt` — named file only, verified; generated `M` never staged |
| `._*` / `__pycache__` | Purged before staging / removed; neither staged (ExFAT precedent) |
| `pull --rebase` | Refused on the unstaged generated runner file (T5/P9 precedent); pre-push fetch clean (`fork/ssx3 == 935a4eb`, no peer commits, nothing to replay) |
| Push | `git push fork ssx3` from the fork clone only (`935a4eb..7eed783`, fast-forward); `fork/ssx3 == 7eed783` |
| NEVER in ssx3 | No `git push` in ssx3 (evidence commit local only, §T12-11) |

## T12-7. Contention + waits record

Canonical log: `$W/P1/run/t12-waits.log` (copied here as
`t12-waits.log`).

| Window | Pre-check | What happened |
|---|---|---|
| 3 configures 03:48–03:53 | quiet (pgrep exit 1 + self-excluding ps) | no contention |
| Release full build 03:54–04:05 | quiet at start | no contention (peer-log scan: nearest write t6 03:42, p1 03:28 — 0 peer edges in window) |
| Dev build attempt 1, 04:09–04:13 | quiet at start (pgrep hit = T13's sleep-poller self-match, paired ps showed sleep only) | peer T13 `/tmp/p1-link` rebuild overlapped (p1-link log last write 04:12); T13's `pkill` pattern cross-fired and SIGTERM'd my ninja at `[317/535]` ("interrupted by user", T13's own message confirms). Build tree wiped; clean reconfigure; sample DISCARDED, not tabled as a wall |
| Dev full build (kept) 04:15–04:24 | quiet (same sleep-poller self-match only) | no contention (T13 stood down until my release per their message; p1-link silent after 04:12) |
| Cells (a) 04:25, (c) 04:26 | quiet each (sleep-poller self-match only) | no contention |
| Boots 04:27–04:31 | lease absent + `pgrep -x` exit 1 | 0 lease waits; single hold, both boots, immediate release |

Method notes: T13 runs a `sleep 270` poll loop whose command line
contains the literal `ninja`, so bare `pgrep -f ninja` exit-0'd on
it three times; every check paired it with a self-excluding `ps`
read showing a sleeper, never a build (T6 §T6-6 precedent).

## T12-8. Proof boots + emitter-vs-emitter ladder

Binaries: REL `81bee6c5…` 163,460,272 B (Release, ThinLTO on); DEV
`758b1dc5…` 138,787,392 B (dev, ThinLTO off). Env = `/tmp/t5-boot-base.py`
verbatim except docstring + `BIN`/`LOG`/`PS2X_DIAG_PARK_DIR`
(script diffs verified: `/tmp/t12-boot-{rel,dev}.py`).
`PS2X_DIAG_PARK=1` both; CWD `$W/P1/run`; ISO 3005415424 B + ELF
3890784 B (match T1/T5).

| Rung | REL (`boot-t12-rel.log`) | DEV (`boot-t12-dev.log`) | Delta |
|---|---|---|---|
| Lines / bytes | 205,533 / 36,319,145 | 207,452 / 36,694,283 | Throughput +0.9% |
| Run | 90 s foreground, SIGTERM, rc=0 | 90 s foreground, SIGTERM, rc=0 | None |
| `[diag:park]` | `:205526` → `/tmp/t12-park-rel/` (111,505 B json) | `:207445` → `/tmp/t12-park-dev/` (111,505 B json) | None |
| Stub lines / thread lines | 527 / 102 | 527 / 102 | None — exact |
| Threads (snapshot) | 1 WAIT29, 2 WAIT26, 3 WAIT30, 4 WAIT31, 5 WAIT32, 6 WAIT36 | identical (all six WAIT, same semas) | None — exact (same SIGTERM phase both) |
| Sched counts | t1 10510, t5 10484, t4 5244 | t1 10620, t5 10594, t4 5299 | TOL_OK ~1.0% |
| Sema creates | 37 | 37 | None — exact |
| RPC | 21 loads / 4 binds / 4 unclaimed calls / 1 sendcmd | Same | None — exact |
| Drops | 6× `dispatchSyscallOverride/KE_ERROR` | 6× byte-identical (`diff` clean) | None — exact |
| Hot-pc top | `0x41ea18` @ 953,381 (= T1's and T5's count) | `0x41ea18` @ 953,381 | None — exact |
| GS kicks/gif/copy | 1,266,008 / 145,392 / 161,571 | 1,279,428 / 146,932 / 163,276 | TOL_OK ~1.0% |
| Crash / FATAL | 0 / 0 | 0 / 0 | None |

D (`tools/ladder_diff.py` current = T9's tool, `T12/D.txt`, 1306 lines):
**1059 exact, 245 tol-ok (worst 1.4%), 0 info, 0 deltas → OK**,
rc=0. Zero `KEY_DELTA`/`COUNT_DELTA`; zero non-EXACT rows outside
`TOL_OK` (no SAMPLED/SATURATED/STALE/BLIND/TRUNC — both boots
parked the same thread phase, so every deterministic row is EXACT
and every throughput row is within tolerance).

Every non-EXACT row is a throughput row at ~1.0–1.4% (sema
wait/signal histories, hot-pc counts, gs, sched). No divergence
rows exist to table.

## T12-9. Adoption inputs (numbers only, no recommendation)

| Input | Release (ThinLTO on) | Dev (`PS2X_DEV_NO_THINLTO=ON`) |
|---|---|---|
| Full build wall (this session) | 710 s | 559 s |
| Full runner link edge | 390.6 s | 0.5 s |
| Incremental cell (a) hot-cpp | 315 s (T6; not re-run) | 5.9 s |
| Incremental cell (c) test-cpp | 8 s (T6; not re-run) | 7.2 s |
| Incremental cell (b) header | 658 s clean (T6) | not measured |
| Suite total/passed/failed | 439/439/0 | 439/439/0 (faces identical) |
| D (dev boot vs Release boot) | — | exit 0: 1059 exact / 245 tol-ok / 0 deltas |
| Divergence rows | — | none (suite + D) |
| Release-behavior change from the commit | — | link line byte-identical; Release binary bit-identical to T6's (`81bee6c5…`) |
| Runner binary size | 163,460,272 B | 138,787,392 B |

## T12-10. Gap rows

| # | Gap |
|---|---|
| 1 | No dev cell-(b) wide-header sample (brief allows the skip; (b) unmeasured on dev) |
| 2 | Release full-build wall 710 s vs T6's 472 s same-flags is unattributed (no peer edges in window; extends T6 gaps 1–2 — same-batch compile spread now 18.6–36.9 s rel, 89.0 s dev non-LTO codegen) |
| 3 | Single run per cell/build (brief-consistent for cells; builds likewise n=1 per config) |
| 4 | MSVC `/GL` + `/LTCG` flags untouched by the option (clang-only host; MSVC dev-link behavior unmeasured) |
| 5 | Dev tests binary still ThinLTO-links (4.0–5.3 s of the 5.9–7.2 s incremental walls); scoping the option wider was not measured |
| 6 | T11's run-to-exit had priority per the brief; T11 had already released the lease before my first boot check (0 waits), so no yield was exercised |

## T12-11. Exact commands

```
# worktree + configures (lease-free; pre-check quiet)
git -C $R worktree add --detach /tmp/t12-base 935a4eb
rsync -a --delete $R/ps2xRuntime/src/runner/ /tmp/t12-base/ps2xRuntime/src/runner/
cmake -S /tmp/t12-base -B /tmp/t12-nocommit -G Ninja <T1 flags>            # 74.6 s
cmake -S $R -B /tmp/t12-link/runtime -G Ninja <T1 flags>                  # 89.2 s
cmake -S $R -B /tmp/t12-dev-link/runtime -G Ninja <T1 flags> -DPS2X_DEV_NO_THINLTO=ON  # 75.2 s
# flags proof (lease-free)
ninja -C <dir> -t commands ps2xRuntime/ps2EntryRunner | tail -1            # x3, diff: base==rel byte-identical, dev minus -flto=thin
diff <(grep '^PS2X_' .../CMakeCache.txt | sort) ...                        # one added OFF line
# builds (pre-check before EVERY build; -j4 MAX)
cmake --build /tmp/t12-link/runtime --target ps2x_tests ps2EntryRunner -j4        # 710 s, exit 0
cmake --build /tmp/t12-dev-link/runtime --target ps2x_tests ps2EntryRunner -j4    # SIGTERM'd@317 by T13 pkill; wiped; reconfigured 76.6 s; rebuilt 558.6 s, exit 0
cd $R && /tmp/t12-link/runtime/ps2xTest/ps2x_tests                        # 439/439/0 rc=0
cd $R && /tmp/t12-dev-link/runtime/ps2xTest/ps2x_tests                    # 439/439/0 rc=0
touch $R/ps2xRuntime/src/lib/ps2_runtime.cpp; cmake --build /tmp/t12-dev-link/... # (a) 5.9 s
touch $R/ps2xTest/src/ps2_memory_tests.cpp; cmake --build /tmp/t12-dev-link/...   # (c) 7.2 s
# fork commit + push (fork clone only)
git add ps2xRuntime/CMakeLists.txt
git commit -- ps2xRuntime/CMakeLists.txt -m "Config: ... (T12)"            # 7eed783
git fetch fork ssx3; git pull --rebase fork ssx3                          # refused (generated M), pre-fetch clean
git push fork ssx3                                                         # 935a4eb..7eed783
# proof (lease T12 held 04:27-04:31 local only; 0 waits)
printf 'T12\n' > /tmp/ssx3-p-lane-lease; python3 /tmp/t12-boot-rel.py      # 90 s, rc=0
python3 /tmp/t12-boot-dev.py                                                # 90 s, rc=0
rm /tmp/ssx3-p-lane-lease
# D (lease released)
python3 $R/tools/ladder_diff.py /tmp/t12-park-rel/park-snapshot.json \
  /tmp/t12-park-dev/park-snapshot.json --names rel,dev                    # exit 0, 1059/245/0/0
# evidence (ssx3, no push)
git add -f local/research/T12/...; git commit -m "[T12] ..."              # local only
```

Receipt paths: `$W/P1/run/boot-t12-{rel,dev}.log`,
`$W/P1/run/t12-waits.log`, `/tmp/t12-{rel,dev}-build*.log`,
`/tmp/t12-dev-cell-{a,c}.log`, `/tmp/t12-suite-{rel,dev}.log`,
`/tmp/t12-boot-{rel,dev}.py`, `/tmp/t12-park-{rel,dev}/`,
`/tmp/t12-linkline-{nocommit,rel,dev}.txt`,
`/tmp/t12-cache-{nocommit,rel}.txt`, `/tmp/t12-D.txt`,
`local/research/T12/` (this dir). Build trees retained at
`/tmp/t12-link/`, `/tmp/t12-dev-link/`, `/tmp/t12-nocommit/`,
`/tmp/t12-base` (not committed).

## T12-12. Evidence files (this dir, standalone)

`REPORT.md` (this file), `D.txt` (1306 lines),
`park-snapshot-rel.json`, `park-snapshot-dev.json` (111,505 B
each), `t12-linkline-{nocommit,rel,dev}.txt`,
`t12-cache-{nocommit,rel}.txt`, `t12-rel-build.log`,
`t12-dev-build2.log`, `t12-dev-cell-{a,c}.log`,
`t12-suite-{rel,dev}.log`, `t12-waits.log` (copy of canonical).

## T12-13. What I could not do

- Run dev cell (b) (brief allows the skip; gap 1).
- Attribute the 472→710 s Release full-build spread (gap 2; no
  peer edges in window, bit-identical output).
- Exercise a lease yield to T11 (lease already free; gap 6).
- One session, inside the 4 h box.
