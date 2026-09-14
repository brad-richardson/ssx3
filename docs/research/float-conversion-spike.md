# Generated floating-point conversion spike

The first candidate separates the normal bit-conversion path from exceptional
inputs and forces only that small path inline. Differential checks pass, but
the performance result depends on the caller: removing an existing helper call
helps; replacing an already-inlined original can hurt. This is an isolated
experiment, not an optimization delivered to the phone.

## The phone already uses Release

The installed `f40bfef6` build is an optimized, development-signed Release
build. Its actual `local/native/ios-device/CMakeCache.txt` and Ninja recipes
show:

| Component | Effective optimization |
| --- | --- |
| Objective-C++ app | `-O3 -DNDEBUG` |
| Dolphin core and Metal renderer | `-O3 -DNDEBUG` |
| Generated game module | `-O2 -DNDEBUG -flto=thin -ffp-contract=off -fno-fast-math` |
| Debug mode / sanitizers | `ENABLE_DEBUG=OFF`, `USE_SANITIZERS=OFF` |
| Link-time optimization | Enabled for the generated module, disabled for the Dolphin core |

The generated compile command also contains an earlier `-O3`; the later `-O2`
is effective. These inspected commands contain no `-g`. Development signing
and the `get-task-allow` entitlement do not imply unoptimized code or an
attached debugger. Stripping symbols is primarily a file-size change; no
material steady-state FPS gain from stripping has been measured or is expected.

Runtime instrumentation is a separate issue. `native/ios/App.mm` enables
dispatch sampling, periodic metrics and the diagnostic smoothing trace.
Dispatch sampling adds a conditional check at dispatch boundaries and updates
the PC sample map every 4,096 native dispatches. Its environment switch is
presence-based: `STATICRECOMP_DISPATCH_SAMPLES=0` still enables it; an A/B
experiment must remove the variable. No defensible combined instrumentation
overhead percentage has been established. A future low-diagnostic comparison
should keep the same Release optimizer settings and retain smoothing safety
checks, measuring diagnostics independently of the FP candidate.
The selected actual commands and cache hashes are retained in
`local/research/120hz/phone-release-audit.json`.

## Why this change is scoped

The [ordinary-frame desktop profile](normal-frame-cpu-spike.md) attributes
484 of 16,988 CPU/GPU-thread running samples to the generated float-format
conversion helpers. Of those, 260 have the hottest chunk, `func_802197A0`,
as their caller: 154 widening and 106 narrowing. These are desktop 3× samples,
not measured phone costs or whole-frame callback timings.

The actual Apple Clang O2 compile of this large chunk leaves 316 widening and
273 narrowing call sites outlined. Only seven other widening sites inline.
Inlining remarks report a threshold of 45 at rejected sites versus costs of
165 and 70. Declaring a helper `inline` alone does not require the compiler to
inline it. The same audit found quantized-load helper specialization blocked
by large inline costs; changing that remains a separate experiment.

The candidate preserves the original two helper bodies in `noinline,cold`
functions. A short `always_inline` path handles normal float32 widening with
integer sign/exponent/mantissa reconstruction. Float64 narrowing retains the
original generic bit mapping except for exponents 874–896, which call the
original exceptional path. There are no arithmetic approximations, omitted
FPSCR updates, or relaxed compiler FP flags.

The exact candidate header is SHA-256
`dcac6fc866a0e49d9f5875c7c5a4a045e11209472f2123a0fc96062adee922d8`.
The original is
`05b40083d151a9db2098c8746e637b1ecbae62d73213b26b94b74945fa1b5a1f`.
No vendor or production generated file is rewritten by the spike tools.

All 323 widening and 273 narrowing sites inline their candidate common path
in the one-chunk compiler probe. Its non-LTO `__text` grows from 465,284 to
489,896 bytes, **5.29%**. Forcing the entire original helpers inline instead
grows it to 529,872 bytes, **13.88%**. These are object-probe sizes; full ThinLTO
can alter code elsewhere and must be assessed separately.

## Correctness and measurement

`tools/native_float_conversion_spike.py` builds a private reference/candidate
harness using production Apple Clang 21.0.0 with O2, ThinLTO and strict FP flags.
The first artifact, `local/research/float-opt-conversion/split1`, passes every
one of the **4,294,967,296 float32 input bit patterns**, comparing raw float64
output bits. Narrowing checks cover **5,046,272 float64 samples**, including
both signs, all 2,048 exponents, every single fraction-bit boundary, and random
raw-bit samples. Another 4,194,304 widening samples and the random narrowing
inputs are checked across all four host rounding modes. NaN payloads and
signed zeros are compared as bits, not by floating-point equality.

This is conversion-output equivalence, not a claim that incidental ARM FPSR
flags are identical. Apple Clang emits an FP compare for the reference's
integer absolute-zero predicate; the candidate common path is integer-only.
The pinned ARM guest FP helper controls FPCR and models guest exceptions
explicitly; this audit found no ARM FPSR consumer in that runtime path.
Whole-guest arithmetic and FPSCR checks for the independent classifier
candidate are documented in [the arithmetic audit](float-arithmetic-audit.md).

The second artifact, `split2`, keeps exactly the same candidate header and
adds a benchmark shape with an explicitly outlined reference helper, matching
the calls observed in the hot chunk. Its own quick differential check passes
16,777,216 widening patterns plus the same narrowing and rounding samples;
the exhaustive check belongs to the earlier binary. Six alternating paired
rounds perform 16,777,216 conversions per case. All 192 timing-row checksums
match. Times use thread CPU time, with identical bounded warmups.

| Finite-input shape | Conversion | Reference ns/input | Candidate ns/input | Candidate / reference |
| --- | --- | ---: | ---: | ---: |
| Compiler chooses inlining in small kernel | Widen | 0.508 | 0.606 | 1.194 |
| Compiler chooses inlining in small kernel | Narrow | 0.508 | 0.568 | 1.118 |
| Outlined reference, inline candidate | Widen | 0.937 | 0.622 | 0.663 |
| Outlined reference, inline candidate | Narrow | 0.919 | 0.574 | 0.624 |

The favorable outlined-reference finite pairs range from 0.656–0.682 for
widening and 0.613–0.630 for narrowing. Rare-input costs still matter:
subnormal widening/narrowing regress about 18%/24% in that shape, and the
zero/infinity/NaN widening corpus regresses about 29%. These corpora are
synthetic; the actual game's operand distribution has not been sampled.

Linked ARM64 disassembly confirms per-iteration array loads and live loops,
original helper calls in the outlined-reference shape, and inlined candidate
common paths with calls only on the exceptional branch. ThinLTO merges the
identical outlined narrowing reference and candidate slow body; the reference
still makes a real call. The assembly is retained in `split2/kernels-arm64.txt`.

The direct potential is modest: the scoped chunk's conversion leaves are only
about 1.53% of sampled active desktop CPU. A 35% reduction in just that cost
would suggest roughly half a percentage point before secondary effects;
it is not a measured game gain. Code growth, register allocation and cache
effects can erase that benefit. Broadly applying this candidate is unjustified
by the already-inlined and rare-input regressions.

## Reproduction and boundaries

```sh
python3 tools/native_float_conversion_spike.py prepare --output local/research/float-opt-conversion/NEW
python3 tools/native_float_conversion_spike.py check --output local/research/float-opt-conversion/NEW --exhaustive
python3 tools/native_float_conversion_spike.py bench --output local/research/float-opt-conversion/NEW --iterations 16777216
python3 -m unittest tests.test_native_float_conversion_spike tests.test_native_float_module_spike
```

The benchmark refuses a changed binary, harness or saved header, and a
correctness receipt from another binary. Focused tests deliberately corrupt the exponent mapping and
verify that the native checker rejects it, alongside stale-evidence checks.
Private source transformations preserve the exact exceptional helper bodies
and every unrelated header byte.

`tools/native_float_module_spike.py` prepares a one-object replacement using
the exact production Apple compile/link recipe. It guards the baseline,
compiler/linker, generated source, original objects and module tables by hash;
it changes only private input/output paths and one hot source object. The
other 182 source objects are reused. A fresh ThinLTO link can still optimize
the entire linked module. The baseline module, player, guards, no-JIT policy,
assets and installed phone app remain unchanged.

The private `split-802197a0` module built successfully: the one-source compile
took 4.35 seconds and the final ThinLTO link took 229.60 seconds. Its SHA-256 is
`ac5d1053a2985af8e30968a462d6aefa26c4a398584a301efeafef4898450686`.
The final `__text` grows from 75,665,516 to 75,673,284 bytes, **7,768 bytes**;
this differs from the non-LTO object growth. ABI export names match, and all
183 original objects, module tables, compiler/linker and production source
hashes still matched at build completion. This verifies the private build's
scope, not gameplay correctness or performance.

The subsequent tool review added an explicit `--conversion-evidence` input
for preparation. It verifies both saved headers and the harness/binary against
their receipts, requires a passing check for that binary, and binds the newly
transformed module header to the verified candidate hash. Build rechecks that
binding. The historical `split-802197a0` module predates this automatic gate;
its exact header match was checked separately. Its original guarded tools
and manifest hash are preserved in `source-tools/archive.json`.
The final schema-2 prepare path also passed against the real production
recipes and `split2` evidence in `recipe-verification-v2`; no second link was
needed. Nineteen focused conversion, arithmetic and module-provenance tests
pass, including the native negative controls.

```sh
python3 tools/native_float_module_spike.py prepare --output local/research/float-opt-module/NEW --conversion-evidence local/research/float-opt-conversion/NEW
python3 tools/native_float_module_spike.py build --output local/research/float-opt-module/NEW
```

Inlining probe evidence is in
`local/research/120hz/codegen-inlining-audit/conversion-probe.json` and
`split-exact/`. Binary/source/compiler receipts and raw conversion results
remain under the two conversion artifact directories. The arithmetic
classifier experiment is independent and is not combined with this candidate.

## Bounded linked-game check

The candidate completed a 226.85-second desktop session using the unchanged
production native player and `gc-gari-027` assets, Metal, Cubeb audio and the
existing 3× internal-resolution configuration. No smoothing callbacks, dispatch
sampling, Metal validation or JIT fallback were enabled. All 431 chunk
verifications passed; invalid memory accesses, GPU command errors, unknown
guest instructions and failed self-modifying-code checks remained zero.
The player and module hashes matched before and after the run.

Fourteen saved captures include active riding and recovery. A capture within
the Time Profiler window shows 15% progress at 12 MPH; the final capture shows
41% at 48 MPH. Late runtime samples remain near 60 FPS and 1.0 guest speed.
This is a bounded gameplay correctness check, not a full-course, phone or
120 Hz acceptance result.

The profile seed was frozen from the earlier desktop profile's completed user
directory, including its resulting settings/card state. It is not the initial
fresh state of that earlier run. Inputs use the same host-timed sequence but
cannot guarantee an identical guest trajectory. A comparison with the earlier
profile can show where helper calls moved or disappeared; it cannot establish
a small whole-game speedup. A second baseline run was not launched merely to
seek a favorable median.

The candidate profile contains 13,559 running CPU/GPU-thread samples. The
earlier profile had 16,988. Within the targeted chunk's ancestry, the earlier
154 widening and 106 narrowing original-helper leaf samples become zero;
the candidate retains 39 samples in the exceptional widening helper.
The linked narrowing helper remains in other chunks: 74 candidate samples
resolve through a merged symbol at module RVA `0x482bb90`, shared by
`dolrecomp_f32_to_bits` and its slow alias. None has the target chunk in its
ancestry. Missing symbol labels alone would not establish helper removal.
The chunk itself has 844 self and 1,310 inclusive samples, versus 1,106 and
1,877 earlier. These changed counts and denominators do not measure an
optimization percentage: the guest idle workload and course trajectory also
differ. This confirms the intended call-boundary change in a live workload
and preserves the need for a controlled CPU-time comparison before promotion.

Runtime receipt: `local/reports/native-runs/20260913-214415.json`.
The private module directory retains `run_case.py`, the frozen seed with
hashes, and `candidate1/` with input records, identity checks, trace and exports.
