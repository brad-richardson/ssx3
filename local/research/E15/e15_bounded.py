#!/usr/bin/env python3
"""E15 fixed-budget monitor. No reclaim; temporary work exclusively on SSD."""
import argparse,datetime,json,os,shutil,signal,subprocess,time,selectors
from pathlib import Path
E=Path(__file__).resolve().parent
W=Path('/Volumes/Extreme SSD/ps2recomp-spike')
B=Path('/tmp/p1-link/runtime');M=1024**2;G=1024**3
BASE=json.loads((E/'internal-artifact-baseline.json').read_text())
def files(path):
    for p in path.rglob('*'):
        try:
            if p.is_file():yield p,p.stat()
        except FileNotFoundError:pass
def size(p):return sum(s.st_blocks*512 for _,s in files(p)) if p.exists() else 0
def growth():return sum(max(0,s.st_blocks*512-BASE.get(str(p),{}).get('allocated',0)) for root in (B,E) for p,s in files(root))
def ssd_usage():
    paths=list((W/'P1').glob('e15-*'))+list((W/'P1/run').glob('*e15*'))
    total=0
    for p in paths:
        if p.name.startswith('._'):continue
        try:total+=size(p) if p.is_dir() else p.stat().st_blocks*512
        except FileNotFoundError:pass # a closed capture can move between list/stat
    return total
def sample():return dict(internal_free=shutil.disk_usage('/private/tmp').free,internal_growth=growth(),ssd_free=shutil.disk_usage(W).free,ssd_allocated=ssd_usage())
def resource_bound(row):
    if row['internal_growth']>=512*M-64*M:return 'internal_growth'
    if row['internal_free']<=G+256*M:return 'internal_floor'
    if row['ssd_free']<=2*G+256*M:return 'ssd_floor'
    if row['ssd_allocated']>=6*G-256*M:return 'ssd_total'
def main():
    ap=argparse.ArgumentParser();ap.add_argument('label');ap.add_argument('wall',type=int);ap.add_argument('command',nargs=argparse.REMAINDER);a=ap.parse_args()
    assert os.environ.get('COPYFILE_DISABLE')=='1' and a.label.replace('-','').isalnum()
    argv=a.command[1:] if a.command[0]=='--' else a.command
    folder=W/'P1/e15-tooltmp'/a.label
    owner=dict(label=a.label,evidence=str(E),utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    caps=dict(tmp=4*G,tmp_guard=256*M,fixture=512*M,log=16*M,log_guard=M,wall=a.wall,wall_guard=15,internal_growth=512*M,internal_growth_guard=64*M,internal_floor=G,internal_guard=256*M,ssd_total=6*G,ssd_floor=2*G,ssd_guard=256*M,poll_s=.25)
    record=dict(**owner,argv=argv,cwd=os.getcwd(),tmpdir=str(folder),caps=caps,before=sample())
    (E/f'{a.label}-bounded-start.json').write_text(json.dumps(record,indent=2)+'\n')
    assert not resource_bound(record['before']),record
    assert record['before']['internal_free']>=G+256*M+max(0,512*M-record['before']['internal_growth']),record
    assert record['before']['ssd_free']>=2*G+256*M+max(0,6*G-record['before']['ssd_allocated']),record
    folder.mkdir(parents=True,exist_ok=False);(folder/'E15-owner.json').write_text(json.dumps(owner))
    env=dict(os.environ,TMPDIR=str(folder)+'/')
    log=E/f'{a.label}.log';t0=time.monotonic();p=None;reason=None;last=-10
    with log.open('wb') as out,(E/f'{a.label}-liveness.jsonl').open('w') as live:
        try:
            p=subprocess.Popen(argv,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,start_new_session=True)
            selector=selectors.DefaultSelector();selector.register(p.stdout,selectors.EVENT_READ)
            while p.poll() is None:
                for key,_ in selector.select(timeout=.05):
                    chunk=os.read(key.fileobj.fileno(),65536)
                    if chunk:
                        remaining=caps['log']-caps['log_guard']-out.tell()
                        out.write(chunk[:remaining]);out.flush()
                        if len(chunk)>=remaining:reason='log'
                    else:selector.unregister(key.fileobj)
                row=dict(elapsed_s=time.monotonic()-t0,tmp_allocated=size(folder),fixture_allocated=size(W/'P1/e15-binding-tests'),log_bytes=log.stat().st_size,**sample())
                if row['elapsed_s']-last>=5:live.write(json.dumps(row)+'\n');live.flush();last=row['elapsed_s']
                reason=reason or resource_bound(row)
                if reason is None:
                    if row['tmp_allocated']>=caps['tmp']-caps['tmp_guard']:reason='tmp'
                    elif row['fixture_allocated']>=caps['fixture']-8*M:reason='fixture'
                    elif row['log_bytes']>=caps['log']-caps['log_guard']:reason='log'
                    elif row['elapsed_s']>=caps['wall']-caps['wall_guard']:reason='wall'
                if reason:
                    record['bound']=dict(reason=reason,**row);os.killpg(p.pid,signal.SIGTERM);p.wait(timeout=15);break
                if not selector.get_map():time.sleep(.05)
            if reason is None:
                while chunk:=p.stdout.read(65536):
                    remaining=caps['log']-caps['log_guard']-out.tell()
                    out.write(chunk[:remaining]);out.flush()
                    if len(chunk)>=remaining:reason='log-after-exit';break
        finally:
            if p is not None and p.poll() is None:os.killpg(p.pid,signal.SIGTERM);p.wait(timeout=15)
    record.update(rc=p.returncode,elapsed_s=time.monotonic()-t0,after=sample(),temporary_allocated=size(folder))
    assert json.loads((folder/'E15-owner.json').read_text())==owner
    shutil.rmtree(folder);record['temporary_cleaned']=True
    (E/f'{a.label}-bounded-result.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record,indent=2));assert p.returncode==0 and reason is None
    print('# E15 BOUNDED TOOL TAIL COMPLETE')
if __name__=='__main__':main()
