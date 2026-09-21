# E3b — One-or-two-frame order capture (inv ordinals 999+1000)

Standalone evidence. Capture boot `boot-e3b-1` (BOUND=span, 31 s, 1/1 boots).
Span: two complete steady 362DE8 invocations (ordinals 999+1000; R1/R4SUM
`inv` labels read +1 — see Erratum E1). 1042 E3 rows, 0 torn, 0 suppressed.

## 0. Steering inputs (recorded verbatim per instruction)

Task brief: tables + hypothesis + next-action recommendation, no verdicts;
G0 gate satisfied (same park survived K1 — K1-8); implement E3-3 R1–R4 taps +
shared u64 seq + `PS2X_E3_INV`/`PS2X_E3_BYTES` binds, constraint C1 (never
force flag values); pre-capture re-verify (override table, K1 state, binding
deltas); scope ONE invocation expanding to ≤2 frames; fork commits to fork
remote only; lease-gated boots (≤2 × ≤600 s, wall+progress+BYTE caps);
evidence `local/research/E3b/` standalone, `[E3b]` prefix, no ssx3 push.

Frontier EVIDENCE CORRECTION (applied before capture):
1. `genFastWrite` constant-address FAST stores bypass the watch
   (`ps2TraceGuestWrite` no-op, no `diagWatchReport` in `Ps2FastWrite*`).
   Capture must cover relevant FAST stores or prove disjointness; zero R2
   rows alone cannot exclude them. → Closed statically: 0 FAST literals in
   0x501400–0x50144F across 9278 runner files (all wraps/aliases preserve
   the low digits); S structurally excluded (scratchpad=special→Store path);
   Font.cpp FAST (guest-controlled bufAddr) proven unwired (0 runner refs).
2. Overlap tests must normalize RAM/KSEG aliases + SPR offsets, split
   wrapped DMA, dedupe WRITE*/Store* doubles. → Done (mirror of
   `ps2ResolveGuestPointer`; `splitSpace` for the engine; src tags +
   adjacent-pair miner rule).
3. Negative results must report capture-complete + dropped/interleaved
   status. → §12 (all green).
4. FIRST-SUCCESS ADDENDUM (no separate boot): `PS2X_FRAME_DUMP_DIR` on the
   capture boot + K1 G4 per-path keep counters (first-N success AND
   first-N fallback); table first-success PNG in K1-9 sidecar shape. → §11
   (upload-16/17.png kept; K1 missed these).

## 1. Experiment contract

Hypothesis H (conjunction): (H_A) the single 395000-skip is caused by a
host SPR/SIF/file/CD/tick/stub write landing on live s1/R bytes in-window
(silent mutation, no watch line); (H_B) a guest write lands between R1
reads in-span (read-vs-write order); (H_C) neither — the watch's
"4-nonzero" is probe-attribution/lifecycle residue and the read-time state
shows exactly 1 nonzero (1 skip); (H_D) neither, but R1 shows 4-nonzero at
read time with 1 skip (branch-logic misread).
Observable: 40 R1 records (pre/post/outcome) + R2 guest writes (old/new,
src-tagged) + R3 host transfers (before/after slices) + R4 boundaries on
one shared seq; E3-4 rows 1–7 answered.
Alternatives: H_A→name the writer, brief fix/gate; H_B→caller-chain brief;
H_C→fix attribution, no SIF/CD/scheduler work; H_D→re-read check logic.
Stop: span-complete + all rows mined + E3-4 answered, or any cap (partial
tabled as gap). Verdict + ONE next action: §15.

## 2. G0 pre-capture re-verify (post-K1 tree, no boot)

HEADs: ssx3 `f3fd739`; fork `b6252bb` (K1 P0) + K1's `fc75f70` below.

### 2a. Override table (post-K1 contents)

| Syscall | Handler (post-K1) | Mechanism | HLE-live? |
|---|---|---|---|
| 0x55–0x59 | payload addrs (K1-8 install#4–8) | K1 equivalent serves | No (K1-shadowed, was KE_ERROR-drop) |
| 0x5A | 0x42CB78 guest loop | guest invocation, fires watch | n/a (guest) |
| 0x54/0x5B | 0x42D100 / 0x80075000 | guest / K1 lookup | No |
| 0x30/0x47/0x4B/0x6F, i-0x58/i-0x5A | none installed | HLE direct | Yes (statically) |
| D3/D4/D5 status | unchanged: still not HLE-live | drop→K1-helper | No delta in verdict |

### 2b. K1 dispatch state

`[k1]` armed at boot (applySsx3CopiedPayload); install#1–8 + lookup#1–6
present with payload addresses (no `0xFFFFFFFF` residue); helper liveness:
DORMANT — 0 `helper#` lines, (57)=0 in K1's 240 s trace (re-censused §5).

### 2c. Binding deltas vs E3 static rows (9278 runner files, was 9262)

All E3 §4 caller counts IDENTICAL (426D18=20, 426078=1, 4261B0=8,
4268F0=0, 3FFA58=2, 3FF708=2, 41605C=48, 41610C=15, 416210=175,
3FE320/3FE2B8/3FE268=0, 401DF8=3, 402520=2, 401FD8=1, 4027B8=1;
SifSetDma/sceVu0/StRead/IntToPos/StoreImage/SetDefDrawEnv/mbtowc=0;
SPR stores=10; SPR L1 ×1/L2 ×2 intact; window-func LibC=0; A6/E12/B8 hold).
Gaps closed: 402A10 sceMpegGetPicture 1 caller (sub_003B0FB8, LIVE),
402B58 Reset 0 (dead-direct); 402618 TrayReq 2 caller files (was uncounted).
Deltas: NONE affecting any DEAD/COND verdict except E9-GetPicture OPEN→YES.

### 2d. Line-number drift (E3-0 rec 3 — K1 hunks now committed)

`diagWatchEmit` 1187→1289 (+102 P0 hunk, committed); Store* 2480→~2616;
override impl 2685→2778; System.cpp K1 hook :440–452 committed; SPR
(:1569–1625), tick (:2579), VSync (:1974) unchanged.

## 3. Implementation (fork, lib-only; no shared-header changes)

New `ps2xRuntime/include/ps2_e3.h` (883 lines): env binds, armed state,
shared seq, frame/thread stamps, WATCH parse, normalization + wrap-split
overlap, Tap begin/end with before/after slices, byte cap, typed row emits.
R1 machine + dispatch switch in `ps2_runtime.cpp` (394ED0 open/close,
395000 outcome latch, 362DE8 counter/R4/summary); R2 old/new + src tags in
the watch-report path (WRITE*=macro, Store*=store, VSync=direct);
R3 taps at every §2 writer (SPR engine with explicit space intervals,
SIF/RPC/IOP chokes, fio/fstat/stat/ioctl, CD ×7, D4–D10, Pad ×4, MPEG ×7,
K1 helper, LibC ×12, MC ×8, RPC B7 ×13 + B14, Loader B13 ×3, SIF B2);
P0 per-path keep counters (first-2 success AND first-2 fallback).
Design mappings (recipe→code): R1 reads `[a1+off]` at 394ED0 entry
(a1==s1 verified 40/40) + post-read at close; R4 entries from dispatch,
exits backfilled from ps2_log (no `ps2_log.h` change — avoids runner
rebuild); FAST covered statically (§0.1); `PS2X_E3_S1BASE` checked, never
assumed. C1: all taps read-only (verified by diff review — no guest write
added). 20 lib files + 1 header + tests; `register_functions.cpp` (foreign
M) untouched. Method note: parallel same-file `edit_file` batches raced
in this environment (~1 edit lost per batch + EOF-append garbage in 7
files); all repaired sequentially and re-verified (tap counts + brace
balance + build). No concurrent lane (only E3b files dirty).

## 4. Build + suite records

| Step | Result |
|---|---|
| `cmake --build /tmp/p1-link/runtime --target ps2x_tests -j4` | exit 0 (24 steps, lib-only, no runner churn) |
| Suite (fork root) | 445/445/0 (443 K1 baseline + 2 new E3 cases, both pass) |
| `cmake --build ... --target ps2EntryRunner -j4` | exit 0 (relink) |
| Binary receipt | sha `607a3399c09ea30698163228fd46cda4501a837c182c1eaadb55af9549abb50`, 160795872 B (K1's was `7f155f4c` 163464560 B) |
| E3 row extract | `e3b-rows.txt` 1042 lines, sha `9c82041112a1c77b…` |

## 5. Lease + boot records

Pre-claim (T13-0 verbatim + K1 sha): lease absent; pgrep exit 1; ISO
3005415424 + ELF 3890784 (match); SSD 459 Gi + internal 15 Gi free; waits
tails released; suite 445/445/0. Claim/release logged to
`$W/P1/run/e3b-waits.log` (02:11:14Z → +31 s).

| Cap | Bind | Hit? |
|---|---|---|
| Wall | 600 s (`SECS`) | No (31 s) |
| Progress | 1M trace lines (`EVENT_CAP`) | No (98,650) |
| Bytes (LOG) | 800 MB (`BYTE_CAP`) | No (85.8 MB) |
| E3 bytes (in-module) | 8 MB (`PS2X_E3_BYTES`) | No (170,210 B, suppressed=0) |
| Span marker | `[e3:span-complete]` + 10 s grace | YES — BOUND=span, SIGTERM rc=0 |

Raws (single canonical copies, SSD): `boot-e3b-1.log` 85.8 MB,
`ps2_log-e3b-1.txt` 249.7 MB, `syscalls-e3b-1.txt` 5.9 MB,
`frames-e3b-1/` 12 files, `park-e3b-1/` 2 files. Left uncompressed (459 Gi
free; reviewer-readable). Baseline: K1 (park) + T26 (watch), by reference.
1/1 boots used; no boot-2 needed.

## 6. R1 — reads + branches (40/40; labels read +1, see E1)

All rows: a0=0x8095f0, ra=0x363240, src=0x363238, s1e==a1 (40/40),
preok=postok=1, base=ok, frame 1042/1043, thread 1. k=0–17: a2=0xb0;
k=18: a2=0xd0; k=19: a2=0x26. Closes k=0–18 at entry+1 (checks
undisturbed — every intervening seq is an R1 row); k=19 closes at the
next invocation's first 394ED0.

| n | ord | k | a1 | entry→close | pre (10,1C,1E) | out | post |
|---|---|---|---|---|---|---|---|
| 18642–18659 | 999 | 0–17 | 0x70001C00+k·0x80 | 40–74→+1 | 0x5dd,0,0 | call ×18 | same |
| 18660 | 999 | 18 | 0x70002500 | 76→77 | 0x5df,0,0 | call | same |
| 18661 | 999 | 19 | 0x70002580 | 78→537 | 0xffff,0,0x1 | SKIP | 0,0,0 |
| 18662–18679 | 1000 | 0–17 | 0x70001C00+k·0x80 | 580–614→+1 | 0x5dd,0,0 | call ×18 | same |
| 18680 | 1000 | 18 | 0x70002500 | 616→617 | 0x5df,0,0 | call | same |
| 18681 | 1000 | 19 | 0x70002580 | 618→1077 | 0xffff,0,0x1 | SKIP | 0,0,0 |

19 calls + 1 skip per invocation; skip = k=19 (terminator: a2=0x26,
+0x10=0xffff) both frames. Every pre-trio == the planting SPR-TO's
after-bytes (§8), k-by-k.

## 7. R2 — guest writes (864 raw → 432 solo; ALL macro+store, ALL scratchpad)

Dedupe rule (frontier #2): adjacent macro+store with identical
addr/width/newlo/newhi/pc/thread = 1 store. 432 pairs, 0 solo macro-only,
0 direct, 0 RAM (0x501420: 0 rows), 0 FAST (0 sites exist).

| pc | fn | n | region | seq range |
|---|---|---|---|---|
| 0x364170/78/7c, 0x3641e0 | sub_00364050 | 162 | ramp (stale) | 159–859 |
| 0x3792ac/e4, 0x3796b8/e4 | sub_00376938 | 184 | ramp 76 + live k0–3 | 346–1068 |
| 0x379a2c/44/84 | sub_00376938 | 6 | ramp | 530–1074 |
| 0x3e64d8/dc | sub_003E6448 | 80 | ramp (stale) | 79–697 |

Live-s1 R2 (68 solo, all seq ≥346 — strictly AFTER all 40 checks):
hammer k=0–3 windows post-read (9+ writes per window). Finals reproduce
T26's 4-nonzero residue exactly: k0 +0x1E=0x5000, k1–k3 +0x1E=0x8000
(all ≠0) — written after the loop read 0. No R2 touches k≥4 live flags.

## 8. R3 — host transfers (128 rows = 4 spr-to; nothing else)

Zero rows for: spr-from, pad, libc, cd, sif, rpc, iop, fio, mc, mpeg,
syscall-results, vblank-tick, k1-h57, elf. In-span LOG activity lines for
pad/sif/rpc/cd/libc/mpeg: 0 (neither fired in-window nor wrote in-window).

| Transfer | seqs | frame | MADR→SADR | size | nwin | Effect on live s1 |
|---|---|---|---|---|---|---|
| T1 | 0–39 | 1042 | 0x809670→0x1C00 | 7168 | 40 | PLANTS all flags (k19→0xffff,0,1) |
| T2 | 321–344 | 1042 | 0x876660→0x2000 | 8176 | 24 | Overwrites k8–19 (k19→0,0,0) |
| T3 | 540–579 | 1043 | 0x809670→0x1C00 | 7168 | 40 | PLANTS all flags (same skip) |
| T4 | 861–884 | 1043 | 0x876660→0x2000 | 8176 | 24 | Overwrites k8–19 |

T2 befores == T1 afters byte-exact (k8/k18/k19 verified) — zero
interleaved writes between plant and overwrite. Per-frame order: plant
(T1) → 20 reads (19 call + k19 skip) → stale-region guest writes →
overwrite (T2) → post-read guest rewrites (k0–3 residue). T1's befores
show previous-frame residue (replant overwrites stale data).

## 9. R4 — boundaries + s1 identity

| seq | inv(ord) | fn | ra | src |
|---|---|---|---|---|
| 345/885 | 999/1000 | 362CC8 | 0x377c08 | 0x377c00 |
| 536/1076 | 999/1000 | 363490 | 0x377b1c | 0x377b14 |
| 539/1079 | 999/1000 | 362DE8 | 0x3634d4 | 0x3634cc |

R4SUM: both invs nrec=20, s1min=0x70001C00, s1max=0x70002580, nbases=1,
drift=0 (steady stride, no aliasing/drift). ps2_log backfill (exact span
lines): 376938 ×60 enters (scheduler-direct — bypasses dispatch, R4 gap
G1 below; its STORES are captured in R2), 364050 ×2, 3e6448 ×0 (persistent
pre-span activation). Whole boot: 362DE8 1706=1706 balanced; 363490 5118
(3:1); 376938 49974. R4 inv labels are entering ordinals (correct).

## 10. E3-4 rows 1–7 answered

1. SPR overlap? YES (spr-to plants/overwrites live s1, 128 rows); spr-from:
   0 rows. 2. 0x501420 overlap? NO — 0 R2 RAM rows, 0 spr-from, MADR srcs
   elsewhere. 3. Read-vs-written? All 20 reads see SPR-planted values
   (pre == T1 afters k-by-k); k=0–18 undisturbed (close=entry+1); k=19
   planted (0xffff,0,1), read, skipped, then overwritten. 4. 1-vs-4?
   RESOLVED: 1 skip (k19 terminator, read-time +0x1E=1) vs 4-nonzero watch
   residue (post-read 0x379xxx rewrites at k0–3, read-time 0) — different
   lifecycle stages. 5. In-window host writes? The 4 spr-to only; all other
   R3 tags silent AND no in-span activity lines. 6. Scratchpad reuse?
   s1 stride exact both frames (nbases=1, drift=0); T1 re-plants over
   previous-frame residue each frame; no foreign reuse. 7. Post-K1 state?
   SAME: `[k1]` armed + install#1–8 (payload addrs) + lookup#1–6, 0 helper
   trips; trace (73)=0,(30)=1,(47)=0,(4b)=9,(6f)=3,(56/57/59)=0,(5a)=1 —
   identical to K1's census; park shape same (6 threads/16 semaphores).

## 11. First-success PNG (addendum; K1-9 sidecar shape + pmode)

Per-path keeps delivered: fallback-0/1.png + upload-16/17.png (K1 kept
only the two earliest = fallbacks). 444 dumps / 128 uploads in 31 s.

| file | seq | tick | bytes | dims | fbp | fnv1a | smode2 | pmode | sha16 |
|---|---|---|---|---|---|---|---|---|---|
| upload-16.png | 16 | 53 | 9448 | 512x448 | 112/112 | fd889dc5 | 0x1 | 0xff21 | 6120a759123a7440 |
| upload-17.png | 17 | 54 | 9448 | 512x448 | 112/112 | fd889dc5 | 0x1 | 0xff21 | 6120a759123a7440 |
| fallback-0.png | 0 | 0 | 13362 | 640x512 | 0/0 | af249dc5 | 0x0 | 0x0 | (rolling pair kept) |

upload-16/17 are byte-identical (static early frame). Keeps + sidecars
(`upload-16/17.png/.txt`, `fallback-0/1.png/.txt`) flat in-evidence, K1
shape; rolling latests + full dir only in P1/run/frames-e3b-1/.

## 12. Capture-complete + dropped/interleaved (frontier #3)

armed ×1 → 40/40 R1 (20/inv) → R4SUM ×2 (nrec=20) → span-complete ×1
(seq=1080, bytes=170210, suppressed=0); byte-cap ×0. Rows: 1042/1042
parsed, torn=0 (single-insertion emits + mutex; no splice). Seq accounting
exact: 1040 row-seqs + 40 entry-seqs = 1080 issued, min 0 max 1079, all
unique. R2 dedupe: 432/432 pairs merged (100% macro+store doubles — every
in-span guest store hit scratchpad-special path). No partial: every bound
except the span marker untouched.

## 13. Exact commands (abridged; full scripts in-evidence)

Pre-claim: `ls /tmp/ssx3-p-lane-lease` (absent); `pgrep -x ps2EntryRunner`
(exit 1); `ls -l` ISO/ELF; `df -h` SSD+Data; suite 445/445/0; waits tails.
Build: `cmake --build /tmp/p1-link/runtime --target ps2x_tests -j4`;
suite at fork root; `--target ps2EntryRunner -j4`.
Boot: claim lease → `python3 /tmp/e3b-boot1.py` (foreground, BOUND=span
31 s) → verify pgrep 1 → `mv ps2_log.txt ps2_log-e3b-1.txt` → release.
Mine: `python3 /tmp/e3b-mine{,2,3}.py`; greps in §§6–11.

## 14. Gaps / errata

E1 (inv labels +1): R1.inv/R4SUM.inv stamp the post-increment counter =
true ordinal +1 (span = ordinals 999+1000, relabeled in §§6–9; boundaries
+ seqs exact; armed marker fires mid-span — split by R4 entries, not it).
G1 (376938 R4 gap): scheduler-direct invocations bypass dispatchGuestBranch
(×60 in-span backfilled from ps2_log; stores captured — bounds only gap).
G2 (R4 exits): post-hoc from ps2_log (balanced 1706=1706), no shared seq —
entries suffice for order brackets. G3: 0x501420's purpose still open (17
init writes, never touched steady-state) — untouched by this capture.

## 15. Hypothesis verdict + ONE next action

H_A CONFIRMED (SPR-TO plants the skipped k19≠0 each frame) + H_C CONFIRMED
(T26's 4-nonzero is post-read guest-rewrite residue at k0–3, never read);
H_B/H_D falsified (no in-span write between plant and checks for k0–18;
read-time state shows exactly 1 nonzero). The skip is STRUCTURAL: k19 is
a terminator record (a2=0x26 vs 0xb0, +0x10=0xffff) skipped by design —
no anomaly, no corruption, lifecycle nominal (plant→read→overwrite→rewrite).
ONE next action: CLOSE G1 as explained — do not pursue SIF/CD/scheduler
writer fixes from this thread; the s1/R steady-state writer search is
complete (only residual: G3, 0x501420's purpose, iff the frontier names it).

---
Tail receipt: REPORT.md §§0–15 complete; e3b-rows.txt 1042 lines;
e3b-boot1.py + e3b-mine{,2,3}.py + 4 PNG keeps + 4 sidecars in-evidence.
Fork: b34b481 pushed fork ssx3 (21 files, +1621/−28; register_functions.cpp
398k-line regen left uncommitted — pre-existing P-lane state, not E3b).
Evidence `[E3b]` committed, unpushed (orchestrator pushes). Lease released
02:11:45Z, verified absent at close. No verdicts beyond the capture scope
(park/shape noted as observed, not gated).
