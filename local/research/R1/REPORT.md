# R1 report — pc-tagged reference: settler receipts (run A recompiler + run B interpreter)

Brief `local/muse/prompts/R1.md`. Tables, no verdicts. All boots ran on
bytesize; laptop-side work was ssh/scp + local reads/analysis only. Time box
2 h; session wall ~19:50–20:25 UTC 2026-09-20 (~35 min active).

Stale-reading guard: `local/research/A0/REPORT.md` §G1 (the paradox:
runtime opening events 1–25 install syscall patches while the T4/T23
reference shows ZERO `(74)/(5b)/(5a)/(64)` over the full boot — and no
static branch explains the avoidance), F3 §19 (milestone table), Part 4
decision 1 (`docs/research/review-2026-09-19-progress.md` Part 4 item 1:
three outcomes — pc-differs@3 → G1-a ExecPS2 args; pc-identical +
interpreter (74)>0 → logging artifact, fix = Part 4 item 3; else state
dependency → E3).

Headline readings: a SEPARATE pc-tagged Devel binary was built from a fresh
local clone (T4 tree clean + T4 binary sha `6719f5d6…` re-verified after the
build and after each run). Run (a) (recompiler, 120 s) and run (b)
(interpreter, 240 s) with the SAME pc-tagged binary both boot the REAL GAME
to rendered screens (rider page / in-game race) because the NVM now carries
T23's Settings-completed state — T4/T23 parked in pre-game BIOS setup (2
ExecPS2, setup screenshots, zero game pcs). Both R1 runs execute 5 ExecPS2s,
reload SLUS_207.72 (EntryPoint `0x00100008`), and fire the game's patch
installer: `(74)=18/(5b)=12/(5a)=3` IDENTICAL under recompiler and
interpreter (pcs `0x42c2f8` locator marks + `0x42c768` 8× + `0x42cbc8` 8×
with the A0 a0-sequence `5a/5b/54/55/56/57/58/59` verbatim); only `(64)`
differs (`0` vs `18164` = the known recompiler FlushCache logging skip).
Post-`ExecPS2:2` event names are identical across T4/T23/R1A/R1B (BIOS-loader
stage, not the game); the game entry is post-`ExecPS2:5`, where all 30
names+pcs+a0 match A-vs-B. Routing table in R1-2.

## R1-0. Rule record

| Item | Value |
|---|---|
| Lease | None of any kind (no lease exists for R1; P-lane lease never touched) |
| Boots on laptop | 0 (all boots on bytesize) |
| Laptop-side work | ssh/scp + local reads/analysis only |
| T4/T23 reference binary | UNTOUCHED (sha + size re-verified post-build, post-A, post-B) |
| T4 source tree | UNTOUCHED (`status --short` empty at every check; patch lives in the R1 clone) |
| R1 source tree | Separate local clone `/home/brad/pcsx2-r1/pcsx2` (one-line patch only) |
| Fork changes | 0 (no ssx3 source touched; evidence + scripts only) |
| `adb` | Not used |
| `git push` in ssx3 | Never run |
| Copyrighted downloads | None (inputs already staged; no apt installs this session) |
| `COPYFILE_DISABLE=1` | Exported on every ssh/scp step touching the SSD |
| Evidence commit | Below (`[R1]`, trailer `Orchestrated-By: Muse Code`, no push) |

Box changes on bytesize (all recorded for reproduce-from-scratch):

| Change | Value |
|---|---|
| `/home/brad/pcsx2-r1/pcsx2` (new) | Local `git clone /home/brad/pcsx2-t4/pcsx2` (rev `9056c08349…`, no submodules) + one-line patch (R1-1) + fresh `build/` (T4 flags, deps prefix `/home/brad/deps` reused read-only) |
| `/home/brad/pcsx2-r1/dat` (new) | `cp -a` of T4 datapath post-T23 (BIOS trio, NVM Settings-completed, memcards, inis); run B flips `EnableEE` here only (`PCSX2.ini.runA` keeps the pre-change ini) — T4 `dat/` never written |
| `/home/brad/pcsx2-r1/logs`, `*.jpg/*.xwd`, `r1-*.txt` | Run logs, snaps, mine outputs (this brief only) |
| `/home/brad/pcsx2-t4/r1-*.sh`, `/mnt/c/Users/bradr/pcsx2-t4/r1-*`, `emulog-r1?.txt` | Staged scripts + retrieval staging (no T4 input/config/log overwritten; T4 `dat/PCSX2/logs/emulog.txt` still the t23 trace) |
| `/tmp/.X11-unix` | tmpfs `mode=1777` mounted over WSL's dir (as root, T4 recipe) before run A; later VMs ran Xvfb on the fresh-boot dir (no mount needed) |
| Xvfb | `:99 -screen 0 1280x1024x24`, started per-run inside the run scripts, `pkill`ed at each run end |

WSL session log (btime changed 2× on idle — VMs cycle without ssh traffic, T23 precedent):

| # | UTC | Event | Receipt |
|---|---|---|---|
| 1 | 19:50:12 | VM1 starts (btime `1789933812`); build + setup + run A here | btime, run-A `UPTIME:351→488` |
| 2 | pre-A | Flaps #1–#3 (`AcceptAsync` @dmesg [21.33],[228.23],[304.19]); mount re-done after #3 (root login @[326.72]) | `r1-dmesg-preA.txt` (full) |
| 3 | 19:56–19:58 | Run A (`UPTIME:351→488`): flap-free window (completion receipts; per-run dmesg unavailable post-hoc — VM cycled on idle, see G5) | `R1A_DONE`, snap, 120 s trace, clean shutdown |
| 4 | ~20:03 | VM1→VM2 cycle on idle; run B starts at `UPTIME:1`, ends `UPTIME:258` | run-B stdout stamps |
| 5 | post-B | VM2→VM3 cycle on idle; current dmesg = fresh VM, 0 `AcceptAsync` | `r1-dmesg-post.txt` (full) |

## R1-1. Task 1 — patch + format + epochs

### Patch table (file + line + before/after + rebuild receipt)

| # | Item | Receipt |
|---|---|---|
| 1 | Clone source | `git clone /home/brad/pcsx2-t4/pcsx2 /home/brad/pcsx2-r1/pcsx2` (local, no network); rev `9056c08349cc29ad02a6d1a3a4133259019195af` (same as T4), `status` clean before patch |
| 2 | File + line | `pcsx2/R5900OpcodeImpl.cpp:917` (`grep -n "Bios call"` — single hit), in `SYSCALL()` |
| 3 | Before | `BIOS_LOG("Bios call: %s (%x)", R5900::bios[call], call);` |
| 4 | After | `BIOS_LOG("Bios call: %s (%x) pc=%x a0=%x", R5900::bios[call], call, cpuRegs.pc, cpuRegs.GPR.n.a0.UL[0]);` |
| 5 | Diff stat | 1 file, 1 insertion, 1 deletion (full diff in `r1-patch.diff`) |
| 6 | Configure | T4 flags verbatim (Devel, IPO OFF, PREFIX=/home/brad/deps, clang-18, lld, ccache, SETCAP OFF, DISABLE_ADVANCE_SIMD, USE_LINKED_FFMPEG, NO_PRECOMPILE_HEADERS); `Configuring done (12.8s)`, `Build type: Devel`; re-run `cmake_rc=0` |
| 7 | Build | `ninja -C build -j10`, 902/902, zero FAILED; `BUILD_EXIT:0`; wall ≈19:51 → 19:53:25 UTC (~2.4 min, matches T4's 2.3 min) |
| 8 | pc-tagged binary | `/home/brad/pcsx2-r1/pcsx2/build/bin/pcsx2-qt`, 130929856 B, sha256 `6069b91b1b3cce2d6291289fe6bc62cdf1eee8e749b3eebec3dd1711df8bccaf`; `PCSX2_DEVBUILD` in 495 `build.ninja` lines (same as T4) |
| 9 | T4 binary untouched | sha256 `6719f5d6ba5ac6c2c26a5954b12b837d0ff8d8e95ee6a83ed6b7b542cedee327` + 130929856 B re-verified post-build AND post-A AND post-B |
| 10 | T4 tree untouched | `git -C /home/brad/pcsx2-t4/pcsx2 status --short` empty at every check; rev `9056c08349…` |

### Run table (both runs, SAME pc-tagged binary)

| Item | Run (a) recompiler | Run (b) interpreter |
|---|---|---|
| Binary | R1 pc-tagged (`6069b91b…`) | SAME R1 pc-tagged binary |
| EE recompiler | ON (`EnableEE = true`, ini line 98) | OFF (`EnableEE = false`, sed in R1 dat copy only; `PCSX2.ini.runA` keeps the `= true` ini) |
| Flags | `-nogui -slowboot -turbo -datapath …/r1/dat -logfile …/logs/boot-r1a.log -- ISO` (T4/T23 flags verbatim; ISO = T4 input read-only) | same (`boot-r1b.log`) |
| Wall | 120 s play, SIGTERM → clean shutdown (`DEV9close`, `Unloading EGL`, `NVRAM has not changed`, `Releasing host memory`) | 240 s play, SIGTERM → clean shutdown (same markers) |
| Exit | ssh exit 0, `R1A_DONE`, WID 2097159 (`SSX 3`) | ssh exit 0, `R1B_DONE`, WID 2097159 (`SSX 3`) |
| Snap | `r1a-park.jpg` (52,096 B): RENDERED GAME SCREEN (Elise Riggs rider page) | `r1b-park.jpg` (50,793 B): RENDERED GAMEPLAY (night race scene, SSX logo) |
| Trace | `emulog-r1a.txt`: 14,574,176 lines / 991,575,587 B, sha `b9494f01…e21a95` (SSD copy sha-matched; bytesize original stays) | `emulog-r1b.txt`: 7,755,209 lines / 528,190,303 B, sha `b3ca14e…42e412` (SSD copy sha-matched; bytesize original stays) |
| EE proof | `EE/iR5900 Recompiler Reset` ×2 (lines 37, 873080) | `Recompiler Reset` count = 0 + ini `EnableEE = false` + 18,164 FlushCache lines (recompiler logs none) |
| T4 binary/tree after | sha `6719f5d6…` + 130929856 B + tree clean re-verified | sha `6719f5d6…` + 130929856 B + tree clean re-verified |

### Format table (`--format-check` on the run-(a) trace)

| # | Item | Receipt |
|---|---|---|
| 1 | Command | `python3 tools/trace_align.py --format-check /Volumes/Extreme\ SSD/ps2x-t4/emulog-r1a.txt` |
| 2 | Output | `emulog-r1a.txt: events=2914577 bad_hex=0 bad_ts_prefix=0 ts_regressions=0`, `rc=0` |
| 3 | Parser intact | `trace_align.py` `LINE_RE`/`TS_RE` match the unchanged prefix; trailing `pc=%x a0=%x` fields accepted (event count 2,914,577 = independent `grep -c "Bios call:"`) |
| 4 | Run B (bonus) | Same regexes parse 2,095,648/2,095,648 events with pc+ts (`r1-window.py`); `grep -c` agrees |

### Epoch table (`ExecPS2` anchors — events, not line numbers)

| Anchor | T4 (ref) | T23 (ref) | Run (a) | Run (b) |
|---|---|---|---|---|
| ExecPS2 #1 | line 142369, ts 0.5720 | line 142369, ts 0.8376 | line 142330, ts 0.9549, pc=0x83238, a0=0x100008 | line 155548, ts 1.2109, pc=0x83238, a0=0x100008 |
| ExecPS2 #2 | line 142465, ts 0.5996 | line 142465, ts 0.8651 | line 142426, ts 0.9823, pc=0x1001b8, a0=0x200000 | line 155603, ts 1.3851, pc=0x1001b8, a0=0x200000 |
| ExecPS2 #3/#4 | — (2 total) | — (2 total) | lines 696629/696720, ts 5.3241/5.3451, pcs 0x83238/0x10002f8, a0 0x1000008/0x100000 (post-PS2LOGO) | lines 686453/686494, ts 18.0183/18.1076 (same pcs/a0) |
| ExecPS2 #5 | — | — | line 872992, ts 9.8517, pc=0x83238, a0=0x100008 (post-SLUS reload) | line 857030, ts 35.9087, pc=0x83238, a0=0x100008 |
| Line shift | — | 0 vs T4 | −39/−39 vs T4 (equal on both anchors = pre-anchor delta; anchors are the events per brief) | n/a (slower boot) |

Loader lines run A: `SYSTEM.CNF → SLUS_207.72 NTSC` (17–19),
`cdvdLoadElf SLUS_207.72` (20), `Initializing Elf: 3890784 bytes` (21),
`ELF Loading: , EntryPoint = 0xFFFFFFFF` (138605),
`cdvdLoadElf rom0:PS2LOGO` (580678–580680, ts 5.1479),
`cdvdLoadElf SLUS_207.72 + Initializing Elf 3890784 + ELF Loading EntryPoint = 0x00100008`
(705870–705872, ts 8.7655–8.7701).
Run B: same sequence slower (`Initializing Elf` line 21, PS2LOGO ts 17.5276,
SLUS reload EntryPoint `0x00100008` line 695885 ts 34.5315, `ReBootStart`
line 155839, `sceCdInit` line 401407).
NVM receipt: R1A head shows `Time Zone Offset: GMT+04:30 / Location: Kabul`
(T23's Settings-completed state) vs T4's `GMT+00:00 / London`; head-60
otherwise identical modulo timestamps/paths (`diff_rc=1`, only ts/path/TZ
lines differ). T4/T23 stop after #2 (setup park, no PS2LOGO, no SLUS reload);
R1A/R1B continue through #5 into the game.

Landmark drift (line numbers T4 → R1A): BIOS 2→2, `cdvdRead05` 257→257,
`ELF Loading` 138643→138605 (−38), `ReBootStart` 142764→142725 (−39),
`sceCdInit` 405737→405620, first vblank 417152→417043, `LoadStartModule`
417354→417245, `UpdateVSyncRate` 456475→456189. The −39 accrues in the
SIF/CDVD storm region (storm counts are timing-dependent); post-anchor
drift grows as the boots diverge (setup park vs game boot).

## R1-2. Task 2 — settler receipts (pc + counts + routing)

### pc table 1 — post-`ExecPS2:2` events 1–10 (the brief's window = BIOS-loader stage)

Names T4/T23/R1A agree on all 10 (T4/T23 have no pc/a0 — pre-patch binary).
The event-3 row is marked `<<<`.

| ev | T4/T23 name | Run (a) name (hex) | Run (a) pc / a0 | Run (b) name (hex) | Run (b) pc / a0 | A-vs-B |
|---|---|---|---|---|---|---|
| 1 | RFU060 | RFU060 (3c) | 0x200068 / 0x2cfff0 | RFU060 (3c) | 0x200068 / 0x2cfff0 | identical |
| 2 | RFU061 | RFU061 (3d) | 0x200084 / 0x416a30 | RFU061 (3d) | 0x200084 / 0x416a30 | identical |
| 3 `<<<` | AddDmacHandler | AddDmacHandler (12) | 0x2585b8 / 0x5 | FlushCache (64) | 0x258b28 / 0x0 | DIFFER (B inserts the recompiler-skipped (64)s; B ev5 ≡ A ev3) |
| 4 | _EnableDmac | _EnableDmac (16) | 0x258608 / 0x5 | FlushCache (64) | 0x258b28 / 0x0 | shifted by the (64) insertion |
| 5 | sceSifGetReg | sceSifGetReg (7a) | 0x258cb8 / 0x80000000 | AddDmacHandler (12) | 0x2585b8 / 0x5 | shifted (≡ A ev3) |
| 6 | sceSifSetDma | sceSifSetDma (77) | 0x258c68 / 0x1ffea30 | _EnableDmac (16) | 0x258608 / 0x5 | shifted (≡ A ev4) |
| 7 | sceSifGetReg | sceSifGetReg (7a) | 0x258cb8 / 0x80000002 | sceSifGetReg (7a) | 0x258cb8 / 0x80000000 | shifted (≡ A ev5) |
| 8 | _DisableDmac | _DisableDmac (17) | 0x258618 / 0x5 | sceSifSetDma (77) | 0x258c68 / 0x1ffea30 | shifted (≡ A ev6) |
| 9 | RemoveDmacHandler | RemoveDmacHandler (13) | 0x2585d8 / 0x5 | sceSifGetReg (7a) | 0x258cb8 / 0x80000002 | shifted (≡ A ev7) |
| 10 | sceSifStopDma | sceSifStopDma (6b) | 0x258b78 / 0x1ffeb80 | _DisableDmac (17) | 0x258618 / 0x5 | shifted (≡ A ev8) |

Run A ts: 0.9919–0.9927 (files 142495–142518). Run B ts: 1.4307–1.4308
(files 155616–155639). Runtime (recomp) opening for contrast (game entry,
`syscalls-t18-on.txt`): ev1–2 RFU060/061, ev3–4 CreateSema ×2, ev5–8 OSD
Get/Set/Get/Set — its ev3 (CreateSema, A0 static pc 0x42c0f4) is game code,
not this loader stage.

### pc table 2 — game entry, post-`ExecPS2:5` (game-vs-game window)

Run A g1–g30 (files 873088–873118, ts 9.8814–9.8827) vs run B g1–g30
(files 857080–857111, ts 35.9332–35.9370). All shared names+pcs+a0 match;
B inserts exactly the two recompiler-skipped FlushCaches (g12–g13).
Runtime column = recomp opening names + A0 static pcs where read.

| A g# | B g# | Name (hex) | pc (A = B) | a0 (A = B) | Runtime ev# / name / A0 pc |
|---|---|---|---|---|---|
| 1 | 1 | RFU060 (3c) | 0x10017c | 0x4a30f0 | ev1 RFU060 / 0x100174 |
| 2 | 2 | RFU061 (3d) | 0x100198 | 0x53f115 | ev2 RFU061 / 0x100190 |
| 3 | 3 | CreateSema (40) | 0x423da8 | 0x1fffd00 | ev3 CreateSema / 0x42c0f4 |
| 4 | 4 | CreateSema (40) | 0x423da8 | 0x1fffd20 | ev4 CreateSema / 0x42c104 |
| 5 | 5 | RFU116 (74) | 0x42c2f8 | 0x83 | ev5 GetOsdConfigParam / via 0x42C3A8 |
| 6 | 6 | RFU116 (74) | 0x42c2f8 | 0x5a | ev6 SetOsdConfigParam / via 0x42C3A8 |
| 7 | 7 | (null) (83) | 0x42c1b0 | 0x80000000 | ev7 GetOsdConfigParam / via 0x42C3A8 |
| 8 | 8 | (null) (83) | 0x42c1b0 | 0x80000000 | ev8 SetOsdConfigParam / via 0x42C3A8 |
| 9 | 9 | RFU116 (74) | 0x42c768 | 0x5a | ev9 RFU116 (74) / 0x42cbf8 |
| 10 | 10 | RFU090 (5a) | 0x42c778 | 0x80076000 | ev10 RFU090 (5a) / 0x42cc10 |
| 11 | 11 | RFU090 (5a) | 0x42c778 | 0x82000 | ev11 FlushCache (64) / 0x42cc18 |
| — | 12 | FlushCache (64) | 0x424028 | 0x0 | ev12 FlushCache (64) / 0x42cc20 |
| — | 13 | FlushCache (64) | 0x424028 | 0x2 | ev13 RFU116 (74) / 0x42cc2c |
| 12 | 14 | RFU116 (74) | 0x42c768 | 0x5b | ev14 RFU116 (74) / 0x42cc38 |
| 13 | 15 | RFU091 (5b) | 0x42c7c0 | 0xfc | ev15 RFU091 (5b) / 0x42cc48 |
| 14 | 16 | RFU116 (74) | 0x42c768 | 0xfc | ev16 RFU116 (74) / 0x42cc58 |
| 15 | 17 | RFU091 (5b) | 0x42c7c0 | 0xfe | ev17 RFU091 (5b) / 0x42cc48 |
| 16 | 18 | RFU116 (74) | 0x42c768 | 0xfe | ev18 RFU116 (74) / 0x42cc58 |
| 17 | 19 | RFU091 (5b) | 0x42c7c0 | 0xfd | ev19 RFU091 (5b) / 0x42cc48 |
| 18 | 20 | RFU116 (74) | 0x42c768 | 0xfd | ev20 RFU116 (74) / 0x42cc58 |
| 19 | 21 | RFU091 (5b) | 0x42c7c0 | 0xff | ev21 RFU091 (5b) / 0x42cc48 |
| 20 | 22 | RFU116 (74) | 0x42c768 | 0xff | ev22 RFU116 (74) / 0x42cc58 |
| 21 | 23 | RFU091 (5b) | 0x42c7c0 | 0x12c | ev23 RFU091 (5b) / 0x42cc48 |
| 22 | 24 | RFU116 (74) | 0x42c768 | 0x12c | ev24 RFU116 (74) / 0x42cc58 |
| 23 | 25 | RFU091 (5b) | 0x42c7c0 | 0x8 | ev25 RFU091 (5b) / 0x42cc6c |
| 24 | 26 | RFU116 (74) | 0x42c768 | 0x8 | ev26 FlushCache (64) / 0x1001a0 |
| 25 | 27 | CreateSema (40) | 0x423da8 | 0x1fffd00 | ev27 GetThreadId (2f) |
| 26 | 28 | CreateThread (20) | 0x423ba8 | 0x1fffcd0 | ev28 ChangeThreadPriority (29) |
| 27 | 29 | StartThread (22) | 0x423bc8 | 0xc | ev29 CreateSema (40) |
| 28 | 30 | GetThreadId (2f) | 0x423c98 | 0xc | ev30 GetThreadId (2f) |

(A g29–30 = ChangeThreadPriority @0x423c38 a0=1 + WaitSema @0x423de8 a0=2,
files 873119–873120 = B g31–32, files 857112–857113, same pcs/a0 — verified
by `sed` on the SSD copies; bonus: B g33 = GetOsdConfigParam @0x423e58.)
The 42CBD0 installer's 8×(74) follow at files 873123–873136 (A) /
857118–857133 (B), a0 = `5a/5b/54/55/56/57/58/59` verbatim in both runs —
the A0 runtime a0-sequence exactly.

pc-convention join (R1 `cpuRegs.pc` at log time vs A0 static insn pcs —
systematic +8 at 5 independent sites, one convention delta, not 5 mismatches):

| Site | A0 static pc | R1 logged pc | Delta |
|---|---|---|---|
| RFU060 entry | 0x100174 | 0x10017c | +8 |
| RFU061 entry | 0x100190 | 0x100198 | +8 |
| CreateSema wrapper 0x423DA0 | 0x423da0 | 0x423da8 | +8 |
| Locator-mark wrapper 0x42C2F0 | 0x42c2f0 | 0x42c2f8 | +8 |
| 42CBD0 wrapper 0x42CBC0 | 0x42cbc0 | 0x42cbc8 | +8 |

(Runtime ev3–4 CreateSema pcs 0x42c0f4/0x42c104 are the game's jal sites;
R1 logs the wrapper+8 `0x423da8` — same call, different convention + the +8.)

### Count table (`(74)/(5b)/(5a)/(64)`, run (a) vs run (b))

Patterns (all literal, A0 lesson): `grep -c ' (74) pc='` etc. on the SSD
copies; python `r1-window.py` agrees on every cell (B64 total = 18157
post-:2 + 7 pre-:2 = 18164 — reconciled, see commands).

| Window | Run (a) n | (74) | (5b) | (5a) | (64) | Run (b) n | (74) | (5b) | (5a) | (64) |
|---|---|---|---|---|---|---|---|---|---|---|
| 30 s post-`ExecPS2:2` (brief's matched window) | 1,738,476 | 18 | 12 | 3 | 0 | 364,123 | 0 | 0 | 0 | 858 |
| Full post-`ExecPS2:2` | 2,914,416 | 18 | 12 | 3 | 0 | 2,095,479 | 18 | 12 | 3 | 18157 |
| Full-trace totals | 2,914,577 | 18 | 12 | 3 | 0 | 2,095,648 | 18 | 12 | 3 | 18164 |
| T4 / T23 full-boot totals | 899,875 / 977,568 | 0 | 0 | 0 | 0 | — | — | — | — | — |

Phase caveat on the brief's window: log-time-matched ≠ phase-matched —
run B is slower (game `ExecPS2:5` @35.91 > t0+30 = 31.39), so its 30 s
window holds no game-entry events while run A's does (game #5 @9.85).
The phase-matched comparison is the full-post row: `(74)/(5b)/(5a)`
18/12/3 in BOTH runs (all inside the game-entry burst, files 873092–873137
A / 857084–857133+ B; zero in the loader stage); only `(64)` differs.
Companion counts: `(2f)` full-post 704,988 (A) / 432,277 (B) vs T4/T23
total 2; `(83)` game-entry 2 (A) / 2 (B), printed as `(null)` (G3);
vblanks (file grep; `vblank.004` channel, not EE — G6) 397 (A) / 395 (B).

### Routing table (the three Part 4 outcomes × match/no + named next)

| # | Part 4 outcome | Test rows | Receipt | Match | Named next |
|---|---|---|---|---|---|
| 1 | pc-differs@3 → G1-a ExecPS2 args | post-:2 ev3 A-vs-B; post-:2 ev3 ref-vs-runtime | A ev3 = AddDmacHandler @0x2585b8 vs B ev3 = FlushCache @0x258b28 (differ); ref ev3 = AddDmacHandler @0x2585b8 vs runtime ev3 = CreateSema @0x42c0f4-static (differ) | ROW MATCHES — causes tabled, not assumed: (i) A-vs-B = the (64)-insertion (B ev5 ≡ A ev3, same pc/a0; B ev1–2/ev5–10 otherwise identical); (ii) ref-vs-runtime = window mismatch (BIOS-loader stage vs game entry — T4/T23/R1A ev1–10 names identical AND T4 never reaches the game) | G1-a ExecPS2 args — TABLED IN THIS REPORT (5 execs × pc/a0 × 2 runs + loader lines; R1-1 epoch table) |
| 2 | pc-identical + interpreter (74)>0 → logging artifact, fix = item 3 | game-entry g1–g30 A-vs-B pcs; B (74) count; A (74) count | all 30 game-entry names+pcs+a0 identical A-vs-B (B inserts only the dropped (64)s); B (74)=18>0; A (74)=18 (recompiler DOES log (74)/(5b)/(5a) — no artifact for these); installer a0-seq ≡ A0 runtime verbatim | MATCHES on the game-entry window (the artifact is (64)-only: 0 vs 18164) | Part 4 item 3 (trampoline fix; runtime patch path faithful on hardware) |
| 3 | else state dependency → E3 | residual after 1–2 | no residual: T4/T23 zero-(74) rows close on boot-path (setup park, 2 ExecPS2, no game pcs, setup screenshots) vs game-boot (5 ExecPS2, SLUS reload, game pcs, rendered screens); A-vs-B deltas close on the (64) skip | NO | — |

### Boot-path comparison (why T4/T23 show zero — receipts, not prose)

| Row | T4 / T23 | R1A / R1B |
|---|---|---|
| NVM | fresh / in-progress (London GMT+00) | Settings-completed (Kabul GMT+04:30) |
| ExecPS2 total | 2 | 5 (same pcs/a0 both runs) |
| PS2LOGO / SLUS reload EntryPoint 0x00100008 | absent | present (A ts 5.15/8.77; B ts 17.53/34.53) |
| Game pcs (`0x10017c/0x42xxxx`) | absent | present (patch burst + storm) |
| End screen | language / User-Prefs / DST / Settings-completed (BIOS setup) | rendered game (rider page / night race) |
| `(74)/(5b)/(5a)/(64)` totals | 0/0/0/0 | 18/12/3/0 (A), 18/12/3/18164 (B) |
| `(2f)` total | 2 | 704,988 (A) / 432,277 (B) |

## R1-3. Exact commands

Laptop (`/Users/bradrichardson/dev/ssx3` unless noted; every remote command
via `ssh bytesize 'wsl …'` (single `wsl`, no inline pipes — cmd.exe eats
them; piped logic lives in staged scripts); `export COPYFILE_DISABLE=1`
on all of these):

```text
# reuse verification (T4 pristine at start)
ssh bytesize 'wsl date -u; grep btime /proc/stat; sha256sum …/bin/pcsx2-qt; stat -c %s …; git -C … rev-parse HEAD; git -C … status --short; echo END'
# 6719f5d6…ee327 / 130929856 / 9056c08349… / empty
# source read + line number
ssh bytesize 'wsl sed -n "880,960p" …/pcsx2/R5900OpcodeImpl.cpp'
ssh bytesize 'wsl grep -n "Bios call" …/pcsx2/R5900OpcodeImpl.cpp'   # :917
# T4 build recipe + snap helper reads
ssh bytesize 'wsl cat /home/brad/pcsx2-t4/run-build.sh'
ssh bytesize 'wsl cat /home/brad/pcsx2-t4/t17-snap.sh'
# clone + patch + build (script staged per file, T4-tree-safe by construction)
scp local/research/R1/r1-build.sh "bytesize:pcsx2-t4/"
ssh bytesize 'wsl cp /mnt/c/Users/bradr/pcsx2-t4/r1-build.sh /home/brad/pcsx2-t4/r1-build.sh; ls -la …'
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/r1-build.sh'              # BUILD_EXIT:0, 902/902, 6069b91b…
ssh bytesize 'wsl git -C /home/brad/pcsx2-r1/pcsx2 diff'             # r1-patch.diff
ssh bytesize 'wsl grep -m1 Build.type …/build-config.log; grep -c FAILED …/build-build.log'
ssh bytesize 'wsl grep Configuring.done /home/brad/pcsx2-r1/build-config.log'   # done (12.8s)
ssh bytesize 'wsl cmake -B /home/brad/pcsx2-r1/pcsx2/build -S /home/brad/pcsx2-r1/pcsx2'  # cmake_rc=0
# ini survey (recompiler key)
ssh bytesize 'wsl grep -n -i recompiler …/dat/PCSX2/inis/PCSX2.ini'  # [EmuCore/CPU/Recompiler]
ssh bytesize 'wsl sed -n 95,110p …/dat/PCSX2/inis/PCSX2.ini'         # EnableEE = true
# flap + mount + datapath snapshot
ssh bytesize 'wsl dmesg' > /tmp/r1-dmesg-preA.txt                    # 3 AcceptAsync, all pre-run
scp r1-setup.sh r1-runA.sh r1-runB.sh "bytesize:pcsx2-t4/"
ssh bytesize 'wsl cp /mnt/c/Users/bradr/pcsx2-t4/r1-setup.sh /mnt/c/Users/bradr/pcsx2-t4/r1-runA.sh /mnt/c/Users/bradr/pcsx2-t4/r1-runB.sh /home/brad/pcsx2-t4'
ssh bytesize 'wsl -u root mount -t tmpfs -o mode=1777,size=10m tmpfs /tmp/.X11-unix'
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/r1-setup.sh'              # dat snapshot, EnableEE=true, TraceLog, Cross
# run A (120 s) + window analysis
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/r1-runA.sh'               # exit 0, R1A_DONE, WID 2097159
scp local/research/R1/r1-window.py "bytesize:pcsx2-t4/"
ssh bytesize 'wsl cp /mnt/c/Users/bradr/pcsx2-t4/r1-window.py /home/brad/pcsx2-r1/r1-window.py'
ssh bytesize 'wsl python3 /home/brad/pcsx2-r1/r1-window.py …/logs/emulog.txt R1A'
# run A mine + snap retrieval
scp local/research/R1/r1-mine.sh "bytesize:pcsx2-t4/"
ssh bytesize 'wsl cp /mnt/c/Users/bradr/pcsx2-t4/r1-mine.sh /home/brad/pcsx2-r1/r1-mine.sh'
ssh bytesize 'wsl bash …/r1-mine.sh R1A …/logs/emulog.txt …/r1a-mine.txt'   # 95 lines
ssh bytesize 'wsl cp …/r1a-mine.txt …/r1a-park.jpg /mnt/c/Users/bradr/pcsx2-t4'
scp "bytesize:pcsx2-t4/r1a-mine.txt" "bytesize:pcsx2-t4/r1a-park.jpg" local/research/R1/
# run B (240 s, EnableEE=false sed inside the script) + analyses
ssh bytesize 'wsl bash /home/brad/pcsx2-t4/r1-runB.sh'               # exit 0, R1B_DONE, WID 2097159
ssh bytesize 'wsl python3 /home/brad/pcsx2-r1/r1-window.py …/logs/emulog.txt R1B'
scp local/research/R1/r1-game.py "bytesize:pcsx2-t4/"
ssh bytesize 'wsl cp /mnt/c/Users/bradr/pcsx2-t4/r1-game.py /home/brad/pcsx2-r1/r1-game.py'
ssh bytesize 'wsl python3 …/r1-game.py …/logs/emulog-pre-r1b-20260920T200311Z.txt R1A5'
ssh bytesize 'wsl python3 …/r1-game.py …/logs/emulog.txt R1B5'
ssh bytesize 'wsl bash …/r1-mine.sh R1B …/logs/emulog.txt …/r1b-mine.txt'   # 18259 lines
ssh bytesize 'wsl cp …/r1b-mine.txt /mnt/c/Users/bradr/pcsx2-t4/r1b-mine.txt'
scp "bytesize:pcsx2-t4/r1b-mine.txt" local/research/R1/r1b-mine.txt
# full-trace retrieval (SSD) + sha verify
ssh bytesize 'wsl cp …/logs/emulog-pre-r1b-20260920T200311Z.txt /mnt/c/Users/bradr/pcsx2-t4/emulog-r1a.txt'
ssh bytesize 'wsl cp …/logs/emulog.txt /mnt/c/Users/bradr/pcsx2-t4/emulog-r1b.txt'
ssh bytesize 'wsl cp …/r1b-park.jpg /mnt/c/Users/bradr/pcsx2-t4/r1b-park.jpg'
scp "bytesize:pcsx2-t4/emulog-r1a.txt" "/Volumes/Extreme SSD/ps2x-t4/emulog-r1a.txt"
scp "bytesize:pcsx2-t4/emulog-r1b.txt" "/Volumes/Extreme SSD/ps2x-t4/emulog-r1b.txt"
scp "bytesize:pcsx2-t4/r1b-park.jpg" local/research/R1/r1b-park.jpg
shasum -a 256 /Volumes/Extreme\ SSD/ps2x-t4/emulog-r1[ab].txt        # b9494f01… / 3b3ca14e… match
# final remote verification
ssh bytesize 'wsl dmesg' > /tmp/r1-dmesg-post.txt                    # fresh VM, 0 AcceptAsync
ssh bytesize 'wsl sha256sum /home/brad/pcsx2-t4/pcsx2/build/bin/pcsx2-qt'   # 6719f5d6…ee327
ssh bytesize 'wsl git -C /home/brad/pcsx2-t4/pcsx2 status --short'   # empty
ssh bytesize 'wsl git -C /home/brad/pcsx2-t4/pcsx2 rev-parse HEAD'   # 9056c08349…
```

Local mining (SSD copies; `E`/`B`/`T` = r1a/r1b/boot3):

```text
python3 tools/trace_align.py --format-check "$E"                    # events=2914577 zeros rc=0
tail -n +142465 "$T" | grep -m11 "Bios call:"                       # T4 post-:2 ev0-10
head -30 /Volumes/Extreme\ SSD/ps2recomp-spike/P1/run/syscalls-t18-on.txt  # runtime opening
grep -c "Bios call: ExecPS2" "$T" ; grep -c "Bios call: .*(74|5b|5a|64)" "$T"  # 2 / 0 / 0 / 0 / 0
grep -c " (74) pc=" "$E" … (A: 18/12/3/0; B: 18/12/3/18164)
head -155603 "$B" | grep -c ' (64) pc='                             # 7 pre-:2 (reconciles 18157+7)
grep -n -m1 "BIOS Found|Initializing Elf|GameDB|Recompiler Reset|cdvdRead05|ELF Loading|…" "$E"
bash -c 'diff <(head -60 "$T"|sed …) <(head -60 "$E"|sed …)'         # ts/path/TZ lines only
python3 local/research/R1/r1-window.py "$E" R1A > local/research/R1/r1a-window.txt  # + R1B, R1A5, R1B5
sed -n '155639,155644p' "$B" ; sed -n '857111,857114p' "$B"         # B ev11-12, g31-33
```

## R1-4. Gap rows

| # | Gap | Detail |
|---|---|---|
| G1 | `0x42C758`-block caller + semantics | Fires 8×(74) + 6×(5b) + 2×(5a) on hardware between the locator scans and the 42CBD0 burst (a0 `5a/5b/fc/fe/fd/ff/12c/8`, copy dst `0x80076000` then a0=`0x82000`); A0 §(i-e) found no caller on the runtime boot path. Needs G1-a static read or E3 — R1 does not name the caller. |
| G2 | +8 pc convention | R1 `cpuRegs.pc` at log time = static insn pc + 8 at all 5 joinable sites (entry RFU060/061, 3 wrappers). Systematic; no action unless pc-equality tooling spans recomp-output pcs and PCSX2 pcs. |
| G3 | `(null) (83)` naming | PCSX2 prints the locator's scan syscall (0x83, unnamed in its table) as `(null)` — F3 §21.4 anticipated exactly this. `trace_align.py` treats `(null)` as a name; census impact none. |
| G4 | Log-time window ≠ phase window | The brief's matched 30 s post-`:2` window holds game-entry events in run A but not in run B (slower). Future A-vs-B windows should anchor on game phase (post-`#5`) — this report's full-post row is the phase-matched comparison. |
| G5 | WSL cycled 2× on idle | VM1 (build+A) → VM2 (B) → VM3 (post); per-run-window dmesg unavailable post-hoc. Pre-A dmesg = 3 pre-run flaps, mount post-flap. Run integrity carried by completion receipts (`R1A_DONE`/`R1B_DONE`, snaps, full-length traces, clean shutdowns). Precautions stand (single-shot scripts, ≤6 min runs, emulog preserved before every boot). |
| G6 | `r1-window.py` vblank blind spot | `WaitVblankStart` is a `vblank.004:` channel line, not `Bios call:` — the script counts 0; vblank counts (397 A / 395 B) are whole-file `grep -c` receipts. Script gap only; counts unaffected. |
| G7 | −39 line shift unattributed | Pre-anchor (head-60 identical modulo ts/paths/TZ; `cdvdRead05` @257 both; −38 by `ELF Loading`). Exact 39-line attribution open — storm-count timing is the standing candidate. Anchors-are-events per brief; no gate impact. |
| G8 | Session wall | ~35 min active of the 2 h box; zero lease waits (no lease exists for R1). |

## Evidence files

`REPORT.md` (this file), `r1-build.sh` (clone+patch+build), `r1-setup.sh`
(datapath snapshot), `r1-runA.sh` (120 s recompiler run), `r1-runB.sh`
(240 s interpreter run, `EnableEE=false` sed inside), `r1-window.py`
(anchors + post-`:2` events + win30 counts), `r1-game.py` (post-last-ExecPS2
events + markers), `r1-mine.sh` (excerpt miner), `r1-patch.diff` (the
one-line diff), `r1a-window.txt` / `r1b-window.txt` (19 lines each),
`r1a-game.txt` (41 lines) / `r1b-game.txt` (39 lines: zero recompiler
markers), `r1a-mine.txt` (95 lines), `r1b-mine.txt` (18,259 lines; `(64)`
section = 18,164 trace lines + 1 set-x echo),
`r1a-park.jpg` (52,096 B, rider page), `r1b-park.jpg` (50,793 B, night
race), `r1-dmesg-preA.txt` (3 pre-run flaps) / `r1-dmesg-post.txt` (fresh
VM). Full traces (NOT in git): `/Volumes/Extreme SSD/ps2x-t4/emulog-r1a.txt`
(991,575,587 B, sha `b9494f01…e21a95`) + `/Volumes/Extreme
SSD/ps2x-t4/emulog-r1b.txt` (528,190,303 B, sha `b3ca14e…42e412`) + the
bytesize originals (`/home/brad/pcsx2-r1/dat/PCSX2/logs/`).

## Tail receipt

Report written in chunks; tail verified intact (no truncation marker):

```text
$ grep -c "truncated 4166" local/research/R1/REPORT.md; tail -2 local/research/R1/REPORT.md
0
trailer `Orchestrated-By: Muse Code`, no push (orchestrator pushes at poll).
End of R1 report.
```

Commit: `git add -f local/research/R1/…` (19 files), message `[R1] …`,
trailer `Orchestrated-By: Muse Code`, no push (orchestrator pushes at poll).
End of R1 report.