#!/usr/bin/env python3
"""Canonical Odin cool-down before a launch (Brad 09-26: speed up Odin runs).

Two modes:
  --mode screen (default): A/B screening runs. Launch at once if thermal status is 0 AND the
      prime-core zone (cpu-1-1-1) is below --max-temp-c (default 42 C); otherwise poll every 15 s
      until both hold. No fixed wait. Pair with a short speed window (--stop-tick 3000).
  --mode final: numbers that go in the ledger or decide a play build. Cool to status <= 1, then a
      FIXED --wait-s (default 180 s), as F4-F7 did (it cancels thermal drift between ABBA legs).
Run it BEFORE claiming the Odin lease (the wait doesn't hold the device). Logs to --out/cooldown.txt.
Exit 0 = ready (launch now); exit 1 = never cooled within --cap-min (operator decides).
"""
import argparse, os, subprocess, sys, time

D = open(os.path.expanduser('~/dev/ssx3/local/odin-serial')).read().strip()

ap = argparse.ArgumentParser()
ap.add_argument('--out', required=True, help='run dir; cooldown.txt is appended there')
ap.add_argument('--mode', choices=['screen', 'final'], default='screen')
ap.add_argument('--max-temp-c', type=float, default=42.0)
ap.add_argument('--wait-s', type=float, default=180.0)
ap.add_argument('--cap-min', type=float, default=20.0)
ap.add_argument('--fan', choices=['performance', 'leave'], default='performance',
                help='performance: set fan_mode=5 for the run (remembers the previous value in\n'
                     '/data/local/tmp/mg/fan_prev; odin_restore_play.sh puts it back). Never writes 0 (off).')
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
LOG = open(os.path.join(a.out, 'cooldown.txt'), 'a')


def log(msg):
    line = f'[{time.strftime("%H:%M:%S")}] {msg}'
    print(line, flush=True)
    LOG.write(line + '\n'); LOG.flush()


def sample():
    out = subprocess.run(['adb', '-s', D, 'shell',
        'echo "$(dumpsys thermalservice | grep -m1 Thermal\\ Status | tr -dc 0-9) '
        '$(for z in /sys/class/thermal/thermal_zone*; do [ "$(cat $z/type)" = cpu-1-1-1 ] && cat $z/temp; done)"'],
        capture_output=True, text=True, timeout=60).stdout.split()
    status = int(out[0]) if out and out[0].isdigit() else -1
    temp_c = int(out[1]) / 1000.0 if len(out) > 1 and out[1].isdigit() else 999.0
    return status, temp_c


# Fan (Brad 09-26: fan_mode 0 = off, 1/4 = quiet/smart, 5 = performance).
if a.fan == 'performance':
    sh_ = lambda c: subprocess.run(['adb', '-s', D, 'shell', c], capture_output=True, text=True, timeout=60).stdout.strip()
    prev = sh_('settings get system fan_mode')
    if prev != '5':
        if prev.isdigit() and prev != '0':
            sh_(f'[ -f /data/local/tmp/mg/fan_prev ] || echo {prev} > /data/local/tmp/mg/fan_prev')
        sh_('settings put system fan_mode 5')
    log(f'FAN performance (fan_mode {prev} -> {sh_("settings get system fan_mode")}; restore via odin_restore_play.sh)')

t0 = time.time()
log(f'COOLDOWN mode={a.mode} max_temp={a.max_temp_c} C wait={a.wait_s if a.mode == "final" else 0:.0f} s')
while True:
    status, temp_c = sample()
    ok = (status == 0 and temp_c < a.max_temp_c) if a.mode == 'screen' else (0 <= status <= 1)
    log(f'SAMPLE status={status} cpu7_zone={temp_c:.1f} C ok={ok} elapsed={(time.time() - t0) / 60:.1f} min')
    if ok:
        break
    if (time.time() - t0) / 60 >= a.cap_min:
        log('COOLDOWN cap reached without cooling'); sys.exit(1)
    time.sleep(15)
if a.mode == 'final':
    log(f'fixed wait {a.wait_s:.0f} s'); time.sleep(a.wait_s)
    status, temp_c = sample()
    log(f'POST status={status} cpu7_zone={temp_c:.1f} C')
log(f'COOLDOWN ready after {(time.time() - t0):.0f} s')
