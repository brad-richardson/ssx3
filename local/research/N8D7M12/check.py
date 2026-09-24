#!/usr/bin/env python3
"""N8D7M12 Part 1 acceptance: shared-core desktop parity vs N8D7M6 Mac receipt.

Compares the new shared-core replay log against the pinned N8D7M6 Mac
parallel log (N8D7M5 binary d06ff1aa) field-by-field, plus suite, runner
guard, harness-absence, and word-watch guard proofs. Writes
check-result.json. Exit 0 = A (suite passes and exact-stream output is
byte/field-equal), 1 = B/OTHER with exact diff. Never quotes wall time.
"""
import hashlib
import json
import os
import re
import struct
import subprocess
import sys

HOME = os.path.expanduser("~")
ARGS = {
    "--stream": f"{HOME}/dev/ssx3-work/N8D7M6/n8d7m6.gs",
    "--scratch": f"{HOME}/dev/ssx3-work/N8D7M12",
    "--fork": f"{HOME}/dev/ssx3-work/N8D7M12/PS2Recomp",
    "--base-log": f"{HOME}/dev/ssx3-work/N8D7M6/mac-parallel.log",
    "--base-dir": f"{HOME}/dev/ssx3-work/N8D7M6/mac-parallel",
}
for i in range(1, len(sys.argv) - 1, 2):
    if sys.argv[i] in ARGS:
        ARGS[sys.argv[i]] = sys.argv[i + 1]

STREAM_SHA = "f6a78f71fa1a5f5bb21442ff2c6757a743cd42c5d2d74a108977d8416da4a593"
NEW_LOG = os.path.join(ARGS["--scratch"], "mac-parallel.log")
NEW_DIR = os.path.join(ARGS["--scratch"], "mac-parallel")

res = {"checks": {}, "verdict": "OTHER", "diffs": []}


def check(name, ok, detail=""):
    res["checks"][name] = {"ok": bool(ok), "detail": detail}
    if not ok:
        res["diffs"].append(f"{name}: {detail}")
    return ok


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


ok_all = True

# 1. stream SHA pair
try:
    pair = [sha(ARGS["--stream"]) for _ in range(2)]
    ok_all &= check("stream_sha_pair", pair == [STREAM_SHA] * 2, pair[0][:16])
except OSError as e:
    ok_all &= check("stream_sha_pair", False, str(e))

# 2. runner-dir guard (fork worktree, committed + working tree)
try:
    p = subprocess.run(
        ["git", "diff", "14b1e5cb", "HEAD", "--stat", "--", "ps2xRuntime/src/runner"],
        capture_output=True, text=True, cwd=ARGS["--fork"], timeout=60)
    q = subprocess.run(
        ["git", "status", "--short", "--", "ps2xRuntime/src/runner"],
        capture_output=True, text=True, cwd=ARGS["--fork"], timeout=60)
    empty = p.returncode == 0 and p.stdout.strip() == "" and q.stdout.strip() == ""
    ok_all &= check("runner_guard", empty, "empty" if empty else (p.stdout + q.stdout)[:200])
except Exception as e:
    ok_all &= check("runner_guard", False, str(e))

# 3. suite 585/585 from suite.log
try:
    with open(os.path.join(ARGS["--scratch"], "suite.log")) as f:
        suite = f.read()
    mt = re.search(r"Total Tests:\s*(\d+)", suite)
    mp = re.search(r"Passed:\s*(\d+)", suite)
    mf = re.search(r"Failed:\s*(\d+)", suite)
    sok = bool(mt and mp and mf and mt.group(1) == "585"
               and mp.group(1) == "585" and mf.group(1) == "0")
    ok_all &= check("suite_585", sok, f"total={mt.group(1) if mt else None} "
                    f"passed={mp.group(1) if mp else None} failed={mf.group(1) if mf else None}")
except OSError as e:
    ok_all &= check("suite_585", False, str(e))


def load_log(path):
    with open(path, errors="replace") as f:
        return f.read()


try:
    base = load_log(ARGS["--base-log"])
    new = load_log(NEW_LOG)
    logs_ok = True
except OSError as e:
    base, new, logs_ok = "", "", False
    ok_all &= check("logs_readable", False, str(e))

SEL = (r"\[n8d7f\] tick=(\d+) fbp=(\d+) fbw=(\d+) psm=(\d+) dbx=(\d+) dby=(\d+) "
       r"phase=(\d+) stride=(\d+) mask=(\d+) samples=(\d+) promoted=(\d+)")
BYTES = r"bytes=(\d+) vram_sha256=(\S+) input_sha256=(\S+) circuit_sha256=(\S+)"
VEC = r"(input|circuit|stage|oracle)_tile_counts=([0-9,]+)"
PACKED = r"(input|circuit|stage|oracle) tiles=(\d+) occupied=(\d+) active=(\d+) packed_sha256=(\S+)"


def one(pat, text):
    m = re.search(pat, text)
    return m.groups() if m else None


def tile_values(text, name):
    m = re.search(rf"{name}_tile_counts=([0-9,]+)", text)
    if not m:
        return None
    fields = [f for f in m.group(1).split(",") if f != ""]
    if len(fields) != 448 or not all(f.isdecimal() for f in fields):
        return None
    values = list(map(int, fields))
    return {"occupied": sum(values), "active": sum(v >= 32 for v in values),
            "sha256": hashlib.sha256(struct.pack("<448H", *values)).hexdigest(),
            "values": values}


if logs_ok:
    ok_all &= check("no_parse_error_new", "GB4_REPLAY_PARSE_ERROR" not in new,
                    "clean" if "GB4_REPLAY_PARSE_ERROR" not in new else "parse error present")

    for key in ("packets", "priv", "transfers", "markers", "readbacks", "clears", "samples"):
        b = one(rf"\s{key}=(\d+)", base)
        n = one(rf"\s{key}=(\d+)", new)
        ok_all &= check(f"count_{key}", b is not None and b == n, f"base={b} new={n}")

    for key in ("mode=queue", "backend=parallel"):
        ok_all &= check(f"summary_{key.split('=')[0]}", key in new, key)

    bmk = one(r"markers=(\d+)", base)
    rows = re.findall(r"GB4_REPLAY tick=(\d+) vram=(\S+) priv=(\S+) present=(\S+)", new)
    brows = re.findall(r"GB4_REPLAY tick=(\d+) vram=(\S+) priv=(\S+) present=(\S+)", base)
    last2050 = rows and rows[-1][0] == "2050"
    ok_all &= check("marker2050", bmk == ("2050",) and bool(last2050),
                    f"markers={bmk} last_sampled={rows[-1][0] if rows else None}")

    bstats = one(r"GB4_PARALLEL_STATS packets=(\d+) presents=(\d+) null_scanouts=(\d+) "
                 r"unsupported_clears=(\d+) unsupported_vram_io=(\d+) init_ok=(\d+) init_failed=(\d+)", base)
    nstats = one(r"GB4_PARALLEL_STATS packets=(\d+) presents=(\d+) null_scanouts=(\d+) "
                 r"unsupported_clears=(\d+) unsupported_vram_io=(\d+) init_ok=(\d+) init_failed=(\d+)", new)
    ok_all &= check("parallel_stats", bstats is not None and bstats == nstats, str(nstats))

    bf = one(r"(GB4_FRAME tick=2050 backend=parallel pmode=\S+ dispfb1=\S+ dispfb2=\S+ "
             r"display_fbp=\S+ source_fbp=\S+ preferred=\S+ present=\S+)", base)
    nf = one(r"(GB4_FRAME tick=2050 backend=parallel pmode=\S+ dispfb1=\S+ dispfb2=\S+ "
             r"display_fbp=\S+ source_fbp=\S+ preferred=\S+ present=\S+)", new)
    ok_all &= check("frame_line", bf is not None and bf == nf, (nf[0] if nf else "none"))

    bsel, nsel = one(SEL, base), one(SEL, new)
    ok_all &= check("selected11", bsel is not None and bsel == nsel, str(nsel))

    bby, nby = one(BYTES, base), one(BYTES, new)
    ok_all &= check("bytes_hashes", bby is not None and bby == nby, str(nby))

    for name in ("input", "circuit", "stage", "oracle"):
        bp = one(rf"{name} tiles=(\d+) occupied=(\d+) active=(\d+) packed_sha256=(\S+)", base)
        np_ = one(rf"{name} tiles=(\d+) occupied=(\d+) active=(\d+) packed_sha256=(\S+)", new)
        ok_all &= check(f"packed_{name}", bp is not None and bp == np_, str(np_))
        bv, nv = tile_values(base, name), tile_values(new, name)
        veq = (bv is not None and nv is not None and bv["values"] == nv["values"]
               and bv["sha256"] == nv["sha256"] == (bp[3] if bp else None))
        ok_all &= check(f"vector_{name}", veq,
                        f"occ={nv['occupied'] if nv else None} act={nv['active'] if nv else None} "
                        f"sha={(nv['sha256'][:16] + '...') if nv else None}")

    bctl = one(r"\[n8d7l\] oracle_controls=(\S+)", base)
    nctl = one(r"\[n8d7l\] oracle_controls=(\S+)", new)
    ok_all &= check("oracle_controls", bctl is not None and bctl == nctl,
                    (nctl[0][:60] + "...") if nctl else "none")
    beq = one(r"oracle_input_equal=(\d+)/448", base)
    neq = one(r"oracle_input_equal=(\d+)/448", new)
    ok_all &= check("oracle_equal", beq == ("448",) and neq == ("448",), str(neq))

    b2050 = [r for r in brows if r[0] == "2050"]
    n2050 = [r for r in rows if r[0] == "2050"]
    ok_all &= check("replay2050_row", len(b2050) == 1 and b2050 == n2050, str(n2050))

# parallel.hashes byte equality
try:
    bh = open(os.path.join(ARGS["--base-dir"], "parallel.hashes"), "rb").read()
    nh = open(os.path.join(NEW_DIR, "parallel.hashes"), "rb").read()
    ok_all &= check("hashes_file", bh == nh, f"{len(nh)}B")
except OSError as e:
    ok_all &= check("hashes_file", False, str(e))

# tick2050 PPM byte equality
try:
    bp = sha(os.path.join(ARGS["--base-dir"], "vq-002050.ppm"))
    np_ = sha(os.path.join(NEW_DIR, "vq-002050.ppm"))
    ok_all &= check("ppm2050", bp == np_, f"{bp[:16]} vs {np_[:16]}")
except OSError as e:
    ok_all &= check("ppm2050", False, str(e))

# no harness string in runtime sources
try:
    p = subprocess.run(["rg", "-l", "MiniTest", "ps2xRuntime"],
                       capture_output=True, text=True, cwd=ARGS["--fork"], timeout=60)
    hits = [h for h in p.stdout.splitlines() if "_deps" not in h and "/build/" not in h]
    ok_all &= check("no_harness_in_runtime", hits == [], ";".join(hits) or "none")
except Exception as e:
    ok_all &= check("no_harness_in_runtime", False, str(e))

# guard ON: TU compile command carries the flag (compile proof)
try:
    cc = json.load(open(os.path.join(ARGS["--scratch"], "build", "compile_commands.json")))
    entry = next(x for x in cc if x["file"].endswith("ps2xRuntime/src/lib/gs/gs_replay_core.cpp"))
    ok_all &= check("guard_on_flag", "-DPS2X_GS_REPLAY_WORD_WATCH=1" in entry["command"], "TU-scoped")
except Exception as e:
    ok_all &= check("guard_on_flag", False, str(e))

# guard OFF: preprocessed TU has no active watch dependency
try:
    pre = open(os.path.join(ARGS["--scratch"], "guard-off.i"), errors="replace").read()
    dead = ["PS2X_GS_REPLAY_WORDS", "watchAddrs", "snapshotWords", "emitWordLine",
            "kN8D7M5LineCap"]
    absent = all(s not in pre for s in dead)
    ok_all &= check("guard_off_absent", absent,
                    "clean" if absent else ",".join(s for s in dead if s in pre))
    low = [l.strip() for l in pre.splitlines() if "n8d7m5" in l]
    ok_all &= check("guard_off_no_emit", low == [], ";".join(low[:3]) or "none")
    decls = [l.strip() for l in pre.splitlines() if "ps2xN8D7M5" in l]
    decl_only = len(decls) == 2 and all(d.endswith(";") for d in decls)
    ok_all &= check("guard_off_decls_only", decl_only, f"{len(decls)} declaration lines")
except OSError as e:
    ok_all &= check("guard_off_absent", False, str(e))
    ok_all &= check("guard_off_no_emit", False, str(e))
    ok_all &= check("guard_off_decls_only", False, str(e))

# word-watch preserved verbatim: guarded regions subset of pre-change test file
try:
    base_src = subprocess.run(
        ["git", "show", "a8cfefa:ps2xTest/src/ps2_gs_replay_tests.cpp"],
        capture_output=True, text=True, cwd=ARGS["--fork"], timeout=60).stdout
    base_lines = {" ".join(l.split()) for l in base_src.splitlines() if l.strip()}
    # Expected assert→result conversions (same as unguarded regions): the
    # wordsOk failure return replaces t.IsTrue(false,...)+return.
    allow = {"result.wordsOk = false;", "return result;"}
    core = open(os.path.join(ARGS["--fork"], "ps2xRuntime/src/lib/gs/gs_replay_core.cpp"),
                errors="replace").read().splitlines()
    depth, region, missing = 0, [], []
    for l in core:
        s = l.strip()
        if s.startswith("#ifdef PS2X_GS_REPLAY_WORD_WATCH"):
            depth += 1
            continue
        if s.startswith("#endif") and depth > 0:
            depth -= 1
            continue
        if depth > 0 and s and not s.startswith("//"):
            region.append(" ".join(s.split()))
    for l in region:
        if l not in base_lines and l not in allow:
            missing.append(l[:100])
    ok_all &= check("watch_verbatim", not missing and depth == 0,
                    f"{len(region)} guarded lines" if not missing else ";".join(missing[:5]))
except Exception as e:
    ok_all &= check("watch_verbatim", False, str(e))

# caps
try:
    log_ok = os.path.getsize(NEW_LOG) <= 16 * 1024 * 2**2 if False else os.path.getsize(NEW_LOG) <= 16 * 1024**2
    ok_all &= check("log_cap", log_ok, f"{os.path.getsize(NEW_LOG)}B")
except OSError as e:
    ok_all &= check("log_cap", False, str(e))
try:
    ev = 0
    for root, _, files in os.walk(os.path.join("/Users/brad/dev/ssx3", "local/research/N8D7M12")):
        for f in files:
            ev += os.path.getsize(os.path.join(root, f))
    ok_all &= check("evidence_cap", ev < 512 * 1024, f"{ev}B")
except OSError as e:
    ok_all &= check("evidence_cap", False, str(e))

parity = ["count_packets", "count_priv", "count_transfers", "count_markers", "count_readbacks",
          "count_clears", "count_samples", "marker2050", "parallel_stats", "frame_line",
          "selected11", "bytes_hashes", "packed_input", "packed_circuit", "packed_stage",
          "packed_oracle", "vector_input", "vector_circuit", "vector_stage", "vector_oracle",
          "oracle_controls", "oracle_equal", "replay2050_row", "hashes_file", "ppm2050"]
setup = [k for k in res["checks"] if k not in parity]
if all(res["checks"][k]["ok"] for k in parity if k in res["checks"]) \
        and all(res["checks"][k]["ok"] for k in setup):
    res["verdict"] = "A"
elif any(not res["checks"][k]["ok"] for k in parity if k in res["checks"]):
    res["verdict"] = "B"
else:
    res["verdict"] = "OTHER"

out = os.path.join("/Users/brad/dev/ssx3", "local/research/N8D7M12", "check-result.json")
with open(out, "w") as f:
    json.dump(res, f, indent=2)
for name, r in res["checks"].items():
    print(f'{"PASS" if r["ok"] else "FAIL"} {name} {r["detail"]}')
print("VERDICT", res["verdict"])
sys.exit(0 if res["verdict"] == "A" else 1)
