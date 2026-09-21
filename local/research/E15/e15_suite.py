#!/usr/bin/env python3
"""Run suite with small APFS test data, charged to the existing evidence reservation."""
import datetime,json,os,shutil,signal,subprocess,sys,time
from pathlib import Path
from e15_bounded import E,W,M,size,sample,resource_bound
def run(label):
    folder=E/('.suite-tmp-'+label);assert not folder.exists()
    before=sample();assert not resource_bound(before)
    # 32 MiB is part of the declared 128 MiB evidence/test-data allocation,
    # not additional admission or a generated-code scratch exception.
    record=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),before=before,temporary_cap=32*M,temporary_guard=4*M,internal_reservation_increase=0,log_cap=16*M,wall_cap=60,peak_allocated=0)
    folder.mkdir();(folder/'E15-owner.json').write_text(json.dumps(dict(task='E15',label=label)))
    env={k:v for k,v in os.environ.items() if not k.startswith('PS2X_')};env['TMPDIR']=str(folder)+'/'
    log=E/f'{label}-suite.txt';bound=None;t=time.monotonic()
    with log.open('wb') as output:
        p=subprocess.Popen(['/tmp/p1-link/runtime/ps2xTest/ps2x_tests'],cwd=W/'PS2Recomp',env=env,stdout=output,stderr=subprocess.STDOUT,start_new_session=True)
        while p.poll() is None:
            n=size(folder);record['peak_allocated']=max(n,record['peak_allocated'])
            if n>=28*M:bound='test_data'
            elif log.stat().st_size>=15*M:bound='test_log'
            elif time.monotonic()-t>=45:bound='test_wall'
            if bound:os.killpg(p.pid,signal.SIGTERM);p.wait(timeout=15);break
            time.sleep(.01)
    record.update(rc=p.returncode,elapsed_s=time.monotonic()-t,bound=bound,remaining_allocated=size(folder),remaining=[str(q.relative_to(folder)) for q in folder.rglob('*')])
    assert json.loads((folder/'E15-owner.json').read_text())==dict(task='E15',label=label)
    shutil.rmtree(folder);record['cleaned']=True
    (E/f'{label}-suite-environment.json').write_text(json.dumps(record,indent=2)+'\n')
    text=log.read_text();assert bound is None
    return p.returncode,text,record
if __name__=='__main__':
    rc,text,record=run(sys.argv[1]);print(json.dumps(record,indent=2));print('\n'.join(x for x in text.splitlines() if 'Total Tests:' in x or 'Passed:' in x or 'Failed:' in x));sys.exit(rc)
