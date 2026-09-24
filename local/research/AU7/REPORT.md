# AU7 — E54C PINTEH fix vs menu side channel: STOPPED at step 1

Worker: Muse Code. Brief: `local/muse/prompts/AU7.md`. No push, no board/ledger edit.

## Result

**Step 1 failed: `5bb1fdd` (AU2 SND spike) conflicts in
`ps2xRuntime/src/lib/Kernel/EeScheduler.cpp`, which is not a test
registration file.** Per the brief ("stop and report the conflict") and the
stop rules ("stop on the first failed step"), no build, suite run, boot,
capture, or `midside.py` measurement was attempted. H1/H0 is undecided; no
AU7 audio exists.

## The conflict

Base `04f3ace` (= `fork/ssx3` tip) contains E54C (`89bec9b` is an ancestor).
AU2's `5bb1fdd` was cut from `b9647f5` (E58-era); between there and `04f3ace`,
`EeScheduler.cpp` gained E54B/E54F2/E55B2/E55C2 and GB2/GB3/GB4 changes. Both
sides add adjacent lines at the same two sites:

| Site | HEAD (`04f3ace`) side | `5bb1fdd` side |
| --- | --- | --- |
| Includes (~line 8) | `ps2_vq.h`, `gs_stream_capture.h`, xxhash block (E55C2) | `ps2_snd_spike.h` |
| Vsync-callback case | `#if PS2X_ENABLE_DET_HASH_TAP emitDetHashTap();` (E55C2) | `ps2_snd_spike::onVBlank(...)` AU2 tick |

The rest of `5bb1fdd` applied cleanly before the conflict stopped the sequence
(new `ps2xRuntime/include/ps2_snd_spike.h`, `SIF.cpp`, `RPC.cpp` hunks staged;
see `receipts/cherry-pick-status.txt`). The cherry-pick was aborted; the
worktree is clean at `04f3ace` on branch `au7-snd`. Later commits `83167d6`,
`3c895ca`, `ddf4f66` were not attempted.

## Pins and environment

| Item | Value |
| --- | --- |
| Worktree | `~/dev/ssx3-work/AU7/PS2Recomp`, branch `au7-snd` @ `04f3ace` (clean) |
| Fork `ssx3` tip (remote) | `fork/ssx3` = `04f3ace` (local `ssx3` is stale at `eac6cba`; untouched) |
| E54C in base | yes (`merge-base --is-ancestor 89bec9b 04f3ace`) |
| `5bb1fdd` parent / merge-base | `b9647f5` (both) |
| Codegen (unused) | `~/dev/ssx3-work/codegen-ssx3` present |
| Reference inputs (verified present, unused) | `~/dev/ssx3-work/AU4/pcsx2-tag1-36k.wav`, `~/dev/ssx3-work/AU6/run/tag1-36k.wav`, `~/dev/ssx3-work/AU6/boot.py` |
| Lease | never claimed; both mini slots were free; no boot |
| `midside.py` | untouched (read-only) |

## Exact commands

```sh
git -C ~/dev/PS2Recomp worktree add -b au7-snd ~/dev/ssx3-work/AU7/PS2Recomp 04f3ace
cd ~/dev/ssx3-work/AU7/PS2Recomp && git cherry-pick 5bb1fdd   # conflicts in EeScheduler.cpp
git diff -- ps2xRuntime/src/lib/Kernel/EeScheduler.cpp        # saved to receipts/cherry-pick-conflict.diff
git cherry-pick --abort                                       # tree clean at 04f3ace
```

Ancestry checks: `git log --oneline fork/ssx3` (= `04f3ace`),
`merge-base --is-ancestor 89bec9b 04f3ace` (true),
`merge-base 5bb1fdd 04f3ace` (= `b9647f5`).

## Budgets and gaps

0 builds, 0 boots, 0 suite runs; scratch `~/dev/ssx3-work/AU7/` holds only the
worktree (~minutes of work, far under 60 min / 8 GB). No `midside.py` output
exists for AU7 (no build) and the AU6 control re-run was not done (step 4 not
reached). Receipts: `receipts/cherry-pick-conflict.diff`,
`receipts/cherry-pick-status.txt`, `receipts/5bb1fdd-stat.txt`.

## Handoff state

`~/dev/ssx3-work/AU7/PS2Recomp` on `au7-snd` at clean `04f3ace`, ready for a
re-brief that either allows resolving the `EeScheduler.cpp` vsync-site
collision or rebases the sound HLE onto `fork/ssx3`.
