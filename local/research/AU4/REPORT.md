# AU4 — PCSX2 EE sound mix comparison

Brief: `local/muse/prompts/AU4.md`. Worker: Codex. **Stopped at the hook/capture gate.** This is an incomplete capture, not a comparison verdict. PCSX2 produced no AU4 tag-1 records; the two-build budget was exhausted (first link failed, one fix build passed). No second build or capture was run.

## Outcome table

| Brief step | Result | Evidence |
| --- | --- | --- |
| PCSX2 hook | Built, env-gated at `sceSifSetDma` (syscall `0x77`), but **0 records** in the first run | `receipts/au4-hunk.diff`, `receipts/bytesize-final.txt` |
| Replay preservation | 7/7 PNG MD5 pins and HWSTAT exact; 0 AU4 lines with the env gate off | `receipts/replay-md5.txt`, `receipts/replay-hwstat.txt`, `receipts/replay-au4-lines.txt` |
| T48 route | Reached Select Character, passed TITLE/MENU/SC/ZC identity gates on try 1; manually ended before SP gate after detecting the empty hook | `receipts/au4a-poll.log`, `receipts/capture-ssh.log` |
| ≥150 s music into race | **Not achieved** | Partial video 119.57 s, no race |
| PCSX2 tag-1 WAV / AU2 alignment | **Not found / not run** | No `pcsx2-tag1.bin` |
| Bit-exact frames %, gain ratio, difference RMS/signal RMS, four spectral bands | **Not found** | No PCSX2 PCM |
| Seam ratio / zero crossings for both captures | **Not found** | Comparison stopped before analysis |
| Spectrogram pair PNG / first 100 PCSX2 tag records | **Not found / no records exist** | Hook wrote no records |
| AU3 93.75 Hz WAV | Not found in `~/dev/ssx3-work/AU3/run/` at inspection | No optional comparison |

AU2's au2b WAV and raw PCM do exist at `~/dev/ssx3-work/AU2/run/`. There is no correlation value or lag to report. The brief's `<0.5` alignment stop condition was not reached because there is no PCSX2 PCM to align.

## Pins and receipts

| Item | Value |
| --- | --- |
| PCSX2 source revision | `9056c08349cc29ad02a6d1a3a4133259019195af`, T65 and later T-lane working tree; preexisting modifications listed in `receipts/pcsx2-rev.txt` |
| AU4 touched source | `/home/brad/pcsx2-g7/pcsx2/pcsx2/R5900OpcodeImpl.cpp` only; pre-AU4 copy at `/home/brad/pcsx2-g7/pre-au4/R5900OpcodeImpl.cpp` |
| Pre-AU4 source SHA-256 | `c03f06b1c90e47fb36798160886173b3b16fa41cebb352037e2d6fb2be3b9f88` |
| Pre-AU4 qt SHA-256 | `46732713f198dbd4351cecdf2405a09d3d3f59b9e198999166d928cb674f5bbd` |
| AU4 qt SHA-256 ×2 | `69a537145d09a10634dbe2108ce2c7b8c0c980cdd50fef38c49c0a2c1946cd9a` both reads |
| AU4 gsrunner SHA-256 ×2 | `e603fa924ba740533fd2e572c43d5a3ab059548d8483a68e489fa7ec536bab03` both reads |
| Exact AU4 diff | `receipts/au4-hunk.diff`, SHA-256 `9c1b3342b4c0820aef6c5453fd033969ea5f67e0edf5216ce23c6a0fd929abba` |
| ISO SHA-256 ×2 | `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5` |
| BIOS trio | Two matching SHA reads in `receipts/input-sha-read1.txt` and `receipts/input-sha-read2.txt` |
| Partial PCSX2 video | `/home/brad/au4/dat/PCSX2/videos/SSX 3_SLUS-20772_20260923203515.mp4`, 51,053,067 B, SHA-256 ×2 `469e0f45f495b5e0388199e536ef2d77515a6a525bc99f28791028f77f057035`; mini copy `~/dev/ssx3-work/AU4/partial-video.mp4` same SHA |
| Partial listenable audio | `~/dev/ssx3-work/AU4/partial-pcsx2-audio.m4a`, AAC stream copied from PCSX2 video capture, 119.57 s, 3.0 MB, SHA-256 `3ba30388840fbbf88217f113b805c1a1e4b073d42942282d5a78472a49291695`; incomplete menu stretch |
| Byte use | `/home/brad/au4` 995 MB after partial run, mini AU4 workdir 273 MB; each below 6 GB cap |

## Build, preservation, and failed hook

`au4-apply-build.sh` copied the source and binary to `pre-au4/`, inserted the env-gated hook, and attempted the build. C++ compilation passed, but linking failed: `undefined symbol: R5900::Interpreter::OpcodeImpl::g_t65_ee_vsync` (`receipts/build.log`). The source had declared the T65 global inside the opcode namespace. `au4-fix-build.sh` moved the declaration to global scope, qualified its use, and the retry linked both targets (`receipts/build2.log`). This used two builds.

The replay ran the new gsrunner on the G13 rich dump with no arm files and `PCSX2_AU4_CAPTURE` unset. PNG MD5 prefixes were `b7a3e8db`, `a7929218`, `bb8b1d85`, `817e934f` twice, `85cf3599` twice, matching T65. HWSTAT was 791 draws, 37 passes, 0 barriers, 14 copies, 320 uploads, 6 readbacks, exact. The replay emulog has 0 AU4 lines.

The hook filtered for SIF descriptor `src == 0x512E40` and read tag 1 at that address. The AU2 raw transport log instead records the SND DMA descriptor source as **`0x512B80`, size 2288 (`0x8F0`)** (`receipts/au2-source.txt`). `0x512E40` is the **tag-1 record address**, offset `0x2C0` into that DMA buffer. That filter mismatch is the likely reason for zero records. PCSX2's live descriptor value was not independently logged, so this remains a diagnosis to verify in a follow-up, not a PCSX2-side measurement.

The first capture passed the available route gates and PCSX2 wrote an MP4 with audio using its `ToggleVideoCapture` hotkey bound to F12 in AU4's copied INI. The runner was ended by PID after the empty hook was found; Xvfb was then stopped. The resulting `SNAP_SP` error in `capture-ssh.log` is the expected consequence of that manual stop, not a game crash. There was one partial capture and no boot beyond 600 s.

## Exact commands and locations

From `~/dev/ssx3`, the bytesize scripts were sent with `ssh bytesize "wsl -d Ubuntu -- bash -s" < local/research/AU4/<script>`. In order: `au4-apply-build.sh`, `au4-fix-build.sh`, `au4-replay.sh`, `au4-setup.sh`, `au4-precap.sh`, `au4-cap.sh`, `au4-stop-first.sh`, then the retrieval scripts. The build command was `cmake --build /home/brad/pcsx2-g7/pcsx2/build --target pcsx2-qt pcsx2-gsrunner -j2`. `au4-replay.sh` records the exact gsrunner invocation. `au4-cap.sh` records the T48/T65 route and 560 s wall cap; its output is `receipts/capture-ssh.log` and `receipts/au4a-poll.log`. All pre-build, pre-replay, and pre-capture bytesize heavy-job checks were empty (`receipts/*jobs.txt`). PCSX2 video audio was extracted on the mini with `ffmpeg -i partial-video.mp4 -vn -c:a copy partial-pcsx2-audio.m4a`.

No audio, ISO, game data, or binaries are committed. The large incomplete emulog and video remain under `/home/brad/au4/`; the video and `.m4a` mini copies remain under `~/dev/ssx3-work/AU4/`.

## Recommended next action for the orchestrator

Issue a new, bounded PCSX2 capture brief. First log the live SIF DMA descriptor once to confirm `src`, `size`, and the tag-1 layout. Then filter `src == 0x512B80`, read tag 1 at `src + 0x2C0`, and repeat one build, replay proof, full route capture, and AU2 comparison. AU4's original build/capture budget is exhausted; the remaining comparison fields must stay unreported until that capture exists.

# Part 2 — corrected descriptor hook and full reference capture

Brad approved one additional PCSX2 build and one full capture after the Part 1 address error. The results below supersede Part 1's missing comparison fields. The Part 1 stop and receipts remain above as the failure history. Part 2 used **one build and one capture**; it did not push the PCSX2 tree.

## Part 2 hook and preservation

The patch in `receipts/part2/part2-hunk.diff` (SHA-256 `4f30699d4102715f1acc7f8c9d762e7e7325e7f4ef09dd4b9863e5de9aeb019b`) changed only `/home/brad/pcsx2-g7/pcsx2/pcsx2/R5900OpcodeImpl.cpp`. The Part 1 source was copied to `/home/brad/pcsx2-g7/pre-au4/R5900OpcodeImpl.cpp.part1` before editing. The hook now logs the first sound descriptor at `0x50C800` before filtering, accepts `src == 0x512B80` and `size >= 0x8E0`, and reads the 0x620-byte tag-1 record from `src + 0x2C0`. Before every write it checks all four tag-1 header words `{1, 0x600, 0, 0}` and the following tag-5 ID. It writes a 4-byte EE vsync followed by the 0x620 record, env-gated by `PCSX2_AU4_CAPTURE`.

| Check | Part 2 result | Receipt |
| --- | --- | --- |
| Live SIF descriptor | `desc=0x50C800 src=0x512B80 size=0x8F0 dst=0x61CF4`; `AU4_TAG_OPEN ... ok=1` | `receipts/part2/part2-hook-lines.txt` |
| PCSX2 qt SHA-256, two matching reads | `9b7e72e7b1c01851eb8a14fbfe07f32fb12e4ecbf02867a78b436ab789974e5b` | `part2-bin-sha-read1/2.txt` |
| PCSX2 gsrunner SHA-256, two matching reads | `764f1ca95c53ae4b55263752608c06fa9185ea15a476a9d9b45e5626ba66cb72` | same |
| Replay PNG MD5 | **7/7** exact T65 pins: `b7a3e8db a7929218 bb8b1d85 817e934f 817e934f 85cf3599 85cf3599` | `receipts/part2/replay-md5.txt` |
| Replay HWSTAT | **Exact:** 791 draws / 37 passes / 0 barriers / 14 copies / 320 uploads / 6 readbacks | `receipts/part2/replay-hwstat.txt` |
| AU4 replay lines with gate off | 0 | `receipts/part2/replay-au4-lines.txt` |

The source revision remained `9056c08349cc29ad02a6d1a3a4133259019195af` plus the preexisting T-lane working tree and the local AU4 hunks. The Part 2 build succeeded on the first attempt (`receipts/part2/part2-build.log`). The replay ran with no arm files and with `PCSX2_AU4_CAPTURE` unset.

## Part 2 full capture

The T48/T65 closed-loop route passed TITLE, MENU, SC, ZC, SP, SM, Happiness SE, Rules, and race-entry gates. The race-entry screen differed from Rules by mean 12.6956; a race F8 was taken. `SC_RECORDS=17122` at the settled Select Character screen. The final raw file has 39,888 records, so it contains **22,766 records = 242.84 s of 36 kHz PCM after that screen**, including the route into the race. Video capture audio started before the title gate and stopped after race entry. The boot ran ~320 wall seconds under the 560 s script cap and the 600 s standing cap. See `receipts/part2/au4b-poll.log` and `capture-ssh.log`.

| Capture | Pin / location |
| --- | --- |
| PCSX2 tag records | `/home/brad/au4/pcsx2-tag1.bin`; mini copy `~/dev/ssx3-work/AU4/pcsx2-tag1.bin`; 62,703,936 B; SHA-256 ×2 on bytesize and matching mini read `ebd23468999cc733f5ad305e5000881cb25e458decf247bf41f6a8b0e66f8dec` |
| Layout and serials | 39,888 valid records, 39,888 unique serials 1–39,888, 0 duplicates, 0 serial gaps; EE vsync 1,228–26,730. The 4-byte vsync prefix makes each record 0x624 bytes. |
| Derived tag-1 WAV | `~/dev/ssx3-work/AU4/pcsx2-tag1-36k.wav`, stereo s16 36 kHz, 425.472 s; SHA-256 `4c97b6328387599fba1f172f6089baf3e158911b6ad3ecdd27ad599fc2541acf` |
| PCSX2 video | `/home/brad/au4/dat/PCSX2/videos/SSX 3_SLUS-20772_20260923204445.mp4`; mini copy `~/dev/ssx3-work/AU4/pcsx2-full-video.mp4`; 224,187,770 B; SHA-256 ×2 on bytesize and matching mini read `0d691ccb8bf44756e0c5a6c952238b92dcfeec3e81ac946a827a44529a53828a` |
| Listenable PCSX2 audio | PCSX2's F12 `ToggleVideoCapture` MP4 audio, extracted with `ffmpeg -vn -c:a aac -b:a 96k -movflags +faststart` to `~/dev/ssx3-work/AU4/pcsx2-full-audio.m4a`; **310.976 s, 3,927,149 B (<5 MB)**, SHA-256 `5f5634449953f72966ba08a875b9a80fb94ccf6cb0e9f1d1d530d8e34913b40f` |
| Byte use | `/home/brad/au4` 2.9 GB including Part 1 residue and the bounded Part 2 emulog (1,519,165,177 B), below the 6 GB cap. |

The tag-1 WAV is the EE transport mix used for the numeric comparison. The `.m4a` is PCSX2's final listenable output and has its own capture clock; its duration differs from the concatenated 36 kHz tag record duration. Audio and game data are left in the work directories, not committed.

## Part 2 comparison: menu music

`compare.py` checks the tag layout, de-duplicates on serial, writes the PCSX2 WAV, and uses normalized waveform cross-correlation to find the shared menu music. AU2's raw `pcm-au2b.bin` has 13,963 valid unique records with no gaps; reconstituting it produces the **exact existing au2b WAV** (SHA-256 `2cd31f2cb34c26e394dffe2921bf0206d130bee00efb4f078a52d96ed4fbf406`). The strongest 5 s menu excerpt gave coarse correlation **0.98972**. A 1 s sample-resolution refinement gave **0.97331** at **PCSX2 lag +111.061556 s** (AU2 21–22 s maps to PCSX2 132.061556–133.061556 s). This clears the brief's 0.5 alignment gate. The measured table uses AU2 **5–35 s** and PCSX2 **116.061556–146.061556 s**, both within the menu section. Fixed-lag 5 s correlations over this span are 0.826–0.979 (`receipts/part2/menu-window-check.txt`).

| Measure over the aligned 30 s menu excerpt | AU2 au2b | PCSX2 | Difference / relationship |
| --- | ---: | ---: | ---: |
| Bit-exact stereo frames | — | — | **0.0503%** |
| RMS, s16 units | 4,884.52 | 4,754.21 | AU2/PCSX2 gain ratio **1.02741**; least-squares fitted gain **0.96658** |
| RMS difference / PCSX2 RMS | — | — | **0.34988** |
| Mean 384-frame seam delta / other delta | **1.26841** | **1.10758** | AU2 exceeds PCSX2 by 0.16083 |
| Zero crossings/s, both channels combined | **5,117.97** | **5,339.23** | — |
| Peak absolute sample | 32,652 | 28,424 | — |

| Difference band | Difference RMS, s16 units | PCSX2 band RMS | Difference / PCSX2 band RMS |
| --- | ---: | ---: | ---: |
| 0–2 kHz | 1,332.51 | 4,575.93 | **0.29120** |
| 2–6 kHz | 767.09 | 1,062.38 | **0.72206** |
| 6–12 kHz | 510.55 | 650.70 | **0.78463** |
| 12–18 kHz | 377.11 | 333.55 | **1.13062** |

Definitions: bit-exact means both s16 channels match at a frame; gain ratio is AU2 RMS / PCSX2 RMS; difference RMS is from direct aligned subtraction without gain correction. Seam ratio is the mean absolute adjacent-sample delta at each capture's own 384-frame record boundary divided by the mean elsewhere. Zero crossings count sign changes across both channels. The band table uses one-sided FFT energy over the aligned difference and PCSX2 signal. The numerical receipt is `receipts/part2/comparison.json`. The equal-scale spectrogram pair is `receipts/part2/menu-spectrogram-pair.png` (1.4 MB, below 5 MB); the first 100 tag records' stats from each side are also in that receipt directory.

The available race footage is relatively short after the long T48 menu route, and AU2's race track/position was not established as the same PCSX2 track. A search of four AU2 race excerpts against the last 90 s of PCSX2 PCM produced maximum absolute normalized correlations only 0.125–0.131 (`receipts/part2/race-alignment-check.txt`); this does not establish a common race waveform. Thus the pairwise table is limited to the menu, as the brief permits for differing EA Radio tracks. This is an alignment limit, not evidence about race mix quality.

Two SHA-256 reads of the AU2 raw input (`1e34ea47d16582b5f403279b8db3dfd0eea4ae92b56caabe51fefd9c0609d2bf`) and WAV (`2cd31f2c…f406`) matched (`receipts/part2/au2-input-sha-read1/2.txt`). AU3's host-stream WAV was still **not found** in `~/dev/ssx3-work/AU3/run/` when Part 2 analysis finished; the optional AU3 comparison was not run.

## Part 2 commands, receipts, and recommendation

From `~/dev/ssx3`: `ssh bytesize "wsl -d Ubuntu -- bash -s" < local/research/AU4/au4-part2-build.sh` (one build), then the existing `au4-replay.sh` (one replay), then `au4-part2-cap.sh` (one boot/capture, redirected to `~/dev/ssx3-work/AU4/part2-capture-ssh.log`). The exact capture script includes its progress/size caps and all route gates. `au4-part2-get-tag.sh` and `au4-part2-get-video.sh` perform two SHA reads before transfer; `au4-part2-get-receipts.sh` retrieves the text proof. The analysis command was `/Users/brad/dev/ssx3-work/AU4/venv/bin/python local/research/AU4/compare.py --pcsx2-bin /Users/brad/dev/ssx3-work/AU4/pcsx2-tag1.bin --au2-bin /Users/brad/dev/ssx3-work/AU2/run/pcm-au2b.bin --au2-wav /Users/brad/dev/ssx3-work/AU2/run/au2b-ee-mix-36k.wav --out /Users/brad/dev/ssx3-work/AU4 --pc-sc-record 17122`. The bytesize heavy-job checks were empty before build, replay, and capture. No mini P-lane lease was needed for PCSX2 on bytesize.

**Recommended next action for the orchestrator:** use the strong menu alignment and the frequency-band table to choose a bounded EE decode/mix arithmetic check, while separately checking why AU2's tick seam ratio is higher. The aligned error exists across the menu waveform, with especially large relative 2–18 kHz differences; the seam ratio alone does not account for the full 0.34988 difference RMS. No causal verdict is declared by this worker.

# Part 3 — local lag and residual analysis

This is analysis of the Part 2 inputs only. No build, capture, device run, or bytesize command was used. `lag_track.py` reuses `compare.py`'s WAV reader, rate, and SHA helper in the existing AU4 venv. The input SHA-256 reads match twice (`receipts/part3/input-sha-read1.txt`, `input-sha-read2.txt`): AU2 `2cd31f2cb34c26e394dffe2921bf0206d130bee00efb4f078a52d96ed4fbf406`, PCSX2 `4c97b6328387599fba1f172f6089baf3e158911b6ad3ecdd27ad599fc2541acf`.

The shared menu waveform is AU2 **8.75–41.0 s**, PCSX2 **119.811556–152.061556 s**, using the Part 2 base lag of **+111.061556 s** (PCSX2 time minus AU2 time). Before ~8.5 s and after ~41 s the local correlation drops toward unrelated audio; these edges are excluded. A short region around AU2 15–16.7 s has intermittent low correlation within the menu and is retained in the full-span sensitivity calculation. Each local fit uses a 50 ms stereo window, 25 ms hop, normalized cross-correlation over ±20 ms around the base lag, and a three-point parabolic interpolation of the peak. The reliable subset has NCC ≥0.8. `receipts/part3/lag-windows.csv` contains all 1,289 fits; `receipts/part3/menu-lag-vs-time.png` (71 KB) plots both the full search range and a zoom of reliable fits.

| Lag tracking measure | Result |
| --- | ---: |
| Windows: all / NCC ≥0.8 / NCC <0.8 | 1,289 / 1,226 / 63 |
| Median reliable NCC | 0.97538 |
| Median reliable local lag | **+111.061560 s** (base +0.00427 ms) |
| Reliable 5th–95th percentile lag offset from base | −0.01892 to +0.00709 ms; spread **0.02602 ms** (0.94 sample) |
| Reliable local extrema | −0.20851 to +0.00950 ms from base; the negative extremes are isolated, not plateaus |
| First/last 5 s median offset | +0.00412 / +0.00421 ms; difference +0.00009 ms |
| Largest adjacent half-second median change | 0.159 sample = 0.00442 ms |
| Sustained jumps ≥1 sample (0.02778 ms) | **0**; size: none |
| Jump relation to 384-frame seams or 59.94 Hz tick | No sustained jumps to align with either |

Jump rule: take each half-second bin's median only when it contains at least 10 NCC ≥0.8 windows; count a jump if adjacent medians differ by at least one sample and the shift persists in the next bin. The 50 ms windows overlap multiple 384-frame record boundaries. Each AU2 record was also produced by one 59.94 Hz spike tick, so record seams and tick events are the same sequence indexed by different clocks (10.667 ms in concatenated 36 kHz PCM versus 16.683 ms in AU2 wall time). These WAVs and this window cadence cannot assign an isolated excursion to one clock rather than the other. The low-NCC windows include search-limit outliers and are not evidence of timing slips.

The following ratios use the same windows before and after local correction. Each corrected PCSX2 window is sampled at its fractional fitted lag with cubic interpolation; the difference is AU2 minus PCSX2, with **no gain correction**. Each 50 ms window contributes its one-sided FFT energy, including overlapped samples. The reliable subset isolates positions where local timing can be estimated; the full-span row keeps the intermittent low-correlation region.

| Difference band / PCSX2 band RMS | Fixed Part 2 lag, reliable | Per-window lag, reliable | Per-window lag, all windows |
| --- | ---: | ---: | ---: |
| 0–2 kHz | 0.18769 | **0.18623** | 0.25840 |
| 2–6 kHz | 0.54912 | **0.52081** | 0.60729 |
| 6–12 kHz | 0.65837 | **0.56602** | 0.61259 |
| 12–18 kHz | 1.04373 | **1.06076** | 1.09033 |
| Whole-band RMS difference / PCSX2 RMS | 0.24306 | **0.23328** | 0.30077 (fixed: 0.30861) |

The lag is effectively constant across the correlated menu music. Per-window timing correction reduces the reliable whole-band error only from 0.24306 to 0.23328; substantial error remains in every band. This supports a waveform/arithmetic cause as the main explanation for the audible distortion, rather than cumulative drift or persistent sample-position jumps. It does not identify which decode or mix operation differs, and it cannot exclude within-record timing defects shorter than the 50 ms analysis window.

`~/dev/ssx3-work/AU3/run/` **did not exist** after the PCSX2 lag analysis, so there was no AU3 host-stream WAV on which to run the Part 2 table or lag tracking. The preexisting modified AU3 report was left untouched.

Reproduce from `~/dev/ssx3`:

```sh
MPLCONFIGDIR=/Users/brad/dev/ssx3-work/AU4/mpl-cache /Users/brad/dev/ssx3-work/AU4/venv/bin/python local/research/AU4/lag_track.py \
  --au2 /Users/brad/dev/ssx3-work/AU2/run/au2b-ee-mix-36k.wav \
  --target /Users/brad/dev/ssx3-work/AU4/pcsx2-tag1-36k.wav \
  --out /Users/brad/dev/ssx3-work/AU4
```

The detailed numerical output is `receipts/part3/lag-analysis.json`; the script, CSV, JSON, and PNG are committed under `local/research/AU4/`. The audio remains in the work directories.
