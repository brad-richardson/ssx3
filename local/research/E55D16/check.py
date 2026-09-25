#!/usr/bin/env python3
"""E55D16 post-run checker: pins, route, caps, pad rows, [MC] lines, frames.

Read-only. Visual/API verdicts rest with the orchestrator gate; this asserts
only byte-verifiable facts. No readability claim.
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

LANE = Path('/Users/brad/dev/ssx3-work/E55D16/run/S1')
HERE = Path('/Users/brad/dev/ssx3/local/research/E55D16')
FORK = Path('/Users/brad/dev/PS2Recomp')
RUNNER = Path('/Users/brad/dev/ssx3-work/E55D16/build/ps2xRuntime/ps2EntryRunner')
ELF = Path('/Users/brad/dev/ssx3-work/E32-inputs/cd/SLUS_207.72')
ISO = Path('/Users/brad/dev/ssx3-work/E32-inputs/SSX 3 (USA).iso')
CODEGEN = Path('/Users/brad/dev/ssx3-work/codegen-ssx3/register_functions.cpp')
SEED = Path('/Users/brad/dev/ssx3-work/E55D16/mc0')

FORK_PIN = 'fb11e182310555c65201635f8d6c7fe8e170de74'
PINS = {
    str(RUNNER): 'f4d7632ca371ed7b429a74ab535db6209968f7fcb4c69a2b2bf560c028b71711',
    str(ISO): '3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5',
    str(ELF): '1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc',
    str(CODEGEN): '8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3',
}
SEED_PINS = {
    'BASLUS-20772-GAM0001/icon.sys': 'eab225745ef6695109743410261609e0569c14edb1555bc8941a965b3890a49c',
    'BASLUS-20772-GAM0001/ssx1.ico': '5f8b5a9252f868d2fbc03378846b84ed601a2c872f47028711de67a4a714fc0b',
    'BASLUS-20772-GAM0001/BASLUS-20772-GAM0001': '4bdaee79a3bdaceef898bb44b6bcf62058e882a24237f8c81e46953a5067b78e',
    'BASLUS-20772-SET0001/icon.sys': 'dddf2d9c81a1c8bac2fe2036e1771dfa63635e3ae676760551defec2da67ee13',
    'BASLUS-20772-SET0001/ssx1.ico': '5f8b5a9252f868d2fbc03378846b84ed601a2c872f47028711de67a4a714fc0b',
    'BASLUS-20772-SET0001/BASLUS-20772-SET0001': '4a31a2d7e095e277edceae2243002055aa830019b3a1be64f126aee9129002f1',
}
SCRIPT_SHA = 'd30b7990d9334a786fdc6fe01e282e4daadc1d964d80e52570c4e2a3c741f0d8'
CARD_SHA = '02360f67dc0d6acfb169d73f7e1249840c18d4f632f52e13fbe8dbf18cc9a91b'
FRAME_PINS = {
    'snap-836t-0026.20s.png': 'e28562e7cb68054fb1ea3ad96e655ea4d64f1c82896808318fe88a8503df7537',
    'snap-1631t-0059.42s.png': '2189d09d534bfdf216ba51b535ccf4a3cc0aeaeb77ebafeb841a2c20cef44238',
    'snap-1803t-0067.48s.png': '76784a230de5b42ccbb7dffcba3c93c8a4f258a651360f2e918bc483fdb4c92e',
    'snap-2057t-0080.57s.png': '28537b5c21c6737ade410168b17421f4bddd37280be9c85af449ab0a475d5ed8',
    'snap-836t-0026.20s.txt': '681775cfd18396bbc2900f2bcf97519652138ce8eeec6135b31a11af5a05ace2',
    'snap-1631t-0059.42s.txt': '7b9beb0934e628459790ecea5e274dd59fa57ac721efb1c206c28fa516e8039e',
    'snap-1803t-0067.48s.txt': '1e212d1cb7aed78b292cfb71efcfa98f0e2f06d63313fc4618b57994df045794',
    'snap-2057t-0080.57s.txt': '0db668b927d80cf4f31ab158b501f9e9e2efc6d82a2666e77e8f4c72f6c7ed6a',
}

cases = []


def record(name, ok, detail=''):
    cases.append((name, ok))
    print('%s %s %s' % ('ok' if ok else 'MISMATCH', name, detail))


def sha_of(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    record('script_sha', sha_of(HERE / 'e55d16_boot.py') == SCRIPT_SHA)
    head = subprocess.run(['git', '-C', str(FORK), 'rev-parse', 'HEAD'],
                          capture_output=True, text=True)
    record('fork_pin', head.stdout.strip() == FORK_PIN, head.stdout.strip()[:12])
    st = subprocess.run(['git', '-C', str(FORK), 'status', '--porcelain'],
                        capture_output=True, text=True)
    record('fork_clean', st.returncode == 0 and not st.stdout.strip(),
           st.stdout.strip()[:100])
    gd = subprocess.run(['git', '-C', str(FORK), 'diff', '--exit-code',
                         '14b1e5cb', 'fb11e18', '--', 'ps2xRuntime/src/runner'])
    record('runner_dir_guard', gd.returncode == 0, 'rc=%d' % gd.returncode)
    for path, want in list(PINS.items()) + [(str(SEED / r), s) for r, s in SEED_PINS.items()]:
        record('pin_' + Path(path).name + '_' + str(len(path)),
               sha_of(path) == want, Path(path).name)
    res = json.loads((LANE / 'result.json').read_text())
    record('result_bound_target', res.get('bound') == 'target', res.get('bound'))
    record('result_stop_2100', res.get('stop_tick') == 2100)
    record('result_last_tick_ge_stop', res.get('last_hash_tick', 0) >= 2100,
           res.get('last_hash_tick'))
    fp = res.get('frame_proof') or {}
    record('result_frame_proof_ge_stop', fp.get('tick', 0) >= 2100, fp)
    record('result_rc_sigterm', res.get('runner_rc') == -15, res.get('runner_rc'))
    record('result_log_cap', res.get('log_bytes', 9**9) <= 16 * 1024 * 1024,
           res.get('log_bytes'))
    record('result_frames_cap', res.get('frames_bytes', 9**9) <= 2 * 1024**3,
           res.get('frames_bytes'))
    record('result_wall_cap', res.get('elapsed_s', 9**9) <= 500, res.get('elapsed_s'))
    sr = res.get('sha_reads', [])
    record('result_double_reads_match', len(sr) == 2 and sr[0] == sr[1])
    record('result_reads_match_pins',
           all(sr[0].get(p) == w for p, w in list(PINS.items()) +
               [(str(SEED / r), s) for r, s in SEED_PINS.items()]) if sr else False)
    record('cards_initial_final_match',
           res.get('card_initial_sha256') == res.get('card_final_sha256') == CARD_SHA,
           res.get('card_final_sha256', '')[:16])
    mc0 = (res.get('card_final_files') or {}).get('mc0', [])
    mc1 = (res.get('card_final_files') or {}).get('mc1', [])
    record('cards_mc0_six_mc1_empty', len(mc0) == 6 and mc1 == [],
           'mc0=%d mc1=%d' % (len(mc0), len(mc1)))
    got = {f['path']: f['sha256'] for f in mc0}
    record('cards_seed_shas', got == SEED_PINS)

    log = (LANE / 'boot.log').read_bytes()
    record('pad_armed', b'[padscript] armed n=10 source=env clock=vsync' in log)
    presses = re.findall(rb'press i=(\d+) now=(\d+)ms at=(\d+)ms hold=(\d+)ms buttons=(0x[0-9a-f]+)', log)
    want_btn = ['0x0008', '0x8000', '0x0040', '0x0040', '0x0040', '0x0040',
                '0x4000', '0x0040', '0x4000', '0x4000']
    record('pad_ten_presses', len(presses) == 10, len(presses))
    record('pad_order', [p[0] for p in presses] == [str(i).encode() for i in range(10)])
    record('pad_buttons', [p[4].decode() for p in presses] == want_btn)
    record('pad_releases', len(re.findall(rb'release i=\d+', log)) == 10)
    # det-hash tick correlation for [MC] lines
    events = []
    for m in re.finditer(rb'\[det-hash:v1\] tick=(\d+)|\[MC\] GetDir port=(\d+) \'([^\']*)\' maxent=(\d+) -> result=(-?\d+)', log):
        if m.group(1):
            tick = int(m.group(1))
        else:
            events.append((tick, m.group(3).decode(), int(m.group(5))))
    record('mc_getdir_count_14', len(events) == 14, len(events))
    wild_set = [e for e in events if e[1] == 'BASLUS-20772-SET*']
    wild_gam = [e for e in events if e[1] == 'BASLUS-20772-GAM*']
    wild_rep = [e for e in events if e[1] == 'BASLUS-20772-REP*']
    record('mc_set_wild_result1', len(wild_set) == 2 and all(e[2] == 1 for e in wild_set),
           wild_set)
    record('mc_gam_wild_result1', len(wild_gam) == 2 and all(e[2] == 1 for e in wild_gam),
           wild_gam)
    record('mc_rep_result0', len(wild_rep) == 2 and all(e[2] == 0 for e in wild_rep),
           wild_rep)
    files = [e for e in events if e[1].startswith('/BASLUS')]
    record('mc_file_getdirs_result1', len(files) == 8 and all(e[2] == 1 for e in files),
           len(files))
    record('mc_max_tick_below_1700', max(e[0] for e in events) < 1700,
           max(e[0] for e in events))
    reads = sorted(int(v) for v in re.findall(rb'Sync cmd=5 result=(\d+)', log))
    record('mc_reads_full_sizes', reads == [964, 964, 964, 964, 3276, 39777], reads)
    record('mc_no_errors', b'result=-' not in log)
    hashes = [int(v) for v in re.findall(rb'\[det-hash:v1\] tick=(\d+)', log)]
    record('hash_count_2112', len(hashes) == 2112, len(hashes))
    record('hash_no_error_markers',
           not any(m in log for m in (b'[det-hash] null', b'[det-hash] line cap',
                                      b'[det-hash] invalid')))
    for name, want in FRAME_PINS.items():
        p = HERE / name
        record('frame_' + name, p.exists() and sha_of(p) == want)
    png_bytes = sum((HERE / n).stat().st_size for n in FRAME_PINS if n.endswith('.png'))
    record('frames_png_le_2mib', png_bytes <= 2 * 1024 * 1024, png_bytes)
    record('result_copy_matches',
           sha_of(HERE / 's1-result.json') == sha_of(LANE / 'result.json'))
    bad = [n for n, ok in cases if not ok]
    print('%d/%d PASS' % (len(cases) - len(bad), len(cases)))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
