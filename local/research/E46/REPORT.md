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

---

## Part 2 — bisect, combined boot, SC rider (orchestrator follow-up)

Budget: up to 6 boots, both mini slots in parallel. Used all 6
(e46c/d/e/f/g/h). Each bisect config = `0x396b40` + one suspect,
own codegen dir (`codegen-ssx3-e46<target>`), E33 vsync route.

### (1) Bisect: the breaker is `0x3b1140`

| Boot | Extra vs e46b | Wall/tick | Verdict |
|---|---|---|---|
| e46c | `0x3b1140`, runner `4591f446…` | 120 s / 6098 | BLACK (4×9448-B snaps, byte-identical to e46a black); 0 missing (died before others fire) |
| e46d | `0x14e130`, runner `1763289a…` | 120 s / 3732 | HEALTHY menus; 16 missing (other 16) |
| e46e | `0x144928`, runner `79d6d9c6…` | 120 s / 3011 | HEALTHY menus; 15 missing (other 15) |
| e46f | `0x30db90`, runner `37eddc99…` ×2 | 120 s / 3927 | HEALTHY menus; 7 missing |

Correlation is perfect: every config containing `0x3b1140` (e46a,
e46c) goes black; all five without it are healthy. Bisect runner
SHAs are single-read (build dirs were reconfigured for the next
config; e46f's binary survives in E46B-build, hence ×2).

Why calling `0x3b1140` breaks (code-read, no fix — no one-line
mechanism bug found):
- The target is a refcount-release: `v0=[a1+16]-1`, store, return
  if >0, else unlink the node. All 3 calls pass `a1=0x548840`
  (same node): counts 3→2→1→0+unlink on the third call. Caller
  (`0x3b0698`, legit vtable call `obj+52`) ignores all outputs, so
  the only observable delta vs the skip path is the refcount +
  unlink memory writes.
- Resume mechanism verified correct by reading, 7 ways: emitted
  callee body faithful (incl. `movn`, `bgtz`+`sw`-delay, `jr ra`);
  caller sets `ra=fallthrough` BEFORE dispatch and runs the delay
  slot; table slot single → correct owner; exactly one switch case;
  owner prefix skipped is other getters (dead by `jr ra` anyway);
  `r0` reads guarded; dispatch returns true with `pc=fallthrough`.
- This is the boot's FIRST previously-skipped call (frames
  identical through tick 245), so pre-246 guest state is faithful;
  the corruption vector must be the unlink writes interacting with
  state our runtime built differently pre-246 (HLE/loader/patch
  suspects), not a resume defect — the same path carries
  `0x396b40` (×1000+), `0x14e130`, `0x144928`, `0x30db90` to
  healthy menus. Recommended next step: PCSX2-side watch on
  `[0x548840+16]` + node words across the transition (T-lane), or
  an EE-word watch boot here with only `0x3b1140` in a pre-246
  window.
- `0x3b1140` stays OUT of `ssx3.toml` (only exclusion).

### (2) Combined boot e46g: all-but-breaker + `0x32f8b0`

18 entries (`codegen-ssx3-e46g`, `resolved 18 of 18 across 17
owners`, 18 files differ), runner `a2521d92…` ×2, wall 300, tick
8951, snap 10 (30 snaps). Missing-target: **only `0x3b1140` ×3** —
all 18 resolve and no new targets appear on this route. Site-1
appx 189 rows all `tw0=0x1b0`. SC transition captured at tick 1269
(no rider yet — appends start ~1273); steady SC missed again
(next snap tick 1481 = Select Peak). Race reached (tick 7403+):
HUD live (1ST/2, 00:00:31, 4%, 75 MPH, +5000 STYLE BONUS) but 3D
world black with faint streaks — same class as E31's own race
frames (viewed `frames-e31l-1/snap-0583.00s.png`: dark + streaks),
so no regression and no race-3D fix either.

### SC rider capture (boot e46h, 6th boot)

e46g's snap-10 still bracketed steady SC, while its race portion
(ticks 7403–8951, same E31-route script and config) already
answers the step-3 questions, so boot 6 was re-aimed at SC
steady-state (wall 120, snap 5, same combined runner): **PASS —
the rider renders.** `e46h-sc-rider.png`: Zoe's 3D model (jacket,
pants, hair, shoes) at Select Character with stats/silhouettes,
matching T62's PCSX2 reference layout. e46h missing-target:
`0x3b1140` ×3 only; site-1 `0x1b0` ×189. Step-2 criterion MET.

### (3) Race: world still dark (from e46g, no 7th boot)

Step 3's questions answered by e46g's race portion (same script +
config as a dedicated race boot would use; a 7th boot would exceed
the 6-boot cap): 3D world NOT visible (black + faint streaks,
E31-class); missing targets remaining: `0x3b1140` ×3 only. Race-3D
needs a follow-up: either race-time-only resume entries (see
rescan candidates below) or a downstream draw/GS gap — SC-rider
pixels prove the menu 3D path end-to-end, the race world path does
not follow yet.

### Rescan (orchestrator FYI): relaxed data-ref pass

`local/tooling/ee/ee-xref 0x396b40` confirms `.rodata 0x493644 →
0x396b40` (my strict scan required `jr ra` at A−8; all 18 census
targets sit behind `[jr ra][?][nop]` with the `jr ra` at A−12).
New script `local/research/E46/e46_rescan.py`, full output
`local/research/E46/e46-rescan.txt`: 106,303 data words →
**1210 hits** (interior, 8-aligned, `word[A−12]==jr ra` and
`word[A−4]==nop`), **census recall 18/19** (misses only
`0x30db90`, reached via register computation; `0x140bc0` has 36
data refs, `0x32f8b0` ← `.rodata 0x48e5a4`). The 1192
non-census hits are the race-time candidate set — report-only, no
entries added without a boot, per instructions.

### Part 2 frames (`local/research/E46/frames/`)

| Frame | SHA256 (short) | Shows |
|---|---|---|
| `e46h-sc-rider.png` | `78da2e1a…` | SC WITH Zoe 3D rider (step-2 PASS) |
| `e46g-sc-transition.png` | `83923a13…` | SC at tick 1269, pre-rider |
| `e46g-race.png` | `f63bf643…` | race HUD live, world dark |
| `e46c-breaker-black.png` | `6120a759…` | breaker black (≡ e46a black) |

### Part 2 receipts

- Fork `ssx3.toml`: 18 passing entries, byte-identical list to the
  validated `ssx3-e46g.toml` (modulo machine paths); `0x3b1140`
  excluded with comment. `codegen-ssx3` untouched (canonical);
  `codegen-ssx3-e46g` is the validated-next candidate dir.
- Suite 591/591 re-run on current source (E46B-build binary).
- Runners: e46g/h `a2521d92…` ×2; e46f `37eddc99…` ×2; e46c/d/e
  single-read (dirs reconfigured).
- Traces: e46g `a2ef1819…` (11,456,512 B), e46h `aa4ed5b1…`
  (4,517,888 B), ×2. Logs: e46g `710dc808…` (10,148,720 B), e46h
  `d37df89c…` (7,427,619 B), ×2.
- Slots: waves ran one runner per slot with own run dirs
  (E46-run/E46B-run) and PID tracking; all leases released; GB2
  peer excused once (`pgrep_rc: 0` on e46f, PID verified foreign).
- Boots used: 6/6 (c, d, e, f, g, h). Disk: E46 ≈ 8 GB total
  (builds ×2 5.8, 7 codegens 1.9, runs + logs 0.2) of 200 GB cap.
- Deltas to Part 1: `e46_boot.py` gained `E46_RUN_DIR` /
  `E46_BUILD_DIR` overrides; new `e46_rescan.py` +
  `e46-rescan.txt`; REPORT appended. No recompiler source changes
  in Part 2 (toml only).

### Updated recommendation

1. Committed: mechanism + 18 passing entries (this report's
   appendix commit). `codegen-ssx3` promotion to `-e46g` content
   is the orchestrator's gate call.
2. `0x3b1140`: needs the T-lane PCSX2 watch (or EE-word watch
   boot) before any entry; do not add blind.
3. Race-3D: next lane picks from the 1192 rescan candidates that
   fire at race time (needs a race-window missing-target census —
   currently ZERO missing targets fire in the race, so the gap
   may be downstream of the function table, not more entries).
4. Cleanup candidate (orchestrator): `E46B-build/`,
   `codegen-ssx3-e46{,b,3b1140,14e130,144928,30db90}/`,
   `E46B-run/` once the gate passes (~4.5 GB).
