# E25 restore procedure — tabled, NOT exercised

The host restart that opened E24 red wiped `/tmp`, taking 1,725 protected
files (1,578,996,782 B) and with them the runner, the suite and E24's boot.
E25 rebuilt the tree and snapshotted it to the SSD so the next restart costs a
**copy**, not a 530-second rebuild.

**This procedure was not tested.** Testing it would mean deleting the live
tree, and the brief forbids exercising the restore. Every command below is
written out and every digest it checks is recorded, but none of them was run.

## What is stored

| Artifact | Path | Bytes | SHA256 |
|---|---|---|---|
| Whole build tree, one tar | `/Volumes/Extreme SSD/ps2recomp-spike/P1/e25-snapshot/e18-mpeg-link.tar` | 1,762,803,200 | `9ded806562f1cc150b81040afd24588089fd4bc1f1cbffb7190bc2badb161d10` |
| Runner, standalone | `/Volumes/Extreme SSD/ps2recomp-spike/P1/e25-snapshot/ps2EntryRunner` | 163,529,696 | `e462e4482fbf5b3fe0902e793f9d677e51c56b220022bca619305f1f69967e22` |
| Suite, standalone | `/Volumes/Extreme SSD/ps2recomp-spike/P1/e25-snapshot/ps2x_tests` | 5,695,128 | `2152e5ad53f19741788aa3051e26184a9c5e831857114ce74407f199de5f04c0` |

Per-file manifest: `snapshot-manifest.json` — **7,342
files**, 1,748,192,253 B,
each with its own SHA256. The tar's member count was listed and equals the
manifest exactly (7,342).

## Why a tar and not a directory copy

The SSD is ExFAT with ~1 MiB allocation clusters. Copying 7,342 files
individually would allocate on the order of gigabytes of slack, and a prior
measurement on this volume showed large writes reading back as zeros. So the
tree is stored as **one** tar, and every artifact is re-read and re-hashed
after it lands (`reread_equal` is recorded true for all three).

## Restore — full tree

```sh
export COPYFILE_DISABLE=1
# 1. Refuse to overwrite a live tree.
test ! -e /tmp/e18-mpeg-link || { echo "tree present; nothing to restore"; exit 1; }
# 2. Verify the archive BEFORE trusting it.
shasum -a 256 "/Volumes/Extreme SSD/ps2recomp-spike/P1/e25-snapshot/e18-mpeg-link.tar"
#   expect 9ded806562f1cc150b81040afd24588089fd4bc1f1cbffb7190bc2badb161d10
# 3. Extract. `-C /tmp` because the tar holds the path `e18-mpeg-link/...`.
tar -C /tmp -xf "/Volumes/Extreme SSD/ps2recomp-spike/P1/e25-snapshot/e18-mpeg-link.tar"
# 4. Re-verify every file against the manifest.
python3 - <<'EOF'
import hashlib, json
from pathlib import Path
m = json.loads(Path('local/research/E25/snapshot-manifest.json').read_text())
bad = []
for row in m['entries']:
    p = Path(row['path'])
    if not p.exists():
        bad.append((row['path'], 'MISSING')); continue
    with p.open('rb') as f:
        if hashlib.file_digest(f, 'sha256').hexdigest() != row['sha256']:
            bad.append((row['path'], 'SHA'))
print(len(m['entries']), 'checked;', len(bad), 'bad')
for b in bad[:20]: print(' ', b)
EOF
```

## Restore — the two binaries only

E26 needs the runner to boot and the suite to re-verify. If the tree itself is
not needed, copy just these two back to the paths every driver and boot argv
names:

```sh
export COPYFILE_DISABLE=1
mkdir -p /tmp/e18-mpeg-link/runtime/ps2xRuntime /tmp/e18-mpeg-link/runtime/ps2xTest
cp -p "/Volumes/Extreme SSD/ps2recomp-spike/P1/e25-snapshot/ps2EntryRunner" /tmp/e18-mpeg-link/runtime/ps2xRuntime/ps2EntryRunner
cp -p "/Volumes/Extreme SSD/ps2recomp-spike/P1/e25-snapshot/ps2x_tests"  /tmp/e18-mpeg-link/runtime/ps2xTest/ps2x_tests
shasum -a 256 /tmp/e18-mpeg-link/runtime/ps2xRuntime/ps2EntryRunner \
              /tmp/e18-mpeg-link/runtime/ps2xTest/ps2x_tests
#   expect e462e4482fbf5b3fe0902e793f9d677e51c56b220022bca619305f1f69967e22
#          2152e5ad53f19741788aa3051e26184a9c5e831857114ce74407f199de5f04c0
```

A two-binary restore is enough to **boot** and to **run the 458 tests**. It is
not enough to build incrementally — for that, restore the tar.

## If the snapshot is gone too

Rebuild from the fork. The recipe is byte-exact and proven reproducible:
`configure-command.json` (cmake argv, asserted equal to E18's own receipt),
then `ninja -C /tmp/e18-mpeg-link/runtime -j2 ps2EntryRunner ps2x_tests`.
E25 measured 72.5 s configure + 530.8 s build, and the runner and suite came
back **bit-identical** to their pins.

## What this does NOT protect

The snapshot covers the E18 tree only. `/tmp/p1-link` and `/tmp/e17-map-link`
(1,150 files, 1,052,423,260 B) remain lost and are not rebuilt here — see the
report. Nothing was deleted to make room for this snapshot.

# E25 RESTORE TAIL COMPLETE
