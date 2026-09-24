# N8D7M12 Part 6M6R orchestrator gate P2 — external-wrapper package A (2026-09-24)

Orchestrator: Claude Opus (pane `w2:p77`, took over from Codex `w2:p26`). Brad
independently read the REPORT, reran `check.py` (20/20 A) and `git show --check`
(clean) before handoff.

Read the full REPORT and receipts (`build2.txt`, `wrapper-pins.txt`,
`source-verify-{pre,post}.json`, `compiled-inputs.txt`, `apk-facts.json`,
`apk-gate.err`) for worker commit `f16a14c2`. Independent checks on the mini:

| Check | Result |
| --- | --- |
| Private Mac APK `~/dev/ssx3-work/N8D7M12P6M6/app-release.apk`, two `shasum -a 256` reads | `da9a41a8e808fe31d509489c60b3927587c367866c6c2c6582009c35de6ef262` ×2, 153,753,116 B (equals worker WSL/Mac reads) |
| ZIP native members (`unzip -l`) | exactly 3, all `lib/arm64-v8a/`, stored: `libhardware.so` 7,112 B, `libps2EntryRunner.so` 139,515,320 B, `libvulkan_freedreno.so` 14,188,488 B |
| Extracted member SHAs, two reads each | runner `e5a3302c…c11af1`, Turnip `717812c3…c1ac29d` (pin), HAL `1b49d27c…4cdfc387` (pin) |
| Runner Build ID (`file`, `llvm-readelf -n`) | `4c9c9d149900cdc3494201c38124d11bfb616fa3` |
| Replay/fingerprint markers in runner (`grep -F -a`) | `PS2X_GS_REPLAY_PKTSEQ` 1, `GB4_PKTSEQ tick=%llu seq=%016llx commands=%llu` 1, `GB4_REPLAY tick=` 1, `GB4_REPLAY_SUMMARY` 1, `GB4_FRAME` 1, `GB4_PARALLEL_STATS` 1, `PS2X_GS_REPLAY_ONDEVICE` 1, `PS2X_GS_REPLAY_CAPTURE` 2, `PS2X_GS_REPLAY_BACKEND` 2; `PNG write failed path=` 0 |
| Staged fork vs private commit | `git archive 4fa0df1` vs `local/research/N8D7M12P6M5/stage/PS2Recomp`: 323/323 files, `diff -rq` empty |
| PKTSEQ source (`git diff a608ed1 4fa0df1`) | gs_frontend digest/count + atomic default-off fast check before mutex; replay core reads `PS2X_GS_REPLAY_PKTSEQ`, emits `GB4_PKTSEQ`; as gated in P5F4P2/P3 |
| Private CMakeCache `fa75edad…32994` | arm64-v8a, RelWithDebInfo; DIAG_TAPS / RUNTIME_LOGS / AGRESSIVE_LOGS / IOP_RPC_TRACE / DEBUG_UI / BUILD_TEST OFF; `PS2X_GS_SHADOW_PARALLEL=ON`; parallel-gs and codegen dirs are the new WSL root |
| Source aggregate pre/post build | `6877de87…80316a` both, no add/missing/change |
| Compiled inputs | 449 compile commands; fork frontend/worker/backend, `gs_interface.cpp`, `page_tracker.cpp`, Granite allocator named; 296 codegen unity batches, 9,455 codegen `.cpp` |
| Commit contents | 22 text files, no binary numstat rows; no APK/game bytes in git |
| Disk | 157.7/200 GB |

**Verdict: A for the package.** One pinned-wrapper `assembleRelease` built the
staged, manifest-pinned inputs unchanged; the APK, its three native members and
the Build ID are pinned, and the runner carries the worker-consumption
fingerprint (`PS2X_GS_REPLAY_PKTSEQ` → `GB4_PKTSEQ`) that this package exists
for. The worker's strict string gate checked only the old P3 set and omitted the
PKTSEQ markers; this gate closes that gap. The 22/23 P3 miss
(`PNG write failed path=`) is accepted as explained: the string is absent from
the staged `4fa0df1` source, which matches `git archive` byte for byte.

Known scope limits, not blockers:
- Runtime is private `4fa0df1` (E54F2 lineage + N8D7 diagnostics), not shipped
  `04f3ace`. It lacks `779e804` E55B2 / `ddaee78` E55C2 (default-off
  deterministic mode and hash tap) and `4ebb2ac`/`04f3ace` I27 (iOS). None act
  in a GS replay.
- The HAL member's historical source transform is still unknown (pinned member
  passthrough only).
- Default-off behavior is proved statically and on the Mac host (P5F4P3), not
  yet on the Odin.

No install or launch happened. No GPU cause, image or speed claim.

Next: one same-settings Odin replay pair with `PS2X_GS_REPLAY_PKTSEQ=1`, same
APK `da9a41a8…`, stream `f6a78f71…a593` and env, comparing 41 ordered
`GB4_PKTSEQ` digest/count rows (run vs run and vs the Mac ON control in
`local/research/N8D7M12P5F4P2/`) plus the existing 41 replay rows and PPMs. Equal
digests with differing frames end input-hash expansion (next: downstream
renderer state/readback); a differing digest means a delivery investigation.
