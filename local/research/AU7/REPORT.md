# AU7 — E54C build restores the menu stereo image (Side NCC 1.0000)

Worker: Muse Code. Brief: `local/muse/prompts/AU7.md` + orchestrator amendment
(keep-both resolution of adjacent-addition conflicts). No push, no board/ledger
edit.

## Result

**H1's observable is met decisively.** On the `fork/ssx3` `04f3ace` + sound-HLE
build (which contains E54C), `midside.py` over the 5–64 s span reports:

| Channel | AU7 NCC | AU7 diff/ref | AU6 control NCC | AU6 control diff/ref |
| --- | --- | --- | --- | --- |
| L | 1.0000 | 0.000 | 0.9975 | 0.071 |
| R | 1.0000 | 0.000 | 0.9939 | 0.111 |
| Mid | 1.0000 | 0.000 | 0.9985 | 0.055 |
| Side | **1.0000** | 0.000 | **0.4337** | 0.980 |

Side level: AU7 +0.00 dB every 4 s bin (was −1.6 to −1.9 dB). The AU6 control
reproduces the brief's baseline (Side 0.434) exactly. Lags: AU7 107.552 s,
control 107.541 s. Full outputs: `receipts/midside-au7.txt`,
`receipts/midside-au6-control.txt`.

Exact-sample check at AU7's lag (independent read, not `midside.py`): over
2,124,000 stereo frames, 12,224 samples (0.29%) differ, all by exactly 1 LSB.
So "1.0000" is quantization-level agreement, not bit-exactness.

## Part 1 stop and amendment resolutions

Step 1 first stopped per the brief: `5bb1fdd` conflicted in `EeScheduler.cpp`
(not a test file). Under the amendment, two conflicts were resolved; both were
positional overlaps where our side only added lines:

1. `5bb1fdd` (AU2) → `ea2a10c`: two sites, both pure adjacent additions.
   Includes: kept HEAD's `ps2_vq.h` / `gs_stream_capture.h` / xxhash block,
   then added `ps2_snd_spike.h`. Vsync case: kept HEAD's
   `#if PS2X_ENABLE_DET_HASH_TAP emitDetHashTap(); #endif` first, then AU2's
   `onVBlank` call. Hunk: `receipts/resolve-5bb1fdd-eesched.diff`
   (original conflict: `receipts/cherry-pick-conflict.diff`).
2. `83167d6` (AU3) → `812d7b6`: one site. AU3 *deletes* the AU2 `onVBlank`
   spike call it supersedes (replaced by `startSoundClock` + `SoundTick`,
   verified present at lines 1920/2873); our side had only added the det-hash
   tap above those untouched lines. Resolution: kept the tap, accepted AU3's
   deletion. No existing line was changed by both sides; no logic authored.
   Hunk: `receipts/resolve-83167d6-eesched.diff`.
3. `3c895ca` → `64b2f6d` and `ddf4f66` → `959f4ea`: applied cleanly.

Branch `au7-snd` HEAD: `959f4ea`. No conflict markers remain in the tree.

## Pins

| Item | Value |
| --- | --- |
| Worktree | `~/dev/ssx3-work/AU7/PS2Recomp`, `au7-snd` @ `959f4ea` |
| Base | `fork/ssx3` `04f3ace` (contains E54C `89bec9b`; local `ssx3` stale, untouched) |
| Picks | `ea2a10c` (AU2+res) `812d7b6` (AU3+res) `64b2f6d` (ABI) `959f4ea` (AU5); skipped `045dd6a` |
| Runner SHA-256 ×2 | `fdb020e4581afb573c6c7a7e300008b282e9f040afc1911824e32a7828be8a18` (match) |
| Codegen | canonical `~/dev/ssx3-work/codegen-ssx3`, 9457 files, listing SHA-256 `7bbbd388cd5a02a4b727d1b278cd4b26dc54e5582afbbe9702aed0de8c8e3430` |
| Suite | 589/589 pass, rc 0, from worktree root (`~/dev/ssx3-work/AU7/suite.log`) |
| tag1.bin / tag1-36k.wav SHA-256 | `42847251…afa42c` / `8795471e…be820` (full in receipts section below) |
| M4A | `~/dev/ssx3-work/AU7/AU7-menu-tag1.m4a`, 833,329 B, SHA-256 `827beb96…8214ef` |

Full SHAs: tag1.bin
`42847251acabd3e9d5fb182ad7d757db158a9eb3c1b984dc49f79888cdafa42c`;
tag1-36k.wav
`8795471e946a511d8adb347420e58ec15f4602a5e273b9c036c94119accbe820`;
m4a `827beb967e8fadee6b911a4bd25be0bd77d6330510d0bbfd7bdf3ec9ec8214ef`.

## Build, boot, and capture

One Release build (`PS2X_ENABLE_DIAG_TAPS=OFF`, AU5 tag-1 capture on;
`~/dev/ssx3-work/AU7/build.sh`, cmake/ninja logs alongside). One leased boot:
slot 1 (`au7-menu`), runner PID 66719, rc 0, bound `target`, 167.3 s elapsed
(cap 500 s), 6,029 consecutive tag records (serials 1–6029, 0 gaps), 64.3 s
PCM. E33 route verified in `run/boot.log`: `[padscript] armed n=2`,
`press i=0 … at=10350ms`, `press i=1 … at=20650ms`. Lease released; both slots
free after. Boot script is AU6's with only `AU6→AU7` paths and the lease label
changed (`diff` verified). Scratch `~/dev/ssx3-work/AU7` = 669 MB (< 8 GB).

Exact commands:

```sh
git -C ~/dev/PS2Recomp worktree add -b au7-snd ~/dev/ssx3-work/AU7/PS2Recomp 04f3ace
cd ~/dev/ssx3-work/AU7/PS2Recomp
git cherry-pick 5bb1fdd   # resolve EeScheduler.cpp keep-both, continue
git cherry-pick 83167d6   # resolve vsync site (tap + AU3 deletion), continue
git cherry-pick 3c895ca   # clean
git cherry-pick ddf4f66   # clean
zsh /Users/brad/dev/ssx3-work/AU7/build.sh
(cd /Users/brad/dev/ssx3-work/AU7/PS2Recomp && /Users/brad/dev/ssx3-work/AU7/build/ps2xTest/ps2x_tests)
python3 /Users/brad/dev/ssx3-work/AU7/boot.py
python3 local/research/AU2/au2_pcmcap.py /Users/brad/dev/ssx3-work/AU7/run/tag1.bin /Users/brad/dev/ssx3-work/AU7/run/tag1-36k.wav
~/dev/ssx3-work/AU4/venv/bin/python local/research/AU7/midside.py ~/dev/ssx3-work/AU7/run/tag1-36k.wav ~/dev/ssx3-work/AU4/pcsx2-tag1-36k.wav
~/dev/ssx3-work/AU4/venv/bin/python local/research/AU7/midside.py ~/dev/ssx3-work/AU6/run/tag1-36k.wav ~/dev/ssx3-work/AU4/pcsx2-tag1-36k.wav
ffmpeg -hide_banner -loglevel error -y -i /Users/brad/dev/ssx3-work/AU7/run/tag1-36k.wav -c:a aac -b:a 96k -movflags +faststart /Users/brad/dev/ssx3-work/AU7/AU7-menu-tag1.m4a
```

## Gaps

- **Attribution confound (stated plainly):** the AU7 base differs from AU6's by
  more than E54C — it also brings E54D (LWU zero-extend + the regenerated
  canonical codegen used here; AU6 used `AU5/codegen`), E54B, E54F2, E55x, GBx
  and others. H1's observable (Side ≥ 0.95 on an E54C build) is met, but
  strict single-variable isolation of the PINTEH lanes would need E54C-only on
  AU6's base. AU5's PINTEH-in-`0x3CB538` finding still points at the mixer.
- `PS2X_AU6_EE_SNAP` from the copied boot script is unread by this binary
  (045dd6a skipped); harmless, kept for route-identical settings.
- No race-scene audio comparison; menu only, same as AU6.
