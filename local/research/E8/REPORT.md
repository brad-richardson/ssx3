# E8 — guest progression parks at an absent memory-card query entry

Exactly one outcome is selected: **(ii), a reached coverage hole requiring
work behind the existing regeneration gate**. The copy fix remains intact.
The guest reaches the memory-card-check screen and keeps rendering it;
no menu/interactive advance is claimed. The forcing edge is the unbound
guest busy query `0x2c5140`, reached from port selection and then from every
observed UI poll. E8 stops without a runtime fix or regeneration.

The next action is the scoped coverage brief in [NEXT-BRIEF.md](NEXT-BRIEF.md),
after the owning lane resolves the `0x426230` DROP prerequisite. Restoring
one query is not a promise of a menu: a second reached query hole is tabled.

## 1. Contract and baseline

E7 REPORT was read in full through its tail before work. The upfront
[CONTRACT.md](CONTRACT.md) records the survey; [BOOT2-CONTRACT.md](BOOT2-CONTRACT.md)
records the targeted observation before boot 2, with explicitly appended
corrections to its initial policy/entry-label assumptions.

| Hypothesis | Observable | Selection/action |
|---|---|---|
| Guest progresses beyond the copy join | Changed guest state and menu/interactive content, joined packet→source→D→Present | Not observed; (i) not selected |
| A specific emulator edge blocks progress | First causal guest predicate, its producer/consumer and runtime behavior | Missing `0x2c5140` query confirmed; this is generated entry coverage, so (ii) and the no-regen stop apply |
| A guest storage/input gate blocks progress | Named request/completion or input dependency | Not established; memory-card text alone does not promote SIF/CD/input |
| Observation is incomplete | Truncated causal window, missing tail, or unalignable records | Boot 2 repairs the survey's report-once visibility; complete causal records select (ii), not (iii) |

`W=/Volumes/Extreme SSD/ps2recomp-spike`, `R=$W/PS2Recomp`, branch `ssx3`.
Handover observed `2026-09-21 05:26:18Z`; deadline `11:26:18Z`. Two of four
permitted boots used. No build, behavioral source change, fork commit,
fork push, generated staging, regeneration, or adb operation in E8.

| Pinned input | Bytes | SHA256 / identity |
|---|---:|---|
| Fork HEAD | — | `4acc59ffebc99561ea2b4fe8e1aa1bebbc3075f2` |
| Runner `/tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner` | 161313936 | `4f02b144a8de09622f66aa81533097d5b7777eaf63ffab3abe80f8e73fafa290` |
| Tests `/tmp/p1-link/runtime/ps2xTest/ps2x_tests` | 5624728 | `9a93097032fd668084c96a6d25caa158a2ce9349ae8a788baf0d701e094f52bf` |
| Both P1 ELF copies | 3890784 | `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc` |
| ISO | 3005415424 | Size checked before both boots |
| Active generated binding file, preexisting modified file | 32658325 | `05836f4b155793834c82f37364bc3cb2d56f1a5dbf6b2c91f765a7493352bf3d` |

The generated binding file is separately pinned because it is the existing
unstaged modification, not a file supplied unchanged by the fork commit.
It was only read. Both preflights require exactly that existing fork-status
line and the pinned runner/test hashes.

## 2. Pre-claim, caps, termination and release

T13 §T13-0 pre-claim checks were repeated: lease absent; `pgrep -x
ps2EntryRunner` exit1; binary hash/size; ISO/ELF sizes and both ELF hashes;
SSD plus internal `df`; prior waits tails; trace-align selftest; fresh full
suite; immediate runner/lease recheck before atomic claim. See
`e8{a,b}-preflight.json`, `*-suite.txt`, `*-aligner.txt`, and `e8-waits.txt`.

| Check | E8a | E8b |
|---|---|---|
| Suite, run before claim | 452/452, exit0 | 452/452, exit0 |
| Trace aligner | selftest ALL PASS | selftest ALL PASS |
| SSD / internal free | 418Gi / 11Gi | 399Gi / 11Gi |
| Lease / runner | absent / pgrep exit1 | absent / pgrep exit1 |
| Waits | No occupied-lease wait | No occupied-lease wait |
| Diagnostic difference | Existing E7 taps; E4 ticks 6000→6001 | Same binary; `PS2X_DIAG_REPORT_ALL=1`; E4 ticks 600→601 |

| Cap class | E8a | E8b |
|---|---|---|
| Wall | 600s, TERM at 585s reserve | 60s, TERM at 45s reserve |
| Progress | 1000000 syscall lines | 1000000 syscall lines |
| Bytes | Boot 256MiB; trace96MiB; function1024MiB; E4 12MiB; E7 8MiB; frame/park32MiB each; aggregate1280MiB | Same limits |
| Safety guard | 8MiB below function/aggregate limits | min(8MiB, cap/4) below every byte limit |
| Poll / liveness | 250ms / 5s | 250ms / 5s |

| Capture/release receipt | E8a | E8b |
|---|---|---|
| Claim UTC | 05:29:51.934033 | 05:44:29.747702 |
| PID | 17638 | 26098 |
| E4 span complete at wall | 100.588994s | 23.387316s |
| First binding cap | Function-log byte guard at 182.179s | Wall guard at 45.162s |
| Syscall lines at bind | 588796 | 77961 |
| Bytes at bind: boot / trace / function | 52582024 / 35205979 / 1066437791 | 11750927 / 4663115 / 215048563 |
| Aggregate bytes at bind | 1164042336 | 241221313 |
| Closed boot / trace / function bytes | 52588530 / 35210106 / 1066559552 | 11755499 / 4665516 / 215112920 |
| Closed retained-input byte sum, including park output | 1164187318 | 241317260 |
| TERM UTC | 05:32:54.136067 | 05:45:14.916465 |
| Process end / exit code | 05:32:54.383360 / 0 | 05:45:15.039471 / 0 |
| Total boot wall | 182.448968s | 45.291680s |
| Lease released UTC | 05:32:54.395025 | 05:45:15.042953 |
| Post-release runner check | exit1 | exit1 |

Only the owned process was terminated. No active file was truncated and
no stream was discarded to extend a boot. Both leases were released before
analysis/compression; neither needed SIGKILL. All limits include the
termination reserve and remained unexceeded. Configs, liveness and result
JSON retain the complete per-category measurements.

## 3. Progression arc

| Phase | Guest/scheduler observations | Graphics/content observations |
|---|---|---|
| Boot and graphics setup | S factory store at 0x22697c selects S=0x61ba60 in both runs; first C increment at tick 41 | Fixed A/P=0, B/D=112 after initialization; M=1 |
| UI card request | E8b first missing busy query at boot-log line 5028; preceding C=75 at line 5010 joins the E7 tap's tick 117 | First observed wall belongs to the same card-check phase; not inferred from a new image |
| Early copy proof, ticks 599–603 | Main, display worker and semaphores continue; both runs retain complete ordered taps | 5/5 copy packets consumed in each run; D holds the same E7 message |
| E8a later boundary, ticks 6000→6001 | UI/card update continues; no new call-set phase | 138 production draws at P0 plus 17 copy draws at D112; VRAM equals E7c and E8b |
| E8a end, latest upload tick 10825 | t1/t4/t5 continue scheduling; steady stub distinct=222 in blocks2–35 | Same D content, field-processed Present exact |
| E8b targeted end, latest upload tick 1365 | 1249 UI polls attempt the missing busy query; no retirement through that branch | Same D and exact latest odd-field upload |

Counts below distinguish emitted-owner entries from logical target calls.
The function trace can re-enter an owner on a scheduler resume; the park
hot-PC tally counts resolved call dispatches and excludes missing targets.

| Progress signal | E8a | E8b |
|---|---:|---:|
| Full function-trace lines / distinct owners | 30024532 / 1073 | 6054164 / 1073 |
| Entry/exit stack mismatches / live stack at EOF | 0 / empty | 0 / empty |
| Display owner 0x382af0 entries | 10783 | 1323 |
| Copy-helper owner 0x371940 entries | 10783 | 1323 |
| Logical card update 0x2c55d8 resolved calls | 10709 | 1250 |
| UI update 0x23d660 resolved calls | 10708 | 1249 |
| Port selector0x2c4480 resolved calls | 2 | 2 |
| sceMcInit0x409940 resolved calls | 1 | 1 |
| Other resolved MC SDK targets 0x409940..0x40b028 | 0 | 0 |
| Owner 0x2c50e0 / state setter0x2c48c0 entries | 0 / 0 | 0 / 0 |
| GS kicks / GIF packets / DMA starts | 3324674 / 311246 / 397586 | 392072 / 36899 / 47571 |

E8a park: t1 Ready, scheduled 21591; t4 waits 31, scheduled 10785; t5
Running, scheduled 21566. t2 waits 26, t3 waits 30 and t6 waits 36. This is
continuing execution around a stable UI gate, not a demonstrated global
scheduler deadlock. The four unhandled boot RPC records are retained in
the progression receipts; no causal join promotes them. `drops=[]` is
not evidence of complete generated coverage, as §5 demonstrates.

## 4. Copy, content and Present join retained

The same-run singleton guard has exactly one nonnull store in each boot,
and no teardown-null observation. The bounded tap has C=1..561 without
gaps; all 561 snapshots show M=1/G=0; all 560 initialized pair snapshots
show A/B/P/D=0/112/0/112. No surprising field-value branch was selected.

| Join boundary | Forcing receipt |
|---|---|
| Guest source→copy packet | Source 0x4ffcc0, QWC 106, 1696 bytes; snapshot SHA256 `79f3582fce45dc36a25c454003206a43bbfd001c340a92459a8726fbd0512e31`; FRAME1 D112, TEX0 P0,17 sprite strips and FRAME2 suffix |
| Packet→GS | Both boots, each tick 599..603: one DMA record and one GS-entry record with the same 1696-byte FNV64 `0x767aae0fde3c567f`; mask 0, queued 0; ordered sequence IDs retained in `e8-join.txt` |
| GS operations→D | E8a late window:287 events,52 GIF tags,80 register writes,155 draws. E8b window:288 events, same GS census plus one host-present event. Both:138 draws P0,17 draws D112, one FRAME2 suffix |
| Source content→D pixels | P nonblack 12563; D nonblack 12358. Full RGB comparison equals P(x+1,y+1), black outside source:0 differing pixels. This records the existing sampled offset; no hardware-perfect raster claim |
| VRAM identity | Both E8 frozen snapshots equal E7c: SHA256 `532288fdaa9cf5e2aa43f628dd9975b4f7cdecf12ac8beac7fdd8897ac4c78e5` |
| D raw RGBA | SHA256 `4a7d98177597f60731c8b0ab5ce83f9c412f2d5f871c1f196526ef599b033243` |
| Present selection | PMODE0xff21, SMODE2=1, DISPFB1=0x9070; display/sourceFBP112, fallback0 |
| Even / odd fields | FNV32 `0xa9301e2d` / `0xf818f78d`, RGB nonblack 12398 /12318; all captured boundary uploads match their independently decoded field |
| Latest host pixels | Both runs: complete 512×448 odd-field RGBA match; PNG SHA256 `ba5fbce889b98081f286c16b2af92b1ffef2ee298745641cc8358508a7592576` |

E8a's five preserved host samples at about30/60/90/120/181s, ticks
1786/3600/5403/7218/10771, all match one of the two fields. The later VRAM
and uploads demonstrate persistence of the existing content. Full source
packet byte snapshots cover ticks 599–603; they are not claimed as new
packet snapshots at tick 6000 or at every later host upload.

## 5. First forced progression wall: busy query is not executed

Evidence: [e8b-missing-query.txt](e8b-missing-query.txt), complete compressed
boot log via `e8b-retained.json`, [e8-wall-dis.txt](e8-wall-dis.txt), and
[e8-runtime-policy.txt](e8-runtime-policy.txt). ELF instructions are
raw-word-verified against OUT annotations using the trusted EF decoder
copied into standalone `e8_static.py` (including correct R5900 SQ decoding).

| Edge / value | Captured or statically forced result |
|---|---|
| Card object MC / vtable VT | a0=0xb851a0; [a0]=0x486f78 in all 1251 query records |
| Busy-query pointer | ELF `[VT+0x5c]=[0x486fd4]=0x2c5140`; this-adjust field atVT+0x58=0 |
| Initial request source | 0x2c44a8→0x2c5140 twice, lines 5028–5029; RA 0x2c44b0 |
| UI poll source | 0x23d6a4→0x2c5140 1249 times, lines 5030–52724; RA 0x23d6ac; UI object s0=0xb84a50 |
| Query input state | MC+4=0 and port MC+0xc=0 in every record |
| Query output register before missing dispatch | v0=0x2c5140 in every record; not the query's boolean result |
| Actual runtime policy | policy 1=`ContinueToTarget`; it sets PC to target and returns true on a missing call, without executing target or changing v0 |
| Generated caller continuation | On true return, emitted JALR wrapper sets PC to its fallthrough; port selector0x2c44b0 and UI poll0x23d6ac then test the preserved nonzero v0 |
| Port-selection consequence | Branch0x2c44b0 takes 0x2c44cc, skipping the active-port write and state 3 request at 0x2c44c0→0x2c48c0→0x2c50e0→sceMcGetInfo |
| UI consequence | Branch0x23d6ac takes 0x23d798, skipping pending-flag clear0x23d6b4; repeated query records establish this recurring path |
| Background card update | Logical0x2c55d8 still runs. State 0's table word0x486350 selects0x2c6074; it never starts the skipped request |
| Intended query | `busy = ([MC+4] != 0 || [MC+0x40] != 0)`, return 0/1. MC+0x40 was not dynamically sampled; its initializer is zero, but pointer-alias completeness is not asserted |

The erroneous nonzero branch is forced by the captured register plus the
runtime/caller code; no after-return register tap is claimed. Its value
is an unexecuted function address, regardless of what the actual busy
predicate would have returned. Query/input storage semantics cannot be
evaluated faithfully until this entry can execute.

| Coverage check | Receipt / implication |
|---|---|
| Active table 0x2c5140 | No binding; live missing-target report confirms absence |
| Neighbor bindings | 0x2c50e0 and 0x2c5118 bind to sub_002C50E0; 0x2c55d8 correctly binds to sub_002C5570 |
| Emitted query body | Instructions 0x2c5140..0x2c5164 exist after the preceding routine's unconditional return, but no 0x2c5140 entry switch case or label exists |
| Table-only insertion | Insufficient: invoking that owner at 0x2c5140 takes its default entry 0x2c50e0, a different routine with a prologue and GetInfo call |
| Reached sibling residual | Missing 0x2c5358 from0x2d3828 occurs 1249 times; VT+0x1a4=0x48711c selects it. No fix is stacked or menu claim inferred |

The all-report boot contains 3834 missing-target markers,3834 fully parsed
records,0 damaged records. Other targets include 0x395730,0x14f2a8,
0x156750,0x243a80 and 0x3a0158; their exact source/count inventory is in
`e8b-progress.json`. These are retained residuals, not all declared causal
to this UI wall. The card query is the first named blocking predicate in
the observed card-check progression path, not the first missing target
anywhere in the boot.

## 6. Challenges, fix discipline and selected action

| Premise challenged | Receipt / corrected framing |
|---|---|
| A memory-card-check image names a storage failure | No: the guest's request is bypassed before GetInfo. Neither SIF/CD nor input is promoted |
| No hot-PC entry means no attempted query | False: missing targets return before the tally. Boot 2 directly records 1251 attempts |
| Empty park drops implies full coverage | False: missing generated calls use a separate reporter; E8a printed only its first missing target |
| Initial prep called policy 1 SkipCallDebug | Corrected: SkipCallDebug is 3; observed policy 1 is ContinueToTarget. The specific true-return/caller behavior still bypasses the absent query |
| Instructions present in OUT imply an entry label | Corrected by source inspection: query instructions exist, but its entry case/label and table binding do not |
| Restoring one busy query guarantees menu progress | Unsupported: MC+0x40 remains unsampled; sibling 0x2c5358 and other missing targets are reached; later storage semantics remain untested |
| The byte cap makes the causal capture truncated | No: planned termination closed both full traces with empty stacks; E4 windows and E7 completion tails are intact; all boot 2 missing records parse |

| Candidate action | E8 disposition | Required proving receipt |
|---|---|---|
| Runtime VIF/GS/Present change | No demonstrated new gap | Existing packet/content/field joins remain correct |
| Force query result / clear guest UI gate | Not a valid implementation | Would substitute guest behavior and hide actual query inputs |
| Generic entry-coverage repair | Behind explicit no-regen gate; selects (ii), recipe only | Exact-PC entry plus truth-table regression and a re-probe showing actual request/poll progression |
| SIF/CD/memory-card completion work | Not promoted | First reach and name an actual outstanding request/completion dependency |

**One next action:** route [NEXT-BRIEF.md](NEXT-BRIEF.md) to the
regeneration-gated coverage lane. It specifies the 0x426230 prerequisite,
the exact 0x2c5140 entry defect, fail-before/pass-after query truth table,
same-run object guards, candidate field addresses, request/poll acceptance
chain and the next-wall stop. No E8 fix or additional boot follows.

## 7. Commands, retention and reproducibility

Historical boot commands, executed once each after their contracts:

```sh
export COPYFILE_DISABLE=1
python3 -B local/research/E8/e8_capture.py a
python3 -B local/research/E8/e8_capture.py b --arm 600 --report-all --wall 60
```

The driver records exact argv, cwd, PS2X environment, watches and caps in
`e8{a,b}-config.json`. Each preflight runs `tools/trace_align.py --selftest`
and the pinned test binary from the fork. No build command was run.

Offline reproduction (no boot/build; writes only derived E8 receipts):

```sh
export COPYFILE_DISABLE=1
python3 -B local/research/E8/e8_mine.py a
python3 -B local/research/E8/e8_mine.py b
python3 -B local/research/E8/e8_frame.py a
python3 -B local/research/E8/e8_frame.py b
python3 -B local/research/E8/e8_progress.py a
python3 -B local/research/E8/e8_progress.py b
python3 -B local/research/E8/e8_wall.py
python3 -B local/research/E8/e8_join.py
```

`e8_retain.py a` and `b` ran lease-free: closed raw logs compressed, every
uncompressed SHA verified before its original was removed, manifests retain
all source names/sizes/hashes. Identical packet/PNG/snapshot payloads have
one canonical content copy; all 10 source packet snapshots resolve to one
1696-byte file. The unchanged VRAM resolves to the already committed E7
content-addressed gzip. That explicit canonical reference avoids another
4MiB raw copy; E8 scripts otherwise stand alone.

The raw function traces retain all 30024532/6054164 lines. Legacy console
watch interleaving affected 187/35 lines, all outside the respective E4
boundary; ordered E7 taps and the causal missing-query records are intact.
E7 taps finish with 12512 events each, bootTruncated=0,
boundaryTruncated=0, packetTruncated=0. Detailed frame JSON preserves the
raw-D versus field-Present distinction rather than declaring raw byte equality.

The final `e8_replay.py` audit verified all 38 distinct canonical payload
hashes and both cap envelopes, reran all 8 offline miner commands, and
required byte-identical reproduction of 19 derived receipts. See
`e8-replay.json` and the complete `e8-replay.txt` tail.

## 8. Repository disposition and limits

| Repository | Commit / status | Disposition |
|---|---|---|
| Fork baseline | `4acc59ffebc99561ea2b4fe8e1aa1bebbc3075f2` | Existing pushed E7 baseline; unchanged by E8 |
| New fork changes/commits | None | No fork push required; existing generated modification untouched/unstaged |
| ssx3 evidence | Enclosing `[E8]` commit | Trailer `Orchestrated-By: Muse Code`; no ssx3 push |

The existing AppleDouble pack-index warnings still appear on fork git
reads; no broad cleanup was performed. Counts and timing are diagnostic
observations, not hardware performance measurements: all-report logging
slows the second boot. No claim covers execution beyond either cap, a
numeric MC+0x40 value, alias-complete guest writers, a storage failure,
first menu content, or success after a future coverage repair.

---
**Tail receipt: E8 §§1–8 complete. Outcome (ii) only: absent 0x2c5140 busy
query is joined to the persistent UI wait. Two boots used, all caps held,
both leases released immediately, full traces closed with empty stacks.
Fresh suite 452/452 before each boot; five-of-five copy packets consumed
per boot; D nonblack 12358 and Present exact after field processing.
Boot 2 missing markers 3834/parsed 3834/damaged0; busy query 1251 attempts.
MC+0x40 unsampled and sibling 0x2c5358 retained as residuals. No runtime
fix, build, regeneration, generated staging, third boot, adb, fork change
or ssx3 push. One gated next-action recipe supplied.**
