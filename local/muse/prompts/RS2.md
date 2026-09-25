# RS2 — cached baselines + one shared boot driver (muse, 2 h)

## Goal
Most lanes boot a control and a candidate. The control for a given fork tip is the same every time, so store it once and let lanes boot only their candidate. Brad approved this 09-25. Also stop copying boot drivers from lane to lane (RP1 → F5 → MC1 …) by promoting one driver to `local/tooling/boot/`.

## Facts
- Latest driver: `local/research/F5/f5_boot.py` (modes det/speed, routes fr1r1/i26, `--dump-ticks`, `--hash-every`, `--env`, `--stack-kb`, lease claims via `local/tooling/p_lane_lease.py`). Compare: `local/research/GB8/gb8_hashdiff.py --base run/A --cand run/B`.
- F5 already has a det control for fork `a3efbfe`: `~/dev/ssx3-work/F5/bin/runner-det` (`119389a7…`) and its boot `~/dev/ssx3-work/F5/run/B1` (FR1-R1, t2400, frames at 1090/1800, snd `cid0=531`, coverage `targets=0`) + `run/B1b` (t2100 frame). Pins in `local/research/F5/REPORT.md`.
- Pins that define a baseline: fork SHA, codegen (`register_functions.cpp` SHA + one changed-file SHA as F5 records), VU1 image set SHA, paraLLEl-GS SHA, build flags (det/non-det), route, stop tick, env (sound, backend, SSAA/hi-res/pipeline), ISO/ELF SHAs.

## Steps
1. Copy `f5_boot.py` to `local/tooling/boot/ssx3_boot.py` (behavior unchanged; leave F5's copy in place). Add `--out DIR` if the run dir isn't already configurable.
2. Write `local/tooling/boot/baseline.py`:
   - `put --runner R --run DIR --pins pins.json`: copy the runner binary + the run's text receipts (det-hash log, boot log tail, coverage/snd/VU1-stats lines, `result.json`) and frame PNGs into `~/dev/ssx3-work/baselines/<key>/` with a `manifest.json` (all pins, SHAs of every stored file). Key = short hash of the canonical pins JSON + a readable prefix (e.g. `a3efbfe-det-fr1r1-t2400-snd1-1x`).
   - `get <key|--pins pins.json>`: print the dir, or exit 2 with `MISSING <key>`. Verify stored SHAs on read (two reads for the runner).
   - `list`: table of keys, pins, dates, sizes.
   - `compare --key K --cand RUNDIR`: runs `gb8_hashdiff.py` against the stored run and prints IDENTICAL / first differing tick; also diffs the snd/coverage lines.
   - `make --pins pins.json --runner R`: boots the control with `ssx3_boot.py` (one mini slot, lease) and `put`s it.
3. Seed: `put` F5's B1 (and B1b's frames) under the `a3efbfe` det key. Then a self-test: boot `runner-det` again with `ssx3_boot.py` (one slot, FR1-R1, t2400) and `compare` → IDENTICAL. That proves both the promoted driver and the store.
4. `local/tooling/boot/README.md` (≤ 40 lines): how a brief uses it ("control: `baseline.py get …`; if MISSING, `make`, then boot only the candidate").

## Rules
≤ 2 boots, one mini slot each, no builds. Baseline store `~/dev/ssx3-work/baselines/` ≤ 3 GB. Never touch the fork. Text only in git (no PNGs/binaries). Don't edit `docs/`: put proposed runbook/brief-template text in the report. First failure: stop, save the error, hand back.

## Deliverable
`local/research/RS2/REPORT.md` (commands, the self-test result, store layout, sizes, proposed runbook text, gaps) + `local/tooling/boot/{ssx3_boot.py,baseline.py,README.md}`; commit `[RS2] …` (explicit paths, `git add -f`, trailer `Orchestrated-By: Muse Code`), no push.
