# N8A — Android paraLLEl + Turnip integration map

You are a Codex worker in `~/dev/ssx3`. Follow `~/dev/AGENTS.md`,
`AGENTS.md`, `local/AGENTS.local.md`, and `docs/orchestration.md` §4.
This is a **read-only** source/packaging audit. Hand back the evidence
table and one Part-2 runbook; the orchestrator chooses implementation.
Your only writes are `local/research/N8A/REPORT.md` and ≤5 MiB of bounded
text receipts under `~/dev/ssx3-work/N8A/`. No source edit, build, boot,
device shell, APK install/launch, or push. No upstream contact.

Start from `local/research/N7/REPORT.md` (N7 Android branch and one Odin
race), `local/research/GB6C/REPORT.md` (GPU backend folded, opt-in), and
`local/research/G43/REPORT.md` plus `docs/todo.md:607-617` (Turnip HAL
test and Brad's bundling approval). Current fork `ssx3` remote tip is
`0cab7d733179e0706b6262e6b6f0a8cd89b274b9` (E54F2 Count on GB6).
N7's bytesize WSL local branch is `n7-android` `81aa92d`; inspect it
read-only through `ssh bytesize`/WSL. Mac fork source is available in
`~/dev/ssx3-work/E54F2/PS2Recomp`. paraLLEl source is the local G43
copy `~/dev/ssx3-work/G43/parallel-gs`. Turnip v36 `.so` pin from G43
is SHA-256 beginning `717812c3`; find and hash the local staged copy
without moving or writing it.

## Table to hand back

1. **Revision delta:** which Android-specific commits from N7 are already
   in fork `0cab7d7`, which must be carried into a new N worktree, and
   any test-registration or build-file conflicts. Cite `git` diffs/paths;
   do not cherry-pick or rebase in Part 1.
2. **Build/link path:** trace `android/app/build.gradle`,
   `AndroidManifest.xml`, CMake options and the runtime backend selection
   from APK packaging to the opt-in `PS2X_GS_BACKEND=parallel` path.
   Name local source paths/CMake flags and any Android compile/link gaps.
   Distinguish the GB6 in-process backend from G43's standalone shell
   replayer.
3. **Turnip loader:** identify where G43's HMI hook exists today, whether
   it is present in the app/Granite path, and exactly how the APK would
   package, locate and select `libvulkan_freedreno.so` on Android.
   Trace each edge in source or state `not found`; do not assume
   `GRANITE_VULKAN_LIBRARY` works on Android because it works on Mac.
   Check ABI/dependency/namespace constraints from local source and the
   G43 receipt, without an external web claim.
4. **Part 2:** one narrow build/install/launch brief with explicit files,
   source/driver SHA gates, ≤2 APK builds and ≤1 Odin launch, bounded
   progress and battery/keyguard/lease/force-stop checks. Name the
   observable that proves Turnip identity and GPU backend use, versus
   CPU fallback or system Vulkan. State a source-only blocker if one is
   found, and separate optional performance profiling.

Budget: 20 minutes; read small source ranges and use `rg`/`git`/LSP
connections, not whole trees in context. No heavy bytesize job, so the
one-heavy-job rule is unaffected. Stop when an edge needs an Android
build or device observation; record that gap rather than guessing. Do
not infer that Turnip can be bundled from the shell replayer alone.

Deliver `REPORT.md` with pinned revisions, path/line citations, exact
commands, Turnip SHA, evidence table, unresolved edges and Part-2
runbook. Commit only the explicit report `[N8A]` with
`Orchestrated-By: Codex`; no push. The orchestrator gates it.
