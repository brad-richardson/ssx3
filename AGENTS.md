# Agent guide for ssx3

Read by every agent working in this repo: the orchestrator (Claude) and
the workers (muse panes in herdr, codex). `CLAUDE.md` imports this file.
Machine-specific details (hosts, device serials, mount points) are in the
untracked `local/AGENTS.local.md`; read it too when it exists.

## Product direction (Brad, 2026-09-22)

- **Next milestone: stock SSX 3 gameplay through our PS2 static recomp
  runtime on the Odin 3.** A menu, working input, and a stock race that
  starts and advances.
- Eventual goal: 120 Hz, ideally **true 120 Hz simulation** (about twice
  the stock update rate at normal wall-clock speed). Faster emulation,
  duplicated presents and frame interpolation are different outcomes and
  are reported as such.
- On the Odin, shipping **Mesa Turnip** with the app (adrenotools-style)
  is acceptable (Brad, 09-22). This is Brad's own project built in the
  open, not a store product.
- NetherSX2 and PCSX2 are references and performance comparisons, not
  deliverables.
- A **dev-only startup-movie bypass** is approved (`PS2X_SKIP_MOVIE`,
  default off, labeled dev-only). Faithful movie playback is fixed
  separately.
- The GameCube/Dolphin route (course restoration, 120 fps host replay,
  iOS app polish) is **reserve**: `docs/reserve.md`. Don't schedule it
  unless Brad asks.

Milestone chain: stable build storage + native title → menu → stock race
+ GS composite correctness → GPU backend integration + Android app, title
linkage and input → Odin native race → measured budgets → 120 Hz sim.

## Where things are

| What | Where |
| --- | --- |
| Current board (lane, owner, pinned rev, next action, blocker) | `docs/status.md` |
| Open work, per lane | `docs/todo.md` (short; history in `docs/archive/`) |
| Every quoted number with its status | `docs/numbers-ledger.md` |
| Worker briefs | `local/muse/prompts/<ID>.md` (committed with `git add -f`) |
| Worker evidence | `local/research/<ID>/REPORT.md` + text receipts |
| Latest review | `docs/research/review-2026-09-22-progress-and-parallelization.md` |
| Parked GameCube work | `docs/reserve.md` |

Lanes: **E** PS2 runtime (PS2Recomp fork, branch `ssx3`), **G** GS
composite/GPU backend (paraLLEl-GS clone + `ps2xGS`), **N** Android app,
**T** PCSX2 reference traces, **I** iOS recomp (parked until E changes the
movie path), **V** storage/restore.

## Roles

- **Orchestrator (Claude)** owns the plan, briefs, gate reads, verdicts,
  `docs/status.md`, `docs/todo.md` and `docs/numbers-ledger.md`. It
  checks in on panes at least hourly, nudges stuck workers, and pushes
  `main` when the tree is clean.
- **Workers (muse)** execute one brief each in their own herdr pane. They
  hand back tables and receipts plus a recommended next action; they don't
  declare verdicts beyond what the brief asks. All implementation is muse
  (Brad, 2026-09-22). No Opus/reasoning-class workers unless Brad asks.
- Workers never edit `docs/status.md`, `docs/todo.md`, the ledger or
  plans. They may read other panes but never prompt them; coordination
  goes through the orchestrator. Subagents are fine for read-only
  fan-out; edits, builds, boots and commits stay in the main worker.

herdr recipe: `herdr tab create --workspace wN --cwd ~/dev/ssx3 --label
<ID>` → `herdr agent start <id> --kind muse --pane <pane> --timeout
120000 -- --yolo` → `herdr agent prompt <id> "Your brief is
local/muse/prompts/<ID>.md …"` → `herdr agent read|get|wait <id>`.
Close the pane after its gate read.

## Brief contract (keep briefs to about one page)

1. Goal and why it matters for the milestone.
2. Facts to start from, with links to the reports they came from.
3. Hypothesis, the correct-behavior model ("the implementation is right
   on these inputs"), the alternatives, and the observable that tells
   them apart. Equal predictions can't discriminate, so work them out
   before any device run.
4. Budgets: builds, boots/runs, time box, byte caps on new dirs.
5. Allowed changes. Briefs may go from diagnosis to **one** candidate fix
   plus one validation run when a single mechanism is named. No tuning
   loops.
6. Stop rules, and how each outcome changes the next action.
7. Deliverable: `REPORT.md` with tables, exact commands, pinned
   revisions, binary SHAs, and gaps stated plainly, plus an `[<ID>]`
   commit with the `Orchestrated-By: Muse Code` trailer. No push.

Dropped on 2026-09-22 as ceremony: prefix-SHA tail receipts,
zero-growth `du` audits of unrelated dirs, and one-question-per-build
splitting.

## Standing rules

- **No upstream contact.** No issues, PRs, filings or Discord posts for
  PS2Recomp, paraLLEl-GS, Granite or others until Brad has proved the
  route and read the code. Fork-and-fix locally is fine. The Adreno
  filing is paused.
- **Git:** never force-push or rewrite history. Workers commit and don't
  push; the orchestrator pushes `main` when the tree is clean. Check
  `git log -1` before committing because several lanes commit to `main`.
  Generated guest code, game data and binaries are never committed or
  pushed anywhere public. On the fork this means nothing under
  `ps2xRuntime/src/runner/` may differ from upstream (`git diff --stat
  14b1e5cb <branch> -- ps2xRuntime/src/runner` must be empty before any
  push). Generated sources live outside the repo via
  `PS2X_GAME_CODEGEN_DIR`. Never `git add -f` inside the fork. The fork's `ssx3` branch holds plain commits;
  experiment branches stay local unless the orchestrator says otherwise.
- **One live PS2 runtime mutator** (the E lane owns the fork checkout and
  the P-lane lease). E and G own distinct files. N ports what it needs on
  its own local branch or hands edits to E.
- **Leases:** one device agent on the Odin at a time
  (`/data/local/tmp/mg/LEASE`) and one host emulator/boot at a time
  (`/tmp/ssx3-p-lane-lease`). Claim before a run and release after.
- **Boots:** every boot script has progress caps. No boot over 600 s
  without orchestrator OK.
- **Storage:** work on the Mac mini's internal disk, capped at 200 GB
  across all ssx3 workstreams (`local/tooling/disk_budget.sh`; details in
  `local/AGENTS.local.md`). The external SSD is ExFAT scratch that
  randomly disconnects (no data loss): nothing live runs from it. Any
  binary that goes to a device, or any pinned input, still gets two
  matching SHA reads before use. Set `COPYFILE_DISABLE=1` on SSD writes.
  Mirror receipts to the share tier.
- **Speed numbers** come only from builds with diagnostics compiled out
  (no runtime/aggressive logs, frame dumps, function traces or watch
  sets), and are stated as guest vsyncs per wall second ÷ 59.94. Numbers
  from diagnostic builds are labelled as such and never quoted as speed.
- **Evidence:** text in git; bounded logs (rings, compress closed logs,
  one canonical copy); reuse existing tools (T1/T5/T12/T22 trackers)
  rather than copying them.
- **Devices:** always `install` (even if present) on the Odin and iPad;
  iPhone installs are fine but never urgent. After an Odin reboot the PIN
  must be entered once before APKs launch (adb-shell binaries still work).
  Before every APK launch, check the Odin isn't on its lockscreen
  (`dumpsys window policy`: `KeyguardServiceDelegate showing=false`): a
  locked device pauses the app within seconds and the run is void. Ask Brad
  to unlock it. Force-stop the app when a lane is done with the device.
- **Ask, don't queue silently:** any decision waiting on Brad, or a
  device/hands-on need that would unblock work, is reported as a
  blocker right away.
