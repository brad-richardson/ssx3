# T16 report — E1 longer boot: NO drain break to cap (7200 s; drain/freeze hold; N = 72,176 reproduced; 359,748 iters)

Brief `local/muse/prompts/T16.md`. Tables, no verdicts.
Stale-reading guard: `local/research/T15/REPORT.md` (all of it —
T15's post-exit window: NO post-241 event to 2400 s cap, 71,762
drain iters over blocks 242–476, N = 72,176) + P1 REPORT Part 33
(P1aj's drain-termination analysis: 1 iter/VBLANK fixed point from
iter 2, 13-row live-guard terminator table T1–T13, E1/E2/E3 spec
with bound math — the trigger watchlist).

`W=/Volumes/Extreme SSD/ps2recomp-spike`, `R=$W/PS2Recomp` (fork,
branch `ssx3`), `LOG=$W/P1/run/boot-t16-1.log` (4,315,920 lines,
1,216,689,154 B), `T=$W/P1/run/ps2_log-t16-1.txt` (197,603,104 lines,
6,978,090,314 B). `$R`-relative paths below unless noted. Zero fork
changes; no `adb`.

Headline readings: the T15 exit invariant reproduced at block 235
(stub 222→218, log line 2,463,373, boot-wall ~1,199 s; collapse one
block shorter than T15 — 211 ×2 + 189 ×2 with residue-13 from block
240, tabled). The run continued 1,188 blocks past block 241 to block
1429 (cap): NO drain break on any of the 12 watches + 2 gated extras
— main stays DORMANT status 5 pc 0x0 (×1191, blocks 239–1429),
stubs hold residue-13 (×1190, blocks 240–1429), 31-drain runs the
full window (359,748 iterations, 0/31 every post block, never idle),
dma/gif frozen 887 tick pairs at T13's exact counters
(2669132/72181), CD/SIF/GS/RPC/drops silent past block 2,
sema-30 parked 4w/3s, thread-3 never releases. Empirical `N` =
72,176 reproduced to the digit (balanced enters/exits, first enter
@19,385, last enter/exit @185,264,853/185,264,992 (+2 vs T13/T15),
ramp ordinals 0–74, steady 20/19, chunks T13-exact). Post-phase trace
= 12,338,112 lines over the same 113 functions (0 post-only); trace
ends with empty stack (all functions balanced — SIGTERM at cap landed
between root dispatches, final iter 28 lines). Wall-rate shape is
T15-class flat: ~60/s in-phase (no dip/surge), ~30.2/s 31-only proxy
post-exit; dormant/inv 2.10–2.13 in-phase slices 0–18 (never T13's
exact 2.0000), ~2.02 per drain iteration post-exit.

## T16-0. Lease / tree-state / build record

| Item | Value |
|---|---|
| ssx3 HEAD at T16 start | `e48cf97` (`[orch] P1aj+M56 gate reads PASS; M57+T16 briefs`), clean |
| ssx3 HEAD at claim/boot | `e48cf97`, clean (next commit `c26e853 [M57]` 12:12:00Z, mid-boot, M-lane offline) |
| ssx3 HEAD at release | `802a676` (`[T4] …`, 14:30:33Z; M57–M59 + T4 briefs landed mid-boot — offline docs/tables, no P-lane interaction) |
| ssx3 HEAD at commit | `802a676` pre-commit (all 7 mid-boot commits post-claim) |
| Fork HEAD throughout | `7eed783` (same as T13 rebuild/boot and T15) + `M ps2xRuntime/src/runner/register_functions.cpp` (foreign, untouched) |
| Fork commits by T16 | 0; fork `git pull/push`: never run |
| Sidecars | 13 (`find $R -name "._*"`; 12 under `.git/`, 1 `ps2xRuntime/include/._ps2_log.h`; T15's 13, untouched per zero-change rule) |
| Rebuild | NONE (tree at T13/T15 boot state; binary sha AND size identical — no build run) |
| Binary | `81bee6c5c0740dafbb910fdfd9c62de8185b816372a0658603dc38c41252d40f`, 163,460,272 B (IDENTICAL to T11/T13/T15 Release) |
| Boot env | T15 `boot1.py` verbatim (`PS2X_DIAG_394ED0=1` kept; `PS2X_DIAG_PARK` unset); script diff = LOG name + `SECS=7200` + docstring only (diff-verified) |
| Monitor | `/tmp/t16-monitor.py` (T15 monitor + P1aj E1 signature rows only, diff-verified, self-tested): exit invariant LOGGED never triggers; T15's 7 post-241 watches + W4 (2nd dormant id=1) + W10 (stub firstRa≠lastRa in ≤30-distinct block) + W11 (per-block dormant/31w band [1.9,2.2] post-241) + T3 (29-resume) + T4 (extra 31-signals) + W8b (status-5 ids 4/5/6) + syscall-new (T2/T10 latent); new-caller trace-only post-hoc; 15 s polls |
| Boots | 1 of 1 used (cap case; no trigger in 7200 s) |
| Wall | 2026-09-20 ~12:05–14:55Z (~2.8 h active), inside the 6 h box |
| ssx3 evidence commit | below (`[T16]`, no push) |

Lease record (`$W/P1/run/t16-waits.log`, 2 lines; no contention —
lease absent at every check, zero WAIT lines):

| Event | Value |
|---|---|
| T16 pre-claim checks (12:10:10Z) | Lease absent; `pgrep -x ps2EntryRunner` exit 1; sha `81bee6c5…` 163460272 B; ISO 3005415424 B + ELF 3890784 B present; 524 Gi free; t13/t14/t15-waits tails = released/done; Part 33 landed |
| T16 claim | `printf 'T16\n' > /tmp/ssx3-p-lane-lease` 12:10:28Z |
| Monitor start | 12:10:32Z (managed session, verified alive + log header before boot) |
| Boot | start 12:11:02Z; invariant LOGGED `block=235 distinct=218 logline=2463373` (~12:31:01Z, monitor-t ~1229 s); NO trigger to cap; boot script `SIGTERM after 7200s, rc=-15`, exit 241 (14:11:03Z) |
| T16 release | 14:12:16Z (7308 s held); verified absent; `pgrep -x` exit 1 |
| Trace copy (lease-free) | `ps2_log.txt` → `ps2_log-t16-1.txt` (197,603,104 lines, 6,978,090,314 B) |

Monitor-coverage note (T13's 29 s lead repeated): the monitor led
the boot by 30 s and polled the full window (474 polls, sema30=7
throughout, `maxblock` 0→1429, `inv=True` from poll 79, trace bytes
monotonic to 6,978,090,314 = trace file size at final poll,
`d1=1` throughout post window). 1187 POST block lines (completions
242–1428), per-block d31 1.997–2.050, w31 294–308 — inside every
band, zero predicate fires. Exit 10 (runner dead, no trigger). No
late trigger on quiescence re-scan. Predicate self-test (pre-boot,
real `scan_chunk` vs T15's log): silent on all 2,857,096 lines
(234 POST lines, d31 2.003–2.040); 9/9 synthetic grafts
(dormant-id1-2nd, stub-ra-split, syscall-new, drain-29-resume,
drain-extra-signal, rate-shape, waiter-status5, pump-idle,
stub-post) fire with the right names.

## T16-1. Exit-invariant table (T15 §T15-1 reproduced?)

Collapse series: T15 `222 ×233 → 218 → 211 ×2 → 189 ×3 → 13 @b241`;
T16 `222 ×233 → 218 → 211 ×2 → 189 ×2 → 13 @b240` (block 240 reads
13, not 189 — the transitional tail is one block shorter; endpoints
218 @235 and residue 13 identical; residue starts one block early).

| Block | Stub distinct | 29w / 31w | Main (t1) | Note |
|---|---|---|---|---|
| 2–234 | 222 ×233 | ~300 / ~300 | RUN/mid/W29 mix | phase steady (preamble b0=961, b1=497 — T11-exact pair) |
| 235 | 218 | 300 / 301 | W29 | INVARIANT (log line 2,463,373; T15: 2,461,202) |
| 236–237 | 211 ×2 | 304 / 303, 299 / 299 | RUN/W29 | pump still flowing |
| 238 | 189 | 279 / 299 | W29 | 29-pump drops inside block 238 (last signal @2,494,970, 97.85% through window) |
| 239 | 189 | 0 / 305 | status 5, pc 0x0 | main DORMANT one block early; 29 halted |
| 240–1429 | 13 ×1190 | 0 / ~301 every block | status 5, pc 0x0 ×1191 | post window: drain + freeze hold to cap |

Five-signature invariant table (brief wording vs T15):

| # | Signature (brief wording) | Receipt | Reading |
|---|---|---|---|
| 1 | New stub phase | 222 ×233 → 218 @b235 → 211 ×2 → 189 ×2 → 13 @b240, holds ×1190 to b1429 | PRESENT at block 235 (transitional tail one block shorter vs T15) |
| 2 | 4th sema-30 signal + thread-3 release | 7 `id=30` lines, 4w/3s, ends parked (last @7226); t3 WAIT-30 ×1429 (blocks 1–1429; only RUN = block 0 @0x416934) | ABSENT (no 8th line, no release — holds to cap) |
| 3 | `0x362DE8` invocation halt | 72,176 / 72,176 balanced; last enter @185,264,853, last exit @185,264,992; 12,338,112 post-phase lines, live frames at EOF = 0 | PRESENT (N = 72,176 reproduced; last lines +2 vs T13/T15) |
| 4 | New caller | Single caller `sub_00363490` ×72,176; any-other 0; post-only trace functions 0 (113 ⊆ 1,073) | ABSENT (holds over 12.34 M post lines) |
| 5 | dma/gif slope break | ratio 0.02703 ±0.0001 on 105 of 106 nonzero deltas (partial step 0.027142, tabled); partial step (8437/229, ticks 12720→12840) then FROZEN 887 pairs (0/0, ticks 12960→119280) at 2669132/72181 | PRESENT (freeze counters T13-exact; extended hold) |

End state at cap SIGTERM: main dormant (status 5, pc 0x0, blocks
239–1429); t3 WAIT-30; t6 WAIT-36; boot log ends on a complete
`id=31 … result=park` line with trailing newline (waker=4);
trace ends with empty stack (all 1,073 functions enter=exit);
29w/s29 72178/72178 balanced; 30w/s30 4/3 parked; 31w/s31
431926/431925 (+1 in-flight).

## T16-2. Next-event table (NONE — third absence window with a bound) + N + rate table

First post-241 event: NONE. All 12 watches + 2 gated extras ran
armed over blocks 242–1429 (1188 blocks, ~5,990 s wall, log lines
2,499,728–4,315,920, 359,748 drain iters):

| # | Watch | Bound observed | Fired? |
|---|---|---|---|
| 1 | Main wake from dormant | t1 status 5 pc 0x0 ×1191 (blocks 239–1429, no other sample) | NO |
| 2 | New stub phase after residue-13 | distinct 13 ×1190 (blocks 240–1429, same 13 addresses) | NO |
| 3 | First new guest event (drop/RPC/CD/SIF/GS) | 0 of each in lines ≥2,463,373 (lasts all < line 7,226) | NO |
| 4 | New caller | 0 `0x362DE8` enters post-phase (last @185,264,853); caller census single ×72,176 | NO |
| 5 | dma/gif unfreeze | 887 consecutive 0/0 pairs (ticks 12960–119280) at 2669132/72181 | NO |
| 6 | 31-drain end (pump fully idle) | 31w 294–308 every complete post block (min 294 @b325/329/712/745/1329…; b1429 partial 47, SIGTERM-cut; never 0) | NO |
| 7 | Second halt (trace stall 120 s) | trace grows every poll to EOF (+~1 MB/15 s; final bytes = file size) | NO |
| 8 | W4 second dormant id=1 | total id=1 = 1 (@2494972) | NO |
| 9 | W10 stub firstRa≠lastRa (≤30-distinct) | all 13 equal in b240/b241/b1429 samples; live scan of every ≤30-distinct row silent | NO |
| 10 | W11 rate-shape post-241 | per-block d31 1.997–2.050 (1187 POST lines); per-slice d/31w 2.013–2.035; in-phase d/inv 2.10–2.13 (never 2.0000 — pre-exit, logged only) | NO |
| 11 | T3 29-resume post-halt | 29w = 0 every block 239–1429 (29s = 0) | NO |
| 12 | T4 extra 31-signals | s31−w31 = −1 total; per-block max +1 (@b251, alternation phase; trip needs >+2) | NO |
| 13 | W8b waiter status-5 (ids 4/5/6) | status=5 ×1191, ALL id=1 (0 for ids 2–6) | NO |
| 14 | syscall-new (T2/T10 latent) | post-241 syscalls exactly 1187× {0x44, 0xffffffbd} (+ b1429 section same 2 ids) | NO |
| + | sema30 8th line (gated) | n=7 all run, last @7226 | NO |
| + | thread-3 release (gated) | WAIT-30 ×1429, no RUN past block 0 | NO |

| Item | Value |
|---|---|
| Empirical `N` | 72,176 (`0x362DE8` enters = exits; first enter @19,385 — exact baseline; last enter @185,264,853; last exit @185,264,992) |
| Trace totals | 394ED0 1,442,182 / 395000 1,370,006 = N×20/19 − 1,338 each (T13's −1,338 constant reproduced to the digit) |
| Ramp (real per-inv join) | non-20/19 = exactly ordinals 0–74 (n=75): ords 0–51 @2/1, ords 52–63 @3/2, ords 64–74 @2/1 |
| Steady per-inv | ordinals 75–72,175 (72,101 invs) ALL exactly 20/19 |
| 362CC8 / caller | 72,177 (N+1; exactly 1 post-phase = 2 lines) / `sub_00363490` 216,528/216,528 = 3N exact balanced |
| 1000-chunks | chunk-0 18642/17643/1000/5234034 (BIT-EXACT vs T11/T13/T15); chunks 1–69 exact 20000/19000/1000/2534000; chunks 70–71 same-enters short-SPAN 2520494/2302066 (chunk-71 span +2 vs T13's 2302064 — boundary shift); tail 3540/3363/177 (span 12,700,510 incl. 12.34 M post lines — boundary artifact + post window) |

Growth arithmetic (P1ah pump-proxy method; proxy valid in-phase
only — 31 decouples post-exit; `blocks.tsv` carries per-block rows):

| Slice | Blocks | Wall (≈) | Pump waits | Invoc proxy | Rate (/s) | Dormant | Dormant/inv |
|---|---|---|---|---|---|---|---|
|| 0 | 0–11 | 0–60 s | 7,687 | 3,843 | 64.06 | 8,080 | 2.102 |
|| 1 | 12–23 | 60–120 s | 7,218 | 3,609 | 60.15 | 7,654 | 2.121 |
|| 2 | 24–35 | 120–180 s | 7,219 | 3,609 | 60.16 | 7,631 | 2.114 |
|| 3 | 36–47 | 180–240 s | 7,225 | 3,612 | 60.21 | 7,653 | 2.118 |
|| 4 | 48–59 | 240–300 s | 7,230 | 3,615 | 60.25 | 7,666 | 2.121 |
|| 5 | 60–71 | 300–360 s | 7,229 | 3,614 | 60.24 | 7,691 | 2.128 |
|| 6 | 72–83 | 360–420 s | 7,209 | 3,604 | 60.08 | 7,633 | 2.118 |
|| 7 | 84–95 | 420–480 s | 7,226 | 3,613 | 60.22 | 7,652 | 2.118 |
|| 8 | 96–107 | 480–540 s | 7,242 | 3,621 | 60.35 | 7,666 | 2.117 |
|| 9 | 108–119 | 540–600 s | 7,222 | 3,611 | 60.18 | 7,672 | 2.125 |
|| 10 | 120–131 | 600–660 s | 7,215 | 3,607 | 60.12 | 7,651 | 2.121 |
|| 11 | 132–143 | 660–720 s | 7,233 | 3,616 | 60.27 | 7,676 | 2.122 |
|| 12 | 144–155 | 720–780 s | 7,228 | 3,614 | 60.23 | 7,641 | 2.114 |
|| 13 | 156–167 | 780–840 s | 7,224 | 3,612 | 60.20 | 7,661 | 2.121 |
|| 14 | 168–179 | 840–900 s | 7,223 | 3,611 | 60.19 | 7,655 | 2.120 |
|| 15 | 180–191 | 900–960 s | 7,219 | 3,609 | 60.16 | 7,669 | 2.125 |
|| 16 | 192–203 | 960–1020 s | 7,217 | 3,608 | 60.14 | 7,646 | 2.119 |
|| 17 | 204–215 | 1020–1080 s | 7,235 | 3,617 | 60.29 | 7,657 | 2.117 |
|| 18 | 216–227 | 1080–1140 s | 7,227 | 3,613 | 60.23 | 7,676 | 2.124 |
|| 19 | 228–239 | 1140–1200 s | 6,900 | 3,450 | 57.50 | 7,467 | 2.164 ‡ |
|| 20 | 240–251 | 1200–1260 s | 3,623 | 1,811 | 30.19 | 7,305 | 4.033 ‡ |
|| 21 | 252–263 | 1260–1320 s | 3,619 | 1,809 | 30.16 | 7,288 | 4.028 ‡ |
|| 22 | 264–275 | 1320–1380 s | 3,640 | 1,820 | 30.33 | 7,344 | 4.035 ‡ |
|| 23 | 276–287 | 1380–1440 s | 3,633 | 1,816 | 30.27 | 7,316 | 4.028 ‡ |
|| 24 | 288–299 | 1440–1500 s | 3,620 | 1,810 | 30.17 | 7,296 | 4.031 ‡ |
|| 25 | 300–311 | 1500–1560 s | 3,625 | 1,812 | 30.21 | 7,309 | 4.033 ‡ |
|| 26 | 312–323 | 1560–1620 s | 3,625 | 1,812 | 30.21 | 7,316 | 4.036 ‡ |
|| 27 | 324–335 | 1620–1680 s | 3,614 | 1,807 | 30.12 | 7,294 | 4.037 ‡ |
|| 28 | 336–347 | 1680–1740 s | 3,616 | 1,808 | 30.13 | 7,299 | 4.037 ‡ |
|| 29 | 348–359 | 1740–1800 s | 3,635 | 1,817 | 30.29 | 7,322 | 4.029 ‡ |
|| 30 | 360–371 | 1800–1860 s | 3,637 | 1,818 | 30.31 | 7,337 | 4.035 ‡ |
|| 31 | 372–383 | 1860–1920 s | 3,627 | 1,813 | 30.23 | 7,322 | 4.037 ‡ |
|| 32 | 384–395 | 1920–1980 s | 3,628 | 1,814 | 30.23 | 7,315 | 4.033 ‡ |
|| 33 | 396–407 | 1980–2040 s | 3,628 | 1,814 | 30.23 | 7,309 | 4.029 ‡ |
|| 34 | 408–419 | 2040–2100 s | 3,633 | 1,816 | 30.27 | 7,325 | 4.032 ‡ |
|| 35 | 420–431 | 2100–2160 s | 3,635 | 1,817 | 30.29 | 7,321 | 4.028 ‡ |
|| 36 | 432–443 | 2160–2220 s | 3,627 | 1,813 | 30.23 | 7,325 | 4.039 ‡ |
|| 37 | 444–455 | 2220–2280 s | 3,635 | 1,817 | 30.29 | 7,328 | 4.032 ‡ |
|| 38 | 456–467 | 2280–2340 s | 3,634 | 1,817 | 30.28 | 7,322 | 4.030 ‡ |
|| 39 | 468–479 | 2340–2400 s | 3,636 | 1,818 | 30.30 | 7,344 | 4.040 ‡ |
|| 40 | 480–491 | 2400–2460 s | 3,640 | 1,820 | 30.33 | 7,353 | 4.040 ‡ |
|| 41 | 492–503 | 2460–2520 s | 3,625 | 1,812 | 30.21 | 7,314 | 4.035 ‡ |
|| 42 | 504–515 | 2520–2580 s | 3,637 | 1,818 | 30.31 | 7,338 | 4.035 ‡ |
|| 43 | 516–527 | 2580–2640 s | 3,631 | 1,815 | 30.26 | 7,329 | 4.037 ‡ |
|| 44 | 528–539 | 2640–2700 s | 3,614 | 1,807 | 30.12 | 7,354 | 4.070 ‡ |
|| 45 | 540–551 | 2700–2760 s | 3,620 | 1,810 | 30.17 | 7,359 | 4.066 ‡ |
|| 46 | 552–563 | 2760–2820 s | 3,618 | 1,809 | 30.15 | 7,340 | 4.057 ‡ |
|| 47 | 564–575 | 2820–2880 s | 3,619 | 1,809 | 30.16 | 7,336 | 4.054 ‡ |
|| 48 | 576–587 | 2880–2940 s | 3,606 | 1,803 | 30.05 | 7,313 | 4.056 ‡ |
|| 49 | 588–599 | 2940–3000 s | 3,621 | 1,810 | 30.18 | 7,309 | 4.037 ‡ |
|| 50 | 600–611 | 3000–3060 s | 3,634 | 1,817 | 30.28 | 7,339 | 4.039 ‡ |
|| 51 | 612–623 | 3060–3120 s | 3,632 | 1,816 | 30.27 | 7,313 | 4.027 ‡ |
|| 52 | 624–635 | 3120–3180 s | 3,634 | 1,817 | 30.28 | 7,326 | 4.032 ‡ |
|| 53 | 636–647 | 3180–3240 s | 3,620 | 1,810 | 30.17 | 7,300 | 4.033 ‡ |
|| 54 | 648–659 | 3240–3300 s | 3,628 | 1,814 | 30.23 | 7,312 | 4.031 ‡ |
|| 55 | 660–671 | 3300–3360 s | 3,637 | 1,818 | 30.31 | 7,353 | 4.043 ‡ |
|| 56 | 672–683 | 3360–3420 s | 3,631 | 1,815 | 30.26 | 7,321 | 4.032 ‡ |
|| 57 | 684–695 | 3420–3480 s | 3,622 | 1,811 | 30.18 | 7,304 | 4.033 ‡ |
|| 58 | 696–707 | 3480–3540 s | 3,626 | 1,813 | 30.22 | 7,319 | 4.037 ‡ |
|| 59 | 708–719 | 3540–3600 s | 3,623 | 1,811 | 30.19 | 7,308 | 4.034 ‡ |
|| 60 | 720–731 | 3600–3660 s | 3,626 | 1,813 | 30.22 | 7,318 | 4.036 ‡ |
|| 61 | 732–743 | 3660–3720 s | 3,631 | 1,815 | 30.26 | 7,323 | 4.034 ‡ |
|| 62 | 744–755 | 3720–3780 s | 3,620 | 1,810 | 30.17 | 7,298 | 4.032 ‡ |
|| 63 | 756–767 | 3780–3840 s | 3,627 | 1,813 | 30.23 | 7,310 | 4.031 ‡ |
|| 64 | 768–779 | 3840–3900 s | 3,630 | 1,815 | 30.25 | 7,321 | 4.034 ‡ |
|| 65 | 780–791 | 3900–3960 s | 3,628 | 1,814 | 30.23 | 7,308 | 4.029 ‡ |
|| 66 | 792–803 | 3960–4020 s | 3,621 | 1,810 | 30.18 | 7,308 | 4.036 ‡ |
|| 67 | 804–815 | 4020–4080 s | 3,630 | 1,815 | 30.25 | 7,324 | 4.035 ‡ |
|| 68 | 816–827 | 4080–4140 s | 3,630 | 1,815 | 30.25 | 7,320 | 4.033 ‡ |
|| 69 | 828–839 | 4140–4200 s | 3,634 | 1,817 | 30.28 | 7,335 | 4.037 ‡ |
|| 70 | 840–851 | 4200–4260 s | 3,627 | 1,813 | 30.23 | 7,322 | 4.037 ‡ |
|| 71 | 852–863 | 4260–4320 s | 3,623 | 1,811 | 30.19 | 7,311 | 4.036 ‡ |
|| 72 | 864–875 | 4320–4380 s | 3,627 | 1,813 | 30.23 | 7,306 | 4.029 ‡ |
|| 73 | 876–887 | 4380–4440 s | 3,636 | 1,818 | 30.30 | 7,325 | 4.029 ‡ |
|| 74 | 888–899 | 4440–4500 s | 3,620 | 1,810 | 30.17 | 7,309 | 4.038 ‡ |
|| 75 | 900–911 | 4500–4560 s | 3,631 | 1,815 | 30.26 | 7,319 | 4.031 ‡ |
|| 76 | 912–923 | 4560–4620 s | 3,623 | 1,811 | 30.19 | 7,314 | 4.038 ‡ |
|| 77 | 924–935 | 4620–4680 s | 3,622 | 1,811 | 30.18 | 7,309 | 4.036 ‡ |
|| 78 | 936–947 | 4680–4740 s | 3,630 | 1,815 | 30.25 | 7,328 | 4.037 ‡ |
|| 79 | 948–959 | 4740–4800 s | 3,630 | 1,815 | 30.25 | 7,322 | 4.034 ‡ |
|| 80 | 960–971 | 4800–4860 s | 3,628 | 1,814 | 30.23 | 7,319 | 4.035 ‡ |
|| 81 | 972–983 | 4860–4920 s | 3,626 | 1,813 | 30.22 | 7,308 | 4.031 ‡ |
|| 82 | 984–995 | 4920–4980 s | 3,638 | 1,819 | 30.32 | 7,337 | 4.034 ‡ |
|| 83 | 996–1007 | 4980–5040 s | 3,620 | 1,810 | 30.17 | 7,332 | 4.051 ‡ |
|| 84 | 1008–1019 | 5040–5100 s | 3,619 | 1,809 | 30.16 | 7,339 | 4.056 ‡ |
|| 85 | 1020–1031 | 5100–5160 s | 3,623 | 1,811 | 30.19 | 7,345 | 4.055 ‡ |
|| 86 | 1032–1043 | 5160–5220 s | 3,618 | 1,809 | 30.15 | 7,356 | 4.066 ‡ |
|| 87 | 1044–1055 | 5220–5280 s | 3,613 | 1,806 | 30.11 | 7,334 | 4.060 ‡ |
|| 88 | 1056–1067 | 5280–5340 s | 3,618 | 1,809 | 30.15 | 7,334 | 4.054 ‡ |
|| 89 | 1068–1079 | 5340–5400 s | 3,627 | 1,813 | 30.23 | 7,333 | 4.044 ‡ |
|| 90 | 1080–1091 | 5400–5460 s | 3,629 | 1,814 | 30.24 | 7,332 | 4.041 ‡ |
|| 91 | 1092–1103 | 5460–5520 s | 3,622 | 1,811 | 30.18 | 7,305 | 4.034 ‡ |
|| 92 | 1104–1115 | 5520–5580 s | 3,634 | 1,817 | 30.28 | 7,349 | 4.045 ‡ |
|| 93 | 1116–1127 | 5580–5640 s | 3,628 | 1,814 | 30.23 | 7,306 | 4.028 ‡ |
|| 94 | 1128–1139 | 5640–5700 s | 3,620 | 1,810 | 30.17 | 7,297 | 4.031 ‡ |
|| 95 | 1140–1151 | 5700–5760 s | 3,633 | 1,816 | 30.27 | 7,337 | 4.039 ‡ |
|| 96 | 1152–1163 | 5760–5820 s | 3,624 | 1,812 | 30.20 | 7,308 | 4.033 ‡ |
|| 97 | 1164–1175 | 5820–5880 s | 3,616 | 1,808 | 30.13 | 7,289 | 4.032 ‡ |
|| 98 | 1176–1187 | 5880–5940 s | 3,622 | 1,811 | 30.18 | 7,311 | 4.037 ‡ |
|| 99 | 1188–1199 | 5940–6000 s | 3,630 | 1,815 | 30.25 | 7,333 | 4.040 ‡ |
|| 100 | 1200–1211 | 6000–6060 s | 3,637 | 1,818 | 30.31 | 7,329 | 4.030 ‡ |
|| 101 | 1212–1223 | 6060–6120 s | 3,635 | 1,817 | 30.29 | 7,328 | 4.032 ‡ |
|| 102 | 1224–1235 | 6120–6180 s | 3,631 | 1,815 | 30.26 | 7,323 | 4.034 ‡ |
|| 103 | 1236–1247 | 6180–6240 s | 3,628 | 1,814 | 30.23 | 7,326 | 4.039 ‡ |
|| 104 | 1248–1259 | 6240–6300 s | 3,627 | 1,813 | 30.23 | 7,317 | 4.035 ‡ |
|| 105 | 1260–1271 | 6300–6360 s | 3,632 | 1,816 | 30.27 | 7,311 | 4.026 ‡ |
|| 106 | 1272–1283 | 6360–6420 s | 3,633 | 1,816 | 30.27 | 7,335 | 4.038 ‡ |
|| 107 | 1284–1295 | 6420–6480 s | 3,625 | 1,812 | 30.21 | 7,315 | 4.036 ‡ |
|| 108 | 1296–1307 | 6480–6540 s | 3,633 | 1,816 | 30.27 | 7,326 | 4.033 ‡ |
|| 109 | 1308–1319 | 6540–6600 s | 3,620 | 1,810 | 30.17 | 7,298 | 4.032 ‡ |
|| 110 | 1320–1331 | 6600–6660 s | 3,630 | 1,815 | 30.25 | 7,321 | 4.034 ‡ |
|| 111 | 1332–1343 | 6660–6720 s | 3,629 | 1,814 | 30.24 | 7,324 | 4.036 ‡ |
|| 112 | 1344–1355 | 6720–6780 s | 3,627 | 1,813 | 30.23 | 7,309 | 4.030 ‡ |
|| 113 | 1356–1367 | 6780–6840 s | 3,632 | 1,816 | 30.27 | 7,321 | 4.031 ‡ |
|| 114 | 1368–1379 | 6840–6900 s | 3,631 | 1,815 | 30.26 | 7,319 | 4.031 ‡ |
|| 115 | 1380–1391 | 6900–6960 s | 3,629 | 1,814 | 30.24 | 7,320 | 4.034 ‡ |
|| 116 | 1392–1403 | 6960–7020 s | 3,628 | 1,814 | 30.23 | 7,319 | 4.035 ‡ |
|| 117 | 1404–1415 | 7020–7080 s | 3,629 | 1,814 | 30.24 | 7,322 | 4.035 ‡ |
|| 118 | 1416–1427 | 7080–7140 s | 3,620 | 1,810 | 30.17 | 7,289 | 4.027 ‡ |
|| 119 | 1428–1429 | 7140–7150 s | 346 | 173 | 17.30 | 698 | 4.035 ‡ |

‡ Slices 19–119 span/exceed the exit: proxy ≠ invocations there
(29-halt); in-phase 29/31 blocks 0–237 = 71,873/71,872 (+1 29-side
window-boundary effect, tabled); pre-block-0 = 26/26 (T11/T13/T15
read 25/25 — fourth datum, +1 here);
block 238 = 279/299 transitional (T15's transitional was block 239
at 5/296; T13's at 117/298);
blocks 239–1429 = 0/359,729 (31-only). Post-exit dormant per
31-iteration ≈ 2.013–2.035 every full slice (T15's 2.014–2.021
reproduced).

Handshake↔trace identities (exact): 29w total 72,178 = N+2;
31w total 431,926; Δ(31−29) = 359,748 = post-phase 31-drain
iterations (9 trace functions × 359,749 markers — markers exceed Δ
by 1: the SIGTERM-cut final iter carries a marker but no handshake
lines yet, tabled). The +2 edge is unattributed (trace carries no
timestamps; tabled, not derived).

Wall-rate shape vs prior windows (numbers only): T16 flat ~60
(s1–18, no dip/surge) → ~30.2 proxy (s20–118, 31-only) → cap;
same shape class as T15 (second flat→30.2 datum); T13 flat ~60 →
dip ~48 → rebound → ~2× surge ~104 → exit; T11 smooth 64→36 decay;
P1ag flat 33–5× step.

E1 bound math (P33-4b check): cap 7200 s → 359,748 iters over the
~5,990 s post window (≈60.1/s ≈ 1/VBLANK); 5.01× T15's 71,762
(P33-4b projected ~430,000 ≈ 6.0× assuming a full 7200 s drain
window — the in-phase ~1,190 s does not contribute; tabled).

E1 miner rows (§P33-4a: drain iters + 3E4AF0 gaps + halt-split trio
+ bLast residue + per-1000 chunks + N2):

| Row | Value |
|---|---|
| Drain iters Δ(31−29) | 359,748 (431,926 − 72,178) |
| Drain iters (trace markers) | 359,749 depth-0 `31A3C0` enters (first @185,265,559, last @197,603,077; +1 vs Δ — final cut iter) |
| 3E4AF0 gap histogram | 6:9140 + 7:43557 (n=52,697 inter-arrival gaps; min 6 max 7; gaps outside {6,7} = NONE) |
| 3E4AF0 per-1000 cadence | 146/147 alternating (359 full chunks) + 110 in final 749-iter chunk; 52,698 in-iter + 1 pre-marker = 52,699 post enters |
| Halt-split trio | last-29 @2,494,970 / first-post-31 @2,494,971 / dormant-id=1 @2,494,972 — ADJACENT (+0/+1/+2); last-29 shape `waker=4 ra=0x31aae4`, last-29-wait @2,494,956 (`waker=1 ra=0x31aa8c`) |
| Halt position | 97.85% through window 238 (span 2,489,103–2,495,099); dormant sched=559 = b239 t1 scheduled (t1/t5 b234–242: 603/604, 596/595, 601/601, 607/607, 598/598, 559/559, 0/0, 0/0, 0/0) |
| bLast (1429) residue | 13; 598×3+299×10; all firstRa==lastRa (same targets+ras as T13/T15) |
| Per-1000 chunk table | 360 chunks (§P33-2a schema): chunk 0 = iters 1–1000, 34,982 lines (T15-exact), 55 distinct (340-enter/40-distinct finite tail ALL in iter 1, buckets 101–1000 = 0; last resid iter 1 @185,266,275); chunks 1–358 = 15 distinct, 34.292–34.294 lines/iter, 9-fam 1.0000/iter; chunk 359 = iters 359001–359749 (749), 25,680 lines (34.286/iter), 15 distinct |
| First/last iteration | iter 1 = 724 lines (steady-15 + finite tail); iters 2–359,748 = fixed point; iter 359,749 = 28 lines (31A3C0-leg + 423DE0 + 31AAF0-direct leg complete; 37E120/3825F8/3C1638 pairs missing — SIGTERM between root dispatches; every enter balanced) |
| N2 (post-boot 362DE8) | 72,176 = N (0 post-phase enters; no second invocation phase) |

## T16-3. Post-exit state table (threads, drain, freeze — cap)

| Row | T15 (cap, b476 end) | T16 (cap, b1429 end) |
|---|---|---|
| Thread-1 end | 55 RUN + 20 mid + 165 W29 + 237 dormant-5 (end: status 5 pc 0x0, blocks 240–476 — main STAYS returned) | 46 RUN + 26 mid + 167 W29 + 1191 dormant-5 (end: status 5 pc 0x0, blocks 239–1429 — main STAYS returned, dormant one block early) |
| Thread-1 RUN pcs | base set (0x186c04/0x2c6074/0x39b72c/0x38f364/0x3778ec/0x38f354) + 0x232d34/0x23d688/0x39ee8c (transient samples; no 0x36356c this run) | base set (0x2c6074/0x186c04/0x38f364/0x39b72c/0x376b64/0x38f354) + 0x3a0714 (sub_003A04F0+0x224, NEW this run) + 0x363bec/0x3778ec/0x39e72c (transient samples; no 0x36356c this run) |
| Thread-3 | WAIT-30 ×476 + RUN b0 (@0x2ab2bc — transient pc differs) — NO release to cap | WAIT-30 ×1429 + RUN b0 (@0x416934 = T11's pc) — NO release to cap |
| Thread-6 | WAIT-36 ×477 | WAIT-36 ×1430 |
| New drops / RPC / CD / SIF / GS | none past block 2 | none past block 2 (exit-region audit ≥line 2,463,373: drops 0, RPC 0, CD 0, SIF 0, GS 0; totals 6/4/810/21/96 = baselines) |
| Post-phase trace | 2,462,182 lines, 113 distinct (SAME set), 0 post-only; top: 423DE0 ×287070, 31AAF0 ×287048, 326EB0 ×287048, 31A6B8 ×143540, 423DD0 ×143528, 9-func ×143524 drain family (71,762 iters), 3E4AF0 ×21026; 394/395 ×0; 362CC8 ×2 lines (1 inv); ends EMPTY stack | 12,338,112 lines, 113 distinct (SAME set), 0 post-only; top: 423DE0 ×719509, 31AAF0 ×719498, 326EB0 ×719498, 31A6B8 ×359757, 423DD0 ×359751, 9-func ×359749 drain family (359,749 iters), 3E4AF0 ×105398 lines (52,699 enters: 52,698 in-iter + 1 pre-marker); 394/395 ×0; 362CC8 ×2 lines (1 inv); ends EMPTY stack |
| 29/31 pump | balanced blocks 0–238 (72,148/72,148); 29 halts (5/0/…0, last signal @2,494,022), 31 drains on (296–307 ×237 blocks); log tail = live `id=31 … result=park` (waker=4), clean trailing newline | balanced blocks 0–237 (71,873/71,872); 29 halts in b238 (279/299, last signal @2,494,970, 97.85% through window), 31 drains on (294–308 ×1190 blocks); log tail = live `id=31 … result=park` (waker=4), clean trailing newline |
| dma/gif | ratio 0.02703 ±0.0001 (106 deltas) → partial (13802/374) → FROZEN (0/0, 160 pairs, ticks 12960–32040) at same 2669132/72181 | ratio 0.02703 ±0.0001 (105 of 106 deltas; partial-step delta 0.027142) → partial (8437/229) → FROZEN (0/0, 887 pairs, ticks 12960–119280) at same 2669132/72181 |
| Stub end state | 222 ×233 → collapse → 13 ×236 (b241–476; b476 residue SAME 13 addresses @598/299) | 222 ×233 → collapse → 13 ×1190 (b240–1429; b1429 residue SAME 13 addresses @598/299 = T15-b476-exact; first residue b240 @610/305 = T15-b241-exact) |

Main pc-sample histogram (1430 samples):

| status | pc | n | Attribution |
|---|---|---|---|
| 5 DORMANT | `0x0` | 1191 | main returned (blocks 239–1429) |
| 2 WAIT-29 | `0x423de8` | 167 | pump sample |
| 1 mid-syscall | `0x423dc8` | 25 | syscall entry |
| 0 RUNNING | `0x2c6074` | 16 | `sub_002C5570+0xb04` |
| 0 RUNNING | `0x186c04` | 12 | `sub_00186A08+0x1fc` |
| 0 RUNNING | `0x38f364` | 5 | `sub_0038F300+0x64` |
| 0 RUNNING | `0x39b72c` | 4 | `sub_0039AE98+0x894` |
| 0 RUNNING | `0x3a0714` | 2 | `sub_003A04F0+0x224` (new this run) |
| 0 RUNNING | `0x376b64` | 2 | `sub_00376938+0x22c` |
| 0 RUNNING | `0x38f354` | 2 | `sub_0038F300+0x54` |
| 0 RUNNING | `0x363bec` | 1 | `sub_00363490+0x75c` |
| 0 RUNNING | `0x3778ec` | 1 | `sub_00376938+0xfb4` |
| 0 RUNNING | `0x39e72c` | 1 | `sub_0039E6B8+0x74` |
| 1 mid-syscall | `0x423de8` | 1 | syscall wait addr |

CD/SIF/GS/RPC silence audit (stub markers b0/b1/b2 @lines
5,702/34,253/50,609; all lasts < line 7,226; zero new events in
lines 50,609–4,315,920 and zero in exit region ≥2,463,373):

| Source | n | Last line | Position vs markers | New past block 2 |
|---|---|---|---|---|
| CD `lbn=` | 810 | 7,176 | b0 span (5,702–34,253) | none |
| SIF loads | 21 | 1,055 | pre-b0 (< 5,702) | none |
| GS kicks | 96 | 2,638 | pre-b0 (< 5,702) | none |
| RPC unhandled | 4 | 5,143 | pre-b0 (< 5,702) | none |
| Sema-30 events | 7 | 7,226 | b0 span (5,702–34,253) | none |

## T16-4. Baselines-kept table (per-row exact-vs-baseline)

| Baseline (source) | T16 observed | Row |
|---|---|---|
| 54-frame modal cycle REP+53 (T10) | modal len 53 ×70,850/72,175 gaps; all 53 slots byte-identical (E @42, C1a#2 @52); class uniformity 70,850/70,850 per `376938` slot | exact (in-phase) |
| 31 gap patterns, ramp ordinals 0–74 (T10) | 36 patterns; boot non-modal = exactly ordinals 0–74 (same set as T11/T13/T15) | exact + exit tail (below) |
| Exit-tail gap regime (T13) | 1,250 tail gaps from first_rep 70722: 1241× len-52 (modal−1) + 6× len-53-alt + singletons len 58/56/58 (reps 70857/71014/71526) | DEVIATION: third singleton len 58, not T13/T15's 57 |
| Class offsets +5/+15/+16/+18/+42/+52 (T10) | C3 +5 ×72176; C7 +15 ×72176; C1a#1 +16 ×72176; C1b +18 ×72176; E @42 ×70856 + @41 ×1242; C1a#2 @52 ×70856 + @51 ×1241 | exact + tail shift |
| E-double gaps 51–62; C1a-extra 0–50 (T10) | E-double ordinals [51..62] exact; C1a×3 in 51 gaps exact; OTHER ×1 (post-phase singleton) | exact + 1 post |
| 20/19/1/2534 per invocation (P1ah) | 69 chunks exact + chunk-0 bit-exact + real-join 75–72175 all exact; chunks 70–71 same-enters short-span (2520494/2302066 — chunk-71 span +2 vs T13); tail-window 177-in-176 (join authoritative) | exact (per-inv) |
| Stubs 222 (P1ag) | 222 ×233 (blocks 2–234) | exact pre-exit |
| Stub preamble b0–b1 (T11: 961/497; T13: 897/588; T15: 887/603) | b0=961, b1=497, steady @b2 | DEVIATION set: T11-exact repeat (fourth pair, second distinct value) |
| Sema-30 4w/3s parked (P1ag) | 7 lines, 4w/3s, ends parked (@643/645/646/706/6974/7024/7226; first four = P1af's, last three +2/+1/+1 vs T15) | exact shape, shifted lines |
| FRR ×N, 0 deviations (T8) | FRR ×72,176, 0 deviations; `363490` 216,528/216,528 = 3N exact | exact |
| Single caller `0x363490` (P1ah) | ×72,176, other 0 | exact |
| Probe change points 104/140/162 (P1ah) | 104/140/162 @7592/7981/8272; `total→0x14` sat.; cap line @62119 (`cap=20000 reached`; T13 :62111, T15 :62107, T11 :62113, P1ag :62604) | exact |
| Probe NULL-head 3136 (T11) | 3135 | DEVIATION (−1) |
| Probe pool drops 1066, arenas 1, buckets 5 | 1066 / 1 (`0x8095f0`) / 5, CYCLE@ 0 | exact |
| Drops 6 @:68–73 KE_ERROR 0x5b | 6 @:68–73, same site | exact |
| RPC unhandled 4 | 4 @:711/:1056/:1062/:5143 (T13's exact lines) | exact |
| SendCmd 1 / handshake 2 / `0x3C45C0` 0 | 1 @:1052 (T13's line) / 2 / 0 | exact |
| CD 810 `0x10`→`0x4311f` | 810, same span (:105–:7176, last +1 vs T15) | exact |
| SIF 21 loads id 1–21 | 21, id 1–21 in order, last @:1055 (T13's line) | exact |
| Creates 37 / `-1` waits 0 | 37 / 0 (`op=wait … waker=-1`) | exact |
| Driver-entry 98 | 98 | exact |
| GS 96 / copy 64 / gif 48 / drawing=1 96 | 96 / 64 / 48 (=1042 broad-`gif` − 994 ticks) / 96 | exact |
| Missing-target 1, JALR `0x2322d4→0x395730` | 1 @:660, same bytes | exact |
| Crash / FATAL / presented frame 0 | 0 / 0 / 0 | exact |
| Thread-3: RUNNING pre-pump → WAIT-30 | RUNNING ×1 (block 0, pc `0x416934`) → WAIT-30 ×1429 | DEVIATION in transient pc only (= T11's pc) |
| Thread-6: WAIT-36 all blocks | WAIT-36 ×1430 | exact |
| First `0x362DE8` enter @ trace line 19,385 | @19,385 | exact |
| Stack mismatches 0 / max depth 29 | 0 / 29 | exact |
| Live frames at EOF | 0 (empty stack; all 1,073 funcs balanced — SIGTERM at cap landed between root dispatches, as in T13/T15) | same-as-T13/T15 |
| Pre-first-rep 294 frames, 3×C1a+1×E | 294, 3×C1a+1×E | exact |
| Post-last-rep | 1,851,473 frames (C3/C7/C1a/C1b ×1 each; T15: 369,352) | NEW (extended drain window; = drain depth-0 total exact) |
| Dormant/inv 2.000 (T11 slices 2+) | 2.102–2.128 slices 0–18 (never 2.0000); post d/31w 2.013–2.035 | DEVIATION (exact-2.0000 regime absent) |
| Freeze counters 2669132/72181 (T13) | identical counters; 887 frozen pairs (T15: 160 pairs) | exact counters, extended freeze |

## T16-5. Absence-window ladder + post-exit rung (P1af / P1ag / T11 / T13 / T15 / T16)

| Rung | P1af (90 s) | P1ag (300 s) | T11 (600 s) | T13 (~1,218 s, EXIT) | T15 (2,400 s, CAP past exit) | T16 (7,200 s, CAP past exit) |
|---|---|---|---|---|---|---|
| Lines / bytes | 207,189 / 36,650,891 | 475,304 / 84,053,701 | 1,036,373 / 184,691,472 | 2,493,828 / 448,535,827 | 2,857,096 / 602,908,868 | 4,315,920 / 1,216,689,154 |
| Trace lines / bytes | 16,103,012 / 572,136,194 | 35,916,072 / 1,275,797,618 | 77,374,859 / 2,748,206,218 | 185,293,022 / 6,581,094,749 | 187,727,172 / 6,659,595,180 | 197,603,104 / 6,978,090,314 |
| Stub / thread / syscall blocks | 17 / 17 / 17 | 59 / 59 / 59 | 119 / 119 / 119 | 242 / 242 / 242 | 477 / 477 / 477 | 1430 / 1430 / 1430 |
| Park/exit onset | NONE (222 ×15) | NONE (222 ×54) | NONE (222 ×117) | EXIT block 235 (218→211→189→13) | EXIT b235 reproduced; NO post event b242–476 (13 ×236) | EXIT b235 reproduced; NO post event b242–1429 (13 ×1190 from b240) |
| Thread-1 | 6 RUN + 11 W29 (end: RUN) | 41 RUN + 12 mid + 6 W29 (end: W29) | 65 RUN + 18 mid + 36 W29 (end: mid) | 105 RUN + 45 mid + 90 W29 + 2 dormant (end: DORMANT) | 55 RUN + 20 mid + 165 W29 + 237 dormant (end: DORMANT) | 46 RUN + 26 mid + 167 W29 + 1191 dormant (end: DORMANT) |
| Thread-3 | WAIT-30 ×16 + RUN b0 | WAIT-30 ×56 + RUN b0–b1 | WAIT-30 ×118 + RUN b0 | WAIT-30 ×241 + RUN b0 (no release) | WAIT-30 ×476 + RUN b0 (no release) | WAIT-30 ×1429 + RUN b0 (no release) |
| Thread-6 | WAIT-36 ×17 | WAIT-36 ×57 | WAIT-36 ×119 | WAIT-36 ×242 | WAIT-36 ×477 | WAIT-36 ×1430 |
| 29-handshake w/s | 5291 / 5290 | 13109 / 13109 | 29470 / 29470 | 72178 / 72178 (= N+2) | 72178 / 72178 (= N+2, identical) | 72178 / 72178 (= N+2, identical) |
| 30-handshake w/s | 4 / 3 (parked) | 4 / 3 (parked) | 4 / 3 (parked) | 4 / 3 (parked — exit needs no 4th) | 4 / 3 (parked to cap) | 4 / 3 (parked to cap) |
| 31-handshake w/s | 5291 / 5290 | 13110 / 13109 | 29471 / 29470 | 72959 / 72958 (+781 post drain) | 143940 / 143939 (+71,762 post drain) | 431926 / 431925 (+359,748 post drain) |
| 4th sema-30 signal | Absent | Absent | Absent | Absent (even at exit) | Absent (to cap) | Absent (to cap) |
| `0x394ED0` trace | 104,442 (= 20N−1338) | 260,822 / 260,822 | 588,042 / 588,042 | 1,442,182 / 1,442,182 (= 20N−1338) | 1,442,182 / 1,442,182 (= 20N−1338) | 1,442,182 / 1,442,182 (= 20N−1338) |
| `0x362DE8`/`0x362CC8` trace | 5289 / 5290 (CC8 = N+1) | 13108 / 13108 | 29469 / 29469 | 72176 / 72177 (CC8 = N+1) | 72176 / 72177 (CC8 = N+1) | 72176 / 72177 (CC8 = N+1) |
| `0x395000` trace | 99,153 (= 19N−1338) | 247714 / 247714 | 558573 / 558573 | 1370006 / 1370006 (= 19N−1338) | 1370006 / 1370006 (= 19N−1338) | 1370006 / 1370006 (= 19N−1338) |
| `run:tick` | 7 ticks | 37 ticks | 78 ticks | 166 ticks, dma 22188→2669132, gif 641→72181, freeze at end | 267 ticks, dma 23858→2669132, gif 687→72181, frozen 160 pairs | 994 ticks, dma 21929→2669132, gif 634→72181, frozen 887 pairs |
| Dormant / start-thread | 11160 / 5 | 26209 / 5 | 59553 / 5 | 149339 / 5 | 296503 / 5 | 878923 / 5 |
| Wall-rate shape | ~59/s uncontended | flat + step @~245 s | 64→36 decay | flat ~60 → dip ~48 → rebound → ~2× surge → exit | flat ~60 → ~30.2 (31-only) → cap | flat ~60 → ~30.2 (31-only) → cap (T15 class) |
| Bound / N | N > 5,289 | N > 13,108 | N > 29,469 | N = 72,176 (empirical) | N = 72,176 + post bound (no event 235 blocks past b241) | N = 72,176 + post bound (no event 1188 blocks past b241) |

## T16-6. Exact commands

From `/Users/bradrichardson/dev/ssx3` unless noted; `$W`, `R`
quoted (path contains a space):

```text
# Tree state + Part-33 check (lease-free)
git rev-parse HEAD; git log --oneline -3; git status --porcelain=v1
git -C "$R" rev-parse HEAD; git -C "$R" log --oneline -3; git -C "$R" branch --show-current; git -C "$R" status --porcelain=v1
git -C "$R" diff --stat; find "$R" -name "._*" | wc -l (13)
grep "^## Part 33" local/research/P1/REPORT.md (landed -> P1aj E1 rows used)
# Scripts (lease-free)
sed /tmp/t15-boot1.py -> /tmp/t16-boot1.py (T15->T16 + t15->t16 + 2400->7200; diff-verified)
sed /tmp/t15-monitor.py -> /tmp/t16-monitor.py (names) + signature-row edits (W4/W10/W11/T3/T4/W8b/syscall-new; diff-verified)
cp /tmp/t15-{trace,mine,blocks,rates,cycle,tail}.py /tmp/t16-*.py (byte-identical, no edits)
sed /tmp/p1aj/trace_drain.py -> /tmp/t16-drain.py (BOUND 185264992 + out paths; diff-verified)
write /tmp/t16-drain2.py (streaming merge of p1aj drain2+drain3: 120MB tail window too small for 12.3M post lines)
python3 -m py_compile (t16-boot1 + t16-monitor + 6 miners + 2 drain miners, OK)
predicate self-test vs T15 data (/tmp/t16-selftest.py execs real scan_chunk: silent on 2,857,096 lines; 9/9 grafts fire)
# Pre-claim checks (12:10:10Z; lease-free)
ls /tmp/ssx3-p-lane-lease (absent); pgrep -x ps2EntryRunner (exit 1)
shasum -a 256 /tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner (81bee6c5..., 163460272 B)
stat ISO + ELF (3005415424 + 3890784 B); df (524 Gi free); t13/t14/t15-waits tails
# Boot (lease T16 held 12:10:28Z-14:12:16Z only)
printf 'T16' > lease + >> t16-waits.log (claim 12:10:28Z)
python3 /tmp/t16-monitor.py (managed session from 12:10:32Z; verified alive + log header)
python3 /tmp/t16-boot1.py (foreground; INVARIANT b235 logged, NO trigger; SIGTERM after 7200s rc=-15; script exit 241)
>> t16-waits.log (release 14:12:16Z); rm lease; verify absent; pgrep exit 1
cp ps2_log.txt ps2_log-t16-1.txt (lease-free; 197603104 lines, 6978090314 B)
# Analysis (lease released)
python3 /tmp/t16-blocks.py LOG (stub series, t1/t3/t6 series, handshakes)
python3 /tmp/t16-mine.py boot-t16-1.log (probe/sema/drops/census/threads/ticks)
python3 /tmp/t16-rates.py LOG (per-block pump + per-60 s slices + ticks + sema30)
wc -l T; grep -c sub_00362DE8/enter+exit (72176/72176); first enter @19385
python3 /tmp/t16-trace.py T 197603104 (caller census + chunks + tenths + balance)
python3 /tmp/t16-cycle.py T (gate + FRR + modal slots + offsets + pre/post)
python3 /tmp/t16-tail.py T (P1ah-bisect per-inv 394/395 join, full 0-72175 + ramp detail)
python3 /tmp/t16-drain.py T (boundary verify, post census, 31A3C0 markers, per-1000 chunks, edge iters)
python3 /tmp/t16-drain2.py T (chunk distinct/3e series, 3E4AF0 gaps, chunk-0 buckets, final iter)
grep rows (probe cap/change points/SendCmd/SIF/dormant/gif/copy/missing/fatal/drops/CD/GS/RPC lasts)
tick-delta + dormant-ratio joins (heredoc python); pre-first 394/395 (= 0/0)
halt-split trio (last-29/first-31/dormant adjacency); t1/t5 scheduled series b234-242
post-241 syscall census (1187x2 ids); b240/b241/b1429 residue rows (ra equality)
pc attribution via P1/output/ps2_recompiled_functions.h (bisect; 5 controls match T13)
blocks.tsv + ticks.tsv generators (heredoc python; 1430 + 994 rows; blocks 0-mismatch vs rates)
# Report (lease released)
(mkdir + write local/research/T16/REPORT.md + blocks.tsv + ticks.tsv; this file)
git add -f local/research/T16/REPORT.md local/research/T16/blocks.tsv local/research/T16/ticks.tsv
git commit -m "[T16] ..." (trailer Orchestrated-By: Muse Code; NO push)
```

## T16-7. What I could not do (gap rows)

- Read 3825F8's `*(a1+0x5A8C)` state (T4's first arm), any
  guard-word VALUES, or 326EB0's ~25 per-branch directions:
  fixed-by-count over 359,749 iters, values unprobed (E3 rows
  specified in §P33-4a; carried from P1aj §P33-6).
- Join trace chunks to log blocks (no timestamps in either stream):
  chunk↔block correspondence is rate-inferred (≈60/s both), not
  observed (same gap as T13 §T13-7/T15 §T15-7/P1aj §P33-6).
- Attribute the halt-position spread from inside the receipts —
  third datum: T13 74.1% through window 239, T15 9.1% through
  window 239, T16 97.85% through window 238 (no host-load log in
  scope; tabled as guest-fixed wall variation).
- Attribute the wall-rate flatness / dormant-ratio surplus host
  cause from inside the receipts (no host-load log in scope);
  tabled as guest-ratio-fixed wall variation (§T16-2), second
  flat→30.2 datum.
- Attribute the +2 29-side edge (72,178 waits vs 72,176
  invocations): the trace carries no timestamps (carried from
  T13/T15). The +1 in-phase 29-side window effect (blocks 0–237:
  71,873/71,872) and the +1 markers-vs-Δ effect (359,749 vs
  359,748) are tabled by exact count, not derived.
- Split block 238's transitional counts beyond the exact halt line
  (last 29-signal @2,494,970): the trace carries no timestamps
  (same gap as T15 §T15-7).
- Build the §P31-6b driver-loop `(i, N)` receipt (still unbuilt;
  moot for `N`, now thrice empirical) or see probe bodies past
  n=19999 (cap at :62119).
- Name the IOP announcer / decode `0x3C45C0`'s `0x1C`/`0x1D` arm
  semantics (carried from §P26-5/§P27-5/§P29-5/§P30-6/T11-7/T13-7/
  T15-7; 0 sightings).
- Session wall time ≈ 12:05–14:55Z (~2.8 h active), inside the
  6 h box; zero lease waits (no contention).

## Evidence files

`REPORT.md` (this file), `blocks.tsv` (1430 blocks ×
distinct/logline/pump/dormant), `ticks.tsv` (994 ticks ×
dma/gif/deltas/ratio, 887 FROZEN pairs).
