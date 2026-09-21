| E19 | Receipt |
|---|---|
| Stop point | The new evidence-only parser interposer caused the pinned suite to exit with SIGSEGV at E18 R3. E19's **“Any red: table + stop (no boot on red)”** rule closed experimental work. |
| Checkpoint | Fork `3adc0478b6d2260acdd28a249466f2eef9a20176`; 9,457 generated names/hashes; baseline 458/458; E15 delivery cases rc0; E16 closure6 and prior bindings rc0. |
| Questions reached | Q1 preparation only. No valid threshold measurement. Q2 demand audit and Q3 guest demand watch did not open. |
| Mutations / launches | Zero fork source edits, zero fork commits, zero title boots, zero shared-lane lease claims. No target behavior fix or game regeneration. |
| Next dependency | Repair and prove the **observation forwarding path to the original `av_parser_parse2`** in a later brief before interpreting parser counts. E18's input→packet dependency remains unclassified. |

| Experiment contract | Bound / observable |
|---|---|
| Time box | Start `2026-09-21T19:48:28Z`; deadline `2026-09-22T03:48:28Z`; eight hours. The red gate occurred at approximately `20:06:34Z`; only stopping, retention, audit and evidence publication followed. |
| Required reads | E18 REPORT all 187 lines and NEXT-BRIEF all 41 lines, including complete tails, read first; verbatim copies retained as `E18-REPORT.md` and `E18-NEXT-BRIEF.md`. |
| Hypothesis | A completed picture boundary may be needed before packet 1; successful but incomplete AddBs input may leave a further-input signal missing. This was a hypothesis, not an established E19 result. |
| Observable | At cumulative 5,040 / 8,192 / 16,384 authored-byte marks: actual AddBs accepted bytes, parser consumption/packets and decoded frames; a bytewise control locates packet 1. |
| Alternatives | A supplied boundary emits; input remains buffered; caller requests again; guest sends again; an undrained remainder exists; or a missing signal must be named. |
| Strict order | Checkpoint → Q1 receipts → Q2 static demand audit/E18 silence → Q3 one guarded boot. Q1 did not finish, so later questions stayed closed. |
| Fix gate | Exactly one demonstrated target edge, ABI-preserving minimal change, own fail-before and full regression. Unknown guest signal, decoder/EOF/policy invention, regeneration requirement or any regression red stops. |
| Preserved constraints | Caller-owned synchronous dispatch; word0-only cbData; v0 discarded; valid-no-input waits; dispatch outside the MPEG mutex; delete/reset cancellation. No CSV, main, scheduler or stream-callback edits. |
| Contract source | `CONTRACT.md`, written after fresh fitting admission and before compilation or fork edits. |

| Storage / execution budget | Admission and accounting |
|---|---|
| Internal reservation | 6 GiB: possible isolated build4, evidence1, parser/scratch0.5, reserve0.5 including main-Git64 MiB; free floor2 GiB plus0.5 GiB guard. Required9,126,805,504 B. |
| SSD reservation | 16 GiB: tooltmp8, fixtures2, probe1.5, possible source/Git1, reserve3.5; same2.5 GiB floor/guard. Required19,864,223,744 B. |
| Initial admission | `2026-09-21T19:52:59.697534Z`: internal9,707,520,000 B / SSD217,055,232,000 B free. Both reservations fit before E19 creation; `initial-admission.json`. |
| Fresh admissions | Every bounded tool saved its start sample and checked remaining reservation plus floor. Checkpoint, parser preparation, link and observer regression all entered under fitting admission. |
| Accounting | `st_blocks × 512`, including ExFAT directory/AppleDouble allocation, E19-owned paths and positive fork source/Git growth; `COPYFILE_DISABLE=1` for SSD steps. No reclaim or deletion. |
| Protected | `/tmp/p1-link`, `/tmp/e17-map-link`, `/tmp/e18-mpeg-link` and DerivedData reserved. Existing objects were read; no protected build command was run. |
| Tool limits | Host parallelism2; one direct fixture compiler/linker process, with the independent single-suite process overlapping part of the link. Encoder threads1. No Ninja build; `ninja -t commands` read the existing link recipe. |
| Process caps | Link1,200 s; stdout16 MiB with1 MiB reserve; tooltmp8 GiB with512 MiB reserve; fixtures2 GiB with64 MiB reserve; polling0.25 s. Suite wall60 s, stdout4 MiB, scratch32 MiB. |
| Parser caps | Payload≤64 KiB per authored case; case process120 s; aggregate fixture evidence64 MiB. Observer text12 MiB / retained API-input blob2 MiB, inside the declared parser16 MiB logical allowance. |
| Reserved probe caps | One launch maximum; wall90 s/TERM75 s;1,000,000 syscall lines; aggregate1.5 GiB logical/allocated; boot256 MiB, trace96 MiB, function1 GiB; E4 12/64 MiB, park32/128, frames32/64, E7 8/64, parser16/64;8 MiB reserve. No tick540 early stop planned. None exercised. |
| Final audit sample | Internal owned13,152,256 B; SSD owned102,760,448 B; positive fork growth0. Internal free9,751,683,072 B; SSD free197,026,381,824 B. `final-audit.json`; publication accounting follows below. |

| Checkpoint re-verification | Receipt |
|---|---|
| Fork identity | HEAD, `refs/remotes/fork/ssx3`, and `git ls-remote fork refs/heads/ssx3` agree at `3adc0478b6d2260acdd28a249466f2eef9a20176`; `fork-before.json`. |
| Generated names / bytes | 9,457 `.cpp`/`.h` files excluding AppleDouble; every SHA256 matches E18's manifest. `before-generated.json`. |
| Protected build hashes | 1,725 objects, archives, PCH files, runners and suites across the three retained builds pinned before work and re-hashed unchanged afterward. `protected-build-before.json`, `final-audit.json`. |
| Runner | 163,529,696 B; SHA256 `e462e4482fbf5b3fe0902e793f9d677e51c56b220022bca619305f1f69967e22`. |
| Suite | 5,695,128 B; SHA256 `2152e5ad53f19741788aa3051e26184a9c5e831857114ce74407f199de5f04c0`. |
| Prior actual fixture | Reused SSD `P1/e18-fixtures/after/binding-test`,165,183,488 B; SHA256 `42d9f4f373265f5f40ea29920db6149e9043f5afbd65d2d576ea9477d6587326`. No relink needed for checkpoint cases. |
| Full suite / E18 R1–R6 | rc0,458 passed/0 failed,1.437 s; `checkpoint-suite.txt/json`. R1 caller ownership/order, R2 AddBs re-entry, R3 real authored decode/resume, R4 no-input wait, R5 cancellation, R6 stream retention all pass in the baseline. |
| Prior bindings | leaf24 / consumer3 / predicate14 / query4 / DROP, all rc0; `checkpoint-bindings-prior.txt` and validation JSON. |
| E15 no-input | rc0, callback1, validNoInputReturns1, AddBsCalls0, deliveredBytes0, resumes0, waitReason6, saved128=1; real E15/E7 closure counts match. |
| E15 input | rc0, callback1, AddBsCalls1, deliveredBytes16, resumes0, waitReason6, saved128=1; real E15/E7 closure counts match. |
| E16 closure | `quiescent`, `idempotent`, `window-complete`, `disabled`, `unopened`, `fallback-error`: six rc0. Enabled source footers unique/count-matched, pending0/truncation0; disabled/unopened silent; run/join/final producer and state-preservation checks pass. |
| Absorbed entries | Actual bindings present at `0x14f2a8`, `0x156750`, `0x243a80`, `0x395730`, `0x3a0158`; five rc0. |
| Ownership fixtures | queued-ready, queued-park and current controls rc0; current invocation preserves caller thread/stack and saved context. `checkpoint-extra-validation.json`. |
| Existing metadata | Fork status was and remains `?? ps2_log.txt`; preexisting AppleDouble Git-index warning retained in command receipts. No cleanup or deletion. |

| Q1 preparation | Exact input provenance / status |
|---|---|
| E18 retained bytes | Exactly64 bytes, starting `000001b3`, copied to `parser/E18-retained-first64.bin` and verified against E18's retained event text. No complete5,040-byte E18 payload exists here. |
| Authored encoding | FFmpeg9.0.1_1 generated eight black800×448 MPEG-2 pictures at30000/1001 fps, threads1, g12, bf0, q2; output7,369 B. Encoder command and input hashes in `parser-build-commands.json` / `authored-manifest.json`. |
| Authored continuation |7,347 B from the first authored GOP start at encoder-output offset22. The four boundary cases combine the E18 first64 with explicitly authored `X` user-data padding and this authored continuation; the user-data-only control omits it. |
| Planned measurement | An extra non-title entry uses the actual generated Create/AddBs wrappers against protected E18 runner objects, verifies accepted byte counts and saved128, and reads diagnostic counters at the marks. It never ran. |
| Observer build | Evidence-only `e19_parser_observer.c/.h` → `parser/e19-parser-observer.dylib`,51,912 B. Compile/author preparation rc0,0.735 s; this established compilation only. |
| Dynamic import check | The pinned runner imports `av_parser_parse2`, `avcodec_send_packet`, `avcodec_receive_frame` and `_Exit`. The proposed dylib interception was not validated as transparent. |
| Fixture link | Existing full runner object recipe retained in `threshold-fixture-link.json`. New test object compiled; link stopped by owned-group SIGTERM after214.270 s when the observer regression failed. No usable new fixture receipt; no threshold invocation. |

| Authored case | Total bytes | Bytes retained from E18 | Packets / frames at5,040 | At8,192 | At16,384 | Packet1 threshold |
|---|---:|---:|---|---|---|---|
| Boundary at64 |16,384 |64 | Not measured | Not measured | Not measured | Not measured |
| Boundary at5,040 |16,384 |64 | Not measured | Not measured | Not measured | Not measured |
| Boundary at8,192 |16,384 |64 | Not measured | Not measured | Not measured | Not measured |
| Boundary at16,384 |23,731 |64 | Not measured | Not measured | Not measured | Not measured |
| User-data-only continuation |16,384 |64 | Not measured | Not measured | Not measured | Not measured |

| Observation regression / stop | Receipt and limit |
|---|---|
| Test configuration | Same pinned baseline suite plus `DYLD_INSERT_LIBRARIES=.../E19/parser/e19-parser-observer.dylib` and a fresh `PS2X_E19_PARSER_DIR`; `observer-suite.json`. |
| Failure | rc−11/SIGSEGV after2.957 s. Last running case: E18 R3; runtime log reached `feedES size=240 first4=000001b3`. Baseline R3 had passed. |
| Crash evidence | macOS report `ps2x_tests-2026-09-21-160641.ips`: `EXC_BAD_ACCESS`, stack-guard protection failure, repeated `observed_parse` frames; complete compressed report and summary retained. |
| Observer records |18,828 complete newline-terminated rows: one open and18,827 `parse-enter`; zero `parse-return`. Same240-byte R3 input repeated. These are recursive **observer entries**, not a valid count of host-parser calls or guest deliveries. |
| Source closure | No `# E19 PARSER CLOSURE` footer. Pending/returned/final truncation fields are unavailable. The2,097,152 B payload cap was reached;10,088 later entries retained0 B. This capture fails the measurement/closure gate. |
| Localized failure | Repeated observer frames and entry-only events demonstrate recursion in the new observation forwarding path. `real_parse` is initialized with `dlsym(RTLD_NEXT, "av_parser_parse2")` and called from `observed_parse`; its transparent forwarding assumption was false in this run. No host-parser emission conclusion follows. |
| Scope of stop | No interposer repair/retry, no threshold runs, no Q2 audit, no title boot and no target behavior change after the red gate. Only failure retention, owned-link termination, unchanged-state audit and evidence publication followed. |
| Owned process receipt | PGID94254 belonged to E19's fixture linker and children; ownership captured in `stopped-owned-link-processes.txt`; SIGTERM recorded in `stop-rule.json`. Bounded wrapper observed rc−15; no output truncation. |
| Regression distinction | Baseline checkpoint remains458/458 with all required fixtures. Observer-loaded run is incomplete/red and is not reported as458/458. Observer-loaded binding/closure follow-ons never ran. |

| Q2 / Q3 / fix gate | Receipt |
|---|---|
| E18 baseline, inherited only | E18 delivered5,040 B, reported parsed5,040/packets0/frames0, then no further instrumented MPEG events through its real run-exit closure. This is the prior report, not a new E19 demand observation. |
| Q2 static demand audit | Not opened: Q1 lacks an eligible packet-threshold receipt. E19 establishes no caller/guest/drain signal or absence. |
| Q3 fresh T13 / lease | Not opened. No T13 boot preclaim, no lease acquisition and0/1 title launches. |
| Second request / delivery | Not observed in E19; no “never asked again” claim is made. |
| GetPicture / successor | No E19 boot evidence; E18's wait at `0x3b1028` remains inherited context only. |
| Graphics alignment / real final probe footers | No E19 boot, so no new graphics or run-exit probe receipt. Baseline E16 closure fixtures remain separately receipted. |
| Target fix gate | Closed: no single target runtime edge demonstrated. Zero fork BEHAVIOR commits or pushes. |
| Next brief | Observation forwarding repair/proof first; full non-title regression; then original E19 Q1→Q2→Q3 order under a new explicit brief. Preserve all E18 ABI constraints. Do not reuse this unvalidated dylib for a title run. |

| Exact command record | Invocation / artifact |
|---|---|
| Environment | SSD/tool steps: `export COPYFILE_DISABLE=1 PYTHONDONTWRITEBYTECODE=1`; bounded wrapper sets task-specific TMPDIR and `CMAKE_BUILD_PARALLEL_LEVEL=2`. |
| Opening audit | `python3 local/research/E19/e19_checkpoint.py`; exact three Git argument arrays/stdout/stderr in `fork-before.json`. |
| Baseline | `python3 local/research/E19/e19_bounded.py checkpoint-regression 1200 -- python3 local/research/E19/e19_baseline.py`; inner suite and every fixture argv/env/cwd in checkpoint JSON receipts. |
| Parser preparation | `python3 local/research/E19/e19_bounded.py parser-prepare 1200 -- python3 local/research/E19/e19_prepare_parser.py`; full clang and FFmpeg argv in `parser-build-commands.json`. |
| Actual-object link | `python3 local/research/E19/e19_bounded.py threshold-link 1200 -- python3 local/research/E19/e19_link_test.py threshold`; complete compiler/linker argv and original Ninja recipe in `threshold-fixture-link.json`. |
| Observer regression | `python3 local/research/E19/e19_bounded.py observer-regression 1200 -- python3 local/research/E19/e19_observer_regression.py`; exact child env/argv in `observer-suite.json`. |
| Stop | Verify PID94254/PPID94253/PGID94254 and the E19 link command; `os.killpg(94254, signal.SIGTERM)`. Full process rows retained; no other process signaled. |
| Final close | `python3 local/research/E19/e19_close.py`; all9,457 generated and1,725 protected hashes rechecked; fork HEAD/ref/remote agree unchanged. |
| Never executed | `e19_threshold.py` and its proposed authored-byte runs; observer binding/closure continuation; any title/probe command; any fork edit, commit, push or game regeneration. |

| Evidence hygiene / handoff | Receipt |
|---|---|
| Standalone data | Full baseline logs/fixture events; both E18 reads; source snapshots; before/final audits; complete commands; authored inputs; failed observer source/binary/logs and macOS crash report. |
| Failed raw retention | `retained.json` maps the complete original observer files to hash-verified canonical gzip copies under `raw/`. Originals preserved. No synthetic source footer appended. |
| Tail qualification | The **report** and archived-file hashes can be complete while the **failed observer capture** lacks a closure footer. The latter remains ineligible; no tail repair by appended counters. |
| Synthetic suite generation | Existing suite recompiler tests created their bounded synthetic test inputs. Game CSV/generated runner sources were not regenerated or altered. |
| Main staging | E19 evidence files only; `.suite-*` scratch remains unstaged, with required failed observer raw preserved canonically. No fork files or generated sources staged. |
| Publication | Local `[E19]` evidence commit with `Orchestrated-By: Muse Code`; no main `ssx3` push. Exact stage and tail receipts follow. |

| Evidence publication budget | Receipt |
|---|---|
| Named force-add | E19 evidence only; initial staged files126; main Git positive allocated growth864256 B of64 MiB cap; at least1 MiB commit reserve |
| Staged set | `evidence-stage.json` lists the exact initial set; final set includes that receipt and `report-tail-receipt.json`. Scratch remains unstaged; no fork files. |
| Publication scope | Local evidence commit only; no main or fork push; automatic Git maintenance disabled for commit. |

| Tail receipt | Value |
|---|---|
| Complete prefix | Lines1–118; 16408 B; SHA256 `b8a497c6e59ac196068d1e674f263ce9ab68cd0a11c232461643e976ec824197` |
| Source-tail gap | Failed observer capture has no real closure footer and reached its payload cap; remains ineligible. Baseline E16 closure receipts remain complete and separate. |
| E19 REPORT TAIL COMPLETE | Stop gate, unanswered questions and all receipts tabled;0 title boots,0 fork edits/commits; evidence publication ends E19. |
