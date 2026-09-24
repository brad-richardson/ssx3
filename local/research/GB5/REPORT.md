# GB5 Part 1 — indexed CPU display crop probe

## Pins and gate table

| Item | Evidence |
| --- | --- |
| G worktree | `~/dev/ssx3-work/GB4/PS2Recomp`, local `gb4-parallel`; started at `c5913e425271515ec57b4e3a8a043e6100957f40`, probe committed as `b7d3227` (`[GB5]`, `Orchestrated-By: Codex`). No push. |
| Capture | Reused `~/dev/ssx3-work/GB4/run/gb4p4.capture.bin`, 2,752,955,786 bytes; SHA-256 `a6f75fb34fceccf6fd92ad65950d16f05a140cf38a3cc2f028be32e56ad51851`, independently checked with `shasum -a 256`. No copy. |
| X5 index | `local/research/X5/packets-949-950.csv`, SHA-256 `858c70a64fe33b94a3ef444b69be9103e7117262a7e9a57e0d7ac37c93d5ad95`. 922 continuous rows, indices 143805–144726: 461 at tick 949, 461 at tick 950. Source: `local/research/X5/REPORT.md`. Packet 144266: tick 950, corrected PATH3, 1,696 GIF bytes, FNV `cc6dd8df`, offset 158919448. |
| Build | One incremental build, pass. Existing GB4 Part 6 Release/Ninja configuration was reused; no configure needed. `~/dev/ssx3-work/GB4/run/build-gb5-1.log`. |
| Default host suite | **556/556 pass**, from fork root with probe unset. `run/suite-gb5-1.log`. |
| CPU replay | One direct CPU replay, **556/556 pass**. All 922 packet tuples checked at replay time against X5's index, tick, record offset, corrected path, embedded path, GIF byte count and GIF FNV. `run/replay-gb5-cpu.log`. |
| Changed-crop packet rows | **0** among 922 checked packets. Header-only [crop-changes.csv](crop-changes.csv) is the committed bounded row receipt; the identical run output is `~/dev/ssx3-work/GB4/run/gb5-crop-changes.csv`. No packet in this window changed a decoded pixel in either crop during its processing. |
| Negative control | Not run: the row table identifies no single candidate packet, so the brief's condition for dropping one is unmet. Replay budget used **1/2**, no device or mini boots. |
| Fork safety | `git diff --check` passed; `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner` was empty before the source commit. Probe source is only `ps2xTest/src/ps2_gs_replay_tests.cpp`; no guest or runner files changed. |

## Candidate table and pixel control

The probe samples the CPU raw DISPFB page before and after each packet, with the packet's own tick as the field parity. It calls the existing `GSCpuBackend::Present` read of live replay VRAM and requires 512×448 output with `displayFbp=sourceFbp=112`. Crops use half-open RGB coordinates; FNV-1a hashes the decoded RGB bytes in row order, and changed-pixel counts compare RGB triples. Reads and log output are replay-only and default off. Each packet's X5 tuple is checked before its pixel read. The row cap is 1,000; with 922 indexed packets it was not approached.

| First changed packet | Tick | Corrected path | GIF bytes / FNV | Upper `(320,120)-(420,205)` | Lower `(340,360)-(430,420)` |
| --- | --- | --- | --- | --- | --- |
| None in 143805–144726 | 949–950 | X5 tuple checked per packet | X5 tuple checked per packet | 0 changed-packet rows | 0 changed-packet rows |

Packet 144266 was checked as part of the 922; it produced no changed-pixel row. The probe emits per-packet before/after hashes only for changed packets, so no before/after hash for that individual packet is claimed.

At the final tick-950 marker the probe printed `GB5_FINAL tick=950 upper=1d75d1be lower=9cb9639d rows=0`. The existing GB4 Part 6 CPU raw image `~/dev/ssx3-work/GB4/run/p6-cpu-raw-ppm/vq-000950.ppm` has SHA-256 `f64e48ac02dead4a6c1fc28e5c1741361cc32f2a40467f71a6ed2932451650d0`; its CPU Present peer is byte-identical. Decoding that PPM independently gives:

| Crop | Pixels | FNV-1a RGB | Nonblack pixels | Distinct RGB values | Match to probe final |
| --- | ---: | --- | ---: | ---: | --- |
| Upper | 8,500 | `1d75d1be` | 8,500 | 566 | Yes |
| Lower | 5,400 | `9cb9639d` | 5,234 | 875 | Yes |

These observations concern CPU replay pixels in the two specified crops only. They do not identify the renderer difference in the paraLLEl image or exclude packet effects outside the tick-949/950 window. A non-packet event between two sampled packets is also outside this per-packet change table.

## Exact commands and budget

Run from `~/dev/ssx3-work/GB4/PS2Recomp` unless stated otherwise:

```sh
# From ~/dev/ssx3: capture pin
shasum -a 256 /Users/brad/dev/ssx3-work/GB4/run/gb4p4.capture.bin

# From ~/dev/ssx3-work/GB4: existing configured build
cmake --build build -j8 --target ps2x_tests > run/build-gb5-1.log 2>&1

# From fork worktree root
../build/ps2xTest/ps2x_tests > ../run/suite-gb5-1.log 2>&1
PS2X_GS_REPLAY_CAPTURE=../run/gb4p4.capture.bin PS2X_GS_REPLAY_PATH_FILE=../run/gb4p4.paths.txt PS2X_GS_REPLAY_STEP=50 PS2X_GS_REPLAY_PPM_TICKS=950 PS2X_GS_REPLAY_GB5_INDEX=/Users/brad/dev/ssx3/local/research/X5/packets-949-950.csv PS2X_GS_REPLAY_GB5_TRACE=../run/gb5-crop-changes.csv ../build/ps2xTest/ps2x_tests > ../run/replay-gb5-cpu.log 2>&1
```

The replay log reports `GB4_REPLAY_SUMMARY mode=direct backend=cpu ... packets=1982063 ... markers=3000 ... samples=60 rtz=off` and `GB4_FRAME tick=950 ... display_fbp=112 source_fbp=112 ... present=f96b53f0`, matching GB4 Part 6's tick-950 CPU frame line and present hash. Build, suite, replay log and trace total 127,663 bytes; the rebuilt `ps2x_tests` binary is 8,196,872 bytes. New output stayed well below 2 GB. Wall budget stayed below 90 minutes; build attempts 1/2 (one correction unused), CPU replays 1/2, boots 0.
