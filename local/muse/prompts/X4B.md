# X4B — Dense Qwen narrow read: RTC seed path for E55

You are a local opencode/Qwen **dense** worker in `~/dev/ssx3`. Follow
`~/dev/AGENTS.md` worker rules. Read only the source; write only
`local/research/X4B/REPORT.md` and commit that report. Hand back a
source table, **no fix or conclusion**.

The broad X4 read stalled near 70k context without a report. This arm
asks only one question: how does host time from `sceCdReadClock` reach
the guest RNG seed? The E55 deterministic-mode brief needs exact
anchors. Source pin is fork `ssx3` `bc1c70f` at
`~/dev/ssx3-work/W1F/PS2Recomp` (read only) and E56 canonical
generated code at `~/dev/ssx3-work/codegen-ssx3` (read only). Start with
`docs/research/review-2026-09-23-frontier-2.md` §B; cite source rather
than the review. Do not list whole source trees or read files unrelated
to this path.

Trace exactly:

1. `sceCdReadClock` in `ps2xRuntime/src/lib/Kernel/Stubs/CD.cpp`: name
   the host time API, value conversion and guest-visible output bytes.
2. The HLE registration/call edge for that syscall, with exact
   `file:line` and LSP goToDefinition/findReferences confirmation if
   available. If LSP cannot resolve it, mark the edge unconfirmed.
3. Guest `0x31ae80` to `func_3177C8`: use `local/tooling/ee/ee-at`,
   `ee-func`, `ee-xref`, `ee-label` for disassembly and labels. Describe
   only the observed load/call/data flow; do not invent names or a
   causal edge where the addresses do not prove one.

Deliver at most 45 lines in `REPORT.md`: revision, exact commands,
`claim | data flow | source:line/address | LSP confirmed? | gap` rows,
and a short `Unconfirmed` section. Every claim needs a source anchor.
Write the report **before** doing any broad search. Acceptance:
`test -s local/research/X4B/REPORT.md` and
`wc -l local/research/X4B/REPORT.md` ≤45; report must contain
`sceCdReadClock`, `0x31ae80`, and `0x3177C8` (even if a link is
unconfirmed). Time box 25 minutes. No build, boot, device, network,
fork edit or push. Commit `[X4B]` with trailer
`Orchestrated-By: opencode`; `local/` is gitignored, so use `git add -f`
with the explicit report path. Do not stage other lanes.
