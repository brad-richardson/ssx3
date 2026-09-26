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

CLI: p_lane_lease.py [--host mini|bradflix] status | claim <label> [--exclusive] | release <slot>
Host split (HS1): mini keeps 4 local slots (legacy paths, default host);
bradflix has 4 remote slots (dirs ~/.ssx3-lease/1..4 on bradflix, mkdir is
the atomic claim). Speed-number boots take all four slots of their host.

  from p_lane_lease import claim, release
  slot = claim("hs1a1", host="bradflix")
"""
import os, subprocess, sys, time

SLOTS = {1: "/tmp/ssx3-p-lane-lease",
         **{n: f"/tmp/ssx3-p-lane-lease-{n}" for n in (2, 3, 4)}}

BRADFLIX_HOST = "bradflix"
BRADFLIX_LEASE_ROOT = "~/.ssx3-lease"
BRADFLIX_SLOTS = (1, 2, 3, 4)


def _try(path, text):
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError:
        return False
    with os.fdopen(fd, "w") as f:
        f.write(text)
    return True


def _bssh(cmd):
    """Run cmd on bradflix; return CompletedProcess, or None on ssh failure."""
    try:
        return subprocess.run(["ssh", "-o", "ConnectTimeout=10", BRADFLIX_HOST, cmd],
                              capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError) as e:
        print(f"bradflix ssh failed: {e}", file=sys.stderr)
        return None


def _bclaim_one(n, text):
    safe = text.strip().replace("'", "_")
    r = _bssh(f"mkdir -p {BRADFLIX_LEASE_ROOT} && mkdir {BRADFLIX_LEASE_ROOT}/{n} 2>/dev/null"
              f" && printf '%s\\n' '{safe}' > {BRADFLIX_LEASE_ROOT}/{n}/HOLDER"
              f" && cat {BRADFLIX_LEASE_ROOT}/{n}/HOLDER")
    return r is not None and r.returncode == 0


def _brelease_list(ns):
    for n in ns:
        _bssh(f"rm -rf {BRADFLIX_LEASE_ROOT}/{n}")


def claim(label, exclusive=False, host="mini"):
    """Return the claimed slot (1-4, or "both" meaning all), or None if busy."""
    text = f"{label} pid={os.getpid()} utc={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n"
    if host == "bradflix":
        if exclusive:
            got = []
            for n in BRADFLIX_SLOTS:
                if not _bclaim_one(n, text):
                    _brelease_list(got)
                    return None
                got.append(n)
            return "both"
        for n in BRADFLIX_SLOTS:
            if _bclaim_one(n, text):
                return n
        return None
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


def release(slot, host="mini"):
    if host == "bradflix":
        _brelease_list(BRADFLIX_SLOTS if slot == "both" else (slot,))
        return
    for n in (tuple(SLOTS) if slot == "both" else (slot,)):
        try:
            os.remove(SLOTS[n])
        except FileNotFoundError:
            pass


def status(host="mini"):
    if host == "bradflix":
        r = _bssh(f"for n in 1 2 3 4; do f={BRADFLIX_LEASE_ROOT}/$n/HOLDER; "
                  f"if [ -f $f ]; then echo \"slot $n: $(cat $f)\"; else echo \"slot $n: free\"; fi; done")
        if r is None or r.returncode != 0:
            return {n: "(unreachable)" for n in BRADFLIX_SLOTS}
        out = {}
        for line in r.stdout.splitlines():
            n = int(line.split()[1].rstrip(":"))
            out[n] = None if line.endswith("free") else line.split(": ", 1)[1]
        return out
    return {n: (open(p).read().strip() if os.path.exists(p) else None)
            for n, p in SLOTS.items()}


if __name__ == "__main__":
    a = sys.argv[1:]
    host = "mini"
    if "--host" in a:
        i = a.index("--host")
        host = a[i + 1]
        del a[i:i + 2]
    if host not in ("mini", "bradflix"):
        sys.exit("host must be mini|bradflix")
    if not a or a[0] == "status":
        for n, s in status(host).items():
            print(f"slot {n}: {s or 'free'}")
    elif a[0] == "claim":
        s = claim(a[1], exclusive="--exclusive" in a, host=host)
        print(s if s is not None else "busy")
        sys.exit(0 if s is not None else 1)
    elif a[0] == "release":
        release("both" if a[1] == "both" else int(a[1]), host=host)
    else:
        sys.exit(__doc__)
