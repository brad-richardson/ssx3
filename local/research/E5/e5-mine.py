#!/usr/bin/env python3
"""E5 miner: join the PC-anchored display-reg write series to the E4-shape chain.

Inputs (SSD canonical): boot-e5-1.log, e5-1/{e4-history.txt,e4-present.txt}.
Comparators: boot-k1-1.log [gs:prim] prefix, local E4 history shape.
Outputs: stdout tables + e5-watch-series.txt (deduped series) in CWD.

Dedup: each MMIO store emits TWO identical [diag:watch] lines (WRITE-macro
pre-split report + Store* report); consecutive identical lines collapse.
PMODE anomaly (single vs pair) is counted, not assumed.
"""
import os
import re
import sys

W = "/Volumes/Extreme SSD/ps2recomp-spike"
RUN = os.path.join(W, "P1/run")
LOG = os.path.join(RUN, "boot-e5-1.log")
E5D = os.path.join(RUN, "e5-1")
K1LOG = os.path.join(RUN, "boot-k1-1.log")

REGNAME = {
    0x12000000: "PMODE", 0x12000020: "SMODE2", 0x12000070: "DISPFB1",
    0x12000080: "DISPLAY1", 0x12000090: "DISPFB2", 0x120000A0: "DISPLAY2",
    0x120000E0: "BGCOLOR",
}

watch_re = re.compile(
    r"diag:watch\] addr=0x([0-9a-f]+) width=(\d+) value=0x([0-9a-f]+)"
    r" pc=0x([0-9a-f]+) thread=(-?\d+) ra=0x([0-9a-f]+) sp=0x([0-9a-f]+)")
dump_re = re.compile(r"frame:dump\] seq=(\d+) tick=(\d+) size=(\S+) fbp=(\S+)")
prim_re = re.compile(r"\[gs:prim\]")


def main():
    with open(LOG, "r", errors="replace") as f:
        lines = f.readlines()
    print(f"log_lines={len(lines)}")

    armed_ln = frozen_ln = None
    dumps = []          # (line#, seq, tick, size, fbp)
    prims = []          # raw [gs:prim] lines (first 64)
    watches = []        # (line#, addr, width, value, pc, thread, ra, sp)
    for i, ln in enumerate(lines):
        if "[e4:armed]" in ln and armed_ln is None:
            armed_ln = i
        if "[e4:frozen]" in ln and frozen_ln is None:
            frozen_ln = i
        m = dump_re.search(ln)
        if m:
            dumps.append((i, int(m.group(1)), int(m.group(2)), m.group(3), m.group(4)))
        if prim_re.search(ln) and len(prims) < 64:
            prims.append(ln.rstrip("\n"))
        m = watch_re.search(ln)
        if m:
            g = m.groups()
            watches.append((i, int(g[0], 16), int(g[1]), int(g[2], 16),
                            int(g[3], 16), int(g[4]), int(g[5], 16), int(g[6], 16)))
    print(f"armed_ln={armed_ln} frozen_ln={frozen_ln} "
          f"dumps={len(dumps)} prims={len(prims)} watch_raw={len(watches)}")

    # --- determinism re-verify: [gs:prim] prefix vs K1 ---
    k1prims = []
    with open(K1LOG, "r", errors="replace") as f:
        for ln in f:
            if prim_re.search(ln):
                k1prims.append(ln.rstrip("\n"))
                if len(k1prims) >= 64:
                    break
    print(f"k1prims={len(k1prims)} e5prims={len(prims)} "
          f"prefix_identical={k1prims == prims}")

    # --- first-upload tick + transition ---
    trans = [(s, t) for (_, s, t, _, _) in dumps]
    first_success = next(((s, t) for (_, s, t, sz, _) in dumps if sz == "512x448"), None)
    last_fallback = next(((s, t) for (_, s, t, sz, _) in reversed(dumps) if sz == "640x512"), None)
    print(f"last_fallback_seq_tick={last_fallback} first_success_seq_tick={first_success}")

    # --- dedupe consecutive identical watch lines ---
    dedup = []
    i = 0
    pair_hist = {}
    while i < len(watches):
        j = i + 1
        while j < len(watches) and watches[j][1:] == watches[i][1:]:
            j += 1
        run = j - i
        key = (watches[i][1], run)
        pair_hist[key] = pair_hist.get(key, 0) + 1
        dedup.append(watches[i] + (run,))
        i = j
    print(f"watch_dedup={len(dedup)}")
    print("runlen_census(addr x runlen: bursts):")
    for (addr, runlen), n in sorted(pair_hist.items()):
        print(f"  {REGNAME.get(addr, hex(addr))} x{runlen}: {n}")

    # --- tick attribution: nearest dump tick at-or-before each watch line ---
    dump_ticks = sorted(dumps)  # by line#
    def tick_at(ln):
        best = None
        for (dln, _s, t, _sz, _fbp) in dump_ticks:
            if dln <= ln:
                best = t
            else:
                break
        return best

    # --- value census per reg (deduped) ---
    from collections import Counter
    print("value_census_per_reg(deduped):")
    for addr in sorted({d[1] for d in dedup}):
        vals = Counter(d[3] for d in dedup if d[1] == addr)
        top = " ".join(f"0x{v:x}x{n}" for v, n in vals.most_common(6))
        print(f"  {REGNAME.get(addr, hex(addr))}: distinct={len(vals)} {top}")

    # --- pc census per reg (deduped) ---
    print("pc_census_per_reg(deduped):")
    for addr in sorted({d[1] for d in dedup}):
        pcs = Counter((d[4], d[6]) for d in dedup if d[1] == addr)
        top = " ".join(f"pc=0x{pc:x}/ra=0x{ra:x}x{n}" for (pc, ra), n in pcs.most_common(4))
        print(f"  {REGNAME.get(addr, hex(addr))}: {top}")

    # --- thread census ---
    print(f"thread_census(deduped): {Counter(d[5] for d in dedup)}")

    # --- first burst (boot display-init): first deduped write per reg in order ---
    seen = set()
    first_burst = []
    for d in dedup:
        if d[1] not in seen:
            seen.add(d[1])
            first_burst.append(d)
        if len(seen) >= 5:
            # keep scanning a bit to catch BGCOLOR if ordered later
            pass
        if len(first_burst) >= 7:
            break
    print("first_burst_first_write_per_reg:")
    for (ln, addr, w, v, pc, th, ra, sp, _run) in first_burst:
        print(f"  ln={ln} tick~{tick_at(ln)} {REGNAME.get(addr, hex(addr))} "
              f"width={w} value=0x{v:x} pc=0x{pc:x} thread={th} ra=0x{ra:x}")

    # --- steady window: deduped writes with armed_ln < ln < frozen_ln ---
    inwin = [d for d in dedup if armed_ln is not None and frozen_ln is not None
             and armed_ln < d[0] < frozen_ln]
    print(f"in_window_dedup={len(inwin)} (raw lines in window: "
          f"{sum(1 for w in watches if armed_ln < w[0] < frozen_ln)})")
    for addr in sorted({d[1] for d in inwin}):
        vals = Counter(d[3] for d in inwin if d[1] == addr)
        pcs = Counter(d[4] for d in inwin if d[1] == addr)
        ths = Counter(d[5] for d in inwin if d[1] == addr)
        print(f"  {REGNAME.get(addr, hex(addr))}: n={sum(vals.values())} "
              f"vals={['0x%x' % v for v in vals]} "
              f"pcs={['0x%x' % p for p in pcs]} threads={dict(ths)}")

    # --- whole-run: any DISPFB1 value other than 0x9070? ---
    disp = [(ln, v, pc, th) for (ln, a, _w, v, pc, th, _ra, _sp, _r) in dedup
            if a == 0x12000070 and v != 0x9070]
    print(f"dispfb1_nonsteady_values={len(disp)}")
    for ln, v, pc, th in disp[:10]:
        print(f"  ln={ln} tick~{tick_at(ln)} value=0x{v:x} pc=0x{pc:x} thread={th}")
    pm = [(ln, v, pc, th) for (ln, a, _w, v, pc, th, _ra, _sp, _r) in dedup
          if a == 0x12000000 and v != 0xFF21]
    print(f"pmode_nonsteady_values={len(pm)}")
    for ln, v, pc, th in pm[:10]:
        print(f"  ln={ln} tick~{tick_at(ln)} value=0x{v:x} pc=0x{pc:x} thread={th}")

    # --- E5 frozen history shape vs E4 ---
    with open(os.path.join(E5D, "e4-history.txt")) as f:
        h = f.read()
    import re as _re
    m = _re.search(r"# E4 history arm=(\d+) freeze=(\d+) entries=(\d+)", h)
    c = _re.search(r"# census tick=(\d+) draws=(\d+)(.*)", h)
    cov = _re.search(r"# coverage firstSeq=(\d+) firstTick=(\d+) lastSeq=(\d+) lastTick=(\d+)", h)
    kinds = _re.findall(r"kind=(\w+)", h)
    gif_disp = len(_re.findall(r"reg=0x5[9abcf]\b", h))
    print(f"e5_history: {m.groups() if m else None} census={c.groups() if c else None} "
          f"coverage={cov.groups() if cov else None}")
    print(f"e5_history_kinds: {Counter(kinds)} gif_0x59_0x5c_events={gif_disp}")
    with open(os.path.join(E5D, "e4-present.txt")) as f:
        print("e5_present: " + f.read().replace("\n", " | "))

    # --- write compact deduped series ---
    with open("e5-watch-series.txt", "w") as f:
        f.write("# E5 deduped display-reg MMIO write series "
                "(ln tick~ reg width value pc thread ra xrunlen)\n")
        for (ln, addr, w, v, pc, th, ra, _sp, run) in dedup:
            f.write(f"{ln} {tick_at(ln)} {REGNAME.get(addr, hex(addr))} "
                    f"{w} 0x{v:x} 0x{pc:x} {th} 0x{ra:x} x{run}\n")
    print("wrote e5-watch-series.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
