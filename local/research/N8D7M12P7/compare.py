#!/usr/bin/env python3
"""N8D7M12 Part 7B comparison: run1 vs run2 vs Mac ON control.

Reads only; no device, no judgment. Per tick 50..2050 compares PKTSEQ
seq/commands and GB4_REPLAY priv/vram/present across the three sides,
reports match counts, first differing tick per field/pair, and final
PPM SHAs with absolute paths. Writes compare-output.txt here.
"""
import hashlib
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SCRATCH = Path("/Users/brad/dev/ssx3-work/N8D7M12P7")
MAC_EXCERPT = (REPO / "local" / "research" / "N8D7M12P5F4P2"
               / "replay-excerpt.txt")
MAC_PPM = Path("/Users/brad/dev/ssx3-work/N8D7M12P5F4/mac-pktseq/frames/vq-002050.ppm")
TICKS = list(range(50, 2051, 50))

PKTSEQ = re.compile(r"GB4_PKTSEQ tick=(\d+) seq=([0-9a-fA-F]+) commands=(\d+)")
REPLAY = re.compile(r"GB4_REPLAY tick=(\d+) vram=([0-9a-fA-F]+) "
                    r"priv=([0-9a-fA-F]+) present=([0-9a-fA-F]+)")


def file_sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_pktseq(lines):
    rows = {}
    for line in lines:
        m = PKTSEQ.search(line)
        if m:
            rows[int(m.group(1))] = (m.group(2).lower(), int(m.group(3)))
    return rows


def parse_replay(lines):
    # Stored as (priv, vram, present); the log order is vram, priv, present.
    rows = {}
    for line in lines:
        m = REPLAY.search(line)
        if m:
            rows[int(m.group(1))] = (m.group(3).lower(), m.group(2).lower(),
                                     m.group(4).lower())
    return rows


def shape(name, rows):
    ticks = sorted(rows)
    ok = ticks == TICKS and len(rows) == 41
    return f"{name}: rows={len(rows)} ticks_ok={ticks == TICKS} exact41={ok}"


def main():
    out = []
    emit = out.append
    pkt, rep = {}, {}
    for run in ("run1", "run2"):
        pkt[run] = parse_pktseq((SCRATCH / run / "pktseq.txt").read_text().splitlines())
        rep[run] = parse_replay((SCRATCH / run / "parallel.hashes").read_text().splitlines())
    mac_lines = MAC_EXCERPT.read_text().splitlines()
    pkt["mac"] = parse_pktseq(mac_lines)
    rep["mac"] = parse_replay(mac_lines)

    emit("shapes:")
    for name, rows in (("run1.pktseq", pkt["run1"]), ("run2.pktseq", pkt["run2"]),
                       ("mac.pktseq", pkt["mac"]), ("run1.replay", rep["run1"]),
                       ("run2.replay", rep["run2"]), ("mac.replay", rep["mac"])):
        emit("  " + shape(name, rows))

    fields = (("seq", 0, pkt), ("commands", 1, pkt), ("priv", 0, rep),
              ("vram", 1, rep), ("present", 2, rep))
    pairs = (("run1", "run2"), ("run1", "mac"), ("run2", "mac"))
    first, counts = {}, {}
    for fname, idx, table in fields:
        for a, b in pairs:
            key = (fname, a, b)
            counts[key] = sum(1 for t in TICKS
                              if table[a].get(t) is not None
                              and table[a][t][idx] == table[b].get(t, (None,))[idx])
            first[key] = next((t for t in TICKS
                               if table[a].get(t) is None or table[b].get(t) is None
                               or table[a][t][idx] != table[b][t][idx]), None)

    emit("")
    emit("per-tick table: tick | seq r1==r2 r1==mac r2==mac | cmd r1==r2 r1==mac r2==mac |"
         " priv r1==r2 r1==mac r2==mac | vram r1==r2 r1==mac r2==mac |"
         " present r1==r2 r1==mac r2==mac  (= equal, X differ, ? missing)")
    for t in TICKS:
        cells = []
        for _fname, idx, table in fields:
            a, b, c = table["run1"].get(t), table["run2"].get(t), table["mac"].get(t)
            if a is None or b is None or c is None:
                cells.append("???")
            else:
                cells.append("".join("=" if x == y else "X" for x, y in
                                     ((a[idx], b[idx]), (a[idx], c[idx]), (b[idx], c[idx]))))
        emit(f"tick={t:5d} " + " ".join(f"{cell}" for cell in cells))

    emit("")
    emit("summary (equal/41, first differing tick or all-equal):")
    for fname, _idx, _table in fields:
        for a, b in pairs:
            key = (fname, a, b)
            f = first[key]
            emit(f"  {fname:8s} {a}=={b}: {counts[key]:2d}/41 "
                 f"first_diff={'tick%d' % f if f else 'none'}")

    emit("")
    emit("tick2050 rows:")
    for side in ("run1", "run2", "mac"):
        p, r = pkt[side].get(2050), rep[side].get(2050)
        emit(f"  {side}: pktseq={p} replay_priv/vram/present={r}")

    emit("")
    emit("final PPMs:")
    for label, path in (("run1", SCRATCH / "run1" / "vq-002050.ppm"),
                        ("run2", SCRATCH / "run2" / "vq-002050.ppm")):
        emit(f"  {label}: {path} bytes={path.stat().st_size} sha={file_sha(path)}")
    if MAC_PPM.exists():
        emit(f"  mac: {MAC_PPM} bytes={MAC_PPM.stat().st_size} sha={file_sha(MAC_PPM)}")
    else:
        emit(f"  mac: {MAC_PPM} MISSING (P5F4P2 REPORT pins vq-002050.ppm 9490484c..14fce3e)")

    text = "\n".join(out) + "\n"
    (HERE / "compare-output.txt").write_text(text)
    print(text, end="")
    shapes_ok = all(len(rows) == 41 and sorted(rows) == TICKS
                    for rows in list(pkt.values()) + list(rep.values()))
    return 0 if shapes_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
