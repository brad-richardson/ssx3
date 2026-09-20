#!/usr/bin/env python3
"""trace_align.py — first-divergence aligner for EE.Bios syscall streams.

Brief 2 (T18): aligns the PCSX2 reference EE.Bios stream
(`/Volumes/Extreme SSD/ps2x-t4/emulog-boot3.txt`) with the runtime trace
channel stream (PS2X_TRACE_SYSCALLS file, same `Bios call: NAME (hex)` shape)
to their FIRST divergence.

Comparison key is the syscall NUMBER (PCSX2 logs abs($v1) as u8; both sides
share the R5900::bios name table, so names agree by construction — a
numbers-equal/names-differ row is tabled as a name-table mismatch, never a
divergence). EE lines carry no args/returns on either side: order + names +
numbers only (T4 format notes).

Usage:
  trace_align.py REF RT [--ref-after NAME[:OCC]] [--rt-after NAME[:OCC]]
                   [--window N] [--locate K] [--census] [--context N]
                   [--drop-names N,...] [--project shared] [--milestones]
  trace_align.py --format-check FILE [FILE ...]
  trace_align.py --selftest

T22 projection: --drop-names removes exact-name events from BOTH streams
after anchor resolution (comparison + locate + milestones; census stays
full post-start). --project shared is the F3 S19 preset (SIF layer, sema
pump, GetThreadId, FlushCache, RFU005). --milestones prints the projected
rare-vocabulary sequences with stamps, both sides.

Exit codes:
  0  no divergence in the compared window (bound tabled)
  1  first divergence found (tabled)
  2  usage error / anchor miss / format-check failure / selftest failure
"""

import argparse
import re
import sys
from array import array
from collections import Counter

LINE_RE = re.compile(r"Bios call: (\S+) \(([0-9a-fA-F]+)\)")
TS_RE = re.compile(r"^\[\s*(\d+\.\d+)\] Bios    : Bios call: ")


def parse_after(spec):
    """'NAME[:OCC]' -> (NAME, OCC) or None for 'none'."""
    if spec is None or spec.lower() == "none":
        return None
    if ":" in spec:
        name, occ = spec.rsplit(":", 1)
        return (name, int(occ))
    return (spec, 1)


# T22 --project shared preset: the F3 S19 projection (order = table order).
# SIF layer (HLE'd by construction; runtime can never emit), sema pump
# (drowns both streams), GetThreadId + FlushCache (runtime-only storms),
# RFU005 (reference-only interrupt-return path, host-side on runtime).
# Deliberately NOT dropped: CreateSema/DeleteSema/ReferSemaStatus (S19
# milestones), iFlushCache (0/0 on both sides), Dmac handlers, Deci2Call.
SHARED_DROPS = (
    "sceSifGetReg",
    "sceSifSetDma_isceSifSetDma",
    "sceSifSetDChain_isceSifSetDChain",
    "sceSifSetReg",
    "sceSifDmaStat_isceSifDmaStat",
    "sceSifStopDma",
    "WaitSema",
    "SignalSema",
    "iSignalSema",
    "PollSema",
    "iPollSema",
    "iReferSemaStatus",
    "GetThreadId",
    "FlushCache",
    "RFU005",
)


def parse_drop_names(spec):
    """'A,B,...' -> [names]; empty entries ignored, whitespace stripped."""
    if spec is None:
        return []
    return [n.strip() for n in spec.split(",") if n.strip()]


class Stream:
    """Parsed event stream: numbers + file lines + interned names."""

    def __init__(self, path):
        self.path = path
        self.nums = array("I")
        self.lines = array("I")
        self.name_ids = array("I")
        self.ts = array("d")  # T22: host-wall stamp per event (NaN if unparseable)
        self.names = []
        self._name_to_id = {}
        self.file_lines = 0
        self.skipped = 0

    def append(self, file_lineno, name, num, ts):
        nid = self._name_to_id.get(name)
        if nid is None:
            nid = len(self.names)
            self.names.append(name)
            self._name_to_id[name] = nid
        self.nums.append(num)
        self.lines.append(file_lineno)
        self.name_ids.append(nid)
        self.ts.append(ts)

    def __len__(self):
        return len(self.nums)

    def name(self, i):
        return self.names[self.name_ids[i]]


def parse_stream(path, progress_every=0):
    st = Stream(path)
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for lineno, line in enumerate(f, 1):
            st.file_lines = lineno
            m = LINE_RE.search(line)
            if not m:
                st.skipped += 1
                continue
            t = TS_RE.match(line)
            ts = float(t.group(1)) if t else float("nan")
            st.append(lineno, m.group(1), int(m.group(2), 16), ts)
            if progress_every and len(st) % progress_every == 0:
                print(f"... {path}: {len(st)} events", file=sys.stderr)
    return st


def find_anchor(st, spec):
    """Resolve (NAME, OCC) -> event index after OCC-th occurrence.

    Returns (index, file_lineno_of_hit, total_hits). Miss -> (None, None, 0).
    """
    name, occ = spec
    hits = 0
    for i in range(len(st)):
        if st.name(i) == name:
            hits += 1
            if hits == occ:
                # total hits needs the full scan; do it once here
                total = hits + sum(
                    1 for j in range(i + 1, len(st)) if st.name(j) == name
                )
                return (i + 1, st.lines[i], total)
    return (None, None, hits)


def fmt_event(st, i):
    return f"{st.name(i)} ({st.nums[i]:x}) @file:{st.lines[i]} ev:{i}"


def fmt_ts(ts):
    return f"{ts:8.4f}" if ts == ts else "     ---"  # NaN -> no stamp


def cmd_align(args):
    ref = parse_stream(args.ref)
    rt = parse_stream(args.rt)

    print(f"ref: {args.ref}")
    print(f"  file_lines={ref.file_lines} events={len(ref)} skipped={ref.skipped}")
    print(f"rt:  {args.rt}")
    print(f"  file_lines={rt.file_lines} events={len(rt)} skipped={rt.skipped}")

    # T22 projection: preset + explicit drops resolve to one ordered list
    # (union, preset first). Unknown preset is a usage error (exit 2).
    project = getattr(args, "project", None)
    drops = []
    if project is not None:
        if project != "shared":
            print(f"project: unknown preset '{project}' (want: shared)")
            print("result: USAGE-ERROR")
            return 2
        drops.extend(SHARED_DROPS)
    for n in parse_drop_names(getattr(args, "drop_names", None)):
        if n not in drops:
            drops.append(n)
    milestones = bool(getattr(args, "milestones", False))

    ref_after = parse_after(args.ref_after)
    rt_after = parse_after(args.rt_after)

    # Anchor table.
    print("--- anchor ---")
    ok = True
    if ref_after is None:
        ref_start = 0
        print(f"ref_start: none requested -> ev:0")
    else:
        idx, hit_line, total = find_anchor(ref, ref_after)
        print(
            f"ref_after: name={ref_after[0]} occ={ref_after[1]} "
            f"total_hits={total} -> "
            + (f"HIT ev:{idx} file:{hit_line}" if idx is not None else "MISS")
        )
        if idx is None:
            ok = False
        else:
            ref_start = idx
    if rt_after is None:
        rt_start = 0
        print(f"rt_start: none requested -> ev:0")
    else:
        idx, hit_line, total = find_anchor(rt, rt_after)
        print(
            f"rt_after: name={rt_after[0]} occ={rt_after[1]} "
            f"total_hits={total} -> "
            + (f"HIT ev:{idx} file:{hit_line}" if idx is not None else "MISS")
        )
        if idx is None:
            ok = False
        else:
            rt_start = idx
    if not ok:
        print("result: ANCHOR-MISS")
        return 2

    # Projected post-start index lists (None = no projection; the old path).
    # Milestones without drops still needs full post-start ranges.
    ref_idx = rt_idx = None
    if drops or milestones:
        drop_set = set(drops)
        ref_idx = [t for t in range(ref_start, len(ref))
                   if ref.name(t) not in drop_set]
        rt_idx = [t for t in range(rt_start, len(rt))
                  if rt.name(t) not in drop_set]

    if drops:
        print("--- project ---")
        print(f"project={project or 'none'} drops={len(drops)} "
              f"ref_post={len(ref) - ref_start} rt_post={len(rt) - rt_start} "
              f"ref_proj={len(ref_idx)} rt_proj={len(rt_idx)}")
        cref_post = Counter(ref.name(t) for t in range(ref_start, len(ref)))
        crt_post = Counter(rt.name(t) for t in range(rt_start, len(rt)))
        for n in drops:
            print(f"  {n} ref={cref_post.get(n, 0)} rt={crt_post.get(n, 0)}")

    def at(k):
        if ref_idx is None:
            return (ref_start + k, rt_start + k)
        return (ref_idx[k], rt_idx[k])

    if ref_idx is None:
        n_ref = len(ref) - ref_start
        n_rt = len(rt) - rt_start
    else:
        n_ref = len(ref_idx)
        n_rt = len(rt_idx)
    limit = min(n_ref, n_rt)
    if args.window and args.window > 0:
        limit = min(limit, args.window)

    # Compare.
    div = None
    name_mismatches = []
    for k in range(limit):
        i, j = at(k)
        if ref.nums[i] != rt.nums[j]:
            div = k
            break
        if ref.name(i) != rt.name(j) and len(name_mismatches) < 10:
            name_mismatches.append((k, i, j))

    print("--- name-table ---")
    print(f"compared={limit} name_mismatches={len(name_mismatches)}")
    for k, i, j in name_mismatches:
        print(f"  k={k} ref={fmt_event(ref, i)} rt={fmt_event(rt, j)}")

    ctx = args.context
    pmark = " (projected)" if drops else ""
    if div is not None:
        i, j = at(div)
        print("--- divergence ---")
        print(f"k={div}{pmark} (agreement run before it: {div} events)")
        print(f"ref: {fmt_event(ref, i)}")
        print(f"rt:  {fmt_event(rt, j)}")
        print(f"--- context (+-{ctx}) ---")
        for k in range(max(0, div - ctx), min(limit, div + ctx + 1)):
            mark = ">>>" if k == div else "   "
            ci, cj = at(k)
            print(
                f"{mark} k={k} ref={fmt_event(ref, ci)} "
                f"rt={fmt_event(rt, cj)}"
            )
        print("result: DIVERGENCE")
        rc = 1
    else:
        print("--- bound ---")
        print(f"agreement_run={limit} events{pmark} (no divergence in window)")
        if args.window and args.window > 0 and limit == args.window:
            end = "window-cap"
        elif n_ref == n_rt == limit:
            end = "both-exhausted"
        elif limit == n_rt:
            end = "rt-exhausted"
        else:
            end = "ref-exhausted"
        print(f"end={end} ref_events_after_start={n_ref} rt_events_after_start={n_rt}")
        if limit < n_ref:
            print(f"ref_next: {fmt_event(ref, at(limit)[0])}")
        if limit < n_rt:
            print(f"rt_next: {fmt_event(rt, at(limit)[1])}")
        print("result: NO-DIVERGENCE")
        rc = 0

    if args.locate and args.locate > 0:
        k = args.locate
        print("--- locate ---")
        if n_rt < k:
            print(f"rt has fewer than {k} post-start events; skipped")
        else:
            # NOTE: bytes(array('I')) would reinterpret raw memory; convert
            # via lists so each event is one byte (all real nums are u8).
            if ref_idx is None:
                needle = list(rt.nums[rt_start : rt_start + k])
                hay = list(ref.nums[ref_start:])
                ev_at = lambda s: ref_start + s  # noqa: E731
            else:
                needle = [rt.nums[t] for t in rt_idx[:k]]
                hay = [ref.nums[t] for t in ref_idx]
                ev_at = lambda s: ref_idx[s]  # noqa: E731
            try:
                pos = bytes(hay).find(bytes(needle))
            except ValueError:
                pos = -1  # a num > 0xFF exists; naive scan instead
                for s in range(len(hay) - len(needle) + 1):
                    if hay[s : s + len(needle)] == needle:
                        pos = s
                        break
            if pos < 0:
                print(f"rt opening {k}-shingle NOT FOUND in ref post-start window{pmark}")
            else:
                print(
                    f"rt opening {k}-shingle first occurs at ref ev:{ev_at(pos)} "
                    f"file:{ref.lines[ev_at(pos)]}{pmark}"
                )

    if milestones:
        ref_ms = ref_idx if ref_idx is not None else range(ref_start, len(ref))
        rt_ms = rt_idx if rt_idx is not None else range(rt_start, len(rt))
        print(f"--- milestones ref ({len(ref_ms)} events) ---")
        for t in ref_ms:
            print(f"  {fmt_ts(ref.ts[t])} {ref.name(t)} ({ref.nums[t]:x}) "
                  f"@file:{ref.lines[t]} ev:{t}")
        print(f"--- milestones rt ({len(rt_ms)} events) ---")
        for t in rt_ms:
            print(f"  {fmt_ts(rt.ts[t])} {rt.name(t)} ({rt.nums[t]:x}) "
                  f"@file:{rt.lines[t]} ev:{t}")

    if args.census:
        print("--- census (post-start) ---")
        # Full post-start ranges even under projection (n_ref/n_rt are the
        # compared/projected lengths; the census is the vocabulary table).
        cref = Counter(ref.name(t) for t in range(ref_start, len(ref)))
        crt = Counter(rt.name(t) for t in range(rt_start, len(rt)))
        print(f"{'name':40s} {'ref':>10s} {'rt':>10s}")
        for name, c in cref.most_common():
            print(f"{name:40s} {c:10d} {crt.get(name, 0):10d}")
        for name, c in crt.most_common():
            if name not in cref:
                print(f"{name:40s} {0:10d} {c:10d}")

    return rc


def cmd_format_check(paths):
    """Validate PCSX2 EE.Bios line shape + ts monotonicity. Returns 0/2."""
    rc = 0
    for path in paths:
        events = 0
        bad_ts = 0
        ts_viol = 0
        last_ts = None
        bad_hex = 0
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for lineno, line in enumerate(f, 1):
                m = LINE_RE.search(line)
                if not m:
                    continue
                events += 1
                name, hexpart = m.group(1), m.group(2)
                # %x shape: lowercase, no leading zeros (except "0" itself)
                canon = format(int(hexpart, 16), "x")
                if hexpart != canon:
                    bad_hex += 1
                    if bad_hex <= 5:
                        print(f"{path}:{lineno}: non-canon hex '{hexpart}' (want '{canon}')")
                t = TS_RE.match(line)
                if not t:
                    bad_ts += 1
                    if bad_ts <= 5:
                        print(f"{path}:{lineno}: missing PCSX2 ts prefix: {line.rstrip()[:90]}")
                else:
                    ts = float(t.group(1))
                    if last_ts is not None and ts < last_ts:
                        ts_viol += 1
                    last_ts = ts
        print(
            f"{path}: events={events} bad_hex={bad_hex} "
            f"bad_ts_prefix={bad_ts} ts_regressions={ts_viol}"
        )
        if events == 0 or bad_hex or bad_ts or ts_viol:
            rc = 2
    return rc


# ---------------- selftest ----------------

def _write(path, lines):
    with open(path, "w") as f:
        for t, name, num in lines:
            f.write(f"[{t:8.4f}] Bios    : Bios call: {name} ({num:x})\n")


def _args(**kw):
    d = dict(ref_after="none", rt_after="none", window=0, locate=0,
             census=False, context=2, drop_names=None, project=None,
             milestones=False)
    d.update(kw)
    return argparse.Namespace(**d)


def cmd_selftest():
    import io
    import tempfile
    from contextlib import redirect_stdout

    fails = []

    def check(tag, cond, detail=""):
        print(f"selftest {tag}: {'PASS' if cond else 'FAIL'} {detail}")
        if not cond:
            fails.append(tag)

    with tempfile.TemporaryDirectory() as td:
        # t1: identical -> exit 0
        ev = [(0.0001 * i, n, h) for i, (n, h) in enumerate(
            [("RFU060", 0x3C), ("RFU061", 0x3D), ("AddDmacHandler", 0x12),
             ("WaitSema", 0x44), ("SignalSema", 0x42)])]
        p1, p2 = f"{td}/a1.txt", f"{td}/b1.txt"
        _write(p1, ev)
        _write(p2, ev)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_align(_args(ref=p1, rt=p2))
        out = buf.getvalue()
        check("t1-identical-exit0", rc == 0, f"rc={rc}")
        check("t1-identical-run5", "agreement_run=5" in out)

        # t2: grafted substitution at k=3 -> exit 1, names the lines
        ev2 = [e for e in ev]
        ev2[3] = (ev2[3][0], "PollSema", 0x45)
        p3 = f"{td}/b2.txt"
        _write(p3, ev2)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_align(_args(ref=p1, rt=p3))
        out = buf.getvalue()
        check("t2-grafted-exit1", rc == 1, f"rc={rc}")
        check("t2-grafted-k3", "k=3" in out)
        check("t2-grafted-names",
              "WaitSema (44)" in out and "PollSema (45)" in out)

        # t3: ref-after skips to 2nd ExecPS2
        evr = [(0.001 * i, n, h) for i, (n, h) in enumerate(
            [("RFU060", 0x3C), ("ExecPS2", 0x7), ("RFU005", 0x5),
             ("ExecPS2", 0x7), ("WaitSema", 0x44), ("SignalSema", 0x42)])]
        evt = [(0.001 * i, n, h) for i, (n, h) in enumerate(
            [("WaitSema", 0x44), ("SignalSema", 0x42)])]
        p4, p5 = f"{td}/r3.txt", f"{td}/t3.txt"
        _write(p4, evr)
        _write(p5, evt)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_align(_args(ref=p4, rt=p5, ref_after="ExecPS2:2"))
        out = buf.getvalue()
        check("t3-anchor-exit0", rc == 0, f"rc={rc}")
        check("t3-anchor-hit", "HIT ev:4" in out)
        check("t3-anchor-run2", "agreement_run=2" in out)

        # t4: anchor miss -> exit 2 with MISS table
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_align(_args(ref=p5, rt=p5, ref_after="ExecPS2:2"))
        out = buf.getvalue()
        check("t4-miss-exit2", rc == 2, f"rc={rc}")
        check("t4-miss-table", "MISS" in out and "ANCHOR-MISS" in out)

        # t5: same number, different name -> NOT a divergence
        ev6 = [(0.0001 * i, n, h) for i, (n, h) in enumerate(
            [("RFU060", 0x3C), ("SetupHeap_ALIAS", 0x3D)])]
        p6 = f"{td}/b5.txt"
        _write(p6, ev6)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_align(_args(ref=p1, rt=p6, window=2))
        out = buf.getvalue()
        check("t5-aliasname-exit0", rc == 0, f"rc={rc}")
        check("t5-aliasname-row", "name_mismatches=1" in out)

        # t6: format-check good + bad
        rc_good = cmd_format_check([p1])
        pbad = f"{td}/bad.txt"
        with open(pbad, "w") as f:
            f.write("Bios call: WaitSema (44)\n")  # no ts prefix
            f.write("[  0.0002] Bios    : Bios call: PollSema (0x45)\n")  # bad hex shape
        # (second line won't parse as event; first parses but lacks ts)
        rc_bad = cmd_format_check([pbad])
        check("t6-format-good", rc_good == 0, f"rc={rc_good}")
        check("t6-format-bad", rc_bad == 2, f"rc={rc_bad}")

        # t7: locate shingle
        evr7 = [(0.001 * i, n, h) for i, (n, h) in enumerate(
            [("RFU060", 0x3C), ("RFU061", 0x3D), ("WaitSema", 0x44),
             ("SignalSema", 0x42), ("PollSema", 0x45)])]
        evt7 = [(0.001 * i, n, h) for i, (n, h) in enumerate(
            [("WaitSema", 0x44), ("SignalSema", 0x42)])]
        p7, p8 = f"{td}/r7.txt", f"{td}/t7.txt"
        _write(p7, evr7)
        _write(p8, evt7)
        buf = io.StringIO()
        with redirect_stdout(buf):
            cmd_align(_args(ref=p7, rt=p8, window=0, locate=2))
        out = buf.getvalue()
        check("t7-locate", "ref ev:2" in out)

        # t8: rt shorter, all agree -> exit 0, rt-exhausted bound
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_align(_args(ref=p1, rt=p6))
        out = buf.getvalue()
        check("t8-short-exit0", rc == 0, f"rc={rc}")
        check("t8-short-bound", "end=rt-exhausted" in out)

        # t9: --drop-names removes pump events from BOTH sides before compare.
        # ref=[A,Pump,B] rt=[A,Pump,C]: undropped k=2, dropped k=1.
        evr9 = [(0.001 * i, n, h) for i, (n, h) in enumerate(
            [("RFU060", 0x3C), ("WaitSema", 0x44), ("AddDmacHandler", 0x12)])]
        evt9 = [(0.001 * i, n, h) for i, (n, h) in enumerate(
            [("RFU060", 0x3C), ("WaitSema", 0x44), ("CreateSema", 0x40)])]
        p9r, p9t = f"{td}/r9.txt", f"{td}/t9.txt"
        _write(p9r, evr9)
        _write(p9t, evt9)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_align(_args(ref=p9r, rt=p9t, drop_names="WaitSema"))
        out = buf.getvalue()
        check("t9-drop-exit1", rc == 1, f"rc={rc}")
        check("t9-drop-k1", "k=1 (projected)" in out)
        check("t9-drop-table", "WaitSema ref=1 rt=1" in out)
        check("t9-drop-projcounts", "ref_proj=2 rt_proj=2" in out)

        # t10: --project shared applies the 15-name preset.
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_align(_args(ref=p9r, rt=p9t, project="shared"))
        out = buf.getvalue()
        check("t10-shared-exit1", rc == 1, f"rc={rc}")
        check("t10-shared-k1", "k=1 (projected)" in out)
        check("t10-shared-table", "project=shared drops=15" in out
              and "GetThreadId ref=0 rt=0" in out)

        # t11: unknown drop-name -> matched=0 row, exit unaffected.
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_align(_args(ref=p9r, rt=p9t, drop_names="NoSuchCall"))
        out = buf.getvalue()
        check("t11-unknown-exit1", rc == 1, f"rc={rc}")
        check("t11-unknown-k2", "k=2 (projected)" in out)
        check("t11-unknown-row", "NoSuchCall ref=0 rt=0" in out)

        # t12: --milestones prints stamped rare-vocabulary sequences, both sides.
        # Census stays full post-start under projection (regression: it once
        # counted only the first len(projected) post-start events).
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_align(_args(ref=p9r, rt=p9t, project="shared",
                                 milestones=True, census=True))
        out = buf.getvalue()
        check("t12-mile-exit1", rc == 1, f"rc={rc}")
        check("t12-mile-ref", "--- milestones ref (2 events) ---" in out
              and "AddDmacHandler (12)" in out)
        check("t12-mile-rt", "--- milestones rt (2 events) ---" in out
              and "CreateSema (40)" in out)
        check("t12-mile-stamps", "0.0000" in out and "0.0020" in out)
        check("t12-mile-pumpgone", "WaitSema (44)" not in out.split("--- milestones")[1])
        check("t12-mile-censusfull", "AddDmacHandler" in out.split("--- census")[1]
              and "CreateSema" in out.split("--- census")[1])

        # t13: unknown --project preset -> exit 2, no anchor table.
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_align(_args(ref=p9r, rt=p9t, project="bogus"))
        out = buf.getvalue()
        check("t13-badproject-exit2", rc == 2, f"rc={rc}")
        check("t13-badproject-msg", "unknown preset 'bogus'" in out
              and "USAGE-ERROR" in out)

    print(f"selftest: {'ALL PASS' if not fails else 'FAILURES: ' + ','.join(fails)}")
    return 0 if not fails else 2


def main(argv=None):
    ap = argparse.ArgumentParser(description="first-divergence EE.Bios aligner (T18)")
    ap.add_argument("ref", nargs="?", help="reference trace (full emulog or EE-only)")
    ap.add_argument("rt", nargs="?", help="runtime channel file")
    ap.add_argument("--ref-after", default="ExecPS2:2",
                    help="skip ref until after OCC-th NAME (default ExecPS2:2; 'none')")
    ap.add_argument("--rt-after", default="none",
                    help="skip rt until after OCC-th NAME (default none)")
    ap.add_argument("--window", type=int, default=0, help="max events to compare (0=all)")
    ap.add_argument("--locate", type=int, default=0,
                    help="locate rt's opening K-shingle in ref (0=off)")
    ap.add_argument("--census", action="store_true", help="print post-start per-name census")
    ap.add_argument("--context", type=int, default=5, help="divergence context events")
    ap.add_argument("--drop-names", default=None, metavar="N,...",
                    help="drop exact-name events from both sides (comma list; "
                    "unknown names table matched=0, non-fatal)")
    ap.add_argument("--project", default=None, metavar="PRESET",
                    help="projection preset: only 'shared' (F3 S19: SIF layer, "
                    "sema pump, GetThreadId, FlushCache, RFU005)")
    ap.add_argument("--milestones", action="store_true",
                    help="print stamped projected sequences, both sides")
    ap.add_argument("--format-check", nargs="+", metavar="FILE",
                    help="validate PCSX2 line shape of FILEs")
    ap.add_argument("--selftest", action="store_true", help="run synthetic self-tests")
    args = ap.parse_args(argv)

    if args.selftest:
        return cmd_selftest()
    if args.format_check:
        return cmd_format_check(args.format_check)
    if not args.ref or not args.rt:
        ap.print_usage(sys.stderr)
        return 2
    return cmd_align(args)


if __name__ == "__main__":
    sys.exit(main())
