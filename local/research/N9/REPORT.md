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
