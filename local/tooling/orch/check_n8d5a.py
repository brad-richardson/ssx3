#!/usr/bin/env python3
"""Format gate for the N8D5A read-only decision table; semantics need review."""
import re
from pathlib import Path

p = Path('local/research/N8D5A/REPORT.md')
s = p.read_text()
assert len(s.encode()) < 1_000_000, 'report cap'
for marker in ('## Candidate probes', '## Format compatibility',
               '## Recommendation', 'PS2XGSC1', 'A/B/C'):
    assert marker in s, f'missing {marker}'
assert len(re.findall(r'[A-Za-z0-9_./+-]+:\d+', s)) >= 8, 'need eight source-line citations'
print('N8D5A format gate: sections, parser fact, A/B/C and citations present')
