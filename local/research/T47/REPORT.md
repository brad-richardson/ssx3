# T47 REPORT — PCSX2 reference frames for the recomp front-end screens + healthy Snow Jam loading window

Brief: `local/muse/prompts/T47.md` (+ orchestrator change: Mission 2 =
Snow Jam loading-window trace analysis of the T46 R3 trace; old
healthy-series Mission 2 cancelled). Mini resume 2026-09-22 evening:
paperwork only (SHA read-2, audio-gate note, this report, `[T47]`
commit); no new PCSX2 runs. Time box 1 h, met.

## T47-0. Pins (reproduce T4/T46)

| Pin | Value |
| --- | --- |
| PCSX2 | v2.9.75, savestate 0x9a590000 (`boot-t47.log`) |
| Binary sha256 | `6719f5d6ba5ac6c2c26a5954b12b837d0ff8d8e95ee6a83ed6b7b542cedee327` (reproduces T4/T46) |
| Tree | `9056c083` unchanged post-run |
| Inputs | ISO 3005415424 B + BIOS trio; NVM `da021d2a…865a961` unchanged post-run (`t47-nvm-post.txt`) |
| Bindings | Cross/Left as T46 (`PCSX2.ini` untouched) |
| Staged scripts | 4/4 shas reproduce |
| Game | SLUS-20772 (snap filenames) |

## T47-1. PCSX2 settings (T46-identical; `PCSX2.ini` not edited)

| Setting | F1 | F2 |
| --- | --- | --- |
| GS renderer | Auto = OGL-HW on llvmpipe | Full software (F9 toggle before attract-skip, `SW_FIRST`; no toggle-back, whole run SW) |
| Renderer proof | T46-identical path | OSD `[SwitchRenderer]` at emu 90.50 (`t47b-swcheck.jpg` in scratch; string not in saved text logs) |
| Resolution | Native (F8 native 640×480 shots) | Native (F8 native 640×480 shots) |
| Display | Xvfb :99, 1280×1024×24; xwd captures scored vs T27–T35 refs | Same |
| Input | Same button sequence as E31 (START, then Cross presses), movies skipped as a player would | v2 settle-robust script, `T47_DONE` first try |
| Movies | Intro movies skipped (player-style) | Same |

F1 path: v1 script `NO_ZC_PARK`ed on a true park (p1–p3 fade 1.36), resumed
from the live process (`t47-resume.sh`), `T47_DONE`. F1 T_BOOT wall
1790102337 (uptime 599); resume legs ZC→CONT→SP→SM→SE→Down-walk→mode
probe→F9 SW→kill. F2 T_BOOT wall 1790103235 (uptime 1497).

## T47-2. Audio gate: HEALTHY (H63)

Immediate @up25: PulseServer socket present + full WSLg dir (native
socket + pid + pulseaudio.log). Delayed @up105:
`PULSE_SERVER=unix:/mnt/wslg/PulseServer`, pactl 35/35, RDPSink. F1/F2
cubeb negotiated, 0 `CUBEB_ERROR` in all three stderr logs (re-verified
on resume), clean stop/destroy. Full transcription:
`t47-audiogate-h63.txt`; post-run primary `t47-pactl-h63-post.txt`.

## T47-3. F1/F2 capture tables

F1 (HW): 10 native F8 shots — title (14:40), menu (14:41), sc (14:41),
then resume: zc (14:45), sp (14:46), sm (14:47), se-default (14:47),
se-walked (14:48, Down-walk Happiness+Rival), se-final (14:48), plus
F9-SW re-capture se-sw. F2 (SW): 9 native F8 shots — title (14:55),
menu (14:56), sc (14:57), zc (14:57), sp (14:58), sm (14:58),
se-default (14:59), se-walked + se-final (15:00).

Chain covered: title→menu→SC→ZC→SP→SM→SE-default→Down-walk
(Happiness+Rival)→F9-SW. All 19 PNGs mirrored to
`/Volumes/Extreme SSD/ps2x-t47/` and `/Volumes/share/ssx3/ps2x-t47/`,
19/19 SHA match on read-1 and read-2 (`t47-ssd-manifest.txt`).

## T47-4. Reference-vs-recomp diffs (Mission 1 deliverable)

Method (`t47-diff.py`, committed): resize PCSX2 640×480 ref to recomp
512×448 (LANCZOS), then whole-frame + 5-region mean/p99 of per-pixel
|Δ| (t44-cropdiff metric, PIL port). Numbers below are
`mean/p99`; HW = F1 ref, SW = F2 ref.

Recomp base: `/Volumes/Extreme SSD/ps2recomp-spike/P1/run`, all
512×448 `fbp=112`.

| Screen | Recomp frame (sha prefix) | Ref HW (sha) | Ref SW (sha) | Whole HW | Whole SW | HWvsSW |
| --- | --- | --- | --- | --- | --- | --- |
| title | `frames-e29b-1/upload-latest.png` (`2ab49bac…`) | `t47-shot-title.png` (`935390b6…`) | `t47b-shot-title.png` (`b35eb0b4…`) | 11.48/166 | 11.76/166 | 0.896/10 |
| menu | `frames-e31d-1/snap/snap-0059.99s.png` (`2c1d5cb7…`) | `t47-shot-menu.png` (`8d669dc3…`) | `t47b-shot-menu.png` (`86c34fa3…`) | 14.60/135 | 14.74/135 | 0.729/9 |
| SC (settled) | `frames-e31b-1/snap/snap-0089.44s.png` (`f61c826d…`) | `t47-shot-sc.png` (`078d30ac…`) | `t47b-shot-sc.png` (`53900143…`) | 27.92/161 | 28.15/161 | 1.786/35 |
| ZC | `frames-e31b-1/upload-latest.png` (`aa355b87…`) | `t47-shot-zc.png` (`0e205582…`) | `t47b-shot-zc.png` (`bed08ad7…`) | 18.85/137 | 18.82/137 | 1.177/24 |
| SE-default | `frames-e31d-1/snap/snap-0209.97s.png` (`e71fe999…`) | `t47-shot-se-default.png` (`f5b9f196…`) | `t47b-shot-se-default.png` (`e3f0ee52…`) | 30.89/154 | 31.15/154 | 0.869/8 |
| SE-Happiness | `frames-e31d-1/upload-latest.png` (`3f41e481…`) | `t47-shot-se-walked.png` (`8b216a8c…`) | `t47b-shot-se-walked.png` (`4156faf8…`) | 30.25/154 | 30.33/154 | 0.753/5 |

Per-region scores (TL/TR/BL/BR/center) + first-pass notes (visible
differences only; orchestrator reads both images):

- title/HW: TL 11.53/109 TR 9.75/120 BL 12.70/198 BR 11.93/218 center
  15.41/131 (SW near-identical). Fairly uniform; center highest.
- menu/HW: TL 10.03/108 TR 9.23/164 BL 25.64/129 BR 13.50/160 center
  13.64/152 (SW same pattern, BL 25.55). BL outlier = stray glyphs
  region, matching the recomp's suspect corner fragments.
- sc/HW: TL 34.70/132 TR 21.24/161 BL 33.70/152 BR 22.03/183 center
  21.57/161 (SW same). TL+BL ≈ 34 = missing Zoe rider model side plus
  corner stray fragments; recomp stat bars all 1.0 with one cell.
- zc/HW: TL 14.81/126 TR 10.65/137 BL 38.73/148 BR 11.20/141 center
  10.99/121 (SW BL 39.01). BL outlier = missing rider model.
- se-default/HW: TL 20.20/143 TR 37.72/160 BL 29.12/117 BR 36.49/201
  center 50.82/162 (SW same). Center ≈ 51 = map photo vs blue graphic;
  TR/BR also high.
- se-happiness/HW: TL 19.76/143 TR 37.63/160 BL 27.36/117 BR 36.24/201
  center 50.82/163 (SW same). Same pattern as SE-default.

HW-vs-SW agree (0.7–1.8 whole): the reference is renderer-independent;
recomp-vs-ref gaps are recomp-side or correct-behavior differences, not
PCSX2 renderer artifacts. Full scores: `t47diff-scores.txt`.

Note: the brief's "Select Character …/frames-e31b-1/upload-latest.png"
is stale — that file is now Setup Character; the settled SC frame is
`frames-e31b-1/snap/snap-0089.44s.png` (used above).

## T47-5. Mission 2 — healthy Snow Jam loading window (T46 R3 trace, no new boot)

Trace pin: `emulog-t46r3.txt` 2682545633 B,
sha `19c1b583…ae84` (SSD re-verified at pause). The run's live race is
Snow Jam (T46 REPORT), so this ENTER→race window is the healthy
counterpart of the E31 stall. Emu-time timeline (wall↔emu ±1 s):

| Emu s | Observation |
| --- | --- |
| 327.0 | ENTER edge: SIF DMA burst starts (`sceSifSetDma`, Sif-1 IOP transfer) |
| 328 | Load burst: EE thread-storm (GetThreadId ~65K, ReferThreadStatus ~51K, RotateThreadReadyQueue ~50K/s), CDVD ~9.9K, SIF ~89K lines/s |
| 330.24–331.22 | 448-chunk SPU voice upload, 1.75 MB |
| 332–337.5 | EE semaphore SPIN (~210K GetThreadId + ~70K Wait/SignalSema per 0.5 s) while the 990-iteration `_sceCdSC` read loop continues (cursor +3.2 MB, 327.13→339.98) |
| 338 | Burst-end (thread-storm and read loop subside) |
| 338–432 | Briefing idle |
| ~432 | XCROSS edge |
| ~435–436 | First race frame |
| anchors | mr-post1 17%, mr-post3 97%, mr-post8 cinematic (T46 % series) |

Findings: all disc I/O in-window goes through `_sceCdSC` (no ioman
I/O); RPC linkage only via sifcmd args + DMA flow; zero ERROR/VSync
lines in-window. Gaps: LBN not in trace; RPC payload IDs not decoded;
Metro-City intermediate legs not covered; wall↔emu mapping ±1 s.
Evidence: `t47m2-halfsec-326-342.txt`, `t47m2-keyagg-326-445.txt`,
`t47m2-secmix-327-340.txt`, `t47-window[23].py`, `t47-tail.py`,
`t47-runs.py`.

## T47-6. PCSX2 loading-window facts for the E31 Snow Jam 99% stall

E31 stall signature (from `local/research/E31/CHECKPOINT.md`): live
loop, zero CD reads after ~478 s, pump `0x27CEA8` fan-out via
`0x27D330`/`0x284B58` @43.5k/s, park t1 Ready `pc=0x423dc8`. Healthy
facts from §T47-5, no verdict:

| # | Healthy-window fact (PCSX2, Snow Jam ENTER→race) | What it bounds for E31 |
| --- | --- | --- |
| 1 | ENTER→first-race-frame completes in ~109 emu-s (327→436), all phases bounded | Stall at 99% with zero CD reads after ~478 s has no healthy counterpart — the healthy load never idles that long with the disc quiet |
| 2 | Disc reads run as one continuous 990-iteration `_sceCdSC` loop, cursor advancing +3.2 MB through emu ~340 | A healthy load keeps the read cursor moving into the briefing; a parked cursor + silent CDVD at 99% points at the read-loop exit/ready handshake, not the streaming itself |
| 3 | EE semaphore SPIN (332–337.5) overlaps continued disc reads, then ends at burst-end 338 | EE spinning while CDVD is active is normal mid-load; spinning with zero CD reads is the anomalous combination to match in the recomp |
| 4 | 448-chunk SPU voice upload (1.75 MB, 330.24–331.22) precedes the spin phase | If the recomp's SPU upload never completes/fires, the downstream wait would present as a late-% stall |
| 5 | Zero ERROR/VSync lines in the whole window; XCROSS edge ~432 then race frames ~3–4 emu-s later | The healthy %→race transition is input-edge-gated and fast; a 99% park past it is past all healthy wait sites |
| 6 | LBN + RPC payload IDs not in trace (gaps) | These are the two blind spots: a wrong-LBN or unanswered-RPC stall canno
...[truncated 2085 chars]