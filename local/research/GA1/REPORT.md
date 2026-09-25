# GA1 Part 1 — GIF arbiter drain-sort inversions: measurement (zero found)

Worker: Muse Code, brief `local/muse/prompts/GA1.md` (review
`docs/research/review-2026-09-25-fable.md` §1 suspect 1, Part 1 only: measure,
no arbiter change). Mac only, ~1 h 20 min of the 2 h box.

**Result: zero inversions on the I26-FAST route to t2400.** 1,840,697 packets
in 1,840,697 drains — every drain on the route processed exactly one packet,
so the drain sort never reordered anything. Per the review's stop rule this
closes suspect 1 for this route (no Part 2 sort replacement); the orchestrator
decides and records it in `facts.md`.

## Pins and inputs

| Item | Pin | Receipt |
| --- | --- | --- |
| Fork base | `ssx3` `56a5e8a` (remote `fork/ssx3`; local `ssx3` label sits behind at `f949ff0`) | `git log`, worktree add |
| GA1 worktree/branch | `~/dev/ssx3-work/GA1/PS2Recomp`, `ga1-order` (unpushed, local-only) | `git status` |
| Codegen / ISO / ELF | `8ea8ed43…`, `3c2f8eb1…`, `1b49d05c…` (×2 per boot, match GB8/F1) | boot-driver precheck |
| Runner `bin/runner-pkorder` | SHA-256 `37e0dfac…dfeb1fe` (×2) | `sha256sum` |
| Route | I26-FAST, race HUD ~t1714; empty mc0/mc1; `PS2X_DETERMINISTIC=1` | `ga1_boot.py`, `result.json` |
| paraLLEl | `PS2X_GS_BACKEND=parallel` + system MoltenVK; `[gs-path] hier_rule=flat-always … desc=plain … gpu=Apple M5 Pro`, no FATAL | `boot.log` |
| Sound | **`PS2X_SOUND=1`** (required on the folded tip — see B1 below; F1's env, not GB8's) | B1 vs B2 |

Build (1/1): Release, Homebrew clang, `PS2X_GS_SHADOW_PARALLEL=ON`,
`PS2X_ENABLE_PK_ORDER=ON` + `PS2X_ENABLE_DET_HASH_TAP=ON` (tick gate only),
all other diagnostics OFF; 456 steps, rc=0. Tap markers present in the binary
(`pk-order`, `det-hash:v1`).

Release-unchanged check (no second build): the tap is 75 inserted lines, all
behind `#if PS2X_ENABLE_PK_ORDER` (CMake option, default OFF, same pattern as
`DET_HASH_TAP`); no signature changes (tick via a setter wired at runtime
init). Both touched TUs compile with `-DPS2X_ENABLE_PK_ORDER=0 -fsyntax-only`
(`ARBITER_OFF_OK`, `RUNTIME_OFF_OK`).

## Method

- `GifArbiter::submit()` stamps `(submitIdx, submitTick)`; `drain()` assigns
  `drainId`/`processIdx` and appends one line per processed packet to
  `$PS2X_PK_ORDER`:
  `drain submitTick processTick submitIdx processIdx path bytes img dhl`
  (`img`/`dhl` reuse the arbiter's own `path3Image`/`path2DirectHl` flags).
  Unset env = counters only. Line-buffered so the bound's SIGTERM loses
  nothing. Files: `ps2xRuntime/CMakeLists.txt`,
  `include/runtime/gs/ps2_gif_arbiter.h`, `src/lib/gs/ps2_gif_arbiter.cpp`,
  `src/lib/ps2_runtime.cpp` (tick wiring).
- Note: the brief's `ps2_memory.cpp` line numbers (2245/2332/2355/2361) are
  stale on this tip; the submit/drain sites are at 2275/2401-2402/2425/2444/
  2481/2486, plus PATH1 from `ps2_vu1_core.cpp:1061` and PATH2 from
  `ps2_vif1_interpreter.cpp:432,784` (all `drainImmediately=true`).
- `inversions.py`: groups by drain (file order = process order), counts pairs
  processed out of submit order. Verified on a synthetic 2-drain log (1
  inversion, `p3img_after_p12=1`).
- Boots: **B1 void** (no `PS2X_SOUND`: title from tick ~250 on, 9 small
  packets/tick, all 31 pad presses fired but ignored — folded-tip sound-off
  hang, new observation, see below). **B2 (spare)** with `PS2X_SOUND=1`:
  `target`, 94.4 s wall, slot 1, det-hash ticks 1..2404 consecutive, no
  FATAL, no missing-function stop.

## Results (B2)

Totals: packets=**1,840,697**, drains=**1,840,697**, multi-packet drains=**0**,
inverted pairs=**0**, affected drains=**0**, affected vsyncs=**0** (of 2,343
packet-bearing vsyncs, span 39..2404). `submitIdx` and `processIdx` are both
exactly 0..1840696 — every submitted packet drained exactly once; tap faithful.
All three paths present: P1 1,536,737 (XGKICK) / P2 276,825 (VIF1 DIRECT) /
P3 27,135. `submitTick==processTick` on all 1.84M lines.

| Phase (ticks) | Packets | Drains | Inverted pairs | Mean pkt/tick |
| --- | --- | --- | --- | --- |
| Title [39,636) | 52,125 | 52,125 | 0 | 87 |
| Menus [636,1440) | 179,392 | 179,392 | 0 | 223 |
| Loading [1440,1714) | 243,019 | 243,019 | 0 | 887 |
| Race [1714,2404] | 1,366,161 | 1,366,161 | 0 | 1,977 |

The per-vsync inversion table and the first-ten list are both empty
(`inversions.py` prints no rows) — there is no inversion instance to tabulate,
and no PATH3-IMAGE-after-PATH1/2 case arises.

Why multi=0 (code-derived, consistent with the measurement): PATH1/2 submit
with `drainImmediately=true` on an empty queue; race PATH3 arrives masked and
is released one EOP packet per MSKPATH3 window with an immediate drain
(RR1's model); the batch/flush multi-submit paths never accumulate >1 packet
on this route. The sort comparator (incl. the DIRECTHL-vs-IMAGE exemption)
never compares two packets here: `img=0` and `dhl=0` on all 1.84M lines — no
PATH3 packet *starts* with an IMAGE tag (uploads ride inside PACKED EOP
packets), and no PATH2 DIRECTHL packet was submitted.

## Tick 1795 vs the PCSX2 order (RR1 E2)

Ours (2072 packets, submit order == process order throughout; positions 1-based):

```
1: P3 1696B → P2 144/160/16B → 5: P3 65,664B → P2 16/48B → P1 draws (208/160/…)…
P3 uploads interleaved to the end: #93 5760, #150 11136, #385 22272, #1175 11136,
#1298/#1303/#1310 5760, #1349 11136, #1375 65664, #1504/#1527 11136, #1541 22272,
#1573/#1593/#1620 11136, #1768 11136, #1886 11136, #1933 4672, #1941 22272, #1978 1824
```

PCSX2 T65 v0 (`pcsx2-timeline.txt`, 1537 transfers): setup regs → one 65,664 B
upload (#6–#9) → TEX0 → draws; upload runs of exactly 65,664/11,136 B between
draws; depth pass late (#1418–1423). Same structure as ours: setup, a single
65,664 B EOP upload fifth, then draws with 21 further EOP-sized uploads
(65,664/22,272/11,136/5760/…) interleaved through #1978 of 2072. No reorder
between our submit and process order at any point, so there is no divergence
from the PCSX2 order attributable to the arbiter. (Which EOP packet carries
the depth pass would need register decode — out of Part 1 scope.)

## Recommendation (orchestrator decides)

Per the stop rule (zero inversions → close): **do not run Part 2** (no sort
replacement) for this route; record in `facts.md` that every arbiter drain on
I26-FAST-to-t2400 holds exactly one packet, so drain-sort order == submit
order trivially. Two follow-ups worth queuing, neither is Part 2:

1. **Folded-tip sound-off hang** (new): B1 without `PS2X_SOUND` sat on the
   title to t2400 with all input ignored; F1 (sound on) races. Pre-fold GB8
   raced with sound off, so AU9's fold introduced a sound-off dependency in
   menu progress. Briefs on this tip must carry `PS2X_SOUND=1` (F1's env, not
   GB8's) until this is understood; the hang itself may deserve its own lane.
2. The `img`/`dhl` flags never fire on this route — if a future brief needs
   the "PATH3 IMAGE" sub-question, it needs byte-level upload classification,
   not the arbiter's first-tag predicate.

## Exact commands

```sh
git -C ~/dev/PS2Recomp worktree add ~/dev/ssx3-work/GA1/PS2Recomp -b ga1-order 56a5e8a
cd ~/dev/ssx3-work/GA1
cmake -S PS2Recomp -B build -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER=/opt/homebrew/opt/llvm/bin/clang \
  -DCMAKE_CXX_COMPILER=/opt/homebrew/opt/llvm/bin/clang++ \
  -DPS2X_GAME_CODEGEN_DIR=/Users/brad/dev/ssx3-work/codegen-ssx3 \
  -DPS2X_BUILD_TEST=OFF -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_DEBUG_UI=OFF \
  -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF \
  -DPS2X_ENABLE_DIAG_TAPS=OFF -DPS2X_ENABLE_DET_HASH_TAP=ON \
  -DPS2X_ENABLE_PK_ORDER=ON -DPS2X_GS_SHADOW_PARALLEL=ON \
  -DPS2X_PARALLEL_GS_SOURCE_DIR=/Users/brad/dev/parallel-gs \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON            # configure.log, rc=0
cmake --build build --parallel 8 --target ps2EntryRunner      # build.log, rc=0
cp build/ps2xRuntime/ps2EntryRunner bin/runner-pkorder
python3 ~/dev/ssx3/local/research/GA1/ga1_boot.py --runner bin/runner-pkorder --label B2 --stop-tick 2400
python3 ~/dev/ssx3/local/research/GA1/inversions.py run/B2/pk-order.txt
python3 ~/dev/ssx3/local/research/GA1/inversions.py run/B2/pk-order.txt --tick 1795
```

Scripts committed here: `ga1_boot.py` (bounded det driver: paraLLEl,
I26-FAST, det-hash tick gate, order-log cap, one slot), `inversions.py`
(per-vsync inversion counts, first-K pairs, `--tick` dump). Scratch:
`~/dev/ssx3-work/GA1/` (build, bin, run/B1+B2, logs; order log 205 MB).

## Budgets and gaps

Builds 1/1 (+0), boots 2/2 (B1 void on env, B2 spare), each ≤ 500 s wall, one
slot each. Scratch ~2 GB (< 10 GB). Never pushed; fork branch `ga1-order`
local-only; no files under `ps2xRuntime/src/runner/` touched. Gaps stated
plainly: no frame dumps (route progress verified by traffic shape + F1's
same-tip viewed frames, not by viewing B2's frames); B2's determinism vs F1's
B1 not hash-compared (different tap sets); batch-pass multi-submit
reachability is code-derived, not directly instrumented; depth-pass identity
at tick 1795 not decoded.

## Orchestrator gate (2026-09-25)

**Pass; RV3 suspect 1 closed for this route.** 1,840,697 packets in 1,840,697 single-packet drains:
the drain sort never reorders anything, so it can't be the flicker. **New blocker-class finding:**
on the folded tip (`56a5e8a`) a sound-off boot (`PS2X_SOUND` unset) sits on the title with input
ignored; sound-on races. AU10 takes it. Until fixed, every boot on this tip sets `PS2X_SOUND=1`.
