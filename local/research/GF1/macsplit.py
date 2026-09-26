# GF1: split a macOS `sample` call graph for one thread: on-cpu vs waiting, and the GS-handoff subtree.
import re, sys, collections
path, thread = sys.argv[1], sys.argv[2]
lines = open(path).read().split('\n')
start = next(i for i, l in enumerate(lines) if re.search(r'Thread_\d+: %s\s*$' % re.escape(thread), l) or re.search(r'Thread_\d+: %s\b' % re.escape(thread), l))
node_re = re.compile(r'^(\s*[+!:| ]*)(\d+) (.*?)  \(in ')
nodes = []  # (depth, count, sym)
for l in lines[start + 1:]:
    if re.match(r'^\s{4}\d+ Thread_', l) or not l.strip(): break
    m = node_re.match(l)
    if not m: continue
    nodes.append((len(m.group(1)), int(m.group(2)), m.group(3)))
total = int(re.search(r'(\d+) Thread_', lines[start]).group(1))
WAIT = ('__psynch_cvwait', '__psynch_mutexwait', '__ulock_wait', '__semwait_signal', 'mach_msg2_trap', 'mach_msg_trap', '__workq_kernreturn', 'semaphore_wait_trap')
GS = ('PS2Memory::submitGifPacket', 'PS2Memory::flushMaskedPath3Packets', 'GifArbiter::', 'GS::', 'GsWorker::')
# children lists
n = len(nodes)
children = [[] for _ in range(n)]; parent = [-1] * n; stack = []
for i, (d, c, s) in enumerate(nodes):
    while stack and nodes[stack[-1]][0] >= d: stack.pop()
    if stack: parent[i] = stack[-1]; children[stack[-1]].append(i)
    stack.append(i)
def selfc(i): return nodes[i][1] - sum(nodes[j][1] for j in children[i])
def anc(i):
    while i != -1: yield i; i = parent[i]
on = off = 0; gs_on = gs_off = 0; wake = 0
cat = collections.Counter()
for i in range(n):
    s = selfc(i)
    if s <= 0: continue
    syms = [nodes[j][2] for j in anc(i)]
    waiting = any(w in syms[0] for w in WAIT)
    ings = any(any(g in x for g in GS) for x in syms)
    if waiting: off += s
    else: on += s
    if ings:
        if waiting: gs_off += s
        else:
            gs_on += s
            j = ' | '.join(syms)
            if '__psynch_cvsignal' in j or 'notify_one' in j or 'notify_all' in j: k = 'wake (cv signal)'
            elif 'memmove' in j or 'memcpy' in j: k = 'memcpy'
            elif 'malloc' in j or 'free' in j or 'operator new' in j or 'operator delete' in j or 'nanov2' in j or 'szone' in j: k = 'allocator'
            elif 'mutex' in j or 'lock' in j.lower(): k = 'mutex/lock'
            else: k = 'other: ' + syms[0][:70]
            cat[k] += s
    elif waiting: cat['WAIT outside GS: ' + next((x for x in syms if 'wait' in x.lower() and 'psynch' not in x), syms[1] if len(syms) > 1 else '?')[:70]] += s
print(f'thread {thread}: total {total} samples; on-cpu {on}, waiting {off}; GS-subtree on-cpu {gs_on} ({100*gs_on/max(on,1):.1f}% of on-cpu), GS-subtree waiting {gs_off}')
for k, v in cat.most_common(30): print(f'{v:6d}\t{k}')
