# V1 Mission 1 — audit (DRAFT: table filled after PASS2/compare)

## Method (how every byte below was read)

- Two full passes (`v1_audit.py pass1|pass2`): per-file stat (bytes+mtime) +
  full SHA256, every Mission-1 path, `COPYFILE_DISABLE=1`, `._*` sidecars
  counted and never hashed. Inter-pass gap recorded per file (target ≥20 min
  on lane-critical bytes — G33's transient held ~10 min across 4 reads).
- Corroboration tiers: Tier-1 = `git HEAD` blobs at `ba7422d` (pins in
  `v1_pins.json`, 7559 entries, each literal machine-verified present in its
  blob); Tier-2 = uncommitted-but-prior lane receipts (supporting only).
- Agreement groups: SSD↔share↔live per file; committed slices (`slices.json`,
  39/39 head+tail byte-exact at draft) for 19 T4 files.
- HEAD walked mid-lane (`e77d83c` → `8e84791` [E28] → `ba7422d` [T46]);
  pins re-extracted and re-verified at the final HEAD. G38 started mid-lane
  (~11:39 ET); all V1 paths are disjoint from G38's (`/tmp/g38-*`,
  `parallel-gs-g38-mac-build/`, `ps2x-g38/`); clone dirt compared open-vs-close.
- Fork ops: `rev-parse` + `status` only. Zero lane-output mutations (see
  worktrees-open/close + final `git status`).

## Pins that could NOT be corroborated (exact list)

No Tier-1 committed bytes exist for these; V1 quotes them with 2-read
stability + cross-copy agreement ONLY:

| # | Bytes | Why uncorroborated |
|---|---|---|
| U1 | G logcat/run-stdout/stderr (15 files × SSD+share) | lanes pin counts/values, never file shas |
| U2 | `emulog-pre-t42-*.txt` ×3 (× SSD+share) | T42 REPORT pins nothing for them (timestamps unreferenced) |
| U3 | `emulog-pre-t17auto-…` sha | T17: size-only pin ("not taken") |
| U4 | W binary/lib FULL shas | I24 commits prefix/tail/size only (`edb3eadce3ff9d03...0c60c1`, `f356aaa7ddfd9643...2addcd`) |
| U5 | `ps2x-g13/` non-dump files (22) | G13 evidence carries zero 64-hex pins |
| U6 | `P1/cd/PAD0.000`, `PAD1.000` | padding, never pinned |
| U7 | signed-app small files (`_CodeSignature`, `Info.plist`, `PkgInfo`, `embedded.mobileprovision`) | never pinned |
| U8 | tar member NAMES (beyond counts) | E25 pins counts (8408/7342) + per-file manifest; name-set equality rides the (untested) extract |

PARTIAL (prefix/tail/size, no full sha): 22 T4 files (see `v1_pins.json`),
W binary/lib (U4), signed-app binary `0a00e4d3…` (prefix-only in I24 REPORT —
V1's full sha is a NEW pin, stability+sole-copy noted).

## Sole-copy flags (summary; detail in table)

- SOLE-COPY ON THE CORRUPT PATH: `ps2x-g13/g13-dump.gs` (no second copy
  anywhere; G38's `ps2x-g38/` copy is transient) + the 16 other `ps2x-g13/`
  files + E25 tar (binaries mirrored; tar itself SSD-only).
- SOLE-COPY bytes, rebuildable fallback: G binaries (clone+hunks),
  signed-app binary (W binary + resign), W tree (rebuild per I23).
- Two+ copies: E25 binaries (SSD+share+live), PPMs (SSD+share), i24 logs
  (SSD+share), T4 (SSD+share, +bytesize origin for most), ELF (3 SSD copies),
  ISO (2 SSD copies), vector + observer (in-git), live tree (manifest+tar).

## Audit table (from `audit-compare.json`, gap_min=1157s gap_max=1261s)

| # | Critical path | Size | SHA (PASS1=PASS2?) | Corroboration | SOLE-COPY? |
|---|---|---|---|---|---|
| 1 | E25 tar (SSD) | 1,762,803,200 | 9ded806562f1… STABLE FULL-match | Tier-1 E25 RESTORE.md + tarlist 8408/7342 | YES (tar) — binaries mirrored; tar SSD-only |
| 2 | E25 runner SSD+share+live | 163,529,696 ×3 | e462e4482fbf… STABLE FULL-match agree=True | Tier-1 E25 RESTORE.md | NO — 3 copies agree |
| 3 | E25 suite SSD+share+live | 5,695,128 ×3 | 2152e5ad53f1… STABLE FULL-match agree=True | Tier-1 E25 RESTORE.md | NO — 3 copies (+v1-smoke 4th) |
| 4 | E25 manifest + RESTORE.md (in-git) | 7342 entries | in-git blobs (no byte reads) | Tier-1 self (HEAD blobs) | NO — git-distributed |
| 5 | G33 replayer (SSD build dir) | 265,853,048 | 7e0ea8031c6a… STABLE FULL-match magic=7f454c46 bid_match=True | Tier-1 G33 REPORT (sha+BuildID) | bytes YES — rebuildable (clone+hunks) |
| 6 | G34 replayer (SSD build dir) | 265,853,192 | 2b101ddec1cb… STABLE FULL-match magic=7f454c46 bid_match=True | Tier-1 G34 REPORT (sha+BuildID) | bytes YES — rebuildable (clone+hunks) |
| 7 | G35 replayer (SSD build dir) | 265,853,184 | e2998ffcc1f0… STABLE PIN-MISMATCH magic=00000000 bid_match=None | Tier-1 G35 REPORT (sha+BuildID) | bytes YES — rebuildable (clone+hunks) |
| 8 | G36 replayer (SSD build dir) | 265,853,160 | 6430dbe875ad… STABLE PIN-MISMATCH magic=00000000 bid_match=None | Tier-1 G36 REPORT (sha+BuildID) | bytes YES — rebuildable (clone+hunks) |
| 9 | G37 replayer (SSD build dir) | 265,853,016 | e2ed9fd85b7d… STABLE PIN-MISMATCH magic=00000000 bid_match=None | Tier-1 G37 REPORT (sha+BuildID) | bytes YES — rebuildable (clone+hunks) |
| 10 | G13 dump (SSD) | 11,537,377 | 154d9d8577a2… STABLE FULL-match | Tier-1 G35/G36/G37 REPORTs | YES — NO second copy anywhere (moves FIRST) |
| 11 | G13 other 22 files (SSD) | ~8.3 MB total | stability per-file in JSON (all checked) | U5 UNCORROBORATED (no G13 pins) | YES — SSD-only |
| 12 | ps2x-g33/ + share (13+13) | ~7 MB/side | PPMs agree+stable=True (pinned); logs agree=True (U1 unpinned) | Tier-1 scanout sha (PPMs); U1 logs | NO — SSD+share agree |
| 13 | ps2x-g34/ + share (13+13) | ~7 MB/side | PPMs agree+stable=True (pinned); logs agree=True (U1 unpinned) | Tier-1 scanout sha (PPMs); U1 logs | NO — SSD+share agree |
| 14 | ps2x-g35/ + share (13+13) | ~7 MB/side | PPMs agree+stable=True (pinned); logs agree=True (U1 unpinned) | Tier-1 scanout sha (PPMs); U1 logs | NO — SSD+share agree |
| 15 | ps2x-g36/ + share (13+13) | ~7 MB/side | PPMs agree+stable=True (pinned); logs agree=True (U1 unpinned) | Tier-1 scanout sha (PPMs); U1 logs | NO — SSD+share agree |
| 16 | ps2x-g37/ + share (13+13) | ~7 MB/side | PPMs agree+stable=True (pinned); logs agree=True (U1 unpinned) | Tier-1 scanout sha (PPMs); U1 logs | NO — SSD+share agree |
| 17 | i24 logs + mirror (3+3) | ~18 MB/side | console+2 RGBA: stability+agreement in JSON | Tier-1 console sizes + RGBA fnv | NO — SSD+share agree |
| 18 | i24 signed-app (SSD) | ~3.2 GB (ISO 3.0 GB) | per-file stability in JSON; ISO+ELF+vector pinned | Tier-1 ISO/ELF/vector; U7 small files | binary YES (resign fallback); ISO/ELF/ App-vector NO |
| 19 | W binary+lib (SSD ps2x-i23) | 122,458,696 + lib | STABLE PREFIX-match | U4 PARTIAL (prefix/tail/size) | bytes YES (rebuild per I23) |
| 20 | spike ISO + staged ISO | 3,005,415,424 ×2 | agree=True FULL-match | Tier-1 full sha | NO — 2 copies agree |
| 21 | ELF ×3 (P1, P1/cd, .app) | 3,890,784 ×3 | P1/cd FULL-match; P1-top separate 2-read; agree in JSON | Tier-1 ELF_A (E23 typo resolved by measure) | NO — 3 copies |
| 22 | P1/cd PAD0/PAD1 + SYSTEM.CNF | 268 MB ×2 + 49 B | stability in JSON | U6/U8 unpinned | YES — padding/conf, SSD-only |
| 23 | ps2x-t4/ + share (41+41) | 64.9 + 67.5 GB | 82/82 stable; FULL=32 PARTIAL=40 rows; slices 40/40 | Tier-1: 25 FULL files (22 rotation-era + variant + t46r3 + r1b), 21 PARTIAL, 1 SIZE-only; U2/U3 rest | NO (SSD+share+bytesize); t46r3 SSD-only fresh; variant share-only by design |
| 24 | live /tmp/e18-mpeg-link (7342) | 1,748,192,253 | 7342/7342 stable; 7342/7342 manifest FULL-match | Tier-1 E25 manifest (per-file) | NO — manifest+tar+live (volatile path noted) |
| 25 | /tmp/p1-link, /tmp/e17-map-link | — | absent (confirmed) | E25 loss inventory (Tier-1) | n/a — lost, orchestrator-tabled |
| 26 | worktree fork_ps2recomp | — | 3adc0478b6d2 ssx3 [?? ps2_log.txt] ref ssx3=3adc0478b6d2 remote-ssx3=3adc0478b6d2 HEAD-vs-ref=SAME | Tier-1 E25/E28 gates | n/a (git refs) |
| 27 | worktree clone_parallel_gs | — | 3a66c1976170 main [M CMakeLists.txt;  m Granite;  M gs/gs_interface.cpp;  M gs/gs_renderer.cpp;  M tools/CMak] | Tier-1 G37 REPORT | n/a (git refs) |
| 28 | worktree fork_wt_i10 | — | 3d2e22d82904 HEAD [clean] | I-lane history (detached) | n/a (git refs) |
| 29 | worktree fork_wt_i11 | — | af0a508694e8 HEAD [clean] | I-lane history (detached) | n/a (git refs) |
| 30 | ssx3 main + 6 worktrees | — | main 252bb34 clean; 2 stale-gone (prune: orch); 3 subagent dirty-detached (untouched) | rev-parse+status (read-only) | n/a (git refs) |

Worktree open-vs-close: ssx3 main HEAD advanced by orch commits (8e84791→…→39f2e6c: [T46]+[G39-brief]+[N1]) — not V1; fork HEAD moved ssx3→e29-movie-bypass @ same commit 3adc0478 (E29 checkout, ref immutable — fork-ref.json); all other worktrees byte-identical. Zero V1 mutations.

Pin-mismatch resolutions (all 5 explained, none are new corruption):
- g35/g36/g37 binaries: the GATED 14th/15th/16th read artifacts PERSIST (zeroed reads, sizes right, values identical to the gated pins e2998ffcc1f0001a/6430dbe875adcfc3/e2ed9fd85b7d16dc); V1 re-pins them with 21-min-separated reads. Run validity stands per precedent (committed build shas remain the authority for what the binaries were).
- t43r1 (both sides): probable ONE-CHAR T43 REPORT tail typo (`…e82e03` vs measured `…d82e03`); carried by prefix+size match, SSD↔share agreement ×2 passes, and committed head+tail slice bytes (40/40). V1-new full pin: `b8a27b8343c9a35b9777c283a55c65f9dcf30cb4b4fb29c779e9321c3ed82e03` (4-read agreement + slices).
- r1b (RESOLVED by upgrade): REPORT prose `b3ca14e…` drops a leading 3; R1 evidence files carry the full sha — now a FULL pin, FULL-match.
- w_lib (RESOLVED by completion): I24 prose pins prefix/tail; I17 pins the size — combined pin PREFIX-match.

Disagreements: none.
Unstable: none.
Keyset drift pass1->pass2: none.

# V1 AUDIT TAIL COMPLETE
