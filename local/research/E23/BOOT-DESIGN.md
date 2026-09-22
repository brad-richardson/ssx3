# E23 step 4 — the ONE title observation that confirms or kills the transfer

## What the transfer question actually is (after the complete-feed reference)

The complete-feed reference supplies a trigger point and a bound, but only one
of them survives contact with the title feed:

| Half of the rule | What the complete path shows | Transfers to the title? |
|---|---|---|
| Trigger point | The ONLY re-entry into `getMpegPicture` after a producer dispatch is the `onComplete` continuation, `MPEG.cpp:2484`, `getMpegPicture(rdram,&parent,runtime,false)`. It already exists, already runs on the title, and is exactly C2a's site. | **Yes.** No invention needed; the site is exercised on both paths. |
| Loop bound | `dispatchGuestNonStreamCallback` is bounded by `nextCallback < delivery->callbacks.size()` — registration-list exhaustion, a constant 1 on both paths. The host feed loop is bounded by buffer exhaustion. Neither is a demand-round bound; no round counter exists anywhere. | **No.** The bound that lets the complete path stop is the `decodedFrames.empty()` gate at `:2469`: once a frame exists, a re-request cannot open a second delivery. On the title, frames stay empty, so that gate never closes the loop. |

So a C2a-shaped release-then-re-request self-terminates on the complete path
for free, and is **unbounded on the title path**. The one extra stop condition
that is not invention is "the producer supplied no new bytes" — and whether
that condition can ever be satisfied depends on a fact this lane has never
measured: does the guest-side source acquire more bytes after the first
5,040 B, while the caller is parked?

## The observation

**Shape.** ONE guarded title boot, identical to `e22a` in every respect
(fresh T13 pre-claims, P-lane lease, runner exec'd DIRECTLY with an
assertion that fails the run if `stdbuf` reappears in argv, the REUSED
`e4d88fdc…b38e6be` observer dylib, E22's wall/progress/byte caps), with one
change: the `PS2X_DIAG_WATCH` list is extended with the producer and source
structures the E7 tap already named on this exact run shape.

**Watched addresses** (all read off E18/E21/E22 receipts, byte-stable across
all three runs; each watch covers an 8-byte window):

| Address | What it is | Receipt |
|---|---|---|
| `0x548800` / `0x548804` / `0x548808` | source descriptor head / `data` / `bytes` | `mpeg-source-result id=8 descriptor=0x548800 data=0xd48748 bytes=5036` |
| `0x5487c0` | source object passed to `0x3b06b0` / `0x3b06f8` | `mpeg-call id=8 target=0x3b06b0 a0=0x5487c0` |
| `0x587b28` / `0x587b78` / `0x587b7c` | producer block `+0x28` sourceObject, `+0x78`/`+0x7c` buffer words | `mpeg-producer id=6 userdata=0x587b00 sourceObject=0x5487c0 buffer78=0xdc8340 buffer7c=0x30dc8340` |
| `0xdc8340` | the staging buffer AddBs actually read 5,040 B from | `mpeg-input id=10 buffer=0xdc8340 requested=5040` |

**What it measures.** Every guest WRITE to those addresses, with pc / thread /
ra / sp, across the whole window — in particular the ~66.9 s AFTER the park at
`seq=6401 tick=249`. This is a direct measurement of whether the guest refills
the source while the MPEG caller is parked. It is not available from any
existing receipt: the E7 tap only records MPEG-target calls, so a refill
performed by threads 2-6 (thread 4 ran ~300x per 5 s throughout E22's park)
would be invisible to it.

## The decision it enables — both branches are decisive

| Outcome | What it means | Decision |
|---|---|---|
| **Zero** watch writes after the park | The source never refills. A second producer dispatch would re-offer the same already-consumed buffer or return 0 bytes. | **Transfer KILLED.** C2a/C4 cannot produce a frame no matter how they are bounded; the missing bytes are not on the guest side at all. The next lane stops looking at the demand edge and looks at where the 5,040 B came from. |
| **Non-zero** watch writes after the park | The source does acquire more bytes while the caller waits. | **Transfer CONFIRMED, with a measured bound.** "Re-ask while the producer makes progress, stop on no-progress" becomes a rule read off data rather than invented, and the next lane gets a concrete fail-before. |

Either way the result is a fact about the title, not an assumption about
firmware. That is why this observation is worth the one boot; a boot that only
re-confirmed the E22 demand verdict would not be.

## Gate

If the P-lane lease is occupied: table and STOP, no boot. If any checkpoint or
pre-claim gate is red: table and STOP, no boot. The boot is spent once.
