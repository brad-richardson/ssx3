# AU6 — EE mix loudness differential

Worker: Codex. Brief: `local/muse/prompts/AU6.md`; orchestrator H4 addendum included. Tables and receipts for the orchestrator; no push.

## Result and limits

**The controlled menu EE mix does not reproduce AU5's ~12 dB deficit.** With the E33 two-input route, our tag-1 PCM matches PCSX2's *same waveform* for 59 continuous seconds (AU6 5–64 s; PCSX2 113.96–172.96 s). The full-span RMS is **5,010.02 ours / 5,002.05 PCSX2**, ratio 1.00159 or **+0.0138 dB**. Every aligned 5 s bin from 10–60 s is within +0.010 to +0.020 dB. The first 5–10 s fade-in bin is +0.095 dB. This comparison uses matched 36 kHz stereo s16 EE transport PCM, not a wall-time host playback level. `receipts/aligned-profile.json` and `receipts/comparison.json` hold the numbers.

AU5's boot wrapper did not set `PS2X_PAD_SCRIPT`; its tag-1 stayed at ~1,300–1,500 RMS after 10 s. AU6 armed the E33 vsync route (`start` at 10.350 guest s, `cross` at 20.650 guest s; both fired in `run/boot.log`). AU5 and AU6 both measured ~1,300 RMS at 5–10 s, then AU6 rose after the route input. Thus the **AU5-to-PCSX2 loudness comparison mixed different content/states**. The route is the named experimental difference; these captures do not show a global EE gain error. This does not establish Brad's perceived race or host-output symptom as solved: neither was pairwise captured here.

AU4 `compare.py` independently reported a 20–25 s coarse NCC 0.999951 and 1 s refined NCC 0.998775 at lag +108.960 s (PCSX2 time minus ours). Its fixed 30 s subtraction (ours 5–35 s) gives gain 1.001647, difference RMS / PCSX2 RMS 0.09543, and 0.131% bit-exact stereo frames. The residual is still above AU5's <0.02 arithmetic gate, especially above 2 kHz; it is a separate waveform-fidelity issue, not a 12 dB level deficit. The 59 s span is defined by consecutive 1 s windows with normalized correlation ≥0.8; whole-span NCC is 0.99568 and difference RMS / PCSX2 RMS is 0.09301.

| Step / gate | Observation | Receipt |
| --- | --- | --- |
| PCSX2 status, first 2,000 ticks | 2,000 serials 1–2,000, no gaps. Only serial words, `+0x004`, and 16 fixed `0xffffffff` words are nonzero. | `receipts/status-fields.tsv`; `~/dev/ssx3-work/AU6/pcsx2-status.json` |
| Same menu mixer state | Both: 16 allocated slots, 6 active type-2 voice/source pairs (slots 10–15); matching source functions, pointers and levels to ≤1 float ULP. | `receipts/mixer-state.tsv` |
| H4 stream-reader check | Neither snapshot contains a live object whose first callback is `0x3C9520` (nor `0x3C95F0`). Both have six `0x3CA460`/`0x3CA5E8` source objects attached to the six active voices, whose callbacks point to `0x3CB540`. The six source objects must not be called six separate MPF tracks without further decoding. | `receipts/mixer-state.tsv`; full 32 MiB snapshots remain outside Git |
| Menu CD reads near snapshot | PCSX2 46 reads, ours 47 within ±200 guest vsyncs. Both have 21×15-sector, 1×16-sector and ~24×1-sector reads in one MUSIC2-region LBN band, with two small backward jumps each. No second independent LBN band is visible in those windows. | `receipts/cd-window.tsv`; text traces in AU6 workdir |
| PCSX2 route/capture | Select Character identity gate passed; `SC_RECORDS=17167`; 20,195 raw tag-1 records; status 1,160,000 bytes; EE snapshot 33,554,432 bytes. Capture ended at 151 s wall. | `receipts/pcsx2-poll.log` |
| Mac build/test/boot | One Release build; `ps2x_tests` 541/541 from fork root. One leased boot, slot 1, target bound 193.588 s, runner rc 0, lease released; 6,001 valid consecutive tag records, 64.011 s PCM. | `receipts/boot-wrap.log`; `~/dev/ssx3-work/AU6/suite.log` |
| Audio copy | `~/dev/ssx3-work/AU6/AU6-menu-tag1.m4a`, AAC 96 kb/s, 845,469 B (<5 MB), diagnostic menu capture. | `receipts/artifact-sha-read1/2.txt` |

## Step 1: status block at EE `0x50B740`

PCSX2 hook writes `{u32 tag serial, 0x240-byte EE block}` at the tag-buffer DMA syscall for serials 1–2,000. At record serial 1, status serials `+0/+0x23c` are 0; at record 2,000 they are 1,999 (the IOP status precedes the EE DMA by one tick). HLE stamps the current serial at these offsets. PCSX2's `+0x004` is initially zero, changes first at serial 57, then 20 more times, roughly every 93–94 ticks, ending at `0x00072da2`. Offsets `+0x1c0,+0x1c8,…,+0x238` are `0xffffffff` in all 2,000 records. Every other aligned word is zero. Their SNDDRV semantics were not established from the disassembly, so no field was copied into HLE. At the later menu snapshots, PCSX2 has these same nonzero classes while ours has zero outside the serial words. Equal voice state and PCM gain despite this disparity are evidence against these words causing the measured menu level.

## Step 2: mixer and stream differential

`0x515B40+0x1DC` points to a 16-entry, 0x60-byte voice table (`0x00AFBAE0` in both snapshots); `+0x04/+0x05` encode 16/2. `0x3C85D0` walks entries, and `0x3C8968` calls it; the type-2 entries 10–15 link through `+0x40` to callbacks and `+0x48` to source objects. Static EE source: `ee-at 0x3C85D0`, `ee-at 0x3C8968`, `ee-at 0x3CB540`; AU5's function chain. The loop object constructor `0x3C9618` stores `0x3C9520/0x3C95F0` at object `+0/+4`; neither snapshot has that signature. Those loop readers may matter in a race, which was not captured here.

| Voice | PCSX2 L/R level | Ours L/R level | Source object | Source `+0x28` PC / ours |
| ---: | --- | --- | --- | ---: |
| 10 | 0 / 0.698741257 | 0 / 0.698741257 | `0x00AFC2E0` | 1683 / 16 |
| 11 | 0.495969236 / same | 0.495969206 / same | `0x00AFC3D0` | 1683 / 16 |
| 12 | 0.698741257 / 0 | same | `0x00AFC4C0` | 1683 / 16 |
| 13 | 0 / 0.698741257 | same | `0x00AFC5B0` | 1683 / 16 |
| 14 | 0.698741257 / 0 | same | `0x00AFC6A0` | 1683 / 16 |
| 15 | 0 / 0 | same | `0x00AFC790` | 1683 / 16 |

All six source objects have `0x3CA460/0x3CA5E8` at `+0/+4`. Their `+0x28` position differs because the two snapshots are at different music phases (PCSX2 tag serial 18,000, vsync 12,736; ours serial 2,000, vsync 1,344), not because one stopped reading. The PCSX2 and runtime CD windows each show the same 1/15-sector pattern and two backward seeks; filenames are unavailable in the raw CD traces, so the exact MPF section count remains unproved. The read LBAs fall in the MUSIC2 region identified in AU2, with the charsel material active along the menu route.

## Step 3: before/after profile and decision point

The PC column is shifted by the measured +108.960 s audio lag; AU5 is the earlier **unrouted** capture, so its values after the transition are not same-content gain ratios.

| Ours capture s | AU5 RMS | AU6 RMS | Aligned PCSX2 RMS | AU6/PC gain dB |
| ---: | ---: | ---: | ---: | ---: |
| 5–10 | 1,294 | 1,310 | 1,296 | +0.095 |
| 10–15 | 1,431 | 3,960 | 3,951 | +0.020 |
| 15–20 | 1,455 | 4,983 | 4,975 | +0.014 |
| 20–25 | 1,271 | 5,185 | 5,180 | +0.010 |
| 25–30 | 1,478 | 4,857 | 4,851 | +0.010 |
| 30–35 | 1,386 | 5,109 | 5,100 | +0.014 |
| 45–50 | 1,355 | 5,509 | 5,500 | +0.014 |
| 50–55 | 1,395 | 5,735 | 5,725 | +0.016 |

No code-level volume or missing-voice mechanism is supported in the controlled menu. Consequently no HLE status-field or mixer candidate fix, nor a post-fix validation boot, was attempted. The current E33 route capture is the diagnostic validation of AU5's level comparison. The M4A is labeled as that diagnostic capture.

**Recommended next action for the orchestrator:** if Brad's audible “half the audio” remains, replay the exact perceived scene and compare the *host-output WAV* with tag-1 PCM and PCSX2 at matched content, especially a race. The menu EE gain result here does not justify changing status fields or voice volumes. Keep the >2 kHz waveform residual as a separate arithmetic investigation.

## Pins, budgets, commands, and gaps

| Item | Value |
| --- | --- |
| Fork | AU5 `au5-snd` `ddf4f66` → AU6 local `au6-snd` `045dd6a`, no push. Default-off `PS2X_AU6_EE_SNAP` only. Generated code is external AU5 codegen. |
| PCSX2 source | `/home/brad/pcsx2-g7/pcsx2` `9056c08349cc29ad02a6d1a3a4133259019195af` plus pre-existing AU4/T65 hooks; new AU6 hunk in `receipts/pcsx2-hunk.diff`; pre-hunk copy `/home/brad/pcsx2-g7/pre-au6/R5900OpcodeImpl.cpp`. No upstream contact or push. |
| PCSX2 builds/captures | 2 builds (second fixed the AU4 tag output path to `/home/brad/au6/`), 1 actual capture. The first preflight detected its own process; fixed before launch. A missing log directory then prevented launch; fixed before the actual boot. |
| Mac builds/boots | 1 build, 1 leased boot, 541/541 suite. Under ≤3 builds/boots. |
| Disk | `~/dev/ssx3-work/AU6` below 6 GB; bytesize `/home/brad/au6` 984 MB; mini total below 200 GB. |
| PCSX2 binary SHA-256 | `a0bb7b27032d231771ce8138c649933bcf8d9661bd67debaf3616c6de3a77de5` |
| Mac runner SHA-256 | `1054cdef713f5e109ce32f3b66c8b716fb6535440836da0a45f32994f822ee9a` |
| ISO SHA-256 | `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5` |
| PCSX2 tag/status/snapshot SHA-256 | `ce0a9637df1f1b14695b178d12cba3f47e8cd69d477ba070ec58721bc69a276d` / `67342dd5ff9f2f9765d0c82f43855f5737d41ed14dded107208b7ee96d03c5e5` / `fe5224aae349e1afdd879163fc0b9bb329b865ec6b8ddb456acd1b508f506952` |
| Ours tag/snapshot SHA-256 | `f87b616a29c00b2d20e28c969be37695b92ba35e53d24adcca190c98a1bc1d06` / `c863dfff7da89f0a1b1e4587e4e9f3cafdbeb4dc8ea4427db1a0e71e92f443cc` |
| M4A SHA-256 | `35d64f13f81e2dce98d394a158eccdd2c182a2576c92ec250984f4c69f92d19c` |

Runner, ELF, ISO, PCSX2 binary, captured inputs and audio artifacts had two matching SHA-256 reads; paired text receipts are under `receipts/*sha-read1/2.txt`. The PC raw transfers matched their remote SHAs. The PCSX2 pre-hunk source has one SHA record, for provenance rather than a binary-use gate. No full memory snapshots, PCM, ISO, generated code, or binary is in Git.

Reproduction commands (fork tests run from its worktree root, not the build directory):

```sh
ssh bytesize 'wsl -d Ubuntu -- bash -lc "bash /home/brad/au6/pcsx2_build.sh"'
ssh bytesize 'wsl -d Ubuntu -- bash -lc "python3 /home/brad/au6/pcsx2_fix_path.py && cmake --build /home/brad/pcsx2-g7/pcsx2/build --target pcsx2-qt -j2"'
ssh bytesize 'wsl -d Ubuntu -- bash -lc "bash /home/brad/au6/pcsx2_cap.sh"'
zsh /Users/brad/dev/ssx3-work/AU6/build.sh
(cd /Users/brad/dev/ssx3-work/AU6/PS2Recomp && /Users/brad/dev/ssx3-work/AU6/build/ps2xTest/ps2x_tests)
python3 /Users/brad/dev/ssx3-work/AU6/boot.py
python3 local/research/AU2/au2_pcmcap.py /Users/brad/dev/ssx3-work/AU6/run/tag1.bin /Users/brad/dev/ssx3-work/AU6/run/tag1-36k.wav
MPLCONFIGDIR=/Users/brad/dev/ssx3-work/AU6/mpl-cache /Users/brad/dev/ssx3-work/AU4/venv/bin/python local/research/AU4/compare.py --pcsx2-bin /Users/brad/dev/ssx3-work/AU6/pcsx2-tag1.bin --au2-bin /Users/brad/dev/ssx3-work/AU6/run/tag1.bin --au2-wav /Users/brad/dev/ssx3-work/AU6/run/tag1-36k.wav --out /Users/brad/dev/ssx3-work/AU6/compare --pc-sc-record 17167
/Users/brad/dev/ssx3-work/AU4/venv/bin/python /Users/brad/dev/ssx3-work/AU6/analyze_pcm.py
ffmpeg -hide_banner -loglevel error -y -i /Users/brad/dev/ssx3-work/AU6/run/tag1-36k.wav -c:a aac -b:a 96k -movflags +faststart /Users/brad/dev/ssx3-work/AU6/AU6-menu-tag1.m4a
```

The PCSX2 script/hunk sources and Mac analysis scripts are retained in `~/dev/ssx3-work/AU6/` and selected text copies are in `receipts/`. PCSX2's existing AU4 capture path is preserved when AU6's env gate is off. Gaps: source-object-to-MPF-section identity, race stream/loudness comparison, host-output playback level, and the high-frequency arithmetic residual.
