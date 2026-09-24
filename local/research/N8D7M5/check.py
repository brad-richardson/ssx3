#!/usr/bin/env python3
"""N8D7M5 scripted acceptance (structure + equality checks; orchestrator gates meaning).

Reads (defaults; override with argv --key value):
  --capture   ~/dev/ssx3-work/N8D4/n8d4.gs
  --scratch   ~/dev/ssx3-work/N8D7M5
  --fork      ~/dev/ssx3-work/N8D7L/PS2Recomp
  --baseline  ~/dev/ssx3-work/N8D4/cpu.hashes   (N8D4 CPU replay rows)
  --words     0x0E0000,0x0E0534,0x0E0040,0x0E2000,0x0F0000,0x0F2000
Verifies: input SHA, runner guard, suite 585, mode=direct, ON/OFF hashes +
PPM equality, OFF==baseline tick2050 row, trace ordering/execution witness,
finals, >=2 pages with transitions. Writes check-result.json. Exit 0 PASS,
1 OTHER/FAIL.
"""
import hashlib
import json
import os
import re
import subprocess
import sys

CAPTURE_SHA = "38ace1a3e8e99e1d5d7d24e611dfa9cedd6e6d44a45c800223991401cd93f97d"
HOME = os.path.expanduser("~")
ARGS = {
    "--capture": f"{HOME}/dev/ssx3-work/N8D4/n8d4.gs",
    "--scratch": f"{HOME}/dev/ssx3-work/N8D7M5",
    "--fork": f"{HOME}/dev/ssx3-work/N8D7L/PS2Recomp",
    "--baseline": f"{HOME}/dev/ssx3-work/N8D4/cpu.hashes",
    "--words": "0x0E0000,0x0E0534,0x0E0040,0x0E2000,0x0F0000,0x0F2000",
}
for i in range(1, len(sys.argv) - 1, 2):
    if sys.argv[i] in ARGS:
        ARGS[sys.argv[i]] = sys.argv[i + 1]

res = {"checks": {}, "verdict": "OTHER", "gaps": []}


def check(name, ok, detail=""):
    res["checks"][name] = {"ok": bool(ok), "detail": detail}
    return ok


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


ok_all = True

# 1. input SHA
try:
    got = sha256(ARGS["--capture"])
    ok_all &= check("input_sha", got == CAPTURE_SHA, got)
except OSError as e:
    ok_all &= check("input_sha", False, str(e))

# 2. runner-dir guard
try:
    p = subprocess.run(
        ["git", "diff", "--stat", "14b1e5cb", "HEAD", "--", "ps2xRuntime/src/runner"],
        capture_output=True, text=True, cwd=ARGS["--fork"], timeout=60)
    out = p.stdout.strip()
    ok_all &= check("runner_guard", p.returncode == 0 and out == "", out or "empty")
except Exception as e:
    ok_all &= check("runner_guard", False, str(e))

# 3. suite (flag-OFF): 585 passed from suite log
try:
    with open(os.path.join(ARGS["--scratch"], "suite.log")) as f:
        suite = f.read()
    m_total = re.search(r"Total Tests:\s*(\d+)", suite)
    m_pass = re.search(r"Passed:\s*(\d+)", suite)
    m_fail = re.search(r"Failed:\s*(\d+)", suite)
    suite_ok = bool(m_total and m_pass and m_fail and m_total.group(1) == "585"
                    and m_pass.group(1) == "585" and m_fail.group(1) == "0")
    ok_all &= check("suite", suite_ok,
                    f"total={m_total.group(1) if m_total else None} "
                    f"passed={m_pass.group(1) if m_pass else None} "
                    f"failed={m_fail.group(1) if m_fail else None}")
except OSError as e:
    ok_all &= check("suite", False, str(e))

words = [int(w, 0) for w in ARGS["--words"].split(",") if w.strip()]


def load_run(tag):
    d = {}
    base = ARGS["--scratch"]
    for name in ("hashes", "log", "ppm_sha"):
        p = os.path.join(base, f"{tag}.{name if name != 'ppm_sha' else 'ppm.sha'}")
        try:
            with open(p, "rb" if name == "hashes" else "r") as f:
                d[name] = f.read()
        except OSError as e:
            d[name] = None
            d[name + "_err"] = str(e)
    return d


off, on = load_run("off"), load_run("on")

# 4a. hashes byte-identical
h_ok = (off["hashes"] is not None and on["hashes"] is not None
        and off["hashes"] == on["hashes"])
ok_all &= check("on_off_hashes_equal", h_ok,
                f"off={None if off['hashes'] is None else len(off['hashes'])}B "
                f"on={None if on['hashes'] is None else len(on['hashes'])}B")

# 4b. PPM SHA equal (compare hash token only; filenames may differ)
def _tok(s):
    return (s or "").strip().split()[0] if (s or "").strip() else ""


p_ok = bool(off["ppm_sha"] is not None and on["ppm_sha"] is not None
            and _tok(off["ppm_sha"]) == _tok(on["ppm_sha"]) and _tok(off["ppm_sha"]))
ok_all &= check("on_off_ppm_equal", p_ok, _tok(off.get("ppm_sha") or "")[:16])

# 4c. OFF tick2050 row == N8D4 cpu baseline
try:
    with open(ARGS["--baseline"]) as f:
        base_rows = [l for l in f.read().splitlines() if "tick=2050" in l]
    off_rows = (off["hashes"].decode().splitlines()
                if off["hashes"] is not None else [])
    off2050 = [l for l in off_rows if "tick=2050" in l]
    ok_all &= check("off_matches_n8d4_cpu2050",
                    len(base_rows) == 1 and off2050 == base_rows,
                    f"off={off2050} base={base_rows}")
except OSError as e:
    ok_all &= check("off_matches_n8d4_cpu2050", False, str(e))

# 4d. mode=direct in both summaries (execution-witness precondition)
def summary_mode(log):
    if log is None:
        return None
    m = re.search(r"GB4_REPLAY_SUMMARY mode=(\w+)", log)
    return m.group(1) if m else None


moff = summary_mode(off["log"] if isinstance(off.get("log"), str) else None)
mon = summary_mode(on["log"] if isinstance(on.get("log"), str) else None)
ok_all &= check("mode_direct_both", moff == "direct" and mon == "direct",
                f"off={moff} on={mon}")

# 5. trace ordering + execution witness (ON log)
WORD_RE = re.compile(
    r"\[n8d7m5\] word idx=(\d+) submit=(\d+) tick=(\d+) path=(\S+) kind=(\S+) "
    r"addr=0x([0-9a-fA-F]+) old=0x([0-9a-fA-F]+) new=0x([0-9a-fA-F]+)")
FINAL_RE = re.compile(r"\[n8d7m5\] final addr=0x([0-9a-fA-F]+) word=0x([0-9a-fA-F]+)")
trace_ok, trace_detail, pages, first_old = True, "", set(), {}
last_idx = -1
n_lines = 0
on_log = on.get("log") if isinstance(on.get("log"), str) else None
if on_log is None:
    trace_ok = False
    trace_detail = "no ON log"
else:
    if "[n8d7m5] truncated" in on_log:
        trace_ok = False
        trace_detail = "trace truncated"
    else:
        for line in on_log.splitlines():
            m = WORD_RE.search(line)
            if not m:
                continue
            n_lines += 1
            idx, submit, tick, path, kind = (int(m.group(1)), int(m.group(2)),
                                             int(m.group(3)), m.group(4), m.group(5))
            addr, old, new = int(m.group(6), 16), int(m.group(7), 16), int(m.group(8), 16)
            if tick > 2050:
                trace_ok = False
                trace_detail = f"tick>2050 at idx={idx}"
                break
            if path in ("1", "2", "3", "native"):
                if submit != idx + 1:
                    trace_ok = False
                    trace_detail = f"submit!=idx+1 at idx={idx} submit={submit}"
                    break
            elif path != "clear":
                trace_ok = False
                trace_detail = f"unknown path {path}"
                break
            if idx < last_idx:
                trace_ok = False
                trace_detail = f"non-monotonic idx {idx} after {last_idx}"
                break
            last_idx = idx
            if old == new:
                trace_ok = False
                trace_detail = f"old==new at idx={idx}"
                break
            if kind == "none":
                trace_ok = False
                trace_detail = f"kind=none at idx={idx} (unattributed write path)"
                break
            pages.add(addr >> 13)
            if addr not in first_old:
                first_old[addr] = old
        trace_detail = trace_detail or f"{n_lines} transitions, pages={sorted(hex(p) for p in pages)}"
ok_all &= check("trace_ordering_witness", trace_ok, trace_detail)

# 6. finals for all watched addrs
finals = {}
if on_log:
    for line in on_log.splitlines():
        m = FINAL_RE.search(line)
        if m:
            finals[int(m.group(1), 16)] = int(m.group(2), 16)
missing = [hex(a) for a in words if a not in finals]
ok_all &= check("post_marker_words", not missing and bool(finals),
                f"finals={len(finals)} missing={missing}")
res["finals"] = {hex(k): hex(v) for k, v in finals.items()}

# 7. >=2 pages with transitions; weak-row flags (first old != 0)
weak = [hex(a) for a, o in first_old.items() if o != 0]
ok_all &= check("two_pages_changed", len(pages) >= 2, f"pages={len(pages)}")
res["weak_rows_first_old_nonzero"] = weak
if weak:
    res["gaps"].append(f"first transition old!=0 (already-nonzero at capture start): {weak}")

changed_addrs = sorted(first_old)
res["changed_addrs"] = [hex(a) for a in changed_addrs]
res["n_transitions"] = n_lines

if not h_ok or moff != "direct" or mon != "direct":
    res["gaps"].append("missing execution-order witness or ON/OFF frame change -> OTHER")

res["verdict"] = "PASS" if ok_all else "OTHER"
out_path = os.path.join("/Users/brad/dev/ssx3/local/research/N8D7M5", "check-result.json")
with open(out_path, "w") as f:
    json.dump(res, f, indent=2)
print(json.dumps(res, indent=2))
sys.exit(0 if ok_all else 1)
