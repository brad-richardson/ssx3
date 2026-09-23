# E46 report — indirect-call targets missing from the function table

Brief `local/muse/prompts/E46.md`. Tables + receipts; the orchestrator
decides. Read first: `AGENTS.md`, `local/AGENTS.local.md`,
`local/research/E44/REPORT.md` (Part 4), `local/research/T64/REPORT.md`,
`local/research/E32/REPORT.md`.

## Outcome

- **Part A census: 18 distinct missing targets** across all
  `~/dev/ssx3-work/*-run/` boot logs plus E31's SSD race boots (same 18;
  38 pairs internal vs 37 E31, the only delta one extra `0x140bc0`
  source). All 18 are 8-aligned genuine function starts (9 tail `jr ra`
  thunks, 9 mid-cluster bodies after nop padding); **none** is
  immediately preceded by `jr ra`, so the brief's boundary signature as
  stated matches zero of them. Every body terminates with `jr ra`
  inside its CSV owner end (no overrun).
- **Static pass: 1686 hits, zero in the census.** Data refs to
  jr-ra-preceded `.text` addresses are a different population
  (vtable slots into runs of `jr ra` nops) and corroborate none of the
  18. The scan contributes no additions.
- **Fix: config list, not CSV surgery.** New `extra_function_starts`
  in `ssx3.toml`, parsed in `config_manager.cpp`, resolved to resume
  entries of the containing function — the exact production path
  direct-call (`jal`) interior targets take
  (`m_resumeEntryTargetsByOwner` → table slot → `switch/goto`).
  5 new unit tests; suite **591/591** flags-unset from the fork root.
- **Regen is faithful:** empty-config regen is byte-identical to
  `codegen-ssx3` (0/9457 differ); all-18 regen differs in exactly 18
  files (table + 17 owners, each +1 switch case +1 label).
- **Boot e46a (all 18): FAILS — black screen.** Frame-identical to
  E44 through tick 245, then stuck on `fd889dc5` forever while E44
  reaches menus at 257. Divergence starts at tick ~246, exactly when
  the first previously-skipped calls fire. Breaker is in the first
  firers (`0x3b1140`×3, `0x14e130`, `0x144928`, `0x30db90`×11).
- **Boot e46b (`0x396b40` only): template-6 FIXED, game healthy.**
  Zero `0x396b40` skips; site-1+2 item-0 w0 = `0x1b0` on all 297 appx
  rows (was `0x30`/silent); menus render; Happiness race reached with
  live HUD (00:00:06→00:00:19, 1%→5%). Race 3D world still dark.
- **Committed: mechanism + `0x396b40`-only config** (boot-proven).
  The other 17 stay out pending one-boot-each bisection. A new 19th
  target `0x32f8b0` (×123, source `0x334f5c`) fires only once
  `0x396b40` executes — downstream work for the next lane.
- **Gap: no Select-Character still.** SC (~tick 1240–1400) fell
  between snap-0030 (tick 1025) and snap-0060 (tick 1933). The rider
  pixels are unobserved; the 0x1b0 data proof stands in. Next lane:
  `--snap 10` around SC.

## Validation criteria (honest status)

| Criterion | Status |
|---|---|
| Zero `missing-target` lines | e46a: 0 but black (invalid). e46b: 17 old + 1 new remain (NOT MET on the validated build) |
| Template-2/item-0 w0 = `0x1b0` | MET (e46b: 165 site-1 + 132 site-2 rows, all `0x1b0`) |
| Rider visible at Select Character | NOT MET (no SC still; snap gap) |
| E31 race route: 3D world in race frames | NOT MET (race reached, HUD live, world still dark) |

## Part A — census (18 targets)

Pairs file: `local/research/E46/e46-census-pairs.txt` (internal, 38
pairs); `local/research/E46/e46-e31pairs.txt` (E31, 37 pairs).
Disassembly windows: `local/research/E46/e46-target-dump.txt`.

| Target | Internal | E31 | Sources | Containing CSV function | Kind |
|---|---|---|---|---|---|
| `0x396b40` | 36211 | 4432 | `0x37a6a0` | `sub_00396958` [0x396958,0x3970f8) | mid getter, ~236 B, mode bits |
| `0x140bc0` | 4669 | 4937 | 14 incl `0x2e3bb8`×2122 | `sub_00140B80` [0x140b80,0x140bc8) | tail `jr ra` +8 |
| `0x375a00` | 1283 | 1360 | `0x2f0b54` | `sub_003759E8` [0x3759e8,0x375a08) | tail `jr ra` +8 |
| `0x38f7f8` | 1283 | 1360 | `0x2f0adc` | `sub_0038F7B0` [0x38f7b0,0x38f800) | tail `jr ra` +8 |
| `0x3968c8` | 1061 | 1129 | `0x2f0e58` | `sub_003961A8` [0x3961a8,0x3968d0) | tail `jr ra` +8 |
| `0x30db90` | 472 | 242 | `0x419460`/`70`/`34` | `sub_0030DB70` [0x30db70,0x30dba0) | mid subtract, 16 B |
| `0x26a0b8` | 408 | 531 | `0x112454` | `sub_0026A090` [0x26a090,0x26a138) | mid FPU, 124 B |
| `0x3b1140` | 108 | 36 | `0x3b0698` | `sub_003B10D0` [0x3b10d0,0x3b11a0) | mid refcount, 92 B |
| `0x144928` | 49 | 34 | 6 incl `0x194fdc` | `sub_001448D8` [0x1448d8,0x144aa8) | mid copy, 188 B |
| `0x14e130` | 36 | 11 | `0x194b64` | `sub_0014E0E0` [0x14e0e0,0x14e2c0) | mid copy, 196 B |
| `0x26a068` | 18 | 34 | `0x26a1b8` | `sub_00269F18` [0x269f18,0x26a070) | tail `jr ra` +8 |
| `0x284b50` | 6 | 16 | `0x27cf14` | `sub_00284AE8` [0x284ae8,0x284b58) | tail `jr ra` +8 |
| `0x155380` | 4 | 5 | `0x14df78` | `sub_00155328` [0x155328,0x155388) | tail `jr ra` +8 |
| `0x2849b8` | 3 | 6 | `0x27cf14` | `sub_00284950` [0x284950,0x2849c0) | tail `jr ra` +8 |
| `0x284940` | 3 | 6 | `0x27cf14` | `sub_002848D8` [0x2848d8,0x284948) | tail `jr ra` +8 |
| `0x153258` | 3 | 4 | `0x14dec8` | `sub_001530E0` [0x1530e0,0x1532a0) | mid flag-set, 72 B |
| `0x1566e8` | 3 | 4 | `0x14dea4` | `sub_001565C8` [0x1565c8,0x1567b8) | mid flag-clear, 100 B |
| `0x153200` | 2 | 3 | `0x14dea4` | `sub_001530E0` [0x1530e0,0x1532a0) | mid flag-clear, 84 B |

All 18: 8-byte aligned yes; immediately preceded by `jr ra` no (all
preceded by `[jr ra][delay][nop]` or `[jr ra][nop][nop]` padding, or
are themselves the cluster's final `jr ra`); first-`jr`-end within
owner end yes (table's size column). Full per-target predecessor words
in `e46-scan.txt` (PART A section).

Pair-set diff internal vs E31: identical except internal has one extra
pair (`0x112e04→0x140bc0`). Target union identical.

New in e46b (not in census): `0x32f8b0` ×123 from `0x334f5c`,
`sub_0032F840` [0x32f840,0x32f8c0), 8-aligned, follows
`[jr ra][addiu sp,80][nop]`, body `lw/sw/jr ra/sw` (getter). Fires
only with `0x396b40` executing — downstream census addition for the
next lane.

## Mechanism

Production direct-call interior targets do NOT become `entry_*`
functions (that slicer is test-only); the member
`discoverAdditionalEntryPoints()` files them as resume entries of the
containing owner (`m_resumeEntryTargetsByOwner`), the table emitter
registers `target → owner`, and the function emitter adds
`case T: goto label_T`. Indirect targets get nothing because no
static analysis sees them.

**Pick: config list** (`extra_function_starts` in `ssx3.toml`).
Same downstream path as direct-call targets (same validation, same
emission, no new codegen shapes); no churn in the 9284-row
Ghidra-sweep CSV (which would also fork the generated artifact from
its source); one boot-proven entry committable while 17 wait.

Diff (fork `ssx3`, on top of `e52b6bf`):

| File | Change |
|---|---|
| `ps2xRecomp/include/ps2recomp/types.h` | `RecompilerConfig::extraFunctionStarts` |
| `ps2xRecomp/src/lib/config_manager.cpp` | parse `extra_function_starts` (hex strings + ints; bad entries warned + skipped); save round-trip |
| `ps2xRecomp/include/ps2recomp/ps2_recompiler.h` | `ResolveExtraFunctionStarts` static decl |
| `ps2xRecomp/src/lib/ps2_recompiler.cpp` | resolver (exec check, known-start skip, decoded-owner best match, dedupe) + hook in member `discoverAdditionalEntryPoints` with reporter line |
| `ps2xTest/src/ps2_recompiler_tests.cpp` | 5 tests (parse, default-empty, round-trip, resolve, skip-starts/gaps/undecoded) |
| `games/ssx3/ssx3.toml` | `extra_function_starts = ["0x00396B40"]` + deferred-17 comment |

Resolver guards (mirroring the live direct-call path): non-executable
→ skip; already a function start → skip; no decoded recompiled
non-`entry_` owner containing the address → skip; owner-start ==
target → skip. Anything unresolved is reported by the
`resolved X of Y` line, never fatal.

## Static pass

Script `local/research/E46/e46_scan.py`, full output
`local/research/E46/e46-scan.txt` (1686 hits). Scanned 106,303
4-aligned words across `.data`, 4 vtable sections, `.rodata`,
`.gcc_except_table`, `.lit4`, `.sdata` for values pointing into
executable sections at 4-aligned non-start addresses with `jr ra` at
A−8. Result: **1686 hits, 0 in the census** (all 18 census targets
listed as missed). The hits are vtable/data refs into runs of tiny
`jr ra` thunks (e.g. `0x113ce0`, `0x167e58` clusters) — a different
population from the census (tail-thunks and padded getters). Per the
brief's rule the scan adds nothing; the 18 rest on census +
prologue/epilogue verification instead.

Sample (first 5 of 1686):

| Hit | Refs | Containing CSV |
|---|---|---|
| `0x1009e0` | `.data:0x43cf24` | `sub_00100680` |
| `0x100b90` | `.data:0x43cf3c` | `sub_00100680` |
| `0x100f88` | `.data:0x43cf34` | `sub_00100680` |
| `0x10a768` | `.rodata:0x4585fc` | `sub_00108E88` |
| `0x10c498` | `.rodata:0x456a74` | `sub_0010C450` |

## Codegen + build + suite

- Scratch toml `~/dev/ssx3-work/E46/ssx3-e46.toml` = canonical toml
  with only the 3 path lines repointed internal (diff receipt kept).
  ELF/CSV verified byte-identical internal vs SSD (`cmp`).
- Empty-config regen → `codegen-ssx3-e46empty`: **0/9457 files differ**
  from `codegen-ssx3` (pipeline fidelity; scratch dir deleted after).
- All-18 regen → `codegen-ssx3-e46`: 18 files differ (table + 17
  owners; each owner +1 case +1 label); log
  `resolved 18 of 18 ... across 17 owner function(s)`.
- `0x396b40`-only regen → `codegen-ssx3-e46b`: 2 files differ.
- Build `~/dev/ssx3-work/E46-build` (E32 flags + new codegen):
  green, no new warnings (pre-existing gs/memory/SDK/System.cpp only).
- Suite from fork root, flags unset: **591/591** (5 new E46 tests;
  HEAD registers 588 `tc.Run`, worktree 593 — the +5 are mine).

## Boots (Mac mini, E46-build, E33 vsync route, lease-claimed)

| Boot | Config | Wall | Result |
|---|---|---|---|
| e46a | all 18, runner `dc23fbf4…2fc5ce` ×2 | 300 s, rc 0, tick 17890 | BLACK: identical frames to E44 thru tick 245, `fd889dc5` forever after; zero missing-target; appends die at ~258 |
| e46b | `0x396b40` only, runner `ceb9ca1a…293a6538` ×2 | 300 s, rc 0, tick 8226 | HEALTHY: menus, loading, Happiness race HUD 00:00:06→00:00:19; `0x1b0` ×297; 18 missing targets remain (17 old + `0x32f8b0`) |

e46a breaker localization: first old-boot skips fire at tick ~246
(`0x3b1140`×3, `0x14e130`, `0x144928`, `0x30db90`×11, then
`0x396b40`); frames diverge 246→257 (old reaches menus, new stays
black). e46b proves `0x396b40` alone is safe, so the breaker is in
the other 17 and almost surely one of the first four firers.
Eliminated as causes: deps drift (`_deps` HEADs identical to E32),
fresh mc0 (both empty), regen infidelity (byte-identical empty
regen), resume-mechanism shape (emitted switch/goto/jr verified by
eye), callee overrun (all 18 terminate inside owner ends).

e46b appx: site-1 165 rows all `tw0=0x1b0`, site-2 132 rows all
`tw0=0x1b0` (site-2 never fired in E44e), site-0 3 rows `0xc`.
appsum (site-0 hist) still m∈{0,3} as in E44e; tplm 0 (tap misses
the transient, same as E44e).

## Frames (viewed by eye; PNGs in `local/research/E46/frames/`)

| Frame | SHA256 (short) | Shows |
|---|---|---|
| T62 `t62a-shot-sc.png` | `50e6809e…` | PCSX2 Select Character WITH Zoe rider (reference) |
| e46b Main Menu (tick 1025) | `1d29776c…` | Single Event highlighted, renders clean |
| e46b Select Mode (tick 1933) | `bef0a69a…` | Peak 1 map, Race/Freestyle |
| e46b Loading (tick ~4100) | `0d2e2ff4…` | Happiness 43% with 3D mountain vista |
| e46b Race (tick ~6500) | `7eeb87c9…` | 2ND/2 00:00:06 1%, HUD live, world black |
| e46b Race (tick 8226) | `f46225b4…` | 2ND/2 00:00:19 5% 73 MPH, world still dark |
| e46a black (tick 17890) | `6120a759…` | 9448-byte black (all 10 e46a snaps identical) |

SC (~tick 1240–1400) fell between snap-0030 (1025) and snap-0060
(1933): no SC still exists in either boot. Rider pixels unobserved.

## Receipts

- Fork: branch `ssx3`, base `e52b6bf`; commit `[E46]` (see below);
  runner-dir gate empty (no `ps2xRuntime/src/runner` diff).
- Runners: e46a `dc23fbf46a1d1ffca76a64844edd98cdaf11d6c886134c6921e4cdac4b2fc5ce` ×2;
  e46b `ceb9ca1a127646bb60ab74f0820bb40bceaff05a59e5bed3cb457f4f293a6538` ×2.
- Traces: e46a `2666f07e…b25f` (6,795,264 B), e46b `f7ade3bc…cdf`
  (9,625,600 B), ×2 each. Boot logs: e46a `ff0191ef…2441`
  (36,310,093 B), e46b `bd516714…875` (39,932,034 B), ×2 each.
- Lease: slot 1 (e46a, no peers) / slot 2 (e46b, peer excused),
  claimed + released, own-PID checks, `pgrep_rc: 1`.
- Disk: 33.5 → 38.1 GB of 200 (E46 ≈ 4.6 GB: build 2.8 + 2 codegens
  0.6 + runs/logs; `codegen-ssx3` untouched).
- Spend: 2 boots (budget), ~3 h of 5 h, builds as needed.

## Recommendation (orchestrator decides)

1. Take the mechanism + `0x396b40` (committed): template-6 path
   proven at the data level, game healthy through race HUD.
2. Next lane bisects the 17 one boot each, suspects first:
   `0x3b1140`, `0x14e130`, `0x144928`, `0x30db90` (each a one-line
   toml change + 2 s regen + incremental rebuild + ≤120 s boot to
   tick ~300; pass = menus at 257). Then the tail thunks as a batch.
3. Re-snap SC with `--snap 10` to catch the rider; race-3D needs the
   remaining entries (watch `0x140bc0`-class + new `0x32f8b0`).
4. The all-18 codegen (`codegen-ssx3-e46`) and E46-build/E46-run are
   left in place for the bisect lane.
