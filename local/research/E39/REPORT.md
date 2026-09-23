# E39 report — VIF1 MPG drop-path hunt: no drop fires in 0–1377, all 37,596 copied

Brief `local/muse/prompts/E39.md`. Tables + receipts; the orchestrator decides.
Read first: `AGENTS.md`, `local/AGENTS.local.md`, `local/research/E38/REPORT.md`,
`local/research/T49/REPORT.md` §T49-5.

## Outcome

- **No drop path fires anywhere in vsyncs 0–1377 (menus through Select
  Character settled): 37,596 MPG records, ALL `copied`; zero `drop_addr`,
  zero `drop_partial`, zero `clipped`. Per the brief stop rule: no fix.**
- No MPG carries PCSX2's `40000048` (slot 2) or `400000f2` (slot 8). Every
  dest=0 upload carries slot 2 = `81d26b7c` (our LQI) — confirming the
  orchestrator's fact that PCSX2's slots 2/8 come from an MPG the game sends
  PCSX2 but never sends us (or sends with bytes our walker never delivers;
  the walker/chain side, not the MPG handler, remains suspect).
- Delivered: dev-only `PS2X_VIF_MPG_LOG` (+`_FROM`/`_TO`, 20k cap,
  flush-every-128) + full-imm fix for the E37/E38 trace's `imm & 0x1FF`
  display alias. 8 new unit tests; suite **491/491** flags-unset from the
  fork root. One fork commit, ff-pushed. Flags-unset boot = E32a exactly.
- A2 side-evidence (no fix, so no change expected or seen): 0x10/0x40 first
  pairs still `LQI`/non-branch with 4 arrivals @0x418 (identical to E38);
  settled stats band identical to E33/E37/E38 down to VU cycles.

## Commits

Fork `~/dev/PS2Recomp`, branch `ssx3`:

| Commit | Subject |
|---|---|
| `0e9b5d0` | [E39] VIF1 MPG upload log + full-imm trace display + tests |

Base `7f022ed` (E38 tip). Pushed `7f022ed..0e9b5d0` (`git ls-remote fork ssx3`
= `0e9b5d0…`); runner-dir gate `git diff --stat 14b1e5cb ssx3 --
ps2xRuntime/src/runner` empty. Suite 491/491 before commit and before push.

## Diff summary

- `ps2xRuntime/include/ps2_vif_mpg_log.h` (new): header-only dev-only logger
  modeled on `ps2_gfx_stats.h` / `ps2_vu1_entry_trace.h` (env gate, FROM/TO
  window on the GS vsyncTick, 20k cap, `configureForTest`/`clearForTest`).
  Per MPG: vsync, full imm, num, linear dest byte range, outcome, available
  payload bytes, FNV-1a/32 of the available payload, slot-2/slot-8 lower+upper
  words under the PCSX2 masked mapping (`(imm*8) & 0x3FFF`, per-instruction
  wrap; `-` = not covered, `short` = covered but bytes missing from this
  buffer). Flush every 128 lines (below).
- `ps2xRuntime/src/lib/ps2_vif1_interpreter.cpp` (MPG arm only): outcome
  classification before the copy (**copy semantics byte-identical**);
  trace `addr` prints the full imm (was `imm & 0x1FF`, the E38 display alias).
- `ps2xTest/src/ps2_vif_mpg_log_tests.cpp` (new, `Ps2VifMpgLog`, 8 tests),
  registered in `src/main.cpp`, listed in `ps2xTest/CMakeLists.txt`.

## Tests (`Ps2VifMpgLog`, all pass; suite 491/491 = 483 E38 + 8 new)

Off-by-default; FNV-1a vectors (empty → `811c9dc5`, `a` → `e40c292c`);
slot-offset wrap (incl. 16K wrap slot 2047 → 0); copied (code lands + exact
line match incl. fnv/slots); drop_addr imm=2048 (code untouched, full imm
logged, would-write slot words under masked mapping); drop_partial (code
untouched, `slot8=short`); clipped imm=2047 (head lands, no wrap to slot 0);
FROM/TO window filters vsyncs.

## Boots (Mac mini, E32-build; E33 vsync route, PS2X_SKIP_MOVIE=1)

| Boot | Env | Result |
|---|---|---|
| e39a (A) | wall 300, snap 2.0, MPG 0–1400 | wall-bound 302.9 s, rc 0, tick 1377; 19,982 MPG lines on disk (see cap note) |
| e39a2 (A2) | wall 300, snap 2.0, MPG 828–1400, stats 1200–1500, entry 0x40,0x10 @1300 | wall-bound 300.5 s, rc 0, tick 1377; 17,614 MPG lines, 177 stats lines 1200–1376, both entry blocks @1300 |
| e39eq | flags-unset, wall 120 (`e32_boot.py`) | EQUIVALENT to E32a: park pc=`0x3b1028`, final `fnv1a=fd889dc5` |

Runner SHAs (two matching reads each): e39a `50da984e…5a45b`; e39a2/e39eq
`fa7d4e44…f32378` (rebuild after the flush tweak; tweak is log-only).

Cap note (read before citing line counts): the 20k cap tripped 14 lines into
vsync 828 in Boot A (19,968 + 14 written = 20,000). The wall-time SIGTERM
skips static destructors, so the final stdio buffer never flushes: 18 lines
lost in A (last line truncated mid-line). Fix: flush every 128 lines — A2
loses only its final partial line at vsync 1377. All counts below are
on-disk `grep -c` values; outcome ratios are unaffected (the cap/loss are
outcome-blind).

## Step-2 table: MPG outcomes, vsyncs 0–1377 (A: 0–828, A2: 828–1377)

| Outcome | A (0–828) | A2 (828–1377) | Union |
|---|---|---|---|
| `copied` | 19,982 | 17,614 | 37,596 |
| `drop_addr` (a) | 0 | 0 | 0 |
| `drop_partial` (b) | 0 | 0 | 0 |
| `clipped` (c) | 0 | 0 | 0 |

Non-`copied` rows: none (nothing to list). Carriers of `40000048` at slot 2
or `400000f2` at slot 8 (copied or not): **none in either boot**.

Supporting cuts (both boots):

- Full-imm range: max imm **1792** (num=193, dest=14336–15880, copied) — no
  imm ≥ 2048 anywhere, so path (a) is structurally absent in 0–1377.
- dest=0 uploads (2,498 in A; same shape in A2): every one carries
  slot2=`81d26b7c 000002ff`, slot8=`8000033c 01d214c5`, FNV `6a82dc60`
  (num=0, 2048 B payload, identical bytes every vsync).
- Rate ~24 MPGs/vsync (32/vsync at the SC screen); the SC-screen settle does
  not change the outcome distribution.

## A2 side-evidence (unchanged state, for the record)

- Entry blocks @1300: 0x10 → 250 pairs, 4 arrivals @0x418, first pair `LQI
  vf18,vf13` (`lo=81d26b7c`, vi13 `d549→d54a`); 0x40 → 244 pairs, 4 arrivals,
  first pair non-branch — **pair-identical to E38**.
- Settled band (1374–1376): `mscal=583 mscnt=0 vu_cycles=32645598
  vu_exhausted=498 vu_maxcyc=65536 xgkick=85` — **identical to E33/E37/E38
  down to cycles**.
- SC frames from A and A2 are byte-identical to each other
  (SHA `41cca09c…be057`, Zoe settled, viewed by eye).

## Frames (paths + SHAs, viewed by eye)

| Point | File | SHA256 | Shows |
|---|---|---|---|
| A+A2 Select Character settled | `local/research/E39/e39a2-sc.png` (= A snap-0301.19s = A2 snap-0299.15s, byte-identical) | `41cca09c…be057` | Zoe name+bars+silhouettes (one orange), mountain backdrop, **no 3D rider model** — same as E38 SC |

## Gaps / notes

- The 0–1400 window asked for is covered 0–1377 (boot ends at tick 1377;
  vsyncs 1378–1400 never execute). Union double-counts ~14 MPGs at vsync 828
  (A's cap-trip point overlaps A2's window start).
- MPG payload bytes vs PCSX2 ground truth still uncompared (T49 logs no
  payloads); with zero drops, the divergence is upstream of the MPG handler
  (chain construction / REF ADDR path / EE-side state) — E38's redirect stands.
- In-vsync MSCAL order (0x10 run vs 0x12B8 upload) still unknown.
- Flush-every-128 loss bound is untested by unit test (only observable under
  SIGTERM kill); verified empirically A→A2 (18-line loss → 1-line loss).
- Bytes: E39-run ~210 MB (frames ×2 boots dominate); internal total 27.0/200
  GB cap. 3 launches used (brief: ≤4 boots +1 retry).

## Exact commands

```
cmake --build ~/dev/ssx3-work/E32-build -j8   # fork ssx3 @ 0e9b5d0
env -u PS2X_SKIP_MOVIE -u PS2X_PAD_SCRIPT ~/dev/ssx3-work/E32-build/ps2xTest/ps2x_tests  # 491/491 (from ~/dev/PS2Recomp)
python3 local/research/E39/e39_boot.py --label e39a --wall 300 --snap 2.0 --mpg-from 0 --mpg-to 1400 --script "<route>"
python3 local/research/E39/e39_boot.py --label e39a2 --wall 300 --snap 2.0 --mpg-from 828 --mpg-to 1400 --stats-from 1200 --stats-to 1500 --entry-pcs 0x40,0x10 --entry-vsync 1300 --script "<route>"
python3 local/research/E32/e32_boot.py --label e39eq --wall 120
git push fork ssx3  # 7f022ed..0e9b5d0 (runner-dir gate empty)
```

(`<route>` = E33 vsync string, as in E38.)

## Recommendation (orchestrator decides)

No MPG fix: all three named drop paths are empirically dead in 0–1377, and
no upload in the window carries the missing B words. Keep the logger (zero
measured behavior change, EQ-clean) for future lanes. The missing-slots-2/8
mechanism is upstream of the MPG handler — E38's ordered redirect stands:
(1) MPG **payload** divergence (needs PCSX2-side payload ground truth, T49
lacks it); (2) in-vsync MSCAL **order** (timestamp 0x10 runs vs the 0x12B8
upload); (3) REF ADDR translation / EE chain construction from diverged
state. Do not run Boot B on this lane (stop rule); the race question is
unchanged from E38.
