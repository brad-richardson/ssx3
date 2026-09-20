# T22 report — Aligner projection + milestones + channel pc= field (no boots, no lease)

Brief `local/muse/prompts/T22.md`. Tables, no verdicts.
Stale-reading guard: `local/research/T18/REPORT.md` (all of it — the
aligner + channel this brief extends), F3 rec 14 (this brief:
`--drop-names`/`--project shared`, `--milestones`; channel `pc=` field;
both env-gated, PCSX2 shape default) and F3 §19 (the hand-made milestone
table — `--milestones` output reproduces its rows mechanically, match/no
per row in §T22-1). Ran beside A0; no dependency either way.

`W=/Volumes/Extreme SSD/ps2recomp-spike`, `R=$W/PS2Recomp` (fork, branch
`ssx3`). `$R`-relative paths below unless noted. No `adb`.

Headline readings: `tools/trace_align.py` gains `--drop-names N,...` +
`--project shared` (the 15-name F3 §19 projection) + `--milestones`
(stamped rare-vocabulary sequences both sides); selftest 34/34 (old 17/17
still green, default output byte-identical to T18's `align-boot3.txt`).
Projected boot3-vs-t18: ref 899,713 → 2,317 milestones, rt 781,372 → 148,
k=2 projected (same events), all 10 §19 rows reproduced modulo 3 tabled
projection-blind spots (FlushCache×3, RFU005, in-window SleepThread count)
+ 1 unisolable hand-scoped sema pair. Channel gains `pc=0x%x` per line,
gated on `PS2X_TRACE_SYSCALLS_PC` (unset/empty = off = T18 byte shape);
harness through the real emit path: off-output ts-normalized diff vs T18
head-200 EMPTY, on-output 200/200 carry `pc=`, both parse exit 0. Fork
`-j4` build exit 0, binary `7f155f4c…b377` 163,464,560 B. Zero boots, zero
lease: full-boot off-diff + on-shape boot lines deferred to the next
leased boot brief (gap G1).

## T22-0. Rule record

| Item | Value |
|---|---|
| ssx3 HEAD at T22 start | `ca03bad` (`[orch] M61+T19+T20+F3 gate reads …`) |
| ssx3 HEAD at commit | `dc9ef50` pre-commit (`[T21] …`; M62+T21 landed mid-run, offline, no T22 interaction) |
| Fork HEAD at T22 start | `282ce92` (E2a tripwires) + `M ps2xRuntime/src/runner/register_functions.cpp` (foreign, untouched throughout) |
| Fork HEAD at commit | `6359fb6` (`Trace: pc= dispatch-pc field … (T22)`, this brief) |
| Fork commits by T22 | 1 (`6359fb6`, 3 files, +22/−6); fork `git pull/push`: never run |
| Sidecars (`find $R -name "._*"`) | 34 with my 3, 31 after removal (mine created + removed mid-run; net zero from my edits) |
| Lease | none held, none claimed (tooling brief; no lease file touched) |
| Boots | 0 (compile + harness proof only) |
| Builds | 2 fork `-j4` (1 fail on AppleDouble glob pickup → sidecars removed → exit 0) + 1 harness `c++` (exit 0); no `adb`; `git push` in ssx3: never run |
| Wall | 2026-09-20 ~18:05–18:35Z (~0.5 h active), inside the 4 h box |
| ssx3 evidence commit | below (`[T22]`, trailer `Orchestrated-By: Muse Code`, no push) |

Inputs (all read-only; streamed, never copied): `/Volumes/Extreme SSD/
ps2x-t4/emulog-boot3.txt` + `/Volumes/Extreme SSD/ps2x-t4/emulog-t17c.txt`
+ `$W/P1/run/syscalls-t18-on.txt`.

## T22-1. Task 1 — projection + milestones

### Drop table (`--project shared`: 15 names, pinned)

Post-start matched counts from the `--- project ---` section
(boot3 ref_post=899,713 / rt_post=781,372):

| # | Name | ref | rt | Why (F3 §19 class) |
|---|---|---|---|---|
| 1 | sceSifGetReg | 260,722 | 0 | SIF layer: HLE'd by construction, runtime can never emit |
| 2 | sceSifSetDma_isceSifSetDma | 957 | 0 | SIF layer, same |
| 3 | sceSifSetDChain_isceSifSetDChain | 937 | 0 | SIF layer, same |
| 4 | sceSifSetReg | 8 | 0 | SIF layer, same |
| 5 | sceSifDmaStat_isceSifDmaStat | 17 | 0 | SIF layer, same |
| 6 | sceSifStopDma | 1 | 0 | SIF layer, same |
| 7 | WaitSema | 203,790 | 231,157 | sema pump: drowns both streams |
| 8 | SignalSema | 158,167 | 187,698 | sema pump, same |
| 9 | iSignalSema | 68,529 | 43,453 | sema pump, same |
| 10 | PollSema | 45,491 | 14,350 | sema pump, same |
| 11 | iPollSema | 45,104 | 0 | sema pump (reference-only interrupt-context mix) |
| 12 | iReferSemaStatus | 67,629 | 0 | sema pump, same |
| 13 | GetThreadId | 2 | 290,210 | runtime-only storm (~20/VBLANK; ref total 2) |
| 14 | FlushCache | 0 | 14,356 | runtime-only storm (~1/VBLANK; ref total 0) |
| 15 | RFU005 | 46,042 | 0 | reference-only interrupt-return path (host-side on runtime, F6) |

Deliberately NOT dropped (tabled): CreateSema/DeleteSema/ReferSemaStatus
(§19 milestones; ReferSemaStatus 0/0 whole-file both sides),
iFlushCache (0/0/0 whole-file all three inputs — in-or-out unobservable),
Dmac handlers + Deci2Call (§19 SDK-SIF/init milestones).

`--drop-names` parsing table:

| Input | Behaviour | Receipt |
|---|---|---|
| `A,B,...` | comma list, exact-name match, both streams, post-anchor; union with `--project` preset | t9: `WaitSema` → k=2 becomes k=1 projected |
| whitespace / empty entries | stripped / ignored | `parse_drop_names` (`"a, b,, "` → `[a, b]`) |
| unknown name | tabled as `NAME ref=0 rt=0`, non-fatal, exit unaffected | t11: `NoSuchCall` → k=2 projected, rc=1 |
| `--project bogus` | usage error, exit 2, no anchor table | t13: `unknown preset 'bogus'` + `USAGE-ERROR` |
| census interplay | census stays full post-start (projection applies to compare + locate + milestones only) | `--census` section diff vs T18 `align-boot3.txt`: EMPTY |

### Milestone table (`--milestones` on boot3-vs-t18 vs F3 §19's rows)

Projected: ref_post 899,713 → ref_proj 2,317; rt_post 781,372 → rt_proj
148. k=2 (projected), same events as T18 (ref `AddDmacHandler (12)`
@ev:164, rt `CreateSema (40)` @ev:2); name_mismatches=0 over 148
compared; rt opening 20-shingle NOT FOUND in ref (projected). Reference
ts is PCSX2 host wall (order, not seconds — §21.4).

| §19 row | Tool rows (mechanical) | Match |
|---|---|---|
| Entry agree | ref `RFU060, RFU061` @0.6090 / rt @0.0000 (k=0,1) | match |
| SDK SIF init | ref `AddDmacHandler, _EnableDmac` @0.6092–93, `Deci2Call` @0.9057, 2nd `AddDmacHandler` @0.9062 (+ `_DisableDmac/RemoveDmacHandler`); SIF storm names collapsed by projection (counts in drop table); rt single `AddDmacHandler` @1.4373 | match modulo storm |
| Kernel-patch path | rt `CreateSema` ×2, `Get/Set/Get/SetOsdConfigParam`, `RFU116 (74)` ×8 (= 0x74 SetSyscall under its PCSX2 table name), `RFU091_GetEntryAddress` ×6 @0.0001–0004; `FlushCache` ×3 absent by projection; extra `RFU090 (5a)` ×1 @ev:9 visible | match modulo FlushCache |
| First thread | ref `Create/StartThread` @0.9294/0.9296 → `ExitDeleteThread` @0.9400; rt first `CreateThread` @1.4325, zero exits anywhere | match |
| Module loads | rt `RFU252` ×21 + `CreateSema/DeleteSema` triplets 0.0135–1.4823 | match |
| OSD config | ref `Set,Get,Get2,Set2` @1.2026–28 (once); rt `Get` ×7 + `Get2` ×3 @1.4348–50, no `Set` | match |
| Thread block | ref 1 + 3 + 4 + 1 + 1 = 10 threads @0.9294/1.2098–99/1.2115/1.2121/1.2125–26, `CancelWakeup` @1.2118, `SleepThread` 4 in-window + 1 @4.5787 = 5 total (vs §19's ×3); rt 3 @1.4325–42 + 1 @1.4372 + 1 @4.5054 | match modulo count |
| INTC | ref `AddIntcHandler` ×2 @1.2122/1.2183; rt ×6 @0.0126/1.4345/1.4372/1.4459 ×2/4.5060 + `_DisableIntc` ×5 | match |
| Display init | ref `GsGetIMR, SetGsCrt` @1.2169, `SetGsVParam`, 2nd `SetGsCrt`, `AddIntcHandler`, `ChangeThreadPriority`, `WakeupThread`; `RFU005` absent by projection; §19's `CreateSema` ×2 not isolable (149-event sema churn spans 1.19–1.213, zero `CreateSema` in 1.2126–1.22); rt zero `SetGsCrt` (= never) | match modulo RFU005/sema |
| Steady state | ref `ReferThreadStatus` ×387 spanning 0.9135–335.1062; rt last milestone @5.0623 ev:9082, remaining 772,290 events 100% dropped vocabulary | match |

t17c-vs-t18: ref_proj=2,364 (+47 vs boot3: the deeper trace's extra
milestones), rt_proj=148 identical, k=2 same events, same NOT FOUND —
boot3 reproduction holds on the deeper reference.

### Selftest table

| Test | Checks | Result |
|---|---|---|
| t1–t8 (old) | 17 checks: identical/grafted/anchor/miss/alias/format/locate/short | 17/17 PASS (unchanged) |
| t9 `--drop-names` | exit 1, `k=1 (projected)`, drop row, `ref_proj=2 rt_proj=2` | 4/4 PASS |
| t10 `--project shared` | exit 1, `k=1 (projected)`, `project=shared drops=15` + zero-row | 3/3 PASS |
| t11 unknown name | exit 1, `k=2 (projected)`, `NoSuchCall ref=0 rt=0` | 3/3 PASS |
| t12 `--milestones` | exit 1, ref/rt sections + stamps, pump gone, census-full regression | 6/6 PASS |
| t13 bad preset | exit 2, `unknown preset 'bogus'` + `USAGE-ERROR` | 2/2 PASS |
| Total | 35 checks | 35/35 PASS (`selftest-after.txt`); before-change 17/17 (`selftest-before.txt`) |

Selftest catch (T18-t7 class): the first cut counted the census over the
first len(projected) post-start events (sceSifGetReg 2,304 instead of
260,722); observed as a census-section diff, fixed to full post-start
ranges, pinned by `t12-mile-censusfull` (verified FAIL on the reverted
copy, PASS on the fix). Default (no new flags) output diff vs T18
`align-boot3.txt`: EMPTY, exit 1.

## T22-2. Task 2 — pc= field + proof

Fork commit `6359fb6` (branch `ssx3`, 3 files, +22/−6; no push):
`TraceChannel.h` (signature + field doc), `TraceChannel.cpp` (cached gate
+ branched emit), `Dispatcher.cpp` (1 call line: passes
`(ctx != nullptr) ? ctx->pc : 0u`).

### Format table

| # | Item | Receipt |
|---|---|---|
| 1 | Gate | `PS2X_TRACE_SYSCALLS_PC`: non-empty = on; unset/empty = off (default). Read once at channel open; channel-off (`PS2X_TRACE_SYSCALLS` unset) = no output regardless (unchanged T18 path) |
| 2 | Off shape | `[%8.4f] Bios    : Bios call: %s (%x)` — the T18 format literal, same branch args, byte-identical |
| 3 | On shape | `[%8.4f] Bios    : Bios call: %s (%x) pc=0x%x` — `pc=0x%x` matches the sibling-diag convention (`Dispatcher.cpp:412` dropArgs, `Sync.cpp`, `Deci2.cpp`) |
| 4 | pc source | `ctx->pc` at dispatch (the same value as diag `first/lastPc`); `0` when `ctx` is null (same null-guard as the drop path) |
| 5 | Off proof | Harness (`pc-harness.cpp`, compiled against the REAL `TraceChannel.cpp`, no boot): 200-event T18-head feed → ts-normalized diff off-output vs T18 head-200: EMPTY |
| 6 | On proof | Same feed, gate=1: 200/200 lines match ` pc=0x[0-9a-f]+$`; on-output minus `pc=` diff vs off-output: EMPTY (uniform addition, 400 `<>` lines) |
| 7 | Empty-gate | `PS2X_TRACE_SYSCALLS_PC=""` output diff vs unset-gate output: EMPTY (= off) |
| 8 | Parser compat | `trace_align.py --format-check` on both harness outputs: 200 events, zeros across, exit 0 (`LINE_RE`/`TS_RE` unaffected by the suffix) |
| 9 | Full-boot diff | DEFERRED (gap G1): ts is host-wall so a boot-output diff needs a leased boot; rides the next leased boot brief |

On-shape sample (first 5 lines of `pc-on-sample.txt`, synthetic pcs
`0x42c000+` through the real emit path):

```text
[  0.0000] Bios    : Bios call: RFU060 (3c) pc=0x42c000
[  0.0000] Bios    : Bios call: RFU061 (3d) pc=0x42c001
[  0.0000] Bios    : Bios call: CreateSema (40) pc=0x42c002
[  0.0000] Bios    : Bios call: CreateSema (40) pc=0x42c003
[  0.0000] Bios    : Bios call: GetOsdConfigParam (4b) pc=0x42c004
```

### Build table

| # | Item | Receipt |
|---|---|---|
| 1 | Command | `cmake --build /tmp/p1-link/runtime --target ps2EntryRunner -j4` (`build-t22.log`, 134 lines), exit 0 (lease-free) |
| 2 | First attempt | exit 1: ninja glob picked up my `._Dispatcher.cpp` AppleDouble sidecar (`source file is not valid UTF-8`); removed my 3 sidecars, rebuilt — log head shows the glob re-check dropping `._Dispatcher.cpp` + `._TraceChannel.cpp` |
| 3 | Binary | `7f155f4cac62466c2535bc6987f64e0d2d31586ab21dd6b63c6a9998febdb377`, 163,464,560 B (+336 B vs T18 `a2a2f660…` 163,464,224 B) |
| 4 | Symbols | `strings` finds `PS2X_TRACE_SYSCALLS` ×2 + `PS2X_TRACE_SYSCALLS_PC` |
| 5 | Warnings | 11 `warning` lines, ALL pre-existing CMake deprecation/author notices (toml11, raylib, FetchContent); 0 compiler warnings, 0 from touched lines (TraceChannel/Dispatcher appear only in the glob-mismatch lines); zero `FAILED`/`error:` |
| 6 | Boot proof | explicitly deferred (gap G1): binary recorded, never executed (0 boots) |

### Proof table

| # | Item | Receipt |
|---|---|---|
| 1 | `align-milestones-boot3.txt` | 2,558 lines, exit 1: headers → anchor (HIT ev:162) → project (15 drops, 2,317/148) → name-table (148, 0 mismatches) → divergence k=2 projected + context → locate NOT FOUND (projected) → milestones ref/rt with stamps → full census |
| 2 | `align-milestones-t17c.txt` | 2,605 lines, exit 1: same shape, ref_proj=2,364, same k=2/divergence/locate |
| 3 | k/divergence rows | included in both (`k=2 (projected)`, both events, ±5 context) |
| 4 | `pc-off-sample.txt` / `pc-on-sample.txt` | 200-line harness off/on outputs + `pc-feed.txt` (feed) + `pc-harness.cpp` (probe source) |
| 5 | `selftest-before.txt` / `selftest-after.txt` | 17/17 → 35/35 logs |

## T22-3. Exact commands

From `/Users/bradrichardson/dev/ssx3` unless noted; `$R`, `$W` quoted
(path contains a space):

```text
# Recon (lease-free, read-only streams)
read local/research/T18/REPORT.md (all) + F3 rec 14 + F3 S19 (Part 3)
python3 tools/trace_align.py --selftest (17/17 PASS, before-change)
git show HEAD:tools/trace_align.py > /tmp/t22-align-before.py (before log)
grep -c drop-list names across boot3 + t17c + t18-on (whole-file census)
# Aligner (lease-free)
edit tools/trace_align.py (--drop-names/--project/--milestones + t9-t13)
py_compile; --selftest (35/35 PASS, after)
default run diff vs local/research/T18/align-boot3.txt (EMPTY, exit 1)
--project shared --milestones --locate 20 --census on boot3 + t17c (exits 1/1)
census-section diff (non-empty -> fix -> EMPTY; t12-mile-censusfull pins it)
buggy-copy selftest (t12-mile-censusfull FAIL, all else PASS)
awk milestone-section extracts for the S19 match/no rows
# Channel (lease-free)
edit $R/.../Syscalls/TraceChannel.h + TraceChannel.cpp + Dispatcher.cpp
c++ -std=c++17 harness vs real TraceChannel.cpp (exit 0)
200-event feed; off/on/empty-gate harness runs; norm diffs (EMPTY/EMPTY)
--format-check on both harness outputs (exit 0)
cmake --build /tmp/p1-link/runtime --target ps2EntryRunner -j4 (fail on
  AppleDouble glob -> rm my 3 sidecars -> exit 0); warnings census; sha
# Commits
git -C $R add 3 Syscalls paths + commit 6359fb6 (ssx3 branch; foreign M kept)
stage 9 evidence files in local/research/T22/ (7 cp'd, 2 aligns written direct)
git add tools/trace_align.py; git add -f local/research/T22/; commit [T22] (no push)
```

## T22-4. Gap rows

| # | Gap | Detail |
|---|---|---|
| G1 | Boot proof deferred (per brief) | Full-boot off-output diff (ts-normalized vs a 781,372-line-class file) + on-shape boot lines + gate-on ladder ride the next leased boot brief. This brief proves the emit path (harness through real code) + compile only |
| G2 | Deeper-trace half outstanding (T18-G7 stands) | t17c plugs into the projected tool unchanged (+47 ref milestones); post-User-Prefs/gameplay alignment still needs a runtime boot that reaches those epochs |
| G3 | Projection-blind §19 cells | `FlushCache` ×3 (kernel-patch row) + `RFU005` (display row) are invisible under `--project shared` by design; re-run without `--project` (or with a narrower `--drop-names`) to see them |
| G4 | SleepThread count note | Mechanical in-window count is 4 + 1 late = 5 total vs §19's hand-scoped ×3; the 4th sits @1.2118 beside `CancelWakeupThread` |
| G5 | AppleDouble glob fragility (pre-existing) | Any `._*.cpp` beside a globbed source breaks the fork build; my 3 sidecars were removed mid-run (31 fork-wide after, net zero from my edits) |
| G6 | Fork git pack `.idx` AppleDouble noise (pre-existing) | `non-monotonic index ._*pack*` errors on every fork git command; commands still succeed (log/status/add/commit verified) |
| G7 | ts are host-wall (F3 §21.4 stands) | Milestone stamps order phases; never compare reference-vs-runtime seconds (Devel 67 vblank/s vs runtime 60 Hz) |
| G8 | Session wall | ~0.5 h active of the 4 h box; zero lease waits (no lease claimed) |

## Evidence files

`REPORT.md` (this file), `align-milestones-boot3.txt` (2,558-line full
projected alignment + milestones + census), `align-milestones-t17c.txt`
(2,605-line T17 plug receipt), `pc-off-sample.txt` + `pc-on-sample.txt`
(200-line harness off/on outputs), `pc-feed.txt` (200-line id/pc feed),
`pc-harness.cpp` (probe source), `selftest-before.txt` (17/17),
`selftest-after.txt` (35/35), `build-t22.log` (134-line `-j4` log).
Plus `tools/trace_align.py` (the deliverable tool edit, committed
alongside). Full-size artifacts stay on the SSD by path+sha:
`emulog-boot3.txt`, `emulog-t17c.txt`, `syscalls-t18-on.txt`
(37,348,669 B), binary `7f155f4c…b377` (163,464,560 B).

## T22-5. Tail receipt (F3 rec 17)

Report written in 4 chunks; closing 3 lines quoted verbatim below
(`tail -3 local/research/T22/REPORT.md` at commit):

```text
T22 evidence complete: projection + milestones + pc= field (boot proof deferred to next leased boot brief).
Trailer: Orchestrated-By: Muse Code.
End of T22 report.
```

T22 evidence complete: projection + milestones + pc= field (boot proof deferred to next leased boot brief).
Trailer: Orchestrated-By: Muse Code.
End of T22 report.
