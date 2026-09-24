# E55D7 — save-manager ingress and route evidence (read-only)

Worker: opencode (Muse Spark Contributor Go). Brief: `local/muse/prompts/E55D7.md`.
Read-only: no build, boot, device, card mutation, fork/source edit, push, or
status/todo/ledger edit. Write scope: this REPORT plus bounded text receipts
in this dir only. The orchestrator judges the gate.

Prior context: `local/research/E55D6/{REPORT.md,ORCH-GATE.md}`,
`local/research/E55D3/{REPORT.md,ORCH-GATE.md}`, `local/research/I26/ROUTES.md`,
EE tools `local/tooling/ee/` (`ee.py:1-14` usage).

## 1. Proven caller edges (backward from the 0x2C cluster)

All addresses below validated live with `ee-xref` / `ee-at` / `ee-func` /
`ee-label`; full outputs in `xref.txt` / `at.txt`. `ee-label` returns
`unknown` for every game address in this chain (no name invented).

| # | Caller PC (in) | Instruction | Callee | Receipt |
| --- | --- | --- | --- | --- |
| B1 | `0x2c5988` (`sub_002C5570`) | `jal func_2C4210` | `sub_002C4210` (GetDir wrapper) | `at.txt:§5988`; `xref.txt:§4210` (`0x2c5988 jal -> 0x2c4210`) |
| B2 | `0x2c59b4` (`sub_002C5570`) | `jal func_2C42B0` | `sub_002C42B0` (GetDir wrapper) | `at.txt:§59B4`; `xref.txt:§42B0` |
| B3 | `0x2c5e64` (`sub_002C5570`) | `jal func_2C6848` | `sub_002C6848` (GetDir user) | `at.txt:§5E64`; `xref.txt:§6848` |
| B4 | `0x2c5f7c` (`sub_002C5570`) | `jal func_2C6B78` | `sub_002C6B78` (Read user) | `at.txt:§5F7C`; `xref.txt:§6B78` |
| B5 | `0x2c424c` (`sub_002C4210`) | `jal func_40A688` (`sceMcGetDir`; `a2=s1+0x139`, pattern ptr unresolved to any string) | `sceMcGetDir@0x40a688` | `at.txt:§424C`; codegen stub `sub_0040A688_0x40a688.cpp:13` (`sceMcGetDir`) |
| B6 | `0x2c431c` (`sub_002C42B0`) | `jal func_40A688` | `sceMcGetDir@0x40a688` | `at.txt:§431C` |
| B7 | `0x2c6884` (`sub_002C6848`) | `jal func_40A688` (`a2=s1+0x139`, same unresolved pattern) | `sceMcGetDir@0x40a688` | `at.txt:§6884` |
| B8 | `0x2c4f84` / `0x2c5020` (`sub_002C48C0`) | `jal func_40A688` | `sceMcGetDir@0x40a688` | `at.txt:§4F84/§5020`; E55D6-mapped pair, re-verified here |
| B9 | `0x2c4d1c` (`sub_002C48C0`) | `jal func_40A090` (fd/buf from `0x18/0x2C/0x20($s2)`) | `sceMcRead@0x40a090` | `at.txt:§4D1C`; stub `sub_0040A090_0x40a090.cpp:13` (`sceMcRead`) |
| B10 | `0x2c4ee4` (`sub_002C48C0`) | `jal func_40A090` (`a1=0x5376F8`, `a2=0x3C4`) | `sceMcRead@0x40a090` | `at.txt:§4EE4` |
| B11 | `0x2c6b90` (`sub_002C6B78`) | `jal func_40A090` | `sceMcRead@0x40a090` | `at.txt:§6B90` |
| B12 | `0x2c4ec8`, `0x2c4ef8` (`sub_002C48C0`) | `jal func_2C5570` | `sub_002C5570` (state machine; mutual recursion with `sub_002C48C0`) | `at.txt:§4EC8/§4EF8`; `xref.txt:§5570` |
| B13 | `0x2c5ba8` (`sub_002C5570`) | `jal func_2C5570` (self; guarded by table-compare at `0x2c5b9c`) | `sub_002C5570` (loop, not an ingress) | `at.txt:§5BA8` |
| B14 | `0x2c3fc0` (`sub_002C3FA8`) | `jal func_2C4050` (with `lui $v0,0x48 / addiu 0x6F78` vtable-ish store in delay slot) | `sub_002C4050` → (`0x2c41f4`) `jal func_2C48C0` | `at.txt:§3FC0`; `xref.txt:§4050`; codegen `sub_002C4050` targets `0x2c2580 + 0x2c48c0` (`strings.txt:§FWD`) |
| B15 | `0x2c22e8` (`sub_002C22C8`) | `jal func_2C3FA8` (after `jal func_317D70` alloc with `a0=0x1500,a1=0x485FF0,a2=0x100`) | `sub_002C3FA8` | `at.txt:§22E8`; `xref.txt:§3FA8` (sole code caller `0x2c22e8`) |
| B16 | `0x1b3fdc` (`sub_001B3F78+0x64`) / `0x23d5b4` (`sub_0023D5A8+0xc`) / `0x2659a4` (`sub_00265950+0x54`) | `jal func_2C22C8` (all three; labels `unknown`) | `sub_002C22C8` | `xref.txt:§22C8`; `at.txt:§1B3FDC/§23D5B4/§2659A4` |

Gating indirection (marked **unknown**, not edges): every card-wrapper call
in `sub_002C5570` is immediately preceded by the same virtual-dispatch
pattern (`lh $a0,0x248($v1)` / `lw $v0,0x24C($v1)` / `jalr $v0`, e.g.
`at.txt:§5988 lines 0x2c5968-0x2c597c`, `§59B4`, `§5E64`, `§5F7C`). The
`jalr` targets are not resolved by data in this survey. Data word
`0x486f8c (.rodata) == 0x2c4050` (`xref.txt:§4050`) is a pointer-table slot
with no static code xref to the slot itself (`xref.txt:§486F8C`: no refs);
its owner/vtable is **unknown**. `0x2c5c78 (sub_002C5570) jal -> 0x2c4410`
and the ~50 `jal -> 0x2c48c0` sites keep the whole card cluster interior to
itself below B14–B16; no UI caller was found below this layer.

## 2. Forward from string-anchored UI handlers (at most two + BASLUS check)

String file offsets → vaddrs resolved against ELF section headers
(`strings.txt:§VADDR`; ELF SHA prefix `1b49d05c`, `§PINS`); xrefs via
`ee-xref` (lui+addiu pairs); forward jal inventory by scanning each
function's codegen file for `jal func_*` targets in `0x2Cxxxx`/`0x40Axxx`
(`strings.txt:§FWD`).

| Handler (string site) | String xref (concrete) | Forward 2C/40A targets in same function | Verdict |
| --- | --- | --- | --- |
| H-A `sub_001A9438` — `cFEStateLogin` (`0x461ca0`) loaded at `0x1a9478` (`lui $a1,0x46; addiu 0x1CA0`; then `jal func_317D70`) | `xref.txt:§461CA0`: sole code ref `0x1a9478`; owner `sub_001A9438`, caller `0x1a9808 (sub_001A97B8)` | `sub_001A9438`: NONE. Its caller `sub_001A97B8`: NONE | Name only. No call edge to the card cluster. `jalr` at `0x1a9464` + `jal func_1BEE30/1A8A40` are unresolved indirections — **unknown**, not card edges |
| H-B `sub_0020D1D8` — `option_savereplay` (`0x471bf0`) loaded at `0x20ddd4`/`0x20de3c` (`lui $a0,0x47; jal func_317670 / func_39B960`) | `xref.txt:§471BF0`: refs `0x20ddd4, 0x20de3c`; data slot `0x474d54 == 0x20d1d8` with no code xref to the slot (`xref.txt:§474D54`) → possible vtable, owner **unknown** | `sub_0020D1D8`: NONE. Its caller `sub_001FB588`: only `0x2c2540, 0x2c26d0 (fiprintf per ssx3.toml), 0x2c27c0` — string utils, no card target | Name only. No call edge to the card cluster |
| BASLUS check `sub_00241AA0` — `BASLUS-20772` (`0x47c3a8`) as `$a1` in delay slot of `jal func_2C2540` at `0x241ab0` | `xref.txt:§47C3A8`: sole code ref `0x241ab0`; `sub_002C2540` is a byte→halfword string-copy loop (`at.txt:§2540`), callers include the BASLUS callers `sub_001877B0/001D5488/001D58B8` | `sub_00241AA0`: only `0x2c2540`. `sub_001877B0/001D5488/001D58B8`: only `0x2c2540 + 0x2c26d0 (fiprintf)` | String reaches string helpers only. NOT a card edge; inferring GetDir/Read from the folder name is forbidden by the brief and not done |
| Title handlers `sub_001902C0/00190540/00190768` (`Title_SaveProfile@0x45e318`), `sub_001FDBF0/001FE968` (`title_Save Replay@0x470100`) | `xref.txt:§45E318/§470100` | All five: NONE | Names only |

No `Title_SaveProfile`, `title_Save Replay`, `option_savereplay`,
`cFEStateLogin`, or `BASLUS-20772` site yields a `jal` (or a resolved data
pointer) into `sub_002C4050/002C48C0/002C5570/002C6848/002C6B78` or
`sceMc{GetDir,Read}`. The `0x2c2540`/`0x2c26d0` hits are string helpers, not
card logic.

## 3. Candidate table (at most two; no complete route proved)

| # | Known call chain (all edges §1) | Missing edge | Candidate UI screen/input | I26-FAST tick | Exact next observation that distinguishes it |
| --- | --- | --- | --- | --- | --- |
| C1 | `sub_002C22C8 --(0x2c22e8)--> sub_002C3FA8 --(0x2c3fc0)--> sub_002C4050 --(0x2c41f4)--> sub_002C48C0 <---> sub_002C5570 --(B1–B4)--> {sub_002C4210, sub_002C42B0, sub_002C6848, sub_002C6B78} --(B5–B11)--> sceMcGetDir@0x40a688 / sceMcRead@0x40a090` | Menu→cluster ingress: who calls `sub_002C22C8`'s three callers (`sub_001B3F78 / sub_0023D5A8 / sub_00265950`, all `unknown`), what the `0x486f8c==0x2c4050` slot belongs to, and what the `jalr $v0` guards pass. All marked **unknown** | **unknown** — no screen/input is evidenced. Do not use the I26 empty-card setup rule or any string name as a trigger | **unknown** (I26-FAST ticks 570–2055 already show zero `getdir`/`mcread` records on empty card: E55D6 §1 #1; that is the baseline, not a trigger) | First-ever E55D3 `getdir`/`mcread` family record (any status incl. `ok=0 reason=empty\|bad-addr…`, E55D3 G1–G6/R1–R7) at title/login ticks on a seeded-card I26-FAST boot proves reachability. GetInfo-only predicts `[MC] GetInfo` runtime lines with still-zero probe lines; HLE-gate (`mcCheck*Start*File` stubs) predicts no `[MC]` lines at all (E55D6 §2A.5). A call yielding a status-only record proves reachability; guest bytes need separate evidence |
| C2 | String-anchored UI layer only: H-A (`cFEStateLogin`) and H-B (`option_savereplay`) exist as code with concrete string xrefs (§2) but their forward jal inventories contain **no** card-cluster target | Handler→cluster edge: no `jal`, no resolved data pointer, no logged `jalr` from either handler (or their sole callers `sub_001A97B8` / `sub_001FB588`) into the §1 chain. Vtable slot `0x474d54==0x20d1d8` owner **unknown**. Marked **unknown** | **unknown** — `cFEStateLogin` suggests a login screen and `option_savereplay` a save-options screen by NAME ONLY; no button sequence or screenshot in evidence drives them, so no input is claimed | **unknown** | Same probe presence test at the (undiscovered) menu ticks. Extra branch: a save-*write* flow exercises `sceMcWrite`/`sceMcMkdir` (E55D6 §1 #5), which are OUTSIDE the E55D3 probe — so continued probe silence PLUS a changed card manifest means write-only path (OTHER), not absence of wiring. State the manifest check in the run's stop rule |

## 4. One-boot empty-card probe design (concrete; no invented route)

No complete static route exists, so the only probe design that stays inside
existing route evidence is a **passive I26-FAST observation** (the single
supported route, `local/research/I26/ROUTES.md:7-33`):

- Start: I26-FAST from title with `PS2X_SKIP_MOVIE=1` (dev-only bypass) on
  the **unchanged empty card** (no seeding; seeding invalidates the E55D4 A/A
  manifest per E55D6 §3 and is out of scope until a path is proven).
- Buttons: the pinned I26-FAST script verbatim (START at tick ~636, menu
  crosses, Rival-card taps); NO save-menu detour — no detour sequence is
  supported by any route or screenshot, and none is proposed here.
- Flags: E55D3 probe `PS2X_PAD_CARD_PROBE=<file>` plus `PS2X_DETERMINISTIC=1`;
  same pinned binary/ISO/ELF/codegen as E55D4 (`§PINS`); P-lane slot lease,
  own cwd, PID-scoped kill.
- Stop: first `getdir`/`mcread` record (any status) or tick cap 2055
  (E55D4/E55D5 parity window); wall 500 s; log 4 MiB; probe 16 MiB caps.
- OTHER: (a) any first probe record → reachability proven, target the proven
  flow next; (b) zero probe records with `[MC] GetInfo` lines → GetInfo-only
  path; (c) zero probe records and no `[MC]` lines → HLE-gate or unwired on
  this route; (d) probe silence + manifest diff → write-only path.
- Note: (b)–(d) on I26-FAST through 2055 are ALREADY the E55D4/D5 result
  (zero records); repeating it without a new route or tap is not informative.
  The binding next step after this report is therefore **route discovery**
  (menu screenshots/logs locating the H-A/H-B screens), not another blind boot.

## 5. Gaps (stated plainly)

- Upstream of B16 unexamined by design (bound: 0x2C cluster + two UI layers).
  The three `sub_002C22C8` callers' own callers, `func_317D70` (alloc),
  `func_1BEE30/1A8A40/39B960/39D860`, and every `jalr` target are **unknown**.
- Guest query path/pattern per GetDir site (`a2=s1+0x139` at `0x2c424c` /
  `0x2c6884` not resolved to a string), `maxEntries`, `tableAddr`, payload
  layout: **unknown** (E55D6 §4b carries over).
- `sceMcGetInfo@0x40a498` single site (`0x2c5110`) and HLE `mcCheck*` gates:
  untested by the current probe (E55D6 §4c carries over).
- `ee-xref` sees only static `jal/j`, lui-pairs, data words, and *skipped*
  `jalr` log lines; successful indirect calls are invisible — absence of a
  static edge does not refute an indirect route.
- Pins: ssx3 `48704501` (this read), ELF SHA prefix `1b49d05c`,
  codegen `register_functions.cpp` prefix `8ea8ed43` (`§PINS`). No SHAs re-read
  beyond prefixes in this part.

## 6. Commands run (read-only; outputs in receipts)

- `ee-xref {0x2C5570,0x2C4210,0x2C42B0,0x2C6848,0x2C6B78,0x2C48C0,0x2C4050,0x2C3FA8,0x2C22C8,0x486f8c,0x474d54}` + string-vaddr xrefs
  `{0x47c3a8,0x45e318,0x470100,0x460db0,0x461ca0,0x471bf0,0x4a12b0}` → `xref.txt`
- `ee-at {0x2c5988,0x2c59b4,0x2c5e64,0x2c5f7c,0x2c424c,0x2c431c,0x2c6884,0x2c4f84,0x2c5020,0x2c4d1c,0x2c4ee4,0x2c6b90,0x2c4ec8,0x2c4ef8,0x2c5ba8,0x2c3fc0,0x2c22e8,0x1b3fdc,0x23d5b4,0x2659a4,0x241ab0,0x1a9478,0x20ddd4,0x2c2540}` → `at.txt`
- `ee-func` / `ee-label` on each of the above (all game labels `unknown`
  except `0x2c26d0: fiprintf [ssx3.toml]`) → noted inline, outputs in receipts
- ELF string file-offset → vaddr mapping via section headers → `strings.txt`
- Forward jal inventory (codegen `jal func_*` scan per handler) → `strings.txt`
- Pins: `git log -1`, `sha256sum` ELF + `register_functions.cpp` → `strings.txt`
- Receipt sizes: REPORT ~9 KiB + three text receipts, total <512 KiB budget;
  <20 min read-only work.

## 7. Recommended next action (no verdict)

Route discovery before any boot or card seeding: capture menu
screenshots/logs that locate the H-A (login) and H-B (save-options) screens
and their button paths from the I26-FAST spine. Only then predeclare a
detour probe against the proven screen. If the orchestrator wants a boot
first, the only evidence-backed boot is the §4 passive I26-FAST title-window
re-observation — already covered with zero records by E55D4/D5, so it cannot
discriminate without a new route or an extended tap.
