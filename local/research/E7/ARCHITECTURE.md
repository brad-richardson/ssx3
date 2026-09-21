# CPU VIF1 ingress contract for the E7 fix

The implemented transaction will be an aligned **128-bit CPU store** to
the translated physical VIF1 FIFO page **0x10005000–0x10005fff**. The
whole 16-byte value enters the existing VIF1 interpreter once, before
generic I/O word splitting. Existing address translation handles KSEG
aliases; the usual quadword alignment check remains in force.

Primary implementation cross-check: PCSX2's
[HwWrite.cpp](https://github.com/PCSX2/pcsx2/blob/master/pcsx2/HwWrite.cpp),
read 2026-09-21, routes aligned quadword writes on page 0x05 to
`WriteFIFO_VIF1`. Its narrower-store handlers use assumed zero-fill
behavior and explicitly identify that assumption as awaiting hardware
confirmation. E7 therefore scopes its change to complete quadword stores;
it does not introduce speculative 8/16/32/64-bit FIFO semantics.

The interpreter, including its existing payload continuation behavior,
remains authoritative for the bytes. Do not special-case MSKPATH3 or SSX3
addresses/FBPs in the fix. No forced mask reset, queue drain, display-base
change, or new guest scheduling action. The observed SQ command block is
one complete quadword containing MSKPATH3 followed by three NOPs.

Regression obligations: CPU mask-on and four-word command order;
interpreted-stream mask followed by CPU unmask; two queued PATH3 packets
flushed in order once; following normal GIF DMA delivered after them;
page mirrors/KSEG aliases; ordinary RAM, neighboring FIFO page, and
display MMIO not rerouted.

Tail receipt: width, physical aperture, alias behavior, ordering, and
the narrower-store scope limit are explicit. Source consulted for the
architecture cross-check; no reference-emulator code copied.
