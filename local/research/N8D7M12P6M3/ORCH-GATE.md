# N8D7M12 Part 6M3 orchestrator gate — source collector A (2026-09-24)

Read the complete worker REPORT, 16-row check result, source/checker diff and commit `238be17a`; `git show --check` is clean. The code prunes excluded directory names before `os.walk` descent and excludes matching file names from the pre/post listing. It retains the existing scan rule, sorted order and no-follow symlink behavior. The 16/16 fixture includes the exact excluded-cache race that failed P6M2, plus an included-file mutation that still fails. I independently reran `verify` on the bounded 41-file, 188,488-byte real-source sample; aggregate matched `029bec991f9e32b962ed84267e52205ffd485d01cb32f2fdd89cf51305fdf83e` with no added/missing/changed paths.

**A for use as a source-byte collector in a bounded full-root package preflight.** This establishes neither compiled inputs nor provenance of the old APK. The next package must separately pin build inputs, flags, native member/Build ID, Turnip/HAL and final APK, and verify the source manifest after transfer. Full fork/codegen scan cost remains unmeasured; set explicit file/byte/time caps. No package, device, GPU or speed verdict here.

## Correction, same day

Before full-root use, the orchestrator found the private fork contains upstream-tracked `ps2xRuntime/src/runner/register_functions.cpp` (438 B, SHA-256 `cf62c485072f07c230e60296b77afd733f130f587955fe608322939ebb87f068`), identical to `14b1e5cb` and HEAD. The collector currently rejects every runner path, so the prior full-root readiness statement is **withdrawn**. P6M3 remains A for the exclusion fix and bounded sample only. P6M4 must accept only that exact upstream stub and still reject generated/changed runner bytes before full-root use.
