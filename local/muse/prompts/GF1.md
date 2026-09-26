# GF1 — split the GS frontend off the MTVU unit thread (Opus, design first, ≤ 6 h)

## Goal
With MTVU + LAG, the **unit thread gates the Odin frame** (CP1 Table 2: 30.1 ms running before VR4's SIMD core; VR4 D1 measured ~21 ms after). Brad wants ~0.9× (≈ 18.5 ms/frame). The unit thread runs VIF1 parsing, VU1, **and** the GIF arbiter + GS frontend (`GS::processGIFPacket` → `GsWorker::enqueue`, MT1 design §2). Moving the GS frontend onto its own thread (a second stage in the pipeline, fed in stream order) could take several ms off the critical path — if the frontend's share is real and the ordering stays exact. Determine the share, design it, build it behind a knob, prove it det-identical and GS-stream-identical, measure.

## Facts
- MT1 (`local/research/MT1/REPORT.md` design §§1–7, stages 2′–4): the unit owns VIF1 → VU1 → GIF → GS frontend; determinism from ownership + sync points (VBlank, CSR reads, priv writes, save/load); the census tooling (`PS2X_MTVU=census`) and the `[pk]` GS-packet-stream comparator (`PS2X_PKLOG=1`, 1.99 M packets identical in MT1 stage 3).
- CP1 Table 3 + VR4 Table 1 (`local/research/VR4/REPORT.md`): unit on-cpu split — VU1 generated code, `commitReadyPipelines`, `processVIF1DataImpl`, `progressXgkick` (children 24.7 % incl. the GIF/enqueue path), libc, kernel. **First measure the GS-frontend share on the unit thread** (Mac `xctrace`/`sample` on the play knobs with MTVU, and PT1's tool or CP1's capture for the Odin) — if it's < ~2 ms/frame on the Odin, stop and hand back.
- Constraints: exactness (det-hash IDENTICAL to the current key; GS packet stream byte-identical knob on vs off; jitter stress), paraLLEl's GsWorker is already another stage downstream; PATH1/2/3 arbitration order must be unchanged (RR1's PATH3 lesson).
- Fork `ssx3` tip `b97b241`. Build/boot/lease tools as usual (`mac_build.sh`, `bradflix_build.sh`, `ssx3_boot.py`, `odin_lease.sh`, `bytesize_lock.sh`).

## Stages
1. Measure + design (commit): the share, the queue boundary (after the arbiter drain? packet-level?), sync points, what the GS frontend reads/writes that the EE or unit can observe.
2. Implementation behind `PS2X_MTVU_GSTHREAD=1` + gates (det, packet stream, jitter, 512 KB) + Mac ABBA. 3. One Android build + Odin pair on the play settings. Stop and hand back.

## Deliverable
`local/research/GF1/REPORT.md` + `[GF1]` commits (explicit paths, `git add -f`, trailer `Orchestrated-By: Claude Code`), no push.
