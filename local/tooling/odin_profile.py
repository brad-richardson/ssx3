#!/usr/bin/env python3
"""odin_profile.py — one-command Odin per-thread profiler (PT1).

README
======
Every speed lane needs a per-thread breakdown on the Odin (running /
runnable / blocked by reason, top self symbols per thread, stage
buckets). CP1 did it by hand over ~2 h; this tool does it in one command.

Live run (needs the Odin lease; FS2 and AP1 have priority)::
    python3 local/tooling/odin_profile.py --apk <path> --apk-sha <sha> \\
        --label L [--env K=V ...] [--window 1900,2500] [--profile-secs 20] \\
        [--offcpu] [--symso <unstripped .so or bytesize:/path>]

1. Cool-down via local/tooling/odin_cooldown.py (--cooldown-mode screen
   by default: launch at status 0 + <42 C with no fixed wait; final for
   ledger numbers: status<=1 + fixed 180 s; every number is labeled with
   the mode), keyguard/battery/mc0-test checks, installs the APK (two
   local SHA reads + installed base.apk SHA), pushes the play-keys +
   I26-FAST + unpaced env, launches.
2. Runs I26-FAST unpaced to the window, records
   ``simpleperf record -g -e cpu-clock [--trace-offcpu]`` for the window
   plus the concurrent schedstat/cpufreq/gpubusy sampler, force-stops,
   pulls perf.data + PNGs, and restores Brad's play state with
   ``local/tooling/odin_restore_play.sh``.
3. Symbolizes on the mini (NDK host simpleperf; unstripped .so Build ID
   checked against the APK; pulled from bytesize over plain ``ssh cat``
   when given as ``bytesize:/path`` — reading a file is not a heavy job).
4. Writes ``local/research/<L>/profile/`` text reports. perf.data stays
   in scratch (``~/dev/ssx3-work/odinprof/<L>/``).

Offline re-analysis (no device):::
    python3 local/tooling/odin_profile.py --from-perf <perf.data> \\
        --symso <unstripped .so> --label L [--samples profile-samples.txt] \\
        [--logcat logcat.txt] [--meta meta.json] [--apk <apk>] [--libc <libc.so>]

Reports (all text, committed):
  per-thread.txt       CP1 Table 2 format: running/runnable/blocked ms/frame
                       with the blocked split by wait object.
  topsym.txt           top-25 self symbols per thread (on-cpu event counts).
  buckets.txt          N12-style stage buckets over on-cpu time, overall and
                       per key thread (VU1 blocks B*, SIMD FMAC, MTVU, GS
                       frontend, paraLLEl submit).
  buckets-appendix.txt every symbol -> stage mapping.
  gpu.txt              GPU busy/clock samples + per-frame busy estimate.
  counters.txt         [mtvu] / [gs:parallel] sync / [present-vk] lines.
  classes.txt          full sleep-class classifier output (CP1 format).
  meta.txt             inputs, SHAs, Build IDs, window derivation, commands.

Method (three clocks, one window — CP1 §Method):
  schedstat deltas give running/runnable/blocked per thread; cpu-clock
  event counts give on-cpu seconds + self symbols; sched_switch pairs
  give exact off-CPU spans, each weighted by its sleep-stack class.
  Blocked splits are pro-rata: class fractions x schedstat blocked, with
  the unpaired share stated. Cross-checks (schedstat vs cpu-clock vs
  switch pairs) are printed in per-thread.txt.
"""
import argparse
import bisect
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from collections import defaultdict

TOOL_DIR = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TOOL_DIR))  # local/tooling -> repo root
HOME = os.path.expanduser('~')
SCRATCH_ROOT = os.path.join(HOME, 'dev/ssx3-work/odinprof')
SIMPLEPERF_DEFAULT = ('/opt/homebrew/share/android-ndk/simpleperf/bin/'
                      'darwin/x86_64/simpleperf')

# ---------------------------------------------------------------------------
# Stage buckets (N12 buckets.py, updated per PT1: VU1 B* blocks, SIMD FMAC,
# MTVU, GS frontend, paraLLEl submit split out; allocator split from libc).
# First matching stage wins — order matters.
# ---------------------------------------------------------------------------
STAGES = [
    ('VU1 generated blocks B*', [r'VU1RecompImage<[^>]*>::B[0-9A-Fa-f]']),
    ('VU1 generated pairs', [r'VU1RecompImage<']),
    ('SIMD FMAC', [r'FMAC|fmac|fma_vf|vfmac|AdvSIMD|\bneon\b|\bNEON\b']),
    ('VU0', [r'executeVU0Microprogram']),
    ('MTVU runtime', [r'ps2_mtvu|MTVU|Worker::(loop|waitFor)|cvWork|m_hasSpace']),
    ('VIF1/DMA', [r'VIF1|Vif1|processVIF|vif1|XGkick|Xgkick|\bDMA\b|DmaCh']),
    ('GS frontend', [r'GS::|GifArbiter|Gif::|GSPacket|GSMem::|processGIFPacket'
                     r'|vertexKick|writeRegister|buildDrawBatch|noteGifPath'
                     r'|submitGifPacket']),
    ('paraLLEl submit', [r'ParallelGS::|Parallel|Granite|granite|EndDrawing'
                         r'|BeginDrawing|flush_pending|drawing_kick']),
    ('GsWorker queue', [r'GsWorker::(threadMain|enqueue|executeQueuedCommand)'
                        r'|executeQueuedCommand']),
    ('guest code', [r'\bsub_[0-9A-Fa-f]{8}']),
    ('VU1 issue/hazard', [r'VU1Interpreter::(issuePair|commitReadyPipelines'
                          r'|calculatePairReadyCycle|markPairWrites|recompChainReady)']),
    ('VU1 interpreter/other', [r'VU1Interpreter::|Vu1|VU1']),
    ('EE runtime helpers', [r'PS2Memory::|TLB|tlb|Syscall|EeKernel'
                            r'|PS2Runtime::(Load|Store|Read|Write|dispatch|executeVU0)'
                            r'|Cop0|cop0']),
    ('PS2 runtime other', [r'PS2Runtime::|ps2_|ps2x::|Ee[A-Z]|R5900|COP2|FPU']),
    ('Vulkan driver CPU (Turnip)', [r'libvulkan_freedreno|libhardware\.so']),
    ('SND/audio', [r'Snd|snd|Spu2|SPU2|Audio|audio|AAudio|aaudio']),
    ('scheduler/sync/waits', [r'EeScheduler|Mutex|mutex|ConditionVariable'
                              r'|condition_variable|notify_one|pthread_cond|futex|Futex'
                              r'|sem_|pthread_|WaitTime|Wait|wait|Sleep|yield']),
    ('allocator', [r'scudo|malloc|free\b|jemalloc']),
    ('profiler unwind overhead', [r'libunwind|do_dl_iterate_phdr']),
    ('PLT', [r'@plt']),
    ('libc/kernel/vdso', [r'__aarch64_|__mem|clock_gettime|__kernel|\[kernel'
                          r'|memcpy|memset|vfprintf|sfvwrite|syscall|ioctl'
                          r'|libc\.so|libm\.so|\[vdso\]']),
]
# On the GameThread, execUpper/execLower self time is the interpreted VU0
# path (CP1 Table 3); everywhere else it stays VU1 interpreter/other.
VU0_EXEC_RE = re.compile(r'VU1Interpreter::exec(Upper|Lower)\b')


def bucketize(sym, comm=''):
    if comm == 'GameThread' and VU0_EXEC_RE.search(sym):
        return 'VU0 (interpreted, via executeVU0Microprogram)'
    for name, rxs in STAGES:
        for rx in rxs:
            if re.search(rx, sym):
                return name
    return 'other'


# ---------------------------------------------------------------------------
# Input parsing
# ---------------------------------------------------------------------------
def parse_profile_samples(path):
    """Parse a CP1 profile-samples.txt into sampler groups."""
    groups = []
    cur = None
    for line in open(path, errors='replace'):
        m = re.match(r't=([\d.]+) tick=(\d+) (.*)', line)
        if m:
            cur = {'t': float(m.group(1)), 'tick': int(m.group(2)),
                   'rest': m.group(3), 'sched': {}}
            groups.append(cur)
            continue
        m = re.match(r'\s*sched (\d+) (.*)', line)
        if m and cur is not None:
            tid = int(m.group(1))
            tail = m.group(2)
            toks = tail.split()
            kv = {}
            comm_toks = []
            for tok in toks:
                if '=' in tok and tok.split('=')[0] in (
                        'cpu', 'ticks', 'run_ns', 'wait_ns', 'slices'):
                    k, v = tok.split('=', 1)
                    kv[k] = v
                elif not kv:
                    comm_toks.append(tok)
            try:
                cur['sched'][tid] = {'comm': ' '.join(comm_toks),
                                     'cpu': kv.get('cpu', '?'),
                                     'ticks': int(kv.get('ticks', 0)),
                                     'run': int(kv.get('run_ns', 0)),
                                     'wait': int(kv.get('wait_ns', 0)),
                                     'slices': int(kv.get('slices', 0))}
            except ValueError:
                continue
    return groups


def parse_therm(rest):
    """Parse a THERM group trailer into cpu6/cpu7 MHz, status, gpubusy, gpuclk."""
    out = {}
    m = re.search(r'cpu6=(\d+)', rest)
    if m:
        out['cpu6_mhz'] = int(m.group(1)) / 1000.0
    m = re.search(r'cpu7=(\d+)', rest)
    if m:
        out['cpu7_mhz'] = int(m.group(1)) / 1000.0
    m = re.search(r'status=(\d+)', rest)
    if m:
        out['status'] = int(m.group(1))
    m = re.search(r'busy=\s*(\d+)\s+(\d+)', rest)
    if m:
        b, t = int(m.group(1)), int(m.group(2))
        out['gpubusy'] = (b, t, 100.0 * b / t if t > 0 else -1.0)
    m = re.search(r'gpuclk=(\d+)', rest)
    if m:
        out['gpuclk_mhz'] = int(m.group(1)) / 1e6
    return out


def parse_logcat_ticks(logcat_path, t0):
    """Epoch-stamped [vsync-rate] lines -> [(wall_s, tick)]."""
    pts = [(0.0, 0)]
    with open(logcat_path, errors='replace') as f:
        for line in f:
            m = re.search(r'^\s*(\d+\.\d+).*\[vsync-rate\] tick=(\d+)', line)
            if m:
                pts.append((float(m.group(1)) - t0, int(m.group(2))))
    return pts


def tick_at(pts, wall):
    if wall <= pts[0][0]:
        return float(pts[0][1])
    for (w0, t0), (w1, t1) in zip(pts, pts[1:]):
        if w0 <= wall <= w1 and w1 > w0:
            return t0 + (w1 - wall and (wall - w0) * (t1 - t0) / (w1 - w0))
    return float(pts[-1][1])


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def build_id_of(path):
    """GNU Build ID of an ELF file via llvm-readelf."""
    for tool in (shutil.which('llvm-readelf'),
                 '/opt/homebrew/opt/llvm/bin/llvm-readelf'):
        if tool and os.path.exists(tool):
            r = subprocess.run([tool, '-n', path], capture_output=True,
                               text=True, timeout=120)
            m = re.search(r'Build ID:\s*([0-9a-fA-F]+)', r.stdout)
            if m:
                return m.group(1).lower()
            return ''
    raise SystemExit('llvm-readelf not found (need brew llvm)')


def apk_lib_build_id(apk_path):
    """Build ID of libps2EntryRunner.so inside the APK."""
    with tempfile.TemporaryDirectory(prefix='odinprof-apk') as tmp:
        with zipfile.ZipFile(apk_path) as z:
            names = [n for n in z.namelist()
                     if n.endswith('libps2EntryRunner.so')]
            if not names:
                raise SystemExit(f'no libps2EntryRunner.so in {apk_path}')
            lib = z.extract(names[0], tmp)
        return build_id_of(lib)


def resolve_symso(symso, scratch_sym_dir):
    """Local path, or bytesize:/wsl/path pulled over plain ssh cat."""
    os.makedirs(scratch_sym_dir, exist_ok=True)
    if symso.startswith('bytesize:'):
        remote = symso[len('bytesize:'):]
        dest = os.path.join(scratch_sym_dir, 'libps2EntryRunner.so')
        with open(dest, 'wb') as f:
            r = subprocess.run(['ssh', '-o', 'ConnectTimeout=20', 'bytesize',
                                'wsl', '-d', 'Ubuntu', '--', 'bash', '-lc',
                                f'"cat {remote}"'],
                               stdout=f, stderr=subprocess.PIPE, timeout=1800)
        if r.returncode != 0:
            raise SystemExit(f'bytesize cat failed: {r.stderr[:300]!r}')
        return dest
    if not os.path.isfile(symso):
        raise SystemExit(f'--symso not found: {symso}')
    return symso


# ---------------------------------------------------------------------------
# report-sample classifier (CP1 classify.py, promoted + subclassed)
# ---------------------------------------------------------------------------
def classify(syms):
    """(topclass, subclass, leaf-note) for one sleep stack's symbol set."""
    js = ' '.join(syms)
    if 'GsWorker::enqueue' in js:
        sub = ('GS-queue-full (m_hasSpace.wait)' if 'm_hasSpace' in js
               else 'GS-queue-full (GsWorker::enqueue)')
        return ('enqueue-backpressure', sub)
    if '__ioctl' in js:
        return ('ioctl-fence', 'kgsl fence (__ioctl sleep; kernel-only unwind)')
    if '__futex_wait_ex' in js:
        if 'Worker::loop' in js or 'cvWork' in js:
            return ('futex-cond', 'starved for jobs (Worker::loop -> cvWork.wait)')
        if 'vblank' in js or 'waitFor' in js:
            return ('futex-cond', 'vblank (ps2_mtvu::vblank -> Worker::waitFor)')
        if 'threadMain' in js:
            return ('futex-cond', 'queue-empty (threadMain -> cond)')
        return ('futex-cond', 'cond (other)')
    if 'epoll' in js or re.search(r'\bpoll\b', js):
        return ('poll', 'epoll/poll')
    for x in syms:
        if 'kernel.kallsyms' not in x and x not in ('syscall',):
            return ('other', x[:80])
    return ('other', 'kernel-only')


class PerfModel:
    """Streaming parse of `simpleperf report-sample --show-callchain`."""

    def __init__(self):
        self.switches = defaultdict(list)   # tid -> [(time, is_on)]
        self.offs = defaultdict(list)       # tid -> [(time, top, sub)]
        self.oncpu = defaultdict(lambda: defaultdict(int))
        self.names = {}                     # tid -> comm
        self.span = [None, None]

    def feed(self, stream):
        rectype, cur, chain, in_chain = None, {}, [], False

        def flush():
            nonlocal rectype, cur, chain, in_chain
            if rectype == 'context_switch' and 'thread_id' in cur:
                try:
                    tid = int(cur['thread_id'])
                    self.switches[tid].append(
                        (int(cur['time']), cur.get('switch_on') == 'true'))
                except (ValueError, KeyError):
                    pass
            elif rectype == 'sample' and 'thread_id' in cur:
                try:
                    tid = int(cur['thread_id'])
                    t = int(cur['time'])
                except (ValueError, KeyError):
                    pass
                else:
                    if 'thread_name' in cur:
                        self.names.setdefault(tid, cur['thread_name'])
                    if cur.get('event_type') == 'cpu-clock':
                        sym = cur.get('symbol', '?')
                        try:
                            self.oncpu[tid][sym] += int(
                                cur.get('event_count', 0))
                        except ValueError:
                            pass
                    else:  # sched_switch off-sample
                        # Ordered, deduped: innermost frame first, so the
                        # "other:" fallback (first non-kernel frame) is
                        # deterministic (a set would pick an arbitrary frame).
                        ordered = list(dict.fromkeys(
                            chain + ([cur['symbol']]
                                     if cur.get('symbol') else [])))
                        top, sub = classify(ordered)
                        self.offs[tid].append((t, top, sub))
                    s = self.span
                    if s[0] is None or t < s[0]:
                        s[0] = t
                    if s[1] is None or t > s[1]:
                        s[1] = t
            rectype, cur, chain, in_chain = None, {}, [], False

        for raw in stream:
            ln = raw.rstrip('\n')
            if not ln.strip():
                continue
            if not ln.startswith((' ', '\t')):
                flush()
                rectype = ln.rstrip(':')
                in_chain = False
                continue
            s = ln.strip()
            if s == 'callchain:':
                in_chain = True
                continue
            if in_chain:
                if s.startswith('symbol:'):
                    chain.append(s[7:].strip())
                continue
            if ':' in s:
                k, v = s.split(':', 1)
                cur[k.strip()] = v.strip()
        flush()

    def off_totals(self):
        """tid -> (switch pairs off_s, [(top, sub, s)], paired_s, unpaired)."""
        out = {}
        for tid in set(self.switches) | set(self.offs):
            evs = sorted(self.switches.get(tid, []))
            s0, s1 = self.span
            off, cur_off = 0, None
            for t, is_on in evs:
                t = max(s0, min(s1, t))
                if not is_on:
                    cur_off = t
                elif cur_off is not None:
                    off += t - cur_off
                    cur_off = None
            ons = sorted(t for t, is_on in evs if is_on)
            cls = defaultdict(int)
            unk = 0
            for t, top, sub in sorted(self.offs.get(tid, [])):
                j = bisect.bisect_right(ons, t)
                if j < len(ons):
                    dur = ons[j] - t
                    if dur < 0 or dur > 60e9:
                        unk += 1
                        continue
                    cls[(top, sub)] += dur
                else:
                    unk += 1
            paired = sum(cls.values())
            ranked = sorted(cls.items(), key=lambda kv: -kv[1])
            out[tid] = (off / 1e9, [(k[0], k[1], v / 1e9) for k, v in ranked],
                        paired / 1e9, unk)
        return out


def run_simpleperf_report_sample(simpleperf, perf_data, symdir):
    cmd = [simpleperf, 'report-sample', '-i', perf_data, '--show-callchain']
    if symdir:
        cmd += ['--symdir', symdir]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True, bufsize=1 << 20)
    model = PerfModel()
    model.feed(p.stdout)
    err = p.stderr.read()
    p.wait()
    if p.returncode != 0:
        raise SystemExit(f'report-sample failed: {err[:500]!r}')
    return model, err


def run_simpleperf_report(simpleperf, perf_data, symdir, sort):
    cmd = [simpleperf, 'report', '-i', perf_data, '--sort', sort]
    if symdir:
        cmd += ['--symdir', symdir]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    if r.returncode != 0:
        raise SystemExit(f'simpleperf report failed: {r.stderr[:300]!r}')
    return r.stdout


# ---------------------------------------------------------------------------
# Analysis -> reports
# ---------------------------------------------------------------------------
KEY_THREADS = ('MTVU', 'GameThread', 'GsWorker')


def analyze(perf_data, samples_path, logcat_path, meta_path, symdir_path,
            out_dir, simpleperf, extra_meta):
    os.makedirs(out_dir, exist_ok=True)
    meta_lines = list(extra_meta)

    groups = parse_profile_samples(samples_path)
    if len(groups) < 2:
        raise SystemExit(f'need >= 2 sampler groups in {samples_path}')
    g0, g1 = groups[0], groups[-1]
    wall = g1['t'] - g0['t']
    meta_lines.append(f'sampler edges: t+{g0["t"]:.1f} (poll tick {g0["tick"]})'
                      f' -> t+{g1["t"]:.1f} (poll tick {g1["tick"]}),'
                      f' {len(groups)} groups, wall {wall:.2f} s')
    if logcat_path and meta_path:
        t0 = json.load(open(meta_path))['T0']
        pts = parse_logcat_ticks(logcat_path, t0)
        k0, k1 = tick_at(pts, g0['t']), tick_at(pts, g1['t'])
        meta_lines.append(
            f'tick interp: {len(pts) - 1} [vsync-rate] lines;'
            f' edges tick {k0:.0f} -> {k1:.0f}')
    else:  # coarse driver-poll ticks only
        k0, k1 = float(g0['tick']), float(g1['tick'])
        meta_lines.append('tick interp: NO logcat/meta; coarse poll ticks')
    frames = max(1.0, k1 - k0)
    ms_per_frame = 1000.0 * wall / frames
    meta_lines.append(f'window: {frames:.1f} frames, {wall:.2f} s wall ='
                      f' {ms_per_frame:.2f} ms/frame,'
                      f' {frames / wall:.2f} vs/s')

    # --- schedstat three-way split + cpu/freq residency ---
    s0, s1 = g0['sched'], g1['sched']
    cpus_seen = defaultdict(set)
    for g in groups:
        for tid, row in g['sched'].items():
            cpus_seen[tid].add(row['cpu'])
    therms = [parse_therm(g['rest']) for g in groups]
    cpu6_mhz = [t['cpu6_mhz'] for t in therms if 'cpu6_mhz' in t]
    cpu7_mhz = [t['cpu7_mhz'] for t in therms if 'cpu7_mhz' in t]

    three = {}
    for tid, r1 in s1.items():
        if tid not in s0:
            continue
        r0 = s0[tid]
        run = (r1['run'] - r0['run']) / 1e6 / frames
        wait = (r1['wait'] - r0['wait']) / 1e6 / frames
        three[tid] = {'comm': r1['comm'], 'run': run, 'wait': wait,
                      'blocked': ms_per_frame - run - wait,
                      'slices': r1['slices'] - r0['slices'],
                      'cpus': sorted(cpus_seen.get(tid, set()),
                                     key=lambda c: (c == '?', c))}

    # --- simpleperf: classifier stream + tid map ---
    model, rep_err = run_simpleperf_report_sample(
        simpleperf, perf_data, symdir_path)
    s0ns, s1ns = model.span
    rec_span = (s1ns - s0ns) / 1e9
    rec_frames = rec_span * frames / wall
    meta_lines.append(f'record span: {rec_span:.3f} s = ~{rec_frames:.0f}'
                      f' frames at the window rate')
    if rep_err.strip():
        meta_lines.append(f'report-sample stderr: {rep_err.strip()[:200]}')
    try:
        tidmap_txt = run_simpleperf_report(
            simpleperf, perf_data, symdir_path, 'comm,tid')
    except SystemExit as e:
        tidmap_txt = f'(tid map failed: {e})'
    # Prefer simpleperf's comm names (unsampled threads keep schedstat comm).
    for tid, comm in model.names.items():
        if tid in three:
            three[tid]['comm'] = comm
    off = model.off_totals()
    oncpu_s = {tid: sum(d.values()) / 1e9 for tid, d in model.oncpu.items()}

    # Unresolved rows in our .so (offset-only, no symbol).
    unresolved = 0
    for tid, d in model.oncpu.items():
        for sym in d:
            if re.search(r'libps2EntryRunner\.so\[\+', sym):
                unresolved += 1
    meta_lines.append(f'unresolved rows in our .so: {unresolved}')

    # --- per-thread.txt (CP1 Table 2 format) ---
    def cpu_str(tid, row):
        cpus = row['cpus']
        n = len(groups)
        if len(cpus) == 1 and cpus[0] != '?':
            pin = f'cpu{cpus[0]} pinned ({n}/{n} samples)'
        else:
            pin = f'roams cpu {"/".join(cpus)}'
        if row['comm'] == 'MTVU' and cpu7_mhz:
            pin += (f'; cpu7 {min(cpu7_mhz):.0f}-{max(cpu7_mhz):.0f} MHz'
                    f' in-window (n={len(cpu7_mhz)})')
        elif row['comm'] == 'GameThread' and cpu6_mhz:
            pin += (f'; cpu6 {min(cpu6_mhz):.0f}-{max(cpu6_mhz):.0f} MHz'
                    f' in-window (n={len(cpu6_mhz)})')
        elif row['comm'] == 'GsWorker':
            pin += f'; {row["slices"]:,} slices/window'
        return pin

    def blocked_str(tid, row):
        if tid not in off:
            return f'{row["blocked"]:.1f} (no switch records in window)'
        off_s, ranked, paired_s, unk = off[tid]
        if paired_s <= 0 or row['blocked'] <= 0:
            return f'{row["blocked"]:.1f} (unsplit)'
        # Pro-rata: class fractions x schedstat blocked.
        shown = [(top, sub, s / paired_s * row['blocked'])
                 for top, sub, s in ranked[:3]]
        parts = [f'{ms:.1f} {sub} [{top}]' for top, sub, ms in shown
                 if ms >= 0.15]
        rest = row['blocked'] - sum(ms for _, _, ms in shown
                                    if ms >= 0.15)
        if rest >= 0.05 and (len(ranked) > len(parts)
                             or sum(1 for _, _, ms in shown if ms >= 0.15)
                             < len(shown)):
            parts.append(f'{rest:.1f} other')
        unsampled_pct = 100.0 * (1.0 - paired_s / off_s) if off_s > 0 else 0
        note = (f'; {unsampled_pct:.0f}% of switch-off unsampled (pro-rata)'
                if unsampled_pct >= 5 else '')
        return f'{row["blocked"]:.1f} = ' + ' + '.join(parts) + note

    key_tids = [tid for tid, r in three.items() if r['comm'] in KEY_THREADS]
    key_tids.sort(key=lambda t: -three[t]['run'])
    other_tids = [tid for tid in three if tid not in key_tids]
    other_tids.sort(key=lambda t: -three[t]['run'])

    with open(os.path.join(out_dir, 'per-thread.txt'), 'w') as f:
        f.write(f'window ticks {k0:.0f} -> {k1:.0f} ({frames:.1f} frames;'
                f' schedstat sample edges t+{g0["t"]:.1f} -> t+{g1["t"]:.1f},'
                f' {wall:.2f} s wall = {ms_per_frame:.2f} ms/frame;'
                f' simpleperf record span {rec_span:.3f} s'
                f' = ~{rec_frames:.0f} frames inside it)\n')
        f.write('run/wait from schedstat deltas; blocked = wall - run - wait;'
                ' blocked splits pro-rata (class fractions x schedstat'
                ' blocked).\n\n')
        f.write('| Thread (TID) | running | runnable | blocked'
                ' (wait object/reason) | core + freq residency |\n')
        f.write('| --- | ---: | ---: | --- | --- |\n')
        for tid in key_tids + other_tids[:7]:
            r = three[tid]
            f.write(f'| {r["comm"]} ({tid}) | {r["run"]:.1f} | {r["wait"]:.1f}'
                    f' | {blocked_str(tid, r)} | {cpu_str(tid, r)} |\n')
        f.write('\nCross-checks (per frame):\n')
        for tid in key_tids:
            r = three[tid]
            oc = oncpu_s.get(tid, 0.0) / rec_frames * 1000.0
            sw = off[tid][0] / rec_frames * 1000.0 if tid in off else -1
            f.write(f'{r["comm"]}: run {r["run"]:.1f} (schedstat) vs'
                    f' {oc:.1f} (cpu-clock); blocked {r["blocked"]:.1f} vs'
                    f' {sw:.1f} (switches)\n')

    # --- topsym.txt (top-25 self per thread) ---
    with open(os.path.join(out_dir, 'topsym.txt'), 'w') as f:
        f.write(f'on-cpu self from cpu-clock event counts / {rec_frames:.0f}'
                f' record frames\n\n')
        tids = sorted(model.oncpu, key=lambda t: -sum(model.oncpu[t].values()))
        for tid in tids:
            tot = sum(model.oncpu[tid].values()) / 1e9
            if tot < 0.05:
                continue
            comm = model.names.get(tid, three.get(tid, {}).get('comm', '?'))
            f.write(f'## {comm} ({tid}): oncpu {tot:.2f} s'
                    f' = {tot / rec_frames * 1000:.1f} ms/frame\n')
            f.write('| # | ms/frame | Symbol |\n| ---: | ---: | --- |\n')
            ranked = sorted(model.oncpu[tid].items(), key=lambda kv: -kv[1])
            for i, (sym, cnt) in enumerate(ranked[:25], 1):
                f.write(f'| {i} | {cnt / 1e9 / rec_frames * 1000:.2f} |'
                        f' `{sym[:150]}` |\n')
            f.write('\n')

    # --- buckets.txt (on-cpu stage rollup) ---
    all_syms = defaultdict(int)
    for tid, d in model.oncpu.items():
        for sym, cnt in d.items():
            all_syms[(model.names.get(tid, ''), sym)] += cnt
    total = sum(all_syms.values())

    def rollup(rows):
        tot = defaultdict(int)
        for comm, sym, cnt in rows:
            tot[bucketize(sym, comm)] += cnt
        return tot

    overall = rollup([(c, s, n) for (c, s), n in all_syms.items()])
    with open(os.path.join(out_dir, 'buckets.txt'), 'w') as f:
        f.write(f'on-cpu buckets: {total / 1e9:.1f} s total on-cpu'
                f' ({rec_span:.1f} s record). shares = % of ALL on-cpu.\n')
        f.write('execUpper/execLower count as VU0 on the GameThread only'
                ' (CP1 Table 3); elsewhere VU1 interpreter/other.\n\n')
        f.write('| Stage | On-cpu s | Share |\n|---|---|---|\n')
        for k, v in sorted(overall.items(), key=lambda x: -x[1]):
            f.write(f'| {k} | {v / 1e9:.2f} | {100.0 * v / total:.2f}% |\n')
        # Per key thread (shares stay % of ALL on-cpu, N12 convention).
        for comm in KEY_THREADS:
            tids = [t for t, nm in model.names.items() if nm == comm]
            if not tids:
                continue
            # The long-lived GsWorker first (transient Turnip workers roam).
            tids.sort(key=lambda t: -sum(model.oncpu[t].values()))
            for tid in tids[:1] if comm != 'GsWorker' else tids:
                rows = [(comm, s, n)
                        for s, n in model.oncpu[tid].items()]
                bt = rollup(rows)
                st = sum(bt.values())
                f.write(f'\n## {comm} ({tid}): {st / 1e9:.2f} s on-cpu\n')
                f.write('| Stage | On-cpu s | Share of ALL on-cpu |\n'
                        '|---|---|---|\n')
                for k, v in sorted(bt.items(), key=lambda x: -x[1]):
                    f.write(f'| {k} | {v / 1e9:.3f} |'
                            f' {100.0 * v / total:.2f}% |\n')
    with open(os.path.join(out_dir, 'buckets-appendix.txt'), 'w') as f:
        f.write('| On-cpu s | Share | Thread | Symbol | Stage |\n'
                '|---|---|---|---|\n')
        for (comm, sym), cnt in sorted(all_syms.items(),
                                       key=lambda kv: -kv[1]):
            f.write(f'| {cnt / 1e9:.4f} | {100.0 * cnt / total:.3f}% |'
                    f' {comm} | `{sym[:160]}` |'
                    f' {bucketize(sym, comm)} |\n')

    # --- classes.txt (CP1 format + subclasses) ---
    with open(os.path.join(out_dir, 'classes.txt'), 'w') as f:
        f.write(f'record span ns: {s0ns} .. {s1ns} = {rec_span:.3f}s'
                f' (~{rec_frames:.0f} frames)\n')
        f.write('\n=== per-thread on/off from switch pairs (ns) ===\n')
        for tid in sorted(off):
            n = len(model.switches.get(tid, []))
            f.write(f'tid={tid} ({model.names.get(tid, "?")}) switches={n}'
                    f' off_s={off[tid][0]:.3f}\n')
        f.write('\n=== sleep classes (time-weighted) ===\n')
        for tid in sorted(off):
            off_s, ranked, paired_s, unk = off[tid]
            n = len(model.offs.get(tid, []))
            f.write(f'tid={tid} ({model.names.get(tid, "?")})'
                    f' offsamples={n} paired_s={paired_s:.3f} unpaired={unk}\n')
            for top, sub, s in ranked[:8]:
                f.write(f'    {s:8.3f}s [{top}] {sub}\n')
        f.write('\n=== on-cpu top symbols by tid (event_count s) ===\n')
        for tid in sorted(model.oncpu,
                          key=lambda t: -sum(model.oncpu[t].values())):
            tot = sum(model.oncpu[tid].values()) / 1e9
            f.write(f'tid={tid} ({model.names.get(tid, "?")})'
                    f' oncpu_s={tot:.3f}\n')
            for s, v in sorted(model.oncpu[tid].items(),
                               key=lambda kv: -kv[1])[:6]:
                f.write(f'    {v / 1e9:8.3f}s {s[:110]}\n')
        f.write('\n=== tid map (simpleperf report --sort comm,tid) ===\n')
        f.write(tidmap_txt)

    # --- gpu.txt ---
    with open(os.path.join(out_dir, 'gpu.txt'), 'w') as f:
        pcts = [t['gpubusy'][2] for t in therms if 'gpubusy' in t]
        clks = [t['gpuclk_mhz'] for t in therms if 'gpuclk_mhz' in t]
        f.write('in-window sampler THERM lines:\n')
        for g, t in zip(groups, therms):
            b = t.get('gpubusy')
            f.write(f't=+{g["t"]:.1f} tick~{g["tick"]}'
                    f' cpu6={t.get("cpu6_mhz", "?")}MHz'
                    f' cpu7={t.get("cpu7_mhz", "?")}MHz'
                    f' status={t.get("status", "?")}'
                    f' gpubusy={b[2]:.1f}% gpuclk={t.get("gpuclk_mhz", "?")}MHz\n'
                    if b else f't=+{g["t"]:.1f} tick~{g["tick"]} (no gpu)\n')
        if pcts:
            mean = sum(pcts) / len(pcts)
            f.write(f'\nkgsl busy % (n={len(pcts)}):'
                    f' {" ".join(f"{p:.1f}" for p in pcts)}'
                    f' (mean {mean:.1f})\n')
            f.write(f'gpuclk: {" ".join(f"{c:.0f}" for c in clks)} MHz\n')
            f.write(f'busy x wall/frame (crude): {mean:.1f}% x'
                    f' {ms_per_frame:.2f} = {mean / 100 * ms_per_frame:.1f}'
                    f' ms/frame\n')

    # --- counters.txt ---
    with open(os.path.join(out_dir, 'counters.txt'), 'w') as f:
        if not logcat_path:
            f.write('no logcat provided\n')
        else:
            txt = open(logcat_path, errors='replace').read()
            f.write(f'last-in-window (tick <= {k1:.0f}) counter lines:\n\n')
            for key in ('[mtvu]', '[gs:parallel] sync', '[gs:parallel] periodic',
                        '[present-vk]'):
                lines = [l for l in txt.splitlines() if key in l]
                f.write(f'--- {key} (n={len(lines)}) ---\n')
                # Prefer the last line at/below the window end tick.
                pick = ''
                for l in lines:
                    m = re.search(r'tick=(\d+)', l)
                    if m and int(m.group(1)) <= k1:
                        pick = l
                if not pick and lines:
                    pick = lines[-1]
                f.write((pick.strip() + '\n' if pick else '(none)\n') + '\n')

    with open(os.path.join(out_dir, 'meta.txt'), 'w') as f:
        f.write('\n'.join(meta_lines) + '\n')
    return {'frames': frames, 'wall': wall, 'ms_per_frame': ms_per_frame,
            'rec_span': rec_span, 'rec_frames': rec_frames,
            'k0': k0, 'k1': k1}


def stage_symdir(symso_path, libc_path, scratch_sym_dir):
    """Build a simpleperf --symdir: our .so + device libc if given."""
    os.makedirs(scratch_sym_dir, exist_ok=True)
    for src in [p for p in (symso_path, libc_path) if p]:
        dst = os.path.join(scratch_sym_dir, os.path.basename(src))
        if os.path.abspath(src) == os.path.abspath(dst) or os.path.exists(dst):
            continue
        try:  # same disk: hardlink the 1.3 GB .so instead of copying it
            os.link(src, dst)
        except OSError:
            shutil.copy2(src, dst)
    return scratch_sym_dir


def run_offline(a, simpleperf):
    label = a.label
    out_dir = os.path.join(REPO, 'local/research', label, 'profile')
    scratch = os.path.join(SCRATCH_ROOT, label)
    os.makedirs(scratch, exist_ok=True)
    perf_data = os.path.abspath(os.path.expanduser(a.from_perf))
    if not os.path.isfile(perf_data):
        raise SystemExit(f'perf.data not found: {perf_data}')
    symso = resolve_symso(os.path.expanduser(a.symso),
                          os.path.join(scratch, 'sym'))
    symdir = stage_symdir(symso, os.path.expanduser(a.libc) if a.libc else '',
                          os.path.join(scratch, 'symdir'))
    meta = [f'tool: odin_profile.py (PT1)',
            f'mode: offline --from-perf {perf_data}',
            f'perf.data: {os.path.getsize(perf_data)} B'
            f' sha={sha256_file(perf_data)[:16]}...',
            f'symso: {symso} ({os.path.getsize(symso)} B'
            f' sha={sha256_file(symso)[:16]}...)',
            f'symso Build ID: {build_id_of(symso)}']
    if a.apk:
        apk = os.path.abspath(os.path.expanduser(a.apk))
        want = apk_lib_build_id(apk)
        have = build_id_of(symso)
        meta.append(f'apk Build ID: {want} match={want == have}')
        if want != have:
            raise SystemExit(
                f'symso Build ID {have} != APK {want}: refusing')
    # Default companions live next to --from-perf (CP1 layout: scratch dir)
    # or next to --samples/--logcat when given explicitly.
    perf_dir = os.path.dirname(perf_data)
    samples = (os.path.abspath(os.path.expanduser(a.samples))
               if a.samples else None)
    logcat = (os.path.abspath(os.path.expanduser(a.logcat))
              if a.logcat else None)
    meta_p = (os.path.abspath(os.path.expanduser(a.meta))
              if a.meta else None)
    if not samples:
        for cand in (os.path.join(perf_dir, 'profile-samples.txt'),
                     os.path.join(REPO, 'local/research', label,
                                  'logs', label, 'profile-samples.txt')):
            if os.path.isfile(cand):
                samples = cand
                break
    if not samples or not os.path.isfile(samples):
        raise SystemExit('need --samples profile-samples.txt'
                         ' (schedstat sampler output)')
    meta.append(f'samples: {samples}')
    if logcat:
        meta.append(f'logcat: {logcat}')
    if meta_p:
        meta.append(f'meta: {meta_p}')
    r = analyze(perf_data, samples, logcat, meta_p, symdir, out_dir,
                simpleperf, meta)
    print(f'wrote {out_dir}/ ({r["frames"]:.0f} frames,'
          f' {r["ms_per_frame"]:.2f} ms/frame)')
    print('perf.data stays in scratch:', perf_data)


# ---------------------------------------------------------------------------
# Live run (F7/CP1 launch path, PT1-generic)
# ---------------------------------------------------------------------------
ODIN_SERIAL_FILE = os.path.join(HOME, 'dev/ssx3/local/odin-serial')
ODIN_PKG = 'com.ps2x.runner'
ODIN_FILES = f'/storage/emulated/0/Android/data/{ODIN_PKG}/files'
ODIN_DSCRAP = '/data/local/tmp/odinprof'
ODIN_LEASESH = os.path.join(REPO, 'local/tooling/odin_lease.sh')
ODIN_RESTORE = os.path.join(REPO, 'local/tooling/odin_restore_play.sh')
ODIN_PLAYDIR = os.path.join(HOME, 'dev/ssx3-work/odin-play')
ODIN_LABEL = 'ODINPROF'
# I31 odin-verify.txt full SHAs (read-only intactness check, never written).
ODIN_MC0_PINS = {
    'BASLUS-20772-GAM0001/BASLUS-20772-GAM0001': '4bdaee79a3bdaceef898bb44b6bcf62058e882a24237f8c81e46953a5067b78e',
    'BASLUS-20772-GAM0001/icon.sys': 'eab225745ef6695109743410261609e0569c14edb1555bc8941a965b3890a49c',
    'BASLUS-20772-GAM0001/ssx1.ico': '5f8b5a9252f868d2fbc03378846b84ed601a2c872f47028711de67a4a714fc0b',
    'BASLUS-20772-SET0001/BASLUS-20772-SET0001': '4a31a2d7e095e277edceae2243002055aa830019b3a1be64f126aee9129002f1',
    'BASLUS-20772-SET0001/icon.sys': 'dddf2d9c81a1c8bac2fe2036e1771dfa63635e3ae676760551defec2da67ee13',
    'BASLUS-20772-SET0001/ssx1.ico': '5f8b5a9252f868d2fbc03378846b84ed601a2c872f47028711de67a4a714fc0b',
}
# I26-FAST pad route (vsync clock; race HUD at tick ~1714).
ODIN_ROUTE = (
    '10611:start:250,12780:cross:250,14749:cross:250,16567:cross:250,18336:cross:250,19770:cross:250,21205:down:150,21706:down:150,22306:cross:250,24025:cross:250,28512:cross:200,28763:down:700,29513:cross:200,29764:down:700,30514:cross:200,30765:down:700,31515:cross:200,31766:down:700,32516:cross:200,32767:down:700,33517:cross:200,33768:down:700,34518:cross:200,34769:down:700,35519:cross:200,35770:down:700,36520:cross:200,36771:down:700,37521:cross:200,37772:down:700,38522:down:30000'
)


def play_env_sha():
    """Want-env SHA from the canonical SHA256SUMS (never hard-coded)."""
    sums = os.path.join(ODIN_PLAYDIR, 'SHA256SUMS')
    for line in open(sums):
        h, name = line.split()
        if name == 'ps2x.env':
            return h
    raise SystemExit(f'no ps2x.env pin in {sums}')


def run_live(a, simpleperf):
    import atexit
    import signal
    label = a.label
    D = open(ODIN_SERIAL_FILE).read().strip()
    OUT = os.path.join(REPO, 'local/research', label, 'logs', label)
    SCR = os.path.join(SCRATCH_ROOT, label)
    PROF = os.path.join(REPO, 'local/research', label, 'profile')
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(SCR, exist_ok=True)
    win = [int(x) for x in a.window.split(',')]
    if len(win) != 2:
        raise SystemExit('--window wants S,E')
    profile_after_tick = win[0]
    stop_tick = a.stop_tick or (3000 if a.cooldown_mode == 'screen' else 4500)
    T0 = [None]
    CLAIMED, PUSHED, LAUNCHED = {'v': False}, {'v': False}, {'v': False}
    DISCONNECTS = {'n': 0}

    # Cool-down BEFORE claiming anything (Brad 09-26 run modes).
    if not a.no_cooldown:
        cmd = [sys.executable, os.path.join(TOOL_DIR, 'odin_cooldown.py'),
               '--out', OUT, '--mode', a.cooldown_mode,
               '--max-temp-c', str(a.cooldown_max_temp),
               '--wait-s', str(a.cooldown_wait)]
        print('+ ' + ' '.join(cmd), flush=True)
        r = subprocess.run(cmd)
        if r.returncode != 0:
            raise SystemExit('cool-down refused (cap reached): aborting')

    def adb(*args, check=False, timeout=60):
        try:
            r = subprocess.run(['adb', '-s', D, *args], capture_output=True,
                               text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            DISCONNECTS['n'] += 1
            with open(f'{OUT}/disconnects.txt', 'a') as f:
                f.write(f't={time.time() - (T0[0] or time.time()):.1f}'
                        f' TIMEOUT adb {args}\n')
            if check:
                raise SystemExit(f'adb {args} timed out')
            return ''
        if r.returncode != 0 and ('device' in r.stderr
                                  and ('not found' in r.stderr
                                       or 'offline' in r.stderr)):
            DISCONNECTS['n'] += 1
            with open(f'{OUT}/disconnects.txt', 'a') as f:
                f.write(f't={time.time() - (T0[0] or time.time()):.1f}'
                        f' TRANSPORT adb {args}: {r.stderr.strip()[:160]}\n')
        if check and r.returncode != 0:
            raise SystemExit(f'adb {args} failed: {r.stderr}')
        return r.stdout

    def sh(cmd, timeout=60):
        return adb('shell', cmd, timeout=timeout)

    def log(msg):
        t = '' if T0[0] is None else f' t+{time.time() - T0[0]:7.1f}'
        line = f'[{time.strftime("%H:%M:%S")}{t}] {msg}'
        print(line, flush=True)
        with open(f'{OUT}/driver.log', 'a') as f:
            f.write(line + '\n')

    def lease_release():
        subprocess.run(['bash', ODIN_LEASESH, 'release', ODIN_LABEL],
                       capture_output=True, timeout=60)

    def cleanup():
        try:
            if PUSHED['v']:
                subprocess.run(['adb', '-s', D, 'push',
                                f'{OUT}/ps2x.env.brad',
                                f'{ODIN_FILES}/ps2x.env'],
                               capture_output=True, timeout=60)
        except Exception:
            pass
        try:
            if LAUNCHED['v']:
                subprocess.run(['adb', '-s', D, 'shell', 'am', 'force-stop',
                                ODIN_PKG], capture_output=True, timeout=30)
        except Exception:
            pass
        try:
            if CLAIMED['v']:
                subprocess.run(['bash', ODIN_LEASESH, 'release', ODIN_LABEL],
                               capture_output=True, timeout=60)
        except Exception:
            pass

    atexit.register(cleanup)
    signal.signal(signal.SIGTERM, lambda *_: sys.exit('SIGTERM'))

    try:
        _live_main(a, simpleperf, label, D, OUT, SCR, PROF, win,
                   profile_after_tick, stop_tick, T0, CLAIMED, PUSHED,
                   LAUNCHED, DISCONNECTS, adb, sh, log, lease_release)
    finally:
        cleanup()
        CLAIMED['v'] = False
        # Full play-state restore (own lease; never a lane copy of an old APK).
        cmd = ['bash', ODIN_RESTORE, f'{label}-prof']
        print('+ ' + ' '.join(cmd), flush=True)
        subprocess.run(cmd, timeout=900)


def _live_main(a, simpleperf, label, D, OUT, SCR, PROF, win,
               profile_after_tick, stop_tick, T0, CLAIMED, PUSHED, LAUNCHED,
               DISCONNECTS, adb, sh, log, lease_release):
    # --- preconditions (before claiming anything) ---
    lease = sh('cat /data/local/tmp/mg/LEASE').strip()
    kg = sh('dumpsys window policy | grep -m1 showing').strip()
    bat = sh('dumpsys battery')
    level = int(re.search(r'level: (\d+)', bat).group(1))
    acm = re.search(r'AC powered: (\w+)', bat)
    ac = acm.group(1) if acm else 'unknown'
    pid0 = sh(f'pidof {ODIN_PKG}').strip()
    dev_env_sha = sh(f'sha256sum {ODIN_FILES}/ps2x.env').split()[0]
    sh(f'mkdir -p {ODIN_FILES}/mc0-test')
    mc0t = sh(f'ls -A {ODIN_FILES}/mc0-test').strip()
    mc0_bad = [f for f, want in ODIN_MC0_PINS.items()
               if sh(f'sha256sum {ODIN_FILES}/mc0/{f}').split()[0] != want]
    want_env = play_env_sha()
    log(f'PRE lease="{lease}" keyguard="{kg}" battery={level}% ac={ac}'
        f' pid0={pid0 or "none"}')
    log(f'PRE device-env={dev_env_sha} mc0-test={mc0t!r} mc0-bad={mc0_bad}')
    if not (lease.startswith('LEASE_FREE') or lease.startswith(ODIN_LABEL + ' ')):
        sys.exit(f'lease held by someone else: {lease}')
    if 'showing=false' not in kg:
        sys.exit('keyguard showing: ask Brad to unlock')
    if level < a.min_battery or ac != 'true':
        sys.exit(f'battery {level}% ac={ac}: need >= {a.min_battery}%'
                 f' and AC powered (status ignored)')
    if pid0:
        sys.exit(f'app already running (pid {pid0}): stop, do not disturb')
    if dev_env_sha != want_env:
        sys.exit(f'device env is NOT the play env: {dev_env_sha}'
                 f' (refusing to touch)')
    if mc0_bad:
        sys.exit(f'Brad mc0 mismatch: {mc0_bad} (refusing to run)')
    if mc0t:
        sys.exit(f'mc0-test not empty: {mc0t!r}')
    if lease.startswith(ODIN_LABEL + ' '):
        CLAIMED['v'] = True
    else:
        r = subprocess.run(['bash', ODIN_LEASESH, 'claim', ODIN_LABEL],
                           capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            sys.exit(f'atomic claim failed: {r.stdout.strip()}'
                     f' {r.stderr.strip()}')
        CLAIMED['v'] = True
        log(f'LEASE claimed via odin_lease.sh: {r.stdout.strip()}')

    adb('pull', f'{ODIN_FILES}/ps2x.env', f'{OUT}/ps2x.env.brad')
    shutil.copy(f'{OUT}/ps2x.env.brad', f'{SCR}/ps2x.env.brad-device')
    if not a.apk:
        sys.exit('live mode needs --apk <path> --apk-sha <sha>')
    h1 = sha256_file(a.apk)
    h2 = sha256_file(a.apk)
    log(f'APK local sha x2 {h1} {h2}')
    if h1 != h2 or (a.apk_sha and h1 != a.apk_sha):
        sys.exit(f'APK SHA mismatch: {h1} {h2} want {a.apk_sha}')
    log('INSTALL ' + adb('install', '-r', a.apk, timeout=600).strip()
        .replace('\n', ' '))
    bp = sh(f'pm path {ODIN_PKG}').strip().split(':', 1)[-1]
    bsha = sh(f'sha256sum {bp}').split()[0]
    log(f'INSTALLED {bp} sha={bsha} match={bsha == h1}')
    if bsha != h1:
        sys.exit('installed base.apk does not match')
    env = [f'# odin_profile {label} variant {a.variant}',
           'PS2X_GS_BACKEND=parallel', 'PS2X_GS_TURNIP=1',
           f'PS2X_CD_IMAGE={ODIN_FILES}/SSX3.iso', 'PS2X_SKIP_MOVIE=1',
           'PS2X_SOUND=1', f'PS2X_MC_ROOT={ODIN_FILES}/mc0-test',
           f'PS2X_PAD_SCRIPT={ODIN_ROUTE}', 'PS2X_PAD_SCRIPT_CLOCK=vsync',
           'PS2X_VSYNC_RATE_LOG=1', 'PS2X_UNPACED=1']
    if a.variant == 'A':
        env.append('PS2X_PGS_PRESENT_PIPELINE=1')
    else:
        env.extend(['PS2X_PGS_SSAA=4', 'PS2X_PGS_HIRES_SCANOUT=1',
                    'PS2X_PGS_PRESENT_PIPELINE=1'])
    for e in (a.env or []):
        if '=' not in e:
            sys.exit(f'bad --env (want K=V): {e!r}')
        env.append(e)
    assert not any(x in e for e in env
                   for x in ('DUMP', 'TRACE', 'CAPTURE', 'ORACLE')), \
        'dump/trace key in env'
    assert all(not e.startswith('PS2X_PGS') or e.split('=')[0] in
               ('PS2X_PGS_PRESENT_PIPELINE', 'PS2X_PGS_SSAA',
                'PS2X_PGS_HIRES_SCANOUT', 'PS2X_PGS_FRAME_CONTEXTS',
                'PS2X_PGS_FLUSH_SPLIT')
               for e in env), \
        'unexpected PGS key in env'
    open(f'{OUT}/ps2x.env', 'w').write('\n'.join(env) + '\n')
    sh(f'mkdir -p {ODIN_DSCRAP}; rm -f {ODIN_DSCRAP}/*.png'
       f' {ODIN_DSCRAP}/*.data')
    adb('push', f'{OUT}/ps2x.env', f'{ODIN_FILES}/ps2x.env', check=True)
    PUSHED['v'] = True
    log('ENV ' + sh(f'sha256sum {ODIN_FILES}/ps2x.env').strip())
    sh(f'am force-stop {ODIN_PKG}')
    adb('logcat', '-c')
    lc = open(f'{OUT}/logcat.txt', 'w')
    lcp = subprocess.Popen(['adb', '-s', D, 'logcat', '-v', 'epoch',
                            '-b', 'main', '-b', 'crash',
                            '-s', 'ps2x', 'raylib', 'DEBUG', 'libc',
                            'AndroidRuntime'],
                           stdout=lc, stderr=subprocess.STDOUT)
    T0[0] = time.time()

    log('AM ' + sh(f'am start -n {ODIN_PKG}/android.app.NativeActivity')
        .strip().replace('\n', ' | '))
    LAUNCHED['v'] = True
    time.sleep(6)
    focus = sh('dumpsys window | grep -m1 mCurrentFocus').strip()
    if ODIN_PKG not in focus:
        sh('input keyevent 4')
        time.sleep(2)
        focus2 = sh('dumpsys window | grep -m1 mCurrentFocus').strip()
        log(f'BACK sent (was covered: {focus[:100]!r}'
            f' now: {focus2[:100]!r})')
    else:
        log(f'FOCUS app-foreground, no BACK ({focus[:100]!r})')
    time.sleep(2)

    def pick_layer():
        cands = []
        for l in sh('dumpsys SurfaceFlinger --list').splitlines():
            if ODIN_PKG not in l or any(x in l for x in
                                        ('leash', 'InputSink', 'Background')):
                continue
            cands += re.findall(r'(com\.ps2x\.runner/android\.app'
                                r'\.NativeActivity#\d+)', l)
            cands.append(l.strip())
        seen = []
        for c in cands:
            if c in seen:
                continue
            seen.append(c)
            rows = [r for r in sh(f"dumpsys SurfaceFlinger --latency '{c}'")
                    .splitlines() if '\t' in r]
            if len(rows) > 2:
                return c, seen
        return '', seen

    layer, tried = pick_layer()
    log(f'LAYER {layer!r} tried={tried}')
    transport = subprocess.run(['adb', 'devices', '-l'], capture_output=True,
                               text=True, timeout=30).stdout
    open(f'{OUT}/transport-start.txt', 'w').write(f'serial={D}\n{transport}')
    json.dump({'T0': T0[0], 'layer': layer, 'env': env,
               'variant': a.variant, 'serial': D,
               'cooldown_mode': a.cooldown_mode,
               'window': win, 'profile_secs': a.profile_secs,
               'offcpu': a.offcpu},
              open(f'{OUT}/meta.json', 'w'), indent=1)
    rate_re = re.compile(r'\[vsync-rate\] tick=(\d+) rate=([\d.]+)')
    cpu_win = win
    cpu_snap = {}

    def task_sched(pid):
        out = sh(f'for t in /proc/{pid}/task/*; do echo "== ${{t##*/}}'
                 f' $(cat $t/comm)"; cat $t/stat; cat $t/schedstat; done',
                 timeout=90)
        res, tid, comm = {}, '', ''
        for line in out.splitlines():
            line = line.strip()
            if line.startswith('=='):
                _, tid, comm = line.split(None, 2)
            elif ')' in line and tid and tid not in res:
                head, rest = line.split(')', 1)
                f = rest.split()
                res[tid] = [comm, int(f[11]) + int(f[12]), f[36], 0, 0, 0]
            elif tid in res and res[tid][3] == 0 and line and line[0].isdigit():
                p = line.split()
                if len(p) >= 3:
                    res[tid][3], res[tid][4], res[tid][5] = (
                        int(p[0]), int(p[1]), int(p[2]))
                tid = ''
        return res

    scap_ticks = [int(x) for x in a.scap_ticks.split(',') if x]
    n_scap = [0]
    last_scap, last_lat, last_gpu = [0.0], [0.0], [0.0]
    profiled = [False]
    tick = [0]

    def scap(tag):
        n_scap[0] += 1
        name = f'sc{n_scap[0]:02d}-{tag}-t{int(time.time() - T0[0])}.png'
        sh(f'screencap -p {ODIN_DSCRAP}/{name}')
        log(f'SCAP {name} tick~{tick[0]}')

    while True:
        el = time.time() - T0[0]
        try:
            txt = open(f'{OUT}/logcat.txt', errors='replace').read()
        except OSError:
            txt = ''
        m = rate_re.findall(txt)
        if m:
            tick[0] = int(m[-1][0])
        if 'FATAL' in txt or 'Fatal signal' in txt:
            log('FATAL seen in logcat')
            break
        pid = sh(f'pidof {ODIN_PKG}').strip()
        if not pid:
            log('process gone')
            break
        if el - last_lat[0] >= 10:
            last_lat[0] = el
            if not layer:
                layer, tried = pick_layer()
                log(f'LAYER retry {layer!r} tried={tried}')
            therm = sh('echo "$(cat /sys/devices/system/cpu/cpu5/cpufreq/scaling_cur_freq) '
                       '$(cat /sys/devices/system/cpu/cpu6/cpufreq/scaling_cur_freq) '
                       '$(cat /sys/devices/system/cpu/cpu7/cpufreq/scaling_cur_freq) '
                       '$(for z in /sys/class/thermal/thermal_zone*; do [ "$(cat $z/type)" = cpu-1-1-1 ] && cat $z/temp; done) '
                       '$(dumpsys thermalservice | grep -m1 "Thermal Status" | tr -dc 0-9)"').split()
            with open(f'{OUT}/thermal.txt', 'a') as f:
                f.write(f't={el:.1f} tick={tick[0]} ' + ' '.join(therm) + '\n')
            with open(f'{OUT}/sf-latency.txt', 'a') as f:
                f.write(f'POLL t={el:.1f} tick={tick[0]}\n')
                f.write(sh(f"dumpsys SurfaceFlinger --latency '{layer}'"))
        if el - last_gpu[0] >= 5:
            last_gpu[0] = el
            gl = sh('cat /sys/class/kgsl/kgsl-3d0/gpubusy; cat /sys/class/kgsl/kgsl-3d0/gpuclk').splitlines()
            g = (gl[0].split() if gl else [])
            clk = gl[1].strip() if len(gl) > 1 else '?'
            try:
                busy, total = int(g[0]), int(g[1])
                pct = 100.0 * busy / total if total > 0 else -1.0
                with open(f'{OUT}/gpubusy.txt', 'a') as f:
                    f.write(f't={el:.1f} tick={tick[0]} busy={busy}'
                            f' total={total} pct={pct:.1f} gpuclk={clk}\n')
            except (ValueError, IndexError):
                with open(f'{OUT}/gpubusy.txt', 'a') as f:
                    f.write(f't={el:.1f} tick={tick[0]}'
                            f' raw={" ".join(g)} gpuclk={clk}\n')
        while scap_ticks and tick[0] >= scap_ticks[0]:
            scap(f'tick{scap_ticks.pop(0)}')
            last_scap[0] = el
        if cpu_win and 'start' not in cpu_snap and tick[0] >= cpu_win[0]:
            t_edge = time.time()
            cpu_snap['start'] = (t_edge, tick[0], task_sched(pid))
            log(f'CPUWIN start tick={tick[0]}')
        if cpu_win and 'start' in cpu_snap and 'end' not in cpu_snap \
                and tick[0] >= cpu_win[1]:
            t_edge = time.time()
            cpu_snap['end'] = (t_edge, tick[0], task_sched(pid))
            log(f'CPUWIN end tick={tick[0]}')
        if profile_after_tick and not profiled[0] \
                and tick[0] >= profile_after_tick:
            profiled[0] = True
            log(f'PROFILE start tick={tick[0]}')
            prof_base = (f'simpleperf record -g --app {ODIN_PKG} '
                         f'-o {ODIN_DSCRAP}/perf-{label}.data '
                         f'--duration {a.profile_secs}')
            # NB: --trace-offcpu requires -e cpu-clock (CP1 R2).
            prof_cmd = (f'simpleperf record -g -e cpu-clock --trace-offcpu'
                        f' --app {ODIN_PKG} -o {ODIN_DSCRAP}/perf-{label}.data'
                        f' --duration {a.profile_secs}') if a.offcpu else prof_base
            p = subprocess.Popen(['adb', '-s', D, 'shell', prof_cmd],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, text=True)
            samp = open(f'{OUT}/profile-samples.txt', 'w')
            t_prof0 = time.time()
            while p.poll() is None:
                try:
                    txt2 = open(f'{OUT}/logcat.txt', errors='replace').read()
                except OSError:
                    txt2 = ''
                m2 = rate_re.findall(txt2)
                tick[0] = int(m2[-1][0]) if m2 else tick[0]
                el2 = time.time() - T0[0]
                s = sh('echo THERM cpu6=$(cat /sys/devices/system/cpu/cpu6/cpufreq/scaling_cur_freq) '
                       'cpu7=$(cat /sys/devices/system/cpu/cpu7/cpufreq/scaling_cur_freq) '
                       'status=$(dumpsys thermalservice | grep -m1 "Thermal Status" | tr -dc 0-9) '
                       'GPU busy=$(cat /sys/class/kgsl/kgsl-3d0/gpubusy) '
                       'gpuclk=$(cat /sys/class/kgsl/kgsl-3d0/gpuclk)',
                       timeout=60)
                samp.write(f't={el2:.1f} tick={tick[0]} {s.strip()}\n')
                samp.flush()
                try:
                    snap = task_sched(pid)
                    for tid2, row in sorted(snap.items()):
                        samp.write(f'  sched {tid2} {row[0]} cpu={row[2]}'
                                   f' ticks={row[1]} run_ns={row[3]}'
                                   f' wait_ns={row[4]} slices={row[5]}\n')
                    samp.flush()
                except Exception as e:
                    samp.write(f'  sched ERROR {e}\n')
                time.sleep(2)
            prof_out = p.stdout.read()
            open(f'{OUT}/simpleperf-record.txt', 'w').write(prof_out)
            samp.write(f'PROFILE wall={time.time() - t_prof0:.1f}s'
                       f' end-tick~{tick[0]}\n')
            samp.close()
            log(f'PROFILE end wall={time.time() - t_prof0:.1f}s'
                f' tick~{tick[0]}')
            log(f'PROFILE out: {prof_out.strip()[:300]!r}')
            perf_ls = sh(f'ls -l {ODIN_DSCRAP}/perf-{label}.data 2>&1').strip()
            log(f'PROFILE data: {perf_ls[:160]!r}')
            try:
                perf_sz = int(perf_ls.split()[4]) if perf_ls.startswith('-') \
                    else -1
            except (ValueError, IndexError):
                perf_sz = -1
            if a.offcpu and perf_sz < 1024:
                log('PROFILE offcpu refused; falling back to plain -g')
                out2 = sh(prof_base, timeout=a.profile_secs + 120)
                open(f'{OUT}/simpleperf-record-fallback.txt', 'w').write(out2)
                try:
                    txt2 = open(f'{OUT}/logcat.txt', errors='replace').read()
                except OSError:
                    txt2 = ''
                m2 = rate_re.findall(txt2)
                tick[0] = int(m2[-1][0]) if m2 else tick[0]
                log(f'PROFILE fallback end tick~{tick[0]}')
                log(f'PROFILE fallback data: '
                    f'{sh(f"ls -l {ODIN_DSCRAP}/perf-{label}.data 2>&1").strip()[:160]!r}')
            scap('postprofile')
            break
        if tick[0] >= stop_tick and not profile_after_tick:
            log(f'STOP tick {tick[0]} >= {stop_tick}')
            break
        if el >= 180 and tick[0] < 570:
            log('STOP title not reached by 180s')
            break
        if el >= a.wall:
            log(f'STOP wall cap {a.wall}s tick={tick[0]}')
            break
        time.sleep(2)

    scap('final')
    time.sleep(1)
    log('THREADS\n' + sh(f'top -H -b -n1 -p $(pidof {ODIN_PKG}) | head -20'))
    log('BATTERY ' + ' '.join(l.strip() for l in sh('dumpsys battery')
                              .splitlines() if 'level' in l or 'status' in l))
    sh(f'am force-stop {ODIN_PKG}')
    LAUNCHED['v'] = False
    time.sleep(2)
    lcp.terminate()
    for name in sh(f'ls {ODIN_DSCRAP}').split():
        if name.endswith('.png') or name.endswith('.data'):
            adb('pull', f'{ODIN_DSCRAP}/{name}', f'{SCR}/{name}')
    # Device libc for host symbolization (cheap, one file).
    adb('pull', '/system/lib64/libc.so', f'{SCR}/libc-device.so')
    adb('push', f'{OUT}/ps2x.env.brad', f'{ODIN_FILES}/ps2x.env', check=True)
    PUSHED['v'] = False
    rest = sh(f'sha256sum {ODIN_FILES}/ps2x.env').split()[0]
    log(f'RESTORE {rest} match={rest == want_env}')
    mc0_bad2 = [f for f, want in ODIN_MC0_PINS.items()
                if sh(f'sha256sum {ODIN_FILES}/mc0/{f}').split()[0] != want]
    log(f'MC0-AFTER bad={mc0_bad2}')
    with open(f'{OUT}/scap-sha.txt', 'w') as f:
        for name in sorted(os.listdir(SCR)):
            if name.endswith(('.png', '.data', '.so')):
                f.write(f'{sha256_file(os.path.join(SCR, name))}  {name}\n')
    transport_end = subprocess.run(['adb', 'devices', '-l'],
                                   capture_output=True, text=True,
                                   timeout=30).stdout
    open(f'{OUT}/transport-end.txt', 'w').write(
        f'serial={D}\ndisconnects={DISCONNECTS["n"]}\n{transport_end}')
    log(f'END pid-after={sh(f"pidof {ODIN_PKG}").strip() or "none"}'
        f' disconnects={DISCONNECTS["n"]}')
    lease_release()
    CLAIMED['v'] = False

    # --- host-side analysis (same as --from-perf) ---
    perf_data = os.path.join(SCR, f'perf-{label}.data')
    if not os.path.isfile(perf_data) \
            or os.path.getsize(perf_data) < 1024:
        log('ANALYZE skipped: no usable perf.data pulled')
        return
    if not a.symso:
        log('ANALYZE skipped: no --symso given (perf.data stays in scratch)')
        return
    symso = resolve_symso(os.path.expanduser(a.symso),
                          os.path.join(SCR, 'sym'))
    libc = os.path.join(SCR, 'libc-device.so')
    symdir = stage_symdir(symso, libc if os.path.isfile(libc) else '',
                          os.path.join(SCR, 'symdir'))
    want, have = apk_lib_build_id(a.apk), build_id_of(symso)
    log(f'BUILDID apk={want} symso={have} match={want == have}')
    if want != have:
        sys.exit(f'symso Build ID {have} != APK {want}: refusing')
    meta = [f'tool: odin_profile.py (PT1)',
            f'mode: live (cooldown={a.cooldown_mode})',
            f'apk: {a.apk} sha={a.apk_sha}',
            f'perf.data: {os.path.getsize(perf_data)} B'
            f' sha={sha256_file(perf_data)[:16]}...',
            f'symso: {symso} Build ID {have} (matches APK)',
            f'window arg: {a.window}; profile_after_tick={profile_after_tick}']
    analyze(perf_data, f'{OUT}/profile-samples.txt', f'{OUT}/logcat.txt',
            f'{OUT}/meta.json', symdir, PROF, simpleperf, meta)
    log(f'ANALYZE wrote {PROF}/')


def build_arg_parser():
    ap = argparse.ArgumentParser(
        description='One-command Odin per-thread profiler (PT1).')
    ap.add_argument('--label', required=True,
                    help='lane label; reports go to local/research/<L>/profile/')
    ap.add_argument('--simpleperf', default='',
                    help='host simpleperf binary (default: NDK on the mini)')
    # Live run.
    ap.add_argument('--apk', default='')
    ap.add_argument('--apk-sha', default='')
    ap.add_argument('--env', action='append', default=[],
                    help='extra ps2x.env line K=V (repeatable)')
    ap.add_argument('--window', default='1900,2500',
                    help='profile window S,E (profile starts at tick S)')
    ap.add_argument('--profile-secs', type=int, default=20)
    ap.add_argument('--offcpu', action='store_true',
                    help='record with --trace-offcpu (needed for blocked splits)')
    ap.add_argument('--variant', choices=('A', 'B'), default='A')
    ap.add_argument('--wall', type=float, default=600.0)
    ap.add_argument('--stop-tick', type=int, default=0,
                    help='0 = auto by cooldown mode (screen 3000, final 4500)')
    ap.add_argument('--scap-ticks', default='2100,3000,4000')
    ap.add_argument('--min-battery', type=int, default=20)
    ap.add_argument('--no-cooldown', action='store_true')
    ap.add_argument('--cooldown-mode', choices=('screen', 'final'),
                    default='screen',
                    help='odin_cooldown.py mode; numbers are labeled with it')
    ap.add_argument('--cooldown-wait', type=float, default=180.0,
                    help='final-mode fixed wait (s)')
    ap.add_argument('--cooldown-max-temp', type=float, default=42.0,
                    help='screen-mode temp gate (C)')
    # Offline re-analysis.
    ap.add_argument('--from-perf', default='',
                    help='existing perf.data (offline mode, no device)')
    ap.add_argument('--symso', default='',
                    help='unstripped libps2EntryRunner.so, or bytesize:/wsl/path')
    ap.add_argument('--samples', default='',
                    help='profile-samples.txt (offline; default: beside perf)')
    ap.add_argument('--logcat', default='',
                    help='logcat.txt with [vsync-rate] lines (offline)')
    ap.add_argument('--meta', default='',
                    help='meta.json with T0 (offline)')
    ap.add_argument('--libc', default='',
                    help='device libc.so for symbolization (offline/live)')
    return ap


def main():
    a = build_arg_parser().parse_args()
    simpleperf = (a.simpleperf or shutil.which('simpleperf')
                  or SIMPLEPERF_DEFAULT)
    if not (simpleperf and os.path.exists(simpleperf)):
        raise SystemExit(f'host simpleperf not found: {simpleperf}')
    if a.from_perf:
        if not a.symso:
            raise SystemExit('offline mode needs --symso <unstripped .so>')
        run_offline(a, simpleperf)
    else:
        run_live(a, simpleperf)


if __name__ == '__main__':
    main()

