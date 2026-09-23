# T59 REPORT — PCSX2: the MENU→SC writer is UCAB stores (fold fixed, caught red-handed)

Brief `local/muse/prompts/T59.md`. Tables + receipts; the orchestrator decides.
Read first: `local/research/T58/REPORT.md` (whose §5 survivor this confirms
or kills).

## T59-0. Mission table

| # | Mission | Result |
| --- | --- | --- |
| 1 | Segment-aware fold (`00/20/30/80/A0` + 32 MiB → `& 0x01FFFFFF`), `vaddr=` in ebw, `/tmp/t59-dump` end dump | DONE — 1 TU, all 6 anchors first try |
| 2 | Builds ≤2 | DONE — 1/1 (b1 clean: 1 TU + 2 links) |
| 3 | Preservation (G13 replay 7/7 + HWSTAT) | DONE, zero hook lines |
| 4 | One capture: T58 run 2 verbatim (`t58-pre-sc-state` → K → SC) + end dump | DONE — 1/2 captures |
| 5 | Tables (first writers + regs, last writers, end dump) | DONE (§T59-4) |
| 6 | Receipts + `[T59]` commit, no push | DONE (this file + dir) |

Headline for the orchestrator: **the orchestrator's read was exactly
right. All 512 ebw lines are `via=store` through `vaddr=0x3080xxxx`
(UCAB) — first writers at vsync 0 from pc `0x379804/0x37980c`
(`0x809670` block, ra `0x379780`) and pc `0x379b48/0x379b50`
(`0x809b70` block, ra `0x379ac8`), and the end dump proves w0 = `0x1b0`
in both buffers directly** (`ebwend vsync=2232 b0=0x1b0 … b1=0x1b0 …`).
T58's "TLB-mapped" survivor was the fold bug, not the TLB. No verdict
beyond that; §T59-6 lists what is now known vs still open.

## T59-1. Pins

| Pin | Value |
| --- | --- |
| PCSX2 tree | `9056c08349cc29ad02a6d1a3a4133259019195af`; base = T58-end working tree + T59 hook below |
| T59 binaries SHAs | qt `7bf7c6e5380e192989dff7572d5f1976d573643790ee52d9364be09db2418d6f`, gsrunner `908d96b73b42281d676f916745701ed89887686684608fdc86352800c778a4a8` |
| Patch | `t59-patch.diff` 27,840 B sha256 `999b75b1d6454d24c91498e98168da76b23383eaa5c8a88c996925c99bd8f66f` (`git diff` of RI vs HEAD: T56+T58 context hunks, T59 hunks are `t58_phys`/`t59_maybe_dump`/5 call-site edits) |
| Inputs | ISO; `dat-t57` (EE+VU0 interp); pre-SC state `t58-pre-sc-state` (T58, rec MENU, sha `5a324e72…`) |
| Capture (t59a) | K→SC-ident ~18 s; SC try1 0.60, SETTLED 0.45, LOADED 1.45/25; F8 `t59a-shot-sc.png` (Zoe); PATHS 0–2571; trace `t59-trace.txt` 503,577 B sha256 `33e1984174f4a7744835138728a313cb346e34c631e3eb8baa4e703d9df1549f` |
| Poll | `t59a-poll.log`: ebw 512, ebwend 1, ebwlast 244, T58_CAP 8, T58_CAPLAST 0, vu0call 0, vif0op 0, T57_CAP 0, ctag 554, spw 1536 |

Builds 1/1, captures 1/2, ~35 min wall of 2 h, bytesize ≈ 250 MB new of
2 GB (capture emulog 118 MB + rotation + snaps + stage).

## T59-2. The patch

`t59-hook.py` (validate-all-then-write, idempotent; 6/6 anchors first
try), one TU (`R5900OpcodeImpl.cpp`):

- `t58_phys()`: seg = addr>>24 ∈ {00,20,30,80,A0} and
  `(addr & 0x00FFFFFF) < 0x02000000` → `*out = addr & 0x01FFFFFF`, else
  unmatched (KSEG2/supervisor and kuseg≥32 MiB stay unmatched: genuinely
  unknown). `t58_store_watch` uses it (DMA madrs pass through the same
  helper — no-op for RAM madrs).
- `t58_emit` gains `vaddr` (DMA passes its madr); ebw lines carry
  `vaddr=0x<>` after `src=`. ebwlast unchanged.
- `t59_maybe_dump()`: one-shot `/tmp/t59-dump` check, at most one `fopen`
  per vsync (cached), called at the top of `t58_store_watch` /
  `t58_dma_watch`; on fire, `memRead32` ×8 (KSEG0 aliases) → `ebwend
  vsync b0=.. b1=..`.
- Cap script (`t59-cap.sh` = `t58-cap.sh` + `rm` gate at start, `touch`
  after settled re-ident, 5 s settle, `ebwend` count).

## T59-3. Preservation

G13 replay on the T59 gsrunner: **7/7 PNG md5s match the T48 pins
exactly** (`b7a3e8db a7929218 bb8b1d85 817e934f ×2 85cf3599 ×2`), HWSTAT
exact (791/37/0/14/320/6), hook-line count 0 (ebw/ebwlast/ebwend/caps +
vu0call/vif0op/T57_CAP all absent).

## T59-4. Tables (capture t59a)

ebw vsync span 0–31 (32 distinct); all 8 words capped at 64 (T58_CAP ×8);
ebwlast 31 vsyncs (0–30); no ebwlast cap.

Table 1 — first writer of each word (full regs in `t59-trace.txt:1–13`):

| addr | # | vsync | value | via | vaddr | pc | ra | reg notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0x809670 | 0 | 0 | 0xc | store | 0x30809670 | 0x379804 | 0x379780 | v0=30809670 (UCAB dst), v1=0xc, a3=008095f0, t3=70000000 (scratchpad!) |
| 0x809674 | 1 | 0 | 0x1414294 | store | 0x30809670 | 0x379804 | 0x379780 | same insn (SW pair) |
| 0x809678 | 4 | 0 | 0x2a0 | store | 0x30809678 | 0x37980c | 0x379780 | v0=30809670 base, +8 |
| 0x80967c | 5 | 0 | 0x0 | store | 0x30809678 | 0x37980c | 0x379780 | same insn |
| 0x809b70 | 8 | 0 | 0xcc | store | 0x30809b70 | 0x379b48 | 0x379ac8 | v0=30809b70, v1=0xb, a1=0xcc, a2=0x240 |
| 0x809b74 | 9 | 0 | 0x1414294 | store | 0x30809b70 | 0x379b48 | 0x379ac8 | same insn |
| 0x809b78 | 12 | 0 | 0x240 | store | 0x30809b78 | 0x379b50 | 0x379ac8 | a1/a2 differ per block |
| 0x809b7c | 13 | 0 | 0x0 | store | 0x30809b78 | 0x379b50 | 0x379ac8 | same insn |

All 512 ebw: via=store, vaddr-seg 0x3080 (Table 2: `store/0x3080 n=512` —
no other via, no other segment). The fill completes by vsync ~31, ~45 s
before the K press (PATHS ~1024): it is MENU-phase (at/after state-load),
not K-triggered.

Table 3 — ebwlast tail (vsync 30, last pre-cap values): `9670:0xc`,
`9674:0x1414294`, `9678:0x2a0`, `967c:0x0`, `9b70:0xcc`,
`9b74:0x1414294`, `9b78:0x240`, `9b7c:0x0` (all store). NOTE: these are
last-*visible*, not last — the 64-caps blind everything past vsync ~31.

Table 4 — end-state dump: `ebwend vsync=2232 b0=0x1b0 0x814884 0x2a0
0x623080 b1=0x1b0 0xb5c616 0x6ea0 0x62aca0` — **w0 = `0x1b0` in both
buffers, directly proven** (T58 gap 5 closed). w2 stays `0x2a0`/`0x6ea0`
from the fill (untouched since); w1/w3 evolve post-cap (0x1414294→…,
0x0→…) — that evolution is cap-blinded, like w0's `0xc`→`0x1b0`.

Table 5 — VU0/VIF0: vu0call 0, vif0op 0, T57_CAP 0 (interp, live hooks).

## T59-5. Reading (no verdict)

- The fold was the whole story: with UCAB visible, the "mystery fill" is
  ordinary EE stores (SW pairs at `0x379804/0x37980c` and
  `0x379b48/0x379b50`, UCAB dst in v0 — the `OR 0x30000000` idiom from
  the brief, one function over from `sub_00362978`'s family).
- The fill runs at MENU (done by vsync 31, pre-K); the K→SC transition
  only re-stages. T58's run-3 F1 (prompt, pre-fill) vs run-2's 47 s MENU
  idle reconciles without any divergence.
- w0's `0xc`→`0x1b0` (and w1/w3) evolution post-vsync-31 is unobserved
  (caps) — a higher-cap re-run could catch it; not spent here (1/2
  captures used).
- vu0call/vif0op stay 0 across MENU→settled under interp: T57–T59 now
  cover boot→settled with no VU0 program and no VIF0 MS op.

## T59-6. Known vs open (for the orchestrator)

Known: writer pcs/ras/vaddrs/values (§T59-4 Table 1); UCAB is the
game's DMA-bound store path here (matches the recomp's `ps2_memory.h`
mapping, so no recomp memory-map defect is indicated on this path);
end state w0 = `0x1b0` both buffers; no VU0/VIF0 involvement boot→settled.
Open: the post-31 value evolution (cap-blind); whether the MENU-phase
fill is load-triggered vs entry-triggered (runs differ in F1 promptness);
the exact caller above ra `0x379780`/`0x379ac8` (one frame up — in-trace
by pc, not named).

## T59-7. Gaps, overruns

1. Builds 1/1, captures 1/2, ~35 min, ≈ 250 MB new of 2 GB. No overruns.
2. `t59-patch.diff` scopes RI vs HEAD, so it carries T56+T58 context
   hunks; only the `t58_phys`/`t59_maybe_dump`/5 call-site hunks are T59's.
3. The 64/word caps blind the `0xc`→`0x1b0` transition by design ("stop
   at the first 64" per brief); ebwlast tail = last-visible, stated.
4. End dump reads KSEG0 aliases while the game writes UCAB — same physical word (fold §T59-2), no cache emulation either way; settled-idle
   RAM, no tearing risk beyond one u32.
5. DMA `vaddr=` repeats the madr (no separate virtual); SIF pc/ra stay
   EE interrupt-time state (no SIF writes observed, moot).

## T59-8. Exact commands

Bytesize over foreground `ssh bytesize` + `wsl -d Ubuntu` (outer
double-quotes; staged files under `t59stage/`): `t59-hook.py`
(validate-all-then-write; 6/6 anchors first try) → `t59-build.sh`
(`cmake --build …/build --target pcsx2-qt pcsx2-gsrunner -j2`; b1 clean)
→ `t59-replay.sh` (G13 7/7 + HWSTAT + zero lines) → `t59-cap.sh`
(`TAG=t59a`, `t58-pre-sc-state`, PATHS bounds, K→SC leg vs `t29-ref-sc`
×3, settled re-ident, `/tmp/t59-dump` touch + 5 s, F8 + LOADED) →
extract (`t59-extract.sh` grammar incl. `vaddr=`/`ebwend`, 0 rejects) +
analyze (`t59-analyze.py`) → scp home. `git log -1` checked before commit
(main @ `be208f8` + prior lane commits).

## T59-9. Receipts

Repo (this commit): `local/research/T59/` — REPORT.md, `t59-patch.diff`
(27,840 B), `t59-hook.py`, `t59-build.sh`, `t59-replay.sh`, `t59-cap.sh`,
`t59-extract.sh`, `t59-analyze.py`, `t59-trace.txt` (sha §T59-1),
`t59a-poll.log`, F8 `t59a-shot-sc.png`. Bytesize residue under cap:
`t59stage/`, capture emulog (118 MB) + rotation, snaps, both binaries
(§T59-1).
