"""Bounded process groups, hard stdout cap, allocated-byte admission; no reclaim."""
import argparse, selectors, signal, subprocess, time
from e28_common import *

def main():
    ap=argparse.ArgumentParser();ap.add_argument('label');ap.add_argument('wall',type=int);ap.add_argument('command',nargs=argparse.REMAINDER);a=ap.parse_args()
    assert os.environ.get('COPYFILE_DISABLE')=='1'
    argv=a.command[1:] if a.command[0]=='--' else a.command
    folder=P/'e28-tooltmp'/a.label
    record=dict(label=a.label,utc=utc(),argv=argv,cwd=os.getcwd(),tmpdir=str(folder),before=sample(),caps=dict(wall=a.wall,wall_reserve=15,stdout=16*M,stdout_reserve=M,tmp=8*G,tmp_reserve=512*M,fixtures=2*G,fixture_reserve=64*M,poll_s=.25))
    save(a.label+'-bounded-start.json',record);admission(record['before'])
    folder.mkdir(parents=True,exist_ok=False)
    (folder/'E28-owner.json').write_text(json.dumps(dict(task='E28',label=a.label,created=record['utc'])))
    env=dict(os.environ,TMPDIR=str(folder)+'/',COPYFILE_DISABLE='1',PYTHONDONTWRITEBYTECODE='1',CMAKE_BUILD_PARALLEL_LEVEL='2')
    t=time.monotonic();p=None;reason=None;last=-10;next_sample=0;seen=0;kept=0
    with (E/(a.label+'.log')).open('wb') as out,(E/(a.label+'-liveness.jsonl')).open('w') as live:
        try:
            p=subprocess.Popen(argv,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,start_new_session=True)
            sel=selectors.DefaultSelector();sel.register(p.stdout,selectors.EVENT_READ)
            while p.poll() is None or sel.get_map():
                for key,_ in sel.select(timeout=.05):
                    chunk=os.read(key.fileobj.fileno(),65536)
                    if not chunk:sel.unregister(key.fileobj);continue
                    seen+=len(chunk);remaining=max(0,15*M-kept);out.write(chunk[:remaining]);kept+=min(len(chunk),remaining);out.flush()
                    if seen>=15*M:reason=reason or 'stdout'
                elapsed=time.monotonic()-t
                if elapsed>=next_sample:
                    row=dict(elapsed_s=elapsed,tmp_allocated=size(folder),fixture_allocated=size(P/'e28-fixtures'),stdout_seen=seen,stdout_kept=kept,**sample())
                    next_sample=elapsed+.25
                    if elapsed-last>=5:live.write(json.dumps(row)+'\n');live.flush();last=elapsed
                    reason=reason or bound(row)
                    if row['tmp_allocated']>=8*G-512*M:reason=reason or 'tmp'
                    if row['fixture_allocated']>=2*G-64*M:reason=reason or 'fixtures'
                    if elapsed>=a.wall-15:reason=reason or 'wall'
                if reason and p.poll() is None:
                    record['binding_cap']=dict(reason=reason,**row)
                    os.killpg(p.pid,signal.SIGTERM)
                    try:p.wait(timeout=10)
                    except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait(timeout=5)
        finally:
            if p and p.poll() is None:os.killpg(p.pid,signal.SIGTERM);p.wait(timeout=15)
    record.update(rc=p.returncode,elapsed_s=time.monotonic()-t,bound=reason,after=sample(),stdout_seen=seen,stdout_kept=kept,stdout_truncated=seen!=kept,temporary_allocated=size(folder))
    # Keep the owned temporary directory for explicit retention/accounting; no deletion.
    save(a.label+'-bounded-result.json',record)
    print(json.dumps(record,indent=2));print('# E28 BOUNDED TOOL TAIL COMPLETE')
    return 0 if p.returncode==0 and reason is None else 1
if __name__=='__main__':raise SystemExit(main())
