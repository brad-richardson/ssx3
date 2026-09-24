# E55D8 — real save/login menu route (read-only inventory)

Worker: opencode (Muse Spark Contributor Go). Brief: `local/muse/prompts/E55D8.md`.
Read-only: no fork/source edit, build, boot, device/card action, push, or
status/todo/ledger edit. Write scope: this REPORT + `check.py` + bounded text
receipts in this dir only. The orchestrator judges the gate.

Prior context: `local/research/E55D7/{REPORT.md,ORCH-GATE.md}` (three static
callers feed the save-manager cluster; string labels prove no on-screen
route), `local/research/E55D6/{REPORT.md,ORCH-GATE.md}` (Flow A seeded-title
vs Flow B save-menu detour; both `unknown` route/tick), and
`local/research/I26/ROUTES.md` (I26-FAST spine, race HUD tick ~1714).

Outcome: **C** — only names/handlers (`cFEStateLogin`, `Title_SaveProfile`,
`title_Save Replay`, `option_savereplay`, `BASLUS-20772`); no observed
save/login screen and no evidenced button transition anywhere in the
inventoried captures, route logs, or input scripts.

## 1. Evidence index (bounded: 15 files read, 2 EE xref chains, 0 boots)

Each row names an existing receipt with full SHA256 and a tick/sequence
citation. `check.py` re-verifies existence, SHA, and citation.

| # | Receipt (repo path) | SHA256 | Tick/seq citation | What it shows |
| --- | --- | --- | --- | --- |
| E1 | `local/research/I26/ROUTES.md` | `ea19733a5edf5270ba2239f604ab14c613bba6f5919658d53969fb47816e2ddd` | Steps 0-10, ticks 636-1709; Main Menu press tick 766; Rival card ~1640, race HUD 1714 | I26-FAST spine: 9 menu screens + Loading + Rival card + race. No save/login/options screen, no down-into-Options transition |
| E2 | `local/research/I26/make_route.py` | `fd1d0ed7bbd5170fd5de2126a9ed88287be083c028b84eb8096f5b918cff0da4` | `v2()`/`v5()` entries with per-screen comments (Main Menu: Single Event … My Rules: Continue, Rival card) | Input script uses only start/cross/down. No triangle/options press, no save-menu detour exists in any v1-v5 route |
| E3 | `local/research/I26/logs/padscript-i26v5.txt` | `538d6de623d3087995dca92722b8add11140bcf3768a6f9e34df4f0be068c9b5` | 31 presses i=0..30: i=0 start, cross `0x4000`, down `0x0040`; i=30 down 30 s | Executed I26-FAST buttons match E2. No save/options input was ever driven |
| E4 | `local/research/I26/logs/screens-i26v5.txt` | `8be11f46777eb8219fa9ec8d13e110184e31feb40941b8ab5919749e63d9b4ea` | Frame-hash changes at ticks 264, 653-697, 773-793, 897-913, 996-1015, 1351-1465, 1583-1627, race 1714 | Tick backbone of the I26-FAST screens; no frame is annotated as a save/login screen |
| E5 | `local/research/I26/REPORT.md` | `532c6a00187f41e21821afeb80de71d55cf40075ca031fd19fd9abe7e421c5fa` | Settle table: Title ~570, Main Menu 708, Select Character 802, Setup Character 926, Select Peak 1015, Select Mode 1110, Select Event 1189, My Rules 1371, Rival 1636, race HUD 1714 | Visible screen text per tick for the whole spine; no save/login/profile prompt on the empty-card route |
| E6 | `local/research/E58/REPORT.md` | `9a17a15848a1510661eda9021592f1523e5ab64ebeb6964174f3bfead00972bc` | Viewed `sc_b-tick837.png`, `sc_c-tick873.png` (Select Character, Zoe drawn); `race1-tick1811.png` clock 00:00:01; `race2-tick1948.png` clock 00:00:03; runner SHA `f3de8d2c…77896` | Current folded-build capture (I26-FAST, `PS2X_SKIP_MOVIE=1`): same screen spine, no save/login screen viewed |
| E7 | `local/research/E55D7/REPORT.md` | `d86c1ce9d11670b201810995c68412e9a051873a5ca542b8e7cb9032046fbe0f` | §1 B1-B16 static chain; §2 H-A (`cFEStateLogin`) / H-B (`option_savereplay`) forward jal NONE; §3 C1/C2 screen/input `unknown` | Three callers reach the card cluster, but no menu-to-cluster edge; UI strings are names only |
| E8 | `local/research/E55D6/REPORT.md` | `047b4543e1f70c0b3c7c6f9f21f923c4357bac6c40d6aaf0cdc38cb606db81d8` | §1 #1 zero getdir/mcread through tick 2055; §2 Flow A/B route/tick `unknown` | Baseline (empty-card I26-FAST never calls) + the two hypothesis flows this part was asked to ground in observed screens |
| E9 | `local/research/E55D5/REPORT.md` | (cited, SHA not re-read in this part) | §1 full B route: only start/cross/down + one square at 33517 ms (tick ~2009, Rival-card window) | The sole non-I26-FAST button ever driven (square) is a card-tap discrimination pulse, not a menu detour |

No videos exist under `local/research/` (glob `**/*.{mp4,mov,avi,mkv}`: no
files found). `local/research/I26/shots/` holds 6 stills (title, Select Mode
before/after, virtual controls, race t13); all viewed-by-report as menu/race
frames, none a save/login screen. No other input script under
`local/research/` drives anything but the I26-FAST spine or the E55D5
single-square pulse.

## 2. Observed screen table (every screen with a receipt; save row explicit)

| Step | Visible screen text | Receipt (frame/log/input) | SHA (prefix) | Tick/seq | Buttons from receipt |
| --- | --- | --- | --- | --- | --- |
| S0 | Title "Press START button" | E1 + E5 | `ea19733a…`, `532c6a00…` | settles ~570, press tick 636 | start (E3 i=0) |
| S1 | Main Menu: Single Event | E1 + E2 (`v2()` comment) + E5 | `ea19733a…`, `fd1d0ed7…`, `532c6a00…` | settles 708, press tick 766 | cross (E3 i=1) |
| S2 | Select Character: Zoe | E5 + E6 (viewed ticks 837/873) | `532c6a00…`, `9a17a158…` | settles 802, press 884 | cross (E3 i=2) |
| S3 | Setup Character: Continue | E1 + E5 | `ea19733a…`, `532c6a00…` | settles 926, press 993 | cross (E3 i=3) |
| S4 | Select Peak: Peak 1 | E1 + E5 | `ea19733a…`, `532c6a00…` | settles 1015, press 1099 | cross (E3 i=4) |
| S5 | Select Mode: Race | E1 + E5 + I26 shots before/after crop | `ea19733a…`, `532c6a00…` | settles 1110, press 1185 | cross (E3 i=5) |
| S6 | Select Event: Snow Jam → Metro-City → Happiness | E1 + E5 | `ea19733a…`, `532c6a00…` | settles 1189, downs 1271/1301, cross 1337 | down, down, cross (E3 i=6,7,8) |
| S7 | My Rules: Continue | E1 + E5 | `ea19733a…`, `532c6a00…` | settles 1371, press 1440 | cross (E3 i=9) |
| S8 | Loading → Rival Challenge card | E1 + E5 | `ea19733a…`, `532c6a00…` | card ~1636-1640, first tap 1709 | 10 cross taps w/ down released (E3 i=10..29) |
| S9 | Race HUD 00:00:00 | E4 (tick 1714) + E5 + E6 (ticks 1810/1811, 1947/1948) | `8be11f46…`, `532c6a00…`, `9a17a158…` | 1714 | down tuck (E3 i=30) |
| SX | Save/login/profile prompt or save-options screen | **none — no observed screen** | **unknown** | **unknown** | **unknown — no evidenced button transition; do not invent one** |

Displayed-save-UI vs card-API-call distinction: S0-S9 are displayed screens
with per-tick receipts; none displays a save UI. The card API calls
(`sceMcGetDir`/`sceMcRead` via the E55D7 §1 chain) have zero probe records on
this spine (E8 §1 #1). Neither side shows a save flow.

## 3. Candidate table (outcome C: screen/input and tick explicitly unknown)

| # | Known chain (all edges E7 §1) | Missing edge | Candidate UI screen/input | I26-FAST tick | Next observation required to produce a route |
| --- | --- | --- | --- | --- | --- |
| C1 | `sub_002C22C8 --(0x2c22e8)--> sub_002C3FA8 --(0x2c3fc0)--> sub_002C4050 --(0x2c41f4)--> sub_002C48C0 <---> sub_002C5570 --(B1–B4)--> {sub_002C4210, sub_002C42B0, sub_002C6848, sub_002C6B78} --(B5–B11)--> sceMcGetDir@0x40a688 / sceMcRead@0x40a090` | Menu→cluster ingress: callers of `sub_001B3F78` / `sub_0023D5A8` / `sub_00265950` are all `unknown` (§4); no button path from S1 Main Menu to any save screen is evidenced | **unknown** — no save/login screen observed; string names (`cFEStateLogin`, `Title_SaveProfile`) are not screens | **unknown** | Settled Main Menu screenshot listing every entry (tick ~708-766) + one-button-at-a-time down-press observations with settled screenshots until an Options/Save entry is displayed, or a title-window screenshot on a seeded card showing a profile prompt. Only then may a detour probe be predeclared |
| C2 | String-anchored UI layer only: H-A `sub_001A9438` (`cFEStateLogin`), H-B `sub_0020D1D8` (`option_savereplay`); forward jal inventories contain **no** card-cluster target (E7 §2) | Handler→cluster edge: no `jal`, no resolved data pointer, no logged `jalr` from either handler (or sole callers `sub_001A97B8` / `sub_001FB588`) into the §1 chain; owners of vtable slots **unknown** | **unknown** — name only, no screen, no input | **unknown** | Same as C1: an observed screenshot of the H-A/H-B screen with its button path from the S0-S1 spine. Continued probe silence + changed card manifest would mean write-only path (OTHER), but that test needs the screen first |

Nearest observed screen: **S1 Main Menu (Single Event), tick 766** (E1/E5).
Missing transition: **any evidenced button sequence leaving S1 toward a
save/options screen** — no down/up/triangle press from S1 exists in any
inventoried input script (E2/E3/E9), and no resulting save screen exists in
any inventoried frame (E4/E5/E6).

## 4. EE xref chains (two of two allowed; indirect jumps marked unknown)

- Chain 1: `ee-xref 0x1B3F78` (E55D7 B16 caller #1 of `sub_002C22C8`) →
  four static callers `0x1a0a14 (sub_001A0720)`, `0x1a9784 (sub_001A9710)`,
  `0x1bf610 (sub_001BF5A8)`, `0x1d52fc (sub_001D5280)`. `ee-label` on
  `0x1A0720`, `0x1B3F78`: **unknown**. None is an evidenced menu handler;
  the `jalr` guard targets inside `sub_002C5570` remain unresolved
  (E55D7 §1). No screen edge.
- Chain 2: `ee-xref 0x23D5A8` (E55D7 B16 caller #2) → sole static caller
  `0x1d5770 (sub_001D5488)`. `ee-label` on `0x1D5488`, `0x23D5A8`:
  **unknown**. Same verdict: no screen edge. (Third caller `sub_00265950`
  left unexamined by the two-chain budget; marked **unknown**.)

Result: the menu→cluster ingress stays **unknown** one level further up.
No chain reaches an S0-S9 screen handler.

## 5. Predeclared outcome

**C** (only names/handlers, no observed screen). Not A (no observed
save/login screen + evidenced button sequence exists), not B (no observed
screen is a save screen — S1 Main Menu shows Single Event only), not OTHER
(no pin/tick mismatch or ambiguous source: pins match E55D4/E55D5).

**No boot in this part** and no runnable detour command is given. A
GetDir/Read status line in a future run would prove reachability only; guest
bytes and changed-card baseline need later work (E55D6 §3 invalidation rule
carries over). Do not repeat I26-FAST empty-card boots: E55D4/D5 already gave
zero GetDir/Read calls there (E8 §1 #1).

## 6. Checker result

`python3 local/research/E55D8/check.py` → **PASS** (outcome C; candidate
table has explicit unknown screen/input and tick fields; no runnable detour
command; all 8 evidence SHA + citation checks hold; fabricated unsupported
step correctly rejected). Full output in `check-result.txt`.

## 7. Gaps (stated plainly)

- Main Menu full entry list **unknown**: only the Single Event entry is
  evidenced (E2 comment). Whether an Options/Save entry exists is unobserved.
- Upstream of Chain 1/2 callers unexamined (two-chain budget); every `jalr`
  target **unknown** — absence of a static edge does not refute an indirect
  route (E55D7 §5 carries over).
- Guest query path/pattern, `maxEntries`, `tableAddr`, payload layout:
  **unknown** (E55D6 §4b / E55D7 §5 carry over).
- `sceMcGetInfo@0x40a498` single site and HLE `mcCheck*` gates: untested
  (E55D6 §4c carries over).
- No SHAs re-read beyond §1 prefixes in this part; E9 SHA not re-read
  (cited, marked as such).

## 8. Commands run (read-only; outputs in §1 receipts + `check-result.txt`)

- `ls local/research/E55D8/`, `ls local/research/`, `git log -1` → `46294d58`
- `ls local/research/I26/{shots,logs}`, `ls` work dirs (listings only)
- `ee-xref 0x1B3F78` → 4 static callers; `ee-xref 0x23D5A8` → 1 static caller
- `ee-label {0x1A0720,0x1D5488,0x1B3F78,0x23D5A8}` → all `unknown`
- `sha256sum` on the 8 §1 receipts (prefixes tabled)
- Glob `**/*.{mp4,mov,avi,mkv}` under `local/research/`: no files found
- `python3 local/research/E55D8/check.py` → PASS (receipt `check-result.txt`)
- Committed text ~14 KiB + checker ~6 KiB (< 512 KiB budget); <20 min
  read-only search (15 files read, 2 xref chains, 0 boots).
