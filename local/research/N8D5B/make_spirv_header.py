#!/usr/bin/env python3
"""Pack the N8D5B shader into a small C++ word array for the local candidate."""
import struct
from pathlib import Path

root = Path(__file__).resolve().parents[4] / 'ssx3-work/N8D5B/parallel-gs/gs/shaders'
binary = (root / 'n8d5_tile.spv').read_bytes()
assert len(binary) % 4 == 0
words = struct.unpack('<' + 'I' * (len(binary) // 4), binary)
lines = ['#pragma once', '#include <cstdint>', 'static const uint32_t n8d5_tile_spirv[] = {']
for i in range(0, len(words), 8):
    lines.append('    ' + ', '.join(f'0x{word:08x}u' for word in words[i:i + 8]) + ',')
lines += ['};', '']
(root.parent / 'n8d5_tile_spirv.hpp').write_text('\n'.join(lines))
