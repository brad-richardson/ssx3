#!/usr/bin/env python3
"""Rebuild an existing imported GC course with verified terrain reset semantics."""
import argparse
import hashlib
import json
from pathlib import Path

from gamecube_surfaces import PROFILES, RESET_PROFILE, transfer_surfaces
from gamecube_world import World, assemble, validate_resource_capacities
from gamecube_reset_paths import compile_reset_paths


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--base-build', required=True, type=Path)
    ap.add_argument('--nbd', required=True, type=Path)
    ap.add_argument('--aip', type=Path, help='Matching donor AIP; defaults to NBD with .aip suffix')
    ap.add_argument('--output', required=True, type=Path)
    ap.add_argument('--profile', choices=PROFILES, default=RESET_PROFILE)
    args = ap.parse_args()
    if args.output.exists():
        ap.error('Preserving existing build; choose a fresh output')
    recipe = json.loads((args.base_build/'experiment.json').read_text())
    raw = args.nbd.read_bytes()
    if (recipe.get('mode') != 'gamecube-replace-terrain' or
            hashlib.sha256(raw).hexdigest() != recipe['donor_nbd_sha256']):
        raise ValueError('Terrain source must match the imported course recipe')
    original = (args.base_build/'BAM.BIG').read_bytes()
    world = World(original)
    group, track = recipe['group'], recipe['track']
    location = world.location(recipe['location'])
    if location['index'] != track or not location['group_start'] <= group <= location['last_group']:
        raise ValueError('Course group and track ownership mismatch')
    old = world.records(group)
    if any(e['track'] != track for e, _ in old if e['kind'] == 1):
        raise ValueError('Foreign terrain shares the imported group')
    records, receipt = transfer_surfaces(old, raw, recipe['matrix'], recipe['translation'],
                                          profile=args.profile, limit=recipe.get('limit'))
    if args.profile == RESET_PROFILE:
        donor = (args.aip or args.nbd.with_suffix('.aip')).read_bytes()
        if hashlib.sha256(donor).hexdigest() != recipe['cleanup_detail']['reset_paths'][0]['source_sha256']:
            raise ValueError('Reset route source must match the imported AIP recipe')
        if recipe.get('safe_reset_paths') or recipe.get('cleanup_detail', {}).get('safe_reset_paths'):
            raise ValueError('Reset network already compiled; rebuild from its original base')
        candidates = [(e, p) for e, p in records if e['kind'] == 14 and p]
        if len(candidates) != 1:
            raise ValueError('Expected one populated course AIP')
        aip, path_receipt = compile_reset_paths(candidates[0][1], donor, records,
            recipe['matrix'], recipe['translation'], recipe['scale'])
        records = [(dict(e, size=len(aip)), aip) if e == candidates[0][0] else (e, p) for e, p in records]
        recipe['safe_reset_paths'] = path_receipt
    archive, _ = assemble(world, {group: records})
    check = World(archive)
    key = lambda rows: [((e['kind'], e['track'], e['rid']), p) for e, p in rows]
    if key(check.records(group)) != key(records):
        raise RuntimeError('Surface archive readback differs')
    for g in world.index['groups']:
        i = g['index']
        if i != group and check.original_group_blocks(i) != world.original_group_blocks(i):
            raise RuntimeError(f'Unexpected change outside course group: {i}')
    receipt.update(base_archive_sha256=hashlib.sha256(original).hexdigest(),
                   archive_sha256=hashlib.sha256(archive).hexdigest(),
                   resource_count=validate_resource_capacities(check),
                   native_verified=False, iphone_verified=False)
    recipe['surfaces'] = receipt
    recipe['output_sha256'] = receipt['archive_sha256']
    args.output.mkdir(parents=True)
    (args.output/'BAM.BIG').write_bytes(archive)
    (args.output/'experiment.json').write_text(json.dumps(recipe, indent=2)+'\n')
    (args.output/'surfaces.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('mapped_reset_patches','changed_source_patches')}, indent=2))


if __name__ == '__main__':
    main()
