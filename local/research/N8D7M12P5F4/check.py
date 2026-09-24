#!/usr/bin/env python3
"""N8D7M12 Part 5F4 receipt checker (read-only; BLOCKED-permission part).

Verifies: fork worktree branch/rev/clean (no bytes changed), REPORT carries
the denial receipt + source-grounded design table + no-run declaration, and
no build/suite/replay artifacts exist. Verdict is PASS only for the BLOCKED
receipt itself; any implementation claim fails.
"""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
RESEARCH = REPO / "local" / "research" / "N8D7M12P5F4"
FORK = Path.home() / "dev/ssx3-work" / "N8D7M12P5F4" / "PS2Recomp"
BASE = "a608ed1e161f60334a0cf3a80d1af3e54b692bd2"
BRANCH = "n8d7m12-p5f4"

results = []


def check(name, ok, detail=""):
    results.append({"name": name, "ok": bool(ok), "detail": detail})


def git(*args):
    out = subprocess.run(["git", "-C", str(FORK), *args],
                         capture_output=True, text=True, timeout=30)
    return out


report = (RESEARCH / "REPORT.md").read_text()
flat = " ".join(report.split())
check("report_denial_receipt",
      "prevents you from using this specific" in flat
      and "N8D7M12P5F4/**" in report,
      "verbatim denial + shadowing allow rule recorded")
check("report_design_table",
      all(k in report for k in
          ("D1", "D4", "D5", "Fence", "PrivWrite", "GB4_PKTSEQ",
           "14695981039346656037")),
      "D1-D9 table, Fence exclusion, PrivWrite gap, emission format")
check("report_no_run_claim",
      "NOT RUN" in report and "no Android claim" in report
      and "BLOCKED" in report,
      "no validation numbers invented")
check("report_no_gpu_verdict",
      "No GPU verdict" in report,
      "no mechanism verdict claimed")

head = git("rev-parse", "HEAD")
check("fork_head_pinned", head.stdout.strip() == BASE,
      head.stdout.strip())
branch = git("branch", "--show-current")
check("fork_branch", branch.stdout.strip() == BRANCH,
      branch.stdout.strip())
status = git("status", "--short")
check("fork_clean", status.stdout.strip() == "",
      repr(status.stdout.strip()))
diff = git("diff", "--stat")
check("fork_no_diff", diff.stdout.strip() == "",
      repr(diff.stdout.strip()[:200]))
sentinel = FORK / ".sentinel-p5f4"
check("sentinel_removed", not sentinel.exists(), str(sentinel))

scratch = Path.home() / "dev/ssx3-work" / "N8D7M12P5F4"
build_dir = scratch / "build"
check("no_build_dir", not build_dir.exists(), str(build_dir))
check("no_replay_outputs",
      not list(scratch.glob("mac-*")) and not list(scratch.glob("*.log")),
      "no mac-*/logs under private scratch")

verdict = "BLOCKED" if all(r["ok"] for r in results) else "FAIL"
payload = {"brief": "N8D7M12P5F4", "verdict": verdict,
           "checks": results,
           "passed": sum(1 for r in results if r["ok"]),
           "total": len(results)}
(RESEARCH / "check-result.json").write_text(json.dumps(payload, indent=2) + "\n")
print(json.dumps(payload, indent=2))
sys.exit(0 if verdict == "BLOCKED" else 1)
