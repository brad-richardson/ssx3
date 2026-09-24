# E54F1 — COP0 Count source and clock contract

Worker: Codex. Brief: local/muse/prompts/E54F1.md. Read-only source audit for the E54 gate. No fix, build, boot, device access, or push.

## Evidence table

| Question | Pinned evidence | Consequence or gap |
| --- | --- | --- |
| Base | E54D worktree ~/dev/ssx3-work/E54D/PS2Recomp is clean at 1aaed05256bf53881824a9edd96a7cd5b7e8bbcc. The top-level fork checkout's ssx3 ref was eac6cba, so fork citations below use E54D. Runner-dir diff from 14b1e5cb is empty. [E54D report](../E54D/REPORT.md) records its generated output promotion to canonical ~/dev/ssx3-work/codegen-ssx3. | E54E's signed-branch candidate failed its visual boot. Its unshipped code and codegen are not a base; [E54E report](../E54E/REPORT.md). |
| Our MFC0, MTC0, Compare | ps2xRecomp/src/lib/cop0_translator.cpp:46-51 emits MFC0 Count and Compare reads of context fields using SET_GPR_S32. Lines 96-101 emit MTC0 Count as ctx->cop0_count = GPR_U32 and MTC0 Compare as a field write plus ctx->cop0_cause &= ~0x8000. ps2xRuntime/include/ps2_runtime.h:113-117 stores all three as 32-bit fields; ps2_runtime_macros.h:1315-1323 sign-extends MFC0 to the GPR low 64 and ignores destination $zero. | No emitted clock lookup or timer scheduling. Text search of E54D fork source excluding generated runner found no other explicit cop0_count assignment; ps2_debug_panel.cpp:756-761 only reads it. Aggregate context reset/copy can also change the value. |
| Initialization and ownership | R5900Context constructor zeroes the structure, then initializes other COP0 values; Count and Compare stay zero (ps2_runtime.h:144-159). PS2Runtime assigns a fresh context (ps2_runtime.cpp:834-840); scheduler reset copies it to the main thread (EeScheduler.cpp:353-416). GuestThread and invocation each hold a context (ee_scheduler.h:100-134); startThread assigns a fresh context (EeScheduler.cpp:980-1007). | Existing Count is per-thread. A clock kept only in ctx->cop0_count could reset or diverge at thread transitions. |
| Canonical generated sites | Canonical codegen has five Count read expressions at four guest PCs, mapped below; no generated Count or Compare assignments and no Compare read. Receipt ~/dev/ssx3-work/E54F1/count-sites.txt SHA-256 a9b69a5e49f738acdc582ccd1dea5a329302f5a91166b4fa30f947cbc1cec355. | 0x3f4414 occurs in two overlapping generated functions. Static presence does not prove dynamic reach. The five Count instruction/comment pairs match E54E, but sub_003F4330 as a whole differs; canonical is authoritative. |
| Scheduler clock | EeScheduler::reset sets m_eeCycle=0 (EeScheduler.cpp:382). checkpointDue calls accountCycles (:852-890), which charges max(1, cycles) to the 64-bit clock and separately advances EE memory timers. Charge points: dispatch before generated function entry (:765-780, 8 cycles); inter-function dispatchGuestBranch (ps2_runtime.cpp:2348-2356, 8 cycles); generated backward edges via eeCheckpointDue (control_flow_emitter.cpp:174-184, default 32 at ee_scheduler.h:261-264). A completed charge is visible to subsequent generated code. waitForEvent can fast-forward the clock to a deadline using accountCycles after a host wait (EeScheduler.cpp:2825-2882). | This is a synthetic, coarse scheduler clock, not per-instruction EE timing. Straight-line reads can see the same cycle; idle advancement requires Count accounting. The declared 294,912,000 EE cycles/s (ee_scheduler.h:261) is used for host-duration conversion, not proof of accurate instruction charges. |
| Safe access | m_eeCycle is private (ee_scheduler.h:425); generated functions receive PS2Runtime* and active R5900Context* (EeScheduler.cpp:769-789). PS2Runtime::eeScheduler already returns the scheduler (ps2_runtime.cpp:3478-3485), and eeCheckpointDue is a wrapper (:3493-3496). snapshot() is a locked, published copy (EeScheduler.cpp:2238-2249), not live. Scheduler methods are executor-only except event posting/stopping (ee_scheduler.h:279-281). | A narrow executor-only scheduler clock method through PS2Runtime is the safe live interface. |
| PCSX2 Count rate/read/write | At pinned PCSX2 9056c0834, pcsx2/COP0.cpp:488-538 MFC0 Count adds cpuRegs.cycle-lastCOP0Cycle to 32-bit Count and records the cycle. If delta is zero, it adds one anyway, including an MFC0 to $zero. Lines 541-549: MTC0 Count writes GPR low 32 and resets lastCOP0Cycle to the current cycle. pcsx2/R5900.h:79-82,127-137 declares Count u32 and cycle/anchor u64; R5900.cpp:60-76 zeroes them at reset. | Implemented rate is one Count tick per EE cycle plus a compatibility minimum +1 for zero-delta MFC0. u32 arithmetic wraps modulo 2^32. MTC0 creates a new epoch; unadjusted low32 cycle or a fixed divisor cannot preserve the write. The +1 rule is PCSX2 behavior, not verified hardware timing. |
| PCSX2 Compare and interrupt | pcsx2/R5900.cpp:319-334,395-412,498-511 updates Count at event tests, checks Status bit 0x8000 and Count >= Compare && Count < Compare+1000, then calls cpuException(0x808000,...). R5900.h:79-99 maps Compare to register 11 and Status bits 8-15 to interrupt mask; R5900.cpp:96-165 handles the exception. The pinned interpreter has no MTC0 Compare special case; register 11 falls to plain default write (COP0.cpp:541-589), unlike our emitted Cause bit clear. | MTC0 Count changes which later timer-check window qualifies without changing Compare. The PCSX2 source calls the test a hack and asks for proper event scheduling on Count/Compare changes (R5900.cpp:324-327). Exact hardware edge/level timing, behavior across wrap, and Compare-write Cause clearing remain unresolved; the dynarec Compare path was not audited. |

### Canonical static Count sites

| Guest PC | Owning function from ee-func | Canonical generated location | Nearby guest use from ee-at |
| --- | --- | --- | --- |
| 0x3f4414 | sub_003F4330 interior; also overlapping sub_003F4410 | sub_003F4330_0x3f4330.cpp:357-358 and sub_003F4410_0x3f4410.cpp:27-28, MFC0 $a0,Count | Loads prior Count at 0x3f4410; subtracts at 0x3f441c. |
| 0x3f4e08 | sub_003F4DE8 | sub_003F4DE8_0x3f4de8.cpp:55-56, MFC0 $v0,Count | Stores it to stack at 0x3f4e0c. |
| 0x3f4fa4 | sub_003F4F40 | sub_003F4F40_0x3f4f40.cpp:125-126, MFC0 $s1,Count | Saves a start value. |
| 0x3f4fc4 | sub_003F4F40 | same file :180-181, MFC0 $v0,Count | Subtracts start value at 0x3f4fc8; reach unknown. |

### Prediction table

Values are 32-bit hex. Alternatives start at zero. MTC0 Count writes 0xfffffff0 at scheduler/EE cycle 200. No intervening timer check or zero-delta MFC0 is assumed. Fixed divisor 2 is one example of the divisor alternative.

| Event | Direct low32(cycle) | Fixed low32(cycle/2) | 1:1 epoch after write | Pinned PCSX2 interpreter |
| --- | --- | --- | --- | --- |
| MFC0 at cycle 100 | 0x00000064 | 0x00000032 | 0x00000064 | 0x00000064 |
| MFC0 at cycle 140 | 0x0000008c | 0x00000046 | 0x0000008c | 0x0000008c |
| MTC0 at cycle 200 | cannot persist | cannot persist | store 0xfffffff0, anchor 200 | store 0xfffffff0, anchor 200 |
| MFC0 at cycle 240 | 0x000000f0 | 0x00000078 | 0x00000018 | 0x00000018 |

The 40-cycle post-write addition wraps from 0xfffffff0 to 0x18. At a repeated MFC0 with no elapsed cycle, PCSX2 returns previous Count +1 (COP0.cpp:526-533); a pure epoch expression would return the same value. The fork scheduler's cycles are coarse charges, so these are interface tests, not predicted SSX 3 run values.

## One Part 2 candidate and focused tests

Candidate: one shared EE COP0 Count/Compare clock in EeScheduler, reached by narrow PS2Runtime readCount, writeCount and writeCompare wrappers emitted for MFC0/MTC0. Keep u32 Count and u64 last-accounted EE cycle. A read accounts elapsed cycles, with PCSX2's minimum +1 on zero-delta MFC0 if that behavior is chosen; a Count write stores low32 and resets the anchor. Timer checks use the same accounting, including after idle fast-forward. A shared clock avoids per-thread reset. Centralize Compare writes for eventual interrupt policy; the approximate PCSX2 window alone does not settle hardware timing.

Focused tests: table above; two reads at the same cycle, including destination $zero; 0xfffffff0 + 40 wrap; write then context switch and read; idle accountCycles then read; Compare unchanged by Count write; Compare-write Cause behavior and enabled/disabled timer cases once that rule is pinned. Generated code tests should verify emitted calls and returned values; MFC0 Count must call the clock even for destination $zero before the GPR write is skipped. No dynamic receipt proves SSX 3 reaches any Count site.

## Pins, receipts, exact commands, gaps

Pinned primary source URLs and full-file SHA-256 from raw downloads; only numbered excerpts retained under ~/dev/ssx3-work/E54F1:

| PCSX2 9056c0834 file | Full SHA-256 | Excerpt SHA-256 |
| --- | --- | --- |
| [pcsx2/COP0.cpp](https://github.com/PCSX2/pcsx2/blob/9056c0834/pcsx2/COP0.cpp) | 5c15c34884f06c95074d725415df0d9751092f9bb9115f3324351ec4aba17686 | 371dfe930c559a1e7dc0be51fdbfa6752b5cbfd00cb6ef21ebc205e7f2094bdd |
| [pcsx2/R5900.cpp](https://github.com/PCSX2/pcsx2/blob/9056c0834/pcsx2/R5900.cpp) | 23974a38273c329054063a324fbe04b13719f484c18ca557de3655d257a8cb3d | af7ef0209f4c3a6a3c2de6282b77f5c27df01b004a1b199e40ba66c1fbfa8dcc |
| [pcsx2/R5900.h](https://github.com/PCSX2/pcsx2/blob/9056c0834/pcsx2/R5900.h) | a6ef18e1b646b5ba6c956c10836aa4f75fd8309798f0ac0cf8644faa41cbf323 | 1bc7d6c5f96a6bea4d254ebb224aedb7cef2d8fbce8ef82a238d9d525938790f |
| [pcsx2/Interpreter.cpp](https://github.com/PCSX2/pcsx2/blob/9056c0834/pcsx2/Interpreter.cpp) | 0580afe6da6c08ce7bb9042c83074ed25b17080fce9be464ba96832cccd2385d | 4c1c0bbc85425fa114eae8c89cae7613307169a76b97058b4945c65e4aa99f48 |

Commands run, from ~/dev/ssx3 unless workdir shown:

    git -C ~/dev/ssx3-work/E54D/PS2Recomp rev-parse HEAD
    git -C ~/dev/ssx3-work/E54D/PS2Recomp status --short
    git -C ~/dev/ssx3-work/E54D/PS2Recomp diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner
    rg -n 'cop0_count|cop0_compare' ~/dev/ssx3-work/codegen-ssx3 --glob '*.cpp'
    rg -n 'cop0_count\s*=|cop0_compare\s*=' ~/dev/ssx3-work/codegen-ssx3 --glob '*.cpp'
    for a in 0x3f4414 0x3f4e08 0x3f4fa4 0x3f4fc4; do local/tooling/ee/ee-func "$a"; local/tooling/ee/ee-at "$a" 1 2; done
    for f in COP0.cpp R5900.cpp R5900.h Interpreter.cpp; do curl -fL --silent --show-error "https://raw.githubusercontent.com/PCSX2/pcsx2/9056c0834/pcsx2/$f" -o "/Users/brad/dev/ssx3-work/E54F1/PCSX2-$f"; done

Small rg/sed reads followed searches. A local Python extraction kept numbered ranges, hashed them, then removed the full downloads. The count-sites receipt and four excerpts total 11,790 bytes, below 5 MiB. Gaps: no hardware primary source beyond pinned PCSX2; no dynarec Compare-write audit; no dynamic Count-site receipt; no precise per-instruction cycle model. The orchestrator decides Part 2.
