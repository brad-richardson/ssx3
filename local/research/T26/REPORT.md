# T26 report — Name the 0x501420 writer: init-only guest stores, 0 in-window writes (one 240 s leased boot)

Brief `local/muse/prompts/T26.md`. Tables, no verdicts.
Stale-reading guard: `local/research/A0/REPORT.md` §(ii-d) (the 20 B block
at `0x501420`: only cross-iteration state, writer open as gap G2 — this
brief names it) + A0 §(ii) (the 20 records' flag halfwords `+0x10/+0x1C/
+0x1E` on the s1 list) + P26's watch recipe (`PS2X_DIAG_WATCH` 8 B windows,
`ps2_runtime.h:269` + `ps2_runtime.cpp:1138`, reused verbatim as mechanism
with retargeted addresses) + `local/research/T22/REPORT.md` (the `pc=`
field, boot-proven by T24 — the syscall attribution channel).

`W=/Volumes/Extreme SSD/ps2recomp-spike`, `R=$W/PS2Recomp` (fork, branch
`ssx3`), `RUN=$W/P1/run`,
`TRACE=$RUN/syscalls-t26-on.txt` (785,356 lines, 46,963,370 B, sha
`16cd027e…93ba`), `LOG=$RUN/boot-t26-1.log` (6,764,707 lines, 705,357,230 B,
sha `3f00f7de…1236`),
`PLOG=$RUN/ps2_log-t26-1.txt` (39,248,128 lines, 1,394,136,084 B, sha
`94e4ae27…f9600`), `PARK=$RUN/park-t26-1` (json 111,635 B sha
`aac51344…28f68` + txt 7,621 B). `$R`-relative paths below unless noted.
Zero fork changes; no `adb`.

Headline readings: ONE writer-watch boot (240 s wall cap, BOUND=wall,
SIGTERM el=241 s rc=0, script exit 241) with 83 watch windows (3 for
`0x501420..0x501434` + 40 ramp-base + 40 steady-base s1 flag windows)
emits 6,245,425 `[diag:watch]` lines. Block `0x501420..0x501437`: 17 writes
from 11 pcs, ALL at log lines 49–275 (boot init: loader zero-init ×3,
`sub_00393048:0x393930` ×2, `sub_003691F8` 9 pcs ×12), ZERO writes during
the 72,176-lookup buildup window — the block is init-constant while the
hash loop runs. s1 flags (steady base `0x70001C00`, probe-confirmed s1 home
for n=140..19999): all `+0x10/+0x1C` flips complete by line ~27k (init, in
k order); during the window only per-invocation rewrites with stable values
(`+0x10` hw 0, `+0x1E` 0x5000/0x80 for k=0..3, 0 elsewhere) — 0 value flips
in-window. Routing: SIF/RPC no (writers precede the line-3706 handshake,
direct-jal boot chains, guest stores); CD/file no (guest stores, not host
completions; synchronous CD; boot-init chains) — neither, routes to E3.
Epoch: blocks 0–47 (b0=962/b1=497, 222×46, 235 absent), 14,423 VBLANKs
(59.8/s), 394ED0 287,122 (19.91/inv), 395000 272,699 (18.91/inv) — A0 shape
match. pc= 100.0000%, `--format-check` exit 0.

## T26-0. Lease / tree-state / build record

| Item | Value |
|---|---|
| ssx3 HEAD at T26 start | `6e3c5ac`, clean (ignored untracked only) |
| ssx3 HEAD at claim/boot/release | `6e3c5ac`, clean (no mid-boot motion observed) |
| ssx3 HEAD at commit | `7c8a68c` pre-commit (other lanes landed mid-run, offline, no P-lane interaction) |
| Fork HEAD throughout | `6359fb6` (T22's commit) + `M ps2xRuntime/src/runner/register_functions.cpp` (foreign, untouched) |
| Fork commits by T26 | 0; fork `git pull/push`: never run |
| Sidecars | 1 (`find $R -name "._*"`; T24's 51 → 1 tabled, untouched per zero-change rule; no build run) |
| Rebuild | NONE (tree at T22/T24 boot state; binary sha AND size identical — no build run) |
| Binary | `7f155f4cac62466c2535bc6987f64e0d2d31586ab21dd6b63c6a9998febdb377`, 163,464,560 B (IDENTICAL to T22/T24) |
| Boot env | T24 verbatim EXCEPT WATCH retargeted (83 windows) + LOG/TRACE/PARK names + `SECS` 240 + `EVENT_CAP` 1000000 (diff-verified vs `/tmp/t24-boot1.py`) |
| WATCH (83 windows) | `0x501420,0x501428,0x501430` (20 B block) + ramp `0x70000000+k*0x80+0x10/+0x18` k=0..19 (40) + steady `0x70001C00+k*0x80+0x10/+0x18` k=0..19 (40); full string in `watch-env.txt`; bases from T24 boot-mined a1 (ramp n=0..139, steady n=140+) |
| Monitor | liveness-only in-script (15 s polls to stdout + `/tmp/t26-liveness.log`, 16 polls + SIGTERM line; no trigger) |
| Caps | wall 240 s + progress 1,000,000 trace lines (event-count, T24 precedent); BOUND=wall (785,254 at last poll, 785,356 final) |
| Boots | 1 of 1 used (writer-watch boot; ≤240 s foreground) |
| Wall | 2026-09-20 ~19:50–21:10Z (~1.3 h active), inside the 4 h box |
| ssx3 evidence commit | below (`[T26]`, trailer `Orchestrated-By: Muse Code`, no push) |

Watch availability + pc= linkage IN the linked binary (E2a G1 lesson —
verified before claiming; all receipts against
`/tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner`):

| # | Receipt | Value |
|---|---|---|
| 1 | `strings` watch gate | `PS2X_DIAG_WATCH` ×1 |
| 2 | `strings` trace gates | `PS2X_TRACE_SYSCALLS` ×2 (base + `_PC` substring) + `PS2X_TRACE_SYSCALLS_PC` ×1 (= 1+1, T24's linked-binary row) |
| 3 | `strings` format literals | BOTH present: `[%8.4f] Bios    : Bios call: %s (%x) pc=0x%x` (on) + `[%8.4f] Bios    : Bios call: %s (%x)` (off) |
| 4 | `nm` symbols | `ps2DiagWatchEnabled` (T text) + `diagWatchEmit` + `ps2_syscalls::traceChannelEmit(unsigned int, unsigned int)` (T text) |
| 5 | `otool -v -t` disassembly | `bl traceChannelEmit` call site in dispatcher + function prologue |
| 6 | Watch semantics (source) | each WATCH addr names an 8 B window `[addr,addr+8)`; every guest macro write overlapping a window prints one `[diag:watch]` line with `pc=` = store insn pc (`ctx->pc` set before `WRITE*`), `thread/ra/sp`; host memcpy/DMA/SIF blits bypass (P26-1h); fires before the special-address check so scratchpad (`0x70000000`) is covered |

Lease record (`$RUN/t26-waits.log`, 2 lines; zero contention — absent at
claim, zero WAIT lines):

| Event | Value |
|---|---|
| T26 pre-claim checks (20:22:34Z) | Lease absent; `pgrep -x ps2EntryRunner` exit 1; sha `7f155f4c…` 163464560 B; watch `strings`+`nm` receipts; pc= `strings`+`nm`+`otool` receipts; ISO 3005415424 B + ELF 3890784 B (both `P1/SLUS_207.72` and `P1/cd/SLUS_207.72`; boot ELF = cd path); 496 Gi free; selftest 35/35 ALL PASS; t24/t20/e2a-waits tails = released; caps wall=240s progress=1000000lines |
| T26 claim | `printf 'T26\n' > /tmp/ssx3-p-lane-lease` 20:22:40Z |
| Boot | start ~20:22Z; 16 liveness polls (trace 46,798 → 785,254 lines, log → 705,338,964 B); SIGTERM el=241 s rc=0 BOUND=wall, script exit 241 |
| T26 release | 20:26:50Z (held 250 s); verified absent; `pgrep -x` exit 1 |
| Trace copy (lease-free) | `ps2_log.txt` → `ps2_log-t26-1.txt` (39,248,128 lines, 1,394,136,084 B); TRACE/LOG/PARK written direct by the runner |

## T26-1. Task 1 — writer-watch boot + epoch table (buildup ran?)

Boot artifacts (all `$RUN`):

| Item | Value |
|---|---|
| `boot-t26-1.log` | 6,764,707 lines, 705,357,230 B, sha `3f00f7de33155e91394779bd85db74a64325949956849411fdb2e009e4f81236` |
| `syscalls-t26-on.txt` | 785,356 lines, 46,963,370 B, sha `16cd027eacf998c14195a2a9834e07129bcd681c917d54495e0ca7b76d7493ba` |
| `ps2_log-t26-1.txt` | 39,248,128 lines, 1,394,136,084 B, sha `94e4ae271956813d08895a78531aaf611445b4154f2d5b4870c25f750bcf9600` (lease-free copy) |
| `park-t26-1/` | json 111,635 B sha `aac51344e04852396317302d476c2d6a082fcca04ee89810024b0ec747428f68` + txt 7,621 B (+ 2 macOS `._*` sidecars, gap G8) |
| `[trace:syscalls]` open line in log | present (channel-on receipt; `pc=` gate receipt = 100% `pc=` below) |
| `[diag:watch]` lines | 6,245,425 total (6,245,368 parsed + 57 unparseable interleaved `[frame:upload]` mid-line, gap G4); block 17, flags 6,245,351 |
| Rate | 785,356/241 s = 3,258.7 events/s (T18: 3,255.7/s; T24: 3,265.5/s) |

Epoch table (`[diag:stubs]` series, 48 lines, blocks 0–47; capture boot,
not exit boot — window labeled):

| Block | Stub distinct | Note |
|---|---|---|
| 0 | 962 | preamble (T24 961, +1 — gap G6) |
| 1 | 497 | preamble (T11/T24-exact) |
| 2–47 | 222 ×46 | phase steady, no deviation |

| # | Check | Receipt | Reading |
|---|---|---|---|
| 1 | Block 235 present | max block = 47; block 235 absent | no (not reached, not contradicted) |
| 2 | Preamble pair | b0=962, b1=497 | b1 exact; b0 +1 vs T24 |
| 3 | Steady distinct | 222 ×46 blocks 2–47 | in-phase throughout the window |
| 4 | `[diag:394ed0]` probe | nmax=19999 (cap 20000 reached); a1 ramp-base0 140 (n=0..139) + steady-base1c00 19,858 (n=140..19999) + 2 unclassified (gap G5); changeover n=140 at log line 23601 | T24-exact split (140/19860-class); s1 home confirmed in T26's own boot |
| 5 | Buildup (ps2_log census) | 362DE8 14,423/14,423 (59.8/s); 394ED0 287,122/287,122 (19.91/inv); 395000 272,699/272,699 (18.91/inv); 363490 43,267/43,267 (3N−2, mid-chain cut); 362CC8 14,423/14,423 (N) | match (A0 240 s: 14,349 / 285,642 / 271,293 / 19.91 / 18.91; T26 +74 inv) |
| 6 | Skip identity | 394ED0 − 395000 = 287,122 − 272,699 = 14,423 = N | exactly one 395000-skip per invocation (the +0x1E nonzero record — see gap G1) |
| 7 | Drops / SIF / CD | 6 drops (baselines); SendCmd `SET_SREG` 1× at line 3706; CD `lbn=` first at lines 95–96 | baselines kept; handshake/CD receipts for routing timing |

Proof table (pc= on-shape + parser — T24's channel reused):

| # | Item | Receipt |
|---|---|---|
| 1 | pc-on stream | 785,356 events, 46,963,370 B; head-200 200/200 carry `pc=`; full-file 785,356/785,356 (100.0000%), 0 unparseable (`proof.txt`) |
| 2 | `--format-check` | `syscalls-t26-on.txt`: events=785356 bad_hex=0 bad_ts_prefix=0 ts_regressions=0, exit 0 |
| 3 | pc= semantics (T24 limit, tabled) | syscall `pc=` = post-SYSCALL dispatch pc (wrapper+8 for wrapped calls); watch `pc=` = guest store-insn pc (`ctx->pc` at the `WRITE*` macro) — the writer attribution used below (OUT join for enclosing functions) |

## T26-2. Task 2 — writer tables (who writes? when? what flips?)

### Writer table: pcs writing `0x501420..0x501437` (all writers, ranked)

17 writes from 11 pcs, all at log lines 49–275 (boot init), thread 1;
ZERO writes at lines 276–6,764,707 (the buildup window). Full rows in
`watch.txt` (11 writer lines).

| pc | Enclosing function (OUT join) | Count | First line | Bytes touched (addr ×n, width) | Values (first→last) | ra |
|---|---|---|---|---|---|---|
| `0x10012c` | `sub_00100008` (entry/loader, 0x100008–0x1001c8) | 3 | 49 | `0x501420`×2 + `0x501430`×1, w16 | `0x0` (zero-init; covers 0x501420–0x50142F and 0x501430–0x50143F) | `0x0` |
| `0x393930` | `sub_00393048` (0x393048–0x394d50) | 2 | 62 | `0x501430`×1 + `0x501432`×1, w2 | `0xffff`, `0xffff` | `0x39710c` (`sub_003970F8`) |
| `0x3694a0` | `sub_003691F8` (0x3691f8–0x3695d8) | 2 | 268 | `0x501424`×2, w4 | `0xb00014` → `0xb00294` | `0x3693b8` (same fn, post-`jal 416210` @0x3693b0) |
| `0x3694a8` | `sub_003691F8` | 2 | 269 | `0x501420`×2, w4 | `0x0`, `0x0` | `0x3693b8` |
| `0x3694e8` | `sub_003691F8` | 2 | 272 | `0x501420`×2, w4 | `0x0`, `0x0` | `0x3693b8` |
| `0x36943c` | `sub_003691F8` | 1 | 264 | `0x501428`, w4 | `0x80` | `0x3693b8` |
| `0x369440` | `sub_003691F8` | 1 | 265 | `0x501424`, w4 | `0xb00000` | `0x3693b8` |
| `0x369448` | `sub_003691F8` | 1 | 266 | `0x501420`, w4 | `0x0` | `0x3693b8` |
| `0x369450` | `sub_003691F8` | 1 | 267 | `0x50142c`, w4 | `0x0` | `0x3693b8` |
| `0x369500` | `sub_003691F8` | 1 | 274 | `0x501430`, w4 | `0xffffffff` | `0x3693b8` |
| `0x369504` | `sub_003691F8` | 1 | 275 | `0x501430`, w4 | `0xffffffff` | `0x3693b8` |

Final block words (last-writer per word, lines 62–275; frozen for the
window): `[0x501420]=0x0` (l.273), `[0x501424]=0xb00294` (l.268–269),
`[0x501428]=0x80` (l.264), `[0x50142c]=0x0` (l.267),
`[0x501430]=0xffffffff` (l.275, covers `0x501430..0x501433`).
`0x501434..0x501437` (window-3 tail): loader-zeroed, 0 rewrites (gap G9).

Caller chains (static, OUT grep): `sub_003691F8` ← `sub_00395288` ←
`sub_00375A08` (sole chain); `sub_00393048` ← `sub_003970F8` (fired path,
ra receipt; 3970F8 has no direct caller — indirect) + `sub_00396128` ←
`sub_00363490` + `sub_00397118` (no direct caller). No SIF/RPC/CD strings
in any writer file; `sub_003691F8` calls `416210` (14-line stub) ×3 +
`3E6448` ×1; `sub_00393048` calls `416210` + `392DF0` + `38F300` +
`38AE28` + `317xxx` ×4.

### Flag table: per-record halfword flips (steady base = s1 during window)

Steady base `0x70001C00+k*0x80` (k=0..19) is the probe-confirmed s1 home
for n=140..19999 (changeover line 23601; assumed for the rest — gap G2).
`+0x10` hw = low hw of writes starting at `+0x10`; `+0x1C` hw = value of
writes starting at `+0x1C` (w4); `+0x1E` hw extracted from covering writes
(`+0x18`w8 top hw, `+0x1C`w4 high hw) — 0 writes start exactly at `+0x1E`.
`halfword.txt` (82 lines) + `flagdeep.txt` (80 lines) hold every cell.

| k | `+0x10` hw (n, values in order) | `+0x1C` hw (n, values) | `+0x1E` hw (n, values) | Last flip line (all fields) |
|---|---|---|---|---|
| 0 | 258,542× `0x0` (no flip; per-inv rewrite pc `0x3796e4`) | 128×`0x0` → 23×`0x1` (pcs `0x364170`/`0x3641e0`) | `0x0` → `0x6c0e` (24×) → `0x5000` (258,261× per-inv rewrite pc `0x3796b8`) | ~23,568 |
| 1 | 143,655×`0x0` + 128×`0x1` (order `0,1`; per-inv `0x3792ac`) | 128×`0x1` | `0x0` → `0x80` (143,479× per-inv rewrite pc `0x3792e4`) | ~23,455 |
| 2 | 57,518×`0x0` + 128×`0x1` (per-inv `0x3792ac`) | 128×`0x1` | `0x0` → `0x80` (57,392× per-inv) | ~23,479 |
| 3 | 28,823×`0x0` + 128×`0x1` (per-inv `0x3792ac`) | 128×`0x1` | `0x0` → `0x80` (28,696× per-inv) | ~23,503 |
| 4–7 | 128×`0x0` → 128×`0x1` (frozen; pcs `0x3e64d8`/`0x364170`) | 128×`0x1` | `0x0` (256×, frozen) | ~23,507–23,567 |
| 8,10,11,12 | 256×`0x0` (frozen) | 128×`0x0` (frozen) | `0x0` (256×, frozen) | ~23,411–23,517 |
| 9 | 258×`0x0` → 2×`0xf800` (pc `0x366364/98`, line ~27,091) | 128×`0x0` → 2×`0xffffffff` → 2×`0x6` (pc `0x366370/88`) | `0x0` → 2×`0xffff` | ~27,091 |
| 13,14,15 | 232×`0x0` → 24×`0x2` | 104×`0x0` → 24×`0x2` | `0x0` (256×, frozen) | ~23,521–23,565 |
| 16–19 | 128×`0x0` → 104×`0x1` → 24×`0x2` | 104×`0x1` → 24×`0x2` | `0x0` (256×, frozen) | ~23,409–23,497 |

First-flip order (init, in k order — lookup order): `+0x10` first lines
665 (k=0), 669 (k=1), …, 743 (k=19), +2/record; `+0x1C` first lines
761–903 interleaved k order. All value flips complete by line ~27,091
(0.4% into the log); during the window (lines 27,091–6,764,707) the only
flag writes are per-invocation rewrites with STABLE values (k=0..3
`+0x10`/`+0x1E` from `sub_00376938` pcs `0x3796e4/b8/ac/e4`, 18/10/4/2 per
inv) — 0 value flips in-window. Per-invocation writer pcs all resolve to
`sub_00376938` (the VBLANK driver, 0x376938–0x37a260; ra `0x3790b4`);
init pcs to `sub_00364050` (`0x364170/78/7c/e0`, ra `0x3640b8`) +
`sub_003E6448` (`0x3e64d8/dc`, ra `0x3640b8`) + `sub_003662D0` (k=9 only)
+ `sub_00368170/4F0` (ramp init 6× each).

Ramp base (`0x70000000`, s1 home ONLY for n=0..139, lines <23,601; all
later ramp-base writes are non-s1 scratchpad reuse): ramp-phase s1 writes
are k=0..2 `+0x10/+0x18` (first lines 905–915; `+0x10` hw order
`0x4/0x8001/0x40 → 0x0 …`, `+0x1E` k=0 `0→6c0e→5000` consistent with the
ramp 2/1 skip); `+0x1C` has ZERO ramp-phase writes (first lines 23,699+,
all post-changeover reuse). Post-changeover ramp traffic (57,436/inv-class
per window from `0x3e64d8` + `0x364170/78/7c`, last line 6,764,xxx) is
tabled in `watch.txt`/`flagdeep.txt`/`halfword.txt` but excluded from the
s1 census.

### Routing table: SIF/RPC-delivered? CD/file completion? neither?

| # | Hypothesis | Code path tabled each way | Reading |
|---|---|---|---|
| 1 | SIF/RPC-delivered (→ P1ae) | Writers fire at lines 49–275; the SIF `SET_SREG` send is at line 3706 (after all writers); writer chains are direct-jal boot code (`375A08→395288→3691F8`; `3970F8→393048`), not SIF dispatch (HLE SIF dispatch nonexistent per P26-1h: `g_sifCmdHandlers` write-only, no SIF0 emulation); writers are guest stores, SIF delivery would be host-side (bypass) | no |
| 2 | CD/file completion (→ CD callback) | CD `lbn=` starts line 95 (loader + `0x393930` precede it; `0x369xxx` at 264–275 follow it but via the boot-init chain `375A08→395288→3691F8`, ra intra-function post-stub-jal — not a CD callback); CD reads are synchronous (`ret=` immediate); a file-completion write would be a host memcpy (watch bypass), but all 17 writers are guest stores (watch fires) | no |
| 3 | Neither (→ E3) | 11 init-only guest-store pcs (loader + 2 init functions), 0 writes during the 14,423-invocation buildup; block is init-constant while the hash loop runs; flag flips likewise complete in init with 0 in-window flips | YES — routes to E3 |

## T26-3. Exact commands

From `/Users/bradrichardson/dev/ssx3` unless noted; `$R`, `$W` quoted
(path contains a space):

```text
# Recon (lease-free, read-only streams)
read local/research/A0/REPORT.md (ii-d + ii) + local/research/T22/REPORT.md (all) + local/research/T24/REPORT.md (all) + P1 Part 26 (P26-1h/2a watch recipe)
read fork ps2_runtime.h:269 + ps2_runtime.cpp:1138 (WATCH 8 B windows) + macros.h:361-428 (watch-before-special) + ps2_runtime.cpp:1252 (store-pc)
mine T24 boot-t24-1.log [diag:394ed0] a1: 23 distinct (base0 0x70000000 n=0..139 + steady 0x70001C00+k*0x80 n=140..19999, 20 records)
git rev-parse HEAD (6e3c5ac) + status (clean); fork rev-parse (6359fb6) + branch (ssx3) + status (foreign M only)
shasum binary (7f155f4c…b377 163464560B = T24, no rebuild)
strings PS2X_DIAG_WATCH x1 + TRACE gates + both pc literals; nm ps2DiagWatchEnabled(T) + traceChannelEmit(T); otool bl+prologue (pre-boot linkage)
stat ISO 3005415424 + ELF 3890784 (both ELF paths); df 496Gi free
python3 tools/trace_align.py --selftest (35/35 + ALL PASS)
tail t24/t20/e2a-waits.log (released/released/released)
# Boot script + miners (lease-free)
write /tmp/t26-boot1.py (T24 env + WATCH=83 windows + SECS 240 + EVENT_CAP 1000000 + t26 names; diff-verified vs /tmp/t24-boot1.py)
write + py_compile /tmp/t26-watch.py /tmp/t26-epoch.py /tmp/t26-proof.py (/tmp/t26-flagdeep.py /tmp/t26-halfword.py post-boot, lease-free)
# Boot (lease T26 held 20:22:40-20:26:50Z, 250 s)
pre-claim checks; printf 'T26' > /tmp/ssx3-p-lane-lease; append t26-waits.log CLAIM
python3 /tmp/t26-boot1.py (foreground; 16 polls; SIGTERM el=241s rc=0 BOUND=wall, exit 241)
rm /tmp/ssx3-p-lane-lease (verified absent; pgrep 1); append t26-waits.log RELEASE
# Analysis (lease-free)
cp ps2_log.txt ps2_log-t26-1.txt (39248128 lines, 1394136084 B)
shasum TRACE (16cd027e…93ba) + LOG (3f00f7de…1236) + PLOG (94e4ae27…f9600) + park json (aac51344…28f68)
t26-watch.py (17 block writes 11 pcs lines 49-275 + 160 flag rows) + t26-flagdeep.py (widths/values/last) + t26-halfword.py (+0x10 low-hw, +0x1E extraction)
t26-epoch.py (blocks 0-47; probe 140/19858; trace 785356) + t26-proof.py (100.0000% pc, 200/200) + --format-check TRACE (exit 0)
ps2_log census (362DE8 14423 / 394ED0 287122 / 395000 272699 / 363490 43267 / 362CC8 14423)
OUT join (9085 func headers; 41 pcs → functions) + caller greps (3691F8/393048/3970F8/395288/396128/397118) + callee greps + SIF/CD string grep (NONE)
SendCmd line (3706) + CD first (95-96) + drops (6) + changeover line (23601) + unparseable sample (57 frame-upload interleaves)
# Evidence
stage 7 txt to local/research/T26/ (watch/flagdeep/halfword/epoch/proof/liveness/watch-env)
write REPORT.md in 4 chunks; tail receipt; git add -f local/research/T26/; commit [T26] (no push)
```

## T26-4. Gap rows

| # | Gap | Detail |
|---|---|---|
| G1 | 1-skip vs 4-nonzero puzzle (open) | Trace proves exactly one 395000-skip per invocation (394ED0−395000=N=14,423); watch shows steady k=0..3 `+0x1E` stable-nonzero (`0x5000`/`0x80`, per-invocation rewrites to end). Naively 4 skips (16/inv), observed 1 (19/inv). Needs within-VBLANK read-vs-write order (362DE8 reads vs `0x379xxx` writes) + host-clear audit (guest stores all fire the watch; a host scratchpad clear would bypass it) |
| G2 | s1 base after probe cap unwitnessed | Probe caps at n=20000 (~1000 inv); s1=steady base confirmed to n=19999, assumed for inv 1000–14423 (producer `0x379xxx` writes steady k=0..3 to end supports it; third-base drift possible but unwitnessed) |
| G3 | Ramp-phase s1 `+0x1C` never written | 0 ramp-phase (lines <23,601) writes to ramp `+0x1C` (first 23,699+, all reuse); ramp reads see init values (scratchpad init unwitnessed — loader `0x10012c` w16 zeroes RDRAM windows; scratchpad zeroing not traced) |
| G4 | 57 unparseable watch lines | Interleaved `[frame:upload]` mid-line truncations (all flag addrs, 0 block); counted in the 6,245,425 total, excluded from tables (resident 0.0009%) |
| G5 | 2 probe lines unclassified | 140 ramp + 19,858 steady = 19,998 vs 20,000 probe lines (n=0..19999); likely SIGTERM-truncated tail lines (0.01%) |
| G6 | b0=962 (+1 vs T24 961) | b1=497 exact; steady 222×46 exact; +1 stub in block 0 (timing noise class, tabled) |
| G7 | Sidecars 1 (T24: 51) | Tabled, untouched per zero-change rule; no build run, no interaction |
| G8 | Park-dir AppleDouble pair | `._park-snapshot.json` + `._park-snapshot.txt` (macOS-created, runner-external); snapshot bytes unaffected |
| G9 | `0x501434..0x501437` tail | Window-3 covers 4 B past the 20 B block; loader-zeroed, 0 rewrites (clean) |
| G10 | Session wall | ~1.3 h active of the 4 h box; zero lease waits (absent at claim) |

## Evidence files

`REPORT.md` (this file), `watch.txt` (174-line writer + flag miner output),
`flagdeep.txt` (80-line widths/values/last per exact field), `halfword.txt`
(82-line `+0x10` low-hw + `+0x1E` extraction per record), `epoch.txt`
(4-line blocks/probe/trace), `proof.txt` (1-line pc= share),
`liveness.txt` (18-line boot liveness + BOUND), `watch-env.txt` (83-window
WATCH string). Full-size artifacts stay on the SSD by path+sha:
`syscalls-t26-on.txt` (46,963,370 B), `boot-t26-1.log` (705,357,230 B),
`ps2_log-t26-1.txt` (1,394,136,084 B), `park-t26-1/` (111,635 + 7,621 B),
binary `7f155f4c…b377` (163,464,560 B).

## T26-5. Tail receipt (F3 rec 17)

Report written in 4 chunks; closing 3 lines quoted verbatim below
(`tail -3 local/research/T26/REPORT.md` at commit):

```text
T26 evidence complete: init-only 0x501420 writers + frozen s1 flags (neither — routes to E3).
Trailer: Orchestrated-By: Muse Code.
End of T26 report.
```

T26 evidence complete: init-only 0x501420 writers + frozen s1 flags (neither — routes to E3).
Trailer: Orchestrated-By: Muse Code.
End of T26 report.
