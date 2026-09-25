# MC1 — does saving work, and is Brad's save safe?

Worker: Muse. Brief: `local/muse/prompts/MC1.md`. Mac mini, scratch copies
only; Brad's save bytes never in git (names, sizes, SHAs only). No fork
push, no upstream contact. Runner-dir check empty (before any push).

Outcome: **the game never wrote in 4/4 boots, and the write trigger is now
identified.** Across three seeded full Happiness races plus an empty-card
race (~85k guest ticks through results, the Replay viewer, the Records
screen and Restart dialogs), SSX 3 issued **zero** `sceMcOpen-WRITE`,
`Write`, `Mkdir`, `Delete`, `Seek` or `SetFileInfo` calls: all card traffic
is boot autoload (ticks 0–258), then silence. Every run card is
bit-identical to its before-state: nothing truncated, zero-filled or
created oddly, and the pristine sources verify 6/6. So **Single Event play
does not touch Brad's save** — but Q1's live write path, Q2's round trip
and Q4's failure mode are **untested**, and Q3's create flow only partly.
B6 found the trigger: the Records screen has a **`Save Records` row** (one
down past Return); my crosses hit Return instead. A follow-up needs one
boot down that row, then a reload boot. No source fix (no mechanism named:
no bug seen, only an unreached screen).

## 1. Base and pins

Branch `mc1-save` (local worktree `~/dev/ssx3-work/MC1/PS2Recomp`, not
pushed): fork `ssx3` tip `8559ab9` + PF1's fix `3c037ab` cherry-picked
cleanly as `fa775f8` (test file auto-merged; no other conflicts).

| Item | Pin | Receipt |
|---|---|---|
| Fork source | `fa775f8` = `8559ab9` + PF1 `3c037ab` | `git log` worktree; `MemoryCard.cpp` identical to `fork/ssx3` |
| paraLLEl-GS (+Granite) | `19d93b2` (`166ba21a`) | copy of F2's tree, clean |
| Canonical codegen | `register_functions.cpp` `8ea8ed43…62d688a3` | two SHA reads per boot |
| ISO / ELF | `3c2f8eb1…61ebf5` / `1b49d05c…67af7bc` | two SHA reads per boot |
| Runner `bin/runner-mc1` | `4a0b4c6b…70dd8` (×2), 135,356,992 B | copy-out + two reads |
| Build | Release, Homebrew clang, `PS2X_GS_SHADOW_PARALLEL=ON`, TEST ON, RUNTIME_LOGS ON, AGGRESSIVE/DIAG_TAPS/DET_HASH OFF | `configure rc=0`, `build rc=0` 630 steps |
| Suite | **647/647** from the worktree root (incl. the PF1 unwind test) | `suite2.log` (first run 646/647: one cwd-dependent VU0-enum test needs the worktree root) |
| `[gs-path]` all boots | `hier-if-large … desc=plain … gpu=Apple M5 Pro` | `result.json` each run |

Common env: `PS2X_GS_BACKEND=parallel`, `GRANITE_VULKAN_LIBRARY=
/opt/homebrew/lib/libvulkan.1.dylib`, `PGS_HIER_BINNING=force`,
`PS2X_SOUND=1` (48 kHz live all runs), `PS2X_SKIP_MOVIE=1` (dev-only),
`PS2X_DETERMINISTIC=1`, vsync pad clock, `PS2X_MISSING_FUNCTION_POLICY=stop`,
`PS2X_VSYNC_RATE_LOG=1`, frame dumps + 15 s snapshotter. One mini slot per
boot. **No speed claims** (RUNTIME_LOGS build).

Observability note: `PS2X_TRACE_SYSCALLS` does **not** cover `sceMc*` —
they are HLE stubs (`MemoryCard.cpp`), not numeric EE syscalls (the trace
emits only from `dispatchNumericSyscall`, `Dispatcher.cpp:93`). The
observable used is the MC HLE log (`RUNTIME_LOGS=ON`): `[MC] Sync cmd=N
result=R` for every completed command (cmd 1 GetInfo, 2 Open, 3 Close,
4 Seek, 5 Read, 6 Write, 10 Flush, 11 Mkdir, 12 Chdir, 13 GetDir,
14 SetFileInfo, 15 Delete, 16 Format, 17 Unformat, 18 GetEntSpace,
19 Rename; results 0 OK / positive bytes-fd-count / −1 changed / −2
noformat / −4 noentry / −5 denied / −6 notempty / −7 handle-limit;
`MemoryCard.cpp:11-34`), plus GetDir/Chdir/GetInfo detail lines. Ticks are
last-`[vsync-rate]`-before-line (±~100t; log lines concatenate, so the
parser scans whole-text offsets). Open/Write/Close/Mkdir/Delete log no
path/flags/size — attribution comes from call order + the host-side diff.

## 2. Boots (4/4 used)

Seeded routes shift FR1-R1 by +4438 ms (+266 ticks) for the seeded title
delay (I31 §5); the shifted prefix is byte-equal to FR1-R1 unshifted
(driver self-check). Seeded races reproduce: B1/B5/B6 all finish Mac
04:31, 2nd to Griff 03:15, results fresh ~18665t.

| Boot | Card | Route (entries) | Result |
|---|---|---|---|
| B1-seed | scratch seed copy | r1seed: FR1-R1 shifted + 12 post crosses (42) | target t20606, 1222 s; crosses hit Restart (default row) → Restart-confirm loop; **no writes** |
| B3-empty | empty | r1empty: FR1-R1 + 12 post crosses (42) | target t20266, 1238 s; Zoe 04:01 2nd; same Restart loop; **nothing created** |
| B5-saveflow | scratch seed copy | r1save: shifted + Replay probe + normalize + Records attempt (47) | target t23310, 1262 s; Replay **viewer** entered (cross=play/pause, circle=slow motion — circles never exit); Records never reached; **no writes** |
| B6-quit | scratch seed copy | r1quit: shifted + down,down,cross + crosses + circle,up,up,down×4 + crosses (51) | target t24236, 1278 s; **Records reached**: "Top 5 Record Times" (Brad's table) with rows Return (highlighted) / **Save Records**; crosses took Return; late nav cycled the Restart dialog (menus **wrap**: up from top → bottom); **no writes** |

All boots: zero FATAL, `targets=0`, E56 four RPCs, sound live, every pad
press fired (`press i=0..N` + releases). B1/B3 ran parallel (slots 3/2);
B5/B6 solo (slots 1/1). RP1 held slot 1 during B1/B3.

## 3. Q1 — write path: no mutating call in any boot

Completed-command counts from the `[MC] Sync` log (all at ticks 0–258;
**zero** card calls after tick 258 in any boot):

| Boot | GetInfo | GetDir | Open | Read | Close | Seek/Write/Mkdir/Delete/… |
|---|---|---|---|---|---|---|
| B1-seed | 26 OK | 12 →1, 2 →0 | 6 (fds 1–6) | 964×4, 3276, 39777 | 6 OK | 0 |
| B5-saveflow | identical to B1 (58/58) | | | | | 0 |
| B6-quit | identical to B1 (58/58) | | | | | 0 |
| B3-empty | 14 OK | 4 →0 | 0 | 0 | 0 | 0 |

Seeded GetDirs: `SET*`→1, `GAM*`→1 (×2 each), both data files + both
`ssx1.ico` →1, `REP*`→0 ×2 — the E55D16 autoload shape, every file read at
its exact size. So the game reads the scratch seed fully and correctly,
then never touches the card through: results idle (B1), Restart dialogs
(B1/B3/B6), the Replay viewer incl. play/pause/camera (B5), the Records
table display (B6). It does not auto-save Single Event results — not even
on the empty card, where any finish would be a first record.

Before/after (before = pristine seed SHAs, verified 6/6 after all runs;
E55D16 original re-read, SHAs match its pins):

| File | Size | SHA-256 | After B1/B5/B6 |
|---|---|---|---|
| `BASLUS-20772-GAM0001/BASLUS-20772-GAM0001` | 39777 | `4bdaee79…7b78e` | unchanged ×3 |
| `BASLUS-20772-GAM0001/icon.sys` | 964 | `eab22574…0a49c` | unchanged ×3 |
| `BASLUS-20772-GAM0001/ssx1.ico` | 73144 | `5f8b5a92…fc0b` | unchanged ×3 |
| `BASLUS-20772-SET0001/BASLUS-20772-SET0001` | 3276 | `4a31a2d7…002f1` | unchanged ×3 |
| `BASLUS-20772-SET0001/icon.sys` | 964 | `dddf2d9c…ee13` | unchanged ×3 |
| `BASLUS-20772-SET0001/ssx1.ico` | 73144 | `5f8b5a92…fc0b` | unchanged ×3 |

No truncation, no zero-fill, no odd creations; mtimes untouched. B3's card
holds 0 files after the run.

Write-path code map (for the follow-up that reaches Save Records;
`MemoryCard.cpp` on `mc1-save`, identical to `fork/ssx3`): open-mode fold
`openMcHostFile` :442-487 (`fopen` :486; WRONLY+existing+no-TRUNC opens
`r+b`, offset 0, no truncate); `sceMcOpen` :1006-1067 (`fopen` fail →
−4/−5 at :1048-1052); `sceMcWrite` :1305-1345 (`fwrite` :1330 + `fflush`
:1334, ferror → −5 :1331); `sceMcClose` :573-591; `sceMcMkdir` :962-1004;
`sceMcDelete` :593-639; Sync delivery + log :1226-1273. Failure mode is
always a Sync error code in the immediate model — no path blocks or
retries, so our side cannot hang Q4's game (game-side reaction untested).

## 4. Q2/Q3/Q4 — verdicts

- **Q2 round trip: untested** (nothing was ever written; no gap in the
  method, just no input). Would-be route: menu boot on the written copy.
- **Q3 empty card: partial.** The game offers nothing and creates nothing
  through Single Event results + Replay-viewer flows (B3: 18 syncs, all
  GetInfo/GetDir→0). Whether it offers to create down the Save Records row
  is open — same follow-up boot as Q1 but on an empty card.
- **Q4 read-only dir: untested** (no write attempt to fail). Code says the
  game sees −4/−5 via Sync (`:1048-1052`, `:1331`); hang-vs-dialog is the
  open question. Same follow-up boot with the card chmodded a-w.

## 5. Screens viewed (all in scratch; receipts below are worker-viewed)

Results ×4 (B1 18686, B3 17844, B5 18665, B6 19055/19769: "Sorry, you
didn't win.", rows Next event/Restart/Replay/Records/Quit, Restart
default); racing ×4 (mid/finish, both cards); Replay viewer ×3 (B5 19479,
20599, 21879: timeline + camera help, no save row); **Records ×1 (B6
19363: Top 5 Record Times, Return highlighted, Save Records below)**;
Restart dialog ×3 (B1 20487, B6 20068/24236: "Are you sure? Yes/No", No
highlighted = the dialog loop end state); B6 20906 (panel-fade backdrop,
re-examined — not a restarted race).

## 6. Recommended next action (follow-up lane, ~2 boots + short reloads)

The trigger is one row below where B6's crosses landed. Boot 1 (seeded,
same build): FR1-R1 shifted prefix, then at results (~18665t, Restart
highlighted): down,down,cross (Records), down (→Save Records), cross,
then crosses every ~300t ×8 to answer the prompt; screenshots + `[MC]`
log + before/after diff = Q1. Boot 2: short menu boot on the written copy
(Q2: no-corruption prompt + updated table). Boot 3 (empty card, same nav):
Q3 create. Boot 4 (seeded chmod a-w, same nav): Q4. Menu-selection
wrap-around is confirmed (B6 end state), so normalize with ups carefully.
A unit test of `sceMcOpen-W/C/T` + `Write` + `Close` + `Mkdir` round-trip
against a tmpdir would pin the HLE half independently of the game.

## 7. Commands, budget, receipts

```sh
git -C ~/dev/PS2Recomp worktree add ~/dev/ssx3-work/MC1/PS2Recomp -b mc1-save fork/ssx3
git -C ~/dev/ssx3-work/MC1/PS2Recomp fetch ~/dev/ssx3-work/PF1/PS2Recomp pf1-postrace
git -C ~/dev/ssx3-work/MC1/PS2Recomp cherry-pick 3c037ab   # -> fa775f8, clean
cp -a ~/dev/ssx3-work/F2/parallel-gs ~/dev/ssx3-work/MC1/parallel-gs  # 19d93b2
cp -pR ~/dev/ssx3-work/E55D16/mc0 ~/dev/ssx3-work/MC1/mc0-seed        # scratch only
cmake -S PS2Recomp -B build -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER=/opt/homebrew/opt/llvm/bin/clang \
  -DCMAKE_CXX_COMPILER=/opt/homebrew/opt/llvm/bin/clang++ \
  -DPS2X_GAME_CODEGEN_DIR=/Users/brad/dev/ssx3-work/codegen-ssx3 \
  -DPS2X_BUILD_TEST=ON -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_DEBUG_UI=OFF \
  -DPS2X_ENABLE_RUNTIME_LOGS=ON -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF \
  -DPS2X_ENABLE_DIAG_TAPS=OFF -DPS2X_ENABLE_DET_HASH_TAP=OFF \
  -DPS2X_GS_SHADOW_PARALLEL=ON \
  -DPS2X_PARALLEL_GS_SOURCE_DIR=/Users/brad/dev/ssx3-work/MC1/parallel-gs \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake --build build --parallel 8 --target ps2EntryRunner ps2x_tests
./build/ps2xTest/ps2x_tests                      # from the worktree root: 647/647
python3 mc1_boot.py --route r1seed --mcmode seed --runner bin/runner-mc1 \
  --label B1-seed --wall 1800 --coverage-tick 16000 --stop-tick 20500
python3 mc1_boot.py --route r1empty --mcmode empty --runner bin/runner-mc1 \
  --label B3-empty --wall 1800 --coverage-tick 16000 --stop-tick 20200
python3 mc1_boot.py --route r1save --mcmode seed --runner bin/runner-mc1 \
  --label B5-saveflow --wall 1800 --coverage-tick 16000 --stop-tick 23200
python3 mc1_boot.py --route r1quit --mcmode seed --runner bin/runner-mc1 \
  --label B6-quit --wall 1800 --coverage-tick 16000 --stop-tick 24200
python3 mc1_analyze.py run/<label>                # tick-correlated [MC] + mc0 diff
```

Budget: 1 build, 4 boots, ~2 h of 2.5. Never pushed. Text in git:
`REPORT.md`, `mc1_boot.py`, `mc1_analyze.py`. Scratch `~/dev/ssx3-work/MC1`
(~6 GB: build + parallel-gs + runs + seed copies; run cards hold only
scratch bytes).

## 8. Gaps

- No live write observed, so Q1's call sequence, Q2, Q4 and the Q3 create
  flow are open; the Save Records row + wrap behavior de-risk the retry.
- Tick correlation ±~100t (rate-line interleave; early-boot lines read 0).
- Open/Write/Close/Mkdir/Delete log no path/flags — a follow-up that
  reaches Save Records attributes the file by order + diff.
- B6's late path (Quit-row attempt) is reconstructed, not shot-by-shot
  certain; the wrap inference rests on the end-state dialog.
- `mc1_boot.py`'s first B1 launch crashed on a bad `shutil.copytree`
  kwarg (fixed; the empty-mode B3 was unaffected).

## Orchestrator gate, Part 1 (2026-09-25)

**Accepted.** Single Event play issues zero card writes (4 boots, ~85k ticks); every card copy is
bit-identical after. The write trigger is the Records screen's `Save Records` row. Part 2 released: one
boot that selects it on a scratch copy of Brad's save (write path, host file changes), one reload boot
(round trip), and the read-only-dir failure mode.

## Part 2 — saving works (delete + recreate, "Save complete."); reload + write-failure open

Same pane, same build (`bin/runner-mc1` `4a0b4c6b…70dd8`, no rebuild),
same scratch-only rules. 3 boots used (P1, P3, P4).

Outcome: **(1) done — the full save path works.** P1 reached the Save
Records screen but the overwrite prompt defaults to **No**, so crosses
looped without writing. P4 (corrected: slot cross → up → cross) drove the
real save: the game deletes the whole SET side (4× Delete OK), recreates
it (Mkdir OK) and writes all three files at exact sizes (964 / 73144 /
3276), zero errors, then shows "Save complete." The SET data changed by
**7 bytes** (tail offsets 3249–3273 — a footer/counter, not table content:
our 04:31 didn't crack Brad's Top 5); icons rewritten byte-identical; GAM
untouched. **(3) partial:** P3 ran the identical browse/prompt flow on a
read-only card — same screens, zero errors, no hang, empty diff, perms
restored after; but since P1's flow never attempted a write, the
write-failure mode (Yes on read-only) is untested. **(2) not run:** the
third boot went to P4's correction instead of the reload; P4's written
card is preserved in scratch for a follow-up. No fix (no mechanism named:
the HLE returned OK with exact sizes throughout).

### Boots

| Boot | Card | Route | Result |
|---|---|---|---|
| P1-saverec | fresh seed copy | r1saverec: shifted FR1-R1 + Records → Save Records + crosses (43) | target t23029, 1207 s; overwrite prompt (No default) looped; **no writes** |
| P3-readonly | fresh seed copy, `chmod -R a-w` | r1saverec (43) | target t23073, 1192 s; identical screens; zero errors, no hang; perms restored; **empty diff** |
| P4-saveyes | fresh seed copy | r1saveyes: + up → cross to confirm Yes (44) | target t23303, 1167 s; **full save at t20532/20673**, "Save complete." |

All: zero FATAL, `targets=0`, E56 four RPCs, sound live, all presses
fired. P1/P3 parallel (slots 1/2); P4 solo (slot 1). 10 s snapshots.

### (1) The save, command by command (P4)

After cross@20650t confirmed Yes on "Would you like to overwrite
Options?":

| Tick | Commands (all OK) |
|---|---|
| 20532 | Delete ×4 (old SET side: data, icon.sys, ssx1.ico, dir) |
| 20673 | Mkdir (SET dir) + Open fd10 → Write 964 → Close (icon.sys) + Open fd11 → Write 73144 → Close (ssx1.ico) + Open fd12 → Write 3276 → Close (SET data) |

Zero Denied/NoEntry/NoFormat anywhere in the run. No GetDir in the
window — the game deletes blind, then recreates. (Pre-confirm, the flow
polls GetInfo continuously and re-lists + re-reads the SET icon.sys about
every 300t — P1: 857 GetInfo + 10 Open/Read-964/Close cycles, fds 7–16;
one `result=919874` line is a log-concatenation artifact, real fd 9.)

Host changes (before = pristine seed SHAs):

| File | Size | Before → after SHA | Verdict |
|---|---|---|---|
| `SET0001/BASLUS-20772-SET0001` | 3276 → 3276 | `4a31a2d7…002f1` → `9b3db142…15fcac` | **7 bytes differ** (runs 3249–3251, 3265–3266, 3272–3273), mtime bumped |
| `SET0001/icon.sys` | 964 | unchanged (`eab22574…`) | rewritten byte-identical (`cmp` clean), mtime bumped |
| `SET0001/ssx1.ico` | 73144 | unchanged (`5f8b5a92…`) | rewritten byte-identical, mtime bumped |
| `GAM0001/*` (all 3) | — | unchanged | byte-identical (`cmp` clean), mtimes untouched |

Nothing truncated, zero-filled or created oddly. The 7-byte tail diff fits
a footer/counter rewrite with no table change (visible Top 5 identical
before/after: BOB 02:57 … RYAN 03:27).

Prompts screenshotted (P4): Records table → Save Records screen (MEMORY
CARD slot 1, "1 Options", X Save / Triangle Previous / Square Delete) →
"Would you like to overwrite Options?" (No default, 20328t) → "Saving game
data to memory card (PS2)…" (20673t, the write tick) → "Save complete."
+ Continue (20824t) → Top 5 table (20970t).

### (2) Reload: not run (gap)

The three Part 2 boots went to P1 (flow discovery), P3 (read-only
browse) and P4 (the corrected save). No boot reloaded P4's written card,
so "loads cleanly / updated records visible / corruption prompt" is open.
The written card is preserved at `~/dev/ssx3-work/MC1/run/P4-saveyes/mc0`
(SHA above); follow-up: `r1saverec` with `--mcsrc` pointed at it, or the
short `menu` route for an autoload-only check.

### (3) Read-only: browse flow identical, write-failure open (gap)

P3 reached the same Save Records screen + overwrite dialog on the
`chmod -R a-w` card (screenshots match P1 frame-for-frame modulo race
jitter): 857 GetInfo + 10 icon re-read cycles, **zero** error results, no
stall (`bound=target`, 19.4 ticks/s — same pace as P1), empty diff,
permissions restored after (writability re-tested). But no write was
attempted (same default-No loop), so game-shows-vs-hang on a failed write
is open. Follow-up: `r1saveyes` with `--mcmode readonly`.

### Fix decision

None. Every HLE call in the save sequence returned OK with exact byte
counts; file sizes/shapes on the host are exactly right. No single
mechanism to fix, so no source change and no new unit test.

### Commands

```sh
python3 mc1_boot.py --route r1saverec --mcmode seed --runner bin/runner-mc1 \
  --label P1-saverec --wall 1800 --coverage-tick 16000 --stop-tick 23000 \
  --snap-period 10
python3 mc1_boot.py --route r1saverec --mcmode readonly --runner bin/runner-mc1 \
  --label P3-readonly --wall 1800 --coverage-tick 16000 --stop-tick 23000 \
  --snap-period 10
python3 mc1_boot.py --route r1saveyes --mcmode seed --runner bin/runner-mc1 \
  --label P4-saveyes --wall 1800 --coverage-tick 16000 --stop-tick 23200 \
  --snap-period 10
python3 mc1_analyze.py run/<label>
```

Part 2 budget: 0 builds, 3 boots, ~1.5 h. Never pushed. Pristine seed
re-verified 6/6 after all runs; E55D16 original re-read, prefixes match.
Text in git: this section + updated `mc1_boot.py` (new routes, `--mcsrc`,
`--snap-period`).

### Part 2 gaps

- Reload of P4's written card (Q2) not run — needs one boot.
- Write-failure on read-only (Yes path) not run — needs one boot.
- The 7 changed bytes are uninterpreted (tail runs only, no content
  dumped); the reload boot would show whether anything visible changes.
- Driver wart: `--mcsrc`/`--snap-period` were added after the first
  `parse_args()` call and initially unrecognized (fixed before any boot;
  two rc=2 no-op launches, no lanes created).
