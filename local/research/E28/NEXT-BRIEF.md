# E28 → E29 handoff

**This is a handoff, not a designed brief.** E27 named the host-side observable
in one paragraph and designed E29's lane nowhere; E28 keeps that discipline and
adds only what e28a measured. The orchestrator writes E29.

## The one host-side observable

E27 asked for a boot that would settle the guest half and log the host half.
E28 was given only the guest half, and the guest half is now **closed**. The
guest is not waiting for anything it cannot do: its kind-1 queue holds
**431,840 bytes** with the head parked on **`0xd49b14`**, the chunk whose
payload at `0xd49b1c` is the start code the parser needs; `0xd49b18` still
carries the tag `0x0100381c` and no guest store touches either address again;
and the re-ask branch at `0x3b10ac` needs nothing but the `jal func_402A10` at
`0x3b1020` to return. So **every remaining question is host-side, and exactly
one observable decides it**: instrument `MPEG.cpp` to log each entry to
`getMpegPicture` with its `requestInput` flag **and the result of
`pending.lock()`**, plus every `completeExternalWait(kMpegPictureWaitType, …)`
with its caller. E27's prediction stands unrevised — `getMpegPicture` entered
exactly **twice** (`requestInput=true`, then `false` from the `onComplete` at
`MPEG.cpp:1760`), `pending.lock()` **non-null on the second**, and
`completeExternalWait` for the picture wait called **zero** times after the
feed — and e28a changes only what it would *mean*: with the guest proved
healthy, a non-null `pending.lock()` at the second entry is no longer one half
of a mutual wait but the **whole** of the stall, and the `shared_ptr` moved into
the parked thread's own `EeWaitState` at `EeScheduler.cpp:2120` is the only
thing left holding it. That is one log line and one boot.

## Facts E29 inherits, with their receipts

| Fact | Receipt |
|---|---|
| kind-1 queue slot | **`0xd486ec`** — `+0` owner, `+4` kind, `+8` bytes (`0xd486f4`), `+0xC` head (`0xd486f8`). `mission-1-slot.json` |
| the STRM context | **`ctx0 = 0xd48300`**, written into `slot+0` by the guest at `pc=0x3e0914`, boot-log line 22329 |
| kind-2 queue slot | `0xd486fc`, same four fields, head on the `SCHl` chunk at `0xd49aec` |
| queue depth at the park | **431,840 B** (`0x696e0`), after 28 walker publishes reached 436,876 and one dequeue took 5,036 back |
| head at the park | **`0xd49b14`**, set at `pc=0x3e13c8`, boot-log line 22820, and never touched again |
| post-park movement | **0** emissions across **243** armed entries, with 24,031 log lines still to run |
| the feed vector | `cde8a830…2a1c875a`, 5,040 B — byte-identical for the **fourth** time |
| e28a captures | `boot-e28a-1.log` `21d702c5…`, `ps2_log-e28a-1.txt` `bb987c8f…`, `syscalls-e28a-on.txt` `a3f4b88b…`. `capture-pins.json` |

## Two operational facts this lane paid for

1. **The capture driver needs no edit to change what is watched.**
   `watch-set.json` is data the driver loads; `e28_capture.py` stayed
   byte-identical to E24's under the mechanical rename while the watch set grew
   from 230 to 243 entries. The 13 extra entries cost about **0.10 s** of
   span-complete against a 75 s bound — and e28a at 243 entries actually ran
   **0.69 s faster** than e26a at 230, so run-to-run variation dominates the
   watch-count term outright. Build the new tier in `watch-set.json` and prove
   the carried vector is an exact prefix (`e28_watchset.py`).

2. **Errata E28-E1 — the lane rename will rewrite a real path.** Any path whose
   spelling contains the previous lane's token gets rewritten, and
   `rename-proof-hexsafe.json` is structurally blind to it. E25 named its
   readiness receipt `e26-readiness.json`, so the `e26→e28` carry pointed
   `e28_restore_gate.py` at a file that does not exist and the Mission 0 gate
   would have died on `FileNotFoundError`. **Run `e28_carry_audit.py` (or its
   successor) before the first gate**; it resolves every cross-lane path
   literal in every carried tool. Add the token to `PROTECTED` when it fires.

## What E28 did NOT do, so E29 does not have to re-check

Zero fork source edits, commits or pushes. Zero builds, relinks, regenerations
or observer rebuilds. Zero deletions. **One** title boot, **one** lease claim,
**one** release. Fix gate **STOP**. The binary booted is byte-for-byte the one
every E15–E27 receipt was taken on, so everything those lanes measured
transfers by identity.

# E28 NEXT-BRIEF TAIL COMPLETE
