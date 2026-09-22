"""Compute REPORT.md's tail receipt and write it into the report.

Errata E24-E2: a stale tail receipt fails the gate. E24's own receipt does not
re-verify against any prefix of its committed file, which is exactly the failure
mode the errata names. E28 removes the possibility by construction:

  the hashed prefix is every line ABOVE the `| Tail receipt | Value |` header,

so the line this tool writes lives strictly AFTER the prefix boundary and
cannot invalidate the digest it carries. The convention is printed in the row
itself, and the tool re-reads the file after writing and re-verifies.
"""
import hashlib
from e28_common import *

REPORT = E / 'REPORT.md'
HEADER = '| Tail receipt | Value |'

def prefix_of(text):
    lines = text.splitlines(keepends=True)
    idx = next(i for i, l in enumerate(lines) if l.startswith(HEADER))
    return lines, idx, ''.join(lines[:idx])

text = REPORT.read_text()
lines, idx, prefix = prefix_of(text)
blob = prefix.encode()
digest = hashlib.sha256(blob).hexdigest()
row = (f'| Complete prefix | Lines 1–{idx}; {len(blob)} B; SHA256 `{digest}` '
       f'(the prefix is every line ABOVE the `| Tail receipt | Value |` header, '
       f'so this row lives after the boundary and cannot invalidate itself — '
       f'errata E24-E2) |\n')
out = []
for i, l in enumerate(lines):
    out.append(row if (i > idx and l.startswith('| Complete prefix |')) else l)
REPORT.write_text(''.join(out))

# Re-read and re-verify from disk.
lines2, idx2, prefix2 = prefix_of(REPORT.read_text())
digest2 = hashlib.sha256(prefix2.encode()).hexdigest()
ok = (digest2 == digest and idx2 == idx and len(prefix2.encode()) == len(blob))
save('tail-receipt.json', dict(utc=utc(), file=str(REPORT),
    convention='sha256 of every line ABOVE the "| Tail receipt | Value |" header',
    prefix_lines=idx, prefix_bytes=len(blob), sha256=digest,
    total_lines=len(lines2), reverified_after_write=ok, reverified_sha256=digest2,
    errata='E24-E2 -- the receipt is recomputed AFTER the last edit, and the row it '
           'writes is outside the hashed range so writing it cannot stale it',
    verify_command=('python3 -c "import hashlib;L=open(\'local/research/E28/REPORT.md\')'
                    '.read().splitlines(keepends=True);'
                    'i=next(n for n,l in enumerate(L) if l.startswith(\'| Tail receipt | Value |\'));'
                    'print(hashlib.sha256(\'\'.join(L[:i]).encode()).hexdigest())"')))
print(f'prefix lines 1-{idx}, {len(blob)} B, sha256 {digest}')
print('re-verified after write:', ok)
print('# E28 TAIL TAIL COMPLETE')
