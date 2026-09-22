# Progress review and recommended work tracks — September 22, 2026

Prepared for Brad and the orchestrating Muse agent. Reviewed through ssx3
`731699f` (G37), with runtime source checked against `3adc0478`. This is a
review and handoff; it does not change runtime code, launch experiments, or
supersede active resource leases.

**Product direction confirmed by Brad during this review:** the next
demonstrable milestone is **stock SSX 3 gameplay through the PS2 static
recompilation runtime on Odin**. The eventual goal remains **120 Hz,
preferably 120 Hz simulation for minimal compromise**. NetherSX2 is a
reference and performance comparison, not the deliverable. An optional,
clearly labeled development-only startup-movie bypass is authorized so
gameplay bring-up and movie correctness can advance separately. This
prioritizes PS2 delivery over equal staffing of the GameCube alternatives;
it does not establish that PS2Recomp already has the performance for 120 Hz.

**Assessment.** Substantial engineering progress is real: the runtime has
advanced through multiple boot failures to visible UI and a specific movie
delivery stall; the GPU experiments now execute and accurately display
injected pixels on Odin; iOS decodes the retained title vector identically
to the host. Execution and evidence preservation are strong. The largest
remaining opportunities are better experiment selection, faster handoffs,
stable build storage, and starting the missing Android integration work.
More diagnostic workers on the same stall will not provide the same benefit.

**What is working, and what each result actually proves**

| Area | Established progress | Remaining milestone |
| --- | --- | --- |
| GameCube baseline | Stock and donor courses run on the Mac/iOS development path; course conversion, touch controls, checkpointing, and test tooling provide a useful working baseline. | Preserve this baseline. It does not satisfy the newly confirmed PS2 recomp milestone or a sustained 120 Hz claim. |
| PS2 execution | E11–E18 restored reached guest entries and movie-callback delivery. E18 delivered 5,040 title bytes; the visible card-message path and copy→GS→presentation comparisons advanced. E25 reproduced the runner and 458-test suite binaries exactly. | The native title path still parks before gameplay. Visible UI is progress, not a playable race. |
| Movie diagnosis | E27 identifies a host-owned request retained by its own blocked continuation, with another guest chunk already queued. This is a concrete lifetime/progress problem, rather than an unbounded search for a missing semaphore. | A fail-before regression, a supported continuation fix, and a live guest resume remain unproven. |
| GPU path | G28 fixes the reached descriptor-related writer failure; subsequent replay runs exit cleanly. G32/G34–G37 render deliberately placed content exactly. | Unmodified game content must reach the displayed surface; standalone replay must then integrate with the PS2 runtime. |
| iOS decoder | I23 supplies FFmpeg integration. I24 shows identical host/device feed-hold, flush-serve, dimensions, and RGBA bytes for the title vector. | Guest-visible title delivery is still open. Another unchanged iPad probe will not resolve the host request lifecycle. |
| Experimental discipline | Explicit controls, bounded runs, source/binary identities, independent gate reads, and honest VOID/RED outcomes prevent false success claims. | Gate the next action on product relevance as well as evidence quality. “Investigation passed” and “milestone advanced” need separate fields. |

Sources: [project baseline](../../README.md), [numbers ledger](../numbers-ledger.md),
[E18](../../local/research/E18/REPORT.md), [E25](../../local/research/E25/REPORT.md),
[E27](../../local/research/E27/REPORT.md), [G28](../../local/research/G28/REPORT.md),
[G37](../../local/research/G37/REPORT.md), [I24](../../local/research/I24/REPORT.md).

**Highest-priority correction: redirect the GPU investigation to the missing composite output.**

G30/G31 interpreted nonzero bytes in display region B, followed by black
scanout, as a sampler fault. G33 subsequently established that **every one
of B's 229,376 pixels has zero RGB**: its 149,721 nonzero bytes are in the
alpha position. G33's correct-render model therefore matches the original
black scanouts exactly. That finding removes the premise of the earlier
“sampler provably reads the wrong bytes” conclusion for this observation.

I independently read the pinned 11,537,377-byte G13 dump, reproduced the
region-B census and FNV, and computed the expected black PPM SHA:
`99418f1b1a94ed9ffcfadd6fc0b6573eca5275d6834a3d4cffb64da330233b34`.
It equals the reported black-image identity. The current
`gs/shaders/sample_circuit.frag` matches its Git object and explicitly
replaces the stored alpha with `0x80` on the relevant PSMCT24 path.
An alpha-only change from `0x00000000` to `0xff000000` produces the same
sampled value, `0x80000000`, by that source logic.

Consequently, G37's proposed **alpha-only “channel-specificity” successor
is not a useful next product experiment**. Correct rendering already
predicts black; an “exact” alpha-only render and a black render are the
same observable here. G37's one white source pixel becoming exactly one
white output pixel is positive sampling evidence, not evidence that a
special content threshold needs further characterization. This does not
prove the complete renderer correct, or erase the separately evidenced
compiler crash and descriptor failures.

The reached divergence worth following is **scene region A changes while
display/composite region B remains at its loaded contents**. G30 records
scene rendering at FBP0 and a composite pass targeting FBP112; G31 confirms
B stays unchanged at every sampled boundary while A changes. Reuse the
same dump and compare the first composite pass on Mac and Odin, with
matching packet/pass/field boundaries. Observe source A, composite state
and selected draw, destination B before/after, and final scanout. Locate
the first differing input, rejection, write, or dependency. Preserve the
existing game/reference timing alignment.

Practical next G brief: remove the color-injection treatment for the
baseline comparison, retain only necessary observation, and investigate
the **A→B producer/composite boundary**. Do not make adoption of the
already isolated crash fixes wait for an unlimited color-probe series;
give them their own regression/adoption gate. Keep the standing
no-upstream-contact rule. Any local filing should distinguish these
separate failures and correct the now-unsupported sampling inference.

Evidence: [G30 raster bounds](../../local/research/G30/REPORT.md),
[G31 state and bytes](../../local/research/G31/REPORT.md),
[G33 §2c2](../../local/research/G33/REPORT.md),
[G37 §4](../../local/research/G37/REPORT.md),
[independent verification receipt](../../local/research/progress-review-2026-09-22/verification.json).
Source inspected: `parallel-gs-g7/gs/shaders/sample_circuit.frag:52–70`
on the existing SSD checkout; SHA `850c1764…` is recorded in the receipt.

**Shorten the native gameplay path while preserving a faithful movie path.**

The approved movie bypass should be one bounded implementation task on an
isolated branch, using a reached movie-specific entry/exit contract and
defaulting off. P7 already surveyed the movie sequence and supplied an
unwired completion-stub candidate. Reuse that research, but verify the
actual current call path: P7 explicitly says its proposed hook was not
runtime-validated. Do not bypass the surrounding game initialization or
replace arbitrary waits with success.

Acceptance: the launch identifies the bypass, the guest exits movie
sequencing coherently, menu/input becomes usable, and a stock race starts
and progresses. Record the next reached blocker if that chain fails.
This is development bring-up evidence; ordinary-boot/movie fidelity stays
open. The bypass branch and faithful branch need separate receipts and
baselines. Do not flush a partial decoder input on every chunk merely to
force frames out: I24's isolated flush proof is not that runtime contract.

The faithful E-lane question can now become a small host-side regression:
an authored stream whose first producer callback supplies bytes but no
complete parser packet, followed by a second queued chunk. Exercise the
real GetPicture/invocation/wait path; assert eventual frame delivery and
one guest resume without duplicate callbacks or an unbounded retry loop.
Cover empty/no-progress input, end-of-stream, cancellation/reset, and
callback ownership. A candidate fix must preserve the established E18
ABI and callback semantics. I checked the request guard, callback
continuation, and captured shared ownership in pinned `MPEG.cpp`; this
supports the diagnosis, not a particular one-line fix.

Finish or close E28 honestly under its current bounds. If its store-only
watches cannot expose the needed queue values, do not schedule more
guest-only confirmation boots. E27 itself says the remaining discriminating
observation is host-side. Combine that observation with the regression and
one candidate-fix evaluation under an explicit brief, rather than
serializing every small observation into a fresh full boot and handoff.

Sources: [P7](../../local/research/P7/REPORT.md),
[E28 brief](../../local/muse/prompts/E28.md),
[E27](../../local/research/E27/REPORT.md),
[I24](../../local/research/I24/REPORT.md).

**Recommended parallel tracks and ownership**

The clean split is by independently reviewable output and owned files.
Use separate worktrees/build directories at pinned revisions. Muse remains
the single integration and scheduling owner; workers exchange artifacts
through that owner. A new worker must not edit or rebuild another lane's
active output.

| Track | First bounded deliverable | Can run alongside | Integration/stop condition |
| --- | --- | --- | --- |
| Native gameplay / E owner | Approved movie-bypass path to menu/race, or the next precisely located blocker. Preserve the faithful branch. | GS work, Android build preparation, read-only reference analysis. | One live PS2 runtime mutator and boot owner. Coordinate branch changes and the P-lane lease. |
| Faithful MPEG regression | Reusable authored two-chunk fail-before case and continuation design; then one tested fix. | Bypass investigation in a separate worktree; no concurrent writes to shared runtime/generated outputs. | Same runtime integration owner serializes merges and live validation. With limited workers, prepare this offline and give gameplay first access. |
| GS / G owner | Matched Mac/Odin A→B composite comparison and smallest supported correction; adoption package for known crash fixes. | Native CPU-runtime work and Android preparation. | Own paraLLEl/Granite patch stack; book exclusive Odin slots. Exit on unmodified game pixels matching the aligned reference, then integrate. |
| Android runtime / platform owner | Reproducible arm64 native APK, generated-title linkage/binding manifest, retained runtime logs, app-owned boot paths, and one stock-title launch to a named checkpoint. | E/G investigation using separate trees and build resources. | Use existing Android scaffolding; a replayer binary or an emulator race does not pass. Own app/build/input/presentation wiring; runtime API edits go through E. |
| Build/storage reliability, then reference support | Durable verified build root, pinned restore manifest, bounded logs, and successful restore smoke check; then aligned reference captures for named E/G questions. | Source review and offline analysis; migration cutover waits for active leases. | No speculative rebuild farm. Known-good independent source for disputed inputs; no sole authoritative copies on the corrupt path. |

**Staffing:** with three execution workers, keep E and G active and use the
third first for storage/cutover, then Android integration. With a fourth,
start Android preparation immediately; the extra regression work can be
offline within E or a short separate assignment. Reference work is
request-driven, not a permanent stream of unrelated motion-tracker
experiments. iOS guest reprobes wait for a relevant runtime change; the
completed decoder work is ready to consume it. GameCube/MetalFX enhancement
work is a reserve track under the confirmed priority.

Android preparation is a real separate opportunity: the fork already has
`android/README.md`, a NativeActivity manifest, and Android CMake paths.
Its README records missing runtime stdout/stderr logcat routing, and
FFmpeg defaults off on Android. Audit those actual paths before promising
a simple port. iOS's newly working decoder reduces design uncertainty but
does not constitute an Android build. Reuse existing packaging and codegen
where valid; do not start by regenerating everything.

The dependency chain is:

```text
stable build/evidence storage ──────────────────────────────────────┐
native title → menu → stock race ──────────────────────────────────┤
GS composite correctness → runtime backend integration ────────────┼→ Odin native race
Android app + title linkage + input/presentation ──────────────────┘
                                                                    ↓
                                      measured native budgets → 120 Hz simulation
```

A CPU-rendered diagnostic launch can unblock runtime/platform work; a
usable Odin gameplay milestone still needs measured rendering throughput.
Do not serialize Android preparation behind the last desktop startup bug.

**Operational changes with immediate payoff**

1. **Move active work onto durable, verified storage.** E24 lost protected
   `/tmp` builds after restart; E25 recovered the binaries bit-identically
   and already provides a snapshot/restore recipe. G36's gate records the
   fifteenth corrupt/read-artifact recurrence. The current two-read and
   independent-pin rules are justified while that path remains suspect.
   A Mac mini migration helps only if its active inputs and build cache
   avoid the same faulty storage path. Restore after the active lease,
   verify against recorded pins, smoke-check once, then publish the new
   paths. Preserve the old evidence. Do not relax checks before cutover.
2. **Use completion-driven gate reads with the hourly poll as a watchdog.**
   Recent Git timestamps show roughly 42–48 minutes between G34/G35/G36
   result commits and their successor brief commits. These are handoff
   intervals, not measured idle CPU time, but they are a clear latency
   opportunity when a worker's experiment takes about 15–40 minutes.
   Queue the allowed successor outcomes in the brief so Muse can gate and
   launch promptly without another product question.
3. **Require the correct-behavior model in every experiment.** Include
   “the implementation is behaving correctly on these inputs,” not just
   two competing fault models. Calculate observable outputs before a
   device run; equal predictions cannot discriminate. G33 found this
   problem, but the interpretation was not propagated to the lane's root
   claim. This is the most consequential process correction in this review.
4. **Allow bounded investigation-through-fix tasks.** Specify the symptom,
   regression, one permitted behavioral change, validation, and stop on
   the next unrelated failure. Keep single-owner semantics and review
   gates. A compulsory “one question, one fresh build, stop regardless”
   pattern needlessly adds handoffs after the relevant mechanism is known.
5. **Reuse build outputs and observation tools.** Several G briefs create
   another complete `[458/458]` build for one changed hunk. After storage
   is stable, use one owned incremental build per configuration, preserving
   immutable before/after binary identities and patch manifests. Separate
   sanitizer/configuration variants. Extend T1/T5/T12/T22 tools rather than
   copying admission, renaming, and receipt machinery into each new brief.
6. **Make current status short and authoritative.** `docs/todo.md` is over
   6,200 lines; its “Live panes” still lists T35/G15/E10/I13 while herdr
   showed E28/G37. The GS plan still describes greenfield backend stages
   while the active work uses paraLLEl-GS. Keep a compact current board
   with owner, pinned revision, product milestone, blocker, next action,
   and lease. Link the full reports as history. Retain source-backed
   numbers; do not treat report volume or PASS counts as delivery metrics.

These extend the earlier reviews' controls rather than reopening the
closed long-drain, residual-microscopy, or dormant kernel sweeps. Runtime
implementation also lives in sibling repositories: ssx3's documentation-
heavy commit history alone is not a measure of coding effort.

**Milestones to use for steering and acceptance**

| Milestone | Evidence that closes it |
| --- | --- |
| Native stock race reached | PS2 recomp revision/module identity; menu/input works; race HUD and advancing guest position; normal versus bypass boot identified. A new blocker is a partial result, not closure. |
| Stock recomp gameplay on Odin | Installed native APK identity; controller/input; correct scene/HUD output; a reproducible full stock race and restart; measured game speed, audio behavior, CPU/GPU work, and presented-frame timestamps. Explicitly identify remaining fidelity/performance issues. |
| Baseline ready for 120 Hz work | Stable stock-speed behavior plus a second, heavier gameplay sample; representative native frame-time budget and thermal conditions. Tiny GS dumps and NetherSX2 headroom do not fill these cells. |
| True 120 Hz simulation | Roughly twice the stock gameplay-update cadence at normal wall-clock game speed, with physics, timer, input, animation, and audio checked against the baseline; distinct display presentations and pacing measured independently. Faster emulation, duplicate presents, and frame interpolation are different outcomes. |

Keep the existing present-time and sustained-window measurements, but
update [route criteria](../route-criteria.md) for Brad's preference for
120 Hz simulation. That older document permits either 60 or 120 Hz
simulation and contains a stale “no first frame”/work-queue snapshot.
Use milestones for both delivery and research: current best playable
state, next missing behavior, time blocked on infrastructure, handoff
latency, and reproducibility of the latest build. Set budgets for the next
bounded outputs rather than claiming an unsupported delivery date.

**Suggested next scheduling decisions for Muse**

1. Record Brad's product direction and authorized development movie bypass.
2. Read the G33/G37/source correction before launching an alpha-only
   successor; assign the A→B composite comparison instead.
3. Close E28 within its current contract, then prioritize the bounded
   movie-bypass/gameplay path and host regression work under one runtime
   integration owner.
4. Assign a short storage cutover/restore task and an Android preparation
   task with distinct outputs and shared-resource reservations.
5. Bring back a native gameplay checkpoint, a matched composite result,
   and an Android build/launch receipt. Revisit staffing on those results.

**Review verification and limits.** I read the active plans, the September
19/20 reviews, route criteria, recent E/G/I/T reports and briefs, selected
GameCube/product backlog, recent Git history, and live herdr state. I
checked the MPEG source against its pinned Git object, the scanout shader
against its Git object, and independently recomputed the critical G33
buffer/channel evidence from the pinned dump. No emulator boot, device
run, build, or full test suite was repeated for this review. Existing
458/458 and device results are attributed to their reports; the new
verification is the small read-only check linked above. G37 landed during
the review; its result is included, while its orchestrator gate and E28's
outcome were not yet read. No external filing, implementation, or change
to a worker's active task was performed by this review.
