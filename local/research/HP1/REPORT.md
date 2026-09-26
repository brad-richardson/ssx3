# HP1 — two hot-path fixes on Android: dev-trace string formatting and emulated TLS

The local-Qwen worker stopped correctly on a permission denial (edits outside its workspace; the brief
didn't grant the fork worktree — orchestrator's error, runbook updated). The orchestrator made the two
edits itself.

| Item | Value |
| --- | --- |
| Fork commits (branch `hp1` from `173b31f`, pushed to fork `ssx3`) | `da7c1a7` [HP1] VIF1: skip E37 string formatting when the entry trace is off; `554fbd9` [HP1] Android: minSdk 29 for native ELF TLS |
| Diff | `ps2_vif1_interpreter.cpp` +12/−6 (MSCAL, MPG, UNPACK blocks guarded by `ps2_vu1_entry_trace::enabled()`; `noteMscalEntry` stays unconditional); `android/app/build.gradle` `minSdk 28` → `29` (only occurrence; no `ANDROID_PLATFORM`) |
| Runner-dir check | empty |
| Mac det build | `mac_build.sh … --det`, runner `fa3a8d66…` |
| Suite (worktree root) | 668/668 |
| Det boot (mini slot 1, FR1-R1, t2400) vs `a3efbfe-det-fr1r1-t2400-snd1-1x-a5f2f32d` | hash IDENTICAL 1..2400; snd: 47 common tick lines identical (see tool fix) → IDENTICAL |
| Android compile / Odin effect | in F6's Android build and Odin runs |

Tool fix found here: `baseline.py compare` compared only the **last** snd tick line, which depends on
when the host stops the runner (this run stopped at 2410 vs the base's 2405 → a false DIFFER). It now
compares every tick line both runs printed (host noise stripped) and requires the common prefix to
cover all but the last two base lines; a one-line corruption in the middle is caught (negative test).
