#!/usr/bin/env python3
"""E55D8 checker: every proposed route step needs an existing receipt + SHA +
tick/sequence citation; outcome B/C requires explicit unknown fields and no
runnable detour command. Exit 0 PASS, nonzero FAIL with reason."""

import hashlib
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
REPORT = Path(__file__).with_name("REPORT.md")


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def section_lines(text, heading_prefix):
    out, active = [], False
    for line in text.splitlines():
        if line.startswith("## "):
            active = line.startswith("## " + heading_prefix)
            continue
        if active:
            out.append(line)
    return out


def table_rows(lines):
    rows = []
    for line in lines:
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if cells and all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
            continue  # separator row (chain arrows like <---> are data)
        rows.append(cells)
    return [r for r in rows if r[0].lower() not in ("#",)]


def check_step(receipt, sha_cell, citation):
    """A supported step: receipt exists, SHA matches (unless explicitly
    marked cited-only), citation is concrete (not unknown/empty)."""
    p = REPO / receipt
    if not p.is_file():
        return False
    if "cited" in sha_cell.lower():
        pass
    else:
        m = re.search(r"[0-9a-f]{64}", sha_cell)
        if not m or sha256_of(p) != m.group(0):
            return False
    if not citation or re.fullmatch(r"(?i)[\W]*(unknown|n/a|none)[\W]*", citation):
        return False
    return True


def main():
    failures = []
    text = REPORT.read_text()

    m = re.search(r"^Outcome:\s*\*\*(\w+)\*\*", text, re.M)
    outcome = m.group(1) if m else None
    if outcome not in ("B", "C"):
        failures.append(f"outcome must be predeclared B or C, found: {outcome!r}")

    ev_rows = table_rows(section_lines(text, "1. Evidence"))
    if not ev_rows:
        failures.append("evidence index table has no data rows")
    for r in ev_rows:
        if len(r) < 5:
            failures.append(f"evidence row malformed: {r[0] if r else '?'}")
            continue
        paths = re.findall(r"`([^`]+)`", r[1])
        if not paths:
            failures.append(f"row {r[0]}: no backticked receipt path")
            continue
        for rp in paths:
            if not check_step(rp, r[2], r[3]):
                failures.append(f"row {r[0]}: unsupported step (receipt={rp})")

    # The checker must reject unsupported steps: prove it on fabrications.
    fabrications = [
        ("local/research/NOPE/missing.txt", "0" * 64, "tick 1"),
        (ev_rows[0] and re.findall(r"`([^`]+)`", ev_rows[0][1])[0] or "x", "f" * 64, "tick 1"),
        (ev_rows[0] and re.findall(r"`([^`]+)`", ev_rows[0][1])[0] or "x", ev_rows[0][2] if ev_rows else "", "unknown"),
    ]
    for rp, sh, ci in fabrications:
        if check_step(rp, sh, ci):
            failures.append(f"checker failed to reject fabricated step ({rp})")

    cand_rows = table_rows(section_lines(text, "3. Candidate"))
    if not cand_rows:
        failures.append("candidate table has no data rows")
    for r in cand_rows:
        if len(r) < 6:
            failures.append(f"candidate row malformed: {r[0] if r else '?'}")
            continue
        if "unknown" not in r[3].lower():
            failures.append(f"candidate {r[0]}: screen/input lacks explicit unknown")
        if "unknown" not in r[4].lower():
            failures.append(f"candidate {r[0]}: tick lacks explicit unknown")
        if not r[5].strip():
            failures.append(f"candidate {r[0]}: next observation empty")

    for pat in (r"e55d8_boot\.py", r"--label\s+[AB][12]\b", r"am start",
                r"PS2X_PAD_CARD_PROBE\s*=\s*\S+"):
        if re.search(pat, text):
            failures.append(f"runnable detour command pattern present: {pat}")
    if "No boot in this part" not in text:
        failures.append("missing explicit 'No boot in this part' statement")

    if failures:
        print("E55D8 check: FAIL")
        for f in failures:
            print(" -", f)
        return 1
    print(f"E55D8 check: PASS (outcome {outcome}; "
          f"{len(ev_rows)} evidence rows SHA+citation ok; "
          f"{len(cand_rows)} candidate rows explicit-unknown; "
          f"no runnable detour; fabrications rejected)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
