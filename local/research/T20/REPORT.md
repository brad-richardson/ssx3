# T20 report — channel-on drain census: drain-window EE stream vs T17 menu-loop stream (1 boot + align)

Brief `local/muse/prompts/T20.md`. Tables, no verdicts.
Stale-reading guard: `local/research/T18/REPORT.md` (all of it —
fork `f2b1852` `PS2X_TRACE_SYSCALLS` channel in PCSX2 byte shape,
non-perturbing ladder, `tools/trace_align.py` selftest 17/17, k=2
boot-phase divergence) + `local/research/T17/REPORT.md` §T17-2
(the menu-loop reference: sema/event/timer storm + per-vblank
`sceCdApplySCmd2` over 23,107 vblanks) + P1 REPORT Part 34 §P34-1c
(the drain's guard table + per-block bands) + `local/research/T16/
REPORT.md` (the exit invariant: block-235 collapse, residue-13,
N = 72,176) + `local/research/T13/REPORT.md` §T13-0 (pre-claim
checks verbatim).

`W=/Volumes/Extreme SSD/ps2recomp-spike`, `R=$W/PS2Recomp` (fork,
branch `ssx3`), `LOG=$W/P1/run/boot-t20-1.log` (3,221,278 lines,
755,887,885 B), `CH=$W/P1/run/syscalls-t20-1.txt` (4,165,755 lines,
199,937,035 B), `T=$W/P1/run/ps2_log-t20-1.txt` (6,739,220,731 B).
`$R`-relative paths below unless noted. Zero fork changes by T20;
no `adb`.

Headline readings: ONE channel-on boot to the 3600 s cap
reproduces the T16 exit invariant on-epoch (block-235 collapse
218 @logline 2461367, residue-13 from block 240 ×475 to block 714,
N = 72,176/72,176 with T13-exact last lines, dma/gif frozen at
T13's counters). The ~1800 s drain sample (215,996 channel events,
ts 1247.0–3047.0) is a strict two-name alternation —
`iSignalSema`/`WaitSema` 107,998/107,998, odd/even exact. The
equal-event-count menu-loop slice (trailing 215,996 EE events of
t17c, 112.6 s wall, 12 names) is missing drain-side in 10 names,
led by `SignalSema` 53,600; zero names are drain-side only. Three
20-event drain shingles (early/mid/late) are all NOT FOUND in the
menu slice. Mid-boot, the E2a lane relinked the shared
`/tmp/p1-link` binary (16:28:23Z, +272 B); the T20 runner kept its
exec-time image, and every guest receipt is exact (tabled with the
wall-rate dip/surge that overlaps the relink window).

## T20-0. Lease / tree-state / build record

| Item | Value |
|---|---|
| ssx3 HEAD at T20 start | `ed76d01` (`[orch] M60+T17+T18+P1ak …; M61+T19+T20+E2a+F3 briefs`), clean |
| ssx3 HEAD at claim/boot | `ed76d01`, clean |
| ssx3 HEAD at release/commit | `b5354a0` (`[F3] …`, landed mid-boot — offline docs, no P-lane interaction) |
| Fork HEAD at claim/boot (exec image) | `f2b1852` (T18 channel) + `M ps2xRuntime/src/runner/register_functions.cpp` (foreign, untouched) |
| Fork HEAD post-boot | `282ce92` (`Stimulus: env-armed pad-state flip … (E2a)`, committed 16:28:48Z) on `f2b1852` + same foreign M |
| Fork commits by T20 | 0; fork `git pull/push`: never run |
| Sidecars | 15 (`find $R -name "._*"`; 14 under `.git/` + 1 `ps2xRuntime/include/._ps2_log.h`; T18's 13 + 2 under `.git/`, untouched per zero-change rule) |
| Rebuild by T20 | NONE (tree at T18 boot state; binary sha AND size identical at exec — no build run) |
| Binary at exec | `a2a2f660f6ffb2ac2b987982e7dd42cb02912ab08089b033c655a1a8006d724d`, 163,464,224 B (IDENTICAL to T18) |
| Boot env | T18-ON verbatim (channel ON + PARK + 394ED0; script diff = LOG/PARK/TRACE names + `SECS=3600` + docstring only, diff-verified) |
| Monitor | `/tmp/t20-monitor.py` (T16 monitor + `LOG_ONLY`, P34-1c band flags, `RES13` row; self-test 14/14 vs T16 slice + grafts; SIGTERM dead by clear-before-trigger) |
| Boots | 1 of 1 used (cap case) |
| Wall | 2026-09-20 ~16:10–17:25Z (~1.3 h active), inside the 6 h box |
| ssx3 evidence commit | below (`[T20]`, trailer `Orchestrated-By: Muse Code`, no push) |

Lease record (`$W/P1/run/t20-waits.log`, 3 lines; zero contention —
lease absent at claim, zero WAIT lines by T20):

| Event | Value |
|---|---|
| T20 pre-claim checks (16:10:17Z) | Lease absent; `pgrep -x ps2EntryRunner` exit 1; sha `a2a2f660…` 163464224 B; ISO 3005415424 B + ELF 3890784 B present; 519 Gi free; t16/t18-waits tails = released; aligner selftest 17/17 |
| T20 claim | `printf 'T20\n' > /tmp/ssx3-p-lane-lease` 16:13:34Z |
| Monitor start | 16:13:38Z (pid 5529, header verified before boot) |
| Boot | start 16:14:15Z; INVARIANT `block=235 distinct=218 logline=2461367` (between polls t=1216/1231 s); NO trigger (log-only); `SIGTERM after 3600s, rc=0`, script exit 241 (~17:14:15Z) |
| T20 release | 17:14:25Z (3651 s held); verified absent; `pgrep -x` exit 1 |
| Trace copy (lease-free) | `ps2_log.txt` → `ps2_log-t20-1.txt` (6,739,220,731 B, COPY-OK before E2a's boot) |
| Handoff | E2a CLAIM 17:14:47Z (their log: 8 WAITs 16:36–17:10Z + claim with pre-claim checks; T20 files name-distinct, no clash) |

E2a mid-boot rebuild (foreign lane; record don't fight):

| Row | Value |
|---|---|
| Note in t20-waits.log (16:38Z, quoted) | E2a rebuilt the SHARED /tmp/p1-link binary at ~16:28Z (`a2a2f660`→`2ac14260`, +272 B pad-stimulus hook; fork `282ce92`); runner keeps old image via open inode; post-run file sha mismatches claim-time sha |
| Binary mtime (local-rendered Z) | 12:28:23 = 16:28:23Z |
| Fork commit time | `282ce92` 12:28:48−04:00 = 16:28:48Z, on top of `f2b1852` |
| Post-run file sha/size | `2ac14260…`, 163,464,496 B = 163,464,224 + 272 (note's deltas reproduce exactly) |
| E2a waits log | 8 WAIT lines (16:36:26–17:10:34Z, ~5 min polls, `lease=T20`) + CLAIM 17:14:47Z (no build line there; start time E2a-side unknown) |
| Non-perturbation receipts (T20 data) | Monitor polls t=790–958 s (relink window) strictly monotonic in loglines + trace_bytes, maxblock advancing 148→182, zero stalls; exit invariant / bands / N / residue / freeze counters all exact (below); runner clean to cap |
| Wall-rate overlap | Per-60 s slices 11–14 soften→dip→surge (60.31→59.81→49.27→71.10) over blocks 132–179 ≈ monitor t 770–900 ≈ 16:26:30–16:28:40Z, overlapping the relink; tabled as overlap (§T20-1) |

Monitor-coverage note: the monitor led the boot by 37 s and polled
the full window (238 polls, `sema30=7` throughout, `maxblock`
0→714, `inv=True` from poll 79, `d1=1` from poll 80, trace bytes
monotonic to 6,739,220,731 = trace file size at final poll).
472 POST block lines (completions 242–713), per-block w31 294–307,
d31 2.000–2.056, w29 = 0 every row, s31−w31 ∈ [−1,+1] — inside
every P34-1c band, zero OUT flags, zero LOGGED-NOTRIGGER. Exit 10
(runner dead, no trigger). No late trigger on quiescence re-scan.

## T20-1. Epoch table (T16 invariant reproduced? + drain-sample window)

Collapse series: T16 `222 ×233 → 218 @235 → 211 ×2 → 189 ×2 →
13 @b240 ×1190 (b240–1429)`; T20 `222 ×233 → 218 @235 → 211 ×2 →
189 ×2 → 13 @b240 ×475 (b240–714)` (collapse shape T16-exact;
preamble `b0/b1 = 903/586` is a NEW pair — 5th pair, 3rd distinct
value after T11/T16 961/497, T13 897/588, T15 887/603).

| Block | Stub distinct | 29w / 31w | Main (t1) | Note |
|---|---|---|---|---|
| 0–1 | 903 / 586 | 531/532, 300/299 | W29 mix | NEW preamble pair; steady @b2 |
| 2–234 | 222 ×233 | ~300 / ~300 | RUN/mid/W29 mix | phase steady |
| 235 | 218 | 302 / 303 | (pump sample) | INVARIANT (log line 2,461,367; T16: 2,463,373) |
| 236–237 | 211 ×2 | 301/301, 300/299 | pump | pump still flowing |
| 238 | 189 | 289 / 299 | pump | 29-pump drops inside block 238 (T16: 279/299 same block) |
| 239 | 189 | 0 / 307 | dormant from b240 | 29 halted |
| 240–713 | 13 ×474 | 0 / 294–307 every block | status 5, pc 0x0 | post window: drain + freeze hold |
| 714 | 13 (stub rows complete) | 0 / 176 | status 5, pc 0x0 | SIGTERM-cut block (pump partial; stub census 604×3+302×10) |

Five-signature table (brief wording vs T16's numbers):

| # | Signature | Receipt | Match? |
|---|---|---|---|
| 1 | New stub phase | 222 ×233 → 218 @b235 → 211 ×2 → 189 ×2 → 13 @b240 ×475 to b714 | MATCH (shape T16-exact) |
| 2 | 4th sema-30 signal + thread-3 release | 7 `id=30` lines, 4w/3s, ends parked (last @7228, +2 vs T16); t3 WAIT-30 (end @b714); t6 WAIT-36 ×715 | MATCH (no 8th line, no release) |
| 3 | `0x362DE8` invocation halt | 72,176 / 72,176 balanced; first enter @19,385 (exact baseline); last enter @185,264,851, last exit @185,264,990 | MATCH (N exact; last lines T13-exact) |
| 4 | New caller | NOT RUN (trace caller miner out of T20 scope; tabled, not derived) | — |
| 5 | dma/gif slope break | FROZEN @logline 2496316 at 2669132/72181 (T13's exact counters); tail ticks frozen through tick 59040 @b713 | MATCH (counters exact) |

End state at cap SIGTERM: main dormant (status 5, pc 0x0, from
block 240); t3 WAIT-30; t6 WAIT-36; 29w/s29 72178/72178 (= N+2);
30w/s30 4/3 parked; 31w/s31 215938/215938 (BALANCED, +0 in-flight —
T13/T15/T16 read +1; tabled); run-wide Δ(31−29) = 143,760.
Log tail bytes: `INFO: Window closed successfully\n[run] exiting
loop` with NO trailing newline (runner rc=0 after SIGTERM;
boot-script exit 241 = cap case, same code as T16/T18).

Drain-sample window (ON-EPOCH — exit reproduced, sample labeled
on-epoch):

| Row | Channel side (ts window) | Log side (block window) |
|---|---|---|
| Bounds | ts [1247.0, 3047.0), actual [1247.0155, 3046.9578] | blocks 248–607 (360 blocks) |
| Events / iters | 215,996 events (ev 3883430–4099426, lines 3883431–4099426) | w31sum 108,837, w29 = 0 all 360, dormsum 219,847 (d/w31 = 2.0200) |
| Wall | 1799.94 s @ ~120 ev/s | 360 × 5 s nominal |
| Margins | +60 s past exit wall (poll-quant ±7.5 s + ε ≤ 5 s absorbed); 553 s to channel end (ts 3599.74) | first window block ~b248 ≈ ts 1247 (mapping §T20-4 G2) |
| Cross note | 107,998 WaitSema/iSignalSema pairs vs 108,837 handshake waits (Δ 839 = window-edge accounting, tabled) | same Δ, other direction |

Wall-rate slices (per-60 s, 12 blocks each, proxy=(29w+31w)/2;
‡ = exit-spanning or post-exit where the proxy ≠ invocations):

| Slice | Blocks | Wall | Pump waits | Invoc proxy | Rate (/s) | Dormant | Dormant/inv |
|---|---|---|---|---|---|---|---|
| 0 | 0–11 | 0-60s | 7692 | 3846 | 64.10 | 8028 | 2.087 |
| 1 | 12–23 | 60-120s | 7218 | 3609 | 60.15 | 7641 | 2.117 |
| 2 | 24–35 | 120-180s | 7220 | 3610 | 60.17 | 7624 | 2.112 |
| 3 | 36–47 | 180-240s | 7230 | 3615 | 60.25 | 7638 | 2.113 |
| 4 | 48–59 | 240-300s | 7217 | 3608 | 60.14 | 7581 | 2.101 |
| 5 | 60–71 | 300-360s | 7224 | 3612 | 60.20 | 7638 | 2.115 |
| 6 | 72–83 | 360-420s | 7227 | 3613 | 60.23 | 7613 | 2.107 |
| 7 | 84–95 | 420-480s | 7209 | 3604 | 60.08 | 7636 | 2.119 |
| 8 | 96–107 | 480-540s | 7218 | 3609 | 60.15 | 7646 | 2.119 |
| 9 | 108–119 | 540-600s | 7223 | 3611 | 60.19 | 7650 | 2.119 |
| 10 | 120–131 | 600-660s | 7253 | 3626 | 60.44 | 7650 | 2.110 |
| 11 | 132–143 | 660-720s | 7237 | 3618 | 60.31 | 7332 | 2.027 |
| 12 | 144–155 | 720-780s | 7177 | 3588 | 59.81 | 7188 | 2.003 |
| 13 | 156–167 | 780-840s | 5913 | 2956 | 49.27 | 5913 | 2.000 |
| 14 | 168–179 | 840-900s | 8532 | 4266 | 71.10 | 8894 | 2.085 |
| 15 | 180–191 | 900-960s | 7222 | 3611 | 60.18 | 7655 | 2.120 |
| 16 | 192–203 | 960-1020s | 7235 | 3617 | 60.29 | 7659 | 2.118 |
| 17 | 204–215 | 1020-1080s | 7235 | 3617 | 60.29 | 7597 | 2.100 |
| 18 | 216–227 | 1080-1140s | 7229 | 3614 | 60.24 | 7630 | 2.111 |
| 19 | 228–239 | 1140-1200s | 6912 | 3456 | 57.60 | 7483 | 2.165 ‡ |
| 20 | 240–251 | 1200-1260s | 3619 | 1809 | 30.16 | 7305 | 4.038 ‡ |
| 21 | 252–263 | 1260-1320s | 3629 | 1814 | 30.24 | 7318 | 4.034 ‡ |
| 22 | 264–275 | 1320-1380s | 3625 | 1812 | 30.21 | 7321 | 4.040 ‡ |
| 23 | 276–287 | 1380-1440s | 3629 | 1814 | 30.24 | 7327 | 4.039 ‡ |
| 24 | 288–299 | 1440-1500s | 3621 | 1810 | 30.18 | 7325 | 4.047 ‡ |
| 25 | 300–311 | 1500-1560s | 3639 | 1819 | 30.32 | 7355 | 4.043 ‡ |
| 26 | 312–323 | 1560-1620s | 3631 | 1815 | 30.26 | 7318 | 4.032 ‡ |
| 27 | 324–335 | 1620-1680s | 3621 | 1810 | 30.18 | 7303 | 4.035 ‡ |
| 28 | 336–347 | 1680-1740s | 3623 | 1811 | 30.19 | 7322 | 4.043 ‡ |
| 29 | 348–359 | 1740-1800s | 3641 | 1820 | 30.34 | 7355 | 4.041 ‡ |
| 30 | 360–371 | 1800-1860s | 3633 | 1816 | 30.27 | 7324 | 4.033 ‡ |
| 31 | 372–383 | 1860-1920s | 3624 | 1812 | 30.20 | 7319 | 4.039 ‡ |
| 32 | 384–395 | 1920-1980s | 3635 | 1817 | 30.29 | 7322 | 4.030 ‡ |
| 33 | 396–407 | 1980-2040s | 3638 | 1819 | 30.32 | 7336 | 4.033 ‡ |
| 34 | 408–419 | 2040-2100s | 3618 | 1809 | 30.15 | 7289 | 4.029 ‡ |
| 35 | 420–431 | 2100-2160s | 3625 | 1812 | 30.21 | 7313 | 4.036 ‡ |
| 36 | 432–443 | 2160-2220s | 3627 | 1813 | 30.23 | 7312 | 4.033 ‡ |
| 37 | 444–455 | 2220-2280s | 3633 | 1816 | 30.27 | 7318 | 4.030 ‡ |
| 38 | 456–467 | 2280-2340s | 3634 | 1817 | 30.28 | 7345 | 4.042 ‡ |
| 39 | 468–479 | 2340-2400s | 3632 | 1816 | 30.27 | 7332 | 4.037 ‡ |
| 40 | 480–491 | 2400-2460s | 3629 | 1814 | 30.24 | 7322 | 4.036 ‡ |
| 41 | 492–503 | 2460-2520s | 3646 | 1823 | 30.38 | 7347 | 4.030 ‡ |
| 42 | 504–515 | 2520-2580s | 3631 | 1815 | 30.26 | 7331 | 4.039 ‡ |
| 43 | 516–527 | 2580-2640s | 3628 | 1814 | 30.23 | 7318 | 4.034 ‡ |
| 44 | 528–539 | 2640-2700s | 3627 | 1813 | 30.23 | 7323 | 4.039 ‡ |
| 45 | 540–551 | 2700-2760s | 3624 | 1812 | 30.20 | 7307 | 4.033 ‡ |
| 46 | 552–563 | 2760-2820s | 3617 | 1808 | 30.14 | 7340 | 4.060 ‡ |
| 47 | 564–575 | 2820-2880s | 3619 | 1809 | 30.16 | 7365 | 4.071 ‡ |
| 48 | 576–587 | 2880-2940s | 3621 | 1810 | 30.18 | 7349 | 4.060 ‡ |
| 49 | 588–599 | 2940-3000s | 3620 | 1810 | 30.17 | 7370 | 4.072 ‡ |
| 50 | 600–611 | 3000-3060s | 3618 | 1809 | 30.15 | 7356 | 4.066 ‡ |
| 51 | 612–623 | 3060-3120s | 3618 | 1809 | 30.15 | 7343 | 4.059 ‡ |
| 52 | 624–635 | 3120-3180s | 3613 | 1806 | 30.11 | 7338 | 4.063 ‡ |
| 53 | 636–647 | 3180-3240s | 3623 | 1811 | 30.19 | 7335 | 4.050 ‡ |
| 54 | 648–659 | 3240-3300s | 3630 | 1815 | 30.25 | 7312 | 4.029 ‡ |
| 55 | 660–671 | 3300-3360s | 3625 | 1812 | 30.21 | 7311 | 4.035 ‡ |
| 56 | 672–683 | 3360-3420s | 3632 | 1816 | 30.27 | 7325 | 4.034 ‡ |
| 57 | 684–695 | 3420-3480s | 3625 | 1812 | 30.21 | 7320 | 4.040 ‡ |
| 58 | 696–707 | 3480-3540s | 3629 | 1814 | 30.24 | 7312 | 4.031 ‡ |
| 59 | 708–714 | 3540-3575s | 1991 | 995 | 28.44 | 4017 | 4.037 ‡ |

Wall-rate shape (numbers only): flat ~60 (s1–10, d/inv
2.10–2.12) → soften (s11–12: 60.31→59.81, d/inv 2.027→2.003)
→ dip 49.27 (s13, d/inv exactly 2.000) → surge 71.10 (s14) →
flat ~60 (s15–18) → exit (s19) → ~30.2 proxy (s20–58, d/proxy
4.03–4.07) → partial s59 (SIGTERM-cut). Post-exit dormant per
31-iteration = 2.0200 over the drain window (b248–607). The
s11–s14 wobble spans blocks 132–179 ≈ monitor t 770–900 ≈
16:26:30–16:28:40Z, overlapping the E2a binary relink
(16:28:23Z); T13's dip/surge sat at blocks 202–215 with no
known foreign build. Prior shape classes: T11 smooth 64→36
decay; T13 flat→dip 48→rebound→surge 104→exit; T15/T16 flat
~60→~30.2.

## T20-2. Drain-vs-menu census (what's missing on each side?)

Slice table (equal EVENT count; wall asymmetric):

| Side | File (SSD `$W/P1/run/`) | Events | Ev / line bounds | Wall | Rate |
|---|---|---|---|---|---|
| Drain sample | `t20-drain-sample.txt` (`2ca9b108…`, 215,996 lines) | 215,996 | ev 3883430–4099426 / lines 3883431–4099426 of 4,165,755 | ts 1247.0155–3046.9578 (1799.94 s) | ~120/s |
| Menu slice | `t20-menu-slice.txt` (`05c9f539…`, 215,996 lines) | 215,996 | trailing 215,996 of t17c / lines 5270358–7648528 of 7,648,547 | log ts 228.2693–340.8897 (112.6 s) | ~1918/s |
| Channel full | `syscalls-t20-1.txt` (`2b6087d5…`, 199,937,035 B) | 4,165,755 | ts 0.0000–3599.7400; opens RFU060/RFU061/CreateSema; closes iSignalSema | 3600 s | ~1157/s avg |
| Reference full | `/Volumes/Extreme SSD/ps2x-t4/emulog-t17c.txt` | 914,791 | T17/T18 count reproduced by the slicer | 341 s run | — |

Census table (per-name EE counts; `t20-census.py` output verbatim;
`--ref-after none --rt-after none --census` cross-check in
`align-census.txt` carries IDENTICAL counts on all 12 rows):

| Name | Menu | Drain |
|---|---|---|
| WaitSema | 68998 | 107998 |
| SignalSema | 53600 | 0 |
| iSignalSema | 23162 | 107998 |
| iReferSemaStatus | 22915 | 0 |
| RFU005 | 15525 | 0 |
| PollSema | 15405 | 0 |
| iPollSema | 15276 | 0 |
| CreateSema | 247 | 0 |
| DeleteSema | 247 | 0 |
| sceSifSetDChain_isceSifSetDChain | 247 | 0 |
| sceSifSetDma_isceSifSetDma | 247 | 0 |
| ReferThreadStatus | 127 | 0 |

Drain mix shape: strict alternation — all 107,998 odd lines
`iSignalSema (43)`, all 107,998 even lines `WaitSema (44)`
(awk-verified over all 215,996 lines); first pair at ts
1247.0155/1247.0158 (~0.3 ms spacing, ~60 pairs/s).

Missing table (S1/S2/S3 candidate list + reverse):

| Direction | Name | Count | Rank |
|---|---|---|---|
| Menu-only | SignalSema | 53600 | 1 |
| Menu-only | iReferSemaStatus | 22915 | 2 |
| Menu-only | RFU005 | 15525 | 3 |
| Menu-only | PollSema | 15405 | 4 |
| Menu-only | iPollSema | 15276 | 5 |
| Menu-only | CreateSema | 247 | 6 (tie) |
| Menu-only | DeleteSema | 247 | 6 (tie) |
| Menu-only | sceSifSetDChain_isceSifSetDChain | 247 | 6 (tie) |
| Menu-only | sceSifSetDma_isceSifSetDma | 247 | 6 (tie) |
| Menu-only | ReferThreadStatus | 127 | 10 |
| Drain-only | (none — drain's 2 names both exist menu-side) | — | — |

Shingle table (`--locate 20` drain shingles in the menu slice;
full outputs in `locate-{early,mid,late}.txt`):

| Shingle | Drain offset (ev) | Drain ts | Menu-slice locate |
|---|---|---|---|
| Early | 0–19 | 1247.0155–1247.0212 | NOT FOUND |
| Mid | 107998–108017 | 2146.9731–2146.9789 | NOT FOUND |
| Late | 215976–215995 | 3046.8223–3046.8280 | NOT FOUND |

Aligner notes: `compared=215996 name_mismatches=0`; first
divergence k=0 (menu `RFU005 (5)` vs drain `iSignalSema (43)`);
shingle-run exits 1 (divergence + NOT FOUND). Format-check zeros
on the full channel file (4,165,755 events) and all five slice
files.

## T20-3. Exact commands

From `/Users/bradrichardson/dev/ssx3` unless noted; `$W`, `$R`
quoted (path contains a space):

```text
# Recon (lease-free)
read local/research/T18/REPORT.md (all) + T17 REPORT (all) + T16/T13 REPORTs
read P1 REPORT Part 34 P34-1 (guard table + bands) + tools/trace_align.py
# Pre-claim checks (16:10:17Z; lease-free)
ls /tmp/ssx3-p-lane-lease (absent); pgrep -x ps2EntryRunner (exit 1)
shasum -a 256 /tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner (a2a2f660..., 163464224 B)
stat ISO + ELF (3005415424 + 3890784 B); df (519 Gi free); t16/t18-waits tails
python3 tools/trace_align.py --selftest (17/17 ALL PASS)
git -C "$R" rev-parse HEAD (f2b1852) + status (foreign M only) + branch (ssx3)
find "$R" -name "._*" (15); git rev-parse HEAD (ed76d01, clean)
# Scripts (lease-free)
sed /tmp/t18-boot-on.py -> /tmp/t20-boot.py (names + 3600s + docstring; diff-verified)
sed /tmp/t16-monitor.py -> /tmp/t20-monitor.py (names) + LOG_ONLY edits (bands, RES13; diff-verified)
python3 -m py_compile (t20-boot + t20-monitor, OK)
python3 /tmp/t20-selftest.py (14/14: T16 slice INVARIANT/RES13/B241 + 16 POST all OK + 4 grafts)
cp /tmp/t16-{blocks,rates}.py /tmp/t20-{blocks,rates}.py (byte-identical, cmp-verified)
write /tmp/t20-slice.py + /tmp/t20-census.py (py_compile OK)
dry run: t20-slice.py on syscalls-t18-on.txt x t17c (100s window) + census + --locate 20 + --format-check (all OK)
# Boot (lease T20 held 16:13:34Z-17:14:25Z only)
mkdir -p local/research/T20
printf 'T20' > lease + >> t20-waits.log (claim 16:13:34Z)
python3 /tmp/t20-monitor.py (background from 16:13:38Z; pid + header verified)
python3 /tmp/t20-boot.py (foreground; SIGTERM after 3600s rc=0; script exit 241)
mid-run reads (lease held, read-only): monitor tails, band OUT audit (0/0), artifact sizes
>> t20-waits.log (release 17:14:25Z); rm lease; verify absent; pgrep exit 1
cp ps2_log.txt ps2_log-t20-1.txt (lease-free; 6739220731 B)
# Analysis (lease released)
shasum 3 boot artifacts + 2 slices + monitor log (6 shas above)
grep INVARIANT/RES13/B241/DORMANT/FROZEN + poll window t=790-958 (relink continuity)
python3 /tmp/t20-blocks.py LOG > t20-blocks.out (handshakes, stub/t1/t3/t6 series)
python3 /tmp/t20-rates.py LOG > t20-rates.out (exit-region blocks, 60 slices, 492 ticks, sema30)
grep -c sub_00362DE8 enter/exit (72176/72176) + first/last lines (19385, 185264851/185264990)
--format-check syscalls-t20-1.txt (4165755 ev, zeros, exit 0)
python3 /tmp/t20-slice.py CH t17c 1247 1800 /tmp/t20-slices (215996/215996, capped=False)
--format-check 5 slice files (zeros); t20-census.py slices > census.txt
trace_align.py menu drain --ref-after none --rt-after none --census (exit 1, k=0, counts identical)
3x trace_align.py menu shingle-{early,mid,late} --locate 20 (all NOT FOUND, exit 1)
awk alternation proof (107998/107998); POST extremes (w31 294-307, d31 2.000-2.056, s31-w31 +/-1)
sed residue rows b714 + b241 (same 13 targets+RAs); boot-log tail bytes (xxd, no trailing NL)
slice-table renderer (heredoc python over t20-rates.out; 60 rows)
# Archive + report (lease released; E2a holds the lease, files name-distinct)
cp 11 t20-* analysis files + t20-monitor.log + t20-blocks/rates.out to $W/P1/run/
cp census/align-census/slice-info/locate-*.txt to local/research/T20/
write local/research/T20/REPORT.md (this file)
git add -f local/research/T20/REPORT.md local/research/T20/census.txt local/research/T20/align-census.txt local/research/T20/slice-info.txt local/research/T20/locate-early.txt local/research/T20/locate-mid.txt local/research/T20/locate-late.txt
git commit -m "[T20] ..." (trailer Orchestrated-By: Muse Code; NO push)
```

## T20-4. What I could not do (gap rows)

- G1: E2a relinked the shared `/tmp/p1-link` binary mid-boot
  (16:28:23Z, `a2a2f660`→`2ac14260` +272 B, fork `282ce92`;
  tabled §T20-0 with mtime/commit/wait-log receipts). T20 made
  zero fork changes; guest non-perturbation rests on the
  receipts tabled (monotonic polls, exact invariant/bands/N),
  not on a controlled A/B.
- G2: channel-ts ↔ log-block mapping is approximate (monitor
  poll quantization ±7.5 s + channel-open ε ≤ 5 s); absorbed by
  the +60 s pure-drain margin. Window edges tabled on both
  sides (ts [1247,3047) ≈ blocks 248–607); the 839-iter
  handshake-vs-channel delta is edge accounting, tabled.
- G3: census slices are event-count-equal but wall-asymmetric
  (1800 s drain vs 112.6 s menu, ~16× rate ratio). Raw counts
  only; no rate normalization applied. Presence/absence is
  length-robust for high-count names; the four 247-count menu
  names sit nearest the rarity floor.
- G4: no caller census, no per-invocation 394/395 join, no
  post-phase trace census (394ED0 trace miners not run — out
  of T20 scope; the 6.7 GB trace is archived by path+sha).
- G5: menu slice = trailing-N (User Prefs park tail, log ts
  228–341); the pre-press language-select park is not
  separately censused.
- G6: E2a holds the P-lane lease now (claimed 17:14:47Z); CWD
  `ps2_log.txt` will be overwritten by their boot (T20 copy
  taken first). T20 SSD files are `*t20*`-named (no clash).
- G7: session wall ~1.3 h active of the 6 h box; zero lease
  waits by T20.

## Evidence files

`REPORT.md` (this file), `census.txt` (`t20-census.py`
side-by-side + both missing tables), `align-census.txt` (full
`trace_align.py --census` cross-check output), `slice-info.txt`
(window bounds), `locate-early.txt` / `locate-mid.txt` /
`locate-late.txt` (full `--locate 20` outputs). Full-size
artifacts stay on the SSD by path+sha: `boot-t20-1.log`
(755,887,885 B, `519642d9…`), `syscalls-t20-1.txt`
(199,937,035 B, `2b6087d5…`), `ps2_log-t20-1.txt`
(6,739,220,731 B, `32c77d32…`), `t20-drain-sample.txt`
(`2ca9b108…`), `t20-menu-slice.txt` (`05c9f539…`),
`t20-shingle-{early,mid,late}.txt`, `t20-census.txt`,
`t20-align-census.txt`, `t20-slice-info.txt`,
`t20-locate-{early,mid,late}.txt`, `t20-monitor.log`
(`0a548c52…`, 238 polls + 472 POST), `t20-blocks.out`,
`t20-rates.out`, `park-t20-1/` (json `ae44b058…` 111,757 B +
txt `23db336c…` 7,647 B), `$W/P1/run/t20-waits.log`.
Miners live in `/tmp` (`t20-boot/monitor/selftest/blocks/
rates/slice/census.py`, recipes in §T20-3).
