# T53 REPORT — PCSX2: the EE store that stamps 0x434990 into the chain CALL tags

Brief `local/muse/prompts/T53.md`. Tables + receipts; the orchestrator decides.
Read first: `AGENTS.md`, `local/AGENTS.local.md`,
`local/research/T51/REPORT.md` (§T51-5: CALL→`0x434990` sites
`0x63d430/0x63dcb0/0x70a0b0/0x70a930`; raw watch saw 0 writes),
`local/research/E41/REPORT.md` (recomp writes arrive via an uncached mirror
and/or a low-level fast path), `local/muse/prompts/E42.md` (recomp side).

## T53-0. Mission table

| # | Mission | Result |
| --- | --- | --- |
| 1 | Folded-mirror ADDR watch (8 words) in every EE interp store path | DONE — RI fold-fix (5 edits) + new SWC1 (FPU) / SQC2 (VU0) hooks, all anchors first try |
| 2 | TU attribution (`tu=ri/swc1/sqc2`) | DONE — T53b, one trailing field, prefix-compatible |
| 3 | Builds ≤2 | DONE — b1 + b2, both clean first try |
| 4 | Preservation (G13 replay 7/7 + HWSTAT, zero watch lines) | DONE on both binaries |
| 5 | Capture 1: SC-settled watch, no TU tag | DONE — 512 hits (8 addrs × 64 cap), transcript kept |
| 6 | Capture 2: SC-settled watch with TU tag | DONE — 512 hits, all `tu=ri`; trace + PNG in repo |
| 7 | Receipts + `[T53]` commit, no push | DONE (this file + dir) |

Headline for the orchestrator: **all 8 CALL ADDR words ARE EE-stored every
~2nd vsync from boot: the four `0x434990`-bound words by one `SW`-class store
at pc `0x365994`, the four `0x435bd0`-bound words by one at pc `0x3651d8`,
both `ra=0x363cfc`, all `tu=ri`, all through the `0x30` mirror** (dest regs
read `0x3063xxxx`) — which is exactly why T51's `& 0x1fffffff` watch saw 0.
This discriminates E40's two residual gaps in favor of **mirror alias, not a
fast-path bypass**: the plain opcode-level tap catches it once folded.

## T53-1. Pins

| Pin | Value |
| --- | --- |
| PCSX2 tree | `9056c08349cc29ad02a6d1a3a4133259019195af` (`/home/brad/pcsx2-g7/pcsx2`); base = T51-end working tree + T53 hooks below |
| Post-T53 source SHAs | R5900OpcodeImpl `fb243c41…64c673f`, FPU `dac16d5b…6bda111`, VU0 `215c9de3…67df1f2` |
| Build-1 bins (fold + SWC1/SQC2, no TU tag) | qt `70b60b2d…185e851`, gsrunner `8b7e5cbc…99cfedb` |
| Build-2 bins (final, +`tu=`) | qt `d4ae80f6…b182c15`, gsrunner `63bb2902…97f97dfe` |
| Patch | `t53-patch.diff` 75,545 B sha256 `6d4e8764…b31b84d` (full working-tree diff, T48–T53; T53's own hunks are the `T53`-marked lines, §T53-2) |
| Inputs | ISO `SSX 3 (USA).iso`; `dat-t50` (interp, `EnableEE=false`); state `t50-sc-state` (T50 SC-settled F1) |
| Watch file | `/tmp/t53-watch`: `0x63d434 0x63dcb4 0x70a0b4 0x70a934` (0x434990-bound, tag_at+4) + `0x63c654 0x63c8a4 0x63cb64 0x63cdf4` (0x435bd0-bound, tag_at+4 of T51's 0x63c650-class CALL sites) |
| Capture 1 | CWINDOW 542, `tagaddrwrite` 512, armed 3, cap 8, ctag 1803; LOADED 1.5634/42; trace sha `fc0b6e00…cbbf62d` (transcript only — file overwritten by capture 2, §T53-6.6) |
| Capture 2 (canonical) | `t53-trace.txt` 300,674 B sha256 `33140a14…15040d3c`: 512 tagaddrwrite, 3 ARMED, 8 CAP, 0 rejects; CWINDOW 546; F8 `t53-shot-sc.png`; LOADED 1.5437/41 |
| Poll log | `t53-poll.log` (capture 2) |

Builds: b1 clean first try (3 TUs + 2 links); b2 (TU tag) clean first try = 2/2.
Captures: 2/2, no infra kills (foreground held-ssh recipe from T51 §T51-6 held).
Bytesize new bytes ≈ 90 MB of 5 GB (two 43 MB emulogs dominate; `t53stage/` 1 MB).

## T53-2. The patch

T51 hooked the 9 integer store opcodes in `R5900OpcodeImpl.cpp` but compared
raw (`& 0x1fffffff`, which maps only `0x8/0x9/0xA/0xB` mirrors) and never
hooked the two non-integer EE store opcodes. Store-path audit (this lane):

| Path | Location | T53 status |
| --- | --- | --- |
| SB/SH/SW/SWL/SWR/SD/SDL/SDR/SQ | R5900OpcodeImpl.cpp (9× `t51w_watch`) | KEPT, fold-fixed (§below) |
| SWC1 | FPU.cpp | NEW `t53w_watch(addr,4)` + self-contained T53 block |
| SQC2 | VU0.cpp | NEW `t53w_watch(addr,16)` + self-contained T53 block |
| LL/SC | — | no interpreter impl exists (game would trap); nothing to hook |
| SDC1 | — | does not exist on the EE |
| MMI / COP0 | MMI.cpp / COP0.cpp | register-only ops, no EE-RAM stores |
| CACHE / PREF | R5900OpcodeImpl.cpp | stub / no-op by upstream design |
| SYSCALL-internal memWrite32/8 (ExecPS2 param setup) | R5900OpcodeImpl.cpp:1269/1316/1318 | HLE setup, excluded (as T51); noted |
| VIF/GIF/SIF DMA direct-to-RAM | various | non-EE-CPU writers, excluded by brief scope; E41 found zero plants there on the recomp side |

RI fold-fix (5 one-line edits, `t51w_*` names kept, markers now `T53W_*`,
file now `/tmp/t53-watch`): watch-addr store `(a & 0x0fffffff) & ~3u`,
store-addr `pbase = vaddr & 0x0fffffff`. T51's `t51e_store_watch`/`t50_read_watch`
masks left untouched (different windows, out of scope).
T53b: one trailing ` tu=ri|swc1|sqc2` field per TU format literal (head-anchored
edit; the shared GPR tail also matches T50's `srcread` line, so tail-anchoring
was rejected during authoring). Per-TU static state ⇒ the "first 64 per
address" cap is per (address, TU); worst case 64×3 lines per address (§T53-6.1).
Line format is otherwise T51-byte-identical: post-write `memRead32(w)` word +
pc/ra + 24 GPRs.

## T53-3. Preservation

G13 rich-dump replay on build-1 AND build-2 gsrunner: **7/7 PNG md5s match the
T48 pins exactly** (`b7a3e8db a7929218 bb8b1d85 817e934f ×2 85cf3599 ×2`),
HWSTAT exact (791/37/0/14/320/6), zero `tagaddrwrite`/`T53W_*` lines
(gsrunner runs no EE).

## T53-4. The watch table (capture 2, canonical)

All 8 words capped at 64 hits each (512 lines, 0 rejects, no off-watch addrs).
Every hit is a single (value, pc, ra, tu) group per address:

| addr (tag_at+4) | CALL target | value | storing pc | ra | tu | n | vsync range | first |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0x63d434 | 0x434990 | 0x434990 | 0x365994 | 0x363cfc | ri | 64 | 1–127 | 1 |
| 0x63dcb4 | 0x434990 | 0x434990 | 0x365994 | 0x363cfc | ri | 64 | 1–127 | 1 |
| 0x70a0b4 | 0x434990 | 0x434990 | 0x365994 | 0x363cfc | ri | 64 | 0–126 | 0 |
| 0x70a934 | 0x434990 | 0x434990 | 0x365994 | 0x363cfc | ri | 64 | 0–126 | 0 |
| 0x63c654 | 0x435bd0 | 0x435bd0 | 0x3651d8 | 0x363cfc | ri | 64 | 1–127 | 1 |
| 0x63c8a4 | 0x435bd0 | 0x435bd0 | 0x3651d8 | 0x363cfc | ri | 64 | 1–127 | 1 |
| 0x63cb64 | 0x435bd0 | 0x435bd0 | 0x3651d8 | 0x363cfc | ri | 64 | 1–127 | 1 |
| 0x63cdf4 | 0x435bd0 | 0x435bd0 | 0x3651d8 | 0x363cfc | ri | 64 | 1–127 | 1 |

512/512 lines `tu=ri`, 0 from `swc1`/`sqc2` (all three TUs armed: the FPU/VU0
hooks are live, just never overlap the watch). Distinct storing pcs overall:
`0x3651d8`, `0x365994` (same caller `ra=0x363cfc`). 64 hits over ~128 vsyncs
⇒ roughly every 2nd vsync from boot — the same even-vsync cadence E41 saw in
the recomp's `plant` lines. Caps fired at vsync 128/129, so the post-129
window is unobserved (cap, not silence).

Per-word pointer/index fields (first hit; constant fields in Table B):

| addr | a3 / s0 (src ptr) | v1 / t1 (dest, 0x30 mirror) | s2 / s6 (index) | s3 |
| --- | --- | --- | --- | --- |
| 0x63d434 | 0x623080 | 0x3063d430 | 0x13 | 0x85aabc |
| 0x63dcb4 | 0x62aca0 | 0x3063dcb0 | 0x1d | 0x85abac |
| 0x70a0b4 | 0x6efd00 | 0x3070a0b0 | 0x13 | 0x85aabc |
| 0x70a934 | 0x6f7920 | 0x3070a930 | 0x1d | 0x85abac |
| 0x63c654 | (a0=0x3063c650) | 0x3063c650 | s2=0, s6=1 | 0x85ac24 |
| 0x63c8a4 | (a0=0x3063c8a0) | 0x3063c8a0 | s2=1, s6=2 | 0x85ac54 |
| 0x63cb64 | (a0=0x3063cb60) | 0x3063cb60 | s2=2, s6=3 | 0x85ac9c |
| 0x63cdf4 | (a0=0x3063cdf0) | 0x3063cdf0 | s2=4, s6=4 | 0x85ac3c |

Table B — full register images (first hit of each pc-class; remaining 6 words
differ only in the Table-A fields above; complete lines in `t53-trace.txt`):

- pc `0x365994` → `0x63d434` @vsync 1: `a0=10000007 a1=0 a2=0 v0=50000000
  t0=69cd0 t2=180 t3=623080 t4=50000000 t5=53 t6=10000002 t7=8 t8=8732c0
  t9=1fffa20 s1=0 s4=8095f0 s5=1fffa20 s7=1e` (a3/s0/v1/t1/s2/s3/s6 per Table A).
- pc `0x3651d8` → `0x63c654` @vsync 1: `a1=0 a2=0 a3=0 v0=50000000 v1=50000000
  t0=69cd0 t2=180 t3=0 t4=1fffa14 t5=1fffa10 t6=2 t7=8695f0 t8=873440
  t9=1fffa20 s0=0 s1=1 s4=8095f0 s5=1fffa20 s7=1` (a0/v1/t1/s2/s3/s6 per Table A).

Reading (no verdict): one writer function per value family (shared ra), the
dest address rides in t1/v1 (0x365994) resp. a0 (0x3651d8), and neither stored
value appears in any of the 24 logged GPRs — consistent with an immediate-form
(`lui/ori` + `sw`) or an unlogged source reg (`$at/k0/k1/gp/sp/fp`, §T53-6.2).
Single pc per word + full-word value ⇒ single `SW` (a lone SWL/SWR, SD or SQ
could not write these misaligned words without trapping).

## T53-5. The mirror finding (why T51 saw 0)

The destination registers carry the `0x30` mirror (`v1=t1=0x3063d430…`,
`a0=0x3063c650…`). T51's mask arithmetic: `0x3063d434 & 0x1fffffff =
0x1063d434 ≠ 0x063d434` → every hit missed. Folded: `0x3063d434 &
0x0fffffff = 0x0063d434` → hit. The opcode-level tap catches the stores, so
no inlined/below-opcode fast path is involved on the PCSX2 side — E40's gap
pair resolves to **mirror alias**. Capture-2 ctag count (3606 over V546–547)
reproduces T51-B's 3606-line shape; the four `0x434990` sites are the same
words the watch now sees stamped.

## T53-6. Gaps, overruns

1. 64-cap is per (address, TU); a two-TU writer would show 128 lines on one
   address. Observed 64 exactly on all 8 ⇒ single-TU writers; no cap split.
2. The exact integer opcode (SW vs SWL/SWR/…) is inferred, not logged: the
   watch logs addr+size overlap, not the opcode. The guest instruction word at
   `0x365994`/`0x3651d8` would settle it (SW expected); left for E42/follow-up.
   Source reg may be `$at/k0/k1/gp/sp/fp` (unlogged by the T51 line format).
3. Caps at vsync 128/129 cut the window: stamping cadence past SC-settle+~130
   vsyncs is unobserved (cap, not silence).
4. LOADED p99 41–42 vs T51's 21/23 (mean 1.54–1.56, same <2.0 SC band; F8 PNG
   + CWINDOW + ctag confirm the route). Likely watch-logging jitter; the speed
   gate already passed on the diagnostic-free gsrunner replay (§T53-3).
5. Capture 1 (no-`tu` format) survives only as transcript counts + trace sha
   `fc0b6e00…cbbf62d` (CWINDOW 542, 512/3/8, ctag 1803, LOADED 1.5634/42);
   its files were overwritten by capture 2 (same filenames). Capture 2
   (CWINDOW 546, 512/3/8, ctag 3606, LOADED 1.5437/41) is the in-repo canonical.
6. Budgets: 2 builds + 2 captures + 2 replays; ~25 min wall; bytesize ≈90 MB
   new of 5 GB.

## T53-7. Exact commands

Bytesize over one foreground `ssh bytesize` each (WSL-Ubuntu; notes: remote
one-liners must avoid `>|<|` — Windows cmd parses them inside the ssh string;
multi-step logic lives in staged script files; file transfer is
`scp ⇄ C:/Users/bradr/` + `cp ⇄ /mnt/c/Users/bradr/` with sha256 both ends):
staged `t53stage/` = `t53-hook.py` (validate-all-then-write) → `t53-build.sh`
(`cmake --build …/build --target pcsx2-qt pcsx2-gsrunner -j2`; SHAs §T53-1) →
`t53-replay.sh` (G13 dump, 7/7 + HWSTAT) → `t53-cap.sh` (statefile,
8-word `/tmp/t53-watch`, free-gate, CWINDOW→PATHS V+2, F8) → extract
(`t53-extract.sh` grammar, 0 rejects) + analyze (`t53-analyze.py`) →
`t53b-hook.py` (TU tag) → rebuild + replay + capture 2 → `git diff
--output=…/t53-patch.diff`. `git log -1` checked before commit (main @
`1a041ce` + prior lane commits).

## T53-8. E42 join keys (for the orchestrator)

| Fact | T53 (PCSX2, healthy) |
| --- | --- |
| 0x434990 stamper | pc `0x365994`, ra `0x363cfc`, integer store (`tu=ri`), dest in t1/v1 via `0x30` mirror, value not in logged GPRs |
| 0x435bd0 stamper | pc `0x3651d8`, ra `0x363cfc`, integer store, dest in a0 via `0x30` mirror, value not in logged GPRs |
| Cadence | ~every 2nd vsync from boot (all 8 words capped 64 by vsync 128/129) |
| SWC1/SQC2 | hooked, armed, zero overlapping hits — excluded as stamp paths |
| E40-gap verdict | mirror alias (0x30); no fast-path bypass on this side |

## T53-9. Receipts + recommendation

Repo (this commit): `local/research/T53/` — REPORT.md, `t53-patch.diff`
(75,545 B), appliers (`t53-hook.py`, `t53b-hook.py`), build/cap/extract/
analyze/replay scripts, `t53-trace.txt` (sha `33140a14…15040d3c`),
`t53-poll.log`, F8 `t53-shot-sc.png`. Bytesize residue under cap: `t53stage/`
(scripts, `t53-patch.diff`), both traces, both poll logs (cap-1 lines in this
report), rotated emulogs, `t53-frames/`, both binaries (§T53-1).

Recommended next action (orchestrator): hand pcs `0x365994`/`0x3651d8`
(+ra `0x363cfc`, reg images above) to E42's codegen read — the healthy
chain-builder cluster is now two addressed stores, and the value-formation
question (immediate vs table load feeding the store) is answerable from the
guest disassembly at those pcs.
