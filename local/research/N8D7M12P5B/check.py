#!/usr/bin/env python3
"""N8D7M12 Part 5B postrun checker: static only, no device calls.

Reads the private run receipts in ~/dev/ssx3-work/N8D7M12P5A/
(result.json, driver.log) plus pulled-file metadata recorded there, and
verifies REPORT.md carries the required tables. Writes
check-result.json here. Usage: check.py [--self-check] (default).
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRATCH = Path("/Users/brad/dev/ssx3-work/N8D7M12P5A")
REPORT = HERE / "REPORT.md"
REVIEWED_SHA = "287140bf370acfb105f1b64347a635822300699150e517e6b912340ae031334e"
PINS = {
    "apk": "caa1110297dc413d3b04e7442873e0fb5d5624af8417e1e30537d76184d5f512",
    "runner": "329e44db7133a7f56c7978fd9594189e7ff595e2834d9755fa80efe46a218a3d",
    "turnip": "717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d",
    "hal": "1b49d27c839f25363237d8276c91a401602845ee8eef67de50d6540f4cdfc387",
    "stream": "f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593",
}
CONTROL_ADDRS = ("0x0E0000", "0x0E0534", "0x0E0040", "0x1BFFF4",
                 "0x0E2000", "0x0F0000", "0x0E1FFC", "0x0F2000")

CHECKS = []


def check(name):
    def deco(fn):
        CHECKS.append((name, fn))
        return fn
    return deco


def load():
    result = json.loads((SCRATCH / "result.json").read_text())
    driver = (SCRATCH / "driver.log").read_text()
    rep = REPORT.read_text() if REPORT.exists() else ""
    return result, driver, rep


@check("verdict_provisional_pass_no_failure")
def c_verdict(r, _d, _rep):
    return (r.get("verdict") == "PROVISIONAL PASS"
            and r.get("first_failure") == "not found"
            and not r.get("cleanup_errors")
            and r.get("provisional") is True)


@check("script_sha_reviewed_pin")
def c_sha(r, _d, _rep):
    return r.get("script_sha") == REVIEWED_SHA


@check("single_install_single_launch")
def c_counts(r, _d, _rep):
    return r.get("install_count") == 1 and r.get("launch_count") == 1


@check("all_hash_pairs_match_pins")
def c_hashes(r, _d, _rep):
    h = r.get("hashes", {})
    pairs = [("local_apk", PINS["apk"]), ("installed_apk", PINS["apk"]),
             ("local_stream", PINS["stream"]), ("device_stream", PINS["stream"])]
    if any(h.get(k) != [pin, pin] for k, pin in pairs):
        return False
    for label, pin in (("packaged_runner", PINS["runner"]),
                       ("packaged_turnip", PINS["turnip"]),
                       ("packaged_hal", PINS["hal"])):
        if h.get(label) != [pin, pin]:
            return False
    for name in ("vq-002050.ppm", "parallel.hashes"):
        entry = h.get(name, {})
        if not entry or entry["device"] != entry["local"] \
                or entry["device"][0] != entry["device"][1]:
            return False
    return True


@check("markers_tick2050_no_errors")
def c_markers(r, _d, _rep):
    m = r.get("markers", {})
    return (m.get("summary", [None] * 6)[1] == "parallel"
            and m.get("summary", [None] * 6)[5] == "2050"
            and m.get("frame", [None] * 4)[0] == "2050"
            and m.get("replay_ok", [None] * 2)[1] == "2050"
            and not m.get("errors"))


@check("census_alignment_control_stages")
def c_census(r, _d, _rep):
    p = r.get("probe", {})
    if p.get("alignment") != ["2050", "112", "ff21", "512", "448"]:
        return False
    if p.get("control") != ["128", "128", "PASS"]:
        return False
    stages = p.get("stages", {})
    return (stages.get("circuit1", [])[:3] == [512, 224, 448]
            and stages.get("pre_deinterlace_merged", [])[:3] == [512, 224, 448]
            and stages.get("final", [])[:3] == [512, 448, 896]
            and all(s[5] == 128 for s in stages.values())
            and not p.get("errors"))


@check("census_vectors_consistent")
def c_vectors(r, _d, _rep):
    p = r.get("probe", {})
    vec = p.get("vectors", {})
    sel = p.get("selected", {})
    if set(vec) != {"sampled", "raw", "input", "circuit", "stage", "oracle"}:
        return False
    if any(not v for v in vec.values()):
        return False
    if (vec["sampled"]["occupied"], vec["sampled"]["active"]) != (
            int(p["sampled"][1]), int(p["sampled"][2])):
        return False
    if (vec["raw"]["occupied"], vec["raw"]["active"]) != (
            int(p["raw"][1]), int(p["raw"][2])):
        return False
    for kind in ("input", "circuit", "stage", "oracle"):
        summ = sel[kind]
        if (vec[kind]["occupied"], vec[kind]["active"]) != (
                int(summ[1]), int(summ[2])):
            return False
        if summ[3] != "unavailable" and summ[3] != vec[kind]["sha256"]:
            return False
    shas = {vec[k]["sha256"] for k in ("input", "circuit", "stage", "oracle")}
    if len(shas) != 1:
        return False
    if vec["sampled"]["sha256"] != vec["raw"]["sha256"]:
        return False
    if sel.get("equal") != ["448", "448"]:
        return False
    if p.get("oracle", {}).get("equal") != ["448"]:
        return False
    shared_sel = sel["metadata"][:11]
    shared_or = p["oracle"]["metadata"][:11]
    return shared_sel == shared_or


@check("oracle_control_addresses_literal_order")
def c_controls(r, _d, _rep):
    payload = r.get("probe", {}).get("oracle", {}).get("controls", [None])[0]
    if payload is None:
        return False
    parts = payload.split(",")
    if len(parts) != 8:
        return False
    return [p.split("=")[0] for p in parts] == list(CONTROL_ADDRS)


@check("cleanup_intact_in_driver_log")
def c_cleanup(_r, d, _rep):
    return ("CLEANUP pid-after=none" in d
            and "CLEANUP env restored" in d
            and "CLEANUP lease=LEASE_FREE N8D7M12P5A done" in d
            and "CLEANUP ERROR" not in d)


@check("caps_elapsed_log_output")
def c_caps(r, _d, _rep):
    if not (r.get("elapsed_s", 9999) <= 600):
        return False
    gz = SCRATCH / "logcat-all.txt.gz"
    ppm = SCRATCH / "vq-002050.ppm"
    hashes = SCRATCH / "parallel.hashes"
    if not (gz.exists() and ppm.exists() and hashes.exists()):
        return False
    if gz.stat().st_size > 16 * 1024 * 1024:
        return False
    return ppm.stat().st_size + hashes.stat().st_size <= 64 * 1024 * 1024


@check("report_tables_provisional_no_cause")
def c_report(_r, _d, rep):
    low = rep.lower()
    keys = ("provisional pass", "provisional until the orchestrator views",
            "no cause", "no same-binary off control")
    full = (REVIEWED_SHA, PINS["apk"], PINS["stream"],
            "39b70d677651f08d702c7e0460a71dff8905aad639797b1b5b23540025350d41")
    return all(k in low for k in keys) and all(k in rep for k in full)


@check("no_device_calls_in_checker")
def c_noself(_r, _d, _rep):
    mine = (HERE / "check.py").read_text()
    tok = "subpro" + "cess"
    adb_pat = "ad" + r"b\s*\("
    imports = re.findall(r"^\s*(?:import\s+" + tok + r"|from\s+" + tok + r")\b",
                         mine, re.M)
    calls = re.findall(r"^\s*(?:" + tok + r"\s*\.\s*(?:run|Popen|call)|os\s*\.\s*system"
                       r"|" + adb_pat + r")", mine, re.M)
    return not imports and not calls


def main():
    result, driver, rep = load()
    rows = []
    for name, fn in CHECKS:
        try:
            rows.append({"check": name, "pass": bool(fn(result, driver, rep))})
        except Exception as exc:
            rows.append({"check": name, "pass": False, "error": repr(exc)})
    passed = sum(1 for row in rows if row["pass"])
    mismatch = ("markers_tick2050_no_errors", "census_alignment_control_stages",
                "census_vectors_consistent", "all_hash_pairs_match_pins")
    verdict = "A" if passed == len(rows) else (
        "B" if any(row["check"] in mismatch and not row["pass"] for row in rows)
        else "OTHER")
    out = {"brief": "N8D7M12P5B", "checks": rows,
           "passed": f"{passed}/{len(rows)}", "verdict": verdict,
           "note": "Static postrun read of the single released run. "
                   "Frame stays provisional until the orchestrator views it."}
    (HERE / "check-result.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"{verdict} {passed}/{len(rows)}")
    for row in rows:
        print(("PASS " if row["pass"] else "FAIL ") + row["check"])
    return 0 if verdict == "A" else 1


if __name__ == "__main__":
    if "--self-check" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(main())
    raise SystemExit("usage: check.py [--self-check]")
