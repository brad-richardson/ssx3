# E55D15 Part 1 — inventory a real SSX 3 save source (read-only)

Worker: opencode (Muse Spark). Brief: `local/muse/prompts/E55D15P1.md`.
Read-only inventory. **No copy, extraction, seed, device or game boot.
No build, fork/source/card edit, save seed/copy, extraction, device/lease
action, push, board/global edit, or upstream contact.**
Own only this brief and `local/research/E55D15P1/`.
Fork `~/dev/PS2Recomp` @ `eac6cba` read only (MemoryCard.cpp lines below).
Repo `main` @ `dda8fa99` at read time.

Question: does an already local, legitimately acquired **valid SSX 3 (USA)**
save exist with enough provenance to design one private seeded-card test?
E55D14 Part 2B observed stock Load game query at tick1740: raw
`BASLUS-20772-GAM*`, normalized `/BASLUS-20772-GAM*`, empty parent, host
root `mc0`, max6; five status rows returned empty and no mcRead
(`local/research/E55D14P2B/REPORT.md:21`, `ORCH-GATE.md:3`). Per brief,
`BASLUS-20772` was previously only a name string; a matching name alone is
not a valid save.

Predeclared outcome: **B** — no existing save has evidenced provenance,
correct region, exact wildcard-compatible name and sufficient layout to
design a separate bounded seed. B is stated plainly; no save invented,
no card seeded, no successful read claimed.

## 1. Candidate table

| # | Candidate path | Format | Region/game-ID evidence | Source/provenance | File list + sizes | 2×SHA | Host-dir layout? | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C1 | `~/dev/ssx3-work/*/mc0`, `mc1` (all lane run/card dirs) | host-dir card (plain dirs) | n/a (empty) | run inputs created empty by lane scripts (e.g. E55D12/E55D14P2 S1; manifest `f9401596…ccb9ce`) | `[]` — every mc0/mc1 dir empty (full 8-deep sweep, §2) | n/a (no candidate later used; no bytes to pin) | yes, structurally (§3) | **empty, not a save** |
| C2 | `Mcd001.ps2` / `Mcd002.ps2` (T-lane PCSX2 cards) | whole-card image (PCSX2 `.ps2`) | game serial `SLUS-20772` in same trace (region USA disc, not save region) | T27/T28 trace heads: bytesize `/home/brad/pcsx2-t4/` run, `McdSlot 0/1 [File]: Mcd001.ps2/Mcd002.ps2 [8 MB, UNFORMATTED]` (`local/research/T27/t27r1-trace-head.txt:34-35`, same in T28) | 8 MB each per trace text; files themselves live on bytesize (remote, not read: no ssh per worker limits) | n/a (not local, not used) | n/a | **UNFORMATTED empty cards, not a valid save** |
| C3 | `~/dev/ssx3-work/E32-inputs/` (`SSX 3 (USA).iso`, `cd/SLUS_207.72`) | disc image + ELF (not a save) | filename `SSX 3 (USA).iso` (3,005,415,424 B); ELF `SLUS_207.72` (3,890,784 B); trace `Name: SSX 3, Serial: SLUS-20772, CRC: 08FFF00D` (T27 head:27-29) | E32 lane inputs; `cd/mc0`, `cd/mc1` empty dirs | `SYSTEM.CNF` 49 B, `PAD0.000`/`PAD1.000` 268,435,456 B each, `SLUS_207.72` 3,890,784 B | n/a (not a save candidate) | n/a | **disc, not a save** |
| C4 | `BASLUS-20772` ELF string / tick1740 query pattern | name string only | `BASLUS-` prefix is consistent with USA `SLUS-20772`, but prefix alone is not region proof of a payload | `local/research/E55D6/REPORT.md:§1 #6` (ELF `strings` → `BASLUS-20772`, `mc0:` only; `SAVEDATA` absent); `E55D7/strings.txt:4`, `xref.txt:44` (sole code ref is a string-copy, not a card edge); tick1740 `getdirpath` pattern `BASLUS-20772-GAM*` (E55D14P2B REPORT:21) | no files | n/a | pattern known (§3) but zero payload bytes | **name only, not a save (per brief rule)** |

No other candidates: no `*BASLUS*` directory, no save-export file
(`*.psu`/`*.cbs`/`*.xps`/`*.max`/`*.sps`/`*.npo`/`*savegame*`/`*gamesave*`),
and no card image (`*.ps2`/`*.p2s`/`Mcd*.bin`/`*memcard*.bin`) exists
anywhere under `~/dev/ssx3-work` or `~/dev/ssx3-inputs` (§2). Two matching
SHA reads: none required — no candidate is later used, so no SHA is pinned
here (stated plainly, not omitted).

## 2. Locations inventoried (bounded, read-only; no payload bytes printed)

- Lane receipts (`local/research`, `rg -li BASLUS-20772`): only E55D6/E55D7
  (ELF string), E55D8, E55D13 (design: payload unknown), E55D14P2B
  (tick1740 pattern). No receipt anywhere pins save filenames, sizes,
  bytes, or provenance.
- Private `~/dev/ssx3-work` card dirs: `find -maxdepth 8 -type d
  \( -name mc0 -o -name mc1 \)` with non-empty check → **zero non-empty**
  (DONE, all empty). Spot `ls -la`: `E55D14P2/run/S1/mc0`,
  `E32-inputs/cd/mc0`, `E43-run/mc0`, `E42-run/mc0`, `E40-run/mc0`,
  `E41-run/mc0` all `total 0`, 2 entries (`.`/`..` only).
- Image/export sweep: `find ~/dev/ssx3-work ~/dev/ssx3-inputs -type f`
  over the four card-image name shapes → zero hits; over six
  save-export shapes → zero hits; `-type d -iname *BASLUS*` → zero hits.
- PCSX2 locations under `~/dev`: only build/trace artifacts
  (`AU6/pcsx2_*.bin/.txt/.sh`, `E51/pcsx2-vram.bin`, `E60/pcsx2_*.sh/.log`);
  no local card files. The referenced `Mcd001.ps2`/`Mcd002.ps2` live at
  bytesize `/home/brad/pcsx2-t4/` (trace text) — remote, and recorded
  UNFORMATTED (C2).
- Share tier: **not inventoried — `/Volumes/share` is not mounted**
  (`ls /Volumes/` → `Extreme SSD`, `Macintosh HD`, `Recovery` only).
  The external SSD was not scanned (outside the brief's bounded locations;
  unrelated personal files). No ssh to bradflix/bytesize (worker denial
  scope), so remote card/game dirs are unobserved beyond trace text.
- `local/research/I26/ROUTES.md:4-5`: setup requires an empty card (no
  profile prompt) — a route rule, not a save.

## 3. GetDir host-directory layout (source-grounded; fork `eac6cba`)

LSP `hover` on `MemoryCard.cpp:119` returned no results (no usable server
in this environment, same as E55D6 §1 #12); mapping below is by direct
read with exact lines (all in
`~/dev/PS2Recomp/ps2xRuntime/src/lib/Kernel/Stubs/MemoryCard.cpp`):

- `getMcRootPath` (:118-155): root is `PS2X_MC_ROOT` env, else
  `elfDirectory/mc0`, else `cwd/mc0` (:120-134); port ≤ 0 returns root
  (:137-140); port 1 rewrites leaf `mc0`→`mc1` (:145-148). So port 0
  (tick1740 `port=0 slot=0`) reads the host `mc0` dir.
- `normalizeGuestMcPathLocked` (:210-246): backslash fold (:212),
  `mc0:`/`mc1:` strip (:214-217), `.`/`..`-resolved join against per-port
  cwd for relative paths (:219-245).
- `guestMcPathToHostPath` (:248-256): host path = `getMcRootPath(port)`
  joined with the guest path minus leading `/`.
- `sceMcGetDir` (:706-770): `rawPath` read bounded by `kMcMaxPathLen`
  (:710); normalize (:728-729); wildcard split → `(parentRel, pattern)`
  (:730-742), else dir-vs-file probe (:744-758); empty pattern → `*`
  (:760-763); `hostDir = getMcRootPath(port) [/ parentRel]` (:765-770).

Applied to tick1740 (`raw=BASLUS-20772-GAM*`, `parent=""`,
`pattern=BASLUS-20772-GAM*`, `host=<lane>/mc0`): hasWildcard → `parentRel`
empty → `hostDir` is the `mc0` root itself, and entries are listed
directly under `mc0/` filtered by `wildcardMatch("BASLUS-20772-GAM*",
name)` (filter at :818-824 per E55D13 §1 #5; `.`/`..` gated on pattern
match). **Yes — a host-directory layout can be established from the
runtime implementation**: seed entries would sit directly under the
port-0 `mc0` host dir with names matching `BASLUS-20772-GAM*`. What is
NOT established: the expected entry names beyond the pattern, the file
set/sizes/bytes inside any entry, or timestamps the game accepts —
still unknown, same gap as E55D13 §7.

## 4. Extraction tool/process (no extraction now)

Not applicable: no whole-card image candidate was found locally, so no
extraction is needed or performed. No extraction tool is pinned in local
evidence; the tool/process gets identified only if/when an image
candidate appears. (Per brief: without extracting now — nothing was
extracted.)

## 5. Exact commands run (read-only; no boot/build/seed)

- `ls ~/dev/ssx3-work/`, `ls ~/dev/ssx3-inputs/`, `ls /Volumes/`
  (share absent), `ls ~/dev/` (PCSX2-adjacent entries).
- `rg -li BASLUS-20772 local/research/` (receipt list).
- `find ~/dev/ssx3-work -maxdepth 4 \( -iname *BASLUS* -o -iname *20772*
  -o -iname *memcard* -o -iname *memorycard* -o -iname *.ps2 -o -iname
  *.p2s -o -iname *.max -o -iname *.cbs -o -iname *.psu -o -iname *.xps \)`
  → zero hits; same shapes over `~/dev/ssx3`, `~/dev/ssx3-inputs`
  (only `native/patches/moderngekko-memcard-read-rate.patch`, unrelated).
- `find ~/dev/ssx3-work -maxdepth 8 -type d \( -name mc0 -o -name mc1 \)`
  + non-empty check → zero non-empty; `ls -la` on six mc0 dirs → empty.
- `find` for `*BASLUS*` dirs, six save-export shapes, four card-image
  shapes under ssx3-work/ssx3-inputs → all zero.
- `rg -i memcard|... local/research docs` + P4 follow-up (deploy
  `savedata/` layout note, not an existing save); `sed -n 25,45p
  T27/t27r1-trace-head.txt` (serial + UNFORMATTED cards).
- `rg -i save|memcard|card|BASLUS|empty local/research/I26/ROUTES.md`
  (setup rule); V1 manifest `rg` → no card rows.
- `grep MemoryCard.cpp` for
  `getMcRootPath|normalizeGuestMcPathLocked|hostDir = |hasWildcard|PS2X_MC_ROOT`
  (20 hits); full reads of :110-159, :210-269, :700-774; LSP hover
  (no results); `git -C ~/dev/PS2Recomp log --oneline -1` (`eac6cba`).
- `python3 local/research/E55D15P1/check.py` → ALL PASS (§6).

## 6. Gaps (stated plainly)

- Share tier unobserved (`/Volumes/share` unmounted); remote bytesize /
  bradflix dirs unobserved (no ssh). A save could exist there — the B
  verdict covers only the bounded locations actually inventoried.
- C2's bytesize card files were never read here; only the trace text
  (`UNFORMATTED`) evidences emptiness.
- Expected save entry names beyond the `BASLUS-20772-GAM*` pattern, file
  set, sizes, bytes, and accepted timestamps remain unknown (§3); even a
  correctly named entry is not yet a valid save.
- Source strings and empty-card receipts cannot prove guest behavior
  (same caveat as E55D13 `check.py`).
- No SHAs pinned (no candidate used); no raw save bytes seen or recorded.

## 7. Outcome + smallest next observation for B

**B**: no existing local save with evidenced provenance, correct region,
exact wildcard-compatible name and sufficient layout exists in the
bounded inventory to design a separate seeded-card test. This B is a
design input, **not** proof the guest accepts any save.

Smallest next observation: the orchestrator (which holds ssh/scope this
brief denies) checks the two unobserved bounded locations for a
`BASLUS-20772*` export — (1) mount/read the share tier, (2) list the
bytesize PCSX2 memcard dir behind the T27/T28 traces — filename/size
listing only, no copy. If both are empty/absent, the unblock is
acquisition (a fresh dump from owned hardware/disc), not further search.

Base commit: `dda8fa99`. Fork: `eac6cba`. Boots/builds/runs: 0.
Committed text: `REPORT.md` + `check.py` only (<256 KiB).
