| E23 | Receipt |
|---|---|
| Stop point | All gates executed: checkpoint re-verified unloaded + observer-LOADED, the complete-feed demand cadence mined on the ACTUAL title wrappers across four sweep points, trigger point and loop bound named by comparison, ONE guarded title boot spent on the observation that decides the transfer. Fix gate: **STOP**, X named and moved upstream. |
| Checkpoint | Fork `3adc0478b6d2260acdd28a249466f2eef9a20176` triple-agreed at open and close; 9,457 generated names/hashes; 1,725 protected builds; 458/458 UNLOADED; 458/458 observer-LOADED with the REUSED dylib; E15 rc0s; E16 closure 6; prior 24/3/14/4/DROP; E18 R1–R6 present in suite text. |
| Questions reached | The R3-shape cadence reference landed on both branches (SERVED and STALLED); the trigger/bound transfer tabled; the one title observation designed, executed and read. |
| Mutations / launches | Zero fork source edits, zero fork commits, zero pushes. One fixture link against the current unmodified runner object set. One guarded title boot (wall-bound, rc 0), one lease claim / one clean release. No target fix, no regeneration, no observer rebuild. |
| Next dependency | The missing bytes are **not obtainable at the demand edge**. X moves upstream of MPEG: why does the guest hand over exactly 5,040 B and then leave all six threads waiting with DMA/GIF frozen? |

| Experiment contract | Bound / observable |
|---|---|
| Time box | Start `2026-09-22T00:02:45Z`; deadline `2026-09-22T08:02:45Z`; eight hours. Final audit `2026-09-22T00:23:30Z`. **Actual time used: 20 min 45 s** (open → final audit), well inside the box. |
| Required reads | E22 REPORT 134 lines + NEXT-BRIEF 22 lines, E21 REPORT 148 lines, E18 NEXT-BRIEF 41 lines, E23 prompt 60 lines — all read in full including tails, before any copy, link or boot. |
| Hypothesis | **H0**: the complete-feed path runs a multi-round demand cadence whose round count and stop condition supply the missing rule. **H1**: it fires the producer exactly once, the same as the stall, and terminates only because the single round sufficed. |
| Result | **H0 falsified, H1 held.** Producer firings = 1 at 60, 120, 180 and 240 B — on the two branches that stall and the two that serve a decoded picture. |
| Alternatives | (a) the complete path loops and its bound transfers; (b) it fires once and the branches differ only by byte sufficiency; (c) it loops for a reason that does not transfer; (d) observation fails. **(b) realised**; (a) and (c) excluded by the sweep; (d) excluded by four receipt-verified parser closures plus a closed boot receipt. |
| Observable | Per `GetPicture`: producer firings, AddBs entries, completion edges and their matched-waiter counts, thread and tick of each in sequence order, the terminating event, and per-call parser timing with 1:1 backend forwarding. |
| Strict order | Contract → admission → checkpoint → loaded regression → reference fixture → join/compare → boot design → ONE boot → fix gate → close. Opened in order; no red gate tripped; no boot on red. |
| Fix gate | Exactly one demonstrated edge + minimal ABI-preserving change + own fail-before + full regression. Closed: **STOP**. `fix-gate.json`. |
| Preserved constraints | Caller-owned synchronous dispatch; word0-only cbData; v0 discarded; valid-no-input waits; dispatch outside the MPEG mutex; delete/reset cancellation. No CSV, main, scheduler or stream-callback edits. |
| Contract source | `CONTRACT.md`, written before the first copy, link or boot. One declared amendment, `AMENDMENT-A1.md`. |

| **Contract amendment A1** | Receipt |
|---|---|
| What tripped | The cadence sweep's fresh admission refused: `internal_free 3,200,606,208 < 2 GiB + 512 MiB + (3 GiB − 4,075,520)`. Correct under the contract as written — the *reservation* half of the rule, not the floor half. |
| Cause (measured) | Internal free went 6,133,268,480 B → 3,200,606,208 B across the 405 s thin-LTO relink: **−2.93 GB, not returned**. Not swap (`vm.swapusage used = 11.75M`), not a local snapshot (`tmutil listlocalsnapshots /` empty), and not a findable file (no internal file >50 MB with an mtime in the link window; the `linker-crash-*` dirs all predate it). macOS's own `com.apple.cache_delete` ran during the window. |
| Change | Internal reservation 3 GiB → 512 MiB. **Floor and guard unchanged** at 2 GiB + 0.5 GiB; SSD reservation unchanged at 16 GiB. E23's actual internal footprint at the refusal was 4,075,520 B — 131× under the amended reservation — because every remaining step writes to the SSD. |
| Discipline | Declared in `AMENDMENT-A1.md` with `amendment-a1.diff` and `amendment-a1.json` before use; the gate was never bypassed, no file deleted, no cache reclaimed, no protected path touched, and no second build step run under it. |

| Storage / execution budget | Admission and accounting |
|---|---|
| Internal reservation | 3 GiB at open, 512 MiB after A1 (evidence 0.25, scratch 0.25); floor 2 GiB + 0.5 GiB guard throughout. |
| SSD reservation | 16 GiB in NEW `e23-*` paths (tooltmp 8, fixtures 2, probe 1.5, reserve 4.5); same floor/guard. |
| Initial admission | `2026-09-22T00:02:45Z`: internal 6,340,960,256 B / SSD 169,172,008,960 B free. Both reservations fit. Internal was the scarce side all run. |
| Fresh admissions | Every bounded tool saved its start sample and re-checked the reservation plus floor; the one that did not fit **refused and is reported above**, it did not proceed. |
| Final audit sample | Internal owned 4,567,040 B, free 3,262,234,624 B; SSD owned 749,731,840 B across 22 `e23-*` paths, free 159,352,094,720 B; fork growth **0**. `final-audit.json`. |
| Accounting | `st_blocks × 512`, incl. ExFAT directory/AppleDouble allocation, E23-owned paths and positive fork source/Git growth; `COPYFILE_DISABLE=1` on every SSD step. No reclaim, no deletion. |
| Protected | `/tmp/p1-link`, `/tmp/e17-map-link`, `/tmp/e18-mpeg-link` and DerivedData reserved; all 1,725 protected hashes re-verified equal at close. No protected build command run. |
| Boot cap utilisation | Bound hit: **wall only**. rc 0, 75.75 s, 54,914 trace lines of 1,000,000; span-complete at 8.30 s. |
| Lease | Atomic `/tmp/ssx3-p-lane-lease`, never waited; 1 claim (`00:19:09Z`) / 1 clean release (`00:20:25Z`); post-release `pgrep -x ps2EntryRunner` rc 1, lease absent. |

| Checkpoint re-verification | Receipt |
|---|---|
| Fork identity | HEAD, `refs/remotes/fork/ssx3` and `git ls-remote fork refs/heads/ssx3` agree at `3adc0478…` at open and close. Preexisting AppleDouble Git-index warning retained (stderr only; `status --short` is exactly `?? ps2_log.txt`). |
| Generated names / bytes | 9,457 `.cpp`/`.h` files; every SHA256 matches E18's manifest at open and close. |
| Protected build hashes | 1,725 objects/archives/PCH/runners/suites across the three retained builds; all re-hashed equal at close. |
| Runner / suite | 163,529,696 B `e462e448…67e22`; 5,695,128 B `2152e5ad…f04c0`. |
| Full suite (unloaded) | rc 0, 458 passed / 0 failed; R1–R6 present. `checkpoint-suite.txt/json`. |
| Full suite (observer-LOADED) | rc 0, 458 passed / 0 failed with the reused dylib; 10/10 observer dirs receipt-verified. `observer-regression.json`. |
| Prior / E15 / E16 / absorbed | leaf 24 / consumer 3 / predicate 14 / query 4 / DROP; E15 no-input + input rc 0 with `saved128=1 waitReason=6 callbackCalls=1 resumes=0`; six closure modes rc 0; five presence checks and three ownership controls rc 0. |

| Instrument reuse (no rebuild) | Receipt |
|---|---|
| Reused dylib | E21's `e21-parser-observer.dylib` copied to `local/research/E23/parser/`; re-sha **hits** `e4d88fdc6740449893d5a96c112fae6ce3f19135bad8a309d140d45bbf38e6be` (52,472 B). Not rebuilt, not renamed. |
| Interface carried verbatim | `PS2X_E21_PARSER_DIR`, `PS2X_E21_PROOF` and `# E21 PARSER CLOSURE` stay E21-spelled by necessity; held out of the rename as protected tokens. |
| Inherited proof | E21's isolation forwarding (byte-identical feed, `_Exit` rc 3 both ways, 4/4 valid bindings) consumed by binary identity and re-asserted in `e23_observer_regression.py` and `e23_prepare_probe.py`. |
| Fixture source chain | `e21/e18/e17/e16/e15/prior_binding_test.cpp` + `e21_parser_observer.h` carried **byte-identical** (`carried-fixture-sources.json`, all `verbatim: true`). |

| Tooling provenance | Receipt |
|---|---|
| Pure rename (8 files) | `e23_io/bounded/checkpoint/baseline/validate/parser_receipt/closed_events/observer_regression`. Hex-safe normalized diff is **byte-empty for all eight** (`rename-proof-hexsafe.json`). |
| Intentionally changed (3 files) | `e23_common.py` (amendment A1), `e23_prepare_probe.py` (boot gated on the E23 cadence reference), `e23_capture.py` (producer/source watch set). Full diffs in `tooling-diff.md` and `amendment-a1.diff`. |
| New files | `e23_complete_test.cpp`, `e23_payload.inc`, `e23_link_test.py`, `e23_cadence.py`, `e23_mine.py`, `e23_boot_mine.py`, `e23_close.py`. |
| `stdbuf` in E23 | Present only as the forbidding assertion and the receipt field; the boot argv execs the runner directly (`argv0_is_runner=true`, `stdbuf_free=true`). |
| **Errata E23-E1 (found and repaired in-lane)** | The mechanical `e22`→`e23` rename rewrote the substring `e22` **inside a hex digest**: `ELF_SHA` became `…ce9ae2391d61a…` instead of `…ce9ae2291d61a…`. The normalized-diff proof was blind to it by construction (it maps both `e22` and `e23` to `EXX`). **Caught by `e23_capture.py`'s own preflight file-hash gate, before the atomic lease claim — no boot was spent** (`probe-preclaim-stop-attempt1.json`; `boot-attempt.json` absent at that point). Repaired, then every renamed file audited: `hex-audit.json` shows exactly one corruption across eleven files, zero remaining. The rename proof was replaced with a hex-safe one. |

| The complete-feed reference (E23's target measurement) | Receipt |
|---|---|
| Path | The R3 authored payload (240 B, four 16×16 I-frames) driven through the **actual title wrappers** — `0x4027b8` Create, `0x402c08` AddCallback, `0x402a10` GetPicture, `0x4029d0` AddBs — in a fixture linked from the current unmodified runner object set, observer-loaded, with the E7/E15 tap. Payload extracted verbatim; FNV64 `0x54b07fc845a0494d` **equals** the suite's own `parse-enter call=1` hash. |
| New-binary control | The new fixture reproduces **every** carried receipt: prior 24/3/14/4/DROP, E15 no-input/input, all six closure modes, all rc 0. The only behavioural difference is the added mode. |
| **Producer firings** | **1 at every sweep point.** 60 B → STALLED, 120 B → STALLED, 180 B → SERVED, 240 B → SERVED; `AddBsCalls=1`, `selections=1`, `invocations=1` in all four. |
| Served runs | `resumes=1 resumeV0=0 width=16 height=16 pixel=0x800000fe`, `saved128=1`, `manualCallbackCalls=0`, `parks=0`. |
| Stalled runs | `parked=1 waitReason=6 resumes=0` — the title's shape at fixture scale. |
| Parser receipts | All four `pending=0 errors=0`, backend forwarding exactly 1:1, `bindingChecks=4` all valid. 240 B → 4 parse calls / 3 packets / 2 frames, reproducing the suite's `[MPEG:feed] inSize=240 parsed=240 packets=3 newFrames=2 totalFrames=2` and **E18's committed R3 line** independently. |
| Divergence point | The 60 B and 240 B tap sequences are **identical event for event through seq 12** (same thread, same tick). They differ only afterwards: the stall reaches `mpeg-wait`, the serve reaches `mpeg-complete` and then returns without parking. Full tables in `CADENCE.md`. |

| What ends the loop — three bounds, none a demand rule | Receipt |
|---|---|
| Callback dispatch | `nextCallback < delivery->callbacks.size()` (`MPEG.cpp:1714`) — registration-list exhaustion, **constant 1** on the fixture, the suite and the title. |
| Host parser feed | `while (remaining > 0)`, early-out on `used == 0 && packetSize == 0` (`MPEG.cpp:102-145`) — offered-buffer exhaustion **inside one AddBs**. The 240 B feed's four parse calls are this loop draining one offering, not four demands. |
| Picture wait | `decodedFrames.empty()` at `:2469` / `:2496` — serve if a frame exists, else `waitExternal`. |
| Round counter | **None exists anywhere.** |

| The C1 control E22's elimination lacked | Receipt |
|---|---|
| New evidence | On the SERVED branch `sceMpegAddBs` **does** change the frame count, so `completeExternalWait` **is** raised (`seq=13`) — and matched **zero** waiters (`mpeg-complete matched=0`), because the caller is still inside its own callback (`seq 9–15`). |
| Consequence | E22 eliminated C1 where the wake is never raised. E23 shows it **raised and still inert on the path that works**. The `onComplete` retry at `MPEG.cpp:2484` is the only mechanism that has ever delivered a picture in this runtime. |

| Transfer to the title | Receipt |
|---|---|
| Trigger point | **Transfers.** The sole post-dispatch re-entry is `onComplete` → `getMpegPicture(..., false)` at `:2484` — C2a's site — and it already runs on the title. No invention needed. |
| C2a vs C4 | **C2a has precedent, C4 has none.** C4's site (`:2496–2513`) is reached only on branches that stall; no run that served a picture ever visited it. E22 could not separate them. |
| Loop bound | **Does not transfer.** The complete path stops because `decodedFrames.empty()` becomes false, closing the gate against a second delivery. On the title that gate never closes, leaving a C2a-shaped re-ask unbounded. |
| Only non-invented extra bound | "The producer supplied no new bytes" — decidable only by measuring whether the guest refills its source. That is what the one boot measured. |
| Assumptions tabled, not adopted | A1 multi-round firmware demand (unobserved on all four decoding paths); A2 a no-progress stop (no such counter exists); A3 the 5,040 B is partial; A4 importing Q1's `GOP + 5,461` (barred by E22's scope limit). `CADENCE.md` §6. |

| The one boot (e23a) — the transfer is killed | Receipt |
|---|---|
| Pre-claims + lease | Fresh T13 battery green; suite preclaim 458/458; atomic claim `E23A`; clean release; post-release `pgrep` rc 1. Boot gated on E23's own cadence reference (four cases, both branches, receipts clean) before it could be spent. |
| Boot argv | `['/tmp/e18-mpeg-link/runtime/ps2xRuntime/ps2EntryRunner', '/Volumes/Extreme SSD/ps2recomp-spike/P1/cd/SLUS_207.72']` — runner exec'd DIRECTLY, `stdbuf_free=true`, observer dylib inserted. |
| Bound / rc / window | `bound=wall`, rc 0, 75.75 s, 54,914 trace lines, span-complete at 8.30 s. |
| Reproduces E22 | 6,401 E7 events; park at `seq=6401 tick=249`; parser called **once** (5,040 offered / 5,040 consumed / `packets=0` / `frames=0` / `errors=0`); backend 1:1; `bindingChecks=4`; real `# E21 PARSER CLOSURE … reason=_Exit rc=0`. |
| Watch instrument health | 6,676 `[diag:watch]` lines — the **most frequent tag in the pre-park log** (6,639 of 10,171 lines; 1,291 in the final 2,000 before the park). Emitter is uncapped and ungated (`ps2_runtime.cpp:1309`). |
| **Producer/source writes** | **29, every one before the park**, last at boot-log line 10,168 against a park marker at line 10,171. Values match E18 exactly: `0x548804 = 0xd48748`, `0x548808 = 0x13ac` (5,036), `0x587b78 = 0xdc8340`, `0x587b7c = 0x30dc8340`. The staging buffer was written once, at line 9,447, by **thread 3** (`pc=0x3e65d0`, the CD/stream reader), and never again. |
| **Writes after the park** | **0**, across 12,113 further boot-log lines (~66 s). |
| Guest liveness control | The guest is **not** frozen: thread 4 is scheduled ~300× per 5 s interval in the last sample and the dormant path's counter runs 333 → 638. All six threads `status=2`: thread 1 `waitReason=6` at `pc=0x3b1028`, threads 2–6 `waitReason=2` at `pc=0x423de8`. DMA/GIF frozen at `dma=4542 gif=210` across all six post-park `[run:tick]` samples. |
| Decision (pre-registered) | **Transfer KILLED.** A second producer dispatch would re-read a source nothing has touched for 66 s while a guest thread was running, and would deliver no new bytes. C2a and C4 cannot produce a frame however they are bounded. |
| **Residual, named** | The watch covers 22 eight-byte windows, not the address space. At line 10,168 the descriptor head advanced `0x548800 = 0x548880`, and that successor node was **not** watched — its silence is vacuous, not measured. Thread 4's ~300 wakes per 5 s are likewise unattributed. The verdict is **strong but not exhaustive**: the pre-registered branch on the evidence obtained, not a proof that no byte exists anywhere in guest RAM. |

| Fix gate | Receipt |
|---|---|
| Demonstrated edges | (1) One producer firing per `GetPicture` on every path, serving and stalling alike. (2) The trigger point transfers; the bound does not. (3) C4's site is never visited on a path that serves. (4) The wake edge is inert even when raised. (5) The guest does not refill its source while the caller is parked. |
| Isolated to ONE edge? | **No.** The trigger point is isolated, but the bound is not derivable and the measurement shows a re-ask would fetch nothing. |
| Gate decision | **STOP.** Implementing C2a or C4 would add a demand policy that provably cannot produce a picture — invention with a known-null result. Per brief: "Guest never sends more without X" → NAME X and STOP. |
| X moved upstream | The missing bytes are not obtainable at the demand edge. X is now: why does the guest hand over exactly 5,040 B and then leave all six threads waiting (thread 1 on Mpeg, threads 2–6 on semaphores) with DMA and GIF frozen? |
| Mutations | Zero fork source edits, zero fork commits, zero pushes. Diagnosis-only. `fix-gate.json`. |

| Exact command record | Invocation / artifact |
|---|---|
| Environment | `export COPYFILE_DISABLE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=…/E23`; bounded wrapper sets task-specific TMPDIR on the SSD and `CMAKE_BUILD_PARALLEL_LEVEL=2`. |
| Rename + instrument copy | Protected-token rename → `rename-proof.json`, `rename-proof-probe.json`, `rename-proof-hexsafe.json`, `hex-audit.json`; `cp -p` of the E21 dylib and fixture sources, re-sha'd. |
| Checkpoint | `python3 local/research/E23/e23_checkpoint.py`; then `… e23_bounded.py checkpoint-regression 1200 -- … e23_baseline.py`; rc 0. |
| Loaded regression | `… e23_bounded.py observer-regression 1200 -- … e23_observer_regression.py`; rc 0, 458/458 loaded, 10/10 receipts. |
| Fixture link | `… e23_bounded.py complete-link 1800 -- … e23_link_test.py complete`; rc 0, 405 s, 165,202,160 B, SHA256 `3136f3ca…fd4279a2`. |
| Cadence sweep | `… e23_bounded.py cadence 900 -- … e23_cadence.py`; rc 0, four cases plus nine carried controls. |
| Probe gates | `python3 local/research/E23/e23_prepare_probe.py` → `entry-preflight.json`, `e23a-build.json`. |
| The boot | `python3 local/research/E23/e23_capture.py a --report-all` (sole boot; the earlier attempt stopped in preflight on errata E23-E1, before the lease claim). |
| Mining / joins | `python3 local/research/E23/e23_boot_mine.py`; watch liveness and post-park thread joins. |
| Final close | `python3 local/research/E23/e23_close.py`; 9,457 + 1,725 hashes rechecked; fork HEAD/ref/remote agree unchanged; lease absent; 1 boot / 1 claim / 0 fork commits. |
| Never executed | Any fork edit, commit or push; any game regeneration; a second title boot; an observer rebuild; E19's or E20's dylib in any run; `stdbuf` in the boot argv; any deletion or reclaim. |

| Evidence hygiene / handoff | Receipt |
|---|---|
| Standalone data | Contract + amendment, checkpoint and loaded logs and receipts, rename/hex-audit/tooling proofs, carried fixture sources, the linked fixture's link and binary records, four cadence runs with their tap and parser receipts, boot design, boot config/preflight/liveness/result, the retained title parser events and full payload, watch and post-park liveness joins, fix-gate record, final audit. |
| Retained copies | `observed/parser-events.txt`, `observed/parser-input.bin` (the title's real 5,040 B payload), `cadence-*-events.txt`, `suite-parse-episodes.json`. |
| `.suite-*` scratch | Remains unstaged (checkpoint, observer, preclaim); loaded-suite observer receipts preserved canonically under `observer-receipts/`. |
| Tail qualification | Every bounded tool, suite, fixture, receipt and boot artifact ends with its real `TAIL COMPLETE` / runtime closure footer; counts re-verified, never appended. |
| Errata carried | E21-E1 (stale harness size/sha in E21's REPORT) carried forward unchanged. **E23 introduces E23-E1**, found, repaired and audited in-lane — see Tooling provenance. |
| Publication | `[E23]` evidence commit with `Orchestrated-By: Muse Code`, `git add -f`. Scope: E23 evidence only; no fork files, no generated sources. **Not pushed** — the orchestrator pushes at poll. |

| Tail receipt | Value |
|---|---|
| Complete prefix | Lines 1–139; 20842 B; SHA256 `2c76271cb50c7becb6671f55891fdd7c5fe760d2b08ae3c943a2cf93c0c50f8f` |
| Source-tail gap | **None.** Every E23 capture (suite, fixtures, four cadence runs, boot E7, boot parser) carries its real runtime closure footer. The one instrument limit — the watch set's unwatched successor descriptor node — is tabled in `CADENCE.md` §7 as a named residual, not papered over. |
| E23 REPORT TAIL COMPLETE | Complete-feed cadence measured: the producer fires exactly once per `GetPicture` on every path, serving and stalling alike, so no multi-round reference exists to calibrate C2a/C4; the trigger point transfers and the bound does not; the wake edge is inert even when raised; and the one boot shows the guest never refills its source while parked, killing the transfer. 1 boot, 1 lease claim, 0 fork edits/commits/pushes, 1 declared amendment, 1 errata found and repaired before it could cost a boot. |
