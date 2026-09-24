#!/usr/bin/env bash
# N9 Part 2 wrapper pin verify (read-only): double-read the external pinned
# wrapper files and confirm they equal the standing pins. The staged fork
# tracks no gradlew script/jar (as in P6M6R), so the P3-root wrapper is
# invoked as a build tool from the new-root android cwd. Adapted from
# N8D7M12P6M6R/wrapper_pins.sh (new root n9).
# Expected:
#   gradlew            a3648413b47ef77af21d5ebc36c687c7d103aaef3e17f33de7d4f080a6f300a3
#   gradle-wrapper.jar 498495120a03b9a6ab5d155f5de3c8f0d986a449153702fb80fc80e134484f17
#   wrapper properties 3d91f0932da99885c41e9dc4e85c9f9a2d3bfef4f0ad87473014dc0827a94884
set -euo pipefail
ext=/home/brad/n8d7m12p3/PS2Recomp/android
new=/home/brad/n9/PS2Recomp/android
echo "== double reads =="
sha256sum "$ext/gradlew" "$ext/gradlew"
sha256sum "$ext/gradle/wrapper/gradle-wrapper.jar" "$ext/gradle/wrapper/gradle-wrapper.jar"
sha256sum "$ext/gradle/wrapper/gradle-wrapper.properties" "$new/gradle/wrapper/gradle-wrapper.properties"
echo "== props diff (expect empty) =="
diff "$ext/gradle/wrapper/gradle-wrapper.properties" "$new/gradle/wrapper/gradle-wrapper.properties" && echo WRAPPER_PROPS_EQUAL
echo "== new root still has no wrapper script/jar (expect both absent) =="
test ! -e "$new/gradlew" && echo "new gradlew absent OK"
test ! -e "$new/gradle/wrapper/gradle-wrapper.jar" && echo "new wrapper jar absent OK"
echo "== heavy jobs recheck =="
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
df -BG /home | tail -1
