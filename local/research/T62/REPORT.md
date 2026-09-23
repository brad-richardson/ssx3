# T62 REPORT — PCSX2: who produces 0x1b0 after the SC input

Brief `local/muse/prompts/T62.md`. Tables + receipts; the orchestrator decides.
Read first: `local/research/T61/REPORT.md`.

## T62-0. Mission table

| # | Mission | Result |
| --- | --- | --- |
| 1 | 3 appender copy sites (`appx`: count=v1, t0, tw0..4), exact-`0x1b0` store watch (`v1b0`), appsum + per-site counts; emits only vsync ≥ 1025 | DONE — 2 TUs, hook first try, b1 clean |
| 2 | Builds ≤1 (+1) | DONE — 1/1 |
| 3 | Preservation (G13 replay 7/7 + HWSTAT) | DONE, zero hook lines |
| 4 | One capture `t58-pre-sc-state` → K → SC settled | DONE — 1/2 captures (t62a) |
| 5 | Item-0 writer at SC + tw0; first `v1b0` producers; preservation | DONE (§T62-4) |
| 6 | Receipts + `[T62]` commit, no push | DONE (this file + dir) |

Headline for the orchestrator: **there are two templates, not a rearm.**
The SC copy sites (`0x37ad44`, `0x37b474`, ra `0x37a958`) read a
*different* template at **`0x61c910` whose tw0 is already `0x1b0`** from
their first post-window execution (vsync 1065 = K+106). Item 0 at SC is
written by **`0x37ad44` (count=1 ⇔ item 0 post-increment) at K+106,
tw0=`0x1b0`**. The `v1b0` watch (200 hits, vsync 1025–1030) caught **only
pointer stores whose low 10 bits are `0x1b0`** (heap/list addresses) —
**zero writes to either template**: the SC template's `0x1b0` predates the
window (static image data, pre-K EE fill, or DMA — §T62-6.4). Register map
(v1=count, $8=t0) verified by `axfirst` insurance rows at all 3 sites.

## T62-1. Pins

| Pin | Value |
| --- | --- |
| PCSX2 tree | `9056c08349cc29ad02a6d1a3a4133259019195af` (= T61 base); only Interpreter.cpp + R5900OpcodeImpl.cpp modified (Vif_Transfer M = T61's, untouched by T62) |
| T62 binaries SHAs | qt `6c4365eab29065fc7a1b7d5ff29d864c4fc7b5d0ad7bddc4f043f5a30e7ce12e`, gsrunner `8c1e3f4fa662ef3db151f10ef15c691aac5a85b1410caa228812c056352f780e` |
| Patch | `t62-patch.diff` 45,396 B sha256 `15b1c8c5f41e6c6506cd01e96e03bb3c02d6554c2667c961cbfe7681673880ea` (2 TUs vs HEAD; carries pre-T62 context — only t62 hunks are T62's) |
| Inputs | ISO; `dat-t57` (EE+VU0 interp); pre-SC state `t58-pre-sc-state` |
| Capture (t62a) | K-down ≈ vsync 959 (`PATHS_AT_START`; `T51C_WINDOW` @958), K-up ≈ 1034; window ≥ 1025 = K+66 (opens in the last ~0.2 s of the K hold); SC try1 0.44, SETTLED 0.60, LOADED 1.53/39; F8 `t62a-shot-sc.png`; PATHS 959–2613; trace `t62-trace.txt` 2,053,331 B sha256 `310297ca45a9c30a7393fa8b16032836051b1ed3ee4505981a614a0cc204225b` |
| Poll | `t62a-poll.log`: appx 300 (cap), axfirst 6, v1b0 200 (cap), T62_CAPAX 1, T62_CAPV 0, app/tpl 200/200, ebw 512, ebwend 1 |

Builds 1/1, captures 1/2, ~1 h wall of 2 h, bytesize ≈ 150 MB new of
2 GB (capture emulog 123 MB + rotation + snaps + stage).

## T62-2. The patch

`t62-hook.py` (validate-all-then-write; all anchors first try), 2 TUs:

- Interpreter.cpp: T62 block *before* `t60_check` (single insertion point;
  `void t61_app_account(u32);` forward decl covers the later T61
  definition — the T61-fix2 pattern). `t62_ax(site)` on every execution of
  the 3 sites: v1=GPR3, t0=GPR8, tw via memRead32, ra=GPR31; always updates
  template globals + per-site census (site≠0 also feeds
  `t61_app_account`, so **n_app/hist are redefined to all-sites**);
  emits only ≥1025: `axfirst` (first 2/site, wide regs — register-map
  insurance, ≤6 rows, outside the 300 budget) + `appx` (count≤1 or
  mode==6, cap 300, `T62_CAPAX` once). `t62_store_v1b0` (external linkage):
  per-32-bit-lane scan of every RAM-foldable EE store (all widths
  1/2/4/8/16 via the single `t58_store_watch` choke point, post-write so
  lane reads are new values); hit = `(v&0x3FF)==0x1b0` anywhere, or
  template-target `[t0p,t0p+20)` with mode 6; `v1b0` rows with 14 regs
  (T60-tpl layout), cap 200 (`T62_CAPV` once). Scope: RAM mirrors only
  (same `t58_phys` fold as T58/T60/T61); DMA/SIF (no pc) out of scope.
- R5900OpcodeImpl.cpp: prototype + one call line after `t60_store_tpl`
  (global scope). Vif_Transfer untouched.
- `appsum` format += `ax=ax0,ax1,ax2` (per-site execs since last emit;
  reset inside the emit — safe: emits are exactly one per vsync and the
  counter is single-threaded, §T62-5.3).

Line formats (extract grammar, 1 known reject §T62-6.5):
`appx vsync site count t0 tw0..tw4 ra`;
`axfirst vsync site v1 t0 tw0 tw1 tw2 s0 a0 ra`;
`v1b0 vsync addr vaddr value pc ra a0..a3 v0 v1 s0..s7`;
`appsum vsync n_app n_tpl mode_hist ax=a,b,c`.

## T62-3. Preservation

G13 replay on the T62 gsrunner: **7/7 PNG md5s match the T48 pins
exactly**, HWSTAT exact (791/37/0/14/320/6), hook-line count 0 (all
T60/T61/T62 families absent).

## T62-4. Tables (capture t62a; K = K-down = vsync 959)

Register-map proof (`axfirst`, all 6 rows observed):

| vsync | site | v1 | t0 | tw0 | tw1 | ra |
| --- | --- | --- | --- | --- | --- | --- |
| 1025 | 0x3797ec ×2 | 1, 2 | 0x61c8fc | 0xc | 0x1414294 | 0x379780 |
| 1065 | 0x37ad44 ×2 | 1, 2 | 0x61c910 | 0x1b0 | 0x814884/0xb5c616 | 0x37a958 |
| 1065 | 0x37b474 ×2 | 4, 6 | 0x61c910 | 0x1b0 | 0x814884 | 0x37a958 |

v1 behaves as a small item index and $8 holds the template at all 3
sites — the brief's codegen read VERIFIED empirically (s0 differs:
site-0 varies, SC sites constant `0x61ba60`).

Table 1 — appx (300 rows, `T62_CAPAX` @1088):

| site | n | vsync span | counts | t0 | tw0 |
| --- | --- | --- | --- | --- | --- |
| 0x3797ec | 40 | 1025–1064 (K+66…105) | always 1 | 0x61c8fc | 0xc |
| 0x37ad44 | 166 | 1065–1088 (K+106…129) | 1–11 | 0x61c910 | 0x1b0 |
| 0x37b474 | 94 | 1065–1088 | 4–9 | 0x61c910 | 0x1b0 |

260/300 rows are mode 6 (all SC-site rows). **Item 0 at SC: site
`0x37ad44`, count=1, vsync 1065 (K+106), t0=`0x61c910`, tw0=`0x1b0`,
ra=`0x37a958`.** No count=0 rows exist anywhere (v1 is post-increment:
item 0 ⇔ v1=1, matching the "ldl after the count increment" note). The
two SC sites interleave one count sequence 1–11 per vsync (ad44:
1,2,3,5,7,10,11; b474: 4,6,8,9 — two item types sharing a list).
End state confirms the copy: `ebwend vsync=2290 b0=0x1b0 0x814884 …
b1=0x1b0 0xb5c616 …` — the settled w1 words equal the SC template's.

Table 2 — first `v1b0` producers (all K+66 = vsync 1025; 44 distinct pcs
total, 200 rows over vsync 1025–1030, then capped):

| K+ | pc | ra | addr | value |
| --- | --- | --- | --- | --- |
| 66 | 0x379ad4 | 0x379ac8 | 0x621460 | 0x623db0 |
| 66 | 0x379b60 | 0x379ac8 | 0x809b88 | 0x623db0 |
| 66 | 0x37a198 | 0x3a3b5c | 0x621460 | 0x62bdb0 |
| 66 | 0x37a220 | 0x3a3b5c | 0x80be08 | 0x62bdb0 |
| 66 | 0x3629b0 | 0x363138 | 0x860ab8 | 0x623db0 |

First-row regs (0x379ad4): a0=1 a1=1 a2=0x110 a3=0x8095f0 v0=0x623db0
v1=2 s4=0x61ba60. Per-pc top totals: 0x379ad4/0x379b60 ×24, 0x3629b0 ×21.
Values are all heap/list **pointers** with low10=`0x1b0` (top:
`0x5129b0` ×12, `0x623db0`/`0x6269b0`/`0x62bdb0`/… ×9); one small value
(`0x5b0` @ K+71). **Template-target rows: 0** — no write to
`[0x61c910,+20)` or `[0x61c8fc,+20)` in-window.

Table 3 — appsum validation (accounting proof, not just census):
pre-12 lines: n_app==ax0 exactly (ax1=ax2=0); vsync 12 is the T60-cap
transition (n_app=14, ax=22,0,0 — cap hit mid-vsync); **all 2619 post-12
lines: n_app==ax1+ax2 exactly, zero mismatches**. Totals: ax0=86,077
(all site-0 execs, uncapped) ax1=10,962 ax2=6,264 n_app=17,504; and
17,504−10,962−6,264 = **278 = T61's exact site-0 total** — the MENU phase
(appsum lines 0–12, identical values/hists to T61) is deterministic
across runs; T60's app-cap froze site-0 accounting at 278 while site-0
kept executing (~33/vsync to end of run). Hist union: {0:78, 3:200,
6:17,226}. Late-run shape (e.g. 2627–2630): n_app=11 hist=6:11
ax=39,7,4 — site 0 counted in ax but (capped) not in n_app, as designed.

## T62-5. Reading (no verdict)

1. The SC scene does not re-template `0x61c8fc`: it uses a second template
   at `0x61c910` (offset +0x14) whose tw0 is `0x1b0` from first sight.
   Site `0x3797ec` keeps the MENU template through K+105 (count≡1,
   tw0≡0xc — plausibly a header/item-1 rewrite during the K hold).
2. The `v1b0` value-half fires on pointer traffic (addresses ending in
   `0x1b0` are common in the 0x62xxxx/0x6fxxxx heaps); the mode-6 template
   write, if it is an EE store, happened before K+66.
3. The ax/n_app accounting split (T60's early-return vs T62's always-on
   census) reconciles exactly (§T62-4 Table 3) — no hook bug; the
   analyzer's naive equality was wrong, the corrected rule holds 2631/2632
   with the cap-transition line explained.

## T62-6. Gaps, overruns

1. Builds 1/1, captures 1/2, ~1 h, ≈ 150 MB of 2 GB. No overruns.
2. `t62-patch.diff` carries pre-T62 context hunks (file-scoped diff);
   only the t62 hunks are T62's.
3. Both T62 caps hit fast: appx 300 by vsync 1088 (K+129), v1b0 200 by
   vsync 1030 (K+71) — post-cap producers of both kinds unobserved.
4. The ≥1025 gate = K+66: the K-down…K+65 span (K hold + release ≈ 1034)
   is unlogged for appx/v1b0. The SC template's `0x1b0` predates first
   observation — its producer (pre-window EE, DMA, or static image data)
   is still open; a MIN≈K rerun would close it.
5. Extract rejects = 1: bare `apc vsync=2289` (zero-store vsync; grammar
   needs ≥1 pc — T61 §T61-6.4 class). No dump-duplicate this run
   (apc==appsum==2632).
6. T60's `app`/`tpl` hooks ran unchanged (200/200, caps @12/100 —
   deterministic); their formats are byte-identical to T61.

## T62-7. Exact commands

Bytesize over foreground `ssh bytesize` + `wsl -d Ubuntu` (outer
double-quotes; NO shell pipes inside the remote string; staged files
under `C:/Users/bradr/t62stage/`): probes (store-watch choke point =
post-write for all widths 1/2/4/8/16; execI pattern; `t60_phys` name) →
`t62-hook.py` (validate-all-then-write; all anchors first try) →
`t62-build.sh` (same cmake line; b1 clean, 2 TUs + 2 links) →
`t62-replay.sh` (G13 7/7 + HWSTAT + zero T62-family lines) → `t62-cap.sh`
(`TAG=t62a`, PATHS bounds, K→SC leg ×1, settled re-ident, `/tmp/t59-dump`
+ F8 + LOADED) → extract (`t62-extract.sh`, new appx/axfirst/v1b0/extended
...[truncated 911 chars]