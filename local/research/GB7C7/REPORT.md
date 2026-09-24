# GB7C7 — observe packet5470 texture word (OpenCode Go)

Predeclared outcomes (brief): **A** = executed sample at packet5470/batch10
has computed tap0 address `0x000bae74`, directly read CT32 word with RGB
`353341`, and the same accepted pixel write changes `dc302f3b` to
`dc353341`; **B** = sample/address/word differs while the destination write
is observed (first differing field named); **OTHER** = context gap, cap, pin
failure, missing write, or ON/OFF perturbation. A proves this single pixel's
sampled word only — not the word's earlier producer, a whole glyph, or a GPU
cause. The orchestrator gates.

Outcome: **OTHER — probe not implemented: first fork edit denied by
workspace scope permission (`../*` deny); no build, replay, or trace
produced.** Read-only audit and pins below are verified; the bounded
instrumentation design in §2 is ready for a worker with the scoped edit
exception (same exception the GB7C4 resume used, REPORT §0).

## 0. Stop record

- Attempted edit: `ps2xRuntime/include/runtime/gs/gs_cpu_backend.h`
  (GB7C7 probe decls) in private fork `~/dev/ssx3-work/GB4/PS2Recomp`.
- Denial text: "The user has specified a rule which prevents you from using
  this specific tool call" (permission `edit` deny pattern `../*` — fork is
  outside the start folder `/Users/brad/dev/ssx3`).
- Per WORKER-RULES-v2 did not retry via another tool/path. No fork file
  touched (`git status` in fork: clean, still `8966b0be`); no P-lane slot
  claimed; no build/replay/boot.
- Shared ssx3 main moved during the audit: `2075169f` → `effbf5ec`
  (`[N8D7M6] One same-stream Odin/Mac selected-VRAM comparison`); ssx3 tree
  clean. Isolation from N8D7M6 kept (no shared fork contact at all).

## 1. Pins (all verified read-only before the stop)

| Item | Value | How |
| --- | --- | --- |
| ssx3 HEAD at stop | `effbf5ec` | `git log -1` in `/Users/brad/dev/ssx3`; tree clean |
| GB4 fork `~/dev/ssx3-work/GB4/PS2Recomp` | `8966b0be` branch `gb4-parallel` | `git log -1`; matches brief pin `8966b0b`; tree clean |
| capture `~/dev/ssx3-work/GB4/run/gb4p4.capture.bin` | `a6f75fb34fceccf6fd92ad65950d16f05a140cf38a3cc2f028be32e56ad51851` | `sha256sum` (brief pin matches) |
| sidecar `run/gb4p4.paths.txt` | 1,982,063 lines; line 5471 = `5470 3` | `wc -l` + `sed -n 5471p` |
| build dir `~/dev/ssx3-work/GB4/build` | `CMAKE_BUILD_TYPE=Release`, `PS2X_ENABLE_DIAG_TAPS=OFF`, `ps2x_tests` present | `CMakeCache.txt` grep + `ls` |
| LSP | `documentSymbol` on `gs_cpu_backend.cpp:2608` → no results | per brief, code links confirmed by direct source reads instead |

## 2. Read-only source audit + bounded proposed instrumentation (not applied)

Trace plumbing inspected (all cites at fork `8966b0be`):

| Piece | Location | Reuse note for GB7C7 |
| --- | --- | --- |
| Probe decl pattern | `gs_cpu_backend.h:79-103` (GB7C5) | add `Gb7c7PacketContext` + Open/Close/SetPacketContext/Enabled after line 103 |
| Probe state + caps pattern | `gs_cpu_backend.cpp:417-490` (GB7C5, 20k rows / 8 MiB) | new `Gb7c7ProbeState` after `NoteGb7c5DirectOp` (`:658-667`); caps same |
| Batch counting | `NoteGb7c5BatchBegin` (`:574-610`), `NoteGb7c4BatchBegin` (`:1898-1971`); `DrawPrimitive` assigns per call (`:2257-2273`) | new `NoteGb7c7BatchBegin`: flag kind=1 iff `tick==259 && packet==5470 && path==3 && sprite && fst && tme && fbp==112 && tbp0==0`; hook in `DrawPrimitive` next to the GB7C5 hook |
| Executed sample | `DrawSprite` FST branch (`:2827-2840`): `texel = SampleTexture(state,0,0,1,sampleU,sampleV)` | capture `texUf/texVf/sampleU/sampleV/texel` at `x==342 && y==377 && curKind==1 && curBatch==10`; old read `ReadVramUnlocked(fpsm,fbp,fbw,x,y)` before `WritePixel` (`:2937`), trace call after (mirrors GB7C4 `:2938-2959`) |
| Tap recompute | `SampleTexture` linear path (`:2671-2678`); GB7C4 carrier re-derivation (`:2087-2124`) | new `TraceGb7c7Pixel`: recompute 4 taps, per-tap `wrapTextureCoordinate`, `ReadVramUnlocked(tex.psm,tbp0,tbw)` words, `GSPSMCT32::addrPSMCT32` addrs, `applyTexa` rgba; log actual `texel` arg (not inferred) |
| Write verdict | `WritePixel` (`:2412-2576`); GB7C4 outcome ladder (`:2130-2162`) | same TEST/ALPHA/Z evaluation on independent old value; `accepted-write-changed` vs `*-same-unknown` vs `test-rejected:*` |
| Harness | `ps2_gs_replay_tests.cpp:426-532` (probe open/exclusion), `:634-652` (context), `:849-925` (PPM/sample/stop), `:1035-1055` (close/assert) | new `PS2X_GS_REPLAY_GB7C7_TRACE` (direct-CPU only, exclusive with GB5/GB5B/GB7B/GB7C2/GB7C4/GB7C5 both directions); `SetPacketContext` per packet; stop `tick >= 301`; close + `GB7C7 replay reached marker 301` |
| Expected rows | — | 1 batch row (packet5470) + 1 pixel row (batch10, `(342,377)`); ≪1 MiB trace |

Predicted values the trace must show for A (GB7C6 §3c): taps
`(343,378);(344,378);(343,379);(344,379)`, `fx=fy=0`, tap0 addr
`0x000bae74`, tap0 word RGB `353341`, dst old/new `dc302f3b`→`dc353341`.

## 3. Validation (not run — stop rule)

No build, suite, ON/OFF replay, hash/PPM comparison, or frame view: the
single allowed instrumentation edit was denied, and the brief permits one
incremental build plus two replays only after instrumentation. No GPU
replay, no speed claim, no device action was attempted.

## 4. Observation table

| Field | Value |
| --- | --- |
| tap0 address / word / RGB | not found (no trace) |
| taps 1-3 addrs / words | not found |
| interp / quant UV | not found |
| TEX0/TEX1/CLAMP/TEXA/FRAME/TEST/ALPHA/PRIM/RGBAQ | not found |
| dst old / new | not found |
| packet / tick / path / batch | pin-verified statically (5470/259/3/—), not executed |

## 5. Gaps / recommended next action

- Gap: everything in §4. The only blocker is the workspace edit permission;
  the design in §2 is complete and bounded, and pins/build-dir are verified.
- Recommended next action: rerun this exact brief in a pane with the scoped
  edit exception for `~/dev/ssx3-work/GB4/PS2Recomp` + `~/dev/ssx3-work/GB7C7/`
  (GB7C4 precedent), reusing §2 verbatim: apply the 3-file edit, one
  incremental Release build, flag-OFF suite, ON + OFF direct-CPU replays
  (`PS2X_GS_REPLAY_STEP=50`, PPM ticks `259,300,301`, stop marker 301), then
  the `check.py` acceptance below.

## 6. Receipts

- ssx3 (this dir): `REPORT.md`, `check.py`, `check-result.txt` —
  to be committed `[GB7C7]`, `Orchestrated-By: opencode`, no push.
- No fork commit (no fork change), no scratch output (`~/dev/ssx3-work/GB7C7/`
  holds only an empty `run/` dir), no P-lane lease touched.
- `check.py` verifies the §1 pins plus the stop condition (no trace ⇒
  OTHER with first-mismatch reason); result in `check-result.txt`.
