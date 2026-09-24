# N8D7M13 Part A orchestrator gate — Mac STEP=1 control read, launcher amended (2026-09-24)

Read REPORT and worker commit `544fb2f7`. The Mac STEP=1 run (binary `3b21ce61…`, rc 0,
586/586) produced 2050 ordered `GB4_REPLAY` rows. At the 41 shared ticks it equals the STEP=50
Mac control in **VRAM 41/41 and priv 41/41**; present 0/41 and PKTSEQ seq/commands 0/41 differ.

Orchestrator reading (not the worker's stop rule verbatim):
- PKTSEQ counts grow by ~2 commands per extra sample (349 vs 251 at tick50, +4,018 by tick2050),
  consistent with each sample adding its own readback/flush commands. Sampling-induced, expected.
- Viewed Mac STEP=1 vs STEP=50 tick2050 frames (`~/dev/ssx3-work/N8D7M13/macpair.png`): the same
  race frame (HUD 00:00:05, terrain, rider). The present-hash difference is presentation cadence,
  not rendered content.
- So **VRAM is unperturbed by per-tick sampling on the Mac** and remains a valid baseline for an
  Odin STEP=1 comparison. The control passes for VRAM/priv; PKTSEQ/present are cadence-dependent.
- PKTSEQ stdout interleaves with `[INFO]: G11: flush()` lines at STEP=1 (2023 strict rows of 2050),
  so a strict PKTSEQ gate would void a good device run.

**Amendment:** launcher PKTSEQ gate made best-effort (rows and lines recorded, not fatal); the
2050-row `GB4_REPLAY` tick gate stays. Released SHA
**`50abff3da0e2af7a83c9cc01021589417506cf817e2812219bf67d961791a557`** (double read, `py_compile`
OK). The worker checker (38/38 at `f70f8ae1…`) will now flag this amendment; that is expected.

13B readings: compare Odin vs Mac STEP=1 per tick on **VRAM** (primary) and priv; present and
PKTSEQ are Odin-vs-Mac-at-STEP=1 secondary. First VRAM departure ≤50 → packet bisect; VRAM equal
far beyond tick50 → per-tick readback hides the fault (sync implicated).
