# GB4 report — GS stream replay queue gate

Work resumed under the orchestrator's clarified write scope. Part 1 stopped at the first direct-replay/live comparison failure, as required by the brief. No queue replay or Part 2 run was started.

## Pins and receipts

| Item | Result |
|---|---|
| Fork source | `~/dev/PS2Recomp` at `eac6cba` (`ssx3`), clean before setup |
| GB4 worktree | `~/dev/ssx3-work/GB4/PS2Recomp`, branch `gb4-replay`, based on `574354a` |
| Existing GB3 worktree | Left untouched; it was at `94ea49a`, so GB4 was created as a separate worktree directly from the required `574354a` base |
| Configure | `cmake -S PS2Recomp -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DPS2X_GAME_CODEGEN_DIR=$HOME/dev/ssx3-work/codegen-ssx3 -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF` from `~/dev/ssx3-work/GB4`; pass |
| Build | `nice -n 10 cmake --build build -j8`; full build pass, then incremental pass after adding native upload capture and forced unchanged-value priv-store capture. First full attempt had undeclared capture symbols in `gs_frontend.cpp`; one include fix resolved them. |
| Suite | `../build/ps2xTest/ps2x_tests` from the fork worktree; **607/607**, final log `~/dev/ssx3-work/GB4/suite-final.log` |
| Capture-boot runner SHA-256 (two reads) | `743959b09f40a6dbea734633a421726434b483b60256ffdee28cd60ea2b9fdf7` / same |
| Final replay runner SHA-256 (two reads) | `1f7361d0c0cd56d4927ef37773042078fe6b09e53d7315274b1ae3a1a2a4510b` / same |
| ISO SHA-256 (two reads) | `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5` / same |
| Initial disk budget | `disk_budget.sh`: 80.4/200 GB before configure; 90.6/200 GB after boot; 151 GiB free. GB4 tree stayed under its 12 GB cap. |

## Capture

| Boot | Result |
|---|---|
| Command | `python3 gb4_boot.py --label gb4cap --wall 540 --snap 10 --script "$ROUTE" --vq --vq-from 100 --vq-to 8300 --vq-step 50 --vq-dump --pklog --capture-file "$HOME/dev/ssx3-work/GB4/run/gb4cap.capture.bin"`; `ROUTE=10350:start:2500,20650:cross:2000,23200:cross:400,24000:cross:400,30890:cross:1700,39560:cross:1750,47240:down:4200,55450:cross:1800,64920:cross:2000,113340:cross:800,118270:cross:700,122510:cross:700,113340:down:20000` |
| Env | Queue unset/off; `PS2X_PAD_SCRIPT_CLOCK=vsync`; `PS2X_SKIP_MOVIE=1`; VQ + pklog; capture path set |
| Lease | Slot 1, label `gb4cap`; released by wrapper. Slot 2 remained free. |
| Wall / exit | 540.616 s, wrapper `bound=wall`, runner `rc=0` |
| Reached | At least tick 12,071 (`[frame:dump]`); VQ samples through tick 8,300, beyond the race-load entry near tick 4,056 |
| Capture | `~/dev/ssx3-work/GB4/run/gb4cap.capture.bin`, 5,093,324,283 bytes (4.7 GiB); zstd copy 1.3 GiB. Header `PS2XGSC1`; parser reached EOF cleanly. Record counts: 3,725,840 GIF packets, 15,336 priv events, 49,699 transfer metadata events, 12,128 VBlank markers; final marker tick 12,128. No native-upload records or cap error in this file. |
| pklog | 2,000,001 lines, 107,288,527 bytes (the existing 2M line cap); VQ and frame dumps are present. |

## Implementation in `gb4-replay`

- Added an env-gated, length-prefixed binary capture (`PS2X_GS_CAPTURE`): GIF packet path+bytes, observed privileged-register changes plus guest stores even when the value is unchanged, transfer metadata, native upload payloads, and VBlank markers. The uncompressed writer stops and logs at 6 GiB; it flushes at VBlank. Unset path avoids packet copies/file locking.
- Added `PS2GSReplay` case in `ps2x_tests`. It streams packet/priv/native-upload events into direct or queued GS and prints VRAM, priv-register, and Present FNV hashes every Nth tick marker (default 50). `PS2X_GS_REPLAY_EXPECT` checks against a saved direct hash table; `PS2X_GS_REPLAY_DROP_PRIV=1` supplies the negative control.

## Replay gate and remaining work

| Check | Result |
|---|---|
| Capture parses fully / exact end tick | Pass; clean EOF, final VBlank tick 12,128 (parser command and output above) |
| Direct replay | Completed: `PS2X_GS_REPLAY_CAPTURE=../run/gb4cap.capture.bin PS2X_GS_REPLAY_OUT=../run/replay-direct.hashes ../build/ps2xTest/ps2x_tests`; log `~/dev/ssx3-work/GB4/run/replay-direct.log`; 607/607 tests pass. Hashes in `~/dev/ssx3-work/GB4/run/replay-direct.hashes`. |
| Direct replay vs capture boot live VQ | **Fail at first comparable marker, tick 100.** Replay `vram=dc2e1eaa priv=57a05358`; live `[vq]` `vram=43e5391b regs=3d2c63b8`. Present hashes were emitted, but are not used here because their pixel hashing extents have not been aligned. Stop rule applied; no queue replay, negative control, or Part 2. |
| Capture completeness gaps observed | The capture boot used runner SHA `743959…`, before the final unchanged-value priv-store capture change in runner SHA `1f7361…`; therefore this capture does not contain that newly instrumented class of guest writes. Source inspection also confirms `GS::consumeLocalToHostBytes` has no capture/replay event for bytes returned to the guest. These are concrete gaps to address before a replacement capture; neither is proven to cause the tick-100 mismatch. |
| Queue replay vs direct; queue repeat | Not run: direct/live gate failed; brief requires stopping here. |
| Drop-priv negative control | Not run: direct/live gate failed; brief requires stopping here. |
| Part 2 paraLLEl | not run |
| Runner-dir check `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner` | Empty (pass) |
| Fork commits | GB4 implementation committed locally on `gb4-replay`; no push |

## Handoff

The direct replay does not reproduce the live capture boot at tick 100, so the brief's Part 1 stop rule applies. Recommended next action: orchestrator reviews the two identified capture gaps, especially capture/replay version skew, before authorizing a replacement capture and rerun. No cause is concluded from the current mismatch. The final report and fork implementation are committed with `Orchestrated-By: Codex`.
