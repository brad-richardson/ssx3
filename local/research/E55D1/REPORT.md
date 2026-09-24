# E55D1 — ExternalWake placement and pad/card boundary audit

Read-only source audit at fork pin `ddaee780288adb076ce40050d87969b20bc4bb05`
(branch `e55-vblank-hash` in `~/dev/ssx3-work/E55C2/PS2Recomp`, clean at check).
ssx3 checkout `git log -1` at audit time: `b4ab748 [orch] Queue N8D7G replay
and parallel source audits` (see commit section for the log line at commit time).
No source edit, build, boot, device, web, upstream contact or push in this part.
This task does not own the E/fork mutator lease.

Prior context: `local/research/E55B1/REPORT.md` (scheduler host-deadline audit),
`local/research/E55C2/REPORT.md` (VBlank XXH64 tap + 3-boot observation),
E55 subsection of `docs/todo.md`. Companion receipt: `source-map.tsv`
(8 rows; columns `path,producer,enqueue_or_state,drain_or_consumer,
cycle_anchor,hash_relation,unknown`).

## 1. Where an external post enters

`EeScheduler::postEvent` (`EeScheduler.cpp:950-964`) is the only enqueue
entry: `Stop` short-circuits to `requestStop`; anything else is appended to
`m_events` under `m_eventMutex`, sets `m_checkpointPending`, and notifies
`m_eventCv`. The cross-thread forwarder `PS2Runtime::postEeEvent`
(`ps2_runtime.cpp:3522-3525`) just calls it. Header contract
(`ee_scheduler.h:276-284`): all kernel calls except `postEvent`/
`requestStop` execute on the EE executor and need no host synchronization —
`postEvent` is the designated host-thread entry.

Producer search (`rg -n "postEvent\(|postEeEvent|ExternalWake"` over
`ps2xRuntime/src`, `ps2xRuntime/include`, `ps2xTest/src`): **zero production
call sites** outside the definition, the forwarder, and test helpers
(`ps2_runtime_kernel_tests.cpp:53-64` inject `scheduleEvent`/`processEvent`
directly). An LSP `findReferences` on the forwarder definition returned no
results (no usable LSP server in this environment; the `rg` evidence above
is the citable result). So at this pin the ExternalWake enqueue path is live
code with **no production producer**: nothing in-tree posts `EeEventType::
ExternalWake` from a host thread.

Related but distinct: the MPEG stubs call
`EeScheduler::completeExternalWait` **directly, synchronously, on the
executor thread** (e.g. `MPEG.cpp:2175,2199,2234,2419,2465,2471,2558,2564`)
from inside guest stub execution, and `waitExternal(Mpeg,...)` is called from
one site (`MPEG.cpp:2723-2724`). These never touch `m_events`, never cross
threads, and never take a guest-cycle timestamp. `completeExternalWait`
(`EeScheduler.cpp:2242-2271`) asserts executor, matches `(type, token)` over
threads in `Waiting`/`WaitingSuspended` with reason `External` or `Mpeg`,
wakes matches sorted by thread id, and publishes a snapshot. There is no
`EeWaitReason::External` waiter-producer in-tree either (only debug-panel and
`Thread.cpp` display/poll references).

## 2. When it is drained relative to guest-cycle accounting and VBlank hashing

Drain order in `processPendingEvents` (`EeScheduler.cpp:2632-2663`):
(1) `processDueDeadlines`, (2) pending EE-timer IRQs in timer-index order,
(3) the whole swapped `m_events` FIFO via `processEvent`. The ExternalWake
branch (`2852-2854`) just runs `completeExternalWait(event.id, event.value,
KE_OK)` — no cycle advance at drain.

Cycle anchor: none exists. `EeEvent` (`ee_scheduler.h:236-241`) carries
`(type, id, value)` only; `ScheduledEvent` (`ee_scheduler.h:367-373`) adds
`deadlineCycle/hostDeadline/sequence`, but `postEvent` never creates one.
`m_eeCycle` advances only in `accountCycles` (`1000-1014`, at least 1 cycle
per call, plus timer-IRQ side channel) and in `waitForEvent` timeout jumps
(`3026-3038`). The deterministic flag `m_cycleOnlyEvents`
(`EeScheduler.cpp:192-198`, exact `PS2X_DETERMINISTIC=1`; header note
`ee_scheduler.h:415-417`) changes only the *scheduled* paths — whole
cycle-due set extraction (`2673-2685`) and guest-cycle timer choice
(`3015`) — and explicitly leaves ExternalWake outside the ordering guarantee.
A queued post therefore floats against `m_eeCycle`: its observable position
is "whichever `processPendingEvents` pass swaps the FIFO next", and in
`waitForEvent` any arrival both wakes the waiter early and suppresses a
pending fast-forward (`3023-3038`).

Hash-tap placement (`EeScheduler.cpp:2794-2851`; tap `229-300`,
`ee_scheduler.h:391-402`): inside the `VBlankStart` branch, after
`++m_vsyncTick`, GS `vsyncTick` store, CSR update, guest flag/tick writes,
`completeVSync` waiter wake, GsCallback queueing, and `dispatchIrq(false,2)`
— `emitDetHashTap()` runs last (`2848-2850`). Snapshot covers RDRAM
(32 MiB), scratchpad, VU1 data/code (16 KiB each), and the VU1
`execute`-start count folded as explicit little-endian bytes; gated by
`tick % EVERY == 0`, 4096-line cap, 256-byte line cap. NOT hashed: thread/
waiter/readiness state, `m_events`/`m_deadlines` contents, pad port state,
host card files. A wake that changes only readiness is invisible at the
current tick and appears only via the woken thread's later guest stores.

## 3. Which pad/card paths can change the hashed state or guest actions

Pad merge is synchronous at guest-read time, not a queued external post.
`scePadRead` (`Pad.cpp:1223-1277`) resolves `data = getMemPtr(rdram,
dataAddr)` and calls `readPadPortData` (`843-916`), which merges, in strict
priority: (a) `g_padOverrideState` under `g_padOverrideMutex` (set/cleared by
`setPadOverrideState`/`clearPadOverride`, `1461-1476`); else (b)
`PSPadBackend::readState` (`ps2_pad.cpp:29-147`: gamepad at index 0, or
keyboard when no gamepad; non-iOS builds use keyboard only when no gamepad);
else (c) legacy `applyGamepadState` + `applyKeyboardState` (`671-767`,
note the float→byte mapping differs from the backend's: `axisToByte`
clamp+lround vs `128+axis*127` truncation). Then `padStimOnRead` (dev-only
stim, `77-200`: read-count + wall-minimum gates) and `padScriptOnRead`
(`584-642`: entries applied while `nowMs` in `[atMs, atMs+holdMs)`).
`fillPadStatus` (`819-841`) writes the 32-byte guest buffer; port-open
zero-fills 32 bytes (`1185-1221`). The vsync clock maps guest tick to ms
(`tick*100000/5994`, `507-512`) using the GS vsync tick sampled at the read
(`895-897`); the wall clock uses `steady_clock`. Cycle anchor: the consumed
value is fixed at the guest's `scePadRead` call (guest pc/readCount), so the
boundary is per-read sampling, not host arrival. Hash relation: direct — the
32-byte buffer is an RDRAM store hashed at the next tap.

Virtual-pad producer runs on the render thread: `PS2Runtime::run`'s frame
loop stores `pressedMask` into `ps2x::vpad::liveMask` every frame
(`ps2_runtime.cpp:3839-3854`), or 0 when a physical pad is in use; the
executor thread ORs it into `btns` at read time (`ps2_pad.cpp:142`).
`activeTestTouches` indexes dev-only script touches by guest vsync tick
(`3844-3846`). Producer cadence is host frames; consumer cadence is guest
reads; the store itself carries no guest-cycle stamp.

Card I/O is synchronous executor-thread file I/O into RDRAM. Root:
`getMcRootPath` (`MemoryCard.cpp:118-155`) from `PS2Runtime::getIoPaths().
mcRoot`, set from `PS2X_MC_ROOT` (`main.cpp:270-275`,
`ps2_ios_runtime.mm:110`) or defaulted to `elfDirectory/mc0`
(`ps2_runtime.cpp:1421-1423,1442`); port 1 derives mc1 by leaf rewrite.
Mutating paths: `sceMcRead` freads host bytes straight into the RDRAM dst
(`1094-1105`); `sceMcGetDir` memcpys `SceMcTblGetDir` entries into RDRAM
(`839-843`); `sceMcGetInfo`/`sceMcSync` write type/free/format and
cmd/result words (`905-929,1254-1268`); immediate model — every op completes
in the stub, `sceMcSync` returns 1 finished / -1 idle (`1226-1273`).
Host-clock injection: `sceMcGetDir` stamps `.`/`..` and mtime-fallback
entries with `std::time(nullptr)` (`776-784`) via `fillMcDirTableEntry`
(`314-331`), and real entries carry host `last_write_time`/`file_size`
(`819-830`); in-stub re-sort is case-insensitive (`802-808`) but write-time
errors fall back to host now. Hash relation: direct and strongest of the
three families — file bytes, directory tables, and timestamps are RDRAM
stores. E55C2's repeatability observation used empty cards with identical
manifest `f94015964371517ad24d36c71ea0c9bdc6fb4a23f3c46d7cc0def479feccb9ce`;
nonempty-card isolation is unproved.

Correct-behavior model (equal inputs ⇒ same dequeue boundary and hash
prefix): with zero production ExternalWake posters, empty cards, and a
vsync-clocked (or unset) pad script, repeated boots from pinned inputs
should drain identical `m_events` FIFO contents (empty) at identical
`processPendingEvents` passes and hash identical RDRAM prefixes. The three
alternatives and their single distinguishing observables are tabled below.

## 4. Discriminating experiments (each with null control)

| # | Family isolated | Minimal experiment (I26-FAST, `PS2X_DETERMINISTIC=1`, `PS2X_DET_HASH_EVERY=1`, all else pinned) | Observable that separates it from the other two | Null control |
|---|---|---|---|---|
| 1 | Host-arrival reordering (ExternalWake/dequeue boundary) | A: test-only `postEeEvent(ExternalWake{id=7,value=9})` injected from a helper thread at a fixed wall delay after tick 500 vs B: same injection after tick 1500, with a planted `waitExternal(External,7,9)` waiter; guest pad fixed to vsync script, cards empty | First tick whose waiter thread leaves `Waiting` (kernel snapshot /Diag) shifts with injection tick while the pad-script tick map and card manifest are byte-identical across A/B; pad or card causes cannot move a waiter wake without changing pad bytes or RDRAM file bytes | Same boot with no injection: waiter stays `Waiting`, hash prefix equals both runs' common prefix; proves the wake, not the harness, moved the boundary |
| 2 | Pad merge variance | A: `PS2X_PAD_SCRIPT_CLOCK=vsync` fixed script vs B: `PS2X_PAD_SCRIPT_CLOCK=wall` (or live keyboard/gamepad) replaying the same nominal buttons; cards empty, no ExternalWake waiter planted | `scePadRead` 32-byte guest buffers (E3 `pad-read` tap or readCount-indexed dump) differ at the same guest read index while card dir/file bytes and waiter-wake ticks are identical; arrival/card causes predict identical pad buffers | vsync-script A/A repeat: identical pad buffers at every read index; proves the merge, not host timing elsewhere, produced the B delta |
| 3 | Card contents/state | A: empty cards (E55C2 manifest pin) vs B: one extra file (or one-byte file edit, or touched mtime) in `mc0`; pad on fixed vsync script, no waiter planted | `sceMcGetDir` table bytes / `sceMcRead` payload bytes in RDRAM (E3 `mc-getdir`/`mc-read` ranges) and the next VBlank combined hash differ at the first card-touching tick while pad buffers and waiter states match; arrival/pad causes predict identical card bytes | A/A repeat with untouched mtimes: identical dir-table bytes and hash prefix; proves file state, not clock jitter, produced the B delta |

Notes: experiments 2–3 need no scheduler change (pad/card are synchronous
guest-call paths). Experiment 1 needs a test-only injection seam because no
production ExternalWake poster exists at this pin; it must not ship as a
placement policy. Do not run boots in this part (brief forbids them).

## 5. Disagreements with E55B1 assumptions

1. E55B1 §"Uncertain event semantics" said ExternalWake "has no
   guest-cycle timestamp ... this audit cannot assign its deterministic
   guest cycle" and its sequences treated early/late posts as reachable
   host arrivals. At `ddaee78` this is sharper: there is **no production
   poster at all** (rg-clean + LSP-empty), so the early/late-post sequences
   are test-only scenarios, not live-boot hazards. The open question is not
   "when does the live post land" but "should any production path ever post,
   and if so with what stamp" — still Part 2's decision, not this part's.
2. E55B1's batch-ordering statements predate E55B2's `m_cycleOnlyEvents`.
   Confirmed present and covering exactly the scheduled/idle-timer paths
   (`2673-2685`, `3015`); the header comment (`ee_scheduler.h:415-417`)
   now states the ExternalWake exclusion explicitly. No contradiction on
   the scheduled semantics; the exclusion is new evidence.
3. E55B1 listed "pad neutrality, memory-card isolation, and hash tap" as
   separate work. This part closes the mapping: pad merges at guest-read
   time (per-read sampling boundary), card completes synchronously with
   host-clock bytes in the payload (strongest hash coupling), and the tap
   sits after callback queue + INTC2 with kernel/waiter state outside the
   snapshot. E55C2's "live pad merge, card state on other inputs, and
   ExternalWake timing remain possible divergence sources" stands, now with
   exact line anchors.

## 6. Gaps and recommended Part 2 question

Gaps: (a) no producer trace outside the searched fork tree (dedicated
JOINT/IOP/SIO hosts, Android/iOS entry loops, and `ps2xTest` harnesses
beyond the grepped files were not exhaustively walked — the rg covered
`ps2xRuntime/src`, `ps2xRuntime/include`, `ps2xTest/src` for the named
symbols only); (b) LSP cross-file confirmation unavailable (findReferences
returned no results — no working server — so caller/callee links rest on
`rg` + line-range reads, cited exactly); (c) stock-SSX3 reach frequency of
`scePadRead` stick paths, card calls, and any external-waiter use was not
traced here; (d) nondefault RDRAM size tap boundary (E55C2 §memory-size
boundary) still open; (e) `Dmac` branch still empty (`2858-2859`), no rule
inferred; (f) no boot/build/run performed per brief, so all predictions are
source-derived.

Recommended Part 2 question: with zero production ExternalWake posters at
this pin, decide (i) whether any production path should ever enqueue
ExternalWake (or whether the waiter mechanism stays test/MPEG-only with
MPEG's synchronous completion as the model), and only if yes, (ii) what
guest-cycle stamp an enqueued post carries (enqueue-cycle, drain-cycle, or
explicit caller stamp) and where it sits in the
deadlines→timers→FIFO drain order — validated by experiment 1 above plus
its null control before any policy ships. Pad/card isolation (experiments
2–3: vsync-clocked scripts, pinned card manifests/mtimes) proceeds
independently of that decision.

## 7. Commands, receipts, sizes

- `git -C ~/dev/ssx3-work/E55C2/PS2Recomp rev-parse HEAD` →
  `ddaee780288adb076ce40050d87969b20bc4bb05` (matches brief expectation;
  no stop needed). `status --short --branch` → `## e55-vblank-hash` clean
  (no output lines).
- Searched files: `EeScheduler.cpp` (3098 lines), `ee_scheduler.h`
  (477), `ps2_pad.cpp` (147), `ps2_virtual_pad.h`, `Stubs/Pad.cpp`
  (1532), `Stubs/Pad.h` (120), `Stubs/MemoryCard.cpp` (1570),
  `Stubs/MemoryCard.h` (104), `ps2_runtime.cpp` (3890),
  `Stubs/MPEG.cpp` (MPEG waiter/completion sites), `main.cpp:270-275`
  (PS2X_MC_ROOT).
- Key `rg` commands (from the fork root): `rg -n
  "ExternalWake|postEeEvent|postExternal|PS2X_DETERMINISTIC|deterministic|
  DetHash|det-hash|DET_HASH|makeDetHash|..."` (tap + flag map);
  `rg -n "postEeEvent|EeEventType::ExternalWake|EeExternalWait|
  waitExternal" ...`; `rg -n "EeEvent\{|postEvent|postEeEvent|
  ExternalWake" ...`; `rg -n "postEvent|waitExternal|EeWaitReason::
  (External|Mpeg)" ...`; pad/card/host-clock searches as cited inline.
  Reads were small line-range reads of the files above.
- Receipt sizes (must total <80 KiB): see `wc -c` at commit time; both
  files are short text (this report ~14 KiB, TSV ~8 KiB, well under cap).

## 8. Commit

ssx3 `git log -1` before commit: `7860042 [orch] Gate N8D7G Mac selected
capture replay` (note: moved twice during this audit — several lanes commit
to `main`; re-checked before committing per standing rules). Commit: `[E55D1]` with trailer `Orchestrated-By: opencode`, named
text receipts only (`local/research/E55D1/REPORT.md`,
`local/research/E55D1/source-map.tsv`), no push.
