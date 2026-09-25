# ST1 — fine horizontal stripes on paraLLEl frames (Mac)

Worker: Muse Code. Brief: `local/muse/prompts/ST1.md` (Part 1 evidence + one fix).
Scratch: `~/dev/ssx3-work/ST1/` (worktrees + build + runs, 3.4 GB). **No pushes.**

## 0. Outcome first

**H1 confirmed, fixed, validated.** The stripes are paraLLEl's field weave
showing the *previous guest tick's* scanout lines, verbatim, on alternating
rows. SSX 3 renders a full 448-line frame into one buffer every vsync
(SMODE2 INT=1/FFMD=0, single circuit, DY=50 even, DBY=0 — identical at menu
and race), but paraLLEl scans it as interlaced fields and fastmad-weaves the
current field with the previous tick's field. On motion the stale rows read
as alternate-line stripes; the stripe phase flips every tick with
`phase = vsyncTick & 1`. H2 (field offset) is out (DY even, DBY 0, no
offset); H3 (half-texel) is out (fresh rows are pixel-exact vs the buffer
model, stale rows bit-identical to the previous tick).

**Fix (one line, local-only):** `force_progressive = true` in the fork's
paraLLEl `vsync()` call — scan the full buffer as-is like the CPU weave,
no deinterlace. Validation boot: stripes gone (|A| ≤ 0.16, was −1.00),
exact-pixel agreement with the CPU backend doubled (0.077 → 0.153),
det-hash byte-identical (guest untouched), frames viewed.

## 1. Pins and inputs

| Item | Pin |
| --- | --- |
| PS2Recomp base | fork `ssx3` `96e9f45` (worktree, detached) |
| ST1 local commits (no push) | `ad27866` sidecar DISPLAY/DISPFB diagnostic (text only) + `92f9991` force-progressive fix |
| paraLLEl-GS | `19d93b2` (worktree, detached); Granite `166ba21a` (gitlink match) |
| Canonical codegen | `register_functions.cpp` `8ea8ed43…` ×2 (623 files ref `PS2X_SBR_LT`) |
| ISO / ELF | `3c2f8eb1…` / `1b49d05c…` (driver precheck ×2 every boot) |
| Route | I26-FAST, `PS2X_SKIP_MOVIE=1`, `PS2X_DETERMINISTIC=1`, empty mc0, `PS2X_SOUND=1` |
| Parallel env | `PS2X_GS_BACKEND=parallel`, `GRANITE_VULKAN_LIBRARY=/opt/homebrew/lib/libvulkan.1.dylib`, `PGS_HIER_BINNING=force` |

Runners (both from one build dir, Release, Homebrew clang,
`PS2X_GS_SHADOW_PARALLEL=ON`, logs OFF, diag taps OFF, det-hash tap ON):

| Runner | SHA-256 | Note |
| --- | --- | --- |
| `bin/runner-det` | `5d5f887e…b6ace9` (2 matching reads) | base + sidecar diagnostic |
| `bin/runner-fix` | `be1e1910…f30c163` (staged + driver precheck reads) | + force-progressive |

Suite from the worktree root: **616/616 pass** (612 F2 + 4 tap-only det-hash tests).

Runner guard: `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner` empty.

## 2. Present path (file:line at the pinned revs)

Fork `ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp:247-254` builds a
zeroed `VSyncInfo`, sets only `phase = vsyncTick & 1`, the `dst_*` layout,
and `adapt_to_internal_horizontal_resolution = true`, then calls
`m_iface->vsync()`. All deinterlace-affecting flags stay false:
`force_progressive`, `skip_deinterlace`, `anti_blur`, `overscan`,
`crtc_offsets` (`parallel-gs/gs/gs_interface.hpp:155-199`).

With SSX 3's regs (SMODE2 INT=1/FFMD=0, §3), paraLLEl takes the
`alternative_sampling` path (`gs_renderer.cpp:4258-4270`, `:4303-4311`):
`phase = info.phase` (`:4557-4567`), each circuit scans half its lines
(`compute_circuit_rect`, `:4198-4253`: `phase_offset = (DY ^ phase) & 1`,
stride 2, half height) into a 224-line field, and `fastmad_deinterlace`
(`:5164-5210` + `shaders/weave.frag`) doubles it to 448: output rows with
`(y & 1) == phase` come from the current field verbatim; the other rows
take the previous field (`uField1`) when still, else blend toward a
vertical-average bob (`smoothstep(0.04, 0.06, diff)`).

`PS2X_DEINTERLACE` is read **only** by the CPU backend
(`gs_cpu_backend.cpp:456`, default weave) and is set in no game env, app
env, or lane tooling (repo-wide grep: only `docs/` mentions). Mac paraLLEl
boots are unaffected by it.

## 3. Scanout registers (new sidecar fields, identical menu → race)

Extended the frame-dump sidecar with raw `display1/2 + dispfb1/2`
(`ps2_runtime.cpp`, local commit `ad27866`; text only, zero pixel effect).
Seven sidecars (menu 1088/1096, race 2095/2097/2098/2100/2101) agree:

| Reg | Raw | Decoded (layouts: `gs_registers.hpp:560-623`) |
| --- | --- | --- |
| SMODE2 | `0x1` | INT=1, FFMD=0 (field mode) |
| PMODE | `0xff21` | EN1=1, EN2=0 (single circuit), ALP=255 |
| DISPLAY1 | `0x1bfa0002032281` | DX=641, **DY=50 (even)**, MAGH=4, MAGV=0, DW=2560, DH=447 |
| DISPFB1 | `0x9070` | FBP=112, FBW=8 (512 px), PSM=1, DBX=0, **DBY=0** |
| DISPLAY2/DISPFB2 | `0x1bf27f00000000`/`0x1400` | circuit off (EN2=0) |

DY even + DBY 0 rules out H2: `phase_offset = (DY ^ phase) & 1 = phase`,
no field offset anywhere. Single 512×448 buffer at FBP 112.

## 4. Stripe evidence (H1)

Metric: signed period-2 amplitude `A = mean((row − mean)·(−1)^y)` over a
window (`st1_rowluma.py`, GB8's validated stdlib PNG decoder). `A > 0` =
even rows brighter. Global `A` dilutes the effect (|A| < 0.2 full-frame);
the smooth near-field snow (x380–480, y388–410) is the detector.

### 4a. Stripe phase flips with tick parity (par1, consecutive ticks)

| Tick | Parity | Zone mean | A |
| --- | --- | --- | --- |
| 2095 | odd | 175.71 | **+0.505** |
| 2097 | odd | 172.10 | **+0.682** |
| 2098 | even | 171.30 | **−0.113** |
| 2100 | even | 169.49 | **−1.004** |
| 2101 | odd | 168.31 | **+0.177** |

Sign tracks tick parity on all 5 frames incl. both consecutive pairs
(2097/2098, 2100/2101): the stale rows are always parity `!= phase`.

### 4b. Striped rows are the previous tick, verbatim (no bob)

Tick 2098 (phase 0), same zone, vs tick 2097:

| Rows @2098 | mean\|cur − tick2097\| | mean\|cur − vertical-avg\| |
| --- | --- | --- |
| even (fresh) | 1.743 (scene moved) | 0.119 (smooth) |
| odd (mixed) | **0.000 (bit-identical)** | 0.289 |

fastmad's motion diff never fired here (`bob_factor = 0`): output row `y`
at tick N is buffer line `y` from tick `N − (y&1 != N&1)`. A textbook field
weave of frame-rendered content. H3 is out with it (no resampling error on
either row set).

### 4c. Same-tick CPU contrast (cpu1, det-hash identical)

Tick-2100 det-hash lines are byte-identical across par1/cpu1/par2
(`combined=4b16184f587dd107`), so any pixel difference is present-path only.

| Tick | par1 A | cpu1 A |
| --- | --- | --- |
| 2098 | −0.113 | −0.074 |
| 2100 | **−1.004** | −0.081 |
| 2101 | +0.177 | −0.128 |

The 2100 pair is decisive: same guest state, paraLLEl striped, CPU smooth.
The game redraws full frames (a field-only renderer would comb under the
CPU weave too). Menu static zone (x100–300, y20–60): par1 +0.000, par2
+0.055, cpu1 +0.135 — no motion, no stripes, all backends.

### 4d. Why the Odin screens look worse (for the N lane)

N9's `race.png`/`menu.png` carry the same signature (measured ±4 LSB
oscillation, ~6-row screen period = guest period 2 × 2.125 vertical
upscale + bilinear beat) but **global and on static UI**, vs Mac ±1 LSB on
motion only. The weave logic is shared fork code, so §5's fix (which
removes all field-history reads) plausibly fixes the Odin too — but the
static-UI component smells like an additional Turnip/wave64 contribution
(e.g. field-history sampling), which only an Odin A/B can close. N9 has no
guest PNGs (sidecars only), so this lane could not check Odin guest frames.

## 5. Fix + validation (one line, one boot)

`ps2_gs_parallel_backend.cpp` (+6, local commit `92f9991`, no push):

```cpp
// ST1 (local-only): SSX 3 renders a full frame every vsync into one
// buffer (SMODE2 INT=1/FFMD=0, single circuit, DY even). The field
// weave shows the previous tick's lines on alternating rows
// (stripes on motion, phase flips each tick), so scan the full
// buffer as-is like the CPU weave instead of deinterlacing.
vsync.force_progressive = true;
```

With `force_progressive`, `scanout_is_interlaced` goes false:
mode 640×224→448, circuits sample full height stride 1 at y-offset 0 for
our regs (`(DY+0)>>0 − 50 = 0`, height 448 = mode height), no fastmad.
Build 2: incremental, rc=0.

Validation boot (par2, same env/pins, det-hash identical):

| Tick | par2 zone A | Verdict |
| --- | --- | --- |
| 2095/2096/2098/2099/2101/2103 | −0.16/−0.16/−0.11/−0.11/−0.09/−0.07 | stripes gone, CPU level |

(2098/2099 share fnv `7c6212e1`: the game presented identical bytes twice.)

Same-tick 2098 pixel stats vs CPU: equal_px 0.077 → **0.153**,
within±2 0.293 → **0.366**, within±8 0.564 → 0.578. (Absolute levels are
below GB8's 0.67 only because GB8 measured half-broken frames: its race
frame mean luma is 43.8 — the dark pre-RR1 region — vs 151.9 now fully
drawn.) Viewed: par2-2098 full race (2ND/2, 00:00:05, trick 190, radio
card, rider, terrain — same scene as F2's striped frame) and the
bottom-right crop that striped before: smooth. Menu par1-1088 viewed:
Select Peak, Peak 1 highlighted, photo + text correct.

## 6. Side observation (not this lane)

The CPU backend leaves output row 447 black (full-width mean 0.00 at 2098;
par2 shows content 173.37 there) — a CPU present-path off-by-one, worth one
line in E/G triage. It also explains a +3 LSB coherent bottom-tile reading;
it is not striping.

## 7. Boots, budgets, gaps

| Boot | Backend | Runner | Wall | Last tick | HUD wall | Bound |
| --- | --- | --- | --- | --- | --- | --- |
| par1 | parallel | runner-det | 85.5 s | 2402 | 35.35 s | target |
| cpu1 | cpu | runner-det | 180.9 s | 2401 | 69.99 s | target |
| par2 | parallel | runner-fix | 85.5 s | 2401 | 35.35 s | target |

`[gs-path]` on both parallel boots:
`hier_rule=hier-if-large hier_t2=2 hier_t4=4 … desc=plain … gpu=Apple M5 Pro`.
No `[gs:parallel] FATAL` anywhere. Builds 2/2, boots 3/3, all ≤ 500 s wall.
No speed numbers (diagnostic build: det-hash tap + frame dumps).

Gaps: snapshotter (0.1 s, change-gated) missed some ticks (no par1 2096/
2099/2100-sidecars beyond the five; no par2 2100) — consecutive pairs still
captured both parities. Menu snaps are sparse (guest outruns the
snapshotter at 1.28×) and cross-boot menu ticks differ by Δ1–2. Odin
guest-frame check outstanding (§4d). Product form of the fix (unconditional
vs per-game env knob) is a G-lane call — unconditional is safe for SSX 3
(single INT/FFMD mode menu→race) but untested for other games.

## 8. Exact commands

```sh
# worktrees (E-lane checkout untouched apart from worktree metadata)
git -C ~/dev/PS2Recomp worktree add ~/dev/ssx3-work/ST1/PS2Recomp 96e9f45
git -C ~/dev/parallel-gs worktree add --detach ~/dev/ssx3-work/ST1/parallel-gs 19d93b2
git -C ~/dev/ssx3-work/ST1/parallel-gs submodule update --init --recursive  # Granite 166ba21a
# build 1 (base + ad27866 sidecar diagnostic)
cmake -S PS2Recomp -B build -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER=/opt/homebrew/opt/llvm/bin/clang \
  -DCMAKE_CXX_COMPILER=/opt/homebrew/opt/llvm/bin/clang++ \
  -DPS2X_GAME_CODEGEN_DIR=/Users/brad/dev/ssx3-work/codegen-ssx3 \
  -DPS2X_BUILD_TEST=ON -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_DEBUG_UI=OFF \
  -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF \
  -DPS2X_ENABLE_DIAG_TAPS=OFF -DPS2X_ENABLE_DET_HASH_TAP=ON \
  -DPS2X_GS_SHADOW_PARALLEL=ON \
  -DPS2X_PARALLEL_GS_SOURCE_DIR=/Users/brad/dev/ssx3-work/ST1/parallel-gs \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON            # rc=0
cmake --build build --parallel 8 --target ps2EntryRunner ps2x_tests  # rc=0, 626 steps
cp build/ps2xRuntime/ps2EntryRunner bin/runner-det
# boots (one P-lane slot each, released on every path)
python3 st1_boot.py --mode det --backend parallel --runner bin/runner-det --label par1 --stop-tick 2400 --sound on
python3 st1_boot.py --mode det --backend cpu --runner bin/runner-det --label cpu1 --stop-tick 2400 --sound on
# fix (92f9991) + build 2 + validation
cmake --build build --parallel 8 --target ps2EntryRunner  # rc=0, 4 steps
cp build/ps2xRuntime/ps2EntryRunner bin/runner-fix
python3 st1_boot.py --mode det --backend parallel --runner bin/runner-fix --label par2 --stop-tick 2400 --sound on
# analysis
python3 st1_rowluma.py [--rows|--tiles] A.png [B.png ...]
```

## 9. Recommendation (orchestrator decides)

Fold the one-line `force_progressive` fix (G-lane to choose unconditional
vs env knob) and re-check the Odin: if N9-style static-UI stripes survive
there, they are a separate Turnip/wave64 field-history issue and want an
Odin replay A/B (`odin_replay.py` rows + guest PNGs) as the follow-up
brief. Retire the CPU row-447 black line to E/G triage.

## Receipts

- `st1_boot.py` (F2 driver + 0.1 s change-gated snapshotter), `st1_rowluma.py`
  (global A, d1/d2, `--rows`, coherent `--tiles`), `zone-rows.tsv`
  (x380–480/y388–410 row means: par1-2100 striped, cpu1-2100 clean,
  par2-2098 fixed).
- Scratch: `~/dev/ssx3-work/ST1/` (build, bin, run/par1+cpu1+par2 with
  logs, traces, `result.json`, sidecars + snaps; `configure.log`,
  `build.log`, `build2.log`, `suite.log`).
