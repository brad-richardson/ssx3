# X11B — low-thinking dense Qwen scheduler trial, partial

Orchestrator audit of a partial worker table, not a worker verdict. Local
Qwen3.8-27B used per-pane `thinking_budget=512` and the same pinned fork
`4f93216` excerpt as X11 (`../X11/source-excerpts.txt`). The following
rows include the orchestrator's two source-scope/arithmetic corrections.

| Case | Source observation | Citation |
| --- | --- | --- |
| Due membership | `processDueDeadlines` re-scans all `m_deadlines` on each loop pass; an item is a pacing candidate if `item.deadlineCycle <= m_eeCycle` (guest-cycle check vs the live EE cycle, not host time), which also drives `m_eventCv.wait_until(pacingDeadline)` when `now < pacingDeadline`; then `std::partition` moves into the `due` batch exactly those items with `deadlineCycle <= m_eeCycle && hostDeadline <= pacedNow` (re-read after the wait), so membership is the two-condition AND of guest cycle reached AND host wall-clock reached; the `due` items are erased from `m_deadlines` and `updateNextDeadline()` runs before dispatch (dispatch itself, `processEvent`, is outside the windows — gap). | excerpt lines 2555-2569 (cycle cond 2564), 2572-2588 (wait), 2590-2599 (partition/erase/updateNextDeadline) |
| Within-batch order | After the critical section, `due` is sorted by `deadlineCycle`, `event.type`, `event.id`, then insertion `sequence`, each ascending. The host deadline is absent from this comparator. The shown pool is scanned and partitioned; no pool sort appears in these windows. Host gating can split otherwise cycle-due records into separate batches and thereby affect their dispatch order. | excerpt lines 2553-2616 |
| Idle timer versus event | `waitForEvent` returns immediately for queued events or stop. It chooses the scheduled record with least `(deadlineCycle, sequence)`, then compares **that record's host deadline** with `timerHostDeadline = now + eeCyclesToHostDuration(timerCycles)`; the timer replaces the target only when its host deadline is earlier. If `wait_until` times out with no queued event, it advances the selected guest-cycle gap in `accountCycles` steps of at most `UINT32_MAX` cycles each and flags a checkpoint. A signaled wait does not advance cycles here. | excerpt lines 2850-2905 |
| Posted event cycle | Unanswered in the excerpt. `postEvent` appends the event verbatim to `m_events` (no `m_deadlines` insert, no cycle/deadline assignment, no `updateNextDeadline`); `processPendingEvents` drains the deque FIFO and calls `processEvent(event)` after `processDueDeadlines` and EE-timer IRQ dispatch. Whether the guest cycle a posted event is seen at is stamped inside `processEvent` (or already carried on `EeEvent`) is not in any window. `processPendingEvents` has no visible loop bound or re-scan — gap. | excerpt lines 838-852, 2520-2541 |

LSP findReferences probe: one call, `findReferences` on `processDueDeadlines` at its definition in `~/dev/ssx3-work/E55A2/PS2Recomp/ps2xRuntime/src/lib/Kernel/EeScheduler.cpp` (line 2553, char 19, matching the pinned excerpt). Tool returned: `No results found for findReferences` — no usable locations. The E55A2 checkout is at pin `4f93216`, so the position is correct and the empty result is a tool/indexing gap, recorded as such per the brief, not evidence that the symbol has no callers. No second probe (budget: one). The four semantic rows stand on the excerpt alone.

## Trial result and tool gaps

X11B wrote four cited rows and called LSP once. The LSP returned no
references at the correct fork file/definition position; no caller
absence follows from that result. It used three directory Globs despite
the brief's exact paths, missed the 3-minute first-write target, and
reached about 24.3k context at the 8-minute cap. The worker did not run
`check_x11.py` or commit its report. The orchestrator stopped and closed
the pane, then corrected an unsupported fork-wide pool-sort claim and
two mistakes in the uint32 chunk arithmetic. The original checker
rejected a valid citation range because it required literal `2553`;
the orchestrator changed it to test line coverage inside cited ranges,
then it passed on this corrected table. That is an orchestrator check,
not a worker acceptance. No source edit, build,
boot, device action or E55 verdict came from this trial. Compared with
X11's default 8192-token thinking budget, 512 produced a table and one
LSP call, but still failed the bounded worker handoff.
