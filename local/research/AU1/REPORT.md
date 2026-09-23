# AU1 REPORT: SSX 3 sound, what it needs and the routes to audible audio

Brief: `local/muse/prompts/AU1.md` (lane renamed from A1 on 09-23). Worker:
Claude Code (Opus pane). Scope was read-mostly: one Mac boot (one slot) and no
code changes. Tables and receipts follow; the recommendation is in AU1-6, and
the orchestrator decides.

## AU1-0. Short answer

- **No sound code runs today, on either side.** The EE loads SNDDRV.IRX and
  LIBSD.IRX (the HLE loader returns success). It binds EA's `SND` server
  (SID `0x534E44`) and sends it one init RPC, which goes unhandled. The EE
  sound thread (entry `0x3C19A8`) then sleeps forever on semaphore 36. That
  semaphore is signalled only by the handler at `0x3C1578`, which the game
  registers for **SIF command 1 from the IOP**. Nothing sends that command.
  The runtime records handler registrations (`SIF.cpp:482`) but never calls
  them.
- **The EE still feeds audio data.** It reads the audio archives' directories,
  sound banks, the menu-music program `charsel.mpf`, and the first ~194 KB of
  **`charsel.mus`** (menu music, MUSIC2.BIG) at vsync 335. In the race it reads
  `fspoon.mus` / `fsloops0.mus`. After that, streaming stalls because nothing
  consumes the data.
- **How EA SND works:** the EE SND library (V8.03.03) sends 0x30-byte SIF
  command packets (cid 0) to SNDDRV. The IOP calls back with cid-1 ticks, and
  the EE sound thread runs once per tick. SNDDRV mixes and resamples, and
  pushes PCM to the SPU2 core's AutoDMA input with `sceSdBlockTrans`. It also
  imports the hardware-voice calls (`VoiceTrans`, `SetParam`, `SetSwitch`).
  SNDDRV.IRX **keeps its symbol table** (145 functions), which makes it cheap
  to reverse-engineer.
- **Routes.** (a) HLE of the SND protocol plus a host mixer is the cheapest to
  run but means re-implementing EA's IOP driver. (b) Adopting upstream
  `feature/iop-emulator` gives an R3000 interpreter and IRX loader, but no
  SPU2. It also stubs the four `sifcmd` imports SNDDRV depends on, and it would
  run *every* IRX physically. (c) A hybrid runs only SNDDRV (and possibly
  LIBSD) on a small R3000 core and captures libsd's AutoDMA PCM, adding an
  SPU2 voice engine only if hardware voices turn out to carry sound.
- **Recommended first milestone:** menu music (`charsel`) audible on the Mac,
  produced by the game's own SND code. The shortest path starts with a
  discriminating spike (AU2, AU1-6).

## AU1-1. IOP modules and SIF RPC census (one current Mac boot to the race)

Boot `au1a`: E51 runner (E50 build, fork `e51-diag` = `ssx3` `eac6cba` + E50
taps + GIF dump), sha256 `20163c2a22b52689361944406a881b665728926c9936e53c29abaa053fb3b010`
(same as E51's). E51 route, 540 s wall, slot 1, rc 0. It reached tick 8688,
race timer 00:00:25 (`receipts/au1a-race-540s.png`). The park snapshot
records every SIF load/bind/call/sendcmd (`kMaxRpcEvents` 4096,
overflow 0). The census matches E51's `e51a` boot event for event.

| # | Module (load order) | Load tid | Sound? | Runtime result | Evidence |
| --- | --- | --- | --- | --- | --- |
| 1 | `DATA\MODULES\SIO2MAN.IRX` | 1 | no | claimed (HLE no-op load) | `receipts/park-au1a.txt` |
| 2 | `PADMAN.IRX` | 1 | no | claimed | same |
| 3 | **`LIBSD.IRX`** (28,557 B; exports `libsd` v0x0105) | 1 | **yes**: Sony SPU2 library | claimed, **not executed** | same; `irx-imports.txt` |
| 4 | **`SNDDRV.IRX`** (96,016 B; EA "SND_Library_EE_Driver", `ps2/sndiop.c`) | 1 | **yes**: EA SND IOP driver | claimed, **not executed** | same; `snddrv-symbols.txt` |
| 5–6 | `MCMAN.IRX`, `MCSERV.IRX` | 1 | no | claimed (MCSERV HLE core service) | same |
| 7–8 | `USBD.IRX`, `USBKB.IRX` | 3 | no | claimed | same |
| 9–18 | `DEV9`, `INET`, `NETCNF`, `INETCTL`, `SMAP`, `PPP`, `SPDUART`, `PPPOE`, `MSIFRPC`, `LIBNET` | 3 | no | claimed | same |
| 19 | `DRTYSCKF.IRX` | 3 | no | claimed | same |
| 20 | `LGAUD.IRX` (exports `lgaud`; imports `usbd`) | 3 | USB headset audio (online voice chat); **not needed** for game sound | claimed | `irx-imports.txt` |
| 21 | `VOIPF.IRX` (imports `lgaud`, `inet`) | 3 | voice over IP; **not needed** | claimed | same |

Not loaded by the game: `DATA/MODULES/SDRDRV.IRX` (8,065 B) and the
`NETGUI/MODULES` set (MODMIDI/MODHSYN/EZMIDI/SDRDRV belong to the network
GUI ELF).

| SID | Binds | Calls (fno, send/recv B) | Caller PC | Sound? | Runtime result |
| --- | --- | --- | --- | --- | --- |
| `0x237` | 1 | 1 (fno 0, 128/128) | `0x3f6a04` | no (network setup area, not identified) | unhandled: dummy server, reply = copy of send buffer |
| `0x80000211` | 1 | 1 (fno 1, 16/144) | `0x40c34c` | not identified | unhandled, same fallback |
| **`0x534E44`** ("SND") | 1 | **1** (fno 0, 20/0) | `0x3c0bc4` (in `sub_003C0B10`) | **yes**: EA SND driver | unhandled; recv size 0, so nothing is written back |
| `0x80000006` | 1 | 1 (fno 0xff, 0/4) | `0x42b0e8` | no | unhandled |
| sendcmd `0x80000001` | – | 1 (24 B) | – | no (SSX 3 sregs handshake) | claimed |

SND init payload (first 16 of 20 bytes, `receipts/boot-au1a-sound-lines.txt`):
`03 03 08 00 | 40 B7 50 00 | 00 00 00 00 | A0 8C C0 5D`. The second word is
EE address `0x0050B740`. In the whole 540 s there are **no further SND
RPCs**, because per-tick traffic uses SIF commands (AU1-4). This census counts
RPC calls only. `sceSifSendCmd` and `sceSifSetDma` calls from the SND library
are not tallied by any current tap (gap G2).

## AU1-2. How the runtime handles each piece today

| Piece | Where | Status | What the guest gets back | Audio produced? |
| --- | --- | --- | --- | --- |
| IRX loads (all 21) | park `op=load … claimed` | HLE no-op | success | – |
| SND RPC `0x534E44` | `Kernel/Syscalls/RPC.cpp:304` bind (dummy server), `:560–720` call; `ps2xIOP` has no SSX 3 profile (`builtin_profiles.cpp`, README table: recvx/lotr/fatal-frame only) | **missing** | bind OK; call returns 0; recv 0 B (the unhandled fallback copies send→recv, but recv size is 0) | no |
| libsd RPC `0x80000701` | `ps2xIOP/src/modules/libsd.cpp` → `PS2AudioBackend::onSoundCommand` (`ps2_audio.cpp`) | HLE for games that use Sony's `sdrdrv`-style RPC; SSX 3 **never calls it** | – | no |
| `sceSd*` EE stubs | `Kernel/Stubs/Audio.cpp` (`sceSdRemote` transfer bookkeeping; `sceSSyn_*`/`sceSynthesizer*` are `TODO_NAMED`) | stubs; not used by SSX 3's SND library | – | no |
| `sceSifAddCmdHandler` | `Kernel/Stubs/SIF.cpp:477–484` | handler address stored in `g_sifCmdHandlers`, **never invoked** (no IOP→EE command path) | 0 | – |
| `sceSifSendCmd` | `Kernel/Stubs/SIF.cpp:27–47` | copies the extra-data range if dst ≠ 0, returns 1; **the packet itself is dropped** | 1 | – |
| `sceSifSetDma` | `Kernel/Stubs/SIF.cpp:846–979` | copies each descriptor. IOP destinations inside the HLE IOP heap window `0x04000000–0x04500000` go to a host mirror (`SIF.cpp:295–310`); **any other IOP address is written into EE RDRAM** (masked). Hazard for later SND work, not observed this run | transfer ID | – |
| EE sound thread | thread 6, entry `0x3C19A8`, pri 6 | ran once (`sched=1`), blocked in WaitSema(36) at `ra=0x3c19f0`; semaphore 36 has **0 signals** (`receipts/park-au1a.txt`) | – | – |
| Host audio device | `ps2_runtime.cpp:844–845` `InitAudioDevice()` → `setAudioReady` | **present on all targets**: Mac "AUDIO: Device initialized successfully … miniaudio \| Core Audio" (this boot); iPhone Core Audio 48 kHz (I8 REPORT); Android links OpenSL ES via raylib (N2 `build1c-tail.log:25`); not yet heard on the Odin | – | device opens, nothing is submitted |
| Host playback path | `PS2AudioBackend` (`ps2_audio.cpp`) | one-shot raylib `Sound` per decoded VAG, max 4 concurrent, WAV built per play. **Not a streaming path** (no `AudioStream`/callback) | – | – |

## AU1-3. Sound data on the ISO

All values come from the ISO / extracted tree. Formats are named from on-disc
bytes; codec names beyond the raw tag values are not verified in the repo.

| File (ISO LBN) | Size | Container | Entries | Payload format (on-disc magic, header tags) | Used for |
| --- | --- | --- | --- | --- | --- |
| `DATA/AUDIO/MUSIC.BIG` (`0xe0ba6`) | 435.5 MB | EA `BIGF` (BE dir) | 71: 45 `.mus`, 25 `.mpf`, 1 `.bnk` | `.mus` = `SCHl` streams (25) or `BNKl` (20 loop banks); `.mpf` = `PFDx` (stored `xDFP`: EA interactive-music program) | licensed music |
| `DATA/AUDIO/MUSIC2.BIG` (`0x9bdb4`) | 464.7 MB | `BIGF` | 59: 38 `.mus`, 20 `.mpf`, 1 `.bnk` | same | music incl. **`charsel`** (menu) and **`fspoon`/`fsloops0`** (race) |
| `DATA/AUDIO/SPEECH.BIG` (`0x6030f`) | 261.4 MB | `BIGF` | 295: 294 `.dat` + `headers.big` | `SCHl` mono (no `0x82` tag) | rider speech |
| `DATA/AUDIO/ENGLISH.BIG` (`0x7f58f`) | 239.1 MB | `BIGF` | 30: 29 `.dat` + `langhead.big` | `SCHl` | DJ / PA ("EA Radio" DJ lines) |
| `DATA/AUDIO/AUDIO.BIG` (`0x5f4f3`) | 7.4 MB | `BIGF` | 140: 131 `.bnk`, 9 `.eam` | `BNKl` (little-endian EA bank); `.eam` = `MIDx` | SFX banks, crowd |
| `DATA/AUDIO/GRNT_*.BNK` ×12 | 13–54 KB each | none | – | `BNKl` | per-rider grunts |
| `DATA/MOVIES/*.MPC` (15 files) | 1.3–178 MB | `MPCh` video chunks interleaved with EA audio | e.g. INTRO.MPC: 6,219 `MPCh`, 1 `SCHl` + 6,216 `SCDl` | MPEG-2 video + `SCHl` audio | movies (skipped under `PS2X_SKIP_MOVIE`) |

`SCHl` platform header (raw, `big-census.txt`, AU1 dumps): every stream is
`PT 05 00`. Music has `0x82 = 2` (channels), `0x84 = 0x7D00` (32,000 Hz),
`0xA0 = 0x0A`. Speech has `0xA0 = 0x0A` and no channel/rate tag (defaults).
`charsel.mus` segment 1: `0x85 = 0x0A067F` (657,023 samples ≈ 20.5 s at
32 kHz), stereo, `0xA0 = 0x0A`. SNDDRV contains XA unpackers
(`SFILTER_unpackxaf`, `…xalf`, `decxa16c`), which fits codec `0x0A` being
EA's XA-family ADPCM. That is an inference from symbol names; there is no
decoder in the repo to confirm it.

**How it's read:** SNDDRV imports **no `cdvdman` and no `ioman`**
(`irx-imports.txt`). All disc reads are the EE's own `sceCdRead` (callers
`0x3E3618`, `0x3E3B00`, `0x3E3D78`, the file thread). Data then goes to the
IOP over SIF. Census CD reads of the audio archives (`audio-big-reads.txt`,
`cdread-au1a-files.md`, from `PS2X_CD_READ_TRACE`):

| Archive | Reads | Sectors | vsync | Entries touched |
| --- | ---: | ---: | --- | --- |
| MUSIC2.BIG | 61 | 337 | 53–7092 | `charsel.mpf` + first 97 sectors of **`charsel.mus`** (vsync 234–335); `fspoon.mpf`, `fsloops0.mus` (157 sectors), `fspoon.mus` (67 sectors, trickling to 7092) |
| AUDIO.BIG | 11 | 40 | 53–4009 | directory, `LoadingScreen.bnk` (34 sectors), `zBxsfx.bnk`, crowd `.eam` headers |
| SPEECH.BIG | 19 | 107 | 53–1402 | directory, `headers.big`, `Post_Selection_zoe.dat` (49 sectors) |
| ENGLISH.BIG | 4 | 17 | 66–77 | `langhead.big` |
| MUSIC.BIG | 3 | 3 | 53 | directory only |
| GRNT_AI.BNK | 3 | 27 | 4016 | whole file |

Single-sector reads at entry boundaries (e.g. `abullys.mpf`, `finger.mus`)
are directory/boundary probes. Total music read in 540 s is 0.66 MiB. A live
32 kHz stereo stream would need several MB over the same span, so the
streamer primes its buffers and stops.

## AU1-4. The EA SND mechanism (EE ↔ IOP), from code

EE addresses are cited from `ee-at` / `ee-xref`. Only labels from `ee-label`
are used for names; everything else is described by address. SNDDRV names
come from its own ELF symtab (`snddrv-symbols.txt`); `libsd`/`sifcmd` ordinal
names also match PCSX2 `pcsx2/IopModuleNames.cpp` @ `9056c0834` (bytesize
clone).

| Step | EE side | IOP side (SNDDRV) |
| --- | --- | --- |
| Init | `sub_003C1B80` region: `func_425FF0(0x50C880, 16)` then `sceSifAddCmdHandler(1, 0x3C1578, 0x50C900)` (`0x3c20a8–0x3c20cc`); starts the sound thread `0x3C19A8`; `sub_003C0B10` → `sceSifCallRpc(client 0x50B980, fno, mode = (fno==2), send 0x50AD00, size)` (the one census RPC, fno 0) | `SNDIOP_init` (2,048 B); `sceSifRegisterRpc` for `0x534E44` served by `SNDIOP_dispatchrpc` (412 B) via GetNextRequest/ExecRequest; `sceSifAddCmdHandler` → `SNDIOP_cmdhandler` |
| Tick (IOP→EE) | handler `0x3C1578`: packet +0x10 = type. 0/2 → store +0x0C to `0x50C804`, `iSignalSema` (wrapper `0x423DD0`) on sema at `0x50C7A4` (id 36); 1 → `func_3C4918(+0x0C)` | `SNDIOP_dmathread` polls `sceSdBlockTransStatus`, refills with `SNDIOP_loadautodma1/2`; sends `sceSifSendCmd`/`isceSifSendCmd` |
| Update (EE) | sound thread wakes, waits for the init flag byte `0x50C7AD`, calls the fn ptr stored at `0x44C46C`, then `sub_003B5540(0x5E)` (`0x3c1a24`) → `sub_003B55F0`, which **increments the tick counter `0x50A8E8+0x180`** (`0x3b5618–0x3b5620`) | – |
| Commands (EE→IOP) | `sub_003C4450` builds a 0x30-byte cid-0 packet (type 1 at +0x10; +0x14/+0x18/+0x1C words; +0x20 u16; +0x22 u8) and sends it with `sceSifSendCmd` / `isceSifSendCmd` (`0x3c4588–0x3c45c0`) | `SNDIOP_cmdhandler` (80 B): type 1 → `SNDIOP_dmqueue(+0x14, +0x18, +0x1C, +0x20, +0x22)` (llvm-objdump, AU1-7) |
| Mix / output | EE-side mixing is implied by `SNDIOP_maincpufx` and the rate converters `SNDIOP_ee{24,36,48}_iop{24,36,48}[_spu48]` (not yet traced on the EE) | IOP mix + XA unpack (`SFILTER_unpackxa*`, `decxa16c`); output through libsd **`sceSdBlockTrans`** (AutoDMA PCM) plus hardware-voice imports (`sceSdVoiceTrans`, `SetParam`, `SetSwitch`, `SetAddr`, `SetCoreAttr`, `SetEffectAttr`) |
| Waits on IOP progress | `sub_003C2268` spins `func_3C60E0` while counter `+0x180` < start + 10 (`0x3c22b8–0x3c22e8`) | – |

Consequences: (1) with no cid-1 ticks, the SND library never runs, so the
recomp stays silent while the game logic proceeds. (2) Any code path that
waits on the `+0x180` counter (e.g. `sub_003C2268`, reached from
`sub_003B5158` / `sub_003B5320`) would hang today. This is a lead for the
E-lane stall work, not a verdict.

## AU1-5. Routes, cost and fit

Cost units: briefs of roughly one worker day each, including their builds
and boots. Perf figures marked "est." are estimates without measurements.

| | (a) HLE the SND protocol + host mixer | (b) LLE: upstream `feature/iop-emulator` + SPU2 core | (c) Hybrid: SNDDRV (± LIBSD) on a small R3000 core + libsd-level capture (+ SPU2 voices if needed) |
| --- | --- | --- | --- |
| What we build | (1) SIF cmd bridge: deliver cid-1 packets to EE handlers (guest interrupt-context call), capture cid-0 packets and SIF DMA; SND RPC reply. (2) Native reimplementation of SNDDRV's command semantics (`dmqueue`, stream/bank lifetimes, voice ops). (3) Host mixer: EA XA decode for IOP-mixed channels, an SPU-style ADPCM voice engine if hardware voices are used, resample to 48 kHz, raylib `AudioStream` ring | Merge 21 upstream commits (15,785 insertions / 1,236 deletions across 129 files, incl. `SIF.cpp` ±412, `RPC.cpp`, `ps2_runtime.cpp`, GS files) into our fork; fill the `sifcmd` gaps SNDDRV needs (ordinals 8 SetCmdBuffer, 10 AddCmdHandler, 20/21 GetNextRequest/ExecRequest are no-op `setV0(0)` in `iop_rpc.cpp`); add IOP→EE command delivery to EE handlers; port PCSX2 SPU2 (`pcsx2/SPU2`, 6,568 lines incl. debug/wavedump); wire IOP DMA ch4/7 (today a register store plus completion IRQ, `iop_memory.cpp`) and SPU2 IRQs | Take the branch's R3000 core (`iop_cpu.cpp` 497 lines + `iop_memory`) **without** its loader policy; a purpose-built import layer for exactly SNDDRV's imports (`libsd` 12 fns, `sifcmd` 9, `thbase` 9, `sysmem` 3, `sysclib` 4, `intrman` 2, `loadcore` 1, `sifman` 1) and LIBSD's (`thevent` 7, `intrman` 7, `sifman` 2, …); either run LIBSD.IRX too or HLE `libsd` natively and capture `sceSdBlockTrans` AutoDMA buffers as the final PCM; SPU2 voice engine only if hardware voices carry sound |
| Accuracy | Medium; exact only where we copy EA's semantics. Mixing/resampling/filters (`SFILTER_*`, `SNDMIXI_*`) re-derived by hand | Highest: real driver, real libsd, SPU2 core with ADSR/reverb/interp | High: real driver logic; output bit-exact for the AutoDMA PCM path; hardware voices exact only with an SPU2 port |
| Effort (est.) | 4–6 briefs, plus open-ended RE if hardware voices matter | 6–10 briefs, plus merge conflicts with E/G-lane fork work; every IRX would run physically (branch policy: "original IRX modules execute on the R3000 path … physical IRX is authoritative"), so PAD/MC/network modules change behaviour too, a regression risk that needs an allowlist | 3–5 briefs (R3000 core exists; imports are few and named; SNDDRV has symbols); +2–3 if the SPU2 voice port is needed |
| Game-specific? | Fully (EA SND 8.03.03 only; other EA titles of that era may share it) | Generic | Mostly generic (any IRX + libsd game) |
| Odin / iOS perf | Cheapest: all native | IOP interpreter + all modules + SPU2: est. 10–30% of one A78-class core worst case; SPU2 48 voices at 48 kHz est. 5–10% of a core | IOP interpreter runs only SNDDRV (+LIBSD) wakeups: est. a few % of a core; AutoDMA capture is ~free; SPU2 voices as (b) if needed |
| Timing / 120 Hz | Tick source is ours: clock cid-1 ticks from the host audio callback, so audio stays wall-clock-true at any sim rate | IOP clocked from EE cycles (`runEeCycles`); at 2× sim the IOP clock and audio would follow EE time unless decoupled | Same choice as (a): drive SNDDRV's timer/DMA-complete events from the host audio clock |
| Shared needs (all routes) | Host streaming output (raylib `AudioStream` at 48 kHz: the current `PS2AudioBackend` is one-shot only); IOP→EE SIF command delivery to `g_sifCmdHandlers`; a guest-speed floor: the EE sound thread (pri 6) must run every few ms of wall time. On the Odin today (0.2–3 guest fps in 3D) any route will underrun until the speed work lands | | |

Pieces of existing code worth reusing: `ps2_audio_vag.cpp` (PS-ADPCM VAG
decode, for SPU voice data), `ps2xIOP` service/profile framework (an
`ssx3-us` profile could host (a)'s SND service or (c)'s adapter), and
upstream's `iop_cpu.cpp` plus the `iop_rpc.cpp` SendCmd→`m_host.sendSifCommand`
plumbing.

## AU1-6. Smallest audible milestone and the shortest path

**Milestone M-A1:** on the Mac, at Select Character, the `charsel` menu music
is audible, produced by the game's own SND library (not a host-side jukebox).
Acceptance: a WAV capture from the host stream plus a listen check. The EE
keeps reading `charsel.mus` past its first 194 KB, and the counter
`0x50A8E8+0x180` advances.

One unknown decides the path: **where the `charsel` stream gets decoded and
mixed.** If the EE mixes it, the PCM leaves the EE in cid-0 `dmqueue`
transfers and a bridge alone gives music. If SNDDRV unpacks the XA on the IOP
(`SFILTER_unpackxa*`) and mixes there, we need SNDDRV itself (route c) or a
reimplementation of that unpack/mix (route a). The `ee*_iop*` converter
family allows either.

Proposed next brief **AU2** (one Opus/muse worker, 1 build, ≤2 Mac boots):

1. Part A (static, no boots): disassemble SNDDRV (`llvm-objdump
   --triple=mipsel`; the symbols are present) for `SNDIOP_dmqueue`,
   `dmservice`, `dmathread`, `threadmain`, `dispatchrpc`, `init`, and the EE
   packet builders at `0x3C4450` / `0x3C43C0` and the cid-1 handler. Output: a
   protocol table (cid-0 fields, cid-1 types 0/1/2, RPC fno 0 payload incl.
   `0x0050B740`, who DMAs what where).
2. Part B (spike, env-gated, default off, e.g. `PS2X_SND_TICK=1`): deliver a
   cid-1 type-2 packet to the registered EE handler at a fixed host rate, and
   log every cid-0 packet plus SIF DMA descriptor. Observable: sema 36 signals
   > 0, the counter advances, `charsel.mus` reads continue, and the logged
   `dmqueue` source ranges hold either PCM (a WAV dump plays music) or XA
   blocks (they match `SCDl` payload bytes from MUSIC2.BIG).
3. Outcome → next: PCM from the EE means route (a)-lite: wire those buffers to
   a raylib `AudioStream`, and M-A1 is 1–2 briefs away. XA forwarded to the
   IOP means route (c): SNDDRV on the R3000 core with a libsd AutoDMA capture
   (3–5 briefs).

Not recommended as the first step: merging upstream `feature/iop-emulator`
wholesale (route b). It lacks SPU2 and the SNDDRV-critical `sifcmd` imports,
and would switch every IRX to physical execution.

## AU1-7. Commands, pins, receipts

| Item | Value |
| --- | --- |
| Boot | `local/research/AU1/au1_boot.sh au1a 540`: E46 wrapper, `E46_RUN_DIR=~/dev/ssx3-work/AU1/run`, `E46_BUILD_DIR=~/dev/ssx3-work/E50/build`, `PS2X_CD_READ_TRACE=…/cdread-au1a.txt`, E51 route; slot 1 claimed 22:57:30Z, released; own PID 60796 exited (checked by PID) |
| Runner | `~/dev/ssx3-work/E50/build/ps2xRuntime/ps2EntryRunner` sha256 `20163c2a…3b010` (read once here; matches E51 REPORT) |
| ISO | `~/dev/ssx3-work/E32-inputs/SSX 3 (USA).iso`; extracted tree `…/E32-inputs/cd` |
| Raw (not committed, `~/dev/ssx3-work/AU1/run`, 14 MB) | `boot-au1a-1.log` `43e04b64…6441`; `cdread-au1a.txt` `7ccd49a5…4c90`; `park-snapshot.txt` `728b74e5…2820` (`receipts/sha256-raw.txt`) |
| Receipts (committed) | `receipts/park-au1a.txt`, `receipts/cdread-au1a.txt.gz` (cdread/cdsearch lines only), `receipts/boot-au1a-sound-lines.txt`, `receipts/au1a-result.json`, `receipts/wrap-au1a.log`, `receipts/au1a-race-540s.png` |
| Tables | `iso-lbn-map.txt` (`au1_isomap.py`), `big-census.txt` (`au1_big.py`), `cdread-au1a-files.md` (`au1_cdfiles.py`), `audio-big-reads.txt` (`au1_bigreads.py`), `irx-imports.txt` (`au1_irx_imports.py`), `snddrv-symbols.txt` (`au1_elfsyms.py`; the game ELF has no symtab) |
| EE lookups | `local/tooling/ee/ee-at 0x3c0b10 0 60`, `ee-at 0x3c19a8 0 40`, `ee-at 0x3c20c0 14 8`, `ee-at 0x3c15c0 40 12`, `ee-at 0x3c2268 0 70`, `ee-at 0x3c4560 20 24`, `ee-at 0x3b5620 16 4`; `ee-xref 0x3c0b10 / 0x426d18 / 0x4261b0 / 0x4261f0 / 0x401df8 / 0x3c1578 / 0x3c19a8`; `ee-label 0x423dd0 / 0x426020 / 0x426d18` |
| IOP disasm | `/opt/homebrew/opt/llvm/bin/llvm-objdump -d --triple=mipsel --disassemble-symbols=SNDIOP_cmdhandler,SNDIOP_dmqueue,SNDIOP_dmathread,SNDIOP_transfersputoiop …/SNDDRV.IRX` |
| Upstream read (no contact) | `git log fork/feature/iop-emulator` (head `78ecbae`, 2026-09-14); `git diff --stat fork/main...fork/feature/iop-emulator`; `git show fork/feature/iop-emulator:ps2xIOP/src/emulator/{iop_emulator.cpp,services/iop_rpc.cpp,core/iop_memory.cpp}` |
| PCSX2 read | `ssh bytesize` → `/home/brad/pcsx2-t4/pcsx2` @ `9056c0834`: `pcsx2/IopModuleNames.cpp` (libsd/sifcmd/sifman names), `wc -l pcsx2/SPU2/*` (6,568) |
| Budget | 1/1 boot; no builds, no code changes; ~1 h 45 min; AU1 dir 192 KB + 14 MB raw; internal 65.4 of 200 GB before the boot |

## Gaps

- G1. The EE side of EA SND is only partly traced (packet builder, handler,
  tick counter). Where the music stream is decoded/mixed is **not settled**;
  AU2 settles it.
- G2. No current tap counts `sceSifSendCmd` / `sceSifSetDma` /
  `sceSifGetOtherData` calls. This boot can't show how many SND commands the
  EE issues without ticks, or where SIF DMA landed. A counter tap needs a
  build: a new build dir is ~2.9 GB (E50/build), over this brief's 2 GB cap,
  so none was made.
- G3. `SCHl` codec `0x0A` is not named from repo evidence. The full layout of
  the 44 MB `charsel.mus` (8 `SCHl` segments / 8.5 MB of `SCDl` found by a
  naive walk) isn't decoded; the MPF (`PFDx`) format isn't decoded.
- G4. Whether SSX 3 plays anything on SPU2 **hardware voices** (vs all PCM
  through AutoDMA) is unknown. PCSX2's T47 trace shows a 1.75 MB, 448-chunk
  "SPU voice upload" at the Snow Jam load, which suggests yes for some
  content.
- G5. Identities of SIDs `0x237`, `0x80000211`, `0x80000006` are not
  verified. None is in the sound path.
- G6. Odin audio output has never been listened to. Perf figures in AU1-5 are
  estimates.
