# E15 — MPEG request/delivery probe; shutdown closure remains open

| Scope / disposition | Recorded result |
|---|---|
| Selected stop shape | **Measurement incomplete (iii-shaped): the required boot shutdown footer is absent.** The one authorized boot is spent. No second boot or MPEG implementation was attempted |
| Positive request evidence | Actual wrappers register type 1, then GetPicture enters a typed MPEG wait. Both delivery fixtures fail before a fix; the boot joins the same dynamic MPEG object through Create/register/request/wait. Original ELF establishes the callback ABI and caller context |
| Positive graphics evidence | Guarded UI 3→6 at tick 225 arms ticks 226→227. This run's 1,696-byte copy reaches GS, refreshes D=112 from P=0, and the subsequent actual Present upload matches D after field processing. Content remains the memory-card-check message; no movie/menu claim |
| One next action | Repair the observation exit path and verify its real shutdown behavior, then take a newly authorized guarded closure probe. Exact recipe: [NEXT-BRIEF.md](NEXT-BRIEF.md). MPEG implementation remains parked |
| Fork | Observation-only commit **`67c0a632d44cad8c0e47b4e2c0ee3782b22fd467`**, pushed to remote `fork`, branch `ssx3`; remote SHA verified |
| Scope boundaries | No CSV/map changes, no regeneration, no generated-TU rebuild, no MPEG source changes, no E14 absorb retry, no adb, no main-repository push |

## 1. Contract, checkpoint and admission

Start **2026-09-21 12:39:32 UTC**; eight-hour deadline **20:39:32 UTC**.
[CONTRACT.md](CONTRACT.md), [PROBES.md](PROBES.md) and [ABI.md](ABI.md)
were written before extension/boot. E15 read E13 REPORT/NEXT-BRIEF, E14
REPORT and the E15 prompt. Main `git pull --ff-only` returned up to date at
`f58f787`. E14's verified five-row absorb remains queued.

| Hypothesis / alternative | Observable / stop rule |
|---|---|
| Checkpoint matches E13 | All generated names/bytes, configs, registry, binaries, suite and prior actual-binding cases before extension; mismatch stops |
| Small no-regeneration budget fits | Persist fresh internal/SSD admission before any extension; shortage stops without reclaiming protected or unproven trees |
| Registration exists but request omits delivery | Distinguish API registration, private-map eligibility, scheduler selection, actual invocation, valid-no-input return, AddBs and completion; derive ABI from original ELF |
| Transition-aligned capture catches the copy | Same-run constructor/UI guards arm the capture on old=3/new=6; packet/source/GS/D/Present must join |
| Shutdown closes a quiescent source | Require explicit source counters/truncation flags without needing another guest event; absent footer remains a measurement gap |

| Checkpoint item | Reverification receipt |
|---|---|
| Baseline fork | `83fb4d60904abb016522c477cce704c52118f95f`; protected build `/tmp/p1-link/runtime`; no reclamation |
| Generated mirror | **9,452** names and SHA256s equal E13 `after/generated.json`; repeated final source audit also equal. [checkpoint-identity.json](checkpoint-identity.json), [source-audit.json](source-audit.json) |
| Registry | `98753bfad809d7b54fdbef1c41cc6757724bcbfee9f957f3f89219a39da69e59` |
| Canonical CSV | `0c6085744ab1a2afd60170a18ac261db02472441fa1d343ffd6756026e92d9f4`; prior repaired rows present once; unchanged |
| Canonical TOML | `2f2ae5432b91f873f053045cfa29d9c1d4e3d8e5a941f5693eea720f26daaf1c`; used inputs also unchanged |
| Original runner | 163,437,488 B; `b2099130a366940fb0fa3d273a8bebc7d3ac28618cf0ceac1c743f90939fbbf6` |
| Original test binary | `cbcddc01b860f9d3478492fd92501fb0e536372c0b633aac9be8e4f81f71ec87` |
| Original ELF / ISO | ELF 3,890,784 B, SHA `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc`; ISO 3,005,415,424 B |
| Baseline checks | Suite **452 passed / 0 failed**; leaf 24, consumer 3, predicate 14, query 4 and DROP handler pass; [checkpoint.json](checkpoint.json) and retained complete test logs |
| Fresh extension admission | At 12:53:00 UTC internal free **3,182,592,000 B ≥ 1,879,048,192 B** required; SSD **255,852,544,000 B ≥ 8,858,370,048 B** required. [admission-extension-recheck.json](admission-extension-recheck.json) |

## 2. Fixed budgets and measurement exceptions

| Budget | Declared limit / observed accounting |
|---|---|
| Internal admission | 512 MiB positive artifact-growth reserve + 1 GiB free floor + 256 MiB guard. Reserve split: 128 MiB evidence, 128 MiB handwritten objects/libs, 256 MiB transient runner replacement |
| Internal stop | Growth ≥448 MiB or free ≤1.25 GiB. Largest recorded growth **193,581,056 B** was the failed compiler log; total 512 MiB reserve remained intact, but the log/evidence component bounds did not (below) |
| SSD | 6 GiB owned task allocation, 2 GiB free floor, 256 MiB guard; compiler/link TMPDIR 4 GiB, fixture 512 MiB; temporary work on SSD |
| Build/link | `-j2`, build 1,800 s / link 1,200 s, each with 15 s stop reserve; generated translation units excluded by dry-run and actual build logs |
| Boot | One boot, planned 90 s with 15 s stop reserve, absolute ≤600 s; 1,000,000 syscall lines; 1.5 GiB total logical/allocated capture limit |
| Per-boot files | Boot log 256 MiB, syscalls 96 MiB, function log 1 GiB; E4 12/64 MiB, park 32/128 MiB, frames 32/64 MiB, E7 8/64 MiB logical/allocated; 8 MiB allocation reserve |
| Tap limits | E7 boot 4 MiB + boundary 1 MiB, packets 512 KiB / ≤16 files; ≤4 extra aligned actual upload pairs. Missing source shutdown flags prevent claiming final internal tap counters |
| Final retained work | `final-audit.json`: internal positive growth 11,853,824 B at that checkpoint; SSD owned allocation 173,015,040 B, chiefly the canonical actual-binding executable. No protected-tree reclaim |

| Measurement/build issue | Exact receipt / disposition |
|---|---|
| Initial compiler-log cap **overrun** | A newly created `Kernel/._EeScheduler.cpp` entered CMake's recursive source glob. Polling noticed 45,969,536 B at 13.478 s, sent SIGTERM; closed raw was **192,334,611 B**, exceeding the 16 MiB log cap by **175,557,395 B** and also the 128 MiB evidence component. This is not reported as an all-caps pass |
| Repair before continuing | Original binaries unchanged at failure. Proven E15-owned sidecar removed using birth time, AppleDouble magic and hash (`owned-metadata-receipt.json`). Monitor changed to a hard bounded stdout pipe under the same limits; no budget expansion or emulator fix. Full failed log retained losslessly as `build.log.gz`, SHA of decompressed raw `3554e6c…f5`, round-trip verified |
| Fixture setup errors | First fixture compile had a macro-parenthesization error; first run used synthetic PCs outside the registry's dense range. Test-only repairs use verified empty entries `0x100040/50/60/70`; neither attempt reached MPEG and neither was counted as fail-before evidence |
| ExFAT suite data | One intermediate suite run was 451/452: GetDir expected 3 entries, got 4. Same binary passes 452/0 with bounded APFS test data; metadata is the environment inference, not an MC fix. Test scratch cap 32 MiB charged to the existing evidence reserve, sampled peak 4 KiB, cleaned after. Final and preclaim suites use this recorded environment |
| Broad SSD sampler omission | During boot the `e15-*` glob omitted shared `ps2_log.txt`; the boot-specific allocated/logical counters included it throughout. Corrected binding sample is **385,875,968 B**. Final closed capture accounting is complete; original samples are preserved, not rewritten |
| Retention monitor race | Completed retention removed a directory between the monitor's glob/stat, causing FileNotFoundError. Manifest had completed; all 29 source hashes were independently rechecked, all original paths absent, no pending journal. Only the proven E15 monitor temporary was cleaned. No invented child return code; `retention-audit.json`. Future monitor tolerates vanished paths |
| Existing fork git warning | Preexisting AppleDouble pack-index warning remained; named git operations returned 0 and remote SHA matched. No unrelated metadata/tree cleanup |

## 3. Read-only taps and actual-wrapper fail-before

The fork commit names exactly five files. [observation-tracked.diff](observation-tracked.diff)
and `sources/*.gz` pin their bytes; MPEG.cpp/MPEG.h and prior residual source
receipts remain unchanged. All new guest pointers are const reads; diagnostic
atomics, shadow registrations, counters and files do not alter guest state.
Taps require E15/E7 environment gates. No generated sources were staged.

| Named fork file | Observation change / required receipt |
|---|---|
| `ps2xRuntime/include/ps2_e15.h` | Original call args/RA/SP, IDs, actual returns versus C++ unwinds; shadow registration from successful observed API returns; selection/invocation/source/input/lifetime counters; footer |
| `ps2xRuntime/src/lib/ps2_runtime.cpp` | Scoped traces at real nested dispatch; retain actual Present uploads in the armed interval; destructor calls diagnostic closure (incorrect boot exit placement, §7) |
| `ps2xRuntime/src/lib/Kernel/EeScheduler.cpp` | Scheduler target/queue/invoke and typed MPEG wait/completion observations; no scheduling decision changed |
| `ps2xRuntime/include/ps2_e7.h` | Guarded UI 3→6 sets diagnostic arm/freeze ticks; bounded packet retention; direct shutdown counters |
| `ps2xRuntime/include/ps2_e4.h` | Use the dynamic E15 ticks when enabled; prior static capture behavior otherwise retained |

| Final artifact | SHA256 / validation |
|---|---|
| Runner, 163,456,240 B | `7544d4ebde5d501e450f473c0d81073cc312d48335fa03dfbb7c76eafaf2f599` |
| Suite, 5,643,528 B | `8ba90048da7804a3dd278f172efbeb92d968ca89fd4ac9209b243e3d15c5a2eb`; **452/0**, again **452/0** immediately before boot |
| Actual-binding fixture, 165,103,200 B | `b0aefc016c69a0dd693093828bda828a1c7f9eaf36c17a38bb757763642321f2`; single executable retained at `$P1/e15-binding-tests/entry/binding-test` |
| Prior regressions relinked to current objects | Leaf **24**, consumer **3**, predicate **14**, query **4**, DROP all pass (`final-prior-binding.txt`) |

`e15_binding_test.cpp` links the actual runner objects and registry, including
Create `0x4027b8`, AddCallback `0x402c08`, GetPicture `0x402a10`, AddBs
`0x4029d0` and the existing guest callback/helper/source entries. The synthetic
callback is registered through actual AddCallback. Actual GetPicture runs
through runtime dispatch and the scheduler. **No callback is called manually.**

| Final case | Registration / request | Selection / invocation / callback return | Delivery / state |
|---|---|---|---|
| `no-input` | Type 1, callback `0x100070`, userdata `0x15f000`, handle 1; real GetPicture | 0 selected, 0 invoked, 0 callbacks, 0 valid-no-input returns | Expected delivery predicate false, rc **1 FAIL-BEFORE**; not an observed no-input callback outcome |
| `input` | Same real path; callback would re-enter actual AddBs with 16 sequence-end bytes | 0 / 0 / 0 | AddBs calls 0, delivered bytes 0, resumes 0; rc **1 FAIL-BEFORE** |
| Both | Supplied RA `0x100050`, SP `0x1e00000` | Main parks at supplied continuation with waitReason 6 / Waiting | Relevant callee-saved **128-bit** registers and full **32 MiB RAM** unchanged on the undelivered request |
| Fixture closure | Real destructor reached by this fixture | calls 3 = returned 2 + unwound 1; pending 0; registrations 1; no truncation flags | Both actual source footers present. This does **not** validate runner `main` shutdown |

`expectedDelivery=0` in the fixture tail is the evaluated predicate, not a
zero-delivery expectation. Both cases require callback delivery to pass.
The input case tests AddBs reentry/delivery only; sequence-end bytes alone
do not establish a decoded frame or GetPicture completion. Future owner-thread,
completion, no-input retry and lifetime tests remain required before a fix.

## 4. Original ELF ABI and request edge

| Edge | Forcing raw-word receipt / implication |
|---|---|
| Register type | `0x402c08..2c`: load inner from MPEG+0x40, index type<<3, store function at +0x0c and userdata at +0x10 |
| Select / invoke | `0x402c4c..68`: callback-data word 0 indexes the slot; `jalr` at `0x402c64`, delay slot loads a2 userdata; a0 MPEG and a1 callback-data unchanged |
| Type-1 data / return | `0x402c80..a8`: initializes only first stack word to 1; selector call; forces v0=1, discarding callback return. No assumed stream-event layout and no EOF inference from callback v0=0 |
| Request trigger | GetPicture `0x402a44→0x402e10→0x407520→0x4072e8`; busy polling `(MMIO[0x10002010]&0x80004000)==0x80000000`, threshold `0x1389`, invokes `0x402c80` at `0x407344` |
| Execution ownership | Original `jalr` is within the GetPicture caller's thread/stack. A later design cannot assume the existing stream RPC-callback queue has equivalent ownership |
| Guest callback | `0x3b0b10` reorders `(mpeg,cbdata,userdata)` for helper `(userdata,mpeg,cbdata)` at `0x3b0b40`, then returns 1 |
| Guest source | Helper obtains source through `0x3b06b0` using userdata+0x28; descriptor+4/+8 and userdata+0x78/+0x7c supply the AddBs path |
| No-source branch | `0x3b0bdc..0x3b0c00` builds four little-endian `00 00 01 b7` words, count 16; common call `0x3b0c2c→0x4029d0` still occurs |
| Current wrapper implementation | MPEG.cpp:1939 records `stream=false`; its only callback-map selecting reader (1141–1157) filters `callback.stream`. GetPicture:2318–2345 reaches waitExternal without selecting non-stream callbacks |

Full ranges, raw words and verified OUT joins are in `mpeg-*-dis.txt`,
`guest-callback-dis.txt` and [ABI.md](ABI.md). Other API differences
(AddCallback's old-function versus allocated-handle return; AddBs's original
1 versus copied-byte return) are parked, not repaired or used to substitute
for the delivery evidence.

## 5. Single guarded boot and dynamic joins

| Preclaim / lifecycle | Receipt |
|---|---|
| Fresh T13 shape | Lease absent, `pgrep -x ps2EntryRunner` rc1, runner/test SHA match, ELF/ISO sizes, SSD/internal `df`, trace-align selftest ALL PASS, waits tails, three caps and suite 452/0 in `e15a-preflight.json` |
| Admission | Internal 11,548,696,576 B free; SSD 255,686,868,992 B free at preclaim. Increased external free space did not authorize or trigger E14 retry |
| Claim / start | `2026-09-21T13:32:26.720597Z` / `.725264Z`; PID 97456; foreground boot, REPORT_ALL=1, E15/E7/E4/park/watch taps |
| First binding cap | Wall reserve at **75.153 s**, SIGTERM `13:33:41.994451Z`; no SIGKILL |
| Exit / release | rc0 at `13:33:42.112285Z`; lease removed `13:33:42.117085Z`, about **4.8 ms** later; total **75.390724 s** |
| Closed caps | **150,866,023 B logical / 204,472,320 B allocated**; **54,793** syscall lines; every boot-specific bound satisfied (`e15a-closed-caps.json`) |
| Analysis | Lease-free; pgrep rc1. Aligned E4 span complete observed at elapsed 9.270 s. The source shutdown gate is independently missing (§7) |

| Same-run object / state | Exact join |
|---|---|
| Graphics S | Singleton factory write `0x22697c→[0x4a289c]=0x61ba60`; no teardown-null in recorded events; counter writes contiguous 1..206 |
| Steady S fields | `(M,G,A,B,P,D)=(1,0,0,112,0,112)` after initial setup; all interpreted from guarded same-run S |
| MC / UI | Constructor `0x2c3fc4`, `[MC]=0x486f78`, MC=`0xb851a0`; UI pointer store `0x23d5c8` proves UI=`0xb84a50`, `[UI+0x434]=MC` |
| Prior entries | **375** exact query call/returns, **8** predicate pairs, **142** leaf pairs; SP/arguments/truth joins checked; 781 card call/exit pairs, no unmatched/unclosed observed pairs |
| UI advance | +0x130: 2→3 tick223, **3→6 tick225**, 6→29 tick229. Six +0x43c route writes are 0→0; no observed 8→0 clear |
| Lifetime guard limit | MC vtable destruction/reuse at tick248; later writes at the old address are retained as raw stores, not interpreted as a live card object |
| MPEG creation | tick249 seq6402/6403: a0=`0x587b30`, work=`0x11e4ec0`, size=`0xfd76c`; v0=`0x11e4fd8`, RA=`0x3b0f54` |
| Registration | seq6404/6405: same a0, type **1**, function **`0x3b0b10`**, userdata **`0x587b00`**, v0 handle **1**, RA=`0x3b0f6c` |
| Picture request | seq6407: same MPEG, image=`0x1104d80`, source=`0x3b1020`, supplied RA=`0x3b1028`, SP=`0x1fffd60`, thread1 |
| Wait | seq6409: type1/token=`0x587b30`, waitReason6, PC/RA=`0x3b1028`; raw boot line **10454** logs `ended=0 failed=0 sawInput=0`. Pinned branch implies empty decoded queue and no current EOF |
| Request exit | seq6410 is a **C++ unwind**, not a successful guest GetPicture return; its v0=`0x3800` is not a decoded-frame result |
| Selection / producer | Recorded selection, callback dispatch, source helper, AddBs and completion events all zero. Full park hot-PC census has no `0x3b0b10/0x3b0b40/0x4029d0`; registration/target bindings exist |
| Park / independent logs | T1 waits MPEG at `0x3b1028`; T2/3/4/5/6 wait semas 26/30/31/32/36. Function trace: **3,628,676** lines, **1,322** distinct labels, zero pairing mismatches, empty final stack |
| Queued map rows remain | 216 missing-entry records parsed, no damaged markers; includes E14's five named rows. No row was absorbed or promoted as this request's cause |

The dynamic counts are **observed-record counts**, qualified by §7. Zero
callback dispatch is not a valid-no-input callback result. No callback entry
means the userdata source fields, actual bytes, decode, delivery completion,
removal and post-request lifetime were not exercised. No CD/SIF/storage/input
failure follows merely from this screen or nearby I/O.

## 6. Transition-aligned packet/source/display/Present

| Boundary | This-run receipt |
|---|---|
| Trigger | seq5521, tick225, PC=`0x23d3a0`, UI/MC guards true, old3/new6; arm226/freeze227 |
| Capture coverage | E4 **288** contiguous entries, all tick226; census **155** draws = **138** P=0 + **17** D=112 strips; explicit arm/freeze/span-complete |
| Primary packet | tick226 seq5548, source=`0x4ffcc0`, **1,696 B**, FNV64=`0x767aae0fde3c567f`, SHA256=`79f3582fce45dc36a25c454003206a43bbfd001c340a92459a8726fbd0512e31` |
| GS consumption | Same tick/length/hash, seq5550; packet FRAME selects FBP112/FBW8/PSM24, TEX0 source TBP0/TBW8/PSM32; 17 textured strips. 206 recorded production-copy submissions each join one GS entry |
| Source → D | P RGB nonblack **12,563**; D **12,358**. Decoded packet geometry predicts D(x,y)=P(x+1,y+1), clipped edges black; **0** differing RGB pixels over 512×448 |
| Source stability | Whole 4 MiB arm/freeze VRAM files identical; source changed pixels **0**. This is a same-content refresh, not a newly decoded movie frame |
| D content identity | RGBA SHA256=`4a7d98177597f60731c8b0ab5ce83f9c412f2d5f871c1f196526ef599b033243`; retained D PNG visually inspected: memory-card-check message |
| Present mode | `DISPFB1=0x9070`, `SMODE2=1`, `PMODE=0xff21`, display/source FBP112, 512×448; no preferred/fallback substitute |
| Upload before primary copy | tick226 upload79, event5539 precedes copy5550. Exact even-field pixel match, but not claimed as that copy's later presentation |
| Upload after primary copy | tick227 upload80, event5622 **after** primary GS5550 and before next copy5631/5633; exact odd-field D match, FNV32=`0xf818f78d`, PNG SHA256=`ba5fbce889b98081f286c16b2af92b1ffef2ee298745641cc8358508a7592576` |
| Next packet | tick227 packet independently retained with same SHA; outside E4's [226,227) VRAM interval and not substituted for the primary content proof |

[e15a-graphics.json](e15a-graphics.json) records the complete packet fields,
strips, event order, pixel comparisons and actual upload metadata. The
positive graphics chain is intact; the source shutdown counters remain absent.
No changed image, menu, interaction or MPEG delivery is claimed.

## 7. Shutdown failure, challenges and next action

| Premise / requirement | Observation / consequence |
|---|---|
| “Destructor closure proves runner shutdown” | **Contradicted.** Unchanged `ps2xRuntime/src/main.cpp:252` calls `runtime.run()`, then line259 calls `std::_Exit(0)`, bypassing the automatic PS2Runtime destructor. The new footer hook at runtime.cpp:698–699 is unreachable on this normal exit path |
| Required source footer | Boot event file ends with seq6410, a complete newline, but contains neither `# E15 CLOSURE` nor `# E7 SHUTDOWN`. Strict miner fails; [exit-closure-audit.json](exit-closure-audit.json) pins source SHA and actual tail |
| What remains checkable | 6,410 contiguous event rows, five observed MPEG calls paired with four returns/one unwind, E4 span, whole function trace balance, rc0/process absence/lease release. These do not supply final source counters or truncation flags |
| Fixture versus boot | Both wrapper fixtures have real footer counters because their runtime objects leave scope normally. That fixture coverage missed main's `_Exit` path |
| “Copy observed late at 599–603” | E15 avoids that missed phase: guarded tick225 trigger captures 226–227, before last production copy248 |
| “Memory-card message names storage failure” | UI reaches29 and constructs MPEG; the joined first picture request has no supplied input. A storage dependency has not been demonstrated |
| “Mirror the stream callback queue” | Original ELF requires callback execution within GetPicture's caller context. Existing stream queue semantics must be audited before any future implementation; matching function arguments alone is insufficient |

The strict parser is still strict by default. Partial-analysis callers
explicitly opt into absent-footer analysis and emit `source_shutdown_complete=false`,
`closure=null`, `shutdown=null`. **No runtime footer was synthesized.**
The initial failing miner logs remain retained alongside partial/replay logs.

| Cross-lane comparison | Scope and constraint |
|---|---|
| I19 convergence | Retained I19 report SHA `79e7d3a1592e486211872f32b1b5d7ad2608a730e1340e08b38c8ba798215fa5` names the same non-stream callback selection gap and worker semaphores; these are I19's device receipts, not an E15 device run |
| Configuration difference | I19 device decoder is FFmpeg-OFF; this host cache says FFmpeg-ON and pins its libraries. That later device decode edge is not repaired or projected onto this host's undelivered request |
| Additional E15 contract | Original ELF closes `(mpeg,cbdata,userdata)`, first type word only, ignored callback return, IPU polling trigger, and caller-thread ownership |
| Parked later design | Generic non-stream request delivery in MPEG.cpp, outside its mutex for AddBs reentry, preserving ordering/ownership and lifetime; regression against actual wrappers plus no-input/completion/teardown cases. This remains a proposal, not E15 work or the immediate next action |

**One next action:** repair the diagnostic closure at the actual handwritten
`PS2Runtime::run()` exit after the game thread joins, retain an idempotent
destructor fallback, prove that path without a title boot, then take a newly
authorized guarded closure probe. [NEXT-BRIEF.md](NEXT-BRIEF.md) gives the
exact scope and stops. No MPEG implementation follows within E15.

## 8. Retention, commands and final handoff

| Artifact / hygiene | Receipt |
|---|---|
| Canonical boot captures | 29 original files, 150,759,527 logical content bytes (excludes metadata), **25 unique canonical files / 3,602,123 B**; compressed raw logs/VRAM, deduplicated equal packet/image content; every removed raw hash round-tripped. [e15a-retained.json](e15a-retained.json), [retention-audit.json](retention-audit.json) |
| Replay | `e15_io.py` resolves original paths to canonical retained content; join/card/progression miners rerun after raw removal. Explicit closure gap persists |
| Whitespace check | Raw config/log/diff receipts preserve their exact whitespace; full evidence diff-check flags those bytes. Authored Markdown/Python/C++/header files checked separately |
| Final source identity | All 9,452 generated names/bytes and all configuration inputs unchanged; source audit pins unchanged MPEG and the five observation files |
| Fork staging | Only five named observation files committed. Preexisting generated `register_functions.cpp` dirt and untracked `ps2_log.txt` untouched; no generated runner sources staged |
| Fork remote | `git push fork HEAD:ssx3` and `git ls-remote fork refs/heads/ssx3` agree on `67c0a632d44cad8c0e47b4e2c0ee3782b22fd467`; full commands/receipts in `fork-commit.json` |
| Final process ownership | One boot only; lease absent, pgrep rc1; owned tool temporaries and duplicate SSD fixture event copies cleaned. `/tmp/p1-link` and DerivedData protected |
| Evidence | Standalone `local/research/E15/`, forced named-directory staging, `[E15]` commit with `Orchestrated-By: Muse Code`; no main push |

Exact command records, environment and argv are in [COMMANDS.md](COMMANDS.md),
`*-bounded-start.json`, `e15a-preflight.json`, `e15a-result.json`,
`fork-commit.json` and the executable miner/fixture scripts. All SSD work
exports `COPYFILE_DISABLE=1`. Static decoding uses the retained EF-derived
R5900 SQ handling; no ELF alteration or generation.

**E15 REPORT TAIL COMPLETE — one guarded boot; MPEG request/delivery evidence
and aligned copy/Present receipts retained; required source shutdown footer
absent; measurement-only next action; no MPEG fix, no regen, no absorb retry.**
