# Orchestrating ssx3: runbook and lessons

For the next orchestrator session. It collects the rules, recipes and
lessons from the 2026-09-22/23 sessions that aren't in `AGENTS.md`. Read
these first:
- `AGENTS.md` (the rules: leases, devices, git, speed numbers);
- `docs/status.md` (the board);
- `docs/todo.md` (open work and every gate read);
- `docs/numbers-ledger.md`;
- `local/AGENTS.local.md` (hosts, worker-kind recipes, quota state).

Latest live handoff to Opus (2026-09-24): `docs/handoff-opus-2026-09-24.md`.

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
`local/AGENTS.local.md`. **Current 2026-09-24 override:** OpenCode Go
models are **standard tier**. Use Go Muse Spark Contributor or DeepSeek
Flash for suitable worker briefs to preserve Codex quota for orchestration;
local oMLX Qwen remains budget tier. Brad's stop rule is to issue no new
tasks once Codex weekly quota remaining reaches 5%. The 09-23 launch
notes below and §10's Codex-only handoff describe their historical state;
they do not override this routing.

As of 2026-09-23 evening (historical):
- Claude is near its weekly limit.
- muse is out until 2026-09-26.
  - **New lanes went to Codex `gpt-6-sol`** via
  `local/tooling/orch/launch-codex.sh <ID> "Your brief is local/muse/prompts/<ID>.md …"`.
- Brad resets the Codex quota once it's **below 5% left**. Tell him when
  it gets close (the Codex footer shows the weekly warning).
- Panes already running keep their model ("no need to stop in progress").

| Kind | Launcher | Lessons |
|---|---|---|
| Codex (`gpt-6-sol`) | `launch-codex.sh` (auto mode: `--approve-for-me`, workspace-write sandbox, network on, `--add-dir` ssx3-work / PS2Recomp / /tmp) | Auto mode since 09-23 evening, replacing `danger-full-access`. Sandbox denials (`nice`, `simctl`) escalate and get auto-approved; writes elsewhere (e.g. `~/.config`) are blocked. **The sandbox protects the top-level `.git` of each writable root, so git writes in fork worktrees fail, and the game runner hangs at graphics init inside it.** The launcher suffix therefore tells workers to escalate sandbox failures (not stop) and to run fork git writes and runner boots escalated from the start. Codex `execpolicy` `allow` rules don't help: they skip approval but still run in the sandbox (tested 09-23). Three lanes (AU3, E58, GB4) stalled on this once. The prompt suffix **must** grant the write scope: the paths the brief names (`~/dev/ssx3-work/<ID>`, fork worktrees, the lease files) count as the started folder. It must also say that "first failure" means a failed *brief step*, not a typo in the worker's own exploratory command. Luna (`gpt-6-luna`) stopped twice on literal readings of `~/dev/AGENTS.md` (GB4/AU3, 09-23), so Brad moved to Sol. Wait ~10 s after `agent start`: Codex's update banner swallowed GB4's first prompt, and the pane sat idle for an hour. **Read the pane a minute after launch to confirm it's working on the brief.** |
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
- Addresses paraphrased into a brief with the wrong meaning. AU4 was told
  to filter on the DMA source `0x512E40`, which is the tag-1 record
  *inside* the `0x512B80` buffer, and that cost a build and a capture.
  Copy each address from its source report together with what it is.
- Missing a lane commit that landed while the watcher was down (E58's
  `02ed074` sat unread under two `[orch]` commits). Before every
  `[orch]` commit, scan `git log --oneline -8` for lane commits you haven't
  gated.
- Trusting a Codex pane's model late in the week. Near its quota, one
  pane's footer showed `GPT-6-Luna medium` after launching on Sol, and a
  prompt to that idle pane never arrived. This happened twice (AU4 and E58):
  once a Codex pane finishes a turn, its footer flips to Luna medium and it
  ignores follow-up prompts. **Continue a Codex lane in a fresh pane**
  (`launch-codex.sh <ID>C "Lane <ID>, Part N (continuing) …"`) rather than
  re-prompting the old one.
- Committing with `git add <mine> && git commit` while a worker has staged
  files: the shared index sweeps their staged work into an `[orch]` commit
  (E58's report went into `421c51d`). Commit orchestrator changes with
  explicit paths: `git commit -m … -- <paths>`.
- Frame-hash gates on free-running boots (E56's SC hash at a fixed tick).
  Until E55's determinism mode lands, two boots aren't frame-identical at
  a given tick, so use viewed frames or capture/replay instead.

## 10. Resume state (written 2026-09-24 ~00:30, end of the 09-23 session)

The session ended at Brad's request: the Claude weekly and 5 h limits were
nearly used up. **Codex was reset at ~22:40 (93% left)**, and all running
lanes are Codex Sol in herdr workspace `w2`, auto mode per §2.

**On resume:**
1. Run `git log --oneline -15` and read every lane commit since `16b9474`.
2. Run `herdr pane list --workspace w2` and read each pane's tail.
3. Restart `local/tooling/orch/watch.sh` in the background.

A Codex pane that has finished a turn may not take a new prompt; continue
it in a fresh pane (`launch-codex.sh <ID>C "Lane <ID>, Part N (continuing)…"`).

| Pane | Lane | Doing | Gate when it lands |
|---|---|---|---|
| `w2:p1Y` | GB4 Part 6 | isolate the `PS2X_GS_BACKEND` env from unit tests; fix/characterize the paraLLEl present offset (CPU 00:00:08 vs paraLLEl 00:00:09 at one marker); clean PSNR table; diagnose the HUD small-text glyph breakage; first **live paraLLEl boot** (race reached?, presents/s, GameThread/GsWorker split, diagnostic) | View the side-by-sides yourself. If live paraLLEl reaches the race: plan Odin/Turnip (G lane) and a push of `gb4-parallel` after review |
| `w2:p22` | E56 Part 2 | cherry-pick onto `13cac7f`, regen, taps-OFF/ON suites, a 600 s stop-policy boot with zero misses, then **ff push to fork `ssx3` and promote the codegen** | Check the push (`git ls-remote fork refs/heads/ssx3`), the codegen promotion and the miss counters. After that, fold W1 |
| `w2:p24` | AU6 | why our EE mix is ~12 dB below PCSX2: the IOP status block at `0x50B740` (our HLE writes only the serial) and an active-stream/voice differential; lead H4 = MPF multi-layer music (charsel.mus = 139 stereo sections; `charsel.mpf` `PFDx`; 6-ch streams exist) | Loudness profile before/after and an `.m4a` for Brad |
| `w2:p25` | E60 | the sky packet's wrong ALPHA/CBP → VU0 data differential at `sceVu0MemReadQ` (VLQI `0x3feb8c`) vs a PCSX2 hook → name the writer (VIF0 / VU0 microprogram / EE store) → one fix | View the race frames (sky/sun/flare), and check the sky packet ALPHA=0x2a/CBP match |

**Waiting on Brad:**
- **W1 2D stretch:** in anamorphic 16:9, the 3D is correct but title/menu/HUD
  2D widen ~33%. Accept as the default, or queue a 2D-squeeze lane?
  (Frames were sent 09-23.)
- He listens to AU6's capture.

**Queued next, in order (briefs not yet written unless named):**
1. **W1 fold** into `ssx3` after E56 pushes. `w1-wide` includes I26's
   presenter + virtual pad `8a357ac`; desktop default becomes 16:9
   (anamorphic) + bilinear. Then reinstall the iPhone (install only; tell
   Brad).
2. **E54** semantics batch 2: PINTEH/PINTH lanes (AU5 found 4 PINTEH in
   the mixer candidate `0x3CB538`), LWU, 64-bit sign branches, COP0 Count
   from the EE cycle, CSR W1C/VSINT/FIELD, INTC 5/7. The review's §A2
   lists the sites.
3. **E55** determinism mode + hash tap (fixed RTC for `sceCdReadClock`,
   cycle-only events). It unblocks frame-hash gates (§9) and the ±1-tick
   GS race (GB3).
4. **E57** VU1 speed: pipeline/hazard bookkeeping is ~30% self on the
   Odin; VU1 is 39–50% of race time. The other lever is paraLLEl (GB4).
5. **I27** HiDPI drawable on iOS (the fonts); a small Codex lane.
6. After the sky fix + paraLLEl: an Odin rerun (N8) with a simpleperf race
   profile, and check N7's rider stall (0–1 MPH at 21–38 s).

**Numbers:** the ledger has clean speed rows for N5 (Odin pre-fold), E58
(Mac fold) and N7 (Odin fold, provisional). Diagnostic numbers stay out.

**Fork `ssx3`:** `13cac7f`. Canonical codegen = the E53 regen
(`~/dev/ssx3-work/codegen-ssx3`; `-pre-e58` and `-e53` copies exist;
E56 will promote a new one). Disk ~97/200 GB.

### Notes for a Codex (GPT Sol) orchestrator (09-24 handoff)

- You're the orchestrator: `~/.config/agents/AGENTS.md` (the "Work Method"
  section applies to you, not the worker rules) plus this repo's
  `AGENTS.md`. Where they say "Claude" for the orchestrator role, read
  "the orchestrator".
- Commit trailer for your `[orch]` commits: `Orchestrated-By: Codex`.
  Commit with explicit paths (`git commit -m … -- <paths>`); workers
  share the index (§9).
- Claude-only tools don't exist for you: `PushNotification`,
  `SendUserFile` and Artifacts. Tell Brad things in your replies, and give
  file paths for audio/images (he can open them on the mini).
- **Workers at handoff:** Codex lanes launched with
  `local/tooling/orch/launch-codex.sh` (Sol, auto mode with the escalation
  suffix). This is superseded by the 09-24 Go standard-tier override in
  §2; continue a finished Codex lane in a fresh pane only when routing
  calls for Codex.
- **The watcher:** run `local/tooling/orch/watch.sh` in the background
  (it exits on a lane commit, a blocked pane or the 25 min heartbeat),
  then gate and restart it.
- **Brad's standing rules:**
  - iPhone install-only;
  - Odin force-stop after every run;
  - no upstream contact;
  - fork ff pushes only after the runner-dir check;
  - never force-push or rewrite history;
  - no generated code in git.
