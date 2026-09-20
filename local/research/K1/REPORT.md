# K1 report — provenance-checked equivalent for the SSX3 copied syscall payload

Brief `local/muse/prompts/K1.md` + three frontier steering inputs (recorded in
K1-1; the third points at `docs/research/review-2026-09-20-first-frame-and-gs.md`,
read in full before finalizing). Tables, no verdicts.
`R=/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp` (fork, branch `ssx3`),
`W=/Volumes/Extreme SSD/ps2recomp-spike`, `RUN=$W/P1/run`,
`OUT=$W/P1/output`, ELF `$W/P1/SLUS_207.72` + `$W/P1/cd/SLUS_207.72`
(boot ELF = cd path). Time box 6 h; session wall ~22:55–23:25Z 2026-09-20
plus analysis to ~23:35Z (~2.5 h active, inside the box).

Headline readings: the six `dispatchSyscallOverride(0x5B)→0x80075000`
KE_ERROR drops are served by a provenance-checked HLE equivalent (game
override + guest copy-integrity memcmp; no game code bytes in the
runtime): all six payload lookups return the payload's own values
(`55→80075038, 56→800750C8, 57→80075108, 58→80075158, 59→800751A8,
03→80075330` data); installed table holds 8 game/payload addresses with
no `-1`; drop census 6 → 0 in boot log AND park snapshot; helpers
`0x55–0x59` unreached on both runtime and R1 game paths (equivalents
stand by, untripped); boot reaches the identical park (thread pcs,
waits, semaphores, hot-pc top, missing-target, stub blocks, upload
count all equal; event/GS counters within 0.3% wall noise); P0 settled
frame captured = uniform opaque black (first-frame milestone not met);
suite 439/439/0 → 443/443/0.

## K1-0. Rule record

| Item | Value |
|---|---|
| ssx3 HEAD at start | `a1a4b73` (findings doc era; tree clean) |
| Fork HEAD at start | `6359fb6` (branch `ssx3`) + pre-existing `M ps2xRuntime/src/runner/register_functions.cpp` (generated, untouched throughout, still uncommitted at end) |
| Fork commits by K1 | 2 (`fc75f70` fix, `b6252bb` P0 capture), pushed to FORK remote only (`7eed783..b6252bb ssx3 -> ssx3`; range includes pre-existing branch commits between the remote head and local base) |
| Fork upstream remote | never pushed, never fetched |
| Generated runner sources | never staged/committed/pushed (only named source/test files added) |
| ssx3 evidence commit | below (`[K1]`, trailer `Orchestrated-By: Muse Code`, NO push — orchestrator pushes at poll) |
| Lease | `/tmp/ssx3-p-lane-lease` held 23:03:57–23:08:08Z (251 s) for boot-1 only; zero waits (absent at claim; no other agent named) |
| Boots | 1 of 2 used (BOUND=wall 242 s; second boot not needed — no new question; K1-7) |
| Builds | any time, `-j4` throughout (K1-5) |
| `adb` | not used |
| `COPYFILE_DISABLE=1` | exported on every step touching the SSD |
| Sidecars | 4 `._*` created by K1 edit tooling removed before build (K1-5); evidence dir sidecar-free at commit |
| ps2sdk source | NOT copied (AFL-2.0 vs GPL per steering); payload semantics decoded from game ELF bytes only (`/tmp` miners) |
| TheTharin side-map candidate | considered, NOT adopted (house override mechanism suffices; no copied-MIPS execution attempted; no third-party code copied — K1-2) |

## K1-1. Steering inputs recorded (all three + findings doc)

| # | Input | Content applied |
|---|---|---|
| 1 | Frontier correction (same poll as brief) | R1 proves game patch installation under PCSX2, not hardware/physical parity — claimed only as shown; R1-only scanner `0x83` + `0x42C758` installer tabled (K1-10); the 6 drops are the copied-code path `0x5B→0x80075000` (built-in fix insufficient) — fix addresses it; expanded acceptance rows tabled (K1-11) |
| 2 | Second refinement (before implementation) | `0x80075000` is a six-entry TLB-payload lookup (table at dst `0x80075300`), not original handlers — verified verbatim from ELF words (K1-3); index 3 = data `_kExecArg`, not code — preserved as data; ps2sdk corroboration is AFL-2.0 — not copied; A0 event-flag labels for 54–59 misleading — not relied on; generic trampolines CANNOT satisfy all six — NOT built (scope change from brief Task 1.1, recorded here); `0x42C758` absence explained by `InitAlarm@0x42C7C8` HLE stub — semantics compared, not counts (K1-10); full findings doc: ARRIVED (see 3), no OPEN row needed |
| 3 | Third input + `docs/research/review-2026-09-20-first-frame-and-gs.md` (read lines 1–204 before finalizing) | P0 framebuffer capture implemented + inspected (K1-9); ONE boot default held (K1-7); semantic counters independent of `PS2X_DROP_SILENCE` (`[k1]` stderr lines + snapshot census — K1-2/K1-8); ACTUAL baseline reported (439/439/0, not the brief's 427 — K1-6); no frame promised (causal link unestablished — K1-11/K1-13); TheTharin mechanics-only pointer considered, not adopted (K1-0/K1-2); E3 parked behind K1 (noted, no action); ret0 retired ONLY with convergence evidence — held (K1-2) |

## K1-2. Fix table (files + lines touched)

Commit `fc75f70` (fix + tests). Line numbers = post-commit fork tree.

| # | File | Lines | Change |
|---|---|---|---|
| 1 | `ps2xRuntime/src/lib/Kernel/Syscalls/Ssx3CopiedPayload.h` | 1–27 (new) | `tryDispatchSsx3CopiedPayload` / `noteSsx3CopiedPayloadInstall` / enabled + reset-for-testing decls |
| 2 | `ps2xRuntime/src/lib/Kernel/Syscalls/Ssx3CopiedPayload.cpp` | 1–247 (new) | `ssx3-copied-payload` game-override descriptor (SLUS_207.72, entry `0x100008`); copy-integrity memcmp gate (src `0x4561C0` vs dst `0x80075000`, `0x330` B, both in RDRAM); destination-table lookup emulation (6 pairs at dst+`0x300`, hit → value, miss → 0); five helper equivalents with payload-matching validation (K1-3); `[k1]` stderr diagnostics with seq counters (armed / install# / lookup# / helper# / provenance-FAIL#) |
| 3 | `ps2xRuntime/src/lib/Kernel/Syscalls/System.cpp` | `:2` include; `:440–452` hook (no-function branch tries the equivalent before the KE_ERROR drop); `:511` `noteSsx3CopiedPayloadInstall` in `SetSyscall` | 9 added lines total; built-in `GetEntryAddress` (`:1006` shape) untouched — never fires on this path (override shadows it) |
| 4 | `ps2xTest/src/ps2_runtime_kernel_tests.cpp` | `:28–29` fwd decl; `:1941–2127` four `tc.Run` cases (six keys + miss; helper validation matrix; broken-copy/unarmed/unmatched refusal; scanner marker cross-check) | 188 added lines; quirk armed via the real `applyMatching` path in tests |

Commit `b6252bb` (P0 capture; env-gated, unset = zero behavior change).

| # | File | Lines | Change |
|---|---|---|---|
| 5 | `ps2xRuntime/src/lib/ps2_runtime.cpp` | `:379–473` dump helper (`PS2X_FRAME_DUMP_DIR`, FNV-1a, PNG + sidecar, `[frame:dump]` line); `:514–517` fallback-path hook; `:553–559` success-path hook (size-guarded) | 102 added lines |

Scope decisions (deviations from brief Task 1.1, per steering):

| Decision | Brief text | Built instead | Pointer |
|---|---|---|---|
| No generic trampolines | Part 4 dec-3 shape (reserved range, per-syscall trampolines, synthetic table at trampoline base) | Payload-specific equivalent: exact six results incl. data (a generic trampoline cannot return `0x80075330`-as-data for key 3) | Refinement 2.5; findings doc K1 acceptance |
| `ret0@0x42c1f0` HELD (not retired) | "ret0 retired" | Scanner intentionally dormant; retirement needs convergence evidence (one causal question per run; K1's question = the 6 drops). Pre-evidence tabled: entries exist (CSV rows 9231–9232: `sub_0042C130`, `sub_0042C168`), marker cross-check unit-tested (K1 test 4), static sketch (zero-filled scan range + mirror markers converge on path 1). Successor question justifying a second boot | Findings doc "Retire the scanner's ret0 only with evidence…" + one-boot rule |
| No copied-MIPS execution | "copied-code execution OR provenance-checked HLE equivalent" | The equivalent (OR-branch): static recompiler has no JIT/interpreter for copied bytes; load-address-aware overlay out of box | Findings doc ("narrowly validated HLE equivalent is better scoped") |
| `0x54→0x42D100` untouched | — | Still installed, still dormant (`(54)=0` both paths); mid-function handler out of K1 scope | K1-8 census |
| TraceChannel 0x54–0x59 names untouched | — | Still event-flag RFU labels (PCSX2-verbatim); misleading under this table per refinement, but renaming risks aligner joins — tabled, not changed | Refinement 2.4 |

## K1-3. Payload contract (decoded from game ELF bytes, dest base `0x80075000`)

Miner `local/research/K1/k1_dis.py` (capstone, read-only). Table words at
ELF `0x4564C0` verified verbatim against refinement 2.1 (all six pairs +
zero padding). Copy geometry: `Copy(dst 0x80075000, src 0x4561C0, 0x330)`
via guest `0x42CB78` word loop; table at src+`0x300` → dst `0x80075300`.

| Entry | Role (layout-derived) | Validation (exact) | HLE success shape |
|---|---|---|---|
| `+0x0` lookup | linear search 6 pairs at `0x80075300` for `a0` | none | hit → value; miss → 0 (payload-exact, reads DESTINATION table) |
| `+0x38` idx `0x55` | mtc0 set + `tlbwr` + `tlbp`, returns Index | `(a1>>24)&0xF0 ∈ {0x00,0x30,0x40}`, else −1 | valid → 0 (ASSUMPTION A1: index unknowable without a TLB); invalid → −1 exact |
| `+0xC8` idx `0x56` | indexed `tlbwi`, returns `a0` | `a0 < 0x30`, else −1 | `a0` (input-echo, exact) |
| `+0x108` idx `0x57` | `tlbr`, stores 4 COP0 words to `[a1],[a2],[a3],[t0]`, returns `a0` | `a0 < 0x30`, else −1 | zeros stored (ASSUMPTION A2: empty-TLB read); null ptr → −1 (defensive) |
| `+0x158` idx `0x58` | `tlbp` + conditional stores, returns index or −1 | none (probe) | −1 always (ASSUMPTION A3: no HLE mappings → always miss) |
| `+0x1A8` idx `0x59` | probe + wired-index alloc (`tlbwi` map) | fail iff `(a0&0xFFF)!=0` or `a0 ∈ [1,0x0FFFFFFF]` | `a0==0` → 0; else wired counter 0,1,… (ASSUMPTION A4: alloc sequence; HLE probe always misses per A3) |
| key `0x03` → `0x80075330` | DATA one past the payload (`_kExecArg`) | n/a (table value) | returned as data; NO executable manufactured (verified: `(03)` issued 0× both paths — K1-8) |

Assumption exposure: A1–A4 are unreachable-on-both-paths (`(55–59)=0` in
K1 AND R1A game epoch — K1-8/K1-10); every helper hit would emit a loud
`[k1] helper#` line with full args, so any future reach is attributable.
No helper line appeared in boot-1 (K1-8).

## K1-4. Downstream-use analysis (first use of the data result)

`[0x456538]` write: proven by chain — `[k1] lookup#6 key=0x3
value=0x80075330` + static no-`v0`-clobber between `jal 42CBB0` return
(`0x42cc74`) and `sw $v0,0x6538($v1)` (`0x42cc88`; only `lui v1` + 4×`ld`
in between — `sub_0042CBC0_0x42cbc0.cpp:270–292`). Before: `-1`; after:
`0x80075330`. The store is `FAST_WRITE32` (recompiled): invisible to
`PS2X_DIAG_WATCH` (macro writes only) and to `ps2TraceGuestWrite`
(no-op stub) — hence the static chain, tabled here, not a watch line.

| Consumer | Site | Before-path status | Evidence |
|---|---|---|---|
| `a3=[0x456538]` → `jal 4239F0` (ExecPS2) | `0x42c674` (`sub_0042C628`) | NOT executed | straight-line (`lw,daddu,daddu`) to existing-entry `jal`; execution would fire syscall 7; `(7)=0` in T18/T26/K1 |
| `a1=[0x456538]+4` → `j 4241C0` | `0x42c744` (`sub_0042C6E8`) | NOT executed | `0x4241C0` has no entry (no OUT file); execution would emit `[guest-branch:missing-target] target=0x4241C0`; 0 lines (channel live: 1411 in T18, 1 in T26/K1 — same single IndirectCall in both, K1-8) |
| `a2=[0x456538]+4` → `j 4239E0` (LoadExecPS2) | `0x42c6c8` (`sub_0042C6A0`) | NOT executed | same shape: `target=0x4239e0` 0 lines |
| `s3=[0x456538]` → `v0=s3+0x40` … | `0x42c520` (`sub_0042C510`) | OPEN (static) | callers confined to `{42C6A0@0x42c6b0, 42C628@0x42c65c, 42C6E8-file@0x42c72c}` (OUT-wide grep); executes iff `42C628`-entry reaches its `0x42c65c` call (the other two call sites sit past disproven points). No syscall issued by the `0x42c500–0x42c6FF` range in 785,356 T26 events (pc-tagged) |
| `_kExecArg` content at `0x80075330` | data | UNWRITTEN in-window | WATCH windows `0x80075330/38`: 0 lines (guest-macro coverage; host memcpy/DMA/SIF bypass per P26-1h — stated, not covered) |

Operational close (boot comparison): trace census, park, stub blocks,
upload count, missing-target, and hot-pc top are identical modulo
wall-timing noise (K1-8) — the changed word has NO observed downstream
use in-window. First downstream use: none observed; 3/4 consumers
disproven, 1/4 (`42C510`) open-but-silent.

Copy-landing proof (guest-macro watch, 6 lines, all `pc=0x42cb98`
thread 1): `0x80075000/04` (head `3c028007/0000282d`),
`0x80075300/04` (key `0x55` + `0x80075038`), `0x80075328/2c` (key `0x3`
+ `0x80075330`) — the provenance gate's memcmp passed on top of this.

## K1-5. Build record

| # | Build | Command / target | Result |
|---|---|---|---|
| 1 | Baseline (pre-fix tree) | `cmake --build /tmp/p1-link/runtime --target ps2x_tests -j4` | exit 0 (`/tmp/k1-baseline-build.log`; 19 steps) |
| 2 | Fix (attempt 1) | same | FAILED: glob picked up 4 AppleDouble `._*.cpp` sidecars created by edit tooling (non-UTF-8 "source"); removed the 4 (mine only; `find` before/after), rebuilt |
| 3 | Fix | same | exit 0 (`/tmp/k1-fix-build2.log`); suite binary relinked |
| 4 | Runner + fix | `--target ps2EntryRunner -j4` | exit 0 (`/tmp/k1-runner-build.log`); sha `6d3d1458…` 163466496 B (pre-P0) |
| 5 | Runner + fix + P0 | same | exit 0 (`/tmp/k1-runner-build2.log`); suite relink + re-green (K1-6) |
| Final | K1 boot binary | `/tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner` | sha256 `72b2cfc59dbf09de91c4e378ffcf0624c4e792c99cbce4b025914dad27ae89f6`, 163483200 B |

Linkage receipts (boot binary): `strings … | grep -c "\[k1\]"` = 5;
`grep -c PS2X_FRAME_DUMP_DIR` = 1.

## K1-6. Suite record

Run from the fork root (`cd $R`; the `ps2xRecomp/include/…` relative
candidate requires it).

| Run | Total | Passed | Failed | Note |
|---|---|---|---|---|
| Baseline (pre-fix, build dir cwd) | 439 | 438 | 1 | `VU0 macro mappings…` — cwd artifact (no `ps2xRecomp/` under `/tmp/p1-link/runtime`), NOT a product failure |
| Baseline (pre-fix, fork-root cwd) | 439 | 439 | 0 | ACTUAL baseline (`/tmp/k1-baseline-suite2.log`; brief's 427 stale) |
| Post-fix + P0 (fork-root cwd) | 443 | 443 | 0 | `/tmp/k1-fix-suite2.log`, exit 0; 4 new K1 cases all `[Passed]` (443 `[Passed]`, 0 `[Failed]`) |

New cases (`ps2_runtime_kernel_tests.cpp:1941–2127`): six installer keys
+ miss-returns-0; helper validation matrix (0x56/0x57 bounds, 0x55
nibble allow/deny sets, 0x58 miss, 0x59 align/range/alloc-0-then-1);
broken-copy/unarmed/unmatched-pair refusal (KE_ERROR path preserved);
scanner marker cross-check (both markers visible in the KSEG0 mirror,
same base). Quirk armed via the real `applyMatching` registry path.

## K1-7. Lease + pre-claim + boot record

Waits log `$W/P1/run/k1-waits.log` (2 lines; canonical copy, not
duplicated into evidence).

| Event | Value |
|---|---|
| Pre-claim checks (23:03:52Z, T13 §T13-0 verbatim) | Lease absent; `pgrep -x ps2EntryRunner` exit 1; sha `72b2cfc5…` 163483200 B; ISO 3005415424 B + ELF 3890784 B (both `P1/` and `P1/cd/` paths; boot ELF = cd path); SSD 465 Gi free (internal 19 Gi; all logs → SSD); selftest 35/35 ALL PASS (`tools/trace_align.py --selftest`); t26-waits tail = released; caps wall=240 s + progress=1000000 trace lines (T24 precedent); env T26-verbatim + WATCH=5 payload windows + `PS2X_FRAME_DUMP_DIR` |
| Claim | `printf 'K1\n' > /tmp/ssx3-p-lane-lease`, 23:03:57Z; zero waits (no poll needed) |
| Boot-1 | `python3 /tmp/k1-boot1.py` (foreground, `local/research/K1/k1-boot1.py` copy); 16 liveness polls; SIGTERM el=242 s rc=0; BOUND=wall (trace 783,005 at last poll < 1M cap); script exit 0 |
| Release | 23:08:08Z (held 251 s); verified absent; `pgrep -x` exit 1 |
| Boot 2 | NOT used — no new question arose (all acceptance rows closable from boot-1; ret0-retirement is tabled as the successor's question, which would justify a second boot) |

## K1-8. Before/after tables (before = T26/T18 pre-fix; after = K1 boot-1)

Artifacts (SSD canonical copies, referenced not duplicated):
`boot-k1-1.log` (528,891 lines, 92,925,537 B),
`syscalls-k1-on.txt` (783,250 events),
`park-k1-1/park-snapshot.{json,txt}`, `frames-k1-1/` (K1-9).

### Drops + installs + lookups (semantic counters, silencing-independent)

| Row | Before (T18/T26) | After (K1 boot-1) |
|---|---|---|
| `[drop]` census (boot log) | 6 (`syscall/dispatchSyscallOverride KE_ERROR syscall=0x5b handler=0x80075000`) | 0 |
| Snapshot `drops[]` (independent of `PS2X_DROP_SILENCE`) | `[{dispatchSyscallOverride, KE_ERROR, 6}]` | `[]` |
| `[k1] lookup#1–6` | n/a (quirk absent) | `55→80075038, 56→800750C8, 57→80075108, 58→80075158, 59→800751A8, 03→80075330` — payload-exact, in installer order |
| `[k1] install#1–8` | n/a (no install log) | `5A→42CB78, 5B→80075000, 54→42D100, 55→80075038, 56→800750C8, 57→80075108, 58→80075158, 59→800751A8` — no `-1` |
| Installed handlers `0x55–0x59` | `0xFFFFFFFF` ×5 (drop residue) | payload code addresses ×5 |
| `[0x456538]` | `-1` | `0x80075330` (chain proof — K1-4) |
| `[k1] helper#` | n/a | 0 (equivalents stand by, untripped) |
| `[k1] provenance-FAIL#` | n/a | 0 (memcmp passed) |

### Event census (trace; T26 → K1, both 240 s wall-bound, pc-tagged)

| Events | T26 | K1 | Δ |
|---|---|---|---|
| total | 785,356 | 783,250 | −2,106 (−0.27%, wall noise) |
| `(74)` / `(5b)` / `(5a)` | 8 / 6 / 1 | 8 / 6 / 1 | identical (installer fires identically; opening events 1–26 same names+pcs) |
| `(64)` | 14,429 | 14,390 | −39 (noise) |
| `(55–59)` issued | 0 | 0 | helpers unreached both |
| `(54)` issued | 0 | 0 | dormant both |
| `(03)` issued | 0 | 0 | no syscall-3 executable manufactured |
| `(83)` | 0 | 0 | scanner stubbed both (ret0 held) |
| `(2f)` | 291,690 | 290,910 | −0.27% (same storm rate) |
| `(40)` | 37 | 37 | identical |

### Park + log census (T26 → K1)

| Row | T26 | K1 |
|---|---|---|
| Threads | 6: t1 `0x423dc8` wait 0; t2–t6 `0x423de8` waits 26/30/31/32/36 | IDENTICAL (all ids/pcs/waits) |
| Statuses | t1 status 0; t2–t6 status 2 | identical |
| Semaphores / hot-pc len | 16 / 1188 | 16 / 1188 |
| Hot-pc top3 | `392c60:1965676, 325260:1147840, 41ea18:953381` | `392c60:1960333, 325260:1144720, 41ea18:953381` (same pcs; third count EXACT) |
| sched_counts | `-1:28839 1:28871 2:86 3:152 4:14425 5:28845 6:1` | `-1:28762 1:28793 2:86 3:152 4:14386 5:28767 6:1` (t2/t3/t6 exact) |
| GS kicks/drawing/packets/dma | 3505928/3477164/402432/532262 | 3496412/3467726/401340/530791 (≤0.3%) |
| GS writes/vif_writes | 0 / 2 | 0 / 2 |
| Missing-target | 1 (`IndirectCall JALR 0x2322d4→0x395730`, same regs) | 1 (IDENTICAL line) |
| `[diag:stubs]` blocks | 48 | 48 |
| `[frame:upload]` lines | 128 (idx 0 tick 53 … idx 127 tick 980) | 128 (idx 0 tick 49 … idx 127 tick 765; same fbp/size; 128 = print cap) |
| `[diag:394ed0]` | 20001 | 20001 (drain loop identical) |
| Boot log | 6,764,707 lines, 705,357,230 B (6.24M = T26's own 83-window watch) | 528,891 lines, 92,925,537 B (watch = 6 K1 lines) |
| `target=0x4241c0` / `target=0x4239e0` | 0 / 0 | 0 / 0 (re-verify post-fix; K1-4 consumers still silent) |

Park: SAME (all pcs/waits/statuses/counts equal; event/GS deltas are
wall-timing noise). The fix removes bad state; it does not move the
ladder — and per steering, no frame was promised (K1-11/K1-13).

## K1-9. P0 framebuffer capture (first upload + settled park)

Dumps in `$W/P1/run/frames-k1-1/`; evidence carries `upload-latest.*` +
`fallback-0.*` (`fallback-latest.*` byte-identical to `fallback-0.*`,
same hash — not duplicated).

| Upload | seq | tick | Size | displayFbp/sourceFbp | preferred | fallback | fnv1a | smode2/pmode |
|---|---|---|---|---|---|---|---|---|
| first (fallback) | 0 | 0 | 640×512 | 0/0 | 0 | 1 | `af249dc5` | 0x0/0x0 |
| last fallback | 12 | 40 | 640×512 | 0/0 | 0 | 1 | `af249dc5` | 0x0/0x0 |
| first success | 13 | 49 | 512×448 | 112/112 | 0 | 0 | `fd889dc5` | — (see sidecar shape) |
| settled success | 3640 | 14422 | 512×448 | 112/112 | 0 | 0 | `fd889dc5` | 0x1/0xff21 |

Counts: 3,641 `[frame:dump]` lines = 14 fallback=1 + 3,496
fallback=0 + 131 spliced (tail lost to concurrent stdout/stderr
interleave — pre-existing log behavior, e.g.
`[diag:394ed0]…total=0x[frame:dump]…`, `size=200x1c0…fallback=14…`
impossible values). `[frame:upload]` 128 (print cap, idx 0–127).
Hash census: `af249dc5` ×13 clean (14th fallback hash spliced) +
`fd889dc5` ×3,465 clean + 11 corrupted-hash + 32 fallback-known /
hash-lost. Spliced sizes: 50 success-sized, 72 cut before size, 9
corrupted-size. Net: 3,465/3,496+ success lines share `fd889dc5`
(96%+); 162 lines unattributable (stated, not dropped).

Image inspection (viewed, not just counted):

| Image | Content | Distinct RGBA | Reading |
|---|---|---|---|
| `fallback-0.png` (640×512) | uniform magenta | 1 (`ff00ffff` ×327,680) | fallback path + dumper pipeline proven |
| `upload-latest.png` (512×448) | uniform opaque black | 1 (`000000ff` ×229,376) | settled success frame; nonuniform = 0 |

Hash proof: FNV-1a over 229,376×`(0,0,0,255)` recomputed independently
= `0xfd889dc5` ✓ — first success through settled are byte-identical
black (FNV-32 proxy, stated). Consistent with the park (game never
issues `SetGsCrt`; the "presentable buffer" is a zero buffer).
First-frame milestone: NOT met (no recognizable content) — and not
promised by this fix.

MISSED (OPEN, fix noted): the numbered keeps (`seq<2`) were consumed by
the two earliest fallbacks, so no numbered first-*success* PNG exists;
only `upload-latest.png` (+ hash-equality back to seq 13). Successor
tweak: per-path keep counters (first-N success AND first-N fallback).

## K1-10. R1 game-epoch comparison (executable/epoch/mode/pc named)

Reference: R1A recompiler trace post-`ExecPS2:5` (game entry
`0x100008`, file ≥872992, 2,414,436 events; `/tmp/k1-r1a-game.txt`
slice). Runtime: K1 boot-1 (same game entry, HLE, 783,250 events).
PCSX2 prints `pc=`/`a0=` WITHOUT `0x` (R1 one-line patch).

| Patch block (pc) | R1A game (74 / 5b / 5a) | K1 runtime | Disposition |
|---|---|---|---|
| locator marks (`42c2f8`) | 2 (`83,5a`) / — / — | 0 | ret0 scanner; intentionally dormant in K1 (entries exist; K1-2) |
| alarm installer (`42c768`) | 8 (`5a,5b,fc,fe,fd,ff,12c,8`) / 6 (`fc,fe,fd,ff,12c,8`) / 2 (dst `80076000`, size `82000`) | 0 / 0 / 0 | `InitAlarm@0x42C7C8` + `InitThread` HLE collapse; explained at call-path level (refinement 2.6) — NOT counted as defect |
| main installer (`42cbc8`) | 8 (`5a,5b,54,55,56,57,58,59`) / 6 (`55,56,57,58,59,3`) / 1 (dst `80075000`) | 8 (same a0 set, `[k1] install#`) / 6 (same keys+order, `[k1] lookup#`) / 1 | IDENTICAL shape; K1 serves all six with payload values |
| locator scans (`83`) | 2 (`@42c1b0 a0=80000000`) | 0 | same ret0 row |
| syscalls `0x55–0x59` ISSUED | 0 | 0 | installed helpers dormant on BOTH paths in-window |
| `AddIntcHandler (10)` / `_EnableIntc (14)` / `_DisableIntc (15)` | 7 / 7 / 5 | 6 / 6 / 5 | within 1 (timer/alarm/INTC semantics, not raw counts) |
| `SetCPUTimer*` / alarm names | 0 | 0 | absent both |
| `(2f)` GetThreadId | 704,984 | 290,910 | both storm; rate differs (phase/timing, not K1 scope) |
| `SetSyscall(0x12c)` (timer-3 meaning per Play!) | present (alarm block) | absent (alarm block HLE-collapsed) | structural HLE difference; downstream effect OPEN (K1-13) |

## K1-11. Acceptance rows (revised acceptance × evidence)

| Acceptance (findings doc, supersedes brief + correction 1) | Evidence | Row |
|---|---|---|
| Execute the copied lookup correctly, or equivalent guarded by verified payload identity + load layout | `[k1] lookup#1–6` exact six values; memcmp gate (src+dst+size in RDRAM) + game-override gate; 0 provenance-FAIL | CLOSED |
| Preserve the data result + subsequent reads/writes; do NOT manufacture a syscall-3 executable | key 3 → `0x80075330` as data; `(03)` issued 0×; `_kExecArg` writes 0 (guest-macro); consumers 3 disproven + 1 open-but-silent | CLOSED (open consumer bounded — K1-4) |
| Cover reached copied helper entries + required original-text entries incl. scanner; dormant-by-statement allowed | helpers `0x55–0x59`: equivalents serve validation; unreached both paths (0 counts) — dormant, stated; scanner `0x42C130/68`: entries exist, intentionally dormant (ret0 held) — stated with pre-evidence | CLOSED as stated-dormant |
| Retire scanner ret0 ONLY with convergence evidence | NOT retired (no convergence evidence yet); marker cross-check unit-tested; successor question | HELD (this row is the hold) |
| Show installed table + six returns + no −1 + first downstream use; count failures independent of silencing | `[k1] install#1–8` (no −1); six returns; downstream = none observed (K1-4); snapshot `drops[]` 6→0 + `[k1]` stderr (both silencing-independent) | CLOSED |
| Run current relevant tests, report ACTUAL baseline; one bounded boot + framebuffer + park signature; second boot needs new question | baseline 439/439/0; post 443/443/0; 1 boot BOUND=wall; P0 captured+inspected; park identical; boot 2 unused (no new question) | CLOSED |
| Do NOT promise the frame (A0: 0x54–59 uncalled; causal link unestablished) | park SAME after fix; settled frame black; no frame claimed anywhere in this report | HELD (no promise made) |
| Original-handler chaining (correction-1 blanket requirement) | SUPERSEDED by findings doc ("This supersedes the blanket original-handler chaining requirement…"): payload helpers are terminal implementations, not wrappers; no chaining exists to validate | SUPERSEDED (pointer recorded) |

## K1-12. Exact commands

Fork (`R=/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp`, every command
with `export COPYFILE_DISABLE=1`):

```text
git -C "$R" rev-parse HEAD; git -C "$R" status --short; git -C "$R" branch --show-current  # 6359fb6 + M register_functions.cpp, ssx3
grep -n "SetSyscall|GetEntryAddress|..." System.cpp; sed -n '400,560p / 960,1038p' System.cpp  # hook-site reads
sed -n '1,160p' Dispatcher.cpp; sed -n '2660,2800p' ps2_runtime.cpp  # override check :108; table/mirror impl
sed -n '680,730p' EeScheduler.cpp; sed -n '2155,2200p' EeScheduler.cpp  # unknown-pc; bind self-init
grep -n "PS2_REGISTER_GAME_OVERRIDE" RPC.cpp:171; sed -n '1,80p' game_overrides.h  # house pattern
# payload decode (read-only ELF; capstone)
python3 /tmp/a0_elf.py words 0x4564C0 16            # six pairs verbatim
python3 /tmp/k1_dis.py 204                           # full payload @ dest base (local/research/K1/k1_dis.py copy)
# downstream statics (OUT/REF/RUN reads)
grep -rln "456538" $W/P1/output/; sed contexts 42C6E8/42C6A0/42C510/42C628
grep -c "target=0x4241c0|4239e0" boot-t18-on.log     # 0 / 0
grep -oE "pc=0x42c[56]..." syscalls-t26-on.txt       # 0 in 785,356
# builds + suite (cwd discipline tabled)
cmake --build /tmp/p1-link/runtime --target ps2x_tests -j4            # baseline exit 0
cd "$R" && /tmp/p1-link/runtime/ps2xTest/ps2x_tests                   # 439/439/0 (build-dir cwd: 438/1 cwd artifact)
cmake --build ... --target ps2x_tests -j4                             # fix: attempt-1 sidecar FAIL, attempt-2 exit 0
cmake --build ... --target ps2EntryRunner -j4                         # exit 0 (×2: fix, fix+P0)
cd "$R" && .../ps2x_tests                                             # 443/443/0
shasum -a 256 .../ps2EntryRunner                                      # 72b2cfc5… 163483200 B
strings .../ps2EntryRunner | grep -c "\[k1\]|PS2X_FRAME_DUMP_DIR"      # 5 / 1
# fork commits (fork remote only; generated sources never staged)
git -C "$R" add <4 fix files>; git -C "$R" commit                     # fc75f70
git -C "$R" add ps2_runtime.cpp; git -C "$R" commit                   # b6252bb
git -C "$R" push fork ssx3                                           # 7eed783..b6252bb
```

Boot + analysis (lease held only for the boot line):

```text
python3 tools/trace_align.py --selftest                              # 35/35 ALL PASS
ls /tmp/ssx3-p-lane-lease; pgrep -x ps2EntryRunner                   # absent; exit 1
printf 'K1\n' > /tmp/ssx3-p-lane-lease                               # CLAIM 23:03:57Z
python3 /tmp/k1-boot1.py                                             # BOUND=wall 242 s rc=0 (lease held)
rm /tmp/ssx3-p-lane-lease; pgrep -x ps2EntryRunner                   # RELEASE 23:08:08Z; exit 1
grep "\[k1\]" boot-k1-1.log; grep -c "\[drop\]" boot-k1-1.log        # 16 lines; 0
grep -c "diag:watch" boot-k1-1.log                                   # 6 (copy proof; _kExecArg 0)
tail -n +872992 emulog-r1a.txt > /tmp/k1-r1a-game.txt                # R1A game epoch slice
for h in ...; do grep -cE "Bios call: .+ \($h\)" slice/trace; done   # censuses (K1-8/K1-10)
python3 (json) park-t26-1 vs park-k1-1 snapshots                     # park compare (K1-8)
python3 (struct/zlib) PNG distinct-RGBA + FNV recompute              # P0 inspection (K1-9)
```

## K1-13. Gaps + OPEN rows (coverage + remainder; box did not bind)

| # | Gap / OPEN | Detail | Next shape (not this brief) |
|---|---|---|---|
| G1 | `42C510` read (`0x42c520`) statically OPEN | Executes iff `42C628`-entry reaches its `0x42c65c` call; silent in-window (no event/park delta; `0x42c500–0x42c6FF` syscall-silent in 785k T26 events) | One static read of `42C628:0x42c628–0x42c65c` control flow, or a targeted `pc=`-in-hot-path probe; no boot needed unless it fires |
| G2 | ret0 retirement (successor question) | Needs convergence evidence: boot with real `0x42C1F0` showing marker search converges + `[0x455230]=0x80011F80` (+ recompiler regen of the stubbed TU — unexplored path) | Its own brief + boot (justifies boot 2 of a later box, per one-boot rule) |
| G3 | A1–A4 helper success shapes unvalidated dynamically | Unreached both paths; any future reach self-reports via `[k1] helper#` with args | Revisit if a helper line ever appears |
| G4 | First-*success* PNG missed | Numbered keeps consumed by seq 0–1 fallbacks; hash-equality (`fd889dc5` seq 13→3640) + settled PNG proxy it | Per-path keep counters in the dumper (2-line change) |
| G5 | 162/3641 dump lines unattributable | Pre-existing concurrent-log interleave (3.6% splice on this channel; impossible values prove splice, not content) | Bounded recent-event ring / locked logging (findings doc tooling row); P0 claims rest on clean lines + sidecars + PNGs |
| G6 | `_kExecArg` host-write coverage | WATCH sees guest-macro writes only; host memcpy/DMA/SIF bypass (P26-1h) | E3-shape host-write audit already covers the class (parked behind K1 per steering) |
| G7 | `0x12C` timer-3 structural difference | R1A installs it (alarm block); runtime HLE-collapses the alarm block; INTC counts within 1; downstream effect unknown | Alarm/timer/INTC contract brief (validate replacement, not counts) |
| G8 | Causal link fix→frame unestablished | Park SAME; settled frame black; helpers dormant both paths — the fix removes poison but nothing downstream consumed it in-window | Next behavior change must come from park evidence (findings hand-back Q3), not from K1 |
| G9 | `0x54→0x42D100` still installed+dormant | Out of K1 scope; would KE_ERROR-drop if `0x54` ever issued | Same-class follow-up if `(54)>0` ever observed |

## Evidence files

`REPORT.md` (this file), `k1-boot1.py` (boot script copy),
`k1_dis.py` (payload disassembler copy), `k1-liveness.log` (16 polls),
`upload-latest.png` (9,448 B) + `upload-latest.txt` (sidecar),
`fallback-0.png` (13,362 B) + `fallback-0.txt` (sidecar). SSD canonical
artifacts referenced by path (not duplicated): `RUN/boot-k1-1.log`
(528,891 lines, 92,925,537 B), `RUN/syscalls-k1-on.txt` (783,250 ev),
`RUN/park-k1-1/`, `RUN/frames-k1-1/`, `RUN/k1-waits.log` (2 lines),
`/tmp/k1-r1a-game.txt` (R1A slice; regenerable via K1-12 command).

## Tail receipt

Report written in 4 chunks (`write_file` + 3 `edit_file` appends);
tail verified intact:

```text
$ tail -3 local/research/K1/REPORT.md
trailer `Orchestrated-By: Muse Code`, no push (orchestrator pushes at poll).
End of K1 report.
```

Commit: `git add -f local/research/K1/…` (8 files), message `[K1] …`,
trailer `Orchestrated-By: Muse Code`, no push (orchestrator pushes at poll).
End of K1 report.
