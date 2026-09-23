#!/usr/bin/env python3
"""GB3: compare [vq] quiescent samples (vram/regs/present) + pklog streams.

Usage:
  python3 local/research/GB3/gb3_vq.py <boot-A.log> <boot-B.log> \
      [--pk <pklog-A.txt> <pklog-B.txt>] [--gate-from 100 --gate-to 1350 --gate-step 50] \
      [--fields vram,regs] [--table]

Parses GB3 lines:
  [vq] tick=100 vram=.. regs=.. size=.. sub=.. reg=.. priv=.. pres=.. pw=.. ph=..
(GB2 lines without priv/pres also parse; missing fields read "-").

Gate = the `--fields` (default vram,regs) identical at every matched tick
inside the gate window (default GB2's 26 ticks 100..1350 step 50). Ticks
outside the window are reported as "extra" (same comparison, not gating).
With --pk: packet streams compared row-for-row (tick+fnv+len+src) and the
first differing [pk] / [csr] row is printed. Exit 0 iff the gate passes.
"""
import argparse
import re
import sys

VQ_RE = re.compile(r"\[vq\] tick=(\d+) (.*)$")
KV_RE = re.compile(r"(\w+)=(\S+)")


def parse_vq(path):
    vq, armed = {}, False
    with open(path, "rb") as f:
        for raw in f:
            line = raw.decode("utf-8", "replace").rstrip("\n")
            if "[vq] armed" in line:
                armed = True
                continue
            m = VQ_RE.search(line)
            if m:
                vq[int(m.group(1))] = dict(KV_RE.findall(m.group(2)))
    return vq, armed


def parse_pk(path):
    pk, csr = [], []
    with open(path, "rb") as f:
        for raw in f:
            line = raw.decode("utf-8", "replace").strip()
            if line.startswith("[pk]"):
                d = dict(KV_RE.findall(line))
                pk.append((d.get("tick"), d.get("fnv"), d.get("len"), d.get("src")))
            elif line.startswith("[csr]"):
                d = dict(KV_RE.findall(line))
                csr.append((d.get("tick"), d.get("value"), d.get("pc"), d.get("addr")))
    return pk, csr


def first_diff(a, b):
    n = min(len(a), len(b))
    for i in range(n):
        if a[i] != b[i]:
            return i
    return None if len(a) == len(b) else n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--pk", nargs=2, default=None)
    ap.add_argument("--gate-from", type=int, default=100)
    ap.add_argument("--gate-to", type=int, default=1350)
    ap.add_argument("--gate-step", type=int, default=50)
    ap.add_argument("--fields", default="vram,regs")
    ap.add_argument("--table", action="store_true", help="print every matched tick")
    args = ap.parse_args()
    fields = args.fields.split(",")

    A, a_armed = parse_vq(args.a)
    B, b_armed = parse_vq(args.b)
    print(f"A: {len(A)} vq samples armed={a_armed}  ({args.a})")
    print(f"B: {len(B)} vq samples armed={b_armed}  ({args.b})")
    if not (a_armed and b_armed):
        print("REFUSE: VQ not armed in both boots")
        return 2
    common = sorted(set(A) & set(B))
    gate = [t for t in common if args.gate_from <= t <= args.gate_to
            and (t - args.gate_from) % args.gate_step == 0]
    extra = [t for t in common if t not in gate]
    print(f"matched ticks: {len(common)} (gate {len(gate)}, extra {len(extra)})")

    def row(t):
        a, b = A[t], B[t]
        ok = all(a.get(k) == b.get(k) for k in fields)
        cols = [f"{a.get(k, '-')}/{b.get(k, '-')}" for k in ("vram", "regs", "pres")]
        return ok, cols, a, b

    print()
    print("| tick | vram A/B | regs A/B | pres A/B | sub A/B | priv A/B | pw×ph A/B | verdict |")
    print("|---|---|---|---|---|---|---|---|")
    gate_mism, extra_mism, first = 0, 0, None
    pres_mism = 0
    for t in common:
        ok, cols, a, b = row(t)
        in_gate = t in gate
        if not ok:
            if in_gate:
                gate_mism += 1
            else:
                extra_mism += 1
            if first is None:
                first = t
        if a.get("pres") != b.get("pres"):
            pres_mism += 1
        if args.table or not ok or in_gate:
            print(f"| {t} | {cols[0]} | {cols[1]} | {cols[2]} | {a.get('sub', '-')}/{b.get('sub', '-')} | "
                  f"{a.get('priv', '-')}/{b.get('priv', '-')} | {a.get('pw', '-')}x{a.get('ph', '-')}/"
                  f"{b.get('pw', '-')}x{b.get('ph', '-')} | {'OK' if ok else 'MISMATCH'}"
                  f"{'' if in_gate else ' (extra)'} |")
    print()
    print(f"gate: {len(gate) - gate_mism}/{len(gate)} match on {fields}; extra: "
          f"{len(extra) - extra_mism}/{len(extra)}; present-hash mismatches (all matched ticks): "
          f"{pres_mism}/{len(common)}")
    if first is not None:
        print(f"FIRST MISMATCH tick {first}")

    if args.pk:
        pa, ca = parse_pk(args.pk[0])
        pb, cb = parse_pk(args.pk[1])
        n = min(len(pa), len(pb))
        d = first_diff(pa[:n], pb[:n])
        print()
        print(f"pk rows A={len(pa)} B={len(pb)} compared={n}: "
              f"{'IDENTICAL' if d is None else f'first diff idx {d}: A={pa[d]} B={pb[d]}'}")
        m = min(len(ca), len(cb))
        dc = first_diff(ca[:m], cb[:m])
        print(f"csr rows A={len(ca)} B={len(cb)} compared={m}: "
              f"{'IDENTICAL' if dc is None else f'first diff idx {dc}: A={ca[dc]} B={cb[dc]}'}")
    return 0 if gate_mism == 0 and gate else 1


if __name__ == "__main__":
    sys.exit(main())
