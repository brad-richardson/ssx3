# E15 required receipts before extension and boot

| Probe | Read-only site / required receipt | Limit or interpretation |
|---|---|---|
| Create / register | Existing dispatcher, original a0–a3/t0, PC/source/RA/SP, actual target and return; record Create `0x4027b8`, AddCallback `0x402c08` | Shadow registration is an observation of API arguments, not a read of the private MPEG callback map |
| Picture request | `0x402a10`, same-run MPEG identity and image, typed scheduler wait, original continuation | Existing GetPicture wait message plus its exact source branch proves empty frame queue, !EOF, !ended, !failed and logs sawInput. No MPEG source edit or new private-state accessor |
| Selection / delivery | Scheduler queue/invoke observations for dynamically registered callback targets; scheduler and nested dispatcher entries, original ABI args, first callback-data word, return/unwind | Queue selection and actual invocation are separate counts. No dispatch is not a valid no-input return. Private selector eligibility is evaluated separately from pinned source |
| Guest source | Exact entries `0x3b0b10`, `0x3b0b40`, `0x3b06b0`, `0x3b06f8`; registered userdata and range-guarded +0x28/+0x78/+0x7c | Callback userdata must join registration and callback a2. If callback never enters, source behavior remains unobserved |
| AddBs / completion | `0x4029d0` original MPEG/buffer/count; bounded source hash/bytes; wrapper return count; scheduler completion type/token/matched waiter count | No AddBs call means no decoder-result inference. Any internal decoder detail not exposed by existing logs is an explicit gap |
| Lifetime | MPEG reset/init and available delete/remove bindings; recorded Create lifetime and stream terminal log; observed call/return/unwind balance | Do not invent an absent Delete binding or infer EOF from callback v0=0 |
| Guards | Existing constructor, UI pointer, leaf/flag/state, S singleton/slots | Dynamic constructor/store checks required before interpreting object fields |
| Graphics | Guarded UI old=3/new=6 write arms E4 at next VBlank and freezes one tick later; same window retains E7 copy bytes | At most 16 packet files / 512 KiB; this run's packet→GS/source→D→field-Present join, or exact gap |
| Closure | Runtime destruction emits sink shutdown footer even when no more guest events arrive | Counts/budget/truncation plus E15 entered/returned/unwound/pending counters; normal window end and shutdown are distinct |

The original ELF is the primary ABI contract for this binary. At
`0x402c08`, registration indexes `(type << 3)` and stores function/userdata.
`0x402c30` loads the callback by `cbdata[0]`, invokes it with unchanged a0
(MPEG), a1 (callback data), and a2 (stored userdata). `0x402c80` initializes
only the type word to 1 and discards callback v0, returning 1 itself.
The IPU busy loops, e.g. `0x406e80..0x406ea4`, invoke that type-1 dispatcher
when the polling counter reaches the `0x1389` threshold. The guest callback `0x3b0b10` reorders those
three arguments for `0x3b0b40`; it does not inspect a stream-event layout.
The helper calls AddBs even on its no-source branch, using a 16-byte MPEG
sequence-end buffer. These are raw-word/verified-OUT receipts, not PSP ABI
assumptions. Retained disassembly contains complete range tails.

The actual-wrapper fixture will register a synthetic guest callback through
the real AddCallback binding, call the real GetPicture binding in the
scheduler, and stop at a bounded observer thread after the request parks.
Separate no-input and AddBs-reentry callbacks will count selection/queue,
invocation, completed no-input return and input delivery separately. Neither
callback is called manually. Both expected-delivery cases must fail before
any future fix; E15 makes no fix. Prior binding regressions remain separate.

**E15 PROBE TABLE TAIL COMPLETE — recorded before tap/fixture extension.**
