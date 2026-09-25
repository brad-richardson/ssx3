# AU8 — exploratory audio session: what the IOP mixes that we don't (Opus, 2 h, free rein)

You are an exploratory worker, approved by Brad on 2026-09-24. **You choose the experiments.** Goal: find why SSX 3's menu music sounds incomplete/"discordant" on our runtime, and ideally prototype the fix so Brad can hear it. Read `~/dev/AGENTS.md` (worker rules; the exploratory freedom here overrides "follow the brief exactly"), repo `AGENTS.md`, `local/AGENTS.local.md` (bytesize access, PCSX2 there), `docs/facts.md`, then `local/research/{AU2,AU3,AU4,AU6,AU7}/REPORT.md`, `local/research/AU7/midside.py`, and memory note on PINE (one PINE client at a time or PCSX2 dies).

## Facts to start from
- The music is EE-mixed PCM: 384 stereo s16 frames per sound tick in **tag 1** of a tag buffer the EE DMAs to the IOP each tick; tick ≈ 93.75 Hz of guest time, so 36 kHz. Brad confirmed 36 kHz sounds best of 36/44.1/48 k.
- Our runtime (fork `ssx3` `fb11e18`, sound HLE default-on) reproduces PCSX2's tag-1 PCM to 1 LSB on both channels (AU7). Yet Brad says **both** our clip and the PCSX2 tag-1 clip sound incomplete/"pitched down, discordant"; his first reaction to PCSX2's real speaker output was "ours is missing a few tracks".
- **Lead:** AU2's IOP table: tag 1 → `SNDIOP_mix` (IOP `0x705C` → mix at `0x6C2C–0x6C74`) **combines the IOP mixer slice (`MIX_audioslice`, 24 kHz, rate field `0x5DC0` at `+0x0E`) with the EE 36 kHz slice** via `SNDIOP_ee36_iop24_spu48`, output 48 kHz AutoDMA to the SPU2 core input. Tag 2 `SNDIOP_maincpufx` (EE-side effects), tag 3 `updatevoices`, tag 4 `parsedts`. AU2 saw no SPU uploads and an empty voice record in *our* HLE, but nobody checked whether PCSX2's IOP mixer slice (or effects/reverb on the core) carries audio. Our HLE plays tag 1 only.
- PCSX2 with our trace hooks is on bytesize (`~/pcsx2-g7`, AU4/AU6 hook scripts in `local/research/AU4/`, `~/au6`); `pcsx2-tag1-36k.wav` and a full-speaker video capture exist from different runs (they don't align; don't compare across runs).

## Suggested first moves (your call)
1. In **one PCSX2 run**, capture at the same time: tag-1 PCM (existing hook), the IOP mixer slice or the AutoDMA 48 kHz buffer the IOP writes to the SPU2 (IOP memory / `sceSdBlockTrans` source), and PCSX2's own audio output (SPU2 wav dump / recording). Then speaker − resampled tag 1 = what we're missing; listen to it and measure it.
2. If the IOP slice has music: find what feeds `MIX_audioslice` (IOP-side stream decode? a second XA/EA stream read by the IOP from CD? tag 2 effects?) from the IOP module code (IRX in the ISO/`~/dev/ssx3-work/E32-inputs/cd`) and PCSX2 traces.
3. Prototype the missing part in our sound HLE on a local branch (worktree `~/dev/ssx3-work/AU8/PS2Recomp` from `fb11e18`) and produce an aligned A/B against PCSX2's speaker output from the same scene.

## Rules
- bytesize: one heavy job at a time; don't disturb other lanes' dirs. PINE: one client. No upstream contact. Mac boots: one mini lease slot at a time (`local/tooling/p_lane_lease.py`; UP1, I29 and E55D16 are also using the mini — wait for a free slot, `nice` builds). No Odin, no iPhone.
- Code: local branch only, never push the fork, never `git add -f` inside it. Scratch `~/dev/ssx3-work/AU8/` ≤ 20 GB. No game audio or binaries in git.
- **Measure in stereo** (mid/side), align by NCC before comparing, never across different captures.
- Time box: 2 h from your first command, then write up (15 min).

## Deliverables (commit `[AU8] …`, explicit paths, `git add -f`, trailer `Orchestrated-By: Claude Code`, no push)
- `local/research/AU8/NOTEBOOK.md`, append-only, one row per experiment; commit it every ~30 min.
- `local/research/AU8/REPORT.md`: the best explanation with evidence rows; any prototype as a diff on your branch (SHA + `--stat`); listenable A/B files (≤ 5 MB `.m4a`, 48 kHz AAC) under `~/dev/ssx3-work/AU8/` with absolute paths for the orchestrator to send Brad; what's next; gaps. Label hypotheses as hypotheses.
