# AU5 — EE sound mix arithmetic

Worker: Codex. Brief: `local/muse/prompts/AU5.md`. Tables and receipts for the orchestrator; no push.

## Pins and gates

| Item | Result / receipt |
| --- | --- |
| Fork | E58 `fork/ssx3` `b9647f5`; AU3 cherry-picks `7c2a02e` → `5bb1fdd`, `d2096ee` → `83167d6`, `c19a5d6` → `3c895ca`; local AU5 branch `au5-snd` at `ddf4f66` (`Orchestrated-By: Codex`). |
| Changes | Added `0x3C9518`, `0x3C9520`, `0x3C95F0` to `extra_function_starts`; kept the host WAV valid on disk across bounded SIGTERM boots; corrected the host tag-1 parser's PCM offset from `+8` to `+16` and its test; added bounded, default-off `PS2X_SND_TAG1` raw-record tap. |
| Codegen | `~/dev/ssx3-work/AU5/codegen` from `ssx3-au5.toml` with E52 recompiler. It reported `20/22` configured extra starts resolved; the generated registration table contains all three requested addresses. `receipts/regen-head.txt`. |
| Build/suite | **3 Release/Ninja builds**, nice'd; `PS2X_ENABLE_DIAG_TAPS=OFF`, runtime/aggressive logs OFF. All linked; suite after each **541/541 passed**, 0 failed. Third build has an env-gated decoder tap inserted only into the external generated `.cpp` by `~/dev/ssx3-work/AU5/instrument_decode.py`. Logs and CMake cache in AU5 workdir; final suite receipt `receipts/suite-summary.txt`. |
| Boots | **2** one-slot mini boots, 97.853 s and 19.173 s, target-bound with runner rc 0. Both leases released. `receipts/boot1-result.json`, `receipts/boot2-result.json`. No debugger. |
| Disk / runner dir | AU5 workdir below 1 GB; internal ssx3 usage below 200 GB. `git diff --stat 14b1e5cb au5-snd -- ps2xRuntime/src/runner` empty. Generated code, game bytes, binaries, WAV, and M4A remain outside Git. |

Pinned ELF, map CSV, recompiler, ISO, and both runners had two matching SHA-256 reads before use. Matching reads of captured inputs and artifacts are in `receipts/*sha-read1.txt` and `*sha-read2.txt`.

| Input/artifact | SHA-256 |
| --- | --- |
| Capture runner (build 2) | `5555cc3f1c611ce237662a9eac6ea569098905d18cef1c1362067e9f6763a5e4` |
| Differential runner (build 3) | `b05727056639f7552c83d023e7db30a71616fffb60c3132ed8ea9eeaff1547a0` |
| ISO | `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5` |
| AU5 raw tag-1 | `e5ee95c5ff5718ef37814e39f064712f9f0b8fded5fb96bd1405db9d15c8bdff` |
| AU5 tag-1 WAV | `f4668e3c14d00b27e2ea94b56cce7cc1e2ff13b54a3f8b39055ae409c73c7559` |
| PCSX2 raw tag-1 | `ebd23468999cc733f5ad305e5000881cb25e458decf247bf41f6a8b0e66f8dec` |
| AU5 M4A | `754c510fb3d0174cfdf39a5d6902799d1403b2cda8b7146750404a0ce08c1d6d` |

## Step 1 — capture and comparison

Boot 1 captured **5,047** consecutive valid 0x620-byte tag-1 records (serials 1–5,047; 0 gaps/duplicates), or **53.835 s** of 36 kHz stereo s16 PCM. 4,626 records are non-silent. `au2_pcmcap.py` accepted every record and wrote `~/dev/ssx3-work/AU5/run/tag1-36k.wav`. The host callback WAV is also valid: 36 kHz stereo s16, 96.83 s, 13,943,564 B. Its incremental header/data writes survive the harness stopping the runner. Both boot logs show **0 missing targets from `0x3CB7A8`** and 0 other missing targets (`receipts/missing-targets.txt`).

Brad's listenable copy is `~/dev/ssx3-work/AU5/AU5-menu-tag1.m4a`: 708 KiB (<5 MB), AAC from the **EE transport mix**. This is the measured tag-1 stream, not the host callback stream.

AU4 `compare.py` found a 5 s coarse match (NCC `0.998941`) and 1 s refined match (NCC `0.987618`) at PCSX2 lag `+107.552 s`. Its fixed-lag 30 s subtraction returned `1.02086` residual/PCSX2 RMS, but this includes unrelated waveform beyond the common excerpt. `lag_track.py` found NCC ≥0.8 only at AU5 **8.775–12.125 s**: 135 of 1,289 windows, with no sustained one-sample lag jump. The AU5 residual below covers that **3.35 s** common excerpt, while AU4/AU2 used ~32 s; they are not same-duration improvement/regression measurements. Full output: `receipts/comparison.json`, `receipts/lag-analysis.json`.

| Locally corrected difference / PCSX2 band RMS | AU4 on AU2, 1,226 reliable windows | AU5, 135 reliable windows |
| --- | ---: | ---: |
| Whole band | 0.23328 | **0.26904** |
| 0–2 kHz | 0.18623 | 0.09766 |
| 2–6 kHz | 0.52081 | 0.20138 |
| 6–12 kHz | 0.56602 | 0.38856 |
| 12–18 kHz | 1.06076 | 0.76557 |

The corrected residual does **not** meet the `<0.02` early-stop condition. The short shared excerpt prevents attributing the broader difference to E53 semantics or the restored functions alone.

## Step 2 — static instruction census

`instruction-census.csv` lists **every** MMI, COP1, COP2/VU0, and EE LQ/SQ instruction in 13 selected function ranges (723 rows), with its address, word, disassembly, and edge-test status. `census.py` produces it from the `ee-at` generated-code index and function map. “Tested” requires a PCSX2-grounded edge-input semantics test in `ps2_fpu_cop2_audit_tests.cpp`; decoder/code-string tests do not qualify. `receipts/census-summary.txt` counts family/status per function.

| EE function / link | Relevant instructions and test status |
| --- | --- |
| `0x3C1638` containing thread address `0x3C1B48` | Builds tag 1 near `0x3C17C0`, calls `0x3C8968`, sends DMA at `0x3C1B48`. EE LQ/SQ alignment edge test not found. |
| `0x3C8968` → `0x3C85D0` | Direct dispatcher and indirect-callback driver. C.EQ.S tested; COP1 loads/moves/stores and LQ/SQ alignment untested. |
| `0x3C9E50` → `0x3CCF90` → `0x3CCA08` | Direct XA decode chain confirmed by `ee-xref`. PPACH, PEXTLH, PSRAW and ADDA.S untested. CVT.S.W/MADD.S/MADDA.S edge tested; decoder COP1 loads/moves/stores and LQ alignment untested. |
| `0x3C07A8`, `0x3C0858`, `0x3C08F8`, `0x3C1298` | Direct sound-thread helpers: VU0 state/macros, LQC2/SQC2 and LQ/SQ; transfer and alignment edges untested. |
| `0x3CBB28`, interior callback `0x3CBB78` | `0x3C8128` stores `0x3CBB78` in a mixer table. VADD tested; VMULx and VU transfers untested. Its exact live tag-1 input mapping was not proved. |
| `0x3CB538`, voice-path candidate | Four PINTEH plus PADDW/PEXLW/PSLLW/PSRLW, all untested. Called from `0x3C8A88`; a live contribution to the captured tag 1 was not proved. |
| `0x3C03E0`, pack/level candidate | PPACH/PMAXW/PAND/PEXTLW/PEXTUW/PCPY*/PNOR/PSRLW, all untested. Called from `0x3BD5B8`; link to this tag-1 capture unproved. |

The selected ranges contain no PMULTH, PMADDH, PHMADH, PADDSH, PMAXH, PMINH, PSRAH, PSRLH, PSLLH, PSRAVW, PINTH, PEXCH, or PEXEH. Adjacent candidates are included because the thread reaches part of the mixer through guest function pointers; static evidence alone cannot assign every callback to this capture.

## Step 3 — decoder differential and stop point

Build 3's default-off `PS2X_AU5_DECODER` tap recorded the first 32 decoder frames: 61 input bytes, float history in/out bits, and 28 output float bits each. The raw frame bytes remain only in `~/dev/ssx3-work/AU5/run2/decoder.txt` (not committed). `compare_decode.py` calls AU2's `au2_eaxa.frame()` with each captured input history rounded to integer and compares all 896 samples.

| Differential | Result |
| --- | ---: |
| Integer reference vs rounded EE float output | 234 of 896 samples differ |
| First difference | Frame 3, sample 1, header `0x23`: AU2 integer `−55`; EE float `−56.1796875` (rounded `−56`); input histories `−16`, `+12` |
| EE float vs simple float XA model using captured float history | Maximum absolute error `0.016845703125` sample unit |

These compare **different numeric representations**: AU2's reference rounds/clamps integer history each sample; the EE routine carries float history and emits float samples before the mixer. The integer mismatch does not identify a faulty opcode. Multiple COP1 operations in `0x3CCA08` may affect the last bits; the mix and untested MMI/VU0 path remain unmeasured. There is no single-instruction candidate for step 4, so no candidate fix or validation capture was attempted. The brief's stop rule for multiple implicated instructions applies. Numeric receipt: `receipts/decoder-comparison.json`.

## Exact commands and recommended next action

From `~/dev/ssx3` (fork builds/boots were run escalated as required):

```sh
/Users/brad/dev/ssx3-work/E52/build/ps2xRecomp/ps2_recomp /Users/brad/dev/ssx3-work/AU5/ssx3-au5.toml
zsh /Users/brad/dev/ssx3-work/AU5/build.sh
nice -n 5 cmake --build /Users/brad/dev/ssx3-work/AU5/build --target ps2EntryRunner ps2x_tests -j4
/Users/brad/dev/ssx3-work/AU5/build/ps2xTest/ps2x_tests
python3 /Users/brad/dev/ssx3-work/AU5/boot.py
python3 local/research/AU2/au2_pcmcap.py /Users/brad/dev/ssx3-work/AU5/run/tag1.bin /Users/brad/dev/ssx3-work/AU5/run/tag1-36k.wav
MPLCONFIGDIR=/Users/brad/dev/ssx3-work/AU5/mpl-cache /Users/brad/dev/ssx3-work/AU4/venv/bin/python local/research/AU4/compare.py --pcsx2-bin /Users/brad/dev/ssx3-work/AU4/pcsx2-tag1.bin --au2-bin /Users/brad/dev/ssx3-work/AU5/run/tag1.bin --au2-wav /Users/brad/dev/ssx3-work/AU5/run/tag1-36k.wav --out /Users/brad/dev/ssx3-work/AU5/compare --pc-sc-record 17122
MPLCONFIGDIR=/Users/brad/dev/ssx3-work/AU5/mpl-cache /Users/brad/dev/ssx3-work/AU4/venv/bin/python local/research/AU4/lag_track.py --au2 /Users/brad/dev/ssx3-work/AU5/run/tag1-36k.wav --target /Users/brad/dev/ssx3-work/AU4/pcsx2-tag1-36k.wav --out /Users/brad/dev/ssx3-work/AU5/lag --start 8.75 --end 41 --base-lag-frames 3871872
python3 /Users/brad/dev/ssx3-work/AU5/instrument_decode.py
nice -n 5 cmake --build /Users/brad/dev/ssx3-work/AU5/build --target ps2EntryRunner ps2x_tests -j4
AU5_RUN_NAME=run2 AU5_TARGET_TAG_RECORDS=1000 PS2X_AU5_DECODER=/Users/brad/dev/ssx3-work/AU5/run2/decoder.txt python3 /Users/brad/dev/ssx3-work/AU5/boot.py
/Users/brad/dev/ssx3-work/AU4/venv/bin/python local/research/AU5/compare_decode.py /Users/brad/dev/ssx3-work/AU5/run2/decoder.txt /Users/brad/dev/ssx3-work/AU5/decoder-comparison.json
python3 local/research/AU5/census.py
ffmpeg -hide_banner -loglevel error -y -i /Users/brad/dev/ssx3-work/AU5/run/tag1-36k.wav -c:a aac -b:a 96k -movflags +faststart /Users/brad/dev/ssx3-work/AU5/AU5-menu-tag1.m4a
```

The generated-code insertion command is one-shot; regenerate AU5 codegen before rerunning it. Logs and binaries stay in AU5 workdir.

**Recommended next action:** capture the **same sustained menu waveform and route** in PCSX2 and AU5, then establish the live callback that contributes to tag 1 and tap its input/output around one record. Audit PINTEH and packing semantics after a first differing mixed sample identifies a function/opcode. AU5's decoder comparison does not justify an arithmetic patch.
