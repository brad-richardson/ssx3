# AU9: race sound effects on SPU2 voices

Brief: `local/muse/prompts/AU9.md` (exploratory, 3 h). Worker: Claude Code (Opus 5.5). Clock started
21:49:20 EDT; row-by-row log in `NOTEBOOK.md`.

## Answer

Our runtime had no sound effects for two reasons, and AU9 fixes both on a local fork branch.

1. **The game never loaded its SPU sound banks, because of a recompiler bug.** EA's CD file layer
   keeps its file table sorted with a comparator at `0x3E3968` (`lwu, lwu, dsubu, bltz, bgtz`). Our
   recompiler emits BLTZ/BGTZ/BLEZ/BGEZ as tests on the **low 32 bits** of the register
   (`GPR_S32(ctx, rs) < 0`), but the R5900 tests bit 63. The 64-bit difference of two unsigned words
   then gets compared as a wrapped 32-bit value, which isn't an order. The table sorts into a rotated
   sequence and bsearch misses exactly six files: `data/config/banks.inf`, `GRNT_ZOE.BNK`,
   `GRNT_ARI.BNK`, `SLUSOVF.BIG`, `NETCNF.IRX`, `EZMIDI.IRX`. Without `banks.inf` the game never loads
   `SSX3Menu.bnk` (menus) or the race banks (Crowd, land, Mtn, zboardSPU, zBxsfx), so it never sends
   a cid-0 upload and never keys on a voice. AU2/AU3 saw "0 cid-0 packets" for this reason.
2. **Our SND HLE had no SPU voices.** AU9 adds a model of the SPU2 parts the game uses (48 voices,
   PS-ADPCM, pitch, ADSR, volumes, key on/off, dry mix) and a port of SNDDRV's
   `SNDIOP_updatevoices`, which turns the per-tick tag-3 record into voice register writes. The
   cid-0 uploads are copied into a 2 MB SPU RAM. The music goes through SNDDRV's own 3→4 upsampler,
   and the host stream moves to 48 kHz.

With the comparator override in place, our boot uploads **531 chunks, the same as PCSX2** (83 for the
boot bank + 448 for the race banks). The uploaded bytes match PCSX2's SPU RAM. When PCSX2's own tag-3
records are fed through our voice model, **every second's voice-layer level matches PCSX2's to within
0.3 %**.

## Evidence

| # | Evidence | Result | Receipt |
| --- | --- | --- | --- |
| 1 | PCSX2 race capture with new env-gated hooks (full tag buffer + EE status per tick, every EE SetDma, every SPU2 register write, SPU DMA, SPU RAM every 20 s, all in guest time) | 38,786 ticks, race reached. 596 × 4 KB SND payload DMAs + 531 cid-0 packets: boot bank at vsync 1553–1560 (83 chunks), race banks at vsync 24209–24317 (448 chunks = T47's 1.75 MB) | NOTEBOOK E1–E5; `pcsx2/au9_patch.py`, `sifdma_up.py` |
| 2 | Tag-3 layout (static SNDDRV `updatevoices` 0x7d1c + PCSX2 records) | Payload after `{3, 0x2A8}`: +0 wet mask (0), +8 dry mask (all 48 voices), +0x20 + v·8 = {u32 keyon serial << 23 \| SPU byte address (0 = key off), u16 pitch (0x1000 = 48 kHz), s8 vol L, s8 vol R}. Key on = SSA, LSAX 0x5000, ADSR 0x000F/0x0005, VOLL/VOLR; if ENVX ≠ 0 the driver keys off and retries next tick. Status block +0x3C + v·8 = word, +0x40 + v·8 = NAX (0 once ended) | NOTEBOOK E3, E6; `tagbuf.py` |
| 3 | Our baseline boot (AU8 runner) | cid0 = 0 over 5,828 ticks (menus + race), as AU2/AU3 saw | E4 |
| 4 | Bank headers our EE loads; ISO BNKl/BIGF scan | All 6 loaded banks have SPU size 0. Only 7 banks on the disc carry SPU data, all in AUDIO.BIG; SSX3Menu = 83 chunks, Crowd+land+Mtn+zboardSPU+zBxsfx = 448 chunks (PCSX2's counts exactly); the list is `/DATA/CONFIG/BANKS.INF` | E7–E8; `isofiles.py` |
| 5 | Our reads + lldb (runner launched under lldb with its own lease) | BANKS.INF never read; the FE/WORLD loaders run (3/4 hits) but the EA lookup of `data/config/banks.inf` fails. Lookup = uppercase + hash h·33+c + bsearch with comparator `0x3E3968` | E9–E11 |
| 6 | Our file table dumped at that lookup + offline bsearch | 163 entries, rotated (wraps at index 111). With the 32-bit wrapped compare, bsearch misses exactly BANKS.INF, SLUSOVF.BIG, GRNT_ZOE.BNK, GRNT_ARI.BNK, NETCNF.IRX, EZMIDI.IRX | E12 |
| 7 | Generated code for `sub_003E3968` + `control_flow_emitter.cpp` | `dsubu` is 64-bit, `bltz`/`bgtz` read `GPR_S32`. BLEZ/BGTZ/BLTZ/BGEZ (+L/AL) all test 32 bits; BEQ/BNE compare 64 | E13 |
| 8 | Boot with the 0x3E3968 override | **cid0 = 531, dmq = 531, done = 531**, first `spu=0x5040 size=4096`, same as PCSX2; tag-3 keyons identical to PCSX2's in the menus (`0x822470` pitch 3763 …) | E14–E15 |
| 9 | Upload bytes vs PCSX2 SPU RAM dumps | 82/83 boot and 443/448 race chunks byte-identical; the 1 + 5 others are the last partial chunk of each bank (bytes past the bank end; staging leftovers, hypothesis) | E17 |
| 10 | PCSX2 race tap | Final out = music (core0 input) + dry0 + dry1 with residual 2 LSB RMS per second; reverb (wet) silent. The mix model needs no extra gain | E16; `receipts/` |
| 11 | Our voice model on PCSX2's own tag-3 records + PCSX2's SPU RAM, vs PCSX2's tapped voice layer (same capture, one lag) | 28.5 s of race: per-second RMS equal within 0.1–0.3 %; NCC 0.967 (L 0.966, R 0.962); 0.997–0.999 in the loud SFX seconds, 0.84–0.88 in quiet ones | E18; `receipts/e16-replay-vs-pcsx2.txt` |
| 12 | Live boot `run-v1` with voices (runner `8af43c1`, slot 3, I26-FAST; 5,922 ticks = 64 s guest, 560 s wall bound on a busy mini) | cid0/dmq/done 531. **Menu SFX vs PCSX2, aligned on the first voice onset: NCC 0.9997 over 2 s**, per-second RMS within 1.3 %. Race HUD at 00:00:36 (tick 3908), frame not black | E19; `receipts/e19-ours-vs-pcsx2.txt` |
| 13 | Same boot, music path | Music channels = the boot's tag-1 read planar + SNDDRV 3→4 integer model: **100.000 % exact, both channels, 6,002 ticks** | E20; `receipts/e20-music-exact.txt` |
| 14 | Same boot, race voice layer | Ours 1728/1714 RMS, sounding 98 % of the time; PCSX2 1260/1202, 66 %. Different scene (our route leaves the rider at 1 MPH); after the start both hold the same looping samples (`0xafc80`, `0xc6e20`) | E19, E21 |
| 15 | Same boot, host output | 48 kHz WAV carries the mixed stream (sampled 8-frame windows: 623/3,000 found in music+voices, 40 in music only); 89 % underrun silence = guest below real time on the busy mini (speed symptom, as in AU8) | `receipts/e19-hostwav.txt` |
| 16 | Frames, override vs no override (orchestrator datum): two deterministic boots (`PS2X_DETERMINISTIC=1`, I26-FAST, 3,700 ticks, frame dump at tick 2400), AU8 runner `a81f8343` (no override) vs AU9 runner `e829827b` | Both are in the race at 00:00:11, 14 MPH, same scene: mean level 29.5 vs 29.6, mean \|Δ\| 1.16 per channel. The override doesn't change what renders (not black). Only one dump tick fired | E22; `receipts/e22-frames.txt` |

**Hypotheses, not verified:**
- The 0.84–0.88 NCC in quiet replay seconds (row 11) comes from sub-tick timing (the IOP applies each
  tag-3 update partway into a 512-sample tick; we apply it at the tick boundary) and from the
  linear stand-in for SNDDRV's volume sweeps. Levels match, so it shouldn't be audible, and Brad heard no problem in the race clips.
- The 1 + 5 upload chunks that differ from PCSX2 differ only past the bank ends (row 9).
- Other effects of the six unfindable files: `GRNT_ZOE.BNK`/`GRNT_ARI.BNK` are Zoe's and Allegra's
  grunt banks, so their voice lines were silent too. Missing `SLUSOVF.BIG`, `NETCNF.IRX`,
  `EZMIDI.IRX` may matter elsewhere. The override fixes all six, but only the SFX were checked.

## Prototype (fork worktree `~/dev/ssx3-work/AU9/PS2Recomp`, local branch `au9-spu`, not pushed)

Base: fork `ssx3` `f949ff0`. The fork has since moved to `71c952e` (I32); a fold rebases onto it.

| Commit | What | Status |
| --- | --- | --- |
| `a46fb2e` | Recompiler: BLEZ/BGTZ/BLTZ/BGEZ (+L/AL) test `GPR_S64`, plus a codegen test | **NOT validated in a boot.** The runner uses the external codegen, which this commit doesn't touch. E54E made the same global change and its boot went black, so it needs its own lane before any regeneration. Kept separate so it can be dropped |
| `fb75ec3` | Game override `ssx3-file-key-compare`: replaces `0x3E3968` with the guest semantics (unsigned 32-bit keys ordered by the 64-bit difference; match counter at `0x51ED80`) | Validated: rows 8, 12 |
| `8af43c1` | SND HLE voice layer: `ps2_snd_spu.h` (SPU model + SNDDRV driver port + 3→4 upsampler), `ps2_snd_spu_gauss.h` (PCSX2 table), spike/output wiring, host 48 kHz, 6 unit tests | Validated: rows 11–15 |
| `243b759` | `<cstdlib>` include (found building the offline replay) | Suite |

`git diff --stat f949ff0 au9-spu`:

```
 ps2xRecomp/src/lib/control_flow_emitter.cpp   |  11 +-
 ps2xRuntime/CMakeLists.txt                    |   1 +
 ps2xRuntime/include/ps2_snd_spike.h           | 109 +++++-
 ps2xRuntime/include/ps2_snd_spu.h             | 485 ++++++++++++++++++++++++++
 ps2xRuntime/include/ps2_snd_spu_gauss.h       | 272 +++++++++++++++
 ps2xRuntime/include/ssx3_file_key_compare.h   |  15 +
 ps2xRuntime/src/lib/ps2_runtime.cpp           |   7 +
 ps2xRuntime/src/lib/ps2_snd_audio_output.cpp  |   4 +-
 ps2xRuntime/src/lib/ssx3_file_key_compare.cpp |  63 ++++
 ps2xTest/src/code_generator_tests.cpp         |  40 +++
 ps2xTest/src/ps2_snd_tests.cpp                | 125 +++++++
 11 files changed, 1125 insertions(+), 7 deletions(-)
```


- Suite: **602/602** from the worktree root (`receipts/suite-summary.txt`).
- Runner sha256 at `243b759`: `e829827b1d2804dde7f2def22b465acf71403ebc40c4bde10aa218186df06a61`
  (two reads). The live boot `run-v1` used the `8af43c1` build (`receipts/runner-sha.txt`); the only
  difference is an include.
- Runner-dir check: `git diff --stat 14b1e5cb au9-spu -- ps2xRuntime/src/runner` is empty.
- Licence: PS2Recomp is GPL-3.0. PCSX2's SPU2 files are GPL-3.0-or-later, which allows use under
  GPL-3.0. The ported pieces (ADPCM decode, ADSR, the Gaussian table) carry PCSX2's copyright line
  in `ps2_snd_spu.h` and `ps2_snd_spu_gauss.h`.
- Env: voices are on with `PS2X_SOUND=1`; `PS2X_SND_VOICES=0` gives music only (still 48 kHz via
  SNDDRV's upsampler); `PS2X_SND_MIX_RAW=<file>` records the guest-time 48 kHz mix as music L/R +
  voices L/R.
- Host output is now 48 kHz with SNDDRV's own 3→4 interpolation, which also closes AU8's G3.
- Not modelled: reverb (PCSX2's wet mix is silent in these captures), SPU noise and pitch
  modulation, SPU2 IRQs. SNDDRV's volume sweeps are approximated by a one-tick linear ramp. IOP voices
  (tag-3 +0x1A0…, `updateiopvoices`) are empty in both captures.

## Listening files (for Brad), all 48 kHz AAC 128 kb/s

| File | What it is |
| --- | --- |
| `/Users/brad/dev/ssx3-work/AU9/AU9-AB-15s-race-before-then-after.m4a` | 15 s of our race as the runtime plays it today (music only), then the same 15 s with the SFX layer. **Brad listened: "the race sound effects sound right" (2026-09-24)** |
| `/Users/brad/dev/ssx3-work/AU9/AU9-A-ours-before-music-only.m4a` | Our boot `run-v1`, 59 s (menus → race start → race), music only |
| `/Users/brad/dev/ssx3-work/AU9/AU9-B-ours-after-with-sfx.m4a` | Same 59 s with the SPU voice layer (what the new HLE sends to the host) |
| `/Users/brad/dev/ssx3-work/AU9/AU9-C-pcsx2-race-output.m4a` | PCSX2's final SPU2 output, 30 s from the race-bank upload to race time 00:00:15 (same event, different run) |
| `/Users/brad/dev/ssx3-work/AU9/AU9-D-pcsx2-race-voices-only.m4a` | PCSX2's voice layer alone, same 30 s |
| `/Users/brad/dev/ssx3-work/AU9/AU9-E-pcsx2-menu-output.m4a` | PCSX2's final output around its first menu SFX, 10 s |

The before/after clips come from one boot's guest-time capture, so they line up sample for sample.
PCSX2's clips cover the same event but a different scene (its rider is moving, ours has stopped).
SHA-256 values are in `receipts/clips-sha.txt`.

## What's left (recommendation; the orchestrator decides)

1. Brad has listened and approved the race SFX (via the orchestrator, 2026-09-24).
2. Fold `fb75ec3` + `8af43c1` + `243b759` onto fork `ssx3` `71c952e` (after the runner-dir check), **without**
   `a46fb2e`. Every shipped build picks it up with `PS2X_SOUND=1`. The Odin/iOS cost of the
   voice layer is unmeasured: 48 voices × 48 kHz of Gaussian mixing on the EE thread, with idle
   voices skipped.
3. The codegen bug is wider than this one function: every BLTZ/BGTZ/BLEZ/BGEZ reading a register
   whose bit 63 differs from bit 31 is wrong in today's codegen. E54E's black screen suggests that
   some HLE or runtime path leaves non-sign-extended upper bits that the correct predicate then
   exposes. A separate E-lane brief: find that path (for example with a tripwire where a signed
   branch's 64-bit and 32-bit predicates disagree, log the PC, then fix), then regenerate. Until
   then, per-function overrides like `fb75ec3` are the scoped fix.
4. Small follow-ups: model the hardware volume sweep exactly (register log in
   `pcsx2/spureg.txt`), and reverb if a mode turns it on.

## Budget, pins, gaps

| Item | Value |
| --- | --- |
| PCSX2 | `/home/brad/pcsx2-g7/pcsx2` `9056c08` + AU4/AU6/AU8 hunks + AU9 hunk (`pcsx2/au9_patch.py`; diff `/home/brad/au9/au9-hunk.diff`; pristine copies `/home/brad/au9/pre/`), env-gated by `PCSX2_AU9_DIR`. 3 builds (2 failed: missing extern; duplicate symbol in multi-ISA `Mixer.cpp`). `pcsx2-qt` sha256 `a0e4a5fe…c94` ×2 |
| PCSX2 runs | 1 capture `au9r` (after two false starts: WSL died with the ssh session; TL1's APK build was running). `/home/brad/au9` ≈ 1 GB (tap 667 MB). Capture SHAs in NOTEBOOK E2 and `/home/brad/au9/cap-sha.txt` |
| Mac boots | 6 leased boots, one slot each: baseline, movies-on, override check, the live validation boot, and 2 frame-control boots. 5 lldb-launched boots (runner launched under lldb with its own lease, never attached, ≤150 s) |
| Builds | 1 full + 4 incremental (`~/dev/ssx3-work/AU9/build`, deps read-only from AU8) |
| Scratch | `~/dev/ssx3-work/AU9` 1.2 GB (build 566 MB, boots, PCSX2 slices; WAV intermediates deleted); ssx3 internal total 93.5 of 200 GB (`receipts/disk.txt`) |
| Time | 21:49:20 → 23:13 EDT (1 h 24 min of the 3 h box) |

Gaps:
- G1. Brad approved the race SFX. The menu SFX and the quiet-passage differences from row 11 were not singled out for listening.
- G2. The race comparison against PCSX2 is statistical (different scenes). Exact comparisons are
  the offline replay on PCSX2's inputs (row 11) and the menu SFX (row 12).
- G3. The emitter change (`a46fb2e`) is unvalidated by design, and the codegen hasn't been
  regenerated.
- G4. Mac only: no Odin/iOS run, and no speed measurement of the voice layer.
- G5. Slot 1 held a stale `au8-race pid=66267` lease at 21:56; I left it alone.

