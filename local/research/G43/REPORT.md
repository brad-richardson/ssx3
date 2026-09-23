# G43 report — HAL layout fixed, Turnip runs to Done! but B lands with different content (285accdf≠840cd308); sys control flips C1+C4 to lost

## 0. Outcome first

The G43 hunk works: with `reserved[12]` restored, all four HAL device ops
are non-null code pointers inside the Turnip `.so`'s mapped text, Turnip
initializes (Adreno 830, API 1.4.359, Driver 26.2.99) and leg T runs to
`Done!`. But the brief's branches don't cover what happened: B under Turnip
is **neither** `840cd308…` (lands) **nor** `eea04488…` (Adreno loss) — it is
`285accdfb83609fa`/699122, full coverage (same nz, same head) with different
pixel content, and 9/10 scanouts show varying content. And the sys control
(C1 repeat) came back **C1 LOST + C4 LOST** (C4 never flipped before).
Taken branch: closest to brief branch 2 ("B still lost ⇒ our pipeline"):
acceptance (Odin-B == `840cd308…`) unmet → table it, stop, no Mission 2
(its "C1-only loss" premise is also broken). Recommendation in §6.

## 1. Pins and receipts

- Working copy `~/dev/ssx3-work/G43/parallel-gs` @ `3a66c19` + SSD-tracked
  diff (equality proof §2) + the G43 hunk (`g43-hunk.diff`); Granite
  `16e7395f` + SSD shims. Nothing committed to either fork.
- NDK r30 `30.0.16248370` at `/opt/homebrew/share/android-ndk` (fresh
  `brew install --cask`, no sudo).
- Odin `622c49b1`, Android 15. Keyguard `showing=false` pre-run; battery
  91 %, AC powered. Lease claimed `G43 2026-09-23T01:11:30Z`, released +
  `/data/local/tmp/g43/` removed after pulls. Shell binary only, nothing to
  force-stop. No new tombstone (`_23` newest before and after).
- Turnip driver: same pinned StevenMXZ `Turnip_Gen8_V36.zip` `.so`
  (`717812c3…`, 14,188,488 B) staged from the internal copy.
- Binary SHAs (two matching host reads + on-device re-read, all equal):
  replayer `c4d1c3342d7727f0`, dump `154d9d8577a210fb`, Turnip `.so`
  `717812c3c51fd283`. Mac binary `767dd6b1…` (51,934,456 B).
- Runs: `local/research/G43/g43-run-odin.sh both` — leg T RUN_EXIT=0
  (Done! + 10/10 PPMs + no tombstone; the numeric exit scrolled out of the
  captured head, gap stated), leg S RUN_EXIT=0, all 10 PPMs each, `Done!`
  both. T wall ~10 s, S wall ~1 s (plausibly cold Turnip shader compile vs
  warm Adreno system cache; diagnostic-build timings, not speed numbers).
- Receipts: internal `~/dev/ssx3-work/G43/odin-run/` (2 logcats + 20 PPMs);
  share mirror `/Volumes/share/ssx3/ps2x-g43/` (same 22 files).

## 2. Mission 0 — equality proof (internal copy vs SSD source of truth)

- Method: `git clone ~/dev/parallel-gs` → `checkout -b g43-work 3a66c19`;
  Granite submodule from the local module store at `16e7395f`; SSD tree's
  tracked `git diff` applied in two parts (main / Granite-internal); 18
  nested Granite third_party submodules initialized from local object stores
  at SSD-pinned commits (nested gitlinks identical). Zero network fetch.
- Main repo `git diff --ignore-submodules`: sha256 `1d4c069e…e259` on BOTH
  sides (`cmp` identical). Granite `git diff --abbrev=40`: sha256
  `8ffa13bf…ab7934` on BOTH sides (`cmp` identical). (Default-abbrev display
  differs only in auto-abbrev length, 8 vs 7 hex — repo-size artifact.)
- Delta vs `~/dev/parallel-gs` `wip/ssx3-snapshot` (`faf6400`): main-tree
  content BYTE-IDENTICAL to faf6400's committed tree (72270 B diff, empty
  `diff`); Granite content identical (faf6400 gitlink `aaeee97` embeds the
  same 5-file shims as the SSD uncommitted Granite diff). Net delta of the
  working copy vs faf6400: the G43 hunk only.
- Byte cap: `~/dev/ssx3-work/G43` 5.4 GB of 15 GB; all-ssx3 internal
  16.6 GB of 200 GB (budget script exit 0). Nothing built or linked on SSD.

## 3. The fix and the four pointers + `.so` range (Mission 1.1)

`G42HalDevice` gains `uint64_t reserved[12]`; `static_assert`s pin
`close==112`, `enum_ext==120`, `create_inst==128`, `get_proc==136` on LP64 —
both the Mac arm64 and Android arm64 builds compiled them, proving the
offsets on both ABIs at compile time. Turnip leg logcat:

- `G42: HMI tag=48574d54 id=vulkan name=Mesa 3D Vulkan HAL …`
- `G43: HMI maps at base=0x73c8e4d000 file=/data/local/tmp/g43/libvulkan_freedreno.so`
  + 4 `/proc/self/maps` lines; text segment `r-xp 73c9772000-73c9b43000`.
- `G43: HAL dev tag=48574454 close=0x73c98cdb90 enum_ext=0x73c980b18c create_inst=0x73c9807048 get_proc=0x73c980b1b8`
  — all four non-null, all inside the `.so` text range. The brief's
  correct-behavior model holds exactly.
- Driver identity: `Adreno (TM) 830, API 1.4.359, Driver 26.2.99`
  (vs sys control `API 1.3.284, Driver 512.800.58`). The 1.4.359 API matches
  the Turnip v36 release notes → leg T genuinely ran on Turnip.

## 4. Turnip vs system-driver table (G42 format)

| row | Turnip leg (T) | System control (S) |
| --- | --- | --- |
| driver identity | Mesa HMI → HAL open rc=0 → 4 ops in-`.so` text → Adreno 830, API 1.4.359, Driver 26.2.99 | `(system)` → Adreno 830, API 1.3.284, Driver 512.800.58 |
| B at boundary 1 (O3/O3b/G31) | O3 `285accdfb83609fa` nz=699122 head=`d5530000…`; O3b identical; G31 seq1 B identical (A bytes identical to Mac both seqs) | O3 `eea04488c453e75b` nz=149721 head=0; O3b identical; G31 B identical (Mac B: `840cd308c91c4d8a`/699122) |
| scanouts (10/10 SHA) | 9 with content (vsync1 `323d6a3d…`, vsync2 `4a864021…`, vsync3 `4481bba7…`, vsync4/5 `bcef2d53…`, vsync6/7+last `b7a307fa…`); vsync0/first blank `99418f1b…` (as Mac) | all 10 blank `99418f1b…` |
| canary C1–C5 | ALL LANDED byte-exact (C1 `0c1f0f28…`/4932, C2 `8803470a…`/4211, C3 `19a7754f…`/4211, C4 `dfce1467…`/4211, C5 `b8d9711b…`/1328) | C1 LOST nchg=0, C4 LOST nchg=0; C2/C3/C5 landed byte-exact |
| G26 / G28 | G26 delivered line present; G28 descriptorBuffer-skipped line ABSENT (branch presumably not skipped under Turnip — capability difference, benign) | G26 ×1, G28 ×1 (as G42) |
| census / overlap | 16/16 cord, 32/32 census, fov=0 zov=0 clean; recomp==O4m true (`95de73fe…`); input diffs ⊆ {texa, mb46}; rect SAME | 16/16, 32/32, clean; recomp==O4m true (`04916dd9…`); diffs ⊆ {texa, mb46}; rect SAME |

Mac F0 (same binary family, `(system)` first line): B cord1 `840cd308…`/
699122; C1–C5 all landed byte-exact; 10/10 scanout SHAs named-identical to
G42 Mac; strict content diff (2549 lines, host/timing/path classes excluded)
0-diff vs G42 Mac stderr. No perturbation.

## 5. Budgets: Mac builds/runs 1/1, Odin builds/runs 1/2 (+1 session), ~2 h of 3 h.

## 6. The ONE next action (orchestrator decides)

**New brief: page-level B diff (Mac `840cd308` vs Turnip `285accdf`) +
canary-intermittency triage — no wall.** (a) Diff the B pages between the
Mac and Turnip runs (which pages/bytes differ: whole-B shift vs localized
region) to decide whether Turnip's B is "Adreno-loss fixed but off-palette"
or a second driver quirk (Turnip-on-A830 is young; our pipeline may also be
driver-sensitive in content, not just in landing). Cross-check the differing
region against a T-lane PCSX2 reference if one covers this dump. (b) The
canary record across three same-shape sys runs is now {G41-O1: C1 lost},
{G42-S: none lost}, {G43-S: C1+C4 lost} — Odin run variance is confirmed
independent of the loader hunk (the G41→G42 flip predates any hunk change;
the G43 system path executes zero new instructions — early return before
all new code — and Mac F0 is 0-diff, so hunk perturbation on the sys path
is ruled out by construction). Mission 2's "C1-only loss" premise no longer
holds; don't fire the combined wall until (a)/(b) re-baseline it. The
proprietary-driver-fault verdict is half-proven (writes land with full
coverage under Turnip) but byte-exactness is open — no Turnip-bundling
recommendation yet.
