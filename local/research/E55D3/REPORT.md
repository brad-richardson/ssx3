# E55D3 — bounded ordered pad/card guest-write tap

Worker: opencode. Fork worktree `~/dev/ssx3-work/E55D3/PS2Recomp`, branch
`e55d3-pad-card-tap`, from exact `ddaee780288adb076ce40050d87969b20bc4bb05`.
E55C2 worktree untouched (still `e55-vblank-hash`, clean). External codegen
`~/dev/ssx3-work/codegen-ssx3` (`register_functions.cpp` SHA
`8ea8ed43…688a3`, re-verified after the work). No generated guest source in
git. No boot, no device, no upstream contact, no push.

Prior context: `local/research/E55D1/REPORT.md` (+ `ORCH-GATE.md`),
`local/research/E55D2/REPORT.md` (+ `ORCH-GATE.md`), E55D3 entry in
`docs/todo.md`. One named semantic repair applied on orchestrator review
(`E55D3-SEM1`): ferror-with-bytes now keeps the payload with `err=io-error`,
and the three outer `sceMcGetDir` exits are tapped.

## 1. Evidence table

| Item | Value |
| --- | --- |
| Fork branch / commit | `e55d3-pad-card-tap` / `bab6eb3` (see §4) |
| Fork base (exact) | `ddaee780288adb076ce40050d87969b20bc4bb05` |
| ssx3 receipts commit | this commit (`[E55D3]`, trailer `Orchestrated-By: opencode`, no push) |
| Build config | Release/Ninja, `~/dev/ssx3-work/E55D3/build-taps`, E55C2 `build.sh on` flags verbatim + pinned `_deps` dirs (`~/dev/ssx3-work/E50/build/_deps`), `PS2X_GAME_CODEGEN_DIR=~/dev/ssx3-work/codegen-ssx3`, LLVM clang 23.1.1 |
| Configure | exit 0 (`cmake-on.log`) |
| Build (`ps2x_tests`, `ps2EntryRunner`) | exit 0 first build (`build-on.log`); exit 0 SEM1 rebuild (`build-on-sem1.log`) |
| Full suite, flag unset | 686/687 (`suite-on.log`); 3/3 new `Ps2E55D3Probe` pass; 1 failure is a CWD artifact (see §6) |
| `PS2X_PAD_CARD_PROBE` during suite | unset (verified in run command); no `*probe*`/`*PAD_CARD*` file under `build-taps`, no `/tmp/ps2x-e55d3*` remains |
| `git diff --exit-code 14b1e5cb HEAD -- ps2xRuntime/src/runner` | clean (exit 0) |
| Disk 200 GiB cap before / after | 141.3 GB / 143.0 GB (`disk_budget.sh`); free 106 Gi |
| No generated/binary files staged | fork status shows only the 6 intended source files (§2) |
| New E55D3 bytes / text receipts | 1.7 GiB dir (< 5 GiB) / this REPORT only, ~9 KiB (< 512 KiB) |

## 2. Changed files (E55D3 owns only these + necessary CMake/tests)

| File | Change |
| --- | --- |
| `ps2xRuntime/include/ps2_e55d3_pad_card_probe.h` | NEW (~430 lines): shared default-OFF tap, see §3 |
| `ps2xRuntime/src/lib/Kernel/Stubs/Pad.cpp` | +12: include, tick sample, `notePad` on bad-addr skip and post-fill (ok + closed) |
| `ps2xRuntime/src/lib/Kernel/Stubs/MemoryCard.cpp` | +52: include, tick samples, `noteGetDir` on all 6 exits, `noteMcRead` on all 7 exits |
| `ps2xTest/src/ps2_e55d3_probe_tests.cpp` | NEW: disabled-path + cross-family ordering + tiny-cap runs |
| `ps2xTest/CMakeLists.txt`, `ps2xTest/src/main.cpp` | register the test under `PS2X_ENABLE_DIAG_TAPS` |

No guest writes, results, timestamps, pad merge, or thread scheduling
changed: every tap call is read-only, after the bytes are visible, and a
single relaxed-atomic no-op when the flag is unset/empty. Card taps sit
inside the existing `g_mcStateMutex` scope exactly like the pre-existing
E3/E41 taps; disabled cost is one atomic check.

## 3. Record schema + cap semantics

Master gate `PS2X_PAD_CARD_PROBE=<file>`; unset/empty = one relaxed atomic
per call, no file I/O, no payload scan. One process-local log; a single
leaf mutex protects shared `seq`, per-family `ord`, and file writes.

- `pad seq=<s> vsync=<t> ord=<padOrd> port=<p> slot=<sl> addr=0x<8x> len=32 ok=1 bytes=<64 hex>`
- `pad ... len=0 ok=0 reason=<bad-addr|closed> bytes=` (empty)
- `getdir seq=<s> vsync=<t> ord=<dirOrd> port=<p> slot=<sl> addr=0x<8x> entries=<n> max=<m> len=<64n> ok=1 bytes=<hex>`
- `getdir ... entries=<n> max=<m> len=0 ok=0 reason=<bad-port|unformatted|no-dir|empty|bad-addr> bytes=` (empty)
- `mcread seq=<s> vsync=<t> ord=<readOrd> fd=<f> addr=0x<8x> req=<q> len=<a> ok=1 err=<-|io-error> bytes=<hex>`
- `mcread ... req=<q> len=<a> ok=0 reason=<zero-size|bad-fd|bad-addr|eof|io-error> bytes=` (empty)
- `cap seq=<s> vsync=<t> bytes=<written> msg=byte-cap-reached`

`seq` is shared across all families (cap line included); `ord` counts every
call of its family including skip/fail lines. One line per record, hex has
no whitespace, every line newline-terminated. Hard cap 16 MiB with a
256-byte reserve for the cap line: a record that would overflow triggers
exactly one `cap` line instead and permanently disarms the tap; a payload
record is written whole or not at all. File total never exceeds 16 MiB.
Flush every 16 lines and on the cap line. `vsync` is the GS vsync tick (the
clock the vsync pad script uses), sampled once per stub call; null runtime
in tests records 0.

## 4. Source patch and fork commit SHA

Fork commit `bab6eb3` on `e55d3-pad-card-tap` (`[E55D3]`, trailer
`Orchestrated-By: opencode`, no push): the 6 files of §2 only.
`git diff --stat`: `MemoryCard.cpp +52, Pad.cpp +12, CMakeLists +1,
main.cpp +2`, plus the 2 new files. Pre-SEM1 build also passed; SEM1 is
included in `e2fbc53` (ferror payload + 3 outer getdir taps + `err` field).

## 5. Exact coverage table (every stub exit → probe record)

scePadRead:

| # | Exit path | Guest bytes? | Probe record |
| --- | --- | --- | --- |
| P1 | `data==nullptr` (bad addr), ret 0 | none | `pad ok=0 reason=bad-addr` |
| P2 | port closed (`readPadPortData` false), ret 0 | none | `pad ok=0 reason=closed` |
| P3 | success, ret 1 | 32 B fill | `pad ok=1` + full 64 hex |

sceMcGetDir (ret is always 0 dispatched; result via `sceMcSync`):

| # | Exit path | Guest bytes? | Probe record |
| --- | --- | --- | --- |
| G1 | bad port/slot | none | `getdir ok=0 reason=bad-port entries=0` (SEM1) |
| G2 | card unformatted | none | `reason=unformatted` (SEM1) |
| G3 | host dir missing/not-a-dir | none | `reason=no-dir` (SEM1) |
| G4 | `entryCount==0` or `tableAddr==0` | none | `reason=empty` (`tableAddr==0` → `bad-addr`) |
| G5 | table `memcpy` ok | `entryCount*64` B | `getdir ok=1` + full hex |
| G6 | `tableAddr` unmapped | none | `reason=bad-addr` |

sceMcRead:

| # | Exit path | Guest bytes? | Probe record |
| --- | --- | --- | --- |
| R1 | `size<=0` | none | `mcread ok=0 reason=zero-size` |
| R2 | unknown/closed fd | none | `reason=bad-fd` |
| R3 | `dstAddr` unmapped | none | `reason=bad-addr` |
| R4 | `fread` clean, `bytesRead>0` | full payload | `mcread ok=1 err=-` + full hex |
| R5 | `bytesRead>0` with `ferror` set | payload IS in RDRAM | `mcread ok=1 err=io-error` + full hex (SEM1; was status-only) |
| R6 | `bytesRead==0`, clean (EOF) | none | `ok=0 reason=eof` |
| R7 | `bytesRead==0` with `ferror` | none | `ok=0 reason=io-error` |

Out of scope by brief: `scePadPortOpen`'s 32-byte zero fill is not a
`scePadRead` fill and is not tapped; `sceMcWrite`/`sceMcGetInfo` guest
writes are not in the three families.

## 6. Build/config/suite result

- Configure: exit 0 (flags == E55C2 `build.sh on`, CODEGEN pinned,
  `_deps` pinned; `register_functions.cpp` SHA re-verified `8ea8ed43…688a3`).
- Build `ps2x_tests` + `ps2EntryRunner`: exit 0 (576 steps); SEM1 rebuild:
  exit 0 (8 steps). Only warnings: pre-existing `ld: ignoring duplicate
  libraries`.
- Suite with flag unset: **686/687**. All `PadInput`, `PS2RuntimeIO`, and
  3/3 new `Ps2E55D3Probe` runs pass. The single failure (`VU0 macro
  mappings cover all S1/S2 enums`, `code_generator_tests.cpp:1149`) reads
  `instructions.h` from CWD-relative candidates
  (`ps2xRecomp/…`, `../ps2xRecomp/…`, `../../ps2xRecomp/…`); the suite was
  run from `build-taps/`, which matches none, while the file exists at the
  fork root (candidate 1 needs CWD = fork root). Pre-existing test,
  untouched by this diff (no codegen paths modified); total 687 = 684
  pre-existing + 3 new. No budget remains for a corrected-CWD rerun, so
  this stands as reported.
- Focused test (structural only, no encoder logic copied): disabled stub
  call writes no file; pad→getdir→mcread yield `seq` 1,2,3 in call order
  with nonempty `bytes=`; 600-byte cap yields ≥1 full pad line, exactly one
  trailing `cap` line, file ≤ cap, newline-terminated.

## 7. Untested live-coverage gaps

- No boot in this part: whole-boot call counts and log volume through race
  tick 2053 unmeasured; the 16 MiB cap is analysis-sized, not measured.
- Pinned vsync-pad/empty-card A/A, pad-B, and card-B comparisons not run.
- Concurrent-call interleave never observed (stubs run on the EE executor;
  the leaf lock is present but uncontended in tests).
- R5 (`err=io-error` with payload), G1/G2/G3, R6/R7 paths covered by code
  review only — no deterministic unit trigger.
- `vsync` is 0 in all unit tests (null runtime); production tick wiring
  (GS `vsyncTick`) is live-code only.
- Cap behavior proven at 600 B, not at 16 MiB.

## 8. Commands

- `git -C ~/dev/PS2Recomp worktree add ~/dev/ssx3-work/E55D3/PS2Recomp -b e55d3-pad-card-tap ddaee780288adb076ce40050d87969b20bc4bb05`
- `sha256sum ~/dev/ssx3-work/codegen-ssx3/register_functions.cpp` → `8ea8ed43…688a3`
- cmake configure (E55C2 `on` flags, `OUT=~/dev/ssx3-work/E55D3/build-taps`) → exit 0
- `cmake --build … --target ps2x_tests ps2EntryRunner` → exit 0; SEM1 rebuild → exit 0
- `(unset PS2X_PAD_CARD_PROBE; ./ps2xTest/ps2x_tests)` from `build-taps` → 686/687
- `git diff --exit-code 14b1e5cb HEAD -- ps2xRuntime/src/runner` → clean
- `local/tooling/disk_budget.sh` → 141.3 GB before, 143.0 GB after (cap 200 GB)
- `git log -1` checks before both commits (several lanes commit to `main`)

## 9. Commits

- Fork: `bab6eb3 [E55D3]` on `e55d3-pad-card-tap` with `Orchestrated-By:
  opencode`, no push.
- ssx3: `[E55D3]` with the same trailer, no push (this REPORT plus the
  brief `local/muse/prompts/E55D3.md`, both force-added).
