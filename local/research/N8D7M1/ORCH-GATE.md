# N8D7M1 orchestrator gate — PASS, Android package only

Worker commit `1da356b9` (`Orchestrated-By: opencode`) created one
isolated arm64 Android APK carrying N8D7L's default-OFF independent
selected-input oracle. No Odin install/launch, replay, device cause or
speed measurement. I read the whole report, build/source/package scripts
and JSON gates. The WSL source tree was copied from N8D7H and differs
only in the N8D7L fork backend (`84a13a80…a4645`); G43 and jniLibs are
byte-identical. The fork PSMCT32 table header SHA is
`9635a40e…5e71f7` in both trees. Pre/postbuild source gates pass; the
Android cache has shadow paraLLEl ON, the pinned external codegen/G43
paths and all five diagnostics/UI flags OFF.

| Gate check | Result |
| --- | --- |
| Build | One arm64 `assembleRelease`, 48 tasks, success in 5m31s; no repair |
| APK | 153,736,732 B; WSL/Mac SHA pair `e077bef8a7ba8aab44f46c515f79fade1ae045cc337bf7285e7b652e739758a1` |
| Native members | Exactly arm64 runner `f3de999acc9227b82a9d9fab6a4a0b5b7fb279e6205991c1b3022da781e3c1bf`, unchanged Turnip `717812c3…1ac29d`, unchanged HAL `1b49d27c…fc387`; each double-read; runner Build ID `73291620f0c62fdc01ac0b603e9e5cca3114d0a5` differs from N8D7H |
| Oracle linkage | Runner contains required N8D7F/N8D7L env/log/control strings; oracle source under Android's enabled `PS2X_HAS_PARALLEL_SHADOW` fence, no Mac-only gate |
| Independent gate | Orchestrator reran `mac_apk_gate.py` against retained APK: status pass with both APK SHA reads and all three member pairs matching WSL receipt |
| Scope/caps | Worker commit has named brief/scripts/text receipts only, no APK/binary/game data; private fork runner-dir diff vs `14b1e5cb` empty. WSL 6.94 GiB <10 GiB, Mac APK 160 MiB <500 MiB, global ssx3 144.6/200 GB. `git show --check` flags one whitespace line in the saved source patch context |

Verdict: **PASS** for source isolation and Android package contents. This
does not show that the oracle runs or that the Odin selected snapshot is
sparse/broad. Next N step: one installed Odin run with the new APK,
aligned tick2050 input/circuit/stage/oracle vectors, eight controls and
same-run frame, under the existing battery/lockscreen/lease rules.
