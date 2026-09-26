# HS2 — make `bradflix_build.sh` safe with several lanes at once (muse, 1.5 h)

## Goal
VR2 (`local/research/VR2/REPORT.md` Part 2B, "Bradflix incidents") hit two races in `local/tooling/build/bradflix_build.sh`: (1) every build checks out its SHA in the **one shared** `~/dev/ssx3-work/HS1/PS2Recomp` clone (`:82-87`), so a concurrent lane switched the tree mid-build (mixed sources); (2) a paraLLEl pin mismatch triggers `rm -rf` of the **shared** `HS1/parallel-gs` + re-clone (`:126-132`), and two lanes' re-clones collided. `codegen`/`vu1gen` are also overwritten in place when their hash differs (`:96-105`). Several lanes now build on bradflix at once (VR2, TM1, F6's successors). Make concurrent builds safe and unpushed SHAs buildable, without changing what gets built.

## Design (keep it this simple)
- **Fork source per build:** export the requested SHA with `git -C ~/dev/PS2Recomp archive <sha>` on the mini and untar it into `~/$RROOT/<name>/src` on bradflix (works for unpushed local commits too; drop the `git fetch/checkout` on the shared clone). Record the SHA in the build dir.
- **Inputs by content, never overwritten:** paraLLEl in `~/$RROOT/pgs-<pin12>` (created once: clone `--recursive` into a temp dir, checkout the pins, verify 29/29 submodules, then atomic `mv`; if the dir exists, verify pins and use it; **never `rm -rf` a shared dir**). `codegen-<sha12 of register_functions.cpp>` and `vu1gen-<sha12 of the image manifest>` the same way.
- **One lock** around the setup phase on bradflix (`flock ~/$RROOT/.setup.lock`), released before compiling.
- CLI unchanged (`<fork-sha> <build-name> [--det]`), plus optional `--vu1 DIR` / `--codegen DIR` / `--pgs-pin SHA` passthroughs like `mac_build.sh`. Keep the Docker image, ccache mount and flags byte-identical.
- Leave the old shared dirs in place (other lanes may be mid-build); list them in the report for later cleanup.

## Acceptance
1. Two builds started 10 s apart for **different** SHAs (fork `ssx3` tip and `173b31f`) both succeed; each runner's embedded sources match its SHA (check a file that differs between them).
2. A build of an **unpushed** local commit (make a throwaway branch with one comment change; delete it after) succeeds.
3. A rebuild of the fork tip gives a byte-identical runner to a first build (reproducibility kept) and ccache hits.
4. One det boot of the tip runner via `ssx3_boot.py --host bradflix` → `baseline.py compare` vs `a3efbfe-det-fr1r1-t2400-snd1-1x-a5f2f32d` IDENTICAL.

## Rules
Only `bradflix_build.sh` (+ its README lines if any) and your report. bradflix: Docker only, `docker ps` first, don't touch media containers, don't delete other lanes' dirs. ≤ 6 builds, 1 boot. Workers don't edit `docs/`; put proposed runbook text in the report. First failure: stop, save the error, hand back.

## Deliverable
`local/research/HS2/REPORT.md` (design, acceptance table, old dirs to clean later, runbook text) + the script; commit `[HS2] …` (explicit paths, `git add -f`, trailer `Orchestrated-By: Muse Code`), no push.
