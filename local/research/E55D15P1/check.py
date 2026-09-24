#!/usr/bin/env python3
"""E55D15P1 checker: re-verify pinned inventory claims (read-only pins only)."""
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
REP = REPO / "local/research/E55D15P1/REPORT.md"
MC = Path("/Users/brad/dev/PS2Recomp/ps2xRuntime/src/lib/Kernel/Stubs/MemoryCard.cpp")

fails = []


def check(name, cond, detail=""):
    print(("PASS" if cond else "FAIL"), name, detail)
    if not cond:
        fails.append(name)


text = REP.read_text()
check("report-exists", REP.exists())
check("report-size-cap-256k", REP.stat().st_size < 256 * 1024, f"{REP.stat().st_size}B")
check("outcome-B-declared", re.search(r"Predeclared outcome:\s*\*\*B\*\*", text) is not None)
check("outcome-B-in-sec7", re.search(r"## 7\. Outcome.*\n\n\*\*B\*\*", text) is not None)
check("candidate-table-4-rows", all(f"| C{i} |" in text for i in (1, 2, 3, 4)))
check("no-candidate-sha-plainly-na",
      "no SHA is pinned" in text and "no candidate is later used" in text)
check("no-raw-bytes", "no raw save bytes seen or recorded" in text)
check("share-gap-stated", "/Volumes/share` is not mounted" in text)
check("no-invented-save", "not a valid save" in text)
check("design-input-not-proof",
      "not** proof the guest accepts" in text or "not proof the guest accepts" in text)
check("source-lines-cited", all(s in text for s in
      ["getMcRootPath` (:118-155)", "normalizeGuestMcPathLocked` (:210-246)",
       "guestMcPathToHostPath` (:248-256)", "sceMcGetDir` (:706-770)"]))
check("lsp-denial-noted", "no usable server" in text)
check("tick1740-pattern", "BASLUS-20772-GAM*" in text)
check("extraction-na", "no whole-card image candidate was found locally" in text)
check("next-observation", "Smallest next observation" in text)
check("zero-boots", "Boots/builds/runs: 0" in text)

# Live re-verification of source anchors (read-only).
mc = MC.read_text()
check("src-getMcRootPath", "std::filesystem::path getMcRootPath(int32_t port)" in mc)
check("src-wildcard-split", "queryRel.parent_path()" in mc)
check("src-hostdir", "std::filesystem::path hostDir = getMcRootPath(port);" in mc)

# Live re-verification: no local card images / BASLUS dirs / save exports.
def find_count(args):
    try:
        out = subprocess.run(args, capture_output=True, text=True, timeout=120)
        return len([l for l in out.stdout.splitlines() if l.strip()])
    except Exception as e:
        check("find-runnable", False, str(e))
        return -1

work = str(Path.home() / "dev/ssx3-work")
inp = str(Path.home() / "dev/ssx3-inputs")
check("live-no-card-images", find_count(
    ["find", work, inp, "-type", "f", "(", "-iname", "*.ps2", "-o",
     "-iname", "*.p2s", "-o", "-iname", "Mcd*.bin", ")"]) == 0)
check("live-no-baslus-dirs", find_count(
    ["find", work, inp, "-type", "d", "-iname", "*BASLUS*"]) == 0)
check("live-no-save-exports", find_count(
    ["find", work, inp, "-type", "f", "(", "-iname", "*.psu", "-o",
     "-iname", "*.cbs", "-o", "-iname", "*.xps", "-o",
     "-iname", "*.sps", "-o", "-iname", "*.npo", ")"]) == 0)

print(f"{len(fails)} failures" if fails else "ALL PASS")
sys.exit(1 if fails else 0)
