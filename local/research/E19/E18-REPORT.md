# E18 — caller-owned MPEG input delivery

| Contract | Bound / observable |
|---|---|
| Scope | I20 S1–S10 consumed; generic non-stream delivery on GetPicture entry only. No second behavior fix, map edit, code generation, scheduler edit, or main edit |
| Start / deadline | 2026-09-21T18:38:00.452951Z / 2026-09-22T02:38:00.452951Z |
| Hypothesis | Delivering the observed type1 input request on the GetPicture caller permits AddBs and subsequent picture completion while preserving ownership, no-input waits, and stream behavior |
| Observable | Actual bindings rc1→rc0; R1–R6; all old regressions; dynamic object/callback/input/completion and graphics joins from at most one guarded title probe |
| Alternatives | Delivery remains absent; delivery occurs with no input; input arrives without decode/completion; completion reaches a named later guest dependency |
| Stop | Any regression red: no boot. Occupied lease: no wait/no boot. First demonstrated missing link after delivery: name the edge, no second fix. Required regeneration: stop |
| Source authorization | MPEG.cpp and regression tests; MPEG.h only if cross-TU needed (not needed). Fork push authorized; local evidence commit only, no main-repository push |
| Boots | 0/1 used at report opening; ownership and regression fixtures are non-title |
| Detailed contract | `CONTRACT.md`; required reads archived in `I20-SPEC.md`, `E15-CONSTRAINTS.md`, `E16-CONSTRAINTS.md`; E17 receipt baseline pinned by checkpoint |

| Allocation admission before edits | Internal | SSD |
|---|---:|---:|
| Declared owned-byte budget | 6,442,450,944 | 17,179,869,184 |
| Floor + guard | 2,684,354,560 | 2,684,354,560 |
| Initial free bytes | 13,019,901,952 | 230,192,840,704 |
| Required initial admission | 9,126,805,504 | 19,864,223,744 |
| Reclaim/deletion | 0 | 0 |
| Protected | `/tmp/p1-link`, `/tmp/e17-map-link`, DerivedData | Existing checkpoint/fixture trees |
| Tracking | st_blocks×512, owned build/evidence allocation | st_blocks×512, ExFAT metadata/AppleDouble, tooltmp/fixtures/probe/shared function log, positive source/Git growth; COPYFILE_DISABLE=1 |

| Checkpoint | Receipt |
|---|---|
| Fork HEAD / tracking / ls-remote | `e63f1616320d12c3f213899af6fba03fee3eafb2`; `opening-git.json` |
| Generated names + bytes | 9,457 names, all E17 hashes equal; `checkpoint.json`, `before-generated.json` |
| Baseline suite | 452/452, rc0; `baseline-suite.json`, full stdout |
| Prior binding fixture reuse | SSD E17 binary, SHA256 `3d6bb6bbbffa201389e14650ba346696a0d9a372e5e60743f0e2b73a9635b401`; no relink needed for checkpoint |
| Prior cases | leaf24 / consumer3 / predicate14 / query4 / DROP green, rc0 |
| E16 closure | quiescent / idempotent / window-complete / disabled / unopened / fallback-error: all six rc0, real source footers where enabled |
| E15 no-input / input | Both rc1 FAIL-BEFORE; callbacks=0; no manual callback; typed MPEG wait; saved128 and pre-request RAM retained |
| Protected build manifest | 1,150 object/library/PCH/runner/suite files from E16/E17 pinned in `protected-build-before.json` |
| Baseline process caps | No wall/allocation/stdout cap reached, no truncated fixture tail |

| Ownership audit (before implementation) | Caller thread → callback thread | Caller SP → callback SP | Other evidence |
|---|---|---|---|
| queueInvocation, caller runnable | 1 → 1 | 0x1e00000 → 0xffff0 | Args and saved128 retained; callbacks/completions/resumes=1 |
| queueInvocation, caller parked | 1 → −1 | 0x1e00000 → 0xffff0 | Synthetic owner; args alone do not preserve ownership |
| invokeCurrent / HleCall | 1 → 1 | 0x1e00000 → 0x1e00000 | Full parent-context restore, callbacks/completions/resumes=1 |
| Selection | Current-thread HleCall | Caller stack retained | `OWNERSHIP.md`, `ownership-dynamic.json`, numbered source evidence; all actual-linked to E17 objects, title boots=0 |
| Continuation | Generated GetPicture wrapper already sets pc to supplied RA | Invocation RA0 is the scheduler completion sentinel | onComplete restores the untouched parent and continues GetPicture; no guest-PC-specific branch |

| Implementation before regression | File / behavior |
|---|---|
| Selector | `MPEG.cpp`: generic `!stream && type == requestedType`; GetPicture requests the only observed type1 |
| Delivery | Collect under MPEG mutex; dispatch after unlock on current caller; guest buffer initializes only the type word; callback v0 ignored; buffer freed in onComplete |
| Ordering / dedupe | Registration order; null/unbound targets skipped; weak pending index per (mpeg,type), retained by invocation/wait continuations |
| Lifetime | Delete/reset/init/create invalidate pending tokens; an attached callback not yet entered is suppressed; negative result `KE_WAIT_DELETE`; in-flight callback data retained until onComplete |
| Return | After the collected callbacks finish, continue the same GetPicture without triggering duplicate input; existing frame/no-input/EOF behavior retained |
| Stream retention | Existing selectors/dispatch helpers byte-equal; original test file recoverable byte-for-byte after removing additions; `before-build-scope.json` |
| Tests added | R1 order/filter/ABI/owner; R2 AddBs re-entry; R3 authored MPEG-2 input decoded into guest image; R4 no-input v0 variations; R5 pending delete/reset; R6 stream exclusion plus unchanged stream regression |
| R3 environment | FFmpeg-enabled host build, four authored red16×16 I-frames (240B). Provenance and independent 4096B decode receipt in `regression-frame-provenance.json`; no claim about device stub decode |
| Source-review helper correction | Initial scope script erroneously treated the intentionally edited test as immutable; corrected its allowlist before compilation. No source/test execution failure at this step |

| Build environment receipt | Observation / action |
|---|---|
| First build | CMake glob included binary AppleDouble `._MPEG.cpp`; compiler reported invalid UTF-8. Repeated diagnostics reached the 15MiB stdout stop reserve; rc−9, 45.834s, stdout_seen=15,807,443, truncated=true. No regression executable ran; this log cannot supply a complete compiler tail |
| Ownership check | Both new `._MPEG.cpp` and `._ps2_runtime_expansion_tests.cpp` absent in pre-edit allocation manifest; birth times match E18 edits; untracked, AppleDouble magic `00051607`; `sidecar-audit.json` |
| Reversible environment correction | Two owned sidecars renamed intact to `P1/e18-sidecars`; hashes match; deleted bytes=0; preexisting test metadata untouched. `sidecars-retained.json` |
| Build continuation | Same isolated build, flags and `-j2`; CMake refreshes its build-file glob. No PS2 generated source changes or generator invocation. `after-sidecars-scope.json` confirms source hashes and retained stream/test bytes |

| Host regression | Receipt |
|---|---|
| Full suite | 458/458, rc0 (original 452 + six new cases); `current-suite.json`, `current-suite.txt` |
| R1 | Ordered type1 delivery; null/unbound/type2 filtered; caller thread/SP and saved128 retained; cbData+4 canary intact; buffer released |
| R2 | Delivered callback re-entered AddBs, copied16 bytes, returned without deadlock; no frame, typed MPEG wait retained |
| R3 | Actual 240B MPEG-2 input: parsed240, packets3, newFrames2; GetPicture FRAME16×16, caller resumed once with rc0 and nonzero guest image; no frame injection |
| R4 | Callback v0=0 / 1 / 0xffffffff, no AddBs: each callback once, no resume, typed wait retained; data released |
| R5 | Scheduler preemption placed delete/reset between invocation attachment and guest dispatch; both suppress callback, resume with −425 (`KE_WAIT_DELETE`), retain saved128 and free data |
| R6 | GetPicture ignores a stream registration with the same type; original video/audio/EOF/reset/create Demux stream test remains unmodified and green |
| Detailed new-case stdout | `r1-r6-results.txt`, complete tail |
| Reviewable implementation | `behavior.diff`; before/after source gzip snapshots, no generated or CSV diff |

| Completed build audit | Receipt |
|---|---|
| Source-only build | rc0, 564.842s, no binding cap; 46,731 stdout bytes, untruncated final log |
| Runner | 163,529,696B, SHA256 `e462e4482fbf5b3fe0902e793f9d677e51c56b220022bca619305f1f69967e22` |
| Suite | 5,695,128B, SHA256 `2152e5ad53f19741788aa3051e26184a9c5e831857114ce74407f199de5f04c0` |
| Name/hash audit | 9,457 generated `.cpp/.h` names and every byte hash equal to checkpoint; code-generation invocations=0 |
| Protected builds | All 1,150 pinned E16/E17 objects/libraries/PCHs/runner/suite hashes unchanged |
| Compiler inputs | Zero AppleDouble files in final compile database |
| Allocation at binary receipt | Internal1,890,865,152B; SSD288,358,400B, including fixture link starting; within declared budgets |
| Host concurrency | Ninja `-j2`, CMAKE_BUILD_PARALLEL_LEVEL=2; standard ThinLTO linker internals unchanged from E17. Completed suite ran while runner linked; no second build driver |

| Fresh probe progress guard, before launch | Receipt / limit |
|---|---|
| Source-window constraint | E7 stops ordered event rows after tick603; E15 continues lifetime counters. Continuing a progressing MPEG path beyond603 could prevent footer-to-row count agreement |
| Added guard | First sampled E7 tick≥540 triggers TERM; 63-tick reserve, polling0.25s. The declared 90s wall/75s TERM, 1M syscall and byte ceilings remain maxima |
| Scope | Evidence capture driver only; still exactly one title boot; footer tick/count/pending/truncation checked from real shutdown. No claim about dependencies beyond the captured interval |

| Remaining actual-linked gates | Receipt |
|---|---|
| Current fixture link | rc0, 289.886s, no cap/truncation; 165,183,488B; SHA256 `42d9f4f373265f5f40ea29920db6149e9043f5afbd65d2d576ea9477d6587326` |
| Fixture integrity | All five C++ fixture source hashes equal before/after; unchanged E15, E16, E17 and prior cases; actual new runner objects linked |
| E15 no-input | rc1→rc0; selection1/invocation1/callback1; validNoInputReturns1; AddBs0; resumes0; typed MPEG wait and saved128 retained |
| E15 input | rc1→rc0; selection1/invocation1/callback1; AddBs1; delivered16; resumes0; saved128 retained. Those16 EOS bytes without a sequence header do not produce a frame |
| Fixture RAM | Before request/no callback: RAM unchanged. After delivery: RAM changed by cbData initialization; no false claim of RAM equality after a behavior fix |
| Prior bindings | leaf24 / consumer3 / predicate14 / query4 / DROP rc0 |
| E16 closure | quiescent, idempotent, window-complete, disabled, unopened, fallback-error: six rc0; enabled source footers counted, pending/truncation0 |
| Additional prior coverage | Five E17 exact absorbed bindings present; three ownership audit modes rc0 again on E18 objects |
| Fresh T13 | Suite458/458 again; binary/ELF hashes, no runner, free lease, resource admission, trace-align selftest and expected fork status; `e18a-preflight.json` |

| Sole guarded probe | Receipt |
|---|---|
| Claim / boot / release | `boot-attempt.json`, `e18a-result.json`; one launch, shared `/tmp/ssx3-p-lane-lease`, REPORT_ALL=1; release2026-09-21T19:27:31.534922Z |
| Exit / cap | rc0, 75.363s, wall TERM guard; no SIGKILL. Added event-tick guard did not bind: guest events stopped at249 |
| Closed byte accounting | Logical150,717,419B / allocated216,006,656B; trace54,822 lines; every declared cap fits; no runner and lease absent |
| Source footers | Real run-exit tick4446: calls10=returned9+unwound1; pending0; selections1; invocations1; registrations1; registrationTruncated0 |
| E7 footer | events6401; bootBytes1,021,759; boundaryBytes29,747; packetBytes3392/files2; boot/boundary/packetTruncated0; windowComplete0; aligned1/arm226 |
| Counter closure | All10 call/exit pairs match; selection/invocation/event/byte counts equal retained rows; complete newline/tail. Diagnostic pending0 is not a claim that the guest MPEG wait ended |
| Observation window | Last guest event tick249; shutdown tick4446. E15 lifetime counters still equal retained rows, proving no additional instrumented MPEG calls after the recorded input. No source-footer synthesis |

| Dynamic MPEG join | This run's receipt |
|---|---|
| Lifetime | Init1; Create1 succeeds. MPEG object `0x587b30` derived from this run's Create.a0 and joined to registration/request/token; numeric equality with earlier runs is not the join criterion. No title Delete/Reset observed |
| Registration | type1, callback `0x3b0b10`, userdata `0x587b00`, returned handle1; matching request-registration shadow |
| Request | GetPicture `0x402a10`, supplied continuation `0x3b1028`, SP `0x1fffd60`, thread1; unwinds into current-thread callback |
| Selection / delivery | One direct selection; one actual callback entry, word0=1/readable, `(mpeg,cbData,userdata)` matches registration. Callback SP/thread equal caller; supplied callback RA0 reaches HLE completion sentinel |
| Producer | Callback→`0x3b0b40`→`0x3b06b0`; guarded userdata sourceObject `0x5487c0`; returned descriptor `0x548800`, data `0xd48748`, bytes5036; source-release `0x3b06f8` observed |
| AddBs | `0x4029d0` called once inside the observed callback scope; buffer `0xdc8340`, requested5040, returned5040; safe hash span5040, FNV64 `0xd2a9588f0e0fd358`; first64 bytes retained |
| Callback return | Completed once with v0=1; runtime discards it. Valid-no-input returns0 for this title callback because its actual AddBs is joined, not inferred from v0 |
| Decoder / frame | Host FFmpeg ON: input5040, parsed5040, packets0, newFrames0, totalFrames0; `decoderFailed=0`; no decoded-frame log |
| Completion / resume | Completion events0, matched waiters0; main Waiting/Mpeg at pc=ra=`0x3b1028`, SP `0x1fffd60`; no observed successor past the original request |
| Exact stop edge | Accepted initial input → complete parser packet / decoded frame → GetPicture wake is incomplete. No second callback/input/completion observed; existing log `ended=0 failed=0 sawInput=1` |
| Separation | Delivery is observed and ABI-owned. Parser buffering with no output is observed; a decoder error, EOF, or device-codec outcome is not established |
| Source for next brief | `dispatchGuestNonStreamCallback` completion calls `getMpegPicture(..., false)`; empty decoder output reaches the typed MPEG wait. Further-input demand/packet-boundary progress is the named next dependency; no second fix made |

| Guarded graphics join | Receipt |
|---|---|
| Objects / alignment | MC constructor + UI pointer guard joined; UI3→6 event; arm226, freeze227 |
| Packet / consumer | 206 source-copy events and206 matching GS-consumer joins; two retained packets, parse end exact; packet file/byte footer counts match |
| VRAM / Present | Arm-tick copy joins source→display→host field Present with exact field/hash match; `e18a-graphics.json` |
| Temporal boundary | E4 frozen interval is [226,227); copies at227 alone do not establish frozen-source contents |
| Dependency limit | The aligned graphics path predates the MPEG request at249. It does not establish movie decode or completion |

| Handoff boundary | Next action / preserved constraint |
|---|---|
| E-track | Name and measure the initial-input→additional-input/packet/frame dependency. Preserve valid-no-input waits and callback v0-discard; no fabricated EOF, frame, semaphore wake, guest-gate bypass or decoder patch in E18 |
| I-lane S9 | After consuming the E18 fork commit: their separate rebuild + reinstall +90s diagnostic probe, including sema-create cross-check; compare callback/AddBs and first post-delivery wall. No I-lane/device execution performed here |
| Device residual | Host parser output0 does not establish the FFmpeg-OFF device decoder outcome; I20's device Cause-B remains a separately observed/re-probed dependency |
| Payload limit | Complete 5040B guest payload was not separately dumped; retained evidence has first64 bytes and full-span hash. Do not claim standalone full-payload decoder replay |
| Stop compliance | No behavior edits after the demonstrated edge; no second title boot; MPEG.h/main/scheduler/CSV/generated sources unchanged |

| Publication | Receipt |
|---|---|
| Fork BEHAVIOR commit | `3adc0478b6d2260acdd28a249466f2eef9a20176`; prefix `[E18]`; trailer `Orchestrated-By: Muse Code` |
| Exact staged set | `ps2xRuntime/src/lib/Kernel/Stubs/MPEG.cpp` +189/−3; `ps2xTest/src/ps2_runtime_expansion_tests.cpp` +284/−0; two files only |
| Push / agreement | `git push fork HEAD:refs/heads/ssx3`; subsequent ls-remote and tracking ref both equal `3adc0478…`; `fork-push.json` |
| Fork status | Tracked source/index clean; preexisting untracked `ps2_log.txt` remains. Preexisting `.git` AppleDouble index warnings recorded; no metadata deletion or unrelated commit |
| No source expansion | MPEG.h, scheduler, main, CSV/TOML and all9457 generated names/hashes unchanged; 1150 protected E16/E17 build artifacts still equal after the probe and commit |
| Handoff | `NEXT-BRIEF.md`: exact post-delivery edge, ABI/lifetime constraints, committed file summary, I-lane rebuild/reinstall/90s trigger |

| Standalone retention / final allocation | Receipt |
|---|---|
| Canonical capture | 29 source files →25 unique canonical files; all hashes equal; 150,582,251 logical source bytes, canonical allocated3,645,440B; SSD originals preserved |
| Independent verification | `e18_verify_retained.py` read zero SSD original payloads; canonical-only MPEG and graphics miners reproduce joins and real footer counts |
| Retention accounting | Closed aggregate includes ExFAT metadata; canonical evidence excludes AppleDouble metadata, which remains on SSD. No raw-capture reclamation |
| Final pre-evidence-Git allocation | Internal1,895,751,680B (build1,870,770,176 / evidence24,981,504); SSD807,403,520B including35,651,584 positive fork source/Git growth; budgets6GiB/16GiB |
| Remaining free at audit | Internal10,772,480,000B; SSD223,346,688,000B; floor+guard2.5GiB retained |
| Full final audit | `final-audit.json`; runner/suite/current fixture hashes unchanged, one boot, no lease, no code generator invocation |
| Graphics detail | Counter1..206 continuous (tick41..248); producer/display each7103 nonblack RGB pixels; shifted-copy mismatches0; VRAM arm/freeze equal; exact host field uploads at226 and227 |
| Unfinished behavior | GetPicture completion remains unobserved for title input; the next input/parser-output dependency is tabled, not repaired |
| Explicit limits | No full5040B payload replay, device probe, device decoder claim, later guest successor, or second behavior fix |

| Exact command entry points | Full arguments / receipts |
|---|---|
| Configure/build | `e18_configure.py`; `ninja -C /tmp/e18-mpeg-link/runtime -j2 ps2EntryRunner ps2x_tests`; `configure-command.json` and both build start/result receipts |
| Regressions | `e18_validate.py` labels baseline/current, `e18_extra.py`; exact binary/mode/cwd/environment in validation JSONs and `commands-all-bounded.json` |
| Sole probe | `python3 local/research/E18/e18_capture.py a --report-all --wall 90`; full environment/caps/T13 in `e18a-config.json` and `e18a-preflight.json` |
| Analysis / archive | `e18_analyze.py`, `e18_retain.py a`, `e18_verify_retained.py`; canonical replay uses `E18_CANONICAL_ONLY=1` |
| Publication | `e18_commit_fork.py`; all git arguments/results in `fork-commit-commands.json`; source/type changes only in the named staged set |
| Reproduction index | `COMMANDS.md`; scripts and required prior fixture/helper sources are local to E18 |
| Hygiene | Report written in bounded chunks; real source tail and full file prefix checked below. Initial AppleDouble compiler log is explicitly incomplete; successful source-only build and all test/probe receipts have complete tails |

| Evidence publication budget | Receipt |
|---|---|
| Named force-add | E18 only; initial staged files300; main Git positive allocated growth3002368B of32MiB cap; at least1MiB commit reserve |
| Git accounting | `main-git-before.json`, `evidence-stage.json`; automatic Git maintenance disabled for the commit; no main-repository push |
| Final stop | Fork3adc0478 pushed; one probe spent; parser-output/further-input edge handed off; local evidence commit ends E18 |

| Tail receipt | Value |
|---|---|
| Complete prefix | Lines1–181; 20284B; SHA256 `97c36f47d4d8dedbb19778feb18007d57ba3da0b6c0f06d1d1e9b9ebd99f3577` |
| Source tails | Real E15/E7 run-exit footers, count match, pending0/truncation0; retained file ends with newline |
| E18 REPORT TAIL COMPLETE | Tables complete; no second fix or boot; main evidence publication only |
