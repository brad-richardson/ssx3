# T58 REPORT — PCSX2: how the rider item's EE staging buffer is built (scene build, not the settled window)

Brief `local/muse/prompts/T58.md`. Tables + receipts; the orchestrator decides.
Read first: `AGENTS.md`, `local/AGENTS.local.md`,
`local/research/T56/REPORT.md`, `local/research/T57/REPORT.md`,
`local/research/T48/REPORT.md` (the route).

## T58-0. Mission table

| # | Mission | Result |
| --- | --- | --- |
| 1 | Log-only ebw/ebwlast hooks on all EE-RAM write paths, stacked on T57 | DONE — 7 TUs, all anchors first try; 2 link-scope fixups (§T58-7.1) |
| 2 | Builds ≤2 | OVERRUN — 3 invocations (b1 link, b2 compile, b3 clean; declared §T58-7.1) |
| 3 | Preservation (G13 replay 7/7 + HWSTAT) | DONE, zero T58/T57 lines |
| 4 | Pre-SC state via T48's rec route | DONE — cold rec boot to MENU, F1 save (`t58-pre-sc-state`, all gates try1) |
| 5 | Capture ≤3 (MENU state + K to settled SC) | DONE — 2 runs + 1 cold-interp fallback run = 3/3 |
| 6 | Tables (first writers + vsync vs SC entry, per-vsync last writers, VU0/VIF0) | DONE (§T58-4) |
| 7 | Receipts + `[T58]` commit, no push | DONE (this file + dir) |

Headline for the orchestrator: **the rider staging buffers (`0x809670`,
`0x809b70` families) are ZERO from ELF load through MENU — kernel
zero-stores at boot (t≈0.8 s) plus a game `memset`-0 just before MENU
(pc `0x41628c`, ra `0x394db8`, stride-`0x80` table walk rooted at
`0x8095f0`) — and no hooked path writes them during MENU→SC→settled
either. Yet settled SC stages `0x1b0` items from those same addresses
(T56; run2 srcs match). The MENU→SC fill therefore passes through no
hooked EE-store site (500+ store-hook firings in-run prove the sites are
live), no fromSPR/SIF0/SIF2/IPU DMA, and no VU0/VIF0 program runs at any
point from cold boot to settled SC. By elimination the fill is
**TLB-mapped EE stores during MENU→SC** (fromSPR-MFIFO excluded by T48's
`p3=0`; supervisor segments implausible). Recommended next: a TLB-write
hook (physical-resolving) over the MENU→SC window to catch the fill
red-handed — and the E44 lead is concrete: the recomp most likely never
performs that TLB fill, so its staging stays mode-0.**

## T58-1. Pins

| Pin | Value |
| --- | --- |
| PCSX2 tree | `9056c08349cc29ad02a6d1a3a4133259019195af` (`/home/brad/pcsx2-g7/pcsx2`); base = T57-end working tree + T58 hooks/fixups below |
| T58 binaries SHAs | qt `f12a831d37a4c8110c3722aec84ab10068cd19c29a6b3e47909ac2e58d4aaecc`, gsrunner `ecdfe3ebc60c767e86bb0b361608f91946ea2306d22929ed955b94f5bef011796` (re-verified post-hoc) |
| Patch | `t58-patch.diff` 52,004 B sha256 `9e9859f0d6710feec49a89320b06170ad8a019ffae2019dc62712e91bd539aa3` (diff of the 7 touched files vs HEAD; stacks on the T57 tree) |
| Inputs | ISO `SSX 3 (USA).iso`; `dat-t48` (T48 verbatim, rec, for the state run); `dat-t57` (EE+VU0 interp, for capture + interp state run) |
| Pre-SC state (rec) | `/home/brad/pcsx2-g7/t58-pre-sc-state`, 6,916,176 B, sha256 `5a324e7209a8c821e985a95c5b5596015590543146f7f22028a1c291b7343169` (F1 at MENU, mtime-fresh) |
| Pre-SC state (interp) | `/home/brad/pcsx2-g7/t58-pre-sc-state-int`, 7,090,927 B, sha256 `bcef7b0925e657d1f5f3bc91465a0e1d0fe5014f7487d17f3b05e0452e139bb4` (run 3 bonus artifact, not captured from) |
| Run 1 = state run (rec) | TITLE poll1 0.43, TITLE→MENU leg try1 0.33, MENU-PRE 0.31; F1 fresh-save; emulog 687 MB (dat-t48, ebw-relevant §T58-5) |
| Run 2 = capture (t58a) | K→SC-ident ~19 s wall; SC try1 0.54, SETTLED 0.45, LOADED 1.57/45; F8 `t58a-shot-sc.png` (Zoe, full rider render); PATHS 0–2500; trace `t58-trace.txt` 279,014 B sha256 `8aa5becc737a246ea9ee5141806c3a237cac1060a6c54e02c66a2bb8c2614428` |
| Run 3 = cold interp boot (t58i) | TITLE poll1 0.43, leg try1 0.31, MENU-PRE 0.32; F1 fresh-save; trace `t58i-trace.txt` 15,089 B sha256 `2d3bf021caab055c343df5e60386e5be652f2cbaadb39002e9c7eec4c820a9be` |
| Poll logs | `t58s-poll.log`, `t58a-poll.log`, `t58i-poll.log` |

Runs 3/3, builds 3 invocations (overrun §T58-7.1), ~1.5 h wall of 3 h,
bytesize ≈ 1.3 GB new of 3 GB (dat-t57 865 MB→1.4 GB: run3 emulog 475 MB
+ capture rotation 115 MB + snaps; run1 emulog 687 MB in dat-t48; stage +
states ≈ 25 MB).

## T58-2. The patch

`t58-hook.py` (validate-all-then-write across all 7 files before any
write, idempotent) + `t58-fix.py`/`t58-fix2.py`/`t58-fix3.py` (link-scope
sequence §T58-7.1). Core (one copy, global scope in R5900OpcodeImpl.cpp):
8 watched offsets, ebw 64/word (`T58_CAP` per word), ebwlast lazy flush on
vsync change, 400 total (`T58_CAPLAST` once). T57's VU0/VIF0 hooks untouched
(own 2000-line budget).

| Hook | Anchor | What |
| --- | --- | --- |
| T58 core | `static void t56_watch(…)` in RI (×1) | state + `t58_store_watch` (alias fold `& 0x1FFFFFFF`, post-write `memRead32`) + `t58_dma_watch` (range overlap, values via caller's host ptr, byte-assembled, no new includes) |
| T58 stores ×11 | the 9 `t56_watch(…)` call lines in RI + SWC1 + SQC2 (×1 each) | one-line `t58_store_watch` after each (FPU/VU0 calls use global `::` + global-scope decls after fix3) |
| T58 fromSPR ×2 | the two `memcpy_from_spr` call lines (chain/interleave, ×1 each) | `t58_dma_watch(spr0ch.madr, pMem, bytes, "spr-from", spr0ch.sadr)` after the copy (madr pre-advance) |
| T58 SIF0 | `WriteFifoToEE` def + `sif0.fifo.read(…)` (×1 each) | `t58_dma_watch(sif0ch.madr, ptag, bytes, "sif0", 0)` between drain and madr advance |
| T58 SIF2 | same pair in sif2.cpp | `…(sif2dma.madr, ptag, bytes, "dma-ch7", 0)` (DMAC_SIF2 = 7) |
| T58 IPU-from | `ipu_fifo.out.read(pMem, readsize)` (×1) | `…(ipu0ch.madr, pMem, bytes, "dma-ch3", 0)` (DMAC_FROM_IPU = 3; IPU1/toIPU reads EE — excluded) |

Coverage argument (probed, §T58 probes 1–7): the 11 store sites are all EE
store opcodes under the interpreter (T56 precedent); the DMA sites are the
only fifo→EE drains (SIF0/SIF2 `WriteFifoToEE`, IPU `dmaIPU0`, SPR
`memcpy_from_spr` ×2). Excluded with reason: SIF1 (EE→IOP), IPU1/toIPU +
VIF0/VIF1/GIF/toSPR (EE readers), USB/FW (no game heap use), CACHE ops (not
emulated), fromSPR→MFIFO branch (writes the VIF1/GIF MFIFO ring; T48's
full-run census has `p3=0` everywhere, so it never fires on this route).

Line formats (grammars checked, 0 rejects both traces):
`ebw vsync addr value via=<store|spr-from|sif0|dma-ch7|dma-ch3> src=<EE
xfer base, 0 for stores> pc ra a0..s7` (24 regs, T56 order; DMA pc/ra are
EE interrupt-time state, racy when SIF drains on the IOP thread — stated);
`ebwlast vsync addr value via pc ra` (no src/regs by design; only vsyncs
with ≥1 write emit; trailing vsync may stay unflushed).

## T58-3. Preservation

G13 replay on the T58 gsrunner: **7/7 PNG md5s match the T48 pins
exactly**, HWSTAT exact (791/37/0/14/320/6), zero `ebw`/`ebwlast`/`T58_CAP`
and zero `vu0call`/`vif0op`/`T57_CAP` lines (all counts verified 0).

## T58-4. Tables

### Run 3 (cold interp boot → MENU): the only writers anywhere

32 ebw (all `store`, all value `0x0`), 24 ebwlast (3 vsyncs), no caps.
ebw vsync span 2–1021 (4 distinct mirror vsyncs).

Table 1 — first writer of each w0–w3 (all 8 words identical shape):

| addr | # | vsync (mirror) | boot t | value | via | pc | ra | regs (summary) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0x809670…c, 0x809b70…c (all 8) | 0–7 | 2 | 0.77 s | 0x0 | store | 0x8000e5ec | 0x8000db78 | s0 = dst kuseg alias (00809670/00809b70); kernel memset at ELF load |

Table 2 — value timeline per word: `2:0x0:store 433:0x0:store
787:0x0:store 1021:0x0:store` (n=4 each word; nothing else ever).

Table 3 — ebwlast: vsyncs 2, 433, 787 (8 words each, all `store`,
pc `0x8000e5ec`, ra `0x8000db78` then `0x8000dc84`). Vsync 1021's writes
are the unflushed trailing edge (no later vsync change; values in Table 2).

The vsync-1021 rows are game code, not kernel: pc `0x41628c`, ra
`0x394db8`, a0/a3 = dst (`00809670`, then `00809678`), a1 = 0, a2 = len
(`0x10` then `0x08`), s0 = dst+`0x80` (`008096f0`/`00809bf0`, next-item
stride!), s3 = `008095f0` constant — a stride-`0x80` table-zeroing loop
rooted at `0x8095f0` (T55's hash base) clearing 16 B + 8 B per buffer.
Full regs in `t58i-trace.txt:94–101`.

Relative to SC entry: run 3 ends at MENU (F1), so these writers precede
MENU by construction — kernel zeros ≈ boot+0.8 s, game memset ≈ seconds
before MENU save (t=42.6 s). Run 2's K→SC-ident (≈ PATHS 1024→~2400s)
follows; cross-boot estimate puts the first fills ≥1400 PATHS-vsyncs
before SC ident. (Mirror≠PATHS scales differ per boot; T50's −392 offset
was statefile-specific.)

### Runs 1+2: no writers by any hooked path

- Run 2 (MENU→SC→settled, interp, all hooks live, PATHS 0–2500): ebw 0,
  ebwlast 0, no caps. Same binary's T56 hooks in the same run: spw 1536 =
  sd 369 + sw 131 + sq 12 + sqc2 512 + spr-dma 512 (24 T56_CAPs) — the
  shared RI/VU0/SPR hook sites demonstrably fired hundreds of times.
- Run 1 (rec boot→MENU): ebw 0 with DMA hooks live (EE-store hooks silent
  under rec by design) — no fromSPR/SIF0/SIF2/IPU writes during boot.
- toSPR staging in run 2 uses the watched srcs (8 srcs × 64 capped rows:
  `0x809670/…c`, `0x809b70/…c`) — addresses confirmed, content present.

### Table 4 — VU0/VIF0 in the build windows

| Window | vu0call | vif0op (cmds) | ops seen |
| --- | --- | --- | --- |
| Run 3 boot→MENU (interp, live) | 0 | 45 lines (63) | NOP/STCYCL/ITOP/STMOD/STMASK only — boot VIF0 mode setup, zero MSCAL/F/NT, zero UNPACK/MPG/DIRECT |
| Run 2 MENU→settled (interp, live) | 0 | 0 | — |
| Run 1 boot→MENU (rec; VU0 hooks interp-only) | unobserved | unobserved | (DMA hooks live: no EE-bound DMA) |

No VU0 micro-program runs from cold boot to settled SC in any
configuration observed; `vcallmsr` at `0x37deb8` never executes in that
span (residual: a trailing-edge start past the last pump, as in T57).

## T58-5. Reading (no verdict): the fill is TLB-mapped

Chain: buffers are 0 at MENU (run3 last writes = game memset-0) and 0x1b0
at settled SC (T56 byte-exact; run2 reaches the identical screen,
LOADED 1.57/45, F8 Zoe rendered) with zero hooked writes between — while
500+ hook-site executions prove the net was live. DMA paths are
additionally ruled out in run 1 (live) and run 3 (live); MFIFO by T48's
`p3=0`; supervisor segments are implausible for game heap. Survivor:
game stores through TLB-mapped aliases (fold `& 0x1FFFFFFF` misses them)
during MENU→SC — consistent with everything, including the direct-mapped
`s0` memset the game itself uses one screen earlier.

## T58-6. E44 join keys (for the orchestrator)

| Fact | T58 (PCSX2, healthy) |
| --- | --- |
| Staging-buffer contents at MENU | all-zero (last writer: game memset-0 pc `0x41628c` ra `0x394db8`) |
| Buffer table shape | stride-`0x80` items from base `0x8095f0` (s0 walks +0x80, s3 pinned) |
| 0x1b0 fill window | MENU→SC, via TLB-mapped stores (elimination §T58-5; direct TLB proof needs a new hook) |
| VU0/`0x37deb8` over boot→settled | never run (0 vu0call in interp windows covering the whole span) |
| VIF0 over boot→MENU | mode setup only (63 cmds, no MS/data ops) |
| E44 lead | the recomp likely never performs the TLB fill — check its TLB-mapped store path first; start from `0x41628c`/`0x394db8`/`0x8095f0` |

## T58-7. Gaps, overruns

1. **Build overrun (3 invocations vs ≤2, declared).** b1: link fail —
   cross-TU refs need scope care (FPU/VU0 call sites sit in nested
   namespaces). b2: compile fail — block-scope `extern` names the
   enclosing namespace, not global (my C++ error). b3: clean (global-scope
   decls + plain calls). All incremental (2-TU + links); `t58-fix{,2,3}.py`
   documents the sequence, as T55/T56.
2. Runs 3/3 (state + capture + cold-interp fallback, the brief's own
   fallback). ~1.5 h wall; ≈ 1.3 GB new of 3 GB.
3. State scripts (`t58-state.sh`, `t58-state-int.sh`) `rm` but never
   re-`touch` the `/tmp/*-arm` gate files — harness bug: run 1/3 emulogs
   carry no T48_PATHS/T51C_WINDOW lines. The vsync mirror advances
   unconditionally (ebw vsyncs span normally), so attribution is intact;
   only the PATHS-anchored cross-checks are missing there.
4. TLB fill is elimination-grade, not observed: a physical-resolving TLB
   hook over MENU→SC is the follow-up (new brief; no budget left here).
   Supervisor-segment stores are a residual (implausible, unstated).
5. Settled-SC staging values in run 2 are cap-blinded (spr-dma 64/word
   fill during the MENU phase); the 0x1b0 end-state rests on T56 +
   LOADED/F8 identity, not re-observed values.
6. SIF pc/ra are EE interrupt-time state and racy when drains run on the
   IOP thread (no SIF writes observed, so moot).
7. Savestates restore RAM invisibly (no hook fires) — this is how content
   time-travels across the F1/load boundary in runs 1→2, not a gap in the
   windows themselves.

## T58-8. Exact commands

Bytesize over foreground `ssh bytesize` + `wsl -d Ubuntu` (outer
double-quotes; no pipes/redirection inside the ssh string; multi-step
logic in `t58stage/` files): probes (`probe1..13.sh`: DMA enumeration,
drain bodies, channel numbers = fromIPU 3/SIF0 5/SIF2 7/fromSPR 8, Pad1
bindings dat-t48 = dat-t57, anchors) → `t58-hook.py`
(validate-all-then-write; all anchors first try) → `t58-build.sh`
(`cmake --build …/build --target pcsx2-qt pcsx2-gsrunner -j2`; b1 link
fail; `t58-fix.py`; b2 compile fail; `t58-fix2.py`+`t58-fix3.py`; b3
clean; SHAs §T58-1) → `t58-replay.sh` (G13 7/7 + HWSTAT + zero lines) →
`t58-state.sh` (cold rec `dat-t48` slowboot, A1 TITLE poll, Return→MENU
leg vs `t28-ref-menu`, MENU-PRE ident, F1 save + T50 freshness/size
checks, cp + sha → `t58-pre-sc-state`) → `t58-cap.sh` (`TAG=t58a`,
`dat-t57` asserts, `-statefile t58-pre-sc-state`, PATHS bounds, K→SC leg
vs `t29-ref-sc` ×3, settled re-ident, F8 + LOADED) → `t58-state-int.sh`
(same shape under interp: sleep 120, 70×3 s A1 polls, 25 s leg settles,
F1 → `t58-pre-sc-state-int`) → extract (`t58-extract.sh` grammar, 0
rejects both traces) + analyze (`t58-analyze.py`) → verification
(`probe11.sh` spr-dma srcs + state-run ebw=0 + `nm`/`strings` liveness;
`probe12.sh` [t] stamps + `git diff --output=…` + bytes;
`probe13.sh` spw via-breakdown) → scp home. `git log -1` checked before
commit (main @ `8416522` + prior lane commits).

## T58-9. Receipts

Repo (this commit): `local/research/T58/` — REPORT.md, `t58-patch.diff`
(52,004 B), applier (`t58-hook.py`, `t58-fix.py`, `t58-fix2.py`,
`t58-fix3.py`), build/cap/extract/analyze/replay scripts, state scripts
(`t58-state.sh`, `t58-state-int.sh`), verification probes
(`probe11/12/13.sh`), traces (`t58-trace.txt` capture sha §T58-1;
`t58i-trace.txt` run 3), poll logs (`t58s/t58a/t58i-poll.log`), F8
`t58a-shot-sc.png`. (Probes 1–10 were read-only anchor reads superseded
by §T58-2; not committed.) States (`t58-pre-sc-state[-int]`) stay on
bytesize (game data, never committed) with SHAs §T58-1. Bytesize residue
under cap: `t58stage/`, `dat-t57/` growth (§T58-1), run1 emulog (dat-t48),
rotations, `t58-frames/`, both binaries (§T58-1).
