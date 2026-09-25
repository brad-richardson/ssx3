# N9 Part 1 — sort, branch, Mac build (worker receipt)

Worker: Muse Code. Brief: `local/muse/prompts/N9.md` (Part 1 only; no device, no pushes).
Scratch: `~/dev/ssx3-work/N9/` (fork clones + build). **No pushes made.**

## 1. Pins

| Repo | Ref | SHA |
| --- | --- | --- |
| paraLLEl-GS fork `ssx3` | `origin/ssx3` fresh clone | `3b1ca9e281c61ef8ee3a63e77780106851cf7e13` |
| Granite fork (`ssx3` gitlink) | submodule fresh init | `46db18a89b18439b37c515bf1a1bafb86e7ea234` |
| N8D7F snapshot (super) | `ssx3-n8d7f-snapshot` in `~/dev/ssx3-work/N8D7F/parallel-gs` | `b4137544d8ead5b0f01277c53ae001a2f46c3c22` |
| N8D7F snapshot (Granite) | same worktree submodule | `36ae0d0b85ddfabddb8d12c0048aa3ade699bcaa` |
| PS2Recomp fork `ssx3` | `fork/ssx3` | `959f4ea7a8286505e14cdb1a14617c4e99ed4062` |
| N8B1 commits | `n8-turnip-apk` | `a4babc6`, `17e90de` (parent `4f93216`; NOT in `959f4ea`) |

N8D7F superproject + Granite worktrees are clean (no uncommitted content beyond the snapshot
commits). Snapshot already contains the fork's replayer HAL-loader + G26 hunks
(`PGS_G42_TURNIP|disable_sampler_feedback`: 5 matches on both sides), so the diff is
snapshot-additive. `.gitmodules` (fork points at `brad-richardson/Granite`) is kept as-is.

## 2. Classification table (fork `ssx3` → snapshot)

Backend call surface at `959f4ea` (`ps2_gs_parallel_backend.cpp`, 442 lines): `GSInterface`,
`init`, `set_debug_mode` (`dm.feedback_render_target=false`, G26-corrected), `flush`, `vsync`
(sets only upstream `VSyncInfo` fields: `phase/dst_layout/dst_stage/dst_access` +
`adapt_to_internal_horizontal_resolution`), `get_priv_register_state`, `gif_transfer`,
`write_register`, `map_vram_read/write`, `end_vram_write`, `read_transfer_fifo`,
`reset_context_state`; reads only `shot.image`. `git grep` over `ps2xRuntime` at `959f4ea`
for every snapshot-only symbol (`g40_*`, `capture_selected_input`, `capture_scanout_stages`,
`selected_*`, `n8d5`, `PGS_SKIP_SAMPLER_FEEDBACK`, `PGS_G40_WALL`, `PGS_G41_CANARY`,
`supports_descriptor_buffer`) returns **zero hits**.

### 2a. Superproject: 31 hunks + 3 new files — ALL diagnostic

| # | File:base-line | Content | Class | Why |
| --- | --- | --- | --- | --- |
| S1 | `gs/gs_interface.cpp:9` | G40/G41 file statics + helpers + `<cstdlib>` | diagnostic | env-gated probe state, never called by backend |
| S2 | `gs/gs_interface.cpp:132` | G40/G41 `flush_render_pass` entry (ordinals, census) | diagnostic | logging + counters only |
| S3 | `gs/gs_interface.cpp:298` | G11 record-batch identity LOGI | diagnostic | logging |
| S4 | `gs/gs_interface.cpp:348` | G40 wall end (O1/O2/O2x/O3/O3b/O4/O4m/O5) + G41 end (cord join, hash breakdown, canary kick, self-restoring) | diagnostic | env-gated (`PGS_G40_WALL`/`PGS_G41_CANARY`), default off |
| S5–S8 | `gs/gs_interface.cpp:1257,1661,1707,1804` | G40 tex reuse/made/resolve counters | diagnostic | counters only |
| S9 | `gs/gs_interface.cpp:2484` | G41 kick-time register snapshot | diagnostic | env-gated state copy |
| S10–S13 | `gs/gs_interface.cpp:2573,2604,2786,2835` | G40 kick bb/fuse/acc counters | diagnostic | counters only |
| S14 | `gs/gs_interface.cpp:2872` | G40 kick seen/adc/deg counters | diagnostic | counters only |
| S15–S16 | `gs/gs_interface.cpp:3896,3905` | G11 FRAME_1/FRAME_2 LOGI | diagnostic | logging |
| S17 | `gs/gs_interface.cpp:4266` | G11 `flush()` census LOGI | diagnostic | logging |
| S18 | `gs/gs_interface.cpp:4685` | G31 vsync split probe | diagnostic | read-only probe + LOGI |
| S19 | `gs/gs_interface.hpp:155` | `VSyncInfo.capture_scanout_stages/capture_selected_input` | diagnostic | N8D7F selected capture + scanout-stage flags; backend never sets them |
| S20 | `gs/gs_renderer.cpp:1588` | `g40_record/finish_probes` + FNV helper | diagnostic | called only from S4 |
| S21 | `gs/gs_renderer.cpp:3485` | G22 `PGS_SKIP_SAMPLER_FEEDBACK` skip | diagnostic | env-gated experiment workaround, default off; no `ps2xRuntime` ref at `959f4ea`; live env (N8D2 `ps2x.env`) never sets it |
| S22–S25 | `gs/gs_renderer.cpp:4622,4638,4797,4867` | selected-capture record + VRAM/circuit1 staging copies | diagnostic | N8D7F selected capture; gated on S19 flag |
| S26 | `gs/gs_renderer.cpp:5102` | `pre_deinterlace_merged` capture | diagnostic | scanout-stage capture; gated on S19 flag |
| S27–S29 | `gs/gs_renderer.hpp:23,292,331` | `ScanoutResult` capture fields, g40 decls, g40 members | diagnostic | support S20/S22–S26; backend reads only `image` |
| S30–S32 | `gs/n8d5_tile_spirv.hpp` + `gs/shaders/n8d5_tile.comp/.spv` (new) | N8D5 tile probe | diagnostic | unreferenced: not included anywhere in the snapshot tree |
| S33–S34 | `tools/gs_dump_replayer.cpp:241,275` | G8/G10/G29/G30 scanout/stats/VRAM hooks | diagnostic | replay-tool additions; replayer unused by the recomp backend |
| — | `.gitmodules` | snapshot points at `Themaister/Granite` | keep fork | not ported to either branch |

### 2b. Granite: 2 hunks — 1 product, 1 diagnostic

Fork `46db18a8` already contains the snapshot's other 3 files (`platforms/CMakeLists.txt`,
`timer.cpp`, `memory_allocator.cpp` incl. the G28 guard — identical, no diff). Remaining:

| # | File:base-line | Content | Class | Why |
| --- | --- | --- | --- | --- |
| G1 | `vulkan/shader.cpp:528` | G18: gate `create_update_templates()` on derived `supports_descriptor_buffer` instead of the raw feature bit | **product** | G-lane fix. Same predicate `CommandBuffer` uses for the flush path (`command_buffer.cpp:108,1166,1594`); `context.hpp:79` exists in fork HEAD. Raw-on/supports-off is exactly Adreno 830 (G28 receipt), the shipped config; without it the legacy path passes NULL to the driver. All validated N8D7F/M12/X1 builds ran with it. |
| G2 | `vulkan/command_buffer.cpp:1195` | G20 pre-create compute-pipeline LOGI | diagnostic | logging only |

## 3. Branches (all local; clones under `~/dev/ssx3-work/N9/`; no pushes)

Clone: fresh `parallel-gs` fork `ssx3` + Granite submodule from
`brad-richardson/Granite`, then `git submodule update --init --recursive`
(Granite `third_party/*` needed to configure). Snapshot reached via a local
`n8d7f` remote (no network for snapshot bytes).

| Branch | Commits (oldest first) | Head SHA |
| --- | --- | --- |
| Granite `ssx3-next` | G18 product hunk (G1) | `166ba21a247a681903cc9d0bb6562fe50a554c85` |
| Granite `wip-next` | `ssx3-next` + G20 diagnostic (G2) | `24fb882fc164fe5864f7659a1df02d01efb501bd` |
| super `ssx3-next` | N8X1 wave64 fix (separate, cites N8X1) + Granite gitlink → Granite `ssx3-next` | `963cb57503245e31efb2df89a4740cd4da66513b` |
| super `wip-next` | `ssx3-next` + S1–S34 diagnostic hunks (one commit) + Granite gitlink → Granite `wip-next` | `2632711772bced49779103e1505c3783e4045ba3` |

Fix commit: `495cb69`; diagnostics commit: `baddb36`. The N8X1 clean diff
applied verbatim (`git apply --check` OK on `3b1ca9e`; snapshot regions don't
overlap it). No superproject product hunks exist, so `ssx3-next` content =
fork `ssx3` + fix + the Granite pointer. The gitlink bumps are separate
commits so the orchestrator can drop them; without the bump, fork-tip builds
would silently lack G18. Verification: `wip-next` vs snapshot over
`gs/ tools/` differs by exactly the 10-line fix; Granite `wip-next` ==
snapshot Granite (empty diff); `.gitmodules` keeps the fork URL on both
branches. The applied diagnostic diff had 1 pre-existing trailing-whitespace
warning (snapshot's `G40 O1\t` line), kept verbatim.

## 4. PS2Recomp `n9-android`

Worktree `~/dev/ssx3-work/N9/PS2Recomp` from `959f4ea`, branch `n9-android`:

- `f5e6378` cherry-pick `a4babc6` ([N8B1] Turnip backend) — clean, no conflicts.
- `fb11e18` cherry-pick `17e90de` ([N8B1] diagnostics off) — clean, no conflicts.
- Head: `fb11e182310555c65201635f8d6c7fe8e170de74`. **No third commit:**
  PS2Recomp has no submodules (no Granite gitlink), and
  `PS2X_PARALLEL_GS_SOURCE_DIR` is a build-time-only cache var (empty default;
  Gradle `-Pps2xParallelGsSourceDir`, no hardcoded checkout path), so nothing
  in-repo must change to point at the fork clone.

Runner-dir guard: `git diff --stat 14b1e5cb n9-android -- ps2xRuntime/src/runner`
→ empty, RC=0.

## 5. Mac build + suite (1 build; taps OFF; shadow ON vs `ssx3-next`)

Submodule checkout at build time: super `963cb57` + Granite `166ba21a` (both
`ssx3-next`), worktrees clean. First configure failed only on the missing
Granite `third_party` submodules (fresh-clone setup gap, fixed with
`--recursive` init, no source change); configure re-run from a clean build dir.

Exact commands:

```sh
cmake -S ~/dev/ssx3-work/N9/PS2Recomp -B ~/dev/ssx3-work/N9/host-build -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_DIAG_TAPS=OFF \
  -DPS2X_GS_SHADOW_PARALLEL=ON \
  -DPS2X_PARALLEL_GS_SOURCE_DIR=/Users/brad/dev/ssx3-work/N9/parallel-gs
cmake --build ~/dev/ssx3-work/N9/host-build --parallel 8 --target ps2x_tests
cd ~/dev/ssx3-work/N9/PS2Recomp && ../host-build/ps2xTest/ps2x_tests
```

| Step | Result |
| --- | --- |
| configure | RC=0 (`G44 parallel-gs shadow backend ON (standalone, from …/N9/parallel-gs)`) |
| build `ps2x_tests` | RC=0, 324/324 Ninja steps (sole `error` grep hit is `dwarf_error.c.o`; ld duplicate-lib warning only) |
| suite (from worktree root) | **593/593 passed, 0 failed** |
| N8D7M12 Mac replay control | **not run**: replay core (`ps2xRuntime/.../gs_replay_core.{h,cpp}`) is absent on `959f4ea`/`n9-android` (only `ps2_gs_replay_tests.cpp` exists; the core lives on branch `n8d7m12-replay-core`), as the brief predicted |

Full logs (scratch, not in git): `~/dev/ssx3-work/N9/{configure,build,suite}.log`.
Disk: N9 scratch 2.7 GB of the 20 GB lane cap; global `161.5/200 GB` (check exit 0).

## 6. Receipts

- `REPORT.md` (this file; classification table §2).
- `super-ssx3-vs-snapshot.diff` — `git diff 3b1ca9e b413754` (`--binary`, excl. `Granite`; 92 KB).
- `granite-ssx3-vs-snapshot.diff` — `git diff 46db18a8 36ae0d0b` (2.4 KB).
- `build-receipt.txt` — exact build/suite commands + suite tail + guard output.

Gaps: the clean N8X1 diff is compiled here (Mac `ps2x_tests` incl. renderer TU)
but its wave64 path is Apple-unreachable, so this build doesn't execute the fix
(N8X1 row 10 same gap); first live run of the default path is Part 2's job.
No speed numbers (diagnostic build; suite only, no boot).

---

# N9 Part 2 — one APK from pushed tips + live Odin race (worker receipt)

Gate `ORCH-GATE-P1.md` verdict A; pushed tips confirmed before use:
`parallel-gs ssx3=963cb57` (fresh `--recursive` clone: super `963cb57`,
Granite `166ba21a` from `brad-richardson/Granite`), `PS2Recomp ssx3=fb11e18`
(`git ls-remote` + fetch). Battery rule per Brad: AC + level ≥ 20 %, status
ignored (launch script enforces it). No `PS2X_PGS_*` env anywhere (asserted in
`launch.py`, re-checked by `check.py`). One `assembleRelease`, one Odin launch,
no push.

## 7. Inputs (all double-read)

| Input | Pin |
| --- | --- |
| parallel-gs fork `ssx3` | fresh clone `963cb57`, Granite `166ba21a`, `.gitmodules` = fork URL, `--recursive` populated |
| PS2Recomp fork `ssx3` | `fb11e18` (`git archive` export, 327 files; wrapper props `3d91f093…` = external pin) |
| canonical codegen | 9,457 files; `register_functions.cpp` `8ea8ed43…` ×2 (matches N8B1 pin) |
| Turnip v36 | `717812c3…` ×2, 14,188,488 B |
| HAL shim | `1b49d27c…` ×2, 7,112 B |
| staged aggregate | `22c30bd2…` (34,096 files; codegen bytes 266,831,289 = P6M5 byte-exact) |

Staged bytes verified: N8X1 fix present, G18 present, zero diagnostic-knob
strings in `gs/`+`tools/`, Turnip backend present in fork. Gate string sets
were derived from staged sources: 7 present-strings in fb11e18 backend
sources; 17 absent-strings (replay/diagnostic/`PS2X_PGS_HIER`) verified absent
from staged fork+parallel sources (`PS2XGSC1` excluded: it is product
stream-capture code on fb11e18).

## 8. One bytesize build (`/home/brad/n9`)

Preflight: root absent, toolchain + governor present, `HEAVY_JOBS []`, 729G
free. Transfer: 777,011,200 stream bytes, 6 top-level entries (36,662 benign
LIBARCHIVE xattr lines condensed per P6M6R precedent). Collector verify pre
**and** post: `status=match`, aggregate `22c30bd2…`, added/missing/changed
empty; staged `runner/` holds only the 438 B upstream stub (`cf62c485…`).
Wrapper pins: gradlew `a3648413…`, jar `49849512…`, props `3d91f093…` (all ×2),
props equal, no wrapper script/jar in new root.

`build.sh` (the one build): `BUILD SUCCESSFUL in 14m 24s`, 48/48 tasks, zero
`FAILED`. Compiled inputs: 449 `compile_commands` entries incl. fork
frontend/worker/parallel-backend + `gs_interface.cpp` + `page_tracker.cpp` +
Granite `memory_allocator.cpp`; 296 `ps2_game_objects` unity batches incl.
`register_functions.cpp` + all 9,455 codegen `.cpp`.

APK gate (`apk_gate.py`, RC=0, `status=pass`; `apk_facts.py` 11/11):

| Item | Value |
| --- | --- |
| APK | `25711bfe…08152`, 153,703,964 B (×2 WSL, ×2 Mac; new vs P6M6) |
| runner | `96e61f3b…205c4a`, 139,466,552 B (member ×2 + extracted ×2); Build ID `4426b8b3…26fc1d6` (new vs P6M6) |
| Turnip / HAL members | `717812c3…` / `1b49d27c…` (pins equal; exact 3-member arm64 set) |
| strings | 7/7 Turnip/HMI/HAL present; 0/17 replay/diagnostic present |
| arm64 cache | sole `…/321k3v65/arm64-v8a/CMakeCache.txt`: 6 flags OFF, `SHADOW=ON`, new-root parallel + codegen dirs, `RelWithDebInfo` |

## 9. One Odin launch (I26-FAST vsync route, no knob env)

Preflight: device, lease free, keyguard `showing=false`, battery 90 % status 3
on AC. Claimed `N9 one-launch`; `adb install -r` Success; installed-APK/ELF/
ISO SHAs all ×2 match; `mc0` empty; saved orig `ps2x.env` (`176eff84…`);
pushed N9 env (parallel + Turnip + movie bypass + route + dumps 1840/1950/
2050); second preflight green. PID 16273, BACK sent for USB dialog.

| Screen | Trigger | SHA | Reading |
| --- | --- | --- | --- |
| `menu.png` 1920×1080, nonblack 0.647 | guest tick 1170, t=41.2 s | `09071b72…` (×4) | **Drawn**: Select Event, Snow Jam / Metro-City / Happiness, track map, description; widescreen |
| `race.png` 1920×1080, nonblack 0.650 | host dump tick 2050, t=117.5 s | `74669f82…` (×4) | **Drawn**: 2ND/2, 00:00:05, snow terrain, rider, HUD, EA Radio card; widescreen |

Host dumps: ticks 1840/1950/2050, 512×448, fbp 112/112, fallback=0,
fnv1a `1a297d49`/`4a725fa0`/**`4483c15c` — the tick-2050 hash byte-matches
N8X1's fixed (`off`) run**, so the fork-tip default path reproduces the
validated bytes with no knob env. No fatal loader/backend/crash line in the
same-PID log. Force-stop after run (PID gone), `ps2x.env` restored
(`176eff84…` ×2), lease `LEASE_FREE N9 done`, launch-to-exit 119.2 s (within
180/240 caps). Fine horizontal stripes visible on both screens (known since
N8D2, not investigated).

Not black → no stop. No speed claim (frame dumps were on; rate lines are
diagnostic).

Gaps: host dump PNGs don't exist on this fork rev (only `.txt` sidecars —
`ps2_runtime.cpp` mentions PNG only in comments since the P6M6-era rev change;
same gap as N8X1); screen evidence is the device screencaps. `.txt` sidecars
pulled under a 10 s follow-up lease (`LEASE_FREE N9 sidecars done`).

## 10. Part 2 receipts

Scripts: `preflight.sh`, `transfer.sh`, `source_verify.sh`, `wrapper_pins.sh`,
`build.sh` (the one build), `compiled_inputs.sh`, `codegen_graph.sh`,
`apk_gate.py`, `apk_facts.py`, `check.py` (16 rows, verdict A), `launch.py`.
Outputs: `preflight.txt`, `transfer.txt`, `transfer-bytes.txt`,
`transfer-tar.err` (empty), `source-verify-pre/post.json{,.err}`,
`wrapper-pins.txt`, `build.txt`, `compiled-inputs.txt`, `codegen-graph.txt`,
`apk-gate.json` (+`.err` empty), `apk-facts.json` (+`.err` empty),
`apk-fetch.err` + `cmake-cache-fetch.err` (empty), `menu.png`, `race.png`,
`upload-{0,1,latest}.txt`, `ps2x.env`, `result.json`, `driver.log`,
`logcat-pid.txt`, `check-result.json`. `source-manifest.json` (9.2 MB) stays
untracked per P6M5 precedent; APK + CMakeCache stay in scratch
(`~/dev/ssx3-work/N9/`). WSL root `/home/brad/n9` left in place (~8 GB).
Scratch 4.9 GB of the 20 GB lane cap.

## Orchestrator gate (2026-09-24)

**Part 1 A** (branches verified minimal fast-forwards, pushed; see `ORCH-GATE-P1.md`).
**Part 2 A.** Read §7–§10 and commit `022e2af1`. Independently: screencap SHAs `09071b72…`
(menu) and `74669f82…` (race) re-read; viewed both (`~/dev/ssx3-work/N9/orch-n9-screens.png`):
Select Event menu and the race at 00:00:05 (terrain, rider, HUD, radio card) are fully drawn on
the Odin screen. Device left clean (lease `LEASE_FREE N9 sidecars done`, app not running). The
tick-2050 host-dump hash `4483c15c` equals N8X1's fixed run, so the fork-tip default path (no
`PS2X_PGS_*` env) reproduces the validated output. **The Odin milestone "stock race renders live"
is now reproducible from committed fork code** (PS2Recomp `fb11e18`, paraLLEl-GS `963cb57`, Granite
`166ba21a`; APK `25711bfe…`). Loose ends: the image doesn't fill the Odin screen (margins),
fine horizontal stripes, missing sky (also Mac), no speed number yet (diagnostic dumps on).
