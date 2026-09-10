#!/usr/bin/env python3
"""Create test ISOs by substituting verified, fixed-size SSB blocks.

Streams the original once, writes fresh images on the share, then rereads every
output byte to verify its predicted SHA-256. Originals are never opened for writing.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time

from inspect_disc import Region, iso_files, file_region, digest


def replace_ranges(chunk, chunk_offset, replacements):
    out = bytearray(chunk)
    for offset, data in replacements:
        lo, hi = max(chunk_offset,offset), min(chunk_offset+len(chunk),offset+len(data))
        if lo < hi:
            out[lo-chunk_offset:hi-chunk_offset] = data[lo-offset:hi-offset]
    return bytes(out)


def stream_sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        while chunk := f.read(4*1024*1024):
            h.update(chunk)
    return h.hexdigest()


def build_images(iso_path, experiment_dirs):
    size = iso_path.stat().st_size
    builds = []
    with iso_path.open('rb') as source:
        disc = Region(source,0,size)
        _, files = iso_files(disc)
        world = file_region(disc,files,'DATA/WORLDS/BAM.BIG')
        world_hash = digest(world,'sha256')
        for directory in experiment_dirs:
            info = json.loads((directory/'experiment.json').read_text())
            if info['mode'] not in ('control','bump','recompress','uv','words') or info['source_archive_sha256'] != world_hash:
                raise ValueError('Experiment does not match source ISO world archive')
            archive = directory/'BAM.BIG'
            if archive.stat().st_size != world.size or stream_sha(archive) != info['rebuilt_archive_sha256']:
                raise ValueError('Rebuilt archive does not match its experiment manifest')
            replacements, cursor = [], 0
            # Independently verify that substituting the listed blocks constructs
            # the actual rebuilt archive, including unchanged prefix/suffix bytes.
            with archive.open('rb') as f:
                for block in info['changed_blocks']:
                    offset, length = block['archive_offset'], block['size']
                    if offset < cursor or offset+length > world.size:
                        raise ValueError('Overlapping or out-of-bounds block replacement')
                    if f.read(offset-cursor) != world.read(cursor,offset-cursor):
                        raise ValueError('Unlisted archive changes')
                    data = f.read(length)
                    old = world.read(offset,length)
                    if hashlib.sha256(data).hexdigest()!=block['rebuilt_sha256'] or hashlib.sha256(old).hexdigest()!=block['original_sha256']:
                        raise ValueError('Replacement block hash mismatch')
                    replacements.append((world.base+offset,data))
                    cursor = offset+length
                if f.read() != world.read(cursor,world.size-cursor):
                    raise ValueError('Unlisted archive suffix changes')
            destination = directory/f'SSX3-{info["mode"]}.iso'
            manifest = directory/'image.json'
            if destination.exists() or manifest.exists():
                raise ValueError(f'Image or manifest already exists in {directory}')
            if destination.resolve() == iso_path.resolve():
                raise ValueError('Output would replace source ISO')
            builds.append(dict(destination=destination,manifest=manifest,replacements=replacements,
                               info=info,hash=hashlib.sha256()))
        if len({b['destination'].resolve() for b in builds}) != len(builds):
            raise ValueError('Duplicate output directories')
        opened = []
        try:
            for b in builds:
                b['stream'] = b['destination'].open('xb')
                opened.append(b)
            source.seek(0)
            source_hash = hashlib.sha256()
            offset, last_update = 0, time.monotonic()
            while chunk := source.read(4*1024*1024):
                source_hash.update(chunk)
                for b in builds:
                    new = replace_ranges(chunk,offset,b['replacements'])
                    b['stream'].write(new)
                    b['hash'].update(new)
                offset += len(chunk)
                if time.monotonic()-last_update > 15:
                    print(f'Copied {offset/size:.0%} of source into {len(builds)} test images',flush=True)
                    last_update = time.monotonic()
            if offset != size:
                raise ValueError('Source size changed during copy')
        except BaseException:
            for b in opened:
                b['stream'].close()
                b['destination'].unlink()
            raise
        finally:
            for b in opened:
                b['stream'].close()
    for b in builds:
        print(f'Reading back {b["destination"].name} for full-file verification',flush=True)
        expected = b['hash'].hexdigest()
        if b['destination'].stat().st_size != size or stream_sha(b['destination']) != expected:
            raise ValueError(f'Output readback failed: {b["destination"]}')
        with b['destination'].open('rb') as f:
            _, output_files = iso_files(Region(f,0,size))
        if output_files != files:
            raise ValueError('Output ISO directory differs from source')
        report = dict(source_iso=str(iso_path),source_iso_sha256=source_hash.hexdigest(),
                      output_iso=str(b['destination']),output_iso_sha256=expected,size=size,
                      mode=b['info']['mode'],emulator_tested=False,
                      full_readback_verified=True,iso_directory_unchanged=True,
                      replacement_ranges=[dict(offset=o,size=len(d)) for o,d in b['replacements']],
                      experiment='experiment.json')
        with b['manifest'].open('x') as f:
            f.write(json.dumps(report,indent=2)+'\n')
        print(f'Verified {b["destination"]}: {expected}',flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('iso',type=Path)
    ap.add_argument('experiments',nargs='+',type=Path)
    args = ap.parse_args()
    build_images(args.iso,args.experiments)
