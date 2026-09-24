# AU4 — PCSX2 reference capture of SSX 3's EE sound mix, compared with ours

You are a worker in a herdr pane in the ssx3 repo (`~/dev/ssx3`, Mac mini;
PCSX2 on bytesize via `ssh bytesize` → `wsl -d Ubuntu -- bash -lc "…"`).
Follow `~/dev/AGENTS.md`. **Tables + receipts; recommend, the orchestrator
decides.** Read first:
- `AGENTS.md`;
- `local/AGENTS.local.md` (bytesize row: one heavy job at a time);
- `local/research/AU2/REPORT.md` (the protocol tables; AU2-3's capture);
- `local/research/T65/REPORT.md` §T65-1/T65-2 (how the T-lane patches PCSX2
  and drives the T48 route; the race statefile);
- `local/research/T48/REPORT.md` (the route) if T65 isn't enough.

Write scope: `local/research/AU4/` (report, scripts, small receipts);
`~/dev/ssx3-work/AU4/` (captures, analysis); on bytesize, `/home/brad/pcsx2-g7/`
(a new `au4` hunk set on top of the T65 tree, keeping `pre-au4/` copies of
every file you touch) and `/home/brad/au4/`. Everything else is read-only.
No mini lease is needed (PCSX2 on bytesize).

## Why

Brad listened to AU2's capture (`~/dev/ssx3-work/AU2/run/au2b-ee-mix-36k.wav`,
the EE's tag-1 PCM from our runtime): the music is **recognizable but
distorted**. The orchestrator's quick stats on 50–110 s:
- no clipping;
- no duplicate blocks;
- the mean |Δsample| at the 384-frame tick seams is **1.56×** the mean
  elsewhere;
- about 3,940 zero crossings/s, which suggests high-frequency content.

Candidate causes, each with what tells it apart:
- **(1) Tick rate:** the spike ticked at 59.94 Hz, not 93.75 Hz, so the
  EE's stream position and the mix could slip at the seams. Predicts: the
  distortion is concentrated at the seams, and PCSX2's seam ratio is ~1.0.
- **(2) Decode or mix arithmetic** (MMI/FPU/VU0-macro semantics in the
  recompiled EA-XA decoder `sub_003CCA08` or the mixer). Predicts:
  broadband error everywhere, not tied to the seams.
- **(3) Capture artefact** (lldb read a buffer mid-write). Predicts: a
  few corrupt records, not a steady error.

## Work

1. **PCSX2 hook** (log-only, env/arm-file gated like T65): when the EE
   sends the SND tag buffer to the IOP (SIF1 DMA / syscall 0x77 with EE
   source `0x512E40`, per AU2's transport table; confirm the address in
   PCSX2), append the 0x620 bytes (tag-1 header + 384 stereo s16 frames +
   tag-5 serial) to `/home/brad/au4/pcsx2-tag1.bin`, with the EE vsync.
   One build. Replay-preservation check as in T65-3 (the 7 PNG md5 and
   HWSTAT exact) to prove no behaviour change.
2. **Capture:** the T48 route from boot through the menus (charsel music)
   into the race, ≥150 s of music, the same stretch as AU2's au2b.
   Also record one **listenable PCSX2 audio file** of the same stretch
   (PCSX2's own audio dump or video-capture audio; name the method) and
   convert it to ≤5 MB `.m4a` in `~/dev/ssx3-work/AU4/`.
3. **Compare** (Mac, a script in `local/research/AU4/`):
   - convert the PCSX2 records to a 36 kHz WAV (de-dup on serial, the same
     as `au2_pcmcap.py`);
   - align with AU2's au2b WAV on the menu music start (cross-correlation;
     report the lag);
   - table: bit-exact frames %, gain ratio, the RMS of the difference
     over the RMS of the signal, the difference spectrum in bands
     (0–2k, 2–6k, 6–12k, 12–18k), and the seam ratio + zero crossings/s
     for **both** captures;
   - make a spectrogram pair PNG;
   - if the race tracks differ (EA Radio shuffle, AU2 G5), compare only
     the menu section.
4. If AU3's host-stream WAV exists by then
   (`~/dev/ssx3-work/AU3/run/`, 93.75 Hz guest-clock tick), run the same
   table on it too.

## Budgets and stop rules

1 PCSX2 build (+1 if the first hook doesn't fire), ≤2 captures, 4 h, cap
6 GB. Check `pgrep -f "gradle|ninja|clang|pcsx2"` on bytesize before
building or capturing. If the menu sections can't be aligned (lag
correlation < 0.5), stop and hand back both spectrograms plus the first
100 tag-1 records' stats from each side.

## Deliverable

`local/research/AU4/REPORT.md` (tables, commands, PCSX2 binary SHA ×2,
patch diff, capture SHAs, PNGs ≤5 MB). `[AU4]` commit (`git add -f
local/research/AU4 local/muse/prompts/AU4.md`, `git log -1` first). Don't
commit audio; give the `.m4a` paths.
