# E10 — DROP preflight completed; query generation stopped at fresh APFS admission

Selected outcome **(iii)**. DROP-only regeneration finished normally on APFS,
was installed and rebuilt, and passed the 452-test suite plus the actual generated
handler test. The fresh resource check for query generation then rejected the
run. The query row was restored to its original absence. **Zero boots ran.**

The ONE next action is [NEXT-BRIEF.md](NEXT-BRIEF.md): admit a renewed bounded
query-entry brief with sufficient internal space, verify the completed DROP
checkpoint, then resume the sanctioned query repair and guarded boot. This is a
resource-admission failure; E10 has no new guest progression or wall observation.
E10's regeneration exception closes here; standing no-regen resumes.

## 1. Contract and scope

[CONTRACT.md](CONTRACT.md) records the hypotheses, observations, alternatives and
bounds before work. Start 2026-09-21 06:48:40 UTC; deadline 12:48:40 UTC. E9 REPORT
and NEXT-BRIEF were read in full. The last implementation attempt stopped at
07:27:10.768704 UTC; subsequent work only restored, retained and reported evidence.

| Hypothesis / observable | Alternative / stop | E10 observation |
|---|---|---|
| APFS output completes unchanged DROP generation without ExFAT allocation amplification. Normal exit, manifests, real binding, rebuild and behavior check. | Failed preflight → (iii), stop. | Complete: normal exit 0, installed manifest exact, suite 452/0, real handler returns normally. |
| One sanctioned map row restores query 0x2c5140. Actual binding fails before, then truth table and preservation checks pass after regeneration. | Entry/admission failure → (iii), stop without another fix. | Fresh admission failed before generator spawn. Row restored exactly. Actual query remains absent; no pass-after test. |
| One guarded boot observes query return, intended request and the complete display join. | First remaining wall → (ii); demonstrated advance → (i). | Not reached. No boot, query-object capture, request, image or menu claim. |

| Ownership / limits | Recorded handling |
|---|---|
| Fork | Baseline and final HEAD be0c9eeaa337d9685e9536fa4f66c5ce5029aad8. No new fork commit or push. The DROP config commit was already pushed in E9. |
| Tracked changes | Query CSV briefly received the authorized single row, then was restored byte-for-byte after admission failure. No handwritten runtime/header, HLE or generator source edit was installed. |
| Generated mirror | DROP output installed locally. Generated sources never staged. register_functions.cpp remains modified/unstaged, as before E10, with its new bytes pinned separately. Ignored generated bodies/headers follow the same owning-lane rule. |
| Builds/tests | Runtime/test build -j4; isolated actual-binding test linked from the rebuilt runner objects. No ELF load, GUI or scheduler boot in that fixture. |
| Boots/lease | 0 of 2 boots; lease never claimed; no waits. At closure pgrep -x ps2EntryRunner exits 1 and lease is absent. T13 boot pre-claim checks were never invoked because no boot was admitted. |
| SSD/APFS | COPYFILE_DISABLE=1 on SSD steps. Only the named APFS scratch was used for generation; removed after retention. No adb, ssx3 push or upstream push. |

## 2. Inputs, complete output and installation

`before/manifest.json`, `before/generated.json`, `drop-admission.json` and
`drop-output.json` pin the inputs and output. `after/manifest.json` and
`after/generated.json` pin the restored final checkpoint. `final-generated-audit.json`
compares every emitted source/header name and SHA to the active mirror.

| Input | SHA-256 / identity |
|---|---|
| Canonical post-DROP TOML | 2f2ae5432b91f873f053045cfa29d9c1d4e3d8e5a941f5693eea720f26daaf1c |
| P1 used TOML | 5a5fa6f64600f51168ad34832845d2a979ee8e15196b6a1b753bbf60b479a60c; also excludes the selector. |
| Actual derived DROP TOML | a7152674d036704b0692a4ad353695b9114c93a0a6da075644ff1316ce707e42; only general.output differs from canonical. |
| Canonical CSV | b9aae74782fde6ba54671cfe07a9887c0af8ba1aad9d5befc1095e8cfef146ca; includes P9. Historical P1 CSV is preserved but not selected. |
| ELF | 3,890,784 bytes; 1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc |
| Pinned generator | 1,567,240 bytes; 511791795c16649e69706725c412408acc8d35fda68c4d83a3229eae6bda0763. Recompiler/analyzer source diff b6252bb..HEAD is empty. |

| Output / installation | Forcing receipt |
|---|---|
| Normal completion | drop-generation.json: exit 0, 2.253264333 s. Native log ends with registry/header/output summary. 9,446 functions and 401,444 resumable entries across 7,609 owners. |
| Complete manifest | 9,447 C++ files including registry, 2 headers, plus 122-byte ownership marker. Total 9,450 files / 266,708,892 logical B / 286,580,736 allocated B. |
| Manifest coverage correction | E9's 9,276-file manifest covered C++ only; its script looked for generated headers under include, but these two headers live in src/runner. E10's initial complete manifest includes them: 9,278 files / 263,199,906 logical B. Existing C++/binary hashes still matched E9. This corrects coverage, not source content. |
| Name disposition | One obsolete sub_0042C1F0_0x42c1f0.cpp wrapper removed after preserving it. Old/new registries both bind unchanged named InitSystemCallTableAddress_0x42c1f0_0x42c1f0; no emitted reference to obsolete symbol. Exact hash/reason in drop-installation.json. |
| Bytes copied | 174 changed files: 172 new bodies plus registry and function header; 9,275 unchanged. 36,946,883 bytes copied with copyfile, without metadata-copy operations. |
| Sidecar repair | Native writes nevertheless created 174 provenance AppleDouble companions, proven to match E10's changed names. First build's source glob attempted to compile them. Removed only those companions (182,452,224 allocated B), then rebuilt successfully. Full first-attempt raw is compressed; cleanup manifest retained. No generated C++ bytes were changed to repair this installation artifact. |
| Final mirror | 9,449 sources/headers, 266,708,770 logical B, 9,949,937,664 allocated B. Exact emitted-name/hash equality; zero sidecars in the audited runner source directory. |
| Binding | Registry SHA 5d4ce8c47d9e5238c67ffa5830c43466e4e9f03b2c1adf0bbd3d9028a79c4ad1. Slot 825482 at 0x426230 binds sub_00426230_0x426230, whose retained body has no selector/TODO HLE call. 0x2c5140 and sibling 0x2c5358 remain absent. |

| Resource bound fixed before generation | Recorded amount / result |
|---|---|
| Admission | 1 GiB logical reservation + 2 GiB free floor + 256 MiB guard = 3,489,660,928 B. Initial free 5,965,844,480 B; after DROP generation 5,672,869,888 B. |
| Output | 1 GiB logical / 1.25 GiB allocated; stop 128 MiB before either cap. Completed output is below both guards. |
| Wall/log | 1,200 s with 15 s reserve; 16 MiB log with 1 MiB reserve; 0.25 s polls. Generation ended normally before any guard. |
| Mirror | 24 GiB allocated-growth cap with 256 MiB guard and 2 GiB SSD floor. Final growth over initial mirror is 179,306,496 B after created-sidecar removal. |
| Boot bounds | Planned wall/progress/byte limits remain in CONTRACT.md and the prepared capture driver; no lease or capture activated them. |

## 3. Actual generated binding and query baseline

The isolated fixture uses the actual rebuilt runner object files and registry,
with executable entry changed to e10_binding_main. `lookupFunction` obtains the
real handler pointer; `dladdr` records its emitted symbol. Exact compile/link argv
are in `drop-binding-link.json`. No handwritten handler or query is substituted.

| Check | Observation |
|---|---|
| Full suite | 452 total / 452 passed / 0 failed, exit 0; drop-suite.txt. |
| Actual DROP binding | _Z21sub_00426230_0x426230PhP12R5900ContextP10PS2Runtime |
| Empty-buffer fixture | [0x52bcd8]=0x210000; first buffer byte zero. Entry PC=0x426230; supplied RA=0xf00000; SP=0x100000. |
| Handler result | PC=0xf00000, SP=0x100000, v0=0, s0 low 64 bits preserved; normal return. This tests the empty-buffer path, not live SIF0 delivery. |
| Query fail-before | Actual hasFunction(0x2c5140)=false. Expected-absent invocation exits 0 with complete success tail; expected-present exits 1 with query-entry-presence failure. |
| Fixture executable | 165,065,200 B; 6fe978804cd63cbac35155d40b623eb73e1eecbd939ca9ddacf1b4fa258736d4. Retained on SSD at P1/e10-binding-tests/drop/binding-test. |
| DROP checkpoint runner | 163,436,912 B; f5eeea20f661666f045d90da14acbde49a6349056d055c3fd0efcc34568c7f1f. Final active path /tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner. |
| Test binary | 5,624,728 B; 9a93097032fd668084c96a6d25caa158a2ce9349ae8a788baf0d701e094f52bf. |

`query-raw-dis.txt` revalidates the ELF: load state at +4, return 1 if nonzero;
otherwise load outstanding at +0x40, return 1 if nonzero, else 0. Both returns
use supplied RA, with v0 assigned in the delay slot. This static truth table is
not a pass-after execution receipt.

| Query case | Required v0 | E10 after-repair execution |
|---|---:|---|
| state=0, outstanding=0 | 0 | Not run; no entry generated. |
| state=1, outstanding=0 | 1 | Not run. |
| state=0, outstanding=1 | 1 | Not run. |
| state=1, outstanding=1 | 1 | Not run (additional prepared case). |

The fixture contains RA/SP, relevant 128-bit callee-save, whole-RAM and zero
GetInfo-call assertions. Their presence is not evidence those query checks ran.
Prepared card/capture/miner scripts were not installed or boot-validated.

## 4. Exact stop and restoration

| Event | Receipt / implication |
|---|---|
| Closed E9 fixture cleanup | Removed only the obsolete E9 isolated-test executable/object/log after matching the recorded executable SHA. closed-e9-test-cleanup.json records all three files and free space 3,018,752,000→3,182,592,000 B. E9 source/link receipts remain retained. |
| Closed-checkpoint reclamation | All 9,449 DROP scratch source/header hashes verified against installed copies, then redundant scratch files removed: 286,576,640 allocated B. Verified runner temporarily retained on SSD, freeing 163,438,592 allocated B internally. drop-checkpoint-reclamation.json records names and before/after df. |
| Earlier free reading | Reclamation's post-checkpoint reading was 5,608,226,816 B. It did not reserve that capacity for later use. |
| Map insertion | Authorized row inserted at line 5087, preserving existing owner. Temporary CSV SHA c17db90b72db490772a649eb64b91487d54d1602b258be2e3205e2e7b039c6aa. query-map-edit.json records exact neighbors. |
| Fresh admission failure | At 07:27:10.768704 UTC: free=3,240,579,072 B, required=3,489,660,928 B, shortfall=249,081,856 B. entry-admission-failure.json and entry-admission-console.txt preserve the values and stopped command sequence. No cause is assigned to the intervening filesystem free-space change. |
| Stop location | e10_generate.py asserted before deriving entry-used.toml or spawning the generator. set -e prevented entry installation, observer installation and build. Empty entry-generation-driver.txt is explained by the assertion preceding stdout output. |
| CSV restoration | Removed only the inserted row; restored exact original SHA b9aae74782fde6ba54671cfe07a9887c0af8ba1aad9d5befc1095e8cfef146ca. No partial query repair is left active or committed. |
| Executable restoration | Verified DROP checkpoint copied back to its active path with the identical SHA; redundant SSD checkpoint copy removed. Isolated binding-test executable remains on SSD. |
| Scratch cleanup | Only E10-owner.json remained after source retention; marker checked, removed and directory removed. closure-restoration.json records before/after df, exact marker, final runner hash, absent scratch/lease and pgrep exit 1. |

| Required finding selection | Selected? | Forcing receipt / next action |
|---|---|---|
| (i) Query restored and guest advances | No | Query still absent; zero boots. |
| (ii) Restored query exposes first remaining guest wall | No | No verification boot or dynamic remaining-wall evidence. |
| **(iii) Entry/preflight failure** | **Yes** | Fresh APFS admission shortfall stopped query generation. Resume only with the resource/ordering recipe in NEXT-BRIEF.md under renewed bounded authorization. |

No storage, SIF/CD, input, raster or Present work is promoted. No new frame was
captured. The E7 runtime fix's handwritten code was not changed, but E10 makes
no claim of re-proving its dynamic copy chain after this regeneration.

## 5. Commands, retention and remaining gaps

All SSD commands started with `export COPYFILE_DISABLE=1`. Paths containing the
SSD name were passed as structured argv or quoted. Work used:

```sh
python3 -B local/research/E10/e10_manifest.py before
python3 -B local/research/E10/e10_generate.py drop
python3 -B local/research/E10/e10_install.py drop
cmake --build /tmp/p1-link/runtime --target ps2EntryRunner ps2x_tests -j4
# First build: created AppleDouble companions removed using the retained manifest.
# The same -j4 build command then completed successfully.
/tmp/p1-link/runtime/ps2xTest/ps2x_tests
python3 -B local/research/E10/e10_link_test.py drop
# cwd: /Volumes/Extreme SSD/ps2recomp-spike/P1/e10-binding-tests/drop
./binding-test absent
./binding-test present  # required failure before query repair: exit 1
python3 -B local/research/E10/e10_static.py dis 0x2c5130 0x2c5170
python3 -B local/research/E10/e10_add_entry.py
python3 -B local/research/E10/e10_generate.py entry  # admission rejects; no spawn
# Restore only the inserted CSV row and the verified DROP checkpoint binary.
python3 -B local/research/E10/e10_manifest.py after
```

The generator's exact argv/cwd are in drop-generation.json; the isolated test's
full compile/link argv are in drop-binding-link.json. The rejected foreground
sequence is in entry-admission-console.txt. Restoration and cleanup operations
are pinned by closure-restoration.json and drop-checkpoint-reclamation.json.
Closed large logs are compressed; `retention.json` records canonical copies,
raw hashes and duplicate aliases. Before/after manifests retain every generated
name/hash without committing generated runner sources. The local replay auditor
checks these joins without generating, building or booting.

| Remaining gap | Bound on the conclusion |
|---|---|
| Query entry and truth-table execution | Still pending. Required static body and fail-before are recorded; pass-after is not. |
| Verification boot / object and copy joins | Still pending. No E10 dynamic a0, port-selection result, request completion, UI transition or pixel join. |
| Resource availability | Admission observes free space; earlier snapshots did not reserve it. A renewed brief must establish sufficient space before CSV mutation and recheck immediately before generation. |
| Known diagnostics | Fork git commands emit pre-existing AppleDouble pack-index warnings while returning successfully. E10 did not alter those unrelated metadata files. |
| New fork commits | None. Only generated output changed at closure, and the user explicitly prohibits staging it. Evidence commit uses [E10] and Orchestrated-By: Muse Code; ssx3 push is left to the orchestrator. |

Tail receipt: outcome (iii) only; DROP preflight complete; query absent; 452/452
suite; actual DROP handler returns to supplied RA with unchanged SP and preserved
s0 low 64 bits; zero boots; fork HEAD be0c9ee; generated sources unstaged; CSV
restored; APFS scratch and lease absent; no ssx3 push; standing no-regen resumed.
