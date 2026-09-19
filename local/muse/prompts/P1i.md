# P1i — SSX 3 on PS2Recomp, Part 10: diagnose the GS CSR park at 0x375d10 (no fix)

You are muse in a herdr panel, working directory
`/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp` (fork, branch `ssx3`,
remote `fork`). Runbook: exact steps, receipts named up front, **tables,
no verdicts**. Read `/Users/bradrichardson/dev/ssx3/local/research/P1/REPORT.md`
Part 9 first (P9-3 new park, P9-1/P9-2 MMIO fix), and skim
`/Users/bradrichardson/dev/ssx3/local/research/P4/REPORT.md` §5 rows
S4/S12/S17 as candidate-producer context (not prescription).
`W=/Volumes/Extreme SSD/ps2recomp-spike`. Rules exactly as
`local/muse/prompts/P1c.md` "Rules" (lease `P1i`, no adb, never commit
generated runner sources or `._*`, purge sidecars, one commit per change
with the two trailers, boots foreground ≤90 s, logs
`$W/P1/run/boot-p1i-N.log`, `PS2X_DIAG_PERIOD_MS=5000`), plus: the host
lease is currently free — still use the lease protocol (check absent,
`printf`, release immediately after any boot; if it names another
agent, poll every 5 min, log waits). Push rule: `git push` ONLY inside
this fork clone to the `fork` remote; NEVER run `git push` in
`/Users/bradrichardson/dev/ssx3`. Time box 2 hours.

## Facts you start from

Boot 1 (`boot-p1h-1.log`, binary `43aba129`) advanced thread 1 past the
MMIO park: it returned from `sub_003912A8` via `0x375a94` and now spins
at `0x375d10` in caller `sub_00375A08`, all 35 blocks, `sp` +`0x10` (frame
popped). The loop: `ld $v0,0($v1)` (`$v1=0x12001000` = GS CSR), spins
while `(CSR&0xC000)!=0x4000`. Read path per P9-3: `READ64` →
`PS2Memory::read64` → `gs_regs.csr.load()` (`ps2_memory.cpp:787-796`).
No VIF/GIF/frame/crash; CD idle; same block-0 syscall set.

## Step 1 — diagnose from the closed log + ELF + sources (no lease, no boot)

a. CSR bits: what are bits 15:14 (`0xC000`) and what does `0x4000` mean?
   Identify from the GS CSR layout (runtime code or PS2 docs in tree —
   cite file:line or doc page; never guess from memory).
b. Producers: what in the runtime ever sets/clears those CSR bits?
   Table every `gs_regs.csr` writer (grep `csr` stores): site,
   condition, and whether it fired in this boot (log evidence or
   counter). Cover the vsync worker, present path, and timer paths.
c. Consumer path: verify the `0x375d10 ld` routing — dynamic `READ64`
   or TOML-MMIO machinery? (Is `0x375d10` in `[mmio]`? Does the
   regenerated code bake a constant or compute the address?) State
   which, with the generated line.
d. State the missing producer or the misread, with exact lines/words.
   If the closed log + sources cannot answer, name the single missing
   receipt and go to Step 2; otherwise skip it.

## Step 2 — one short boot only if Step 1 cannot answer (≤90 s)

Current `/tmp/p1-link` binary (state its sha; rebuild first only if
stale), same env as boot-p1h-1, foreground max 90 s, log
`$W/P1/run/boot-p1i-1.log`. Release the lease immediately after.
Receipts: the missing Step-1 receipt only, plus the standard ladder
row (thread table, first new syscall ids, VIF/GIF/frame/crash).

## Step 3 — report

Append `## Part 10` (P10-0 lease record, P10-1 park diagnosis: CSR-bit
table + producer table + consumer routing, P10-2 ladder delta vs
boot-p1h-1, P10-3 binaries and commits, P10-4 exact commands, P10-5
what I could not do) to `local/research/P1/REPORT.md` in
`/Users/bradrichardson/dev/ssx3`; commit with `git add -f`, prefix
`[P1i]`, trailers; push `fork ssx3` from the fork clone only; remove
the lease if held; stop. No runtime fix in this brief.
