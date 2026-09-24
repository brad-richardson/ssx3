#!/usr/bin/env python3
"""N8D7M12 Part 5E2 narrow receipt checker (read-only, device-free).

Compares the OFF2 run receipts against the pinned OFF1 receipts and the
brief acceptance rows. Exit 0 + verdict A only if every row passes;
otherwise exit 1 with the first failure named. Never touches the
device, never launches, never edits receipts.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
P5E1 = REPO / "local/research/N8D7M12P5E1"
P5E2 = REPO / "local/research/N8D7M12P5E2"
WORK = Path.home() / "dev/ssx3-work"
OFF1_DIR = WORK / "N8D7M12P5D1"
OFF2_DIR = WORK / "N8D7M12P5E1"
OFF1_HASHES_SHA = "19738cc310ff81552546477ae040061f780124b19fefbccad0f671537c783af9"
OFF1_PPM_SHA = "5e0caca3773096d51595530fe3278cc92ca42b59f590a5c4e0d3e84d05adbea4"
OFF2_LAUNCHER_SHA = "ad22755d07cd4ce87cbd6823144181389e0b50d2a2f081f3cf879f54b80af4ca"
EXPECTED_TICKS = list(range(50, 2051, 50))

ROW_RE = re.compile(r"GB4_REPLAY tick=(\d+) vram=([0-9a-f]+) priv=([0-9a-f]+) present=([0-9a-f]+)")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def parse_rows(path):
    rows = []
    for line in Path(path).read_text().splitlines():
        m = ROW_RE.search(line)
        if m:
            rows.append((int(m.group(1)), m.group(2), m.group(3), m.group(4)))
    return rows


def main():
    checks = []

    def check(name, ok, detail=""):
        checks.append({"check": name, "pass": bool(ok), "detail": detail})
        print(("PASS " if ok else "FAIL ") + name + (f" ({detail})" if detail else ""))
        return ok

    ok = True
    # 1. OFF2 launcher SHA unchanged (reviewed, gated)
    ok &= check("off2_launcher_sha", sha(P5E1 / "launch.py") == OFF2_LAUNCHER_SHA, sha(P5E1 / "launch.py")[:12])
    # 2. OFF1 receipts preserved byte-exact
    ok &= check("off1_hashes_preserved", sha(OFF1_DIR / "parallel.hashes") == OFF1_HASHES_SHA, f"{(OFF1_DIR / 'parallel.hashes').stat().st_size} B")
    ok &= check("off1_ppm_preserved", sha(OFF1_DIR / "vq-002050.ppm") == OFF1_PPM_SHA, f"{(OFF1_DIR / 'vq-002050.ppm').stat().st_size} B")
    # 3. OFF2 result exists and is complete
    rpath = OFF2_DIR / "result.json"
    if not rpath.exists():
        ok &= check("off2_result_present", False, "result.json missing")
    else:
        res = json.loads(rpath.read_text())
        ok &= check("off2_result_present", True, "")
        m = res.get("markers", {})
        ok &= check("off2_replay_ok", m.get("summary", [None] * 6)[5] == "2050" and m.get("replay_ok") == ["862958", "2050"] and m.get("errors") == [], f"summary={m.get('summary')} replay_ok={m.get('replay_ok')}")
        ok &= check("off2_one_install_launch", res.get("install_count") == 1 and res.get("launch_count") == 1, f"install={res.get('install_count')} launch={res.get('launch_count')}")
        ok &= check("off2_no_first_failure", res.get("first_failure") in (None, "not found", ""), str(res.get("first_failure"))[:80])
        ok &= check("off2_cleanup_clean", not res.get("cleanup_errors"), str(res.get("cleanup_errors", ""))[:80])
        ok &= check("off2_script_sha", res.get("script_sha") == OFF2_LAUNCHER_SHA, str(res.get("script_sha", ""))[:12])
    # 4. OFF2 hashes: 41 rows, exact tick list
    hpath = OFF2_DIR / "parallel.hashes"
    if not hpath.exists():
        ok &= check("off2_hashes_present", False, "no parallel.hashes in OFF2 scratch")
        off2_rows = []
    else:
        ok &= check("off2_hashes_present", True, f"{hpath.stat().st_size} B")
        off2_rows = parse_rows(hpath)
        ok &= check("off2_41_rows", len(off2_rows) == 41, f"{len(off2_rows)} rows")
        ok &= check("off2_exact_ticks", [r[0] for r in off2_rows] == EXPECTED_TICKS, "50..2050 step50")
    # 5. Row-by-row OFF1/OFF2 comparison
    off1_rows = parse_rows(OFF1_DIR / "parallel.hashes")
    if off2_rows and len(off2_rows) == 41 and len(off1_rows) == 41:
        ok &= check("rows_compared_41x41", True, "both sides 41 rows, exact ticks")
        pe = sum(1 for o, f in zip(off1_rows, off2_rows) if o[2] == f[2])
        ve = sum(1 for o, f in zip(off1_rows, off2_rows) if o[1] == f[1])
        pre = sum(1 for o, f in zip(off1_rows, off2_rows) if o[3] == f[3])
        diffs = [o[0] for o, f in zip(off1_rows, off2_rows) if o != f]
        print(f"INFO priv_equal {pe}/41 vram_equal {ve}/41 present_equal {pre}/41")
        if diffs:
            print(f"INFO first_diff tick={diffs[0]}")
            print(f"INFO diff_ticks {diffs}")
            print("INFO classification SAME_SETTINGS_VARIANCE (OFF2 differs from OFF1)")
        else:
            print("INFO classification REPRODUCED (all 41 rows equal)")
        ok &= check("comparison_recorded", True, f"priv={pe}/41 vram={ve}/41 present={pre}/41 first={diffs[0] if diffs else 'none'}")
    else:
        ok &= check("rows_comparable", False, f"off1={len(off1_rows)} off2={len(off2_rows)}")
    # 6. OFF2 PPM vs OFF1 PPM SHA
    p2 = OFF2_DIR / "vq-002050.ppm"
    if not p2.exists():
        ok &= check("off2_ppm_present", False, "no vq-002050.ppm under OFF2 scratch")
    else:
        s = sha(p2)
        ok &= check("off2_ppm_present", True, f"{p2} {p2.stat().st_size} B")
        print(f"INFO off2_ppm_sha {s}")
        print(f"INFO off2_ppm_path {p2}")
        if s == OFF1_PPM_SHA:
            print("INFO ppm_equal OFF2==OFF1")
        else:
            print("INFO ppm_differs OFF2!=OFF1")
        ok &= check("ppm_compared", True, "diff recorded, not a checker failure")
    verdict = "A" if ok else "OTHER"
    (P5E2 / "check-result.json").write_text(json.dumps({"brief": "N8D7M12P5E2", "verdict": verdict, "checks": checks}, indent=2))
    print(f"VERDICT {verdict}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
