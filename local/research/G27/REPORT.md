# G27 report — HWASan names the flag-path heap writer: stride-0 descriptor slab + driver `vkGetDescriptorEXT` smash (Odin)

Brief: G27 (this turn) — executes G26 §4's ONE next action ONLY: (1) table
the sanitizer choice BEFORE building (exactly one: ASan vs HWASan, with a
trivial probe proving loadability first); (2) build in a NEW SSD dir (G22
recipe + sanitizer flags); (3) ONE bounded WITH-FLAG instrumented run to
NAME O6's heap-corruption writer (allocation stack + free stack + class at
the flag-path site). Tables + hypothesis + next-action recommendation, no
verdicts beyond the hypothesis. Time box 6 h (used ~0.45 h — measured wall
15:28:57→15:55 EDT). Read first per the brief: `local/research/G26/
REPORT.md` (all of it: narrower hunk delivers ONLY the flag, O6 persists
byte-identically, flag path implicated, ride-along exonerated) + G15
(HWASan precedent) + G16 (host ASan). No upstream contact of any kind
(standing no-upstream order — local hunks only, filing stays local).

Machine: same as G8–G26 (Apple M4, macOS — no new installs).
Device: Odin3 (`622c49b1`, Android 15), transient dir `/data/local/tmp/g27/`
ONLY; removed at end (`mg/` only).

Headline result: the writer is NAMED, with a closed proof. (1) HWASan
chosen (G15 recipe + fresh trivial probe: clean exit 0 AND fault-mode
tag-mismatch report on-device); ASan rejected (unproven on both axes, one
build). (2) ONE build, exit 0, full identity (NEW size/sha/BuildID, 164
`__hwasan` symbols, G26 strings ×1/×2/×0). (3) ONE flag run: exit 134, and
the sanitizer FIRED — `allocation-tail-overwritten`, size-72 object, full
alloc + free stacks, class heap-buffer-overflow (in-granule) — REPLACING
O6's Scudo signature as predicted. (4) Attribution: the victim's alloc
stack runs through `gs_interface.cpp:1725` (`renderer.create_cached_
texture`), the exact line between the flag's `:1698` + `:1761` gates; the
free stack is post-`Done!` `Device` teardown. The size-72 proof (72 =
64+0+8, the fallback `malloc` for a ZERO-size slab) + an on-device Vulkan
probe (`MISMATCH=1`) + a guard asymmetry in Granite (`create_image_view`'s
descriptorBuffer branch checks the raw feature while `init()` and the
buffer-view path check `supports_descriptor_buffer_or_heap`) converge on
ONE root cause: on Adreno 830 the slab is never initialized (stride 0, all
slots alias one address) yet used, and the driver's `vkGetDescriptorEXT`
(memory_allocator.cpp:1448) writes 64 descriptor bytes through the aliased
pointer, smashing the chunk tail (payload = descriptor bytes 8..15) and
the neighboring chunk (Scudo's `corrupted chunk header` mechanism — O5/O6's
exact detector). (5) Side findings: 10 scanouts WROTE + `Done!` printed
(first scored run since G22) — all pure BLACK (adoption read: made, black,
matching G22's black); O4 absent (4-leg proof). One run spent; retry not
used; lldb not used. The G27 binary was zero-destroyed post-run (6th
recurrence, tabled — run validity unaffected: 3 matching pre-run reads).

## 0. Byte caps (declared at session start) vs actuals

| class | cap | actual |
| --- | --- | --- |
| NEW SSD build dir `parallel-gs-g27-hwasan-build` | 8 GB | 4,817,920 KiB (== G15 hwasan dir scale) PASS |
| NEW SSD `ps2x-g27/` (retrieval: logcat + stderr/stdout + tombstone_23 + 10 PPMs) | 50 MB | ~7.2 MB apparent; 28,672 KiB allocated (ExFAT clusters) PASS |
| SSD `ps2x-g10..g26` + G14/G15/G16/G18/G20/G22/G24/G26 build dirs (read-only) | 0 growth | all == pre-run snapshot exactly (g10 43008, g14 7168, g15 31744, g16 43008, g18–g19 5120, g20 11264, g21 15360, g22 25600, g23 9216, g24–g26 5120; g14-build 4480000, g15-hwasan 4816896, g16-asan 4577280, g18/g20/g22/g24/g26-build 4482048 KiB) PASS |
| SSD clone (source) | ONE hunk max (sanitizer workaround only, else zero) | ZERO new source edits (build flags only); G22 + G26 hunks still uncommitted, HUNK_MATCH re-verified pre-build; budget UNSPENT PASS |
| internal volume (`/`) | <=1 GB delta, no clones/builds | 10 Gi avail before → 9.3 Gi after (other-lane delta); G27 `/tmp` residue ~120 KB (2 probes + blocks) PASS |
| SSD volume | — | 214 Gi avail before → 208 Gi after (new build dir + retrieval; remainder other-lane) |
| device | `/data/local/tmp/g27/` ONLY | staged ≤4 files at a time, pulled 13, dir removed after (`mg/` only); tombstones _21/_22 (probe faults) + _23 (flag run) remain in OS store (auto-rotated, shell cannot remove) PASS |
| network | none used | no clones, no installs PASS |
| host build | ONE build, `-j2`, new dir | configure exit 0 + full build exit 0 `[458/458]`, pre-existing warnings only PASS |
| device runs | TWO bounded max (flag + retry iff O1/O3) | ONE flag run (probe-load checks + vkprops query are not replayer runs and don't count) PASS |
| committed to git | text only | REPORT.md + 4 session scripts; no binaries |

No P-lane lease, no bytesize/WSL. `COPYFILE_DISABLE=1` on all SSD steps.
No code copied into any project tree.

## 1. Experiment contract

| slot | content |
| --- | --- |
| hypothesis | The ONE instrumented WITH-FLAG run names O6's heap-corruption writer: the sanitizer report gives the allocation stack + free stack + overflow/underflow/use-after-free class at the flag-path site (`gs_interface.cpp` `:1698`+`:1761` gate region), replacing O6's Scudo `corrupted chunk header` signature |
| observable signal | sanitizer choice table + probe receipts + build exit/sha/build-id + verify-then-push chain (host re-sha → push → on-device match, no gap) + ONE bounded flag run (exit/wall/fate + `G26:` receipt + knob receipts + sanitizer stderr COMPLETE verbatim + tombstone triage) + scanouts scored (`g14-diff.py`) + O4 legs + writer file/line/function |
| alternatives | (a) sanitizer names the writer (alloc + free + class at flag site) => writer-fix brief next; (b) Scudo still fires first => table why the sanitizer missed + what narrower scope catches it; (c) neither sanitizer loads => receipt the obstacle, STOP, no second shape; (d) O1/O3 instead of first draw => lottery note + ONE retry |
| stop condition | ONE hunk max (sanitizer-necessitated source workaround ONLY, else zero); ONE build (new dir); TWO bounded device runs max (flag run + one retry iff O1/O3); no tuning loop, no second shape, no new dumps; no lldb unless the tombstone cannot triage |
| outcome → next action | numbers name the next single experiment (§4) |

Outcome: alternative (a) — the sanitizer FIRED with full lifecycle + class
at the flag-path site, and convergent proof (size math + on-device mismatch
probe + guard asymmetry) names the exact store. No tuning loop was entered:
zero source edits, one build, one device run. Retry not used (O1/O3 never
fired); lldb not used (sanitizer report + tombstone classify fully).

## 2. Task 1 — sanitizer choice + probe + build + verify-then-stage (no run until §3)

### 2a. Pin verification (pre-work — G26 §2 reproduced, ZERO edits after)

| item | observed |
| --- | --- |
| SSD clone HEAD | `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd` (== pin) |
| tree status (pre-build) | `M CMakeLists.txt` + `m Granite` + `M gs/gs_interface.cpp` + `M gs/gs_renderer.cpp` + `M tools/CMakeLists.txt` + `M tools/gs_dump_replayer.cpp` (116 changed lines) + ExFAT `._` sidecars — G26 end state exactly |
| G22 hunk | `git diff gs/gs_renderer.cpp` byte-identical to `g22-workaround.diff` (HUNK_MATCH) |
| G26 hunk | worktree `@@ -93,9 +96,15 @@` block line-identical to committed `g26-narrowing.diff` (HUNK_MATCH); other `@@` blocks are the pre-existing G8/G10 hunks, untouched; hunk UNCOMMITTED (tested shape stays flag-only) |
| G24 | stays SUPERSEDED (no G24-shaped code in tree; diff text survives in `local/research/G24/`) |
| G26 binary (5th zero-damage recurrence) | 265,840,408 B, mtime frozen 14:32 (G26's build), sha `ae1bc63a…` (zeros), magic `0000` — destroyed AFTER G26's report-time intact read, as the brief states; tabled, not rebuilt (superseded binary, out of scope) |
| rich dump (host) | 11,537,377 B, sha `154d9d85…d7e32` full-match |
| dirs 0-growth | pre-run `du -sk` == G26 §0 exactly (see §0); post-run re-verified §0 |
| recipe | NDK r30 (`Pkg.ReleaseName = r30`); cmake 4.4.3 + ninja; `libclang_rt.hwasan-aarch64-android.so` (1,138,992 B, sha `8f4cb822…`) + `libc++_shared.so` (9,485,032 B, sha `7466ed09…`) present in NDK |
| device (read-only pre-check) | `622c49b1`, Odin3, Android 15; `/data/local/tmp/` == `mg/` only; newest tombstone `_20` (G26's O6, 14:33); `/data` 29 G free |
| `g14-diff.py` + oracles | tool present; `ps2x-g13/` holds dump + 8 vsync PPMs |

### 2b. Sanitizer choice (tabled BEFORE building — exactly one)

| candidate | build on this tree | on-device load on Odin3/Android 15 | verdict |
| --- | --- | --- | --- |
| HWASan (`-fsanitize=hwaddress`, shared STL, `hwasan-globals=0`) | PROVEN: G15 recipe exit 0 `[452/452]` on this source family (static-STL link failure + shared-STL fix already known) | PROVEN twice: G15 full-binary run on this exact device/OS (exit 139, executed) + G27 trivial probe this brief (§2c: clean exit 0 AND fault-mode report) | **CHOSEN** |
| ASan (`-fsanitize=address` + runtime staging) | UNPROVEN for Android on this tree (G16 was mac-host only); link risk on the 265 MB binary untested; one-build budget cannot absorb a link failure | UNPROVEN (no Android ASan execution anywhere in the G-lineage) | REJECTED |

`wrap.sh` note (tabled): the NDK docs require `wrap.sh` for *app*
(zygote-spawned) processes; our shell-launched binary inherits env
directly — G15 precedent + the §2c probe prove `LD_LIBRARY_PATH=<dir>`
staging suffices. No `wrap.sh` used. No second shape was needed (STOP
clause not triggered).

### 2c. Loadability probe (trivial instrumented probe — NOT a run)

Source `g27-hwasan-probe.c` (mirrored): `malloc(32)` + print + free; argv
`fault` triggers a 1-byte heap-buffer-overflow. Built with NDK clang
(`--target=aarch64-linux-android35`, same HWASan flags), 10,392 B,
NEEDED `libclang_rt.hwasan-aarch64-android.so`. Staged in
`/data/local/tmp/g27/` with the runtime .so (on-device shas FULL-match
host: probe `c085cf9b…`, runtime `8f4cb822…`).

| probe mode | observed |
| --- | --- |
| clean | `G27-PROBE-LOAD-OK`, `done exit=0`, exit 0 — runtime loads, malloc/free interceptors work; `/apex/…/bionic/hwasan/libc.so` present (OS-supported path) |
| fault | full `HWAddressSanitizer: tag-mismatch` report (WRITE size 1, `heap-buffer-overflow`, fault + alloc stacks, memory tags), exit 134, tombstone_21 — detector FIRES, report shape confirmed |
| fault re-run (exit-code confirm) | exit 134, tombstone_22 — stable |

Probe tombstones _21/_22 (42 KB each) are method residue in the OS-owned
store (tabled, irremovable as shell). Newest tombstone before the flag run:
_22. The full build was committed ONLY after this probe passed.

### 2d. Build record (NEW SSD dir — all older dirs untouched)

Configure (G22/G26 recipe + G15 HWASan flags, `g27-build-hwasan.sh`
mirrored): exit 0 (`Configuring done (13.3s)`, `Generating done (9.3s)`,
`Processor: aarch64`). Build `cmake --build … --target
parallel-gs-replayer -j2`: exit 0 (`[458/458]`, 15:31:30→15:34:32).

| item | observed |
| --- | --- |
| warnings | pre-existing `-Wshadow` (`FileDeleter`, `gs_dump_parser.hpp:49` — same class/file as G22/G24/G26); zero warnings point at the hunk lines or sanitizer flags |
| binary | `tools/parallel-gs-replayer`, 289,112,232 B (+4,056 vs G15 hwasan — new hunk; NEW size expected) |
| sha (build-time re-sha #1, 15:34:47) | `6387d2f31c5e42b545529a87b75632d4582b390415d9a24729573ef2202eda46` (NEW — expected; all later pre-run reads must match THIS) |
| build-id | `529778869c94e294ee415199f22ad109fe5d760c` (distinct from G26 `2e946006…` and G15 hwasan) |
| plumbing presence | `strings` grep: `G26: debug_mode delivered` ×1, `disable-sampler-feedback` ×2, `G24: debug_mode delivered` ×0 (narrower hunk in the binary) |
| instrumentation proof | 164 `__hwasan` symbols (== G15's 164); NEEDED `libclang_rt.hwasan-aarch64-android.so` + `libc++_shared.so` + system libs |
| magic | `7f45 4c46` ELF |
| build dir | 4,817,920 KiB (cap 8 GB ✓) |

### 2e. Verify-then-push with NO gap (standing rule)

| step | time (EDT) | observed |
| --- | --- | --- |
| host pre-push re-sha (#2) | 15:35:15 | `6387d2f3…` FULL-match build sha (28 s after identity — no zero-damage window) |
| device stage | 15:35:27–30 | `rm -rf` + `mkdir` + push dump (0.022 s) + push binary (2.351 s) + push 2 runtimes into `/data/local/tmp/g27/` ONLY |
| on-device sha match (#3) | 15:35:30 | `154d9d85…` (dump) + `6387d2f3…` (binary) + `7466ed09…` (libc++_shared) + `8f4cb822…` (hwasan rt) ALL FULL-match host — push→match gap ~3 s |
| run launch | 15:35:41 | `logcat -c` (verified empty) then run — on-device match→run gap seconds, no idle window |
| report-time re-sha (#4) | 15:50:08 | `13d2fc69…` MISS + ELF magic `0000` (stable across 2 reads, size/mtime frozen) — **6th zero-damage recurrence**, ~15 min post-push; run validity UNAFFECTED (3 matching pre-run reads + on-device match; destruction came after the completed run) |

Identity gate: build→pre-push→on-device ALL MATCHING (3 reads + 4 files
on-device). The zero-destroyer fired inside this brief's window but AFTER
the run, not inside the verify-then-push chain.

## 3. Task 2 — ONE instrumented run + writer triage (Odin)

### 3a. Knob matrix (flag SET — the ONLY delta vs G26's run is the instrumented binary)

| knob / flag | G26 setting | G27 setting | rationale |
| --- | --- | --- | --- |
| `--disable-sampler-feedback` | SET | SET | same tested shape (flag-only hunk in tree) |
| `PGS_SKIP_SAMPLER_FEEDBACK` | UNSET | UNSET | no G22 skip to mask or confound |
| `PGS_SKIP_COMPILATION_TASKS=1` | KEPT | KEPT | same async-path control |
| `HWASAN_OPTIONS` | n/a | `halt_on_error=1` (verbatim) | first violation halts; report to stderr |
| `LD_LIBRARY_PATH` | n/a | `/data/local/tmp/g27` (verbatim) | runtime + `libc++_shared` staging (G15 precedent; no `wrap.sh` — shell binary, §2b) |

Predicted discriminators: `G26: …disable_sampler_feedback=1,
feedback_render_target=0` receipt + sanitizer report (alloc + free + class
at the flag-path site) REPLACING O6's Scudo signature.

### 3b. Run table (ONE run — retry not used, §3k)

| item | observed |
| --- | --- |
| staging | `/data/local/tmp/g27/` ONLY; dump + HWASan binary + 2 runtimes pushed; 4/4 on-device shas FULL-match host (§2e); logcat cleared, verified empty before |
| command | `PGS_SKIP_COMPILATION_TASKS=1 HWASAN_OPTIONS=halt_on_error=1 LD_LIBRARY_PATH=/data/local/tmp/g27 timeout -s KILL 280 ./hwasan-replayer /data/local/tmp/g27/g13-dump.gs --iterations 2 --disable-sampler-feedback` (stdout→file, stderr→file) |
| exit / wall | **134** (SIGABRT — sanitizer abort, §3c) / ~1 s wall (`date` 1790019341→1790019342; logcat 15:35:41.8→15:35:42.7; `Process uptime: 2s`) |
| NARROWING receipt | line 29 `G26: debug_mode delivered (disable_sampler_feedback=1, feedback_render_target=0, use_rdoc=0).` (×1) — ONLY the flag delivered, in the instrumented binary |
| knob receipts | line 25 `Skipping precompilation…` (async knob effective); line 28 `Failed to load RenderDoc` (`use_rdoc=false`, benign as ever); 0 `G22: skipping` (knob unset, as designed) |
| logcat | 1804 lines (== G26's 1793 + 10 `wrote` + `Done!` exactly): init + ext list (`VK_EXT_descriptor_buffer` enabled, line 21) + 18 `Running frame` + 18 G10 lines (BOTH iterations complete) + 8 Stalled posts, all `success: yes` + `Total time per VBlank: 7.743 ms` (HWASan overhead vs G26's 1.810) + 10 `G8: wrote … scanout` (lines 1794–1803) + `Done!` as the LAST line (1804); 0 `success: no`; 0 ERROR/LOGE besides RenderDoc |
| behavioral narrowing | warm-pass `img=`: 0/0/0/8192/0/0/0/0 (cf. G26's 0×8 — one 8192-residue line under HWASan layout; feedback writes still gone); cold pass keeps first-touch residue (1966080/315392/282624/327680/0/0/0/0) |
| fate | NOT O1/O2/O3 (full loop completed); NOT O4 (proof §3h); NOT O6-as-Scudo (no `corrupted chunk header` anywhere — Scudo replaced by construction, §3j) → **HWASan FIRED** (§3c): post-`Done!`, Device-teardown, tail-overwrite detected at free |
| device outputs | 10 scanouts (vsync0–7 + first + last, 688,143 B each); stdout 0 B; stderr 8,050 B (the report, §3c); tombstone_23 written 15:35 (pulled, §3g); device dir removed after (`mg/` only ✓) |

### 3c. Sanitizer report (COMPLETE, VERBATIM — 8,050 B, 84 lines, nothing omitted)

```text
==7301==ERROR: HWAddressSanitizer: allocation-tail-overwritten; heap object [0x00427b9616c0,0x00427b961708) of size 72

Stack of invalid access unknown. Issue detected at deallocation time.
deallocated here:
    #0 0x00723b552fe4  (/data/local/tmp/g27/libclang_rt.hwasan-aarch64-android.so+0x22fe4) (BuildId: 10d9bcd9527ea1f5fdcda1f8e9f339f5ce052211)
    #1 0x005f7c70d2b4  (/data/local/tmp/g27/hwasan-replayer+0xdf92b4) (BuildId: 529778869c94e294ee415199f22ad109fe5d760c)
    #2 0x005f7c2fd808  (/data/local/tmp/g27/hwasan-replayer+0x9e9808) (BuildId: 529778869c94e294ee415199f22ad109fe5d760c)
    #3 0x005f7c2fd770  (/data/local/tmp/g27/hwasan-replayer+0x9e9770) (BuildId: 529778869c94e294ee415199f22ad109fe5d760c)
    #4 0x005f7c2fd684  (/data/local/tmp/g27/hwasan-replayer+0x9e9684) (BuildId: 529778869c94e294ee415199f22ad109fe5d760c)
    #5 0x005f7c2fd60c  (/data/local/tmp/g27/hwasan-replayer+0x9e960c) (BuildId: 529778869c94e294ee415199f22ad109fe5d760c)
    #6 0x005f7c2fd510  (/data/local/tmp/g27/hwasan-replayer+0x9e9510) (BuildId: 529778869c94e294ee415199f22ad109fe5d760c)
    #7 0x005f7c2fd3dc  (/data/local/tmp/g27/hwasan-replayer+0x9e93dc) (BuildId: 529778869c94e294ee415199f22ad109fe5d760c)
    #8 0x005f7c2fd078  (/data/local/tmp/g27/hwasan-replayer+0x9e9078) (BuildId: 529778869c94e294ee415199f22ad109fe5d760c)
    #9 0x005f7c2fcf68  (/data/local/tmp/g27/hwasan-replayer+0x9e8f68) (BuildId: 529778869c94e294ee415199f22ad109fe5d760c)
    #10 0x005f7c2fcd08  (/data/local/tmp/g27/hwasan-replayer+0x9e8d08) (BuildId: 529778869c94e294ee415199f22ad109fe5d760c)
    #11 0x005f7c2fcc24  (/data/local/tmp/g27/hwasan-replayer+0x9e8c24) (BuildId: 529778869c94e294ee415199f22ad109fe5d760c)
    #12 0x005f7c2fcaac  (/data/local/tmp/g27/hwasan-replayer+0x9e8aac) (BuildId: 529778869c94e294ee415199f22ad109fe5d760c)
    #13 0x005f7c4f7144  (/data/local/tmp/g27/hwasan-replayer+0xbe3144) (BuildId: 529778869c94e294ee415199f22ad109fe5d760c)
    #14 0x005f7c4f70a0  (/data/local/tmp/g27/hwasan-replayer+0xbe30a0) (BuildId: 529778869c94e294ee415199f22ad109fe5d760c)
    #15 0x005f7c263690  (/data/local/tmp/g27/hwasan-replayer+0x94f690) (BuildId: 529778869c94e294ee415199f22ad109fe5d760c)
    #16 0x005f7c28a28c  (/data/local/tmp/g27/hwasan-replayer+0x97628c) (BuildId: 529778869c94e294ee415199f22ad109fe5d760c)
    #17 0x005f7c0dbd40  (/data/local/tmp/g27/hwasan-replayer+0x7c7d40) (BuildId: 529778869c94e294ee415199f22ad109fe5d760c)
    #18 0x00723c696cc0  (/apex/com.android.runtime/lib64/bionic/hwasan/libc.so+0x5ecc0) (BuildId: 91a4326da199a46291216996c70f6974)
    #19 0x005f7c0d93f8  (/data/local/tmp/g27/hwasan-replayer+0x7c53f8) (BuildId: 529778869c94e294ee415199f22ad109fe5d760c)

allocated here:
    #0 0x00723b553648  (/data/local/tmp/g27/libclang_rt.hwasan-aarch64-android.so+0x23648) (BuildId: 10d9bcd9527ea1f5fdcda1f8e9f339f5ce052211)
    #1 0x00723c68a470  (/apex/com.android.runtime/lib64/bionic/hwasan/libc.so+0x52470) (BuildId: 91a4326da199a46291216996c70f6974)
    #2 0x005f7c70cf68  (/data/local/tmp/g27/hwasan-replayer+0xdf8f68) (BuildId: 529778869c94e294ee415199f22ad109fe5d760c)
    #3 0x005f7c737754  (/data/local/tmp/g27/hwasan-replayer+0xe23754) (BuildId: 529778869c94e294ee415199f22ad109fe5d760c)
    #4 0x005f7c3f0a70  (/data/local/tmp/g27/hwasan-replayer+0xadca70) (BuildId: 529778869c94e294ee415199f22ad109fe5d760c)
    #5 0x005f7c4f98e0  (/data/local/tmp/g27/hwasan-replayer+0xbe58e0) (BuildId: 529778869c94e294ee415199f22ad109fe5d760c)
    #6 0x005f7c4f92b4  (/data/local/tmp/g27/hwasan-replayer+0xbe52b4) (BuildId: 529778869c94e294ee415199f22ad109fe5d760c)
    #7 0x005f7c321664  (/data/local/tmp/g27/hwasan-replayer+0xa0d664) (BuildId: 529778869c94e294ee415199f22ad109fe5d760c)
    #8 0x005f7c2a8f58  (/data/local/tmp/g27/hwasan-replayer+0x994f58) (BuildId: 529778869c94e294ee415199f22ad109fe5d760c)
    #9 0x005f7c2b0af0  (/data/local/tmp/g27/hwasan-replayer+0x99caf0) (BuildId: 529778869c94e294ee415199f22ad109fe5d760c)
    #10 0x005f7c267cb4  (/data/local/tmp/g27/hwasan-replayer+0x953cb4) (BuildId: 529778869c94e294ee415199f22ad109fe5d760c)
    #11 0x005f7c1c3f50  (/data/local/tmp/g27/hwasan-replayer+0x8aff50) (BuildId: 529778869c94e294ee415199f22ad109fe5d760c)
    #12 0x005f7c12e430  (/data/local/tmp/g27/hwasan-replayer+0x81a430) (BuildId: 529778869c94e294ee415199f22ad109fe5d760c)
    #13 0x005f7c1300d8  (/data/local/tmp/g27/hwasan-replayer+0x81c0d8) (BuildId: 529778869c94e294ee415199f22ad109fe5d760c)
    #14 0x005f7c1753c4  (/data/local/tmp/g27/hwasan-replayer+0x8613c4) (BuildId: 529778869c94e294ee415199f22ad109fe5d760c)
    #15 0x005f7c13c518  (/data/local/tmp/g27/hwasan-replayer+0x828518) (BuildId: 529778869c94e294ee415199f22ad109fe5d760c)
    #16 0x005f7c17e0f4  (/data/local/tmp/g27/hwasan-replayer+0x86a0f4) (BuildId: 529778869c94e294ee415199f22ad109fe5d760c)
    #17 0x005f7c17fa70  (/data/local/tmp/g27/hwasan-replayer+0x86ba70) (BuildId: 529778869c94e294ee415199f22ad109fe5d760c)
    #18 0x005f7c13e980  (/data/local/tmp/g27/hwasan-replayer+0x82a980) (BuildId: 529778869c94e294ee415199f22ad109fe5d760c)
    #19 0x005f7c149bd0  (/data/local/tmp/g27/hwasan-replayer+0x835bd0) (BuildId: 529778869c94e294ee415199f22ad109fe5d760c)

Tail contains: .. .. .. .. .. .. .. .. 10 00 20 00 30 8c 35 00 
Expected:      .. .. .. .. .. .. .. .. c0 c3 0c 43 7e ac ed 59 
                                       ^^ ^^ ^^ ^^ ^^ ^^ ^^ ^^ 
This error occurs when a buffer overflow overwrites memory
after a heap object, but within the 16-byte granule, e.g.
   char *x = new char[20];
   x[25] = 42;
HWAddressSanitizer does not detect such bugs in uninstrumented code at the time of write,
but can detect them at the time of free/delete.
To disable this feature set HWASAN_OPTIONS=free_checks_tail_magic=0
Thread: T0 0x006900002000 stack: [0x007fea035000,0x007fea835000) sz: 8388608 tls: [0x00723e8a5ec0,0x00723e8a9000)

Memory tags around the buggy address (one tag corresponds to 16 bytes):
  0x00427b960e00: eb  e1  58  58  58  58  58  58  b0  b0  b0  b0  b0  b0  98  98 
  0x00427b960f00: 98  98  98  98  24  24  24  24  24  b4  6f  6f  6f  6f  6f  2c 
  0x00427b961000: 83  83  83  83  83  83  de  de  de  de  de  de  3f  3f  3f  3f 
  0x00427b961100: 3f  3f  34  34  34  34  34  34  83  83  83  83  83  cc  64  64 
  0x00427b961200: 64  64  64  62  ce  ce  ce  ce  ce  c2  fc  fc  fc  fc  fc  24 
  0x00427b961300: 95  95  95  95  95  67  dc  dc  dc  dc  dc  dc  d8  d8  d8  d8 
  0x00427b961400: d8  e0  94  94  94  94  94  94  b3  b3  b3  b3  b3  b3  6b  6b 
  0x00427b961500: 6b  6b  6b  6b  e0  e0  e0  e0  e0  8a  5f  5f  5f  5f  5f  5f 
=>0x00427b961600: e9  e9  e9  e9  e9  e9  d5  d5  d5  d5  d5  e6 [59] 59  59  59 
  0x00427b961700: 08  d8  9f  9f  9f  9f  9f  b1  a9  a9  a9  a9  a9  a9  20  20 
  0x00427b961800: 20  20  20  20  5f  5f  5f  5f  5f  5f  51  51  51  51  51  fb 
  0x00427b961900: 99  99  99  99  99  42  af  af  af  af  af  af  fd  fd  fd  fd 
  0x00427b961a00: fd  f8  2c  2c  2c  2c  2c  a0  e0  e0  e0  e0  e0  e0  35  35 
  0x00427b961b00: 35  35  35  35  ed  ed  ed  ed  ed  ed  40  40  40  40  40  8b 
  0x00427b961c00: 53  53  53  53  53  c4  7c  7c  7c  7c  7c  77  1b  1b  1b  1b 
  0x00427b961d00: 1b  1b  54  54  54  54  54  21  2d  2d  2d  2d  2d  e9  1b  1b 
  0x00427b961e00: 1b  1b  1b  1b  12  12  12  12  12  12  ec  ec  ec  ec  ec  ec 
Tags for short granules around the buggy address (one tag corresponds to 16 bytes):
  0x00427b961500: ..  ..  ..  ..  ..  ..  ..  ..  ..  ..  ..  ..  ..  ..  ..  .. 
=>0x00427b961600: ..  ..  ..  ..  ..  ..  ..  ..  ..  ..  ..  .. [..] ..  ..  .. 
  0x00427b961700: 00  ..  ..  ..  ..  ..  ..  ..  ..  ..  ..  ..  ..  ..  ..  .. 
See https://clang.llvm.org/docs/HardwareAssistedAddressSanitizerDesign.html#short-granules for a description of short granule tags
Learn more about HWASan reports: https://source.android.com/docs/security/test/memory-safety/hwasan-reports
SUMMARY: HWAddressSanitizer: allocation-tail-overwritten (/data/local/tmp/g27/hwasan-replayer+0xdf92b4) (BuildId: 529778869c94e294ee415199f22ad109fe5d760c) 
```

Class: `allocation-tail-overwritten` = heap-buffer-overflow whose write
stayed inside the 16-byte granule (invisible to tag checks), detected at
free time. Victim: 72-byte heap object. Payload: 8 tail bytes overwritten
with `10 00 20 00 30 8c 35 00`.

### 3d. Stack symbolization (NDK `llvm-symbolizer`, unstripped binary)

Deallocation stack (free in post-`Done!` `Device` teardown):

| # | function | file:line |
| --- | --- | --- |
| 1 | `Util::memalign_free` | Granite `util/aligned_alloc.cpp:77` (fallback `free(p[-1])` branch) |
| 2–10 | `SlabAllocator::MallocDeleter` → `unique_ptr` reset/dtor → `vector<unique_ptr<uchar, MallocDeleter>>` clear/dtor | `slab_allocator.hpp:46` + libc++ headers |
| 11–12 | `SlabAllocator::~SlabAllocator` → `ThreadSafeSlabAllocator::~ThreadSafeSlabAllocator` | `slab_allocator.hpp:33` → `:55` |
| 13–14 | `DescriptorBufferAllocator::DescriptorTypeInfo::~DescriptorTypeInfo` → `~DescriptorBufferAllocator` | `memory_allocator.hpp:414` → `memory_allocator.cpp:1177` |
| 15–17 | `Device::Managers::~Managers` → `Device::~Device` → `main` | `device.hpp:618` → `device.cpp:2179` → `gs_dump_replayer.cpp:258` |

Allocation stack (victim born on the FLAG path):

| # | function | file:line |
| --- | --- | --- |
| 2 | `Util::memalign_alloc` | Granite `util/aligned_alloc.cpp:48` (fallback `malloc(boundary + size + 8)` branch) |
| 3–4 | `SlabAllocator::allocate` → `ThreadSafeSlabAllocator::allocate` | `slab_allocator.cpp:37` → `slab_allocator.hpp:61` |
| 5–6 | `DescriptorBufferAllocator::alloc_storage_image` → `create_image_view` | `memory_allocator.hpp:389` → `memory_allocator.cpp:1447` |
| 7–10 | `ImageResourceHolder::create_default_view(s)` → `Device::create_image_from_staging_buffer` → `Device::create_image` | `device.cpp:3643` → `:3522` → `:4392` → `:3885` |
| 11 | `GSRenderer::create_cached_texture` | `gs/gs_renderer.cpp:1385` |
| 12 | `GSInterface::drawing_kick_update_texture` | `gs/gs_interface.cpp:1725` — the `renderer.create_cached_texture(desc)` call, BETWEEN the flag's `:1698` and `:1761` gates |
| 13–19 | `drawing_kick_update_state` → `drawing_kick_append` → `drawing_kick_primitive` → `drawing_kick` → `packed_XYZ` → `packed_STQRGBAXYZ` → `gif_transfer` | `gs_interface.cpp:1843` → `:2697` → `:2894` → `:2938` → `:4132` → `:4145` → `:4386` |

### 3e. Writer identification (the closed proof chain)

The report says `Stack of invalid access unknown` (in-granule writes never
trip tag checks), so the store PC is identified by convergent proof, not by
a captured PC. Five links, each independently checkable:

| # | link | evidence |
| --- | --- | --- |
| 1 | The 72-byte victim is a slab block grown with size **0** | `SlabAllocator::allocate` grows via `memalign_alloc(64, count × object_size)` with `count = 64<<k ≥ 64` (`slab_allocator.cpp:36-37`) — a multiple of 64, so 72 is IMPOSSIBLE from that call directly. Both DWARF frames resolve to the `aligned_alloc.cpp` FALLBACK branch (alloc `:48` = `malloc(boundary + size + 8)`, free `:77` = `free(p[-1])`, 7 lines from the POSIX branch — not attribution slop). `malloc(64 + S + 8) = 72` ⟺ `S = 0` ⟺ `object_size = 0` (count > 0). The slab was NEVER initialized: stride 0, all 64 slots alias ONE address |
| 2 | Stride-0 slabs happen ⟺ `DescriptorBufferAllocator::init()` early-returns | `init_copy_func` unconditionally runs `slab.init(info.size)` (`memory_allocator.cpp:1039`); the only skip is the `!supports_descriptor_buffer_or_heap` early-`true` at `:835-836` (the `:899-903` create_buffer failure would LOGE — 0 such lines in logcat). `device.cpp:995` ignores `init()`'s return, so the early-`true` is silent |
| 3 | The slab is USED despite that: guard asymmetry | `create_image_view`'s descriptorBuffer branch (`memory_allocator.cpp:1424`) checks ONLY the raw `descriptor_buffer_features.descriptorBuffer` — NO `supports_descriptor_buffer_or_heap` check — while the sibling buffer-view path (`:1488`), `sampler.cpp:139`, `descriptor_set.cpp:488/:570`, and `device.cpp:2597/:2686/:4698` ALL check it. `create_default_view` (`device.cpp:3643`) calls in unconditionally |
| 4 | The mismatch is REAL on Odin3 (not hypothetical) | `g27-vkprobe` (§3f): Adreno 830 reports `descriptorBuffer_feature=1` (use-branch RUNS) but `supports_descriptor_buffer=0` (`maxSamplerRange` 128 KiB << 512K×64 B, c1=c2=0) → `MISMATCH=1`. `storageImageDescriptorSize=64` (nonzero — excludes the size-zero alternative, which would write 0 bytes and never overflow) |
| 5 | The store is the driver's 64-byte descriptor write at the aliased pointer | `create_image_view` line 1448: `vkGetDescriptorEXT(…, props.storageImageDescriptorSize=64, view.storage.ptr)`. Slot pointer P = `align64(base+8)` = `0x700` for chunk `[0x6c0,0x708)` (base%64=32 — arithmetic in §3e note). Write covers `[0x700,0x740)`: `[0x700,0x708)` in-chunk (fine), `[0x708,0x710)` = the 8 tail bytes = descriptor bytes 8..15 = payload `10 00 20 00 30 8c 35 00` ✓, `[0x710,0x740)` = 48 bytes into the NEIGHBOR chunk (its header + data) — Scudo's `corrupted chunk header` mechanism, O5/O6's exact detector, firing at whichever free touches that region first (layout-dependent site) |

**WRITER NAMED**: the Adreno driver's `vkGetDescriptorEXT` storage-image
write, invoked at Granite `vulkan/memory_allocator.cpp:1448` in
`DescriptorBufferAllocator::create_image_view`, through a storage-image
slab slot whose stride is 0 because the slab was never initialized
(`init()` early-`true` at `:835-836`, return ignored at `device.cpp:995`),
on a device where the descriptorBuffer feature is on but
`supports_descriptor_buffer` is off (Adreno 830: 128 KiB sampler range).
Victim alloc site on the flag path: `gs_interface.cpp:1725`
(`drawing_kick_update_texture`, between the `:1698` + `:1761` flag gates) ←
`gs_renderer.cpp:1385` (`create_cached_texture`). Class:
heap-buffer-overflow (56 bytes past a 72-byte chunk: 8 in-granule tail +
48 into the neighbor).

§3e note (P arithmetic): chunk base `0x…6c0`, `0x6c0 & 63 = 32`;
fallback `P = ((base + 8 + 63) & ~63) = 0x…700`. Driver writes 64 B at P:
last in-chunk byte `0x707`, tail `[0x708,0x710)` (8 B — the report's
clobbered 8), neighbor `[0x710,0x740)` (48 B). Every number in §3c is
explained. The tag-`08` granule at `[0x700,0x710)` (object tag `59`) is
tabled as observed-but-unexplained — likely secondary heap-metadata damage
from the 48-byte neighbor smash confusing a later malloc; explicitly NOT
load-bearing for links 1–5.

Why the store PC stayed unnamed (tabled per the brief): HWASan tag checks
cannot see in-granule writes by design; only the tail-magic free check
fired. No narrower HWASan scope would catch it live. The scope that WOULD
catch the store PC live is an Android ASan build (8-byte shadow with exact
tail poisoning sees intra-16B overflows) — unneeded now that links 1–5
close the proof without it.

### 3f. Vulkan mismatch probe (NOT a replayer run — device properties query)

`g27-vkprobe.c` (mirrored, 8,752 B, links system libvulkan only) evaluates
Granite's exact guards (`context.cpp:2271-2286`) on the live Adreno 830.
Staged in a re-created `/data/local/tmp/g27/`, run, dir removed after
(`mg/` only ✓). Exit 0, no tombstone:

```text
G27-VKPROBE: ngpu=1
G27-VKPROBE: gpu0 name=Adreno (TM) 830
G27-VKPROBE: descriptorBuffer_feature=1
G27-VKPROBE: samplerDescriptorSize=64 sampledImageDescriptorSize=64 storageImageDescriptorSize=64
G27-VKPROBE: combinedImageSamplerDescriptorSingleArray=1
G27-VKPROBE: maxSamplerRange=131072 maxResourceRange=260046848
G27-VKPROBE: max_heap=131072 c1_sampler512K=0 c2_sampled512K=0 c3_singleArray=1
G27-VKPROBE: supports_descriptor_buffer=0 use_branch_1424=1 MISMATCH=1
G27-VKPROBE: done exit=0
```

Reading: the use-branch condition is true (feature on) while the init
condition is false (128 KiB sampler range << 512K×64 B = 32 MiB) →
`MISMATCH=1`, the exact init/use split links 2–3 require. `c3` passes, so
the failing sub-conditions are c1+c2 (range caps), not singleArray.

### 3g. Tombstone_23 triage (pid 7301 — the sanitizer abort, post-`Done!`)

| slot | fact |
| --- | --- |
| signal | SIGABRT (signal 6, SI_QUEUE); abort message = the §3c HWASan `allocation-tail-overwritten` line (size 72) — NOT Scudo |
| stack | 26 frames: libc `abort` ← `__sanitizer::Abort/Die` ← `ScopedReport` ← `ReportTailOverwritten` ← `HwasanDeallocate` ← `memalign_free` ← slab teardown ← `DescriptorBufferAllocator::~DescriptorBufferAllocator` ← `Device::Managers::~Managers` ← `Device::~Device` ← `main`; pid == tid (main thread); frame-for-frame the §3d free stack under the sanitizer abort prefix |
| timing | post-`Done!` teardown — logcat's last line is `Done!` (15:35:42.727); death after all 10 scanout writes |
| classification | sanitizer detection-at-free in Device teardown (O5's PHASE, DescriptorBufferAllocator sub-site — see §3j) |
| binary identity | tombstone BuildId `52977886…` == G27 binary FULL-match |
| census | `7463…`/`c61f…` ×0; `DescriptorSetAllocator` ×0; `corrupted chunk` ×0; `dispatch_texture_analysis`/`vkCreateComputePipelines` ×0; `libllvm-qgl` ×4 (memory-map lines only — zero in the 26-frame crashing stack: mapped-not-executing); tombstone 182,528 B |

### 3h. O4-absent proof (four legs, G24/G26 §3d shape — flag efficacy holds)

| # | leg | evidence |
| --- | --- | --- |
| 1 | exit/signal differs | 134/SIGABRT via sanitizer abort vs O4's 139/SIGSEGV; full loop + scanouts + `Done!` vs O4's first-draw death |
| 2 | crashing input never exists | crasher pipeline/shader hashes logged 0×; 8/8 Stalled posts `success: yes`, 0 `success: no` |
| 3 | death stack has zero driver-compile frames | tombstone_23: HWASan runtime + slab/destructor frames + `main`; no `dispatch_texture_analysis`, no `libllvm-qgl` execution, no pipeline-build frames |
| 4 | death is post-`Done!` | tombstone after logcat `Done!`; crashing thread is main in `Device` teardown, BuildId `52977886…` == G27 binary |

O4 is absent (4th flag-set run in a row: G24 + G26 + G27 absent at value-1
vs G25 + G23r2 present at value-0/dropped — the bidirectional A/B stands).

### 3i. Score vs G13 oracles (`g14-diff.py`, zero new tooling)

`g14-diff.py ps2x-g13 ps2x-g27` (tool exit 0): oracles **ALL OK** (8/8
pixel-shas); device PPMs: **10** (vsync0–7 + first + last):

| k | exact | \|d\|≤2 | \|d\|≤32 | PSNR R/G/B (dB) |
| --- | --- | --- | --- | --- |
| 1 | 0.0000 | 0.0000 | 0.0000 | 1.9 / 2.4 / 33.1 |
| 2 | 0.0000 | 0.0000 | 0.0000 | 1.1 / 1.5 / 32.3 |
| 3 | 0.0000 | 0.0000 | 0.0000 | 0.4 / 0.8 / 31.2 |
| 4 | 0.0000 | 0.0000 | 0.0000 | 0.5 / 1.2 / 7.7 |
| 5 | 0.0000 | 0.0000 | 0.0000 | 0.5 / 1.2 / 7.7 |
| 6 | 0.0000 | 0.0000 | 0.0000 | 0.3 / 2.3 / 12.8 |
| 7 | 0.0000 | 0.0000 | 0.0000 | 0.3 / 2.3 / 12.8 |

Bright-vs-black adoption read (MADE — first scored run since G22): all 10
device scanouts are pure BLACK (mean 0.0,0.0,0.0, identical pixel-sha
`3d53e321`), vs BRIGHT oracles (means ~200+). G22's no-flag device scanouts
are likewise pure black (mean 0,0,0) — so flag and no-flag agree on-device
(black), and both differ from the bright mac oracles. Hypothesis-level link
(not a verdict): stride-0 slab aliasing makes every storage-image view
overwrite the SAME descriptor memory (last-writer-wins), so all views sample
through one wrong descriptor — a single common cause for black pixels AND
heap corruption, discriminated by the §4 fix brief (bright-after-fix
confirms, black-after-fix refutes).

### 3j. O5/O6 attribution triage (three detection sites, one writer family)

| signature | phase | detector | free-site | status after G27 |
| --- | --- | --- | --- | --- |
| O6 (G24/G26) | pre-first-write (16 ms post-Total) | Scudo `corrupted chunk header` | `DescriptorSetAllocator::clear` ← `wait_idle` ← `save_scanout_ppm` | Scudo signature did NOT reproduce under HWASan (allocator replaced by construction — no Scudo-managed chunk exists to corrupt; no live tag violation fired pre-write either). The §3e writer's 48-byte neighbor smash reproduces O6's EXACT detector+neighborhood (chunk-header corruption surfacing at a descriptor-allocator free) |
| O5 (G22) | post-`Done!` Device teardown | Scudo `corrupted chunk header` | `Device::~Device` ← `PerFrame` ← `vector<CommandPool>` | O5-as-Scudo-signature unobservable under HWASan (same replacement). Same phase as G27's detection, different sub-site — consistent with layout-dependent detection of one writer (G22 ran a different knob/shape, hence a different heap layout) |
| G27 (this brief) | post-`Done!` Device teardown | HWASan `allocation-tail-overwritten` | `Device::~Device` ← `Managers` ← `DescriptorBufferAllocator` slab free | WRITER NAMED (§3e): victim lifecycle + class + exact store, flag-path alloc site |

The numbers support the single-writer-family reading (G26 §3f's three-site
family, now with the writer named): one 56-byte neighbor-smashing store,
three layout-dependent detection sites. Flag-vs-mechanism precision: the
mechanism (uninit slab + driver write) is device-driven, but its
REACHABILITY is flag-driven — no run without the flag ever survived first
draw (O4), so the flag path is the only path that reaches texture-upload +
teardown. G26's implication (flag path) and G27's naming (flag-path alloc
site) agree.

### 3k. Retry + lldb decisions (tabled)

| decision | verdict | rationale |
| --- | --- | --- |
| ONE retry | NOT USED | Brief permits it iff "O1/O3 fires instead of first draw" — first draw was reached, the full loop + scanouts + `Done!` completed; the sanitizer firing IS the discriminating outcome |
| second shape | NOT USED | out of budget by the stop rule (naming closed on the first run — no second shape needed) |
| lldb triage | NOT USED | sanitizer report (§3c verbatim, both stacks symbolized §3d) + tombstone_23 (§3g) fully classify; the residual unknowns (tag-`08` granule, smash-alternative) need a fix-verification run, not post-mortem lldb |

## 4. Hypothesis verdict + the ONE next action

| claim | verdict |
| --- | --- |
| The ONE instrumented WITH-FLAG run names O6's heap-corruption writer (allocation stack + free stack + class at the flag-path site), replacing O6's Scudo signature | **CONFIRMED, decisively.** Sanitizer FIRED (§3c verbatim): full alloc stack through `gs_interface.cpp:1725` (between the flag's `:1698`+`:1761` gates) + full free stack (post-`Done!` Device teardown) + class heap-buffer-overflow (§3d). Scudo replaced (0 `corrupted chunk` anywhere). The exact store is named by the 5-link convergent proof (§3e: stride-0 slab + ignored `init()` early-`true` + guard asymmetry + on-device `MISMATCH=1` + 64-byte driver write at `memory_allocator.cpp:1448`): every number in the report is explained (72 = 64+0+8, P = 0x700, payload = descriptor bytes 8..15, 48-byte neighbor smash = Scudo's detector). O4 absent (§3h — A/B stands). Pixels SCORED: black, matching G22 (§3i). One run, zero source edits, retry + lldb correctly unspent (§3k). |

The ONE next action the numbers justify: **a writer-fix brief — gate
`create_image_view`'s descriptorBuffer branch (`memory_allocator.cpp:1424`)
on `supports_descriptor_buffer_or_heap` (the guard its sibling paths
already carry), or equivalently initialize the slabs unconditionally and
fall back cleanly; then ONE verification run (same dump/iterations, flag
SET) expecting exit 0.** Rationale: the writer is named to a one-line-class
fix shape, and that single run discriminates THREE open questions at once:
(1) O5/O6 gone => single-writer family confirmed (fix brief closes the
identity reading §3j); (2) scanouts bright => aliasing caused the black
(§3i link confirmed) vs still black => black is a separate device trait
(G22's finding stands alone); (3) the G26 narrower hunk becomes the adopted
shape once exit 0 + brightness agree. Queued behind it (not this action):
the Adreno filing — STILL OPEN regardless (submit needs user
identity/tracker; the local root cause does not close it — note the filing
content upgrades from "O4 shader crash" to "named Granite init/use bug +
Adreno's 128 KiB sampler range"); G18-hunk fix adoption (still queued); O1
writer naming (still open); the tag-`08` granule curiosity (§3e note).

No verdicts beyond the hypothesis. No port, no adoption, no upstream contact.

## 5. License / provenance receipts

| artifact | receipt |
| --- | --- |
| paraLLEl-GS rev | `3a66c19…` (LGPL-3.0+ per G7 §4 — cited, not re-read) |
| Granite rev | `16e7395f…` (MIT per G7 §4 — cited); G20 capture hunk compiled in (logging-only, uncommitted, SSD clone only); writer site is Granite framework code (`memory_allocator.cpp:1424-1448`, `:835-836`, `context.cpp:2279-2286`) + NDK fallback branch (`aligned_alloc.cpp:48/:77`) |
| G14 shims S1–S3 + G7/G8/G10/G11/G18/G22/G26 hunks | untouched, still uncommitted in SSD clone only (G22 + G26 HUNK_MATCH re-verified pre-build; ZERO new edits this brief) |
| G27 additions | ZERO clone edits — session files only: `g27-build-hwasan.sh` + `g27-run-hwasan.sh` + `g27-hwasan-probe.c` + `g27-vkprobe.c` (G27-original, text, mirrored) |
| NDK r30 | build + `llvm-readelf`/`llvm-nm`/`llvm-symbolizer` use (Apache-2.0); hwasan runtime + `libc++_shared` are NDK-shipped, pushed to the transient device dir only, removed after |
| logcat/tombstone/scanouts | run receipts of our own binary in SSD `ps2x-g27/` ONLY (not in git); no PII (`uid: 2000` shell) |
| adoption hunks | NONE — no third-party code copied into any project tree this brief |

## 6. Exact commands

Mac (`/Users/bradrichardson/dev/ssx3` unless noted;
`COPYFILE_DISABLE=1` on SSD steps; `SSD="/Volumes/Extreme SSD"`):

```text
git -C $SSD/parallel-gs-g7 rev-parse HEAD ; status --short ; diff --stat  # §2a
git -C $SSD/parallel-gs-g7 diff gs/gs_renderer.cpp | diff local/research/G22/g22-workaround.diff -  # HUNK_MATCH
git -C $SSD/parallel-gs-g7 diff tools/gs_dump_replayer.cpp | grep -A15 '93,9 +96,15'  # vs g26-narrowing.diff: HUNK_MATCH
shasum -a 256 <g26-binary> ; xxd -l 16 <g26-binary>             # §2a 5th zero-damage confirm (ae1bc63a…, zeros)
shasum -a 256 $SSD/ps2x-g13/g13-dump.gs                         # 154d9d85… full-match
du -sk <ps2x-g10..g27 + 9 build dirs> ; df -h / $SSD           # §0 (pre + post)
clang --target=aarch64-linux-android35 -fsanitize=hwaddress ... /tmp/g27-hwasan-probe.c -o /tmp/g27-hwasan-probe  # §2c exit 0
llvm-readelf --dynamic /tmp/g27-hwasan-probe | grep NEEDED      # hwasan runtime
cmake -S <clone> -B <g27-build> -G Ninja -DCMAKE_TOOLCHAIN_FILE=... -DANDROID_ABI=arm64-v8a -DANDROID_PLATFORM=android-35 -DANDROID_STL=c++_shared "-DCMAKE_C_FLAGS=..." "-DCMAKE_CXX_FLAGS=..." -DCMAKE_EXE_LINKER_FLAGS="-fsanitize=hwaddress"  # §2d exit 0 (see g27-build-hwasan.sh)
cmake --build <g27-build> --target parallel-gs-replayer -j2    # §2d exit 0 [458/458], pre-existing warnings
shasum -a 256 <g27-binary> (build, pre-push, report×2)          # 6387d2f3… ×2 match, then 13d2fc69… destroyed
llvm-readelf --notes <g27-binary> ; strings grep ×1/×2/×0 ; llvm-nm grep -c __hwasan (=164) ; xxd -l 4  # 52977886… + ELF
llvm-symbolizer --exe=<g27-binary> --inlining=false -f -C <36 offsets>  # §3d both stacks
python3 local/research/G14/g14-diff.py $SSD/ps2x-g13 $SSD/ps2x-g27  # §3i
grep -c Running/G10/success/crasher/G26/G22 <logcat> ; census <tombstone>  # §3 census
clang --target=aarch64-linux-android35 /tmp/g27-vkprobe.c -o /tmp/g27-vkprobe -lvulkan -llog  # §3f exit 0
```

adb (`-s 622c49b1` throughout; `/data/local/tmp/g27/` ONLY; `mg/` never touched):

```text
shell 'ls /data/local/tmp/ ; ls -lt /data/tombstones/ | head ; df -h /data | tail -1'  # pre-check (mg/ only, _20 newest, 29G)
shell 'rm -rf /data/local/tmp/g27 && mkdir -p /data/local/tmp/g27'
push /tmp/g27-hwasan-probe $G27DIR/probe ; push <ndk-hwasan-rt> $G27DIR/  # §2c probe stage
shell 'sha256sum probe libclang_rt.hwasan-aarch64-android.so'  # both FULL-match host
shell 'LD_LIBRARY_PATH=$G27DIR ./probe; echo PROBE_CLEAN_EXIT=$?'       # 0 (§2c)
shell 'LD_LIBRARY_PATH=$G27DIR ./probe fault; echo PROBE_FAULT_EXIT=$?' # 134 + tag-mismatch report (§2c)
push <dump> $G27DIR/g13-dump.gs ; push <g27-binary> $G27DIR/hwasan-replayer ; push <libc++_shared> <hwasan-rt>  # §2e
shell 'sha256sum g13-dump.gs hwasan-replayer libc++_shared.so libclang_rt.hwasan-aarch64-android.so'  # 4/4 FULL-match (§2e)
logcat -c ; logcat -d -s Granite:V | tail -2                         # before (empty)
shell 'cd $G27DIR && date +%s; PGS_SKIP_COMPILATION_TASKS=1 HWASAN_OPTIONS=halt_on_error=1 LD_LIBRARY_PATH=$G27DIR timeout -s KILL 280 ./hwasan-replayer $G27DIR/g13-dump.gs --iterations 2 --disable-sampler-feedback > g27-run-stdout.txt 2> g27-run-stderr.txt; echo RUN_EXIT=$?; date +%s'  # 134 (HWASan fired)
logcat -d -s Granite:V > $SSD/ps2x-g27/g27-logcat.txt                # 1804 lines
pull $G27DIR/g27-run-stderr.txt $SSD/ps2x-g27/ (8050 B) ; pull stdout (0 B)
shell 'ls -la $G27DIR/ ; ls -lt /data/tombstones/ | head -6'         # 10 scanouts; _23 new 15:35
pull /data/tombstones/tombstone_23 $SSD/ps2x-g27/g27-tombstone-23.txt
pull $G27DIR/*.ppm $SSD/ps2x-g27/ (10 files)
shell 'rm -rf /data/local/tmp/g27 && ls /data/local/tmp/'            # DEVICE_CLEAN (mg/ only)
shell 'mkdir -p /data/local/tmp/g27' ; push /tmp/g27-vkprobe $G27DIR/vkprobe ; shell './vkprobe'  # §3f MISMATCH=1, exit 0
shell 'rm -rf /data/local/tmp/g27 && ls /data/local/tmp/'            # DEVICE_CLEAN again (mg/ only)
```

## 7. Gaps (what this brief could not do)

1. The store PC was not captured LIVE (HWASan `Stack of invalid access
   unknown` — in-granule writes are invisible to tag checks by design).
   The store is instead named by the 5-link convergent proof (§3e); an
   Android ASan run would capture the PC live but is unneeded for naming.
2. The tag-`08` granule at `[0x700,0x710)` (object tag `59`) is unexplained
   (working note: secondary heap-metadata damage from the 48-byte neighbor
   smash); explicitly non-load-bearing for §3e links 1–5.
3. The `posix_memalign`-absence `nm` check (4th fallback-path leg) is VOID —
   it ran against the already-zero-destroyed binary (§2e #4); fallback
   execution stands on DWARF alloc line `:48` + free line `:77` + the
   72=64+0+8 size math. No rebuild was spent on it (one-build budget).
4. Which dynamic view-creation instance FIRST smashed is unnamed
   (immaterial — all slots alias one address, every storage-image
   `vkGetDescriptorEXT` writes the same memory).
5. The black-pixels⇐aliasing link (§3i) is hypothesis-level, discriminated
   by the §4 fix brief (bright-after-fix confirms).
6. O6-identity beyond the single-writer-family reading (§3j) is hypothesis-
   level, discriminated by the same fix brief (O6-gone confirms).
7. No lldb (decision tabled §3k); OS tombstone store otherwise untouched
   (_21/_22 probe + _23 flag run remain, auto-rotated). `upstream/` +
   harness code untouched; no new dumps; run budget 1/2 spent (retry
   intentionally unspent — no retry condition fired).
8. The zero-destroyed G27 binary was left destroyed (run already complete
   and valid; rebuilding a receipt binary is out of scope). 6th recurrence
   overall (5th was the G26 binary, §2a).
9. The Adreno filing is still open and unfiled (needs user identity /
   tracker — unchanged owner; content upgrades per §4).
10. O1 writer, G18-hunk adoption, G17 filing: unchanged / queued.

## 8. Receipt paths

- SSD receipts: `/Volumes/Extreme SSD/ps2x-g27/` (13 files: `g27-logcat.txt`
  1804 lines, `g27-run-stderr.txt` 8,050 B, `g27-run-stdout.txt` 0 B,
  `g27-tombstone-23.txt` 182,528 B, 10 PPMs × 688,143 B) +
  `parallel-gs-g27-hwasan-build/` (binary 289,112,232 B `6387d2f3…`
  BuildID `52977886…` at push time; zero-destroyed at report time).
- SSD receipts (read-only, 0 growth): `ps2x-g10/`-`ps2x-g26/` + G14/G15/G16/
  G18/G20/G22/G24/G26 build dirs + SSD clone (HEAD `3a66c19…`, G22 + G26
  hunks uncommitted — ZERO new edits).
- Session-only: `/tmp/g27-hwasan-probe.c`, `/tmp/g27-hwasan-probe`,
  `/tmp/g27-vkprobe.c`, `/tmp/g27-vkprobe`, `/tmp/g27-g26block.txt`,
  `/tmp/g27-wt-block.txt` (~120 KB; sources mirrored in git).
- Commits: ssx3 `local/research/G27/` `[G27]` + `Orchestrated-By: Muse Code`
  trailer (NOT pushed); ps2xGS untouched (zero commits — no source edits).

TAIL-RECEIPT: G27 report ends here. HWASan chosen + probed, one build exit
0, ONE flag run exit 134 with the sanitizer FIRING (alloc-tail-overwritten,
size 72, full lifecycle at gs_interface.cpp:1725), writer NAMED (stride-0
slab + vkGetDescriptorEXT@memory_allocator.cpp:1448, MISMATCH=1 on Adreno
830), 10 black scanouts + Done!, O4 absent, writer-fix brief next, filing
still open.



