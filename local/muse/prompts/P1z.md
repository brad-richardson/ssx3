# P1z — Settle P1v's provisional rule from the EE kernel disassembly

You are muse in a herdr panel in `/Users/bradrichardson/dev/ssx3`. **Tables,
no verdicts.** Read `local/research/P1/REPORT.md` Part 23 §P23-1a/b first
(P1v's evidence table: all written sources silent/LLE, host rule uncited,
game-as-oracle decisive → exact-zero treated as binary sema, recorded
PROVISIONAL), plus `docs/research/review-2026-09-19-progress.md` §4.4/§7.5
(the game-expects-X rule). This brief settles the rule from the one
source P1v could not read. No fork edits — the amendment, if any, is a
later brief.

## Facts you start from

A PS2 BIOS dump is in-repo at
`local/emulator/course-cleanup/profile/PCSX2/bios/ps2-bios-0200a-20040614-100909.bin`
(verify, do NOT assume). The stock EE kernel's `CreateSema` validation is
in there. Two questions: (1) does the stock kernel accept `max_count=0`?
(2) stored-max semantics — clamped, stored-0, or other? P1w/P1x/P1y run
concurrently in other panes — you share nothing with them.

## Gates and rules

- READ ONLY everywhere: no fork writes/commits/pushes, no fork boots, no
  lease, no `adb`. Work on a COPY of the BIOS under
  `/Volumes/Extreme SSD/ps2x-p1z/` (new dir — analysis tools write
  sidecars; the in-repo dump stays pristine). Internal disk is tight,
  heavy artifacts stay on the SSD. Installed disassemblers only (check
  what exists: Ghidra? LLVM/ Capstone mips? — table, never download).
- Evidence dir `local/research/P1z/` (STANDALONE — do NOT append to
  `P1/REPORT.md`). Commit with `git add -f`, prefix `[P1z]`,
  two-trailer convention (copy from the previous ssx3 commit). NEVER
  run `git push` in ssx3.
- Time box 4 hours.

## Steps

1. **Locate.** Find the EE kernel `CreateSema` in the BIOS copy
   (syscall table, strings, cross-refs — record the method + address).
   If it cannot be located with installed tools, stop after Step 4
   with the exact blocker (the negative result IS the deliverable).
2. **Disassemble.** The validation path only (entry → max/init checks →
   return): instruction table with addresses, no heroics beyond the
   create path.
3. **Answer.** (1) max=0 accepted? (2) stored-max semantics? Then the
   verdict table: P1v's clamp-1 rule CONFIRMED or AMENDED (exact
   amendment spelled out), or UNSETTLED → per-game TOML quirk per §7.5
   (exact quirk text proposed, not applied).
4. **Report.** `local/research/P1z/REPORT.md`: method, address,
   disassembly table, answer, verdict/amendment, exact commands,
   receipt paths, "What I could not do". Commit, stop.
