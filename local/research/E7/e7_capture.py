#!/usr/bin/env python3
"""E7 bounded capture driver. Explicit preflight, caps, owned lease cleanup."""
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
EVIDENCE = REPO / 'local/research/E7'
W = Path('/Volumes/Extreme SSD/ps2recomp-spike')
FORK = W / 'PS2Recomp'
RUN = W / 'P1/run'
BIN = Path('/tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner')
TEST = Path('/tmp/p1-link/runtime/ps2xTest/ps2x_tests')
ELF = W / 'P1/cd/SLUS_207.72'
LEASE = Path('/tmp/ssx3-p-lane-lease')
WAITS = RUN / 'e7-waits.log'
BIN_SHA = 'e21ab7077496cdb312cdefa147da4fb6afadd52dba1f6f0cee709d75bb026330'
TEST_SHA = 'c035e12ef4e38a0880188b37852b764d2262d9baf9491d538995465ca853b968'
ELF_SHA = '1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc'
DISPLAY = [0x12000000, 0x12000020, 0x12000070, 0x12000080,
           0x12000090, 0x120000a0, 0x120000e0]
OFFSETS = [0x5a78, 0x5a7c, 0x5a84, 0x5a88, 0x5a74, 0xf44, 0x59e8]
MIB = 1024 * 1024
CAPS = dict(wall_s=600, terminate_reserve_s=15, progress_lines=1000000,
            boot_log=800*MIB, trace=64*MIB, function_log=512*MIB,
            e4_dir=12*MIB, park_dir=32*MIB, frames_dir=32*MIB,
            e7_dir=8*MIB,
            aggregate=1024*MIB, poll_s=0.25, grace_s=10)


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
    record = dict(label=label, utc=utc(), caps=CAPS, lease_absent=not LEASE.exists())
    if LEASE.exists():
        append_wait(f'{label.upper()} WAIT {utc()} owner={LEASE.read_text().strip()!r}; retry >=300s')
        raise RuntimeError('Lease occupied; logged WAIT; retry no sooner than five minutes')
    record['runner_check'] = command(['pgrep', '-x', 'ps2EntryRunner'])
    assert record['runner_check']['rc'] == 1, record['runner_check']
    record['fork_head'] = command(['git', '-C', str(FORK), 'rev-parse', 'HEAD'])
    record['fork_status'] = command(['git', '-C', str(FORK), 'status', '--short'])
    manifest_path=EVIDENCE/f'{label}-build.json'
    build=json.loads(manifest_path.read_text()) if manifest_path.exists() else dict(
        fork_head='a13b66a540514544007c121e7220b02846e1275d',bin_sha=BIN_SHA,bin_size=160817056,
        test_sha=TEST_SHA,test_size=5598280,test_count=448)
    record['build_manifest']=build
    assert record['fork_head']['stdout'].strip() == build['fork_head']
    assert record['fork_status']['stdout'].splitlines() == [' M ps2xRuntime/src/runner/register_functions.cpp']
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


def size(path):
    if not path.exists():
        return 0
    if path.is_file():
        return path.stat().st_size
    return sum(p.stat().st_size for p in path.rglob('*') if p.is_file())


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase',choices=['a','b','c','d'])
    parser.add_argument('--s',type=lambda x:int(x,0))
    args=parser.parse_args()
    def interrupted(signum, frame):
        raise KeyboardInterrupt(f'capture driver signal {signum}')
    signal.signal(signal.SIGTERM, interrupted)
    assert os.environ.get('COPYFILE_DISABLE')=='1'
    assert (args.phase=='a' and args.s is None) or (args.phase!='a' and args.s is not None)
    label='e7'+args.phase
    paths=dict(boot_log=RUN/f'boot-{label}-1.log',trace=RUN/f'syscalls-{label}-on.txt',
               function_log=RUN/'ps2_log.txt',e4_dir=RUN/f'{label}-1',
               park_dir=RUN/f'park-{label}-1',frames_dir=RUN/f'frames-{label}-1')
    if args.phase!='a':
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
    preflight(label)
    env=dict(os.environ)
    # Clear inherited diagnostic switches, then recreate E5's lean environment.
    inherited={k:v for k,v in env.items() if k.startswith('PS2X_')}
    for key in inherited:
        del env[key]
    env.update(PS2X_CD_IMAGE=str(W/'SSX 3 (USA).iso'),PS2X_DIAG_PERIOD_MS='5000',
               PS2X_DIAG_PARK='1',PS2X_DIAG_PARK_DIR=str(paths['park_dir']),
               PS2X_TRACE_SYSCALLS=str(paths['trace']),PS2X_TRACE_SYSCALLS_PC='1',
               PS2X_FRAME_DUMP_DIR=str(paths['frames_dir']),PS2X_E4_ARM_TICK='600',
               PS2X_E4_FREEZE_TICK='601',PS2X_E4_DIR=str(paths['e4_dir']),
               PS2X_DIAG_WATCH=','.join(hex(x) for x in watches))
    if args.phase!='a':
        env['PS2X_E7_DIR']=str(paths['e7_dir'])
    config=dict(label=label,argv=['stdbuf','-o0','-e0',str(BIN),str(ELF)],cwd=str(RUN),
                caps=CAPS,watch_addresses=[hex(x) for x in watches],s=args.s,
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
    t0=time.monotonic()
    try:
        with (EVIDENCE/f'{label}-liveness.txt').open('w') as live, paths['boot_log'].open('wb') as log:
            def emit(obj):
                line=json.dumps(obj,sort_keys=True)
                live.write(line+'\n');live.flush();print(line,flush=True)
            p=subprocess.Popen(config['argv'],cwd=RUN,env=env,stdout=log,stderr=subprocess.STDOUT)
            result['pid']=p.pid
            result['boot_utc']=utc()
            trace_pos=0;lines=0;span_at=None;last_emit=-5
            while p.poll() is None:
                elapsed=time.monotonic()-t0
                counts={k:size(path) for k,path in paths.items()}
                counts['aggregate']=sum(counts.values())
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
                sample=dict(elapsed_s=round(elapsed,3),trace_lines=lines,bytes=counts)
                if elapsed-last_emit>=5:
                    emit(sample);last_emit=elapsed
                bound=next((k+'_bytes' for k,n in counts.items() if n>=CAPS[k]),None)
                if bound is None and lines>=CAPS['progress_lines']: bound='progress'
                if bound is None and elapsed>=CAPS['wall_s']-CAPS['terminate_reserve_s']: bound='wall'
                if bound is None and span_at is not None and elapsed-span_at>=CAPS['grace_s']: bound='span'
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
    return 0 if result['bound']=='span' else 2


if __name__=='__main__':
    sys.exit(main())
