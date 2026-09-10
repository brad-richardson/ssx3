#!/usr/bin/env python3
"""Re-encode every SSB block of an SSX 3 world archive in place (same offsets, same sizes).

A full-stream compression control: every block's decoded bytes stay identical, every
block keeps its original 32 KiB slot, header, and boundaries, and every other archive
byte is untouched. Blocks are encoded with the optimal parser, escalating the match
search when a block does not fit. Writes BAM.BIG plus an experiment.json that
build_test_images.py accepts (mode "recompress").
"""
import argparse
import hashlib
import io
import json
from multiprocessing import Pool
from pathlib import Path

from inspect_disc import Region, big_members, file_region
from probe_worlds import refpack
from refpack_optimal import encode

LEVELS = ((128, 64), (256, 10**9), (512, 10**9), (1024, 10**9))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encode_block(job):
    offset, packed = job
    raw, consumed = refpack(packed[8:])
    capacity = len(packed) - 8
    for candidates, skip in LEVELS:
        out = encode(raw, candidates, skip)
        if len(out) <= capacity:
            break
    else:
        raise ValueError(f'Block at SSB offset {offset} does not fit: {len(out)} > {capacity}')
    if refpack(out)[0] != raw:
        raise ValueError(f'Block at SSB offset {offset} failed decoder check')
    new_block = packed[:8] + out + bytes(capacity - len(out))
    return dict(ssb_offset=offset, size=len(packed), decoded_size=len(raw),
                original_compressed_size=consumed, rebuilt_compressed_size=len(out),
                level=(candidates, skip), block=new_block, original_sha256=sha(packed), rebuilt_sha256=sha(new_block))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('archive', type=Path)
    ap.add_argument('--world-report', type=Path, default=Path('local/reports/ssx3-world.json'))
    ap.add_argument('--output', type=Path, required=True, help='New directory; never overwrites')
    ap.add_argument('--jobs', type=int, default=8)
    args = ap.parse_args()
    if args.output.exists():
        ap.error('Output directory already exists')
    original = args.archive.read_bytes()
    report = json.loads(args.world_report.read_text())
    if sha(original) != report['archive_sha256']:
        raise ValueError('Source archive differs from inspected baseline')
    archive = Region(io.BytesIO(original), 0, len(original))
    _, members = big_members(archive)
    ssb = file_region(archive, members, 'data/worlds/bam.ssb')
    jobs = [(b['offset'], ssb.read(b['offset'], b['size'])) for g in report['groups'] for b in g['blocks']]
    with Pool(args.jobs) as pool:
        results = pool.map(encode_block, jobs, chunksize=4)
    rebuilt = bytearray(original)
    changed = []
    for r in results:
        absolute = ssb.base + r['ssb_offset']
        rebuilt[absolute:absolute + r['size']] = r['block']
        changed.append(dict(archive_offset=absolute, ssb_offset=r['ssb_offset'], size=r['size'],
                            decoded_size=r['decoded_size'], original_compressed_size=r['original_compressed_size'],
                            rebuilt_compressed_size=r['rebuilt_compressed_size'], level=list(r['level']),
                            original_sha256=r['original_sha256'], rebuilt_sha256=r['rebuilt_sha256']))
    # Independent check: decoded groups are identical to the inspected baseline.
    rebuilt_region = Region(io.BytesIO(bytes(rebuilt)), 0, len(rebuilt))
    _, members2 = big_members(rebuilt_region)
    ssb2 = file_region(rebuilt_region, members2, 'data/worlds/bam.ssb')
    for g in report['groups']:
        raw = b''.join(refpack(ssb2.read(b['offset'], b['size'])[8:])[0] for b in g['blocks'])
        if sha(raw) != g['sha256']:
            raise ValueError(f'Group {g["index"]} decodes differently after recompression')
    if rebuilt[:ssb.base] != original[:ssb.base] or rebuilt[ssb.base + ssb.size:] != original[ssb.base + ssb.size:]:
        raise ValueError('Bytes outside the SSB member changed')
    details = dict(mode='recompress', source_archive_sha256=sha(original), rebuilt_archive_sha256=sha(rebuilt),
                   archive_bytes=len(rebuilt), blocks=len(changed),
                   original_compressed_total=sum(c['original_compressed_size'] for c in changed),
                   rebuilt_compressed_total=sum(c['rebuilt_compressed_size'] for c in changed),
                   levels_used={str(l): sum(1 for c in changed if c['level'] == list(l)) for l in LEVELS},
                   changed_blocks=changed, unrelated_archive_bytes_unchanged=True, decoded_groups_unchanged=True,
                   emulator_tested=False)
    args.output.mkdir(parents=True, exist_ok=False)
    path = args.output / 'BAM.BIG'
    with path.open('xb') as f:
        f.write(rebuilt)
    if sha(path.read_bytes()) != details['rebuilt_archive_sha256']:
        raise ValueError('Saved archive failed readback hash verification')
    (args.output / 'experiment.json').write_text(json.dumps(details, indent=2) + '\n')
    print(json.dumps({k: v for k, v in details.items() if k != 'changed_blocks'}, indent=2))


if __name__ == '__main__':
    main()
