#!/usr/bin/env python3
"""F5 Odin cool-down: replicate the F4-2b method (thermal status 0 pre-wait,
180 s wait, thermal status 0 at launch) BEFORE launch.py runs, so the device
lease is not held during the wait. Logs to the run's OUT dir (created here;
launch.py appends its own files after).

Usage: cooldown.py --label R1 [--pre-cap-min 20] [--wait-s 180]
Exit 0 = status 0 now (launch when ready); exit 1 = never cooled / run would
launch hot (operator decides).
"""
import argparse, os, subprocess, sys, time

D = open(os.path.expanduser('~/dev/ssx3/local/odin-serial')).read().strip()
PKG = 'com.ps2x.runner'

ap = argparse.ArgumentParser()
ap.add_argument('--label', required=True)
ap.add_argument('--pre-cap-min', type=float, default=20.0)
ap.add_argument('--wait-s', type=float, default=180.0)
a = ap.parse_args()

OUT = os.path.expanduser(f'/Users/brad/dev/ssx3/local/research/F5/logs/{a.label}')
os.makedirs(OUT, exist_ok=True)
LOG = open(f'{OUT}/cooldown.txt', 'a')


def log(msg):
    line = f'[{time.strftime("%H:%M:%S")}] {msg}'
    print(line, flush=True)
    LOG.write(line + '\n')
    LOG.flush()


def sh(cmd, timeout=60):
    r = subprocess.run(['adb', '-s', D, 'shell', cmd], capture_output=True,
                       text=True, timeout=timeout)
    return r.stdout


def sample():
    out = sh('echo "$(dumpsys thermalservice | grep -m1 Thermal\\ Status | tr -dc 0-9) '
             '$(for z in /sys/class/thermal/thermal_zone*; do '
             '[ "$(cat $z/type)" = cpu-1-1-1 ] && cat $z/temp; done) '
             '$(dumpsys battery | grep -m1 level:)"').split()
    status = int(out[0]) if out and out[0].isdigit() else -1
    return status, ' '.join(out)


t0 = time.time()
log(f'COOLDOWN start pre-wait (cap {a.pre_cap_min} min)')
while True:
    status, raw = sample()
    log(f'PRE status={status} raw={raw!r} elapsed={(time.time() - t0) / 60:.1f}min')
    if status == 0:
        break
    if (time.time() - t0) / 60 >= a.pre_cap_min:
        log('COOLDOWN pre-wait cap reached without status 0')
        sys.exit(1)
    time.sleep(15)

log(f'COOLDOWN status 0; waiting {a.wait_s:.0f} s')
time.sleep(a.wait_s)
status, raw = sample()
log(f'POST status={status} raw={raw!r}')
extra = 0.0
while status != 0 and extra < 600:
    time.sleep(60)
    extra += 60
    status, raw = sample()
    log(f'POST+{extra:.0f}s status={status} raw={raw!r}')
if status != 0:
    log('COOLDOWN still hot after extensions; refusing to green-light')
    sys.exit(1)
pid = sh(f'pidof {PKG}').strip()
kg = sh('dumpsys window policy | grep -m1 showing').strip()
log(f'COOLDOWN green: status 0 at launch, pid={pid or "none"} keyguard={kg!r}')
LOG.close()
