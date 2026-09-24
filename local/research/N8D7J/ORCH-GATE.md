# N8D7J orchestrator gate — static path PASS, proposed classifier rejected

Read the full worker report and 12-row map, checked worker commit
`a1632be9` and source anchors in the pinned N8D7F fork. No build, replay,
device action or GS cause verdict. The path map is useful: the 4 MiB
`buffers.gpu` copy is made before circuit1, mapped after `wait_idle`, and
the logged selected `input` is a **CPU decode of that raw snapshot**, not
a raw-byte tally. CPU input and GPU circuit use the same `swizzle_PS2`
family/base, so their 448/448 equality cannot independently validate
the address algorithm. Android prints `unavailable` for the raw SHA.

**Correction:** the proposed contiguous FBP-window nonzero-word count
cannot classify sparse VRAM versus conversion loss. The selected field
uses phase/stride and GS page layout; the suggested linear span does not
prove it covers the displayed addresses. Even a high count in a broad
window could come from unrelated bytes. The report's A/B categories and
"only observation" claim are therefore *not accepted*. No run is
released from this design. A useful successor needs an independently
checked PSMCT24/FBW8/FBP112 address oracle or a source-side write trace,
then exact raw word values at the selected coordinates from the **same**
Odin frame, with a null control and bounded logs. The Mac/Odin streams
remain different.

Verdict: static source path PASS with this correction; raw VRAM content
and the source of the sparse image are still unknown.
