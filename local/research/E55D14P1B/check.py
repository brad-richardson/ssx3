#!/usr/bin/env python3
"""E55D14 Part 1B checker: re-verifies source/test/build/runner pins from receipts.

Run from the fork root: python3 .work/receipts/check.py
"""
import hashlib
import re
import subprocess
import sys
from pathlib import Path

# Receipts were authored inside the private fork worktree. The orchestrator
# imported this checker into ssx3 without moving the build or generated code.
ROOT = Path("/Users/brad/dev/ssx3-work/E55D14P1/PS2Recomp")
BASE = "bab6eb382673155ffd756fe8db265964eeff9703"
NAMED = [
    "ps2xRuntime/include/ps2_e55d3_pad_card_probe.h",
    "ps2xRuntime/src/lib/Kernel/Stubs/MemoryCard.cpp",
    "ps2xTest/src/ps2_e55d3_probe_tests.cpp",
]
fails = []


def sh(*args):
    r = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
    return r


def check(name, cond, detail=""):
    print(("PASS" if cond else "FAIL") + f" {name}" + (f" -- {detail}" if detail else ""))
    if not cond:
        fails.append(name)


branch = sh("git", "branch", "--show-current").stdout.strip()
check("branch is e55d14p1-getdir-path", branch == "e55d14p1-getdir-path", branch)

base_ok = sh("git", "rev-parse", BASE).stdout.strip() == BASE
check("base pin resolves", base_ok, BASE)

diff = sh("git", "diff", "--name-only", BASE, "HEAD", "--").stdout.split()
check("changed files vs base are exactly the three named",
      sorted(diff) == sorted(NAMED), str(diff))

status = sh("git", "status", "--short").stdout
work_untracked = "?? .work/" in status
staged_ok = all(
    line.startswith(("M ", "A ")) and line[3:] in NAMED
    for line in status.splitlines() if line and not line.startswith("??")
) if [l for l in status.splitlines() if l and not l.startswith("??")] else True
check(".work/ remains untracked", work_untracked, status.replace("\n", "|")[:200])
check("no other tracked modifications staged/unstaged",
      all(l[3:] in NAMED for l in status.splitlines() if l and not l.startswith("??")),
      status.replace("\n", "|")[:200])

runner_guard = sh("git", "diff", "--stat", "14b1e5cb", "HEAD", "--",
                  "ps2xRuntime/src/runner")
check("runner dir guard vs 14b1e5cb empty",
      runner_guard.stdout.strip() == "" and runner_guard.returncode == 0,
      runner_guard.stdout.strip()[:120] or "empty")

runner = ROOT / ".work/build/ps2xRuntime/ps2EntryRunner"
if runner.exists():
    h1 = hashlib.sha256(runner.read_bytes()).hexdigest()
    h2 = hashlib.sha256(runner.read_bytes()).hexdigest()
    check("runner double SHA match", h1 == h2, h1[:16])
else:
    check("runner exists", False, str(runner))

suite = ROOT / ".work/receipts/suite.log"
if suite.exists():
    text = suite.read_text(errors="replace")
    m = re.search(r"Total Tests:\s*(\d+)\s*Passed:\s*(\d+)\s*Failed:\s*(\d+)",
                  text)
    if m:
        total, passed, failed = map(int, m.groups())
        check("suite 693/693/0", (total, passed, failed) == (693, 693, 0),
              f"{total}/{passed}/{failed}")
    else:
        check("suite totals parse", False, "no totals line")
    probe = re.findall(r"\[Run\]: .*?(getdirpath|Ps2|pad, getdir|disabled|tiny cap)",
                       text)
    # Count probe-suite passed lines in the Ps2E55D3Probe block
    block = text.split("[Suite]: Ps2E55D3Probe", 1)
    if len(block) == 2:
        seg = block[1].split("[Suite]:", 1)[0]
        passed_n = seg.count("[Passed]")
        failed_n = seg.count("[Failed]")
        check("probe suite 9 passed 0 failed",
              passed_n == 9 and failed_n == 0, f"{passed_n}/{failed_n}")
    else:
        check("probe block present", False, "missing")
else:
    check("suite.log exists", False, "missing")

for name in NAMED:
    p = ROOT / name
    check(f"named file present: {name}", p.exists())

print("RESULT: " + ("ALL PASS" if not fails else f"{len(fails)} FAILURES"))
sys.exit(1 if fails else 0)
