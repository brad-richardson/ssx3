# TM1 — live simulation-step chain in a race

Worker: Muse Code, brief `local/muse/prompts/TM1.md` (+ RV7 anchors),
2026-09-25 ~23:00–24:00 EDT. Observation only; no behaviour change, no fix.
No push. No `docs/` edits.

## Outcome

RV6's static chain is **confirmed live and metronomic** in the race window
(ticks 1800–2400, FR1-R1, Happiness): every VBlank delivers exactly 1 worker
wake → 1 produced record → 1 successful consume → 1 active-app update →
1 successful render, with all RV6 addresses bit-exact. All three RV6
predictions hold; the render-coupled, substep and variable-time alternatives
are rejected for the exercised path. Two first-order findings for the 120 Hz
program: (1) the rider triple at `0x5409c0` moves per VBlank but is
**bit-stable across all 601 app updates** — the live writer is not the app
update; (2) the Metro `bc1t` at `0x230704` is never taken and `A+0x34` stays
0 on this route, so the community Metro NOPs are a no-op equivalent here.

## Observed chain (all 601/601 VBlanks, ticks 1800–2400)

| Stage | Live value | RV6 static | Match |
| --- | --- | --- | --- |
| A (`[gp+0x2a74]`) | `0x4c9428`, constant | object at `0x4a5b64` | addr class ✓ |
| A vtable (`A+0x5c`) | `0x47d9c8` | `0x47d9c8` | ✓ |
| Active app (`A+0x0`) | `0xcbfb20`, constant | table at `0x47d110` | ✓ |
| Active vtable | `0x47d110` | `0x47d110` | ✓ |
| Update target (slot `+0x34`) | `0x2306b8`, all 601 site calls | `0x2306b8` | ✓ |
| Render target (slot `+0x3c`) | `0x22b008`, all 601 site calls | `0x22b008` | ✓ |
| Consumer (mgr slot `+0x34`) | `0x227e98`, all 1803 site calls | `0x227e98` | ✓ |
| Producer (mgr slot `+0x3c`) | `0x227f58`, all 601 site calls | `0x227f58` | ✓ |
| Resync (mgr slot `+0x2c`) | `0x227e68`, 0 calls | `0x227e68` | ✓ (never needed) |
| Ring obj (`[gp-0x850]`) | `0x618b60`, 2 channels | ring of 30 | ✓ |
| `A+0x10/0x14/0x20/0x24/0x28` | 60 / 1/60 (`3c888889`) / 12 / 1.0 / 0.0, const | same | ✓ |
| `A+0x2c/0x30` (smoothed) | 59.9999504 / 0.9, const | not physics dt | ✓ |
| `A+0x34` render mode / `A+0x58` | 0 / 0, const | mode 0 / normal | ✓ |
| `A+0x18` wrapper / `A+0x1c` update cnt | +1 / +1 per VBlank, exactly | counters | ✓ |
| Ring cons/prod | +1 / +1 per VBlank, `(prod-cons)%30 = 1` always | modulo-30 | ✓ |

## Counts per VBlank (steady state; 600/600 intervals, see boundary note)

| Observable | Per VBlank | Total |
| --- | --- | --- |
| Producer wrapper entries (`0x317348`) | 1 | 601 |
| Producer slot calls (site `0x3173bc`) | 1 | 601 |
| Ring producer calls (`0x326b88`) | 1 | 601 |
| Consumer calls (site `0x3171d0`) | 3 | 1803 |
| Consumer successes (v0≠0) | 1 | 600 obs. + 1 boundary (note) |
| Active-app update entries (site `0x3171b4`) | 1 | 601 |
| Update sync returns / suspensions | 1 / 0 | 600 obs. + 1 boundary / 0 |
| `$s1` at update/consume sites (max) | 1 | bound 12 never approached |
| Render calls (sites `0x317208`+`0x31723c`) | 1 | 601 |
| Render successes (v0≠0) | 1 | 600 obs. + 1 boundary |
| Resync calls (`0x227e68`) | 0 | 0 |
| Metro helper calls (`0x2ee400` from `0x2306ec`) | 1 | 601 |

Boundary note: the tap arms at tick 1800, so interval (1799,1800] counts
1 unarmed update/consume/render entry whose post lands outside the observed
posts (600 observed sync posts + the 601 update lines all `ret=sync`). This
is the arming edge, not a model violation: `A+0x1c` deltas are exactly 1 on
all 600 sample steps, and every armed update has `s1=1`, `tgt=0x2306b8`.

The 3-consume microstructure (inferred from counts + code shape, not
per-call order): drain pass 1 (success → update → terminating fail) plus a
second drain attempt that fails on the empty ring, then 1 render success
resets `$s1`. Both consistent orders (fail-first vs fail-last) fit; the tap
logs counts, not within-interval order (gap).

## Which prediction holds (RV6 §5)

1. **One produced record per wrapper wake at multiplier 1: HOLDS** (601/601:
   wrap=pslot=ringp=1, ring steps +1, accumulator exactly 0).
2. **One app update per successful consume below the cap: HOLDS** (600/600
   steady-state intervals; `$s1`=1 ≪ 12; resync never called).
3. **No dt inflation when rendering lags: HOLDS with a caveat** — dt is
   bit-constant (`3c888889`) and render succeeds every VBlank, so the lag
   path is never exercised in these controls. Per RV6 §5, overload behaviour
   is not inferred; it needs a separately budgeted guest-load perturbation.
- **Render-coupled updates: REJECTED** — updates follow ring-drain success,
  render follows updates (mode 0, `$s1` reset each VBlank).
- **Extra physics substeps in one app update: REJECTED for `0x5409c0`** —
  the triple is bit-identical before/after all 601 updates (see below).
- **Variable-time consumers: REJECTED** — dt/mult/acc bit-constant, all
  counts metronomic, EE step 4915268–4915330/VBlank (nominal 4915200;
  +0.002% matches RV6 §4's 16,667 µs period).

## RV7 anchors (observation only, no patches applied)

| Anchor | Live behaviour, ticks 1800–2400 |
| --- | --- |
| Metro `[[this+0x84]+0x10]` (mcount) | 1 every update (< 2: conditional path always; the unconditional mode-1 store at `0x2306e8` never fires) |
| Metro `0x2ee400(6)` f0 return | exactly 0.0 all 601 (vs 0.9: `bc1t` at `0x230704` never taken) |
| `A+0x34` before → after each update | 0 → 0 all 601 (conditional store at `0x230710` fires, writing 0) |
| `0x317180/0x317184` `$s1` vs bound `A+0x20`=12 | `$s1`=1 always; bound never hit; resync 0 calls |
| Aspect scalars `0x622600/604` | `0x3f400000,0x3f800000` = 0.75, 1.0, constant (game's own anamorphic values) |

Consequence: on this route the Metro NOP pair would suppress a store that
only ever writes the already-prevailing 0 — a no-op equivalent, not a
timestep change. The 2P `$s1`+2 patch would raise `$s1` to 2/update, still
far below the catch-up bound of 12 (its mode-1 render-threshold effect is
moot in mode 0).

## Rider position: the writer is not the app update

- Per-VBlank motion is smooth and alive: mean step 12.8, path 7693 units
  over 600 VBlanks; `(2871,-45500,95574)` → `(8196,-42985,91071)`.
- `posb==posa` for **all 601/601** updates: `0x5409c0` never changes during
  `0x2306b8`, sync returns included. The integrator writing the observed
  triple runs outside the app update on this route (other thread/function,
  VU0 op, or render-time copy — unattributed here; write taps need
  DIAG_TAPS, which is off on bradflix builds).
- One discontinuity: ticks 2109→2110 jump 153.7 units (~10× normal) with all
  chain counters undisturbed — a scripted/teleport move on the input-free
  route, not a substep burst.

## HUD race clock: not found as a stored word

- Displayed clock (viewed frames): tick 1800 → 00:00:01, tick 2100 →
  00:00:06, tick 2400 → 00:00:11. Slope exactly **1 s per 60 updates**
  (`updcnt` 1750/2050/2350; HUD = (`updcnt`−1690)/60).
- Census: active-app header words constant (`0x47d110,0,0,0x5bc700`); every
  `A` field is either constant or a 60 Hz counter. No 1 Hz word in the
  sampled state. Verdict: **not found** — the HUD clock is consistent with
  derivation from the update counter at render time (or a store outside the
  census). Writer attribution would need memory-write taps (DIAG_TAPS,
  exceeds this lane's build cap).

## Tap overhead and non-perturbation

- det-hash ticks 1–2400 + snd/coverage **IDENTICAL** to
  `a3efbfe-det-fr1r1-t2400-snd1-1x-a5f2f32d` for BOTH the unset control
  (required) and the tap-armed run (bonus): guest perturbation is zero.
- Repeat: two tap runs byte-identical over all 1203 tap lines except the
  host `wall_ms` field (the only run-varying field by design).
- Walls (paced diagnostic boots, not speed numbers): tap 99.8/100.3 s vs
  unset 97.0 s; tap log +25 KB (1203 lines) in a ~1 MB boot.log, far under
  the 16 MB boot cap and the 32 MB tap cap (60k lines / 32 MB caps never
  near: 1203 lines / ~0.8 MB).
- Unset boot emits 0 tap lines. No `tm1-badptr`, no `tm1-capped`, no lost
  rows (601/601 ticks), no foreign-lease wait (slot 1, all slots free).
- Frame FNVs: tick 1800 matches across repeats (`fa1afc90`); 2100/2400
  differ between guest-identical runs — known present jitter (SS1/SS2
  precedent), not divergence.

## Exact commands, pins, SHAs

- Worktree `~/dev/ssx3-work/TM1/PS2Recomp`, branch `tm1` =
  fork `ssx3` `173b31f` + `cdaa331` (`[TM1] Observation-only
  PS2X_TIMING_TAP…`, 3 files, +599). Never pushed. Runner-dir check
  `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner` empty.
- Tap code: `ps2xRuntime/include/ps2_tm1_tap.h` (new) + hook sites in
  `ps2_runtime.cpp` (`dispatchGuestBranch` pre/post) and `EeScheduler.cpp`
  (`VBlankStart` → `noteVBlank`). Env: `PS2X_TIMING_TAP=1`, window
  1800–2400, caps 60k lines / 32 MB.
- Transfer (VR2/SS2 recipe, nothing to GitHub): `git bundle create
  /tmp/tm1.bundle 173b31f..tm1`, scp to `HS1/tm1.bundle`, bradflix
  `git fetch … tm1:refs/tm1/tap` =
  `cdaa3313b868aee5fa8aaa5f6b5efa1e05122ae8`.
- Build 1/3: `local/tooling/build/bradflix_build.sh cdaa331… tm1-det
  --det` → runner `fddb902884a6c4e34e0f2d205feb0b3c659b0cdd4025acf682a8c231caec6d49`
  (2 reads match), 175,851,912 B, 60 s wall (hot ccache), image
  `d124af4da093`. Inputs verified by the script (codegen/ELF/ISO/VU1/PGS
  `464f263`/Granite `166ba21a`).
- Boots 3/4 (all `--host bradflix --mode det --backend parallel --runner
  dev/ssx3-work/HS1/tm1-det/ps2xRuntime/ps2EntryRunner --stop-tick 2400
  --wall 600`, FR1-R1, sound on):
  `tm1-tap-a` (+ `--dump-ticks 1800,2100,2400 --env PS2X_TIMING_TAP=1`):
  target, t2401, 99.8 s, log 1,015,239 B;
  `tm1-tap-b` (same): target, t2401, 100.3 s, log 1,015,449 B;
  `tm1-unset` (no env/dumps): target, t2404, 97.0 s, log 989,945 B.
- Compares: `baseline.py compare --key
  a3efbfe-det-fr1r1-t2400-snd1-1x-a5f2f32d --cand
  ~/dev/ssx3-work/from-bradflix/tm1-{unset,tap-a}` → both IDENTICAL
  (hash 1..2400, snd/coverage).
- Receipts: `tm1-lines-a.txt.gz` (1203 canonical tap lines, sha256
  `72ca1eac…9c7df`), `analysis.txt` (this report's census program output).
  Full logs/frames: `~/dev/ssx3-work/from-bradflix/tm1-{tap-a,tap-b,unset}/`
  (outside git). Local syntax pre-check: both edited TUs pass
  `-fsyntax-only` against the base compile commands.

## Gaps and next

- Rider-write attribution: which code writes `0x5409c0` between updates
  (thread/function/VU0/render) needs a DIAG_TAPS write-tap build — the
  rank-2 probe's true physics boundary depends on it.
- HUD-clock writer: not found as a stored word (see slope evidence above);
  same write-tap requirement for a definitive answer.
- Within-VBlank micro-order (producer wake vs drain vs render sequencing)
  needs per-call stamps; counts alone fit two orders.
- Overload/backlog behaviour unexercised (no missed VBlank in controls);
  RV6's queued guest-load perturbation stands.
- Suggested next: a bounded write-tap lane (DIAG_TAPS build, mini or a
  bradflix DIAG exception) attributing `0x5409c0` + HUD-timer writers over
  ~60 race VBlanks before any rank-2 rate experiment.
