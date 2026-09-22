# E29 CONTRACT — bounded DEV-ONLY movie bypass

Written BEFORE the branch was cut, before a byte was configured or built, and
before any lease was claimed. No amendment is declared unless it appears below.

## What this lane is, and is not

E29 buys **REACHABILITY** (menu/race on the recomp runtime), not understanding.
It is **NOT a fix**. It claims nothing about the stall mechanism beyond what it
demonstrates. Understanding + the faithful fix is **E30**.

## Bounds, as the brief sets them

| Bound | Value |
|---|---|
| Time box | 8 h, opened `2026-09-22T16:01:18Z` |
| Flag | `PS2X_SKIP_MOVIE` — exact name, no variants. Default **OFF**. |
| Branch | `e29-movie-bypass`, cut from exactly `3adc0478b6d2260acdd28a249466f2eef9a20176` |
| Worktree mutations permitted | EXACTLY TWO: the branch checkout, and the Mission-1 bypass diff. No opportunistic edits, no regeneration, no `git worktree add`, no second clone. |
| Commits | `[E29]` evidence in `~/dev/ssx3` only; bypass commits on `e29-movie-bypass` ONLY; never merged; **zero pushes**. |
| Boots | UP TO TWO, one at a time, each claimed/released per the P-lane protocol. **No third boot for any reason.** |
| Boot 1 | flag OFF — MUST reproduce e28a's terminal state (bar below) or the bypass is CONTAMINATED: table + STOP, no Boot 2. |
| Boot 2 | flag ON — only if Boot 1 green. |
| Fix gate | **NOT APPLICABLE** (scaffolding, not a fix). Gate file still written, recording that + the E30 handoff. |
| Byte caps | NEW SSD build dir ≤ 6 GB; NEW SSD `e29-*` paths ≤ 16 GB total; internal volume ≤ 512 MB delta; **NO /tmp build** (the floor forbids two trees); evidence text-only; `COPYFILE_DISABLE=1` on every SSD step; **zero deletions**. |
| Watch vector | E28's **243** entries carried UNCHANGED. No new watch design this lane. |
| SSD rule (standing, link PROVEN pattern-dependent corrupt) | every build-output byte needs **2+ matching reads separated in time AND corroboration**. If `/Volumes/Extreme SSD` disappears mid-run: table + STOP immediately, do not improvise paths. |
| Preserved constraints (E18 ABI, BINDING) | The bypass adds one env-gated block inside one host stub and one trace counter. It changes **no** ABI, **no** callback semantics, and **nothing** on the default (flag-off) path. |

## Declared label

The boot labels are `e29a` (Boot 1, flag OFF) and `e29b` (Boot 2, flag ON), by
the same mechanical rename that carried E24's driver into E26 and E26's into
E28. Label-derived output destinations differ; every other driver key and value
is identical to E28's.

## Declared ELF difference — the one fidelity row that CANNOT be carried

E15–E28 all booted one binary and pinned it by SHA (`1b49d05c…7af7bc`,
3,890,784 B). **E29 builds a new one**, so the boot-fidelity check's ELF-pin row
cannot be "equal to E28's" and is replaced by a **stronger, two-sided**
statement, recorded before the build:

1. the NEW binary is built from `3adc0478` **plus the Mission-1 diff and
   nothing else** (branch diff receipted in full, `git status` clean but for the
   one file);
2. the NEW binary passes the **full 458-test suite with the flag OFF** — the
   faithful-equivalence gate; and
3. Boot 1 (flag OFF) reproduces e28a's terminal state byte-for-byte on the
   pre-registered bar.

Any other reading of the new ELF's SHA is not claimed.

## Order (strict)

tooling bootstrap + hex-safe carry + proof → **carry audit** (E28-E1 mitigation,
before the first gate) → **fork gate (first gate, mainline)** → CONTRACT →
**Mission 1** (static mechanism + checkpoint + limits; table+STOP if no
mechanism) → **Mission 2** (branch checkout AS LATE AS POSSIBLE → diff → SSD
build → 458 flag-off → check back to mainline → triple-agree) → **Mission 3**
(Boot 1, then Boot 2 only if Boot 1 green) → E30 handoff → fix gate → close.

## Coordination with the V1 lane

The V1 worker is auditing fork HEAD concurrently. The branch checkout is
therefore deferred to the **start of Mission 2**, not before; checkout and
check-back times are recorded; mainline must be triple-agree + clean at close.

## AMENDMENT A1 — declared before the configure step, no build byte written

Internal delta cap **512 MB → 32 MiB**, and the `bound()` trip for it changes from the absolute `IRES-128*M` to the scaling `IRES*3//4`. The second half is part of the same amendment and is recorded because it changes *when the lane stops*, not only where it builds: `IRES-128*M` goes negative once the cap is right-sized, so it would have fired unconditionally and stopped E29 on an arithmetic artefact rather than on a real bound. FLOOR (2 GiB), GUARD (0.5 GiB) and both
SSD caps are **unchanged**. Reason: the carried `admission()` reserves the whole
remaining internal cap as free headroom above the floor — E28 semantics, where
that number sized an internal BUILD TREE. E29 builds on the SSD and writes only
text evidence internally (E28's comparable directory: 980 KB). Receipt:
`amendment-A1.json`. The amendment does **not** lower the floor: `bound()` still
stops the lane the moment internal free reaches 2 GiB + 0.5 GiB.

Standing risk, named here because it caused the trip: internal free fell from
3.10 to 2.78 GiB **during** this lane, from activity outside it (the volume sits
at 99%). If it reaches the floor, E29 tables and stops.
