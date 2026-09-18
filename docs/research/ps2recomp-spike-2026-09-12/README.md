# PS2Recomp feasibility spike (muse on bradflix, 2026-09-11/12) — recovered transcript

Source: muse sessions `2026/09/11/01a092b8…` and `2026/09/12/01a092fb…` on bradflix (copies on the SSD under `bradflix-ps2recomp/sessions/`). The working trees `/tmp/PS2Recomp` and `/tmp/ssx3vu` were lost when bradflix rebooted on 2026-09-18; `commands-and-outputs.md` is every shell command with its output, `scripts/` are the four scratch decoders the spike wrote. Upstream at the time: ran-j/PS2Recomp `main` (last commit 2026-08-18 `14b1e5cb`, still the head on 2026-09-18). No runtime was built (raylib needed X11); no boot was attempted. Verdicts below are the spike agent's words, not verified here.

## 1. Feasibility answer (09-11)

Feasible as a spike, not as a quick port.

**ps2recomp (ran-j/PS2Recomp):**
- Static recompiles PS2 ELF -> literal C++ (`addiu` -> `ctx->r4 = ADD32(...)`), plus `ps2xRuntime` + `ps2xIOP` HLE.
- Needs CMake 3.20+, C++20, SSE4/AVX. Mostly tested on MSVC.
- Retail/stripped workflow is: Ghidra + `ExportPS2Functions.java` -> TOML/CSV -> `./ps2_recomp config.toml`. Fallback `./ps2_analyzer game.elf` is faster but misses entry points on stripped games.
- You hand-map syscalls/stubs (`sceCdRead@0xADDR`, `ret0/ret1`), unresolved `J/JAL` falls back to `lookupFunction()`. Expect to stub a lot of IOP/GS/VU.

**SSX 3 specifics:**
- NTSC-U boot is `SLUS_207.72`, sha1 `77114dfd...` per [timfox/ssx3](https://github.com/timfox/ssx3). EA BIG/`.mpc` movies, `SYSTEM.CNF`, `fefont.sfn`, VU0/MMI + COP1 float sensitivity.
- Prior art proves the hard parts: `timfox/ssx3` (matching decomp + Vulkan/SDL HAL, not yet playable) and `npiriou/ssx3` (Windows physics rehost, snapshot-tested, no playable prototype). Graphics/audio/IOP + EA codecs are the long pole, not the recomp itself.

**Spike plan (1-2 days):**
1. Identify ISO variant + hash, extract `SYSTEM.CNF` + `SLUS_207.72`
2. Ghidra export -> `ps2xRecomp` on ELF, count funcs vs `TODO_NAMED`/unresolved
3. Link subset with `ps2xRuntime`, boot to first syscall/CD-read

**Blocked:** I can't see `/mmt/share/brad/games` from here — shell sandbox is down (`bwrap` missing) and file tools are confined to `/home/brad/dev`, so that absolute path is denied.

Questions:
1. Can you paste `ls -lh /mmt/share/brad/games` + region of the SSX3 ISO?
2. Can you copy `SYSTEM.CNF` + boot ELF (or the ISO) under `~/dev/` so I can inspect it?
3. Spike goal: just "ELF recompiles + runs a frame in harness" or "boots to menu"?


## 2. VU1 coverage, from source reading (09-11)

Short answer: it's the long tail, not a missing VU1 stage — with one caveat I couldn't close without the ISO.

**Verified in upstream source (ran-j/PS2Recomp `main`):**
- Full VU1 micro-mode interpreter exists at `ps2xRuntime/src/lib/vu/`: `ps2_vu1_core.cpp` (~57KB), `ps2_vu1_lower.cpp` (~28KB), `ps2_vu1_upper.cpp` (~16KB), plus state/pipeline tracking in `include/runtime/ps2_vu1.h` (VF/VI/ACC/Q/P/I/R regs, MAC/clip/status flags, branch-delay, E/D/T bits, TOP/ITOP, XGKICK pipeline).
- Upper covers the standard FMAC set (`ADD/SUB/MADD/MSUB/MAX/MINI/MUL` bc-forms, `MULq/i`, `MAX/MINIi`, …). Lower covers `LQ/SQ/ILW/…`, branches, and `XGKICK` into the GIF arbiter, with polynomial approximations for `EATAN/ESIN/EEXP`.
- The surrounding path exists too: `ps2_vif1_interpreter.cpp` (MPG/UNPACK/DIRECT/…), GIF PATH1/2/3 arbiter, GS frontend/backend.
- History says "correctness tail": PR #80 added the VU1/VIF1/GIF pathways; PR #191 (merged Aug) says *"the current VU1 was almost all wrong"* — fixes were VU1 flags mask, pipeline, and cache. Issue #161 (still open) asks for per-instruction unit tests incl. saturation/flag edge cases.

**Not verified:** I read the heads of upper/lower, not every opcode arm (DIV/RSQRT/RGET/RNEXT/WAITP/XITOP and branch-delay × E-bit interactions are unconfirmed). And SSX3's actual microprograms need the disc — I still can't reach `/mmt/share/brad/games` from this sandbox.

**Inference:** SSX3 will almost certainly upload standard EA VU1 microcode via `MPG` + `XGKICK`, which is the implemented path (PCSX2's history even shows SSX3 fixed by GIF/VIF accuracy work, not by new VU1 ops). So expect common-op success with risk concentrated in flag/pipeline/GS-backend fidelity — the long tail.

Decisive next step if you want certainty: pull the ISO's `MPG` upload blobs (or a PCSX2 VU1 trace) into `~/dev` and I'll diff their opcodes against the `execUpper`/`execLower` switch tables.


## 3. Spike complete: SSX 3 microcode census + EE recompile (09-12)

Spike complete. Bottom line first, evidence after.

## Answer: it's the long tail — SSX3 hits no unimplemented VU1 opcodes

I extracted SSX3's VU1 microcode from your ISO and decoded every instruction against PS2Recomp's own VU1 decoder, then built `ps2_analyzer`+`ps2_recomp` from upstream and ran both on the game's ELF. Nothing in SSX3 falls into a `reportReservedInstruction` path.

## What SSX3 actually ships (from `SLUS_207.72` in your ISO)

- `.vutext` (59 KB): 7 VU microprograms as VIF upload streams — 32 `MPG` packets (`load_addr` 0x0→0x700 stepping 0x100, i.e. VU1 micro-mem layout), each preceded by `STMASK/STMOD/OFFSET/BASE` preambles, with `MSCAL` entries. Sizes: 1172 / 2005 / 576 / 1985 / 804 / 275 / 488 instructions (two programs fill nearly all 16 KB of VU1 micro-mem).
- 32 `.DVP.overlay.*` sections: all **zero-filled** in the ELF (verified byte-level) — they're runtime staging buffers, not code. Their reserved sizes match the 7 `.vutext` programs 1:1, confirming the mapping. (This is the reverse of the Champions-of-Norrath layout where overlays hold the code.)
- `.DVP` (1557 B): loader table — EE addresses + overlay names as ASCII.
- Engine is EAGL (EA Graphics Library), per rodata.

## VU1 opcode coverage: 7,305/7,305 instructions implemented

| Check | Result |
|---|---|
| Instructions in unimplemented encodings | **0** |
| Distinct ops used | 85, incl. VU1-only `XGKICK`×47, `XTOP`×62, `XITOP`, `CLIP`×120, `DIV`×125, `RSQRT`, `RNEXT/RINIT`, `MFP`, EFU `ESIN`/`ERLENG`, `WAITP/WAITQ` |
| `LOI` float immediates (44×, e.g. `loi 0.5`) | handled via the runtime's I-bit path (`upper & 0x80000000`), which has dedicated tests |
| VIF commands used at boot (`MPG/MSCAL/UNPACK/STMASK/STMOD/OFFSET/BASE/MARK/FLUSH`) | all present in `ps2_vif1_interpreter.cpp` |

Two traps I ruled out along the way: the I-bit is bit 31 of the *upper* word (my first histogram misclassified 16 `LOI`s as reserved — all resolved), and the `.vutext` "reserved" hits outside `MPG` payloads are `UNPACK` headers, DMA/GIF tags, and an inline float table, not code.

## EE recompiler coverage: also clean

```
Functions discovered: 8143, recompiled: 8017, stubs: 126, skipped: 0, decode failures: 0
Unhandled instructions: 0. Warnings: 3594, errors: 0
```

VU0 macro-mode (COP2) appears in 484 functions and recompiles with 0 unhandled. The 359 "untracked" analyzer hits are mostly C++ RTTI/dbg cruft recompiled normally, not blockers.

## Where the real work is (not VU opcodes)

1. **GS emulation** — upstream's own limitation ("Graphics Synthesizer … need external implementation"); `XGKICK` feeds a GIF arbiter with no real renderer behind it. This is the biggest item by far.
2. **VU/VIF fidelity, not coverage** — flag pipelines, `CLIP`, Q/P latency, `XTOP/XITOP` vs `MSCAL` timing. The interpreter models pipelines, but it's unproven against EAGL.
3. **EE runtime surface** — 126 bound stubs (`scePad/sceDma/sceGs`…), 165 raw `SYSCALL` sites dispatching via `$v1`, 20+ IOP modules (`SNDDRV`, `PADMAN`, …) needing `ps2xIOP` profiles.
4. **Control flow noise** — 3,594 unresolved indirect `JR/JALR`s → 724K fallback entries. The Ghidra-export path (not the quick analyzer I used) is recommended here.

Note: I couldn't find the literal "very long tail" phrase upstream — the concrete statements are "VU1 microcode is not complete" plus partial HW emulation. Against current upstream, SSX3 doesn't touch the incomplete parts at the opcode level. What I did *not* verify (would need the runtime built + a boot): per-frame DMA chains, which are constructed dynamically and can't be enumerated statically.

Suggested next step if you proceed: build the runtime (needs X11 for raylib — configure failed here without it), run `ps2xTest`'s VU suite, then try booting to the first `MSCAL` and GS kick. My scratch decoders are in `/tmp/ssx3vu/` if you want to re-run the census.
