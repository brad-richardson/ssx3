# SS2 — save states on Linux (bradflix): fix the libstdc++ failures

Worker: Muse Code, brief `local/muse/prompts/SS2.md`, 2026-09-25 ~21:15–22:45 EDT.
Fork worktree `~/dev/ssx3-work/SS2/PS2Recomp`, local branch `ss2` from `5474956`
(never pushed; bradflix holds the commits under private ref `refs/ss2/fix`).
No push anywhere. No `docs/` edits.

## Outcome

**Both bradflix failures are fixed with one mechanism.** A bradflix-saved state
(t2000) loads on bradflix and runs **bit-exactly**: det-hash IDENTICAL
t2001–t2600 vs a straight bradflix run, SND guest counters identical, frames
match straight runs (see the jitter analysis). Suite is green on both hosts
(667/667, +1 new test). The Mac result is unchanged (suite green, Mac round
trip IDENTICAL, frames 3/3 equal to SS1's A4 values). Mac→Linux loads still
refuse, now in `syscalls` instead of `kernel`, for a precise reason (below);
cross-STL loads need the order dependency removed (brief's option B), which
is a bigger change and was not required.

## Repro (bradflix, Docker `ssx3-hs1`, plain `5474956`)

| Item | Value |
| --- | --- |
| Suite (non-det, VR2's `ss1base-tests`, my rerun) | **661/662**, RC=1 |
| Suite (det, my `ss2base-det` build) | **665/666**, RC=1 |
| Failing test | `Ps2Savestate / scheduler round trip is byte-identical (threads, waits, objects, deadlines)` |
| Failing output | `- load succeeds: ordered-map bucket count not reproducible` → `[Failed]` (`- all bytes consumed`, `- re-save is byte-identical` also fail) |
| Generic `unordered_map round trip` test on Linux | **Passed** (reverse insertion reproduces order on libstdc++ for non-empty maps) |
| Mac-state refusal (B1: seeded `a3efbfe-…-t2000` state on `ss2base-det`) | `[savestate] load refused: section kernel: ordered-map bucket count not reproducible` (clean exit in 1.5 s) |

Receipts: `/tmp/ss2-repro-suite.log`, `/tmp/ss2base-suite.log` (mini scratch),
run `~/dev/ssx3-work/from-bradflix/ss2-b1-repro/`.

## Mechanism (probed, not guessed)

Probe: `clang++ -O1` in the `ssx3-hs1` image (clang 18, libstdc++), Ubuntu 24.04:

| Probe | Result |
| --- | --- |
| Fresh `unordered_map` bucket count | **1** (libc++: 0) |
| `rehash(0)` / `rehash(1)` | **2** in both cases (irreproducible) |
| `rehash(64)` then insert (Mac power-of-2 simulation) | 67 (prime rehash; irreproducible) |
| `rehash(13)` (genuine libstdc++ count) | 13 (reproduces) |
| 7 sequential inserts → order | 6 5 4 3 2 1 0 (new bucket's run goes to the head, **same rule as libc++**) |
| Reverse-insertion rebuild at same buckets | order **identical** (`same=1`), no rehash during rebuild |
| Used-then-emptied (`clear()`) | buckets stay 13 (reproducible) |

So: SS1's "same bucket count + reverse insertion" rule is correct on
libstdc++ too, and fails in exactly two situations — (1) a **fresh-empty
map**, whose default count (libc++ 0, libstdc++ 1) `rehash()` cannot
reproduce under libstdc++ (both yield 2); (2) a **cross-STL** load, where
bucket counts (prime vs power-of-2 policy) and string hashes differ.

- The scheduler-test failure is case (1): `m_invocationStackTops` is empty
  in the test → saved `(buckets=1, n=0)` → `rehash(1)→2` → refuse. It is
  the only empty map in that test; all other ordered maps there are
  non-empty and round-trip.
- The B1 `kernel` refusal is case (1) cross-STL: the first kernel map
  (`m_eeExitHandlers`) is empty in the Mac state → saved `(0, 0)` →
  `rehash(0)→2` → refuse.

## Fix (fork `ss2`, two commits)

`git log 5474956..ss2` (worktree `~/dev/ssx3-work/SS2/PS2Recomp`):

- `5cce392 [SS2] Tolerate irreproducible bucket counts on empty ordered maps; verify restore order`
- `55f0c8d [SS2] Verify restore order against pre-move saved keys; test empty/string-keyed maps`

Runner-dir check `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner`:
**empty** at both commits. No section version bump: the file format is
unchanged (writer untouched); the loader is more lenient on empty maps and
stricter (verified) elsewhere. Old states load the same or better.

In `ps2_savestate.h::readOrdered`:

1. **`n == 0`: skip the bucket requirement.** Iteration order of an empty map
   is trivial. Best-effort `rehash()` toward the saved count only when it
   differs (a used-then-emptied map keeps its count on the same STL; a
   corrupt huge count is capped at 2^20 and never allocated). Fresh→fresh
   round-trips are a no-op on both STLs, so re-saves stay byte-identical.
2. **`n > 0`: unchanged exact rehash + reverse insert + shape check, plus a
   key-by-key order verification** (`ordered-map iteration order not
   reproducible`). A non-empty map whose bucket count reproduces but whose
   order doesn't now refuses loudly instead of drifting the guest
   silently. (Cross-STL loads of non-empty maps still refuse at the bucket
   check first, as before.)
3. The verification compares against the **saved key sequence copied before
   the insert loop** (`55f0c8d`): the loop moves entries into the map, so
   comparing against `entries[i]` afterwards reads moved-from strings for
   string-keyed maps. The first version of the check passed the suite (no
   string-keyed map in tests) and was caught by the B3 boot refusing in
   `syscalls`; the fix was verified by B3b loading the same file.

New test `ordered-map round trip covers empty and string-keyed maps`
(+1 suite test): an empty map round-trips, and a 50-entry
`unordered_map<string, int32_t>` round-trips with identical order and
contents. (Had this test existed with the first version of the check, it
would have failed on both hosts — the moved-from bug is STL-independent.)

## Results

### Suites (final code `55f0c8d`)

| Host | Build | Runner SHA-256 | Suite |
| --- | --- | --- | --- |
| Mac mini (det) | `~/dev/ssx3-work/SS2/build-det` | `e7607b7e…` (×2) | **667/667** |
| bradflix (det, `ss2fix2-det`) | `~/dev/ssx3-work/HS1/ss2fix2-det` | `96b8105d…` (×2) | **667/667** |

Superseded builds: Mac `e48f4754…` (first fix version), bradflix
`ss2base-det ac8b6e22…` (plain `5474956`, 665/666), bradflix `ss2fix-det
9b193539…` (first fix version, 666/666 — suite green, B3 boot caught the
verify bug).

### bradflix acceptance (fix build `ss2fix2-det`, FR1-R1, sound on, parallel 1×)

- **B2** `ss2-b2-save`: save t2000 (`saved tick=2000 eeCycle=9830598000
  bytes=52852753 sections=39`), straight through to t2602 in 119 s.
  eeCycle equals SS1's B7 save cycle — cross-host det parity at the save
  point. No CLUT tail in the file (bradflix PGS pin `19d93b2` predates
  `ss1-clut`; 1,045,262 B smaller than the Mac save).
- **B3b** `ss2-b3b-load`: load B2's state in the fixed runner
  (`loaded tick=2000 … sections=38`; 39 vs 38 is the header, counted only
  on save) after the expected cross-runner `runner_sha` warning, run to
  t2600.
- **Compare: `hash IDENTICAL ticks 2001..2600`** (`ss1_hashdiff.py`,
  base 2653 lines, cand 653, missing 0/0).
- **SND: guest-identical.** Final `tick` lines match field for field
  (`ticks=3948 counter=0x1067 cid0=531 dmq=531 done=531 setdma=4543
  tagbufs=3947`); only host-side `overflows=` differs (stripped by
  `baseline.py` as host noise).
- **Frames** (`[frame:dump]` FNVs; B2b is a second straight run, same
  binary, to separate jitter from divergence):

| tick | B2 (straight) | B2b (straight) | B3b (load) |
| --- | --- | --- | --- |
| 2100 | `ccfbda8c` | `ccfbda8c` | `ccfbda8c` |
| 2300 | `b0f544b0` | `28d05fd3` | `28d05fd3` |
| 2600 | `bdec3d64` | `bdec3d64` | `367837d1` |

Reading: B2 vs B2b differ at t2300 with det-hash IDENTICAL 1..2600, so
present jitter exists between straight bradflix runs (SS1 §Stage 3: two
straight Mac runs disagreed the same way, and there a *straight* run was
the odd one out). B3b's t2300 equals B2b's — the load matches a straight
run exactly where straights disagree (SS1's pattern). The isolated t2600
diff, with det-hash + SND + two frame ticks matching straight runs, sits
inside that documented jitter model: a GS-restore corruption would hit
the first post-load frames (t2100), not appear 600 ticks later. No
further boot margin remained to run a third straight (8/8 used); the
Mac 3/3 below corroborates the load path.

### Mac unchanged (fix build, `~/dev/ssx3-work/SS2/build-det`)

- **B4** `run-b4`: save t2000 (`saved tick=2000 eeCycle=9830600296
  bytes=53898015 sections=39`, one palette-upload deferral — cycle and
  byte count **equal SS1's P-B save**), straight to t2611 in 71 s.
- **B5** `run-b5`: load → t2614 in 27 s. **Compare IDENTICAL 2001..2600.**
- **Frames 3/3** `7ad8f18d / e6f87cdd / fad39c2b` = B4 = **SS1's A4
  values** (CLUT accessor present on the Mac PGS checkout).

### Mac→Linux verdict (B6, fixed runner, seeded Mac t2000 state)

**Refused, as permitted (not required to pass):**

```
[savestate] warning: state has a paraLLEl CLUT but this build can't restore it
[savestate] load refused: section syscalls: ordered-map iteration order not reproducible
```

Why: with empty maps tolerated, the Mac state now loads through `memory`,
`kernel`, `scheduler`, `vu0`, `vu1` and `gs` on Linux — small int-keyed
maps coincide (both STLs use prime 13-class counts there, identity hashes
assign identically). It stops at the **string-keyed** SIF-module map:
libc++ and libstdc++ hash strings with different algorithms, so the same
bucket count holds a different iteration order, and the new verification
refuses loudly. (Larger maps would refuse earlier on bucket counts, since
the prime tables diverge.) Making Mac→Linux loads work needs brief's
option B — removing the runtime's order dependency (e.g. at
`acquireInvocationThread`) so restore is order-free — plus canonical
string hashing or sorted save order. Not attempted here.

## Driver change (`--host bradflix` save/load passthrough)

`ssx3_boot.py --host bradflix` previously dropped `--save-at/--save-path/
--exit-after-save/--load/--strict` (VR2 worked around it with `--env`).
Added, guest-neutral (this lane's boots B1–B3/B2b/B6 are its validation):

- `local/tooling/boot/ssx3_boot.py`: `--save-path NAME` is sent as a plain
  file name (basename), saved as `run/<label>/NAME` in the container and
  pulled back into the mini lane dir (hashed into `pull.json`);
  `--load FILE` must exist on the mini and is `scp`'d to
  `HS1/load-staging/<label>.state` first (outside the run dir so the
  remote no-reuse guard keeps working); `--strict` passes through.
- `local/tooling/boot/bradflix_det_boot.py`: `--save-at/--save-path/
  --exit-after-save/--load/--strict` set the same `PS2X_SAVESTATE_*` env
  as the mini path (paths validated: no `/` or `..`); a clean exit after
  a save counts as `target`, mirroring the mini driver.

## Exact commands

- Setup: `git -C ~/dev/PS2Recomp worktree add ~/dev/ssx3-work/SS2/PS2Recomp
  -b ss2 5474956`
- STL probe: `scp /tmp/ss2-probe.cpp bradflix:dev/ssx3-work/HS1/` +
  `docker run --rm --user 1000:1000 -v ~/dev/ssx3-work/HS1:/work ssx3-hs1
  bash -c "clang++ -O1 -o /work/ss2-probe /work/ss2-probe.cpp && /work/ss2-probe"`
- Builds: `local/tooling/build/mac_build.sh
  ~/dev/ssx3-work/SS2/PS2Recomp ~/dev/ssx3-work/SS2/build-det --det` (×2);
  `local/tooling/build/bradflix_build.sh {5474956,5cce392,55f0c8d}
  {ss2base-det,ss2fix-det,ss2fix2-det} --det`
- Fix transfer (VR2's recipe): `git bundle create … 5474956..ss2`,
  `scp` to `HS1/`, `git -C …/HS1/PS2Recomp fetch <bundle> +ss2:refs/ss2/fix`
- Suites: `cd <worktree> && <build>/ps2xTest/ps2x_tests` (Mac);
  `ssh bradflix 'docker run --rm --user 1000:1000 -w /work/PS2Recomp -v
  ~/dev/ssx3-work/HS1:/work ssx3-hs1 /work/<build>/ps2xTest/ps2x_tests'`
- Boots: `ssx3_boot.py --host bradflix --mode det --backend parallel
  --runner dev/ssx3-work/HS1/<build>/ps2xRuntime/ps2EntryRunner --label
  <ss2-b*> [--save-at 2000 --save-path ss2-t2000.state] [--load <state>]
  --stop-tick 2600 --dump-ticks 2100,2300,2600`; Mac boots the same
  without `--host` (absolute scratch `--save-path`, `--out` under
  `~/dev/ssx3-work/SS2/`).
- Compares: `local/research/SS1/ss1_hashdiff.py --base <straight> --cand
  <load> --from 2001 --to 2600`.
- Seeded state: `baseline.py get-state
  a3efbfe-fr1r1-t2000-parallel-1x-433cb405` (two SHA reads inside).

## Budget

Builds 5/6 (2 Mac + 3 bradflix). Boots 8/8: B1 repro-refusal, B2 save,
B3 load-refusal (caught the verify bug), B3b load-IDENTICAL, B2b straight
jitter control, B4/B5 Mac round trip, B6 Mac→Linux verdict. Scratch:
`~/dev/ssx3-work/SS2` 1.9 GB (build dir; states+runs ~250 MB),
bradflix `HS1/run/ss2-*` ~8 MB logs only (states, bundles, probe and
staging removed after the gate). States never entered git.

## Gaps

- The bradflix t2600 frame diff is attributed to present jitter (two
  straights disagree at t2300; SS1's precedent; load matches a straight
  at both other ticks), but a third straight run would have nailed it —
  no boot margin remained. If a lane re-runs, one more straight with the
  same dump ticks settles it.
- bradflix builds still pin PGS `19d93b2` (no `ss1-clut` accessor), so
  bradflix states carry no CLUT tail and bradflix loads warn on Mac
  states that do. Same-build round trips are exact regardless; the pin
  update belongs to HS1 (`bradflix_build.sh`), untouched here.
- Cross-STL (Mac→Linux) loads refuse by design at the first
  hash-algorithm-dependent map; option B (order-free runtime + canonical
  save order) is the route if lanes ever need them.
- The refusal names the section but not the map; naming the map would
  have made B3/B6 attribution one step shorter (kept out to hold the
  one-mechanism scope).
- `ss2-b1-repro`/`ss2-b3-load` runs show `runner_rc=0` on refusal (the
  runner exits 0 after a clean load refusal); the drivers report
  `bound=exit`, rc=1 — unchanged SS1 behaviour, noted only.
