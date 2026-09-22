# I24 — V3-vector probe: retained title 5,040 B on host-7.1.1 AND device (P4 close)

- Date: 2026-09-22. Tables, no verdicts.
- `local/research/I23/REPORT.md` read first (all of it: shape-A integration, branch `i23-ffmpeg-ios`, H2 request text, P1–P10 table with P4's V3 precondition outstanding; P2b/P9b/P5/P7 standing).
- `local/research/E24/REPORT.md` §Objective 3 + §picture finding read (all of it: dims provenance 512×448 MPEG-2 MP@ML 4:2:0 29.97, 35-code / 28-slice census, tail 5024+15, NO terminator) + `dims.json` + `picture-completeness.json` + `payload-tail.json` + `observed-vector.json` + `NEXT-BRIEF.md` (E24-E1, WARNING, sharpened X) read in full. E24-E3 carried: FOUR 177s (vpos 1,2,4,5), slice28 191 raw / 176 to-last-nonzero — correcting E24 REPORT prose ("two are 177 B"); the committed `picture-completeness.json` already shows four.
- `local/research/I22/REPORT.md` §sufficiency read (all of it: host probe recipe — verbatim `i22-decode.c` + existing-prefix link).
- Target: Brad's iPad, iPad Air 11-inch (M2) (`iPad14,9`), UDID `P` — pre-state = I23's install (UUID `C163D3F5-…`) present AND running (PID 4790, 9th brief with a relaunched occupant); untouched until the authorized overwrite-install.
- BASE: `3adc0478` (fork `ssx3` at recon AND end; E-lane advanced 0 during I24; branch `i23-ffmpeg-ios` @`aa73dbc` both ends).
- Product: V3 vector lock (3 retained copies identical) + host-7.1.1 V3 anchor (EXISTING prefix, no rebuild: verbatim harness 5× + split-phase harness 3×) + device V3 probe (I23 final build reused byte-identical, NO rebuild, V3 via the C3 `PS2X_MPEG_VECTOR_PATH` diagnostic) + P4 structural-identity table (every row exact) + cheap P2b/P9b/P5/P7 re-check (unchanged standing).
- Rules honored: ZERO fork commits (no code changes → no `i24-v3-vector` branch needed; `fork/ssx3` unmoved); E-lane pane never prompted/steered; rebuild/reinstall/probe AUTHORIZED, used reinstall+probe only; no PS2 boots → no lease; no `adb`; every device-scoped `devicectl` with explicit `--timeout`; `export COPYFILE_DISABLE=1` on SSD steps + `._*` purges; byte caps declared up front + tracked (NEW `ps2x-i24/` paths only; `ps2x-i23/` byte-untouched at 9.6G); evidence `local/research/I24/` standalone, `[I24]` commit, no push.
- Outcome shape: V3 SERVES on both sides — feed holds (`parsed=5040 packets=0 newFrames=0`, the E-lane record reproduced exactly) and the parser-flush drain serves ONE 512×448 frame (host 8/8 runs, device 1/1 probe, RGBA `048b41af…` byte-identical both sides). P4's structural-identity bar meets on every row; the title-path live hold (main still parked, 0 guest frames) is unchanged — the remaining wall is the guest stopping one start code short (E24's sharpened X), not the decoder.

Path shorthands: `W` = `/Volumes/Extreme SSD/ps2x-i23/` (read-only reuse), `N` = `/Volumes/Extreme SSD/ps2x-i24/` (NEW scratch), `P` = iPad UDID `00008112-001224302184A01E`, `FORK` = shared clone (read-only: `ls-remote`/`log`/`status` only), `V3` = `local/research/E24/observed/parser-input.bin` (5040 B).

## Experiment contract

| Item | Content |
|---|---|
| Hypothesis H | The retained 5040 B V3 vector decodes with STRUCTURAL identity on host-7.1.1 (existing prefix) and the I23 device build: same feed counts, same flush counts, same frame dims, byte-identical RGBA (if frames), same stall-or-serve shape — closing P4 |
| Observable | Vector-lock table (3-copy sha/FNV/size + first4 + dims re-parse + slice census); host runs (counts + RGBA digests + phase split); device console (vector lines + feed-traces + retrieved RGBA + cmp); P4 row-by-row table; cheap P2b/P9b/P5/P7 rows |
| Alternatives | H-a exact structural identity on every row (observed). H-b device-only deviation (re-opens Cause-B — tabled with both sides, no smoothing). H-c contested vector (any lock mismatch → table + stop, no probes) |
| Stop | All bars tabled, or any cap (6 h / SSD / evidence / /tmp), or any FORK/E-lane conflict (none encountered). Contract outcome: H-a on every row |
| Time box | 6 h (used ~12 min wall: recon+lock ~2 min → host ~2 min → stage/sign/install/probe ~5 min → analysis/evidence/report/commit ~3 min) |
| V3 precondition | I23 P4's bar precondition (V3 capture + title dims) satisfied by E24: dims 512×448 + retained 5040 B spec; verified before use per the brief (Mission 1), not assumed |

## Caps (declared up front, tracked)

| Cap | Declared | Used | Receipt |
|---|---|---|---|
| `N` SSD allocated bytes (ExFAT) | ≤ 5 GB (brief suggested ≤2 GB; the single ISO stage alone is 2.9 GB allocated — cause recorded, declared before staging) | 2.9 GB (58%) — signed-app 2.9G (ISO 3.0G logical) + logs 20M (console 17M + 2 RGBA bins) | `du -sh N` at end |
| `/tmp` transient (APFS) | ≤ 500 MB | 11M (2 probes + scripts + 9 RGBA bins; kept, transient) | `du -sh` at end |
| Evidence `local/research/I24/` | ≤ 5 MB | 104 KB logs + REPORT, 15 files + REPORT | `du -sh` + file count |
| Screenshots committed | 0 (not needed for structural identity) | 0 | — |
| Build parallelism | `-j2` max | No builds (prefix + binary both reused; 2 `clang` single-file links) | §Task 1 |
| Fork writes | zero commits (cut `i24-v3-vector` only if code changes needed) | 0 commits, 0 pushes, no new branch (none needed); remote `ssx3` at `3adc0478` recon AND end | §Task 2 + end pin |
| Device ops | reinstall + probes (AUTHORIZED) | 1 install (exit 0, 13th overwrite) + 1 probe (V3 PID 5108, exit 2 alive, cleaned) + 1 RGBA retrieval + 1 crashlog check | §Task 2 |
| Host runs | decode probes ONLY (no PS2 boots, no repo builds) | 0 PS2 boots, 0 repo builds, 0 prefix rebuilds; 8 V3 runs (5 verbatim + 3 split) | §Task 1 |
| E-lane contact | read-only inspection, never prompt/steer | Clone: `ls-remote`/`log`/`status` only; worktree `MPEG.cpp` read-only (feed/flush/diagnostic shapes); pane untouched | §Task 1–2 |
| Elsewhere growth | 0 (`ps2x-i23/` untouched) | `W` 9.6G before AND after (reads only; no purges/changes there) | `du -sh W` |

## Task 1 — Vector lock + host V3 anchor (no device)

### Vector lock (Mission 1 — all three copies verified before use)

| Row | E22 copy | E23 copy | E24 copy | Standing |
|---|---|---|---|---|
| Size | 5040 B | 5040 B | 5040 B | EQUAL |
| SHA256 | `cde8a830…2a1c875a` | same | same | EQUAL (full: `cde8a830265592be927d28ec78c26a27567ce046a7ac161698759e742a1c875a`) |
| FNV64 | `0xd2a9588f0e0fd358` | same | same | EQUAL |
| first4 | `000001b3` | same | same | EQUAL |
| Byte-identity | `E22==E23: True  E22==E24: True` | — | — | LOCKED (`logs/vector-lock.txt`) |

| Re-parse row (independent, `vlock.py`) | Value | vs E24 spec |
|---|---|---|
| Dims from sequence header | 512×448 (aspect 1, ratecode 4) | EXACT (`dims.json` dims + aspect + ratecode) |
| Start-code census | 35 total: b3×1 b5×3 b2×1 b8×1 pic×1 slices×28 | EXACT |
| Slice vpos | 1..28 contiguous | EXACT |
| 177 B slices | FOUR (vpos 1,2,4,5) | EXACT per E24-E3 carry (E24 REPORT prose "two" NOT reproduced) |
| Slice 28 | 191 raw / 176 to-last-nonzero | EXACT per E24-E3 carry |
| Last nonzero / stuffing | 5024 / 15 zero bytes | EXACT (`payload-tail.json`) |
| Terminating start code | 0 codes after final slice header | ABSENT (E24 deficit confirmed) |

No mismatch → probes authorized (brief's stop clause not triggered).

### Host V3 anchor (Mission 2 — EXISTING `W/host-7.1.1/`, zero prefix rebuild)

| Item | Receipt |
|---|---|
| Prefix reuse | `libavcodec.a` 682,168 B `c2193235…` + `libavutil.a` 935,176 B `369c7241…` + `libswscale.a` 875,320 B `d720f9ef…` (mtimes Sep 21 19:33, untouched; no configure/make/distclean run) |
| Verbatim harness | `i22-decode.c` copied → `diff` clean (VERBATIM — the source is size-generic over argv, so the "adaptation" is vacuous); `clang -arch arm64` + 3 archives + CF/CV/VTB: exit 0 |
| V3 runs 1–5 | exit 0 ×5, `in=5040 parsed=5040 packets=1 frames=1 rgba=917504` identical (`logs/decode-v3-host.log`); per-frame line: `frame0 512x448 fmt=0 (drain)` — the ONLY frame arrives via the drain, never in-loop |
| V3 RGBA digest | `len=917504 fnv64=c1fdca14f69b2325 sha256=048b41af…` (`logs/v3-rgba-host-fnv.txt`); first64/last64 = `fd4900ff` ×16; uniform orange R=253 G=73 B=0 A=255; nonzero 688128/917504; 4 distinct bytes; run1==run2..5 `cmp` clean |
| swscaler notice | `[swscaler] No accelerated colorspace conversion found from yuv420p to rgba` on harness stderr ×8 (cosmetic; I23's V1/V4 logs captured stdout only — that is why it never appeared there) |
| SIGSEGV re-observe | 0/8 (I22's 1/7 harness fault still unreproduced across I23 8× + I24 8× = 16 consecutive clean runs) |

### Split-phase harness (feed-vs-flush attribution, mirrors `MpegFfmpegDecoder`)

`logs/i24-decode-split.c` (new, committed): same call shapes as the worktree `MPEG.cpp` `:106-187` feed (whole-remaining parse chunks, NOPTS, EAGAIN retry in sendPacket) + `:189-227` flush (parser NULL-flush → send → codec NULL-send → drain), `SWS_BILINEAR` to RGBA. Compile exit 0, same recipe.

| Split run (×3 identical) | Receipt |
|---|---|
| `[feed]` | `inSize=5040 parsed=5040 packets=0 newFrames=0 totalFrames=0 ok=1` — the E-lane title hold reproduced EXACTLY at feed phase (`logs/decode-v3-split-host.log`) |
| `[flush]` | `packets=1 newFrames=1 totalFrames=1 ok=1`, `frame0 512x448 fmt=0 (flush-drain)` — the drain serves the complete picture with NO appended bytes |
| Totals + bytes | `parsed=5040 packets=1 frames=1 rgba=917504`, sha `048b41af…`; verbatim==split `cmp` clean ×3 |
| Anchors kept | `N/logs/v3-rgba-host-7.1.1.bin` (917,504 B, `048b41af…`) on SSD; digests committed (`logs/v3-rgba-host-fnv.txt`, `logs/v3-input-fnv.txt`) |

Reference shape for the device: **feed-hold + drain-serve** (0 in-loop, 1 via flush, 512×448, `048b41af…`).

## Task 2 — Device V3 probe (reuse + install + run + retrieve)

### Reuse check (Mission 3 gate — byte-identical → NO rebuild)

| Item | Receipt |
|---|---|
| Final binary re-sha | `W/ios-runtime-device/.../ps2EntryRunner`: 122,458,696 B / sha `edb3eadc…` — BYTE-IDENTICAL to I23 (`e3ff9d03…0c60c1` full in §commands) |
| Game-objects lib re-sha | `libps2_game_objects.a` sha `f356aaa7…` — BYTE-IDENTICAL to I17/I18/I21/I23 |
| iOS prefix (reference) | `libavcodec.a` `3b870c96…` + `libavutil.a` `f178bce2…` + `libswscale.a` `8da0523e…` (677,728 / 926,952 / 895,632 B, mtimes Sep 21 19:32, untouched) |
| Disposition | NO rebuild, NO reconfigure, NO new branch, ZERO fork commits; worktree @`193451a` read-only (`MPEG.cpp` C3 diagnostic `:476-601` + feed `:106-187` + flush `:189-227` shapes read to predict the console) |
| Signed-app delta note | `W/signed-app/.../ps2EntryRunner` is 122,717,056 B `0a00e4d3…` — differs from the build-tree binary ONLY by the I23 codesignature (signing embeds +258,360 B; expected, not a content delta) |

### Stage + sign + install (NEW `N/signed-app/`, I23 mechanism)

| Step | Receipt |
|---|---|
| Stage | `cp -R` build-tree `.app` (byte-identical binary) + ELF + ISO + `embedded.mobileprovision` (all from the I23 staged set) + `i24-v3.m2v` (= E24 `parser-input.bin` bytes); sidecars 0 after purge. NEW vs I23 bundle: V3 replaces V1+V4 (V3-only bundle) |
| Bytes | ELF `1b49d05c…` (identical), ISO 3005415424 B `3c2f8eb1…` (identical), V3 `cde8a830…` (as locked §Task 1), pre-sign binary `edb3eadc…` (identical) |
| Profile/identity/entitlements | Same wildcard profile `f0793278-…` (copied), same identity `295EFB42E6734599…` (Apple Development: Brad Richardson), entitlements = I21 file (valid XML plist, I17==I21 byte-identical, keys match the `codesign -d` extract of the I23 app exactly). Method note: `codesign -d --entitlements <file>` emits human-readable `[Dict]` debug text, NOT a plist (`plutil` rejects it) — hence the I21 file reuse |
| Sign | `codesign --force --sign FP --timestamp=none --entitlements` exit 0, `codesign --verify --strict` exit 0; post-sign binary 122,717,056 B sha `02a6a2c2…` (SAME size as I23's signed binary; sha differs by the CMS signing-time attribute, which `--timestamp=none` does not suppress) |
| Install (OVERWRITE) | Pre: PID 4790 (I23 UUID `C163D3F5-…`, relaunched occupant). Plain install exit 0 in 68.4s, clean replace → new UUID `F05E490A-…`; live occupant reaped BY the install (0 `ps2` after). **Thirteenth clean overwrite** (`logs/install.log`) |

### Probe — V3 vector (`PS2X_MPEG_VECTOR_PATH` + `PS2X_MPEG_FEED_TRACE`, 90 s)

| Item | Receipt |
|---|---|
| Shape | I23 env + V3 path; `--console --timeout 90 --terminate-existing` → exit 2 (alive, PID 5108), 45611 lines / sha `1806a480…` (`N/logs/launch-v3-console.log` full on SSD; evidence: vector-extract + frame + thread-block0 + sizes) |
| **V3 on device (lines 15160–15166)** | `path=…/i24-v3.m2v inSize=5040 inputFnv64=d2a9588f0e0fd358` (input = locked V3, FNV exact) → `[MPEG:feed-trace] inSize=5040 parsed=5040 packets=0 newFrames=0 totalFrames=0` (feed HOLDS — the E-lane record, field-exact) → `feed: ok=1 newFrames=0` → `flush: ok=1 newFrames=1 totalFrames=1` (the drain SERVES) → `frame0 512x448 rgba=917504` → `rgba=917504 fnv64=c1fdca14f69b2325 first64/last64=fd4900ff×16` (FNV + slices exact vs host) → `wrote=…/tmp//i23-vector-rgba.bin bytes=917504` |
| **Title on device (line 15167)** | `[MPEG:feed-trace] inSize=5040 parsed=5040 packets=0 newFrames=0 totalFrames=0` — the title hold reproduces a THIRD time (I23 probe1, probe2, I24) |
| **Retrieval** | `device copy from … tmp/i23-vector-rgba.bin` exit 0 → 917,504 B, sha `048b41af…` = host-7.1.1 byte-exact; `cmp` clean (`V3-RGBA-BYTE-IDENTICAL`, `logs/rgba-compare.txt`); SSD copy `N/logs/v3-rgba-device.bin` kept (E24 `/tmp`-volatility lesson) |
| Delivery | Dormant-trace markers `0x4029d0` ×6, `0x3b0b10/0x3b0b40/0x3b06b0` ×2, `0x3b1028` ×10 (all = I21/I23); CD 1103 reads; tails scheduled 398+ immediately after line 15167 |
| Tripwires | `guest-branch` ×0, `missing-target` ×0, `without FFmpeg` ×0, `sceCdSt` ×0, `Failed to open ELF` ×0, `sceCdRead unresolved` ×0, `teardown` ×0, `MPEG:GetPicture` ×0 (AGRESSIVE-gated, expected) |
| Threads | Block-0 row **byte-identical to I21/I23** (main `waitReason=6 waitId=0 pc=0x3b1028 scheduled=8255`; t4 `scheduled=859`); main still parked — 0 title frames served to the guest |
| Frames | 5/5, vsync 900→4500, `diff` vs I23's committed frame log clean (submission frozen — 0 title frames served) |
| Crash logs | `systemCrashLogs`: 26 files, **0 ps2-named**; no new `.ips` for I24 in the probe window. Method note: I23's "0 files" came from a different domain spelling (`crashLogs` is rejected by this `devicectl`); the ps2-count is the comparable row |
| Cleanup | Only OUR PID signaled (5108 via `process terminate`, exit 0); post-cleanup grep = 0; app left installed (I24 bundle + ISO + V3; precedent kept) |

## Task 3 — P4 structural identity + cheap re-checks + handoff

### P4: host-vs-device STRUCTURAL identity, row by row (Mission 4)

| # | Row | Host-7.1.1 (§Task 1) | Device (§Task 2) | Standing |
|---|---|---|---|---|
| 1 | Input bytes | 5040 B, FNV `d2a9588f0e0fd358`, sha `cde8a830…` | `inSize=5040 inputFnv64=d2a9588f0e0fd358` (same staged bytes, sha `cde8a830…`) | EXACT |
| 2 | Feed counts | `parsed=5040 packets=0 newFrames=0 totalFrames=0 ok=1` | `[MPEG:feed-trace] inSize=5040 parsed=5040 packets=0 newFrames=0 totalFrames=0` + `feed: ok=1 newFrames=0` | EXACT |
| 3 | Flush counts | `packets=1 newFrames=1 totalFrames=1 ok=1` | `flush: ok=1 newFrames=1 totalFrames=1` | EXACT |
| 4 | Frame dims | `frame0 512x448` (fmt=0 yuv420p) | `frame0 512x448 rgba=917504` | EXACT |
| 5 | RGBA bytes | 917,504 B, sha `048b41af…`, FNV `c1fdca14f69b2325`, `fd4900ff`×16 slices | 917,504 B retrieved, sha `048b41af…`, FNV `c1fdca14f69b2325`, same slices; `cmp` clean | EXACT |
| 6 | Stall-or-serve shape | Feed-hold + drain-serve (0 in-loop, 1 via parser-flush, NO appended bytes) | Same phase split through the REAL `MpegFfmpegDecoder` class | EXACT |
| 7 | Title-path trace | E-lane record `parsed=5040 packets=0 newFrames=0` | Line 15167 reproduces it (3rd observation) | EXACT |

Contract outcome: **H-a** — the two sides agree exactly on all 7 rows. P4's bar (title FRAMES from the V3 vector, not the hold alone) is met at the decoder: the device produces the 512×448 title frame through the real class, byte-identical to host. No device-only deviation → Cause-B stays closed on the decoder (the live title path still holds for lack of a terminating start code — E24's sharpened X, an input-shape fact, not a decoder fact).

### Cheap P2b/P9b/P5/P7 re-check (V3's output does NOT light guest paths)

| # | Bar | I24 receipt | Standing |
|---|---|---|---|
| P2b | FRAME served + resume-once + guest image nonzero | Main still parked (`waitReason=6`, block-0 byte-identical); frames frozen (5/5 bit-identical); the V3 frame is isolated by the no-fabrication constraint (no guest waiter exists for it) | NOT OBSERVED (unchanged) |
| P9b | IsEnd true only when ended + queue empty + presentation complete | Guest never drives flush/IsEnd to completion on the title path (0 title frames) | NOT OBSERVED (unchanged) |
| P5 | No-input semantics | Shape NOT DRIVEN on device (guest drives real input). Host R4 green on the identical class source (E18, 458/458 suite) | Host-held; device N/A (unchanged) |
| P7 | EOS-without-header holds | Shape NOT DRIVEN (title carries a sequence header per first4). Host E15-input row green on the identical class source | Host-held; device N/A (unchanged) |
| P9a+ | Drain requirement (I22 run-A-vs-B) | V3 adds a third drain-serve proof on device (`flush: +1`, V1/V4 already PASS in I23) | PASS (strengthened) |

### E24-WARNING nuance (observation, not a verdict)

E24's NEXT-BRIEF warned a replay reproduces `packets=0` "unless the harness appends a start code or feeds a following chunk". Observed on BOTH sides: the warning holds for the FEED phase exactly, and the parser NULL-flush — with NO appended bytes and NO following chunk — serves the complete picture. The picture was already fully delivered (28 contiguous slices, final at modal length); only the in-loop emission needed the terminator. Tabled for the E-lane's X (`why does the guest stop one start code short?`): on the live path the guest never flushes, so the served-frame question stays with the input shape, not the decoder.

### New gap rows (each with the exact next brief it needs)

| # | Gap | Proving line | Exact next brief needed |
|---|---|---|---|
| G1 | V3 (full 5040 B + title dims) | §Task 1 lock + §P4 table (this brief) | **CLOSED — no brief** (I23 G1/G2's V3 half; the guest-serve half carries below) |
| G2 | Guest-visible title serve (P2b/P9b: live-path frame + resume + IsEnd) | §cheap re-check (0 guest frames; main parked; title never flushed on the live path) | E-lane input-shape work on X (their lane/lease); a device re-probe rides after a live-path change lands |
| G3 | Shared host/brew/CI 7.1.x pin (E1/E2) | I23 §concurrence (zero I23/I24 edits by design) | E-lane concurrence + pin implementation (their config) |
| G4 | Branch `i23-ffmpeg-ios` unmerged (E-lane owns the fork) | 5 pushed commits (I23), 0 to `ssx3`; I24 added 0 | Merge/rebase conversation when the E-line allows (I24 needs no branch — nothing to merge from here) |
| G5 | Crashlog domain spelling (`crashLogs` rejected; `systemCrashLogs` lists 26, 0 ps2) | §Task 2 crash row | Informational — next brief uses `systemCrashLogs` + ps2-count; no brief |

### Handoff (what the next briefs consume / what stays)

| # | Item | Disposition |
|---|---|---|
| H1 | This P4 table + V3 host/device receipts (counts, digests, bytes) | CONSUMED by the merge decision (E-lane review of `i23-ffmpeg-ios`) or the G2 re-probe |
| H2 | `N/` (`signed-app/` V3 bundle + `logs/` full console + host/device RGBA bins) | STAYS on SSD (re-probe cost without: restage + 68 s install) |
| H3 | I24 device baseline (installed build UUID `F05E490A-…`, NOT running post-cleanup; V3 console + thread/frame rows) | STAYS — the next re-probe diffs against it |
| H4 | E-lane fork ownership + remote moves | E-lane ONLY — I24 moved nothing (remote `ssx3` at `3adc0478` recon AND end; 0 pushes) |
| H5 | `W/` prefixes + build tree + worktree @`193451a` | STAYS byte-identical (I24 read-only; next rebuild-if-needed starts here) |

## Exact commands

```sh
# --- Recon + vector lock (read-only; E-lane live) ---
FORK="/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp"; W="/Volumes/Extreme SSD/ps2x-i23"; N="/Volumes/Extreme SSD/ps2x-i24"
export COPYFILE_DISABLE=1; mkdir -p local/research/I24/logs "$N/logs" /tmp/ps2x-i24
git -C "$FORK" ls-remote fork ssx3          # 3adc0478 at recon AND end
git -C "$FORK" ls-remote fork i23-ffmpeg-ios  # aa73dbc at recon AND end
python3 /tmp/ps2x-i24/vlock.py | tee local/research/I24/logs/vector-lock.txt  # 3-copy lock + re-parse + census
# --- Host V3 anchor (existing prefix, no rebuild) ---
shasum -a 256 "$W/host-7.1.1/lib/"*.a       # c2193235/369c7241/d720f9ef
cp local/research/I22/logs/i22-decode.c /tmp/ps2x-i24/i24-decode.c; diff # VERBATIM
clang -arch arm64 -Os -I"$W/host-7.1.1/include" /tmp/ps2x-i24/i24-decode.c \
  "$W/host-7.1.1/lib/"*.a -framework CoreFoundation -framework CoreVideo -framework VideoToolbox \
  -o /tmp/ps2x-i24/i24-decode                  # exit 0
for i in 1 2 3 4 5; do /tmp/ps2x-i24/i24-decode local/research/E24/observed/parser-input.bin /tmp/ps2x-i24/v3-rgba-$i.bin; done  # 5x exit 0, 5040/5040/1/1/917504
clang [same recipe] /tmp/ps2x-i24/i24-decode-split.c -o /tmp/ps2x-i24/i24-decode-split  # exit 0
for i in 1 2 3; do /tmp/ps2x-i24/i24-decode-split local/research/E24/observed/parser-input.bin /tmp/ps2x-i24/v3s-rgba-$i.bin; done  # 3x feed-hold + drain-serve
python3 /tmp/ps2x-i24/fnv.py <v3-rgba-1.bin, E24 parser-input.bin>  # FNV64+sha+first64/last64
cp /tmp/ps2x-i24/v3-rgba-1.bin "$N/logs/v3-rgba-host-7.1.1.bin"     # SSD anchor
# --- Device pre-state (read-only) ---
P="00008112-001224302184A01E"
xcrun devicectl list devices --timeout 30
xcrun devicectl device info apps --device "$P" --timeout 60 | grep -iE "ps2|MF1"
xcrun devicectl device info processes --device "$P" --timeout 60 | grep -i ps2EntryRunner  # PID 4790
# --- Reuse check (no rebuild) ---
stat -f%z + shasum "$W/ios-runtime-device/.../ps2EntryRunner"  # 122458696 edb3eadce3ff9d03...0c60c1
shasum .../libps2_game_objects.a                               # f356aaa7ddfd9643...2addcd
# --- Stage/sign/install/probe ---
cp -R "$W/ios-runtime-device/.../ps2EntryRunner.app" "$N/signed-app/"
cp "$W/signed-app/.../SLUS_207.72" "$W/signed-app/.../embedded.mobileprovision" "$N/signed-app/ps2EntryRunner.app/"
cp local/research/E24/observed/parser-input.bin "$N/signed-app/ps2EntryRunner.app/i24-v3.m2v"
cp "$W/signed-app/.../SSX3.iso" "$N/signed-app/ps2EntryRunner.app/"; find "$N" -name "._*" -delete
shasum ELF/ISO/V3/binary  # 1b49d05c/3c2f8eb1/cde8a830/edb3eadc pre-sign
codesign --force --sign 295EFB42E6734599E5726A9A5EF47EBD1EFEF7B1 --timestamp=none \
  --entitlements /tmp/ps2x-i24/entitlements-from-i21.plist "$N/signed-app/ps2EntryRunner.app"  # exit 0
codesign --verify --strict "$N/signed-app/ps2EntryRunner.app"  # exit 0
xcrun devicectl device install app --device "$P" --timeout 1200 "$N/signed-app/ps2EntryRunner.app"  # exit 0, 68.4s -> F05E490A
B="/private/var/containers/Bundle/Application/F05E490A-D080-498B-ABC5-2480EC78ACFE/ps2EntryRunner.app"
xcrun devicectl device process launch --device "$P" --timeout 90 --console --terminate-existing \
  -e '{"PS2X_CD_IMAGE":"'"$B"'/SSX3.iso","PS2X_DIAG_PERIOD_MS":"15000","PS2X_DIAG_SEMA":"1","PS2X_DIAG_SEMA_CREATE":"1","PS2X_MPEG_VECTOR_PATH":"'"$B"'/i24-v3.m2v","PS2X_MPEG_FEED_TRACE":"1"}' \
  org.ps2x.ps2entryrunner "$B/SLUS_207.72" > "$N/logs/launch-v3-console.log" 2>&1  # exit 2 (alive, PID 5108), 45611 lines
xcrun devicectl device info files --device "$P" --timeout 60 --domain-type appDataContainer \
  --domain-identifier org.ps2x.ps2entryrunner --subdirectory tmp --no-recurse  # i23-vector-rgba.bin 896 KB
xcrun devicectl device copy from --device "$P" --timeout 120 --domain-type appDataContainer \
  --domain-identifier org.ps2x.ps2entryrunner --source tmp/i23-vector-rgba.bin --destination /tmp/...  # exit 0
cmp /tmp/ps2x-i24/v3-rgba-device.bin "$N/logs/v3-rgba-host-7.1.1.bin"  # V3-RGBA-BYTE-IDENTICAL
cp /tmp/ps2x-i24/v3-rgba-device.bin "$N/logs/v3-rgba-device.bin"  # SSD preserve + re-cmp
xcrun devicectl device info files --device "$P" --timeout 60 --domain-type systemCrashLogs --no-recurse  # 26 files, 0 ps2
xcrun devicectl device process terminate --device "$P" --timeout 30 --pid 5108  # cleanup only, 0 after
```

## Receipt paths

- `local/research/I24/REPORT.md` (this file)
- `local/research/I24/logs/vector-lock.txt` (3-copy lock + dims re-parse + census) + `v3-input-fnv.txt` + `v3-rgba-host-fnv.txt` + `rgba-compare.txt`
- `local/research/I24/logs/i24-decode.c` (verbatim I22 harness) + `i24-decode-split.c` (split-phase harness) + `decode-v3-host.log` (5×) + `decode-v3-split-host.log` (3×)
- `local/research/I24/logs/ipad-prestate-i24.log` + `install.log` + `launch-v3-vector.log` + `launch-v3-frame.log` + `launch-v3-threads-block0.log` + `launch-v3-console.sizes` + `crashlog-check1.log`
- `N/logs/` (full V3 console 45611 lines + host/device RGBA bins, cmp-clean) + `N/signed-app/` (installed V3 bundle bits)
- No fork push this brief (nothing to push — zero fork commits by design)

## What I could not do

- Serve a guest-visible title FRAME on device — the live title path still holds (0 frames, main parked); the V3 frame is isolated by the no-fabrication constraint (P2b/P9b).
- Drive the P5/P7 input shapes on device — the guest drives one shape (5040 B with header); host rows stand on the identical class source.
- Exercise `sceMpegFlush`/IsEnd completion on the live title path — the guest never flushes there (P9b).
- Use the ≤2 GB scratch the brief suggested — the single ISO stage is 2.9 GB allocated; declared ≤5 GB with cause before staging, used 2.9 GB.
- Reproduce I23's "0 files" crashlog check verbatim — `crashLogs` is rejected by this `devicectl`; used `systemCrashLogs` (26 files, 0 ps2-named) instead (G5).
- Pin the shared host/brew/CI config — explicitly out of scope; tabled for E-lane concurrence (G3).
- Merge the branch — E-lane owns the fork; I24 added 0 commits (G4).
- Name the launcher of pre-install PID 4790 — the I23 bundle was running though I23 signaled only its own probe PID at cleanup (ninth brief running with a relaunched occupant); it was reaped by the install without investigation.

## TAIL RECEIPT

Report written in 6 chunks (header + contract + caps; Task 1 lock + host anchor; Task 2 reuse + install + probe; Task 3 P4 + re-checks + gaps + handoff; commands + receipts + could-not-do; this receipt). Pre-receipt measure: 246 lines total, sha256 `20c826a4fd5d88bf8c922203905c4b5de6017dfc50017d03545a60b6bf465bbf` over lines 1–246 (everything before this `## TAIL RECEIPT` section).
Tail content line: "Name the launcher of pre-install PID 4790 — the I23 bundle was running though I23 signaled only its own probe PID at cleanup (ninth brief running with a relaunched occupant); it was reaped by the install without investigation." This receipt line ends the report. END-I24-REPORT.
