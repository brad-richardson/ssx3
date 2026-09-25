# E55D16 — seed our memory card from Brad's real SSX 3 save, then load it

Worker: muse. Brief: `local/muse/prompts/E55D16.md`.
Fork `~/dev/PS2Recomp` @ `fb11e18` (clean; runner-dir guard exit 0).
Repo `main` @ `225135e1` at write time. No fork edits, no push.

Outcome: **Part 1 complete, no blocker** (seed extracted + verified).
**Part 2 boot ran clean** (`bound=target`, 1 boot used) and proves the
seeded `mc0` layout is fully accepted (game enumerates + fully reads both
saves at boot), but the **brief's screen observable was NOT met**: the
E55D12-timed route missed the seed-delayed title, so the run never reached
the Load game MEMORY CARD screen. Failed brief step: Part 2 observable.
No further boots attempted (budget 1 boot). No speed claims (diagnostic
build; `[vsync-rate]` lines ignored).

## 1. Part 1a — our runtime's `mc0` host format (fork `fb11e18`)

All paths in `ps2xRuntime/src/lib/Kernel/Stubs/MemoryCard.cpp` unless noted.

- Root: `PS2X_MC_ROOT` env, else `<elf dir>/mc0`, else `<cwd>/mc0`
  (`getMcRootPath`, :118-140; env applied in `src/main.cpp:270-278`;
  defaults in `ps2_runtime.cpp:394`, `:1430-1433`, `:1444-1452`).
  Port 0 → root; port 1 → sibling `mc1` (leaf rewrite, :141-154).
- Guest→host: `mc0:`/`mc1:` prefix strip, backslash fold, `.`/`..`
  resolution against per-port cwd (`normalizeGuestMcPathLocked`, :210-246);
  host = root + guest path minus leading `/` (`guestMcPathToHostPath`,
  :248-256).
- `sceMcGetDir` (:706-865): wildcard split to `(parentRel, pattern)`
  (:730-758, empty pattern → `*`); host dir list filtered by
  `wildcardMatch` (:333-370), sorted case-insensitively (:802-808);
  each hit copied as a 64 B `SceMcTblGetDir` (`fillMcDirTableEntry`,
  :314-331): Create=Modify=host mtime, size 0 for dirs, AttrFile =
  R|W|File/Subdir|Closed|Exists fixed synthesis, EntryName[32] truncated.
  `.`/`..` included only if the pattern matches (:777-789). Returns entry
  count (0 valid, e.g. `REP*` below).
- `sceMcOpen` (:1006-1067): guest→host map, `fopen` via `openMcHostFile`
  (:442-487, O_RDONLY/WRONLY/RDWR/APPEND/CREAT/TRUNC → `r+b`/`w+b`/…),
  fd table max 32 (:411-440). `sceMcRead` (:1069-1115) is `fread` into
  RDRAM; `Mkdir/Chdir/Delete/Rename` are the obvious host-fs ops.
- `sceMcSetFileInfo` (:1193-1224) ignores attr/time args: success iff the
  host path exists. `GetInfo` reports type=2, free=0x2000, format=1
  (:876-935); ports start formatted (`sceMcInit`, :942-960).

## 2. Part 1b — card image format map (decoded from the image, verified)

No mymc/PCSX2 memcard sources exist locally (only trace artifacts), so the
image was decoded empirically. Source `Mcd001.ps2` SHA
`ac98cf37…97bc` matches the brief pin (full in `s1-receipts.txt`).

- Geometry: 8,650,752 B = 16,384 pages × (512 data + 16 spare). Page 0:
  magic `Sony PS2 Memory Card Format 1.2.0.0`, page_len 512 (@0x28),
  pages_per_cluster 2 (@0x2A) → cluster 1024 B, pages_per_block 16 (@0x2C),
  clusters_per_card 8192 (@0x30), rootdir FAT cluster 0 → physical 41
  (@0x34 = 41 = alloc offset), alloc_end 8135 (@0x38), backup blocks
  1023/1022 (@0x40/0x44).
- Cluster map: physical cluster = FAT cluster + 41 (verified 4/4: root
  FAT 0 → phys 41, GAM dir FAT 2 → phys 43, SET dir FAT 117 → phys 158,
  BRAD dir FAT 198 → phys 239). `ifc` table at page 16 lists FAT#k at
  physical 9+k (FAT#1 = pages 18-19 covers FAT 0-255; FAT#2 = pages 20-21).
- FAT entries: `0x80000000|next`, END `0xFFFFFFFF`, FREE `0x7FFFFFFF`.
  All 9 chains touching our saves verified end-clean with exact lengths:
  root 0→1→197, GAM dir 2→3→77, GAM icon 4 (1 cl.), GAM .ico 5-76 (72),
  GAM data 78-116 (39), SET dir 117→118→192, SET icon 119 (1),
  SET .ico 120-191 (72), SET data 193-196 (4). FAT#1 fully used (256/256:
  fc 0-197 root/GAM/SET + fc 198-255 BRAD dir/slime head). Tail
  fc 8135-8191 marked END (= alloc_end; backup-block guard).
- Dirents: 512 B, one per page: mode u32 @0x00 (dir `0x8427`, file
  `0x8497`, root `..` `0xA426`), byte size @0x04 (dirs: entry count = 5),
  created @0x08, first FAT cluster @0x10, modified @0x18, name[32] @0x40.
  Timestamps are sane wall clock (2026-05-08; SET ~06:14, GAM ~06:44).
- Verification: magic + geometry asserts, every FAT chain walked to END
  with length == size-implied cluster count, both `icon.sys` start with
  `PS2D` and reference `ssx1.ico` ×3, both `.ico` share one SHA (same
  game icon), dir slots beyond the 5 entries/side are erased/empty,
  backup block 1023 holds stale copies (not walked). Root also holds a
  third dir `BASLUS-21065BRAD` (not extracted). `Mcd002.ps2` has no
  `BASLUS-20772` match (slot 2 holds no SSX 3 saves).

## 3. Part 1c — extraction table (into `~/dev/ssx3-work/E55D16/mc0/`)

Extractor: scratch-private `~/dev/ssx3-work/E55D16/e55d16_extract.py`
(stays out of git). Card bytes and save files never committed.

| Dir / file | Size | SHA-256 | Card modified |
| --- | --- | --- | --- |
| `BASLUS-20772-GAM0001/icon.sys` | 964 | `eab22574…0a49c` | 2026-05-08 06:44:13 |
| `BASLUS-20772-GAM0001/ssx1.ico` | 73144 | `5f8b5a92…fc0b` | 2026-05-08 06:44:14 |
| `BASLUS-20772-GAM0001/BASLUS-20772-GAM0001` | 39777 | `4bdaee79…7b78e` | 2026-05-08 06:44:15 |
| `BASLUS-20772-SET0001/icon.sys` | 964 | `dddf2d9c…ee13` | 2026-05-08 06:14:31 |
| `BASLUS-20772-SET0001/ssx1.ico` | 73144 | `5f8b5a92…fc0b` | 2026-05-08 06:14:31 |
| `BASLUS-20772-SET0001/BASLUS-20772-SET0001` | 3276 | `4a31a2d7…002f1` | 2026-05-08 06:14:32 |

(Full SHAs in `s1-receipts.txt`.) Dir modes `0x8427`, file modes
`0x8497`; this is exactly the 3-file + `.`/`..` set per side.

Representability → **no blocker, proceeded to Part 2.** The host layout
holds names/bytes/sizes and one mtime per file. It cannot represent card
mode bits (runtime synthesizes fixed AttrFile), separate create vs modify
stamps (runtime reports host mtime for both), or ECC — but nothing proves
the game checks any of these, and Part 2 is the experiment that tests it.
Lane copy carries card-faithful mtimes (card wall clock via `mktime`,
host-local interpretation, applied by the boot script).

## 4. Part 2 — one seeded boot (S1)

Runner: no existing binary had both runtime logs and det-hash (E55D3
checkout retired; `PS2X_PAD_CARD_PROBE` exists nowhere in the current
fork), so a fresh Release build was configured in-lane
(`RUNTIME_LOGS=ON`, `DET_HASH_TAP=ON`, `NO_THINLTO=ON`, unity+PCH,
`-j6`, ~4 min): `~/dev/ssx3-work/E55D16/build/ps2xRuntime/ps2EntryRunner`
SHA `f4d7632c…1711` (two reads match). Card lines come from `[MC]`
RUNTIME_LOG lines in `boot.log`, tick-correlated via interleaved
`[det-hash:v1]` lines (last-hash-before-line, approximate).

Route: E55D12's 9 inputs at identical ticks (Start 636, Square 820,
Downs 1000/1070/1140/1210, C1 1360, D5 1540, C2 1700) plus C3 Cross @1950
to select the MEMORY CARD row; stop 2100. Script
`e55d16_boot.py` SHA `d30b7990…f0d8` (`--self-check` all ok). One mini
slot (slot 2; slot 1 held by up1b), wall cap 500.

Run: `bound=target`, 82.2 s wall, last tick 2112, frame proof tick 2106,
log 1.0/16 MiB, frames 21 MB/2 GiB, PID gone, lease released, cards
bit-identical after (`02360f67…9a91`). All 10 pad presses fired in plan
order on the vsync clock (D4/C2/C3 +16 ms; gaps ≥ 60). `check.py` 52/52.

Card API (the seed works): 14 GetDirs, all at ticks 118-373 (boot
autoload, before any input): `SET*`→1 (×2), `GAM*`→1 (×2), `REP*`→0
(×2, correct — no replays seeded), 8 file GetDirs (data + `ssx1.ico` per
side, re-listed) →1. Reads: `icon.sys` 964 B ×4, SET data 3276 B,
GAM data 39777 B — every read is the exact full file size. No GetDir at
tick ≥ 1700 (the Load-game screen was never reached).

Screens (worker-viewed; verdict to the gate): the seed delays the title
by ~200 ticks (boot autoload), so the E55D12-timed inputs landed one
screen late: START@636 and Square@820 eaten (tick 654: logo without
prompt; tick 836: `Press START` just appeared) → C1@1360 title→Main Menu
→ D5 main-menu row 2 (`Conquer The Mountain`, tick 1631) → C2 Select
Character (`Mac`, tick 1803) → C3 select Mac → `Basic Controls` +
`15% Loading…` (tick 2057). The brief's MEMORY CARD observable was
therefore not reached; the cascade is fully evidenced, not inferred.

Curated: 4 PNG + 4 txt (`snap-836/1631/1803/2057`, 1.1 MB),
`s1-result.json`, `s1-receipts.txt`, `check.py`, `e55d16_boot.py`.

## 5. Gaps

- The MEMORY CARD list/select observable is unobserved; needs a re-timed
  route (title prompt at ~836 on seeded card vs ~636 empty: shift START
  to ~850+ and re-derive), i.e. a follow-up boot, over this brief's
  1-boot budget.
- `[MC]` lines carry no tick; tick correlation is by log interleave
  (±1 tick). No per-call table bytes (no E55D3-style probe in this fork).
- Host mtimes assume card wall clock = host-local wall clock (TZ of the
  Odin writer unknown); sub-minute create/modify skew preserved exactly.
- Attr-shape difference (fixed synthesis vs card modes `0x8427/0x8497`)
  untested against a real-card reference; the game read everything anyway.
- Snapshot tick tags are copy-time approximations (1 s wall grid).

Recommended next action: follow-up lane reusing this seed + runner with a
seeded-card route (START ~850, Square ~1050, re-derive Downs/C1/D5/C2/C3
from fresh settle observations, or probe-first: boot to Main Menu, then
Options→Save/Load→Load game with per-screen frame checks), 1 boot.

## 6. Commands run

- Reads: brief, `~/dev/AGENTS.md`, repo/local AGENTS, `docs/facts.md`,
  E55D12/E55D14P2B/E55D15P1 reports; `MemoryCard.cpp` (full),
  `Pad.cpp` padscript, `ps2_runtime.cpp` frame dump/logs, `ps2_log.h`.
- Hex/sweep decode of `Mcd001.ps2` (exploratory one-liners), then
  `e55d16_extract.py` (private scratch) → `mc0/` + `manifest.json`.
- `cmake` + `ninja -j6 ps2EntryRunner` (in-lane build dir; fork untouched).
- `e55d16_boot.py --self-check` (all ok) → `--label S1` (sole boot).
- Post: PID-gone + lease-free checks, frame viewing (654/836/1631/1803/
  1950/2057 + adjacency), `[MC]`/pad parsing, `gzip -k` closed boot.log,
  curated copies, `check.py` 52/52, commit (no push).

Base commit `225135e1`. Boots/builds/runs: 1 boot, 1 build. Text ~1.2 MB
(4 PNGs + small files); scratch (build + run + seed) stays private.

## Orchestrator gate (2026-09-24)

**A for the seed; the Load-game screen observable is moot.** Read the whole report and commit
`bd1885cb`; PNGs moved out of git to `~/dev/ssx3-work/E55D16/shots/` (text receipts only). The game
**autoloads** the seeded card at boot (ticks 118–373: GetDir SET*/GAM* → 1, every file read at its
exact size), so the route's Load game step isn't needed. Viewed tick 1631 (Main Menu) and tick 1803
(Select Character): Mac shows rider ranking 2.9 and stats 3.0–4.0, where unseeded boots show
default ~1.0 bars (IPAD1 Select Character), so Brad's progress loaded, not just the files. The
card-image decoder and the `mc0` host mapping (§1–§2) are the reusable result. Card bytes and
extracted saves stay private (`~/dev/ssx3-work/E55D16/mc0/`). Next only if Brad wants it: push his
save into the Odin/iPhone app's `mc0` so builds he plays start with his progress; retime I26-FAST
for the ~200-tick later title on a seeded card.
