# P1z REPORT — P1v's provisional rule settled from the EE kernel disassembly

Brief `local/muse/prompts/P1z.md`. Standalone (no `P1/REPORT.md` append).
Tables; the verdict is itself a table (§5). No fork edits — the amendment
is spelled out for a later brief.

Inputs re-read first: `local/research/P1/REPORT.md` Part 23 §P23-1a/b
(P1v: written sources silent/LLE, host rule uncited, game-as-oracle
decisive → exact-zero treated as binary sema, recorded PROVISIONAL) and
`docs/research/review-2026-09-19-progress.md` §4.4/§7.5 (game-expects-X
rule: hardware semantics first, kernel disassembly over emulator
sources, TOML quirks only for what cannot be settled).

## P1z-0. Ground facts

| Item | Value |
|---|---|
| In-repo BIOS | `local/emulator/course-cleanup/profile/PCSX2/bios/ps2-bios-0200a-20040614-100909.bin`, 4194304 B |
| sha256 before | `6d23d001daf2a0fa8b381a5d49f51753c36e3622d0f04be46af1a0c548be4744` |
| sha256 after (pristine check §P1z-6) | identical |
| Work copy | `/Volumes/Extreme SSD/ps2x-p1z/ps2-bios-0200a-20040614-100909.bin` (same sha; all sidecars on SSD) |
| ROMVER @ file `0x35ac` | `0200AC200406…` (matches filename) |
| Lease / adb / boots / fork writes | none / none / none / none (READ ONLY per brief) |
| Downloads | none |

### Installed-disassembler inventory (table, per brief)

| Tool | Present | Used |
|---|---|---|
| Ghidra / `ghidraRun` | absent | — |
| radare2 / r2 / rabin2 | absent | — |
| `llvm-objdump` (brew llvm 23.1.1, `mipsel` target registered) | present | no (Capstone sufficed) |
| `llvm-mc`, `llvm-dis`, `mips*-objdump` | absent | — |
| Apple `objdump`/`otool` (no MIPS) | present | no |
| Python3 + Capstone 5.0.7 (`CS_ARCH_MIPS`) | present | YES — all decode |
| `xxd` / `strings` / `sha256sum` | present | YES — recon/hashing |

R5900 gaps hand-decoded: `lq`/`sq` (op `0x1E`/`0x1F`), `daddu`
(func `0x2D`, used as `move`). MMI context-save words (`0x7000xx28`)
left undecoded — outside every path below.

## P1z-1. Locate (`CreateSema` at `0x800049b8`)

| Step | Finding |
|---|---|
| Reset vector | file `0x0` = `0xBFC00000`, MIPS (`mfc0 k0,r15` chip check → `0xBFC00800` / `0xBFC02000`) |
| ROMDIR | table at file `0x2740` (names every `0x10`: RESET, ROMDIR, EXTINFO, ROMVER, …) |
| File layout rule | cumulative `(size+0xF)&~0xF` — read out of RESET's own finder (`0xBFC02640`: `(size+0xF)&~0xF` accumulate; self-check `RESET_rounded == ROMDIR_off` holds: `0x2740`) |
| Layout anchor | recomputed SYSMEM starts with `7fELF`; IOPBTCON2 starts cleanly with `@800` |
| KERNEL file | file `0x39d410`–`0x3b4238` (`0x16e28` B); rodata (`# Syscall: undefined (%d)`, `# <Thread> No active threads`, `rom0:OSDSYS`, …) at KERNEL+`0x1544c`+ |
| Load base | **`0x80000000`** — 8 `lui r,0x8001` + `addiu r,r,lo16` xrefs to 4 distinct rodata strings all solve to `addr − fileoff = 0x80000000` (e.g. `0x80001568/6c` → `0x80015489` = KERNEL+`0x15489`) |
| Syscall dispatcher | `0x80000280`: `bltzl v1` (interrupt path negates) → `sll v1,v1,2` (`0x800002ec`) → `lui k0,0x8001` → `lw k0,0x4f40(k0)` (`0x800002f8`) → `jalr k0`. **Table = `0x80014f40` + `num*4`.** Special-case: `v1==0x7c` → `j 0x800141fc` |
| Table[0x40] | file `0x3b2450` = **`0x800049b8` = `CreateSema`** |

### Table cross-checks (slot → target; all vaddr)

| Slot | Target | Role (worker/wrapper agree) |
|---|---|---|
| `0x00`, `0x3F`, `0x7C` (+10 more) | `0x80001564` | undef-handler (`# Syscall: undefined (%d)`, prints `v1>>2`); 13 undef slots in `[0,0x7D)` |
| `0x40` | `0x800049b8` | **CreateSema** (direct, no wrapper) |
| `0x41` / `0x42` / `0x44` | `0x80003540` / `0x800034c0` / `0x80003440` | Delete / Signal / Wait wrappers → workers `0x80004a40` / `0x80004bc0` / `0x80004cf0` |
| `0x43` / `0x45` / `0x46` | `0x80004bc0` / `0x80004dc0` / `0x80004dc0` | iSignal / Poll / iPoll workers (direct) |
| `0x47` / `0x48` | `0x80004df8` | ReferSemaStatus / iRefer (direct) |
| `0x49` | `0x80004a40` | iDelete (direct) |

Game-thunk numbers (P1 report: `0x40` create, `0x42` signal, `0x44`
wait), fork `Dispatcher.cpp:250-285` (`0x40`–`0x48`, `-0x49/-0x43/-0x46/-0x48`),
and worker semantics (§P1z-3) all agree with this map. (Side note: the
positive namespace has no `+0x43` API; that slot is the iSignal worker.)

## P1z-2. Disassembly — create path (`0x800049b8`–`0x80004a38`)

Conventions: `a3` = user `ee_sema_t *` (`{count@0, max@4, init@8,
…}`, confirmed by P22's `[+4]=max,[+8]=init` writes); node = 32 B slot
in pool `0x8001F240` (`0x80020000−0xDC0`); freelist head
`[0x8001A63C]`; id counter `[0x8001A638]`. `daddu rd,rs,zero` =
`move`.

| Address | Word | Instruction | Annotation |
|---|---|---|---|
| `0x800049b8` | `0280063c` | `lui a2,0x8002` | — |
| `0x800049bc` | `3ca6c68c` | `lw a2,-0x59c4(a2)` | `a2` = freelist head |
| `0x800049c0` | `0400c010` | `beqz a2,0x800049d4` | no free slot → FAIL |
| `0x800049c4` | `2d388000` | `daddu a3,a0,zero` | (delay, always) save user ptr |
| `0x800049c8` | `0800e88c` | `lw t0,8(a3)` | `t0` = `init_count` |
| `0x800049cc` | `03000105` | `bgez t0,0x800049dc` | **`init<0` → FAIL; THE ONLY param check** |
| `0x800049d0` | `1800c424` | `addiu a0,a2,0x18` | (delay) `a0` = `node+0x18` |
| `0x800049d4` | `0800e003` | `jr ra` | FAIL return |
| `0x800049d8` | `ffff0224` | `addiu v0,zero,-1` | (delay) `v0 = -1` (`KE_ERROR`) |
| `0x800049dc` | `0280033c` | `lui v1,0x8002` | — |
| `0x800049e0` | `38a6638c` | `lw v1,-0x59c8(v1)` | `v1` = id counter |
| `0x800049e4` | `040084ac` | `sw a0,4(a0)` | wait-list init: `[node+0x1c]=node+0x18` |
| `0x800049e8` | `0280023c` | `lui v0,0x8002` | — |
| `0x800049ec` | `40f24224` | `addiu v0,v0,-0xdc0` | `v0` = pool base `0x8001F240` |
| `0x800049f0` | `01006324` | `addiu v1,v1,1` | counter+1 (stored next) |
| `0x800049f4` | `0000c58c` | `lw a1,(a2)` | `a1` = next free node |
| `0x800049f8` | `0280013c` | `lui at,0x8002` | — |
| `0x800049fc` | `38a623ac` | `sw v1,-0x59c8(at)` | counter += 1 |
| `0x80004a00` | `2310c200` | `subu v0,a2,v0` | `node − poolbase` |
| `0x80004a04` | `0400c8ac` | `sw t0,4(a2)` | **`node.count = init`** |
| `0x80004a08` | `43110200` | `sra v0,v0,5` | **id = slot index** (`/32`) |
| `0x80004a0c` | `1800c4ac` | `sw a0,0x18(a2)` | wait-list head = `node+0x18` |
| `0x80004a10` | `0400e38c` | `lw v1,4(a3)` | `v1` = user `max_count` |
| `0x80004a14` | `0280013c` | `lui at,0x8002` | — |
| `0x80004a18` | `3ca625ac` | `sw a1,-0x59c4(at)` | freelist unlink |
| `0x80004a1c` | `0800c3ac` | `sw v1,8(a2)` | **`node.max = max` — stored AS-IS, no clamp, no check** |
| `0x80004a20` | `0000c0ac` | `sw zero,(a2)` | `node+0 = 0` |
| `0x80004a24` | `1000e38c` | `lw v1,0x10(a3)` | user+`0x10` → … |
| `0x80004a28` | `0c00c3ac` | `sw v1,0xc(a2)` | …`node+0xc` (attr/option area, out of scope) |
| `0x80004a2c` | `1400e48c` | `lw a0,0x14(a3)` | user+`0x14` → … |
| `0x80004a30` | `1400c0ac` | `sw zero,0x14(a2)` | `node.numWait = 0` |
| `0x80004a34` | `0800e003` | `jr ra` | return id |
| `0x80004a38` | `1000c4ac` | `sw a0,0x10(a2)` | (delay) user+`0x14` → `node+0x10` |

The stretch `0x800049dc`–`0x80004a38` is branch-free: the two
branches above (freelist-empty, `init<0`) are the complete `-1` set.
**No `max` validation of any kind exists** (`max<=0` reject, `max==0`
special-case, `init<=max` — all absent).

## P1z-3. Signal / wait semantics (needed for Q2's implication)

Node layout used below: `+0: link, +4: count, +8: max, +0x14:
numWait, +0x18: wait-queue` (from create stores + pool-init loop at
`0x80004e60`, where free slots carry `count=-1`).

### SignalSema worker `0x80004bc0` (reached via wrapper `0x800034c0` and directly as iSignal `-0x43`)

| Address | Instruction | Annotation |
|---|---|---|
| `0x80004bd4` | `sltiu v0,s3,0x100` | id `< 256` else `-1` |
| `0x80004be8`–`f4` | `sll v1,s3,5`; `s0 = 0x8001F240+v1` | node = pool + `id*32` |
| `0x80004bf8` | `lw v1,4(s0)` | `count` |
| `0x80004bfc` | `bgezl v1,ok (v0=[s0+0x14])` | `count<0` (free slot) → `-1`; else `v0` = numWait |
| `0x80004c0c` | `blez v0,no_waiters (v1=count+1)` | waiter? (delay always pre-increments) |
| waiter path | `jal 0x80005af8` … wake one, `v0=id` | handoff; **count untouched, max unread** |
| `0x80004cc8` | `v0=id; [s0+4]=v1` | no-waiter: **unconditional `count++`** |

### WaitSema worker `0x80004cf0` / PollSema `0x80004dc0` (essence)

| Worker | Rule (count-only) |
|---|---|
| Wait `0x80004cf0` | `count>0` → consume (`count--`, return id); `count<=0` → `numWait++`, enqueue on `node+0x18`, return `-2` (wrapper parks the thread) |
| Poll `0x80004dc0` | `count>0` → consume, return id; `count<=0` → return `-1` |

### Audit: every `node+8` (max) access in sema code

| Address | Access | Meaning |
|---|---|---|
| `0x80004a1c` (create) | `sw v1,8(a2)` | the single store (Q2) |
| `0x80004e2c` (ReferSemaStatus) | `lw v1,8(a2)` → copied to out-param | report-only |
| signal / wait / poll / delete workers | **zero reads** | max is never enforced; `KE_SEMA_OVF` is unreachable on the EE signal path |

(`0x800049c8` `lw t0,8(a3)` reads the *user param*, not the node.)

## P1z-4. Answer

| # | Question | Answer | Evidence |
|---|---|---|---|
| 1 | `max_count=0` accepted? | **YES.** In fact *no* max value is rejected: negative max and `init>max` also succeed (no checks exist) | §P1z-2 branch census: only `-1` paths are freelist-empty and `init<0` |
| 2 | Stored-max semantics? | **Stored as-is (`0` stays `0`)**; max is write-only (besides status reporting) and never enforced — EE semaphores behave unbounded regardless of stored max | `sw` at `0x80004a1c` with no clamp; §P1z-3 audit; signal has no OVF branch |

## P1z-5. Verdict table (P1v's clamp-1 rule)

**Verdict: AMENDED** (no TOML quirk — the hardware rule is fully determined, so §7.5's quirk fallback does not trigger).

| P1v claim | Kernel truth | Standing |
|---|---|---|
| exact-zero create succeeds | succeeds (freelist + `init>=0` only) | CONFIRMED |
| stored max is 1 (binary sema) | stored max is 0, as-is | **AMENDED → store as-is** |
| second waiter-less signal overflows (`KE_SEMA_OVF`, lost) | signals never overflow: waiter handoff, else unconditional `count++` | **AMENDED → drop the OVF check** |
| wait blocks at count 0, waiter-first wake | identical | CONFIRMED (fork already matches) |

Why not CONFIRMED: clamp-1 + the fork's OVF check diverges from
hardware exactly in P1v's own race window (two waiter-less F7 signals
before an F6 wait: hardware holds count 2 and both waits succeed; the
fork loses the second signal at count 1 and the second wait blocks).
P1v's Alt-A rejection attributed this hazard to the wrong alternative —
it is the clamp (with the OVF check retained), not stored-0, that loses
signals, because the kernel has no OVF check at all.

### Exact amendment (for the later brief; no edit made here)

| # | Location (fork `ssx3` branch) | Change |
|---|---|---|
| A1 | `ps2xRuntime/src/lib/Kernel/EeScheduler.cpp:1143` `createSemaphore` | Delete the `effectiveMax` clamp and its comment; reject **only** `initCount < 0` (+ existing id-exhaustion); store `maxCount` as-is (`semaphore.maxCount = maxCount`). Negative max and `init>max` become accepted, matching the kernel (no checks, §P1z-2). Update the `dropArgs` format (`effmax` field goes away). |
| A2 | same file `signalSemaphore`, `count == maxCount → KE_SEMA_OVF` block (`:1259-1273`) | Delete the OVF block (incl. its diag/`emitDrop`); waiter-less signals always `++count` and return id, matching `0x80004bc0`. Keep the waiters-first branch as-is. (`KE_SEMA_OVF` at `:45` becomes unused on this path — keep or remove at the brief's discretion.) |
| A3 | `ps2xTest/.../ps2_runtime_kernel_tests.cpp` P1v test | Zero-max create asserts `maxCount==0` (not 1); add: two waiter-less signals then two waits all succeed with `count` reaching 2 (no OVF). |
| — | wait / poll / `ReferSemaStatus` | No change: already count-only / report-max, matching the kernel. |

## P1z-6. Receipts

Exact commands (all read-only; `$B`= SSD BIOS copy, `$R`= ssx3 root):

| # | Command |
|---|---|
| 1 | `sha256sum $R/local/emulator/course-cleanup/profile/PCSX2/bios/ps2-bios-0200a-20040614-100909.bin` → `6d23d001…4744` |
| 2 | `mkdir -p "/Volumes/Extreme SSD/ps2x-p1z" && cp -n <in-repo> <SSD>` + re-`sha256sum` → identical |
| 3 | tool probe loop (`command -v` × 16) + `brew llvm llvm-objdump --version` + `python3 -c "import capstone"` → §P1z-0 table |
| 4 | `strings -t x $B > /Volumes/Extreme\ SSD/ps2x-p1z/strings-x.txt` (34908 lines) |
| 5 | ROMDIR parse + layout scripts (16-byte rounding per RESET finder) → KERNEL @ `0x39d410` |
| 6 | Capstone `CS_ARCH_MIPS/MIPS32/LE` sweeps + `lui 0x8001`/`addiu lo16` xref scan → base `0x80000000`, dispatcher, table, `0x800049b8` |
| 7 | word-pattern audits: `sll v1,v1,2` sites; `j/jal/beq/bne`→`0x80001564`; `lw/sw *,8(*)` in sema ranges; table dump `0x40`–`0x4a` |
| 8 | re-`sha256sum` in-repo BIOS → `6d23d001…4744` (pristine) |

Receipt paths (heavy, on SSD only — NOT committed):

| Path | Content |
|---|---|
| `/Volumes/Extreme SSD/ps2x-p1z/strings-x.txt` | full `strings -t x` |
| `/Volumes/Extreme SSD/ps2x-p1z/reset-dis.txt` | RESET `0xBFC00000` full word-decode (finder `0xBFC02640`) |
| `/Volumes/Extreme SSD/ps2x-p1z/tbin-dis.txt` | TBIN full word-decode (entry nuclei only read) |
| `/Volumes/Extreme SSD/ps2x-p1z/kernel-dispatch.txt` | `0x80000180`–`0x80000400` (vectors + dispatcher) |
| `/Volumes/Extreme SSD/ps2x-p1z/kernel-exc.txt` | `0x80001300`–`0x80001700` (context save/restore, undef handlers) |
| `/Volumes/Extreme SSD/ps2x-p1z/kernel-createsema.txt` | `0x800049b8`–`0x80004c40` (create + delete head) |
| `/Volumes/Extreme SSD/ps2x-p1z/kernel-sema-ops.txt` | `0x80003400`–`0x80003640` (wrappers) |
| `/Volumes/Extreme SSD/ps2x-p1z/kernel-signal-wait.txt` | `0x80004bc0`–`0x80004f00` (signal/wait/poll/refersema/pool-init) |

Changed files (this commit): `local/research/P1z/REPORT.md` only.

## P1z-7. What I could not do

| # | Limit |
|---|---|
| 1 | No Ghidra/radare2 installed (brief forbade downloads); linear Capstone sweep + hand-decoded R5900 ops instead of CFG analysis. MMI context words left as `???` — none sits on the create/signal/wait paths. |
| 2 | Static only (no boots per brief): the `init<0 → -1`, stored-0, and no-OVF claims are disassembly facts, not runtime-observed. A PCSX2 EE-RAM dump could confirm but was out of remit. |
| 3 | `ee_sema_t` words `+0x10/+0x14` → `node+0xc/+0x10` mapping noted but attr/option positions not pinned (out of scope). |
| 4 | Observed but out of scope, no verdict: kernel PollSema returns plain `-1` when count is 0 (`0x80004de4`→`0x80004dcc`); the fork returns `KE_SEMA_ZERO` (`-419`). Separate divergence, untouched by A1–A3. |
| 5 | TBIN-vs-IOPBOOT second-stage selection and KERNEL handoff sketched, not fully traced (out of scope). |
| 6 | Time used ≈1 h of the 4 h box (single session, no subagents). |
