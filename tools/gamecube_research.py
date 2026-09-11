#!/usr/bin/env python3
"""Generate reproducible static research leads, never inferred function names.

Address materialization and data-pointer matches are candidates for inspection,
not proof of execution, function boundaries, or a safe patch location.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import struct


def signed(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def address_pair(first, second):
    """Decode adjacent lis + addi/ori; return the computed 32-bit address."""
    if first >> 26 != 15 or (first >> 16) & 31:
        return None
    register = (first >> 21) & 31
    upper = (first & 0xFFFF) << 16
    if second >> 26 == 14 and (second >> 16) & 31 == register and register != 0:
        return (upper + signed(second & 0xFFFF, 16)) & 0xFFFFFFFF
    if second >> 26 == 24 and (second >> 21) & 31 == register:
        return upper | (second & 0xFFFF)
    return None


def materializations(words, base):
    """Conservative constant propagation, clearing state at unknown instructions.

    This intentionally misses references rather than assuming register values
    survive calls, branches, unmodeled operations, or memory loads.
    """
    known = {}
    for i, word in enumerate(words):
        opcode, rt, ra, immediate = word >> 26, (word >> 21) & 31, (word >> 16) & 31, word & 0xFFFF
        value = None
        destination = rt
        if opcode in (14, 15):
            prior = 0 if ra == 0 else known.get(ra)
            if prior is not None:
                value = (prior + (signed(immediate, 16) << (16 if opcode == 15 else 0))) & 0xFFFFFFFF
        elif opcode in (24, 25):
            destination = ra
            if rt in known:
                value = known[rt] | (immediate << (16 if opcode == 25 else 0))
        elif opcode in (32, 33, 34, 35, 40, 41, 42, 43):
            known.pop(rt, None)
            if opcode & 1:
                known.pop(ra, None)
            continue
        elif opcode in (36, 37, 38, 39, 44, 45, 47, 48, 49, 50, 51, 52, 53, 54, 55):
            if opcode & 1 and opcode != 47:
                known.pop(ra, None)
            continue
        elif opcode in (10, 11):  # cmpli/cmpi do not change GPRs.
            continue
        else:
            known.clear()
            continue
        known.pop(destination, None)
        if value is not None:
            known[destination] = value
            yield base + i * 4, value


class Dol:
    def __init__(self, data):
        if len(data) < 0x100:
            raise ValueError("Truncated DOL header")
        self.data = data
        self.sections = []
        for name, count, offsets, addresses, sizes in (
            ("text", 7, 0, 0x48, 0x90), ("data", 11, 0x1C, 0x64, 0xAC)
        ):
            for i in range(count):
                offset, address, size = (struct.unpack_from(">I", data, base + 4 * i)[0]
                                         for base in (offsets, addresses, sizes))
                if not size:
                    continue
                if offset < 0x100 or offset + size > len(data):
                    raise ValueError(f"Invalid {name}{i} file extent")
                self.sections.append(dict(name=f"{name}{i}", offset=offset, address=address, size=size))

    def word(self, address):
        for section in self.sections:
            delta = address - section["address"]
            if 0 <= delta <= section["size"] - 4:
                return struct.unpack_from(">I", self.data, section["offset"] + delta)[0]
        raise ValueError(f"Address {address:08x} not backed by this DOL")


def symbols(info):
    result = []
    # Section table also has address/size columns: do not mistake it for symbols.
    body = info.split("Discovered symbols:", 1)[1]
    pattern = r"\| (0x[0-9A-Fa-f]+) +\| (0x[0-9A-Fa-f]+) +\| (\S+)"
    for address, size, name in re.findall(pattern, body):
        if int(size, 16):
            result.append((int(address, 16), int(size, 16), name))
    return result


def analyze(dol, info, smc):
    anchors = {}
    pattern = re.compile(r"world|terrain|\.gdb|\.gsb|physics|course|restart|reset|prestartscreen", re.I)
    for section in dol.sections:
        if not section["name"].startswith("data"):
            continue
        data = dol.data[section["offset"]:section["offset"] + section["size"]]
        for match in re.finditer(rb"[\x20-\x7e]{5,}", data):
            value = match.group().decode("ascii")
            if pattern.search(value):
                address = section["address"] + match.start()
                anchors[address] = {"address": f"0x{address:08X}", "text": value,
                                    "adjacent_address_pairs": [], "materialization_candidates": [],
                                    "data_pointer_candidates": []}
    calls_to_main = []
    main = next((address for address, size, name in symbols(info) if name == "main"), None)
    for section in dol.sections:
        words = list(struct.iter_unpack(">I", dol.data[section["offset"]:
                          section["offset"] + section["size"] // 4 * 4]))
        if section["name"].startswith("text"):
            for pc, address in materializations((w[0] for w in words), section["address"]):
                if address in anchors:
                    anchors[address]["materialization_candidates"].append(f"0x{pc:08X}")
        for i, (word,) in enumerate(words):
            pc = section["address"] + i * 4
            if section["name"].startswith("text"):
                if i + 1 < len(words):
                    address = address_pair(word, words[i + 1][0])
                    if address in anchors:
                        anchors[address]["adjacent_address_pairs"].append(f"0x{pc:08X}")
                if word >> 26 == 18 and word & 1:
                    displacement = signed(word & 0x03FFFFFC, 26)
                    target = (displacement if word & 2 else pc + displacement) & 0xFFFFFFFF
                    if target == main:
                        calls_to_main.append(f"0x{pc:08X}")
            elif word in anchors:
                anchors[word]["data_pointer_candidates"].append(f"0x{pc:08X}")
    known = symbols(info)
    warnings = []
    instruction_counts = Counter()
    # Only label instruction classes positively recognized here.
    extended = {982: "icbi", 1014: "dcbz", 54: "dcbst", 86: "dcbf", 470: "dcbi"}
    for start, end in re.findall(r"(0x[0-9A-Fa-f]+)-(0x[0-9A-Fa-f]+)", smc):
        a, b = int(start, 16), int(end, 16)
        contained = [name for address, size, name in known if address <= a and b < address + size]
        instructions = []
        for pc in range(a, b + 1, 4):
            word = dol.word(pc)
            opcode, xo = word >> 26, (word >> 1) & 1023
            name = extended.get(xo, "unclassified") if opcode == 31 else "unclassified"
            if opcode in (36, 38, 44):
                name = {36: "stw", 38: "stb", 44: "sth"}[opcode]
            if opcode == 4 and xo == 1014:
                name = "dcbz_l"
            instruction_counts[name] += 1
            instructions.append({"pc": f"0x{pc:08X}", "class": name})
        warnings.append({"start": start, "end_inclusive": end,
                         "dtk_symbol": contained[-1] if contained else None,
                         "instructions": instructions})
    return {"schema": 1, "dol_sha256": hashlib.sha256(dol.data).hexdigest(),
            "limits": "Static leads only. Adjacent pairs may be embedded data; pointer matches may be integers. No control-flow or runtime validation. SMC flags do not prove code modification.",
            "dtk_main": f"0x{main:08X}" if main else None,
            "direct_call_candidates_to_main": calls_to_main, "anchors": list(anchors.values()),
            "smc_range_count": len(warnings), "smc_instruction_classes": dict(instruction_counts),
            "smc_ranges": warnings}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dol", type=Path, required=True)
    parser.add_argument("--dol-info", type=Path, required=True)
    parser.add_argument("--smc", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = analyze(Dol(args.dol.read_bytes()), args.dol_info.read_text(), args.smc.read_text())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"output": str(args.output), "anchors": len(report["anchors"]),
                      "smc_range_count": report["smc_range_count"],
                      "smc_instruction_classes": report["smc_instruction_classes"]}, indent=2))


if __name__ == "__main__":
    main()
