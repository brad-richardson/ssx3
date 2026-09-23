# T54 REPORT — PCSX2: draw-record census by mode and the mode-6 producers (healthy side of E43)

Brief `local/muse/prompts/T54.md`. Tables + receipts; the orchestrator decides.
Read first: `AGENTS.md`, `local/AGENTS.local.md`,
`local/research/T53/REPORT.md`, `local/muse/prompts/E43.md`.

## T54-0. Mission table

| # | Mission | Result |
| --- | --- | --- |
| 1 | Census hook at EE pc `0x363cf4` (drec/drecs) + folded producer watch (dprod) on T53's clone, EE interp | DONE — Interp census + RI(decl+9)/SWC1/SQC2 watch, all anchors first try (one authoring retry on a shared `_SetLink` anchor) |
| 2 | Builds ≤2 | DONE — 1 build, clean first try |
| 3 | Preservation (G13 replay 7/7 + HWSTAT, zero T54 lines) | DONE |
| 4 | Capture 1: SC-settled census, modes per frame + record words | DONE — 928 vsyncs, 6 records/vsync, all `a1=0`; modes from record w0 bits: 4× mode-3 + 2× mode-6 |
| 5 | Capture 2: producer watch on mode-6 record words | DONE — all 8 words, 64 hits each, single RI cluster `0x394fdc–0x394fe8`, ra `0x362f70`, SWC1/SQC2 zero |
| 6 | Receipts + `[T54]` commit, no push | DONE (this file + dir) |

Headline for the orchestrator: **at SC settled the walker at `0x363cf4`
walks exactly 6 draw records every vsync — 4 with record-word mode bits 3
(`0x85ac24/54/9c/3c`, w0=`0xcc`) and 2 with mode bits 6 (`0x85aabc/ac`,
w0=`0x1b0`) — while `a1` at the jal reads 0 on all 11,088 calls, so the
E43 model "a1 = (*(s3)&0x3C0)>>6" does not hold at this site; the mode
travels in the record word, not the register.** The two mode-6 records are
rebuilt EE-side **every vsync from boot** by one 4-store RI cluster
(`0x394fdc/0x394fe0/0x394fe4/0x394fe8`, ra `0x362f70`); their w3 word
ping-pongs two source pointers by vsync parity
(`0x6efd00`/`0x623080`, `0x6f7920`/`0x62aca0` — the same pointers T53 saw
in the stampers' regs). SWC1/SQC2 armed, zero overlap: excluded.

## T54-1. Pins

| Pin | Value |
| --- | --- |
| PCSX2 tree | `9056c08349cc29ad02a6d1a3a4133259019195af` (`/home/brad/pcsx2-g7/pcsx2`); base = T53-end working tree + T54 hooks below |
| T54 binary SHAs | qt `1fb9ab33…94bed`, gsrunner `7c523434…44a53ea` |
| Patch | `t54-patch.diff` 32,776 B sha256 `181de32c…245011c` (diff of the 4 touched files vs HEAD; carries T48–T54 hunks, 42 `T54` marker lines) |
| Inputs | ISO `SSX 3 (USA).iso`; `dat-t50` (interp, `EnableEE=false`); state `t50-sc-state` (T50 SC-settled F1) |
| Watch file (cap 2) | `/tmp/t54-watch-list`: `0x85aabc/…ac` +0/+4/+8/+12 (8 words) |
| Capture 1 (census) | CWINDOW 503, `drec` 928, `drecs` 5574, `dprod` 0, armed 0, ctag 3606; LOADED 1.5205/37; F8 `t54a-shot-sc.png`; trace `t54a-trace.txt` 552,900 B sha256 `5e7e7b0b…752d98` |
| Capture 2 (producer) | CWINDOW 500, `drec` 920, `drecs` 5526, `dprod` 512, armed 3, cap 8, ctag 3606; LOADED 1.5503/40; F8 `t54b-shot-sc.png`; trace `t54b-trace.txt` 732,965 B sha256 `084cbc63…1b85ec78` |
| Poll logs | `t54a-poll.log`, `t54b-poll.log` |

Builds: 1/2 (4 TUs recompiled + link, clean first try). Captures: 2/3, no
infra kills (foreground held-ssh recipe from T51 §T51-6 held). Bytesize new
bytes ≈ 90 MB of 5 GB (two ~41 MB emulogs dominate; `t54stage/` scripts).

## T54-2. The patch

`t54-hook.py` (validate-all-then-write, idempotent) on the T53 tree:

| Hunk | File:anchor | What |
| --- | --- | --- |
| T54-Interp | `Interpreter.cpp` `#include "Common.h"` + `void JAL()` | Census decl (`t54_census`, per-vsync `cnt[16]`/`seen[16]`, flush-on-vsync-change via `g_t48_vsync`); at JAL entry `if (cpuRegs.pc == 0x363cf8) t54_census(a1=r[5], s3=r[19])` — execI pre-increments pc, so `0x363cf8` inside JAL is the jal @`0x363cf4`; hook runs before `_SetLink`, ra intact |
| T54-RI | `R5900OpcodeImpl.cpp` before `t51w_watch` decl + after each of the 9 `t51w_watch(…)` calls | `t54w_watch` decl (own statics, `/tmp/t54-watch`, fold `& 0x0fffffff`, `T54W_ARMED/CAP`, `dprod … tu=ri`) + 9 same-arg calls |
| T54-FPU | `FPU.cpp` `void SWC1()` + `t53w_watch(addr,4)` line | `t54w_watch` decl (`tu=swc1`) + call after the T53 line |
| T54-VU0 | `VU0.cpp` `void SQC2()` + `t53w_watch(addr,16)` line | `t54w_watch` decl (`tu=sqc2`) + call after the T53 line |

Line formats: `drec vsync=<n> mode=<m> count=<c>` (flushed on first call of
the next vsync); `drecs vsync=<n> mode=<m> addr=0x<x> w0..w3` (first 8 per
mode per vsync); `dprod vsync=<n> addr value pc ra a0..a3 v0 v1 t0..t9 s0..s7
tu=<ri|swc1|sqc2>` (post-write word, first 64 per address per TU). Authoring
retry: a `\t_SetLink(31)` anchor matched 5× (shared by BGEZAL-class ops) —
dropped, unused by any replacement.

## T54-3. Preservation

G13 rich-dump replay on the T54 gsrunner: **7/7 PNG md5s match the T48 pins
exactly** (`b7a3e8db a7929218 bb8b1d85 817e934f ×2 85cf3599 ×2`), HWSTAT
exact (791/37/0/14/320/6), zero `drec/drecs/dprod/T54W_*` lines (gsrunner
runs no EE).

## T54-4. Census: modes per frame (captures 1+2 agree exactly)

`a1` at the jal is **0 on every call**: cap-1 5,568/5,568, cap-2 5,520/5,520
(`modes ever seen: [0]`). 6 calls **every** vsync, no exceptions over
928/920 vsyncs (cap-1 range 0–927, cap-2 0–919; the kill-cut final vsync
keeps its 6 `drecs` lines but no `drec` summary — 5,574 = 928×6+6).

| vsync row (every vsync, both captures) | mode 0 (a1) count |
| --- | --- |
| 0 … 927/919 | 6 |

Record identities come from the words (full per-vsync coverage: only 6
records exist, all ≤ the 8/mode cap). Words constant over the whole trace
except mode-6 w3 parity ping-pong (464/465 splits):

| record addr | w0-bit mode `(w0&0x3C0)>>6` | w0 | w1 | w2 | w3 |
| --- | --- | --- | --- | --- | --- |
| 0x85ac24 | 3 | 0xcc | 0x1414294 | 0x120 | 0x0 |
| 0x85ac54 | 3 | 0xcc | 0x1414294 | 0x140 | 0x0 |
| 0x85ac9c | 3 | 0xcc | 0x1414294 | 0x1c0 | 0x0 |
| 0x85ac3c | 3 | 0xcc | 0x1414294 | 0x200 | 0x0 |
| 0x85aabc | **6** | 0x1b0 | 0x814884 | 0x2a0 | 0x6efd00 even / 0x623080 odd |
| 0x85abac | **6** | 0x1b0 | 0xb5c616 | 0x6ea0 | 0x6f7920 even / 0x62aca0 odd |

The 6 record addresses are exactly T53 Table-A's `s3` values, and the w3
alternates are exactly T53's stamper src regs (`a3/s0=0x623080`,
`v1/t1` dests aside): the census records feed the T53 stampers. `ctag`
3606 in both captures reproduces T51-B/T53 exactly.

## T54-5. Mode-6 producers (capture 2)

All 8 watched words capped at 64 hits each (512 lines, 0 rejects, no
off-watch addrs). Every hit `tu=ri` (SWC1/SQC2 armed, zero overlap —
excluded as producer paths). One cluster, ra `0x362f70` throughout:

| addr (word) | value(s) | storing pc(s) | n | vsync range | first |
| --- | --- | --- | --- | --- | --- |
| 0x85aabc (w0) | 0x1b0 | 0x394fe0 | 64 | 0–63 | 0 |
| 0x85aac0 (w1) | 0x814884 | 0x394fdc + 0x394fe8 (32+32) | 64 | 0–31 | 0 |
| 0x85aac4 (w2) | 0x2a0 | 0x394fdc + 0x394fe8 (32+32) | 64 | 0–31 | 0 |
| 0x85aac8 (w3) | 0x6efd00 even / 0x623080 odd | 0x394fe4 | 64 | 0–63 | 0/1 |
| 0x85abac (w0) | 0x1b0 | 0x394fe0 | 64 | 0–63 | 0 |
| 0x85abb0 (w1) | 0xb5c616 | 0x394fdc + 0x394fe8 (32+32) | 64 | 0–31 | 0 |
| 0x85abb4 (w2) | 0x6ea0 | 0x394fdc + 0x394fe8 (32+32) | 64 | 0–31 | 0 |
| 0x85abb8 (w3) | 0x6f7920 even / 0x62aca0 odd | 0x394fe4 | 64 | 0–63 | 0/1 |

Producer register images (first hit per record; the two records differ only
in the per-record fields):

- → `0x85aabc` @vsync 0: `a0=00870be8 a1=0085aabc a2=06040679 a3=00000158
  v0=000001b0 v1=000002a0 t0=ef t1=00870be8 … s3=0061ba60 …`
  (a1 = the record address; v0 = the w0 value `0x1b0`; v1 = the w2 value).
- → `0x85abac` @vsync 0: `a0=00870ae8 a1=0085abac a2=0604067b a3=00000058
  v0=000001b0 v1=000006ea0 … s3=0085ab94 …` (same shape, second record).

Reading (no verdict): the mode-6 records are rebuilt EE-side **every vsync
from boot** (first hits @vsync 0 — no scene-build-only baking on this
side): w0/w3 ×1/vsync, w1/w2 ×2/vsync (two pcs each — plausibly SD pairs or
two SWs; the guest instruction words at `0x394fdc–0x394fe8` settle it).
Complete lines in `t54b-trace.txt`.

## T54-6. Gaps, overruns

1. **a1=0 vs E43's model.** E43 (`local/muse/prompts/E43.md`) states the
   walker calls with `a1 = (*(s3) & 0x3C0) >> 6`; observed a1=0 on all
   11,088 calls while the records' w0 bits carry modes 3/6. Either the mode
   is derived from the record inside the callee (not passed in a1), or the
   mode-jal is a different site than `0x363cf4`. The ra chain corroborates
   the site (T53 stampers' ra=`0x363cfc` = return after the jal @`0x363cf4`
   + delay slot). T53's stamper-time `a1=0` (Table B) is consistent with
   this capture. Needs E43's codegen read to resolve; census/producer
   addresses are unaffected (they key on s3/words, not a1).
2. w1/w2 double-hit opcode (SW pair vs SD vs SWL/SWR) is inferred, not
   logged — guest disassembly at `0x394fdc–0x394fe8` settles it.
3. Caps at vsync 32 (w1/w2) / 64 (w0/w3) cut the producer window: per-frame
   rebuild cadence past ~64 vsyncs is extrapolated from vsync 0–63, not
   observed (cap, not silence). The census (uncapped counts) runs the full
   928/920 vsyncs and shows the records walked every vsync throughout.
4. No fresh-boot capture was needed: the producer fires from vsync 0 of the
   statefile boot (per-frame rebuild, not scene-build baking).
5. LOADED p99 37–40 vs T51's 21/23 (means 1.52–1.55, same <2.0 SC band; F8
   PNGs + CWINDOW + ctag-3606 confirm the route). Same watch-logging
   jitter class as T53-6.4; speed gate already passed on gsrunner (§T54-3).
6. Budgets: 1 build + 2 captures + 1 replay; ~15 min wall; bytesize ≈90 MB
   new of 5 GB.

## T54-7. Exact commands

Bytesize over foreground `ssh bytesize` + `wsl -d Ubuntu` (no `>|<|` in the
ssh string; multi-step logic in staged files; transfers via
`C:/Users/bradr/t54stage/`): `t54-hook.py` (validate-all-then-write) →
`t54-build.sh` (`cmake --build …/build --target pcsx2-qt pcsx2-gsrunner
-j2`; SHAs §T54-1) → `t54-replay.sh` (G13 dump, 7/7 + HWSTAT) →
`t54-cap.sh` (`TAG=t54a`, no watch file; `TAG=t54b WATCH_SRC=…` for the
producer run; statefile, free-gate, CWINDOW→PATHS V+2, F8) → extract
(`t54-extract.sh` grammar, 0 rejects both traces) + analyze
(`t54-analyze.py`) → `git diff -- <4 files> --output=…/t54-patch.diff`.
`git log -1` checked before commit (main @ `cc27006` + prior lane commits).

## T54-8. E43 join keys (for the orchestrator)

| Fact | T54 (PCSX2, healthy) |
| --- | --- |
| Walker @`0x363cf4` | 6 records/vsync, every vsync; a1=0 always; s3 = record addr; mode in record w0 bits 6–9 |
| Mode-3 records | `0x85ac24/54/9c/3c`, w0=`0xcc`, fully constant words |
| Mode-6 records | `0x85aabc` (w1=`0x814884` w2=`0x2a0`), `0x85abac` (w1=`0xb5c616` w2=`0x6ea0`); w0=`0x1b0`; w3 = src ptr ping-pong by parity |
| Mode-6 producer | pcs `0x394fdc/0x394fe0/0x394fe4/0x394fe8`, ra `0x362f70`, integer store (`tu=ri`), every vsync; a1=record addr, v0=w0 value |
| w3 alternates | rec1 `0x6efd00`/`0x623080`, rec2 `0x6f7920`/`0x62aca0` — T53's stamper src regs |
| SWC1/SQC2 | hooked, armed, zero overlapping hits — excluded as producer paths |

## T54-9. Receipts

Repo (this commit): `local/research/T54/` — REPORT.md, `t54-patch.diff`
(32,776 B), applier (`t54-hook.py`), build/cap/extract/analyze/replay
scripts, `t54a-trace.txt` (sha `5e7e7b0b…752d98`) + `t54b-trace.txt` (sha
`084cbc63…1b85ec78`), `t54a/b-poll.log`, F8 `t54a/b-shot-sc.png`. Bytesize
residue under cap: `t54stage/` (scripts, both traces, both poll logs,
`T54W` watch list, `t54-patch.diff`), rotated emulogs, `t54-frames/`, both
binaries (§T54-1).
