# E54F2 — shared EE COP0 Count clock

Worker: Codex. Brief: local/muse/prompts/E54F2.md. The orchestrator decides the gate. After the first failed test, work stopped; the orchestrator authorized exactly one test-only harness repair and continuation. No push.

## Gate table

| Gate | Result | Receipt / gap |
| --- | --- | --- |
| Fork pin and oracle | fork/ssx3 and local branch base both 293fd81ade60afb56b47434297c6f2241843dfff, verified with git ls-remote. Commit title is [GB4] Part 6 isolate replay backend and probe display pages, although the brief calls it GB6. E54F1 cites pinned PCSX2 9056c0834, COP0.cpp:488–549: one tick per charged EE cycle, minimum one on same-cycle MFC0, low32 MTC0 write resets anchor, u32 wrap. | [E54F1 report](../E54F1/REPORT.md) |
| Candidate | Shared scheduler m_count and m_countCycle; executor-only readCount/writeCount through PS2Runtime. Active-context mirror updates on accounting, supplied context on reads/writes. Only Count MFC0/MTC0 emission changed. MFC0 $zero emits an explicit helper call because SET_GPR_S32 skips value evaluation for register zero. Compare and Cause lines remain byte identical. | Local fork branch e54-count commit 0cab7d733179e0706b6262e6b6f0a8cd89b274b9 |
| Focused values | Initial taps-OFF suite: **579/580**, one focused case failed two assertions. After 0x1a, the test's simulated SET_GPR_S32(..., 0, readEeCount(...)) skipped the helper, so the next value was 0x1b rather than 0x1c and the idle read was 0x6b rather than 0x6c. The emitter already generated an explicit helper call for $zero. The orchestrator authorized one test-only repair: replace that simulation line with (void)runtime.readEeCount(&first), retain the zero-register invariant assertion, rebuild only ps2x_tests and rerun OFF. **580/580** then passed. Other checked values: cycle 100=0x64; cycle 140=0x8c; write 0xfffffff0 at cycle 200 then cycle 240=0x18; same-cycle increments, context switch and 80-cycle idle-style charge. | ~/dev/ssx3-work/E54F2/{suite-off.log,build-off-test-repair.log,suite-off-repair.log}; Ps2EeCount |
| One codegen regeneration | Completed with E54F2 recompiler and retargeted E54D TOML. 9,457 files, including 9,455 .cpp. Five helper expressions at four guest PCs: 0x3f4414 twice in overlapping functions, 0x3f4e08, 0x3f4fa4, 0x3f4fc4. Four .cpp files differ from canonical E54D; all 9,457 generated files match after exactly five Count-read substitutions. No static MTC0 Count site. No dynamic-reach inference. Later $zero emitter change cannot affect these nonzero-destination sites. | ~/dev/ssx3-work/E54F2/{regen.log,generated-sites.txt,codegen/} |
| Release/Ninja taps OFF | Initial build failed on incomplete Symbol, Section and Instruction types in new test. One clear repair added ps2recomp/types.h; repair build passed. First suite 579/580 failed for the test harness cause above; authorized test-only repair build passed and final suite **580/580**, zero failed. Runs were from fork root. | ~/dev/ssx3-work/E54F2/{cmake-off.log,build-off.log,build-off-repair.log,suite-off.log,build-off-test-repair.log,suite-off-repair.log} |
| Release/Ninja taps ON | One configure/build with E54F2 codegen, **675/675**, zero failed. Run from fork root. | ~/dev/ssx3-work/E54F2/{cmake-on.log,build-on.log,suite-on.log} |
| I26-FAST diagnostic CPU boot | One mini lease, slot 1; PS2X_SKIP_MOVIE=1 dev-only; no GPU opt-in, no packet log; OFF runner with diagnostic frame capture. Wall cap 500 s, elapsed 106.925 s, own PID 33180, bound=target, rc=0, last tick 2079 (target ≥2050). Lease released by harness. Boot log 10,735 B, no PK log; total run dir 1.8 MiB. Functional regression only. | ~/dev/ssx3-work/E54F2/run/count-one/{result.json,boot.log} |
| Three frames | Viewed Select Character tick 830 (Zoe), race tick 1810 (HUD 00:00:01, 0%), race tick 2050 (HUD 00:00:05, 1%). The known dark GS region persists. Matching two-read frame SHAs below. No proof Count sites ran. | ~/dev/ssx3-work/E54F2/run/count-one/{sc-tick830.png,race_early-tick1810.png,race_late-tick2050.png} |
| Runner-dir check; fork commit | git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner was empty after commit. Only allowed fork source/tests committed as [E54F2] Share EE COP0 Count clock, 0cab7d733179e0706b6262e6b6f0a8cd89b274b9, trailer Orchestrated-By: Codex. Clean local branch; no push. | Local fork e54-count |

## Input SHA pairs and budgets

| Input | SHA-256 read 1 | SHA-256 read 2 |
| --- | --- | --- |
| Stock ELF at ~/dev/ssx3-work/E32-inputs/cd/SLUS_207.72 | 1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc | Same |
| Stock ISO at ~/dev/ssx3-work/E32-inputs/SSX 3 (USA).iso | 3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5 | Same |
| E54F2 generated register_functions.cpp | 8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3 | Same |
| E54F2 taps-OFF ps2EntryRunner | f2e47c98301a61da21f5403b46f7042f8b9cec8d53e662706631b6433bf697c0 | Same |
| SC frame tick 830 | 43ff22a5f005e629a22ea6d8196dc8f79245ea3587713ccd6955e5905e0a65f3 | Same |
| Race frame tick 1810 | e9f450a798ed708cac08d2a3b85f3d8c01a9f528a569efe3bad9aac044078651 | Same |
| Race frame tick 2050 | c5f8892142c76e63facfdef3bea37e208d5274e14170c42c74a2a0f8a778003c | Same |

Pair receipts: ~/dev/ssx3-work/E54F2/{input-sha.txt,gate-sha.txt,frame-sha.txt}. Global internal usage after boot was 112.1/200 GB, with 130 GiB free. E54F2 was 977 MiB, under 9 GiB. Boot log 10,735 B under 32 MiB; run dir including frames 1.8 MiB under 25 MiB. One regeneration, one initial OFF build, one clear compile repair, one orchestrator-authorized test-only repair build, one ON build and one boot. No tuning loop.

## Exact commands and gaps

Commands ran from ~/dev/ssx3 unless another workdir is shown:

    git ls-remote fork refs/heads/ssx3
    git worktree add -b e54-count ~/dev/ssx3-work/E54F2/PS2Recomp 293fd81ade60afb56b47434297c6f2241843dfff
    local/tooling/disk_budget.sh
    ./build.sh baseline
    shasum -a 256 '/Users/brad/dev/ssx3-work/E32-inputs/cd/SLUS_207.72' '/Users/brad/dev/ssx3-work/E32-inputs/cd/SLUS_207.72' '/Users/brad/dev/ssx3-work/E32-inputs/SSX 3 (USA).iso' '/Users/brad/dev/ssx3-work/E32-inputs/SSX 3 (USA).iso' | tee input-sha.txt
    ~/dev/ssx3-work/E54F2/build-baseline/ps2xRecomp/ps2_recomp ~/dev/ssx3-work/E54F2/ssx3-e54f2.toml > ~/dev/ssx3-work/E54F2/regen.log 2>&1
    ./build.sh off
    nice -n 10 cmake --build ~/dev/ssx3-work/E54F2/build --parallel 8 --target ps2x_tests ps2EntryRunner > ~/dev/ssx3-work/E54F2/build-off-repair.log 2>&1
    ~/dev/ssx3-work/E54F2/build/ps2xTest/ps2x_tests > ~/dev/ssx3-work/E54F2/suite-off.log 2>&1
    nice -n 10 cmake --build ~/dev/ssx3-work/E54F2/build --parallel 8 --target ps2x_tests > ~/dev/ssx3-work/E54F2/build-off-test-repair.log 2>&1
    ~/dev/ssx3-work/E54F2/build/ps2xTest/ps2x_tests > ~/dev/ssx3-work/E54F2/suite-off-repair.log 2>&1
    ./build.sh on
    ~/dev/ssx3-work/E54F2/build-taps/ps2xTest/ps2x_tests > ~/dev/ssx3-work/E54F2/suite-on.log 2>&1
    shasum -a 256 codegen/register_functions.cpp codegen/register_functions.cpp build/ps2xRuntime/ps2EntryRunner build/ps2xRuntime/ps2EntryRunner | tee gate-sha.txt
    python3 e54f2_boot.py --label count-one --capture --target 2050 --wall 500
    shasum -a 256 run/count-one/sc-tick830.png run/count-one/sc-tick830.png run/count-one/race_early-tick1810.png run/count-one/race_early-tick1810.png run/count-one/race_late-tick2050.png run/count-one/race_late-tick2050.png | tee frame-sha.txt
    git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner
    git commit -m '[E54F2] Share EE COP0 Count clock' -m 'Clock Count from the EE scheduler with write epochs and same-cycle read increments. Emit runtime Count helpers and cover values, context switches, wrap and neighboring COP0 emissions.' -m 'Orchestrated-By: Codex'

git ls-remote and worktree add ran from ~/dev/PS2Recomp; build, regeneration, hashes and boot from ~/dev/ssx3-work/E54F2; suites, runner check and commit from ~/dev/ssx3-work/E54F2/PS2Recomp. Read-only source checks used rg, sed, git diff and Python byte comparisons. No dynamic Count-site receipt exists. The synthetic scheduler charges 32 cycles on back edges, 8 on dispatch and can fast-forward while idle; these values are not exact hardware timing. Compare interrupt timing, Compare writes, Cause and Status were outside this candidate.
