# A0 report — Name the divergence (static, no boot)

Brief `local/muse/prompts/A0.md`. Tables, no verdicts.
`R=/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp` (fork, read-only),
`W=/Volumes/Extreme SSD/ps2recomp-spike`, `OUT=$W/P1/output` (recompiled,
read-only), `RUN=$W/P1/run`, `REF=/Volumes/Extreme SSD/ps2x-t4/emulog-boot3.txt`
(504 MB reference, read-only), ELF `$W/P1/SLUS_207.72` (read-only).
No lease of any kind, no boots, no builds, no fork changes, no `adb`.
ELF md5 `$W/P1` vs ISO stream: `9e64f3df7ed6e898061411ce43fe75eb` both (same bytes).

## A0-0. Rule record

| Item | Value |
|---|---|
| ssx3 HEAD at start | `ed76d01`-era tree (Part 3 read); evidence dir `local/research/A0/` standalone |
| Fork HEAD (read-only, `rev-parse`) | `282ce922470a38a4cd65ddbacc300fdf8d8f34d0` (`Stimulus: env-armed pad-state flip + 326EB0 dormant-arm tripwires (E2a)`, 2026-09-20 12:28:48 -0400); branch `ssx3`; pre-existing `M ps2xRuntime/src/runner/register_functions.cpp` untouched |
| Fork writes | 0 (all fork/OUT/ELF/ISO reads read-only; scratch miners in `/tmp/a0_*.py` only) |
| Lease / boots / builds / `adb` / push | none / 0 / 0 / unused / never run |
| Streams mined (committed/read-only) | `RUN/syscalls-t18-on.txt` (781,372 ev), `RUN/boot-t18-on.log` (518,344 lines), `REF` (899,714 post-`ExecPS2:2` Bios calls), `RUN/park-t18-on/park-snapshot.json` (6 threads, 1,188 hot pcs) |
| Wall | ~2 h box, single session |

## Table (i) — the patch installer + locator

### (i-a) Unconditional path (entry → installer), every PC straight-line

| Step | PC | Function / file line | Action |
|---|---|---|---|
| 1 | `0x100174`/`0x100190` | `sub_00100008` (`sub_00100008_0x100008.cpp:317-337`) | RFU060 (0x3C) + RFU061 (0x3D) = runtime trace events 1–2 |
| 2 | `0x100198` | same file `:352` | `jal func_42C300` (no branch on any return before or after) |
| 3 | `0x42c0f4`/`0x42c104` | `sub_0042C0D8` (`sub_0042C0D8_0x42c0d8.cpp:52-72`) | CreateSema ×2 via `0x423DA0` (v1=0x40) = events 3–4; results → `[0x455248]`/`[0x45524C]` |
| 4 | `0x42c310` | `sub_0042C300` (`sub_0042C300_0x42c300.cpp:47`) | `jal func_42C1F0` = ret0 stub (v0 discarded; next insn unconditionally `jal 42C7C8`) |
| 5 | `0x42c318`/`0x42c320` | same file `:58-69` | `InitAlarm` + `InitThread` host stubs (no syscall events) |
| 6 | `0x42c328` | same file `:80` | `jal func_42C410` (OSD ×4 + skipped patch block; §(i-d)) |
| 7 | `0x42c334` | same file `:86` | `j func_42CBD0` tail-jump into the installer (mid-file label in `sub_0042CBC0_0x42cbc0.cpp`) |
| 8 | `0x1001a0` | `sub_00100008_0x100008.cpp:361` | `jal func_424020` FlushCache(0) after 42C300 returns = event 26 |

No `beq/bne/beqz/bnez` on any path 0x100008→0x100198→42C300→42CBD0 (entry `0x100140 bnez` is a bss-zero loop only).

### (i-b) Installer `0x42CBD0` — 8 SetSyscall + 6 GetEntryAddress + 1 Copy + 2 FlushCache

Wrappers: `0x42CBC0` = SetSyscall (v1=0x74), `0x42CBB0` = GetEntryAddress (v1=0x5B),
`0x42CB68` = Copy (v1=0x5A), `0x424020` = FlushCache (v1=0x64). Table words read
from ELF (`/tmp/a0_elf.py words`, md5-matched binary). s0=`0x456540`, s1=`0x456558`, s2=3→8.

| # | Event (trace order) | PC | a0 (number) | a1 (handler/value) | ELF word source |
|---|---|---|---|---|---|
| 1 | SetSyscall | `0x42cbf8` | `0x5A` (Copy) | `0x42CB78` (guest word-copy loop) | `[0x456540]=0x5A`, `[0x456544]=0x42CB78` |
| 2 | Copy(0x5A) | `0x42cc10` via `0x42CB68` | dst `0x80075000` | src `0x4561C0`, size `0x330` | immediates (`sub_0042CBC0_0x42cbc0.cpp:100-118`); executes GUEST `0x42CB78` via the event-1 override (hasFunction true, no drop) |
| 3–4 | FlushCache ×2 | `0x42cc18` (a0=0), `0x42cc20` (a0=2) | — | — | `sub_0042CBC0_0x42cbc0.cpp:135-150` |
| 5 | SetSyscall | `0x42cc2c` | `0x5B` (GetEntryAddress) | `0x80075000` (copied payload) | `[0x456548]=0x5B`, `[0x45654C]=0x80075000` |
| 6 | SetSyscall | `0x42cc38` | `0x54` (ClearEventFlag) | `0x42D100` (mid-`sub_0042CD98`, no entry) | `[0x456550]=0x54`, `[0x456554]=0x42D100` |
| 7–11 | GetEntryAddress ×5 | `0x42cc48` loop, s2=3..7 | `0x55,0x56,0x57,0x58,0x59` | returns v0=`-1` (each DROPS: override from event 5 routes 0x5B→`0x80075000`, hasFunction false) | `[0x456558+8k]` k=0..4 = `0x55..0x59` |
| 7–11 | SetSyscall ×5 | `0x42cc58` loop | same `0x55..0x59` | `0xFFFFFFFF` (= v0 `KE_ERROR`, `State.h:25`) | a1=v0 passthrough (`daddu $a1,$v0,$zero` @`0x42cc54`) |
| 12 | GetEntryAddress | `0x42cc6c` | `0x3` | returns `-1` (6th drop) | `addiu $a0,$zero,0x3` |
| 13 | — | `0x42cc88` | `[0x456538] = v0` = `-1` | — | epilogue store |

Loop bound: s2 init 3 (`0x42cbe0`), `sltiu $v0,$s2,8` + `bnel` @`0x42cc60/64` → 5 iterations.
Trace join: runtime events 9–25 = rows above in order (8×`RFU116 (74)`, 6×`RFU091 (5b)`,
1×`RFU090 (5a)`, 2×`(64)`); boot log `:70-75` = the 6 `[drop] syscall/dispatchSyscallOverride KE_ERROR syscall=0x5b handler=0x80075000`
lines; full-log `[drop]` census = 6 (no other drops in 240 s).

### (i-c) Effective override table after the installer (8 distinct numbers)

`setEeSyscallOverride` (`ps2_runtime.cpp:2685`): handler==0 erases, else installs +
mirrors to `rdram[0x11F80+idx*4]`; `dispatchSyscallOverride` (`Syscalls/System.cpp:422`,
checked first in `Dispatcher.cpp:108`) drops `KE_ERROR` when `hasFunction(handler)` is false.
HLE names: 0x54 ClearEventFlag, 0x55 RFU085_iClearEventFlag, 0x56 WaitEventFlag,
0x57 PollEventFlag, 0x58 RFU088_iPollEventFlag, 0x59 ReferEventFlagStatus, 0x5A Copy,
0x5B GetEntryAddress (`TraceChannel.cpp:46-58`, PCSX2-verbatim).

| Syscall | Handler | Entry? | Fires in 240 s? | Effect |
|---|---|---|---|---|
| `0x54` | `0x42D100` (mid-`sub_0042CD98` `0x42cd98-0x42d320`, CSV: no `0x42d100` row) | no | never issued (census count 0) | dormant; would drop if issued |
| `0x55..0x59` | `0xFFFFFFFF` | no | never issued (counts 0) | dormant poison; would drop if issued |
| `0x5A` | `0x42CB78` (`sub_0042CB78`, word-copy loop `0x42cb78-0x42cba8`) | yes | 1× (installer event 2) | Copy rerouted to guest loop; chain-to-original broken |
| `0x5B` | `0x80075000` (0x330 B copied from ELF `0x4561C0`; head `3C028007/0000282D/24435300` = kernel-code shape, lui v0+zero_a1) | no | 6×, all drop | GetEntryAddress permanently `-1`; `[0x456538]=-1` |

F3 said "≤7 overridden syscalls": static count is 8 SetSyscall events / 8 distinct
numbers (`0x54-0x5B` contiguous). The 5 loop-installed handlers are `-1` (drop residue),
not game addresses — the only game-address handlers are `0x42CB78`, `0x80075000`, `0x42D100`.

### (i-d) Second patch block `0x42C410` (same shape, SKIPPED in the runtime)

| Item | Value |
|---|---|
| Gate | `jal 42C3A8` @`0x42c420`, `beqz $v0 → 0x42c4a4` @`0x42c428` (taken = skip whole block) |
| 42C3A8 role | issues the OSD Get/Set/Get/Set = events 5–8 (only OSD source on the path); returns 0 in the runtime (block skipped: trace shows 8 not 11 SetSyscalls, 1 not 2 Copies) |
| Skipped payload (static) | `SetSyscall(0x5A→0x42C360)` @`0x42c440` (wrappers `0x42C340`=0x74 / `0x42C350`=0x5A / `0x42C398`=0x5B); `Copy(0x80074000←0x455250,0x7A8)` @`0x42c458`; FlushCache(0,2) @`0x42c460/68`; `SetSyscall(0x5B→0x80074000)` @`0x42c474`; 1 loop iter (s2=2, `s2<3`): `GetEntry([0x455A08]=0xFFFFC402)` + `SetSyscall(same,v0)` @`0x42c480/90` |
| Tables | `[0x4559F8]=0x5A,[0x4559FC]=0x42C360,[0x455A00]=0x5B,[0x455A04]=0x80074000` (ELF reads); payload head `0x455250` = `3C028007…` (same kernel-code shape as `0x4561C0`) |

### (i-e) Other `SetSyscall` (v1=0x74) wrapper sites — liveness

| Site | Wrapper file | Called from | Fires? |
|---|---|---|---|
| `0x42C2F0` | SetSyscall; used twice INSIDE true `0x42C1F0` only (`SetSyscall(0x83→0x42C168)`, `SetSyscall(0x5A→0x42C130)` from `[0x455238..44]`) | `0x42c228`/`0x42c234` (dead: whole function ret0-stubbed) | no |
| `0x42C340` | SetSyscall for the 42C410 block | `0x42c440/74/90` (dead: gate skipped) | no |
| `0x42CBC0` | SetSyscall for the 42CBD0 block | `0x42cbf8/2c/38/58` | yes (8×) |
| `0x424110`, `0x42C500`, `0x42C760` | v1=0x74 wrappers (F3 §24 grep) | no caller found on the boot path (no `func_424110/42C500/42C760` refs in entry/42C300 subtree; 240 s trace shows exactly 8×0x74, all accounted) | no |

### (i-f) Locator `InitSystemCallTableAddress@0x42C1F0` — true body (ELF disasm, MIPS64)

CSV row 9234 (`0x42c1f0-0x42c2f0`, 0x100 B); recompiled output is the ret0 stub
(`InitSystemCallTableAddress_0x42c1f0_0x42c1f0.cpp`, `toml:207`).

| Phase | PCs | Action |
|---|---|---|
| Mark | `0x42c224-38` | `SetSyscall(0x83, 0x42C168)` + `SetSyscall(0x5A, 0x42C130)` via `0x42C2F0` (args from `[0x455238]=0x83,[0x45523C]=0x42C168,[0x455240]=0x5A,[0x455244]=0x42C130`) |
| Scan A | `0x42c23c-4c` | syscall `0x83` (= guest scanner `0x42C168` after marking): find word `0x42C168` in KSEG0 `[0x80000000,0x80080000)` → s3 |
| Scan B | `0x42c250-64` | syscall `0x83`: find word `0x42C130` in same range → s2 |
| Locate | `0x42c260-2c0` | s1=s3-`0x20C` (=match-`0x83*4`), s0=s2-`0x168` (=match-`0x5A*4`); converge loop (`0x42c278-2b0`, advance-past-false-positive rescans @`0x42c284/2a0`) until s1==s0 |
| Publish | `0x42c2bc/2c0` | `[0x455230] = s1` (table base); epilogue restores regs, `jr ra` |

The markers ARE the just-installed table slots: slot `0x83` holds `0x42C168`,
slot `0x5A` holds `0x42C130`, so each match minus its slot offset = table base,
cross-checked. Return register: path 1 (immediate match) returns v0=s2 (slot-`0x5A`
address); path 2 (loop exit) returns v0=0 (delay-slot `sltu` on equality). The
result the game keeps is the global `[0x455230]`, not v0.

| Caller question | Static answer |
|---|---|
| Sole caller | `0x42c310` in `sub_0042C300` (only `func_42C1F0` ref in OUT; `sub_0042C300_0x42c300.cpp:47`) |
| Branch on return/0? | NONE: v0 discarded, straight into `jal 42C7C8`; installer reached by unconditional tail-jump `0x42c334`. `[0x455230]` has no live reader (only mid-function `0x42c1b8`, unreachable: no CSV row, no xrefs) |
| Rung-1 hang mechanism (why ret0 exists) | Unstubbed, scan syscalls dispatch override `0x83→0x42C168`; `0x42C168` is mid-function (inside the `0x42c130-0x42c1a8` copy/scan chunk, no entry) → `hasFunction` false → perpetual `KE_ERROR` → s3/s2 never converge ("polls FindAddress forever", Part 1 §4 ladder row 1) |
| Recognised-vs-0 | On hardware the scan finds both markers (real table) and publishes the base; `0` is returned on the loop-exit path regardless (v0 is not the signal) and on scan failure the loop cannot converge |

Gap G1 (reference paradox, for A1): the reference (`REF`, BIOS USA v02.00) shows
ZERO `(74)/(5b)/(5a)/(64)` over the full boot AND no CreateSema/OSD at entry —
yet the identical ELF (md5 match) reaches the installer unconditionally after
RFU060/061. PCSX2 `SYSCALL()` logs unconditionally before the switch
(`R5900OpcodeImpl.cpp:906-917`, BIOS_LOG, table non-null for `0x54-0x5B/0x64/0x74`),
both `ExecPS2` windows checked (lines 142369/142465; inter-window = 4 Bios-call
lines only), no pnach (T4 G8). No static branch explains the reference's avoidance;
A1's "kernel-true return skips the patches" premise does not follow from the
caller graph (nothing branches). Candidates: reference loader path difference,
HLE SetupThread/SetupHeap side effect, or an unmodelled early state dependency —
each needs a dynamic read, not a config flip.

## Table (ii) — the hash-loop exit predicate + the 20 lookups

### (ii-a) Call chain + per-invocation shape (hot_pc join, 240 s)

`376938 --0x377b14--> 363490 --0x3634cc--> 362DE8 --0x362f68--> 394ED0`.
Single callers throughout (`func_362DE8` only in `sub_00363490`; `func_363490`
only @`sub_00376938:10004`; `func_394ED0` in `sub_00362DE8` + never-fired `sub_0038B0F8`).

| PC | Count | ra | Per-363490 |
|---|---|---|---|
| `0x363490` | 14,349 | `0x377b1c` (sole) | 1 |
| `0x362de8` | 14,349 | `0x3634d4` (sole) | 1 |
| `0x394ed0` | 285,642 | `0x363240` (in-362DE8 return site) | 19.91 (≈20, ramp deficit; long-boot exact 20N−1338, P34) |
| `0x395000` | 271,293 | `0x3632e4` (in-362DE8) | 18.91 (≈19) |
| `0x362cc8` | 14,350 | `0x3629f0` (boot, 1×) → `0x377c08` (steady) | 1.0 (from `0x377c00`, AFTER 363490 returns) |
| `0x423c90` GetThreadId | 290,210 | `0x3e5028`→`0x3e5774` | 20.22 (see iii) |
| `0x424020` FlushCache | 14,356 | `0x42cc20` (boot) → `0x382938` (steady) | 1.0005 (see iii) |

Pacing: 14,349 invocations / 240 s = 59.8/s ≈ 60 Hz VBLANK; N=72,176 over
~1,203 s guest = 60.0/s (F2). Post-363490 in 376938: `WaitSema(*(s3+0x5ACC))`
via `0x423DE0` @`0x377b1c` (`sub_00376938_0x376938.cpp:10030`), `SignalSema`
via `0x423DC0` @`0x377b5c`+`0x377b64`, `362CC8(*(s3+0x18F0))` @`0x377c00`.

### (ii-b) `sub_00394ED0` — 256-bucket hash lookup-or-insert (full decode)

Args: a0=t2=table base (s6 passthrough from 363490's a0 = `*(s3+0x18F0)` heap),
a1=key ptr (s1 record), a2=hash byte. `sub_00394ED0_0x394ed0.cpp` (386 lines).

| Step | PCs | Action |
|---|---|---|
| Bucket | `0x394ed0-e8` | a3=a2&0xFF; t1 = t2+`0x674A0`+a3*4; head=[t1] |
| Empty | `0x394ef0→84` | head==0 → allocate path |
| Walk | `0x394f08-3c` | per node: 4-word key compare `[node+0..12]` vs `[key+0..12]` (`0x394f18-30`, t0=0..3, `bne→0x394f58` mismatch); all-match → v0=1 |
| Hit | `0x394f3c-54` | match + `[t4+t5]==node` → return node (v0=a2); else move-to-front (`0x394f60-74`: unlink, push head, return node) |
| Miss-next | `0x394f78-80` | mismatch: a2=[node+`0x14`]; nonzero → next iteration (t1=&link); zero → allocate path |
| Allocate | `0x394f84-fc` | N=[t2+`0x51480`]; rec=t2+`0x51484`+N*`0x18`; copy 20 B key (ldl/ldr/sdl/sdr ×2 + lw/sw @`0x394fc4-e8`); rec+`0x14`=old head; [bucket]=rec; [count]=N+1; return rec |

Key shape: 16-byte key (4 words) + record stride `0x18` (24 B: 20 B key + next link
at +`0x14`). Bucket table base t2+`0x674A0` (256×4 B). Hit = return + move-to-front;
miss = insert + return new (never fails statically; saturation behaviour needs E3).

### (ii-c) `sub_00362DE8` — per-record hash + checks (20 records/invocation)

Inner loop head `0x362f00` (`sub_00362DE8_0x362de8.cpp:308`); back-edge `0x363160 bnez $s7 → 0x362f00`.

| Step | PCs | Action |
|---|---|---|
| Hash | `0x362f00-64` | v0 = k0^k1^k2^k3 (4 key words @s1+0..12); a2 = avalanche(v0) (sra/sll/addu/xor chain); delay-slot `andi a2,0xFF` into the call |
| Lookup | `0x362f68` | `jal 394ED0` (a0=s6 base, a1=s1 key, a2=hash byte); s3=v0 (node) |
| Halfword checks | `0x362f74-88` | `[s1+0x1E]==0`? nonzero → `0x363014` path (s5=0); zero → `[s1+0x1C]`/`[s1+0x10..12]` halfword compares + `jal 395000` @`0x363008` (19×: skipped on the nonzero path) |
| Advance | `0x363014-160` | s1=next record; `bnel s5` / `bnez s7` control 20-count (s7 = remaining, set in prologue from list header) |

What the 20 lookups look up: 20 hash records (TO-fed per P1af: a2 `0x9d`/`0x26`
post-SPR-fix) walked from the s1 list; per-record 16 B key + flag halfwords at
+`0x10/+0x1C/+0x1E`. Record source list head: prologue (`0x362e2c-64`, s6/a0
passthrough + `jal 424698` + div) — exact head pointer needs E3 register read.

### (ii-d) Exit predicate + flag-deliverer (partially open)

| # | Finding | Evidence |
|---|---|---|
| 1 | No backward branch in `363490`/`376938`/`375A08` encloses the per-VBLANK call (`/tmp/a0_loops.py`: max spans 230/188/66 insns; `0x377b14` unenclosed; `0x3634cc` unenclosed) | OUT disasm comments; loop tables in `loops-375a08-363490-376938.txt` |
| 2 | `376938` entered indirectly (no direct caller: 3 self-`jal` @`0x376b5c/8208/8e4` only; `375A08` does NOT call it — earlier substring match was the range comment) + hot_pc lacks `0x376938` while `0x363490`=14,349 ra-`0x377b1c` | OUT greps; `park-snapshot.json` hot_pc (1,188 rows) |
| 3 | Exit = return, not break-to-elsewhere: last `362DE8` exit → 73-line sibling unwind (`364360/364050/3666F8/38F300`) → `363490` exit → `376938` exit → main dormant (pc 0) | P32-1c unwind table (trace lines 185264990–185265064) |
| 4 | Per-iteration flag writes observed: `363490` zeroes `[sp+0x2C]`/`[sp+0x30]` targets + copies 20 B `0x501420→fp+0x69CA8` @`0x3634d4-534`; `376938` copies 20 B `0x501420→[s3+0xE84]` @`0x377bd0-fc`, then `jal 362CC8/3673D0` | `sub_00363490_0x363490.cpp:112-190`, `sub_00376938_0x376938.cpp:10147-10225` |
| 5 | VBLANK gate per iteration: `WaitSema(*(s3+0x5ACC))` @`0x377b1c` + 2× `SignalSema` @`0x377b5c/64` (thread-1 WAIT-29 samples @`0x423de8` between iterations) | P1:9319; `sub_00376938_0x376938.cpp:10030-10138`; T13 blocks 234–239 |
| 6 | Stop-count N=72,176 exact to the digit across boots; no counter/flag/compare identified statically as the terminator | T15/T16/P33-4b; F2 (VBLANK-counted give-up signature) |

Flag-deliverer column (SIF/RPC? OSD? neither?): the 20 B block at `0x501420`
is the only cross-iteration shared state found in the (ii) functions, but its
writer is unidentified (no writer in 363490/376938/362DE8 bodies; SIF/RPC and OSD
paths neither confirmed nor excluded). Gap G2: name the `0x501420` writer
(E3 register/stall read or T22 `pc=` store attribution) and the indirect caller
of `376938` (function-pointer source); Gap G3: the (i,N) bound read at `0x36356c`
(P1ah receipt) still needs E3 — A1 does not need it, E3-conditional does.

## Table (iii) — storm issuers + override join

### (iii-a) GetThreadId (0x2F): 290,210 vs 2 — single wrapper, 21 call sites

Wrapper `0x423C90` (`sub_00423C90_0x423c90.cpp:28-33`): PLAIN `addiu $v1,$zero,0x2F`
+ `syscall` + `jr ra`. (F3 "no plain site" was a grep miss: file spells `0x2F`
uppercase with multi-space fill; pattern `addiu $v1,$zero,0x2f` single-space
lowercase cannot match.) hot_pc: `{pc 0x423c90, count 290210 (= census exact),
first_ra 0x3e5028, last_ra 0x3e5774}` — count equality proves this is the ONLY
issue site (no indirect/host path).

| # | Call site | Enclosing function | ra match |
|---|---|---|---|
| 1 | `0x31ab4c` | `sub_0031AAF0` | — |
| 2 | `0x31a734` | `sub_0031A6B8` (P1t `-1` spin fn) | — |
| 3 | `0x320b10` | `sub_00320550` | — |
| 4 | `0x3c1fbc` | `sub_003C1B80` | — |
| 5 | `0x3c3390` | `sub_003C3380` | — |
| 6 | `0x3c33e8` | `sub_003C33E0` | — |
| 7 | `0x3e5020` | `sub_003E5018` (SYNCTASK/driver) | first_ra `0x3e5028` ✓ (site+8) |
| 8–9 | `0x3e53f4`, `0x3e5418` | `sub_003E5398` | — |
| 10–11 | `0x3e570c`, `0x3e5738` | `sub_003E5700` | — |
| 12 | `0x3e576c` | `sub_003E5760` | last_ra `0x3e5774` ✓ (site+8) |
| 13–15 | `0x3e52f4`, `0x3e533c`, `0x3e5360` | `sub_003E52B0` | — |
| 16 | `0x3e51bc` | `sub_003E51A0` | — |
| 17–19 | `0x3e544c`, `0x3e54c0`, `0x3e5538` | `sub_003E5440` | — |
| 20 | `0x3f4740` | `sub_003F4528` | — |
| 21 | `0x418cb8` | `sub_00418CA8` | — |

(All `jal func_423C90`, opcode `0xc108f24`.) Per-VBLANK: 290,210/14,349
= 20.22/invocation (boot-phase issues explain the +0.22 over 20; reference
total = 2). Both sampled ras fall in the `0x3E5xxx` SYNCTASK cluster (13 of
21 sites), not in main's `0x36xxxx` loop — the "same 20" is correlation across
one hash iteration's triggered driver work, not issuance from the hash loop.
Per-site split needs T22 `pc=` (Gap G4).

### (iii-b) FlushCache (0x64): 14,356 vs 0 — wrapper + 23 call sites

Wrapper `0x424020` (`sub_00424020_0x424020.cpp:30-33`, v1=0x64); HLE =
`Thread.cpp:153` no-op returning `KE_OK` (a0 ignored → mode gaps moot).
hot_pc: `{pc 0x424020, count 14356 (= census exact), first_ra 0x42cc20,
last_ra 0x382938}` — sole issue site; first = installer `0x42cc18`+8 (boot),
last = `0x382930`+8 (steady state).

| Call site | Enclosing function | Class |
|---|---|---|
| `0x1001a0` | `sub_00100008` (entry, a0=0) | boot (event 26) |
| `0x42cc18` (a0=0), `0x42cc20` (a0=2) | `sub_0042CBC0` (installer) | boot (events 11–12) |
| `0x42c460` (a0=0), `0x42c468` (a0=2) | `sub_0042C410` | dead (gate skipped) |
| `0x382930` | `sub_00382760` (queue/desc writes `0x382908-2c`, thread-5 area; entry `0x382740`) | STEADY (last_ra; 14,353/≈14,400 VBLANKs ≈ 1.0/VBLANK) |
| `0x2ec5f0` (×2 files: `2EC418`+`2EC478` overlap), `0x37c0c8`, `0x3837a8`, `0x391404`, `0x39134c`, `0x3c1b18`, `0x3c4410`, `0x3e4144`, `0x3f4f7c`, `0x3f4fb0`, `0x3f5210`, `0x3f52c4`, `0x3f5528`, `0x3fd0ac`, `0x3fd0b4`, `0x40359c` | 15 more sites | silent in 240 s (else count would exceed boot 3 + VBLANK ~14,353) |

### (iii-c) Override-join: issuers vs table (i-c)

| Issuer | Number | Overridden? | Route |
|---|---|---|---|
| GetThreadId `0x423C90` + 21 sites | `0x2F` | NO (table holds `0x54-0x5B` only) | direct HLE; zero drops reference it |
| FlushCache `0x424020` + 23 sites | `0x64` | NO | direct HLE no-op; zero drops reference it |
| Game wrappers `0x42CB78` (live Copy) | `0x5A` | YES | 1 hit (installer self-copy); never re-issued (census 1) |
| `0x80075000` / `0x42D100` / `0xFFFFFFFF` | `0x5B/0x54/0x55-59` | YES | 6 drops / dormant (never issued) |

No storm issuer routes through a game wrapper. Reference join: 2 vs 0
(`(2f)`=2, `(64)`=0 full-boot).

## Commands + line refs (all read-only)

```text
# fork HEAD (read-only) + OUT inventory
git -C "$R" rev-parse HEAD                                    # 282ce92… (E2a) + M register_functions.cpp
ls $W/P1/output | wc -l                                       # 9278 (9262 sub_*)
# installer + tables (ELF reads via /tmp/a0_elf.py: capstone-mips64 dis + word dump)
grep -rn "func_42C1F0|func_42CBD0" $OUT --include=*.cpp        # sole refs: sub_0042C300:47/:86
python3 /tmp/a0_elf.py words 0x456540 16                      # 0x5A/0x42CB78 0x5B/0x80075000 0x54/0x42D100 0x55..0x59
python3 /tmp/a0_elf.py words 0x4559F8 12                      # 0x5A/0x42C360 0x5B/0x80074000 …
python3 /tmp/a0_elf.py dis 0x42c1f0 62                         # locator mark/scan/locate/publish
python3 /tmp/a0_elf.py dis 0x42c168 24                         # KSEG0 word scanner (match-addr-or-0)
# census joins (single awk pass each; 36 MB / 504 MB inputs)
awk '{print $NF}' $RUN/syscalls-t18-on.txt | sort | uniq -c | sort -rn   # (2f) 290210 (64) 14356 (74) 8 (5b) 6 …
tail -n +142465 $REF | grep -c "Bios call: .* (74|5b|5a|64)"   # 0 each; (2f)=2 full-boot
grep -n "Bios call: ExecPS2" $REF                             # lines 142369 + 142465 (both windows checked)
grep -c/-n "drop" $RUN/boot-t18-on.log                        # 6, lines 70–75, all 0x5b/0x80075000
bsdtar -xOf ISO SLUS_207.72 | md5 ; md5 $W/P1/SLUS_207.72      # 9e64f3df… both
# hash loop + issuers
grep -rn "jal.*func_423C90|func_424020" $OUT --include=*.cpp   # 21 + 23 sites (tables iii-a/b)
python3 /tmp/a0_loops.py $OUT/sub_003*.cpp                    # backward-branch spans → loops-*.txt
python3 json hot_pc query on park-t18-on/park-snapshot.json   # counts+ras in (ii-a)/(iii-a,b)
```

Supporting files: `census-runtime.txt` (awk table), `loops-375a08-363490-376938.txt`
(loop spans), `census-reference-patchpath.txt` (REF counts).

## Gaps (what A1 / E3 need from each table)

| # | Gap | Needed by | Shape of the read |
|---|---|---|---|
| G1 | Reference avoidance mechanism (no static branch skips the unconditional installer) | A1 (blocks its premise) | dynamic: loader/HLE-setup comparison, not config |
| G2 | `0x501420` writer + `376938` indirect caller (function-pointer source) | SIF-peer decision, E3 | E3 stall/register read or T22 `pc=` store attribution |
| G3 | (i,N) bound + guard-word values at `0x36356c` | E3-conditional only | E3 probe (P1ah receipt unchanged) |
| G4 | Per-site GetThreadId split across the 21 sites (both ras sample the SYNCTASK cluster) | nobody blocks; T22 closes it | T22 `pc=` channel (in flight) |
| G5 | s1 record-list head pointer + saturation behaviour of the `394ED0` allocator | E3-conditional | E3 register read at `0x362f00` |
