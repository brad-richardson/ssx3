# CT1 — read the silent counters on the F1 fold: coverage, VU1 caps, INTC handlers, the code overlay (muse, 2 h, Mac)

Review `docs/research/review-2026-09-25-fable.md` §1 suspects 2–4 and §6 items 1, 2, 5: the fold may now reach code we never recompiled, and several failure counters exist but are never read.
**New fact (orchestrator, 09-25):** `DATA/CONFIG/SLUSOVF.BIG` is a BIGF archive holding `overlay.dat` (0x1903ac bytes, starts with a **relocatable MIPS ELF**, `e_type=1`) and `config.dat`. Before AU9's `0x3E3968` override its lookup failed; now it can load.

Questions and observables (base fork `ssx3` **`56a5e8a`**, worktree `~/dev/ssx3-work/CT1/PS2Recomp`, branch `ct1-counters`):
1. **Overlay:** does the game open `SLUSOVF.BIG`/`overlay.dat` on the I26-FAST route (CD read log), where does it load it (EE address, `ee-xref` the loader), and does execution ever enter that range (missing-function targets in it)? Also list its ELF sections/symbols (host `llvm-readelf`/`llvm-objdump` on the extracted file; the ISO is `~/dev/ssx3-work/E32-inputs/SSX 3 (USA).iso`, extract with `bsdtar`; **extracted game data stays in scratch, never in git**).
2. **Coverage:** get the `[coverage:missing-functions]` line (printed at exit: make the boot exit cleanly at t2400, or add a default-off env that prints it at a tick). Table every missing target with the caller PC.
3. **VU1 cap hits:** `PS2X_GFX_STATS` (or `ps2_gfx_stats::noteVuRun(budgetExhausted)`, `ps2_vu1_core.cpp:1954`): capped programs per vsync with startPC and cycles, to t2400.
4. **INTC:** a one-line default-off log of the cause in `addHandler` (`Interrupt.cpp:26-38`): which INTC causes the game registers (esp. 5 VIF1 / 7 VU1), and which we dispatch (`EeScheduler.cpp:2655,2860,2869`).
5. Unhandled RPC pairs vs the E56 four (F1 B1 already shows the same four: sid `80000211/1`, `80000006/ff`, `534e44/0`, `237/0`).
Budget: 1 build, ≤ 2 det boots (paraLLEl env as GB8, I26-FAST, empty mc0), one mini slot each, 2 h. Default-off logging only; no behaviour changes. Never push; runner-dir check empty; text only in git. Deliverable `local/research/CT1/REPORT.md` with one table per question + gaps; commit `[CT1] …` (explicit paths, `git add -f`, `Orchestrated-By: Muse Code`), no push. Hand back; the orchestrator decides.
