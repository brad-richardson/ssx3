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
