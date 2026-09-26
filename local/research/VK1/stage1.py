#!/usr/bin/env python3
"""VK1 stage-1 summary for one Odin run dir (logs/<label>):
- threadcpu.txt (launch.py --cpu-window): per-thread CPU ms per guest frame
- gpubusy.txt: mean kgsl busy % over the same tick window
- logcat.txt: backend `[gs:parallel] periodic ... presents=N present_ms_avg=..`
  lines are cumulative averages; the window delta is
  (avg2*n2 - avg1*n1) / (n2 - n1) between the lines bracketing the window.
Usage: stage1.py logs/P1 [logs/P2 ...]
"""
import re
import sys

STAT = re.compile(r'\[gs:parallel\] (?:periodic|first-present) .*?presents=(\d+) .*?present_ms_avg=([\d.e+-]+) '
                  r'readback_ms_avg=([\d.e+-]+) copy_ms_avg=([\d.e+-]+)(.*)')
RATE = re.compile(r'\[vsync-rate\] tick=(\d+) rate=([\d.]+)')


def window(d):
    head = open(f'{d}/threadcpu.txt').readline()
    m = re.search(r'ticks (\d+)->(\d+) \((\d+) frames\) wall ([\d.]+) s = ([\d.]+) ms/frame, ([\d.]+) vs/s', head)
    return tuple(float(x) for x in m.groups())


def main():
    for d in sys.argv[1:]:
        k0, k1, frames, wall, msf, vss = window(d)
        print(f'== {d}: ticks {k0:.0f}->{k1:.0f}, {frames:.0f} frames, {wall:.1f} s, {msf:.1f} ms/frame, '
              f'{vss:.2f} vs/s = {vss / 59.94:.3f}x')
        rows = [l.split() for l in open(f'{d}/threadcpu.txt').read().splitlines()[2:]]
        by = {}
        for tid, comm, cpu_s, msframe, util in rows:
            by.setdefault(comm, []).append((float(msframe), float(util), tid))
        for comm, v in sorted(by.items(), key=lambda kv: -sum(x[0] for x in kv[1]))[:12]:
            ms = sum(x[0] for x in v)
            print(f'   {comm:<18} threads={len(v):<2} cpu {ms:7.2f} ms/frame  util {sum(x[1] for x in v):5.1f} %')
        busy = []
        for l in open(f'{d}/gpubusy.txt'):
            m = re.search(r'tick=(\d+) .*pct=([\d.]+)', l)
            if m and k0 <= int(m.group(1)) <= k1 and float(m.group(2)) >= 0:
                busy.append(float(m.group(2)))
        if busy:
            print(f'   GPU busy mean {sum(busy) / len(busy):.1f} % (n={len(busy)})')
        stats = []
        ticks = []
        for l in open(f'{d}/logcat.txt', errors='replace'):
            m = RATE.search(l)
            if m:
                ticks.append(int(m.group(1)))
            m = STAT.search(l)
            if m:
                tick_now = ticks[-1] if ticks else 0
                stats.append((tick_now, int(m.group(1)), *[float(x) for x in m.groups()[1:4]], m.group(5).strip()))
        before = [s for s in stats if s[0] <= k0]
        after = [s for s in stats if s[0] >= k1]
        if before and after:
            a, b = before[-1], after[0]
            n = b[1] - a[1]
            if n > 0:
                pr = (b[2] * b[1] - a[2] * a[1]) / n
                rb = (b[3] * b[1] - a[3] * a[1]) / n
                cp = (b[4] * b[1] - a[4] * a[1]) / n
                print(f'   backend per present (ticks ~{a[0]}->{b[0]}, {n} presents): present {pr:.2f} ms, '
                      f'readback {rb:.2f} ms, copy {cp:.2f} ms, present-minus-readback-copy {pr - rb - cp:.2f} ms')
        if stats:
            print(f'   last stats line: presents={stats[-1][1]} present={stats[-1][2]:.2f} readback={stats[-1][3]:.3f} '
                  f'copy={stats[-1][4]:.3f} {stats[-1][5][:200]}')


if __name__ == '__main__':
    main()
