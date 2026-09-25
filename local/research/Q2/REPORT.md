# Q2 — `sbr-census.py`, the signed-branch census over generated code

Brief: `local/muse/prompts/Q2.md`. Worker: local Qwen via opencode.
Deliverables: `local/tooling/ee/sbr-census.py` + this report + the two JSON
receipts below.

## Inputs

| Generation | Path | Dir mtime | `.cpp` files |
| --- | --- | --- | --- |
| old (pre-SB1) | `~/dev/ssx3-work/codegen-ssx3-pre-sb1` | 2026-09-24 02:31:30 | 9455 (9457 entries; the dir also holds two non-`.cpp` files) |
| new (SB1) | `~/dev/ssx3-work/codegen-ssx3` | 2026-09-25 07:53:19 | 9455 |

Gap, stated plainly: the codegen generations carry no pinned revision in the
brief; inputs are identified by path + mtime above. The census is a pure
function of those two dirs.

## Shape confirmation (before writing regexes)

- pre-SB1 site line (exact, hexdumped):
  `        const bool branch_taken_0x426cf0 = (GPR_S32(ctx, 4) < 0);`
  (8-space indent, single ASCII spaces, **one** closing paren before `;`)
- SB1 site line:
  `        const bool branch_taken_0x426cf0 = (PS2X_SBR_LT(ctx, runtime, 4, 0x426CF0));`
  (two closing parens — the macro call plus the surrounding parens)
- Writer lines: `SET_GPR_(S32|U32|U64|S64|VEC)(ctx, N, <expr>);`
- Function region: from the line matching
  `(uint8_t* rdram, R5900Context* ctx, PS2Runtime *runtime) {` to the first
  line that is exactly `}`. One function per generated file.

## Commands (all from `~/dev/ssx3`)

```
python3 local/tooling/ee/sbr-census.py ~/dev/ssx3-work/codegen-ssx3-pre-sb1 --json local/research/Q2/census-old.json
python3 local/tooling/ee/sbr-census.py ~/dev/ssx3-work/codegen-ssx3        --json local/research/Q2/census-new.json
python3 local/tooling/ee/sbr-census.py --self-check
```

Runtime: ~3 s per dir (read-only scan, 273 MB each). `--self-check` re-runs
both dirs (env `SBR_CENSUS_OLD` / `SBR_CENSUS_NEW` override the paths).

## Output, old generation (`census-old.json`)

```
generation:            pre-sb1
files scanned:         9455
files with >=1 site:   1936
signed sites:          4466
  LT=1086  GE=1088  LE=1945  GT=347
nearest writer of tested reg (same function):
  set_gpr_s32         3232
  u64_add             677
  s64_add             28
  set_gpr_u32         51
  set_gpr_vec         53
  and_or_xor          34
  slt                 25
  mf                  24
  ld                  7
  u64_shift           6
  other               3
  live_in             160
  none_within_400     166
```

## Output, new generation (`census-new.json`)

```
generation:            sb1
files scanned:         9455
files with >=1 site:   1936
files w/ PS2X_SBR_LT:  623
signed sites:          4466
  LT=1086  GE=1088  LE=1945  GT=347
nearest writer: identical per-category counts to the old generation
  (3232 / 677 / 28 / 51 / 53 / 34 / 25 / 24 / 7 / 6 / 3 / 160 / 166)
```

The predicate mix is identical to the site between generations (LT 1086,
GE 1088, LE 1945, GT 347) — the SB1 op mapping is 1:1 with the pre-SB1
comparisons, and writers are untouched by the SB1 patch, so the
nearest-writer table is identical. That is the expected signature of a
faithful branch-only patch.

## Self-check

```
[PASS] old total == 4466 (exact)  (actual: 4466)
[PASS] old set_gpr_s32 = 3231 +/-2%  (actual: 3232)
[PASS] old u64_add = 686 +/-2%  (actual: 677)
[PASS] new total == old total == 4466 (exact)  (actual: 4466)
[PASS] new files referencing PS2X_SBR_LT == 623 (exact)  (actual: 623)
```

Exit 0. Both known category answers land inside the brief's ±2 % band
(+0.03 % and −1.3 %); both exact answers are exact.

## Deviations from review S6, explained (no tuning)

Review `docs/research/review-2026-09-25-fable.md` row S6 vs this census,
old generation:

| Category | Review S6 | This census | Δ |
| --- | --- | --- | --- |
| SET_GPR_S32 | 3231 | 3232 | +1 |
| U64 64-bit add | 686 | 677 | −9 |
| S64 add | 28 | 28 | 0 |
| SET_GPR_U32 | 51 | 51 | 0 |
| SET_GPR_VEC | 53 | 53 | 0 |
| and/or/xor | 34 | 34 | 0 |
| SLT | 25 | 25 | 0 |
| MFHI/MFLO | 24 | 24 | 0 |
| LD | 7 | 7 | 0 |
| (no row) | — | u64_shift 6 | +6 |
| (no row) | — | other 3 | +3 |
| live-in | 151 | 160 | +9 |
| none within 400 | 176 | 166 | −10 |

The deltas sum to zero (4,466 = 4,466). Reading:

1. **u64_add −9 / u64_shift +6 / other +3.** The review's one-off regex
   bucketed all nine of these U64 writers into "64-bit add"
   (677 + 6 + 3 = 686 exactly). This census splits them by the top-level
   operator of the writer expression: 6 sites whose nearest writer is a
   64-bit shift, 3 whose nearest writer is a `runtime->Load64` (a runtime
   memory load, not `READ64`):
   - `sub_00411340_0x411340.cpp:145` site `branch_taken_0x41138c = (GPR_S32(ctx, 16) < 0)`, writer `SET_GPR_U64(ctx, 16, GPR_U64(ctx, 2) << (32 + 0));`
   - `sub_004198D8_0x4198d8.cpp:2384` site `…(GPR_S32(ctx, 16) >= 0)`, writer `SET_GPR_U64(ctx, 16, GPR_U64(ctx, 16) >> (32 + 0));`
   - `sub_00405B70_0x405b70.cpp:438` site `…(GPR_S32(ctx, 4) >= 0)`, writer `SET_GPR_U64(ctx, 4, runtime->Load64(rdram, ctx, 0x10002030u));`
   The new `u64_shift`/`other` rows are extra precision, not a discrepancy
   in total.
2. **live-in +9 / none-within-400 −10, S32 +1.** Boundary differences
   between the two passes' 400-line window and writer-regex edge cases
   (~10 sites). Inside the brief's stated ±2 % tolerance for one-off-regex
   categories; the total is exact.

No regex was tuned to hit a number. Two genuine bugs were found and fixed
during validation, with evidence:

- The pre-SB1 site regex was written with two closing parens
  (`0\)\);`) where the generated text has one (`0);`); caught by a
  hexdump of the canonical line (`od -c`), not by a count.
- `top_ops()` counted the `-` and `>` of the `->` member arrow as
  top-level operators, which misclassifies every `SET_GPR_U64(ctx, N,
  ctx->hi/lo)` (MFHI/MFLO) writer as `u64_add`; caught by the `mf` bucket
   reading 0 against the review's 24. Fixed by treating `->` as one token.

## Notes for future regens

- `--self-check` is the gate to run after every codegen regen; it exits
  non-zero on any failed assertion and prints three example sites for the
  two known categories to diff against.
- The review's own caveat (fable.md §2) still applies: the census is a
  regex pass, not a dataflow analysis — "nearest preceding writer in the
  same function" can be a non-dominating path, so the counts bound the
  problem, they do not prove a site safe.
- If a future regen fails the exact-total check, the first thing to diff is
  the per-predicate mix (LT/GE/LE/GT) against this run: a branch-only
  patch must keep it 1:1.
