# Progress review, Sept 17–19 (PS2 recomp focus)

Written 2026-09-19 evening by the frontier session from: `docs/todo.md`
(Now section), `docs/numbers-ledger.md`, `local/research/P1/REPORT.md`
(Parts 1–22), the fork log at `/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp`
(branch `ssx3`), the muse session logs under `~/.local/share/muse/sessions/2026/09/1[89]`,
and the live herdr panes (p1v, m14, i5, wN:p3). Audience: the user and the
muse orchestrator. Sections 7 and 8 are the actionable part.

**Standing user decision recorded here (09-19):** upstream submission of
fork fixes or ps2xGS patches is NOT a priority until the user has proved the
route out and read the code personally. Keep fixes upstream-shaped (clean
commits, tests) but do not brief, schedule, or recommend any submission,
Discord ask, or PR prep.

## 1. Summary

The PS2 static recompile of SSX 3 has cleared eight boot parks in about 30
hours of wall time; the ninth fix (P1v) is being built tonight. No frame has
been rendered yet. Progress is real and every step is receipted, but the
pace is set by how many briefs each park costs, and one park cost ten. The
two most expensive stretches were interpretation errors that a direction
read would have caught early.

Three lanes ran in parallel across Sept 18–19, all as muse panels in herdr,
214 commits in ssx3 since Sept 16:

- **P lane (PS2Recomp fork).** 22 report parts, 23 fork commits over
  upstream, six behaviour fixes. Thread 1 now leaves the CD-driver park and
  spins on a semaphore the runtime refused to create; P1v makes zero-max
  `CreateSema` succeed.
- **M lane (GameCube host replay, 120 Hz route).** Milestone 2 nearly done.
  The M7–M9 "zero pixel" mystery was a measurement artefact (skip-to-VRAM
  uninitialised pattern, not rendered output); camera deltas now move real
  bytes in rendered frames on 100/100 replays.
- **I lane (PS2 runtime on the iOS Simulator).** From no iOS backend to a
  linked 120 MB arm64 `.app` in five briefs. Install fails on a missing
  `CFBundleIdentifier`, a one-line CMake fix.
- **G lane (ps2xGS harness).** Resting. 102 captures, sensitivity proven,
  CPU backend profiled at release. Reactivates when the game produces frames.

Since 09-18 20:22 a muse session (pane wN:p3), not a frontier model, has
been the orchestrator: it wrote the briefs, read the gates, and since 09-19
19:20 launches follow-ups on its own ("polls carry launch authority"). That
is the single largest process observation here; most recommendations follow
from it.

## 2. The boot ladder

Eight parks cleared between Sept 18 13:00 and Sept 19 16:00, one behaviour
fix per park. The SYNCTASK stretch is the outlier: ten briefs, ~16 hours of
wall clock, for a 46-line fix.

| Rung (where thread 1 parked) | Briefs | Wall clock | Fix | Fork commit |
| --- | --- | --- | --- | --- |
| SDK kernel-patch scanner polls `FindAddress` forever | P1 | 09-18 morning | TOML `ret0@0x0042c1f0` | config only |
| `sceCdRead` LBN 0x10 fails; constructor prologues merged by analyzer | P1b | 09-18 13:00–17:00 | `PS2X_CD_IMAGE` env hook; function-map CSV splits (39 ctors) | `cf06e36` |
| Every thread parked: `sceCdCallback`/`sceCdInitEeCB` were no-ops | P1b–P1c | 09-18 afternoon | Async CD completion callback HLE | `04905db` |
| Main thread returns to 0: INTC handler prologue overwrote its parked frame | P1d–P1f | 09-18 18:00–20:33 | Handlers/alarms on reserved stacks, not thread sp | `6046260` |
| VIF0 STR poll spins: analyzer folded LUI+ORI MMIO to page base | P1g–P1h | 09-18 20:33–21:32 | Analyzer low-half fold, 245/273 `[mmio]` corrected | `f2149e7` |
| GS CSR wait: nothing produces FIFO bits 15:14 | P1i–P1j | 09-18 21:32–22:42 | Hard-wire FIFO EMPTY, guest writes read-only (documented cheat) | `8fad69e` |
| SYNCTASK driver park: CD callback registered mid-function, invocation silently dropped | P1k–P1t (10) | 09-18 22:42 → 09-19 15:09 | Exact-entry host shim for 8 insns at 0x3E3AD8 | `58c9144` |
| `WaitSema(-1)` spin: game stores an unchecked zero-max `CreateSema` return | P1u–P1v | 09-19 15:09 → | Accept max 0 as binary semaphore (P1v, building) | pending |

Also in the P lane: P2 (PCSX2 source read, negative result), P3/P4 (fork and
downstream survey, 20 borrowable snippets tabled with bodies), P5 (360/N64/
PSP/Xbox recomp tooling survey, 32 borrowables), P6 (ssxdecomp names: 801
addresses, 6.7% coverage, none of the ladder addresses named). **None of the
borrowable snippets has been applied**; every fix was written from the
fork's own diagnostics.

What still stands between the runtime and a first frame is unknown. Known
candidates: IOP RPC traffic for pad and sound (SNDDRV, PADMAN), the VIF/GIF
path into the CPU GS backend, and the EA intro movies (`.mpc` on the disc),
which no brief has looked at.

## 3. Fork inventory

23 commits over ran-j/PS2Recomp `14b1e5cb`, 15 files, +1258/−75. Six change
behaviour, five are iOS build plumbing, thirteen are env-gated diagnostics.
P1v's tree adds an uncommitted scheduler change with a unit test.

| Class | Commits | Notes |
| --- | --- | --- |
| Behaviour, hardware-faithful | `6046260` reserved stacks; `f2149e7` MMIO fold; `04905db` CD callback HLE; `cf06e36` CD image hook | Generic, tested where the harness allows. |
| Behaviour, documented cheat | `8fad69e` CSR FIFO EMPTY | Comment cites four emulators and names the replacement (GIF occupancy tracking). Fine until a GIF FIFO exists. |
| Behaviour, game-specific | `58c9144` shim for 0x3E3AD8 | Hardcoded SSX 3 address in `Stubs/CD.cpp`. P1t's own table says a CSV split is the correct fix (§4.3). |
| Behaviour, provisional | P1v zero-max `CreateSema` (uncommitted) | Rule chosen by inference, not from the kernel (§4.4). |
| iOS build plumbing | `abc6f6c`, `d62c4b5`, `66d992c`, `4eb7a8e`, `53bac61` | Desktop-proof by byte-identical install + green tests. |
| Diagnostics | 13 `Diag:` commits | All behind `PS2X_DIAG_*`: thread dumps, syscall/call histograms, RAM watchpoints, sema trace, driver-entry probe, CreateSema census. |

Game-side configuration is split: the TOML lives in the fork tree; the
function-map CSV (1,000+ splits, as much game config as the TOML) is
untracked on the SSD under `P1/`. That split is what forced the shim.

One `ps2xTest` case fails build-to-build, alternating between AFAIL and
GsSyncV on the same tree. Order/state dependent, documented pre-existing,
queued since P1j and never scheduled.

## 4. Observations: P lane

### 4.1 The SYNCTASK stretch cost ten briefs and the answer was visible at brief one

P1k's report (09-18 23:03) already said: the first CD callback signals sema
26 yet thread 2 never wakes. A signal with no wake is a runtime bug by
definition. The next seven briefs (P1l–P1r) instead chased the driver-flag
writer chain: splits, watch-miss mechanism, driver-entry probe, true-frame
watch, table base, entry-0 selection, signal-during-park order. Each was
individually correct and receipted. P1s (09-19 13:23) finally looked at
delivery and found the runtime attaches the invocation, then silently zeroes
the pc because the address has no function-table entry. P1t fixed it in 46
lines.

Inside that stretch, a three-brief saga (P1l, P1m, P1n; 00:08 → 07:45) was
caused by a hex slip in the P1l brief (`0x1fffd80+0x80` written as
`0x1ffe000`) that the orchestrator "audited correct" twice. The agents did
exactly what was asked. The brief was wrong.

Both are interpretation errors, the class CLAUDE.md names as the expensive
one. Neither was an execution error.

### 4.2 Silent drops are the recurring root cause

Three of eight rungs were the runtime discarding something without a trace:
`SetAlarm` rejecting an address (P1c), the analyzer folding MMIO targets
(P1g), and the scheduler zeroing a guest invocation (P1s). Each took a
multi-brief hunt to find because nothing announced the drop. A fork-wide
rule (every rejected/unhandled path in the scheduler, syscall dispatcher,
stub layer, and analyzer emits one diagnostic line, on by default in the
runner) would turn the next such park into a single boot.

### 4.3 The shim is debt created by process, not by the problem

P1t's Part 21 table evaluates a CSV split at 0x3E3AD8 as functionally
correct (clean `jr $ra` boundary on both sides, zero collision) and cleaner
than the shim. It was rejected because the CSV is untracked, so a split
produced no committable diff and failed the brief's "Fix: commit + the diff"
receipt rule. The result is a game address and eight hand-emulated MIPS
instructions inside runtime code. Every further mid-function callback the
game registers would become another block in `CD.cpp`.

### 4.4 The zero-max semaphore rule is provisional and checkable

P1v's fix treats `max_count == 0` as 1. PCSX2 is LLE and its sources are
silent, as the agent found. The inference (the game ships two unchecked
zero-param creates and runs on hardware) is reasonable. But the real answer
is the EE kernel's `CreateSema`, disassemblable from the BIOS the user has.
This is the second "game expects X, runtime refuses" fix; a rule is needed
for the pattern (§7.4).

### 4.5 Cadence and cost

P-lane briefs ran 0.5–3.6 h each, 40–190 tool batches, 0–7 failed commands.
Gate-read latency has been the bottleneck as often as agent time: the
orchestrator noted twice that agents finished unnoticed between check-ins
(fixed 09-19 with the hourly cron). The lease protocol worked: zero forced
waits recorded across M and P sharing the host.

### 4.6 The GS backend question should not reopen on G6

G6 measured the CPU GS backend at 0.36 ms median per present at -O3 and
noted "GPU urgency reopens". Those are 64×64 synthetic presents. The
throughput gate measured 1.5–2.4 ms of GS work per frame on NetherSX2's
hardware renderer thread at 512×448; SSX's blended particle load on a
software rasterizer at that resolution will be far worse. Decide on G1
captures of real frames, not synthetics.

## 5. Observations: orchestration

- **Hand-off.** At 09-18 20:22 the user asked a muse session to "pick up
  where [Claude] left off in monitoring and orchestrating." It has run 23
  hours, 51 user prompts, 631 tool batches, and authored every gate read
  and brief since (commits carry `Orchestrated-By: Muse Code`).
- **What it does well.** Receipts and verification. Each gate read
  re-derives counts, re-runs tests, checks shas and pushes, and records
  "what I could not do" faithfully. Pane reuse, lease discipline, disk
  discipline, and the hourly poll all work.
- **Where it costs.** Direction. §4.1's two misses are the whole cost of the
  SYNCTASK stretch. The brief cadence is one narrow question per brief,
  which is the right shape for muse executing, but nobody asked "which of
  the open anomalies is most likely the runtime's fault" between briefs.
- **Since 09-19 19:20** the polls carry launch authority, so briefs now
  queue with no frontier read at all. That removes the last point where a
  direction error could be caught before it costs a brief.
- **Rule drift.** The 09-18 memory says "muse runs every implementation
  step, Claude does the judgment between briefs." Judgment between briefs
  has been muse since 20:22 that day.

## 6. Other lanes

- **M lane.** M5–M14 delivered milestone 2 items 1–3 of host replay
  (replay fidelity, event-bus split + frame aging + record guard, pose
  interp/camera delta on the `g_transform` seam). M10 proved the earlier
  zero-pixel results were an instrument error. M11–M13 partitioned where
  delta bytes land (slot 36, indexed path, per-draw). M14 is measuring the
  true camera-delta pixel effect and which draws carry it. Open question
  after M14: what to do with a proven transform seam (milestone 3 is the
  on-device interpolated frame).
- **I lane.** I1 (spike) found raylib 5.5 has no iOS backend; I2 fixed the
  fork CMake; I3 tabled upgrade/fork-patch/SDL; user chose SDL; I4 built
  SDL2 + raylib-SDL-ES2 + runtime into a 120 MB Simulator `.app`; I5 could
  not install it (no bundle ID). Touch input has no owner anywhere in the
  runtime or rlImGui.
- **G lane.** G0–G6: repo, `.gscap` format, recording backend, `gsreplay`,
  78 → 102 synthetic captures, `strict` oracle backend, present-heuristic
  pins, CLUT/RMW/Present spikes as patch files, release-build numbers. All
  identity-exact, CTest green. G1 (game captures) gated on first frame.

## 7. Recommendations (prioritized, brief-ready)

1. **Restore a frontier direction read at fixed points.** Muse keeps polls,
   gate reads on receipts, and brief mechanics. A frontier session reads
   direction (a) after every P-lane behaviour fix lands, (b) whenever a park
   survives three briefs, (c) before any brief that changes game-vs-hardware
   semantics. Roughly four reads a day. Owner: user (it is a quota call).
2. **Land "no silent drops" in the fork before the next park (one brief).**
   Every rejected or unhandled path in `EeScheduler`, `Syscalls/Dispatcher`,
   `Stubs/*`, and `elf_analyzer` emits one line (`[drop] <site> <reason>
   <args>`), on by default in the runner, gated only by a kill switch.
   Receipt: a boot log's `[drop]` census. Owner: orchestrator brief.
3. **Capture a PCSX2 runtime trace of the real boot (one brief, read-only,
   host only).** PCSX2's EE syscall/thread/CD logging on the real ISO to the
   first menu frame gives the ordered sequence the fork must reproduce.
   Store it under `$W/P1/ref/`. Each future park then starts with "where
   does the fork's histogram diverge from the reference" instead of first
   principles. P2 read source; this is different. Owner: orchestrator brief.
4. **Track the function-map CSV, then replace the shim with a split.**
   Decide where the CSV lives (fork branch alongside the TOML is the
   natural place; `local/` in ssx3 is the alternative). Then a brief splits
   at 0x3E3AD8, removes `ssx3CdCallbackSemaSignal`, and proves the boot
   ladder identical. Owner: user decides location; orchestrator briefs.
5. **A rule for game-expects-X fixes.** Hardware semantics first, verified
   against the EE kernel disassembly when emulator sources are silent.
   Anything that cannot be settled goes in a per-game quirks section of the
   TOML, never a constant in runtime code. Apply retroactively to P1v: one
   short brief to disassemble kernel `CreateSema` and confirm or amend.
6. **Decide the movie player before the ladder hits it.** Check the disc
   for `.mpc` in the boot path; default to an HLE stub that reports
   completion, logged, revisited after frames exist.
7. **Schedule the flaky `ps2xTest` case.** It has been queued since P1j and
   keeps costing a "pre-existing failure" paragraph in every gate read.
8. **Do not reopen the GS compute-rasterizer decision on G6.** Measure on
   G1 captures.
9. **Fix the bundle ID and get one Simulator launch receipt, then park the
   I lane** until the phone is back; the next gaps (touch, lifecycle) only
   matter on a device.
10. **Write the route-comparison criteria now** (host replay vs PS2 recomp
    for 120 Hz): Odin frame-time budget, visual correctness receipt,
    remaining-work estimate. Decide nothing yet; the comparison point is
    "host replay shows an interpolated frame on the Odin" and "PS2 shows a
    first frame with a real GS census".

## 8. Upcoming branching decisions

| When | Decision | Options | Recommendation |
| --- | --- | --- | --- |
| Now (P1v landing) | Who reads direction on the P lane | muse only; frontier at fixed points; frontier fully back | Frontier at fixed points (§7.1) |
| Before next park | Tooling first or keep diagnosing | first principles per park; drop-instrumentation + PCSX2 trace first | Both tooling briefs first (§7.2, §7.3) |
| Now | Where the function-map CSV lives | fork branch; ssx3 `local/`; stay untracked | Fork branch, then replace shim (§7.4) |
| Now | Rule for game-vs-hardware semantics | game's expectation as quirk; hardware from kernel | Hardware from kernel, TOML quirks fallback (§7.5) |
| Before it is hit | Boot movies | HLE stub; decoder | Stub, log, revisit (§7.6) |
| Week of Sept 21 (mini arrives) | Where the GS GPU loop starts and what moves to the mini | wait for game frames; start S1/S2 on synthetics now | Start S1 on the mini day one; P-lane builds and boots move too, laptop keeps orchestration + Odin |
| After I5 fix | How much Simulator work before the phone | continue to touch/lifecycle; park after first launch | Park after first launch (§7.9) |
| After M14 + first PS2 frame | Which 120 Hz route continues | host replay; PS2 recomp; both | Not yet; write criteria now (§7.10) |

Upstreaming is intentionally absent from this table per the user's
decision recorded at the top.

## 9. Evidence

- Ladder, fixes, receipts: `local/research/P1/REPORT.md` Parts 1–22;
  `docs/numbers-ledger.md` rows "PS2Recomp …".
- Fork commits: `git log origin/main..HEAD` in the fork clone (23 commits);
  `git show 58c9144`, `8fad69e`.
- Shim vs split reasoning: REPORT Part 21 §P21-1a.
- Zero-max sema evidence: REPORT Part 22 §P22-1, §P22-2; P1v pane output.
- Muse orchestrator hand-off: session `2026/09/18/01a0b709-…` first prompt
  09-18 20:22; commits `4863e06`, `7534aed` trailers.
- Per-brief cadence: session `recorded_at` spans and `tool_batch.effect.*`
  counts under `~/.local/share/muse/sessions/2026/09/1[89]`.
- Throughput gate and G6 numbers: ledger rows "PS2 throughput gate" and
  "ps2xGS release numbers (G6)".
- Lane states tonight: `herdr agent list`; `herdr agent read p1v|m14|i5`.

---

# Part 2 — Follow-up read, 09-20 00:10 (after the steering answers)

Frontier direction read at the fixed point the steering answers set
("after each behavior fix"): P1ac was a behavior fix, so this is that
read. Covers 09-19 20:00 → 09-20 00:07. Standing decision unchanged:
upstreaming is off every list until the user has proved the route out
and read the code.

## 10. Outcome since the steering doc

| Since 20:00 | |
|---|---|
| Briefs launched / passed | 20 / 18 (P12, P1ad, M16 running at 00:07) |
| Ladder rungs cleared | 2 (WaitSema(-1) spin → SIF `sregs[1]` poll → current) |
| Current park | main RUNNING in `sub_00394ED0` list-walk (15,989 balanced calls); thread 3 WAIT sema-30; thread 6 WAIT 36 |
| Suite | 431/431/0 (flaky GsSyncV/AFAIL pair fixed in P1y: stale floor since `6046260`) |
| Fork commits | 14 (`8d10619`..`45da174`); shim retired `4326926`; config tracked `5b5ac3d`; drop census `ed387c7` (180 sites, default-on, `PS2X_DROP_SILENCE` kill switch) |
| Orchestrator | 13 prompts, 197 tool batches, 17 references to this doc; launches went event-driven (wait fires → next brief) |

Recommendation status (§7 numbering):

| # | Recommendation | Status |
|---|---|---|
| 1 | Frontier reads at fixed points | Adopted; fixed points recorded in `docs/todo.md` (7f66bb1). This Part is the first such read. |
| 2 | No-silent-drops brief | Done (P1w). Paid off in one brief: 6 census lines made `0x52BE04` attributable to the SIF layer (P1ab). |
| 3 | PCSX2 reference trace | Blocked (P1x): app is x86_64-only, no Rosetta, Release build compiles trace channels out. User deferred to the Mac mini. See §11 — P1x did not consider the bytesize box. |
| 4 | Track CSV, replace shim | Done (P1w, P9). Ladder byte-identical `:600-630` with the split. |
| 5 | Hardware-first with quirks | Kernel side working: P1z disassembled `CreateSema@0x800049b8`, refuted the P1v clamp-1 rule, P1aa applied store-as-is; P10 settled PollSema miss to -1. Quirks side drifted into C++ (see §12 concern 1). |
| 6 | Movie stub | Done, unwired (P7, `e235c4b`), wire when the boot reaches the movie table. |
| 7 | Flaky test | Done (P1y). Root cause was a stale expectation, not a race. |
| 8 | Don't reopen GS decision | Held. G lane quiet. |
| 9 | Bundle ID then park I lane | I6 fixed the identifier; I7 got a first window and stopped at a miniaudio CoreAudio wall. Parked as planned. |
| 10 | Route-comparison criteria | Queued behind first frame; user picked the host synth demo (M15/M16) meanwhile. |

## 11. Concerns

1. **The SIF fix is the CD-shim pattern again.** `6447d8b` writes guest
   `0x52BE04` from inside `sceSifSendCmd`, gated by
   `PS2_REGISTER_GAME_OVERRIDE("ssx3-sif-handshake", "SLUS_207.72", …)`.
   It unblocked the ladder and is well tested, but it hard-codes one
   game's `.bss` word in runtime source. The hardware-faithful shape is
   a *virtual IOP SIF peer*: when the EE sends `SET_SREG` /
   `INIT_CMD` (cid `0x80000001` / `0x80000002`), the peer queues the
   IOP's reply command and delivers it by dispatching the guest's own
   sifcmd system-handler for `SET_SREG` (the handler table lives in the
   guest's `sif_cmd_data`, whose address the HLE learns at
   `sceSifInitCmd`/`SetCmdBuffer`). The write then lands wherever *that
   game* keeps `sregs`, with no address in host code. Thread 3 is
   already at RPC-client waits and one unhandled host RPC
   (`sid=0x80000211`, P27-2c row 3), so the next SIF-shaped park is
   close. **That park gets the generic peer, not a second address
   poke.** Reference implementations: DobieStation `src/core/sif.cpp`
   (on the SSD at `dobiestation-q4`), ps2sdk `iop/system/sifcmd` server
   side, Play! `Iop_SifCmd.cpp`.
2. **Kernel-truth sweeps are crowding out ladder work.** P10 found all
   23 guest consumers of the poll-miss value indifferent to it. P12 is a
   4 h box on the unknown-sema-id code (-408) with no boot-path consumer
   yet. Rule: settle a divergence kernel-first *when the census shows it
   firing on the boot path*; otherwise batch the open ones into a single
   sweep brief after first frame. Kernel truth is still the standard; the
   scheduling is what changes.
3. **`docs/todo.md` Now is a log again.** Each gate read is a 15-line
   paragraph; muse's working memory is that file. Move a read to Done
   the moment its successor brief launches; keep one line per live pane
   in Now.
4. **One host lease, six panes.** P1ad's brief says "M15 holds the lease,
   poll patiently"; every P-lane report carries a waits log. P-lane boots
   are ≤90 s and affect only the throughput columns of the ladder. Split
   into `ssx3-host-lease` (M lane, needs a quiet host) and a P-lane lease
   that P briefs share, marking throughput columns "contended". The mini
   doubles capacity anyway when it arrives.
5. **PCSX2 path, corrected.** The Mac mini is arm64 too, so it inherits
   PCSX2's "Apple Silicon has no EE/VU/IOP recompilers, very slow" warning
   (P1x-5 path 1). The `bytesize` box (ssh over Tailscale, Windows x86_64,
   RTX 4070, WSL2 Ubuntu) can build a native Devel PCSX2 with full
   recompilers and all trace channels today, over ssh, with WSLg or the
   Windows console as the display. P1x did not survey it. This is the
   cheapest path to the reference trace and it needs no user action on
   this laptop.

## 12. Tooling to build (priority order)

| # | Harness | Why now | Brief shape |
|---|---|---|---|
| T1 | **Park snapshot** (`PS2X_DIAG_PARK=1`): on SIGTERM/timeout the runtime writes one JSON + one table: per-thread state (pc, ra chain, wait object), semaphore table with waiter/signaller pc histograms, hot-pc histogram, `[drop]` census, SIF/RPC tally, GS counters | P1ab, P1ac, P1ad each rebuild this by hand from 19k-line logs (P1ab ≈ 2 h). It is the diagnosis brief's whole first hour. | Runtime, 1 brief, lease-free build + 1 proof boot. Then `tools/ladder_diff.py` comparing two snapshots so "ladder-identical" proofs (P9, P11) stop being manual. |
| T2 | **SIF/RPC census table**: every `sceSifLoadModule`/`BindRpc`/`CallRpc`/`SendCmd` with sid, fno, payload size, thread, and claimed/unclaimed by host | The trace lines exist; the table does not. It is the input to the IOP decision (§13) and the next SIF park. | Post-processor over the existing `[IOP/RPC trace]` lines, or a runtime tally in T1. |
| T3 | **IRX inventory** (static, lease-free, ~1 h): extract all 22 `DATA/MODULES/*.IRX` from the ISO (`bsdtar -xf`), table imports (IOP kernel libs), exports, registered RPC sids (`sceSifRegisterRpc` immediates), version strings | Decides HLE-vs-LLE for sound with data. Sample done tonight: `SNDDRV.IRX` 96,016 B = EA's own SND library (`ps2/sndiop.c`), imports only intrman, libsd, loadcore, sifcmd, sifman, sysclib, sysmem, thbase. `MSIFRPC.IRX` 7,377 B; `PADMAN.IRX` 43,813 B; `SDRDRV.IRX` 8,065 B. | Muse, no fork changes, evidence dir `local/research/P13/`. |
| T4 | **PCSX2 Devel on bytesize + first-divergence aligner** between its `EE.Bios` syscall trace and a runtime trace emitted in the same format | The highest-leverage harness from §7 rec 3, still unbuilt. Every park so far was "what would the kernel/IOP have done here"; a reference trace answers that in minutes. | Brief 1: build Devel PCSX2 on bytesize (WSL2 cmake or VS), boot SSX3 to the park's epoch, capture trace. Brief 2: runtime trace channel + `tools/trace_align.py`. |
| T5 | **Analyzer rule: materialized `.text` pointers are function entries**: extend the LUI+ORI/ADDIU fold (`f2149e7`) so any folded constant inside `.text` becomes a split | Would have prevented the `0x3E3AD8` mid-function callback park outright (10 briefs) and closes the class. N64Recomp does this. | Analyzer, 1 brief; prove with `recomp` counts and a ladder-identical boot. |
| T6 | **Build cache check**: clean build is 511 s; the generated `register_functions.cpp` is 398k lines | Every brief rebuilds. Measure incremental time; if >3 min, add ccache and split the generated output into N files for parallel compile. | Measurement first, one brief only if it bites. |

## 13. External codebases not yet used

- **Play!** (jpd002/Play-, BSD-2, not on the SSD; cited once in the
  project, for a GS CSR bit). It is the only mature codebase with the
  same design as this runtime: HLE EE kernel (`PS2OS.cpp`: CreateSema,
  WaitSema, PollSema, thread scheduling, alarms) plus an interpreted IOP
  whose kernel modules are HLE'd (`Iop_Thbase`, `Iop_SifMan`,
  `Iop_SifCmd`, `Iop_LibSd`, `Iop_PadMan`, `Iop_McServ`, `Iop_Cdvdfsv`,
  `Iop_LoadCore`, `Iop_Sysmem`). Use it as the second source in every
  kernel-truth brief (BIOS disassembly stays the first), and as the
  reference for the IOP model below. Clone to the SSD.
- **The IOP decision (branching, not yet due).** EA's SND protocol between
  the EE `Snd::System` and `SNDDRV.IRX` (SIF RPC sid `0x534E44` + cmd
  handler cid 1) is proprietary; HLE-ing sound means reversing both
  sides. Three routes: (a) HLE EA's protocol; (b) Play!'s route: run the
  disc's IRX in an R3000 interpreter with the eight imported kernel libs
  HLE'd (DobieStation's `src/core/iop/` is a clean small interpreter,
  already on the SSD); (c) static-recompile the IRX: the IOP is the PS1
  CPU, and `psxrecomp` (SSD, `q3-siblings/`) already has an R3000
  emitter; IRX are relocatable ELFs so a relocation + import-stub pass is
  needed. **Not needed before first frame**: the unclaimed-sid fallback
  lets `CallRpc` return. Do T3 now so the decision is one brief away when
  a sound-shaped park appears.
- **DobieStation `sif.cpp`** (SSD): the reference for the generic
  EE↔IOP SIF peer in §11 concern 1 — how the IOP answers `INIT_CMD`
  and `SET_SREG`, SIF0/SIF1 register semantics.
- **UnleashedRecomp mid-asm hooks** (SSD, `q3-siblings/UnleashedRecomp`):
  address-specific host code is declared in the game's config TOML, not
  in runtime source. The two SSX3 overrides now in C++ (`Ssx3Movie.cpp`,
  the SIF handshake) fit that model in `games/ssx3/ssx3.toml`, which
  keeps the runtime upstream-shaped and makes the quirks list auditable.
- **N64Recomp** (SSD): treats every address referenced by a `lui/addiu`
  pair or a data pointer as a function entry (T5 above).
- **PPSSPP** (not cited anywhere): HLE kernel that charges cycles per
  syscall (`hleDelayResult`, `hleEatCycles`) and advances guest time
  inside waits. The runtime has no notion of syscall time. The moment a
  park turns out to be a timed busy-wait, that is the template.
- **PCSX2 GS dumps** (`.gs`): PCSX2 can dump the GS packet stream and
  its regression runner replays them. An SSX3 menu/first-frame dump from
  bytesize would give ps2xGS a ground-truth capture before the recomp
  reaches it. Depends on T4.
- `fork-survey/trulio2-iop` carries no IOP changes (HEAD is upstream
  `78ecbae`); nothing to borrow there.

## 14. Branching decisions added

| Decision | When | Recommendation |
|---|---|---|
| Generic SIF peer vs per-address pokes | Next SIF-shaped park (likely P1ad's successor or the `0x80000211` RPC) | Generic peer, dispatched through the guest's handler table. |
| IOP model for sound (HLE protocol / interpret IRX / recompile IRX) | First sound-shaped park after first frame | Run T3 now; lean Play!-route (b) unless T3 shows the SND RPC surface is tiny. |
| PCSX2 reference on bytesize vs Mac mini | Now (user call: bytesize needs nothing on this laptop) | bytesize; the mini is arm64 and slow for PCSX2. |
| Kernel-truth sweep scheduling | Now | Census-gated; batch the rest post first frame. |
| Lease split P/M | Now | Split; low risk. |

## 15. Evidence for Part 2

- ssx3 commits `1b1cc7e..5ebce5f` (44); steering answers `7f66bb1`
  (`docs/todo.md`); user decisions `2c09937` (P1x → mini), `99857d8`.
- Fork `git log origin/main..HEAD` (SSD clone, branch `ssx3`);
  `git show 6447d8b` (SIF handshake), `ed387c7` (census), `4326926`
  (shim retired), `f26f273` (kernel-true sema).
- REPORT Parts 23–27 (`local/research/P1/REPORT.md:7536-9120`);
  `local/research/P1x/REPORT.md` §P1x-5 (paths ranked, no bytesize row);
  `local/research/P8/REPORT.md` rows 65–66, 86, 121–122 (IRX list,
  sid `0x534E44`, unclaimed fallback).
- IRX facts: `bsdtar -tvf "SSX 3 (USA).iso" | grep IRX` (22 modules under
  `DATA/MODULES`); extracted SNDDRV/MSIFRPC/PADMAN/SDRDRV and read import
  library names with `strings`.
- Orchestrator session `2026/09/18/01a0b709-…`: 7,847 records since 20:00,
  13 `runtime.user_intent.accepted`, 197 `tool_batch.effect.started`.
- Pane states at 00:07: `herdr agent list` (p12, p1ad, m16 working; p1ac,
  i7 done; wN:p3 orchestrator idle).
