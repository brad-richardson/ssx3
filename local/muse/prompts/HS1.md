# HS1 — host split: fast bradflix builds + 4 bradflix boot slots (muse, 3 h)

## Goal
Brad (09-25): after F5, move correctness boots to bradflix (4 slots) and keep the mini (1 slot) and the Odin for speed benchmarks. Blocker first: a full paraLLEl build on bradflix took ~50 min because one 32-file game-code unity batch (`unity_74`) spent ~25 min in clang 18 -O3 (`local/research/LX1/REPORT.md` ~l.690–700, 749). The Mac builds the same tree cold in ~270 s. Target: bradflix cold ≤ 5 min, warm ≤ 2 min, det-hash equal to the Mac baseline.

## Facts
- bradflix: Ubuntu 24.04, x86_64, 20 cores, 62 GB, Arrow Lake iGPU (Mesa ANV). No sudo; Docker image `ssx3-lx1` (`local/research/LX1/Dockerfile`, clang 18). GPU: `--device /dev/dri/renderD128 --group-add 993`; X via the driver's Xvfb (`local/research/LX1/lx1_boot.py`, `--gpu`). paraLLEl there runs `desc=buffer` (Odin's path). `/tmp` is wiped on reboot.
- LX1 fixed the TZ leak and the x86 MXCSR clobber; bradflix det-hash equals the Mac to t2400 (CPU and paraLLEl).
- Recipe of record: `local/tooling/build/mac_build.sh` (RS1). Boot driver: `local/tooling/boot/ssx3_boot.py`; controls: `local/tooling/boot/baseline.py` (key `a3efbfe-det-fr1r1-t2400-snd1-1x-a5f2f32d`). Lease: `local/tooling/p_lane_lease.py` (mini slots 1–4).
- Fork `ssx3` `a3efbfe`, paraLLEl-GS `19d93b2` + Granite `166ba21a`, canonical codegen `~/dev/ssx3-work/codegen-ssx3`, VU1 images `~/dev/ssx3-work/vu1gen-ssx3` (sync to bradflix with SHA checks; generated code never leaves our machines otherwise).

## Steps
1. **Why unity_74 is slow:** reproduce that one TU in the container with `-ftime-trace` (or `-ftime-report`); name the pass and the function(s). Try, one at a time, and time each: (a) clang 20+ in the image (apt.llvm.org), (b) `PS2X_RUNNER_UNITY_BUILD_BATCH_SIZE` smaller for game code, (c) that TU at a lower opt level only if (a)/(b) fail — report the det-hash effect of anything that changes codegen flags. Pick the best; no tuning loops.
2. **Build script:** `local/tooling/build/bradflix_build.sh <fork-sha> <build-dir> [--det]` — syncs inputs (SHA-checked), builds in Docker with ccache (cache in a bind-mounted `~/dev/ssx3-work/ccache`, `base_dir` set), prints wall + hit rate. Cold and warm times; runner SHA.
3. **Boots:** `local/tooling/remote/bradflix_boot.sh` (or `ssx3_boot.py --host bradflix`): one boot in Docker with GPU + Xvfb, same args/outputs as `ssx3_boot.py`, results synced back into a local run dir so `baseline.py compare` works unchanged. Lease: extend `p_lane_lease.py` with `--host bradflix` (4 slots, lease files on bradflix under `~/.ssx3-lease/`, `--exclusive` claims all four; default host stays `mini`, legacy behavior unchanged).
4. **Acceptance:** 4 concurrent det boots on bradflix (FR1-R1, t2400, paraLLEl, `PGS_HIER_BINNING=force`), each `baseline.py compare` vs the `a3efbfe` key → IDENTICAL; wall per boot concurrent vs single; bradflix load/memory during the 4-way run.
5. Proposed runbook/AGENTS text for the host split in the report (orchestrator edits docs).

## Rules
bradflix: builds and boots only inside Docker; don't touch its media services or other containers; `docker ps` first and keep total load reasonable (it serves media). ≤ 8 builds, ≤ 8 boots. Scratch `~/dev/ssx3-work/HS1/` on the mini ≤ 5 GB and `~/dev/ssx3-work/` on bradflix ≤ 40 GB. No fork commits needed (report if one is); never push. Text only in git. First failure: stop, save the error, hand back.

## Deliverable
`local/research/HS1/REPORT.md` (unity_74 diagnosis, build times table, lease/boot design, the 4-way acceptance table, proposed doc text, gaps) + the scripts and the `p_lane_lease.py`/Dockerfile edits; commit `[HS1] …` (explicit paths, `git add -f`, trailer `Orchestrated-By: Muse Code`), no push.
