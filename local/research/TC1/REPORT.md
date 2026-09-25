# TC1 report: per-thread guest state audit + vf0 read-only

Worker session (Muse Code), 2026-09-25, ~2 h box, Mac mini. Fork worktree
`~/dev/ssx3-work/TC1/PS2Recomp`, branch **`tc1-ctx`** from fork `ssx3` `0ed07c4`.
All fork file:line citations are at `0ed07c4` unless noted. Codegen usage counts are over
canonical `~/dev/ssx3-work/codegen-ssx3` (9457 files).

## Outcome

1. **Audit: after the RD1 fix, exactly one per-thread state delta remains: VU0 R.**
   Main sets `vu0_r` = 1.0-bits (`ps2_runtime.cpp:878`); `EeScheduler::startThread`
   builds threads from `R5900Context{}` (`EeScheduler.cpp:1132`), whose R = 0. It is
   benign for SSX 3 (report §1) and is left for a follow-up lane (one-line ctor fix).
   Every other field is identical between main and thread contexts.
2. **vf0 read-only implemented in the emitter** (commit **`e29e4975`** on `tc1-ctx`,
   6 files +202, no push): LQC2, QMTC2 and the 29 remaining unguarded VU macro helpers
   no longer emit stores to `ctx->vu0_vf[0]`. Suite red→green: 612/615 fail without the
   fix (rc=3), **615/615 pass** with it (rc=0), run from the worktree root.
3. **No det boot, no frames:** the change is emitter (`ps2xRecomp`) + tests only; the
   runner links neither, and generated code is byte-identical until a regen. Brief §3
   is conditioned on a runtime change, and brief §2 says game-visible effect awaits an
   orchestrator-coordinated regen. Post-regen det-hash prediction: identical to the
   RD1-fixed baseline (recorded in §3).

## 1. Audit: fields whose hardware value differs from zero

Hardware column is PCSX2 (bytesize `~/pcsx2-t4/pcsx2/pcsx2`, the T-lane tree) unless noted.
"Thread" is post-RD1-fix (`51c759b` in the ctor).

| Field | Main | Thread | Hardware (PCSX2) | Used by SSX 3? |
|---|---|---|---|---|
| `vu0_vf[0]` | (0,0,0,1) (`ps2_runtime.cpp:876`) | (0,0,0,1) via RD1 ctor fix | (0,0,0,1): `VUmicroMem.cpp` `vuMemReset:37-40`; asserted in `VU0microInterp.cpp:207-214` | Read in 270 files; 1 write: `lqc2 $vf0` at 0x3fe9bc (`sub_003FE828`, VU0 save/restore) |
| `vu0_r` (R) | 1.0-bits (`:878`) | **0 — the remaining delta** | 0 at boot (BSS; `vuMemReset` doesn't set R). All R writers normalize to `0x3F800000\|mantissa` (`VUops.cpp:1308-1341`, `VU0.cpp:178`) | RINIT ×2 (`sub_0036D400`, `sub_0038D660`), one ctc2-R restore; reads only inside the save/restore echo (self-consistent) → benign |
| `vu0_q` (Q) | 1.0 (ctor `ps2_runtime.h:149` + `:877`) | 1.0 (ctor) | 0 (BSS; never set at reset). True HW reset unknown — gap | 195 files mention `vu0_q`; reset value matters only if a `*q` op reads Q before any DIV/SQRT/RSQRT write on that thread (not established) |
| `vu0_p`, `vu0_i` | 0 | 0 | 0 (BSS) | P: 8 files, I: 2 files |
| `vi[0]` | 0 (memset) | 0 | 0, hardwired (`vuMemReset:41`) | Read once (save/restore `cfc2 $vi0`); game emits no `vi[0]` dest |
| `vu0_acc` | 0 | 0 | 0 (`vuMemReset` memsets ACC) | Reset-correct |
| `vu0_status/mac/clip` | 0 | 0 | 0 (VI memset) | Save/restore echoes them; our macro emitter models no flag updates (separate gap, not init state) |
| `cop0_random` | 47 (ctor `:152`) | 47 | Not verified in PCSX2 (gap); 47 = 48-entry-TLB − 1 per MIPS convention | 1 file (`sub_0042CD98`, kernel TLB region) |
| `cop0_status` | 0x10001 = EIE\|IE (ctor `:156`, "kernel handoff" model) | 0x10001 | Reset 0x70400004 (`R5900.cpp` `cpuReset`, ≈:69: CU0\|BEV\|TS). Deliberate model difference, main==thread | 44 files (EI/DI helpers set IE/EIE); the game never sees reset state |
| `cop0_config` | 0 | 0 | 0x440 (`cpuReset` ≈:68) | 0 files read → benign |
| `cop0_prid` | 0x2e20 (ctor `:157`) | 0x2e20 | 0x2e20 (`R5900.cpp:70`) ✓ | 0 files |
| `cop0_cause/epc/count/…` | 0 | 0 | 0 (memset in `cpuReset`) | cause 3, epc 4 (kernel exception region); no delta |
| `fcr31` | 0 | 0 | 0x01000001 (`cpuReset` ≈:72) | 809 files, but SSX 3's entry executes `ctc1 $zero,$FpcCsr` at 0x100118 (FCR31 := 0); all other writes are c.\<cond\> bit-23 RMW; zero whole-reads → reset delta moot |
| FCR0 (unmodeled; emitter returns constant 0, `fpu_translator.cpp:36`) | 0 | 0 | 0x2e30 (`cpuReset` ≈:71) | Unknown (emitted constant is indistinguishable in codegen text; needs an EE disasm sweep — gap) |
| `r[0]` ($zero) | 0 (memset + explicit `:875`) | 0 (memset) | Hardwired 0; enforced: reads forced 0 (`ps2_runtime_macros.h:1290`), all `SET_GPR_*` guard reg 0 (`:1319-1358`) | Fully enforced |
| MMI state | none (uses GPRs; no control state in the struct) | same | none exists | n/a |
| Rest (`sa`, `hi/lo/hi1/lo1`, `f[32]`, `f_acc`, `llbit/lladdr`, `cop2_ccr`, delay-slot state, VU0 control regs `cmsar/tpc/fbrst/itop/top/info/xitop/pc/cf/vpu_stat*`) | 0 | 0 | 0 (memset/BSS) | `f_acc` in 3 files (ADDA family); `llbit`=0 (no reservation) correct |

PCSX2 reset anchors: `R5900.cpp` `cpuReset` (PRId at `:70`; Config/Status/FCR0/FCR31 on
adjacent lines), `VUmicroMem.cpp` `vuMemReset:25-53`.

### Init sites a thread start does not repeat

- `ps2_runtime.cpp:872-878`: main = `R5900Context{}` + `r0`/`vf0`/`Q`/`R` patch.
  `startThread` (`EeScheduler.cpp:1117-1162`) assigns `R5900Context{}` (`:1132`) then sets
  only pc/a0/gp/sp/ra. Post-RD1 delta: **R only**.
- ELF load (`ps2_runtime.cpp:1234` pc, `:3791-3797` args/sp) has its thread equivalent
  inside `startThread`. No delta.
- `EeScheduler::reset` copies the main context into thread 1 (`EeScheduler.cpp` ≈:505:
  `main.context = mainContext`), so the main thread inherits the patched values.
- `seedVu0IdleSuccess` (`:253-266`) also sets R = 1.0-bits, but its only caller is the
  `executeVU0Microprogram` early-out (`:2683`), which runs for whatever context executes
  a VCALLMS — main and threads alike. No thread delta.
- `copyVu0StateToContext` (`:308-333`) pins `vf0` (`:331`) and `vi0` (`:332`) on the VU0
  micro round-trip for every context. Symmetric.
- Callback/invocation contexts copy the caller (`RPC.cpp:790`, `System.cpp:539`,
  `Thread.cpp:88`: `invocation.context = *ctx`), so they inherit a correct vf0
  post-RD1 (as RD1 noted). `GuestThread`/`GuestInvocation` (`ee_scheduler.h:100,107`)
  otherwise default-construct.

### Sibling write-guard gaps found (not implemented; brief scope is vf0)

- **VI0**: CTC2 guards it (`vu_translator.cpp:70-74`), LQI/SQI/LQD/SQD inc/dec guard it,
  VILWR guards it — but the integer ALU does not: VMTIR (`:94`), VIADD (`:141`),
  VISUB (`:146`), VIADDI (`:152`), VIAND (`:157`), VIOR (`:162`) emit raw `ctx->vi[vid]`
  stores. SSX 3 emits no `vi[0]` dest (verified: zero `ctx->vi[0] =` lines in codegen),
  so this is hardening-only for the game.
- **RNEXT-to-vf0** (pre-existing guard, `:190-198`) skips the R advance as well as the
  store; whether HW/PCSX2 advance R on a vf0-dest RNEXT is unverified. SSX 3 has no
  RNEXT sites — moot.
- **FCR0** should read 0x2e30, not 0 (`fpu_translator.cpp:36`); game usage unknown.

## 2. vf0 read-only fix

Precedent already in the tree: RNEXT/FTOI/RGET/LQI/LQD guard dest 0 with
`// V<op> to vf0 ignored` (`vu_translation_helpers.cpp:190-198,752-794,807-814`), and
CTC2-to-VI0 emits an ignore comment. The fix extends that convention to every remaining
vf writer (verified by sweep: no other `vu0_vf[` stores exist anywhere else in
`ps2xRecomp`):

- `ps2xRecomp/src/lib/vu_translation_helpers.cpp` +87: early-return guard in the 27
  `sa`-dest arithmetic helpers (VADD/VSUB/VMUL/VMADD/VMSUB/VMINI/VMAX families incl.
  `q`/`i`/`_Field` variants, VOPMSUB) plus rt-dest VMFIR and VITOF. All are pure-vf
  writers (ACC writers are the `*A` ops, which write no vf; Q writers DIV/SQRT/RSQRT
  write no vf), so skipping the whole emission is exact.
- `ps2xRecomp/src/lib/instruction_translator.cpp` +5 (LQC2): keeps the load, drops the
  store — `(void)READ128(...);` — matching PCSX2 (`VU0.cpp:94-103` reads into a dummy
  when `_Ft_ == 0`) and preserving special-address side effects and diag taps.
- `ps2xRecomp/src/lib/vu_translator.cpp` +3 (QMTC2): early ignore comment, matching
  PCSX2 (`VU0.cpp:128-137`, `if (_Fs_ == 0) return`).
- Tests: new `ps2xTest/src/ps2_tc1_vf0_tests.cpp` (+`CMakeLists.txt`, `main.cpp`
  registration): LQC2 driven through the real decoder on SSX 3's own encodings
  (`0xda000000` → no store + still reads; `0xda010010` → stores), QMTC2 translator
  level, and macro level covering both dest conventions (`sa`: VADD, VMADDq;
  `rt`: VITOF, VMFIR), each with a nonzero-dest control.

Commit `e29e4975` on branch `tc1-ctx` (from `0ed07c4`), 6 files +202, trailer
`Orchestrated-By: Muse Code`, not pushed. Runner-dir check
`git diff --stat 14b1e5cb tc1-ctx -- ps2xRuntime/src/runner` is empty.

Suite (Release, diag taps off, same flags as UV1/RD1; `ps2x_tests` run from the
worktree root): red 612 pass / 3 fail (rc=3) with the emitter fix stashed, green
**615/615 (rc=0)** with it. Logs: `~/dev/ssx3-work/TC1/{configure,build,build-red,
build-green,suite-red,suite-green}.log`.

## 3. Why no det boot (brief §3 conditional)

No `ps2xRuntime` file changed, and `ps2EntryRunner` links neither `ps2xRecomp` nor the
tests, so the runner is behaviorally identical with the current codegen — a det boot
would compare a binary against itself. Game-visible effect needs a codegen regen
(orchestrator-coordinated, per brief §2). Post-regen prediction: det-hash identical to
the `0ed07c4`+`51c759b` baseline, because the only vf0-writing guest op (`lqc2 $vf0` at
0x3fe9bc) restores exactly what the matching `sqc2 $vf0` saved from a correct context
(`sub_003FE828_0x3fe828.cpp:100` save / `:405` restore); skipping the restore keeps
vf0 = (0,0,0,1) either way.

## 4. Gaps and recommended next actions

Gaps: Q/P true hardware reset values (PCSX2 boots 0; no explicit init found; EE manual
not consulted); FCR0 usage by SSX 3 (needs EE disasm sweep); `cop0_random` PCSX2 value
unverified; RNEXT-to-vf0 R-advance semantics; no det boot / frames (§3).

Recommended (orchestrator decides): (1) regen + det-hash vs RD1 baseline (expect
identical), then fold `e29e497`; (2) one-line `vu0_r` = 1.0-bits ctor fix in its own
lane with a det boot (touches the shared header → full rebuild; benign per §1 but
closes the last thread delta); (3) fold vi0 integer-ALU guards + FCR0 0x2e30 with the
next regen (all unexercised by SSX 3, zero behavioral risk).
