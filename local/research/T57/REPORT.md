# T57 REPORT — PCSX2: VU0 micro-program calls and VIF0 traffic at Select Character (healthy side of E44 Part 2)

Brief `local/muse/prompts/T57.md`. Tables + receipts; the orchestrator decides.
Read first: `AGENTS.md`, `local/AGENTS.local.md`,
`local/research/T56/REPORT.md`.

## T57-0. Mission table

| # | Mission | Result |
| --- | --- | --- |
| 1 | Log-only VU0-start + VIF0-census hooks on T56's clone, EE + VU0 interp | DONE — 5 TUs, all anchors first try, b1 clean |
| 2 | Builds ≤2 | DONE — 1/2 (b1: 5 TUs + 2 links, no fixup) |
| 3 | Preservation (G13 replay 7/7 + HWSTAT, zero T57 lines) | DONE |
| 4 | Capture: settled-SC boot, first 2000 lines | DONE — 1 capture, 913 vsyncs, 0 rejects |
| 5 | Tables (VU0 by startPC + vi1/vi2; VIF0 per vsync; 0x37deb8 mark) | DONE — all three are empty; bounds stated (§T57-4) |
| 6 | Null verification (hooks proven live, §T57-5) | DONE — no second capture needed |
| 7 | Receipts + `[T57]` commit, no push | DONE (this file + dir) |

Headline for the orchestrator: **over the entire SC-settled boot
(vsyncs 0–912, game alive every vsync), PCSX2 executes ZERO VU0
micro-programs (no COP2 `vcallms`/`vcallmsr` from any EE pc, no VIF0
MSCAL/MSCALF/MSCNT-started program) and transfers ZERO VIF0 command words.
The `vcallmsr` at EE `0x37deb8` (`sub_0037D968`) never executes in-window.
The hooks are proven linked into the run binary and the logging path is
proven live in-run (same binary/emit path produced 1536 T56-`spw` lines).
Reading (no verdict): the T56 staging buffers are baked pre-window and the
walker/DMA replays them every vsync with no VU0 involvement — a VU0
cull/skinning program that stages those buffers must run at scene build
(before the statefile point), not in the settled window. Recommended next:
a scene-build-window capture (cold boot toward SC, or an earlier state) to
find where `0x37deb8` and the VU0 program actually run.**

## T57-1. Pins

| Pin | Value |
| --- | --- |
| PCSX2 tree | `9056c08349cc29ad02a6d1a3a4133259019195af` (`/home/brad/pcsx2-g7/pcsx2`); base = T56-end working tree + T57 hooks below |
| T57 binaries SHAs | qt `340bc502aa880971221d4ee20027006fcd1e745259331b0c2d8a816054362960`, gsrunner `4012e3fdea7f623b330258fcc9c04b617bdb5288019ed948bb7df519a68378bf` |
| Patch | `t57-patch.diff` 9,759 B sha256 `1ca0a48d79c3683a6a156ed343b192a2660eef7da96228e40a073830a6b97ab6` (diff of the 5 touched files vs HEAD; stacks on the T56 tree) |
| Inputs | ISO `SSX 3 (USA).iso`; `dat-t57` = `dat-t50` copy + `EnableVU0=false` (EE+VU0 interp; `EnableEE=false` kept); state `t50-sc-state` (T50 SC-settled F1) |
| Capture (TAG=t57a) | CWINDOW 495, TARGET 501 PATHS seen, `vu0call` 0, `vif0op` 0, `T57_CAP` 0, `ctag` 3606, `spw` 1536; LOADED 1.5838/45; F8 `t57a-shot-sc.png` (Zoe SC screen); trace `t57a-trace.txt` 101,248 B sha256 `e92263adf76bc211332e9e6e0cc8b0fcad207f4f8c7e2eb2f145e80d04ffd627` |
| Trace span | `T48_PATHS` vsyncs 0–912 (913 vsyncs, game alive throughout); 0 grammar rejects |
| Probe boot (T56 binary + dat-t57, pre-build) | CWINDOW 496, TARGET 502, `T48_MODE mtvu=0`, `spw` 1536, `ctag` 3606 — statefile loads under VU0-int, route identical |
| Poll logs | `t57a-poll.log`, `t57probe-poll.log` |

Builds: b1 clean (5 TUs + 2 links, ~5 s incremental). Captures: 1/2.
~40 min wall of 3 h; bytesize ≈ 970 MB new of 2 GB (`dat-t57` 865 MB
dominates: 796 MB copy + capture emulog/snaps).

## T57-2. Execution model + the patch

Probed before authoring (probes 1–9, read-only). The VU0-start choke point
is `vu0ExecMicro(u32 addr)` (`VU0micro.cpp`): it has **exactly 3 callers**
— COP2 `VCALLMS` (imm `(code>>6)&0x7FFF`), COP2 `VCALLMSR`
(`VI[CMSAR0]`), and `vifExecQueue(0)` (`Vif_Codes.cpp:44`, for VIF0-queued
MSCAL/MSCALF/MSCNT; MSCNT-continue passes `addr=-1`, resuming TPC). VIF0
`vuExecMicro(idx,...)` only *queues* (`queued_program`/`queued_pc`); real
execution always funnels through `vu0ExecMicro`. All VIF0 packet words flow
through `vifTransferLoop<0>` (`Vif_Transfer.cpp`), next to T49's VIF1 hook.
E-bit stop under VU0 interp is the `ebit-- == 1` block in `_vu0Exec`
(`VU0microInterp.cpp`).

Review-claim check (PCSX2 side only): **no 4,096-cycle budget exists on the
VU0-interp path.** The only `0x1000`s are `VU0_MEMSIZE`/`VU0_PROGSIZE`
(byte sizes, `VUmicro.h`). `InterpVU0::Execute` loops unbounded to
E-bit/M-bit/`VPU_STAT`-clear, and `_vu0run` pumps with
`runCycles=0x7fffffff`. `EECycleRate=0` in the dat, so `VU0.cycle` needs no
rescale. (Whether the *recomp* runner has such a budget is not observable
here.)

`t57-hook.py` (validate-all-then-write, idempotent; asserts every anchor):

| Hook | Anchor | What |
| --- | --- | --- |
| T57 decl | `#include <cmath>` in VU0micro.cpp (×1) | budget (2000 lines + `T57_CAP`), VIF namer (T49's table, copied), pending-program + armed-context state, emit/count/flush/arm/entry/ebit functions |
| T57 entry/arm | `void vu0ExecMicro(u32 addr) {` + `CpuVU0->SetStartPC(...)` (×1 each) | `t57_entry()` (prior program died with `VPU_STAT` clear → `end=abort`); `t57_arm()` after the stall-finish (still-pending → `end=abort`, else arm caller/via/startPC=`TPC<<3`/cycle) |
| T57 COP2 ×2 | the two `vu0ExecMicro(...)` call lines (×1 each) | `t57_cop2_ctx()` (via=cop2, caller=`cpuRegs.pc`) after the finish-pump, before the call |
| T57 VIF queue | `if (!idx)` + `vu0ExecMicro(vif0.queued_pc)` block (×1) | `t57_vif0_ctx()` (via=vif0) — braced so the `if` stays exact |
| T57 MS ops ×3 | the three `vuExecMicro(idx, ...)` call lines (false/true/-1, ×1 each) | `t57_msop(0x14/0x15/0x17)` for MSCAL/MSCALF/MSCNT (idx 0 only) |
| T57 census | `if (idx == 1) t49_vif_record(` (×1) | `if (idx == 0) t57_vif0_count(vifX.cmd & 0x7f)` after it |
| T57 ebit | `VPU_STAT ... &= ~0x1; /* E flag */` + next line `vif0Regs.stat.VEW = false;` | `t57_vu0_ebit()` — emits the pending line with cycles + post-run `VI[1]`/`VI[2]` (interp only) |

Line formats (grammar-checked, 0 rejects):

- `vu0call vsync=<n> caller_pc=0x<> via=<cop2|vif0|unknown> startPC=0x<byte> cycles=<n> vi1=0x<> vi2=0x<>[ ms=0x<14|15|17>][ mark=sub_0037D968][ end=abort]` — `ms=` (vif0 only) names the queuing MS op; `mark=` flags COP2 caller `0x37deb8`; `end=abort` = never reached E-bit (cycles approximate). vsync is read at completion.
- `vif0op vsync=<n> op=<NAME> n=<count>` — per-(vsync,op) nonzero counts, flushed on vsync change (+ opportunistic flush when a `vu0call` completes in a newer vsync). A vsync with no VIF0 words yields no lines.

## T57-3. Preservation

G13 rich-dump replay on the T57 gsrunner: **7/7 PNG md5s match the T48
pins exactly** (`b7a3e8db a7929218 bb8b1d85 817e934f ×2 85cf3599 ×2`),
HWSTAT exact (791/37/0/14/320/6), zero `vu0call`/`vif0op`/`T57_CAP` lines
(gsrunner runs no EE/VIF).

## T57-4. Tables (capture t57a)

913 settled vsyncs (PATHS 0–912), budget untouched (0/2000, no `T57_CAP`).

Table 1 — VU0 calls by startPC: **(empty: 0 micro-program starts)** — no
row for any startPC; no cop2/vif0/unknown callers; `mark=sub_0037D968`
count 0; `end=abort` count 0.

Table 2 — VIF0 opcodes per vsync: **(empty: 0 VIF0 command words)** — no
vsync has any `NOP/STCYCL/.../MSCAL/MSCALF/MSCNT/UNPACK/...` count.

## T57-5. Why the null is trustworthy (no second capture spent)

1. Hooks linked into the run binary: `nm` shows all 7 `t57_*` functions +
   state; `strings` shows the 3 `vu0call` variants + `vif0op` + mark
   (probe13; SHA matches the b1 pin).
2. Trigger sites exhaustive by source: the only 3 `vu0ExecMicro` callers
   are hooked; `vifTransferLoop<0>` is the sole VIF0 packet path.
3. Logging path live in-run: the same binary/emit path wrote 1536 T56
   `spw` + 3606-path markers to the same emulog.
4. Guest identical to T55/T56: `ctag` 3606 exact, `spw` 1536 exact, LOADED
   1.58/45 in the same <2.0 SC band, F8 = Zoe SC screen.
5. VU0 interp confirmed in-run (`VU0 Recompiler is not enabled`,
   `T48_MODE mtvu=0` in the probe boot).
6. Liveness: any started program must complete-or-abort visibly — EE pumps
   `_vu0FinishMicro` constantly and a stuck VPU would freeze the game,
   which ran 913 vsyncs. Residual hole (§T57-7.5): a start orphaned by
   `vu0ResetRegs` with no following start stays invisible; at most the
   trailing edge can hide this way.

## T57-6. E44 join keys (for the orchestrator)

| Fact | T57 (PCSX2, healthy, settled window) |
| --- | --- |
| VU0 micro starts (COP2 or VIF0) | none in 913 vsyncs (bound: 0/2000-line budget untouched) |
| VIF0 command words | none in 913 vsyncs (all ops incl. MSCAL/MSCALF/MSCNT: 0) |
| `vcallmsr` @ `0x37deb8` (`sub_0037D968`) | never executes in-window (no COP2 caller at any pc) |
| VU0 cycle budget (PCSX2 interp) | no cap exists; programs run to E-bit (none ran to observe) |
| Route identity | ctag/spw/LOADED/F8 identical to T55/T56 — same guest code, VU0 simply idle |

## T57-7. Gaps, overruns

1. Builds 1/2, captures 1/2 (plus one probe boot on the pre-build T56
   binary — method validation, not a capture). ~40 min wall; ~970 MB new
   of 2 GB.
2. The 2000-line cap was never approached; the window is the full boot
   (PATHS 0–912), not a capped prefix.
3. `vu0call.vsync` is read at E-bit completion (start and completion are
   ≤1 program apart; skew class same as T48's GS/EE mirror).
4. `vi1`/`vi2` are `VU0.VI[1]`/`VI[2]` post-run by construction; `ms=`
   attributes the last queuing MS op (a superseded queue is correctly
   attributed to its last queuer).
5. Residual hole: a `vu0ResetRegs` (COP2 CTC) orphan with no later start
   emits nothing; only the trailing edge can hide it (no reset chatter in
   the emulog either).
6. Census trailing-vsync flush is opportunistic (moot here: zero counts).
   Vsyncs with zero VIF0 words are silent by design — here that is
   all of them.
7. `dat-t57` (865 MB) duplicates `dat-t50` + one ini flip; pinned inputs
   (`dat-t50`, state, ISO) untouched.
8. LOADED p99 45 vs T56's 36–47 (same watch-logging jitter class; speed
   gate already passed on gsrunner, §T57-3).

## T57-8. Exact commands

Bytesize over foreground `ssh bytesize` + `wsl -d Ubuntu` (outer
double-quotes for the remote command; no pipes/redirection inside the ssh
string — all multi-step logic in staged files under `t57stage/`, the
Windows-home staging dir): probes (`probe1..9.sh` code reads;
`probe10-boot.sh` = `t57-probe-boot.sh`, T56-binary load check on `dat-t57`
created by `cp -r dat-t50` + `sed EnableVU0=false`) → `t57-hook.py`
(validate-all-then-write; all anchors first try) → `t57-build.sh`
(`cmake --build …/build --target pcsx2-qt pcsx2-gsrunner -j2`; b1 clean;
SHAs §T57-1) → `t57-replay.sh` (G13 dump, 7/7 + HWSTAT + zero T57 lines)
→ `t57-cap.sh` (`TAG=t57a`, dat-t57 asserts `EnableEE=false` +
`EnableVU0=false`, statefile, free-gate, CWINDOW→PATHS V+6, F8) →
extract (`t57-extract.sh` grammar, 0 rejects) + analyze
(`t57-analyze.py`, empty tables + bounds) → null verification
(`probe11/12.sh` emulog signs-of-life; `probe13.sh` `nm`/`strings` on the
run binary) → `git diff --output=…/t57-patch.diff -- <5 files>` (note:
`--output` precedes `--`) → staged (`probe14.sh`) → scp home.
`git log -1` checked before commit (main @ `31d4f00` + prior lane commits).

## T57-9. Receipts

Repo (this commit): `local/research/T57/` — REPORT.md, `t57-patch.diff`
(9,759 B), applier (`t57-hook.py`), build/cap/extract/analyze/replay
scripts, boot probe (`t57-probe-boot.sh`), verification probes
(`probe11/13/14.sh`), `t57a-trace.txt` (sha §T57-1), `t57a-poll.log`,
`t57probe-poll.log`, F8 `t57a-shot-sc.png`. (Probes 1–9 were read-only code
reads superseded by §T57-2; not committed.) Bytesize residue under cap:
`t57stage/` (scripts, trace, poll logs, PNG, `t57-patch.diff`), `dat-t57/`
(865 MB), rotated emulogs, `t57-frames/`, both binaries (§T57-1).
