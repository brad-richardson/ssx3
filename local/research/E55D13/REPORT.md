# E55D13 — grounded seeded-card design for reached Load game GetDir (read-only)

Worker: opencode (Muse Spark Contributor Go). Brief: `local/muse/prompts/E55D13.md`.
Read-only source/receipt design. **No source edit, build, boot, card seed/copy,
device action, lease, push, board/global edit, or upstream contact.**
Writes are `local/research/E55D13/REPORT.md` + `check.py` only.
Fork `~/dev/ssx3-work/E55D3/PS2Recomp` @ `bab6eb382673155ffd756fe8db265964eeff9703`
and private lane `~/dev/ssx3-work/E55D12/run/S1/` were read only.
Outcome of this design: **B** — no grounded query/seed exists; one minimal
path-tap design is handed back. A future seeded run is separate and cannot be
released from this design alone. No card-determinism conclusion is made.

## 1. Evidence table (source/receipt pins)

| # | Claim | Evidence (repo source or receipt, exact) |
| --- | --- | --- |
| 1 | E55D12 post-choice GetDir at tick1740, table `0x00ba5b20`, max6, `ok=0 reason=empty`, port0 slot0; four earlier empties at 118/122/126/223, addr `0x00b85660` | `local/research/E55D12/s1-receipts.txt:36-39`; `ORCH-GATE-P2.md:5`; private `~/dev/ssx3-work/E55D12/run/S1/probe.log:3371` `getdir seq=3371 vsync=1740 ord=5 port=0 slot=0 addr=0x00ba5b20 entries=0 max=6 len=0 ok=0 reason=empty bytes=`; early `probe.log:123,132,141,336` same schema at 118/122/126/223 addr `0x00b85660`; `mcread n=0` (`s1-receipts.txt:37`) |
| 2 | Probe records status/bytes but **not rawPath/pattern**: `noteGetDir` carries tick/port/slot/tableAddr/entryCount/max/copied/reason/bytes only | `ps2_e55d3_pad_card_probe.h:287-289` signature `(vsync, port, slot, tableAddr, entryCount, maxEntries, copied, reason, bytes)`; `:307-326` header formats `entries/max/len/ok/bytes`; all six `sceMcGetDir` tap sites in `MemoryCard.cpp:729-730,846-848,864-865,871-872,879-880,887-888` pass those fields and never `rawPath/guestQuery/pattern/hostDir` |
| 3 | `sceMcGetDir` normalizes `mc0:/mc1:`-stripped, `\/`-split, `.`/`..`-resolved query against per-port cwd | `MemoryCard.cpp:211-247` `normalizeGuestMcPathLocked` (`:213` backslash fold, `:215-218` `mc0:/mc1:` strip, `:220-244` absolute-vs-cwd join with `.`/`..` handling); call `:736-737` `normalizeGuestMcPathLocked(port, rawPath.empty() ? "." : rawPath)` with `rawPath` from `:711` `readPs2CStringBounded(..., kMcMaxPathLen)` |
| 4 | hostDir/pattern selection: wildcard split else dir-vs-file probe; empty pattern becomes `*` | `MemoryCard.cpp:738-742` `hasWildcard` + `queryRel`; `:745-766` wildcard→`(parentRel, filename)` else existing-dir→`(queryRel, "*")` else `(parent, filename)`; `:768-771` empty pattern→`"*"`; `:773-778` `hostDir = getMcRootPath(port) [/ parentRel]`; `:781-782` `exists && is_directory` gate; miss→`:879-880` `reason=no-dir` |
| 5 | 64-byte entries: `.`/`..` only on pattern match, case-insensitive sort, pattern filter, `EntryName` at +32, host timestamps | `MemoryCard.cpp:74` `static_assert(sizeof(SceMcTblGetDir) == 64)`; `:315-332` `fillMcDirTableEntry` (Create/Modify, `FileSizeByte`, `AttrFile` readable+writeable+file/subdir+closed+exists, `strncpy EntryName[32]`); `:785-797` `appendSpecial(".")/("..")` gated on `wildcardMatch(pattern, name)`; `:810-816` case-insensitive sort; `:818-824` per-entry `wildcardMatch` filter; `:827-837` isDirectory/size/`last_write_time` with host-now fallback |
| 6 | Copy rule: `entryCount = min(matches, max>0?max:0)`; zero/tableAddr0 writes nothing (`empty`/`bad-addr`); memcpy only on mapped dst | `MemoryCard.cpp:841-842` entryCount; `:843-850` zero-or-null→status-only (`bad-addr` if tableAddr0 else `empty`, result=entryCount); `:851-866` mapped-dst `memcpy` + `ok=1` probe; `:868-874` unmapped→`bad-addr`; other exits `:729-731` `unformatted`, `:887-888` `bad-port` |
| 7 | `PS2X_MC_ROOT` maps mc0/mc1: env root else elfDir/mc0 else cwd/mc0; port1 rewrites `mc0` leaf to `mc1` | `main.cpp:270-276` env→`ioPaths.mcRoot`; `MemoryCard.cpp:119-156` `getMcRootPath` (`:138-141` port≤0→root; `:146-149` leaf `mc0`→`parent/mc1`; `:150-153` empty leaf→`root/mc1`; else `leaf+"_slot"+port`); same fallback in `Syscalls/Helpers/Path.h:84-98` `getConfiguredMcRoot`; Open/Read use the same normalize+host map (`sceMcOpen :1056-1057`, `sceMcRead fread :1136`) |
| 8 | Only grounded save name is `BASLUS-20772` as an ELF string; no payload filenames/sizes/bytes/provenance pinned | `local/research/E55D6/REPORT.md:§1 #6` (`strings SLUS_207.72` → `BASLUS-20772`, `mc0:` only; `SAVEDATA` absent from ELF) + `§4b` (payload filenames/sizes/query unknown); `local/research/E55D7/strings.txt:4` (`BASLUS-20772` file `0x37d3a8`→vaddr `0x47c3a8`); `xref.txt:44`, `at.txt:212` (sole code ref is a string-copy, NOT a card edge per `E55D7/REPORT.md:60`) |
| 9 | `/SAVEDATA/*` + `test.txt` are stub self-test bytes, not game behavior; all card manifests to date are empty | `local/research/E26/e26a-preclaim-suite.txt:740-742,752` (unit-test `SAVEDATA` mkdir/open + `GetDir '/SAVEDATA/*' maxent=8 → 3`); `E55D6/REPORT.md:§1 #6` labels it a stub self-test; `E55D12/s1-receipts.txt:22` + `E55D4/REPORT.md:21-22` manifests `f9401596…ccb9ce`, `mc0/mc1: []` |
| 10 | Checker | `local/research/E55D13/check.py` re-verifies #1–#9 pins; states source strings cannot prove guest behavior |

## 2. Candidate/alternative matrix

| Candidate | Exact guest path/pattern + host bytes pinned? | Verdict |
| --- | --- | --- |
| A — already-grounded minimal seed (exact query + host bytes from source/receipt) | No. Query side: rawPath/pattern unlogged (#2), per-call `maxEntries`/tableAddr unknown before the run (post-choice max6 is observed once, not a rule). Content side: only the folder *name* `BASLUS-20772` is grounded (#8); no file list, sizes, payload bytes, or provenance exists in any receipt (#8–#9). A `mc0/BASLUS-20772/` + invented file would be an invented save, forbidden by the brief | **Not met** |
| B — missing query-path observation | Yes: this is the grounded reading. All five GetDir lines are status-only `reason=empty` (#1); the tap structurally cannot report what was asked (#2); no receipt supplies the missing pattern or a valid save image (#8–#9) | **Holds: outcome B** |
| OTHER — receipt/source pin mismatch | No mismatch found: receipts match the five private probe lines; source anchors match E55D1/E55D6 line ranges modulo the `bab6eb3` SEM1 shift | Not taken |

Do not invent the requested pattern. Do not claim a random file is a valid SSX 3 save.

## 3. Minimal path-tap design (NOT implemented here)

Goal: answer "what did tick1740 ask?" with the smallest dev-only, default-off
change to the existing E55D3 probe, zero guest bytes/results change.

- Reuse the master gate `PS2X_PAD_CARD_PROBE=<file>` (unset/empty = today's
  single-atomic cost, no I/O). No new env var: the extra line is emitted only
  when the probe is already armed, so default-off is inherited.
- New line family `getdirpath` in `ps2_e55d3_pad_card_probe.h`, mirroring the
  existing cap/flush conventions: `getdirpath seq=<s> vsync=<t> pord=<p>
  port=<p> slot=<sl> max=<m> rawLen=<r> raw="<esc>" query="<esc>"
  parent="<esc>" pattern="<esc>" host="<esc>"` with backslash-escape of
  `\ "`, non-printables as `\xHH`, each field capped (raw ≤1024 already by
  `kMcMaxPathLen`; escaped line ≤ ~5 KiB), whole-or-nothing against the same
  16 MiB `kByteCap`+`kCapReserve`, one `cap` line then permanent disarm, flush
  every 16. Shared `seq` for ordering, **own `pord`** so existing per-family
  `ord` (asserted 1..5 by `check-p2.py`) is undisturbed.
- Single call site in `sceMcGetDir` after `hostDir` is resolved
  (`MemoryCard.cpp` after `:778`), plus the same call on the early
  `unformatted`/`bad-port` exits so an `empty`/`no-dir` answer still logs its
  question. Read-only: captures `std::string`s, never touches RDRAM, return
  values, `sceMcSync` results, or sort/order. Disabled cost: one `armed()`
  relaxed-atomic (the existing gate), no string build.
- Why not extend the `getdir` line instead: changing its header breaks every
  existing checker (`check-p2.py` asserts exact `ord`/suffix framing); a
  sibling line is a smaller diff and keeps A/A comparability.
- One-run receipt gate (future, unexecuted): rebuild the E55D3 taps runner
  only, re-pin runner SHA with two reads, rerun the exact E55D12 S1
  script/route/cards/lease/caps, require the same 5 `getdir` lines plus 5
  `getdirpath` lines with identical `(raw, query, parent, pattern, host, max)`
  on a same-scene empty-card A/A before any seeded run. Any guest-byte,
  result, or `ord` drift voids the tap.

## 4. Predeclared future controls (NOT run; need the §3 tap first)

- Null A/A: two boots, same binary/ISO/ELF/codegen SHAs, same E55D12
  route/ticks, same empty manifest `f9401596…ccb9ce`, same scene
  (Save/Load submenu → Load game → MEMORY CARD slot1), same probe. Require:
  identical 5 `getdir` ticks/addrs/max/reasons (118/122/126/223 @
  `0x00b85660`, ~1740 @ `0x00ba5b20`, max6, `reason=empty`, `mcread n=0`) and
  identical 5 `getdirpath` queries; frame proof ≥1800 each side. Empty answers
  copy zero bytes, so host timestamps cannot couple — exact match is required.
- Changed-card run: same binary/script/scene, one seeded input (designed only
  after §3 reveals the query; no seed is designed here). Observable is the
  post-choice (`vsync ≥ 1700`) `getdir` line flipping `ok=0 reason=empty
  len=0` → `ok=1 len=<entryCount*64> bytes=<hex>` with `entryCount ≤ max`
  64-byte records (`SceMcTblGetDir`: +0 Create 8B, +8 Modify 8B, +16 size 4B,
  +20 AttrFile 2B incl. file/subdir bits, +32 EntryName 32B). `.`/`..` lead
  only if the revealed pattern matches them; `BASLUS-20772` appears only on a
  matching pattern. Timestamp bytes (Create/Modify, mtime fallbacks) and
  host sort ties are excluded from equality (compare EntryName+Attr+size);
  record order follows the runtime's case-insensitive sort. Same
  `getdirpath` query with differing table bytes = content signal; shifted
  tick with still-empty answer = menu-timing signal, not content.

## 5. Exact unexecuted patch/command plan

1. Patch (future diff, not applied): `ps2_e55d3_pad_card_probe.h` add
   `noteGetDirPath()` (~40 lines, §3 schema); `MemoryCard.cpp` add one armed
   call after `:778` + two early-exit calls; `ps2_e55d3_probe_tests.cpp` add
   escaping/cap/ord-stability tests. No guest-write, result, or scheduler edit.
2. Build: E55D3 worktree taps runner rebuild only; two SHA reads of the new
   runner; runner-dir guard stays clean.
3. Run (one, after orchestrator release): `python3
   local/research/E55D12/e55d12_boot.py --label S1` pattern reuse with the new
   runner pin, empty cards, slot-lease discipline, 500 s/120 s/16 MiB/2 GiB
   caps, frame proof ≥1800. Then the §4 null A/A second boot; seeded run only
   after both.
4. Receipts: `getdirpath` lines + unchanged `getdir`/`mcread` counts; checker
   asserts query identity (§4). Stop at first `getdirpath` mismatch (void) or
   first table-byte difference (signal).

## 6. Stop/cost rules

- Stop on: first failure (save error text to this REPORT's gaps and hand
  back); any guest-byte/result/`ord` drift from the tap; any card seed/copy
  (forbidden in this design); >25 min box; committed text >512 KiB (this dir
  is ~20 KiB); any second boot/build without a new release.
- Cost: zero boots/builds/runs in this part (`Boots/builds/runs: 0`).

## 7. Gaps (stated plainly)

- The tick1740 guest query (raw/pattern/parent/host) is unobserved — the
  question this design exists to answer (§3).
- No valid SSX 3 save layout/bytes/provenance exists in evidence; even with
  the query known, seed validity (icon.sys, file set, sizes, timestamps the
  game accepts) is a separate unblocking item.
- `sceMcGetInfo`/HLE-gate alternative (E55D6 §2A.5) stays untested; the path
  tap does not cover it.
- Tick tags remain snapshotter-approximate (E55D12 §5); the 1740-vs-C2 gap
  (40 ticks) is probe-exact, the frame tags are not.
- Source strings and empty-card receipts cannot prove guest behavior
  (`check.py` asserts pins only).

## 8. Commands run (read-only; no boot/lease/build/seed)

- Read: brief, repo `AGENTS.md`, `local/AGENTS.local.md`, E55D12 full
  `REPORT.md`/`ORCH-GATE-P2.md`/`s1-receipts.txt`/`check-p2.py`, E55D3
  `REPORT.md`, E55D4 `REPORT.md`, E55D6 `REPORT.md`, E55D7 `strings.txt`/
  `xref.txt`/`at.txt` excerpts, E55D8 `REPORT.md` (§1), E26 suite excerpt.
- `rg` over `MemoryCard.cpp`/`main.cpp`/`Path.h` for `mcRoot|PS2X_MC_ROOT`;
  `rg getdir` over private `probe.log` (5 lines) and E55D11 `probe.log` (4 lines).
- Full reads: `MemoryCard.cpp:1-1311` (GetDir/Open/Read/normalize/map),
  `ps2_e55d3_pad_card_probe.h` (full, 469 lines), `main.cpp:255-295`,
  `Path.h:80-100`.
- `python3 local/research/E55D13/check.py` → PASS (see §1 #10).
- `git log -1`, `git status`, stage named paths only, commit `[E55D13]`
  with `Orchestrated-By: opencode`, no push.

Base commit: `6769ffe71104966c25aba725852cde70f431a95f`.
Boots/builds/runs: 0. Recommended next action: orchestrator reviews this
design; if accepted, release a tap-only build + one path-tap run (§3+§5)
before any seed is designed.
