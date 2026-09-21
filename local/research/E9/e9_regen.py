#!/usr/bin/env python3
"""E9-only bounded regeneration and explicit generated-source mirror install."""
import datetime, hashlib, json, os, shutil, subprocess, sys, time, tomllib
from pathlib import Path
HERE=Path(__file__).resolve().parent; W=Path('/Volumes/Extreme SSD/ps2recomp-spike'); R=W/'PS2Recomp'
TOOL=Path('/Volumes/Extreme SSD/ps2x-i10/host-recomp/ps2xRecomp/ps2_recomp')
OUT=W/'P1/e9-codegen'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert os.environ.get('COPYFILE_DISABLE')=='1'
    phase=sys.argv[1]; assert phase in ['drop','entry']
    record=HERE/f'{phase}-regen.json'; assert not record.exists()
    canonical=R/'games/ssx3/ssx3.toml'; csv=R/'games/ssx3/ssx3-functions.sweep.csv'
    before=canonical.read_text(); cfg=tomllib.loads(before)
    for p in [canonical,W/'P1/ssx3.toml']:
        assert not any('426230' in x.lower() for x in tomllib.loads(p.read_text())['general']['stubs'])
    assert ('sub_002C5140,0x2c5140,0x2c5168,0x28' in csv.read_text())==(phase=='entry')
    used=before.replace(cfg['general']['output'],str(OUT)+'/')
    config=HERE/f'{phase}-used.toml'; config.write_text(used)
    assert sha(TOOL)=='511791795c16649e69706725c412408acc8d35fda68c4d83a3229eae6bda0763'
    OUT.mkdir(exist_ok=True)
    caps=dict(wall_s=1200,log_bytes=16*1024**2,output_allocated=12*1024**3,ssd_free_floor=2*1024**3)
    rec=dict(phase=phase,argv=[str(TOOL),str(config)],cwd=str(R),caps=caps,tool_sha=sha(TOOL),config_sha=sha(config),csv_sha=sha(csv),start_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),free_before=shutil.disk_usage(W).free)
    start=time.monotonic(); log=HERE/f'{phase}-regen.log'
    with log.open('wb') as f:
        p=subprocess.Popen(rec['argv'],cwd=R,stdout=f,stderr=subprocess.STDOUT)
        while p.poll() is None:
            time.sleep(1)
            allocated=sum(q.stat().st_blocks*512 for q in OUT.iterdir() if q.is_file())
            if time.monotonic()-start>caps['wall_s'] or log.stat().st_size>caps['log_bytes'] or allocated>caps['output_allocated'] or shutil.disk_usage(W).free<caps['ssd_free_floor']:
                p.terminate();p.wait(timeout=15);rec['cap_bound']=True;break
    rec.update(rc=p.returncode,wall_s=time.monotonic()-start,free_after=shutil.disk_usage(W).free)
    record.write_text(json.dumps(rec,indent=2)+'\n'); assert p.returncode==0 and not rec.get('cap_bound')
    sources=sorted(q for q in OUT.iterdir() if q.suffix in ['.cpp','.h'] and not q.name.startswith('._'))
    rows=[]
    for q in sources:
        dst=R/'ps2xRuntime'/('src/runner' if q.suffix=='.cpp' else 'include')/q.name
        digest=sha(q); changed=not dst.exists() or sha(dst)!=digest
        if changed:shutil.copyfile(q,dst)
        rows.append(dict(name=q.name,bytes=q.stat().st_size,allocated=q.stat().st_blocks*512,sha256=digest,mirror_changed=changed))
    old=sorted(q.name for q in (R/'ps2xRuntime/src/runner').glob('*.cpp') if not q.name.startswith('._') and not (OUT/q.name).exists())
    # Unexpected leftovers need disposition; never silently keep or delete them.
    rec.update(generated_files=len(rows),generated_allocated=sum(x['allocated'] for x in rows),mirror_changed=sum(x['mirror_changed'] for x in rows),mirror_leftovers=old)
    (HERE/f'{phase}-output.json').write_text(json.dumps(rows,indent=2)+'\n')
    record.write_text(json.dumps(rec,indent=2)+'\n'); print(json.dumps(rec,indent=2))
    assert not old,old
if __name__=='__main__':main()
