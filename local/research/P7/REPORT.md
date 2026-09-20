# P7 — Intro movies: disc survey + HLE completion stub

Standalone (P1/REPORT.md untouched; a peer brief owns it). Tables, no verdicts.

## P7-0 Rules record

| Rule | Receipt |
| --- | --- |
| No fork boots, no lease, no `adb` | 0 boots; lease file never touched; no `adb` run |
| Fork: new stub files only, named `git add` | `e235c4b`, 2 files, 203 insertions, 0 deletions; `git add` named paths only |
| `pull --rebase`, stop on foreign conflicts | Refused on unstageable generated `runner/register_functions.cpp` (P1w precedent); no foreign conflict seen; rebase never started |
| Push ONLY in fork clone to `fork` remote | `f26f273..e235c4b ssx3 -> ssx3`, fast-forward, rc=0 |
| NEVER `git push` in ssx3 | No push run in `/Users/bradrichardson/dev/ssx3` |
| Evidence `local/research/P7/` only, `git add -f`, `[P7]` prefix, trailer | This dir; commit (see P7-5) |
| 4h box | Session 21:39 → 22:06 EDT (~0.5 h) |

## P7-1a Disc survey: `.mpc` inventory

Source: extracted ISO at `$W/P1/cd` (`$W=/Volumes/Extreme SSD/ps2recomp-spike`;
ISO read-only, never written). No `.pss`/`.pms` anywhere on disc. `SYSTEM.CNF`:
`BOOT2=cdrom0:\SLUS_207.72;1`, `VER=1.00`, `VMODE=NTSC`.

| File (`DATA/MOVIES/`) | Bytes | ffprobe (`ea` demuxer) |
| --- | --- | --- |
| ABC1.MPC | 13608948 | mpeg2video 512x448 30000/1001, 1 stream |
| ABC1WS.MPC | 13605364 | mpeg2video 512x448 30000/1001, 1 stream |
| DBC2.MPC | 14857460 | mpeg2video 512x448 30000/1001, 1 stream |
| DBC2WS.MPC | 14855192 | mpeg2video 512x448 30000/1001, 1 stream |
| EABIG.MPC | 1281956 | mpeg2video 512x448 30000/1001, 1 stream |
| EBC3.MPC | 14857176 | mpeg2video 512x448 30000/1001, 1 stream |
| EBC3WS.MPC | 14857752 | mpeg2video 512x448 30000/1001, 1 stream |
| INTRO.MPC | 178170376 | mpeg2video 512x448 30000/1001, 1 stream |
| INTRO_DJ.MPC | 178170376 | mpeg2video 512x448 30000/1001, 1 stream |
| MTNALIVE.MPC | 143321576 | mpeg2video 512x448 30000/1001, 1 stream |
| NFLXSELL.MPC | 39939976 | mpeg2video 512x448 30000/1001, 1 stream |
| NFSXSELL.MPC | 26219496 | mpeg2video 512x448 30000/1001, 1 stream |
| ST3XSELL.MPC | 28613560 | mpeg2video 512x448 30000/1001, 1 stream |
| THX.MPC | 2362484 | mpeg2video 512x448 30000/1001, 1 stream |

All 14: single stream, video-only per ffprobe (no audio stream surfaced),
`Duration: N/A`. INTRO vs INTRO_DJ: same size, different bytes
(md5 `6928fd72…` vs `5293e92a…`). Full receipt: `mpc-probe.txt`.

MPC container (EABIG + spot checks; INTRO tail matches):

| Offset | Bytes | Meaning |
| --- | --- | --- |
| 0 | `MPCh` | Magic (repeats per chunk: 75× in EABIG) |
| 4 | LE u32 | Offset of first `SCHl` chunk (EABIG: `0x13ac`=5036=`SCHl` file offset) |
| 8 | `00 00 01 B3` | MPEG-2 sequence header starts immediately (all 14 files) |
| mid | `SCCl`@19440 (EABIG) | EA chunk framing inside the file |
| end-8 | `…01B7 5343456c 08000000` | MPEG seq-end, then `SCEl` + trailer |

No PS pack headers (`00 00 01 BA`: 0 in EABIG), no `01 BD`/`01 C0` private
streams: the video is one MPEG-2 elementary stream per file. Audio, if any,
rides EA chunks (`SCHl`/`SCCl`) that ffprobe does not surface as a stream.

## P7-1b ELF survey: movie-string refs + pointer tables

ELF `$W/P1/cd/SLUS_207.72` (3890784 bytes, single `PT_LOAD`
off `0x1000` VA `0x100000`, `off=0x1000+(va-0x100000)`). Method: raw-word MIPS
scan (MMI-safe; capstone chokes on `0x1C` MMI at entry) + pointer scan.

| ELF string | VA | Referenced from |
| --- | --- | --- |
| `data\movies\eabig.mpc` | 0x4612B8 | table 0x441248 (boot list) |
| `data\movies\thx.mpc` | 0x4612D0 | table 0x44124C (boot list) |
| `data\movies\intro_dj.mpc` | 0x4612E8 | table 0x441250 (boot list) |
| `data\movies\intro.mpc` | 0x461308 | table 0x441254 (boot list) |
| `data\movies\nfsxsell.mpc` | 0x460178 | table 0x441128 (sell list) |
| `data\movies\nflxsell.mpc` | 0x460198 | table 0x44112C (sell list) |
| `data\movies\st3xsell.mpc` | 0x4601B8 | table 0x441130 (sell list) |
| `data/movies/ABC1.mpc` | 0x4826C0 | replay record 0x482708 |
| `data/movies/DBC2.mpc` | 0x4826D8 | replay record 0x482724 |
| `data/movies/EBC3.mpc` | 0x4826F0 | replay record 0x482740 |
| `data/movies/ABC1ws.mpc` | 0x482760 | replay record 0x4827A8 |
| `data/movies/DBC2ws.mpc` | 0x482778 | replay record 0x4827C4 |
| `data/movies/EBC3ws.mpc` | 0x482790 | replay record 0x4827E0 |
| (MTNALIVE.MPC: no ELF ref) | — | `DATA/BE/RWRDPS2.DAT` only (data-driven) |
| `MoviePlayer` | 0x461320 | `sub_001A1CE8` (use@0x1A27F8), `sub_001D22F0` (use@0x1D23EC) |
| `RCMP::mpegbuff` | 0x4953F0 | `sub_003B0B40` (use@0x3B0EA4) |
| `PsIIlibmpeg 2700` | 0x4531B8 | version stamp, no code xref found |
| `[MPEG ERROR]%s` | 0x497CE8 | `sub_00403460` (libmpeg region) |

Boot order (table slot order; readers in `sub_001A1CE8` consume slots
low→high): eabig → thx → intro_dj → intro. Table context: slots sit in a wider
pointer table (`check5`/`check6` before, `|map_peakA/B` after). Sell table
`0x441128`: nfsxsell → nflxsell → st3xsell → NULL. Replay records: 8-word
`{pathptr,1,1,0x40000000,0x21,0,-1}` repeating per movie.

Table readers (all four boot slots read in one function):

| Reader VA | Slot | Function |
| --- | --- | --- |
| 0x1A2838/0x1A2840 | 0x441248 eabig | `sub_001A1CE8` 0x1A1CE8..0x1A2B00 (boot sequencer) |
| 0x1A285C/0x1A2864 | 0x44124C thx | `sub_001A1CE8` |
| 0x1A28D0/0x1A28DC | 0x441250 intro_dj | `sub_001A1CE8` |
| 0x1A28E0/0x1A28E8 | 0x441254 intro | `sub_001A1CE8` |
| 0x195674/0x195678 | 0x441128 sell list | `sub_00195498` |

## P7-1c ELF survey: playback API surface (JAL census)

Chain (each hop is a `jal` receipt in `elf-strings-jal.txt`/`elf-cluster.txt`):

| Hop | Caller → target | Args / notes |
| --- | --- | --- |
| 1 | `sub_001A1CE8` @0x1A2934 → `sub_002534A8@0x2534A8` | `$a0`=obj, `$a1`=stack args, `args[0]`=movie path; flag-driven select above |
| 2 | `sub_002534A8` → `jalr` factory + `sub_003ADE08`/`sub_003ADDC0` | Copies 0x38 arg bytes; path NULL/empty check; returns 1 |
| 3 | `…08`/`…C0` → `sub_003ADEC8` | Funnel (1–3 jals each) |
| 4 | `sub_003AEAD0@0x3AEAD0` → `sub_003B11A0`/`…11F0`/`…04F8`/`…0538`/`…0720` | Movie entry; NO `jal` caller in image (reached indirectly/vtable) |
| 5 | `sub_003B11A0` → `sub_003B0948` → `sub_003B0B40` | RCMP player (`RCMP::mpegbuff` use inside) |
| 6 | `sub_003B0B40` → libmpeg | `sceMpegInit@0x402708`, `sceMpegCreate@0x4027B8`, `sceMpegAddBs@0x4029D0`, `sceMpegAddCallback@0x402C08` |
| 7 | `sub_003B0FB8` → libmpeg | `sceMpegGetPicture@0x402A10` + internal `0x402B38`; self-recursive jal, no external `jal` caller |

Libmpeg `jal`-caller census (whole image): the ONLY game-code callers of wired
entries are `sub_003B0B40` (Init/Create/AddBs/AddCallback) and `sub_003B0FB8`
(GetPicture); `GetPictureRAW8/RAW8xy/GetDecodeMode` have 0 callers;
`Reset/ClearRefBuff` are called only from inside `sceMpegCreate`. No `sceMpeg*`
dynamic imports exist (libmpeg is statically linked at 0x402708+; TOML already
HLE-wires 10 entries + `_dispatchMpegCallback*` + `_ipuSetMPEG1`).

Cluster `0x3B0340–0x3B3308` externals: `sub_003E6448`/`sub_003E6574` (leaf,
libc-region), `sub_003B3D40/…3DA8/…38B8/…39D8` (upper cluster),
`sub_00417828`→`sub_0041B658`, `sub_004165A8`, `sub_00416810` (file-layer
candidates), `sub_003C0C90`/`sub_003C0E28`. Zero syscalls and zero `0x1000`
HW-`lui` in `0x3A0000–0x3C0000`: the movie path never touches IPU/GIF/DMA
registers or syscalls directly — file I/O goes through EA helpers, decode
through libmpeg. `sub_003B07F8` has a second caller: `jal@0x42E070` inside a CSV
map gap (`0x42DFF0–0x42E508` unmapped; word verified `0x0C0EC1FE`).

`sub_002534A8` has exactly 4 `jal` callers: sequencer `@0x1A2934`,
`sub_001D25E8@0x1D2610`, wrapper `sub_00253418@0x25348C`,
`sub_002838E8@0x283964`.

## P7-2 Stub

New files (fork branch `ssx3`, commit `e235c4b`; path
`ps2xRuntime/src/lib/Kernel/Stubs/`, the tree's stub home; picked up by the
existing `file(GLOB_RECURSE … src/lib/Kernel/*.cpp)` — no CMake edit):

| File | Contents |
| --- | --- |
| `Ssx3Movie.h` | Decls + hook-candidate table + wiring recipe + decoder-attach note |
| `Ssx3Movie.cpp` | `ssx3MoviePlayComplete`, `ssx3MoviePollComplete`, counter + reset test hooks |

| Handler | Contract | Return |
| --- | --- | --- |
| `ssx3MoviePlayComplete` | Blocking-play hook (primary candidate `sub_002534A8@0x2534A8`); logs path from `$a1[0]` | `$v0=1` (real body returns 1) |
| `ssx3MoviePollComplete` | Poll-style "is done?" hook | `$v0=1` (matches `sceMpegIsEnd`-true) |

Conventions followed: `ps2_stubs` namespace; TOML-stub trampoline shape (set
`$v0`, trampoline returns — same as the `sceMpeg*` handlers); stderr `[…]`
diag channel; `reset*State` test-hook pattern; `PS2_RAM_SIZE`/`PS2_SCRATCHPAD_*`
named constants. Deliberate deviation: guest reads hard-fail outside RDRAM
instead of wrapping (a wrapped read would log a garbage path). No rate limit:
brief mandates one line per invocation.

Diff receipt: `git show --stat e235c4b` = 2 files, 203+/0−; staged via two
named `git add` paths; generated `runner/register_functions.cpp` left
unstaged; no `._*` sidecars committed (purged; exFAT volume creates them).

## P7-3 Build-verify

Tree state at build: fork HEAD `f26f273` (peers' P1y/P25 already pushed) +
2 new files; sole worktree `M` = generated `runner/register_functions.cpp`.

| Check | Command (abridged) | Result |
| --- | --- | --- |
| Stub compiles + links | `cmake --build /tmp/p1-link/runtime --target ps2EntryRunner ps2x_tests -j4` | rc=0; `Ssx3Movie.cpp.o` built, linked into `libps2_runtime.a` + both executables |
| Symbols | `llvm-nm -g Ssx3Movie.cpp.o` | 4 `T ps2_stubs::ssx3Movie*` defined |
| Standalone harness (13 checks) | `/tmp/p7_movie_test` (throwaway; test-CMake is a P-lane file, not touched) | `P7-HARNESS-PASS` 13/13: `$v0`, exact log lines, null-ctx, KSEG0 alias, OOB path, reset |
| Suite (canonical CWD=fork root) | `ps2x_tests` | 427/427/0, rc=0 — no failure, nothing new |
| Suite (wrong CWD=`ps2xTest/`) | `ps2x_tests` | 427/426/1, sole failure `VU0 macro mappings… instructions.h should be readable from the test working directory` — CWD artifact, not a code failure |

Runtime behavior: explicitly UNVERIFIED (ladder stall is thread-3 poll on
`0x52BE04`; no movie stage reached; P7 runs no fork boots by design).

First-firing grep line (exact format, `n=1` marks first firing):

```text
[ssx3movie] play-complete n=1 pc=0x1a2934 ra=0x1a293c a0=0x123400 a1=0x1000 path="data\movies\eabig.mpc"
```

Future brief greps the boot log for `\[ssx3movie\]` (stderr is captured in boot
logs). Wiring recipe (NOT applied): add `X(ssx3MoviePlayComplete)` /
`X(ssx3MoviePollComplete)` to `PS2_STUB_LIST`, add
`"ssx3MoviePlayComplete@0x002534A8"` to TOML `stubs`, re-recomp. Do NOT hook
`sub_001A1CE8@0x1A1CE8` (does non-movie work around the table reads).

## P7-4 Gap rows (decoder revisit after frames)

| # | Gap | Revisit trigger |
| --- | --- | --- |
| 1 | Hook address unverified: `0x2534A8` is the best static candidate, but the real play path reaches the cluster indirectly (vtable/`jalr`); first firing may need a different hook | Ladder reaches movie stage; confirm `[ssx3movie] n=1` in boot log |
| 2 | MPC demux missing: video is raw MPEG-2 ES at file offset 8 (feeds existing FFmpeg `sceMpegAddBs` path as-is), but EA chunk framing (`SCHl`/`SCCl`, audio?) is unparsed | After frames exist: extend `Stubs/MPEG.cpp` with `MPCh` container handling or pre-demux to ES |
| 3 | Audio unknown: no audio stream in any of the 14 files per ffprobe; `SCHl`/`SCCl` chunks may carry EA audio | Decoder revisit: inspect chunk payloads; check `DATA/AUDIO` for parallel tracks |
| 4 | Streaming-open call unpinned: cluster file I/O bottoms out at EA helpers (`0x4165A8`/`0x416810`/`0x41B658`-chain, `0x3C0C90`/`0x3C0E28`); exact open/read entry not identified | Decoder revisit if stub must fake streaming (not completion) |
| 5 | Map gap `0x42DFF0–0x42E508` holds a real caller (`jal@0x42E070` → cluster); analyzer CSV incomplete there | Any future CSV-resync brief |
| 6 | No committed unit test: `ps2xTest/CMakeLists.txt` lists sources explicitly and is a P-lane file (P1y); harness lives in `/tmp` + `harness.log` here | A future brief with test-file rights ports the 13 checks to MiniTest |

## P7-5 Exact commands

From `/Users/bradrichardson/dev/ssx3` unless noted;
`$W=/Volumes/Extreme SSD/ps2recomp-spike`, `$R=$W/PS2Recomp`:

```sh
strings -a $W/P1/cd/SLUS_207.72 | grep -i -E 'mpc|movies|\.pss|mpeg|movie'
ffprobe -hide_banner $W/P1/cd/DATA/MOVIES/EABIG.MPC
python3 /tmp/p7_elf.py   # raw-word MIPS scan: string VAs, lui/xrefs, JAL census
python3 /tmp/p7_elf3.py  # pointer scan, 0x3B cluster map, callers-into-cluster
python3 /tmp/p7_elf4.py  # tables, upper cluster, gap check, MPCh-immediate scan
/opt/homebrew/opt/llvm/bin/clang++ -std=gnu++20 -O1 -DUSE_SSE2NEON \
  -o /tmp/p7_movie_test /tmp/p7_movie_test.cpp $R/ps2xRuntime/src/lib/Kernel/Stubs/Ssx3Movie.cpp \
  -I$R/ps2xRuntime/include -I$R/ps2xRuntime/src/lib/Kernel \
  -I$R/ps2xRuntime/src/lib/Kernel/Stubs -I$R/ps2xIOP/include \
  -I/tmp/p1-link/runtime/_deps/sse2neon-src -I/tmp/p1-link/runtime/_deps/raylib-src/src
/tmp/p7_movie_test                                     # 13/13 PASS
cmake --build /tmp/p1-link/runtime --target ps2EntryRunner ps2x_tests -j4   # rc=0
cd $R && /tmp/p1-link/runtime/ps2xTest/ps2x_tests      # 427/427/0
cd $R && git add ps2xRuntime/src/lib/Kernel/Stubs/Ssx3Movie.cpp \
  ps2xRuntime/src/lib/Kernel/Stubs/Ssx3Movie.h && git commit  # e235c4b
cd $R && git pull --rebase   # refused: unstaged generated runner file (P1w precedent)
cd $R && git fetch fork && git push fork ssx3   # f26f273..e235c4b, rc=0
```

## P7-6 Receipt paths

| Receipt | Path |
| --- | --- |
| This report | `local/research/P7/REPORT.md` |
| Disc probe (ls, 14× ffprobe, md5, headers) | `local/research/P7/mpc-probe.txt` |
| ELF strings/JAL/libmpeg-callers | `local/research/P7/elf-strings-jal.txt` |
| ELF pointer scan + cluster map + callers | `local/research/P7/elf-cluster.txt` |
| Harness log (13/13) | `local/research/P7/harness.log` |
| Build tail (rc=0) | `local/research/P7/build-tail.log` |
| Suite tail (427/427/0) | `local/research/P7/suite-tail.log` |
| Fork commit | `e235c4b` in fork clone `$R`, branch `ssx3` (pushed) |
| Scratch (not committed) | `/tmp/p7_elf*.py`, `/tmp/p7_movie_test*`, `/tmp/p7_suite.log`, `/tmp/p7_build.log` |

## P7-7 What I could not do

- Runtime-verify the stub: ladder has not reached any movie stage (stall
  `0x52BE04`); P7 runs no fork boots by design. Build + harness verified only.
- Wire the stub into `PS2_STUB_LIST`/TOML: existing shared files (P-lane);
  wiring an unverified hook could perturb concurrent lanes' boots. Recipe
  recorded in P7-3 and `Ssx3Movie.h`.
- Add a committed MiniTest: `ps2xTest/CMakeLists.txt` is explicitly-listed
  and under P1y's edit. Throwaway harness + log instead (gap row 6).
- Pin the streaming open/read entry and MPC audio: traced to EA helper
  frontier (gap rows 3–4); deeper dataflow left for the decoder revisit.
- Read `docs/research/review-2026-09-19-progress.md` §7.6 as a section: the
  doc's movie ask lives in §7 item 6 + §8 ("HLE stub; decoder: stub, log,
  revisit") — no §7.6 heading exists. Followed that ask.
