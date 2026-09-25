#!/usr/bin/env python3
"""Mac mini boot lease: four slots for diagnostic boots, all four for speed runs.

Slot 1 is the legacy path /tmp/ssx3-p-lane-lease (older boot scripts claim
it directly); slot n > 1 is /tmp/ssx3-p-lane-lease-<n>.

  from p_lane_lease import claim, release
  slot = claim("g46a")                   # first free slot, or None
  slot = claim("n5speed", exclusive=True)  # all slots (speed numbers)
  ...
  release(slot)

Rules (AGENTS.md "Leases"):
- Diagnostic boots take one slot. Speed-number boots take all of them.
- Kill and check your own runner by PID, never `pkill`/`pgrep -x
  ps2EntryRunner`: another slot may be running one.
- Run each boot from its own cwd (the runtime writes ps2_log.txt there).

CLI: p_lane_lease.py status | claim <label> [--exclusive] | release <slot>
"""
import os, sys, time

SLOTS = {1: "/tmp/ssx3-p-lane-lease",
         **{n: f"/tmp/ssx3-p-lane-lease-{n}" for n in (2, 3, 4)}}


def _try(path, text):
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError:
        return False
    with os.fdopen(fd, "w") as f:
        f.write(text)
    return True


def claim(label, exclusive=False):
    """Return the claimed slot (1-4, or "both" meaning all), or None if busy."""
    text = f"{label} pid={os.getpid()} utc={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n"
    if exclusive:
        got = []
        for path in SLOTS.values():
            if not _try(path, text):
                for q in got:
                    os.remove(q)
                return None
            got.append(path)
        return "both"
    for n, path in SLOTS.items():
        if _try(path, text):
            return n
    return None


def release(slot):
    for n in (tuple(SLOTS) if slot == "both" else (slot,)):
        try:
            os.remove(SLOTS[n])
        except FileNotFoundError:
            pass


def status():
    return {n: (open(p).read().strip() if os.path.exists(p) else None)
            for n, p in SLOTS.items()}


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "status":
        for n, s in status().items():
            print(f"slot {n}: {s or 'free'}")
    elif a[0] == "claim":
        s = claim(a[1], exclusive="--exclusive" in a)
        print(s if s is not None else "busy")
        sys.exit(0 if s is not None else 1)
    elif a[0] == "release":
        release("both" if a[1] == "both" else int(a[1]))
    else:
        sys.exit(__doc__)
