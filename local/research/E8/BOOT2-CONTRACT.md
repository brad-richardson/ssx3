# E8b — busy-query coverage receipt

Recorded after E8a and before the second boot. Baseline stays fork
4acc59f and the exact E7c runner/test binaries; no source changes, build,
regeneration, guest patches, input injection, or storage promotion.

E8a reaches tick10825 with continuing frame/scheduler activity and the
same memory-card-check content. The first card port-selection call is
0x2c4480, reached twice. Its indirect busy query at 0x2c44a8 reads
vtable slot 0x486fd4, whose ELF value is 0x2c5140. The generated dispatch
table has entries for 0x2c50e0 and 0x2c5118 but none for 0x2c5140;
the emitted owner has an internal label for the latter. The first boot's
missing-target reporter printed only its first unrelated missing target.
Its absence from the hot-PC tally does not prove the call was unattempted.

| Hypothesis | Observable in boot 2 | Selection / action |
|---|---|---|
| H-coverage | Missing-target receipt source=0x2c44a8, target=0x2c5140, policy=SkipCallDebug, v0=0x2c5140, and object state +4; later UI polling at 0x23d6a4 repeats the same missing busy query. The report does not expose object +0x40, so its value must remain a separate residual unless another receipt closes it. | Coverage wall selects (ii). Preserve the exact predicate and propose gated regeneration/binding repair; no handwritten guest substitute or forced return. |
| H-other | Query resolves to a different target, state is nonzero, or another operation precedes the busy wait. | Follow the first demonstrated gate using existing static evidence; do not implement the proposed coverage hypothesis. |
| H-measurement | Missing-target records are incomplete, capped before the gate, or cannot be aligned. | (iii): identify only the measurement repair. |

Existing diagnostics suffice: add PS2X_DIAG_REPORT_ALL=1, keep the
singleton/S guards, E7 copy tap, and E4 window at ticks600→601. Every
missing-target report includes guest PC, source, target, registers,
object header, dispatch history, and active missing-function policy.
Static branch truth table plus captured registers will distinguish the
intended query result from the skip-call residual register.

Stop at the first cap: wall60s (SIGTERM at45s, reserve15s), progress
1,000,000 syscall lines, existing E8a byte bounds. For this potentially
noisy boot, reserve min(8MiB, cap/4) in every byte category before its
limit. Keep 250ms polling, 5s liveness, identical pre-claim suite/selftest,
owned lease, and release immediately after termination. No truncation of
active logs. This consumes boot 2 of at most4.

Historical command to be executed once:

```sh
export COPYFILE_DISABLE=1
python3 -B local/research/E8/e8_capture.py b --arm 600 --report-all --wall 60
```

Tail receipt: hypothesis, alternatives, selection rules and three caps
recorded before boot 2; no proposed behavioral fix is authorized by the
static candidate alone.

Post-capture corrections (the prospective wording above is preserved):
policy=1 is ContinueToTarget, not SkipCallDebug=3. Its call-path `true`
return nevertheless makes the generated caller resume at fallthrough
with the unchanged target address in v0. The query instructions are
present in the emitted owner, but there is **no entry switch case or
label at 0x2c5140**; its code follows the preceding routine's unconditional
return. A table-pointer insertion alone would enter 0x2c50e0 instead.
Both corrections are tabled in REPORT.md and e8-runtime-policy.txt.
