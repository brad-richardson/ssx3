#!/usr/bin/env python3
"""N8D7M13 Part B comparison: Odin STEP=1 vs Mac STEP=1 (+ vs P7 STEP=50 pair).

Reads only; no device, no judgment. Primary: per-tick Odin vs Mac STEP=1
equality on VRAM, then priv (both sides' parallel.hashes files). Secondary:
present and PKTSEQ. Also: Odin STEP=1 rows at ticks 50..2050 vs P7 run1/run2
(does per-tick readback change the Odin result?). Writes compare-output.txt
here.
"""
import hashlib
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRATCH = Path("/Users/brad/dev/ssx3-work/N8D7M13")
P7SCRATCH = Path("/Users/brad/dev/ssx3-work/N8D7M12P7")
TICKS2050 = list(range(1, 2051))
TICKS41 = list(range(50, 2051, 50))

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


def spans(ticks):
    """Merge a sorted tick list into [(start, end)] inclusive spans."""
    out = []
    for t in sorted(ticks):
        if out and t == out[-1][1] + 1:
            out[-1][1] = t
        else:
            out.append([t, t])
    return [(a, b) for a, b in out]


def fmt_spans(sp):
    return " ".join(f"{a}-{b}" if a != b else f"{a}" for a, b in sp)


def main():
    out = []
    emit = out.append
    warn = []

    odin_hashes = parse_replay((SCRATCH / "step1" / "parallel.hashes")
                               .read_text().splitlines())
    odin_logcat = parse_replay((SCRATCH / "step1" / "logcat-pid.txt")
                               .read_text().splitlines())
    odin_pkt = parse_pktseq((SCRATCH / "step1" / "pktseq.txt")
                            .read_text().splitlines())
    mac_hashes = parse_replay((SCRATCH / "mac" / "parallel.hashes")
                              .read_text().splitlines())
    mac_pkt = parse_pktseq((SCRATCH / "mac" / "replay.log")
                           .read_text().splitlines())
    p7_pkt, p7_rep = {}, {}
    for run in ("run1", "run2"):
        p7_pkt[run] = parse_pktseq((P7SCRATCH / run / "pktseq.txt")
                                   .read_text().splitlines())
        p7_rep[run] = parse_replay((P7SCRATCH / run / "parallel.hashes")
                                   .read_text().splitlines())

    emit("shapes:")
    emit(f"  odin.hashes: rows={len(odin_hashes)} "
         f"ticks1..2050={sorted(odin_hashes) == TICKS2050}")
    emit(f"  odin.logcat: rows={len(odin_logcat)} (gate-failed side; "
         f"missing={2050 - len(odin_logcat)})")
    emit(f"  odin.pktseq: rows={len(odin_pkt)} "
         f"ticks1..2050={sorted(odin_pkt) == TICKS2050}")
    emit(f"  mac.hashes: rows={len(mac_hashes)} "
         f"ticks1..2050={sorted(mac_hashes) == TICKS2050}")
    emit(f"  mac.pktseq: rows={len(mac_pkt)} (known STEP=1 gaps, see 13A REPORT)")
    for run in ("run1", "run2"):
        emit(f"  p7.{run}.pktseq: rows={len(p7_pkt[run])} "
             f"exact41={sorted(p7_pkt[run]) == TICKS41}")
        emit(f"  p7.{run}.replay: rows={len(p7_rep[run])} "
             f"exact41={sorted(p7_rep[run]) == TICKS41}")

    # Odin logcat vs Odin hashes cross-check (logcat is the dropped side).
    emit("")
    emit("odin cross-check: logcat rows vs parallel.hashes rows:")
    bad = [t for t in odin_logcat
           if odin_hashes.get(t) != odin_logcat[t]]
    missing = [t for t in TICKS2050 if t not in odin_logcat]
    emit(f"  logcat rows disagreeing with hashes: {len(bad)}")
    if bad:
        emit(f"  first bad: {bad[:10]}")
        warn.append("odin logcat/hashes disagreement")
    emit(f"  logcat missing spans: {fmt_spans(spans(missing))}")

    # Primary: Odin vs Mac STEP=1 per tick, VRAM then priv; present/PKTSEQ
    # secondary. REPLAY tuple is (priv, vram, present); PKTSEQ is (seq, cmds).
    emit("")
    emit("primary: odin(step1,hashes) vs mac(step1,hashes) per tick 1..2050:")
    fields = (("vram", 1, odin_hashes, mac_hashes),
              ("priv", 0, odin_hashes, mac_hashes),
              ("present", 2, odin_hashes, mac_hashes),
              ("pktseq.seq", 0, odin_pkt, mac_pkt),
              ("pktseq.commands", 1, odin_pkt, mac_pkt))
    for fname, idx, ota, mta in fields:
        eq = [t for t in TICKS2050
              if t in ota and t in mta and ota[t][idx] == mta[t][idx]]
        nodin = [t for t in TICKS2050 if t not in ota]
        nomac = [t for t in TICKS2050 if t not in mta]
        first = next((t for t in TICKS2050
                      if t not in ota or t not in mta
                      or ota[t][idx] != mta[t][idx]), None)
        emit(f"  {fname:15s} equal={len(eq)}/2050 "
             f"first_diff={'tick%d' % first if first else 'none'} "
             f"missing_odin={len(nodin)} missing_mac={len(nomac)}")
        if fname == "vram":
            emit(f"    vram-equal spans: {fmt_spans(spans(eq))}")
            lead = 0
            for t in TICKS2050:
                if t in ota and t in mta and ota[t][idx] == mta[t][idx]:
                    lead += 1
                else:
                    break
            emit(f"    longest leading equal run: ticks 1..{lead} "
                 f"({lead} ticks; first departure tick{lead + 1})")
            if first:
                for t in (first - 1, first, first + 1):
                    if 1 <= t <= 2050:
                        emit(f"    tick={t} odin={ota.get(t)} mac={mta.get(t)}")
        if fname == "priv":
            diff = [t for t in TICKS2050
                    if t in ota and t in mta and ota[t][idx] != mta[t][idx]]
            if diff:
                emit(f"    priv-diff spans: {fmt_spans(spans(diff))}")
        if nomac and fname.startswith("pktseq"):
            emit(f"    mac-missing spans: {fmt_spans(spans(nomac))}")

    # Secondary: Odin STEP=1 at ticks 50..2050 vs P7 run1/run2 (STEP=50).
    emit("")
    emit("secondary: odin step1 vs P7 STEP=50 pair at ticks 50..2050:")
    pairs = (("odin", "run1"), ("odin", "run2"))
    tables = {"odin": (odin_pkt, odin_hashes),
              "run1": (p7_pkt["run1"], p7_rep["run1"]),
              "run2": (p7_pkt["run2"], p7_rep["run2"])}
    sfields = (("seq", 0, 0), ("commands", 0, 1), ("priv", 1, 0),
               ("vram", 1, 1), ("present", 1, 2))
    for fname, tab, idx in sfields:
        cells = []
        for a, b in pairs:
            ta, tb = tables[a][tab], tables[b][tab]
            n = sum(1 for t in TICKS41
                    if ta.get(t) is not None and tb.get(t) is not None
                    and ta[t][idx] == tb[t][idx])
            f = next((t for t in TICKS41
                      if ta.get(t) is None or tb.get(t) is None
                      or ta[t][idx] != tb[t][idx]), None)
            cells.append(f"{a}=={b}: {n:2d}/41 "
                         f"first_diff={'tick%d' % f if f else 'none'}")
        emit(f"  {fname:8s} " + " | ".join(cells))

    emit("")
    emit("tick2050 rows:")
    emit(f"  odin.step1: pktseq={odin_pkt.get(2050)} "
         f"replay_priv/vram/present={odin_hashes.get(2050)}")
    emit(f"  mac.step1: pktseq={mac_pkt.get(2050)} "
         f"replay_priv/vram/present={mac_hashes.get(2050)}")
    for run in ("run1", "run2"):
        emit(f"  p7.{run}: pktseq={p7_pkt[run].get(2050)} "
             f"replay_priv/vram/present={p7_rep[run].get(2050)}")

    emit("")
    emit("final PPMs:")
    ppm_specs = [
        ("odin.step1", SCRATCH / "step1" / "vq-002050.ppm"),
        ("mac.step1", SCRATCH / "mac" / "frames" / "vq-002050.ppm"),
        ("p7.run1", P7SCRATCH / "run1" / "vq-002050.ppm"),
        ("p7.run2", P7SCRATCH / "run2" / "vq-002050.ppm"),
    ]
    for label, path in ppm_specs:
        if path.exists():
            emit(f"  {label}: {path} bytes={path.stat().st_size} "
                 f"sha={file_sha(path)}")
        else:
            emit(f"  {label}: {path} MISSING")
            warn.append(f"{label} ppm missing")

    text = "\n".join(out) + "\n"
    (HERE / "compare-output.txt").write_text(text)
    print(text, end="")
    shapes_ok = (sorted(odin_hashes) == TICKS2050
                 and sorted(odin_pkt) == TICKS2050
                 and sorted(mac_hashes) == TICKS2050
                 and all(sorted(p7_pkt[r]) == TICKS41 for r in ("run1", "run2"))
                 and all(sorted(p7_rep[r]) == TICKS41 for r in ("run1", "run2")))
    if warn:
        print("WARNINGS: " + "; ".join(warn))
    return 0 if shapes_ok and not warn else 1


if __name__ == "__main__":
    raise SystemExit(main())
