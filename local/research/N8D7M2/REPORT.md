# N8D7M2 — one Odin independent-oracle frame

**State: PART 1 + PART 2 COMPLETE. The orchestrator released `launch.py` SHA
`6b5976ce…677ef`; exactly one install and one launch ran, the app was
force-stopped, PID verified absent and the lease released. The run classified
as predeclared `CATEGORY A`. No source, build, iOS, upstream or push action
followed. The orchestrator views the frame and gates the result; no cause is
declared here.**

This adapts the released N8D7I launcher to one N8D7M1 install and one launch,
enabling `PS2X_N8D7L_ORACLE=1` alongside the N8D7I selected/stage/tile flags. It
parses the full 448-word `[n8d7f] oracle_tile_counts` vector plus the N8D7I
vectors, the `[n8d7l]` metadata / `oracle_controls` / `oracle_input_equal`
lines, checks the eight literal control addresses against the N8D7L Mac control
set, checks that every shared selected/oracle metadata field describes the same
frame, and classifies one same-run tick-2050 frame into **A/B/C/D/OTHER**.

## 1. Release hold and exact script SHA

`launch.py` refuses to run without `--released-sha <reviewed SHA-256>`, refuses
a changed file, and the one-run guard refuses a reused scratch receipt. Two
matching local reads:

| Artifact | SHA-256 (two reads) |
| --- | --- |
| `local/research/N8D7M2/launch.py` | `6b5976ceca948f32ce45c7c2fb4619d72b7d946180a4cd1849eff562c09677ef` |
| `local/research/N8D7M2/parser_selfcheck.py` | `b5268d7037914dee49e747712e1f1758e8ef6e5a368f9241a1375f28d3dc4965` |
| `local/research/N8D7M2/parser-selfcheck.txt` (45/45 PASS) | `22e927fffa622a45c6f26640a6f63fb8d36c9147e187886b4ebf05130fc80808` |
| `local/research/N8D7M2/launcher.diff` (383 lines vs N8D7I) | `adb762ed5a43d7e03250ca7be45f0d68e512ee3f769ff720eb84776aea97b8f0` |

Release-hold behaviour checked locally (wrong SHA refused, no device contact):
`python3 local/research/N8D7M2/launch.py --released-sha 0…0` →
`review hold: launch.py SHA differs from reviewed pin`, exit 1.

Released command to run once, from `/Users/brad/dev/ssx3` (Part 2 only):

```sh
python3 -u local/research/N8D7M2/launch.py --released-sha 6b5976ceca948f32ce45c7c2fb4619d72b7d946180a4cd1849eff562c09677ef
```

## 2. Fixed inputs and local pin verification

| Field | Predeclared pin | Local check (Part 1, read-only) |
| --- | --- | --- |
| APK | `/Users/brad/dev/ssx3-work/N8D7M1/app-release.apk`, 153,736,732 B, SHA `e077bef8a7ba8aab44f46c515f79fade1ae045cc337bf7285e7b652e739758a1` | size matches; two SHA reads match |
| Packaged runner | `f3de999acc9227b82a9d9fab6a4a0b5b7fb279e6205991c1b3022da781e3c1bf`, 139,497,400 B, Build ID `73291620f0c62fdc01ac0b603e9e5cca3114d0a5` | two APK-member reads match |
| Packaged Turnip | `717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d`, 14,188,488 B | two APK-member reads match (unchanged) |
| Packaged HAL shim | `1b49d27c839f25363237d8276c91a401602845ee8eef67de50d6540f4cdfc387`, 7,112 B | two APK-member reads match (unchanged) |
| Installed ELF | `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc` | device double-read at run preflight |
| Installed ISO | `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5` | device double-read at run preflight |
| Odin | serial `622c49b1`; lease `/data/local/tmp/mg/LEASE` | not contacted pre-release |
| Run budget | One install, one launch; no second run | enforced by one-run guard |

Packaged lib members are exactly `lib/arm64-v8a/{libhardware.so,
libps2EntryRunner.so, libvulkan_freedreno.so}` (no x86). Pin conflict check vs
N8D7I: Turnip, HAL, ELF and ISO are identical; only the APK and packaged runner
differ, which is the point of the N8D7M1 oracle package. No conflict.

## 3. Predeclared same-frame gate

All categories require this same tick-2050 frame; anything else is OTHER.

| Requirement | Predeclared value |
| --- | --- |
| Alignment (`[n8d5b]`) | tick 2050, FBP 112, PMODE `0xff21`, 512×448 |
| Selected metadata (`[n8d7f]`) | status 2; valid 512×224; samples 1; promoted 0; tick 2050, fbp 112 |
| Oracle metadata (`[n8d7l]`) | tick 2050, fbp 112, fbw 8, psm 1, samples 1, promoted 0, mask 4194303 |
| Selected/oracle field alignment | every shared field — tick, FBP, FBW, PSM, DBX, DBY, phase, stride, mask, samples, promoted — must be equal between `[n8d7f]` and `[n8d7l]`; any disagreement is OTHER |
| Selected vectors (`[n8d7f]`) | input / circuit / stage / oracle each 448 tiles |
| Existing stages (`[n8d6a]`) | circuit1 512×224×448, pre_deinterlace_merged 512×224×448, final 512×448×896; control 128 each |
| Old-final control (`[n8d5b]`) | `control=128 expected=128 PASS` |
| Final vectors (`[n8d5b]`) | sampled and raw 896 tiles each, exact 896/896 equality; each vector consistent with its summary |
| Selected/oracle consistency | each parser vector has 448 words; occupied/active match the logged summary; packed SHA compared only when the firmware printed a real digest (Android logs `unavailable`) |
| Controls (`[n8d7l]`) | exactly eight well-formed `addr=value` words, addresses in kOracleControls order equal the eight literal addresses below |
| Equality counts | recomputed `input_circuit_equal`/`circuit_stage_equal` must equal the logged counts; logged `oracle_input_equal` must equal the recomputed oracle/input cell equality |
| Frame | same-run tick-2050 PNG + metadata, 512×448, FBP 112/112, fallback 0, PMODE `0xff21` |
| Errors | no probe/pipeline error, no `[n8d7f] OTHER` / `[n8d7l] OTHER` line |

Stage locations, **not** cause or driver verdicts; Mac and Odin GS streams are
not byte-identical. Active means a 16×16 tile with ≥32 qualifying pixels.

## 4. Category table (predeclared thresholds)

`oracle` = independent fork-table census; `input` = G43 selected-input vector,
both out of 448. `equal` = logged `oracle_input_equal`.

| Category | requirement | Meaning |
| --- | --- | --- |
| A | equal 448/448 and oracle active ≤100 and input active ≤100 | oracle and G43 selected input agree; same-run raw snapshot sparse |
| B | equal <448/448 and oracle active ≥250 and input active ≤100 | oracle broad, G43 input sparse — decoder mismatch candidate |
| C | equal <448/448 and oracle active ≤100 and input active ≥250 | oracle sparse, G43 input broad — decoder mismatch candidate |
| D | equal 448/448 and oracle active ≥250 and input active ≥250 | sparsity not reproduced on this Odin run |
| OTHER | any other count combination, incomplete gates, missing/malformed vectors or controls, metadata misalignment, logged equality mismatch, error line | |

`oracle_input_equal` must equal the recomputed equality; A/D require 448/448,
B/C require <448/448. Circuit, GPU-stage and final counts are reported
separately and are **not** part of the A–D threshold unless a gate fails. B/C
are decoder-mismatch candidates only; no address or shader cause is asserted.

## 5. Eight literal control words

Addresses (compile-time constants in `kOracleControls`, expected identical on
device) and the N8D7L Mac literal values:

| # | Address | Mac value |
| --- | --- | --- |
| 1 | `0x0E0000` | `0x00260803` |
| 2 | `0x0E0534` | `0x00260802` |
| 3 | `0x0E0040` | `0x00260804` |
| 4 | `0x1BFFF4` | `0x000C0000` |
| 5 | `0x0E2000` | `0x00260802` |
| 6 | `0x0F0000` | `0xFF230401` |
| 7 | `0x0E1FFC` | `0x003D2B00` |
| 8 | `0x0F2000` | `0x00604400` |

Gate (orchestrator clarification, this handback): the eight **addresses and
their order** are the gate. Exactly eight words must be logged, in this address
order; a missing word, wrong count, malformed field or reordered address is
OTHER. The on-device **values** are each reported as a separate same-run
comparison against the Mac literals (`value_matches`, 0–8, and the eight
`addr=value mac=… match=…` lines). A value mismatch alone must **not** force
OTHER, because Mac and Odin streams are not proved identical; the values are an
observation, not a cause and not cross-device identity. Separate from the
controls, the launcher reports the 448-cell oracle/input comparison and the
logged `oracle_input_equal`.

## 6. Parser self-check

`python3 local/research/N8D7M2/parser_selfcheck.py` — **45/45 PASS**, written to
[parser-selfcheck.txt](parser-selfcheck.txt). It covers:

- the saved N8D7L Mac receipt (`local/research/N8D7L/replay-excerpt.txt`): the
  full `[n8d7f] oracle_tile_counts` decodes to 448 words, occupied 64,374,
  active 300, packed SHA `e1dc4c5c…c78a593`; input/circuit/stage/oracle all
  equal; `[n8d7l] oracle_controls` parses to the eight literal address=value
  pairs in order; `oracle_input_equal=448/448` and the recomputed equality match;
- a synthetic comma-led 448-word `oracle_tile_counts` continuation, plus
  trailing-comma and three-segment variants, all decoding to 448 words;
- rejection of oversized (449), non-decimal, incomplete and summary-only oracle
  inputs; control payloads with 7 words or a malformed field rejected;
- `classify` over saved N8D6C `[n8d5b]`/`[n8d6a]` lines plus synthetic
  receipts: A (sparse, equal), B (oracle high / input low, 168/448), C (oracle
  low / input high, 168/448), D (equal high, and the saved Mac vector), and
  OTHER for logged-equality mismatch, mid-range equal active, reordered control
  addresses, missing oracle vector and missing `[n8d7l]` lines;
- **metadata alignment**: A when the shared selected/oracle fields agree
  (including a non-default matching stride/dbx pair), and OTHER for a
  selected/oracle mismatch in each of stride, dbx, dby, phase, fbw, psm, mask,
  samples, promoted, tick and fbp.

## 7. Launcher changes vs N8D7I

`launcher.diff` (383 lines) is the exact unified diff against
`local/research/N8D7I/launch.py`. Functional changes: N8D7M2 scratch/APK/lease
paths and pins; `PS2X_N8D7L_ORACLE=1` added to the env; a `parse_controls`
helper and `oracle_details`; `[n8d7f] oracle` summary and 448-word
`oracle_tile_counts` parsing plus `[n8d7l]` metadata/controls/equal parsing;
`[n8d7l] OTHER` added to the error scan; `classify` extended to the A/B/C/D
thresholds with the oracle gates, the shared selected/oracle metadata
alignment check, and the logged-equality check; a bounded `tile-excerpt.txt`
writer. Preserved unchanged: I26-FAST pad route, parallel backend, Turnip, dev
movie bypass, tick-2050 frontend dump, same-PID logcat, 16 MiB log cap, one-run
guard, release-by-script-SHA hold, and cleanup.

## 8. Device procedure and stop rules (Part 2)

Preflight before install and immediately before launch: serial `622c49b1`
online; lease free; `KeyguardServiceDelegate showing=false`; battery charging
or full and ≥20 %; free storage ≥1 GiB. If locked, stop and tell the
orchestrator so Brad can unlock. Claim the lease, install even if present,
double-read installed APK/ELF/ISO, require empty `mc0` and a unique empty frame
directory. Set parallel backend, Turnip, dev movie bypass, installed ISO,
I26-FAST vsync pad route, `PS2X_N8D5_TILE_CAPTURE=1`,
`PS2X_N8D7F_SELECTED_CAPTURE=1`, `PS2X_N8D7L_ORACLE=1`, one frame dump at
tick 2050, and progress-only vsync log. Capture same-PID logcat to a 16 MiB cap;
send BACK once at ~6 s only for the USB dialog.

Stop at the first complete aligned oracle/selected receipt plus frame; first
fatal or process exit; tick 2100 without a complete receipt; 180 s below tick
1700; or 300 s wall. Force-stop after the run, verify the PID is gone, and
release the lease even on error. Pull only the tick-2050 PNG/txt with two
device and two Mac SHA reads; compress the closed log in scratch. Report full
vectors (or a bounded file + SHA), the eight control words, equality, frame,
cleanup and first failure. Commit named text/PNG receipts `[N8D7M2]` with
`Orchestrated-By: opencode`; no push; hand back the evidence table and a
recommended next action, without declaring the verdict. No diagnostic timing is
reported as speed.

## 9. Caps

Mac scratch `~/dev/ssx3-work/N8D7M2` 100 KiB (<500 MiB); committed
receipts/images 228 KiB (<8 MiB); global mini ssx3 <200 GB. No diagnostic
timing is reported as speed.

## 10. Part 2 run receipt

One `--released-sha` run, exit 0. Receipts committed in this directory:
[result.json](result.json), [driver.log](driver.log), [ps2x.env](ps2x.env),
[tile-excerpt.txt](tile-excerpt.txt), [upload-0.png](upload-0.png),
[upload-0.txt](upload-0.txt).

| Field | Observation |
| --- | --- |
| Script / env SHA | `6b5976ceca948f32ce45c7c2fb4619d72b7d946180a4cd1849eff562c09677ef` / `dd8bdd9470b40847c885334a7f4c52fdbe4ddc3a5320fb9d41b7f20bdfa7c822` |
| Preflight before install | state=device, lease `LEASE_FREE N8D7I done`, keyguard false, battery 100% (`status 5`), free 25,895,268,352 B |
| Preflight before launch | held lease `N8D7M2 one-launch`, keyguard false, battery 100% (`status 5`), free 25,894,244,352 B |
| Install and input pins | one `adb install -r`: Success; installed APK / ELF / ISO each matched on two device reads; `mc0` empty; unique empty frame dir |
| Flags | parallel backend, Turnip, dev movie bypass, installed ISO, I26-FAST vsync pad route, `PS2X_N8D5_TILE_CAPTURE=1`, `PS2X_N8D7F_SELECTED_CAPTURE=1`, `PS2X_N8D7L_ORACLE=1`, frame dump at tick 2050, vsync-rate log |
| Launch and stop | one launch, PID `24461`; one BACK at 5.3 s; elapsed 116.06 s; final tick 2053; stop `first complete oracle and vector receipt with frontend dump`; no second run |
| Alignment | tick 2050, FBP 112, PMODE `ff21`, 512×448 |
| Selected metadata | tick 2050, fbp 112, fbw 8, psm 1, dbx 0, dby 0, phase 0, stride 2, mask 4194303, samples 1, promoted 0, extent/valid 512×224, status 2; `bytes=5177344`; SHA fields `unavailable` (Apple-only) |
| Oracle metadata | tick 2050, fbp 112, fbw 8, psm 1, dbx 0, dby 0, phase 0, stride 2, mask 4194303, samples 1, promoted 0 — all 11 shared fields equal the selected metadata (alignment gate PASS) |
| Selected input/circuit/stage | each 448 words, occupied 2058, active 15; recomputed packed SHA `bd33829e1337dee5da54c2dd1b02cc8de9769ecbf8bf7de7585333f02a19d5cd`; `input_circuit_equal=448/448`, `circuit_stage_equal=448/448` |
| Oracle vector | 448 words, occupied 2058, active 15, recomputed packed SHA `bd33829e…a19d5cd`; `oracle_input_equal=448/448` logged and recomputed; input / circuit / stage / oracle cell-equal |
| Existing stages | circuit1 512×224×448 (occ 2058, act 15, control 128); pre_deinterlace_merged same; final 512×448×896 (occ 4355, act 29, control 128) |
| Old-final control and summaries | `control=128 expected=128 PASS`; sampled `896/4355/29`; raw `896/4355/29` |
| Final vectors | sampled == raw; 896 words; recomputed packed SHA `887f999897945c094e52d23730ee22573d6dd40c3a9b9a3819bd3e55ff4e5f73` |
| Controls (`[n8d7l]`) | 8/8 words present, addresses/order match the pinned kOracleControls set; value matches vs the Mac literal set **0/8** (all eight on-device words differ) — reported separately, not a gate or cause |
| Frame | seq 0 tick 2050, 512×448, display/source FBP 112/112, fallback 0, `fnv1a=17e31fb5`, `smode2=0x1`, `pmode=0xff21`; PNG SHA `1a6a89e9ff3b915292a04a05b63eb8fdaabad1937cf076641dcf57ae741c54e3` (two device + two local reads); metadata SHA `158463fd324976cc6171a9c65e5c4628e231d59e52eea5c7a6549d2611d36738` |
| Probe/pipeline errors | none |
| Category | **A** — oracle and G43 selected input equal 448/448, each active 15 (≤100); circuit/stage active 15, final active 29 |
| Cleanup | `am force-stop` completed, PID absent, lease `LEASE_FREE N8D7M2 done`; closed log gzip 5,625 B in Mac scratch |

An independent re-parse of the saved same-PID log with the released parser
reproduces alignment, stages, all four 448-word vectors (SHA `bd33829e…`),
sampled == raw (SHA `887f9998…`), the eight control addresses and the 448/448
equalities, and classifies A.

The run is a same-frame observation only. It does not declare a cause, a
Mac/Odin stream identity or a speed result; the orchestrator views
`upload-0.png` and gates the category.

## 11. Gaps and handback

- The control **values** are reported, not gated: on this run all eight differ
  from the Mac literal set (0/8). That is consistent with a different (sparse)
  Odin stream and is **not** called a cause or an address/data fault.
- The frame is mostly black with isolated snowy-terrain and rider fragments,
  as in N8D7I; this run's selected active count is 15 (N8D7I 35) on a different
  boot, so cross-run sparsity is not constant.
- No cause, driver, address or shader verdict; no Mac/Odin stream identity is
  claimed. No second run, source or build change, iOS action, upstream contact
  or push.
- Recommended next action (for the orchestrator, not a verdict): gate this
  frame and, since oracle == G43 selected input on this Odin run, consider a
  bounded same-run raw-VRAM discriminator to separate sparse raw VRAM from CPU
  decode / input selection, rather than another selected-input comparison.
