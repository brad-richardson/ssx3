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

## Part 2 — continuation

| Gate | Result | Receipt |
|---|---|---|
| Marker, live `sub`, and pklog alignment, ticks 100..8300 | **165/165 exact packet counts at the same tick; offset 0.** Of the 165 samples, 155 have pklog coverage at tick N−1 and all 155 agree with live `sub` at tick N. | `~/dev/ssx3-work/GB4/run/marker-alignment.csv`, generated by `run/align_markers.py`; first rows: tick 100 live/marker 536/536, pklog N−1/N 536/547; tick 150 1267/1267, 1267/1284; tick 200 2117/2117, 2117/2134. Capture packet byte hash/tick/length matches pklog for first 5,000 packets (`run/check_packet_prefix.py`). |
| Corrected direct replay vs live | **Fail at tick 100:** live/replay VRAM `955d391b`/`a70b668b`; regs `3d2c63b8`/same; Present `fd889dc5`/same. Across all 165 VQ samples, VRAM matches 1, regs 165, Present 3. | `~/dev/ssx3-work/GB4/run/direct-live-p2.csv`, `run/replay-direct-p2.hashes`, `run/boot-gb4cap4-1.log` |
| Queue vs direct, queue repeat, drop-priv control | Not run: direct/live gate failed. | No gate data |
| paraLLEl replay and live boot | Not run: Part 1 did not pass. | No gate data |

The original marker was after the VQ sample and FIELD flip in `EeScheduler::processEvent`, although its packet count matched VQ because no GIF packets intervened. Part 2 moves it immediately after VQ so the privileged-register sample has the same stream position. This is a within-VBlank ordering correction, not a one-tick packet shift. The original capture cannot acquire that ordering retroactively. The initial tick-100 VRAM mismatch is therefore not explained by marker timing.

The replacement runner records local-to-host bytes returned to the guest and the HLE `clearFramebufferContext` operation (a direct VRAM mutation at `sceGsSwapDBuffDc` that the original capture omitted). The replay checks returned bytes and applies each captured clear. Replay Present FNV now hashes only the visible rows, matching VQ's width and stride. The final runner's unchanged-value priv-store capture is included. Build 1 and suite passed (607/607). The replacement capture had zero clear and readback events, so those additions did not affect this gate.

### Sandboxed boot attempt, void under Brad's 2026-09-23 authorization

| Item | Receipt |
|---|---|
| Build | `nice -n 10 cmake --build build -j8 > run/build-part2-1.log 2>&1` from `~/dev/ssx3-work/GB4`: pass (12 Ninja steps). One of two allowed builds used. |
| Tests | `(cd PS2Recomp && ../build/ps2xTest/ps2x_tests > ../run/suite-part2-1.log 2>&1)`: 607/607 pass. |
| Runner SHA-256, two reads | `f2ba000f5b28a44378560e6778baef6429f96703fb945b8bdba293553639c0e4` / same. |
| ISO SHA-256, two reads | `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5` / same. |
| Route and command | E33 route from `local/research/I26/ROUTES.md`; `python3 gb4_boot.py --label gb4cap2 --wall 540 --snap 10 --script "$ROUTE" --vq --vq-from 100 --vq-to 8300 --vq-step 50 --vq-dump --pklog --capture-file "$HOME/dev/ssx3-work/GB4/run/gb4cap.capture.bin"`. Queue off, vsync pad clock, dev movie bypass. Full route string is in `run/boot-part2-wrapper.jsonl`. |
| Boot result | Slot 1 claimed and released by wrapper. `bound=wall`, 540.215 s, runner `rc=-15` from wrapper termination. Boot log remained 909 bytes, ending with macOS `com.apple.hiservices-xpcservice` connection invalid and `_LSModifyNotification` failure at graphics initialization. No pklog, VQ line, or capture file. Slot 1 and slot 2 confirmed free after the run. **Brad classified this sandboxed boot as void, outside the +1 boot budget; the replacement boot will run escalated from launch.** |
| Old capture preservation | The Part 1 raw capture was deleted to keep the lane below its 12 GB cap after its compressed copy passed `zstd -t` (expanded size 5,093,324,283 bytes). It is `run/gb4cap-part1.capture.bin.zst`. Alignment CSV and script remain in `run/`. |

The graphics-service log is the observed startup failure under the Codex sandbox; the exact reason for the connection failure is unproven. A read-only `ps -p 73903` probe returned `operation not permitted` in that sandbox; the wrapper's bounded exit and lease status provide the process and release receipt. No process inspection workaround was attempted.

Fork implementation commit: `df0c99b` (`[GB4] Part 2 capture HLE clears and readbacks`, `Orchestrated-By: Codex`).

### Escalated replacement attempt: lease refusal before launch

After Brad authorized escalation for runner boots, preflight showed both mini slots free. The escalated `gb4_boot.py --label gb4cap3` command then exited 2 before runner launch: `REFUSE: no mini slot free: {1: 'E58-part3-smoke pid=76495 utc=2026-09-24T01:47:05Z', 2: 'au3a2'}`. The wrapper receipt is `~/dev/ssx3-work/GB4/run/boot-part2-escalated-wrapper.jsonl`. No runner PID, capture, boot log, or lease was created by this attempt; the +1 replacement-boot budget remains unused. The worker brief names lease failure as a first-failure stop, so no retry or downstream gate was run.

### Escalated replacement capture and direct/live gate

Brad clarified that busy slots mean wait, then run. The wrapper claimed slot 1 for `gb4cap4`; the escalated runner reached the race HUD (last snapshot `run/frames-gb4cap4-1/snap/snap-0270.24s.png`, showing 2nd/2, race clock and speed) and all 165 VQ samples through tick 8300. After the final requested VQ marker, PID 77008 received SIGTERM by PID; the runner handled it and exited 0. Wrapper: `bound=exit`, elapsed 274.173 s, `lease_released=true`. Slot 1 was confirmed free. Command: `python3 gb4_boot.py --label gb4cap4 --wall 540 --snap 10 --script "$ROUTE" --vq --vq-from 100 --vq-to 8300 --vq-step 50 --vq-dump --pklog --capture-file "$HOME/dev/ssx3-work/GB4/run/gb4cap.capture.bin"`, using the E33 route string in `run/boot-part2-escalated2-wrapper.jsonl`. Runner and ISO SHAs remained the two-read values above.

| Capture/replay item | Result | Receipt |
|---|---|---|
| Capture bytes | 2,126,672,057 bytes; GB4 lane 6.7 GB, all-ssx3 89.9/200 GB after boot. | `run/gb4cap.capture.bin`; `local/tooling/disk_budget.sh` |
| Complete records | 1,497,245 GIF packets, 52,411 priv events, 20,200 transfer metadata events, 9,369 VBlank markers; no native upload, local-to-host readback or HLE-clear events. | Binary walk of `run/gb4cap.capture.bin`; replay summary in `run/replay-direct-p2.log` |
| Tail integrity | **Partial final record:** at byte 2,126,670,514, a 1,758-byte packet record has only 1,539 payload bytes remaining (219 missing). `readEvent` currently treats this partial EOF as clean, so the replay test reports 607/607 despite the truncated tail. The last requested marker at tick 8300 precedes the truncated tail. | Binary length walk; `run/replay-direct-p2.log` |
| Marker/packet alignment | Capture and live `sub` packet counts match **165/165** at ticks 100..8300 (offset 0). First 5,000 capture packet byte hashes, ticks and lengths match the live pklog. | `run/marker-alignment-p2.csv`, `run/check_packet_prefix_p2.py` |
| Direct replay command | `PS2X_GS_REPLAY_CAPTURE=../run/gb4cap.capture.bin PS2X_GS_REPLAY_OUT=../run/replay-direct-p2.hashes ../build/ps2xTest/ps2x_tests > ../run/replay-direct-p2.log 2>&1` from the fork worktree; exit 0, suite 607/607, but the parser's tail check is defective. | `run/replay-direct-p2.log` |
| Direct vs live | First comparable tick 100 differs in VRAM; table above. Priv hash now matches at all 165 ticks. Present is compared on the same visible width/stride and matches only 3/165. | `run/direct-live-p2.csv` |

The capture has the same number of packets at every sampled marker, and the first 5,000 packet byte hashes agree with pklog. No missing early packet or HLE clear/readback has been demonstrated; the source of the VRAM divergence remains unidentified. The final record is incomplete because the runner was stopped mid-write after tick 8300, and replay's EOF validation must be fixed before any later gate. Capture path metadata is also suspect: packet 0 records Path1 while live pklog labels its source Path3; `m_curGifPath` defaults to Path1 when the stats listener is not armed. This metadata error is not shown to affect CPU VRAM. Per the GB4 stop rule, queue replay, negative control and paraLLEl were not started.

## Part 3 — first VRAM divergence bisect

| Gate | Result | Receipt |
|---|---|---|
| Partial EOF rejected | Pass: `readEvent` distinguishes a clean EOF from a partial length or body. New unit test passes. The Part 3 capture closes at marker 120 and passes an independent binary length walk. | `~/dev/ssx3-work/GB4/run/suite-part3.log`, `run/gb4p3.capture.bin` |
| Live vs replay ticks 1..120 | First VRAM difference at **VQ tick 95**: tick 94 live/replay `10ecb55c`/same; tick 95 `0949391b`/`95581d99`, both at 481 submitted packets. VRAM matches 98/120 sampled ticks; priv hashes match at tick 95 (they differ at some early pre-setup ticks). | `~/dev/ssx3-work/GB4/run/bisect-ticks-p3.csv` |
| First differing packet or pre-packet write | **Packet index 479, submitted during tick 94 (PATH1)**. After index 478 both VRAM hashes are `7aa1e8e6`; after index 479 live/replay are `0949391b`/`95581d99`. Its 208 bytes are identical to pklog (`fnv=2951ff70`). GIF PACKED tag: NLOOP=4, EOP=1, PRE=1, PRIM=`0x04c` (triangle strip, IIP and ABE), NREG=3; descriptors are NOP, RGBAQ, XYZF2. | [packet-479-part3.txt](packet-479-part3.txt), `~/dev/ssx3-work/GB4/run/bisect-packets-p3.csv` |

### Part 3 pins, commands and stop point

| Item | Result |
|---|---|
| Fork | `gb4-replay` at `140ace3` (`[GB4] Part 3 bisect first VRAM divergence`, `Orchestrated-By: Codex`); four source/test files. `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner` empty. No push. |
| Build | One allowed build: `nice -n 10 cmake --build build -j8 > run/build-part3.log 2>&1` from `~/dev/ssx3-work/GB4`; pass. |
| Suite | `(cd PS2Recomp && ../build/ps2xTest/ps2x_tests > ../run/suite-part3.log 2>&1)`; **608/608**, including `GB4 rejects a partial capture record at EOF`. |
| Runner SHA-256 (two reads) | `05a9aadd56939da915b0632b78735e509e402a9a60fe64a3149d2aec796c5008` / same. |
| ISO SHA-256 (two reads) | `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5` / same. |
| Boot | One escalated boot, queue off, slot 2: `python3 gb4_boot.py --label gb4p3 --wall 300 --snap 30 --script "$ROUTE" --vq --vq-from 1 --vq-to 120 --vq-step 1 --pklog --capture-file "$HOME/dev/ssx3-work/GB4/run/gb4p3.capture.bin" --env PS2X_GS_BISECT_TO=120`. The E33 route string is recorded in `run/boot-part3-wrapper.jsonl`. Capture closed at marker 120; tracked runner PID 84394 was then stopped by PID, exited 0. Wrapper `bound=exit`, elapsed 47.363 s, lease released; both slots subsequently free. |
| Capture | `run/gb4p3.capture.bin`, **375,884 bytes**, clean EOF with last record a tick-120 marker: 757 GIF packets, 508 priv writes, 6 transfer metadata events, 120 markers. 120 live VQ samples and 757 post-packet live VRAM hashes. |
| Replay | `PS2X_GS_REPLAY_CAPTURE=../run/gb4p3.capture.bin PS2X_GS_REPLAY_STEP=1 PS2X_GS_REPLAY_BISECT_TO=120 PS2X_GS_REPLAY_PACKET_TRACE=../run/replay-packets-p3.csv PS2X_GS_REPLAY_OUT=../run/replay-vq-p3.hashes ../build/ps2xTest/ps2x_tests > ../run/replay-p3.log 2>&1` from the fork worktree; exit 0, 608/608. 120 marker and 757 packet hashes emitted. |

The first divergence occurs **after a packet**, with identical pre-packet VRAM and identical packet bytes. It is not a demonstrated direct VRAM write between packets. The hidden GS draw state or CPU raster behavior at this first triangle strip is unresolved; the packet's raw fields are in the receipt. Live and replay VRAM hashes converge again after packet 481, then diverge at later draw packets. This report names the first distinguishing input/output point only; no cause or fix is claimed. Per the Part 3 instruction, work stops here and does not enter queue gates.

## Part 4 — rounding probe and fold

The Part 3 packet-479 divergence is sensitive to the host rounding mode. The old live boot reached the PATH1 XGKICK under round-toward-zero (RTZ); forcing that mode only for PATH1 replay packets reproduces its VRAM. The folded E53 base scopes GS processing to host IEEE mode, and the fresh capture/replay gate below matches through the race. These are observations from the named streams; no free-running queue boot or paraLLEl comparison was run in Part 4.

| Gate | Result | Receipt |
|---|---|---|
| Old `gb4p3` capture, nearest replay | Packet 479 after-hash `95581d99` vs live `0949391b`; VRAM matches 98/120 ticks, first difference tick 95. | `~/dev/ssx3-work/GB4/run/replay-packets-p3.csv`, `replay-vq-p3.hashes` |
| Old capture, RTZ for true PATH1 packets | Packet 479 after-hash **`0949391b`**; **120/120** tick VRAM hashes match live. 38 GIF packets rounded. The true path map is the first 757 entries of the live `pklog-gb4p3-1.txt`, saved as `run/gb4p3.paths.txt`; capture path metadata had the known default-PATH1 defect. The sequential test suite passed 608/608. | `run/replay-packets-p4-path1.csv`, `replay-vq-p4-path1.hashes`, `replay-p4-path1-sequential.log`, [rounding-p4.csv](rounding-p4.csv) |
| Old capture, RTZ for every packet | Packet 479 also `0949391b`, but only **82/120** tick VRAM hashes match; first difference tick 48. 757 GIF packets rounded. | `run/replay-packets-p4-all.csv`, `replay-vq-p4-all.hashes`, [rounding-p4.csv](rounding-p4.csv) |
| Fold onto fork `b9647f5`, build and suite | Local `gb4-fold` at `13cac7f`: seven GB2/GB3 prerequisite commits and four GB4 commits cherry-picked. E53's `ScopedHostMode` was kept after the queue-enqueue check in the three frontend conflict sites. Build passed; suite **548/548** with `PS2X_ENABLE_DIAG_TAPS` off. No runner-dir changes against `14b1e5cb`; no push. | `run/build-part4-fold.log`, `run/suite-part4-fold.log` |
| New capture, direct vs live | One queue-off I26-FAST race boot, slot 1, exited 0 after 288.356 s; capture closed cleanly at marker 3000, 2,752,955,786 bytes, 1,982,063 GIF packets, 16,264 priv events, 66,244 transfer metadata events, 3,000 markers. At **59/59** live VQ samples (ticks 100..3000 step 50), direct replay matches VRAM, priv-register and Present hashes; capture packet count matches live `sub=` at every sample. | `run/boot-gb4p4-1.log`, `run/gb4p4.capture.bin`, `run/replay-p4-fold-direct.log`, [direct-live-p4.csv](direct-live-p4.csv) |
| Queue vs direct, repeat | Both independent queued replays match all **60/60** direct replay rows (ticks 50..3000) byte for byte, for VRAM, priv and Present. Each suite passed 548/548. | `run/replay-p4-fold-queue1.log`, `run/replay-p4-fold-queue2.log`, `run/replay-vq-p4-fold-{direct,queue1,queue2}.hashes` |
| Drop-priv negative control | Expected gate failure: row 0 at tick 50 has priv `15fd4de7` and Present `00000000`, versus direct `af58b6ee` and `aea8f41f`. VRAM at that early row remains `ca1aad8a`. Test totals 547 passed, 1 expected failure; **0/60** rows equal direct. | `run/replay-p4-fold-droppriv.log`, `run/replay-vq-p4-fold-droppriv.hashes` |

The 59 live VQ `priv=` values are GS `privWrite` *call* counts; the capture has two more priv *events* at every sampled marker because one call may record multiple changed registers. Register hashes still match 59/59. The difference is recorded explicitly in [direct-live-p4.csv](direct-live-p4.csv). The live VQ line at tick 3000 and direct replay both read `vram=3ed0b123`, `priv=a38c42dd`, `present=86a4f61f`; cumulative GIF packets are 1,982,063.

### Part 4 pins and commands

| Item | Pin / command |
|---|---|
| Fork | `gb4-replay` probe commit `f6fb863`; folded branch `gb4-fold` at `13cac7f`, based on fork `b9647f54934f9f7c448d7cf41fb42f81c74c8ed8` (E58/E53 line). The fold includes GB2/GB3 prerequisites `f67e123 bdf58cf a0bde6e f1c7cab e630532 f9f9a6f 574354a`, then GB4 `62e6a55 df0c99b 140ace3 f6fb863`. `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner` was empty. |
| Probe | In the old GB4 build: `PS2X_GS_REPLAY_CAPTURE=../run/gb4p3.capture.bin PS2X_GS_REPLAY_STEP=1 PS2X_GS_REPLAY_BISECT_TO=120 PS2X_GS_REPLAY_PATH_FILE=../run/gb4p3.paths.txt PS2X_GS_REPLAY_RTZ=path1 PS2X_GS_REPLAY_PACKET_TRACE=../run/replay-packets-p4-path1.csv PS2X_GS_REPLAY_OUT=../run/replay-vq-p4-path1.hashes ../build/ps2xTest/ps2x_tests`; repeated with `RTZ=all` and the corresponding `p4-all` output paths. The two experimental suites were initially run concurrently and hit unrelated E41 file-based test interference; the sequential PATH1 rerun passed 608/608. |
| Build | `nice -n 10 cmake --build ../build -j8`; existing Ninja Release cache points `PS2X_GAME_CODEGEN_DIR` at canonical `/Users/brad/dev/ssx3-work/codegen-ssx3`, runtime/aggressive logs off. Part 4 used two successful builds total: old probe and folded build. |
| Boot | From `~/dev/ssx3-work/GB4`: `python3 gb4_boot.py --label gb4p4 --wall 540 --script '<I26-FAST route from local/research/I26/ROUTES.md>' --gs-queue 0 --vq --vq-from 100 --vq-to 3000 --vq-step 50 --pklog --capture-file /Users/brad/dev/ssx3-work/GB4/run/gb4p4.capture.bin --env PS2X_SKIP_MOVIE=1 --env PS2X_GS_CAPTURE_STOP_TICK=3000`. It was launched with escalated permissions, claimed/released mini slot 1, and used only the one authorized boot. The exact route is in the wrapper's `event=env` output and the I26 route file. |
| Runner SHA-256 (two reads) | `b795e8f635c75b034b7a29c102c7c7d43c5c13d9e2bf28ee68d6cbd44e279581` both times for `build/ps2xRuntime/ps2EntryRunner`. |
| ISO SHA-256 (two reads) | `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5` both times for `~/dev/ssx3-work/E32-inputs/SSX 3 (USA).iso`. |
| Capture SHA-256 (two reads) | `a6f75fb34fceccf6fd92ad65950d16f05a140cf38a3cc2f028be32e56ad51851` both times. The direct replay parsed clean EOF and 3,000 markers. |
| Replay | With `PS2X_GS_REPLAY_CAPTURE=../run/gb4p4.capture.bin PS2X_GS_REPLAY_STEP=50`, run `../build/ps2xTest/ps2x_tests` once with `PS2X_GS_REPLAY_OUT=../run/replay-vq-p4-fold-direct.hashes`. For queue runs add `PS2X_GS_REPLAY_MODE=queue PS2X_GS_REPLAY_EXPECT=../run/replay-vq-p4-fold-direct.hashes`, changing `OUT` to `queue1`/`queue2`; for the negative control add `PS2X_GS_REPLAY_DROP_PRIV=1` and output `droppriv`. |

All Part 4 builds, boot and gates completed within the added budget. The original Part 2 paraLLEl work is still separate: it requires its own build and live boot, which the Part 4 budget did not provide. Recommended next action: the orchestrator can use this matched stream gate to authorize a paraLLEl comparison against the same capture.
