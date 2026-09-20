# A1 — ssx3 pre-publication audit, part 1: game-derived and third-party content

Runbook: `local/muse/prompts/A1.md`. Read-only run: no builds, no `adb`,
no changes to tracked files (this report is a new untracked file under
`local/research/A1/`; nothing was staged or committed).
Observed tracked-file count at run time: **388** (`git ls-files | wc -l`;
runbook states 387).

## 1. Inventory (tracked files, grouped by directory)

Primary class per group. Files in flagged categories are listed
individually in §2; everything else is counted here.

| Directory | Count | Primary class |
|---|---|---|
| `.` (root: `README.md`, `.gitignore`) | 2 | documentation (README) / other (.gitignore) |
| `docs/` top level (30 `.md`/`.json`) | 30 | documentation |
| `docs/research/` (25 `.md` + 4 `.py` under `ps2recomp-spike-2026-09-12/scripts/`) | 29 | documentation (25) / project source/tool (4 scripts) |
| `tools/` top level (123 `.py`/`.sh`/`.swift`) | 123 | project source/tool |
| `tools/macos/` | 8 | project source/tool |
| `tools/course_presets/` (`aloha.json`, `garibaldi.json`) | 2 | data/table derived from the game (build configs with game codes/anchors) |
| `tests/` (`*.py`, `native_grab_probe.cpp`, `native_hash_probe.cpp`) | 101 | project source/tool |
| `tests/float-conversion-original-generated.h` | 1 | generated guest code from the recompiler (see §2) |
| `native/diagnostics/` (21 `.h`/`.c` + 3 `.json`) | 24 | project source/tool |
| `native/ios/` (sources, `CMakeLists.txt`, `toolchain.cmake`, `WriteBuildInfo.cmake`, `Info.plist`, `README.md`, 4 smoke/soak `.json`, 4 tests) | 25 | project source/tool |
| `native/` top level (`README.md`, `research.md`, `dependencies.json`, `validation.json`, `mobile-validation.json`) | 5 | documentation / project source/tool |
| `native/patches/` (15 `.patch`) | 15 | patch to third-party (see §3) |
| `local/research/` tracked with `-f` (`G0/REPORT.md`, `P1/REPORT.md`, `S2/` ×9, `S2b/` ×12) | 23 | documentation (4 REPORTs + 11 logs/txt) / project source/tool (8 `.py`/`.sh`/`.h`) |
| `third_party/` tracked | 0 | (directory exists on disk but is git-ignored; see §3) |
| **Total tracked** | **388** | |

Notes recorded during classification:

- `third_party/` on disk holds `ModernGekko/`, `SSX-Library/`,
  `sunpad-reference/`; `git ls-files | grep -iE "third_party|vendor|vendored"`
  returns nothing, and `git log --stat -- third_party/` is empty.
- No tracked file outside `native/patches/` is a copy of third-party
  source. The 853 `git grep` hits for vendor names are references
  (docs), build wiring, patch bodies, and test assertions, not copies.
- `tools/*.py` files that cite `SSX-Library` (`LOC.cs`, `BIGF4.cs`,
  `PBDHandler.cs`, `SSBHandler.cs`, `AIPSOPHandler.cs`, `WorldAIP.cs`)
  reimplement layouts in Python against disc bytes; no C# source is
  copied into the tracked tree.
- `local/` paths named inside tracked files (e.g. `local/game/...`,
  `local/evidence/...`, `local/research/startgate/host-script.bin`,
  `local/source/...`) are untracked local inputs/evidence, not tracked
  content. `tests/test_gamecube_lun.py` skips its stock-script test when
  `local/research/startgate/host-script.bin` is absent.

## 2. Flagged-files table

`facts` = addresses, offsets, sizes, hashes, table layouts, names we
assigned, profiler labels, lookup keys. `content` = bytes, strings, code,
or art from the binary/discs, or guest code produced from them by a
recompiler. Quotes are ≤ 120 chars. `history only?` is `no` for every row:
no tracked file was ever deleted (§4), so all listed files are current.

| File | Category | What exactly (quoted) | Facts-or-content | Size of flagged material | In history only? | Removal shape |
|---|---|---|---|---|---|---|
| `tests/float-conversion-original-generated.h` | generated guest code from the recompiler | `// DolRecomp output` / `// cpu: gekko` (header of C-backend output) | content | 549 lines (helpers + tables) | no | delete |
| `docs/rebuild-experiment.md:579` | verbatim game text | `"Snow Jam is an exciting BEGINNER track"` | content | 1 quoted line (~40 chars) | no | edit |
| `docs/peaks-and-locations.md:42-68` | verbatim game text + data/table derived from the game | `"| 0 | Snow Jam | Snow Jam | ARA1 | 0 0 0 0 |"` (24 display/short-name rows) | content (display/short names); facts (codes, words, offsets `0x33e940`/`0x33f24c`) | 24 event rows + 50 location entries | no | edit |
| `native/diagnostics/course-start-freestyle.json:2` | verbatim game text | `"the event list becomes R&B / Crow's Nest / The Junction / Happiness Jam"` | content (short menu strings) | 1 JSON field | no | edit |
| `docs/research/120hz-f-spike.md:114-124` | decompiled/disassembled game code | `` "`8010ac1c fdivs f1,f1,f0` ... `8010ac20 bl" `` | content | ~10 lines of PowerPC excerpts + addresses | no | edit |
| `docs/research/ps2recomp-spike-2026-09-12/commands-and-outputs.md:307` | decompiled/disassembled game code (1-instruction example) | `` "addiu $r4, $r4, 0x20` becomes `ctx->r4 = ADD32(ctx->r4, 0X20);" `` | content (1 MIPS insn + 1 generated line); surrounding `sub_*` log lines are facts (30 mentions, filenames/addresses) | 1 example line; 30 `sub_00…` log mentions | no | edit |
| `local/research/P1/REPORT.md:307,402,420-427` | decompiled/disassembled game code (short excerpt) | `` "`0x42c278 beqz $v0` / `0x42c284 jal func_42C1A8`" `` | content (3-insn poll loop + `syscall 0`/`$v1=0x83`); call-order/counts are facts | ~8 lines; generated filenames (`output/sub_0042C1F0_0x42c1f0.cpp`) cited local-only | no | edit |
| `docs/gamecube-collision.md:85-95` | notes on disassembled game code (paraphrase; listing itself is untracked) | `` "`801DCAF0`/`801DEED4`: terrain surface halfword at patch +8" `` | facts (addresses + behavior paraphrase; `local/evidence/garibaldi-scenery/ssx3-disasm.txt` not tracked) | ~10 lines | no | edit |
| `docs/full-course-experiment.md:63-68` | notes on disassembled game code (paraphrase, no listing) | `"Inspection of the loaded MIPS instructions around `0x3a7768` shows a routine"` | facts | ~6 lines | no | edit |
| `docs/locale-tables.md` | data/table derived from the game | `"Snow Jam's description is index **549**, hash **0x0af521c1**"` | facts (index/hash/offset/slot/layout; `--find 'Snow Jam'` is a lookup key) | ~47-line file section | no | edit |
| `docs/location-anatomy.md` | data/table derived from the game | `"| 148 | 6175 | 4365701 | 3921076 | 444625 | [45] | 0:128 1:1739"` | facts (group/kind inventory; kind names per SSX-Library labels, unverified in play) | whole file | no | edit |
| `docs/course-selection.md` | data/table derived from the game | `"mode row `+4` | `0x802E2C1C` | 1 station/debug, 2 race, 3 slopestyle"` | facts (offsets, mode words, rename mechanics) | scattered lines | no | edit |
| `tools/course_presets/garibaldi.json`, `tools/course_presets/aloha.json` | data/table derived from the game | `"donor": { "code": "gari", ... } / "target": { "location": "ARA1"` | facts (codes, anchors, yaw/scale, gate counts are measurements/config) | 2 files, ~40 lines each | no | edit |
| `docs/full-course-validation.json`, `native/validation.json`, `native/mobile-validation.json`, `docs/runtime-validation.json` (+ hash lines in `docs/aloha-conversion.md`, `docs/gamecube-*.md`, `docs/rebuild-experiment.md`, `docs/investigation.md`, `local/research/S2*/REPORT.md`) | hashes of game/disc/build artifacts | `"archive_sha256": "395d342ff54e8bf37274e13b54802fde14632e4ed44e70aaea31f486587156a5"` | facts (199 hex-pattern hits reviewed; all are SHA-256-length hashes, not byte dumps) | 199 `git grep -E '([0-9a-fA-F]{2}[ ,]?){32,}'` hits across ~30 files | no | edit |
| `docs/gamecube-scenery.md:442-443` | decoded-record table excerpt | `"001 ...0007 0001 00000000 00000005 0000037f 00000380 00000381"` | facts (flipbook mode-word table, not game bytes) | 2 table rows | no | edit |
| `tools/gamecube_lun.py:28`, `tools/gamecube_spline_import.py:27` (+ test fixtures using them) | authored stub, assessed-not-game-content (recorded for completeness) | `"EMPTY_RETURN = bytes.fromhex('004e554c0000001400000024000000242aff"` | neither (36-byte authored empty LUN return; below the 64-byte threshold) | 1 line + synthetic test fixtures | no | — |

Negative results recorded (no rows added for these):

- Hex/base64 scan: no tracked hex dump or base64 blob longer than 64
  bytes holding game bytes. The single base64-pattern hit
  (`docs/share-recovery.md:62`) is an Apple documentation URL.
- Asset-derived blobs: no tracked texture/model/terrain tables as data
  blobs, audio banks, script (`LUN`) contents, memory-card saves,
  `.dtm` files, or screenshots/images. `.dtm` (`det-record-007.dtm`),
  texture dumps (`tex1_*…png`), and `*.big`/`*.nbd`/`*.gsf`/`*.aip`
  inputs named in docs/tools are local-only and untracked;
  `git ls-files` shows no `.dtm`, no image extensions, and the
  `.gitignore` blocks `*.iso/*.dol/*.elf/*.big/*.nbd/*.pbd/*.sav/*.gci`
  and others.
- Generated guest code bodies: none tracked besides
  `tests/float-conversion-original-generated.h`. `func_802197A0`,
  `func_801097A0`, `chassis_dispatch`, `StaticRecompCore::Run`,
  `sub_00…` in docs/reports are profiler/log labels and filenames
  (facts), not code bodies. No `.recomp` files or register-context C++
  bodies are tracked. `native/patches/*` are host-side C++ integration
  (course redirect, observability, platform), with no guest code.
- `PRESS START` / `RELEASE START` in `native/diagnostics/*.json`,
  `native/ios/*.json`, and `native/ios/App.mm:1005` is Dolphin
  controller-input vocabulary plus timings, not game text.
- `tools/patch_locale.py` / `tools/build_course_image.py` default
  replacement text (`Garibaldi from SSX Tricky. Experimental terrain
  port; race setup in progress.`) is authored project text, not game
  content.

## 3. Third-party table

`third_party/` is git-ignored and untracked (`git ls-files` finds no
`third_party|vendor` paths; `git log --stat -- third_party/` is empty),
so the table describes on-disk checkouts plus their tracked records
(pins, patches, docs). No vendored third-party file is tracked outside
`native/patches/`.

| Directory / vendored file | Upstream project and URL | License file present and type | Upstream commit/version recorded | Tree modifies it? | Attribution preserved? |
|---|---|---|---|---|---|
| `third_party/ModernGekko/` (on disk, untracked) | `https://github.com/ExpansionPak/ModernGekko.git` (per `native/dependencies.json`; `PROVENANCE.md` also records RecompCore fork `ExpansionPak/RecompCore-ModernGekko`, original `aharonahdoot/RecompCore`, Dolphin base, DolRecomp submodule) | `LICENSE` present; GPL-3.0-or-later (per `PROVENANCE.md`); Dolphin aggregate notice in `vendor/dolphin/COPYING`, per-file SPDX in `vendor/dolphin/LICENSES/` (per `PROVENANCE.md`) | `0514d9f03f8602809f66fc92fdca87d30e752997` (`native/dependencies.json`); RecompCore `8b47e90bf62a599995425cdcb9bc172c9d39fd9c`, original upstream `53e04dc7940d0f93ff4f56b3f597a2cf7e922374`, Dolphin base `1ccbcaa04a95a5807d92429bf35598da345a3f16` (`PROVENANCE.md`); RecompCore `13e492094902644b0d113c586300d358640f9e19`, DolRecomp `fa0cf619e8d7eb8cba7eaf55267a12caaebb46aa` (`native/dependencies.json`) | Tracked tree carries deltas as `native/patches/*` (applied at bootstrap); no in-tree edits observed in tracked files (`git log --stat -- third_party/` empty; ignored checkout not diffed against upstream in this run) | `PROVENANCE.md`, `LICENSE`, `README.md` on disk; pins in `native/dependencies.json` |
| `third_party/SSX-Library/` (on disk, untracked) | `https://github.com/GlitcherOG/SSX-Library` (per `README.md`) | `LICENSE.txt` present; GPL-3.0 (license-text header; `README.md`/`docs/investigation.md` state GPL-3.0) | `5c345e08dc521b0b1041734925cf0ece085e84c9` (per `README.md` "Upstream reference" and `docs/investigation.md`) | No tracked copies; Python tools cite layouts (`LOC.cs`, `BIGF4.cs`, `PBDHandler.cs`, `SSBHandler.cs`, `AIPSOPHandler.cs`) without copying source | `README.md` "Upstream reference" section with URL + commit; `docs/investigation.md` inspected-file list |
| `third_party/sunpad-reference/` (on disk, untracked) | `https://github.com/chrissotraidis/sunpad` (per `native/dependencies.json`, `native/ios/README.md`, `docs/gamecube-feasibility.md`) | `LICENSE` present; GPL-3.0 (license-text header); `THIRD_PARTY_NOTICES.md` present | `ec20f8d843fa40a484c7455cacb90b19884867ec` (per `native/dependencies.json` and `native/ios/README.md`) | Tracked deltas recorded as `native/patches/*-platform.patch`; `native/ios/README.md` states Sunshine-specific addresses/cheats/scheduler settings are not used | `native/ios/README.md` "Upstream provenance" section with URL + rev; `THIRD_PARTY_NOTICES.md` on disk |
| `native/patches/moderngekko-android-egl.patch` (48 lines) | ModernGekko/RecompCore tree (target of patch) | Upstream license per ModernGekko row above (patch itself is project-authored delta) | Against pinned tree (see ModernGekko row) | Is the modification record (applies at bootstrap) | Patch headers retain target paths |
| `native/patches/moderngekko-android-flags.patch` (37) | as above | as above | as above | as above | as above |
| `native/patches/moderngekko-android-headless.patch` (33) | as above | as above | as above | as above | as above |
| `native/patches/moderngekko-dolphin-ios-dcblock.patch` (56) | as above (Dolphin submodule record; checked by `tests/test_dolphin_patch_records.py`) | as above | as above | as above | as above |
| `native/patches/moderngekko-dolphin-mixer-skip-silent.patch` (104) | as above (same record test) | as above | as above | as above | as above |
| `native/patches/moderngekko-memcard-read-rate.patch` (116) | as above | as above | as above | as above | Inline comment states hardware-rate behavior and what changes |
| `native/patches/moderngekko-metrics.patch` (49) | as above | as above | as above | as above | as above |
| `native/patches/moderngekko-platform.patch` (604) | as above | as above | as above | as above | `native/ios/README.md` provenance section describes lineage |
| `native/patches/recompcore-android-egl.patch` (32) | as above | as above | as above | as above | as above |
| `native/patches/recompcore-android-flags.patch` (26) | as above | as above | as above | as above | as above |
| `native/patches/recompcore-android-headless.patch` (250) | as above | as above | as above | as above | as above |
| `native/patches/recompcore-android-vulkan.patch` (34) | as above | as above | as above | as above | as above |
| `native/patches/recompcore-course-redirect.patch` (625) | as above | as above | as above | as above (SSX 3 course manifest hook; guest RAM rewrite at boot, `sys/main.dol` untouched per header comment) | Header comment describes scope |
| `native/patches/recompcore-observability.patch` (103) | as above | as above | as above | as above | as above |
| `native/patches/recompcore-platform.patch` (2354 lines; largest patch blob, 105691 bytes) | as above | as above | as above | as above | as above |

License/provenance unclear: no third-party directory or vendored file
with unclear license or provenance was found. All three on-disk
references have a license file on disk, a stated license type, and a
recorded upstream URL + commit in tracked files.

## 4. History table

| Item | Finding |
|---|---|
| Files deleted from the tree that were ever committed (`git log --diff-filter=D --name-only --format=`) | None: both the `COMMIT %H %s` form and the bare-name form return empty; `git log --all --oneline --diff-filter=D` is empty (observed line-deletions in `--stat` output only, no file deletions) |
| Blobs over 500 KB that ever existed (`git rev-list --objects --all` → `git cat-file --batch-check`, 2197 objects) | None: zero blobs with size > 512000 |
| Largest blobs ever (for reference; all < 500 KB) | `docs/todo.md` 115287 B; `native/patches/recompcore-platform.patch` 105691 B; `native/ios/App.mm` 101516 B; `docs/research/ps2recomp-spike-2026-09-12/commands-and-outputs.md` 96645 B |
| Screenshots/images ever committed (`*.png/.jpg/.jpeg/.gif/.bmp/.tga/.dds/.ktx/.webp` in `git rev-list --objects --all`) | None: zero matches; none tracked now (`git ls-files` image-extension grep empty) |
| Data-URI images inside Markdown (`git grep -nE 'data:image/' -- '*.md'`) | None: zero matches |
| Removal needing a history rewrite vs a plain commit | Nothing found whose removal would need a history rewrite. Every flagged item in §2 is in a current tracked file, so mechanical removal shapes are `edit` (redact/replace lines) or `delete` (remove the generated header) with a plain commit; no history-only flagged material exists |

## 5. Exact commands used

```sh
git ls-files | wc -l
git ls-files > /tmp/A1_lsfiles.txt; wc -l /tmp/A1_lsfiles.txt
cut -d/ -f1 /tmp/A1_lsfiles.txt | sort | uniq -c | sort -rn
awk -F/ '{if(NF==1)print $1" (root)"; else print $1"/"$2}' /tmp/A1_lsfiles.txt | sort | uniq -c | sort -rn
cat .gitignore
git status --short
git ls-files | grep -i -E "third_party|vendor|vendored"
ls -la third_party/; for d in third_party/*/; do echo "DIR: $d"; ls "$d"; done
cat native/dependencies.json
cat third_party/ModernGekko/PROVENANCE.md
head -n 20 third_party/ModernGekko/LICENSE
head -n 20 third_party/SSX-Library/LICENSE.txt
head -n 20 third_party/sunpad-reference/LICENSE
head -n 40 third_party/sunpad-reference/THIRD_PARTY_NOTICES.md
head -n 60 third_party/SSX-Library/README.md
git grep -nE '([0-9a-fA-F]{2}[ ,]?){32,}' -- . > /tmp/A1_hex.txt
git grep -nE '[A-Za-z0-9+/]{88,}={0,2}' -- . > /tmp/A1_b64.txt
git grep -nE 'func_8|sub_00|chassis_dispatch|\.recomp|register-context|RecompCore|DolRecomp|StaticRecomp' -- . > /tmp/A1_recomp.txt
git grep -niE 'mips|powerpc|disassembl|decompil|lw \$|addiu|ps2|EE PC|0x00[0-9a-f]{6}' -- . > /tmp/A1_asm.txt
git grep -nE 'Snow Jam|Garibaldi|Merqury|Metro City|Ruthless Ridge|Peak [123]|Elise|Mac|Kaori|Zoe|Psymon|Moby|Eddie' -- . > /tmp/A1_names.txt
git grep -niE 'press start|freestyle|alpine|big air|EXCIT|WORLDS/BAM|DATA/MODELS' -- . > /tmp/A1_menu.txt
git grep -niE '\.dtm|memory.?card|\.gci|\.sav|texture names|audio bank|LUN|WorldBin|WorldSpline|kind-16|aip\.bin|\.nbd|\.pbd|\.big|\.gdb|\.gsb|\.ghm|\.gsm' -- . > /tmp/A1_asset.txt
git grep -niE 'SSX-Library|LOC\.cs|SunPad|sunpad|ModernGekko|Dolphin|RecompCore|SDL|imgui|fmtlib|zlib|ninja' -- . > /tmp/A1_vendor.txt
git grep -nE '[0-9]{2,4}x[0-9]{2,4}' -- . 
git grep -n 'bytes.fromhex' -- .
git grep -n -E "fromhex\('[0-9a-fA-F ]{129,}'" -- .
git log --oneline | head -n 20; git log --oneline | wc -l
git rev-list --objects --all > /tmp/A1_objects.txt
git cat-file --batch-check < /tmp/A1_objects.txt > /tmp/A1_batch.txt
awk '$2=="blob" && $3>512000 {print}' /tmp/A1_batch.txt
git log --diff-filter=D --name-only "--format=COMMIT %H %s"
git log --diff-filter=D --name-only "--format=" | sort -u
git log --diff-filter=D --oneline
git log --all --oneline --diff-filter=D
grep -iE '\.(png|jpg|jpeg|gif|bmp|tga|dds|ktx|webp)(\s|")' /tmp/A1_objects.txt
git ls-files | grep -iE '\.(png|jpg|jpeg|gif|bmp|tga|dds)$'
git grep -nE 'data:image/' -- '*.md'
git ls-files | grep -iE '\.dtm$'
git ls-files -s | cut -d' ' -f2 > /tmp/A1_tracked_shas.txt; git cat-file --batch-check < /tmp/A1_tracked_shas.txt | sort -k3 -rn | head -n 15
git grep -n "SSX-Library\|GlitcherOG\|LOC.cs" -- .
git grep -n "chrissotraidis/sunpad\|sunpad" -- .
git log --stat -- third_party/
```

Read-only file reads (via `read_file`/`sed`/`head`/`grep -n`): `docs/locale-tables.md`,
`docs/peaks-and-locations.md`, `tools/course_presets/garibaldi.json`,
`tools/course_presets/aloha.json`, `docs/location-anatomy.md`,
`tools/patch_locale.py`, `tools/patch_executable.py`,
`tools/build_course_image.py`, `tools/gamecube_lun.py`,
`tests/test_gamecube_lun.py`, `tests/test_gamecube_game_dir.py`,
`tests/test_gamecube_interactions.py`, `tests/float-conversion-original-generated.h`,
`native/patches/recompcore-course-redirect.patch`,
`native/patches/moderngekko-memcard-read-rate.patch`,
`docs/rebuild-experiment.md`, `docs/full-course-experiment.md`,
`docs/gamecube-collision.md`, `docs/gamecube-scenery.md`,
`docs/research/120hz-f-spike.md`,
`docs/research/ps2recomp-spike-2026-09-12/commands-and-outputs.md`,
`local/research/S2/s2_replay_capacity.h`, `docs/asset-policy.md`,
`docs/texture-remaster.md`, `native/ios/README.md`, `README.md`,
`docs/investigation.md`, `tests/test_dolphin_patch_records.py`,
`native/diagnostics/course-start-freestyle.json`.

## 6. What I could not do

- The runbook's commit step (`git add -f local/research/A1/`, `[A1]`
  prefix, co-author/session trailers) was not performed: the invoking
  instruction for this run forbids changes to tracked files, so this
  report is left as a new untracked file and nothing was staged.
- `git log --stat -- third_party/<x>` and any diff of the ignored
  checkouts against their recorded upstream commits were not run as
  tree diffs: the checkouts are untracked/ignored, so git history
  covers them with zero commits; comparing working-tree checkouts to
  upstream would need network fetches outside the read-only box.
- Local-only evidence named in tracked files (e.g.
  `local/evidence/garibaldi-scenery/ssx3-disasm.txt`,
  `local/research/startgate/host-script.bin`,
  `local/game/...`, `local/source/...`, `det-record-007.dtm`,
  dumped `tex1_*…png` files) was not opened: only the tracked
  references to those paths were inspected.
- `local/` beyond this report directory was not touched; no builds
  were run; `adb` was not used.
