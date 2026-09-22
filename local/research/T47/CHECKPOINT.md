# T47 CHECKPOINT (pause 2026-09-22 ~15:25 local / 19:25 UTC)

Brief: `local/muse/prompts/T47.md` + orchestrator change (new Mission 2 =
Snow Jam loading-window trace, 99% stall; old healthy-series Mission 2
cancelled). E lane is live on this Mac (lease `e31l`, runner PID 55733) —
untouched; T47 holds no lease and runs nothing.

## Done

- **Mission 1 captures (COMPLETE, verified):**
  - F1 (Auto=OGL-HW on llvmpipe, T46-identical): full front-end chain
    title→menu→SC→ZC→SP→SM→SE-default→Down-walk(Happiness+Rival)→F9-SW.
    v1 script NO_ZC_PARKed on a true park (p1-p3 fade 1.36); resumed from
    live process, T47_DONE. 10 native 640x480 F8 shots.
  - F2 (full software renderer, F9@emu90.50 verified by OSD
    [SwitchRenderer]): v2 settle-robust script, T47_DONE first try.
    9 native 640x480 F8 shots.
  - Audio gate: H63 healthy (socket @up25, pactl 35/35 RDPSink @up105);
    F1/F2 cubeb negotiated, 0 CUBEB_ERROR, clean stop/destroy.
  - Pins reproduce T4/T46 (binary 6719f5d6, tree 9056c083, NVM da021d2a
    unchanged post-run, bindings, staged shas 4/4).
  - Mirrored 19 PNGs to `/Volumes/Extreme SSD/ps2x-t47/` and
    `/Volumes/share/ssx3/ps2x-t47/`; SHA read-1 done 19:17:15 UTC
    (matches fetch-time SHAs). Read-2 NOT yet done.
- **Mission 1 diffs (COMPLETE):** `/tmp/t47diff-scores.txt` (also copied to
  evidence dir): HWvsSW agree (0.7–1.8); recomp-vs-ref: title 11.5,
  menu 14.6 (BL 25.6 stray glyphs), SC 27.9 (missing Zoe model + strays),
  ZC 18.9 (BL 38.7 missing model), SE ~30 (map photo vs blue graphic).
  Recomp frame SHAs recorded (title 2ab49bac, menu 2c1d5cb7,
  SC-settled f61c826d, ZC aa355b87, SE-default e71fe999, SE-Happiness
  3f41e481). NOTE: brief's "Select Character …/frames-e31b-1/
  upload-latest.png" is stale — that file is now Setup Character; the
  settled SC frame is `frames-e31b-1/snap/snap-0089.44s.png`.
- **Mission 2 analysis (COMPLETE, no new boot needed):** T46 R3 trace
  (SSD sha re-verified 19c1b583) covers ENTER→race with % anchors
  (mr-post1 17%, mr-post3 97%, mr-post8 cinematic). Timeline mapped:
  ENTER edge emu 327.0; load burst 328 (EE thread-storm, CDVD 9.9K,
  SIF 89K); 448-chunk SPU voice upload 330.24–331.22 (1.75 MB);
  EE semaphore SPIN 332–337.5 (~210K GetThreadId + ~70K Wait/SignalSema
  per 0.5 s) while 990-iteration _sceCdSC read loop continues
  (cursor +3.2 MB, 327.13→339.98); burst-end 338; briefing idle;
  XCROSS edge ~432; first race frame ~435-436. LBN NOT in-trace (gap);
  RPC IDs only via sifcmd args + DMA flow (gap); no ioman I/O in window
  (all disc via _sceCdSC); zero ERROR/VSync lines in window.
- **Evidence:** `local/research/T47/` has 34 files (scripts, logs, polls,
  boot logs, dmesg×2, eventlog×2, NVM-post, pactl-post, diff scores,
  snap sizes, 3 Mission-2 tables). dmesg delta explained (--help
  SIGABRT probe + root login + drop_caches; no run crash).
- Bytesize left clean: C: staging removed, stray --help killed, WSL
  holder killed (idles off alone). Logs dir grew ~5 GB (F1 3.06 GB +
  F2 2.13 GB traces, both rotated on-box).

## In flight

- NOTHING running. No holder, no boots, no background tasks owned.

## Exact next step to resume

1. SHA read-2: `shasum -a 256 "/Volumes/Extreme SSD/ps2x-t47/"*.png`
   and compare to `/tmp/t47-ssd-sha1.txt` (if /tmp wiped, read-1 values
   are also in checkpoint context: menu 8d669dc3…, sc 078d30ac…,
   se-default f5b9f196… — else re-derive: read-1 = fetch-time SHAs in
   REPORT tables; mismatch discipline per AGENTS.md). Same for share
   tier vs `/tmp/t47-share-sha1.txt`. Write
   `local/research/T47/t47-ssd-manifest.txt` (19 paths + both SHAs).
2. Write `local/research/T47/t47-audiogate-h63.txt` (transcribed gate
   values, labeled: immediate @up25 socket-present full WSLg dir;
   delayed @up105 PULSE_SERVER=unix:/mnt/wslg/PulseServer, pactl 35/35
   RDPSink; post-run primary already in t47-pactl-h63-post.txt).
3. Write `local/research/T47/REPORT.md` (Mission-1 ref-vs-recomp table
   ×6 screens with per-region notes; PCSX2 settings table; F1/F2 run
   tables; Mission-2 timeline table emu 326–445 + read-loop/voice/
   spin findings + gaps: LBN, RPC payload IDs, Metro-City intermediate,
   wall↔emu ±1 s).
4. `git log -1` (several lanes commit to main), then
   `git add -f local/research/T47 local/muse/prompts/T47.md` (if brief
   not yet committed — check `git log --oneline -3` first; brief commit
   `1f4647f` exists, so only T47 dir), commit `[T47] …` with
   `Orchestrated-By: Muse Code` trailer, NO push.
5. Reply handoff: tables + recommended next action; orchestrator decides.
