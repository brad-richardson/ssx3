# N5 — Odin: current tree, dumps-off, speed through the race

- Date: 2026-09-23. Brief: `local/muse/prompts/N5.md`. Worker: Claude Code
  (Opus pane).
- **STATUS: STOPPED at Work step 1 (rebase). The permission layer denied the
  rebase; per `~/dev/AGENTS.md`, not retried another way.** No builds, no
  launches, no Odin lease taken, nothing changed on bytesize.
- Budget used: 0/3 builds, 0/5 launches, ~25 min.

## The denial (receipt)

One Bash call, piped to `ssh bytesize 'wsl -d Ubuntu -- bash -s'`, containing:

```
git branch -f n5-pre-rebase 65c95d9          # backup ref before the rebase
git fetch origin
git rebase --onto eac6cba e57b5f8 n2-android
```

(The same call also streamed `e45.patch` to `~/n5/` first.) Result, verbatim:

> Permission for this action was denied by the Claude Code auto mode
> classifier. Reason: [Git Destructive].

The whole call was refused, so nothing ran on bytesize: `n2-android` is still
`65c95d9`, no backup ref, no `~/n5/`, no fetch.

## What is ready (read-only facts gathered before the stop)

| Item | Finding | Source |
|---|---|---|
| bytesize `n2-android` | `65c95d9` = `e57b5f8` + 6 local commits (`8e7d5ac` H1, `322e55b` env shim, `3da81ad` arm64, `f9d78da` manifest/PNG, `ae210c9` union, `65c95d9` padlog); tree clean apart from untracked gradle wrapper | `git log` on bytesize |
| bytesize load | `pgrep -f pcsx2` = 0; WSL just started (uptime 0 min); 852 GB free | same session |
| E45 `310b30f` | **Not on any remote** (`git branch -r --contains` empty); only on the mini's local `e45-vu-double`. Exported as `format-patch` (sha256 `ae21c498…0de2`, scratch) to apply with `git am -3` | mini fork, read-only |
| Runtime/aggressive logs | `ps2xRuntime/CMakeLists.txt:15-16` default **OFF**; `android/app/build.gradle` doesn't set them → the default release build has logs compiled out | bytesize tree |
| Frame dumps | `dumpPresentationFrame` returns on its first line when `PS2X_FRAME_DUMP_DIR` is unset (cached `getenv`; no hash, no encode): the same APK is (a) without the env and (b) with it, so **one build covers both APKs** | `eac6cba:ps2xRuntime/src/lib/ps2_runtime.cpp:386-491` |
| Guest vsync counter with dumps off | none on `eac6cba` or `n2-android` (N4/PF1 read ticks from `[frame:dump]`). Plan was to port I25's env-gated `PS2X_VSYNC_RATE_LOG` hunk (`31d988d`, one `fprintf` per 5 s on the host loop) as an `[N5-local]` commit | `i25-ios` `31d988d` |
| Pad route | `local/research/I26/ROUTES.md` absent → E33 vsync-clock route (13 entries, `PS2X_PAD_SCRIPT_CLOCK=vsync`; I25 proved it reaches the race on `eac6cba`) | `E33/REPORT.md` §Vsync-clock script, `I25/REPORT.md` row 2 |

## Ways forward (orchestrator decides)

1. **Allow the rebase** (a Bash permission rule for git on bytesize, or
   approval for this brief), then re-run N5 from step 1 unchanged.
2. **No ref rewrite:** create a new local branch `n5-android` at `eac6cba`
   and cherry-pick the six N-local commits + E45 onto it, leaving
   `n2-android` at `65c95d9` untouched. Same build result; this needs your
   explicit OK because it reaches the brief's goal by a different route
   after a denial.
3. Either way, OK the `[N5-local]` vsync-rate commit (measurement line
   only, off unless `PS2X_VSYNC_RATE_LOG=1`); without it the dumps-off APK
   gives no guest vsync count except the 13 pad-script `press … now=…ms`
   lines.

## Gaps

- Rebase conflicts unknown (not attempted). `e57b5f8..eac6cba` (30
  commits, mini fork) adds 110 lines to `ps2_runtime.cpp` (where N4's
  `writePngBytes` lives) and doesn't touch `ps2_pad.cpp`,
  `ps2xRuntime/CMakeLists.txt` or `android/`. So `f9d78da` is the one
  likely conflict. E45 touches `ps2_vu1.h`/`ps2_vu1_core.cpp`, which the
  range also grows (+36/+899), so `git am -3` may need a hand merge.
