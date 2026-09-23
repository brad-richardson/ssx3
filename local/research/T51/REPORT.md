# T51 REPORT — PCSX2 render-DMA state machine at Select Character + CALL→0x434990 sites (redirect)

Brief `local/muse/prompts/T51.md` + orchestrator redirect (E40 Part-6 join:
recomp CALLs all point at `0x435bd0`; find PCSX2's `0x434990` CALLs, dump both
kicked chains for 1 vsync in E40 `ctag` format, then whole-boot watch the
`0x434990`-bound CALL ADDR words). Tables + receipts; the orchestrator decides.
Read first: `AGENTS.md`, `local/AGENTS.local.md`,
`local/research/T50/REPORT.md`, `local/research/E40/REPORT.md` Part-3/4/5.

## T51-0. Mission table

| # | Mission | Result |
| --- | --- | --- |
| 1 | Bounded log-only patch, same tree (store/sema/irq/gsreg taps) | DONE — T51 (RI 11 + HW 3 + GS 4 hunks, 18/18 anchors first try) |
| 2 | Redirect patch (ctag dump + file-driven ADDR watch) | DONE — T51c (Vif1_Dma 2) + T51w (RI 1 decl + 9 calls, all anchors first try) |
| 3 | Builds ≤2 (+2 redirect) | DONE — b1 fail-fast (GS `Console` scope) + b2 clean; redirect b3 clean first try |
| 4 | Preservation (replay 7/7 + HWSTAT, zero T51 lines) | DONE on b2 and b3 binaries |
| 5 | Capture A: SC-settled chain dump + 5-vsync state/sema/irq sequence | DONE — CWINDOW 507, ctag 3574, st 103, sema 37, irq 32 |
| 6 | Capture B: ADDR-word watch over statefile boot | DONE — ARMED naddr=4, **0 hits**; B reproduces A's 4 sites exactly |
| 7 | Receipts + `[T51]` commit, no push | DONE (this file + dir) |

Headline for the orchestrator: **PCSX2 has 4 CALL→`0x434990` sites**
(`0x63d430`, `0x63dcb0`, `0x70a0b0`, `0x70a930`, all qwc=0) next to 5–8
CALL→`0x435bd0` sites per vsync pair. The state word (`0x6214EC` = s0+0x5A8C)
cycles **0→1→2→3→4→5→0 every vsync via 6 distinct thread-mode writers
(all `intc=0`)**; the waited sema is **id 22** (`*(0x62152C)`, the +0x4C word —
not the brief's +0x28/+0x2C words, which are TADR-slot mirrors);
`SignalSema` comes from thread mode (`ra=0x382ae8`, right after kick 2, plus a
`0x377b64` producer thread), never `iSignalSema`; the only recurring EE
interrupts are **DMAC VIF1 (dmac:1, ~2/vsync, one per kick)** + VBLANK_S/E +
TIM1 — **no INTC_VIF1, no GS interrupt, no SIGNAL/FINISH/LABEL** in the window.
The 4 ADDR words are never EE-stored post-load (baked at scene build, as E40
Part-4 found on the recomp side).

## T51-1. Pins

| Pin | Value |
| --- | --- |
| PCSX2 tree | `9056c08349cc29ad02a6d1a3a4133259019195af` (`/home/brad/pcsx2-g7/pcsx2`); base = T50-end working tree, + T51 hooks below |
| Pre-T51 SHAs (working tree) | RI `68253620…0302bcdf`, HW `215c0707…5bed6bf6`, GSState `a4f1f283…902eebf2` |
| Post-T51 SHAs | RI `037c42c9…55141282a`, HW `2b7436d5…9318c553c`, GSState `22b6ccf3…f06ddf7d4` |
| Post-redirect SHAs | Vif1_Dma changed (see diff); binaries below |
| Build-2 bins (T51) | qt `96c6c2f7…85278ff58`, gsrunner `14936b31…adc5f03474` (no warnings) |
| Build-3 bins (+redirect) | qt `a011563f…bbf5c5d6f`, gsrunner `a51fbb91…301b7334` (no warnings) |
| Patch | `t51-patch.diff` 821 lines over 4 files (T50 hunks included in RI/Vif1_Dma; every T51 line marked `T51`/`t51`, 59 marker lines) |
| Inputs | ISO `SSX 3 (USA).iso`; `dat-t50` (interp, `EnableEE=false`); state `t50-sc-state` (T50 SC-settled F1) |
| Capture A | `t51a-trace.txt` 437,734 B sha256 `84b8a365…b10ec7`: ctag 3574 + dmareg 256 + st 103 + sema 37 + semaid 5 + irq 32 + gsreg 0, 0 rejects; F8 `t51-shot-t51a-sc.png`, xwd LOADED 1.4146/21 |
| Capture B | `t51b-trace.txt` 231,651 B sha256 `1ce081d3…f90720f3`: WATCH ARMED naddr=4, tagaddrwrite 0, ctag 3606; F8 `t51-shot-t51b-sc.png`, LOADED 1.4443/23 |
| Poll logs | `t51a-poll.log` / `t51b-poll.log` (FREE/CWINDOW/TARGET/END/GSHOT/LOADED/COUNTS) |

Builds: b1 (GS `Console` undeclared — decl block preceded `common/Console.h`; relocated, `fix-gs.py`) + b2 clean = original ≤2; redirect b3 clean first try = redirect 1/2.
Captures: 3 infra-killed attempts (WSL restart loop, §T51-6, no data) + A + B
= redirect 2/3. Bytesize new bytes ≈ 300 MB of 5 GB (rotated emulogs dominate).

## T51-2. The patch

Hook sites (all log-only, all gated; per-TU self-contained state, no cross-TU
deps so every binary — qt and gsrunner — links):

| Hunk | File:anchor | What |
| --- | --- | --- |
| T51-RI0 | `R5900OpcodeImpl.cpp` T50 comment | EE decls: `g_t51e_*` (atomics), `t51e_gate` (/tmp/t51-arm + free OR T48-window fallback; latches `T51_WINDOW tu=ee`, open V..V+4) |
| T51-RI-SB/SH/SW/SD/SDL/SDR/SQ | after each `memWrite*` | `t51e_store_watch(addr,size)` — post-write word read-back per overlapped lane in `0x6214E0–0x621520` |
| T51-RI-SWL/SWR | span-scoped multi-line close | same watch `(addr&~3,4)` |
| T51-RI-SC | after SYSCALL `BIOS_LOG` | `t51e_syscall_watch(call)` — 0x42–0x45 only; sema id matched against w28/w2c/**w4c** (`0x621508/0x62150C/0x62152C`); per-vsync `semaid` sample |
| T51-HW0/1/2 | `Hw.cpp` Hardware.h + STAT sets | `t51h_irq_watch(src,n)` — mask-enabled only (pends excluded); `cause` = INTC_STAT/DMAC_STAT, `handler` = interrupted EE pc |
| T51-GS0/1/2/3 | `GSState.cpp` + 3 A+D dispatch sites | `t51g_ad` — SIGNAL/FINISH/LABEL only; free-gate |
| T51c-VD0/VD1 | `Vif1_Dma.cpp` includes + T50 tap line | `t51c_tag(tadr,ptag)` at `vif1SetupTransfer` (chain path; MFIFO drain excluded); E40 `ctag` format; window V..V+1; cap 4000 |
| T51w-RI0 + 9 calls | after `g_t51e_semaid_vs` + each T51 store line | `t51w_watch(addr,size)` — addresses from `/tmp/t51-watch` (≤16, read once, `T51W_ARMED`); no vsync window; 64 hits/address |

Line formats (`vsync` = `g_t48_vsync` mirror; emulog order = execution order):
`st vsync=<n> addr=0x<> value=0x<> pc=0x<> ra=0x<> intc=<0/1>` (intc = CP0
Status.EXL — set by `cpuException`, cleared by ERET; BIOS-syscall paths also
run EXL=1, so pc range separates game vs BIOS code).
`sema vsync=<n> pc=0x<> ra=0x<> call=<name> id=<n> m=+0x<>`
(`m=` names the matched offset word; `semaid` companion line exposes all three
candidates — this is what settled +0x28/+0x2C vs +0x4C, §T51-4).
`irq vsync=<n> cause=0x<> ch=<intc|dmac>:<n> handler=0x<>`
(`handler` = interrupted pc; the game's registered handler runs later via the
BIOS dispatcher and is not visible to PCSX2 — documented, not probed).
`ctag tag_at=0x<> id=<> qwc=<> addr=0x<> tte=<16hex>` (E40-exact, **no vsync
field**; id/qwc = tag word 0, addr = word 1 raw incl. SPR bit, tte = words 2,3
memory order).
`tagaddrwrite vsync=<n> addr=0x<> value=0x<> pc=0x<> ra=0x<> a0..s7` (28 GPRs).
D1 kicks reuse T50 `dmareg` (same arm/free files).

## T51-3. Preservation

Leg 1 — G13 rich-dump replay, b2 binaries: **7/7 PNG md5s match T48 pins
exactly** (`b7a3e8db a7929218 bb8b1d85 817e934f ×2 85cf3599 ×2`), HWSTAT exact
(791/37/0/14/320/6), zero T51 lines. Leg 1 repeated on b3 binaries: identical
7/7 + HWSTAT, zero `st/sema/irq/gsreg/ctag/tagaddrwrite` lines.
Leg 2 — live SC: A LOADED mean 1.4146 p99 21, B 1.4443 p99 23 (both < 2.0 vs
T47 SC; p99 reflects the settled-SC frequencies, same class as T50's 0.52–0.60
LOADED band under interp).

## T51-4. The 5-vsync state/sema/irq sequence (capture A, EE window 507–511)

State word = **`0x6214EC`** (s0+0x5A8C — not 0x62152C, which is the sema-id
field). It runs the 6-state cycle 0→1→2→3→4→5→0 about once per vsync, drifting
in phase (window opens mid-cycle: 507 starts at 4; 27 writes over 507–511):

| value | writer pc | ra | n | notes |
| --- | --- | --- | --- | --- |
| 0 | 0x38281c | 0x3827e8 | 5 | frame close/open |
| 1 | 0x382924 | 0x382824 | 4 | after kick 1 (ra 0x382938 TADR/CHCR @0x382a08/10) |
| 2 | 0x3826ac | 0x38266c | 4 | after first dmac:1 |
| 3 | 0x382ad0 | 0x3827e8 | 4 | 8 B before TADR store @0x382ad8 (second-kick site) |
| 4 | 0x3826d4 | 0x38266c | 5 | after second dmac:1 |
| 5 | 0x382638 | 0x3825dc | 5 | — |

All 103 st lines `intc=0`. Other per-frame fields: `0x6214f0/0x6214f4`
(counters, pcs `0x382818/0x38271c/0x382920/0x377b5c`), `0x62151c` 0/1 toggle
(pcs `0x38261c/0x382640`), `0x6214e4/0x6214e8` (incl. value `0x70`), and the
`0x377bxx`-thread slots `0x621504/08/0c/10/14` (TADR/MADR fields — writer pcs
`0x377b38–0x377b5c`, ra `0x377b24`; the values stored at +0x28/+0x2C ARE the
ping-pong TADRs, alternating parity).

Sema (id **22** = `0x16` = `*(0x62152C)` constantly; the +0x28/+0x2C words are
`0x7091e0/0x7096f0` odd vsyncs, `0x63c560/0x63ca70` even — never the sema id):

| call | pc | ra | pattern |
| --- | --- | --- | --- |
| WaitSema | 0x423de8 (BIOS thunk) | 0x3827e8 | render thread waits (re-arms each pass) |
| SignalSema | 0x423dc8 | 0x382ae8 | 8 B after kick-2 CHCR @0x382ae0 |
| WaitSema / SignalSema | same pcs | 0x377b24 / 0x377b64 | producer-thread pair, 1×/vsync |

No `iSignalSema`/`PollSema` matched in 507–511. Full vsync-508 interleave (in
file order): Wait(3827e8) → st 0 → st 1 + field writes → Signal(382ae8) →
dmac:1 → st 2 → Wait → st 3 → Signal → dmac:1 → st 4 → VBLANK_E → producer
Wait(377b24) + 6 field writes → producer Signal(377b64) → Wait/Signal pair →
dmac:5, TIM1, VBLANK_S → st 5 → st 0 (next frame).

IRQ (32 lines, 507–511): `dmac:1` (VIF1) ×9 ≈ 2/vsync, one per kick;
`dmac:5` (SIF0) ×8; `intc:2` VBLANK_S ×5, `intc:3` VBLANK_E ×5, `intc:10` TIM1
×5 — one each per vsync. **Zero `intc:5` (VIF1), zero `intc:0` (GS).**
Interrupted pc is `0x81fc0` throughout (BIOS idle loop).
`gsreg` = 0 and no `T51_WINDOW tu=gs`: zero GIF A+D SIGNAL/FINISH/LABEL writes
from boot through kill (the GS tap latches only on an event; none arrived).

D1 kicks (T50 gate, capped 256): both sites every vsync —
`TADR 0x63c560/0x7091e0` pc `0x382a08` ra `0x382938` (site 1) +
`TADR 0x63ca70/0x7096f0` pc `0x382adc` ra `0x3827e8` (site 2), CHCR `0x185`
both — TADR values identical to T50's (deterministic from this statefile).

## T51-5. Redirect tables (captures A + B)

ctag: A 3574 lines (V 507–508, no cap), B 3606 (V 550–551, no cap).

| id | A n | B confirms |
| --- | --- | --- |
| 1 CNT | 1247 | inline-payload links |
| 2 NEXT | 433 | sub-chain links |
| 3 REF | 17 | `0x44b140`-class payload refs |
| 5 CALL | 937 | 446 sub-chain + uploader CALLs (below) |
| 6 RET | 937 | balanced with CALL (every CALL returns) |
| 7 END | 3 | 3 top-level chains over the 2-vsync window (spillover) |

Uploader CALLs (all qwc=0, all tte=0):

| target | A sites (tag_at) | B sites |
| --- | --- | --- |
| `0x434990` ×4 | 0x63d430, 0x63dcb0, 0x70a0b0, 0x70a930 | identical 4 |
| `0x435bd0` | 0x63c650, 0x63c8a0, 0x63cb60, 0x63cdf0, 0x709a70 | same 0x63xx 4 + 0x7092d0, 0x709520, 0x7097e0, 0x709a70 |

A fifth `0x435bd0` site family in `0x709xxx` alternates by vsync parity (A's
window V=507 odd vs B's V=550 even kicked different `0x70xx` chains) — same
alternation E40 Part-5 saw in the recomp (`0x6f`/`0x62` sets). `tag_at=
0x434990` itself appears (the walk follows CALLs into the uploader's tags).
Remaining ~900 CALLs fan out to `0x62xxxx`/`0x63xxxx`/`0x6fxxxx`/`0x70xxxx`
sub-chains (×1–2) and the `0xecxxxx–0xf1xxxx` program region (×2, both vsyncs).

tagaddrwrite (B, watch = `0x63d434 0x63dcb4 0x70a0b4 0x70a934`):
`T51W_ARMED naddr=4` then **0 hits, 0 caps** from statefile load through kill
— with complete EE-store coverage (all 9 interp opcodes incl. SQ; no EE path
bypasses them) the 4 ADDR words are never EE-written post-load. The chains
(and the 3490-vs-bd0 choice) are baked at scene build, before SC settle —
convergent with E40 Part-4 (`arenastore` = 0). B's ctag reproduces A's 4
`0x434990` sites exactly (deterministic arenas from this statefile).

## T51-6. WSL restart loop (infra; no data lost)

Five consecutive WSL instance restarts (uptime resets, /tmp tmpfs wiped,
detached children reaped) hit the first three capture attempts — idle or
loaded, including a bare `sleep 240` probe (`persist.log` shows `alive-0`, no
`done`). Host Windows is stable (boot 01:31, no recurrence). Survivor bias
explains it: builds/replays that finished did so between restarts.
Fix that unblocked the lane: **foreground single-ssh runs** — T50's recipe
held one connection per boot; my detached `setsid` launches died with the
transport. Captures A/B, the b3 build and both replays all completed in
foreground (≤3 min each). Long unattended background boots on bytesize are
currently unsafe; keep one held connection per run.

## T51-7. Gaps, overruns

1. ctag has no vsync field (E40-exact format): V vs V+1 unattributable within
   the file; END=3 shows processing spillover. Join key is tag_at/id/addr.
2. ctag qwc = tag-word QWC field, addr = word 1 raw (SPR bit kept), tte =
   words 2,3 in memory order — definitions for the E40 join (their RET qwc=998
   is a transfer-size convention, not comparable 1:1).
3. MFIFO-drain tags excluded from ctag by design (chain-path only).
4. `handler=` = interrupted pc (`0x81fc0`), not the game's registered handler
   (invisible to PCSX2 by construction).
5. irq covers mask-enabled requests only; masked-pends excluded by design.
6. Capture B is a statefile boot, not reset→SC: full interp boot to SC is
   ~19k vsyncs at ~5/s (60+ min, over the 600 s cap) and interp hooks can't
   run under the recompiler. The zero stands under either reading of "boot" (baked pre-load either way);
   the storing pc needs an earlier window.
7. `sema` carries an extra `m=` field vs the brief (names the matched offset;
   the analyzer strips it).
8. Budgets: original 2 builds (b1 fail-fast + b2) + redirect 1 (b3); captures
   3 infra-killed + A + B; bytesize ≈ 300 MB new of 5 GB.

## T51-8. Exact commands

Bytesize (foreground, one held ssh each; scripts in `pcsx2-t4/t51stage/`):
`t51r-hook.py` (validate-all-then-write) → `t51-build.sh`
(`cmake --build …/build --target pcsx2-qt pcsx2-gsrunner -j2`; SHAs in §T51-1)
→ `t51-replay.sh` (G13 dump, 7/7 + HWSTAT) → `t51-capA.sh` (statefile,
free-gate, CWINDOW→PATHS V+2, F8) → analyze (`t51c-analyze.py`) →
`t51-capB.sh` (= capA + 4-word `/tmp/t51-watch`) → extract (`t51-extract.sh`
 grammars, 0 rejects both traces).
`git log -1` checked before commit (main @ `393b376` + E40 commits above).

## T51-9. E40 join (for the orchestrator)

| Fact | E40 (recomp, E33 ticks) | T51 (PCSX2, SC settled) |
| --- | --- | --- |
| Uploader CALLs | 4× `0x435bd0` only (0x63b8/0x6f80 sites) | 4× `0x434990` + 4–5× `0x435bd0` (0x63cx/0x63dx/0x709x/0x70a0 sites) |
| Kick pcs/ras | 0x382a04/0x382ad8, ra 0x382938 | 0x382a08/0x382adc, ra 0x382938 + 0x3827e8 (T50 −4 convention already joined in T50 §T50-9) |
| Chains | baked pre-window, re-kicked | baked pre-load, re-kicked (tagaddrwrite 0) |
| Sema | — | id 22 = +0x4C word; brief's +0x28/+0x2C are TADR mirrors |
| Wakeup IRQ | — | DMAC VIF1 ×2/vsync; no INTC_VIF1/GS, no iSignalSema, all st intc=0 |

## T51-10. Receipts + recommendation

Repo (this commit): `local/research/T51/` — REPORT.md, `t51-patch.diff`
(821 lines, 4 files), appliers (`t51-hook.py`, `t51r-hook.py`, `fix-gs.py`),
build/cap/extract/analyze/replay scripts, `t51a/b-trace.txt` (+SHAs),
`t51a/b-poll.log`, both F8 PNGs. Workdir `~/dev/ssx3-work/T51/` holds the
staging copies + probes. Bytesize residue under cap: `t51stage/` (scripts,
logs, both traces, `t51-patch.diff`), rotated emulogs, `t51-frames/`.

Recommended next action (orchestrator): the missing pc is the scene-build-time
writer of the `0x63d434`-class ADDR words. Cheapest path is the E-lane (fast
recomp boot + its arenastore watch moved before SC) or a PCSX2 run from an
earlier state; no further T-lane captures queued by this brief. The state-word
writer table (§T51-4) + the 4 `0x434990` sites (§T51-5) are the join keys for
the recomp-side fix.
