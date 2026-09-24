#!/usr/bin/env bash
# N8D7M12P6M6R preflight: fresh root absent, toolchain/governor, disk, heavy jobs.
# Read-only except stdout.
set -euo pipefail
test ! -e /home/brad/n8d7m12p6m6 && echo "n8d7m12p6m6 absent OK"
echo "== toolchain/governor =="
test -d /home/brad/n2/toolchain/jdk-17 && echo "jdk-17 present OK"
test -d /home/brad/n2/toolchain/android-sdk && echo "android-sdk present OK"
test -d /home/brad/n2/toolchain/android-sdk/ndk/28.2.13676358 && echo "ndk present OK"
test -d /home/brad/n2/gradle-home && echo "gradle-home present OK"
test -f /home/brad/n8b1/mem_governor.sh && echo "governor present OK"
echo "== disk =="
df -h /home | tail -1
df -BG /home | tail -1
echo "== heavy jobs =="
python3 - <<'PY'
from pathlib import Path
terms = ('gradle', 'ninja', 'clang', 'pcsx2')
active = []
for p in Path('/proc').iterdir():
    if not p.name.isdigit():
        continue
    try:
        comm = (p/'comm').read_text().strip().lower()
        cmd = (p/'cmdline').read_bytes().replace(b'\0', b' ').decode(errors='replace')
    except (OSError, PermissionError):
        continue
    if any(term in comm for term in terms):
        active.append((p.name, comm, cmd[:180]))
print('HEAVY_JOBS', active)
PY
