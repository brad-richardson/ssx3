# AU6 — Why our EE mix is ~12 dB quieter than PCSX2's

You are a worker in a herdr pane in the ssx3 repo (`~/dev/ssx3`, Mac mini;
PCSX2 on bytesize via `ssh bytesize` → `wsl -d Ubuntu -- bash -s`). Follow
`~/dev/AGENTS.md`. **Tables + receipts; recommend, the orchestrator
decides.** Read first:
- `AGENTS.md`;
- `local/research/AU2/REPORT.md` (the protocol tables, the status block,
  the tag buffer);
- `local/research/AU4/REPORT.md` (the PCSX2 hook recipe, Parts 1–2: build,
  replay-preservation proof, T48 route capture);
- `local/research/AU5/REPORT.md` (our capture, the census, the function
  chain).

Write scope: `local/research/AU6/`, `~/dev/ssx3-work/AU6/`, a fork worktree
`~/dev/ssx3-work/AU6/PS2Recomp` on local branch `au6-snd` from AU5's
`au5-snd` `ddf4f66`, bytesize `/home/brad/pcsx2-g7/` (a new `au6` hunk set on
top of AU4's, keeping `pre-au6/` copies) and `/home/brad/au6/`, and the
lease files. No push.

## Facts (orchestrator-measured)

- Loudness profile, RMS per 5 s:
  - AU5 (ours, 3 missing SND functions restored) stays flat at
    **~1,300–1,500** through menus and race;
  - PCSX2's tag-1 mix is **~4,500–8,600** in menus and race;
  - AU2 (ours, before the functions were restored) was ~5,000.
- So we're ~12 dB low, and Brad hears it as "only half the audio". Stereo
  is fine (L/R balanced, correlation ~0.93).
- The restored `0x3c9520` is the looping stream reader: it reads samples
  via `0x3CDE68`, advances the position `[s0+0x20]`, and at the end seeks
  to the loop start `[s0+0x24]` (`0x3CE0B8`, `0x3CDDE8`). It was skipped in
  AU2.
- Suspects:
  - (1) a music stem or voice missing from the mix (EA MPF plays a main
    track plus loop stems, e.g. `plloops0.mus` next to `poorleno.mus`);
  - (2) a volume taken from IOP state: our HLE fills only the serial in
    the 0x240-byte status block at EE `0x50B740`, while real SNDDRV
    fills the rest;
  - (3) a per-voice volume computed wrong (untested MMI/VU0 ops in the
    mixer: AU5's census).

## Work

1. **Status block (cheapest):** in PCSX2, dump the 0x240-byte block at
   `0x50B740` on every SND tick for the first ~2,000 ticks (extend AU4's
   hook, log-only and env-gated). Table the non-zero fields and how they
   change over time. Compare with ours (zero except the serial).
2. **Mixer state differential:** locate the mixer's voice/stream table.
   Follow the driver `0x3C85D0`/`0x3C8968` and the per-stream objects
   (`+0x1C` handle, `+0x20` position, `+0x24`/`+0x28` loop points).
   Dump that table (addresses, active flags, volumes, stream handles and
   positions) at the same menu moment in PCSX2 and ours; use a bounded
   dev tap in our runtime (default off). Table which voices/streams are
   active on each side and their volumes.
3. **Name the difference.** If it's the status block, implement the
   fields SNDDRV provides (from SNDDRV's disassembly in AU2) in our HLE.
   If it's a missing voice, find why it isn't started. If it's a volume,
   name the instruction. One candidate fix plus one validation capture,
   then compare the loudness profile and `compare.py` against PCSX2 over
   the longest common menu stretch. Use the E33 route for the capture (its
   menus are long) so the overlap is ≥20 s.
4. Make a ≤5 MB `.m4a` of the validation capture for Brad.

## Budgets and stop rules

≤2 PCSX2 builds + ≤1 PCSX2 capture (bytesize, one heavy job at a time);
≤3 Mac builds, ≤3 boots (one slot each, escalated, wait for a free slot);
6 h; cap 6 GB. Stop and hand back the tables if step 3 doesn't name a
single mechanism.

## Deliverable

`local/research/AU6/REPORT.md` (tables, commands, SHAs ×2,
before/after loudness profile). `[AU6]` commit (`git add -f
local/research/AU6 local/muse/prompts/AU6.md`, `git log -1` first).
