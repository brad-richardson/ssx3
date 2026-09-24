#!/usr/bin/env python3
"""N8D7I parser self-check.

Exercises the launcher's ``tile_vector`` parser against the saved N8D6C
same-PID log (896-word ``[n8d5b]`` vectors), a synthetic 448-word ``[n8d7f]``
vector with a comma-led logcat continuation, malformed/incomplete inputs, the
Android ``packed_sha256=unavailable`` case, and unequal input/circuit/stage
vectors. It also checks that the released N8D6C parser rejects the comma-led
continuation (the bug this brief fixes) and that ``classify`` refuses a
summary-only receipt while still accepting divergence categories B and C.

Writes a PASS/FAIL table to ``parser-selfcheck.txt`` next to this file.
No device, build, network or source change is made.
"""

import hashlib
import importlib.util
from pathlib import Path
import struct

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
N8D6C_LAUNCH = REPO / 'local/research/N8D6C/launch.py'
SAVED_LOG = Path('/Users/brad/dev/ssx3-work/N8D6C/logcat-pid.txt')
PREFIX = '         1790000000.000 17446 17467 I ps2x    : '
CHECKS = []


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'cannot load {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


launch = load('n8d7i_launch', HERE / 'launch.py')
released = load('n8d6c_launch', N8D6C_LAUNCH)


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


# ---- saved N8D6C same-PID log (896-word vectors) --------------------------
saved_text = SAVED_LOG.read_text(errors='replace') if SAVED_LOG.exists() else ''
saved = saved_text.splitlines()
saved_sampled = launch.tile_vector(saved, 'sampled', 896, '<896I')
saved_raw = launch.tile_vector(saved, 'raw', 896, '<896I')

check('saved 896 sampled words', saved_sampled and saved_sampled['words'], 896)
check('saved 896 sampled occupied', saved_sampled and saved_sampled['occupied'], 5894)
check('saved 896 sampled active', saved_sampled and saved_sampled['active'], 39)
check('saved 896 sampled sha',
      saved_sampled and saved_sampled['sha256'],
      '3f06a58ad6805c695a01c305fe06b52cc0d92198a6fb699aeee0c4ea09681ba5')
check('saved 896 raw equals sampled',
      bool(saved_sampled and saved_raw and saved_sampled['values'] == saved_raw['values']), True)

# Released parser must still reject the same comma-led continuation.
check('released N8D6C parser rejects comma-led 896 (bug reproduced)',
      released.tile_vector(saved, 'sampled'), None)

# ---- synthetic 448-word [n8d7f] wrapping ----------------------------------
vals448 = [64] * 20 + [0] * 428
occ448 = sum(vals448)
act448 = sum(value >= 32 for value in vals448)
sha448 = digest(vals448)
head = ','.join(map(str, vals448[:200]))
tail = ','.join(map(str, vals448[200:]))

comma_led = [L('[n8d7f] input_tile_counts=' + head), L(',' + tail)]
comma_led_back = launch.tile_vector(comma_led, 'input', 448, '<448H')
check('synthetic 448 comma-led words', comma_led_back and comma_led_back['words'], 448)
check('synthetic 448 comma-led occupied', comma_led_back and comma_led_back['occupied'], occ448)
check('synthetic 448 comma-led active', comma_led_back and comma_led_back['active'], act448)
check('synthetic 448 comma-led sha', comma_led_back and comma_led_back['sha256'], sha448)

trailing = [L('[n8d7f] input_tile_counts=' + head + ','), L(tail)]
check('synthetic 448 trailing-comma split sha',
      launch.tile_vector(trailing, 'input', 448, '<448H'), comma_led_back)

three = [L('[n8d7f] input_tile_counts=' + ','.join(map(str, vals448[:150]))),
         L(',' + ','.join(map(str, vals448[150:300]))),
         L(',' + ','.join(map(str, vals448[300:])))]
check('synthetic 448 three-segment split sha',
      launch.tile_vector(three, 'input', 448, '<448H'), comma_led_back)

# ---- malformed / incomplete -------------------------------------------------
long_vals = list(vals448) + [7]
check('oversized 449 rejected',
      launch.tile_vector([L('[n8d7f] input_tile_counts=' + ','.join(map(str, long_vals)))],
                         'input', 448, '<448H'), None)

malformed = [L('[n8d7f] input_tile_counts=' + ','.join(map(str, vals448[:10]))),
             L(',x,' + ','.join(map(str, vals448[11:])))]
check('non-decimal field rejected',
      launch.tile_vector(malformed, 'input', 448, '<448H'), None)

incomplete = [L('[n8d7f] input_tile_counts=' + ','.join(map(str, vals448[:200]))),
              L('[n8d7f] circuit tiles=448 occupied=0 active=0 packed_sha256=unavailable')]
check('incomplete (summary next) rejected',
      launch.tile_vector(incomplete, 'input', 448, '<448H'), None)

summary_only = [L(f'[n8d7f] input tiles=448 occupied={occ448} active={act448} '
                  f'packed_sha256={sha448}')]
check('summary without vector rejected',
      launch.tile_vector(summary_only, 'input', 448, '<448H'), None)

# ---- full synthetic probe + classify --------------------------------------
# Keep the saved log intact: its wrapped 896-word continuations carry no
# '[n8d5b]' marker, so any line filter would drop them.
N8D5B_6A = saved
FRAME = (0, 2050, 512, 448, 112, 112, 0)
METADATA = ('[n8d7f] tick=2050 fbp=112 fbw=8 psm=1 dbx=0 dby=0 phase=0 stride=2 '
            'mask=4194303 samples=1 promoted=0 extent=512x224 valid=512x224 status=2')


def build_selected(vin, vci, vst, sha_mode='hex', override_equal=None):
    def summary(kind, values):
        psha = digest(values) if sha_mode == 'hex' else 'unavailable'
        return (f'[n8d7f] {kind} tiles=448 occupied={sum(values)} '
                f'active={sum(v >= 32 for v in values)} packed_sha256={psha}')

    ic = equal_count(vin, vci)
    cs = equal_count(vci, vst)
    if override_equal is not None:
        ic, cs = override_equal
    byte_sha = 'a' * 64 if sha_mode == 'hex' else 'unavailable'
    bytes_line = (f'[n8d7f] bytes=5177344 vram_sha256={byte_sha} '
                  f'input_sha256={byte_sha} circuit_sha256={byte_sha}')
    return [
        L(METADATA), L(bytes_line),
        L(summary('input', vin)), L('[n8d7f] input_tile_counts=' + ','.join(map(str, vin))),
        L(summary('circuit', vci)), L('[n8d7f] circuit_tile_counts=' + ','.join(map(str, vci))),
        L(summary('stage', vst)), L('[n8d7f] stage_tile_counts=' + ','.join(map(str, vst))),
        L(f'[n8d7f] input_circuit_equal={ic}/448 circuit_stage_equal={cs}/448'),
    ]


def classify_selected(selected_lines):
    return launch.classify(launch.probe(N8D5B_6A + selected_lines), FRAME)


low = [64] * 20 + [0] * 428          # active 20
high = [64] * 300 + [0] * 148        # active 300

# Mac-style hex digest, all three equal and sparse -> A.
check('hex-sha equal vectors classify A',
      classify_selected(build_selected(low, low, low)), 'A')
# Android logs packed_sha256=unavailable and bytes unavailable -> still A.
android_a = build_selected(low, low, low, sha_mode='unavailable')
check('unavailable-sha equal vectors classify A', classify_selected(android_a), 'A')
probe_a = launch.probe(N8D5B_6A + android_a)
check('unavailable bytes accepted',
      bool(probe_a['selected']['bytes'] and all(
          value == 'unavailable' for value in probe_a['selected']['bytes'][1:])), True)

# Divergence: loss by circuit -> input high, circuit/stage low -> B.
b_lines = build_selected(high, low, low)
check('unequal vectors loss-by-circuit classify B', classify_selected(b_lines), 'B')
check('B equality recomputed (168/448)',
      launch.probe(N8D5B_6A + b_lines)['selected']['equal'], ('168', '448'))

# Divergence: loss by GPU stage -> input/circuit high, stage low -> C.
c_lines = build_selected(high, high, low)
check('unequal vectors loss-by-stage classify C', classify_selected(c_lines), 'C')
check('C equality recomputed (448/168)',
      launch.probe(N8D5B_6A + c_lines)['selected']['equal'], ('448', '168'))

# Logged equality that disagrees with the parsed vectors -> OTHER.
check('mismatched logged equality classify OTHER',
      classify_selected(build_selected(high, low, low, override_equal=(448, 448))), 'OTHER')

# Summary-only (input vector removed) -> OTHER; corrupt vector -> OTHER.
no_input = [line for line in android_a if 'input_tile_counts=' not in line]
check('summary-only receipt classify OTHER', classify_selected(no_input), 'OTHER')
corrupt = [line.replace('[n8d7f] stage_tile_counts=', '[n8d7f] stage_tile_counts=x')
           if 'stage_tile_counts=' in line else line for line in android_a]
check('corrupt stage vector classify OTHER', classify_selected(corrupt), 'OTHER')

# ---- report -----------------------------------------------------------------
lines = ['N8D7I parser self-check', 'saved log: ' + str(SAVED_LOG),
         'launcher:  ' + str(HERE / 'launch.py'), '']
width = max(len(name) for name, *_ in CHECKS)
for name, ok, got, want in CHECKS:
    lines.append(f'{"PASS" if ok else "FAIL"}  {name:<{width}}  got={got}  want={want}')
passed = sum(1 for _, ok, *_ in CHECKS if ok)
lines += ['', f'{passed}/{len(CHECKS)} checks passed']
report = '\n'.join(lines) + '\n'
(HERE / 'parser-selfcheck.txt').write_text(report)
print(report)
raise SystemExit(0 if passed == len(CHECKS) else 1)
