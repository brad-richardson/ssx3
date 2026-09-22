| E30 | Receipt |
|---|---|
| Stop point | **Both missions executed; nothing blocked.** Read-only on the fork throughout (E31 owns the worktree + P-lane lease): fork touched only via `git show`/`git grep`/`git archive` at `3adc0478`, plus reads of `P1/run` boot logs. Zero checkouts, builds, boots, leases. |
| Headline | **The zero-packet stall is (a)+(d): a correct parser waiting for a second chunk the host latch never requests.** The 5,040 B chunk holds a complete-but-unterminated first picture (all 28 slices present, no closing start code); FFmpeg's mpegvideo parser correctly buffers it (`parsed=5040 packets=0`). The E27 host latch then parks forever after exactly one producer dispatch. Fix: re-request input while decoder-accepted bytes flow without yielding frames; park when the producer is dry. |
| Deliverables | `e30-fix.diff` (1 file, +105/−3), `e30-regression.diff` (1 file, +231/−1), `e32-handoff.md` (apply + suite + A/B boot plan), `predictions.md` (written before any run), `harness-results.txt`, `startcode-scan.txt`. |
| Recommendation | Hand both diffs to E32 (apply-and-boot). No tuning needed from E30: every byte fact is harness-proven, both fixed TUs compile clean under the exact E29 build flags, both diffs dry-run apply. |

## Mission 1 — why 15,056 consumed bytes complete zero packets

Byte facts (feed vector `local/research/E22/observed/parser-input.bin`, 5,040 B, `cde8a830…2a1c875a`, re-hashed in E30 scratch):

- Start-code scan (`startcode-scan.txt`): seq_hdr@0 (512×448, framerate_code 4), ext, GOP@68, picture@76 (temporal_ref 0, type 3 = **B**), slices 0x01–0x1c = 28/28 macroblock rows, then 12 zero pad bytes. The final slice is **unterminated**: no start code closes the picture.
- E26's terminator `00 00 01 00` lives at guest `0xd49b1c`, inside chunk 2 (queue head `0xd49b14`, E27/E28). One chunk can never complete a packet.
- No pack (BA) / system (BB) / program-end (B9) / PES (BD/E0–EF) codes anywhere: the input is pure elementary stream.

| Candidate | Verdict | Evidence |
|---|---|---|
| (a) parser needs more bytes; second chunk never requested (host latch) | **SUPPORTED (the defect)** | H1 reproduces `5040/0/0`; H2a/H2b (vector + terminator) yield 1 packet. Latch side: E27 mechanism + boot logs (feedES ×1, GetPicture ×1 per movie). |
| (b) ES-vs-PS mis-framing | **EXCLUDED** | Pure-ES scan above; `sceMpegAddBs` → `feedElementaryStream` → mpeg2video parser is the right path; H2 packets ≥ 1 proves the parser choice. |
| (c) no-FFmpeg stub build | **EXCLUDED twice** | E18 `configure-command.json` sets `PS2X_ENABLE_FFMPEG=ON` and E29 built on that recipe; `[MPEG:feed]` lines exist in the e29b boot log and that format string exists ONLY in the `#if PS2X_HAS_FFMPEG` branch. |
| (d) correct behavior (needs more data) | **SUPPORTED (the parser half)** | 0 packets from one unterminated chunk is what a correct parser does. The defect is (a): the runtime never feeds chunk 2. |

Predictions-vs-results (harness = 416-line **verbatim** copy of `MpegFfmpegDecoder` + helpers from `MPEG.cpp` @ `3adc0478`, fidelity-checked line-by-line; Apple clang 21, FFmpeg libavcodec 63 / libavutil 61 / libswscale 10):

| Run | Input | Predicted parsed/packets/frames | Measured | Verdict |
|---|---|---|---|---|
| H1 | vector | 5040 / 0 / 0 | 5040 / 0 / 0 | CONFIRM — boot closure reproduced exactly |
| H2a | vector + 68 B terminator | 5108 / ≥1 / 0 (B-frame, no refs) | 5108 / 1 / 0 | CONFIRM |
| H2b | vector + picture+slice heads | ≥1 packet / 0 frames | 1 / 0 | CONFIRM |
| H3 | vector, then `flush()` | SPLIT: 0 or 1 frame | 1 frame, 512×448 | resolved → 1 (I24 flush-serve corroborated on this vector) |
| H4 | vector split 2500/2540 | 5040 / 0 / 0 | 5040 / 0 / 0 | CONFIRM — chunking irrelevant, only the terminator matters |
| H5/H6 | vector (+terminator) + flush, hashed | same frame | same FNV `35ef864cdd920383` | second chunk releases the packet; the frame still needs flush/refs |

Consequence for the fix: re-requesting input completes **packets**; frames follow from later chunks (refs) or the existing end-of-stream flush (`finishPlaybackStream` → `flushDecoderIfEnded`, already wired). No new flush needed — and none added.

## Mission 2 — regression diff + fix diff

### The fix (`e30-fix.diff`, against `ps2xRuntime/src/lib/Kernel/Stubs/MPEG.cpp` @ `3adc0478`)

`redispatchNonStreamInputIfStarved()`, called from the delivery `onComplete` (which the scheduler reaches only when the callback list is exhausted — `invokeCurrent` is `[[noreturn]]`, throwing `EeDispatcherTransfer`, so re-dispatch trampolines through the dispatcher and cannot recurse the C++ stack). Rule:

- Re-dispatch (fresh delivery, same dispatch path/callbacks/order/cbData layout) iff: no wake condition (frames/EOF/ended/failed) AND fresh **decoder-accepted** bytes since this delivery started AND round count ≤ 4096.
- Else: erase the exhausted delivery's latch token and continue the request (serve or park) exactly as today.

Why decoder-accepted bytes (new `decoderBytesFed`, incremented only past the sequence-header gate): R2's 16 pre-header bytes never reach the decoder, so R2 keeps its dispatch-once contract and stays green — this is the load-bearing compatibility point. A dry producer parks after exactly 1 dispatch; a trickling producer parks after 4097 (hang-stop); the title re-requests until frames arrive. No signature changes (E18 ABI intact), no flush added, no synthetic success, no EOF invented.

Per-movie re-arm is automatic: `sceMpegCreate` invalidates deliveries + installs fresh playback (counter back to 0). Cancel/reset win over re-dispatch: `onComplete` returns early on `cancelled` before reaching the helper, and the helper bails (without resurrecting state) if the playback entry is gone.

### The regression (`e30-regression.diff`, against `ps2xTest/src/ps2_runtime_expansion_tests.cpp` @ `3adc0478`)

`runNonStreamProbe` and R1–R6 are byte-untouched; a new `runNonStreamChunkProbe` reuses the same PCs with a chunk-queue producer over a mechanically-copied 240 B fixture (seq headers at 0/60/120/180, verified). New tests R7, R8, R8b, R9, R10, R11 (suite becomes 464):

| Test | Asserts | Base (no fix) | Fixed |
|---|---|---|---|
| R7 two-chunk core | delivered {11,11}, copied 240, resumed ×1, result 0, 16×16 pixels, ownership/saved/freed | FAIL (parks after 1 dispatch) | PASS |
| R8 empty input (AddBs(0) + no-AddBs) | 1 dispatch, 0 copied, parked, saved/freed | PASS (characterization: the dry bound) | PASS |
| R8b trickle hang-stop | exactly 4097 dispatches, then parked | FAIL (1 dispatch: pre-fix parks on any no-frame round) | PASS |
| R9 EOF flushes partial feed | EOF-after-park, {11,11}, resumed ×1, 16×16 | FAIL on dispatch count (resume half passes via EOF-flush — the fix's endgame, characterized) | PASS |
| R10 delete/reset on 2nd dispatch | {11,11}, resumed ×1, KE_WAIT_DELETE, saved/freed | FAIL (never reaches 2nd dispatch) | PASS |
| R11 Create re-arm, 2 movies | {11⁴}, copied 480, resumed ×2, 16×16 | FAIL (movie 1 parks) | PASS |

The five E29-measured bypass-broken tests (R1, R2, R4, R6, "waits for new decoder output") are named in the diff header as must-stay-green; R1/R2/R4/R6 traced green by inspection (zero decoder bytes / frames-present / cancelled paths bypass the helper).

### Proof status (honest split)

- **Proven in E30:** zero-packet cause (H1–H6); regression byte design — chunk1 `[0,60)` → 0 packets, +chunk2 → 3 packets + 2 decoded 16×16 frames, chunk1 + flush → 1 frame (`R7-design`, `R9-design` in `harness-results.txt`); both diffs dry-run apply (`patch -p1` PASS); both fixed TUs compile clean (`-fsyntax-only`, rc 0) with the exact E29 `compile_commands.json` flags (LLVM 23, gnu++20, FFmpeg 9.0.1 headers, sse2neon).
- **Only the real suite + a boot can prove (E32):** dispatch counts, resume counts, R1–R6 green, 464/464, and title behavior (`[MPEG:nonstream-redispatch]` ≥ 1, feedES ×N, frames served, A/B vs E29 e29b title screen). The standalone harness cannot execute the scheduler trampoline.

## Residuals and limits

1. Harness FFmpeg (8.x, libavcodec 63) ≠ build FFmpeg (9.0.1): parser hold/terminator behavior agreed on all vectors, but E32's suite run is the version-authoritative proof.
2. Mid-movie CD refill still doesn't wake a dry-parked GetPicture (pre-existing; only EOF wakes). The title's 431 KB queue makes this unreachable before end-of-movie; named, not solved.
3. The guest's empty-queue 16-byte `sequence_end` feed (E27) counts as decoder bytes, so an empty queue spins to the 4097 hang-stop before parking — bounded and far from the title's state, but E32 should watch for `round=` climbing in boot logs.
4. `sceMpegReset` after `streamEnded` preserves ended-ness; R11 uses Create (the title's path, E29), not Reset.

## Hygiene

- Fork: read-only (`git show`/`grep`/`archive` @ `3adc0478`; HEAD verified `3adc0478` at open). No checkout/build/boot/lease. E29 `e29-movie-bypass` read for the A/B reference only.
- Scratch: `/Volumes/Extreme SSD/ps2x-e30/` 446 MB logical (cap 2 GB); `COPYFILE_DISABLE=1` on every command. Evidence: text only.
- Time: well inside the 5 h box, single session.
