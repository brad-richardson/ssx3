# N8X1 orchestrator gate — Odin black frame = hierarchical binner at wave128; wave64 fix; live race on screen (2026-09-24)

Read REPORT, NOTEBOOK, the three diffs and commits `0c9f471c`, `85d1c201`, `2e9a7367` (Brad-approved
2 h Opus exploratory session, 18:26–19:16 device work). Device state checked after: lease
`LEASE_FREE N8X1 explore done`, app not running, `ps2x.env` SHA `176eff84…cef32d` (= the pre-session
bytes recorded by P7's driver). Knob APK `19fed514…` remains installed (diagnostic).

Viewed frames: `orch-verify.png` (Mac / old Odin / Odin HIER=off on the original stream at tick2050:
full race frame matches the Mac by eye) and `orch-live-wave64.png` (live Odin device screencaps: Select
Peak menu and race at 00:00:05 with terrain, rider, HUD, radio card).

**Verdict A.** Evidence rows 7–9 isolate the cause: paraLLEl-GS enables hierarchical binning for passes
with >=256 primitives except on Apple; on Adreno (no exact wave32) the free 4..128 subgroup range runs
wave128 (`wg=512, hier=2` logged), and wave128 mis-bins (black tiles, run-to-run variance). Forcing
wave64 or flat binning gives full, deterministic frames (off r1 = r2 byte-identical; 91% of pixels
within ±2 of the Mac; remainder = hardware bilinear rounding, a separate small effect). Why wave128
fails in Turnip/ir3 is a labelled hypothesis (subgroup ID / ballot lowering), untested.

Accepted candidate: `n8x1-fix-clean.diff` (prefer fixed wave64 before the free-range fallback);
validated as APK 2's default path on replays; the clean diff itself was not built and no live run used
the default path yet. The fold lane must build it and run the live route with no knob env.

Not accepted as numbers: the live `off` 0.123x rate (diagnostic build) stays out of the ledger.
Loose ends: fine horizontal stripes on both live screens (seen since N8D2), sky missing (also Mac),
4:3 (APK predates W1), exact bilinear (shader regen needed), tick665-class STQ precision.
