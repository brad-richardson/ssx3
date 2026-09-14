# Floating-point arithmetic classifier spike

This is an isolated optimization experiment against the pinned GXRuntime implementation. It does not change the vendor checkout, generated game code, app, or phone build. The first broad classifier candidate preserves tested state but has mixed timing results; it is not approved for production by these measurements.

## Why this seam

The [ordinary Snow Jam desktop CPU profile](normal-frame-cpu-spike.md) recorded 326 self samples in `ppc_fadds`, 325 in `ppc_fmuls`, and 250 in generated `ppc_fma`, out of 16,988 samples on the CPU/GPU thread. These are desktop samples, not a phone cost breakdown. The current generated chunk sources contain 5,684 static `ppc_fadds` calls, 12,228 `ppc_fmuls` calls, 5,836 `ppc_fma` calls, and no `ppc_fmadd_op` calls. Static call-site counts do not measure runtime frequency.

The result classifiers in `GXRuntime/src/core/cpu_interpreter_float.c` map finite normal results to FPRF class 4 or 8 according to their sign. The first candidate inserts this integer-only early return before the existing exceptional classification branches:

```c
if (__builtin_expect(exponent != 0 && exponent != EXPONENT_MASK, 1))
    return 4u << sign;
```

The original NaN, infinity, subnormal, and signed-zero classification stays intact. For any normal finite bit pattern, the original final expression is `sign ? 8 : 4`; the sign is exactly 0 or 1, so the added return is equivalent. This does not use floating-point comparison, change rounding, omit FPSCR writes, or enable fast math.

Apple Clang 21 at O2/ThinLTO emits a shorter normal-result epilogue: an exponent-range test, a rare-path branch, sign extraction, and FPRF insertion. Source-level branch hints alone are not evidence of a faster complete program. The first linked harness also outlines `ni_add`, whereas the production module inlines it into `ppc_fadds`; that limits the interpretation of the small harness's `fadds` result.

## Arithmetic semantics that must remain intact

| Path | Existing behavior to preserve |
| --- | --- |
| `ppc_fadds` | Uses `ni_add`, honors invalid-exception gating, applies `force_single`, writes both FPR/PS1 lanes and FPRF. Ordinary finite addition preserves FI/FR; exceptional paths have their existing clear behavior. |
| `ppc_fmuls` | Applies `force_25bit_c` to C, uses `ni_mul`, honors invalid gating, applies `force_single`, writes both lanes/FPRF, then clears FI/FR. |
| Generated `ppc_fma` | Uses fused arithmetic, with its single-precision C rounding and double-rounding tie correction. NaN operand priority is A, then B, then C; payload quieting and invalid-exception flags are preserved. VE can prevent the output/FPRF write. Negative variants leave NaNs unnegated. The generated caller writes destination lanes only when the helper returns true. |
| Interpreter `ppc_fmadd_op` | Uses a different helper path and FI/FR behavior from generated FMA. Plain single `fmadds` updates FI from the rounding comparison; double writes only FPR. It must not be substituted for generated `ppc_fma`. |

`force_single` explicitly flushes tiny values under guest NI while preserving sign, then otherwise casts to float. Generated `ppc_fma` does not call that helper; its existing host FP mode still matters. `force_25_bit` and `force_25bit_c` also differ in their subnormal handling. Combining these helpers or replacing single arithmetic with a plain float operation requires separate correctness work.

`ppc_fpscr_control_updated` normalizes FPSCR summary flags and programs host ARM FPCR rounding/NI controls. Tests must preserve all four guest rounding modes, NI, sticky exception state, and unrelated guest registers. The classifier experiment changes none of these mechanisms.

## Reproducible harness

```sh
python3 tools/native_float_classify_spike.py prepare --output local/research/float-opt-arithmetic/NEW
python3 tools/native_float_classify_spike.py check local/research/float-opt-arithmetic/NEW
python3 tools/native_float_classify_spike.py bench local/research/float-opt-arithmetic/NEW --rounds 6 --iterations 10000000
python3 -m unittest tests.test_native_float_classify_spike -v
```

`prepare` copies the exact arithmetic source, private header, tables, and CPU/type declarations. Its receipt records their SHA-256s, transformed sources, compiler, command, harness, and binary. Symbol prefixes allow independent variants to coexist. Flags are `-O2 -flto=thin -ffp-contract=off -fno-fast-math`; this is a small executable using the same optimizer/FP settings, not a full-module relink. Checks and timings reject changed receipt inputs; timing also requires a passing differential check for that exact binary.

The current tool links three variants: the exact reference; the broad `candidate` changing both shared classifiers; and `scoped`, adding two private classifiers used only by generated `ppc_fma`. The scoped transformation preserves the original classifiers and all other caller source. A test removes its two added helper definitions and one redirected FMA classification statement and requires byte-for-byte recovery of the original source.

The classifier oracle covers every sign and exponent with zero fraction, every single fraction bit, and all fraction bits set: 233,984 cases. This covers every predicate category, not every possible 32/64-bit input. Integration checks cover 431,856 cases across `fadds`, `fmuls`, eight generated FMA variants, and eight interpreter FMA variants. Both candidates compare the entire 3,528-byte CPUState, FMA return status and output bits, and ARM FPCR/FPSR. Inputs include:

- Four rounding modes crossed with NI; enabled and sticky FPSCR exception combinations.
- Distinct registers, destination aliases with each input, and all-register aliasing.
- Signed zeros, float/double subnormals and boundaries, finite overflow, infinities, positive/negative quiet and signaling NaN payloads.
- Single rounding ties and neighboring bits, C rounding boundaries, and deterministic random raw-bit triples.
- Initially clear and prepopulated host FPSR exception/saturation flags.

The negative test modifies an unrelated guest CR bit in the copied scoped candidate. Both the receipt gate and, after recompilation, the actual full-state differential checker reject it. Agreement is with the pinned runtime, not an independent proof that the runtime perfectly implements hardware PowerPC semantics.

## First broad-candidate timing

Artifact: `local/research/float-opt-arithmetic/classifier2`. Apple Clang 21.0.0, ARM64 macOS/Darwin 25.6.0; binary SHA-256 `26627e62143deb2d18f120baeea7bd4c76006b0b9010da709975157e638d5cc1`. The source arithmetic SHA-256 is `3026eb10f63667a85dccb6e1fc7df1d2c299058cd636cae6b2c0ca7b02a4806c`.

Six alternating reference/candidate rounds execute ten million calls per case. Timings use thread CPU time, include identical dispatch/input/checksum overhead, and require matching output checksums. One corpus uses deterministic finite normal inputs; another replaces 1/64 triples with zero/subnormal/infinite/NaN/overflow inputs. Neither corpus claims to reproduce game operand distributions.

| Operation | Normal reference → candidate ns/call | Change in median | Special-corpus change in median |
| --- | ---: | ---: | ---: |
| `fadds` | 5.814 → 5.427 | −6.66% | +0.50% |
| `fmuls` | 5.586 → 5.494 | −1.64% | −2.06% |
| Generated FMA single | 3.731 → 3.482 | −6.66% | −6.20% |
| Generated FMA double | 3.973 → 3.725 | −6.24% | −5.76% |
| Interpreter FMA single | 5.828 → 6.905 | +18.47% | −3.09% |

Generated FMA improved in every paired round of both corpora. Other cases showed large variation: normal `fmuls` reference ranged 4.340–5.850 ns/call and candidate 4.097–5.622; interpreter FMA reference ranged 5.603–7.333 and candidate 5.723–7.024. These ranges prohibit treating every median difference as a stable optimization. CPU frequency/core placement and layout/branch effects were not independently measured. Thread CPU time excludes descheduling, but does not normalize processor frequency or microarchitectural state.

The broad candidate must remain experimental. The useful next comparison confines the new classifiers to generated FMA and includes the unchanged operations as controls, with balanced variant ordering and explicit paired ranges. Even a stable 6% helper reduction would affect only a small fraction of whole-frame CPU in the desktop profile; it cannot be described as a 6% frame-rate improvement or assigned directly to the phone.

## Scoped FMA comparison and variance controls

The follow-up artifact is `local/research/float-opt-arithmetic/classifier-scoped1`; binary SHA-256 `e186d10f19ab177da287182513e90d0efa05c4d8cb11ad8f37e77064eb5206c0`. Both candidates passed all 431,856 arithmetic cases, totaling 863,712 complete-state/host-flag comparisons, and the classifier oracle passed. All four focused tool tests pass, including scope isolation, changed-source rejection, benchmark result consistency, and deliberately corrupted CR rejection.

The three variants share one linked executable. Six rounds cover every permutation of reference/global/scoped execution order, with ten million calls per case. Every checksum matches. Percentages below are the median and range of **paired** per-round changes against that round's reference, rather than a ratio of independently chosen medians.

| Generated FMA case | Reference median ns | Global median ns | Global paired change, range | Scoped median ns | Scoped paired change, range |
| --- | ---: | ---: | --- | ---: | --- |
| Single, normal | 3.581 | 3.480 | −2.85% [−6.33, −2.14] | 3.482 | −2.80% [−6.41, −1.71] |
| Double, normal | 3.683 | 3.727 | +0.77% [−6.60, +7.26] | 3.604 | −0.14% [−4.51, +0.21] |
| Single, special 1/64 | 3.834 | 3.754 | −2.60% [−5.96, −1.87] | 3.692 | −3.98% [−5.70, +1.56] |
| Double, special 1/64 | 3.958 | 3.972 | +0.55% [−2.13, +1.95] | 3.969 | +0.47% [−1.97, +3.12] |

The unchanged controls expose material benchmark sensitivity. Scoped/reference `fmuls` is identical linked code, yet its normal paired change ranges −0.72% to +24.23%. Scoped/reference interpreter FMA also shares one function address, yet its normal paired change ranges −19.95% to +28.18%. Different variant wrapper addresses/layout, core placement, frequency, and predictor state are potential contributors; this experiment does not identify their individual contributions.

`nm` provides especially useful evidence here:

| Functions | Same linked address |
| --- | --- |
| `candidate_ppc_fma`, `scoped_ppc_fma` | `0x100001050` |
| `reference_ppc_fmuls`, `scoped_ppc_fmuls` | `0x100000a48` |
| `reference_ppc_fmadd_op`, `scoped_ppc_fmadd_op` | `0x100000c58` |

Thus the global and scoped generated FMA bodies are identical after ThinLTO, while unaffected arithmetic bodies remain identical to the reference. The FMA body grows from 876 to 884 bytes in this executable; fewer common-path instructions do not imply a smaller total function. Disassembly is saved as `linked-arithmetic.s` in the artifact directory.

The scoped version is the preferable correctness boundary for any further experiment: it leaves unrelated classifier users untouched. Its normal single FMA improved in each round, but the effect is small and the double case is flat. The earlier broad-candidate 6% result is not a reliable universal estimate. Keep both off the phone pending an actual generated-module/workload comparison. A useful next microbenchmark refinement is a shared caller invoking the selected arithmetic function directly, eliminating the distinct per-variant `apply` wrapper layout; the same-address function pairs can then serve as a stricter noise control. Do not repeat this benchmark until a favorable median appears.

For whole-frame prioritization, the profiled `ppc_fma` self cost is about 1.47% of sampled desktop CPU/GPU-thread running time. Even a few-percent reduction there predicts only a small frame-level effect before secondary interactions, and the profile includes both FMA precisions. Generated conversion/call-boundary optimization and measured rendering work remain more promising next targets. This spike establishes a tested narrow transformation and rejects broad performance claims; it does not establish a phone speedup.
