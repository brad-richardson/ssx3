# E2a report — STIMULUS pad-state flip mid-drain: NO response to cap (2400 s; stimulus delivered + latched; bands/gaps/padpair/residue hold over 41,678 post-fire iters)

Brief `local/muse/prompts/E2a.md`. Tables, no verdicts.
Stale-reading guard: P1 REPORT Part 34 §P34-2c (the E2a
brief-shape row) + §P34-1c (T8's 326EB0 live-span guard table) +
`local/research/T16/REPORT.md` (all of it — the E1 baseline this run
perturbs: exit @b235, drain 359,748 iters, bands w31 294–308 /
d-w31 [1.9,2.2] / gaps {6,7}) + `local/research/T18/REPORT.md`
(fork-diff + rebuild + sha-record discipline; T18's `f2b1852`
channel kept ON for this dual-purpose boot).

`W=/Volumes/Extreme SSD/ps2recomp-spike`, `R=$W/PS2Recomp` (fork,
branch `ssx3`), `LOG=$W/P1/run/boot-e2a-1.log` (2,857,513 lines,
603,341,176 B), `T=$W/P1/run/ps2_log-e2a-1.txt` (187,724,944 lines,
6,659,523,314 B), `SYS=$W/P1/run/syscalls-e2a-1.txt` (4,021,628
events, 192,946,881 B). `$R`-relative paths below unless noted. No
`adb`. 1 of 2 boots used (2nd not needed — stimulus injected
nominally, timing not missed).

Headline readings: the stimulus hook (fork `282ce92`, Pad.cpp +227:
env-armed read-count + wall backstop, latched all-buttons-pressed +
analog-extreme flip, GetState-ra + PortOpen tripwires) fired
reads-gated at exactly reads=204,356, wall=1702 s, log line
2,646,552 (block-338 window, 24.2% in), delivering flipped pad
values into guest buffers on both ports (`[padread]` ×48 cap,
data2/3=0x00, first at fire+1). Pre-arming T16 baselines reproduced
to the fire point (exit @b235 with T16's exact collapse shape,
N = 72,176 exact with T16's exact first/last lines, singletons
58/56/58, chunk-71 span +2, ramp ordinals 0–74, residue-13 from
b240). Post-fire over 41,678 drain iters (138 blocks): NO response
on any armed row — residue stays 13 (0 target diff), no new HLE
target, 326EB0/iter = 2.0 exact (143,394 = 2×71,697; live PADPAIR
2.0000 every window), 0 post-fire PortOpens (tripwire live),
3E4AF0 gaps {6,7} both sides (pre 6:762+7:3631, post 6:1059+7:5048),
w31/d31 bands hold (post 296–307 / 2.000–2.034), all 12 E1 watches +
2 gated extras silent. One tripwire voided by a build defect
(GETSTATE-NEWRA could never fire: the linked `sub_003FFBC0` inlines
a hookless GetState body — disassembly receipted; Read/PortOpen
hooks proven live in the same binary). The dormant-3FFBC0-site row
therefore rests on indirect rows only (all negative).

## E2a-0. Lease / tree-state / build / stimulus-diff record

| Item | Value |
|---|---|
| ssx3 HEAD at E2a start | `ed76d01` (`[orch] M60+T17+T18+P1ak gate reads PASS; …`), clean |
| ssx3 HEAD at commit | `ed76d01` pre-commit |
| Fork HEAD at E2a start | `f2b1852` (T18's channel) + `M register_functions.cpp` (foreign, untouched) |
| Fork HEAD at boot/commit | `282ce92` (`Stimulus: env-armed pad-state flip + 326EB0 dormant-arm tripwires (E2a)`, this brief; 1 file, +227) |
| Fork commits by E2a | 1 (`282ce92`); fork `git pull/push`: never run |
| Sidecars | 15 (`find $R -name "._*"`; 14 under `.git/`, 1 `ps2xRuntime/include/._ps2_log.h` = T15's; 1 mine created + removed mid-run: `Stubs/._Pad.cpp`, which broke the first build via the source glob) |
| Binary | `2ac142608f7a9a6e93804c17468ca43e8bae51eb2670cd2baddc8769a1ba746e`, 163,464,496 B (+272 B vs T18's `a2a2f660…` 163,464,224 B); 7 `padstim`/`PS2X_PAD_STIM` strings (GETSTATE-NEWRA format absent — see gap G1) |
| Build | 1 success (`-j4`, lease-free) + 1 failed (sidecar glob); 0 warnings from new code (11 CMake notices only); no `adb`; `git push` in ssx3: never run |
| Boot env | T18-ON env verbatim (`PS2X_DIAG_394ED0=1`, PARK, `PS2X_TRACE_SYSCALLS` channel ON) + `PS2X_PAD_STIM_AFTER=204356` + `PS2X_PAD_STIM_WALLMIN=1450` (boot-script diff vs `/tmp/t18-boot-on.py` = docstring + LOG/SECS/paths + 2 env lines only, diff-verified) |
| Monitor | `/tmp/e2a-monitor.py` (T16 monitor + E2a rows: STIM-FIRED record, hle-new-target, trace-tail PADPAIR, stim-portopen, stim-getstate-newra; self-test: silent on T16's 4.3M lines + invariant@235 + residue-13 seeded; 6/6 grafts incl. run-wide 31A3C0=431,926/326EB0=863,852 exact-2.0 on T16's trace) |
| Boots | 1 of 2 used (cap case; no trigger in 2400 s) |
| ssx3 evidence commit | below (`[E2a]`, no push) |

Lease record (`$W/P1/run/e2a-waits.log`; 9 WAIT lines — T20 held the
lane 16:13:34–17:14:25Z):

| Event | Value |
|---|---|
| E2a waits (9) | 16:36:26–17:10:34Z, 5-min polls, all `lease=T20; runner alive` |
| E2a pre-claim checks (17:14:47Z) | Lease absent; `pgrep -x ps2EntryRunner` exit 1; sha `2ac14260…` 163464496 B; ISO 3005415424 B + ELF 3890784 B present; 506 Gi free; t20-waits tail = released 17:14:25Z; arm AFTER=204356 WALLMIN=1450s + flip record |
| E2a claim | `printf 'E2a\n' > /tmp/ssx3-p-lane-lease` 17:14:47Z |
| Monitor start | 17:15:07Z (died poll-1 on a `global fired` bug, fixed + restarted; rescan-from-zero loses nothing — all triggers arm post-241) |
| Boot | start 17:16:20Z; INVARIANT `block=235 distinct=218 logline=2462838` logged; STIM-FIRED `reads=204356 wall=1702s logline=2646552 maxblock=338`; NO trigger to cap; boot script `SIGTERM after 2400s, rc=0`, exit 241 (17:56:20Z) |
| E2a release | 17:57:11Z (held 2544 s); verified absent; `pgrep -x` exit 1 |
| Trace copy (lease-free) | `ps2_log.txt` → `ps2_log-e2a-1.txt` (187,724,944 lines, 6,659,523,314 B) |

Monitor-coverage note: 136 polls, sema30=7 throughout, `maxblock`
0→476, PADPAIR ratio 2.0000 on every ≥100-iter window (final totals
143,874/287,748 = exactly 2.0 run-wide), 234 POST block lines,
`d1=1` from the halt trio on, zero predicate fires. Exit 10
(runner dead, no trigger). Quiescence re-scan silent.

Stimulus-diff record (fork `282ce92`, `ps2xRuntime/src/lib/Kernel/
Stubs/Pad.cpp` +227, ONLY file):

| # | Item | Receipt |
|---|---|---|
| 1 | Arming | `PS2X_PAD_STIM_AFTER` (total `scePadRead` fills) + `PS2X_PAD_STIM_WALLMIN` (steady-clock s since first pad call); fires once when BOTH met; unset AFTER = one relaxed atomic check per pad call, zero behavior change |
| 2 | Threshold choice | AFTER=204,356 = in-phase 326EB0 144,354 (mined from T16's trace pre-185264992) + in-phase 326DF0 2 + 2×30,000 margin iters; WALLMIN=1450 s (≈ exit+250 s backstop — reads-gated nominally) |
| 3 | Flip (latched to cap) | buttons 0xFFFF→0x0000 (all 16 pressed, active-low) + lx/ly/rx/ry 0x80→0x00/0x00/0xFF/0xFF; applied post-backend pre-`fillPadStatus` on all ports; GetState return untouched (stable=6); mode untouched (0x41) |
| 4 | Markers (stderr → boot log) | `[padstim] armed …` once; `progress` every 25k reads (every 1k once reads-past, wall-waiting); `FIRED …` once; `post` every 25k reads; 13 lines total this boot |
| 5 | Tripwires | GetState-ra census (pre-fire set + post-fire new-ra print — VOID, gap G1); PortOpen post-fire print (first 10 + count — LIVE: 2 boot opens counted) |
| 6 | Delivery proof | `[padread]` ×48 (cap) data2/3=0x00 guestButtons=0xffff, first at fire+1 (logline 2646553), on ports 0+1 (aggressive logs are ON in this build: `-DAGRESSIVE_LOGS=1`) |

## E2a-1. Pre-arming table (T16 baselines reproduced to arming?)

Fire at drain-iter ≈29,997 of 71,697 (w31 split: pre 29,997 =
905 (w239–241) + 29,017 (POST 242–337) + 75 (w338 pre); mix w338 =
75 pre + 229 post, fire 24.2% through the window; post 41,678 =
229 + 41,427 (POST 339–475) + 22 (w476 partial)).

| # | Baseline (source) | E2a observed to arming | Row |
|---|---|---|---|
| 1 | Exit @b235, 218 (T16) | b235 distinct=218 @logline 2,462,838 (T16: 2,463,373) | match (line −535) |
| 2 | Collapse shape (T16: 211×2+189×2, residue @b240) | 211×2 (236–237) + 189×2 (238–239) + 13 @b240 | exact shape |
| 3 | residue-13 from b240 (T16) | 13 ×237 blocks (240–476), same 13 targets+ras | match |
| 4 | N = 72,176 (T16) | 72,176/72,176; first @19,385; last enter/exit @185,264,853/185,264,992 (T16-exact); single caller `00363490` ×72,176 | exact |
| 5 | Ramp ordinals 0–74 (T16) | non-20/19 = exactly ords 0–74 (n=75); 75–72,175 all exact 20/19 | exact |
| 6 | w31 294–308 (P34) | pre-fire POST 295–307 (96 blocks) | inside |
| 7 | d/w31 [1.9,2.2] (P34) | pre-fire POST 2.0033–2.0367 | inside |
| 8 | gaps {6,7} (P34) | pre-fire drain gaps 6:762 + 7:3631 (n=4,393), none outside | exact |
| 9 | Halt trio adjacent (T16) | 2,494,583/2,494,584/2,494,585 (+0/+1/+2); shapes `waker=4 ra=0x31aae4` / `waker=1 ra=0x31aa8c` | exact |
| 10 | Freeze counters 2669132/72181 (T13) | identical; frozen from the same pair | exact counters |
| 11 | sema-30 4w/3s parked (P1ag) | 7 lines, 4w/3s, ends parked (@644/646/647/708/6978/7028/7230 — T16's +4/+4/+4 class) | exact shape, shifted lines |
| 12 | Singletons 58/56/58 (T16 D4) | 58/56/58 @70857/71014/71526 | exact (= T16) |
| 13 | Inv-chunk-71 span 2302066 (T16 D5) | 2302066 (enters same) | exact (= T16) |
| 14 | FRR ×N 0 dev; modal 53 ×70850 (T10/T16) | FRR 0 dev; modal len 53 ×70,850; E-double ords 51–62; pre-first 294 (3×C1a+1×E) | exact |
| 15 | b241 residue shape (T15: 610×3+305×10) | 592×3 + 296×9 + 295×1 (3825F8 one short — window-240 transitional edge; b242 clean 606×3+303×10) | DEVIATION (edge count −1) |
| 16 | Stub preamble (T16: 961/497) | b0=973, b1=491 (= T18-ON pair; 6th datum, 3rd distinct value) | DEVIATION set |
| 17 | Read cadence 120/s (derived) | 119.95–119.98/s pre-fire (25k milestones over 207–1666 s) | match |
| 18 | GetState cadence (assumed 1:1) | getstate=0 at every milestone (hook void — gap G1, not a guest row) | VOID instrument |

## E2a-2. Response table (first stimulus response + E1 no-break watches)

First stimulus response: NONE. All armed rows silent over 41,678
post-fire iters (138 blocks, ~700 s wall):

| # | Armed row | Bound observed | Fired? |
|---|---|---|---|
| R1 | residue ≠13 | 13 ×138 post-fire blocks (339–476); pre/post target sets identical (13 = 13, 0 diff) | NO |
| R2 | new HLE target in stubs | `hle-new-target` silent; post_syscall ids {0x44, 0xffffffbd} only; all post stub rows firstRa==lastRa | NO |
| R3 | 326EB0/iter ≠2 | post 326EB0 = 143,394 = 2×71,697 exact (full-run); live PADPAIR 2.0000 every post-fire window | NO |
| R4a | 3FF708 arm fires (PORTOPEN tripwire, LIVE) | postFirePortOpens=0; total PortOpens=2 (boot only) | NO |
| R4b | 3FFBC0@0x327080 executes (GETSTATE-NEWRA tripwire) | VOID instrument (gap G1) — indirect rows R1–R3 + W10 cover, all negative | n/a (void) |
| R5 | gaps break {6,7} | post-fire gaps 6:1059 + 7:5048 (n=6,107) + spanning 7; none outside | NO |
| R6 | w31 band break | post w31 296–307 (138 blocks) | NO |
| R7 | d/w31 band break | post d31 2.000–2.034 (min 2.000 exactly @b345 — first exact-2.0000 post-exit datum) | NO |

E1 no-break watches (all armed post-241, same as T16 — all silent):

| # | Watch | Bound observed | Fired? |
|---|---|---|---|
| 1 | Main wake from dormant | t1 status 5 pc 0x0 ×238 (blocks 239–476) | NO |
| 2 | New stub phase after residue | distinct 13 ×237 (blocks 240–476) | NO |
| 3 | First new guest event | drops/RPC/CD/SIF/GS 0 past block 2 (lasts 75/5145/7180/1058/2642) | NO |
| 4 | New caller | `0x362DE8` 0 post-phase; caller single ×72,176; post-only trace funcs 0 | NO |
| 5 | dma/gif unfreeze | 174 frozen 0/0 pairs at 2669132/72181 (all 104 nonzero deltas in 0.02703±0.0001, partial incl.) | NO |
| 6 | 31-drain end | w31 295–307 every complete post block (min 295 @b271; b476 partial 22) | NO |
| 7 | Second halt (trace stall) | trace grows every poll to EOF (final 6,659,523,314 B) | NO |
| 8 | W4 second dormant id=1 | total id=1 = 1 (@2494585) | NO |
| 9 | W10 stub ra-split | all post rows firstRa==lastRa (live scan silent) | NO |
| 10 | W11 rate-shape | per-block d31 2.000–2.037 (234 POST lines); s31−w31 max +1 (@b255) | NO |
| 11 | T3 29-resume | 29w = 0 every block 239–476 | NO |
| 12 | T4 extra 31-signals | s31−w31 max +1 (trip needs >+2) | NO |
| 13 | W8b waiter status-5 | status=5 ×238, ALL id=1 (0 for ids 2–6) | NO |
| 14 | syscall-new | post-241 syscalls exactly {0x44, 0xffffffbd} all 235 sections | NO |
| + | sema30 8th line (gated) | n=7 all run, last @7230 | NO |
| + | thread-3 release (gated) | WAIT-30 ×476 + RUN b0 (@0x416934 = T11/T16 pc), no release | NO |

## E2a-3. Diff table (pre/post-stimulus + miner rows)

| Row | Pre-fire | Post-fire |
|---|---|---|
| Residue targets | 13 (same set) | 13 (0 diff) |
| Stub ra equality | all firstRa==lastRa | all firstRa==lastRa |
| Pad-read cadence | 119.95/s (25k milestones) | 120.0/s (25k milestones; no T5 skip) |
| Pad values in guest bufs | 0xFFFF/0x80 (0 `[padread]` pre) | 0x0000 + extremes (`[padread]` ×48 cap from fire+1, ports 0+1) |
| 326EB0/iter | 2.0000 (live PADPAIR) | 2.0000 (live PADPAIR) |
| 3E4AF0 gaps | 6:762 + 7:3631 (n=4,393) | 6:1059 + 7:5048 (n=6,107) + spanning 7 |
| w31 band | 295–307 (96 blocks) | 296–307 (138 blocks) |
| d31 band | 2.0033–2.0367 | 2.000–2.034 |
| Syscall ids | {0x44, 0xffffffbd} | {0x44, 0xffffffbd} |
| Wall-rate slices | 30.17–30.28 (336–347 spans fire) | 30.14–30.36 (384–407 marginally high; per-block bands hold) |
| PortOpen census | 2 (boot) | 0 new |
| T8 branch split | — | NOT fired (no new HLE targets; no PORTOPEN; padpair exact) |

E1 miner rows (P33-4a M1–M10 class + P34-1a/b/c, run-wide):

| Row | Value |
|---|---|
| Drain iters Δ(31−29) | 71,697 (143,875 − 72,178; T15: 71,762) |
| Drain iters (trace markers) | 71,697 depth-0 `31A3C0` drain-ordinals (first @185,265,559 = T16's line; = Δ exactly, no +1 cut effect) |
| Post-phase trace | 2,459,952 lines over 113 functions (preset 1072), 0 post-only; 394/395 0/0; 362CC8 1/1 (N+1); ends: final iter 71,697 = 28 lines (SIGTERM-cut shape) |
| 9-family | 71,697/71,697 ×9 balanced |
| 31AAF0/326EB0 | 143,394/143,394 = 2× exact |
| Strays | 423DE0 +11, 423DD0 +2 (= iters+2), 31A6B8 +8 (= iters+8) — T16's exact strays |
| Chunk-0 | 340/40, ALL in iter 1 (last resid iter 1 @185,266,275 `001D8DE0` — T16's line) |
| Chunks 1–40 | 15 distinct, 146/147 alternation; chunk 41 = 697 iters |
| Depth-0 tops | 423DE0 71700 (+3), 31A3C0/37E120/3C1638/31AAF0 71697, 3E4AF0 10503 — T16's shape |
| N2 (post-boot 362DE8) | 72,176 = N (0 post-phase; bound_ok=True) |
| EE stream (dual-purpose) | 4,021,628 events, format zeros (`--format-check`); first RFU060 (3c) @0.0 s, last WaitSema (44) @2398.6 s; top GetThreadId 1,431,968 / WaitSema 1,222,578 / SignalSema 933,941 / iSignalSema 288,632 / FlushCache 72,183 / PollSema 72,178 (= N+2) / CreateSema 37 / RFU252 21 (= T18's count); 29 distinct names |

## E2a-4. Baselines-kept table (per-row exact-vs-baseline)

| Baseline (source) | E2a observed | Row |
|---|---|---|
| 54-frame modal cycle REP+53 (T10) | modal len 53 ×70,850/72,175 gaps; E-double ords 51–62; C1a×3 in 51 gaps; OTHER ×1 (post singleton) | exact (in-phase) |
| 31 gap patterns, ramp ords 0–74 (T10) | 36 patterns; non-modal = exactly ords 0–74 | exact + exit tail |
| Exit-tail singletons (T16: 58/56/58) | 58/56/58 @70857/71014/71526 | exact (= T16; vs T13/T15's third 57) |
| Class offsets (T10) | C3/C7/C1a#1/C1b exact; E @42 + @41 tail shift class; C1a#2 @52/@51 | exact + tail shift |
| 20/19/1/2534 per invocation (P1ah) | chunks exact; chunk-70 span 2520494 (T13-exact); chunk-71 span 2302066 (= T16's +2) | exact (= T16) |
| Stubs 222 (P1ag) | 222 ×233 (blocks 2–234) | exact pre-exit |
| Stub preamble (T16: 961/497) | b0=973, b1=491 (= T18-ON pair) | DEVIATION set (6th datum, 3rd value) |
| Sema-30 4w/3s parked (P1ag) | 7 lines, 4w/3s, ends parked (@644–7230; last three +4/+4/+4 vs T16) | exact shape, shifted lines |
| FRR ×N, 0 deviations (T8) | FRR ×72,176, 0 deviations; `363490` 216,528/216,528 = 3N exact | exact |
| Single caller `0x363490` (P1ah) | ×72,176, other 0 | exact |
| Probe change points 104/140/162 (P1ah) | @7596/7985/8275 (T16: 7592/7981/8272); `total→0x14` sat. @8275; cap line @62114 (T16: 62119; 5th distinct value) | exact points, shifted lines |
| Probe NULL-head (T16: 3135) | 3135 | exact (= T16/P1ag; vs T11/T13/T15 3136) |
| Probe pool drops 1066, arenas 1, buckets 5 | 1066 / 1 (`0x8095f0`) / 5, CYCLE@ 0 | exact |
| Drops 6 KE_ERROR 0x5b (T16: @68–73) | 6 @70–75, same site bytes | exact count+site, +2 lines (+1 = trace-open@66; +1 unattributed pre-70) |
| RPC unhandled 4 (T13 lines) | 4 @713/1059/1065/5145 (T16: 711/1056/1062/5143) | exact count, +2/+3/+3/+2 lines |
| SendCmd 1 / handshake 2 / `0x3C45C0` 0 | 1 @1055 (T13: 1052) / 2 / 0 | exact count, +3 lines |
| CD 810 `0x10`→`0x4311f` | 810 (:107–:7180; T16 last 7176) | exact count, shifted span |
| SIF 21 loads id 1–21 | 21, last @1058 (T16: 1055) | exact count, +3 lines |
| Creates 37 / `-1` waits 0 | 37 / 0 | exact |
| Driver-entry 98 | 98 | exact |
| GS 96 / copy 64 / gif 48 / drawing=1 96 | 96 / 64 / 48 (= 327 broad − 279 ticks) / 96 | exact |
| Missing-target 1, JALR `0x2322d4→0x395730` | 1 @662 (T16: 660), same bytes | exact, +2 lines |
| Crash / FATAL / presented frame 0 | 0 / 0 / 0 | exact |
| Thread-3: RUNNING pre-pump → WAIT-30 | RUNNING ×1 (block 0, pc `0x416934` = T11/T16) → WAIT-30 ×476 | exact |
| Thread-6: WAIT-36 all blocks | WAIT-36 ×477 | exact |
| First `0x362DE8` enter @19,385 | @19,385 | exact |
| Stack mismatches 0 / max depth 29 | 0 / 29 (live frames at EOF = 0 — SIGTERM between root dispatches) | exact |
| Pre-first-rep 294 frames, 3×C1a+1×E | 294, 3×C1a+1×E | exact |
| Post-last-rep (T15: 369,352) | 369,017 frames (C3/C7/C1a/C1b ×1) | T15-scale (≈ −335) |
| Freeze counters 2669132/72181 (T13) | identical; 174 frozen pairs (T15: 160 same window) | exact counters, +14 pairs |
| Halt envelope (T13/T15/T16) | 97.60% through window 238 (4th datum; T16: 97.85% w238) | envelope holds |
| Dormant/inv 2.000 (T11 slices 2+) | in-phase slices 2.10–2.13 class (never exact); post d31 exact 2.000 @b345 (first exact post-exit datum) | DEVIATION note (in-band) |
| Thread-1 end (T15: 55/20/165/237) | 55 RUN + 22 mid + 162 W29 + 238 dormant-5 (end: status 5 pc 0x0, blocks 239–476) | same shape ±2 |
| Pre-block-0 29/31 (T16: 26/26) | 37/37 (pre-marker-0 anchor; T16's anchor unverified — comparability caveat) | DEVIATION (new value + caveat) |
| In-phase b0–237 29/31 (T16: 71873/71872) | 71,861/71,861 balanced exact | DEVIATION (exact-balance replaces +1 29-side) |

## E2a-5. Absence-window ladder note (E2a rung: first stimulus null)

| Rung | T15 (2,400 s, CAP past exit) | E2a (2,400 s, CAP past exit + stimulus) |
|---|---|---|
| Lines / bytes | 2,857,096 / 602,908,868 | 2,857,513 / 603,341,176 |
| Trace lines / bytes | 187,727,172 / 6,659,595,180 | 187,724,944 / 6,659,523,314 |
| Stub blocks | 477 | 477 |
| Exit | b235 reproduced | b235 reproduced (T16-shape collapse) |
| Post-exit iters | 71,762 (no stim) | 71,697 (stim @29,997: 29,997 pre + 41,678 post + 22 edge) |
| Post response | n/a (no stimulus) | NONE on every armed row (R1–R7 + 12 E1 + 2 gated) |
| Dormant-arm evidence | n/a | PORTOPEN 0 post-fire (live); GETSTATE void (G1); residue/padpair indirect negative |
| EE stream | n/a | 4,021,628 events, zeros (dual-purpose boot) |

## E2a-6. Exact commands

From `/Users/bradrichardson/dev/ssx3` unless noted; `$W`, `$R`
quoted (path contains a space):

```text
# Recon (lease-free)
read local/muse/prompts/E2a.md; P1 REPORT Part 34 (P34-1c guard table + P34-2c E2a row); T16 REPORT (all); T18 REPORT (all)
git -C $R rev-parse/log/branch/status (ssx3 @f2b1852 + foreign register_functions.cpp)
sed Pad.cpp (override/surface); grep HLE call chains (326EB0 -> 3FFBC0/GetState + 3FFA58/Read; 3FF708/PortOpen)
awk T16 trace pre-185264992 (in-phase 326EB0=144354, 326DF0=2 -> AFTER=204356; WALLMIN=1450)
# Stimulus diff + build (lease-free; mid-T20-boot relink at ~16:28Z -> FYI note in t20-waits.log)
edit_file Pad.cpp (+chrono include, +stimulus block, 3 call sites; +227)
rm Stubs/._Pad.cpp (mine; broke first -j4 via source glob)
cmake --build /tmp/p1-link/runtime --target ps2EntryRunner -j4 (exit 0; binary 2ac14260 163464496 B)
git -C $R add Pad.cpp + commit 282ce92 (ssx3 branch ONLY; no push/pull)
# Scripts (lease-free)
write /tmp/e2a-boot1.py (diff vs t18-boot-on.py = names + SECS + 2 env lines) + /tmp/e2a-monitor.py (T16 + 5 E2a rows)
python3 -m py_compile (boot + monitor + selftest + 8 miners, OK)
python3 /tmp/e2a-selftest.py (silent on T16 log + 6/6 grafts incl. run-wide exact-2.0; 1 harness bug fixed)
sed t16-{blocks,mine,rates,trace,cycle,tail,drain,drain2}.py -> e2a-*.py; write /tmp/e2a-stim.py + /tmp/e2a-tsv.py
# Boot (lease E2a held 17:14:47-17:57:11Z only)
pre-claim checks (absent/pgrep-1/sha/ISO+ELF/506Gi/t20-tail); printf claim; >> e2a-waits.log
python3 /tmp/e2a-monitor.py (bg; died poll-1 global-bug -> fixed, restarted, rescanned from 0)
python3 /tmp/e2a-boot1.py (foreground; INVARIANT b235, STIM-FIRED b338, NO trigger; SIGTERM after 2400s rc=0; exit 241)
rm lease; verify absent; pgrep exit 1; >> e2a-waits.log (release)
cp ps2_log.txt ps2_log-e2a-1.txt (lease-free; 187724944 lines, 6659523314 B)
# Analysis (lease released)
wc -l LOG/T/SYS; python3 /tmp/e2a-blocks.py LOG; awk N/boundary (72176/72176, lastX=185264992 -> BOUND stands)
python3 /tmp/e2a-mine.py boot-e2a-1.log; python3 /tmp/e2a-rates.py LOG
python3 /tmp/e2a-trace.py T 187724944; python3 /tmp/e2a-cycle.py T; python3 /tmp/e2a-tail.py T
python3 /tmp/e2a-drain.py T (-> /tmp/e2a-drain-summary.txt); python3 /tmp/e2a-drain2.py T
python3 /tmp/e2a-stim.py LOG SYS (fire-anchored split); python3 /tmp/e2a-tsv.py LOG blocks.tsv ticks.tsv (sums exact)
grep rows (stub series, residue b241/b242/b476, halt trio, padstim x13, padread x48, ticks, lasts, probe points)
tick-ratio + dormant-ratio joins; POST-extremes + fire-split awk (75/229 mix; 29997/41678 iters)
gap-split pass (drain ordinals; pre 4393 + post 6107 + spanning 1 = 10501)
tools/trace_align.py --format-check syscalls-e2a-1.txt (4021628 events, zeros)
otool -tV sub_003FFBC0/sub_003FF708 + nm sweeps (gap G1 receipts); fresh Pad.cpp.o recompile test (0 strings)
# Report (lease released)
(mkdir + write local/research/E2a/REPORT.md + blocks.tsv + ticks.tsv; this file)
git add -f local/research/E2a/REPORT.md local/research/E2a/blocks.tsv local/research/E2a/ticks.tsv
git commit -m "[E2a] ..." (trailer Orchestrated-By: Muse Code; NO push)
```

## E2a-7. What I could not do (gap rows) + E2b/E2c/E3 reads

- G1 (VOID instrument, mechanism unresolved): the
  GETSTATE-NEWRA tripwire could never fire. Receipts: (a) live
  getstate=0 over 287k+ reads while 0x3FFBC0 tallies 602
  dispatches/block; (b) the binary lacks the GETSTATE-NEWRA format
  string (5/6 hook formats + 2 env names present); (c) disassembly
  of linked `sub_003FFBC0` shows the GetState body inlined WITHOUT
  the hook (state-mutex lock first, no atomic checks); (d) a fresh
  `Pad.cpp.o` recompile from current source also yields 0 padstim
  strings; (e) single definition verified (Pad.cpp only), table
  slot math verified correct (786158 = registered), one
  `[diag:stub]` emitter verified. Suspected incremental-ThinLTO
  staleness (small single-caller function re-imported hookless
  while Read/PortOpen hooks in the same TU linked live —
  `sub_003FF708` tail-calls the real hooked PortOpen). Guest impact:
  none (GetState LOGIC executes normally — guest behavior is
  baseline-exact; only E2a's counter went blind). The dormant
  3FFBC0@0x327080 row rests on indirect rows (all negative).
  Lesson for E2b/E2c/E3: verify every hook IN the linked binary
  (strings/symbol/disassembly receipt) before booting; prefer a
  clean rebuild for instrumented binaries.
- Read the ~25 326EB0 live-span branch directions: still jointly
  fixed (pad-pair 2×/iter exact over 71,697 MORE iters, now under
  flipped pad values) — the stimulus did not open the branch
  surface observably (E3 rows stand).
- Join trace chunks to log blocks (no timestamps either stream):
  fire-iter ≈29,997 is reads-inferred (2 reads/iter exact both
  sides), not observed (same gap as T13/T15/T16/P1ak).
- Attribute the pre-b0 37/37 datum (vs T16 26/26): mine uses the
  pre-marker-0 anchor; T16's anchor is unverified from its report —
  comparability caveat tabled, not derived.
- Attribute the +1 early-line shift beyond trace-open@66 (drops
  +2 with 1 insertion before them): tabled as unattributed
  boot-jitter, not derived.
- Attribute the +22 pre-239 31-surplus (71,675 post-239 w31 vs
  Δ=71,697): tabled by count (in-phase +1s + pre-b0 + transitional
  class, cf. T16's +2 edge rows), not derived.
- Rebuild the binary post-G1 (would void the booted-binary
  receipts; forbidden mid-lease-window by the etiquette breach in
  §E2a-0): the booted binary is receipted as-is.
- E2b read (SIF0-reply): untouched by E2a's null (different
  surface); E2a's env-arm + milestone + tripwire pattern + the G1
  linkage-verification lesson transfer directly.
- E2c read (debug SignalSema-30): untouched by E2a's null
  (parked-waiter surface); same pattern transfer.
- E3 read (read-only probe): E2a's null RAISES E3's value — guard
  WORD VALUES (pad HLE returns as the guest branches see them,
  T1–T10 branch-hit counts) remain the only way to see inside
  326EB0's live-span branches; E3 must include the G1 lesson
  (per-hook linkage receipts + clean rebuild).
- Session wall inside the 6 h box (waits included); zero lease
  contention after T20's release; 2nd boot unneeded and unused.

## Evidence files

`REPORT.md` (this file), `blocks.tsv` (477 per-block rows with
fire_rel flags; pump sums 72,141/143,838 exact), `ticks.tsv` (279
tick rows with deltas). Full-size artifacts stay on the SSD by
path+sha: `boot-e2a-1.log` (603,341,176 B), `ps2_log-e2a-1.txt`
(6,659,523,314 B), `syscalls-e2a-1.txt` (192,946,881 B),
`park-e2a-1/` (111,765 + 7,655 B), `$W/P1/run/e2a-waits.log`,
`/tmp/e2a-monitor.log` (136 polls, 0 triggers).

