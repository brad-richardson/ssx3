#!/usr/bin/env python3
"""N12: bucket rollup of a simpleperf `--sort comm,symbol` self report into
the N11 stage list plus F5/VR1/VB1 shapes. First matching stage wins (order
matters). Usage: buckets.py <self-comm-sym.txt> [--appendix] [--comm NAME]
With --appendix, prints every symbol -> stage mapping after the table.
With --comm, only rows for that thread (shares stay % of ALL samples).
With --counts, input is a `report -n` file: shares come from the exact
Sample column (no display rounding), covering 100% of samples.
VU0 note: execUpper/execLower self rows cannot be attributed to a caller from
the self report alone; the VU0 stage here catches executeVU0Microprogram
itself, and the execUpper/execLower split comes from the children report.
"""
import re, sys

# (stage, [regexes]) — order = priority. N12 shapes first (brief §New symbol
# shapes); the old N11 VU1 rows are kept below as fallback (first match wins).
STAGES = [
    ('guest code', [r'\bsub_[0-9A-Fa-f]{8}']),
    ('VU1 generated pairs', [r'VU1RecompImage<']),
    ('VU1 issue/hazard', [r'VU1Interpreter::(issuePair|commitReadyPipelines|calculatePairReadyCycle|markPairWrites|recompChainReady)']),
    ('VU1 interpreter/other', [r'VU1Interpreter::', r'Vu1|VU1']),
    ('VU0', [r'executeVU0Microprogram']),
    ('__bzero/__memset zeroing', [r'__bzero|__memset']),
    ('VU1 hazard bookkeeping', [r'VU1Interpreter::(commitReadyPipelines|calculatePairReadyCycle|markPairWrites)']),
    ('VU1 execute', [r'VU1Interpreter::', r'Vu1|VU1']),
    ('VIF1/DMA', [r'VIF1|Vif1|processVIF|vif1|XGkick|Xgkick|DMA|DmaCh']),
    # Turnip is stripped (no defined FUNCs in dynsym); all driver CPU lands here.
    ('Vulkan driver CPU (Turnip)', [r'libvulkan_freedreno|libhardware\.so']),
    ('paraLLEl CPU submit', [r'ParallelGS::|Parallel|Granite|granite|EndDrawing|BeginDrawing']),
    ('GIF/GS packet handling', [r'GifArbiter|Gif::|GSPacket|GS::|GSMem::|GsWorker::threadMain|GsWorker::executeQueuedCommand|executeQueuedCommand']),
    ('EE runtime helpers', [r'PS2Memory::|TLB|tlb|Syscall|EeKernel|PS2Runtime::(Load|Store|Read|Write|dispatch|executeVU0)|Cop0|cop0']),
    ('SND/audio', [r'Snd|snd|Spu2|SPU2|Audio|audio|AAudio|aaudio']),
    ('scheduler/sync/waits', [r'EeScheduler|GsWorker::enqueue|Mutex|mutex|ConditionVariable|condition_variable|notify_one|pthread_cond|futex|Futex|sem_|pthread_|WaitTime|Wait|wait|Sleep|yield']),
    ('PLT', [r'@plt']),
    ('libc/kernel/vdso', [r'__aarch64_|__mem|clock_gettime|__kernel|\[kernel|scudo|malloc|free\b|memcpy|memset|vfprintf|sfvwrite|syscall|ioctl|libc\.so|libm\.so|\[vdso\]']),
    ('PS2 runtime other', [r'PS2Runtime::|ps2_|ps2x::|Ee[A-Z]|R5900|COP2|FPU']),
    # Profiler's own stack-unwinding cost (libunwind walks every sample).
    ('profiler unwind overhead', [r'libunwind|do_dl_iterate_phdr']),
]

comm_only = None
if '--comm' in sys.argv:
    comm_only = sys.argv[sys.argv.index('--comm') + 1]
use_counts = '--counts' in sys.argv
tot = {}
rows = 0
covered = 0.0
total_n = 0
mapping = []
for line in open(sys.argv[1]):
    if use_counts:
        m = re.match(r'\s*([\d.]+)%\s+(\d+)\s+(\S+)\s+(.*)', line)
        if not m:
            continue
        p, n, comm, sym = float(m.group(1)), int(m.group(2)), m.group(3), m.group(4)
    else:
        m = re.match(r'\s*([\d.]+)%\s+(\S+)\s+(.*)', line)
        if not m:
            continue
        p, comm, sym = float(m.group(1)), m.group(2), m.group(3)
        n = 0
    if comm_only and comm != comm_only:
        continue
    rows += 1
    total_n += n
    covered += p
    stage = 'other'
    for name, rxs in STAGES:
        if any(re.search(rx, sym) for rx in rxs):
            stage = name
            break
    tot[stage] = tot.get(stage, 0) + (n if use_counts else p)
    mapping.append((p, n, comm, sym, stage))

if use_counts:
    print(f'rows={rows} samples={total_n} (exact counts, 100% of samples)')
    print('| Stage | Samples | Share |')
    print('|---|---|---|')
    for k, v in sorted(tot.items(), key=lambda x: -x[1]):
        print(f'| {k} | {v} | {100.0 * v / total_n:.2f}% |')
else:
    print(f'rows={rows} covered={covered:.2f}%')
    print('| Stage | Self % |\n|---|---|')
    for k, v in sorted(tot.items(), key=lambda x: -x[1]):
        print(f'| {k} | {v:.2f}% |')
if '--appendix' in sys.argv:
    if use_counts:
        print('\n| Samples | Share | Thread | Symbol | Stage |')
        print('|---|---|---|---|---|')
        for p, n, comm, sym, stage in sorted(mapping, key=lambda r: -r[1]):
            print(f'| {n} | {100.0 * n / total_n:.3f}% | {comm} | `{sym}` | {stage} |')
    else:
        print('\n| Self % | Thread | Symbol | Stage |')
        print('|---|---|---|---|')
        for p, n, comm, sym, stage in sorted(mapping, reverse=True):
            print(f'| {p:.2f} | {comm} | `{sym}` | {stage} |')
