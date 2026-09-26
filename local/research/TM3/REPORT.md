# TM3 — rider integrator + first 120 Hz conversion probe

Worker: Muse Code, brief `local/muse/prompts/TM3.md`, 2026-09-26 ~00:40–01:10 EDT.
Research only; nothing ships. No push. No `docs/` edits.

## Outcome

**Part A:** the live position `[obj+0x110]` (`obj=0x1465c40`) is written by **two
alternating `pos += delta` integrators** (`sqc2` at `0x1380b4` in `sub_00137D18`,
56 stores, and at `0x13e0dc` in `sub_0013D818`, 45 stores; 101/101 VBlanks, one
store each), on EE thread 1, **after** the app update returns (not inside
`0x2306b8`). No `A+0x14`/`A+0x10` use in either owning function or its direct
caller; the delta is precomputed without direct manager access.

**Part B:** the `PS2X_TM_RATE120` probe arms (`A+0x10=120`, `A+0x14=1/120`,
`A+0x24=2.0`, `A+0x28=0.0`) and yields exactly 2 producer records, 2 consumes
and 2 app updates per VBlank with 1 render. The route still reaches the race.
Motion runs at **1.89× per VBlank** (full steps, not halved) and the HUD clock
at **2× per VBlank** (hard-coded `/60`); audio counters are identical. First
unconverted consumers: the rider integrator step and the HUD `/60` formatter.

## Part A — the integrator

`obj=0x1465c40` (`tm3-obj` line, tick 1800, src `0x1218b4`, dst `0x5409c0`;
`local/research/TM3/tm3-obj.txt`). Watch `0x1465D50/54/58/5C` ticks 1799–1899
(TM1 lines 1800–1900): 404 lines = 101 stores, one per VBlank, all width=16.

| What | Writer 1 (stores 1–56) | Writer 2 (stores 57–101) |
| --- | --- | --- |
| Guest PC | `0x1380b4`: `sqc2 $vf5, 0x110($v1)`, `vf5=[v1+0x110]+[sp+0x60]` | `0x13e0dc`: `sqc2 $vf5, 0x110($v1)`, `vf5=[v1+0x110]+[sp+0x50]` |
| Owning `sub_` | `sub_00137D18` `[0x137d18,0x138640)` | `sub_0013D818` `[0x13d818,0x13f178)` |
| Caller (static) | `0x136eb8` in `sub_00136E98` (`jal 0x137d18`, `a0=s0`) | `0x11143c` in `sub_00111408` (`jal 0x13d818`) |
| Caller +1 (static) | `0x11145c` in `sub_00111408` (`jal 0x136e98`) | `0x1216e8` in `sub_001216E0` (`jal 0x111408`) |
| Thread / sp | 1 / `0x1fffcb0` | 1 / `0x1fffc50` |
| `$ra` at store | `0x137f94` (stale: last interior `jal` return in same func) | `0x13dc54` (stale, same reason) |
| Inside `0x2306b8`? | No: every store triple follows its `tm1-update` return line | Same |
| `A+0x14`/`A+0x10` on path | Not found in `sub_00137D18` / `sub_00136E98` (no `gp+0x2a74` ref, no 1/60 literal) | Not found in `sub_0013D818` / `sub_00111408` (same negatives) |

Both chains converge on `sub_00111408` (two call sites, `0x11143c`/`0x11145c`);
the 56/45 split is a clean mode switch mid-window (store 57 ≈ tick 1855), not
alternation. Values match TM2's snapshot stream bit for bit (first store
`3f80000047baab34c731bc38453370b9`). Overlap note: the 4th watch window
`[0xD5C,0xD64)` also caught 369 lines of `obj+0x120` stores (adjacent field,
not the target; listed in Gaps).

## Part B — the probe

Probe arms once at `0x316da8` (`tm3-probe-armed A=0x4c9428 wrote=1`;
`local/research/TM3/tm3-probe-arm.txt`); stock shows no probe line. FR1-R1 to
t2400, det, mini, tap + Part A watch + dumps 1800/2100/2400.

| Observable (per VBlank, ticks 1800–2400) | Stock (`tm3-stock`) | Probe (`tm3-probe`) |
| --- | --- | --- |
| Producer records (`dv_pslot`/`dv_ringp`) | 1 / 1 (600/600 steady) | 2 / 2 (599/600; 1 boundary) |
| Consumes (`dv_cons` attempts / `dv_consOK`) | 3 / 1 | 4 / 2 |
| App updates (`dv_upd` / `dv_updRet`) | 1 / 1 (601 updates) | 2 / 2 (1202 updates; 1 susp at tick 1853) |
| Renders (`dv_rnd` / `dv_rndOK`) | 1 / 1 | 1 / 1 |
| `A+0x10` / `A+0x14` / `A+0x24` / `A+0x28` | 60 / 1/60 / 1.0 / 0.0 | 120 / 1/120 / 2.0 / 0.0 |
| `A+0x20` / `A+0x34` (controls) | 12 / 0 | 12 / 0 (unchanged) |
| `A+0x1c` at 1800/2400 | 1750 / 2350 (+1/VB) | 3480 / 4680 (+2/VB) |
| Rider path 1800→2400 (601 `tm1-vblank` samples) | 7692.8, mean **12.82**/VB, max step 153.7 (teleport ~2109) | 14526.7, mean **24.21**/VB (1.89×), max 184.5 |
| Rider per HUD second | 769.3 (10 HUD-s over window) | 726.3 (20 HUD-s; 0.94× stock) |
| HUD clock 1800 / 2100 / 2400 (frames viewed) | 00:00:01 / 06 / 11 | 00:00:02 / 12 / 22 (2× slope) |
| SND final (`ticks/counter/cid0/dmq/done/setdma/tagbufs`) | 3666/0xf3b/531/531/531/4261/3665 | identical (EE cycle +0.0002%, underruns +0.27%) |
| Route reaches race? | Yes (2ND/2, race HUD ~1714) | Yes (2ND/2, race HUD; ahead: airborne at 1800) |
| det-hash vs `a3efbfe-…-a5f2f32d` | IDENTICAL | DIFFER (first at tick 39; intended) |

`[obj+0x110]` stores in probe window (ticks 1799–1899): 216 over 101 VBlanks
(94×2, 3×3, 3×4, 1×7 per VBlank). Same two integrators dominate
(`0x1380b4`×103, `0x13e0dc`×81) plus mode-dependent extras: `0x113950` (copy in
`sub_00113648`)×18, `0x138398` (`vsub` correction in `sub_00137D18`)×6,
`0x10655c`×4, four singletons. `obj` itself is unchanged (`0x1465c40` both).

Which consumers follow dt: **none observed**. Motion takes ~full steps per
update (1.89×/VBlank, not 1.0×); the HUD formatter still divides by 60 (2×/VB,
not 1×/VB). Audio correctly ignores the probe (own timebase, counters
identical). First unconverted consumers: the rider `pos += delta` step and the
HUD `/60` formatter (TM2's predicted 2× clock confirmed).

## Exact commands, pins, SHAs

- Worktree `~/dev/ssx3-work/TM3/PS2Recomp`, branch `tm3` (never pushed):
  fork `ssx3` tip `fb28d99` (= `ls-remote` tip, still current) + `364f56e`
  (cherry-pick TM1 `449026e`) + `406281b` (cherry-pick TM2 `86388ec`) +
  `e9affcf` (`[TM3] Obj logger (tm3-obj) + PS2X_TM_RATE120 probe`, 3 files).
  Runner-dir check `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner`
  empty (before and after `e9affcf`).
- Build 1/1 (shared by both parts): `local/tooling/build/mac_build.sh
  …/TM3/PS2Recomp …/TM3/build-det-diag --det --diag` → runner
  `dc8256208fe991747e71fb894839dcb40aa0241b543df28127c7aec41977a3bb`
  (2 reads match), 416,375,376 B, 70 s wall (hot ccache).
- Boot A1/2 `tm3-obj`: `ssx3_boot.py --host mini --mode det --backend parallel
  --runner …/build-det-diag/…/ps2EntryRunner --label tm3-obj --out
  …/TM3/tm3-obj --route fr1r1 --stop-tick 2400 --sound on --wall 600 --env
  PS2X_TIMING_TAP=1` → target, t2400, 66.0 s, slot 2 (held), log 1,687,440 B.
- Boot A2/2 `tm3-watch`: same + `--env PS2X_DIAG_WATCH=
  0x1465D50,0x1465D54,0x1465D58,0x1465D5C --env PS2X_DIAG_WATCH_TICKS=
  1799-1899` → target, t2411, 64.0 s, slot 2, log 1,790,059 B, 404 target +
  369 adjacent watch lines.
- Boot B1/2 `tm3-stock`: A2 + `--dump-ticks 1800,2100,2400` → target, t2408,
  64.4 s, slot 2, log 1,116,805 B.
- Boot B2/2 `tm3-probe`: B1 + `--env PS2X_TM_RATE120=1` → target, t2404,
  64.4 s, slot 2, log 1,312,056 B.
- Slot: mini slot 2 held across all four boots (`p_lane_lease.py claim tm3-A1`
  → 2, `SSX3_HELD_SLOT=2`, released after B2); waited out VR2-H15 (exclusive
  speed hold) and MT1-C2/B2/A2 (exclusive) before claiming.
- Compares: `baseline.py compare --key
  a3efbfe-det-fr1r1-t2400-snd1-1x-a5f2f32d --cand …/TM3/tm3-{obj,watch,stock}`
  → all three IDENTICAL (ticks 1–2400 + snd/coverage); `tm3-probe` → DIFFER
  from tick 39 (intended behaviour change).
- Receipts: `tm3-obj.txt` (1 line), `tm3-watch-lines.txt` (404 canonical
  `[diag:watch]` lines for `0x1465d50`), `tm3-probe-arm.txt` (1 line).
  Full logs/frames: `~/dev/ssx3-work/TM3/tm3-{obj,watch,stock,probe}/`
  (outside git); analysis one-liners in `/tmp/tm3_motion.py`,
  `/tmp/tm3_counts.py`, `/tmp/tm3_pwv.py` (scratch, outside git).
- Counts: 601/601 `tm1-vblank` in all four boots; 601 `tm1-update` stock
  (1 cosmetically mangled by `[frame:dump]` prefix, value intact), 1202 probe;
  zero `tm1-capped`/`tm1-badptr`; no `tm3-probe-refused`.

## Gaps and next

- The integrator delta (`[sp+0x60]`/`[sp+0x50]`) source — velocity × dt vs
  per-step constant — is untraced; no manager/dt access in the two owning
  functions or their direct callers, so the dt boundary (if any) sits higher
  (candidates: `sub_00111408` inputs, `sub_001216E0`, or velocity init).
- `obj+0x120` (overlap-captured): stock writers `0x11e078`/`0x11e0c0`/
  `0x121ef8` (+2 `0x13e0dc`-family); role unidentified (small-magnitude
  128-bit, not position-scale velocity).
- Probe extras `0x113950` (copy), `0x138398` (`vsub`), `0x10655c` and four
  singletons are mode-dependent one-offs (18/6/4/1 stores); not attributed to
  game events.
- Within-VBlank order integrator-vs-snapshot in probe (2 stores vs 1 copy)
  and the tick-1853 suspended update's real return are unobserved (tap gaps).
- HUD `/60` formatter still not located (TM2 negative stands); the −1690
  race-start base in probe terms (≈3360 for `/60`) is inferred from two clock
  points, not found as a stored word.
- Suggested next: trace the delta source one level up (watch a velocity/
  state input to `sub_00137D18`/`sub_0013D818`), then a rank-3 brief converting
  the integrator step + HUD formatter with normal-time acceptance per RV6 §5.

## Orchestrator gate (2026-09-26)

**Pass.** Integrators named (`0x1380b4` / `0x13e0dc`, `pos += delta`, after the app update, no manager
dt/rate on the path); the RV6 probe gives exactly 2 updates per VBlank and still reaches the race, but
motion takes full steps (1.89×/VBlank) and the HUD divides by 60 (2×). So the manager's rate/dt are not
the physics timestep: a real 120 Hz simulation needs the per-update step constants found and halved
coherently. **Next (TM4, queued, low priority while speed is the bottleneck):** census of where the
rider's `delta` comes from (velocity × a fixed step, 1/60 literals, per-update friction/accel constants),
then one coherent probe. Paused until the mini's speed holds (VR2/MT1) free up; no device work.
