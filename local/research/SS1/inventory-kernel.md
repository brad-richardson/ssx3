# SS1 inventory: EE scheduler + syscalls

Read-only subagent read for SS1 (Opus); file:line against fork a3efbfe, paths relative to ps2xRuntime/.

## Save-state feasibility study: EE scheduler and syscall state inventory (read-only)

All paths are relative to `/Users/brad/dev/ssx3-work/SS1/PS2Recomp/ps2xRuntime`. Nothing was edited, built or run.

**R5900Context** (`include/ps2_runtime.h:58-195`) holds no host pointers. It is plain data: `__m128i r[32]`, pc, insn_count, hi/lo, VU0 regs, COP0, llbit/lladdr, in_delay_slot/branch_pc, cop2_ccr, FPU regs. The constructor memsets it and seeds vf0/Q/R/status (lines 144-168). A memcpy of `sizeof` is enough to serialize it.

### 1. Mutable state

Plans used below:
- **C** = captured
- **R** = rebuildable (recompute after init, or drop)
- **B** = blocker

**EeScheduler members (`include/runtime/ee_scheduler.h`)**

| item | file:line | type | host ptr / fn / time? | plan | notes |
|---|---|---|---|---|---|
| m_runtime | h:418 | PS2Runtime& | host ref | R | rebind |
| m_cycleOnlyEvents | h:421 | const bool | env | R | from PS2X_DETERMINISTIC (cpp:196-199). Must be equal at save and restore. Bit-exact restore only makes sense when it is true (see §3). |
| m_detHashEvery | h:423 | u64 | env | R | diagnostic |
| m_rdram | h:425 | uint8_t* | host ptr | R | set by reset() (cpp:471) |
| m_readyQueues | h:426 | array<deque<int>,128> | no | C | order inside each deque matters |
| m_threads | h:427 | unordered_map<int,GuestThread> | contains std::function | C (+B) | see GuestThread rows. Iteration order is guest-visible (§4.3). |
| m_semaphores / m_eventFlags | h:428-429 | map of POD + deque<int> waiters | no | C | waiter order matters |
| m_alarms, m_intcHandlers, m_dmacHandlers | h:430-432 | map of POD | no | C | handler `order` is unique (cpp:2084), so dispatchIrq's sort (cpp:2201) does not depend on map order |
| m_next*Id, head/tail orders | h:433-443 | int | no | C | |
| m_enabledIntcMask / m_enabledDmacMask | h:444-445 | u32 | no | C | |
| m_currentThreadId | h:446 | int | no | C | can be non-zero at the loop top (a thread keeps running across slices) |
| m_rescheduleRequested, m_timeSliceExpired, m_insideInterrupt, m_soundClockStarted | h:447-450 | bool | no | C | m_insideInterrupt is always false at the loop top (cpp:898/914/920) |
| m_pendingEeTimerInterrupts | h:451 | u32 | no | C | zeroed by processPendingEvents (cpp:2720) |
| m_eeCycle, m_countCycle, m_count, m_sliceEndCycle | h:452-455 | u64/u32 | no | C | |
| m_executorThread | h:456 | std::thread::id | host | R | reset() (cpp:470) |
| m_running, m_guestExecuting, m_stopRequested, m_checkpointPending | h:457-460 | atomic<bool> | no | R | recompute checkpointPending the way cpp:2740-2743 does |
| m_debugPublishCountdown | h:461 | u32 | no | C | sets when copyMainContextToRuntime runs (cpp:772-781). Cheap, so keep it. |
| m_eventMutex, m_eventCv | h:463-464 | sync | host | R | |
| m_events | h:465 | deque<EeEvent> | no | C | empty after a drain (cpp:2728-2736). ExternalWake has no cycle stamp (h:419-420). postEeEvent has no in-repo callers (ps2_runtime.cpp:3820). |
| m_deadlines | h:466 | vector<ScheduledEvent> | **host time** (hostDeadline, h:374) | C + rebase | cycle, event and sequence are captured; hostDeadline must be rebased (§3) |
| m_pendingInvocations | h:467 | deque<GuestInvocation> | onComplete std::function | C (+B) | only MPEG.cpp:1876 queues an entry that has onComplete |
| m_eventSequence, m_invocationSequence | h:468-469 | u64 | no | C | tie-breaks at cpp:2827, 3110, 3171 |
| m_vsyncTick | h:470 | u64 | no | C | |
| m_vsyncPacer | h:473 | Pacer (m_nextNs) | **host time** | R | set to `Pacer{}` as reset() does (cpp:514) |
| m_vsyncPace | h:474 | bool | env | R | |
| m_vsyncFlagAddress … m_gsVSyncCallbackSp | h:475-479 | u32 | no | C | |
| m_invocationStackTops | h:480 | unordered_map<u64,u32> | no (guest addresses) | C | key is `(thread id<<32)\|depth` (cpp:2037). Also capture PS2Runtime m_asyncCallbackStackTop (ps2_runtime.cpp:3493). |
| m_nextDeadlineCycle | h:481 | atomic<u64> | no | R | updateNextDeadline() (cpp:3157) |
| m_snapshotMutex, m_snapshot, m_snapshotSequence | h:483-485 | diag copy | no | R | publishSnapshot() (cpp:2462) |

**GuestThread, EeWaitState and GuestInvocation fields**

| item | file:line | type | host ptr / fn / time? | plan | notes |
|---|---|---|---|---|---|
| GuestThread POD fields + context | h:107-122 | POD | no | C | |
| EeWaitState.reason / payload | h:80-81 | enum + variant of POD | no | C | |
| **EeWaitState.completion** | h:82 | std::function<void(R5900Context&)> | **fn** | **B** | §2 |
| **GuestThread.resumeCompletion** | h:124 | std::function | **fn** | **B** | makeReady moves the wait completion here (cpp:2668-2671); run() calls it before the next slice (cpp:755-770) |
| GuestThread.invocations | h:125 | vector<GuestInvocation> | contains onComplete | C (+B) | kind, sequence, tag and context are POD |
| **GuestInvocation.onComplete** | h:102 | std::function<void(const ctx&, ctx&)> | **fn** | **B** | runs on pc==0 (cpp:788-804) |

**Statics in EeScheduler.cpp, the pacer and the unwind header**

| item | file:line | type | host ptr / fn / time? | plan | notes |
|---|---|---|---|---|---|
| s_detHashLines | cpp:211 | atomic<u32> | no | R | diagnostic |
| diagPeriodMs, diagSemaEnabled, diagSemaS0Enabled, intcLogEnabled, coverageTick | cpp:116, 174, 186, 1991, 2007 | static const env caches | env | R | |
| g_diagSchedCounts | cpp:166 | unordered_map<int,u64> | no | R (drop) | diagnostic |
| run() s_diagTick, s_diagLastMs, s_diagBlock | cpp:554-556 | static u64 | host ms | R (drop) | diagnostic |
| run() idleSince, idleDumpPrinted | cpp:690-691 | static time_point/bool | host time | R (drop) | diagnostic |
| Pacer m_period, m_nextNs | ps2_vsync_pacer.h:79-80 | i64 | host steady ns | R | the first onVsync re-anchors (h:46-49) |
| ps2_guest_unwind pending | ee_guest_unwind.h:15 | thread_local bool | no | R | cleared before each slice (cpp:910) |

**Syscalls (`src/lib/Kernel/Syscalls/`)**

| item | file:line | type | host ptr / fn / time? | plan | notes |
|---|---|---|---|---|---|
| g_fileDescriptors | Helpers/State.h:6 | unordered_map<int,FILE*> | **host FILE\*** | **B** if any fd is open | no path or offset is stored (FileIO.cpp:14-15, 104), so a file can't be reopened. Record path+pos+mode, or require zero open fds. |
| g_nextFd | State.h:7 | int | no | C | |
| g_rpc_servers, g_rpc_clients | State.h:212-213 | maps of int / guest addr | no | C | |
| g_sif_rpc_debug_history, g_sif_rpc_debug_next_seq | State.h:214-215 | array with `const char* op` | host ptr (string literal) | R (drop) | debug ring |
| g_rpc_initialized, next_id, packet_index, server_index, active_queue | State.h:218-222 | bool/u32 | no | C | packet_index and server_index pick guest pool slots (Runtime.h:126, 137) |
| g_bootmode_initialized, pool_offset, addresses | State.h:224-226 | bool/u32/map | no | C | |
| g_tls_index | State.h:234 | u32 | no | C | guest slot allocator (Runtime.h:444) |
| g_osd_config_initialized, raw, raw2 | State.h:237-239 | bool/u32 | host timezone at init | C | timezone is pinned only when deterministic (Runtime.h:308-317) |
| g_ps2_paths_initialized, host/cdrom base and cwd, g_ps2_cwd_device | State.h:242-247 | filesystem::path / string | host paths | R (base) / C (cwd, device) | |
| g_sif_modules_by_id, g_sif_module_id_by_path, g_next_sif_module_id | State.h:355-357 | maps / strings | no | C | ids are guest-visible (Loader.h:114) |
| g_sif_module_log_count | State.h:358 | u32 | no | R | log cap |
| mutexes | State.h:158, 216-217, 223, 233, 236, 241, 354 | sync | host | R | |
| g_vagAccum | FileIO.cpp:41 | unordered_map<int,{vector<u8>, u32}> | no | C | keyed by fd, so it goes with the fd blocker |
| g_deci2Sessions, g_nextDeci2Socket | Deci2.cpp:17-18 | map of POD / int | no | C | probably empty |
| g_deci2LogCount, s_unknownDeci2Logs | Deci2.cpp:19, 234 | atomic | no | R | diagnostic |
| g_diagSyscallCounts, LastMs, Block, s_diagTick | Dispatcher.cpp:47-49, 94 | diag | host ms | R (drop) | |
| env caches | Dispatcher.cpp:15, Sync.cpp:18, System.cpp:49 | static const | env | R | |
| loggedSignatures, handshakeCount, logCount | RPC.cpp:112, 1154, 1164 | log caps | no | R | |
| g_ssx3SifHandshakeEnabled | RPC.cpp:165 | atomic<bool> | no | R | set by the game-override apply at load (RPC.cpp:172) |
| s_logged, s_unknownCounts, s_findAddress*Logs | System.cpp:70, 481, 832-833 | diag | no | R | |
| TraceChannelState | TraceChannel.cpp:113 | FILE*, steady_clock | host | R | diagnostic |
| g_k1Enabled | Ssx3CopiedPayload.cpp:34 | atomic<bool> | no | R | set at load (line 46) |
| g_lookupServed … g_provenanceFail | Ssx3CopiedPayload.cpp:36-39 | atomic counters | no | R | log sequence numbers only |
| **g_wiredAlloc** | Ssx3CopiedPayload.cpp:41 | atomic<u32> | no | **C** | the guest sees it as a return value (line 175) |
| warnCount, warned, secFilterLogCount, logCount, successLogs | Helpers/Runtime.h:24, 78, 273; Loader.h:262, 403, 431 | log caps | no | R | |

Outside scope but needed for a full save: PS2Runtime::m_eeExitHandlers (ps2_runtime.cpp:3860), the guest heap, m_asyncCallbackStackTop, the CD.cpp g_cdCallback* and g_cdStreamTiming globals, MPEG g_mpeg_stub_state, the snd_spike State, and the PS2Memory EE timers and GS registers.

### 2. Sites that store std::function completions (exhaustive over src/lib + include)

| file:line | caller | captures (name: type) | tagged descriptor? |
|---|---|---|---|
| src/lib/ps2_runtime.cpp:3849-3854 (waitVSync completion) | PS2Runtime::eeWaitVSyncTicks | resumePc: u32 | Yes: {SetPc, pc}. There are no callers in the repo; generated code outside it may call it. |
| src/lib/Kernel/Stubs/CD.cpp:1002-1012 (waitVSync completion) | continueCdStRead (CD.cpp:940) | rdram: uint8_t*, runtime: PS2Runtime*, state: CdStReadContinuation (4×u32: requestedSectors, buffer, errorAddress, sectorsRead; CD.cpp:923-929) | Yes: {CdStReadContinue, 4 ints}. rdram and runtime are process singletons. |
| src/lib/Kernel/Stubs/MPEG.cpp:2723-2734 (waitExternal completion) | getMpegPicture (MPEG.cpp:2627) | rdram, runtime, delivery: shared_ptr<MpegNonStreamDelivery> (MPEG.cpp:691-703; the body doesn't use it) | Yes: {MpegGetPictureRetry}. The shared_ptr only keeps the delivery alive; restoring it depends on MPEG state (§4). |
| src/lib/Kernel/Stubs/MPEG.cpp:2760-2770 (waitVSync completion) | getMpegPicture | same as the row above | Yes: same descriptor |
| src/lib/Kernel/Stubs/IPU.cpp:86-89 (onComplete) | sceIpuInit (IPU.cpp:53) | rdram, runtime | Yes: {IpuInitComplete} |
| src/lib/Kernel/Syscalls/RPC.cpp:798-801 (onComplete) | SifCallRpc (RPC.cpp:416) | finishCall, a lambda (RPC.cpp:665) with `[=]` of: iopResult (ps2x::iop::RpcResult, POD of about 13 words, ps2xIOP/include/ps2x/iop/iop_types.h:89-100), receiveBuffer, receiveSize, sendBuf, sendSize, guestDefaultResult, clientPtr, serverPtr, sid, rpcNum, mode, endFunction, endParameter, completionSemaphore (all u32), rdram, runtime | Yes, but about 26 ints: {RpcFinishCall, …}. It calls invokeCurrent again (RPC.cpp:783). |
| src/lib/Kernel/Syscalls/RPC.cpp:779-782 (onComplete) | SifCallRpc (the finishCall callback path) | completeClient, a lambda (RPC.cpp:699) with `[=]` of everything above plus handled, resultPointer, copiedFallback, zeroedFallback | Yes: {RpcCompleteClient, clientPtr, …}. The only guest-affecting effect is `g_rpc_clients[clientPtr].busy=false` (RPC.cpp:703); the rest is debug/park tallies. |
| src/lib/Kernel/Stubs/MPEG.cpp:1876-1879 (onComplete, queued) | dispatchGuestStreamCallback (MPEG.cpp:1842) | runtime, cbDataAddr: u32 | Yes: {GuestFree, addr} |
| src/lib/Kernel/Stubs/MPEG.cpp:1922-1935 (onComplete) | dispatchGuestNonStreamCallback (MPEG.cpp:1883) | rdram, runtime, delivery: shared_ptr<MpegNonStreamDelivery> (mutable: nextCallback, callbackData, cancelled, vector callbacks); it is shared with the MPEG `pending` weak_ptr (MPEG.cpp:2646, 2659) | Partly. Needs {MpegNonStreamNext, delivery index} plus the delivery object serialized once, with its identity kept. |
| src/lib/Kernel/Syscalls/System.cpp:543-546 (onComplete) | dispatchSyscallOverride (System.cpp:503) | nothing | Yes: {CopyV0} |
| src/lib/Kernel/Syscalls/Thread.cpp:99-102 (onComplete) | exitThreadWithHandlers (Thread.cpp:71) | runtime, deleteThread: bool | Yes: {ExitCurrent, deleteThread} |

These sites construct a GuestInvocation or wait with **no** completion: Interrupt.cpp:81 (WaitVSyncTick), EeScheduler.cpp:1314/1735/1863 (Sleep, Semaphore and EventFlag waits), EeScheduler.cpp:2213/2924/2973 (IRQ, GS callback, Alarm), CD.cpp:76 (CD callback), include/ps2_snd_spike.h:346 (sound handler). EeScheduler.cpp:2956 passes a `[this]` lambda to onSoundTick but only for the length of the call; it is not stored.

**Summary:** 11 storage sites. 9 map directly onto an enum plus at most 4 ints (the two RPC ones need about 26 ints). The two MPEG delivery sites also need the MPEG stub state to be serializable.

### 3. Run loop, save point and host-time rebasing

- **Where a vsync is processed:** `processEvent` case VBlankStart (EeScheduler.cpp:2877-2946). It does the pacer sleep (2878-2884), `++m_vsyncTick` (2885), writes the flag/tick (2901-2920), calls completeVSync (2921), queues the GS callback (2922-2932) and dispatches INTC cause 2 (2942). It is reached from processDueDeadlines (2836-2845), which also reschedules VBlankEnd/VBlankStart there. processDueDeadlines runs inside processPendingEvents (2715), which is called at run() lines 566 and 931.
- **No guest frames on the host stack at the loop top.** The only place guest code runs is `function(m_rdram, &context, &m_runtime)` (911). It either returns or throws EeDispatcherTransfer, caught at 917. Checkpoints inside nested generated code unwind by returning (ee_guest_unwind.h:3-10; eeCheckpointDue marks this at ps2_runtime.cpp:3825-3832). So at the top of `while` (558), and right after `processPendingEvents()` (566-570), no guest code is on the host stack, m_events has been drained (2728-2736) and due deadlines have fired.
- **Natural save point:** set a "save requested" flag in VBlankStart, then take the save at 567-570, the loop iteration after processPendingEvents returns. At that point:
  - m_currentThreadId may be non-zero. That is fine, because a preempted-in-place thread resumes from `context.pc` (891-894, 932-940).
  - VBlank-queued GuestInvocations (GS callback, IRQ handlers) are sitting in m_pendingInvocations, with no onComplete.
  - Any Ready thread whose wait completed can still hold `resumeCompletion` (set at 2671, run at 755). Any Waiting thread can hold `wait.completion`. Every nested invocation holds its onComplete. This is why §2 is the gating work, unless you instead defer the save until all of these are empty.
- **ScheduledEvent::hostDeadline** is written at:
  - reset: EeScheduler.cpp:537
  - setAlarm: 1890
  - startSoundClock: 1931 (`now()`)
  - the VBlank chain: 2839 and 2842 (`previous hostDeadline + period`, so the absolute anchor carries forward forever)
  - SoundTick: 2960

  It is read at:
  - the non-deterministic gate: 2771-2808. Events fire only when `deadlineCycle <= m_eeCycle && hostDeadline <= now`, with a wait_until at 2790.
  - the idle wait in waitForEvent: 3113 and 3127. This is used in both modes.

  In deterministic mode, host deadlines never gate events (2756-2767), but a stale value after restore makes the idle `wait_until` either return at once or hang, since the steady_clock epoch differs per boot. **Rebase** each entry to `now + eeCyclesToHostDuration(deadlineCycle - m_eeCycle)` (helper at EeScheduler.cpp:81-88), or to `now_restore + (hostDeadline - now_save)`. The timer deadline in waitForEvent is recomputed from `now()` each call (3117), so it needs no rebase.
- **Pacer:** `m_nextNs` is an absolute steady-clock nanosecond value (ps2_vsync_pacer.h:80). Restore it as `Pacer{}`, the same as reset() at 514; the first vsync re-anchors without sleeping (h:46-49). The pacer never touches guest state (h:14-16).
- **Mode:** default mode (m_cycleOnlyEvents=false) lets host time decide when events are delivered relative to guest cycles (2771-2808). Bit-exact save/restore is only meaningful with PS2X_DETERMINISTIC=1, and both processes have to agree on it (cpp:196-199).

### 4. True blockers

1. **std::function closures** (h:82, h:102, h:124; the 11 sites in §2). They can't be serialized. Either replace them with a tagged descriptor (enum plus ints, rebound to the rdram/runtime singletons on restore), or only save when every completion, resumeCompletion and onComplete is empty.
2. **MPEG deliveries.** The shared_ptr<MpegNonStreamDelivery> is shared between completions and MPEG stub state (MPEG.cpp:1922, 2646-2659), and MPEG state probably holds the host decoder. Treat it as a blocker unless saves are refused while any MPEG wait or delivery is live. A race normally has no movie playing.
3. **g_fileDescriptors holds host FILE\* with no path or offset recorded** (State.h:6; FileIO.cpp:14-15). This blocks any save taken while a fio fd is open. Either record path, mode and position at fioOpen, or refuse the save. g_vagAccum (FileIO.cpp:41) goes with the fds.
4. **unordered_map iteration order can reach the guest.** acquireInvocationThread (EeScheduler.cpp:2541-2549) returns the first dormant negative-id thread in `m_threads` iteration order. That choice changes `owner->id`, which changes the invocationStackTop key (2037) and therefore the guest `$sp` and stack contents. A restored map won't reliably reproduce the libc++ iteration order. Make the selection deterministic (for example the lowest id) or use an ordered map. The other m_threads walks sort their results (2311, 2343, 2493), and dispatchIrq sorts by a unique order.
5. **Host time in guest-visible state:** hostDeadline (h:374) and the default-mode gating (§3). The OSD timezone is taken from the host unless deterministic (Helpers/Runtime.h:308-317); that value is captured in g_osd_config_raw, so it is fine once saved.
6. **Not a blocker, but unverified:** eeWaitVSyncTicks (ps2_runtime.cpp:3845) and postEeEvent (3820) have no callers in the repo. If the external generated code in PS2X_GAME_CODEGEN_DIR calls eeWaitVSyncTicks, its `{SetPc}` descriptor covers it.
