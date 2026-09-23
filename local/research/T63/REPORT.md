# T63 REPORT — PCSX2: who writes SC template 2 at 0x61c910 (w0 = 0x1b0)?

Brief `local/muse/prompts/T63.md`. Tables + receipts; the orchestrator decides.
Read first: `local/research/T62/REPORT.md`.

## T63-0. Mission table

| # | Mission | Result |
| --- | --- | --- |
| 1 | Change-only watch on template array `[0x61c8fc,0x61c94c)` (20 words) over all EE store widths + T58 DMA paths, boot baseline, 2000 lines total; keep T62 appx/axfirst | DONE — 2 TUs, hook first try, b1 clean |
| 2 | Builds ≤1 (+1) | DONE — 1/1 |
| 3 | Preservation (G13 replay 7/7 + HWSTAT) | DONE, zero hook lines |
| 4 | Run 1: cold boot → MENU → F1 fresh state | DONE (t63r1; state `t63-menu-state` 6.4 MB) |
| 5 | Run 2: fresh state → K → SC settled | DONE (t63r2, no fallback needed) |
| 6 | Template-2 w0–w4 history; first 0x1b0 writer; value source; preservation | DONE (§T63-4; writer bounded, not row-caught) |
| 7 | Receipts + `[T63]` commit, no push | DONE (this file + dir) |

Headline for the orchestrator: **the 0x1b0 fill was not row-caught, but it
is now cornered.** Template array is runtime-filled BSS (all-zero at boot
baseline). Run 1 (boot→MENU) shows the init (0xffff fills + w1/w2 seeds at
vsync 1021) and never touches template-2 w0 (virgin 0 through the 2000-cap
at vsync 1282). The fresh MENU state has template-2 =
`{w0:0xc, w1:0x1414294, w2:0x1c0, w3:0, w4:0xffff0613}`. Run 2 watches w0
churn `0xc↔0xcc` (881 rows, writers `0x3798d8`/`0x379ba0`/`0x399674`) until
its cap dies at vsync 6 — and the first `0x1b0` sample lands at vsync 1121
(K+104, same vsync the SC copy sites and SC appender runs ignite). So the
money write sits in **run-2 vsync (6,1121] = (K−1011,K+104]**, via EE store
(DMA excluded: 0 DMA rows to the array in 4000 watched writes) and not via
any post-1025 exact-`0x1b0` store (v1b0 value-half clean) — i.e. an
ordinary `sw/sd` in the blind span, plausibly the same churn family taking
a scene-setup value. The churn writers carry the value in a register
(`v0`); immediate-vs-load is an offline decode at those pcs.

## T63-1. Pins

| Pin | Value |
| --- | --- |
| PCSX2 tree | `9056c08349cc29ad02a6d1a3a4133259019195af` (= T62 base); Interpreter.cpp + R5900OpcodeImpl.cpp modified (Vif_Transfer M = T61's) |
| T63 binaries SHAs | qt `e1873b590169560740a6e7b4a04e91bffc7e8ba0612511f9350bf791d4ebf071`, gsrunner `32b7392b935a799485616c3dfa21a25c8ed70ef2dde9620758d7d27b6ca13a8f` |
| Patch | `t63-patch.diff` 48,837 B sha256 `dbf82ebe0646f4d9864564783764acbfd7fb979ec2fe5281883c37381c25e529` (2 TUs vs HEAD; carries pre-T63 context — only t63 hunks are T63's) |
| Inputs | ISO; `dat-t57` (EE+VU0 interp) |
| Run 1 (t63r1) | Cold `-slowboot -turbo` boot → title poll1 → MENU first try → F1; state `t63-menu-state` sha256 `6d1d7237bb2a0b35c8b7e459aa4f347abf23f1f1ad509586a86980164af53fab`; emulog 469 MB sha `1fdcf8e6…`; trace `t63r1-trace.txt` 3,263,591 B sha256 `943a4d5463e56eff2aa4b8b08d588fbc08850e2ec8b4e408c35d2dea9a157679` |
| Run 2 (t63r2) | Fresh state → K-down ≈ vsync 1017 (`PATHS_AT_START`; `T51C_WINDOW` @1016) → SC try1 0.43, SETTLED 0.61, LOADED 1.59/45; F8 `t63r2-shot-sc.png`; trace `t63r2-trace.txt` 2,602,301 B sha256 `fcf4e6c8373e2ae5fc8bd6fb72407cfb1898d6291d5d183beed728c573ef07b1` |

Builds 1/1, runs 2/2, ~1.5 h wall of 2.5 h, bytesize ≈ 650 MB new of
3 GB (run-1 emulog 469 MB + run-2 emulog 126 MB + traces/states/snaps).

## T63-2. The patch

`t63-hook.py` (validate-all-then-write; all anchors first try — the execI
`pc` anchor needed one revision: 3 occurrences, re-anchored on T62's site
line), 2 TUs:

- Interpreter.cpp: T63 block before `t60_check` (no T61/T62 deps — the
  range is a static phys constant, no fold needed): 20-word shadow +
  `t63_baseline()` (one-shot first-execI snapshot — precedes all stores —
  plus a 20-row `twbase` receipt, a deliberate separate line kind outside
  the 2000 cap) + `t63_store_tw` / `t63_dma_tw` (T60's overlap/read
  patterns: post-write `memRead32` lanes for stores, host-assembled bytes
  for DMA) + shared `t63_emit`. Change-only; shared 2000-line cap
  (`T63_CAPTW`); `via` = `st1/st2/st4/st8/st16` or the DMA channel string.
  execI: one baseline line. T62's appx/axfirst/v1b0/censuses untouched.
- R5900OpcodeImpl.cpp: 2 prototypes + call in `t58_store_watch` + call in
  `t58_dma_watch` (via passed through). DMA coverage = exactly T58's five
  call sites: SPR-from, SIF0, SIF2/dma-ch7, IPU/dma-ch3 (all EE-RAM DMA
  writers; VIF/GIF don't target EE RAM, SIF1 reads).
- Backdoor caveat (by design): ELF-loader/host-side writes bypass both
  hooks; run-1's `old=0x0` first rows are consistent with zero-filled RAM
  (BSS semantics) with no intervening backdoor write required.

Line formats (extract grammar; run-1 rejects ≈900 bare-`apc` boot lines,
run-2 rejects 1 — known T61 class):
`tw vsync addr vaddr old new via pc ra a0..a3 v0 v1 s0..s7`;
`twbase vsync addr value`; `T63_CAPTW vsync` (unfired both runs — the fill
landed exactly on call boundaries; cap enforced by count at 2000).

## T63-3. Preservation

G13 replay on the T63 gsrunner: **7/7 PNG md5s match the T48 pins
exactly**, HWSTAT exact (791/37/0/14/320/6), hook-line count 0 (all
families incl. `tw`/`twbase`/T63 absent).

## T63-4. Tables

Template index: t1=`0x61c8fc` t2=`0x61c910` t3=`0x61c924` t4=`0x61c938`
(w0 = mode word; w3 is zero everywhere, likely padding).

Table 1 — run 1 (boot→MENU, ~7800 vsyncs): twbase 20×`0x0`; tw 2000 rows
@1021–1282; per-template {t1:1990, t2:4, t3:4, t4:2}. Init @1021:
`0x36927c`/`0x3692bc` st2 double-fill of w4 slots → `0xffffffff`
(t1w4,t2w4,t3w4,t4w4); `0x369534/0x36953c/0x369540` st8 seeds
w1=`0xb00294` w2=`0x80` on t1+t2 (+t3, 4 rows). Then a `0x232xxx` fill loop
(8 pcs ×248 = 1984 rows: st4/st8/st2) pounds template 1 to the cap @1282
(tail: tw1 `0xb00294→0x1300294→0x1000294` @`0x2320cc/0x2320dc`,
ra `0x23204c` — pointer values). **Template-2 w0: zero rows (virgin 0).**
Template-2 range total: 4 rows (w4 ×2, w1, w2 — init only).

Table 2 — run 2 baseline (fresh MENU state @vsync 0): t1 =
`{cc,1414294,2a0,0,ffff0613}`, t2 = **`{c,1414294,1c0,0,ffff0613}`**,
t3 = `{0,b00294,80,0,ffffffff}`, t4 = `{0,0,0,0,ffffffff}`. So run-1's
blind span (1283–F1) filled t2w0=`0xc`, t2w2 `0x80→0x1c0`, w4
`ffffffff→ffff0613` (writers unobserved — cap).

Table 3 — run 2 (tw 2000 rows @0–6; per-template {t2:1748, t1:252}):
template-2 w0 churns `0xc↔0xcc`, 881 rows, values never anything else —
first (0: `0xc→0xcc` st4 @`0x3798d8`, ra `0x3996e0`), last (6: `0xc→0xcc`
st8 @`0x399674`, ra `0x3991d0`); writers `0x3798d8` (140) / `0x379ba0`
(440, →`0xc`) / `0x399674`+`0x39967c`+`0x3996cc` (st8/st4, →`0xcc`) +
tail (`0x398ae8` st2, `0x3a3af4`, …). Template-2 w2 churns
`{0x1c0,0x2a0,0x240}` (same pcs); w1 (`0x1414294`) and w3 (0) stable.
**`new=0x1b0` rows: 0 (both runs, any address).**

Table 4 — the bound. Last w0 sighting: `0xcc` @run-2 vsync 6. First
`0x1b0` sample: appx @1121 (K+104; T62 reproduced K+105) — the same vsync
SC copy sites start, site 0 stops (1119/1120→1121 one-vsync handoff),
SC apc runs ignite (0x37b48c first @1121; MENU writer 0x37a208 last
@1028), `T62_CAPAX` @1139. **Money write ∈ run-2 vsync (6,1121] =
(K−1011,K+104].** Exclusions: (i) no DMA to the array, ever (0/4000 rows
both runs); (ii) run-1 w0 untouched [1021–1282]; (iii) run-2 w0 last
`0xcc` @6; (iv) v1b0 exact-value half clean over [1025–1029] (0 rows
`value=0x1b0`; template-half caveat: it follows appx t0 = template 1
until 1121, so only the value-half covers template 2 there).

Table 5 — value source. DMA excluded (above). Churn writes carry the value
in a register: st4 @`0x3798d8`/`0x379ba0` → `v0` (0xcc/0x0c rows show
`v0` = new); st8 @`0x399674` → `v0` low half. Whether `v0` is filled by an
immediate (`ori`/`addiu`) or a load (and from which address) is an offline
decode at those three pcs + their ra frames — the rows carry full regs
for it. The init fills carry constants (`0xffff` halfwords,
`0xb00294`/`0x80` — plausibly immediates, same decode). The 0x1b0 write
has no row; by mechanism parity with the churn writers (same word, same
hot pcs) an `sw`/`sd` of a register is the standing hypothesis.

## T63-5. Reading (no verdict)

- The array is BSS filled at runtime in three waves: zero → @1021 init
  (-1 fills + w1/w2 seeds, templates start as copies) → blind-span MENU
  values → run-2 MENU churn (c↔cc on t1w0/t2w0; w2 orbiting) → the 0x1b0
  mode-set (one-shot, stable through SC: appx samples it uniformly
  1121–1139+, ebwend `b0=b1=0x1b0`).
- w3 is never written anywhere (20/20 zero at both baselines) — padding
  or an unwritten slot; w4 goes `-1 → ffff0613` in the blind span.
- The SC handoff is a single-vsync event (1120→1121) across three
  independent hooks (appx sites, apc runs) — the scene build starts
  K+104, not at K-down.

## T63-6. Gaps, overruns

1. Builds 1/1, runs 2/2, ~1.5 h, ≈ 650 MB of 3 GB. No overruns. No
   fallback needed (fresh state saved first try).
2. `t63-patch.diff` carries pre-T63 context hunks (file-scoped diff);
   only the t63 hunks are T63's.
3. Both tw caps died on high-frequency writers (run-1: 0x232xxx fill
   @1282; run-2: MENU churn @6, ~285 rows/vsync) — blind spans
   run-1 (1283–F1) and run-2 (7–end). The bound in Table 4 is robust to
   this (baseline + first-sample sandwich), but the money row itself is
   inside run-2's blind span.
4. T62's ≥1025 gates/caps behaved identically on the fresh state
   (appx 300, CAPAX@1139; v1b0 200 @1025–1029; site spans match T62 ±1) —
   the fresh MENU state reproduces t58-pre-sc-state dynamics.
5. v1b0's template-half watches whichever template appx touched last
   (template 1 until 1121) — for template-2-only coverage it is weaker
   than the value-half; stated in Table 4(iv).
6. Run-1 rejects ≈900 bare-`apc` (BIOS/loader vsyncs with no item stores
   — expected new class for a boot run, same grammar cause).

## T63-7. Exact commands

Bytesize over foreground `ssh bytesize` + `wsl -d Ubuntu` (outer
double-quotes; no shell pipes inside the remote string; staged files
under `C:/Users/bradr/t63stage/`): DMA-coverage probe (t58_dma_watch =
SPR/SIF0/SIF2/IPU only) → `t63-hook.py` (validate-all-then-write; one
anchor revision: execI `pc` ×3 → T62 site line) → `t63-build.sh` (same
cmake line; b1 clean) → `t63-replay.sh` (G13 7/7 + HWSTAT + zero
tw/twbase/T63 lines) → `t63-run1.sh` (T58 run-3 int shape, TAG/paths
retagged, state → `t63-menu-state`, emulog pinned with tw/twbase/cap
counts + sha) → extract (`t63-extract.sh` with explicit paths,
`s
...[truncated 807 chars]