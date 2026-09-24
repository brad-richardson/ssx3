# AU3 — Sound HLE: SND tick on the guest clock, tag-1 PCM to the host audio stream

You are a worker in a herdr pane in the ssx3 repo (`~/dev/ssx3`, Mac mini).
Follow `~/dev/AGENTS.md`. **Tables + receipts; recommend, the orchestrator
decides.** Read first:
- `AGENTS.md` (two-slot lease via `local/tooling/p_lane_lease.py`; kill by PID);
- `local/AGENTS.local.md`;
- `local/research/AU2/REPORT.md` (all of it: the protocol tables, the
  spike, and **§AU2-4, the lease incident**);
- `local/research/AU1/REPORT.md` §§ on sema 36 and the sound thread.

## Why

AU2 proved that SSX 3's EA SND library decodes and mixes everything on the
EE. Each tick it hands the IOP 384 finished stereo s16 frames at 36 kHz in
tag 1 of the tag buffer. All we need for audible music is to deliver the
IOP's cid-1 tick at the right rate and play tag-1 PCM. We don't need SPU2,
SNDDRV emulation or an XA decoder.

## Work

Worktree off fork `ssx3` `eac6cba` on a new local branch `au3-snd`, with
AU2's `au2-snd` `7c2a02e` cherry-picked (no history rewrite). Canonical
codegen `~/dev/ssx3-work/codegen-ssx3`.

1. **SND HLE** (`PS2X_SOUND=1`; default off for now):
   - Deliver the cid-1 type-0 tick from an **EE-scheduler event on the
     guest cycle clock** at 36,000 / 384 = **93.75 Hz of guest time**, not
     per vblank and not from the host audio callback. That keeps it
     deterministic, which E55's determinism mode needs, and keeps it in step
     with the guest when it runs slow.
   - Keep AU2's status stamp and type-2 answers.
   - Take the tag-1 PCM from the SetDma'd tag buffer on the EE thread and
     push it into a lock-free ring.
2. **Host output:** a raylib `AudioStream` fed from the ring, 36 kHz stereo
   s16. If raylib/miniaudio won't open 36 kHz, resample host-side to 48 kHz
   (linear is fine for now; name the method). On underrun play silence, on
   overflow drop the oldest, and count both.
3. **Fix `_sceSifSendCmd` (0x426078) for real:** bind it to the
   7-argument `(cid, mode, pkt, size, src, dst, esize)` form, unconditional
   and not spike-gated, with a unit test.
4. **Tests:** tick cadence (N guest cycles → expected tick count), tag
   buffer parse → PCM ring bytes, SendCmd argument binding. Run the suite
   from the worktree root.

## Validation (Mac, ≤2 boots, one slot each, PID-tracked, no debugger attached to harness children)

- Boot A (`PS2X_SOUND=1`, the E51/GB3 route, ≤540 s):
  - a WAV tap of exactly what reaches the host stream
    (`PS2X_SOUND_WAV=<path>`, capped at 200 MB);
  - the tick rate in guest time and in wall time;
  - underruns and overflows per minute, per phase (title, menus, SC,
    race);
  - the sound thread's sema 36 signals and waits.
- Boot B, the same with `PS2X_SOUND=0`: guest ticks at the same wall
  snapshots, to show the cost of the sound thread now running ~94×/s.
  **Label it diagnostic** (the taps are compiled in; no speed claims).
- Check that the race still starts on both.
- Convert the WAV to a ≤5 MB `.m4a` (`afconvert -f m4af -d aac -b 128000`)
  at `~/dev/ssx3-work/AU3/run/au3-host-stream.m4a` for Brad to listen to.
  Don't commit audio.

## Budgets and stop rules

1–2 builds (`nice`; check for other clang/ninja), ≤2 boots, 5 h, cap 3 GB.
If the tick-on-guest-clock breaks the race or the sound thread starves the
game thread (guest ticks at a matched wall time are < 80 % of boot B's),
stop and hand back the table. Don't tune.

## Deliverable

`local/research/AU3/REPORT.md` (tables, commands, runner SHA ×2, suite
count, runner-dir check empty). `[AU3]` commit (`git add -f
local/research/AU3 local/muse/prompts/AU3.md`, `git log -1` first). Fork
commits stay on local `au3-snd`; no push.
