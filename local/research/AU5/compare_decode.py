#!/usr/bin/env python3
"""Compare AU5's first 32 EE float frames with AU2's integer XA decoder."""
import argparse
import importlib.util
import json
import struct
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("au2_eaxa", HERE.parent / "AU2/au2_eaxa.py")
au2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(au2)


def f32(bits):
    return struct.unpack(">f", bytes.fromhex(bits))[0]


def floating_model(raw, h1, h2):
    fi = raw[0]
    if fi == 0xEE:
        return None
    c = (fi >> 4) & 3
    shift = fi & 15
    out = []
    h1, h2 = np.float32(h1), np.float32(h2)
    for i in range(28):
        byte = raw[1 + i // 2]
        nibble = byte >> 4 if i % 2 == 0 else byte & 15
        if nibble & 8:
            nibble -= 16
        sample = np.float32(
            np.float32(nibble * 2 ** (12 - shift))
            + np.float32(np.float32(au2.C1[c] / 256) * h1)
            + np.float32(np.float32(au2.C2[c] / 256) * h2)
        )
        out.append(float(sample))
        h2, h1 = h1, sample
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tap", type=Path)
    ap.add_argument("out", type=Path)
    args = ap.parse_args()
    first = None
    int_mismatches = 0
    trunc_mismatches = 0
    max_float_error = 0.0
    frames = 0
    for line in args.tap.read_text().splitlines():
        fields = line.split()
        assert len(fields) == 9, (len(fields), line[:80])
        frame_no = int(fields[0])
        hist1, hist2 = f32(fields[3]), f32(fields[4])
        raw = bytes.fromhex(fields[7])
        assert len(raw) == 61
        ee = [f32(fields[8][i:i + 8]) for i in range(0, 28 * 8, 8)]
        ref, _, _ = au2.frame(raw, 0, (round(hist1), round(hist2)))
        model = floating_model(raw, hist1, hist2)
        assert model is not None
        for sample_no, (got, want, predicted) in enumerate(zip(ee, ref, model)):
            max_float_error = max(max_float_error, abs(got - predicted))
            if round(got) != want:
                int_mismatches += 1
                if first is None:
                    first = {"frame": frame_no, "sample": sample_no,
                             "frame_header": hex(raw[0]), "ee_float": got,
                             "ee_rounded": round(got), "au2_integer": want,
                             "history_in": [hist1, hist2]}
            if int(np.trunc(got)) != want:
                trunc_mismatches += 1
        frames += 1
    result = {"frames": frames, "samples": frames * 28,
              "rounded_integer_mismatches": int_mismatches,
              "truncated_integer_mismatches": trunc_mismatches,
              "first_rounded_mismatch": first,
              "max_abs_ee_vs_float_model": max_float_error,
              "scope": "Each AU2 frame starts from the EE tap's rounded input history; EE outputs are pre-mix float samples."}
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
