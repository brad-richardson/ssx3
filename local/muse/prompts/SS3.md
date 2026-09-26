# SS3 — close RV5's save-state holes (muse, 3 h)

## Goal
Save states (SS1/SS2, fork `ssx3`, knobs default off) are used by lanes to start at the race. RV5 (`docs/research/review-2026-09-26-astra-f6.md` §S2–S5, read them fully) found four holes that could make a load silently diverge or mis-identify its runner. Fix them so states are safe for lanes now and for device play later.

## The four findings (fix each; one commit each; a test that fails before the fix)
- **S2 paraLLEl palette indices:** `write_clut_state()` restores the CLUT ring and renderer cursors but not `GSInterface`'s `render_pass.clut_instance` / `latest_clut_instance`. Save/restore them (paraLLEl fork change on top of fork `ssx3` `1b3a294`, plus the section version bump in PS2Recomp), or reconstruct from a documented invariant. Test: a load followed by a CLD=0 paletted draw and a partial palette update.
- **S3 partial GS input at the save point:** `SavestateIdle()` checks readbacks and palette uploads only; an in-progress host→local transfer (`host_to_local_active`, payload/cursor) or a strip/fan's retained vertices are lost. Either serialize them or **defer the save** while any is live (`[savestate] deferred … reason=gs-transfer|gs-vertex`); deferring is acceptable. Test: continuations that split an IMAGE upload and a strip/fan across the save point.
- **S4 memory-card directories and timestamps:** save directories (incl. empty ones) and the timestamps `sceMcGetDir` returns; validate the whole destination tree; don't rewrite identical files; propagate traversal errors. Bump the `stub:mcdir` section version. Test: mkdir then save then load then create a file in it; `GetDir` timestamps equal after load.
- **S5 Android runner identity:** hash the loaded runtime library (`dladdr` on a function in it) instead of `/proc/self/exe`; strict mode fails if identity can't be obtained. Test on the Mac that the path chosen is the module containing the runtime (unit-test the helper); Android compile only (no device).

## Facts
- Fork `ssx3` tip `5d5c382` (MTVU, VU0 recompile etc. landed; save/load already syncs MTVU). paraLLEl fork `ssx3` `1b3a294` (`~/dev/ssx3-work/parallel-gs-ssx3` is the canonical checkout; branch your own paraLLEl worktree, never modify the canonical one).
- Tools: `local/tooling/build/mac_build.sh` (`--pgs` for your paraLLEl worktree), `local/tooling/boot/ssx3_boot.py` (`--save-at/--load`), `baseline.py` state store (`get-state`), bradflix via `--host bradflix` (states are per host).
- Existing states in the store will refuse after a section version bump — that's intended; re-seed `a3efbfe`-equivalent t1720/t2000 states for the new tip at the end (`put-state`), on the Mac and on bradflix.

## Gates
Suite green (Mac + bradflix); det IDENTICAL with knobs unset vs `a3efbfe-det-fr1r1-t2400-snd1-1x-a5f2f32d`; save/load round trip t2000 → t2600 IDENTICAL on the Mac and on bradflix; 4×+hi-res round trip IDENTICAL; one Android compile (bytesize, one heavy job at a time, hold the ssh). Never push; runner-dir check empty. ≤ 8 builds. Text only in git; states stay in scratch. Workers don't edit `docs/`. First failure: stop, save the error, hand back.

## Deliverable
`local/research/SS3/REPORT.md` (finding → fix → test table, gates, new state keys, fork + paraLLEl commits, gaps) + `[SS3]` commit (explicit paths, `git add -f`, trailer `Orchestrated-By: Muse Code`), no push.
