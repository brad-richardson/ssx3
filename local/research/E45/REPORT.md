# E45 — VU1 math on arm64 Android: drop `long double` (quad soft-float) for `double`

- Date: 2026-09-23. Brief: `local/muse/prompts/E45.md`.
- Read first: `AGENTS.md`, `local/AGENTS.local.md`, `local/research/N4/REPORT.md` (Profile 2).
- HEADLINE: `VuWide=double` committed on fork branch `e45-vu-double` (`310b30f`);
  suite 570/570; **double-Odin hash == Mac hash on all 5 bench programs (PASS)**,
  and quad-Odin is bit-identical too — alternative (a): the only change is speed.
  Quad soft-float costs ~1.3–1.8× on FMAC-dense interpretive runs (P3: 1.6×).
- Budget: ~6 builds (1 suite + 1 Mac double + 1 Mac quad + 2 NDK + probes),
  2 Odin bench runs (~30 s lease each), ~40 min of 4 h, 1.4 GB of 2 GB.
  No push anywhere.

## Change (fork branch `e45-vu-double`, commit `310b30f`)

Worktree `~/dev/ssx3-work/E45/PS2Recomp` from `ssx3 @ 571579e`; `~/dev/PS2Recomp` untouched.

| File | Change |
|---|---|
| `ps2xRuntime/include/runtime/ps2_vu1.h` | `VuWide` alias (`double` default, `long double` under `PS2X_VU_WIDE_QUAD=1`) + `static_assert(sizeof(long double)==sizeof(double))` on `__APPLE__`; 2 decls use `VuWide` |
| `ps2xRuntime/src/lib/vu/ps2_vu1_core.cpp` | all 9 `long double` sites → `VuWide`; all 4 `0.0L` literals → `0.0` (a `0.0L` in a `VuWide` expression would reintroduce quad soft-float via promotion) |

Full diff: `logs/fork-diff.txt` (31 insertions, 15 deletions).

Why the `0.0L` literals matter: with `VuWide=double`, `cond ? 0.0L : <double>` promotes
the double branch to quad (`__extendsftf2`) and `magnitude == 0.0L` becomes a quad
compare. `0.0` converts to `long double` exactly, so the quad build is unaffected.

### Other `long double` sites (checked, untouched)

- `ps2xRuntime/src/lib/Kernel/Stubs/Helpers/Support.h:1170`: guest `%Lf` printf path —
  converts guest double bits to host `long double` for host `snprintf`. Formatted-print
  slow path, not VU math; changing it would alter host formatting, so out of scope.
- VU0: no separate interpreter — `VU1Interpreter(Unit::VU0)` shares this core
  (decode-width branches only), so the alias covers VU0 macro-mode FMAC math too.
- Repo-wide grep for `long double|float128|__float128|TFmode` in `ps2xRuntime`
  finds nothing else.

## Tests

### 1. Mac suite: 570/570 green from the worktree root, `ps2_vu*` unmodified

```
cmake -S ~/dev/ssx3-work/E45/PS2Recomp -B ~/dev/ssx3-work/E45/build \
  -DCMAKE_BUILD_TYPE=Release -DPS2X_GAME_CODEGEN_DIR=/Users/brad/dev/ssx3-work/codegen-ssx3
cmake --build ~/dev/ssx3-work/E45/build --target ps2x_tests -j10
cd ~/dev/ssx3-work/E45/PS2Recomp && env -u PS2X_SKIP_MOVIE -u PS2X_PAD_SCRIPT \
  ~/dev/ssx3-work/E45/build/ps2xTest/ps2x_tests   # 570/570 (log: logs/suite.txt)
```

Note: one run from the wrong cwd fails `VU0 macro mappings cover all S1/S2 enums`
(it reads `instructions.h` relative to cwd); from the fork root it is 570/570,
matching E44's 570/570 on `ssx3`.

### 2. Odin bench (adb-shell binaries, no APK)

Standalone build of the three real VU1 TUs (`ps2_vu1_{core,lower,upper}.cpp`) +
driver (`bench/e45_bench.cpp`: 5 programs, deterministic edge-case inputs, SHA-256
over VF/VI/ACC/Q/P/I/R/PC/MAC/clip/status + full 16 KB VU-mem after each program)
+ link stubs (`bench/e45_stubs.cpp`: `GS::GS`, `GS::processGIFPacket`,
`PS2Memory::submitGifPacket` — bench programs never XGkick, stubs abort if hit).
Same driver sources on both hosts; only the NDK/Mac compilers differ.

Microprogram source: the brief-allowed fallback (suite program shapes + FMAC-heavy
loop). E40's `mpgpay` lines give DMA-chain guest-RAM source addresses of
runtime-constructed chains plus FNVs of the first words — not byte-exact payloads —
and T50's VU1 trace is a census (`start_pc/cycles/xgkicks`), so real SSX 3
microprograms would need a RAM-dump boot. The fallback covers every op handled by
`calculateFmacExactResult` (36 regular + 36 special encodings), a 2048-trip
dependent-chain loop, and an overflow/underflow/cancellation/denormal torture
program — the exact boundary set where quad-vs-double could differ.

Builds (`-std=c++20 -O3 -DNDEBUG -DUSE_SSE2NEON`, mirroring the app's Release flags):

| Binary | Compiler | SHA-256 | Quad soft-float refs (`__addtf3` et al) |
|---|---|---|---|
| `e45_mac_double` | Homebrew clang++ 23 (mini) | `234db9cf…` | n/a (Mac `long double` is 64-bit) |
| `e45_odin_double` | NDK r28 (clang 19.0.1), `-march=armv8-a+fp+simd+crypto+crc`, `-static-libstdc++` | `e267bf7a…` | **0** (`llvm-nm` + `strings`) |
| `e45_odin_quad` | same + `-DPS2X_VU_WIDE_QUAD=1` | `ea0a5639…` | **7** (`llvm-nm`) |

Full SHAs + `file` output: `logs/ndk-build.txt`. Binaries pinned three ways before
device use (bytesize build tree + Windows landing + mini agree).

### Bench table (variant × ns/instr × hash × hash-equal-to-Mac)

Same args everywhere: `iters=20 loopN=2048`. `cycles` agree across all three
builds per program (10/39/39/32786/29 — same guest path). Binaries print
`sizeofVuWide=8` (double, both hosts) and `=16` (Odin quad), proving the type.

| Program | Mac double ns/instr | Odin double ns/instr (run 1 / run 2) | Odin quad ns/instr (run 1 / run 2) | Quad ÷ double (r1 / r2) | SHA-256 (all 5 runs agree) | = Mac? |
|---|---|---|---|---|---|---|
| P0 smoke (5 pairs) | 336.7 | 1379.2 / 1385.4 | 1962.5 / 1382.3 | 1.42 / 1.00 | `b98a94d0…abf81` | yes |
| P1 opsweep (37) | 139.8 | 599.9 / 540.5 | 1065.7 / 925.7 | 1.78 / 1.71 | `d25e6c73…23c2f` | yes |
| P2 special (37) | 134.5 | 720.7 / 530.0 | 949.7 / 953.1 | 1.32 / 1.80 | `a7ef0491…1a91a` | yes |
| P3 fmacloop (16394) | 114.0 | 167.0 / 175.7 | 272.1 / 281.6 | 1.63 / 1.60 | `f8e260a6…b57f82` | yes |
| P4 torture (24) | 146.1 | 271.7 / 235.7 | 354.9 / 305.1 | 1.31 / 1.29 | `9fe4a0dc…bee8dd` | yes |

Full SHAs: `logs/mac-double.txt`, `logs/odin-double.txt`, `logs/odin-quad.txt`,
`logs/odin-raw-2.txt` (repeat). Mac quad (`logs/mac-quad.txt`, loopN 512) matches
Mac double (`logs/mac-double-512.txt`) on all 5 programs too — expected, since
`long double` is 64-bit there.

Reading: **PASS — double-Odin == Mac on every program**, and quad-Odin is
bit-identical as well, so this is the brief's alternative (a): no input tested
distinguishes quad from double (not even the FLT_MAX/FLT_MIN/cancellation/
denormal boundaries in P4), the change is speed-only. These are A/B host
ns/instr from identical back-to-back binaries (same driver/flags), so the
ratios are the finding; absolutes include driver reset+memcpy per iteration
and are not quotable speed numbers. P3 (16K pairs/run, ~90 ms/run) is the
stablest probe at 1.6×; P0's 5-pair runs are scheduling noise (quad r2 ≈
double). The ratios exceed N4's ~8–9% quad-soft-float self share because the
bench is FMAC-denser than game code (nearly every pair is an FMAC); game-code
speedup will be smaller — N's APK measurement decides that.

Odin runs: lease `E45 2026-09-23T16:10:34Z` → `LEASE_FREE E45 done`, then repeat
`E45 2026-09-23T16:10:54Z` → `LEASE_FREE E45 done` (N6 held it 15:36–16:10Z;
E45 waited and polled; each hold ~30 s). On-device SHAs match all three pins
(`e267bf7a…` double, `ea0a5639…` quad). AC powered (level line missed by the
script's `head -4`, not recorded — shell-binary runs, not APK launches).
`/data/local/tmp/e45` removed; no app installed, no force-stop needed
(shell binaries only).

### Diff for N to pick up

One fork commit on branch `e45-vu-double`: `310b30f` (parent `ssx3 @ 571579e`),
text in `logs/fork-diff.txt`. Since it touches only
`ps2xRuntime/include/runtime/ps2_vu1.h` + `ps2xRuntime/src/lib/vu/ps2_vu1_core.cpp`
(no Android files), N can `git cherry-pick 310b30f` onto `n2-android` (or merge
the branch) — verified to apply cleanly onto `e57b5f8` (n2-android's base) in
a scratch worktree, then removed. Default build is the
new behavior; `-DPS2X_VU_WIDE_QUAD=1` restores quad for any A/B.

## Recommendation (orchestrator decides)

1. ACCEPT the change for `ssx3` (fold `310b30f`): Mac no-op proven three ways
   (static_assert, 570/570 suite, Mac quad==double hashes on all 5 programs);
   Odin correctness proven by double==Mac==quad hashes; only effect is speed.
2. N lane: cherry-pick `310b30f` onto `n2-android` and take the APK number
   (dumps-off build per N4's recommendation; this brief's 1.3–1.8× is an
   FMAC-dense upper bound, not a game-speed claim).
3. Keep `PS2X_VU_WIDE_QUAD` as the documented A/B switch (one line in the N
   build if a quad APK is ever wanted); no further E45 work.

## Gaps

- Real SSX 3 VU1 microprograms not run (fallback programs instead; see above).
  The fallback covers all 72 FMAC exact-result paths + the float-boundary set,
  but a game-program hash would be stronger. Needs a RAM-dump boot (E40's
  `mpgpay` lines are addresses+FNVs, not payloads).
- Mac–Odin absolute ns/instr differ by host/compiler/CPU (expected); only the
  same-device quad÷double ratio is claimed.
- P0's run-2 quad timing (≈double) is small-sample noise; kept in the table
  rather than re-run since P3 pins the ratio.
- The APK measurement is N's lane, not this brief's.

## Receipts

- `bench/`: `e45_bench.cpp`, `e45_stubs.cpp`, `odin_run.sh`, NDK `build_e45.sh`.
- `logs/`: `fork-diff.txt`, `suite.txt`, `mac-double.txt`, `mac-double-512.txt`,
  `mac-quad.txt`, `ndk-build.txt`, `odin-double.txt`, `odin-quad.txt`,
  `odin-raw-1.txt`, `odin-raw-2.txt`.
- `~/dev/ssx3-work/E45/`: worktree, `build/`, `bench/` (binaries), `ndk/` (pkg).
- Fork branch `e45-vu-double` (`310b30f`), never pushed. Odin lease claimed/released
  around the bench runs; `/data/local/tmp/e45` removed.
