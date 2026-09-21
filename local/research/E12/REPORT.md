# E12 — exact card predicate restored; remaining low-bit consumer parked

| Selected outcome | Forcing receipts | One next action |
|---|---|---|
| **(ii): `0x2c5300` restored; remaining `0x2c5358` result changes a reached UI flag calculation.** | Actual generated binding passes 14 predicate cases; both observed calls return 0 for status 0. Caller proceeds beyond `0x242158`, and its UI+0x344 clear does not occur. Later, raw line9061 / E7 seq5092 records missing `0x2c5358`, stale v0=`0x2c5358`, status0=0. Reached consumer `0x241c48` uses the low bit, producing flag bit3=8 instead of the guest-required 0. | Separately authorize the single `0x2c5358` entry repair and direct flag/state probes in [NEXT-BRIEF.md](NEXT-BRIEF.md). No second entry was repaired here. |

The displayed no-card message is unchanged. The copy/source/D/Present join is
complete; no menu or storage/input dependency is inferred from that image.
E11's limited same-nonzero-branch comparison does not cover the newly joined
low-bit consumer. The flag-word consequence below is explicitly code-derived;
the missing input and subsequent function-call path are directly observed.

## 1. Contract and scope

| Item | Record |
|---|---|
| Start / budget | 2026-09-21 09:39:09 UTC; eight-hour deadline17:39:09 UTC |
| Read-in | Latest pull already up to date; E12 brief and all E11 REPORT/NEXT-BRIEF read |
| Hypothesis | One exact-PC CSV row restores `status[port] == -10002`; correct return permits the caller's next checks |
| Alternatives / stop | Checkpoint, admission, generation or binding failure → (iii); correct caller advance with a remaining result/guest wall → (ii); advance without a demonstrated wall → (i). One boot only; no stacked repair |
| Authorized mutation | Row `sub_002C5300,0x2c5300,0x2c5320,0x20`, plus bounded observation taps. Owner preserved; `0x2c5358` stays OUT |
| Exception close | Standing no-regen resumes on E12 close. No adb, new HLE, raster/Present change, or additional boot |

The [upfront contract](CONTRACT.md) records every admission, allocation, wall,
progress and ownership bound before execution. [COMMANDS.md](COMMANDS.md)
separates the executed mutation sequence from read-only reproduction.

## 2. Checkpoint identity and fail-before

| Check before CSV mutation | Receipt |
|---|---|
| Fork baseline | `ffdf58c4ee3b95bc6dd8779a0baeed0b23afe19b` |
| Complete generated mirror | **9,450** names and hashes equal E11's checkpoint; no DROP or busy-query generation repeated as a separate phase |
| Registry | `68217e9a308cd7aaa540a1cac4115e9f9021b3e984b2a7e6b1e3250639be8907` |
| Runner | 163,437,088 B; `c39e59a7f202436e8a70c1f9f4373e7b577b71b1191c6912ecc8ad2cfd0f2c96` |
| Test binary | 5,624,840 B; `3ccf369fc01ce8d3e02fae6a7e4f8597c2b3fdb1ec1cc3051b91005562e68573` |
| Regressions | Suite **452/0**; E11's actual query four cases and guest DROP handler pass |
| Fresh baseline fixture | Relinked against baseline runner objects, not a handwritten predicate. SHA `1f153899ba209738fb955b5f6791df38aceed902fa89752cdc7d86c4d8d7571c`; link rc0 |
| Fail-before | `hasFunction(0x2c5300)=false`; absent mode rc0; expected-present mode **rc1**. Query four and DROP pass before the deliberate presence failure |

[Checkpoint](checkpoint.json), [identity audit](checkpoint-identity.json),
[before manifest](before/manifest.json), [baseline absent](checkpoint-predicate-absent.txt),
[expected-present failure](checkpoint-predicate-present.txt), [fixture](e12_binding_test.cpp).

## 3. Fresh admission and bounded reclamation

| Requirement / sample | Bytes / disposition |
|---|---|
| Generation admission | 1 GiB reservation +2 GiB floor +256 MiB guard = **3,489,660,928** |
| Reclamation stop target | Admission +512 MiB = **4,026,531,840**; never lowered |
| Fresh post-fail-before sample | **1,114,849,280**, insufficient; CSV still untouched |
| Persisted sample before edit | **4,185,862,144** |
| Immediate sample at edit | **4,187,017,216**, 09:50:55.138939Z |
| Immediate sample before spawn | **4,186,906,624**, 09:50:55.355198Z |

| Oldest retired tree removed | Allocated B | Free before → after | Proof |
|---|---:|---:|---|
| `/private/tmp/t1-link` | 1,764,282,368 | 1,108,041,728 → 2,875,265,024 | UID/type/CMake identity, live board, no handles; rechecked before removal |
| `/private/tmp/t5-link` | 1,316,732,928 | 2,866,221,056 → 4,185,989,120 | Independent proof; target reached, reclamation stopped before CSV edit |
| `/private/tmp/t5-base-link` | 1,721,241,600 | 1,304,944,640 → 3,029,413,888 | Later build-time space regression; new board/handle proof |
| `/private/tmp/t5-rule-link` | 1,714,913,280 | 3,026,452,480 → 4,744,593,408 | Next oldest retired tree; fresh4,744,540,160 ≥target, stopped |

All per-tree `lsof +D` checks and immediate rechecks returned1 with no handles.
Live T38/I16/G17 board/pane receipts were retained; their paths were not
removed. **`/tmp/p1-link` and DerivedData were protected.** Total removed
allocation: **6,517,170,176 B**. [Ledger](reclamation-ledger.json),
[inventory](reclamation-inventory.json), and each `reclaim-*-proof.json` /
`reclaim-*-removal.json` contain the ownership evidence.

| Resource interval | Observed bound |
|---|---|
| Generation | 2.291 s, normal rc0; 266,714,625 logical /286,588,928 allocated B, below1 GiB/1.25 GiB caps; free after3,894,194,176 B |
| Baseline link | 137.452 s; minimum sampled internal free1,172,250,624 B |
| Rebuild `-j4` | 597.716 s, rc0; minimum sampled internal free1,294,913,536 B |
| Entry fixture link | 224.614 s, rc0; minimum sampled internal free4,720,320,512 B |
| Build/link floor | Separately declared **1 GiB**; all samples above it. The generator's higher floor did not apply to this separate interval and was not lowered |
| Tool temporaries | Owned E12 SSD TMPDIRs, peak2,097,152 B each, below8 GiB cap; cleaned |
| APFS scratch | All9,451 emitted source/header hashes matched installed copies before cleanup; owned scratch removed **before build**. Before/after df and retained-copy manifest in [scratch-cleanup.json](scratch-cleanup.json) |

## 4. One row, generation and installation

| Link | Receipt |
|---|---|
| Raw ELF | Eight instructions `0x2c5300..0x2c531c`, including JR delay-slot `sltiu`; [raw disassembly](predicate-raw-dis.txt) |
| CSV diff | Exactly one row after `sub_002C52D8`; owner and busy query preserved. Result SHA **`41024f83a9e95408a48dbb91336db52b88f0b6fc7335a91eb6719479679f363d`**, matching E11 prediction |
| Inputs | ELF `1b49d05c…`; generator `51179179…`; canonical TOML unchanged `2f2ae543…`. Full hashes and exact argv in [generation record](entry-generation.json) |
| Used config | Derived canonical TOML changes only `general.output` to owned APFS scratch; historical P1 CSV remains unused |
| Generator | **One invocation**, normal rc0; complete9,452-file output manifest includes the owner marker |
| Scope audit | New predicate body; changed existing header and registry only; no deleted names. Owner, query and DROP body bytes unchanged; sibling absent |
| Installation | **3 changed /9,448 unchanged**, no leftovers; 33,470,714 logical B copied without metadata; three proven-created sidecars removed |
| Mirror allocation | 9,950,986,240 →9,952,034,816 B; within declared allocation-growth cap |
| Exact binding | Registry slot464062 → `sub_002C5300_0x2c5300`; new registry SHA **`4fb59437942fd0b2bc1a9a3fd18a5fa4610d1867e4f2959d80a7c67db9f2bb21`** |

[Scope audit](generation-scope-audit.json), [installation](entry-installation.json),
[after manifest](after/manifest.json), [bindings](after/binding-targets.json).

| Measurement correction | Disposition |
|---|---|
| An added output assertion rejected any `dispatchGuestBranch` token | Generator had already exited0 with complete manifests. The generated leaf contains a conditional **Return** diagnostic for raw `JR $ra`, not an API call |
| Narrowed verifier | Forbids DirectCall/IndirectCall/stub calls, allows the single diagnostic Return; replayed against all9,452 unchanged output hashes **before installation** |
| Scope | No regeneration retry, generated-byte edit, handwritten predicate or second emulator fix. [Original assertion and correction](verifier-correction.json), [replay](verifier-replay.txt) |

## 5. Actual-binding truth table and regressions

| Selected status | Other status | Port0 v0 | Port1 v0 |
|---:|---:|---:|---:|
| -10002 | 0 | 1 | 1 |
| 0 | 0 | 0 | 0 |
| 1 | 0 | 0 | 0 |
| -10001 | 0 | 0 | 0 |
| -7 | 0 | 0 | 0 |
| 0 | -10002 | 0 | 0 |
| -10002 | -10002 | 1 | 1 |

| Check | Receipt |
|---|---|
| Actual symbol | `_Z21sub_002C5300_0x2c5300PhP12R5900ContextP10PS2Runtime`; `hasFunction=1`; sibling5358=0 |
| All14 predicate cases | Supplied RA=`0xf00000`, SP=`0x100000`; GPR16–23/28–31 full128-bit preservation; whole32 MiB RAM unchanged; GetInfo/Sync calls0 |
| Busy-query four cases | `(state,outstanding)=(0,0)→0`, `(1,0)/(0,1)/(1,1)→1`; same preservation checks, GetInfo0 |
| DROP | Actual `sub_00426230`, empty buffer →v0=0, supplied RA, unchanged SP/s0; never TODO/HLE |
| Suite | **452/0** at checkpoint, after rebuild, and fresh pre-boot |
| New runner | 163,437,168 B; **`97b8dc25fe315eb7b68a9fd83879fb4d9ef2a9ab1a71dd1283f724846220260c`** |
| New test binary | 5,624,840 B; `cfdbf44635af5402b49d8623169e2d16677a59841b2a80dc9ca9eac81b7573f5` |
| Relinked fixture | 165,082,208 B; `9589a4aa7a7b0ca96e9d621e144e2183291027f15d3d5d7fc511d749ea2c6a97`; rc0 |

[Full regression output](entry-binding-present.txt), [entry preflight](entry-preflight.json),
[exact link argv](entry-binding-link.json), [build identity](entry-build.json).

## 6. Single guarded boot and progression arc

| Preclaim / ownership | Receipt |
|---|---|
| Fresh T13 shape | Lease absent; `pgrep -x ps2EntryRunner` rc1 and immediate recheck; pinned new binaries; ISO3,005,415,424 B; both ELF copies3,890,784 B with expected SHA; SSD/internal df; waits tails |
| Green checks | Trace-align selftest ALL PASS; suite452/0 immediately before claim |
| Lease | Claim10:15:59.068675Z → process end10:17:14.512023Z → release10:17:14.558066Z; release precedes analysis; post-release pgrep1 |
| First binding cap | Wall guard at75.326 s; SIGTERM; normal rc0 at75.443 s, below90 s declared wall; no SIGKILL |
| Progress | **97,283** closed syscall lines <1,000,000 |
| Bytes after shutdown | **436,859,320 logical /488,636,416 allocated** <1,610,612,736 aggregate caps; all per-group caps pass |
| Taps | REPORT_ALL=1, E7/E4; no truncated E7 sinks; same-run constructor/UI/singleton guards |

[Fresh preflight](e12a-preflight.json), [environment/caps](e12a-config.json),
[result](e12a-result.json), [closed caps](e12a-closed-caps.json), [liveness](e12a-liveness.txt).

| Phase | Direct observation / joined consequence |
|---|---|
| Tick80 object guards | Constructor PC`0x2c3fc4`, seq853: **MC=`0xb851a0`**, `[MC]=0x486f78`. UI-pointer PC`0x23d5c8`, seq866: **UI=`0xb84a50`**, `[UI+0x434]=MC`, guard1 |
| Tick118 request/query | Query return at`0x2c44b0`: four calls overall give0/1/0/0, including outstanding1→1; state3 request path reaches GetInfo; UI+0x338 clears atseq1752 |
| Tick118 repaired caller | seq1760: PC`0x242110` writes **UI+0x344=1**. Predicate seq1761→1762: source`0x242150`, original a0=MC/a1=0, status0=0, returnv0=0 at`0x242158`, SP unchanged |
| Caller path beyond repair | Function lines2891569–2891668 include predicate→next checks (`0x2c67a8`, `0x2d3928`, `0x2c53b0`) and continuation work; raw line5058's PC ring corroborates those exact targets. **No PC`0x2421b4` clear** anywhere in the complete tick≤603 tap |
| Subsequent tick118 request | seq1769 calls`0x2c48c0` from`0x2c44c0`; seq1771 calls`0x2c50e0` from`0x2c4980` with state3; seq1775 calls GetInfo from`0x2c5110`. These ordered events follow the repaired caller |
| Tick223→225 | Pending request setsUI+0x338; Sync completes; pending clears atseq5087. Predicate seq5090→5091 from`0x2d37f8` again returns0, original a0/a1 preserved in observations |
| Tick225 remaining result | seq5092 / raw line9061: missing`0x2d3828→0x2c5358`, a0=MC,a1=0,status0=0,stalev0=`0x2c5358`,policy1. Reached UI flag consumer described in §8 |
| Full captured request series | **321/321** query calls/returns, every observed truth/RA/SP join correct; GetInfo **12** returns0; Sync **15** returns1. No unclosed calls or unmatched returns |
| Later liveness | GS copies3,543; main/T5 continue scheduling (7,100/7,075). Shutdown main waitssem29, T4sem31, T5sem32; ordinary waits are not a storage diagnosis |

[Card joins](e12a-card.json), [ordered requests](e12a-request-join.json),
[caller/residual receipts](e12a-residual-receipts.txt), [progression](e12a-progress.json).
Both live predicate calls used port0; both ports were exercised in the fixture.
The UI+0x424 observations are retained separately and are not asserted to be
an executed port1 predicate path.

## 7. Packet/source → GS → D → field-Present

| Guard / edge | Receipt |
|---|---|
| Graphics singleton | One global`0x4a289c` store →S=`0x61ba60`; no teardown-null store |
| Field guard | 561 continuous increments; M=1/G=0; 560 post-initial snapshots `(A,B,P,D)=(0,112,0,112)` |
| Copy packet | Five identical1,696 B packets, source`0x4ffcc0`; SHA`79f3582fce45dc36a25c454003206a43bbfd001c340a92459a8726fbd0512e31`; FNV64`767aae0fde3c567f`; mask0/queued0 |
| DMA→GS seq pairs | tick599 **13324→13326**;600 **13389→13391**;601 **13454→13456**;602 **13519→13521**;603 **13584→13586** |
| Packet/source | FRAME D112, TEX0 source block0/width8, 17 sprites; E4 first17 draws D112, following production P0. Arm-source VRAM independently predicts freeze D |
| Full content | D **26,085 nonblack**; all512×448 RGBA pixels predicted exactly. 228,418 copied pixels,958 uncovered border pixels measured black; final sprite decoded separately |
| Boundary VRAM | Arm=freeze SHA`006f4d93f8bfb5cda2c194d95f36c71847d36a171c4f17c1a0c7a0405dfa2fad`; byte-identical to E11's measured surface |
| Present | display/source112/112,fallback0; all **five** observed fields match: odd`96a6875d`,even`0d4ede7d`; PMODE`ff21`,SMODE2=1,DISPFB1=`9070` |
| Host upload | Full PNG equals D's expected even field; RGBA SHA`83de822714ae8e857034b6187f89107af0c8201456476ba453e9457c7986fbe0` |

[Copy joins](e12a-join.json), [per-sprite content proof](e12a-copy-content-join.json),
[field calculation](e12a-frame.json). Viewed [source PNG](source-arm-428d0abfed9a84ee0564e176319c6989536ffb7516700c020c4b45d9e76600c7.png)
and [display PNG](display-d593db2e727744c4ace7e9eb7ca091387e118f2c04612e5c5091f8ed23561aff.png):
“No memory card (PS2) inserted” remains. Wrapping/clipping is retained.
The initial uniform-offset comparison still reports two final-row differences;
the full per-sprite model gives zero. This is a content join against the
captured runtime, not a hardware raster-conformance claim.

## 8. Remaining wall and challenged premise

| Link | Evidence / qualification |
|---|---|
| Sibling remains absent | Registry empty for`0x2c5358`; **113** complete misses:112 from`0x2d3828`,one from`0x23e364`; every captured a1=0/status0=0 |
| Required exact result | ELF`0x2c5358..0x2c53ac` returns1 for status0. Runtime policy1 preserves observed stale even value`0x2c5358`; wrapper`0x2d3810` restores RA/SP without normalizing v0 |
| Reached low-bit consumer | MC vtable+`0x1a8/0x1ac`→wrapper`0x2d3810`; caller`0x241c3c`; raw line9061 ring includes`0x23e540→0x241cd8→0x241b20` and ends`0x2d3810`. Same-run tapseq5092 pins arguments/status/SP |
| Exact wrong bit | `0x241c48 xori v0,1`;`0x241c4c andi v0,1`;`0x241c58 sll v0,3`: **stale→8; correct1→0**. Old bit3 is cleared first, so this contribution is not hidden by an earlier flag |
| Downstream state path | `0x241d10` stores flags toUI+0x43c; function trace reaches`0x23e608→0x23eb50→0x23cdb0`. ELF`0x23eb54` sets state argument4. Flag word and state argument are **code-derived**, not new direct taps |
| Scope | Named missing entry is a demonstrated exact-result gap. No second repair, no attribution of all later pixels to this one bit, and no menu claim |

[Residual join](e12a-residual-join.json), [complete raw/function receipts](e12a-residual-receipts.txt),
[predicate ELF](predicates-raw-dis.txt), [flag ELF](ui-flags-dis.txt),
[selector ELF](ui-select-rest-dis.txt), [state4 ELF](ui-exit-dis.txt),
[actual generated source/binding pins](residual-source-manifest.json).

| Challenged premise | Corrected scope |
|---|---|
| E11's missing sibling has the same nonzero branch sense, so it need not be first | That comparison holds for boolean branches only. The reached **low-bit** consumer distinguishes stale even`0x2c5358` from exact1, forcing a different flag. `0x2c5358` becomes the next named repair candidate, not an automatically authorized fix |
| Owner-labelled function trace implies entry at the owner's start | Some existing aliases have `switch(ctx->pc)` prologues: e.g.`0x2c67a8→sub_002C63E8` and`0x2d3810→sub_002D2988`. Their exact switch arms exist; no owner-entry bug inferred from log names |
| Unchanged no-card screen proves missing storage/input | GetInfo/Sync completion is observed; a wrong guest-visible predicate result is demonstrated first. No storage/SIF/CD/input promotion follows |

## 9. Commits, retention and limits

| Repository / artifact | Disposition |
|---|---|
| Fork commit | **`9da21ff8aeb9529368b32d91b0eec6a82ba79344`**, “SSX3: restore the exact card status predicate”; pushed to **fork** `ssx3` only; remote SHA matched |
| Named fork files | Canonical CSV, `ps2xRuntime/include/ps2_e7.h`, `ps2xRuntime/src/lib/ps2_runtime.cpp`; row + original-a1/predicate/UI-store observations only |
| Generated sources | Installed and rebuilt; **never staged**. Tracked generated registry remains modified. Existing untracked `ps2_log.txt` left untouched |
| Evidence | Standalone E12 manifests, miners, fixtures, complete capture tails and canonical retained contents; `[E12]` commit with required trailer; no ssx3 push |
| Capture retention | **28 original files →21 canonical contents,16,277,160 retained B**. [Manifest](e12a-retained.json) verifies every raw hash before removal; [retention receipt](e12a-retention.txt). Miners rerun against retained copies |
| APFS / lease | Owned scratch absent; active checkpoint retained; lease released immediately; one boot used |

[Reproduction](reproduction.json) records all six miners succeeding and all
seven joined outputs remaining byte-identical. Closed build/generator/link
logs are compressed; duplicate source/config/image snapshots use relative
aliases within E12, recorded in [evidence-retention.json](evidence-retention.json).

| Limit / gap | Parking |
|---|---|
| Generic stdout watch interleaving |146 damaged watch lines outside the E4 boundary; boundary damaged count0. Required card/field series come from the separately ordered, complete E7 sink. No all-stdout completeness claim |
| Missing-target coverage | All3,678 markers parse, damaged0. Earlier unrelated misses remain in progression table, without a new causal promotion |
| Function trace |11,254,916 lines,1,172 distinct entries, mismatch0, empty final stack |
| Direct next-state values | UI+0x43c and state-handler argument not tapped in E12. The next brief requires direct observations in addition to the ELF/function-trace join |
| Boot tail | Normal rc0 and exact `[run] exiting loop` literal without final newline; syscall/function tails complete. This known literal is not a truncated capture |
| Source/tool receipts | Full exact link commands are file-backed to avoid truncating their many object arguments. Generated verifier correction is retained explicitly |

## 10. Tail receipt

| Completion marker | Value |
|---|---|
| E7 sink | `# E7 COMPLETE tick=604 events=13640 bootBytes=1375294 boundaryBytes=34990 packetBytes=8480 bootTruncated=0 boundaryTruncated=0 packetTruncated=0` |
| Binding regression | `E12 ACTUAL BINDING TEST COMPLETE success=1 boot=0` |
| Content join | `# E12 JOIN TAIL COMPLETE` |
| Remaining wall | `# E12 RESIDUAL JOIN TAIL COMPLETE`; stale8 versus guest0 at reached low-bit consumer |
| Raw tails | [e12a-raw-tails.txt](e12a-raw-tails.txt), complete and untruncated |
| Selected outcome | **(ii)** only; one next action in NEXT-BRIEF, not executed |
| Close | One boot; lease released; scratch cleaned; fork pushed; no ssx3 push; standing no-regen resumed |

**E12 REPORT TAIL COMPLETE — tables, hypothesis, one next action; no menu claim.**
