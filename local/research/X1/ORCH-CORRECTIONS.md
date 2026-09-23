# X1 — orchestrator corrections (2026-09-22)

Checked against `ps2xRuntime/src/lib/Kernel/Syscalls/Dispatcher.cpp` and the
codegen wrappers (`addiu $v1, $zero, N; syscall`):

| Wrapper | $v1 | Actual syscall | X1 said |
| --- | --- | --- | --- |
| `0x423DA0` | 0x40 | CreateSema | Lread |
| `0x423DC0` | 0x42 | **SignalSema** | Open (0x44) |
| `0x423DE0` | 0x44 | **WaitSema** | (not named) |
| `0x423C90` | 0x2F | GetThreadId | Read |

Consequences: E31's thread 1 (`pc=0x423dc8`, `ra=0x377b6c`) is returning from
SignalSema, not blocked in a file Open; thread 5 (`pc=0x423de8`) is in the
WaitSema wrapper. The "IOP file open" and "IOP shutdown" narratives and the
"Recommended next action" section are discarded (the brief forbade
conclusions). Kept: the caller/callee rows and the polled-offset list as leads
(unverified).

Reading with the right names: the recomp sits in the same SignalSema/WaitSema/
GetThreadId spin that PCSX2 shows during the healthy load (T47 §T47-5: 332–337.5
emu-s), but in PCSX2 that spin ends when the 990-iteration `_sceCdSC` read loop
finishes; in the recomp CD reads stop at ~478 s. Next question: why the read
loop stops early (unanswered CD request / SIF RPC reply / sound-module upload).
