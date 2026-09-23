# T64 REPORT — PCSX2: catching the 0x1b0 write into template 2

Brief `local/muse/prompts/T64.md`. Tables + receipts; the orchestrator decides.
Read first: `local/research/T63/REPORT.md`.

## T64-0. Mission table

| # | Mission | Result |
| --- | --- | --- |
| 1 | w0-only churn-excluded `tw` (new ∉ {0,c,cc}) + 8 pre-pc words, cap 200; uncapped per-vsync `t2`; drop other tw emission, keep shadows | DONE — Interpreter.cpp only, hook first try, b1 clean |
| 2 | Builds ≤1 (+1) | DONE — 1/1 |
| 3 | Preservation (G13 replay 7/7 + HWSTAT) | DONE, zero hook lines |
| 4 | One capture `t63-menu-state` → K → SC settled | DONE — 1/2 captures (t64a) |
| 5 | First non-churn writer (K-relative, pc/ra/regs/pre-words); `t2` table around the change | DONE (§T64-4) |
| 6 | Receipts + `[T64]` commit, no push | DONE (this file + dir) |

Headline for the orchestrator: **caught, with full provenance.** At vsync
1015 (**K+85**, K-down ≈ 930) a two-store staging pair fires, 10×/vsync
through the cap (1015–1024): `0x396b98` writes `0x180` (`ori v0,v0,0x180`
immediate, then `sw v0,0(v1)` with v1=`0x61c910`), then `0x37a6fc` loads
it back (`lw v0,0(a0)`, a0=`0x61c910` = `lw a0,0xe84(s0)` per the pre-word
precedent), ORs `0x30` (`ori v0,v0,0x30` immediate) and stores **`0x1b0`**
(`sw v0,0(a0)`). So `0x1b0 = 0x180 | 0x30`, both bits from **immediate
`ori`s, composed through the template word itself** (read-modify-write);
no load of the value, no DMA. The word does not settle — it is staged per
event and cleared after (t2 last-value stays `0xc`; the SC copies sample
the transient). SC copies ignite K+95, one vsync after the pairs begin.

## T64-1. Pins

| Pin | Value |
| --- | --- |
| PCSX2 tree | `9056c08349cc29ad02a6d1a3a4133259019195af` (= T63 base); only Interpreter.cpp modified by T64 (RI/Vif M = earlier lanes) |
| T64 binaries SHAs | qt `626be79691b318211206c85f60cc79879d5a3405559d81558042ea05df12360f`, gsrunner `ecb13c0f732fc8f6a2bef1f8ee940cd051350c61bc0d287c44525f63517a2725` |
| Patch | `t64-patch.diff` 50,703 B sha256 `051d3edb7f88cc81e35227c5d7f6a772698ea12c6209b3cf2c5b1b0fb168cd71` (2 TUs vs HEAD; carries pre-T64 context — only t64 hunks are T64's) |
| Inputs | ISO; `dat-t57` (EE+VU0 interp); `t63-menu-state` (T63 run 1) |
| Capture (t64a) | K-down ≈ vsync 930 (`PATHS_AT_START`; `T51C_WINDOW` @929); SC try1 0.59, SETTLED 0.52, LOADED 1.51/37; F8 `t64a-shot-sc.png`; PATHS 930–2608; trace `t64-trace.txt` 2,358,430 B sha256 `be82aa9b58cf795c1d0968fd30103897eee0f8f67c63b80d56e69fb6fb7c9cb6` |
| Poll | `t64a-poll.log`: tw 200 (cap, `T64_CAPTW` 1), t2 2557 (uncapped), appx 300 (192+108, site-0 zero rows), axfirst 6, v1b0 200, T63_CAPTW 0 |

Builds 1/1, captures 1/2, ~40 min wall of 1.5 h, bytesize ≈ 150 MB new
of 1.5 GB (capture emulog 120 MB + rotation + snaps + stage).

## T64-2. The patch

`t64-hook.py` (validate-all-then-write, 11 anchors first try), small
surgical replaces on T63's block, RI untouched:

- Cap decls → T64 state (w0 cap 200 + t2 rollover state: vs/last/n/32 pcs).
- Both fn-top guards → uncapped + `t64_roll(v)` (superset: DMA path too).
- Both loop bodies → shadows always update; w0 counted (`t64_note`),
  non-w0 silent, churn (`0/c/cc`/unchanged) skipped.
- Both cap guards → T64 w0 cap; tails use the hoisted old.
- `tw` format/args += 8 pre-pc words (`memRead32(pc-32..pc-4)`).
- `t61_flush_all` += `t64_flush()` (one line; trailing partial covered).
- t2 line: `t2 vsync w0 last n pcs` (`,`-joined, `-` when empty); rollover
  on every store-watch call (stores occur every vsync — verified: t2 has
  every vsync 0..2555; one writeless vsync 2219 doubles with the
  dump-flush, benign T61-class duplicate) + dump flush.

## T64-3. Preservation

G13 replay on the T64 gsrunner: **7/7 PNG md5s match the T48 pins
exactly**, HWSTAT exact (791/37/0/14/320/6), hook-line count 0 (all
families incl. `t2`/T64 absent).

## T64-4. Tables (K = K-down = vsync 930)

Table 1 — first non-churn writer (full rows):

| # | vsync | old → new | via | pc / ra |
| --- | --- | --- | --- | --- |
| 1 | 1015 (K+85) | 0x0 → 0x180 | st4 | 0x396b98 / 0x37a6a8 |
| 2 | 1015 (K+85) | 0x180 → 0x1b0 | st4 | 0x37a6fc / 0x37a6bc |

Regs #1: a0=`3fffffff` a1=`ffffffc3f` a2=`c0000000` a3=`01000101`
v0=`00000180` v1=`0061c910` s0=s2=`61ba60`. Regs #2: a0=a1=`0061c910`
a2=`00069db0` a3=`00ee7280` v0=`000001b0` v1=`00000604` s0=s2=`61ba60`
s1=`00ee72e0` s4=`00ee86a8`. Later rows alternate ra `0x37a6a8`/`0x37a6bc`
for `0x37a6fc` (two call paths); `0x396b98` ra always `0x37a6a8`. Totals:
100× `0x180` @`0x396b98` + 100× `0x1b0` @`0x37a6fc`, 20/vsync @1015–1024
(cap), all st4, no DMA.

Table 2 — pre-pc words (raw, oldest first) with certain decodes (each
corroborated by row regs/values; MIPS EE):

Row #1 (`0x396b98`): `34e70007, 00073c38, 34e70100, 00073c38, 34e70101,
34420180, 25ab6bb0, ac620000`.
Row #2 (`0x37a6fc`): `00021080, 02021021, 8c4310b0, a4a30012, 8e040e84,
8c820000, 34420030, ac820000`.
Decoded: `34420180` = `ori v0,v0,0x180`; `ac620000` = `sw v0,0(v1)`
(v1=`0x61c910`); `8e040e84` = `lw a0,0xe84(s0)` (the brief's
`*(s0+0xE84)` template pointer, a0=`0x61c910`); `8c820000` = `lw v0,0(a0)`;
`34420030` = `ori v0,v0,0x30`; `ac820000` = `sw v0,0(a0)`.
Caveat: each window's last word duplicates a store opcode (unrolled
neighbor at pc−4); pc attribution is per the T60-verified `cpuRegs.pc`
convention (±1 instruction).

Table 3 — `t2` around the change (n = all w0 writes incl. invisible
churn resets; pcs truncated):

| vsync | w0(last) | n | pcs |
| --- | --- | --- | --- |
| ≤1014 | 0xc | 425 | 5 churn pcs |
| 1015–1024 | 0xc | 476 | +`0x37a678,0x37a67c,0x396b98,0x37a6fc,0x37aaa8,0x37a9f0` (+31 invisible resets: 20 visible + 31 churn-clear per vsync) |
| 1025+ | 0xc | 476 | same set (pairs continue past the tw cap — t2 counts what tw can't emit) |

SC copies (appx) ignite @1025 (K+95: first SC row count=1 tw0=`0x1b0`);
site 0 emits zero appx rows this run (axfirst v1=12,13 tw0=`0xc` — gate
correctly passes nothing; MENU-phase variation vs T62's count≡1).
`T62_CAPAX` @1052 (K+122). t2 spans 0..2555 + flush (2557 lines).

## T64-5. Reading (no verdict)

- Value source: **immediates** (`ori 0x180`, `ori 0x30`), sequenced
  store → load → store through w0 itself. Not a loaded constant, not DMA.
- w0 is a staging word, not a latch: set (0→180→1b0) → sampled by the
  copies → cleared, ~10 events/vsync from K+85 while SC builds. The
  "stable 0x1b0" of T62's appx is sampling-phase luck (copies run inside
  the transient); end-of-vsync rest is `0xc`.
- The pair rate (10/vsync) matches list granularity; the two ra's at
  `0x37a6fc` suggest two staging call sites.

## T64-6. Gaps, overruns

1. Builds 1/1, captures 1/2, ~40 min, ≈ 150 MB of 1.5 GB. No overruns.
2. `t64-patch.diff` carries pre-T64 context hunks (file-scoped diff);
   only the t64 hunks are T64's.
3. The tw cap (200) covers 1015–1024; post-cap pairs are counted (t2 n)
   but their pcs/values past 1024 come only from the t2 pc sets (values
   unseen — all post-1024 pairs assumed same shape by pc identity).
4. pc attribution ±1 instruction (unrolled-neighbor note, Table 2).
5. Run-to-run K varies (930 vs 959/1017) with MENU-phase consequences
   (site-0 counts 12,13 here vs 1 in T62) — K-relative alignment holds
   (pairs K+85, copies K+95, cap K+122 vs T62's onset K+105).
6. Extract rejects = 1 bare-`apc` (2219, also the t2 flush-duplicate
   vsync — same benign class).

## T64-7. Exact commands

Bytesize over foreground `ssh bytesize` + `wsl -d Ubuntu` (outer
double-quotes; no shell pipes inside the remote string; staged files
under `C:/Users/bradr/t64stage/`): `t64-hook.py` (11 anchors, all first
try; two pre-fixes: pre-word order, no-unused-var) → `t64-build.sh`
(same cmake line; b1 clean — Interpreter.cpp only) → `t64-replay.sh`
(G13 7/7 + HWSTAT + zero t2/T64 lines) → `t64-cap.sh` (t63-run2 shape,
TAG=t64a, `t63-menu-state`, PATHS bounds, K→SC leg ×1, settled re-ident,
`/tmp/t59-dump` + F8 + LOADED) → extract (`t64-extract.sh`: tw+pre, t2,
T64_CAP grammars) → analyze (`t64
...[truncated 583 chars]