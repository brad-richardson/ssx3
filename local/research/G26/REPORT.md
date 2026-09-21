# G26 report — Narrower hunk: ONLY `disable_sampler_feedback` delivered, O6 PERSISTS at the same site (flag path implicated, Odin)

Brief: G26 (this turn) — executes G25 §4's narrower hunk ONLY: (1) deliver
ONLY `disable_sampler_feedback` (keep `feedback_render_target` at its
interface default `false` — the G24 move MINUS the ride-along), rebuild in
a NEW SSD build dir; (2) ONE bounded WITH-FLAG run (same dump/iterations,
flag SET) + `g14-diff.py` pixel-diff vs G13 oracles. Tables + hypothesis +
next-action recommendation, no verdicts beyond the hypothesis. Time box
6 h (used ~0.15 h — measured wall 14:27:59→14:36 EDT). Read first per the
brief: `local/research/G25/REPORT.md` (all of it) + G24 §2b (the
`feedback_render_target` ride-along) + §3c (O6). No upstream contact of any
kind (standing no-upstream order — local hunks only, filing stays local).

Machine: same as G8-G25 (Apple M4, macOS — no new installs).
Device: Odin3 (`622c49b1`, Android 15), transient dir `/data/local/tmp/g26/`
ONLY; removed at end (`mg/` only).

Headline result: the separation TERMINATES. (1) The narrower hunk delivers
exactly one variable vs G24 (`feedback_render_target` true→false, all else
identical — proven by the `G26:` receipt `=1, =0, =0` AND behaviorally by
the G10 `img=` counter collapsing to 0 on all 8 warm-pass lines while every
other counter is line-identical to G24). (2) O6 PERSISTS at the SAME Scudo
site: exit 134, `corrupted chunk header`, 16-frame tombstone through
`save_scanout_ppm → wait_idle → DescriptorSetAllocator::clear →
vkDestroyDescriptorPool`, 16 ms after Total-time — the ride-along is
EXONERATED, the FLAG's full-upload path is IMPLICATED. (3) O4 stays absent
(4-leg proof, same shape as G24). Score N/A for the fourth brief in a row
(0 scanouts, blocked by O6). One run spent; retry not used (no O1/O3).

## 0. Byte caps (declared at session start) vs actuals

| class | cap | actual |
| --- | --- | --- |
| NEW SSD build dir `parallel-gs-g26-android-build` | 6 GB | 4,482,048 KiB (== G18/G20/G22/G24 dirs exactly) PASS |
| NEW SSD `ps2x-g26/` (retrieval: logcat + tombstone_20, 0 PPMs) | 50 MB | ~329 KB apparent; 5,120 KiB allocated (ExFAT clusters) PASS |
| SSD `ps2x-g10..g25` + G14/G18/G20/G22/G24 build dirs (read-only) | 0 growth | all == pre-run snapshot exactly (g10 43008, g14 7168, g18 5120, g19 5120, g20 11264, g21 15360, g22 25600, g23 9216, g24 5120, g25 5120, g14-build 4480000, g18/g20/g22/g24-build 4482048 KiB) PASS |
| SSD clone (source) | ONE hunk only | `tools/gs_dump_replayer.cpp` ONE `@@` block REPLACED (+8/−1 vs HEAD, net +3 vs G24's block); all other files == G25 §2b; hunk UNCOMMITTED PASS |
| internal volume (`/`) | <=1 GB delta, no clones/builds | 11 Gi avail before → 12 Gi after (other-lane delta); no residue outside repo PASS |
| SSD volume | — | 220 Gi avail before → 216 Gi after (new build dir + receipts; remainder other-lane) |
| device | `/data/local/tmp/g26/` ONLY | pushed 2 files, pulled 2, dir removed after (`mg/` only) PASS |
| network | none used | no clones, no installs PASS |
| host build | ONE build, `-j2`, new dir | configure exit 0 + full build exit 0 `[458/458]`, 1 pre-existing warning PASS |
| committed to git | text only | REPORT.md + `g26-narrowing.diff`; no binaries |

No P-lane lease, no bytesize/WSL. `COPYFILE_DISABLE=1` on all SSD steps.
No code copied into any project tree.

## 1. Experiment contract

| slot | content |
| --- | --- |
| hypothesis | The narrower hunk (ONLY `disable_sampler_feedback` delivered, `feedback_render_target=false`) both reaches post-loop (the flag suppresses O4 — proven bidirectionally in G25) AND separates the two halves: O6 persists at the same Scudo site => the FLAG's full-upload path is implicated (next: scoped ASan/HWASan instrumentation on that path); scanouts write (bright or black) => the RIDE-ALONG is implicated (next: this narrower hunk IS the adoption shape) |
| observable signal | hunk diff (one block) + build exit/sha/build-id + verify-then-push chain (4+ matching re-shas incl. on-device) + ONE bounded flag run (exit/wall/fate + `G26:` receipt + knob receipts + crasher absence/presence + tombstone triage if any) + scanouts pulled and scored (`g14-diff.py`) + O4 legs + O5 table |
| alternatives | (a) O6 persists => flag path; (b) scanouts write => ride-along; (c) O4 returns despite the flag => flag efficacy re-opened; (d) O1/O3 instead of first draw => lottery note + ONE retry |
| stop condition | ONE hunk max (the narrowing + at most one LOGI line); ONE build (new dir); TWO bounded device runs max (flag run + one retry iff O1/O3 fires instead of first draw); no tuning loop, no second shape, no new dumps; no lldb unless the tombstone cannot triage |
| outcome → next action | numbers name the next single experiment (§4) |

Outcome: alternative (a) — O6 PERSISTS at the same site with the ride-along
removed. No tuning loop was entered: one hunk, one build, one device run.
Retry not used (O1/O3 never fired); lldb not used (tombstone classifies;
tabled §3h).

## 2. Task 1 — narrower hunk + rebuild + verify-then-push (no run until §3)

### 2a. Pin verification (pre-work — G25 §2b reproduced, ZERO edits after)

| item | observed |
| --- | --- |
| SSD clone HEAD | `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd` (== pin) |
| tree status (pre-hunk) | `M CMakeLists.txt` + `m Granite` + `M gs/gs_interface.cpp` + `M gs/gs_renderer.cpp` + `M tools/CMakeLists.txt` + `M tools/gs_dump_replayer.cpp` + ExFAT `._` sidecars — G25 §2b exactly |
| G22 hunk | `git diff gs/gs_renderer.cpp` byte-identical to `g22-workaround.diff` (HUNK_MATCH) |
| G24 hunk | worktree `@@ -93,9 +96,12 @@` block byte-identical to committed `g24-plumbing.diff` (HUNK_MATCH — verified BEFORE superseding); other `@@` blocks are the pre-existing G8/G10 hunks, untouched; hunk UNCOMMITTED |
| G24 binary (4th zero-damage recurrence) | 265,840,424 B, mtime frozen 13:28 (G25's rebuild), sha `fc62d01a…` (zeros), magic `0000` — destroyed AFTER G25's report-time intact read, as the brief states; tabled, not rebuilt (superseded binary, out of scope) |
| G22 binary (reference) | 265,840,344 B, sha `5e1f7827…` full-match (zero-fill watch: intact; NOT the tested binary) |
| rich dump (host) | 11,537,377 B, sha `154d9d85…d7e32` full-match |
| dirs 0-growth | pre-run `du -sk` == G25 §0 exactly (see §0); post-run re-verified §0 |
| recipe | NDK r30 (`Pkg.ReleaseName = r30`); cmake 4.4.3 + ninja (same recipe/NKT) |
| device (read-only pre-check) | `622c49b1`, Odin3; `/data/local/tmp/` == `mg/` only; newest tombstone `_19` (G25's O4, 13:29); `/data` 28 G free |
| `g14-diff.py` + oracles | tool present; `ps2x-g13/` holds dump + 8 vsync PPMs |

### 2b. Hunk design (ONE block REPLACED in `tools/gs_dump_replayer.cpp`, +8/−1 vs HEAD)

Supersede choice (tabled per the brief): REPLACE — the G24 `@@` block is
edited in place into the G26 shape, so the worktree holds ONE tested shape
only. The G24 diff text survives committed beside the G24 report as history;
no G24-shaped code remains in the tree. Net vs G24's block: +3 lines
(+2 comment, +1 surgery; LOGI line swapped, `set_debug_mode` + rdoc lines
unchanged).

The hunk (also saved as `g26-narrowing.diff` beside this report; the file's
other `@@` blocks are the pre-existing G8/G10 hunks, untouched):

```diff
@@ -93,9 +96,15 @@ int main(int argc, char **argv)
 		return EXIT_FAILURE;

 	bool use_rdoc = Device::init_renderdoc_capture();
+	// G26 local narrowing (not upstream): deliver ONLY disable_sampler_feedback;
+	// force feedback_render_target back to the interface default (false) so the
+	// G24 ride-along is removed. Field surgery on the parsed struct: every other
+	// parsed field passes through unchanged, one variable vs G24.
+	debug_mode.feedback_render_target = false;
+	iface.set_debug_mode(debug_mode);
+	LOGI("G26: debug_mode delivered (disable_sampler_feedback=%d, feedback_render_target=%d, use_rdoc=%d).\n", int(debug_mode.disable_sampler_feedback), int(debug_mode.feedback_render_target), int(use_rdoc));
 	if (use_rdoc)
 	{
-		iface.set_debug_mode(debug_mode);
 		device.begin_renderdoc_capture();
 	}
```

Construction (tabled — field surgery vs second struct):

| # | fact |
| --- | --- |
| 1 | CHOSEN: field surgery on the delivered struct — one added line `debug_mode.feedback_render_target = false;` immediately before the (unchanged) `iface.set_debug_mode(debug_mode);` call. The staged `=true` at `:43` is overwritten; the parsed `--disable-sampler-feedback` value passes through untouched |
| 2 | REJECTED: second struct (`DebugMode narrow; narrow.disable_sampler_feedback = …;`) — would additionally zero `draw_mode`/`timestamps`/`deterministic_timeline_query`, which are already None/false/false in our run (no `--strided`/`--full`), so zero discriminator gain for more lines + divergence from the sibling delivery shape |
| 3 | G24 receipt shape preserved: same call site, same unconditional delivery, same LOGI family — the receipt `printf` keeps G24's `(disable_sampler_feedback=%d, use_rdoc=%d)` slots in order and appends the one field that changed (`feedback_render_target=%d`), so the run is a clean single-variable A/B vs G24 |
| 4 | Delivered state on our path is now exactly (disable=1, feedback=0, timestamps=0, deterministic=0, draw=None) — i.e. the pre-G24 gated behavior (all-default) PLUS the one flag; strictly fewer behavior changes than G24 |

LOGI choice (tabled): ONE line, SWAPPED not added (the G24 receipt line is
replaced, so the binary carries `G26:` ×1 and `G24:` ×0 — `strings`-proven
§2c). It proves the NARROWING independently of behavior: `=1, =0, =0` names
both delivered values directly. Cost: one log line per process (same `LOGI`
already used 8×+ in this TU — no new includes).

No-new-hazard reasoning (tabled):

| # | fact |
| --- | --- |
| 1 | `feedback_render_target=false` is the interface default (`gs_interface.hpp:139`) and exactly what the pre-G24 gate produced on our path (`use_rdoc=0` → setter never called → default-constructed member) — this hunk RESTORES a long-tested configuration for that field, it does not invent one |
| 2 | The setter is a plain struct copy + `set_enable_timestamps(false)` on our path (timestamps unset) — no new threads, no new host writes, no lifecycle change (same as G24 §2b #1) |
| 3 | The surgery line executes once per process, before any parsing-dependent work, with no branches and no allocation — no failure mode beyond what the G24-tested call already had |
| 4 | Worst case the run reproduces G24 exactly (if the ride-along was inert) — which is itself the discriminating outcome (a), not a hazard |

Post-hunk tree status: G25 §2b files + `tools/gs_dump_replayer.cpp`
113→116 changed lines (the ONE replaced `@@` block above); nothing else.
Hunk stays UNCOMMITTED in the SSD clone (G18/G22/G24 precedent).

### 2c. Build record (NEW SSD dir — G14/G18/G20/G22/G24 dirs untouched)

| item | observed |
| --- | --- |
| configure | G24 recipe verbatim into `parallel-gs-g26-android-build` → exit 0, `Configuring done (17.2s)`, `Generating done (10.1s)`, `Processor: aarch64` |
| build | `cmake --build … --target parallel-gs-replayer -j2` → exit 0 (`[458/458]`, full build in the new dir) |
| warnings | ONE `-Wshadow` at `gs_dump_parser.hpp:49` (pre-existing — same class/file as G22/G24; zero warnings point at the hunk lines). No separate TU-rebuild capture needed: this IS a full-build warning record, unlike G24's relink |
| binary | `tools/parallel-gs-replayer`, 265,840,408 B (−16 vs G24 — receipt-string length delta; NEW size expected for a new hunk) |
| sha (build-time re-sha #1, 14:33:01) | `811411816969b1f596394e57710656e3a009a28423c767bc63fb3d86c395d724` (NEW — expected; all later reads must match THIS) |
| build-id | `2e946006f3a6c77af01ce20b2cf37396667a5194` (NDK `llvm-readelf --notes`; distinct from G24's `c7f68343…` and G22's `c2dc902b…`) |
| plumbing presence | `strings` grep: `G26: debug_mode delivered` ×1, `disable-sampler-feedback` ×2, `G24: debug_mode delivered` ×0 (supersede proven in the binary) |
| magic | `7f45 4c46` ELF |
| build dir | 4,482,048 KiB (cap 6 GB ✓; == G18/G20/G22/G24 dirs exactly); older dirs == pre-run exactly (0 growth ✓) |

### 2d. Verify-then-push with NO gap (standing rule — host re-sha → push → on-device match → run)

| step | time (EDT) | observed |
| --- | --- | --- |
| host pre-push re-sha (#2) | 14:33:19 | `81141181…` FULL-match build sha (18 s after build — no zero-damage window) |
| device stage | 14:33:19–22 | `rm -rf` + `mkdir` + push dump (0.017 s) + push binary (2.037 s) into `/data/local/tmp/g26/` ONLY |
| on-device sha match (#3) | 14:33:22 | `154d9d85…` (dump) + `81141181…` (binary) BOTH FULL-match host — push→match gap ~3 s |
| run launch | 14:33:2x | `logcat -c` then run in the next command — on-device match→run gap seconds, no idle window |
| report-time re-sha (#4) | 14:34:39 | `81141181…` FULL-match + ELF magic + size/mtime intact — binary survived the session |

Identity gate: build→pre-push→on-device→report ALL MATCHING (4 reads).
The zero-destroyer did not fire inside this brief's window.

## 3. Task 2 — ONE bounded flag run + score + attribution (Odin)

### 3a. Knob matrix (flag SET — the ONLY delta vs G24's run is the narrowed binary)

| knob / flag | G24 setting | G26 setting | rationale |
| --- | --- | --- | --- |
| `--disable-sampler-feedback` | SET | SET | same tested shape, now without the ride-along |
| `PGS_SKIP_SAMPLER_FEEDBACK` | UNSET | UNSET | no G22 skip to mask or confound |
| `PGS_SKIP_COMPILATION_TASKS=1` | KEPT | KEPT | same async-path control as G22/G24/G25 |

Predicted discriminators: `G26: …disable_sampler_feedback=1,
feedback_render_target=0` receipt + O6 persists at the same Scudo site =>
flag path implicated => scoped instrumentation next; scanouts write (bright
or black) => ride-along implicated => this hunk IS the adoption shape.

### 3b. Run table (ONE run — retry not used, §3h)

| item | observed |
| --- | --- |
| staging | `/data/local/tmp/g26/` ONLY; dump + G26 binary pushed; on-device shas FULL-match host (§2d); logcat cleared, Granite empty before |
| command | `PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer /data/local/tmp/g26/g13-dump.gs --iterations 2 --disable-sampler-feedback` |
| exit / wall | **134** (SIGABRT — O6's exit, NOT O4's 139) / ~1 s wall (`date` 1790015607→1790015607; logcat 14:33:27.407→14:33:27.901; tombstone .917; `Process uptime: 1s`) |
| NARROWING receipt | line 29 `G26: debug_mode delivered (disable_sampler_feedback=1, feedback_render_target=0, use_rdoc=0).` (×1) — ONLY the flag delivered, ride-along at interface default |
| knob receipts | line 25 `Skipping precompilation…` (×1, async knob effective); line 28 `Failed to load RenderDoc` (`use_rdoc=false`, as ever); 0 `G22: skipping` (knob unset, as designed) |
| logcat | 1793 lines (== G24's count exactly): init + ext list + 18 `Running frame` + 18 G10 lines (2 resets + 16 vsync — BOTH iterations complete) + 1664 G11 lines + 8 compute pre-creates + 8 Stalled posts, all `success: yes` (7 compute + 1 graphics `e5825d…`, same graphics hash as G24) + `Total time per VBlank: 1.810 ms` as the LAST line; 0 `success: no`; 0 `wrote … scanout`; 0 `Done!` |
| unpaired-compile note | compute pre-create `959d84147e61df64` has no paired Stalled post — the SAME benign async completion as G24 §3b (same hash, also in G22's log; ~1600 healthy lines follow it) |
| fate | NOT O1/O2/O3 (full loop completed); NOT O4 (proof §3d) → O6 PERSISTS (§3c): post-loop, pre-first-write Scudo abort in first scanout readback, same site as G24 |
| device outputs | 0 scanouts; tombstone_20 written 14:33 (pulled, §3c); device dir removed after (`mg/` only ✓) |

Behavioral narrowing proof (beyond the receipt line): the G10 `img=`
counter collapses while EVERY other counter is line-identical to G24 —

| signal | G24 (ride-along) | G26 (narrowed) |
| --- | --- | --- |
| prims/passes/pal/copies/copy_threads/copy_barriers/scratch | (16 lines) | IDENTICAL on all 16 lines |
| `img=` pass 0 | 1966080/1638400 ×8 (all nonzero) | 1966080, 28672, 0, 327680, 0, 0, 0, 0 (cold-pass residue only) |
| `img=` pass 1 (warm) | 1966080/1638400 ×8 (all nonzero) | 0 ×8 (feedback writes GONE) |

The ONLY behavioral delta vs G24 is the feedback-image counter going to
zero — the single-variable A/B the hunk promised (§2b #3–#4).

### 3c. Tombstone_20 triage (pid 24481 — O6's EXACT signature, same site)

| slot | fact |
| --- | --- |
| signal | SIGABRT (signal 6, SI_QUEUE), Scudo abort message: `corrupted chunk header at address 0x200007c3a87bc30` — same detector/message as G24's O6 (address differs: ASLR) |
| stack | 16 frames (`16 total frames`, == G24): libc abort ← Scudo `deallocate → reportHeaderCorruption` ← adreno anon ×2 + `vkDestroyDescriptorPool` (#09, BuildId `d05dded9…`) ← `DescriptorSetAllocator::clear` (#10) ← `wait_idle_nolock` (#11) ← `wait_idle` (#12) ← `save_scanout_ppm` (#13, `main::$_10`) ← `main` (#14) ← `__libc_init` (#15); main thread pid == tid — frame-for-frame the G24 O6 path |
| timing | post-loop, pre-first-write — 14:33:27.917 = 16 ms after the last logcat line (Total-time, .901; == G24's 16 ms); died inside the FIRST `save_scanout_ppm`'s `wait_idle` before its first LOGI (0 `wrote`, 0 `no image`, series non-empty by absence of the `no iterate-true` LOGE) |
| classification | O6 PERSISTS: identical signal + detector + stack path + phase + post-logcat delta. The ride-along is removed in this binary and nothing about the death changed |
| binary identity | tombstone BuildId `2e946006…` == G26 binary FULL-match => the tested binary is proven to be the narrowed build |
| census | `libllvm-qgl` ×4 (memory-map lines only — zero in the 16-frame crashing stack: mapped-not-executing, as in G24); `vkCreateComputePipelines` ×0; `7463…`/`c61f…` ×0 in logcat AND tombstone; `corrupted chunk` ×1; tombstone 170,457 B (vs _18's 171,439 — ASLR-driven) |

### 3d. O4-absent proof (four legs, G24 §3d shape — flag efficacy holds)

| # | leg | evidence |
| --- | --- | --- |
| 1 | exit/signal differs | 134/SIGABRT vs O4's 139/SIGSEGV; full loop completed (Total-time printed) vs O4's first-draw death |
| 2 | crashing input never exists | crasher pipeline/shader hashes logged 0×; 8/8 Stalled posts `success: yes` (7 compute + 1 graphics), 0 `success: no` (the one unpaired pre-create is G24's benign async completion, §3b note) |
| 3 | death stack has zero driver-compile frames | tombstone_20: Scudo + adreno `vkDestroyDescriptorPool` + Granite descriptor cleanup + `main`; no `dispatch_texture_analysis`, no `libllvm-qgl` execution, no pipeline-build frames |
| 4 | death is post-loop | tombstone 16 ms after Total-time; crashing thread is main in scanout readback, binary BuildId `2e946006…` == G26 binary |

O4 is absent (3rd flag-set run in a row: G24 + G26 absent at value-1 vs
G25 + G23r2 present at value-0/dropped — the bidirectional A/B stands).

### 3e. Score vs G13 oracles (`g14-diff.py`, zero new tooling)

`g14-diff.py ps2x-g13 ps2x-g26` (tool exit 0): oracles **ALL OK**
(8/8 pixel-shas); device PPMs: **0**; `SCORE: N/A - 0 device scanouts`.
(The tool's parenthetical cites its own G14 run; the G26 reason is tabled:
the full replay loop completed but death came inside the FIRST scanout
readback's `wait_idle`, before any PPM write — same as G24.) No means/PSNR
exist to table — the bright-vs-black adoption read is UNMADE for the fourth
brief in a row (G23: O4 → G24: O6 → G25: O4-return → G26: O6-persists).

### 3f. O5 re-fire table (expected post-`Done!` either way — observed: no)

| run | reached teardown? | O5 fired? | note |
| --- | --- | --- | --- |
| run 1 (O6-persists) | NO (died pre-first-write, pre-`Done!`) | NO | Scudo detector fired, but site/phase are O6's (§3c), not O5's post-`Done!` `Device` teardown |

O5 status: unchanged from G24/G25 (named, writer unnamed, three detection
sites in the family — O3-init, O5-post-`Done!`, O6-pre-write — all
writer-unnamed). This brief neither confirms nor denies its re-fire under
the narrowed flag shape — no run reached teardown.

### 3g. O6-attribution verdict (the separation question — TERMINATED)

| candidate | verdict | evidence |
| --- | --- | --- |
| FLAG's full-upload path | IMPLICATED | the ONLY delivered non-default value in this binary; O6 fires identically (signal/stack/phase/16 ms delta) with the ride-along removed |
| `feedback_render_target` ride-along | EXONERATED | delivered =false (interface default) in this binary — proven by receipt (§3b) AND by warm-pass `img=`=0 (§3b table); O6 unchanged, so the ride-along neither causes O6 nor moves its detection |
| O6 site reached? | YES | post-loop death at the identical site — the discriminating phase G25 never reached |

The separation as designed attributes O6: post-loop reached, halves
separated, one run terminates. Note the asymmetry with G25 §3g's framing:
G25's (b) alternative ("scanouts write => flag path") did not fire — but
O6's persistence under the narrowed binary implicates the flag path just as
decisively, since the flag path is now the only remaining delta vs G22's
10 clean scanout writes.

### 3h. Retry + lldb decisions (tabled)

| decision | verdict | rationale |
| --- | --- | --- |
| ONE retry | NOT USED | Brief permits it iff "O1/O3 fires instead of first draw" — first draw was reached and the full loop completed; O6-persists is the discriminating outcome, not a retry condition |
| second shape | NOT USED | out of budget by the same stop rule (the discriminating run already terminated — no second shape needed) |
| lldb triage | NOT USED | tombstone_20 fully classifies (signal/message/full 16-frame stack/thread/timing vs logcat + lambda-level death site); the open question (O6's WRITER) needs an instrumented brief, not post-mortem lldb |

## 4. Hypothesis verdict + the ONE next action

| claim | verdict |
| --- | --- |
| The narrower hunk reaches post-loop AND separates the halves: O6 persists => flag path, or scanouts write => ride-along | **CONFIRMED on the (a) arm, decisively.** Narrowing proven two ways (receipt `=1, =0, =0` §3b + warm-pass `img=`=0 with all other counters line-identical §3b). O6 PERSISTS at the identical site (134, Scudo `corrupted chunk header`, frame-for-frame 16-frame stack §3c, 16 ms post-Total-time) with the ride-along removed => the FLAG's full-upload path is IMPLICATED, the ride-along EXONERATED (§3g). O4 stays absent (4-leg proof §3d — the bidirectional A/B stands). Pixels UNSCORED (0 scanouts, SCORE N/A §3e); O5 unobserved (§3f). |

The ONE next action the numbers justify: **a scoped-instrumentation brief —
ASan or HWASan on the flag's full-upload path** (the `disable_sampler_feedback`
fallback: `gs_interface.cpp:1698` + `:1761` gate region and the CPU-upload
heuristics it selects — per G15/G16 precedent), run on the same
dump/iterations WITH the flag, to NAME O6's heap-corruption writer.
Rationale: O6 is now attributed to the only remaining delta vs G22's clean
writes, and the detector (Scudo `corrupted chunk header` at
`DescriptorSetAllocator::clear`-time `free`) says detection-at-free — only
an instrumented allocator sees the writer. Queued behind it (not this
action): the O5/O3 writer-naming follow-ups (same family, same tooling);
G18-hunk fix adoption (still queued); O1 writer naming (still open);
brighter-vs-black adoption read (unblocked once O6's writer is fixed — the
G26 narrower hunk is the adoption SHAPE candidate, pending that fix); the
Adreno filing — STILL OPEN regardless (submit needs user
identity/tracker; the attribution result does not close it).

No verdicts beyond the hypothesis. No port, no adoption, no upstream contact.

## 5. License / provenance receipts

| artifact | receipt |
| --- | --- |
| paraLLEl-GS rev | `3a66c19…` (LGPL-3.0+ per G7 §4 — cited, not re-read) |
| Granite rev | `16e7395f…` (MIT per G7 §4 — cited); G20 capture hunk compiled in (logging-only, uncommitted, SSD clone only) |
| G14 shims S1–S3 + G7/G8/G10/G11/G18/G22 hunks | untouched, still uncommitted in SSD clone only (G22 HUNK_MATCH re-verified pre-hunk; ZERO other edits this brief) |
| G24 plumbing hunk | SUPERSEDED by the G26 narrowing (replaced in the worktree; diff text survives committed in `local/research/G24/`) |
| G26 narrowing hunk | local-only, uncommitted in SSD clone; diff text committed beside this report (`g26-narrowing.diff`) |
| NDK r30 | build + `llvm-readelf` use (Apache-2.0) |
| logcat/tombstone | run receipts of our own binary in SSD `ps2x-g26/` ONLY (not in git); no PII (`uid: 2000` shell) |
| adoption hunks | NONE — no third-party code copied into any project tree this brief |

## 6. Exact commands

Mac (`/Users/bradrichardson/dev/ssx3` unless noted;
`COPYFILE_DISABLE=1` on SSD steps; `SSD="/Volumes/Extreme SSD"`):

```text
git -C $SSD/parallel-gs-g7 rev-parse HEAD ; status --short ; diff --stat  # §2a
git -C $SSD/parallel-gs-g7 diff gs/gs_renderer.cpp | diff local/research/G22/g22-workaround.diff -  # HUNK_MATCH
git -C $SSD/parallel-gs-g7 diff tools/gs_dump_replayer.cpp (block vs g24-plumbing.diff)  # HUNK_MATCH (pre-supersede)
shasum -a 256 <g24-binary> ; xxd -l 16 <g24-binary>             # §2a 4th zero-damage confirm (fc62d01a…, zeros)
shasum -a 256 <g22-binary>                                      # 5e1f7827… intact
grep -n set_debug_mode/DebugMode/feedback $SSD/parallel-gs-g7/gs/*.* $SSD/parallel-gs-g7/tools/*.cpp  # §2b design
# (replace the ONE @@ block at gs_dump_replayer.cpp:98-106; block > local/research/G26/g26-narrowing.diff)
cmake -S <clone> -B $SSD/parallel-gs-g26-android-build -G Ninja -DCMAKE_TOOLCHAIN_FILE=$NDK/build/cmake/android.toolchain.cmake -DANDROID_ABI=arm64-v8a -DANDROID_PLATFORM=android-35  # §2c exit 0
cmake --build <g26-build> --target parallel-gs-replayer -j2    # §2c exit 0 [458/458], 1 pre-existing warning
shasum -a 256 <g26-binary> (×3 host: build, pre-push, report)  # 81141181… FULL-match
llvm-readelf --notes <g26-binary> ; strings grep ×1/×2/×0 ; xxd -l 4  # 2e946006… + ELF
du -sk <ps2x-g10..g26 + 6 build dirs> ; df -h / $SSD           # §0 (pre + post)
python3 local/research/G14/g14-diff.py $SSD/ps2x-g13 $SSD/ps2x-g26  # §3e
grep -c Running/G10/success/crasher/G26/G22 <logcat> ; pre/post pairing ; census <tombstone>  # §3 census
```

adb (`-s 622c49b1` throughout; `/data/local/tmp/g26/` ONLY; `mg/` never touched):

```text
shell 'ls /data/local/tmp/ ; ls -lt /data/tombstones/ | head ; df -h /data | tail -1'  # pre-check (mg/ only, _19 newest, 28G)
shell 'rm -rf /data/local/tmp/g26 && mkdir -p /data/local/tmp/g26'
push <dump> $G26DIR/g13-dump.gs ; push <g26-binary> $G26DIR/parallel-gs-replayer
shell 'sha256sum g13-dump.gs parallel-gs-replayer'                   # both FULL-match host (§2d)
logcat -c ; logcat -d -s Granite:V | tail -2                         # before (empty)
shell 'cd $G26DIR && date +%s; PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer $G26DIR/g13-dump.gs --iterations 2 --disable-sampler-feedback; echo RUN_EXIT=$?; date +%s'  # 134 (O6-persists)
logcat -d -s Granite:V > $SSD/ps2x-g26/g26-logcat.txt                # 1793 lines
shell 'ls -la $G26DIR/ ; ls -lt /data/tombstones/ | head -6'         # 0 scanouts; _20 new 14:33
pull /data/tombstones/tombstone_20 $SSD/ps2x-g26/g26-tombstone-20.txt
shell 'rm -rf /data/local/tmp/g26 && ls /data/local/tmp/'            # DEVICE_CLEAN (mg/ only)
```

## 7. Gaps (what this brief could not do)

1. Pixels remain unscored (0 scanouts) and the bright-vs-black read unmade —
   blocked by O6 for the second brief in a row (fourth unscored overall).
   The G26 narrower hunk is the adoption SHAPE candidate but unadopted.
2. O6's heap-corruption WRITER is still unnamed (detection-at-free inside a
   driver `free`; §4 action instruments the now-implicated flag path).
3. O5's re-fire under the narrowed flag shape is unobserved (no run reached
   teardown).
4. The warm-pass `img=`=0 vs cold-pass residue (1966080/28672/327680 on pass
   0 #0/#1/#3) split is unexplained at the mechanism level — consistent with
   first-touch uploads, but no brief has named the `img=` counter's exact
   inputs; immaterial to attribution (G24-vs-G26 contrast is stark either
   way).
5. The Adreno filing is still open and unfiled (needs user identity /
   tracker — unchanged owner; the attribution result does not close it).
6. O1 writer, G18-hunk adoption, G17 filing: unchanged / queued.
7. No lldb (decision tabled §3h); OS tombstone store otherwise untouched.
   `upstream/` + harness code untouched; no new dumps; run budget 1/2 spent
   (retry intentionally unspent — no retry condition fired).
8. The zero-destroyed G24 binary was left destroyed (superseded binary;
   rebuilding it is out of scope — G25 already proved its rebuild
   bit-identical before this recurrence).

## 8. Receipt paths

- SSD receipts: `/Volumes/Extreme SSD/ps2x-g26/` (2 files: `g26-logcat.txt`
  1793 lines, `g26-tombstone-20.txt` 170,457 B; 0 PPMs) +
  `parallel-gs-g26-android-build/` (binary 265,840,408 B `81141181…`
  BuildID `2e946006…`).
- SSD receipts (read-only, 0 growth): `ps2x-g10/`-`ps2x-g25/` + G14/G18/G20/
  G22/G24 build dirs + SSD clone (HEAD `3a66c19…`, G22 + G26 hunks
  uncommitted — G24 superseded).
- Session-only: none (no `/tmp/g26-*` files were written).
- Commits: ssx3 `local/research/G26/` `[G26]` + `Orchestrated-By: Muse Code`
  trailer (NOT pushed); ps2xGS untouched (zero commits — hunk uncommitted
  per G18/G22/G24 precedent).

TAIL-RECEIPT: G26 report ends here. Narrower hunk delivers ONLY the flag
(receipted + behaviorally proven), O6 persists at the identical Scudo site
(134, frame-for-frame 16-frame stack, 16 ms delta), flag path implicated,
ride-along exonerated, O4 absent, score N/A, scoped instrumentation next,
filing still open.
