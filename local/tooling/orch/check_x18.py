#!/usr/bin/env python3
"""Gate the X18 logcat vector parser against the saved N8D6C failure."""

import gzip
import hashlib
import importlib.util
from pathlib import Path
import re
import struct

ROOT = Path(__file__).resolve().parents[3]
MODULE = ROOT / 'local/tooling/orch/tile_vector_v2.py'
LOG = Path('/Users/brad/dev/ssx3-work/N8D6C/logcat-all.txt.gz')
EXPECTED_SHA = '3f06a58ad6805c695a01c305fe06b52cc0d92198a6fb699aeee0c4ea09681ba5'

spec = importlib.util.spec_from_file_location('tile_vector_v2', MODULE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
parse = module.tile_vector

lines = gzip.open(LOG, 'rt', errors='replace').read().splitlines()
same_pid = [line for line in lines if re.search(r'^\s*\d+\.\d+\s+17446\s+', line)]
for kind in ('sampled', 'raw'):
    result = parse(same_pid, kind)
    assert result is not None, f'{kind}: saved continuation rejected'
    assert result['words'] == 896 and len(result['values']) == 896
    assert result['occupied'] == 5894 and result['active'] == 39
    assert result['sha256'] == EXPECTED_SHA
    assert hashlib.sha256(struct.pack('<896I', *result['values'])).hexdigest() == EXPECTED_SHA

prefix = '  1790255526.027 17446 17467 I ps2x    : '
numbers = list(range(896))
first = prefix + '[n8d5b] sampled_tile_counts=' + ','.join(map(str, numbers[:500]))
tail = prefix + ',' + ','.join(map(str, numbers[500:]))
expected = hashlib.sha256(struct.pack('<896I', *numbers)).hexdigest()
synthetic = parse([first, tail], 'sampled')
assert synthetic is not None and synthetic['sha256'] == expected
assert synthetic['occupied'] == sum(numbers)
assert synthetic['active'] == sum(n >= 32 for n in numbers)
assert parse([first, tail.replace(': ,', ': ,,', 1)], 'sampled') is None
assert parse([first + ',', tail], 'sampled') is None  # doubled separator across the segment boundary
assert parse([first, tail.replace(': ,', ': ,x,', 1)], 'sampled') is None
assert parse([first], 'sampled') is None
assert parse([first, prefix + '[n8d5b] raw_summary tiles=896'], 'sampled') is None
assert parse([first, tail, prefix + ',999'], 'sampled')['words'] == 896

print('PASS saved sampled/raw 896-word vectors and synthetic continuation/negative cases')
