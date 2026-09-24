#!/usr/bin/env python3
"""Bounded input and row gate for the X11 dense local-model trial."""

from pathlib import Path

excerpt = Path("local/research/X11/source-excerpts.txt").read_text()
report = Path("local/research/X11/REPORT.md").read_text()
for anchor in (
    "item.deadlineCycle <= m_eeCycle",
    "item.hostDeadline <= pacedNow",
    "std::sort(due.begin(), due.end()",
    "timerHostDeadline < hostDeadline",
    "m_events.push_back(event)",
):
    assert anchor in excerpt, f"missing pinned anchor: {anchor}"
assert "FILL" not in report, "unfilled report"
rows = {
    line.split(" |", 1)[0][2:]: line
    for line in report.splitlines()
    if line.startswith("| ") and not line.startswith("| ---")
}
expected = {
    "Due membership": ("deadlineCycle", "hostDeadline", "2553", "2594"),
    "Within-batch order": ("cycle", "type", "id", "sequence", "2602"),
    "Idle timer versus event": ("timerHostDeadline", "deadlineCycle", "2882", "2893"),
    "Posted event cycle": ("m_events", "cycle", "838", "848"),
}
assert len(rows) == 5, f"expected header plus four rows, got {len(rows)}"
for name, terms in expected.items():
    row = rows.get(name)
    assert row is not None, f"missing {name}"
    assert row.count("|") == 4, f"bad columns in {name}"
    for term in terms:
        assert term.lower() in row.lower(), f"{name}: missing {term}"
assert "LSP findReferences probe:" in report
print("X11 input/row gate: PASS; orchestrator still checks semantics")
