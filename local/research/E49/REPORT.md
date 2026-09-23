# E49 report: the MPEG HLE signals end-of-movie, and `0x3b1140` is enabled

Brief `local/muse/prompts/E49.md`. Worker: Claude Code (Opus pane),
2026-09-23, Mac mini (M5 Pro). Tables + receipts; the orchestrator
decides.

## Outcome

- **Boot A passes all six of E48's predicted observables.** With
  `PS2X_SKIP_MOVIE=1` and the breaker enabled, each startup movie ends
  through the guest's own end check. The frontend starts at t258 (E48 B2:
  t257), and the rider is visible at Select Character. The route then
  reaches the race (HUD 00:00:28, 1ST/2, 66 MPH at t8797).
- **Boot B (faithful path, bypass off) does not get past movie 1.**
  The main thread parks in the MPEG picture wait at the first
  `sceMpegGetPicture` (t247) and stays there until t18001 (end of the
  300 s boot). There are 15 CD reads (240 sectors) at t247, then no
  more CD activity for the rest of the boot, and the display is black.
  The end word is never reached, so this is the known
  faithful-playback stall (E30's "second chunk never requested"
  shape), not a failure of this fix. It goes to E34.
- The fork's `ssx3` is at `b48b502` (2 commits, ff-pushed after the
  runner-dir check). The suite is 592/592, and the new test fails on
  the base runtime.

## Code read

`ee-at 0x402b38 0 12` (function start, `sub_00402B38`, 0x20 bytes;
`ee-xref`: one caller, `jal` at `0x3b108c` in `sub_003B0FB8`):

```
0x402b38: 8c830040  lw $v1, 0x40($a0)
0x402b3c: 03e00008  jr $ra
0x402b40: 8c620000  lw $v0, 0x0($v1)  [delay slot]
```

So the end check returns `[[a0+0x40]+0]`, where a0 = the mpeg handle
(`codec+0x30`, the same handle `sceMpegGetPicture` receives). The
address was resolved the way the guest resolves it. No HLE is bound
at `0x402b38`.

Second finding (ELF disassembly with `llvm-objdump`: the `0x4027b8`
Create is an HLE stub, so `ee-at` has no code for it). The stock
`sceMpegCreate@0x4027B8` stores the work area to `mpeg+0x40` at
`0x402820` and then calls `sceMpegReset@0x402B58` (`jal` at
`0x40292c`). The Reset HLE already clears `inner+0`, but the Create
HLE never calls Reset. The guest's Open (`0x3b0b40`) calls Create at
`0x3b0f4c` for every movie, and each movie's handle and work area are
reused at the same address (E48). Without a clear in Create, movie 2
would start with movie 1's end word set.

## Change (fork `~/dev/PS2Recomp`, branch `ssx3`)

| Commit | What |
|---|---|
| `9d3b53b` [E49] MPEG HLE sets the sceMpegIsEnd word; enable 0x3b1140 | `MPEG.cpp`: `getMpegPicture` computes `publishEnd = streamEnded && decodedFrames.empty()` under the MPEG lock after the serve/no-serve decision, then writes `1` to `[[mpeg+0x40]+0]` (only if `[mpeg+0x40] != 0`). Bypass: GetPicture sets `streamEnded` itself. Faithful path: program end (`0xB9`) or producer EOF (`finishPlaybackStream`), after the flush, so the word is set on the call that serves the last queued picture, or on the first call after the queue drains. `sceMpegCreate` clears `inner+0` (mirrors the stock Create→Reset). `ssx3.toml`: `"0x003B1140"` appended to `extra_function_starts` (19 entries), header comment updated. New unit test. |
| `b48b502` [E49] End-word test: dirty value 7 … | Test hardening (below) |

`git diff --stat 14b1e5cb ssx3 -- ps2xRuntime/src/runner` is empty
(checked before each push). Pushes: `2e21cdc..9d3b53b`, then
`9d3b53b..b48b502`, to `fork/ssx3`, both fast-forward.

### Unit test

`sceMpegGetPicture publishes the sceMpegIsEnd word once the stream has
ended` (`ps2xTest/src/ps2_runtime_expansion_tests.cpp`): the work area
is pre-dirtied with 7, then Create → 0. After a DemuxPss of
`00 00 01 B9` (program end) the word is still 0. GetPicture then
returns 0 without waiting and the word is 1. Re-Create → 0.

| Runtime | Suite | This test |
|---|---|---|
| fix (`b48b502`) | **592/592** | pass |
| base `MPEG.cpp` @ `2e21cdc` (test build only) | 591/592 | **all 4 end-word assertions fail** |

The first version (dirty value 1) passed its GetPicture assertion on
the base runtime from stale data, which is why `b48b502` switches to 7.
The suite ran from the fork root, flags unset.

## Codegen and build

- Toml `~/dev/ssx3-work/E49/ssx3-e49.toml` is the fork toml with the
  3 path lines repointed at internal disk. Regen used
  `E46-build/ps2xRecomp/ps2_recomp` (recompiler unchanged since
  `351b57f`) → `~/dev/ssx3-work/codegen-ssx3-e49`, 1.6 s, `resolved 19
  of 19 configured extra function start(s) across 18 owner
  function(s)`. **2 files differ** from canonical `codegen-ssx3`:
  `register_functions.cpp` and `sub_003B10D0_0x3b10d0.cpp`. Canonical
  `codegen-ssx3` was not touched.
- Build `~/dev/ssx3-work/E49-build`: Release, AGRESSIVE/RUNTIME logs
  OFF, TEST ON, STUDIO OFF, FFmpeg ON, deps from `E46-build/_deps`.
  The cache differs from E46-build only in `PS2X_GAME_CODEGEN_DIR`.
  `ninja -j8 ps2EntryRunner ps2x_tests`: 7 min 31 s, rc 0.
- Wait rule: the build started once both lease slots were free (E47's
  runner had exited) and load was 7.85. A Spotlight burst on the new
  codegen dir had pushed load to 11; I waited it out.

## Boot A: `PS2X_SKIP_MOVIE=1`, E33 route, 300 s

`python3 local/research/E49/e49_boot.py --skip 1 --label e49a --wall 300
--snap 2 --script "<E33 route>"` (E48's wrapper with the E49 runner and
a bypass switch; same 14-window `PS2X_DIAG_WATCH`). Slot 2. E50's boot
held slot 1 (peer PID 29918), and my runner was tracked by its own PID.
rc 0, bound wall 300.3 s, max tick 8881. Analyzer output:
`an-e49a.md`.

| Predicted observable (E48) | E48 B2 (breaker off) | **E49 A** | Verdict |
|---|---|---|---|
| per movie, `0x402b38` nonzero at the 2nd next-picture call | n/a (pool-empty exit) | `0x3b1050` ×6 = `0x402b38` ×6, alloc ×3, GetPicture ×3: each movie's 2nd call returns before alloc. Watch: per movie one alloc, then the release, then Close, with no 2nd alloc (t246/248/249, t249/251/252, t253/254/255) | **PASS** |
| alloc `0x3b10d0` ×3 (not 6) | 6 | **3** | **PASS** |
| `0x3b1140` ×3, zero missing-target | 0 run, 3 missing | **3** (first/last ra `0x3b06a0`), **0** missing-target lines | **PASS** |
| Close ×3 | 3 | **3** (`0x3b09a0`) | **PASS** |
| menus at ~t257 | t257+ (`34df101e` at t267) | black `fd889dc5` t248–257, then `2f658187` t258, `34df101e` t260–268; title screen at t296 (`frames/e49a-title-t296.png`) | **PASS** |
| rider visible at Select Character | Zoe + stray glyphs (t1363) | Zoe visible at t1300 (`frames/e49a-sc-t1300.png`); stray glyphs still present (open item, as E48 expected) | **PASS** |

Other counters: SetPicture `0x254c48` ×3, release caller `0x254dc0`
×3, thunk `0x3b0680` ×3, Open ×3. MPC CD reads at t246/t249/t253
(`0x13ba33`, `0x13b5b1`, `0x15107b`), the same as E48 B2. In the
watch timeline, release #1 writes rc=0 at `0x3b1150`, unlinks from
the active list and relinks to the free list (`0x3b116c..90`). Close
then drains the **free** list (`0x3b0a8c..`), not the active list as
in B2. That's the expected difference once the release runs. Later
in the same boot the E33 route reaches the race: HUD 2ND/2 00:00:03
at t7295 (`frames/e49a-race-t7295.png`) and 1ST/2 00:00:28 7% 66 MPH
at t8797 (`frames/e49a-race-t8797.png`). The world is still dark
(E47's open issue). Park at SIGTERM: `park-e49a.txt`. The tick rate
comes from a diagnostic build (watch on, frame dumps), so it isn't a
speed number.

## Boot B: bypass off (faithful path), E33 route, 300 s

Same wrapper with `--skip 0`, under `env -u PS2X_SKIP_MOVIE` (the boot
event's env shows no `PS2X_SKIP_MOVIE`). Slot 2, with E50's `e50b` in
slot 1 (peer PID 30901). rc 0, bound wall 300.2 s, max tick 18001.
Analyzer output: `an-e49b.md`.

| Question | Answer |
|---|---|
| Do the startup movies end on their own? | **No.** Movie 1 never ends; movies 2 and 3 never start (1 MPC read) |
| Title/menus reached? | No. Black `fd889dc5` from t248 to t18001 (16,077 dumps; `frames/e49b-black-t17930.png`, the same bytes as E48's B1 black) |
| MPEG activity (park hot_pc) | Open ×1, `0x3b1050` ×1, `0x402b38` ×1 (returned 0), alloc ×1, GetPicture ×1; SetPicture, release and Close ×0 |
| Where it stops | thread 1 `Waiting wait=Mpeg:0 pc=0x3b1028` (inside the GetPicture call); threads 2–6 in semaphore waits (`park-e49b.txt`) |
| CD activity | 15 `sceCdRead` of movie 1 (`0x13ba33`..`0x13bb13`, 240 sectors) all at t247, then **no CD reads for the rest of the boot** |
| missing-target | 0 |

The MPEG logs are compiled out in this build, so feed/packet counts
aren't visible. The shape (one GetPicture parked in its picture wait,
the producer idle after about 491 KB) matches E30's zero-packet stall
(first chunk parsed, second chunk never requested). E30's re-dispatch
fix is not in `ssx3`. Per the brief, this state goes to E34. The end
word is never exercised on this path, because playback never reaches
`streamEnded`.

## Budgets

| Budget | Used |
|---|---|
| Builds | 1 full (7.5 min) + 3 test-only relinks (negative/positive checks) |
| Boots | 2 of 2 (slot 2 each; claimed and released by the wrapper; own-PID tracked) |
| Time | ~0.7 h of 4 h |
| Disk (cap 4 GB) | `E49-build` 2.8 GB + `codegen-ssx3-e49` 273 MB + `E49` 85 MB ≈ **3.2 GB**; ssx3 total 44.8 GB of 200 before |

## Gaps

- Boot B can't show whether the end word fires correctly on the
  faithful path, since it never gets that far. The faithful-path
  branch (program end / producer EOF with an empty queue) is covered
  only by the unit test (program end).
- Both boots shared the host with E50's boots in the other slot. That
  doesn't affect the counters, but the tick rate isn't comparable to
  quiet-host boots.
- No T-lane PCSX2 read of `[[0x587b30+0x40]+0]` at the end of movie 1
  (E48's suggested cross-check). The only evidence that the stock game
  ends movies through this word is the code shape plus boot A.
- Stray glyphs at Select Character are unchanged (still open, todo H4).

## Receipts

| Item | Value |
|---|---|
| Fork | `ssx3` @ `b48b502` (`9d3b53b` + `b48b502` on `2e21cdc`), pushed to `fork/ssx3` |
| Runner | `~/dev/ssx3-work/E49-build/ps2xRuntime/ps2EntryRunner` `6889bd48aafe1dd07605bc4c7e69aa368728feb1beb10273a8106fe14f6fa4a7` (read ×2 before boot A, ×1 before boot B, ×1 after the test relinks) |
| Codegen | `~/dev/ssx3-work/codegen-ssx3-e49` (2 files differ from `codegen-ssx3`) |
| Boot A log | `~/dev/ssx3-work/E49/run/boot-e49a-1.log(.gz)` (only the .gz kept) 12,041,263 B `3c74e8dd3b4c1aec7354ad327964d31bc6d547b818a370ca305dca4af0dff2fc`; gz 336,624 B `0201e459f8def0a2aff19807b964c8626e289b9ec52e84e044479d046ae81411` |
| Boot B log | `…/boot-e49b-1.log(.gz)` (only the .gz kept) 51,327,887 B `fe4f2bfaeb3f2f3d8fd71354f8a17517c54ebc13e171d38b1576711c5ac64202`; gz 617,678 B `aaac864233a5d41e7b56dea404f8c11010aeda447f52e3cd3432e5a1fe9911ea` |
| Frames | `frames/e49a-title-t296.png` `054edef5…`, `e49a-sc-t1300.png` `786da7d2…`, `e49a-race-t7295.png` `3dc5330d…`, `e49a-race-t8797.png` `1d0c6a4d…`, `e49b-black-t17930.png` `6120a759…` |
| Share mirror | `/Volumes/share/ssx3/ps2x-e49/` (both .gz + REPORT.md, SHAs re-read) |
| In this dir | `e49_boot.py`, `e49_analyze.py`, `an-e49a.md`, `an-e49b.md`, `park-e49a.txt`, `park-e49b.txt` |
| Logs in `~/dev/ssx3-work/E49/` | `regen.log`, `configure.log`, `build.log`, `suite.log` (592/592), `suite-negative.log` (591/592), `boot-e49{a,b}.driver.log` |

## Exact commands

```
local/tooling/ee/ee-at 0x402b38 0 12; local/tooling/ee/ee-xref 0x402b38
llvm-objdump -d --triple=mipsel --mcpu=mips3 --start-address=0x4027b8 --stop-address=0x402a10 ~/dev/ssx3-work/E32-inputs/cd/SLUS_207.72
~/dev/ssx3-work/E46-build/ps2xRecomp/ps2_recomp ~/dev/ssx3-work/E49/ssx3-e49.toml
cmake -S ~/dev/PS2Recomp -B ~/dev/ssx3-work/E49-build -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_BUILD_TEST=ON -DPS2X_BUILD_STUDIO=OFF \
  -DPS2X_GAME_CODEGEN_DIR=/Users/brad/dev/ssx3-work/codegen-ssx3-e49 -DFETCHCONTENT_SOURCE_DIR_<X>=~/dev/ssx3-work/E46-build/_deps/<x>-src …
ninja -C ~/dev/ssx3-work/E49-build -j8 ps2EntryRunner ps2x_tests
(cd ~/dev/PS2Recomp && ~/dev/ssx3-work/E49-build/ps2xTest/ps2x_tests)
python3 local/research/E49/e49_boot.py --skip 1 --label e49a --wall 300 --snap 2 --script "<E33 route>"
env -u PS2X_SKIP_MOVIE python3 local/research/E49/e49_boot.py --skip 0 --label e49b --wall 300 --snap 2 --script "<E33 route>"
python3 local/research/E49/e49_analyze.py e49a > local/research/E49/an-e49a.md   # likewise e49b
```

E33 route: `10350:start:2500,20650:cross:2000,23200:cross:400,24000:cross:400,30890:cross:1700,39560:cross:1750,47240:down:4200,55450:cross:1800,64920:cross:2000,113340:cross:800,118270:cross:700,122510:cross:700,113340:down:20000`.

## Recommendation (the orchestrator decides)

1. Accept the fix. Promote `codegen-ssx3-e49` as canonical
   `codegen-ssx3` (the fork toml already carries `0x003B1140`), and
   point the next lanes' builds at `ssx3` @ `b48b502`. That also
   removes E48's side lead: the null-node GetPicture write to low RAM
   no longer happens, because alloc returns 0 zero times.
2. E34 (faithful movies): start from boot B's state (GetPicture
   parked at t247 after 240 sectors) and E30's un-landed re-dispatch
   diffs. Once movies play, check that the end word fires at producer
   EOF.
3. Optional: a T-lane PCSX2 read of `[[0x587b30+0x40]+0]` across the
   end of movie 1, to confirm the stock end signal.
