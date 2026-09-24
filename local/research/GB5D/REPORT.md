# GB5D — earlier matched replay marker bracket

## Pins and replay gate

| Item | Evidence |
| --- | --- |
| G worktree | `/Users/brad/dev/ssx3-work/GB4/PS2Recomp`, branch `gb4-parallel`, `f79666938a90b550a4d8f4860e9ec567ad00c48a`; clean at start, no source edits. |
| Capture | Reused `run/gb4p4.capture.bin`, 2,752,955,786 bytes. Independent `shasum -a 256` and `sha256sum` reads both gave `a6f75fb34fceccf6fd92ad65950d16f05a140cf38a3cc2f028be32e56ad51851`. Reused `run/gb4p4.paths.txt` true path sidecar; neither input was copied. |
| CPU inputs | All ten `run/gb5b-periodic-raw-ppm/vq-<tick>.ppm` files existed at ticks 100, 200, 300, 400, 500, 600, 700, 800, 850, 899; each was 688,143 bytes. The comparison parser verified P6, 512×448, maxval 255, and exactly 688,128 raster bytes in every CPU and GPU frame. |
| Binary and build | Existing `../build/ps2xTest/ps2x_tests`, 8,196,984 bytes, was newer than `ps2xTest/src/ps2_gs_replay_tests.cpp` at the pinned revision. Builds: **0**. |
| Replay | **One** escalated paraLLEl replay, no sandbox retry. `run/gb5d/replay.log` has **556/556**, failed 0, and all ten `run/gb5d/parallel-ppm/vq-<tick>.ppm` files. `GB4_PARALLEL_STATS` has `init_ok=1`, `init_failed=0`. All ten `GB4_FRAME` rows have `display_fbp=source_fbp=112`, `dispfb1=9070`. |
| Counters | `GB4_REPLAY_SUMMARY`: 1,982,063 packets, 16,264 priv writes, 66,244 transfers, 3,000 markers, 60 samples, 0 readbacks, 0 clears. `GB4_PARALLEL_STATS`: 1,982,063 packets, 61 presents, **0 null_scanouts, 0 unsupported_clears, 0 unsupported_vram_io**. |
| Data cap | `run/gb5d`: 21 files, 18,135,997 logical bytes total; ten PPMs 6,881,430 bytes (<100 MiB), eight PNGs 3,132,505 bytes (<25 MiB), all data <1 GiB. One successful GPU replay, 0 builds, 0 boots, 0 source edits. No speed claim. |

## Matched P6 lower-crop comparison

The lower crop is half-open `(340,360)-(430,420)`, 5,400 RGB pixels. FNV-1a is 32-bit over row-major crop bytes. RGB MAE is mean absolute error over 16,200 channels. Full-frame differing pixels compare all 229,376 RGB triplets. [`compare_and_pairs.py`](/Users/brad/dev/ssx3-work/GB4/run/gb5d/compare_and_pairs.py) validates P6 header, dimensions and exact raster size before comparing. Machine-readable receipt: [`lower-comparison.csv`](/Users/brad/dev/ssx3-work/GB4/run/gb5d/lower-comparison.csv). The 899 lower row reproduces GB5C's matched values.

| Tick | Lower differing pixels | Lower RGB MAE | CPU FNV-1a | paraLLEl FNV-1a | Full-frame differing pixels |
| ---: | ---: | ---: | --- | --- | ---: |
| 100 | 0 | 0.000000 | `69e12a65` | `69e12a65` | 82 |
| 200 | 0 | 0.000000 | `69e12a65` | `69e12a65` | 12,058 |
| 300 | 4,968 | 14.201481 | `02bfd499` | `f1414a21` | 175,335 |
| 400 | 4,966 | 14.041358 | `02bfd499` | `701eb6df` | 176,324 |
| 500 | 5,141 | 14.704444 | `02bfd499` | `ffb684fd` | 180,170 |
| 600 | 5,141 | 14.704444 | `02bfd499` | `ffb684fd` | 179,310 |
| 700 | 4,996 | 37.387222 | `032a9954` | `d9a35135` | 161,214 |
| 800 | 5,067 | 55.868395 | `3423acc5` | `1aa732ff` | 144,292 |
| 850 | 5,063 | 56.537963 | `3423acc5` | `81a8e712` | 145,672 |
| 899 | 3,189 | 6.777531 | `fbdfe4ac` | `faf4ea9e` | 78,035 |

## Viewed frames and marker interval

Each PNG has CPU on the left, paraLLEl Present on the right, the lower crop outlined in green, and that crop enlarged 4× below. I viewed all eight generated pairs; the four required marker pairs are linked here.

| Tick | Viewed pair | Lower-label observation |
| ---: | --- | --- |
| 700 | [`pair-700.png`](/Users/brad/dev/ssx3-work/GB4/run/gb5d/pair-700.png) | Main Menu button labels “Select,” “Previous,” “Options” are legible in CPU. The same letters have interrupted, blocky and doubled strokes in paraLLEl, especially “Select” and “Previous.” |
| 800 | [`pair-800.png`](/Users/brad/dev/ssx3-work/GB4/run/gb5d/pair-800.png) | Select Character buttons “Select,” “Previous,” “Options,” “Load game” are legible in CPU. paraLLEl retains broken/blocky strokes through the same labels; the effect is not just a background change. |
| 850 | [`pair-850.png`](/Users/brad/dev/ssx3-work/GB4/run/gb5d/pair-850.png) | The same four button labels persist; paraLLEl “Select,” “Previous,” and “Options” strokes are visibly interrupted and doubled again. |
| 899 | [`pair-899.png`](/Users/brad/dev/ssx3-work/GB4/run/gb5d/pair-899.png) | The transition fades the buttons to “Select,” “Previous,” “Options.” Despite lower contrast, paraLLEl strokes have the same blocky/broken pattern noted in GB5C. |

Supplementary viewed pairs [`pair-300.png`](/Users/brad/dev/ssx3-work/GB4/run/gb5d/pair-300.png), `pair-400.png`, `pair-500.png`, and [`pair-600.png`](/Users/brad/dev/ssx3-work/GB4/run/gb5d/pair-600.png) show the title/copyright screen, including visibly damaged paraLLEl **copyright text** from tick 300. They do **not** show the lower button labels. The lower crop is black at 100 and 200 in both backends; its difference at 300–600 is copyright text/background, not evidence about button-label strokes.

**First sampled CPU-visible lower button labels: tick 700. First sampled paraLLEl damage to those same label strokes: tick 700.** With tick 600 showing no button labels, the narrowest sampled bracket for *their first visible appearance already damaged* is **(600,700]**. This does not locate the first damaging input/state: it could precede visibility. The separate copyright-text damage at tick 300 shows the broader text-stroke problem is visible by 300, but the lower button glyphs cannot be compared before 700. The targeted next replay question is: at which markers in `(600,700]` do the button labels first appear in CPU, and are their matched paraLLEl strokes already damaged at that first appearance? No packet, texture or state producer is inferred from these frames. The orchestrator decides the gate.

## Exact commands and limits

From `/Users/brad/dev/ssx3-work/GB4/PS2Recomp` unless otherwise stated (`run/` resolves to `/Users/brad/dev/ssx3-work/GB4/run/`):

```sh
git branch --show-current
git rev-parse HEAD
git status --porcelain
shasum -a 256 ../run/gb4p4.capture.bin
sha256sum ../run/gb4p4.capture.bin

PS2X_GS_REPLAY_BACKEND=parallel GRANITE_VULKAN_LIBRARY=/opt/homebrew/lib/libvulkan.1.dylib PS2X_GS_REPLAY_CAPTURE=../run/gb4p4.capture.bin PS2X_GS_REPLAY_PATH_FILE=../run/gb4p4.paths.txt PS2X_GS_REPLAY_STEP=50 PS2X_GS_REPLAY_PPM_TICKS=100,200,300,400,500,600,700,800,850,899 PS2X_GS_REPLAY_PPM_DIR=../run/gb5d/parallel-ppm ../build/ps2xTest/ps2x_tests > ../run/gb5d/replay.log 2>&1

cd ../run/gb5d
python3 compare_and_pairs.py
```

The replay command used escalated permissions for Vulkan initialization. No live boot, mini/Odin/iOS use, fork commit, source edit or push. The local run data and comparison script remain outside git; only this report is committed in `ssx3`.
