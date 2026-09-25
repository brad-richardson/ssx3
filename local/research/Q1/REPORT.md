# Q1 — how PCSX2's microVU handles pipeline hazards statically

Worker: local Qwen via opencode. Brief: `local/muse/prompts/Q1.md`. Box: 2026-09-25.

Source of record: PCSX2 `master` at commit `2c804670c5f2c99d6a6b842904dd222de89aa493`
(2026-09-20). Files read: `pcsx2/x86/`: `microVU.h`, `microVU.cpp`, `microVU_IR.h`,
`microVU_Analyze.inl`, `microVU_Branch.inl`, `microVU_Flags.inl`, `microVU_Upper.inl`,
`microVU_Lower.inl`, `microVU_Misc.h/.inl`, `microVU_Alloc.inl`, `microVU_Clamp.inl`,
`microVU_Compile.inl`, `microVU_Execute.inl`, `microVU_Macro.inl`, `microVU_Log.inl`,
`microVU_Tables.inl`, plus `pcsx2/`: `VU.h`, `VUmicro.h`, `VUmicro.cpp`, `VU1micro.cpp`,
`MTVU.h`, `MTVU.cpp`, `Config.h`, `VUflags.h/.cpp`. Local read-only copies in
`local/research/Q1/src/` (untracked). Quotes are verbatim from those files, cited as
`file:line`; the equivalent GitHub path is
`https://github.com/PCSX2/pcsx2/blob/2c804670c5f2c99d6a6b842904dd222de89aa493/pcsx2/<path>`.

Note: on master the old monolithic `microVU.inl` no longer exists; the recompiler is the
split set above. All findings are from master (current), not the 1.8/2.0 release tags.

## Q1 — how microVU computes stalls (analysis pass, tracked state, unknown entry state)

- Two passes per block, all static. Pass 1 walks the block instruction by instruction,
  ticking a scoreboard per instruction: `mVUcompile` first pass (microVU_Compile.inl:704-712):
  `startLoop(mVU); mVUincCycles(mVU, 1); mVUopU(mVU, 0);` … `mVUsetCycles(mVU);`
  (line 777). So each instruction costs `1 + mVUstall` simulated cycles; there is no
  runtime waiting at all.
- Tracked state is a per-register "cycles until ready" scoreboard, `microRegInfo`
  (`static_assert(sizeof(microRegInfo) == 96)`, microVU_IR.h:61): u8 per VF lane
  (VF[1..31] x,y,z,w), u8 per VI[1..15], plus `q`, `p`, `r`, `xgkick` counters.
  `mVUincCycles` (microVU_Compile.inl:331-383) decrements every counter by `x` with
  saturating subtraction: `__fi u8 calcCycles(u8 reg, u8 x) { return ((reg > x) ? (reg - x) : 0); }`
  (microVU_Compile.inl:304).
- `mVUstall` for an instruction = max of the ready-counters of all its source operands,
  set by per-operand analyze helpers, e.g. `analyzeVIreg1`: `mVUstall = std::max(mVUstall, mVUregs.VI[xReg]);`
  (microVU_Analyze.inl:108-115), `analyzeReg5` per VF lane (microVU_Analyze.inl:111-124),
  `analyzeQreg(x)`: `mVUregsTemp.q = x; mVUstall = std::max(mVUstall, mVUregs.q);`
  (microVU_Analyze.inl:131-134), `analyzePreg` similar with `p-1` (microVU_Analyze.inl:136-140).
- Result latencies are hard-coded constants at each opcode site: DIV `mVUanalyzeFDIV(mVU, _Fs_, _Fsf_, _Ft_, _Ftf_, 7)`
  (microVU_Lower.inl:35), RSQRT `… 13)` (microVU_Lower.inl:111); EFU ops pass p-pipe
  constants 54 (microVU_Lower.inl:197), 44 (:297), 18 (:349), 12 (:373), 24 (:399),
  11 (:479), 29 (:502), 12 (:547/:571); VI writes take an `aCycles` param
  (`analyzeVIreg2`, microVU_Analyze.inl:117-126).
- Q/P are 2-instance dual buffers: `mVUinfo.readQ = mVU.q; mVUinfo.writeQ = !mVU.q;`
  (microVU_Compile.inl:792-795); when a counter hits 0 the instance toggles
  (`incQ`/`incP`, microVU_Compile.inl:306-307). q reaching ≤4 raises `doDivFlag`
  (microVU_Compile.inl:350-356); `xgkick` hitting 0 raises `doXGKICK` and records
  `XGKICKPC = xPC` (microVU_Compile.inl:372-379).
- Same-cycle upper/lower hazards are resolved structurally in `mVUsetCycles`
  (microVU_Compile.inl:395-420): if upper and lower write the same VF reg, the lower op
  becomes a NOP (or `noWriteVF` if it has R/VI side effects); if the lower reads what the
  upper writes, `swapOps`; if both directions, `backupVF`. New write latencies are then
  committed with `tCycles(u8 dest, u8 src) { return std::max(dest, src); }`
  (microVU_Compile.inl:305) — the scoreboard only ever moves forward.
- Block-end state is normalized before linking: `mVUoptimizePipeState`
  (microVU_Compile.inl:313-330) applies `optimizeReg(u8 rState) { return (rState == 1) ? 0 : rState; }`
  (:303), with the comment "If the cycles remaining is just '1', we don't have to transfer
  it to the next block … essentially '1' will be the same as '0'"; `mVUregs.r = 0;`
  ("There are no stalls on the R-reg, so its Safe to discard info").
- Unknown/entry state: not guessed — it is carried. `mVUinitFirstPass`
  (microVU_Compile.inl:530-550): `memcpy((u8*)&mVUregs, (u8*)pState, sizeof(microRegInfo));`
  plus `mVU.p = 0; mVU.q = 0;   // All blocks start at p index #0 / q index #0`. A block
  compiled for a branch target receives the *producer* block's end state as its entry
  state (see Q3), so the "what was in flight when we jumped in" problem is solved by
  state-passing + a full scoreboard equality check at the link, not by a cold assumption.

## Q2 — flag pipelines (4-cycle-old flags, which instances to keep)

- There are 4 instances of each flag register in a ring: `alignas(16) u32 micro_macflags[4];`
  `micro_clipflags[4]; micro_statusflags[4];` (VU.h:149-151). The dispatcher keeps all 4
  status instances live in `gprF0..F3` (microVU_Execute.inl:64-67, reloaded on xgkick
  resume :103-106, saved on exit :113-117 — "Backup Status Flag (other regs were backed
  up on xgkick)"); `mVU.statFlag[4] // 4 instances of status flag (backup for xgkick)`
  (microVU.h:84).
- Every instruction carries which instance it writes/reads: `struct microFlagInst { bool doFlag; bool doNonSticky; u8 write; u8 lastWrite; u8 read; }`
  (microVU_IR.h:144-152), one each for status/MAC/clip per instruction
  (`microOp.sFlag/mFlag/cFlag`, microVU_IR.h:181-183).
- Instance assignment is per-block in `mVUsetFlags` (microVU_Flags.inl:107-217+):
  the 4-slot cycle maps `mFC.xStatus[4]/xMac[4]/xClip[4]` (`struct microFlagCycles`
  microVU_IR.h:154-160) are initialized to identity (Flags.inl:142-147), then inherited
  from the previous block's `pState` — if `needExactMatch & 1` is clear, all but one
  status instance are invalidated and the newest kept:
  `mFC.xStatus[(xS - 1) & 3] = 0;` where `xS = (mVUpBlock->pState.flagInfo >> 2) & 3;`
  (Flags.inl:149-157); bits 2 and 4 do the same for MAC/clip (Flags.inl:159-175). If a
  bit is set, all 4 instances are considered valid.
- Per instruction: `mFC.cycles += mVUstall;` (Flags.inl:192) then
  `sFLAG.read = doSFlagInsts ? findFlagInst(mFC.xStatus, mFC.cycles) : 0;` (Flags.inl:194-196) —
  `findFlagInst` returns the newest of the 4 instances whose write-cycle ≤ current cycle
  (microVU_Flags.inl:63-75), so a flag read at cycle C is routed to the instance that was
  last written at or before C: exactly the 4-cycle-old visibility, computed statically.
- Tail window: "Ensure last ~4+ instructions update mac/status flags (if next block's
  first 4 instructions will read them)" (microVU_Flags.inl:113) — the function walks back
  up to 3 instructions (`if (aCount >= 3) break;` :131-134) and the FSSET dedup
  (`mVUstatusFlagOp`) is suppressed inside that window (:184-190) so the instances the
  next block will read are definitely written.
- FSSET dedup: `mVUstatusFlagOp` (microVU_Flags.inl:20-61) walks back through recent
  instructions to find the last non-sticky status writer and drops redundant sticky
  writes, only when `!noFlagOpts` (:182).
- DIV flag: q expiry raises `doDivFlag` (Q1); at program end `mVUdivSet`
  (microVU_Flags.inl:7-16) folds the pending div result into the status flag register,
  emitted from `mVUDTendProgram` (microVU_Branch.inl:40-44).
- Program/M-bit boundary: `mVUSaveFlags` (microVU_Compile.inl:597-601) memcpys the live
  `mFC` to `mFCBackup` and re-runs `mVUsetFlags(mVU, mFCBackup)`, so a program that ends
  mid-flag-window still hands the next program a consistent instance map.
- `sortFlag`/`sortFullFlag` (microVU_Flags.inl:78-101) renumber the 4 instances into a
  dense order for block linking; `mVUsetFlagInfo` packs the survivor index into
  `pState.flagInfo` for the next block (used at Flags.inl:151/:169).

## Q3 — block boundaries, keying, branch-into-middle, E/D/T bits

- A block is a straight-line run. It ends (EOB) when: a branch resolves
  (`if (branch >= 2) { mVUinfo.isEOB = true; if (branch == 3) mVUinfo.isBdelay = true; … break; }`
  microVU_Compile.inl:802-817 — branch 3 = E-bit branch, the branch delay slot is
  executed); an M-bit without E-bit (`needExactMatch |= 7; … break;` :832-841); or the
  natural program end (`mVUinfo.isEOB` set by the op).
- Each block stores its pipeline state at both ends: `microBlock { microRegInfo pState; microRegInfo pStateEnd; u8* x86ptrStart; … }`
  (microVU_IR.h:71-75; `pStateEnd` is "needed by JR/JALR opcodes"). At block exit:
  `mVUsetFlags(mVU, mFC); mVUoptimizePipeState(mVU);  // Optimize the End Pipeline State for nicer Block Linking`
  `mVUtestCycles(mVU, mFC);` (microVU_Compile.inl:858-862).
- Entry keying: `mVUsearchProg` (microVU.cpp:244-295) buckets by
  `mVU.regs().start_pc / 8`, keeps a one-entry `quick` cache plus an LRU `list`; a hit
  requires `mVUcmpProg` — a generated SIMD comparator `mVUGenerateCompareState`
  (microVU_Execute.inl:253-310) that compares the whole 96-byte `pState` as
  6×128-bit (SSE) or 3×256-bit (AVX) `PCMP.EQD`+AND+`MOVMSK` words. If the scoreboard
  differs, a fresh program instance is created (`mVUcreateProg` + `mVUblockFetch`,
  microVU.cpp:272-278). So a branch-into-middle reuses a compiled block **only if the
  in-flight state matches bit-for-bit**; otherwise the block is recompiled for that state.
- Jump targets: pass-1 resolves JR/JALR/branches via `mVUsetupRange`/`mVUblocks[target]`
  (microVU_Compile.inl:743-762); E-bit/`doJumpCaching = true` (microVU_Misc.h:296) feeds
  a jump cache (`struct microJumpCache { microProgram* prog; void* x86ptrStart; }`
  microVU_IR.h:55-59); `doJumpAsSameProgram = false` (microVU_Misc.h:303).
- E-bit: at an E-bit branch `mVUDTendProgram` (microVU_Branch.inl:20+) flushes the whole
  scoreboard — `mVUincCycles(100); mVUcycles -= 100;` — because an E-bit branch
  discards the pipeline (VU hardware semantics), so no in-flight results may leak into
  the linked block; it also runs any pending XGKICK if `xPC >= XGKICKPC` and the pending
  div flag (microVU_Branch.inl:40-55). `mVUup.eBit` is then consumed at block link
  (microVU_Branch.inl:312/395/498/566/621).
- M-bit (VU0 sync): at codegen, an M-bit that isn't an E-bit/EOB snapshot-copies the
  96-byte state (`xMOV(ptr32[lpS], cpS[0]);` loop, microVU_Compile.inl:912-918), calls
  `mVUendProgram` + `normBranchCompile` to link the continuation, then `goto
  perf_and_return` (microVU_Compile.inl:919-933); the runtime XORs
  `VUFLAG_MFLAGSET` into `mVU.regs().flags` (:890-893). M-bit also forces
  `needExactMatch |= 7` (flags must be exact across the COP2 sync).
- D/T bits: recorded pass-1 (`mVUup.dBit`/`mVUup.tBit`, microVU_Compile.inl:766-772),
  handled pass-2 *after* the branch — "T/D Bit on branch is handled after the branch,
  branch delay slots are executed." (microVU_Compile.inl:899): `mVUDoTBit` /
  `mVUDoDBit` (microVU_Compile.inl:560-595; D-bit gated by `doDBitHandling = false`
  microVU_Misc.h:313, so D-bit is off by default). Both call `mVUDTendProgram` with a
  1-cycle tail and set the jump target.
- vi15 constant info propagates across blocks: `mVUregs.vi15 = (doConstProp && mVUconstReg[15].isValid) ? … : 0;`
  (microVU_Compile.inl:855-857; `doConstProp = false` microVU_Misc.h:290 — off by
  default).

## Q4 — XGKICK timing / VU1→GS path

- Compile-time model: `mVUanalyzeXGkick` (microVU_Analyze.inl:467-485):
  `mVUlow.isKick = true; mVUregs.xgkickcycles = 0; mVUlow.kickcycles = 0;` then, unless
  `CHECK_XGKICKHACK`, `analyzeXGkick1(); // Stall will cause mVUincCycles() to trigger pending xgkick`
  + `analyzeXGkick2(1)` — the kick itself contributes 1 cycle of transfer latency. The
  comment is explicit about the model's fudge: "Technically XGKICK should stall on the
  next instruction, this code stalls on the same instruction. The only case where this
  will be a problem with, is if you have very-specifically placed FMxxx or FSxxx opcodes
  checking flags near this instruction AND the XGKICK instruction stalls. No-game should
  be effected by this minor difference."
- Accumulation: every non-kick instruction does `mVUregs.xgkickcycles += 1 + mVUstall;`
  and a VU1 store to memory snapshots it: `if (mVUlow.isMemWrite) { mVUlow.kickcycles = mVUregs.xgkickcycles; mVUregs.xgkickcycles = 0; }`
  (microVU_Compile.inl:778-791) — i.e. the transfer is scheduled to start when the
  *store's data* lands, not when the XGKICK instruction executes. A pending count at
  block/branch/M-bit end is folded into `kickcycles` the same way
  (microVU_Compile.inl:808-812/:834-838/:846-850).
- Runtime, default path: when the 1-cycle kick latency expires, codegen emits
  `mVU_XGKICK_DELAY` (microVU_Compile.inl:935-938 → microVU_Lower.inl:1808-1824), which
  fastcalls `mVU_XGKICK_(u32 addr)` (microVU_Lower.inl:1698-1714): it reads the
  path-1 tag (`gifUnit.GetGSPacketSize(GIF_PATH_1, vuRegs[1].Mem, addr, ~0u, true)`) and
  transfers the **entire packet at once** (`gifUnit.TransferGSPacketData(GIF_TRANS_XGKICK,
  &vuRegs[1].Mem[addr], size, true)`), with wrap-around split at 0x4000. So stock
  PCSX2 models XGKICK as: statically-scheduled 1-cycle delay, then an atomic full-packet
  consume. `xgkickcyclecount`/`xgkickenable` live in `VURegs` (VU.h:164-170).
- Runtime, `CHECK_XGKICKHACK` path (per-game fix): the kick drains over time instead.
  XGKICK opcode: `mVUlow.kickcycles = 99; mVU_XGKICK_SYNC(mVU, true);`
  (microVU_Lower.inl:1828-1832); per instruction: `if (isVU1 && mVUlow.kickcycles && CHECK_XGKICKHACK) mVU_XGKICK_SYNC(mVU, false);`
  (microVU_Compile.inl:895-898). `mVU_XGKICK_SYNC` (microVU_Lower.inl:1788-1806):
  `xADD(ptr32[&VU1.xgkickcyclecount], mVUlow.kickcycles-1);` then if
  `xgkickcyclecount >= 2` it calls `_vuXGKICKTransfermVU(flush)` and afterwards
  `xADD(ptr32[&VU1.xgkickcyclecount], 1);`. The drain (`_vuXGKICKTransfermVU`,
  microVU_Lower.inl:1716-1786) loops `while (VU1.xgkickenable && (flush || VU1.xgkickcyclecount >= 2))`
  moving `transfersize = std::min(VU1.xgkicksizeremaining, VU1.xgkickcyclecount * 8);`
  bytes per step (8 bytes = one qword per VU1 cycle) and on flush adds the drained
  cycles to `VU1.cycle`. Final flush at program/branch end: `mVUlow.kickcycles = 99;
  mVU_XGKICK_SYNC(mVU, true);` (microVU_Branch.inl:52-55, :176-179).
- The hack is a **gamefix, not a speedhack**: `#define CHECK_XGKICKHACK
  (EmuConfig.Gamefixes.XgKickHack) // Special Fix for Erementar Gerad, adds more delay to
  VU XGkick instructions. Corrects the color of some graphics.` (Config.h:1516) and the
  option comment "Erementar Gerad, adds more delay to VU XGkick instructions. Corrects
  the color of some graphics, but breaks Tri-ace games and others." (Config.h:~1113).
- On the MTVU (threaded VU1) path, transfer completion is signalled to the GS thread
  with `semaXGkick.Post(); // Tell MTGS a path1 packet is complete` (MTVU.cpp:155;
  `Threading::UserspaceSemaphore semaXGkick;` MTVU.h:36).

## Q5 — known accuracy shortcuts (VU flag hack, VU1 instant, MTVU, …)

User-facing options live in `EmuConfig` (Config.h):

| Option | Definition | Effect (source) |
| --- | --- | --- |
| `Speedhacks.vuFlagHack` | `#define CHECK_VU_FLAGHACK (EmuConfig.Speedhacks.vuFlagHack)` (microVU_Misc.h:329) | `sHackCond (mVUsFlagHack && !sFLAG.doNonSticky)` → `sFLAG.doFlag = false` (microVU_Flags.inl:103-104, :206-209): status-flag (non-sticky) updates are dropped, so flag-reading ops see a coarser/older flag value — a classic correctness-for-speed shortcut. |
| `Speedhacks.vu1Instant` | `#define INSTANT_VU1 (EmuConfig.Speedhacks.vu1Instant)` (Config.h:1506); "Enable Instant VU1 (Without MTVU only)" (Config.h:1145) | `vu1ExecMicro` (VU1micro.cpp:69-79): `VU1.cycle = cpuRegs.cycle; … if(!INSTANT_VU1) CpuVU1->ExecuteBlock(1); else CpuVU1->Execute(vu1RunCycles);` with `#define vu1RunCycles (3000000)` (VUmicro.h:20) — the whole VU1 program runs as one burst, decoupled from the EE clock, instead of being paced 1:1; `vu1Finish` then `vu1Thread.WaitVU()` (VU1micro.cpp:27-30). VU1 no longer constrains EE timing. |
| `Speedhacks.vuThread` | Config.h SpeedhackOptions ("Enable Threaded VU1") | MTVU: VU1 runs on its own thread in a free-run loop (`CpuVU1->Execute(vu1RunCycles); … vuCycles[vuCycleIdx].store(VU1.cycle…)` MTVU.cpp:145-157); VU0 meets it at sync points (`vu1Finish`/`ExecuteBlock` early-return under `THREAD_VU1`, VU1micro.cpp:25-33, VUmicro.cpp:32-36). Timing is "Yolo it" per the in-code comment (VU1micro.cpp:53-61). |
| `Speedhacks.EECycleRate` / `EECycleSkip` | Config.h SpeedhackOptions | VU0 may skip clock: `mVUcleanUp` (microVU_Execute.inl:355-370) advances `cpuRegs.cycle` by `min(mVU.cycles, 3000) * EmuConfig.Speedhacks.EECycleSkip` per block; `mVUtestCycles` rescales VU0 cycles by the rate (microVU_Compile.inl:449+). |
| `Gamefixes.XgKickHack` | Config.h:1516 | See Q4 — per-game XGKICK re-timing. |
| `Gamefixes.IbitHack` | Config.h GamefixOptions ("Needed to stop constant VU recompilation in some games") | Pass-1 skips upper-half I-ops `IADDI/IADDIU/ISUBU/ILW/ISW/LQ/SQ` ("this is a little risky as we could be ignoring subtle differences… It's a hack anyways...", microVU_Compile.inl:739-767) and re-bounds the program range. |
| `Gamefixes.VUSyncHack` / `FullVU0SyncHack` | Config.h GamefixOptions | On M-bit, `xMOV(ptr32[&mVU.regs().nextBlockCycles], 0);` (microVU_Compile.inl:924-926) and the VU0 rate-skip is suppressed (microVU_Compile.inl:452-453) — "Makes microVU run behind the EE". |
| (internal) `noFlagOpts` | `constexpr bool noFlagOpts = false` (microVU_Misc.h:265) | Disables all flag optimizations; forces `sFLAG.doNonSticky = true; mFLAG.doFlag = true;` (microVU_Flags.inl:211-217). The dev escape hatch for flag-related breakage. |
| (internal) `doSFlagInsts/doMFlagInsts/doCFlagInsts` | microVU_Misc.h:273-275 (all `true`) | Kill the 4-instance flag tracking per flag type. |
| (internal) `doConstProp` | `= false` (microVU_Misc.h:290) | vi15 constant propagation across instructions/blocks (off by default). |
| (internal) `doDBitHandling` | `= false` (microVU_Misc.h:313) | D-bit is ignored at runtime unless enabled. |
| (internal) `doJumpCaching` / `doJumpAsSameProgram` | microVU_Misc.h:296/303 | Jump cache on; treat jump target as same program off. |

## Mapping to our stage B

E57 Stage B (local/research/E57/REPORT.md:142-147) requires per basic block: "precompute
stalls assuming the pipeline state at block entry, with a cheap guard (compare the entry
scoreboard against the assumed one; interpreter fallback on mismatch)". PCSX2 is a direct
working model of exactly this design:

- **Entry guard**: PCSX2 compares the *full* 96-byte scoreboard at block entry
  (Q1/Q3; `mVUcmpProg` SIMD compare, microVU_Execute.inl:253-310). Our guard can be
  coarser — compare only the in-flight counters that actually matter for the block —
  since a mismatch just forces the interpreter fallback.
- **Precomputed stalls**: the pass-1 loop (Q1) is the template: per-instruction
  `1 + max(read-latencies)`, latencies as opcode constants, writes committed with
  `max()`, all over a copied entry state — i.e. exactly "precompute stalls assuming the
  pipeline state at block entry".
- **Flag visibility at exact cycles**: Q2 — keep the 4-instance ring + per-instruction
  `findFlagInst` routing, the 3-instruction tail window, and `needExactMatch`
  inheritance at block links; the FSSET dedup and `vuFlagHack` are the accuracy knobs to
  *not* copy (or expose).
- **Q/P latencies, WAITQ/WAITP**: Q1 — q/p 2-instance counters in the scoreboard with
  opcode constants (DIV=7/RSQRT=13; EFU p 11–54); WAITQ/WAITP just read the q/p counter.
- **LSU commit before PATH1 consumes a qword**: Q4 — PCSX2 schedules the transfer start
  from `kickcycles`, snapshotted at the *memory write* (microVU_Compile.inl:783-788),
  which is the same ordering constraint.
- **XGKICK per-cycle progress**: decision point. Stock PCSX2 default = atomic
  full-packet transfer at the statically computed point; the 8-byte/cycle drain exists
  only under the per-game `XgKickHack`. We must pick: atomic (fast, PCSX2 default) or a
  drain model (closer to real per-cycle GIF pacing).
- **VI branch backup / E+D/T delay slots**: Q3 — E-bit flushes the scoreboard
  (`incCycles(100); cycles -= 100`) before linking; T/D handled after the branch
  (D-bit off by default in PCSX2); `doConstProp` (vi15) off by default.
- **Practical caveats to carry into our design**: (a) counters are u8 — a block with
  >255 cycles of in-flight history saturates; PCSX2 tolerates this via the entry
  compare; (b) the XGKICK stall is modeled on the same instruction, not the next one
  (Analyze.inl:478-483 comment); (c) `optimizeReg` drops 1-cycle states at block exit —
  a free precision-for-size win we can take too.

## Gaps

- `VU1.xgkickcyclecount` per-cycle ticking: no per-VU1-cycle increment site was found in
  the files read (VU.h, VUmicro.h/.cpp, VU1micro.cpp, MTVU.h/.cpp, all x86/*.inl). It is
  advanced per *instruction* by the generated `mVU_XGKICK_SYNC` (+kickcycles-1, +1) and
  consumed in 8-byte steps; in the default (non-hack) path the packet is transferred
  atomically by `mVU_XGKICK_` and the count appears unused. Treated as: stock timing =
  atomic transfer; per-cycle drain is hack-only. Confidence: high for the code read, but
  a full repo grep was not possible (code search API requires auth).
- EFU latency constants (54/44/18/12/24/11/29, microVU_Lower.inl:197-571) are cited by
  line without the opcode name sitting above each line; mapping constant→opcode
  (SQRT/RSQRT/RCP) was not captured.
- `mVUoptimizePipeState` body was read (Q1) but its per-register `optimizeReg` only
  handles the ==1 case; any further reduction (e.g. capping at 254) was not verified.
- The old monolithic `microVU.inl` (1.8/2.0 tag) was not read; all findings are master.
  If stage B should mirror a *released* PCSX2 exactly, diff against a tag later.
