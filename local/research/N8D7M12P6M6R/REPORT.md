# N8D7M12 Part 6M6R — pinned package resume on SSH-capable worker (STOPPED: staged fork lacks gradlew)

Worker receipt. Brief: `local/muse/prompts/N8D7M12P6M6R.md` (incorporates
`local/muse/prompts/N8D7M12P6M6.md`). Owns only
`local/research/N8D7M12P6M6R/` text scripts/receipts. No source/fork/
renderer/collector edit, no Odin/emulator action, no game bytes or binaries
in git, no upstream contact, no subagents, no push. Time box 45 min (used
~25 min; stopped on first failure per brief). SSH to `bytesize` worked on
this route; the prior P6M6 stop receipt was not reused as evidence.

Goal (not achieved — blocked): one arm64 APK from exact P6M5 staged bytes
with a reviewable source→native→APK link.

## 1. Stop reason: staged fork has no Gradle wrapper; zero builds attempted

The single `./gradlew assembleRelease` could not start: the staged fork
contains no `android/gradlew` script and no `android/gradle/wrapper/
gradle-wrapper.jar`. The failure fired in the toolchain-version prologue,
before any build:

```
./gradlew: No such file or directory   (build.txt; RC=127; no BUILD line)
```

Cause chain (all read-only, independently re-checked here):

- Fork HEAD `4fa0df1811df4381aa3ba95aa3fcd1310afd1d25` tracks exactly one
  wrapper path: `android/gradle/wrapper/gradle-wrapper.properties`
  (250 B, pins `gradle-8.9-bin`). `git log -- android/gradlew` is empty:
  the wrapper script was **never tracked** in the fork.
- P6M5 staged the fork via `git archive HEAD`, so the stage faithfully
  holds fork HEAD — and faithfully lacks `gradlew`/wrapper jar. The P6M5
  manifest records only the `.properties` file in fork scope.
- The N8D7M1/P3 WSL roots carried both files out-of-band (read-only
  single-read reference, WSL):
  - `android/gradlew` 8,762 B
    `a3648413b47ef77af21d5ebc36c687c7d103aaef3e17f33de7d4f080a6f300a3`
  - `android/gradle/wrapper/gradle-wrapper.jar` 43,504 B
    `498495120a03b9a6ab5d155f5de3c8f0d986a449153702fb80fc80e134484f17`
  - N8D7M1 wrapper `.properties` is byte-equal to the staged one
    (`WRAPPER_PROPS_EQUAL`); the `gradle-8.9-bin` distribution is already
    cached in shared `/home/brad/n2/gradle-home/wrapper/dists/`. No system
    `gradle` exists on WSL PATH.
- Copying those two files into the WSL root would inject unpinned bytes
  outside the staged manifest and break the brief's "exact P6M5 staged
  bytes" model, so per the no-repair-loop stop rule no workaround was
  tried. **Zero `assembleRelease` attempts; the one-build budget is
  unspent but this brief ends.**

## 2. Evidence table

| Item | Value | Status |
| --- | --- | --- |
| P6M5 checker re-run (`check.py`) | 24 rows, 0 failing, verdict A | pass (`preflight-p6m5-check.txt`) |
| P6M5 manifest aggregate (Mac) | `6877de873b197bf915d068d1b03331e6488c529e6bdac64273513f338080316a` | match |
| P6M5 counts | 26,211 files / 612,576,408 B | within 30,000 / 2,000,000,000 caps |
| Mini project disk before/after | 157.5 GB of 200 GB cap, RC=0 both ends, 87 Gi free | pass |
| SSH `bytesize` | `SSH_OK`, user `brad` | pass (this route authorized) |
| WSL root `/home/brad/n8d7m12p6m6` pre-transfer | absent | pass (`preflight.txt`) |
| WSL toolchain/governor | jdk-17, android-sdk, ndk 28.2.13676358, gradle-home, mem_governor.sh all present | pass |
| WSL free disk | 749 G on /dev/sdc | ≥20 GiB pass |
| WSL heavy jobs | `HEAVY_JOBS []` | pass (one-heavy-job rule) |
| Transfer | tar stream of 4 staged dirs + `source-manifest.json` + `source_manifest.py`; STREAM_BYTES=669184000 | pass (`transfer.sh`, `transfer.txt`, `transfer-bytes.txt`) |
| WSL root post-transfer | 6 top-level entries, 619,387,661 B | pass |
| WSL collector `verify` pre-build | `status=match`, expected=actual=`6877de87…80316a`, added/missing/changed all empty | pass (`source-verify-pre.json`) |
| WSL runner dir | sole `register_functions.cpp`, 438 B, `cf62c485…87f068` | pass (stub-only) |
| `assembleRelease` | not attempted (no `gradlew` in staged bytes) | STOP |
| Post-build verify / compiled-input list | not reached | open |
| APK SHA / member SHAs / Build ID / strings / flags | not reached (no APK built) | open |
| Mac APK scratch `~/dev/ssx3-work/N8D7M12P6M6/` | empty, 0 B | no APK transferred |
| Receipt dir | 64 KiB | ≤512 KiB pass |

Full SHAs: aggregate
`6877de873b197bf915d068d1b03331e6488c529e6bdac64273513f338080316a`;
runner stub
`cf62c485072f07c230e60296b77afd733f130f587955fe608322939ebb87f068`;
reference (single-read) N8D7M1 `gradlew`
`a3648413b47ef77af21d5ebc36c687c7d103aaef3e17f33de7d4f080a6f300a3`,
wrapper jar
`498495120a03b9a6ab5d155f5de3c8f0d986a449153702fb80fc80e134484f17`.
Versions captured before the stop: Temurin JDK 17.0.20.1+1, NDK r28c
(28.2.13676358), CMake 3.22.1, build-tools 34.0.0, platforms android-34
(`build.txt`).

## 3. Exact commands

```sh
python3 local/research/N8D7M12P6M5/check.py   # 24/24 A (preflight-p6m5-check.txt)
bash local/tooling/disk_budget.sh             # 157.5/200 GB (disk-budget-before/after.txt)
ssh bytesize 'wsl -d Ubuntu -- bash -lc "echo SSH_OK; ..."'   # SSH + root-absent check
ssh bytesize 'wsl -d Ubuntu -- bash -s' < local/research/N8D7M12P6M6R/preflight.sh > .../preflight.txt 2>&1
bash local/research/N8D7M12P6M6R/transfer.sh > .../transfer.txt 2> .../transfer-bytes.txt
ssh bytesize 'wsl -d Ubuntu -- bash -s' < local/research/N8D7M12P6M6R/source_verify.sh > .../source-verify-pre.json 2> .../source-verify-pre.err
ssh bytesize 'wsl -d Ubuntu -- bash -s' < local/research/N8D7M12P6M6R/build.sh > .../build.txt 2>&1   # RC=127, gradlew absent
python3 local/research/N8D7M12P6M6R/check.py  # 8 rows pass, verdict C (stop)
```

Transfer stderr note: remote GNU tar printed 28,049 benign `Ignoring
unknown extended header keyword 'LIBARCHIVE.xattr.com.apple.provenance'`
lines (macOS bsdtar xattrs ignored on extract); condensed to a 517 B
summary in `transfer-bytes.txt`. Content integrity rests on the collector
`verify: match`, not on that stderr.

## 4. Source→member→APK graph (as far as reached)

```
[P6M5 stage: PS2Recomp 323 + parallel-gs 16,429 + codegen-ssx3 9,457 + jniLibs 2]
  == tar 669,184,000 B over ssh ==▶ [/home/brad/n8d7m12p6m6 same four roots]
  == collector verify: match, aggregate 6877de87…80316a ==▶ (inputs pinned)
  ── BLOCKED: no android/gradlew + wrapper jar in staged bytes ──
  (ps2_game_objects / parallel-gs STATIC / libps2EntryRunner.so / APK: not reached)
```

## 5. Gaps (hand-back, no package/GPU verdict)

1. The staged fork cannot build: `android/gradlew` + `gradle-wrapper.jar`
   are build-required inputs that live only in the N8D7M1/P3 WSL roots,
   never in the fork. Their historical bytes are named above (single
   read, reference only).
2. All post-build facts are open: no build log, no CMakeCache, no
   `PS2X_GAME_SOURCE_COUNT`, no compiled-input file list, no native
   member SHAs/Build ID, no APK SHA.
3. The WSL root `/home/brad/n8d7m12p6m6` is left in place with verified
   pre-build bytes only (619 MB; no build outputs, no APK). The next
   brief either reuses it after pinning the wrapper files or recreates a
   fresh root; it must not be written by any other lane meanwhile.
4. Transfer xattr-warning stderr was condensed (see §3); full text was
   benign and is not retained.

## 6. Recommended next action

Stage the two wrapper files as pinned build inputs (double-read their
SHAs at staging time; decide whether they join the source manifest as a
new scope, the JNI-style scope, or a separately pinned toolchain pair),
then re-issue the one-build package brief against the extended manifest.
The `gradle-8.9` distribution cache and wrapper `.properties` already
agree, so no other input is known-missing — but the next worker should
still preflight-execute `./gradlew --version` from the staged tree before
counting its one build. No Mac-side retry or repair is needed.

## 7. Receipts

- `local/research/N8D7M12P6M6R/{REPORT.md,check.py,check-result.json}`
  (committed with `git add -f`, `[N8D7M12] Part 6M6R` /
  `Orchestrated-By: Muse Code`; no push).
- Scripts: `preflight.sh`, `transfer.sh`, `count_bytes.py`,
  `source_verify.sh`, `build.sh` (this dir).
- Outputs: `preflight-p6m5-check.txt`, `disk-budget-before/after.txt`,
  `preflight.txt`, `transfer.txt`, `transfer-bytes.txt`,
  `transfer-tar.err` (empty), `source-verify-pre.json`,
  `source-verify-pre.err` (empty), `build.txt`.
- Base commit `15027e8e` (`[orch] Gate SSH policy stop and reroute
  Android package`).
- No APK, no binary, no game bytes in git; no device, lease, or upstream
  action.
