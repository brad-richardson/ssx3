#!/usr/bin/env python3
"""Bound compiler/linker work, keep temporary files and large outputs on SSD."""
import argparse, datetime, json, os, shutil, signal, subprocess, time
from pathlib import Path
E=Path(__file__).resolve().parent
W=Path('/Volumes/Extreme SSD/ps2recomp-spike')
M=1024**2;G=1024**3
def size(p):return sum(q.stat().st_blocks*512 for q in p.rglob('*') if q.is_file())
def main():
    ap=argparse.ArgumentParser();ap.add_argument('label');ap.add_argument('wall',type=int);ap.add_argument('command',nargs=argparse.REMAINDER);a=ap.parse_args()
    assert os.environ.get('COPYFILE_DISABLE')=='1' and a.label.replace('-','').isalnum()
    argv=a.command[1:] if a.command[0]=='--' else a.command
    folder=W/'P1/e14-tooltmp'/a.label;folder.mkdir(parents=True,exist_ok=False)
    owner=dict(label=a.label,evidence=str(E),utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    (folder/'E14-owner.json').write_text(json.dumps(owner))
    env=dict(os.environ);env['TMPDIR']=str(folder)+'/'
    caps=dict(allocated=8*G,allocated_guard=256*M,ssd_floor=2*G,internal_floor=G,wall=a.wall,reserve=15,log=16*M,log_guard=M,poll_s=.25)
    record=dict(**owner,argv=argv,cwd=os.getcwd(),tmpdir=str(folder),caps=caps,free_before=shutil.disk_usage('/private/tmp').free)
    (E/f'{a.label}-bounded-start.json').write_text(json.dumps(record,indent=2)+'\n')
    assert record['free_before']>caps['internal_floor'] and shutil.disk_usage(W).free>caps['ssd_floor']
    log=E/f'{a.label}.log';t0=time.monotonic();p=None;reason=None;last=-10
    with log.open('wb') as out,(E/f'{a.label}-liveness.jsonl').open('w') as live:
        try:
            p=subprocess.Popen(argv,env=env,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
            while p.poll() is None:
                try:allocated=size(folder)
                except FileNotFoundError:allocated=0
                row=dict(elapsed_s=time.monotonic()-t0,allocated=allocated,internal_free=shutil.disk_usage('/private/tmp').free,ssd_free=shutil.disk_usage(W).free,log_bytes=log.stat().st_size)
                if row['elapsed_s']-last>=5:live.write(json.dumps(row)+'\n');live.flush();last=row['elapsed_s']
                if row['allocated']>=caps['allocated']-caps['allocated_guard']:reason='temporary_allocation'
                elif row['internal_free']<=caps['internal_floor']:reason='internal_floor'
                elif row['ssd_free']<=caps['ssd_floor']:reason='ssd_floor'
                elif row['log_bytes']>=caps['log']-caps['log_guard']:reason='log'
                elif row['elapsed_s']>=caps['wall']-caps['reserve']:reason='wall'
                if reason:
                    record['bound']=dict(reason=reason,**row);os.killpg(p.pid,signal.SIGTERM);p.wait(timeout=15);break
                time.sleep(.25)
        finally:
            if p is not None and p.poll() is None:os.killpg(p.pid,signal.SIGTERM);p.wait(timeout=15)
    record.update(rc=p.returncode,elapsed_s=time.monotonic()-t0,free_after=shutil.disk_usage('/private/tmp').free,
                  temporary_logical=sum(q.stat().st_size for q in folder.rglob('*') if q.is_file()),temporary_allocated=size(folder))
    assert json.loads((folder/'E14-owner.json').read_text())==owner
    shutil.rmtree(folder);record['temporary_cleaned']=True
    (E/f'{a.label}-bounded-result.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record,indent=2));assert p.returncode==0 and reason is None
    print('# E14 BOUNDED TOOL TAIL COMPLETE')
if __name__=='__main__':main()
