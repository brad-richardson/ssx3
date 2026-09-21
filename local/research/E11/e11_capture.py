#!/usr/bin/env python3
"""E11 progression capture driver. Explicit preflight, caps, owned lease cleanup."""
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
from e11_frame import read_png, fnv32
EVIDENCE = REPO / 'local/research/E11'
W = Path('/Volumes/Extreme SSD/ps2recomp-spike')
FORK = W / 'PS2Recomp'
RUN = W / 'P1/run'
BIN = Path('/tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner')
TEST = Path('/tmp/p1-link/runtime/ps2xTest/ps2x_tests')
ELF = W / 'P1/cd/SLUS_207.72'
LEASE = Path('/tmp/ssx3-p-lane-lease')
WAITS = RUN / 'e11-waits.log'
ELF_SHA = '1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc'
DISPLAY = [0x12000000, 0x12000020, 0x12000070, 0x12000080,
           0x12000090, 0x120000a0, 0x120000e0]
OFFSETS = [0x5a78, 0x5a7c, 0x5a84, 0x5a88, 0x5a74, 0xf44, 0x59e8]
MIB = 1024 * 1024
ALLOCATED_CAPS=dict(boot_log=256*MIB,trace=96*MIB,function_log=1024*MIB,e4_dir=64*MIB,park_dir=128*MIB,frames_dir=64*MIB,e7_dir=32*MIB,aggregate=1536*MIB)
CAPS = dict(wall_s=600, terminate_reserve_s=15, progress_lines=1000000,
            boot_log=256*MIB, trace=96*MIB, function_log=1024*MIB,
            e4_dir=12*MIB, park_dir=32*MIB, frames_dir=32*MIB,
            e7_dir=8*MIB,
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
        append_wait(f'{label.upper()} STOP {utc()} owner={LEASE.read_text().strip()!r}; E11 forbids lease wait')
        raise RuntimeError('Lease occupied; E11 tables and stops without waiting')
    record['runner_check'] = command(['pgrep', '-x', 'ps2EntryRunner'])
    assert record['runner_check']['rc'] == 1, record['runner_check']
    record['fork_head'] = command(['git', '-C', str(FORK), 'rev-parse', 'HEAD'])
    record['fork_status'] = command(['git', '-C', str(FORK), 'status', '--short'])
    manifest_path=EVIDENCE/f'{label}-build.json'
    assert manifest_path.exists(), 'fresh E11 build manifest required'
    build=json.loads(manifest_path.read_text())
    entry=json.loads((EVIDENCE/'entry-preflight.json').read_text())
    assert entry['suite_rc']==entry['binding_rc']==0 and entry['query_cases']==4
    record['build_manifest']=build
    assert record['fork_head']['stdout'].strip() == build['fork_head']
    assert record['fork_status']['stdout']==build['fork_status'], record['fork_status']
    record['files'] = []
    for path, size, expected in [(BIN,build['bin_size'],build['bin_sha']),(TEST,build['test_size'],build['test_sha']),
                                  (W/'SSX 3 (USA).iso',3005415424,None),
                                  (ELF,3890784,ELF_SHA),(W/'P1/SLUS_207.72',3890784,ELF_SHA)]:
        item = dict(path=str(path), bytes=path.stat().st_size)
        assert item['bytes'] == size, item
        if expected:
            item['sha256'] = sha(path)
            assert item['sha256'] == expected, item
        record['files'].append(item)
    record['space'] = command(['df', '-h', str(W), '/private/tmp'])
    assert shutil.disk_usage(W).free > 2*1024*MIB
    assert shutil.disk_usage('/private/tmp').free > 1024*MIB
    record['wait_tails'] = {}
    for path in sorted(RUN.glob('*-waits.log'), key=lambda p:p.stat().st_mtime, reverse=True):
        if path.name.startswith('._'):
            continue
        record['wait_tails'][path.name] = path.read_text().splitlines()[-4:]
        if len(record['wait_tails']) >= 8:
            break
    record['sidecars_outside_git'] = command(['rg','--files','--hidden','-g','._*','-g','!.git'],cwd=FORK)
    record['aligner'] = command([sys.executable,'-B','tools/trace_align.py','--selftest'])
    (EVIDENCE/f'{label}-aligner.txt').write_text(record['aligner']['stdout']+record['aligner']['stderr'])
    assert record['aligner']['rc']==0 and 'selftest: ALL PASS' in record['aligner']['stdout']
    suite = command([str(TEST)],cwd=FORK)
    (EVIDENCE/f'{label}-suite.txt').write_text(suite['stdout']+suite['stderr'])
    record['suite'] = dict(rc=suite['rc'], tail=suite['stdout'].splitlines()[-7:])
    assert suite['rc']==0 and f'Total Tests: {build["test_count"]}' in suite['stdout'] and 'Failed: 0' in suite['stdout']
    # Recheck immediately before the atomic claim, after tests.
    record['runner_recheck'] = command(['pgrep','-x','ps2EntryRunner'])
    assert record['runner_recheck']['rc']==1 and not LEASE.exists()
    record['preflight_complete_utc'] = utc()
    (EVIDENCE/f'{label}-preflight.json').write_text(json.dumps(record,indent=2)+'\n')
    return record


def size(path, allocated=False):
    if not path.exists():
        return 0
    if path.is_file():
        return path.stat().st_blocks*512 if allocated else path.stat().st_size
    return sum((p.stat().st_blocks*512 if allocated else p.stat().st_size) for p in path.rglob('*') if p.is_file())


def sample_host(folder,elapsed):
    """Preserve one canonical PNG per content hash, only with a matching sidecar."""
    meta=folder/'upload-latest.txt';png=folder/'upload-latest.png'
    if not meta.exists() or not png.exists():return
    try:
        before=meta.read_text();data=png.read_bytes();after=meta.read_text()
        if before!=after:return
        class Buffer:
            def read_bytes(self):return data
        w,h,rgba=read_png(Buffer())
        fields=dict(part.split('=',1) for part in before.split())
        if fnv32(rgba)!=int(fields['fnv1a'],16):return
        digest=hashlib.sha256(data).hexdigest();name=f'survey-{digest}.png'
        dest=folder/name
        if not dest.exists():dest.write_bytes(data)
        with (folder/'survey-index.jsonl').open('a') as f:
            f.write(json.dumps(dict(elapsed_s=elapsed,png=name,sha256=digest,metadata=fields))+'\n')
    except (OSError,AssertionError,ValueError,KeyError):
        return # Concurrent rewrite: the next sample will retry; no partial artifact.


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase',choices=['a'])
    parser.add_argument('--s',type=lambda x:int(x,0),default=0x61ba60)
    parser.add_argument('--arm',type=int,default=600)
    parser.add_argument('--report-all',action='store_true',help='Retain each missing-target branch receipt')
    parser.add_argument('--wall',type=int,default=90)
    args=parser.parse_args()
    assert 20 <= args.wall <= 600
    CAPS['wall_s']=args.wall
    def interrupted(signum, frame):
        raise KeyboardInterrupt(f'capture driver signal {signum}')
    signal.signal(signal.SIGTERM, interrupted)
    assert os.environ.get('COPYFILE_DISABLE')=='1'
    assert args.s is not None and args.arm>0
    assert not list(EVIDENCE.glob('e11?-result.json')), 'E11 permits only one boot'
    label='e11'+args.phase
    paths=dict(boot_log=RUN/f'boot-{label}-1.log',trace=RUN/f'syscalls-{label}-on.txt',
               function_log=RUN/'ps2_log.txt',e4_dir=RUN/f'{label}-1',
               park_dir=RUN/f'park-{label}-1',frames_dir=RUN/f'frames-{label}-1')
    if args.s is not None:
        paths['e7_dir']=RUN/f'{label}-join'
    kept_function=RUN/f'ps2_log-{label}-1.txt'
    assert not kept_function.exists()
    for key,path in paths.items():
        if key!='function_log':
            assert not path.exists(), f'Refuse to overwrite {path}'
    watches=[0x4a289c]+DISPLAY
    if args.s is not None:
        watches += [args.s+off for off in OFFSETS]
        watches += [0x10005000,0x1000a000,0x1000a010,0x1000a020]
    watches += [0xb851a0,0xb851a4,0xb851ac,0xb851e0,0xb84e84,0xb84d88,0x4a3938,0x4a393c,0x4a3940,0x4a3944]
    preflight(label)
    env=dict(os.environ)
    # Clear inherited diagnostic switches, then recreate E5's lean environment.
    inherited={k:v for k,v in env.items() if k.startswith('PS2X_')}
    for key in inherited:
        del env[key]
    env.update(PS2X_CD_IMAGE=str(W/'SSX 3 (USA).iso'),PS2X_DIAG_PERIOD_MS='5000',
               PS2X_DIAG_PARK='1',PS2X_DIAG_PARK_DIR=str(paths['park_dir']),
               PS2X_TRACE_SYSCALLS=str(paths['trace']),PS2X_TRACE_SYSCALLS_PC='1',
               PS2X_FRAME_DUMP_DIR=str(paths['frames_dir']),PS2X_E4_ARM_TICK=str(args.arm),
               PS2X_E4_FREEZE_TICK=str(args.arm+1),PS2X_E4_DIR=str(paths['e4_dir']),
               PS2X_DIAG_WATCH=','.join(hex(x) for x in watches))
    if args.s is not None:
        env['PS2X_E7_DIR']=str(paths['e7_dir'])
    if args.report_all:
        env['PS2X_DIAG_REPORT_ALL']='1'
    config=dict(label=label,argv=['stdbuf','-o0','-e0',str(BIN),str(ELF)],cwd=str(RUN),
                caps=CAPS,allocated_caps=ALLOCATED_CAPS,watch_addresses=[hex(x) for x in watches],s=args.s,
                env={k:v for k,v in env.items() if k.startswith('PS2X_')},
                removed_inherited_keys=sorted(inherited),paths={k:str(v) for k,v in paths.items()})
    (EVIDENCE/f'{label}-config.json').write_text(json.dumps(config,indent=2)+'\n')
    print(json.dumps(config),flush=True)
    for key,path in paths.items():
        if key.endswith('_dir'):
            path.mkdir()
    token=f'{label.upper()}\npid={os.getpid()} utc={utc()}\n'
    with LEASE.open('x') as f:
        f.write(token)
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
            p=subprocess.Popen(config['argv'],cwd=RUN,env=env,stdout=log,stderr=subprocess.STDOUT)
            result['pid']=p.pid
            result['boot_utc']=utc()
            trace_pos=0;lines=0;span_at=None;last_emit=-5;last_frame=-30
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
                sample=dict(elapsed_s=round(elapsed,3),trace_lines=lines,bytes=counts,allocated=allocated,ssd_free=shutil.disk_usage(W).free,ssd_free_delta=free_before-shutil.disk_usage(W).free)
                if elapsed-last_emit>=5:
                    emit(sample);last_emit=elapsed
                if elapsed-last_frame>=30:
                    sample_host(paths['frames_dir'],elapsed);last_frame=elapsed
                bound=next((k+'_bytes' for k,n in counts.items() if n>=CAPS[k]-(min(8*MIB,CAPS[k]//4) if args.report_all or k in ['function_log','aggregate'] else 0)),None)
                if bound is None:
                    bound=next((k+'_allocated_bytes' for k,n in allocated.items() if n>=ALLOCATED_CAPS[k]-8*MIB),None)
                if bound is None and sample['ssd_free']<2*1024*MIB: bound='ssd_free_floor'
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
            result['process_end_utc']=utc()
            result['elapsed_s']=time.monotonic()-t0
            if result['bound'] is None: result['bound']='exited'
    finally:
        if p is not None and p.poll() is None:
            p.terminate()
            try: p.wait(timeout=15)
            except subprocess.TimeoutExpired: p.kill();p.wait()
        # Preserve the closed shared-path raw in O(1) before relinquishing ownership.
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
