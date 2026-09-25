# Where the time went, 09-22 → 09-24, and what would have helped

Orchestrator review, 2026-09-24 evening. Source: git log (734 commits since 09-22: 102 on
09-22, 226 on 09-23, 406 on 09-24; 420 `[orch]`, 314 lane).

## Time by area

| Area | Span | Commits (lane / orch) | Outcome |
| --- | --- | --- | --- |
| Odin black frame (N8A → N8D7M13 → N8X1) | 09-24 03:00–19:20, ~16 h | 88 / ~60 | Solved; cause found in the last 40 min |
| Save/load route (E55D, 15 parts) | 09-24 10:30–15:30, ~5 h | ~20 | Ended "no save available"; Brad knew it was on the Odin |
| GS glyph damage (GB5/GB7) | 09-24 00:30–13:30 | 17 | One texture word traced; still open |
| CPU semantics + determinism (E54/E55A–C) | 09-24 00:30–04:20 | ~15 | Four fixes + determinism mode shipped |
| GS queue/bridge (GB2–GB4) | 09-23 | 17 | 7 parts on racy live gates before replay gating |
| Audio (AU2–AU7) | 09-23 → 09-24 | ~12 | Stereo loss unseen ~22 h; fixed in one lane once measured |
| Orchestration | throughout | 420 of 734 | 236 gates, 76 briefs/queues |

N8 chain, approximately: Turnip loader 1.5 h (productive); image-stage and tile probes 5 h;
decoder/oracle 2 h; read-only designs 2.3 h (mostly verdict B/partial); replay harness 1.5 h;
hash designs + Mac control 2 h; one APK's provenance 2.5 h; PKTSEQ pair + first tick 35 min;
exploratory Opus session 40 min to the cause (wave128 hierarchical binning on Adreno).

Counts across all commit subjects since 09-22: 48 "design/read-only", 21 "stop", 21
"correction", 16 B/partial/OTHER/invalid, 8 permission/SSH denials, 3 void.

## Top bottlenecks

1. **Serial narrow briefs on an unknown-cause bug.** Every hypothesis paid brief → launch →
   gate → commit → push (20–40 min). The explorer ran ~40 device replays in 40 minutes by
   iterating freely (stream splitting, one-variable variants). The bounded loop is right for
   execution and provenance (N9, AU7), wrong for search.
2. **Wrong or incomplete observables.** The Mac "ground truth" never executed the failing path
   (`#ifdef __APPLE__` disables hierarchical binning); audio was measured in mono, hiding a
   stereo side-channel loss; 50-tick samples hid the tick-44 departure.
3. **Branch and provenance friction.** GPU code lived in dirty clones (P6 packaging ~2.5 h, N9
   Part 1); the sound code sat on a side branch, so audio was measured on code lacking the E54C
   fix; 8 permission stops, a missing Gradle wrapper, logcat drops.
4. (Smaller) Searching for what Brad knew: the save hunt.

## Remedies (adopted 09-24)

Process (in `docs/orchestration.md`):
- **Exploration mode:** after two inconclusive bounded parts on one symptom, switch to a
  time-boxed frontier session with the device and free rein plus a notebook; return to bounded
  briefs once a mechanism is named.
- **Reference equivalence:** before trusting a baseline, check that the reference takes the same
  code path (platform switches, feature fallbacks); log the path each device takes.
- **Full-signal measurement:** stereo mid/side, per-tick hashes when hunting a first divergence,
  frames viewed by the orchestrator.
- **Fold as you go:** product code lands on a fork branch in the lane that proves it; side
  branches fold the day they gate.
- **Ask Brad first** before searching for assets, hardware or preferences.

Tooling (in `docs/todo.md`, cross-lane): `odin-replay` CLI with stream surgery, a
reference-path logger, a `gate` helper, worker permission preflight, a nightly fork-tip build.
