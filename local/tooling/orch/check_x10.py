#!/usr/bin/env python3
"""Mechanical completeness gate for the X10 model trial."""

from pathlib import Path


report = Path("local/research/X10/REPORT.md").read_text()
rows = [
    line for line in report.splitlines()
    if line.startswith("| ") and not line.startswith("| ---")
]
required = (
    "EE timer pending",
    "VBlankStart",
    "VBlankEnd",
    "VIF1 transfer completion",
    "`dispatchDmacHandlersForCause`",
    "VU1 `stoppedByD` / `stoppedByT` callbacks",
)
assert "FILL" not in report, "report has unfilled cells"
assert len(rows) == len(required) + 1, f"expected 6 data rows; got {len(rows)-1}"
for name in required:
    row = next((line for line in rows if line.startswith(f"| {name} |")), None)
    assert row is not None, f"missing row: {name}"
    assert row.count("|") == 5, f"bad table columns: {name}"
    assert ".cpp:" in row, f"missing file:line citation: {name}"
print("X10 format/completeness: PASS; source semantics require orchestrator review")
