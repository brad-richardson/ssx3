# E25 experiment contract — written BEFORE the first copy, rename, configure or build

| Field | Bound / observable |
|---|---|
| Lane | E25 — rebuild runner + suite from fork `3adc0478b6d2260acdd28a249466f2eef9a20176`, re-establish the verification set without a boot, and assemble the re-baseline evidence. |
| Time box | Start `2026-09-22T12:03:15Z`; deadline `2026-09-22T20:03:15Z`; eight hours. |
| Required reads (all of each, before the first action) | `local/muse/prompts/E25.md`; `local/research/E24/REPORT.md` (166 lines); `local/research/E23/REPORT.md` (144 lines); `local/research/E18/NEXT-BRIEF.md` (41 lines); E18's build records (`configure-command.json`, `e18_configure.py`, `e18_common.py`, `build-driver.txt`, `build-source-only-driver.txt`, `built-binaries.json`, `configure.log`). |
| Hypothesis | **H0**: the E18 recipe rebuilds a runner + suite that is *behaviourally* identical to the lost pins — 458/458 unloaded and observer-LOADED, E15/E16/E18 R1–R6 all reproducing E23's retained receipts — while the binary SHA differs (derived output, not reproducible bit-for-bit). **H1**: the rebuild is bit-identical and no re-baseline is needed. **H2**: the rebuild differs behaviourally, in which case the checkpoint stays red and nothing is re-baselined. |
| Result | Recorded in `REPORT.md`. This lane **tables**; the orchestrator decides the re-baseline. |
| Alternatives | (a) bit-identical rebuild (H1); (b) SHA differs, behaviour identical (H0); (c) behaviour differs (H2 → table + stop, no re-baseline on red); (d) the recipe is ambiguous or the build fails (→ table the ambiguity + candidate readings, continue the unambiguous remainder). |
| Observable | Per-path present/missing inventory; fork triple-agree; 9,457 generated name/hash audit; 1,725 protected-hash audit; every build command with argv, rc, elapsed, stdout receipt; new runner/suite size+sha; suite pass/fail counts unloaded and observer-LOADED; E15/E16/prior/absorbed rc; E18 R1–R6 fixture behaviour compared field-by-field against E23's retained receipts; an explicit OLD-vs-NEW pin table. |
| Strict order | Contract → admission → fork triple-agree (**first gate; any fork red → table + stop**) → loss inventory → tooling rename + proof → configure → build → binary pins → unloaded regression → observer-LOADED regression → fixture behaviour compare → re-baseline table → durability snapshot → fix gate (N/A) → close. |
| **Boot / lease** | **NO title boot. NO lease claim. No `boot-attempt.json`.** Suite runs and fixture runs are not boots. Any step that needs a boot is tabled for E26 and that line stops. `pgrep -x ps2EntryRunner` asserted rc 1 at open and close; `/tmp/ssx3-p-lane-lease` asserted absent at open and close. |
| Forbidden | Any fork source edit, commit or push. Any regeneration / CSV work (regen need = stop). Any deletion or reclaim. Any observer rebuild (the E21 dylib is reused by copy + re-sha). Any `stdbuf` in any argv. Testing the restore procedure by deleting anything. |
| Fix gate | **N/A** — no diagnosis, no code changes, no fork commits. Recorded as N/A with its receipt, not skipped silently. |
| Preserved constraints (E18 ABI, BINDING) | Caller-owned synchronous `HleCall` dispatch; `(mpeg,cbData,userdata)` with word0-only cbData; callback `v0` discarded, no `v0`→EOF rule; valid-no-input must remain waiting; collect under the MPEG mutex, dispatch outside; AddBs re-entry; registration order/dedupe; delete/reset cancellation; free cbData in `onComplete`. E25 changes **no** source, so every constraint is preserved by construction — the rebuild is from the unmodified fork tree at `3adc0478`. |
| Contract source | This file, written before the first copy, rename, configure or build. Amendments, if any, declared in their own file with a diff before use. |

## Byte caps, declared up front

| Cap | Value | Rationale |
|---|---|---|
| Internal (`/private/tmp`) reservation | **3 GiB** for E25-owned internal paths (the rebuilt tree + evidence + scratch). | The brief sets internal ≤3 GB delta. E18's measured full tree was **1,870,770,176 B** allocated (`build-source-only-driver.txt`). E23's amendment A1 shrank the reservation to 512 MiB *because E23 ran no full build after its relink*; E25 **must** run a full build, so the reservation is re-expanded to the brief's 3 GiB and declared here rather than amended mid-run. |
| Internal floor | free ≥ 2 GiB + 0.5 GiB guard, unchanged. | Carried from E18/E23/E24 unchanged. |
| SSD reservation | **16 GiB** in NEW `e25-*` paths only. | Brief. Snapshot + fixtures + tooltmp live here. |
| SSD floor | free ≥ 2 GiB + 0.5 GiB guard, unchanged. | Carried unchanged. |
| Growth elsewhere | **0** — fork tree, generated sources and every non-`e25-*` path. | Measured as positive-growth delta against the open sample. |
| `COPYFILE_DISABLE=1` | On every SSD step. | Carried; ExFAT AppleDouble discipline. |
| Known measured hazard | E23 measured a single thin-LTO **relink** costing **2.93 GB** of internal volume that was **not returned** (cause: `com.apple.cache_delete`, not swap, not a snapshot, not a findable file). A full build is larger than a relink. The internal floor + guard is the gate that catches it; if the floor trips, the build **refuses** rather than deleting anything. |

## Re-baseline discipline

- E25 **computes and tables** every old-vs-new pin. It does **not** declare a new
  baseline, does not rewrite any prior lane's receipts, and does not touch E24's
  directory (read-only reference).
- A rebuilt runner is **expected** not to match the pinned SHA (E24: *"A rebuilt
  runner will not match the pinned SHA — that re-baselining decision is the
  orchestrator's, not this lane's."*). The lane's job is to make the delta
  **explained**, not to make it disappear.
- Nothing that survived is rebuilt: the E21 observer dylib and both SSD fixture
  binaries are reused by **copy + re-sha**.

## Errata carried (do not re-fix)

- **E21-E1** — stale harness size/sha in E21's REPORT.
- **E23-E1** — a mechanical rename rewrote `e23` inside a hex digest; use the
  hex-safe rename + hex-run-equality proof.
- **E23-E2** — `MPEG.cpp:2467` / `:2498` are the actual line numbers.
- **E24-E1** — the blocked semaphore set is `26/30/31/32/36`; E23's REPORT and
  NEXT-BRIEF omit 31. The primary record confirms 31.
- **E24-E2** — the tail receipt must be recomputed **after** the last edit to
  `REPORT.md`; a stale tail receipt fails the gate.
- **E24-E3** — slice lengths: **four** 177 B slices; slice 28 is 191 B raw /
  176 B to the last non-zero byte. The JSON was right; E24's REPORT prose
  ("two are 177 B", "slice 28 is 176 B") is the errata.

# E25 CONTRACT TAIL COMPLETE
