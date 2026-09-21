# T41 report — sub-second `sleep 0.5` blind cadence around the 1 s hold: does SCPS40 resolve the hold hop? (bytesize, no lease)

Brief: T41 (T40's G1, first arm only: sub-second `sleep 0.5` blind
cadence, NOT the ROI retune). Tables, no verdicts. One boot ran on
bytesize (RESULT PENDING — section T41-3 filled after the run);
laptop-side work was ssh/scp + local reads/analysis only. Time box 4 h.

Stale-reading guard: `local/research/T40/REPORT.md` (all of it: R1
DISCARDED (C:-full guest wedge at T+185 — environment failure, full
forensics + C: fix: cleared 20 stale emulog transfer copies ~30 GB, C:
116 KB → 29.1 GB; C: headroom ~5 GB+ is now a pre-run gate); R2 reproduced
the chain to LIVE gameplay, ONE 1038.0 ms D-pad Left hold @T+503.09 on a
live race (pre-pair 00:01:28 6TH/6 36% / 00:01:29 6TH/6 36%), blind
back-to-back 10-snap series at ≈1.07 s exposures scored post-hoc to
00:01:46 6TH/6 41%: SCPS120 railing drops 7/11 → 3/11 with the hold hop
RESOLVED (+49 @ 0.79 — first resolved input hop in T36–T40), SCPS40 rails
4/11 INCLUDING the hold hop (+40 @ 0.74), RDC gated out 10/12 with no gated
pair straddling the hold; G1 proposes ONE variant — this brief takes the
`sleep 0.5` arm, NOT the ROI retune). This brief executes T40's G1 (first
arm only). T40's scripts reused (copied, not modified).

Experiment contract (up front): hypothesis — T40's ≈1.07 s blind exposures
resolved the hold hop at SCPS120 (+49 @ 0.79) but SCPS40 still railed it
(+40 @ 0.74), so halving the dense-phase cadence (`sleep 1` → `sleep 0.5`,
still blind, capture-bound at ~70 ms + scheduler) yields ≈0.6 s exposures
where SCPS40 resolves the hold hop too and a gated RDC pair can straddle
it; observable — pre-hold pair = live race (race clock + position/progress
HUD read off the viewed snaps), the hold row (proven 1 s keydown→keyup +
phase match vs T40's hold), dense 10-snap series + per-snap HUD + tracking
metrics + per-hop whole diffs, all scored post-hoc from fetched snaps;
screen content read off viewed snaps; alternatives — SCPS40 still rails
the hold hop / RDC still floods at ≈0.6 s exposures (→ table the exact
observed rates + noise floors and STOP with a recipe), run provably never
reached live gameplay at a matched phase (→ ONE bounded re-attempt
allowed); stop — table the rail-rate comparison vs T40 + gated-pair
verdict + recipe, one input variant per attempt, never blind multi-presses.

## T41-0. Rule record

| Item | Value |
|---|---|
| Lease | None of any kind (no lease exists for T41; bytesize needs none) |
| Boots on laptop | 0 (all boots on bytesize) |
| Laptop-side work | ssh/scp + local reads/analysis only |
| Build | REUSED, no rebuild (sha/size/rev all reproduce T4, see below) |
| Fork changes | 0 (no ssx3 source touched; evidence + scripts only) |
| `adb` | Not used |
| `git push` in ssx3 | Never run |
| Copyrighted downloads | None (inputs already staged; no installs this session) |
| ssx3 HEAD at commit | Below (`[T41]`, trailer `Orchestrated-By: Muse Code`, no push) |

Build-reuse verification (all reproduce T4 §T4-1 row 8 exactly; verified
on VM-H32 before R1):

| Item | T4 value | T41 observed | Match |
|---|---|---|---|
| Binary sha256 | `6719f5d6…ee327` | `6719f5d6ba5ac6c2c26a5954b12b837d0ff8d8e95ee6a83ed6b7b542cedee327` | yes |
| Binary size | 130929856 B | 130929856 B | yes |
| Tree rev | `9056c08349…95af` | `9056c08349cc29ad02a6d1a3a4133259019195af` | yes |
| Tree status | clean | clean (empty `status --short`) | yes |
| Inputs | ISO 3005415424 B + BIOS trio | same paths, same sizes (ISO 3005415424, .bin 4194304, .mec 4, .nvm 1024) | yes |
| NVM pre-run | `da021d2a…` mtime Sep 20 15:20 | `da021d2a3d4b4e43182c240cb368986ae6b4cdf5f034e2e9afea0cb2d865a961`, mtime Sep 20 15:20 | yes |
| Pad binding (Cross) | `Cross = Keyboard/K` | `PCSX2.ini:579` unchanged | yes |
| Pad binding (Left) | — | `Left = Keyboard/Left`, `PCSX2.ini:576` (the hold key; T38's binding re-verified) | yes |
| Title ref present | — | `t27-ref-title.ppm` sha `b964856a…e94f59a` reproduces T27 | yes |
| Menu ref present | — | `t28-ref-menu.ppm` sha `8f34385f…ae76` reproduces T28 | yes |
| SC ref present | — | `t29-ref-sc.ppm` sha `dd7e4716…2c06e55` reproduces T29 | yes |
| ZC ref present | — | `t30-ref-zc.ppm` sha `212b0970…f79f722` reproduces T30 | yes |
| SP ref present | — | `t31-ref-sp.ppm` sha `1a8b1ed9…d22b40` reproduces T31 | yes |
| SM ref present | — | `t32-ref-sm.ppm` sha `e724021c…92845c2` reproduces T32 | yes |
| SE ref present | — | `t33-ref-se.ppm` sha `4baec4bc…bedd889d` reproduces T33 | yes |
| MR ref present | — | `t34-ref-mr.ppm` sha `069b1113…64d373` reproduces T34 | yes |
| Panel ref present | — | `t35-ref-panel.ppm` sha `192e0472…580eb6` reproduces T35 | yes |
| T40 reference snaps present | — | all 12 sizes reproduce T40 §chain (`npre1/2` 52069/50992, `d-post1..10` 48456/51050/57207/53965/56852/50871/54132/53532/59421/62473) | yes |
| Free space | — | WSL `/` 867 G pre; C: 27 G pre (GATE ~5 GB+ PASSES — no wedge risk); laptop `/` 11 Gi avail; SSD 237 Gi free | yes |
| Live trace pre-run | — | `emulog.txt` 2782052936 B sha `6fb03830…a367c` = T40 R2 (preserved at R1 boot) | yes |

Phase-match targets (tabled BEFORE the run — T40 R2's hold window, match
PHASE not seed; AI lineup/RNG differ run to run):

| Item | T40 hold-window value | T41 hold-window target |
|---|---|---|
| Hold slot | T+503.09 (keydown) | ≈T+502.5 (same script slot; ≈0.5 s earlier from shorter pre-pair gap) |
| Pre-pair race clocks | 00:01:28 / 00:01:29 | ≈00:01:2x–00:01:3x (mid-race, ≈±10 s) |
| Pre-pair positions | 6TH/6 / 6TH/6 | racing pack (1ST–6TH/6, AI lottery) |
| Pre-pair progress | 36% / 36% | ≈36–45% (±5 pp) |
| Series span | 10 snaps over +11.8 s wall / +17 s race | 10 snaps over ≈+7 s wall (shorter: `sleep 0.5` blind capture) |

Blind-capture cadence (tabled BEFORE the run — the deliberate change):

| Item | T40 (blind `sleep 1`) | T41 (blind `sleep 0.5`) |
|---|---|---|
| Dense-phase shape | `sleep 1` + capture only; ns wall stamps per snap; ZERO scoring calls | `sleep 0.5` + capture only; ns wall stamps per snap; ZERO scoring calls |
| Expected exposure gap | ~1–2 s (measured 10 × 1.071–1.074 s) | ~0.5–0.7 s (0.5 s sleep + ~70 ms snap overhead + scheduler; measured post-hoc from ns stamps) |
| Pre-pair gap | `sleep 1`, no scoring (measured 1.074 s) | `sleep 0.5`, no scoring (≈0.6 s expected) |
| Hold-hop span | hold 1.038 s + `sleep 1` + overhead (measured 2.111 s) | hold ≈1.04 s + `sleep 0.5` + overhead (≈1.6 s expected) |
| Dense span (npre1→d-post10) | 12.90 s wall | ≈7.9 s wall expected |
| Run length | T40 R2 524 s | shorter by ≈5.5 s (11 × 0.5 s saved); delta tabled |

Post-hoc scoring plan (tabled BEFORE the run — all from fetched snaps
with the committed tools):

| Step | Tool | Output |
|---|---|---|
| 1. Fetch 61 JPGs + poll log | scp via C: staging (T25 recipe) | `t41r1-*.jpg`, `t41r1-poll.log` |
| 2. Chain panel: every snap vs all 9 refs + title-band + SE-TAG | numpy batch port of `t41-cropdiff.py`, bit-exact validated 4/4 (T39/T40 protocol); committed tool reproduces any score | screen chain table + xrun frame identities vs T40 R2 |
| 3. All hops (chain + dense) whole-frame | same batch scorer | transition-hops table (dense hops have NO in-script remote counterpart — PIL only) |
| 4. Dense 12-snap tracking | committed `t41-track.py` (byte-identical to T40's = T38's frozen) | RDC cx/cy/npix + gate, SCPS40 + SCPS120 lags |
| 5. View all snaps | local reads | HUD per snap (clock/position/progress/speed/score) |
| 6. Rail-rate comparison | — | RDC gate-out / SCPS40 / SCPS120 rates vs T40 + gated-pair verdict |

Rail rates to beat (tabled BEFORE the run — T40 R2 hold dense phase,
12 snaps / 11 hops at ≈1.07 s):

| Metric | T40 (1038.0 ms hold, ≈1.07 s gaps) | T41 question |
|---|---|---|
| RDC gated out | 10/12 | does any gated pair now straddle the hold? |
| SCPS40 rails | 4/11 (INCL the hold hop +40 @ 0.74) | does the hold hop resolve at ≈0.6 s? |
| SCPS120 rails | 3/11 (hold hop RESOLVED +49 @ 0.79) | stays resolved? |
| Input-hop SCPS40 | +40 @ 0.74 RAIL | resolved or still railed? |
| Dense whole-hop range | 6.72–16.60 | motion-class floor at ≈0.6 s? |

## T41-9. Wrap note (machine restart — full report pending)

Machine restart forced a wrap with scoring complete but the full report
unwritten. Core facts (all evidence committed herein): R1/R2 = environment
failures (WSLg-audio-down cubeb modal occluded the title band both runs,
NO-PARK 3/3 attempts each, flap-clean); R3 = NO-SP-PARK (chain nominal to
SP, game-side SP→SM advance T+214–218 with zero input in-window; my one
parallel Start@T+155 landed inertly on ZC — ccpre/sp-post1 clean);
R4 (H36, T+520, exit 0, T41_DONE, zero in-window flaps/events) = FULL CHAIN
+ ONE 1038.4 ms Left hold @T+503.19 on a live 2ND/6 race (pre-pair
00:01:29 2ND/6 45% / 00:01:29 2ND/6 46%) + 10-snap blind series at 10 ×
≈0.57 s (hold hop 1.611 s) to 00:01:40 2ND/6 49% (d10 wall crash +
RECOVER). Tracking (frozen t41-track.py): RDC gated out 11/12 (only
d-post5 VALID — no gated pair anywhere); SCPS40 rails 4/11 with the hold
hop OFF-rail at +29 @ 0.02 (no match) vs T40's +40 @ 0.74 rail; SCPS120
rails 1/11 with the hold hop at +119 @ 0.37 (1 px off-rail, weak) vs
T40's +49 @ 0.79 clean resolve. Dense whole hops 6.36–17.47 (T40:
6.72–16.60). Census sets identical to T40 (EE 52, IOP 155). SSD stream
BLOCKED (Extreme SSD detached mid-session) — full R4 trace retained ONLY
as bytesize original `…/dat/PCSX2/logs/emulog.txt` 2745300674 B
`5b0a7349…53d3f` + committed head/tail slices. Full T41-1…T41-8 tables
follow after restart.
