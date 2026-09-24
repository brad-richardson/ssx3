# N8D7M12 Part 7B orchestrator gate — PKTSEQ pair A: delivery equal, divergence downstream (2026-09-24)

Read the full Part 7B section of `REPORT.md`, `compare.py` and `compare-output.txt` for worker
commit `e9205cb7`. Two installs and two launches of the released launcher `5983f315…b934aa`, both
clean (lease, env 2+2 restore, force-stop, PID absent), battery 100% on AC (amended gate),
keyguard false.

Independent checks:
- Extracted the 41 `GB4_PKTSEQ tick=… seq=… commands=…` rows from `run1/pktseq.txt`,
  `run2/pktseq.txt` and the Mac ON control `N8D7M12P5F4P2/replay-excerpt.txt`: all three files
  are **byte-identical** (41/41 ticks 50..2050; tick2050 `79ee00a3024bfb44`, 1,737,496 commands).
- PPM SHAs re-read: run1 `65a544a7…fe82db`, run2 `d2261c63…9550b6`, Mac `9490484c…14fce3e`.
- **Viewed the three frames** (`~/dev/ssx3-work/N8D7M12P7/trio.png`): Mac is the full race frame
  (terrain, rider, HUD 00:00:05). Both Odin frames are ~95–99% black (non-black pixels 3,263 and
  10,334 of 229,376), with scattered rectangular fragments that differ between runs. Only
  ~25–29% of the surviving Odin pixels match the Mac. A quick block test could not establish
  GS-page alignment (too little content); no page claim is made.

| Field | run1=run2 | Odin=Mac |
| --- | --- | --- |
| PKTSEQ seq + commands | 41/41 | 41/41 (both runs) |
| priv | 41/41 | 41/41 |
| VRAM | 19/41, first split tick850 | 3/41, first split **tick50** |
| present | 25/41, first split tick850 | 0/41 |

**Verdict A. Reading per the predeclared rule:** the GS worker consumes an identical command
sequence (order, kinds, payload digest, count) on the Odin and the Mac, so delivery is ruled out
within the digest's limits (PrivWrite content opaque, 64-bit FNV). The divergence is downstream of
command consumption: paraLLEl renderer, Turnip/Adreno execution, or VRAM/scanout readback. Stop
adding input hashes (ARCH1).

Two separate features now stand out: (1) the Odin VRAM differs from the Mac **from the first
sample (tick50)** while two Odin runs agree up to tick800, so there is an early deterministic
difference; (2) from tick850 the Odin also differs from itself run to run. No GPU root cause,
image-correctness or speed claim.

Next (N8D7M13): per-tick VRAM rows (`PS2X_GS_REPLAY_STEP=1`) on the Mac and on the Odin to find
the first tick where the Odin departs from the Mac. The per-tick readback also acts as a sync
probe: if the Odin matches the Mac far longer with a readback every tick, missing GPU
synchronization is implicated.
