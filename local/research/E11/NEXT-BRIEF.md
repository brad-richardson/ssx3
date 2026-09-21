# Next E-lane brief — restore the first branch-changing card predicate

This is a proposed next brief, not authorization to regenerate or boot now.
E11's query-only exception is closed. A new bounded exception is required.

| Prerequisite | Current receipt |
|---|---|
| Fork baseline | `ffdf58c4ee3b95bc6dd8779a0baeed0b23afe19b`, pushed to fork `ssx3` |
| Active checkpoint | `/tmp/p1-link/runtime`; protect it and DerivedData. Registry `68217e9a308cd7aaa540a1cac4115e9f9021b3e984b2a7e6b1e3250639be8907`; 9,450 generated names in `after/generated.json` |
| Runner / suite | Runner `c39e59a7f202436e8a70c1f9f4373e7b577b71b1191c6912ecc8ad2cfd0f2c96`; suite 452/452; query four-case actual-binding test passes; DROP handler still guest code |
| Authorization | Renew for **`0x2c5300` only**, no second predicate. No blanket analyzer sweep or storage/raster change |
| APFS admission | Fresh sample and persistence before any CSV mutation, then immediately before generator spawn. At least 1 GiB logical +2 GiB floor +256 MiB guard; account for build/link headroom separately. Do not assume E11's final free space persists |

## Forcing receipt and repair shape

| Link | E11 evidence |
|---|---|
| Missing entry | Raw line5119: source `0x242150`→`0x2c5300`; a0=`0xb851a0`, vtable=`0x486f78`, a1=0, stale v0=`0x2c5300`, policy1. Same-run slot0 status=0 |
| Guest semantics | ELF `0x2c5300..0x2c5320` returns `status[a1] == -10002`; stride0x14, offset0x184. Correct observed result is zero |
| Consequence | Actual caller tests stale nonzero at `0x242158`, implying branch to `0x2421a8` and UI+0x344 clear at `0x2421b4`; the branch/store is a code-derived join that the next probe should observe directly |
| Existing owner | `sub_002C52D8,0x2c52d8,0x2c5320,0x48` contains the predicate after its earlier return. Preserve it |
| Single sanctioned row | Insert `sub_002C5300,0x2c5300,0x2c5320,0x20` after the owner and before `sub_002C5320` in canonical CSV. Regenerate via the established APFS path; no handwritten implementation or owner-only registration |
| Keep separate | `0x2c5358` remains absent, but all113 captured zero-status calls require nonzero result, matching the observed branch sense. Table it; do not add its row to this repair |

Read E11 REPORT, `e11a-residual-join.json`, raw predicates/caller/vtable
disassembly and retained actual generated source before changing anything.

## Required regression and installation

| Check | Required evidence |
|---|---|
| Fail-before | Relink fixture against actual baseline runner objects; `hasFunction(0x2c5300)=false`; an expected-present test fails before regeneration |
| Exact entry | Newly emitted `sub_002C5300_0x2c5300`, actual registry lookup and symbol; preserve owner body, busy-query entry and DROP binding |
| Predicate truth table | For **each port 0 and1**, selected status `-10002→1`; `0→0`, `1→0`, `-10001→0`, `-7→0`. Put `-10002` in the unselected port while selected=0 to prove indexing; reverse to prove selected-port behavior |
| Preservation | Supplied RA, unchanged SP, full relevant callee-saved 128-bit GPRs, whole-RAM preservation and zero unexpected memory-card API calls. Caller-saved a0/a2/v1 may change as the guest body specifies |
| Regression | E11's exact busy-query four cases; DROP empty-buffer RA/SP/s0 receipt; full suite. Do not bypass the actual registry with a handwritten predicate |
| Installation | Manifests before/after, compare all emitted names, disposition leftovers, copy changed bytes only without metadata, remove only proven-created companions; generated runner sources never staged |

## One guarded verification boot proposed

Same lease / fresh T13 pre-claims / REPORT_ALL / E7/E4 / wall, progress and
logical+allocated byte caps. One boot, release immediately before analysis.
Use dynamic constructor/UI guards, never assume E11 heap addresses.

| Probe | Purpose |
|---|---|
| Constructor `0x2c3fc4`, UI pointer `0x23d5c8` | Capture MC dynamically, require `[MC]=0x486f78`; derive UI+0x434, status0/1=MC+0x184/+0x198 |
| `0x2c5300` calls/returns | Capture original a0 and a1 before the predicate mutates caller-saved registers; selected status, return v0/RA/SP, sources `0x242150`, `0x2d37f8` |
| UI+0x344 (`UI+port*0xe0+0x344`) stores | Capture PC `0x2421b4` and initialization `0x242110`; direct receipt of the caller branch consequence |
| Existing query/request join | `0x2c5140`→return`0x2c44b0`; state3→`0x2c4980`→`0x2c50e0`→GetInfo; Sync/outstanding/UI pending completion |
| Remaining predicates | Retain bounded `0x2c5358` a1/status/v0 missing observations. A new wall is tabled, not fixed in the same scope |
| Display join | Same-run graphics singleton/S fields; packet hash/source→GS consumption→D VRAM→field-processed Present. Decode the final copy row separately as `e11_join.py` does |

| Outcome | Stop / next action |
|---|---|
| Named entry restored and caller takes the correct path | Join the ensuing request and changed content; identify exactly one next action |
| Remaining entry or guest gate appears | Table first forcing receipt and exact next recipe; no menu claim or stacked repair |
| Admission, generation, binding or capture failure | Stop on that measurement/resource/entry failure only |

The E11 screen alone is not a storage dependency. GetInfo/Sync already provide
present/formatted-card success. Promote storage, SIF/CD or input only if a
new actual guest request/completion dependency names it.

**NEXT-BRIEF TAIL COMPLETE — proposal only; no further work executed in E11.**
