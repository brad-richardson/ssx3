#!/usr/bin/env python3
"""sbr-census: the signed-branch census over PS2 static-recomp generated code.

Usage:
  sbr-census.py <codegen_dir> [--json out.json]
  sbr-census.py --self-check

Counts, over the generated *.cpp files under <codegen_dir>:
  - total signed-branch sites ("signed sites"), per predicate kind (LT/GE/LE/GT)
  - number of files containing at least one site
  - for each site, the nearest preceding writer of the tested register inside
    the same function, classified into the review S6 categories
    (docs/research/review-2026-09-25-fable.md, row S6):
      set_gpr_s32   nearest writer is a SET_GPR_S32 line (sign-extending setter;
                    "safe by construction")
      u64_add       SET_GPR_U64 whose expression top-level op is + / -
                    (64-bit adds; mostly daddu moves of an argument/return)
      s64_add       SET_GPR_S64 (daddiu and the dsra/dsra32 shift family)
      set_gpr_u32   SET_GPR_U32
      set_gpr_vec   SET_GPR_VEC
      and_or_xor    SET_GPR_U64 whose expression top-level op is | & ^
                    (or/and/xor/ori/andi/xori; ldl/ldr merges land here too)
      slt           SET_GPR_U64 ternary compare (slt/sltu/slti/sltiu family)
      mf            SET_GPR_U64 reading ctx->hi / ctx->lo (MFHI/MFLO/MFHI1/...)
      ld            SET_GPR_U64 reading memory via READ64 (ld)
      u64_shift     SET_GPR_U64 whose expression top-level op is << / >>
                    (extra bucket; the review's one-off pass has no such row)
      other         any other SET_GPR_U64 writer shape
      live_in       no writer of the register anywhere in the function
      none_within_400  nearest writer exists but is more than 400 lines above
    Writer category is chosen from the writer line itself: the macro name
    (SET_GPR_S32/U32/U64/S64/VEC) and, for SET_GPR_U64, the top-level operator
    of its expression. Writer destination is the second argument of the macro.

Site shapes (confirmed against both generations):
  pre-SB1:  const bool branch_taken_0x… = (GPR_S32(ctx, N) {<,>=,<=,>} 0);
  SB1:      const bool branch_taken_0x… = (PS2X_SBR_{LT,GE,LE,GT}(ctx, runtime, N, 0x…));

--self-check runs the census over both known generations and asserts the
known answers (env SBR_CENSUS_OLD / SBR_CENSUS_NEW override the dirs):
  old (codegen-ssx3-pre-sb1): total exactly 4466; set_gpr_s32 3231 +/-2%;
                              u64_add 686 +/-2%  (review S6; category counts
                              allowed +/-2% because that pass was a one-off
                              regex, the total must be exact)
  new (codegen-ssx3):         total exactly 4466 (equals the old total);
                              623 files reference PS2X_SBR_LT (F2 Part 1)
On a mismatch it prints the actual numbers plus three example sites for the
offending category (to diff against the review's pass) and exits non-zero.

Stdlib only. Read-only over the input dir. One function per generated .cpp
file; the function body is the region from its
`(uint8_t* rdram, R5900Context* ctx, PS2Runtime *runtime) {` signature to the
first line that is exactly `}`.
"""
import json
import os
import re
import sys

HOME = os.path.expanduser("~")
OLD_CODEGEN = os.environ.get("SBR_CENSUS_OLD", f"{HOME}/dev/ssx3-work/codegen-ssx3-pre-sb1")
NEW_CODEGEN = os.environ.get("SBR_CENSUS_NEW", f"{HOME}/dev/ssx3-work/codegen-ssx3")

WINDOW = 400  # lines

# Site shapes (whole canonical line).
SITE_PRE_SB1 = re.compile(
    r"const bool branch_taken_0x[0-9A-Fa-f]+ = "
    r"\(GPR_S32\(ctx, (\d+)\) (<=|>=|<|>) 0\);")
SITE_SB1 = re.compile(
    r"const bool branch_taken_0x[0-9A-Fa-f]+ = "
    r"\(PS2X_SBR_(LT|GE|LE|GT)\(ctx, runtime, (\d+), 0x[0-9A-Fa-f]+\)\);")
OP_TO_PRED = {"<": "LT", ">=": "GE", "<=": "LE", ">": "GT"}

WRITER = re.compile(r"SET_GPR_(S32|U32|U64|S64|VEC)\(ctx, (\d+), (.*)\);?")
SIG = re.compile(r"\(uint8_t\* rdram, R5900Context\* ctx, PS2Runtime \*runtime\) \{")
SB1_LT = re.compile(r"PS2X_SBR_LT\(")

CATEGORIES = [
    "set_gpr_s32", "u64_add", "s64_add", "set_gpr_u32", "set_gpr_vec",
    "and_or_xor", "slt", "mf", "ld", "u64_shift", "other",
    "live_in", "none_within_400",
]


def top_ops(expr):
    """Top-level binary operators of a C expression (paren-depth aware)."""
    ops = set()
    depth = 0
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
        elif depth == 0:
            two = expr[i:i + 2]
            if two == "->":  # member arrow, not an operator
                i += 1
            elif two in ("<<", ">>", "<=", ">=", "==", "!="):
                ops.add(two)
                i += 1
            elif c in "+-|^&?:<>":
                ops.add(c)
        i += 1
    return ops


def classify_writer(macro, rhs):
    if macro == "S32":
        return "set_gpr_s32"
    if macro == "U32":
        return "set_gpr_u32"
    if macro == "VEC":
        return "set_gpr_vec"
    if macro == "S64":
        return "s64_add"
    ops = top_ops(rhs)
    if "?" in ops or ":" in ops:
        return "slt"
    if "+" in ops or "-" in ops:
        return "u64_add"
    if "|" in ops or "&" in ops or "^" in ops:
        return "and_or_xor"
    if rhs.startswith("READ64"):
        return "ld"
    if re.match(r"ctx->(hi|lo)", rhs):
        return "mf"
    if "<<" in ops or ">>" in ops:
        return "u64_shift"
    return "other"


def census_file(path):
    """Return (sites, writers, has_sb1_lt) for one generated .cpp file.

    sites:   list of (line_idx, predicate, reg, line_text)
    writers: dict reg -> list of (line_idx, category) sorted by line_idx
    """
    with open(path, errors="replace") as f:
        lines = f.read().splitlines()

    sig_idx = None
    for i, ln in enumerate(lines):
        if SIG.search(ln):
            sig_idx = i
            break
    if sig_idx is None:
        return [], {}, False

    end_idx = len(lines)
    for i in range(sig_idx + 1, len(lines)):
        if lines[i] == "}":
            end_idx = i
            break

    sites = []
    writers = {}
    has_lt = False
    for i in range(sig_idx + 1, end_idx):
        ln = lines[i]
        m = SITE_PRE_SB1.search(ln)
        if m:
            sites.append((i, OP_TO_PRED[m.group(2)], int(m.group(1)), ln))
            continue
        m = SITE_SB1.search(ln)
        if m:
            if m.group(1) == "LT":
                has_lt = True
            sites.append((i, m.group(1), int(m.group(2)), ln))
            continue
        if "PS2X_SBR_LT(" in ln:
            has_lt = True
            continue
        w = WRITER.search(ln)
        if w:
            writers.setdefault(int(w.group(2)), []).append(
                (i, classify_writer(w.group(1), w.group(3))))
    return sites, writers, has_lt


def nearest_writer_category(writers, reg, site_idx):
    lst = writers.get(reg)
    if not lst:
        return "live_in"
    # writers for one reg are collected in ascending line order; the first
    # hit scanning backwards is the nearest preceding writer
    for j in range(len(lst) - 1, -1, -1):
        widx, wcat = lst[j]
        if widx < site_idx:
            if site_idx - widx <= WINDOW:
                return wcat
            return "none_within_400"
    return "live_in"


def census_dir(codegen_dir):
    files = sorted(
        p for p in os.listdir(codegen_dir)
        if p.endswith(".cpp") and os.path.isfile(os.path.join(codegen_dir, p)))
    total = 0
    per_pred = {"LT": 0, "GE": 0, "LE": 0, "GT": 0}
    per_cat = {c: 0 for c in CATEGORIES}
    files_with_site = 0
    files_with_sb1_lt = 0
    examples = {c: [] for c in CATEGORIES}
    pre_sites = sb1_sites = 0
    for name in files:
        sites, writers, has_lt = census_file(os.path.join(codegen_dir, name))
        if has_lt:
            files_with_sb1_lt += 1
        if sites:
            files_with_site += 1
        for s in sites:
            total += 1
            per_pred[s[1]] += 1
            if "PS2X_SBR_" in s[3]:
                sb1_sites += 1
            else:
                pre_sites += 1
            cat = nearest_writer_category(writers, s[2], s[0])
            per_cat[cat] += 1
            if len(examples[cat]) < 3:
                examples[cat].append(
                    f"{name}:{s[0] + 1} reg={s[2]} {s[3].strip()}")
    gen = "sb1" if pre_sites == 0 else ("pre-sb1" if sb1_sites == 0 else "mixed")
    return {
        "dir": os.path.abspath(codegen_dir),
        "generation": gen,
        "files_scanned": len(files),
        "files_with_site": files_with_site,
        "files_with_sb1_lt": files_with_sb1_lt,
        "total_sites": total,
        "per_predicate": per_pred,
        "per_category": per_cat,
        "examples": examples,
    }


def print_report(r):
    print(f"sbr-census: {r['dir']}")
    print(f"  generation:            {r['generation']}")
    print(f"  files scanned:         {r['files_scanned']}")
    print(f"  files with >=1 site:   {r['files_with_site']}")
    if r["files_with_sb1_lt"]:
        print(f"  files w/ PS2X_SBR_LT:  {r['files_with_sb1_lt']}")
    print(f"  signed sites:          {r['total_sites']}")
    pp = r["per_predicate"]
    print(f"    LT={pp['LT']}  GE={pp['GE']}  LE={pp['LE']}  GT={pp['GT']}")
    print("  nearest writer of tested reg (same function):")
    for c in CATEGORIES:
        if r["per_category"][c]:
            print(f"    {c:18s} {r['per_category'][c]}")


def within_pct(actual, expected, pct=2.0):
    return abs(actual - expected) <= expected * pct / 100.0


def self_check():
    ok = True
    old = census_dir(OLD_CODEGEN)
    new = census_dir(NEW_CODEGEN)
    print_report(old)
    print()
    print_report(new)
    print()
    checks = [
        ("old total == 4466 (exact)", old["total_sites"] == 4466,
         old["total_sites"]),
        ("old set_gpr_s32 = 3231 +/-2%",
         within_pct(old["per_category"]["set_gpr_s32"], 3231),
         old["per_category"]["set_gpr_s32"]),
        ("old u64_add = 686 +/-2%",
         within_pct(old["per_category"]["u64_add"], 686),
         old["per_category"]["u64_add"]),
        ("new total == old total == 4466 (exact)",
         new["total_sites"] == old["total_sites"] == 4466,
         new["total_sites"]),
        ("new files referencing PS2X_SBR_LT == 623 (exact)",
         new["files_with_sb1_lt"] == 623,
         new["files_with_sb1_lt"]),
    ]
    for name, passed, actual in checks:
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}  (actual: {actual})")
        if not passed:
            ok = False
    if not ok:
        print("  self-check FAILED. Example sites per non-trivial category,")
        print("  for diffing against the review's one-off pass (S6):")
        for c in CATEGORIES:
            if old["examples"][c] and c in ("set_gpr_s32", "u64_add"):
                for ex in old["examples"][c]:
                    print(f"    {c}: {ex}")
    return 0 if ok else 1


def main(argv):
    args = [a for a in argv[1:]]
    if "--self-check" in args:
        args.remove("--self-check")
        self_check_invoked = True
    else:
        self_check_invoked = False
    if self_check_invoked:
        if args:
            print("sbr-census: --self-check takes no other arguments", file=sys.stderr)
            return 2
        return self_check()
    if len(args) in (0, 2) or len(args) > 3 or (len(args) == 3 and args[1] != "--json"):
        print("sbr-census: signed-branch census over generated code",
              file=sys.stderr)
        print("usage: sbr-census.py <codegen_dir> [--json out.json] | --self-check",
              file=sys.stderr)
        return 2
    codegen_dir = args[0]
    if not os.path.isdir(codegen_dir):
        print(f"sbr-census: not a directory: {codegen_dir}", file=sys.stderr)
        return 2
    r = census_dir(codegen_dir)
    print_report(r)
    if len(args) == 3:
        out = {k: v for k, v in r.items() if k != "examples"}
        with open(args[2], "w") as f:
            json.dump(out, f, indent=2)
            f.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
