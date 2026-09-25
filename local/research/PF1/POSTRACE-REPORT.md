> **ID collision:** `local/research/PF1/` already holds an older PF1 lane (Odin baseline, `REPORT.md`, `CHECKPOINT.md`, `logs/`). This post-race lane writes `POSTRACE-REPORT.md` + `NOTEBOOK.md` + `pf1_*.py` beside it; the orchestrator may want to rename the lane.

# PF1 report — post-race jump to garbage (PAUSED, 2026-09-25 ~13:58 EDT)

Exploratory Opus worker, Mac mini, started 13:02. Paused at Brad's request before the fix was
written. Details in `NOTEBOOK.md`; the orchestrator decides.

## Status

| Item | State |
|---|---|
| Repro on the F3 tip | **Yes.** C1 (`ec2dbf1` + PF1 commits, legacy slicing `PS2X_EE_TIME_SLICE=1` = F3 behaviour): same site `0x39e724`, tick 18823, rc −6; crash RAM + stack captured |
| Mechanism | **Named (runtime bug):** `PS2Runtime::dispatchGuestBranch` treats `ctx->pc == entryPc` after a callee as a normal return. When a checkpoint (timer-1 interrupt deadline here) suspends a **recursive** call to the same entry (`0x398868` → `0x398868`), the caller continues with the suspended callee's registers (`s0`/`s1` of `0x398868`), walks into a UI element list and calls through a float |
| Fix | **Not written yet.** Design in NOTEBOOK "Resume plan" (unwind-pending flag set by `checkpointDue`, honoured in the post-call check, cleared at top-level dispatch) |
| Fork branch | `pf1-postrace` (local, from `ec2dbf1`, not pushed): `9c98713` equal-priority time-slice change + test (**not the PF1 mechanism**; hold, don't fold as the fix), `a1eb9b9` dev-only `PS2X_MISSING_DUMP`. Runner-dir check empty. Suite 643/643 (642/643 under `PS2X_EE_TIME_SLICE=1`) |
| Validation boot | Not run. C0 (fixed-slice build) stopped at tick 10992 for host contention; never re-booted |

## Evidence

| Row | Receipt |
|---|---|
| FR1 crash: node `0x5aa300` +0x48 = `0x42640000` (57.0f), s1 = `0x5ae940` = element `0x5ae900` + 0x40 | `FR1/run/r1-full/boot.log:60049`; B2 menu-time watches (`PF1/run/B2-ram-stopped`) show `0x5ae900`/`0x5aa300` built by UI-element ctor `sub_0039FB30` |
| C1 crash: s1 = `0x5a7b40`, s0 = `0x5a9d00` = `[0x5a9b00+4]`; stack frame at `0x1ff7a80` is `0x398868`'s (ra `0x39e72c`, saved s1 `0x5bef00`, s0 `0x5a7b00`) | `PF1/run/C1-legacy/boot.log:1157-1166`, `crash.ram` + `pf1_lists.py` |
| Trace tail `… 0x397718 → 0x397718 → 0x3e4db8 (timer-1 handler) → 0x397718 → 0x39e738` | same line |
| Generated code: jalr at `0x39e724` continues at `0x39e72c` iff `dispatchGuestBranch` returns true | `codegen-ssx3/sub_0039E6B8_0x39e6b8.cpp:255-285`; `ps2_runtime.cpp` post-call check (`ctx->pc == entryPc` → fallthrough) |

## Builds and runners

`~/dev/ssx3-work/PF1/build` (Release, diag taps OFF, TEST ON, paraLLEl `19d93b2` copy, codegen
`8ea8ed43…`): `bin/runner-pf1` sha256 `811c7928b35b3cdb3ef60add1535cbb2d765d87162c45ca6581512498763d747`
(= `a1eb9b9`). RD1 `probe4` runner (0ed07c4) used for B1/B2 watches. Boot driver `pf1_boot.py`
(FR1's + `--env`, `--mc-src`, `--no-frames`, `PS2X_UNPACED=1`).

## Gaps

- No fix, no validation boot, no results-screen frames viewed (C1's frames at 17800 exist under
  `run/C1-legacy/frames/` but were not viewed before the pause).
- Host contention (load 40–50, three builds on 6 P-cores) made 20k-tick boots miss the 1,800 s cap;
  the validation boot (results + 2 min idle) probably needs > 1,800 s wall or a quiet mini.
- Brad's-card variant (lead 1) not tried; the mechanism doesn't depend on the card.
- Leases: none held at pause. Scratch `~/dev/ssx3-work/PF1` (~3 GB incl. build and paraLLEl copy).
