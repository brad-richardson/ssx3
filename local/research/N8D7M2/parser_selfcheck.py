#!/usr/bin/env python3
"""N8D7M2 parser self-check.

Exercises the launcher's ``tile_vector``, ``parse_controls`` and ``classify``
against the saved N8D7L Mac receipt (the full 448-word ``[n8d7f]
oracle_tile_counts`` vector, its ``[n8d7l] oracle_controls`` and
``oracle_input_equal``), a synthetic comma-led 448-word continuation, malformed
inputs, and synthetic A/B/C/D/OTHER receipts built on the saved N8D6C same-PID
``[n8d5b]``/``[n8d6a]`` lines.

Writes a PASS/FAIL table to ``parser-selfcheck.txt`` next to this file. No
device, build, network or source change is made.
"""

import hashlib
import importlib.util
from pathlib import Path
import struct

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
EXCERPT = REPO / 'local/research/N8D7L/replay-excerpt.txt'
SAVED_N8D6C = Path('/Users/brad/dev/ssx3-work/N8D6C/logcat-pid.txt')
PREFIX = '         1790000000.000 17446 17467 I ps2x    : '
CHECKS = []


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'cannot load {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


launch = load('n8d7m2_launch', HERE / 'launch.py')


def brief(value):
    if isinstance(value, dict) and 'values' in value:
        return (f"{{words={value['words']} occupied={value['occupied']} "
                f"active={value['active']} sha256={value['sha256'][:16]}..}}")
    return repr(value)


def check(name, got, want):
    ok = got == want
    CHECKS.append((name, ok, brief(got), brief(want)))
    return ok


def L(payload):
    return PREFIX + payload


def pack16(values):
    return struct.pack(f'<{len(values)}H', *values)


def digest(values):
    return hashlib.sha256(pack16(values)).hexdigest()


def equal_count(left, right):
    return sum(a == b for a, b in zip(left, right))


CONTROLS_LITERAL = ('0x0E0000=0x00260803,0x0E0534=0x00260802,0x0E0040=0x00260804,'
                    '0x1BFFF4=0x000C0000,0x0E2000=0x00260802,0x0F0000=0xFF230401,'
                    '0x0E1FFC=0x003D2B00,0x0F2000=0x00604400')


# ---- N8D7L saved Mac receipt (full oracle vector + controls) ----------------
excerpt = EXCERPT.read_text(errors='replace').splitlines() if EXCERPT.exists() else []
mac_oracle = launch.tile_vector(excerpt, 'oracle', 448, '<448H')
mac_input = launch.tile_vector(excerpt, 'input', 448, '<448H')
mac_circuit = launch.tile_vector(excerpt, 'circuit', 448, '<448H')
mac_stage = launch.tile_vector(excerpt, 'stage', 448, '<448H')
mac_controls_line = next((line for line in excerpt if 'oracle_controls=' in line), None)
mac_controls = launch.parse_controls(
    mac_controls_line.split('oracle_controls=', 1)[1] if mac_controls_line else None)
mac_equal_line = next((line for line in excerpt if 'oracle_input_equal=' in line), None)

check('saved oracle 448 words', mac_oracle and mac_oracle['words'], 448)
check('saved oracle occupied', mac_oracle and mac_oracle['occupied'], 64374)
check('saved oracle active', mac_oracle and mac_oracle['active'], 300)
check('saved oracle packed sha',
      mac_oracle and mac_oracle['sha256'],
      'e1dc4c5c6b7579e4c036e9df8cde0dfe8096e9bbe3fe56c8494a50720c78a593')
check('saved input/circuit/stage/oracle all equal',
      bool(mac_input and mac_circuit and mac_stage and mac_oracle
           and mac_input['values'] == mac_circuit['values'] == mac_stage['values']
           == mac_oracle['values']), True)
check('saved controls 8 literal pairs', mac_controls,
      [(addr, launch.MAC_CONTROLS[addr]) for addr in launch.CONTROL_ADDRS])
check('saved control addresses match pin',
      bool(mac_controls and [a for a, _ in mac_controls] == list(launch.CONTROL_ADDRS)), True)
check('saved oracle_input_equal logged 448/448',
      mac_equal_line.split('oracle_input_equal=', 1)[1] if mac_equal_line else None, '448/448')
check('saved oracle/input recomputed equality',
      bool(mac_oracle and mac_input
           and equal_count(mac_oracle['values'], mac_input['values']) == 448), True)

# ---- synthetic comma-led 448-word [n8d7f] oracle continuation ---------------
vals448 = [64] * 20 + [0] * 428
occ448 = sum(vals448)
act448 = sum(value >= 32 for value in vals448)
sha448 = digest(vals448)
head = ','.join(map(str, vals448[:200]))
tail = ','.join(map(str, vals448[200:]))

comma_led = [L('[n8d7f] oracle_tile_counts=' + head), L(',' + tail)]
comma_led_back = launch.tile_vector(comma_led, 'oracle', 448, '<448H')
check('synthetic oracle comma-led words', comma_led_back and comma_led_back['words'], 448)
check('synthetic oracle comma-led occupied', comma_led_back and comma_led_back['occupied'], occ448)
check('synthetic oracle comma-led active', comma_led_back and comma_led_back['active'], act448)
check('synthetic oracle comma-led sha', comma_led_back and comma_led_back['sha256'], sha448)

trailing = [L('[n8d7f] oracle_tile_counts=' + head + ','), L(tail)]
check('synthetic oracle trailing-comma split sha',
      launch.tile_vector(trailing, 'oracle', 448, '<448H'), comma_led_back)

three = [L('[n8d7f] oracle_tile_counts=' + ','.join(map(str, vals448[:150]))),
         L(',' + ','.join(map(str, vals448[150:300]))),
         L(',' + ','.join(map(str, vals448[300:])))]
check('synthetic oracle three-segment split sha',
      launch.tile_vector(three, 'oracle', 448, '<448H'), comma_led_back)

# ---- malformed / incomplete vector and control inputs ----------------------
long_vals = list(vals448) + [7]
check('oversized 449 oracle rejected',
      launch.tile_vector([L('[n8d7f] oracle_tile_counts=' + ','.join(map(str, long_vals)))],
                         'oracle', 448, '<448H'), None)
malformed = [L('[n8d7f] oracle_tile_counts=' + ','.join(map(str, vals448[:10]))),
             L(',x,' + ','.join(map(str, vals448[11:])))]
check('non-decimal oracle field rejected',
      launch.tile_vector(malformed, 'oracle', 448, '<448H'), None)
incomplete = [L('[n8d7f] oracle_tile_counts=' + ','.join(map(str, vals448[:200]))),
              L('[n8d7l] oracle_input_equal=448/448')]
check('incomplete oracle (next tag) rejected',
      launch.tile_vector(incomplete, 'oracle', 448, '<448H'), None)
check('summary without oracle vector rejected',
      launch.tile_vector([L('[n8d7f] oracle tiles=448 occupied=0 active=0 '
                            'packed_sha256=unavailable')], 'oracle', 448, '<448H'), None)
check('control payload with 7 words rejected',
      launch.parse_controls(','.join(CONTROLS_LITERAL.split(',')[:7])), None)
check('control payload with bad field rejected',
      launch.parse_controls(CONTROLS_LITERAL.replace('0x1BFFF4=0x000C0000', '0x1BFFF4')),
      None)

# ---- synthetic full receipts + classify ------------------------------------
SAVED_896 = SAVED_N8D6C.read_text(errors='replace').splitlines() if SAVED_N8D6C.exists() else []
FRAME = (0, 2050, 512, 448, 112, 112, 0)
METADATA = ('[n8d7f] tick=2050 fbp=112 fbw=8 psm=1 dbx=0 dby=0 phase=0 stride=2 '
            'mask=4194303 samples=1 promoted=0 extent=512x224 valid=512x224 status=2')
ORACLE_METADATA = ('[n8d7l] tick=2050 fbp=112 fbw=8 psm=1 dbx=0 dby=0 phase=0 stride=2 '
                   'mask=4194303 samples=1 promoted=0')


def build_receipt(vin, vci, vst, vor, sha_mode='hex', override_equal=None,
                  override_oracle_equal=None, controls_payload=None,
                  include_oracle=True, metadata=None, oracle_metadata=None):
    def summary(kind, values):
        psha = digest(values) if sha_mode == 'hex' else 'unavailable'
        return (f'[n8d7f] {kind} tiles=448 occupied={sum(values)} '
                f'active={sum(v >= 32 for v in values)} packed_sha256={psha}')

    ic = equal_count(vin, vci)
    cs = equal_count(vci, vst)
    if override_equal is not None:
        ic, cs = override_equal
    oe = equal_count(vor, vin)
    if override_oracle_equal is not None:
        oe = override_oracle_equal
    byte_sha = 'a' * 64 if sha_mode == 'hex' else 'unavailable'
    lines = [L(metadata or METADATA),
             L(f'[n8d7f] bytes=5177344 vram_sha256={byte_sha} input_sha256={byte_sha} '
               f'circuit_sha256={byte_sha}'),
             L(summary('input', vin)), L('[n8d7f] input_tile_counts=' + ','.join(map(str, vin))),
             L(summary('circuit', vci)), L('[n8d7f] circuit_tile_counts=' + ','.join(map(str, vci))),
             L(summary('stage', vst)), L('[n8d7f] stage_tile_counts=' + ','.join(map(str, vst))),
             L(f'[n8d7f] input_circuit_equal={ic}/448 circuit_stage_equal={cs}/448'),
             L(summary('oracle', vor))]
    if include_oracle:
        lines.append(L('[n8d7f] oracle_tile_counts=' + ','.join(map(str, vor))))
    lines += [L(oracle_metadata or ORACLE_METADATA),
              L('[n8d7l] oracle_controls=' + (controls_payload or CONTROLS_LITERAL)),
              L(f'[n8d7l] oracle_input_equal={oe}/448')]
    return lines


def classify_receipt(extra):
    return launch.classify(launch.probe(SAVED_896 + extra), FRAME)


low = [64] * 20 + [0] * 428          # active 20
high = [64] * 300 + [0] * 148        # active 300
mac_values = mac_oracle['values'] if mac_oracle else []

check('A: oracle==input sparse active 20',
      classify_receipt(build_receipt(low, low, low, low)), 'A')
android_a = build_receipt(low, low, low, low, sha_mode='unavailable')
check('A: unavailable-sha equal vectors',
      classify_receipt(android_a), 'A')
check('B: oracle high, input low (equality 168/448)',
      classify_receipt(build_receipt(low, low, low, high)), 'B')
check('C: oracle low, input high (equality 168/448)',
      classify_receipt(build_receipt(high, high, high, low)), 'C')
check('D: oracle and input high (equality 448/448)',
      classify_receipt(build_receipt(high, high, high, high)), 'D')
check('D on saved Mac vector (equality 448/448, active 300)',
      classify_receipt(build_receipt(mac_values, mac_values, mac_values, mac_values)), 'D')
check('OTHER: logged oracle_input_equal disagrees with vectors',
      classify_receipt(build_receipt(low, low, low, high, override_oracle_equal=448)), 'OTHER')
mid = [64] * 150 + [0] * 298        # active 150
check('OTHER: 448/448 but active 150 neither sparse nor broad',
      classify_receipt(build_receipt(mid, mid, mid, mid)), 'OTHER')
swapped_words = CONTROLS_LITERAL.split(',')
swapped = ','.join([swapped_words[1], swapped_words[0], *swapped_words[2:]])
check('OTHER: control address order mismatch',
      classify_receipt(build_receipt(low, low, low, low, controls_payload=swapped)), 'OTHER')
check('OTHER: missing oracle vector',
      classify_receipt(build_receipt(low, low, low, low, include_oracle=False)), 'OTHER')
no_oracle_tags = [line for line in android_a if '[n8d7l]' not in line]
check('OTHER: missing [n8d7l] lines',
      classify_receipt(no_oracle_tags), 'OTHER')

# ---- shared selected/oracle metadata alignment ------------------------------
METADATA_ORDER = ('tick', 'fbp', 'fbw', 'psm', 'dbx', 'dby', 'phase',
                  'stride', 'mask', 'samples', 'promoted')


def meta(shared=None, status=None, valid='512x224'):
    base = {'tick': 2050, 'fbp': 112, 'fbw': 8, 'psm': 1, 'dbx': 0, 'dby': 0,
            'phase': 0, 'stride': 2, 'mask': 4194303, 'samples': 1, 'promoted': 0}
    if shared:
        base.update(shared)
    line = ' '.join(f'{key}={base[key]}' for key in METADATA_ORDER)
    if status is None:
        return '[n8d7l] ' + line
    return '[n8d7f] ' + line + f' extent={valid} valid={valid} status={status}'


check('A: shared metadata fields align', classify_receipt(build_receipt(low, low, low, low)), 'A')
check('A: shared metadata agree on non-default stride/dbx',
      classify_receipt(build_receipt(low, low, low, low,
                                     metadata=meta(status=2, shared={'stride': 4, 'dbx': 1}),
                                     oracle_metadata=meta(shared={'stride': 4, 'dbx': 1}))), 'A')
for field, sel, orc in (('stride', 4, 2), ('dbx', 1, 0), ('dby', 1, 0),
                        ('phase', 1, 0), ('fbw', 7, 8), ('psm', 2, 1),
                        ('mask', 4194302, 4194303), ('samples', 2, 1),
                        ('promoted', 1, 0)):
    check(f'OTHER: selected/oracle {field} mismatch',
          classify_receipt(build_receipt(low, low, low, low,
                                         metadata=meta(status=2, shared={field: sel}),
                                         oracle_metadata=meta(shared={field: orc}))), 'OTHER')
check('OTHER: selected/oracle tick mismatch',
      classify_receipt(build_receipt(low, low, low, low,
                                     metadata=meta(status=2, shared={'tick': 2049}),
                                     oracle_metadata=meta(shared={'tick': 2050}))), 'OTHER')
check('OTHER: selected/oracle fbp mismatch',
      classify_receipt(build_receipt(low, low, low, low,
                                     metadata=meta(status=2, shared={'fbp': 113}),
                                     oracle_metadata=meta(shared={'fbp': 112}))), 'OTHER')

# ---- report -----------------------------------------------------------------
lines = ['N8D7M2 parser self-check', 'excerpt:  ' + str(EXCERPT),
         'saved 896: ' + str(SAVED_N8D6C), 'launcher: ' + str(HERE / 'launch.py'), '']
width = max(len(name) for name, *_ in CHECKS)
for name, ok, got, want in CHECKS:
    lines.append(f'{"PASS" if ok else "FAIL"}  {name:<{width}}  got={got}  want={want}')
passed = sum(1 for _, ok, *_ in CHECKS if ok)
lines += ['', f'{passed}/{len(CHECKS)} checks passed']
report = '\n'.join(lines) + '\n'
(HERE / 'parser-selfcheck.txt').write_text(report)
print(report)
raise SystemExit(0 if passed == len(CHECKS) else 1)
