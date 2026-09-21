# E17 — five verified I-row absorb

## Chunk 1 — contract, checkpoint and admission

| Contract / scope | Observable / bound |
|---|---|
| Required prior reads | E14 REPORT all153lines; E16 REPORT all185lines and NEXT-BRIEF all23lines, complete tails read before E17 work |
| Start / deadline | 2026-09-21T17:32:16.155688+00:00; deadline 2026-09-22T01:32:16.155688+00:00; eight-hour box |
| Hypothesis | Five established E14 rows yield predicted CSV7c827add, five exact runtime bindings, and unchanged prior regressions; no MPEG implementation |
| Alternatives / stop | Any row mismatch stops all five. Admission shortage stops before mutation. Generation/regression/observation failure is tabled. Lease occupied→stop without waiting; no partial absorb or second boot |
| Detailed upfront contract | [CONTRACT.md](CONTRACT.md); source/fork modifications follow checkpoint, all five fail-befores, and fresh admission |
| Internal budget |6GiB: build4GiB/codegen1.25GiB/evidence0.5GiB/reserve0.25GiB;2GiB floor+0.5GiB guard; required9,126,805,504B |
| SSD budget |36GiB: generated install/Git24GiB/temp8GiB/fixtures1GiB/probe1.5GiB/reserve1.5GiB;2GiB floor+0.5GiB guard; required41,339,060,224B |
| Admission | Initial internal 14172160000 B, SSD 236978176000 B; fits. Fresh after all fail-befores, before CSV edit: internal 14166921216 B, SSD 237677576192 B; [initial-admission.json](initial-admission.json), [admission-at-edit.json](admission-at-edit.json) |
| Accounting | `st_blocks*512`, including ExFAT directories/AppleDouble; logical bytes separately; fork positive growth, E17 owned paths, shared function trace included; COPYFILE_DISABLE=1 |
| Protected checkpoint | /tmp/p1-link and DerivedData retained; separate /tmp/e17-map-link/runtime and APFS /tmp/ssx3-e17-absorb-codegen; no reclamation |
| Execution caps | Ninja-j2; configure1800s/build7200s/link1200s/generation1200s;15s reserve; stdout16MiB with1MiB reserve. Probe90s/SIGTERM75s,1M syscall lines,1.5GiB aggregate; exact per-path caps in contract |
| Commit authorization | One MAP fork commit after regression and probe; explicit E17 generated staging supersedes older E14 no-generated-staging instructions. Fork push only; E17 evidence local commit, no main push |

| Checkpoint / baseline | Receipt |
|---|---|
| Fork remote/tracking/HEAD | All784f2b3e668ffa7a238936be415dc2e03d6c283c, before any build or source edit; [opening-git.json](opening-git.json) |
| Generated mirror |9,452 names/hashes equal E16; inputs/observation sources/main/MPEG match E16; [checkpoint.json](checkpoint.json), [before-generated.json](before-generated.json) |
| Protected build |554 objects/executables pinned; all remain byte-identical after generation/install; [protected-build-before.json](protected-build-before.json), [installed-source-audit.json](installed-source-audit.json) |
| E16 runner |163,456,352B; SHA256d9eb59012898545b84981a810c0b20ff78a6e4f60664774f660cecc2cadeed8d |
| Suite |452/452, rc0; unchanged5,643,528B suite SHA2568ba90048da7804a3dd278f172efbeb92d968ca89fd4ac9209b243e3d15c5a2eb; [baseline-suite.json](baseline-suite.json) |
| E16 closure fixture | Reused surviving165,122,752B SSD binary2089be52f52e1a6001cae902f78cc177b32669a46d8f96b70ff67d95bc45c94f; all six closure cases rc0; [baseline-closure-validation.json](baseline-closure-validation.json) |
| Prior / MPEG fixtures | Leaf24/consumer3/predicate14/query4/DROP pass; input and no-input both rc1 FAIL-BEFORE with callbacks0,saved128/RAM32MiB unchanged; [baseline-prior-validation.json](baseline-prior-validation.json) |
| Five-row fixture | Relinked against actual E16 runner objects/registry; alternate entry;165,123,040B, SHA2566cb77021baa522799e7845f1d5e5b0f93fe4d51a339aa0cf1f8008b114013005; linkrc0 in152.178626s; [before-fixture-link.json](before-fixture-link.json) |
| Title boots in baseline |0; all fixture executions are non-title |

| Origin | Exact CSV row bytes excluding LF | Current bytes / ELF | Absent / expected-present |
|---|---|---|---|
| I12 | `sub_0014F2A8,0x14f2a8,0x14f35c,0xb4` | E14 baseline owner, live I-owner/entry, raw180B slice all equal | rc0 / rc1 |
| I13 | `sub_00156750,0x156750,0x1567b8,0x68` | E14 baseline owner, live I-owner/entry, raw104B slice all equal | rc0 / rc1 |
| I14 | `sub_00243A80,0x243a80,0x243ab0,0x30` | E14 baseline owner, live I-owner/entry, raw48B slice all equal | rc0 / rc1 |
| I11 | `sub_00395730,0x395730,0x395750,0x20` | E14 baseline owner, live I-owner/entry, raw32B slice all equal | rc0 / rc1 |
| I15 | `sub_003A0158,0x3a0158,0x3a0290,0x138` | E14 baseline owner, live I-owner/entry, raw312B slice all equal | rc0 / rc1 |

| Reverification detail | Receipt |
|---|---|
| All five | [row-verification.json](row-verification.json) retains hashes, exact row hex, current paths, return/delay-slot bounds and permitted zero-NOP omissions; copied row-sources and originating I-row receipts make E17 standalone |
| Fail-before parser adaptation | E14 REPORT said binding=null, but E14 raw logs and unchanged lookupFunction return a diagnostic fallback while hasFunction=0. Initial E17 absence check itself returned0; the new parser's null assumption failed. Parser corrected and all ten checks rerun; no source/CSV mutation preceded the completed pairs. [presence-parser-adaptation.json](presence-parser-adaptation.json), [before-presence.json](before-presence.json) |
| Predicted / installed CSV |7c827add09aeea837e25f6048007ab91e65eb4b5f7a98f8fb4f448b606cfb9ba; identical to E14 prediction and I17 full CSV. No hash shift; prior2c5140/2c5300/2c5358 rows remain once each |

**E17 REPORT CHUNK 1 COMPLETE — all five reverified; admission fits before CSV mutation.**

## Chunk 2 — scoped regeneration and installation

| Phase / scope | Receipt |
|---|---|
| CSV edit | Exactly five sorted insertions; removing those five lines recreates the baseline byte-for-byte; [map-edit.json](map-edit.json) |
| Tool | Existing pinned ps2x-i10 host generator SHA256511791795c16649e69706725c412408acc8d35fda68c4d83a3229eae6bda0763; generator/analyzer source diff empty since b6252bb |
| Config | Only output path differs in generation-used.toml; canonical TOML, ELF, runtime/main/MPEG untouched |
| Fresh spawn admission | [admission-at-spawn.json](admission-at-spawn.json); original E14 admission floor and larger E17 overall allocation budget both checked |
| Generator result | rc0; 266766125 B logical / 286650368 B allocated including owner marker;9,457 generated cpp/header files plus owner marker; all output hashes retained; [generation-result.json](generation-result.json), [generation-output.json](generation-output.json) |
| Added generated files | sub_0014F2A8_0x14f2a8.cpp, sub_00156750_0x156750.cpp, sub_00243A80_0x243a80.cpp, sub_00395730_0x395730.cpp, sub_003A0158_0x3a0158.cpp; each byte-equal to pinned I-lane entry |
| Changed existing files | ps2_recompiled_functions.h and register_functions.cpp only; all other9,450 existing generated files unchanged; no removal; [generation-scope.json](generation-scope.json) |
| Exact slots | Five previously empty slots now target their exact generated entries; prior query/predicate/leaf/DROP slots retained |
| Interior slots |0x14f2c8 and0x14f31c move from owner0x14f250 to new entry0x14f2a8; both inside the verified I12 slice and match the current I12 registry exactly; [i12-interior-slot-receipt.json](i12-interior-slot-receipt.json) |
| Slot-audit adaptation | Initial check assumed only five changed assignments. Two generated interior resumes were identified and verified against I12; no extra CSV row, source change, or repeated generation; [slot-audit-adaptation.json](slot-audit-adaptation.json) |
| Installation | Seven changed/new generated files copied with byte verification. Only newly created globbed AppleDouble siblings moved to owned quarantine, preexisting metadata retained; [installation.json](installation.json) |
| Inherited Git delta | HEAD registry is438B empty scaffold; E16 active registry was32,674,473B with398,955 populated slots. Full inherited baseline archived; E17 active-before→after delta is exactly five new slots plus two I12 resume aliases. [inherited-registry-delta.json](inherited-registry-delta.json) |
| E16 protection | All554 protected objects/executables and all pinned handwritten sources unchanged; [installed-source-audit.json](installed-source-audit.json) |

| Build / complete regression | Receipt |
|---|---|
| Configure / build | rc0 in73.910040s /669.355607s; separate /tmp/e17-map-link/runtime; E16 configure flags retained; Ninja-j2; compile database contains zero sidecar inputs |
| Native linker concurrency | Unchanged ThinLTO linker sampled564.7% CPU and4,231,376KiB RSS; Ninja remains-j2; [link-process-sample.json](link-process-sample.json) |
| New runner | 163490704 B; SHA256530ab6c6b5aa6f9159c6e59f7a3b8d01f682d5a50272b33f37182b621867dad8; [built-binaries.json](built-binaries.json) |
| Rebuilt suite |5,643,528B; SHA256939cc64fc376f70bb81295f511eb76fe028524f85387d13577a50d0a6cf8a8dc; **452/452**, rc0; [current-suite.json](current-suite.json) |
| Current actual-linked fixture | 165157552 B; SHA2563d6bb6bbbffa201389e14650ba346696a0d9a372e5e60743f0e2b73a9635b401; linkrc0 in324.034004s; four fixture source files identical before/after; [fixture-source-identity.json](fixture-source-identity.json), [after-fixture-link.json](after-fixture-link.json) |
| Five bindings | All five check-present rc0 with exact named function symbol; inverse check-absent rc1; [after-presence.json](after-presence.json) |
| Prior bindings | Leaf24,consumer3,predicate14,query4,DROP pass; [current-binding-validation.json](current-binding-validation.json) |
| MPEG delivery cases | No-input/input both **rc1 FAIL-BEFORE**; callbacks0,manualCallbackCalls0,AddBs0,completion0; saved128 and32MiB RAM preserved; no MPEG implementation |
| Run-exit closure cases | Quiescent,idempotent,window-complete,disabled,unopened,fallback-error all rc0; real footer counts/pending/truncation checks retained; [current-closure-validation.json](current-closure-validation.json) |
| Protected / unchanged sources | Full9,457-name installed mirror and554 protected E16 object/executable hashes rechecked; main/runtime/MPEG/observation sources unchanged; [regressed-source-audit.json](regressed-source-audit.json) |
| Pre-probe order | All full regression gates complete before capture preparation; fork HEAD still784f2b3e and index empty; [entry-preflight.json](entry-preflight.json), [e17a-build.json](e17a-build.json) |

**E17 REPORT CHUNK 2 COMPLETE — scoped generation, installation and full regression receipts retained.**

## Chunk 3 — one guarded boot and closed joins

| Guard / capture | Receipt |
|---|---|
| Fresh T13 pre-claims | At18:02:14–16Z: fork/source/binary identities, suite452/452, aligner selftest ALL PASS, ISO/ELF, byte admission, prior lane release tails; lease absent and runner pgrep rc1, rechecked immediately before atomic claim. [e17a-preflight.json](e17a-preflight.json) |
| Launch | REPORT_ALL=1; E15 trace/alignment, E7 events/packets, E4 VRAM/history/Present; exact argv/environment in [e17a-config.json](e17a-config.json) |
| Lease / boot allowance | Claim18:02:16.318493Z; boot18:02:16.323514Z; process end18:03:32.831452Z; release18:03:32.879920Z,48.468ms later. **1/1 title boot spent**; no second launch. [boot-attempt.json](boot-attempt.json), [e17a-result.json](e17a-result.json) |
| Wall bound | SIGTERM guard observed75.607s; runner rc0 at76.512374s within90s cap; no SIGKILL. Aligned span complete at9.091095s |
| Closed cap accounting |150,166,588B logical /216,006,656B allocated;54,894 syscall lines <1,000,000; all group and aggregate caps pass after shutdown flush. [e17a-closed-caps.json](e17a-closed-caps.json) |
| Complete source tail | Real run-exit footer tick4492:6,386 contiguous events;5 calls=4 returns+1 unwind;pending0;registrations1;registrationTruncated0. [e17a-observation-closure.json](e17a-observation-closure.json) |
| Byte / packet reconciliation |bootBytes1,019,105;boundaryBytes29,747;packetBytes3,392=2×1,696; every source count matches retained rows/bytes; boot/boundary/packet truncation flags all0;windowComplete0;aligned1;arm226 |
| Retention / replay |29 original files,150,031,420B payload,25 unique canonical paths; metadata/directory allocation explains difference from cap accounting. Every content hash verified; SSD originals preserved. Five canonical-only miners rc0; all nine outputs byte-identical. [e17a-retained.json](e17a-retained.json), [canonical-replay.json](canonical-replay.json) |

| Dynamic object / lifetime join | Receipt / interpretation limit |
|---|---|
| Singleton | S=0x61ba60 observed; S+0x5a74 stores1…206 contiguous; steady(M,G,A,B,P,D)=(1,0,0,112,0,112) |
| Memory-card object | Constructor MC=0xb851a0,VT=0x486f78 atseq855/tick80; UI=0xb84a50 points to it atseq868 withguard1;1,050 guarded card events |
| Lifetime boundary | Vtable overwrite atseq6371/tick248 ends interpretation of MC fields; four later stores retained as raw. [e17a-lifetime.json](e17a-lifetime.json) |
| Card joins |375 query calls/returns,8 predicates,142 leaf calls,141 wrappers;0 unmatched returns/unclosed calls/nonreturn exits. [e17a-card.json](e17a-card.json) |
| UI alignment | Guarded UI3→6 atseq5521/**tick225**, arms226/freezes227; transition and capture boundary ticks kept separate |
| MPEG identity | Dynamically discovered0x587b30 through Create→AddCallback→GetPicture→wait token equality; no inherited numeric MPEG address used as the join key |
| Registration | Atseq6380/tick249: type1,function0x3b0b10,userdata0x587b00; returned handle1; request shadowseq6384 matches all fields |
| Request / typed wait | GetPicture atseq6383/tick249; source0x3b1020; continuation0x3b1028; typed Mpeg wait atseq6385,token0x587b30; request unwinds atseq6386; thread1 remains Waiting/Mpeg at0x3b1028 |
| Existing private-state log | ended0,failed0,sawInput0. Empty frame queue follows the pinned wait branch; no new private-state accessor |
| Callback selection / delivery | Scheduler selections0; actual callback dispatches0; callback returns0; valid-no-input returns0; AddBs dispatches0; input/completion events0. Zero returns describes absence, not an exercised no-input branch |
| Static eligibility | Unchanged AddCallback storesstream=false; private selector requiresstream=true. Private-map selection is not tapped; static source eligibility remains separate from scheduler selection and actual dispatch |
| Owner-label caveat | One sub_003B0B40 owner log is exact setup entry0x3b0c58 from0x3b0520, not exact callback-helper entry0x3b0b40. Exact callback/helper/AddBs dispatches0. [function-owner-alias-audit.json](function-owner-alias-audit.json) |
| Missing request/completion edge | Actual GetPicture request has no observed type1 callback delivery or completion. Guest feeder/decoder behavior is unexercised; no promotion to a feeder, decoder or graphics dependency. [e17a-mpeg.json](e17a-mpeg.json) |

| Graphics join | Receipt / boundary |
|---|---|
| Copy consumption |206 source0x4ffcc0 copy events each joined to one later GS entry bytick/hash/bytes; aligned copies226/227 each1,696B;2 retained packets |
| Frozen interval |[226,227); primary copyseq5547→GS5549 at226 is inside. Tick227 copyseq5619→GS5621 remains outside the frozen-source interval |
| Source / display |17 destination-FBP112 strips fromsource-FBP0; VRAM arm/freeze byte-identical;0 source-changed pixels; shifted source→display RGB mismatches0; both7,103 nonblack pixels |
| Actual Present ordering | Upload87/seq5556 at226 andupload88/seq5610 at227 both follow primaryGS5549 and exactly match corresponding display fields. The second upload precedes tick227 copy; it is not attributed to that later copy |
| Display parameters |512×448;SMODE2=0x1;PMODE=0xff21;DISPFB1=0x9070; source/displayFBP112;preferred0/fallback0 |
| Visual receipt | Inspected retained upload87: memory-card checking message. Pixel hashes and complete packet/VRAM/Present relationships in [e17a-graphics.json](e17a-graphics.json); visual content alone is not a completion dependency |

| Absorbed entry | Function-owner entries in this boot | Missing-target records |
|---|---:|---:|
|0x14f2a8|4|0|
|0x156750|1|0|
|0x243a80|1|0|
|0x395730|204|0|
|0x3a0158|6|0|

| Trace integrity / gap | Receipt |
|---|---|
| Function census |3,608,880 lines;1,327 distinct owners; balanced stack;0 mismatches;0 missing markers/parsed missing/damaged records;0 DROP records and0 SIF RPC overflows. Owner entry counts are not exact guest-PC or completion claims |
| Observation receipts | All four primary miners rc0 with no missing receipt; separate alias audit rc0; [boot-analysis-summary.json](boot-analysis-summary.json) |
| MPEG implementation | None; both actual-linked delivery cases remain rc1 FAIL-BEFORE. ABI constraints retained in [E15-ABI.md](E15-ABI.md) and original ELF slices |

**E17 REPORT CHUNK 3 COMPLETE — source closure, dynamic lifetime/request and guarded graphics joins retained.**

## Chunk 4 — fork publication, dedupe handoff and evidence closure

| Fork publication | Receipt |
|---|---|
| MAP commit | `e63f1616320d12c3f213899af6fba03fee3eafb2`; parent `784f2b3e668ffa7a238936be415dc2e03d6c283c`; [fork-commit.json](fork-commit.json) |
| Named staging | Exactly eight files below, checked before commit and by diff-tree after commit; no handwritten/runtime/MPEG/main/config changes in the commit |
| Inherited generated content | Registry was the only inherited tracked modification: committed438B scaffold versus active E16 registry32,674,473B. The MAP commit records the generated registry and previously ignored declarations; active E16→E17 changes remain exactly five entries plus two verified I12 interior aliases |
| Push agreement | Pushed only `fork HEAD:refs/heads/ssx3`; local HEAD, fork tracking ref and fresh ls-remote equal the MAP commit. [fork-push.json](fork-push.json), [fork-commit-commands.json](fork-commit-commands.json) |
| Receipt chronology | fork-commit.json was captured before push and records pushed=false at that instant; fork-push.json and final-audit.json record the subsequent successful push and agreement |
| Fork remainder | Index and tracked worktree clean; only preexisting untracked ps2_log.txt remains. Existing AppleDouble pack-index warning persists with Git rc0; no unrelated metadata reclaimed |

| Committed path | Classification |
|---|---|
| `games/ssx3/ssx3-functions.sweep.csv` | Five-row CSV insertion |
| `ps2xRuntime/src/runner/sub_0014F2A8_0x14f2a8.cpp` | Matching generated source |
| `ps2xRuntime/src/runner/sub_00156750_0x156750.cpp` | Matching generated source |
| `ps2xRuntime/src/runner/sub_00243A80_0x243a80.cpp` | Matching generated source |
| `ps2xRuntime/src/runner/sub_00395730_0x395730.cpp` | Matching generated source |
| `ps2xRuntime/src/runner/sub_003A0158_0x3a0158.cpp` | Matching generated source |
| `ps2xRuntime/src/runner/ps2_recompiled_functions.h` | Matching generated source |
| `ps2xRuntime/src/runner/register_functions.cpp` | Matching generated source |

| I-lane dedupe | CSV line in MAP commit | Exact row |
|---|---:|---|
| I12 | 873 | `sub_0014F2A8,0x14f2a8,0x14f35c,0xb4` |
| I13 | 1022 | `sub_00156750,0x156750,0x1567b8,0x68` |
| I14 | 2943 | `sub_00243A80,0x243a80,0x243ab0,0x30` |
| I11 | 7012 | `sub_00395730,0x395730,0x395750,0x20` |
| I15 | 7176 | `sub_003A0158,0x3a0158,0x3a0290,0x138` |

| Handoff / remaining gap | Receipt / scope |
|---|---|
| Absorb dependency | All five rows landed together; predicted CSV7c827add remains exact. I-lane local-port dedupe is handed off with commit and line numbers; no I-lane edits performed |
| MPEG brief | Now unblocked and queued as a separate brief. First missing edge remains actual GetPicture request→type1 callback delivery/completion; no MPEG implementation in E17 |
| ABI constraints | Original `(mpeg,callback-data,userdata)` call; type1 producer initializes only word0=1 and discards callback v0. Saved128-bit registers/RAM/continuation preserved by the retained actual-linked fixture. No EOF inference from callback return, guessed event layout, invented wall cadence or feeder diagnosis without delivery. [E15-ABI.md](E15-ABI.md), [NEXT-BRIEF.md](NEXT-BRIEF.md) |
| Measurement gaps | No missing required E17 closure/join receipt. Private callback-map selection and guest source/decoder behavior remain outside the observed delivery path; kept separate in the MPEG table |
| Harness adaptations | Initial presence-parser null assumption corrected using original raw logs; all five complete absent/present pairs rerun before mutation. Registry audit expanded only for two verified I12 resumes. Both first attempts preserved; no repeated generation or title boot |
| Boot / task stop |1/1 spent, lease released, final runner pgrep rc1. Stop after standalone evidence commit; no extra title run or implementation |

| Final resource / hygiene receipt | Observed |
|---|---|
| Final pre-staging sample | Internal owned 2,185,027,584B /6GiB; free 11,938,250,752B. SSD charged 859,832,320B /36GiB; free 236,837,666,816B; fork positive growth 42,991,616B. [final-audit.json](final-audit.json) |
| Evidence Git allocation | Additional32MiB cap declared from the original0.25GiB internal reserve before staging; actual scope/growth and combined internal charge in [staging-receipt.json](staging-receipt.json) |
| Protected checkpoint | Final9,457-name installed mirror matches regeneration; all554 E16 objects/executables byte-identical; pinned handwritten/main/MPEG/config sources unchanged. [final-source-audit.json](final-source-audit.json) |
| Tool caps | Every bounded operation finished without cap binding or stdout truncation. The initial five-fail-before wrapper rc1 is the retained parser-assumption failure; its corrected complete rerun rc0 preceded edits |
| Retained payload |29 SSD originals rehashed equal25 canonical files totaling 3,570,462B; no original deleted. Final real-footer reparse matches6,386 events |
| Time box | Final source/retention/remote audit at 2026-09-21T18:13:26.163108+00:00; within eight-hour deadline2026-09-22T01:32:16.155688Z |
| Exact commands | [COMMANDS.md](COMMANDS.md); structured command/argv/cwd/environment/log receipts retained alongside each phase |
| Evidence commit | `git add -f -- local/research/E17`; `[E17]` prefix and `Orchestrated-By: Muse Code`; local main evidence commit only, no ssx3 push |
| Document closure | Four complete report chunks; full final tail and document hashes in [TAIL-RECEIPT.md](TAIL-RECEIPT.md); inventory [EVIDENCE.json](EVIDENCE.json), authored checks [HYGIENE.json](HYGIENE.json) |

**E17 REPORT CHUNK 4 COMPLETE — fork publication, I-lane row handoff and queued MPEG boundary recorded.**

**E17 REPORT TAIL COMPLETE — five-row MAP e63f1616320d12c3f213899af6fba03fee3eafb2 pushed to fork; 452/452; one guarded boot with real source closure; MPEG implementation queued; evidence committed locally, no main push.**
