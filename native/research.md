# GXBE69 research notebook

All addresses refer to revision 0, DOL SHA-256
`b92162d6c616be3ce46b4eb61d5ddbb49891bc387ea7ddb2fea5792842fa29ce`.
Date: 2026-09-10. These are static observations, awaiting runtime validation.

| Lead | Evidence | Next check |
| --- | --- | --- |
| Entry `0x80003154`, `main` `0x801CA8A0` | DTK startup/SDK recognition; direct branch-and-link at `0x800032A8` targets main | Confirm both execute in native boot trace |
| World path construction near `0x800E81FC` | Address construction for `data/worlds/` at `0x802DD498`; disassembly shows surrounding string calls, then `0x800E8264` calls `0x8024C0FC` with the constructed path in r3 | Capture arguments and return value around this candidate loader call |
| GDB loading at `0x8024C0FC` | Builds a name using `.gdb`, checks loaded bytes for `00 37`, and sets a table pointer to buffer + 80; these match the extracted GDB header and first table offset | Record input path, returned buffer, selected location records, and subsequent GSB requests |
| World cache near `0x8024C4B0` | Address construction for `cWorldCache` at `0x802F9064` | Establish object constructor and file/stream relationships |
| World block allocation near `0x8024B2AC` / `0x8024B2D8` | References to block-array and memory-block labels | Follow allocation size, owner, and GDB/GSB group lifetime |
| World triggers near `0x8013A478` / `0x8013AF04` | References to instance-array and manager labels | Find event setup/cleanup and reset behavior |
| World painter near `0x801659E8` | Reference to painter manager label | Separate material/scenery setup from collision and physics |
| Restart strings at `0x802D6A80`, `0x802D6ADC` | Pointers in menu/localization data at `0x802D6B5C`, `0x802D6B70` | Trace action dispatch from an actual restart, not from string presence alone |

The static pass found 40 relevant string anchors. Its conservative constant
tracking discards assumptions at calls, branches, and unmodeled instructions.
It deliberately misses some references. Data-pointer matches may also be
ordinary integers; nearby code addresses are not established function entries.

The GDB routine has stronger evidence than a string match alone. Startup at
`0x80003334`/`0x80003338` establishes r13 as `0x803DFA60`; its r13-relative
operand at offset -24280 points to `.gdb` at `0x803D9B88`. Its header checks and
buffer + 80 pointer setup independently match the parsed archive. This identifies
a useful loader boundary statically, while its calling contract and ownership
still need runtime observation.

## Code-modification triage

The pinned compiler also reports 115 warning ranges, containing 140 flagged
instruction words: 4 `icbi`, 28 `stw`, 36 `sth`, and 72 `stb`. DTK's named,
nonzero-size symbol ranges place the four `icbi` sites in `__flush_cache`,
`OSExceptionInit` (two sites), and `ICInvalidateRange`.

The store warnings still need runtime validation. Inspection found that the
generator's linear known-register analysis does not reset its state at all
control-flow boundaries. For example, a `lis` in the preceding routine can
remain assumed across `blr` when analyzing the `sth` at `0x8029122C`, whose
actual address comes from an argument register. This is a concrete source of
false positives; it does not prove all store warnings harmless. Keep runtime
chunk hash verification enabled and prioritize actual mismatches/fallback sites.

## Scope of the first hooks

Identify stock course selection, resource loading, spawn, reset, and event
teardown before changing them. Keep the original rider physics, collisions,
tricks, and game clock running. The standalone course adapter should initially
replace the event/resource inputs, with assertions and a reversible stock path.
The GC terrain payload is 430 bytes rather than the PS2 writer's 432 bytes;
asset conversion must use the already-verified GC layouts rather than reuse
PS2 offsets unmodified.

## First runtime observations

The native stock Snow Jam test reached a running race, accepted test inputs,
opened the pause menu, and returned to the starting briefing through Restart.
Its roughly five-minute process lifetime includes startup hashing, menus,
loading, gameplay, and pause; it is not five minutes of continuous riding.
All four runs used interpreter CPU fallback, reported zero JIT fallback entries,
and had zero failed chunk hash checks. See `validation.json` for counters,
precise limitations, and the short gameplay performance window.

The last run's interpreter samples concentrate at `0x00000C00`–`0x00000C18`,
the low-memory PowerPC system-call vector. This is a more useful next profiling
target than treating the 115 static SMC warnings as confirmed defects. Identify
the copied vector's source and its callers, then compare state/timing before
replacing or translating that path. The September 11 mobile work adds a portable
vertex loader and an executable-allocation guard. Guarded Mac gameplay passes;
physical iPhone execution and performance remain separate acceptance checks.

The 15-minute iOS simulator soak (`mobile-validation.json`, `ios_simulator`)
shows the same concentration: about 43,000 sampled interpreter instructions at
`0x00000C00`–`0x00000C18` versus roughly 200 each across `0x00000518`–`0x0000058C`,
the external-interrupt vector. Both vectors sit below the DOL's text sections,
so the translator never emitted native code for them; every system call and
interrupt entry runs interpreted. Translating or hooking the copied vector
bodies is the first measured optimization candidate once phone timings exist.

## Interpreted exception vectors (2026-09-13)

The Mac run receipt `local/reports/native-runs/20260913-131431.json` (190 s of
Garibaldi) gives the shape of the remaining interpreter work. 94% of sampled
interpreted instructions are the seven words at `0x00000C00`–`0x00000C18`,
the system-call vector; the external-interrupt vector at `0x500` is under 5%.
Native-raised exceptions run at about 27,000 per second (roughly 450 per
frame) and interpreted instructions at about 262,000 per second.

The executable contains three `sc` instructions: at the end of `DCFlushRange`
(`0x80284DF8`), at the end of the unnamed `DCStoreRange` (`0x80284E28`), and a
two-instruction `sc; blr` helper at `0x8028342C`. The vector body is the SDK's
`__OSSystemCallVector` (`0x80288824`, copied to `0xC00` by `__OSInitSystemCall`):
it toggles HID0 bit 0x8 around a `sync` and returns with `rfi`. On a host with
no data-cache emulation (`AccurateCPUCache` is off) the vector has no effect
beyond the return. Every `sc` therefore costs a burst exit, a state sync into
Dolphin's interpreter, seven interpreted steps and a sync back.

The same receipt's dispatch samples show the surrounding cost is larger than
the vector itself: `DCStoreRangeNoSync+20`, `DCFlushRange+20`,
`DCInvalidateRange+20` and `DCFlushRangeNoSync+20` account for 38% of sampled
native dispatches, one dispatch per cache line, each delegating `dcbf`/`dcbst`/
`dcbi` to the runtime cache hook (about 1.04 million hook calls per second).
`SelectThread+0x14C`, the OS idle spin `while (run queue == 0)`, is another
39% of dispatch samples; `StaticRecompIdlePC` is unset in every profile, so
idle-loop skipping is off.

Fix options, cheapest first:

1. Set `StaticRecompIdlePC = 0x80288ED4` in the profile's `[Core]` settings so
   the runtime calls `CoreTiming::Idle()` at the spin instead of executing it.
   Battery and thermal headroom on the phone, no semantic change.
2. High-level-emulate the `DC*Range` family (`DCFlushRange`, `DCStoreRange`,
   `DCInvalidateRange`, `DCFlushRangeNoSync`, `DCStoreRangeNoSync`,
   `DCZeroRange` excluded because it writes memory) as immediate returns using
   the runtime's host-call hook at their entry addresses. With cache emulation
   off, Dolphin's own `dcbf`/`dcbst` are no-ops apart from a JIT invalidation
   heuristic that this AOT runtime does not need. This removes the per-line
   dispatches and the trailing `sc` together. Keep chunk verification enabled
   and validate self-modifying-code paths (`smc_failed`, `reverify_events`).
3. Intercept the vector itself: register `0x80000C00` as a host call that checks
   the seven words against `__OSSystemCallVector` and performs the `rfi`
   (MSR from SRR1, PC from SRR0). Smaller gain than 2 but generic for any
   remaining `sc` caller, including the `sc; blr` helper.

Option 2 needs a host-call source. ModernGekko's code-mod loader supports
entry hooks at addresses, but every runner here passes `--no-mods` and the iOS
build links statically, so the hooks belong in `recompcore-platform.patch` or
in the platform runtime rather than a loadable mod. Measure with the same
receipt counters: `fallback` and `native_exc` should drop by more than 90%,
and `hook_fb` by roughly the cache-hook share.

### Results (2026-09-13, later the same day)

Fixes 2 and 3 are implemented inside the recompiler core, not as code-mod host
calls. The first attempt used `StaticRecompModuleSource::host_call`: it worked
functionally, but the core forces any chunk containing a host-call address
into the interpreter (`[staticrecomp] mod fallback: chunk [0x802817A0,0x802857A0)`),
and `IsHostCallAddress` runs on every native dispatch. Both slowed the OS idle
spin, which is what paces guest time in this runtime, and speed fell to 0.30.
The core now takes `return_hooks` and `emulate_syscall_vector` from the module
source: hooked entries are removed from the dispatch lookup table so a burst
stops there at no per-dispatch cost, and the run loop performs the verified
return or the vector's `rfi` before the interpreter fallback. The GXBE69 table
lives in `dolphin_runtime.cpp` (`ssx3_hle`), gated by `SSX3_HOST_HLE=0`.

Matched 180 s Garibaldi checks through `gamecube_schedule_check.py` (640x528,
immediate XFB), HLE against a back-to-back control on the same player:

| Counter (whole run) | Control | HLE |
| --- | ---: | ---: |
| Interpreted instructions | 42.2M | 12.9M |
| Native-raised exceptions | 4.30M | 0.09M |
| Cache-hook calls | 161M | 0 |
| HLE returns / vectors / rejects | 0 | 4,812,183 / 1 / 0 |
| Chunk hash failures | 0 | 0 |
| Speed, median of samples 60–175 | 0.835 | 0.822 |

The course check passed in both. The remaining interpreted instructions are
the external-interrupt and decrementer vectors. Speed did not change on the
Mac: the saved time went into the `SelectThread` idle spin (43% → 61% of
dispatch samples). Absolute speed drifted down across the afternoon (0.999 in
the morning baseline, 0.905 and 0.835 in later controls with identical
settings), so only back-to-back pairs are comparable. The phone should see
the benefit where it currently dips below real time, and during the smoothing
trial, whose scheduler replaces the spin with `CoreTiming::Idle()` slices.

Fix 1 (idle-loop skipping) is **not** adopted. `StaticRecompIdlePC` with the
stock per-slice behaviour reduced speed from 0.905 to 0.69 (HLE off) and 0.87
(HLE on): `CoreTiming::Idle()` only zeroes the current slice, at most
`MAX_SLICE_LENGTH` = 20,000 cycles (about 41 us), so every 41 us of skipped
idle costs a burst exit, `Advance()` and re-entry. A tighter loop that kept
calling `Idle()`/`Advance()` while the guest sat at the idle address delivered
interrupts (exits by pc change at about 227/s, MSR showing EE cleared) but the
game never became runnable and stayed at boot with zero frames, with or
without immediate XFB. That change is reverted; `SSX3_IDLE_PC` remains as an
opt-in research knob in `tools/native_gamecube.py` for the stock behaviour.
The wake-up path that differs between executing the spin natively and
skipping it is still unidentified; any future idle-skipping work must start
there, because the same `Idle()` slice cost applies to the smoothing
scheduler's cooperative yield.
