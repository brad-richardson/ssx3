# T15 report — run past the exit: NO post-241 event to cap (2400 s; drain/freeze hold; N = 72,176 reproduced)

Brief `local/muse/prompts/T15.md`. Tables, no verdicts.
Stale-reading guard: `local/research/T13/REPORT.md` (all of it —
phase EXITED at block 235; N = 72,176; T13's boot SIGTERMed
30 s after trigger so nothing past block 241 was ever observed)
+ P1 REPORT Part 32 NOT landed (tail is still Part 31 §P31-8
as of `af47c77`; used §T13-1's exit table + the brief's 7
generic watches).

`W=/Volumes/Extreme SSD/ps2recomp-spike`, `R=$W/PS2Recomp` (fork,
branch `ssx3`), `LOG=$W/P1/run/boot-t15-1.log` (2,857,096 lines,
602,908,868 B), `T=$W/P1/run/ps2_log-t15-1.txt` (187,727,172 lines,
6,659,595,180 B). `$R`-relative paths below unless noted. Zero fork
changes; no `adb`.

Headline readings: the T13 exit invariant reproduced at block 235
(stub 222→218, log line 2,461,202, boot-wall ~1,183 s; transitional
shape 211 ×2 + 189 ×3 vs T13's 211 ×3 + 189 ×2 — one-block
boundary shift, tabled). The run continued 235 blocks past the
exit to block 476 (cap): NO post-241 event on any of the 7 watches
+ 2 gated extras — main stays DORMANT status 5 pc 0x0 (×237,
blocks 240–476), stubs hold residue-13 (×236), 31-drain runs the
full window (71,762 iterations, 0/31 every post block, never idle),
dma/gif frozen 160 tick pairs at T13's exact counters
(2669132/72181), CD/SIF/GS/RPC/drops silent past block 2,
sema-30 parked 4w/3s, thread-3 never releases. Empirical `N` =
72,176 reproduced to the digit (balanced enters/exits, first enter
@19,385, last enter/exit @185,264,851/185,264,990, ramp ordinals
0–74, steady 20/19, chunks bit-exact). Post-phase trace = 2,462,182
lines over the same 113 functions (0 post-only); trace ends with
empty stack (all 1,073 functions balanced — SIGTERM at cap landed
idle). Wall-rate shape is new-flat: ~60/s in-phase (no dip/surge),
~30.2/s 31-only proxy post-exit; dormant/inv 2.06–2.16 in-phase
(never T13's exact 2.0000), ~2.02 per drain iteration post-exit.

## T15-0. Lease / tree-state / build record

| Item | Value |
|---|---|
| ssx3 HEAD at T15 start | `aaf029a` (`M45+P1ai+T15 briefs written (post-exit wave)`), clean |
| ssx3 HEAD at claim/boot | `aaf029a`, clean (next commit `8b65b33 [M48]` 06:45:12 EDT, mid-boot, M-lane offline) |
| ssx3 HEAD at release | `864bf33` (`[M49] …`, 06:52:56 EDT; M48-gate + M49-brief landed mid-boot 06:46:20 EDT — offline docs/tables, no P-lane interaction) |
| ssx3 HEAD at commit | `af47c77` pre-commit (`M52 brief written (peak residuals)`; M49-gate..M52 all post-release) |
| Fork HEAD throughout | `7eed783` (same as T13 rebuild/boot) + `M ps2xRuntime/src/runner/register_functions.cpp` (foreign, untouched) |
| Fork commits by T15 | 0; fork `git pull/push`: never run |
| Sidecars | 13 (`find $R -name "._*"`; 12 under `.git/`, 1 `ps2xRuntime/include/._ps2_log.h`; T13 read 0 — tabled, untouched per zero-change rule) |
| Rebuild | NONE (tree at T13's boot state; binary sha AND size identical — no build run) |
| Binary | `81bee6c5c0740dafbb910fdfd9c62de8185b816372a0658603dc38c41252d40f`, 163,460,272 B (IDENTICAL to T11/T13 Release) |
| Boot env | T13 `boot1.py` verbatim (`PS2X_DIAG_394ED0=1` kept; `PS2X_DIAG_PARK` unset); script diff = LOG name + `SECS=2400` + docstring only (diff-verified) |
| Monitor | `/tmp/t15-monitor.py` (T13 monitor + signature rows only, diff-verified): exit invariant LOGGED never triggers; 7 post-241 watches (main-wake, stub-post, guest-event, dma-gif-unfreeze, pump-idle, trace-stall-120s; new-caller trace-only post-hoc) + sema30-8th/thread3-release gated post-241; 15 s polls |
| Boots | 1 of 1 used (cap case; no trigger in 2400 s) |
| Wall | 2026-09-20 ~10:08–11:20Z (~1.2 h active), inside the 4 h box |
| ssx3 evidence commit | below (`[T15]`, no push) |

Lease record (`$W/P1/run/t15-waits.log`, 2 lines; no contention —
lease absent at every check, zero WAIT lines):

| Event | Value |
|---|---|
| T15 pre-claim checks (10:11:47Z) | Lease absent; `pgrep -x ps2EntryRunner` exit 1; sha `81bee6c5…` 163460272 B; ISO 3005415424 B + ELF 3890784 B present; 531 Gi free; t13/t14-waits tails = released/done; Part 32 absent (P1 tail = P31) |
| T15 claim | `printf 'T15\n' > /tmp/ssx3-p-lane-lease` 10:12:07Z |
| Monitor start | 10:12:14Z (managed session, verified alive + log header before boot) |
| Boot | start 10:12:48Z; invariant LOGGED `block=235 distinct=218 logline=2461202` (~10:33:05Z, monitor-t ~1217 s); NO trigger to cap; boot script `SIGTERM after 2400s, rc=-15`, exit 241 (10:52:48Z) |
| T15 release | 10:53:54Z (2507 s held); verified absent; `pgrep -x` exit 1 |
| Trace copy (lease-free) | `ps2_log.txt` → `ps2_log-t15-1.txt` (187,727,172 lines, 6,659,595,180 B) |

Monitor-coverage note (T13's 29 s lead repeated): the monitor led
the boot by 34 s and polled the full window (159 polls, sema30=7
throughout, `maxblock` 0→476, `inv=True` from poll 78, trace bytes
monotonic to 6,659,595,180 = trace file size at final poll).
Exit 10 (runner dead, no trigger). No late trigger on quiescence
re-scan.

## T15-1. Exit-invariant table (T13 §T13-1 reproduced?)

Collapse series: T13 `222 ×233 → 218 → 211 ×3 → 189 ×2 → 13`
(blocks 235–241); T15 `222 ×233 → 218 → 211 ×2 → 189 ×3 → 13`
(block 238 reads 189, not 211 — one-block transitional boundary
shift; endpoints 218 @235 and 13 @241 identical).

| Block | Stub distinct | 29w / 31w | Main (t1) | Note |
|---|---|---|---|---|
| 2–234 | 222 ×233 | ~300 / ~300 | RUN/mid/W29 mix | phase steady (preamble b0=887, b1=603) |
| 235 | 218 | 304 / 304 | WAIT-29 | INVARIANT (log line 2,461,202; T13: 2,453,403) |
| 236–237 | 211 ×2 | 300 / 300, 305 / 305 | W29/RUN | pump still flowing |
| 238–240 | 189 ×3 | 302 / 302, 5 / 296, 0 / 305 | W29/W29/dormant-5 | 29-pump drops inside block 239 (last signal @2,494,022) |
| 241 | 13 | 0 / 301 | status 5, pc 0x0 | stub residue 13; 31 drains on |
| 242–476 | 13 ×236 | 0 / ~303 every block | status 5, pc 0x0 ×237 | post window: drain + freeze hold to cap |

Five-signature invariant table (brief wording vs T13):

| # | Signature (brief wording) | Receipt | Reading |
|---|---|---|---|
| 1 | New stub phase | 222 ×233 → 218 @b235 → 211 ×2 → 189 ×3 → 13 @b241, holds ×236 to b476 | PRESENT at block 235 (transitional counts shifted 1 block vs T13) |
| 2 | 4th sema-30 signal + thread-3 release | 7 `id=30` lines, 4w/3s, ends parked (last @7225); t3 WAIT-30 ×476 (blocks 1–476; only RUN = block 0 @0x2ab2bc) | ABSENT (no 8th line, no release — holds to cap) |
| 3 | `0x362DE8` invocation halt | 72,176 / 72,176 balanced; last enter @185,264,851, last exit @185,264,990; 2,462,182 post-phase lines, live frames at EOF = 0 | PRESENT (N = 72,176 reproduced) |
| 4 | New caller | Single caller `sub_00363490` ×72,176; any-other 0; post-only trace functions 0 (113 ⊆ 1,073) | ABSENT (holds over 2.46 M post lines) |
| 5 | dma/gif slope break | ratio 0.02703 ±0.0001 on 106 nonzero deltas; partial step (13802/374, ticks 12720→12840) then FROZEN 160 pairs (0/0, ticks 12960→32040) at 2669132/72181 | PRESENT (freeze counters T13-exact; fewer pre-freeze ticks) |

End state at cap SIGTERM: main dormant (status 5, pc 0x0, blocks
240–476); t3 WAIT-30; t6 WAIT-36; boot log ends on a complete
`id=31 … result=park` line with trailing newline (waker=4);
trace ends with empty stack (all 1,073 functions enter=exit);
29w/s29 72178/72178 balanced; 30w/s30 4/3 parked; 31w/s31
143940/143939 (+1 in-flight).

## T15-2. Next-event table (NONE — second absence window with a bound) + N + rate table

First post-241 event: NONE. All 7 watches + 2 gated extras ran
armed over blocks 242–476 (235 blocks, ~1,183 s wall, log lines
2,497,041–2,857,096, trace bytes ≈6,581,725,098–6,659,595,180):

| # | Watch | Bound observed | Fired? |
|---|---|---|---|
| 1 | Main wake from dormant | t1 status 5 pc 0x0 ×237 (blocks 240–476, no other sample) | NO |
| 2 | New stub phase after residue-13 | distinct 13 ×236 (blocks 241–476, same 13 addresses) | NO |
| 3 | First new guest event (drop/RPC/CD/SIF/GS) | 0 of each in lines ≥2,461,202 (lasts all < line 7,175) | NO |
| 4 | New caller | 0 `0x362DE8` enters post-phase (last @185,264,851); caller census single ×72,176 | NO |
| 5 | dma/gif unfreeze | 160 consecutive 0/0 pairs (ticks 12960–32040) at 2669132/72181 | NO |
| 6 | 31-drain end (pump fully idle) | 31w 295–307 every complete post block (min 295 @b415; b476 partial 71, SIGTERM-cut; never 0) | NO |
| 7 | Second halt (trace stall 120 s) | trace grows every poll to EOF (+~1 MB/15 s; final bytes = file size) | NO |
| + | sema30 8th line (gated) | n=7 all run, last @7225 | NO |
| + | thread-3 release (gated) | WAIT-30 ×476, no RUN past block 0 | NO |

| Item | Value |
|---|---|
| Empirical `N` | 72,176 (`0x362DE8` enters = exits; first enter @19,385 — exact baseline; last enter @185,264,851; last exit @185,264,990) |
| Trace totals | 394ED0 1,442,182 / 395000 1,370,006 = N×20/19 − 1,338 each (T13's −1,338 constant reproduced to the digit) |
| Ramp (real per-inv join) | non-20/19 = exactly ordinals 0–74 (n=75): ords 0–51 @2/1, ords 52–63 @3/2, ords 64–74 @2/1 |
| Steady per-inv | ordinals 75–72,175 (72,101 invs) ALL exactly 20/19 |
| 362CC8 / caller | 72,177 (N+1; exactly 1 post-phase = 2 lines) / `sub_00363490` 216,528/216,528 = 3N exact balanced |
| 1000-chunks | chunk-0 18642/17643/1000/5234034 (BIT-EXACT vs T11/T13); chunks 1–69 exact 20000/19000/1000/2534000; chunks 70–71 short-SPAN 2520494/2302064 (T13-exact); tail 3540/3363/177 (T13-exact boundary artifact) |

Growth arithmetic (P1ah pump-proxy method; proxy valid in-phase
only — 31 decouples post-exit; `blocks.tsv` carries per-block rows):

| Slice | Blocks | Wall (≈) | Pump waits | Invoc proxy | Rate (/s) | Dormant | Dormant/inv |
|---|---|---|---|---|---|---|---|
| 0 | 0–11 | 0–60 s | 7,691 | 3,845 | 64.09 | 7,992 | 2.079 |
| 1 | 12–23 | 60–120 s | 7,213 | 3,606 | 60.11 | 7,493 | 2.078 |
| 2 | 24–35 | 120–180 s | 7,217 | 3,608 | 60.14 | 7,618 | 2.111 |
| 3 | 36–47 | 180–240 s | 7,233 | 3,616 | 60.27 | 7,613 | 2.105 |
| 4 | 48–59 | 240–300 s | 7,220 | 3,610 | 60.17 | 7,660 | 2.122 |
| 5 | 60–71 | 300–360 s | 7,229 | 3,614 | 60.24 | 7,659 | 2.119 |
| 6 | 72–83 | 360–420 s | 7,211 | 3,605 | 60.09 | 7,566 | 2.099 |
| 7 | 84–95 | 420–480 s | 7,214 | 3,607 | 60.12 | 7,593 | 2.105 |
| 8 | 96–107 | 480–540 s | 7,230 | 3,615 | 60.25 | 7,643 | 2.114 |
| 9 | 108–119 | 540–600 s | 7,218 | 3,609 | 60.15 | 7,650 | 2.120 |
| 10 | 120–131 | 600–660 s | 7,228 | 3,614 | 60.23 | 7,660 | 2.120 |
| 11 | 132–143 | 660–720 s | 7,214 | 3,607 | 60.12 | 7,611 | 2.110 |
| 12 | 144–155 | 720–780 s | 7,218 | 3,609 | 60.15 | 7,452 | 2.065 |
| 13 | 156–167 | 780–840 s | 7,236 | 3,618 | 60.30 | 7,459 | 2.062 |
| 14 | 168–179 | 840–900 s | 7,218 | 3,609 | 60.15 | 7,659 | 2.122 |
| 15 | 180–191 | 900–960 s | 7,226 | 3,613 | 60.22 | 7,631 | 2.112 |
| 16 | 192–203 | 960–1020 s | 7,222 | 3,611 | 60.18 | 7,653 | 2.119 |
| 17 | 204–215 | 1020–1080 s | 7,216 | 3,608 | 60.13 | 7,594 | 2.105 |
| 18 | 216–227 | 1080–1140 s | 7,208 | 3,604 | 60.07 | 7,651 | 2.123 |
| 19 | 228–239 | 1140–1200 s | 6,935 | 3,467 ‡ | 57.79 | 7,474 | 2.156 ‡ |
| 20 | 240–251 | 1200–1260 s | 3,635 | 1,817 ‡ | 30.29 | 7,345 | 4.042 ‡ |
| 21 | 252–263 | 1260–1320 s | 3,634 | 1,817 ‡ | 30.28 | 7,326 | 4.032 ‡ |
| 22 | 264–275 | 1320–1380 s | 3,624 | 1,812 ‡ | 30.20 | 7,297 | 4.027 ‡ |
| 23 | 276–287 | 1380–1440 s | 3,625 | 1,812 ‡ | 30.21 | 7,307 | 4.033 ‡ |
| 24 | 288–299 | 1440–1500 s | 3,619 | 1,809 ‡ | 30.16 | 7,293 | 4.032 ‡ |
| 25 | 300–311 | 1500–1560 s | 3,633 | 1,816 ‡ | 30.27 | 7,328 | 4.035 ‡ |
| 26 | 312–323 | 1560–1620 s | 3,623 | 1,811 ‡ | 30.19 | 7,304 | 4.033 ‡ |
| 27 | 324–335 | 1620–1680 s | 3,638 | 1,819 ‡ | 30.32 | 7,327 | 4.028 ‡ |
| 28 | 336–347 | 1680–1740 s | 3,627 | 1,813 ‡ | 30.23 | 7,317 | 4.036 ‡ |
| 29 | 348–359 | 1740–1800 s | 3,619 | 1,809 ‡ | 30.16 | 7,292 | 4.031 ‡ |
| 30 | 360–371 | 1800–1860 s | 3,636 | 1,818 ‡ | 30.30 | 7,331 | 4.033 ‡ |
| 31 | 372–383 | 1860–1920 s | 3,628 | 1,814 ‡ | 30.23 | 7,324 | 4.038 ‡ |
| 32 | 384–395 | 1920–1980 s | 3,638 | 1,819 ‡ | 30.32 | 7,336 | 4.033 ‡ |
| 33 | 396–407 | 1980–2040 s | 3,626 | 1,813 ‡ | 30.22 | 7,307 | 4.030 ‡ |
| 34 | 408–419 | 2040–2100 s | 3,647 | 1,823 ‡ | 30.39 | 7,365 | 4.040 ‡ |
| 35 | 420–431 | 2100–2160 s | 3,648 | 1,824 ‡ | 30.40 | 7,348 | 4.029 ‡ |
| 36 | 432–443 | 2160–2220 s | 3,630 | 1,815 ‡ | 30.25 | 7,331 | 4.039 ‡ |
| 37 | 444–455 | 2220–2280 s | 3,629 | 1,814 ‡ | 30.24 | 7,314 | 4.032 ‡ |
| 38 | 456–467 | 2280–2340 s | 3,624 | 1,812 ‡ | 30.20 | 7,304 | 4.031 ‡ |
| 39 | 468–476 | 2340–2385 s | 2,488 | 1,244 ‡ | 27.64 | 5,011 | 4.028 ‡ |

‡ Slices 19–39 span/exceed the exit: proxy ≠ invocations there
(29-halt); in-phase 29/31 blocks 0–238 = 72,148/72,148 balanced;
pre-block-0 = 25/25 (exact T11/T13 match); block 239 = 5/296
(transitional — T13 read 117/298 with the same script);
blocks 240–476 = 0/71,471 (31-only). Post-exit dormant per
31-iteration ≈ 2.014–2.021 every slice (T13's slice-20 4.027 proxy
shape reproduced on full slices).

Handshake↔trace identities (exact): 29w total 72,178 = N+2;
31w total 143,940; Δ(31−29) = 71,762 = post-phase 31-drain
iterations (9 trace functions × 143,524 lines, §T15-3). The +2 edge
is unattributed (trace carries no timestamps; tabled, not derived).

Wall-rate shape vs prior windows (numbers only): T15 flat ~60
(s0–18, no dip/surge) → ~30.2 proxy (s20–38, 31-only) → exit;
T13 flat ~60 → dip ~48 → rebound → ~2× surge ~104 → exit; T11
smooth 64→36 decay; P1ag flat 33–37 + 3–5× step. Fifth distinct
shape (steadiest).

## T15-3. Post-exit state table (threads, drain, freeze — cap)

| Row | T13 (exit, b241 end) | T15 (cap, b476 end) |
|---|---|---|
| Thread-1 end | 105 RUN + 45 mid + 90 W29 + 2 dormant-5 (end: status 5 pc 0x0) | 55 RUN + 20 mid + 165 W29 + 237 dormant-5 (end: status 5 pc 0x0, blocks 240–476 — main STAYS returned) |
| Thread-1 RUN pcs | 0x36356c/0x363bec/0x3171bc/0x39f114/0x31aa8c/0x377b6c + base set | base set (0x186c04/0x2c6074/0x39b72c/0x38f364/0x3778ec/0x38f354) + 0x232d34/0x23d688/0x39ee8c (transient samples; no 0x36356c this run) |
| Thread-3 | WAIT-30 ×241 + RUN b0 (@0x2850b4) | WAIT-30 ×476 + RUN b0 (@0x2ab2bc — transient pc differs) — NO release to cap |
| Thread-6 | WAIT-36 ×242 | WAIT-36 ×477 |
| New drops / RPC / CD / SIF / GS | none past block 2 | none past block 2 (exit-region audit ≥line 2,461,202: drops 0, RPC 0, CD 0, SIF 0, GS 0; totals 6/4/810/21/96 = baselines) |
| Post-phase trace | 28,032 lines, 113 distinct funcs, 0 post-only; 9-func ×781 drain | 2,462,182 lines, 113 distinct (SAME set), 0 post-only; top: 423DE0 ×287070, 31AAF0 ×287048, 326EB0 ×287048, 31A6B8 ×143540, 423DD0 ×143528, 9-func ×143524 drain family (71,762 iters), 3E4AF0 ×21026; 394/395 ×0; 362CC8 ×2 lines (1 inv); ends EMPTY stack |
| 29/31 pump | balanced blocks 0–238; 29 halts (117/0/0), 31 drains on (298/303/297) | balanced blocks 0–238 (72,148/72,148); 29 halts (5/0/…0, last signal @2,494,022), 31 drains on (296–307 ×237 blocks); log tail = live `id=31 … result=park` (waker=4), clean trailing newline |
| dma/gif | ratio 0.02703 ±0.0001 (164 deltas) → partial (8658/234) → FROZEN (0/0, 1 pair) | ratio 0.02703 ±0.0001 (106 deltas) → partial (13802/374) → FROZEN (0/0, 160 pairs, ticks 12960–32040) at same 2669132/72181 |
| Stub end state | 222 ×233 → collapse → 13 (b241 residue @606/303) | 222 ×233 → collapse → 13 ×236 (b241–476; b476 residue SAME 13 addresses @598/299) |

Main pc-sample histogram (477 samples):

| status | pc | n | Attribution |
|---|---|---|---|
| 5 DORMANT | `0x0` | 237 | main returned (blocks 240–476) |
| 2 WAIT-29 | `0x423de8` | 165 | pump sample |
| 1 mid-syscall | `0x423dc8` | 19 | syscall entry |
| 0 RUNNING | `0x186c04` | 18 | `sub_00186A08+0x1fc` |
| 0 RUNNING | `0x2c6074` | 17 | `sub_002C5570+0xb04` |
| 0 RUNNING | `0x39b72c` | 8 | `sub_0039AE98+0x894` |
| 0 RUNNING | `0x38f364` | 6 | `sub_0038F300+0x64` |
| 0 RUNNING | `0x3778ec` | 2 | `sub_00376938+0xfb4` |
| 0 RUNNING | `0x38f354` | 1 | `sub_0038F300+0x54` |
| 0 RUNNING | `0x232d34` | 1 | `sub_00232AE0+0x254` |
| 0 RUNNING | `0x23d688` | 1 | `sub_0023D660+0x28` |
| 0 RUNNING | `0x39ee8c` | 1 | `sub_0039ECB0+0x1dc` |
| 1 mid-syscall | `0x423de8` | 1 | syscall wait addr |

CD/SIF/GS/RPC silence audit (stub markers b0/b1/b2 @lines
5,366/34,265/50,664; all lasts < line 7,226; zero new events in
lines 50,664–2,857,096 and zero in exit region ≥2,461,202):

| Source | n | Last line | Position vs markers | New past block 2 |
|---|---|---|---|---|
| CD `lbn=` | 810 | 7,175 | b0 span (5,366–34,265) | none |
| SIF loads | 21 | 1,056 | pre-b0 (< 5,366) | none |
| GS kicks | 96 | 2,639 | pre-b0 (< 5,366) | none |
| RPC unhandled | 4 | 5,144 | pre-b0 (< 5,366) | none |
| Sema-30 events | 7 | 7,225 | b0 span (5,366–34,265) | none |

## T15-4. Baselines-kept table (per-row exact-vs-baseline)

| Baseline (source) | T15 observed | Row |
|---|---|---|
| 54-frame modal cycle REP+53 (T10) | modal len 53 ×70,850/72,175 gaps; all 53 slots byte-identical (E @42, C1a#2 @52); class uniformity 70,850/70,850 per `376938` slot | exact (in-phase) |
| 31 gap patterns, ramp ordinals 0–74 (T10) | 36 patterns; boot non-modal = exactly ordinals 0–74 (same set as T11/T13) | exact + exit tail (below) |
| Exit-tail gap regime (T13) | 1,250 tail gaps from first_rep 70722: 1241× len-52 (modal−1) + 6× len-53-alt + singletons len 58/56/57 (reps 70857/71014/71526); ~203 modal-53 interspersed | exact (T13-exact) |
| Class offsets +5/+15/+16/+18/+42/+52 (T10) | C3 +5 ×72176; C7 +15 ×72176; C1a#1 +16 ×72176; C1b +18 ×72176; E @42 ×70856 + @41 ×1242; C1a#2 @52 ×70856 + @51 ×1241 | exact + tail shift |
| E-double gaps 51–62; C1a-extra 0–50 (T10) | E-double ordinals [51..62] exact; C1a×3 in 51 gaps exact; OTHER ×1 (post-phase singleton) | exact + 1 post |
| 20/19/1/2534 per invocation (P1ah) | 69 chunks exact + chunk-0 bit-exact + real-join 75–72175 all exact; chunks 70–71 same-enters short-span (T13-exact spans); tail-window 177-in-176 (join authoritative) | exact (per-inv) |
| Stubs 222 (P1ag) | 222 ×233 (blocks 2–234) | exact pre-exit |
| Stub preamble b0–b1 (T11: 961/497; T13: 897/588) | b0=887, b1=603, steady @b2 | DEVIATION in preamble counts (third distinct pair; steady same block) |
| Sema-30 4w/3s parked (P1ag) | 7 lines, 4w/3s, ends parked (@643/645/646/706/6972/7023/7225; first four = P1af's, last three +1 vs T13) | exact shape, shifted lines |
| FRR ×N, 0 deviations (T8) | FRR ×72,176, 0 deviations; `363490` 216,528/216,528 = 3N exact | exact |
| Single caller `0x363490` (P1ah) | ×72,176, other 0 | exact |
| Probe change points 104/140/162 (P1ah) | 104/140/162 @7591/7979/8270; `total→0x14` sat.; cap line @62107 (`cap=20000 reached`; T13 :62111, T11 :62113, P1ag :62604) | exact |
| Probe NULL-head 3136 (T11) | 3136 | exact |
| Probe pool drops 1066, arenas 1, buckets 5 | 1066 / 1 (`0x8095f0`) / 5, CYCLE@ 0 | exact |
| Drops 6 @:68–73 KE_ERROR 0x5b | 6 @:68–73, same site | exact |
| RPC unhandled 4 | 4 @:711/:1057/:1063/:5144 (4th @5144 = P1af's line +1) | exact count, +1 shift |
| SendCmd 1 / handshake 2 / `0x3C45C0` 0 | 1 @:1053 / 2 / 0 | exact (+1 line) |
| CD 810 `0x10`→`0x4311f` | 810, same span (:106–:7175, last +1) | exact |
| SIF 21 loads id 1–21 | 21, id 1–21 in order, last @:1056 (+1) | exact |
| Creates 37 / `-1` waits 0 | 37 / 0 (`op=wait … waker=-1`) | exact |
| Driver-entry 98 | 98 | exact |
| GS 96 / copy 64 / gif 48 / drawing=1 96 | 96 / 64 / 48 (=315 broad-`gif` − 267 ticks) / 96 | exact |
| Missing-target 1, JALR `0x2322d4→0x395730` | 1 @:660, same bytes | exact |
| Crash / FATAL / presented frame 0 | 0 / 0 / 0 | exact |
| Thread-3: RUNNING pre-pump → WAIT-30 | RUNNING ×1 (block 0, pc `0x2ab2bc`) → WAIT-30 ×476 | DEVIATION in transient pc only |
| Thread-6: WAIT-36 all blocks | WAIT-36 ×477 | exact |
| First `0x362DE8` enter @ trace line 19,385 | @19,385 | exact |
| Stack mismatches 0 / max depth 29 | 0 / 29 | exact |
| Live frames at EOF | 0 (empty stack; all 1,073 funcs balanced — SIGTERM at cap landed idle, as in T13) | same-as-T13 (prior runs cut mid-chain) |
| Pre-first-rep 294 frames, 3×C1a+1×E | 294, 3×C1a+1×E | exact |
| Post-last-rep | 369,352 frames (C3/C7/C1a/C1b ×1 each; T13: 4,049) | NEW (extended drain window) |
| Dormant/inv 2.000 (T11 slices 2+) | 2.062–2.123 all in-phase slices (never 2.0000); post d/31w 2.014–2.021 | DEVIATION (exact-2.0000 regime absent) |
| Freeze counters 2669132/72181 (T13) | identical counters; 160 frozen pairs (T13: 1 pair) | exact counters, extended freeze |

## T15-5. Absence-window ladder + post-exit rung (P1af / P1ag / T11 / T13 / T15)

| Rung | P1af (90 s) | P1ag (300 s) | T11 (600 s) | T13 (~1,218 s, EXIT) | T15 (2,400 s, CAP past exit) |
|---|---|---|---|---|---|
| Lines / bytes | 207,189 / 36,650,891 | 475,304 / 84,053,701 | 1,036,373 / 184,691,472 | 2,493,828 / 448,535,827 | 2,857,096 / 602,908,868 |
| Trace lines / bytes | 16,103,012 / 572,136,194 | 35,916,072 / 1,275,797,618 | 77,374,859 / 2,748,206,218 | 185,293,022 / 6,581,094,749 | 187,727,172 / 6,659,595,180 |
| Stub / thread / syscall blocks | 17 / 17 / 17 | 59 / 59 / 59 | 119 / 119 / 119 | 242 / 242 / 242 | 477 / 477 / 477 |
| Park/exit onset | NONE (222 ×15) | NONE (222 ×54) | NONE (222 ×117) | EXIT block 235 (218→211→189→13) | EXIT b235 reproduced; NO post event b242–476 (13 ×236) |
| Thread-1 | 6 RUN + 11 W29 (end: RUN) | 41 RUN + 12 mid + 6 W29 (end: W29) | 65 RUN + 18 mid + 36 W29 (end: mid) | 105 RUN + 45 mid + 90 W29 + 2 dormant (end: DORMANT) | 55 RUN + 20 mid + 165 W29 + 237 dormant (end: DORMANT) |
| Thread-3 | WAIT-30 ×16 + RUN b0 | WAIT-30 ×56 + RUN b0–b1 | WAIT-30 ×118 + RUN b0 | WAIT-30 ×241 + RUN b0 (no release) | WAIT-30 ×476 + RUN b0 (no release) |
| Thread-6 | WAIT-36 ×17 | WAIT-36 ×57 | WAIT-36 ×119 | WAIT-36 ×242 | WAIT-36 ×477 |
| 29-handshake w/s | 5291 / 5290 | 13109 / 13109 | 29470 / 29470 | 72178 / 72178 (= N+2) | 72178 / 72178 (= N+2, identical) |
| 30-handshake w/s | 4 / 3 (parked) | 4 / 3 (parked) | 4 / 3 (parked) | 4 / 3 (parked — exit needs no 4th) | 4 / 3 (parked to cap) |
| 31-handshake w/s | 5291 / 5290 | 13110 / 13109 | 29471 / 29470 | 72959 / 72958 (+781 post drain) | 143940 / 143939 (+71,762 post drain) |
| 4th sema-30 signal | Absent | Absent | Absent | Absent (even at exit) | Absent (to cap) |
| `0x394ED0` trace | 104,442 (= 20N−1338) | 260,822 / 260,822 | 588,042 / 588,042 | 1,442,182 / 1,442,182 (= 20N−1338) | 1,442,182 / 1,442,182 (= 20N−1338) |
| `0x362DE8`/`0x362CC8` trace | 5289 / 5290 (CC8 = N+1) | 13108 / 13108 | 29469 / 29469 | 72176 / 72177 (CC8 = N+1) | 72176 / 72177 (CC8 = N+1) |
| `0x395000` trace | 99,153 (= 19N−1338) | 247714 / 247714 | 558573 / 558573 | 1370006 / 1370006 (= 19N−1338) | 1370006 / 1370006 (= 19N−1338) |
| `run:tick` | 7 ticks | 37 ticks | 78 ticks | 166 ticks, dma 22188→2669132, gif 641→72181, freeze at end | 267 ticks, dma 23858→2669132, gif 687→72181, frozen 160 pairs |
| Dormant / start-thread | 11160 / 5 | 26209 / 5 | 59553 / 5 | 149339 / 5 | 296503 / 5 |
| Wall-rate shape | ~59/s uncontended | flat + step @~245 s | 64→36 decay | flat ~60 → dip ~48 → rebound → ~2× surge → exit | flat ~60 → ~30.2 (31-only) → cap |
| Bound / N | N > 5,289 | N > 13,108 | N > 29,469 | N = 72,176 (empirical) | N = 72,176 + post bound (no event 235 blocks past exit) |

## T15-6. Exact commands

From `/Users/bradrichardson/dev/ssx3` unless noted; `$W`, `R`
quoted (path contains a space):

```
# Tree state + Part-32 check (lease-free)
git rev-parse HEAD; git log --oneline -3; git status --porcelain=v1
git -C "$R" rev-parse HEAD; git -C "$R" log --oneline -3; git -C "$R" branch --show-current; git -C "$R" status --porcelain=v1
git -C "$R" diff --stat; find "$R" -name "._*" | wc -l (13)
tail local/research/P1/REPORT.md (tail = P31; Part 32 NOT landed -> generic watches)
# Scripts (lease-free)
sed /tmp/t13-boot1.py -> /tmp/t15-boot1.py (T13->T15 + t13->t15 + 1800->2400; diff-verified)
write /tmp/t15-monitor.py (T13 monitor + signature rows: invariant logged, 7 post-241 watches; diff-verified)
python3 -m py_compile (t15-boot1 + t15-monitor, OK)
cp /tmp/t13-{trace,mine,blocks,rates,cycle,tail}.py /tmp/t15-*.py (argv paths; no edits)
python3 -m py_compile (all 6 T15 miners, OK)
predicate self-test vs T13 data (trigger names + gating asserts; T13 blocks.tsv stub-post sim = []; guest lasts << exit line)
# Pre-claim checks (10:11:47Z; lease-free)
ls /tmp/ssx3-p-lane-lease (absent); pgrep -x ps2EntryRunner (exit 1)
shasum -a 256 /tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner (81bee6c5..., 163460272 B)
stat ISO + ELF (3005415424 + 3890784 B); df (531 Gi free); t13/t14-waits tails
# Boot (lease T15 held 10:12:07Z-10:53:54Z only)
printf 'T15' > lease + >> t15-waits.log (claim 10:12:07Z)
python3 /tmp/t15-monitor.py (managed session from 10:12:14Z; verified alive + log header)
python3 /tmp/t15-boot1.py (foreground; INVARIANT b235 logged, NO trigger; SIGTERM after 2400s rc=-15; script exit 241)
>> t15-waits.log (release 10:53:54Z); rm lease; verify absent; pgrep exit 1
cp ps2_log.txt ps2_log-t15-1.txt (lease-free; 187727172 lines, 6659595180 B)
# Analysis (lease released)
python3 /tmp/t15-blocks.py LOG (stub series, t1/t3/t6 series, handshakes)
python3 /tmp/t15-mine.py boot-t15-1.log (probe/sema/drops/census/threads/ticks)
python3 /tmp/t15-rates.py LOG (per-block pump + per-60 s slices + ticks + sema30)
wc -l T; grep -c sub_00362DE8/enter+exit (72176/72176); first enter @19385
python3 /tmp/t15-trace.py T 187727172 (caller census + chunks + tenths + balance)
python3 /tmp/t15-cycle.py T (gate + FRR + modal slots + offsets + pre/post)
python3 /tmp/t15-tail.py T (P1ah-bisect per-inv 394/395 join, full 0-72175 + ramp detail)
grep rows (probe cap/change points/SendCmd/SIF/dormant/gif/copy/missing/fatal/drops/CD/GS/RPC lasts)
tick-delta + dormant-ratio joins (heredoc python); pre-first 394/395 (= 0/0)
post-region census (lines 185264991-187727172; 113 funcs; novelty vs balance set = 0)
pc attribution via P1/output/ps2_recompiled_functions.h (bisect; 2 controls match T13)
blocks.tsv + ticks.tsv generators (heredoc python; 477 + 267 rows)
# Report (lease released)
(mkdir + write local/research/T15/REPORT.md + blocks.tsv + ticks.tsv; this file)
git add -f local/research/T15/REPORT.md local/research/T15/blocks.tsv local/research/T15/ticks.tsv
git commit -m "[T15] ..." (trailer Orchestrated-By: Muse Code; NO push)
```

## T15-7. What I could not do (gap rows)

- Read P1ai's §P32-6 next-park spec: Part 32 had not landed when
  the monitor was written or when the boot ran (P1 tail = P31 at
  `af47c77`) — the 7 generic watches from the T15 brief were used
  instead (all armed, none fired).
- Split block 239's transitional counts exactly (5/296 here vs
  117/298 in T13 with the same script): the trace carries no
  timestamps, so the halt point inside block 239's window is
  tabled by exact line (last 29-signal @2,494,022), not derived.
- Attribute the wall-rate flatness / dormant-ratio surplus host
  cause from inside the receipts (no host-load log in scope);
  tabled as guest-ratio-fixed wall variation (§T15-2), fifth
  distinct shape.
- Attribute the +2 29-side edge (72,178 waits vs 72,176
  invocations): the trace carries no timestamps (carried from T13).
- Build the §P31-6b driver-loop `(i, N)` receipt (still unbuilt;
  moot for `N`, now twice empirical) or see probe bodies past
  n=19999 (cap at :62107).
- Name the IOP announcer / decode `0x3C45C0`'s `0x1C`/`0x1D` arm
  semantics (carried from §P26-5/§P27-5/§P29-5/§P30-6/T11-7/T13-7;
  0 sightings).
- Session wall time ≈ 10:08–11:20Z (~1.2 h active), inside the
  4 h box; zero lease waits (no contention).

## Evidence files

`REPORT.md` (this file), `blocks.tsv` (477 blocks ×
distinct/logline/pump/dormant), `ticks.tsv` (267 ticks ×
dma/gif/deltas/ratio, 160 FROZEN pairs).
