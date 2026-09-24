#!/usr/bin/env python3
"""X5 sparse index: extract GIF packet records at capture ticks 949-950."""

import csv
import hashlib
import struct
import sys
from pathlib import Path

CAPTURE = Path("/Users/brad/dev/ssx3-work/GB4/run/gb4p4.capture.bin")
PATHS  = Path("/Users/brad/dev/ssx3-work/GB4/run/gb4p4.paths.txt")
PKLOG  = Path("/Users/brad/dev/ssx3-work/GB4/run/pklog-gb4p4-1.txt")

EXPECTED_SHA = "a6f75fb34fceccf6fd92ad65950d16f05a140cf38a3cc2f028be32e56ad51851"
EXPECTED_PATHS_LINES = 1982063
TARGET_TICKS = {949, 950}
EXPECTED_TOTAL_CSV = 922

KNOWN_PACKET_144266 = {
    "packet_index": 144266,
    "tick": 950,
    "length": 1696,
    "fnv32": "cc6dd8df",
    "corrected_path": 3,
}


def fnv1a(data: bytes) -> str:
    h = 2166136261
    for b in data:
        h = ((h ^ b) * 16777619) & 0xffffffff
    return f"{h:08x}"


def load_paths(paths_path: Path) -> dict[int, int]:
    result: dict[int, int] = {}
    with open(paths_path) as f:
        for i, line in enumerate(f):
            result[i] = int(line.split()[1])
    return result


def load_pklog(pklog_path: Path) -> list[tuple[int, int, str, int, int]]:
    entries: list[tuple[int, int, str, int, int]] = []
    with open(pklog_path) as f:
        for line in f:
            if line.startswith("[pk]"):
                tokens = line.strip().split()
                kv: dict[str, str] = {}
                for t in tokens[1:]:  # skip '[pk]' tag
                    k, v = t.split("=", 1)
                    kv[k] = v
                entries.append((
                    int(kv["idx"]),
                    int(kv["tick"]),
                    kv["fnv"],
                    int(kv["len"]),
                    int(kv["src"]),
                ))
    return entries


def main() -> int:
    failures: list[str] = []

    # --- Validate capture SHA ---
    sha = hashlib.sha256()
    with open(CAPTURE, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            sha.update(chunk)
    actual_sha = sha.hexdigest()
    if actual_sha != EXPECTED_SHA:
        failures.append(
            f"capture SHA mismatch: got {actual_sha}, expected {EXPECTED_SHA}"
        )

    # --- Validate paths file ---
    paths = load_paths(PATHS)
    if len(paths) != EXPECTED_PATHS_LINES:
        failures.append(
            f"paths.txt has {len(paths)} rows, expected {EXPECTED_PATHS_LINES}"
        )

    # --- Load pklog for cross-reference ---
    pklog = load_pklog(PKLOG)

    # --- Parse capture: stream, find GIF packet records at ticks 949-950 ---
    rows: list[dict] = []
    gif_packet_index = 0
    file_offset = 0  # offset in file (starts after 8-byte magic)
    file_size = CAPTURE.stat().st_size

    with open(CAPTURE, "rb") as f:
        magic = f.read(8)
        assert magic == b"PS2XGSC1", "bad magic"

        while file_offset < file_size:
            start_offset = f.tell()

            # Read payload_size (LE32)
            ps_bytes = f.read(4)
            if len(ps_bytes) < 4:
                failures.append(
                    f"short record header at file_offset={start_offset}, "
                    f"expected 4 bytes, got {len(ps_bytes)}"
                )
                break
            payload_size = struct.unpack("<I", ps_bytes)[0]

            rec = f.read(payload_size)
            if len(rec) < payload_size:
                failures.append(
                    f"truncated record at file_offset={start_offset}, "
                    f"needed {payload_size}, got {len(rec)}"
                )
                break

            record_end = start_offset + 4 + payload_size

            kind = rec[0]
            if kind == 1:  # GIF packet (Packet = 1)
                tick = struct.unpack_from("<Q", rec, 1)[0]
                path = rec[9]
                data_size = struct.unpack_from("<I", rec, 10)[0]
                gif_data = rec[14:]

                if len(gif_data) != data_size:
                    failures.append(
                        f"packet {gif_packet_index}: data_size={data_size}, "
                        f"actual data len={len(gif_data)}"
                    )

                if tick in TARGET_TICKS:
                    fnv_val = fnv1a(gif_data)
                    rows.append({
                        "packet_index": gif_packet_index,
                        "tick": tick,
                        "record_offset": start_offset,
                        "corrected_path": paths.get(gif_packet_index, -1),
                        "embedded_path": path,
                        "length": len(gif_data),
                        "fnv32": fnv_val,
                    })

                file_offset = record_end
                gif_packet_index += 1
            else:
                file_offset = record_end

    # Check final parsed offset reaches EOF
    if file_offset != file_size:
        failures.append(
            f"final parsed offset {file_offset} != file size {file_size} "
            f"(gap of {file_size - file_offset} bytes)"
        )

    # --- Validate packet 144266 ---
    p144266 = None
    for r in rows:
        if r["packet_index"] == 144266:
            p144266 = r
            break

    if p144266 is None:
        failures.append("packet 144266 not found in tick 949-950 range")
    else:
        known = KNOWN_PACKET_144266
        checks = {
            "packet_index": p144266["packet_index"] == known["packet_index"],
            "tick": p144266["tick"] == known["tick"],
            "length": p144266["length"] == known["length"],
            "fnv32": p144266["fnv32"] == known["fnv32"],
            "corrected_path": p144266["corrected_path"] == known["corrected_path"],
        }
        for k, v in checks.items():
            if not v:
                failures.append(
                    f"packet 144266 {k}: got {p144266[k]}, expected {known[k]}"
                )

    # --- Cross-reference with pklog ---
    cross_matches = 0
    cross_mismatches = 0
    cross_missing = 0
    cross_rows: list[dict] = []

    for r in rows:
        idx = r["packet_index"]
        if idx < len(pklog):
            pk = pklog[idx]
            # Verify pklog declares the same index
            if pk[0] != idx:
                failures.append(
                    f"pklog[{idx}] declares idx={pk[0]}, expected {idx}"
                )
            # pklog tuple: (idx, tick, fnv, length, src)
            pk_row = {
                "packet_index": idx,
                "tick": pk[1],
                "fnv32": pk[2],
                "length": pk[3],
                "pklog_src": pk[4],
                "csv_tick": r["tick"],
                "csv_fnv32": r["fnv32"],
                "csv_length": r["length"],
                "csv_corrected_path": r["corrected_path"],
            }
                    # Exact match: (tick, fnv32, length, corrected_path==src)
            # pklog FNV may lack leading zeros; normalize to 8 digits
            pk_fnv_norm = pk[2].zfill(8)
            csv_tick = int(r["tick"])
            csv_length = int(r["length"])
            csv_corrected = str(r["corrected_path"])
            if (csv_tick == pk[1] and r["fnv32"] == pk_fnv_norm and
                    csv_length == pk[3] and csv_corrected == str(pk[4])):
                cross_matches += 1
                pk_row["status"] = "match"
            else:
                cross_mismatches += 1
                pk_row["status"] = "mismatch"
            cross_rows.append(pk_row)
        else:
            cross_missing += 1
            cross_rows.append({
                "packet_index": idx,
                "status": "missing_pklog",
            })

    # --- Validate acceptance criteria ---
    if len(rows) != EXPECTED_TOTAL_CSV:
        failures.append(
            f"CSV count: {len(rows)}, expected {EXPECTED_TOTAL_CSV}"
        )

    if not failures:
        all_exact = all(
            r["status"] == "match" for r in cross_rows if r.get("status")
        )
        if not all_exact:
            failures.append(
                f"{cross_mismatches} CSV-pklog mismatches, {cross_missing} missing pklog"
            )

    # --- Write CSV ---
    csv_path = Path("/Users/brad/dev/ssx3/local/research/X5/packets-949-950.csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "packet_index", "tick", "record_offset", "corrected_path",
            "embedded_path", "length", "fnv32",
        ])
        w.writeheader()
        for r in rows:
            w.writerow(r)

    # --- Summary line ---
    tick_counts = {}
    for r in rows:
        tick_counts[r["tick"]] = tick_counts.get(r["tick"], 0) + 1

    first_idx = rows[0]["packet_index"] if rows else None
    last_idx = rows[-1]["packet_index"] if rows else None

    summary = (
        f"[X5] rows={len(rows)} first={first_idx} last={last_idx} "
        f"ticks={tick_counts} matches={cross_matches} "
        f"mismatches={cross_mismatches} missing_pklog={cross_missing} "
        f"sha_ok={'OK' if actual_sha == EXPECTED_SHA else 'FAIL'} "
        f"paths_ok={'OK' if len(paths) == EXPECTED_PATHS_LINES else 'FAIL'}"
    )
    print(summary)

    if failures:
        for msg in failures:
            print(f"  FAIL: {msg}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
