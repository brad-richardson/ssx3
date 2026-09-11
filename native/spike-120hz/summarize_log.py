#!/usr/bin/env python3
"""Aggregate the [ssx3-framegen] statistics windows of a native run log.

Usage: summarize_log.py LOG [--skip-seconds N]   (windows before N seconds of wall time are ignored)
"""
import re
import sys


def main():
    path = sys.argv[1]
    skip = float(sys.argv[sys.argv.index("--skip-seconds") + 1]) if "--skip-seconds" in sys.argv else 0.0
    pattern = re.compile(r"\[ssx3-framegen\] frames=(\d+) window_s=([\d.]+) gpu_ms avg=([\d.]+) max=([\d.]+) "
                         r"samples=(\d+) presented total=(\d+) real=(\d+) interp=(\d+) rate=([\d.]+)/s "
                         r"intervals<=12ms=(\d+) >12ms=(\d+) latency_ms real_avg=([\d.]+) real_max=([\d.]+) "
                         r"interp_avg=([\d.]+)(?: cost avg=([\d.]+) max=([\d.]+) cut_frames=(\d+))?")
    elapsed = 0.0
    gpu_sum = gpu_max = 0.0
    gpu_n = 0
    presented = real = interp = short = long_ = 0
    window_sum = 0.0
    lat_sum = lat_max = 0.0
    lat_n = 0
    ilat_sum = 0.0
    ilat_n = 0
    cost_sum = cost_max = 0.0
    cost_n = cuts = 0
    rates = []
    fps = []
    for line in open(path, errors="replace"):
        m = re.search(r"\[ssx3-metrics\] sample=(\d+) fps=([\d.]+) vps=([\d.]+) speed=([\d.]+)", line)
        if m and int(m.group(1)) >= skip:
            fps.append((float(m.group(2)), float(m.group(4))))
        m = pattern.search(line)
        if not m:
            continue
        window = float(m.group(2))
        elapsed += window
        if elapsed < skip or window < 5:
            continue
        samples = int(m.group(5))
        gpu_sum += float(m.group(3)) * samples
        gpu_max = max(gpu_max, float(m.group(4)))
        gpu_n += samples
        presented += int(m.group(6)); real += int(m.group(7)); interp += int(m.group(8))
        rates.append(float(m.group(9)))
        short += int(m.group(10)); long_ += int(m.group(11))
        window_sum += window
        n_real = int(m.group(7))
        lat_sum += float(m.group(12)) * n_real; lat_n += n_real
        lat_max = max(lat_max, float(m.group(13)))
        n_i = int(m.group(8))
        ilat_sum += float(m.group(14)) * n_i; ilat_n += n_i
        if m.group(15):
            cost_sum += float(m.group(15)) * samples; cost_n += samples
            cost_max = max(cost_max, float(m.group(16))); cuts += int(m.group(17))
    print(f"{path}")
    print(f"  windows: {len(rates)} covering {window_sum:.0f} s (after skipping {skip:.0f} s)")
    if gpu_n:
        print(f"  gpu_ms per synthesized frame: avg={gpu_sum / gpu_n:.3f} max={gpu_max:.3f} (n={gpu_n})")
    print(f"  presented: total={presented} real={real} interp={interp} rate avg={sum(rates) / max(1, len(rates)):.1f}/s "
          f"intervals<=12ms={short} >12ms={long_}")
    if lat_n:
        print(f"  latency_ms real: avg={lat_sum / lat_n:.2f} max={lat_max:.2f}", end="")
        print(f"  interp avg={ilat_sum / ilat_n:.2f}" if ilat_n else "")
    if cost_n:
        print(f"  cost: avg={cost_sum / cost_n:.4f} max={cost_max:.4f} cut_frames={cuts}")
    if fps:
        print(f"  emulation: fps avg={sum(f for f, _ in fps) / len(fps):.1f} speed avg={sum(s for _, s in fps) / len(fps):.3f} (n={len(fps)})")


if __name__ == "__main__":
    main()
