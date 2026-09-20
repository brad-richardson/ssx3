# T4 report — PCSX2 Devel on bytesize + SSX3 reference trace (Brief 1: build + boot + capture)

Brief `local/muse/prompts/T4.md`. Tables, no verdicts. All boots ran on
bytesize; laptop-side work was ssh/scp only. Time box 6 h; session wall
~13:30–14:35 UTC 2026-09-20 (~2 h).

Stale-reading guard: `docs/research/review-2026-09-19-progress.md` §11.4–§12
(T4 row), `local/research/T15/REPORT.md` (park epoch: block-235 exit scale,
N = 72,176, 31-drain past block 241), P1 REPORT Part 33 (drain-termination
tables), `local/research/P1x/REPORT.md` (all: flags/channels/recipe reused).

Headline readings: Devel PCSX2 v2.9.75 built on bytesize WSL2 (2.3 min,
`PCSX2_DEVBUILD` in 495 compile lines, full EE/VU/IOP recompilers) and
booted SSX3 (USA BIOS, SLUS-20772, CRC 08FFF00D) unattended to the
language-select menu: 7,483,481-line / 528,683,584 B `EE.Bios`+`IOP.Bios`+
`IOP.cdvd`+`MISC.sif` trace over 336 s wall (22,580 vblanks), retrieved to
SSD with matching sha. The T15 drain region was not reached: the game parks
at language-select awaiting pad input (screenshot committed).

## T4-0. Rule record

| Item | Value |
|---|---|
| Lease | None of any kind (T4 has no lease; P-lane lease never touched) |
| Boots on laptop | 0 (all boots on bytesize) |
| Laptop-side work | ssh/scp + local reads/analysis only |
| Fork changes | 0 (`7eed7838`, + pre-existing foreign `M ps2xRuntime/src/runner/register_functions.cpp`, untouched) |
| `adb` | Not used |
| `git push` in ssx3 | Never run |
| Copyrighted downloads | None (BIOS+ISO are own dumps, scp'd; toolchain/apt/git only) |
| ssx3 HEAD at commit | `4303a57`, clean before evidence add |
| Evidence commit | Below (`[T4]`, trailer `Orchestrated-By: Muse Code`, no push) |

Box changes on bytesize (all recorded for reproduce-from-scratch):

| Change | Value |
|---|---|
| apt (WSL, as root) | CI list noble-adjusted (clang-18, no libfuse2) + `xvfb` + `x11-apps` + `netpbm` |
| `C:\Users\bradr\.wslconfig` (new) | `[wsl2]` `memory=10GB` (WSL was 7 GB, now 9 GB usable); revert = delete + `wsl --shutdown` |
| `/tmp/.X11-unix` | tmpfs `mode=1777` mounted over WSLg's stale read-only dir (reverts on reboot) |
| Dirs created | `/home/brad/pcsx2-t4/*`, `/home/brad/deps`, `C:\Users\bradr\pcsx2-t4\*` |
| WSLg state | Weston already down after `wsl --shutdown` (no `wslg.exe`/`weston.exe`, no `wayland-0`); Xvfb `:99` used instead, killed at teardown |

## T4-1. Task 1 — Devel build

### Survey table (bytesize over ssh)

| # | Item | Receipt |
|---|---|---|
| 1 | Host/OS/user | `bytesize`, Windows 10.0.26200.9457, `bytesize\bradr`, `C:\Users\bradr` |
| 2 | CPU | 13th Gen Intel i5-13600K, `nproc` = 20, no `avx512f` |
| 3 | GPU/driver | RTX 4070, 610.47 (Windows and WSL `nvidia-smi` agree) |
| 4 | RAM | Host 16908652544 B; WSL 9 GB usable + 3 GB swap (after cap raise) |
| 5 | Disk | C: 84–94 GB free across reads (90.26/90.25/89.87/89.71/94.03 GB); WSL `/` = `/dev/sdc` 1007G, 933G avail (sparse vhdx; real bound is C:) |
| 6 | WSL | Ubuntu 24.04.1 LTS (noble), kernel 5.15.167.4-microsoft-standard-WSL2, user `brad` (sudo needs password; root via `wsl -u root`) |
| 7 | Display | WSLg dead (see T4-0); Xvfb `:99` 1280x1024x24 + `QT_QPA_PLATFORM=xcb` |
| 8 | Windows toolchain | git ✓ (`C:\Program Files\Git\cmd\git.exe`); msbuild ✗; cmake ✗; VS2019 dir only (x86 path) → WSL cmake path chosen |
| 9 | WSL toolchain (apt) | cmake 3.28.3, ninja 1.11.1, clang 18.1.3, gcc 13.3.0, lld-18, git 2.43.0, python 3.12.3 |
| 10 | PCSX2 inputs on box (pre-existing, unused, PAL) | `Documents\PCSX2\bios\`: 14 files (30004R V6 Pal .bin 4194304/.MEC 4/.NVM 1024, rom1.bin 199680, SCPH-70004 V12 .BIN 4194304/.EROM 3145728/.NVM 1024/.ROM1 524288/.ROM2 524288, scph10000.bin 4194304/.NVM 1024, scph39001.bin 4194304/.MEC 4/.NVM 1024); `roms\` empty |

### Input table (sizes + shas both ends)

| File | Laptop (size, sha256) | bytesize WSL (size, sha256) |
|---|---|---|
| USA BIOS `.bin` | 4194304, `6d23d001…be4744` | 4194304, `6d23d001…be4744` (match) |
| USA BIOS `.mec` / `.nvm` | 4 / 1024 | 4 / 1024 (match; sha not taken, sizes only) |
| `SSX 3 (USA).iso` | 3005415424, `3c2f8eb1…9761ebf5` | 3005415424, `3c2f8eb1…9761ebf5` (match) |

Full shas: BIOS `6d23d001daf2a0fa8b381a5d49f51753c36e3622d0f04be46af1a0c548be4744`
(matches P1z/P1x); ISO `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5`
(matches `$W/P1/ref/inputs.sha256`). Transfer: scp to `C:\Users\bradr\pcsx2-t4\inputs\`,
`wsl cp` to `/home/brad/pcsx2-t4/inputs/`. BIOS installed to
`/home/brad/pcsx2-t4/dat/PCSX2/bios/` (all three files).

### Build table

| # | Item | Receipt |
|---|---|---|
| 1 | Clone | `https://github.com/PCSX2/pcsx2.git` `--recurse-submodules` → `/home/brad/pcsx2-t4/pcsx2` |
| 2 | Revision | `9056c08349cc29ad02a6d1a3a4133259019195af`, 2026-09-20 13:07:52 +0200, `describe` v2.9.75, `status` clean, `submodule status` empty (no submodules) |
| 3 | Devel support (source) | Default type Devel (`cmake/BuildParameters.cmake:57-58`); `PCSX2_DEVBUILD` for `CONFIG:Devel` (`:273`); gate `pcsx2/DebugTools/Debug.h:216-220` identical to P1x |
| 4 | Why source deps | Qt6 ≥ 6.10 required (`SearchForStuff.cmake:107`) vs noble 6.4.2; FFmpeg 7.1 required (`:25`) vs noble 6.1.1; no `libsdl3-dev`/`rapidyaml-dev` candidates → CI `build-dependencies-qt.sh` (Qt 6.11.2, FFmpeg 9.0.1, SDL3-3.4.16, shaderc 2026.2, KDD 2.4.1, …), `BUILD_FFMPEG=1`, prefix `/home/brad/deps` |
| 5 | Deps wall | 13:46:41 → 13:58:00 UTC (~11.5 min). First attempt failed at Qt APNG (script copy broke `$SCRIPTDIR`-relative patch path); resume = lines 1–110 + 283–end with `SCRIPTDIR` pinned to repo scripts dir; `NPROCS=12` (only other diff); `DEPS2_EXIT:0`; upstream clone untouched |
| 6 | Configure | CI-adapted: `Devel`, `IPO OFF` (9 GB link memory), `PREFIX=/home/brad/deps`, clang/clang++-18, `-fuse-ld=lld`, ccache, `ENABLE_SETCAP=OFF`, `DISABLE_ADVANCE_SIMD=TRUE` (moot: no AVX512), `USE_LINKED_FFMPEG=ON`; `CONFIG_EXIT:0` in 13.4 s; `Build type: Devel`, `Using tag: v2.9.75`; patches.zip/AppImage/unittests skipped |
| 7 | Build | `ninja -j10`, 902/902, zero FAILED; `BUILD_EXIT:0`; wall 13:58:27 → 14:00:43 UTC (~2.3 min) |
| 8 | Binary | `/home/brad/pcsx2-t4/pcsx2/build/bin/pcsx2-qt`, 130929856 B, sha256 `6719f5d6ba5ac6c2c26a5954b12b837d0ff8d8e95ee6a83ed6b7b542cedee327`; `-help` prints `PCSX2 v2.9.75 [Devel]`; `ldd` fully resolved (Qt/KDD/FFmpeg/SDL3 via `/home/brad/deps`) |
| 9 | Devel proof | `CMakeCache.txt` `Devel`; `PCSX2_DEVBUILD` in 495 `build.ninja` lines; `EE.Bios` emits 899,875 lines at runtime (see T4-2) |
| 10 | Recompiler proof | Boot log: `EE/iR5900 Recompiler Reset`, `iR3000A Recompiler reset.`, `mVU Reset` ×2; `R5900/R3000A/MicroVU/VIF` recompiler caches allocated |
| 11 | Sizes | `build/` 565M, `/home/brad/deps` 194M |

### Boot-smoke table

Display/runner for all: Xvfb `:99`, `QT_QPA_PLATFORM=xcb`, `-nogui -slowboot
-datapath /home/brad/pcsx2-t4/dat`. ini: `[EmuCore/TraceLog]`
`Enabled/EE.bios/IOP.bios/IOP.cdvd/MISC.sif = true`, `BIOS =
ps2-bios-0200a-20040614-100909.bin`, `EnableFastBoot = false`,
`EnableFileLogging = true` (pre-existing), `SetupWizardIncomplete = false`
(after smoke1), `EnableEEConsole/EnableIOPConsole = false` (defaults kept).

| Boot | Wall (UTC) | Exit | `-logfile` | BIOS? | ELF? | Note |
|---|---|---|---|---|---|---|
| smoke1 | 14:09:45 + 180 s | 124 (killed) | 4231 B | n/a | no | Hung in modal SetupWizardDialog (`SetupWizardIncomplete=true` + nogui has no exemption, `QtHost.cpp:2512-2517`); fixed in ini |
| smoke2 | 14:14:03 + 240 s | 124 (killed) | 4231 B | yes (implied) | yes (implied) | VM booted: memcards dir + `gl_programs.*` created 14:14:03–14:14:16; its VM log went to `emulog.txt` (overwritten by boot3) |
| boot3 (capture) | 14:18:56 + ~336 s | SIGTERM → clean shutdown | 4231 B | yes (`USA v02.00(14/06/2004)`) | yes (`ExecPS2` ×2, see T4-2) | `-turbo`; full trace in `emulog.txt` (see T4-2) |

`-logfile` finding (all three runs): the flag captures only the 4231-byte
pre-VM init log; once the VM starts, log output goes to
`dat/PCSX2/logs/emulog.txt` (fd 17 in `/proc`, all channels). The
`--help`/`--` style double-dash flags do not exist (single-dash only);
unknown args raise a modal dialog that hangs under Xvfb (two stale
`--help` processes found and killed).

## T4-2. Task 2 — reference capture (boot3)

Run: `-nogui -slowboot -turbo`, 336 s play time, SIGTERM → graceful
shutdown (`Pausing…`, DEV9close, `Unloading EGL`, `Releasing host memory`).
No errors besides the expected `patches.zip` warning (skipped download).

### Epoch table (guest events, log-time = wall since app start)

| Log time | Line | Event |
|---|---|---|
| 0.0345 | 2 | `BIOS Found: USA v02.00(14/06/2004) Console 20040614-100909` (rom1/rom2 absent, skipped) |
| 0.0359 | 13 | DVD open: 1467488 sectors × 2048 |
| 0.0360 | 20–21 | `SYSTEM.CNF` → `SLUS_207.72` NTSC v1.00; `cdvdLoadElf`; `Initializing Elf: 3890784 bytes` |
| 0.0378–0.0594 | 22–24 | GameDB 12841 games; `Disc changed to SSX 3 (USA).iso`: Serial SLUS-20772, CRC 08FFF00D; no gamesettings ini |
| 0.0598 | 34 | Memcards `Mcd001/002.ps2` 8 MB UNFORMATTED (created smoke2 14:14:03) |
| 0.0599–0.0968 | 37–39 | Recompiler resets (EE/iR5900, iR3000A, mVU ×2) |
| 0.1955 | 51 | `Opening GS…`: Vulkan `llvmpipe` probed, rejected for SW renderer; EGL/GLX llvmpipe (20 `llvmpipe-N` + 20 `GS` threads) |
| 0.3331 | 257 | First CDVD hw traffic (`cdvdRead05`) |
| 0.5499 | 138615 | First SIF lines (`dmaSIF0`/`SIF0 DMA start`) |
| 0.5503 | 138641 | First EE syscalls: `RFU060 (3c)`, `RFU061 (3d)` |
| 0.5505 | 138643 | `ELF Loading: …, EntryPoint = 0xFFFFFFFF` |
| 0.5562 | 138783 | `AddDmacHandler`/`_EnableDmac`, SIF storm begins (`sceSifGetReg` ×260,846 over 138785–404985) |
| 0.5720/0.5996 | 142369/142465 | `ExecPS2 (7)` ×2 — game ELF executed |
| 0.6101 | 142764 | IOP `ReBootStart` |
| 0.9066 | 404985 | Last `sceSifGetReg` (SIF boot storm ends 0.35 s after EE boot) |
| 0.9097 | 405737 | `sceCdInit` |
| 0.9365–0.9397 | 417152–417619 | First `WaitVblankStart`; `LoadStartModule` ×2 |
| 1.2169 | 456475 | `UpdateVSyncRate: Mode Changed to DVD NTSC` |
| ~283 (screenshot) | — | Language-select menu on screen (`Select language.` … `✕ Enter`), awaiting pad input |
| 0.94–335.87 | — | Steady menu loop: 22,580 vblanks (~67/s under turbo+llvmpipe), per-vblank `sceCdApplySCmd2` (22,551), sema/event/timer storm; 10 EE threads, 0 errors |
| 335.8734–335.9817 | 7483172–7483481 | Last guest lines (menu loop) → `Pausing…` → shutdown markers |

Drain region: not reached. The run parks at language-select awaiting ✕;
the T15 drain is deep gameplay. Reaching it needs pad-input automation
(gap row G1).

### Trace table

Trace file (all four channels interleaved by timestamp in one `emulog.txt`):

| Item | Value |
|---|---|
| bytesize path (VM sink) | `/home/brad/pcsx2-t4/dat/PCSX2/logs/emulog.txt` |
| bytesize staging copy | `C:\Users\bradr\pcsx2-t4\emulog-boot3.txt` |
| SSD copy | `/Volumes/Extreme SSD/ps2x-t4/emulog-boot3.txt` |
| Lines / bytes | 7,483,481 / 528,683,584 (all three copies identical size) |
| sha256 (bytesize + SSD) | `2433a33ea0da1e84f104d0658db251164c6dae0e1c6762b87aa997cbc259c6a5` (match) |
| Retrieval | `wsl cp` to Windows staging + `scp` home (~1 min); 529 MB < 1 GB so a home copy exists AND the bytesize original stays |
| `EE.Bios` (`Bios call: NAME (hex)`) | 899,875 lines, 42 distinct names (census in `census-final.txt`) |
| `IOP.Bios` (`lib.idx: func (a0..a3)`) | 5,095,286 lines, 103 distinct (same) |
| `MISC.sif` (`SIF : …`) | 915,373 lines |
| `/cdvd/i` outside EE/IOP classes (hw `CDVD : …` + misc) | 437,690 lines |
| Other (startup/shutdown/misc) | 135,257 lines |
| Vblanks / play time | 22,580 `WaitVblankStart` / 336 s |
| `-logfile` files (pre-VM init only) | `/home/brad/pcsx2-t4/logs/boot-smoke{1,2,3}.log`, 4231 B each |

### Sample table (verbatim from `emulog-boot3.txt`; line numbers are file lines)

First ~50 `EE.Bios` lines:

```
138641 [    0.5503] Bios    : Bios call: RFU060 (3c)
138642 [    0.5505] Bios    : Bios call: RFU061 (3d)
138783 [    0.5562] Bios    : Bios call: AddDmacHandler (12)
138784 [    0.5563] Bios    : Bios call: _EnableDmac (16)
138785 [    0.5564] Bios    : Bios call: sceSifGetReg (7a)
138786 [    0.5564] Bios    : Bios call: sceSifGetReg (7a)
138787 [    0.5564] Bios    : Bios call: sceSifGetReg (7a)
138788 [    0.5564] Bios    : Bios call: sceSifGetReg (7a)
138789 [    0.5564] Bios    : Bios call: sceSifGetReg (7a)
138790 [    0.5564] Bios    : Bios call: sceSifGetReg (7a)
138791 [    0.5564] Bios    : Bios call: sceSifGetReg (7a)
138792 [    0.5564] Bios    : Bios call: sceSifGetReg (7a)
138793 [    0.5565] Bios    : Bios call: sceSifGetReg (7a)
138794 [    0.5565] Bios    : Bios call: sceSifGetReg (7a)
138795 [    0.5565] Bios    : Bios call: sceSifGetReg (7a)
138796 [    0.5565] Bios    : Bios call: sceSifGetReg (7a)
138798 [    0.5565] Bios    : Bios call: sceSifGetReg (7a)
138799 [    0.5565] Bios    : Bios call: sceSifGetReg (7a)
138800 [    0.5565] Bios    : Bios call: sceSifGetReg (7a)
138801 [    0.5565] Bios    : Bios call: sceSifGetReg (7a)
138802 [    0.5565] Bios    : Bios call: sceSifGetReg (7a)
138803 [    0.5565] Bios    : Bios call: sceSifGetReg (7a)
138804 [    0.5565] Bios    : Bios call: sceSifGetReg (7a)
138806 [    0.5565] Bios    : Bios call: sceSifGetReg (7a)
138808 [    0.5565] Bios    : Bios call: sceSifGetReg (7a)
138810 [    0.5565] Bios    : Bios call: sceSifGetReg (7a)
138811 [    0.5565] Bios    : Bios call: sceSifGetReg (7a)
138812 [    0.5565] Bios    : Bios call: sceSifGetReg (7a)
138813 [    0.5565] Bios    : Bios call: sceSifGetReg (7a)
138814 [    0.5565] Bios    : Bios call: sceSifGetReg (7a)
138815 [    0.5565] Bios    : Bios call: sceSifGetReg (7a)
138816 [    0.5565] Bios    : Bios call: sceSifGetReg (7a)
138817 [    0.5565] Bios    : Bios call: sceSifGetReg (7a)
138818 [    0.5565] Bios    : Bios call: sceSifGetReg (7a)
138819 [    0.5565] Bios    : Bios call: sceSifGetReg (7a)
138820 [    0.5565] Bios    : Bios call: sceSifGetReg (7a)
138821 [    0.5565] Bios    : Bios call: sceSifGetReg (7a)
138822 [    0.5565] Bios    : Bios call: sceSifGetReg (7a)
138823 [    0.5565] Bios    : Bios call: sceSifGetReg (7a)
138824 [    0.5565] Bios    : Bios call: sceSifGetReg (7a)
138825 [    0.5565] Bios    : Bios call: sceSifGetReg (7a)
138826 [    0.5565] Bios    : Bios call: sceSifGetReg (7a)
138827 [    0.5566] Bios    : Bios call: sceSifGetReg (7a)
138828 [    0.5566] Bios    : Bios call: sceSifGetReg (7a)
138829 [    0.5566] Bios    : Bios call: sceSifGetReg (7a)
138830 [    0.5566] Bios    : Bios call: sceSifGetReg (7a)
138831 [    0.5566] Bios    : Bios call: sceSifGetReg (7a)
138832 [    0.5566] Bios    : Bios call: sceSifGetReg (7a)
138833 [    0.5566] Bios    : Bios call: sceSifGetReg (7a)
138834 [    0.5566] Bios    : Bios call: sceSifGetReg (7a)
```

Deepest 20 `EE.Bios` lines (menu loop, pre-shutdown):

```
7483172 [  335.8725] Bios    : Bios call: WaitSema (44)
7483197 [  335.8726] Bios    : Bios call: PollSema (45)
7483199 [  335.8726] Bios    : Bios call: SignalSema (42)
7483201 [  335.8726] Bios    : Bios call: PollSema (45)
7483203 [  335.8726] Bios    : Bios call: SignalSema (42)
7483204 [  335.8726] Bios    : Bios call: WaitSema (44)
7483205 [  335.8726] Bios    : Bios call: WaitSema (44)
7483206 [  335.8726] Bios    : Bios call: SignalSema (42)
7483207 [  335.8726] Bios    : Bios call: WaitSema (44)
7483208 [  335.8726] Bios    : Bios call: SignalSema (42)
7483217 [  335.8726] Bios    : Bios call: WaitSema (44)
7483221 [  335.8726] Bios    : Bios call: WaitSema (44)
7483449 [  335.8734] Bios    : Bios call: iReferSemaStatus (48)
7483450 [  335.8734] Bios    : Bios call: iSignalSema (43)
7483453 [  335.8734] Bios    : Bios call: RFU005 (5)
7483458 [  335.8736] Bios    : Bios call: SignalSema (42)
7483459 [  335.8736] Bios    : Bios call: WaitSema (44)
7483460 [  335.8736] Bios    : Bios call: WaitSema (44)
7483461 [  335.8736] Bios    : Bios call: SignalSema (42)
7483462 [  335.8736] Bios    : Bios call: WaitSema (44)
```

Format notes for Brief 2: EE lines carry no args/return values (name +
hex syscall number only); IOP lines carry `(a0, a1, a2, ra?)`; all lines
carry `[ seconds]` host-wall timestamps. SIF/CDVD-hw head/tail samples are
in committed `samples.txt` (§SIF FIRST 10 / DEEPEST 5, §CDVD-hw FIRST 8 /
DEEPEST 5). Epoch anchor: `ExecPS2` ×2 @142369/142465 + first vblank
@417152 + language-menu screenshot `snap-language-select.jpg`.

## T4-3. Exact commands

Laptop (`/Users/bradrichardson/dev/ssx3` unless noted; remote commands via
`ssh bytesize "…"` (Windows cmd) or `ssh bytesize 'wsl …'` (WSL)):

```
# survey
ssh bytesize "whoami & hostname & wsl --list --verbose"
ssh bytesize "wsl cat /etc/os-release" ; "wsl cmake --version" ; ninja ; git ; gcc ; nproc
ssh bytesize "wsl df -h /" ; "wsl sudo -n true" ; printenv DISPLAY/WAYLAND_DISPLAY ; "wsl ls /tmp/.X11-unix"
ssh bytesize "wsl whoami" ; "wsl -u root whoami" ; "wsl python3 --version"
ssh bytesize "wsl nvidia-smi --query-gpu=name,driver_version --format=csv"
ssh bytesize "nvidia-smi --query-gpu=name,driver_version --format=csv" ; "fsutil volume diskfree C:"
ssh bytesize "where msbuild" ; "where cmake" ; "where git"
ssh bytesize "echo %USERPROFILE%" ; "dir \"%USERPROFILE%\"" ; VS dirs ; roms ; Documents\PCSX2\bios
ssh bytesize "wsl ls /home/brad" ; "wsl free -g" ; "wsl dpkg -s qt6-base-dev"
ssh bytesize "wsl grep -m1 model.name /proc/cpuinfo" ; avx512f probe ; Win32_Processor Name
ssh bytesize "wsl uname -r"
# inputs (verify + stage)
shasum -a 256 "SSX 3 (USA).iso" ; shasum BIOS ; cat $W/P1/ref/inputs.sha256
ssh bytesize "mkdir \"%USERPROFILE%\\pcsx2-t4\"" (+ \inputs)
scp BIOS.{bin,mec,nvm} bytesize:pcsx2-t4/inputs/ ; scp ISO bytesize:pcsx2-t4/inputs/
ssh bytesize 'wsl mkdir -p /home/brad/pcsx2-t4/inputs' ; 'wsl cp /mnt/c/.../inputs/* files'
ssh bytesize 'wsl sha256sum <bios>' ; 'wsl sha256sum "<iso>"'
# clone + recipe reads
ssh bytesize "wsl mkdir -p /home/brad/pcsx2-t4"
ssh bytesize "wsl git clone --recurse-submodules https://github.com/PCSX2/pcsx2.git /home/brad/pcsx2-t4/pcsx2"
rev-parse HEAD ; log -1 --format=%ci ; describe --tags ; status ; submodule status
wsl cat linux_build_qt.yml, build-dependencies-qt.sh, linux_build_matrix.yml
wsl grep Qt6_VERSION / find_package / FFMPEG / Devel probes ; apt-cache policy probes
# box prep + toolchain
ssh bytesize "echo [wsl2] > \"%USERPROFILE%\\.wslconfig\"" ; "echo memory=10GB >> …" ; wsl --shutdown ; "wsl free -g"
ssh bytesize "wsl -u root apt-get update"
ssh bytesize "wsl -u root apt-get -y install <CI list noble-adjusted>"  (311 new, exit 0)
cmake/ninja/clang/gcc/lld --version probes
# deps (scripts scp'd: run-deps.sh, run-deps2.sh)
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/run-deps.sh'      # 13:46:41, failed at Qt APNG patch path
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/run-deps2.sh'     # 13:56:37→13:58:00, DEPS2_EXIT:0
ssh bytesize 'wsl ls /home/brad/deps/lib' ; 'wsl ls /home/brad/deps/include'
# build (script scp'd: run-build.sh)
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/run-build.sh'     # CONFIG_EXIT:0, BUILD_EXIT:0, 13:58:27→14:00:43
sha256sum build/bin/pcsx2-qt ; ls build/bin ; CMakeCache grep ; build.ninja PCSX2_DEVBUILD count ; du -sh
# display (WSLg dead; scripts scp'd: start-xvfb.sh)
ssh bytesize "tasklist /FI …wslg/weston…" ; "wsl -u root apt-get -y install xvfb x11-apps netpbm"
ssh bytesize 'wsl -u root mount -t tmpfs -o mode=1777,size=10m tmpfs /tmp/.X11-unix'
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/start-xvfb.sh'    # :99 up
# run prep (scripts scp'd: config-ini via t4-config-ini.sh)
env DISPLAY=:99 QT_QPA_PLATFORM=xcb pcsx2-qt -help           # v2.9.75 [Devel]
mkdir dat logs ; -datapath …/dat -testconfig ; dat skeleton ls -R
cp BIOS trio to dat/PCSX2/bios/ ; ini key greps ; TraceLog sed dump ; config script run
# boots (scripts scp'd: t4-boot1/2/3.sh, t4-inspect.sh)
'wsl bash …/t4-boot1.sh'   # wizard hang, 180 s, exit 124
sed SetupWizardIncomplete true→false (verified)
'wsl bash …/t4-boot2.sh'   # booted (proven post-hoc), 240 s, exit 124
'wsl bash …/t4-boot3.sh'   # background capture, PID file
'wsl -u root bash …/t4-inspect.sh'  (49 threads: CPU/MTVU/ISO/GS/llvmpipe×20; ISO+memcards+emulog fds)
# capture analysis (scripts scp'd: t4-census.py, t4-sample.py, t4-snap.sh)
grep -c/-m probes (Bios call, SIF, CDVD, module, elf, LoadExec…)
python3 t4-census.py emulog.txt [census1.txt] ; wc growth reads ; ps liveness reads
bash t4-snap.sh (xwd→jpeg) ; wsl cp snap+census to staging ; scp home ; view
wsl kill 13706 ; sleep ; pgrep ; wc final ; sha256sum final
wsl kill -9 331 424 (stale --help) ; python3 t4-sample.py … samples.txt ; census-final.txt
tail -n 30 emulog.txt ; memcards/cache/logs full-iso mtimes
wsl cp emulog→staging ; scp 529 MB home to /Volumes/Extreme\ SSD/ps2x-t4/ ; shasum verify (match)
wsl pkill Xvfb ; pgrep verify (teardown)
# local epoch mining on the SSD copy
grep -n ExecPS2/LoadStartModule/ReBootStart/sceCdInit/WaitVblankStart ; first/last sceSifGetReg
# report
mkdir local/research/T4 ; cp census-final.txt samples.txt snap1.jpg ; write REPORT.md
git add -f local/research/T4/REPORT.md local/research/T4/census-final.txt local/research/T4/samples.txt local/research/T4/snap-language-select.jpg
git commit -m "[T4] …" (trailer Orchestrated-By: Muse Code; NO push)
```

## T4-4. Gap rows (Brief 2 inputs + what I could not do)

| # | Gap | Detail |
|---|---|---|
| G1 | Input automation (blocks deeper epochs) | Run parks at language-select awaiting ✕. Reaching title/menu/gameplay (let alone the T15 drain) needs pad input: PCSX2 pad mapping + scripted keys (e.g. `xdotool` to Xvfb, or PCSX2 input APIs). Each screen needs more input; a gameplay playthrough is out of unattended scope. Proposed follower: map ✕ to a key, single-press run, screenshot-verify each new screen |
| G2 | Game printfs off | `EnableEEConsole/EnableIOPConsole=false` (defaults kept to not disturb the running capture); EE `sysPrintOut` + IOP stdout absent. A rerun with both `=true` would add game-side strings |
| G3 | `-logfile` is not the VM sink | VM channels bypass it (go to `dat/PCSX2/logs/emulog.txt`); Brief 2 must read `emulog.txt`, not `-logfile` output |
| G4 | No per-thread scheduler series | PCSX2 has no thread-switch channel (P1x-6 row b stands on master); thread events exist only as syscall names in `EE.Bios` |
| G5 | No sema ids/sites | `EE.Bios` lines carry names only; BIOS owns ids (P1x-6 row c stands) |
| G6 | Turbo+llvmpipe pace | 22,580 vblanks / 336 s ≈ 67/s; a real-GPU GS (WSLg repair or Windows-native Devel) would run faster than real-time |
| G7 | smoke2's VM log lost | Overwritten by boot3's `emulog.txt` (no rotation); smoke2's boot proven only via memcard/cache mtimes |
| G8 | `patches.zip` skipped | `Download patches` CI step omitted (needs `aria2c` + 1 download); warning-only, no boot impact |
| G9 | First-run `-testconfig` ≠ setup-complete | `-testconfig` leaves `SetupWizardIncomplete=true`, which hangs `-nogui` runs modally; must sed to `false` (done here) |
| G10 | Session wall | ~2 h active of the 6 h box; zero lease waits (no lease exists for T4) |

## Evidence files

`REPORT.md` (this file), `census-final.txt` (full EE+IOP per-name census +
markers), `samples.txt` (EE 50+20, SIF 10+5, CDVD-hw 8+5, verbatim with
file lines), `snap-language-select.jpg` (epoch proof: language menu).
Full trace: `/Volumes/Extreme SSD/ps2x-t4/emulog-boot3.txt` (528,683,584 B,
sha `2433a33e…59c6a5`, NOT in git) + bytesize original
`/home/brad/pcsx2-t4/dat/PCSX2/logs/emulog.txt` (same).
