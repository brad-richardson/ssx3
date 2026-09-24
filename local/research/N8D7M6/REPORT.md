# N8D7M6 — one same-stream Odin/Mac selected-VRAM comparison (OpenCode Go)

**State: device + Mac replay COMPLETE, predeclared category A. Exactly one
Odin install and one launch of the reviewed launcher; two Mac paraLLEl replay
invocations of the same captured stream (second only because the first ran
with the wrong cwd and tripped an unrelated suite test — disclosed in §7).
No source/Android/iOS edit, no upstream contact, no push. The orchestrator
views frames and gates the result; no Turnip/shader/barrier cause is claimed
here.**

## 1. Release and script pins

| Item | Value |
| --- | --- |
| Released `launch.py` SHA-256 | `46e07188edda3704e60d9db63d3ac6e2d36c09d52a8ea21863808ea2f901494b` (verified unchanged after the run) |
| `accept.py` SHA-256 at prepared gate | `6ba84cf04d7f887523d381cfcacbfaf63228673df9c8e3e09aef91c19f96c006` |
| `accept.py` SHA-256 as run for `--final` | `ab2a3576f87979e0a0cc963bd18c0c8f64a59bb207db2d710333a602dbbd3459` (one-line cwd fix only: run the replay binary with cwd=fork worktree; see §7) |
| `launch.py` after release | **Unaltered** (SHA re-verified `46e07188…`) |
| Prepared gate | `accept.py --prepared` PASS before any device action (receipt `prepared-gate.txt`) |

## 2. Odin run (one install, one launch)

Released command, from `/Users/brad/dev/ssx3`:

```sh
python3 -u local/research/N8D7M6/launch.py --released-sha 46e07188edda3704e60d9db63d3ac6e2d36c09d52a8ea21863808ea2f901494b
python3 local/research/N8D7M6/accept.py --capture
python3 -u local/research/N8D7M6/accept.py --final
```

| Field | Observation |
| --- | --- |
| Preflight (before install and before launch) | state=device, lease free/held, keyguard `showing=false`, battery 100% status 5, free ~25.9 GB (≥10 GiB) |
| Install/inputs | one `adb install -r` Success; installed APK / ELF / ISO each matched pinned SHAs on two device reads; `mc0` empty; unique empty frame dir; capture target absent before run |
| Env | N8D7M2 env + `PS2X_GS_CAPTURE=…/n8d7m6.gs`, `PS2X_GS_CAPTURE_STOP_TICK=2050` (`ps2x.env` SHA `176eff84…`) |
| Launch/stop | one launch, PID 6028; BACK once at ~5 s; elapsed 115.9 s; stop `first complete tick2050 receipt+frame+closed stream`; no second run |
| Alignment | tick 2050, FBP 112, PMODE `ff21`, 512×448; status 2; `control=128 expected=128 PASS` |
| Selected metadata | tick 2050, fbp 112, fbw 8, psm 1, dbx/dby 0, phase 0, stride 2, mask 4194303, samples 1, promoted 0, extent/valid 512×224 |
| Selected vectors (Odin) | input/circuit/stage/oracle each 448 words, occupied 3990, active **23**; packed SHA `2106649d…c9137` identical all four; `input_circuit_equal=448/448`, `circuit_stage_equal=448/448`, `oracle_input_equal=448/448` logged and recomputed |
| Final vectors | sampled == raw, 896 words, occupied 7917, active 46 |
| Controls (Odin) | 8/8 addresses in kOracleControls order; values `0x0E0000=0x00060000`, `0x0E0534=0x000C0000`, `0x0E0040=0x000C0000`, `0x1BFFF4=0x00000000`, `0x0E2000=0x000C0000`, `0x0F0000=0xFF0C0000`, `0x0E1FFC=0x00000000`, `0x0F2000=0x00000000` — observation only, not cross-device identity |
| Capture | `PS2XGSC1`, 1,100,696,462 B (≤4 GiB), SHA `f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593`; two device + two Mac reads match; EOF marker tick 2050; 862,958 packets / 11,499 priv / 25,445 transfers / 2,050 markers / 0 readbacks / 0 clears |
| Frame | seq 0 tick 2050, 512×448, display/source FBP 112/112, fallback 0, `pmode=0xff21`; PNG SHA `1fec7d3983c6af4c084d1ada9cc07241dd11a38781d0d37c06f06772959114c4` (two device + two local reads); viewed: mostly black with sparse pale terrain/rider fragments and HUD edge, consistent with active-23 selected input |
| Cleanup | `am force-stop`, PID absent, lease `LEASE_FREE N8D7M6 done`; closed log gzip 6,090 B; text log ≤16 MiB |

## 3. Mac paraLLEl replay of the same stream

Binary: N8D7M5 `ps2x_tests` `d06ff1aa…0b77f` (fork `a8cfefa` incl. N8D7L oracle
`d1ba1d4`; codegen `8ea8ed43…`; parallel source `N8D7F/parallel-gs`), env
`PS2X_GS_REPLAY_BACKEND=parallel` + `PS2X_N8D7F_SELECTED_CAPTURE=1` +
`PS2X_N8D7L_ORACLE=1` + `PS2X_N8D5_TILE_CAPTURE=1`, one P-lane slot, ≤600 s.
Two invocations happened (§7); the gated record is the second (exit 0,
suite 585/585, log ≤16 MiB).

| Field | Mac replay (same `n8d7m6.gs`, SHA `f6a78f71…`) |
| --- | --- |
| Summary | `mode=queue backend=parallel`, packets=862958 priv=11499 transfers=25445 markers=2050 readbacks=0 clears=0 samples=41 — counts identical to capture |
| Backend stats | 862,958 packets, 41 presents, zero null scanouts/unsupported clears/VRAM I/O, `init_ok=1` |
| Frame | `GB4_FRAME tick=2050 backend=parallel pmode=ff21 dispfb1=9070 dispfb2=1400 display_fbp=112 source_fbp=112 preferred=0 present=d19b96fe` |
| Selected metadata | 11 shared fields byte-equal to Odin selected metadata; status 2 |
| Selected vectors (Mac) | input/oracle each 448 words, occupied 64399, active **300**; packed SHA `1d847d50…bd988b` identical; `oracle_input_equal=448/448` |
| 4 MiB SHAs | `vram_sha256=99053d8f…` real digest; `input_sha256==circuit_sha256` |
| Controls (Mac) | 8/8 in order, values exactly the N8D7L literal set (`0x0E0000=0x00260803` … `0x0F2000=0x00604400`) |

## 4. Outcome table (predeclared categories)

Active = 448-tile active count (≥32-pixel tiles); thresholds: sparse ≤100,
broad ≥250; descriptor = the 11 shared selected fields (tick/FBP/FBW/PSM/
DBX/DBY/phase/stride/mask/samples/promoted).

| Category | Predeclared requirement | This run | Met? |
| --- | --- | --- | --- |
| A | complete identical stream replay, same descriptor/phase, Mac broad + Odin sparse | counts identical; descriptor equal; Mac 300/300, Odin 23/23 | **YES** |
| B | same descriptor, both sparse | Mac broad (300) | no |
| C | descriptor/phase/base mismatch despite same stream | descriptor equal | no |
| D | same descriptor, both broad | Odin sparse (23) | no |
| OTHER | incomplete stream, bad gate, intermediate counts, vector mismatch, missing SHA | none apply | no |

**Result: category A** — same-stream, same-descriptor comparison: Mac
paraLLEl selected input broad (300/448), Odin selected input sparse
(23/448). This locates a device-specific selected-VRAM divergence
at/before the mapped snapshot on this stream. Per the brief, this does
**not** distinguish missing GPU writes from snapshot/copy ordering, and no
Turnip/shader/barrier cause is claimed.

## 5. Limits / gaps

- Odin control-word values (mostly dark/zero) vs Mac literal values are a
  same-stream observation consistent with the sparse snapshot, not a
  word-fault verdict; full 448-tile vectors (not 8 words) carry the
  category.
- The Odin frame reading ("mostly black with sparse fragments") is a worker
  viewing note; the orchestrator views `upload-0.png` and gates.
- No CPU replay was run; no speed number is quoted (diagnostic wall only).
- First Mac replay log was overwritten by the rerun before the preservation
  instruction arrived (§7); only its key lines survive in the driver
  transcript, not the file.

## 6. Receipts

- ssx3 (this dir): `REPORT.md`, `launch.py`, `accept.py`,
  `prepared-gate.txt`, `tile-excerpt.txt`, `result.json` (vectors stripped
  to summaries), `comparison.json`, `upload-0.png` + `upload-0.txt`.
- Scratch `~/dev/ssx3-work/N8D7M6/`: `n8d7m6.gs` (1.10 GB, kept out of git),
  `mac-parallel.log` (second run), `mac-parallel/` hashes+PPM,
  `logcat-pid.txt`, `logcat-all.txt.gz`, `driver.log`, `ps2x.env`.
- Commit `[N8D7M6]` with `Orchestrated-By: opencode`, no push.

## 7. Budget deviation (disclosed)

Two Mac paraLLEl replay invocations instead of one. The first invocation
replayed the stream completely (all §3 counts/frame/vectors present in its
log) but exited nonzero solely because `accept.py` ran the binary with
cwd=`/Users/brad/dev/ssx3`, tripping the known unrelated suite test `VU0
macro mappings cover all S1/S2 enums` (584/585; N8D7M5 REPORT §5 documents
it reads `instructions.h` by relative path and must run from the fork
worktree). The checker was fixed with a one-line cwd change (accept.py
`ab2a3576…`; `launch.py` untouched), the P-lane slot was released, and the
second invocation ran clean (exit 0, 585/585) and is the gated record. The
second run overwrote `mac-parallel.log`/hashes/PPM in scratch — the first
log file is lost; its replay lines (summary/frame/Failed: 1/VU0 name) were
observed before overwrite and are quoted above. No further replay, build,
or device run was made.
