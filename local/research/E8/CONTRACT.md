# E8 — progression survey contract

Recorded before boot 1. Handover observed 2026-09-21 05:26:18Z;
six-hour deadline 11:26:18Z. E7 REPORT read in full through its tail.
Baseline fork `4acc59ffebc99561ea2b4fe8e1aa1bebbc3075f2`, runner SHA256
`4f02b144a8de09622f66aa81533097d5b7777eaf63ffab3abe80f8e73fafa290`,
161,313,936 bytes; suite 452/452. No baseline rebuild or regeneration.

| Hypothesis | Observable | Alternative / selected action |
|---|---|---|
| H-progress | Guest PC/caller and scheduler phases change beyond the copy join, with later meaningful frame content. | Menu/interactive content selects (i) only with packet/source/D/Present proof; an image change alone is insufficient. |
| H-wall | A stable guest predicate, wait, or missing emulator transition is the first wall. | Trace its producer/consumer before classifying. A named generic emulator gap permits one fix, failing regression before and passing after, then re-probe. |
| H-guest | Progress requires a guest-side decision, storage/input dependency, or unavailable coverage. | Exact predicate and missing receipt select (ii), with a concrete next probe brief; stop rather than bypass. |
| H-measurement | Complete boundary tails and aligned progress observations. | Missing/truncated causal observations select (iii): repair that measurement gap only. |

Boot 1 runs the fixed runtime forward with existing diagnostics. E7's
ordered tap retains its built-in ticks 0..603 and verifies the early
join; it is not claimed to cover later execution. The configurable E4
window moves to 6000→6001. Watch singleton, seven S fields, display
registers, FIFO and GIF DMA. Preserve periodic scheduler/stub/EE/IOP
signals, syscall PCs, full function trace, and host-frame samples.
Do not infer a memory-card/SIF/CD cause from the visible message alone.

| Per-boot stopping bound | Limit |
|---|---|
| Wall | 600 s, initiate SIGTERM at 585 s to reserve termination time |
| Progress | 1,000,000 syscall trace lines |
| Boot log / syscall trace | 256 MiB / 96 MiB |
| Function log | 1 GiB |
| E4 / E7 tap directories | 12 MiB / 8 MiB |
| Frame / park directories | 32 MiB each |
| Aggregate capture bytes | 1.25 GiB |
| Byte safety margin | Stop within 8 MiB of function/aggregate caps; others at cap |
| Poll / liveness | 250 ms / 5 s |

Run until the first bound or process exit; E4 span completion is a
milestone, not the end of the progression survey. Do not truncate active
files or discard a noisy stream to extend a boot. Terminate only the
owned child, preserve the closed default log by same-volume rename,
release the lease immediately, then analyze and compress lease-free.

Pre-claim: T13 §T13-0 shape plus E7c binary/test hashes; lease absent,
pgrep exit 1, ISO/ELF sizes and ELF hashes, SSD/internal free space,
wait-log tails, selftest ALL PASS, suite re-green. Atomic owned lease.
If occupied, log to P1/run/e8-waits.log and retry at five-minute intervals.
At most four boots total, each <=600 s, no parallel P-lane boots.

Fix only a demonstrated blocking emulator gap: forcing receipt,
generic hand-written runtime implementation, fail-before/pass-after
regressions, rebuild -j4, re-probe before considering another gap.
No raster/Present rework, speculative storage promotion, adb, or regen;
0x426230 DROP disposition still gates generated work. Generated runner
sources remain unstaged. Fork commits pushed only to fork; standalone
E8 evidence committed with [E8] and Orchestrated-By: Muse Code, no ssx3 push.

Tail receipt: hypotheses, observables, outcomes i–iii, first-boot plan,
three cap classes, lease rules, and fix discipline recorded up front.
