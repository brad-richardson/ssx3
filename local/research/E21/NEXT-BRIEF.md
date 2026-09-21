| Handoff | Required boundary |
|---|---|
| Base | Fork `3adc0478b6d2260acdd28a249466f2eef9a20176` unchanged and remote-agreed at open and close. E21 made zero fork commits. |
| Completed | Checkpoint 9457/1725/458/E15/E16/prior/R1–R6; isolation 1:1 + `_Exit` proof; observer-loaded 458/458; Q1 9-case threshold (packet-1 = GOP + 5,461 B); Q2 static re-request absence; Q3 demand watch (1 callback, 1×5,040 B AddBs, 0 completions, park at `0x3b1028`). |
| Proven instrument | `parser/e21-parser-observer.dylib` (SHA256 `e4d88fdc…b38e6be`) is the first validated parser probe: byte-identical forwarding, 1:1 backend counts, 4/4 bindings, clean closures. Reuse it; do not rebuild or rename without re-proof. |
| Boot-argv warning | macOS `stdbuf` replaces `DYLD_INSERT_LIBRARIES` — e21a booted uninstrumented (parser-wise) because of it. Any future observed boot must exec the runner directly (proven: 0 observer files under `stdbuf` vs 2 direct). |
| Exact next measurement edge | Per-call parser timing inside the title window (e21a's gap): one `stdbuf`-free observed boot under a new brief's single-boot allowance, then the packet-1 vs guest-feed join. |
| Named missing signal X | A second input-demand signal after successful-but-incomplete AddBs. Runtime side: no re-request path exists (Q2). Guest side: no unprompted retry exists (Q3). A fix here invents demand policy — still excluded. |
| No target fix authority inferred | E21 isolated the stall shape, not a single minimal ABI-preserving edge. A future fix still needs exactly one demonstrated edge plus its own fail-before. No decoder/EOF/policy invention, no fabricated frames, no second fix. |
| ABI carry | Caller-owned synchronous delivery, word0-only cbData, v0 discarded, valid-no-input waits, no guest invocation under MPEG mutex, delete/reset cancellation, stream behavior unchanged. |
| Protected state | `/tmp/p1-link`, `/tmp/e17-map-link`, `/tmp/e18-mpeg-link`, DerivedData; all 1,725 hashes equal at close. No reclaim authorized. E21's `P1/e21-*` fixtures/tooltmp/boot artifacts retained. |
| Probe count | E21 spent 1/1 title boots and 1/1 lease claims (wall-bound, rc0, clean release). A later brief requires its own fresh admission, T13, lease and caps. |
| Source receipts | `REPORT.md`, `isolation-proof.json`, `observer-regression.json`, `threshold-results.json`, `Q2-AUDIT.md`, `e21a-mpeg.json`, `q3-complete.json`, `stdbuf-*.txt`, `final-audit.json`. |

| E21 NEXT-BRIEF TAIL COMPLETE | Observation repaired and proven; stall bounded on both sides; instrument + argv warning carry forward. |
|---|---|
