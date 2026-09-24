#!/usr/bin/env python3
"""N8D7M12 Part 4 checker: pin/lease/result agreement. Exit 0 on PASS."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STREAM_PIN = "f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593"
STREAM_SIZE = 1100696462
APK_PIN = "caa1110297dc413d3b04e7442873e0fb5d5624af8417e1e30537d76184d5f512"
APK_SIZE = 153753116

rows = []


def row(name, ok, detail=""):
    rows.append({"row": name, "pass": bool(ok), "detail": detail})


def main():
    r = json.loads((HERE / "result.json").read_text())
    verdict = r.get("verdict")
    row("local_stream_pin", r.get("hashes_local_stream") == [STREAM_PIN] * 2
        and r.get("size_local_stream") == STREAM_SIZE,
        f"{r.get('hashes_local_stream')} size={r.get('size_local_stream')}")
    row("local_apk_pin", r.get("hashes_local_apk") == [APK_PIN] * 2
        and r.get("size_local_apk") == APK_SIZE,
        f"{r.get('hashes_local_apk')} size={r.get('size_local_apk')}")
    row("preflight_gates", r.get("keyguard") == "false"
        and r.get("battery_level", 0) >= 20 and r.get("battery_status") in (2, 5)
        and r.get("free_bytes", 0) >= 10 * 1024**3,
        f"keyguard={r.get('keyguard')} batt={r.get('battery_level')}%/{r.get('battery_status')} "
        f"free={r.get('free_bytes')}")
    row("push_cap", r.get("push_count", 99) <= 1, f"push_count={r.get('push_count')}")
    remote_ok = (r.get("remote_sha") == [STREAM_PIN] * 2
                 and r.get("remote_size") == STREAM_SIZE)
    row("device_stream_exact", remote_ok,
        f"{r.get('remote_sha')} size={r.get('remote_size')}")
    row("app_stopped_end", r.get("app_pid_end") == "", f"pid={r.get('app_pid_end')!r}")
    row("lease_released", str(r.get("lease_after", "")).startswith("LEASE_FREE")
        and r.get("lease_tag") not in (None, "")
        and not str(r.get("lease_after", "")).endswith(str(r.get("lease_tag"))),
        f"before={r.get('lease_before')!r} after={r.get('lease_after')!r}")
    if verdict == "A":
        row("verdict_A_agrees", all(x["pass"] for x in rows),
            "A requires every row above")
    elif verdict == "B":
        row("verdict_B_agrees", r.get("push_count") == 0
            and not remote_ok and len(r.get("remote_sha", [])) == 2,
            "B requires mismatch recorded with two hashes and no push")
    elif verdict == "OTHER":
        row("verdict_OTHER_agrees", r.get("first_failure") not in ("not found", ""),
            "OTHER requires a recorded failure")
    else:
        row("verdict_known", False, f"verdict={verdict!r}")
    passed = sum(1 for x in rows if x["pass"])
    out = {"verdict": verdict, "rows": rows, "passed": passed,
           "total": len(rows), "gate": "PASS" if passed == len(rows) else "FAIL"}
    (HERE / "check-result.json").write_text(json.dumps(out, indent=2) + "\n")
    for x in rows:
        print(("PASS " if x["pass"] else "FAIL ") + x["row"] + " " + x["detail"])
    print(f"{out['gate']} {passed}/{len(rows)} verdict={verdict}")
    return 0 if out["gate"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
