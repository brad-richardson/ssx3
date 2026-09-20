# RC1 report: sourcing + gaps

Brief: `local/muse/prompts/RC1.md` (docs brief, 4 h box). Method:
read-only — no lease, no boots, no builds, no harness runs, no fork
changes, no adb. Deliverables: `docs/route-criteria.md` (this
commit) + this file. Tables, no verdicts; the route decision is
explicitly deferred to the comparison point.

## Sourcing: how each number was sourced

Every GameCube cell in `docs/route-criteria.md` carries a file+line
pointer in its Source table. Source inventory read for this brief:

| Source | What it supplied | Lines/sections used |
| --- | --- | --- |
| `docs/research/review-2026-09-19-progress.md` | rec 10 mandate + comparison-point quotes; §8 deferral row; Part 4 dec 4 (no-first-frame timing), dec 1–3 (R1/T26/trampoline), dec 5 (frontier-authored reads) | :247-251, :264, :612-620 |
| `docs/plan-120fps-2026-09-17.md` | S2 ≤6 ms gate; wave/gate structure | :90-102 |
| `docs/research/120hz-pacing-acceptance.md` | 25 s window rule; ≥117/s + spacing + speed bars; phone evidence (no sustained pass) | :16-22, :27-38, :123-136 |
| `docs/research/120hz-output-resolution.md` | Full/Half/Match dims; extra-draw wall/CPU medians | :10-17, :44-47 |
| `docs/research/120hz-cpu-overhead-spikes.md` | Extra-callback CPU-busy finding (6.8–9.7 ms range) | :1-17 |
| `docs/research/120hz-reprojection.md` | Presenting-command-buffer medians; block-matcher failure; MetalFX never built | :17-22, :36-41 |
| `docs/research/120hz-host-replay.md` | Capture/audit evidence (frame 6868 / present 13737); side-effect inventory | :53-88, :109-120 |
| `docs/research/120hz-f-spike.md` | Phase-1 desktop 0.9726 guest/host (context for B2 bar) | :68-81 |
| `docs/research/120hz-native-interpolation.md` | Extra-draw throughput variants (context) | :69-74 |
| `docs/research/120hz-analysis.md` | Color-only prototype rejection numbers (context) | :44-63 |
| `docs/numbers-ledger.md` | All quoted Odin/M5/D4/M3b/D6/S2/S3/D5/M15/snow rows | :36, :50-51, :57-66, :68-71, :73, :83, :91, :97, :220 |
| `docs/todo.md` | Open 120 Hz backlog (W-G rows); live queue (W-P rows); gate reads; phone burst numbers | :8-10, :199-209, :264-332, :369-375, :405-407, :497-512, :691-707, :753-782, :815-880, :928-948, :2661-2705, :2729-2796, :2980-2985 |
| `docs/odin-testing.md` | Read; Garibaldi handheld-test doc, no criteria numbers used | — |
| `local/research/S2/REPORT.md` | 0.665/0.866 ms medians, 200/200 `done` | :27-28 |
| `local/research/M15/REPORT.md` | 13418 B / 0.0234 residual, 95.67% static, synth==blend | :260-261, :274-275, :343 |
| SSD `/Volumes/Extreme SSD/android-spike/D6/REPORT.md` | D6 probe medians update 3.1880 / render 7.9338 | :63, :197-198 |

## Spot verification (3 re-derivable numbers, read-only grep, <5 min)

SV1 — S2 replay medians:

```text
27:   `s2-egl-a` 200/200 with `done`, **0.665 ms** median per replay (p95 0.729);
28:   `s2-egl-b` 200/200 with `done`, **0.866 ms** median (p95 0.963); no
```

Note: `S2/REPORT.md:543` cites arm 2 as 0.881 ms in a frame-size
discussion; the doc quotes the summary value 0.866 ms (`:27-28`,
matching `docs/numbers-ledger.md:69`).

SV2 — M15 residual + static share:

```text
260:| synth-vs-truth | 13418 | 102 | 1.712 | 0.0234 |
261:| blend-vs-truth | 13418 | 102 | 1.712 | 0.0234 |
274:| static (v0==mid==full) | 548582 (95.67%) | synth byte-exact (no motion to interpolate) |
275:| moved (v0≠full) | 24858 (4.33%) | blend-synth leaves 13418 B residual vs truth (xdmean 1.7; 87% of residual Y px at |d|=1) |
```

SV3 — pacing acceptance bars:

```text
29:| Actual presentations | At least 117 per second |
30:| Median spacing | At most 8.6 ms |
31:| p95 spacing | At most 10 ms |
32:| p99 spacing | At most 17 ms |
```

## Gaps: what OD1 must supply (GC side)

| Gap | Fills | Form |
| --- | --- | --- |
| Named synth-path Odin interface | W-G6 | Interface doc + device-run checklist |
| Interpolated frame presented on the Odin | Comparison-point GC quote; C1 on-device | On-device receipt (HUD-verified, SF timestats) |
| Screenshot-capable replay trial | W-G3 | Trial binary + HUD-anchored arms |
| Host-replay onscreen display proof | W-G5, B5 on-device | `sfstats.sh` series on the replay build |

## Gaps: what PS2-first-frame must supply (PS2 side)

| Gap | Fills | Form |
| --- | --- | --- |
| First PS2Recomp frame on a game stream | Comparison-point PS2 quote (frame half) | Game-frame receipt from the P lane |
| Real GS census on that stream | Comparison-point PS2 quote (census half); C4 | `gscensus` output via G1 captures |
| Per-thread EE/GS/VU frame times | B1–B3, B6–B8 PS2 cells | PS2 D6/M3b/D1b-shaped probe briefs (none queued) |
| Present-timestamp series | B4–B5 PS2 cells | PS2 paced brief with SF timestats (none queued) |
| PS2 synth-vs-truth analog | C1–C3 PS2 cells | PS2-side M15 analog (none queued) |

## Could not do

- D6 evidence lives on the SSD (`/Volumes/Extreme SSD/android-spike/`),
  not in the repo: the committed pointer for D6 numbers is
  `docs/numbers-ledger.md:66`, with SSD report lines as secondary.
- No PS2-side M15/D6/M3b/D1b-shaped briefs exist to cite; the Blank
  table names the receipt shape instead of a brief id where none is
  queued.
- `docs/odin-testing.md` (Garibaldi handheld test) contributed no
  criteria numbers; listed for completeness.
