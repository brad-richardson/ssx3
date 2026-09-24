# GB7C5 — first displayed glyph-pixel writer (OpenCode Go)

Predeclared outcomes (brief): **P** = a prior packet makes the watched
FBP112 RGB transition to final glyph RGB by a measured accepted write;
**Q** = the word changes by a transfer/clear/direct VRAM path outside the
watched pixel loop, with the packet/operation found; **R** = the final word
was present before capture's first packet; **OTHER** = trace gap,
overwritten history or unknown mutation. CPU replay facts only — not a
paraLLEl damage cause. The orchestrator declares the gate.

Outcome: **P for watched pixel A.** Tick259 path3 packet5470 batch10
draws sprite `prim=sprite frame=fbp112,fbw8,psm1,fbmsk=0xff000000` and the
actual storage word moves `dc302f3b`→`dc353341`: the displayed RGB
transitions to the final glyph RGB `0x353341` by a measured changed write.
No further change in the next ~41,770 packets: pre-47240 and post-47240
snapshots both read `dc353341`, so packet47240's carrier is a
steady-state same-RGB rewrite (its CT24 read path reports `00353341`;
the `0xdc` high byte is storage alpha, invisible to the CT24 display).
B/C/D were not instrumented: A is unambiguous, per the brief's stop rule.

## 0. Pins (verified before the build)

See `pins.txt`. Fork `a01e679` on `gb4-parallel`, tree clean before
edits; capture `a6f75fb3…ad51851` by two SHA reads; paths 1,982,063
lines; Release + `DIAG_TAPS=OFF`; runner-dir guard empty.
Address basis recomputed from source (`GSPSMCT32::addrPSMCT32`, block
3584 = 112<<5, width 8): A (342,377) → `0x19ae38`, B → `0x19be80`,
C → `0x19bfa4`, D → `0x19ce38` — all four match GB7C4 `chain.tsv`
exactly. Old words at carrier time from that trace: A `00353341`
(CT24 read; storage holds `dc353341`, §4).

## 1. Source audit (read-only, before instrumenting)

All VRAM mutation paths in the direct-CPU replay funnel through
`GSCpuBackend::WriteVramUnlocked` (`gs_cpu_backend.cpp`):

| Path | Entry | Write call |
| --- | --- | --- |
| draw pixels | `Submit` → `DrawPrimitive` → `DrawSprite/DrawTriangle/DrawLine/Point` → `WritePixel` | `WriteVramUnlocked(fpsm,fbp,fbw,x,y)` + Z write |
| host→local upload | GIF-packet IMAGE data / kind-5 `uploadImageNative` → `UploadImage` | `WriteVramUnlocked(dpsm,dbp,dbw,…)` per format |
| local→local | GIF TRX packet → `BeginTransfer(dir 2)` → `PerformLocalToLocalTransfer` | read + `WriteVramUnlocked` per pixel |
| local→host | `BeginTransfer(dir 1)` | reads only — no mutation |
| clear | kind-7 `clearFramebufferContext` → `ClearFramebuffer` | `WriteVramUnlocked` loop over scissor rect |
| direct | `GS::WriteVram` → `WriteVram` | `WriteVramUnlocked` |

Capture-kind audit over the full 2,067,571 records (8-byte `PS2XGSC1`
magic skipped): kind-1 packet 1,982,063, kind-2 priv 16,264, kind-3
transfer 66,244, kind-4 marker 3,000 — **zero** kind-5/6/7 records, so
no native upload, readback or clear record exists anywhere in the
stream (both replay summaries confirm `readbacks=0 clears=0`). Kind-3
is audit-only ("operation reproduced by the source packet immediately
preceding it"). PrivWrites touch regs only. The watch therefore covers
every mutating path by construction; any residual gap would surface as
`capped=1` or an unknown op tag, both of which `check.py` maps to
OTHER. Neither occurred.

## 2. Implementation (private fork, 3 files, default-OFF)

- `ps2xRuntime/include/runtime/gs/gs_cpu_backend.h`: `Gb7c5PacketContext`
  (tick/packetIndex/path/batch) + `ps2xGb7c5ProbeOpen/Close/
  SetPacketContext/NotePacket47240Done/Enabled/RegisterVram` decls +
  five private hook decls.
- `ps2xRuntime/src/lib/gs/gs_cpu_backend.cpp`: default-OFF watch.
  `WriteVramUnlocked` loads the 4 storage bytes at `0x0019ae38`
  before/after the real write and logs a `change` row on difference
  (op tag, write coords/psm/base/bw, old→new, packet context). Op tags
  are set at each funnel entry: `NoteGb7c5BatchBegin` per
  `DrawPrimitive` (same batch counting as GB7C2/GB7C4, plus prim type
  and FRAME regs), `NoteGb7c5UploadOp` (BITBLTBUF dest + TRXREG/POS),
  `NoteGb7c5LocalToLocalOp` (src+dst regs), `NoteGb7c5ClearOp`,
  `NoteGb7c5DirectOp`. `SetPacketContext` emits `snapshot-start`
  (packet 0) and `pre-47240`; the harness calls
  `NotePacket47240Done` right after packet47240 for `post-47240`.
  Snapshots read the registered live VRAM base. OFF path = one
  `enabled` branch per write; rendering untouched. Caps: 20,000 rows /
  8 MiB, stop-writing-at-cap, `GB7C5_SUMMARY` line on close.
- `ps2xTest/src/ps2_gs_replay_tests.cpp`: `PS2X_GS_REPLAY_GB7C5_TRACE`
  (direct-CPU only, exclusive with GB5/GB5B/GB7B/GB7C2/GB7C4 both
  directions), per-packet `SetPacketContext`, post-47240 note, stop
  after the first sampled marker ≥601 (tick 650 at STEP=50),
  `GB7C5 replay reached marker 601` assertion. No pixel poke.

## 3. Validation (exact commands from `~/dev/ssx3-work/GB4/PS2Recomp`)

| Step | Command | Result |
| --- | --- | --- |
| build (1, incremental) | `cmake --build ../build --target ps2x_tests > ../run/gb7c5/build-1.log 2>&1` | exit 0, first try — no repair; `ps2x_tests` 8,234,792 B; only pre-existing `-Wswitch` warnings in `ps2_gs_memory.h`; `PS2X_ENABLE_DIAG_TAPS` untouched |
| flag-OFF suite | `../build/ps2xTest/ps2x_tests > ../run/gb7c5/suite-1.log 2>&1` (flag unset) | 556/556 pass |
| ON replay (P-lane slot 1, claimed/released per replay) | `PS2X_GS_REPLAY_CAPTURE=../run/gb4p4.capture.bin PS2X_GS_REPLAY_PATH_FILE=../run/gb4p4.paths.txt PS2X_GS_REPLAY_STEP=50 PS2X_GS_REPLAY_PPM_TICKS=600,601 PS2X_GS_REPLAY_PPM_DIR=../run/gb7c5/ppm PS2X_GS_REPLAY_GB7C5_TRACE=../run/gb7c5/watch.tsv ../build/ps2xTest/ps2x_tests > ../run/gb7c5/replay-1.log 2>&1` | 556/556 pass; `GB7C5_SUMMARY rows=7 bytes=891 capped=0`; `packets=53269 priv=3689 transfers=483 markers=650 samples=13`; no GPU replay |
| OFF control replay (slot 1, same env minus trace flag, `PPM_DIR=../run/gb7c5/ppm-off`) | `... ../build/ps2xTest/ps2x_tests > ../run/gb7c5/replay-off.log 2>&1` | 556/556 pass; full stream (`packets=1982063 priv=16264 transfers=66244 markers=3000 samples=60`) |

OFF-control equivalence: `GB4_FRAME` tick600 `present=a6948f2`,
tick601 `present=582dd887` in ON, OFF, and the GB7C2/GB7C4 baselines —
all identical. PPM bytes ON vs OFF identical at both ticks (sha256:
600 `895856fd…`, 601 `660d38f3…`, each pair matching, both matching
GB7C4). First ON attempt's PPMs were lost (dirs not pre-created —
`dumpPpm` does not mkdir); both PPM dirs were created and both replays
re-run under a fresh slot-1 claim. `check.py` → ACCEPT (see
`check-result.txt`).

## 4. Producer table (authoritative: `watch.tsv`, 7 data rows)

Storage words are CT24 with a `0xdc` high byte; displayed RGB is the
low 3 bytes (GB7C4's read path reports `00353341` for storage
`dc353341`).

| seq | tick/packet/path/batch | op / state | old→new (RGB effect) |
| --- | --- | --- | --- |
| 0 | 40/0/3/0 | `-` `snapshot-start` | `00000000` (R excluded: capture starts zeroed) |
| 1 | 256/5139/3/1 | `upload` `dst=dpsm27,dbp5760,dbw8 rrw512,rrh512 dsax0,dsay0` (write coords 86,121 in the upload surface) | `00000000`→`dc000000` — earliest storage change, high byte only, **invisible** |
| 2 | 257/5223/3/10 | `draw` `prim=sprite frame=fbp112,fbw8,psm1,fbmsk=0xff000000` | `dc000000`→`dc2c2a36` — earliest visible RGB change |
| 3 | 258/5348/3/10 | same draw state | `dc2c2a36`→`dc302f3b` |
| 4 | 259/5470/3/10 | same draw state | `dc302f3b`→`dc353341` — **first final-RGB write (P producer)** |
| 5 | 601/47240/3/1 | `pre-47240` | `dc353341` — unchanged across ~41,770 packets |
| 6 | 601/47240/3/32 | `post-47240` | `dc353341` — carrier rewrote same RGB |

Predicted vs observed: P required a prior packet's measured accepted
write creating the final glyph RGB — seq4 (packet5470) is exactly that.
Q would require the final value to arrive by transfer/clear/direct
path — the only upload (seq1) wrote an invisible byte, never the RGB.
R required the final word before packet 0 — snapshot is zero. No OTHER
condition (uncapped, all ops known, snapshots present, order/canonical
address verified by `check.py`).

## 5. Gaps / recommended next action

- The seq4 producer draw is attributed to packet5470/batch10/sprite/
  FBP112 state, but this probe does not log that sprite's TEX0/UV/TEST/
  vertex state, so *what image* it sampled is not identified here — a
  GB7C4-style tap trace on packet5470 batch10 would name the source.
- Seq1's `dpsm27` (T8H) bulk upload overlapping the watched word is
  logged only by its dest regs; its content cause is out of scope.
- Ticks 259→601 hold the value steady on the CPU path; nothing here
  bears on the paraLLEl-GS damage cause (CPU replay only).
- Recommended next action: tap-trace the packet5470 batch10 sprite at
  (342,377) to identify which texture/CLUT supplies RGB `353341`
  (the menu-font upload precedes it), then compare that draw's
  CPU/GPU behavior. The GB7C4 §5 one-pixel carrier poke stays valid
  and orthogonal.

## 6. Receipts

- ssx3 (this dir): `REPORT.md`, `watch.tsv` (7 data rows, 894 B, full
  trace as excerpt), `check.py`, `check-result.txt`, `pins.txt`,
  `sizes.txt` — committed `[GB7C5]`, `Orchestrated-By: opencode`, no push.
- `run/gb7c5/` (private, not committed): `build-1.log`, `suite-1.log`,
  `replay-1.log` (ON), `replay-off.log` (OFF control), `watch.tsv`,
  `ppm/vq-00060{0,1}.ppm`, `ppm-off/` same two.
- Fork: `[GB7C5]` commit `8966b0b` on `gb4-parallel` (3 files:
  replay test cpp, gs_cpu_backend.cpp, gs_cpu_backend.h),
  `Orchestrated-By: opencode` trailer, no push.
