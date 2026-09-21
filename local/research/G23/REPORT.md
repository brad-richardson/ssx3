# G23 report — upstream `--disable-sampler-feedback` is a no-op without RenderDoc: O4 persists, 0 scanouts, O5 never reached

Brief: G23 (this turn) — executes G22 §4's ONE next action ONLY: (1) ONE
bounded on-device run of the SAME dump/iterations with the UPSTREAM flag
(NO rebuild — the G22 binary already ships it) and WITHOUT
`PGS_SKIP_SAMPLER_FEEDBACK`; (2) `g14-diff.py` pixel-diff vs G13 oracles.
Tables + hypothesis + next-action recommendation, no verdicts beyond the
hypothesis. Time box 6 h (used ~1 h). Read first per the brief:
`local/research/G22/REPORT.md` (all of it). No upstream contact of any
kind (standing no-upstream order — the filing draft stays a local doc).

Machine: same as G8-G22 (Apple M4, macOS — no new installs).
Device: Odin3 (`622c49b1`, Android 15), transient dir `/data/local/tmp/g23/`
ONLY; removed at end (`mg/` only).

Headline result: the prediction is REFUTED on both halves, with the exact
mechanism named. (1) Run 1 died in init on the O3 lottery (exit 134,
SIGABRT @ `CommandPool::trim` ← `init_frame_contexts`, zero frames —
retry authorized and spent). (2) The retry reached first draw and died on
O4 EXACTLY as G20 (exit 139, 48-line logcat, the `7463`/`c61f` crasher
pre-create dangling as the last line, 43-frame tombstone through
`dispatch_texture_analysis` → `vkCreateComputePipelines` →
libllvm-qgl): the upstream flag did NOT gate the crashing compile.
(3) Root cause (static + receipt, zero source edits): in
`tools/gs_dump_replayer.cpp` the ONLY `set_debug_mode` call (:101) sits
inside `if (use_rdoc)` (:98-103, identical in HEAD) — and the run logs
`Failed to load RenderDoc` (r2 :28), so the parsed flag never leaves the
local `DebugMode` struct; the interface keeps its default
(`disable_sampler_feedback=false`). (4) Score: oracles ALL OK, device
PPMs 0, SCORE N/A — the bright-vs-black adoption read is unmade. (5) O5
did NOT re-fire in either run (teardown never reached); run 1's abort
message matches O5's Scudo detector at O3's site (message-match,
site-drift — tabled §3d, no new number).

## 0. Byte caps (declared at session start) vs actuals

| class | cap | actual |
| --- | --- | --- |
| NEW SSD `ps2x-g23/` (retrieval: 2 logcats + 2 tombstones, 0 PPMs) | 50 MB | ~333 KB apparent; 9,216 KiB allocated (ExFAT clusters) PASS |
| SSD `ps2x-g10..g22` + G14/G18/G20/G22 build dirs (read-only) | 0 growth | all == pre-run snapshot exactly (g10 43008, g14 7168, g18 5120, g19 5120, g20 11264, g21 15360, g22 25600, g14-build 4480000, g18/g20/g22-build 4482048 KiB) PASS |
| SSD clone (source) | ZERO edits | `git status`/`diff --stat` == G22 post-hunk exactly; HUNK_MATCH re-verified PASS |
| internal volume (`/`) | <=1 GB delta, no clones/builds | 14 Gi avail before and after; no residue outside repo PASS |
| SSD volume | — | 233 -> 232 Gi avail (ps2x-g23 + other-lane) |
| device | `/data/local/tmp/g23/` ONLY | pushed 2 files, pulled 4, dir removed after (`mg/` only) PASS |
| network | none used | no clones, no installs PASS |
| host build | none (NO REBUILD) | no configure, no compile PASS |
| committed to git | text only | REPORT.md only; no binaries PASS |

No P-lane lease, no bytesize/WSL. `COPYFILE_DISABLE=1` on all SSD steps.
No code copied into any project tree.

## 1. Experiment contract

| slot | content |
| --- | --- |
| hypothesis | The upstream `--disable-sampler-feedback` flag (full-upload fallback, no dispatch at all) removes O4 AND renders correct (bright) pixels on the same dump/iterations; O5 is expected to re-fire harmlessly post-`Done!` either way |
| observable signal | binary re-sha + on-device sha match + ONE bounded flag run (exit/wall/fate + knob/flag receipts + crasher absence/presence + tombstone triage if any) + scanouts pulled and scored (`g14-diff.py` exact/le2/le32 + means) + O5 re-fire table |
| alternatives | (a) no-O4 + correct pixels => adoption shape named; (b) O4 persists => flag ineffective, mechanism briefed; (c) new wall => its exact brief; (d) O1/O3 instead of first draw => lottery note + ONE retry |
| stop condition | ZERO source edits; TWO bounded device runs max (flag run + one retry iff O1/O3 fires instead of first draw); no tuning loop, no second workaround shape, no new dumps; no lldb unless the tombstone cannot triage |
| outcome → next action | numbers name the next single experiment (§4) |

Outcome: alternatives (d) then (b) — run 1 hit the O3 lottery in init
(retry spent per the stop rule); the retry hit O4 in first draw with the
flag proven no-op (RenderDoc gate). No tuning loop was entered: zero
hunks, zero builds, two device runs (budget exhausted). lldb not used
(both tombstones classify; tabled §3c).

## 2. Task 1 — pins + flag runs (no analysis until receipts were in)

### 2a. Pin verification (pre-work — G22 §2a reproduced, ZERO edits after)

| item | observed |
| --- | --- |
| SSD clone HEAD | `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd` (== pin) |
| tree status | `M CMakeLists.txt` + `m Granite` + `M gs/gs_interface.cpp` + `M gs/gs_renderer.cpp` + `M tools/CMakeLists.txt` + `M tools/gs_dump_replayer.cpp` + ExFAT `._` sidecars — G22 post-hunk exactly |
| G22 hunk presence | `git diff gs/gs_renderer.cpp` byte-identical to `g22-workaround.diff` (`diff` exit 0, HUNK_MATCH); `diff --stat`: `gs_renderer.cpp` +15 only |
| G22 binary (start re-sha #1) | 265,840,344 B, sha `5e1f782735234fa9a938ebde51f815cb99e7e8a234555f868fb6cc049ae717e8` full-match, BuildID `c2dc902b48d04b8406707c7799f0477b7695294a` (== pins, no zero-fill) |
| G22 binary (pre-push re-sha #2) | same sha + same byte size (standing re-sha hygiene: start AND before push) |
| flag ships in binary | `strings`: `disable-sampler-feedback` ×2, `PGS_SKIP_SAMPLER_FEEDBACK` ×1 |
| rich dump (host) | 11,537,377 B, sha `154d9d8577a210fb794b29a048ee2cf08053f87fe220bb2bf975933a02ad7e32` full-match |
| G14/G18/G20 dirs 0-growth | pre-run `du -sk` == G22 §0 exactly (§0 table); post-run re-verified identical |
| upstream flag (worktree) | usage `:36`, handler `:58` (`cbs.add("--disable-sampler-feedback", … disable_sampler_feedback = true)`), default `gs_interface.hpp:143` (`= false`) — brief's refs match |
| upstream flag (HEAD) | usage `:33`, handler `:55`, default `:143` — the +3 worktree shift is G8/G10-hunk drift; the flag is upstream, not a G-hunk |
| flag consumers (HEAD) | `gs_interface.cpp:1682` (`if (!… && long_term_cache_texture)`) + `:1745` (`commit_cached_texture(…, !…)`); worktree `:1698`/`:1761` (+16 G11-hunk drift) — both upstream |
| device (read-only pre-check) | `622c49b1`, Odin3; `/data/local/tmp/` == `mg/` only; newest tombstone `_15` (G22's O5); `/data` 29 G free |

### 2b. Knob matrix (tabled choice — upstream shape tested independently)

| knob / flag | setting | rationale |
| --- | --- | --- |
| `--disable-sampler-feedback` | SET (appended after `--iterations 2`; dump stays `argv[1]` per `parser.open(argv[1])`) | the tested shape |
| `PGS_SKIP_SAMPLER_FEEDBACK` | UNSET | test the upstream shape independently — no G22 skip to mask or confound it |
| `PGS_SKIP_COMPILATION_TASKS=1` | KEPT | G22's tabled choice: keeps the async path from compiling `sampler_feedback` independently of the flag gate and confounding the experiment |

Predicted discriminators: O4-absent + bright pixels => flag works;
O4-present (crasher pre-create + 139) => flag did not gate; `G22:
skipping` line absent either way (knob unset); `Skipping precompilation`
line present (async knob effective); O5 expected post-`Done!` either way.

### 2c. Flag mechanism (static — what the flag SHOULD do when delivered)

| step | fact (worktree line refs) |
| --- | --- |
| parse | `:58` sets the local `debug_mode.disable_sampler_feedback = true` |
| delivery (THE GATE) | the ONLY `set_debug_mode` call in this tool (`:101`) sits inside `if (use_rdoc)` (`:98-103`); HEAD `:95-100` identical — upstream shape |
| setter | `GSInterface::set_debug_mode` (`gs_interface.cpp:4478`) is a plain struct copy (`debug_mode = mode`) |
| default | interface keeps `disable_sampler_feedback=false` (`gs_interface.hpp:143`) unless the setter runs |
| downstream (when true) | `:1698` gate skips short-term-cache analysis registration; `:1761` passes `sampler_feedback=false` => `commit_cached_texture` (`gs_renderer.cpp:1473-1482`) skips `texture_analysis.resize` + `allocate_upload_indirection` => `texture_analysis` stays empty => `flush_rendering` (`:3238`) never calls `dispatch_texture_analysis` => `upload_texture` (`:3659`) takes the direct full-dispatch branch |
| sibling contrast | `gs_repro_replayer.cpp:165` + `gs_stream_replayer.cpp:185,235` call `set_debug_mode` UNCONDITIONALLY — only the dump replayer gates it on RenderDoc |

### 2d. Run tables (TWO runs — budget exhausted: flag run + one O3 retry)

Staging (both runs): `/data/local/tmp/g23/` ONLY; dump + G22 binary
pushed; on-device shas FULL-match host (`154d9d85…` / `5e1f7827…`;
binary re-verified on-device before the retry too); logcat cleared,
Granite empty before each run.

Run 1 — O3 lottery in init (retry authorized):

| item | observed |
| --- | --- |
| command | `PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer /data/local/tmp/g23/g13-dump.gs --iterations 2 --disable-sampler-feedback` |
| exit / wall | **134** (SIGABRT) / ~0 s wall (`date` 1790007909→1790007909; logcat 12:25:09.867→12:25:09.881; tombstone `Process uptime: 1s`) |
| logcat (`g23-logcat.txt`) | 23 lines: init + ext list, last line `Disabling pipeline cache control.` (:23); 0 `Running frame`; 0 `Skipping precompilation` (died before it); 0 `G22: skipping` (knob unset, as designed); 0 `Done!` |
| crasher refs | `7463…`/`c61f…`: 0 in logcat, 0 in tombstone_16 (no compile ever started) |
| fate | O3 (triage §3b): SIGABRT @ `CommandPool::trim` ← `init_frame_contexts` in init, before first draw — the brief's exact retry condition |
| device outputs | 0 scanouts; tombstone_16 written 12:25 (pulled) |

Run 2 (ONE retry — same command verbatim):

| item | observed |
| --- | --- |
| exit / wall | **139** (SIGSEGV — the O4 signal, NOT 134) / ~0 s wall (`date` 1790007956→1790007956; logcat 12:25:56.225→12:25:56.361; tombstone `Process uptime: 1s`) |
| logcat (`g23-logcat-r2.txt`) | 48 lines (== G20's count): `Skipping precompilation` (:25, async knob effective) + `Failed to load RenderDoc…` (:28, `use_rdoc=false` receipt) + `Running frame` (:30) + `502d…` success (:38) + `b710…` success (:47) + **dangling crasher pre-create** `7463…`/`c61f…` as the LAST line (:48); 0 `G22: skipping`; 0 `Done!` |
| compile census | 2× `success: yes`, 0× `success: no`; `7463…` pre-create unpaired (G20 decode rule: death during that compile) |
| fate | O4 (triage §3c): textbook first-draw sync-compile SIGSEGV through `dispatch_texture_analysis` — the flag did not gate it |
| device outputs | 0 scanouts; tombstone_17 written 12:25 (pulled); device dir removed after (`mg/` only) |

## 3. Task 2 — triage + score + adoption input

### 3a. Tombstone_16 triage (run 1, pid 27957 — O3, retry authorized)

| slot | fact |
| --- | --- |
| signal | SIGABRT (signal 6, SI_QUEUE), Scudo abort message: `corrupted chunk header at address 0x2000076cb22d770` |
| stack | `main+1580 ← Device::init_frame_contexts(+104) ← wait_idle_nolock ← PerFrame::trim_command_pools ← CommandPool::trim(+192) ← vkFreeCommandBuffers ← adreno (2 anon) ← Scudo deallocate → reportHeaderCorruption → abort` (15 frames, main thread; #00–#05 libc, #06–#08 adreno BuildId `d05dded9…`, #09–#13 replayer BuildId `c2dc902b…`, #14 `__libc_init`) |
| timing | init only — 12:25:09.913 = ~32 ms after the last logcat line (`Disabling pipeline cache control`, .881); zero frames, zero compiles |
| classification | O3 by site + phase (SIGABRT @ `trim()` in init, pre-first-draw — G22 §3a's definition verbatim). NOT O1 (139/null-`table` — this is 134); NOT O2 (no `0xf0` fault); NOT O4 (no compile, no driver compile frames); NOT O5 (O5 is post-`Done!` teardown — this never drew) |
| message vs O5 | the Scudo `corrupted chunk header` detector matches O5's message, but the site/phase differ (init `trim` vs post-run `Device` teardown) — message-match, site-drift; writer still UNNAMED (detection-at-free); no new number (O3 by site+phase) |
| flag involvement | NONE plausible: the crash site (`init_frame_contexts`) executes before the dump is parsed and before `debug_mode` is consumed anywhere; the local flag struct is never read on this path |
| binary identity | tombstone BuildId `c2dc902b…` == G22 binary => the tested binary is proven |
| census | `libllvm-qgl`: 0×; `vkCreateComputePipelines`/`kick_compilation`/`__async_func`: 0×; crashing thread is main (pid == tid) |

### 3b. Tombstone_17 triage (run 2, pid 28134 — O4, textbook)

| slot | fact |
| --- | --- |
| signal | SIGSEGV (signal 11, SEGV_MAPERR), null-pointer dereference, fault addr `0x0` |
| stack | 43 frames: #00–#17 libllvm-qgl.so (BuildId `28a2407f…`, == G22's O4 driver BuildId) ← #18–#21 vulkan.adreno.so incl. `vkCreateComputePipelines` ← #22–#26 Granite (`create_pipeline ← build_compute_pipeline ← flush_compute_pipeline ← flush_compute_state ← dispatch`) ← #27 `GSRenderer::dispatch_texture_analysis` ← #28 `flush_rendering` ← #29 `flush_render_pass` ← … ← #40 `GSDumpParser::iterate_until_vsync` ← #41 `main` (all replayer frames BuildId `c2dc902b…`) |
| timing | first draw — 12:25:56.380 = ~19 ms after the last logcat line (dangling crasher pre-create, .361) |
| classification | O4 textbook: exit 139 + dangling `7463`/`c61f` pre-create + death inside the sync compile of exactly that pipeline on the sync thread. NOT O1/O2/O3 (first-draw driver SEGV, not init); NOT O5 (pre-draw, not post-`Done!`) |
| flag involvement | the flag was parsed but never DELIVERED (§2c gate + r2 :28 `use_rdoc=false` receipt): the interface ran with default `disable_sampler_feedback=false`, so `dispatch_texture_analysis` was reached exactly as in G20 (same 48-line shape, same death point) |
| binary identity | tombstone BuildId `c2dc902b…` == G22 binary => the tested binary is proven |
| vs G20 | same dump/iterations/knob-minus-skip shape, same crasher, same signal, same 48-line logcat count — the flag changed nothing observable |

### 3c. Retry + lldb decisions (tabled)

| decision | verdict | rationale |
| --- | --- | --- |
| ONE retry | USED (run 2) | Brief permits it iff "O1/O3 fires instead of first draw" — run 1 was O3 in init with zero frames; the retry reached first draw and yielded the classifiable O4 + no-op mechanism |
| second retry | NOT USED | budget exhausted (2/2); run 2 reached first draw, so no further retry condition exists |
| lldb triage | NOT USED | both tombstones fully classify (signal/message/full stack/thread/timing vs logcat); the open questions (O3/O5 corruption WRITERS) need instrumented briefs, not post-mortem lldb |

### 3d. Score vs G13 oracles (`g14-diff.py`, zero new tooling)

`g14-diff.py ps2x-g13 ps2x-g23` (tool exit 0): oracles **ALL OK**
(8/8 pixel-shas); device PPMs: **0**; `SCORE: N/A - 0 device scanouts`.
(The tool's parenthetical cites its own G14 run; the G23 reason is tabled:
run 1 died in init on O3, run 2 died in first draw on O4 — neither run
reached the first iterate/scanout write.) No means/PSNR exist to table —
the bright-vs-black adoption read is UNMADE, and the adoption input is the
no-op mechanism instead (§4).

### 3e. O4-persistence legs (mirror of G22 §3b — four legs for presence)

| # | leg | evidence |
| --- | --- | --- |
| 1 | exit/signal matches | 139/SIGSEGV (== O4); no `Done!` (died first draw, opposite of G22's post-`Done!` 134) |
| 2 | crashing input exists and dangles | crasher `7463…`/`c61f…` pre-created as the last logcat line with no paired `success` post; 2/2 earlier compiles paired `success: yes` (G20 decode rule) |
| 3 | death stack is the driver compile path | 43 frames: 18 libllvm-qgl + 4 adreno (`vkCreateComputePipelines`) + Granite pipeline-build + `dispatch_texture_analysis` ← `flush_rendering` ← `iterate_until_vsync` ← `main` |
| 4 | death is in-draw, pre-teardown | tombstone 19 ms after the last draw-phase logcat line; crashing thread is main in the replay loop, binary BuildId `c2dc902b…` == G22 binary |

### 3f. O5 re-fire table (expected post-`Done!` either way — observed: neither)

| run | reached teardown? | O5 fired? | note |
| --- | --- | --- | --- |
| run 1 (O3) | NO (died in init) | NO | abort MESSAGE matches O5's Scudo detector, but site/phase are O3's (§3a: message-match, site-drift) |
| run 2 (O4) | NO (died first draw) | NO | no teardown reached; no Scudo frames at all (pure driver SEGV) |

O5 status: unchanged from G22 (named, writer unnamed, scanouts-unaffected
when reached). This brief neither confirms nor denies its re-fire under
the flag — no run reached teardown.

## 4. Hypothesis verdict + the ONE next action

| claim | verdict |
| --- | --- |
| The upstream `--disable-sampler-feedback` flag removes O4 AND renders correct pixels on the same dump/iterations; O5 re-fires harmlessly post-`Done!` either way | **REFUTED on both halves, mechanism named**: O4 PERSISTS (4-leg proof §3e: 139, dangling crasher pre-create, 43-frame driver-compile stack through `dispatch_texture_analysis`, in-draw death) AND pixels are UNSCORABLE (0 scanouts, SCORE N/A §3d). The flag is a no-op without RenderDoc: parsed at `:58` but never delivered — the only `set_debug_mode` call (`:101`) is inside `if (use_rdoc)`, and the run receipts `use_rdoc=false` (r2 :28). O5 did not re-fire (no run reached teardown — §3f). Companion finding: run 1 lost the O3 init lottery (retry spent per the stop rule). |

The ONE next action the numbers justify: **a plumbing brief — move
`iface.set_debug_mode(debug_mode)` out of the `if (use_rdoc)` gate in
`tools/gs_dump_replayer.cpp` (ONE hunk, unconditional like the sibling
replayers), rebuild, and re-run the SAME flag run + pixel-diff — it
decides the adoption shape**. Rationale: the flag's downstream path
(full-upload fallback, no dispatch at all, §2c) is still untested — every
observed byte is consistent with "flag never delivered", so no pixel or
adoption conclusion can be drawn until delivery is proven (e.g. a
`debug_mode` receipt line plus the O4-absent + bright-pixels discriminators
of §2b). Queued behind it (not this action): O5/O3 writer-naming briefs
(ASan/HWASan per G15/G16); G18-hunk fix adoption (still queued); O1
writer naming (still open); the Adreno filing — STILL OPEN regardless
(submit needs user identity/tracker; the no-op finding does not close it).

No verdicts beyond the hypothesis. No port, no adoption, no upstream contact.

## 5. License / provenance receipts

| artifact | receipt |
| --- | --- |
| paraLLEl-GS rev | `3a66c19…` (LGPL-3.0+ per G7 §4 — cited, not re-read) |
| Granite rev | `16e7395f…` (MIT per G7 §4 — cited); G20 capture hunk compiled in (logging-only, uncommitted, SSD clone only) |
| G14 shims S1–S3 + G7/G8/G10/G11/G18/G22 hunks | untouched, still uncommitted in SSD clone only (HUNK_MATCH re-verified pre-run; ZERO new edits) |
| upstream `--disable-sampler-feedback` | exercised on-device via the G22 binary (no rebuild); RenderDoc-gate mechanism cited by file/line (HEAD + worktree); not modified |
| NDK r30 | `llvm-readelf` use only (BuildID re-verify; Apache-2.0) |
| logcats/tombstones | run receipts of our own binary in SSD `ps2x-g23/` ONLY (not in git); no PII (`uid: 2000` shell) |
| adoption hunks | NONE — no third-party code copied into any project tree this brief |

## 6. Exact commands

Mac (`/Users/bradrichardson/dev/ssx3` unless noted;
`COPYFILE_DISABLE=1` on SSD steps; `SSD="/Volumes/Extreme SSD"`):

```text
git -C $SSD/parallel-gs-g7 rev-parse HEAD ; status --short ; diff --stat  # §2a
git -C $SSD/parallel-gs-g7 diff gs/gs_renderer.cpp | diff local/research/G22/g22-workaround.diff -  # HUNK_MATCH
shasum -a 256 <g22-binary>            # §2a start re-sha #1 (5e1f7827…)
llvm-readelf --notes <g22-binary>     # BuildID c2dc902b…
strings <g22-binary> | grep -c disable-sampler-feedback / PGS_SKIP_SAMPLER_FEEDBACK  # 2 / 1
shasum -a 256 $SSD/ps2x-g13/g13-dump.gs  # 154d9d85…
grep -n disable-sampler-feedback/disable_sampler_feedback <replayer.cpp/gs_interface.*>  # §2a/§2c
git show HEAD:tools/gs_dump_replayer.cpp | sed -n '88,102p'  # gate in HEAD
grep -rn set_debug_mode <tools/ gs/>  # sole call :101 + sibling contrast
du -sk <ps2x-g10..g23 + 4 build dirs> ; df -h / $SSD  # §0 (pre + post)
mkdir -p $SSD/ps2x-g23 ; shasum -a 256 <g22-binary> <dump>  # pre-push re-sha #2
python3 local/research/G14/g14-diff.py $SSD/ps2x-g13 $SSD/ps2x-g23  # §3d
grep -c 7463…/c61f… <logcats/tombstones> ; grep -c 'success: yes/no' <r2>  # §3 census
```

adb (`-s 622c49b1` throughout; `/data/local/tmp/g23/` ONLY; `mg/` never touched):

```text
shell 'ls /data/local/tmp/ ; ls -lt /data/tombstones/ | head ; df -h /data | tail -1'  # pre-check (mg/ only, _15 newest, 29G)
shell 'rm -rf /data/local/tmp/g23 && mkdir -p /data/local/tmp/g23'
push <dump> $G23DIR/g13-dump.gs ; push <g22-binary> $G23DIR/parallel-gs-replayer
shell 'sha256sum g13-dump.gs parallel-gs-replayer'   # both FULL-match host
logcat -c ; logcat -d -s Granite:V | tail -2         # before each run (empty)
shell 'cd $G23DIR && date +%s; PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer $G23DIR/g13-dump.gs --iterations 2 --disable-sampler-feedback; echo RUN_EXIT=$?; date +%s'  # run1: 134 (O3)
logcat -d -s Granite:V > $SSD/ps2x-g23/g23-logcat.txt              # 23 lines
shell 'ls -la $G23DIR/ ; ls -lt /data/tombstones/ | head -6'       # 0 scanouts; _16 new 12:25
pull /data/tombstones/tombstone_16 $SSD/ps2x-g23/g23-tombstone-16.txt
shell 'sha256sum $G23DIR/parallel-gs-replayer'       # on-device re-verify pre-retry
logcat -c ; <same run command verbatim>              # run2: 139 (O4)
logcat -d -s Granite:V > $SSD/ps2x-g23/g23-logcat-r2.txt           # 48 lines
pull /data/tombstones/tombstone_17 $SSD/ps2x-g23/g23-tombstone-17.txt
shell 'rm -rf /data/local/tmp/g23 && ls /data/local/tmp/'          # DEVICE_CLEAN (mg/ only)
```

## 7. Gaps (what this brief could not do)

1. The flag's downstream path (full-upload fallback) is STILL UNTESTED —
   every observation equals "flag never delivered"; pixels remain
   unscored (0 scanouts) and the adoption shape undecided (§4 action).
2. O3's and O5's heap-corruption WRITERS are unnamed (detection-at-free
   only; run 1 adds a second Scudo site — needs instrumented briefs).
3. O5's re-fire under the flag is unobserved (no run reached teardown).
4. The Adreno filing is still open and unfiled (needs user identity /
   tracker — unchanged owner; the no-op finding does not close it).
5. O1 writer, G18-hunk adoption, G17 filing: unchanged / queued.
6. No lldb (decision tabled §3c); OS tombstone store otherwise untouched.
   `upstream/` + harness code untouched; no new dumps; run budget 2/2 spent.

## 8. Receipt paths

- SSD receipts: `/Volumes/Extreme SSD/ps2x-g23/` (4 files: `g23-logcat.txt`
  23 lines, `g23-logcat-r2.txt` 48 lines, `g23-tombstone-16.txt` 152,032 B,
  `g23-tombstone-17.txt` 174,249 B; 0 PPMs).
- SSD receipts (read-only, 0 growth): `ps2x-g10/`-`ps2x-g22/` + G14/G18/G20/
  G22 build dirs + SSD clone (HEAD `3a66c19…`, G22 hunk uncommitted).
- Commits: ssx3 `local/research/G23/` `[G23]` + `Orchestrated-By: Muse Code`
  trailer (NOT pushed); ps2xGS untouched (zero source edits — no commit).

TAIL-RECEIPT: G23 report ends here. Upstream flag is a RenderDoc-gated
no-op (O4 persists, 0 scanouts, SCORE N/A), O3 spent the retry, O5 never
reached, plumbing brief next, filing still open.
