#!/usr/bin/env python3
"""Check the bounded X14 Granite resource-layout extraction."""
import csv
import hashlib
import sys
from pathlib import Path

root = Path('/Users/brad/dev/ssx3')
excerpt = (root / 'local/research/X14/excerpt.txt').read_bytes()
assert hashlib.sha256(excerpt).hexdigest() == 'c9050d87a3011718660e3595a8305cad5f035fbc1e4e02a7dd9826f3c8149efa'
source = excerpt.decode()
expected = [
    ('sampled_image_mask', '0x00000003', 'shader:5,shader:6,reflect:920'),
    ('fp_mask', '0x00000003', 'shader:5,shader:6,reflect:923'),
    ('storage_buffer_mask', '0x00000004', 'shader:7,reflect:1010'),
    ('push_constant_size', '8', 'shader:8,reflect:1046'),
    ('reflection_mode', 'explicit_layout_required', 'cmake:40,device:403,device:408,reflect:1095,reflect:1102'),
]
with Path(sys.argv[1]).open(newline='') as f:
    rows = list(csv.DictReader(f, delimiter='\t'))
assert len(rows) == len(expected), f'{len(rows)} rows, expected {len(expected)}'
assert list(rows[0]) == ['field', 'value', 'evidence'], list(rows[0])
for row, (field, value, evidence) in zip(rows, expected):
    assert row == {'field': field, 'value': value, 'evidence': evidence}, (field, row)
    for anchor in evidence.split(','):
        assert any(line.startswith(anchor + ':') for line in source.splitlines()), anchor
print('X14 layout gate: 5/5 exact fields and cited anchors')
