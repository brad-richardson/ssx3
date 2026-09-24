# AU5 — Find the arithmetic that distorts the EE sound mix

You are a worker in a herdr pane in the ssx3 repo (`~/dev/ssx3`, Mac mini).
Follow `~/dev/AGENTS.md`. **Tables + receipts; recommend, the orchestrator
decides.** Read first:
- `AGENTS.md` (the two-slot lease; kill by PID; never attach a debugger to
  a harness child);
- `local/AGENTS.local.md`;
- `local/research/AU2/REPORT.md` (the protocol and the decoder
  `sub_003CCA08`: coefficient table, nibble shift, 15-byte/28-sample
  frames; `au2_eaxa.py` is a reference decoder that works on the disc
  data);
- `local/research/AU4/REPORT.md` (all three parts);
- `local/research/AU3/REPORT.md`.

Write scope: `local/research/AU5/`, `~/dev/ssx3-work/AU5/`, a new fork
worktree `~/dev/ssx3-work/AU5/PS2Recomp` on local branch `au5-snd`, and the
lease files via `local/tooling/p_lane_lease.py`. No push.

## Facts

- AU4 aligned our EE tag-1 mix (AU2's capture) with PCSX2's at NCC 0.975.
  The local lag is constant to within 1 sample over 32 s, so it isn't
  timing. After per-window lag correction the difference is still
  **0.23 of the PCSX2 RMS**:
  - 0.19 at 0–2 kHz;
  - 0.52 at 2–6 kHz;
  - 0.57 at 6–12 kHz;
  - 1.06 at 12–18 kHz.

  Brad hears it as distortion; the PCSX2 reference sounds clean.
- AU2's runner was fork `eac6cba`, **before** E53's semantics batch
  (VU0 macro VSQI/VLQI, MIN/MAX/C.cond, DIV.S specials, RTZ+FZ, no FMA).
  The fold E58 puts those on `ssx3`.

## Work

0. **Base:** fork `ssx3` after E58's push. If E58 hasn't pushed when you
   start, wait and poll `git -C ~/dev/PS2Recomp fetch fork &&
   git -C ~/dev/PS2Recomp log -1 fork/ssx3`. Cherry-pick AU3's sound
   commits (branch `au3-snd`, the latest AU3 report names them) onto it.
   Build with the diagnostic taps OFF, `nice`d.
1. **Discriminator (1 boot):** capture ≥40 s of menu tag-1 PCM with
   `PS2X_SOUND=1` and the WAV tap. Run AU4's `compare.py` +
   `lag_track.py` against `~/dev/ssx3-work/AU4/pcsx2-tag1-36k.wav`, and
   table it next to AU4's AU2 numbers. If the corrected residual falls
   below 0.02 overall, stop there: E53's semantics fixed it. Also make a
   ≤5 MB `.m4a` for Brad.
2. **Static census (no boot):** with `local/tooling/ee/ee-func`, `ee-xref`
   and `ee-at`, list the EE functions on the decode/mix path: the XA
   decoder `sub_003CCA08`, its caller `0x3CCF90`, and the mixer that fills
   tag 1 (follow from the sound thread `0x3C1B48`). For each function,
   list every MMI (P*), COP1 and COP2/VU0-macro instruction. Mark each
   opcode "tested" (it has a unit test with edge inputs against PCSX2
   semantics in the fork suite) or "untested". Pay particular attention
   to saturating and packing ops (PPACH/PMAXH/PMINH/PADDSH…), halfword
   multiplies (PMULTH/PMADDH/PHMADH), shifts (PSRAH/PSRLH/PSLLH/PSRAVW…),
   PINTEH/PINTH/PEXCH/PEXEH lanes (frontier review 2 flags PINTEH), and
   LQ/SQ alignment.
3. **Differential (≤1 boot):** add an env-gated dev tap (off by default)
   that dumps, for the first N calls of `sub_003CCA08`:
   - its input frame bytes;
   - the channel history in/out;
   - its output samples.

   Decode the same input with `au2_eaxa.py` and compare sample for
   sample. If they match exactly, the fault is in the mixer: tap the
   mixer's inputs and outputs the same way and compare with a Python model
   of the mixer that you write from its disassembly.
4. **One candidate fix,** if steps 2–3 name a single instruction's
   semantics: fix it with a unit test (edge inputs, PCSX2 semantics), one
   validation capture, and the step-1 table again.

## Budgets and stop rules

≤3 builds, ≤3 boots (one slot each), 6 h, cap 6 GB. Stop and hand back if
the first differing sample can't be traced to one function, or if more
than one instruction is implicated. The orchestrator then splits the
work.

## Deliverable

`local/research/AU5/REPORT.md` (tables, commands, runner SHA ×2,
suite count, runner-dir check). `[AU5]` commit (`git add -f
local/research/AU5 local/muse/prompts/AU5.md`, `git log -1` first).
