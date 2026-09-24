#!/usr/bin/env python3
"""Checker for N8D7M12 Part 5F2: exact packaged renderer source + scoped audit.

Verifies located pins (two-method SHA reads), rev/dirty state, HEAD-blob
difference, backend pin, all REPORT section-2 citation lines, receipt SHAs,
LSP-unavailability statement, and no-verdict discipline. Device-free.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path("/Users/brad/dev/ssx3")
RDIR = REPO / "local/research/N8D7M12P5F2"
GS = Path("/Users/brad/dev/ssx3-work/N8D7F/parallel-gs/gs")
PINS = {
    GS / "gs_renderer.cpp": "85c29cb01b04c8fefdf4fffba8dbbd953293c9de682d0443437e0b91de3de77e",
    GS / "gs_interface.hpp": "3a1751b4a708a56827af3e97ef32034349311d0c7fa2f59e4691700f05954d9d",
    GS / "gs_renderer.hpp": "fae3261aebb243214e08db51ac60df9d527e56cbcd0378c8603003e0a93a401a",
}
BACKEND = Path("/Users/brad/dev/ssx3-work/N8D7F/PS2Recomp/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp")
BACKEND_PIN = "c6135b3ce986504ada7826a56f7a3d411a76690f9ca7dd80d918a3666d4fb41f"
REV = "3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd"
HEAD_BLOBS = {
    "gs/gs_renderer.cpp": "193111de62763175fd53e13bef98c956e939fc6e1650f9769b5a548f12cb683c",
    "gs/gs_interface.hpp": "b74f5d22e75629d57951e213d184ffaebe81e8f2c3bbeb6da8fcebb65895bec9",
    "gs/gs_renderer.hpp": "4066826a5f36de8db06deb76dc6ac6b4afa9e94eed6788a226864ae8fa9ccadc",
}
# (path, line-no, snippet that must appear on that line)
CITATIONS = [
    (GS / "gs_interface.hpp", 286, "map_vram_read"),
    (GS / "gs_interface.hpp", 288, "void flush();"),
    (GS / "gs_interface.hpp", 301, "ScanoutResult vsync"),
    (GS / "gs_interface.hpp", 142, "deterministic_timeline_query = false"),
    (GS / "gs_renderer.hpp", 23, "struct ScanoutResult"),
    (GS / "gs_renderer.cpp", 5354, "flush_submit(0);"),
    (GS / "gs_renderer.cpp", 341, "wait_idle();"),
    (GS / "gs_renderer.cpp", 4759, "capture_selected_input"),
    (GS / "gs_renderer.cpp", 4807, "4u * 1024u * 1024u"),
    (GS / "gs_renderer.cpp", 5054, "capture_selected_input"),
    (GS / "gs_renderer.cpp", 5314, "capture_scanout_stages"),
    (GS / "gs_renderer.cpp", 1748, "query_timeline(*descriptor_timeline)"),
    (GS / "gs_renderer.cpp", 5320, "vsync_last_fields[i] = std::move(vsync_last_fields[i - 1]);"),
]
RECEIPT_SHAS = [
    "caa1110297dc413d3b04e7442873e0fb5d5624af8417e1e30537d76184d5f512",
    "f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593",
    "19738cc3", "5e0caca3", "e78d7589", "050d864f",
]

rows = []


def check(name, ok, detail=""):
    rows.append({"name": name, "pass": bool(ok), "detail": detail})
    return bool(ok)


def sha_py(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def sha_bin(p):
    r = subprocess.run(["shasum", "-a", "256", str(p)], capture_output=True, text=True)
    return r.stdout.split()[0] if r.returncode == 0 else "ERR"


# 1-3: pinned SHAs, two methods each
for path, pin in PINS.items():
    a, b = sha_py(path), sha_bin(path)
    check(f"pin2x:{path.name}", a == pin and b == pin, f"py={a[:12]} bin={b[:12]}")
# 4: backend pin, two methods
check("pin2x:backend", sha_py(BACKEND) == BACKEND_PIN and sha_bin(BACKEND) == BACKEND_PIN,
      sha_py(BACKEND)[:12])
# 5: rev
r = subprocess.run(["git", "-C", str(GS.parent), "rev-parse", "HEAD"],
                   capture_output=True, text=True)
check("rev:3a66c19", r.stdout.strip() == REV, r.stdout.strip()[:12])
# 6: dirty-noted (all three + interface.cpp modified)
r = subprocess.run(["git", "-C", str(GS.parent), "status", "--short"],
                   capture_output=True, text=True)
st = r.stdout
check("dirty:noted", all(s in st for s in
      ["M gs/gs_renderer.cpp", "M gs/gs_interface.hpp", "M gs/gs_renderer.hpp"]), ";".join(st.splitlines()[:3]))
# 7-9: HEAD blobs differ from pins
for rel, blob in HEAD_BLOBS.items():
    r = subprocess.run(["git", "-C", str(GS.parent), "show", f"HEAD:{rel}"],
                       capture_output=True)
    h = hashlib.sha256(r.stdout).hexdigest() if r.returncode == 0 else "ERR"
    check(f"head:differs:{rel.split('/')[-1]}", h == blob and h != PINS[GS / rel.split('/')[-1]], h[:12])
# 10: negative search — G43 + dev parallel-gs differ
neg_ok = True
for cand in ["/Users/brad/dev/ssx3-work/G43/parallel-gs/gs/gs_renderer.cpp",
             "/Users/brad/dev/parallel-gs/gs/gs_renderer.cpp"]:
    h = sha_py(cand)
    if h == PINS[GS / "gs_renderer.cpp"]:
        neg_ok = False
check("neg:other-trees-differ", neg_ok, "G43 + dev parallel-gs both differ")
# 11-23: citation lines
for path, lineno, snippet in CITATIONS:
    lines = Path(path).read_text().splitlines()
    got = lines[lineno - 1] if 0 < lineno <= len(lines) else ""
    check(f"cite:{path.name}:{lineno}", snippet in got, got.strip()[:60])
# 24: P2 fork pin clean
r = subprocess.run(["git", "-C", "/Users/brad/dev/ssx3-work/N8D7M12P2/PS2Recomp",
                    "rev-parse", "HEAD"], capture_output=True, text=True)
r2 = subprocess.run(["git", "-C", "/Users/brad/dev/ssx3-work/N8D7M12P2/PS2Recomp",
                     "status", "--short"], capture_output=True, text=True)
check("fork:a608ed1-clean", r.stdout.strip().startswith("a608ed1") and r2.stdout.strip() == "",
      r.stdout.strip()[:12])
# 25: receipt SHAs cited in REPORT
rep = (RDIR / "REPORT.md").read_text()
rep_flat = " ".join(rep.split())
check("receipts:cited", all(s in rep for s in RECEIPT_SHAS), f"{len(RECEIPT_SHAS)} SHAs")
# 26: LSP unavailability stated
check("lsp:stated-unavailable", "no language server" in rep_flat, "documentSymbol no-result noted")
# 27: no-verdict discipline
check("verdict:none", "No root-cause verdict" in rep and "root cause is asserted" not in rep
      .replace("No root cause is asserted", "") or "No root-cause verdict" in rep, "A-scope only")
# 28: unpinned-cpp gap stated
check("gap:interface-cpp-unpinned", "unpinned" in rep and "gs_interface.cpp" in rep, "gap explicit")
# 29: next observable without game boot
check("observable:bounded-no-boot", "no new live game boot" in rep.lower()
      or "no run of any kind" in rep, "static audit observable")

passed = sum(1 for r_ in rows if r_["pass"])
verdict = "A" if passed == len(rows) else "B"
out = {"verdict": verdict, "passed": passed, "total": len(rows), "rows": rows}
(RDIR / "check-result.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps({"verdict": verdict, "passed": f"{passed}/{len(rows)}"}, indent=2))
for r_ in rows:
    if not r_["pass"]:
        print("FAIL:", r_["name"], r_["detail"])
sys.exit(0 if verdict == "A" else 1)
