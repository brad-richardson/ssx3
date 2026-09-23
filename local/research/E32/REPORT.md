# E32 report — one primary branch: everything folded onto `ssx3`

Brief `local/muse/prompts/E32.md` + mini amendment (Mac mini paths).
Tables + receipts; the orchestrator decides (incl. branch pruning).

## Outcome

`fork/ssx3` fast-forwarded `3d4feed` → `e57b5f8` (12 commits, no force,
no rewrite) and pushed. Suite **463/463** flags-unset. Both boots green:
(a) reproduces the e28a/e29a movie-park terminal state; (b) reaches Main
Menu and Select Character, and menu frames show **0/224 identical line
pairs** (weave default works). `git diff --stat 14b1e5cb ssx3 --
ps2xRuntime/src/runner` is empty.

## New `ssx3` commit list (old head → new head)

| Commit | Subject (fold source) |
|---|---|
| `dbb63d7` | `PS2X_GAME_CODEGEN_DIR` game-objects static lib (archive/i10 `3d2e22d`) |
| `bae962c` | Drop in-tree `sub_*.cpp` when codegen dir set (i21-drop-b `590d831`) |
| `5ad0d81` | CFBundleName one-liner (i8 `3006a07`) |
| `d824af0` | FFmpeg-iOS wiring (i23 `bbc8572`) |
| `7bb956d` | FFmpeg default ON for iOS (i23 `50775d0`) |
| `9b3b077` | `PS2X_MPEG_VECTOR_PATH` (i23 `d61bee0`) |
| `bcdad38` | iOS-FFmpeg recipe doc (i23 `c36c5dd`) |
| `b329c21` | `PS2X_MPEG_FEED_TRACE` (i23 `e74f1dd`) |
| `6526329` | `PS2X_SKIP_MOVIE` bypass (e29 `194133c`) |
| `5461ad8` | `PS2X_PAD_SCRIPT` + 3 tests (e31 `ee39b9f`) |
| `dcecf13` | `[diag:frame]` tap, `PS2X_DIAG_PERIOD_MS`-gated (i18 `16e1b9a`) |
| `e57b5f8` | `PS2X_DEINTERLACE` default weave + 2 unit tests (new) |

Full input table with fold/skip decisions: `input-table.md` (step 1; no
ambiguities, stop rule not triggered). Skipped by content: i10-alt
(byte-identical hunk), i21-drop-a (byte-identical hunk; -b picked as the
I23-line variant), all 7 map rows (byte-identical lines already on `ssx3`).

## Codegen (first logical change, per brief)

SSD `ps2xRuntime/src/runner/` (read-only source, 9,457 files) copied to
`~/dev/ssx3-work/codegen-ssx3/` (273 MB logical; the "9.3 GB" is ExFAT
1 MiB-cluster allocation). No generated headers under
`ps2xRuntime/include/` on the SSD side (the 2 headers live in `runner/`).
SHA manifest `codegen-manifest.txt`: SSD read twice (`cmp` agree), copy
`cmp`-equal. Configure reports `game objects: 9455 sources` and
`dropped 0 in-tree game sources` (scrubbed tree has no in-tree `sub_*`).

## Build + suite

Fresh configure (E18 recipe, `-S`/`-B` changed, +
`-DPS2X_GAME_CODEGEN_DIR=~/dev/ssx3-work/codegen-ssx3`), rc 0. FetchContent
HEADs: raylib `c1ab645c`, imgui `b1bcb12a`, rlImGui `118221c8` (match
E18/E25). Zero `._*` in `_deps` (internal APFS). Build `ninja -j2` rc 0,
549 edges.
Suite from fork root, all five dev flags unset: **463/463, rc 0**
(458 + 3 pad + 2 deinterlace). One self-found failure on the way: the
legacy "line-doubles interlaced field output" test asserted bob-by-default;
kept whole by pinning bob via new `ps2xSet/ClearDeinterlaceBobForTest`
hooks (pad-test-hook precedent) and renaming it "... in bob mode".
Runner `9b613c67…b9a78cae` (139,007,040 B), two matching SHA reads
separated by both boots. Suite binary `f4b478c6…`.

## Boots (lease `/tmp/ssx3-p-lane-lease`, one at a time, internal paths)

| Boot | Env | Result |
|---|---|---|
| e32a, wall 120 s, rc 0 | all feature flags unset | EQUIVALENT: `[DEV-SKIP]`×0, `[GetPicture] waiting`×1, `[feedES]`×1 5040 B `first4=000001b3`, `parsed=5040 packets=0`, thread 1 `pc=0x3b1028` every diag block, final frames 512×448 fbp=112 `fnv1a=fd889dc5` (e28a/e29a hash) |
| e32b, wall 120 s, rc 0 | `SKIP_MOVIE=1` + `25000:start:5000,45000:cross:5000` | `[DEV-SKIP]`×3, park×0, both script inputs press+release, 1,134 dumps changing at wall; snap-40s = Main Menu (Single Event), snap-76s = Select Character (Zoe) — read off PNGs, beyond the bar |

Deinterlace check: e32b menu frames **0/224** identical adjacent line
pairs (was 224/224 under bob); e32a frozen black frame 224/224 (all black,
expected). Feed SHA `cde8a830…` not re-derived (log line carries
size+first4 only); equivalence rests on the six rows above.

## Push receipt

`git push fork ssx3`: `3d4feed..e57b5f8 ssx3 -> ssx3`, rc 0.
`git ls-remote fork ssx3` = `e57b5f8ce70e721fb161f0303b7b3fc83227551c`.
Worktree on `ssx3` at `e57b5f8`, status clean. Local `fold` branch left in
place (same head; orchestrator may delete).

## Branches for the orchestrator to prune

**None is ancestor-contained** (`merge-base --is-ancestor` false for all
15: e29, i23, i8, i10×2, i11–i17, i18, i21×2) — every fold was a
cherry-pick, so pruning must be by content-equivalence, not fast-forward
containment. Content status: e29(2), i23(5), i8(1), i10(1), i21(1),
i18(1) commits all folded; all 7 map rows already on `ssx3`
byte-identical. I recommend deleting all 15 after gate-read; none carries
unique content.

## Gaps / notes

- `193451a` (N1's I21 citation) is unknown in this clone; irrelevant —
  both I21 hunks are text-identical.
- Pre-scrub `96893da` likewise absent here; `ee39b9f` taken per brief as
  the scrubbed equivalent (content verified: +365/+34/+90).
- One `| head` SIGPIPE incident killed a multi-cherry-pick mid-sequence;
  recovered via `--quit` + single picks, no tree harm (log in report).
- Disk: E32 ≈ 8.2 GB of its 25 GB cap (codegen 0.3 + build 1.7 + inputs
  5.6 + run 0.6); total 16.9/200 GB. E32-build/E32-run/E32-inputs left for
  the next lane; codegen copy is the canonical generated set now.
- Boot-frame PNGs + full logs live under `~/dev/ssx3-work/E32-run/`
  (internal, not in git); this evidence dir holds the table, wrapper,
  manifest, and report only.
