# Fast cold start to the main menu

The faster-start option skips the pending startup movies, waits for the title
screen's resource-readiness callback and a complete active input update, then
sends one START through the ordinary controller path. Frontend construction,
asset loading, title UI loading, and
the normal transition into the main menu still execute. It does not restore
an in-race snapshot, jump the guest PC, replace initialization results, or
alter the guest clock.

The phone menu offers **Turn on faster cold starts** / **Turn off faster cold
starts**. This preference persists and applies to the next cold launch or Full
Reset. It defaults on for this personal development build, including Full Reset. `--debug-main-menu` and `--normal-boot` override that
choice for one launched process without replacing the saved preference.
Compatible checkpoint restores retain precedence and disable the startup
observer entirely. Loading an existing checkpoint therefore cannot apply the
movie skip later when the player returns to the frontend.

## Verified native seams

These addresses are specific to GXBE69 revision 0, DOL SHA256
`b92162d6c616be3ce46b4eb61d5ddbb49891bc387ea7ddb2fea5792842fa29ce`.

| Seam | Evidence and action |
| --- | --- |
| Frontend update `0x80097dc4` | First initialized frontend update; checks the pinned entry instruction, `r13=0x803dfa60`, a valid frontend RAM extent, null movie player at `this+0xb5a58`, zero movie delay at `this+0xb5a60`, and pending mask exactly `0xf`. |
| Pending movies `0x803d7f64` (`r13−31484`) | Clear these four bytes once. The original mask selects black/EA BIG/THX/intro movie entries through the table at `0x802d7454`. Normal frontend update already has a no-pending-movie path at `0x80098104`, so resource and UI updates continue. Later attract-mode movies are untouched. |
| Title initialization `0x800d27e4` | Observe the real title state with vtable `0x802dfd78`. |
| Title resource readiness `0x800d2710` | Observe a true return at matching caller PC and stack; require a loaded UI pointer, no pending movies and no active movie player. Record `title_assets_ready`; this alone does not permit START. The original readiness countdown and widget activation remain intact. |
| Active title update `0x800d2628` | Require the same title, pinned entry instruction, loaded UI, and state-manager state 5 (`(title[29] >> 2) & 63`). Observe the complete update returning at matching caller PC and stack, then recheck state/UI/movie conditions before reporting `title_ready`. This update invokes the original input handler at `0x8023de94`. |
| Main-menu initialization `0x800d23cc` | Observe the real main-menu state with vtable `0x802dfd10`. |
| Main-menu update `0x800d20bc` | Require the matching state and loaded UI before reporting `main_menu_ready`; disable further observer work. |

The initial START attempt is state driven. It releases as soon as the title
state changes, or after two seconds, and never retries. A 200 ms pulse was too
short in the first native experiment. Pausing releases the startup input along
with normal controls; after an interrupted attempt, the user can continue
through the ordinary title input. Manual START ownership takes precedence.

Unknown initial masks, allocated movie players, invalid memory extents or an
unexpected layout disable the shortcut without modifying that state. A
120-second deadline checked at the frontend update seam bounds startup
observation. No clock read is added to each native dispatch. The usual
interpreter fallback, executable-memory guard, chunk verification, graphics
readiness, smoothing cancellation and checkpoint rules remain active.

## Evidence and limits

The first isolated native player used the production module, fresh controller
profiles, Metal validation, and unchanged production/vendor binaries. In
`local/research/startup/startup-skip3.jsonl`, frontend update and the movie skip
occurred at 14.065 s after guest execution began; title readiness at 19.052 s;
main-menu initialization at 19.719 s; and main-menu update at 20.137 s. A captured
frame shows the actual Main Menu with Single Event, Conquer The Mountain and
Multi Play. The 50-second run completed with zero invalid accesses, GPU command
errors, unknown instructions, failed chunk checks or JIT fallback entries.

The initial implementation's final helper and driver were rebuilt together under
`local/research/startup/player2`. Its 45-second `startup-final` check reached
the main menu at **20.085 s**: movie skip at 14.064 s, title readiness at
19.051 s, and main-menu initialization at 19.668 s. The driver released its
single START press on that state transition after about 595 ms. The final
screenshot again shows the actual Main Menu, and the runtime receipt reports
zero invalid accesses, GPU errors, unknown instructions, failed chunk checks
or JIT fallback entries. Exact source/player hashes and evidence paths are in
`local/research/startup/player2/build.json`,
`local/research/startup/player2/startup-final-check.json`, and
`local/research/startup/delivery.json`.

Subsequent Simulator checks exposed a startup input race: the original gate
reached the main menu in one of three runs, while two runs consumed the START
attempt without advancing. Both 75% and Match output reproduced it. The true
resource-ready return at `0x8023d66c` precedes promotion to state 3; the next
state-manager pass activates the title and promotes it to state 5. A button
edge delivered between resource readiness and activation can be lost even
while the button remains held. The corrected gate therefore waits for the
first complete state-5 title update before permitting that same single START
attempt. It adds no arbitrary delay or retry. Traces now distinguish
`title_assets_ready` from `title_ready` and include the observed title state.
The pre-fix failures are retained under
`local/research/120hz/match-startup-simulator-failed-start` and
`local/research/120hz/default-fast-start-simulator-failed-repeat`; they provide
no successful main-menu or smoothing acceptance. The stricter gate has
synthetic regression coverage; installed-build validation must use the new
header receipt rather than treating the earlier native captures as proof of
the revised gate.

The ordinary observer run `startup-normal1` retained mask `0xf` and played the
unattended movie sequence during its 110-second cap. It also completed without
runtime faults and continued capturing frames. This establishes that the
normal route remains available; it is not a matched comparison against a
person manually skipping the movies. The initial sandboxed attempt could not
enumerate Metal and executed no guest instructions; it is excluded from the
startup result.

These native timings exclude runtime creation and full asset verification.
The phone already reports `runtime_create_seconds` separately; its
`startup.jsonl` starts after runtime creation/checkpoint selection. Lifecycle
events provide host timestamps for effective startup mode, observed phases,
the START press/release, and sequence start. `startup.jsonl` includes relative
elapsed time, guest timebase, source PC/LR and the movie mask. Further reducing
the 14-second guest initialization phase or the original five-second title
readiness wait requires separate initialization/asset profiling. Native
success alone does not establish phone cold-start latency or persisted
preference behavior; the subsequent phone timing is recorded below, while
saved-toggle/relaunch coverage remains open.

## Reproduction

Build and run an isolated native player (each run requires a fresh profile):

```sh
python3 tools/gamecube_startup.py build --game local/game/gc-gari-027 \
  --output local/research/startup/player-new
python3 tools/gamecube_startup.py run --game local/game/gc-gari-027 \
  --player local/research/startup/player-new/player --profile startup-new \
  --skip --seconds 60
```

Omit `--skip` to observe ordinary boot. A debug run must establish both the
movie skip and real main-menu readiness to pass. Keep the build receipt,
startup trace, native runtime receipt and screenshots together.

The new sequence fixture waits for the main menu before beginning its bounded
20-second observation:

```sh
python3 tools/mobile_gamecube.py launch --simulator --device SIMULATOR_UUID \
  --debug-main-menu --sequence native/ios/main-menu-smoke.json \
  --simulator-null-audio
```

`start_when: "main_menu"` requires explicit `--debug-main-menu` at launch,
so a stale saved preference cannot accidentally leave automation waiting.
Sequence input, duration and scheduled smoothing use that anchored clock;
ordinary metrics keep their existing runtime-running clock and additionally
report `sequenceSeconds` (null while waiting). The original smoke sequence
remains available with `--normal-boot` for normal-boot coverage. Desktop `native_replay.py` accepts
`--startup-trace` for a main-menu-anchored sequence; supply only that run's fresh
trace. It waits at most 120 seconds and sends no sequence input before readiness.

## Installed build with the active-input gate

Build `113c9b20` is installed on the phone (September 13, 20:22 EDT), with fast
start enabled by default even for Full Reset. Three fresh final-build Simulator
runs reached Main Menu at 20.492, 20.530 and 20.467 seconds; each sent exactly
one START after a complete active title input update. Two runs used the default
preference with no launch override. The Match/2× run continued into a ride and
smoothing trial, then restored and stopped cleanly. These checks validate the
repeat-startup fix on Simulator. Delivery evidence is indexed in
`local/research/120hz/match-startup-delivery.json`.

The user's subsequent Garibaldi-only phone session `1789345362.689` reaches
the real main menu at **20.614526 s after guest execution began**. The user
reports that fast start worked great. All ten checkpoint saves committed.
This confirms the active-input shortcut on the phone; it does not include
runtime creation or full asset verification, prove saved-toggle persistence,
or validate every Full Reset/checkpoint-restore path. The ride's three guarded
smoothing trials do not establish sustained 120 Hz, and their audio counters
do not establish uninterrupted audio. Results and hashes are in
`local/research/120hz/match-startup-phone-user-results.json`; detailed pacing
limits are in the [resolution report](120hz-output-resolution.md).

## Loading and memory-card follow-up

Benchmark the remaining loading phases before changing their timing: actual
file I/O, decompression and resource initialization; emulated DVD/card delays;
and game UI/readiness timers. Record wall and guest time for cold startup,
memory-card checking and course loading, with fresh-process and warm-cache
runs distinguished. Preserve normal boot and verify menu readiness, card
read/write/relaunch behavior, loading transitions and ordinary riding.

The first isolated configuration candidate is Dolphin's **FastDiscSpeed**,
currently defaulting to false in pinned `Core/Config/MainSettings.cpp:211`.
`Core/HW/DVD/DVDInterface.cpp:1069` treats all reads as buffered when enabled,
changing modeled disc latency without skipping actual data reads or game
initialization. The subsequent [six-run Mac comparison](loading-speed-spike.md)
reduces median time to the main menu from 20.10 to 14.85 s, with startup states
and runtime checks passing. It remains off on the phone. Next compare on the
phone with identical assets/startup mode, then measure course loading separately;
retain the correctness checks above before considering adoption.

## Both levers reached the phone (September 15)

`FastDiscSpeed` existed only as the `-ssxFastDisc` launch flag, so an ordinary
tap on the icon never got the 20.10 -> 14.85 s improvement measured below. It is
now a stored setting.

The memory-card wait is modelled, not work: `MC_TRANSFER_RATE_READ` is
512 KiB/s, so scanning a card the device does not physically have costs seconds
of simulated latency. `SSX3_MEMCARD_READ_SPEEDUP` divides that read time
(`native/patches/moderngekko-memcard-read-rate.patch`); completion still runs
through the same `CoreTiming` events in the same order, so only the delay
changes. **Write rate is deliberately untouched** at 96.125 KiB/s - save
durability depends on the game seeing a write finish when it expects to, and
rushing writes improves no part of the boot.

Both sit behind one **Faster loading** switch in the pause menu, which sets
`SSXFastDisc` and an 8x card-read multiplier together, because they are the
same question: how much of the boot is modelled hardware latency rather than
real work. Still to measure on the phone: time to main menu with the switch on
against off, and the card-check phase in isolation.

## Measured on the phone (September 15): neither lever is where the time is

The card is instrumented now - `[ssx3-memcard]` at shutdown reports transfers
and the modelled delay they scheduled. One boot to the main menu:

    reads=1360 bytes=696320 modelled=0.165s | writes=0 bytes=0 modelled=0.000s

That is with an 8x read multiplier, so the stock cost is **1.32 s, and there are
no writes at all** - the folder-backed card is scanned, not written. Whatever
the pre-menu card screen is waiting for, at most 1.3 s of it was ever the card.

Nor does FastDiscSpeed reproduce its Mac result here. Across 82 sessions with a
readiness trace:

| fastDisc | card multiplier | n | main menu ready | frontend update |
| --- | --- | ---: | ---: | ---: |
| off | 1 | 2 | 20.45 s | 14.41 s |
| off | (absent) | 65 | 20.69 s | 14.65 s |
| on | 8 | 1 | 19.39 s | 13.32 s |

The 1.2 s saved is essentially the 1.15 s of card latency removed, so
FastDiscSpeed bought close to nothing - against 20.10 -> 14.85 s on the Mac.
The difference is what the bottleneck is: the Mac was fast enough that modelled
latency dominated, while the phone is CPU-bound, so buffering reads changes
nothing. Latency knobs cannot recover more than about 1.2 s of this 20 s boot.
(n=1 on the last row; worth repeating before leaning on it.)

## The boot is already skippable, and that is the lever

`SessionStore` restores a savestate on launch when the runtime identity matches,
and a checkpoint is about 104 MB written in 0.115 s - against a 20 s cold boot.
It works: 16 sessions restored. But 84 rejected it with "Game files or app
changed. Starting fresh.", because the identity is disc + DOL + module ABI +
**appBuild** + a hash of the whole `files` directory
(`HashDirectorySha256(root / "files")`, `src/runtime/game.cpp:300`).

So every app install invalidates it, and so does every world push and every
provision, since the patched glyph sheets live in `files/data/ui`. A session
spent iterating on the app guarantees a cold boot every time. The texture pack
does *not* invalidate it - the pack lives under `User/`, outside `files`.

Which reframes the question. Rather than shaving modelled latency, the boot is
avoided entirely by leaving the identity alone, and the remaining work is to
make resume the normal path: hold a checkpoint taken at main-menu readiness
rather than only at the last pause, and narrow the identity to what a savestate
genuinely depends on. Note also that hashing a 1.3 GB `files` tree happens on
every launch and is part of the ~1.9 s `runtime_create_seconds`; caching it
against file count, size and newest mtime would pay for itself.

Memory-card delays need a separate audit. Pinned
`Core/HW/EXI/EXI_DeviceMemoryCard.cpp:48` models 512 KiB/s reads and
96.125 KiB/s writes, with asynchronous completion events in `DMARead` and
`DMAWrite` (lines 522–555). No simple fast-memory-card flag is established.
Measure the card-check phase and preserve completion/interrupt ordering and
save durability; do not replace it with a shorter UI wait. These source paths
are relative to `third_party/ModernGekko/vendor/dolphin/Source/Core/`.
