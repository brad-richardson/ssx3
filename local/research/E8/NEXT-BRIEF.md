# Proposed next brief — restore the reached memory-card query entry

E8 selected outcome (ii); this recipe is not executed in E8. Baseline
remains fork 4acc59ffebc99561ea2b4fe8e1aa1bebbc3075f2. The two E8 boots
retain the E7 copy fix and do not reach menu content.

| Prerequisite | Exact requirement |
|---|---|
| Regeneration gate | Obtain the existing 0x426230 DROP disposition from the owning lane before any regeneration. Current binding is sub_004261F0 at 0x426230; a regeneration that silently replaces it with the selector/HLE trap is not acceptable. |
| Source identity | ELF 3890784 bytes, SHA256 1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc. Preserve configuration, generated-source and binding manifests before/after. |
| Scope | Fix entry coverage for the reached guest busy query 0x2c5140. Do not force its return value, clear UI pending state, substitute host memory-card success, or stack storage/raster fixes. |

Forcing receipt: e8b-missing-query.txt plus the complete raw log. Two
port-selection calls at source 0x2c44a8 and 1249 UI polls at source 0x23d6a4
all request target 0x2c5140 with a0=0xb851a0, vtable=0x486f78,
state[a0+4]=0, v0=0x2c5140 and policy=1 (ContinueToTarget). The runtime
returns true without executing the absent target. The generated callers
resume at 0x2c44b0/0x23d6ac and take the nonzero-result busy branches.

The body is already emitted after the preceding routine's unconditional
return in sub_002C50E0_0x2c50e0.cpp. It has neither a 0x2c5140 entry
switch case/label nor a generated table binding. Registering the existing
owner alone would incorrectly start 0x2c50e0. The next lane must produce
a real exact-PC entry, through the sanctioned generator/splitting path
after the prerequisite gate, and demonstrate its correct binding.

| Required check | Expected receipt |
|---|---|
| Fail-before/pass-after entry test | Dispatch 0x2c5140 using the actual generated binding, not a handwritten replacement. Before: hasFunction false. After: reaches the query body, returns to supplied RA with unchanged SP, and does not call sceMcGetInfo as part of the query. |
| Query truth table | state(+4)=0/outstanding(+0x40)=0 → v0=0; either nonzero → v0=1. Exercise both nonzero cases. Preserve relevant callee-saved registers and guest memory. |
| No DROP regression | Explicit 0x426230 binding/behavior receipt satisfying its disposition; full suite green. Generated files follow the owning lane's staging rules. |
| One diagnostic verification boot | Same shared lease, fresh T13 pre-claim checks, new binary hashes, wall/progress/byte caps, no parallel boot, release before analysis. Keep PS2X_DIAG_REPORT_ALL=1 and E7/E4 copy/frame taps. |

For the verification boot, capture the object dynamically from the
query's a0 and require [a0]=0x486f78. If using watch addresses, the E8b
candidates are below; guard them with the constructor write at 0x2c3fc4
and the UI pointer store, rather than assuming another boot's heap.

| Watch / observation | E8b candidate address / edge |
|---|---|
| MC object/vtable, state, port, outstanding | 0xb851a0, 0xb851a4, 0xb851ac, 0xb851e0 |
| UI MC pointer and pending flag | UI=0xb84a50; +0x434=0xb84e84; +0x338=0xb84d88 |
| GetInfo outputs/result globals | 0x4a3938, 0x4a393c, 0x4a3940, 0x4a3944 |
| Port selection | 0x2c44a8→0x2c5140→0x2c44b0; record the actual returned v0 |
| Intended request advance | 0x2c44c0→0x2c48c0(state 3)→0x2c4980→0x2c50e0→sceMcGetInfo0x40a498 |
| Poll/retirement | 0x23d6a4→0x2c5140→0x23d6ac; observe pending flag retirement at 0x23d6b4 when the guest predicate permits it |
| Copy guard | Singleton0x4a289c and S fields from E7; packet source/hash→GS→D→field-processed Present |

E8b also reaches an absent sibling status-query entry 0x2c5358 from
0x2d3828, 1249 times. Keep it tabled as a reached residual; do not claim
that restoring 0x2c5140 alone reaches a menu. After the one coverage
repair, stop at the first demonstrated remaining wall. Only an actual
guest request/completion dependency can promote memory-card storage,
SIF/CD or input work. A changed frame requires the full packet/source/
display/Present join before claiming interactive/menu progression.

Tail receipt: one proposed coverage action, explicit prerequisite gate,
exact entry and truth table, candidate addresses guarded within the same
run, acceptance chain and stop condition; no E8 regeneration or fix.
