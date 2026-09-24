# N8D7L orchestrator gate — PASS, Mac independent oracle

Worker commits: ssx3 `b5200bf2`, private fork `d1ba1d4`, both with
`Orchestrated-By: opencode`. The one-file fork patch adds a default-OFF
PSMCT24 selected-input census using `GSPSMCT32::addrPSMCT32` literal
tables, independent of G43's bit-arithmetic `swizzle_PS2`. It reads the
same 4 MiB mapped selected snapshot as N8D7F. Source review confirms
512×224 pixels, RGB threshold 32, 16×16 tiles, phase/stride and 4 MiB
address bound; eight literal address controls were already checked in
N8D7K. The fixture's 13/13 result is static text/math, not a compiled
oracle unit test.

| Gate check | Result |
| --- | --- |
| Build/suite | One Release/Ninja build, no repair, 585/585 flag-OFF suite; binary SHA `a14e4e9bc3914cb89c9e596292e6aa48890063d8d3706f77cef758531c751533` independently rehashed |
| Same-stream OFF/ON | Both replay exits 0 on pinned N8D4 stream; `off.hashes` and `on.hashes` byte-identical, SHA `f038cde992d13f868b06a7acf6cee922a3096345dda39f72761d5326f67fcdfb`. OFF has zero N8D7L lines; ON has three and no OTHER |
| Oracle | Orchestrator parsed the full saved ON log: input, circuit, stage and oracle each have 448 tile entries, 64,374 occupied pixels and 300 active tiles; all four vectors equal cell by cell, including oracle/input 448/448. Eight control words logged |
| Viewed frame | OFF/ON tick2050 PPMs byte-identical SHA `8c85489e242eb8a24f96e21495728ec7c80efdd7747b40a8fb0c5e4ffea25d4d`; orchestrator viewed converted PNG: race HUD, rider and snowy terrain visible, dark lower region persists |
| Scope/cleanup | Private fork runner-dir diff vs `14b1e5cb` empty; worker commits only named source/receipts, correct trailers, no push. Mini lease released. `git show --check` flags whitespace in saved CMake/fixture logs and patch context; these are raw receipts, not source edits |

Verdict: **PASS** for the Mac same-snapshot independent decoder check.
The Mac selected snapshot is broad at this tick and G43's selected-input
vector agrees with the independent fork-table census. This does not
classify the sparse Odin selected snapshot: neither the oracle nor this
capture was run on Odin, and Mac/Odin streams have not been proved equal.
Next: package the default-OFF oracle for Android and run one pinned Odin
capture, with the same full 448-tile comparison and explicit controls.
No diagnostic wall time is a speed number.
