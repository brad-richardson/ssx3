# E14 — five I-lane rows verified; absorb stops at fresh APFS admission

**Outcome (iii): admission remains below the declared bound after the sole
eligible retired link tree is reclaimed.** All five rows verify and all five
fail-befores are recorded. No CSV edit, regeneration, installation, new fork
commit, or boot occurred. MPEG remains queued for E15.

Start 2026-09-21 11:51:36 UTC; eight-hour deadline 19:51:36 UTC. Latest pull
was already current. E14 brief and E13 REPORT read in full; E13's independent
I17 cross-check and the I11–I15 row tables were read. The upfront
[contract](CONTRACT.md) records hypotheses, alternatives, caps and stop rules.
Tables and one next action; no later-phase result is inferred.

## 1. Checkpoint identity and baseline regression

| Check | Receipt / observation |
|---|---|
| Fork baseline | `83fb4d60904abb016522c477cce704c52118f95f`, branch `ssx3`; no new fork commit |
| Complete generated mirror | All 9,452 names and hashes match E13; `checkpoint-identity.json`, `before/generated.json`, standalone `expected-generated.json` |
| Registry SHA256 | `98753bfad809d7b54fdbef1c41cc6757724bcbfee9f957f3f89219a39da69e59` |
| Runner | 163,437,488 B; SHA256 `b2099130a366940fb0fa3d273a8bebc7d3ac28618cf0ceac1c743f90939fbbf6` |
| Test executable | 5,624,840 B; SHA256 `cbcddc01b860f9d3478492fd92501fb0e536372c0b633aac9be8e4f81f71ec87` |
| Prior exact rows | 2c5300 and 2c5358 present exactly once in canonical CSV; neither re-added |
| Full suite | 452 tests, 0 failures; `checkpoint-suite.txt` |
| Prior actual-binding fixture | E13 fixture SHA256 `804cb918ee585acc8f5615b1dc50a98f1dc379214971ef6634868e90dcaeb866`; leaf 24, consumer 3, predicate 14, query 4 and DROP all pass; `checkpoint-prior-binding.txt` |
| Complete checkpoint record | `checkpoint.json`: identities, executable argv, return codes and case counts |
| Protected / foreign state | `/tmp/p1-link/runtime` retained; DerivedData untouched. Existing dirty generated registry and fork `ps2_log.txt` remain unstaged |

The suite and fixture execute isolated tests; they do not boot the guest ELF.
No earlier generation or repair was repeated.

## 2. Five fail-befores on the actual baseline binding

| PC | `check-absent` | `check-present` | Actual registry result |
|---|---:|---:|---|
| `0x14f2a8` | rc0 | rc1 | hasFunction=0, binding=null |
| `0x156750` | rc0 | rc1 | hasFunction=0, binding=null |
| `0x243a80` | rc0 | rc1 | hasFunction=0, binding=null |
| `0x395730` | rc0 | rc1 | hasFunction=0, binding=null |
| `0x3a0158` | rc0 | rc1 | hasFunction=0, binding=null |

| Fixture / bounds | Receipt |
|---|---|
| Fresh relink | Actual baseline runner objects and unchanged registry; `baseline-binding-link.json` retains complete compiler/linker/object argv; no substitute guest implementation |
| Result | rc0, 300.687051 s; `baseline-link-bounded-result.json`; 1,200 s wall / 15 s reserve, 8 GiB temporary allocation / 256 MiB guard, 1 GiB internal floor, 2 GiB SSD floor, log cap all respected |
| Temporary files | 4,230 logical B / 2,097,152 allocated B; owned SSD temporary directory removed after normal exit |
| Fail-before ordering | Finished at 12:02:05.933477 UTC, before fresh admission at 12:02:06.027938 UTC. Complete ten per-PC raw logs and `baseline-binding-results.json` retained |

## 3. Per-row byte and bound verification

| Origin | Exact row bytes, excluding final LF | Baseline owner | Guest bytes | Final return PC | Disposition |
|---|---|---|---:|---|---|
| I12 | `sub_0014F2A8,0x14f2a8,0x14f35c,0xb4` | `0x14f250` | 180 | `0x14f354` | Verified; no exclusion |
| I13 | `sub_00156750,0x156750,0x1567b8,0x68` | `0x1565c8` | 104 | `0x1567b0` | Verified; no exclusion |
| I14 | `sub_00243A80,0x243a80,0x243ab0,0x30` | `0x243a40` | 48 | `0x243aa8` | Verified; no exclusion |
| I11 | `sub_00395730,0x395730,0x395750,0x20` | `0x3956e8` | 32 | `0x395748` | Verified; no exclusion |
| I15 | `sub_003A0158,0x3a0158,0x3a0290,0x138` | `0x3a0048` | 312 | `0x3a0284` | Verified; no exclusion |

For every row, the complete baseline owner C++ bytes equal the originating
I-lane owner bytes. Within each authorized slice, every emitted instruction annotation in both
owners and the I-lane exact entry matches the raw ELF. Only zero-word NOPs may be absent
from annotations, and those omissions are explicitly listed. The I-lane
entry header matches the requested end-exclusive bounds; the final return
and delay slot lie within them. Each exact-entry hash also matches its
originating I11–I15 report prefix. No disagreements or exclusions occurred.

| PC | Raw guest-slice SHA256 | I-lane exact-entry SHA256 |
|---|---|---|
| `0x14f2a8` | `6ae422ab95a19211ffca40b21221879bcec853fa4643e61b7e7493d1800b9416` | `740bac80385858acf623cf39a1ecea3a18749576498c1f9fc69b7e67996d44d0` |
| `0x156750` | `a5a42d223056c683982bf26e5e8012cb3b3f504cdae0f34d5f4be8f0f2e1fcbb` | `aa6b35d8365a5dfb855b88d976f9d1bb561e46cc0f43b97cc00ff5985d8d3e7b` |
| `0x243a80` | `493badb9db16bea6507b456e80410d2dbb583db0163b508b867ae043c4e0a8ad` | `f75aeb026f7afa631461c155f316a1f0ef0d9327f076ff8446f4eb2b5d3f63dc` |
| `0x395730` | `2a856c6dacf875525e2e3578f3da76edb89f0c093b74a001e71e377fd5ae9027` | `8dbfb20852fd366285263b2b533ab6039e4f855bcbc5a44e648a3b5a748f7605` |
| `0x3a0158` | `a532adee27fd4e87fcb24602766e9a9a356a305c986a428acef3e30ee8ea486c` | `cbc6a2ad1695efd4d72617ff695de37aff1352c5c72fa997fa1c066ac92af89f` |

`row-verification.json` contains full source paths, both owner hashes, exact
row hex, NOP lists, return bounds and per-row reasons. `row-sources/` retains
all raw slices and compressed baseline/I-lane source bytes. The five
`I*-row-receipts.txt` files preserve the originating report rows with line
numbers. These checks ran independently of any CSV mutation.

| CSV prediction | SHA256 / observation |
|---|---|
| Actual unchanged canonical CSV | `0c6085744ab1a2afd60170a18ac261db02472441fa1d343ffd6756026e92d9f4` |
| Computed five-row result | `7c827add09aeea837e25f6048007ab91e65eb4b5f7a98f8fb4f448b606cfb9ba` |
| Independent I17 comparison | Computed result equals I17's recorded full CSV hash in `expected-i17-rows.json`; row bytes match all five named device-only rows |
| Actual after-edit match | Not reached: the admission stop precedes CSV mutation. The predicted hash is not presented as an installed result |

## 4. Fresh admission, reclamation and binding stop

| Sample / event | Free APFS B | Required / result |
|---|---:|---|
| Fresh sample after all five fail-befores, 12:02:06.027938 | 1,566,236,672 | Below 3,489,660,928 B; no CSV edit |
| Before scoped removal | 1,558,126,592 | Fresh ownership and handle recheck complete |
| Immediately after removal | 3,217,530,880 | Observed free-space increase 1,659,404,288 B |
| Fresh post-reclamation sample, 12:04:11.434666 | **3,217,489,920** | **Still below 3,489,660,928 B: stop** |
| Admission shortfall at stop | 272,171,008 B | Reservation/floor/guard unchanged |
| Reclamation target shortfall | 809,041,920 B | Target remains 4,026,531,840 B, including 512 MiB headroom |

| Per-tree proof / disposition | Receipt |
|---|---|
| Eligible inventory | Only unprotected `/private/tmp/t12-dev-link`; `/private/tmp/p1-link` is protected. Ownership UID and birth times in `reclamation-inventory.json` |
| Retired ownership | T12 completed gate plus T12 REPORT explicitly identify the dev tree; `retired-lane-receipts.txt`. Current lane board contains no T12 or matching path claim |
| Cache identity | CMake cache identifies `/tmp/t12-dev-link/runtime`, project PS2RetroX, canonical fork source; same user, no file symlinks observed |
| Handles | `lsof -nP +D /private/tmp/t12-dev-link` rc1, empty stdout/stderr; repeated immediately before removal |
| Size | 7,328 files; 1,637,050,728 logical B / 1,656,139,776 allocated B. Observed free-space delta is separately recorded; no claim that unrelated filesystem activity was absent |
| Board recheck | Pane/name/cwd identities unchanged immediately before removal; full snapshots retained |
| Removal | Only this proven-retired tree removed. It is the oldest and sole eligible tree; `reclaim-t12-dev-link-proof.json` and `reclaim-t12-dev-link-removal.json` |
| Remaining target | No eligible unprotected `/tmp/*-link` tree remains. The active checkpoint and DerivedData were not candidates |

This triggers E14 Task 1's explicit instruction: if admission is still short,
stop without CSV mutation or regeneration. `admission-before-edit-initial.json`,
`admission-after-reclamation.json` and `stop.json` preserve the order and exact
math. No lower guard or alternate output placement was substituted.

## 5. Phase disposition and one next action

| Phase | Recorded status |
|---|---|
| Checkpoint + baseline regressions | Completed |
| Five actual-binding fail-befores | Completed |
| Five per-row byte/bound checks | Completed; all five verify |
| Admission | Unmet after eligible reclamation; mandatory stop |
| CSV edit / generation / installation | 0 / 0 / 0 |
| New build / post-absorb regression | Not reached; only baseline fixture relink occurred |
| Fork commit / push | None; fork stays at `83fb4d60904abb016522c477cce704c52118f95f` |
| Verification boot / lease | 0 boots; lease never claimed; absent at closeout |
| MPEG / any second gap | Untouched; E15 remains queued |
| **Outcome (iii)** | Restore declared APFS admission, then resume the same verified absorb under renewed authorization; [exact continuation recipe](NEXT-BRIEF.md) |

There is no additional safe deletion target in the inspected eligible set.
The next action is a fresh admission after separately authorized reclamation
or external free-space recovery, with at least the recorded 809,041,920 B
headroom shortfall restored at that sample. New measurements govern; the
report does not reserve future free space. Do not reclaim the active build
or promote an arbitrary temporary directory to a retired target.

## 6. Retention, closeout and gaps

| Artifact / check | Record |
|---|---|
| Final identity | Before/after inputs, binary records, fork HEAD/status and all 9,452 generated records are identical; `closeout.json` |
| Scratch / process | E14 generation scratch never created; baseline link temporary children empty; `pgrep -x ps2EntryRunner` rc1; no lease held |
| Canonical evidence | Standalone `local/research/E14/`; compressed closed raw log and identical local snapshots aliased only after hash verification; `evidence-retention.json` |
| Unexecuted preparation | Draft later-phase adapters removed after stop; hashes/disposition in `unexecuted-adapters.json`. They are not evidence of execution |
| Exact commands | [COMMANDS.md](COMMANDS.md); compiler/linker argv and ten per-PC logs complete |
| Evidence commit | `[E14]` with `Orchestrated-By: Muse Code`; no main push |
| Gaps | Five entries remain absent in the active runtime. No post-absorb regression, new boot joins or guest-advance receipt exists because admission blocked those phases |

Standing no-regen resumes at this scope's close. The verified row set and
baseline fixture are ready for an admission-first continuation.

**E14 REPORT TAIL COMPLETE — five verified rows and five fail-befores;
admission stop before CSV edit; zero regeneration, fork commits or boots.**
