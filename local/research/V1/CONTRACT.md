# V1 contract — durable verified storage audit (READ-ONLY on lane outputs)

Lane V1 executes `local/muse/prompts/V1.md` exactly: Mission 1 audit table,
Mission 2 `restore-manifest.json` + ONE small smoke restore, Mission 3
mini-cutover list. Tables + receipts, no verdicts beyond the missions.

## Rules (from the brief, restated before the first read)

- READ-ONLY on all lane outputs: build dirs, `ps2x-*`, worktrees,
  `/tmp/e18-mpeg-link`, share mirrors. No builds, no boots, no lease, no
  devices, no adb/devicectl, no network writes except share-tier READS.
- Fork operations: `rev-parse` / `status` only (V1 tables HEADs +
  clean/dirty; `ls-remote` deliberately not re-run — E28's committed gate
  already triple-agreed, and V1 adds no network load beyond share reads).
- Scratch restores to NEW `v1-*` paths ONLY: internal `/tmp/v1-*` ≤ 1 GB
  (smoke: one 5.7 MB file); SSD `v1-*` ≤ 4 GB (planned: 0 bytes — smoke
  stays on internal). RETAINED + receipted; zero deletions ever.
- `COPYFILE_DISABLE=1` on every SSD step; `._*` AppleDouble sidecars are
  never hashed (counted + skipped explicitly).
- Evidence `local/research/V1/` text-only (manifests are JSON — sizes +
  shas, never bytes). Time box 6 h from ~15:35Z. Commit `[V1]` +
  `Orchestrated-By: Muse Code` trailer, `git add -f`, NO push.

## SSD-corruption rule (G33 AMENDMENT + E26 gate: 16 recurrences, pattern-dependent)

Every byte V1 quotes needs 2+ matching reads separated in time (PASS1 +
PASS2, gap recorded per file; G33's transient held ~10 min, so V1 targets
a ≥20 min inter-pass gap on lane-critical bytes) AND corroboration
against pinned committed (git HEAD) bytes. Corroboration tiers:

- Tier 1: `git HEAD` blobs (E25 manifest/REPORT/RESTORE/pins/snapshot;
  G33–G37/I24/T REPORTs + logs; `docs/todo.md`, `docs/status.md`).
- Tier 2: uncommitted-but-prior lane receipts (E28 fork-gate/pins —
  separation in time + authorship, not content-addressed). Supporting only.
- UNCORROBORATED: quoted only with 2-read stability + cross-copy
  agreement; listed exactly (see `AUDIT.md` §uncorroborated).

## Reservations

- Internal: evidence ~6 MB + `/tmp/v1-smoke/` 5.7 MB « 1 GB cap.
- SSD: 0 new bytes planned (no `v1-*` SSD paths needed).
- HEAD at open: `e77d83c` (status clean — verified before PASS1).

# V1 CONTRACT TAIL COMPLETE
