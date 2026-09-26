import sys, collections
sys.path.insert(0, '/home/brad/n2/toolchain/android-sdk/ndk/28.2.13676358/simpleperf')
from simpleperf_report_lib import ReportLib
FR = 405.0
lib = ReportLib(); lib.SetSymfs('/home/brad/gf1/symdir'); lib.SetRecordFile('/home/brad/gf1/perf-R2b.data'); lib.SetTraceOffCpuMode('on-cpu')
incl = collections.Counter(); selfc = collections.Counter(); tot = 0
while True:
    s = lib.GetNextSample()
    if s is None: break
    if s.tid != 30557: continue
    sym = lib.GetSymbolOfCurrentSample(); cc = lib.GetCallChainOfCurrentSample()
    names = [sym.symbol_name] + [cc.entries[i].symbol.symbol_name for i in range(cc.nr)]
    tot += s.period
    selfc[names[0][:120]] += s.period
    for n in set(x[:120] for x in names): incl[n] += s.period
print('total', tot/1e6/FR)
print('## inclusive top 45')
for k, v in incl.most_common(45): print(f'{v/1e6/FR:7.3f}\t{k}')
print('## self top 30')
for k, v in selfc.most_common(30): print(f'{v/1e6/FR:7.3f}\t{k}')
