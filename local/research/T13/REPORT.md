# T13 report — run-to-exit: PHASE EXIT at block 235, empirical N = 72,176 (1 boot + live monitor)

Brief `local/muse/prompts/T13.md`. Tables, no verdicts.
Stale-reading guard: `local/research/T11/REPORT.md` (all of it —
600 s absence window, N > 29,469, all baselines kept) + P1 REPORT
Part 31 §P31-6c (first-post-phase signatures) + T11 §T11-5 (ladder
this run closes with an exit).

`W=/Volumes/Extreme SSD/ps2recomp-spike`, `R=$W/PS2Recomp` (fork,
branch `ssx3`), `LOG=$W/P1/run/boot-t13-1.log` (2,493,828 lines,
448,535,827 B), `T=$W/P1/run/ps2_log-t13-1.txt` (185,293,022 lines,
6,581,094,749 B). `$R`-relative paths below unless noted. Zero fork
changes; no `adb`.

Headline readings: the phase EXITED at block 235 (stub 222→218,
log line 2,453,403, boot-wall ~1,188 s), caught live by the
signature monitor (29 s pre-boot lead, full-window coverage —
T11's 330 s-late gap fixed). Monitor trigger + 30 s grace →
SIGTERM; lease released at once. Empirical `N` = 72,176
(`0x362DE8` enters = exits, last exit @ trace 185,264,990, 28,032
post-phase lines, empty stack at EOF). Per-invocation work never
breaks: ordinals 75–72,175 all exactly 20/19 (non-20/19 = exactly
ramp ordinals 0–74). Exit sequencing: stub collapse 222→218→211→
189→13 (blocks 235–241) → 29-pump halt (block 239 partial,
0 at 240–241) while 31-pump continues (781 post-phase drain
iterations, trace-verified) → main DORMANT status 5 pc 0x0
(blocks 240–241, returned with empty stack) → dma/gif counters
freeze (last tick pair). Sema-30 stays 4w/3s parked (no 4th
signal); thread-3 never releases; single caller throughout
(×72,176, other 0); zero post-only trace functions (113 post
distinct ⊆ 1,073 full). Pre-exit rate shape is new: flat ~60/s,
dip to ~48/s (780–900 s), rebound, ~2× surge ~104/s (blocks
205–215, dip-first 202–204), normal to exit — guest ratios fixed
throughout (dormant/inv 2.0000 slices 7–17, d_gif/d_dma 0.02703
±0.0001 on 164 deltas).

## T13-0. Lease / tree-state / build record

| Item | Value |
|---|---|
| ssx3 HEAD at T13 start | `5f881a2` (`T13+M34 briefs written …`; + `M docs/numbers-ledger.md`, `M docs/todo.md`, foreign) |
| ssx3 HEAD at boot | `ef2ce0a` (`T12+M36 gate reads pass (event-driven)`), clean |
| ssx3 HEAD at commit | `bfc98ea` pre-commit (`M44 brief written (split columns)`; this report commits on top) |
| Fork HEAD at T13 start | `935a4eb` (same as T11) + uncommitted T12 `ps2xRuntime/CMakeLists.txt` dev option + `M ps2xRuntime/src/runner/register_functions.cpp` + `?? tools/__pycache__/` |
| Fork HEAD at rebuild/boot | `7eed783` (`Config: PS2X_DEV_NO_THINLTO … (T12)`, committed by T12 lane) + `M ps2xRuntime/src/runner/register_functions.cpp` + `?? tools/__pycache__/` (foreign, untouched) |
| Fork commits by T13 | 0; fork `git pull/push`: never run |
| Sidecars | 0 (`find $R -name "._*"` — none; no purge needed) |
| Rebuild | `cmake --build /tmp/p1-link/runtime --target ps2EntryRunner -j4`, exit 0 (`/tmp/t13-build.log`, 183 steps resumed, 6 warning lines on the incremental log) |
| Binary | `81bee6c5c0740dafbb910fdfd9c62de8185b816372a0658603dc38c41252d40f`, 163,460,272 B (sha AND size IDENTICAL to T11/P1ag — T12's committed option is a Release no-op) |
| Boot env | P1ag/T11 verbatim (`PS2X_DIAG_394ED0=1` kept; `PS2X_DIAG_PARK` unset); script diff = LOG name + `SECS=1800` + docstring only (diff-verified) |
| Monitor | `/tmp/t13-monitor.py` (T11 monitor verbatim: LOG/MONLOG names + 1800 s comment only, diff-verified), 15 s polls, same 5 signatures + 120 s trace-stall trip |
| Boots | 1 of 2 used (exit case; ≤90 s confirm not run — 90 s cannot reach the ~1,188 s exit, §P30-6/T11-7 rule) |
| Wall | 2026-09-20 ~08:08–10:40Z (~2.5 h active), inside the 4 h box |
| ssx3 evidence commit | below (`[T13]`, no push) |

Lease record (`$W/P1/run/t13-waits.log`, 6 lines; T12's waits in
`$W/P1/run/t12-waits.log`):

| Event | Value |
|---|---|
| T13 start | 08:14:05Z (rebuild first attempt; killed below) |
| T12 note (their log, 08:14:59Z) | T13 pkill cross-fire SIGTERM'd T12 dev-build ninja at [317/535]; T12 wiped + reconfigured clean + rebuilt (their choice); T13 messaged T12 (`able-moonlet`, accepted) with apology + yield proposal |
| T13 yield | all T13 builds/boots held until T12 builds + suite + proof boots done |
| T12 proof boots (their log) | claim 08:26:46Z → release 08:29:47Z (2 boots, 90 s each); T13 logged WAIT 08:28:45Z |
| T13 rebuild (uncontended) | 08:32:58Z resume → exit 0; sha `81bee6c5…` |
| T13 pre-claim checks (08:41:05Z) | Lease absent; `pgrep -x ps2EntryRunner` exit 1; sha `81bee6c5…`; ISO 3005415424 B + ELF 3890784 B present; 544 Gi free; t12-waits tail = released |
| T13 claim | `printf 'T13\n' > /tmp/ssx3-p-lane-lease` 08:41:05Z |
| Monitor start | 08:41:11Z (managed session, verified alive + log header before boot) |
| Boot | start 08:41:40Z; monitor TRIGGER `stub-phase` block=235 distinct=218 logline=2453403 (~09:01:28Z, poll 79, t=1217 s); 30 s grace; SIGTERM pid=82288; boot script exit 0 ("exited before timeout") |
| T13 release | 09:01:58Z (1253 s held); verified absent; `pgrep -x` exit 1 |
| Trace copy (lease-free) | `ps2_log.txt` → `ps2_log-t13-1.txt` (185,293,022 lines, 6,581,094,749 B) |

Monitor-coverage note (T11 §T11-0 gap closed): the monitor led
the boot by 29 s and polled the full window (79 polls, sema30=7
at trigger, trace bytes monotonic to 6,498,452,906 at poll 79).
No late start; no post-hoc-only window.

## T13-1. Exit table (exit case — first event + 30 s grace)

First post-phase event: `[diag:stubs] block=235 distinct=218`
(LOG line 2,453,403). Exit sequencing (measured):

| Block | Stub distinct | 29w / 31w | Main (t1) | Note |
|---|---|---|---|---|
| 2–234 | 222 ×233 | ~300 / ~300 | RUN/mid/W29 mix | phase steady |
| 235 | 218 | 304 / 303 | WAIT-29 | FIRST EXIT EVENT (monitor trigger) |
| 236–238 | 211 ×3 | ~302 / ~302 | W29/RUN/W29 | pump still flowing |
| 239 | 189 | 117 / 298 | WAIT-29 | 29-pump drops mid-block |
| 240 | 189 | 0 / 303 | status 5, pc 0x0 | main DORMANT; 29 halted |
| 241 | 13 | 0 / 297 | status 5, pc 0x0 | stub residue 13; 31 drains on |
| tail | — | — | — | dma/gif frozen; log ends clean (`park\n`); trace stack empty |

Five-signature exit table (brief wording vs P31-6c):

| # | Signature (brief wording) | Receipt | Reading |
|---|---|---|---|
| 1 | New stub phase | 222 ×233 → 218 → 211 ×3 → 189 ×2 → 13 (blocks 235–241); b241 residue = 13 stubs @606/303 counts | PRESENT at block 235 (first event) |
| 2 | 4th sema-30 signal + thread-3 release | 7 `id=30` lines, 4w/3s, ends parked (last @7224); t3 WAIT-30 ×241 (blocks 1–241; only RUN = block 0) | ABSENT (no 8th line, no release — exit does not release t3) |
| 3 | `0x362DE8` invocation halt | 72,176 / 72,176 balanced; last enter @185,264,851, last exit @185,264,990; 28,032 post-phase lines, live frames at EOF = 0 | PRESENT (phase completed; N = 72,176) |
| 4 | New caller | Single caller `sub_00363490` ×72,176; any-other 0; post-only trace functions 0 (113 ⊆ 1,073) | ABSENT |
| 5 | dma/gif slope break | ratio 0.02703 ±0.0001 on 164 nonzero deltas; partial step (8658/234) then FROZEN pair (0/0, ticks 19800→19920, blocks 240–241 tail) | PRESENT (freeze at exit) |

End state at SIGTERM: main dormant (status 5, pc 0x0, blocks
240–241); t3 WAIT-30; t6 WAIT-36; boot log ends on a complete
`id=31 … result=park` line with trailing newline (waker=4);
trace ends with empty stack (all 1,073 functions enter=exit);
29w/s29 72178/72178 balanced; 30w/s30 4/3 parked; 31w/s31
72959/72958 (+1 in-flight).

## T13-2. Empirical N + per-60 s rate table (rate inflects — tabled)

| Item | Value |
|---|---|
| Empirical `N` | 72,176 (`0x362DE8` enters = exits; first enter @19,385 — exact baseline; last enter @185,264,851; last exit @185,264,990) |
| Trace totals | 394ED0 1,442,182 / 395000 1,370,006 = N×20/19 − 1,338 each (ramp deficit, T11's −1,338 constant reproduced to the digit) |
| Ramp (real per-inv join, P1ah bisect) | non-20/19 = exactly ordinals 0–74 (n=75): ords 0–51 @2/1, ords 52–63 @3/2, ords 64–74 @2/1; sums 162/87; 1500−162 = 1425−87 = 1338 |
| Steady per-inv | ordinals 75–72,175 (72,101 invs) ALL exactly 20/19 — no tail-off, no break at exit |
| 362CC8 / caller | 72,177 (N+1; exactly 1 post-phase) / `sub_00363490` 216,528 = 3N exact |
| 1000-chunks | chunk-0 18642/17643/1000/5234034 (BIT-EXACT vs T11); chunks 1–69 exact 20000/19000/1000/2534000; chunks 70–71 short-SPAN (same enters, 2520494/2302064 lines — len-52 tail gaps, §T13-4); tail window = 177 invs in a 176-labeled window (3540/3363/177 — miner boundary artifact, per-inv join authoritative) |

Growth arithmetic (P1ah pump-proxy method; proxy valid in-phase
only — 31 decouples post-exit):

| Slice | Blocks | Wall (≈) | Pump waits | Invoc proxy | Rate (/s) | Dormant | Dormant/inv |
|---|---|---|---|---|---|---|---|
| 0 | 0–11 | 0–60 s | 7,680 | 3,840 | 64.00 | 8,033 | 2.092 |
| 1 | 12–23 | 60–120 s | 7,223 | 3,611 | 60.19 | 7,665 | 2.123 |
| 2 | 24–35 | 120–180 s | 7,220 | 3,610 | 60.17 | 7,632 | 2.114 |
| 3 | 36–47 | 180–240 s | 7,229 | 3,614 | 60.24 | 7,662 | 2.120 |
| 4 | 48–59 | 240–300 s | 7,234 | 3,617 | 60.28 | 7,697 | 2.128 |
| 5 | 60–71 | 300–360 s | 7,226 | 3,613 | 60.22 | 7,632 | 2.112 |
| 6 | 72–83 | 360–420 s | 7,217 | 3,608 | 60.14 | 7,440 | 2.062 |
| 7 | 84–95 | 420–480 s | 7,088 | 3,544 | 59.07 | 7,088 | 2.0000 |
| 8 | 96–107 | 480–540 s | 6,590 | 3,295 | 54.92 | 6,590 | 2.0000 |
| 9 | 108–119 | 540–600 s | 6,792 | 3,396 | 56.60 | 6,792 | 2.0000 |
| 10 | 120–131 | 600–660 s | 6,902 | 3,451 | 57.52 | 6,902 | 2.0000 |
| 11 | 132–143 | 660–720 s | 6,876 | 3,438 | 57.30 | 6,876 | 2.0000 |
| 12 | 144–155 | 720–780 s | 6,788 | 3,394 | 56.57 | 6,788 | 2.0000 |
| 13 | 156–167 | 780–840 s | 6,178 | 3,089 | 51.48 | 6,178 | 2.0000 |
| 14 | 168–179 | 840–900 s | 5,798 | 2,899 | 48.32 | 5,798 | 2.0000 |
| 15 | 180–191 | 900–960 s | 7,010 | 3,505 | 58.42 | 7,010 | 2.0000 |
| 16 | 192–203 | 960–1020 s | 6,644 | 3,322 | 55.37 | 6,644 | 2.0000 |
| 17 | 204–215 | 1020–1080 s | 12,539 | 6,269 | 104.49 | 12,539 | 2.0000 † |
| 18 | 216–227 | 1080–1140 s | 7,216 | 3,608 | 60.13 | 7,618 | 2.111 |
| 19 | 228–239 | 1140–1200 s | 7,037 | 3,518 ‡ | 58.64 | 7,482 | 2.127 ‡ |
| 20 | 240–241 | 1200–1210 s | 600 | 300 ‡ | 30.00 | 1,208 | 4.027 ‡ |

† Slice 17 = real guest burst (ratio holds 2.0000; per-block:
dip 261→239→186 blocks 202–204, then surge 331→410→554→576→
631→611→612→588→574→582→615 blocks 205–215, normal 298 at
216). ‡ Slices 19–20 span the exit: proxy ≠ invocations there
(29-halt); in-phase 29/31 blocks 0–238 = 72,036/72,036 balanced;
pre-block-0 = 25/25 (exact T11 match); block 239 = 117/298
(transitional); blocks 240–241 = 0/600 (31-only).

Handshake↔trace identities (exact): 29w total 72,178 = N+2;
31w total 72,959 = N+783; Δ(31−29) = 781 = post-phase 31-drain
iterations (9 trace functions × 781, §T13-3). The +2 edge is
unattributed (trace carries no timestamps; tabled, not derived).

Wall-rate shape vs prior windows (numbers only): T13 flat ~60
(s0–6) → dip ~48 (s14) → rebound → ~2× surge ~104 (s17) →
normal → exit; T11 smooth 64→36 decay; P1ag flat 33–37 + 3–5×
step. Burst/surge/dip onsets: dip blocks 202–204, surge blocks
205–215, exit block 235.

## T13-3. First-post-phase table (threads, drain, freeze)

| Row | T11 (600 s, in-phase end) | T13 (exit) |
|---|---|---|
| Thread-1 end | 65 RUN + 18 mid + 36 W29 (end: mid-syscall) | 105 RUN + 45 mid + 90 W29 + 2 dormant-5 (end: status 5 pc 0x0, blocks 240–241 — main RETURNED, P1 Dormant precedent `makeDormant on pc==0`) |
| Thread-1 new RUN pcs | — | 0x36356c (sub_00363490+0xdc = driver-loop call site, §P31-6b exact), 0x363bec (same fn +0x75c), 0x3171bc, 0x39f114 ×2, 0x31aa8c, 0x377b6c ×2 |
| Thread-3 | WAIT-30 ×118 + RUN b0 | WAIT-30 ×241 + RUN b0 (@0x2850b4; T11: @0x416934 — transient pc differs) — NO release at exit |
| Thread-6 | WAIT-36 ×119 | WAIT-36 ×242 |
| New drops / RPC / CD / SIF / GS | none past block 2 | none past block 2 (post-exit audit >line 2453403: drops 0, RPC 0, CD 0, SIF 0, GS 0; totals 6/4/810/21/96 = baselines) |
| Post-phase trace | — (mid-chain cut, 3 live) | 28,032 lines, 113 distinct funcs, 0 post-only; top: 423DE0 ×1573, 326EB0 ×1562, 31AAF0 ×1562, 31A6B8 ×789, 423DD0 ×783, 9-func ×781 drain family (3C1638/3825F8/37E120/326B88/31A3C0/317520/317500/317348/227F58), 3E4AF0 ×115; 394/395 ×0; 362CC8 ×1; ends EMPTY stack (all balanced) |
| 29/31 pump | balanced every block | balanced blocks 0–238; 29 halts (117/0/0), 31 drains on (298/303/297); log tail = live `id=31 … result=park` (waker=4), clean trailing newline |
| dma/gif | ratio 0.0270 ±0.0002, flowing | ratio 0.02703 ±0.0001 (164 deltas) → partial step (8658/234) → FROZEN (0/0, ticks 19800→19920) |
| Stub end state | 222 ×117 (no park) | 222 ×233 → collapse → 13 (b241 residue @606/303 counts: 0x3ffa58/0x3ffbc0/0x326eb0 ×606, 5 more ×303…) |

Main pc-sample histogram (242 samples):

| status | pc | n | Attribution |
|---|---|---|---|
| 0 RUNNING | `0x186c04` | 32 | `sub_00186A08+0x1fc` |
| 0 RUNNING | `0x2c6074` | 27 | `sub_002C5570+0xb04` |
| 0 RUNNING | `0x38f364` | 12 | `sub_0038F300+0x64` |
| 0 RUNNING | `0x38f354` | 11 | `sub_0038F300+0x54` |
| 0 RUNNING | `0x39b72c` | 6 | `sub_0039AE98+0x894` |
| 0 RUNNING | `0x3778ec` | 5 | `sub_00376938+0xfb4` |
| 0 RUNNING | `0x39f114` | 2 | `sub_0039F100+0x14` |
| 0 RUNNING | `0x39e72c` | 2 | `sub_0039E6B8+0x74` |
| 0 RUNNING | `0x377b6c` | 2 | `sub_00376938+0x1234` |
| 0 RUNNING | `0x376b64` | 2 | `sub_00376938+0x22c` (T11 wrote +0x12c — arithmetic slip, same header) |
| 0 RUNNING | `0x363bec` | 1 | `sub_00363490+0x75c` (block 231) |
| 0 RUNNING | `0x36356c` | 1 | `sub_00363490+0xdc` = invocation call site (block 231) |
| 0 RUNNING | `0x31aa8c` | 1 | `sub_0031A6B8+0x3d4` |
| 0 RUNNING | `0x3171bc` | 1 | `sub_00316F00+0x2bc` |
| 1 mid-syscall | `0x423dc8` | 42 | syscall entry |
| 1 mid-syscall | `0x423de8` | 3 | syscall wait addr |
| 2 WAIT-29 | `0x423de8` | 90 | pump sample |
| 5 DORMANT | `0x0` | 2 | main returned (blocks 240–241) |

CD/SIF/GS/RPC silence audit (all lasts in blocks 0–2; zero new
events in blocks 3–241):

| Source | n | Last line | Last block | New past block 2 |
|---|---|---|---|---|
| CD `lbn=` | 810 | 7,174 | 2 | none |
| SIF loads | 21 | 1,055 | 0 | none |
| GS kicks | 96 | 2,638 | 1 | none |
| RPC unhandled | 4 | 5,143 | 2 | none |
| Sema-30 events | 7 | 7,224 | 2 | none |

## T13-4. Baselines-kept table (per-row exact-vs-baseline)

| Baseline (source) | T13 observed | Row |
|---|---|---|
| 54-frame modal cycle REP+53 (T10) | modal len 53 ×70,850/72,175 gaps; all 53 slots byte-identical (E @42, C1a#2 @52); class uniformity 70,850/70,850 per `376938` slot | exact (in-phase) |
| 31 gap patterns, ramp ordinals 0–74 (T10) | 36 patterns; boot non-modal = exactly ordinals 0–74 (same set as T11: 0/1/10–26/27/28/29/34/35/36/37/51/52/63/74 + multi-n 36/52/63/1/27/29) | exact + exit tail (below) |
| Exit-tail gap regime (new) | 1,250 tail gaps from first_rep 70722: 1241× len-52 (modal−1: E @41, C1a#2 @51) + 6× len-53-alt + singletons len 58/56/57 (reps 70857/71014/71526); ~203 modal-53 interspersed | NEW (exit signature in-trace) |
| Class offsets +5/+15/+16/+18/+42/+52 (T10) | C3 +5 ×72176; C7 +15 ×72176; C1a#1 +16 ×72176; C1b +18 ×72176; E @42 ×70856 + @41 ×1242; C1a#2 @52 ×70856 + @51 ×1241 | exact + tail shift |
| E-double gaps 51–62; C1a-extra 0–50 (T10) | E-double ordinals [51..62] exact; C1a×3 in 51 gaps exact; OTHER ×1 (post-phase singleton) | exact + 1 post |
| 20/19/1/2534 per invocation (P1ah) | 69 chunks exact + chunk-0 bit-exact + real-join 75–72175 all exact; chunks 70–71 same-enters short-span (tail gaps); tail-window 177-in-176 artifact (join authoritative) | exact (per-inv) |
| Stubs 222 (P1ag) | 222 ×233 (blocks 2–234) | exact pre-exit |
| Stub preamble b0–b1 (T11: 961/497, steady @b2) | b0=897, b1=588, steady @b2 | DEVIATION in preamble counts (faster boot; steady same block) |
| Sema-30 4w/3s parked (P1ag) | 7 lines, 4w/3s, ends parked (@643/645/646/706/6972/7022/7224; first four = P1af's, last three −3 volume shift) | exact shape, shifted lines |
| FRR ×N, 0 deviations (T8) | FRR ×72,176, 0 deviations; `363490` 216,528/216,528 = 3N exact | exact |
| Single caller `0x363490` (P1ah) | ×72,176, other 0 | exact |
| Probe change points 104/140/162 (P1ah) | 104/140/162 @7590/7979/8270; `total→0x14` sat.; cap line @62111 (`cap=20000 reached`; T11 :62113, P1ag :62604) | exact |
| Probe NULL-head 3136 (T11) | 3136 | exact |
| Probe pool drops 1066, arenas 1, buckets 5 | 1066 / 1 (`0x8095f0`) / 5, CYCLE@ 0 | exact |
| Drops 6 @:68–73 KE_ERROR 0x5b | 6 @:68–73, same site | exact |
| RPC unhandled 4 | 4 @:711/:1056/:1062/:5143 (4th @5143 = P1af's exact line) | exact count, P1af line |
| SendCmd 1 / handshake 2 / `0x3C45C0` 0 | 1 @:1052 / 2 / 0 | exact |
| CD 810 `0x10`→`0x4311f` | 810, same span (:105–:7174) | exact |
| SIF 21 loads id 1–21 | 21, id 1–21 in order, last @:1055 | exact |
| Creates 37 / `-1` waits 0 | 37 (max 37) | exact |
| Driver-entry 98 | 98 | exact |
| GS 96 / copy 64 / gif 48 / drawing=1 96 | 96 / 64 / 48 (=214 broad-`gif` − 166 ticks) / 96 | exact |
| Missing-target 1, JALR `0x2322d4→0x395730` | 1 @:660, same bytes | exact |
| Crash / FATAL / presented frame 0 | 0 / 0 / 0 | exact |
| Thread-3: RUNNING pre-pump → WAIT-30 | RUNNING ×1 (block 0, pc `0x2850b4`) → WAIT-30 ×241 | DEVIATION in transient pc only |
| Thread-6: WAIT-36 all blocks | WAIT-36 ×242 | exact |
| First `0x362DE8` enter @ trace line 19,385 | @19,385 | exact |
| Stack mismatches 0 / max depth 29 | 0 / 29 | exact |
| Live frames at EOF | 0 (empty stack; all 1,073 funcs balanced — SIGTERM landed idle post-phase) | DEVIATION (all prior runs cut mid-chain) |
| Pre-first-rep 294 frames, 3×C1a+1×E | 294, 3×C1a+1×E | exact |
| Post-last-rep | 4,049 frames (C3/C7/C1a/C1b ×1 each; T11: 3 live frames mid-chain) | NEW (post-phase unwind) |
| Dormant/inv 2.000 (T11 slices 2+) | 2.0000 slices 7–17; 2.06–2.13 slices 0–6 AND 2.11–2.13 slices 18–19 (surplus resurges pre-exit); 4.03 slice 20 | DEVIATION (surplus extent) |

## T13-5. Absence-window ladder, closed by exit (P1af / P1ag / T11 / T13)

| Rung | P1af (90 s) | P1ag (300 s) | T11 (600 s) | T13 (~1,218 s, EXIT) |
|---|---|---|---|---|
| Lines / bytes | 207,189 / 36,650,891 | 475,304 / 84,053,701 | 1,036,373 / 184,691,472 | 2,493,828 / 448,535,827 |
| Trace lines / bytes | 16,103,012 / 572,136,194 | 35,916,072 / 1,275,797,618 | 77,374,859 / 2,748,206,218 | 185,293,022 / 6,581,094,749 |
| Stub / thread / syscall blocks | 17 / 17 / 17 | 59 / 59 / 59 | 119 / 119 / 119 | 242 / 242 / 242 |
| Park/exit onset | NONE (222 ×15) | NONE (222 ×54) | NONE (222 ×117) | EXIT block 235 (218→211→189→13) |
| Thread-1 | 6 RUN + 11 W29 (end: RUN) | 41 RUN + 12 mid + 6 W29 (end: W29) | 65 RUN + 18 mid + 36 W29 (end: mid) | 105 RUN + 45 mid + 90 W29 + 2 dormant (end: DORMANT) |
| Thread-3 | WAIT-30 ×16 + RUN b0 | WAIT-30 ×56 + RUN b0–b1 | WAIT-30 ×118 + RUN b0 | WAIT-30 ×241 + RUN b0 (no release) |
| Thread-6 | WAIT-36 ×17 | WAIT-36 ×57 | WAIT-36 ×119 | WAIT-36 ×242 |
| 29-handshake w/s | 5291 / 5290 | 13109 / 13109 | 29470 / 29470 | 72178 / 72178 (= N+2) |
| 30-handshake w/s | 4 / 3 (parked) | 4 / 3 (parked) | 4 / 3 (parked) | 4 / 3 (parked — exit needs no 4th) |
| 31-handshake w/s | 5291 / 5290 | 13110 / 13109 | 29471 / 29470 | 72959 / 72958 (+781 post drain) |
| 4th sema-30 signal | Absent | Absent | Absent | Absent (even at exit) |
| `0x394ED0` trace | 104,442 (= 20N−1338) | 260,822 / 260,822 | 588,042 / 588,042 | 1,442,182 / 1,442,182 (= 20N−1338) |
| `0x362DE8`/`0x362CC8` trace | 5289 / 5290 (CC8 = N+1) | 13108 / 13108 | 29469 / 29469 | 72176 / 72177 (CC8 = N+1) |
| `0x395000` trace | 99,153 (= 19N−1338) | 247714 / 247714 | 558573 / 558573 | 1370006 / 1370006 (= 19N−1338) |
| `run:tick` | 7 ticks | 37 ticks | 78 ticks | 166 ticks, dma 22188→2669132, gif 641→72181, freeze at end |
| Dormant / start-thread | 11160 / 5 | 26209 / 5 | 59553 / 5 | 149339 / 5 |
| Wall-rate shape | ~59/s uncontended | flat + step @~245 s | 64→36 decay | flat ~60 → dip ~48 → rebound → ~2× surge → exit |
| Bound / N | N > 5,289 | N > 13,108 | N > 29,469 | N = 72,176 (empirical) |

(P1af cells re-mined from `boot-p1af-1.log` /
`ps2_log-p1af-1.txt` for this rung; CC8 = N+1 in P1af (no exit)
and T13 (exit), = N in P1ag/T11 — tabled, not derived.)

## T13-6. Exact commands

From `/Users/bradrichardson/dev/ssx3` unless noted; `$W`, `R`
quoted (path contains a space):

```
# Tree state + scripts (lease-free)
git rev-parse HEAD; git log --oneline -3; git status --porcelain=v1
git -C "$R" rev-parse HEAD; git -C "$R" log --oneline -3; git -C "$R" branch --show-current; git -C "$R" status --porcelain=v1
git -C "$R" diff --stat; find "$R" -name "._*" | wc -l (0)
sed /tmp/t11-boot1.py -> /tmp/t13-boot1.py (LOG + SECS=1800 + docstring; diff-verified)
sed /tmp/t11-monitor.py -> /tmp/t13-monitor.py (LOG/MONLOG + comment; diff-verified)
cp /tmp/t11-{trace,mine,blocks,rates,cycle}.py /tmp/t13-*.py (argv paths; no edits)
python3 -m py_compile (all 7 T13 scripts, OK)
# Rebuild attempt 1 (killed: peer-build contention + overbroad pkill — §T13-0)
cmake --build /tmp/p1-link/runtime --target ps2EntryRunner -j4 (started, killed mid-build)
pkill cross-fire also SIGTERM'd T12 dev ninja [317/535] (their log notes; resumable; messaged T12)
# Yield to T12 (poll builds + t12-waits.log + lease every ~5 min)
T12 dev rebuild clean -> suite -> cells -> claim 08:26:46Z -> 2x90s boots -> release 08:29:47Z
# Rebuild attempt 2 (uncontended, lease-free)
cmake --build /tmp/p1-link/runtime --target ps2EntryRunner -j4 > /tmp/t13-build.log 2>&1 (exit 0)
shasum -a 256 /tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner (81bee6c5..., 163460272 B)
# Boot (lease T13 held 08:41:05Z-09:01:58Z only)
pre-claim checks (lease absent; pgrep exit 1; shasum 81bee6c5; ISO + ELF sizes; df; t12-waits tail)
printf 'T13' > lease + >> t13-waits.log (claim 08:41:05Z)
python3 /tmp/t13-monitor.py (managed session from 08:41:11Z; verified alive + log header)
python3 /tmp/t13-boot1.py (foreground; monitor TRIGGER stub-phase b235 @~09:01:28Z; grace 30 s; SIGTERM pid=82288; script exit 0)
>> t13-waits.log (release 09:01:58Z); rm lease; verify absent; pgrep exit 1
cp ps2_log.txt ps2_log-t13-1.txt (lease-free; 185293022 lines, 6581094749 B)
# Analysis (lease released)
python3 /tmp/t13-blocks.py LOG (stub series, t1/t3/t6 series, handshakes)
python3 /tmp/t13-mine.py boot-t13-1.log (probe/sema/drops/census/threads/ticks)
python3 /tmp/t13-rates.py LOG (per-block pump + per-60 s slices + ticks + sema30)
wc -l T; grep -c sub_00362DE8/enter+exit (72176/72176); first enter @19385
python3 /tmp/t13-trace.py T 185293022 (caller census + chunks + tenths + balance)
python3 /tmp/t13-cycle.py T (gate + FRR + modal slots + offsets + pre/post)
write /tmp/t13-tail.py (P1ah-bisect per-inv 394/395 join, full 0-72175 + ramp detail)
grep rows (probe cap/change points/SendCmd/SIF/dormant/gif/copy/missing/fatal/drops/CD/GS/RPC lasts)
tick-delta + dormant-ratio joins (heredoc python); pre-first 394/395 (= 0/0)
post-region census (sed slice 185264991-185293022; 113 funcs; novelty vs balance set = 0)
single-pass novelty grep (11 candidates, -F -o); pc attribution via P1/output/ps2_recompiled_functions.h
P1af rung re-mine (blocks.py + greps on boot-p1af-1.log + ps2_log-p1af-1.txt)
blocks.tsv + ticks.tsv generators (heredoc python; 242 + 166 rows)
# Report (lease released)
(mkdir + write local/research/T13/REPORT.md + blocks.tsv + ticks.tsv; this file)
git add -f local/research/T13/REPORT.md local/research/T13/blocks.tsv local/research/T13/ticks.tsv
git commit -m "[T13] ..." (trailer Orchestrated-By: Muse Code; NO push)
```

## T13-7. What I could not do (gap rows)

- Run the optional ≤90 s confirm boot (1 of 2 boots used): 90 s
  cannot reach the ~1,188 s exit; a short re-boot adds no new
  window (same rule as §P30-6/T11-7).
- Build the §P31-6b driver-loop `(i, N)` receipt (still unbuilt;
  moot for `N`, now empirical) or see probe bodies past n=19999
  (cap at :62111; probe lives in `ps2_runtime.cpp`, outside this
  diag brief's zero-change rule).
- Attribute the wall-rate dip/surge host cause from inside the
  receipts (no host-load log in scope); tabled as guest-ratio-
  fixed wall variation (§T13-2), fourth distinct shape.
- Attribute the +2 29-side edge (72,178 waits vs 72,176
  invocations) or split block 239's transitional counts exactly:
  the trace carries no timestamps, so per-block invocation
  boundaries past the proxy are derived, not observed.
- Name the IOP announcer / decode `0x3C45C0`'s `0x1C`/`0x1D` arm
  semantics (carried from §P26-5/§P27-5/§P29-5/§P30-6/T11-7;
  0 sightings).
- Avoid SIGTERM'ing T12's dev-build ninja with an overbroad
  `pkill` pattern (contained: [317/535] progress kept, T12 noted
  + rebuilt clean, messaged + yielded; cost T12 one rebuild).
- Session wall time ≈ 08:08–10:40Z (~2.5 h active), inside the
  4 h box.

## Evidence files

`REPORT.md` (this file), `blocks.tsv` (242 blocks ×
distinct/logline/pump/dormant), `ticks.tsv` (166 ticks ×
dma/gif/deltas/ratio, last delta FROZEN).
