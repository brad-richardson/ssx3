# E7 — experiment contract, recorded before either boot

## Authorized updates after E7a (before E7b)

The orchestrator approved EF's copy/FIFO-first framing after E7a had
already completed. E7a used one boot and confirmed S=0x61ba60. Its owned
lease was released at 04:21:32.971Z. A subsequent explicit scope expansion
authorizes up to **four boots total**, runtime fixes and tests if H-FIFO
is confirmed, and a meaningful frame: P→D packet consumed, D VRAM nonblack
with expected content, and faithful Present reading D. No regeneration.

E7b adds observation-only taps at the named interfaces, gated by
`PS2X_E7_DIR`: singleton/field stores before mutation; CPU FIFO command;
memory FIFO mask/queue before and after; interpreted MSKPATH3; normal GIF
DMA bytes; PATH3 queued/sent/flushed; GS packet entry. Ordered records go
to one separate file, capped at 4 MiB for boot and 1 MiB reserved for
ticks 599..603. Packet snapshots add at most 512 KiB; outer E7-directory
cap is 8 MiB. The original E4 window stays 600→601. This supersedes the
initial zero-new-code plan below; these taps do not alter guest semantics.
P1f watches add FIFO 0x10005000 and GIF CHCR/MADR/QWC to the guarded
singleton, fields, and display set. A meaningful-frame implementation
will be a separate change after the hypothesis is resolved.

Stop conditions from the expanded brief: unexpected M/slots/H-pair
(follow outcome-ii residual); H-FIFO falsified (follow the first named
missing edge); ingress fix still leaves the copy unconsumed (table it,
do not stack fixes); or any fourth-boot cap. Never exceed four total
boots, 600 seconds each, with a fresh lease and three classes of caps.
Fork commits go to the fork remote only; ssx3 evidence is not pushed.

The initial contract follows as a record of the plan used for E7a.

Handover received by 2026-09-21 04:13:16Z; six-hour deadline 10:13:16Z.
EF committed first as `c8727de`. E6 `57e1afb` REPORT read in full through
its tail; E5 watch-series and capture/miner shape read. This E7 follows the
newly authorized two-boot recipe. EF's alternative combined capture is
not the execution plan.

| Hypothesis | Observable | Alternative / selected outcome |
|---|---|---|
| H-S | Factory publishes S at 0x4a289c; historical candidate 0x61ba60. | E7a reads the actual store value; E7b also watches the pointer to check cross-boot stability. A mismatch invalidates the field-address join: (iii). |
| H-fixed / H-pair | M=1, A=P=0, B=D=112; C increments each display call; G explains pick-vs-skip only. | Unexpected values with complete coverage select (ii), with the specific residual followed statically. |
| H-gate | G set/consume series is writer-attributed; the guest fixed-buffer choice may be intentional copy mode. | G alone does not measure unique fp-user call rate; count writes by PC and report observation limits. |
| H-parking | With values confirmed, static whole-function copy and submission logic names the operation that should join P→D. | (i) only when values and parking question have a named next action. An emulator gap may be named statically without its same-window causal receipt being complete; report that distinction. |
| H-measurement | Both boots preserve complete watch series and E4 600→601 history/Present inputs. | A cap, damaged boundary, or unresolvable event join selects (iii): measurement repair only. |

E7a: one boot, watch singleton `0x4a289c` plus E5's seven display
addresses. E7b: one boot, watch the seven S-relative fields from E7a
(`+0x5a78,+0x5a7c,+0x5a84,+0x5a88,+0x5a74,+0xf44,+0x59e8`), plus the
singleton guard and the same display set. No additional FIFO/DMA watches,
new taps, runtime code, regeneration, backend changes, or fixes in E7.

P1f watch windows are eight bytes wide. Adjacent S-field windows overlap;
the miner must count emitter multiplicity before identifying distinct
stores. For RAM stores, repeated watch matches must not be mistaken for
multiple guest writes. PMODE/MMIO macro/Store duplication is retained and
dispositioned separately, following E5. Preserve raw lines and writer PCs.

| Stop / cap | Per boot |
|---|---|
| Successful boundary | E4 arm 600, freeze 601, `[e4:span-complete]` + 10 seconds grace, as E5. |
| Wall | 600 seconds, including termination budget; SIGTERM initiated with 15 seconds reserved if no earlier bound. |
| Progress | 1,000,000 syscall trace lines. |
| Boot log | 800 MiB. |
| Syscall trace | 64 MiB. |
| Default function log | 512 MiB. |
| E4 outputs | 12 MiB. |
| Park outputs / frame outputs | 32 MiB each. |
| Aggregate captured streams | 1 GiB. |
| Monitor | 250 ms checks; progress/byte values printed every 5 seconds. First detected cap binds; overshoot, if any, is measured. |

Before each boot: lease absent, `pgrep -x ps2EntryRunner` exit 1,
E5 runner SHA/size, ISO/ELF sizes and matching ELF hashes, SSD/internal
free space, fork status, latest wait-log tails, trace-aligner selftest,
and 448-test suite green from fork root. No rebuild needed if the pinned
runner and test binary are unchanged. Any required build is -j4, no regen.
If the lease is taken, log WAIT to P1/run/e7-waits.log and retry only at
five-minute intervals; never run alongside another P-lane owner.

Claim is exclusive-create and ownership-tagged. Run in the foreground
from P1/run with absolute ELF/ISO paths. On the first binding condition,
SIGTERM only this child, wait at most 15 seconds, then kill only that child
if necessary. Preserve the closed default function log with a same-volume
rename during cleanup so a later owner cannot overwrite it, then release
the owned lease immediately. No analysis while holding it. Log release
and verify runner absence. Compress closed raw streams lease-free and
retain single canonical copies plus hashes.

The final report will give tables, hypotheses, gaps, exactly one outcome
(i–iii), and one next action. No SIF/CD promotion without a named
dependency; no raster/Present fix follows from this window. No ssx3 push;
evidence commit prefix `[E7]`, trailer `Orchestrated-By: Muse Code`.

Tail receipt: initial E7a contract and authorized pre-E7b expansion both
complete. Revised maximum four boots total; no regeneration; owned lease,
pre-claim checks, and byte/progress/wall caps on every boot.
