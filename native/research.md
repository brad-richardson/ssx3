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
