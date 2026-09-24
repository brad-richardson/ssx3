# GB5C — matched replay crop comparison

## Pins and replay

| Item | Evidence |
| --- | --- |
| G worktree | `/Users/brad/dev/ssx3-work/GB4/PS2Recomp`, branch `gb4-parallel`, `f79666938a90b550a4d8f4860e9ec567ad00c48a`; clean at start and no source edit. |
| Capture | `run/gb4p4.capture.bin`, 2,752,955,786 bytes; two independent reads (`shasum -a 256`, `sha256sum`) both `a6f75fb34fceccf6fd92ad65950d16f05a140cf38a3cc2f028be32e56ad51851`. No copy. |
| Path sidecar | `run/gb4p4.paths.txt`, 18,709,520 bytes; same capture and true packet path sidecar as GB5B. |
| CPU raw inputs | All eight P6 512×448 maxval 255 files existed before replay: 899 from `gb5b-periodic-raw-ppm`; 900, 901, 950 from `p6-cpu-raw-ppm`; 902, 921, 922, 949 from `gb5b-target-raw-ppm`. Parser checked format and raster size for every CPU and GPU frame. CPU crop hashes at 899 and 950 match GB5B's reported values. |
| Existing binary | `../build/ps2xTest/ps2x_tests`, 8,196,984 bytes, newer than replay source at the pinned worktree; no build. |
| Replay | One sandbox attempt initialized no Vulkan device (`init_ok=0`, no PPMs), so it was retained as `run/gb5c/replay-sandbox.log`. One escalated correction produced eight PPMs in `run/gb5c/parallel-ppm`; `run/gb5c/replay.log` reports **556/556**, failed 0. This is the GPU run used below. |
| Replay counters | `GB4_REPLAY_SUMMARY`: 1,982,063 packets, 16,264 priv writes, 66,244 transfers, 3,000 markers, 60 samples, readbacks 0, clears 0. `GB4_PARALLEL_STATS`: packets 1,982,063, presents 66, null_scanouts **0**, unsupported_clears **0**, unsupported_vram_io **0**, init_ok 1, init_failed 0. All eight `GB4_FRAME` rows have `display_fbp=source_fbp=112`, `DISPFB1=9070`. |
| Data cap | `run/gb5c` has 18 files / 14,443,480 logical bytes, including 8 PPMs / 5,505,144 bytes (<100 MiB), 4 PNGs / 738,606 bytes (<25 MiB), and both logs. <1 GiB total. One successful GPU replay plus one sandbox correction; builds 0, boots 0. No speed claim. |

## Crop comparison

Crop bounds are half-open: upper `(320,120)-(420,205)` (8,500 pixels), lower `(340,360)-(430,420)` (5,400 pixels). The read-only [`compare.py`](/Users/brad/dev/ssx3-work/GB4/run/gb5c/compare.py) validates P6 format, 512×448 dimensions, maxval 255 and exact raster length; it prints CSV to stdout. FNV-1a is 32-bit over row-major RGB crop bytes. RGB MAE is mean absolute error over all crop channels; differing pixel counts compare RGB triplets. First difference is in full-frame coordinates. Full-frame count compares all 229,376 RGB pixels. Machine-readable receipt: [`crop-comparison.csv`](/Users/brad/dev/ssx3-work/GB4/run/gb5c/crop-comparison.csv).

| Tick | Crop | Differing pixels | RGB MAE | First differing `(x,y)` | CPU FNV-1a | paraLLEl FNV-1a | Full-frame differing pixels |
| ---: | --- | ---: | ---: | --- | --- | --- | ---: |
| 899 | upper | 3115 | 0.208275 | `(364,120)` | `30c4fd7b` | `5a48264e` | 78035 |
| 899 | lower | 3189 | 6.777531 | `(356,360)` | `fbdfe4ac` | `faf4ea9e` | 78035 |
| 900 | upper | 3632 | 0.214902 | `(364,120)` | `e0300fd4` | `59bb20ae` | 90097 |
| 900 | lower | 3818 | 10.182407 | `(356,360)` | `555cccdc` | `233314df` | 90097 |
| 901 | upper | 4189 | 0.276353 | `(364,120)` | `5f555125` | `1bd2b732` | 96046 |
| 901 | lower | 3959 | 13.020062 | `(356,360)` | `3c07ca34` | `b4ecd14d` | 96046 |
| 902 | upper | 4273 | 0.290549 | `(361,120)` | `ecf3e93c` | `04147199` | 100592 |
| 902 | lower | 4115 | 15.978086 | `(356,360)` | `ca77b54e` | `17761acb` | 100592 |
| 921 | upper | 6461 | 28.980157 | `(361,120)` | `f0642646` | `c773af82` | 113874 |
| 921 | lower | 4771 | 33.229815 | `(356,360)` | `9cb9639d` | `3130a09c` | 113874 |
| 922 | upper | 6349 | 30.896824 | `(361,120)` | `1d75d1be` | `8f66e65b` | 114724 |
| 922 | lower | 4835 | 33.353272 | `(356,360)` | `9cb9639d` | `a7e990de` | 114724 |
| 949 | upper | 6412 | 31.296745 | `(361,120)` | `1d75d1be` | `db2d1d95` | 125362 |
| 949 | lower | 4771 | 33.268704 | `(356,360)` | `9cb9639d` | `37785208` | 125362 |
| 950 | upper | 6241 | 31.320588 | `(361,120)` | `1d75d1be` | `35daf739` | 123546 |
| 950 | lower | 4737 | 34.048086 | `(356,360)` | `9cb9639d` | `b57315aa` | 123546 |

## Viewed frames

The PNGs show CPU on the left and paraLLEl on the right, with a red upper outline, green lower outline, and 4× crop enlargements below the full frames. I viewed all four:

| Tick | PNG | Observation |
| ---: | --- | --- |
| 899 | [`pair-899.png`](/Users/brad/dev/ssx3-work/GB4/run/gb5c/pair-899.png) | The upper crop is empty menu background on both sides, with low-amplitude pixel differences (MAE 0.208). The lower crop already has paraLLEl breaks/dark spots through “Select,” “Previous,” and “Options”; full-frame thin marks are also visible on the paraLLEl side. |
| 902 | [`pair-902.png`](/Users/brad/dev/ssx3-work/GB4/run/gb5c/pair-902.png) | Main menu list is still absent from the upper crop; background pixels differ slightly (MAE 0.291). Lower labels on the paraLLEl side have darker, blockier strokes and horizontal banding. |
| 921 | [`pair-921.png`](/Users/brad/dev/ssx3-work/GB4/run/gb5c/pair-921.png) | “Continue,” “Equip Gear,” “Rider Details,” and “Music” are present in both upper crops, but paraLLEl letters are blurred, interrupted or doubled. Lower button labels remain blocky/damaged. |
| 950 | [`pair-950.png`](/Users/brad/dev/ssx3-work/GB4/run/gb5c/pair-950.png) | Zoe and the highlighted “Continue” row are recognizable on both sides. paraLLEl menu glyphs and lower labels still have interrupted/doubled strokes; thin horizontal marks remain elsewhere in the frame. |

## Timing comparison and limits

The earliest sampled crop and full-frame mismatch is **tick 899**, before GB5B's 13 crop-changing instances of the recurring 1,696-byte PATH3 composite at ticks 902–921. The lower label damage is already visible at 899. Those 902–921 instances therefore cannot be the first cause of *all* matched crop divergence or of the already-visible lower label damage. No earlier matched pair was sampled, so the first divergence is only bounded as **at or before 899**. The upper menu glyphs are absent at 899 and 902 and damaged once present at 921; this comparison does not exclude a 902–921 packet or state contribution to those glyphs. A crop hash difference is not evidence of glyph-stroke identity, and the replay does not isolate a producer. The orchestrator decides the gate.

## Exact commands and gaps

From `/Users/brad/dev/ssx3-work/GB4/PS2Recomp` unless shown otherwise (`run/` means `/Users/brad/dev/ssx3-work/GB4/run/`):

```sh
# Input verification, from run/
shasum -a 256 gb4p4.capture.bin
sha256sum gb4p4.capture.bin

# Same command for sandbox attempt and escalated correction; logs kept separately.
PS2X_GS_REPLAY_BACKEND=parallel GRANITE_VULKAN_LIBRARY=/opt/homebrew/lib/libvulkan.1.dylib PS2X_GS_REPLAY_CAPTURE=../run/gb4p4.capture.bin PS2X_GS_REPLAY_PATH_FILE=../run/gb4p4.paths.txt PS2X_GS_REPLAY_STEP=50 PS2X_GS_REPLAY_PPM_TICKS=899,900,901,902,921,922,949,950 PS2X_GS_REPLAY_PPM_DIR=../run/gb5c/parallel-ppm ../build/ps2xTest/ps2x_tests > ../run/gb5c/replay.log 2>&1

python3 ../run/gb5c/compare.py > ../run/gb5c/crop-comparison.csv
python3 ../run/gb5c/make_pairs.py
```

The sandbox attempt's 556/556 exit did not prove replay success: its `GB4_PARALLEL_STATS` had `init_ok=0`, `init_failed=1`, and no PPMs. The escalated correction's Vulkan timestamp-domain warning did not prevent frame output or clean replay counters. No live boot, source edit, fork commit or push. Only this report is committed in `ssx3`.
