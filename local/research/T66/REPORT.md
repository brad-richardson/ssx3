# T66 REPORT — PCSX2: the SC camera object at 0x00bc5920 (confirm E50's model)

Brief: `local/muse/prompts/T66.md`. Worker: Claude Code (Opus), on the T65
tree. Tables and receipts; the orchestrator decides. Read first:
`local/research/E50/REPORT.md` (Outcome and the camera tables).

## T66-0. Mission table

| # | Mission | Result |
| --- | --- | --- |
| 1 | EE RAM 0x00bc5920..0x00bc59a0 at settled SC, once per vsync for 3 vsyncs, hex + float | DONE: the object is at that address; 3 identical dumps (§T66-3) |
| 2 | Store watch on 0x00bc5950..0x00bc595c from `t63-menu-state` → K → SC; first 32 writes with pc/ra/regs (+ f-regs for SWC1/SQC2) | DONE: **exactly one write** in the whole run (§T66-4) |
| 3 | Preservation | DONE: G13 replay 7/7 md5 pins + HWSTAT exact, 0 hook lines (§T66-2) |

Budget: **1 build of ≤1, 1 capture of ≤2**, about 40 min of 2 h, and about
260 MB new on bytesize (the capture emulog is 251 MB), within the 1.5 GB cap.

Observations (no verdict):

- **E50's predicted PCSX2 values hold exactly.** The quaternion at +0x30 is
  `80000000 80000000 3f3504f3 3f3504f3` = (−0, −0, 0.7071068, 0.7071068),
  and the position at +0x20 is (0, 200, 0, 1). All 3 settled-SC vsyncs show
  the same words.
- **The quaternion is written once**, 10 vsyncs after K, by
  `sq $a0, 0x30($s0)` at **`0x15e0d4`** in `sub_0015E050` (s0 = 0x00bc5920,
  ra = 0x15e0bc). Nothing else writes it before or after, through settled SC
  (census: one pc, n = 1). No DMA hits the range.
- **Object header word +0x0c = `3f490fdb` = π/4 (float).** π/4 is also the
  half-angle of the stored quaternion (sin = cos = 0.7071068). Header words:
  0.4363323 (= 25° in rad), 5, 5000, π/4, then 5, 5000, 0, 0x6c9.

## T66-1. Pins

| Pin | Value |
| --- | --- |
| PCSX2 tree | `9056c08349cc29ad02a6d1a3a4133259019195af`, T65 working tree + T66 hunks (one TU) |
| Pre-T66 | qt `e85ddbfca5e1c4768e3e8e6da097a50839932c41ae4603953e270f53a47b1696` (= T65 pin); `R5900OpcodeImpl.cpp` `01a060ce00519380b505aa652dd1dc10110d122775dbf8841f2a422d01241086` (copy in `/home/brad/pcsx2-g7/pre-t66/`) |
| T66 qt | `46732713f198dbd4351cecdf2405a09d3d3f59b9e198999166d928cb674f5bbd`, 131,362,144 B |
| T66 gsrunner | `d546787f39df99ee36db6aba7572b91294448849606001356af6272a78868209`, 90,867,440 B |
| Patch | `t66-patch.diff` sha256 `b1273c7ce9a95ab50df59ff9f74e74137f7c0c17670216f239a756ea6e595818` (128 lines, T66 hunks only) |
| Config / input | `dat-t57` (EE + VU0 + VU1 interpreters, MTVU off), statefile `t63-menu-state` (MENU), ISO `SSX 3 (USA).iso` |
| Capture t66a | K at GS vsync 4164 (`T52_MARK scentry`); SC try 1 ident 0.589, settled 0.476, LOADED 1.55; dump gate at 5349 (`T52_MARK scsettled`); F8 `t66a-shot-sc.png` (settled SC, Zoe rendered, viewed) |
| Trace | `t66a-trace.txt` 31 lines, sha256 `566416f27b9dff1d23cd1e352d6fe896ef25f5775b8a4d1711ea104fb9e29959` |
| Capture emulog | 250,909,877 B sha256 `e4be3c1ddc8fe708110f636fc2f039dbf4b6ff87501a43194334198144ba5c5b` (left on bytesize) |

## T66-2. Patch and preservation

`t66-hook.py` checks all 4 anchors before it writes (one TU,
`R5900OpcodeImpl.cpp`) and applied on the first try. It builds on the T58/T59
watch, which every EE-interpreter store (SB…SQ, SWC1, SQC2) and the DMA
paths already call through the segment-aware fold:

| Hunk | What |
| --- | --- |
| T66-1 (before `t58_store_watch`) | `t66_emit`: when a store or DMA overlaps phys 0x00bc5950..0x00bc595f it re-reads the 4 quaternion words. The first 32 events print a full `t66w` line (pc, `at` = pc−4 when it holds `cpuRegs.code`, code, ra, a0–a3, v0, v1, s0–s7, sp, q hex + float). SWC1 adds `t66f` (f0–f31 + ACC) and SQC2 adds `t66v` (VF00–31 + ACC). Past the cap, up to 64 `t66chg` lines print on value changes. `t66cen` is a per-vsync writer census (pc, n, last q). `t66_maybe_dump`: at most one `fopen` per vsync; on `/tmp/t66-dump`, 3 vsyncs of `t66obj` (8 qwords from 0x80bc5920) plus one EE RAM scan (`t66scan`) for T65 §5c's SC camera qw0 words and for (0x3f3504f3, 0x3f3504f3) pairs |
| T66-2/3/4 | calls in `t58_store_watch` (dump gate + range check) and `t58_dma_watch` |

Preservation (`t66-replay.sh`, G13 rich dump):

| Check | Result |
| --- | --- |
| 7 PNG md5 | `b7a3e8db a7929218 bb8b1d85 817e934f 817e934f 85cf3599 85cf3599`: **7/7 = pins** |
| HWSTAT | 791 / 37 / 0 / 14 / 320 / 6: **exact** |
| t66 hook lines in replay | **0** (the one `t66` text match is the dump-path line) |

## T66-3. Object dump at settled SC (GS vsyncs 5349, 5350, 5351: all identical)

| off | addr | w0 | w1 | w2 | w3 | float decode |
|---|---|---|---|---|---|---|
| 0x00 | 0x00bc5920 | 3edf66f4 | 40a00000 | 459c4000 | 3f490fdb | 0.4363323, 5, 5000, 0.7853982 |
| 0x10 | 0x00bc5930 | 40a00000 | 459c4000 | 00000000 | 000006c9 | 5, 5000, 0, (int 0x6c9) |
| 0x20 | 0x00bc5940 | 00000000 | 43480000 | 00000000 | 3f800000 | **pos = 0, 200, 0, 1** |
| 0x30 | 0x00bc5950 | 80000000 | 80000000 | 3f3504f3 | 3f3504f3 | **q = −0, −0, 0.7071068, 0.7071068** |
| 0x40 | 0x00bc5960 | bf7fffff | 00000000 | 33800000 | 00000000 | −0.9999999, 0, 5.960464e-08, 0 |
| 0x50 | 0x00bc5970 | b3800000 | 00000000 | bf7fffff | 00000000 | −5.960464e-08, 0, −0.9999999, 0 |
| 0x60 | 0x00bc5980 | 00000000 | 3f800000 | 00000000 | 00000000 | 0, 1, 0, 0 |
| 0x70 | 0x00bc5990 | 37480000 | 00000000 | 4347ffff | 3f800000 | 1.192093e-05, 0, 200, 1 |

- In E50's layout, qw 0x40–0x70 is the object matrix out. Its rows are the
  90° rotation (diagonal ≈ 0, off-diagonal ±1) and then a row holding 200
  and 1.
- RAM scan at vsync 5349: **0 hits** for T65 §5c's SC camera qw0 words
  (`bf093f99 00000000 3380419a 33800000`) anywhere in the 32 MiB of EE RAM,
  and **1** (0x3f3504f3, 0x3f3504f3) pair, at 0x00bc5958 (this object). So
  the view×proj block VU1 receives at SC is not stored in EE RAM with those
  exact words at that moment. Scratchpad was not scanned.

## T66-4. Writer table (store watch from the MENU state through settled SC)

| # | GS vsync | via | at (store pc) | cpuRegs.pc | code | ra | q after write |
|---|---|---|---|---|---|---|---|
| 1 | 4174 (K+10) | store (SQ, rt = a0, base s0, +0x30) | **0x15e0d4** | 0x15e0d8 | `7e040030` | 0x15e0bc | 80000000, 80000000, 3f3504f3, 3f3504f3 |

Registers at #1: a0 = 80000000 (low word; the SQ stores the 128-bit a0,
which the q column gives in full), a1 = 00bc5950, a2 = 00000000,
a3 = fffffffb, v0 = 00000000, v1 = 004c53a0, **s0 = 00bc5920**,
s1 = 01fffb00, s2 = 01fffaf0, s3 = 0, s4 = 0, s5 = 00585a24, s6 = 0,
s7 = 00000001, sp = 01fff6a0.

- The census (`t66cen`) has one entry for the whole run (vsync 4174,
  pc 0x15e0d8, n = 1). There were no `t66chg`, `t66f` or `t66v` lines: the
  one store is SQ, not SWC1/SQC2, and there was no later value change.
- **pc convention:** PCSX2's `cpuRegs.pc` at store time is the next
  instruction. `at` is the store's own address, confirmed by
  `memRead32(pc−4) == cpuRegs.code`. Compare `at` = 0x15e0d4 with the
  recomp's store pc.

Disassembly context (`local/tooling/ee/ee-at`, `ee-func`; the code is
identical in both emulators, so this is only for locating the writer):

```
sub_0015E050 (0x15e050..0x15e2a8), a0 -> s0 (object), a1 -> s2, a2 -> s1
  0x15e074  jal func_176D68            (a0 = sp: work struct)
  0x15e084  lq v1, 0(s1) ; 0x15e08c lq v0, 0(s2)
  0x15e094  sq v1, 0x20(sp) ; sq v0, 0x40(sp) ; swc1 f20(=1.0) -> 0x4c(sp), 0x2c(sp)
  0x15e0a0  jal func_166640            (a0 = sp, a1 = 1)
  0x15e0a8  jal func_166F90            (a0 = sp)
  0x15e0b4  jal func_1673A0            (a0 = sp+0x390, a1 = sp)
  0x15e0bc  lq v0, 0x390(sp) ; 0x15e0c4 lq a0, 0x3a0(sp)
  0x15e0d0  sq v0, 0x20(s0)            (pos)
  0x15e0d4  sq a0, 0x30(s0)            (quaternion)  <- the write
  0x15e0dc..  lqc2 vf1-4 from 0x4c53a0 ; sqc2 -> 0x40(s0)...
sub_001673A0 (size 0x58): lq a2, 0x60(a1) ; sq a2, 0(a0) ; lq v1, 0x70(a1) ; sq v1, 0x10(a0)
```

So the stored quaternion is `sp+0x70` of the work struct. That struct is
filled from the two input vectors `*a2` (→ sp+0x20) and `*a1` (→ sp+0x40),
w = 1.0, and then processed by `func_166640(sp, 1)` and `func_166F90(sp)`.
Not traced further. I haven't read those two routines, and the input-vector
values (at 0x01fffb00 and 0x01fffaf0 on the caller's stack) were not logged.

## T66-5. Gaps

1. The watch starts at the MENU statefile, so writes before that state
   (boot → MENU) are not covered. From the state onward the census is
   complete: one write.
2. The input vectors to `sub_0015E050` (`*a1`, `*a2`) and the work struct
   after `func_166640`/`func_166F90` are not logged. Logging them needs a
   second build, which is outside this brief's budget. I did not use the
   second capture.
3. The RAM scan covered EE main RAM only (not scratchpad) and used exact
   word matches.

## T66-6. Exact commands

Via `run.sh` (scp to `C:/Users/bradr/t66stage/`, then
`ssh bytesize "wsl -d Ubuntu -- bash …"`, foreground):
`t66-apply-build.sh` (stash, `python3 t66-hook.py`,
`cmake --build … --target pcsx2-qt pcsx2-gsrunner -j2`: 1 TU + 2 links) →
`t66-replay.sh` → `t66-cap.sh` (generated from `T64/t64-cap.sh` by `gencap.py`;
changes marked T66: only `/tmp/t48-arm` touched, T52 marks at K and settled,
`/tmp/t66-dump` in place of `/tmp/t59-dump`, then a wait for `t66obj_done`) →
`t66-extract.sh t66a`. Disassembly: `local/tooling/ee/ee-at 0x15e0d4 40 8`,
`ee-func 0x15e0d4`, `ee-at 0x1673a0 0 400`.

## T66-7. Receipts

In this dir: `REPORT.md`, `t66-patch.diff`, `t66-hook.py`, `t66-apply-build.sh`,
`t66-replay.sh`, `t66-cap.sh`, `gencap.py`, `t66-extract.sh`, `run.sh`,
`t66a-trace.txt` (all t66 lines + marks), `t66a-poll.log`,
`t66a-paths-first.txt`, `t66a-shot-sc.png`. On bytesize: `pre-t66/`, the T66
binaries in the tree, the `dat-t57` emulog, and `pcsx2-t4/t66a-*` snaps.

Recommended next action (the orchestrator decides): E50 Part 2 compares its
recomp writer against `sq a0, 0x30(s0)` @ 0x15e0d4 (K+10, a single write).
If the recomp writes the same pc with (0, 0, 0.52736, 0.94813), the
divergence is inside `func_166640`/`func_166F90` on the work struct, or in
their inputs `*a1`/`*a2`. A T67 can log the work struct at 0x15e0a8 and
0x15e0b0, plus the two input qwords, for a side-by-side comparison
(1 build, 1 capture).
