# E15 original-binary callback contract

Primary source: the supplied SSX3 ELF, SHA256
`1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc`.
All ranges retain raw instruction words; OUT annotations are accepted only
after raw-word equality. No PSP contract or stream-event layout is assumed.

| Edge | Exact receipt | Contract established |
|---|---|---|
| Registration | `0x402c08` loads `[mpeg+0x40]`; `0x402c0c` shifts type by 3; `0x402c1c` stores userdata at inner+type*8+0x10; `0x402c20/28` returns old function and replaces inner+type*8+0x0c | Registration is indexed by type; function and userdata are paired |
| Selector | `0x402c4c` reads the callback-data type word, shifts by 3, then `0x402c58/5c` loads/tests the corresponding function | Type selects a non-null registered callback; null means no invocation |
| Invocation ABI | `0x402c64` jalr function, delay slot `0x402c68` loads stored userdata into a2; a0/a1 are unchanged | `(mpeg, callback-data, userdata)`; supplied callback return address is the selector continuation |
| Type 1 producer | `0x402c84/94` initializes stack callback-data word 0 to 1; `0x402c90` calls selector; `0x402c9c` sets v0=1 | Only the first word is initialized here. Callback v0 is discarded; it is not an EOF flag |
| GetPicture route | `0x402a44→0x402e10→0x407520`; `0x40756c→0x4072e8`; `0x407344→0x402c80`, original MPEG loaded from inner+0x858 | The original picture path services type 1 while its bit-reader busy condition persists |
| Busy condition | `0x40731c..28`: `(MMIO[0x10002010] & 0x80004000)==0x80000000`; loop counter compared against `0x1389`; call at `0x407344`; repeat condition at `0x40736c` | Receipt names the exact register condition and polling threshold; no host-wall cadence is inferred |
| Guest consumer | `0x3b0b10..2c` reorders a0/a1/a2 as helper `(userdata,mpeg,callback-data)` | Independent consumer agrees with original selector ABI |
| Source branch | `0x3b0b68→0x3b06b0` using userdata+0x28; returned descriptor +4/+8 supplies source/length; copy/pad uses userdata+0x7c | Requires actual callback/source observation before naming a feeder failure |
| No-source branch | `0x3b0bdc..0x3b0c00` writes four `0xb7010000` words (little-endian `00 00 01 b7`) and count 16; common `0x3b0c2c` calls AddBs using userdata+0x78 | This guest's no-source branch supplies sequence-end bytes. A callback not invoked cannot be classified as this branch |
| Guest return | `0x3b0b34` sets v0=1 independently of helper outcome | No-input return and successful AddBs delivery require separate measurements |

The runtime's current API wrappers bypass these original library bodies.
Pinned MPEG.cpp records AddCallback as `stream=false`; its only map-selecting
reader filters for `stream=true`. GetPicture's empty-frame/nonterminal branch
registers a typed wait without selecting the non-stream callback. E15 tests
that request path through the actual generated wrappers. Static eligibility,
scheduler selection, actual invocation, callback return and AddBs delivery
remain separate evidence columns.

Two unrelated API differences are recorded without repair: the original
AddCallback returns the previous callback function whereas the current HLE
returns an allocated handle; original AddBs returns 1 whereas the current HLE
returns copied bytes. Neither difference is substituted for the missing
request/delivery receipt and neither is changed in this brief.

**E15 ABI TAIL COMPLETE — original ELF contract; no MPEG implementation.**
