# N8D7M12 Part 5B — one gated Odin GS-stream replay (COMPLETE)

**State: device run COMPLETE, outcome A (provisional). Exactly one
install and one launch of the reviewed launcher SHA
`287140bf370acfb105f1b64347a635822300699150e517e6b912340ae031334e`.
No retry, no second install/launch, no source/script/APK/stream edit,
no device reboot/unlock, no iOS/fork/push/board action. Text <512 KiB;
PPM/logcat/APK/stream stay outside git in
`~/dev/ssx3-work/N8D7M12P5A/`. No cause is inferred here; no same-binary OFF control was run or claimed; no speed is quoted
(elapsed time is run control only).**

Brief: `local/muse/prompts/N8D7M12P5B.md`. Released command, from
`/Users/brad/dev/ssx3`:

```sh
python3 -u local/research/N8D7M12P5A/launch.py --released-sha 287140bf370acfb105f1b64347a635822300699150e517e6b912340ae031334e
```

Coordination: start was held for the E55D14P1B Mac build/link, then
explicitly released; no sibling Mac build/boot was active. Pre-run:
SHA recomputed = reviewed pin, P5A `check.py --self-check` 24/24 A,
private `result.json`/`driver.log` absent, scratch sentinel OK.

## 1. Pins and hashes (all pairs exact)

| Item | SHA-256 (both reads) | Size |
| --- | --- | --- |
| Launcher `launch.py` | `287140bf370acfb105f1b64347a635822300699150e517e6b912340ae031334e` | — |
| Local APK | `caa1110297dc413d3b04e7442873e0fb5d5624af8417e1e30537d76184d5f512` ×2 | 153,753,116 B |
| Packaged runner | `329e44db7133a7f56c7978fd9594189e7ff595e2834d9755fa80efe46a218a3d` ×2 | — |
| Packaged Turnip | `717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d` ×2 | — |
| Packaged HAL shim | `1b49d27c839f25363237d8276c91a401602845ee8eef67de50d6540f4cdfc387` ×2 | — |
| Local stream | `f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593` ×2 | 1,100,696,462 B |
| Installed APK (device) | `caa1110297dc413d3b04e7442873e0fb5d5624af8417e1e30537d76184d5f512` ×2 | — |
| Device stream (verify only) | `f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593` ×2 | 1,100,696,462 B |
| Pulled `vq-002050.ppm` (2 device + 2 local) | `39b70d677651f08d702c7e0460a71dff8905aad639797b1b5b23540025350d41` ×4 | 688,143 B |
| Pulled `parallel.hashes` (2 device + 2 local) | `0e89a493764096ade2c2cc94cdb610c5a0fbf643378e5cffb98cf02a68f2c82a` ×4 | 2,686 B |
| Preserved `ps2x.env` (2 device + 2 local, restored 2+2) | `176eff84eaf8e4f55800362f4827744b5f777ca0e3cbd623d271d4cd97cef32d` | — |
| Replay `ps2x.env` pushed | `a41b9b280e1ff2c4450550377d2887606ec57be710d293e04c8394bb60eb13bf` | — |

Installed path:
`/data/app/~~z5QOVmHsdGcm72F_s7HSqg==/com.ps2x.runner-K0u2aSyF83mZAJYZA6Jphw==/base.apk`.
PPM dir / hashes path:
`.../files/n8d7m12p5a-frames-1790276646`,
`.../files/n8d7m12p5a-1790276646.hashes`.

## 2. Run control (one install, one launch)

| Field | Observation |
| --- | --- |
| Preflight (before install) | device, lease `LEASE_FREE N8D7M12P4 done`, keyguard=false, 100% status 5, 24,795,971,584 B free |
| Lease | `N8D7M12P5A replay` claimed, re-read persists; released `LEASE_FREE N8D7M12P5A done` (tag ours) |
| Install | one `adb install -r`, Success |
| Pre-start preflight | device, lease ours, keyguard=false, 100% status 5, 24,795,193,344 B free; PID absent |
| Launch | one `am start`, PID 1822; BACK once ~6 s |
| Stop | `first complete tick2050 summary/census/frame (PROVISIONAL)`, elapsed 13.336 s (control only) |
| Progress | 41 `GB4_REPLAY` rows; no error row; no drain path taken |
| Caps | logcat gzip 3,127 B (≤16 MiB); PPM+hashes 690,829 B (≤64 MiB) |
| Postrun | `am force-stop`, PID absent |
| Env restore | pushed file removed-equivalent: pre-existing bytes restored, 2+2 reads match |
| `first_failure` | `not found`; no `cleanup_errors` |

## 3. Replay markers

| Marker | Value |
| --- | --- |
| `GB4_REPLAY_SUMMARY` | mode=queue backend=parallel packets=862958 priv=11499 transfers=25445 markers=2050 |
| `GB4_FRAME` | tick=2050 backend=parallel pmode=ff21 present=b167a719 |
| `[n8d7m12] replay ok` | packets=862958 markers=2050 |
| Error rows | none |

## 4. Numeric census (tick 2050)

| Census | Value |
| --- | --- |
| Alignment | tick=2050 fbp=112 pmode=ff21 512×448 |
| Control | `control=128 expected=128 PASS` |
| Sampled summary | tiles=896 occupied=5117 active=24 |
| Raw summary | tiles=896 occupied=5117 active=24 (values == sampled) |
| Stages | circuit1 512×224 tiles=448 occupied=2660 active=14 control=128; pre_deinterlace_merged same; final 512×448 tiles=896 occupied=5117 active=24 control=128 |
| Selected metadata | tick=2050 fbp=112 fbw=8 psm=1 dbx=0 dby=0 phase=0 stride=2 mask=4194303 samples=1 promoted=0 extent=512×224 valid=512×224 status=2 |
| Selected bytes | 5177344 (vram/input/circuit SHAs `unavailable` on-device) |
| Selected input/circuit/stage/oracle | each 448 tiles, occupied=2660, active=14, packed SHA `3c69b421c6469a6c4058a4ebe91b18d77da2d4e3644831e641c5bed6b0b4e8c5` identical all four |
| Equality (logged) | input_circuit_equal=448/448 circuit_stage_equal=448/448 oracle_input_equal=448/448 |
| Oracle metadata | 11 shared fields byte-equal to selected |
| Oracle controls (kOracleControls order) | `0x0E0000=0x00060000`, `0x0E0534=0x000C0000`, `0x0E0040=0x000C0000`, `0x1BFFF4=0x00000000`, `0x0E2000=0x00000000`, `0x0F0000=0xFF000000`, `0x0E1FFC=0x00000000`, `0x0F2000=0x00000000` |
| Sampled/raw vectors | 896 words, occupied=5117, active=24, SHA `1feafa32eb531269c129722320cd32a3294d02b9e7a1b031e6e37b514fe356aa` identical |

Descriptor row (11 shared selected fields):
`tick=2050 fbp=112 fbw=8 psm=1 dbx=0 dby=0 phase=0 stride=2 mask=4194303
samples=1 promoted=0`.

## 5. Outcome table

| Condition | Outcome | Next action |
| --- | --- | --- |
| Complete on-device replay receipt + intact cleanup | **A (this report), PROVISIONAL PASS — provisional until the orchestrator views `vq-002050.ppm`** | Orchestrator frame view + same-binary controls |
| One runtime mismatch with exact first failing row | B (not this run) | — |
| Preflight/permission/resource failure | OTHER (not this run) | — |

## 6. Gaps

- Frame content is unviewed by this worker; A stays provisional until
  the orchestrator views `vq-002050.ppm` (SHA above, 688,143 B).
- On-device 4 MiB `vram/input/circuit_sha256` are `unavailable`; the
  448-tile packed SHAs (all four identical) carry the census instead.
- One ON replay only: no default-off behavior, no determinism claim,
  no graphics cause, no speed number.
- Device stream history after N8D7M6 remains untraced; only current
  exact bytes are gated (two device SHAs here).

## 7. Receipts

- ssx3 (this dir, committed text only): `REPORT.md`, `check.py`,
  `check-result.json`.
- Private scratch (outside git): `result.json`, `driver.log`,
  `logcat-all.txt.gz`, `logcat-pid.txt`, `vq-002050.ppm`,
  `parallel.hashes`, `ps2x.env`, `ps2x.env.before`.
- Commit `[N8D7M12] Part 5B` with `Orchestrated-By: opencode`, explicit
  paths only, no push.
