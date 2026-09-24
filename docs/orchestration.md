# Orchestrating ssx3: runbook and lessons

For the next orchestrator session. It collects the rules, recipes and
lessons from the 2026-09-22/23 sessions that aren't in `AGENTS.md`. Read
these first:
- `AGENTS.md` (the rules: leases, devices, git, speed numbers);
- `docs/status.md` (the board);
- `docs/todo.md` (open work and every gate read);
- `docs/numbers-ledger.md`;
- `local/AGENTS.local.md` (hosts, worker-kind recipes, quota state).

## 1. The loop

1. **Watch.** Run `local/tooling/orch/watch.sh` in the background (herdr
   workspace from `WS`, default `w2`). It exits on:
   - a new non-`[orch]` commit on `main`;
   - a pane in `blocked` state;
   - the 25 min heartbeat (`MAX=1500`), when it lists pane states.

   Restart it after every exit. On the heartbeat, read any pane that's
   `done` or `idle` (`herdr agent read <pane> | tail`). A Claude pane shows
   `done` while it waits on its own background shell; that's normal. A
   Codex pane that's `idle` with no commit has stalled or stopped.
2. **Gate.** Do the following for each lane commit.
   - Read the whole `REPORT.md`.
   - **Look at the frames yourself** (the Read tool on the PNGs), and
     verify every label or code line a conclusion rests on (`ee-at`,
     `ee-label`, `rg` in the fork).
   - Decide. Then record the gate:
     - a `[x]` entry in `docs/todo.md` in that lane's section (what
       passed, what's open, the next action);
     - the lane's row in `docs/status.md`;
     - `docs/numbers-ledger.md` rows (speed only from clean builds, §5).
   - Commit `[orch] Gate <ID> …` with the session trailer and push `main`.
   - Close the pane **by pane id**.
   - Write the next brief and launch it.
3. **Tell Brad** the result in plain terms: what works now, what's next,
   and anything waiting on him.
   - With Remote Control on, use `PushNotification` only for blockers and
     major results while he's away. It's skipped when the terminal is
     active.
   - When a build lands on his iPhone, say so ("installed, not
     launched").
   - Send listenable or viewable results with `SendUserFile`. For
     example, AU2's audio went as a ≤3 MB `.m4a` made with
     `afconvert -f m4af -d aac`.

## 2. Workers

Routing is in `~/.config/agents/AGENTS.md`; the current quota state is in
`local/AGENTS.local.md`. As of 2026-09-23 evening:
- Claude is near its weekly limit.
- muse is out until 2026-09-26.
- **New lanes go to Codex `gpt-6-sol`** via
  `local/tooling/orch/launch-codex.sh <ID> "Your brief is local/muse/prompts/<ID>.md …"`.
- Brad resets the Codex quota once it's **below 5% left**. Tell him when
  it gets close (the Codex footer shows the weekly warning).
- Panes already running keep their model ("no need to stop in progress").

| Kind | Launcher | Lessons |
|---|---|---|
| Codex (`gpt-6-sol`) | `launch-codex.sh` | The prompt suffix **must** grant the write scope: the paths the brief names (`~/dev/ssx3-work/<ID>`, fork worktrees, the lease files) count as the started folder. It must also say that "first failure" means a failed *brief step*, not a typo in the worker's own exploratory command. Luna (`gpt-6-luna`) stopped twice on literal readings of `~/dev/AGENTS.md` (GB4/AU3, 09-23), so Brad moved to Sol. Wait ~10 s after `agent start`: Codex's update banner swallowed GB4's first prompt, and the pane sat idle for an hour. **Read the pane a minute after launch to confirm it's working on the brief.** |
| Claude Opus | `launch-opus.sh` (`--permission-mode auto`) | The auto-mode classifier refuses history rewrites (`git rebase`, `branch -f`), which is correct under our rules. So briefs must never ask for one: use a new branch plus cherry-picks (N5). |
| muse | `launch-muse.sh` | Quota out until 09-26. |
| local Qwen (opencode) | recipe in `local/AGENTS.local.md` | The dense 27B stalls at its 16k output cap; `thinking_budget: 8192` fixed that (dev-71). Resume a stalled worker with `--session`, not a fresh start. `lsp` and `web_search` are on: briefs say "cite the repo, not the web". Paste lookup tables in; verify every label. Only for low-reasoning reads and runs. |

**herdr gotchas:**
- Close panes by exact pane id. A name-filtered `head -1` closed the
  wrong pane once.
- `herdr agent prompt … --wait --until working` returning `working`
  doesn't prove the brief arrived. Read the pane.
- Workers never prompt each other; everything goes through the
  orchestrator.

## 3. Writing briefs

The brief contract is in `AGENTS.md`. On top of it:
- **Check the ID is free** (`ls local/muse/prompts/<ID>.md`).
  Overwriting the GameCube-era `A1.md` once cost a restore; audio lanes
  are `AU*`.
- **Discriminating gates.** Work out what each hypothesis predicts first,
  and run the null control before the treatment (off vs off).
  - GB2/GB3 lesson: free-running boot A/B comparisons are racy. The game
    reaches its first GS packet at tick 40 ± 1 depending on host timing,
    before any GS work. GS-side changes are gated by **capture + replay**
    (the same stream in, compare VRAM), not by two live boots.
  - Any live A/B must first check that packet 0 lands on the same tick.
  - GB2's racy live-present gate and its CSR-only drain were
    orchestrator gate-design errors.
- **Routes:** race boots use **I26-FAST** (`local/research/I26/ROUTES.md`),
  race HUD at tick ~1714; E33 got there at ~7100.
  - The Rival card ignores X while down is held.
  - The 600 s boot cap exceptions are granted per brief, explicitly
    (E53 Part 2 got 900 s).
- **Host contention:** two mini boot slots
  (`local/tooling/p_lane_lease.py`). Builds run `nice`d and wait for no
  other clang/ninja. E47's race boot starved at 0.6× next to E48's builds.
  Speed boots take both slots.
- **Never attach a debugger to a harness child.** AU2's lldb capture made
  the harness think the runner had exited. It released the lease and ran
  ~10.5 min unleased and over the cap.
- **Workers read code with the EE helpers** (`local/tooling/ee/ee-at`,
  `ee-func`, `ee-xref`, `ee-label`). Orchestrator-verified labels go in
  `local/tooling/ee/labels.tsv`.
- Workers split diagnosis → fix as Part 1 → Part 2 briefs when a judgment
  sits in between. Continuing in the same pane is fine when its context
  matters and the quota allows.

## 4. Fork (PS2Recomp) procedure

- Canonical branch `ssx3` on `fork` (`brad-richardson/PS2Recomp`). The
  remote is named `fork`, not `origin`, in `~/dev/PS2Recomp`, and that
  checkout sits on `ssx3`.
- Every lane works in its own worktree under `~/dev/ssx3-work/<ID>/PS2Recomp`
  on a local branch.
- **Folds happen in a lane that builds and runs the suite.** Never
  cherry-pick and push blind. Test registration
  (`ps2xTest/CMakeLists.txt`, `ps2xTest/src/main.cpp`) conflicts between
  sibling branches; `73b8b3a` needed I25's env-file test to apply.
- Before any push: `git diff --stat 14b1e5cb <branch> -- ps2xRuntime/src/runner`
  must be empty. Push fast-forward only. Generated code never goes in the
  fork.
- After a codegen-changing fold, regenerate and promote
  `~/dev/ssx3-work/codegen-ssx3`. Keep one older dir for A/B, delete the
  rest (disk cap 200 GB, `disk_budget.sh`).
- The pending fold after E53 Part 2 is in `docs/todo.md` (N section).

## 5. Numbers

- Speed numbers come only from builds with `PS2X_ENABLE_DIAG_TAPS=OFF`
  (N5 found the taps compiled into every guest store since E40, which made
  guest `.text` 3.2×). They also need runtime/aggressive logs off and no
  frame dumps. Stated as guest vsyncs/s ÷ 59.94.
- Presents/s are **not** guest frames: the host presents ~60/s whatever
  the guest does.
- Race numbers vary run to run (the RNG is seeded from the RTC; E55's
  determinism mode will fix that), so use ≥2 runs.
- Mac wall rates are contaminated when other lanes run (load average ~20).
  Diagnostic builds are labelled as such, and their numbers are never
  quoted as speed.

## 6. Devices (Brad's standing rules; details in `AGENTS.md`)

- **iPhone: build and install only.** Never launch, test or screenshot it
  unless Brad asks for that session. Test on the Simulator, then the iPad
  (it's often locked: ask). Profile `f0793278-…`, wildcard, expires
  2027-09-16.
- **Odin:**
  - lease `/data/local/tmp/mg/LEASE`;
  - keyguard `showing=false` before every launch;
  - `dumpsys battery` charging and ≥20 %;
  - **`am force-stop` after every run**, because the charger can't keep
    up with a running app.

## 7. Brad's preferences

These are from 09-23 and aren't all in `AGENTS.md` yet:
- He checks overall quality on the iPhone and flags issues early (fonts,
  artifacts, startup), so keep the iOS build current and tell him when a
  new one is installed.
- Widescreen 16:9 by default is planned (W1, after the E53 fold).
  Upscaled internal resolution is **parked** (W2): widescreen and the
  120 Hz sim come first.
- He wants sound (AU lanes) and listens to captures himself: AU2's was
  "recognizable but distorted" (AU4 is comparing against PCSX2).
- No upstream contact. The 120 Hz goal means a true 120 Hz simulation,
  reported separately from faster emulation or interpolation.

## 8. Where the technical story stands (09-23 evening)

Solved, with reports under `local/research/<ID>/`:

| Area | What fixed it |
|---|---|
| Menu 3D | E46: 19 missing indirect-call entries, `extra_function_starts` in `games/ssx3/ssx3.toml` |
| Movies end | E49: MPEG end word |
| Camera and race world | E50: SQRT.S used the wrong operand, CVT.W.S rounded instead of truncating |
| COP2/FPU semantics batch 1 | E53: VSQI/VCALLMSR, special values, RTZ+FZ, no FMA contraction, `log` stub ABI, VU1 EFU tables. The pre-race terrain now renders |
| VU1 on arm64 | E45: `double` instead of quad soft-float |
| Odin | N6: the built-in controller works. N5: the Odin plays to the race: 0.47× title, 0.33× SC, 0.19–0.26× race; VU1 50 %, GS raster 36 %, guest 0.4 % |
| iOS | I25/I26: Simulator + iPhone. Black startup, fast route, 4:3 bilinear presentation, virtual pad |
| Sound | AU1/AU2: EA SND mixes on the EE; the IOP needs only a cid-1 tick at 93.75 Hz; tag-1 PCM goes straight to host audio |
| Menu artifacts | G46: upstream (wrong texture-page contents), not the GS backend. The fonts were host presentation |

Open work is in `docs/todo.md`. The main threads:
- **E53 Part 2:** the race validation plus a VU0 per-call cost profile.
  About 830 VU0 calls/vsync now drops the race to ~6 ticks/s on the Mac.
- **The fold + N7:** the Odin textured race.
- **E54:** semantics batch 2 (PINTEH, COP0 Count, CSR W1C, …).
- **E55:** determinism mode.
- **E56:** function-boundary closure and the stop policy.
- **E57:** VU1 speed.
- **GB4:** GS capture/replay gate, then paraLLEl live.
- **AU3/AU4:** sound.
- **W1:** widescreen.
- **I27:** HiDPI on iOS.

The plan-of-record reasoning for E54–E57 is in
`docs/research/review-2026-09-23-frontier-2.md`.

## 9. Orchestrator mistakes to avoid (from these sessions)

- Briefs that asked for a rebase (N5): forbidden, so plan a new branch
  instead.
- Racy or under-controlled gates (GB2 Parts 1–7, T61's filter admitting
  mode 3).
- Hypotheses stated before the evidence: the E48 UI-glyph idea was refuted,
  and `sub_003629B8` was misnamed as the w0 writer. Verify with the
  helpers before relaying.
- Edits by Python string anchor that didn't match: grep first, or use
  the Edit tool.
- Letting parallel builds starve a timing boot (E47).
- Reading a pane's `working` status as proof the prompt landed (GB4).
