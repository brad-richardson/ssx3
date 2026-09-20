# P8 — Input/audio API surface survey (pad + sound, read-only)

Tables, no verdicts. Static only: no fork writes, no boots, no lease, no adb.

## Pins

| Item | Receipt |
|---|---|
| Game ELF | `local/ssx3.elf` (SLUS_207.72), MD5 `9e64f3df7ed6e898061411ce43fe75eb`, 3890784 B |
| ELF layout | 1 LOAD (`off=0x1000 vaddr=0x100000`, so `VA=off+0xFF000`); 81 section headers; **no `.symtab`** (fully stripped); `.text 0x100000–0x42E020`, `.rodata 0x456900–0x49B018`, `gp=0x4A30F0` (`.reginfo`) |
| Fork | `/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp`, branch `ssx3`, HEAD `c41efce` ("Entry: add iOS scene manifest so UIKit entry reaches SDL_main (I7b)") |
| Fork worktree | 3 pre-existing local mods, untouched: `ps2xRuntime/src/lib/Kernel/EeScheduler.cpp`, `ps2xRuntime/src/runner/register_functions.cpp`, `ps2xTest/src/ps2_runtime_kernel_tests.cpp` |
| Analyzer map | `/Volumes/Extreme SSD/ps2recomp-spike/P1/ssx3.toml` (`stubs` = named lib fns, `untracked_stubs` = named but recompiled) + `ssx3-functions.sweep.csv` (9270 fns) |
| Recomp corpus | `/Volumes/Extreme SSD/ps2recomp-spike/P1/output/` — 9261 `sub_*.cpp` with disassembly comments; JAL census over all of them (8073 distinct `jal func_` targets) |
| Boot-log cross-ref | P1b `boot-p1b-2.log` (P1/REPORT.md:500): entry → 6 SIF module loads (`SIO2MAN PADMAN LIBSD SNDDRV MCMAN MCSERV`) → `sceCdRead` park |
| Scratch | `/Volumes/Extreme SSD/ps2x-p8/` (`strings-x.txt`, `jal_counts.tsv`, `jal_callers/`, `findrefs.py`, `jalcensus.py`) |

Census caveat: the analyzer emitted **overlapping functions**, so raw per-file JAL counts double-count. Overlaps seen:
`sub_00326DF0/sub_00326EB0/sub_00326E50` (pad wrapper, same PCs in 2 files),
`sub_0040B400/sub_0040B5B0/sub_0040B6D0`, `sub_003C0B10/sub_003C0BE8`.
All counts below are **unique static PCs** (deduped), with the raw file count in parentheses where it differs.

No dynamic imports exist anywhere: all SDK libs (pad/cd/mc/sif/rpc) are **statically linked**;
there are zero `scePad*`/`sceSd*` strings in the ELF. "Import receipt" below = TOML stub address + name.

## Table 1a — Game side: pad (`scePad*`, libpad statically linked at `0x3FF4A8–0x4007A8`)

15 of 28 libpad entry points are called, all from one wrapper region `0x326Dxx–0x3277xx`
(`sub_00326DF0` ← `0x326DB8` ← `sub_00326D60` ← `0x326A3C`), except `scePadInit` from boot.
Port/slot args are dynamic (`lw` from game struct `[s0+4]`/`[s0+8]`), not constants.

| Call | Stub VA | Unique JAL PCs (count) | Caller |
|---|---|---|---|
| `scePadInit` | `0x3FF4A8` | `0x31AE78` (1) | `sub_0031ADB0` (boot) |
| `scePadPortOpen` | `0x3FF708` | `0x326EE4` (1) | pad wrapper |
| `scePadPortClose` | `0x3FF8F0` | `0x326E78` (1) | pad wrapper |
| `scePadRead` | `0x3FFA58` | `0x3271E0` (1) | pad wrapper |
| `scePadGetState` | `0x3FFBC0` | `0x326F1C`, `0x327080` (2) | pad wrapper |
| `scePadGetReqState` | `0x3FFCD8` | `0x3270EC`, `0x32718C` (2) | pad wrapper |
| `scePadInfoAct` (rumble caps) | `0x3FFD60` | `0x327138` (1) | pad wrapper |
| `scePadInfoMode` | `0x3FFFA0` | `0x326F9C`, `0x326FB8` (2) | pad wrapper |
| `scePadSetMainMode` | `0x4000D8` | `0x32704C` (1) | pad wrapper |
| `scePadSetActDirect` (rumble) | `0x400190` | `0x327710` (1) | pad wrapper |
| `scePadSetActAlign` (rumble) | `0x400250` | `0x327164` (1) | pad wrapper |
| `scePadInfoPressMode` | `0x400490` | `0x3270A0` (1) | pad wrapper |
| `scePadEnterPressMode` | `0x4004F0` | `0x3270CC` (1) | pad wrapper |
| `scePadInit2` / `End` / `GetDmaStr` / `GetFrameCount` / `StateIntToStr` / `SetReqState` / `InfoComb` / `GetButtonMask` / `SetButtonInfo` / `ExitPressMode` / `SetVrefParam` / `GetPortMax` / `GetSlotMax` / `GetModVersion` / `SetWarningLevel` | `0x3FF5E8`…`0x4007A8` | 0 each | — (dead in this game) |

Arg windows: `PortOpen(a0=[s0+4] port, a2=s0+0x80 buffer)` @`0x326EDC–0x326EE4`;
`Read(a0=[s0+4], a1=[s0+8] slot, a2=$sp)` @`0x3271D8–0x3271E0`. No multitap evidence statically
(slot is dynamic; fork reports 1 slot).

## Table 1b — Game side: sound + SIF/RPC transport

No `sceSd*`/`sceSdr*`/libsd/libsdr function could be identified: zero such strings in the ELF,
zero in TOML `stubs`+`untracked_stubs`, analyzer symbol DB knows only the 6 `sceSdRemote*` names.
All EE→IOP sound traffic goes through game code + `sceSif*` RPC / raw SIF CMD.

**IOP module strings** (`strings-x.txt`, file offsets; `VA=off+0xFF000`):

| Strings (file off) | VA | Users |
|---|---|---|
| `cdrom0:\` + `%sDATA\MODULES\` (`0x38E9C8`, `0x38E9D8`) | `0x48D9C8`, `0x48D9D8` | path builder `sub_00319610` (`0x319674/0x31967C`) |
| `MSIFRPC/SIO2MAN/PADMAN/LIBSD/SNDDRV/MCMAN/MCSERV.IRX` (`0x38E9E8`–`0x38EAD8`, stride `0x10`) | `0x48D9E8`–`0x48DAD8` | boot `sub_0031ADB0` (6× via loader `0x319718`); `MSIFRPC` via `sub_003197D0` |
| `host0:/usr/local/sce/iop/modules/libsd.irx`, `host0:snddrv.irx` + bare names (`0x396828`–`0x396880`) | `0x495828`–`0x495880` | audio init `sub_003C1B80` (dev-path fallback after cdrom attempt fails) |
| 13 net/voice IRXs: `USBD USBKB DEV9 INET NETCNF INETCTL SMAP SPDUART PPPOE LIBNET DRTYSCKF LGAUD VOIPF` (`0x37B988`–`0x37BB30`) | `0x47A988`–`0x47AB30` | net init `sub_00228EE0` (14× via loader `0x319718`) |

**Loader + init graph** (all `jal`, unique PCs):

| Function | VA | Role | Callers |
|---|---|---|---|
| `sub_0031ADB0` | `0x31ADB0` | EE boot: 6 module loads + `scePadInit` + `sceMcInit` + `sceCdReadClock` + RPC-init chain | `0x31AFA0` |
| `sub_00319718` | `0x319718` | generic IRX loader (wraps `sceSifLoadModule@0x42BA68` @`0x319754`) | 6× boot, 14× net init (`0x228F0C`–`0x229138`), 1× `0x3197EC` |
| `sub_003C1B80` | `0x3C1B80` | **audio init**: reloads LIBSD+SNDDRV (4× `0x42BA68` @`0x3C1E64`–`0x3C1ED4`, cdrom then `host0:` fallback), `InitRpc`, `InitIopHeap`, `AllocIopHeap`, `AddCmdHandler(cid=1)`, `BindRpc`, thread/sema setup | `0x3B523C` (`sub_003B5158` ← `0x2A8D14`/`0x3C5DD4`) |
| `sub_003C0B10` | `0x3C0B10` | audio RPC wrapper: `CheckStatRpc` + `CallRpc` @`0x3C0BBC` | `0x3C2224` (audioInit tail), `0x3C232C`, 2× `sub_003C3450` |
| `sub_003C4450` | `0x3C4450` | audio SIF-CMD sender: `SendCmd` @`0x3C45C0` (`a2=0x30`, rest dynamic) | `0x3C4640`, `0x3C48EC` |
| `sub_00228EE0` | `0x228EE0` | net/voice init: 13 IRX loads + `BindRpc(sid=0x237)` via `0x3F6A40` @`0x229148` | `0x2282FC` |
| `sub_003F61D0` | `0x3F61D0` | secondary loader path (via `0x3F5DA8` helper) | `0x266814` |

**SIF/RPC entry points used** (TOML stub VA → unique JAL PCs):

| Call | VA | Sites | Caller files (unique PCs) |
|---|---|---|---|
| `sceSifInitRpc` | `0x426408` | 9 | `0x319620`, 2× `0x3198xx`, `0x3C1E18` (audio), 4× cd (`0x400xxx–0x401xxx`), `0x40C040` (usbkb) |
| `sceSifBindRpc` | `0x426B48` | 8 | `0x3C20F0` (audio, `sid=0x534E44`), `0x3F6A5C` (net, `sid=0x237`), 4× cd, `0x40C08C` (usbkb), `0x42B09C` (mod-mgr) |
| `sceSifCallRpc` | `0x426D18` | 38 | `0x3C0BBC` (audio), `0x3F69FC` (net), 4× cd, 6× usbkb, 24× file/mod-mgmt (`0x428E18` `_sceCallCode`, `0x42A538`, `0x42AC90`–`0x42B068`, `0x42B438`–`0x42B7D4`), 2 with overlap duplicates (deduped) |
| `sceSifCheckStatRpc` | `0x426F08` | 3 | `0x3C0B90` (audio), `0x3F69C0` (net), `0x40C87C` (usbkb) |
| `sceSifSendCmd` | `0x4261B0` | 12→10 unique | `0x3C45C0` (audio), `0x3F4988/0x3F4F98/0x3F52E0` (net cluster), 2× `sceSifM*` lib (`0x40B1C8`, `0x40B52C`), rest overlap duplicates of `0x40B670/0x40B85C/0x40B8C8` |
| `sceSifAddCmdHandler` | `0x426020` | 3 | `0x3C20C8` (audio, `cid=1`, handler `0x3C1578`), `0x400E68` (cd power-off), `0x40B198` (`sceSifMInitRpc`) |
| `sceSifLoadModule` (unnamed, inside TOML `_sceSifLoadModule` range) | `0x42BA68` | 7 | `0x319754` (generic loader), 4× audioInit, 2× `0x3F5DA8` |
| `sceSifInitCmd`/`ExitCmd`/`RemoveCmdHandler`/`InitIopHeap`/`AllocIopHeap`/`WriteBackDCache`/`SyncIop`/`RebootIop` | — | 1/2/1/3/3/14/1/1 | boot/audio/file paths (counts only) |
| `VSync`/`VSync2` (`0x424230`/`0x4242C0`, untracked) | — | 0/0 | game must vsync elsewhere (INTC/GS path, not pad/sound) |
| `sceSifMCallRpc`/`sceSifMBindRpc` (`0x40B6D0`/`0x40B3D8`, untracked) | — | 0/0 | multi-RPC lib present but unused |
| `sceSifSendCmd` direct-SPU2? | — | — | not resolvable statically (cmd id lives in packet memory) |

Key immediates: audio `BindRpc` @`0x3C20E0–0x3C20F0`: `a1=0x534E44` ("SND"-ASCII, service TBD at runtime),
`a2=0`; net `BindRpc` @`0x3F6A54`: `a1=0x237`; audio `AddCmdHandler` @`0x3C20C8`: `a0=1`.
`DNAS271.IMG` string sits next to the module table (online auth, out of scope).

## Table 2 — Fork side: status of every Table-1 call

Paths relative to fork root. `TODO_NAMED` = **throws `std::runtime_error`** on first hit
(`Unimplemented.cpp`), returns `-1` silently past the rate cap; every hit is P1w-census-counted
via `emitDrop("stub/TODO_NAMED",…)` before the throw/return.

| Call | Status | Return / behavior | Receipt |
|---|---|---|---|
| all 15 used `scePad*` | **implemented** (state machine, 2 ports × 1 slot) | `Init/PortOpen/PortClose/SetMainMode/SetButtonInfo/SetReqState/Enter+ExitPressMode=1`; `Read=1` + 32 B pad packet; `GetState`: `5`(EXECCMD once after mode cmds) else `6`(STABLE), `0` if closed; `GetReqState=reqState`; `InfoMode`: CURID/CUREXID=current (4 digital→7 analog), MODETABLE=1/0; `InfoPressMode=1`; `InfoAct`: 2 motors / per-index 1/0; `PortOpen` memsets DMA buf | `ps2xRuntime/src/lib/Kernel/Stubs/Pad.cpp:354–807` |
| `scePadSetActDirect` / `scePadSetActAlign` (rumble) | **stubbed no-op** | `return 1`, args ignored; **no host vibration call exists in-tree** (no `SetGamepadVibration`/rumble refs) | `Pad.cpp:695–707`; rumble grep §receipts |
| 13 unused `scePad*` | implemented (dead from game) | canned: `PortMax=2 SlotMax=1 ModVersion=0x200 FrameCount++ DmaStr=dmaAddr InfoComb=0 SetVrefParam=1 SetWarningLevel=0` + `*IntToStr` writers | `Pad.cpp:343–807` |
| `scePadInfoMode` unknown `a2` | **drop (canned)** | `emitDrop("stub/scePadInfoMode","unknown-info-mode")`, `return 0` | `Pad.cpp:546–554` |
| `sceSifLoadModule` (all 7 sites) | **implemented (fake registry)** | returns incrementing module id; no IRX bytes read; repeat loads refcount same id; empty path → `emitDrop` + `-1` | `Stubs/SIF.cpp:19–22` → `Syscalls/RPC.cpp:188–219` → `Syscalls/Helpers/Loader.h:78–125` |
| `sceSifInitRpc` | implemented | one-time init + debug event, `return 0` | `Stubs/SIF.cpp:692–695` → `Syscalls/RPC.cpp:221–249` |
| `sceSifBindRpc` | implemented (always succeeds) | dummy server allocated if none, `return 0`; null client → `emitDrop` + `-1` | `Stubs/SIF.cpp:466–469` → `Syscalls/RPC.cpp:251–335` |
| `sceSifCallRpc` (all 38 sites) | implemented transport, **HLE by SID** | routes to `PS2IopTransport::handleRpc`; unclaimed SID → `return 0` with send→recv copy (or zero) + `[IOP/RPC trace:unhandled]` stderr + debug event (no crash, no `emitDrop`); missing client → `emitDrop` + `-1` | `Syscalls/RPC.cpp:337–702`; unhandled `575–646`; `iop_subsystem.cpp:278–285` |
| `sceSifCheckStatRpc` | implemented | busy?1:0 (unknown client → 0) | `Syscalls/RPC.cpp:817–828` |
| `sceSifSendCmd` | implemented (memcpy) | copies `size` bytes src→dst, `return 1` (no handler dispatch) | `Stubs/SIF.cpp:24–44` |
| `sceSifAddCmdHandler` | implemented (registry) | records cid→handler, `return 0` (nothing ever invokes them) | `Stubs/SIF.cpp:439–446` |
| `sceSifInitCmd/ExitCmd/RemoveCmdHandler/InitIopHeap/AllocIopHeap/WriteBackDCache/IsAliveIop/ResetIop/SyncIop/RebootIop` | implemented (canned) | `0/0/0/0/heapAddr/0/1/1/1/1` | `Stubs/SIF.cpp:448–464, 679–695, 697–700, 737–744, 755–759, 1001–1009` |
| audio `BindRpc sid=0x534E44` | **unclaimed — silent fallback** | no IOP service claims it (core: `0x80000701/0x80000400/0x80001300`; profiles: TSNDDRV/CRI/CLFILE/SOUND-stub/SDRDRV) → copy/zero fallback + trace line | `builtin_profiles.cpp:1–144`; `modules/libsd.cpp:10`; `mcserv.cpp:17`; `dbcman.cpp:13` |
| net `BindRpc sid=0x237` | **unclaimed — silent fallback** | same fallback; no `0x237` anywhere in fork non-runner sources | same + §receipts grep |
| `sceSdRemote` / `sceSdRemoteInit` | implemented (LIBSD multiplexer) | VoiceTrans/BlockTrans/status/SetParam state machine; `RemoteInit=0` | `Stubs/Audio.cpp:77–206` |
| `sceSdCallBack` / `sceSdTransToIOP` / all `sceSSyn_*` / `sceSynthesizer*` (~90 fns) | **crash (TODO_NAMED)** | throw on first call | `Stubs/Audio.cpp` (90× `TODO_NAMED`), `Audio.h:1–101` |
| game-called `sceSd*` | none statically | the crash-stubs above are unreachable by any `jal` in the corpus | Table 1b |

P1w `[drop]`-census illumination at runtime: WILL show — 6 boot + 2 audio module loads
(`[SIF module]` log), audio `BindRpc sid=0x534E44` + every `CallRpc` (debug-event history +
`[IOP/RPC trace:unhandled]` with `sid/rpc/sendBytes`), `SendCmd` traffic (only via read log —
no per-call log), unknown `scePadInfoMode` modes (`emitDrop`), any `TODO_NAMED` crash with
`pc/ra/args`. WILL NOT show — pad happy path (no drops; observable via `getPadDebugSnapshot`
+ `readCount`), `sceSifSendCmd` contents (memcpy, no log), SIF-CMD-handler invocations (never
dispatched: `SIF.cpp:439–446` records only).

## Table 3 — Host backends (in-tree, static)

| Backend | Wired to host devices? | Receipt |
|---|---|---|
| Input: raylib gamepad (`IsGamepadAvailable(0–3)`, axes+16 buttons incl. L3/R3) + keyboard fallback (arrows, `Z/X/C/V`, `Q/E`, `1/3`, Enter/RShift, WASD analog) | yes — polled every `scePadRead` | `Stubs/Pad.cpp:85–193` (`applyGamepadState`, `applyKeyboardState`), used `Pad.cpp:298–316` |
| Input: `PSPadBackend::readState` (second mapping: gamepad 0, else keys incl. `WASD`/Space/Esc/Tab/Shift) | yes — preferred when `runtime->padBackend()` answers | `ps2_pad.cpp:28–125`; `ps2_runtime.h:465–466,504` |
| Input: scripted override (`setPadOverrideState`/`clearPadOverrideState`, debug snapshot) | test/debug only | `Pad.cpp:809–871`, `Pad.h:31–78` |
| Host window + audio device | yes — `InitWindow`, `InitAudioDevice`, `SetTargetFPS(60)` (desktop; Vita skips audio) | `ps2_runtime.cpp:700–707` |
| Host audio out: raylib `LoadWaveFromMemory→LoadSoundFromWave→PlaySound`, ≤4 concurrent, VAG→WAV (`ps2_audio_vag.cpp`), `SetSoundPitch/Volume`; Vita = compiled-out no-op | yes, but reachable only via (a) LIBSD-SID `0x80000701` `onSoundCommand`, or (b) `fioClose` VAG-magic sniff | `ps2_audio.cpp:86–139,146–308`; `FileIO.cpp:150–166`; `ps2_host_backend.h:3` (`#include "raylib.h"` — the whole file) |
| Audio for SSX3's `sid=0x534E44` | **no** — `onSoundCommand` returns unless `sid==0x80000701`; SSX3 binds `0x534E44` | `ps2_audio.cpp:150–151` |
| SDL | **no direct use** — only raylib's iOS platform backend (`PLATFORM=SDL`, prebuilt SDL2) + vita setup scripts | `ps2xRuntime/CMakeLists.txt:83–92`; `vita/{build,setup}.sh` |
| Rumble/haptics | **none** | no `Vibration`/`rumble` refs in `src/lib` (only `SLUS-20174 "Rumble Racing"` title string, `games_database.cpp:549`) |
| Mic/voice (VOIPF/LGAUD path) | **none** | no mic/USB-audio backend; net SID `0x237` unclaimed (Table 2) |
| Multitap (slot>0) | no — `kPadSlotCount=1`, `GetSlotMax=1` | `Pad.cpp:17,445–451` |

## Ordered work list

`M` = must work for MENUS, `G` = can wait for gameplay. Each row cites its Table-1 + Table-2 justification.

| # | Need | Class | Justification | Gap → exact next brief |
|---|---|---|---|---|
| 1 | Boot: 6 module loads + `scePadInit` + `sceMcInit` + RPC-init must return success | M | T1b `sub_0031ADB0` sequence (= P1b boot log) × T2 (all fake-OK today) | Verify values at runtime contact: P1w `[drop]` census + ladder boot brief (no new code expected) |
| 2 | Pad poll loop: `PortOpen→SetMainMode→InfoMode→EnterPressMode→Read/GetState/GetReqState` byte-exact (incl. pressure bytes 8–19, mode byte `0x41/0x73`) | M | T1a 13-site wrapper × T2 implemented-but-unverified values | Pad-conformance brief at runtime contact: drive menus, compare `getPadDebugSnapshot` + `Read` packets vs game reads; fix values only |
| 3 | Audio-init must not wedge boot: `sub_003C1B80` (4 loads, `BindRpc 0x534E44`, `AddCmdHandler cid=1`, `CallRpc` wrapper, `SendCmd`) | M | T1b audio graph × T2 (loads/bind OK; SID unclaimed→fallback; SendCmd memcpy; handlers never dispatched) | Runtime-trace brief: capture `[IOP/RPC trace:unhandled]` `(sid,rpc,sendBytes)` + bind/call args; then SSX3-IOP-profile brief (SNDDRV-HLE service for `0x534E44`, incl. whether SIF-CMD-1 dispatch is needed) |
| 4 | Menu BGM/SFX audibility path | M | T1b (EA `SSXAudioSystem`, `data/audio/*.big`, no libsd) × T3 (audio-out exists but gated on `0x80000701`/fio-VAG, both unreachable by SSX3 today) | Depends on #3's trace: brief an SSX3 audio-profile (route `0x534E44` traffic to `PS2AudioBackend`, or CD-streaming path via P7/`sceCdRead` lane if music comes from disc) |
| 5 | Rumble: `SetActDirect/SetActAlign/InfoAct` → host vibration | G | T1a 3 sites × T2 no-op-`1`, T3 no haptics | Gameplay-feel brief: wire raylib `SetGamepadVibration` (or platform equiv.) behind the two setters; menus don't need it |
| 6 | Net/voice: 13 IRX loads + `BindRpc 0x237` + `0x3F61D0/0x3F5DA8` chain | G | T1b net graph (online-only incl. `VOIPF/LGAUD`/DNAS) × T2 fallback-harmless | Online-play brief (post-menus): trace `0x237`, decide stub-vs-HLE; explicitly out of menu scope |
| 7 | `sceSifM*` / `VSync` / `sceSd*`-crash-stub reachability | — | T1b (0 static JALs each) | No brief: only re-open if runtime (JALR) evidence shows a hit; `TODO_NAMED` throw will announce it |
| 8 | Static naming pass (`0x3Cxxxx` audio, `0x3F4xxx–0x3F6xxx` net, `0x326xxx` pad wrapper) | — | T1a/T1b (all `sub_*`) | Optional Ghidra pass if #3/#6 stall on attribution; not on the critical path |

## Exact commands (all read-only; nothing written outside scratch + `local/research/P8/`)

```
# pins
file local/ssx3.elf; md5 local/ssx3.elf
git -C "/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp" log --oneline -2; git -C ... status --short
ls "/Volumes/Extreme SSD/ps2recomp-spike/P1/output" | wc -l   # 9277 (9261 sub_*.cpp + indexes)
# strings census
strings -a -t x local/ssx3.elf > "/Volumes/Extreme SSD/ps2x-p8/strings-x.txt"   # 28375 lines
grep -i "\.irx\|padman\|sio2man\|libsd\|snddrv\|mcman\|mcserv" strings-x.txt
grep -i "scesd\|scesdr\|sndrv\|libsdr\|spu2" strings-x.txt   # empty
# ELF layout (python3, stdlib): 1 LOAD seg; VA=off+0xFF000; gp=0x4A30F0 from .reginfo+20
# JAL census: ./jalcensus.py "$W/P1/output" /Volumes/Extreme\ SSD/ps2x-p8
#   → jal_counts.tsv (8073 targets), j_counts.tsv, jal_callers/<TGT>.txt
# string→code xrefs: ./findrefs.py local/ssx3.elf <VAs...>   # lui+addiu/ori/lw pairs
# fork side (all grep/sed/read): Stubs/Pad.cpp|Audio.cpp|SIF.cpp|RPC.cpp, Syscalls/RPC.cpp,
#   Syscalls/Helpers/Loader.h, ps2_pad.cpp, ps2_audio.cpp, ps2_iop_host.cpp,
#   ps2xIOP/src/{builtin_profiles,iop_subsystem,modules/*}.cpp, ps2_host_backend.h,
#   ps2_call_list.h, ps2_runtime.cpp:700-707, ps2_runtime.h:463-466
```

Receipt paths: full JAL tables + per-target caller lists in `/Volumes/Extreme SSD/ps2x-p8/`
(`jal_counts.tsv`, `j_counts.tsv`, `jal_callers/`, `j_callers/`); pad/sound extract in
`local/research/P8/census-pad-sound.tsv`. Disassembly windows cited by `(file, PC)` in
`/Volumes/Extreme SSD/ps2recomp-spike/P1/output/sub_*.cpp`.

## What I could not do

- Static JAL census misses `JALR`/vtable/function-pointer calls entirely: a zero count means
  "no direct call", not "never called". Runtime (P1w census + ladder) is the only closer.
- Port/slot constants, `BindRpc` client structs, `SendCmd` packet bytes, SIF-CMD-1 protocol,
  and `sid 0x534E44` / `sid 0x237` semantics are dynamic — recorded as raw immediates only.
- Could not prove a negative on statically-linked libsd/libsdr: no strings, no analyzer names,
  analyzer DB holds only `sceSdRemote*` — consistent with "EA drives SNDDRV directly", but a
  byte-signature pass would be needed to fully exclude an unnamed copy.
- No boots, no debugger, no downloads per the brief; SDL-vs-raylib and iOS-audio-wall details
  live with the I7 lane (fork HEAD `c41efce`).
