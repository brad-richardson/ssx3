# Orchestrating ssx3: runbook

For whoever orchestrates. Read at start, in order: `AGENTS.md` (rules), `docs/status.md`
(board), `docs/todo.md` (open work), `docs/numbers-ledger.md`, `local/AGENTS.local.md`
(hosts, worker recipes, quota). Git history is the record of everything done; don't write
history into these docs.

## 1. The loop

1. **Watch.** Run `WS=w2 MAX=1800 local/tooling/orch/watch.sh` in the background (as a tracked
   background task, never `&` inside a shell, or nothing wakes you). It exits on: a new non-`[orch]`
   commit; a `blocked` pane; **STOPPED** (a worker that was working went idle/done without a
   commit); **ERROR** (a pane shows a model/memory/rate-limit/API failure string); **STALL** (a
   working pane's output unchanged for `STALL` s, default 1200); or the heartbeat (lists pane
   states). Restart it after every exit, and never end a turn with panes working and no watcher.
   **Stall check on every exit, heartbeat included:** for each pane, compare its status with what
   it should be doing, read its last output, and act: nudge a stuck worker, re-send after a
   transient error, pause or close one that competes for a shared resource (e.g. two local Qwen
   workers hitting the oMLX memory guard), and tell Brad about anything he'd notice. Before any `[orch]` commit, scan `git log --oneline -8` for
   lane commits you haven't gated (one sat unread under two `[orch]` commits once).
2. **Gate** each lane commit:
   - read the whole `REPORT.md` and the receipts a conclusion rests on;
   - **look at the frames yourself** and re-run the key number (hashes, `cmp`, a checker)
     rather than trusting the worker's table; verify every label or code line a conclusion
     rests on (`ee-at`, `ee-label`, `rg` in the fork);
   - record: append a short `## Orchestrator gate` section to the lane's `REPORT.md`
     (verdict, what you checked, what's open), one line in `docs/todo.md`, the lane row in
     `docs/status.md`, live numbers in the ledger (speed only from clean builds, §5);
   - commit `[orch] Gate <ID> …` with explicit paths (`git commit -m … -- <paths>`; workers
     share the index), push `main`, close the pane **by exact pane id**.
3. **Tell Brad** in plain terms: what works now, what's next, anything waiting on him.
   Send viewable/listenable results with `SendUserFile` (audio as ≤ 5 MB `.m4a`);
   `PushNotification` only for blockers and major results while he's away.

Handoffs between orchestrators are not committed: the board, the todo and git log are the
handoff. Put anything session-specific in an untracked `local/handoff.md`.

## 2. Workers

Routing: `~/.config/agents/AGENTS.md`; current quota state: `local/AGENTS.local.md`.
As of 09-24: bounded briefs → `local/tooling/orch/launch-muse.sh <ID> "<prompt>"` (muse runs
Go Muse Spark Contributor, has SSH/adb); open-ended or high-judgment work → Opus panes
(`launch-opus.sh`) when Brad approves; local Qwen (opencode) for mechanical, script-checked
jobs; **no Codex workers** while its quota is low.

Every prompt names the write scope (the paths the brief names count as the started folder)
and says "first failure" means a failed brief step, not a typo in the worker's own command.
Read the pane about a minute after launch to confirm the brief arrived (`working` status
doesn't prove it). Muse panes can be re-prompted for a Part 2; a finished Codex pane can't
(continue it in a fresh pane).

| Kind | Lessons |
| --- | --- |
| muse (Go) | Good at bounded builds, device runs and source sorting; stops correctly on conflicts, so give explicit resolution rules when you release Part 2. |
| Opus | Auto-mode classifier refuses history rewrites: never brief a rebase; use a new branch plus cherry-picks. Good for exploratory sessions with free rein inside device rules (N8X1). |
| opencode (local Qwen) | Dense 27B for reads, sparse only for script-checked mechanics; paste lookup tables in; verify every label. `ssh` is denied. |
| Codex | Sandbox blocks fork git writes and runner boots unless escalated; Luna reads worker rules too literally. |

herdr: close panes by exact id; workers never prompt each other.

## 3. Writing briefs

The contract is in `AGENTS.md` (about one page). On top of it:
- **Check the ID is free** (`ls local/muse/prompts/<ID>.md`).
- **Discriminating gates:** work out what each hypothesis predicts first; run the null
  control before the treatment. Free-running boots are racy (first GS packet lands at tick
  40 ± 1), so GS changes are gated by capture + replay, not two live boots.
- **Split at judgment points:** Part 1 gathers evidence or prepares a script and stops;
  the orchestrator gates and releases Part 2 with the exact SHA.
- **Copy addresses and pins from their source report together with what they are.**
- **Exploration mode:** after two inconclusive bounded parts on one symptom, switch to a
  time-boxed frontier session with the device and free rein plus a notebook (N8X1 found in 40
  min what 15 h of narrow briefs didn't); return to bounded briefs once a mechanism is named.
- **Reference equivalence:** before trusting a baseline, check the reference takes the same code
  path (platform `#ifdef`s, feature fallbacks; the Mac never ran Adreno's binning path).
- **Full-signal measurement:** stereo mid/side (`local/research/AU7/midside.py`), per-tick
  hashes when hunting a first divergence, frames viewed yourself.
- **Ask Brad first** before any search for assets, hardware or preferences.
- Routes: race boots use I26-FAST (`local/research/I26/ROUTES.md`, race HUD ~tick 1714).
  600 s boot cap unless a brief grants more.
- Host contention: four mini boot slots (`local/tooling/p_lane_lease.py`); builds `nice`d;
  speed boots take all four. Never attach a debugger to a harness child.
- Workers read code with `local/tooling/ee/{ee-at,ee-func,ee-xref,ee-label}`.

## 4. Forks and branches

- **PS2Recomp** `brad-richardson/PS2Recomp` (remote `fork`), primary branch `ssx3`. Every
  lane works in its own worktree under `~/dev/ssx3-work/<ID>/PS2Recomp`. Folds happen in a
  lane that builds and runs the suite (from the worktree root). Before any push:
  `git diff --stat 14b1e5cb <branch> -- ps2xRuntime/src/runner` must be empty;
  fast-forward only; generated code never goes in the fork.
- **paraLLEl-GS** `brad-richardson/parallel-gs` and **Granite** `brad-richardson/Granite`:
  product fixes on `ssx3`, diagnostics on `wip/ssx3-n9`. Build from the fork tips, never
  from a dirty working copy (every GPU build before N9 did, which cost a provenance lane).
  Granite's submodule `origin` is upstream: push only to the fork URL. The orchestrator
  pushes these two forks.
- **Fold as you go:** product code lands on a fork branch in the lane that proves it; side
  branches fold the day they gate (the sound code sat unfolded while audio was measured).
- After a codegen-changing fold, regenerate and promote `~/dev/ssx3-work/codegen-ssx3`;
  keep one older copy for A/B (disk cap 200 GB, `local/tooling/disk_budget.sh`).
- Upstreams (read-only fetches fine, no contact): `ran-j/PS2Recomp`,
  `Arntzen-Software/parallel-gs`, `Themaister/Granite`.

## 5. Numbers

- Speed only from builds with diagnostics compiled out (`PS2X_ENABLE_DIAG_TAPS=OFF`, no
  runtime/aggressive logs, no frame dumps), stated as guest vsyncs/s ÷ 59.94, host named.
- Presents/s are not guest frames. Race numbers vary run to run: ≥ 2 runs.
- Mac wall rates are contaminated when other lanes run. Diagnostic numbers are labelled and
  never quoted as speed.

## 6. Devices

- **iPhone:** build and install only; never launch/test/screenshot unless Brad approves for
  that session. Test on the Simulator, then the iPad (ask Brad to unlock it).
- **Odin:** lease `/data/local/tmp/mg/LEASE`; `showing=false` before every launch;
  `dumpsys battery`: `AC powered: true` and ≥ 20 % (ignore `status`, which reads 3 on AC);
  **`am force-stop` after every run**; restore `ps2x.env` if a run changed it. Env keys in
  `ps2x.env` are `setenv`'d before `main`, so driver env (`TU_DEBUG`, …) reaches Turnip.
  Android logcat drops lines on big bulk flushes: pull on-device output files instead.

- The Odin on the mini's USB (serial `622c49b1`) discharges under any load; only the wall charger
  keeps it ≥ 20 %. Workers never toggle the Odin screen/keyguard (a wake test locks it behind
  the PIN, 09-25); read `dumpsys battery` and report.

- A fold only built on the Mac isn't proven for Android: Darwin's `uint64_t` is `unsigned long long`,
  Linux's is `unsigned long` (F2's lambda broke the NDK build). Compile the Android target before
  calling a runtime fold done.

- Disk: every lane's own build tree (~1.7 GB each, iOS staging ~6 GB) fills the 200 GB cap within a day of
  parallel lanes. After closing a lane, delete its `build*`/`staged*` dirs (rebuildable) unless a
  committed script references them (`grep -rhoE "ssx3-work/..." local/research/*/*.sh local/tooling`).

- Odin speed pairs drift with heat (NP1 09-25: the same APK read −7.3 % from its first to its last run
  of an ABBA set). Cool to thermal status ≤ 1 with a fixed wait before every run, prefer ABBA-BAAB,
  and report GameThread CPU per frame next to wall speed.

- Odin over Wi-Fi (09-25): Android Wireless debugging is paired with the mini (one-time pairing
  code). adb finds the Odin by mDNS and connects by itself, even after port changes and Wi-Fi drops;
  the serial is the service name in `local/odin-serial`
  (`adb-622c49b1-IJnTHA._adb-tls-connect._tcp`). Launchers read that file. Fallbacks: legacy
  `192.168.1.53:5555` (tcpip, lost on reboot) and USB `622c49b1`. If the Odin reboots and Wireless
  debugging comes back off, Brad re-enables it in Developer options (no re-pairing needed).

- Mac-only validation hides stack depth: the Mac's main thread has 8 MB and Apple clang may tail-call
  where Android's NDK doesn't (F4: VU1 chain recursion crashed the Odin at 512 frames). Anything with
  deep or chained calls gets a small-stack test (512 KB) on the Mac before a device build.

- bradflix (HS1): `bradflix_build.sh <fork-sha> <name> [--det]` (cold ~400 s, warm ~50 s, shared ccache in
  `~/dev/ssx3-work/ccache`); boots `ssx3_boot.py --host bradflix --mode det …` (det only; results pulled
  back, then `baseline.py compare` as usual; coverage lines compare as a multiset because libc++ and
  libstdc++ hash orders differ). Everything under `~/dev/ssx3-work/` there, never `/tmp`.

- Mac builds: `local/tooling/build/mac_build.sh <fork-worktree> <build-dir> [--det]` (the recipe of
  record behind a shared ccache; ~80 s warm vs ~270 s cold, byte-identical runners; `--no-cache` for
  controls). `ccache -z` before a measured build; never `ccache -C` without asking (it wipes every
  lane's entries). (RS1)

- Boots and controls: use `local/tooling/boot/ssx3_boot.py` (never copy a driver into a lane). Controls
  are cached: `local/tooling/boot/baseline.py get --pins PINS` prints the control dir (rc 2 `MISSING`);
  if missing, `make --pins PINS --runner R` once, then the lane boots only its candidate and runs
  `compare --key K --cand DIR`. Brief line: `Control: baseline key <K> (pins <path>); candidate: one
  ssx3_boot.py boot + compare.` (RS2)

- bytesize builds run over a held, foreground ssh: WSL stops the Ubuntu distro ~1–2 min after the last
  `wsl.exe` client disconnects, killing `&`/`setsid` jobs (F5 G5). Background the ssh on the mini instead.

- Before assigning a lane ID, check `local/research/<ID>/` doesn't exist (PF1 collided with an older Odin lane on 09-25).

## 7. Brad's preferences

- Plain updates; delegate longer work; say when something is waiting on him.
- He listens to audio and looks at frames himself: send them, correctly aligned.
- Widescreen anamorphic 16:9 with stretched 2D is accepted; upscaling is parked.
- No upstream contact until he says; upstreaming is the eventual goal (rebase parked).
- The 120 Hz goal means a true 120 Hz simulation, reported separately from faster emulation
  or interpolation.

## 8. Mistakes to avoid
- 09-26: BA1 ran `adb install` with no lease check while VK2 held the Odin, killing VK2's stress run
  (Android exit reason PACKAGE UPDATED). The old check-then-write lease was also racy. Fix:
  `local/tooling/odin_lease.sh` (atomic claim/release, `run` wrapper); briefs that touch the Odin
  must name it.
- 09-26: an opencode (local Qwen) brief asked for edits in a fork worktree under `~/dev/ssx3-work/`; the
  managed permission rules deny edits outside the started folder, so the worker (correctly) stopped. A local
  worker that must edit outside `~/dev/ssx3` needs `OPENCODE_CONFIG_CONTENT` via `herdr tab create --env`,
  or the job goes to muse.

- Racy or under-controlled gates (GB2 Parts 1–7; frame-hash gates on free-running boots).
- Hypotheses stated before evidence; labels relayed without verifying them.
- Addresses paraphrased into briefs with the wrong meaning (AU4's DMA source).
- Letting parallel builds starve a timing boot (E47).
- Committing with `git add` while a worker has staged files (use explicit paths).
- A reference A/B cut from a different capture's timeline (AU6, 09-24): verify alignment
  (NCC) before sending audio or frames to compare.
- Ad-hoc per-run thresholds instead of the standing rule (battery, 09-24).
- Measuring stereo audio in mono: a side-channel (L−R) fault is invisible in L+R.
- Scratch cleanup keep-lists must include every path a committed build script references (the
  09-24 cleanup deleted `ssx3-work/I25`, the iOS FFmpeg/SDL2 prebuilts; rebuilt into `ios-deps/`).
- Ending a turn without a live watcher (09-24 night): every lane finished and nothing was gated
  for ~7 h while Brad was offline. **Never end a turn with workers running unless a watcher (or
  a scheduled wakeup) is live**; when Brad goes offline, keep the loop going with watch.sh
  restarts, not a final message.
