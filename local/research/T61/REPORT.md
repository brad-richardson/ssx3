# T61 REPORT — PCSX2: mode-6 template setter hunt (value-filtered rerun of T60)

Brief `local/muse/prompts/T61.md`. Tables + receipts; the orchestrator decides.
Read first: `local/research/T60/REPORT.md`.

## T61-0. Mission table

| # | Mission | Result |
| --- | --- | --- |
| 1 | Value filter (`new`/sampled tw0 `& 0x3C0 != 0`, tw0/tw1 snapshots on tpl) + appsum + apc censuses, same tree/rules as T60 | DONE — 3 TUs, hook first try, one ordering fix |
| 2 | Builds ≤1 (+1 on compile fail) | DONE — b1 failed (2 use-before-decl), b2 clean |
| 3 | Preservation (G13 replay 7/7 + HWSTAT) | DONE, zero hook lines |
| 4 | One capture `t58-pre-sc-state` → K → SC settled | DONE — 1/2 captures (t61a) |
| 5 | Mode-6 setter table, per-vsync mode histogram around SC, appender-pc census | DONE (§T61-4; setter table is EMPTY — null result) |
| 6 | Receipts + `[T61]` commit, no push | DONE (this file + dir) |

Headline for the orchestrator: **no mode-6 template set exists anywhere in
the capture.** All 200 filtered tpl rows are 2 shapes only (tw0 `0xc→0xcc`
@ `0x379c28`, tw1 `→0xb00294` @ `0x1a2614`); all 200 app rows sample
tw0=`0xcc`; the 2725-line appsum census sees only modes 0 and 3
(78 + 200 of 278 executions); exact `0x1b0` appears NOWHERE in app/tpl
words (end state still settles `b0=b1=0x1b0` post-cap, same as T59/T60).
The append activity sits entirely pre-K (vsync 0–12, ~47 s before K-down);
post-K the `0x3797ec` path never executes. The apc census answers T60's
open gap: **43 distinct appender pcs in 6 unrolled runs** write the item
area — the steady pair (`0x379804`-run header writes + `0x379b48`-run bulk
writes, vsync 0–2724) plus a MENU-only run (`0x37a208`, ends 1035, just
after K-down ≈1025) and three SC-scene runs (`0x37b48c/0x37ad5c/0x37b4ac`,
onset 1111, just after K-up ≈1106). E44's trace must cover all six runs,
not just `0x3797ec`.

## T61-1. Pins

| Pin | Value |
| --- | --- |
| PCSX2 tree | `9056c08349cc29ad02a6d1a3a4133259019195af` (= T60 base); repo root `pcsx2-g7/pcsx2`; only the 3 TUs modified |
| T61 binaries SHAs | qt `a9fcd424f63502c02c06b313c753271efe627a64a37c1169f38d8138bf8ee82e`, gsrunner `74a8054688893fcb3d0681fb182660ef4fe396065ed02a952f83dc343d064342` |
| Patch | `t61-patch.diff` 41,662 B sha256 `c175a7f2ca98c85128f6d462d6d209ec8612d8f57680ba045047135645bbca1d` (3 TUs vs HEAD; carries T55/T56/T58/T59/T60 context — only the t61 hunks are T61's) |
| Inputs | ISO; `dat-t57` (EE+VU0 interp); pre-SC state `t58-pre-sc-state` |
| Capture (t61a) | K-down ≈ vsync 1025, K-up ≈ 1106; SC try1 0.59, SETTLED 0.51, LOADED 1.58/41; F8 `t61a-shot-sc.png`; PATHS 1024–2708; trace `t61-trace.txt` 1,993,296 B sha256 `fcf71c6943489384022588c3896f559eb18cac60331e78e0ed4c1b4f3730796a` |
| Poll | `t61a-poll.log`: app 200, tpl 200, tplrearm 0, T60_CAP 2, T61_CAPSUM 0, ebw 512, ebwend 1, ebwlast 240, vu0call/vif0op 0 |

Builds 2/2 (b1 compile-fail + b2 clean), captures 1/2, ~1.5 h wall of
2 h, bytesize ≈ 250 MB new of 2 GB (capture emulog 126 MB + rotation +
snaps + stage).

## T61-2. The patch

`t61-hook.py` (validate-all-then-write; all anchors first try), 3 TUs:

- Interpreter.cpp: T61_SUM block (value filter on both emit paths, tw0/tw1
  post-write snapshots on tpl, `t61_app_account` on every `0x3797ec`
  execution, `appsum` flush on vsync change, `t61_flush_all` dump tail);
  caps 200/200 (`T60_CAPAPP/T60_CAPTPL` names kept), appsum cap 3000
  (`T61_CAPSUM` once).
- R5900OpcodeImpl.cpp: T61_APC block (4096-pc census over
  `[0x809670,0x80B670)` = brief §3's `[0x8095f0+0x80,+0x80*64)`; pc-sorted
  `apc` flush per vsync) + record line in `t58_store_watch` + dump-tail
  call in `t59_maybe_dump`.
- Vif_Transfer.cpp: `t61_vsync_tick()` prototype + per-VIF1-packet call
  (the tick path that converges with the app/store paths).

`t61-fix2.py` (b1 → b2): b1 failed with 2 use-before-decl errors —
`g_t61_sum_tpl` (tpl-watch code precedes the SUM block) and
`t61_flush_all` (dump call precedes the APC block). Fix hoists the appsum
counters above `t60_check` and moves the `t61_flush_all` prototype to file
scope above `t59_maybe_dump` (global scope — namespaces start at RI:744).
Same fix2 also repaired a real applier bug it exposed: the
`("\tg_t60_napp++;","",1)`-style cleanup ate the moved-up `t60_arm(t0);`
(first occurrence), leaving arming post-filter; fix2 restores the arm
before the mode filter and drops the trailing double-arm (exactly one
`\tt60_arm(t0);` verified). b2: 3 TUs + 2 links clean.

Line formats (extract grammar, 2 known rejects §T61-6.3):
`app` = T60 format (unchanged);
`tpl` = T60 + `tw0= tw1=` post-write snapshots;
`appsum vsync n_app n_tpl mode_hist=m:count,…|-`;
`apc vsync pc=0x…:count,…` (pc-sorted).

## T61-3. Preservation

G13 replay on the T61 gsrunner: **7/7 PNG md5s match the T48 pins
exactly** (`b7a3e8db a7929218 bb8b1d85 817e934f ×2 85cf3599 ×2`),
HWSTAT exact (791/37/0/14/320/6), hook-line count 0 (all
T60/T61/T58/T57 families absent).

## T61-4. Tables (capture t61a)

K/SC mapping (emulog-ts ↔ vsync via `T48_PATHS`; `kmap2-t61.sh`):
K-down ≈ **vsync 1025** (`T51C_WINDOW` sits at 1023; `PATHS_AT_START=1024`
at K−15 ms), K-up ≈ **1106** (2 s hold @ ~40/s), SC-first-ident ≈
**vsync 1868**, kill @ 2724. All "relative to K" below use K-down = 1025.

Table 1 — mode-6 setters (pc, ra, regs, first vsync rel. K): **EMPTY.**
Zero tpl rows with `new&0x3C0==0x180` (of 200); zero app rows with
tw0 `&0x180==0x180` (of 200); exact `0x1b0` in NO app tw word and NO tpl
old/new/tw0/tw1 word (searched). The mode-6 template set is post-cap
(T59's w0 story holds for the template too).

Table 2 — filtered app (200 rows, vsync 0–12 = K−1025…K−1013, all pre-K):
t0 constant `0x61c8fc`, ra constant `0x379780`, tw0 always `0xcc`
(mode 3 — the filter admits it; `0xc` rows of T60 are the 78 filtered).
Counts 37–49, 54–56 (16 distinct; 1–36/50–53 absent — same gap as T60,
now explained by Table 4). s4 arenas alternate per vsync
(`0x6f…` even / `0x625…` odd — double-buffered). First 3 rows:

| vsync | count | tw0 | tw1 | s4 |
| --- | --- | --- | --- | --- |
| 0 | 37 | 0xcc | 0x1414294 | 0x6f27a0 |
| 0 | 38 | 0xcc | 0x1414294 | 0x6f2ae0 |
| 0 | 39 | 0xcc | 0x1414294 | 0x6f2dc0 |

Per-vsync app counts: 18,14,16×10,8 (cap `T60_CAPAPP` at vsync 12).

Table 3 — filtered tpl (200 rows, vsync 0–100): exactly 2 shapes,
periodic 2/vsync (vsync 1: 0 rows — template static; vsync 0: 3 rows —
startup transient, the `0xc→0xcc` transition fires twice as the state
loads mid-cycle; cap `T60_CAPTPL` at vsync 100):

| n | addr | old → new | tw0/tw1 snapshots | setter pc / ra |
| --- | --- | --- | --- | --- |
| 100 | 0x61c8fc | 0xc → 0xcc | 0xcc / 0x1414294 | 0x379c28 / 0x3a3b5c |
| 100 | 0x61c900 | 0x1414294 → 0xb00294 | 0xcc / 0xb00294 | 0x1a2614 / 0x1a25dc |

All other T60 transitions (`0xcc→0x0`, `0x0→0xc`, remaining tw1 steps)
are shadow-tracked, unemitted, by design.

Table 4 — appender-pc census (43 distinct pcs, 6 straight-line runs —
equal totals per pc within a run = one store per pc per iteration;
4-byte gaps at `0x379b5c`, `0x37ad74`, `0x37b4a0` are non-store slots):

| run | pcs | per-pc total | vsync first–last |
| --- | --- | --- | --- |
| 0x379804–0x379824 | 9 | 54,019 | 0–2724 (header/item writes; ebw sees 804 = tw0-slot `0xc`, 808 = tw1-slot, ra `0x379780`) |
| 0x379b48–0x379b6c | 9 | 93,303 | 0–2724 (bulk writes) |
| 0x37a208–0x37a228 | 9 | 9,324 | 0–1035 (MENU-only; ends ~10 vsyncs after K-down) |
| 0x37b48c–0x37b4a8 | 7 | 6,456 | 1111–2724 (SC-scene) |
| 0x37ad5c–0x37ad78 | 7 | 11,298 | 1111–2724 (SC-scene) |
| 0x37b4ac–0x37b4b0 | 2 | 17,754 | 1111–2724 (SC-scene; onset ~5 vsyncs after K-up) |

The two always-on runs are T60's missing counts 7–36 mechanism (bulk
appends via other pcs in the `0x3797xx` family, same ra `0x379780`).

Table 5 — mode histogram: active window (the ONLY n_app>0 vsyncs;
278 executions = 200 emitted + 78 filtered — sums check):

| vsync | n_app | n_tpl | mode_hist |
| --- | --- | --- | --- |
| 0 | 30 | 3 | 0:12,3:18 |
| 1 | 14 | 0 | 3:14 |
| 2–11 | 22 | 2 | 0:6,3:16 (each) |
| 12 | 14 | 2 | 0:6,3:8 |

Union over the whole capture: modes {0:78, 3:200} — no other mode ever
sampled at `0x3797ec`. Around SC entry (1863–1873, ±5 of 1868): every
vsync `n_app=0 n_tpl=0 mode_hist=-` (in fact ALL vsyncs 13–2724 are zero —
post-K the `0x3797ec` path never executes).

End state: `ebwend vsync=2375 b0=0x1b0 … b1=0x1b0 …` (T60: same values @
2272 — gate timing only).

## T61-5. Reading (no verdict)

- The value filter works as specified (78 mode-0 executions suppressed,
  shadow still tracks: skipped rows' old/new equal their snapshots by
  construction; `T61_CAPSUM` never fired — 2725 < 3000).
- The `0x3797ec` append path is MENU-idle-only; the SC scene build
  (post-K) writes the same item area through the Table-4 runs while
  `0x3797ec` stays silent — E44 must trace all six runs.
- `0x379c28` (tw0=`0xcc` setter, ra `0x3a3b5c`) and the `0x3798xx` writer
  family sit within ~1 KB of the appender — near-neighbor code, same note
  as T60's.
- `t60_phys`-style fold: apc reuses T59's `t58_phys` in place (no new
  fold; kuseg-low area so any fold agrees — T60 §T60-5 note still holds).

## T61-6. Gaps, overruns

1. Builds 2/2 (b1 compile-fail + b2 clean), captures 1/2, ~1.5 h,
   ≈ 250 MB of 2 GB. No overruns.
2. `t61-patch.diff` carries pre-T61 context hunks (file-scoped diff);
   only the t61 hunks are T61's.
3. Both caps hit (app 200 by vsync 12, tpl 200 by vsync 100): post-cap
   template/appends unobserved except via the uncapped censuses
   (appsum/apc run to 2724/2724 by design).
4. Extract grammar rejects = 2, both bare `apc vsync=` lines (1074 —
   vsync with zero item-area stores; 2374-bare — see 5). Grammar needs
   ≥1 pc; the lines are correct output, not data errors.
5. `apc vsync=2374` appears twice (full then bare): dump-tail ordering —
   `t61_flush_all` emits 2374-full, then the same store's `t61_apc_tick`
   re-emits 2374-empty before rolling to 2375. Benign duplicate
   (explains apc = appsum + 1); census content complete in the full line.
6. `T51C_WINDOW vsync=1023` (a T51-lane marker) lands ~1 vsync before
   K-down — reported as position only; its semantics belong to T51.
7. Mode-6 setter table empty by measurement, not by filter design: the
   filter admits any `&0x3C0 != 0` (modes 1–7, 9–15 all pass) and the
   uncapped appsum hist independently confirms only modes 0/3 occur.

## T61-7. Exact commands

Bytesize over foreground `ssh bytesize` + `wsl -d Ubuntu` (outer
double-quotes; NO shell pipes inside the remote string — cmd.exe mangles
them; loop-free single commands or staged scripts under
`C:/Users/bradr/t61stage/`): `t61-hook.py` (validate-all-then-write) →
`s
...[truncated 1352 chars]