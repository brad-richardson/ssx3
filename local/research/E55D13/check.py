#!/usr/bin/env python3
"""E55D13 checker: verifies source/receipt pins WITHOUT proving guest behavior.

Checks:
 - E55D12 post-choice GetDir pins (tick1740, addr 0x00ba5b20, max6, empty)
   from s1-receipts.txt and, when present, the private probe.log lines.
 - E55D3 probe header noteGetDir signature carries table bytes/status only
   (no rawPath/normalized query/pattern fields).
 - MemoryCard.cpp anchors for normalize/select/copy + mc0/mc1 mapping exist.
 - No grounded save payload is pinned (BASLUS-20772 is a name-only string;
   /SAVEDATA/* is a stub self-test, not game behavior).

It CANNOT prove what guest query the game issued or that any seed is a valid
SSX 3 save: source strings and empty-card receipts cannot prove guest behavior.
Outcome B (no grounded query/seed) is the only grounded reading.

Usage: python3 local/research/E55D13/check.py
Exit 0 on PASS, 1 on FAIL.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]  # ~/dev/ssx3
FORK_MC = Path("/Users/brad/dev/ssx3-work/E55D3/PS2Recomp/ps2xRuntime/src/lib/Kernel/Stubs/MemoryCard.cpp")
FORK_PROBE_H = Path("/Users/brad/dev/ssx3-work/E55D3/PS2Recomp/ps2xRuntime/include/ps2_e55d3_pad_card_probe.h")
FORK_MAIN = Path("/Users/brad/dev/ssx3-work/E55D3/PS2Recomp/ps2xRuntime/src/main.cpp")
E12_RECEIPTS = REPO / "local/research/E55D12/s1-receipts.txt"
E12_PROBE = Path("/Users/brad/dev/ssx3-work/E55D12/run/S1/probe.log")
E55D6_REPORT = REPO / "local/research/E55D6/REPORT.md"
E55D7_STRINGS = REPO / "local/research/E55D7/strings.txt"

FAIL = []


def check(name, ok, detail=""):
    print("%s %s %s" % ("ok" if ok else "FAIL", name, detail))
    if not ok:
        FAIL.append(name)


def main():
    rec = E12_RECEIPTS.read_text()
    check("e12_receipts_exist", E12_RECEIPTS.exists(), str(E12_RECEIPTS))
    for tok in ["1740", "0x00ba5b20", "0x00b85660", "118/122/126/223",
                "ok=0 reason=empty", "mcread n=0", "port=0 slot=0"]:
        check("e12_receipt_has_%s" % tok.replace("/", "_").replace("=", "_"),
              tok in rec, tok[:24])

    if E12_PROBE.exists():
        lines = E12_PROBE.read_bytes().splitlines()
        getdirs = [l for l in lines if l.startswith(b"getdir")]
        check("probe_five_getdir", len(getdirs) == 5, "n=%d" % len(getdirs))
        ticks = []
        for l in getdirs:
            m = re.search(rb"vsync=(\d+)", l)
            ticks.append(int(m.group(1)) if m else -1)
        check("probe_ticks_118_122_126_223_1740", sorted(ticks) == [118, 122, 126, 223, 1740], str(ticks))
        post = [l for l in getdirs if b"vsync=1740" in l]
        check("probe_post_single", len(post) == 1, "n=%d" % len(post))
        if post:
            p = post[0].decode("ascii", "replace")
            check("probe_post_addr", "addr=0x00ba5b20" in p, p[:60])
            check("probe_post_max6", "max=6" in p, p[:60])
            check("probe_post_empty", "ok=0" in p and "reason=empty" in p
                  and p.rstrip().endswith("bytes="), p[:80])
            check("probe_post_no_path_fields",
                  "rawPath=" not in p and "query=" not in p and "pattern=" not in p, "path tap absent by design")
        early = [l for l in getdirs if b"vsync=1740" not in l]
        check("probe_early_addr", all(b"addr=0x00b85660" in l for l in early), "")
        check("probe_early_max6", all(b"max=6" in l for l in early), "")
    else:
        check("probe_private_absent_noted", True, "private lane absent; receipts hold pins")

    h = FORK_PROBE_H.read_text()
    m = re.search(r"void noteGetDir\((.*?)\)", h, re.S)
    check("probe_header_exists", FORK_PROBE_H.exists(), "")
    check("probe_sig_found", m is not None, "")
    if m:
        sig = m.group(1)
        for tok in ["tableAddr", "entryCount", "maxEntries", "copied", "reason", "bytes"]:
            check("probe_sig_has_%s" % tok, tok in sig, "")
        for tok in ["rawPath", "guestQuery", "parentRel", "pattern", "hostDir"]:
            check("probe_sig_no_%s" % tok, tok not in sig, "absent: query unobserved")

    mc = FORK_MC.read_text()
    for tok in ["normalizeGuestMcPathLocked", "guestMcPathToHostPath",
                "wildcardMatch", "fillMcDirTableEntry",
                "sizeof(SceMcTblGetDir) == 64", "getMcRootPath",
                "normalizeGuestMcPathLocked(port, rawPath.empty"]:
        check("mc_has_%s" % tok[:28], tok in mc, "")
    check("mc_mc0_leaf_rewrite", 'lowerLeaf == "mc0"' in mc, "")
    check("mc_empty_means_no_copy", "entryCount == 0u || tableAddr == 0u" in mc, "")
    check("mc_dot_gated_on_pattern", "appendSpecial(\".\")" in mc and "wildcardMatch(pattern, name)" in mc, "")
    check("mc_sort_case_insensitive", "toLowerAscii(lhs.path().filename().string())" in mc, "")
    check("mc_entryname_32", "EntryName[32]" in mc, "")
    main_cpp = FORK_MAIN.read_text()
    check("main_ps2x_mc_root", "PS2X_MC_ROOT" in main_cpp, "")

    r6 = E55D6_REPORT.read_text()
    check("e55d6_baslus_name_only", "BASLUS-20772" in r6, "")
    check("e55d6_payload_unknown",
          ("payload filenames" in r6 and "unknown" in r6) or "Expected card content unknown" in r6, "")
    check("e55d6_savedata_is_selftest", "stub self-test" in r6 and "/SAVEDATA/*" in r6, "")
    s7 = E55D7_STRINGS.read_text() if E55D7_STRINGS.exists() else ""
    check("e55d7_baslus_string", "BASLUS-20772" in s7, "")
    check("no_grounded_seed_bytes_pinned", True,
          "BY-DESIGN: no receipt pins save payload bytes+provenance; a random file is not a valid save")

    check("source_strings_cannot_prove_guest_behavior", True,
          "UNPROVED-BY-CHECKER by design: code/receipt pins cannot prove the guest query or save validity")
    if FAIL:
        print("CHECK FAIL: %s" % ", ".join(FAIL))
        return 1
    print("CHECK PASS: pins hold; query/seed remain unobserved (outcome B)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
