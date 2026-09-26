# GF1: on-cpu split of the MTVU unit thread's GS-handoff path (CP1 R2b profile).
import sys, collections
sys.path.insert(0, '/home/brad/n2/toolchain/android-sdk/ndk/28.2.13676358/simpleperf')
from simpleperf_report_lib import ReportLib
FRAMES = float(sys.argv[2]) if len(sys.argv) > 2 else 405.0
lib = ReportLib()
lib.SetSymfs('/home/brad/gf1/symdir')
lib.SetRecordFile(sys.argv[1])
print('modes', lib.GetSupportedTraceOffCpuModes())
lib.SetTraceOffCpuMode('on-cpu')
TIDS = {30588: 'MTVU', 30578: 'GameThread'}
KEYS = ['PS2Memory::submitGifPacket', 'PS2Memory::flushMaskedPath3Packets', 'GifArbiter::submit', 'GifArbiter::drain',
        'GS::noteGifPath', 'GS::processGIFPacket', 'GsWorker::enqueue', 'GsWorker::beginBatch', 'GsWorker::endBatch',
        'VU1Interpreter::progressXgkick', 'VU1Interpreter::finishXgkick', 'PS2Memory::processVIF1DataImpl',
        'VU1Interpreter::run', 'ps2_mtvu::detail::Worker::loop', 'processPendingTransfers', 'PS2Memory::processPendingTransfers',
        'condition_variable::notify_one', 'condition_variable::notify_all', 'mutex::lock', 'mutex::unlock', 'stable_sort', '__stable_sort',
        'GsWorker::pendingCount', 'GsWorker::isQuiescent', 'GS::drainQueue', 'ps2_mtvu::']
GS = ('PS2Memory::submitGifPacket', 'PS2Memory::flushMaskedPath3Packets', 'GifArbiter::', 'GS::', 'GsWorker::')
tot = collections.Counter(); incl = collections.Counter(); gsleaf = collections.Counter(); gsown = collections.Counter()
gstot = collections.Counter(); events = collections.Counter()
while True:
    s = lib.GetNextSample()
    if s is None: break
    ev = lib.GetEventOfCurrentSample().name
    events[ev] += 1
    t = TIDS.get(s.tid)
    if not t: continue
    p = s.period
    tot[t] += p
    sym = lib.GetSymbolOfCurrentSample()
    names = [sym.symbol_name]
    cc = lib.GetCallChainOfCurrentSample()
    for i in range(cc.nr):
        names.append(cc.entries[i].symbol.symbol_name)
    hit = set()
    for k in KEYS:
        if any(k in n for n in names): hit.add(k)
    for k in hit: incl[(t, k)] += p
    # GS-handoff subtree: first (outermost) GS frame decides membership
    gsidx = [i for i, n in enumerate(names) if any(g in n for g in GS)]
    if gsidx:
        gstot[t] += p
        leaf = names[0]
        if 'kallsyms' in sym.dso_name or leaf.startswith('[kernel'): leaf = '[kernel]'
        gsleaf[(t, leaf[:110])] += p
        inner = names[gsidx[0]]  # innermost GS-ish frame
        gsown[(t, inner[:110])] += p
ms = lambda v: v / 1e6 / FRAMES
print('events', dict(events))
for t in tot: print(f'#TOTAL {t} oncpu {tot[t]/1e9:.3f} s = {ms(tot[t]):.2f} ms/frame; GS-handoff subtree {ms(gstot[t]):.2f} ms/frame')
print('## inclusive on-cpu ms/frame')
for (t, k), v in sorted(incl.items(), key=lambda x: -x[1]): print(f'{t}\t{ms(v):7.3f}\t{k}')
print('## GS subtree by leaf symbol (top 40)')
for (t, k), v in sorted(gsleaf.items(), key=lambda x: -x[1])[:40]: print(f'{t}\t{ms(v):7.3f}\t{k}')
print('## GS subtree by innermost GS frame')
for (t, k), v in sorted(gsown.items(), key=lambda x: -x[1])[:30]: print(f'{t}\t{ms(v):7.3f}\t{k}')
