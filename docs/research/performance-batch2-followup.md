# Fast-FP batch follow-up — September 14, 2026

Fast-FP remains a candidate. The installed phone build is `53e2e1e4` with
`fast_fp=true`; installation succeeded September 13 at 23:38. Its signed app
and receipts are preserved under
`local/research/perf-batch2/phone-pair/fastfp/`. No new phone performance result
has yet been established by this follow-up.

## Existing evidence, rechecked

`tools/native_determinism_check.py compare ... --strict` now checks trace
integrity and provenance in addition to overlapping values. Duplicate dispatch
counts are rejected instead of silently overwriting rows. The strict mode
requires a contiguous sampled prefix from dispatch zero, identical movie
hashes captured at run time, matching runner/world/configuration, explicit
single-core mode, a successful exit without a fault, a loaded module with
positive native execution counts, and no fallback JIT runs. Invalid accesses,
GPU command errors, unknown instructions and failed chunk checks must also be
zero. Only the randomized Analytics ID
is excluded when comparing configurations, and only after the retained file's
hash is verified against its run receipt.

Rechecking `det-play-base-2` against `det-play-fast-2` gives:

| Measurement | Result |
| --- | --- |
| Compared control-register rows | 1,022, all identical |
| Dispatch interval | 0–1,070,596,096 |
| Trace coverage | 100% of baseline; 99.32% of candidate |
| Runner/world/configuration and reported native execution/fault checks | Pass |
| Historical movie identity | Unverified: old runs did not capture its hash |
| Strict control-flow gate | **Inconclusive / fails strict acceptance** |
| Observed rider-state sequence | 83 entries / 82 changes, identical |
| Exact gameplay-state equivalence | **Not verified** |

Artifact: `local/research/perf-batch2/phone-pair/control-flow-audit.json`.
The old recording's movie hash is calculated from its retained file for
descriptive comparison only. It cannot prove which bytes the historical runs
consumed and does not satisfy strict acceptance. Newer record/play summaries
save the hash and execution outcome at completion.

The dispatch rows contain PC, LR, CTR, CR and timebase every 1,048,576
dispatches. Matching these values does not establish equality of floating-point
registers, positions, velocities, trick state or guest memory. The separate
`rider.jsonl` observations sample changed MemoryWatcher fields on host time,
approximately ten times per second, and do not contain a guest frame or update
identifier. Matching state-transition sequences is useful smoke evidence, but
there is no justified exact position alignment. Do not expand fast-FP semantics
on the strength of this check alone.

## Bounded phone comparison

Use unchanged `gc-gari-027`, dual-core, Half output, 2× detail, no smoothing,
and no dispatch sampling. Preserve the memory-card directory and resume files
before testing. Automated launches bypass the saved checkpoint and use the
same main-menu-anchored sequence; they do not make the dual-core ride
deterministic.

The prepared 166-second sequence is
`local/research/perf-batch2/phone-pair/sequence.json`, copied from the existing
main-menu riding smoke sequence. Compare builds from the same source snapshot
with only the fast-FP compile option changed. Keep the signed candidate archive
available for restoration. No course provisioning is needed.

For each run, retain launch metadata, metrics, runtime log and exact build
receipt. Confirm actual row settings, nominal/fair thermal state, workload and
rider motion before comparing callback cost. `tools/mobile_frame_cost.py` now
supports `--ordinary-only --max-thermal 0 --internal-scale 2 --output-scale 0.5`
and reports excluded rows and observed configurations. Missing requested
metadata is excluded. Audio counter deltas count only adjacent selected rows
with increasing timestamps no more than two seconds apart; excluded intervals
and counter resets are omitted. Its timing percentiles are medians of per-interval
statistics, not pooled callback percentiles. Launch settings alone are not
enough because users can change settings during a session.

Assess update/render callback CPU, speed/headroom, slow rows, thermal state,
draw calls and vertex workload together. If routes or thermal conditions
differ materially, label the comparison inconclusive rather than attributing
the difference to fast-FP. End after the bounded pair; sustained thermal
acceptance remains deferred.

## Result: the bounded phone pair is inconclusive (September 14)

Both arms ran on September 14 at Half output, 2x internal detail, dual-core,
no smoothing and no dispatch sampling, over the prepared 166-second sequence.
Both completed cleanly: 186.4 s and 186.6 s active, `error=false`, zero
fallback JIT runs, no audio interruption, thermal nominal throughout, and 87
riding rows each after the ordinary-only/thermal-zero/configuration filters,
with zero excluded riding rows.

| Riding rows only | Fast-FP `53e2e1e4` | Baseline `94f5096e` |
| --- | ---: | ---: |
| Render callback CPU median / p95 | 7.630 / 8.415 ms | 8.756 / 9.772 ms |
| Update callback CPU median / p95 | 3.290 / 3.682 ms | 3.104 / 3.597 ms |
| Draw calls per frame, median | 591.1 | 660.4 |
| Speed median / minimum | 1.000 / 0.792 | 1.000 / 0.802 |
| Slow rows | 12 | 13 |
| Guest headroom median | 1.270 | 1.198 |
| Audio empty dequeues | 30 | 16 |

**These numbers do not measure fast-FP.** The two runs rode different lines.
The automated sequence is input-identical, but the dual-core runtime is not
deterministic, and the rider positions separate within about three seconds of
the race starting: of the 86 riding seconds present in both runs, only four
(77-80, the gate and first moments) are within 100 world units of each other,
and the median separation across the rest is 13,614 units with a maximum of
27,146. Per-second draw calls diverge with them, 34,521/s against 40,109/s.

The apparent 12.9% render-callback advantage therefore tracks a 10.5% lighter
rendering workload in the same direction, which is what the follow-up's own
guard says to treat as inconclusive rather than attribute to the compile
option. The update callback moves the other way, fast-FP 6.0% slower, which no
general floating-point speedup explains either. Artifacts:
`local/research/perf-batch2/phone-pair/pair-cost.json` and `pair-run.log`.

What this does establish is that the automated sequence cannot produce a
matched route on a dual-core phone at all, so no number of repeats of this
design will settle fast-FP. A conclusive pair needs route control that this
harness does not yet have: a deterministic single-core arm, which isolates the
compile option but is not the shipping configuration, or movie-driven input on
the device the way the desktop reprojection captures are paired. Fast-FP
remains unmeasured on the phone, and the September 14 strict-provenance gap in
the historical desktop comparison is unchanged.

## Current execution status

The device connection initially timed out, then recovered. At 00:04 and 00:11
on September 14, CoreDevice reported `passcodeRequired=true`: the phone must be
unlocked before a test launch. No new app was installed or launched.

Preparation is complete:

- Baseline `94f5096e`, fast-FP off, built and signed successfully; archived app
  and receipts: `local/research/perf-batch2/phone-pair/baseline/`.
- Candidate `53e2e1e4`, fast-FP on, remains installed; verified signed archive
  and receipts: `local/research/perf-batch2/phone-pair/fastfp/`.
- Copied installed course receipt confirms `gc-gari-027` and archive SHA
  `a67ec9e518a46fb07c1ed433ecc8c4300dd734e42347b4290e8befcfb3318e7f`.
- App-only GC/SRAM and resume checkpoint backups, with hashes, are in the
  same `phone-pair/` folder. Game assets and on-device state were not changed.
- Twenty targeted evidence-tool tests pass, including review regressions for
  non-native/failed runs, missing historical movie hashes and audio attribution
  across excluded intervals.

The shared `local/native/ios-device` build tree now contains the prepared
baseline with matching baseline build/signing receipts. Use the archived app
paths explicitly when installing either arm of the comparison; rebuilding a
candidate still requires `--fast-fp`. The installed phone remains on fast-FP.
