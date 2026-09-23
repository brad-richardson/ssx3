# X2 — orchestrator corrections (2026-09-22)

X2 (local Qwen 35B-A3B) wrote REPORT.md but did not commit; the orchestrator
committed it with these corrections.

| X2 claim | Check | Verdict |
| --- | --- | --- |
| "WaitVSync: 6 call sites (0x424120, 0x42c2f0, …)" | wrappers set `$v1 = 0x74`; `Dispatcher.cpp:376` `case 0x74: SetSyscall` (0x73 is SetVSyncFlag) | **Wrong**: these are SetSyscall wrappers, not vsync waits |
| "60.0 and 30.0 found in VU microcode (sub_00105D98)" | `sub_00105D98` is an EE function in `games/ssx3/ssx3-functions.sweep.csv:67` (0x105d98–0x106538) | **Wrong label**: EE code, not VU microcode; the constants' use is unverified |
| Loop at 0x317184: `addiu $s1,$s1,1` (delay slot of `jal func_317328`), then `lw $v0,0x20($s0)`, `slt $v0,$v0,$s1`, `bnel` back | `sub_00316F00_0x316f00.cpp` L1794–1828 | **Confirmed** as a counted loop calling `func_317328` per iteration against a limit at `state+0x20`; matches the previously published PS2 patch site. Whether it is a fixed-step catch-up loop needs a runtime read |
| "Modifying this is the direct path to 120 Hz" | — | Discarded (a conclusion; brief said tables only) |
| 1/60, 1/30, 1/50 not in rodata | not re-checked | Open |

Kept as leads: the 0x317184 counted-step loop and `func_317328` as the
per-step candidate; the `10.0` load at 0x317148. Next (orchestrator): an
instrumented read of `state+0x20` and the per-frame iteration count at
Select Character and in-race (E-lane, after E33), before any 120 Hz design.
