# E37 report — full entry trace of the stuck VU1 programs (recomp side of a PCSX2 diff)

Brief `local/muse/prompts/E37.md`. Tables + receipts; the orchestrator decides.
Read first: `AGENTS.md`, `local/AGENTS.local.md`, `local/research/E36/REPORT.md`
(all), `local/research/T48/REPORT.md` §T48-5.

## Outcome

- New DEV-ONLY `PS2X_VU1_ENTRY_TRACE` (+`_PCS` byte PCs, +`_VSYNC` gate):
  for the first MSCAL at each listed startPC at/after the gate vsync, one
  block with the 16 KB VU1 data memory at MSCAL entry (`vumem`), every VIF1
  command since the previous MSCAL boundary (`vif`, cap 4096), and every
  executed pair from startPC to the first `0x418` arrival plus 3 loop
  iterations (`pair`, cap 16384). One fork commit; suite **480/480**.
- One Boot-A run (e37a): both blocks captured (`0x10`, `0x40` @ vsync 1300);
  gfx-stats reproduce E33/E36 bit-identically (583 MSCAL, 498 exhausted,
  xgkick=85 every settled vsync), so the armed tracer perturbs nothing.
- Headline finding: **`vi03 is never written`** — not in either setup path
  (129/123 straight-line pairs), not in 3 sampled loop iterations, and per
  E36 not elsewhere in the `0x418–0x548` loop body. It is only *read*
  (`IBEQ` guards at `0x2c8`/`0x408`, `IBNE` exit at `0x548`). Its value is
  inherited persistent VI state: by E36 end-values + the E37 no-write proof,
  entry `vi03 = -15836 (0xC224)` for both programs. `vi11/vi13/vi14` are
  likewise never initialized — only relatively bumped (`LQI` post-inc,
  `IADDIU +3`) from inherited entry values. No fix (brief names none);
  no A/B/C verdict per the brief.

## Commits

Fork `~/dev/PS2Recomp`, branch `ssx3`:

| Commit | Subject |
|---|---|
| `11725b4` | [E37] DEV-ONLY VU1 entry trace (vumem + VIF packet + setup pairs) |

Base was `018f56b` (pushed E36 tip). Runner-dir gate:
`git diff --stat 14b1e5cb ssx3 -- ps2xRuntime/src/runner` is empty.
Suite (flags-unset, fork root): **480/480, rc 0** (476 E36 + 4 new
`Ps2Vu1EntryTrace` cases: off-by-default, PCS parse, freeze/arm-once,
pair-stream stop after head + 3 iterations).

## Trace design (what `PS2X_VU1_ENTRY_TRACE` records)

Header-only `ps2xRuntime/include/ps2_vu1_entry_trace.h` (E36/gfx-stats
pattern). `PS2X_VU1_ENTRY_TRACE=<file>` master gate,
`PS2X_VU1_ENTRY_TRACE_PCS=0x40,0x10` (byte PCs, `0x`-hex or decimal,
max 16), `PS2X_VU1_ENTRY_TRACE_VSYNC=<n>` (default 0). First MSCAL per
listed PC at/after the gate freezes the block; repeats never re-arm.
Windows cut at `EeScheduler` VBlankStart (same tick E36 uses).

- `vumem <row-dec> <w0> <w1> <w2> <w3>`: 1024 lines, `%08x`, snapshotted in
  the VIF1 MSCAL branch before the execute callback runs (synchronous, so
  this is exactly MSCAL-entry memory).
- `vif <name> num=<> addr=<> fmt=<> usn=<> mask=<8hex> cl=<> wl=<> [row=|col=]
  data=<words|-> [+more=<>] [mode=<> men=<>]`: one line per decoded VIF1
  command since the previous MSCAL/F/CNT boundary, inclusive of the
  triggering MSCAL (`addr` = dest VU row for UNPACK with `+TOPS` when the
  imm TOPS-relative bit is set, micro slot for MPG, startPC/8 for MSCAL/F,
  `-` otherwise; `fmt` = `V{vn+1}_{32|16|8}` or `V4_5`, `GIF` for DIRECT,
  `-` otherwise; UNPACK `data` = all source words, DIRECT/MPG = first 8 +
  `+more`; `mode=`/`men=` suffix on UNPACK only; all payload reads clamped
  to the available bytes so truncated packets can't overread).
- `pair pc=0x<> up=<8hex> lo=<8hex> <lower-disasm> | up <NOP|0x...> [| vi<i>:
  <4hex>-><4hex> …] [| vf<n>.<xyzw>:<8hex>-><8hex> …] [| rd <row>:<4 words>]
  [| wr <row>:<4 words>]`: per issued pair; VI compared full-word but
  printed low-16 hex, VF per changed lane by bits; loads decode the row
  from pre-exec state (address math mirrors `execLower`, incl. LQI/LQD and
  ILWR pre/post adjust) and read it; stores print the exact payload passed
  to `queueStore` (lane merge happens at commit, one cycle later — same
  model the interpreter uses). Stream stops after the 4th `0x418` arrival
  is recorded (first arrival + 3 iterations) or at 16384 pairs; execution
  itself continues untouched.

Default-off cost: one relaxed check per VIF1 command, per issued pair,
and per MSCAL; snapshots/strings exist only while a listed program is
armed (2 programs × ~250 pairs here). Proven zero guest-visible change:
e37a stats lines are identical to E36's everywhere overlapped (see Boots).

## Boots (Mac mini, E32-build @ fork `11725b4`, script-claimed lease, wall-bound)

| Boot | Env | Result |
|---|---|---|
| e37a | E33/E36 vsync route, wall 300, stats 1200–1500, entry `_PCS=0x40,0x10` `_VSYNC=1300` | rc 0, wall-bound, tick 1360; stats window fully settled; both blocks at vsync 1300 |

Lease released (`lease_released: true`). Trace file 145,331 B,
SHA256 `18e250ffd822c283221f012a06388c632e0ccee5181e3e916e170d046b97b37f`
(identical copy in `local/research/E37/vu1-entry-e37a.txt`).

## Per-startPC tables (e37a, vsync 1300)

Setup = pairs before the first `pc=0x418` arrival. Both setups are
straight-line (distinct PCs == pairs: 129/129 and 123/123), fall through
both `IBEQ`s and the `BAL`, and converge onto the same `0x2a8+` shared
path. No `ILW/ILWR/MTIR/MFIR/XTOP/XITOP` anywhere in either block; the
only VI writers are `LQI` post-increments, `IADDIU`, and the `BAL` link.

### startPC 0x10 (T48's 0x2; 177/vsync) — 129 setup, 250 total, arrivals=4

| Register | First writer in block | Source operands and values |
|---|---|---|
| vi13 | `pc=0x10` `LQI vf18,vf13` (`lo=0x81d26b7c`) | addr reg vi13 entry `0xd549` → `0xd54a`; `rd 329` = all zero |
| vi11 | `pc=0xb0` `LQI vf21,vf11` | entry `0x3df7` → `0x3df8`; `rd 503` = all zero |
| vi14 | `pc=0x2b0` `IADDIU vi14,vi14,3` | entry `0xd477` → `0xd47a` |
| vi15 | `pc=0x2a8` `BAL vi15,0` | link write `0x57` = already-held value → no visible change |
| **vi03** | **no writer in the block** | read-only: `IBEQ vi13,vi3,135` @`0x2c8` (not taken), `IBEQ vi13,vi3,41` @`0x408` (not taken), `IBNE vi13,vi3,-39` @`0x548` (exit, taken); entry value `-15836` (`0xC224`) via E36 end-values + no-write proof |

In-loop vi13 walk: `0xd54d→0xd54e→0xd54f→0xd550→0xd551`, `rd 333–336` all zero.

VIF packet (52 lines): `STCYCL×6 STMASK×3 STROW×3 UNPACK×6 NOP×33 MSCAL imm=2`.
UNPACKs: `V4_32 num=8 @0+TOPS`, `V4_16 num=56 @8+TOPS` (mask `0x50`),
`V3_16 num=56 @9+TOPS`, `V3_32 num=56 @10+TOPS`, `V2_32 num=1 @180+TOPS`
(`00000000 46480000`), `V4_8 num=7 @181+TOPS`; all `mode=0 men=0`.
Cross-check: `@0+TOPS` payload words 0–2 = `00008038 302e4000 00000412` =
E36's `0x10` TOP header exactly (`vumem` rows are absolute; TOPS-relative
placement is the T49-compare input, not re-derived here).
`vumem` nonzero rows: 184/1024; every setup/loop `rd` row reads zero and
matches the snapshot row-for-row.

### startPC 0x40 (T48's 0x8; 195/vsync) — 123 setup, 244 total, arrivals=4

| Register | First writer in block | Source operands and values |
|---|---|---|
| vi13 | `pc=0x88` `LQI vf21,vf13` (`lo=0x81d56b7c`) | addr reg vi13 entry `0xdbb0` → `0xdbb1`; `rd 944` = all zero |
| vi11 | `pc=0xb0` `LQI vf21,vf11` | entry `0x445d` → `0x445e`; `rd 93` = all zero |
| vi14 | `pc=0x2b0` `IADDIU vi14,vi14,3` | entry `0xe7ac` → `0xe7af` |
| vi15 | `pc=0x2a8` `BAL vi15,0` | link write, no visible change (as 0x10) |
| **vi03** | **no writer in the block** | same three readers, same outcomes; entry `-15836` (`0xC224`) |

In-loop vi13 walk: `0xdbb3→…→0xdbb7`, `rd 947–950` all zero.

VIF packet (52 lines): `STCYCL×5 STMASK×3 STROW×3 UNPACK×5 FLUSH×1 NOP×34
MSCAL imm=8`. UNPACKs: `V4_32 num=7 @0+TOPS`, `V4_16 num=57 @7+TOPS`,
`V3_16 num=57 @8+TOPS`, `V3_32 num=57 @9+TOPS`, `V2_32 num=1 @180+TOPS`
(no `V4_8@181`, unlike 0x10). `@0+TOPS` words 0–2 = `00008039 302e4000
00000412` = E36's `0x40` TOP header exactly.
`vumem` nonzero rows: 179/1024; all `rd` rows zero, matching the snapshot.

## What the T49 diff gets from this

- `vumem` at each MSCAL + the full feeding packet with TOPS-relative
  addrs and payloads → tells apart "different VU memory at MSCAL" (VIF
  UNPACK/placement upstream) from "same inputs, different VI results"
  (instruction semantics). Header-word agreement with E36 (`00008038/39
  302e4000 00000412`) proves the packet log and the memory snapshot are
  mutually consistent.
- A third outcome this trace adds: same `vumem` but different VI *entry*
  values (persistent regs `vi03/vi11/vi13/vi14` are never initialized by
  these programs) → a state-carry/ordering divergence. Entry values here:
  `vi03=0xC224` both; `vi13=0xd549` (0x10) / `0xdbb0` (0x40);
  `vi11=0x3df7` / `0x445d`; `vi14=0xd477` / `0xe7ac` (all from first-write
  olds; `vi03`/`vi15` via E36 join).

## Gaps / notes

- `pair` lines record only *changed* VI/VF (entry values reconstructed as
  above); no flag/Q/P/ACC deltas (E36 already ruled flag reads out of the
  loop span).
- Upper-op disassembly is `NOP` vs raw hex (setup uppers are FMACs shown
  as hex, e.g. `up 0x01d4a2be`); lower-op names reuse E36's mini-decoders.
  One observed upper write (`vf24.z:00000000->7f7fffff` at 0x40/pc=0xb0)
  confirms upper VF deltas are captured.
- `0x40`'s packet has one fewer UNPACK (`V4_8@181` missing) and an extra
  FLUSH vs `0x10`'s; not investigated (both converge to the same loop
  with the same wild-`vi03` signature).
- E36's `0x0`-block entry anomaly (PCs from `0x20` visited 2×) is outside
  these two blocks; the shared-path convergence (`0x2a8+`) suggests all
  stuck entries funnel through the same IBEQ-guarded shape.
- Bytes: E37-run dir 36 MB incl. frames/snaps (boot log 4.0 MB);
  internal total 26.7/200 GB cap. Trace file 145 KB — the only new
  artifact that matters.

## Exact commands

```
cmake --build ~/dev/ssx3-work/E32-build -j8   # fork ssx3 @ 11725b4
env -u PS2X_SKIP_MOVIE -u PS2X_PAD_SCRIPT ~/dev/ssx3-work/E32-build/ps2xTest/ps2x_tests  # 480/480
python3 local/research/E37/e37_boot.py --label e37a --wall 300 --snap 2.0 --stats-from 1200 --stats-to 1500 --entry-pcs 0x40,0x10 --entry-vsync 1300 --script "<route>"
python3 local/research/E37/e37_analyze.py ~/dev/ssx3-work/E37-run/vu1-entry-e37a.txt
shasum -a 256 ~/dev/ssx3-work/E37-run/vu1-entry-e37a.txt
```

(`<route>` = E33/E36 vsync route `10350:start:2500,20650:cross:2000, …`;
no push on either repo; fork ff-push + ssx3 commit pending orchestrator.)

Recommended next action (orchestrator): hand `vu1-entry-e37a.txt` + this
report to the T49 diff (done from our side), and consider a follow-up lane
for the writer of `vi03`: none of the 8 stuck entries writes it, so the
candidate sources are (a) one of the 85 healthy programs per vsync, or
(b) a VI-write mis-target in the interpreter — an entry-trace arming on a
healthy writer (or a VI-write watch) would discriminate.
