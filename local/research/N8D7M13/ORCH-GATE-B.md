# N8D7M13 Part B orchestrator gate — first Odin VRAM departure tick44 (2026-09-24)

Read Part B of REPORT and worker commit `c9dd26f6`. One install/launch of the released launcher
`50abff3d…a557`, clean cleanup. The logcat REPLAY gate failed on 88 dropped lines of the end-of-run
bulk flush (spans 297–350, 895–928); the on-device `parallel.hashes` (2050 rows, `c4195281…`,
2+2 SHA) was pulled read-only under the lease, and all 1,962 logcat rows agree with it. I accept
the hashes file as the row source; the logcat gate failure is a transport limit, not a replay fault.

| Odin STEP=1 vs Mac STEP=1 | Result |
| --- | --- |
| VRAM | ticks 1..43 equal; **first departure tick44**; 96/2050 equal |
| priv | 2050/2050 equal |
| present | first diff tick45 |
| PKTSEQ | equal on every intact row (Mac-side gaps only) |

Viewed `~/dev/ssx3-work/N8D7M13/step1-vs-mac.png`: the Odin frame is still mostly black with
block-shaped fragments. **Verdict A. Reading:** per-tick readback (a GPU sync each tick) does not
delay the departure, so the primary fault is an early, deterministic rendering difference at tick44
rather than a missing-sync race; the later run-to-run variance may be a second effect. Next: find
the packet(s) inside tick44 whose execution first changes Odin VRAM (handed to the N8X1 explorer).
