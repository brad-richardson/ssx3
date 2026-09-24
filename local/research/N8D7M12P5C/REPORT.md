# N8D7M12 Part 5C — same-APK replay OFF-control design (read-only)

**State: DESIGN COMPLETE, outcome A. Read-only: no source/script edit
(outside this dir), build, replay, install, launch, lease, device,
stream/APK/env change, push, board/global edit, or upstream contact.
No control run is released from this design alone. No graphics
root-cause verdict. Text <512 KiB.**

Brief: `local/muse/prompts/N8D7M12P5C.md`. Question: smallest
same-APK, same-stream Odin control testing whether
selected/oracle/tile instrumentation perturbed the sparse ON replay.

## 1. Pins (all re-verified by `check.py`, 15/15 A)

| Item | Value |
| --- | --- |
| APK `~/dev/ssx3-work/N8D7M12P3/app-release.apk` | 153,753,116 B, `caa11102…f512` (fresh read; P5B had 2× local + 2× device) |
| Stream `~/dev/ssx3-work/N8D7M6/n8d7m6.gs` | 1,100,696,462 B, `f6a78f71…a593` (2 fresh reads) |
| Source base | fork `n8d7m12-app` @ `a608ed1` (worktree `~/dev/ssx3-work/N8D7M12P2/PS2Recomp`) |
| Mac Part 1 binary `~/dev/ssx3-work/N8D7M12/build/ps2xTest/ps2x_tests` | `2a0446e8…ae5`, still present |
| Mac ON `parallel.hashes` / `vq-002050.ppm` | `94b433df…` (2686 B) / `9490484c…` (688,143 B) |
| Odin ON `parallel.hashes` / `vq-002050.ppm` | `0e89a493…` (2686 B) / `39b70d67…` (688,143 B) |
| ON `result.json` verdict | `PROVISIONAL PASS`, markers queue/parallel 862958/11499/25445/2050, frame `2050 parallel ff21 b167a719` |

ON comparison recomputed from the two pinned hash files: **priv
41/41, VRAM 3/41 (ticks 100, 250, 1600), present 0/41, first VRAM
divergence tick50**; Mac tick2050 present `d19b96fe` vs Odin
`b167a719`. Odin selected 14/448, Mac 300/448 (P5B gate; Odin PPM
viewed mostly-black vs fuller Mac PPM).

## 2. Source/evidence citation table (@ `a608ed1`)

| # | Fact | Source |
| --- | --- | --- |
| 1 | Replay entered only when `PS2X_GS_REPLAY_ONDEVICE=1`; capture/backend/Turnip required; `_Exit(0/1)` with `[n8d7m12] replay ok/failed` | `ps2xRuntime/src/main.cpp:215-269` |
| 2 | Selected gate: `request.vsyncTick == 2050 && SELECTED==1`; tile gate: selected OR (`tick==2050 && TILE==1`); both feed `vsync.capture_*` | `ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp:439-446` |
| 3 | Oracle gated on `ORACLE==1` **inside** the `if (selectedRequested)` block (`:603`), so it runs only at tick2050 with selected on | same file `:603,667-669` |
| 4 | All three flags `strcmp(..,"1")==0`: unset/empty/`0` all disable | same file `:441-444,668` |
| 5 | `GB4_FRAME` + PPM dump gated only on `dumpTick` (`PS2X_GS_REPLAY_PPM_TICKS`), never on capture flags | `ps2xRuntime/src/lib/gs/gs_replay_core.cpp:115-130,447,460-472` |
| 6 | `GB4_REPLAY` rows gated only on sampling stride (`PS2X_GS_REPLAY_STEP`); `PS2X_GS_REPLAY_OUT` writes rows unconditionally | same file `:210-213,505-513,699-705` |
| 7 | Tile census lines (`[n8d5b]` control/sampled, `[n8d6a]` stages, `[n8d5b]` raw) gated on `tileRequested` | backend `:489,795` |
| 8 | Renderer extra work under `capture_selected_input`: 4 MiB VRAM staging copy + barriers (`:4800-4823`), circuit1 staging copy (`:5054-5073`); `capture_scanout_stages` only returns images (`:4983,5314`) — copies, no draw-path change | `~/dev/ssx3-work/N8D7F/parallel-gs/gs/gs_renderer.cpp:4759,4777,4983,5054,5314` |
| 9 | ON env (11 keys + PPM_DIR/OUT, no live keys) | `local/research/N8D7M12P5A/launch.py:71-79,82,620-621` |
| 10 | Mac ON/OFF precedent (different binary/stream): OFF `SELECTED=0 TILE=1` vs ON `SELECTED=1 TILE=1` on `66457eb4` + `n8d4.gs` gave byte-identical 41-row hashes (`f038cde9…`) and PPM (`8c85489e…`, 688,143 B) | `local/research/N8D7F/REPORT.md:40-51`, `~/dev/ssx3-work/N8D7F/run-receipt.json` |
| 11 | Mac same-binary control status: ON side exists (Part 1 exact-stream replay, §3 of its REPORT); OFF side with `2a0446e8` + `n8d7m6.gs` was never run | `local/research/N8D7M12/REPORT.md` §§3-4 |

Key discriminator (rows 2-4): the three flags take effect **only at
tick2050**. On every other tick both ON and OFF pass
`capture_*=false` to the renderer, so GB4 rows at ticks 50-2000 are
provably flag-independent. First ON divergence is at tick50.

## 3. ON/OFF variable matrix

| Variable | ON (gated) | OFF (proposed) |
| --- | --- | --- |
| APK / stream / backend / Turnip | `caa11102`, `f6a78f71`, parallel, `PS2X_GS_TURNIP=1` | identical |
| `PS2X_GS_REPLAY_ONDEVICE` | 1 | **1 (kept)** |
| `PS2X_GS_REPLAY_CAPTURE/BACKEND/STEP/PPM_TICKS/PPM_DIR/OUT` | capture, parallel, 50, 2050, unique dir, unique path | **identical incl. 2050 PPM + 41 sampled rows** |
| `PS2X_N8D7F_SELECTED_CAPTURE` | 1 | **absent (unset)** |
| `PS2X_N8D7L_ORACLE` | 1 | **absent (unset)** |
| `PS2X_N8D5_TILE_CAPTURE` | 1 | **absent (unset)** |
| Live keys (`PS2X_GS_CAPTURE*`, `PS2X_PAD_SCRIPT*`, `PS2X_CD_IMAGE`) | asserted absent | asserted absent |

Unset (not `=0`) is specified: source treats both as off, and absence
is unambiguous in the `ps2x.env` diff.

OFF still produces (rows 5-6): `GB4_REPLAY_SUMMARY`, 41 `GB4_REPLAY`
rows, `GB4_FRAME tick=2050`, `GB4_PARALLEL_STATS`, `vq-002050.ppm`
(688,143 B shape), `parallel.hashes`, `[n8d7m12] replay ok`.
OFF loses by design: `[n8d5b]/[n8d6a]` tile census, `[n8d7f]`
selected metadata/vectors, `[n8d7l]` oracle, sampled/raw 896-word
vectors. The ON selected 14/448 and Mac 300/448 numbers **cannot be
measured in OFF mode; they are not compared and not invented.**

## 4. Predicted outcomes (predeclared)

| Observation (OFF vs ON, same device) | Reading |
| --- | --- |
| 41 OFF rows byte-equal ON rows AND OFF PPM SHA == ON `39b70d67…` | **Persistent divergence**: instrumentation did not perturb the replay path; tick50 VRAM/present split vs Mac stands without the capture flags. Graphics cause still open. |
| OFF rows differ from ON at ticks ≤2000 | **Void/nondeterminism**: flags are unread on those ticks (§2), so any difference is device variance or harness fault, not instrumentation. Diagnose before any comparison. |
| OFF == ON at ticks ≤2000 but differs at tick2050 row and/or PPM | **Tick-2050 instrumentation effect**: the §2-row-8 extra staging/barrier/compute work at tick2050 perturbed the frame. Sparse result needs re-read with this confound. |
| OFF PPM fuller (broad) while ON sparse, rows ≤2000 equal | **Instrumentation-caused sparsity**: capture path perturbed tick2050 rendering. |
| Either run: control ≠128/128, `GB4_REPLAY_PARSE_ERROR`, `replay failed/rejected`, markers ≠2050 | FAIL/void; first error recorded, no comparison. |

Broad/sparse visual observation (orchestrator-viewed PPM only, no
threshold invented here): OFF PPM viewed against the ON mostly-black
`39b70d67…` frame — fuller OFF weakens any device/backend reading of
ON sparsity; still-sparse OFF strengthens persistence.

## 5. Exact unexecuted command/script-diff plan

Mac OFF replay (separate gate; one P-lane slot; Part 1 binary+stream):

```sh
python3 local/tooling/p_lane_lease.py claim 1 n8d7m12p5c-mac
PS2X_GS_REPLAY_CAPTURE=~/dev/ssx3-work/N8D7M6/n8d7m6.gs PS2X_GS_REPLAY_BACKEND=parallel \
PS2X_GS_REPLAY_STEP=50 PS2X_GS_REPLAY_PPM_TICKS=2050 \
PS2X_GS_REPLAY_PPM_DIR=~/dev/ssx3-work/N8D7M12P5C/mac-off \
PS2X_GS_REPLAY_OUT=~/dev/ssx3-work/N8D7M12P5C/mac-off/parallel.hashes \
GRANITE_VULKAN_LIBRARY=/opt/homebrew/lib/libvulkan.1.dylib \
~/dev/ssx3-work/N8D7M12/build/ps2xTest/ps2x_tests
python3 local/tooling/p_lane_lease.py release 1 n8d7m12p5c-mac
```

Diff vs Part 1 §4 command: drop the three capture flags; new
`mac-off` output dir; binary, stream, backend, step, PPM ticks fixed.

Odin OFF run (separate gate; new launcher required): copy
`local/research/N8D7M12P5A/launch.py` to a new P5C launcher deleting
exactly the three lines 75-77 (`SELECTED/ORACLE/TILE`) and re-pointing
unique PPM dir/hashes path; the P5A `--released-sha` guard means the
P5A SHA **cannot** authorize the OFF run — the new launcher needs its
own review + SHA gate. Single `install -r` + single `am start`,
≤600 s wall, battery charging ≥20%, free ≥10 GiB, keyguard=false
pre-install and pre-start (blocker, never worked around), BACK once,
force-stop + PID-absent + env 2+2 restore + lease release in
`finally`. No simultaneous host heavy job.

Budgets: at most one Mac OFF replay and one Odin OFF install/launch,
each in its own gate. No control run is released by this design.

## 6. Acceptance / stop rows

| # | Gate | Required | On failure |
| --- | --- | --- | --- |
| 1 | Pins: APK/stream/Mac-binary SHAs + sizes; source `a608ed1` | §1 exact | OTHER, stop |
| 2 | OFF env diff is exactly minus-three-flags; live keys absent | matrix §3 | stop, no run |
| 3 | OFF launcher is a fresh reviewed SHA (P5A SHA not reused) | new gate | stop, no run |
| 4 | OFF yields SUMMARY + 41 rows + `GB4_FRAME tick=2050` + PPM + hashes + `replay ok markers=2050` | §3 outputs | FAIL/void per §4 |
| 5 | Mac OFF rows vs Mac ON rows; Odin OFF rows vs Odin ON rows | §4 table | void on ≤2000-tick mismatch |
| 6 | Cleanup: force-stop, PID absent, env restored 2+2, lease freed; any failure flips outcome to FAIL | P5A rules | record first failure |
| 7 | No speed number from any diagnostic run; frame reading is orchestrator-viewed only | standing rules | — |

## 7. Source limitations checked (none blocks comparison)

- OFF cannot emit the selected/oracle census — predeclared as
  not-compared (§3), not a blocker: the comparison fields (41 rows,
  tick2050 present, PPM bytes) are flag-independent outputs (§2).
- Nondeterminism would void, not confuse: rows ≤2000 are a built-in
  flag-independent invariant (§4 row 2).
- N8D7F precedent (§2 row 10) is a different binary/stream: supporting
  evidence only, not a substitute for the §5 Mac OFF replay.

## 8. Verdict and handback

**A — discriminating bounded control plan.** One Mac OFF replay plus
one same-APK Odin OFF run, each separately gated, separate the
selected/oracle/tile instrumentation hypothesis from persistent
device/backend divergence using exact row/PPM fields. B does not
apply: no flag/output-path coupling prevents the comparison.

| Deliverable | Path |
| --- | --- |
| This report | `local/research/N8D7M12P5C/REPORT.md` |
| Checker (15/15 A; proves pins + ON comparison + source rows; states OFF unproved) | `local/research/N8D7M12P5C/check.py`, `check-result.json` |

Receipts: `check.py` exit 0, verdict A. Commit `[N8D7M12] Part 5C`
with `Orchestrated-By: opencode`, explicit named paths, no push.

(End of file)
