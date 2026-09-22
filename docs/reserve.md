# Reserve — parked GameCube/Dolphin work

Parked 2026-09-22 when Brad set the milestone to stock SSX 3 through the
PS2 static recomp on the Odin (see `AGENTS.md`). Nothing here gets
scheduled unless Brad asks. The full text and evidence links for every
item are in `docs/archive/todo-2026-09-22.md` (line numbers below point
there).

## Where the GameCube route stands

Stock SSX 3 boots, menus and races natively on macOS/iOS and headless or
onscreen on the Odin (display spike, 09-17). Garibaldi and Aloha Ice Jam
ride as donor courses through the boot-time course manifest, and course
rows apply live. For 120 Hz, full-sim route F is dead on this build (D6).
Host replay measures 0.67–0.87 ms per replay on the Odin (S2). The Odin
emulation path runs about 1.05–1.2× short of what full sim needs.
Numbers: `docs/numbers-ledger.md`.

## GameCube 120 fps route

- 120 fps plan of record and its gates — `plan-120fps-2026-09-17.md` (L13)
- Codegen entry-switch pruning: capped CPU-gated A/B, then land or drop (L18, L241)
- FP-unavailable fault storm on Odin: cost per fault, eager-FP context switch (L32)
- fast-FP on/off and EFB 1×/2× re-A/B off the phantom wall (L257, L266)
- Throttle s64 hardening; memory fast paths; desktop cost table re-run (L270–L284)
- Harness measurement fixes; texture-cache mode + video-thread atomics (L289, L296)
- Replay re-scope + empty-queue sync; bind captures to encoder frames (L300, L957)
- Affinity/priority follow-through for the hot thread (L306, L401)
- SyncGPU double decode; FIFO exception-poll change (L314, L449)
- Trial-driver fast path; screenshot cadence; budget-stop hardening (L320, L326, L364, L386)
- Interp alpha period mismatch (59.94 vs 120) (L331, L407)
- f32-from-bits slow-path histogram; signpost caveats (L335, L340, L410)
- Layout-lottery follow-up to the fcmp inline regression (L354)
- Display production wiring for the Android APK (CreateAndroidPlatform) (L371)
- Patch-stack drift receipts (L378); frame-exact snow A/B (L392)
- Self-clearing short-window veto (L440); Odin viability gap (L455)
- 120 Hz verdict re-issue after the generation fix; arch-review findings 2–4 (L499, L515)
- Callback CPU profile; route F probes; F render test; headroom backlog (L755–L854)
- Output-size comparison on the phone (L951); observational MemoryWatcher reads (L965)
- Exception-vector interpreter fallback (L1287)

## Course restoration and content

- Implementation plan of record — `impl-plan-2026-09-15.md` (L524); route control (L541)
- Next Tricky course (L576); course selection for added tracks (L653); new menu entry / peak = fixed-table surgery (L419)
- Live-apply: deferred-then-applied E2E; iOS compile check (L345, L351)
- Course texture/lighting review; donor fog/backdrop (L492, L740)
- Visual remaster with trained upscalers (L607; method in `texture-remaster.md`)
- Jump-approach captures; full-course acceptance after resets (L743, L745)
- Garibaldi: water callbacks, obstacle collision, surface profile, scene animation, breakable scenery, start gate and countdown, scenery flags, rails, host-scenery isolation, course name in the frontend (L987–L1214)
- GameCube Garibaldi in Dolphin for Android on the Odin (L749, L752)

## Controls and mobile app

- Grab 1–4 buttons; boost + jump prep; C-stick touch; four-input grab mask; physical pad test (L1218–L1226)
- Control mapping doc (L747)
- iPhone: fast-start/Full Reset/checkpoint, redesigned menu, lifecycle Resume, cold-start profile, 15-min soak, memory card (L1237–L1280)
- Android native build of the GameCube runtime (L1284)

## Housekeeping carried here

- `fsck_exfat` the SSD at a quiet time (L415), superseded in practice by the V-lane storage cutover.
