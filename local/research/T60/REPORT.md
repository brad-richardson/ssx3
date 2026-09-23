# T60 REPORT — PCSX2: who sets mode 6 in the render-state template (append trace + template watch)

Brief `local/muse/prompts/T60.md`. Tables + receipts; the orchestrator decides.
Read first: `local/research/T59/REPORT.md`.

## T60-0. Mission table

| # | Mission | Result |
| --- | --- | --- |
| 1 | `app` trace at every EE pc `0x3797ec` + dynamic template watch (tw0/tw1 changes), same formats for E44 | DONE — 2 TUs, all anchors first try |
| 2 | Builds ≤2 | DONE — 1/1 (b1 clean: 2 TUs + 2 links) |
| 3 | Preservation (G13 replay 7/7 + HWSTAT) | DONE, zero hook lines |
| 4 | One capture `t58-pre-sc-state` → K → SC settled (T59 cap script) | DONE — 1/2 captures |
| 5 | app table (40 rows + counts), tpl-before-first-append + setters, preservation | DONE (§T60-4) |
| 6 | Receipts + `[T60]` commit, no push | DONE (this file + dir) |

Headline for the orchestrator: **the template (`t0=0x61c8fc`, never moves)
churns through the same 10-write cycle every vsync — tw0:
`0xcc→(0x1a2618)→0x0→(0x397fc4)→0xc→(0x379c28)→0xcc`; tw1 through six
values back to `0x1414294` (setters §T60-4 Table 2) — and the appends at
`0x3797ec` sample it: counts 1–6 get tw0=`0xc`, counts 37+ get tw0=`0xcc`.
No `0x1b0` appears in 300 tpl rows: the mode-6 template value is set
post-cap (same story as T59's w0 evolution). Structural findings: ra is
constant `0x379780` (true caller, outside `0x379784–0x379820` — not
clobbered); two lists alternate per vsync (s4 arenas `0x6efd00` /
`0x623080`, double-buffered); lists restart at count=1, never 0; counts
7–36 and 50–53 have no app rows (30+4 appends per list via other paths —
E44 must cover all appenders, not just `0x3797ec`).**

## T60-1. Pins

| Pin | Value |
| --- | --- |
| PCSX2 tree | `9056c08349cc29ad02a6d1a3a4133259019195af`; base = T59-end working tree + T60 hook below |
| T60 binaries SHAs | qt `c1a058dee7b438f123c38a4339abc5ab97c427c0badaa5731e2d0eedf28d2be7`, gsrunner `0ac5b3f907bf788b4bdb58b8b85364ba20312d8ff71e52411ea25baf261718b6` |
| Patch | `t60-patch.diff` 36,279 B sha256 `e404bd934394f4a3616cbf88880014f75c9f1d30b5ca522961085b08cbaf8580` (RI + Interpreter vs HEAD; carries T55/T56/T58/T59 context — only the t60 hunks are T60's) |
| Inputs | ISO; `dat-t57` (EE+VU0 interp); pre-SC state `t58-pre-sc-state` |
| Capture (t60a) | K→SC-ident ~17 s; SC try1 0.50, SETTLED 0.64, LOADED 1.54/39; F8 `t60a-shot-sc.png` (Zoe); PATHS 0–2614; trace `t60-trace.txt` 618,594 B sha256 `6b8e48a5ec136927c943a67a5df2b66c1147814c4063ce047442d2df3188ac93` |
| Poll | `t60a-poll.log`: app 300, tpl 300, tplrearm 0, T60_CAP 2, ebw 512, ebwend 1, ebwlast 244, vu0call 0, vif0op 0, LOADED in-band |

Builds 1/1, captures 1/2, ~40 min wall of 2 h, bytesize ≈ 250 MB new of
2 GB (capture emulog 120 MB + rotation + snaps + stage).

## T60-2. The patch

`t60-hook.py` (validate-all-then-write, idempotent; anchors first try),
2 TUs (`Interpreter.cpp`, `R5900OpcodeImpl.cpp`):

- `execI` (next to T55's pc checks, standalone `if` — no T55 interaction):
  `if (pc == 0x3797ec) t60_app();` (×1 anchor on the T55 mark line).
- T60 core at global scope in Interpreter.cpp (needs no new includes:
  g_t48_vsync/memRead32/Console/cpuRegs all visible): `t60_app()` (cap
  300, `T60_CAPAPP` once; count=`memRead32(a3)`, t0=GPR8, tw[5] via
  memRead32, s4=GPR20, t1=GPR9, ra=GPR31 raw; then `t60_arm(t0)`),
  `t60_arm` (fold copy of T59's; shadow tw[5]; re-arm + `tplrearm` line on
  t0 change, sharing the 300 tpl budget), `t60_check` (tw0/tw1 change →
  `tpl` with old/new + 14 regs a0..a3 v0 v1 s0..s7 (E44 format),
  `T60_CAPTPL` once), `t60_store_tpl` / `t60_dma_tpl` (range overlap vs
  [t0p,t0p+20); values via memRead32 / byte-assembled host).
- RI: global decls + one call line in each of `t58_store_watch` /
  `t58_dma_watch` (×1 anchors each; T58 lesson: global scope both ends).

Line formats (grammars checked, 0 rejects; for E44 Part 4):
`app vsync count t0 tw0 tw1 tw2 tw3 tw4 s4 t1 ra`;
`tpl vsync addr old new pc ra a0..a3 v0 v1 s0..s7`;
`tplrearm vsync old new`; `T60_CAPAPP/T60_CAPTPL vsync`.

## T60-3. Preservation

G13 replay on the T60 gsrunner: **7/7 PNG md5s match the T48 pins
exactly**, HWSTAT exact (791/37/0/14/320/6), hook-line count 0 (all
T60/T58/T57 families absent).

## T60-4. Tables (capture t60a)

app vsync span 0–13 (300 rows, capped); tpl span 0–30 (300 rows, capped);
t0 constant `0x61c8fc` (tplrearm 0); ra constant `0x379780` (outside
`0x379784–0x379820`: the brief's caller claim VERIFIED, not clobbered).

Table 1 — app first 40: counts 1–6 (tw0=`0xc`, s4/t1 advancing ~0xE0–0x1A0
per item) then 37–49, 54–56 (tw0=`0xcc`); full rows in
`t60-analyze.py` output / `t60-trace.txt:1–40`. Counts observed: 22
distinct (1–6, 37–49, 54–56), min 1 max 56. **No count=0 append exists**;
lists restart at count=1 (app# 0,22,44,… — 14 restarts, alternating s4
arenas `0x6efd00`/`0x623080`: two lists, double-buffered per vsync).

Table 2 — tpl setter pc→ra per new mode value (×30 each in-window):

| word | new | setter pc | ra |
| --- | --- | --- | --- |
| tw0 | 0x0 | 0x1a2618 | 0x1a25dc |
| tw0 | 0xc | 0x397fc4 | 0x397fc4 (=pc, as observed) |
| tw0 | 0xcc | 0x379c28 | 0x3a3b5c |
| tw1 | 0xb00294 | 0x1a2614 / 0x397e2c | 0x1a25dc / 0x1a274c |
| tw1 | 0xb0d294 | 0x1a26d0 | 0x1a25dc |
| tw1 | 0xf00294 | 0x397f58 | 0x397f14 |
| tw1 | 0x1700294 | 0x397f78 | 0x397f14 |
| tw1 | 0x1400294 | 0x397f88 | 0x397f14 |
| tw1 | 0x1414294 | 0x397f9c | 0x397f14 |

Per-vsync steady cycle (identical every vsync 0–30): tw1
`0x1414294→0xb00294→0xb0d294→0xb00294→0xf00294→0x1700294→0x1400294→0x1414294`
while tw0 goes `0xcc→0x0→0xc→0xcc`. **No `0x1b0` in 300 tpl rows**
(searched) — the mode-6 template set happens post-cap.

Table 3 — tpl before list restarts: the cycle is periodic, so the sequence
before EVERY count=1 is the same 10-row pattern (shown for restart #22 in
analyzer output). Appends sample it: early-list (counts 1–6) see tw0=`0xc`,
late-list (37+) see tw0=`0xcc`.

Missing counts 7–36 + 50–53 (34 appends/list with no app row): same-vsyc
hook live (neighboring counts logged), so these append via other pcs
(different item-type appenders sharing the header) or batched count bumps
— E44's trace must cover all appenders. The s4 advance across the gap
(`0x6f05e0`→`0x6f27a0`, ≈279 B/item × 31) is consistent with 31 real items.

End state (kept machinery): `ebwend vsync=2272 b0=0x1b0 … b1=0x1b0 …`;
vu0call/vif0op still 0 under interp.

## T60-5. Reading (no verdict)

- tw0 sampled by the append is `0xc`/`0xcc` in-window; `0x1b0` (and
  w1/w3's settled values) arrive post-cap — same shape as T59.
- The `0x379c28` setter (tw0=`0xcc`, ra `0x3a3b5c`) sits one function over
  from the `0x3797xx` appender — near-neighbor code worth E44's look.
- `t60_phys` fold copy in Interpreter.cpp duplicates T59's (pure function,
  no state split); template t0 is kuseg-low so any fold agrees.

## T60-6. Gaps, overruns

1. Builds 1/1, captures 1/2, ~40 min, ≈ 250 MB of 2 GB. No overruns.
2. `t60-patch.diff` carries T55/T56/T58/T59 context hunks (file-scoped
   diff); only the t60 hunks are T60's.
3. Both caps hit (app 300 by vsync 13, tpl 300 by vsync 30): post-cap
   template/appends unobserved, including any `0x1b0` template set.
4. `tplrearm` (my addition for E44 parity) never fired (t0 constant) —
   format reserved, zero rows.
5. Count-gap mechanism (other appenders vs batched bumps) unresolved —
   needs a pc census over `0x379784–0x379820` or item-stride watch;
   flagged for E44, not this brief.
6. ra=`0x397fc4` on the tw0=`0xc` setter rows equals its pc (leaf/jump
   idiom?) — reported as-is.

## T60-7. Exact commands

Bytesize over foreground `ssh bytesize` + `wsl -d Ubuntu` (outer
double-quotes; staged files under `t60stage/`): probes (interp loop =
`execI`, T55 pc-check pattern) → `t60-hook.py` (validate-all-then-write;
all anchors first try) → `t60-build.sh` (`cmake --build …/build --target
pcsx2-qt pcsx2-gsrunner -j2`; b1 clean) → `t60-replay.sh` (G13 7/7 +
HWSTAT + zero lines) → `t60-cap.sh` (`TAG=t60a`, `t58-pre-sc-state`,
PATHS bounds, K→SC leg vs `t29-ref-sc` ×3, settled re-ident,
`/tmp/t59-dump` + 5 s, F8 + LOADED) → extract (`t60-extract.sh` grammar
incl. app/tpl/tplrearm, 0 rejects) + analyze (`t60-analyze.py` + one
Table-3 revision re-staged/re-run, no new capture) → scp home.
`git log -1` checked before commit (main @ `a9dce3a` + prior lanes).

## T60-8. Receipts

Repo (this commit): `local/research/T60/` — REPORT.md, `t60-patch.diff`
(36,279 B), `t60-hook.py`, `t60-build.sh`, `t60-replay.sh`, `t60-cap.sh`,
`t60-extract.sh`, `t60-analyze.py` (final, incl. Table-3 revision),
`t60-trace.txt` (sha §T60-1), `t60a-poll.log`, F8 `t60a-shot-sc.png`.
(Probes 1–2 were read-only loop reads superseded by §T60-2.) Bytesize
residue under cap: `t60stage/`, capture emulog (120 MB) + rotation,
snaps, both binaries (§T60-1).
