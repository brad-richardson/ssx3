| E21 | Receipt |
|---|---|
| Stop point | All gates executed: forwarding proven in isolation, observer-loaded regression green, Q1 threshold tabled, Q2 static absence proven, Q3 demand watched. Fix gate closed: X named, STOP (policy invention required, explicitly excluded). |
| Checkpoint | Fork `3adc0478b6d2260acdd28a249466f2eef9a20176` triple-agreed; 9,457 generated names/hashes; 1,725 protected builds; baseline 458/458; E15 rc0s; E16 closure 6; prior 24/3/14/4/DROP; E18 R1–R6 in suite text. |
| Questions reached | Q1 threshold (9 runs, byte-exact packet-1), Q2 static demand audit (proven absence), Q3 demand watch (guest never sends more). |
| Mutations / launches | Zero fork source edits, zero fork commits, one guarded title boot (wall-bound, rc0), one lease claim/release. No target fix, no regeneration. |
| Next dependency | After a successful-but-incomplete AddBs the runtime never asks again (Q2) and the guest never volunteers more (Q3). The missing signal X: a second input-demand edge. A later brief must also drop `stdbuf` from the boot argv (it swallows `DYLD_INSERT_LIBRARIES`). |

| Experiment contract | Bound / observable |
|---|---|
| Time box | Start `2026-09-21T21:14:22Z`; deadline `2026-09-22T05:14:22Z`; eight hours. Final audit `2026-09-21T22:13:03Z`; all work inside the box. |
| Required reads | E19 REPORT 124 lines, NEXT-BRIEF 17 lines, E18 NEXT-BRIEF 41 lines, E20 prompt 104 lines, E21 prompt 68 lines, all read fully incl. tails; verbatim copies retained (`E19-REPORT.md`, `E19-NEXT-BRIEF.md`, `E18-NEXT-BRIEF.md`, `E20-PROMPT.md`, `E21-PROMPT.md`). E20 partial landing `51d786c` read as reference, never edited. |
| Hypothesis | Direct imports in the interposing image retain the real backend binding; `RTLD_NEXT` can return an interposed result. Verified locally (mechanism table below), not inherited. |
| Observable | 1:1 enter→backend→return with byte-identical results; authored-byte marks 5,040/8,192/16,384 packets/frames; bytewise packet-1; demand signal or proven absence; one guarded boot second-request verdict. |
| Alternatives | Transparent observation or forwarding gap; complete boundary or insufficient input; caller/guest re-request or undrained buffer/missing signal. |
| Strict order | Checkpoint → isolation proof → loaded regression → Q1 → Q2 → Q3. All opened in order; no red gate tripped. |
| Fix gate | Exactly one demonstrated edge + minimal ABI-preserving change + own fail-before + full regression. Guest-needs-X → name X and stop. Closed: any fix here invents demand policy. |
| Preserved constraints | Caller-owned synchronous dispatch; word0-only cbData; v0 discarded; valid-no-input waits; dispatch outside the MPEG mutex; delete/reset cancellation. No CSV, main, scheduler or stream-callback edits. |
| Contract source | `CONTRACT.md`, written after fresh fitting admission and before compilation or fork edits. |

| Storage / execution budget | Admission and accounting |
|---|---|
| Internal reservation | 3 GiB: isolated build 2, evidence 0.5, observer/scratch 0.25, reserve 0.25 incl. main-Git 64 MiB; floor 2 GiB + 0.5 GiB guard. Required 5,905,580,032 B. |
| SSD reservation | 16 GiB: tooltmp 8, fixtures 2, probe 1.5, possible source/Git 1, reserve 3.5; same 2.5 GiB floor/guard. Required 19,864,223,744 B. |
| Initial admission | `2026-09-21T21:14:22Z`: internal 6,512,640,000 B / SSD 178,257,920,000 B free. Both reservations fit; `initial-admission.json`. |
| Fresh admissions | Every bounded tool saved its start sample and checked remaining reservation plus floor; all entered fitting. |
| Final audit sample | Internal owned 6,025,216 B; SSD owned 740,294,656 B across 22 `e21-*` paths (threshold binary, tooltmp, fixtures, boot artifacts); fork growth 0. Internal free 5,718,056,960 B; SSD free 185,175,375,872 B. `final-audit.json`. |
| Accounting | `st_blocks × 512`, incl. ExFAT directory/AppleDouble allocation, E21-owned paths and positive fork source/Git growth; `COPYFILE_DISABLE=1` for SSD steps. No reclaim or deletion. |
| Protected | `/tmp/p1-link`, `/tmp/e17-map-link`, `/tmp/e18-mpeg-link` and DerivedData reserved; all 1,725 protected hashes re-verified equal at close. No protected build command run. |
| Tool limits | Host parallelism 2; one direct compiler/linker process per build step; encoder unused (no re-encoding). `ninja -t commands` read the existing link recipe only. |
| Process caps | Link 1,200 s; stdout 16 MiB with 1 MiB reserve; tooltmp 8 GiB with 512 MiB reserve; fixtures 2 GiB with 64 MiB reserve; polling 0.25 s. Suite wall 60 s, stdout 4 MiB, scratch 32 MiB. |
| Parser caps | Payload ≤64 KiB per authored case (max 23,731 B); case process 300 s; aggregate fixture evidence <64 MiB. Observer text 12 MiB / retained API-input blob 2 MiB. Backend EOF never fabricated. |
| Probe caps | One launch; wall 90 s / TERM 75 s; 1,000,000 syscall lines; aggregate 1.5 GiB logical/allocated; boot 256 MiB, trace 96 MiB, function 1 GiB; E4 12/64 MiB, park 32/128, frames 32/64, E7 8/64, parser 16/64; 8 MiB reserve. No tick540 stop. Bound hit: wall only. |
| Lease | Atomic `/tmp/ssx3-p-lane-lease`, never waited; 1 claim / 1 clean release; post-release `pgrep` rc1, lease absent. |

| Checkpoint re-verification | Receipt |
|---|---|
| Fork identity | HEAD, `refs/remotes/fork/ssx3`, and `git ls-remote fork refs/heads/ssx3` agree at `3adc0478b6d2260acdd28a249466f2eef9a20176`; `fork-before.json` (21:16:47Z) and `final-audit.json` (close). Preexisting AppleDouble Git-index warning retained. |
| Generated names / bytes | 9,457 `.cpp`/`.h` files; every SHA256 matches E18's manifest at open and at close. `before-generated.json`. |
| Protected build hashes | 1,725 objects/archives/PCH/runners/suites across the three retained builds; all re-hashed equal at close. `protected-build-before.json`, `final-audit.json`. |
| Runner | 163,529,696 B; SHA256 `e462e4482fbf5b3fe0902e793f9d677e51c56b220022bca619305f1f69967e22`. |
| Suite | 5,695,128 B; SHA256 `2152e5ad53f19741788aa3051e26184a9c5e831857114ce74407f199de5f04c0`. |
| Prior actual fixture | Reused SSD `P1/e18-fixtures/after/binding-test`, 165,183,488 B; SHA256 `42d9f4f373265f5f40ea29920db6149e9043f5afbd65d2d576ea9477d6587326`. |
| Full suite / E18 R1–R6 | rc0, 458 passed / 0 failed, 1.086 s, suite SHA pinned; `checkpoint-suite.txt/json`. R1–R6 present in suite text. |
| Prior bindings | leaf 24 / consumer 3 / predicate 14 / query 4 / DROP, all rc0; `checkpoint-bindings-validation.json`. |
| E15 no-input / input | Both rc0 with `saved128=1`, `waitReason=6`, `callbackCalls=1`, `resumes=0`; delivered 0 / 16 bytes; E15/E7 closure counts match. |
| E16 closure | Six rc0 (`quiescent`, `idempotent`, `window-complete`, `disabled`, `unopened`, `fallback-error`); strict counter/byte closure checks pass. |
| Absorbed entries | Five presence checks rc0 (`0x14f2a8`, `0x156750`, `0x243a80`, `0x395730`, `0x3a0158`). Ownership controls rc0. `checkpoint-extra-validation.json`. |

| Observer lineage | Receipt |
|---|---|
| Starting input | E20's repaired `e20_parser_observer.c/.h` (direct-import bindings, recursion guards, proof events, schema-2 stats), copied to `e21_*` with mechanical E20→E21 identifier/path rename only. |
| Rename proof | Normalized diff (E20/E21 tokens unified) is byte-empty for both `.c` and `.h`; wire schema stays 2. CONTRACT line 17. |
| Build | `parser/e21-parser-observer.dylib`, 52,472 B, SHA256 `e4d88fdc6740449893d5a96c112fae6ce3f19135bad8a309d140d45bbf38e6be`; zero compiler warnings. `parser-build-commands.json`, `parser-build.json`. |
| E19/E20 failed artifacts | Never loaded for any suite, fixture, or title run. E20 dir read-only reference. |

| Isolation proof (minimal non-title harness) | Receipt |
|---|---|
| Harness | `parser/e21-isolation-test`, 35,072 B, SHA256 `f6059aa07e261da68b8bfa9f508e649a7e1c8ddd496e5ac4bf0e89e5aa2ded3f`. Modes: `feed` (parser+decoder over fixed 1,000 B chunks, canonical record incl. packet FNV and frame-plane FNV), `exitcode` (`_Exit` path), `addrs` (address-only mechanism). No guest runtime. |
| Feed input | `authored-black.m2v` (7,369 B complete authored stream; the GOP-only continuation lacks the sequence header and the decoder rightly rejects it — first attempt tabled this, then fixed). |
| Byte identity | Uninstrumented vs observer-loaded (`PS2X_E21_PROOF=1`) records byte-identical: 1,862 B, FNV64 `0x74130eff64b134a2`. `isolation-feed-record.txt`. |
| Observer footer (loaded feed) | `reason=destructor rc=0`: parseCalls 13, offered 11,620, consumed 7,369, packets 7, packetBytes 7,099, sends 7, receives 13, frames 6, errors 0, returned 33, pending 0, truncation 0, ioErrors 0; **backendParse 13 / backendSend 7 / backendReceive 13** (exact 1:1); bindingChecks 4, recursionGuards 0, proof 1. `isolation-proof.json`. |
| Receipt strictness | `e21_parser_receipt.py` verifies closure footer, seq continuity, event/byte/counter joins, 1:1 backend counts, 4/4 valid bindings. Applied to every observer run in E21. |
| `_Exit` closure | `exitcode 3`: rc 3 both uninstrumented and loaded; loaded footer `reason=_Exit rc=3` with parseCalls 1, pending 0. Real `_Exit` counter closure proven separately. |
| First-attempt record | Attempt a1 (continuation input, non-refcounted packets): byte-identical but decoder INVALIDDATA, receives 0 — receipt correctly refused the 1:1 receive proof. Retained under `P1/e21-fixtures/isolation/` without an `a2` overwrite; a2 is the proof. |

| Forwarding mechanism (why `RTLD_NEXT` lied) | Receipt |
|---|---|
| Uninstrumented (`addrs` plain) | All four APIs: direct == `RTLD_NEXT` == explicit-handle == real image (`libavcodec.63.1.101.dylib`, `libsystem_c.dylib`). `isolation-addrs-plain.txt`. |
| Loaded main image (`addrs` loaded) | Direct == `RTLD_NEXT` == observer replacement; explicit dlopen of the observer path yields `0x0` (no such export). Generic interposition rewrites every lookup style in a normal image. `isolation-addrs-loaded.txt`. |
| Loaded observer image (binding events) | Direct imports == real backend images with valid symbols (`valid=1` × 4); `RTLD_NEXT` == replacement (`nextIsReplacement=1` × 4); explicit dlopen of the *real* libavcodec + `dlsym` == replacement too (`explicitIsReplacement=1` × 4). `isolation-proof.json` bindings. |
| Mechanism verdict | E20's audit claim verified locally: only the interposing image's own direct imports preserve the original binding. E19's `RTLD_NEXT` self-call is explained (it returned the replacement), and the explicit-handle alternative is *also* disproven — it returns the interposed address. No inheritance; all three styles compared by address without invoking candidates. |

| Observer-loaded full regression | Receipt |
|---|---|
| Suite | rc0, 458 passed / 0 failed WITH `e21-parser-observer.dylib` loaded. `observer-suite.txt/json`. |
| Suite observation | Suite observer footer: parse 8, packets 4, frames 2, errors 0, pending 0, `reason=_Exit rc=0` — R3's real decode observed through the repaired path that killed E19. |
| Bindings + closure + extras | Prior/no-input/input, all six closure modes, same assertions as checkpoint — all rc0 loaded. `observer-bindings-validation.json`, `observer-closure-validation.json`. |
| Closure receipts | 10/10 observer dirs receipt-verified (pending/truncation/ioErrors 0, 1:1 backend, 4/4 bindings); `_Exit rc=0` footers for suite + quiescent/idempotent/window-complete/disabled/unopened. `observer-regression.json`, `observer-receipts/`. |

| Q1 threshold fixtures | Receipt |
|---|---|
| Fixture binary | `P1/e21-fixtures/threshold/binding-test` relinked from the current unmodified runner object set + `e21_binding_test.cpp` (actual Create/AddBs wrappers, saved128-checked); E15–E18/prior chain sources carried verbatim (hashes match E19). `threshold-fixture-link.json`, `threshold-fixture-binary.json`. |
| Inputs | E20's eight carried files re-verified by hash (no re-encoding): first64 `44cb3691…`, authored `e4bb4aef…`, continuation `b2b51539…`, four boundary cases, userdata-only control. `carried-inputs.json`. All runs observer-loaded, EOF sends 0. |
| Raw retention | Per-run `parser-events.txt`/`parser-input.bin` gzipped under `threshold-raw/`; aggregate parser-cases <64 MiB. `threshold-results.json` (9 cases), `q1-complete.json`. |

| Authored case | Total bytes | At 5,040 fed | At 8,192 fed | At 16,384 fed | Packet-1 (byte-exact fed) | End packets/frames |
|---|---:|---|---|---|---|---|
| Boundary at 64 | 16,384 | 0 / 0 | 7 / 6 | 7 / 6 | 5,525 (= 64 + 5,461) | 7 / 6 |
| Boundary at 5,040 | 16,384 | 0 / 0 | 0 / 0 | 7 / 6 | 10,501 (= 5,040 + 5,461) | 7 / 6 |
| Boundary at 8,192 | 16,384 | 0 / 0 | 0 / 0 | 7 / 6 | 13,653 (= 8,192 + 5,461) | 7 / 6 |
| Boundary at 16,384 | 23,731 | 0 / 0 | 0 / 0 | 0 / 0 (7 / 6 at 23,731) | 21,845 (= 16,384 + 5,461) | 7 / 6 |
| User-data-only control | 16,384 | 0 / 0 | 0 / 0 | 0 / 0 | never (byte mode N/A) | 0 / 0 |

| Q1 threshold shape | Receipt |
|---|---|
| Packet-1 rule | First packet emits exactly when fed bytes reach GOP offset + 5,461 continuation bytes in all four GOP cases (bytewise mode, 1 B/AddBs from byte 64; `firstPacketAtFed` in `THRESHOLD` lines). 5,461 = 5,457 first-picture bytes + 4 next-start-code lookahead bytes the parser holds back. |
| First-packet size | 5,521 / 10,497 / 13,649 / 21,841 = all bytes fed so far minus the 4 held-back bytes (parser emits the buffered run, incl. `X` padding, as packet 1). Marks-mode first-packet calls: 3/4/4/5. |
| E18 volume | At 5,040 fed bytes every case shows packets 0 / frames 0 — E18's `parsed=5040 packets=0` is the expected pre-threshold state, not a decoder failure (`errors=0`, `decoderFailed=0` throughout). |
| Parser call shape | AddBs wrapper splits input into its own parser chunking (e.g. 3 AddBs → 10 parse calls at the 8,192 mark); consumed == fed in every run; sendEof 0 everywhere. |
| Scope limit | Only bytes actually fed support results; no full-E18-payload replay (only its first64 are retained); no universal threshold claim beyond these labeled inputs. |

| Q2 static demand audit | Receipt |
|---|---|
| Sole input-request site | `getMpegPicture` MPEG.cpp L2467–2493: type-1 delivery + caller-thread `HleCall` dispatch, only when `requestInput && !delivery && frames empty && !eof && !streamEnded && !decoderFailed`. Full table in `Q2-AUDIT.md`. |
| Post-callback re-request | Absent by construction: `onComplete` continues with `requestInput=false` (L1757–1760, "without re-triggering it"). |
| Resume re-request | Suppressed: the parked `waitExternal` lambda captures the live delivery (L2518), so `pending.lock()` (L2465) still succeeds. |
| Park primitive | `waitExternal(Mpeg, 1, mpegAddr)` is `[[noreturn]]`, no timeout (`ee_scheduler.h:337`); exit only via `completeExternalWait`. |
| AddBs wake signal | L2053: wakes ONLY on frame-count change, `streamEnded`, or `decoderFailed`. Accepted-but-buffered bytes → silence. No other wake source fires on the AddBs-only path (demux/EOF/flush/cancel enumerated and excluded). |
| Guest re-call while parked | Hits the same gate with the first delivery alive → no second delivery, second park. |
| Runtime second-request verdict | No static path to a second input callback after successful-but-incomplete AddBs. E18's post-input silence is the predicted shape. |

| Q3 demand-watch boot (e21a) | Receipt |
|---|---|
| Pre-claims + lease | Fresh T13 battery green: process/binary/ELF/aligner/suite/hash/space (`e21a-preflight.json`); suite preclaim 458/458; atomic claim `E21A`, clean release; post-release `pgrep` rc1. `boot-attempt.json` (sole boot). |
| Bound / rc / window | `bound=wall`, rc 0, 75.8 s; 54,908 syscall lines (cap 1M); E7 tick 4,502 with complete footers; all byte caps ≤ 10% except function log at 12%. `e21a-result.json`, `e21a-liveness.txt`. |
| Demand verdict | ONE registration, ONE type-1 callback (`0x3b0b10`, cbWordReadable=1), ONE AddBs (requested 5,040 / returned 5,040), ZERO completions, ONE park (`mpeg-wait` thread 1 pc=ra=`0x3b1028` sp=`0x1fffd60` reason 6). Guest never sent more through the full 75 s window. `e21a-mpeg.json`, `q3-complete.json`. |
| E7 closure | 6,401 events (same count as E18); `# E15 CLOSURE tick=4502 calls=10 returned=9 unwound=1 pending=0 selections=1 invocations=1`; `# E7 SHUTDOWN` byte-exact, all truncation flags 0. |
| Host parser counters | `[MPEG:feed] inSize=5040 parsed=5040 packets=0 newFrames=0 totalFrames=0`; `[MPEG:feedES] size=5040 first4=000001b3 decoderFailed=0`; `[MPEG:GetPicture] waiting … sawInput=1`. Byte-identical shape to E18. |
| Parser-observation gap | The per-call observer log is absent: `RUN/e21a-parser/` is empty. Cause isolated to the boot argv, not the observer — macOS `stdbuf` replaces `DYLD_INSERT_LIBRARIES` with its own injection. Controlled proof: identical harness invocation yields 0 observer files under `stdbuf` vs 2 files direct (`stdbuf-with-stdbuf*.txt`, `stdbuf-direct*.txt`; the `stdbuf` addrs show uninterposed libavcodec). A second (observer-loaded, `stdbuf`-free) boot is FORBIDDEN by the one-boot rule — named below as the next dependency. |
| Gap consequence | None for the demand verdict (E7 + host feed counters are complete and the boot ran fully unperturbed/uninstrumented, matching E18's instrumentation level). Per-call parser timing inside the title window remains unobserved. |

| Fix gate | Receipt |
|---|---|
| Demonstrated edges | (1) Runtime never re-requests after buffered-but-incomplete AddBs (Q2 static proof). (2) Guest never volunteers more unprompted (Q3 dynamic proof). (3) Packet 1 needs GOP + 5,461 continuation bytes; E18's 5,040 B cannot emit (Q1). |
| Gate decision | STOP with X named. Any "fix" here invents a demand policy the firmware's true shape is unknown for (re-dispatch? re-wake on buffered bytes? guest retry policing?) — policy invention is explicitly excluded. Per brief: "Guest never sends more without X" → X = a second input-demand signal, and STOP. |
| Mutations | Zero fork source edits, zero fork commits, zero pushes to fork. Diagnosis-only. |

| Exact command record | Invocation / artifact |
|---|---|
| Environment | SSD/tool steps: `export COPYFILE_DISABLE=1 PYTHONDONTWRITEBYTECODE=1`; bounded wrapper sets task-specific TMPDIR and `CMAKE_BUILD_PARALLEL_LEVEL=2`. |
| Opening audit | `python3 local/research/E21/e21_checkpoint.py` (prior session); receipts `fork-before.json`, `before-generated.json`, `protected-build-before.json`, `checkpoint.json`. |
| Checkpoint | `python3 local/research/E21/e21_bounded.py checkpoint-regression 1200 -- python3 local/research/E21/e21_baseline.py`; rc0. |
| Parser build | `… e21_bounded.py parser-prepare 1200 -- … e21_prepare_parser.py` (inputs + dylib + harness); `… parser-rebuild 1200 …` (harness fix: refcounted packets). |
| Isolation | `… e21_bounded.py isolation-proof 1200 -- … e21_isolation.py` (a1: receipt refused, INVALIDDATA diagnosis); `… isolation-proof2 1200 …` (a2: green). |
| Loaded regression | `… e21_bounded.py observer-regression 1200 -- … e21_observer_regression.py`; rc0, 458/458 loaded. |
| Threshold link/run | `… e21_bounded.py threshold-link 1200 -- … e21_link_test.py threshold`; `… threshold-run 1200 -- … e21_threshold.py`; 9/9 runs rc0. |
| Probe gates | `python3 local/research/E21/e21_prepare_probe.py`; then `python3 local/research/E21/e21_capture.py a --report-all` (sole boot, own caps/lease logic); `python3 local/research/E21/e21_mine.py`. |
| Stdbuf control | Two direct harness invocations (with/without `stdbuf`), outputs in `stdbuf-*.txt`. |
| Final close | `python3 local/research/E21/e21_close.py`; all 9,457 + 1,725 hashes rechecked; fork HEAD/ref/remote agree unchanged; lease absent; 1 boot / 1 claim / 0 fork commits. |
| Never executed | Any fork edit, commit, or push; any game regeneration; a second title boot; E19's or E20's dylib in any run. |

| Evidence hygiene / handoff | Receipt |
|---|---|
| Standalone data | Full baseline + loaded logs, isolation records, threshold raws (gz), E7/boot/park/run artifacts referenced by hash, Q2 audit, Q3 joins, stdbuf control, complete commands, final audit. |
| `.suite-*` scratch | Remains unstaged (checkpoint, observer, preclaim); loaded-suite observer receipts preserved canonically under `observer-receipts/`. |
| Tail qualification | Every bounded tool, fixture, suite, receipt, and boot artifact ends with its real `TAIL COMPLETE` / closure footer; counts re-verified, never appended. |
| Publication | `[E21]` evidence commit with `Orchestrated-By: Muse Code`; verify-then-push. Scope: E21 evidence only; no fork files, no generated sources. |

| Tail receipt | Value |
|---|---|
| Complete prefix | Lines 1–148; 20667 B; SHA256 `1565a09db3559a1259291a7349faf50fffcbaea59318bcdcf1887ca21c207722` |
| Source-tail gap | None: every E21 capture (suite, fixtures, isolation, threshold, boot E7) carries its real runtime closure footer. The e21a per-call parser log is absent by boot-argv cause (stdbuf), tabled above — not a tail repair. |
| E21 REPORT TAIL COMPLETE | Forwarding proven, Q1/Q2/Q3 answered, fix gate stopped with X named; 1 boot, 0 fork edits/commits; evidence publication ends E21. |
