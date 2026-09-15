#!/usr/bin/env python3
"""Measure everything a course conversion needs to know about a target slot.

Converting a Tricky course into an SSX 3 location needs a dozen numbers out of
the stock archive - which group holds the terrain, which track index the
records carry, which texture group the template patch's lightmap lives in,
how many race gates the slot has, what shape its kind-21 race line is. For
Aloha those were dug out by hand and written into `docs/aloha-conversion.md`
section 4; this reads them, so the next slot is a command rather than a dig.

Everything printed is read from the archive. The only judgement left is which
patch to use as the template, and the candidate list is ordered so the obvious
choice is first: patches whose page word matches the location's own track and
whose texture and lightmap are the most common pairing in the slot, which is
the "ordinary snow" surface a converted course wants to inherit.

    python3 tools/gamecube_slot_probe.py ARCHIVE ASS1 DSS2 ESS3
"""
import argparse
import collections
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gamecube_world import World

PATCH_SIZE = 430
ORDINAL_AT = 408
PAGE_AT = 412
BINDING_AT = 416


def patch_facts(payload):
    """Track, page and image bindings of one terrain record."""
    ordinal = struct.unpack_from('>I', payload, ORDINAL_AT)[0]
    page = struct.unpack_from('>I', payload, PAGE_AT)[0]
    texture, lightmap = struct.unpack_from('>HH', payload, BINDING_AT)
    return {'track': ordinal >> 24, 'rid': ordinal & 0xffffff, 'page': page,
            'page_track': page >> 16, 'texture_group': page & 0xffff,
            'texture': texture, 'lightmap': lightmap}


def race_line(payload):
    """kind-21: node count, marker count, total distance and the trailer."""
    nodes, stride, markers, size = struct.unpack_from('>4I', payload)
    trailer = 16 + nodes * stride
    total = struct.unpack_from('>f', payload, trailer)[0]
    pairs = [struct.unpack_from('>If', payload, trailer + 4 + 8 * i) for i in range(markers)]
    return {'nodes': nodes, 'node_stride': stride, 'markers': markers,
            'payload_size': size, 'total_distance': round(total, 1),
            'trailer': [(tag, round(distance, 1)) for tag, distance in pairs],
            'marker_fractions': [round(distance / total, 7)
                                 for tag, distance in pairs if tag == 1 and total]}


def probe(archive, code):
    world = World(Path(archive).read_bytes())
    location = world.location(code)
    group = location['last_group']
    records = world.records(group)

    patches, pages, pairs = [], collections.Counter(), collections.Counter()
    line = None
    for entry, payload in records:
        if entry['kind'] == 1 and entry['size'] == PATCH_SIZE:
            facts = patch_facts(payload)
            patches.append(facts)
            pages[facts['page']] += 1
            pairs[(facts['texture'], facts['lightmap'], facts['texture_group'])] += 1
        elif entry['kind'] == 21:
            line = race_line(payload)

    tracks = collections.Counter(p['track'] for p in patches)
    track = tracks.most_common(1)[0][0] if tracks else None
    # The template wants the slot's own track and the commonest image pairing:
    # that is the ordinary snow surface, which is what a converted course
    # inherits for every patch it brings in.
    ranked = sorted(patches, key=lambda p: (-pairs[(p['texture'], p['lightmap'],
                                                    p['texture_group'])],
                                            p['page'] >> 16 != track, p['rid']))
    return {
        'archive': str(archive), 'location': code, 'location_index': location['index'],
        'groups': [location['group_start'], location['last_group']],
        'group_count': location['group_count'], 'terrain_group': group,
        'records_in_terrain_group': len(records), 'terrain_patches': len(patches),
        'track': track,
        'pages': {hex(page): count for page, count in pages.most_common(6)},
        'template_candidates': [
            {'rid': p['rid'], 'page': hex(p['page']), 'texture_group': p['texture_group'],
             'texture': p['texture'], 'lightmap': p['lightmap'],
             'patches_sharing_images': pairs[(p['texture'], p['lightmap'], p['texture_group'])]}
            for p in ranked[:5]],
        'kind_counts': {str(k): v for k, v in sorted(location['kind_counts'].items(),
                                                     key=lambda kv: int(kv[0]))},
        'race_line': line,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('archive', type=Path)
    parser.add_argument('codes', nargs='+', help='location codes, e.g. ASS1 DSS2')
    parser.add_argument('--output', type=Path, help='JSON receipt')
    args = parser.parse_args()
    report = [probe(args.archive, code) for code in args.codes]
    if args.output:
        args.output.write_text(json.dumps(report, indent=2) + '\n')
    for slot in report:
        summary = {k: slot[k] for k in ('location', 'location_index', 'groups', 'terrain_group',
                                        'terrain_patches', 'track', 'pages')}
        print(json.dumps(summary, indent=2))
        print('  template candidates:', json.dumps(slot['template_candidates'][:3]))
        print('  race line:', json.dumps(slot['race_line']))
        print()


if __name__ == '__main__':
    main()
