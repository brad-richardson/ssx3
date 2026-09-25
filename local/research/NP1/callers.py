#!/usr/bin/env python3
"""NP1: callers of target symbols from a simpleperf `-g callee` forest.

The forest holds one section per symbol; only the section headed by the
target is read (whole-file attribution would multi-count shared stacks).
First-level children of `-- TARGET` are direct callers: `|--X%--` / `--X%--`
edges take X% of the section root's Children%, bare chain links take 100%.
Attributed < root Children% => the rest had no fp frame above the leaf.

Usage: callers.py <p1-callee-full.txt> <regex> [<regex> ...]
"""
import re
import sys

ROOT = re.compile(r'^\s*([\d.]+)%\s+([\d.]+)%\s+(\S.*\S|\S)\s*$')
PCT = re.compile(r'^(.*)\|--([\d.]+)%-- (.*\S)\s*$')
DASHPCT = re.compile(r'^(.*)--([\d.]+)%-- (.*\S)\s*$')
PLAIN = re.compile(r'^(.*)-- ([^|].*\S)\s*$')


def sections(path):
    """Yield (children, self, symbol, lines) per section."""
    cur = None
    for line in open(path, errors='replace'):
        m = ROOT.match(line)
        if m and '--' not in line and '|' not in line.split('%')[-1]:
            if cur:
                yield cur
            cur = [float(m.group(1)), float(m.group(2)), m.group(3), []]
        elif cur is not None:
            cur[3].append(line)
    if cur:
        yield cur


def children(lines):
    """Parse one section body; return (target_child_indent, [(sym, edge, kids)]).

    Only the top two levels are needed: `-- TARGET`, then its callers.
    """
    top = []
    stack = []  # (indent, node)
    for line in lines:
        if '--' not in line:
            continue  # bare chain link (100% of parent) or '|' filler; skip
        m = PCT.match(line) or DASHPCT.match(line)
        if m:
            indent, edge, sym = len(m.group(1)), float(m.group(2)), m.group(3)
        else:
            m2 = PLAIN.match(line)
            if not m2 or line.lstrip()[0].isdigit():
                continue
            indent, edge, sym = len(m2.group(1)), None, m2.group(2)
        while stack and stack[-1][0] >= indent:
            stack.pop()
        node = [sym, edge, []]
        if stack:
            stack[-1][1][2].append(node)
        else:
            top.append(node)
        stack.append((indent, node))
    return top


def main():
    path, patterns = sys.argv[1], sys.argv[2:]
    for p in patterns:
        rx = re.compile(p)
        print(f'=== {p} ===')
        for kids_total, self_total, sym, lines in sections(path):
            if not rx.search(sym):
                continue
            top = children(lines)
            # The `-- TARGET` node mirrors the section root; its children are callers.
            callers = []
            for node in top:
                if node[2]:
                    callers = node[2]
                    break
            else:
                callers = top  # no mirror node; top level is the caller list
            attr = 0.0
            rows = []
            for csym, edge, _ in callers:
                a = (edge / 100.0 * kids_total) if edge is not None else kids_total
                attr += a
                rows.append((a, csym))
            rows.sort(reverse=True)
            print(f'section root: children={kids_total:.2f}% self={self_total:.2f}% '
                  f'attributed={attr:.2f}% truncated={kids_total - attr:.2f}%')
            for a, csym in rows[:14]:
                print(f'  {a:6.2f}%  {csym[:160]}')
        print()


main()
