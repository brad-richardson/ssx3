# T56 REPORT — PCSX2: who writes scratchpad item 0x70000000 (w0 = 0x1b0)? Healthy side of E44

Brief `local/muse/prompts/T56.md`. Tables + receipts; the orchestrator decides.
Read first: `AGENTS.md`, `local/AGENTS.local.md`,
`local/research/T55/REPORT.md`, `local/muse/prompts/E44.md` (**same line
formats** as E44: `spw vsync addr value via pc ra a0..a3 v0 v1 t0..t9
s0..s7`, DMA adds `src=0x<EE madr>`).

## T56-0. Mission table

| # | Mission | Result |
| --- | --- | --- |
| 1 | Log-only watch on scratchpad words `0x70000000..0x7000000c` + `0x70000500..0x7000050c`: all EE-store paths + toSPR DMA, on T55's clone, EE interp | DONE — RI(decl+9: SB/SH/SW/SWL/SWR/SD/SDL/SDR/SQ) + FPU(SWC1) + VU0(SQC2) + SPR(decl+2: normal/chain + interleave), all anchors first try |
| 2 | Builds ≤2 | DONE — b1 compile error (2 generator bugs) + fixup + b2 clean |
| 3 | Preservation (G13 replay 7/7 + HWSTAT, zero T56 lines) | DONE |
| 4 | Capture 1: settled-SC writer census | DONE — 1536 spw, 24 caps, 0 rejects |
| 5 | Capture 2 (brief's conditional): watch the DMA EE source words | DONE — 8 EE addrs, armed ×3, **0 hits**; capture 1 reproduced exactly |
| 6 | Capture 3 (alias sweep for capture 2's hole) | DONE — 24 addrs (kuseg/KSEG0/KSEG1), armed ×3, **0 hits** |
| 7 | Receipts + `[T56]` commit, no push | DONE (this file + dir) |

Headline for the orchestrator: **the `w0=0x1b0` scratchpad items are
staged by toSPR DMA (channel 9), pc `0x371d90` ra `0x38f53c`, every vsync:
item `0x70000000` from EE `0x809670` (`0x1b0/0x814884/0x2a0`,
w3 `0x6efd00` even / `0x623080` odd) and item `0x70000500` from EE
`0x809b70` (`0x1b0/0xb5c616/0x6ea0`, w3 `0x6f7920` even / `0x62aca0`
odd) — byte-exact T55 Table items.** Each vsync stages each item 3× in
fixed order (0x1b0-item first, then two 0xcc-items). The EE staging words
are never EE-stored in-window (captures 2+3, all aliases, armed): w0/w1/w2
are baked pre-load; the w3 pointer ping-pongs every vsync through a path
that is not an EE store (fromSPR/SIF DMA unhooked — open, §T56-8.6).

## T56-1. Pins

| Pin | Value |
| --- | --- |
| PCSX2 tree | `9056c08349cc29ad02a6d1a3a4133259019195af` (`/home/brad/pcsx2-g7/pcsx2`); base = T55-end working tree + T56 hooks below (Interpreter.cpp untouched by T56) |
| T56 binaries SHAs | qt `57bdb158855d0f17d78956f54c82012ff1490201fba54d39750ab780ca715e72`, gsrunner `2512b5dd68d8734ce9baade822ddedc79edc674778a0c80dea99f91d3071ffef` |
| Patch | `t56-patch.diff` 43,830 B sha256 `1a21453636eee9ae7dcb82e90a3b98fc5040b7d5bc6cc6f8dd3585833198a8e7` (diff of the 4 touched files vs HEAD; stacks on the T55 tree, 136 `T56`/`t56` marker lines) |
| Inputs | ISO `SSX 3 (USA).iso`; `dat-t50` (interp, `EnableEE=false`); state `t50-sc-state` (T50 SC-settled F1) |
| Capture 1 (no watch2) | CWINDOW 535, TARGET 541 PATHS seen, `spw` 1536, `T56_CAP` 24, `T56W_ARMED` 0, `ctag` 3606; LOADED 1.6194/47; F8 `t56a-shot-sc.png`; trace `t56a-trace.txt` 675,216 B sha256 `428b16d140024d91e70b5f8b37e8a782a5272b54982a016d98d0a6d73eda5624` |
| Capture 2 (watch2 = 8 EE addrs) | CWINDOW 536, TARGET 542, `spw` 1536, caps 24, ARMED 3 (`naddr=8` × RI/FPU/VU0), `ctag` 2011; LOADED 1.6058/46; F8 `t56b-shot-sc.png`; trace `t56b-trace.txt` 674,829 B sha256 `5c8412c0bd30dd99a0e053b6c514690b5f2895730ae056315abb35c269c427e5` |
| Capture 3 (watch2 = 24 addrs, all aliases) | CWINDOW 531, TARGET 537, `spw` 1536, caps 24, ARMED 3 (`naddr=24`), `ctag` 2908; LOADED 1.5045/36; F8 `t56c-shot-sc.png`; trace `t56c-trace.txt` 672,834 B sha256 `92ac9c81a748928666d8a62422b081aff4a62260a9e17cc26dccc3829cc13329` |
| Poll logs | `t56a/b/c-poll.log` |

Builds: b1 fail (compile) + fixup + b2 clean (3 TUs + 2 links). Captures:
3/3, no infra kills (foreground held-ssh recipe from T51 §T51-6 held).
Bytesize new bytes ≈ 140 MB of 2 GB (3 rotated emulogs ~44 MB each
dominate; `t56stage/` scripts + traces).

## T56-2. The patch

`t56-hook.py` (validate-all-then-write, idempotent) + `t56-fix.py`
(2 generator bugs, §T56-8.7). Touched files: `R5900OpcodeImpl.cpp`,
`FPU.cpp`, `VU0.cpp`, `SPR.cpp`.

| Hook | Anchor | What |
| --- | --- | --- |
| T56 RI decl | `static void t51w_watch(…)` (×1) | `g_t56_fixed[8]` + per-word hits, `/tmp/t56-watch2` file watch (≤64, `T56W_ARMED`), `t56_emit` + `t56_watch(vaddr,size,via)` (overlap test, post-write `memRead32`, 64/word + `T56_CAP`) |
| T56 RI 9 calls | 9 `t54w_watch(…)` lines, order-asserted SB/SH/SW/SWL/SWR/SD/SDL/SDR/SQ | `t56_watch(<same args>, "sb"…​"sq")` after each |
| T56 FPU | `void SWC1() {` (×1) + t54 line (×1) | decl + `t56_watch(addr, 4, "swc1")` |
| T56 VU0 | `void SQC2() {` (×1) + t54 line (×1) | decl + `t56_watch(addr, 16, "sqc2")` |
| T56 SPR decl | `#include "MTVU.h"` (×1) + `TestClearVUs` (×1) | `<atomic>` + `g_t48_vsync` extern + `g_t56s_fixed[8]`, `t56s_emit` (with `src`), `t56_spr_watch(sadr,bytes,madr)` (post-copy `psSu32`, per-word src = `madr+(off-sadr)`, wraparound handled, 64/word + `T56_CAP`) |
| T56 SPR 2 calls | `memcpy_to_spr` in `SPR1transfer` (×1) + in `_SPR1interleave` (×1) | `t56_spr_watch(sadr, bytes, madr)` before sadr/madr advance |

Coverage argument (probed, §T56-9): the 9 RI sites are the only
`memWrite*` sites in interpreter opcode bodies (strays at +1335/+1382 are
BIOS boot params); CACHE is not emulated (no hole); `SPR1transfer` +
`_SPR1interleave` are the only `memcpy_to_spr` callers (all toSPR modes).

Line formats: `spw vsync=<n> addr=0x<> value=0x<> via=<sb|sh|sw|swl|swr|sd|sdl|sdr|sq|swc1|sqc2>
pc=0x<> ra=0x<> a0=… s7=…` (24 regs, T54 order); DMA:
`… via=spr-dma src=0x<EE madr> pc=…` (pc/ra/regs are EE interrupt-time
state; the writer key is `src`).

## T56-3. Preservation

G13 rich-dump replay on the T56 gsrunner: **7/7 PNG md5s match the T48
pins exactly** (`b7a3e8db a7929218 bb8b1d85 817e934f ×2 85cf3599 ×2`),
HWSTAT exact (791/37/0/14/320/6), zero `spw`/`T56_CAP`/`T56W_ARMED` lines
(gsrunner runs no EE/DMA).

## T56-4. Writer tables (capture 1; captures 2–3 reproduce exactly, §T56-6)

All 3 captures: 1536 rows = 8 words × 192, vsyncs 0–31 (statefile boot;
settled throughout per T55), 0 grammar rejects. Every word capped at 64
in 3 TUs (8 VU0 + 8 SPR + 8 RI = 24 `T56_CAP`); FPU(`swc1`) never fires.

Item `0x70000000` words (vsync span 0–21 = hottest, capped first):

| word | vias (n) | values (n) |
| --- | --- | --- |
| `0x70000000` (w0) | sqc2 64 (pc `0x386cc4` ra `0x310810`); spr-dma 64 (pc `0x371d90` ra `0x38f53c`); sd 62 (`0x379a4c` ×43 + `0x3796b8` ×19, vsync 0 only); sq 2 (`0x3683a8` ra `0x3687d0`, vsync 0 only) | `0x10000010` 45 (sd) · `0xcc` 42 (spr-dma srcs 2/3) · **`0x1b0` 22 (spr-dma src `0x809670`)** · floats (sqc2) |
| `0x70000004` (w1) | same shape | `0x0` 64 (sqc2) · `0x1414294` 42 · **`0x814884` 22 (src `0x809674`)** · floats |
| `0x70000008` (w2) | same shape | `0x0` 78 · **`0x2a0` 22 (src `0x809678`)** · `0x280` 21 · `0x1c0` 21 |
| `0x7000000c` (w3) | same shape | `0x0` 170 · **`0x6efd00` 11 even / `0x623080` 11 odd (src `0x80967c`)** |

Item `0x70000500` words (span 0–31):

| word | vias (n) | values (n) |
| --- | --- | --- |
| `0x70000500` (w0) | sqc2 64; spr-dma 64; sd 64 (`0x3792fc`, vsyncs 0–12, capped) | `0xcc` 42 · **`0x1b0` 22 (src `0x809b70`)** · floats (sqc2/sd) |
| `0x70000504` (w1) | same | **`0xb5c616` 22 (src `0x809b74`)** · `0x1414294` 42 · floats |
| `0x70000508` (w2) | same (sd pc `0x379334`) | **`0x6ea0` 22 (src `0x809b78`)** · `0x2a0`/`0x1c0` 21 each |
| `0x7000050c` (w3) | same | **`0x6f7920` 11 even / `0x62aca0` 11 odd (src `0x809b7c`)** · `0x0` 106 · `0x7fffff` 64 (sqc2) |

DMA-time register images (all spr-dma rows): `a1=0x70000000`
(dest sadr), `s1=0x00809670`-family (src), **`s6=0x008095f0`** =
T55's hash base `a0=s6`.

## T56-5. The per-vsync DMA staging (all captures agree)

Every vsync stages each item **3× in fixed order** (12 rows/vsync/item;
shown for word0, vsyncs 3–5 identical):

| order | src (item0) | w0 value | src (item-0x500) | w0 value |
| --- | --- | --- | --- | --- |
| 1st | `0x809670` | `0x1b0` | `0x809b70` | `0x1b0` |
| 2nd | `0x80ce70` | `0xcc` | `0x80d370` | `0xcc` |
| 3rd | `0x810670` | `0xcc` | `0x810b70` | `0xcc` |

Src families hold full items: `0x809670` → `(0x1b0, 0x814884,
0x2a0, 0x6efd00/0x623080)`; `0x80ce70` → `(0xcc, 0x1414294, 0x280,
0x0)`; `0x810670` → `(0xcc, 0x1414294, 0x1c0, 0x0)` (item-0x500
family identical with `0x809b70/0x80d370/0x810b70`). w3 parity is
strict: even vsyncs `0x6efd00`/`0x6f7920`, odd `0x623080`/`0x62aca0`,
from the same EE src words. The `0x809670`-family fires every vsync
0–21 (cap; cadence past the cap is extrapolated, §T56-8.3).

Reading (no verdict): the T55 `w0=0x1b0` items arrive via the **first**
of three per-vsync toSPR stagings. The last staging of each vsync is a
0xcc-item — how the walker still reads 0x1b0 (T55) is an ordering
question between the DMA and the `sub_00362DE8` walk, not settled here.

## T56-6. Captures 2–3: the EE source words have no EE-store writer

| Capture | Watch file | Armed | Hits on file addrs |
| --- | --- | --- | --- |
| t56b | 8 addrs (`0x809670..c`, `0x809b70..c`) | `T56W_ARMED naddr=8` ×3 (RI/FPU/VU0) | **0** |
| t56c | 24 addrs (above × kuseg `0x00…` + KSEG1 `0xA0…` aliases) | `naddr=24` ×3 | **0** |

Both captures reproduce capture 1's fixed-word census exactly
(1536/24, identical via/pc/src/value distributions). The staging
buffers' w0/w1/w2 are baked pre-load (scene build); the w3 word
changes every vsync (§T56-5) through a path that is **not** an EE
store in any alias mapping. fromSPR (SPR→EE) and SIF (IOP→EE) DMAs
are unhooked — that is where the per-vsync w3 update must come from,
or nowhere observed (open, §T56-8.6).

## T56-7. E44 join keys (for the orchestrator)

| Fact | T56 (PCSX2, healthy) |
| --- | --- |
| Writer of `w0=0x1b0` at `0x70000000` / `0x70000500` | toSPR DMA, guest pc `0x371d90` ra `0x38f53c`, every vsync, first of 3 stagings |
| EE staging buffers | `0x809670..0x80967c` (item0), `0x809b70..0x809b7c` (item-0x500); full item contents §T56-5; DMA-time `s6=0x8095f0` (T55's hash base) |
| EE-store writers of the staging buffers | none in-window (all aliases watched, armed, 0 hits) |
| Other scratchpad writers (same words) | SQC2 uploader `0x386cc4` (floats/VU data, capped); SD loops `0x379a4c/0x3796b8` (vsync 0 only @item0), `0x3792fc/0x379334` (floats @item-0x500); SQ `0x3683a8` (vsync 0 only); SWC1 never |
| Order vs walker | open: last-DMA-per-vsync is a 0xcc-item, yet the walker reads 0x1b0 (T55) |

## T56-8. Gaps, overruns

1. Builds: b1 compile error + b2 clean = 2/2 within the brief's ≤2
   (T55-shaped authoring miss, no extra full build).
2. Captures 3/3 (brief's ≤3: 1 census + 1 conditional + 1 alias sweep,
   no rebuilds for 2/3). ~1.2 h wall; bytesize ≈140 MB new of 2 GB.
3. Caps at 64/word/TU cut every word (item0 @vsync 21, item-0x500
   @vsync 31): per-vsync cadence past the cap is extrapolated from
   0–21/0–31, not observed (cap, not silence). The 3×/vsync order and
   w3 parity are exact inside the window.
4. `ctag` varies across the three boots (3606/2011/2908): T51c-window
   kill-timing jitter, same class as T55-7.6. Route confirmed by
   LOADED (1.62/47, 1.61/46, 1.50/36 — same <2.0 SC band), F8 PNGs,
   CWINDOW→PATHS, and exact spw reproduction ×3.
5. Savestate load writes scratchpad directly (no EE store, no DMA):
   pre-window staging is invisible to this watch by construction.
6. The per-vsync w3-pointer update path is unidentified (fromSPR/SIF
   unhooked). DMA transfer totals (sadr/qwc) were not logged, only
   overlapping words + per-word src.
7. `t56-fix.py` repairs 2 `t56-hook.py` authoring bugs (RI call-line
   paren placement; SPR emit decl params). Committed pair documents
   the sequence, as T55.
8. LOADED p99 36–47 vs T55's 46 (same watch-logging jitter class;
   speed gate already passed on gsrunner, §T56-3).

## T56-9. Exact commands

Bytesize over foreground `ssh bytesize` + `wsl -d Ubuntu` (no `>|<|` in
the ssh string; multi-step logic in staged files; transfers via
`C:/Users/bradr/t56stage/`): probes (`probe1..6.sh`) → `t56-hook.py`
(validate-all-then-write) → `t56-build.sh` (`cmake --build …/build
--target pcsx2-qt pcsx2-gsrunner -j2`; b1 fail; `t56-fix.py`; b2 clean;
SHAs §T56-1) → `t56-replay.sh` (G13 dump, 7/7 + HWSTAT) → `t56-cap.sh`
(`TAG=t56a`, no watch2; `TAG=t56b WATCH2_SRC=…` 8 addrs; `TAG=t56c
WATCH2_SRC=…` 24 alias addrs; statefile, free-gate, CWINDOW→PATHS V+6,
F8) → extract (`t56-extract.sh` grammar, 0 rejects all three) +
analyze (`t56-analyze.py`) → `git diff --output=…/t56-patch.diff --
<4 files>` (note: `--output` must precede `--`; post-`--` it is parsed
as a path).
`git log -1` checked before commit (main @ `c57fa54` + prior lane commits).

## T56-10. Receipts

Repo (this commit): `local/research/T56/` — REPORT.md,
`t56-patch.diff` (43,830 B), appliers (`t56-hook.py`, `t56-fix.py`),
build/cap/extract/analyze/replay/patch scripts, `t56-watch2.txt` (cap-2
file) + `t56-watch2b.txt` (cap-3 alias file), `t56a/b/c-trace.txt` (+SHAs
§T56-1), `t56a/b/c-poll.log`, F8 `t56a/b/c-shot-sc.png`, probes
(`probe1..6.sh`). Bytesize residue under cap: `t56stage/` (scripts,
traces, poll logs, PNGs, `t56-patch.diff`, watch files), rotated
emulogs, `t56-frames/`, both binaries (§T56-1).
