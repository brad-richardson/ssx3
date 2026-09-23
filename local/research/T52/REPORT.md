# T52 REPORT — PCSX2: every CD read from boot to Select Character settled

Brief `local/muse/prompts/T52.md`. Read first: `AGENTS.md`,
`local/AGENTS.local.md`, `local/research/T51/REPORT.md` (§T51-5/§T51-6),
`local/research/T47/REPORT.md` (route, pins), `local/research/T46/REPORT.md`.
Tables + receipts; the orchestrator decides. No verdict.

## T52-0. Mission table

| # | Mission | Result |
| --- | --- | --- |
| 1 | Fresh boot to SC settled, bounded log of every IOP CD read (`cdread seq/vsync/lbn/sectors/mode/dest`) + `cdsearch`/ioman names if cheap | DONE — 5836 reads, seq 0–5835 contiguous, 0 rejects; names via offline ISO extent map (guest-side search/open names are not host-visible, §T52-7) |
| 2 | Vsync anchors for title / menu / SC entry / SC settled | DONE — 4 `T52_MARK`s at vsync 10911 / 15991 / 16780 / 19350 |
| 3 | Table: reads per phase, distinct LBN ranges for menu→SC + SC-on-screen, file names | DONE (§T52-5/6, full lists in `evidence/t52-analysis.txt`) |
| 4 | Budgets: ≤2 builds, ≤2 boots, 3 h, 5 GB | DONE — 2 builds, 1 boot, ~35 min wall, ~1.3 GB new on bytesize |
| 5 | Receipts + `[T52]` commit, no push | DONE (this file + dir) |

Headline for the orchestrator: from power-on to settled SC the game issues
**5836 N-data-reads / 72,745 sectors (~149 MB), all DVD except 34 early CD
reads**. The menu→SC transition is **533 reads: MUSIC2.BIG streaming +
83 sectors of MDLPS2.BIG + 59 of ZOETXP.BIG**; once SC is on screen **every
read (446) is MUSIC2.BIG streaming** (stride-16 1–4-sector comb,
728448–730589 + 736823–737811). The Zoe-texture reads land in the
menu→scentry window — the healthy side loads Zoe before SC settles.

## T52-1. Pins

| Pin | Value |
| --- | --- |
| PCSX2 tree | `9056c08349cc29ad02a6d1a3a4133259019195af` (`/home/brad/pcsx2-g7/pcsx2`); base = T51-end working tree + T52 hooks |
| Pre-T52 SHAs | CDVD.cpp `3d513320…fb11c4`, GS.cpp `717277a0…107749f1` |
| Post-T52 SHAs | CDVD.cpp `ae78dbf6…4c44c3d1f61`, GS.cpp `20a473e0…a609dedfc` |
| Build-1 bins | qt `978c5c73…0122a221`, gsrunner `b5686de7…8db10268a` (3 `-Wmisleading-indentation` warnings on T52 lines, then fix1) |
| Build-2 bins (capture) | qt `815e29e9…f198ca43`, gsrunner `99b0044b…a5231af0` (zero warnings) |
| Patch | `t52-hook.py` (6/6 anchors first try) + `t52-fix1.py` (3/3 lines); appliers ARE the patch, both committed |
| Inputs | ISO `SSX 3 (USA).iso` 3005415424 B; BIOS trio as T46; datapath `dat-t48` rec (`EnableEE = true`, `Renderer = -1`) |
| Capture boot | T_BOOT wall 1790162341, WID 2097159 (same as T31–T51), `T52_DONE` at T+205 s (< 600 s cap) |
| Trace | `evidence/t52-trace.txt` 690262 B sha256 `2c160443…5bc8eb3`: cdread 5836 + marks 4, 0 rejects, last_seq 5835 |
| Poll | `evidence/t52-poll.log` (all gates + MENU_T+ press walls) |
| F8 native PNGs | `evidence/t52-shot-{title,menu,sc}.png` (266/124/202 KB) |
| Settle pair | `evidence/t52-{scpre,scfinal}.jpg` (70 KB each) |
| Isomap | `evidence/t52-isomap.txt` (ISO9660 walk, 101 files + dirs) |
| Full range tables | `evidence/t52-analysis.txt` (425 lines, reproduced locally bit-class) |
| Fresh emulog | `/home/brad/pcsx2-g7/dat-t48/PCSX2/logs/emulog.txt` 1188816166 B (stays on bytesize; pre-boot rotation `emulog-pre-t52-20260923T111901Z.txt`) |

Builds 2/2 (b1 warning-only + fix1 rebuild). Boots 1/1 (all route gates
passed first try). Bytesize new bytes ≈ 1.3 GB of 5 GB (emulog 1.19 GB +
t52-frames 916K + snaps/logs). WSL held one boot throughout (up 8 min at
close, zero restarts — the T51-6 loop did not bite).

## T52-2. The patch (log-only, 2 files)

Built-in `CDVD_LOG("DvdRead > …")` lines already log every read (9036 in the
old emulog) but carry **no vsync**, so one hook was needed for the
`vsync=` join and the exact transition anchors.

| Hunk | File:anchor | What |
| --- | --- | --- |
| T52-INC/DECL | `CDVD/CDVD.cpp` after `#include <memory>` / `u32 PSXCLK` | `#include <atomic>`, `extern g_t48_vsync` (T48 mirror, stored unconditionally every GS vsync), `static g_t52_seq`, `t52_cdread(kind)` |
| T52-CD/CDDA/DVD | same, after each N-data-read verbose statement | `t52_cdread("CD"/"CDDA"/"DVD")` at statement level (dedented — unconditional by construction; b1 proved it: reads logged with `CdvdVerboseReads = false`) |
| T52-MARKS | `GS/GS.cpp` after the `g_t48_vsync.store` line | poll 4 fixed `/tmp/t52-mark-<label>` paths per vsync → `T52_MARK` + `remove()` (skew ≤ 1 vsync, explicit paths — no `snprintf` in this TU) |

Line formats (emulog channel; `vsync` = `g_t48_vsync`, the T48–T51 frame
counter convention):
`T52_CDREAD seq=<n> vsync=<n> kind=<CD|DVD|CDDA> lbn=<SeekToSector>
sectors=<SectorCnt> blocksize=<N> speed=<N>x spindle=<CAV|CLV>
readmode=0x<N> dest=-`
`T52_MARK vsync=<n> label=<title|menu|scentry|scsettled>`

`dest=-` always: the N-command layer never sees the IOP destination (data
drains later via DMA3 interrupt). `lbn` = requested start sector
(`cdvd.SeekToSector`; also logged `CurrentSector` in `CDVD_LOG`, kept in
the raw emulog). No caps (every read is the deliverable), no gates
(always on — the replay leg bounds the blast radius instead).

## T52-3. Preservation

G13 rich-dump replay, build-2 gsrunner: **7/7 PNG md5s match the T48 §T48-1
pins exactly** (`b7a3e8db a7929218 bb8b1d85 817e934f ×2 85cf3599 ×2`),
**HWSTAT exact** (791/37/0/14/320/6), **zero T52 lines** (replay performs
no disc reads). Hook fires only on guest N-data-reads; renderer/EE/timing
untouched.

## T52-4. Capture route + screen gates (T47 frontend verbatim to SC park)

Fresh `-slowboot -turbo` rec boot, attract-skip ONE Cross, title→menu→SC
with T47's thresholds, `touch /tmp/t52-mark-*` at each gate pass, F8 at
each screen, 8 s settle pair, kill. All gates passed first try:

| Gate | Score (mean/p99) | Threshold | MENU_T+ | Mark → vsync |
| --- | --- | --- | --- | --- |
| A1 title poll01 (first attempt) | 0.4329/6 vs title | < 2.0/≤ 10 | 101 | title → 10911 |
| post8/post15/post25 non-title + hops 0.0571/0.0253 static, post25 vs-menu 0.2866 | MENU-LIKE | — | 110–146 | menu → 15991 |
| menupre vs-menu 0.3163/5 | menu | — | 146 | — |
| mc-post1 departs menu 11.1131 (> 5.0) | SC entry | — | 157 | scentry → 16780 |
| mc-post3/8/15 vs-sc 0.58/0.61/0.55, hops 1.03/0.06/0.21, vs-menu ~10.2 | SC-LIKE | nonmenu + static | 161–190 | — |
| scpre vs-sc 0.5196/8 (< 2.0) | SC confirm | — | 196 | scsettled → 19350 |
| scfinal vs-sc 0.5666/8, settle hop scpre→scfinal 0.1449 (< 1.0) | settled | — | 198+ | — |

F8 SC viewed: settled Select Character, **Zoe 3D model rendered**, stat
bars, rider silhouettes — the healthy full-scene side. SC-settled vsync
19350 matches the T48-A (18807) / T50-boot1 (19026) class for this route.

## T52-5. Reads per phase (count, total sectors) + file attribution

Phases from marks: boot→title [0,10911), title→menu [10911,15991),
menu→scentry [15991,16780), scentry→scsettled [16780,19350),
scsettled→end [19350,20437). File owners from the ISO extent map
(`lbn=extent sectors=size name=path`).

| Phase | n reads | Sectors (bytes) | Kinds | Top files by sectors |
| --- | --- | --- | --- | --- |
| boot→title | 4544 | 63265 (129.6 MB) | CD 34, DVD 4510 | INTRO_DJ.MPC 56112, SLUS_207.72 1888, THX.MPC 1154, FE_1.SSH 980, EABIG.MPC 626, MUSIC2.BIG 458, BOLTPS2.DAT 270, FE.LUI 220, AUDIO.BIG 204, ANM.BIG 198, DNAS271.IMG 133, PARTICLE.SSH 96 |
| title→menu | 619 | 4952 (10.1 MB) | DVD 619 | MUSIC2.BIG 4952 (100%) |
| menu→scentry | 227 | 932 (1.9 MB) | DVD 227 | MUSIC2.BIG 790, MDLPS2.BIG 83, ZOETXP.BIG 59 |
| scentry→scsettled | 306 | 2483 (5.1 MB) | DVD 306 | MUSIC2.BIG 2483 (100%) |
| scsettled→end | 140 | 1113 (2.3 MB) | DVD 140 | MUSIC2.BIG 1113 (100%) |
| **whole boot** | **5836** | **72745 (149.0 MB)** | **CD 34, DVD 5802, CDDA 0** | — |

Mode census: DVD all `blocksize=2064 speed=4x CAV readmode=0x3`; CD
`blocksize=2048` (13× `2x CLV`, 21× `4x CAV`), readmode 0x3. Zero CDDA
reads anywhere boot→kill.

## T52-6. LBN ranges: transition vs SC-on-screen

Transition = menu→scsettled: **533 reads, 521 distinct LBN, 207 ranges**.
SC-on-screen = scentry→end: **446 reads, 431 distinct, 206 ranges**.
Exhaustive lists: `evidence/t52-analysis.txt` (regenerable:
`t52-analyze.py evidence/t52-trace.txt`). Cluster summary with file owners:

| Window | LBN clusters | Owner file (extent range) | Reads |
| --- | --- | --- | --- |
| menu→scentry | 310335–310337, 310382–310385, 314661–315165 (11 small ranges) | MDLPS2.BIG (309729–316951, character models) | ~30 |
| menu→scentry | 377830–379957 (6 ranges, incl. 379931–379957 ×27) | ZOETXP.BIG (374782–381602, Zoe textures) | ~40 |
| transition + SC | 728448–737811 comb: stride-16 1–4-sector reads (e.g. 728448/9, 728464/5, … 737811) | MUSIC2.BIG (638388–865270, streamed music) | ~460 |
| SC-on-screen | 728448–730589 + 736823–737811 (same comb continues) | MUSIC2.BIG | 446 (100%) |

Shape notes for the join: the game reads MUSIC2.BIG as a persistent
stride-16 1–4-sector comb through the whole front end (title→menu 619
reads all MUSIC2.BIG too); the **only non-music reads in the menu→SC
window are MDLPS2.BIG + ZOETXP.BIG**, both in menu→scentry, i.e. loaded
as the SC scene builds. Reads continue while SC sits settled (140 reads
post-mark) — settled ≠ disc-quiet.

## T52-7. CD-kind reads + the cheap name lookups (all results)

34 CD reads, two groups. seq 0–12 (vsync 421–778, 2x CLV): BIOS area —
lbn 16 (PVD) → 257 → 261 (root dir) → 483 ×2 (SYSTEM.CNF) → lbn 0 ×12
sectors (lead-in) → repeat 16/257/261 → SLUS_207.72 head 484–515
(4×8 sectors). seq 245–265 (vsync 884–897, 4x CAV): lbn 16/257/261/273
(metadata) then DNAS271.IMG+0..+131 (17 reads, 8 sectors each, then
4 + 1) — DNAS auth. Filesystem-metadata reads (16/257/261/273) are the
host-visible half of `sceCdSearchFile`-style lookups; the names never
cross to the host: **zero `SearchFile` and zero `sceOpen` lines in the
1.19 GB emulog**, and no ioman opens on the CD path (convergent with
T47-5: all disc I/O goes through the `_sceCdSC` read loop, no ioman I/O).
File names in §T52-5/6 come from the offline extent map instead.

## T52-8. Gaps, overruns

1. `dest=-` on all lines (N-command layer has no IOP dest; §T52-2).
2. `vsync` = GS/EE frame counter (`g_t48_vsync`, T48–T51 convention), not a
   separately-counted EE VBLANK — same numbering the E40 join already uses.
3. Mark skew ≤ ~2 wall-s (`sleep 2` in `mark()` after the gate snap) + ≤ 1
   vsync detection; phases span 789–10911 vsyncs, so attribution is exact
   for diff purposes.
4. UNMAPPED owners (lbn 0/16/257/261/273) are ISO metadata/lead-in, not
   files, by construction of the extent map.
5. CDVD readahead (`DoCDVDreadTrack`) does not emit extra N-lines — one
   line = one guest N-data-command.
6. Budgets: builds 2/2 (b1 warning-only, fix1 clean), boots 1/2, ~35 min
   wall of 3 h, ~1.3 GB of 5 GB. No overruns.
7. No audio-gate receipts this lane (route is player-style identical to T47
   F1; no modal appeared — v2 dialogwatch not needed, gates passed first
   try). No speed numbers quoted (diagnostic build by definition).

## T52-9. Exact commands

Bytesize, foreground, one held ssh per run (no detached launches; WSL
stops between calls, each call demand-boots):
stage (`scp` → `C:\Users\bradr\pcsx2-t4\t52stage\` → `cp` to
`/home/brad/pcsx2-t4/t52stage/`) → pre-SHAs → `python3 t52-hook.py`
(6/6 anchors) → `t52-build.sh` (cmake `--build …/build --target pcsx2-qt
pcsx2-gsrunner -j2`; SHAs §T52-1) → `python3 t52-fix1.py` (3/3) →
`t52-build.sh` again → `t52-replay.sh` (G13 dump 7/7 + HWSTAT + zero T52)
→ `t52-cap.sh` (fresh rec boot, T_BOOT 1790162341, `T52_DONE` T+205 s) →
`python3 t52-extract.py <emulog> t52-trace.txt` (5836+4, 0 rejects) →
`t52-analyze.py` → `t52-isomap.py` / `t52-join.py` → `grep -c SearchFile`
/ `sceOpen` (both 0) → fetch set via `t52fetch/` → `scp` to
`local/research/T52/evidence/`.
`git log -1` checked before commit (see §T52-10). Never push.

## T52-10. Receipts + handoff

Repo (this commit): `local/research/T52/` — REPORT.md, hook/build/replay/
cap/fix1/extract/analyze/isomap/join scripts, `evidence/` (trace 690 KB +
sha `2c160443…5bc8eb3`, analysis 425 lines, poll, isomap, boot logs,
3 F8 PNGs, scpre/scfinal settle pair). Bytesize residue under cap:
`t52stage/` (scripts + trace + isomap), `t52-frames/` (916K replay PNGs),
`emulog-t52proof.txt`, rotated `emulog-pre-t52-*`, fresh emulog (1.19 GB).

Handoff for the orchestrator (no verdict): join keys for the recomp diff
are the §T52-6 clusters — MDLPS2.BIG 310335–310385 + 314661–315165,
ZOETXP.BIG 377830–379957 (menu→scentry only), MUSIC2.BIG comb
728448–737811 (whole front end, continues while SC is settled) — plus the
seq 0–12 / 245–265 CD reads (BIOS/SLUS/DNAS). If the recomp's reader log
shows fewer/no reads in any of these LB
...[truncated 211 chars]
