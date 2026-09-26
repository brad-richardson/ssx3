# PT1 — one-command Odin profiler

Worker: Muse Code. Brief: `local/muse/prompts/PT1.md`. Date: 2026-09-26.
Method: promoted CP1's `classify.py` + launch/sampler path and N12's
`buckets.py` into `local/tooling/odin_profile.py`; symbolization on the
mini with the NDK host simpleperf; validated offline against CP1's R2b
capture (no device run — the Odin lease was held by FS2, which has
priority; the live path is code-complete but unexercised).

## Status

**Done, offline-validated.** `odin_profile.py --from-perf` reproduces
CP1's Table 2 and Table 3 within ~5% (most rows ≤1.5%; the GsWorker
blocked split differs 5–6% from CP1's point estimate, inside CP1's own
stated ±20% — see §Gaps for the normalization note), GPU Table 4
exactly, byte-identical across repeat runs (19 s each on the mini).

## Deliverable

`local/tooling/odin_profile.py` (executable; README in the module
docstring):

- Live: `--apk --apk-sha --label [--env …] [--window 1900,2500]
  [--profile-secs 20] [--offcpu] [--symso <so|bytesize:/path>]`
  → `odin_cooldown.py` (`--cooldown-mode screen|final`, default screen
  per the 09-26 run-modes rule; `--stop-tick` auto: screen 3000, final
  4500; the mode is recorded in `meta.json`/`meta.txt` so every number
  is labeled) → F7/CP1 launch path (lease, keyguard/battery/mc0-test
  checks, install + SHAs, I26-FAST unpaced env) → simpleperf + concurrent
  schedstat/cpufreq/gpubusy sampler → force-stop → pull (perf.data stays
  in `~/dev/ssx3-work/odinprof/<L>/`) → `odin_restore_play.sh` → host
  analysis (Build ID checked against the APK; refuses on mismatch).
- Offline: `--from-perf <perf.data> --symso <so>` (+ `--samples`,
  `--logcat`, `--meta`, `--apk`, `--libc`) re-analyses a capture.
- Reports in `local/research/<L>/profile/`: `per-thread.txt` (CP1 Table 2
  format), `topsym.txt` (top-25 self per thread), `buckets.txt` +
  `buckets-appendix.txt` (N12 stages + VU1 `B*` blocks, SIMD FMAC, MTVU,
  GS frontend, paraLLEl submit, allocator split; execUpper/execLower
  count as VU0 on the GameThread only), `gpu.txt`, `counters.txt`
  (`[mtvu]`/`[gs:parallel] sync`/`[present-vk]`), `classes.txt`,
  `meta.txt`.

## Validation (offline, CP1 R2b capture)

Inputs: `~/dev/ssx3-work/CP1/odin/R2b/perf-R2b.data` (106,789,790 B,
`1f835a3a…`), `local/research/CP1/logs/R2b/{profile-samples,logcat}.txt`
+ `meta.json`, VR3 unstripped `.so` pulled from bytesize over plain
`ssh cat` (1,327,528,856 B, `01fceae5…2273ea`, Build ID
`837d7dbb…14fa` **= APK's**), `~/dev/ssx3-work/CP1/libc-device.so`.
Window: ticks 1983→2403, 420 frames, 50.00 ms/frame — exact match.
Unresolved rows in our `.so`: 0. Host simpleperf:
`/opt/homebrew/share/android-ndk/simpleperf/bin/darwin/x86_64/simpleperf`
(universal binary, runs native on the mini).

Table 2 vs CP1 (ms/frame; tool | CP1):

| Thread | running | runnable | blocked = split |
| --- | --- | --- | --- |
| MTVU | 30.1 \| 30.1 | 0.9 \| 0.9 | 19.0 \| 19.0 = 12.1/6.6/0.3 \| 12.2/6.7/0.3 |
| GameThread | 13.1 \| 13.1 | 0.2 \| 0.2 | 36.7 \| 36.7 = 36.6 vblank \| 36.2 vblank |
| GsWorker-30557 | 9.7 \| 9.7 | 3.7 \| 3.7 | 36.6 \| 36.6 = 18.4/18.0 \| ~19.5/~19.1 (±20%) |

Table 3 vs CP1 (MTVU self, ms/frame; tool ÷400 record frames, CP1 ÷405):

| Symbol | tool | CP1 | Δ |
| --- | ---: | ---: | ---: |
| kernel `…a8e810` | 2.32 | 2.29 | +1.3% |
| `B2a10` | 2.22 | 2.20 | +0.9% |
| `B0628` | 1.50 | 1.48 | +1.4% |
| `commitReadyPipelines` | 1.31 | 1.30 | +0.8% |
| `processVIF1DataImpl` | 0.87 | 0.86 | +1.2% |
| `B0a58` | 0.86 | 0.85 | +1.2% |

GPU: 47.1 47.0 49.1 47.9 48.2 46.9 48.0 56.4 56.1 (mean 49.6),
660 MHz, 24.8 ms/frame — exact. Cross-checks: MTVU run 30.1 vs 30.3,
blocked 19.0 vs 19.4; GT 13.1 vs 12.9, 36.7 vs 36.6; GsW 9.7 vs 10.1,
36.6 vs 39.2 (same shape as CP1's 1–6%). Determinism: two runs →
all 8 reports byte-identical. Fixed during validation: `other:` sleep
labels were nondeterministic (set iteration) — classifier now walks the
ordered callchain (innermost userspace frame first).

## Exact commands

```sh
python3 local/tooling/odin_profile.py --from-perf \
  ~/dev/ssx3-work/CP1/odin/R2b/perf-R2b.data \
  --symso ~/dev/ssx3-work/odinprof/PT1/sym/libps2EntryRunner.so \
  --libc ~/dev/ssx3-work/CP1/libc-device.so --label PT1 \
  --samples local/research/CP1/logs/R2b/profile-samples.txt \
  --logcat local/research/CP1/logs/R2b/logcat.txt \
  --meta local/research/CP1/logs/R2b/meta.json \
  --apk ~/dev/ssx3-work/odin-play/app-release.apk
# live (NOT run — lease held by FS2):
python3 local/tooling/odin_profile.py --apk <path> --apk-sha <sha> \
  --label L --env PS2X_MTVU=1 --offcpu --symso bytesize:/home/brad/vr3/…/libps2EntryRunner.so
```

## Gaps

| Gap | Reason |
| --- | --- |
| Live device path untested | lease held by FS2 at validation time (priority per brief); first live user should watch one run |
| GsWorker split −5–6% vs CP1's point estimate | tool pro-rates class fractions to the schedstat blocked headline (parts sum to 36.6); CP1 scaled to switch-pair blocked (parts sum to ~38.7). Inside CP1's stated ±20%; method documented in the report header |
| SIMD FMAC stage empty in R2b | no FMAC/NEON self symbols in this capture; stage regex present for future captures |
| Plain `-g` (no `--offcpu`) degradation untested | blocked splits print "no switch records"; no R2-style fallback capture was re-analysed |
| Transient Turnip GsWorkers absent from per-thread table | they exit mid-window, so no schedstat edge delta; their on-cpu still appears in topsym/buckets/classes |

Budgets: 0/0 builds, 0 device runs (optional smoke skipped: FS2 held
the lease), ~2 h of 3 h. Scratch `~/dev/ssx3-work/odinprof/PT1/` 1.3 GB
(the symdir hardlinks the pulled `.so`). Text in git (tool + REPORT);
`local/research/PT1/profile/` left on disk, uncommitted (regenerates in
19 s). No lease held at close; play state untouched (no device run).

## Orchestrator gate (2026-09-26) — adopted, lane closed

**Pass.** Offline reproduction of CP1's Tables 2–4 within ~5 % (GPU exact), deterministic, 19 s per analysis; the
live path follows the run-modes rule and labels its mode. The live path gets exercised by CP2 (its first user).
