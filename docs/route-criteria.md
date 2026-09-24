# Route-comparison criteria: host replay vs PS2 recomp for 120 Hz

Steering 09-22 (Brad, progress review): the milestone is STOCK SSX 3
GAMEPLAY through our PS2 static recomp runtime ON ODIN; the eventual
goal is 120 Hz, ideally TRUE 120 Hz SIMULATION (not merely 120
presents — physics/timer/input/animation/audio at ~2× stock cadence,
pacing measured independently). The "either 60 or 120 Hz simulation"
reading below is superseded; the "Neither has happened" snapshot is
stale (PS2 has visible UI + a located movie stall; NetherSX2 is
reference-only). Tables retained as GameCube-side evidence; PS2
column fills from the new milestones (native stock race → Odin
gameplay → 120 Hz baseline → true sim). See
`docs/research/review-2026-09-22-progress-and-parallelization.md`.

Source mandate: Part 1 §7 rec 10
(`docs/research/review-2026-09-19-progress.md:247-251`): write the
criteria NOW against measured numbers; decide nothing. Part 4
decision 4 (`review-2026-09-19-progress.md:618`) governs timing: this
doc does NOT need the PS2 first frame — GameCube numbers now, PS2
column blank. (An older backlog note at `docs/todo.md:2980-2985` said
the doc needs the first frame for the comparison; the Part 4 steering
read supersedes it.)

Comparison point (rec 10, fixed quotes):

- "host replay shows an interpolated frame on the Odin"
- "PS2 shows a first frame with a real GS census"

Neither has happened. This doc holds criteria + GameCube-side measured
numbers + a blank PS2 column. It makes no route recommendation; the
decision is explicitly deferred to the comparison point (see
Decision-point table).

## Budget table: Odin frame-time budget (B)

| ID | Criterion (what is measured) | How (tool / command / trial) | Pass bar | GameCube measured + pointer | PS2 |
| --- | --- | --- | --- | --- | --- |
| B1 | Host-replay video-thread cost per replayed frame | D2/S2 replay-capacity trial: 200 back-to-back replays at one seam, `Flush`+`WaitForGPUIdle` per replay, ms/replay median + p95 | ≤ 6 ms per replay (S2 gate, `docs/reserve/plan-120fps-2026-09-17.md:101`) | 0.665 / 0.866 / 0.806 ms median (p95 0.729 / 0.963 / 0.874), 200/200 `done`, two arms + third arm, EGL (`docs/numbers-ledger.md:69,71`; `local/research/S2/REPORT.md:27-28`) | BLANK — needs PS2 replay-equivalent or recomp frame-time receipt (see Blank table) |
| B2 | 8.33 ms composition: update pair + render + system, sustained, 1× internal | F-trial / callback probe on device: paired update+render CPU per frame | < 8.33 ms sustained (`docs/todo.md:832-833`) | Phone F-trial pair+render ≈ 12 ms at 1× (`docs/todo.md:873-875`); Odin stock update 3.19 ms med + render 7.93 ms med = 11.1 ms CPU per 60 Hz frame, render p95 11.00, max 20.7 (`docs/numbers-ledger.md:66`) | BLANK — needs PS2Recomp per-frame EE/GS/VU thread times |
| B3 | Per-frame ms bars at 1×/2×/Match detail-output combos | Output-resolution phone trials: extra-draw wall + thread CPU, displays/s per combo | Pacing bars per combo (B5), no load-protection exit | Full/1× extras: wall med 8.638 ms (52 samples) and 11.858 ms (3 samples) (`docs/research/120hz-output-resolution.md:44-47`); Half/2×: 102.94/112.67 displays/s over 8.92/18.38 s (`docs/todo.md:755-757`); Half/1×: 117.22 displays/s over best 7.75 s warmed window (`docs/todo.md:758-760`); Match/2×: load-limited after 3.49–13.55 s (`docs/todo.md:764-766`) | BLANK — needs PS2 1×/2×-equivalent frame-time split |
| B4 | Trial shape: continuous warmed evidence | `tools/mobile_pacing_check.py` steady window: exclude first 2 s + last 0.5 s, require 25 continuous s | 25 continuous warmed seconds (`docs/research/120hz-pacing-acceptance.md:16-22`) | Longest warmed span 15.88 s at 114.34 displays/s (`docs/todo.md:756-758`); no 25 s window exists in any collection (`docs/research/120hz-pacing-acceptance.md:123-136`) | BLANK — needs a 25 s PS2 paced window |
| B5 | Pacing bars: rate + spacing + speed | Display-present timestamps (`presentedTime`) per window; SF timestats on Odin (`part3/sfstats.sh`) | ≥ 117/s, med ≤ 8.6 ms, p95 ≤ 10 ms, p99 ≤ 17 ms, speed ≥ 0.98× (`docs/research/120hz-pacing-acceptance.md:27-38`) | Old smoothing trial (Odin): 75–91 presents/s, med 16.5 ms (`docs/numbers-ledger.md:91`); uncapped no-trial: med 8.5 ms (`docs/numbers-ledger.md:91`); phone bursts: 117.22/s over 7.75 s (`docs/todo.md:758-760`), combined-kind fps peaked 102 (`docs/todo.md:889-893`); no sustained pass | BLANK — needs PS2 present-timestamp series |
| B6 | 60 Hz base holds 1.0× under cap | Capped-1.0 race arms, HUD-anchored pace + busy fractions | 1.00× full race, both anchors | Snow Jam holds 1.00×; Crow's Nest opens 0.82–0.84× for 51 s then locks 1.00× (`docs/numbers-ledger.md:58`); control re-run opens ~0.90×, condition-dependent (`docs/numbers-ledger.md:70`); capped busy emu 0.58 / video 0.27 ≈ 9.7 / 4.5 ms per frame (`docs/numbers-ledger.md:62`) | BLANK — needs PS2Recomp capped-1.0 race pace |
| B7 | Harness + config deltas on the budget | det-none vs det-GPU A/B; Null-video arm; clock/thermal sampler | Recorded as deltas, not bars | det-none +7% race pace (`docs/numbers-ledger.md:60`); Null video = base pace, video busy unchanged (`docs/numbers-ledger.md:61`); cpu7 parks at 3.28 GHz floor under cap (`docs/numbers-ledger.md:58,70`) | BLANK — needs PS2Recomp determinism/config deltas |
| B8 | Thermal guard | Thermal state sample per window; Odin `cpu-*` zones + throttle ticks | Nominal/fair, never serious/critical (`docs/research/120hz-pacing-acceptance.md:35`); Odin zero throttle ticks | Odin: `cpu-1-1-1` reads 104.7 °C clamp, cpu7 ≥ 3.28 GHz, zero throttle ticks (`docs/numbers-ledger.md:65`); spin pacer +10 °C, null effect (`docs/numbers-ledger.md:70`); phone: most collected samples serious (`docs/todo.md:760-761`) | BLANK — needs PS2Recomp thermal-window receipt |

## Correctness table: visual-correctness receipt (C)

| ID | Criterion (what is measured) | How (tool / command / trial) | Pass bar | GameCube measured + pointer | PS2 |
| --- | --- | --- | --- | --- | --- |
| C1 | Interpolated-motion distinctness: synth vs truth | M15 3-phase capture (mid/full/identical runs) + masked-SAD synth-vs-truth diff; blended-extras counters on device | synth==blend; residual below display LSB; blended > 0 | synth==blend, residual 13418 B = 2.34% of blend, 87% of residual at \|d\|=1, static 95.67% exact (`docs/numbers-ledger.md:220`; `local/research/M15/REPORT.md:260-261,274-275,343`); M16–M63 close: 0 B explained by rule, 102 far-tail bytes stand, below display LSB (`docs/numbers-ledger.md:97`); iPad fixed build 35/36 + 30/30 blended (`docs/todo.md:502-505`); desktop 202/203 blended (`docs/todo.md:506-508`); phone distinct-motion still open (`docs/todo.md:767-768`) | BLANK — needs PS2 synth-vs-truth analog (no queued brief) |
| C2 | Static-wall MAE | Reprojection batch: offline half-step warp vs truth on static geometry | MAE < 0.02 units (recorded bar, `docs/todo.md:693-695`) | Static-wall MAE under 0.02 units on the calm frame (`docs/todo.md:693-695`) | BLANK — needs PS2 static-geometry warp MAE |
| C3 | HUD/alpha exactness | Paired-background HUD alpha: three movie-driven runs (natural/black/white), tail solved per pixel | Exact solve, every pixel within 2 levels of untouched run (`docs/todo.md:699-703`) | Solved exactly on frames 7500-7507: 7.04% coverage, mean alpha 0.727, every pixel within 2 levels (`docs/todo.md:699-703`); EFB is RGB8_Z24 with no destination alpha (`docs/todo.md:702-703`) | BLANK — needs PS2 HUD-layer isolation receipt |
| C4 | Artifact bars: holes, scorer, side effects | Footprint-splat coverage; `tools/gamecube_snow_check.py`; M5 fail-closed counters per replay | Holes closed ≥ 77%; snow < 0.12; zero accumulating side effects | Footprint splat closes 77–81% of point-splat holes; uncovered 0.44% calm frame, 1.2–2.4% on movie pairs p95 motion 76–128 px (`docs/todo.md:693-698`); snow clean ≤0.05/≤0.08, corrupt ≥0.17/≥0.38, threshold 0.12 (`docs/numbers-ledger.md:36`); M5: `xfb_equal` 200/200, `dpend`/`pediff`/`vidiff` 0, `dtex` −7…+1 no accumulation, `dframe` +1/replay unresolved (`docs/numbers-ledger.md:83`) | BLANK — needs PS2 artifact bars + GS side-effect counters |
| C5 | Guest-clean continuation | Watched-window compare + post-replay ride-on; update `position_changed` gate | Window unchanged, guest rides on, zero GPU-command errors | Desktop: watched window unchanged, guest rides on cleanly, zero GPU command errors (`docs/numbers-ledger.md:57`); Odin D6: all updates `position_changed` (`docs/numbers-ledger.md:66`); M5 det=1 counters clean (`docs/numbers-ledger.md:83`) | BLANK — needs PS2 post-frame guest-state receipt |

## Work table: remaining-work estimate (W)

Size class quotes the backlog's own sizing (brief time-box, XS/S/M) or
`unsized` where the backlog states none. GameCube rows from the open
120 Hz backlog; PS2 rows from the live queue to first frame
(`docs/todo.md:8-10`).

| ID | Route | Open item | Size class | Pointer |
| --- | --- | --- | --- | --- |
| W-G1 | GC | ReplayContext milestone 2 ownership items (EFB/XFB + texture-cache resources, event suppression, frame counter), each a brief with the desktop determinism gate | brief-sized each | `docs/todo.md:2670-2673,2701-2704` |
| W-G2 | GC | Pose interpolation on the `XFReplay::g_transform` seam | brief-sized | `docs/todo.md:2671-2673` |
| W-G3 | GC | HUD proof of replay arms via a screenshot-capable trial | brief-sized (S2b follow-up shape) | `docs/todo.md:2699-2700` |
| W-G4 | GC | Vulkan relink (fresh `core-vk-build` from current vendor tree + `-DHAS_VULKAN`) — only if a Vulkan production path is on the table | build brief | `docs/todo.md:2665-2669`; `docs/numbers-ledger.md:71` |
| W-G5 | GC | Onscreen host-replay display proof re-run (`sfstats.sh` + analyzer) once the host-replay route runs in the APK | device brief | `docs/todo.md:199-209` |
| W-G6 | GC | OD1 Odin readiness (named interface + what the device run must show) | unsized (brief queued after RC1) | `docs/todo.md:10`; `review-2026-09-19-progress.md:618` |
| W-G7 | GC | MF1 MetalFX spike s1, GameCube track | 6 h | `docs/todo.md:9` |
| W-G8 | GC | Replay re-scope + empty-queue GPU sync fix (~3.3 ms floor, 2.74 ms spin, fix named never scheduled) | unsized | `docs/todo.md:298-303` |
| W-G9 | GC | Interp alpha period reconcile (TicksPerSecond/59.94 vs /120) | XS | `docs/todo.md:329-332,405-407` |
| W-G10 | GC | 120 Hz verdict re-issue: interp-fx determinism re-proof + phone Combined re-run with blending on | unsized | `docs/todo.md:497-512` |
| W-G11 | GC | Longer Snow Jam movie for capped full-race numbers (current exhausts at HUD 3:33) | movie-record, unsized | `docs/todo.md:2740-2741` |
| W-G12 | GC | Route F backlog residue: D6 gate read records F dead on this SoC (render 95% of 8.33 ms before update); open sub-items (fast-FP phone measurement, fewer chassis round-trips, 1× BC pack, VI-paced true-120 arch question) | varies / unsized | `docs/todo.md:2783-2796` (gate read), `docs/todo.md:852-872` (backlog) |
| W-G13 | GC | Display production wiring (CreateAndroidPlatform branch, headless=false, vsync/pacing policy, input glue, shader cache, packaging) | XS–M per sub-item | `docs/todo.md:369-375` |
| W-G14 | GC | Harness measurement batch (trial-driver fast path, screenshot cadence out of trial windows, EFB re-A/B, memory fast paths, SyncGPU gating) | XS–S per sub-item | `docs/todo.md:264-328` |
| W-P1 | PS2 | R1 pc-tagged reference (bytesize, no lease) | ≤ 2 h | `docs/todo.md:9`; `review-2026-09-19-progress.md:612` |
| W-P2 | PS2 | T26 writer-watch boot (P-lane lease) | 4 h | `docs/todo.md:9`; `review-2026-09-19-progress.md:614` |
| W-P3 | PS2 | Item-3 trampoline fix (iff R1 shows faithful path) | one fix brief | `docs/todo.md:10`; `review-2026-09-19-progress.md:616` |
| W-P4 | PS2 | P1ae generic SIF peer (iff writer is SIF/RPC-delivered) | one fix brief | `docs/todo.md:10`; `review-2026-09-19-progress.md:614` |
| W-P5 | PS2 | E3 conditional (R1-state-dependency OR writer-watch-neither) | one brief | `docs/todo.md:10` |
| W-P6 | PS2 | G1 game captures (reference captures; gated on P-side rendering; G-lane resting) | unsized | `docs/todo.md:10,91-100` |
| W-P7 | PS2 | G2 loop brief (after G1) | unsized | `docs/todo.md:91-100` |
| W-P8 | PS2 | Kernel-truth sweeps batched post-first-frame | batched, unsized | `docs/todo.md:8` |
| W-P9 | PS2 | T25 NVM-verify + scripted path (bytesize reference enabler) | 6 h | `docs/todo.md:9` |
| W-P10 | PS2 | Mini day-one: GS GPU loop S1 start on synthetics | unsized | `review-2026-09-19-progress.md:262` |

## Source table: every GameCube number → file + line

Re-derivation commands are read-only greps unless noted; SV1–SV3 were
spot-verified this brief (see `local/research/RC1/REPORT.md`).

| Cell | Number | Source file + line/section | Re-derive |
| --- | --- | --- | --- |
| B1 | 0.665 / 0.866 ms med, 200/200 `done` | `local/research/S2/REPORT.md:27-28`; `docs/numbers-ledger.md:69` | SV1: `grep -n "0.665 ms" local/research/S2/REPORT.md` |
| B1 | 0.806 ms med third arm | `docs/numbers-ledger.md:71` | `grep -n "s2-egl-c" docs/numbers-ledger.md` |
| B1 | ≤ 6 ms gate | `docs/reserve/plan-120fps-2026-09-17.md:101` | `grep -n "6 ms" docs/reserve/plan-120fps-2026-09-17.md` |
| B2 | pair+render ≈ 12 ms at 1× (phone) | `docs/todo.md:873-875` | `grep -n "pair+render" docs/todo.md` |
| B2 | update 3.19 / render 7.93 ms med, p95 11.00, max 20.7 | `docs/numbers-ledger.md:66`; SSD `/Volumes/Extreme SSD/android-spike/D6/REPORT.md:197-198` | `grep -n "| update \|| render |" /Volumes/Extreme\ SSD/android-spike/D6/REPORT.md` |
| B2 | < 8.33 ms bar | `docs/todo.md:832-833` | `grep -n "8.33 ms sustained" docs/todo.md` |
| B3 | extras 8.638 / 11.858 ms wall med | `docs/research/120hz-output-resolution.md:44-47` | `grep -n "Extra wall median" docs/research/120hz-output-resolution.md` |
| B3 | Half/2× 102.94/112.67 per s; Half/1× 117.22 per s; Match/2× limited | `docs/todo.md:755-766` | `grep -n "112.67\|117.22\|Match/2" docs/todo.md` |
| B4 | 25 s warmed window rule | `docs/research/120hz-pacing-acceptance.md:16-22` | `grep -n "25 continuous" docs/research/120hz-pacing-acceptance.md` |
| B4 | longest warmed 15.88 s at 114.34/s; no sustained pass | `docs/todo.md:756-758`; `docs/research/120hz-pacing-acceptance.md:123-136` | `grep -n "15.88" docs/todo.md` |
| B5 | ≥117/s, med ≤8.6, p95 ≤10, p99 ≤17, speed ≥0.98 | `docs/research/120hz-pacing-acceptance.md:27-38` | SV3: `grep -n "At least 117" docs/research/120hz-pacing-acceptance.md` |
| B5 | 75–91 presents/s med 16.5 ms; uncapped med 8.5 ms | `docs/numbers-ledger.md:91` | `grep -n "presents/s" docs/numbers-ledger.md` |
| B5 | bursts fps peaked 102 | `docs/todo.md:889-893` | `grep -n "peaked 102" docs/todo.md` |
| B6 | Crow's opens 0.82–0.84× 51 s then 1.00× | `docs/numbers-ledger.md:58` | `grep -n "0.82" docs/numbers-ledger.md` |
| B6 | control re-run ~0.90× opening | `docs/numbers-ledger.md:70` | `grep -n "0.90" docs/numbers-ledger.md` |
| B6 | capped busy 0.58/0.27 ≈ 9.7/4.5 ms | `docs/numbers-ledger.md:62` | `grep -n "9.7 ms" docs/numbers-ledger.md` |
| B7 | det-none +7%; Null = base; 3.28 GHz floor | `docs/numbers-ledger.md:60-62` | `grep -n "det-none\|Null video" docs/numbers-ledger.md` |
| B8 | 104.7 °C clamp, zero throttle ticks | `docs/numbers-ledger.md:65` | `grep -n "throttle ticks" docs/numbers-ledger.md` |
| B8 | spin +10 °C null; phone samples serious | `docs/numbers-ledger.md:70`; `docs/todo.md:760-761` | `grep -n "spin only adds heat" docs/numbers-ledger.md` |
| C1 | residual 13418 B = 0.0234 of blend | `local/research/M15/REPORT.md:260-261` | SV2: `grep -n "13418" local/research/M15/REPORT.md` |
| C1 | static 95.67% exact; 87% residual at \|d\|=1 | `local/research/M15/REPORT.md:274-275`; `docs/numbers-ledger.md:220` | same SV2 grep |
| C1 | synth==blend | `local/research/M15/REPORT.md:343` | `grep -n "synth==blend" local/research/M15/REPORT.md` |
| C1 | 0 B explained, 102 far-tail bytes stand | `docs/numbers-ledger.md:97` | `grep -n "M16.M63 CLOSED" docs/numbers-ledger.md` |
| C1 | iPad 35/36 + 30/30; desktop 202/203 blended | `docs/todo.md:502-508` | `grep -n "blended 35/36\|202/203" docs/todo.md` |
| C2 | static-wall MAE < 0.02 | `docs/todo.md:693-695` | `grep -n "MAE moving" docs/todo.md` |
| C3 | HUD exact: 7.04%, alpha 0.727, within 2 levels | `docs/todo.md:699-703` | `grep -n "7.04%" docs/todo.md` |
| C4 | holes 77–81%; uncovered 0.44% / 1.2–2.4% | `docs/todo.md:693-698` | `grep -n "77-81%" docs/todo.md` |
| C4 | snow ≤0.05/≤0.08 clean, ≥0.17/≥0.38 corrupt, 0.12 | `docs/numbers-ledger.md:36` | `grep -n "Snow scorer" docs/numbers-ledger.md` |
| C4 | M5 counters: xfb 200/200, dframe +1 unresolved | `docs/numbers-ledger.md:83` | `grep -n "M5" docs/numbers-ledger.md` |
| C5 | window unchanged, rides on, zero GPU errors | `docs/numbers-ledger.md:57` | `grep -n "Host replay capacity, desktop" docs/numbers-ledger.md` |
| C5 | all updates `position_changed` | `docs/numbers-ledger.md:66`; SSD D6 `REPORT.md:63` | `grep -n "position_changed=1" /Volumes/Extreme\ SSD/android-spike/D6/REPORT.md` |

## Blank table: every PS2 BLANK → the receipt that fills it

No PS2 cell is filled by the NetherSX2 throughput gate
(`docs/numbers-ledger.md:68`): those are JIT-emulator numbers, not a
static-recomp first frame with a real GS census, so they do not meet
rec 10's comparison point. Each row names the future brief or report
row that fills it.

| Cell | What fills this BLANK | Which future brief / report row |
| --- | --- | --- |
| B1 | PS2Recomp per-frame cost on the Odin (or a PS2 replay-equivalent capacity number with the same ≤6 ms gate shape) | No queued brief; needs an OD1-shaped PS2 capacity brief after first frame |
| B2 | PS2Recomp update+render CPU per frame vs 8.33 ms | G-lane first game frames (`docs/todo.md:10`) + a PS2 D6-shaped probe brief |
| B3 | PS2 1×/2×-equivalent frame-time split | Same as B2, second config arm |
| B4 | A 25 continuous warmed seconds PS2 paced window | PS2 onscreen/paced brief after first frame (no queued brief) |
| B5 | PS2 present-timestamp series (rate + spacing + speed) | Same as B4, with SF timestats sampling |
| B6 | PS2Recomp capped-1.0 race pace, light + heavy anchors | G-lane first game frames + a PS2 M3b-shaped corpus brief |
| B7 | PS2Recomp determinism/config deltas | PS2 D1b-shaped matrix brief (no queued brief) |
| B8 | PS2Recomp thermal-window receipt | Same as B7, thermal columns |
| C1 | PS2 synth-vs-truth analog (interpolated vs true intermediate frame) | No queued brief; needs a PS2-side M15 analog |
| C2 | PS2 static-geometry warp MAE | Same as C1, static-geometry sub-table |
| C3 | PS2 HUD-layer isolation receipt | Same as C1, HUD sub-table |
| C4 | PS2 artifact bars + GS side-effect counters | G1 game captures (`docs/todo.md:91-100`) + `gscensus` on game streams (`docs/numbers-ledger.md:73`) |
| C5 | PS2 post-frame guest-state receipt | G-lane first game frames |

## Decision-point table: the comparison point

| Element | Content (mechanics, not outcome) |
| --- | --- |
| GC quote (rec 10) | "host replay shows an interpolated frame on the Odin" (`review-2026-09-19-progress.md:249-250`) |
| PS2 quote (rec 10) | "PS2 shows a first frame with a real GS census" (`review-2026-09-19-progress.md:250-251`) |
| Trigger | Both receipts exist: an interpolated frame presented on the Odin (GC side) and a first PS2Recomp frame with `gscensus` output on a game stream (PS2 side) |
| Inputs at the point | This doc with the PS2 column filled from the Blank-table receipts; no other inputs are named by rec 10 |
| Reader | Frontier-authored read at the fixed point (Part 4 dec 5, `review-2026-09-19-progress.md:620`); muse drafts tables only |
| Output | The route decision — explicitly deferred, not in this doc (`review-2026-09-19-progress.md:264`: "Not yet; write criteria now") |
| Non-trigger | Either receipt missing → no comparison; the PS2 column stays BLANK (this doc's current state) |
