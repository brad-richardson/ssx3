# N8D7L — independent full-frame selected-input oracle (VALIDATED, no push)

**State: VALIDATED. One Release/Ninja build, one flag-OFF suite (585/585),
paired OFF/ON Mac replay through tick2050 on lease slot 1 (released).
No live boot, device, or Android package. Commits below; no push.
No cause declared. The static fixture is not a compiled oracle test.**

## 1. Evidence table

| Item | Value |
| --- | --- |
| Fork worktree | `/Users/brad/dev/ssx3-work/N8D7L/PS2Recomp`, branch `n8d7l-oracle`, base `0678dd96e496a65bbb09af5467f17240ae2bbdc8`; one file, +138 lines |
| Oracle header | `ps2_gs_psmct32.h` SHA `9635a40e11bae56189b64d1d9660fb68d0375444d355db43246973adb95e71f7` |
| Backend SHAs | pre `c6135b3ce986504ada7826a56f7a3d411a76690f9ca7dd80d918a3666d4fb41f` (= N8D7F), post `84a13a80686be8d4ed17750a9399d298ea6b998b98f48d3720b6b5bc839a4645` |
| Independence | zero `swizzle_PS2` in worktree `ps2xRuntime/`; oracle calls only `GSPSMCT32::addrPSMCT32` |
| Fixture (static) | `oracle-fixture-check.py` — **13/13 PASS** (`fixture-check.log`); literals only |
| Syntax | `clang++ -fsyntax-only`, exact N8D7F TU flags, exit 0, no warnings (`syntax-check.log`, 0 B) |
| Configure | exit 0, 98 s (`cmake.log` tail); N8D7F flags, `-B …/N8D7L/build`, G43 = N8D7F private copy (read-only) |
| Build | exit 0, 322 targets, no errors (`build.log`); one attempt, no repair needed |
| Binary | `build/ps2xTest/ps2x_tests` SHA `a14e4e9bc3914cb89c9e596292e6aa48890063d8d3706f77cef758531c751533` ×2 |
| Suite (flags OFF) | exit 0, **585/585** (`suite.log`) |
| OFF replay | exit 0, `off.hashes` SHA `f038cde9…`, zero `[n8d7l]` lines (flag-off clean) |
| ON replay | exit 0, `on.hashes` byte-identical to OFF; tick2050 `present=7bf5c012`, pmode `ff21`, fbp112, status 2 |
| Oracle vector (ON) | `tiles=448 occupied=64374 active=300 packed_sha256=e1dc4c5c…` — identical SHA to input/circuit/stage |
| Equality | `input_circuit_equal=448/448`, `oracle_input_equal=448/448` |
| Controls (ON) | 8/8 words: `0x0E0000=0x00260803,0x0E0534=0x00260802,0x0E0040=0x00260804,0x1BFFF4=0x000C0000,0x0E2000=0x00260802,0x0F0000=0xFF230401,0x0E1FFC=0x003D2B00,0x0F2000=0x00604400` |
| OTHER count | 0 in OFF, 0 in ON; `[n8d7l]` total 320 B (<16 KiB) |
| Frames | `vq-002050.ppm` 688143 B both runs, SHA `8c85489e…` identical (= N8D7F frame SHA) |
| Lease | slot 1 claimed `n8d7l`, both runs, released (both slots free) |
| Runner guard | `git diff 14b1e5cb n8d7l-oracle -- ps2xRuntime/src/runner` empty |
| Disk | receipts 180 KiB (<512 KiB); global 143.0/200 GB |

## 2. Exact commands (from `/Users/brad/dev/ssx3-work/N8D7L/PS2Recomp`)

Configure:
```sh
cmake -S /Users/brad/dev/ssx3-work/N8D7L/PS2Recomp -B /Users/brad/dev/ssx3-work/N8D7L/build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=/opt/homebrew/opt/llvm/bin/clang -DCMAKE_CXX_COMPILER=/opt/homebrew/opt/llvm/bin/clang++ -DPS2X_GAME_CODEGEN_DIR=/Users/brad/dev/ssx3-work/codegen-ssx3 -DPS2X_GS_SHADOW_PARALLEL=ON -DPS2X_PARALLEL_GS_SOURCE_DIR=/Users/brad/dev/ssx3-work/N8D7F/parallel-gs -DPS2X_ENABLE_DIAG_TAPS=OFF -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF -DGRANITE_VULKAN_SPIRV_CROSS=OFF
```
Build / suite:
```sh
nice -n 10 cmake --build /Users/brad/dev/ssx3-work/N8D7L/build --target ps2x_tests -j 6
/Users/brad/dev/ssx3-work/N8D7L/build/ps2xTest/ps2x_tests
```
OFF replay:
```sh
env PS2X_N8D7F_SELECTED_CAPTURE=0 PS2X_N8D7L_ORACLE=0 PS2X_N8D5_TILE_CAPTURE=1 PS2X_GS_REPLAY_CAPTURE=/Users/brad/dev/ssx3-work/N8D4/n8d4.gs PS2X_GS_REPLAY_STEP=50 PS2X_GS_REPLAY_OUT=/Users/brad/dev/ssx3-work/N8D7L/off.hashes PS2X_GS_REPLAY_BACKEND=parallel PS2X_GS_REPLAY_PPM_DIR=/Users/brad/dev/ssx3-work/N8D7L/off-ppm PS2X_GS_REPLAY_PPM_TICKS=2050 GRANITE_VULKAN_LIBRARY=/opt/homebrew/lib/libvulkan.1.dylib /Users/brad/dev/ssx3-work/N8D7L/build/ps2xTest/ps2x_tests
```
ON replay: same with `PS2X_N8D7F_SELECTED_CAPTURE=1 PS2X_N8D7L_ORACLE=1`, `on.hashes`, `on-ppm`.
Full 4.8 MB logs stay in `ssx3-work/N8D7L/` (scratch); receipts hold
`replay-excerpt.txt` (vectors/controls/frames) + `run-receipt.json` (pins).

## 3. Correct-behavior reading (no verdict)

On the pinned N8D4 Mac stream at tick2050 the fork-table oracle reproduces
the G43 input vector exactly (448/448, shared SHA): no conversion/address
mismatch on this frame, and the selected raw snapshot is broad here
(300/448 active), consistent with the N8D7G Mac calibration. This says
nothing about why the Odin snapshot is sparse or about Mac/Odin stream
equality.

## 4. Gaps

- The static fixture checks source text and literal census math; it is not
  a compiled oracle test and is not claimed as one. Compiled-oracle evidence
  is the ON replay above.
- No new compiled unit test: no device-free backend-TU fixture exists, and a
  checked-in census reimplementation would mirror the oracle.
