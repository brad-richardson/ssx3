# GF1: (1) MTVU off-cpu split of the GS-handoff subtree; (2) GsWorker on-cpu split: GS frontend decode vs paraLLEl vs driver.
import sys, collections
sys.path.insert(0, '/home/brad/n2/toolchain/android-sdk/ndk/28.2.13676358/simpleperf')
from simpleperf_report_lib import ReportLib
FR = 405.0
def run(mode, tidset, classify):
    lib = ReportLib(); lib.SetSymfs('/home/brad/gf1/symdir'); lib.SetRecordFile('/home/brad/gf1/perf-R2b.data')
    lib.SetTraceOffCpuMode(mode)
    c = collections.Counter(); tot = collections.Counter()
    while True:
        s = lib.GetNextSample()
        if s is None: break
        if s.tid not in tidset: continue
        sym = lib.GetSymbolOfCurrentSample(); cc = lib.GetCallChainOfCurrentSample()
        names = [sym.symbol_name] + [cc.entries[i].symbol.symbol_name for i in range(cc.nr)]
        dsos = [sym.dso_name] + [cc.entries[i].symbol.dso_name for i in range(cc.nr)]
        tot[s.tid] += s.period
        c[(s.tid, classify(names, dsos))] += s.period
    lib.Close()
    return tot, c
def mtvu_off(names, dsos):
    j = ' | '.join(names)
    if 'GsWorker::enqueue' in j:
        return 'GS enqueue: ' + ('m_hasSpace wait (queue full)' if 'condition_variable::wait' in j or 'pthread_cond_wait' in j else ('mutex contended' if 'mutex::lock' in j or 'MutexLock' in j else 'other'))
    if 'GsWorker::endBatch' in j or 'GsWorker::beginBatch' in j or 'submitGifPacket' in j or 'GifArbiter' in j:
        return 'GS path other: ' + ('mutex contended' if 'mutex::lock' in j or 'MutexLock' in j else 'other')
    if 'Worker::loop' in j and ('condition_variable::wait' in j or 'pthread_cond_wait' in j) and 'processPendingTransfers' not in j:
        return 'starved (Worker::loop cvWork wait)'
    return 'other: ' + next((n for n in names if 'kernel' not in n and 'futex' not in n and 'syscall' not in n), '?')[:80]
def gsw_on(names, dsos):
    j = ' | '.join(names)
    leafdso = dsos[0].split('/')[-1]
    if 'GS::executeQueuedCommand' not in j:
        return 'outside executeQueuedCommand: ' + leafdso
    if 'ParallelGS' in j or 'parallel_gs' in j or 'GSInterface' in j or 'ParallelGs' in j or 'PS2GsParallel' in j or 'GSParallel' in j or 'Vulkan::' in j:
        if 'vulkan' in leafdso.lower() or 'adreno' in leafdso.lower() or 'kgsl' in leafdso.lower() or 'turnip' in leafdso.lower() or leafdso.startswith('libvulkan'):
            return 'paraLLEl -> driver dso ' + leafdso
        if 'kallsyms' in dsos[0]: return 'paraLLEl -> kernel'
        return 'paraLLEl backend (our .so)'
    if 'kallsyms' in dsos[0]: return 'frontend -> kernel'
    return 'GS frontend decode (no backend frame)'
tot, c = run('off-cpu', {30588}, mtvu_off)
print('## MTVU off-cpu (ms/frame), total', {k: round(v/1e6/FR, 2) for k, v in tot.items()})
for (t, k), v in sorted(c.items(), key=lambda x: -x[1])[:25]: print(f'{v/1e6/FR:7.3f}\t{k}')
tot, c = run('on-cpu', {30557}, gsw_on)
print('## GsWorker-30557 on-cpu (ms/frame), total', {k: round(v/1e6/FR, 2) for k, v in tot.items()})
for (t, k), v in sorted(c.items(), key=lambda x: -x[1])[:25]: print(f'{v/1e6/FR:7.3f}\t{k}')
