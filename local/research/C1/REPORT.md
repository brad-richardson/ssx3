# C1 report — ssx3 publication cleanup (mechanical run)

Brief: `local/muse/prompts/C1.md`. Inputs: A1/A2/A3 `REPORT.md` files plus
A3 drafts under `local/research/A3/drafts/`. Six commits, all `[C1]`-prefixed
with the brief's trailers; `git add <paths>` throughout (plus one `git add -f`
for this report). No history rewrite. No builds, no `adb`, no device.

## Step 1 — Archive stale docs (commit `da50281`)

| File | Change |
|---|---|
| `docs/archive/roadmap.md` | `git mv` from `docs/roadmap.md`; banner `Archived 2026-09-18; superseded by docs/impl-plan-2026-09-15.md and native/README.md.` (supersession per A3 §1 + ARCHIVE-CANDIDATES) |
| `docs/archive/ssx3-120hz-handoff-2026-09-13.md` | `git mv` from `docs/research/ssx3-120hz-handoff-2026-09-13.md`; banner `Archived 2026-09-18; superseded by docs/plan-120fps-2026-09-17.md.` |
| `docs/rebuild-experiment.md:548` | `[the roadmap](roadmap.md)` → `(archive/roadmap.md)` |
| `docs/research/120hz-analysis.md:3` | link → `(../archive/ssx3-120hz-handoff-2026-09-13.md)` |
| `docs/research/120hz-native-path.md:20` | link → `(../archive/…)` (same target) |
| `docs/research/120hz-reprojection.md:361` | backtick path → `../archive/…` |
| `docs/README.md` | adopted A3 draft; the two archived entries repointed to `archive/roadmap.md` and `archive/ssx3-120hz-handoff-2026-09-13.md` |

Post-move `git grep -rn "roadmap\.md\|ssx3-120hz-handoff-2026-09-13"`: 4 hits,
all pointing at `archive/`. No other inbound file-links existed (remaining
"roadmap" mentions are milestone words like "roadmap M2", not links).

## Step 2 — Tool defaults off the author's machine (commit `fbe712d`)

New `tools/paths.py`: `workbench_root()` (`SSX3_WORKBENCH`) and `games_root()`
(`SSX3_GAMES`); each raises `RuntimeError` naming its variable when unset.
Expected layout is documented in the module docstring and the root README
Configuration section (verified against actual tool usage: `builds/`,
`source/ssx3/BAM.BIG`, `extracted/garibaldi/gari.pbd`, `native/GXBE69`,
`emulator/`; `ps2/`, `gamecube/`).

| File | Old literal | New default | CLI flags |
|---|---|---|---|
| `tools/course_census.py` | `GAME_DEFAULT = Path('…/ssx3-workbench/native/GXBE69')` | `None`, resolved in `main()` for `build-player`/`run` to `workbench_root() / 'native/GXBE69'` | `--game` kept (+ help text) |
| `tools/native_gamecube.py` | `DEFAULT_GAME = Path('…/ssx3-workbench/native/GXBE69')` | `None`, resolved in `main()` for `run` (inside the existing `try`, so a missing var prints `error: SSX3_WORKBENCH is not set…`, exit 1) | `--game` kept (+ help text) |
| `tools/import_crossing.py` | `src = Path('…/source/ssx3/BAM.BIG')` | `workbench_root() / 'source/ssx3/BAM.BIG'` (needed at run) | none (positional driver) |
| `tools/patch_crossing.py` | same `src` literal | same replacement | none (positional driver) |
| `tools/import_terrain.py` | `--pbd` default `…/extracted/garibaldi/gari.pbd` | `None`, resolved in `main()` | `--pbd` kept (+ help text) |
| `tools/prepare_emulator.py` | `--games …/games/ps2`, `--builds …/ssx3-workbench/builds` | `None` → `games_root() / 'ps2'`, `workbench_root() / 'builds'` | both kept (+ help text) |
| `tools/ride_locations.py` | `--archive …/source/ssx3/BAM.BIG` | `None`, resolved in `main()` | `--archive` kept (+ help text) |

Defaults resolve lazily: `--help` and module import never need the env vars
(verified with env unset). `native/**` contains no `.py`/`.sh` scripts, so no
native script defaults existed to change. `git grep -n '/Volumes/'` under
`tools/ native/ tests/` after the edit: only `tools/macos/share_keepalive.*`
(generic `/Volumes/share` mount-point validation, not an author default),
`tools/odin_wireless.sh:17` (`SSD_FILE` on Extreme SSD — see Left #3), and
`native/README.md` (docs; replaced in step 6). Tests: neither A2-listed file
asserts `/Volumes` paths (`test_android_trial` asserts `/data/local/tmp/mg`
device paths; `test_texture_pack_union` matched only `tex1_…` names), and the
full suite passed unchanged — no test updates needed.

## Step 3 — Scrub private infrastructure tokens (commit `7fb18fc`)

Applied with `git grep -l` + `sed -i ''`, plus hand edits for the three bare
`bytesize` leftovers and `tools/odin_wireless.sh`.

| File | Before | After |
|---|---|---|
| `docs/full-course-validation.json` | 6× `/Users/bradrichardson/` | 0 (`~/dev/ssx3/…`) |
| `docs/impl-plan-2026-09-15.md` | 1 (`ssh bytesize`) | 0 (`ssh <gpu-box>`; `user bradr` kept — not in the token list, see Left #4) |
| `docs/plan-120fps-2026-09-17.md` | 4 (2× serial, 2× bytesize) | 0 (`<odin-serial>`; `optional the GPU box WSL`; `the GPU box's WSL2` + `ssh <gpu-box>`) |
| `docs/research/ps2recomp-spike-2026-09-12/README.md` | 2 (`bradflix` ×3 incl. `bradflix-ps2recomp/`) | 0 (`the media server`, incl. `` `the media server-ps2recomp/sessions/` `` — see Left #5) |
| `docs/texture-remaster.md` | 5 (4× `ssh bytesize`, 1× `bytesize:` scp) | 0 (`ssh <gpu-box>`, `<gpu-box>:set.tgz`) |
| `docs/todo.md` | 1 (`bradflix`) | 0 |
| `tests/test_android_trial.py` | 4 (synthetic `192.168.1.50:5555`, `622c49b1`) | 0 (`<odin-ip>:5555`, `<odin-serial>`; values stay consistent so the tests still pass — 23 passed) |
| `tools/odin_wireless.sh` | 2 (`622c49b1`) | 0 (`ODIN_USB_SERIAL="${ODIN_USB_SERIAL:-$(cat local/odin-usb-serial 2>/dev/null \|\| true)}"`, documented in the header; `USB` follows the variable; `zsh -n` ok; env passthrough and empty-unset verified) |
| `tools/upscale_textures.py` | 1 (`ssh bytesize`) | 0 (`ssh <gpu-box>`) |

`smb://` hosts already read `YOUR_SMB_HOST` — untouched. Post-scrub grep over
the nine files: empty. Whole-tree re-run
`git grep -nE '192\.168\.|622c49b1|bradflix|bytesize|/Users/bradrichardson|macbook\.air'`:
hits remain **only** in `local/research/*` (A2 22, A3 1, G0 5, P1 2,
S2 REPORT 5 / arm.py 2 / wait_device.sh 2 / waits.log 1, S2b REPORT 2 /
arm.py 2 / vk-relink-attempt1-error40.txt 4 / waits.log 2) — untouchable per
the Rules (see Left #2). Zero hits in `native/patches/` (the brief's stated
exception is vacuous for this pattern).

## Step 4 — Game text trims (commit `24d4d30`, plus revert commit context)

- `docs/rebuild-experiment.md:579`: `"Snow Jam is an exciting BEGINNER track"`
  → `"Snow Jam is an…"` (first four words + ellipsis). Done.
- `native/diagnostics/course-start-freestyle.json`: **left unchanged**. The
  consumer (`tools/gamecube_course_check.py`) copies `--menu-sequence` bytes
  verbatim into the output dir and hashes them; nothing parses or compares
  the `name` field, so the flagged menu strings are not a lookup key — but
  precisely because nothing consumes the field, trimming prose around the
  course names has no code-comparison basis either. Recorded here per the
  brief instead of edited.

## Step 5 — Generated header (attempted, then reverted in `32a6c24`)

The file stays (orchestrator ruling stands — no deletion performed). The
ordered two-line top comment was added, then **reverted**: it changes the
file bytes pinned by `tests/test_native_gamecube.py::ConversionSplitDefault`
(`ORIGINAL 05b40083…`, `CANDIDATE dcac6fc8…`), failing 3 tests
(`test_applies_proven_split_to_original_header`,
`test_keeps_existing_candidate_header`,
`FastFpDefault::test_module_build_enables_fast_fp_without_flag`). The test
comment states a mismatch "must be re-spiked, not adjusted", so the pins were
not touched. See Left #1. Net file change: none. Related tests after revert:
10 passed, 1 skipped.

## Step 6 — README and sub-READMEs (commit `56d214e`)

- `README.md`: A3 draft adopted, then (a) Status section's ledger/`todo.md`
  quote blocks replaced with `Current measured numbers live in
  docs/numbers-ledger.md; the working plan is docs/todo.md.` plus the three
  ordered track lines; (b) new Configuration section (`SSX3_WORKBENCH` /
  `SSX3_GAMES` + expected layout, matching `tools/paths.py`); (c) Not-included
  section kept and strengthened (`…are never in this repository… must supply
  them yourself from your own retail copies`); (d) Licensing section per the
  brief (MIT + `LICENSE`; GPL-3 vendored trees; GPL-3 patches; combined builds
  GPL-3; DolRecomp oracle header note).
- `native/README.md`, `tools/README.md`: A3 drafts adopted verbatim (both
  existed).
- `LICENSE`: MIT text, `Copyright (c) 2026 Brad Richardson`.
- New/changed READMEs + LICENSE are token-grep clean; all `[…](…)` link
  targets in the four READMEs resolve to existing files.

## Step 7 — Verification

- Test suite (`python3 -m pytest tests -q`): **746 passed, 1 skipped,
  243 subtests passed** — identical to the pre-C1 baseline. Mid-run
  regression (3 failures from the step-5 comment) was caught by the suite and
  reverted; final state is green.
- Scrub re-run: only `local/research/*` hits (table in step 3); nothing in
  `native/patches/`.
- `git status`: clean except this report (untracked, force-added on commit).

## Left for the orchestrator

1. **Step-5 comment vs pinned oracle.** Any byte change to
   `tests/float-conversion-original-generated.h` (even a comment) invalidates
   the `ORIGINAL`/`CANDIDATE` pins in `ConversionSplitDefault`. If the
   provenance note is still wanted, it needs a re-spike (new pins) or a
   ruling to house the note elsewhere (e.g. beside the test, not in the
   file).
2. **Brief vs Rules on `local/`.** Step 3 says "every tracked file" and the
   final grep "must be empty except inside `native/patches/`", but the Rules
   forbid touching `local/` beyond this report, and the audit reports under
   `local/research/*` are tracked. All remaining scrub-pattern hits are
   there (counts in step 3). Sanitizing them needs an orchestrator ruling.
3. **`/Volumes/` leftovers.** `tools/macos/share_keepalive.m/.py` validate a
   generic `/Volumes/share` mount point (not an author default — left).
   `tools/odin_wireless.sh:17` `SSD_FILE="/Volumes/Extreme SSD/…"` has no
   matching variable in the brief's vocabulary (`SSX3_WORKBENCH`/`SSX3_GAMES`
   don't cover Extreme SSD) — left as-is.
4. **Tokens outside the step-3 list, left as-is:** `user bradr`
   (impl-plan), `/home/brad/…` + `/mnt/c/Users/bradr/…` (texture-remaster),
   `/Users/bradr` (not `bradrichardson`). None match the listed patterns or
   the verification grep.
5. **Mechanical artifact:** `bradflix-ps2recomp/sessions/` became `` `the
   media server-ps2recomp/sessions/` `` (ps2recomp-spike README) — faithful
   to the mapping, awkward as a path; flagging in case a rename is wanted.
6. **Cosmetic:** `course_census.py` with env unset raises `RuntimeError`
   with traceback (exit 1); `native_gamecube.py` prints a clean
   `error: …` line via its existing handler. Behavior identical otherwise.
7. **A3 draft adoption side effects (applied as ordered):** the new
   `native/README.md` drops the old file's DTK one-liner detail and
   2026-09-10 validation stamp; root README drops the old build/result
   tables. Link check passes; content call is the orchestrator's.
