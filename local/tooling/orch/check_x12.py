#!/usr/bin/env python3
"""Check X12's exact source-line extraction against its pinned worktree."""
import csv
import pathlib
import subprocess
import sys

root = pathlib.Path('/Users/brad/dev/ssx3-work/N8B1/PS2Recomp')
expected_rev = '17e90ded3689685ad359b76a9168c80a1f752e2d'
actual_rev = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
if actual_rev != expected_rev:
    raise SystemExit(f'wrong pin: {actual_rev}')

spec = {
    'shot_width': ('ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp', 'shot.image->get_width()'),
    'buffer_bytes': ('ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp', 'info.size ='),
    'copy_extent': ('ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp', 'cmd->copy_image_to_buffer('),
    'host_map': ('ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp', 'm_device->map_host_buffer('),
    'backend_stride': ('ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp', 'kStride = 640u'),
    'frontend_stride': ('ps2xRuntime/src/lib/gs/gs_frontend.cpp', 'sourceRowBytes ='),
    'texture_upload': ('ps2xRuntime/src/lib/ps2_runtime.cpp', 'UpdateTexture(tex, s_uploadBuffer.data())'),
}
with open(sys.argv[1], newline='', encoding='utf-8') as fp:
    reader = csv.DictReader(fp, delimiter='\t')
    if reader.fieldnames != ['id', 'file', 'line', 'source']:
        raise SystemExit(f'bad columns: {reader.fieldnames}')
    rows = list(reader)
if len(rows) != len(spec) or {r['id'] for r in rows} != set(spec):
    raise SystemExit('missing, duplicate, or extra IDs')
for row in rows:
    rel, token = spec[row['id']]
    if row['file'] != rel:
        raise SystemExit(f"{row['id']}: wrong file")
    lines = (root / rel).read_text().splitlines()
    try:
        actual = lines[int(row['line']) - 1].strip()
    except (ValueError, IndexError):
        raise SystemExit(f"{row['id']}: bad line")
    if token not in actual or row['source'] != actual:
        raise SystemExit(f"{row['id']}: source mismatch")
print('X12 exact-line gate: 7/7, pinned source')
