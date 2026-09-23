#!/usr/bin/env python3
"""E44 analyzer: summarize spw (scratchpad write watch) lines + Part-4
append/template streams (app, tpl, tplrearm, tplm, appsum, apc, appx,
v1b0).

Usage:
  python3 local/research/E44/e44_analyze.py <trace.txt>

Prints per-word writer tables: (vsync range, n, via, value set, pc set,
ra set, fn set, src set) plus the full register state of the first line
per (addr, via, pc) for the codegen join. Part 4: app count/tw0/ra
summary, tpl setter table per new value, tplm/appx/v1b0 rows,
appsum/apc per-vsync series.
"""

import sys
from collections import Counter, defaultdict

REG_FIELDS = ("a0 a1 a2 a3 v0 v1 t0 t1 t2 t3 t4 t5 t6 t7 t8 t9 "
              "s0 s1 s2 s3 s4 s5 s6 s7").split()


P4_KINDS = ("app", "tpl", "tplrearm", "tplm", "appsum", "apc",
              "appx", "v1b0", "tw")


def parse_kv(line, keys):
    d = {}
    for p in line.split()[1:]:
        if "=" not in p:
            raise ValueError(p)
        k, v = p.split("=", 1)
        d[k] = v
    for k in keys:
        if k not in d:
            raise ValueError(k)
    d["vsync"] = int(d["vsync"])
    return d


def parse(path):
    rows = []
    eb = []
    last = []
    p4 = {k: [] for k in P4_KINDS}
    torn = 0
    with open(path, errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("ebwlast "):
                try:
                    eb.append(parse_kv(line, ("vsync", "addr", "value",
                                              "via", "pc", "ra", "fn")))
                except ValueError:
                    torn += 1
                continue
            if line.startswith("spwlast "):
                last.append(line)
                continue
            handled = False
            for kind in P4_KINDS:
                if line.startswith(kind + " "):
                    # "tpl " must not catch "tplm "/"tplrearm": the
                    # trailing space in the prefix guards it.
                    try:
                        p4[kind].append(parse_kv(line, ("vsync",)))
                    except ValueError:
                        torn += 1
                    handled = True
                    break
            if handled:
                continue
            if not line.startswith("spw "):
                continue
            try:
                d = parse_kv(line, ("vsync", "addr", "value", "via",
                                    "src", "pc", "ra", "fn") +
                             tuple(REG_FIELDS))
                rows.append(d)
            except ValueError:
                torn += 1
    return rows, eb, last, p4, torn


def vspan(rs):
    vs = sorted(r["vsync"] for r in rs)
    return f"{vs[0]}..{vs[-1]} ({len(vs)} distinct)" if vs else "-"


def main():
    path = sys.argv[1]
    rows, eb, last, p4, torn = parse(path)
    print(f"file={path} spw_rows={len(rows)} ebwlast_rows={len(eb)} "
          f"spwlast_rows={len(last)} torn={torn}")
    for k in P4_KINDS:
        if p4[k]:
            print(f"  {k}_rows={len(p4[k])} vsync={vspan(p4[k])}")
    if p4["app"]:
        app = p4["app"]
        counts = sorted(set(int(r["count"]) for r in app))
        print(f"\n## app ({len(app)}): count min={counts[0]} max={counts[-1]} "
              f"distinct={len(counts)}")
        print(f"  tw0={sorted(set(r['tw0'] for r in app))}")
        print(f"  ra={sorted(set(r['ra'] for r in app))}")
        print(f"  t0={sorted(set(r['t0'] for r in app))}")
        print(f"  s4 arenas={sorted(set(r['s4'] for r in app))[:8]}")
        print("  first 40:")
        for r in app[:40]:
            print(f"    vsync={r['vsync']} count={r['count']} t0={r['t0']} "
                  f"tw0={r['tw0']} tw1={r['tw1']} s4={r['s4']} ra={r['ra']}")
    if p4["tpl"]:
        tpl = p4["tpl"]
        print(f"\n## tpl ({len(tpl)}): setter pc->ra per new value")
        by_new = defaultdict(set)
        for r in tpl:
            by_new[(r["addr"], r["new"])].add((r["pc"], r["ra"]))
        for (addr, new), prs in sorted(by_new.items()):
            print(f"  {addr} -> {new}: {sorted(prs)[:6]}")
    for kind in ("tplrearm", "tplm", "appx", "v1b0"):
        if p4[kind]:
            print(f"\n## {kind} ({len(p4[kind])} rows)")
            for r in p4[kind][:60]:
                vals = " ".join(f"{k}={r[k]}" for k in sorted(r) if k != "vsync")
                print(f"  vsync={r['vsync']} {vals[:300]}")
    if p4["tw"]:
        tw = p4["tw"]
        print(f"\n## tw ({len(tw)}): vsync={vspan(tw)}")
        by_an = defaultdict(set)
        for r in tw:
            by_an[(r.get("addr"), r.get("new"))].add(
                (r.get("pc"), r.get("ra")))
        for (addr, new), prs in sorted(by_an.items()):
            print(f"  {addr} -> {new}: {sorted(prs)[:4]}")
    if p4["appsum"]:
        print(f"\n## appsum ({len(p4['appsum'])} rows)")
        for r in p4["appsum"][:80]:
            print(f"  vsync={r['vsync']} n_app={r.get('n_app')} "
                  f"n_tpl={r.get('n_tpl')} mode_hist={r.get('mode_hist')}")
    if p4["apc"]:
        apc = p4["apc"]
        print(f"\n## apc ({len(apc)} rows)")
        by_vs = defaultdict(list)
        for r in apc:
            by_vs[r["vsync"]].append((r.get("pc"), r.get("count")))
        vss = sorted(by_vs)
        print(f"  vsync span {vss[0]}..{vss[-1]}; distinct pcs: "
              f"{sorted(set(p for v in vss for p, _ in by_vs[v]))}")
        for v in vss[:30]:
            print(f"  vsync={v} " + " ".join(f"{p}x{c}" for p, c in by_vs[v]))
    if eb:
        print("\n## ebwlast (last writer per word per changed vsync)")
        for r in eb:
            print(f"  vsync={r['vsync']} addr={r['addr']} value={r['value']} "
                  f"via={r['via']} pc={r['pc']} ra={r['ra']} fn={r['fn']}")
    if last:
        print(f"\n## spwlast ({len(last)} lines)")
        for line in last[:45]:
            print(f"  {line[:360]}")
    by_addr = defaultdict(list)
    for r in rows:
        by_addr[r["addr"]].append(r)
    for addr in sorted(by_addr):
        rs = by_addr[addr]
        vs = sorted(r["vsync"] for r in rs)
        print(f"\n## {addr} n={len(rs)} vsync={vs[0]}..{vs[-1]}")
        print(f"  value={sorted(set(r['value'] for r in rs))}")
        print(f"  via={sorted(set(r['via'] for r in rs))}")
        print(f"  pc={sorted(set(r['pc'] for r in rs))}")
        print(f"  ra={sorted(set(r['ra'] for r in rs))}")
        print(f"  fn={sorted(set(r['fn'] for r in rs))}")
        print(f"  src={sorted(set(r['src'] for r in rs))}")
        seen = set()
        for r in rs:
            key = (r["via"], r["pc"])
            if key in seen:
                continue
            seen.add(key)
            regs = " ".join(f"{k}={r[k]}" for k in REG_FIELDS)
            print(f"  first via={r['via']} pc={r['pc']} vsync={r['vsync']} "
                  f"value={r['value']} src={r['src']} ra={r['ra']} fn={r['fn']}")
            print(f"    {regs}")


if __name__ == "__main__":
    main()
