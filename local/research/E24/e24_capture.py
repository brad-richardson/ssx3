#!/usr/bin/env python3
"""E24 demand-watch capture driver. Fresh T13 pre-claims, caps, owned lease cleanup. One boot."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / 'local/research/E24'))
from e24_common import sample as resource_sample, bound as resource_bound, admission, size as owned_size
from e24_validate import suite as run_suite
EVIDENCE = REPO / 'local/research/E24'
W = Path('/Volumes/Extreme SSD/ps2recomp-spike')
FORK = W / 'PS2Recomp'
RUN = W / 'P1/run'
BIN = Path('/tmp/e18-mpeg-link/runtime/ps2xRuntime/ps2EntryRunner')
TEST = Path('/tmp/e18-mpeg-link/runtime/ps2xTest/ps2x_tests')
ELF = W / 'P1/cd/SLUS_207.72'
LEASE = Path('/tmp/ssx3-p-lane-lease')
WAITS = RUN / 'e24-waits.log'
ELF_SHA = '1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc'
DISPLAY = [0x12000000, 0x12000020, 0x12000070, 0x12000080,
           0x12000090, 0x120000a0, 0x120000e0]
OFFSETS = [0x5a78, 0x5a7c, 0x5a84, 0x5a88, 0x5a74, 0xf44, 0x59e8]
# E24 step 4: the guest producer/source structures the E7 tap named on this exact
# run shape in E18/E21/E22. Watching them measures whether the guest refills the
# MPEG source while the caller is parked -- the one fact that decides whether a
# re-ask at C2a's site could ever be satisfied. Addresses and their receipts are
# tabled in BOOT-DESIGN.md; each watch covers an 8-byte window.
# E24 CHANGE 2: the TIERED extended watch set (BOOT-DESIGN.md, watch-set.json).
# E23 watched 8 producer/source words and NAMED the gap: the descriptor head
# advanced 0x548800 = 0x548880 and that successor node was unwatched, so its
# post-park silence was vacuous. This covers the whole descriptor node array,
# both buffers, and the bytes just past the delivered region -- 230 entries
# against e23a's 37, sized by the cost model because diagWatchEmit scans the
# whole vector on EVERY guest store.
_WATCH_SET = json.loads((Path(__file__).resolve().parent / 'watch-set.json').read_text())
PRODUCER = [0x5487c0, 0x587b28, 0x587b78, 0x587b7c]   # carried singles, not in any tier
for _tier in _WATCH_SET['tiers']:
    PRODUCER.extend(_tier['addrs'])
assert len(PRODUCER) == _WATCH_SET['new_entries'] + _WATCH_SET['carried_producer_singles'], len(PRODUCER)
MIB = 1024 * 1024
ALLOCATED_CAPS=dict(boot_log=256*MIB,trace=96*MIB,function_log=1024*MIB,e4_dir=64*MIB,park_dir=128*MIB,frames_dir=64*MIB,e7_dir=64*MIB,parser_dir=64*MIB,aggregate=1536*MIB)
CAPS = dict(wall_s=90, terminate_reserve_s=15, progress_lines=1000000,
            source_window_end=603,
            boot_log=256*MIB, trace=96*MIB, function_log=1024*MIB,
            e4_dir=12*MIB, park_dir=32*MIB, frames_dir=32*MIB,
            e7_dir=8*MIB, parser_dir=16*MIB,
            aggregate=1536*MIB, poll_s=0.25, grace_s=10)


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def command(args, cwd=REPO):
    p = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    return dict(argv=[str(x) for x in args], rc=p.returncode, stdout=p.stdout, stderr=p.stderr)


def append_wait(text):
    with WAITS.open('a') as f:
        f.write(text + '\n')


def preflight(label):
    record = dict(label=label, utc=utc(), caps=CAPS, allocated_caps=ALLOCATED_CAPS, lease_absent=not LEASE.exists())
    if LEASE.exists():
        append_wait(f'{label.upper()} STOP {utc()} owner={LEASE.read_text().strip()!r}; E24 forbids lease wait')
        raise RuntimeError('Lease occupied; E24 tables and stops without waiting')
    record['runner_check'] = command(['pgrep', '-x', 'ps2EntryRunner'])
    assert record['runner_check']['rc'] == 1, record['runner_check']
    record['fork_head'] = command(['git', '-C', str(FORK), 'rev-parse', 'HEAD'])
    record['fork_status'] = command(['git', '-C', str(FORK), 'status', '--short'])
    manifest_path=EVIDENCE/'e24a-build.json'
    assert manifest_path.exists(), 'fresh E24 probe-gate manifest required'
    build=json.loads(manifest_path.read_text())
    entry=json.loads((EVIDENCE/'entry-preflight.json').read_text())
    assert entry['suite_rc']==entry['binding_rc']==0 and entry['query_cases']==4
    assert entry['predicate_cases']==14 and entry['leaf_cases']==24 and entry['consumer_cases']==3 and entry['leaf_present'] and entry['mpeg_delivery_cases']==2 and entry['new_regression_cases']==6 and entry['run_exit_cases']==6
    assert entry['isolation_identical'] and entry['loaded_regression_green'] and entry['q1_cases']==9 and entry['q2_audit']
    record['build_manifest']=build
    assert record['fork_head']['stdout'].strip() == build['fork_head']
    assert record['fork_status']['stdout']==build['fork_status'], record['fork_status']
    # E24 CHANGE 1: PRESENCE first. e23a's driver went straight to .stat() and
    # would raise FileNotFoundError deep inside the loop; E24 opened to exactly
    # that situation (all three protected build trees wiped by a host restart)
    # and a boot driver must refuse it as a named gate, before the lease.
    record['presence'] = {}
    for path in (BIN, TEST, ELF, W / 'P1/SLUS_207.72', W / 'SSX 3 (USA).iso',
                 EVIDENCE / 'parser/e21-parser-observer.dylib'):
        record['presence'][str(path)] = path.exists()
    absent = sorted(k for k, v in record['presence'].items() if not v)
    if absent:
        raise RuntimeError('required binaries absent; E24 tables and stops '
                           'without claiming the lease: ' + '; '.join(absent))
    record['files'] = []
    for path, size, expected in [(BIN,build['bin_size'],build['bin_sha']),(TEST,build['test_size'],build['test_sha']),
                                  (W/'SSX 3 (USA).iso',3005415424,None),
                                  (ELF,3890784,ELF_SHA),(W/'P1/SLUS_207.72',3890784,ELF_SHA),
                                  (EVIDENCE/'parser/e21-parser-observer.dylib',None,json.loads((EVIDENCE.parent/'E21/parser-build.json').read_text())['observer']['sha256'])]:
        item = dict(path=str(path), bytes=path.stat().st_size)
        if size is not None:
            assert item['bytes'] == size, item
        if expected:
            item['sha256'] = sha(path)
            assert item['sha256'] == expected, item
        record['files'].append(item)
    record['space'] = command(['df', '-h', str(W), '/private/tmp'])
    record['resource_admission']=resource_sample()
    assert not resource_bound(record['resource_admission'])
    admission(record['resource_admission'])
    record['wait_tails'] = {}
    for path in sorted(RUN.glob('*-waits.log'), key=lambda p:p.stat().st_mtime, reverse=True):
        if path.name.startswith('._'):
            continue
        record['wait_tails'][path.name] = path.read_text().splitlines()[-4:]
        if len(record['wait_tails']) >= 8:
            break
    record['aligner'] = command([sys.executable,'-B','tools/trace_align.py','--selftest'])
    (EVIDENCE/f'{label}-aligner.txt').write_text(record['aligner']['stdout']+record['aligner']['stderr'])
    assert record['aligner']['rc']==0 and 'selftest: ALL PASS' in record['aligner']['stdout']
    suite_rc,suite_text,_ = run_suite(label+'-preclaim')
    record['suite'] = dict(rc=suite_rc, tail=suite_text.splitlines()[-7:])
    assert suite_rc==0 and f'Total Tests: {build["test_count"]}' in suite_text and 'Failed: 0' in suite_text
    record['runner_recheck'] = command(['pgrep','-x','ps2EntryRunner'])
    assert record['runner_recheck']['rc']==1 and not LEASE.exists()
    record['preflight_complete_utc'] = utc()
    (EVIDENCE/f'{label}-preflight.json').write_text(json.dumps(record,indent=2)+'\n')
    return record


def size(path, allocated=False):
    path=Path(path)
    return owned_size(path, allocated)+owned_size(path.with_name('._'+path.name), allocated)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase',choices=['a'])
    parser.add_argument('--s',type=lambda x:int(x,0),default=0x61ba60)
    parser.add_argument('--arm',type=int,default=600)
    parser.add_argument('--report-all',action='store_true',help='Retain each missing-target branch receipt')
    parser.add_argument('--wall',type=int,default=90)
    args=parser.parse_args()
    assert args.wall == 90
    CAPS['wall_s']=args.wall
    def interrupted(signum, frame):
        raise KeyboardInterrupt(f'capture driver signal {signum}')
    signal.signal(signal.SIGTERM, interrupted)
    assert os.environ.get('COPYFILE_DISABLE')=='1'
    assert args.s is not None and args.arm>0
    assert not (EVIDENCE/'boot-attempt.json').exists(), 'E24 permits only one boot'
    assert not list(EVIDENCE.glob('e24?-result.json')), 'E24 permits only one boot'
    label='e24'+args.phase
    assert args.report_all, 'E24 requires REPORT_ALL=1'
    paths=dict(boot_log=RUN/f'boot-{label}-1.log',trace=RUN/f'syscalls-{label}-on.txt',
               function_log=RUN/'ps2_log.txt',e4_dir=RUN/f'{label}-1',
               park_dir=RUN/f'park-{label}-1',frames_dir=RUN/f'frames-{label}-1',parser_dir=RUN/f'{label}-parser')
    if args.s is not None:
        paths['e7_dir']=RUN/f'{label}-join'
    kept_function=RUN/f'ps2_log-{label}-1.txt'
    assert not kept_function.exists()
    assert not paths['function_log'].exists(), 'shared function log already exists; table ownership gap'
    for key,path in paths.items():
        if key!='function_log':
            assert not path.exists(), f'Refuse to overwrite {path}'
    watches=[0x4a289c]+DISPLAY
    if args.s is not None:
        watches += [args.s+off for off in OFFSETS]
        watches += [0x10005000,0x1000a000,0x1000a010,0x1000a020]
    watches += [0xb851a0,0xb851a4,0xb851ac,0xb851e0,0xb84e84,0xb84d88,0x4a3938,0x4a393c,0x4a3940,0x4a3944]
    watches += PRODUCER
    try:
        preflight(label)
    except Exception as error:
        (EVIDENCE/'probe-preclaim-stop.json').write_text(json.dumps(dict(utc=utc(),error=str(error),lease_present=LEASE.exists()),indent=2)+'\n')
        raise
    env=dict(os.environ)
    inherited={k:v for k,v in env.items() if k.startswith('PS2X_')}
    for key in inherited:
        del env[key]
    # E24 CHANGE 3: PS2X_DIAG_SEMA / _S0 are already compiled into the proven
    # runner (EeScheduler.cpp:156,168) and print nothing when unset, so this
    # needs no rebuild and no fork edit. They are the ONLY source of the waker
    # `ra` per signal -- the always-on park tally records the syscall stub pc
    # (0x423dc8 / 0x423dd8), which cannot name a caller. Objective 2.
    env.update(PS2X_CD_IMAGE=str(W/'SSX 3 (USA).iso'),PS2X_DIAG_PERIOD_MS='5000',
               PS2X_DIAG_SEMA='1',PS2X_DIAG_SEMA_S0='1',
               PS2X_DIAG_SEMA_CREATE='1',PS2X_DIAG_PARK='1',PS2X_DIAG_PARK_DIR=str(paths['park_dir']),
               PS2X_TRACE_SYSCALLS=str(paths['trace']),PS2X_TRACE_SYSCALLS_PC='1',
               PS2X_FRAME_DUMP_DIR=str(paths['frames_dir']),PS2X_E15_ALIGN='1',PS2X_E15_TRACE='1',
               PS2X_E4_DIR=str(paths['e4_dir']),PS2X_E21_PARSER_DIR=str(paths['parser_dir']),
               DYLD_INSERT_LIBRARIES=str(EVIDENCE/'parser/e21-parser-observer.dylib'),
               PS2X_DIAG_WATCH=','.join(hex(x) for x in watches))
    if args.s is not None:
        env['PS2X_E7_DIR']=str(paths['e7_dir'])
    if args.report_all:
        env['PS2X_DIAG_REPORT_ALL']='1'
    boot_argv=[str(BIN),str(ELF)]
    assert not any('stdbuf' in x for x in boot_argv), 'E24 forbids stdbuf in the boot argv'
    config=dict(label=label,argv=boot_argv,cwd=str(RUN),
                caps=CAPS,allocated_caps=ALLOCATED_CAPS,watch_addresses=[hex(x) for x in watches],s=args.s,
                env={k:v for k,v in env.items() if k.startswith('PS2X_') or k=='DYLD_INSERT_LIBRARIES'},
                stdbuf_free=True,dyld_insert=env.get('DYLD_INSERT_LIBRARIES'),
                argv0_is_runner=boot_argv[0]==str(BIN),
                removed_inherited_keys=sorted(inherited),paths={k:str(v) for k,v in paths.items()})
    (EVIDENCE/f'{label}-config.json').write_text(json.dumps(config,indent=2)+'\n')
    print(json.dumps(config),flush=True)
    for key,path in paths.items():
        if key.endswith('_dir'):
            path.mkdir()
    token=f'{label.upper()}\npid={os.getpid()} utc={utc()}\n'
    try:
        with LEASE.open('x') as f:
            f.write(token)
    except FileExistsError:
        (EVIDENCE/'probe-preclaim-stop.json').write_text(json.dumps(dict(utc=utc(),error='lease occupied at atomic claim',owner=LEASE.read_text()),indent=2)+'\n')
        raise
    append_wait(f'{label.upper()} CLAIM {utc()} preflight=green caps={json.dumps(CAPS,sort_keys=True)}')
    p=None
    result=dict(label=label,claim_utc=utc(),bound=None)
    free_before=shutil.disk_usage(W).free
    result['ssd_free_before']=free_before
    t0=time.monotonic()
    try:
        with (EVIDENCE/f'{label}-liveness.txt').open('w') as live, paths['boot_log'].open('wb') as log:
            def emit(obj):
                line=json.dumps(obj,sort_keys=True)
                live.write(line+'\n');live.flush();print(line,flush=True)
            (EVIDENCE/'boot-attempt.json').write_text(json.dumps(dict(utc=utc(),label=label,lease_token=token,argv=config['argv']),indent=2)+'\n')
            p=subprocess.Popen(config['argv'],cwd=RUN,env=env,stdout=log,stderr=subprocess.STDOUT)
            result['pid']=p.pid
            result['boot_utc']=utc()
            trace_pos=0;lines=0;span_at=None;last_emit=-5
            while p.poll() is None:
                elapsed=time.monotonic()-t0
                counts={k:size(path) for k,path in paths.items()}
                counts['aggregate']=sum(counts.values())
                allocated={k:size(path,True) for k,path in paths.items()}
                allocated['aggregate']=sum(allocated.values())
                if paths['trace'].exists():
                    with paths['trace'].open('rb') as f:
                        f.seek(trace_pos)
                        while chunk:=f.read(MIB):
                            lines+=chunk.count(b'\n')
                        trace_pos=f.tell()
                with paths['boot_log'].open('rb') as f:
                    f.seek(max(0,counts['boot_log']-2*MIB))
                    has_span=b'[e4:span-complete]' in f.read()
                if has_span and span_at is None:
                    span_at=elapsed
                    emit(dict(event='span-complete',elapsed_s=elapsed,grace_s=CAPS['grace_s']))
                observation_tick=None
                event_path=paths.get('e7_dir',RUN)/'e7-events.txt'
                if event_path.exists():
                    import re
                    with event_path.open('rb') as f:
                        f.seek(max(0,event_path.stat().st_size-8192))
                        ticks=re.findall(rb'\btick=(\d+)',f.read())
                    if ticks:observation_tick=max(map(int,ticks))
                resources=resource_sample()
                sample=dict(resources=resources,elapsed_s=round(elapsed,3),trace_lines=lines,observation_tick=observation_tick,bytes=counts,allocated=allocated,ssd_free=shutil.disk_usage(W).free,ssd_free_delta=free_before-shutil.disk_usage(W).free)
                if elapsed-last_emit>=5:
                    emit(sample);last_emit=elapsed
                bound=next((k+'_bytes' for k,n in counts.items() if n>=CAPS[k]-(min(8*MIB,CAPS[k]//4) if args.report_all or k in ['function_log','aggregate'] else 0)),None)
                if bound is None:
                    bound=next((k+'_allocated_bytes' for k,n in allocated.items() if n>=ALLOCATED_CAPS[k]-8*MIB),None)
                if bound is None: bound=resource_bound(resources)
                if bound is None and lines>=CAPS['progress_lines']: bound='progress'
                if bound is None and elapsed>=CAPS['wall_s']-CAPS['terminate_reserve_s']: bound='wall'
                if bound:
                    result.update(bound=bound,bind=sample,span_complete_s=span_at,signal_utc=utc())
                    emit(dict(event='SIGTERM',bound=bound,**sample))
                    p.terminate()
                    try: p.wait(timeout=15)
                    except subprocess.TimeoutExpired:
                        p.kill();p.wait()
                        result['needed_sigkill']=True
                    break
                time.sleep(CAPS['poll_s'])
            result['rc']=p.returncode
            # E24 CHANGE 4: record span-complete on EVERY path, not only when a
            # bound fires, so the next lane can refit the watch-count cost model
            # in BOOT-DESIGN.md against a third data point.
            result.setdefault('span_complete_s',span_at)
            result['watch_entries']=len(config['watch_addresses'])
            result['process_end_utc']=utc()
            result['elapsed_s']=time.monotonic()-t0
            if result['bound'] is None: result['bound']='exited'
    finally:
        if p is not None and p.poll() is None:
            p.terminate()
            try: p.wait(timeout=15)
            except subprocess.TimeoutExpired: p.kill();p.wait()
        try:
            if p is not None and paths['function_log'].exists():
                paths['function_log'].rename(kept_function)
        finally:
            if LEASE.exists() and LEASE.read_text()==token:
                LEASE.unlink()
                result['release_utc']=utc()
                append_wait(f'{label.upper()} RELEASE {result["release_utc"]} bound={result["bound"]} rc={result.get("rc")}')
            else:
                result['lease_ownership_error']=True
            (EVIDENCE/f'{label}-result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)
    check=command(['pgrep','-x','ps2EntryRunner'])
    print('POST_RELEASE',json.dumps(check),'lease_absent',not LEASE.exists(),flush=True)
    assert not result.get('lease_ownership_error')
    return 0 if result['rc'] in [0,-15] and result.get('release_utc') else 2


if __name__=='__main__':
    sys.exit(main())
