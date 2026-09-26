# TM1 — observe SSX 3's live simulation-step chain in a race (muse, 2.5 h, observation only)

## Goal
RV6 (`docs/research/review-2026-09-26-astra-120hz.md`, read §1 and §5 fully) recovered SSX 3's timing model statically: an application manager **A** at `gp+0x2a74` with nominal rate `A+0x10`=60, step duration `A+0x14`=float(1/60), a producer multiplier `A+0x24`=1.0 + fractional accumulator `A+0x28`, a catch-up threshold `A+0x20`=12, VBlank-end (INTC 3) → semaphore → worker → producer `0x317348` → ring of 30 → consumer `0x227e98` → active-app update (vtable slot `+0x34`). This lane **observes** it live in a race, the prerequisite for any 120 Hz simulation experiment (the product's eventual goal). No behaviour change, no candidate fix.

## What to record (RV6 §5 "First-experiment brief sketch" is the spec; follow it)
A default-off, observation-only tap (`PS2X_TIMING_TAP=1`, armed for race ticks ~1800–2400) that logs per VBlank, bounded (≤ 32 MiB text per run): EE cycle, VBlank tick, `A` and its vtable, the active-app object and vtable (confirm slot `+0x34` target vs RV6's static `0x2306b8`), `A+0x10..0x34`, producer/consumer ring indices, producer calls per wake, consumer successes per main-loop pass, active-app update entries/returns, render calls, and the rider position triple at `0x5409c0` before/after each update. Plus a bounded attribution of what writes the HUD race clock (report "not found" if it exceeds the cap).

## Predictions to test (from RV6)
One produced record per wrapper wake at multiplier 1; one app update per successful consume below the threshold; no dt inflation when rendering lags. Alternatives: render-coupled updates, extra physics substeps inside one app update, variable-time consumers. Say which the data supports.

## Setup
Fork worktree `~/dev/ssx3-work/TM1/PS2Recomp`, local branch `tm1` from fork `ssx3` `173b31f` (never push; runner-dir check empty). Build det runners with `local/tooling/build/bradflix_build.sh` (needs a SHA bradflix can fetch: carry your commit there with a git bundle into a private ref as VR2/SS2 did, never to GitHub) and boot on bradflix (`local/tooling/boot/ssx3_boot.py --host bradflix`, FR1-R1, t2400, 600 s cap). Two boots with the tap (repeat check: identical logs) and one with the tap compiled in but unset, compared to the a3efbfe baseline (`baseline.py compare`, must be IDENTICAL: the tap must not perturb the guest). Guest addresses come from the generated code `~/dev/ssx3-work/codegen-ssx3/` (read-only; derived from game data, never committed).

## Rules
≤ 3 builds, ≤ 4 boots. Stop on a foreign lease, unexpected pointers, lost rows, or a repeat mismatch; hand back counts and the first disagreement. Text only in git (bounded logs compressed). Workers don't edit `docs/`.

## Deliverable
`local/research/TM1/REPORT.md` (the observed chain with counts per VBlank, which prediction holds, HUD-clock writer or "not found", tap overhead, exact commands, SHAs, gaps) + `[TM1]` commit (explicit paths, `git add -f`, trailer `Orchestrated-By: Muse Code`), no push.
