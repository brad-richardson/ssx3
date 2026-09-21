"""One authorized five-row map edit, pinned generation, verified installation."""
import gzip,subprocess,sys,tomllib
from e17_common import *
assert os.environ.get('COPYFILE_DISABLE')=='1'
phase=sys.argv[1];CSV=R/'games/ssx3/ssx3-functions.sweep.csv';CONFIG=R/'games/ssx3/ssx3.toml'
prediction='7c827add09aeea837e25f6048007ab91e65eb4b5f7a98f8fb4f448b606cfb9ba'
def fresh(label):
    r=sample();save(label+'.json',r);admission(r)
    assert r['internal_free']>=3489660928
    return r
rows=json.loads((E/'row-verification.json').read_text())['rows'];assert len(rows)==5 and all(r['verified'] for r in rows)
if phase=='edit':
    gate=json.loads((E/'before-presence.json').read_text());assert len(gate['cases'])==10 and all(x['rc']==x['expected_rc'] for x in gate['cases'])
    for label in ['baseline-suite','baseline-closure','baseline-prior']:
        d=json.loads((E/(label+'-bounded-result.json')).read_text());assert d['rc']==0 and d['bound'] is None
    fresh('admission-at-edit')
    before=CSV.read_bytes();after=(E/'predicted.csv').read_bytes()
    assert before==(E/'before-ssx3-functions.sweep.csv').read_bytes()
    assert hashlib.sha256(after).hexdigest()==prediction
    reverted=after
    for r in rows:reverted=reverted.replace((r['row']+'\n').encode(),b'',1)
    assert reverted==before
    CSV.write_bytes(after)
    save('map-edit.json',dict(utc=utc(),before=hashlib.sha256(before).hexdigest(),after=sha(CSV),rows=[dict(row=r['row'],line=after.decode().splitlines().index(r['row'])+1) for r in rows],only_five_insertions=True))
elif phase=='generate':
    assert sha(CSV)==prediction
    tool=Path('/Volumes/Extreme SSD/ps2x-i10/host-recomp/ps2xRecomp/ps2_recomp')
    assert sha(tool)=='511791795c16649e69706725c412408acc8d35fda68c4d83a3229eae6bda0763'
    p=subprocess.run(['git','-C',str(R),'diff','b6252bb..HEAD','--','ps2xRecomp','ps2xAnalyzer'],capture_output=True,text=True)
    assert p.returncode==0 and not p.stdout
    fresh('admission-before-generation')
    OUT.mkdir(exist_ok=False);(OUT/'E17-owner.json').write_text(json.dumps(dict(utc=utc(),evidence=str(E))))
    text=CONFIG.read_text();cfg=tomllib.loads(text);used=text.replace(cfg['general']['output'],str(OUT)+'/')
    checked=tomllib.loads(used);checked['general']['output']=cfg['general']['output'];assert checked==cfg
    config=E/'generation-used.toml';config.write_text(used)
    fresh('admission-at-spawn')
    command=[str(tool),str(config)]
    save('generation-start.json',dict(utc=utc(),argv=command,cwd=str(R),tool=pin(tool),config_sha256=sha(config),canonical_sha256=sha(CONFIG),csv_sha256=sha(CSV),source_diff=p.stdout))
    proc=subprocess.run(command,cwd=R)
    output=[dict(name=p.name,**{k:v for k,v in pin(p).items() if k!='path'}) for p in sorted(OUT.iterdir()) if p.is_file()]
    save('generation-output.json',output);save('generation-result.json',dict(utc=utc(),rc=proc.returncode,files=len(output),allocated=size(OUT),logical=size(OUT,False)))
    assert proc.returncode==0
elif phase=='verify':
    assert json.loads((E/'generation-result.json').read_text())['rc']==0
    generated={r['name']:r['sha256'] for r in json.loads((E/'generation-output.json').read_text()) if r['name'].endswith(('.cpp','.h'))}
    old={Path(r['path']).name:r['sha256'] for r in json.loads((E/'before-generated.json').read_text())}
    assert len(old)==9452
    added=sorted(set(generated)-set(old));deleted=sorted(set(old)-set(generated))
    changed=sorted(k for k in old if old[k]!=generated.get(k))
    names=sorted(f"sub_{int(r['start'],16):08X}_{r['start']}.cpp" for r in rows)
    assert added==names and not deleted and changed==['ps2_recompiled_functions.h','register_functions.cpp'],(added,deleted,changed)
    for r in json.loads((E/'generation-output.json').read_text()):assert sha(OUT/r['name'])==r['sha256']
    for r in rows:
        name=f"sub_{int(r['start'],16):08X}_{r['start']}.cpp";assert generated[name]==r['i_entry_sha256']
    registry=(OUT/'register_functions.cpp').read_text().splitlines()
    slots={}
    for pc in [int(r['start'],16) for r in rows]+[0x2c5140,0x2c5300,0x2c5358,0x426230]:
        found=[dict(line=n,text=l) for n,l in enumerate(registry,1) if l.rstrip().endswith(f'// 0x{pc:x}')]
        assert len(found)==1 and f'sub_{pc:08X}_0x{pc:x}' in found[0]['text'];slots[hex(pc)]=found
    save('generation-scope.json',dict(utc=utc(),generated_files=len(generated),added=added,changed=changed,deleted=deleted,slots=slots,all_existing_bodies_unchanged=True,all_five_entries_equal_I_lane=True))
    for name in added+changed:(E/'sources'/(name+'.gz')).write_bytes(gzip.compress((OUT/name).read_bytes(),mtime=0))
elif phase=='install':
    scope=json.loads((E/'generation-scope.json').read_text());assert scope['generated_files']==9457
    fresh('admission-at-install');dest=R/'ps2xRuntime/src/runner';record=[]
    quarantine=P/'e17-install-metadata';quarantine.mkdir(exist_ok=False)
    for name in scope['added']+scope['changed']:
        src=OUT/name;dst=dest/name;side=dst.with_name('._'+dst.name);pre=side.exists()
        previous=sha(dst) if dst.exists() else None
        shutil.copyfile(src,dst);assert sha(src)==sha(dst)
        metadata=None
        if side.exists() and not pre:
            metadata=pin(side);side.rename(quarantine/side.name)
        record.append(dict(name=name,before=previous,after=sha(dst),created_sidecar=metadata,sidecar_preexisting=pre))
        assert not bound(sample())
    after=[]
    for r in json.loads((E/'generation-output.json').read_text()):
        if r['name'].endswith(('.cpp','.h')):
            p=dest/r['name'];assert sha(p)==r['sha256'];after.append(pin(p))
    save('after-generated.json',after);save('installation.json',dict(utc=utc(),changes=record,generated_files=len(after),resources=sample(),source_scratch_preserved=True))
else:raise AssertionError(phase)
print('# E17 ABSORB PHASE TAIL COMPLETE '+phase)
