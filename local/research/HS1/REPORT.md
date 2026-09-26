# HS1 — host split: fast bradflix builds + 4 bradflix boot slots

Worker: Muse Code, brief `local/muse/prompts/HS1.md`. No push (orchestrator gates).

**Result: host split works.** bradflix builds the a3efbfe parallel-det
runner cold in ~400 s / warm in 51 s with a shared ccache, and 4
concurrent det boots (FR1-R1, t2400, paraLLEl, `PGS_HIER_BINNING=force`)
all `baseline.py compare` **IDENTICAL** vs the `a3efbfe` Mac key, with no
wall slowdown concurrent-vs-single (117 s both). Two misses, stated
plainly: cold build 400 s vs the 300 s target (G1), and 9 boots vs the 8
budget after the launcher serialized the first 4-way attempt (G2).

Pins: fork `a3efbfe946631c44f113f20a94b3c64754d87701` (has the F5 fold of
lx1-tz incl. `-msse4.1`, verified by message, not SHA: `18b8f90 efb7f04
c8b5f54 607271c 6bcee0e`), parallel-gs `19d93b2d0bb0172c2ab4c057de4adbd6ed566eba`,
Granite `166ba21a247a681903cc9d0bb6562fe50a554c85`, codegen register
`8ea8ed43…688a3` + vf0 `89953ba2…383d`, vu1gen manifest `aa8127bc…` (=
`F5/vu1gen.sha` hash; the pins value `1733…` uses an unknown scheme — G5),
image `ssx3-hs1 d124af4da093`.

## 1. unity_74 diagnosis (step 1)

Same TU both sides: HS1 `unity_74_cxx.cxx` at a3efbfe holds the same 32
files as LX1's (first `sub_001E4878`, confirmed by grep). Only the flags
differ — and the wall differs 25×:

| TU | Config | Wall (clang 18 -O3, bradflix) |
| --- | --- | --- |
| unity_74, LX1 build-parallel | DIAG_TAPS=ON, DET on (from its CMakeCache) | ~25 min (LX1 report; ninja-log top entry 1270 s) |
| unity_74, HS1 | DIAG_TAPS=OFF, DET on (acceptance flags) | **60.5 s** (`time`, two runs: 60.5/60.7 s) |

`-ftime-trace` of the 60 s compile: `ExecuteCompiler` 60.6 s, of which
the function pass pipeline on **`sub_001E9A30_0x1e9a30`** takes 31.7 s
with **`GVNPass` 24.8 s** on that function alone. The function is a
54,851-line generated body (guest 0x1e9a30–0x1f10f8, switch/goto
spaghetti) with ~4,000 guest-memory macro uses (READ32×1807,
WRITE32×999, READ64×665, …).

Mechanism: `DIAG_TAPS=1` swaps live watch-tap namespaces (4 trace
headers + `__func__`/argument setup) into every READ/WRITE macro
expansion (`ps2_runtime_macros.h:17-23`, `ps2xRuntime/CMakeLists.txt:490`);
`=0` compiles them to nothing. In a 55 k-line function the inflated IR
sends superlinear GVN into a 25-minute blowup. The acceptance config
(DIAG off, as in `mac_build.sh`) never had the problem — the "blocker"
was a DIAG-build artifact, matching the Mac's ~270 s cold (also DIAG off).

Brief options, each timed once, no loops:

| Option | Experiment | Result |
| --- | --- | --- |
| (a) clang 20+ | not run | judged unable to close the remaining gap (G3) |
| (b) smaller batches | full cold build at batch 16 (hs1b2) | **411 s — worse** than 400 s at 32 (2× header re-parse eats the tail saving) |
| (c) lower opt | unity_74 standalone: -O2 59.0 s, -O1 32.1 s | -O1 halves the hot TU but projects to only ~300 s full-build while taxing every future boot's wall ~1.5× — rejected; -O3 stands |

**Pick: no flag/codegen changes.** Fork defaults (-O3, batch 32,
DIAG off). Det-hash effect: none — verified by the step-4 acceptance
(bradflix -O3/batch-32 == Mac -O3/batch-32).

## 2. Builds (step 2)

`local/tooling/build/bradflix_build.sh <fork-sha> <build-name> [--det]`
+ `local/tooling/build/Dockerfile.bradflix` (LX1 recipe + ccache; LX1's
file untouched as its evidence). Image `ssx3-hs1`. ccache in
bind-mounted `~/dev/ssx3-work/ccache` (v4.9.1, `CCACHE_BASEDIR=/work`,
5 GB default cap — G6), 16 jobs.

| Build | Batch | Cache state | Wall (configure+build) | ccache | Runner SHA-256 |
| --- | --- | --- | --- | --- | --- |
| hs1b1 | 32 | cold (empty) | ~400 s (ninja span 352 s) | 0/615 hits | `81e78ce5…90967` |
| hs1b2 | 16 | cold (wiped) | 411 s | 0/910 hits | `0c107b7a…04434` |
| hs1b3 | 32 | game-cold/rest-hot | 242 s | mixed | `81e78ce5…90967` |
| hs1b4 | 32 | warm (hot) | **51 s** | 615/615 hits in-build | `81e78ce5…90967` |

- Cold target ≤ 300 s: **MISS** (400 s). Build is 3,792 job-seconds at
  67% parallel efficiency (9 TUs > 60 s, slowest 103 s, link < 1 s).
  Steady state is better than cold: new fork SHAs reuse the unchanged
  game-code objects (~150–240 s), same-SHA rebuilds are 51 s. See G1.
- Warm target ≤ 120 s: **PASS** (51 s).
- Reproducibility: hs1b1/hs1b3/hs1b4 (three separate build dirs, two
  cache states) are byte-identical runners (`81e78ce5…`, 182,785,976 B).
- Suite: `ps2x_tests` builds as part of every build (same as
  `mac_build.sh`); the suite itself was not re-run here. HS1 made no
  fork change, and LX1 Part 1c already showed 650/650 with these fixes
  folded; the det-hash acceptance is the stronger check.

## 3. Lease + boot path (step 3)

- `local/tooling/p_lane_lease.py`: `--host mini|bradflix` (default mini;
  mini paths/behavior byte-identical). bradflix slots are dirs
  `~/.ssx3-lease/1..4` (`mkdir` = atomic claim, HOLDER file inside);
  `--exclusive` claims all four with rollback. Self-test: claim→1,
  claim→2, exclusive→both then busy(rc=1), release→all free.
- `local/tooling/boot/ssx3_boot.py --host bradflix` (det only; speed
  rejected): claims a bradflix slot (30 s retry loop, honors
  `SSX3_HELD_SLOT_BRADFLIX`), syncs the driver, runs it over ssh,
  pulls result.json/boot.log/trace.jsonl/snd.log/frames back to `--out`
  (default `~/dev/ssx3-work/from-bradflix/<label>`) + writes `pull.json`
  provenance, releases the slot. `--runner` is a bradflix path.
- `local/tooling/boot/bradflix_det_boot.py` (runs on bradflix): mirrors
  ssx3_boot det env exactly (same 4 SHA pins incl. the F4 vf0 file, same
  pad route passed through `--pad-script` — ROUTE strings verified equal
  by import test — same sound/coverage/dump-ticks/vu1-stats/unpaced/
  stack-kb/`--env` handling, same caps/trace/hud/result.json fields).
  Guest-neutral deltas only: Docker `ssx3-hs1`, GPU
  (`renderD128`+group 993) for parallel backend, direct-Xvfb management
  (LX1 lesson), no `GRANITE_VULKAN_LIBRARY` (system loader, LX1 Part 2
  recipe), requires the held lease slot. Fixed during HS1: remote
  `~/..` quoting (relative driver path), `expanduser` on `--runner`.
- LX1's `bradflix_boot.sh` + `BRADFLIX_LEASE` single-lease scheme are
  left untouched and are superseded for boots (builds move to
  `bradflix_build.sh`).

## 4. Acceptance (step 4)

Runner hs1b4 (`81e78ce5…`), FR1-R1, t2400, parallel, force (driver sets
`PGS_HIER_BINNING=force` as on the mini), sound on, coverage 2400,
vu1-stats, dump-ticks 1090,1800,2100. `[gs-path]` on all boots:
`hier-if-large … desc=buffer … gpu=Intel(R) Graphics (ARL)` (Odin's
descriptor path, as in LX1 Part 2). `gs_fatal=null` everywhere.

| Boot | Slot | Wall (elapsed) | Ticks | HUD | `baseline.py compare` vs `a3efbfe-det-fr1r1-t2400-snd1-1x-a5f2f32d` |
| --- | --- | --- | --- | --- | --- |
| HS1S1 single | 1 | 116.9 s | 2406 | 55.6 s | IDENTICAL (after the coverage fix below) |
| HS1B1 4-way | 2 | 116.9 s | 2403 | 53.3 s | IDENTICAL |
| HS1B2 4-way | 3 | 116.9 s | 2402 | 53.3 s | IDENTICAL |
| HS1B3 4-way | 4 | 117.4 s | 2404 | 53.6 s | IDENTICAL |
| HS1B4 4-way | 1 | 116.8 s | 2402 | 53.3 s | IDENTICAL |

- Concurrent-vs-single wall: **no slowdown** (117 s both; 4-way
  aggregate 4×117 s in a 121 s window).
- Concurrency proof: distinct slots 1–4 held simultaneously, all four
  walls overlap in one 121 s window (the earlier HS1A1–A4 set ran
  sequentially — all slot 1 — after the launcher serialized a parallel
  tool block; kept as 4 extra single-boot IDENTICALs, see G2).
- bradflix during the 4-way: loadavg 1-min 1.0 → 4.1 (≈1 core/boot,
  cf. mini ~1.2), mem ~11/62 GB used, media containers untouched
  (`docker ps` before/after identical, 21 services up throughout).
- Lease verified all-free after every run.

### The one candidate fix (brief contract §5): coverage order

First compare of HS1S1: **det-hash IDENTICAL ticks 1–2400**, snd
guest-counters identical (only host under/overruns differ, already
stripped by `SND_HOST_NOISE`), but coverage DIFFER: the 4
`[coverage:unhandled-rpc]` lines print in `std::unordered_map`
iteration order — stable per host (F5 B1–B5 identical), different
across STLs (Mac libc++ vs Linux libstdc++), same content.
Fix in `local/tooling/boot/baseline.py`: compare coverage as
`sorted(cov_b) == sorted(cov_c)` with a comment. This cannot mask a
real difference (multiset equality), is verdict-neutral for same-host
compares (verified: baseline self-compare still IDENTICAL), and is
necessary regardless of any future fork-side sort, because all
existing baselines have hash-ordered coverage baked in. No fork
commit needed; none made; nothing pushed. (Fork-side alternative for
the record: sort at print in `ps2_runtime.cpp:1819-1823` + re-baseline
— heavier, still needs this compare change for old keys.)

## 5. Proposed runbook/AGENTS text (orchestrator edits docs)

> **Host split (HS1, 09-25): bradflix is the correctness host, the mini
> and the Odin are for speed.** Det/correctness boots move to bradflix
> (4 slots); the mini keeps 1 slot for benchmark-shape boots; speed
> numbers still come only from the mini (diagnostics-out builds) and
> the Odin. bradflix cold ~400 s / warm ~50 s (shared ccache) for the
> parallel-det runner; 4 concurrent det boots show no wall slowdown.
> - Build: `local/tooling/build/bradflix_build.sh <fork-sha>
>   <build-name> [--det]` (SHA-checked inputs, Docker `ssx3-hs1`).
> - Boot: `python3 local/tooling/boot/ssx3_boot.py --host bradflix
>   --mode det --backend parallel --runner <bradflix path> --label
>   <L> [same args as mini]`, then `baseline.py compare` unchanged.
> - Lease: `p_lane_lease.py --host bradflix status|claim|release`
>   (slots 1–4 under `~/.ssx3-lease/`; `--exclusive` takes all four).
> - bradflix rules: builds/boots only in Docker; `docker ps` first,
>   don't touch media containers; jobs stay at 16; everything under
>   `~/dev/ssx3-work/` (never `/tmp`); `~/.ssx3-lease/` is the only
>   lease (LX1's `BRADFLIX_LEASE` dir is retired — delete after HS1).

## 6. Budgets, exact commands, gaps

Builds 4/8 (hs1b1–hs1b4). Boots 9/8 (G2): HS1S1 + HS1A1–A4
(sequential) + HS1B1–B4 (concurrent 4-way). Time ~2.5 h of 3 h.
Mini scratch `~/dev/ssx3-work/HS1/` 18 MB (≤5 GB).
bradflix `~/dev/ssx3-work/`: HS1 11 GB + ccache 0.1 GB + LX1 22 GB ≈
33 GB (≤40 GB; LX1's share is not HS1's to clean). Mini internal
142.9/200 GB (pre-existing; HS1 added ~20 MB).

```sh
# unity_74 diagnosis (single-TU, acceptance flags + -ftime-trace)
./local/tooling/build/bradflix_build.sh a3efbfe946631c44f113f20a94b3c64754d87701 hs1b1 --det
./local/tooling/build/bradflix_build.sh a3efbfe946631c44f113f20a94b3c64754d87701 hs1b2 --det  # batch 16
./local/tooling/build/bradflix_build.sh a3efbfe946631c44f113f20a94b3c64754d87701 hs1b3 --det
./local/tooling/build/bradflix_build.sh a3efbfe946631c44f113f20a94b3c64754d87701 hs1b4 --det  # warm
python3 ./local/tooling/boot/ssx3_boot.py --host bradflix --mode det --backend parallel \
  --runner /home/brad/dev/ssx3-work/HS1/hs1b4/ps2xRuntime/ps2EntryRunner --label HS1B1 \
  --stop-tick 2400 --sound on --route fr1r1 --coverage-tick 2400 --vu1-stats \
  --dump-ticks 1090,1800,2100 --out ~/dev/ssx3-work/HS1/run/HS1B1   # ×4, concurrent
python3 local/tooling/boot/baseline.py compare --key a3efbfe-det-fr1r1-t2400-snd1-1x-a5f2f32d --cand ~/dev/ssx3-work/HS1/run/HS1B1
python3 local/tooling/p_lane_lease.py --host bradflix status
```

Receipts: `/tmp/hs1-build2.log`, `/tmp/hs1-build3.log`,
`/tmp/hs1-build4.log` (script outputs), `/tmp/hs1-bootA1..4.log`,
`/tmp/hs1-bootB1..4.log` (wrapper outputs), `/tmp/hs1_4way.py`
(4-way launcher), bradflix `~/dev/ssx3-work/HS1/u74.json`
(-ftime-trace), `~/dev/ssx3-work/HS1/run/HS1{S1,A1-A4,B1-B4}/`
(pulled runs), `~/dev/ssx3-work/from-bradflix/` (unused default —
HS1 passed explicit `--out`).

Gaps, stated plainly:
- G1. Cold 400 s vs 300 s target (build 3,792 job-s @67%: the tail
  is nine -O3 unity TUs >60 s). Follow-ups, each re-verified by
  det-hash: game-only -O1 fork knob (needs a fork commit; taxes boot
  wall ~1.5×), PCH for game objects, or accept (new-SHA ~150–240 s,
  warm 51 s is the steady state that matters).
- G2. Boots 9/8: the first 4-way attempt (HS1A1–A4) ran sequentially
  (parallel tool block executed serially; all slot 1) — salvaged as
  4 extra single-boot IDENTICALs; the true 4-way (HS1B1–B4, slots
  1–4, overlapping walls) is the acceptance.
- G3. (a) clang 20+ not tried: single-core optimizer speed cannot
  plausibly close the measured gap (Mac-8-job cold ≈2,160 job-s vs
  bradflix 3,792 job-s is 1.75×; version deltas are ~5–10%).
- G4. The `baseline.py` coverage-sort is a shared-tool semantic
  change (one line + comment): needs orchestrator review. It cannot
  mask content differences; same-host verdicts unchanged.
- G5. `vu1_images` pins value `1733…` ≠ the F5 manifest-hash scheme
  (`aa8127bc…`, reproduced here): content verified identical to
  `F5/vu1gen` file-for-file; the scheme that produced `1733…` is
  unknown. The build script uses the manifest scheme both sides.
- G6. ccache cap is the 5 GB default; fine at ~0.1 GB now, revisit if
  per-SHA accumulation evicts (watch hit rate in `bradflix_build.sh`
  output).
- G7. Sound-on in the container runs the null audio backend
  (overflows, zero underruns) vs Mac hardware counters — guest SND
  HLE is bit-identical (all guest counters equal); host counters
  were already stripped by compare. No snd change needed.
