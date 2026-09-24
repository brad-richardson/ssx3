# GB5B — earlier glyph pixel producer probe

## Verdict frame (orchestrator decides)

13 changed-packet rows in ticks 902–949, all the same recurring PATH3
composite packet (1,696 bytes, FNV `cc6dd8df`, first packet of its tick).
Per the orchestrator checkpoint these are composite/fade candidates, not
proof of the glyph stroke producer: the identical bytes recur once per
tick at 900–951 but change the crops on only 13 of 48 probed ticks, and
rows at 902–905 rewrite all 8,500/5,400 crop pixels per packet. Glyph
attribution is unresolved. Tighter intervals below.

## Pins and gate table

| Item | Evidence |
| --- | --- |
| G worktree | `~/dev/ssx3-work/GB4/PS2Recomp`, local `gb4-parallel`; started at `b7d3227`, probe committed as `f796669` (`[GB5B]`, `Orchestrated-By: Muse Code`). No push. |
| Capture | Reused `~/dev/ssx3-work/GB4/run/gb4p4.capture.bin`, 2,752,955,786 bytes; SHA-256 `a6f75fb34fceccf6fd92ad65950d16f05a140cf38a3cc2f028be32e56ad51851` via `shasum` and `sha256sum`. No copy. |
| Saved PPM crops | Raw `vq-000899/900/901.ppm` upper `30c4fd7b`/`e0300fd4`/`5f555125`, lower `fbdfe4ac`/`555cccdc`/`3c07ca34`; `vq-000949/950/951.ppm` all match `GB5_FINAL` (`upper=1d75d1be lower=9cb9639d`). Changed marker interval `(901,949]`. CPU non-raw PPMs byte-identical to raw at 899 and 950. |
| Periodic replay | Ticks `100,200,300,400,500,600,700,800,850,899`, CPU direct, **556/556**. 20 PPMs ≈ 13 MiB (cap 100 MiB). `run/replay-gb5b-periodic.log`. 899 re-render byte-identical (sha256 `86a941ff…f4b67`). |
| Periodic finding | Crops black at 100–200; nonblack from 300 (title screen); no periodic tick matches `GB5_FINAL`. `display_fbp=source_fbp=112` at all 10 markers; `dispfb1=9070` throughout. |
| Targeted replay | Ticks `902,949`, CPU direct, **556/556**. `GB5B_FINAL tick=949 upper=1d75d1be lower=9cb9639d rows=13`, matching `GB5_FINAL`. `run/replay-gb5b-target.log`. 60/60 `OUT` rows byte-match `run/replay-vq-p4-fold-direct.hashes`. |
| Changed rows | **13** packets, all corrected PATH3, 1,696 bytes, FNV `cc6dd8df`, each the first packet of its tick (902–905, 913–921). Cap 1,000 not approached. [crop-changes.csv](crop-changes.csv). |
| Non-packet timeline | 288 priv + 48 markers in range, 0 native/readback/clear, 239 transfers counted (metadata-only, not timeline rows). **0 gap rows**: no crop change between consecutively sampled same-tick packets. [timeline.csv](timeline.csv). |
| Recurrence | Independent walk: the identical 1,696 B / `cc6dd8df` packet occurs exactly once per tick at 900–951, always first of tick (tick-950 instance is X5/GB5 packet 144266, offset 158919448). 35 of the 48 probed ticks process it with no crop change. |
| pklog check | `[pk] idx=128702 tick=902`, `idx=129105 tick=905`, `idx=130913 tick=921`: all `fnv=cc6dd8df len=1696 src=3`, matching trace rows. Capture embedded path is 1 (known default-PATH1 metadata defect); replay used `run/gb4p4.paths.txt` true paths. |
| Display-page assumption | Holds: probe reads (which require `displayFbp=sourceFbp=112`) never failed over 15,564 sampled packets; `GB4_FRAME` shows 112 at 902/921/922/949 and all periodic markers. |
| Marker phase | Capture markers open their tick: marker-N PPM equals the pre-packet state of tick N (marker-902 upper `ecf3e93c` = before-hash of first packet 128702; marker-922/949 upper `1d75d1be` = post-921 state). |
| Omission (supplementary) | Dropped packet 130913 (tick 921, upper-final completer): **556/556**, `GB5B_FINAL tick=949 upper=1d75d1be lower=9cb9639d rows=14` — final hashes UNCHANGED. Ticks 922–923 repaint to the identical final state (new rows 131358/131819); all 60 `OUT` rows byte-match baseline (full reconvergence by tick 950). 0 gap rows. [drop-130913.csv](drop-130913.csv). Per the orchestrator checkpoint this is not claimed as the brief's single-producer control (13 rows, no isolated producer); it is evidence of per-tick redundant composite repaint. |
| Fork safety | `git diff --check` passed; `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner` empty before the source commit. Probe source is only `ps2xTest/src/ps2_gs_replay_tests.cpp`. |

## Tighter intervals (CPU display-page 112 crops)

| Crop | First final-state producer | Marker interval | Evidence |
| --- | --- | --- | --- |
| Lower `(340,360)-(430,420)` → `9cb9639d` | Packet 129105, tick 905 (full 5,400 px rewrite) | `(904,905]` | Final after 905; unchanged 906–949 (44 ticks, ~14k packets, 0 rows) |
| Upper `(320,120)-(420,205)` → `1d75d1be` | Packet 130913, tick 921 (1,548 px; completes pair) | `(920,921]` | Upper built over 902–905 (full rewrites) + 913–921 (~1,400 px/tick); unchanged 922–949 (28 ticks, ~13k packets, 0 rows) |
| Pair = `GB5_FINAL` | Complete after tick 921 | `(921,949]` stable | Consistent with GB5's 0 rows over 949–950 |

Viewed frames: periodic raw 100/200/300/500/600/700/800/850 (plus 899/900/901/949/950 saved) and target raw 902/921/922/949. At 902 the menu area is a pale transition (header only); at 921 the unhighlighted menu list is drawn; at 922 the Continue highlight bar lands; at 949 the full Zoe menu is stable.

## Why glyph attribution stays unresolved

- All 13 rows share byte-identical GIF input, yet the same input is a no-op on 35 sibling ticks. The crop effect depends on GS state set up elsewhere in the tick (scissor, frame/texture state, fade level), so a row's before/after hash is not a glyph-stroke producer.
- The 902–905 rows rewrite every crop pixel each tick (fade/composite behavior), and the recurring packet matches GB4 Part 6's tick-950 full-height sprite-composite candidate (32-pixel-wide strips over the glyph region).
- Zero gap rows exclude a between-packet crop change inside same-tick sequences, but do not exclude a priv/transfer/state setup role: 288 priv writes in range are listed in [timeline.csv](timeline.csv) for follow-up.

## Exact commands and budget

From `~/dev/ssx3-work/GB4/PS2Recomp` unless stated (`run/` = `~/dev/ssx3-work/GB4/run/`):

```sh
# Capture pin (two independent reads)
shasum -a 256 /Users/brad/dev/ssx3-work/GB4/run/gb4p4.capture.bin
sha256sum /Users/brad/dev/ssx3-work/GB4/run/gb4p4.capture.bin

# Build 1/2 + default suite (probe unset)
cmake --build build -j8 --target ps2x_tests > run/build-gb5b-1.log 2>&1
../build/ps2xTest/ps2x_tests > ../run/suite-gb5b-1.log 2>&1

# Replay 1/3: periodic PPM scan to 899
PS2X_GS_REPLAY_CAPTURE=../run/gb4p4.capture.bin PS2X_GS_REPLAY_PATH_FILE=../run/gb4p4.paths.txt PS2X_GS_REPLAY_STEP=50 PS2X_GS_REPLAY_PPM_TICKS=100,200,300,400,500,600,700,800,850,899 PS2X_GS_REPLAY_PPM_DIR=../run/gb5b-periodic-ppm PS2X_GS_REPLAY_RAW_PPM_DIR=../run/gb5b-periodic-raw-ppm ../build/ps2xTest/ps2x_tests > ../run/replay-gb5b-periodic.log 2>&1

# Replay 2/3: targeted probe over (901,949]
PS2X_GS_REPLAY_CAPTURE=../run/gb4p4.capture.bin PS2X_GS_REPLAY_PATH_FILE=../run/gb4p4.paths.txt PS2X_GS_REPLAY_STEP=50 PS2X_GS_REPLAY_PPM_TICKS=902,921,922,949 PS2X_GS_REPLAY_PPM_DIR=../run/gb5b-target-ppm PS2X_GS_REPLAY_RAW_PPM_DIR=../run/gb5b-target-raw-ppm PS2X_GS_REPLAY_GB5B_TRACE=../run/gb5b-crop-changes.csv PS2X_GS_REPLAY_GB5B_TICKS=902,949 PS2X_GS_REPLAY_OUT=../run/replay-vq-gb5b-target.hashes ../build/ps2xTest/ps2x_tests > ../run/replay-gb5b-target.log 2>&1

# Replay 3/3: supplementary omission of packet 130913 (launched before the
# orchestrator checkpoint; reported as redundancy evidence, not the gated control)
PS2X_GS_REPLAY_CAPTURE=../run/gb4p4.capture.bin PS2X_GS_REPLAY_PATH_FILE=../run/gb4p4.paths.txt PS2X_GS_REPLAY_STEP=50 PS2X_GS_REPLAY_GB5B_TRACE=../run/gb5b-drop-130913.csv PS2X_GS_REPLAY_GB5B_TICKS=902,949 PS2X_GS_REPLAY_GB5B_DROP=130913 PS2X_GS_REPLAY_OUT=../run/replay-vq-gb5b-drop.hashes ../build/ps2xTest/ps2x_tests > ../run/replay-gb5b-drop.log 2>&1
```

Replays used 3/3, builds 1/2 (correction unused), boots 0. New PPM output ≈ 19 MiB (cap 100 MiB); all new run data well below 2 GB. No mini/Odin/iOS use. No push.

## Probe notes and gaps

- `PS2X_GS_REPLAY_GB5B_TRACE` + `PS2X_GS_REPLAY_GB5B_TICKS=lo,hi` enable the range probe (direct CPU only, mutually exclusive with GB5); the timeline is written to `<trace>.timeline`. `PS2X_GS_REPLAY_GB5B_DROP=<index>` omits one packet's `processGIFPacket` (path note, counting and sampling preserved).
- Gap detection compares hashes only for consecutively sampled packets sharing a tick, so cross-tick parity changes cannot false-positive.
- Transfer metadata records (kind 3) are counted, not timeline rows: the replay treats them as audit-only no-ops reproduced by the preceding packet. No kind-5/6/7 records exist in this capture (independent walk: native=0, readbacks=0, clears=0); the probe timeline-logs them if present but crop-samples kind-1 only.
- No X5-style external per-packet index exists for 902–948; record numbering was verified post-hoc (independent binary walk + `paths.txt` + pklog spot lines above).
