# Proposed next brief — admit the query regeneration after completed DROP preflight

E10 selected (iii) at the fresh APFS admission for query generation. DROP-only
generation, installation, rebuild, the 452-test suite and the actual regenerated
handler test are complete. The query remains absent. No boot ran.

The ONE next action is a renewed, bounded query-entry brief after sufficient
internal APFS space is available. Reuse the completed DROP checkpoint after
identity checks; do not repeat its generation merely because E10 stopped.
Standing no-regen resumes when E10 closes. This recipe is not authorization.

| Prerequisite | Exact receipt / action |
|---|---|
| Fork/config | be0c9eeaa337d9685e9536fa4f66c5ce5029aad8; canonical and P1 used TOMLs remain selector-free at 0x426230. Canonical CSV remains b9aae74782fde6ba54671cfe07a9887c0af8ba1aad9d5befc1095e8cfef146ca. |
| Completed active checkpoint | Registry SHA 5d4ce8c47d9e5238c67ffa5830c43466e4e9f03b2c1adf0bbd3d9028a79c4ad1; 0x426230 binds sub_00426230_0x426230; 0x2c5140 absent. Runner SHA f5eeea20f661666f045d90da14acbde49a6349056d055c3fd0efcc34568c7f1f. Compare all 9,449 active generated names/hashes to after/generated.json. Generated files remain unstaged. |
| Resource failure | Fresh free space 3,240,579,072 B was 249,081,856 B short of E10's fixed 3,489,660,928 B admission. Earlier reclamation showed 5,608,226,816 B, so that earlier sample did not assure later availability. E10 does not identify the cause of the free-space change. |
| Fresh admission | Record both df results, at least 1 GiB logical-output reservation, 2 GiB internal free floor and explicit polling headroom. E10 used another 256 MiB, making admission 3.25 GiB. Account for other allocations and build/link growth before choosing the next upfront budget. Do not lower a declared guard after a rejection. Stop if unmet. |
| Ordering repair | Check and persist admission **before** editing the CSV; record rejection before raising. Recheck immediately before spawning. E10 inserted the row first, then stopped at admission and restored it exactly. A prior free-space snapshot is not a reservation. |
| Scratch | /tmp/ssx3-e9-retry-codegen is absent. Make a fresh owned directory under renewed bounded APFS authorization. Derive used TOML from canonical by changing only general.output. Clean it after verified installation/retention, recording before/after df. |
| Inputs | ELF SHA 1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc; generator SHA 511791795c16649e69706725c412408acc8d35fda68c4d83a3229eae6bda0763. Recheck source identity and canonical CSV; historical P1 CSV is stale. |

| Step | Recipe / acceptance |
|---|---|
| Checkpoint recheck | Full suite green and actual-binding fixture absent mode. The existing isolated binary is P1/e10-binding-tests/drop/binding-test, SHA 6fe978804cd63cbac35155d40b623eb73e1eecbd939ca9ddacf1b4fa258736d4; relink if any input changes. Expected-present mode currently fails with hasFunction=false. |
| Query entry | Revalidate ELF 0x2c5140..0x2c5168. Insert sub_002C5140,0x2c5140,0x2c5168,0x28 after owner sub_002C50E0,0x2c50e0,0x2c5168,0x88 and before 0x2c5168. Keep owner unchanged. Expected one-row CSV SHA c17db90b72db490772a649eb64b91487d54d1602b258be2e3205e2e7b039c6aa. |
| Generation/install | Normal exit, complete registry/header/body manifests, real exact-PC query binding and guest DROP handler. Compare emitted names and disposition leftovers; copy only changed bytes. Native macOS created provenance AppleDouble files despite COPYFILE_DISABLE=1: remove only companions proven created by this installation before CMake's source glob. Do not stage generated sources. |
| Actual-binding regression | Rebuild -j4; relink e10_binding_test.cpp against actual new runner objects. Query truth table (0,0)→0, (1,0)→1, (0,1)→1, optionally (1,1)→1; supplied RA, unchanged SP, relevant 128-bit callee-saves, whole 32 MiB RAM unchanged, zero GetInfo calls. Recheck DROP handler and full suite. E10 has no pass-after query receipt. |
| Observation | e10_observe.py / e10_card_observe.inc are prepared but **not installed, compiled or boot-validated**. Review before reuse. They extend the bounded E7 sink to observe dynamic constructor/UI/query inputs, returns, request calls and sibling status inputs without changing dispatch/results. |
| One guarded verification boot | Fresh T13 pre-claim checks, binary hashes, selftest, suite, lease and wall/progress/logical+allocated-byte caps. REPORT_ALL=1; E7/E4 taps retained. Capture query a0 dynamically, require [a0]=0x486f78, constructor PC=0x2c3fc4 and UI pointer store PC=0x23d5c8. Never trust another boot's heap. |
| Required joins | Query return at 0x2c44b0 and port-selection v0; state-3 path 0x2c48c0→0x2c4980→0x2c50e0→0x40a498; UI pending +0x338; packet→GS→D→field-processed Present. Candidate MC=0xb851a0/UI=0xb84a50 and S=0x61ba60 require same-run guards. |
| Stop | Exact entry/preflight failure, or first remaining wall (including 0x2c5358). No sibling repair, stacked fixes or storage/SIF/CD/input promotion without an actual request/completion dependency. A changed image alone does not establish progression. |

The prepared capture/miner scripts have not captured E10 data. Any next brief must
give them its own fresh evidence names, count boots under its own limits and keep
the existing shared lease discipline.

Tail receipt: DROP checkpoint complete; query absent; zero E10 boots; scratch and
lease absent; fresh resource admission and renewed regeneration authorization
required before the remaining query work.
