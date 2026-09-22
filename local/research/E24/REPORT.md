| E24 | Receipt |
|---|---|
| Stop point | **Checkpoint RED — no boot spent.** The host restart between E23's close and E24's open wiped `/tmp`, taking all three protected build trees (1,725/1,725 files, 1,578,996,782 B) including `ps2EntryRunner` and the 458-test suite. The brief's mission 1 says *any red → table + stop, no boot on red*; the boot-authorization gate refused and the capture driver refused before the lease. Everything the block does not touch was executed in full. Fix gate: **STOP**. |
| Checkpoint | Fork `3adc0478b6d2260acdd28a249466f2eef9a20176` triple-agreed at open and close; 9,457 generated names/hashes equal; 21 E18 input/behavior source hashes equal; both SSD fixture binaries sha-equal; reused observer sha-equal. **BLOCKED:** 1,725 protected build hashes, the runner binary, the suite binary (and with it the 458 counts and the E18 R1–R6 suite text). |
| Questions reached | Objective **3 CLOSED** (title dims derived: **512 × 448**). Objective **1b CLOSED** (thread 4's wakes attributed exactly). Objective **2** closed on its static half and on the wait/signal ledger; the per-signal waker `ra` needs the boot. Objective **1a NOT reached** — it is the one question that strictly requires the new watch set, and the boot could not run. |
| Mutations / launches | Zero fork source edits, zero fork commits, zero pushes, zero regeneration, zero relinks, zero observer rebuilds, **zero title boots, zero lease claims**. |
| Next dependency | Restore a runner+suite build, then spend the designed boot. E24 hands over the boot design, the extended watch set, the patched driver and its gates, all pre-registered. |

| Experiment contract | Bound / observable |
|---|---|
| Time box | Start `2026-09-22T11:31:22Z`; deadline `2026-09-22T19:31:22Z`; eight hours. Final audit `2026-09-22T11:45:17Z`. **Actual time used: 13 min 55 s** (open → final audit), well inside the box. |
| Required reads | E24 prompt, E23 REPORT 139 lines + NEXT-BRIEF 22 lines + CADENCE 130 lines, E22 REPORT 134 lines, E18 NEXT-BRIEF 41 lines — all read in full including tails, before any copy, rename or run. |
| Hypothesis | **H0**: the successor descriptor node and the `0xd48748+` region are also silent post-park, so E23's KILLED verdict is exhaustive. **H1**: one of them moves, so E23's verdict was watch-set-limited. |
| Result | **Neither decided.** H0/H1 are decidable only by the boot, and the boot was barred by a red checkpoint. This is reported as un-decided, not resolved by inference. |
| Alternatives | (a) silent post-park; (b) moves post-park; (c) the semaphore wait resolves upstream and MPEG is symptom; (d) observation fails. **(d) realised, and by a cause outside the experiment** — the instrument binary ceased to exist. (a)/(b) untested; (c) partially advanced by static and retained-artifact evidence. |
| Observable | What was obtainable without a boot: the retained 5,040 B payload, the retained e23a park snapshot / boot log / 127 MB function log, and the 9,457-file recompiled image. |
| Strict order | Contract → admission → checkpoint → loaded regression → boot design → boot gate → (REFUSED) → mine → fix gate → close. Opened in order; the red gate stopped the boot exactly where the brief says it should. |
| Fix gate | Closed: **STOP**. `fix-gate.json`. |
| Preserved constraints | Caller-owned synchronous dispatch; word0-only cbData; v0 discarded; valid-no-input waits; dispatch outside the MPEG mutex; delete/reset cancellation. No CSV, main, scheduler or stream-callback edits. Nothing was edited at all. |
| Contract source | `CONTRACT.md`, written before the first copy, rename or run. **No amendment declared** — E23's amendment A1 is carried (internal reservation 512 MiB, floor and guard untouched) and was never approached, because E24 ran no build step. |

| **The red gate** | Receipt |
|---|---|
| Trigger | Host restart between E23's close (`2026-09-22T00:23:30Z`) and E24's open (`2026-09-22T11:31:22Z`). Every surviving `/tmp` entry is dated 07:18–07:27 today. |
| Lost | `/tmp/p1-link` **575 files / 526,188,690 B**; `/tmp/e17-map-link` **575 / 526,234,570 B**; `/tmp/e18-mpeg-link` **575 / 526,573,522 B**. **1,725 of 1,725 protected files, 1,578,996,782 B. Zero present.** |
| The two that matter | `ps2EntryRunner` (163,529,696 B, `e462e448…67e22`) and `ps2x_tests` (5,695,128 B, `2152e5ad…f04c0`) — the binary every E15–E23 receipt was taken on, and the suite that carries the 458 counts and the E18 R1–R6 text. |
| Recovery searched and excluded | `tmutil listlocalsnapshots /` returns no snapshots. A size-exact search across the whole SSD for 163,529,696 B / 5,695,128 B returns **nothing**. DerivedData holds only CMake probe directories. The SSD's `tmp-evacuated-0918` / `laptop-evacuated-0918` trees predate these builds. |
| What survived | The ELF, the ISO and the game data; **both** SSD fixture binaries (`e18-fixtures/after/binding-test` `42d9f4f3…87326`, `e23-fixtures/complete/binding-test` `3136f3ca…79a2`) sha-equal; the reused observer dylib sha-equal; every retained e23a artifact (boot log, syscall trace, park snapshot, E7 tap, parser events + payload, the 127 MB function log). |
| **Nothing irreplaceable was lost** | The fork is at `3adc0478…` unchanged, all 9,457 generated sources and all 21 E18 behavior/input sources are hash-equal. The lost trees are **derived output, rebuildable from intact inputs**. A rebuilt runner will **not** match the pinned SHA — that re-baselining decision is the orchestrator's, not this lane's. |
| Why no rebuild here | A rebuild is a protected-build command the contract reserves, it would break the one-variable control that makes the designed boot comparable to `e23a`, and E23 measured that a single thin-LTO **relink** already cost 405 s and 2.93 GB of internal volume that was not returned. |

| Checkpoint, gate by gate | Status |
|---|---|
| Fork triple-agree (`HEAD`, `refs/remotes/fork/ssx3`, `ls-remote`) | **VERIFIED** at `3adc0478…`; `status --short` exactly `?? ps2_log.txt` |
| 9,457 generated names/hashes | **VERIFIED**, every SHA256 equal to E18's manifest |
| E18 input/behavior source hashes (21 files) | **VERIFIED**, gzipped into `sources/` |
| E18 fixture binary | **VERIFIED** 165,183,488 B, sha-equal |
| E23 cadence fixture binary | **VERIFIED** 165,202,160 B, sha-equal |
| Reused observer dylib (copy + re-sha, never rebuilt) | **VERIFIED** `e4d88fdc…b38e6be`, 52,472 B |
| Prior actual bindings | **VERIFIED** 24 / 3 / 14 / 4 / DROP, rc 0 |
| E15 no-input / input | **VERIFIED** both rc 0, `saved128=1 waitReason=6 callbackCalls=1 resumes=0` |
| E16 closure, six modes | **VERIFIED** all rc 0 |
| Absorbed entries | **VERIFIED** 5 presence checks + 3 ownership controls, all rc 0 |
| Observer-LOADED fixture regression | **VERIFIED** 9/9 closures, `pending=0`, `bindingChecks=4` on every one |
| **1,725 protected build hashes** | **BLOCKED** — 0 present |
| **Runner binary** | **BLOCKED** — absent |
| **Suite binary (458 tests, E18 R1–R6 text)** | **BLOCKED** — absent |

| The complete-feed reference, re-established independently | Receipt |
|---|---|
| Why | In E23 the suite was the **only** loaded run that reached the parser. With the suite blocked, the parser-reach receipt moves to the surviving E23 cadence fixture, driven through the actual title wrappers with the reused observer loaded. |
| Result | E24 reproduces E23's reference **exactly**, on a different day and a different lane: 60 B → STALLED, 120 B → STALLED, 180 B → SERVED, 240 B → SERVED; `producerFirings=1`, `addBs=1` in all four; `matched=0` on both served branches. |
| Parser health | All four `pending=0 errors=0 bindingChecks=4`, backend forwarding exactly 1:1. `cadence.json`. |
| What it re-confirms | E23's H1 (the producer fires exactly once per `GetPicture` on every path) is not an artifact of E23's binaries or its day. |

| **Objective 3 — the I-lane V3 dims (I23 H2). CLOSED.** | Receipt |
|---|---|
| Method | Static parse of the **already-retained** 5,040 B. Trace-mining only; nothing extra burned, no boot, no probe. |
| Identity proven first | 5,040 B, SHA256 `cde8a830…2a1c875a`, FNV64 `0xd2a9588f0e0fd358`, first4 `000001b3` — E22's, E23's and the e23a run-dir copy all byte-identical. |
| **Dims** | **512 × 448** (`horizontal_size_value=512`, `vertical_size_value=448`; both `_extension` fields 0). `display_horizontal_size=512`, `display_vertical_size=448`. |
| Stream | **MPEG-2**, `profile_and_level_indication=72` (0x48 = Main Profile @ Main Level), `chroma_format` **4:2:0**, `progressive_sequence=1`, square samples (1:1), frame rate code 4 = **30000/1001 (29.97)**, bit rate **3,836,400 bps**, `vbv_buffer_size_value=112`, no quantiser matrices loaded. |
| Colour | `colour_description=1`, primaries 5, transfer 5, matrix 4 (from `sequence_display_extension`). |
| Derivable? | **Yes, unambiguously**, from `sequence_header_code` at offset 0 plus `sequence_extension` (0x000001b5, id 1) at offset 12. Nothing was missing; the question only needed the bytes the E-lane already held. |
| Vector | The standalone replayable 5,040 B carried into `local/research/E24/observed/parser-input.bin` with its own pin — H2's other half, so one path serves both requests. |

| **New: what the 5,040 B actually IS** | Receipt |
|---|---|
| Start-code census | 35 start codes: 1 sequence header, 3 extensions, 1 user data, 1 GOP header, **1 picture start code**, **28 slice start codes**. |
| Slices | Vertical positions **1..28 contiguous** — exactly `448 / 16 = 28` macroblock rows. Not a truncated prefix of a slice list. |
| Slice lengths | Slices 1..27 are 176 B (two are 177 B). **Slice 28 is 176 B — the modal length.** The final slice is not short. |
| The tail | Last non-zero byte at offset **5,024**, then **15 zero bytes** of stuffing to 5,039. |
| The deficit | **No `00 00 01` prefix appears anywhere after the final slice header.** The parser holds the picture pending a next start code and never gets one. |
| Consequence | E22 recorded the deficit as *"not computable from this run"* and barred importing Q1's `GOP + 5,461`. E24 computes it from the retained bytes without importing anything: **the feed is one structurally complete picture missing its terminating start code — not thousands of bytes of missing picture data.** |
| Named limit | Slice **header** structure and length are measured. Macroblock-level completeness of slice 28 is **not** provable from start-code structure alone, and is not claimed. |

| **Objective 1b — thread 4's ~300 wakes per 5 s. CLOSED.** | Receipt (mined from retained e23a artifacts) |
|---|---|
| Identity | Thread 4, entry `0x31ac08`, priority 99, parked `waitReason=2` on semaphore **31** at `pc=0x423de8`, `ra=0x31ac30`. |
| The attribution | `scheduled = 4,467` at the park and semaphore 31's wait tally is **4,467**. They are equal. Thread 4's wakes **are** its own `WaitSema(31)` round trips. |
| The driver | Semaphore 31 was signalled **4,466** times, **every one by `iSignalSema`** — interrupt context. Thread 4 is an interrupt-driven worker loop. |
| What they touch | **Nothing in any watched producer/source window** — 0 hits after the park across all 8 of e23a's windows, which is why E23 could not attribute them. |
| Named limit | The attribution is to the **semaphore round trip**. What thread 4 touches between wake and re-wait lies outside every watched window and outside the E7 tap; that still needs the extended watch set. |

| **Objective 2 — the semaphore wait** | Receipt (mined from retained e23a artifacts + closed static analysis) |
|---|---|
| **Errata E24-E1** | E23's REPORT and NEXT-BRIEF both give the blocked set as `26/30/32/36` — four ids for five threads. The recorded set is **26/30/31/32/36**; thread 4 waits on **31**, which both documents omit. Corrected here. |
| The ledger | thread 2 → sema 26: 737 waits / 736 signals. thread 3 → sema 30: 5 / 4. thread 4 → sema 31: 4,467 / 4,466. thread 5 → sema 32: 616 / 615. thread 6 → sema 36: **1 / 0**. |
| **Every deficit is exactly 1** | Threads 2–5 sit on semaphores that have been signalled 4 to 4,466 times. They are workers parked on their *next* item, not deadlocked. |
| **The exception** | Semaphore 36 has **never been signalled once**. Thread 6 (entry `0x3c19a8`, priority 6) was scheduled exactly **once** in the whole run, waited, and never woke. |
| Signaller enumeration, **closed** | Semaphore 36's id is stored once (`0x3c1e08  sw $v0, 0x1AA4($s0)`, the `CreateSema ret=36` return) and never copied. Across **all 9,457 generated sources** the slot appears in exactly **4** instructions: the store; `0x3c19ec lw $a0` → **WaitSema** (owner `sub_003C1980`); `0x3c15c0 lw $a0` → **iSignalSema** (owner `sub_003C1298`); `0x3c2378 lw $a0` → **DeleteSema** (owner `sub_003C2268`). |
| Cross-check | The waiter site `0x3c19ec` returns to `0x3c19f0` — **exactly** thread 6's recorded park `ra`. |
| **The finding** | There is exactly **ONE** signaller of semaphore 36 in the entire image, and its function has **ZERO entries** in the 127 MB `ps2_log-e23a-1.txt` function log. Its neighbour on the delete path also has zero. **The only code that can ever wake thread 6 never executed.** |
| Signaller `ra` per signal | **BLOCKED.** The always-on park tally records the syscall **stub** pc (`0x423dc8` SignalSema / `0x423dd8` iSignalSema), which cannot name a caller. `PS2X_DIAG_SEMA=1` emits the waker `ra` and is already compiled into the proven runner — it needs the boot. |
| Is the MPEG stall a symptom? | **Not answered, and not guessed.** The evidence shows **two independent blocked chains**: thread 1 on the host MPEG wait, and thread 6 on a semaphore whose sole signaller never runs. Nothing in the retained evidence links them in either direction. |

| The boot that was designed and NOT spent | Receipt |
|---|---|
| Watch set | **230 entries** against e23a's 37, tiered: the descriptor node array `0x548800`-`0x5489ff` at 8-byte stride (64) — which **completely covers E23's named residual**, the successor node at `0x548880`; the data-region head (32) and tail (16) at 8; the body `0xd48848`-`0xd49a73` sampled at 128 (37); the **past-end extension** `0xd49af4`-`0xd49b73` (16), chosen because E24 measured the feed ends with no terminating start code so a continuation writes exactly there; the staging buffer (32); plus 33 carried. `watch-set.json`. |
| Why tiered, not full | `diagWatchEmit` (`ps2_runtime.cpp:1309`) is called from **every** guest store and scans the whole vector, so watch count multiplies per-store cost. Full 8-byte cover of the body would be 630 entries. |
| Cost model | Fitted on the only calibration available (e22a 29 watches → 7.61 s span-complete; e23a 37 → 8.30 s): `k = 0.0863 s/entry`, `base = 5.11 s`. Predicts **~24.9 s** span-complete at 230 entries → **~50 s** post-park window under the unchanged 75 s SIGTERM (e23a got 66 s); 630 entries would predict ~64 s and leave ~11 s. A two-point fit is indicative, not measured — it is used only to **size** the list, and the driver now records span-complete on every path so the next lane can refit. |
| Residual this design leaves | An isolated write **shorter than 121 B** landing inside the sampled body span and touching none of the sampled windows. A bulk refill cannot hide there (stride 128 − window 8 = 120 B maximum gap); a single stray word can. Strictly smaller than E23's residual — an entire unwatched 128-byte node — and declared as a trade, not an oversight. |
| Second instrument, no rebuild | `PS2X_DIAG_SEMA=1` + `PS2X_DIAG_SEMA_S0=1` (`EeScheduler.cpp:156,168`) — one line per signal and wait with id, count transition, waiters, waker thread, waker **pc and `ra`**, inInt, iSafe, invocation kind/depth/cbFunc, target waiter, result. Cached static env checks; nothing printed when unset, so the proven binary is untouched. ~20k lines expected, ~4 MB against a 256 MiB cap. |
| Caps | **Identical** to e22a/e23a — wall 90 s, SIGTERM at 75 s, same byte caps — so exactly one variable changes against `e23a`. |
| Pre-registered branches | Four, all decisive, in `BOOT-DESIGN.md`. |

| Gates proven, not asserted | Receipt |
|---|---|
| Boot authorization | `e24_prepare_probe.py` checks the red flag **first** and refused: `authorized=false`, `boot_spent=false`, `lease_claimed=false`. `probe-authorization.json`. |
| Capture driver | Run for real. It refused inside preflight, **before** the atomic claim. `/tmp/ssx3-p-lane-lease` never created; `boot-attempt.json` never written; `probe-preclaim-stop.json` records the stop. |
| New presence gate | e23a's driver went straight to `.stat()` and would have raised `FileNotFoundError` deep inside a loop — an absent tree is exactly what stopped E24, so the driver now checks **presence first** and names every missing path. Proved against the real paths: runner and suite ABSENT, ELF / ISO / game data / observer PRESENT. `capture-gate-proof.json`. |
| Lease discipline | 0 claims, 0 releases, lease absent at open and at close, `pgrep -x ps2EntryRunner` rc 1 throughout. |

| Storage / execution budget | Admission and accounting |
|---|---|
| Internal reservation | 512 MiB (E23 amendment A1 carried; floor 2 GiB + 0.5 GiB guard). Never approached — E24 ran no build step. |
| SSD reservation | 16 GiB in NEW `e24-*` paths; same floor/guard. |
| Initial admission | `2026-09-22T11:32:39Z`: internal 10,943,016,960 B free / SSD 154,894,598,144 B free. Both reservations fit. |
| Final audit sample | Internal owned **3,604,480 B**, free 10,926,620,672 B; SSD owned **350,224,384 B** across 4 `e24-*` paths, free 154,540,179,456 B; fork growth **0**. |
| Accounting | `st_blocks × 512`, incl. ExFAT directory/AppleDouble allocation; `COPYFILE_DISABLE=1` on every SSD step. No reclaim, no deletion — **in particular nothing was deleted in response to the loss**. |
| Boot cap utilisation | None — no boot. |

| Tooling provenance | Receipt |
|---|---|
| Pure rename (12 files) | `io / closed_events / parser_receipt / bounded / validate / observer_regression / baseline / mine / cadence / capture / prepare_probe / boot_mine`. Hex-safe normalized diff **byte-empty for all twelve**; every hex run byte-equal. `rename-proof-hexsafe.json`. |
| Errata E23-E1 honoured | The rename masks every run of ≥16 hex characters **before** renaming, so a digest cannot be rewritten, and the proof additionally asserts hex-run equality — the check E23's proof lacked by construction. `ELF_SHA` is byte-identical to E23's. |
| Protected tokens extended | The five E21 instrument tokens, plus two new: `e23-fixtures/complete` and `# E23 COMPLETE FEED FIXTURE TAIL COMPLETE`. The cadence fixture **binary** survived at its E23 path and owns its footer string; renaming either would point at a non-existent file or assert on a footer the binary never prints. |
| Intentional changes | 6 to the lane tools, 4 to the boot driver, each applied idempotently and recorded as data (`tooling-changes.json`, `capture-changes.json`), with full diffs in `tooling-diff.md`. |
| New files | `e24_rename.py`, `e24_patch.py`, `e24_patch_capture.py`, `e24_env_audit.py`, `e24_checkpoint.py`, `e24_dims.py`, `e24_sema_mine.py`, `e24_signaller_closure.py`, `e24_close.py`. |
| `stdbuf` in E24 | Present only as the forbidding assertion and the receipt field. No boot argv was ever built. |

| Fix gate | Receipt |
|---|---|
| Demonstrated edges | (1) The 5,040 B is one structurally complete picture — 28 contiguous slices, final slice at modal length, 15 bytes of zero stuffing, **no terminating start code**. (2) Semaphore 36's **unique** signaller never executes. (3) Thread 4's wakes are sema-31 round trips, not source traffic. (4) The blocked set is 26/30/**31**/32/36. |
| Isolated to ONE edge? | **No** — and it could not have been acted on if it were: with the suite and runner gone there is no fail-before and no regression to run. |
| Gate decision | **STOP.** |
| X, sharpened | X stays upstream of the MPEG demand edge and gets sharper: the deficit at the parser is a **terminating start code**, not missing picture data. **Why does the guest stop one start code short?** — and, separately, why does semaphore 36's only signaller never run? |
| Mutations | Zero fork source edits, zero fork commits, zero pushes. Diagnosis-only. `fix-gate.json`. |

| Exact command record | Invocation / artifact |
|---|---|
| Environment | `export COPYFILE_DISABLE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=…/E24`; bounded wrapper sets task-specific TMPDIR on the SSD. |
| Rename + instrument copy | `python3 local/research/E24/e24_rename.py …` (12 files) → `rename-proof-hexsafe.json`; `python3 e24_patch.py`, `python3 e24_patch_capture.py`; `cp -p` of the E21 dylib, re-sha'd → `instrument-reuse.json`. |
| Environment audit | `python3 local/research/E24/e24_env_audit.py` → `env-audit.json`. |
| Checkpoint | `python3 local/research/E24/e24_checkpoint.py`; then `… e24_bounded.py checkpoint-regression 1200 -- … e24_baseline.py`; rc 0. |
| Loaded regression | `… e24_bounded.py observer-regression 1200 -- … e24_observer_regression.py`; rc 0, 9/9 loaded closures. |
| Cadence reference | `… e24_bounded.py cadence 900 -- … e24_cadence.py`; rc 0, four cases plus nine carried controls. |
| Objective 3 | `python3 local/research/E24/e24_dims.py` → `dims.json`, `observed-vector.json`, `picture-completeness.json`, `payload-tail.json`. |
| Objectives 1b / 2 | `python3 local/research/E24/e24_sema_mine.py`; `python3 local/research/E24/e24_signaller_closure.py`. |
| Boot gates (both REFUSED) | `python3 local/research/E24/e24_prepare_probe.py` → `probe-authorization.json`; `python3 local/research/E24/e24_capture.py a --report-all` → `probe-preclaim-stop.json`, no lease, no `boot-attempt.json`. |
| Final close | `python3 local/research/E24/e24_close.py`; 9,457 hashes rechecked; fork HEAD/ref/remote agree unchanged; lease absent; 0 boots / 0 claims / 0 fork commits. |
| Never executed | Any fork edit, commit or push; any regeneration; any build, relink or observer rebuild; any title boot; any lease claim; `stdbuf` in any argv; **any deletion or reclaim, including of the lost trees' remains**. |

| Evidence hygiene / handoff | Receipt |
|---|---|
| Standalone data | Contract, environment audit, checkpoint with every gate's status, unloaded and loaded regression logs and receipts, the re-established cadence reference with tap and parser receipts, rename/hex/tooling proofs, the boot design and watch set with its cost model, both refused boot gates, the dims + picture-completeness + payload-tail receipts, the retained vector, the semaphore mine, the closed signaller enumeration, fix gate, final audit. |
| Retained copies | `observed/parser-input.bin` (the title's real 5,040 B, `cde8a830…2a1c875a`), `sources/*.gz`, `cadence-*-events.txt`, `observer-receipts/`. |
| `.suite-*` scratch | None created — the suite never ran. |
| Tail qualification | Every bounded tool, fixture, receipt and mine ends with its real `TAIL COMPLETE` footer; counts re-verified, never appended. |
| Errata carried | E21-E1, E23-E1, E23-E2 carried forward unchanged. **E24 adds E24-E1** (E23's REPORT and NEXT-BRIEF omit semaphore 31 from the blocked set). |
| Publication | `[E24]` evidence commit with `Orchestrated-By: Muse Code`, `git add -f`. Scope: E24 evidence only; no fork files, no generated sources. **Not pushed** — the orchestrator pushes at poll. |

| Tail receipt | Value |
|---|---|
| Complete prefix | Lines 1–164; 23899 B; SHA256 `b52965563e95391e2c9b84800c4bdf6cf9c71b5b9b5591b2600f78d1f2e46d94` |
| Source-tail gap | **None, and one honest hole.** Every E24 capture carries its real footer. The hole is objective **1a**: it requires the new watch set on a live title boot, the boot was barred by a red checkpoint, and it is reported as **not reached** rather than inferred from E23's smaller watch set. |
| E24 REPORT TAIL COMPLETE | The host restart wiped all three protected build trees (1,725/1,725 files, 1.58 GB), so the checkpoint went red and no boot was spent — the brief's own rule. Everything the block does not touch was executed in full: the title movie dims are **512 × 448** MPEG-2 MP@ML 4:2:0 29.97 fps, and the 5,040 B proves to be **one structurally complete picture — 28 contiguous slices, final slice at modal length — missing only its terminating start code**; thread 4's wakes are sema-31 round trips, not source traffic; the blocked set is 26/30/**31**/32/36, every deficit exactly 1, and semaphore 36's **sole** signaller in the entire 9,457-file image **never executes**. The extended-watch boot is designed, driven, gated and pre-registered, waiting only on a restored build. 0 boots, 0 lease claims, 0 fork edits/commits/pushes, 0 deletions, 1 errata added. |
