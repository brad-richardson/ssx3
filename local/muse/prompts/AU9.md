# AU9 — race sound effects on SPU2 hardware voices (Opus exploratory, 3 h)

You are an exploratory worker, approved by Brad on 2026-09-24. **You choose the experiments.** Goal: make our runtime play the race sound effects that PCSX2 plays on SPU2 hardware voices, with an aligned A/B Brad can hear. Read `~/dev/AGENTS.md` (the exploratory freedom overrides "follow the brief exactly"), repo `AGENTS.md`, `local/AGENTS.local.md`, `docs/facts.md`, then `local/research/AU8/{REPORT.md,NOTEBOOK.md}` (E10 especially), `local/research/AU2/REPORT.md` (IOP sound driver map + `snddrv-disasm.txt`), `local/research/AU3/REPORT.md` (our sound HLE), `local/research/T47/REPORT.md` (1.75 MB SPU upload at Snow Jam load).

## Facts
- Music: tag-1 planar PCM (AU8, folded in fork `ssx3` `f949ff0`, confirmed by Brad).
- AU8 E10 (PCSX2 Snow Jam race, SPU2 tap): SPU2 **voices** active in races (dry0 625 / dry1 545 RMS over 60 s, wet 0), intermittent bursts from t≈22 s, 94% energy < 1 kHz, near-mono, −15.5 dB of output. Likely SFX. Our HLE has **no SPU voices**: it plays tag 1 only.
- IOP side (AU2): cid-0 command packets → `SNDIOP_dmqueue` → `SNDIOP_dmtransfer` → **`sceSdVoiceTrans`** (IOP RAM → SPU RAM uploads); tag 3 `SNDIOP_updatevoices` (0x2A8-byte voice-parameter record each tick); tag 2 `SNDIOP_maincpufx`. Our HLE currently accepts cid-0 packets and SetDma but plays nothing.
- PCSX2 with the AU8 SPU2 tap is on bytesize (`~/au8`, `~/pcsx2-g7`; `au8_race_cap.sh` reaches a Snow Jam race). PS2Recomp is GPL: reusing PCSX2 SPU2 code (ADPCM decode, ADSR, voice mixing) is allowed if the licence versions are compatible (check and record) and every reused file keeps attribution.

## Suggested path (your call)
1. Characterize in PCSX2: which SPU RAM uploads happen (sizes, SPU addresses, when), what the tag-3 records contain per tick (key on/off, pitch, volumes, ADSR, start address) and which SPU2 register writes `SNDIOP_updatevoices` turns them into. Decode the record layout from the IOP code + the PCSX2 tap/trace, not guesses.
2. Implement in our sound HLE on a local branch (worktree `~/dev/ssx3-work/AU9/PS2Recomp` from fork `ssx3` `f949ff0`): SPU RAM (2 MB) fed by the cid-0 uploads, 24/48 voices with PS-ADPCM decode, pitch, ADSR, volume, key on/off from tag 3, mixed with the tag-1 music into the host stream (host stays 36 kHz or moves to 48 kHz with the SNDDRV 3→4 resample; your call, labelled). Unit tests for ADPCM decode and ADSR against known vectors.
3. Validate: our race boot's voice layer vs PCSX2's (same route; align by events, not wall time), plus music unchanged (planar music still bit-exact). Produce A/B clips.

## Rules
- bytesize: one heavy job at a time (TL1 may be building an APK there; wait for it). PINE: one client. Mac boots: one mini lease slot (`p_lane_lease.py`; I30 and TL1 share the mini). No Odin, no iPhone.
- Local branch only; never push the fork; never `git add -f` inside it. Scratch `~/dev/ssx3-work/AU9/` ≤ 20 GB. **No PNG/WAV/audio or game data in git** (text receipts only). No upstream contact.
- Measure in stereo, align by NCC or events within one capture/boot, never across captures.
- Time box 3 h from your first command, then write up (15 min). Notebook committed every ~30 min.

## Deliverables (commit `[AU9] …`, explicit paths, trailer `Orchestrated-By: Claude Code`, no push)
- `local/research/AU9/NOTEBOOK.md` (append-only), `local/research/AU9/REPORT.md` (explanation, evidence rows, prototype diff SHA + `--stat`, suite result, runner-dir check, what's left, gaps; hypotheses labelled).
- Listening clips (≤ 5 MB `.m4a`, 48 kHz) under `~/dev/ssx3-work/AU9/` with absolute paths: our race audio before/after and PCSX2's race output from the same scene.
