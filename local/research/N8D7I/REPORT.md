# N8D7I — one Odin selected-input/circuit/GPU-stage frame

**State: one released run completed as `CATEGORY A`. The orchestrator released
`launch.py` SHA `c842e4c7…7013c`; exactly one install and one launch ran, the
app was force-stopped, PID verified absent and the lease released. No source,
build, iOS, upstream or push action followed. The orchestrator views the frame
and gates the result; no cause is declared here.**

This adapts the released N8D6C launcher for one N8D7H install and one launch,
enabling `PS2X_N8D7F_SELECTED_CAPTURE=1` alongside the N8D6C stage/tile flags.
The corrected comma-led continuation parser handles all five vectors; the
Apple-only packed SHA is handled by recomputing it from the full parsed vectors,
and the input/circuit/stage equality counts are recomputed so the intended B/C
divergence is a result, not OTHER.

## Release hold and exact script SHA

`launch.py` refuses to run without `--released-sha <reviewed SHA-256>` and
refuses a changed file or a reused scratch receipt. Two matching local reads:

| Artifact | SHA-256 (two reads) |
| --- | --- |
| `local/research/N8D7I/launch.py` | `c842e4c7b92ec01f49566d9cfc88952e174c8f25462972d70ba4a14a5837013c` |
| `local/research/N8D7I/parser_selfcheck.py` | `1454287f29bf47815e584c7e0f0885e216dd2b47182cff54a45406b69352cda6` |

Intended command from `/Users/brad/dev/ssx3` (not run):

```sh
python3 -u local/research/N8D7I/launch.py --released-sha c842e4c7b92ec01f49566d9cfc88952e174c8f25462972d70ba4a14a5837013c
```

## Fixed inputs and local pin verification

| Field | Predeclared pin | Local check |
| --- | --- | --- |
| APK | `/Users/brad/dev/ssx3-work/N8D7H/app-release.apk`, 153,736,732 B, SHA `86fca856b6de0148aea24fb53b63119e4ec1382eb9cf3490d2ce0db2031df14a` | size matches; two SHA reads match |
| Packaged runner | `8e32841d8a6fff8f45862ca806c74ed92ec31469638f71281f9139e2fc32c683`, Build ID `1c1bce61bfe6bc21cd2ac86d473da323f480eb7b` | two APK-member reads match |
| Packaged Turnip | `717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d` | two APK-member reads match; unchanged from N8D6C |
| Packaged HAL shim | `1b49d27c839f25363237d8276c91a401602845ee8eef67de50d6540f4cdfc387` | two APK-member reads match; unchanged from N8D6C |
| Installed ELF | `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc` | device double-read at run preflight |
| Installed ISO | `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5` | device double-read at run preflight |
| Odin | serial `622c49b1`; lease `/data/local/tmp/mg/LEASE` | not contacted pre-release |
| Run budget | One install, one launch; no second run | enforced by one-run guard |

Pin conflict check vs N8D6C: Turnip, HAL, ELF and ISO are identical to N8D6C's
pinned run; only the APK and packaged runner differ, which is the point of the
new N8D7H package. No conflict.

## Preregistered same-frame gate

All categories require this same tick-2050 frame; anything else is OTHER.

| Requirement | Predeclared value |
| --- | --- |
| Alignment (`[n8d5b]`) | tick 2050, FBP 112, PMODE `0xff21`, 512×448 |
| Selected metadata (`[n8d7f]`) | status 2; valid 512×224; samples 1; promoted 0 |
| Selected vectors (`[n8d7f]`) | input / circuit / stage each 448 tiles |
| Existing stages (`[n8d6a]`) | circuit1 512×224×448, pre_deinterlace_merged 512×224×448, final 512×448×896; controls 128 each |
| Old-final control (`[n8d5b]`) | `control=128 expected=128 PASS` |
| Final vectors (`[n8d5b]`) | sampled and raw 896 tiles each, exact 896/896 equality; each vector consistent with its summary |
| Selected consistency | parses to 448 words each; occupied/active match the logged summary; packed SHA recomputed from the full vector and compared only when the firmware printed a real digest (Android logs `unavailable`) |
| Equality counts | recomputed from parsed vectors and required to equal the logged `input_circuit_equal`/`circuit_stage_equal` (0..448; equality is not forced to 448) |
| Frame | same-run tick-2050 PNG + metadata, 512×448, FBP 112/112, fallback 0, PMODE `0xff21` |
| Errors | no probe/pipeline error, no `[n8d7f] OTHER` line |

These are stage locations, **not** cause or driver verdicts; Mac and Odin GS
streams are not byte-identical. Active means a 16×16 tile with ≥32 qualifying
pixels.

## Category table (predeclared thresholds)

Counts are parsed vector active counts: `input`/`circuit`/`stage` out of 448,
`final` (sampled == raw) out of 896.

| Category | input | circuit | stage | final | Meaning |
| --- | --- | --- | --- | --- | --- |
| A | ≤100 | ≤100 | ≤100 | ≤100 | sparse already at the selected input |
| B | ≥250 | ≤100 | ≤100 | ≤100 | loss introduced by circuit |
| C | ≥250 | ≥250 | ≤100 | ≤100 | loss introduced by the GPU stage |
| D | ≥250 | ≥250 | ≥250 | ≤100 | loss introduced later |
| E | ≥250 | ≥250 | ≥250 | ≥500 | intended sparsity not reproduced |
| OTHER | any other counts, or promotion, sample count ≠1, alignment, missing/malformed data, control failure, error line | | | | |

## Parser self-check

`python3 local/research/N8D7I/parser_selfcheck.py` — **26/26 PASS**, written to
[parser-selfcheck.txt](parser-selfcheck.txt). It covers:

- the saved N8D6C same-PID log: both 896-word vectors decode to 896, occupied
  5,894, active 39, packed SHA `3f06a58a…1ba5`, and sampled == raw;
- the released N8D6C parser still rejects that comma-led continuation (bug
  reproduced);
- a synthetic 448-word `[n8d7f]` vector with a comma-led continuation, plus
  trailing-comma and three-segment variants, all decoding to 448 words;
- rejection of oversized, non-decimal, incomplete and summary-only inputs;
- `packed_sha256=unavailable` and `bytes=…unavailable` accepted (Android);
- unequal vectors classified B (input high, circuit/stage low) and C
  (input/circuit high, stage low), with the equality counts recomputed
  (168/448 and 448/168);
- a summary-only receipt and a corrupt vector classified OTHER.

## Run receipt

Exactly one `--released-sha` run, exit 0. Receipts in this directory:
[result.json](result.json), [driver.log](driver.log), [ps2x.env](ps2x.env),
[tile-excerpt.txt](tile-excerpt.txt), [upload-0.png](upload-0.png),
[upload-0.txt](upload-0.txt).

| Field | Observation |
| --- | --- |
| Script / env SHA | `c842e4c7b92ec01f49566d9cfc88952e174c8f25462972d70ba4a14a5837013c` / `3f8a1f73c75b30dac6e8c755c52270e1c7babc5310b6bf262a5e211e2eb7f549` |
| Preflight before install | state=device, lease `LEASE_FREE N8D6C-ORCH readback done`, keyguard false, battery 100% (`status 5`), free 25,913,323,520 B |
| Preflight before launch | held lease `N8D7I one-launch`, keyguard false, battery 100% (`status 5`), free 25,912,168,448 B |
| Install and input pins | one `adb install -r`: Success; installed APK / ELF / ISO each matched on two device reads; `mc0` empty; unique empty frame dir |
| Flags | parallel backend, Turnip, dev movie bypass, installed ISO, I26-FAST vsync pad route, `PS2X_N8D5_TILE_CAPTURE=1`, `PS2X_N8D7F_SELECTED_CAPTURE=1`, frame dump at tick 2050, vsync-rate log |
| Launch and stop | one launch, PID `10097`; one BACK at 5.3 s; elapsed 114.32 s; final tick 2020; stop `first complete selected and vector receipt with frontend dump`; no second run |
| Alignment | tick 2050, FBP 112, PMODE `ff21`, 512×448 |
| Selected metadata | tick 2050, fbp 112, fbw 8, psm 1, dbx 0, dby 0, phase 0, stride 2, mask 4194303, samples 1, promoted 0, extent/valid 512×224, status 2; `bytes=5177344`; SHA fields `unavailable` (Apple-only) |
| Selected input/circuit/stage | each 448 words, occupied 5333, active 35; recomputed packed SHA `dd42fd963576953cefaedb9b8d5a2ea10c80376b7899027211c1aa1f186097d0`; `input_circuit_equal=448/448`, `circuit_stage_equal=448/448` |
| Existing stages | circuit1 512×224×448 (occ 5333, act 35, control 128); pre_deinterlace_merged same; final 512×448×896 (occ 10636, act 63, control 128) |
| Old-final control and summaries | `control=128 expected=128 PASS`; sampled `896/10636/63`; raw `896/10636/63` |
| Final vectors | sampled == raw; 896 words; recomputed packed SHA `36a8206463c50be2d96ea7aa0ead8d5d3a8b1b5667f62598b37b9bdc87c05551` |
| Frame | seq 0 tick 2050, 512×448, display/source FBP 112/112, fallback 0, `fnv1a=c01b8b4f`, `smode2=0x1`, `pmode=0xff21`; PNG SHA `ee2a6849bc4374786ece4e985daa443802c3c0d1b6843caabac3a60214f36e0a` (two device + two local reads); metadata SHA `806773f1c548421f7774bbab45846c04543b52c5425c28ab5b5202cb843fb127` |
| Probe/pipeline errors | none |
| Category | **A** — input/circuit/stage active 35/35/35 (≤100) and final active 63 (≤100) |
| Cleanup | `am force-stop` completed, PID absent, lease `LEASE_FREE N8D7I done`; closed log gzip 5,601 B in Mac scratch |

The run is a stage-location observation only. It does not declare a cause or a
speed result, and the orchestrator views `upload-0.png` and gates the category.

## Intended device procedure and stop rules

Preflight before install and immediately before launch: serial `622c49b1`
online; lease free; `KeyguardServiceDelegate showing=false`; battery charging
or full and ≥20%; storage ≥1 GiB. If locked, stop and tell the orchestrator so
Brad can unlock. Claim the lease, install even if present, double-read
installed APK/ELF/ISO, require empty `mc0` and a unique empty frame directory.
Set parallel backend, Turnip, dev movie bypass, installed ISO, I26-FAST vsync
pad route, `PS2X_N8D5_TILE_CAPTURE=1`, `PS2X_N8D7F_SELECTED_CAPTURE=1`, one
frame dump at tick 2050, and progress-only vsync log. Capture same-PID logcat
to a 16 MiB cap and send BACK once at ~6 s only for the USB dialog.

Stop at the first complete aligned receipt plus frame; first fatal or process
exit; tick 2100 without a complete receipt; 180 s below tick 1700; or 300 s
wall. Force-stop after this run, verify the PID is gone, and release the lease
even on error. Pull only the tick-2050 PNG/txt with two device and two Mac SHA
reads; compress the closed log in scratch.

## Caps

Mac scratch `<500 MiB`; committed receipts/images `<8 MiB`; global mini ssx3
`<200 GB`. No diagnostic timing is reported as speed.

## Gaps

The frame is committed for the orchestrator's own view; no cause, driver or
speed conclusion is drawn here. The `[n8d7f]` SHA fields are `unavailable` on
Android, so the committed vector SHAs are the launcher's recomputation from the
full parsed vectors, not a device-side digest. The 896-word `[n8d5b]` sampled
and raw vectors and the closed log remain in Mac scratch
(`~/dev/ssx3-work/N8D7I/logcat-all.txt.gz`); only summaries and the full 448-word
`[n8d7f]` vectors are in the committed `tile-excerpt.txt`. No second run, source
or build change, iOS action, upstream contact or push followed the release.
