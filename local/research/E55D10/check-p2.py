#!/usr/bin/env python3
"""E55D10 Part 2 checker: validates S1 run receipts WITHOUT judging pixels.

Checks s1-result.json (bound, route, pins, caps, cards, frame proof),
the curated PNG SHAs against s1-receipts.txt, the private boot.log
[padscript] rows (exactly one Start + one Square press/release, no
others), and that curated PNG bytes total <= 2 MiB. It CANNOT prove
visual labels (menu/Options text, highlight, footer): those are worker
readings for the orchestrator's visual verdict, recorded in REPORT.md
and s1-receipts.txt, never asserted here.

Usage: python3 local/research/E55D10/check-p2.py
Exit 0 on PASS, 1 on FAIL.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN = Path('/Users/brad/dev/ssx3-work/E55D10/run/S1')
FAIL = []

PINS = {
    '/Users/brad/dev/ssx3-work/E55D3/build-taps/ps2xRuntime/ps2EntryRunner':
        'e282c8a79cb4ce3e616244d1cfb0b5ab6d522e2f262408c6ffa92860f211643f',
    '/Users/brad/dev/ssx3-work/E32-inputs/SSX 3 (USA).iso':
        '3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5',
    '/Users/brad/dev/ssx3-work/E32-inputs/cd/SLUS_207.72':
        '1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc',
    '/Users/brad/dev/ssx3-work/codegen-ssx3/register_functions.cpp':
        '8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3',
}
FORK_FULL = 'bab6eb382673155ffd756fe8db265964eeff9703'
CURATED = ['snap-760t-0029.24s.png', 'snap-919t-0035.28s.png', 'snap-945t-0036.29s.png']


def sha_of(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def check(name, ok, detail=''):
    print('%s %s %s' % ('ok' if ok else 'FAIL', name, detail))
    if not ok:
        FAIL.append(name)


def main():
    result = json.loads((HERE / 's1-result.json').read_text())
    check('stop_bound_target', result.get('bound') == 'target', str(result.get('bound')))
    check('route_exact', result.get('route') == '10611:start:250,13680:square:150',
          result.get('route', ''))
    check('stop_tick_920', result.get('stop_tick') == 920, str(result.get('stop_tick')))
    check('fork_pin', result.get('fork_pin_full') == FORK_FULL, result.get('fork_pin', ''))
    reads = result.get('sha_reads', [])
    check('two_sha_reads', len(reads) == 2, 'n=%d' % len(reads))
    check('sha_reads_match', len(reads) == 2 and reads[0] == reads[1], '')
    for path, want in PINS.items():
        got = (reads[0].get(path) if reads else None)
        check('pin_%s' % Path(path).name, got == want, (got or 'missing')[:16])
    check('caps_log', result.get('log_bytes', 1 << 60) <= 16 * 1024 * 1024,
          str(result.get('log_bytes')))
    check('caps_frames', result.get('frames_bytes', 1 << 60) <= 2 * 1024 * 1024 * 1024,
          str(result.get('frames_bytes')))
    check('caps_wall', result.get('wall_cap_s') == 500, str(result.get('wall_cap_s')))
    check('caps_progress', result.get('progress_cap_s') == 120,
          str(result.get('progress_cap_s')))
    proof = result.get('frame_proof') or {}
    check('frame_proof_ge_920', proof.get('tick', -1) >= 920, str(proof))
    check('cards_empty_unchanged',
          result.get('card_initial_sha256') == result.get('card_final_sha256')
          == 'f94015964371517ad24d36c71ea0c9bdc6fb4a23f3c46d7cc0def479feccb9ce'
          and result.get('card_final_files') == {'mc0': [], 'mc1': []},
          str(result.get('card_final_sha256'))[:16])

    log = (RUN / 'boot.log').read_bytes()
    presses = re.findall(rb'\[padscript\] press i=\d+ .* buttons=(0x[0-9a-f]+)', log)
    releases = re.findall(rb'\[padscript\] release i=\d+', log)
    check('pad_one_start_one_square',
          sorted(presses) == [b'0x0008', b'0x8000'], str(presses))
    check('pad_two_releases', len(releases) == 2, 'n=%d' % len(releases))
    check('pad_five_rows_total', log.count(b'[padscript]') == 5,
          'n=%d' % log.count(b'[padscript]'))
    check('pad_no_down_cross', b'0x0001' not in presses and b'0x0020' not in presses, '')

    receipts = (HERE / 's1-receipts.txt').read_text()
    total = 0
    for name in CURATED:
        p = HERE / name
        check('curated_present_%s' % name[:12], p.exists(), '')
        if p.exists():
            total += p.stat().st_size
            check('curated_sha_%s' % name[:12], sha_of(p) in receipts, sha_of(p)[:16])
        txt = HERE / (name.replace('.png', '.txt'))
        check('curated_meta_%s' % name[:12], txt.exists(), '')
    check('curated_png_le_2mib', total <= 2 * 1024 * 1024, str(total))

    check('screen_labels_not_asserted_here', True,
          'UNOBSERVED-BY-CHECKER by design: pixels judged only by orchestrator gate')
    if FAIL:
        print('CHECK-P2 FAIL: %s' % ', '.join(FAIL))
        return 1
    print('CHECK-P2 PASS: receipts hold; screen labels rest on orchestrator visual gate')
    return 0


if __name__ == '__main__':
    sys.exit(main())
