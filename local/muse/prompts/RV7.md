# RV7 — what other PS2 emulators do that we should learn from (GPT Astra, read-only research + web, ≤ 2.5 h)

Brad (09-26): look at PCSX2's tricks and the newer PS2 emulators for anything worth adopting in our static-recompilation runtime (performance first, then correctness and features). You are a researcher: read, search, reason, write one document. No builds, boots or source edits.

## Our situation (read these first, briefly)
- `docs/research/review-2026-09-26-astra-perf.md` (RV4: where Odin time goes today, ranked levers) and `docs/numbers-ledger.md` (current numbers). Architecture: EE code statically recompiled to C++ (`~/dev/PS2Recomp`, branch `ssx3`); VU1 microprograms statically recompiled per image (VR1/VB1/VR2 reports in `local/research/`); VU0 still interpreted; GS on paraLLEl-GS (Vulkan compute) with a GS worker thread; SPU2/IOP by HLE; Odin 3 (Snapdragon, Turnip), iPhone/iPad (MoltenVK), Mac. Brad parks threading splits (e.g. VU1 on its own thread) during the get-it-working phase; correctness gates (det-hash) are non-negotiable.
- Local PCSX2 source excerpts: `local/research/Q1/src/` (microVU files). Q1 (`local/research/Q1/REPORT.md`) already covered microVU hazard/flag analysis: don't repeat it.

## Survey (use web search; cite URLs and, for code, file + commit or permalink)
1. **PCSX2:** speed hacks and their correctness trade-offs (MTVU, EE cycle rate/skip, INTC/vsync wait-loop detection, instant VU1, fast CDVD, VU clamping modes), GS hardware-renderer tricks relevant to paraLLEl (texture/CLUT caching, draw batching, readback avoidance), and **game patches for SSX 3 specifically** (pnach files: 60 fps, widescreen, any "fps unlock": what they change, which addresses; these may directly inform our 120 Hz work and our widescreen mode).
2. **AetherSX2 / NetherSX2** (ARM64 JIT on Android; the Odin-class baseline): what they did differently from PCSX2 for ARM (register allocation, fastmem, VU recompiler, threading, Vulkan/Adreno workarounds).
3. **Newer/other projects:** find the currently active PS2 emulators and recompilers (e.g. Play!, ARMSX2 or other Android forks, any static-recompilation or "decomp"-style projects, PS2Recomp's upstream and forks, other recomp toolchains such as N64Recomp/XenonRecomp whose techniques transfer). For each: what's novel, maturity, license, and whether a technique transfers to a static recompiler.
4. **Rank transferable techniques** for us: expected benefit on the Odin (ms per frame or a qualitative band), cost, risk to exactness, and whether it conflicts with Brad's parked items. Tag **do now / queue / park**, with a one-paragraph brief sketch for each "do now".

## Rules
Read-only; web search allowed. Licensing: note licenses; we don't copy code into our forks from GPL sources without Brad's decision, so describe techniques, not code. Don't contact anyone upstream.

## Deliverable
`docs/research/review-2026-09-26-astra-emulators.md` (≤ ~400 lines), commit `[RV7] …` with the explicit path, trailer `Orchestrated-By: Codex`, no push.
