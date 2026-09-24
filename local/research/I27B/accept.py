#!/usr/bin/env python3
"""Bounded I27B Simulator gate; run from ssx3 with local Pillow on PYTHONPATH."""
from pathlib import Path
import hashlib
import re
import sys

from PIL import Image, ImageChops

root = Path('/Users/brad/dev/ssx3-work/I27B')
run = root / 'run-i27b'
console = (run / 'console.log').read_text(errors='replace')
suite = (root / 'suite.log').read_text(errors='replace')
build = (root / 'logs/sim-release-build.log').read_text(errors='replace')
cache = (root / 'ios-runtime-sim-release/CMakeCache.txt').read_text(errors='replace')
response_dir = root / 'ios-runtime-sim-release/build/ps2_game_objects.build/Release-iphonesimulator/Objects-normal/arm64'
responses = list(response_dir.glob('*-common-args.resp'))
response = responses[0].read_text(errors='replace') if len(responses) == 1 else ''
source = (root / 'raylib-src/src/platforms/rcore_desktop_sdl.c').read_text()
run_text = (run / 'run.txt').read_text(errors='replace')
cleanup = Path('/Users/brad/dev/ssx3/local/research/I27B/cleanup.txt').read_text(errors='replace')
disk = Path('/Users/brad/dev/ssx3/local/research/I27B/disk-budget.txt').read_text(errors='replace')
window = re.findall(r'\[ios-window\] window=(\d+)x(\d+) drawable=(\d+)x(\d+)', console)
render = re.findall(r'\[ios-render\] screen=(\d+)x(\d+) render=(\d+)x(\d+)', console)
ticks = [int(tick) for tick in re.findall(r'\[vsync-rate\] tick=(\d+)', console)]
armed = re.search(r'\[padscript\] armed n=(\d+) source=(\w+) clock=(\w+)', console)
frames = sorted(run.glob('shot-*.png'))

print('I27B acceptance')
print('raylib patch present:', 'SDL_GL_GetDrawableSize(platform.window, &drawableWidth, &drawableHeight);' in source)
suite_counts = {label: re.search(label + r':\s*(\d+)', suite) for label in ('Total Tests', 'Passed', 'Failed')}
print('Mac suite:', ', '.join(f'{label}={match.group(1) if match else "not found"}' for label, match in suite_counts.items()))
print('Simulator build:', 'BUILD SUCCEEDED' if '** BUILD SUCCEEDED **' in build else 'not found')
release_flags = ('CMAKE_C_FLAGS_RELEASE:STRING=-O3 -DNDEBUG' in cache and
                 'CMAKE_CXX_FLAGS_RELEASE:STRING=-O3 -DNDEBUG' in cache and
                 '-O3' in response and '-DNDEBUG' in response and '-O0' not in response)
print('verified Release flags:', release_flags)
print('Simulator staged app:', (root / 'staged-sim/ps2EntryRunner.app/ps2EntryRunner').exists())
print('window/drawable:', window[-1] if window else 'not found')
print('screen/render:', render[-1] if render else 'not found')
print('route:', f'armed={armed.groups() if armed else "not found"} last_tick={max(ticks) if ticks else "not found"}')
print('frames:', len(frames))
occupied = []
paired = []
sizes = []
for path in frames:
    first = hashlib.sha256(path.read_bytes()).hexdigest()
    second = hashlib.sha256(path.read_bytes()).hexdigest()
    with Image.open(path) as image:
        image.load()
        rgb = image.convert('RGB')
        box = ImageChops.difference(rgb, Image.new('RGB', rgb.size)).getbbox()
        occupied.append(box)
        paired.append(first == second)
        sizes.append(rgb.size)
        print(f'{path.name}: size={rgb.size} bytes={path.stat().st_size} nonblack_bbox={box} sha1={first} sha2={second} paired={first == second}')

valid = True
valid &= 'SDL_GL_GetDrawableSize(platform.window, &drawableWidth, &drawableHeight);' in source
valid &= all(re.search(label + r':\s*(\d+)', suite) for label in ('Total Tests', 'Passed', 'Failed'))
valid &= bool(re.search(r'Passed:\s*585', suite) and re.search(r'Failed:\s*0', suite))
valid &= '** BUILD SUCCEEDED **' in build
valid &= release_flags
valid &= (root / 'staged-sim/ps2EntryRunner.app/ps2EntryRunner').exists()
valid &= bool(window and render and armed and ticks and max(ticks) >= 1714)
valid &= len(frames) == 4
valid &= all(paired) and all(size == (2622, 1206) for size in sizes)
valid &= all(box is not None and box[2] > 1748 for box in occupied)
valid &= sum(path.stat().st_size for path in frames) <= 12 * 1024 * 1024
valid &= 'elapsed=160s completed_four_shots=yes' in run_text
valid &= 'cleanup slot=1 own_pid=' in run_text
valid &= 'slot 1: free' in cleanup and 'slot 2: free' in cleanup and 'own_launch_pid_alive=no' in cleanup
global_budget = re.search(r'ssx3 internal usage: ([\d.]+) GB of (\d+) GB cap', disk)
scratch_budget = re.search(r'^([\d.]+)G\s+/Users/brad/dev/ssx3-work/I27B$', disk, re.M)
valid &= bool(global_budget and float(global_budget.group(1)) < int(global_budget.group(2)))
valid &= bool(scratch_budget and float(scratch_budget.group(1)) < 8)
print('budgets:', f'global={global_budget.groups() if global_budget else "not found"} scratch_GiB={scratch_budget.group(1) if scratch_budget else "not found"}')
receipt_dir = Path('/Users/brad/dev/ssx3/local/research/I27B')
text_logs = [path for path in receipt_dir.iterdir() if path.is_file() and
             (path.suffix == '.log' or path.name.endswith(('-error.txt', 'acceptance.txt', 'config-flags.txt', 'sim-run.txt', 'clang-sample.txt')))]
log_bytes = sum(path.stat().st_size for path in text_logs)
print('text log bytes:', log_bytes)
valid &= log_bytes <= 8 * 1024 * 1024
if window and render:
    w, h, dw, dh = map(int, window[-1])
    sw, sh, rw, rh = map(int, render[-1])
    print(f'drawable/window={dw / w:.3f}x{dh / h:.3f} render/drawable={rw / dw:.3f}x{rh / dh:.3f}')
    valid &= w == sw and h == sh and rw >= dw and rh >= dh
print('bounded gate:', 'PASS' if valid else 'FAIL')
sys.exit(0 if valid else 1)
