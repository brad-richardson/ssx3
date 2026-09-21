# E16 — checkpoint rebuild and run-exit observation closure

## Chunk 1 — contract and rebuilt checkpoint

| Contract item | Bound / observable / stop |
|---|---|
| Scope | E15 NEXT-BRIEF §1–§3: rebuild lost checkpoint; repair observation closure; ≤1 separately capped, leased title probe. No MPEG implementation, CSV/map change, guest regeneration, main edit, or E14 absorb |
| Start / deadline | Admission clock 2026-09-21 16:17:13 UTC; deadline 2026-09-22 00:17:13 UTC |
| Hypothesis | Existing E15 closure plus E7 shutdown at the end of `PS2Runtime::run()` emits final source counters before unchanged main calls `_Exit` |
| Forcing observable | Actual-linked non-title fixture reaches `run()`, joins its synthetic guest thread, executes the last shutdown producer, checks the real file before destruction, and calls `_Exit`; same fixture fails before and passes after repair |
| Alternative / stop | Source/config identity mismatch, unfitting storage, occupied lease, first binding cap, missing receipt, or first different demonstrated dependency is tabled; no second title boot |
| Regression requirements | Suite452; leaf24/consumer3/predicate14/query4/DROP; both MPEG delivery fixtures remain FAIL-BEFORE; guest RAM/register/scheduler state unchanged by closure |
| Probe requirements | Dynamic object/lifetime and MPEG joins; separate callback absence/delivery fields; guarded UI3→6 copy/GS/VRAM/later Present; actual final source counters, contiguous count match, pending0, no truncation |
| Detailed contract | [CONTRACT.md](CONTRACT.md), written before configure/build/link/repair/probe |

| Storage / execution budget | Declared bound | Fresh admission / accounting |
|---|---|---|
| Internal | 4 GiB build + 512 MiB evidence/test scratch + 512 MiB repair/link reserve; 2 GiB floor + 512 MiB guard; required **8,053,063,680 B** | **16,301,449,216 B free**, before build; stop at 4.5 GiB allocation or free≤2.5 GiB |
| SSD | 12 GiB total: temp8 GiB, fixtures1 GiB, probe1.5 GiB, reserve1.5 GiB; 2 GiB floor + 512 MiB guard; required **15,569,256,448 B** | **252,475,080,704 B free**; stop at 11.5 GiB allocated or free≤2.5 GiB |
| Allocated accounting | `st_blocks*512`, including directories/sidecars on ExFAT; logical bytes separately | Owned E16 paths plus shared boot `ps2_log.txt`; explicit fork allocation inventory; vanished paths tolerated; no reclamation |
| Build / link | `-j2`; configure1800 s, rebuild7200 s, repair1800 s, fixture link1200 s; 15 s termination reserve | Hard stdout pipe16 MiB with1 MiB reserve; compiler/link `TMPDIR` on SSD; `COPYFILE_DISABLE=1` |
| Suite environment | APFS test data≤32 MiB within evidence reserve | Fork cwd required for relative source-header test; scratch monitored and retained |
| Probe | One90 s allowance; SIGTERM at75 s; absolute≤600 s; 1,000,000 syscall lines | Fresh T13 preclaims; atomic shared `/tmp/ssx3-p-lane-lease`; occupied→stop without waiting |
| Probe bytes | Aggregate1.5 GiB logical/allocated; boot256 MiB; syscalls96 MiB; function trace1 GiB; E4 12/64 MiB, park32/128 MiB, frames32/64 MiB, E7 8/64 MiB | 8 MiB allocation reserve; source boot4 MiB/boundary1 MiB/packet512 KiB; ≤16 packet files, ≤4 extra aligned Present pairs |

| Checkpoint receipt | Recorded result |
|---|---|
| Remote, tracking ref, HEAD | All **`67c0a632d44cad8c0e47b4e2c0ee3782b22fd467`** before building; [before-fork.json](before-fork.json) |
| Lost build | `/tmp/p1-link/runtime` absent at audit; reconstructed in that path; no protected-tree deletion |
| Generated audit | **9,452 names and hashes match E15**, no guest regeneration; [before-generated.json](before-generated.json), [before-checkpoint.json](before-checkpoint.json) |
| Registry | `98753bfad809d7b54fdbef1c41cc6757724bcbfee9f957f3f89219a39da69e59`; inherited generated registry dirt remains outside staging |
| Canonical CSV / TOML | `0c6085744ab1a2afd60170a18ac261db02472441fa1d343ffd6756026e92d9f4` / `2f2ae5432b91f873f053045cfa29d9c1d4e3d8e5a941f5693eea720f26daaf1c`; used inputs also unchanged |
| MPEG.cpp / MPEG.h | `949894dcebfa0c3a632381a80944a7dfe2db57223971adce7207ccaa881989b8` / `d414d295f3bf9756ae5d91a7554fc1a36ac2a00ebab9b95d2dc95da45b135b25`; unchanged |
| Main | `9a7ea63e8afe61581a8fb13622c13a1cecc6d0a1fa28f3e3e453e6ab0a1d7f94`; unchanged `_Exit` path |
| Configure / rebuild | rc0 / rc0; **123.91 s / 531.26 s**; [configure-bounded-result.json](configure-bounded-result.json), [rebuild-bounded-result.json](rebuild-bounded-result.json) |
| Rebuilt runner | **163,456,240 B; `7544d4ebde5d501e450f473c0d81073cc312d48335fa03dfbb7c76eafaf2f599`**, byte-identical to E15 |
| Rebuilt suite | **5,643,528 B; `8ba90048da7804a3dd278f172efbeb92d968ca89fd4ac9209b243e3d15c5a2eb`**, byte-identical to E15; **452/452** in [rebuilt-cwd-suite.txt](rebuilt-cwd-suite.txt) |
| Generated object checkpoint | **296 unity objects** pinned before repair; [rebuilt-binaries-objects.json](rebuilt-binaries-objects.json) |
| Surviving SSD fixture | Reused executable at `P1/e15-binding-tests/entry/binding-test`; **165,103,200 B; `b0aefc016c69a0dd693093828bda828a1c7f9eaf36c17a38bb757763642321f2`** |
| Reused fixture regressions | Leaf24, consumer3, predicate14, query4, DROP pass; input/no-input both rc1 FAIL-BEFORE; saved128 and RAM32 MiB unchanged; [ssd-reuse-validation.json](ssd-reuse-validation.json) |

| Setup / measurement exception | Exact receipt / disposition |
|---|---|
| Initial suite cwd | 451/452: VU0 enum test could not read relative `ps2xRecomp/include/ps2recomp/instructions.h` from APFS scratch cwd. Same binary passed452/452 after using fork cwd with APFS `TMPDIR`, matching E15. [suite-cwd-gap.json](suite-cwd-gap.json); failed log retained |
| Initial metadata audit | A conservative audit flagged nine preexisting AppleDouble source/header sidecars. CMake uses explicit lists for these locations; runner/Kernel globs contain none. Final compile database has **zero sidecar inputs**; no metadata deletion |
| Top-level SSD sidecars | Initial sampler omitted two top-level `._e16-*` metadata files; fixed before fixture links and probe. Their2 MiB allocation is included in later complete samples; original samples retained. Shared boot function trace was included from the start |
| Git pack warning | Preexisting non-monotonic AppleDouble pack-index warning; named git commands return0 and remote SHA matches; unrelated metadata retained |
| Host concurrency | Ninja explicitly `-j2`; unchanged ThinLTO link flags. Native linker internal workers observed at611.2% CPU, RSS4,150,224 KiB; no increase to Ninja build jobs |

**E16 REPORT CHUNK 1 COMPLETE — checkpoint rebuilt byte-for-byte; repair/probe receipts follow.**

## Chunk 2 — observation repair and forcing fixture

| Repair / provenance | Receipt |
|---|---|
| Named source change | Six added lines in `ps2xRuntime/src/lib/ps2_runtime.cpp`: existing `ps2_e15::closure` then `ps2_e7::shutdown`, after `gameThread.join()`, debug UI shutdown, texture/window cleanup, and the final run log; [observation-repair.diff](observation-repair.diff) |
| Destructor fallback | Existing pair retained. The first shutdown closes the shared sink; later closure/shutdown calls leave it unchanged |
| Producer ordering | [producer-callsite-audit.txt](producer-callsite-audit.txt); actual fixture's final diagnostic producer runs in the real shutdown callback, after the real join; the run-exit footer follows it |
| Source class / commit | **OBSERVATION**, local fork commit **`784f2b3e668ffa7a238936be415dc2e03d6c283c`**, exactly one named file; **no push**; [fork-commit.json](fork-commit.json) |
| Rebuild scope | Actual log contains one handwritten runtime compile, archive, and runner/suite links; **296 generated/main unity object hashes unchanged**; [repaired-binaries-objects.json](repaired-binaries-objects.json) |
| Dry-run limitation | Ninja's dry run showed its CMake glob-verification prelude. Actual build log and all object hashes supply the completed no-generated-rebuild receipt |
| Repaired runner | **163,456,352 B**, SHA256 **`d9eb59012898545b84981a810c0b20ff78a6e4f60664774f660cecc2cadeed8d`** |
| Repaired suite | **452/452**; same E15 suite bytes/hash. APFS scratch sampled peak **3,162,112 B**, cap32 MiB; [repaired-suite.json](repaired-suite.json) |
| Actual-linked fixture | Current runner objects and registry; separate `_e16_binding_main`; no title ELF loaded. Before/after fixture source files and **compiled test object are identical**, SHA256 `d1851c8f5945b3c3afd096c6c9a25002bf6a3ec8e64c44060c71dbb12da26186`; [fixture-object-identity.json](fixture-object-identity.json) |
| Repaired fixture binary | SSD `P1/e16-fixtures/after/binding-test`, **165,122,752 B**, SHA256 `2089be52f52e1a6001cae902f78cc177b32669a46d8f96b70ff67d95bc45c94f` |

| Non-title case | Before / after receipt | Source counters / state |
|---|---|---|
| Quiescent `run()` → `_Exit` | **rc1 FAIL-BEFORE → rc0 PASS**; footer inspected before destruction; [before](closure-before-quiescent.txt), [after](closure-after-quiescent.txt) | Last event tick17; five contiguous events; after: calls2=returned2+unwound0, pending0, registrations1, all truncation flags0; bootBytes815 exactly matches rows |
| Real source footer | [closure-after-quiescent-events.txt](closure-after-quiescent-events.txt) | Actual `# E15 CLOSURE` and `# E7 SHUTDOWN`; neither appended nor synthesized by the harness |
| `run()` then destructor | rc0 | Event file byte-identical before/after destructor; exactly one closure/shutdown pair |
| Window already complete | rc0 | Real COMPLETE at tick604, then final closure/shutdown; four events, calls2/returned2, pending0, windowComplete1, truncation0 |
| Disabled / unopened | rc0 / rc0 | Both return safely; no event file or fabricated footer |
| Caller error / fallback | rc0; intentional caller error after actual Create, `runCalled=0` | Destructor produces real footers: calls1/returned1, pending0, two events, truncation0 |
| State preservation | Every actual `run()` case | Full32 MiB RAM, runtime CPU context, all captured thread contexts, and scheduler snapshot unchanged from final producer to returned `run()` |
| Prior actual bindings on repaired objects | Leaf24 / consumer3 / predicate14 / query4 / DROP pass | [current-binding-validation.json](current-binding-validation.json) |
| MPEG no-input / input | Both **rc1 FAIL-BEFORE**, unchanged expectation | Selections0, invocations0, callbacks0; AddBs/input/completion0; typed MPEG wait6; saved128 and RAM32 MiB unchanged; callback absence remains separate from a valid-no-input callback outcome |
| Scope counters | Six non-title `run()` executions total, including fail-before; one additional destructor-error case | **Zero title boots for fixtures**; no manual callback invocation; no main/MPEG/header/generated-source change |

**E16 REPORT CHUNK 2 COMPLETE — actual run-exit fail-before/pass-after proven; current regressions retained.**

## Chunk 3 — the single guarded closure probe

| Fresh T13 / execution receipt | Observed value |
|---|---|
| Preclaims | Lease absent; `pgrep -x ps2EntryRunner` rc1 twice; repaired runner/suite hashes rechecked; fork HEAD/status pinned; ISO size and both ELF hashes checked; wait-log tails read; trace-align selftest ALL PASS; fresh suite **452/452**; [e16a-preflight.json](e16a-preflight.json) |
| Fresh free space | Internal **14,330,757,120 B**, SSD **242,154,995,712 B**, before claim; allocation admission fits the original budgets |
| Observation environment | `PS2X_DIAG_REPORT_ALL=1`, E15 trace/alignment, E7, E4, parked-thread snapshot, syscall-PC trace, actual Present dumps; exact argv/cwd/environment in [e16a-config.json](e16a-config.json) |
| Lease / boot | Atomic shared lease claimed **17:01:30.728841 UTC**; boot **17:01:30.734108**, PID37652; [boot-attempt.json](boot-attempt.json) prevents a second E16 title launch |
| Bound | Aligned span complete at **9.392522459 s**; first binding cap was wall at **75.404 s**; SIGTERM17:02:46.294326; rc0 at17:02:46.399152; total **75.6700455 s**; no SIGKILL |
| Release | **17:02:46.454561 UTC**, **55.409 ms** after process end; shared function log renamed to the owned capture before release; lease absent and runner absent afterward; [e16a-result.json](e16a-result.json) |
| Closed byte / progress bounds | **150,954,908 B logical / 216,006,656 B allocated**, including metadata; **54,787 syscall lines**; every per-path and aggregate bound fits; [e16a-closed-caps.json](e16a-closed-caps.json) |
| Boot count | **1/1 title boots used**; no further E16 boot allowance |

| Dynamic object / lifetime join | Receipt | Interpretation boundary |
|---|---|---|
| S singleton | seq1 tick41: store at `0x4a289c`, factoryPC`0x22697c`, observed S=`0x61ba60` | S derived from this run's singleton event; counter1…206 continuous, steady `(M,G,A,B,P,D)=(1,0,0,112,0,112)` |
| MC construction | seq855 tick80, constructorPC`0x2c3fc4`, observed MC=`0xb851a0`, vtable`0x486f78` | Start of the interpreted MC lifetime |
| UI→MC pointer | seq868 tick80, storePC`0x23d5c8`, observed UI=`0xb84a50`; UI+`0x434`=MC, guard1 | UI derived from the pointer store and joined to the constructor |
| Guarded actual calls | Query **375 call/return pairs**, predicate8, leaf142; **1,050 guarded events** | Every selected event is within the constructed lifetime and has the expected vtable; no unmatched or unclosed card calls |
| UI state sequence | UI+`0x130`: 2→3 at seq5398/tick223; 3→6 at seq5522/tick225; 6→29 at seq5801/tick229 | Guarded alignment event seq5521 precedes the actual3→6 store; a UI route receipt does not establish MPEG completion |
| MC lifetime end | seq6395 tick248, PC`0x2c402c`, vtable `0x486f78`→`0x4871e8` | The end store plus three later stores remain raw; no object-field interpretation after the end |
| Canonical joins | [e16a-card.json](e16a-card.json), [e16a-lifetime.json](e16a-lifetime.json), [e16a-observation-closure.json](e16a-observation-closure.json) | Constructor, pointer, lifetime, and guard receipts retained independently of the watch-address configuration |

| MPEG edge / field | Actual receipt | Limit / missing edge |
|---|---|---|
| Dynamic identity | Create seq6402→6403/tick249, a0=`0x587b30`, work=`0x11e4ec0`, size=`0xfd76c`, v0=`0x11e4fd8`, RA=`0x3b0f54` | MPEG identity comes from this run's Create; no E15 numeric MPEG address is used as the join key |
| Registration | seq6404→6405, same object, type1, callback`0x3b0b10`, userdata`0x587b00`, returned handle1, RA`0x3b0f6c` | Actual API argument/return pair; shadow records type/function/userdata/handle |
| Picture request | seq6407, same object, image`0x1104d80`, source`0x3b1020`, RA`0x3b1028`, SP`0x1fffd60`, thread1 | seq6408 joins the live request to the observed registration |
| Request state / wait | Boot line10461: `ended=0 failed=0 sawInput=0`; seq6409 type1/token=`0x587b30`, reason6/Mpeg, PC=RA`0x3b1028` | Empty queue is implied by the pinned wait branch; private state fields come from the existing runtime log |
| Eligibility, source inference | Unchanged `MPEG.cpp` stores AddCallback with `stream=false`; its map-selecting reader requires `stream=true` | Private-map selection is not directly tapped; this is a source-backed eligibility inference |
| Scheduler selections | **0** events and source footer `selections=0` | Separate from the private-map inference |
| Actual invocation / return | **0** dispatches; source footer `invocations=0`; callback returns0 | Callback delivery was not observed |
| Valid no-input callback | **0 observed returns** | Absence of a callback is not a demonstrated no-input callback outcome |
| AddBs / input / completion | **0 / 0 / 0** | No actual source-read, feed, decode, or completion dependency was exercised |
| Request exit | seq6410, C++ unwind, v0`0x3800`; closure calls5=returned4+unwound1 | Unwind is not a frame completion; the main thread remains parked on Mpeg |
| Function owner alias | Exact setup dispatch seq6399 targets`0x3b0c58` from`0x3b0520`, returns seq6406. One `sub_003B0B40` owner label surrounds it | Owner logging precedes the entry-PC switch; both addresses map to that owner. Exact callback`0x3b0b10`, helper`0x3b0b40`, and AddBs dispatches are zero; [function-owner-alias-audit.json](function-owner-alias-audit.json) |
| Reproducing artifacts | [e16a-mpeg.json](e16a-mpeg.json), [function-owner-alias-source.json](function-owner-alias-source.json), [function-owner-alias-context.json](function-owner-alias-context.json) | Numbered source excerpts, exact target events, and complete balanced function trace retained |

| Guarded graphics edge | Receipt | Temporal / pixel check |
|---|---|---|
| UI3→6 alignment | seq5521 tick225, UI/MC/lifetime guard1; arm226, freeze227 | E4 source interval is **[226,227)** |
| E4 history | 288 entries, 155 draws:138 producer and17 display | Both producer and display bytes retained |
| Primary packet→GS | tick226 packet seq5548→GS seq5550, **1,696 B**, FNV64`0x767aae0fde3c567f`; SHA256`79f3582fce45dc36a25c454003206a43bbfd001c340a92459a8726fbd0512e31` | **206/206** observed copy packets join GS by length/hash; two retained aligned packets total3,392 B |
| Copy contract | FRAME: FBP112/FBW8/PSM24; TEX0: TBP0/TBW8/PSM32;17 strips | Predicts `D(x,y)=P(x+1,y+1)`; **0 different RGB pixels** over512×448 |
| Source preservation | Whole4 MiB VRAM identical at arm/freeze; producer changed pixels0 | Producer nonblack12,563; display nonblack12,358; identity alone does not prove a new frame |
| Actual Present before primary copy | Tick226, upload79, event5539; exact even-field match | Occurs before packet5548/GS5550; retained without treating it as the later-upload receipt |
| Actual Present after primary copy | Tick227, upload80, event5622; exact odd-field match, FNV32`0xf818f78d` | **GS5550 < Present5622 < next-copy5631/GS5633**; the freeze-tick copy is outside the frozen-source interval |
| Display selection | DISPFB1`0x9070`, SMODE2`0x1`, PMODE`0xff21`,512×448; source/displayFBP112; preferred0/fallback0 | Actual upload80 PNG SHA256`ba5fbce889b98081f286c16b2af92b1ffef2ee298745641cc8358508a7592576` |
| Retained image inspection | [display PNG](display-4a7d98177597f60731c8b0ab5ce83f9c412f2d5f871c1f196526ef599b033243.png): memory-card checking message on black, with line wrapping | Image/copy/Present receipt only; no title-menu, storage-failure, or movie-completion promotion |
| Reproduction | [e16a-graphics.json](e16a-graphics.json), retained packets/VRAM/Present files in [e16a-retained.json](e16a-retained.json) | Pixel and packet comparisons reproduce from canonical files |

| Real source closure / independent tail | Final receipt |
|---|---|
| Raw event file | **1,052,122 B**, SHA256`79825ae51186a32598b96c2edef17fa376e178deb6bc7886f074a45f0b1f307e`; contiguous seq1…6410; complete newline; exactly one final closure/shutdown pair |
| E15 source footer | `tick=4442 calls=5 returned=4 unwound=1 pending=0 selections=0 invocations=0 registrations=1 registrationTruncated=0` |
| E7 source footer | `tick=4442 events=6410 bootBytes=1019105 boundaryBytes=32555 packetBytes=3392 packetFiles=2 bootTruncated=0 boundaryTruncated=0 packetTruncated=0 windowComplete=0 aligned=1 arm=226` |
| Counter checks | Event count, API calls/exits, pending balance, registration/selection/invocation counts, boot/boundary line bytes, and both packet sizes match retained content; all truncation flags0 |
| Quiescence / window distinction | Last ordinary event at tick249; real run-exit footers at tick4442. `windowComplete=0` records that no later ordinary event closed the static window; required final shutdown exists, and the guarded E4 span is complete |
| Producer provenance | Production run exits through the repaired handwritten path before unchanged main's `_Exit`; no analysis process appended a footer; actual-linked fixture independently forces this path |
| Park | T1 Waiting/Mpeg at`0x3b1028`; T2…T6 Waiting/Semaphore26/30/31/32/36 at`0x423de8`; [e16a-progress.json](e16a-progress.json) |
| Independent function trace | **3,628,576 lines,1,322 distinct owners**,0 stack mismatches,empty final stack;216 missing-target records,216 parsed,0 damaged; query`0x2c5140` missing records0; drops0, SIF/RPC overflow0 |
| Tail receipt | [e16a-raw-tails.txt](e16a-raw-tails.txt), [e16a-events.txt](e16a-events.txt), [e16a-observation-closure.json](e16a-observation-closure.json); complete raw tails and strict parser results retained |

**E16 REPORT CHUNK 3 COMPLETE — one boot closed; all required joins and real source counters retained.**

## Chunk 4 — handoff, evidence closure, and commit boundary

| Handoff field | Evidence state / queued work |
|---|---|
| Rebuilt checkpoint | Fork67c0a632 reverified before build; rebuilt runner and suite byte-identical to E15;9,452 generated names/hashes unchanged; suite452/452; surviving SSD fixture reused and current-object bindings rechecked |
| Closure repair | Actual-linked non-title run-exit fixture FAIL-BEFORE→PASS; fallback/idempotence/window/disabled cases retained; real probe source counters and byte counts match, pending0,truncation0 |
| Request dependency | Same dynamic MPEG object joins Create→type1 registration→GetPicture→typed Mpeg wait; first undelivered edge is the request's type1 callback selection/delivery. No request-to-input or request-to-completion receipt exists |
| Later MPEG work | Diagnosis and original-binary constraints are complete for handoff; MPEG implementation remains absent. [NEXT-BRIEF.md](NEXT-BRIEF.md), [E15-ABI.md](E15-ABI.md) preserve caller thread/stack, type-word-only callback data, ignored callback v0, AddBs reentry outside the mutex, ordering/ownership, cancellation/lifetime and existing stream callback cases |
| API / decode residuals | Previous-function vs allocated-handle AddCallback return, AddBs1 vs copied-byte return, host FFmpeg ON, I19 device path OFF remain tabled; no downstream source/decode failure inferred from absent delivery |
| NEXT E brief | **E14 five-row absorb remains queued next.** No CSV/map change or absorb retry in E16; later MPEG implementation requires its own brief |
| Other demonstrated dependency | None replaces the joined type1 request/delivery edge in this capture;216 retained missing-target records do not independently establish a different request/completion dependency |
| Remaining E16 measurement gap | None in the required closure/object/request/graphics joins. Private-map eligibility remains an explicitly named source inference, and callback/input/completion remain unexercised observations |
| Boot stop | One title allowance spent; no second boot, no MPEG fix, no absorb |

| Standalone evidence / hygiene | Receipt |
|---|---|
| Capture retention | **29 originals**,150,819,740 content bytes, mapped to **25 canonical files**,3,601,989 retained bytes; each original content hash verified. Metadata remains included in the larger closed-cap totals; [e16a-retained.json](e16a-retained.json) |
| Canonical-only reproduction | Five miners run with `E16_CANONICAL_ONLY=1`, forcing retained input resolution; all nine analysis outputs byte-identical. Final replay also asserts registration count and every MPEG exit's target/object identity; [canonical-replay.json](canonical-replay.json) |
| Source / config closure | Final9,452-name/hash audit unchanged; MPEG.cpp/h, main, CSV/TOML and existing observation headers unchanged; [final-checkpoint.json](final-checkpoint.json) |
| Post-analysis resource sample | At17:13:38 UTC: build1,870,368,768 B + evidence17,604,608 B = **1,887,973,376 B internal allocated**; SSD owned710,934,528 B + fork positive growth16,777,216 B = **727,711,744 B**; free internal14,296,346,624 B / SSD240,309,501,952 B; [final-audit.json](final-audit.json) |
| Staging / commit reserve | Main Git positive growth capped at **32 MiB**, within the original512 MiB repair/link reserve; pre-staging allocation inventory and final staging receipt track it. Named E16 evidence only; [staging-receipt.json](staging-receipt.json) |
| Preserved SSD ownership | Before/after fixtures, tool temporary directories, and original captures retained. No preexisting content reclaimed, no E14 ownership-proof deletion needed |
| Post-exit process-query retry | Default sandbox `pgrep` returned3 because its process-list service was unavailable; identical read-only elevated check returned1, with lease absent. No second boot; [post-exit-process-check-retry.json](post-exit-process-check-retry.json) |
| Analysis alias lookup adaptation | Initial lookup assumed a separate0x3b0c58 generated file; none exists. Its E16-owned empty gzip is preserved under `analysis-errors`, explicitly not a source snapshot. Anchored two-row registry receipt replaces a truncated broad console search; [analysis-adaptations.json](analysis-adaptations.json) |
| Output completeness | Tool display limits on exploratory reads do not replace raw receipts. All bounded execution logs have `stdout_truncated=false`; canonical captures are hash-verified; report is read in chunks with a separate complete tail receipt |
| Exact commands | [COMMANDS.md](COMMANDS.md), all bounded-start/result JSON, exact fixture compile/link argv, case environments, probe argv/environment, and fork named commit commands |
| Inventory / review | [EVIDENCE.json](EVIDENCE.json) lists every retained file except itself; [HYGIENE.json](HYGIENE.json) and [TAIL-RECEIPT.md](TAIL-RECEIPT.md) pin complete report/command/handoff tails and authored-file checks |

| Repository boundary | Final action / retained state |
|---|---|
| Fork observation commit | `784f2b3e668ffa7a238936be415dc2e03d6c283c`; exactly `ps2xRuntime/src/lib/ps2_runtime.cpp`; `[E16]` prefix and `Orchestrated-By: Muse Code` trailer; **not pushed** |
| Fork inherited dirt | Generated `ps2xRuntime/src/runner/register_functions.cpp` and untracked `ps2_log.txt` remain exactly outside E16 staging; no generated source staged |
| Evidence commit | `git add -f -- local/research/E16`; message **`[E16] Rebuild checkpoint and close run-exit observations`**, trailer **`Orchestrated-By: Muse Code`**; commit identity returned separately after creation |
| Publication | **No push**; orchestrator owns publication at poll |
| Stop | Required E16 work closes at the evidence commit, within the eight-hour box; E14 absorb and MPEG implementation remain queued outside this task |

**E16 REPORT CHUNK 4 COMPLETE.**

**E16 REPORT TAIL COMPLETE — checkpoint rebuilt; run-exit repair forced before/after; 1/1 guarded probe closed with real counters; MPEG unchanged; E14 absorb queued next; no push.**
