# T24 report — pc= boot proof + GetThreadId per-site split (one short leased boot)

Brief `local/muse/prompts/T24.md`. Tables, no verdicts.
Stale-reading guard: `local/research/T22/REPORT.md` (all of it — the
`pc=` field, fork `6359fb6`, env-gated default-off, harness-proven,
boot proof deferred as gap G1 — this brief closes it) +
`local/research/A0/REPORT.md` §(iii-a) (the 21 GetThreadId call sites
whose per-site split needs `pc=` — A0 gap G4, same boot).

`W=/Volumes/Extreme SSD/ps2recomp-spike`, `R=$W/PS2Recomp` (fork,
branch `ssx3`), `RUN=$W/P1/run`,
`TRACE=$RUN/syscalls-t24-on.txt` (1,959,328 lines, 117,162,539 B,
sha `3a30c58a…0ed24`), `LOG=$RUN/boot-t24-1.log` (1,267,635 lines,
228,533,486 B, sha `3062934c…51497`),
`PLOG=$RUN/ps2_log-t24-1.txt` (94,337,564 lines, 3,350,636,222 B),
`PARK=$RUN/park-t24-1` (json 111,701 B sha `f2849613…8916b` + txt
7,643 B). `$R`-relative paths below unless noted. Zero fork changes;
no `adb`.

Headline readings: ONE pc=-on boot (600 s wall cap, BOUND=wall,
SIGTERM el=605 s rc=0, script exit 241) emits 1,959,328 events,
1,959,328 carrying `pc=` (100.0000%, head-200 200/200). Boot proof:
suffix-stripped (name,number) sequence matches T18's full 781,372-event
pc-off stream exactly, and the ts-normalized byte diff of head-781,372
minus suffix vs T18 is EMPTY (29,534,949 B each); `--format-check`
exit 0, zeros across. Site split: GetThreadId 726,490 events ALL at
one pc (`0x423c98` = wrapper `0x423C90`+8), 0 at all 21 A0 sites and 0
at all 21 site+8 ras; FlushCache 36,170 ALL at `0x424028`
(wrapper+8), 0 at steady/silent sites — `pc=` is the post-SYSCALL
dispatch pc, wrapper-internal for wrapped calls. Per-name census: 29
names, 28 single-pc, sole multi-pc AddIntcHandler (`0x423a88` ×4 +
`0x423a98` ×2). Epoch: blocks 0–119, preamble b0=961 b1=497
(T11-exact), 222 ×118; block 235 not reached (collapse: no; capture
window labeled). Rates (wall-approx): GetThreadId 20.18/VBLANK,
FlushCache 1.005/VBLANK.

## T24-0. Lease / tree-state / build record

| Item | Value |
|---|---|
| ssx3 HEAD at T24 start | `b7a12f0`, clean |
| ssx3 HEAD at claim/boot/release | `b7a12f0`, clean (no mid-boot motion until commit) |
| ssx3 HEAD at commit | `6810155` pre-commit (`[T23] …`; T23 landed post-release, offline, no P-lane interaction) |
| Fork HEAD throughout | `6359fb6` (T22's commit) + `M ps2xRuntime/src/runner/register_functions.cpp` (foreign, untouched) |
| Fork commits by T24 | 0; fork `git pull/push`: never run |
| Sidecars | 51 (`find $R -name "._*"`; T22's 31 → 51 tabled, untouched per zero-change rule; no build run) |
| Rebuild | NONE (tree at T22 boot state; binary sha AND size identical — no build run) |
| Binary | `7f155f4cac62466c2535bc6987f64e0d2d31586ab21dd6b63c6a9998febdb377`, 163,464,560 B (IDENTICAL to T22) |
| Boot env | T18-ON verbatim + `PS2X_TRACE_SYSCALLS_PC=1`; both gates recorded (`PS2X_TRACE_SYSCALLS=$RUN/syscalls-t24-on.txt`, `PS2X_TRACE_SYSCALLS_PC=1`); script diff = LOG/TRACE/PARK names + `SECS` 240→600 + `EVENT_CAP`/`POLL` + PC gate + polling loop (diff-verified vs `/tmp/t18-boot-on.py`) |
| Monitor | liveness-only in-script (15 s polls to stdout + `/tmp/t24-liveness.log`, 40 polls + SIGTERM line; no trigger) |
| Caps | wall 600 s + progress 2,000,000 trace lines (first brief under the progress-cap rule); BOUND=wall (1,959,058 at last poll, 1,959,328 final) |
| Boots | 1 of 1 used (capture boot; ≤600 s foreground) |
| Wall | 2026-09-20 ~19:12–19:35Z (~0.5 h active), inside the 4 h box |
| ssx3 evidence commit | below (`[T24]`, trailer `Orchestrated-By: Muse Code`, no push) |

pc= linkage IN the linked binary (E2a G1 lesson — verified before
claiming; all receipts against `/tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner`):

| # | Receipt | Value |
|---|---|---|
| 1 | `strings` format literals | BOTH present: `[%8.4f] Bios    : Bios call: %s (%x) pc=0x%x` (on) + `[%8.4f] Bios    : Bios call: %s (%x)` (off) |
| 2 | `strings` gates | `PS2X_TRACE_SYSCALLS` ×1 + `PS2X_TRACE_SYSCALLS_PC` ×1 (T22's table row said ×2+1; the linked binary holds 1+1 — recorded, no rebuild) |
| 3 | `nm` symbol (demangled) | `ps2_syscalls::traceChannelEmit(unsigned int, unsigned int)` (T text) + `TraceChannelState` ctor/dtor |
| 4 | `otool -v -t` disassembly | `bl traceChannelEmit` call site in dispatcher + function prologue with gate branches (`tbz`/`cbz` on the cached gates) |

Lease record (`$RUN/t24-waits.log`, 2 lines; zero contention —
absent at claim, zero WAIT lines):

| Event | Value |
|---|---|
| T24 pre-claim checks (19:14:44Z) | Lease absent; `pgrep -x ps2EntryRunner` exit 1; sha `7f155f4c…` 163464560 B; ISO 3005415424 B + ELF 3890784 B (`P1/SLUS_207.72` and `P1/cd/SLUS_207.72` both 3890784; boot ELF = cd path); 499 Gi free; selftest 35/35; t20/e2a-waits tails = released |
| T24 claim | `printf 'T24\n' > /tmp/ssx3-p-lane-lease` 19:14:44Z |
| Boot | start ~19:15Z; 40 liveness polls (trace 48,538 → 1,959,058 lines, log → 228,532,904 B); SIGTERM el=605 s rc=0 BOUND=wall, script exit 241 |
| T24 release | 19:25:00Z (held 616 s); verified absent; `pgrep -x` exit 1 |
| Trace copy (lease-free) | `ps2_log.txt` → `ps2_log-t24-1.txt` (94,337,564 lines, 3,350,636,222 B); TRACE/LOG/PARK written direct by the runner |

## T24-1. Task 1 — capture boot + epoch table (T16 exit shape to cap?)

Boot artifacts (all `$RUN`):

| Item | Value |
|---|---|
| `boot-t24-1.log` | 1,267,635 lines, 228,533,486 B, sha `3062934c9d1c140bbaadb060e302432910a22b2f3a7813ace17c522c47851497` |
| `syscalls-t24-on.txt` | 1,959,328 lines, 117,162,539 B, sha `3a30c58a12aefe68beacfa3654e08f9c61a051c2f642ea1619e0dca12ea0ed24` |
| `ps2_log-t24-1.txt` | 94,337,564 lines, 3,350,636,222 B (lease-free copy) |
| `park-t24-1/` | json 111,701 B sha `f28496131532aaabd76b7169528344882a04a92697a7d97424b797eb2fb8916b` + txt 7,643 B (+ 2 macOS `._*` sidecars, gap G7) |
| `[trace:syscalls]` open line in log | present (`open path=…/syscalls-t24-on.txt`; channel-on receipt) |
| Rate | 1,959,328/600 s = 3,265.5 events/s (T18: 781,372/240 = 3,255.7/s) |

Epoch table (`[diag:stubs]` series, 120 lines, blocks 0–119;
capture boot, not exit boot — window labeled):

| Block | Stub distinct | Note |
|---|---|---|
| 0 | 961 | preamble (T11-exact pair) |
| 1 | 497 | preamble (T11-exact pair) |
| 2–119 | 222 ×118 | phase steady, no deviation |

| # | Check (T16 §T16-1 wording, block-235 collapse only) | Receipt | Reading |
|---|---|---|---|
| 1 | Block 235 present with distinct 218 | max block = 119; block 235 absent | no (not reached, not contradicted) |
| 2 | Preamble pair | b0=961, b1=497 | T11-exact pair |
| 3 | Steady distinct | 222 ×118 blocks 2–119 | in-phase throughout the window |

## T24-2. Task 2 — boot proof + site split (what does pc= show?)

### Proof table (pc= boot proof — T22 G1)

| # | Item | Receipt |
|---|---|---|
| 1 | pc-on stream | 1,959,328 events, 117,162,539 B; head-200 200/200 carry `pc=`; full-file 1,959,328/1,959,328 (100.0000%), 0 unparseable (`proof.txt`) |
| 2 | Suffix-stripped sequence vs T18 | (name,number) sequence, ts ignored: exact-match run = 781,372 = ALL of T18's pc-off stream (`prefix_status=T18-exhausted-T24-longer`; zero divergence in the shared window) |
| 3 | Ts-normalized byte diff | head-781,372 minus ts minus `pc=` suffix vs T18 minus ts: `cmp` EMPTY (29,534,949 B each) |
| 4 | `--format-check` | `syscalls-t24-on.txt`: events=1959328 bad_hex=0 bad_ts_prefix=0 ts_regressions=0, exit 0 (T22 parser-compat row holds on boot lines) |

On-shape boot sample (first 5 lines of `TRACE`, verbatim; `head200.txt`
holds the first 200):

```text
[  0.0000] Bios    : Bios call: RFU060 (3c) pc=0x10017c
[  0.0000] Bios    : Bios call: RFU061 (3d) pc=0x100198
[  0.0001] Bios    : Bios call: CreateSema (40) pc=0x423da8
[  0.0001] Bios    : Bios call: CreateSema (40) pc=0x423da8
[  0.0002] Bios    : Bios call: GetOsdConfigParam (4b) pc=0x423e58
```

### Mechanism table (what pc= holds — dispatch pc, post-SYSCALL)

`pc=` = guest pc of the instruction AFTER the SYSCALL insn at dispatch
(wrapper+8 for wrapped calls: addiu @+0, SYSCALL @+4, next @+8;
direct sites likewise SYSCALL+4). Join of A0 wrapper pcs with census pcs:

| Syscall | Wrapper/site pc (A0) | Stream pc= | Offset |
|---|---|---|---|
| RFU060 (3c) | site `0x100174` | `0x10017c` | +8 (SYSCALL+4) |
| RFU061 (3d) | site `0x100190` | `0x100198` | +8 (SYSCALL+4) |
| GetThreadId (2f) | wrapper `0x423C90` | `0x423c98` | +8 |
| WaitSema (44) | wrapper `0x423DE0` | `0x423de8` | +8 |
| SignalSema (42) | wrapper `0x423DC0` | `0x423dc8` | +8 |
| FlushCache (64) | wrapper `0x424020` | `0x424028` | +8 |
| RFU116/SetSyscall (74) | wrapper `0x42CBC0` | `0x42cbc8` | +8 |
| RFU091 (5b) | wrapper `0x42CBB0` | `0x42cbb8` | +8 |
| RFU090/Copy (5a) | wrapper `0x42CB68` | `0x42cb70` | +8 |

### Site-split table (GetThreadId 726,490 events — A0 iii-a 21 sites)

All 726,490 events carry `pc=0x423c98` (wrapper+8, 100.000%);
0 at every site pc and 0 at every site+8 ra (`sites.txt`):

| # | Call site | Enclosing function | At site | At ra (site+8) | Share |
|---|---|---|---|---|---|
| 1 | `0x31ab4c` | `sub_0031AAF0` | 0 | 0 | 0% |
| 2 | `0x31a734` | `sub_0031A6B8` | 0 | 0 | 0% |
| 3 | `0x320b10` | `sub_00320550` | 0 | 0 | 0% |
| 4 | `0x3c1fbc` | `sub_003C1B80` | 0 | 0 | 0% |
| 5 | `0x3c3390` | `sub_003C3380` | 0 | 0 | 0% |
| 6 | `0x3c33e8` | `sub_003C33E0` | 0 | 0 | 0% |
| 7 | `0x3e5020` | `sub_003E5018` | 0 | 0 | 0% |
| 8 | `0x3e53f4` | `sub_003E5398` | 0 | 0 | 0% |
| 9 | `0x3e5418` | `sub_003E5398` | 0 | 0 | 0% |
| 10 | `0x3e570c` | `sub_003E5700` | 0 | 0 | 0% |
| 11 | `0x3e5738` | `sub_003E5700` | 0 | 0 | 0% |
| 12 | `0x3e576c` | `sub_003E5760` | 0 | 0 | 0% |
| 13 | `0x3e52f4` | `sub_003E52B0` | 0 | 0 | 0% |
| 14 | `0x3e533c` | `sub_003E52B0` | 0 | 0 | 0% |
| 15 | `0x3e5360` | `sub_003E52B0` | 0 | 0 | 0% |
| 16 | `0x3e51bc` | `sub_003E51A0` | 0 | 0 | 0% |
| 17 | `0x3e544c` | `sub_003E5440` | 0 | 0 | 0% |
| 18 | `0x3e54c0` | `sub_003E5440` | 0 | 0 | 0% |
| 19 | `0x3e5538` | `sub_003E5440` | 0 | 0 | 0% |
| 20 | `0x3f4740` | `sub_003F4528` | 0 | 0 | 0% |
| 21 | `0x418cb8` | `sub_00418CA8` | 0 | 0 | 0% |
| — | `0x423c98` (wrapper+8) | `sub_00423C90` | 726,490 | — | 100.000% |

| # | Brief question | Tabled answer |
|---|---|---|
| 1 | Which sites carry the 20/VBLANK? | Unattributable via `pc=`: distinct_pc=1 (all 21 sites 0/0); per-site split needs call-site ra, not dispatch pc (gap G1) |
| 2 | SYNCTASK cluster share? | 0 attributable via `pc=`; A0's park ras (`0x3e5028`/`0x3e5774`, both SYNCTASK-cluster) remain the only attribution — unconfirmed and undenied by this stream |
| 3 | Rate | 726,490/600 s/60 = 20.18/VBLANK (wall-approx; T18: 290,210/240/60 = 20.15); density 726,490/1,959,328 = 37.07% (T18: 37.13%) |

### FlushCache table (36,170 events — A0 iii-b sites)

All 36,170 events carry `pc=0x424028` (wrapper `0x424020`+8,
100.000%); 0 at every site pc and 0 at every site+8 ra (`flush.txt`):

| Call site | Enclosing function | Class | At site | At ra |
|---|---|---|---|---|
| `0x1001a0` | entry | boot | 0 | 0 |
| `0x42cc18` | `sub_0042CBC0` | boot | 0 | 0 |
| `0x42cc20` | `sub_0042CBC0` | boot | 0 | 0 |
| `0x42c460` | `sub_0042C410` | dead | 0 | 0 |
| `0x42c468` | `sub_0042C410` | dead | 0 | 0 |
| `0x382930` | `sub_00382760` | steady | 0 | 0 |
| `0x2ec5f0` | overlap 2EC418/2EC478 | silent? | 0 | 0 |
| `0x37c0c8` | ? | silent? | 0 | 0 |
| `0x3837a8` | ? | silent? | 0 | 0 |
| `0x391404` | ? | silent? | 0 | 0 |
| `0x39134c` | ? | silent? | 0 | 0 |
| `0x3c1b18` | ? | silent? | 0 | 0 |
| `0x3c4410` | ? | silent? | 0 | 0 |
| `0x3e4144` | ? | silent? | 0 | 0 |
| `0x3f4f7c` | ? | silent? | 0 | 0 |
| `0x3f4fb0` | ? | silent? | 0 | 0 |
| `0x3f5210` | ? | silent? | 0 | 0 |
| `0x3f52c4` | ? | silent? | 0 | 0 |
| `0x3f5528` | ? | silent? | 0 | 0 |
| `0x3fd0ac` | ? | silent? | 0 | 0 |
| `0x3fd0b4` | ? | silent? | 0 | 0 |
| `0x40359c` | ? | silent? | 0 | 0 |
| `0x424028` (wrapper+8) | `sub_00424020` | — | 36,170 | — |

| # | Brief question | Tabled answer |
|---|---|---|
| 1 | Steady state really only `0x382930`? | Unobservable via `pc=` (distinct_pc=1; steady site 0/0) — neither confirmed nor denied |
| 2 | Silent-site activity? | Unobservable via `pc=` (all 16 silent candidates 0/0; any issuer collapses to `0x424028`) |
| 3 | Rate | 36,170/600 s/60 = 1.005/VBLANK (wall-approx; T18: 14,356/240/60 = 0.997) |

### pc census table (per-name distinct pcs — `pccensus.txt`)

29 names; 28 single-pc (each its wrapper+8); sole multi-pc row last:

| Name | Count | distinct_pc | pc= value(s) |
|---|---|---|---|
| GetThreadId (2f) | 726,490 | 1 | `0x423c98` |
| WaitSema (44) | 580,181 | 1 | `0x423de8` |
| SignalSema (42) | 471,280 | 1 | `0x423dc8` |
| iSignalSema (43) | 108,895 | 1 | `0x423dd8` |
| FlushCache (64) | 36,170 | 1 | `0x424028` |
| PollSema (45) | 36,164 | 1 | `0x423df8` |
| CreateSema (40) | 37 | 1 | `0x423da8` |
| RFU252 (fc) | 21 | 1 | `0x423b28` |
| DeleteSema (41) | 21 | 1 | `0x423db8` |
| GetOsdConfigParam (4b) | 9 | 1 | `0x423e58` |
| RFU116 (74) | 8 | 1 | `0x42cbc8` |
| RFU091_GetEntryAddress (5b) | 6 | 1 | `0x42cbb8` |
| AddIntcHandler (10) | 6 | 2 | `0x423a88` ×4 + `0x423a98` ×2 |
| _EnableIntc (14) | 6 | 1 | `0x423ae8` |
| CreateThread (20) | 5 | 1 | `0x423ba8` |
| StartThread (22) | 5 | 1 | `0x423bc8` |
| _DisableIntc (15) | 5 | 1 | `0x423af8` |
| ChangeThreadPriority (29) | 3 | 1 | `0x423c38` |
| EndOfHeap (3e) | 3 | 1 | `0x423d88` |
| GetOsdConfigParam2 (6f) | 3 | 1 | `0x4240b8` |
| SetOsdConfigParam (4a) | 2 | 1 | `0x423e48` |
| RFU060 (3c) | 1 | 1 | `0x10017c` |
| RFU061 (3d) | 1 | 1 | `0x100198` |
| RFU090_iReferEventFlagStatus (5a) | 1 | 1 | `0x42cb70` |
| ReferThreadStatus (30) | 1 | 1 | `0x423ca8` |
| _DisableDmac (17) | 1 | 1 | `0x423b18` |
| AddDmacHandler (12) | 1 | 1 | `0x423ac8` |
| _EnableDmac (16) | 1 | 1 | `0x423b08` |
| SleepThread (32) | 1 | 1 | `0x423cc8` |

## T24-3. Exact commands

From `/Users/bradrichardson/dev/ssx3` unless noted; `$R`, `$W` quoted
(path contains a space):

```text
# Recon (lease-free, read-only streams)
read local/research/T22/REPORT.md (all) + local/research/A0/REPORT.md (all, iii-a focus)
read local/research/T13/REPORT.md (T13-0 shape) + T16/T18 heads (exit shape, boot recipe)
ls -la; no Makefile/Taskfile/package.json/CI/lint configs (no gate applies; selftest is the gate)
git rev-parse HEAD (b7a12f0) + status (clean); fork rev-parse (6359fb6) + status (foreign M only)
shasum binary (7f155f4c…b377 163464560B = T22, no rebuild)
strings both pc literals + nm traceChannelEmit(u32,u32) + otool call+gate disasm (pre-boot linkage)
stat ISO 3005415424 + ELF 3890784 (both ELF paths); df 499Gi free
python3 tools/trace_align.py --selftest (35/35 + ALL PASS)
tail t20/e2a/t18-waits.log (released/released/released)
# Boot script (lease-free)
write /tmp/t24-boot1.py (sed from /tmp/t18-boot-on.py: names + SECS 240->600
  + EVENT_CAP=2000000 + POLL=15 + PS2X_TRACE_SYSCALLS_PC=1 + poll loop w/ BOUND)
py_compile; diff vs /tmp/t18-boot-on.py (verified)
write + py_compile /tmp/t24-proof.py /tmp/t24-sites.py /tmp/t24-flush.py /tmp/t24-epoch.py /tmp/t24-pccensus.py
# Boot (lease T24 held 19:14:44-19:25:00Z, 616 s)
pre-claim checks; printf 'T24' > /tmp/ssx3-p-lane-lease; append t24-waits.log CLAIM
python3 /tmp/t24-boot1.py (foreground; 40 polls; SIGTERM el=605s rc=0 BOUND=wall, exit 241)
rm /tmp/ssx3-p-lane-lease (verified absent; pgrep 1); append t24-waits.log RELEASE
# Analysis (lease-free)
cp ps2_log.txt ps2_log-t24-1.txt (94337564 lines, 3350636222 B)
shasum TRACE (3a30c58a…0ed24) + LOG (3062934c…51497) + park json (f2849613…8916b)
--format-check TRACE (1959328 ev, zeros, exit 0)
t24-proof.py (100.0000% pc; run 781372 = all T18) + head-781372 stripped cmp vs T18 (EMPTY)
t24-sites.py (726490 @0x423c98, 21x0/0) + t24-flush.py (36170 @0x424028, 22x0/0)
t24-epoch.py (blocks 0-119; 235 absent) + t24-pccensus.py (29 names; AddIntcHandler 4+2)
grep AddIntcHandler pc split (4/2); head-200 pc share (200/200)
# Evidence
stage 7 txt to local/research/T24/ (proof/sites/flush/epoch/pccensus/head200/liveness)
write REPORT.md in 4 chunks; tail receipt; git add -f local/research/T24/; commit [T24] (no push)
```

## T24-4. Gap rows

| # | Gap | Detail |
|---|---|---|
| G1 | A0 G4 NOT closed by this stream | `pc=` is the post-SYSCALL dispatch pc: all 21 GetThreadId call sites funnel through wrapper `0x423C90` → single `0x423c98` (726,490/726,490); per-site split needs call-site ra (an `ra=` field or equivalent) — future brief |
| G2 | FlushCache steady-vs-silent unobservable | Single `0x424028` (36,170/36,170); `0x382930`-only steady state + silent-site activity neither confirmed nor denied |
| G3 | T22 G1 CLOSED | Boot proof: full-T18-window sequence parity (781,372/781,372) + ts-normalized byte diff EMPTY + on-shape boot lines 100% + `--format-check` exit 0 |
| G4 | AddIntcHandler dual-pc mechanism untabled | `0x423a88` ×4 + `0x423a98` ×2 (sole multi-pc name); two wrappers vs branched wrapper needs an OUT grep (lease-free static) |
| G5 | Block-235 collapse unobserved | 600 s window ends at block 119; T16 exit shape holds-to-cap vacuously (no contradiction, no observation) |
| G6 | Sidecars 51 (T22: 31) | Untouched per zero-change rule; no build run, no interaction |
| G7 | Park-dir AppleDouble pair | `._park-snapshot.json` + `._park-snapshot.txt` (macOS-created, runner-external); snapshot bytes unaffected |
| G8 | Session wall | ~0.5 h active of the 4 h box; zero lease waits (absent at claim) |

## Evidence files

`REPORT.md` (this file), `proof.txt` (4-line proof-miner output),
`sites.txt` (27-line GetThreadId split), `flush.txt` (26-line
FlushCache split), `epoch.txt` (8-line stub series), `pccensus.txt`
(31-line per-name census), `head200.txt` (200-line pc-on head),
`liveness.txt` (42-line boot liveness + BOUND). Full-size artifacts
stay on the SSD by path+sha: `syscalls-t24-on.txt` (117,162,539 B),
`boot-t24-1.log` (228,533,486 B), `ps2_log-t24-1.txt`
(3,350,636,222 B), `park-t24-1/` (111,701 + 7,643 B), binary
`7f155f4c…b377` (163,464,560 B).

## T24-5. Tail receipt (F3 rec 17)

Report written in 4 chunks; closing 3 lines quoted verbatim below
(`tail -3 local/research/T24/REPORT.md` at commit):

```text
T24 evidence complete: pc= boot proof + wrapper-pc site tables (A0 G4 needs ra=).
Trailer: Orchestrated-By: Muse Code.
End of T24 report.
```

T24 evidence complete: pc= boot proof + wrapper-pc site tables (A0 G4 needs ra=).
Trailer: Orchestrated-By: Muse Code.
End of T24 report.
