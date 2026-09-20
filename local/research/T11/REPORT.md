# T11 report — run-to-exit: cap at 600 s, N > 29,469 (1 boot, read-only miners)

Brief `local/muse/prompts/T11.md`. Tables, no verdicts.
Stale-reading guard: `local/research/T10/REPORT.md` §T10-4 (step 3c
is this brief — no readable bound in-trace, `N` goes empirical via
run-to-exit) + P1 REPORT Part 31 §P31-6c (5 first-post-phase
signatures; the brief's "P31-6d" label points at the §P31-6d 600 s
table, signatures live in §P31-6c) + Part 30 (P1ag's 300 s absence
window this run extends).

`W=/Volumes/Extreme SSD/ps2recomp-spike`, `R=$W/PS2Recomp` (fork,
branch `ssx3`), `LOG=$W/P1/run/boot-t11-1.log` (1,036,373 lines,
184,691,472 B), `T=$W/P1/run/ps2_log-t11-1.txt` (77,374,859 lines,
2,748,206,218 B). `$R`-relative paths below unless noted. Zero fork
changes; no `adb`.

Headline readings: the 600 s cap hit with main still in the hash
phase (block-118 sample mid-syscall, pump balanced, trace cut
mid-chain at modal slot 8) — a third absence window with a tighter
bound, `N` > 29,469. All five first-post-phase signatures absent
over the full window. Fixed baselines reproduce: 54-frame modal
dispatcher cycle (REP+53, 29,393/29,468 gaps byte-identical, same 31
patterns, same 0–74 ramp ordinals); per-invocation 20/19/1/2534 over
28 machine-identical 1,000-chunks; stubs 222 ×117 blocks; sema-30
4w/3s parked (line numbers bit-identical to P1af); FRR ×29,469 with
0 deviations. Wall rate decays smoothly 64→36/s across the window
while every guest-denominated ratio holds fixed (dormant/pump 2.000,
394/inv 20.00, 395/inv 19.00, d_gif/d_dma 0.0270).

## T11-0. Lease / tree-state / build record

| Item | Value |
|---|---|
| ssx3 HEAD at T11 start | `66a156abfae3a513d11e12efd1a6afa5abbe3269` (`T10 gate read passes …`) |
| ssx3 working tree at start | clean (no output) |
| Fork HEAD at T11 | `935a4ebf6db16c4057c30f5dd5cdba23af0ff3b6` (same as T10; T9 landed, `ssx3`) |
| Fork working tree | `M ps2xRuntime/src/runner/register_functions.cpp`, `?? tools/__pycache__/` (foreign, untouched) |
| Fork commits by T11 | 0; fork `git pull/push`: never run |
| Sidecar purge (ExFAT precedent, §P2-1) | `find $R -name "._*" -delete` (45 files, 5 non-`.git`); `git status` unchanged after |
| Rebuild | `cmake --build /tmp/p1-link/runtime --target ps2EntryRunner -j4`, exit 0 (`/tmp/t11-build.log`, 18 warning lines — same count as P1ag) |
| Binary | `81bee6c5c0740dafbb910fdfd9c62de8185b816372a0658603dc38c41252d40f`, 163,460,272 B (sha IDENTICAL to P1ag's — T1 emitter bytes now committed, same content) |
| Boot env | P1ag verbatim (`PS2X_DIAG_394ED0=1` kept; `PS2X_DIAG_PARK` unset); script diff = LOG name + `SECS=600` + docstring only (diff-verified) |
| Boots | 1 of 2 used (no exit → no ≤90 s confirm; P1ag §P30-6 precedent) |
| Wall | 2026-09-20 ~07:10–08:05Z (~55 min active), inside the 4 h box |
| ssx3 evidence commit | below (`[T11]`, no push) |

Lease record (`$W/P1/run/t11-waits.log`, 4 lines):

| Event | Value |
|---|---|
| Pre-claim checks (07:29:24Z) | Lease absent; `pgrep -x ps2EntryRunner` exit 1; sha `81bee6c5…`; ISO 3005415424 B + ELF 3890784 B present; 547 Gi free |
| Claim | `printf 'T11\n' > /tmp/ssx3-p-lane-lease` 07:29:29Z, immediately before boot |
| Boot | 600 s foreground, SIGTERM rc=-15 (script exit 241); LOG 1,036,373 lines, 184,691,472 B; trace copied to T (77,374,859 lines, 2,748,206,618 B… see note) |
| Release | 07:39:44Z, right after boot (analysis needs no lease); verified absent; `pgrep -x` exit 1 |
| Waits | None (no foreign P-lane holder all session) |
| Live monitor | `/tmp/t11-monitor.py`, 15 s polls for the 5 signatures + trace-stall trip; 20 polls, no trigger; exit 10 (cap-or-end) |

Note: trace byte size is 2,748,206,218 B (the "…618" above is a
typo carried in the waits log line only, not a second measurement).

Monitor-coverage gap (tabled, no consequence for the cap result):
the monitor process started 07:34:59Z (tool-launch latency), so live
exit polling covered wall ~330–600 s only; the first ~330 s is
covered post-hoc (full log+trace mined). No trigger fired in the
monitored window; post-hoc confirms no exit signature in EITHER
window, so the missed early-kill opportunity cost lease time only
(600 s held, within the allowance).

## T11-1. Exit-or-cap table (all 5 signatures absent → cap case)

| # | Signature (brief wording) | Receipt | Reading |
|---|---|---|---|
| 1 | New stub phase | 222 ×117 blocks (2–118); b0=961, b1=497 preamble | absent past block 5 (steady one block earlier than P1ag's block 5 — tabled in §T11-4) |
| 2 | 4th sema-30 signal + thread-3 release | 7 `id=30` lines, 4w/3s, ends parked; t3 WAIT-30 ×118 (blocks 1–118) | absent |
| 3 | `0x362DE8` invocation halt | 29,469 / 29,469 balanced; last enter @77,374,481 of 77,374,859 (378 post lines = chain closes); pump sema traffic cut mid-line at SIGTERM | flowing at cap, absent |
| 4 | New caller | Single caller `sub_00363490` ×29,469; any-other 0 | absent |
| 5 | dma/gif slope break | d_gif/d_dma 0.0270 ± 0.0002 on all 77 tick deltas | absent (smooth wall-rate decay, ratio fixed — §T11-3) |

End state at SIGTERM: main sample block 118 = status 1 mid-syscall
@`0x423dc8` (not parked); trace cut mid-chain at modal slot 8
(`382650`→`382688`→`423dd0` open, live=3); boot log cut mid-line
(`…invKind=`, no trailing newline); 29w/s29 29470/29470 balanced,
31w/s31 29471/29470 (+1 in-flight).

## T11-2. Bound table (cap case — the tighter bound)

| Window | Cap | Final invocation ordinal | Bound |
|---|---|---|---|
| P1af 90 s | SIGTERM | 5,289 | N > 5,289 |
| P1ag 300 s | SIGTERM | 13,108 | N > 13,108 |
| **T11 600 s** | **SIGTERM** | **29,469** | **N > 29,469** |

Growth arithmetic (P1ah method: pump proxy `(29w+31w)/2` per 5 s
block; in-block proxy 29,444 + pre-block-0 25 = 29,469 =
trace enters exactly; pre-block-0 25 vs P1ag's 14 = faster boot):

| Slice | Blocks | Wall (≈) | Pump waits | Invoc proxy | Rate (/s) | 394ED0 (20×) | 395000 (19×) |
|---|---|---|---|---|---|---|---|
| Pre-block-0 | — | 0–~5 s | — | 25 | — (boot) | 500 | 475 |
| 0 | 0–11 | 0–60 s | 7,688 | 3,844 | 64.07 | 75,542† | 71,698† |
| 1 | 12–23 | 60–120 s | 7,234 | 3,617 | 60.28 | 72,340 | 68,723 |
| 2 | 24–35 | 120–180 s | 7,205 | 3,602 | 60.04 | 72,040 | 68,438 |
| 3 | 36–47 | 180–240 s | 7,194 | 3,597 | 59.95 | 71,940 | 68,343 |
| 4 | 48–59 | 240–300 s | 6,798 | 3,399 | 56.65 | 67,980 | 64,581 |
| 5 | 60–71 | 300–360 s | 6,134 | 3,067 | 51.12 | 61,340 | 58,273 |
| 6 | 72–83 | 360–420 s | 4,304 | 2,152 | 35.87 | 43,040 | 40,888 |
| 7 | 84–95 | 420–480 s | 4,386 | 2,193 | 36.55 | 43,860 | 41,667 |
| 8 | 96–107 | 480–540 s | 3,990 | 1,995 | 33.25 | 39,900 | 37,905 |
| 9 | 108–118 | 540–595 s | 3,956 | 1,978 | 35.96 | 39,560 | 37,582 |
| Sum vs trace | | | | 29,469 | 49.12 mean | 588,042 / 588,042 exact | 558,573 / 558,573 exact |

† Slice 0 ramp-adjusted (−1,338 each, P1ah §P31-1f rule); derived
sums reconcile to BOTH trace totals exactly.

Longer-window cost (numbers only):

| Item | Value |
|---|---|
| Lease cost | linear: 600 s held for 600 s wall (~10.3 min incl. overhead) |
| Trace growth | 4.58 MB/s → ~16.5 GB/h |
| Boot-log growth | 0.31 MB/s → ~1.1 GB/h |
| Disk bound (547 Gi free) | ~31 h of receipts before the volume fills |
| Miner cost (measured) | one 2.75 GB trace pass ≈ 1–3 min (`grep -c` ×10 ≈ 4 min; `t11-trace.py` ≈ 100 s; `t11-cycle.py` ≈ 110 s) |
| What a longer window cannot supply | the driver-loop bound `N` (§P31-6b receipt, still unbuilt); probe bodies past n=19999 (cap) |

## T11-3. Rate shape + uniform-scaling check (no inflection, smooth decay)

Wall rates decay ~64→36/s with onset window ~240–360 s (slice 4
dips, slice 5 transitional, slice 6 settles); dma deltas mirror
(~25.5k → ~9.5k per tick). Every guest-denominated ratio holds
fixed across the decay (same signature class as P1ag's step,
opposite direction):

| Quantity | Kind | Pre-decay (slices 0–3) | Post-decay (slices 6–9) | Factor |
|---|---|---|---|---|
| Handshake / 5 s | wall rate | ~300–315 | ~165–200 | ~0.58× |
| Dormant / 5 s | wall rate | ~600–630 | ~330–400 | ~0.58× |
| d_dma / tick | wall rate | ~23k–26k | ~8.5k–11k | ~0.40× |
| d_gif / tick | wall rate | ~630–700 | ~230–295 | ~0.40× |
| Dormant / 29w | guest ratio | 2.000 (slices 2–3; 2.09/2.07 in 0–1, P1af-like boot surplus) | 2.0000 all slices | 1.00× |
| 394ED0 / invoc | guest ratio | 20.00 | 20.00 | 1.00× |
| 395000 / invoc | guest ratio | 19.00 | 19.00 | 1.00× |
| Trace lines / invoc | guest ratio | 2,534 | 2,534 | 1.00× |
| d_gif / d_dma | guest ratio | 0.0270 ± 0.0002 | 0.0270 ± 0.0002 | 1.00× |
| Stub distinct | guest state | 222 | 222 | same |
| `0x362DE8` caller set | guest state | {`0x363490`} | {`0x363490`} | same |
| Sema-30 shape | guest state | parked (4w/3s) | parked (4w/3s) | same |

## T11-4. Baselines-kept table (per-row exact-vs-baseline)

| Baseline (source) | T11 observed | Row |
|---|---|---|
| 54-frame modal cycle REP+53 (T10) | modal len 53 ×29,393/29,468 gaps; all 53 slots byte-identical; class uniformity 29,393/29,393 per `376938` slot | exact |
| 31 gap patterns, ramp ordinals 0–74 (T10) | 31 patterns; non-modal = exactly ordinals 0–74; variant first_reps 36/52/63/1/27/29/0/10–26/28/34/35/37/51/74 = P1ag's list | exact |
| Class offsets +5/+15/+16/+18/+42/+52 (T10) | C3 +5 ×29,469; C7 +15 ×29,468; C1a#1 +16 ×29,468; C1b +18 ×29,468; E @42 ×29,393; C1a#2 @52 ×29,393 | exact |
| E-double gaps 51–62; C1a-extra 0–50 (T10) | E-double ordinals [51..62]; C1a×3 in 51 gaps | exact |
| 20/19/1/2534 per invocation (P1ah) | 28 chunks 20000/19000/1000/2534000 + chunk-0 18642/17643/1000/5234034 (bit-exact) + tail +20/+19 SIGTERM structure | exact |
| Stubs 222 (P1ag) | 222 ×117 (blocks 2–118) | exact past preamble |
| Stub preamble b0–b4 (P1ag: 687/250/283/674/268→222 @b5) | b0=961, b1=497, steady @b2 | DEVIATION (faster boot; steady 3 blocks earlier) |
| Sema-30 4w/3s parked (P1ag) | 7 lines, 4w/3s, ends parked | exact (line numbers 643/645/646/706/6975/7025/7227 = P1af's, uncontended shift) |
| FRR ×N, 0 deviations (T8) | FRR ×29,469, 0 deviations; `363490` 88,407/88,407 = 3× | exact |
| Single caller `0x363490` (P1ah) | ×29,469, other 0 | exact |
| Probe change points 104/140/162 (P1ah) | 104/140/162; `total→0x14` sat.; cap line @:62113 (P1ag :62604) | exact |
| Probe NULL-head 3135 (P1ag) | 3136 | DEVIATION +1 (one extra NULL-head touch) |
| Probe pool drops 1066, arenas 1, buckets 5 | 1066 / 1 (`0x8095f0`) / 5, CYCLE@ 0 | exact |
| Drops 6 @:68–73 KE_ERROR 0x5b | 6 @:68–73, same site | exact |
| RPC unhandled 4 | 4 @:711/:1056/:1062/:5142 (4th @5142 vs P1af 5143 / P1ag 5315 — volume shift) | exact count, shifted line |
| SendCmd 1 / handshake 2 / `0x3C45C0` 0 | 1 @:1052 / 2 / 0 | exact |
| CD 810 `0x10`→`0x4311f` | 810, same span, last @:7177 | exact |
| SIF 21 loads id 1–21 | 21, id 1–21 in order, last @:1055 | exact |
| Creates 37 / `-1` waits 0 | 37 (max 37) | exact |
| Driver-entry 98 | 98 | exact |
| GS 96 / copy 64 / gif 48 / drawing=1 96 | 96 / 64 / 48 (=126 `gif` lines − 78 tick lines) / 96 | exact |
| Missing-target 1, JALR `0x2322d4→0x395730` | 1 @:660, same bytes | exact |
| Crash / FATAL / presented frame 0 | 0 / 0 / none | exact |
| Thread-3: RUNNING pre-pump → WAIT-30 | RUNNING ×1 (block 0, pc `0x416934`) → WAIT-30 ×118 | DEVIATION in transient (P1ag: 2 RUNNING @`0x3232b8`/`0x323ebc`; faster pump onset) |
| Thread-6: WAIT-36 all blocks | WAIT-36 ×119 | exact |
| First `0x362DE8` enter @ trace line 19,385 | @19,385 | exact |
| Stack mismatches 0 / max depth 29 | 0 / 29 | exact |
| Live frames at EOF 2 (C3-live @slot 5) | 3 (`382650` d0 + `382688` d1 + `423dd0` d2 @slot 8; C3 closed) | DEVIATION (later SIGTERM cut point; post-region n=8 vs 5) |
| Pre-first-rep 294 frames, 3×C1a+1×E | 294, 3×C1a+1×E | exact |

Main pc-sample histogram (119 samples: 65 RUNNING + 18 mid-syscall
+ 36 WAIT-29; end sample block 118 = mid-syscall, not parked):

| status | pc | n | Attribution |
|---|---|---|---|
| 0 RUNNING | `0x186c04` | 18 | `sub_00186A08+0x1fc` |
| 0 RUNNING | `0x2c6074` | 17 | `sub_002C5570+0xb04` |
| 0 RUNNING | `0x38f364` | 9 | `sub_0038F300+0x64` |
| 0 RUNNING | `0x39b72c` | 8 | `sub_0039AE98+0x894` |
| 0 RUNNING | `0x38f354` | 4 | `sub_0038F300+0x54` |
| 0 RUNNING | `0x39e72c` | 2 | `sub_0039E6B8+0x74` |
| 0 RUNNING | `0x376b64` | 2 | `sub_00376938+0x12c` |
| 0 RUNNING | `0x3778ec` | 1 | `sub_00376938+0xfb4` |
| 0 RUNNING | `0x397fc4` | 1 | `sub_00397DF8+0x1cc` |
| 0 RUNNING | `0x397ef4` | 1 | `sub_00397DF8+0xfc` |
| 0 RUNNING | `0x3988dc` | 1 | `sub_00398798+0x144` |
| 0 RUNNING | `0x3a0714` | 1 | `sub_003A04F0+0x224` |
| 1 mid-syscall | `0x423dc8` | 17 | syscall entry |
| 1 mid-syscall | `0x423de8` | 1 | syscall wait addr |
| 2 WAIT-29 | `0x423de8` | 36 | pump sample |

CD/SIF/GS/RPC silence audit (all lasts in blocks 0–2; zero new
events in blocks 3–118):

| Source | n | Last line | Last block (≈wall) | New past block 2 |
|---|---|---|---|---|
| CD `lbn=` | 810 | 7,177 | 2 | none |
| SIF loads | 21 | 1,055 | 0 | none |
| GS kicks | 96 | 2,639 | 1 | none |
| RPC unhandled | 4 | 5,142 | 2 | none |
| Sema-30 events | 7 | 7,227 | 2 | none |

## T11-5. Absence-window ladder (T11 vs P1ag)

| Rung | P1ag (300 s) | T11 (600 s) |
|---|---|---|
| Lines / bytes | 475,304 / 84,053,701 | 1,036,373 / 184,691,472 |
| Trace lines / bytes | 35,916,072 / 1,275,797,618 | 77,374,859 / 2,748,206,218 |
| Stub / thread / syscall blocks | 59 / 59 / 59 | 119 / 119 / 119 |
| Park onset | NONE (222 ×54) | NONE (222 ×117) |
| Thread-1 | 41 RUN + 12 mid + 6 WAIT-29 (end: WAIT-29) | 65 RUN + 18 mid + 36 WAIT-29 (end: mid-syscall) |
| Thread-3 | WAIT-30 ×56 + RUN b0–b1 | WAIT-30 ×118 + RUN b0 |
| Thread-6 | WAIT-36 ×57 | WAIT-36 ×119 |
| 29-handshake w/s | 13109 / 13109 | 29470 / 29470 |
| 30-handshake w/s | 4 / 3 (ends parked) | 4 / 3 (ends parked) |
| 31-handshake w/s | 13110 / 13109 | 29471 / 29470 |
| 4th sema-30 signal | Absent | Absent |
| `0x394ED0` trace | 260,822 / 260,822 | 588,042 / 588,042 |
| `0x362DE8`/`0x362CC8` trace | 13108 / 13108 | 29469 / 29469 |
| `0x395000` trace | 247714 / 247714 | 558573 / 558573 |
| `run:tick` | 37 ticks, dma 259→455579, gif 16→12355 | 78 ticks, dma 22394→1185212, gif 647→32098 |
| Dormant / start-thread | 26209 / 5 | 59553 / 5 |
| Wall-rate shape | flat 33–37/s + 3–5× step @~245 s | 64→36/s smooth decay, onset ~240–360 s |
| Contention note | T1 `-j4` build through whole boot | none observed (P1af-like uncontended rate early) |

## T11-6. Exact commands

From `/Users/bradrichardson/dev/ssx3` unless noted; `$W`, `R`
quoted (path contains a space):

```
# Tree state + rebuild (lease-free)
git rev-parse HEAD; git log --oneline -3; git status --porcelain=v1
git -C "$R" rev-parse HEAD; git -C "$R" log --oneline -3; git -C "$R" branch --show-current; git -C "$R" status --porcelain=v1
find "$R" -name "._*" -delete (45 files); git -C "$R" status --porcelain=v1 (unchanged)
cmake --build /tmp/p1-link/runtime --target ps2EntryRunner -j4 > /tmp/t11-build.log 2>&1 (exit 0)
shasum -a 256 /tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner (81bee6c5...)
sed /tmp/p1ag-boot1.py -> /tmp/t11-boot1.py (LOG + SECS=600 + docstring; diff-verified)
write /tmp/t11-monitor.py (15 s exit-signature polls + trace-stall trip)
cp /tmp/p1ah-trace.py /tmp/t11-trace.py; cp /tmp/p1ag-mine.py /tmp/t11-mine.py
p1ag-blocks.py -> /tmp/t11-blocks.py (argv path); write /tmp/t11-rates.py; t10-pass2.py -> /tmp/t11-cycle.py (argv path)
# Boot (lease T11 held 07:29:29Z-07:39:44Z only)
pre-claim checks (lease absent; pgrep exit 1; shasum 81bee6c5; ISO + ELF sizes; df)
printf 'T11' > lease + >> t11-waits.log; python3 /tmp/t11-boot1.py (600 s, SIGTERM rc=-15)
python3 /tmp/t11-monitor.py (20 polls from 07:34:59Z, no trigger, exit 10)
cp ps2_log.txt ps2_log-t11-1.txt; >> t11-waits.log (release); rm lease; verify absent
# Analysis (lease released)
python3 /tmp/t11-blocks.py LOG (stub series, t1/t3/t6 series, handshakes)
python3 /tmp/t11-mine.py boot-t11-1.log (probe/sema/drops/census/threads/ticks)
python3 /tmp/t11-rates.py LOG (per-block pump + per-60 s slices + ticks + sema30)
wc -l T; grep -c sub_00362DE8/00394ED0/00395000/00362CC8/00376938 enter/exit on T
python3 /tmp/t11-trace.py T 77374859 (caller census + chunks + tenths + balance)
python3 /tmp/t11-cycle.py T (gate + FRR + modal slots + offsets + pre/post + persist d0seq/repidx)
grep rows (probe cap/change points/SendCmd/SIF/dormant/gif/copy/missing/fatal/drops/CD/GS/RPC lasts)
tick-delta + dormant-ratio joins (heredoc python)
pc attribution via P1/output/ps2_recompiled_functions.h + T10 slot table
# Report (lease released)
(mkdir + write local/research/T11/REPORT.md + blocks.tsv + ticks.tsv; this file)
git add -f local/research/T11/REPORT.md local/research/T11/blocks.tsv local/research/T11/ticks.tsv
git commit -m "[T11] ..." (trailer Orchestrated-By: Muse Code; NO push)
```

## T11-7. What I could not do (gap rows)

- Produce any of the 5 first-post-phase events inside 600 s: main
  is still in the hash phase at the cap (29,469 returning
  invocations and going, stubs steady 222, no exit signature).
  The phase-exit time stays unprojected — total phase work unknown.
- Run the optional ≤90 s confirm boot (1 of 2 boots used): the
  600 s absence + all-balanced traces + exact guest-event match to
  P1ag/P1af already span four consistent windows; a shorter
  re-boot adds no new window (same rule as §P30-6).
- Live-monitor the first ~330 s of wall time (monitor start
  latency — §T11-0 gap); post-hoc mining covers the full window.
- Attribute the wall-rate decay's host cause from inside the
  receipts (no host-load log in scope); tabled as uniform scaling
  of wall rates with fixed guest ratios (§T11-3).
- Raise the 20000-line probe cap (hit at :62113): the probe
  lives in `ps2_runtime.cpp`, outside this diag brief's
  zero-change rule. Trace enter/exit gives totals (588k here).
- Name the IOP announcer / decode `0x3C45C0`'s `0x1C`/`0x1D` arm
  semantics (carried from §P26-5/§P27-5/§P29-5/§P30-6; 0 sightings).
- Session wall time ≈ 07:10–08:05Z (~55 min active), inside the
  4 h box; zero lease waits.

## Evidence files

`REPORT.md` (this file), `blocks.tsv` (119 blocks ×
distinct/logline/pump/dormant), `ticks.tsv` (78 ticks ×
dma/gif/deltas/ratio).
