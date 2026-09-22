"""What E29 inherits, checked rather than asserted.

E29 spends E24's designed e24a boot on the re-baselined build. Three things it
needs are checked here, read-only, with no boot and no lease:
  1. the runner at the exact path E24's boot argv names, and its identity
     against the binary E23 actually booted;
  2. the preflight file-hash gate E24's capture driver runs before its atomic
     lease claim -- every pin it checks, evaluated now;
  3. the second instrument E24's design depends on (`PS2X_DIAG_SEMA`), present
     in the fork source at 3adc0478 and in the built binary.
Nothing here launches anything.
"""
import re, subprocess
from e29_common import *

E24D = E.parent / 'E24'
ELF = W / 'P1/cd/SLUS_207.72'
ELF_SHA = '1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc'
BIN = B0 / 'ps2xRuntime/ps2EntryRunner'
TEST = B0 / 'ps2xTest/ps2x_tests'

e23 = json.loads((E.parent / 'E23/final-audit.json').read_text())
checks = []
def check(name, ok, **d):
    checks.append(dict(check=name, ok=bool(ok), **d))

# 1. the boot argv's own paths
boot_argv = ['/tmp/e18-mpeg-link/runtime/ps2xRuntime/ps2EntryRunner',
             '/Volumes/Extreme SSD/ps2recomp-spike/P1/cd/SLUS_207.72']
check('E23 boot argv[0] exists at its exact path', Path(boot_argv[0]).exists(), path=boot_argv[0])
check('E23 boot argv[1] exists at its exact path', Path(boot_argv[1]).exists(), path=boot_argv[1])
check('rebuilt runner IS the binary E23 booted (sha)', sha(BIN) == e23['runner']['sha256'],
      sha256=sha(BIN), e23_sha=e23['runner']['sha256'])

# 2. E24's capture preflight gate, every pin
gate = []
for label, path, size, expected in [
        ('runner', BIN, e23['runner']['bytes'], e23['runner']['sha256']),
        ('suite', TEST, e23['suite']['bytes'], e23['suite']['sha256']),
        ('ELF (cd)', ELF, 3890784, ELF_SHA),
        ('ELF (P1)', W / 'P1/SLUS_207.72', 3890784, ELF_SHA),
        ('observer dylib', E / 'parser/e21-parser-observer.dylib', 52472,
         json.loads((E.parent / 'E21/parser-build.json').read_text())['observer']['sha256'])]:
    p = Path(path)
    row = dict(item=label, path=str(p), present=p.exists())
    if p.exists():
        row.update(bytes=p.stat().st_size, sha256=sha(p),
                   size_ok=(size is None or p.stat().st_size == size),
                   sha_ok=sha(p) == expected)
    gate.append(row)
check('E24 capture preflight hash gate passes on all five pins',
      all(r.get('present') and r.get('size_ok') and r.get('sha_ok') for r in gate),
      pins=len(gate))

# 3. the second instrument E24's boot design needs
sched = R / 'ps2xRuntime/src/lib/Kernel/EeScheduler.cpp'
text = sched.read_text(errors='replace') if sched.exists() else ''
envs = {v: len(re.findall(re.escape(v), text)) for v in ('PS2X_DIAG_SEMA', 'PS2X_DIAG_SEMA_S0')}
check('PS2X_DIAG_SEMA present in EeScheduler.cpp at 3adc0478', envs['PS2X_DIAG_SEMA'] > 0, **envs)
strings = subprocess.run(['strings', '-a', str(BIN)], capture_output=True, text=True).stdout
in_bin = {v: strings.count(v) for v in ('PS2X_DIAG_SEMA', 'PS2X_DIAG_SEMA_S0', 'PS2X_DIAG_PERIOD_MS')}
check('PS2X_DIAG_SEMA compiled into the rebuilt runner', in_bin['PS2X_DIAG_SEMA'] > 0, **in_bin)

# posture
lease = Path('/tmp/ssx3-p-lane-lease')
pg = subprocess.run(['pgrep', '-x', 'ps2EntryRunner'], capture_output=True, text=True)
check('lease absent', not lease.exists())
check('no runner process', pg.returncode == 1)
check('no boot-attempt.json written by E29', not (E / 'boot-attempt.json').exists())

ok = all(c['ok'] for c in checks)
save('e29-readiness.json', dict(utc=utc(), boot_argv=boot_argv,
     capture_preflight_gate=gate, checks=checks, all_green=ok,
     note=('E29 spends no boot and claims no lease. These are read-only checks of what '
           'E29 inherits. Because the rebuilt runner is byte-identical to the binary E23 '
           'booted, every property E15-E23 measured on that binary transfers by identity '
           'rather than by re-measurement.')))
for c in checks:
    print(f"{'PASS' if c['ok'] else 'FAIL'}  {c['check']}")
print('ALL GREEN:', ok)
print('# E29 E29 READINESS TAIL COMPLETE')
