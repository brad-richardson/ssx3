# T14 — Dev cell-(b): wide-header incremental on the dev config (closes the adoption table)

Tables, no verdicts. Brief `local/muse/prompts/T14.md`.
`local/research/T12/REPORT.md` re-read first (all of it): T12 gap 1 is
this brief — cell (b) wide-header incremental was measured on Release
(658 s clean) but never on dev. `local/research/T6/REPORT.md` §T6-2/§T6-4
re-read: the (b) method below repeats T6 verbatim (same header,
mtime-only touch with content check, clean vs contended handling).
This is a MEASUREMENT brief: one cell, no fork changes, no boots.

`R=/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp` (fork, branch
`ssx3`), `W=/Volumes/Extreme SSD/ps2recomp-spike`, `RUN=$W/P1/run`.
Peer lanes concurrent; build etiquette observed throughout (§T14-4).

Headline receipts: dev cell-(b) 640.9 s wall (exit 0, 345 edges:
PCH + 338 compiles + 3 `ar` + 2 links + glob re-check); runner link
edge 0.6 s (was 396.7 s on Release); compiles own the wall (Σ
2527.2 s / 4 ≈ 631.8 s = 98.6%); (b) ratio Release 658 s vs dev
640.9 s = 1.03×; header sha `566c30a6…` identical before touch,
after touch, and after build.

## T14-0. Setup

| Item | Value |
|---|---|
| Date / window | 2026-09-20 08:37–09:05Z (≈28 min, inside the 4 h box) |
| Host | Apple M4, 10 CPUs, macOS; ninja 1.13.2; `/opt/homebrew/opt/llvm/bin/clang(++)` |
| ssx3 HEAD | `fc653eb` (start; untouched until the evidence commit) |
| Fork HEAD start/end | `7eed7838c21c4227271b065d9670f85373635894` / same (T12's commit, as expected; unmoved) |
| Fork worktree | `M ps2xRuntime/src/runner/register_functions.cpp` (pre-existing generated, identical both ends; never staged) |
| Build dir | `/tmp/t12-dev-link/runtime` (REUSED from T12 — verified intact, not reconfigured) |
| Reuse proof | `PS2X_DEV_NO_THINLTO:BOOL=ON` in its `CMakeCache.txt`; `ninja -t commands` runner link 20,283 B with zero `-flto=thin` (evidence `t14-linkline-dev.txt`; = T12 Release 20,294 B minus the 11 B ` -flto=thin`); tests link keeps `-flto=thin` |
| Targets | `ps2x_tests ps2EntryRunner` (T1's line), `-j4` MAX |
| No-lease rule | No boots, no `adb`; zero fork commits; no `git push` in ssx3 |

## T14-1. Method (T6 §T6-2/§T6-4 verbatim)

| Step | T6 (b) | T14 (this run) |
|---|---|---|
| Header | `ps2xRuntime/include/ps2_log.h` | Same file |
| Touch | mtime-only, content verified unchanged | `touch` only; sha `566c30a6…e0` identical before touch, after touch (`2026-09-20T04:48:20-0400`), and after build |
| Header mtime at start | — | `2026-09-20T03:31:16-0400` (T6's touch; untouched since) |
| Per-step timestamps | `NINJA_STATUS='[%f/%t %e] '` | Same |
| Durations | Cross-checked against `.ninja_log` | Same (excerpt lines 546–890, evidence `t14-ninja-log-excerpt.txt`) |
| Contended handling | First run contended → kept as contended sample + clean rerun, table both | Same rule armed; trigger is mid-run peer-BUILD contention (T6: 329 peer edges); run had 0 peer build edges → single sample, no rerun (§T14-4) |
| Wall source | Last-edge `%e` + date | `[344/345 640.935]` + `date +%s` (641 s) |

## T14-2. Dev cell-(b) result + side-by-side with T6 Release (b) clean

| Cell | Wall | Exit | Rebuilt | Contention |
|---|---|---|---|---|
| Dev (b), this run | 640.9 s (10.7 min; start 08:48:20Z, last edge `[344/345 640.935]`) | 0 | PCH + 338 compiles + 3 `ar` + 2 links + glob re-check (345 edges; 344 `[n/345]` + `[0/2]`) | 0 peer build edges in window (pre-check `pgrep` exit 1 both; p1-link silent since 04:40); T13 boot overlapped whole window (lease T13; runner 33–110% CPU) — §T14-4 |
| Release (b) clean (T6, cited) | 658 s (11.0 min) | 0 | PCH + 338 compiles + 3 `ar` + 2 links (345 edges) | none (0 peer edges) |
| Release (b) first (T6, cited) | 844 s | 0 | same 345-edge set | CONTENDED (peer p1-link 329 edges inside window) |

3-minute gate (180 s) on dev: (b) 640.9 s — over (same gate outcome
as Release). Warnings: same pre-existing `-Wswitch` + `ld`
duplicate-library warning as T1/T6/T12.

## T14-3. Dominance table (which step owns the dev-(b) wall)

Dev (b), 640.9 s wall (`t14-dev-cell-b.log` + `t14-ninja-log-excerpt.txt`
original line numbers):

| Phase | Duration | Share | Line |
|---|---|---|---|
| PCH rebuild (`cmake_pch.hxx.pch`, 14534→16093) | 1.6 s | 0.2% | 584 |
| 338 compiles (Σ edge 2527.2 s ÷ 4) | ≈631.8 s parallel | 98.6% | 546–890 |
| slowest batch `unity_73` | 137.6 s | (inside parallel span) | 842 |
| `unity_176` / `unity_214` / `unity_78` / `unity_195` | 109.4 / 89.5 / 66.7 / 36.9 s | (inside parallel span) | 753 / 693 / 817 / 704 |
| `unity_0` (giant-TU batch) / `unity_2` (last compile) | 15.2 / 20.7 s | (inside parallel span) | 888 / — |
| `ar` × 3 (0.1 + 0.2 + 0.2) | 0.5 s | 0.1% | 583 / 587 / 885 |
| link `ps2x_tests` (625332→635126; overlapped with `unity_0`/`unity_2` tail) | 9.8 s | 1.5% | 887 |
| link `ps2EntryRunner` (640290→640935, serial tail) | 0.6 s | 0.1% | 890 |

Release-vs-dev dominance side by side (Release cited from T6 §T6-4):

| Phase | Release (b) 658 s | Dev (b) 640.9 s |
|---|---|---|
| PCH | 1.2 s (0.2%) | 1.6 s (0.2%) |
| 338 compiles (Σ/4) | 1018 s / 4 ≈ 250 s (38%) | 2527.2 s / 4 ≈ 631.8 s (98.6%) |
| slowest batch `unity_73` | 49.2 s | 137.6 s |
| `unity_0` (giant-TU batch) | 14.2 s | 15.2 s |
| `ar` × 3 | ≤0.3 s (0.0%) | 0.5 s (0.1%) |
| link `ps2x_tests` | 12.0 s (1.8%) | 9.8 s (1.5%) |
| link `ps2EntryRunner` | 396.7 s (60.3%) | 0.6 s (0.1%) |

The (b) ratio row: Release 658 s vs dev 640.9 s = **1.03×**.
Step owning dev-(b): compiles (98.6% of wall); runner link fell from
60.3% (Release) to 0.1% (dev).

Same-config batch reference (dev full build, T12 §T12-3, uncontended,
cited for the contention record — not a verdict):

| Batch | T12 dev full | T14 dev (b) | Ratio |
|---|---|---|---|
| `unity_73` | 89.0 s | 137.6 s | 1.55× |
| `unity_176` | 84.5 s | 109.4 s | 1.29× |
| `unity_214` | 72.1 s | 89.5 s | 1.24× |
| `unity_78` | 46.4 s | 66.7 s | 1.44× |
| `unity_195` | 29.9 s | 36.9 s | 1.23× |

## T14-4. Contention + waits record

Canonical log: `$W/P1/run/t14-waits.log` (copied here as
`t14-waits.log`).

| Window | Pre-check | What happened |
|---|---|---|
| 04:37–04:48 wait | peer build active at first check | T13 `/tmp/p1-link` rebuild (`cmake --build -j4`, PID 78237/78238) overlapped; waited ~11 min per etiquette (logged). No self-match issue: `pgrep -f` + self-excluding `ps` paired every check (T6 §T6-6 / T12 §T12-7 method; T13's `sleep`-poller noted, never matched as a build) |
| 04:40 | — | Peer build done (link edge 337.7 s, binary `81bee6c5…` == Release bit-identical); T13 claimed lease 04:41 for boots |
| 04:48:11 pre-build | quiet (`pgrep -f ninja` exit 1 + `pgrep -f cmake --build` exit 1, `ps` confirms no builds; load 2.28) | Started cell-(b). T13 boot active (lease T13, runner ~39% CPU) — not a build, noted |
| cell-(b) 04:48:20–04:59:01 | quiet at start | exit 0, wall 641 s. 0 peer build edges in window (nearest `.ninja_log` write p1-link 04:40, 8 min before start). T13 boot (PID 82288) overlapped the whole window at 33–110% CPU with GB-scale log writes to the shared SSD; load 8–10 mid-run. Batch times vs the T12 dev full-build reference are tabled in §T14-3 for the record |
| rerun decision | — | No rerun: the brief's trigger is mid-run peer-BUILD contention (T6 precedent: 329 peer edges in-window); 0 here. The 1.23–1.55× batch ratios sit inside the documented unattributed-spread envelope (T6 gaps 1–2: link 313–397 s, `unity_73` 18.6–49.2 s uncontended; T12 gap 2: same-batch 2× across sessions) — tabled, not attributed |

## T14-5. Adoption-inputs refresh (full table, no verdict)

Side-by-side: Release (T6/T12 numbers, cited not re-run) vs dev
(T12 (a)/(c) + this run's (b)). Fills T12 gap 1.

| Input | Release (ThinLTO on) | Dev (`PS2X_DEV_NO_THINLTO=ON`) |
|---|---|---|
| Full build wall (T12 session) | 710 s | 559 s |
| Full runner link edge | 390.6 s | 0.5 s |
| Incremental cell (a) hot-cpp | 315 s (T6; not re-run) | 5.9 s (T12) |
| Incremental cell (b) wide header | 658 s clean (T6; 844 s contended first run) | 640.9 s (this run; §T14-2/§T14-3) |
| Incremental cell (c) test-cpp | 8 s (T6; not re-run) | 7.2 s (T12) |
| 3-min gate on dev | (a) over, (b) over, (c) under | (a) 5.9 s under, (b) 640.9 s over, (c) 7.2 s under |
| Suite total/passed/failed | 439/439/0 (T12) | 439/439/0, faces identical (T12) |
| D (dev boot vs Release boot) | — | exit 0: 1059 exact / 245 tol-ok (worst 1.4%) / 0 deltas (T12) |
| Divergence rows | — | none (suite + D) (T12) |
| Release-behavior change from the commit | — | link line byte-identical; Release binary bit-identical to T6's (`81bee6c5…`) (T12); reuse re-verified this session (runner link 20,283 B, zero `-flto=thin`) |
| Runner binary size | 163,460,272 B | 138,787,392 B |
| Tests binary size | 5,433,640 B | 5,409,512 B |

The (b) ratio row: 658 / 640.9 = **1.03×** (Release : dev).
Dev-(b) owner: compiles at 98.6% of wall (Release-(b) owner: runner
link at 60.3%).

Gap rows (anything unmeasured that an adoption decision would still
want — named, not run):

| # | Gap |
|---|---|
| 1 | Single run per cell/build everywhere (T6/T12/T14) — no within-cell variance estimate (extends T12 gap 3) |
| 2 | T13 boot overlapped the whole dev-(b) window (CPU ~0.3–1.1 cores + GB-scale log I/O on the shared SSD); its effect is unseparated from environmental spread (batch ratios 1.23–1.55× vs the n=1 T12 dev full reference — §T14-3/§T14-4) |
| 3 | Compile-wall spread unattributed (extends T6 gaps 1–2, T12 gap 2): dev `unity_73` 89.0 s (T12 full) vs 137.6 s here; no CPU temp/frequency/load/I/O logging |
| 4 | Release full-build wall 710 s (T12) vs 472 s (T6) same-flags still unattributed (T12 gap 2 carried); Release (a)/(c) not re-run since T6 |
| 5 | MSVC `/GL` + `/LTCG` flags untouched by the option (T12 gap 4 carried; clang-only host) |
| 6 | Dev tests binary still ThinLTO-links (4.0–9.8 s across T12/T14 samples); scoping the option wider not measured (T12 gap 5 carried) |

## T14-6. Exact commands

```
# reuse verify (lease-free; peer p1-link build active → waited, §T14-4)
grep -E '^PS2X_DEV_NO_THINLTO' /tmp/t12-dev-link/runtime/CMakeCache.txt   # ON
ninja -C /tmp/t12-dev-link/runtime -t commands ps2xRuntime/ps2EntryRunner | tail -1  # 20283 B, zero -flto=thin
# pre-check before EVERY build (pgrep + self-excluding ps; -j4 MAX)
pgrep -f ninja; pgrep -f "cmake --build"                                  # exit 1 both
ps aux | grep -E '[n]inja -j|[c]make --build /tmp'                        # no peer builds
# cell-(b) (T6 method verbatim)
shasum -a 256 $R/ps2xRuntime/include/ps2_log.h                            # 566c30a6…e0 before
touch $R/ps2xRuntime/include/ps2_log.h; shasum -a 256 $R/.../ps2_log.h   # same after (mtime-only)
NINJA_STATUS='[%f/%t %e] ' cmake --build /tmp/t12-dev-link/runtime --target ps2x_tests ps2EntryRunner -j4  # 640.9 s, exit 0
shasum -a 256 $R/ps2xRuntime/include/ps2_log.h                            # same after build
# breakdown (from .ninja_log lines 546-890)
awk 'NR>=546 && NR<=890' /tmp/t12-dev-link/runtime/.ninja_log            # excerpt + line refs
# evidence (ssx3, no push)
git add -f local/research/T14/...; git commit -m "[T14] ..."             # local only
```

Receipt paths: `$W/P1/run/t14-waits.log`,
`/tmp/t14-dev-cell-b.log`, `/tmp/t14-ninjalog-excerpt.txt`,
`/tmp/t14-linkline-dev-check.txt`, `/tmp/t14-report-skeleton.md`
(draft notes), `local/research/T14/` (this dir). Build tree retained
at `/tmp/t12-dev-link/` (not committed; `.ninja_log` now 890 lines).

## T14-7. Evidence files (this dir, standalone)

`REPORT.md` (this file), `t14-dev-cell-b.log` (43,882 B raw build
log), `t14-ninja-log-excerpt.txt` (345 lines, original line numbers
546–890), `t14-linkline-dev.txt` (20,283 B runner link line),
`t14-waits.log` (copy of canonical).

## T14-8. What I could not do

- Run a second dev-(b) sample (brief's rerun trigger — mid-run
  peer-build contention — not met: 0 peer build edges; gap 1–2).
- Attribute the 1.23–1.55× batch ratios vs the T12 dev full-build
  reference (boot overlap vs environmental spread; gap 2–3 — no
  temp/freq/I/O logging, same as T6/T12).
- Re-run Release cells (brief: cited not re-run; gap 4).
- One session, inside the 4 h box.
