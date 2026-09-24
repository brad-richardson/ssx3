# N8D7M12 Part 4 — exact stream staging and Odin preflight (no launch)

Worker receipt. **No app run/install, no `ps2x.env` write, no
reboot/unlock, no iOS, no push, no source/fork/stream/APK edit, no
device-file delete, no upstream contact.** Zero `adb push` calls (remote
stream already exact, reused). Local text 40 KiB (<512 KiB).

Brief: `local/muse/prompts/N8D7M12P4.md`. Pins: stream
`f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593`
(1,100,696,462 B); APK
`caa1110297dc413d3b04e7442873e0fb5d5624af8417e1e30537d76184d5f512`
(153,753,116 B). FILES path
`/storage/emulated/0/Android/data/com.ps2x.runner/files/n8d7m6.gs`.
Serial `622c49b1` from `local/odin-serial`. Every adb used `-s`.

## 1. Acceptance table

| Check | Result |
| --- | --- |
| Local stream 2 matching SHA + size | PASS `f6a78f71…a593` ×2, 1,100,696,462 B |
| Local APK 2 matching SHA + size | PASS `caa11102…f512` ×2, 153,753,116 B |
| Preflight (device/keyguard/battery/space/app) | PASS device, keyguard=false, 100% status 5, 24,805,888,000 B free, app stopped |
| Device stream (reuse match, no push) | PASS 2 device SHAs `f6a78f71…a593`, size 1,100,696,462 B |
| Lease released, app stopped at end | PASS `LEASE_FREE N8D7M12P4 done`, pid empty |
| Verdict (A/B/OTHER) | **A** |

A = exact inputs + device stream verified, lease released, app stopped.
A proves **no** runtime behavior, default-off control, graphics cause or
speed. The orchestrator gates any install/replay.

## 2. SHA/size pairs

| Input | SHA read 1 | SHA read 2 | Size | Pin match |
| --- | --- | --- | --- | --- |
| Stream local `~/dev/ssx3-work/N8D7M6/n8d7m6.gs` | `f6a78f71…a593` | `f6a78f71…a593` | 1,100,696,462 | yes |
| APK local `~/dev/ssx3-work/N8D7M12P3/app-release.apk` | `caa11102…f512` | `caa11102…f512` | 153,753,116 | yes |
| Stream device (FILES `n8d7m6.gs`) | `f6a78f71…a593` | `f6a78f71…a593` | 1,100,696,462 | yes |

Full hashes in `result.json`.

## 3. Device/lease state

| Item | Value |
| --- | --- |
| `adb devices` | `622c49b1 device` (`adb-devices.txt`) |
| Lease before | `LEASE_FREE N8D7M6 done` (free, no other Odin worker) |
| Lease tag | `N8D7M12P4 staging 1790275764` (claim verified by re-read) |
| Lease after | `LEASE_FREE N8D7M12P4 done` (released in `finally`, tag matched) |
| Keyguard | `showing=false` (no lockscreen; no launch in this part regardless) |
| Battery | 100%, status 5 (full, charging-class; ≥20% gate met) |
| `df` free | 24,805,888,000 B (~23.1 GiB ≥ 10 GiB) |
| App PID preflight/end | empty / empty (never launched) |
| Pushes | 0 (remote present with exact size+SHA, reused per brief) |

## 4. Exact commands

```sh
python3 local/research/N8D7M12P4/stage.py   # pins, claim, preflight, verify/reuse, release
python3 local/research/N8D7M12P4/check.py   # 8/8 pin/lease/result agreement
```

`stage.py` flow: two local SHA reads each input → `adb devices` →
read lease (free) → claim unique tag + re-read → preflight reads
(window policy, battery, df, pidof, remote stat) → remote
present+size-match → two device `sha256sum` reads → match → reuse
(absent would take exactly one `adb push` + size + two device SHAs;
mismatch would record B with both hashes and stop, no overwrite) →
end pidof → verdict → `finally` releases lease only if tag still ours.

## 5. Gaps

- The device stream is the pre-existing FILES copy (N8D7M6's on-device
  capture source); its history after N8D7M6 is not traced here — only
  its current exact bytes are pinned (two device reads).
- No APK hash was taken on-device (no install per brief); the next gate
  must verify the installed APK before replay.
- `dumpsys window policy` keyguard parse used the
  `KeyguardServiceDelegate showing=` row (N8D7M6 `launch.py` pattern).

## 6. Receipts

`REPORT.md`, `stage.py`, `check.py`, `check-result.json` (8/8 PASS),
`result.json`, `adb-devices.txt`, `adb-battery.txt`,
`adb-window-policy.txt`, `adb-df.txt`. No logcat (no launch).
