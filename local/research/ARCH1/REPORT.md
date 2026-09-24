# ARCH1 — independent architecture/direction review

2026-09-24. Independent steering, not a root-cause finding or project verdict.
Read-only except this report and its commit; no builds, boots, device access,
config changes, push, or pane coordination. The orchestrator owns the verdict.

**Keep Odin race visibility ahead of deep speed work. Proceed with the worker
fingerprint only as one bounded delivery sanity check, with an explicit exit
from that investigation. The highest-value integration risk is incomplete
source-to-package provenance; this review found a concrete backend attribution
error.** Fixing run variance is useful, but is not itself the visible-race gate.

| Recommendation | Supporting evidence | What would falsify it | Cost / lease / build impact | Confidence |
| --- | --- | --- | --- | --- |
| Retain the milestone chain; require a visible, advancing, input-responsive **live Odin race** after replay repair. Keep the CPU backend as the functional reference. | Current board E/G/N: `docs/status.md:9-11`; N7 world visible but rider-stall check open, `docs/todo.md:1038-1045`; controller mapping exists, `:1001-1013`. Replay bypasses the live game. | A current, provenance-pinned live GPU race already satisfies these observations; none in the named evidence. | No new work before the bounded graphics discriminator; one live acceptance run after a candidate repair, not a speed run. | High |
| Permit one worker-consumption pair; call equality a partial delivery receipt, not GPU localization. Stop expanding input-hash probes after an equal-digest/different-output pair. | Verified FIFO, payload copy and by-value priv capture [S1-S3]; F3 gate line 5 already narrows equality. F4 remains unapplied. | A differing consumed digest/count at or before an output split makes delivery investigation the next branch. | Existing F4 budget: one host build/suite/replay, one mini slot; subsequently one Android package and two same-settings leased Odin replays, each <=600 s, force-stop after each. No tuning loop. | High on interpretation; medium on expected information gain |
| Before that package, close one source-manifest gap across the actual build inputs. Correct the backend attribution now; do not infer a readback bug from a renderer-local missing wait. | P3 pins backend `84a13a80…`, not F2/F3's `c6135b3c…`; current Present still waits idle [S4]. Interface/page tracker/Granite remain unpinned to the old APK [E3]. | A complete old-package manifest matching these exact files is recovered. That closes provenance, not graphics correctness. | Bounded receipt/source reconciliation (suggest <=30 min), no lease or standalone rebuild; attach the manifest to the already-planned next build. | High |
| Keep title-glyph archaeology below N; leave the save-seed search parked. Spend the next measurement on the Odin boundary, then return to live input/progress acceptance. | Board G explicitly prioritizes N; GB7C8 cannot isolate packet5470 at marker260; E has no valid save source (`docs/status.md:9-11`; `docs/todo.md:952-963`). | Glyph work names a mechanism that predicts the same Odin race failure, or a real pinned save becomes available and blocks the named next experiment. | Avoid competing builds/leases. No cancellation of completed work or restart of the historical queue. | Medium-high |

**Measured facts and limits.** I independently read both OFF hash files: 41
ordered rows, priv 41/41 equal, VRAM 16/41, present 25/41; the first differing
sample is tick850. At that sample OFF1 is `23589ef3/60a25873/9d6d204c`, OFF2
`f4b5d042/60a25873/52bf27d0` (VRAM/priv/present). Mac ON/OFF hash files and
final PPM compare byte-for-byte equal. Image descriptions here rely on the
orchestrator's viewed-frame gates, not a new visual review [E1-E2].

Tick850 is the first **sampled** difference, not a proved first faulty command:
samples are 50 ticks apart and hashes can miss transient differences. Mac/Odin
ON already differs at tick50 (ledger live row “N8D7M12 offline Odin replay”).
Variance and persistent blackness need not share a cause; stable black output
would not satisfy the milestone. This memo makes no new speed estimate.

**Does the fingerprint discriminate?** Under the verified source model, a single
replay producer reads fixed records, copies GIF bytes into owned queue storage,
captures priv `offset/value` by value, and one worker pops FIFO [S1-S3]. Equal
consumed fields are therefore the model's necessary prediction. If “delivery
variation” means ordinary scheduling of this correct FIFO, the proposed test is
effectively tautological: scheduling changes timing, not order. It is not
tautological against corruption, an unexpected producer, a queue defect, or a
different packaged implementation. That is its narrow value. Hashing before
dispatch also does not prove that a handler accepted or applied a command.

| Hypothesis | Worker-consumption digest prediction | Alternative: digest at accepted `RawGifPacket` entry, before `gif_transfer` [S4] |
| --- | --- | --- |
| GIF bytes/path/order differ before worker consumption | Different digest/count by the next sample covering the change, barring collisions/coverage gaps. | Different GIF digest/count if the difference reaches this boundary. |
| Worker sees equal commands but a GIF handler drops/changes delivery before the backend | Worker digest can remain equal. | Backend digest/count differs; this is the alternative's extra discrimination. |
| Consumed and delivered inputs equal; renderer state, GPU execution or host readback differs | Equal digest with differing output. Timing-dependent behavior is still possible. | Equal digest with differing output; does not separate those downstream classes either. |
| Only priv-write content/effects differ | Kind-only digest can remain equal. | GIF-only digest can remain equal too. |

The alternative loses non-GIF coverage and shares the fixed-input/FIFO
prediction. Do not spend a separate pair replacing one with the other. A later
tap in the same build would test acceptance/drop, not supply an independent
GPU-cause discriminator.

For the proposed pair, require 64-bit digest **plus command count**, explicit
kind/length/field encoding, correct quiescent snapshots, and exclude Fence from
the running digest/count because its presence is timing-dependent [S2; F4
REPORT:55-75]. F3 proposed 32-bit; F4 already prefers 64-bit. Neither is collision
proof. Sampled `privHash` covers final CPU register mirrors, not every transition;
opaque `PrivWrite.apply` leaves a real content gap. By-value replay captures
reduce one lifetime concern but do not measure applied effects. A future closure
would hash semantic offset/value at consumption or register effects immediately
after each apply; hashing a callable's object bytes is not a substitute. Do not
expand F4 into a general command-API refactor merely to eliminate this caveat.

Predeclare outcomes: (1) digest/count differs before/at the first output split:
bounded delivery investigation; (2) digests equal but output differs: retire the
covered delivery hypothesis and choose one downstream state/readback probe;
(3) everything equal: variance not reproduced on this instrumented pair, no
causal verdict and no automatic retry; (4) malformed/missing rows or provenance
failure: measurement invalid. Added CPU hashing/locking changes timing, so case
(3) is not a repair claim. The pair uses the **same new APK**, not the old
`caa11102…` APK with an impossible retroactive instrumentation claim. Fences
order CPU command handling, not GPU execution; handlers can submit before the
explicit readback (F3 gate:5).

**Highest-value risk: source provenance across runtime/GS/Android.** F2
REPORT:23,47-55 and F3 REPORT:30,38-40 label the `c6135b3c…` backend APK-tied.
But `N8D7M1/REPORT.md:20-25` records its replacement by `84a13a80…`, and
`N8D7M12P3/REPORT.md:66-73` plus `source-gate.json:68-73` pin that replacement
in the OFF-pair package. I hashed the P2 backend and obtained
`84a13a80686be8d4ed17750a9399d298ea6b998b98f48d3720b6b5bc839a4645`.
The diff adds the oracle; the important wait/map and SnapshotVram statements
remain in the actual source [S4]. Thus this is a citation/provenance correction,
not evidence that those synchronization conclusions reverse. The three renderer
pins still match independently [S5].

Bounded next action: assemble one manifest for the next package's fork
core/frontend/worker/backend, paraLLEl interface/renderer/page tracker/shaders,
Granite including dirty patches, build flags, and Turnip/HAL inputs; connect it
to APK/native-member SHA and Build ID using the existing P3 gates. Reconcile
old inputs only within the time box. If historical bytes cannot be recovered,
mark the gap and establish a new pinned baseline; do not claim equivalence to
the old build. Stop before a causal comparison if unexpected changes remain.
This prevents further detailed audits of code not demonstrated to be running.

`Present` barriers, waits idle, then maps [S4]. `SnapshotVram` delegates to the
interface; the unpinned interface waits on a timeline and Granite conditionally
invalidates non-coherent memory [S6]. Neither “no renderer-local wait” nor
“conditional invalidate” proves a defect. A downstream probe must distinguish
actual GPU-memory variation from stale host-visible bytes with a named resource,
writer and visibility contract; rehashing the same pointer cannot do that.

**Allocation of effort.** The current N priority is sound. The avoidable
over-investment would be more source-map-only rounds or title-pixel work without
a changed prediction; P5F2/F3 now provide enough map to bound a measurement.
Under-investment is in a reproducible package boundary and eventual live
input/progress acceptance. The old review's RTC/scheduler recommendations are
not untouched backlog: current live E55C2/D4/D5 rows already record bounded
repeatability and an input discriminator. That does not establish universal
determinism, but full guest determinism/card coverage is not a prerequisite for
this fixed-stream replay. Keep sky, E54E, INTC and later E57 in the board's
order; do not revive the stale §10 queue or schedule 120 Hz work now.

Evidence anchors (all local; source line numbers at the read pins):

- [E1] `local/research/N8D7M12P5E2/REPORT.md:67-98`, `ORCH-GATE.md:3-5`.
  Private OFF1/OFF2: `~/dev/ssx3-work/N8D7M12P5D1/parallel.hashes`
  SHA `19738cc3…783af9`; `N8D7M12P5E1/parallel.hashes` SHA `e78d7589…4ec580e`.
- [E2] `local/research/N8D7M12P5M4/REPORT.md:77-98`, gate:3-5.
  Mac hashes `94b433df…10c290`; compared private ON/OFF final PPM bytes too.
- [E3] Full F2/F3 reports and gates; F4 REPORT:3-34,48-118 and its permission
  gate. F4 is an uncompiled design; its stop is not a technical test failure.
- [S1] Root `~/dev/ssx3-work/N8D7M12P2/PS2Recomp/ps2xRuntime/`:
  `src/lib/gs/gs_worker.cpp:44-76,91-125` (rehashed `3300f41d…538341`).
- [S2] Same root, `src/lib/gs/gs_frontend.cpp:178-279,929-956,1438-1451`
  (rehashed `f6972433…dc1808`); `include/runtime/gs/gs_worker.h:97-115`.
- [S3] Same root, `src/lib/gs/gs_replay_core.cpp:84-92,217-233,350-459`
  (rehashed `c5fdaf64…396c`): owned setup, replay dispatch, priv capture,
  marker drain and sampled readbacks.
- [S4] Same root, `src/lib/gs/ps2_gs_parallel_backend.cpp:592-602,790-791,
  867-885,897-904`, hash `84a13a80…a4645` above; P3 source-gate:68-73.
- [S5] Root `~/dev/ssx3-work/N8D7F/parallel-gs/`: rehashed
  `gs/gs_renderer.cpp` `85c29cb0…3de77e`, `gs/gs_interface.hpp`
  `3a1751b4…05954d9d`, `gs/gs_renderer.hpp` `fae3261a…a93a401a`;
  renderer:1194-1208,5354 verified. F2 REPORT:18-22 has full pins.
- [S6] Same renderer root, **unpinned to APK**:
  `gs/gs_interface.cpp:5126-5165`,
  `Granite/vulkan/memory_allocator.cpp:480-505`, directly read.
- Context read: repo/local/parent AGENTS; current board, E/G/N todo and live
  ledger rows; `docs/orchestration.md` §§1,10; full
  `docs/research/review-2026-09-23-frontier-2.md`. Board and gate updates
  during this review were read; no orchestrator-owned file was changed.
