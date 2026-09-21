#!/usr/bin/env python3
"""Read-only EF handover supplement. No captures, builds, or emulator execution."""
import hashlib
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
FORK = Path('/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp')
E6_REF = '57e1afb'


def main():
    print('# EF handover supplement: E6 landed; independent trace work stopped')
    full = subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', E6_REF]).decode().strip()
    print('E6_commit', full)
    report = subprocess.check_output(['git', '-C', str(REPO), 'show', f'{full}:local/research/E6/REPORT.md'])
    lines = report.decode().splitlines()
    print('E6_REPORT bytes', len(report), 'lines', len(lines), 'sha256', hashlib.sha256(report).hexdigest())
    print('## H1 E6 decision and complete tail')
    for lo, hi in [(312, 336), (350, 365), (406, 414)]:
        for n in range(lo, hi + 1):
            print(f'{n}: {lines[n - 1]}')

    print('\n## H2 CPU store-width descent supplement')
    path = FORK / 'ps2xRuntime/src/lib/ps2_memory.cpp'
    data = path.read_bytes()
    lines = data.decode().splitlines()
    print('SOURCE', str(path), 'sha256', hashlib.sha256(data).hexdigest())
    for n in range(967, 1083):
        print(f'{n}: {lines[n - 1]}')

    print('\n## H3 library/header references: every textual processVIF1Data and FIFO-address hit')
    for root in [FORK / 'ps2xRuntime/src/lib', FORK / 'ps2xRuntime/include']:
        hits = []
        for path in sorted(root.rglob('*')):
            if path.name.startswith('._') or path.suffix not in {'.cpp', '.h', '.hpp'}:
                continue
            for n, line in enumerate(path.read_text().splitlines(), 1):
                if 'processVIF1Data' in line or '10005000' in line.upper():
                    hits.append(f'{path.relative_to(FORK)}:{n}: {line}')
        print('\n'.join(hits))
    print('Scope: textual references supplement the write-path source audit; not a whole-program semantic proof.')
    print('\n# EF HANDOVER TAIL COMPLETE: H1-H3; zero new runtime observations')


if __name__ == '__main__':
    main()
