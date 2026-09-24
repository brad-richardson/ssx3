# E55D2 — minimal pad/card guest-write probe map

Read-only audit at fork pin `ddaee780288adb076ce40050d87969b20bc4bb05`
(branch `e55-vblank-hash` in `~/dev/ssx3-work/E55C2/PS2Recomp`; `rev-parse HEAD`
matches; status clean at check). ssx3 checkout `git log -1` at audit time:
`d721653c [orch] Queue E55D2 pad and card probe map` (re-checked at commit time).
No build, boot, device, source edit, web, upstream contact or push in this part.
No determinism claim. Companion receipt: `probe-map.tsv` (8 rows; columns
`candidate,source_anchor,enable_flag,coverage,bytes_per_event,cap,limitation`).

Prior context: `local/research/E55C2/REPORT.md` (DET_HASH tap + 3-boot
observation: idle-1/idle-2 match through tick 2053, loaded through 2052, with
no pad/card rows in any log), `local/research/E55D1/REPORT.md` (pad merges at
guest-read time in `scePadRead`; card completes synchronously into RDRAM),
`local/research/E55D1/ORCH-GATE.md`, E55D2 entry in `docs/todo.md`.
LSP: no usable server in this environment, so caller/callee links rest on
exact line citations below (brief-allowed fallback).

## 1. Why E55C2's logs contain no pad/card rows

E55C2's ON runner was built with `TAPS=ON`
(`~/dev/ssx3-work/E55C2/build.sh on`: `-DPS2X_ENABLE_DIAG_TAPS=ON
-DPS2X_ENABLE_DET_HASH_TAP=ON -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF
-DPS2X_ENABLE_RUNTIME_LOGS=OFF`), so every E3/E44/E41 tap below was compiled
in. But the boot script (`e55c2_boot.py:73-74`) sets only
`PS2X_DETERMINISTIC=1`, `PS2X_DET_HASH_EVERY=1`, `PS2X_PAD_SCRIPT_CLOCK=vsync`
and `PS2X_PAD_SCRIPT`; it never sets `PS2X_E3_INV`, `PS2X_E44_TRACE`,
`PS2X_CD_READ_TRACE` or `PS2X_DIAG_WATCH`. Each of those gates compiles to a
single cached-bool/atomic check when unset (`ps2_e3.h:75-78,627-635`;
`ps2_e44_trace.h:547-551`; `ps2_e41_trace.h:297-306`; `ps2_runtime.cpp:1638-1641`),
so the ON runner paid near-zero overhead and emitted only `[det-hash:v1]`
lines (verified: `run/idle-1/boot.log` lines 67+ are det-hash rows; no
`pad-read`, `mc-read`, `mc-getdir`, `[diag:watch]`, `[padread]`, `plant` or
`spw` lines). Two further rows are dead regardless of env:
`ps2TraceGuestRangeWrite` at `Pad.cpp:1235` (and every other call site) is an
empty inline no-op (`ps2_runtime.h:255-267`, marked TODO-delete), and the
`[padread]` aggressive log (`Pad.cpp:1255-1274`) compiled out because both
builds pass `PS2X_ENABLE_AGRESSIVE_LOGS=OFF` (`ps2_log.h:284` maps
`PS2_IF_AGRESSIVE_LOGS` to `(void)0`).

## 2. Coverage table (detail behind probe-map.tsv)

No existing hook records every successful `scePadRead` 32-byte buffer or every
`sceMcGetDir`/`sceMcRead` guest write through tick 2053 with guest order and a
bounded log. Per candidate:

- **e3-pad-read / e3-mc-getdir / e3-mc-read** (`ps2_e3.h`): master gate
  `PS2X_E3_INV=<u64>` arms only 0x362DE8 render-walker dispatches in
  `[t,t+1]` (`ps2_e3.h:487-533`) — a 2-invocation window unrelated to pad/card
  call frequency. Even inside the window, `tapBegin` returns an inactive tap
  unless armed (`ps2_e3.h:625-635`), and `tapEnd` emits `[e3:r3]` rows only for
  `PS2X_DIAG_WATCH` windows overlapped by the range (`ps2_e3.h:715-728`).
  Guest `dataAddr`/`tableAddr`/`dstAddr` vary per call, so a static watch list
  cannot cover every buffer. Rows carry the shared `seq` + VBlank `frame`
  (`noteVBlank` at `EeScheduler.cpp:2796`) but no pad-read or mc-call ordinal,
  and only 8-byte before/after slices — never the full 32 B / N*64 B / payload.
  Byte cap `PS2X_E3_BYTES` (default 4 MiB, `ps2_e3.h:101-115`) with one
  `[e3:byte-cap]` line then silent suppression (`ps2_e3.h:206-232`).
- **e44-pad-read** (`Pad.cpp:1239` → `ps2_e44_trace.h:724-782`): needs
  `PS2X_E44_TRACE=<file>` plus tick in `[FROM,TO]` (default 1270..1280,
  `ps2_e44_trace.h:350-376`) plus containment of a watched word (8 fixed
  scratchpad words + up to 8 `PS2X_E44_EXTRA` words). Dynamic RDRAM pad buffers
  match only if each future address is pre-listed. Emits word read-backs, not
  the 32 B buffer; 64 lines per watched word; no ordinal.
- **e44-mc-read** (`MemoryCard.cpp:1101-1103`): strictly worse — nested inside
  `if (e3t.active && bytesRead > 0)`, so it is double-gated on the E3 span.
  `sceMcGetDir` has no E44 call at all (only E3 at `841-844` + E41 plant at
  `845-849`), so dir tables have no E44 path.
- **aggressive-padread** (`Pad.cpp:1255-1274`): start-press-gated, 2 payload
  bytes, 48-line cap, no tick/ordinal — and compiled out of the E55C2 runner.
- **e41-plant-pad-card** (`Pad.cpp:1240-1242`, `MemoryCard.cpp:845-849,290-292`
  → `ps2_e41_trace.h:500-572`): watches exactly the 4 render-chain CALL words
  (`kPlantWord`, `ps2_e41_trace.h:114`); pad/card ranges never overlap them, so
  these sites emit zero lines by construction. Cap 40000/file.
- **diag-watch-p1f** (`ps2_runtime.cpp:1546-1641`, reporters only in
  `ps2_runtime_macros.h:544-719` + 2 scheduler tick sites at
  `EeScheduler.cpp:2175,2965`): observes guest-CPU stores only. The pad fill
  (`fillPadStatus` → host write into `getMemPtr` memory), the mc table
  `memcpy` (`MemoryCard.cpp:843`) and the mc `fread` (`MemoryCard.cpp:1095`)
  are host-side fills that never pass through `ps2DiagWatchReport`, so this
  gate yields zero pad/card lines by construction. Uncapped output.
- Reference (not a per-call probe, in prose per brief): the DET_HASH tap
  (`EeScheduler.cpp:199-300,2794-2851`; env `PS2X_DET_HASH_EVERY`, exact
  decimal, invalid/overflow disables with one bounded error; 4096-line /
  256-byte caps) hashes RDRAM+scratchpad+VU1 regions per tick. It explains the
  E55C2 match and why that match cannot attribute a divergence to pad vs card.

Untapped internal counters exist but are never logged: per-port `readCount`
(`Pad.cpp:66,911`) and the E3 shared `seq` domain. Effect on the normal path
when all env is unset: one cached-bool/relaxed-atomic check per call site
(E3/E44/E41/DIAG_WATCH headers as cited); zero guest-visible behavior change.

## 3. Recommendation (one minimal default-OFF edit site pair, not implemented)

One shared bounded seq-stamped byte-dump helper behind a new
`PS2X_PAD_CARD_PROBE=<file>` (empty/unset = today's single-check cost, no I/O;
optional `PS2X_PAD_CARD_PROBE_FROM/TO` tick window and
`PS2X_PAD_CARD_PROBE_BYTES` cap, E3-style single cap line then quiet), called
at exactly two site groups: (a) `scePadRead` post-fill at
`Pad.cpp:1237-1239`, emitting guest vsync tick (already sampled at
`Pad.cpp:895-896`), the port's `readCount` (`Pad.cpp:911`), port/slot/addr/ok
and the full 32 bytes; (b) the two mc payload writes —
`sceMcGetDir` table `memcpy` at `MemoryCard.cpp:843` (tick, per-boot mc-call
ordinal, tableAddr, entryCount, full N*64 bytes) and `sceMcRead` `fread` at
`MemoryCard.cpp:1095` (tick, ordinal, dstAddr, full bytesRead bytes; skip when
bytesRead==0)./Print one line per call with full hex payload: ~120 B + 2 B/byte
(32 B pad ≈ 190 B/line; N-entry dir ≈ 120+128N B/line). Whole-boot volume is
unmeasured (per-call counts through tick 2053 are a gap — no existing counter
logs them), so size the default cap from a first gated run, not from a guess.
No change to merge/fill semantics; helper runs after the bytes are visible.

## 4. Expected observables and first-difference stop rule

- **A/A** (identical pinned inputs, vsync pad script, empty cards at manifest
  `f9401596…`, same `PS2X_DETERMINISTIC`): every pad row byte-identical at the
  same (tick, readCount ordinal), every card row byte-identical at the same
  (tick, mc-call ordinal), through stock race tick 2053; no first difference.
- **pad-B** (wall/live pad or altered script, cards pinned): first difference
  appears in a pad row at some guest read ordinal while all card rows match to
  that point; the next VBlank combined hash diverges at/after that tick.
- **card-B** (one extra file, one-byte edit, or touched mtime in mc0, pad
  pinned): first difference appears in a card row (dir-table bytes incl.
  host-mtime words, or read payload) while all pad rows match; the combined
  hash diverges at/after the first card-touching tick.
- **Stop rule:** stop each comparison at the first differing guest pad or card
  write; record family (pad/card), tick, ordinal, guest address and differing
  bytes; do not run past it for attribution. Either family's null control is
  its own A/A repeat.

## 5. Gaps

(a) Per-call counts/addresses of `scePadRead`, `sceMcGetDir`, `sceMcRead`
through tick 2053 are unmeasured (no boot allowed in this part), so log-volume
estimates above are per-event only. (b) LSP cross-file confirmation
unavailable (no server); links rest on the cited line ranges. (c) Only the
E3/E44/stub/runtime gates and their direct call sites were searched; E50
valwatch, GFX_STATS, VU1/MPEG/CD traces were not evaluated as probe
candidates. (d) The E44 `emitRangeOverlap` linear-space containment
(`ps2_e44_trace.h:724-782`) vs the E3 wrap-safe normalization (`ps2_e3.h:308-353`)
were read, not tested, for aliased pad/card addresses. (e) No boot/build/run
performed; all predictions are source-derived.

## 6. Commands, receipts, sizes

- `git -C ~/dev/ssx3-work/E55C2/PS2Recomp rev-parse HEAD` →
  `ddaee780288adb076ce40050d87969b20bc4bb05`; status clean (no output).
- Reads: `ps2_e3.h` (full, 883 lines), `ps2_e44_trace.h` (§1-1426 + cited
  ranges), `ps2_e41_trace.h` (§1-120, 290-380, 490-574), `Pad.cpp`
  (§60-99, 895-939, 1223-1282 + rg hits), `MemoryCard.cpp` (§820-919,
  1080-1139 + rg hits), `ps2_runtime.h:230-309`, `ps2_runtime_macros.h:14-93`,
  `ps2_runtime.cpp:1546-1705`, `ps2_log.h:255-288`, `EeScheduler.cpp` cited
  lines via rg, `e55c2_boot.py:73-74`, `run/idle-1/boot.log:67-71`.
- `rg` commands (from the fork root): `PS2X_ENABLE_DIAG_TAPS|...` over
  `ps2xRuntime/src/lib` (gate map); `PS2X_[A-Z_0-9]+|diag|...` over
  `Pad.cpp`/`MemoryCard.cpp` (stub gates); `ps2TraceGuestRangeWrite` over
  `ps2xRuntime/{include,src/lib}` (no-op proof); `ps2DiagWatchReport(` over
  `ps2xRuntime` (writer-family proof); `PS2X_ENABLE_DIAG_TAPS` over headers +
  `CMakeLists.txt` (compile gates); `readCount|...` over `Pad.cpp` +
  `EeScheduler.cpp` (ordinal gap).
- Receipt sizes: see `wc -c` at commit time (both short text, well under the
  64 KiB total cap).

## 7. Commit

ssx3 `git log -1` before commit: re-checked per standing rules (several lanes
commit to `main`). Commit `[E55D2]` with trailer `Orchestrated-By: opencode`,
named text receipts only (`local/research/E55D2/REPORT.md`,
`local/research/E55D2/probe-map.tsv`), no push.
