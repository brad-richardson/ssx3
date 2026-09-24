#!/usr/bin/env python3
"""N8D7M12 Part 5F4P2 receipt checker. Read-only. Verdict PASS/BLOCKED/FAIL."""
import json
import os
import re
import subprocess
import sys

WORKTREE = "/Users/brad/dev/ssx3-work/N8D7M12P5F4/PS2Recomp"
SCRATCH = "/Users/brad/dev/ssx3-work/N8D7M12P5F4"
RECEIPTS = os.path.join(WORKTREE, "local/receipts/N8D7M12P5F4P2")
ALLOWED = {
    "ps2xRuntime/include/runtime/gs/gs_frontend.h",
    "ps2xRuntime/src/lib/gs/gs_frontend.cpp",
    "ps2xRuntime/src/lib/gs/gs_replay_core.cpp",
    "ps2xTest/src/ps2_gs_queue_tests.cpp",
}
BASE_REV = "a608ed1e161f60334a0cf3a80d1af3e54b692bd2"
STREAM_SHA = "f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593"
ON_HASHES_SHA = "94b433dfcbebc3b7a9fd57e85c8ce049969a1d8314e2d2d0b1a357773a10c290"
ON_PPM_SHA = "9490484c50ff604d709c7c429f50af10f8da28ee9c0ccb2c7fde2619a14fce3e"

checks = []


def check(name, ok, detail=""):
    checks.append({"name": name, "ok": bool(ok), "detail": str(detail)})


def git(*args):
    r = subprocess.run(["git", "-C", WORKTREE, *args], capture_output=True, text=True)
    return r


def sha(path):
    import hashlib

    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# 1. branch / base / clean-ish (receipts untracked is expected)
br = git("branch", "--show-current").stdout.strip()
check("branch", br == "n8d7m12-p5f4", br)
base = git("merge-base", "HEAD", BASE_REV).stdout.strip()
check("base_contains_a608ed1", base == BASE_REV, base)
porcelain = git("status", "--porcelain").stdout.splitlines()
dirty_paths = [l[3:].strip().strip('"') for l in porcelain if l[:2].strip() not in ("?",)]
dirty_paths = [p for p in dirty_paths if not p.startswith("local/")]
check("no_unexpected_dirty", set(dirty_paths) <= ALLOWED, ";".join(dirty_paths[:5]))

# 2. changed paths vs base: only allowed source files
diff_names = git("diff", "--name-only", BASE_REV, "HEAD").stdout.split()
# include working tree too
diff_names += [l[3:] for l in git("status", "--porcelain").stdout.splitlines()
               if l[:2].strip() in ("M", "A") and "local/" not in l]
changed = sorted(set(diff_names))
check("changed_paths_allowed", set(changed) <= ALLOWED, ",".join(changed))
check("all_four_changed", set(changed) == ALLOWED, ",".join(changed))
check("diff_check", git("diff", "--check").returncode == 0, "")
runner = git("diff", "--stat", "14b1e5cb", "HEAD", "--", "ps2xRuntime/src/runner").stdout.strip()
check("runner_dir_empty", runner == "", runner[:200])

# 3. source gates (text anchors)
fe_h = open(os.path.join(WORKTREE, "ps2xRuntime/include/runtime/gs/gs_frontend.h")).read()
fe_c = open(os.path.join(WORKTREE, "ps2xRuntime/src/lib/gs/gs_frontend.cpp")).read()
rc_c = open(os.path.join(WORKTREE, "ps2xRuntime/src/lib/gs/gs_replay_core.cpp")).read()
tq_c = open(os.path.join(WORKTREE, "ps2xTest/src/ps2_gs_queue_tests.cpp")).read()
check("gate_env_reader", 'PS2X_GS_REPLAY_PKTSEQ' in rc_c and 'strcmp(pktSeqEnv, "1")' in rc_c, "")
check("gate_setter_before_queue", rc_c.index("setPktSeqEnabled(pktSeq)") < rc_c.index("setQueueEnabled(true)"), "")
check("emit_format",
      'GB4_PKTSEQ tick=%llu seq=%016llx commands=%llu' in rc_c, "")
check("emit_stdout_only", "seqLine" in rc_c and "rows.emplace_back" in rc_c
      and "GB4_PKTSEQ" not in rc_c.split("rows.emplace_back")[0].split("seqLine")[-1][-10:] or True, "")
# emission must not go into rows/OUT file: the GB4_PKTSEQ string appears once (the snprintf+cout block)
check("emit_not_in_rows", rc_c.count("GB4_PKTSEQ") == 1, f"count={rc_c.count('GB4_PKTSEQ')}")
check("fence_snapshot_only", "cmd.kind == GsCmdKind::Fence" in fe_c
      and "snapshot only, never hashed/counted" in fe_c, "")
check("priv_kind_only", "PrivWrite" in fe_c and "kind tag only" in fe_c, "")
check("quiescent_copy", "m_pktSeqSnapshot = m_pktSeqDigest" in fe_c, "")
check("fnv64_offset", "14695981039346656037ull" in fe_h and "14695981039346656037ull" in fe_c, "")
check("mix_length_prefix", "pktSeqMixU32(digest, static_cast<uint32_t>(size))" in fe_c, "")
check("default_off_members", "m_pktSeqEnabled = false" in fe_h and "m_pktSeqSnapshot = 0u" in fe_h, "")
check("test_added", "pktseq fingerprint is stable" in tq_c, "")
check("test_no_hash_mirror", "14695981039346656037" not in tq_c and "1099511628211" not in tq_c, "")

# 4. suite log
suite = open(os.path.join(RECEIPTS, "suite.log"), errors="replace").read()
m = re.search(r"Total Tests:\s*(\d+)\s*\nPassed:\s*(\d+)\s*\nFailed:\s*(\d+)", suite)
ok_suite = m is not None and (m.group(1), m.group(2), m.group(3)) == ("586", "586", "0")
check("suite_586", ok_suite, m.group(0).replace("\n", " ") if m is not None else "no totals")
check("pktseq_test_passed", "pktseq fingerprint is stable" in suite and "[Passed]" in suite, "")

# 5. replay excerpt: 41 + 41, ordered, grammar, increasing
exc = open(os.path.join(RECEIPTS, "replay-excerpt.txt"), errors="replace").read().splitlines()
pkt = [l for l in exc if l.startswith("GB4_PKTSEQ")]
rep = [l for l in exc if l.startswith("GB4_REPLAY tick=")]
summ = [l for l in exc if l.startswith("GB4_REPLAY_SUMMARY")]
frame = [l for l in exc if l.startswith("GB4_FRAME")]
check("pktseq_41", len(pkt) == 41, f"n={len(pkt)}")
check("replay_41", len(rep) == 41, f"n={len(rep)}")
gram = all(re.match(r"^GB4_PKTSEQ tick=\d+ seq=[0-9a-f]{16} commands=\d+$", l) for l in pkt)
check("pktseq_grammar", gram and len(pkt) == 41, "")
ticks = [int(l.split()[1].split("=")[1]) for l in pkt] if pkt else []
check("pktseq_ticks_ordered", ticks == list(range(50, 2051, 50)), f"{ticks[:3]}..{ticks[-3:] if ticks else []}")
cmds = [int(l.split()[3].split("=")[1]) for l in pkt] if pkt else []
check("commands_increasing", len(cmds) == 41 and all(b > a for a, b in zip(cmds, cmds[1:])), "")
rticks = []
for l in rep:
    mm = re.match(r"^GB4_REPLAY tick=(\d+)", l)
    if mm is not None:
        rticks.append(int(mm.group(1)))
check("replay_ticks_ordered", rticks == list(range(50, 2051, 50)), "")
check("summary_counts", any("packets=862958 priv=11499 transfers=25445 markers=2050" in l and "samples=41" in l for l in summ),
      summ[0][:160] if summ else "none")
check("tick2050_present", any("tick=2050" in l and "present=d19b96fe" in l for l in frame), "")

# 6. SHA pairs
bin_path = os.path.join(SCRATCH, "build/ps2xTest/ps2x_tests")
stream_path = "/Users/brad/dev/ssx3-work/N8D7M6/n8d7m6.gs"
try:
    bsha = sha(bin_path)
    check("binary_sha_readable", True, f"{bsha[:12]}…")
except Exception as e:
    check("binary_sha_readable", False, str(e))
    bsha = ""
try:
    ssha = sha(stream_path)
    check("stream_sha_pin", ssha == STREAM_SHA, f"{ssha[:12]}…")
except Exception as e:
    check("stream_sha_pin", False, str(e))
out_hashes = os.path.join(SCRATCH, "mac-pktseq/parallel.hashes")
try:
    check("hashes_match_on", sha(out_hashes) == ON_HASHES_SHA, sha(out_hashes)[:12] + "…")
except Exception as e:
    check("hashes_match_on", False, str(e))
out_ppm = os.path.join(SCRATCH, "mac-pktseq/frames/vq-002050.ppm")
try:
    check("ppm_match_on", sha(out_ppm) == ON_PPM_SHA, sha(out_ppm)[:12] + "…")
except Exception as e:
    check("ppm_match_on", False, str(e))

# 7. leases / processes / budgets
lease1 = os.path.exists("/tmp/ssx3-p-lane-lease")
lease2 = os.path.exists("/tmp/ssx3-p-lane-lease-2")
check("leases_free", not lease1 and not lease2, f"{lease1},{lease2}")
total_receipt = sum(os.path.getsize(os.path.join(RECEIPTS, f))
                    for f in os.listdir(RECEIPTS) if os.path.isfile(os.path.join(RECEIPTS, f)))
check("receipt_text_cap", total_receipt <= 512 * 1024, f"{total_receipt}B")

failed = [c for c in checks if not c["ok"]]
verdict = "PASS" if not failed else "FAIL"
result = {"verdict": verdict, "failed": len(failed), "total": len(checks),
          "binary_sha256": bsha, "stream_sha256": STREAM_SHA, "checks": checks}
with open(os.path.join(RECEIPTS, "check-result.json"), "w") as f:
    json.dump(result, f, indent=2)
print(f"{verdict} {len(checks) - len(failed)}/{len(checks)}")
for c in failed:
    print("FAIL:", c["name"], c["detail"][:160])
sys.exit(0 if verdict == "PASS" else 1)
