#!/usr/bin/env python3
"""MT1 stage 3: det-hash compare for a sparse-hash candidate (--hash-every N).

Every det-hash tick the candidate emitted must exist in the baseline with the
same line (the baseline has every tick). gb8_hashdiff would read the skipped
ticks as missing; snd/coverage still come from `baseline.py compare` (its
verdict line is printed, its hash line is not used here).
Usage: sparse_compare.py --key KEY --cand RUN_DIR [--every 60] [--max-tick 2400]
"""
import argparse, importlib.util, pathlib, subprocess, sys

REPO = pathlib.Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("gb8", REPO / "local/research/GB8/gb8_hashdiff.py")
gb8 = importlib.util.module_from_spec(spec); spec.loader.exec_module(gb8)

ap = argparse.ArgumentParser()
ap.add_argument("--key", required=True)
ap.add_argument("--cand", required=True)
ap.add_argument("--every", type=int, default=60)
ap.add_argument("--max-tick", type=int, default=2400)
ap.add_argument("--store", default=str(pathlib.Path.home() / "dev/ssx3-work/baselines"))
a = ap.parse_args()
hb = gb8.hash_lines(pathlib.Path(a.store) / a.key)
hc = gb8.hash_lines(a.cand)
want = [t for t in range(a.every, a.max_tick + 1, a.every)]
missing = [t for t in want if t not in hc]
extra = [t for t in hc if t % a.every != 0 and t <= a.max_tick]
diff = [t for t in sorted(hc) if t <= a.max_tick and (t not in hb or hb[t] != hc[t])]
good = not missing and not diff
print("sparse hash %s every=%d ticks<=%d: compared=%d missing=%d off-grid=%d first_diff=%s"
      % ("IDENTICAL" if good else "DIFFER", a.every, a.max_tick, len([t for t in hc if t <= a.max_tick]),
         len(missing), len(extra), diff[0] if diff else None))
r = subprocess.run([sys.executable, str(REPO / "local/tooling/boot/baseline.py"), "compare", "--key", a.key,
                    "--cand", a.cand], capture_output=True, text=True)
snd = [l for l in r.stdout.splitlines() if l.startswith("snd/coverage")]
print(snd[0] if snd else "snd/coverage: (no line)")
sys.exit(0 if good and snd and snd[0].endswith("IDENTICAL") else 1)
