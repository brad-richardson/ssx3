# V1 — durable verified storage: audit, pinned restore manifest, smoke, mini-cutover

| V1 | Receipt |
|---|---|
| Stop point | **All three missions executed; nothing blocked.** 147.5 GB audited twice (7610 files, 19.3–21.0 min inter-pass gaps), 7561 Tier-1 pins machine-verified against HEAD blobs, `restore-manifest.json` written, ONE smoke restore end-to-end PASS, mini-cutover list tabled. Zero lane-output mutations, zero deletions, zero builds/boots/leases/devices. |
| Checkpoint | 7610/7610 stable across passes; 7539 pin-matches; 5 pin-mismatches all resolved (3 gated G artifacts persist + 1 REPORT-tail typo + 2 resolved by pin upgrade/completion); 0 cross-copy disagreements; 40/40 committed slices byte-exact; live tree 7342/7342 manifest-identical; smoke pin ×2 + cmp ×2 clean. |
| Mutations / launches | Zero fork edits/commits, zero pushes, zero builds, zero boots, zero lease claims, zero deletions, zero lane-output writes. New bytes: V1 evidence (~7 MB, text) + `/tmp/v1-smoke/` (5.7 MB, retained). |
| Next dependency | Orchestrator: gate E28, mirror `emulog-t46r3.txt` to share (V1 read-only), prune 2 stale ssx3 + 7 stale fork worktrees, schedule the mini cutover off `CUTOVER.md` (waits for E29's boot + G38). |

## Mission 1 — audit (table: `AUDIT.md`)

| Finding | Receipt |
|---|---|
| E25 tar + binaries | Tar `9ded8065…` STABLE FULL-match; runner/suite FULL-match on SSD+share+live (agree=True); tarlist 8408/7342 = E25's counts exactly. |
| G binaries | G33/G34 FULL-match (sha+ELF+BuildID). G35/G36/G37 still read ZEROED (14th/15th/16th artifacts persist; values identical to gated pins; re-pinned with 21-min reads). Sizes all correct. |
| G mirrors | All 5 lanes: 13+13 files, PPMs pinned+agree, logs agree (U1 unpinned). Zero disagreements. |
| G13 dump | `154d9d85…` FULL-match (V1 ×2 + G38 independent ×4, Tier-2). SOLE-COPY on the corrupt path — moves first at cutover. 22 siblings uncorroborated (U5). |
| I24 | Logs 3+3 agree + pinned. Signed-app: ISO/ELF/vector pinned + agree; signed binary sole-copy (resign fallback). W binary/lib PREFIX-match (U4 full shas never committed). |
| T4 | 41 SSD + 41 share files, 82/82 stable, FULL/PARTIAL/SIZE pins match except t43r1 tail (1-char REPORT typo, 6 agreements carry it). 40/40 slices. Variant share-only by design; t46r3 SSD-only fresh (streamed mid-pass, verified complete). 3 pre-t42 unpinned (U2). |
| Live tree | 7342/7342 stable AND manifest FULL-match — bit-identical to E25's snapshot 8+ h later, across E26/E28 boots. p1/e17 still absent. |
| Fork row | `ssx3` ref = tracking = ls-remote = `3adc0478` (checkout-proof; remote default HEAD `14b1e5cb` is NOT the lane). E29 checked out `e29-movie-bypass` @ same commit mid-lane — ref immutable, design validated live. |
| Clones/worktrees | parallel-gs-g7 @ `3a66c19` (G dirt, unchanged open→close); i10/i11 clean-detached; ssx3 main advanced by orch commits only; 2 stale-gone; 3 subagent dirty-detached, untouched. |
| Uncorroborated | Exactly U1–U8 (`AUDIT.md`): G logs, 3 pre-t42, pre-t17auto sha, W full shas, G13 non-dump, PADs, signed smalls, tar member names. Stated, not hidden. |

Cache note: PASS1 small-set reads ran at >1 GB/s (buffer-cache served). The pins — not the cache — are the check: a cache-frozen corrupt read cannot match a committed pin, and the 147 GB pass churns the entire cache before PASS2.

## Mission 2 — pinned restore manifest + smoke

| Finding | Receipt |
|---|---|
| Manifest | `restore-manifest.json`: repo → share → SSD → rebuild fallbacks, every step with paths + shas/sizes + verify commands. E fallback measured (72.5+530.8 s); G/I walls unmeasured (stated); T has no rebuild (share is the backup). |
| Smoke | Share `ps2x_tests` → `/tmp/v1-smoke/`: pin FULL-match ×2 (1674 s apart) + cmp clean vs live AND share. **SMOKE PASS.** Retained. |
| Untested remainder | Full-tar extract (forbidden), live-path two-binary restore (would overwrite lane outputs), G/I/T restores (mirrors verified in place, no copy exercised). Stated in manifest + `SMOKE.md`. |

## Mission 3 — mini-cutover list (table: `CUTOVER.md`)

Active inputs + fresh build cache move to mini-internal (6 rows); SSD becomes backup (7 rows); 6 post-move re-verify checks; 8 lease/holder rows (cutover WAITS: E29 boot, G38 run, E28 gate); first-commands checklist; sole-copy move order (dump first, tar watched).

## Success bars

| Bar | Status |
|---|---|
| Full audit table with sole-copy flags | DONE (`AUDIT.md`, 30 rows) |
| `restore-manifest.json` with ordered steps + pins + verify commands | DONE |
| ONE smoke restore with receipts | DONE, PASS (`SMOKE.md`, `smoke.json`) |
| Mini-cutover list | DONE (`CUTOVER.md`) |
| Untested remainder stated | DONE (manifest + smoke + report) |
| Zero lane mutations | DONE (worktrees open/close + status receipts) |
| Tail receipt with byte-exact prefix sha | BELOW |

## Exact command record

| Step | Command |
|---|---|
| Pins | `python3 local/research/V1/v1_extract_pins.py` → `v1_pins.json` (7561 pins, HEAD blobs) |
| PASS1 | `python3 local/research/V1/v1_audit.py pass1` → 147.5 GB, 15:39:47–15:52:06Z |
| PASS2 | `sleep 420; python3 local/research/V1/v1_audit.py pass2` → 147.5 GB, 16:00:48–16:12:52Z |
| Compare | `... v1_audit.py compare` → `audit-compare.json` (7610 stable, gaps 1157–1261 s) |
| Slices | `python3 local/research/V1/v1_slices.py` → `slices.json` (40/40) |
| Worktrees | `... v1_audit.py worktrees open|close` → `worktrees-*.json` |
| Tarlist | `... v1_audit.py tarlist` → 8408/7342 |
| Fork ref | `rev-parse HEAD|ssx3|refs/remotes/fork/ssx3` + `ls-remote` → `fork-ref.json` (open 16:01Z + close 16:14Z) |
| Smoke | `cp -p` + `shasum` ×2 (1674 s) + `cmp` ×2 → `smoke.json` |
| ELF P1-top | `shasum` ×2 (1490 s apart) → both `1b49d05c…e2291d…` (E23 `e2391d` typo confirmed) |
| Render | `python3 local/research/V1/v1_render_audit.py` → `AUDIT.md` table |

Env: `COPYFILE_DISABLE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=local/research/V1` on every step.

## Evidence hygiene

Text only (`du` receipt at commit). Tools committed (`v1_common/audit/extract_pins/slices/render_audit.py`).
HEAD walked mid-lane (`e77d83c`→`8e84791`→`ba7422d`→`491d9a1`→`39f2e6c`→`252bb34`); pins
re-extracted and re-verified at the final HEAD. Internal free fell 4.3→2.9 GB
during the lane (other workers/system — V1 owns ~13 MB); SSD owned by V1: 0 bytes.
G38 started mid-lane on disjoint paths; V1 read-only throughout. Publication:
`[V1]` evidence commit with `Orchestrated-By: Muse Code`, `git add -f`, NO push.

| Tail receipt | Value |
|---|---|
| Complete prefix | Lines 1–77; 6605 B; SHA256 `f7464f03574b5f1be21fc1b78aefc7efd45f4aec9e36a4aedfcf540f52c660d6` (the prefix is every byte ABOVE the `| Tail receipt | Value |` header line, so this row lives after the boundary and cannot invalidate itself — errata E24-E2) |
| Source-tail gap | None. Every V1 capture carries its receipt; the untested remainder is stated in three places (manifest, smoke, §Mission 2), not inferred away. |
| V1 REPORT TAIL COMPLETE | Two passes over 147.5 GB, 19–21 min apart, every byte corroborated against committed pins or named as uncorroborated: the E25 snapshot, the share mirrors, the live tree, the G/I/T lanes' critical paths and the fork refs all re-verify — with the three gated G artifacts persisting exactly as gated, one REPORT-tail typo and one REPORT prose truncation caught and carried, and the E23 ELF typo closed by three measured copies. The restore manifest names every step in order with pins and verify commands; the smoke restore passes end-to-end; the mini-cutover list waits on leases rather than preempting them. 0 lane mutations, 0 deletions, 0 builds, 0 boots. |
