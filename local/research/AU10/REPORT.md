# AU10 — folded tip races with sound off (SND HLE unconditional)

Brief: `local/muse/prompts/AU10.md`. Worker: Muse Code, Mac mini, ~1 h of the 2 h box.

**Result: fixed and validated.** The folded tip's sound-off title hang (GA1 B1)
was the whole SND HLE gated on `PS2X_SOUND=1`: with sound off there was no
sound clock, no tick/status/done delivery, and no voice-state advance, while
the always-on AU9 file-table override makes the game load its SPU banks and
wait on SND progress. One candidate fix per the brief: the guest-time SND
model now runs unconditionally; `PS2X_SOUND=1` only enables the host
AudioStream that drains the PCM ring. Sound-off boots race, and **det-hash
lines are identical sound-on vs sound-off for ticks 1..2400**.

## Mechanism (with citations)

Where voice state advances (all guest-time, EE thread):

- `Driver::update()` (`ps2xRuntime/include/ps2_snd_spu.h:385`) turns each
  tag-3 record into key on/off, pitch, volume writes plus status word/NAX
  slots — including the ENVX retry (key-on waits until ENVX == 0, :418-422).
  Called only from `mixTickLocked()` (`ps2_snd_spike.h:446`).
- `Spu::render()` (`ps2_snd_spu.h:270`) mixes 512 frames/tick; `Adsr::step()`
  (:129) advances ENVX and `advance()` (:318) moves NAX. Called only from
  `mixTickLocked()` (:447), which runs only on tagbuf SetDma (:488).
- Guest-visible delivery: `onSoundTick()` (:397-430, status serials +
  statusWord/statusNax writes + tick packet to the cid-1 handler) and
  `onSendCmd()` done packets (:552-558).

What gated it on `PS2X_SOUND` (folded tip `56a5e8a`, `au10-soundoff` base):

- `initLocked()` (`ps2_snd_spike.h:274-276`) early-returned unless
  `PS2X_SOUND=1`, so `enabled()` was false; all five entry points check it
  (`noteAddCmdHandler` :369, `noteRpc` :383, `onSoundTick` :399, `onSetDma`
  :473, `onSendCmd` :521).
- `SIF.cpp:482` starts the sound clock only when `noteAddCmdHandler`
  returns true, and `EeScheduler::startSoundClock()` (`EeScheduler.cpp:1923`)
  early-returns when `!enabled()` — so sound-off boots schedule zero
  SoundTick events, capture zero tagbufs, and answer zero cid-0 uploads.
- Host output is separately gated at `ps2_runtime.cpp:1135`
  (`ps2_snd_audio_output::initialize()`); the callback
  (`ps2_snd_audio_output.cpp:75-132`) only pops `pcmRing()` host-side —
  nothing guest-visible. Without a consumer the ring overflows and drops
  (`PcmRing::pushFrame`, `ps2_snd_spike.h:200-214`).

Why pre-fold GB8 (`f949ff0`) raced with sound off: the gate is identical
there (same `initLocked` early-return), but the comparator bug hid
`banks.inf`, so the game never loaded SPU banks, never sent cid-0, never
keyed a voice — it never waited on SND progress. The fold added the
**always-on** `ssx3-file-key-compare` override (`ps2_runtime.cpp:438-442`,
no env gate): the game now loads 531 upload chunks and waits on tick/done/
status progress that never arrives → title hang, pad ignored.

Call-graph confirmation: the brief asked for `lsp`, which does not exist in
this environment (opencode-worker tool, not on PATH/Homebrew); used
repo-wide grep over every `enabled()`/entry-point call site plus the build
and suite instead. Remaining `PS2X_SOUND` references after the fix: the
`ps2_runtime.cpp:1135` host-output gate (intentional) and comments.

## Fix (fork worktree `~/dev/ssx3-work/AU10/PS2Recomp`, branch `au10-soundoff`, not pushed)

Commit `2fb2003` (`git diff --stat 56a5e8a au10-soundoff`):

```
 ps2xRuntime/include/ps2_snd_spike.h         | 14 ++++++-----
 ps2xRuntime/include/ps2_snd_spu.h           |  5 ++--
 ps2xRuntime/src/lib/Kernel/Stubs/SIF.cpp    |  4 +--
 ps2xRuntime/src/lib/Kernel/Syscalls/RPC.cpp |  2 +-
 ps2xTest/src/ps2_snd_tests.cpp              | 39 +++++++++++++++++++++++++++++
 5 files changed, 53 insertions(+), 11 deletions(-)
```

- `initLocked()`: removed the `PS2X_SOUND` early-return; the SND HLE
  (ticks, cid-0/dmqueue/done, tag-3 voice updates, status block) always runs.
  `PS2X_SOUND=1` now only initializes the host AudioStream.
- Comments updated where they said default-off (`ps2_snd_spike.h:1-6`,
  `ps2_snd_spu.h:1-3`, `SIF.cpp`, `RPC.cpp`).
- Unit test: "keyed-off voice ENVX decays to zero with no output device,
  then retriggers" — key on via tag-3, sustain at 0x7fff, key off, ENVX 0
  within one 512-frame tick, voice stopped, retrigger at ENVX 0 keys on
  immediately (no retry spin). No audio output initialized in the test.
- Runner-dir check: `git diff --stat 14b1e5cb au10-soundoff --
  ps2xRuntime/src/runner` empty. Never pushed.

## Suite and build (1/2 builds)

One Release build from the worktree root (Homebrew clang,
`PS2X_BUILD_TEST=ON`, `PS2X_ENABLE_DET_HASH_TAP=ON`,
`PS2X_GS_SHADOW_PARALLEL=ON`, all other diagnostics OFF; GB8 recipe +
tests): configure rc=0, `ps2EntryRunner` + `ps2x_tests` rc=0 (627 steps).
Suite **616/616** from the worktree root. (First run from the wrong cwd
failed 1 unrelated VU0 test that needs `instructions.h` in the cwd;
re-run from `PS2Recomp/` is fully green, including the new test.)

Runner `bin/runner-au10` SHA-256
`734767d10f2b3bfc6e25c526726a6e9581436dbc3d23edf4a96aa6e9c620b98e` (×2+
boot-script precheck reads plus staged-copy reads).

## Boots (2/3, one slot each, I26-FAST, empty mc0, deterministic, paraLLEl)

Driver: `au10_boot.py` (this dir; GA1's driver plus `--sound on|off`,
`PS2X_SND_LOG`, `PS2X_FRAME_DUMP_DIR` + `ONCE_TICKS=1090,2100,2390`).
Env differs only in `PS2X_SOUND`. Stop tick 2400, wall cap 500 s.

| Boot | Sound | Bound | Wall | Last tick | cid0/dmq/done | tagbufs | Ring u/o | FATAL/missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S-off | off | target | 83.8 s | 2403 | 531/531/531 | 3571 | 0 / 1,795,584 | none |
| S-on | on | target | 82.8 s | 2401 | 531/531/531 | 3571 | 2,014,656 / 36,096 | none |

- **Race reached in both** (sound off fixed): tick-2100 frame shows the
  race at 00:00:06, 2ND/2, rider on snow, EA Radio box; tick-1091 frame
  shows the Select Peak menu (Peak 3, mountain photo). S-on sidecars carry
  identical FNV-1a hashes, so its pixels are identical (viewed S-off only).
- **det-hash IDENTICAL ticks 1..2400** (`gb8_hashdiff.py`, 0 missing both
  sides, first_diff None): the guest cannot depend on host audio. Host
  audio timing does not leak into guest state in either direction.
- Sound-off ring: 0 underruns (no consumer), 1.8M overflows = frames
  dropped host-side as designed. Sound-on: consumer drains
  (`[snd-output] stream rate=48000`), underruns = guest below real time on
  a loaded mini (same symptom as AU8/AU9, not a regression — and not a
  speed number: diagnostic build).
- Frame sidecars (both boots identical): 1091 `fnv1a=363b0550`, 2100
  `c597fc53`, 2390 `89aeed28`, all 512x448 fbp 112.

## Budgets and gaps

Builds 1/2, boots 2/3, ~1 h/2 h. Scratch `~/dev/ssx3-work/AU10` 1.8 GB;
ssx3 internal 117.7/200 GB. Never pushed; fork branch local-only; text in
git (`au10_boot.py`, this report).

Gaps, stated plainly:

- G1. The exact guest wait that spins on the title (done callback vs tick
  serial vs status word) is not identified — validated at the observable
  level (race + identical det-hash), which is what the brief asked.
- G2. S-on PNGs not separately viewed (FNV-1a-identical to S-off).
- G3. No speed measurement of the now-always-on 48-voice Gaussian mix
  (diagnostic build; AU9 already flagged the Odin cost as unmeasured).
- G4. The HLE now captures any cid-1 SIF handler / SND-sid RPC and starts
  the sound clock for any title; correctness is SSX3-scoped (this runtime
  is SSX3-focused). No opt-out knob, per the brief's "unconditionally".
- G5. `lsp` confirmation unavailable in this environment (see Mechanism).

## Orchestrator gate (2026-09-25)

**Pass.** The SND HLE (tick/status/done delivery, voice state) now runs on guest time regardless of
`PS2X_SOUND`; `PS2X_SOUND=1` only opens the host stream. Det-hash identical sound on vs off to t2400,
so guest state doesn't depend on host audio. Folds in F2 (`2fb2003`).
