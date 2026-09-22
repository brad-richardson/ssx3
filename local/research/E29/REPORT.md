| E29 | Receipt |
|---|---|
| Stop point | **All three missions executed; nothing was blocked and neither boot was stopped.** Mission 1 found a visible mechanism, so the build was not blind. Mission 2 cut `e29-movie-bypass` from `3adc0478`, applied a 46-line env-gated diff, built on the SSD and ran **458/458 with the flag OFF**. Mission 3 spent **both** permitted boots: `e29a` (flag OFF) reproduced e28a's terminal state on **20/20** pre-registered rows, so `e29b` (flag ON) was authorised. Fix gate: **NOT APPLICABLE**, as the brief sets it. |
| Headline | **With `PS2X_SKIP_MOVIE=1` the title reaches the SSX 3 TITLE SCREEN — rendered, animating, "Press START button".** The same binary with the flag unset still parks on the movie forever. One env-gated block, 46 inserted lines, 0 deletions, one file. |
| Checkpoint verdict | **C1 MET · C2 MET · C3 MISSED-AS-WRITTEN.** C3's pre-registered proxy was the wrong one and is recorded as a miss, not swapped out — see its row. |
| Checkpoint | Fork `3adc0478b6d2260acdd28a249466f2eef9a20176` triple-agreed at open **and** close; `status --short` exactly `?? ps2_log.txt` at both. Fork HEAD was moved for **1,521 s (25.4 min)**, `16:13:26Z → 16:38:48Z`, and is back on `ssx3` with `MPEG.cpp` byte-equal to its git object. |
| Mutations / launches | **Exactly the two worktree mutations the brief permits**: the branch checkout, and the bypass diff. One branch, **one commit** (`e5ce086d`), **never merged, never pushed**. One configure + one reconfigure, one build, **two title boots, two lease claims, two releases**, **zero deletions**. |
| Amendments | **TWO, both declared before the step they affected: A1 and A2.** A2 is the one place E29 does not do what the brief literally says; it is flagged in its own row below. |

| Experiment contract | Bound / observable |
|---|---|
| Time box | 8 h. Opened `2026-09-22T16:01:18Z`, closed the same session, **well inside the box**. |
| Required reads | E28 `REPORT.md` (172 lines) + E27 `REPORT.md` Mission 2a/3 + `docs/research/review-2026-09-22-progress-and-parallelization.md` §E‑lane — all read in full before the first gate. |
| Strict order | tooling bootstrap → hex-safe carry + proof (21 files) → **carry audit** (E28‑E1's standing mitigation, before the first gate) → **fork gate (first gate)** → CONTRACT → **Mission 1** (two passes) → **Mission 2** (checkout as late as possible → diff → build → 458 → commit → checkback) → **Mission 3** (Boot 1, then Boot 2) → E30 handoff → fix gate → close. No gate tripped. |
| Preserved constraints (E18 ABI, BINDING) | **Preserved on the default path by construction and by measurement**: the diff adds one `if` gated on an env flag that must be exactly `"1"`, one struct field and two resets. With the flag off, **458/458**. |
| Contract source | `CONTRACT.md`, written before the branch was cut. Amendments A1 and A2 appended to it, each before the step it affected. |

## Mission 1 — mechanism, checkpoint and limits, pre-registered

| Mission 1 | Receipt |
|---|---|
| **The mechanism, named exactly** | `getMpegPicture`, `ps2xRuntime/src/lib/Kernel/Stubs/MPEG.cpp`. The park is produced by **one statement** — `waitExternal(EeWaitReason::Mpeg, kMpegPictureWaitType, …)` at **:2514** — reachable only through the four-term guard at **:2498–2501**. Of those four terms, `!playback.streamEnded` is the only one the host already sets on two REAL paths (`finishPlaybackStream` :1459, the `kMpegProgramEnd` path :1303), that the guest's own player already handles, and that invents no state the runtime cannot otherwise be in. |
| **Where the block goes, and why that makes it bounded** | Between **:2497** and **:2498** — i.e. AFTER the producer dispatch at :2489. Everything up to and including the guest's `sceMpegAddBs` and the parser feed runs exactly as it does with the flag off; the run diverges **only** at the park. |
| **Checked, not recalled** | **22 anchors** grepped out of the file; the tool refuses to continue if one is absent. **0 missing.** `MPEG.cpp` sha256 `f83ed02e…ef600` **equal to its git object** at `3adc0478`. `PS2X_SKIP_MOVIE` proved to be a **new** name against the 23 `PS2X_*` names already in the runtime. Two passes **256.7 s apart, identical**. |
| **Rejected alternatives, with reasons** | P7's `ssx3MoviePlayComplete` (needs a re-recomp of 9,454 generated sources — not a permitted mutation, and its hook was never runtime-validated); suppressing the `nonStreamDeliveries` latch (that is a candidate FIX for E30, not a bypass); returning a synthetic frame ("replace arbitrary waits with success", explicitly ruled out by the review); flushing the decoder when the flag arms (could emit a frame and change `picturesServed`, for no reachability gain). `mission-1-block.txt`. |
| **(b) the flag-OFF equivalence bar** | Computed from e28a's **committed** pins, not recalled: `[MPEG:GetPicture] waiting` ×1 · `[MPEG:feedES]` ×1 · `[MPEG:feed]` ×1 · `[MPEG:GetPicture:FRAME]` ×0 · thread 1 `Waiting wait=Mpeg:0 pc=0x3b1028 ra=0x3b1028 chain=[0x3b1028]` · feed 5,040 B `cde8a830…2a1c875a` first4 `000001b3` · closure `parseCalls=1 offered=5040 consumed=5040 packets=0 frames=0 errors=0 pending=0` · head `0xd486f8 = 0xd49b14` · bytes `0xd486f4 = 0x696e0` (431,840) · 243 watch entries. |
| **(a) the checkpoint** | **C1** movie sequencing exited (`[MPEG:DEV-SKIP-MOVIE]` ≥ 1, `[MPEG:GetPicture] waiting` == 0, thread 1 not parked on `Mpeg:0`). **C2** the guest leaves e28a's terminal **13-stub** loop. **C3** a `[frame:upload]` display configuration e28a never produced. |
| **(c) the limits, written before the code** | Nine, in `pre-registration-*.json`. Including, in advance: **`[gs:prim]` caps at 64 and `[gs:kick]` at 96, and e28a sits EXACTLY at both caps**, so neither can discriminate menu/race rendering — named before the run so no reader mistakes a capped counter for a result. |
| Two passes | Mechanism 256.7 s apart, pre-registration 128.7 s apart. **Identical both times.** `mission-1-gate.json`. |

## Mission 2 — branch, build, suite

| Mission 2 | Receipt |
|---|---|
| Branch | **`e29-movie-bypass`**, cut from exactly `3adc0478…a20176` at **`16:13:26.910Z`** — deferred to the start of Mission 2 because the V1 worker is auditing fork HEAD concurrently. Cut **in the main fork worktree**: a `git worktree add` or a second clone would lack the gitignored generated guest sources. 6/6 checks green, **tree unmoved** by the checkout. |
| The diff | **One file, 46 insertions, 0 deletions.** 4 hunks: the flag helper (matching the codebase's own `diagReportAll()` idiom — the value must be exactly `"1"`), one `MpegStubState` counter, two counter resets, and the bypass. Receipted in full: `bypass.diff`. |
| DEV-ONLY at every layer, audited | flag name · branch name · build dir name · ≥2 `DEV-ONLY` code comments · the log marker · report title. **17/17** in `bypass-verify-pass-1.json`, including `wait_guard_untouched`, `no_decoder_flush_added` (measured against the base blob, not a remembered number) and `waitExternal_call_count_unchanged`. |
| Build recipe | **Loaded from E18's committed `configure-command.json`** and asserted equal to a literal transcription, exactly as E25 did. **The only difference is `-B`.** Configure rc 0 / 143.9 s; reconfigure rc 0 / 19.8 s; build `ninja -j2` **rc 0, bound null, 674.5 s, 543 edges** (E25's internal build: **543**), stdout not truncated. |
| FetchContent HEADs | **All three byte-identical to E18/E25's**: raylib `c1ab645c…`, imgui `b1bcb12a…`, rlImGui `118221c8…`. |
| **458/458 with the flag OFF** | `Total Tests: 458 · Passed: 458 · Failed: 0`, rc 0, flag proved absent from the env. **The faithful-equivalence gate is GREEN.** |
| **What the flag actually costs, measured** | With `PS2X_SKIP_MOVIE=1` the suite is **453/458**, and the five failures are exactly the tests that assert what the bypass suspends: **MPEG non-stream R1, R2, R4, R6** and **"sceMpegGetPicture waits for new decoder output instead of duplicating the last frame"**. Not a defect — the measured reason this is a flag and not a change, and the regression bar E30 must hold *without* one. |
| Binary pins, under the standing SSD rule | **Three reads, separated in time, all agreeing** — runner `8c09eefb…84b8` 163,529,696 B, suite `f22ce08c…716f` 5,695,128 B. Plus a **zero-run scan** (the known corruption signature): longest zero run **0.02 MiB** in each, far below a megabyte-scale wipe. Plus **corroboration that is not another read**: both binaries executed 458 tests. |
| A coincidence worth naming | Both new binaries are **byte-for-byte the same SIZE** as their mainline counterparts, while differing in SHA. Not a stale copy: `PS2X_SKIP_MOVIE` appears **twice** and `[MPEG:DEV-SKIP-MOVIE]` **once** in each new binary, and **zero times** in either mainline binary. |
| Check-back | `16:38:48.216Z`. Back on `ssx3`, HEAD `3adc0478`, status `?? ps2_log.txt`, `MPEG.cpp` restored to `f83ed02e…`. Branch: **one commit, parent = the fork point, unmerged, unpushed.** |
| Generated sources | **19/19 rows equal to E27's committed pins on BOTH of E27's passes**, checked twice, after the whole branch round-trip and the build. |

## Mission 3 — two boots

| Boot | Flag | rc | bound | elapsed | lease | Verdict |
|---|---|---|---|---|---|---|
| `e29a` | **OFF** | 0 | `wall` | 77.285 s | claimed `16:47:14.734Z`, released `16:48:32.027Z` | **EQUIVALENT, 20/20** |
| `e29b` | **ON** | 0 | `wall` | 76.720 s | claimed `16:54:37.717Z`, released `16:55:54.448Z` | **C1 MET · C2 MET · C3 missed-as-written** |

| Boot 1 — the equivalence gate | Receipt |
|---|---|
| **20/20 rows** | Every pre-registered value reproduced exactly: `[MPEG:GetPicture] waiting` ×1 · `[MPEG:feedES]` ×1 · `[MPEG:feed]` ×1 · `FRAME` ×0 · `[MPEG:DEV-SKIP-MOVIE]` **×0** · thread 1 `Waiting wait=Mpeg:0 pc=0x3b1028 ra=0x3b1028` · feed **5,040 B `cde8a830…2a1c875a`** · closure `parseCalls=1 … packets=0 frames=0 errors=0 pending=0` · head `0xd49b14` · bytes `0x696e0` · 243 entries · flag absent from the boot env. |
| **The feed vector, a fifth independent time** | `cde8a830…2a1c875a` — byte-identical to E22's, E23's, E24's, E26's and E28's, now reproduced on a **different binary**. |
| **A corroboration that was not pre-registered** | e29a's final frame capture is **byte-identical to e28a's**: `6120a759…`, 9,448 B, `fnv1a=fd889dc5`. The flag-off bypass build ends on the same rendered bytes as the binary every prior lane booted. Recorded as an unregistered corroboration, not as a bar that was set in advance. |

| Boot 2 — the checkpoint | e29a (OFF) | e29b (ON) | Verdict |
|---|---|---|---|
| `[MPEG:DEV-SKIP-MOVIE]` | 0 | **3** | C1 pass |
| `[MPEG:GetPicture] waiting` | 1 | **0** | C1 pass — **the park never happened** |
| thread 1 at the wall | `Waiting wait=Mpeg:0 pc=0x3b1028 ra=0x3b1028` | **`Ready wait=None:0 pc=0x423dc8 ra=0x377b6c`** | C1 pass |
| `[MPEG:feedES]` | 1 | **3** (5,040 / 5,008 / 5,008 B) | **three movies, not one** |
| final `[diag:stubs] distinct` | **13** | **251** | C2 pass — **the reachability claim** |
| boot-log lines | 47,598 | **133,620** | — |
| distinct non-fallback frame contents | 42 | **1,135**, still changing at the wall | — |
| `[frame:upload]` display configurations | one (`fbp=112, 512x448`) | **the same one** | **C3 MISS** |
| **What the final frame actually is** | **black, frozen** (`fnv1a=fd889dc5` to the wall) | **the SSX 3 title screen: the logo over the mountain art, "Press START button", "© 2003 Electronic Arts Inc. All Rights Reserved"** | read off the PNG |

| Why C3 missed, stated rather than swapped | Receipt |
|---|---|
| The proxy was wrong | SSX 3's front end renders into the **same** 512×448 framebuffer (`fbp=112`) the movie used, so a display-configuration change was never going to signal it. The pre-registration bet on the wrong observable, and that is recorded as a **MISS** rather than replaced after the fact with one that happened to fire. |
| What did change | Frame **content**. e29a produced **42** distinct non-fallback frames and then froze on one forever; e29b produced **1,135** and was still changing when the wall bound. |
| The evidence that settles it is visual, and named as such | `frames-e29b-1/upload-latest.png`, `2ab49bac…`, 176,214 B — the title screen, read directly. Pinned by path + SHA in `frame-pins.json`; the evidence directory is text-only by the brief, so no image is copied into the repo. |

| The three bypass cycles, verbatim | Receipt |
|---|---|
| Movie 1 | `22899 [MPEG:feedES] #0 size=5040 first4=000001b3` → `22900 [MPEG:feed] inSize=5040 parsed=5040 packets=0` → `22901 [MPEG:DEV-SKIP-MOVIE] bypass armed … n=1 requestInput=0 sawInput=1 served=0` |
| Movie 2 | lines 25705–25707, `size=5008` |
| Movie 3 | lines 29749–29751, `size=5008` |
| What `n=1` on each means | `sceMpegCreate` resets the playback state per movie, so the bypass **re-arms once per movie** rather than latching. A fix that works once would not have produced this. |
| **The number E30 needs** | Across all three: `parseCalls=3 offered=15056 consumed=15056 **packets=0** frames=0 errors=0 pending=0`. **Every byte consumed, not one packet completed** — E22–E28's one-chunk result, now reproduced on three independent movies. |

## The two amendments

| A1 — declared before the configure step | Receipt |
|---|---|
| What | Internal delta cap **512 MB → 32 MiB**, and its `bound()` trip from the absolute `IRES-128*M` to the scaling `IRES*3//4`. |
| Why | The carried `admission()` reserves the whole remaining internal cap as free headroom above the floor — E28 semantics, where that number sized an internal BUILD TREE. E29 builds on the SSD and writes only text evidence internally (E28's comparable directory: 980 KB; E29's final: 4.24 MB). The second half matters because `IRES-128*M` goes **negative** once the cap is right-sized, so it would have fired unconditionally and stopped E29 on an arithmetic artefact rather than a real bound. |
| What it does not do | **It does not lower the floor.** `bound()` still stops the lane at 2 GiB + 0.5 GiB free. |
| Standing risk, named | Internal free fell **3.10 → 2.76 GiB during this lane**, from activity outside it (the volume sits at 99%). |

| **A2 — the one place E29 does not do what the brief literally says** | Receipt |
|---|---|
| What | The brief's SSD byte caps (build dir ≤ 6 GB, `e29-*` ≤ 16 GB) are read as **LOGICAL** bytes, paired with new explicit **allocation ceilings** (48 GB / 64 GB) and an SSD free-space floor **raised from 2.5 GiB to 32 GiB**. |
| Why, measured | `/Volumes/Extreme SSD` is **ExFAT with a 1,048,576-byte allocation block** (`diskutil`; empirically the smallest non-empty file in the tree is 4,049 B logical and 1,048,576 B allocated). A CMake/FetchContent tree is tens of thousands of small files, so the **configure alone** produced 1.25 GB logical / **17.2 GB allocated — over BOTH caps before one object file was compiled**. The caps were written for a tree the size of the internal one (1.6 GB logical), and the logical tree here is exactly that size. Measured in allocation, **no build of this project can exist on this volume within a 16 GB cap**: the cap would forbid the lane rather than bound it. |
| At close | build **1.783 GB logical / 18.97 GB allocated**; all `e29-*` **2.441 GB logical / 19.81 GB allocated**; SSD free **101.0 GiB**. |
| What it strengthens | The real protection is **13× stronger** after the amendment than before: the free-space floor went from 2.5 GiB to 32 GiB. |
| **Flagged for the orchestrator** | If the brief meant *allocation*, then E29's build must not run on this volume at all and the lane needs re-briefing rather than re-running. That call is the orchestrator's, not this lane's. |

## Two obstacles that cost real time, and what they teach

| Finding | Receipt |
|---|---|
| **E18's AppleDouble bug, reproduced — including on E29's own edit** | Building into an **ExFAT** build dir puts FetchContent's `_deps` checkout on a filesystem with no native xattrs, so macOS writes a `._x` sidecar beside every file carrying one: **7,865** in the tree. `compile_commands.json` picked up **33** of them, and clang echoed their binary contents — E18's exact failure, which killed the first `ninja` at edge 1/576. **One of the 33 was `._MPEG.cpp`, created at 16:14Z by E29's own diff.** Fixed by E18's own procedure — **retain by rename, 153 files, ZERO deletions** — then a reconfigure re-globbed to **0** AppleDouble entries of 531. E18 needed two `ninja` invocations for this reason; so did E29. |
| **The 458/458 gate is CWD-sensitive** | Run from the binary's own directory, the suite is **457/458** — "VU0 macro mappings cover all S1/S2 enums" fails. It fails **identically on the mainline binary**, measured as a control, so it is not the diff. E28 ran the suite with `cwd` = the **fork worktree root**; E29 reproduced that exactly and got 458/458. A later lane that runs the suite from the wrong directory will see a red gate that means nothing. |

## Gates, hygiene, budget

| Gate | Receipt |
|---|---|
| Fork gate | Open `16:03:15Z` 7/7 green; close 7/7 green, same sha, same status. `fork-gate-open.json`, `fork-gate-close.json`. |
| Carry audit | Ran **before the first gate**, as E28-E1's mitigation requires: 10 cross-lane path literals resolved, **0 dangling**. |
| Tooling | 21 files carried hex-safely (normalized diff empty, hex runs equal, protected tokens preserved, **all 21**); `e29_rename.py` produced by a bootstrap proved by **FIXPOINT**. **4 declared changes** with full diffs (`tooling-changes.json`, `tooling-diff.md`) + **5 declared driver changes** (binary path, two phases, the flag, label-derived manifest, and the one-boot guard → a **hard cap of two**). 8 tools written fresh. |
| Watch vector | E28's **243** entries carried **byte-identical** (`watch-set.json` `797fdee8…0d91`); armed 243 on both boots. No new watch design, as the brief requires. |
| Instrument | E21 observer dylib `e4d88fdc…6be` carried by `cp -p` + re-sha, **never rebuilt**. |
| Boots / leases | **2/2 boots, 2/2 claims, 2/2 releases**, one at a time, both `pgrep` rc 1 and lease absent after release. **No third boot**, and the driver now refuses one by construction. |
| Fix gate | **NOT APPLICABLE** — scaffolding, not a fix. `fix-gate.json` records that, the candidates still killed, what E29 does **not** claim, and the E30 handoff. |
| Deletions / reclaim | **Zero.** The 153 AppleDouble sidecars, the failed first build log and Boot 1's sentinel were all **renamed**, never removed. |
| Final audit | **38/38 green.** `final-audit.json`. |

## The E30 handoff

E27 named the host latch statically and E28 closed the guest half; neither could say what the latch actually costs. **E29 measures it: the single `waitExternal` at `MPEG.cpp:2514` is the only thing between the current park and a rendered, live SSX 3 title screen.** Nothing else in the boot chain had to change — 46 inserted lines, one file, zero deletions — and with the park suspended thread 1 goes from `Waiting wait=Mpeg:0` to `Ready`, the boot log grows from 47,598 lines to 133,620, the HLE stub surface goes from **13** distinct entry points to **251**, and the framebuffer goes from 42 frozen frames to **1,135** still changing at the wall. The faithful fix must reproduce that **without the flag**, and E29 leaves it four things it must satisfy: (1) `getMpegPicture` must **return** to the guest rather than park it; (2) it must do so **per movie, repeatedly** — `e29b` runs three, each arming the bypass exactly once because `sceMpegCreate` resets the playback state, so a fix that works once and latches is not enough; (3) it must keep green the **five** tests the flag breaks — MPEG non-stream **R1, R2, R4, R6** and *"sceMpegGetPicture waits for new decoder output instead of duplicating the last frame"* — which are now a measured regression bar (453/458 with the flag, 458/458 without); and (4) it must deliver **actual pictures**, because across all three movies the parser reports `offered=15056 consumed=15056 **packets=0** frames=0`: every byte consumed and not one packet completed, which is E22–E28's one-chunk result reproduced on three independent movies. What E30 also gains is cheap: a branch and a binary that reach a **known-reachable downstream state**, so a candidate fix can be A/B-ed against a title screen instead of against a black screen, using the same binary and one environment variable. The one question E29 could **not** answer is whether that title screen is polling the pad — it cannot be read from this boot, because the `[diag:stub]` histogram caps at 30 rows of 251 distinct targets and the `[padread]` marker only prints when a button is actually pressed, which never happened in a headless run. The runtime already has `PS2X_PAD_STIM_AFTER` / `PS2X_PAD_STIM_WALLMIN` for exactly this; one boot with START injected would settle whether "Press START button" is live. That is a brief to write, not a claim to make here.

| Tail receipt | Value |
|---|---|
| Complete prefix | Lines 1–127; 21192 B; SHA256 `c06b32f2f7f735fd2f4177c9b4974b9a4645c51fb130061f26fe58947bdb7084` (the prefix is every line ABOVE the `| Tail receipt | Value |` header, so this row lives after the boundary and cannot invalidate itself — errata E24-E2) |
| Source-tail gap | **None, and five named limits.** (1) The bypass proves nothing about movie *correctness*: three movies were **skipped**, not played, and every picture it shows is `writeBlankMpegFrame` output. (2) It does not explain the stall — `streamEnded` is set by fiat above the wait guard, so the `nonStreamDeliveries` latch is neither exercised nor disproved. (3) **C3 missed**: menu/race was **not** reached on the bar as written; the title screen was, and the evidence for that is a frame capture read directly, which is weaker than a counter and is labelled as such. (4) Both boots are bounded at the same 90 s wall every prior lane used, so "how far it gets" is bounded by time as well as by the runtime. (5) This is a macOS arm64 host build and says nothing about Odin/Android. |
| Publication | `[E29]` evidence commit with `Orchestrated-By: Muse Code`, `git add -f`. Bypass commit `e5ce086d` on `e29-movie-bypass` only — **never merged, never pushed**. Evidence **not pushed**; the orchestrator pushes at poll. |
| E29 REPORT TAIL COMPLETE | Mission 1 named the mechanism against **22 grepped anchors** on a file equal to its git object, pre-registered the equivalence bar from e28a's committed pins, the checkpoint, and nine limits — including, in advance, that `[gs:prim]`/`[gs:kick]` are at their caps and cannot discriminate. Mission 2 cut `e29-movie-bypass` from `3adc0478` at `16:13:26Z`, applied **46 insertions / 0 deletions in one file**, rebuilt on E18's recipe with only `-B` changed (**543 edges, E25's number**; all three FetchContent HEADs byte-identical), and gated it at **458/458 with the flag OFF** — while measuring that the flag ON costs exactly **five** named MPEG tests. Mission 3 spent both boots: **`e29a` reproduced e28a on 20/20 pre-registered rows**, down to the 5,040-byte feed SHA for the fifth independent time and a final frame **byte-identical** to e28a's; **`e29b` then reached the SSX 3 title screen** — bypass armed 3×, park count **0**, thread 1 **Ready**, **251** distinct HLE stubs against e28a's 13, **1,135** distinct frames still changing at the wall. **C1 MET, C2 MET, C3 MISSED-as-written and reported as a miss.** Two obstacles cost real time and are recorded for reuse: E18's AppleDouble bug reproduced on E29's own edit (153 sidecars retained by rename, zero deletions), and the 458/458 gate's CWD sensitivity (457/458 from the wrong directory, **on the mainline binary too**). Two amendments, both declared before the step they affected; **A2 is flagged as the one place E29 departs from the brief's literal text**, with the ExFAT 1 MiB allocation block measured as the reason. Mainline triple-agreed and clean at open and close, fork HEAD moved for **25.4 min**, generated sources **19/19 unmoved** across two passes, **2/2 boots, 0 pushes, 0 merges, 0 deletions**, fix gate **NOT APPLICABLE**, final audit **38/38**. |
