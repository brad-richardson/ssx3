# T48 REPORT — PCSX2 reference for the recomp's missing 3D: per-draw census by GIF path + VU1 program cycles, Select Character and race start

Brief: `local/muse/prompts/T48.md`. Tables + receipts; the orchestrator
decides. Read first: `AGENTS.md`, `local/research/T47/REPORT.md`,
`local/research/G12/REPORT.md` §2, `local/research/G13/REPORT.md`,
`local/research/G10/REPORT.md` §3c. Lane recipe complied with throughout
(no-status-edit rule respected — this file is the worker handoff).

## T48-0. Mission table

| # | Mission | Result |
| --- | --- | --- |
| 1 | One bounded log-only patch (GIF-path tag + verts on G12_DRAW; T48_PATHS/vsync; T48_VU1/program; script-driven dump trigger), same tree `9056c083` | DONE — 3 builds, budget was ≤2 (overrun declared §T48-7.1) |
| 2 | Capture A: Select Character settled, Zoe visible — 8-vsync `.gs` + logs + native F8 | DONE |
| 3 | Capture B: Happiness Rival Challenge, first seconds of race — 8-vsync `.gs` + logs + native F8 | DONE (5th boot; run-budget overrun declared §T48-7.2) |
| 4 | Tables per capture (draws/vsync by path; top TBP0/PRIM tuples; VU1 cycle min/med/p99/max + n>65536; xgkicks/program) | DONE both captures |

Headline for the E-brief: across **11,591 healthy VU1 programs** (5,499 at
SC + 6,092 in-race), **zero exceed 65,536 cycles** — SC max 2,090 (31×
below the recomp budget), race max 23,540 (2.8× below). All race/menu
traffic flows through GIF PATH1 (XGKICK/ring); PATH2/3/dead = 0 in both
windows and across B04's full 30,977-vsync run. H1 (budget truncation)
predicts missing PATH1 draws; the healthy side shows complete PATH1 draw
sets (191 draws/8 vsyncs at SC, 1,743/8 in-race) with full dump geometry.

## T48-1. Pins

| Pin | Value |
| --- | --- |
| PCSX2 tree | `9056c08349cc29ad02a6d1a3a4133259019195af` (`/home/brad/pcsx2-g7/pcsx2`); pre-work status = G13-end exactly (M GS.cpp, GSState.cpp, GSRendererHW.cpp, GSDumpReplayer.cpp, R5900OpcodeImpl.cpp) |
| Pre-patch qt | `1f664fddbd268f94a42695895cf65977c32dce8dc91e8323385b9bcd13fd0696`, 130,961,672 B (== G13 pin; stashed `/home/brad/pcsx2-g7/pre-t48/`) |
| Pre-patch gsrunner | `8e446ff19fa2d1d10f2f981d7425047baa9e23334fd951a205e60c2a30bc8a56`, 90,455,240 B (== G13 pin; stashed alongside) |
| Post-patch qt | `2539e2cd6a6874d7908c7352a7244239aa339499706d35fec3bd0cd5f2f5114b`, 130,978,600 B |
| Post-patch gsrunner | `765baf09c401b410cca777c41d9c9923d10717208f12b6d50a8e0a0c81de39a1`, 90,483,912 B |
| Game inputs | T47's: ISO `SSX 3 (USA).iso` (3,005,415,424 B), BIOS trio, `dat-t48` = copy of `pcsx2-t4/dat` (T47 lineage, 25,356 KiB) with exactly 2 keys flipped (§T48-2) |
| Capture A dump | `t48a-dump.gs` sha256 `a34e70df9a7b3133609e1d92f72cba1608f0a46a73dbd0b3b48d0d98777937c9` (11,319,387 B; transfer `.gs.zst` 1,267,456 B) |
| Capture A F8 | `t48-shot-t48a-sc.png`, 199,503 B, 640×480 native, settled SC + Zoe rendered (viewed §T48-5) |
| Capture B dump | `t48b-dump.gs` sha256 `244c51185fd7b0c44c0f571509b33c6214b8a1aa37557a547261b195ebb8013b` (19,973,281 B; transfer `.gs.zst` 4,664,562 B sha256 `377ca2f1680ba72e42b5bbf9a1426db0bf9494fff628427598f444a20dc4e7a8`) |
| Capture B F8 | `t48-shot-t48b-race.png`, 404,847 B, race 00:00:17 / 8% / 43 MPH / 2ND/2 (rider largely behind a tree at this instant — stated; window frames bracketed §T48-6) |
| B04 bonus PATHS | full-run 30,977-vsync path census incl. ~11k race vsyncs (§T48-6) |

## T48-2. Capture configuration (declared deviation)

T46 settings EXCEPT two speedhack-class flags, flipped in the `dat-t48`
copy (setup `t48-setup.sh`):

| Key (PCSX2.ini) | T46/T47 | T48 | Why |
| --- | --- | --- | --- |
| `vuThread` (Speedhacks) | true (MTVU on) | false | VU1 programs must execute synchronously on the EE thread for exact per-program start→E-bit attribution; MTVU runs them async on a worker |
| `EnableVU1` (Cpu/Recompiler) | true (microVU) | false (interpreter) | cycle + E-bit + XGKICK hooks sit in the interpreter (`_vu1Exec` E-bit tail, `_vuXGKICK`); interp counts 1 cycle/instr + modeled stalls — the closest healthy counterpart to the recomp's interpreter budget |

Everything else is T47-identical (renderer Auto = OGL-HW on llvmpipe,
native F8 `ScreenshotSize = 0`, same ISO/BIOS/memcards/bindings, same T47
F1 navigation gates). Capture binary = T48 build; proof binary = stashed
pre-patch G13 build with `resources/` + `translations/` symlinked
alongside (verified failure mode: without them it sits on a
`Translation Error` dialog and boots nothing — §T48-7.5). `T48_MODE
mtvu=0` logged once per run; interp execution is additionally proven by
the `end=ebit` ratio (100% both captures — an mVU run would show
abort-only records).

## T48-3. The patch (`t48-patch.diff`, one logical patch)

Applier `t48-hook.py` (exact-match hunks, assert count==1 or abort),
plus `t48-hook-vu.py` (identical VU hunks, used once as the repair half),
`t48-fix1.py`/`t48-fix2.py` (two small repair scripts). Net vs
`9056c083`: +191/−2 lines across 6 files in 12 hunks — all counters +
`Console.WriteLn` on the G8 emulog channel. No renderer, EE, timing or
content change. `t48-patch.diff` (301 lines) extracted from the worktree
diff by hunk filter, verified to contain all 16 edits.

Hook sites (T48 hunks only):

| Hunk | File:line | What |
| --- | --- | --- |
| T48-GS1 | `pcsx2/GS/GS.cpp` ~26 | `g_t48_vsync` (atomic int, GS→EE vsync mirror), `g_t48_window` (atomic bool, widened window), externs for GSState counters |
| T48-GS3 | `pcsx2/GS/GS.cpp` ~460 | script-driven trigger (`/tmp/t48-arm`, `/tmp/t48-dump-now` → one-shot `GSQueueSnapshot("",5)` + `T48_DUMP_QUEUED`); per-vsync `T48_PATHS`; `g_t48_window = queued && [winstart−30, winstart+8)`; vsync mirror |
| T48-GS4a/b | `pcsx2/GS/GS.cpp` ~505 | `&& !t48_seen` guards on the G13 rate + fallback fires |
| T48-ST1 | `pcsx2/GS/GSState.cpp` ~21 | `g_t48_pkts[4]`, `g_t48_bytes[4]`, `g_t48_curpath`, `g_t48_ring_{n,v,p}[4096]` |
| T48-ST2 | `pcsx2/GS/GSState.cpp` ~3378 | `Transfer<index>` top: per-index packet/byte counters + mapped current-path stash |
| T48-ST3 | `pcsx2/GS/GSState.cpp` ~2545 | `FlushPrim`: ring write keyed `s_n & 4095` |
| T48-HW0/1 | `pcsx2/GS/Renderers/HW/GSRendererHW.cpp` ~2790 | block-scope ring externs; `G12_DRAW` gains match-checked `verts=` (replaces the G12 zero) + `path=` (−2 on ring miss); still under the G13 `if (m_dump)` gate |
| T48-VU1 | `pcsx2/VU1micro.cpp` ~11 + ~83 | record globals; begin-record per MSCAL/MSCNT/MSCALF (live record closes as `end=abort`); one-shot `T48_MODE` |
| T48-VU2 | `pcsx2/VU1microInterp.cpp` ~14 + ~199 | close-record at the E-bit stop (`cycles = VU1.cycle − start`, E-bit instr inclusive, stalls included); `end=ebit` |
| T48-VU3 | `pcsx2/VUops.cpp` ~12 + ~1912 | XGKICK-instruction counter (`_vuXGKICK`) |

Index→PATH map (verified in-tree, §T48-8 anchors): MTGS ring
`Command::GIFPath1/2/3` → `GSgifTransfer/2/3` (`MTGS.cpp:386/411/436`)
→ `Transfer<3>/<1>/<2>` (`GS.cpp:431-444`); `gifPath[tranType & 3]`
(`Gif_Unit.h:693`) puts XGKICK→PATH1, DIRECT→PATH2, DMA/FIFO→PATH3;
`GSgifTransfer1` (→`Transfer<0>`) has no callers (dead slot). So **idx3
= PATH1 (XGKICK+VIF1), idx1 = PATH2 (EE direct), idx2 = PATH3
(DMA/FIFO), idx0 = dead (expect 0)**. `T48_PATHS` prints
p1(idx3)/p2(idx1)/p3(idx2)/p0(idx0); DRAW `path=` stores the mapped PATH
(1/2/3, 0 = dead slot, −1 = pre-first-transfer, −2 = ring miss).

`verts=` semantics (empirical): `tail−head` at FlushPrim is the per-flush
vtx_buff increment (observed 0–2: strip carry-over increments), NOT the
draw's batch totals — a race draw aggregates ~4 prims, an SC draw ~22
(§T48-5/6 censuses). Geometry authority for the E-brief is the `.gs`
dump itself (full vertex data); `verts` separates empty/state flushes
from vertex-carrying ones. No fourth build was spent chasing batch
totals (budget §T48-7.1).

## T48-4. Behavior preservation (two legs)

Leg 1 — deterministic replay (patched gsrunner `765baf09…` on the G13
rich dump `154d9d85…`, G10 §3c shape, `-loop 1`): **7/7 PNG md5s match
the G13 §3c pins exactly** (`b7a3e8db a7929218 bb8b1d85 817e934f ×2
85cf3599 ×2`, pairwise identities reproduced) **and HWSTAT matches
exactly** (791 draws / 37 passes / 0 barriers / 14 copies / 320 uploads
/ 6 readbacks). Transfer counters, ring writes and gated-log code are
behavior-neutral. Side finding: the replay emulog carries 0 G12_DRAW
lines — the G13 `if (m_dump)` gates work as designed (gsrunner never
opens the dump writer, so gated logs stay silent while ungated
G12_VSYNC/DUMP_VSYNC fire; G13's 785 replay DRAWs came from its pre-gate
gsrunner build).

Leg 2 — live frames (patched `2539e2cd…` vs stashed unpatched
`1f664fdd…`, same `dat-t48`, same settled SC, native 640×480 F8,
cropdiff whole-frame): **mean = 0.45, p99 = 16** — identical up to
animation phase (T47's title gate is mean < 2.0). Both match T47's F8 SC
ref (mVU+MTVU settings) at mean ≈ 0.85–0.91 — the interp/no-MTVU config
reaches the same settled screen.

## T48-5. Capture A — Select Character, settled, Zoe visible

Route: T47 F1 script verbatim to the SC park (all gates passed),
`T48_DUMP_QUEUED vsync=18807`, dump over vsyncs 18808–18815, native F8
after the window. F8 viewed: settled SC, Zoe 3D model rendered, stat
bars, rider silhouettes. (A-run poll log lost to a same-name overwrite
by the first proof attempt — §T48-7.4; settled state re-proven by the
SC-LIKE gate pass + F8-vs-T47-ref mean ≈ 0.9.)

Draws per vsync by path (191 G12_DRAW, all `path=1`, 0 ring misses):

| vsync | p1 pkts / bytes | p2 | p3 | p0 | draws (all PATH1) |
| --- | --- | --- | --- | --- | --- |
| 18808 | 603 / 724,128 | 0 | 0 | 0 | 23 |
| 18809 | 603 / 724,128 | 0 | 0 | 0 | 24 |
| 18810 | 603 / 724,128 | 0 | 0 | 0 | 24 |
| 18811 | 603 / 724,128 | 0 | 0 | 0 | 24 |
| 18812 | 603 / 724,128 | 0 | 0 | 0 | 24 |
| 18813 | 603 / 724,128 | 0 | 0 | 0 | 24 |
| 18814 | 603 / 724,128 | 0 | 0 | 0 | 24 |
| 18815 | 603 / 724,128 | 0 | 0 | 0 | 24 |

Whole SC frame flows through PATH1; PATH2/3/dead = 0 all window. Dump
census (ground truth): 603 xfers / 724,128 GIF bytes per vsync —
**exactly the T48_PATHS numbers**; dump `paths=[3]` (= idx3 = PATH1,
map confirmed end to end); per-vsync geometry 112 TRI + 41 SPRITE + 387
tristrips (540 prims), 6 IMAGE tags (393,216 B uploads), 12 texture
TBP0s.

Top (FBP, TBP0, PRIM, TME) tuples by count (8 vsyncs):

| FBP | TBP0 | PRIM | TME | n |
| --- | --- | --- | --- | --- |
| 0 | 4736 | 4 (tristrip) | 1 | 32 |
| 0 | 3712 | 4 | 1 | 32 |
| 0 | 5760 | 4 | 1 | 16 |
| 0 | 11017 | 6 (sprite) | 1 | 16 |
| 0 | 4736 | 3 (triangle) | 0 | 12 |
| 0 | 3712 | 3 | 0 | 12 |
| 112 | 0 | 6 | 1 | 8 |
| 0 | 0 | 6 | 0 | 8 |
| 0 | 0 | 3 | 0 | 8 |
| 0 | 11017 | 3 | 0 | 8 |

(TBP0 4736/3712 = Zoe mesh textures; 112←0 = composite; (0,0,*,0) =
untextured state draws. TBP0s match the dump census list.)

VU1 programs over the widened window (5,499 records, **100% end=ebit,
0 aborts**):

| stat | cycles | xgkicks/program |
| --- | --- | --- |
| min | 2 | 0 (2,016 programs) / 1 (3,483 programs) |
| median | 76 | — |
| p99 | 2,004 | — |
| max | 2,090 | max 1 |
| **n > 65,536** | **0** | — |

Distinct start_pcs: 0x8 (1,755) / 0x2 (1,593) / 0x257 (765) / 0x0 (576)
/ 0x73 (333) / rest — a handful of tiny object programs (tens to ~2k
cycles, 0–1 XGKICK each), re-kicked every vsync (230–1,212/vsync; ±1
vsync attribution skew, §T48-7.6).

## T48-6. Capture B — Happiness Rival Challenge, first seconds of race

Route (B05): T47 legs with identity-vs-ref gates (TITLE/MENU/SC/ZC/SP/SM
all try1, means 0.33–0.65) → 4×Down walk → SE-WALKED vs T47's surviving
xwd walked snap (Happiness-verified): **mean = 0.0472, p99 = 0** — the
same screen, pixel-identical up to animation; viewed: Select Event with
Happiness highlighted, `Rival` header, course map. EVENT_CROSS → My
Rules (static + orange bar y≈487/n≈8022). Rules closed loop (R1 departs
but stays static → UP×11 clamp-to-top → R2 departs + animates → race).
Rules exit goes **straight to racing** (no static pre-race hold on this
path — B04 proved it: race timer 00:00:04 twelve seconds after the
Rules exit). RACE_ENTRY try1 depart = 12.32 → `T48_DUMP_QUEUED
vsync=25544`, dump over vsyncs 25545–25552, F8 after the window.

Window ≈ race 00:00:08–00:00:12 (trigger ≈ race+4–8 emu-s; F8 at
00:00:17). "First ~5 s" approximately — stated plainly. The F8
(00:00:17, 8%, 43 MPH, 2ND/2) caught the rider largely behind a
foreground tree; the window itself is bracketed by live frames at
00:00:04 and 00:00:12 both showing the rider clearly with terrain, and
the dump's packets decode fully (§census below, replay HWSTAT
1,805 draws ≈ live 1,743).

Draws per vsync by path (1,743 G12_DRAW, all `path=1`, 0 ring misses):

| vsync | p1 pkts / bytes | p2 | p3 | p0 | draws (all PATH1) |
| --- | --- | --- | --- | --- | --- |
| 25545 | 1,520 / 1,817,104 | 0 | 0 | 0 | 218 |
| 25546 | 1,522 / 1,816,768 | 0 | 0 | 0 | 216 |
| 25547 | 1,508 / 1,804,064 | 0 | 0 | 0 | 216 |
| 25548 | 1,507 / 1,803,104 | 0 | 0 | 0 | 219 |
| 25549 | 1,481 / 1,793,088 | 0 | 0 | 0 | 216 |
| 25550 | 1,473 / 1,791,808 | 0 | 0 | 0 | 216 |
| 25551 | 1,482 / 1,798,016 | 0 | 0 | 0 | 221 |
| 25552 | 1,476 / 1,780,096 | 0 | 0 | 0 | 221 |

Race traffic ≈ 1.8 MB GIF bytes/vsync, all PATH1. Dump census v0:
1,520 xfers / 1,817,104 B, `paths=[3]` — **exactly the T48_PATHS row**;
per-vsync geometry ≈ 35 sprites + 629 tristrips + 277 trifans (≈940
prims), 72 IMAGE tags (~500 KB uploads), ~28k data kicks, 12 texture
TBP0s. Replay HWSTAT: 1,805 draws (avg 226) ≈ live 1,743 — packets
decode and execute; replay frames show HUD-only (missing pre-window
VRAM: course textures upload once at load, outside the 8-vsync window —
fidelity note, not a data gap: the packets hold the geometry).

Top (FBP, TBP0, PRIM, TME) tuples by count (8 vsyncs):

| FBP | TBP0 | PRIM | TME | n |
| --- | --- | --- | --- | --- |
| 0 | 15145 | 4 (tristrip) | 1 | 306 |
| 0 | 12777 | 4 | 1 | 280 |
| 0 | 14857 | 4 | 1 | 272 |
| 0 | 11433 | 4 | 1 | 202 |
| 0 | 13449 | 4 | 1 | 56 |
| 0 | 14953 | 4 | 1 | 48 |
| 0 | 14313 | 4 | 0 | 48 |
| 0 | 4352 | 4 | 1 | 32 |
| 0 | 12585 | 6 (sprite) | 1 | 31 |
| 0 | 13033 | 4 | 1 | 24 |

(Course-texture TBP0s; dump census tbp0s match.)

VU1 programs over the widened window (6,092 records, **100% end=ebit,
0 aborts**):

| stat | cycles | xgkicks/program |
| --- | --- | --- |
| min | 2 | 0 (1,143 programs); ≥1 (4,949 programs) |
| median | 554 | mean 1.60 |
| p99 | 11,158 | — |
| max | 23,540 | max 34 |
| **n > 65,536** | **0** | — |

Distinct start_pcs: 0x459 (1,137) / 0x44e (1,038) / 0x0 (729) / 0xd7
(423) / 0x10 (414) / 0xe (414) / 0x741 (351) / 0x257 (297) / rest —
course/rider object programs (hundreds to ~23k cycles, 0–34 XGKICKs).

Healthy-side reading: under real 3D race load the longest healthy VU1
program runs **23,540 cycles — 2.8× below the recomp's 65,536 budget**,
with a complete PATH1 draw set (1,743 draws, dump geometry complete).

BONUS (B04 full run, `t48b4-paths.txt`, 30,977 vsyncs boot→menus→~11k
race vsyncs): p2 = p3 = p0 = **0 for the entire run** — every GIF byte
on every screen flows through PATH1. p1 means: menus ≈ 0.43–0.52
MB/vsync, race ≈ 2.5–2.9 MB/vsync, course-load spikes to 3.6–4.3 MB;
race onset ≈ vsync 20000.

## T48-7. Gaps, overruns, and harness lessons

1. **Build budget overrun (3 builds vs ≤2).** Build 1 failed on a scope
   bug (GS globals landed in a function body); the retry failed on
   linkage (`static` on cross-TU globals) and exposed a real mapping
   error (PATH1 = Transfer idx3, not idx0 — the first build would have
   dropped all PATH1 traffic). Build 3 is clean (one benign pre-existing
   G13 warning). The mapping fix alone justified the extra build.
2. **Capture-run budget overrun (5 boots vs ≤3).** A ✓; B01 (0.5 s menu
   holds eaten on slow interp screens); B02 (blind retry double-advanced
   past SE — diagnosed from frames); B03 (walk holds too short at interp
   speeds + hlscan staging miss); B04 (reached animated racing but
   waited for a static pre-race screen that doesn't exist on this path —
   killed by WALL_CAP mid-race); B05 ✓. Each failure was a harness bug
   with a concrete evidenced fix, never a route stall; the route itself
   (nav→Happiness→Rules→race) worked from B02 on.
3. **Time box overrun (~5.7 h vs 5 h).** Value delivered for it: both
   captures + the B04 full-run census + a reusable closed-loop capture
   recipe (identity gates, Rules clamp loop, orange-bar probe).
4. **Patch repair path.** The first hook application had anchor re-add
   duplications in 3 VU hunks (caught in diff review before any build);
   the 3 VU files were reverted (no prior hunks there) and the fixed VU
   hunks applied via `t48-hook-vu.py`. Committed `t48-hook.py` is the
   corrected full recipe.
5. **Proof-run harness bug**: the stashed pre-patch binary needs
   `resources/` + `translations/` alongside it (without them it sits on
   a `Translation Error` dialog and boots nothing). Symlinked in
   `pre-t48/`.
6. **`verts=` is not batch totals** (§T48-3/5). No extra build spent;
   the dump is the geometry authority.
7. **A-run poll log lost** (first proof attempt reused the `t48a-poll.log`
   name; fixed mid-lane: UNPATCHED runs use `t48proof-poll.log`).
   A-run navigation evidence = gate passes + F8 + extracts.
8. **Capture config deviation** (`vuThread=false`, `EnableVU1=false`,
   §T48-2): guest semantics verified same-screen (Leg 2 + T47-ref
   scores); cycle numbers are interp-exact by construction.
9. **Vsync attribution skew**: EE-side VU records carry the GS mirror
   vsync (±1) — use window totals + distributions, not single-vsync
   program counts.
10. **B F8 rider occlusion** (tree at 00:00:17) + **replay HUD-only
    frames** (missing pre-window VRAM) — both stated with the
    bracketing evidence; neither affects the packet/log tables.
11. Bytesize byte use: dat-t48 25 MB + build +1 MB + dumps/logs on-box;
    retrieved text + 2 dumps + shots ≈ 45 MB. Well under the 15 GB cap.
    P-lane lease: claimed/released per the old reading, then released
    finally per the orchestrator's mini-only clarification (no contention
    caused — the file still held the T48 line at release).

## T48-8. Exact commands

Scripts (committed under `local/research/T48/`, also staged at
`/home/brad/pcsx2-g7/t48-*.sh|py` and `C:\Users\bradr\pcsx2-t4\`):

- `t48-hook.py` — the patch (one application); `t48-hook-vu.py`,
  `t48-fix1.py`, `t48-fix2.py` — documented repairs (§T48-7.1/4).
- `t48-apply.sh` — stash pre-patch SHAs + copies, apply.
- `t48-build.sh` / `t48-fix1build.sh` / `t48-fix2build.sh` — the 3
  builds (`cmake --build …/build --target pcsx2-qt pcsx2-gsrunner -j2`).
- `t48-setup.sh` — `dat-t48` copy + 2 ini flips + clean.
- `t48-replay.sh`, `t48-rerun.sh`, `t48-replay-results.sh`,
  `t48-diag.sh`, `t48-png.sh` — preservation leg 1.
- `t48-capA.sh` (`UNPATCHED=1` = proof run), `t48-capB.sh` (final v5
  shape) — captures; `t48-proof-retry.sh`, `t48-proof3.sh`,
  `t48-p3check.sh`, `t48-wnames.sh`, `t48-smoke.sh`, `t48-resfix.sh`,
  `t48-trfix.sh`, `t48-proofcmp.sh` — proof-run debugging trail.
- `t48-getA.sh`, `t48-extractA.sh`, `t48-extractA2.sh`,
  `t48-b4paths.sh`, `t48-finalext.sh`, `t48-stageB*.sh`,
  `t48-bracket.sh`, `t48-bframes.sh`, `t48-b02t.sh`, `t48-b03d.sh`,
  `t48-b04p.sh`, `t48-b04k.sh`, `t48-p3check.sh` — retrieval/diagnosis.
- `t48-anA.py`, `t48-anAB.py` (shared analyzer), `t48-hlscan.py`
  (orange-bar probe), `t48-probeRGB*.py`, `t48-mkdiff.sh` — analysis.
- Key one-liners: `cmake --build /home/brad/pcsx2-g7/pcsx2/build
  --target pcsx2-qt pcsx2-gsrunner -j2`; gsrunner replay
  `pcsx2-gsrunner -renderer vulkan -dumpdir … -logfile … -loop 1
  -noshadercache -surfaceless -ini …/g10-uncorrected.ini -- …gs`;
  boot `pcsx2-qt -nogui -slowboot -turbo -datapath …/dat-t48 -logfile …
  -- '…/inputs/SSX 3 (USA).iso'`.
- Analysis: `t48-anAB.py A|B`; dump census
  `local/research/G13/g13-census.py <dump>`; frame compare
  `local/research/T47`'s `t44-cropdiff.py` (on 16-bit xwd PPMs — note:
  the tool parses them as 8-bit; scores remain self-consistent for
  gating but are not photometric).

## T48-9. Receipt paths + recommendation

- Repo (this commit): `local/research/T48/REPORT.md` (this file),
  `t48-patch.diff`, hook/fix/capture/analysis scripts, line extracts
  (A: vu1/paths/draw/vsync/markers; B: vu1/paths/draw/vsync/markers;
  B04 full-run paths), poll logs (t48b B05; t48proof), markers.
- Share mirror `/Volumes/share/ssx3/ps2x-t48/`: both dumps (`.gs.zst` +
  `.gs` SHAs §T48-1), all F8/keyframe shots, REPORT.md, t48-patch.diff.
- Internal workdir `~/dev/ssx3-work/T48/` holds the same + intermediates.
- Bytesize residue (documented, all under byte cap): `dat-t48/`,
  `pre-t48/` (+2 symlinks), `t48-frames*/`, `emulog-t48*.txt`,
  `t48-*.sh|py`, `t48a/b-*.txt`, `t48-patch.diff`, `t48-full6.diff`.

Recommended next action (orchestrator): hand the A+B tables, both dumps
and the B04 full-run census to the E-brief for the H1/H2/H3 verdict —
healthy VU1 programs top out at 23,540 cycles with complete PATH1 draw
sets at both screens. No follow-up T-lane work is queued by this brief;
the capture recipe (`t48-capB.sh` closed-loop shape) is reusable for any
further PCSX2 reference screens.
