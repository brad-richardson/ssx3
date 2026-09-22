"""E29 -- pin the bypass build outputs under the STANDING SSD RULE.

The SanDisk link is PROVEN pattern-dependent corrupt, and this project has
already measured its signature: large link outputs written to the ExFAT volume
can READ BACK AS ZEROS. A 163 MB binary written straight to that volume is
exactly the shape that has failed before, so a single SHA is not evidence.

Three independent things are required, and all three are recorded:
  (1) TWO matching reads, separated in time (the caller separates them);
  (2) a ZERO-RUN scan -- the specific corruption signature, measured, not
      assumed absent;
  (3) CORROBORATION that is not another read of the same bytes: the binary
      must EXECUTE. A zero-filled image cannot. The 458-test suite (which the
      brief requires anyway) and the runner's own startup are that witness.
"""
import hashlib, sys
from e29_common import *

assert os.environ.get('COPYFILE_DISABLE') == '1'
PASS = sys.argv[1] if len(sys.argv) > 1 else '1'

MAIN = {'runner': MAINLINE_RUNNER, 'suite': MAINLINE_SUITE}
NEW = {'runner': BYPASS_RUNNER, 'suite': BYPASS_SUITE}

def scan(p):
    """SHA + the zero-run signature, in one streaming pass."""
    h = hashlib.sha256()
    total = zeros = longest = cur = 0
    with p.open('rb') as f:
        while True:
            b = f.read(1 << 20)
            if not b: break
            h.update(b)
            total += len(b)
            z = b.count(0)
            zeros += z
            if z == len(b):
                cur += len(b); longest = max(longest, cur)
            else:
                # longest zero run inside a partly-zero block
                run = 0
                for byte in b:
                    if byte == 0:
                        run += 1; longest = max(longest, cur + run) if run == len(b) else max(longest, run)
                    else:
                        cur = 0; run = 0
                cur = 0
    return dict(bytes=total, sha256=h.hexdigest(), zero_bytes=zeros,
                zero_fraction=round(zeros / max(total, 1), 6),
                longest_zero_run=longest,
                longest_zero_run_MiB=round(longest / (1 << 20), 2))

rows = {}
for k, p in NEW.items():
    assert p.exists(), f'{k} missing at {p}'
    r = scan(p)
    m = MAIN[k]
    r['mainline_path'] = str(m)
    r['mainline_bytes'] = m.stat().st_size if m.exists() else None
    r['mainline_sha256'] = sha(m) if m.exists() else None
    r['same_size_as_mainline'] = r['bytes'] == r['mainline_bytes']
    r['differs_from_mainline'] = r['sha256'] != r['mainline_sha256']
    r['path'] = str(p)
    rows[k] = r

save(f'binary-pins-pass-{PASS}.json', dict(utc=utc(), pass_id=PASS, rows=rows))
for k, r in rows.items():
    print(f"{k:7} {r['bytes']:>12,} B  {r['sha256'][:16]}...  "
          f"zero_frac={r['zero_fraction']}  longest_zero_run={r['longest_zero_run_MiB']} MiB  "
          f"same_size_as_mainline={r['same_size_as_mainline']}  differs={r['differs_from_mainline']}")
print('# E29 BINPINS TAIL COMPLETE pass=' + PASS)
