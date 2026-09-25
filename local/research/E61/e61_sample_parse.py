#!/usr/bin/env python3
"""E61: per-thread self-time from macOS `sample` call-graph trees.

Usage: e61_sample_parse.py sample-s1.txt [sample-s2.txt ...]

Parses each Thread_* call tree (`+`-prefixed frame lines), computes
self = count - sum(direct children counts) per frame, and prints per
thread: total samples, top self symbols with their caller chain, and
auto stage groups. Unmatched top symbols are flagged for hand mapping.

Depth rule: after the leading `+`, each tree level occupies 2 chars
(spaces or `! `/`: `/`| ` markers) before the sample count.
"""
import re
import sys
from collections import Counter

THREAD_RE = re.compile(r'^\s*(\d+)\s+(Thread_\S+):?\s*(.*)$')
FRAME_RE = re.compile(r'^\s*\+(.*?)(\d+)\s+(.*?)\s+\(in\s+([^)]+)\)')

# (stage, [substring keywords]); matched against "leaf <- caller" text.
# Order matters (first match wins): specific stages before EE helpers.
STAGES = [
    ('guest code', ['sub_0x', 'ps2_recompiled']),
    ('syscalls/RPC/CD', ['handleSyscall', 'dispatchNumericSyscall', 'Syscall',
                         'SifRpc', 'sif_rpc', 'CdRead', 'cdrom', 'Cdvd']),
    ('VU1', ['VU1', 'Vu1', 'vif1', 'Vif1']),
    ('GIF/GS CPU backend', ['GSCpuBackend', 'GSMem::', 'GS::', 'GSFrame',
                            'vertexKick', 'writeRegister']),
    ('VIF/DMA', ['processVIF', 'GifArbiter', 'processGIFPacket', 'GifPath',
                 'VIF', 'Vif', 'Dma', 'DMA']),
    ('present/host render', ['EndDrawing', 'BeginDrawing', 'swapBuffers',
                             'CGLFlush', 'glSwap', 'gldPresent', 'GLDContext',
                             'MTLCommand', 'IOGPU', 'raylib', 'rlVertex',
                             'glfw', 'GLFW', 'SwapBuffers', 'NSOpenGL',
                             'AGXMetal', 'submitCommandBuffer']),
    ('audio', ['HALC_', 'ma_', 'miniaudio', 'AudioUnit', 'IOWorkLoop',
               'audioCallback', 'OnSendAudioData']),
    ('EE runtime helpers', ['PS2Runtime::', 'EeScheduler::', 'PS2Memory::',
                            'R5900Context', 'ps2Diag', 'dispatchGuestBranch']),
    ('waits/sleep/locks', ['__semwait_signal', 'semaphore_wait', 'nanosleep',
                           'usleep', '__psynch', '_pthread_mutex',
                           '__workq_kernreturn', 'start_wqthread', 'kevent',
                           '__ulock', 'mach_msg', 'cerror', 'futex', 'poll',
                           'select', '_pthread_cond', 'cond_wait']),
]


def stage_of(chain):
    hay = ' <- '.join(chain)
    for stage, keys in STAGES:
        if any(k in hay for k in keys):
            return stage
    return 'other'


def parse_tree(path):
    """Return {thread_name: {'total': n, 'self': Counter{(sym,lib,caller): n}}}."""
    threads, order = {}, []
    cur = None
    stack = []  # (depth, count, sym, lib, kids_sum, chain)
    for line in open(path, errors='replace'):
        if line.startswith('Binary Images:'):
            break
        m = THREAD_RE.match(line)
        if m and 'Thread_' in line and '(in ' not in line:
            while stack:  # flush previous thread's remaining root path
                d, c, s, lb, kids, ch = stack.pop()
                if stack:
                    stack[-1][4] += c
                self_n = c - kids
                if self_n > 0 and cur is not None:
                    threads[cur]['self'][(s, lb, ch[0])] += self_n
            name = (m.group(2) + ' ' + m.group(3)).strip()
            cur = name
            order.append(name)
            threads[cur] = {'total': int(m.group(1)), 'self': Counter()}
            stack = []
            continue
        m = FRAME_RE.match(line)
        if m is None or cur is None:
            continue
        prefix, count, sym = m.group(1), int(m.group(2)), m.group(3).strip()
        lib = m.group(4).strip()
        depth = (len(prefix) + 1) // 2
        while stack and stack[-1][0] >= depth:
            d, c, s, lb, kids, ch = stack.pop()
            if stack:
                stack[-1][4] += c
            self_n = c - kids
            if self_n > 0:
                threads[cur]['self'][(s, lb, ch[0])] += self_n
        caller = stack[-1][2] if stack else ''
        chain = [s for _, _, s, _, _, _ in stack] + [sym]
        stack.append([depth, count, sym, lib, 0, (caller, chain)])
    if cur is not None:
        while stack:
            d, c, s, lb, kids, ch = stack.pop()
            if stack:
                stack[-1][4] += c
            self_n = c - kids
            if self_n > 0:
                threads[cur]['self'][(s, lb, ch[0])] += self_n
    return threads, order


def main(paths):
    for path in paths:
        threads, order = parse_tree(path)
        print('=== %s ===' % path)
        for name in order:
            t = threads[name]
            total = t['total']
            if total == 0:
                continue
            print('--- %s: %d samples ---' % (name, total))
            for (sym, lib, caller), n in t['self'].most_common(15):
                print('%6d %6.2f%% [%s] %s (in %s) <- %s'
                      % (n, 100.0 * n / total,
                         stage_of([sym, caller]), sym[:100], lib, caller[:70]))
            groups = Counter()
            for (sym, lib, caller), n in t['self'].items():
                groups[stage_of([sym, caller])] += n
            accounted = sum(groups.values())
            print('    self-groups: ' + ', '.join(
                '%s %.1f%%' % (g, 100.0 * n / total)
                for g, n in groups.most_common()))
            print('    self-accounted: %.1f%% of thread samples'
                  % (100.0 * accounted / total))
        print()


if __name__ == '__main__':
    main(sys.argv[1:])
