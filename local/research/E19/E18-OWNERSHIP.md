# E18 ownership audit before MPEG mutation

| Shape | Source evidence | Actual-linked non-title receipt | Gate |
|---|---|---|---|
| queueInvocation / RpcCallback, runnable caller | Queue stores no caller owner; scheduler may attach pending invocation to the current runnable thread; zero SP backfilled | callerTid1→callbackTid1; callerSP0x1e00000→callbackSP0xffff0; args and parent saved128 preserved | Same thread in this case; stack differs |
| queueInvocation / RpcCallback, parked caller | Scheduler acquires an invocation thread when no ready caller exists; allocated ids are negative | callerTid1→callbackTid−1; callerSP0x1e00000→callbackSP0xffff0; args preserved; parent resumes after explicit external completion | Required ownership not preserved |
| invokeCurrent / HleCall with copied nonzero SP | Invocation attaches to currentThread; supplied SP survives; pc0 pops invocation and invokes onComplete with untouched parent context | callerTid1→callbackTid1; bothSP0x1e00000; copied arguments; full parent context restored; saved128 preserved; one callback/completion/resume | Selected synchronous caller-owned path |
| Continuation bridge | Existing scheduler pc0 is the HLE-return sentinel. The actual GetPicture wrapper sets parent pc to supplied RA before entering the stub | Current-owner onComplete resumes the MPEG operation before returning to the original parent continuation; callback v0 is ignored | No guest-PC-specific continuation or RPC owner assumed |
| Cancellation | Pending delivery must be invalidated by MPEG deletion/reset; callback data retained while in-flight and freed in onComplete | R5 will preempt the owner before first callback dispatch and cancel; registration order and same-type dedupe covered by R1/R4 | Required before any title boot |
| Receipts | Full pinned sources in sources/before-*.gz; numbered excerpts in ownership-source.json | ownership-dynamic.json and ownership-*.txt; link rc0; title boots0 | Audit precedes behavior mutation |

**E18 OWNERSHIP TAIL COMPLETE — queue ownership fails the required contract; current-thread HleCall selected.**
