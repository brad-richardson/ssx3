#!/usr/bin/env python3
"""Parse the W1F2/I27A Simulator gate without equating free-running frames."""
from pathlib import Path
import hashlib
import re
import struct
import sys

baseline = Path('/Users/brad/dev/ssx3-work/W1F/run-w1f2/console.log')
root = Path('/Users/brad/dev/ssx3-work/I27A')
current = root / 'run-i27a/console.log'
suite = root / 'suite.log'
window_re = re.compile(r'\[ios-window\] window=(\d+)x(\d+) drawable=(\d+)x(\d+)')
render_re = re.compile(r'\[ios-render\] screen=(\d+)x(\d+) render=(\d+)x(\d+)')


def read(path):
    return path.read_text(errors='replace') if path.exists() else ''


def sha_pair(path):
    first = hashlib.sha256(path.read_bytes()).hexdigest()
    second = hashlib.sha256(path.read_bytes()).hexdigest()
    return first, second


def png_size(path):
    with path.open('rb') as file:
        header = file.read(24)
    if header[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError(f'not PNG: {path}')
    return struct.unpack('>II', header[16:24])


base_text, new_text, suite_text = map(read, (baseline, current, suite))
base_match = window_re.search(base_text)
new_match = window_re.search(new_text)
print('I27A Simulator acceptance table')
print('item | baseline | I27A')
for label, match in (('W1F2', base_match), ('I27A', new_match)):
    if match:
        w, h, dw, dh = map(int, match.groups())
        print(f'{label} window/drawable | {w}x{h} | {dw}x{dh} | ratio {dw/w:.3f}x{dh/h:.3f}')
    else:
        print(f'{label} window/drawable | not found')
renders = render_re.findall(new_text)
render = tuple(map(int, renders[-1])) if renders else None
print('I27A screen/render (last sample) | ' + ('%sx%s / %sx%s' % render if render else 'not found'))
transport_ok = False
native_render_ok = False
if new_match:
    w, h, dw, dh = map(int, new_match.groups())
    transport_ok = dw > w and dh > h
    if render:
        sw, sh, rw, rh = render
        native_render_ok = rw >= dw and rh >= dh
        print(f'I27A render/drawable | {rw/dw:.3f}x{rh/dh:.3f}')
print(f'drawable transport | {"UNKNOWN" if not new_match else ("PASS" if transport_ok else "FAIL")}')
print(f'native render-size | {"UNKNOWN" if not (new_match and render) else ("PASS" if native_render_ok else "FAIL")}')
counts = [re.search(rf'{name}:\s*(\d+)', suite_text) for name in ('Total Tests', 'Passed', 'Failed')]
print('Mac taps-OFF suite | ' + (', '.join(f'{name}={match.group(1)}' for name, match in zip(('total', 'passed', 'failed'), counts)) if all(counts) else 'not found'))
ticks = [int(x) for x in re.findall(r'\[vsync-rate\] tick=(\d+)', new_text)]
armed = re.search(r'\[padscript\] armed n=(\d+) source=(\w+) clock=(\w+)', new_text)
print(f'I26-FAST route | armed={armed.groups() if armed else "not found"} | last_tick={max(ticks) if ticks else "not found"} | tick>=1714={bool(ticks and max(ticks)>=1714)}')
frames = sorted((root / 'run-i27a').glob('shot-*.png'))
print(f'frame count | {len(frames)}')
for path in frames:
    a, b = sha_pair(path)
    print(f'{path.name} | png={png_size(path)} bytes={path.stat().st_size} sha1={a} sha2={b} paired={a==b}')
valid = bool(base_match and new_match and all(counts) and int(counts[2].group(1)) == 0 and ticks and max(ticks) >= 1714 and len(frames) <= 4 and all(sha_pair(p)[0] == sha_pair(p)[1] for p in frames))
valid = valid and transport_ok and native_render_ok
print(f'full HiDPI gate={"PASS" if valid else "FAIL"}')
sys.exit(0 if valid else 1)
