# E11 — exact busy-query entry restored; next card predicate parked

| Selected outcome | Receipt | One next action |
|---|---|---|
| **(ii): `0x2c5140` restored; a remaining entry gap appears after the wait.** | 321 actual query call/return pairs, zero missing-query reports, completed GetInfo/Sync and UI pending clear. New missing entry `0x2c5300` has a branch-changing result at the observed zero slot status. D contains the “No memory card (PS2) inserted” message; packet/source/D/field-Present join is complete. | A separately authorized, single-entry repair of `0x2c5300`, with actual-binding predicate tests and guarded caller/slot observations, as specified in [NEXT-BRIEF.md](NEXT-BRIEF.md). No second gap was repaired in E11. |

The visible message is not a menu claim or evidence that a physical storage
dependency blocks progress. GetInfo returned a present, formatted card. The
missing predicate is an earlier demonstrated divergence; attribution of every
later UI transition remains open.

## 1. Contract and scope

| Item | Record |
|---|---|
| Start / deadline | 2026-09-21 07:44:49 / 15:44:49 UTC; [upfront contract](CONTRACT.md). Latest main pull was already up to date. E11 brief and both E10 reports were read in full. |
| Hypothesis | Reclaiming retired build trees admits the one sanctioned CSV row; its generated entry returns the busy predicate without executing its owner's GetInfo body. |
| Observables | Exact checkpoint identity; fresh admission before CSV edit and immediately before spawn; actual-binding four-case truth table; same-run object and query/request/copy joins. |
| Alternatives / stop | Identity, admission or entry failure → (iii). First remaining gap after restoration → (ii), table it. Complete progression → (i). Unusable measurement → its exact repair only. One boot maximum. |
| Scope used | One query regeneration, one build of runner/tests, actual-object relink/test, one verification boot. DROP generation was not repeated. Runtime edits only add bounded observations. |
| Scope closed | No second entry repair, storage/SIF/CD/input promotion, raster/Present change, or additional boot. Standing no-regen resumes when E11 closes. |

## 2. DROP checkpoint re-verification

| Check before reclamation / regeneration | Result | Receipt |
|---|---|---|
| Fork baseline | `be0c9ee`; DROP selector remains absent | [before manifest](before/manifest.json), canonical/used TOMLs |
| Generated names and hashes | All **9,449** match E10's completed checkpoint | [checkpoint.json](checkpoint.json), [expected manifest](expected-drop-generated.json), [observed manifest](before/generated.json) |
| Registry | `5d4ce8c47d9e5238c67ffa5830c43466e4e9f03b2c1adf0bbd3d9028a79c4ad1` | [binding table](before/binding-targets.json) |
| Runner | `f5eeea20f661666f045d90da14acbde49a6349056d055c3fd0efcc34568c7f1f` | [before manifest](before/manifest.json) |
| Suite | **452 passed / 0 failed** | [checkpoint suite](checkpoint-suite.txt) |
| Actual DROP behavior | `sub_00426230_0x426230`; empty buffer returns v0=0, PC=supplied RA, unchanged SP and s0 low 64 bits | [absent-mode test](checkpoint-binding-absent.txt) |
| Actual query fail-before | `hasFunction(0x2c5140)=false`; absent mode rc=0; expected-present mode rc=1 | [present-mode failure](checkpoint-binding-present.txt) |
| Fixture identity | Same E10 executable/inputs: `6fe978804cd63cbac35155d40b623eb73e1eecbd939ca9ddacf1b4fa258736d4` | [checkpoint.json](checkpoint.json) |

## 3. Reclamation and fresh admission

The admission requirement stayed **3,489,660,928 B**: 1 GiB logical reservation,
2 GiB free floor and 256 MiB guard. Reclamation stopped at that requirement
plus 512 MiB headroom, **4,026,531,840 B**. No guard was lowered.

| Tree, oldest eligible first | Ownership proof before removal | File allocation removed | Immediate free before → after | Timing |
|---|---|---:|---:|---|
| `/private/tmp/p10-link` | UID 501; retired P10/CMake identity; no live board/pane claim; `lsof +D` rc=1 with empty stdout/stderr, repeated immediately before deletion | 1,500,246,016 B | 3,132,948,480 → **4,636,819,456 B** | 07:50:17–18; before CSV edit; target crossed, removal stopped |
| `/private/tmp/p11-link` | Same independent proof for P11; fresh live board and empty-handle recheck | 1,761,443,840 B | 1,453,240,320 → 3,217,694,720 B | 08:02:13–15; later build-time free-space regression |
| `/private/tmp/p12-link` | Same independent proof for P12; fresh live board and empty-handle recheck | 1,309,143,040 B | 3,211,194,368 → **4,523,212,800 B** | 08:03:16–18; target crossed, removal stopped |

Receipts: [inventory](reclamation-inventory.json), [ledger](reclamation-ledger.json),
per-tree `reclaim-p10/p11/p12-link-proof.json` and `-removal.json`, including
both `df` readings and board/lsof rechecks. The live board identified E11,
G15, T36 and I14; its current pane evidence superseded the stale E10/I13
documentation line. `/tmp/p1-link` and Xcode DerivedData were protected.

| Admission sample | Internal free | Persisted ordering |
|---|---:|---|
| After initial reclamation, 07:50:18.244 UTC | **4,636,766,208 B** | [admission-before-edit.json](admission-before-edit.json); CSV still unchanged; full target met |
| At edit, 07:51:59.137 UTC | **4,638,035,968 B** | [admission-at-edit.json](admission-at-edit.json), written before CSV mutation |
| Immediately before spawn, 07:51:59.320 UTC | **4,637,945,856 B** | [admission-at-spawn.json](admission-at-spawn.json); full requirement met |
| Generator completion | **4,344,897,536 B** | [entry-generation.json](entry-generation.json) |

**Resource chronology qualification:** initial reclamation and admission
preceded the CSV edit as required. During the subsequent build, internal free
space fell again: scratch cleanup at 07:59 recorded 1,168,519,168 B before
and 1,461,129,216 B after removal. P11 then P12 were reclaimed under renewed
per-tree proofs, restoring the target. The record therefore does **not** claim
the internal floor held throughout the build. The generator's guarded interval
passed; no second generation occurred. [scratch-cleanup.json](scratch-cleanup.json)
records every installed retained name/hash, the owned marker and before/after
`df`; `/tmp/ssx3-e11-query-codegen` is absent.

## 4. Query regeneration, installation and actual-binding tests

| Step | Result / forcing receipt |
|---|---|
| ELF revalidation | `0x2c5140..0x2c5168` loads state +4 and outstanding +0x40, returns their nonzero OR; [raw disassembly](query-raw-dis.txt) |
| CSV edit | Only `sub_002C5140,0x2c5140,0x2c5168,0x28` added in address order; existing owner retained. SHA `c17db90b72db490772a649eb64b91487d54d1602b258be2e3205e2e7b039c6aa`; [edit record](query-map-edit.json) |
| Inputs | ELF `1b49d05c…`; generator `51179179…`; canonical TOML `2f2ae543…`; derived TOML changes only `general.output`. Full identities in [generation record](entry-generation.json). The historical P1 CSV is not the selected function map. |
| Query generation | Normal rc=0 in **2.880692 s**; 266,712,101 logical / 286,584,832 allocated bytes, including owner marker; bounds 1 GiB / 1.25 GiB with 128 MiB headroom, floor+guard, 1,200 s wall and 16 MiB log caps |
| Installation | **3 changed files**, 9,447 unchanged, no leftovers; 33,471,233 changed bytes copied without metadata. Proven-created AppleDouble companions removed. Allocation growth 1 MiB; [installation](entry-installation.json) |
| Changes only | New query body, registry and declaration header. DROP body and prior query owner byte-identical; [scope audit](generation-scope-audit.json) |
| Exact query binding | Registry slot **463950 → `sub_002C5140_0x2c5140`**; registry SHA `68217e9a308cd7aaa540a1cac4115e9f9021b3e984b2a7e6b1e3250639be8907`; [after bindings](after/binding-targets.json) |
| Build / suite | `cmake --build /tmp/p1-link/runtime --target ps2EntryRunner ps2x_tests -j4`; rc=0; **452/452**, then fresh pre-boot **452/452** |
| Actual-object test | Relinked against the new runner objects/registry, not a replacement query. Symbol resolved by `dladdr`; [link manifest](entry-binding-link.json), [test](entry-binding-test.txt) |
| DROP after repair | Still emitted guest handler `sub_00426230_0x426230`, normal RA/SP/s0-low64/v0 receipt; no TODO trap |

| State +4 | Outstanding +0x40 | Actual v0 | RA / SP | Callee-saved 128-bit / RAM / GetInfo |
|---:|---:|---:|---|---|
| 0 | 0 | 0 | PC `0xf00000`, SP `0x100000` | Preserved / whole 32 MiB unchanged / 0 calls |
| 1 | 0 | 1 | Same | Same |
| 0 | 1 | 1 | Same | Same |
| 1 | 1 | 1 | Same | Same |

Checked full 128-bit GPRs 16–23 and 28–31; the GetInfo spy would fail on any
call. [Fixture source](e11_binding_test.cpp), [results](entry-binding-results.json)
and [preflight](entry-preflight.json) retain the exact checks. No handwritten
query, owner-only registration or new HLE was introduced.

## 5. One guarded boot and caps

| Pre-claim | Result |
|---|---|
| Lease / runner | Lease absent; `pgrep -x ps2EntryRunner` rc=1, repeated after tests |
| Media | ISO 3,005,415,424 B; both ELF copies 3,890,784 B with pinned SHA |
| Space / waits / selftest | SSD and internal `df`, recent wait-log tails, aligner `selftest: ALL PASS` |
| Fresh binaries | Runner **163,437,088 B**, SHA `c39e59a7f202436e8a70c1f9f4373e7b577b71b1191c6912ecc8ad2cfd0f2c96`; suite **5,624,840 B**, SHA `3ccf369fc01ce8d3e02fae6a7e4f8597c2b3fdb1ec1cc3051b91005562e68573` |
| Suite immediately before claim | 452 passed, 0 failed |
| Command / taps | `e11_capture.py a --report-all --arm 600 --wall 90`; REPORT_ALL=1; existing E7/E4 plus bounded dynamic card taps; exact argv/env/watch set in [config](e11a-config.json) |

Full [preflight](e11a-preflight.json), [build identity](e11a-build.json),
[liveness](e11a-liveness.txt) and [result](e11a-result.json) are retained.

| Wall / ownership event | UTC / value |
|---|---|
| Claim / process start | 08:16:34.223594 / 08:16:34.228235; PID 90324 |
| Required E4 span complete | 27.153293 s |
| First binding limit | Wall guard at **75.375 s**, 90 s declared cap minus 15 s reserve |
| SIGTERM / normal process exit | 08:17:49.609399 / 08:17:49.718182; rc=0 |
| Release | **08:17:49.764954**, immediately after exit, before analysis |
| Total / boots | **75.494330 s; 1 of 1** |

| Closed capture, including shutdown flush | Logical bytes | Allocated bytes | Logical / allocated cap |
|---|---:|---:|---:|
| Boot log | 11,868,903 | 12,582,912 | 256 / 256 MiB |
| Syscall trace | 3,353,468 | 4,194,304 | 96 / 96 MiB |
| Function trace | 253,406,999 | 253,755,392 | 1,024 / 1,024 MiB |
| E4 | 8,544,788 | 16,777,216 | 12 / 64 MiB |
| Park | 137,991 | 4,194,304 | 32 / 128 MiB |
| Frames | 195,853 | 31,457,280 | 32 / 64 MiB |
| E7 | 1,429,713 | 13,631,488 | 8 / 32 MiB |
| **Aggregate** | **278,937,715** | **336,592,896** | **1.5 / 1.5 GiB** |

Progress **56,380 / 1,000,000 syscall lines**. All byte caps include ExFAT
allocation and metadata; they passed after final flush as well as at the
signal. [Closed-cap audit](e11a-closed-caps.json). No lease wait or second boot.

## 6. Same-run query and intended-request progression

| Join | Ordered receipt |
|---|---|
| Dynamic card object | Tap seq **853**, tick 80, constructor PC `0x2c3fc4` writes vtable `0x486f78` to **MC=`0xb851a0`** |
| UI pointer | Seq **866**, PC `0x23d5c8`, guarded UI=`0xb84a50`; UI+0x434=`0xb84e84` stores that MC |
| Query | **321 calls / 321 matched guest returns**; same dynamic a0, vtable, SP and truth result; unmatched/unclosed=0. Whole function trace also counts 321; missing-query reports=0 |
| Port selection | Seq **1702→1703**, tick 118, source `0x2c44a8`, return `0x2c44b0`, `(state,outstanding)=(0,0) → v0=0` |
| State-3 request | Seq **1705/1706** enters `0x2c48c0` with a1=3 and writes MC+4=3; **1707** calls `0x2c50e0` from **`0x2c4980`**; **1711→1712** calls/returns GetInfo `0x40a498` |
| GetInfo result | v0=0; output globals `(type,free,result,formatted)=(2,8192,0,1)`; then seq **1713/1714** sets outstanding=1 / internal command=5 |
| Intended request accepted | Seq **1717**, port helper returns v0=1 to `0x23fb48`; **1718**, PC `0x2413cc`, writes UI+0x338=1 |
| Completion | Seq **1720→1721**, Sync `0x40a360` returns v0=1; **1722** clears outstanding; **1723** writes port-0 status=0. State 3→4→0 is observed at 1725/1728 |
| Busy case and UI clear | Second outstanding request: **1741→1742** query returns 1 at `0x2c44b0`. Sync completes at **1747**, outstanding clears at **1748**; UI query **1750→1751** returns 0; **1752**, PC `0x23d6b4`, clears UI+0x338 |
| Whole bounded card series | **12 GetInfo returns v0=0; 15 Sync returns v0=1**; later states 6 and 7 also exercise busy returns. Subsequent UI pending clear at tick 225 is retained |

[Card join](e11a-card.json), [ordered request subset](e11a-request-join.json),
[full card events](e11a-card-events.json). The indirect jump-table label
`0x2c4980` is proved by the subsequent call's source PC, not by inventing a
separate function-call observation at that label.

## 7. Packet → source → D → Present

| Guard / edge | Receipt |
|---|---|
| Same-run graphics singleton | One `0x4a289c` store → **S=`0x61ba60`**, no teardown-null store; constructor and display fields match that S |
| Slot/mode guard | 561 continuous display increments, M=1/G=0 throughout; all 560 post-initial snapshots `(PAIR-A,PAIR-B,P,D)=(0,112,0,112)` |
| Boundary packet | Five identical **1,696 B** packets, source `0x4ffcc0`; SHA `79f3582fce45dc36a25c454003206a43bbfd001c340a92459a8726fbd0512e31`, FNV64 `767aae0fde3c567f`; mask=0, queued=0 |
| GS consumption | tick 599 seq **13316→13318**; 600 **13381→13383**; 601 **13446→13448**; 602 **13511→13513**; 603 **13576→13578**. Each DMA→GS entry matches full bytes/hash |
| Packet contents | FRAME1 D=112, TEX0 source block=0 / width=8; 17 textured sprites, then production returns to P=0. E4 records **17 D draws then 219 P draws** |
| Source/D content | Frozen P and D each **26,085 RGB-nonblack pixels**. Packet-derived sprite sampling predicts D with **0 RGB differences** across the full 512×448 surface; 228,418 pixels copied, 958 uncovered border pixels measured black |
| Stable boundary source | Arm and freeze VRAM identical: SHA `006f4d93f8bfb5cda2c194d95f36c71847d36a171c4f17c1a0c7a0405dfa2fad` |
| Present | PMODE=`0xff21`, SMODE2=1, DISPFB1=`0x9070`; display/source=112/112, fallback=0. Four observed fields match independently decoded D exactly: ticks 599/601/603 FNV `96a6875d`; 600 `0d4ede7d` |
| Host upload | Full latest PNG equals the expected odd field of D; 26,240 nonblack pixels, RGBA SHA `cf6665c39ad52f5cd554fcb3e44b68a0cbfc4c6b0f1b27be74578992de0098e4` |

[Join table](e11a-join.json), [packet-derived content calculation](e11a-copy-content-join.json),
[frame calculations](e11a-frame.json), [producer PNG](producer-428d0abfed9a84ee0564e176319c6989536ffb7516700c020c4b45d9e76600c7.png),
[display PNG](display-d593db2e727744c4ace7e9eb7ca091387e118f2c04612e5c5091f8ed23561aff.png).
The images were viewed: the new message starts “No memory card (PS2) inserted”
and requests a card in slot 1. Wrapping/clipping is recorded, not repaired.

| Challenged comparison premise | Correction / limit |
|---|---|
| E7's uniform source offset (+1,+1) suffices for every pixel | It differs at exactly **(27,446)** and **(219,446)** here. The final sprite has XY `(0,446.5)..(512,447.5)` and UV `(0,447.5)..(512,447.5)`, unlike the first 16 half-pixel-offset strips. Per-sprite decode plus the captured runtime's filtering gives **zero** differences. |
| A later producer frame caused those differences | Arm and freeze are byte-identical; this explanation is falsified. [Timing audit](copy-timing-audit.json) and [initial model audit](copy-edge-audit.json) remain retained. |
| Full copy match implies hardware raster conformance | This is a packet/source/content join against the current runtime sampling behavior. The uncovered border is measured separately. No raster change or hardware-conformance claim follows. |

## 8. First remaining card-path entry and parking answer

| Observation / static join | Evidence and scope |
|---|---|
| First new predicate miss | Raw boot line **5119**: source `0x242150`, target `0x2c5300`, a0=MC=`0xb851a0`, a1=s1=0, `[a0]=0x486f78`, v0=`0x2c5300`, policy=1. After the first UI pending clear |
| Selected status | MC+0x184=`0xb85324`; captured write seq 1749 is 0; surrounding snapshots and every captured status write are 0. Following sibling observation seq1757 has a1=0, slot0=slot1=0 |
| Exact guest predicate | ELF `0x2c5300..0x2c5320`: `status[port] == -10002`, stride 0x14, field +0x184. Observed status 0 therefore requires v0=0. Vtable +0x180 adjustment=0; +0x184 points to `0x2c5300` |
| Actual generated caller | Policy 1 returns from missing call without executing a body or changing v0. Caller `0x242158` tests v0 before its delay-slot replacement; observed nonzero implies `0x2421a8→0x2421b4`, clearing UI+0x344. Correct v0=0 would continue to the next check. This downstream branch/store is **code-derived**, not a new dynamic branch/store tap |
| Repeated use | Second miss raw line **9292**, source `0x2d37f8`, same MC, a1=0 and stale nonzero v0; UI-facing wrapper also propagates this result |
| Generated coverage | `0x2c5300` body already lies after the return in owner `sub_002C52D8`; exact binding absent. The sanctioned new row is `sub_002C5300,0x2c5300,0x2c5320,0x20`, preserving the owner |
| `0x2c5358` residual | **113 misses**: 112 from `0x2d3828`, one from `0x23e364`. All captured a1=0 / slot0=slot1=0. Correct predicate returns 1 for status 0, the same nonzero branch sense as its stale missing value. Exact return is still wrong; this is not evidence that this sibling is the first branch-changing wall |
| Storage interpretation | Actual GetInfo/Sync already return present/formatted-card success and complete. The no-card message alone cannot promote a storage/SIF/CD/input dependency; first restore the demonstrated predicate entry under a new brief |

[Residual join](e11a-residual-join.json), [ELF predicates](residual-predicates-dis.txt),
[caller](residual-caller-full-dis.txt), [UI helper](residual-ui-helper-dis.txt),
[vtable words](residual-vtable-words.txt), [actual source/binding manifest](residual-source-manifest.json).

| End-of-boot liveness / residual | Receipt |
|---|---|
| Query coverage | Zero `0x2c5140` misses; all **1,976** other missing markers parse completely. Earlier unrelated gaps remain tabled in [progress.json](e11a-progress.json) |
| EE/scheduler | Main ready at `0x423dc8`, RA `0x377b6c`; T5 running at semaphore wrapper, RA `0x382ae8`; T3 waits on sem30, T4 sem31; no claim that ordinary semaphore waits identify a storage wall |
| GS | 1,838 copy events; rendering and display continue through tick1875 |
| Function trace | **7,147,862 lines**, 1,171 distinct entries; balanced entries/exits, mismatch=0 and final stack empty |

## 9. Commits, retention, commands and limits

| Repository | Commit / disposition |
|---|---|
| Fork `ssx3` | **`ffdf58c4ee3b95bc6dd8779a0baeed0b23afe19b`**, “SSX3: restore the exact card busy-query entry”; pushed to `fork` (`brad-richardson/PS2Recomp`) only |
| Named fork files | `games/ssx3/ssx3-functions.sweep.csv`, `ps2xRuntime/include/ps2_e7.h`, `ps2xRuntime/src/lib/ps2_runtime.cpp`; one CSV row plus 74 lines of bounded read-only card observations |
| Generated runner files | Installed but **never staged**. Registry remains the sole tracked generated modification; active compiled checkpoint retained in `/tmp/p1-link` |
| Evidence | `[E11]` commit with `Orchestrated-By: Muse Code`; no ssx3 push. [Exact commands](COMMANDS.md) include the mutation/boot distinction and read-only reruns |

The single canonical capture retention maps **31 original files to 23 contents**,
9,873,825 retained bytes, verifying hashes before raw removal. [Manifest](e11a-retained.json).
The larger closed byte-cap count includes metadata sidecars, while that
retention total is payload only. All miners, including the pixel and request
joins, reran from retained copies. Scratch was cleaned after installed-copy
verification. The active checkpoint and DerivedData were untouched by reclamation.
Identical source snapshots use local relative aliases; closed generator/build/link
logs are compressed. [Evidence retention](evidence-retention.json) records each
alias and uncompressed hash.

| Limit / qualification | Parking |
|---|---|
| New missing predicate changes a branch by static join | The next boot should observe its call/return, slot status and UI+0x344 store directly. E11 did not attribute all later message selection to a single branch. |
| Other absent predicates remain | Restore only the named first divergence next; do not stack `0x2c5358` or other entries into that repair. |
| Frame coverage | Four Present samples at the boundary; no tick602 Present sample was emitted. Five copy packets are independently joined. |
| Log tail | Boot ends with exact runtime literal `[run] exiting loop` (no final newline), normal rc=0; syscall/function tails are complete. Missing markers all parse; E7 truncation flags all zero. |
| Resource floor | Internal free dipped during build, as explicitly recorded in §3; the generator's admission/interval and all boot caps passed. |

## 10. Tail receipt

| Completion marker | Value |
|---|---|
| E7 sink | `# E7 COMPLETE tick=604 events=13632 bootBytes=1361411 boundaryBytes=34990 packetBytes=8480 bootTruncated=0 boundaryTruncated=0 packetTruncated=0` |
| Actual-binding regression | `E11 ACTUAL BINDING TEST COMPLETE success=1 boot=0` |
| Reproduced joins | `# E11 JOIN TAIL COMPLETE` |
| Raw tails | [e11a-raw-tails.txt](e11a-raw-tails.txt); exact end-of-loop literal, complete trace lines, empty function stack |
| Selected outcome | **(ii)** only: repaired busy query advances; next predicate entry parked |
| Ownership / scope close | One boot used; lease released; APFS scratch absent; fork pushed; no ssx3 push; no second repair. Standing no-regen resumes. |

**E11 REPORT TAIL COMPLETE — tables, hypothesis, one next action; no menu claim.**
