#!/usr/bin/env python3
"""E55D4 Part 1: pure A/A parser/comparator for two pinned runs.

Reads each run dir (result.json, boot.log, probe.log) and decides:
  PASS — both traces contain an exact consecutive hash prefix 1..2053
    (later phase-2 rows allowed, prefix only is compared) with identical
    (tick,eeCycle,rdram,scratch,vu1Data,vu1Code,combined,count) on every
    prefix row; identical ordered pad/getdir/mcread records with
    vsync <= 2053, including exact payload bytes and skip/failure statuses;
    a persisted complete probe line with vsync > 2053 on each side (flush
    proof: the tap writes sequentially, so a durable later line implies the
    whole <= 2053 prefix survived SIGTERM); no cap marker; identical fresh
    card manifests including mtimes; no live pad/physical input.
  FAIL — a measured A/A difference (not proof of its cause). Both the first
    differing hash tick and the first differing shared-seq probe record are
    computed before returning, and both are reported (either may be null).
  OTHER — a shorter/incomplete trace, cap marker, hash-error marker,
    malformed/nonconsecutive probe framing, a missing probe file, a
    truncated (non-newline-terminated) final probe line, a missing flush
    proof, or a live-pad gate hit (bounded run, not a full comparison).
    The live-pad gate adjudicates a full `hidutil list` text by row
    (Class/Product/UserClass columns plus UsagePage/Usage): the known
    internal Apple storage controller is not a gamepad, while an actual
    gamepad/joystick product or an ambiguous controller row is OTHER.

Usage: e55d4_compare.py <runA> <runB> [--json-out <path>]
                        [--hidutil-list <path>]
       e55d4_compare.py --self-check   (synthetic fixtures only, no boots)
Pure stdlib; reads inputs, never boots, never touches the lease.
"""
import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

STOP_TICK = 2053
HASH_RE = re.compile(
    r'\[det-hash:v1\] tick=(\d+) eeCycle=(\d+) rdram=([0-9a-f]{16}) '
    r'scratch=([0-9a-f]{16}) vu1Data=([0-9a-f]{16}) vu1Code=([0-9a-f]{16}) '
    r'combined=([0-9a-f]{16}) count=(\d+)\b')
HASH_ERROR_MARKERS = ('[det-hash] null', '[det-hash] line cap', '[det-hash] invalid')
PROBE_SEQ = re.compile(r'^(pad|getdir|mcread|cap) seq=(\d+)\b')
PROBE_ORD = re.compile(r'\bord=(\d+)\b')
PROBE_VSYNC = re.compile(r'vsync=(\d+)')
HASH_FIELDS = ('tick', 'eeCycle', 'rdram', 'scratch', 'vu1Data', 'vu1Code', 'combined', 'count')

# Known internal Apple devices whose names contain 'Controller' but which are
# not game input (E55D4: AppleANS3CGv2Controller = internal NAND temp sensor,
# UsagePage 65280 vendor / Usage 5, Product 'NAND CH0 temp').
HID_KNOWN_INTERNAL = ('AppleANS3CGv2Controller',)
HID_GAME_USAGES = (4, 5, 8)  # HID Generic Desktop: Joystick / Game Pad / Multi-axis
HID_GAME_NAME = re.compile(r'\b(game\s*pad|joystick)\b', re.IGNORECASE)
HID_ROW_SPLIT = re.compile(r'\s{2,}')


def classify_hid(text):
    """Classify a full `hidutil list` text by row, not by blob substring.

    Each row is split into columns; UsagePage/Usage come from their columns
    and name matching uses the Class/Product/UserClass tail. A row is
    flagged only for an actual gamepad/joystick product, a Generic-Desktop
    game usage (page 1, usage 4/5/8), or an ambiguous non-allowlisted
    'controller' row. The known internal Apple storage controller is
    recorded, not flagged.
    """
    flagged = []
    known_internal = []
    rows = 0
    for raw in text.splitlines():
        row = raw.strip()
        if not row or row.startswith('Services:') or row.startswith('VendorID'):
            continue
        fields = HID_ROW_SPLIT.split(row)
        if len(fields) < 6:
            continue
        rows += 1
        try:
            usage = (int(fields[3]), int(fields[4]))
        except ValueError:
            usage = (None, None)
        tail = ' '.join(fields[7:]) if len(fields) > 7 else row
        if any(name in row for name in HID_KNOWN_INTERNAL):
            known_internal.append(row[:160])
            continue
        if HID_GAME_NAME.search(tail):
            flagged.append(('game_name', row[:160]))
        elif usage[0] == 1 and usage[1] in HID_GAME_USAGES:
            flagged.append(('game_usage', row[:160]))
        elif 'controller' in tail.lower():
            flagged.append(('ambiguous_controller', row[:160]))
    return {'flag': bool(flagged), 'flagged': flagged,
            'known_internal': known_internal, 'rows': rows}


def split_persisted(data):
    """Split probe bytes into (complete_lines, truncated).

    Only newline-terminated lines count as persisted; a trailing chunk
    without '\\n' is a partial write (or torn tail) and is excluded.
    """
    if not data:
        return ([], False)
    if data.endswith(b'\n'):
        return (data[:-1].split(b'\n'), False)
    chunks = data.split(b'\n')
    return (chunks[:-1], True)


def parse_hashes(data):
    rows = []
    for match in HASH_RE.finditer(data):
        tick = int(match.group(1))
        rows.append((tick,) + tuple(
            int(match.group(i)) if i in (2, 8) else match.group(i) for i in range(2, 9)))
    errors = [marker for marker in HASH_ERROR_MARKERS if marker in data]
    return rows, errors


def hash_consecutive(rows):
    return [row[0] for row in rows] == list(range(1, len(rows) + 1))


def hash_prefix_ok(rows):
    """Exact consecutive prefix 1..STOP_TICK; later rows allowed (phase 2)."""
    return (len(rows) >= STOP_TICK
            and [row[0] for row in rows[:STOP_TICK]] == list(range(1, STOP_TICK + 1)))


def parse_probe(data):
    """Parse persisted probe bytes; framing validated on complete lines."""
    complete, truncated = split_persisted(data)
    lines = [c.decode('utf-8', errors='replace') for c in complete]
    families = []
    seqs = []
    ords = {'pad': [], 'getdir': [], 'mcread': []}
    vsyncs = []
    capped = False
    malformed = []
    for lineno, line in enumerate(lines, 1):
        match = PROBE_SEQ.match(line)
        vmatch = PROBE_VSYNC.search(line)
        if not match or not vmatch:
            malformed.append(lineno)
            continue
        family, seq = match.group(1), int(match.group(2))
        families.append(family)
        seqs.append(seq)
        vsyncs.append(int(vmatch.group(1)))
        if family == 'cap':
            capped = True
        else:
            omatch = PROBE_ORD.search(line)
            ords[family].append(int(omatch.group(1)) if omatch else None)
    framing_ok = (not malformed and seqs == list(range(1, len(seqs) + 1))
                  and all(vals == list(range(1, len(vals) + 1))
                          and all(v is not None for v in vals)
                          for vals in ords.values()))
    proof_vsync = max(vsyncs) if vsyncs else None
    windowed = [(seq, line) for seq, fam, vsync, line
                in zip(seqs, families, vsyncs, lines)
                if fam != 'cap' and vsync <= STOP_TICK]
    return {'lines': lines, 'truncated': truncated, 'framing_ok': framing_ok,
            'malformed': malformed, 'capped': capped,
            'proof_vsync': proof_vsync, 'windowed': windowed}


def load_run(run_dir):
    run_dir = Path(run_dir)
    result = json.loads((run_dir / 'result.json').read_text())
    boot = (run_dir / 'boot.log').read_text(errors='replace')
    probe_path = Path(result.get('probe_file', run_dir / 'probe.log'))
    probe = probe_path.read_bytes() if probe_path.exists() else None
    return result, boot, probe


def summarize(result, boot, probe_data):
    rows, errors = parse_hashes(boot)
    probe = parse_probe(probe_data) if probe_data is not None else None
    return {
        'bound': result.get('bound'),
        'hash_rows': len(rows),
        'hash_consecutive_from_1': hash_consecutive(rows) if rows else False,
        'hash_errors': errors,
        'last_hash_tick': rows[-1][0] if rows else 0,
        'log_bytes': result.get('log_bytes'),
        'probe_lines': len(probe['lines']) if probe else 0,
        'probe_windowed_lines': len(probe['windowed']) if probe else 0,
        'probe_framing_ok': probe['framing_ok'] if probe else False,
        'probe_truncated': probe['truncated'] if probe else None,
        'probe_capped': probe['capped'] if probe else None,
        'probe_malformed': probe['malformed'] if probe else None,
        'probe_proof_vsync': probe['proof_vsync'] if probe else None,
        'probe_bytes': result.get('probe_bytes'),
        'probe_missing': probe is None,
        'card_initial_sha256': result.get('card_initial_sha256'),
        'card_final_sha256': result.get('card_final_sha256'),
        'gamepad_like': bool((result.get('hidutil') or {}).get('gamepad_like')),
    }


def first_hash_diff(rows_a, rows_b):
    for tick, row_a, row_b in zip(range(1, STOP_TICK + 1),
                                  rows_a[:STOP_TICK], rows_b[:STOP_TICK]):
        if row_a != row_b:
            fields = [name for name, va, vb in zip(HASH_FIELDS, row_a, row_b) if va != vb]
            return {'differ': True, 'first_hash_tick': tick, 'fields': fields,
                    'row_a': list(row_a), 'row_b': list(row_b)}
    return {'differ': False, 'first_hash_tick': None}


def first_probe_diff(win_a, win_b):
    for (seq_a, line_a), (seq_b, line_b) in zip(win_a, win_b):
        if line_a != line_b:
            return {'differ': True, 'reason': 'probe_difference',
                    'first_probe_seq': seq_a, 'line_a': line_a[:512],
                    'line_b': line_b[:512]}
    if len(win_a) != len(win_b):
        longer = win_a if len(win_a) > len(win_b) else win_b
        return {'differ': True, 'reason': 'probe_length_difference',
                'first_probe_seq': longer[min(len(win_a), len(win_b))][0],
                'lines_a': len(win_a), 'lines_b': len(win_b)}
    return {'differ': False, 'first_probe_seq': None}


def compare(run_a, run_b, hid_text=None):
    res_a, boot_a, probe_a = load_run(run_a)
    res_b, boot_b, probe_b = load_run(run_b)
    out = {'run_a': str(run_a), 'run_b': str(run_b),
           'summary_a': summarize(res_a, boot_a, probe_a),
           'summary_b': summarize(res_b, boot_b, probe_b)}

    def other(reason, **extra):
        out.update({'verdict': 'OTHER', 'reason': reason})
        out.update(extra)
        return out

    parsed_a = parse_probe(probe_a) if probe_a is not None else None
    parsed_b = parse_probe(probe_b) if probe_b is not None else None
    for tag, summ in (('A', out['summary_a']), ('B', out['summary_b'])):
        if summ['probe_missing']:
            return other('probe_missing_%s' % tag)
    assert parsed_a is not None and parsed_b is not None
    parsed = {'A': parsed_a, 'B': parsed_b}
    for tag in ('A', 'B'):
        summ = out['summary_' + tag.lower()]
        if parsed[tag]['truncated']:
            return other('probe_truncated_%s' % tag,
                         persisted_lines=len(parsed[tag]['lines']))
        if not parsed[tag]['framing_ok']:
            return other('probe_framing_%s' % tag,
                         malformed=parsed[tag]['malformed'])
        if summ['hash_errors']:
            return other('hash_error_%s' % tag, markers=summ['hash_errors'])
        if parsed[tag]['capped']:
            return other('probe_cap_%s' % tag)

    rows_a, _ = parse_hashes(boot_a)
    rows_b, _ = parse_hashes(boot_b)
    complete_a = res_a.get('bound') == 'target' and hash_prefix_ok(rows_a)
    complete_b = res_b.get('bound') == 'target' and hash_prefix_ok(rows_b)
    if not (complete_a and complete_b):
        return other('incomplete_trace',
                     complete_a=complete_a, complete_b=complete_b,
                     rows_a=len(rows_a), rows_b=len(rows_b),
                     bound_a=res_a.get('bound'), bound_b=res_b.get('bound'))

    for tag, parsed in (('A', parsed_a), ('B', parsed_b)):
        if parsed['proof_vsync'] is None or parsed['proof_vsync'] <= STOP_TICK:
            return other('probe_unproven_%s' % tag,
                         proof_vsync=parsed['proof_vsync'])

    hash_diff = first_hash_diff(rows_a, rows_b)
    probe_diff = first_probe_diff(parsed_a['windowed'], parsed_b['windowed'])
    if hash_diff['differ'] or probe_diff['differ']:
        if hash_diff['differ'] and probe_diff['differ']:
            reason = 'hash_and_probe_difference'
        elif hash_diff['differ']:
            reason = 'hash_difference'
        else:
            reason = probe_diff['reason']
        fail = {'verdict': 'FAIL', 'reason': reason,
                'first_hash_tick': hash_diff['first_hash_tick'],
                'first_probe_seq': probe_diff['first_probe_seq']}
        if hash_diff['differ']:
            fail.update({k: v for k, v in hash_diff.items()
                         if k not in ('differ', 'first_hash_tick')})
        if probe_diff['differ']:
            fail.update({k: v for k, v in probe_diff.items()
                         if k not in ('differ', 'reason', 'first_probe_seq')})
        out.update(fail)
        return out

    for key in ('card_initial_files', 'card_final_files',
                'card_initial_sha256', 'card_final_sha256'):
        if res_a.get(key) != res_b.get(key):
            out.update({'verdict': 'FAIL', 'reason': 'card_manifest_difference', 'key': key,
                        'first_hash_tick': None, 'first_probe_seq': None})
            return out

    if hid_text is not None:
        hid_cls = classify_hid(hid_text)
        out['hid_classification'] = {
            'flag': hid_cls['flag'], 'flagged': hid_cls['flagged'],
            'known_internal': hid_cls['known_internal'], 'rows': hid_cls['rows']}
        if hid_cls['flag']:
            return other('live_pad_present',
                         hid_classification=out['hid_classification'],
                         hidutil_a=res_a.get('hidutil'), hidutil_b=res_b.get('hidutil'))
    elif out['summary_a']['gamepad_like'] or out['summary_b']['gamepad_like']:
        return other('live_pad_present',
                     note='legacy substring flag; no full hidutil list adjudicated',
                     hidutil_a=res_a.get('hidutil'), hidutil_b=res_b.get('hidutil'))

    out.update({'verdict': 'PASS', 'reason': 'identical_to_tick_%d' % STOP_TICK,
                'hash_rows': STOP_TICK,
                'probe_lines': len(parsed_a['windowed'])})
    return out


PAD_OK = ('pad seq=%d vsync=%d ord=%d port=0 slot=0 addr=0x12345678 len=32 ok=1 bytes=%s')
GETDIR_EMPTY = ('getdir seq=2 vsync=11 ord=1 port=0 slot=0 addr=0x10000000 '
                'entries=0 max=16 len=0 ok=0 reason=empty bytes=')
MCREAD_OK = ('mcread seq=%d vsync=%d ord=%d fd=3 addr=0x10010000 req=64 len=64 '
             'ok=1 err=- bytes=%s')


def _write_fake_run(parent, label, ticks=STOP_TICK, hash_mut=None,
                    probe_lines=None, raw_probe=None, drop_probe=False,
                    bound='target', manifest=None, gamepad=False):
    lane = Path(parent) / label
    lane.mkdir(parents=True)
    boot_lines = []
    for tick in range(1, ticks + 1):
        row = {'tick': tick, 'eeCycle': 1000 + tick, 'rdram': 'a' * 16,
               'scratch': 'b' * 16, 'vu1Data': 'c' * 16, 'vu1Code': 'd' * 16,
               'combined': 'e' * 16, 'count': tick * 3}
        if hash_mut and tick == hash_mut[0]:
            row[hash_mut[1]] = hash_mut[2]
        boot_lines.append(
            '[det-hash:v1] tick={tick} eeCycle={eeCycle} rdram={rdram} '
            'scratch={scratch} vu1Data={vu1Data} vu1Code={vu1Code} '
            'combined={combined} count={count}'.format(**row))
    (lane / 'boot.log').write_text('\n'.join(boot_lines) + '\n')
    if probe_lines is None:
        probe_lines = [
            PAD_OK % (1, 10, 1, 'ab' * 32),
            GETDIR_EMPTY,
            MCREAD_OK % (3, 12, 1, 'cd' * 64),
            PAD_OK % (4, 2054, 2, 'ef' * 32),
        ]
    if raw_probe is not None:
        probe_bytes = raw_probe
    else:
        probe_bytes = ('\n'.join(probe_lines) + '\n').encode()
    if not drop_probe:
        (lane / 'probe.log').write_bytes(probe_bytes)
    files = manifest if manifest is not None else {'mc0': [], 'mc1': []}
    result = {'label': label, 'bound': bound, 'stop_tick': STOP_TICK,
              'log_bytes': len('\n'.join(boot_lines)),
              'probe_bytes': 0 if drop_probe else len(probe_bytes),
              'probe_file': str(lane / 'probe.log'),
              'card_initial_files': files, 'card_final_files': files,
              'card_initial_sha256': 'x', 'card_final_sha256': 'x',
              'hidutil': {'gamepad_like': gamepad}}
    (lane / 'result.json').write_text(json.dumps(result) + '\n')
    return lane


def self_check():
    cases = []

    def check(name, verdict, reason=None, extra=None, **kwargs):
        with tempfile.TemporaryDirectory(prefix='e55d4-self-') as tmp:
            lanes = kwargs.pop('lanes')
            got = compare(*lanes(tmp))
        ok = got['verdict'] == verdict and (reason is None or got['reason'] == reason)
        if extra:
            ok = ok and all(got.get(k) == v for k, v in extra.items())
        cases.append((name, ok, got['verdict'], got['reason']))
        return ok

    def base(tmp):
        return (_write_fake_run(tmp, 'A'), _write_fake_run(tmp, 'B'))

    def extra_hashes_ignored(tmp):
        return (_write_fake_run(tmp, 'A', ticks=2055),
                _write_fake_run(tmp, 'B', ticks=2055,
                                hash_mut=(2055, 'combined', 'f' * 16)))

    def high_vsync_only(tmp):
        lane_b = _write_fake_run(tmp, 'B')
        with open(lane_b / 'probe.log', 'ab') as f:
            f.write((PAD_OK % (5, 2055, 3, 'aa' * 32) + '\n').encode())
        return (_write_fake_run(tmp, 'A'), lane_b)

    def hash_diff(tmp):
        return (_write_fake_run(tmp, 'A'),
                _write_fake_run(tmp, 'B', hash_mut=(777, 'combined', 'f' * 16)))

    def probe_diff(tmp):
        bad = MCREAD_OK % (3, 12, 1, 'ce' + 'cd' * 63)
        lines = [PAD_OK % (1, 10, 1, 'ab' * 32), GETDIR_EMPTY, bad,
                 PAD_OK % (4, 2054, 2, 'ef' * 32)]
        return (_write_fake_run(tmp, 'A'), _write_fake_run(tmp, 'B', probe_lines=lines))

    def both_diff(tmp):
        bad = MCREAD_OK % (3, 12, 1, 'ce' + 'cd' * 63)
        lines = [PAD_OK % (1, 10, 1, 'ab' * 32), GETDIR_EMPTY, bad,
                 PAD_OK % (4, 2054, 2, 'ef' * 32)]
        return (_write_fake_run(tmp, 'A'),
                _write_fake_run(tmp, 'B', hash_mut=(777, 'combined', 'f' * 16),
                                probe_lines=lines))

    def truncated_trace(tmp):
        return (_write_fake_run(tmp, 'A', ticks=2000, bound='progress_cap'),
                _write_fake_run(tmp, 'B'))

    def no_probe(tmp):
        return (_write_fake_run(tmp, 'A', drop_probe=True, bound='exit'),
                _write_fake_run(tmp, 'B'))

    def truncated_probe(tmp):
        raw = ('\n'.join([PAD_OK % (1, 10, 1, 'ab' * 32),
                           GETDIR_EMPTY,
                           MCREAD_OK % (3, 12, 1, 'cd' * 64),
                           PAD_OK % (4, 2054, 2, 'ef' * 32)])).encode()
        return (_write_fake_run(tmp, 'A', raw_probe=raw, bound='flush_unproven'),
                _write_fake_run(tmp, 'B'))

    def seq_gap(tmp):
        lines = [PAD_OK % (1, 10, 1, 'ab' * 32), GETDIR_EMPTY,
                 PAD_OK % (5, 2054, 2, 'ef' * 32)]
        return (_write_fake_run(tmp, 'A', probe_lines=lines, bound='flush_unproven'),
                _write_fake_run(tmp, 'B'))

    def bad_ord(tmp):
        lines = [PAD_OK % (1, 10, 1, 'ab' * 32), GETDIR_EMPTY,
                 MCREAD_OK % (3, 12, 1, 'cd' * 64),
                 PAD_OK % (4, 2054, 3, 'ef' * 32)]
        return (_write_fake_run(tmp, 'A', probe_lines=lines, bound='flush_unproven'),
                _write_fake_run(tmp, 'B'))

    def malformed_line(tmp):
        lines = [PAD_OK % (1, 10, 1, 'ab' * 32), 'not a probe record',
                 MCREAD_OK % (3, 12, 1, 'cd' * 64),
                 PAD_OK % (4, 2054, 2, 'ef' * 32)]
        return (_write_fake_run(tmp, 'A', probe_lines=lines, bound='flush_unproven'),
                _write_fake_run(tmp, 'B'))

    def unproven(tmp):
        lines = [PAD_OK % (1, 10, 1, 'ab' * 32), GETDIR_EMPTY,
                 MCREAD_OK % (3, 12, 1, 'cd' * 64)]
        return (_write_fake_run(tmp, 'A', probe_lines=lines, bound='target'),
                _write_fake_run(tmp, 'B'))

    def capped(tmp):
        lane_a = _write_fake_run(tmp, 'A')
        with open(lane_a / 'probe.log', 'ab') as f:
            f.write(b'cap seq=5 vsync=2055 bytes=100 msg=byte-cap-reached\n')
        return (lane_a, _write_fake_run(tmp, 'B'))

    all_ok = True
    all_ok &= check('identical_pair', 'PASS', 'identical_to_tick_2053', lanes=base)
    all_ok &= check('post2053_hash_ignored', 'PASS', 'identical_to_tick_2053',
                    lanes=extra_hashes_ignored)
    all_ok &= check('high_vsync_only', 'PASS', 'identical_to_tick_2053', lanes=high_vsync_only)
    all_ok &= check('hash_field_diff', 'FAIL', 'hash_difference',
                    extra={'first_hash_tick': 777, 'first_probe_seq': None}, lanes=hash_diff)
    all_ok &= check('probe_payload_diff', 'FAIL', 'probe_difference',
                    extra={'first_hash_tick': None, 'first_probe_seq': 3}, lanes=probe_diff)
    all_ok &= check('both_differ', 'FAIL', 'hash_and_probe_difference',
                    extra={'first_hash_tick': 777, 'first_probe_seq': 3}, lanes=both_diff)
    all_ok &= check('short_trace', 'OTHER', 'incomplete_trace', lanes=truncated_trace)
    all_ok &= check('missing_probe', 'OTHER', 'probe_missing_A', lanes=no_probe)
    all_ok &= check('truncated_probe', 'OTHER', 'probe_truncated_A', lanes=truncated_probe)
    all_ok &= check('seq_gap', 'OTHER', 'probe_framing_A', lanes=seq_gap)
    all_ok &= check('bad_ord', 'OTHER', 'probe_framing_A', lanes=bad_ord)
    all_ok &= check('malformed_line', 'OTHER', 'probe_framing_A', lanes=malformed_line)
    all_ok &= check('unproven', 'OTHER', 'probe_unproven_A', lanes=unproven)
    all_ok &= check('cap_marker', 'OTHER', 'probe_cap_A', lanes=capped)
    for name, ok, verdict, reason in cases:
        print('%s %s verdict=%s reason=%s' % ('ok' if ok else 'MISMATCH', name, verdict, reason))
    return 0 if all_ok else 1


HID_HEADER = ('Services:\nVendorID ProductID LocationID UsagePage Usage '
              'RegistryID Transport Class Product UserClass Built-In')
HID_SMC_ROW = ('0x0  0x0  0x54503962  65280  5  0x100000c3a  (null)  '
               'AppleSMCKeysEndpoint  PMU tdie9  (null)  1')
HID_ANS_ROW = ('0x0  0x0  0x544e306e  65280  5  0x100000cb2  (null)  '
               'AppleANS3CGv2Controller  NAND CH0 temp  (null)  1')
HID_PAD_ROW = ('0x57e  0x2a0  0x12345678  1  5  0x100000d00  USB  '
               'IOUSBHostHIDDevice  Wireless Gamepad  Gamepad  0')
HID_USAGE_ROW = ('0x1234  0x5678  0x1234567a  1  4  0x100000d02  USB  '
                 'IOUSBHostHIDDevice  Vendor Input Stick  (null)  0')
HID_AMB_ROW = ('0x45e  0x28e  0x12345679  65280  3  0x100000d01  USB  '
               'IOUSBHostHIDDevice  Xbox 360 Controller  (null)  0')
HID_INTERNAL_ONLY = '\n'.join([HID_HEADER, HID_SMC_ROW, HID_ANS_ROW]) + '\n'


def self_check_hid():
    """Synthetic controls: internal ANS3 vs real gamepad vs ambiguous."""
    cases = []

    def record(name, ok, detail=''):
        cases.append(ok)
        print('%s %s %s' % ('ok' if ok else 'MISMATCH', name, detail))

    internal = classify_hid(HID_INTERNAL_ONLY)
    record('hid_internal_clean',
           not internal['flag'] and len(internal['known_internal']) == 1,
           'flag=%r known=%d' % (internal['flag'], len(internal['known_internal'])))
    gamepad = classify_hid(HID_INTERNAL_ONLY + HID_PAD_ROW + '\n')
    record('hid_real_gamepad_flagged',
           gamepad['flag'] and gamepad['flagged'][0][0] == 'game_name',
           str([k for k, _ in gamepad['flagged']]))
    usage = classify_hid(HID_INTERNAL_ONLY + HID_USAGE_ROW + '\n')
    record('hid_game_usage_flagged',
           usage['flag'] and usage['flagged'][0][0] == 'game_usage',
           str([k for k, _ in usage['flagged']]))
    ambig = classify_hid(HID_INTERNAL_ONLY + HID_AMB_ROW + '\n')
    record('hid_ambiguous_flagged',
           ambig['flag'] and ambig['flagged'][0][0] == 'ambiguous_controller',
           str([k for k, _ in ambig['flagged']]))

    def hid_pair(tmp, hid_text):
        return (_write_fake_run(tmp, 'A', gamepad=True),
                _write_fake_run(tmp, 'B', gamepad=True), hid_text)

    with tempfile.TemporaryDirectory(prefix='e55d4-hid-self-') as tmp:
        lane_a, lane_b, text = hid_pair(tmp, HID_INTERNAL_ONLY)
        got = compare(lane_a, lane_b, hid_text=text)
        record('hid_internal_end_to_end_pass', got['verdict'] == 'PASS', got['reason'])
    with tempfile.TemporaryDirectory(prefix='e55d4-hid-self-') as tmp:
        lane_a, lane_b, text = hid_pair(tmp, HID_INTERNAL_ONLY + HID_PAD_ROW + '\n')
        got = compare(lane_a, lane_b, hid_text=text)
        record('hid_gamepad_end_to_end_other',
               got['verdict'] == 'OTHER' and got['reason'] == 'live_pad_present',
               got['reason'])
    with tempfile.TemporaryDirectory(prefix='e55d4-hid-self-') as tmp:
        lane_a = _write_fake_run(tmp, 'A', gamepad=True)
        lane_b = _write_fake_run(tmp, 'B', gamepad=True)
        got = compare(lane_a, lane_b)
        record('hid_legacy_flag_other',
               got['verdict'] == 'OTHER' and got['reason'] == 'live_pad_present',
               got['reason'])
    return 0 if all(cases) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('run_a', nargs='?')
    ap.add_argument('run_b', nargs='?')
    ap.add_argument('--json-out', default=None)
    ap.add_argument('--hidutil-list', default=None,
                    help='full `hidutil list` text adjudicating the live-pad gate')
    ap.add_argument('--self-check', action='store_true')
    args = ap.parse_args()
    if args.self_check:
        rc = self_check()
        return rc or self_check_hid()
    if not args.run_a or not args.run_b:
        ap.error('need two run dirs (or --self-check)')
    hid_text = Path(args.hidutil_list).read_text(errors='replace') \
        if args.hidutil_list else None
    out = compare(args.run_a, args.run_b, hid_text=hid_text)
    text = json.dumps(out, indent=2) + '\n'
    if args.json_out:
        Path(args.json_out).write_text(text)
    print(text, end='')
    return 0 if out['verdict'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
