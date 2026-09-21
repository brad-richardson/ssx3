"""Q1 measurements using actual AddBs + parser API calls; labeled synthetic input."""
import gzip
from e21_common import *
from e21_validate import logged
from e21_parser_receipt import receipt
assert os.environ.get('COPYFILE_DISABLE')=='1'
assert (E/'checkpoint-complete.json').exists() and (E/'observer-regression.json').exists()
admission(sample())
carried=json.loads((E/'carried-inputs.json').read_text())
by_name={f['name']:f for f in carried['files']}
cases=[('boundary-64.bin',64),('boundary-5040.bin',5040),('boundary-8192.bin',8192),
       ('boundary-16384.bin',16384),('prefix-userdata-only.bin',None)]
binary=P/'e21-fixtures/threshold/binding-test';results=[]
for filename,gop in cases:
    payload=E/'parser'/filename;info=by_name[filename]
    assert payload.is_file() and sha(payload)==info['sha256']
    for mode in (['marks'] if gop is None else ['marks','byte']):
        name=filename.removesuffix('.bin')+'-'+mode;directory=P/'e21-fixtures/parser-cases'/name;directory.mkdir(parents=True,exist_ok=False)
        env={k:v for k,v in os.environ.items() if not k.startswith('PS2X_')}
        env.update(DYLD_INSERT_LIBRARIES=str(E/'parser/e21-parser-observer.dylib'),PS2X_E21_PARSER_DIR=str(directory))
        argv=[str(binary),'threshold',str(payload),mode]
        rc,txt,record=logged(argv,env,directory,E/(name+'.txt'),300)
        record.update(name=name,mode=mode,rc=rc,payload=info)
        save(name+'-run.json',record)
        assert rc==0 and '# E21 ACTUAL PARSER FIXTURE TAIL COMPLETE boot=0' in txt,(name,rc)
        r=receipt(directory);assert r['footer']['errors']==r['footer']['sendEof']==0
        marks=[x for x in r['rows'] if x['kind']=='mark'];first=next((x for x in r['rows'] if x['kind']=='parse-return' and x['packetSize']>0),None)
        row=dict(name=name,mode=mode,retained_bytes=64,authored_bytes=payload.stat().st_size-64,gop_offset=gop,
                 payload=info,footer=r['footer'],marks=marks,first_packet_call=first,boot=0)
        results.append(row);save('threshold-results.json',dict(utc=utc(),cases=results))
        dest=E/'threshold-raw';dest.mkdir(exist_ok=True)
        for raw in ['parser-events.txt','parser-input.bin']:
            p=directory/raw
            with gzip.open(dest/(name+'-'+raw+'.gz'),'wb') as f:f.write(p.read_bytes())
        assert sum(size(p,False) for p in (P/'e21-fixtures/parser-cases').rglob('*') if p.is_file())<64*M
        print(name,[(x['bytes'],x['packets'],x['frames']) for x in marks],flush=True)
save('q1-complete.json',dict(utc=utc(),cases=len(results),actual_AddBs=True,EOF_flushes=0,
    source='64 retained E18 bytes plus exactly labeled authored bytes only',parser_observer=pin(E/'parser/e21-parser-observer.dylib'),resources=sample()))
print('# E21 Q1 PARSER THRESHOLD TAIL COMPLETE')
