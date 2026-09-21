#!/usr/bin/env python3
"""E11-only APFS generation with fresh admission, bounds and complete manifests."""
import datetime,gzip,hashlib,json,os,shutil,subprocess,sys,time,tomllib
from pathlib import Path
E=Path(__file__).resolve().parent;W=Path('/Volumes/Extreme SSD/ps2recomp-spike');R=W/'PS2Recomp'
OUT=Path('/tmp/ssx3-e11-query-codegen');TOOL=Path('/Volumes/Extreme SSD/ps2x-i10/host-recomp/ps2xRecomp/ps2_recomp')
MIB=1024**2;GIB=1024**3
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def cmd(a):
    p=subprocess.run(a,capture_output=True,text=True);return dict(argv=a,rc=p.returncode,stdout=p.stdout,stderr=p.stderr)
def main():
    assert os.environ.get('COPYFILE_DISABLE')=='1'
    phase=sys.argv[1];assert phase=='entry','E11 authorizes query generation only';assert not (E/f'{phase}-generation.json').exists()
    caps=dict(logical=GIB,allocated=GIB+256*MIB,output_guard=128*MIB,free_floor=2*GIB,free_guard=256*MIB,wall_s=1200,wall_guard_s=15,log=16*MIB,log_guard=MIB,poll_s=.25)
    rec=dict(phase=phase,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),caps=caps,df_before=cmd(['df','-h',str(W),'/private/tmp']),free_before=shutil.disk_usage('/private/tmp').free)
    (E/'entry-initial-admission.json').write_text(json.dumps(rec,indent=2)+'\n')
    assert rec['free_before']>=GIB+caps['free_floor']+caps['free_guard'],rec
    canonical=R/'games/ssx3/ssx3.toml';csv=R/'games/ssx3/ssx3-functions.sweep.csv';elf=W/'P1/SLUS_207.72'
    for p in [canonical,W/'P1/ssx3.toml']:
        assert not any('426230' in s.lower() for s in tomllib.loads(p.read_text())['general']['stubs'])
    assert sha(csv)=='c17db90b72db490772a649eb64b91487d54d1602b258be2e3205e2e7b039c6aa'
    assert csv.read_text().count('sub_002C5140,0x2c5140,0x2c5168,0x28')==1
    assert sha(elf)=='1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc'
    assert sha(TOOL)=='511791795c16649e69706725c412408acc8d35fda68c4d83a3229eae6bda0763'
    rec['source_diff']=cmd(['git','-C',str(R),'diff','b6252bb..HEAD','--','ps2xRecomp','ps2xAnalyzer'])
    assert rec['source_diff']['rc']==0 and not rec['source_diff']['stdout']
    OUT.mkdir(exist_ok=False);(OUT/'E11-owner.json').write_text(json.dumps(dict(evidence=str(E),pid=os.getpid(),utc=rec['utc'])))
    text=canonical.read_text();cfg=tomllib.loads(text);used=text.replace(cfg['general']['output'],str(OUT)+'/')
    conf=E/f'{phase}-used.toml';conf.write_text(used)
    check=tomllib.loads(used);check['general']['output']=cfg['general']['output'];assert check==cfg
    rec.update(argv=[str(TOOL),str(conf)],cwd=str(R),tool_sha=sha(TOOL),elf_sha=sha(elf),csv_sha=sha(csv),config_sha=sha(conf),canonical_sha=sha(canonical))
    (E/f'{phase}-admission.json').write_text(json.dumps(rec,indent=2)+'\n')
    log=E/f'{phase}-generation.log';t0=time.monotonic();last=-10;p=None;reason=None
    with log.open('wb') as f,(E/f'{phase}-generation-liveness.jsonl').open('w') as live:
        try:
            immediate=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),free=shutil.disk_usage(OUT).free,required=GIB+caps['free_floor']+caps['free_guard'])
            (E/'admission-at-spawn.json').write_text(json.dumps(immediate,indent=2)+'\n')
            assert immediate['free']>=immediate['required'],'Stop: immediately-before-spawn admission unmet'
            p=subprocess.Popen(rec['argv'],cwd=R,stdout=f,stderr=subprocess.STDOUT)
            while p.poll() is None:
                elapsed=time.monotonic()-t0;files=[q.stat() for q in OUT.iterdir() if q.is_file()]
                sample=dict(wall_s=elapsed,files=len(files),logical=sum(s.st_size for s in files),allocated=sum(s.st_blocks*512 for s in files),free=shutil.disk_usage(OUT).free,log_bytes=log.stat().st_size)
                if elapsed-last>=5:live.write(json.dumps(sample)+'\n');live.flush();last=elapsed
                reason=next((k for k in ['logical','allocated'] if sample[k]>=caps[k]-caps['output_guard']),None)
                if reason is None and sample['free']<=caps['free_floor']+caps['free_guard']:reason='free_floor_guard'
                if reason is None and elapsed>=caps['wall_s']-caps['wall_guard_s']:reason='wall_guard'
                if reason is None and sample['log_bytes']>=caps['log']-caps['log_guard']:reason='log_guard'
                if reason:
                    rec['bound']=dict(reason=reason,**sample);p.terminate();p.wait(timeout=15);break
                time.sleep(caps['poll_s'])
        finally:
            if p is not None and p.poll() is None:p.terminate();p.wait(timeout=15)
    rec.update(rc=p.returncode,wall_s=time.monotonic()-t0,free_after=shutil.disk_usage(OUT).free,df_after=cmd(['df','-h',str(W),'/private/tmp']))
    rows=[]
    for q in sorted(OUT.iterdir()):
        if q.is_file():
            s=q.stat();rows.append(dict(name=q.name,bytes=s.st_size,allocated=s.st_blocks*512,sha256=sha(q)))
    rec.update(files=len(rows),logical=sum(x['bytes'] for x in rows),allocated=sum(x['allocated'] for x in rows))
    (E/f'{phase}-output.json').write_text(json.dumps(rows,indent=2)+'\n')
    (E/f'{phase}-generation.json').write_text(json.dumps(rec,indent=2)+'\n')
    print(json.dumps({k:v for k,v in rec.items() if k not in ['source_diff','df_before','df_after']},indent=2))
    assert rec['rc']==0 and not reason, 'generation incomplete; no installation'
    for name in ['register_functions.cpp','ps2_recompiled_functions.h','ps2_recompiled_stubs.h','sub_00426230_0x426230.cpp']+(['sub_002C5140_0x2c5140.cpp'] if phase=='entry' else []):
        q=OUT/name;assert q.exists(),name
        with gzip.open(E/f'{phase}-{name}.gz','wb') as f:f.write(q.read_bytes())
    registry=(OUT/'register_functions.cpp').read_text()
    selected={hex(pc):[l for l in registry.splitlines() if l.rstrip().endswith(f'// 0x{pc:x}')] for pc in [0x426230,0x2c5140,0x2c5358]}
    assert len(selected['0x426230'])==1 and 'sub_00426230_0x426230' in selected['0x426230'][0]
    assert bool(selected['0x2c5140'])==(phase=='entry')
    body=(OUT/'sub_00426230_0x426230.cpp').read_text();assert 'TODO' not in body and 'ps2_stubs::sceSifCmdIntrHdlr' not in body
    (E/f'{phase}-bindings.json').write_text(json.dumps(selected,indent=2)+'\n')
    print('# E11 GENERATION TAIL COMPLETE phase='+phase)
if __name__=='__main__':main()
