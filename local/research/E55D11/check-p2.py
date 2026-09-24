#!/usr/bin/env python3
"""E55D11 Part 2 checker: validates S1 run receipts WITHOUT judging pixels.

Checks s1-result.json (bound, route, pins, caps, cards, frame proof),
the curated PNG/txt SHAs against s1-receipts.txt, the private boot.log
[padscript] rows (exactly one Start + one Square + four separate Downs +
one Cross press/release, no other input), and the private probe.log
counts (4 getdir, all ok=0 reason=empty, all vsync < 1360; 0 mcread).
It CANNOT prove visual labels (Options/Save-Load text, highlight row,
footer): those are worker readings for the orchestrator's visual
verdict, recorded in REPORT.md and s1-receipts.txt, never asserted here.

Usage: python3 local/research/E55D11/check-p2.py
Exit 0 on PASS, 1 on FAIL.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN = Path('/Users/brad/dev/ssx3-work/E55D11/run/S1')
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
CROSS_TICK = 1360
CURATED = ['snap-1284t-0047.36s.png', 'snap-1454t-0053.41s.png']
EMPTY_CARD_SHA = 'f94015964371517ad24d36c71ea0c9bdc6fb4a23f3c46d7cc0def479feccb9ce'


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
    check('route_exact', result.get('route') ==
          '10611:start:250,13680:square:150,16683:down:150,17851:down:150,'
          '19019:down:150,20187:down:150,22689:cross:150',
          result.get('route', ''))
    check('stop_tick_1460', result.get('stop_tick') == 1460, str(result.get('stop_tick')))
    check('start_square_cross_ticks',
          (result.get('start_tick'), result.get('square_tick'), result.get('cross_tick'))
          == (636, 820, 1360),
          str((result.get('start_tick'), result.get('square_tick'), result.get('cross_tick'))))
    check('down_ticks_1000_1070_1140_1210', result.get('down_ticks') == [1000, 1070, 1140, 1210],
          str(result.get('down_ticks')))
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
    check('caps_frame_proof_grace', result.get('frame_proof_grace_s') == 120,
          str(result.get('frame_proof_grace_s')))
    proof = result.get('frame_proof') or {}
    check('frame_proof_ge_1460', proof.get('tick', -1) >= 1460, str(proof))
    check('cards_empty_unchanged',
          result.get('card_initial_sha256') == result.get('card_final_sha256')
          == EMPTY_CARD_SHA
          and result.get('card_final_files') == {'mc0': [], 'mc1': []}
          and result.get('card_initial_files') == {'mc0': [], 'mc1': []},
          str(result.get('card_final_sha256'))[:16])

    log = (RUN / 'boot.log').read_bytes()
    presses = re.findall(rb'\[padscript\] press i=\d+ .* buttons=(0x[0-9a-f]+)', log)
    releases = re.findall(rb'\[padscript\] release i=\d+', log)
    check('pad_one_start_one_square_four_downs_one_cross',
          sorted(presses) == sorted([b'0x0008', b'0x8000', b'0x0040', b'0x0040',
                                     b'0x0040', b'0x0040', b'0x4000']),
          str(presses))
    check('pad_press_order_start_square_downs_cross',
          presses == [b'0x0008', b'0x8000', b'0x0040', b'0x0040',
                      b'0x0040', b'0x0040', b'0x4000'],
          str(presses))
    check('pad_seven_releases', len(releases) == 7, 'n=%d' % len(releases))
    check('pad_rows_armed_plus_press_release',
          log.count(b'[padscript]') == 15 and b'[padscript] armed n=7' in log,
          'n=%d' % log.count(b'[padscript]'))

    probe = (RUN / 'probe.log').read_bytes().splitlines()
    getdirs = [l for l in probe if l.startswith(b'getdir')]
    mcreads = [l for l in probe if l.startswith(b'mcread')]
    check('probe_four_getdir', len(getdirs) == 4, 'n=%d' % len(getdirs))
    check('probe_getdir_all_empty_no_bytes',
          all(b'ok=0' in l and b'reason=empty' in l and l.rstrip().endswith(b'bytes=')
              for l in getdirs),
          '')
    ticks = []
    for l in getdirs:
        m = re.search(rb'vsync=(\d+)', l)
        ticks.append(int(m.group(1)) if m else -1)
    check('probe_getdir_have_ticks', all(t >= 0 for t in ticks), str(ticks))
    check('probe_getdir_all_before_cross', all(t < CROSS_TICK for t in ticks), str(ticks))
    check('probe_zero_mcread', len(mcreads) == 0, 'n=%d' % len(mcreads))
    check('probe_sha_matches_receipts',
          sha_of(RUN / 'probe.log') in (HERE / 's1-receipts.txt').read_text(),
          sha_of(RUN / 'probe.log')[:16])

    receipts = (HERE / 's1-receipts.txt').read_text()
    total_png = 0
    total_txt = 0
    for name in CURATED:
        p = HERE / name
        check('curated_present_%s' % name[:12], p.exists(), '')
        if p.exists():
            total_png += p.stat().st_size
            check('curated_sha_%s' % name[:12], sha_of(p) in receipts, sha_of(p)[:16])
        txt = HERE / (name.replace('.png', '.txt'))
        check('curated_meta_%s' % name[:12], txt.exists(), '')
        if txt.exists():
            total_txt += txt.stat().st_size
            check('curated_metasha_%s' % name[:12], sha_of(txt) in receipts,
                  sha_of(txt)[:16])
    check('curated_png_le_2mib', total_png <= 2 * 1024 * 1024, str(total_png))
    check('curated_txt_le_512kib', total_txt <= 512 * 1024, str(total_txt))

    check('screen_labels_not_asserted_here', True,
          'UNOBSERVED-BY-CHECKER by design: pixels judged only by orchestrator gate')
    check('api_outcome_not_asserted_here', True,
          'BY-DESIGN: getdir-ok=0 proves reach, not table bytes; A/B rests on gate')
    if FAIL:
        print('CHECK-P2 FAIL: %s' % ', '.join(FAIL))
        return 1
    print('CHECK-P2 PASS: receipts hold; screen/API labels rest on orchestrator visual gate')
    return 0


if __name__ == '__main__':
    sys.exit(main())
