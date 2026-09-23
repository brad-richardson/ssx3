# AU2 — Sound spike: SND protocol table + deliver the IOP tick; is the menu music mixed on the EE or the IOP?

You are the AU1 worker (same pane and context). Follow `~/dev/AGENTS.md`.
**Tables + receipts; recommend, the orchestrator decides.** Scope is
exactly AU1-6's proposal:

1. **Part A (static):** disassemble SNDDRV.IRX with its symbols
   (`SNDIOP_dmqueue`, `dmservice`, `dmathread`, `threadmain`,
   `dispatchrpc`, `init`) plus the EE packet builders `0x3C4450`/`0x3C43C0`
   and the cid-1 handler `0x3C1578`. Output a protocol table: cid-0 fields,
   cid-1 types, the RPC fno 0 payload including `0x0050B740`, and who DMAs
   what where.
2. **Part B (spike, env-gated, default off, e.g. `PS2X_SND_TICK=1`,
   worktree off fork `ssx3`, branch `au2-snd`):**
   - deliver cid-1 type-2 packets to the registered EE handler at a fixed
     host rate;
   - log every cid-0 packet and SIF DMA descriptor;
   - dump the candidate `dmqueue` source ranges.

   Observables:
   - sema 36 signals > 0;
   - the `0x50A8E8+0x180` counter advances;
   - `charsel.mus` reads continue past 194 KB;
   - the dumped ranges hold either PCM (write a WAV and say whether it's
     music) or XA blocks (match them against `SCDl` payload bytes from
     MUSIC2.BIG).
3. Hand back which case it is (**EE-mixed PCM vs IOP-side XA**) and the
   next-brief shape. No audio output wiring yet.

1 build, ≤2 Mac boots (one slot each; the mini is busy, so wait for a
slot and use `nice`), 4 h, cap 2 GB. `local/research/AU2/REPORT.md`.
`[AU2]` commit (`git add -f local/research/AU2 local/muse/prompts/AU2.md`,
`git log -1` first, trailer `Orchestrated-By: Claude Code`). Fork commits
stay on local `au2-snd`; no push.
