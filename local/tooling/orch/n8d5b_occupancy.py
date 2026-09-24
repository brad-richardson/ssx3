#!/usr/bin/env python3
"""Pinned N8D4 image occupancy baseline for a bounded GPU tile probe."""
import hashlib
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[2] / 'research/N8D4'
images = {
    'mac_parallel': ('mac-parallel-2050.png', '1dc0be5c378374b709aadec6cd54c12e39d9204c43941446829ccea012fbd8ea'),
    'odin_raw': ('odin-raw-2050.png', '873943f028eb42beda2b22119706188c10e6754dbc05fe22486dfddd8a259a46'),
}
results = {}
for label, (filename, expected_sha) in images.items():
    path = root / filename
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected_sha, filename
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(path), '-f', 'rawvideo', '-pix_fmt', 'rgba', '-'])
    width, height, tile = 512, 448, 16
    assert len(raw) == width * height * 4, filename
    counts = []
    for ty in range(0, height, tile):
        for tx in range(0, width, tile):
            count = 0
            for y in range(ty, ty + tile):
                for x in range(tx, tx + tile):
                    pos = 4 * (y * width + x)
                    count += max(raw[pos:pos + 3]) >= 32
            counts.append(count)
    results[label] = {'sha256': expected_sha, 'nonblack_pixels': sum(counts),
                      'active_tiles_at_least_32_pixels': sum(count >= 32 for count in counts),
                      'total_tiles': len(counts)}
assert results['mac_parallel']['active_tiles_at_least_32_pixels'] >= 500
assert results['odin_raw']['active_tiles_at_least_32_pixels'] <= 100
print(json.dumps({'tile_size': 16, 'channel_threshold': 32, 'active_pixel_threshold_per_tile': 32,
                  'results': results}, indent=2))
