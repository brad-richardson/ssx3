#!/usr/bin/env python3
"""Check a bounded source-order table for the X13 local-model trial."""
import csv
import subprocess
import sys
from pathlib import Path

root = Path('/Users/brad/dev/ssx3-work/N8B1/PS2Recomp')
source = root / 'ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp'
expected = [
    ('scanout', 253),
    ('barrier', 275),
    ('copy', 284),
    ('submit', 288),
    ('wait', 289),
    ('map', 291),
    ('pack', 303),
]
pin = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
assert pin == '17e90ded3689685ad359b76a9168c80a1f752e2d', pin
lines = source.read_text().splitlines()
with Path(sys.argv[1]).open(newline='') as f:
    rows = list(csv.DictReader(f, delimiter='\t'))
assert len(rows) == len(expected), f'{len(rows)} rows, expected {len(expected)}'
assert list(rows[0]) == ['stage', 'line', 'source'], list(rows[0])
for row, (stage, line) in zip(rows, expected):
    assert row == {'stage': stage, 'line': str(line), 'source': lines[line - 1].strip()}, (stage, row)
print('X13 source-order gate: 7/7 exact rows, pinned N8B1 source')
