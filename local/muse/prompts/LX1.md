# LX1 — bradflix as a Linux correctness/build host: setup + det-hash parity with the Mac (muse, 3 h)

## Why
The mini runs every lane's builds and boots (load 60–128 on 09-25), which starves speed measurements. bradflix (`ssh bradflix`, Ubuntu 24.04, 20 cores, 62 GB, Intel Arrow Lake iGPU with Mesa ANV, ~1 TB free, idle) could take correctness work (det-hash boots, frame dumps, counters, suites, builds) if a Linux x86 build is **guest-identical** to the Mac arm64 build.

## Facts
- Fork `https://github.com/brad-richardson/PS2Recomp.git` branch `ssx3` (clone it; current tip per `git ls-remote`), paraLLEl-GS fork `https://github.com/brad-richardson/parallel-gs.git` `ssx3` (`19d93b2`, Granite submodule `166ba21a`). Canonical codegen lives only on the mini (`~/dev/ssx3-work/codegen-ssx3`, 9,457 files, `register_functions.cpp` `8ea8ed43…`): copy it with `tar | ssh` and verify SHAs both sides (never into git). Game inputs: ISO + ELF from `~/dev/ssx3-work/E32-inputs/` (SHAs `3c2f8eb1…`, `1b49d05c…`) — Brad's own copies, allowed on his machines; put them under `~/dev/ssx3-work/` on bradflix, **never `/tmp`** (wiped on reboot).
- Mac recipe and boot driver: `local/research/F2/REPORT.md` (build flags) and `local/research/F2/f2_boot.py`. Deterministic mode + det-hash: `PS2X_DETERMINISTIC=1`, build with `PS2X_ENABLE_DET_HASH_TAP=ON`. GB8 proved det-hash is backend-independent (CPU GS = paraLLEl), so the **CPU GS backend** is fine for parity.
- Known cross-arch risks (facts.md): FP model `-ffp-contract=off`; sse2neon on arm64 vs native SSE on x86 (approximate rsqrt/rcp could differ); `long double` differs; VU1 uses `double`.

## Steps
1. Install/confirm deps on bradflix (`sudo` only if already passwordless; otherwise list what's missing and stop): clang/llvm, cmake, ninja, X11/GL dev libs for raylib, `xvfb` for a headless display, Vulkan loader + Mesa ANV (`vulkaninfo --summary`).
2. Build Release (logs/taps off, det-hash tap on), CPU GS (and paraLLEl only if ANV works under Xvfb; don't sink time into it). Suite from the worktree root: count vs the Mac's (612+).
3. Headless boot under `xvfb-run`: I26-FAST, empty mc0, `PS2X_SKIP_MOVIE=1`, `PS2X_DETERMINISTIC=1`, `PS2X_SOUND` unset (AU10: sound-off is guest-identical), to t2400 with frames at ~1090/2100.
4. **Parity:** compare its `[det-hash:v1]` lines with a Mac det boot on the **same fork commit** (run one on the mini with one slot if no matching Mac run exists; F2's B2 is `96e9f45` sound-off). Report equal lines / first differing tick + field (rdram/vu/scratch). If they differ, find the first differing tick and stop (Part 2 would chase the host-arch difference).
5. Wrap it: `local/tooling/remote/bradflix_boot.sh` (build + boot by fork SHA, pulls result.json + det-hash lines + frames back to the mini's scratch) with a usage block.
Rules: text only in git; nothing under bradflix `/tmp`; never push the fork; no Mac lease needed for bradflix boots (it has its own: one heavy job at a time until we know its headroom). Deliverable `local/research/LX1/REPORT.md` (deps, build receipts + SHAs, suite, parity table, wall times, gaps) + the script; commit `[LX1] …` (`git add -f`, `Orchestrated-By: Muse Code`), no push.
