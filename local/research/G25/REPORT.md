# G25 report — Separation: G24 binary REBUILT bit-identical (zero-destroyed on disk), no-flag run returns O4 (Odin)

Brief: G25 (this turn) — executes G24 §4's separation ONLY, with one forced
addition: (1) REBUILD the on-disk G24 binary (orchestrator-verified
100% zero-destroyed, G18-damage class) in the SAME build dir and prove
bit-identity (else table + STOP); (2) run the REBUILT binary WITHOUT
`--disable-sampler-feedback` (same dump/iterations, ONLY delta the absent
flag) + `g14-diff.py` pixel-diff vs G13 oracles. Tables + hypothesis +
next-action recommendation, no verdicts beyond the hypothesis. Time box
6 h (used ~0.15 h — measured wall 13:26:52→13:36 EDT). Read first per the brief:
`local/research/G24/REPORT.md` (all of it). No upstream contact of any
kind (standing no-upstream order — local hunks only, filing stays local).

Machine: same as G8-G24 (Apple M4, macOS — no new installs).
Device: Odin3 (`622c49b1`, Android 15), transient dir `/data/local/tmp/g25/`
ONLY; removed at end (`mg/` only).

Headline result: (1) The rebuild reproduces the G24 link BIT-IDENTICALLY
(size/sha/BuildID/ELF/`strings` all exact — G24's byte-deterministic-link
claim holds a second time). (2) The separation run WITHOUT the flag dies
139/SIGSEGV at FIRST DRAW on O4's exact signature (crasher pre-create
dangling as the last log line, 43-frame tombstone through
`dispatch_texture_analysis` → `vkCreateComputePipelines` → libllvm-qgl):
O4 RETURNS without the flag. (3) O6 attribution is therefore UNRESOLVED —
the O6 post-loop site was never reached, so neither the flag path nor the
ride-along is implicated or exonerated. (4) Consolation with teeth: same-sha
binary, flag=1 → O4 absent (G24), flag=0 → O4 present (G25) is a
bidirectional A/B that confirms the flag's efficacy far more strongly than
G24 alone. Score N/A for the third brief in a row (0 scanouts, now blocked
by the O4-return). One run spent; retry not used (O4 is not O1/O3).

## 0. Byte caps (declared at session start) vs actuals

| class | cap | actual |
| --- | --- | --- |
| G24 build dir (rebuild in EXISTING dir, no new dir) | 0 growth (relink only) | 4,482,048 KiB before AND after (== G18/G20/G22/G24 dirs exactly) PASS |
| NEW SSD `ps2x-g25/` (retrieval: logcat + tombstone_19, 0 PPMs) | 50 MB | ~179 KB apparent; 5,120 KiB allocated (ExFAT clusters) PASS |
| SSD `ps2x-g10..g24` + G14/G18/G20/G22/G24 build dirs (read-only) | 0 growth | all == pre-run snapshot exactly (g10 43008, g14 7168, g18 5120, g19 5120, g20 11264, g21 15360, g22 25600, g23 9216, g24 5120, g14-build 4480000, g18/g20/g22/g24-build 4482048 KiB) PASS |
| SSD clone (source) | ZERO edits | HEAD + HUNK_MATCH (G22 + G24) re-verified; hunk UNCOMMITTED PASS |
| internal volume (`/`) | <=1 GB delta, no clones/builds | 13 Gi avail before and after; no `/tmp/g25-*` residue PASS |
| SSD volume | — | 222 Gi avail before and after (G24 report-time was 227 — other-lane delta) |
| device | `/data/local/tmp/g25/` ONLY | pushed 2 files, pulled 2, dir removed after (`mg/` only) PASS |
| network | none used | no clones, no installs PASS |
| host build | ONE rebuild, `-j2`, same dir | `[1/1]` relink exit 0, ~5 s, no recompiles PASS |
| committed to git | text only | REPORT.md only; no binaries |

No P-lane lease, no bytesize/WSL. `COPYFILE_DISABLE=1` on all SSD steps.
No code copied into any project tree.

## 1. Experiment contract

| slot | content |
| --- | --- |
| hypothesis | The rebuilt binary is bit-identical to the tested G24 binary; running it WITHOUT the flag separates O6's cause: O6 persists at the same site => the `feedback_render_target` ride-along is implicated (next: narrower hunk delivering ONLY the flag); scanouts write => the flag's full-upload path is implicated (next: instrumentation scoped to that path + bright-vs-black read) |
| observable signal | damage confirm (size/sha/magic/build-id/`strings`) + relink exit/sha/build-id + ONE bounded no-flag run (exit/wall/fate + `G24:` receipt at =0 + knob receipts + crasher presence/absence + tombstone triage if any) + scanouts pulled and scored (`g14-diff.py`) + O4 legs + O5 table |
| alternatives | (a) O6 persists => ride-along; (b) scanouts write => flag path; (c) O4 returns at first draw => flag efficacy confirmed bidirectionally, O6 attribution UNRESOLVED (site never reached); (d) O1/O3 instead of first draw => lottery note + ONE retry |
| stop condition | ZERO source edits; ONE rebuild (same dir); TWO bounded device runs max (separation run + one retry iff O1/O3 fires instead of first draw); no tuning loop, no second shape, no new dumps; no lldb unless the tombstone cannot triage; rebuild-identity miss => table + STOP (never test a different binary) |
| outcome → next action | numbers name the next single experiment (§4) |

Outcome: alternative (c) — rebuild identity EXACT (no STOP), then O4
returns at first draw. No tuning loop was entered: zero edits, one
relink, one device run. Retry not used (O4 is not O1/O3, and first draw
was reached); lldb not used (tombstone classifies; tabled §3h).

## 2. Task 1 — rebuild bit-identical (no device until §3)

### 2a. Damage confirmation (start re-sha #1 — vs G24 §2c pins)

| signal | G24 §2c pin | G25 start read | verdict |
| --- | --- | --- | --- |
| size | 265,840,424 B | 265,840,424 B | PRESERVED |
| mtime | 12:49:21 (build) | 2026-09-21 12:49:21 | FROZEN (post-run storage damage, NOT a rebuild) |
| sha256 | `562a0bcf…8f4a` (3 matching reads) | `fc62d01af672ee001739b44094f6effd3e4f30f820b8b4bfc95e56bd0c378893` | DESTROYED (brief's `fc62d01a…` confirmed) |
| magic | `7f45 4c46` ELF | `0000 0000` | ELF gone |
| zero fraction | — | 100.0000% (0 nonzero / 265,840,424 B) | TOTAL |
| first-MB sha | — | `30e14955…` (1 MiB-zero canonical) | all-zero |
| build-id | `c7f68343e5a61c089593374cecc5896441798fe9` | unreadable (`llvm-readelf`: `Format: COFF-<unknown arch>`) | gone |
| `strings` G24 receipt | ×1 | ×0 | gone |
| `strings` disable-sampler-feedback | ×2 | ×0 | gone |
| scope | — | 611 files scanned in build dir: ONLY the binary head-zero | isolated, G18-damage class |

G24 run evidence stands per the G18/G20 precedent (the TESTED binary was
good — tombstone_18 BuildId `c7f68343…` matched; G22 binary intact, §2b).

### 2b. Pre-rebuild verification (pins + 0-growth + device, ZERO edits)

| item | observed |
| --- | --- |
| SSD clone HEAD | `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd` (== pin) |
| tree status | `M CMakeLists.txt` + `m Granite` + `M gs/gs_interface.cpp` + `M gs/gs_renderer.cpp` + `M tools/CMakeLists.txt` + `M tools/gs_dump_replayer.cpp` + ExFAT `._` sidecars — G24 post-hunk exactly |
| G22 hunk | `git diff gs/gs_renderer.cpp` byte-identical to `g22-workaround.diff` (HUNK_MATCH) |
| G24 hunk | worktree `@@ -93,9 +96,12 @@` block byte-identical to committed `g24-plumbing.diff` (HUNK_MATCH); other `@@` blocks are the pre-existing G8/G10 hunks, untouched; hunk UNCOMMITTED |
| Granite diff | `platforms/CMakeLists.txt` + `timer.cpp` + `command_buffer.cpp` +18 + `shader.cpp` — G22 §2a exactly |
| G22 binary (reference) | 265,840,344 B, sha `5e1f7827…` prefix-match (zero-fill watch: intact; NOT the tested binary) |
| hunk TU object | `gs_dump_replayer.cpp.o` 1,888,312 B, valid ELF, `G24: debug_mode delivered` ×1 (link inputs intact — relink-only rebuild expected) |
| rich dump (host) | 11,537,377 B, sha `154d9d85…d7e32` full-match |
| dirs 0-growth | pre-rebuild `du -sk` == G24 §0 exactly (see §0); post-run re-verified §0 |
| recipe | CMakeCache: NDK toolchain + `arm64-v8a` + `android-35`; NDK r30; cmake 4.4.3 + ninja (same recipe/NKT) |
| device (read-only pre-check) | `622c49b1`, Odin3; `/data/local/tmp/` == `mg/` only; newest tombstone `_18` (G24's O6, 12:49); `/data` 28 G free |
| `g14-diff.py` + oracles | tool present; `ps2x-g13/` holds dump + 8 vsync PPMs |

### 2c. Rebuild record (SAME dir — relink only)

| item | observed |
| --- | --- |
| method | `rm` the zero-destroyed binary (FORCED: mtime-frozen zeros would read up-to-date to ninja; evidence recorded §2a) + `cmake --build … --target parallel-gs-replayer -j2` |
| build | exit 0 (`[1/1] Linking CXX executable tools/parallel-gs-replayer`, ~5 s wall, no recompiles, no warnings — link-only; TU warnings already captured in G24's `g24-tu-rebuild.log`) |
| size | 265,840,424 B (== pin EXACT) |
| magic | `7f45 4c46` ELF (restored) |
| sha (post-build re-sha #2) | `562a0bcf14e621ddd21b22d318197a26338a562446e47f9826f67a12fffc8f4a` (FULL-match — 4th lifetime read including G24's three) |
| sha (pre-push re-sha #3) | same `562a0bcf…` FULL-match |
| sha (report-time re-sha #4) | same `562a0bcf…` FULL-match |
| build-id | `c7f68343e5a61c089593374cecc5896441798fe9` (== pin EXACT) |
| `strings` | `G24: debug_mode delivered` ×1, `disable-sampler-feedback` ×2 (== pins EXACT) |
| build dir | 4,482,048 KiB after (== before — 0 growth) |

Identity gate: REPRODUCED BIT-IDENTICALLY on all six signals
(size/sha/BuildID/ELF/`strings`×2). No STOP. G24's byte-deterministic-link
claim now holds across two relinks (G24's TU relink + this full-output
relink from intact objects).

## 3. Task 2 — ONE bounded no-flag run + score + attribution (Odin)

### 3a. Knob matrix (the ONLY delta vs G24's run is the absent flag)

| knob / flag | G24 setting | G25 setting | rationale |
| --- | --- | --- | --- |
| `--disable-sampler-feedback` | SET | ABSENT | the separation variable — ONLY delta |
| `PGS_SKIP_SAMPLER_FEEDBACK` | UNSET | UNSET | no G22 skip to mask or confound |
| `PGS_SKIP_COMPILATION_TASKS=1` | KEPT | KEPT | same async-path control as G22/G24 |

Predicted discriminators: `G24: …disable_sampler_feedback=0` receipt
(delivery still unconditional, value passthrough correct) + O6 persists at
the same Scudo site => ride-along implicated => narrower hunk next;
scanouts write (bright or black) => flag path implicated => scoped
instrumentation next. (Third outcome, observed: O4 returns — §3d.)

### 3b. Run table (ONE run — retry not used, §3h)

| item | observed |
| --- | --- |
| staging | `/data/local/tmp/g25/` ONLY; dump + REBUILT binary pushed; on-device shas FULL-match host (`154d9d85…` / `562a0bcf…`); logcat cleared, Granite empty before |
| command | `PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer /data/local/tmp/g25/g13-dump.gs --iterations 2` (NO flag — cmdline receipted in tombstone) |
| exit / wall | **139** (SIGSEGV — O4's exit, NOT O6's 134) / ~1 s wall (`date` 1790011764→1790011765; logcat 13:29:25.020→13:29:25.158; tombstone .178; `Process uptime: 1s`) |
| DELIVERY receipt | line 29 `G24: debug_mode delivered (disable_sampler_feedback=0, use_rdoc=0).` (×1) — unconditional delivery confirmed AGAIN, value passthrough correct (0 with no flag); behavioral proof the rebuilt binary == G24 binary |
| knob receipts | line 25 `Skipping precompilation…` (×1, async knob effective); line 28 `Failed to load RenderDoc` (`use_rdoc=false`, as ever); 0 `G22: skipping` (knob unset, as designed) |
| logcat | 49 lines: init + ext list + 1 `Running frame` + `G10: pass 0 stats reset` ONLY (no pass 1) + 5 G11 lines + 2 compute compiles `success: yes` + crasher pre-create DANGLING as the LAST line; 0 `success: no`; 0 `wrote … scanout`; 0 `Done!`; 0 Total-time |
| phase | FIRST DRAW, first vsync, pass 0 — died before completing even one pass (vs G24's full 18-frame / 2-pass loop) |
| fate | O4 RETURNS (§3c–§3d): 139 + dangling crasher + driver-compile stack. NOT O1/O2/O3 (first draw reached, init clean); NOT O6 (no Scudo abort, pre-loop death — the O6 site was never reached) |
| device outputs | 0 scanouts; tombstone_19 written 13:29 (pulled, §3c); device dir removed after (`mg/` only ✓) |

### 3c. Tombstone_19 triage (pid 11147 — O4's exact signature)

| slot | fact |
| --- | --- |
| signal | SIGSEGV (signal 11, SEGV_MAPERR, null-pointer dereference, fault addr 0x0) — O4's signal, not O6's SIGABRT |
| stack | 43 frames: libllvm-qgl #00–#17 (EXECUTING, 18 frames) ← adreno #18–#20 (BuildId `d05dded9…`) ← `vkCreateComputePipelines` (#21) ← `PipelineCache::create_pipeline` (#22) ← `build_compute_pipeline` (#23) ← `flush_compute_pipeline` ← `flush_compute_state` ← `dispatch` (#26) ← **`dispatch_texture_analysis`** (#27) ← `flush_rendering` ← … ← `iterate_until_vsync` (#40) ← `main` (#41) ← `__libc_init` (#42); main thread pid == tid |
| timing | 13:29:25.178 = ~20 ms after the last logcat line (crasher pre-create, .158); the crashing compile never posted its Stalled line |
| classification | O4 (first-draw driver compile death in the `sampler_feedback` dispatch): exit + phase + dangling crasher + stack path all match G23 run 2 / G20 — full leg table §3d |
| Scudo | detector did NOT fire: `corrupted chunk` ×0, abort message ×0; the 91 `scudo` lines are all `[anon:scudo:primary/secondary]` memory-map annotations (every tombstone has them) |
| flag involvement | the ONLY delta vs G24's run is the absent flag: value 0 re-enables the `sampler_feedback` dispatch + crashing compile (G23-run-2 precedent) — the A/B arm G24 predicted |
| binary identity | tombstone BuildId `c7f68343…` == rebuilt binary (FULL-match) => the tested binary is proven to be the rebuild |
| census | `dispatch_texture_analysis` ×1; `vkCreateComputePipelines` ×1; `libllvm-qgl` ×24 (executing, vs mapped-not-executing in O6); `7463…`/`c61f…` ×0 in tombstone (Granite-side hashes — identified via the dangling logcat pre-create) |

### 3d. O4-presence proof (four legs, mirrored on G24 §3d's absence legs)

| # | leg | evidence |
| --- | --- | --- |
| 1 | exit/signal/phase match | 139/SIGSEGV; died in FIRST DRAW (pass 0, no Total-time) vs G24's 134/post-loop — same phase as G23 run 2 |
| 2 | crashing input exists and dangles | crasher pipeline `7463dfd379df2855` / shader `c61f1a8116a82d4b` pre-created as the LAST log line with NO paired Stalled post; 2/2 other compiles `success: yes`, 0 `success: no` |
| 3 | death stack is all driver-compile | 18 executing libllvm-qgl frames ← adreno `vkCreateComputePipelines` ← Granite pipeline-build ← `dispatch_texture_analysis`; zero Scudo-abort frames, zero descriptor-cleanup frames |
| 4 | G23-run-2 match | 49-line logcat = G23r2's 48 + EXACTLY the G24 receipt line; same crasher hashes; 43-frame tombstone (`43 total frames` header); same path suffix `dispatch_texture_analysis → flush_rendering → … → iterate_until_vsync → main` |

Brief-expectation note (tabled miss, informative not a failure): the brief
expected O4 ABSENT ("delivery still unconditional") — observed PRESENT.
Delivery and flag VALUE are orthogonal: with no flag the unconditionally
delivered value is 0, which re-enables the `sampler_feedback` dispatch +
crashing compile (G23-run-2 precedent predicted exactly this). The miss
completes the bidirectional A/B: same-sha binary, delivered =1 → O4
absent (G24), delivered =0 → O4 present (G25) — the flag's efficacy is
confirmed far more strongly than by G24 alone (2 O4-present runs at
value-0/dropped vs 1 O4-absent run at value-1, plus the crasher-compile
mechanism — the lottery is strongly disfavored).

### 3e. Score vs G13 oracles (`g14-diff.py`, zero new tooling)

`g14-diff.py ps2x-g13 ps2x-g25` (tool exit 0): oracles **ALL OK**
(8/8 pixel-shas); device PPMs: **0**; `SCORE: N/A - 0 device scanouts`.
(The tool's parenthetical cites its own G14 run; the G25 reason is tabled:
death at first draw on the O4-return, before any scanout readback.) No
means/PSNR exist to table — the bright-vs-black adoption read is UNMADE
for the third brief in a row (G23: O4 → G24: O6 → G25: O4-return).

### 3f. O5 re-fire table (expected post-`Done!` either way — observed: no)

| run | reached teardown? | O5 fired? | note |
| --- | --- | --- | --- |
| run 1 (O4-return) | NO (died first draw, pre-`Done!`) | NO | SIGSEGV in driver compile, not a Scudo abort at any named site |

O5 status: unchanged from G24 (named, writer unnamed, three detection
sites in the family — O3-init, O5-post-`Done!`, O6-pre-write — all
writer-unnamed). This brief neither confirms nor denies its re-fire
without the flag — no run reached teardown.

### 3g. O6-attribution verdict (the separation question — UNRESOLVED)

| candidate | verdict | evidence |
| --- | --- | --- |
| flag's full-upload path | UNRESOLVED | absent in this run, but the run died before the O6 site — neither implicated nor exonerated |
| `feedback_render_target` ride-along | UNRESOLVED | PRESENT in this run (delivered unconditionally, =true as in G24), but the O6 site was never reached — neither implicated nor exonerated |
| O6 site reached? | NO | first-draw death; G24's O6 fired post-loop in scanout readback — 18 frames + Total-time past this run's death point |

The separation as designed cannot attribute O6: the no-flag run dies at
O4 before the discriminating phase. The run is not wasted — it converts
G24's one-directional delivery evidence into a bidirectional A/B (§3d)
and proves the rebuild behaviorally identical (§3b receipt) — but the
flag-vs-ride-along question needs a run that REACHES post-loop with the
two halves separated (§4).

### 3h. Retry + lldb decisions (tabled)

| decision | verdict | rationale |
| --- | --- | --- |
| ONE retry | NOT USED | Brief permits it iff "O1/O3 fires instead of first draw" — O4 fired (not O1/O3), and first draw WAS reached; same stop-rule logic as G24 §3g |
| second shape | NOT USED | out of budget by the same stop rule (a post-loop-reaching shape is the §4 next action, not this action) |
| lldb triage | NOT USED | tombstone_19 fully classifies (signal/full 43-frame stack/thread/timing vs logcat + lambda-level death path); no open triage question needs it |

## 4. Hypothesis verdict + the ONE next action

| claim | verdict |
| --- | --- |
| The rebuilt binary is bit-identical; without the flag, O6 persists => ride-along, or scanouts write => flag path | **SPLIT: rebuild half CONFIRMED, separation half UNRESOLVED.** Rebuild bit-identical on all six signals (§2c — size/sha/BuildID/ELF/`strings`×2 exact, no STOP). Separation: O4 RETURNS at first draw (4-leg presence proof §3d: 139, dangling crasher, all-driver-compile 43-frame stack, G23r2 match) — the O6 post-loop site was never reached, so NEITHER the flag path NOR the ride-along is implicated or exonerated (§3g). Bonus: the no-flag arm completes a bidirectional A/B (same-sha binary: =1 → O4 absent, =0 → O4 present) confirming the flag's efficacy far more strongly than G24 alone; the `=0` receipt behaviorally proves the rebuild identical. Pixels UNSCORED (0 scanouts, SCORE N/A §3e); O5 unobserved (§3f). |

The ONE next action the numbers justify: **a narrower-hunk brief —
deliver ONLY `disable_sampler_feedback` (keep `feedback_render_target`
at its interface default `false`), rebuild, then ONE with-flag run on
the same dump/iterations + pixel-diff**. Rationale: it is the only
single run that both reaches post-loop (the flag suppresses O4 — proven
bidirectionally this brief) AND separates the two halves (ride-along
removed): O6 persists => the flag's full-upload path is implicated =>
scoped ASan/HWASan instrumentation on that path; scanouts write (bright
or black) => the ride-along is implicated => the narrower hunk IS the
adoption shape (attribution + adoption in one run). Queued alternative
(not this action): same-binary no-flag run + `PGS_SKIP_SAMPLER_FEEDBACK=1`
(no rebuild; reaches post-loop via the G22 skip — but ALWAYS needs a
follow-up either way, so it terminates slower). Queued behind it (not
this action): O6/O5/O3 writer-naming briefs (ASan/HWASan per G15/G16);
G18-hunk fix adoption (still queued); O1 writer naming (still open);
the Adreno filing — STILL OPEN regardless (submit needs user
identity/tracker; the A/B result does not close it).

No verdicts beyond the hypothesis. No port, no adoption, no upstream contact.

## 5. License / provenance receipts

| artifact | receipt |
| --- | --- |
| paraLLEl-GS rev | `3a66c19…` (LGPL-3.0+ per G7 §4 — cited, not re-read) |
| Granite rev | `16e7395f…` (MIT per G7 §4 — cited); G20 capture hunk compiled in (logging-only, uncommitted, SSD clone only) |
| G14 shims S1–S3 + G7/G8/G10/G11/G18/G22/G24 hunks | untouched, still uncommitted in SSD clone only (HUNK_MATCH re-verified pre-rebuild; ZERO edits this brief) |
| NDK r30 | relink + `llvm-readelf` use (Apache-2.0) |
| logcat/tombstone | run receipts of our own binary in SSD `ps2x-g25/` ONLY (not in git); no PII (`uid: 2000` shell) |
| adoption hunks | NONE — no third-party code copied into any project tree this brief |

## 6. Exact commands

Mac (`/Users/bradrichardson/dev/ssx3` unless noted;
`COPYFILE_DISABLE=1` on SSD steps; `SSD="/Volumes/Extreme SSD"`):

```text
shasum -a 256 <g24-binary> ; xxd -l 16 <g24-binary>               # §2a damage confirm (fc62d01a…, zeros)
python3 zero-fraction scan (265,840,424 B, 0 nonzero)             # §2a 100.0000%
llvm-readelf --notes <g24-binary> ; strings | grep -c ...        # §2a COFF-unknown, 0/0
python3 head-zero scan of g24-build dir (611 files, 1 hit)        # §2a scope
git -C $SSD/parallel-gs-g7 rev-parse HEAD ; status --short ; diff --stat  # §2b
git -C $SSD/parallel-gs-g7 diff gs/gs_renderer.cpp | diff local/research/G22/g22-workaround.diff -  # HUNK_MATCH
git -C $SSD/parallel-gs-g7 diff tools/gs_dump_replayer.cpp (block vs g24-plumbing.diff)  # HUNK_MATCH
rm <g24-binary> ; cmake --build <g24-build> --target parallel-gs-replayer -j2  # §2c exit 0 [1/1]
shasum -a 256 <g24-binary> (×3: post-build, pre-push, report)    # 562a0bcf… FULL-match
llvm-readelf --notes ; strings grep ×1/×2 ; xxd -l 4             # c7f68343… + ELF
du -sk <ps2x-g10..g25 + 5 build dirs> ; df -h / $SSD             # §0 (pre + post)
python3 local/research/G14/g14-diff.py $SSD/ps2x-g13 $SSD/ps2x-g25  # §3e
grep -c 7463…/c61f…/success/G24/G10/G11 <logcat> ; census <tombstone>  # §3 census
```

adb (`-s 622c49b1` throughout; `/data/local/tmp/g25/` ONLY; `mg/` never touched):

```text
shell 'ls /data/local/tmp/ ; ls -lt /data/tombstones/ | head ; df -h /data | tail -1'  # pre-check (mg/ only, _18 newest, 28G)
shell 'rm -rf /data/local/tmp/g25 && mkdir -p /data/local/tmp/g25'
push <dump> $G25DIR/g13-dump.gs ; push <rebuilt-binary> $G25DIR/parallel-gs-replayer
shell 'sha256sum g13-dump.gs parallel-gs-replayer'                   # both FULL-match host
logcat -c ; logcat -d -s Granite:V | tail -2                         # before (empty)
shell 'cd $G25DIR && date +%s; PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer $G25DIR/g13-dump.gs --iterations 2; echo RUN_EXIT=$?; date +%s'  # 139 (O4-return)
logcat -d -s Granite:V > $SSD/ps2x-g25/g25-logcat.txt                # 49 lines
shell 'ls -la $G25DIR/ ; ls -lt /data/tombstones/ | head -6'         # 0 scanouts; _19 new 13:29
pull /data/tombstones/tombstone_19 $SSD/ps2x-g25/g25-tombstone-19.txt
shell 'rm -rf /data/local/tmp/g25 && ls /data/local/tmp/'            # DEVICE_CLEAN (mg/ only)
```

## 7. Gaps (what this brief could not do)

1. O6 unattributed (flag path vs ride-along) — the no-flag run died at
   O4 before the discriminating phase (§4 action separates with a
   post-loop-reaching run).
2. Pixels remain unscored (0 scanouts) and the adoption shape undecided —
   blocked by the O4-return at first draw, three briefs running.
3. O6's heap-corruption WRITER is still unnamed (no new detection this
   brief — needs an instrumented brief once a path is implicated).
4. O5's re-fire without the flag is unobserved (no run reached teardown).
5. The feedback ride-along's pixel effect is unmeasured (no scanouts to
   compare; the G24 §2b caveat stands until a post-loop run).
6. The Adreno filing is still open and unfiled (needs user identity /
   tracker — unchanged owner; the A/B result does not close it).
7. O1 writer, G18-hunk adoption, G17 filing: unchanged / queued.
8. No lldb (decision tabled §3h); OS tombstone store otherwise untouched.
   `upstream/` + harness code untouched; no new dumps; run budget 1/2 spent
   (retry intentionally unspent — no retry condition fired).
9. Erratum: G24's report left `Time box 6 h (used ~X h)` unfilled — this
   brief fills its OWN actual time (Brief header) but cannot reconstruct
   G24's; G24's report is left untouched.

## 8. Receipt paths

- SSD receipts: `/Volumes/Extreme SSD/ps2x-g25/` (2 files: `g25-logcat.txt`
  49 lines, `g25-tombstone-19.txt` 174,169 B; 0 PPMs) +
  `parallel-gs-g24-android-build/` (REBUILT binary 265,840,424 B
  `562a0bcf…` BuildID `c7f68343…` — bit-identical to the tested binary).
- SSD receipts (read-only, 0 growth): `ps2x-g10/`-`ps2x-g24/` + G14/G18/G20/
  G22 build dirs + SSD clone (HEAD `3a66c19…`, G22 + G24 hunks uncommitted).
- Session-only: none (no `/tmp/g25-*` files were written).
- Commits: ssx3 `local/research/G25/` `[G25]` + `Orchestrated-By: Muse Code`
  trailer (NOT pushed); ps2xGS untouched (zero commits — hunk uncommitted
  per G18/G22 precedent).

TAIL-RECEIPT: G25 report ends here. Rebuild bit-identical (all six
signals exact), no-flag run returns O4 at first draw (139, dangling
crasher, 43-frame driver-compile tombstone), O6 attribution unresolved
(site never reached), flag efficacy confirmed bidirectionally, score N/A,
narrower hunk next, filing still open.
