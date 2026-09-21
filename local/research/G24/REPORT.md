# G24 report — `debug_mode` plumbing: unconditional delivery + rebuild + flag re-run (Odin)

Brief: G24 (this turn) — executes G23 §4's ONE next action ONLY: (1) move
`iface.set_debug_mode(debug_mode)` out of the `if (use_rdoc)` gate in
`tools/gs_dump_replayer.cpp` (ONE hunk, unconditional like the sibling
replayers, at most one LOGI receipt line riding along); (2) rebuild the
replayer in a NEW SSD build dir; (3) ONE bounded on-device run of the SAME
dump/iterations with the flag SET + `g14-diff.py` pixel-diff vs G13
oracles. Tables + hypothesis + next-action recommendation, no verdicts
beyond the hypothesis. Time box 6 h (used ~X h). Read first per the brief:
`local/research/G23/REPORT.md` (all of it). No upstream contact of any
kind (standing no-upstream order — local hunk only, filing stays a local
doc; fork-and-fix standing order covers this app-side hunk).

Machine: same as G8-G23 (Apple M4, macOS — no new installs).
Device: Odin3 (`622c49b1`, Android 15), transient dir `/data/local/tmp/g24/`
ONLY; removed at end (`mg/` only).

Headline result: the plumbing WORKS and the wall moved exactly one step
forward. (1) Delivery is PROVEN: the new `G24:` receipt line reads
`disable_sampler_feedback=1, use_rdoc=0`, and O4 is ABSENT with proof
(exit 134 not 139, crasher never logged, 7/7 + 1/1 compiles `success:
yes`, zero driver-compile frames, full 18-frame / 2-pass loop completed
through `Total time per VBlank`). (2) A NEW wall fires inside the FIRST
scanout readback (tabled O6): Scudo `corrupted chunk header` SIGABRT in
`save_scanout_ppm → wait_idle → DescriptorSetAllocator::clear →
vkDestroyDescriptorPool`, 16 ms after the last logcat line, pre-`Done!`
— same detector as the O3/O5 family, writer unnamed, site+phase matching
no existing number. (3) Score: oracles ALL OK, device PPMs 0, SCORE N/A
— the bright-vs-black adoption read is unmade for the second brief in a
row, now blocked by O6 instead of O4. (4) O5 did NOT re-fire (teardown
never reached). One run spent; retry not used (no O1/O3).

## 0. Byte caps (declared at session start) vs actuals

| class | cap | actual |
| --- | --- | --- |
| NEW SSD build dir `parallel-gs-g24-android-build` | 6 GB | 4,482,048 KiB (== G18/G20/G22 dirs exactly) PASS |
| NEW SSD `ps2x-g24/` (retrieval: logcat + tombstone_18, 0 PPMs) | 50 MB | ~330 KB apparent; 5,120 KiB allocated (ExFAT clusters) PASS |
| SSD `ps2x-g10..g23` + G14/G18/G20/G22 build dirs (read-only) | 0 growth | all == pre-run snapshot exactly (g10 43008, g14 7168, g18 5120, g19 5120, g20 11264, g21 15360, g22 25600, g23 9216, g14-build 4480000, g18/g20/g22-build 4482048 KiB) PASS |
| SSD clone (source) | ONE hunk only | `tools/gs_dump_replayer.cpp` ONE new `@@` block (+5/−1); all other files == G23 §2a; hunk UNCOMMITTED PASS |
| internal volume (`/`) | <=1 GB delta, no clones/builds | 13 Gi avail at report time; no residue outside repo except `/tmp/g24-*` ~KB text PASS |
| SSD volume | — | 232 -> 227 Gi avail (build dir + receipts; remainder other-lane) |
| device | `/data/local/tmp/g24/` ONLY | pushed 2 files, pulled 2, dir removed after (`mg/` only) PASS |
| network | none used | no clones, no installs PASS |
| host build | `-j2` | configure exit 0 + full build exit 0 + 1-TU recompile exit 0 PASS |
| committed to git | text only | REPORT.md + `g24-plumbing.diff`; no binaries |

No P-lane lease, no bytesize/WSL. `COPYFILE_DISABLE=1` on all SSD steps.
No code copied into any project tree.

## 1. Experiment contract

| slot | content |
| --- | --- |
| hypothesis | Delivering the parsed `debug_mode` unconditionally lets `--disable-sampler-feedback` take effect (full-upload fallback, no `sampler_feedback` dispatch at all): O4 is absent AND the run renders correct (bright) pixels on the same dump/iterations; O5 is expected to re-fire harmlessly post-`Done!` either way |
| observable signal | hunk diff (one block) + build exit/sha/build-id + ONE bounded flag run (exit/wall/fate + `G24:` delivery receipt + knob/flag receipts + crasher absence/presence + tombstone triage if any) + scanouts pulled and scored (`g14-diff.py` exact/le2/le32 + means) + O5 re-fire table |
| alternatives | (a) no-O4 + correct pixels => adoption shape named; (b) O4 persists => plumbing ineffective, mechanism briefed; (c) new wall => its exact brief; (d) O1/O3 instead of first draw => lottery note + ONE retry |
| stop condition | ONE hunk max (the move + at most one LOGI line); TWO bounded device runs max (flag run + one retry iff O1/O3 fires instead of first draw); no tuning loop, no second shape, no new dumps; no lldb unless the tombstone cannot triage |
| outcome → next action | numbers name the next single experiment (§4) |

Outcome: split — delivery half CONFIRMED (receipt + O4 absent + full
loop), pixels half UNSCORED (0 scanouts, new pre-write wall O6),
alternative (c). No tuning loop was entered: one hunk, one build, one
device run. Retry not used (O1/O3 never fired); lldb not used (tombstone
classifies; tabled §3g).

## 2. Task 1 — plumbing hunk + rebuild (no device until §3)

### 2a. Pin verification (pre-work — G23 §2a reproduced, ZERO edits after)

| item | observed |
| --- | --- |
| SSD clone HEAD | `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd` (== pin) |
| tree status (pre-hunk) | `M CMakeLists.txt` + `m Granite` + `M gs/gs_interface.cpp` + `M gs/gs_renderer.cpp` + `M tools/CMakeLists.txt` + `M tools/gs_dump_replayer.cpp` + ExFAT `._` sidecars — G23 §2a exactly |
| G22 hunk presence | `git diff gs/gs_renderer.cpp` byte-identical to `g22-workaround.diff` (`diff` exit 0, HUNK_MATCH); `diff --stat`: `gs_renderer.cpp` +15 only |
| Granite diff (pre-hunk) | `platforms/CMakeLists.txt` + G7 (`util/timer.cpp`) + G20 (`command_buffer.cpp` +18) + G18 (`shader.cpp`) — G22 §2a exactly, untouched |
| G22 binary (reference) | 265,840,344 B, sha `5e1f7827…` prefix-match (zero-fill watch: intact; NOT the tested binary) |
| rich dump (host) | 11,537,377 B, sha `154d9d8577a210fb794b29a048ee2cf08053f87fe220bb2bf975933a02ad7e32` full-match |
| G14/G18/G20/G22 dirs 0-growth | pre-run `du -sk` == G23 §0 exactly (g10 43008, g14 7168, g18 5120, g19 5120, g20 11264, g21 15360, g22 25600, g23 9216, g14-build 4480000, g18/g20/g22-build 4482048 KiB); post-run re-verified §0 |
| gate (worktree) | the ONLY `set_debug_mode` call in this tool (`:101`) sits inside `if (use_rdoc)` (`:98-103`) — brief's refs match |
| sibling contrast | `gs_repro_replayer.cpp:165` + `gs_stream_replayer.cpp:185` call `set_debug_mode` UNCONDITIONALLY (stream `:235` is a second call inside its capture-frame block — noted, not the precedent); `gs_interface.cpp:4478` setter is a plain struct copy + `set_enable_timestamps(mode.timestamps)` |
| NDK / cmake | r30 (`/opt/homebrew/share/android-ndk`, `Pkg.ReleaseName = r30`); cmake+ninja `/opt/homebrew/bin/` |
| device (read-only pre-check) | `622c49b1`, Odin3; `/data/local/tmp/` == `mg/` only; newest tombstone `_17` (G23's O4); `/data` 29 G free |
| `g14-diff.py` + oracles | tool present; `ps2x-g13/` holds dump + 8 vsync PPMs (688,143 B each) |

### 2b. Hunk design (ONE block in `tools/gs_dump_replayer.cpp`, +5/−1)

The hunk (also saved as `g24-plumbing.diff` beside this report; the file's
other `@@` blocks are the pre-existing G8/G10 hunks, untouched):

```diff
@@ -93,9 +96,12 @@ int main(int argc, char **argv)
 		return EXIT_FAILURE;

 	bool use_rdoc = Device::init_renderdoc_capture();
+	// G24 local plumbing (not upstream): deliver debug_mode unconditionally
+	// (sibling replayers do the same); the rdoc gate made the flag a no-op.
+	iface.set_debug_mode(debug_mode);
+	LOGI("G24: debug_mode delivered (disable_sampler_feedback=%d, use_rdoc=%d).\n", int(debug_mode.disable_sampler_feedback), int(use_rdoc));
 	if (use_rdoc)
 	{
-		iface.set_debug_mode(debug_mode);
 		device.begin_renderdoc_capture();
 	}
```

LOGI choice (tabled): INCLUDED (one physical line). It proves DELIVERY
independently of the behavioral discriminators: the O4-absent legs and the
pixel score each admit alternative explanations (lottery, shader-variant
effects), but `disable_sampler_feedback=1` on the log line names the
delivered struct value directly. Cost: one log line per process (same
`LOGI` already used 8× in this TU — no new includes).

No-new-hazard reasoning (tabled — the honest version, ride-along named):

| # | fact |
| --- | --- |
| 1 | The setter is a plain struct copy + `set_enable_timestamps(false)` on our path (timestamps unset) — no new threads, no new host writes, no lifecycle change |
| 2 | Without the flag, delivered values equal the interface default except `feedback_render_target` (None/False/False/False otherwise — no `--strided`/`--full` in our run) |
| 3 | The RIDE-ALONG: `feedback_render_target` flips false→true vs current on-device behavior (the tool stages `=true` at `:43`, then the gate dropped it). Effect: ubershader `[1][*]` variants (extra debug-output writes to SEPARATE storage images; main color path unchanged in source) + debug-image alloc/clear/bind + image-handle recycling skipped (memory only) + debug markers iff consumed |
| 4 | That configuration is exactly what upstream runs on every RenderDoc-present host (the common dev path) and what the tool author staged — the gate, not the value, is the anomaly; sibling `gs_stream_replayer.cpp:231-235` likewise delivers `feedback_render_target=true` |
| 5 | Discriminator impact: O4-absent legs are UNAFFECTED (O4 is the `sampler_feedback` compute compile, independent of ubershader variants); bright-vs-black stays a clean coarse read (feedback variants cannot blacken output); only an EXACT oracle match would carry the ride-along caveat — tabled at scoring time |
| 6 | Rejected alternative: deliver ONLY `disable_sampler_feedback` (second struct / field surgery) — diverges from sibling shape + author intent for zero discriminator gain, and spends hunk budget on cleverness instead of the prescribed move |

Post-hunk tree status: G23 §2a files + `tools/gs_dump_replayer.cpp`
108→113 changed lines (the ONE new `@@` block above); nothing else.
Hunk stays UNCOMMITTED in the SSD clone (G18/G22 precedent).

### 2c. Build record (NEW SSD dir — G14/G18/G20/G22 dirs untouched)

| item | observed |
| --- | --- |
| configure | G14 recipe verbatim into `parallel-gs-g24-android-build` → exit 0, `Configuring done (18.1s)`, `Generating done (8.4s)`, `Processor: aarch64` |
| build | `cmake --build … --target parallel-gs-replayer -j2` → exit 0 (`[458/458]`, re-verified `ninja: no work to do`) |
| warnings | hunk TU (`gs_dump_replayer.cpp.o`) recompiled solo to capture output => exit 0, ONE warning: pre-existing `-Wshadow` at `gs_dump_parser.hpp:49` (same class as G22; zero warnings point at the hunk lines) — full log `g24-tu-rebuild.log` beside this report |
| binary | `tools/parallel-gs-replayer`, 265,840,424 B (+80 vs G22 — hunk + strings), valid ELF (`7f45 4c46`) |
| sha (build-time re-sha #1) | `562a0bcf14e621ddd21b22d318197a26338a562446e47f9826f67a12fffc8f4a` (identical before AND after the TU relink — byte-deterministic link; pre-push + report-time re-shas §3/§0) |
| build-id | `c7f68343e5a61c089593374cecc5896441798fe9` (NDK `llvm-readelf --notes`; distinct from G22's `c2dc902b…`) |
| plumbing presence | `strings` grep: `G24: debug_mode delivered` ×1, `disable-sampler-feedback` ×2 |
| build dir | 4,482,048 KiB (cap 6 GB ✓; == G18/G20/G22 dirs exactly); G14/G18/G20/G22 dirs == pre-run exactly (0 growth ✓) |

## 3. Task 2 — ONE bounded flag run + score (Odin)

### 3a. Knob matrix (NO deviation from G23 run 2 — tabled per the brief)

| knob / flag | setting | rationale |
| --- | --- | --- |
| `--disable-sampler-feedback` | SET (appended after `--iterations 2`) | the tested shape, now actually delivered |
| `PGS_SKIP_SAMPLER_FEEDBACK` | UNSET | test the upstream shape independently — no G22 skip to mask or confound it |
| `PGS_SKIP_COMPILATION_TASKS=1` | KEPT | G22's tabled choice: keeps the async path from compiling `sampler_feedback` independently of the flag gate and confounding the experiment |

Predicted discriminators: `G24: …disable_sampler_feedback=1` receipt +
O4-absent + bright pixels => plumbing works; O4-present (crasher pre-create
+ 139) => plumbing ineffective; `G22: skipping` absent either way (knob
unset); `Skipping precompilation` present (async knob effective); O5
expected post-`Done!` either way.

### 3b. Run table (ONE run — retry not used, §3f)

| item | observed |
| --- | --- |
| staging | `/data/local/tmp/g24/` ONLY; dump + G24 binary pushed; on-device shas FULL-match host (`154d9d85…` / `562a0bcf…`); logcat cleared, Granite empty before |
| command | `PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer /data/local/tmp/g24/g13-dump.gs --iterations 2 --disable-sampler-feedback` |
| exit / wall | **134** (SIGABRT — NOT 139) / ~1 s wall (`date` 1790009398→1790009399; logcat 12:49:59.047→12:49:59.569; tombstone `Process uptime: 2s`) |
| DELIVERY receipt | line 29 `G24: debug_mode delivered (disable_sampler_feedback=1, use_rdoc=0).` (×1) — the flag value reached the interface; `use_rdoc=0` confirms the old gate would have dropped it |
| knob receipts | line 25 `Skipping precompilation…` (×1, async knob effective); line 28 `Failed to load RenderDoc` (`use_rdoc=false` receipt, as in G23); 0 `G22: skipping` (knob unset, as designed) |
| logcat | 1793 lines: init + ext list + 18 `Running frame` + 16 G10 pass lines (pass 0+1 × vsync #0–#7 — BOTH iterations complete) + 8 compute pre-creates + 7 compute `success: yes` + 1 graphics `success: yes` + `Total time per VBlank: 2.306 ms` as the LAST line; 0 `success: no`; 0 `wrote … scanout`; 0 `Done!` |
| crasher absence | `7463dfd379df2855` / `c61f1a8116a82d4b` refs in logcat: **0** (the crashing compile never happens) |
| unpaired-compile note | compute pre-create `959d84147e61df64` (:193) has no paired Stalled post — NOT a death-during-compile: ~1600 healthy log lines follow it (both passes complete, Total-time printed), and the same pipeline hash appears in G22's log (benign async-completed compile); the 8th Stalled line is a graphics pipeline (`e5825d…`, success: yes — graphics gets no G20 pre-create by design) |
| fate | NOT O1/O2/O3 (full loop completed); NOT O4 (proof §3d) → NEW signature, tabled **O6** (§3c): post-loop, pre-first-write Scudo abort in scanout readback |
| device outputs | 0 scanouts; tombstone_18 written 12:49 (pulled, §3c); device dir removed after (`mg/` only ✓) |

### 3c. Tombstone_18 triage (pid 860 — NEW wall, tabled O6)

| slot | fact |
| --- | --- |
| signal | SIGABRT (signal 6, SI_QUEUE), Scudo abort message: `corrupted chunk header at address 0x2000079eb4d2130` — same detector/message as O5 (and G23-run1's O3-site abort) |
| stack | `main ← save_scanout_ppm (#13, `main::$_10`) ← Device::wait_idle ← wait_idle_nolock ← DescriptorSetAllocator::clear (#10) ← adreno vkDestroyDescriptorPool (#09, BuildId `d05dded9…`) + 2 anon adreno ← Scudo deallocate → reportHeaderCorruption → abort` (16 frames, main thread pid == tid; #00–#05 libc, #06–#09 adreno, #10–#14 replayer BuildId `c7f68343…`, #15 `__libc_init`) |
| timing | post-loop, pre-first-write — 12:49:59.585 = 16 ms after the last logcat line (Total-time, .569); the FIRST `save_scanout_ppm` call died inside `wait_idle` (:150) before its first LOGI (0 `wrote`, 0 `no image`, series proven non-empty by the absence of the `no iterate-true` LOGE) |
| classification | O6 (new wall): site (`DescriptorSetAllocator::clear ← wait_idle` in scanout readback) + phase (post-loop, pre-`Done!`) match NO existing number — not O3 (init `trim`), not O4 (first-draw driver compile), not O5 (post-`Done!` `Device` teardown). Detector matches the O3/O5 Scudo family; writer UNNAMED (detection-at-free inside a driver `free`) |
| flag involvement | the ONLY configuration delta vs G22's 10 successful scanout writes is this hunk's delivered state (flag path + `feedback_render_target` ride-along §2b) — one of the two moved the corruption detection earlier (or introduced a new writer); the single run cannot separate them (§4 action does) |
| binary identity | tombstone BuildId `c7f68343…` == G24 binary => the tested binary is proven |
| census | `libllvm-qgl`: mapped-not-executing only (no compile death); `7463…`/`c61f…`: 0 in logcat and tombstone; `vkCreateComputePipelines`/`kick_compilation`/`__async_func`: 0 in the crashing stack |

### 3d. O4-absent proof (four independent legs, G22 §3b shape)

| # | leg | evidence |
| --- | --- | --- |
| 1 | exit/signal differs | 134/SIGABRT vs O4's 139/SIGSEGV; full loop completed (Total-time printed) vs O4's first-draw death |
| 2 | crashing input never exists | crasher pipeline/shader hashes logged 0×; 7/7 compute compiles with Stalled posts each `success: yes`, 0 `success: no` (the one unpaired pre-create is a benign async completion, §3b note) |
| 3 | death stack has zero driver-compile frames | tombstone_18: Scudo + adreno `vkDestroyDescriptorPool` + Granite descriptor cleanup + `main`; no `dispatch_texture_analysis`, no `libllvm-qgl` execution, no pipeline-build frames |
| 4 | death is post-loop | tombstone 16 ms after Total-time; crashing thread is main in scanout readback, binary BuildId `c7f68343…` == G24 binary |

O4 is absent. Delivery is proven independently (§3b receipt), so this is
the flag working, not the lottery.

### 3e. Score vs G13 oracles (`g14-diff.py`, zero new tooling)

`g14-diff.py ps2x-g13 ps2x-g24` (tool exit 0): oracles **ALL OK**
(8/8 pixel-shas); device PPMs: **0**; `SCORE: N/A - 0 device scanouts`.
(The tool's parenthetical cites its own G14 run; the G24 reason is tabled:
the full replay loop completed but death came inside the FIRST scanout
readback's `wait_idle`, before any PPM write.) No means/PSNR exist to
table — the bright-vs-black adoption read is UNMADE for the second brief
in a row, now blocked by O6 instead of O4.

### 3f. O5 re-fire table (expected post-`Done!` either way — observed: no)

| run | reached teardown? | O5 fired? | note |
| --- | --- | --- | --- |
| run 1 (O6) | NO (died pre-first-write, pre-`Done!`) | NO | Scudo detector fired, but site/phase are O6's (§3c), not O5's post-`Done!` `Device` teardown |

O5 status: unchanged from G22 (named, writer unnamed, scanouts-unaffected
when reached). This brief neither confirms nor denies its re-fire under
the flag — no run reached teardown. The heap-corruption family now has
THREE detection sites (O3-init, O5-post-`Done!`, O6-pre-write), all writer-
unnamed, all sharing the `corrupted chunk header` detector.

### 3g. Retry + lldb decisions (tabled)

| decision | verdict | rationale |
| --- | --- | --- |
| ONE retry | NOT USED | Brief permits it iff "O1/O3 fires instead of first draw" — first draw was reached and the full loop completed; O6 is a post-loop wall, not a retry condition |
| second shape / separation run | NOT USED | out of budget by the same stop rule (it is the §4 next action, not this action) |
| lldb triage | NOT USED | tombstone_18 fully classifies (signal/message/full stack/thread/timing vs logcat + lambda-level death site); the open question (O6's WRITER) needs an instrumented brief, not post-mortem lldb |

## 4. Hypothesis verdict + the ONE next action

| claim | verdict |
| --- | --- |
| Delivering `debug_mode` unconditionally lets `--disable-sampler-feedback` take effect: O4 absent AND correct (bright) pixels on the same dump/iterations; O5 re-fires harmlessly post-`Done!` either way | **SPLIT: delivery half CONFIRMED, pixels half UNSCORED, O5 unobserved.** Delivery proven (`G24: …disable_sampler_feedback=1` receipt §3b) and O4 ABSENT (4-leg proof §3d: 134, crasher 0×, 8/8 Stalled posts `success: yes` — 7 compute + 1 graphics — zero driver-compile frames, full loop through Total-time). Pixels UNSCORABLE (0 scanouts, SCORE N/A §3e) — blocked by the NEW pre-write wall O6 (post-loop Scudo abort in first scanout readback §3c), not by O4. O5 did not re-fire (no run reached teardown — §3f). The wall moved exactly one step forward (G23: first-draw death → G24: post-loop death). |

The ONE next action the numbers justify: **a separation brief — run the
SAME G24 binary WITHOUT `--disable-sampler-feedback` (NO rebuild) +
pixel-diff — it attributes O6 to the flag path vs the ride-along and
decides the adoption shape**. Rationale: the run cannot separate the two
halves of the delivered state (§2b #3: flag path vs
`feedback_render_target` ride-along) — one of them moved the corruption
detection earlier (or introduced a new writer) relative to G22's 10 clean
scanout writes. Ride-along-only discriminators: O6 persists without the
flag => the feedback variants/debug images are implicated (narrower hunk:
deliver ONLY the flag) => then an instrumented (ASan/HWASan) writer-naming
brief; scanouts write (bright or black) => the flag's full-upload path is
implicated => same instrumentation, scoped to that path, plus the
bright-vs-black read unblocked. Queued behind it (not this action): O6/O5/
O3 writer-naming briefs (ASan/HWASan per G15/G16); G18-hunk fix adoption
(still queued); O1 writer naming (still open); the Adreno filing — STILL
OPEN regardless (submit needs user identity/tracker; the plumbing result
does not close it).

No verdicts beyond the hypothesis. No port, no adoption, no upstream contact.

## 5. License / provenance receipts

| artifact | receipt |
| --- | --- |
| paraLLEl-GS rev | `3a66c19…` (LGPL-3.0+ per G7 §4 — cited, not re-read) |
| Granite rev | `16e7395f…` (MIT per G7 §4 — cited); G20 capture hunk compiled in (logging-only, uncommitted, SSD clone only) |
| G14 shims S1–S3 + G7/G8/G10/G11/G18/G22 hunks | untouched, still uncommitted in SSD clone only (HUNK_MATCH re-verified pre-hunk; the G24 hunk is the sole addition, uncommitted) |
| G24 plumbing hunk | local-only, uncommitted in SSD clone; diff text committed beside this report (`g24-plumbing.diff`) |
| NDK r30 | build + `llvm-readelf` use (Apache-2.0) |
| logcat/tombstone | run receipts of our own binary in SSD `ps2x-g24/` ONLY (not in git); no PII (`uid: 2000` shell) |
| adoption hunks | NONE — no third-party code copied into any project tree this brief |

## 6. Exact commands

Mac (`/Users/bradrichardson/dev/ssx3` unless noted;
`COPYFILE_DISABLE=1` on SSD steps; `SSD="/Volumes/Extreme SSD"`):

```text
git -C $SSD/parallel-gs-g7 rev-parse HEAD ; status --short ; diff --stat  # §2a
git -C $SSD/parallel-gs-g7 diff gs/gs_renderer.cpp | diff local/research/G22/g22-workaround.diff -  # HUNK_MATCH
git -C $SSD/parallel-gs-g7/Granite diff --stat                       # == G22 §2a
grep -n set_debug_mode $SSD/parallel-gs-g7/tools/*.cpp                # §2a gate + siblings
grep -n "feedback_color\|feedback_depth" $SSD/parallel-gs-g7/gs/*.*   # §2b ride-along
# (write the ONE hunk at gs_dump_replayer.cpp:98-103; block > /tmp/g24-plumbing.diff)
cmake -S <clone> -B $SSD/parallel-gs-g24-android-build -G Ninja -DCMAKE_TOOLCHAIN_FILE=$NDK/build/cmake/android.toolchain.cmake -DANDROID_ABI=arm64-v8a -DANDROID_PLATFORM=android-35  # §2c exit 0
cmake --build <g24-build> --target parallel-gs-replayer -j2          # §2c exit 0 [458/458]
rm <g24-build>/tools/.../gs_dump_replayer.cpp.o ; cmake --build ...  # TU recompile exit 0, 1 pre-existing warning
shasum -a 256 <g24-binary> ; llvm-readelf --notes <g24-binary>       # 562a0bcf… + c7f68343… (×3: build, pre-push, report)
strings <g24-binary> | grep -c 'G24: debug_mode delivered'           # 1
xxd -l 4 <g24-binary>                                                 # 7f45 4c46
shasum -a 256 $SSD/ps2x-g13/g13-dump.gs                               # 154d9d85…
du -sk <ps2x-g10..g24 + 5 build dirs> ; df -h / $SSD                 # §0 (pre + post)
python3 local/research/G14/g14-diff.py $SSD/ps2x-g13 $SSD/ps2x-g24    # §3e
grep -c 7463…/c61f…/success/no-image <logcat/tombstone> ; pre/post pairing diff  # §3 census
grep -c 959d84147e61df64 $SSD/ps2x-g22/g22-logcat.txt                 # 1 (benign, §3b)
```

adb (`-s 622c49b1` throughout; `/data/local/tmp/g24/` ONLY; `mg/` never touched):

```text
shell 'ls /data/local/tmp/ ; ls -lt /data/tombstones/ | head ; df -h /data | tail -1'  # pre-check (mg/ only, _17 newest, 29G)
shell 'rm -rf /data/local/tmp/g24 && mkdir -p /data/local/tmp/g24'
push <dump> $G24DIR/g13-dump.gs ; push <g24-binary> $G24DIR/parallel-gs-replayer
shell 'sha256sum g13-dump.gs parallel-gs-replayer'                   # both FULL-match host
logcat -c ; logcat -d -s Granite:V | tail -2                         # before (empty)
shell 'cd $G24DIR && date +%s; PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer $G24DIR/g13-dump.gs --iterations 2 --disable-sampler-feedback; echo RUN_EXIT=$?; date +%s'  # 134 (O6)
logcat -d -s Granite:V > $SSD/ps2x-g24/g24-logcat.txt                # 1793 lines
shell 'ls -la $G24DIR/ ; ls -lt /data/tombstones/ | head -6'         # 0 scanouts; _18 new 12:49
pull /data/tombstones/tombstone_18 $SSD/ps2x-g24/g24-tombstone-18.txt
shell 'rm -rf /data/local/tmp/g24 && ls /data/local/tmp/'            # DEVICE_CLEAN (mg/ only)
```

## 7. Gaps (what this brief could not do)

1. Pixels remain unscored (0 scanouts) and the adoption shape undecided —
   blocked by O6, one step past O4 (§4 action separates flag vs ride-along).
2. O6's heap-corruption WRITER is unnamed (detection-at-free inside a driver
   `free`; the O3/O5 family now has three detection sites — needs an
   instrumented brief).
3. O5's re-fire under the flag is unobserved (no run reached teardown).
4. The feedback ride-along's pixel effect is unmeasured (no scanouts to
   compare; the §2b caveat stands until the separation run).
5. The Adreno filing is still open and unfiled (needs user identity /
   tracker — unchanged owner; the plumbing result does not close it).
6. O1 writer, G18-hunk adoption, G17 filing: unchanged / queued.
7. No lldb (decision tabled §3g); OS tombstone store otherwise untouched.
   `upstream/` + harness code untouched; no new dumps; run budget 1/2 spent
   (retry intentionally unspent — no retry condition fired).

## 8. Receipt paths

- SSD receipts: `/Volumes/Extreme SSD/ps2x-g24/` (2 files: `g24-logcat.txt`
  1793 lines, `g24-tombstone-18.txt` 171,439 B; 0 PPMs) +
  `parallel-gs-g24-android-build/` (binary 265,840,424 B `562a0bcf…`
  BuildID `c7f68343…`).
- SSD receipts (read-only, 0 growth): `ps2x-g10/`-`ps2x-g23/` + G14/G18/G20/
  G22 build dirs + SSD clone (HEAD `3a66c19…`, G22 + G24 hunks uncommitted).
- Session-only: `/tmp/g24-*` (hunk diff, TU rebuild log, pairing lists).
- Commits: ssx3 `local/research/G24/` `[G24]` + `Orchestrated-By: Muse Code`
  trailer (NOT pushed); ps2xGS untouched (zero commits — hunk uncommitted
  per G18/G22 precedent).

TAIL-RECEIPT: G24 report ends here. Plumbing works (delivery receipted,
O4 absent, full loop), new pre-write wall O6 named (0 scanouts, SCORE
N/A), O5 never reached, separation brief next, filing still open.
