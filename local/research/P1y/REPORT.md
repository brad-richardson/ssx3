# P1y — Flaky ps2xTest pair (AFAIL↔GsSyncV): reproduction, isolation, fix

Standalone evidence dir (does not append to `P1/REPORT.md`; a peer brief owns it).
Suite binary `ps2x_tests`, CWD = fork root for every run below.

## 1. Reproduction table (pre-fix, own clone + own build dir)

Fork clone `/Volumes/Extreme SSD/ps2x-p1y/fork` @ `5b5ac3d`
(`Config: track SSX3 game config (P24-1)`); build dir
`/Volumes/Extreme SSD/ps2x-p1y/build` (never `/tmp/p1-link`).
Configure: `cmake -S fork -B build -G Ninja -DCMAKE_BUILD_TYPE=Release
-DPS2X_BUILD_TEST=ON -DPS2X_ENABLE_RUNTIME_LOGS=ON`; build
`cmake --build build --target ps2x_tests -j4`.

| Build | Binary sha256 (short) | Runs | Result every run |
|---|---|---|---|
| build1 (fresh clone) | `085861b4…` | run1–run5 | 426 total / 425 pass / 1 fail: `sceGsSyncVCallback runs as a scheduler invocation on its callback stack` (`callback invocation should use the reserved async stack pool`) |
| build2 (full `rm -rf build`, reconfigure, rebuild) | `085861b4…` (bit-identical to build1) | run6–run10 | same 426/425/1, same test, same assertion |

10/10 runs GsSyncV face. The AFAIL face did not reproduce in any configuration
tried (§4).

## 2. Isolation evidence

Temporary local-only probes (env filter in `MiniTest.h` + `cbSp` print in the
GsSyncV test; both reverted with `git checkout --` before the fix; tree verified
clean). Probe binary built incrementally from build2.

| Probe | Filter | Result |
|---|---|---|
| B1: AFAIL test alone | `AFAIL independently` | 1/1/0 PASS |
| B2: GsSyncV test alone | `sceGsSyncVCallback runs` | 1/0/1 FAIL, `[p1y-probe] cbSp=0xffff0 cbGp=0x36a7f0 hits=1 tick=1 prev=0x0` |
| B3: PS2GS suite only | `PS2GS/` | 71/70/1, sole failure = GsSyncV test |

Both tests behave identically alone, in-subset, and in-suite: no order/state
dependence on this tree. The GsSyncV failure needs no other test to trigger.

Observed values (B2): callback ran once (`hits=1`), positive tick, GP preserved,
`prev=0` — the ONLY wrong value is `sp=0xffff0` vs asserted `>= 0x01F00000`.

## 3. Root-cause call: stale test expectation, not a product bug

| # | Evidence |
|---|---|
| 1 | `f4309cd` (#184) introduced the test with `sp >= 0x01F00000u` when `reserveAsyncCallbackStack` allocated from the RAM top (`m_asyncCallbackStackTop = PS2_RAM_SIZE`) → observed sp was `0x01FFFFF0` → assertion held |
| 2 | `6046260` ("run INTC/DMAC/alarm handlers on reserved stacks", fixing a real corruption: a handler prologue stored zeros over thread 1's ra slot at `0x1ffff00`) relocated the pool to kernel-reserved low RAM `[0x80000,0x100000)` (`ps2_runtime.cpp`: floor/top `0x00080000u`/`0x00100000u`, two sites + member init) and did NOT update the test |
| 3 | First reservation now returns `top - 0x10 = 0x000FFFF0` (`reserveAsyncCallbackStack`, `ps2_runtime.cpp:2230`); the drain paths (`EeScheduler.cpp:430`, `:523`) assign it when the queued invocation has `sp=0`; `activeContext()` returns the invocation context — deterministic `0xFFFF0`, matching the B2 probe exactly |
| 4 | `git log -S` confirms the `0x01F00000u` assertion was never touched after `f4309cd` |
| 5 | Restoring heap-region stacks (the alternative, product-side fix) would reintroduce the `0x1ffff00` collision `6046260` fixed |

Call: test-only fix. The product behavior (low-RAM pool) is deliberate and
documented; the test encoded the old, buggy location.

## 4. The AFAIL face: not reproduced

| # | Evidence |
|---|---|
| 1 | AFAIL test passes 10/10 full-suite runs (2 bit-identical builds), 1/1 alone (B1), and in the PS2GS subset (B3) |
| 2 | Purity audit: `drawGsPixelForTests` builds fresh `vram` + `GS` per call; `GS::reset` memsets contexts; the backend's only static is a `call_once` LUT init; `classifyAlphaTest` is pure |
| 3 | Flag audit: every `PS2_IF_AGRESSIVE_LOGS` block in both code paths is logging-only (counters + `cout`); no `#if` changes behavior in either path |
| 4 | Harness audit: `MiniTest` runs single-threaded in `std::map` (alphabetical) order; no shuffle, no threads |
| 5 | History: every AFAIL-face observation (P15/e73e36a, P20/be01146, orch re-run) came from the shared-clone + shared-incremental-build-dir (`/tmp/p1-link/runtime`) era with concurrent agents; all those trees already contain `6046260`, so a clean build of any of them must fail GsSyncV, not AFAIL |

The historical flip mechanism is unresolved from available evidence (see §8);
no AFAIL-face configuration exists on a clean build of the current tree.

## 5. Diff + why (fork commit `2caf17c`, pushed to `fork` remote)

One file, `ps2xTest/src/ps2_gs_tests.cpp` (+5/−1). Replaces the stale
`sp >= 0x01F00000u` floor with both bounds of the documented post-`6046260`
pool; all other assertions (hits, tick, GP, prev, caller-sp) unchanged:

```diff
-            t.IsTrue(g_gsSyncCallbackSp.load(std::memory_order_acquire) >= 0x01F00000u,
+            // P1y: 6046260 relocated the reserved async pool from the RAM top
+            // to kernel-reserved low RAM [0x80000,0x100000); pin both bounds.
+            t.IsTrue(g_gsSyncCallbackSp.load(std::memory_order_acquire) >= 0x00080000u,
                      "callback invocation should use the reserved async stack pool");
+            t.IsTrue(g_gsSyncCallbackSp.load(std::memory_order_acquire) < 0x00100000u,
+                     "callback stack should stay below the ELF image base");
```

Commit message: `Test: expect the GsSyncV callback stack in the relocated
low-RAM pool (P1y)` + two-trailer convention. `git pull --rebase` before push
pulled peer `ed387c7` (P1w P24-2) + `9c7b028` (I7); rebase applied with no
conflicts (peer files disjoint); pushed `9c7b028..2caf17c ssx3 -> ssx3` from
the fork clone only.

## 6. Before/after run tables

| Phase | Tree | Runs | Result every run |
|---|---|---|---|
| Before (build1) | `5b5ac3d` | run1–run5 | 426/425/1 GsSyncV |
| Before (build2, clean rebuild) | `5b5ac3d` | run6–run10 | 426/425/1 GsSyncV |
| After fix | `5b5ac3d` + fix | run11–run15 | 426/426/0, exit 0 |
| After fix, rebased+pushed | `2caf17c` (= `9c7b028` + fix; P1w P24-2 adds 1 kernel test) | run16–run20 | 427/427/0, exit 0 |

P1v zero-max test (`CreateSema with zero max_count…`) passes in all 20 runs;
on the rebased tree it passes with P1w's `[drop] sched/createSemaphore …`
census line interleaved (peer-diag noise, expected). Both faces gone (exit 0).

## 7. Exact commands

From `$Y=/Volumes/Extreme SSD/ps2x-p1y`, `$F=$Y/fork`:

```
git clone --branch ssx3 https://github.com/brad-richardson/PS2Recomp.git $F
git remote rename origin fork                      # in $F
find $F $Y/build -name '._*' -delete               # exfat AppleDouble hygiene
cmake -S fork -B build -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DPS2X_BUILD_TEST=ON -DPS2X_ENABLE_RUNTIME_LOGS=ON   # in $Y; 511 s first time
cmake -S fork -B build                             # 2nd configure after ._ purge
cmake --build build --target ps2x_tests -j4        # in $Y
(cd $F && $Y/build/ps2xTest/ps2x_tests)            # every run, CWD = fork root
# probes: temporary MiniTest.h filter + cbSp print, incremental rebuild, then:
git checkout -- ps2xTest/include/MiniTest.h ps2xTest/src/ps2_gs_tests.cpp
# fix: edit assertion (§5), rebuild, 5x runs, then:
git add ps2xTest/src/ps2_gs_tests.cpp; git commit -m "Test: ... (P1y)"
git pull --rebase fork ssx3; git push fork ssx3     # fork clone only
# re-verify: rebuild on rebased tree, 5x runs (427/427/0)
```

Build note: on exfat, `._*.c` sidecars appear under `build/_deps` during
FetchContent and get globbed as sources (13 errors); the working recipe is
configure → `find -name '._*' -delete` → reconfigure (51 s) → build.

## 8. What I could not do

- Reproduce the AFAIL face in any configuration (10 full runs / 2 clean
  bit-identical builds / alone / subset); its historical flip mechanism is
  unresolved. Leading hypothesis: stale/mixed objects or a racing worktree in
  the shared-clone + shared-incremental-`/tmp/p1-link/runtime` era (concurrent
  agents; "same tracked tree" ≠ same worktree at compile time) — consistent
  with all observations but not provable now. The separate-clone/separate-
  builddir discipline (P1w/P1y) already removes that environment.
- Verify the pushed rebased tree beyond the host suite (no boots per brief;
  peer P1w P24-2 + I7 changes covered only by the suite going 427/427/0).
- Touch `/tmp/p1-link` (P1w's live build dir) — never read, listed only once
  for the CMake option reference.
