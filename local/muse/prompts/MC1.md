# MC1 — does saving work, and is Brad's save safe? (muse, 2.5 h, Mac, scratch copy of the save only)

## Why
Brad plays with his real save on his iPhone and Odin (I31). The game now finishes races (FR1, PF1 fix), so it will try to **write** to the memory card (records, progress, settings). Our `mc0` is a host directory (`PS2X_MC_ROOT`; `docs/facts.md` memory-card rows, `local/research/E55D16/`). We've only ever proven reads. A bad write could corrupt Brad's save.

## Rules for the save
Work only on a **scratch copy** of `~/dev/ssx3-work/E55D16/mc0/` (copy to `~/dev/ssx3-work/MC1/mc0-*`), never the original, never Brad's devices, never in git (names, sizes and SHAs only).

## Questions (base: fork `ssx3` tip + PF1's fix `3c037ab` cherry-picked on a local branch `mc1-save`, so a finished race doesn't crash; canonical codegen; Mac paraLLEl env + `PGS_HIER_BINNING=force`, `PS2X_SOUND=1`, one mini slot per boot; long boots ≤ 1,800 s approved)
1. **Write path:** with a copy of Brad's save, play the FR1-R1 route adjusted for a seeded card (I31 found the seeded card shifts menus ~+200 ticks; `local/research/I31/REPORT.md` §5 has a validated seeded prefix) to the results screen and let the game save (answer its prompts with scripted presses; screenshot each prompt). Which `sceMc*` calls happen (`PS2X_TRACE_SYSCALLS` or the MC HLE log), which host files change (before/after SHAs + sizes + mtimes), and did anything get truncated, zero-filled or created oddly?
2. **Round trip:** boot again on the written copy: does the game load it without complaint and show the updated record/progress? Any "corrupted data" prompt?
3. **Empty-card path:** the same on an empty card (the test default): does it offer to create a save, and does creating one work and reload?
4. **Failure modes:** what does our MC HLE do if the host write fails (read-only dir): does the game see an error the way it would with a pulled card, or does it hang?
Hand back tables and any bug with file:line; one fix only if a single mechanism is named, with a unit test.
Budget: 1–2 builds, ≤ 4 boots, 2.5 h. Never push; runner-dir check empty; text only in git. Deliverable `local/research/MC1/REPORT.md`; commit `[MC1] …` (`git add -f`, `Orchestrated-By: Muse Code`), no push.
