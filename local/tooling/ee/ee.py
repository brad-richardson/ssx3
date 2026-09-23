#!/usr/bin/env python3
"""EE (SSX 3 main CPU) lookup helpers for workers: exact facts, no guessing.

  ee-at    <addr> [before=8] [after=8]  disassembly window (delay slots included)
  ee-func  <addr>                       owning function(s) from the function map
  ee-xref  <addr> [--range N]           who calls/references an address
  ee-label <addr> | syscall <N>         authoritative names only, else "unknown"

Sources (read-only): generated code comments in $EE_CODEGEN (default
~/dev/ssx3-work/codegen-ssx3), ~/dev/PS2Recomp/games/ssx3/ (function-map CSV,
ssx3.toml), PS2Recomp Dispatcher.cpp (syscall names), the ELF, boot logs under
~/dev/ssx3-work/*-run/, and local/tooling/ee/labels.tsv (orchestrator-verified
labels). The index is cached in ~/dev/ssx3-work/ee-cache/ (first run ~20 s).
"""
import csv, glob, os, pickle, re, struct, subprocess, sys

HOME = os.path.expanduser("~")
CODEGEN = os.environ.get("EE_CODEGEN", f"{HOME}/dev/ssx3-work/codegen-ssx3")
FORK = os.environ.get("EE_FORK", f"{HOME}/dev/PS2Recomp")
CSV = f"{FORK}/games/ssx3/ssx3-functions.sweep.csv"
TOML = f"{FORK}/games/ssx3/ssx3.toml"
DISPATCHER = f"{FORK}/ps2xRuntime/src/lib/Kernel/Syscalls/Dispatcher.cpp"
ELF = os.environ.get("EE_ELF", f"{HOME}/dev/ssx3-work/E32-inputs/cd/SLUS_207.72")
RUNLOGS = f"{HOME}/dev/ssx3-work/*-run/boot-*.log"
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
LABELS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "labels.tsv")
HANDOFF = os.path.join(REPO, "docs/archive/ssx3-120hz-handoff-2026-09-13.md")
CACHE = f"{HOME}/dev/ssx3-work/ee-cache"

LINE = re.compile(r"^\s*// 0x([0-9a-f]+): 0x([0-9a-f]+)\s+(.*?)\s*$")
IMM = r"(-?0x[0-9A-Fa-f]+|-?\d+)"


def parse_addr(s):
    s = s.strip().lower()
    for p in ("sub_", "func_", "label_"):
        if s.startswith(p):
            s = s[len(p):]
    return int(s, 16) if not s.startswith("0x") else int(s, 16)


def norm_text(t):
    ds = t.endswith("(Delay Slot)")
    if ds:
        t = t[: -len("(Delay Slot)")].rstrip()
    m = re.match(r"\.word\s+0x[0-9a-f]+\s+#\s*(.*?)(\s+#.*)?$", t)
    if m:  # instructions the decoder printed as .word with a comment
        t = m.group(1).strip()
    return re.sub(r"\s+", " ", t), ds


def build_index():
    files = sorted(glob.glob(os.path.join(CODEGEN, "sub_*.cpp")))
    key = (CODEGEN, len(files), max(os.path.getmtime(f) for f in files))
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, "index-" + re.sub(r"[^A-Za-z0-9]", "_", CODEGEN)[-60:] + ".pkl")
    if os.path.exists(path):
        with open(path, "rb") as f:
            data = pickle.load(f)
        if data["key"] == key:
            return data
    sys.stderr.write(f"[ee] indexing {len(files)} files in {CODEGEN} (one-time)...\n")
    ins = {}
    for fn in files:
        with open(fn, errors="replace") as f:
            for line in f:
                if "// 0x" not in line:
                    continue
                m = LINE.match(line)
                if m:
                    a = int(m.group(1), 16)
                    if a not in ins:
                        text, ds = norm_text(m.group(3))
                        ins[a] = (int(m.group(2), 16), text, ds)
    xref = build_xref(ins)
    data = {"key": key, "ins": ins, "xref": xref}
    try:
        with open(path, "wb") as f:
            pickle.dump(data, f)
    except OSError as e:  # sandboxed workers may not write outside their workspace
        sys.stderr.write(f"[ee] cache not saved ({e}); continuing in memory\n")
    return data


def build_xref(ins):
    """Static references: jal/j targets and lui+addiu/ori/load/store pairs."""
    xref = {}
    addrs = sorted(ins)
    pos = {a: i for i, a in enumerate(addrs)}
    for a in addrs:
        text = ins[a][1]
        m = re.match(r"(jal|j)\s+func_([0-9A-Fa-f]+)", text)
        if m:
            xref.setdefault(int(m.group(2), 16), []).append((a, m.group(1)))
            continue
        m = re.match(r"lui\s+\$(\w+),\s*" + IMM, text)
        if not m:
            continue
        reg, hi = m.group(1), int(m.group(2), 0) & 0xFFFF
        i = pos[a]
        for b in addrs[i + 1 : i + 9]:
            if b - a > 36:
                break
            t = ins[b][1]
            m2 = re.match(r"(addiu|daddiu|ori)\s+\$(\w+),\s*\$(\w+),\s*" + IMM, t)
            if m2 and m2.group(3) == reg:
                lo = int(m2.group(4), 0)
                tgt = ((hi << 16) | (lo & 0xFFFF)) if m2.group(1) == "ori" else ((hi << 16) + lo)
                xref.setdefault(tgt & 0xFFFFFFFF, []).append((b, f"lui@{a:#x}+{m2.group(1)}"))
                if m2.group(2) == reg:
                    break
                continue
            m3 = re.match(r"(l[bhwdq]u?|lwc1|lqc2|s[bhwdq]|swc1|sqc2|ld[lr]|sd[lr]|lw[lr]|sw[lr])\s+\$\w+,\s*" + IMM + r"\(\$(\w+)\)", t)
            if m3 and m3.group(3) == reg:
                tgt = (hi << 16) + int(m3.group(2), 0)
                xref.setdefault(tgt & 0xFFFFFFFF, []).append((b, f"lui@{a:#x}+{m3.group(1)}"))
    return xref


def load_csv():
    rows = []
    with open(CSV) as f:
        for r in csv.DictReader(f):
            rows.append((int(r["start"], 16), int(r["end"], 16), r["name"]))
    return rows


def extra_starts():
    try:
        txt = open(TOML).read()
    except OSError:
        return set()
    m = re.search(r"extra_function_starts\s*=\s*\[(.*?)\]", txt, re.S)
    return {int(x, 16) for x in re.findall(r'"(0x[0-9A-Fa-f]+)"', m.group(1))} if m else set()


def owners(a):
    return [(s, e, n) for s, e, n in load_csv() if s <= a < e]


def cmd_at(args):
    a = parse_addr(args[0])
    before = int(args[1]) if len(args) > 1 else 8
    after = int(args[2]) if len(args) > 2 else 8
    ins = build_index()["ins"]
    if a not in ins:
        print(f"{a:#x}: not in generated code (not recompiled, data, or outside .text)")
        return
    starts = {s for s, _, _ in load_csv()} | extra_starts()
    for b in range(a - 4 * before, a + 4 * after + 4, 4):
        if b not in ins:
            continue
        word, text, ds = ins[b]
        mark = ">>" if b == a else "  "
        tag = "  [delay slot]" if ds else ""
        head = f"--- function start {b:#x} ---\n" if b in starts else ""
        print(f"{head}{mark} {b:#08x}: {word:08x}  {text}{tag}")


def cmd_func(args):
    a = parse_addr(args[0])
    rows = owners(a)
    ex = extra_starts()
    is_start = any(s == a for s, _, _ in load_csv())
    if not rows:
        print(f"{a:#x}: no owning function in the function map")
    for s, e, n in rows:
        print(f"{a:#x} is in {n} [{s:#x}, {e:#x}) size {e - s:#x}, offset +{a - s:#x}")
    if is_start:
        print(f"{a:#x} is a function START in the function map")
    elif a in ex:
        print(f"{a:#x} is an extra_function_starts entry (resume entry of its owner)")
    elif rows:
        print(f"{a:#x} is an interior address (not a start); an indirect call here needs extra_function_starts")


def elf_data_refs(a):
    try:
        b = open(ELF, "rb").read()
    except OSError:
        return []
    shoff, = struct.unpack_from("<I", b, 0x20)
    shentsize, shnum, shstrndx = struct.unpack_from("<HHH", b, 0x2E)
    secs = [struct.unpack_from("<IIIIIIIIII", b, shoff + i * shentsize) for i in range(shnum)]
    strtab = secs[shstrndx]
    name = lambda off: b[strtab[4] + off: b.index(b"\0", strtab[4] + off)].decode()
    hits = []
    want = struct.pack("<I", a)
    for sh in secs:
        sname, stype, flags, addr, off, size = sh[:6]
        if stype == 8 or not (flags & 2) or (flags & 4):  # NOBITS, not ALLOC, EXEC
            continue
        data = b[off: off + size]
        i = data.find(want)
        while i != -1:
            if i % 4 == 0:
                hits.append((addr + i, name(sname)))
            i = data.find(want, i + 1)
    return hits


def cmd_xref(args):
    a = parse_addr(args[0])
    rng = int(args[args.index("--range") + 1], 0) if "--range" in args else 1
    data = build_index()
    found = False
    for t in range(a, a + rng):
        for site, kind in sorted(data["xref"].get(t, [])):
            own = owners(site)
            on = own[0][2] if own else "?"
            print(f"code  {site:#08x} ({on})  {kind}  -> {t:#x}")
            found = True
    for addr, sec in elf_data_refs(a):
        print(f"data  {addr:#08x} ({sec})  word == {a:#x}  (pointer table / vtable slot)")
        found = True
    pat = f"target=0x{a:x} "
    logs = glob.glob(RUNLOGS)
    if logs:
        out = subprocess.run(["grep", "-h", "-o", "missing-target.*source=0x[0-9a-f]* target=0x[0-9a-f]*"] + logs,
                             capture_output=True, text=True).stdout
        srcs = {}
        for line in out.splitlines():
            if line.endswith(f"target=0x{a:x}"):
                m = re.search(r"source=(0x[0-9a-f]+)", line)
                srcs[m.group(1)] = srcs.get(m.group(1), 0) + 1
        for s, n in sorted(srcs.items()):
            print(f"jalr  {s} -> {a:#x}  observed {n}x as a SKIPPED missing-target in boot logs")
            found = True
    if not found:
        print(f"{a:#x}: no static code refs, no data words, no logged indirect calls "
              "(indirect calls that succeed are not logged)")


def syscall_table():
    table, pending = {}, []
    for line in open(DISPATCHER):
        m = re.match(r"\s*case\s+(?:static_cast<uint32_t>\()?(-?0x[0-9A-Fa-f]+|-?\d+)\)?:", line)
        if m:
            pending.append(int(m.group(1), 0))
            continue
        m = re.match(r"\s*(\w+)\(rdram,", line)
        if m and pending:
            for n in pending:
                table[n] = m.group(1)
            pending = []
        elif pending and re.match(r"\s*(return|break)", line):
            pending = []
    return table


def curated():
    out = {}
    if os.path.exists(LABELS):
        for line in open(LABELS):
            if line.strip() and not line.startswith("#"):
                parts = line.rstrip("\n").split("\t")
                out.setdefault(int(parts[0], 16), []).append((parts[1], parts[2] if len(parts) > 2 else ""))
    try:
        for m in re.finditer(r'"([A-Za-z_]\w*)@(0x[0-9A-Fa-f]+)"', open(TOML).read()):
            out.setdefault(int(m.group(2), 16), []).append((m.group(1), "ssx3.toml stub list"))
    except OSError:
        pass
    try:
        for line in open(HANDOFF):
            if line.startswith("|"):
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if len(cells) >= 2:
                    names = re.split(r"<br>", cells[0])
                    addrs = re.split(r"<br>", cells[1])
                    for n, ad in zip(names, addrs):
                        if re.fullmatch(r"0x[0-9A-Fa-f]{8}", ad.strip()) and re.fullmatch(r"[A-Za-z_][\w]*", n.strip()):
                            out.setdefault(int(ad, 16), []).append((n.strip(), "120 Hz handoff (published symbol)"))
    except OSError:
        pass
    return out


def cmd_label(args):
    if args[0] == "syscall":
        n = int(args[1], 0)
        name = syscall_table().get(n) or syscall_table().get(n & 0xFFFFFFFF)
        print(f"syscall {n:#x}: {name} (Dispatcher.cpp)" if name else f"syscall {n:#x}: unknown (no case in Dispatcher.cpp)")
        return
    a = parse_addr(args[0])
    labels = curated().get(a, [])
    for n, src in labels:
        print(f"{a:#x}: {n}  [{src}]")
    ins = build_index()["ins"]
    for b in range(a, a + 16, 4):  # syscall wrapper: addiu $v1,$zero,N ... syscall
        t = ins.get(b, (0, "", False))[1]
        m = re.match(r"addiu \$v1, \$zero, " + IMM, t)
        if m:
            for c in range(b + 4, b + 16, 4):
                if ins.get(c, (0, "", False))[1].startswith("syscall"):
                    n = int(m.group(1), 0)
                    name = syscall_table().get(n) or syscall_table().get(n & 0xFFFFFFFF)
                    print(f"{a:#x}: syscall wrapper, $v1={n:#x} -> {name or 'unknown'}  [Dispatcher.cpp]")
                    labels = True
                    break
    if not labels:
        print(f"{a:#x}: unknown (no verified label; describe it by address, do not name it)")


if __name__ == "__main__":
    cmds = {"at": cmd_at, "func": cmd_func, "xref": cmd_xref, "label": cmd_label}
    if len(sys.argv) < 3 or sys.argv[1] not in cmds:
        sys.exit(__doc__)
    cmds[sys.argv[1]](sys.argv[2:])
