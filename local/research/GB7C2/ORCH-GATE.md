# GB7C2 orchestrator gate — source/trace PASS, display transfer OTHER

Worker commits: ssx3 `869f2659`, private GB4 fork `7bd8349`, both
`Orchestrated-By: opencode`; no push. I read the whole report and source
patch. The default-OFF probe scopes itself to tick600 packet47176 T4
offscreen sprites and tick601 packet47240 display blits. It takes an
independent old value before `WritePixel`, reads new afterward and diffs
the `(340,375)-(410,415)` offscreen ROI per candidate batch. The fork
commit changes only the CPU backend/header and replay harness, passes
`git show --check`, and has empty runner-dir diff vs `14b1e5cb`.

| Check | Result |
| --- | --- |
| Validation | One incremental build, flag-OFF suite 556/556, one direct CPU replay 556/556 through marker700; 59,904 packets; trace 320 rows/51,529 reported bytes, cap not hit |
| Offscreen producer | Independently parsed full 320-row trace: 48 C1-state sprites in packet47176; 166 changed traced pixels, 9 localized ROI changes of 21–80 pixels each, plus 24 same-value attempts not counted as changes. T4 nibble/CLUT/RGBA and old/new values saved |
| Carrier/crop | Packet47240 has 17 carrier batches and 17/17 stable ROI links. Its 24 sampled carrier pixels all have old==new; selected sample cap reached ROI-top background rows before glyph rows. All 65 chain-window crop rows are clean |
| Frame inspection | Orchestrator viewed tick600, 601 and 700 PPMs. Copyright text is visible at tick600/601; menu at 700 has sprite artifacts. Independently decoded PPMs: target crop `(340,360)-(430,420)` at 600 and 601 is byte-identical, while 700 differs. Tick600/700 Present hashes `a6948f2`/`97b4641e` match GB7B control |
| Source/receipt | Private fork clean, runner-dir guard empty. ssx3 commit has only brief and named text receipts. `git show --check` on ssx3 flags CRLF in selected TSV; it is tabular output, not source whitespace |

Verdict: **PASS** for the bounded CPU offscreen text-composition trace;
**OTHER** for the predeclared displayed-glyph transfer condition. The
tick601 blit may be a steady-state rewrite of text already visible by
tick600, and this trace did not sample glyph rows in the carrier. We
cannot name the displayed glyph producer or a paraLLEl damage cause
from this run. The next discriminating G test should target a known
glyph-row source/destination pair at the carrier and compare its actual
write/mask path, or use a single bounded diagnostic perturbation with
an OFF control to reveal whether the carrier transports that pixel.
No speed or GPU replay claim follows.
