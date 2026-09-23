# V2 — External SSD inventory (read-only, 2026-09-23)

Source: `/Volumes/Extreme SSD` (ExFAT, 1.8 TB). Method: `du -sk` per top-level entry
(ExFAT-allocated: 1 MiB minimum per file, so small-file entries read high; file counts
via `find -type f`; `.[._]*` AppleDouble sidecars excluded from file counts where noted).
Reference check: entry names grepped across `docs/status.md`, `docs/todo.md`,
`docs/numbers-ledger.md`, open briefs (E31/E32/G42/PF1/T47/N3), `local/research/V1/`, and the
REPORT/CHECKPOINT files of E31, G42, PF1, T47, N3 on 2026-09-23. Only open-item references
count toward KEEP-LIVE; closed-report references are history. No hashes over 1 GB.
Repo HEAD at inventory time: `15803f4` (E31 PASS). SSD never written (no mounts changed,
no `._` files cleaned, `COPYFILE_DISABLE` not needed for reads). No disconnects during the pass.

## Totals per class

| Class | Entries | Allocated GB | Files |
| --- | --- | --- | --- |
| KEEP-LIVE | 11 | 206.3 | 78872 |
| KEEP-SOLE | 26 | 255.5 | 195263 |
| DELETE-REBUILDABLE | 34 | 204.1 | 127048 |
| DELETE-MIRRORED | 14 | 63.8 | 316 |
| DELETE-STALE | 95 | 83.9 | 63244 |
| ASK | 7 | 599.0 | 488772 |
| NOT-SSX3 | 15 | 422.4 | 5980 |

GB freed if every DELETE-* row goes: **351.8 GB allocated** (logical less; ExFAT 1 MiB/file slack returns too).

## Table (sorted by size)

| Entry | GB | Files | Mtime | Class | Evidence | Second copy |
| --- | --- | --- | --- | --- | --- | --- |
| brad-google-takeout | 232.6 | 6 | 2024-12-05 | NOT-SSX3 | NOT-SSX3: Brad's own data; size+mtime only, never opened; Brad decides. |  |
| upstream-review | 232.29 | 223191 | 2026-09-18 | ASK | GameCube-recomp tooling + lane sources (m1-modules 118GB, m1d-src, s1b-src, ModernGekko, DolRecomp, GXBE69-game...); reserve-adjacent; no .git; no mirror checked. Needs orchestrator/Brad call. |  |
| ssx3-archive | 190.47 | 146876 | 2026-09-17 | ASK | GameCube-route archive (2026-09-16: builds/checkouts/evidence/game/players/profiles/remaster/reports + MANIFEST; 183GB + mobile reports). Reserve route is parked, not closed; no mirror checked. Needs orchestrator/Brad call. |  |
| aggiemail | 186.05 | 4604 | 2024-12-05 | NOT-SSX3 | NOT-SSX3: Brad's own data; size+mtime only, never opened; Brad decides. |  |
| ps2recomp-spike/P1 | 128.38 | 23947 | 2026-09-22 | KEEP-LIVE | E31 PASS (15803f4: stock race on Mac); E31 brief owns worktree+P1/run+e29-build; E32 brief folds from this worktree (fork ssx3, remote fork). |  |
| android-spike/src-work-trees-S3-S1b-m4src-d8src-modm7 | 117.49 | 107241 | 2026-09-18 | ASK | Lane source/work trees (S3 41GB S-lane bundle; S1b 15GB mixed receipts+builds; m4-src/d8-src 30GB Dolphin-derived + mod-template, no .git; module-m7 4GB src+patch). Reserve D/S/M routes; needs orchestrator/Brad call. |  |
| android-spike/build-trees-8x | 75.03 | 65757 | 2026-09-18 | DELETE-REBUILDABLE | Closed/reserve-lane cmake build outputs (core-build, core-egl-build/-d5/-d8/-lse/-plain, core-vk-build, module-build); inputs = m-src trees + .patch files in KEEP-SOLE report dirs. | rebuild per lane recipe |
| ps2x-t4/rest-40-logs | 60.46 | 40 | 2026-09-22 | DELETE-MIRRORED | V1 AUDIT row 23: SSD<->share agreement, 2 passes + 40/40 committed slices; counts 2026-09-23: 41 files each side incl t46r3 (split to KEEP-SOLE, SSD-only); this row = other 40 logs (SSD carries +41 AppleDouble sidecars). | /Volumes/share/ssx3/ps2x-t4 |
| parallel-gs-g7 | 29.3 | 26126 | 2026-09-21 | KEEP-LIVE | Named live reader in V2 brief (G42). |  |
| laptop-evacuated-0918 | 27.83 | 765 | 2026-09-18 | ASK | Retired-laptop local/ overflow (builds, fast-game.tar 1.35GB, reports.tar 1.43GB, native, research); share's laptop-evacuated-0922 is a different set (8.5GB), not equivalent. Tars may hold reserve-route data. Needs call. |  |
| ps2x-i4 | 24.53 | 20616 | 2026-09-19 | KEEP-SOLE | Parked I lane (todo: re-probe after E30; E32 folds i23-ffmpeg-ios + branchless I10-I21): SSD-only work inputs; fork-wt dirs hold unique pre-fold refs (todo V). Release after E32 lands. |  |
| ps2x-i10 | 23.78 | 19057 | 2026-09-21 | KEEP-SOLE | Parked I lane (todo: re-probe after E30; E32 folds i23-ffmpeg-ios + branchless I10-I21): SSD-only work inputs; fork-wt dirs hold unique pre-fold refs (todo V). Release after E32 lands. |  |
| ps2x-i16 | 18.11 | 14725 | 2026-09-21 | KEEP-SOLE | Parked I lane (todo: re-probe after E30; E32 folds i23-ffmpeg-ios + branchless I10-I21): SSD-only work inputs; fork-wt dirs hold unique pre-fold refs (todo V). Release after E32 lands. |  |
| ps2x-i11 | 18.11 | 14725 | 2026-09-21 | KEEP-SOLE | Parked I lane (todo: re-probe after E30; E32 folds i23-ffmpeg-ios + branchless I10-I21): SSD-only work inputs; fork-wt dirs hold unique pre-fold refs (todo V). Release after E32 lands. |  |
| ps2x-i12 | 18.1 | 14724 | 2026-09-21 | KEEP-SOLE | Parked I lane (todo: re-probe after E30; E32 folds i23-ffmpeg-ios + branchless I10-I21): SSD-only work inputs; fork-wt dirs hold unique pre-fold refs (todo V). Release after E32 lands. |  |
| ps2x-i13 | 18.1 | 14723 | 2026-09-21 | KEEP-SOLE | Parked I lane (todo: re-probe after E30; E32 folds i23-ffmpeg-ios + branchless I10-I21): SSD-only work inputs; fork-wt dirs hold unique pre-fold refs (todo V). Release after E32 lands. |  |
| ps2x-i14 | 18.1 | 14720 | 2026-09-21 | KEEP-SOLE | Parked I lane (todo: re-probe after E30; E32 folds i23-ffmpeg-ios + branchless I10-I21): SSD-only work inputs; fork-wt dirs hold unique pre-fold refs (todo V). Release after E32 lands. |  |
| ps2x-i17 | 18.09 | 14713 | 2026-09-21 | KEEP-SOLE | Parked I lane (todo: re-probe after E30; E32 folds i23-ffmpeg-ios + branchless I10-I21): SSD-only work inputs; fork-wt dirs hold unique pre-fold refs (todo V). Release after E32 lands. |  |
| ps2x-i15 | 18.09 | 14709 | 2026-09-21 | KEEP-SOLE | Parked I lane (todo: re-probe after E30; E32 folds i23-ffmpeg-ios + branchless I10-I21): SSD-only work inputs; fork-wt dirs hold unique pre-fold refs (todo V). Release after E32 lands. |  |
| ps2recomp-spike/e29-movie-bypass-build | 17.68 | 7346 | 2026-09-22 | KEEP-LIVE | E31 PASS (15803f4: stock race on Mac); E31 brief owns worktree+P1/run+e29-build; E32 brief folds from this worktree (fork ssx3, remote fork). |  |
| glimmer-ize | 17.56 | 6 | 2026-09-04 | ASK | Unplaced: 18GB 'models' dir, no references anywhere in repo (grep 2026-09-23); did not open further per NOT-SSX3 caution. Needs Brad call. |  |
| ps2x-p8 | 15.87 | 16242 | 2026-09-19 | DELETE-STALE | Closed-P8 jal-census analysis outputs; P8 REPORT in git; no open refs. |  |
| q2-recomp-scan | 14.48 | 14217 | 2026-09-18 | DELETE-STALE | Closed survey checkouts of public upstream repos, no .git recorded; nothing open references them; re-clonable from GitHub. |  |
| android-spike/work-dirs-stale | 12.97 | 5536 | 2026-09-18 | DELETE-STALE | Closed/reserve-lane work dirs (m3 incl M3_NOTES + dtm inputs, S2/S2b receipts with REPORTs in git, affinity, pace-hunt, snow, onscreen-trial, display, trial, tmp, archive, boot-logs, codegen, panic-fix, m5/m6/m7/vk stubs, 4 loose top-level files). No open refs. |  |
| ps2x-p1y | 12.69 | 10106 | 2026-09-19 | ASK | 13GB P-lane build tree + fork checkout with LOCAL branch ssx3 @c41efce (I7/P1y commits); push-state unverified (V2 read-only). Verify `git branch -r --contains c41efce` / E32 fold before deleting. |  |
| android-spike/report-dirs-D1-D2-D4-D5-D6-D8-m4 | 11.64 | 4351 | 2026-09-18 | KEEP-SOLE | Sole REPORT.md + receipts + patches behind numbers-ledger rows (D1/D2/D4/D5/D6/D8/M4); no git copies (research has no D*/M4 dirs). D route is reserve-parked. |  |
| tmp-evacuated-0918 | 11.36 | 5792 | 2026-09-18 | DELETE-STALE | Retired-laptop /tmp overflow (ssx3-f120 spike tree, codegen-spike, pace/snow, android-display...); closed scratch; no open refs. |  |
| ps2recomp-spike/PS2Recomp | 11.31 | 10340 | 2026-09-22 | KEEP-LIVE | E31 PASS (15803f4: stock race on Mac); E31 brief owns worktree+P1/run+e29-build; E32 brief folds from this worktree (fork ssx3, remote fork). |  |
| ps2x-i7 | 10.85 | 9959 | 2026-09-19 | KEEP-SOLE | Parked I lane (todo: re-probe after E30; E32 folds i23-ffmpeg-ios + branchless I10-I21): SSD-only work inputs; fork-wt dirs hold unique pre-fold refs (todo V). Release after E32 lands. |  |
| ps2recomp-spike/e31-noaggr-build | 10.83 | 7346 | 2026-09-22 | KEEP-LIVE | E31 PASS (15803f4: stock race on Mac); E31 brief owns worktree+P1/run+e29-build; E32 brief folds from this worktree (fork ssx3, remote fork). |  |
| ps2x-i23 | 9.57 | 5631 | 2026-09-21 | KEEP-SOLE | Parked I lane (todo: re-probe after E30; E32 folds i23-ffmpeg-ios + branchless I10-I21): SSD-only work inputs; fork-wt dirs hold unique pre-fold refs (todo V). Release after E32 lands. |  |
| ps2x-i3 | 9.21 | 8758 | 2026-09-19 | KEEP-SOLE | Parked I lane (todo: re-probe after E30; E32 folds i23-ffmpeg-ios + branchless I10-I21): SSD-only work inputs; fork-wt dirs hold unique pre-fold refs (todo V). Release after E32 lands. |  |
| ps2x-i21 | 8.87 | 5259 | 2026-09-21 | KEEP-SOLE | Parked I lane (todo: re-probe after E30; E32 folds i23-ffmpeg-ios + branchless I10-I21): SSD-only work inputs; fork-wt dirs hold unique pre-fold refs (todo V). Release after E32 lands. |  |
| ps2x-i18 | 8.85 | 5266 | 2026-09-21 | KEEP-SOLE | Parked I lane (todo: re-probe after E30; E32 folds i23-ffmpeg-ios + branchless I10-I21): SSD-only work inputs; fork-wt dirs hold unique pre-fold refs (todo V). Release after E32 lands. |  |
| ps2x-i2-desktop | 8.1 | 6645 | 2026-09-19 | DELETE-REBUILDABLE | Superseded I-lane cmake build trees (_deps/CMakeCache present); sources live in fork/ssx3 + I REPORTs in git. | fork + git REPORTs |
| q3-siblings | 7.43 | 6962 | 2026-09-18 | DELETE-STALE | Closed survey checkouts of public upstream repos, no .git recorded; nothing open references them; re-clonable from GitHub. |  |
| fork-survey | 7.24 | 5615 | 2026-09-18 | DELETE-STALE | Closed survey checkouts of public upstream repos, no .git recorded; nothing open references them; re-clonable from GitHub. |  |
| pcsx2-ref | 6.22 | 5986 | 2026-09-18 | DELETE-REBUILDABLE | Public clone with .git (origin github.com/pcsx2/pcsx2, @1275b25); T lane builds on bytesize. | github.com/pcsx2/pcsx2 |
| m16 | 6.06 | 6147 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| ps2x-i6 | 5.39 | 4958 | 2026-09-19 | KEEP-SOLE | Parked I lane (todo: re-probe after E30; E32 folds i23-ffmpeg-ios + branchless I10-I21): SSD-only work inputs; fork-wt dirs hold unique pre-fold refs (todo V). Release after E32 lands. |  |
| ps2x-i8 | 5.25 | 4016 | 2026-09-20 | KEEP-SOLE | Parked I lane (todo: re-probe after E30; E32 folds i23-ffmpeg-ios + branchless I10-I21): SSD-only work inputs; fork-wt dirs hold unique pre-fold refs (todo V). Release after E32 lands. |  |
| ps2x-ios-spike-attempt1 | 4.74 | 4027 | 2026-09-19 | DELETE-REBUILDABLE | Superseded I-lane cmake build trees (_deps/CMakeCache present); sources live in fork/ssx3 + I REPORTs in git. | fork + git REPORTs |
| parallel-gs-g27-hwasan-build | 4.59 | 1567 | 2026-09-21 | DELETE-REBUILDABLE | Closed-G build tree; inputs = public clone ~/dev/parallel-gs @3a66c19 + carried G26/G28 hunks (G39 decision); no open brief pins these binaries (V1 pins are history). | rebuild per lane recipe |
| parallel-gs-g15-hwasan-build | 4.59 | 1566 | 2026-09-21 | DELETE-REBUILDABLE | Closed-G build tree; inputs = public clone ~/dev/parallel-gs @3a66c19 + carried G26/G28 hunks (G39 decision); no open brief pins these binaries (V1 pins are history). | rebuild per lane recipe |
| mini-transfer-0922 | 4.59 | 18 | 2026-09-22 | DELETE-STALE | Mini bring-up tars (ssx3-local, other-dev-repos, agent-state, worker-tmp + .sha256); cutover complete, mini up (smoke 458/458 per status); payloads live on internal. |  |
| parallel-gs-g16-asan-build | 4.37 | 1755 | 2026-09-21 | DELETE-REBUILDABLE | Closed-G build tree; inputs = public clone ~/dev/parallel-gs @3a66c19 + carried G26/G28 hunks (G39 decision); no open brief pins these binaries (V1 pins are history). | rebuild per lane recipe |
| parallel-gs-g42-android-build | 4.27 | 1567 | 2026-09-22 | KEEP-LIVE | Named live readers in V2 brief (G42 Turnip contrast). |  |
| parallel-gs-g41-android-build | 4.27 | 1567 | 2026-09-22 | DELETE-REBUILDABLE | Closed-G build tree; inputs = public clone ~/dev/parallel-gs @3a66c19 + carried G26/G28 hunks (G39 decision); no open brief pins these binaries (V1 pins are history). | rebuild per lane recipe |
| parallel-gs-g40-android-build | 4.27 | 1567 | 2026-09-22 | DELETE-REBUILDABLE | Closed-G build tree; inputs = public clone ~/dev/parallel-gs @3a66c19 + carried G26/G28 hunks (G39 decision); no open brief pins these binaries (V1 pins are history). | rebuild per lane recipe |
| parallel-gs-g37-android-build | 4.27 | 1567 | 2026-09-22 | DELETE-REBUILDABLE | Closed-G build tree; inputs = public clone ~/dev/parallel-gs @3a66c19 + carried G26/G28 hunks (G39 decision); no open brief pins these binaries (V1 pins are history). | rebuild per lane recipe |
| parallel-gs-g36-android-build | 4.27 | 1567 | 2026-09-22 | DELETE-REBUILDABLE | Closed-G build tree; inputs = public clone ~/dev/parallel-gs @3a66c19 + carried G26/G28 hunks (G39 decision); no open brief pins these binaries (V1 pins are history). | rebuild per lane recipe |
| parallel-gs-g35-android-build | 4.27 | 1567 | 2026-09-22 | DELETE-REBUILDABLE | Closed-G build tree; inputs = public clone ~/dev/parallel-gs @3a66c19 + carried G26/G28 hunks (G39 decision); no open brief pins these binaries (V1 pins are history). | rebuild per lane recipe |
| parallel-gs-g34-android-build | 4.27 | 1567 | 2026-09-22 | DELETE-REBUILDABLE | Closed-G build tree; inputs = public clone ~/dev/parallel-gs @3a66c19 + carried G26/G28 hunks (G39 decision); no open brief pins these binaries (V1 pins are history). | rebuild per lane recipe |
| parallel-gs-g33-android-build | 4.27 | 1567 | 2026-09-22 | DELETE-REBUILDABLE | Closed-G build tree; inputs = public clone ~/dev/parallel-gs @3a66c19 + carried G26/G28 hunks (G39 decision); no open brief pins these binaries (V1 pins are history). | rebuild per lane recipe |
| parallel-gs-g32-android-build | 4.27 | 1567 | 2026-09-21 | DELETE-REBUILDABLE | Closed-G build tree; inputs = public clone ~/dev/parallel-gs @3a66c19 + carried G26/G28 hunks (G39 decision); no open brief pins these binaries (V1 pins are history). | rebuild per lane recipe |
| parallel-gs-g31-android-build | 4.27 | 1567 | 2026-09-21 | DELETE-REBUILDABLE | Closed-G build tree; inputs = public clone ~/dev/parallel-gs @3a66c19 + carried G26/G28 hunks (G39 decision); no open brief pins these binaries (V1 pins are history). | rebuild per lane recipe |
| parallel-gs-g30-android-build | 4.27 | 1567 | 2026-09-21 | DELETE-REBUILDABLE | Closed-G build tree; inputs = public clone ~/dev/parallel-gs @3a66c19 + carried G26/G28 hunks (G39 decision); no open brief pins these binaries (V1 pins are history). | rebuild per lane recipe |
| parallel-gs-g29-android-build | 4.27 | 1567 | 2026-09-21 | DELETE-REBUILDABLE | Closed-G build tree; inputs = public clone ~/dev/parallel-gs @3a66c19 + carried G26/G28 hunks (G39 decision); no open brief pins these binaries (V1 pins are history). | rebuild per lane recipe |
| parallel-gs-g28-android-build | 4.27 | 1567 | 2026-09-21 | DELETE-REBUILDABLE | Closed-G build tree; inputs = public clone ~/dev/parallel-gs @3a66c19 + carried G26/G28 hunks (G39 decision); no open brief pins these binaries (V1 pins are history). | rebuild per lane recipe |
| parallel-gs-g26-android-build | 4.27 | 1567 | 2026-09-21 | DELETE-REBUILDABLE | Closed-G build tree; inputs = public clone ~/dev/parallel-gs @3a66c19 + carried G26/G28 hunks (G39 decision); no open brief pins these binaries (V1 pins are history). | rebuild per lane recipe |
| parallel-gs-g24-android-build | 4.27 | 1567 | 2026-09-21 | DELETE-REBUILDABLE | Closed-G build tree; inputs = public clone ~/dev/parallel-gs @3a66c19 + carried G26/G28 hunks (G39 decision); no open brief pins these binaries (V1 pins are history). | rebuild per lane recipe |
| parallel-gs-g22-android-build | 4.27 | 1567 | 2026-09-21 | DELETE-REBUILDABLE | Closed-G build tree; inputs = public clone ~/dev/parallel-gs @3a66c19 + carried G26/G28 hunks (G39 decision); no open brief pins these binaries (V1 pins are history). | rebuild per lane recipe |
| parallel-gs-g20-android-build | 4.27 | 1567 | 2026-09-21 | DELETE-REBUILDABLE | Closed-G build tree; inputs = public clone ~/dev/parallel-gs @3a66c19 + carried G26/G28 hunks (G39 decision); no open brief pins these binaries (V1 pins are history). | rebuild per lane recipe |
| parallel-gs-g18-android-build | 4.27 | 1567 | 2026-09-21 | DELETE-REBUILDABLE | Closed-G build tree; inputs = public clone ~/dev/parallel-gs @3a66c19 + carried G26/G28 hunks (G39 decision); no open brief pins these binaries (V1 pins are history). | rebuild per lane recipe |
| parallel-gs-g14-android-build | 4.27 | 1566 | 2026-09-21 | DELETE-REBUILDABLE | Closed-G build tree; inputs = public clone ~/dev/parallel-gs @3a66c19 + carried G26/G28 hunks (G39 decision); no open brief pins these binaries (V1 pins are history). | rebuild per lane recipe |
| parallel-gs-g42-mac-build | 3.63 | 1755 | 2026-09-22 | KEEP-LIVE | Named live readers in V2 brief (G42 Turnip contrast). |  |
| parallel-gs-g40-mac-build | 3.63 | 1755 | 2026-09-22 | DELETE-REBUILDABLE | Closed-G build tree; inputs = public clone ~/dev/parallel-gs @3a66c19 + carried G26/G28 hunks (G39 decision); no open brief pins these binaries (V1 pins are history). | rebuild per lane recipe |
| parallel-gs-g38-mac-build | 3.63 | 1755 | 2026-09-22 | DELETE-REBUILDABLE | Closed-G build tree; inputs = public clone ~/dev/parallel-gs @3a66c19 + carried G26/G28 hunks (G39 decision); no open brief pins these binaries (V1 pins are history). | rebuild per lane recipe |
| parallel-gs-g7-build | 3.63 | 1754 | 2026-09-20 | DELETE-REBUILDABLE | Closed-G build tree; inputs = public clone ~/dev/parallel-gs @3a66c19 + carried G26/G28 hunks (G39 decision); no open brief pins these binaries (V1 pins are history). | rebuild per lane recipe |
| parallel-gs-g41-mac-build | 3.63 | 1754 | 2026-09-22 | DELETE-REBUILDABLE | Closed-G build tree; inputs = public clone ~/dev/parallel-gs @3a66c19 + carried G26/G28 hunks (G39 decision); no open brief pins these binaries (V1 pins are history). | rebuild per lane recipe |
| ps2x-i9 | 3.24 | 2853 | 2026-09-20 | KEEP-SOLE | Parked I lane (todo: re-probe after E30; E32 folds i23-ffmpeg-ios + branchless I10-I21): SSD-only work inputs; fork-wt dirs hold unique pre-fold refs (todo V). Release after E32 lands. |  |
| ps2x-i24 | 2.95 | 11 | 2026-09-22 | KEEP-SOLE | Parked I lane (todo: re-probe after E30; E32 folds i23-ffmpeg-ios + branchless I10-I21): SSD-only work inputs; fork-wt dirs hold unique pre-fold refs (todo V). Release after E32 lands. |  |
| ps2recomp-spike/SSX 3 (USA).iso | 2.8 | 1 | 2026-09-22 | DELETE-MIRRORED | Size match 3005415424 B SSD<->internal E32-inputs (no hash: >1GB cap). | ~/dev/ssx3-work/E32-inputs/SSX 3 (USA).iso |
| timemachine | 2.69 | 1047 | 2024-12-05 | NOT-SSX3 | NOT-SSX3: Brad's own data; size+mtime only, never opened; Brad decides. |  |
| ps2x-t4/emulog-t46r3.txt | 2.5 | 1 | 2026-09-22 | KEEP-SOLE | V1 AUDIT row 23: FULL pin, SSD-only fresh (absent from share 2026-09-23); T-lane loading-timeline reference. |  |
| ps2x-ios-spike-attempt3 | 1.37 | 1199 | 2026-09-19 | DELETE-REBUILDABLE | Superseded I-lane cmake build trees (_deps/CMakeCache present); sources live in fork/ssx3 + I REPORTs in git. | fork + git REPORTs |
| ps2x-i2-ios-b | 1.19 | 1113 | 2026-09-19 | DELETE-REBUILDABLE | Superseded I-lane cmake build trees (_deps/CMakeCache present); sources live in fork/ssx3 + I REPORTs in git. | fork + git REPORTs |
| ssxdecomp-ssx3 | 1.05 | 953 | 2026-09-18 | DELETE-REBUILDABLE | Public clone with .git (origin ssxdecomp/ssx3 @9cd4626). | github.com/ssxdecomp/ssx3 |
| dobiestation-q4 | 0.84 | 806 | 2026-09-18 | DELETE-REBUILDABLE | Public clone with .git (origin PSI-Rockin/DobieStation @68dd073); closed Q survey. | github.com/PSI-Rockin/DobieStation |
| ps2xgs | 0.7 | 205 | 2026-09-18 | KEEP-SOLE | Sole .gscap captures (atest-*) pinned by committed ps2xGS docs/reports/G0,G2,G3; not tracked in ~/dev/ps2xGS git; G lane open. |  |
| ps2x-i19 | 0.7 | 616 | 2026-09-21 | KEEP-SOLE | Parked I lane (todo: re-probe after E30; E32 folds i23-ffmpeg-ios + branchless I10-I21): SSD-only work inputs; fork-wt dirs hold unique pre-fold refs (todo V). Release after E32 lands. |  |
| ps2x-i20 | 0.69 | 614 | 2026-09-21 | KEEP-SOLE | Parked I lane (todo: re-probe after E30; E32 folds i23-ffmpeg-ios + branchless I10-I21): SSD-only work inputs; fork-wt dirs hold unique pre-fold refs (todo V). Release after E32 lands. |  |
| bradflix-ps2recomp | 0.68 | 587 | 2026-09-18 | ASK | Unplaced: sessions/ with UUID-named files (0.7GB); no repo references found (grep 2026-09-23). Needs call. |  |
| ps2x-i2-ios-a | 0.53 | 451 | 2026-09-19 | DELETE-REBUILDABLE | Superseded I-lane cmake build trees (_deps/CMakeCache present); sources live in fork/ssx3 + I REPORTs in git. | fork + git REPORTs |
| n2-android | 0.49 | 105 | 2026-09-22 | KEEP-LIVE | Named live reader in V2 brief (N APK source of truth). |  |
| ps2x-e30 | 0.44 | 396 | 2026-09-22 | DELETE-STALE | E30 PASS(design): fix + regression diffs carried by E33 brief; scratch dir only. E30 REPORT in git; no open refs. |  |
| Godot | 0.43 | 108 | 2026-09-08 | NOT-SSX3 | NOT-SSX3: Brad's own data; size+mtime only, never opened; Brad decides. |  |
| m11 | 0.38 | 215 | 2026-09-19 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| Screen Recording 2026-09-12 at 2.59.35 PM.mov | 0.37 | 1 | 2026-09-12 | NOT-SSX3 | NOT-SSX3: Brad's own data; size+mtime only, never opened; Brad decides. |  |
| m5 | 0.28 | 134 | 2026-09-18 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m10 | 0.28 | 141 | 2026-09-19 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| n2-scratch | 0.26 | 2 | 2026-09-22 | DELETE-MIRRORED | c17-codegen.tar: 9458 members vs 9457 files in internal ~/dev/ssx3-work/codegen-ssx3 (tar self-entry). | ~/dev/ssx3-work/codegen-ssx3 |
| pf1 | 0.25 | 238 | 2026-09-22 | KEEP-LIVE | Named live reader in V2 brief (PF1 runs). |  |
| bradflix-bkp | 0.21 | 204 | 2024-12-05 | NOT-SSX3 | NOT-SSX3: Brad's own data; size+mtime only, never opened; Brad decides. |  |
| m7 | 0.2 | 82 | 2026-09-19 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m6 | 0.18 | 83 | 2026-09-18 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m9 | 0.16 | 84 | 2026-09-19 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m14 | 0.16 | 86 | 2026-09-19 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m8 | 0.15 | 78 | 2026-09-19 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m13 | 0.14 | 84 | 2026-09-19 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m12 | 0.11 | 82 | 2026-09-19 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m15 | 0.08 | 50 | 2026-09-19 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| ps2x-g42 | 0.08 | 64 | 2026-09-22 | KEEP-LIVE | Named live reader in V2 brief (G42 dump+receipts). |  |
| ps2x-g41 | 0.07 | 60 | 2026-09-22 | DELETE-MIRRORED | Share mirrors present; spot 2026-09-23: g41-dump.gs SSD<->share SHA match (154d9d85, =G13 dump); g41 counts 30 SSD vs 31 share. | /Volumes/share/ssx3/<same> |
| ps2x-p13 | 0.04 | 40 | 2026-09-20 | DELETE-STALE | Closed-P13 ELF sweep outputs; P13 REPORT in git; no open refs. |  |
| ps2x-g16 | 0.04 | 30 | 2026-09-21 | DELETE-STALE | Closed-G receipts + superseded GS dumps (G42 uses g42-dump; G13 dump mirrored internal). REPORTs in git; closed-report refs are history per brief. | share mirrors for g33+ only; g7-32 SSD-only |
| ps2x-g10 | 0.04 | 36 | 2026-09-20 | DELETE-STALE | Closed-G receipts + superseded GS dumps (G42 uses g42-dump; G13 dump mirrored internal). REPORTs in git; closed-report refs are history per brief. | share mirrors for g33+ only; g7-32 SSD-only |
| ps2x-t47 | 0.04 | 38 | 2026-09-22 | KEEP-LIVE | Named live reader in V2 brief (T47 shots). |  |
| ps2x-g40 | 0.04 | 30 | 2026-09-22 | DELETE-MIRRORED | Share mirrors present; spot 2026-09-23: g41-dump.gs SSD<->share SHA match (154d9d85, =G13 dump); g41 counts 30 SSD vs 31 share. | /Volumes/share/ssx3/<same> |
| ps2x-g38 | 0.03 | 28 | 2026-09-22 | DELETE-MIRRORED | Share mirrors present; spot 2026-09-23: g41-dump.gs SSD<->share SHA match (154d9d85, =G13 dump); g41 counts 30 SSD vs 31 share. | /Volumes/share/ssx3/<same> |
| ps2x-g15 | 0.03 | 30 | 2026-09-21 | DELETE-STALE | Closed-G receipts + superseded GS dumps (G42 uses g42-dump; G13 dump mirrored internal). REPORTs in git; closed-report refs are history per brief. | share mirrors for g33+ only; g7-32 SSD-only |
| m31 | 0.03 | 29 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| ps2x-g9 | 0.03 | 18 | 2026-09-20 | DELETE-STALE | Closed-G receipts + superseded GS dumps (G42 uses g42-dump; G13 dump mirrored internal). REPORTs in git; closed-report refs are history per brief. | share mirrors for g33+ only; g7-32 SSD-only |
| ps2x-g27 | 0.03 | 28 | 2026-09-21 | DELETE-STALE | Closed-G receipts + superseded GS dumps (G42 uses g42-dump; G13 dump mirrored internal). REPORTs in git; closed-report refs are history per brief. | share mirrors for g33+ only; g7-32 SSD-only |
| ps2x-g11 | 0.03 | 22 | 2026-09-20 | DELETE-STALE | Closed-G receipts + superseded GS dumps (G42 uses g42-dump; G13 dump mirrored internal). REPORTs in git; closed-report refs are history per brief. | share mirrors for g33+ only; g7-32 SSD-only |
| ps2x-i22 | 0.03 | 14 | 2026-09-21 | KEEP-SOLE | Parked I lane (todo: re-probe after E30; E32 folds i23-ffmpeg-ios + branchless I10-I21): SSD-only work inputs; fork-wt dirs hold unique pre-fold refs (todo V). Release after E32 lands. |  |
| m32 | 0.03 | 25 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| ps2x-g37 | 0.02 | 26 | 2026-09-22 | DELETE-MIRRORED | V1 AUDIT rows 12-16: PPMs agree+stable, logs agree, SSD<->share. | /Volumes/share/ssx3/<same> |
| ps2x-g36 | 0.02 | 26 | 2026-09-22 | DELETE-MIRRORED | V1 AUDIT rows 12-16: PPMs agree+stable, logs agree, SSD<->share. | /Volumes/share/ssx3/<same> |
| ps2x-g34 | 0.02 | 26 | 2026-09-22 | DELETE-MIRRORED | V1 AUDIT rows 12-16: PPMs agree+stable, logs agree, SSD<->share. | /Volumes/share/ssx3/<same> |
| ps2x-g33 | 0.02 | 26 | 2026-09-22 | DELETE-MIRRORED | V1 AUDIT rows 12-16: PPMs agree+stable, logs agree, SSD<->share. | /Volumes/share/ssx3/<same> |
| ps2x-g32 | 0.02 | 26 | 2026-09-21 | DELETE-STALE | Closed-G receipts + superseded GS dumps (G42 uses g42-dump; G13 dump mirrored internal). REPORTs in git; closed-report refs are history per brief. | share mirrors for g33+ only; g7-32 SSD-only |
| ps2x-g30 | 0.02 | 26 | 2026-09-21 | DELETE-STALE | Closed-G receipts + superseded GS dumps (G42 uses g42-dump; G13 dump mirrored internal). REPORTs in git; closed-report refs are history per brief. | share mirrors for g33+ only; g7-32 SSD-only |
| ps2x-g29 | 0.02 | 26 | 2026-09-21 | DELETE-STALE | Closed-G receipts + superseded GS dumps (G42 uses g42-dump; G13 dump mirrored internal). REPORTs in git; closed-report refs are history per brief. | share mirrors for g33+ only; g7-32 SSD-only |
| ps2x-g28 | 0.02 | 26 | 2026-09-21 | DELETE-STALE | Closed-G receipts + superseded GS dumps (G42 uses g42-dump; G13 dump mirrored internal). REPORTs in git; closed-report refs are history per brief. | share mirrors for g33+ only; g7-32 SSD-only |
| ps2x-g22 | 0.02 | 24 | 2026-09-21 | DELETE-STALE | Closed-G receipts + superseded GS dumps (G42 uses g42-dump; G13 dump mirrored internal). REPORTs in git; closed-report refs are history per brief. | share mirrors for g33+ only; g7-32 SSD-only |
| ps2x-g35 | 0.02 | 25 | 2026-09-22 | DELETE-MIRRORED | V1 AUDIT rows 12-16: PPMs agree+stable, logs agree, SSD<->share. | /Volumes/share/ssx3/<same> |
| ps2x-g39 | 0.02 | 24 | 2026-09-22 | DELETE-MIRRORED | Share mirrors present; spot 2026-09-23: g41-dump.gs SSD<->share SHA match (154d9d85, =G13 dump); g41 counts 30 SSD vs 31 share. | /Volumes/share/ssx3/<same> |
| m30 | 0.02 | 21 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m18 | 0.02 | 21 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| ps2x-g13/rest-22-files | 0.02 | 22 | 2026-09-21 | KEEP-SOLE | V1 AUDIT.md rows 10-11: dump mirrored internal (sha 154d9d85 match), other 22 files SSD-only (emulog, PPMs, PNGs, markers, window trace). | internal g13/ holds dump only |
| m43 | 0.02 | 19 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m36 | 0.02 | 19 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m17 | 0.02 | 19 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m53 | 0.02 | 17 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m50 | 0.02 | 17 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m44 | 0.02 | 17 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m34 | 0.02 | 17 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m33 | 0.02 | 17 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m28 | 0.02 | 17 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m25 | 0.02 | 17 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| ps2x-i5 | 0.02 | 17 | 2026-09-19 | KEEP-SOLE | Parked I lane (todo: re-probe after E30; E32 folds i23-ffmpeg-ios + branchless I10-I21): SSD-only work inputs; fork-wt dirs hold unique pre-fold refs (todo V). Release after E32 lands. |  |
| ps2x-p1z/traces | 0.02 | 8 | 2026-09-19 | DELETE-STALE | Closed-P kernel-trace texts; P-lane closed; no open refs (BIOS file split to DELETE-MIRRORED). |  |
| ps2x-g17 | 0.02 | 16 | 2026-09-21 | DELETE-STALE | Closed-G receipts + superseded GS dumps (G42 uses g42-dump; G13 dump mirrored internal). REPORTs in git; closed-report refs are history per brief. | share mirrors for g33+ only; g7-32 SSD-only |
| m63 | 0.02 | 15 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m62 | 0.02 | 15 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m61 | 0.02 | 15 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m60 | 0.02 | 15 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m59 | 0.02 | 15 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m58 | 0.02 | 15 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m57 | 0.02 | 15 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m56 | 0.02 | 15 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m55 | 0.02 | 15 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m54 | 0.02 | 15 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m52 | 0.02 | 15 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m51 | 0.02 | 15 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m49 | 0.02 | 15 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m48 | 0.02 | 15 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m47 | 0.02 | 15 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m46 | 0.02 | 15 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m45 | 0.02 | 15 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m42 | 0.02 | 15 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m41 | 0.02 | 15 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m40 | 0.02 | 15 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m39 | 0.02 | 15 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m38 | 0.02 | 15 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m37 | 0.02 | 15 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m35 | 0.02 | 15 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m29 | 0.02 | 15 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m27 | 0.02 | 15 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m26 | 0.02 | 15 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m24 | 0.02 | 15 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| ps2x-g8 | 0.02 | 10 | 2026-09-20 | DELETE-STALE | Closed-G receipts + superseded GS dumps (G42 uses g42-dump; G13 dump mirrored internal). REPORTs in git; closed-report refs are history per brief. | share mirrors for g33+ only; g7-32 SSD-only |
| ps2x-g21 | 0.01 | 14 | 2026-09-21 | DELETE-STALE | Closed-G receipts + superseded GS dumps (G42 uses g42-dump; G13 dump mirrored internal). REPORTs in git; closed-report refs are history per brief. | share mirrors for g33+ only; g7-32 SSD-only |
| m23 | 0.01 | 13 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m22 | 0.01 | 13 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m21 | 0.01 | 13 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| m20 | 0.01 | 13 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| ps2x-g7 | 0.01 | 7 | 2026-09-20 | DELETE-STALE | Closed-G receipts + superseded GS dumps (G42 uses g42-dump; G13 dump mirrored internal). REPORTs in git; closed-report refs are history per brief. | share mirrors for g33+ only; g7-32 SSD-only |
| m19 | 0.01 | 11 | 2026-09-20 | DELETE-STALE | Closed-lane scratch: REPORT committed in git (local/research/<ID>/REPORT.md); no references from open items (docs/status.md, docs/todo.md, open briefs E31/E32/G42/PF1/T47 checked 2026-09-23). |  |
| ps2x-g13/g13-dump.gs | 0.01 | 1 | 2026-09-21 | DELETE-MIRRORED | SHA 154d9d8577a2... match SSD<->internal (V1 pin). | ~/dev/ssx3-inputs/g13/g13-dump.gs |
| ps2x-g20 | 0.01 | 10 | 2026-09-21 | DELETE-STALE | Closed-G receipts + superseded GS dumps (G42 uses g42-dump; G13 dump mirrored internal). REPORTs in git; closed-report refs are history per brief. | share mirrors for g33+ only; g7-32 SSD-only |
| ps2x-g23 | 0.01 | 8 | 2026-09-21 | DELETE-STALE | Closed-G receipts + superseded GS dumps (G42 uses g42-dump; G13 dump mirrored internal). REPORTs in git; closed-report refs are history per brief. | share mirrors for g33+ only; g7-32 SSD-only |
| ps2x-g12 | 0.01 | 8 | 2026-09-21 | DELETE-STALE | Closed-G receipts + superseded GS dumps (G42 uses g42-dump; G13 dump mirrored internal). REPORTs in git; closed-report refs are history per brief. | share mirrors for g33+ only; g7-32 SSD-only |
| ps2x-g14 | 0.01 | 6 | 2026-09-21 | DELETE-STALE | Closed-G receipts + superseded GS dumps (G42 uses g42-dump; G13 dump mirrored internal). REPORTs in git; closed-report refs are history per brief. | share mirrors for g33+ only; g7-32 SSD-only |
| ps2x-g31 | 0.0 | 6 | 2026-09-21 | DELETE-STALE | Closed-G receipts + superseded GS dumps (G42 uses g42-dump; G13 dump mirrored internal). REPORTs in git; closed-report refs are history per brief. | share mirrors for g33+ only; g7-32 SSD-only |
| ps2x-g26 | 0.0 | 4 | 2026-09-21 | DELETE-STALE | Closed-G receipts + superseded GS dumps (G42 uses g42-dump; G13 dump mirrored internal). REPORTs in git; closed-report refs are history per brief. | share mirrors for g33+ only; g7-32 SSD-only |
| ps2x-g25 | 0.0 | 4 | 2026-09-21 | DELETE-STALE | Closed-G receipts + superseded GS dumps (G42 uses g42-dump; G13 dump mirrored internal). REPORTs in git; closed-report refs are history per brief. | share mirrors for g33+ only; g7-32 SSD-only |
| ps2x-g24 | 0.0 | 4 | 2026-09-21 | DELETE-STALE | Closed-G receipts + superseded GS dumps (G42 uses g42-dump; G13 dump mirrored internal). REPORTs in git; closed-report refs are history per brief. | share mirrors for g33+ only; g7-32 SSD-only |
| ps2x-g19 | 0.0 | 4 | 2026-09-21 | DELETE-STALE | Closed-G receipts + superseded GS dumps (G42 uses g42-dump; G13 dump mirrored internal). REPORTs in git; closed-report refs are history per brief. | share mirrors for g33+ only; g7-32 SSD-only |
| ps2x-g18 | 0.0 | 4 | 2026-09-21 | DELETE-STALE | Closed-G receipts + superseded GS dumps (G42 uses g42-dump; G13 dump mirrored internal). REPORTs in git; closed-report refs are history per brief. | share mirrors for g33+ only; g7-32 SSD-only |
| ps2x-p1z/ps2-bios-0200a-20040614-100909.bin | 0.0 | 1 | 2026-09-19 | DELETE-MIRRORED | SHA 6d23d001daf2... match SSD<->share (file <1GB, hashed 2026-09-23). | /Volumes/share/brad/games/ps2/<same> |
| System Volume Information | 0.0 | 2 | 2024-10-19 | NOT-SSX3 | NOT-SSX3: Brad's own data; size+mtime only, never opened; Brad decides. |  |
| Screenshot 2026-09-18 at 7.53.11 AM.png | 0.0 | 1 | 2026-09-18 | NOT-SSX3 | NOT-SSX3: Brad's own data; size+mtime only, never opened; Brad decides. |  |
| Screenshot 2026-09-17 at 10.22.31 PM.png | 0.0 | 1 | 2026-09-17 | NOT-SSX3 | NOT-SSX3: Brad's own data; size+mtime only, never opened; Brad decides. |  |
| Screenshot 2026-09-18 at 7.54.24 AM.png | 0.0 | 1 | 2026-09-18 | NOT-SSX3 | NOT-SSX3: Brad's own data; size+mtime only, never opened; Brad decides. |  |
| Screenshot 2026-09-14 at 7.38.03 AM.png | 0.0 | 1 | 2026-09-14 | NOT-SSX3 | NOT-SSX3: Brad's own data; size+mtime only, never opened; Brad decides. |  |
| Screenshot 2026-09-14 at 7.36.38 AM.png | 0.0 | 1 | 2026-09-14 | NOT-SSX3 | NOT-SSX3: Brad's own data; size+mtime only, never opened; Brad decides. |  |
| Screenshot 2026-09-12 at 3.35.00 PM.png | 0.0 | 1 | 2026-09-12 | NOT-SSX3 | NOT-SSX3: Brad's own data; size+mtime only, never opened; Brad decides. |  |
| Screenshot 2026-09-12 at 3.18.36 PM.png | 0.0 | 1 | 2026-09-12 | NOT-SSX3 | NOT-SSX3: Brad's own data; size+mtime only, never opened; Brad decides. |  |
| Screenshot 2026-09-12 at 3.01.47 PM.png | 0.0 | 1 | 2026-09-12 | NOT-SSX3 | NOT-SSX3: Brad's own data; size+mtime only, never opened; Brad decides. |  |
| ps2x-p1x | 0.0 | 0 | 2026-09-19 | DELETE-STALE | Empty dir (~1MB ExFAT slack); P1x REPORT in git; no open refs. |  |

## Recommended next actions (orchestrator decides)

1. Delete all DELETE-REBUILDABLE + DELETE-MIRRORED rows first (~lowest risk; rebuild recipes and mirror locations in table).
2. Delete DELETE-STALE after confirming no open brief has picked the names back up.
3. Resolve ASK rows with Brad (NOT-SSX3-adjacent and reserve-route data).
4. Release KEEP-SOLE I-lane rows after the E32 fold lands; re-check T46r3 after T47 gates.

