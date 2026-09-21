# E9 experiment contract — 2026-09-21

Start 06:14:54 UTC; deadline 12:14:54 UTC. Baseline fork
4acc59ffebc99561ea2b4fe8e1aa1bebbc3075f2; E8 evidence 86eb513, gate 231e1ae.
Regeneration is authorized only within E9. Standing no-regen resumes at closure.

| Phase | Hypothesis and observable | Alternative / stop |
|---|---|---|
| DROP preflight | Removing only `_sceSifCmdIntrHdlr@0x00426230` from canonical and used config leaves a guest translation binding. Preserve input, generated-source and binding manifests. Run the full suite and dispatch the actual baseline handler binding on an empty command buffer, proving normal return rather than a TODO trap. Recheck the regenerated handler before a boot. | Missing/replaced handler, behavior failure or failed suite selects (iii): table failure and repair recipe; no boot. |
| Query entry | A CSV function boundary at 0x2c5140 produces a real generated query entry. The actual baseline binding is absent; regenerated binding must return to supplied RA with unchanged SP and callee-saved registers and untouched guest memory. Test (state,outstanding)=(0,0),(1,0),(0,1),(1,1). Observe no sceMcGetInfo dispatch. | Entry or truth-table failure selects (iii); do not substitute a handwritten query. |
| Verification | One guarded capture observes query a0 and vtable 0x486f78, constructor/UI-pointer guards, returned port-selection v0 and intended request advance. Retain singleton/S fields and packet→GS→D→field-processed Present proof. | (i) restored entry and demonstrated advance; (ii) first remaining wall, with exact next recipe; (iii) failed repair/preflight or unalignable observation, measurement repair only. No menu claim from a changed image alone. |

The only behavior repair is the query map entry. No additional query, storage,
SIF/CD, input, raster or Present fixes. DROP removes a selector; it adds no HLE.
Reuse the sanctioned generator and existing taps, extending observation only
where needed. Generated runner files remain unstaged; named handwritten/config
changes are committed to the fork and pushed only to its `fork` remote.

| Budget / ownership | Limit |
|---|---|
| Captures | One planned, at most two boots; each wall ≤600 s with termination reserve; only under an owned `/tmp/ssx3-p-lane-lease`, immediate release before analysis |
| Progress | ≤1,000,000 syscall lines per boot |
| Capture bytes | Per-file and aggregate logical + allocated-byte caps recorded before claim; initial aggregate ceiling 1.5 GiB, function trace 1 GiB, boot log 256 MiB; terminate at the first binding guard |
| Free-space reserve | SSD ≥2 GiB, internal ≥1 GiB; record `df` before each boot and allocated/free-space deltas |
| Build / generation | `-j4` maximum; no adb; COPYFILE_DISABLE=1 for every SSD operation; generated sources + build work bounded at 30 GiB additional allocated storage |
| Lease wait | Log owner/wait to P1/run/e9-waits.log; retry no sooner than five minutes |

Before each boot: T13-0 checks, current binary hashes, lease absent, pgrep exit 1,
ISO/ELF sizes, both free-space receipts, trace-align selftest, waits tails, full
suite re-green and all three caps. Closed raw captures are compressed and retained
once. Evidence commits use `[E9]` and `Orchestrated-By: Muse Code`; no ssx3 push.

Tail receipt: contract written before DROP, regeneration, tests or captures.
