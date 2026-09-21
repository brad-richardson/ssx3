# E13 — exact `0x2c5358` leaf and downstream flag/state join

**Finding: outcome (ii).** The exact leaf is restored; the live flag/state
path advances through state 6 and state 29. The first demonstrated remaining
wall is the MPEG picture wait with no input. No second gap was changed.
No menu or new meaningful-frame claim follows.
Brief: `local/muse/prompts/E13.md`; preceding E12 REPORT/NEXT-BRIEF read in
full. Tables, hypothesis and one next action. Start 10:39:04Z on 2026-09-21;
deadline 18:39:04Z. The bounded regeneration exception covers this entry only.
The upfront [contract](CONTRACT.md) records alternatives, stop conditions and
wall/progress/logical/allocated-byte bounds.

## 1. Checkpoint and fail-before

| Check | Recorded result / receipt |
|---|---|
| Fork baseline | `9da21ff8aeb9529368b32d91b0eec6a82ba79344`; prior repairs reused |
| Complete generated mirror | All 9,451 names and SHA256s match E12; `checkpoint-identity.json`, `before/generated.json`, standalone `expected-generated.json` |
| Registry | `4fb59437942fd0b2bc1a9a3fd18a5fa4610d1867e4f2959d80a7c67db9f2bb21` |
| Runner |163,437,168 B; `97b8dc25fe315eb7b68a9fd83879fb4d9ef2a9ab1a71dd1283f724846220260c` |
| Test binary |5,624,840 B; `cfdbf44635af5402b49d8623169e2d16677a59841b2a80dc9ca9eac81b7573f5` |
| Baseline suite |452 tests, 0 failures; `checkpoint-suite.txt` |
| Prior actual-binding fixture |Predicate5300 fourteen cases, busy query4, guest DROP; rc0 in `checkpoint-prior-binding.txt` |
| Fresh E13 relink |Actual unchanged runner objects and registry; complete compiler/linker argv in `baseline-binding-link.json`;196.768 s, rc0, bounded temp cleaned |
| Absent mode |`hasFunction(0x2c5358)=false`; rc0; full `baseline-binding-absent.txt` |
| Expected-present mode |Same actual binding absent; rc1; full `baseline-binding-present.txt`. Failure before admission/edit recorded at10:52:33.899305Z |
| Reached consumer |Actual registered interior entry`0x241c48`, handler`sub_00241B20`: stale`0x2c5358` contributes bit3=8, flags`0x1b`. Test stop hook only at the following virtual call; whole RAM unchanged |

`checkpoint.json` and `baseline-binding-results.json` preserve return codes
and executable identity. No earlier generation was repeated. Existing dirty
generated registry and untracked fork `ps2_log.txt` were retained unstaged.

## 2. Ordered admission and independent row

| Sample | Internal free B | Required B | Reading |
|---|---:|---:|---|
| After fail-before, before edit10:53:10.886257Z |4,464,640,000 |3,489,660,928 |Also exceeds4,026,531,840 B reclamation headroom target; no trees reclaimed |
| Immediately at edit10:53:23.100083Z |4,471,070,720 |3,489,660,928 |Persisted before CSV write |
| Immediately before spawn10:53:35.283748Z |4,470,349,824 |3,489,660,928 |Persisted before generator process |

| Derivation / independent cross-check | Receipt |
|---|---|
| ELF and emitted owner |22 raw words in`0x2c5358..0x2c53ac`,20 emitted annotations; omitted words at`0x2c5388/0x2c53ac` are zero NOPs. Owner SHA`f4e2e4a9541d8f360ba038cc691253e85c6c313a6fb9c0587ad5e8bc0fce3b21`; `row-derivation.json`, `leaf-raw-dis.txt` |
| Exact row |`sub_002C5358,0x2c5358,0x2c53b0,0x58` plus LF, after unchanged owner5338 and before53B0 |
| Before CSV SHA |`41024f83a9e95408a48dbb91336db52b88f0b6fc7335a91eb6719479679f363d` |
| Expected / actual after SHA |Both`0c6085744ab1a2afd60170a18ac261db02472441fa1d343ffd6756026e92d9f4`; exact one-line diff, `leaf-map-edit.json` |
| I17 independent row |At10:59Z, I17 commit`32d37e794fd87635a559e9baa85fa554f143393b` has byte-identical row. Derived locally before this comparison; no copying |
| I17 full-CSV delta |Five device-only rows at14f2a8,156750,243a80,395730,3a0158; no fork-only rows. Full hashes and bytes in `i17-row-crosscheck.json`; excluded from this change |

## 3. Regeneration and installation

| Check | Result / receipt |
|---|---|
| Inputs |Unchanged canonical TOML`2f2ae543…`, ELF`1b49d05c…`, generator`51179179…`; only derived`general.output` changed. Full hashes/argv in `entry-generation.json`; DROP selector remains absent |
| Generator |Normal rc0 in3.869392 s; owned APFS `/tmp/ssx3-e13-leaf-codegen` |
| Output |9,453 files including ownership marker;266,721,062 logical B;286,597,120 allocated B; all below declared caps; complete `entry-output.json` |
| Scope audit |One new body`sub_002C5358_0x2c5358.cpp`; two changed existing files: registry/header. Query5140, predicate5300, both owners and guest DROP unchanged; `generation-scope-audit.json` |
| Binding |Exact PC 5358 binds new generated leaf; no handwritten body, new HLE or API call. Prior exact bindings retained; `entry-bindings.json`; registry SHA `98753bfad809d7b54fdbef1c41cc6757724bcbfee9f957f3f89219a39da69e59` |
| Install |3 changed files,9,449 unchanged,0 leftovers;33,474,793 B copied without metadata; only three proven-created sidecars removed |
| Allocated mirror |9,952,034,816→9,953,083,392 B; growth1,048,576 B |
| Scratch cleanup |All 9,452 installed generated hashes checked, scratch removed; internal free4,473,466,880 B afterward; `scratch-cleanup.json` includes df before/after and retained manifest |
| Observations |Bounded existing E7 sink extended for wrapper/caller returns, UI+43c/440 old/new, UI+130/b8/748 state/route, original arguments. Only reads/logging; `handwritten.patch`, `observation-install.json` |

## 4. Actual-binding regressions

| Build / resource check | Recorded result |
|---|---|
| Rebuild |`cmake --build /tmp/p1-link/runtime --target ps2EntryRunner ps2x_tests -j4`; rc0 in626.045 s; full `entry-build-bounded-result.json` |
| Internal free-space dip |A recorded fall from about4.45 GB to1.31 GB during compilation; minimum sampled free 1,301,712,896 B, above unchanged1,073,741,824 B build floor. Cause not inferred |
| Retired-tree proof |Fresh lane snapshot, peer pane reads, completed T6/T12 gate records, same-user/cache identity, and no live handles (`lsof +D` rc1/empty) per tree; board/handles rechecked before removal |
| Oldest-first reclamation |`t6-link`: free1,309,057,024→3,084,447,744 B; then `t12-link`:3,081,031,680→4,848,902,144 B. Stop once4,026,531,840 B target met; `reclamation-ledger.json` |
| Protected trees |`/tmp/p1-link/runtime` retained; DerivedData untouched; remaining retired trees untouched |
| Temporary ownership |Build temp allocated2,097,152 B, cleaned after normal exit; bounds never lowered |

| Regression | Result / full receipt |
|---|---|
| New fixture link |Actual rebuilt runner objects and exact registry; `entry-binding-link.json`, bounded rc0 |
| Leaf, ports0 and1 |Each port: -10001,-7,-5,-4,-3,-2,-1,0→exact1; -10002,-8,-6,1→exact0. Contradictory unselected-port status in every case;24/24 |
| Preservation |Every leaf case returns to suppliedRA`0xf00000`, SP`0x100000` unchanged, callee-save GPRs16–23,28–31 preserve all128 bits, whole32 MiB RAM unchanged; zero GetInfo/Sync calls |
| Actual consumer |Registered`0x241c48` executes the generated calculation. Stale`0x2c5358`→flags`0x1b`/bit3=8; actual status0 leaf result1→flags`0x13`/bit3=0, separately for both ports. Unrelated flag bits and RAM preserved;3 checks |
| Regression guards |Predicate5300 fourteen cases + busyquery4 + guest DROP handler, all pass |
| Full suite |452 tests, 0 failures; `entry-suite.txt` |
| Executable fixture |SHA`804cb918ee585acc8f5615b1dc50a98f1dc379214971ef6634868e90dcaeb866`; `entry-preflight.json`, `entry-binding.txt`, `entry-validation-results.json` |


## 5. One guarded boot

| Pre-claim / execution | Receipt |
|---|---|
| Fork / binaries |`83fb4d60904abb016522c477cce704c52118f95f`; runner163,437,488 B, SHA`b2099130a366940fb0fa3d273a8bebc7d3ac28618cf0ceac1c743f90939fbbf6`; test5,624,840 B, SHA`cbcddc01b860f9d3478492fd92501fb0e536372c0b633aac9be8e4f81f71ec87` |
| Fresh T13 checks |Lease absent; pgrep rc1 twice; exact binary hashes, ISO3,005,415,424 B and ELF3,890,784 B/sha checked; SSD+internal df, waits tails, tree status, aligner selftest ALL PASS; suite 452/0 again. `e13a-preflight.json` |
| Environment |REPORT_ALL=1; E7/E4 retained; singleton and candidate-field watches. Full argv/env/watch list in `e13a-config.json` |
| Three caps |90 s wall with 15 s stop reserve;1,000,000 syscall lines; per-group logical/allocated bounds and1.5 GiB aggregate in upfront contract/config |
| Lease |Claim11:14:31.659925Z; boot11:14:31.667593Z; SIGTERM11:15:46.863121Z at75.192 s; normal rc0; process ended11:15:47.115128Z; release11:15:47.122221Z, about 7 ms later |
| Closed totals |75.454803 s;54,775 syscall lines;150,679,825 logical B and195,035,136 allocated B, including metadata. All caps pass; `e13a-closed-caps.json` |
| Full raws |Boot9,724,311 B/23,201 lines; function127,771,154 B/3,628,352 lines; function stack balanced,0 mismatches;216 complete missing-target records,0 damaged |
| Stop |One boot used. Analysis ran after release. No second boot or runtime repair |

### 5a. Dynamic object, exact result, flag and state

| Link | Same-run forcing receipt |
|---|---|
| MC object |E7seq855 tick80, constructor`0x2c3fc4` writes`[0xb851a0]=0x486f78` |
| UI pointer |Seq868 tick80, store`0x23d5c8` gives UI=`0xb84a50`, `[UI+0x434]=MC`, guard1. Addresses re-derived in this run |
| Busy query |375 call/return pairs, supplied-RA/SP joins and `(state || outstanding)` truth all match;0 missing |
| Prior predicate5300 |8 live calls, port0/status0→exact0;0 missing |
| Repaired leaf5358 |142 call/return pairs:141 from`0x2d3828`,1 from`0x23e364`; all original port0/status0→exact1, preserved SP and supplied return PC. Vtable guard holds for every pair;0 missing |
| Wrapper |141 pairs at`0x2d3810`;6 nested within the reached flag calculation |
| First flag chain, tick225 |Leaf seq5502→5503 returns1 to`0x2d3830`; wrapper5501→5504 returns1 to`0x241c44`; calculator5498→5505 returns flags0 to`0x241cec`; store5506 at`0x241d10` writes UI+0x43c, old0→new0 |
| Repeated flag chain |6 complete leaf→wrapper→calculator→store joins, ticks225–230. Each calculator returns0; each UI+0x43c store is0→0. This is **not** a live8→0 clear; stale8 is the fail-before consumer result |
| State selection |Seq5508,`0x23e7e4→0x23cf38`, original a0=UI/a1=6; UI+0x748=`0x47cbd8`, route+0xc=`0x23cf38`; seq5521 at`0x23d3a0` writes UI+0x130 from3→6; seq5522 returns with state6 |
| Later state |Seq5742 tick229 at`0x23d54c`: UI+0x130 from6→29. The state4 route through`0x23eb68` is not taken in this run |
| Teardown |Tick248 seq6336 writes MC vtable`0x486f78→0x4871e8` at`0x2c402c`, followed by allocator writes. MC field interpretations stop before reuse |

Complete pairs, old/new stores and original arguments: `e13a-card.json`,
`e13a-join.json`, `e13a-card-events.json`. All 781 observed card calls have
matched exits; these joined exits also reach their guest return PCs.

### 5b. Graphics guard and explicit observation limits

| Link / challenged assumption | Observation |
|---|---|
| S guard |Singleton raw line229 gives S=`0x61ba60`;206 continuous counter calls, ticks41–248; M=1/G=0 throughout; A/B/P/D=`0/112/0/112` after first pick. Initial D=0 before that first pick is retained |
| CPU copy ingress→GS |206/206 copy DMA packets from`0x4ffcc0`, each1,696 B, match the following GS entry by byte count, FNV64 and order; mask0/queue0 throughout. Last copy at tick248; complete pairs in `e13a-copy-content-join.json` |
| Fixed late window |At ticks599–603 the copy source is already quiet. Zero retained copy-packet byte files. E4 history at600→601 has one Present and **zero draws**. The old five-copy boundary assumption is inapplicable |
| VRAM→Present |Arm/freeze identical, SHA`115c3df692c531ec93241d8190491c7e277c9f0f9d5a52f9abf3b257ab554476`; both P and D have0 nonblack RGB pixels. D RGBA SHA`7dfc7e9cf5415b3da1eaa152cddaaf889c279236c0198375061cab03b1f46f3c`; field-processed Present at600/601 and latest4435 match exactly, FNV32`fd889dc5`. Decoded black PNG viewed |
| Full early content join |Unavailable: the packet/source snapshot window was later than the completed copy phase. Early packet hash equality is not substituted for captured packet bytes plus source pixels. No early image progression or menu claim |
| E7 footer |Raw ends at seq6339/tick248 with a complete newline; no runtime COMPLETE footer. The footer is emitted only on a later `event(tick>603)`, not on shutdown. Source size is constant from15 s through termination |
| Closure audit |6,339 contiguous rows;1,042,729 B total, below4 MiB boot budget; largest possible event body549 B<768; all observed call pairs close, full function trace closes. `e13a-observation-closure.json` pins the unchanged raw, format bounds and source. No artificial footer added |
| Strict miner rejection |Initial E12-derived miner rejected the absent live-window footer. Those failure receipts remain; E13's closed-prefix reader now requires the explicit closure audit. No boot or runtime change was used to obtain these counts |
| Text interleaving |1 of6,647 stdout watch markers is damaged at raw4982/tick111; retained in `e13a-damaged-watch.json`, excluded. Dedicated E7 rows and600→601 Present records are intact; no guessed reconstruction |

## 6. First demonstrated remaining wall and one next action

| Link | Forcing receipt / limit |
|---|---|
| Actual request |Raw10381: `[MPEG:GetPicture] waiting for frames, mpeg=0x587b30 ended=0 failed=0 sawInput=0` |
| Caller→binding |ELF`0x3b1020` calls`0x402a10`, supplied RA`0x3b1028`; actual generated wrapper calls`ps2_stubs::sceMpegGetPicture`. Hot-PC count1/RA matches |
| Durable wait |Main thread waits on Mpeg at PC/RA`0x3b1028`;12 full late diagnostic blocks report0 schedules for main. Final park snapshot agrees. Thread4 continues its semaphore31 pump |
| Preceding registration |`0x402c08` reached once, RA`0x3b0f6c`; actual wrapper calls`sceMpegAddCallback`. Raw ELF fixes type1 and callback`0x3b0b10`, with userdata=s2. Direct original registration arguments remain the next probe's guard |
| Intended producer |Callback`0x3b0b10` reorders callback arguments, calls helper`0x3b0b40`; helper fetches/pads guest data and calls`0x4029d0`→`sceMpegAddBs` |
| Observed delivery |No hot-PC dispatch at callback 3b0b10, helper 3b0b40, or AddBs 4029d0. The JSON contains all 1,478 hot-PC entries (not the text report's top-30 subset); source pins prove the complete map serialization. Callback wrapper function-log count0. All three exact bindings exist |
| Owner-label caution |Function logger shows owner`sub_003B0B40` once, but hot-PC entry is its constructor alias`0x3b0c58`, not helper entry3b0b40. Do not miscount that as delivered callback data |
| Static runtime candidate |`MPEG.cpp` stores AddCallback as`stream=false`; the map's only selecting reader requires`callback.stream`. GetPicture parks on empty frames/not-ended/not-failed; AddBs would feed and wake. All map references and source hashes retained |
| Hypothesis |Missing non-stream type1 callback delivery leaves the guest's AddBs producer uninvoked before GetPicture waits. Confirm original args and callback ABI before implementation; no MPEG fix was attempted |
| Dependency boundary |Successful CD-read payloads occur nearby, but their buffers are not joined to MPEG input. No CD/SIF/storage/input repair is promoted from adjacency |

| Outcome | Selection and prescribed action |
|---|---|
| **(ii)** |Exact leaf and flag/state advance are observed; a remaining MPEG input delivery wall appears. **One next action:** the bounded MPEG type1 callback→AddBs→GetPicture request/delivery probe and actual-binding fixture in [NEXT-BRIEF.md](NEXT-BRIEF.md), with graphics capture aligned to the earlier state transition |

The remaining wall is named without claiming menu/content progression or
stacking a second fix. `e13a-residual-join.json`, complete raw receipts,
MPEG raw disassembly and pinned actual sources make the recipe reviewable.
Standing no-regen resumes at E13 close.

## 7. Commits, retention and gaps

| Artifact / disposition | Record |
|---|---|
| Fork |`83fb4d60904abb016522c477cce704c52118f95f`, pushed to fork `ssx3`; remote SHA verified. Named files: canonical CSV, `ps2_e7.h`, `ps2_runtime.cpp`. Plain commit; no upstream push |
| Generated sources |Never staged; tracked registry remains dirty, generated header/leaf remain ignored. After mirror has 9,452 names/hashes. Existing untracked fork `ps2_log.txt` preserved |
| Evidence |Standalone `local/research/E13/`; `[E13]` commit with required trailer; no ssx3 push |
| Canonical captures |25 retained records,150,589,713 original data B; closed raws compressed and duplicate content deduplicated after hash checks. The 90,112 B difference from closed logical total is owned metadata, not missing evidence |
| Reproduction |7 miners replayed retained captures; all 8 joined JSON outputs byte-identical; `reproduction.json` |
| Tests |Suite 452/0 at checkpoint, post-build and fresh pre-boot; actual leaf24, consumer3, predicate14/query4/DROP plus baseline expected-present failure |
| Limits |Runtime event footer absent for explained quiescence; early full packet/source content join not captured; one interleaved stdout watch excluded; callback registration original args not directly tapped. No assumption silently promoted to a receipt |
| Closeout | `closeout.json` pins final identities, generated mirror, process/lease state, storage and scratch cleanup; `evidence-retention.json` records verified compression/aliases |
| Exact commands |[COMMANDS.md](COMMANDS.md); full long compiler/linker/generator/boot argv in JSON |

**E13 REPORT TAIL COMPLETE — one entry, one regeneration, one boot;
remaining MPEG wall tabled; no second repair, no menu claim, no ssx3 push.**
