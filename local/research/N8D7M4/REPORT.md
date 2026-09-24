# N8D7M4 — same-stream Odin VRAM provenance gate design (read-only)

**State: design only. No source edit, build, replay, boot, Odin/iOS action, push, or status/todo/ledger edit. No cause declared; the orchestrator decides the gate.**

Brief `local/muse/prompts/N8D7M4.md`. Rejected predecessors are not reused as discriminators: N8D7M3's draw-count floor (K), Present-entry pending flag (T1) and two-control-word test were judged nondiscriminating (`local/research/N8D7M3/ORCH-GATE.md`), and no Turnip/GS cause follows from a sparse image alone. Two hard constraints from the brief are honored throughout: (a) N8D4's Odin stream (SHA `38ace1a3…93f97d`) and N8D7M2's Odin boot are **different runs** — no value is compared across them as if one stream; (b) RGBA output bytes are **never** mistaken for VRAM words.

LSP hover on the pinned backend returned no results (no language server for files outside the repo); every code link below rests on direct source reads, same as N8D7M3 §7.

## 1. Source-path table: capture, replay, selected snapshot

Pinned sources: fork worktree `~/dev/ssx3-work/N8D7L/PS2Recomp` rev `d1ba1d49` (== N8D7M1 APK oracle source, `local/research/N8D7M1/REPORT.md` §1–3), G43 worktree `~/dev/ssx3-work/N8D7F/parallel-gs`. Current APK `~/dev/ssx3-work/N8D7M1/app-release.apk` SHA `e077bef8…758a1`.

| # | Stage | Exact code site | What it proves / owns |
| --- | --- | --- | --- |
| 1a | Capture open + magic | `ps2xRuntime/src/lib/gs/gs_stream_capture.cpp:23-43` | `PS2X_GS_CAPTURE` path, writes `PS2XGSC1`, 6 GiB cap |
| 1b | Packet/priv/transfer/native/clear/readback record | same file `:153-240`; call sites `gs_frontend.cpp:951,1079` (packet), `:1137` (nativeUpload), `:1786` (transfer), `:2076` (clear), `:2116` (localToHost), `ps2_memory.cpp:1024,1052` (privWrite) | Every record is length-prefixed (`:107-120`); kinds 1–7 |
| 1c | VBlank marker + stop/close | same file `:242-265`; called from `EeScheduler.cpp:2676` (`ps2x_gs_capture::vblank(m_vsyncTick)`, same position as the live VQ sample) | Type-4 marker per tick; `fflush` per marker; closes file at `PS2X_GS_CAPTURE_STOP_TICK`/`PS2X_GS_BISECT_TO` with `[gs:capture] stopped at marker` |
| 2a | Replay parse | `ps2xTest/src/ps2_gs_replay_tests.cpp:32-44` (length-prefix, `length<9` invalid), `:160-166` (magic check), `:257-474` per-kind decode | Strict: truncated body invalid; kind-6 readbacks byte-compared (`:448-455`); kind-3 transfers audit-only |
| 2b | Replay ordering | same file `:327-329` (`drainQueue` + `vsyncTick=tick` at each marker), `:476` final drain | CPU replay is synchronous at markers: words at marker 2050 = all tick≤2050 packets applied |
| 2c | Existing per-packet probe | same file `:228-236` + `:289-292` (`PS2X_GS_REPLAY_PACKET_TRACE`, per-packet FNV of whole VRAM, only for `tick < BISECT_TO`) | Closest existing probe; logs whole-VRAM hash, **not** per-word old→new (gap §3) |
| 3a | Selected request gate | `ps2_gs_parallel_backend.cpp:440-447` | `selectedRequested` only when `request.vsyncTick==2050` and `PS2X_N8D7F_SELECTED_CAPTURE=1`; `vsync.phase = tick&1`. Tick owned by priv regs (`gs_frontend.cpp:757-777`) |
| 3b | Selected descriptor | G43 `gs/gs_renderer.cpp:4777-4792` | FBP/FBW/PSM/DBX/DBY from `priv.dispfb1`; phase/stride from `compute_circuit_rect`; mask=`vram_size-1`; samples; promoted |
| 3c | 4 MiB snapshot copy | G43 `:4793-4820` (guard: supported PSM, 512×224, 4 MiB, coords<2048; `copy_buffer` staging←`buffers.gpu` with COMPUTE\|TRANSFER→TRANSFER_READ barrier) | Recorded into the vsync command buffer **after** `m_iface->flush()` (backend `:452-453`), so previously flushed draws execute first in GPU order |
| 3d | Ordered completion point | backend `:601-602` (`submit` + `wait_idle`), host maps staging at `:621-626`, status 2 required at `:614-618` | Host-visible snapshot words are post-completion by construction; `control=128 PASS` + `status=2` are the acceptance witnesses |
| 3e | CPU selected decode | backend `:100-156` (`base=fbp*PGS_BLOCKS_PER_PAGE`, `sy=dby+phase+y*stride`, `vram_readback<PSM>` with `&2047` wrap + `swizzle_PS2`) → `selectedTileCounts` `:64-81` (RGB max≥32, 448 tiles) | G43 bit-arithmetic address path |
| 3f | Independent oracle | backend `:190-222` (`GSPSMCT32::addrPSMCT32(block=fbp<<5,fbw,gx,gy)`, `&0x3FFFFF`, RGB≥32) + controls `kOracleControls` `:179-188`, emitted `:712-729`, gated by `PS2X_N8D7L_ORACLE` (`:667-668`) | Fork literal-table path; shares only the mapped snapshot. N8D7M2 agreement (448/448) rules out decoder disagreement **on that run only** |

Address math (actual GS storage, N8D7M3 §2, N8D7K §3): FBP112 base byte `112*8192=0xE0000`, block `112<<5=3584`.

## 2. Diagnostic address/packet candidate table

**Gap stated first:** no existing receipt contains a per-packet VRAM word history. `PS2X_GS_REPLAY_PACKET_TRACE` logs whole-VRAM FNV only; the eight `oracle_controls` words are post-completion snapshots. Therefore **no packet index/tick + old→new row can be filled from available evidence without a new tap** — neither for the pinned N8D4 stream nor for any Odin run. The concrete address set below is exact (runtime-verified literals, self-checked at backend `:685-696`); the packet-provenance column is filled by the Mac tap validation (§5 step 1), never by hand.

 Concrete set: the eight `kOracleControls` words (byte addresses are swizzled GS-storage bytes, not linear offsets). Mac words are observed on the pinned N8D4 stream (`local/research/N8D7L/replay-excerpt.txt:14`); Mac tile counts from the same receipt (`:5`); Odin N8D4 RGBA column is the viewed-image observation (`local/research/N8D4/REPORT.md` §Viewed regions: mostly black with narrow snow fragments, timer/position absent), **not** a word claim.

| # | Pixel (gx,gy) | Tile (census) | GS storage byte | Mac word (N8D4 stream, observed) | Mac tile count (observed) | N8D4 Odin RGBA at that region (observed, not a word) |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | (0,0) | 0 | `0x0E0000` | `0x00260803` | 256 | black (upper HUD corner has only a small cyan fragment) |
| 2 | (31,0) | 1 | `0x0E0534` | `0x00260802` | 256 | black |
| 3 | (0,2) | 0 | `0x0E0040` | `0x00260804` | 256 | black |
| 4 | (511,446) | 447 | `0x1BFFF4` | `0x000C0000` | 0 (dark lower region on both) | black — **not diagnostic alone**; page-extent check only |
| 5 | (64,0) | 2 | `0x0E2000` | `0x00260802` | 256 | black |
| 6 | (0,32) | 32 | `0x0F0000` | `0xFF230401` | 256 | black — other-page context |
| 7 | (63,31) | — (odd-y, never a census pixel) | `0x0E1FFC` | `0x003D2B00` | — | — read-path check only |
| 8 | (64,32) | 34 | `0x0F2000` | `0x00604400` | 256 | black — other-page context |

Primary diagnostic subset: rows 1–3 + 5 (FBP112 page, even-gy census pixels, Mac RGB-nonzero with max byte ≥32). Expected Odin observation **if** the sparse image reflects sparse VRAM: `0x00000000` at rows 1–3,5 — recorded as a *prediction*, not a fact. Cross-run illustration only (different boot, never compared as one stream): on the N8D7M2 run these read `0x00060000,0x000C0000,0x000C0000,…,0x00000000` with tile 0 count 0 vs Mac 256 (`local/research/N8D7M2/tile-excerpt.txt:5-6,16-23`).

**Selection rule for further pixels (tap-emitted addresses, never hand-computed):** any even-gy pixel in a tile with Mac CPU count 256 on the *same* stream, whose word the Mac CPU tap (§5) shows transitioning `0x00000000→nonzero` at a recorded packet index/tick ≤2050. The tap computes the byte address at runtime via `GSPSMCT32::addrPSMCT32`, so no manual swizzle is trusted.

**Why rows 1–3,5 discriminate while M3's controls did not:** M3 compared two nonzero words against a sparse census with no packet history (ORCH-GATE: "can coexist with a sparse census"). Here each word is paired with (i) the CPU packet index/tick that wrote it on the *same* stream and (ii) the post-completion snapshot word on both GPUs — a write proved present in the stream, not a bare nonzero literal.

## 3. The one new tap (Mac test-only) + minimum device-side change

- **New tap (required, Mac `ps2xTest` only, default OFF):** `PS2X_GS_REPLAY_WORDS=0xE0000,0xE0534,…` (≤8 byte addresses). In `replay()` kind==1 branch (`ps2_gs_replay_tests.cpp:260-293`), snapshot the listed `vram[]` words before/after `gs.processGIFPacket` and emit `[n8d7m4] word idx=<packet> tick=<tick> addr=<a> old=<o> new=<n>` **only on change**. ~20 lines, test-only, zero behavior change when unset; suite stays 585. Selection provenance needs no tap: scan the captured stream's kind-2 records offline for offsets `0x0070/0x0080` (DISPFB1/DISPLAY1) and record last-writer tick ≤2050.
- **Device side (no build):** the current N8D7M1 APK already contains **both** paths — verified by direct member read (not a cross-run claim): `libps2EntryRunner.so` contains `PS2X_GS_CAPTURE` (4×), `PS2XGSC1`, `PS2X_GS_CAPTURE_STOP_TICK`, `PS2X_N8D7F_SELECTED_CAPTURE`, `PS2X_N8D7L_ORACLE`, `[n8d7f]/[n8d7l]` markers. One future launch sets capture + snapshot env together (N8D4 set only capture; N8D7M2 set only snapshot — that split is exactly why no same-run comparison exists yet).
- **Minimum build/source change (only if §5 step 1 shows the 8 words insufficient):** add default-OFF `PS2X_N8D7M4_WORDS` (arbitrary ≤8-word list read from the same mapped `selected_vram_staging` after the existing `wait_idle`, emitted as `[n8d7m4] odin_words=…`) and/or `PS2X_N8D7M4_SECOND_TICK` (repeat the selected capture at a second tick, e.g. 2052, to harden the ordering witness). Exact package gate, same as N8D4 `launch.py:237`: runner member must contain `PS2X_GS_CAPTURE_STOP_TICK`, `PS2XGSC1`, `[n8d7f]`, `[n8d7l]`, `oracle_controls=`, plus the new `[n8d7m4]` marker; APK/ELF/ISO two-read SHA pins as in N8D4/N8D7M2.

## 4. Predeclared outcome table (mutually exclusive)

Preconditions for every row (else **OTHER**): aligned tick-2050 frame (FBP112, PMODE `ff21`, 512×448); status 2; 11/11 selected/oracle metadata agreement; `control=128 PASS`; no probe/pipeline error; capture complete (magic `PS2XGSC1`, last event marker (4,2050), local==device bytes, two device + two Mac SHA reads all equal); Mac CPU **and** Mac paraLLEl replays of the *same new stream* parse clean with packet/priv/transfer/marker counts equal to the capture scan. Sparse = active ≤100/448; broad = active ≥250/448. Word "match" = byte-equal at the probed address; "Odin-words-match-CPU" = ≥6/8 addresses equal. A mere draw count, nonzero control word, or cross-run Mac/Odin literal is insufficient for any row.

| Outcome | Same-run observable (all must hold) | Conditional causal conclusion |
| --- | --- | --- |
| S-STREAM (stream/selection difference) | CPU replay of the same stream is also sparse (probed words stay `0x00000000`, census ≤100) with complete capture; **or** the Odin selected descriptor differs from the Mac replay descriptor (fbp/phase/stride/dbx/dby) | The boot's stream lacks FBP112 writes, or the snapshot sampled a different region than the Mac replay. Next: writer side (pad route, movie bypass, GIF delivery). Not a GPU VRAM-write fault |
| S-MISSING (missing GPU VRAM write) | Descriptor match Odin==Mac (11/11 + equal replay descriptor); CPU words transition `0→nonzero` at recorded packets tick≤2050 with census ≥250; Mac paraLLEl snapshot words match CPU (≥6/8); Odin snapshot census ≤100 with probed FBP112 words RGB-zero; Odin tick-2052 frame still sparse | Writes are in the stream and execute on the Mac GPU but are absent from the Odin snapshot after the ordered completion point. Next: Odin upload/flush/raster path. Still not a named Turnip bug — no shader/address cause is declared |
| S-ORDER (snapshot/transfer ordering) | Same as S-MISSING through the Odin sparse snapshot, **but** the Odin tick-2052 frontend frame is broad (writes landed late) | The 2050 copy executed before tick≤2050 draws became visible (stale copy). Next: flush/drain/barrier ordering (`COLOR_ATTACHMENT_OUTPUT` barrier, post-flush re-read). A second-tick snapshot build is the hardening step |
| S-DECODE (census/decoder loss) | Odin probed words match CPU (≥6/8 byte-equal, RGB-nonzero) **yet** the Odin census stays sparse (≤100) | Bytes are present at fork-table addresses but the census loses them (PSM/mask/wrap handling). Next: decode path, not the writer or GPU |
| OTHER | Gate miss; actives 101–249; replay counts ≠ capture counts; descriptor mismatch subset not covered above; incomplete capture; missing 2052 dump (ordering witness unset); ambiguous words (3–5/8 agree) | No conclusion; re-gate. No new device run until the missing line is explained |

S-MISSING vs S-ORDER cannot both hold (2052 frame sparse vs broad); S-DECODE cannot hold with S-MISSING/S-ORDER (words match vs words zero); S-STREAM cannot hold with any other row (CPU sparse vs CPU broad). N8D4 values are used only as Mac-tap calibration expectations, never as identity pins for the new stream.

## 5. Build/run/stop plan

**Step 1 — incremental Mac validation on the pinned N8D4 stream (no device, no Android build):** add the §3 word tap to `ps2xTest` only; rebuild `ps2x_tests` (Mac-only test binary); CPU replay with `PS2X_GS_REPLAY_CAPTURE=~/dev/ssx3-work/N8D4/n8d4.gs` (verify SHA `38ace1a3…93f97d` first), `PS2X_GS_REPLAY_WORDS=<8 controls>`; expect transitions at rows 1–3,5 with tick≤2050 and broad census; offline kind-2 scan for DISPFB1/DISPLAY1 last-writer tick; paraLLEl replay must reproduce the eight Mac words from §2 (already observed). This sets the exact packet rows the Odin run must beat. No diagnostic wall time is a speed number.

**Step 2 — one Odin launch (≤300 s, existing N8D7M1 APK `e077bef8…758a1`, zero Android builds unless §3 extension triggered):** install even if present; I26-FAST vsync pad route; parallel backend + Turnip + dev movie bypass + installed ISO (ELF `1b49d05c…`, ISO `3c2f8eb1…` double-reads); env = N8D7M2 `ps2x.env` **plus** `PS2X_GS_CAPTURE=<path>` + `PS2X_GS_CAPTURE_STOP_TICK=2050`, frame dumps at ticks `2050,2052` (`PS2X_FRAME_DUMP_ONCE_TICKS=2050,2052,999999`), 16 MiB log cap. Preflight: lease free, keyguard `showing=false` (else stop, ask Brad), battery charging ≥20%, free space ≥2 GiB. Stop at first complete aligned receipt + both dumps; first fatal/process exit; tick 2100 without receipt; 180 s below tick 1700; 300 s wall. Force-stop, PID-absent check, lease release even on error.

**Step 3 — same-stream Mac replays:** CPU replay with word tap + paraLLEl replay of the Step-2 stream; compare per §4 using only same-run rows.

**Caps:** ≤1 Android build (reserved, expected 0), ≤1 Odin launch ≤300 s, ≤16 MiB text log, ≤4 GiB stream + private scratch (stream ~1.1 GB precedent), images ≤4 small review PNGs in git; stream/PPMs/raw stay in `~/dev/ssx3-work/N8D7M4/` outside git (**no asset in git**). Mini lease slot via `local/tooling/p_lane_lease.py`; Odin lease `/data/local/tmp/mg/LEASE` (one device agent at a time). Reuse N8D4 `launch.py`/`accept.py` patterns and N8D7L oracle code unchanged.

**Acceptance script** (structure check only; orchestrator judges meaning): verify (i) new-stream SHA across two device + two Mac reads all equal; (ii) capture completeness — magic, last event (4,2050), counts>0, local==device bytes (N8D4 `accept.py:60-87` pattern); (iii) descriptor rows — Odin `[n8d7f]`/`[n8d7l]` 11/11 agreement **and** equality with the Mac replay descriptor; (iv) ordered word rows — Odin 8 controls + Mac CPU tap transitions + Mac paraLLEl controls at the same addresses, each annotated with its completion witness (status 2 / `control=128` / `drainQueue`-at-marker).

## 6. Commands read (all read-only)

Repo/brief/receipts: `local/muse/prompts/N8D7M4.md`; `~/dev/AGENTS.md`; repo `AGENTS.md`; `local/AGENTS.local.md`; `local/research/N8D4/{REPORT.md,replay-result.json}` (+`accept.py`,`launch.py` via targeted search); `local/research/N8D7M2/{REPORT.md,ORCH-GATE.md,result.json,tile-excerpt.txt,ps2x.env}`; `local/research/N8D7L/{REPORT.md,ORCH-GATE.md,replay-excerpt.txt}`; `local/research/N8D7M3/{REPORT.md,ORCH-GATE.md}`; `local/research/N8D7M1/REPORT.md`; `git log -1`, `git status --short`; worktree/lease/scratch listings; APK member string scan (read-only zip). Sources (direct reads; one LSP hover, empty): `gs_stream_capture.cpp` (full 280), `ps2_gs_replay_tests.cpp` (full 565), `ps2_gs_parallel_backend.cpp:1-150,150-449,450-749`, `gs_frontend.cpp:80-159`, `EeScheduler.cpp:2640-2699`, G43 `gs_renderer.cpp:4750-4830` (via bounded print), plus targeted symbol searches over `ps2xRuntime/src` and `parallel-gs`.

## 7. Unresolved risks

- Env forwarding for the combined capture+snapshot launch uses the same app layer as N8D4/N8D7M2, but both-together is untested: capture file growth plus snapshot staging could interact under storage/memory pressure (mitigated by ≥2 GiB preflight and stop rules).
- The 2052-frame lateness witness is one-sided: a sparse 2052 frame supports S-MISSING only jointly with the CPU-proven writes, never alone.
- PSMCT24 upper-byte handling in word compares: compare full 32-bit words; RGB-only threshold (≥32) applies to census classification, never to word equality.
- No local PCSX2 third mapping (bytesize-only); fork-vs-G43 remains the only independent pair (N8D7M3 §7 residual stands).

## 8. Handback tables

Source path: §1. Diagnostic candidates: §2 (8 literal addresses with observed Mac words; packet rows pending the Mac tap — explicit gap, tap specified in §3). Outcomes: §4 (S-STREAM / S-MISSING / S-ORDER / S-DECODE / OTHER, mutually exclusive). Plan/caps: §5 (Mac validation first, ≤1 Android build reserved, ≤1 Odin launch ≤300 s). Risks: §7. Recommended next action (orchestrator decision): gate this design; if accepted, run the Mac tap validation on the pinned N8D4 stream first, then cut the one-launch combined capture/snapshot brief.
