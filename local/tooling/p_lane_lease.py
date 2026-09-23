#!/usr/bin/env python3
"""Mac mini boot lease: two slots for diagnostic boots, both for speed runs.

Slot 1 is the legacy path /tmp/ssx3-p-lane-lease (older boot scripts claim
it directly); slot 2 is /tmp/ssx3-p-lane-lease-2.

  from p_lane_lease import claim, release
  slot = claim("g46a")                   # first free slot, or None
  slot = claim("n5speed", exclusive=True)  # both slots (speed numbers)
  ...
  release(slot)

Rules (AGENTS.md "Leases"):
- Diagnostic boots take one slot. Speed-number boots take both.
- Kill and check your own runner by PID, never `pkill`/`pgrep -x
  ps2EntryRunner`: the other slot may be running one.
- Run each boot from its own cwd (the runtime writes ps2_log.txt there).

CLI: p_lane_lease.py status | claim <label> [--exclusive] | release <slot>
"""
import os, sys, time

SLOTS = {1: "/tmp/ssx3-p-lane-lease", 2: "/tmp/ssx3-p-lane-lease-2"}


def _try(path, text):
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError:
        return False
    with os.fdopen(fd, "w") as f:
        f.write(text)
    return True


def claim(label, exclusive=False):
    """Return the claimed slot (1, 2, or "both"), or None if busy."""
    text = f"{label} pid={os.getpid()} utc={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n"
    if exclusive:
        if not _try(SLOTS[1], text):
            return None
        if not _try(SLOTS[2], text):
            os.remove(SLOTS[1])
            return None
        return "both"
    for n, path in SLOTS.items():
        if _try(path, text):
            return n
    return None


def release(slot):
    for n in ((1, 2) if slot == "both" else (slot,)):
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
