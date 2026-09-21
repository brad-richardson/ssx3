"""Bounded build of observation-only dylib and authored MPEG continuation."""
import subprocess
from e19_common import *
assert os.environ.get('COPYFILE_DISABLE')=='1'
assert (E/'checkpoint-complete.json').exists()
admission(sample())
dest=E/'parser';dest.mkdir(exist_ok=False)
ff=Path('/opt/homebrew/Cellar/ffmpeg/9.0.1_1')
commands=[['/opt/homebrew/opt/llvm/bin/clang','-dynamiclib','-O2','-Wall','-Wextra',
          '-I'+str(ff/'include'),str(E/'e19_parser_observer.c'),'-L'+str(ff/'lib'),'-lavcodec','-lavutil',
          '-o',str(dest/'e19-parser-observer.dylib')],
          [str(ff/'bin/ffmpeg'),'-hide_banner','-nostdin','-loglevel','error','-f','lavfi',
           '-i','color=c=black:s=800x448:r=30000/1001','-frames:v','8','-c:v','mpeg2video',
           '-threads','1','-g','12','-bf','0','-q:v','2','-f','mpeg2video',str(dest/'authored-black.m2v')]]
save('parser-build-commands.json',dict(utc=utc(),commands=commands,parallelism='one compiler, then one encoder thread; no Ninja or regeneration'))
for cmd in commands:subprocess.run(cmd,check=True,timeout=120)
prefix=bytes.fromhex('000001b32001c014095de380000001b5148a00010000000001b52105050408020e00000001b2456e636f6465642077697468204d5045472047696d6578206d6f')
assert len(prefix)==64
(dest/'E18-retained-first64.bin').write_bytes(prefix)
assert prefix.hex() in (E.parent/'E18/e18a-events.txt').read_text()
authored=(dest/'authored-black.m2v').read_bytes()
gop=authored.index(b'\x00\x00\x01\xb8')
continuation=authored[gop:]
(dest/'authored-continuation.bin').write_bytes(continuation)
rows=[]
for shift in [64,5040,8192,16384,None]:
    if shift is None:data=prefix+b'X'*(16384-64);name='prefix-userdata-only'
    else:
        data=prefix+b'X'*(shift-64)+continuation
        data+=b'X'*max(0,16384-len(data));name=f'boundary-{shift}'
    assert len(data)<=65536
    p=dest/(name+'.bin');p.write_bytes(data)
    codes=[dict(offset=i,code=data[i+3]) for i in range(len(data)-3) if data[i:i+3]==b'\x00\x00\x01']
    rows.append(dict(name=name,retained_bytes=64,authored_bytes=len(data)-64,gop_offset=shift,payload=pin(p),start_codes=codes))
save('authored-manifest.json',dict(utc=utc(),source='Only first64 from E18; all remaining bytes authored here. Not E18 full-payload replay.',
    prefix=pin(dest/'E18-retained-first64.bin'),encoder_output=pin(dest/'authored-black.m2v'),gop_offset_in_authored=gop,
    continuation=pin(dest/'authored-continuation.bin'),observer=pin(dest/'e19-parser-observer.dylib'),cases=rows))
print([(r['name'],r['payload']['bytes'],len(r['start_codes'])) for r in rows])
print('# E19 PARSER PREPARATION TAIL COMPLETE')
