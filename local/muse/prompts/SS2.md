# SS2 — save states on Linux (bradflix): fix the libstdc++ failures (muse, 2 h)

## Goal
Save states (SS1, fork `ssx3` `5474956`) work on the Mac. bradflix is now the correctness host (HS1), but VR2 found two failures there: (1) at plain `5474956` the suite on bradflix is **661/662** — the savestate **scheduler round-trip test** fails (Mac passes); (2) loading a Mac-saved state on Linux is **refused in section `kernel`**. Lanes on bradflix need states. Make bradflix-saved states load bit-exactly on bradflix, and decide (with evidence) whether Mac→Linux loads can work.

## Facts
- SS1 report `local/research/SS1/REPORT.md`: unordered maps are saved with bucket count + iteration order and rebuilt by reverse insertion; its test proved the order on libc++ only ("libstdc++ map order untested"); a mismatch fails loudly (`bucket count not reproducible`). Tools: `local/tooling/build/bradflix_build.sh <sha> <name> [--det]`, `local/tooling/boot/ssx3_boot.py --host bradflix` (check it passes `--save-at/--load` through; add it if not), `baseline.py` state store.
- VR2's notes on this: `local/research/VR2/REPORT.md` (2A section, when written) and its pane `vr2` (read, never prompt).
- Libraries differ: libstdc++'s `unordered_map` bucket policy (prime rehash) and insertion-order behaviour differ from libc++'s, so "same bucket count + reverse insertion ⇒ same iteration order" may not hold there.

## Steps
1. Reproduce on bradflix (Docker `ssx3-hs1`): the failing test's name and output; the exact refusal line for the Mac state.
2. Fix (one mechanism): make the restore reproduce iteration order under libstdc++ too (e.g. reserve the saved bucket count before inserting, insert in the order that yields the saved iteration order for that STL, and verify after restore), or, if order cannot be guaranteed, prove where the runtime's behaviour depends on the order and remove that dependency (sorted iteration at those sites). Keep the Mac result unchanged (suite + a Mac save/load round trip compare IDENTICAL).
3. bradflix acceptance: save at t2000 on bradflix, load on bradflix, `compare` from t2001 to t2600 IDENTICAL against a straight bradflix run; suite green on both hosts.
4. Mac→Linux: try once after the fix; report IDENTICAL or the refusing section and why (other STL-dependent layouts). Not required to pass.

## Rules
Fork worktree `~/dev/ssx3-work/SS2/PS2Recomp`, local branch `ss2` from `5474956`; never push; runner-dir check empty. ≤ 6 builds, ≤ 8 boots (bradflix slots; one Mac slot for the Mac check). Don't edit `docs/`. Text only in git; states stay in scratch. First failure: stop, save the error, hand back.

## Deliverable
`local/research/SS2/REPORT.md` (repro, mechanism, fix, both-host results, Mac→Linux verdict, commands, gaps) + an `[SS2]` commit (explicit paths, `git add -f`, trailer `Orchestrated-By: Muse Code`), no push.
