# NP1 — Odin race call-graph profile on the F1 build, then the cheap host-overhead fix (muse)

Review `docs/research/review-2026-09-25-fable.md` §3 rank 2 + "Brief sketch, rank 2 (NP1)". The F1 fold lifted the Odin race to 0.140× (`local/research/F1/REPORT.md` Part 2), below the review's estimate; this lane re-splits the frame and tries the cheapest host fix.

## Part 1 — profile (stop after; the orchestrator decides Part 2's scope)
- APK: F1's `c822a2b3…` (profileable: N11's manifest is folded). It is already installed as Brad's play build; install it again anyway. Driver: `local/research/F1/launch.py` / N11's (`--profile-after-tick 2400 --profile-secs 30`, **`simpleperf record --call-graph fp`** — or `dwarf` if fp unwinds are shallow; say which), full own env, `PS2X_SOUND=1`, `mc0-test` empty, Brad's env + save restored and SHA-verified after (as N11/F1).
- Symbolize on bytesize with the unstripped `.so` from `/home/brad/f1` (N11 Part 2 "Symbolization").
- Tables: the N11 per-stage ms table for the new race frame (race-only wall per frame from F1 S1/S2, 119 ms); callers of `@plt`, `__memset_aarch64_nt`, `memcpy`, `clock_gettime`, and the top kernel rows; top 25 self symbols. Compare with N11 S2 row by row.
- One launch (+1 spare). Lease, keyguard `showing=false`, AC + ≥ 20 %, thermal ≤ 2 before launch, force-stop after.
- Deliverable: `local/research/NP1/REPORT.md` Part 1; commit `[NP1] Part 1 …`. Stop.

## Part 2 (only when the orchestrator releases it)
Candidate from the review: `-Wl,-Bsymbolic` (and/or hidden visibility) on the Android `.so` link, plus replacing the GIF arbiter's `resize`+`memcpy` if the callers point there. One APK (fork branch `np1-link` from fork `ssx3` tip; no push), two clean race runs ABBA vs F1's APK, thermal ≤ 2 before each.

Rules: text only in git; never push; runner-dir check empty for any fork edit; scratch `~/dev/ssx3-work/NP1/` ≤ 5 GB; bytesize one heavy job at a time. First failure: stop, save the error, hand back. Budget Part 1: 1 h.

## Part 2 as released (orchestrator, after the Part 1 gate)
Fork branch `np1-link` from fork `ssx3` **`0ed07c4`** (no push). Up to three commits, each named in the report with before/after profile share:
1. **`-Wl,-Bsymbolic`** on the Android `.so` link (Gradle/CMake for the Android target only; cite the file).
2. **The memset in VU1/VU0 execute:** find what `VU1Interpreter::execute`/`run` (and VU0) zero on every call (`lsp` + the fp callers from Part 1); if it's a per-execute clear of a large struct/array that can be skipped or narrowed without changing results, do that. It must stay bit-exact: run E57's `local/research/E57/check.py` gate on the Mac (suite + 2,400 det-hash lines + GS digest vs `0ed07c4`) before any APK.
3. **Handoff wakeups:** only if the Part 1 callers show `notify_one`/futex per GIF packet on GameThread, batch the wakeup to once per drain/vsync; same bit-exact gate. Otherwise skip and say why.
Then one APK (F2 recipe, bytesize), two clean Odin race runs **ABBA vs F2's `a3d26b56`** (4 runs: A B B A; thermal ≤ 2 and battery ≥ 20 % before each; never toggle the screen), then reinstall **Brad's play build `a3d26b56`** + `deploy-odin.sh` at the end unless the new APK is faster by more than run-to-run spread — in that case leave F2 installed anyway; the orchestrator decides the play build. Append `## Part 2`; commit `[NP1] Part 2 …`. Budget 2 h.
