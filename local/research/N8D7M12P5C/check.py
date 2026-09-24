#!/usr/bin/env python3
"""N8D7M12 Part 5C checker — read-only design verification.

Verifies pinned inputs exist with matching SHAs, recomputes the ON
41-row Mac-vs-Odin comparison (priv 41/41, VRAM 3/41, present 0/41,
first divergence tick50), and confirms the a608ed1 source rows that
make the OFF control discriminating.

States plainly: it CANNOT prove OFF behavior. No OFF replay, install,
launch, build, edit, or device action occurs here.

Usage: python3 local/research/N8D7M12P5C/check.py [--self-check]
Exit 0 + verdict A on full pass; OTHER on any pin mismatch.
B is reserved for a source path that would prevent comparison
(none found; documented in REPORT.md).
"""
import hashlib
import json
import os
import re
import sys

REPO = "/Users/brad/dev/ssx3"
WORK = os.path.expanduser("~/dev/ssx3-work")
FORK = os.path.join(WORK, "N8D7M12P2/PS2Recomp")  # @ a608ed1

PINS = {
    "apk": {"path": os.path.join(WORK, "N8D7M12P3/app-release.apk"),
            "sha": "caa1110297dc413d3b04e7442873e0fb5d5624af8417e1e30537d76184d5f512",
            "size": 153753116},
    "stream": {"path": os.path.join(WORK, "N8D7M6/n8d7m6.gs"),
               "sha": "f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593",
               "size": 1100696462},
    "mac_binary": {"path": os.path.join(WORK, "N8D7M12/build/ps2xTest/ps2x_tests"),
                   "sha": "2a0446e89f8fc0cec621cd1f53adf81c1ba8b95940f8ac2cc041729887268ae5",
                   "size": None},
    "mac_hashes": {"path": os.path.join(WORK, "N8D7M12/mac-parallel/parallel.hashes"),
                   "sha": "94b433dfcbebc3b7a9fd57e85c8ce049969a1d8314e2d2d0b1a357773a10c290",
                   "size": 2686},
    "mac_ppm": {"path": os.path.join(WORK, "N8D7M12/mac-parallel/vq-002050.ppm"),
                "sha": "9490484c50ff604d709c7c429f50af10f8da28ee9c0ccb2c7fde2619a14fce3e",
                "size": None},
    "odin_hashes": {"path": os.path.join(WORK, "N8D7M12P5A/parallel.hashes"),
                    "sha": "0e89a493764096ade2c2cc94cdb610c5a0fbf643378e5cffb98cf02a68f2c82a",
                    "size": 2686},
    "odin_ppm": {"path": os.path.join(WORK, "N8D7M12P5A/vq-002050.ppm"),
                 "sha": "39b70d677651f08d702c7e0460a71dff8905aad639797b1b5b23540025350d41",
                 "size": 688143},
}

# (file-rel-fork, [literal substrings that must all be present])
SOURCE_ROWS = [
    ("ps2xRuntime/src/main.cpp",
     ["PS2X_GS_REPLAY_ONDEVICE", "ps2x_gs_replay_run()", "[n8d7m12] replay ok:"]),
    ("ps2xRuntime/src/lib/gs/gs_replay_core.cpp",
     ["PS2X_GS_REPLAY_PPM_TICKS", "ps2_vq::dumpPpm(dir, tick, frame)",
      "GB4_FRAME tick=", "GB4_REPLAY tick=",
      "PS2X_GS_REPLAY_OUT", "GB4_REPLAY_SUMMARY"]),
    ("ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp",
     ["PS2X_N8D5_TILE_CAPTURE", "PS2X_N8D7F_SELECTED_CAPTURE",
      "request.vsyncTick == 2050u", "PS2X_N8D7L_ORACLE",
      "[n8d5b] raw_tile_counts="]),
    ("ps2xTest/src/ps2_gs_replay_tests.cpp", ["PS2X_GS_REPLAY_CAPTURE"]),
]

ROW_RE = re.compile(r"GB4_REPLAY tick=(\d+) vram=([0-9a-f]+) priv=([0-9a-f]+) present=([0-9a-f]+)")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    results = []
    verdict = "A"

    def check(name, ok, detail=""):
        results.append({"name": name, "ok": bool(ok), "detail": detail})
        return bool(ok)

    # 1. fork rev pin
    rev = ""
    rev_file = os.path.join(FORK, ".git")
    if os.path.isdir(FORK):
        import subprocess
        try:
            rev = subprocess.run(["git", "-C", FORK, "rev-parse", "HEAD"],
                                 capture_output=True, text=True, timeout=30).stdout.strip()
        except Exception as e:
            rev = "error:%s" % e
    if not check("fork_rev_a608ed1", rev.startswith("a608ed1"), rev):
        verdict = "OTHER"

    # 2. pinned files: one fresh SHA (+size) each; stream gets two reads
    for key, pin in PINS.items():
        p = pin["path"]
        if not os.path.isfile(p):
            check("pin_%s_exists" % key, False, p)
            verdict = "OTHER"
            continue
        reads = 2 if key == "stream" else 1
        shas = [sha256(p) for _ in range(reads)]
        ok = all(s == pin["sha"] for s in shas)
        size = os.path.getsize(p)
        if pin["size"] is not None and size != pin["size"]:
            ok = False
        check("pin_%s_sha%s" % (key, "_x2" if reads == 2 else ""),
              ok, "%s size=%d" % (shas[0][:12], size))
        if not ok:
            verdict = "OTHER"

    # 3. ON 41-row comparison recomputed from the two pinned hash files
    try:
        mac = [l.strip() for l in open(PINS["mac_hashes"]["path"]) if l.strip()]
        od = [l.strip() for l in open(PINS["odin_hashes"]["path"]) if l.strip()]
        mm = [ROW_RE.match(l) for l in mac]
        oo = [ROW_RE.match(l) for l in od]
        assert all(x is not None for x in mm) and all(x is not None for x in oo)
        assert len(mm) == 41 and len(oo) == 41
        m = [x.groups() for x in mm if x is not None]
        o = [x.groups() for x in oo if x is not None]
        priv_eq = sum(1 for a, b in zip(m, o) if a[0] == b[0] and a[2] == b[2])
        vram_eq = sum(1 for a, b in zip(m, o) if a[1] == b[1])
        pres_eq = sum(1 for a, b in zip(m, o) if a[3] == b[3])
        first_div = next((a[0] for a, b in zip(m, o) if a[1] != b[1]), None)
        vram_ticks = [a[0] for a, b in zip(m, o) if a[1] == b[1]]
        det = "priv=%d/41 vram=%d/41@%s present=%d/41 first_div=%s" % (
            priv_eq, vram_eq, ",".join(vram_ticks), pres_eq, first_div)
        ok = (priv_eq == 41 and vram_eq == 3 and pres_eq == 0 and first_div == "50"
              and m[-1][0] == "2050" and o[-1][0] == "2050"
              and m[-1][3] == "d19b96fe" and o[-1][3] == "b167a719")
        if not check("on_comparison_41rows", ok, det):
            verdict = "OTHER"
    except Exception as e:
        check("on_comparison_41rows", False, "parse error: %s" % e)
        verdict = "OTHER"

    # 4. ON result.json markers agree (packets/priv/transfers/markers + frame present)
    try:
        r = json.load(open(os.path.join(WORK, "N8D7M12P5A/result.json")))
        mk, probe = r["markers"], r["probe"]
        ok = (mk["summary"] == ["queue", "parallel", "862958", "11499", "25445", "2050"]
              and mk["frame"] == ["2050", "parallel", "ff21", "b167a719"]
              and probe["selected"]["input"][2] == "14"
              and probe["vectors"]["input"]["sha256"].startswith("3c69b421"))
        if not check("on_result_json", ok, "verdict=%s" % r.get("verdict")):
            verdict = "OTHER"
    except Exception as e:
        check("on_result_json", False, "parse error: %s" % e)
        verdict = "OTHER"

    # 5. source rows present at the pinned fork
    for rel, needles in SOURCE_ROWS:
        p = os.path.join(FORK, rel)
        try:
            text = open(p).read()
            missing = [n for n in needles if n not in text]
            if not check("src_%s" % os.path.basename(rel), not missing,
                         "missing=%s" % missing if missing else "all %d rows" % len(needles)):
                verdict = "OTHER"
        except Exception as e:
            check("src_%s" % os.path.basename(rel), False, str(e))
            verdict = "OTHER"

    # 6. REPORT lease plan uses the real CLI (no hardcoded slot).
    try:
        rep = open(os.path.join(REPO, "local/research/N8D7M12P5C/REPORT.md")).read()
        ok = ('`claim <label>`' in rep
              and 'release "$SLOT"' in rep
              and 'p_lane_lease.py:19,70-75' in rep
              and re.search(r"p_lane_lease\.py (claim|release) \d", rep) is None)
        if not check("report_lease_cli", ok, "dynamic slot + trap/finally release"):
            verdict = "OTHER"
    except Exception as e:
        check("report_lease_cli", False, str(e))
        verdict = "OTHER"

    # 7. OFF-behavior disclaimer: this checker proves nothing about OFF.
    check("off_behavior_unproved", True,
          "no OFF replay/install/launch executed; OFF predictions are design only")

    passed = sum(1 for r in results if r["ok"])
    out = {"verdict": verdict, "passed": passed, "total": len(results),
           "results": results,
           "note": "A = pins + ON comparison + source rows hold; OFF behavior unproved by design."}
    with open(os.path.join(REPO, "local/research/N8D7M12P5C/check-result.json"), "w") as f:
        json.dump(out, f, indent=1)
    print("verdict=%s %d/%d" % (verdict, passed, len(results)))
    for r in results:
        print(("PASS " if r["ok"] else "FAIL ") + r["name"] + " " + r["detail"])
    return 0 if verdict == "A" else 1


if __name__ == "__main__":
    sys.exit(main())
