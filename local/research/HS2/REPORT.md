# HS2 — `bradflix_build.sh` safe with several lanes at once

Worker: Muse Code, brief `local/muse/prompts/HS2.md`, 2026-09-26. Tables and receipts;
the orchestrator decides. No push. Stopped per the brief's stop rule after the first
failure (acceptance 1's `173b31f` leg, a premise failure, not an HS2 failure).

## Headline

- The rewritten script works: the tip build compiled green (`BUILD_RC=0`, runner
  `aeb75690…`, 641 s wall), and the concurrent pair exercised every new mechanism —
  atomic name claim, per-build `git archive` export, content-addressed publish vs
  discard-under-lock, serialized docker build. Both builds' `src/` trees verified
  byte-equal to their SHAs.
- **Acceptance 1's `173b31f` leg cannot pass with canonical inputs under any script
  version:** `173b31f` (2026-09-25) predates `PS2X_VU1_NOINLINE` (VR2-2D `d585e5c`,
  2026-09-26), which the canonical vu1gen images require. 40/40 errors are this one
  unknown type name, all in `vu1_*.cpp`. Receipt: `build-173-error.txt`.
- Acceptances 2–4 not run (stop rule). The script is committed and ready; the remaining
  validation is ~2 builds + 1 boot once a buildable second SHA is named.

## Design (what changed in `local/tooling/build/bradflix_build.sh`)

- Fork source per build: `git -C ~/dev/PS2Recomp archive <sha>` on the mini, untarred into
  `~/dev/ssx3-work/HS1/<name>/src` on bradflix; full SHA recorded in `<name>/fork-sha.txt`
  and `CMakeLists.txt` presence asserted. No `git fetch/checkout` on any shared clone.
  Unpushed local commits build (they resolve in the mini clone).
- Inputs by content, never overwritten: `codegen-<sha12 of register_functions.cpp>`,
  `vu1gen-<sha12 of the `sha256sum vu1_*.cpp` manifest>`, `pgs-<pin12>`. Each is staged
  privately, SHA/pin-verified, then published with one atomic `mv` under the lock; if the
  dir already exists it is re-verified and used (a concurrent loser discards its stage).
  If a same-named dir exists with wrong content the script fails loudly. There is no
  `rm -rf` of any shared dir anywhere in the script.
- One lock `~/dev/ssx3-work/HS1/.setup.lock` (`flock -w`): build-name claim (`mkdir`, fails
  if reused), each shared-input publish, and the docker build. Slow transfers (274 MB
  codegen tar, pgs clone) happen in lane-private stage dirs *outside* the lock; the lock
  is held only for re-verify + `mv`. Released before cmake configure/compile.
- CLI `<fork-sha> <build-name> [--det]` unchanged, plus `--vu1 DIR`, `--codegen DIR`
  (content dirs derive from the override's hashes, so overrides stay content-addressed)
  and `--pgs-pin SHA` (full 40-hex; still expects the 29-submodule tree).
- Docker image, ccache mount and cmake flags byte-identical to HS1: same image
  (`d124af4da093` in both builds here), same `-D` set; only `-S`/`-B`
  (`/work/<name>/src`, `/work/<name>`) and the three input `-D…_DIR` paths changed.
- ELF/ISO keep their fixed `inputs/` names (boots reference them) but are published
  atomically (stage → verify → `mv`) instead of overwritten in place.
- The Dockerfile is staged per build (`.stage-<name>-Dockerfile`) and passed with
  `docker build -f`; the fixed `Dockerfile.bradflix` is never written. VU0 images are
  not wired, exactly as before (tip builds with an empty VU0 dir = interpreter, as the
  old script would; VR3 used its own variant).

## Acceptance

| # | Check | Result | Receipt |
| --- | --- | --- | --- |
| 1 | tip + `173b31f` builds 10 s apart both succeed; each `src/` matches its SHA | **BLOCKED (premise).** Setups both green concurrently; tip compiled; `173b31f` fails on `PS2X_VU1_NOINLINE` (needs rev ≥ `d585e5c`). Src isolation verified (below) | `build-tip.log`, `build-173.log`, `build-173-error.txt` |
| 2 | unpushed local commit builds | NOT RUN (stop rule) | — |
| 3 | tip rebuild byte-identical + ccache hits | NOT RUN (stop rule) | — |
| 4 | det boot of tip runner vs `a3efbfe-det-fr1r1-t2400-snd1-1x-a5f2f32d` IDENTICAL | NOT RUN (stop rule) | — |

Src isolation (concurrent exports, `ps2xRuntime/CMakeLists.txt`, present with different
content at both revs):

| Build | `git show <sha>:…` (mini) | Exported `src/` (bradflix) | Match |
| --- | --- | --- | --- |
| hs2-tip-det (`5d5c382…`) | `a795a64acb693a65…` | `a795a64acb693a65…` | yes |
| hs2-173b31f-det (`173b31f…`) | `81cb7b287fbe0f42…` | `81cb7b287fbe0f42…` | yes |

(`fork-sha.txt` in each build dir records the full SHA. Note: `ps2_mtvu.h` was briefly
used as the check file but does not exist at `173b31f` — added later — so the check was
redone with `CMakeLists.txt`.)

Concurrency evidence (build 2 started 10 s after build 1):

| Mechanism | Observed |
| --- | --- |
| Atomic claim | both `flock … mkdir` claims succeeded for distinct names |
| Per-build export | both `EXPORT_OK`, contents verified per-SHA above |
| Publish race (pgs) | tip `published pgs-1b3a2948cc55`; 173 `already published; discarding stage` |
| Shared reuse | 173 found `codegen-8ea8ed436b78 OK`, `vu1gen-d28e3fc6467f OK` (tip published first) |
| Serialized docker | both report `image: ssx3-hs1 d124af4da093` |
| Shared dirs untouched | `HS1/PS2Recomp` still `cdaa331` clean, `parallel-gs` still `1b3a2948…` |

## Builds (2 of ≤ 6 used; 0 of 1 boot)

| Build | Fork SHA | det | Result | Runner SHA (two reads match) | Wall (cfg+build) |
| --- | --- | --- | --- | --- | --- |
| hs2-tip-det | `5d5c38211c6c13e5c6fcecf9df8f051469a49445` (fork `ssx3` tip after `git fetch fork ssx3`) | ON | `BUILD_RC=0` | `aeb75690fced33f5410e738b1159dce221dc0ebb1ecfc5990c4bba57bbb0894d`, 192,245,440 B | 641 s |
| hs2-173b31f-det | `173b31f4884ea3abd05242629728ae3eb2980b87` | ON | `BUILD_RC=1`, 40× `unknown type name 'PS2X_VU1_NOINLINE'` in `vu1_*.cpp`, no other errors | — | 77 s |

Tip ccache: 9473/15235 hits before → 9736/16060 after. Published shared dirs:
`codegen-8ea8ed436b78`, `vu1gen-d28e3fc6467f` (manifest `d28e3fc6…` == old shared `vu1gen`,
so the old script fails `173b31f` identically), `pgs-1b3a2948cc55` (29/29 submodules).

## Recommended next action

Re-brief the remaining validation with a buildable second SHA: any rev ≥ `d585e5c` that
differs from the tip in at least one file (e.g. the tip's parent, or re-fetch `fork/ssx3`
at run time). Then: (1) concurrent tip + second-SHA pair (or accept the isolation proof
above and run them for the green pair), (2) unpushed-commit build (suggested: throwaway
worktree off the tip so the E checkout is never touched — `git worktree add --detach`,
commit, archive, `worktree remove`), (3) tip rebuild for byte-identical + ccache hits,
(4) the det boot vs `a3efbfe-det-fr1r1-t2400-snd1-1x-a5f2f32d`. Budget left: 4 builds, 1 boot.

## Old shared dirs (left in place; clean up later, after no lane uses the old script)

- `~/dev/ssx3-work/HS1/PS2Recomp` (at `cdaa331`, TM1-era; old script's shared checkout)
- `~/dev/ssx3-work/HS1/codegen`, `~/dev/ssx3-work/HS1/vu1gen` (old shared inputs)
- `~/dev/ssx3-work/HS1/parallel-gs` (old shared paraLLEl)
- `~/dev/ssx3-work/HS1/Dockerfile.bradflix` (stale fixed-name copy; new script stages per build)
- Lane-private clones (`PS2Recomp-mt1`, `PS2Recomp-vr2`, `PS2Recomp-vr3`, `vu1gen-*` variants)
  belong to their lanes; not HS2's to remove. Also not removed: this lane's `hs2-tip-det`
  (green, reusable for acceptance 4), `hs2-173b31f-det` (failed, evidence), and any
  `.stage-*` leftovers (none expected — both builds cleaned their stages).

## Proposed runbook text (for the orchestrator; workers don't edit `docs/`)

- Build: `local/tooling/build/bradflix_build.sh <fork-sha> <build-name> [--det]
  [--vu1 DIR] [--codegen DIR] [--pgs-pin SHA]`. The SHA may be unpushed but must exist
  in the mini's `~/dev/PS2Recomp` (`git fetch fork ssx3` first for fresh pushed tips).
- Concurrent builds are safe: shared inputs are content-addressed and immutable, setup
  serializes on `HS1/.setup.lock`, compiles run free. Mixed old/new-script concurrency
  is safe for the new script's builds (they never read the shared checkout/inputs).
- On a failed build, `rm -rf` only your own `<name>` dir, `<name>-*.log`, and
  `.stage-<name>-*` / `.pgs-stage-<name>` leftovers. Never remove a shared
  `codegen-*` / `vu1gen-*` / `pgs-*` dir (the script itself never does).
- Build dirs record provenance: `<name>/fork-sha.txt` plus the final `runner: …`
  line (`fork=`, `src=`, `codegen=`, `vu1=`, `pgs=`).

## Gaps / follow-ups

- Acceptances 2–4 unrun (above) — done in Part 2 below.
- `docker build` still sends all of `HS1/` as context (unchanged from HS1; a
  `.dockerignore` would shrink it without changing the image since the Dockerfile copies
  nothing — possible follow-up, out of scope).
- macOS→GNU tar `LIBARCHIVE.xattr.com.apple.provenance` warnings in the log are cosmetic
  (same as the old script).
- Full old-script-lane immunity note: an old-script lane's non-atomic `Dockerfile`/input
  writes could only collide with a same-instant reader in a microsecond window, and any
  hit fails loudly (parse/SHA error), never silently.

## Part 2 (worker, 2026-09-26)

Script change since Part 1: `--vu0 DIR` (default `~/dev/ssx3-work/vu0gen-ssx3`),
content-addressed exactly like vu1gen (`vu0gen-<manifest12>`, here `vu0gen-17f64123313c`
for the 1-image set), passed as `PS2X_VU0_RECOMP_DIR`. Always published like the other
inputs; a no-op for revs before VR3 (unused `-D`). All Part 2 builds carry VU0 images,
so the Part 2 tip runner (`fdfcf7cc…`) differs from the Part 1 one (`aeb75690…`, no VU0)
by design.

### Acceptance

| # | Check | Result | Receipt |
| --- | --- | --- | --- |
| P2-1 | `5d5c382` + `a5e5940` builds 10 s apart both succeed; each `src/` matches its SHA | **PASS.** Both `BUILD_RC=0`. `ps2_vu1_recomp.cpp`: tip blob `52f95cf84d80aa4a…` == tip export, a5e blob `2ef555a406e8c360…` == a5e export, and they differ | `build-p2-tip.log`, `build-p2-a5e.log` |
| P2-2 | unpushed local commit builds (throwaway `76fe7a9`, comment-only on tip; worktree removed after, E checkout untouched) | **PASS.** `BUILD_RC=0`; runner byte-identical to the tip runner (comment-only change) | `build-p2-unpushed.log` |
| P2-3 | tip rebuild byte-identical + ccache hits | **PASS.** `hs2p2-tip-det2` sha `fdfcf7cc…` == `hs2p2-tip-det`; ccache misses 6699 → 6699 (all hits), 51 s wall | `build-p2-tip2.log` |
| P2-4a | plain det boot of tip runner vs `a3efbfe-det-fr1r1-t2400-snd1-1x-a5f2f32d` | **IDENTICAL** (hash 1..2400, snd/coverage) | `boot-p2-det.log`, `check-p2-det.txt` |
| P2-4b | det boot with `PS2X_VU0_RECOMP=1 PS2X_VU0_DIRECT=1` vs same key | **IDENTICAL**; VU0 path confirmed live (`[vu0-recomp] generated_share=1.0000`, `interpreted_cycles=0`) | `boot-p2-det-vu0.log`, `check-p2-det-vu0.txt` |

### Builds (4 of ≤ 5 used; 2 of ≤ 3 boots)

| Build | Fork SHA | det | Result | Runner SHA (two reads match) | Wall |
| --- | --- | --- | --- | --- | --- |
| hs2p2-tip-det | `5d5c382…` | ON | `BUILD_RC=0` | `fdfcf7cccebbc769e18f5ba57d5c3dad6377596631cf76986458b5790c7f98d7`, 193,407,864 B | 69 s |
| hs2p2-a5e5940-det | `a5e5940612e4dfdcaa98a6d1c49f6c221abf41c5` | ON | `BUILD_RC=0` | `7cb41f0d8eda21ba4fff95543d272687be2b121492c50357b0f47654157d7f1a`, 192,230,024 B | 617 s |
| hs2p2-unpushed-det | `76fe7a981b6177368267353ca3b0df733de62927` (throwaway, unpushed) | ON | `BUILD_RC=0` | `fdfcf7cc…` (== tip) | 51 s |
| hs2p2-tip-det2 | `5d5c382…` | ON | `BUILD_RC=0` | `fdfcf7cc…` (== tip) | 51 s |

Both boots used `hs2p2-tip-det2`'s runner (`--route fr1r1 --stack-kb 512 --vu1-stats`,
sound on, stop tick 2400). Note: `ssx3_boot.py`'s `fork_sha` field reports the stale
shared-checkout SHA (`cdaa331`), not the built runner's — cosmetic metadata, the runner
path and hashes are what matter.

### Runbook addition (amends the Part 1 text)

- VU0 images are a standard input now: `vu0gen-<manifest12>` is published like vu1gen and
  always passed (`-DPS2X_VU0_RECOMP_DIR`); override with `--vu0 DIR`. Revs before VR3
  ignore it. Enable at boot with `--env PS2X_VU0_RECOMP=1 --env PS2X_VU0_DIRECT=1`.

## Orchestrator gate, Part 1 (2026-09-26)

**Pass (design + tip build + isolation proven); the 173b31f leg failed on the brief's premise** — my error:
`173b31f` predates the `PS2X_VU1_NOINLINE` marker the canonical VU1 images now need.

## Part 2 brief (orchestrator)
1. Acceptance 1 again with two buildable SHAs started 10 s apart: fork `ssx3` `5d5c382` and `a5e5940`
   (differs by VR3's VU0 commits; check a file that differs, e.g. `ps2xRuntime/CMakeLists.txt` or the VU0 recomp file).
2. Acceptances 2–4 as briefed (unpushed throwaway commit; byte-identical rebuild + ccache hits; det boot of the tip
   runner vs `a3efbfe-det-fr1r1-t2400-snd1-1x-a5f2f32d` IDENTICAL).
3. Add `--vu0 DIR` (content-addressed `vu0gen-<sha12>` like vu1gen; default `~/dev/ssx3-work/vu0gen-ssx3`) passing
   `PS2X_VU0_RECOMP_DIR`, since the fork now has VU0 images; one det boot with `--env PS2X_VU0_RECOMP=1 --env
   PS2X_VU0_DIRECT=1` IDENTICAL.
Budget: ≤ 5 builds, ≤ 3 boots. Proposed runbook text in the report. Stop after.

## Orchestrator gate, Part 2 (2026-09-26) — adopted, lane closed

**Pass.** Concurrent pair, unpushed commit, byte-identical rebuild with 100 % ccache hits, and two det boots
IDENTICAL (VU0 off and on). The shared-dir race and `rm -rf` are gone. Follow-ups queued: `ssx3_boot.py`'s
`fork_sha` field reports the shared checkout, not the runner's source (cosmetic); clean up the retired shared
`HS1/PS2Recomp` / `HS1/parallel-gs` / `HS1/vu1gen` dirs once no lane uses them.
