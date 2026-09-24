# N8D7M3 — selected raw-VRAM provenance discriminator design (read-only)

**State: design only. No source edit, build, replay, boot, Odin/iOS action,
push, or status/todo/ledger edit.** LSP hover on the oracle source returned
no results (no language server for files outside the repo); all links below
rest on direct source reads. No cause is declared; the orchestrator gates.

## 1. Pins read in this part

| Item | Pin |
| --- | --- |
| Repo HEAD (receipts only) | `52dfba68` |
| Oracle fork worktree | `~/dev/ssx3-work/N8D7L/PS2Recomp`, `ps2_gs_parallel_backend.cpp` 1075 lines |
| Oracle header | `ps2xRuntime/include/runtime/gs/ps2_gs_psmct32.h:9-36` |
| G43 worktree | `~/dev/ssx3-work/N8D7F/parallel-gs`, `gs/gs_renderer.cpp` 5411 lines |
| Frame under test | N8D7M2 Odin tick 2050, FBP 112, FBW 8, PSMCT24, DBX/DBY 0, phase 0, stride 2, 512x224, mask 4194303, PMODE `ff21`, status 2 |
| Odin observation | oracle/input/circuit/stage 448 words, occ 2058, active **15**, SHA `bd33829e…`; final 896/4355/29; controls 0/8 vs Mac; 11/11 metadata alignment; category A |
| Mac observation (N8D7L) | same descriptor, 448 words, occ 64374, active **300**, SHA `e1dc4c5c…`; controls 8/8 literals |

## 2. Pinned source-path table (GIF writes to GPU input)

Calling order is top-to-bottom. Owners named per field.

| # | Stage | Code line + calling path | Owner / clock |
| --- | --- | --- | --- |
| 1 | GIF packets in | `ps2_gif_arbiter.cpp:14-60` capture tap proves packets flow EE -> arbiter; frontend `gs_frontend.cpp:568-573` records each Draw with `vsyncTick` + `frame.fbp` into the debug ring | EE tick drives `m_privRegs->vsyncTick`; frontend ring is the write-side record |
| 2 | VRAM writes | Renderer draws into `buffers.gpu` (ubershader `constants.fb_color_page * PGS_BLOCKS_PER_PAGE`, `ubershader.comp:360`; page flush `gs_renderer.cpp:2391-2392`, fb rect `:3125`) on the GS worker, enqueued from the EE (`gs_frontend.cpp:~750` `enqueue` + rpc `wait`) | GS worker consumes; EE waits per rpc |
| 3 | Snapshot tick + phase | Backend `ps2_gs_parallel_backend.cpp:441-447`: `selectedRequested` only when `request.vsyncTick == 2050` and env `=1`; `vsync.phase = tick & 1`. `request.vsyncTick` comes from `GS::buildPresentationRequestUnlocked` reading `m_privRegs->vsyncTick` (`gs_frontend.cpp:757-777`, tick at `:769`) | Tick owned by priv regs; phase bit owned by backend Present |
| 4 | Selected descriptor | G43 `gs_renderer.cpp:4777-4792`: FBP/FBW/PSM/DBX/DBY copied from `priv.dispfb1`; phase/stride from `compute_circuit_rect` (`:4321-4395`); mask = `vram_size-1` (`:4786`); samples = `super_samples`; promoted = `promoted1 != nullptr` | DISPFB1 owns FBP/FBW/PSM/DBX/DBY; DISPLAY1+SMODE own phase/stride via rect |
| 5 | 4 MiB snapshot | Guard `:4793-4804` (supported PSM, 512x224, 4 MiB, coords < 2048); copy `buffers.gpu` -> `selected_vram_staging` at `:4806-4820`, barrier COMPUTE\|TRANSFER -> TRANSFER_READ then TRANSFER_READ -> FRAGMENT_READ (**no** `COLOR_ATTACHMENT_OUTPUT`) | Same `direct_cmd`; executes at submit time, not at record time |
| 6 | GPU input (circuit1) | `sample_crtc_circuit` (`:4262-4318`): binds `buffers.gpu` (`:4282`), push FBP/FBW/DBX/DBY/phase/stride (`:4307-4313`); shader `sample_circuit.frag:108-115` `coord = px*(1,stride)+(dbx,dby+phase)`, `addr = swizzle_PS2(...)`; circuit1 readback `:5054-5077`, status 2 at `:5076` (raw-circuit early return `:4990-5031` leaves status 1) | GPU-side consumer of the same bytes the CPU decodes |
| 7 | Async boundary | Renderer `flush_submit(0)` at `:5354`; backend `submit` + `wait_idle` at `ps2_gs_parallel_backend.cpp:601-602`; host maps `selected_vram_staging` / `circuit1_staging` / counts at `:621-626` | Host sees bytes only after `wait_idle` |
| 8 | CPU selected decode | `selectedDecode` (`:100-156`): `base = fbp * PGS_BLOCKS_PER_PAGE` (`:105`), `sy = dby+phase+y*stride` (`:108`), `vram_readback<PSM>` (`gs_util.hpp:50-110`, `&2047` wrap + `swizzle_PS2` at `:66`); census `selectedTileCounts` (`:64-81`, RGB max >= 32, 448 tiles) | G43 bit-arithmetic address path |
| 9 | Independent oracle | `oracleDecodeCensus` (`:190-222`): same 512x224 grid through `GSPSMCT32::addrPSMCT32(block = fbp<<5, fbw, gx, gy)` (`psmct32.h:29-35`), `& 0x3FFFFF`, RGB-only >= 32; controls `kOracleControls` (`:179-188`) emitted at `:712-724`; `oracle_input_equal` at `:725-729`, gated by env `PS2X_N8D7L_ORACLE` (`:667-668`) | Fork literal-table path; shares only the mapped snapshot |
| 10 | VRAM upload path | `Initialize`/`uploadHandoff` (`:395-404`) hands frontend VRAM to the GPU on backend swap | Backend init, not per-vsync |

Address math (actual GS storage, never linear rows): FBP112 base byte
`112 * 8192 = 0xE0000`, block `112<<5 = 3584`; e.g. (31,0)->`0xE0534`,
(0,2)->`0xE0040`, (511,446)->`0x1BFFF4` (N8D7K §3, 8/8 fork/G43 agree).

## 3. Hypothesis / observable table (same run, tick-2050 aligned frame)

Preconditions for every row: status 2, 11/11 selected/oracle metadata
agreement, `control=128 PASS`, no probe/pipeline error; else OTHER.
Sparse means active <= 100/448; broad means active >= 250/448 (N8D7I/N8D7M2
conventions). Fields are same-run; a row is accepted only if its named
field differs from every other row's prediction.

| Hyp | Mechanism | Predicted same-run observable |
| --- | --- | --- |
| A sparse source | FBP112 got few writes before selection | `[n8d7m3] writes fbp112_draws` **< K** in window, no competitor >= K; S1 sparse; T1 drained |
| B wrong region | Content written at another valid base/phase; descriptor misses it | **C1 candidate census broad (>= 250)** while S1 sparse; W1 shows competitor FBP/phase draws >= K |
| C too early | FBP112 writes exist but land after the copy executes | W1 `fbp112_draws` **>= K** AND (**T1 `pending>0`** OR **`last112==2050`**); S1 sparse; C1 sparse |
| D decode fault | Bytes present at fork-table addresses but census loses them (PSM/mask/wrap) | W1 >= K, T1 drained, `last112<2050`, C1 sparse, AND **candidate-base control words >= 2/8 RGB-nonzero** while census sparse |
| OTHER | — | gate miss, actives 101-249, missing lines, promoted/samples/phase-gate miss |

K (draw floor) is set by Mac calibration (propose K=20 pending §5).

## 4. One proposed capture (`PS2X_N8D7M3_PROVENANCE=1`, default OFF)

Runs inside the existing N8D7M1 APK/source + G43 stage probes; only the
aligned tick-2050 frame may emit (same gates as N8D7M2). New text < 8 KiB.

- **W1 write witness (frontend, existing debug ring):** for tick window
  [1950,2050], one `[n8d7m3] writes` line: Draw counts by FBP (FBP112 plus
  top-3 others + total), `last112` / `lastCompetitor` Draw ticks,
  DISPFB1/2 change count, FRAME/BITBLTBUF/TRXREG register-write counts.
- **S1 selected baseline (no new code):** existing `[n8d7f]`/`[n8d7l]`
  metadata, 448-vectors (launcher-recomputed packed SHA; Android prints
  `unavailable`), 8 control words.
- **C1 candidate census (backend, same mapped `selected_vram_staging`):**
  fork-table decode at one same-run competitor (most-written non-112 FBP
  from W1; fallback same FBP112 opposite phase): `[n8d7m3] candidate
  fbp=.. phase=.. occupied=.. active=..` + 448 `candidate_tile_counts` +
  8 words at the candidate base. Addresses via
  `GSPSMCT32::addrPSMCT32(fbp<<5, 8, x+dbx, dby+phase+y*stride) & 0x3FFFFF`.
- **T1 timing flag:** at Present/vsync entry, `[n8d7m3] timing
  pending=<unprocessed GIF/draw count for tick <= 2050> drained=<0/1>`.
  Exact site (frontend Present entry vs renderer vsync entry) is fixed at
  implementation; one line either way.
- **Controls:** checkerboard `control=128`; 8 literal controls at selected
  and candidate bases; W1 null control (never-written FBP reads ~0 draws);
  Mac broad-frame positive control (§5).
- **Caps (future brief):** at most one build (default-OFF tap only) and one
  Odin launch (<= 300 s, I26-FAST, N8D7M1 pins, 16 MiB log cap); no raw
  4 MiB or asset bytes in git (checksums/counts + private scratch only).
- **Failure/OTHER:** stop at first aligned receipt+frame, first fatal, tick
  2100 without receipt, 180 s below tick 1700, 300 s wall; force-stop,
  PID-absent check, lease release (N8D7M2 §8 pattern).
- **Mac first:** validate the tap on the pinned N8D4 stream before any Odin
  build (expect W1 FBP112 >= K, S1 active 300, T1 drained); this sets K and
  the window, and needs no Android build.

## 5. What each outcome changes next (no cause declared)

- A: stop snapshot-path probing; next brief on the writer side (stream,
  pad route, movie bypass, GIF/Draw delivery to FBP112).
- B: next brief on selection/layout ownership (DISPFB vs FRAME target,
  promotion rejection, phase parity, DBX/DBY).
- C: next brief on snapshot timing (copy barrier incl.
  `COLOR_ATTACHMENT_OUTPUT`, flush ordering, bounded post-flush re-read).
- D: next brief on PSM/mask/wrap handling (CT24 word vs RGB decode,
  `&2047` wrap, `vram_size-1` mask).
- OTHER: re-gate; no new device run until the missing line is explained.

## 6. Exact commands read in this part (all read-only, from repo root unless noted)

`read` of N8D7M2 REPORT/ORCH-GATE/result.json/tile-excerpt.txt, N8D7L
REPORT/ORCH-GATE/replay-excerpt.txt, N8D7I/N8D7F/N8D7J/N8D7K reports,
N8D7J/N8D7K ORCH-GATEs, `local/AGENTS.local.md`, backend `:1-50/51-350/
351-700/701-820`; shell: `ls ssx3-work dirs`, three `grep -n` sweeps over
`gs_renderer.cpp`/`gs_interface.hpp`/`gs_util.hpp`, `sed -n` of renderer
`:4750-5089/:4396-4470/:4262-4340/:4321-4395`, `gs_interface.hpp:155-260`,
`gs_util.hpp:40-115`, `sample_circuit.frag:55-120`, `psmct32.h:1-45`,
`gs_frontend.cpp:540-600/750-780`, `gif_arbiter:1-60`,
`page_tracker.hpp:1-80`, renderer `:1116-1140`, PGS constant greps,
`git log -1`, `git status --short`, `git check-ignore/ls-files` on the brief;
one LSP hover (no results).

## 7. Missing links (plain)

- Frontend debug-ring Draw/Register field names and enablement beyond the
  cited record calls were not verified; implementer confirms the ring is
  readable at Present time within the log cap.
- Worker queue-depth observable site not located (`grep` over
  `gs_worker.cpp` for vsync/flush/submit returned nothing); T1 site falls
  back to renderer vsync entry if the queue is not observable.
- Scene-draw write path pinned only to ubershader/page-flush lines above;
  full draw-call chain not traced (not needed for the tap sites).
- No local PCSX2 third mapping (bytesize-only; ssh denied); fork-vs-G43
  remains the only independent pair (N8D7K §2 residual stands).
- LSP empty for out-of-repo files; links rest on the direct reads above.

## 8. Handback

| Deliverable | Status |
| --- | --- |
| `local/research/N8D7M3/REPORT.md` | written, < 512 KiB new text |
| Source edits / builds / boots | none |
| Cause declared | none |

Recommended next action (orchestrator decision): gate this design; if
accepted, Mac-validate the tap on the pinned N8D4 stream first, then cut a
one-build/one-launch Odin brief per §4 caps.
