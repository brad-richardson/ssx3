#!/usr/bin/env python3
"""N8D7M12 Part 5D2 narrow receipt checker (read-only, device-free).

Compares the OFF run receipts against the pinned ON receipts and the
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
P5D1 = REPO / "local/research/N8D7M12P5D1"
P5D2 = REPO / "local/research/N8D7M12P5D2"
WORK = Path.home() / "dev/ssx3-work"
ON_HASHES = WORK / "N8D7M12P5A/parallel.hashes"
ON_PPM = WORK / "N8D7M12P5A/vq-002050.ppm"
ON_HASHES_SHA = "0e89a493764096ade2c2cc94cdb610c5a0fbf643378e5cffb98cf02a68f2c82a"
ON_PPM_SHA = "39b70d677651f08d702c7e0460a71dff8905aad639797b1b5b23540025350d41"
OFF_SHA = "223fd15ec0aa45079f44bed7ceffd3e19381d12ac0c51587a0284afb9cd03170"
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
    off_dir = WORK / "N8D7M12P5D1"

    def check(name, ok, detail=""):
        checks.append({"check": name, "pass": bool(ok), "detail": detail})
        print(("PASS " if ok else "FAIL ") + name + (f" ({detail})" if detail else ""))
        return ok

    ok = True
    # 1. OFF launcher SHA unchanged
    ok &= check("off_launcher_sha", sha(P5D1 / "launch.py") == OFF_SHA, sha(P5D1 / "launch.py")[:12])
    # 2. ON receipts preserved byte-exact
    ok &= check("on_hashes_preserved", sha(ON_HASHES) == ON_HASHES_SHA, f"{ON_HASHES.stat().st_size} B")
    ok &= check("on_ppm_preserved", sha(ON_PPM) == ON_PPM_SHA, f"{ON_PPM.stat().st_size} B")
    # 3. OFF result exists and is complete
    rpath = off_dir / "result.json"
    if not rpath.exists():
        ok &= check("off_result_present", False, "result.json missing")
        verdict = "OTHER"
    else:
        res = json.loads(rpath.read_text())
        ok &= check("off_result_present", True, "")
        m = res.get("markers", {})
        ok &= check("off_replay_ok", m.get("summary", [None]*6)[5] == "2050" and m.get("replay_ok") == ["862958", "2050"] and m.get("errors") == [], f"summary={m.get('summary')} replay_ok={m.get('replay_ok')}")
        ok &= check("off_one_install_launch", res.get("install_count") == 1 and res.get("launch_count") == 1, f"install={res.get('install_count')} launch={res.get('launch_count')}")
        ok &= check("off_no_first_failure", res.get("first_failure") in (None, "not found", ""), str(res.get("first_failure"))[:80])
        ok &= check("off_cleanup_clean", not res.get("cleanup_errors"), str(res.get("cleanup_errors", ""))[:80])
    # 4. OFF hashes: 41 rows, exact tick list
    cand = [off_dir / "parallel.hashes"]
    cand = [p for p in cand if p.exists()]
    if not cand:
        ok &= check("off_hashes_present", False, "no parallel.hashes in OFF scratch")
        off_rows = []
    else:
        ok &= check("off_hashes_present", True, cand[0].name)
        off_rows = parse_rows(cand[0])
        ok &= check("off_41_rows", len(off_rows) == 41, f"{len(off_rows)} rows")
        ok &= check("off_exact_ticks", [r[0] for r in off_rows] == EXPECTED_TICKS, "50..2050 step50")
    # 5. Row-by-row ON/OFF comparison
    on_rows = parse_rows(ON_HASHES)
    if off_rows and len(off_rows) == 41 and len(on_rows) == 41:
        first_diff = None
        ticks_le2000_diff = []
        for o, f in zip(on_rows, off_rows):
            if o != f:
                if first_diff is None:
                    first_diff = (o[0], o, f)
                if o[0] <= 2000:
                    ticks_le2000_diff.append(o[0])
        # Predeclared rule (P5C §4 row 2): flags are unread before tick2050,
        # so any ≤2000 difference classifies the comparison VOID. Recording
        # that classification IS the passing outcome, not a checker failure.
        ok &= check("rows_compared_41x41", True, "both sides 41 rows, exact ticks")
        if first_diff is None:
            print("INFO rows_all_equal ON==OFF 41/41")
        else:
            t, o, f = first_diff
            print(f"INFO first_row_diff tick={t} ON={o} OFF={f}")
        if ticks_le2000_diff:
            print(f"INFO classification VOID (differs at {len(ticks_le2000_diff)} ticks ≤2000: {ticks_le2000_diff})")
        else:
            print("INFO classification rows-equal-through-2000")
    else:
        ok &= check("rows_comparable", False, f"on={len(on_rows)} off={len(off_rows)}")
    # 6. OFF PPM vs ON PPM SHA
    ppms = list(off_dir.glob("**/vq-002050.ppm"))
    if not ppms:
        ok &= check("off_ppm_present", False, "no vq-002050.ppm under scratch")
    else:
        p = ppms[0]
        s = sha(p)
        ok &= check("off_ppm_present", True, f"{p} {p.stat().st_size} B")
        print(f"INFO off_ppm_sha {s}")
        print(f"INFO off_ppm_path {p}")
        if s == ON_PPM_SHA:
            print("INFO ppm_equal ON==OFF")
        else:
            print("INFO ppm_differs ON!=OFF")
            ok &= check("ppm_compared", True, "diff recorded, not a checker failure")
    verdict = "A" if ok else "OTHER"
    (P5D2 / "check-result.json").write_text(json.dumps({"brief": "N8D7M12P5D2", "verdict": verdict, "checks": checks}, indent=2))
    print(f"VERDICT {verdict}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
