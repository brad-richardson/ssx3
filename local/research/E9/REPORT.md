# E9 — DROP applied; regeneration preflight stopped at allocation cap

Selected outcome **(iii)**: the DROP-only generation hit its declared allocated-byte
cap before producing the new binding table. The active generated runner was never
replaced. The query repair and verification boot were not attempted. This is an
output-storage budget failure, not evidence of a new emulator or guest wall.

The ONE next action is the bounded preflight repair in [NEXT-BRIEF.md](NEXT-BRIEF.md):
generate the unchanged DROP inputs into an APFS scratch directory, complete the
actual-binding check, then resume the pending query-entry recipe under renewed
regeneration authorization. E9's regeneration exception closes with this report.

## 1. Contract and ownership

The upfront [CONTRACT.md](CONTRACT.md) was written before edits, tests or generation.
Start 2026-09-21 06:14:54 UTC; deadline 12:14:54 UTC. Required E8 REPORT/NEXT-BRIEF,
P13b selector/ledger record and frontier DROP decision at 634dbd5 were read first.

| Hypothesis / observable | Alternative / stop | Observed selection |
|---|---|---|
| Removing the 0x426230 selector retains guest translation rather than the TODO HLE. Full suite and actual baseline binding establish the pre-generation state; generated binding must be checked again. | Failed/incomplete DROP regeneration preflight → (iii), stop before query repair. | Suite and baseline behavior observed; regenerated binding unavailable because the output cap bound. |
| A map entry at 0x2c5140 restores its emitted busy-query body. Actual entry test must fail before and satisfy both nonzero truth-table cases after. | Entry failure → (iii), no handwritten replacement. | Actual baseline absence and expected failure recorded. Map entry and pass-after tests not attempted. |
| One guarded boot observes returned query value, intended request advance and the full copy join. | Remaining wall → (ii); demonstrated advance → (i); missing observation → (iii). | No boot; no new dynamic progression or pixel claims. |

| Ownership / budget | Receipt |
|---|---|
| Fork baseline | 4acc59ffebc99561ea2b4fe8e1aa1bebbc3075f2 |
| Fork mutation | Only `games/ssx3/ssx3.toml`, one selector line removed. Used P1 config receives the same removal. No HLE, runtime, CSV or generated runner mutation. |
| Runtime builds / boots | No runtime build; 0 of 2 boots. One isolated test translation unit was compiled and linked against existing runner objects. No `PS2Runtime::initialize()`, ELF load, GUI or scheduler run; only test RAM is initialized. |
| Lease | Never claimed; runner/generator pgrep each exit 1 at closure; lease absent. No waits or e9-waits.log needed. |
| Generation caps | 1200 s wall, 16 MiB log, 12 GiB allocated output, 2 GiB SSD free-space floor; 1 s polls. Recorded before invocation in e9_regen.py / drop-regen.json. |
| Broader temporary allocation contract | 30 GiB additional; the narrower output cap bound first. The 12 GiB reservation was undersized because it omitted the second allocation per output file. |
| Boot caps | Planned wall/progress/byte caps remain in CONTRACT.md; never activated because no boot was admitted. |
| SSD discipline | COPYFILE_DISABLE=1 recorded; native output still acquired provenance sidecars. No adb, upstream push or ssx3 push. |

## 2. Inputs and DROP

`before/manifest.json` pins binaries and inputs. `before/generated.json` pins all
9,276 active generated files (262,405,581 logical bytes; 9,768,534,016 allocated).
The exact active registry is retained compressed, with a binding listing and the
target owner sources. `after.json`, `after-binaries.json` and
`active-unchanged.json` prove the active output remained unchanged.

| Input | Before → after / use |
|---|---|
| Canonical TOML | `4974423573dd7db9…` → `2f2ae5432b91f873…`; remove only `_sceSifCmdIntrHdlr@0x00426230` (181 → 180 selectors). Full hashes in drop.json. |
| P1 used TOML | `d97cf95300273e2b…` → `5a5fa6f64600f511…`; same selector-only edit. |
| Actual E9 generation config | drop-used.toml, `ed781f7f01c08349ff668a60941a9e7868f833cdff03806e7dc7d9ee7debd03e`; canonical post-DROP config with only output path changed to P1/e9-codegen. |
| Canonical CSV | `b9aae74782fde6ba54671cfe07a9887c0af8ba1aad9d5befc1095e8cfef146ca`; unchanged, includes P9. No 0x2c5140 entry added. |
| P1 historical CSV | Preserved in before/used.csv; it predates P9 and was **not** the generation input. E9's derived config points directly at the canonical CSV. |
| ELF | 3,890,784 bytes; `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc`. |
| Generator | I10 pinned tool, 1,567,240 bytes; `511791795c16649e69706725c412408acc8d35fda68c4d83a3229eae6bda0763`. Recompiler/analyzer source diff b6252bb..4acc59f is empty; generator.json records reuse. |

The generator reported 9 internal output workers. This was its existing behavior;
no generator implementation or build setting was changed.

## 3. Pre-generation behavior receipts

The isolated fixture links the **actual runner object files and generated registry**
using the runner's existing Ninja link command. Only the executable entry symbol
changes to `e9_binding_main`. `lookupFunction(0x426230)` retrieves the real table
binding; the query is never replaced. Exact compile/link argv are retained in
before-binding-link.json.

| Check | Receipt |
|---|---|
| Full suite after config DROP | 452 total / 452 passed / 0 failed; drop-suite.txt, exit 0. |
| Actual handler binding | `_Z21sub_004261F0_0x4261f0PhP12R5900ContextP10PS2Runtime`, resolved by dladdr on the looked-up pointer. |
| Empty command-buffer fixture | `[0x52bcd8]=0x210000`, first buffer byte zero; entry PC=0x426230, supplied RA=0xf00000, SP=0x100000. |
| Handler behavior | Returns PC=0xf00000, SP=0x100000, v0=0, s0 low 64 bits preserved; no TODO trap. before-binding-test.txt ends with the complete success receipt. This proves this handler path, not live SIF0 delivery. |
| Query absence | Actual `hasFunction(0x2c5140)=false`. Expected-absent test exits 0; expected-present invocation exits 1 with `query entry presence differs` (query-fail-before.txt/json). |
| Test executable | 162,958,896 bytes; `fb0a48beb584104deb2288c995aa446bbe4e8c30969b3d20db98a33da7c3765b`. |
| Fixture setup repairs | Two compile attempts preceded execution: corrected PCH argument forwarding, then parenthesized pointer arguments for existing register macros. Both logs retained. No runtime or guest logic changed. |

| Required after-repair query case | Expected v0 | E9 observation |
|---|---:|---|
| state=0, outstanding=0 | 0 | Not run; entry repair not attempted. |
| state=1, outstanding=0 | 1 | Not run. |
| state=0, outstanding=1 | 1 | Not run. |
| state=1, outstanding=1 | 1 | Not run (additional planned case). |

The fixture contains the planned RA/SP, 128-bit callee-save, whole 32 MiB RAM and
GetInfo-call checks. Their presence in source is **not** a pass-after receipt.

## 4. First binding cap and preflight decision

| Step | Observed receipt |
|---|---|
| Start | 06:32:23.578854 UTC; e9_regen.py drop, canonical CSV unchanged. |
| Parse / translation | 9,446 functions extracted; 401,444 resumable entries across 7,609 owners; translation pass completed. |
| Header | Generated guest declaration `sub_00426230_0x426230` at header line 9336; no 0x2c5140 declaration. Header retained as drop-partial-functions.h.gz. |
| Output phase | SIGTERM at the first observed allocated-output cap, 61.431478 s; child rc=-15. No binding table or 0x426230 body emitted before termination. |
| New active output | None: the installer is after the success assertion, so it never ran. All 9,276 active generated hashes rechecked with zero drift. |

| Partial output class | Files | Logical bytes | Allocated bytes |
|---|---:|---:|---:|
| Generated sources/header | 6,151 | 164,487,378 | 6,458,179,584 |
| AppleDouble sidecars | 6,151 | 25,194,496 | 6,449,790,976 |
| Total | 12,302 | 189,681,874 | 12,907,970,560 |
| Declared output cap | — | — | 12,884,901,888 |

The observed overshoot was 23,068,672 bytes (22 MiB) within one polling interval;
termination followed that first observation. The sample source is 18,715 logical
bytes but occupies 1 MiB; its 4,096-byte sidecar also occupies 1 MiB and records
`com.apple.provenance`. See sidecar-sample.json/bin. COPYFILE_DISABLE=1 did not
prevent this native metadata allocation. No live cap increase or retry followed.

| Decision branch | Selection |
|---|---|
| Regenerated handler binding and behavior available, suite green → entry repair | Not selected: new registry absent. |
| Regeneration/preflight incomplete → exact failure and repair recipe, stop | **Selected (iii)**: undersized allocated-output reservation. |

This does not falsify the DROP's translation hypothesis. It prevents the required
regenerated binding/behavior observation. No remaining guest wall is newly named.

## 5. Retention, commits and closure

Every partial output and sidecar was SHA256-verified against
drop-partial-output.json before removing the E9-owned scratch directory. The
complete hash/size/allocation manifest, header, sample sidecar and complete log
remain. Cleanup removed 12,907,970,560 allocated bytes; no active generated files
were removed. cleanup.json and closure.json record cleanup and free space.

| Commit / artifact | State |
|---|---|
| Fork commit | `be0c9eeaa337d9685e9536fa4f66c5ce5029aad8` — one canonical selector deletion. Pushed normally to `fork/ssx3`; ls-remote confirms the same SHA. |
| Fork remote | https://github.com/brad-richardson/PS2Recomp.git; no upstream push. |
| Generated staging | None. Pre-existing modified register_functions.cpp remains byte-identical and unstaged. |
| Used config | P1/ssx3.toml carries the same DROP; before/after copies and full hashes retained here. |
| Active runner | 161,313,936 bytes; unchanged SHA `4f02b144a8de09622f66aa81533097d5b7777eaf63ffab3abe80f8e73fafa290`. |
| Active tests | 5,624,728 bytes; unchanged SHA `9a93097032fd668084c96a6d25caa158a2ce9349ae8a788baf0d701e094f52bf`. |
| Runtime/frame guards | No new boot or frame. E8 binary identity is preserved; no fresh packet/GS/VRAM/Present join is claimed. |
| Final ownership | pgrep runner=1, generator=1; lease absent. No ssx3 push. |
| Evidence commit | This report and its standalone receipts are committed with `[E9]` and `Orchestrated-By: Muse Code`; SHA supplied in handoff. |

## 6. Exact commands and gaps

All SSD steps used `export COPYFILE_DISABLE=1`. The scripts preserve structured
argv and hashes rather than relying on shell quoting for long commands.

```sh
python3 -B local/research/E9/e9_manifest.py before
# Remove the exact selector line from canonical games/ssx3/ssx3.toml
# and P1/ssx3.toml; drop.json records both exact deltas.
/tmp/p1-link/runtime/ps2xTest/ps2x_tests
python3 -B local/research/E9/e9_link_test.py before
cd /tmp/e9-binding-before
./binding-test absent
./binding-test present  # expected rc=1: fail-before receipt
cd /Users/bradrichardson/dev/ssx3
python3 -B local/research/E9/e9_regen.py drop
# rc=1 in driver after bounded child SIGTERM; no installation follows.
# Verify every partial file against its manifest, then remove only P1/e9-codegen.
git -C "$R" add -- games/ssx3/ssx3.toml
git -C "$R" commit -m '[E9] Drop the unimplemented SIF command handler selector' \
  -m 'Preserve translated guest code at 0x426230 on regeneration. E9 stopped at the bounded generation preflight; the query entry and active generated runner are unchanged.' \
  -m 'Orchestrated-By: Muse Code'
git -C "$R" push fork HEAD:refs/heads/ssx3
git -C "$R" ls-remote fork refs/heads/ssx3
```

Remaining gaps: complete regenerated handler binding/behavior; query map repair
and pass-after truth table; guarded dynamic a0/constructor/UI join; returned
port-selection value and intended request advance; verification boot and copy
guard. No storage, SIF/CD, input, raster or Present work is promoted.

**Tail receipt — E9 COMPLETE:** outcome (iii), one DROP-only generation stopped
at its allocation cap, partial output retained by complete manifest and cleaned,
active generated sources/binaries unchanged, fork DROP pushed, 0 boots, no lease
held, ONE next action in NEXT-BRIEF.md. Standing no-regen resumes now.
