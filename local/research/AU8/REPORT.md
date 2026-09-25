# AU8 — the menu music is planar tag-1 PCM played as interleaved frames

Brief: `local/muse/prompts/AU8.md` (exploratory, 2 h). Worker: Claude Code (Opus). Clock started
21:06:24 EDT; row-by-row log in `NOTEBOOK.md`.

## Answer

**The IOP doesn't mix in anything we're missing.** What's wrong is how our sound HLE reads the
tag-1 payload. Each tick the EE sends **two planar 384-sample channel blocks**, and we have been
playing them as 384 interleaved stereo frames. Played that way, each 10.67 ms tick holds one
channel's 384 samples squeezed into 192 frames, followed by the other channel's. So every tick
plays the music an octave up at double speed, twice (once per channel), with a hard splice in the
middle of the tick. And because both "L" and "R" come from the same channel, the stereo image
collapses. That's the "incomplete / discordant / missing tracks" sound Brad heard. PCSX2's tag-1
clip has the same problem: we built it with the same interleaved reading.

PCSX2's real SPU2 output is exactly the planar reading: first block to the **right** channel,
second block to the left, 3→4 linear-interpolated to 48 kHz, and nothing else. At Select Character
the IOP mixer slice is silent, and there are no SPU voices and no reverb.

| # | Evidence | Result | Receipt |
| --- | --- | --- | --- |
| 1 | SNDDRV `SNDIOP_mix` → `SNDIOP_ee36_iop24_spu48` (static, AU2 disassembly) | EE input pointer = the tag-1 payload. Per output channel the loop reads 3 s16 and advances **0x300 bytes (384 samples) per channel**; the last sample of block 0 (`payload+0x2fe`) is kept as that channel's interpolation history. Output: 512 samples/channel (0x400 bytes) at 48 kHz, o0=x[p], o1=(x[p]+3x[p+1])/4, o2=(x[p+1]+x[p+2])/2, o3=(3x[p+2]+x[p+3])/4, plus the IOP slice | `../AU2/snddrv-disasm.txt` 0x5c88–0x6058, 0x6b74–0x6c7c |
| 2 | Continuity of existing tag-1 WAVs (PCSX2 AU4, ours AU7) | Interleaved reading: \|Δ\| at in-tick frame 191→192 is **6.6× / 7.3×** the mean, 1.9–2.7× at the record seam. Planar reading: **1.00 / 1.00** at both | NOTEBOOK E4; `planar.py` |
| 3 | PCSX2 same-run capture (new SPU2 tap in guest time, 48 kHz): stream levels at Select Character, last 70 s | Core0 ADMA input 4,761/4,552 RMS; **core1 input, dry and wet voice mixes of both cores: all 0**; final out = core0 input × 0.9998, residual 0.04% | NOTEBOOK E5; `receipts/e5-tapcmp.txt` |
| 4 | Same run: tag-1 → SNDDRV 3→4 model vs SPU2 core0 input | Interleaved reading: NCC **0.154** (no match). Planar reading, block 0→R, SNDDRV phase: **NCC 1.00000, residual 0.02% RMS, max 2 LSB, 1 LSB RMS in every 5 s bin over 70 s**. Block 0→L instead: side NCC −0.9987 | NOTEBOOK E5–E7; `receipts/e6-tapcmp.txt`, `receipts/e7-phase.txt` |
| 5 | Our AU7 runtime tag-1 vs PCSX2 AU4 tag-1, both read planar (block 0→R), `AU7/midside.py` at AU7's record-aligned lag | L/R/Mid/Side NCC **1.0000**, diff/ref 0.000; Side RMS **922** (interleaved misread: 382, +7.7 dB); L 5,043 ≠ R 4,960 (misread: L ≈ R 5,002) | NOTEBOOK E8; `receipts/e8-midside.txt` |
| 6 | Fixed runtime boot (fork `au8-snd` `f2ec588`), host-output WAV vs that boot's tag-1 read planar | Leased boot (slot 2, E33 route, 168 s, rc 0, 6,018 gap-free records): host WAV windows found in the planar reading are **100% exact frames (31,496 checked, both channels)**, 0% in the interleaved one. That boot's tag-1 read planar vs PCSX2 AU4: L/R/Mid/Side NCC **1.0000**, Side RMS 922 = 922. Host output is 62.7% underrun silence: the guest runs below real time on the loaded mini, same share as AU7's host WAV (166 s host for 64 s of content), a speed symptom not a sound bug | NOTEBOOK E9; `receipts/e9-*.txt`, `receipts/e9-boot-wrap.log` |

So our EE mix was already right (AU7), and the fix is how we read it. PCSX2's AU4 video audio
can't be aligned (host-clocked `-turbo` capture full of dropouts; NOTEBOOK E1), so every
comparison above uses guest-time data.

**Hypotheses, not verified:**
- Channel order (block 0 = right) comes from PCSX2's SPU2 core0 ADMA input. I didn't trace it
  statically through `SNDIOP_getspubuf`/`SNDIOP_loadautodma1`, and there's no hardware
  reference. If PCSX2 mapped the ADMA halves backwards, the image would be mirrored, which is
  audible only as L/R swapped.
- The IOP slice (24 kHz `MIX_audioslice`) and SPU voices are silent at Select Character. The
  race, SFX, or other modes may use them (AU2 G4); the tap would show that.

## Prototype

Fork worktree `~/dev/ssx3-work/AU8/PS2Recomp`, local branch **`au8-snd`** = `ssx3` `fb11e18` +
**`f2ec588`** (not pushed). `PcmRing::push` now interleaves block 1 (left) and block 0 (right);
the tag-1 capture file stays raw. New unit test "PCM ring interleaves the planar tag-1 channels".

```
 ps2xRuntime/include/ps2_snd_spike.h | 11 +++++++++--
 ps2xTest/src/ps2_snd_tests.cpp      | 25 +++++++++++++++++++++++++
 2 files changed, 34 insertions(+), 2 deletions(-)
```

Suite **594/594** from the worktree root. Runner sha256 ``a81f83432cd242264fa39d7b057f1fe77f0a39af0739a199e2dc9ccea5f23574`` (two reads). Runner-dir diff
vs `14b1e5cb` is empty. The host output still plays 36 kHz directly (no 3→4 interpolation); that
is closer to the source than hardware, not a defect.

## Listening files (for Brad)

All 48 kHz AAC 128 kb/s, under 1.2 MB each:

| File | What it is |
| --- | --- |
| `/Users/brad/dev/ssx3-work/AU8/AU8-AB-15s-current-then-fix.m4a` | 15 s of what the runtime plays today, then the same 15 s read correctly (AU7 capture, 5–20 s) |
| `/Users/brad/dev/ssx3-work/AU8/AU8-A-ours-current-interleaved.m4a` | Today's playback, 59 s (AU7 capture 5–64 s) |
| `/Users/brad/dev/ssx3-work/AU8/AU8-B-ours-planar-fix.m4a` | Same 59 s, planar fix (bit-for-bit what `au8-snd` pushes, resampled to 48 kHz by ffmpeg) |
| `/Users/brad/dev/ssx3-work/AU8/AU8-C-pcsx2-spu2-output.m4a` | PCSX2's actual SPU2 final output, 59 s of the au8 run (same menu music, different position) |

SHA-256: A `8b8b9ad3…95ea`, B `c8cc4e12…abe9`, C `3a8be56a…fa76`, A→B `2593acff…6414` (full
values in `receipts/clips-sha.txt`).

## What's next (recommendation; the orchestrator decides)

1. Brad listens to the A→B file. If B sounds right, fold `f2ec588` into fork `ssx3` (the same fast
   path as AU7's fold). Every shipped build (Mac/iOS/Odin) picks it up with no further change.
2. Optional check of the channel order: trace `SNDIOP_getspubuf` → `loadautodma1/2` → the ADMA
   L/R halves, or have Brad listen for a panned SFX on hardware or PCSX2.
3. Race audio: rerun the au8 PCSX2 hook with the route into a race (`au4-part2-cap.sh`) and check
   whether the IOP slice, voices or reverb carry anything there (AU2 G4, AU6 gap).
4. Tidy-ups that don't affect the verdict: the AU4/AU6/AU7 "tag-1 WAV" tools (`au2_pcmcap.py`,
   `compare.py`) all write the interleaved reading. Their NCC/level numbers stay valid as
   same-transform comparisons, but anyone listening to those WAVs hears the misread.

## Budget, pins, gaps

| Item | Value |
| --- | --- |
| PCSX2 | `/home/brad/pcsx2-g7/pcsx2` `9056c08` + existing T/AU4/AU6 hunks + AU8 hunk (`pcsx2/au8_patch.py`; diff `/home/brad/au8/au8-hunk.diff`; pristine copies `/home/brad/au8/pre/`). Env-gated by `PCSX2_AU8_DIR`; with it unset, behaviour is unchanged. 2 builds (first failed: `Console` undeclared). `pcsx2-qt` sha256 `712c132a5cd7369e0202466597ba2adc696db436829a2946036c4cbcc9fb01a0` ×2 |
| PCSX2 run | 1 capture, `au8_cap.sh` (AU6's route, 6,000 records past Select Character), 179 s wall, bytesize idle before. tag sha256 `ef2838848b2b6d32f5444b3582372d865399eae46e77bfbb1b9a40974f25aae2`, tap `3eaa7fe5a18e0965591fb9bd5c02c3ac91862c86bd15514dff7b22d4ccd546eb` (×2); tail-70 s `cbf69f7d7f6cc7445dba458fc9144c685581e3ec2a6c5cf04fe3a8fa6f86bcf2` (matched on the mini). `/home/brad/au8` 1.4 GB |
| Mac | 1 build (+1 incremental after the channel-order edit), 1 leased boot (slot 2). Deps copied to `~/dev/ssx3-work/AU8/deps` (E50's `_deps` is gone). Scratch `~/dev/ssx3-work/AU8` 2.4 GB (build 0.6 GB, deps 1.3 GB, clips, WAVs, 107 MB tap tail); ssx3 internal total 57.0 of 200 GB |
| Time | 21:06 → 21:23 for the core answer (row times in NOTEBOOK; rows E1–E8 carry a time correction) |

Gaps:
- G1. Channel order is from PCSX2 only (above).
- G2. Menu (Select Character) only; race and SFX paths are unmeasured.
- G3. PCSX2's ADMA input already includes the IOP's 3→4 linear interpolation. Our host plays
  36 kHz directly, so ours is slightly brighter than PCSX2/hardware above ~10 kHz. It's not a
  correctness issue, and it's labelled.
- G4. Nobody has listened to the new clips yet.

## Orchestrator gate (2026-09-24)

**A.** Read the report, notebook and commits `1e699ceb`, `eb826cf3`. The verdict rests on guest-time
PCSX2 data (SPU2 tap: final output = tag-1 read planar, block 0 → right, SNDDRV 3→4 phase, max 2 LSB
over 70 s) and on our boot's host output matching the planar reading frame for frame. Sent Brad the
A→B, B and C clips. Folded: `f2ec588` pushed to fork `ssx3` (fast-forward from `fb11e18`; suite
594/594; runner-dir diff empty); then UP1's port on top, `d711506`. Open: channel order rests on
PCSX2 only (G1); race/SFX paths unmeasured (G2); host plays 36 kHz without the 3→4 resample (G3,
labelled); sound output still needs `PS2X_SOUND=1`. Brad's listen of the new clips is pending.

**Brad (2026-09-24):** "that planar fix audio version sounds exactly right."
