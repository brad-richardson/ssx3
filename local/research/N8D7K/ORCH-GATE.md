# N8D7K orchestrator gate — independent address oracle PASS, sparse classifier corrected

Read the full report and ten-row map; checked worker commit `8324a3ce`
and the fork/G43 source anchors. The fork's literal `GSPSMCT32` tables
do not call G43's bit-arithmetic `swizzle_PS2`; its header SHA
`9635a40e…95e71f7` is identical in the older canonical checkout and
the N8D7F private fork. Fork CT24 reads/writes use the CT32 page table.
Eight table-derived byte offsets for FBP112/FBW8/PSMCT24 matched G43
8/8 after independent calculation, including base `0xE0000`, page
boundaries `0xE2000`/`0xF0000`, and far corner `0x1BFFF4`.
All are distinct and inside 4 MiB. This is an independent implementation
check, not proof against a shared GS-spec misunderstanding; no PCSX2
third mapping source was available locally.

**Correction:** six selected words cannot classify the whole 512×224
image as sparse. Even if five are RGB-zero, active data may sit elsewhere;
if a word has nonzero RGB below the ≥32 census threshold, a black tile
is not an address/decode failure. The report's A/B table is therefore
not accepted as a frame-level discriminator. A valid successor should
use this independent fork-table oracle to decode **all 512×224 selected
RGB pixels** from the same 4 MiB snapshot (PSMCT24, phase/stride)
and compute the same 448 tile counts, then compare its full vector with
the existing G43 input/circuit/stage vectors. Keep literal offset checks
and a known-populated control, but do not classify from a handful of
samples. No build, device run or GS cause claim occurred here.

Verdict: static address oracle PASS with this scope correction. Next:
N8D7L bounded full-frame independent-oracle diagnostic design/build.
