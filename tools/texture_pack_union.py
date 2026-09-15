#!/usr/bin/env python3
"""Union many courses' texture dumps into one deduplicated, family-grouped set.

A replacement is keyed by content, not by course, so one pack can cover the
whole game — and it has to, because courses share most of their art (the rider,
the HUD, trees, rocks). This takes one `--course CODE=DUMP_DIR:RUN_DIR` per
course, keeps each distinct texture once, and writes
`<output>/<asset family>/` so each family can go through the model that suits it
(docs/texture-remaster.md).

Every decision is delegated to `texture_dump_inventory`: the same name parser,
the same framebuffer test, the same ride-phase split from each run's own rider
trace, and the same family rule.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import shutil

from texture_dump_inventory import family, is_framebuffer, parse, run_boundaries


def course_textures(dump, run):
    """Every non-framebuffer course texture in one dump, mip sidecars excluded."""
    entries = [e for e in (parse(p) for p in sorted(dump.iterdir()) if p.suffix.lower() == '.png') if e]
    briefing, start = run_boundaries(run)
    keep = []
    for entry in entries:
        if entry['mip_level'] or is_framebuffer(entry) or entry['mtime'] < briefing:
            continue
        entry['phase'] = 'ride' if entry['mtime'] >= start else 'course load'
        keep.append(entry)
    return entries, keep


def parse_course(value):
    code, sep, rest = value.partition('=')
    dump, colon, run = rest.partition(':')
    if not (sep and colon):
        raise argparse.ArgumentTypeError('Use CODE=DUMP_DIR:RUN_DIR')
    return code, Path(dump), Path(run)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--course', type=parse_course, action='append', required=True,
                    metavar='CODE=DUMP_DIR:RUN_DIR', help='Repeatable, one per course')
    ap.add_argument('--output', type=Path, required=True, help='Directory for the grouped union')
    ap.add_argument('--report', type=Path, help='Write the JSON report here')
    args = ap.parse_args()
    if args.output.exists() and any(args.output.iterdir()):
        raise SystemExit(f'{args.output} is not empty; choose a fresh directory')
    union, per_course, dumped_total = {}, {}, 0
    for code, dump, run in args.course:
        if not dump.is_dir():
            raise SystemExit(f'{code}: no dump directory at {dump}')
        entries, keep = course_textures(dump, run)
        dumped_total += len(entries)
        fresh = 0
        for entry in keep:
            # Name is the key: same texture, same name, whichever course showed it.
            if entry['name'] not in union:
                union[entry['name']] = entry
                union[entry['name']]['courses'] = []
                fresh += 1
            union[entry['name']]['courses'].append(code)
        per_course[code] = {'dumped': len(entries), 'course_textures': len(keep), 'new_here': fresh}
        print(f"{code:6} {len(entries):>5} dumped  {len(keep):>4} course textures  {fresh:>4} new")
    for entry in union.values():
        directory = args.output / family(entry)
        directory.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(entry['path'], directory / entry['name'])
    shared = Counter(len(e['courses']) for e in union.values())
    report = {
        'courses': len(args.course), 'dumped_files': dumped_total,
        'union_textures': len(union),
        'by_family': dict(Counter(family(e) for e in union.values()).most_common()),
        'by_format': dict(Counter(e['format_name'] for e in union.values()).most_common()),
        'mipmapped': sum(1 for e in union.values() if e['mipmapped']),
        'bytes': sum(e['bytes'] for e in union.values()),
        'courses_per_texture': {str(k): v for k, v in sorted(shared.items())},
        'per_course': per_course,
        'output': str(args.output),
        'textures': {name: {'courses': e['courses'], 'family': family(e),
                            'format': e['format_name'], 'size': [e['width'], e['height']]}
                     for name, e in sorted(union.items())},
    }
    if args.report:
        args.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'textures'}, indent=2))


if __name__ == '__main__':
    main()
