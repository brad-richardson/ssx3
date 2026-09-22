# V1 Mission 3 — mini-cutover list (FINAL: pins re-verified at HEAD 252bb34 [G39])

All paths parameterized: THIS-HOST (Mac, SSD `/Volumes/Extreme SSD`, share
`/Volumes/share/ssx3`) vs MINI (internal-first; SSD attaches as backup only).
If the migration happens mid-lane: table + stop (per brief — V1 does not
chase a moving target).

## What moves to mini-internal (active inputs + build cache)

| # | Payload | Source (this-host) | Mini dest (internal) | Size | Restores via |
|---|---|---|---|---|---|
| 1 | ssx3 repo | git clone (no fork files inside) | `~/dev/ssx3` @ pinned `HEAD` | ~50 MB + evidence | step 1, `restore-manifest.json` |
| 2 | PS2Recomp fork | clone `fork/ssx3` @ `3adc0478…` | mini-internal fork path | ~2 GB worktree | step 1 (fresh clone, no SSD copy) |
| 3 | E18 live tree | share `e25-restore/` (2 binaries) OR SSD tar | `/tmp/e18-mpeg-link/` | 169 MB (2-bin) / 1.75 GB (tar) | steps 2–3 |
| 4 | paraLLEl-GS clone | clone @ `3a66c19…` + G38 hunk | mini-internal clone path | ~1 GB | step 5 (fresh clone + apply) |
| 5 | G13 dump | SSD `ps2x-g13/g13-dump.gs` (SOLE-COPY — moves FIRST, §sole) | mini-internal inputs | 11.5 MB | step 5 (copy + re-sha twice) |
| 6 | Build cache | fresh `${TMPDIR}`/build dirs on mini-internal | mini-internal | 0 carried (rebuilt) | steps 4/6 (measured recipes) |

Build cache is NOT carried as bytes: E rebuilds in ~10 min (72.5 s +
530.8 s measured), G rebuilds per-lane (~minutes; G37 wall in manifest).
Carrying ExFAT build trees would import allocation slack + suspect bytes.

## What stays on SSD-as-backup (attached to mini or shelf)

| Payload | Why it stays | Second copy |
|---|---|---|
| E25 tar + 2 binaries | 2-binary + full-tree fallback | share `e25-restore/` (binaries); tar SSD-only — NOTE |
| `ps2x-g13/` (dump + emulog + markers + PNGs) | reference inputs | dump: mini-internal after move; rest SSD-only |
| `parallel-gs-g33..37-android-build/` | prior-lane binaries (re-read per gate) | none (rebuildable from clone + hunks) |
| `ps2x-i23/` (W, 9.6 GB) + `ps2x-i24/` (N) | parked I-lane inputs | logs: share mirror; W: SSD-only |
| `ps2x-t4/` (64.9 GB) | reference traces | share mirror (41/41 incl. variant) |
| `ps2x-g33..37/` receipt dirs | run receipts | share mirrors (13/13 each) |

## What re-verifies post-move (pins + one smoke)

| Check | Command source | Expected |
|---|---|---|
| 1. ssx3 HEAD + fork HEAD | `git rev-parse HEAD` both repos | `restore-manifest.json` §repo |
| 2. Runner + suite sha | `shasum -a 256` ×2 reads | `e462e448…` / `2152e5ad…` |
| 3. Full-tree manifest (if tar restored) | manifest loop in `RESTORE.md` | 7342/7342 |
| 4. Dump sha ×2 | `shasum` | `154d9d85…` |
| 5. ONE smoke: suite 458/458 on mini | `ps2x_tests` run (no boot) | rc 0, 458/458 |
| 6. G clone HEAD + BuildID of next build | `rev-parse` + `llvm-readelf --notes` | `3a66c19…` + new BuildID |

## What waits for active leases (cutover WAITS, never preempts)

| Holder | State at V1 open | Cutover rule |
|---|---|---|
| P-lane lease | FREE (E28 1/1/1, released 15:21:44Z); E29 checked out `e29-movie-bypass` @ 3adc0478 16:14Z, no commits yet | E29's boot claims next; cutover never mid-boot |
| E28 gate | LANE DONE, committed `[E28]` 8e84791; orch gate pending | gate first; cutover takes E28's pins as the E-lane floor |
| G38 (G lane) | ACTIVE (REPORT 11:39 ET, dump re-read FULL-match, own build dir + ps2x-g38/ + share mirror) | finishes pre-cutover; cutover never across a run |
| G39 (G lane) | briefed 39f2e6c-era (G26+G28 regression/adoption gate) | schedule post-cutover validation run with it |
| N1 (Android prep) | DONE, committed `[N1]` 39f2e6c (read-only) | unaffected |
| T46 (T lane) | DONE, committed `[T46]` ba7422d; trace `emulog-t46r3.txt` SSD-only fresh (V1-verified, FULL pin) | mirror t46r3 to share before cutover (V1 read-only: cannot mirror) |
| Odin slots | per-run booking | book post-move validation run before decommissioning old paths |
| Subagent worktrees (3, dirty) | other workers' active files — V1 read-only | owner call; V1 touches nothing |

## First commands on the mini (checklist)

```sh
# 0. Mounts: internal-first; attach Extreme SSD read-first; mount share.
/Volumes/share/ssx3/e25-restore/ps2x_tests  # share readable?
# 1. Repo pull
git clone https://github.com/brad-richardson/ssx3.git ~/dev/ssx3
git -C ~/dev/ssx3 rev-parse HEAD            # expect manifest §repo.ssx3_head
# 2. Fork clone (fresh, internal)
git clone <fork-url> <mini-fork-path> && git -C <mini-fork-path> rev-parse HEAD  # 3adc0478…
# 3. Pin re-verify (TWO reads, separated; COPYFILE_DISABLE=1 for SSD reads)
export COPYFILE_DISABLE=1
shasum -a 256 <ssd>/ps2recomp-spike/P1/e25-snapshot/e18-mpeg-link.tar   # 9ded8065…
shasum -a 256 <ssd>/ps2x-g13/g13-dump.gs                                # 154d9d85…
# 4. Restore (ONE path only): 2-binary first, tar iff incremental build needed
#    (exact argv in restore-manifest.json steps 2–3)
# 5. Smoke: shasum ×2 + cmp + 458/458 suite run, no boot
# 6. G clone + dump copy + BuildID-recorded rebuild
# 7. Old paths stay readable until §re-verify above is green; then SSD→backup.
```

## Sole-copy moves (§sole)

The G13 dump is the only lane-critical byte-string with NO durable second
copy on any path (see `AUDIT.md`): it moves first, by copy + re-sha twice
+ cmp, before any cutover step that could disturb the SSD. (G38 holds a
transient sha-verified copy in its own active dir — untouchable and not
durable.) The E25 tar is the second watch-item (binaries mirrored; tar
SSD-only).

# V1 CUTOVER TAIL COMPLETE
