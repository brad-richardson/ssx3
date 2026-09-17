# Deep dive: recomp architecture and performance — September 17, 2026

Second read-only pass of the day, independent of
[the morning architecture review](review-2026-09-17-architecture.md) and
deliberately aimed one layer lower: the static-recompiler output and the
runtime it runs inside, rather than the diagnostics layered on top. Sources
read: `third_party/ModernGekko/vendor/dolphin/DolRecomp/src/{backend,cpu}`,
`GXRuntime/include/core/{cpu,types}.h`,
`Source/Core/Core/PowerPC/StaticRecomp/*`, `Source/Core/Core/CoreTiming.cpp`,
`Source/Core/VideoCommon/{Fifo,VertexLoaderBase}.cpp`, the generated chunks
under `local/research/{mask-sample,startgate}/`, the Odin M7 profile
(`/tmp/android-m7/m7c/m7c-rep-all.txt`), the desktop cost table
(`local/research/120hz/spike-render-breakdown/report.md`), the live session's
own narrative, and the current `docs/todo.md` / research set.

Nothing was edited or run except this file and one hermetic test pass
(`PYTHONDONTWRITEBYTECODE=1 pytest -p no:cacheprovider`: **717 passed, 241
subtests**, 20 s, no bytecode or cache written). The pace agent's then-uncommitted
throttle work was read but not touched; it landed as `1f1bc2d` mid-write and
§1 is updated for it.

Ordered by how much each one changes a decision.

---

## Headline

Three things, in order:

1. **The throttle overflow (`1f1bc2d`, landed while this was being written)
   voids more than the ceiling.** At least nine recorded verdicts — including
   "fast-FP buys 0.00", "SyncGPU costs nothing", "pinning costs nothing",
   "EGL == Vulkan" — were measured *at* the phantom wall and are null results
   with no content. §1 is the sweep list. The first real number is already in,
   and it is not the good news a lifted ceiling implied: **the Odin runs a real
   race at 0.83× mean / 0.63× low**, i.e. ~50 fps with ~38 fps lows.
2. **The biggest untouched performance lever is the generated C itself.** Every
   guest instruction is an entry point of its host function, which structurally
   forbids register allocation across guest instructions; 77–83 % of those entry
   points are unreachable in practice. Guest function bodies are 45–57 % of
   cycles and nobody has looked inside them. §2. With the real Odin race number
   at 0.83×, avg-75 needs ~1.5× on the mean and ~2× on the lows; that is not
   reachable by helper-level work, so this moves onto the critical path.
3. **Every A/B in the record is measured in a configuration the product will
   never ship.** Movie playback forces Dolphin's deterministic GPU thread, which
   double-decodes every FIFO byte; that is also the sole reason the FIFO panic
   existed. §4.

---

## 1. The throttle overflow voids a specific list of verdicts, not just the ceiling

**Status: found, fixed and committed as `1f1bc2d`; the sweep is not done.**

The arithmetic, confirmed against the source: `UpdateSpeedLimit` computed
`std::lround(GetTicksPerSecond() * new_speed)` into a `u32`
(`CoreTiming.cpp:497`, member at `CoreTiming.h:216`). GameCube ticks/s is
486,000,000; at `EmulationSpeed = 10` that is 4.86e9, which wraps to
4.86e9 − 2^32 = **565,032,704**, and 565,032,704 / 486,000,000 = **1.16262**.
Exact, to every digit of the observed wall. At speed 9 the same wrap gives
0.16262, which matches the agent's reported 0.15 probe.

What that means for the record — every one of these was measured with the
throttle, not the machine, as the limiter, and is therefore **uninformative**,
not negative:

| Recorded verdict | Where | Real status |
| --- | --- | --- |
| "1.16 ceiling is STRUCTURAL, backend/SyncGPU/placement-independent" | `todo.md` Pace mechanism | **Resolved** — it was the throttle; real Odin race ceiling 0.83×/0.73× |
| "fast-FP A/B prints identical ceilings; the wall-clock prize for all that FP work is 0.00" | M7 note, `todo.md` | Void — never measured off the wall |
| "Fast-fp: STOP, no rebuild" (descope decision) | 09-17 08:13 | Built on the void number; re-open |
| "Every further CPU optimization is expected ~0% until the pace mechanism is found" | M7/phase-1.5 | Void, and it was steering the whole backlog |
| "Determinism-mode off: 0.0% on speed" | phase-1.5 sync probes | Void (see §4 — this one is likely a real win) |
| "Core pinning: 0.0%" → affinity deferred | `todo.md` Hot-thread affinity | Void |
| "EGL 1.1626 vs Vulkan 1.1627 to 4 decimals" → backends equivalent | M7 | Void; no backend comparison has happened yet |
| "EFB 2x is still full speed" | snow agent bonus | Void |
| "Desktop Metal uncapped binds at menu ~1.17, 69.5 fps rock-steady, validation on/off identical" | ceiling probe run-003 | Void, including the validation sub-verdict |
| psq `always_inline` landed, both leaves gone from profile, no wall-clock change | M7 | Profile change real; wall-clock null is void |

### The first post-fix number changes the milestone arithmetic

`1f1bc2d` reports the true Odin race ceiling on the `m3-menu` movie, screenshot-
verified as actually racing: **OGL 0.83× mean / 0.63× low; Vulkan 0.73× mean /
0.64× low**, zero FIFO panics on either backend. Three consequences:

- **The Odin does not hold 60 fps in a race.** 0.83× is ~50 fps with ~38 fps
  lows. avg-75 needs a sustained 1.25×, so the gap is **~1.5× on the mean and
  ~2× on the lows** — not the "a few percent short" picture the 1.16 wall
  implied. Helper-level work cannot close that; §2 and §3 can plausibly be asked
  to.
- **Vulkan is currently *behind* OGL on race pace** (0.73 vs 0.83). That is the
  first genuine backend comparison — the same commit notes the movie config
  layer overrode `--graphics`, so every prior backend A/B was OGL on both arms.
  The upstream-alignment argument for Vulkan stands; the performance argument
  now points the other way and should be re-measured before any switch.
- **This contradicts M5's "full speed in-race, 0.97–1.0 capped."** Both cannot
  describe the same content. Candidate explanations, all testable: different
  window (M5's 16 s at GO! vs a full race), different vehicle (M5's movie vs
  `m3-menu`), or the DVFS point — pre-fix runs slept 56 % of wall inside the
  throttle, and a handheld governor behaves differently when the core never
  idles, so an *uncapped* ceiling can read lower than the *capped* headroom it
  is supposed to explain. Until that is reconciled neither number should be
  quoted as "the Odin's speed". The cheap resolution is one capped run over the
  same `m3-menu` race window reporting CPU busy-fraction, the metric that
  survives both regimes.

Two process fixes worth making at the same time:

- **`SSX3_EMULATION_SPEED` cannot express "uncapped".** `native_gamecube.py:52`
  rejects `speed <= 0`, but `EmulationSpeed = 0` is exactly Dolphin's unlimited
  mode: `IsSpeedUnlimited()` returns true when `m_throttle_adj_clock_per_sec == 0`
  (`CoreTiming.cpp:397`) and `Throttle()` then short-circuits before any
  arithmetic (`CoreTiming.cpp:458`). Using `0` instead of `10` would have
  sidestepped the entire phantom-ceiling investigation. Allow `0`; the Odin
  harness (`/tmp/android-m7/m7run.sh:28`) hardcodes `EmulationSpeed = 10.0` and
  needs the same change.
- **Under a cap, "speed" is the wrong metric and produces fake nulls.** A capped
  run saturates at 1.00 no matter how much headroom a change buys; the win shows
  up only as idle. The Odin idle A/B is the proof that the right metric was
  available all along: *ON: 1.00 at 56 % CPU; OFF: 0.62–0.93 at 84 % CPU* — the
  CPU column carries the information, the speed column hides it. Recommend that
  every capped run reports **host CPU-ms per guest frame** (or busy fraction) as
  the primary number and speed only as a pass/fail. This also dissolves the
  long-standing idle-skip contradiction across three platforms: −30 % on the Mac
  in September, ≈0 % on desktop at O2, +27 % on Odin. Those are consistent once
  you separate "speed" (saturating) from "work done per guest frame".

One robustness note on the fix itself: `new_ticks = ticks * new_clock_per_sec /
m_throttle_adj_clock_per_sec` now multiplies two s64s. `ticks` is bounded to
roughly one second of cycles by the whole-second push in `Throttle()`, so
4.86e8 × 4.86e9 ≈ 2.4e18 stays inside s64 — but it is within 4× of the limit,
and the first call before any `Throttle()` has no such bound. Dividing before
multiplying, or using `__int128`, costs nothing.

---

## 2. Every guest instruction is an entry point, which forbids register allocation

**This is the largest untouched lever in the project, and it is invisible in
every profile taken so far.**

`emit_function` writes the per-function entry dispatcher as a switch over
*every instruction in the function*:

```c
// DolRecomp/src/backend/emitter.c:1924
fprintf(out, "    switch (ctx->pc) {\n");
for (u32 i = 0; i < count; i++)
    fprintf(out, "    case 0x%08Xu: goto label_%08X;\n",
            insts[i].address, insts[i].address);
```

The CFG builder right next door already computes basic-block leaders
(`c_cfg.c:277–292`) and the *return* dispatcher does use a pruned set
(`cfg.return_targets`, `emitter.c:1959–1965`). The entry switch does not.

Measured on three real chunks from `local/research/`:

| chunk | guest instructions | entry cases today | actual leaders | prunable |
| --- | ---: | ---: | ---: | ---: |
| `chunk_0167_text1_8029D7A0` | 4,088 | 4,088 | 706 | **82.7 %** |
| `chunk_0145_text1_802457A0` | 4,089 | 4,089 | 785 | **80.8 %** |
| `chunk_0064_text1_801017A0` | 4,096 | 4,096 | 963 | **76.5 %** |

Why it matters: a label that is a switch target has an edge from the function
entry, so no value computed before it is live across it. With *every*
instruction a switch target, LLVM cannot keep a guest register in a host
register between two guest instructions — each `ctx->gpr[n]` read is a real
load and each write a real store, forever. Average leader-to-leader run in
these chunks is ~5.8 instructions, so pruning creates ~6-instruction windows
where forwarding, redundant-load elimination and register allocation become
possible for the first time.

The same file also stores the guest PC at **3,876 of 4,088 instructions** (95 %).
`materialize_pc` is only cleared inside recognised counted loops
(`c_cfg.c:305–312`); everywhere else it is unconditionally 1
(`c_cfg.c:272`). PC is observable only at dispatcher boundaries, external
hook calls and exceptions — all of which the generator can identify.

Evidence that this is the regime, not a theory:

- **`-O0 → -O2 + ThinLTO` gave 2.5–3.5×, "the −O0 tax was almost entirely call
  overhead, and −O2 *deleted* it rather than shrinking it"** (Odin phase 1).
  Code whose cost is structural rather than arithmetic behaves exactly like
  that.
- **Guest function bodies are 45 % → 57 % of cycles** after the FP wave (M7).
  Every named helper together is now a minority of the profile. The remaining
  cost is inside `func_*` bodies, which is precisely where the CPUState traffic
  lives — and where no instrument currently looks.
- **The fcmp NO-SHIP result is the signature of a layout/I-cache-bound regime,
  not a compute-bound one.** Removing a call with an identical body cost 7.3 %
  wall throughput, ABA-confirmed, from +347 KB in an 82 MB image. In code that
  is already memory-bound on `ctx->gpr[]`, extra text is pure loss. That result
  should be read as *evidence for §2*, not as a mystery to retry with a layout
  strategy.
- **Per-op microbenchmarks keep failing to reproduce at game level** (psq −30 %
  per call, game-level flat in noise; conversion split 2.79 % → 0 % module-wide,
  no wall change). That is what happens when the helper is a small slice of a
  memory-bound host loop.

Suggested experiment, cheap and bounded, using instruments that already exist:

1. Regenerate **one** hot chunk (`8022D7A0` or `802197A0`, the two heaviest in
   M7) with the entry case list restricted to `leaders ∪ return_targets ∪
   {any address materialised before a `return`}`, and `materialize_pc` cleared
   for instructions that cannot reach a hook.
2. Diff the generated C for label reachability, then A/B with
   `tools/gamecube_movie_ab.py` (trajectory-gated, resolves ≥3–4 % today) plus
   the chunk signposts, which were built for exactly this.
3. If it holds, the correctness question to settle before a full rollout is the
   complete list of addresses the dispatcher can enter at: function starts,
   `m_return_hooks`, loop heads stored on downcount expiry
   (`emitter.c:371`, `:392`), and exception-vector targets. All four are
   enumerable in the generator.

Expected size: guest bodies are ~50 % of cycles and this attacks their dominant
overhead. Even a 1.3× on that half is ~1.15× overall — comparable to the entire
FP wave, on both platforms, from a generator change.

---

## 3. Guest memory access has no fast path

`get_ram_ptr` (`GXRuntime/include/core/cpu.h:169`) is a software translation on
every access:

```c
u32 masked_addr = addr & ~0x40000000u;
if (cpu->exram) { ... }           // loaded and tested even on GameCube
u32 offset = masked_addr - 0x80000000u;
if (offset <= cpu->ram_size - size) return cpu->ram + offset;   // two loads
return NULL;
```

and every **store** additionally pays `clear_matching_reservation` (`cpu.h:190`,
a load of `reserve_valid` plus compares) and a global function-pointer test
`if (g_mem_write_journal && ...)` (`cpu.h:236`, `:253`, `:268`) — a diagnostic
hook that SSX 3 never installs but that every guest store branches on.

Ranked by cost-to-implement:

| # | Change | Why it is safe/cheap | Expected |
| --- | --- | --- | --- |
| 1 | `#if`-out `g_mem_write_journal` when not built for journaling | Nothing in the ship path sets it | A load+branch per guest store |
| 2 | Compile-time constants for GameCube: no EXRAM branch, constant `ram_size` and base pointer | GC has no MEM2; `cpu->ram` never moves after `Run()` entry | 3 loads → 0, bound check folds to one `cmp` with an immediate |
| 3 | Inline gather-pipe fast path in `mem_write*` | Dolphin's JITs do exactly this (`optimizeGatherPipe`); the runtime already has the page test, just on the far side of the call | see below |
| 4 | `__attribute__((preserve_most))` on the external hooks | Cold slow-path calls currently clobber caller-saved registers on the hot path | Reduces spill pressure around every memory access |
| 5 | Fastmem (mmap guest space at a fixed base, `PROT_NONE` elsewhere, SIGSEGV → MMIO) | The standard technique; large but structural | Removes items 1–4 entirely |

On #3, the numbers are already on disk. In the M7 Odin profile,
`HookExternalWrite` is **1.69 %** and `GPFifo::GPFifoManager::Write32` is
**1.16 %** of all cycles — ~2.9 % before counting the caller-side indirect-call
overhead that is attributed to the `func_*` bodies. The fast path exists but is
*inside* the hook (`StaticRecompCore_Hooks.cpp:74`), so every gather-pipe word
still pays: `get_ram_ptr` miss → indirect call across the module boundary →
`TranslateRelAddress` (a linear scan of `m_active_rel_sections`,
`StaticRecompCore_SMC.cpp:137`) → zero-address check → lockstep-journal test →
`GetGPFifo()` → `Write32`. Hoisting the `(ea & 0xFFFFF000) == 0xCC008000` test
into `cpu.h` with a direct pointer bump, calling out only at the 32-byte burst,
collapses that to a handful of instructions.

Also visible in M7 and trivially fixable: **`convert_to_double` at 0.66 % is
out-of-line**. It is `static inline` in `types.h:107` and is being outlined
anyway — the same failure mode the morning review identified for the psq
helpers. `always_inline` it.

---

## 4. Every A/B is measured in a configuration the product will not ship

Movie playback sets `Core::WantsDeterminism()`, which calls
`FifoManager::UpdateWantDeterminism` (`Fifo.cpp:497`); with the default
`GPUDeterminismMode::Auto` and dual core, that turns on
`m_use_deterministic_gpu_thread`. In that mode every FIFO byte is decoded
**twice** — preprocess on the CPU thread, real execution on the video thread —
with slot-boundary waits between them.

The M7 profile shows it plainly on the CPU thread:
`OpcodeDecoder::RunFifo<true>` 0.54 %, `Fifo::FifoManager::RunGpuOnCpu` 0.59 %,
alongside a separate video thread running the real decode. This is the morning
review's finding 3b; the answer given ("trial inis run the default
`SyncGPU=false`") is correct about the *ini* and wrong about the *effect* —
`SyncGPU` is not the switch, determinism is. Three consequences:

- **The FIFO panic was an artefact of the measurement harness, not a product
  defect.** The fix (`309f639`) is gated on `UseDeterministicGPUThread()`, so in
  a normal ride it is a no-op — which means the panic could never have happened
  in a normal ride either. Worth stating plainly in the record: it unblocked
  *measurement*, it did not fix a shipping stability bug.
- **"Determinism-mode off: 0.0 %" is one of the §1 casualties** and is now the
  most promising re-test on the list: it is the one knob known to add real
  CPU-thread work to every movie run.
- **Movie A/B is the only trustworthy comparison instrument and it is
  systematically pessimistic.** Any budget verdict derived from a movie run
  (which is most of them) carries a determinism tax the product will not pay.

Three more configuration divergences in the same family:

- **Vertex loader.** `IsRuntimeCodeGenerationDisabled()` forces the *software*
  loader on iOS unconditionally and on desktop whenever
  `SSX3_NO_EXECUTABLE_MEMORY=1` — which `native_gamecube.py:404` sets by default
  (`VertexLoaderBase.cpp:241`, `moderngekko-platform.patch:178`). Android sets
  neither: `tools/android_trial.py` passes no such variable, so **Odin runs use
  the ARM64 vertex-loader JIT while iOS and desktop runs use the portable
  loader**. Every iOS↔Android render-cost comparison in the record crosses that
  line. Two actions: record the loader in every receipt, and — since the game's
  `(VtxDesc, VAT)` set is small and fixed — consider **AOT-specialised vertex
  loaders** compiled into the binary, which is the same philosophy as the rest
  of the port and sidesteps W^X entirely. Sizing first: the desktop cost table
  puts "ph1 host (FIFO + vertex + encode)" at 1.56 ms of 15.76 and calls it flat
  against draw count, so this is a ~1 ms lever, not a 3 ms one.
- **Metal validation.** The desktop cost table that drives the whole 120 Hz
  budget was taken "single-core, Metal + validation"
  (`spike-render-breakdown/report.md`). The Metal debug layer inflates exactly
  the host-side rows that table ranks first. The one A/B that cleared it
  ("validation on/off identical") is a §1 casualty. `native_gamecube.py:456`
  records `MTL_DEBUG_LAYER` but never sets it — so it is inherited from whatever
  shell launched the run, which is the worst of both worlds. Pin it off for
  measurement runs and assert it in the receipt.
- **Always-on perturbation.** `run` defaults `STATICRECOMP_DISPATCH_SAMPLES=1`
  and, for GUI runs, `SSX3_SCREENSHOTS=1` (`native_gamecube.py:406–418`). The
  morning review flagged screenshot cadence on Android; the desktop default has
  the same shape, and both are inside the windows being measured.

**Stale data point still in circulation:** the cost table above (4.73 ms
update-pair host, 2.74 ms ph2 wait, 11.05 ms quiet pair+render) predates the
fast-FP/conversion/psq wave by a day, yet it is still the arithmetic behind
"needs 1.3–1.9×" in `todo.md`. The FP wave removed named helpers from the
update-pair host bucket specifically. That table needs one re-run before it is
quoted again — it is cheap, the player and script (`rebuild_player.py`) are
preserved.

---

## 5. An interpolated frame costs a whole frame, and that is a choice

The smoothing path injects an extra draw by re-entering the **guest's** render
callback from the idle point:

```c
// native_render_schedule.h:251
c.gpr[3]=app; c.pc=0x8010a4c8;
NativeProbe::Step(c); render.repeated=true; ...
```

and the interleave path does the same (`native_callback_trace.h:578–581`). So an
extra frame re-runs scene-graph traversal, per-object matrix concat, GX state
setup and the full FIFO emission — on top of a full host render. From the
desktop cost table, a render is ph0+ph1+ph2 ≈ **8.0 ms of the 11.05 ms quiet
pair+render**, of which **3.6 ms is guest code** that an interpolated frame does
not conceptually need to re-run: it wants the same draw stream with different
XF matrices, which is exactly what the interpolation layer already patches on
the way out (`native_pose_interpolation.h:WriteXF`).

The cheaper architecture is already half-built and parked:
`native/diagnostics/native_frame_replay.h` records a FIFO frame and audits it.
But its acceptance bar is *"prove exact-image fidelity in an isolated renderer"*
plus owned-memory and ordering gates — a bar appropriate for a replay feature,
and far above what an interpolated extra frame needs. Recommend re-scoping the
replay track to a single question: **can a recorded frame be re-issued with
patched XF matrices and a new XFB, cheaply and without guest-visible side
effects?** If yes, an extra frame's cost drops toward the host decode + draw
submission, and 120 Hz stops being a 2× CPU problem. If no, that is an equally
valuable answer and it should be the reason the current path is the path.

Two related observations on the same budget:

- **The guest syncs the GPU every frame with an empty queue** — `queue_before=0`
  in all 1,360 renders, a ~3.3 ms floor plus a scene-scaling part, measured as
  CPU-busy spin (2.74 ms, 34 % of render CPU). That is a hard guest↔GPU
  serialisation, and the spike already names the fix (defer completion to the
  next submission point). It has never been scheduled, and it is the single
  largest named item in the render half.
- **Product shape.** Each half holds alone on the phone at kitchen-sink
  settings (F: 1,479 doubled at speed 1.00; smoothing: 35 s, 1,097 extras,
  ~91 displays/s, every extra reaching glass); together they do not fit. The
  record has drifted toward "Combined or bust". The evidence supports a
  different default: **60 Hz sim + interpolated presentation** ships the visible
  win today, and F becomes a separate physics-fidelity option rather than a
  prerequisite. Worth deciding explicitly rather than by budget attrition —
  especially given the Sept-16 finding 4 hazard (state-transition ticks under F
  run once at half dt, concentrated at landings and crashes).

---

## 6. Second-tier items with numbers already attached

- **`FastDiscSpeed` is off everywhere by default** yet measured **26 % off
  startup** in a six-run paired A/B (`loading-speed-spike.md`). On iOS it is a
  menu toggle defaulting to `NO` (`App.mm:344`); desktop never sets it. The
  interesting untested case is not startup but **in-race streaming**: the Odin's
  course-load dip to ~0.8 and the onscreen run's load dips to ~22 fps are
  exactly the "lows" the avg-75 milestone is judged on. One ini line, already
  plumbed.
- **Texture cache is in Safe mode**, so `Common::GetHash64_ARMv8_CRC32` runs at
  0.58 % re-hashing textures every frame (M7). Small, but it is a config knob
  with a known accuracy/speed trade and it has never been A/B'd.
- **`__aarch64_cas1_acq_rel` at 1.52 % on the video thread** (M7), plus the
  3.2 % kernel futex share noted earlier, is unexplained atomic/lock traffic on
  the second-busiest thread. Nobody has looked.
- **`TextureCacheBase::CopyRenderTargetToTexture` 1.18 %** on the video thread —
  EFB copies, untouched by the "EFB access closed as a lever" verdict (that was
  about *CPU* EFB access, a different thing).
- **Layout/PGO.** 566 MB of module text with no ordering strategy, and a
  demonstrated 7.3 % swing from a 347 KB perturbation. The ingredients for an
  order file already exist: `tools/gamecube_line_tables.py` plus the 63 chunk
  signposts. This is the right answer to the parked "layout lottery" item — not
  a blind retry of the fcmp inline.

---

## 7. Where the record itself is fragile

Two of the largest errors of the last three days — the stale M5 profile and the
phantom 1.16 ceiling — propagated the same way: a number was written into
`docs/todo.md` prose, superseded elsewhere, and kept being cited. The todo is
now 82 KB with withdrawn verdicts annotated in place, and the research set is
117k words across 30 documents. Finding the *current* value of any given number
requires reading several documents and knowing which paragraph won.

Suggestions, in order of cost:

1. **One current-numbers ledger.** A single table — metric, value, date, device,
   module sha, config (backend / cap / determinism / vertex loader / validation
   / idle), how measured, status (live | superseded | void) — that every document
   cites instead of restating. Most of the §1 sweep would have been mechanical
   against such a table, and the M5 staleness would have been caught by the
   module-sha column.
2. **Verdict-grade runs get an exclusive host.** The idle A/B was contaminated
   by a sibling agent's emulator runs and had to be discarded as an A/B; the
   same week produced an ENOSPC-killed calibration, exFAT zeroing 8 clusters of
   a trial binary, and a 10 M-token disclaim loop from an agent holding a hung
   device shell. Parallel agents are now a leading source of bad data, not just
   of throughput. A lease (host or device) plus a "no siblings during verdict
   runs" rule is cheaper than re-running.
3. **Draw the research/product boundary.** The trial system ships in the app
   under `SSX_NATIVE_TRIAL_APP`: ~2.8k lines of file-scope statics across four
   namespaces, keyed on ~20 hard-coded GXBE69 guest addresses, with the state
   machine's ordering invariant expressed as comments at three call sites
   (Sept-16 finding 2, still open). It is now the largest body of native code in
   the repo and there is no stated plan for what part of it becomes product.
4. **Goal drift is real and worth naming.** The README's objective is standalone
   Tricky courses with SSX 3 handling; `todo.md` itself says "September 14
   priority: course restoration is the main track; keep 120 Hz research
   bounded." The last five days were ~95 % perf/120 Hz/Android. That was
   user-directed and produced genuine wins — but the course-side backlog has not
   moved: Aloha faults after standings as slopestyle, slopestyle needs
   engine-side reach plus `behiloc.dbb` medal targets, Garibaldi still lacks
   fog/backdrop, sprite/animation cycling and a validated finish. Those are the
   items that decide whether this becomes a playable thing.

---

## 8. Smaller notes and corrections

- **Credit where due:** the FIFO fix removed the dead
  `CompileExceptionCheck(FIFOWrite)` on the recomp path in the same commit
  (~0.5 %), which closes the morning review's finding 3 second half.
- **"Endian helpers 12.1 → 0.00" should read "inlined, now unattributable."**
  The cost did not leave; it moved into the `func_*` bodies, which grew 28 % →
  45 % in the same transition. The current framing invites the reading that
  memory access is solved. §2 and §3 are the same cost, seen from inside.
- **The signpost update-side blind spot** (morning finding 10) compounds §2:
  same-chunk callees compile to `goto`, so the only instrument that can see
  inside a chunk is the PC histogram, and it samples at dispatch boundaries.
  A chunk-internal cost like "one load and one store per guest register access"
  is currently unobservable by construction. If §2 is pursued, the A/B harness
  (movie + wall throughput) is the measurement, not the profiler.
- **`m_throttle_adj_clock_per_sec` as a divisor** is now `s64` and can still be
  0 under the unlimited path; `Throttle()` short-circuits first, so it is safe,
  but the `UpdateSpeedLimit` `was_limited` guard is what protects the transition
  — worth a line in the record so a later refactor does not drop it.
- **Alpha period** (`native_pose_interpolation.h:167` uses
  `TicksPerSecond/59.94` while `Deadline` uses `/120`) is still open and now
  has two review mentions; it is an XS item that keeps getting re-discovered.

---

## Suggested order

1. **Finish the §1 sweep** now that the race ceiling is measured: fast-FP
   on/off, determinism on/off, core pinning, EFB 1×/2×, and the capped-versus-
   uncapped reconciliation above. Use `EmulationSpeed = 0`, and report CPU-ms
   per guest frame rather than speed. A few hours; it re-scores the backlog, and
   the fast-FP arm in particular is a descoped decision that the 0.83× number
   may reverse.
2. **Re-run the desktop cost table** on a HEAD module with validation pinned off
   (§4). Everything downstream of "needs 1.3–1.9×" depends on it.
3. **One-chunk codegen experiment** (§2), A/B'd with the movie harness. Highest
   expected value of anything on the board; bounded; no device needed.
4. **Cheap memory-access wins** (§3 items 1–3), measured the same way.
5. **Re-scope the replay track** to the interpolated-frame question (§5) before
   any more budget arithmetic on the current extra-frame cost.
6. **Ledger + exclusive-host rule** (§7 1–2) — these pay for themselves the next
   time a number is questioned.

## What I did not check

The iOS app shell and `SessionMenu`, the course conversion tooling
(`gamecube_*` importers) beyond their docs, the texture-remaster pipeline, the
Aloha/Garibaldi content backlog beyond reading the conversion notes, the Vulkan
and Android display patches beyond their CMake hunks. The pace agent's run set
is read only through `1f1bc2d`'s message and its `/tmp/pace/logs` speeds
(post-fix desktop 1.5–1.8× on a race-ish window, ~3.5× in menus); its own
report is the authority on those.
