#!/usr/bin/env python3
"""Predeclared N8D7G same-stream Mac replay checks; prints JSON, exits 0 only on PASS."""
import hashlib
import json
import re
import sys
from pathlib import Path


def one(pattern, text, label):
    rows = re.findall(pattern, text, re.MULTILINE)
    if len(rows) != 1:
        raise ValueError(f"{label}: expected one row, got {len(rows)}")
    return rows[0]


def fields(line):
    return {k: v for k, v in re.findall(r"([a-z_]+)=([^\s]+)", line)}


def vector(text, name, n):
    raw = one(rf"^\[n8d7f\] {name}_tile_counts=([0-9,]+)$", text, name)
    v = [int(x) for x in raw.split(",")]
    if len(v) != n or any(x < 0 or x > 256 for x in v):
        raise ValueError(f"{name}: invalid {len(v)}-tile vector")
    packed = b"".join(x.to_bytes(2, "little") for x in v)
    summary = fields(one(rf"^\[n8d7f\] {name} tiles=448 .+$", text, name + " summary"))
    if int(summary["occupied"]) != sum(v) or int(summary["active"]) != sum(x >= 32 for x in v):
        raise ValueError(f"{name}: summary mismatch")
    if summary["packed_sha256"] != hashlib.sha256(packed).hexdigest():
        raise ValueError(f"{name}: packed SHA mismatch")
    return v, summary


def final_hash(path):
    row = one(r"^GB4_REPLAY tick=2050 vram=[0-9a-f]+ priv=[0-9a-f]+ present=([0-9a-f]+)$", path.read_text(), str(path))
    return row


def main(root):
    off = (root / "off.log").read_text(errors="replace")
    on = (root / "on.log").read_text(errors="replace")
    checks = {}
    errors = []

    def check(name, yes):
        checks[name] = bool(yes)
        if not yes:
            errors.append(name)

    for name, log in (("off", off), ("on", on)):
        align = fields(one(r"^\[n8d5b\] alignment .+$", log, name + " alignment"))
        check(name + "_alignment", all(align.get(k) == v for k, v in
            {"tick": "2050", "fbp": "112", "pmode": "ff21", "width": "512", "height": "448"}.items()))
        stages = {}
        for stage, height, tiles in (("circuit1", 224, 448), ("pre_deinterlace_merged", 224, 448), ("final", 448, 896)):
            row = fields(one(rf"^\[n8d6a\] stage={stage} .+$", log, name + " " + stage))
            stages[stage] = row
            check(name + "_" + stage, row.get("width") == "512" and row.get("height") == str(height)
                  and row.get("tiles") == str(tiles) and row.get("control") == "128")
        check(name + "_final_broad", int(stages["final"]["active"]) >= 500)
        check(name + "_checkerboard", "[n8d5b] control=128 expected=128 PASS" in log)
        check(name + "_no_errors", not re.search(r"\[n8d(?:5b|6a|7f)\].*(?:ERROR|OTHER)|VK_ERROR|pipeline.*(?:error|failed)", log, re.I))
    check("off_flag_silent", "[n8d7f]" not in off)
    meta = fields(one(r"^\[n8d7f\] tick=2050 .+$", on, "selected metadata"))
    check("selected_metadata", all(meta.get(k) == v for k, v in
        {"tick": "2050", "fbp": "112", "samples": "1", "promoted": "0", "extent": "512x224", "valid": "512x224", "status": "2", "mask": "4194303"}.items()))
    check("selected_geometry", int(meta["dbx"]) + 511 < 2048 and
          int(meta["dby"]) + int(meta["phase"]) + 223 * int(meta["stride"]) < 2048)
    check("capture_bytes", "[n8d7f] bytes=5177344 " in on)
    vectors = {name: vector(on, name, 448) for name in ("input", "circuit", "stage")}
    for name in ("input", "circuit"):
        check(name + "_broad", int(vectors[name][1]["active"]) >= 224)
    check("input_circuit_equal", vectors["input"][0] == vectors["circuit"][0])
    check("circuit_stage_equal", vectors["circuit"][0] == vectors["stage"][0])
    eq = fields(one(r"^\[n8d7f\] input_circuit_equal=448/448 circuit_stage_equal=448/448$", on, "equality row"))
    check("equality_row", eq.get("input_circuit_equal") == "448/448" and eq.get("circuit_stage_equal") == "448/448")
    check("hashes", final_hash(root / "off.hashes") == final_hash(root / "on.hashes") == "7bf5c012")
    return {"verdict": "PASS" if not errors else "OTHER", "checks": checks, "failed": errors,
            "final_hash_off": final_hash(root / "off.hashes"), "final_hash_on": final_hash(root / "on.hashes"),
            "selected": meta, "input_active": vectors["input"][1]["active"],
            "circuit_active": vectors["circuit"][1]["active"], "stage_active": vectors["stage"][1]["active"]}


if __name__ == "__main__":
    try:
        result = main(Path(sys.argv[1]))
    except Exception as exc:
        result = {"verdict": "OTHER", "error": str(exc)}
    print(json.dumps(result, indent=2, sort_keys=True))
    sys.exit(0 if result["verdict"] == "PASS" else 1)
