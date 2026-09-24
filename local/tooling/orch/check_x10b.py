#!/usr/bin/env python3
"""Pinned-input and semantic table gate for the X10B local-model trial."""

from pathlib import Path


excerpt = Path("local/research/X10B/source-excerpts.txt").read_text()
report = Path("local/research/X10B/REPORT.md").read_text()
anchors = (
    "dispatchIrq(false, 9u + timer)",
    "case EeEventType::VBlankStart:",
    "dispatchIrq(false, 2u)",
    "case EeEventType::VBlankEnd:",
    "dispatchIrq(false, 3u)",
    "queueCompletedDmacCause(1u)",
    "dispatchIrq(true, cause)",
    "stoppedByD ? 0x0200u",
    "stoppedByT ? 0x0400u",
)
for anchor in anchors:
    assert anchor in excerpt, f"pinned input lacks {anchor}"
assert "FILL" not in report, "report has unfilled cells"
rows = {
    line.split(" |", 1)[0][2:]: line
    for line in report.splitlines()
    if line.startswith("| ") and not line.startswith("| ---")
}
expected = {
    "EE timer pending": ("9u + timer", "9, 10, 11, 12", "INTC", "EeScheduler.cpp:2507"),
    "VBlankStart tail": ("dispatchIrq(false, 2u)", "INTC", "EeScheduler.cpp:2696"),
    "VBlankEnd": ("dispatchIrq(false, 3u)", "INTC", "EeScheduler.cpp:2702"),
    "VIF1 completion": ("queueCompletedDmacCause(1u)", "DMAC", "ps2_memory.cpp:2286"),
    "DMAC handler helper": ("dispatchIrq(true, cause)", "DMAC", "Interrupt.cpp:70"),
    "VU1 callback status": ("0x0200u", "0x0400u", "VU state", "ps2_runtime.cpp:1046"),
}
assert len(rows) == len(expected) + 1, f"expected six data rows; got {len(rows) - 1}"
for name, terms in expected.items():
    row = rows.get(name)
    assert row is not None, f"missing row: {name}"
    assert row.count("|") == 5, f"bad columns: {name}"
    for term in terms:
        assert term in row, f"{name}: missing {term}"
assert "2, 3, 9, 10, 11, 12" in report, "direct INTC cause list incomplete"
assert "not shown" in report.lower(), "5/7 gap not stated"
print("X10B pinned-input/semantic table: PASS; orchestrator still reviews source")
