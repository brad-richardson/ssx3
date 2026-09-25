# ST1 — fine horizontal stripes on paraLLEl frames (Mac, muse, 2 h, Part 1 evidence + one fix)

## Facts
- Fine horizontal stripes (alternate-line brightness) show on every Odin screen since N8D1 (`local/research/N9/REPORT.md` ~L224) and now on the Mac paraLLEl frames too (F2 B1 `~/dev/ssx3-work/F2/run/B1/frames/snap/snap-002090t-0062.47s.png`). The CPU backend and PCSX2 frames don't show them (compare `~/dev/ssx3-work/RR1/run-g/frames/upload-latest.png` if CPU, and GB8 Q3 pairs `local/research/GB8/REPORT.md`).
- paraLLEl scanout is field-combed and shifted 1–2 px vs the CPU backend (G44/G46 caveat). SSX 3 runs interlaced NTSC (SMODE2 INT/FFMD), `PS2X_DEINTERLACE` exists in the bundled envs (check what it does and whether Mac boots set it).

## Hypotheses → observable
| H | Mechanism | Observable |
|---|---|---|
| H1 | presentation weaves two fields (or shows one field line-doubled with the other field's stale lines) | stripes' line parity flips frame to frame; per-row mean brightness alternates with period 2; changes with `PS2X_DEINTERLACE` / paraLLEl's deinterlace/scanout options |
| H2 | the game renders field-offset frames (FFMD=1, half-height buffers) and we scan out at full height without the field offset | DISPLAY1/2 DY/MAGV and SMODE2 values vs PCSX2's for the same scene; paraLLEl's `vsync` field parameter |
| H3 | a shader-side sampling offset (half-texel) in the scanout blit | stripes present even on a single static full-frame buffer read |

## Steps
Base fork `ssx3` `96e9f45`, paraLLEl `19d93b2`, canonical codegen; worktree `~/dev/ssx3-work/ST1/`. Read how paraLLEl presents (the PS2Recomp paraLLEl backend `vsync`/scanout call and its options; cite file:line). One det boot (paraLLEl env + `PGS_HIER_BINNING=force`, `PS2X_SOUND=1`, I26-FAST, empty mc0) with frame dumps at a static menu (Select Peak ~1090) and race 2100, plus the GS privileged regs (SMODE2, DISPLAY1/2, DISPFB) at those ticks; per-row mean luminance script → period-2 test; the same frames from the CPU backend for contrast. One candidate fix if one mechanism is named (e.g. the right field/deinterlace mode in the paraLLEl vsync call), one validation boot, frames viewed. No tuning loops.
Budget: ≤ 2 builds, ≤ 3 boots, 2 h. Never push; runner-dir check empty; text only in git (row-luminance tables as text). Deliverable `local/research/ST1/REPORT.md`; commit `[ST1] …` (`git add -f`, `Orchestrated-By: Muse Code`), no push.
