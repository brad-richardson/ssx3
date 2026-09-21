# AC1 report — 0x12 alarm/timer/INTC contract validation (read-only)

Brief `local/muse/prompts/AC1.md` (K1 G7). Tables, no verdicts.
`R=/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp` (fork, branch `ssx3`,
read-only), `W=/Volumes/Extreme SSD/ps2recomp-spike`, `E=/Volumes/Extreme
SSD/ps2x-t4/emulog-r1a.txt` (991,575,587 B reference), `K=$W/P1/run`
(runtime traces), ELF `$W/P1/SLUS_207.72`, `OUT=$W/P1/output`.
Read first per brief: K1 §K1-10/§K1-13-G7 + refinement-2 correction
(`InitAlarm@0x42C7C8` + `InitThread` HLE collapse — semantics, not counts).
Time box 3 h; session wall ~02:55–04:05Z 2026-09-21 (~2.5 h, inside the box).

Headline readings: guest `InitAlarm` fully decoded from ELF (54 insns,
0x42c7c8–0x42c8a0): T3.CMPE guard, 8 SetSyscall / 6 GetEntryAddress /
2 Copy / 2 FlushCache, 0x740 B payload to `0x80076000`, 0x28 B stub to
`0x82000`; payload = 6-pair lookup + Set/Cancel bodies + T3 ISR
(`0x80076488`, installed via the `SetSyscall(0x12C)` INT12 trick per Play!)
+ ERET/stub/`(-8)` callback path. HLE replacement = `KE_OK` no-op init +
live scheduler alarms (64 µs/tick) + 4-timer emulation + IRQ dispatch.
In-window both sides SET and FIRE alarms: R1A 379 `(fc)` → 379 `(8)`
(all caller #2 `3E52B0`); K1 21 `(fc)` → ≥20 fired via `(43)` (caller #1
`3E35B0` ×20 + caller #2 ×1). INTC triple: identical driver order, K1
lacks only the phase-late cause-3 re-add. `0xFD/0xFF/0x12C/ cause-12`:
zero issuers both sides.

## AC1-0. Rule record + experiment contract

| Item | Value |
|---|---|
| ssx3 HEAD at start | `57487ca` (AC1 brief; tree clean) |
| Fork HEAD (read-only) | branch `ssx3`, never written, never committed |
| Evidence dir | `local/research/AC1/` standalone (`REPORT.md` + `ac1_dis.py`) |
| Boots / lease / fork writes / `adb` / push | 0 / none / 0 / unused / never (orchestrator pushes at poll) |
| `COPYFILE_DISABLE=1` | exported on every SSD step (reads only) |
| Miners | `/tmp/ac1_dis.py` (gap-tolerant `a0_elf.py` descendant, read-only ELF) + `/tmp/ac1_*.txt` dumps (regenerable, not committed) |
| Play! source | read-only web fetch of pinned `PS2OS.cpp@83700b2c` (semantics citation, no code copied) |

| Contract slot | Value |
|---|---|
| Hypothesis | The HLE collapse preserves the observable alarm contract (set → fire once with arg intact); the missing `0x12C` has no in-window downstream consumer beyond the replaced path |
| Observable | Per-effect contract rows (guest bytes vs HLE source) + caller/reader census from committed + canonical traces |
| Alternatives | (a) a guest effect with no HLE counterpart and an in-window consumer → DIVERGENT with named consequence; (b) statically unresolvable → OPEN with exact probe |
| Stop | All guest-block effects tabled with dispositions; all timer-3 consumers named or bounded; gaps carry exact probes |

## AC1-1. Guest alarm block decode (`InitAlarm`, ELF `0x42c7c8–0x42c8a0`, 54 insns)

CSV `ssx3-functions.csv:8227` (`0x42c7c8,0x42c8a0,0xd8`); TOML
`games/ssx3/ssx3.toml:26` (`stubs = [`), `:196` (`InitAlarm@0x0042C7C8`),
`:141` (`InitThread@0x00424B78`), `:207` (`ret0@0x0042c1f0`).
Wrappers: `0x42C760` = SetSyscall (v1=0x74), `0x42C770` = Copy (v1=0x5A),
`0x42C7B8` = GetEntryAddress (v1=0x5B), `0x424020` = FlushCache (v1=0x64),
`0x42C780` = kCopy word loop (CSV/TOML `kCopy@0x0042C780`).

| # | PC | Action (from ELF bytes) |
|---|---|---|
| 1 | `0x42c7cc–ec` | Guard: `lw $v1,[0x10001810]` (T3_MODE, cached); `andi 0x100` (CMPE); `bnez → 0x42c888` epilogue = already-initialized skip |
| 2 | `0x42c7f8–0c` | `s2=2`, `s0=0x456180`, `s1=0x456190`; `SetSyscall([0x456180]=0x5A, [0x456184]=0x42C780)` via `0x42C760` |
| 3 | `0x42c810–24` | `Copy(dst 0x80076000, src 0x455A18, size 0x740)` via `0x42C770` (alarm payload → KSEG0) |
| 4 | `0x42c828–3c` | `Copy(dst 0x82000, src 0x456158, size 0x28)` via `0x42C770` (callback stub → low RAM) |
| 5 | `0x42c840–4c` | `FlushCache(0)`, `FlushCache(2)` via `0x424020` |
| 6 | `0x42c850–58` | `SetSyscall([0x456188]=0x5B, [0x45618c]=0x80076000)` |
| 7 | `0x42c85c–80` | Loop, `s2=2→8` = 6 iters, `s1=0x456190+8k`: `v0=GetEntryAddress([s1])`; `SetSyscall([s1],v0)` for `0xFC,0xFE,0xFD,0xFF,0x12C,0x08` (`[0x456190–1B8]`, zeros interleaved) |
| 8 | `0x42c884–98` | Epilogue: restore `ra/s2/s1/s0`, `jr ra` |

Trace join (R1A game epoch): 8×`(74)` a0=`5a/5b/fc/fe/fd/ff/12c/8` @pc
`42c768`, 6×`(5b)` a0=`fc/fe/fd/ff/12c/8` @pc `42c7c0`, 2×`(5a)`
a0=`80076000/82000` @pc `42c778` — the 8/6/2 shape verbatim
(`r1a-game.txt:16–31`).

### Payload map (copied `0x455A18–0x456158` → `0x80076000–0x80076740`)

Lookup head `+0x0`: linear search 6 pairs at `0x80076710` (src
`0x456128`), hit → value, miss → 0 (disasm `ac1` dump lines 1–13).
Zero `syscall` insns in all 464 payload words; all 9 `jal` targets
internal (`+0x80000000`).

| Dst entry | Serves | Role (decoded) | HW / mem effects |
|---|---|---|---|
| `0x80076000` | `0x5B` (GetEntryAddress) | 6-pair lookup | read-only (`0x80076710–3F`) |
| `0x80076038` | internal | time-compare w/ wrap (`a1<a0 → a1\|0x10000`) | none |
| `0x80076058` | internal | sorted-insert position + memmove (stride `0x14`) | alarm table `0x80076700(count)/0x80076740(entries,BSS)` |
| `0x80076160` | via FC/FE | **SetAlarm body**: `expiry=(a0&0xffff)+T3_COUNT`; bitmap alloc (`0x80076708`, ≤64); count++; entry `{id,time,bitidx,handler,arg,gp}`; rearm via `0x80076460`; return id/`-1` full | `R [0xb0001800]` T3_COUNT; `W T3_COMP=a0, T3_MODE=0x583` (CLKS=3,CUE,CMPE,EQUF) |
| `0x800762A0` | `0xFD/0xFF` | **CancelAlarm body**: scan id; remove+compact; count−−; bitmap clear; head→rearm; empty→`T3_MODE=0x83`; `-1` if `T3_COMP==time` and `INTC_STAT.12` pending | `R [0xb0001820]` COMP, `R [0x1000f000]&0x1000` (TIMER3 pend); `W MODE` |
| `0x80076440` | `0xFC/0xFE` | SetAlarm entry: `jal 0x80076160` (`a0&=0xffff`, `a1/a2/gp` passthrough); `v1` unread → FC≡FE | via `0x80076160` |
| `0x80076460` | internal | T3 arm: `T3_COMP=a0; T3_MODE=0x583; jr ra` (7 insns) | `W [0xb0001820], [0xb0001810]` |
| `0x80076488` | `0x12C` | **T3 ISR**: scan table; per expired entry clear bit, `gp=entry.gp`, `jal 0x80076680(a0=0x82000,…)`; loop; more→rearm head, none→`T3_MODE=0x483` (CMPE off); `sync; EI(0x42000038); jr ra` | `R table/COMP`; `W MODE/COMP`; callback via ERET path |
| `0x80076680` | internal | callback dispatch: save `ra/sp→[0x80076c40/50]`; `EPC=0x82000`; `Status\|=0x12`; `eret` | `W COP0 EPC/Status`; `W slots` |
| `0x800766C0` | `0x08` | interrupt-exit: `Status&=~0x1c`; `ra/sp=[slots]`; `jr ra` (→ ISR resume) | `W COP0 Status` |
| `0x82000` (stub) | via EPC | `sp=0x81FC0; jalr v1(callback); v1=-8; syscall` | issues `(-8)` → `0x800766C0` |

Pair table (src `0x456128`, dst `0x80076710`): `FC→80076440`,
`FE→80076440`, `FD→800762A0`, `FF→800762A0`, `12C→80076488`,
`08→800766C0`. Alarm count init `[0x456118–24]=0`.

## AC1-2. Guest `InitThread` + `0x12C` semantics (Play!)

Guest `InitThread` (ELF `0x424b78–0x424c50`, 54 insns; CSV
`sub_00424B78,0x424b78,0x424c50,0xd8`):

| # | PC | Action |
|---|---|---|
| 1 | `0x424b88–8c` | If `[0x455170]>0` → return `-1` (already-init) |
| 2 | `0x424b94–a8` | `CreateSema(sp+0x30)` (init `0xff`) via `0x423DA0`; `<0` → `-1`; id→`[0x52B3A0]` |
| 3 | `0x424bb4–e8` | `CreateThread(sp)` via `0x423BA0`: func `0x424AA0`, stack `0x52AFA0/0x400`, gp `0x4A30F0`; id→`[0x455170]`; `<0` → `DeleteSema` + `-1` |
| 4 | `0x424c08–1c` | `StartThread(id, 0x52B3A8)` via `0x423BC0` |
| 5 | `0x424c20–2c` | `GetThreadId()` + `ChangeThreadPriority(self,1)` via `0x423C90/0x423C30`; return `[0x455170]` |

Trace join (R1A): g25–g29 = `CreateSema(40)@423da8`,
`CreateThread(20)@423ba8`, `StartThread(22)@423bc8`,
`GetThreadId(2f)@423c98`, `ChangeThreadPriority(29)@423c38`
(`r1a-game.txt:32–36`).

`SetSyscall(0x12C)` semantics per Play! `PS2OS.cpp@83700b2c`
(`sc_SetSyscall`, fetched verbatim): `number<0x100` → custom table
slot; `number==0x12C` → allocate INTC handler, `address&0x1FFFFFFF`,
`cause=12` (timer 3), `arg=0`, `gp=0`, set `INTC_MASK` bit 12,
queue-front. Comment: *"the BIOS doesn't process custom INTC handlers
for INT12 (timer 3) and the only way to have an handler placed on that
interrupt line is to do that trick"* (a libcdvd version does this).
So on HW the guest's `SetSyscall(0x12C, 0x80076488)` installs the T3
ISR on INT12 **and unmasks it** — not an ordinary syscall slot.
Play! also notes the BIOS enables TIMER2/3 for alarms
(`Reset()`: `T3_MODE=CLOCK_SELECT_EXTERNAL|COUNT_ENABLE|EQUAL_FLAG|OVERFLOW_FLAG`).

## AC1-3. HLE replacement (source)

| # | Component | Behavior (source lines) |
|---|---|---|
| H1 | `InitAlarm` HLE | `setReturnS32(ctx, KE_OK)` only — no state, no installs, no copies, no timer touch (`Sync.cpp:399–402`) |
| H2 | `InitThread` HLE | `setReturnS32(ctx, kMainThreadId=1)` only (`Thread.cpp:184–187`, `ee_scheduler.h:257`) |
| H3 | `SetAlarm` (`0x18/0xFC`) | `scheduler.setAlarm(ticks=a0u16,handler=a1,arg=a2,gp,sp)`: `hasFunction` gate else `KE_ERROR` drop; alloc id; event at `eeCycle+ticks×64µs` (`Dispatcher.cpp:160–163`, `EeScheduler.cpp:1694–1720`, `:55` 64 µs) |
| H4 | `CancelAlarm` (`0x19/0xFE`) | `scheduler.cancelAlarm(id)`; unknown id → `KE_ERROR` (`:164–167`, `:1722–1740`) |
| H5 | i-variants | `-0xFD→iSetAlarm`, `-0xFF→iCancelAlarm` (same bodies); **`+0xFD/+0xFF/+0x08/−0x08/0x12C` → `default: unknown-syscall` drop** (`:168–177`, `:414`) |
| H6 | Alarm fire | `GuestInvocationKind::Alarm`: `pc=handler,a0=id,a1=ticks,a2=arg,gp,sp=reserved(invocationStackTop),ra=0` (`:2639–2660`) |
| H7 | Timer emu | 4 timers (bases `0x10000000/800/1000/1800`, COUNT/MODE/COMP `+0/10/20`); MODE `CLKS[1:0] ZRET6 CUE7 CMPE8 OVFE9 EQUF10 OVFF11`; clocks `{147456000,9216000,576000,15734}` Hz; CUE-gated advance; CMPE+!EQUF→irq bit; guest R/W routed (`ps2_memory.cpp:169–194,1129–1160,2272–2290,428–555`) |
| H8 | Timer→IRQ | `advanceEeTimers` mask → `dispatchIrq(false, 9+timer)` (T3 = cause 12) (`EeScheduler.cpp:858–859,2454–2460,2765–2796` deadline) |
| H9 | INTC HLE | `addIrqHandler` (no cause/address validation, id alloc); `setIrqCauseEnabled` (cause<32, else `cause-range` drop + `KE_OK`); `dispatchIrq` (mask-gated; `hasFunction`-gated else `no-table-entry` drop; `GuestInvocation` `a0=cause,a1=arg`, reserved sp) (`Interrupt.cpp`, `EeScheduler.cpp:1824–1990`) |
| H10 | Override table | unbounded map; mirror `rdram[0x11F80+idx×4]` iff `<0x80000` (`0x12C→0x12430` would mirror); `handler==0` erases (`ps2_runtime.cpp:3032–3060`) |
| H11 | `GetEntryAddress` HLE | returns mirror word `kGuestSyscallTableGuestBase+num×4` (0 if unmapped) (`System.cpp:1020–1030`) |
| H12 | `Copy` HLE | `memcpy` + trace + return 0 (`System.cpp:1001–1017`) |
| H13 | Trace channel | `call = low byte` (`-x→x`); `call≥0x80` → `RFU%03u` (`(fc)`=`RFU252`); **`0x12C prints as `(2c)`** (`TraceChannel.cpp:126–155`) |

## AC1-4. Contract table (guest effect vs HLE replacement)

Dispositions: EQUIVALENT (proof line) / DIVERGENT (consequence) /
OPEN (exact probe). Guest refs = AC1-1 steps; HLE refs = AC1-3 rows.

| # | Guest effect | HLE effect | Disposition |
|---|---|---|---|
| C1 | Re-entry guard: skip if `T3.CMPE` set (step 1) | No guard; init body empty, always `KE_OK` (H1) | EQUIVALENT — proof: both re-entries are observable no-ops (guest skips body; HLE body is empty; return `0` both) |
| C2 | `SetSyscall(0x5A→0x42C780)` (step 2) | Slot untouched by init | DIVERGENT — consequence: none in-window (transient: main installer overwrites `0x5A→0x42CB78` on R1A too; no other Copy between; K1 Copy served by H12) |
| C3 | Payload copy `0x80076000` (step 3) | Region stays zero | DIVERGENT — consequence: `0x5B` queries for `FC–FF/12C/08` return HLE mirror words (H11, all 0 pre-main-installer) instead of payload addrs; no in-window querer (loop itself is the only querer, HLE-collapsed) |
| C4 | Stub copy `0x82000` (step 4) | Region stays zero | DIVERGENT — consequence: none in-window (sole invoker is the payload ISR via EPC; absent with it; no static `0x82000` ref in OUT outside the stubbed region) |
| C5 | `FlushCache(0),(2)` (step 5) | None (HLE FlushCache = `KE_OK` no-op anyway) | EQUIVALENT — proof: no-ops both (`Thread.cpp:153–156`) |
| C6 | `SetSyscall(0x5B→0x80076000)` (step 6) | Slot untouched by init | DIVERGENT — consequence: none in-window (transient: main installer overwrites `0x5B→0x80075000` on both sides before any other `0x5B` use) |
| C7a | Loop installs `FC/FE→set-body`, `FD/FF→cancel-body` (step 7) | `FC→HLE-Set`, `FE→HLE-Cancel`, `+FD/+FF→drop` (H3–H5) | DIVERGENT — consequence: **FE/FD swapped vs guest** (guest FE=set, FD=cancel; HLE FE=cancel, +FD=drop); latent in-window (zero issuers both sides, AC1-5) |
| C7b | Loop installs `08→exit-body` (step 7) | `+8/−8→unknown-syscall` drop (H5) | DIVERGENT — consequence: latent on runtime (sole issuer is the `0x82000` stub, absent); R1A issues 379×`(−8)` via stub, all served by HW path |
| C8 | `SetSyscall(0x12C→ISR)` = INT12 handler + unmask (AC1-2) | Absent: no cause-12 handler, INT12 never unmasked by init, T3 `CUE=0` (reset-zero) | DIVERGENT — consequence: none in-window (no cause-12 Add/Enable either side; T3 never fires; alarms served by scheduler events instead — AC1-5 T4) |
| C9 | Set service: T3-COMP + ISR + ERET/stub/`(−8)`; tick = T3 CLKS=3; cb `a0=bitidx,a1=id\|time,a2=arg` | Scheduler event + `GuestInvocation`; tick 64 µs; cb `a0=id,a1=ticks,a2=arg` (H3,H6) | EQUIVALENT for `a2`-only handlers — proof: `0x3e3588` uses only `a2` (sema id) and fires `iSignalSema` on both sides (K1 20×`(43)`; R1A path same code); rate: HLE 64 µs vs fork-model T3/15734 Hz = 63.56 µs (0.7%) |
| C10 | Cancel service incl. `-1`-if-`INTC_STAT.12`-pending race (FD/FF body) | `cancelAlarm` erase + deadline scrub; unknown id → `KE_ERROR` (H4) | DIVERGENT — consequence: latent (zero cancel issuers both sides); race semantic has no HLE counterpart |
| C11 | Callback context: ERET into `0x82000`, `sp=0x81FC0`, `Status` manip, `EI`, `ra→ISR` | `GuestInvocation` on reserved stack, `ra=0`, no COP0 touch (H6) | DIVERGENT — consequence: none observed in-window (callbacks used: `iSignalSema`-only + register-indirect; no callback reads COP0/sp/ra — bounded by `0x3e3588` body; #2-handler body OPEN G4) |
| C12 | `InitThread`: sema + thread(`0x424AA0`) + start + prio(self,1), returns tid/`−1` (AC1-2) | Returns `1`, no thread/sema/prio (H2) | DIVERGENT — consequence: early topology differs (R1A g25–29 present, K1 absent); both reach multi-threaded steady state (K1 park: 6 threads); scheduling delta across phases unmeasurable from committed traces |
| C13 | INTC triple 7/7/5, causes `a,3,2,5,7,3,2` (AC1-5) | 6/6/5, same wrapper-pc order minus late cause-3 re-add | EQUIVALENT for the 6 shared — proof: identical `(10)/(14)/(15)` wrapper-pc order (`88,98,98,88,88,88`); K1 causes untraced → positional inference only (OPEN G5 for arg-level proof) |

## AC1-5. Task 2 — consumers + missing-`0x12C` downstream effect

### T1. `SetAlarm` (`0x423B20`, v1=`0xFC`) callers — exhaustive (4 direct `jal`; `0x423B20u` materialization search adds only the neighbor fallthrough `sub_00423B10:49`; computed-`jalr` bound noted in G6)

| Caller | Site | Args at call (OUT) | Handler body | K1 (21 `(fc)`) | R1A (379 `(fc)`) |
|---|---|---|---|---|---|
| #1 `3E35B0` | `0x3e35ec` | `ticks=a0&0xffff`, `h=0x3e3588`, `arg=sema(CreateSema)`; then `WaitSema` | `0x3e3588` (10 insns): `iSignalSema(a2); sync; EI; ret` | 20× — proof: 20× `CreateSema→(fc)→WaitSema→(43)→DeleteSema` cycles (K lines 92–187); `first_ra=0x3e35f4` | 0× — proof: all 379 `(8)` have `a0∈{0x8001a550,58}` (KSEG0 ptr), handler #1 exits with small sema id |
| #2 `3E52B0` | `0x3e5304` | `ticks=mult/div-derived&0xffff`, `h=s1` (register-indirect), `arg=GetThreadId()` | unknown (11 static callers pass `s1`; G4) | 1× — proof: line 626 `GetThreadId→(fc)→SleepThread` = #2 fingerprint (`0x3e52f4` internal GetThreadId); `last_ra=0x3e530c` | 379× — proof: by exclusion (#1 `#4` via `(8)`-a0, #3 via fixed `a0=8` absent); ticks `{0x106×338, 0x1e0×40, 0xa41×1}` |
| #3 `3F4528` | `0x3f4a14` | `ticks=8`, `h=0x3f4448` (reads `a0` vs `[s0+…]`, calls `iWakeupThread@0x424C50`-stub) | `0x3f4448` (`a0`-sensitive) | 0× — proof: all 21 `(fc)` attributed (#1×20 + #2×1) | 0× — proof: zero `(fc)` with `a0=8` |
| #4 `40A328` | `0x40a344` | `ticks=a0&0xffff`, `h=0x40a320`, `arg=[0x4533C8]` (ELF init `−1`) | `0x40a320` (no CSV/OUT entry): `j iSignalSema(a0=a2)` trampoline | 0× — proof: `hasFunction` gate would emit `sched/setAlarm KE_ERROR`; boot log has 0 drops (unmuted receipt, K1-8) | 0× — proof: same `(8)`-a0 excluder as #1 (arg is a sema id, init `−1`) |

Firing: R1A 379 `(fc)` → 379 `(8)` (every alarm fires exactly once;
`(fc)` span ts 11.0458–16.6915; `(8)` `pc=0x82014` = stub `syscall+4`;
`(8)`-a0 flips `…550→…558` at ts 12.2947). K1: 20/21 fired-observed
(`(43)` after each of the 20 #1-cycles); 21st (#2) callback
unattributed in the steady-state `(43)` storm → OPEN G3.
Zero issuers both sides: `(fd)/(fe)/(ff)/(12c)/(18)/(19)/(1e)/(1f)/(6c)/(6d)`
(R1A full-epoch census; K1 full-file census; K1 `(2c)`=0 closes the
`0x12C`-prints-as-`(2c)` conflation, H13).

### T2. Timer-3 state readers — bounded negative

109 OUT files materialize `lui 0x1000/0xb000`; ∩ with `0x1800/0x1810/0x1820`
operands = **0 files**. No recompiled game code forms a T3 address
(method bound: immediate-operand match; stubbed `InitAlarm` + runtime
payload excluded by construction; G6). Cause-12 INTC: zero
`Add/Enable(12)` both sides. Sole T3 observers in-window are the alarm
mechanisms themselves (T1).

### T3. INTC order (game epoch; K1 `pc=0x…`, R1A `pc=…` + `a0=cause`)

R1A (19 lines): `(10)a,(14)a` @11.0388–89 → `(15,10,14)3` @11.6623 →
`(15,10,14)2` @11.6680 → `(15,10,14)5` @11.6714 → `(15,10,14)7` @11.6714 →
**`(10,14)3` (no Disable) @12.2953** → `(15,10,14)2` @13.7834.
K1 (17 lines, K77–78,222–224,275–277,293–298,5807–09): same wrapper-pc
sequence `(10)@88,98,98,88,88,88` + `(14)/(15)` twins; lacks only the
`@12.2953` cause-3 re-add (0.6 s after an alarm callback — game-phase
event past K1's park). No cause-12 anywhere.

### T4. Missing-`0x12C` downstream-effect table

| Consumer of timer-3 state | Observes (guest block present, R1A) | Observes (HLE replacement, K1) | In-window difference |
|---|---|---|---|
| SetAlarm callers (T1) | id allocated (bitmap ≤64); `-1` iff full | id allocated (map); `KE_ERROR`(=-1) iff no-`hasFunction`/exhausted | None observed (all served; K1 0 drops; R1A drop channel n/a) |
| Alarm callbacks (#1-handler) | fire once, `a2`=sema, ERET ctx | fire once, `a2`=sema, `GuestInvocation` ctx | None observed (`(43)` each; C9/C11) |
| Alarm callbacks (#2-handler) | fire once, `a0∈{0x8001a550,58}` (379/379) | set once, fire unattributed (G3) | Unresolvable statically (phase + trace-arg gaps) |
| Cancel callers | none in-window | none in-window | None (C10 latent) |
| `(8)/(−8)` issuers | 379× stub-`(−8)` → HW exit path | none (stub absent; `+8/−8` would drop) | Mechanism-only (C7b latent) |
| T3 register readers | none static (T2) | none static (T2) | None |
| INT12/cause-12 registrants | none (trick path needs no `(10)`) | none | None (C8 latent) |
| `GetEntryAddress` queriers of `FC–FF/12C/08` | payload addrs (post-install) | HLE mirror words (0 pre-main-installer) | None (sole querer is the collapsed loop, C3) |

## AC1-6. INTC/timer comparison (semantic framing, not counts)

| Axis | Reference (R1A game epoch) | Runtime (K1 boot-1) | Reading |
|---|---|---|---|
| Alarm install | 8/6/2 block + `SetSyscall(0x12C→ISR)` + INT12 unmask (guest) | HLE no-op init; scheduler + timer emu stand by | Mechanism replaced; service preserved for `FC` (C9) |
| Alarm use | 379 set → 379 fired (`(8)` receipts), ticks `{0x106,0x1e0,0xa41}`, span 11.04–16.69 s | 21 set → ≥20 fired (`(43)` receipts), boot window 0.03–1.38 s | Both live; client mix differs by phase (T1) |
| Tick quantum | T3 CLKS=3 (fork model 15734 Hz = 63.56 µs; PCSX2-wall pairing confounded — G2) | scheduler 64 µs (15625 Hz); timer emu 15734 Hz | HLE-internal 0.7% (C9); HW-rate absolute OPEN (G2) |
| Cancel path | never issued | never issued | Latent both (C7a/C10) |
| INTC triple | 7/7/5, causes `a,3,2,5,7,3,2`, no 12 | 6/6/5, same order minus phase-late cause-3 re-add | Same driver sequence (C13/T3) |
| Timer-3 IRQ | INT12 armed via `0x12C` trick; 379 ISR runs implied by 379 `(8)` | T3 `CUE=0`; zero timer IRQs; zero cause-12 handlers | IRQ path idle both as observed (no `(10)/(14)`-12); fires delivered as events on K1 |
| `SetCPUTimer*` | 0 | 0 | Absent both (K1-10 row reconfirmed) |

## AC1-7. Exact commands (all read-only; SSD steps with `export COPYFILE_DISABLE=1`)

```text
# guest decode (ELF reads via /tmp/ac1_dis.py; committed copy local/research/AC1/ac1_dis.py)
python3 /tmp/ac1_dis.py dis 0x42c7c8 54                 # InitAlarm 54 insns (AC1-1)
python3 /tmp/ac1_dis.py dis 0x424b78 54                 # InitThread 54 insns (AC1-2)
python3 /tmp/a0_elf.py words 0x456180 12; ... 0x4561b0 4; ... 0x456128 12; ... 0x456158 10; ... 0x455a18 16
python3 /tmp/ac1_dis.py dis 0x455a18 464 > /tmp/ac1_payload_full.txt  # whole payload, gap-tolerant
grep -n "syscall" /tmp/ac1_payload_full.txt             # 0 hits (payload issues no syscalls)
grep -n "jal" /tmp/ac1_payload_full.txt                 # 9 internal jals
python3 /tmp/ac1_dis.py dis 0x4560d8 16; ... 0x40a318 8  # handler-8; 0x40a320 trampoline
# HLE sources (fork reads): Sync.cpp:399, Thread.cpp:184, Dispatcher.cpp:160-177+414,
# EeScheduler.cpp:55,1694-1740,1824-1990,2454-2460,2639-2660, ps2_memory.cpp:169-194+428-555,
# TraceChannel.cpp:126-155, ps2_runtime.cpp:3032-3060, games/ssx3/ssx3.toml:26+141+196
# OUT reads: sub_0042C760/770/780/7B8/7C8, sub_00424B78, sub_0042C300, sub_00423B20,
#   4 caller files + 2 handler files; grep -rln "func_423B20"/"func_3E52B0"/"0x423B20u" OUT
# R1A game epoch (E=/Volumes/Extreme SSD/ps2x-t4/emulog-r1a.txt):
awk 'NR>=872992' "$E" | grep -E ' \((10|14|15|fc|fd|fe|ff|12c|18|19|1e|1f|8|2c|6c|6d)\) pc=' | ... # census (AC1-5)
awk 'NR>=872992' "$E" | grep -E ' \((10|14|15)\) pc='   # 19 INTC lines in order (T3)
awk 'NR>=872992' "$E" | grep -cE ' \(fc\) pc=' / ' \(8\) pc='  # 379 / 379
# K1 (K=$W/P1/run/syscalls-k1-on.txt, B=$W/P1/run/boot-k1-1.log):
grep -nE ' \((10|14|15|fc)\) pc=' "$K"                  # 17 + 21 lines in order
grep -c "\[drop\]" "$B"; grep -cE "unknown-syscall|..." "$B"  # 0 / 0
python3 -c "hot_pc query park-k1-1/park-snapshot.json"  # 0x423b20 ×21, first/last ra
# Play!: web fetch raw PS2OS.cpp@83700b2c → grep 0x12C (:2933), TIMER3 lines
```

## AC1-8. Gaps + OPEN rows (each with the exact closing probe)

| # | Gap | Detail | Exact probe (needs a run or remote read — tabled, not run) |
|---|---|---|---|
| G1 | K1-side cause values (6/6/5) | K1 trace has no `a0`; C13 positional only | Patch `traceChannelEmit` to append `a0=0x%x` (1-line `TraceChannel.cpp`), rebuild `ps2EntryRunner`, 240 s boot; or mine `PS2X_DIAG_PERIOD_MS` diag (pc-only, insufficient alone) |
| G2 | Absolute T3 CLKS=3 rate on PCSX2 | Fork model 15734 Hz; R1A `(fc)→(8)` wall pairing suggests ~2× but turbo confounds wall ts | Read-only: `grep -rn "CLKS\|15734\|HBLANK" <pcsx2-src>/pcsx2/.../Timer.cpp` on bytesize (R1 recipe `ssh bytesize 'wsl grep …'`); no boot needed |
| G3 | K1 21st alarm (#2) fired? | Set observed (K626); callback lost in `(43)` storm | Boot with `[k1]`-style scheduler alarm-fire counter (`EeEventType::Alarm` dequeue log with id/handler), 60 s; correlate id↔line 626 |
| G4 | Caller #2's `s1` handler body | 11 static callers of `3E52B0`; R1A exit-`a0∈{0x8001a550,58}` | Read-only: `a1` at each of the 11 `func_3E52B0` call sites (OUT greps, same method as T1); then handler-body read |
| G5 | C13 arg-level proof | Same as G1 (K1 INTC causes) | Same probe as G1 |
| G6 | Method bounds (negatives) | T2/T1-exhaustiveness assume immediate operands + direct `jal` | Read-only: ELF sweep for `lui 0x1000/0xb000` + reaching-defs to `0x18xx` (def-use, not textual); OUT sweep for computed `jalr` targets (range analysis) |
| G7 | FE/FD-swap + cancel race (C7a/C10) | Zero issuers both sides; HLE/guest disagree | If `(fe)/(fd)/(ff)` ever observed: re-open as defect brief with the issuing trace |

## Evidence files

`REPORT.md` (this file), `ac1_dis.py` (gap-tolerant ELF
word/disassembly miner — `/tmp/ac1_dis.py` copy; A0 `a0_elf.py`
mapping + per-word `.word` fallback for R5900 `MULT` with `rd>3`).
Canonical SSD artifacts referenced by path (not duplicated):
`P1/run/syscalls-k1-on.txt` (783,250 ev), `P1/run/boot-k1-1.log`
(528,891 lines), `P1/run/park-k1-1/park-snapshot.json` (hot-pc 1188),
`ps2x-t4/emulog-r1a.txt` (991,575,587 B), `$W/P1/ssx3-functions.csv`,
`OUT/*` (9278 files), fork sources at branch `ssx3`.

## Tail receipt

Report written in 4 chunks (`write_file` + 3 `edit_file` appends) +
2 fix edits; tail verified intact:

```text
$ tail -3 local/research/AC1/REPORT.md
trailer `Orchestrated-By: Muse Code`, no push (orchestrator pushes at poll).
End of AC1 report.
```

Commit: `git add -f local/research/AC1/…` (2 files), message `[AC1] …`,
trailer `Orchestrated-By: Muse Code`, no push (orchestrator pushes at poll).
End of AC1 report.
