"""Re-verify E20's carried parser inputs by hash, copy them, build observer dylib + isolation harness. No re-encoding."""
import shutil, subprocess
from e21_common import *
assert os.environ.get('COPYFILE_DISABLE')=='1'
assert (E/'checkpoint-complete.json').exists()
admission(sample())
carried=json.loads((E.parent/'E20/carried-inputs.json').read_text())
dest=E/'parser';assert dest.is_dir()
files=[]
for row in carried['files']:
    src=Path(row['path']);assert src.is_file(),src
    assert sha(src)==row['sha256'],src
    if (dest/src.name).is_file():
        assert sha(dest/src.name)==row['sha256'],src  # rebuild: verify, don't re-copy
    else:
        shutil.copyfile(src,dest/src.name)
        assert sha(dest/src.name)==row['sha256']
    files.append(dict(name=src.name,bytes=(dest/src.name).stat().st_size,sha256=row['sha256']))
save('carried-inputs.json',dict(utc=utc(),source_manifest='local/research/E20/carried-inputs.json',
    source_dir='local/research/E20/parser',reencoded=False,failed_dylib_copied=False,files=files))
ff=Path('/opt/homebrew/Cellar/ffmpeg/9.0.1_1');assert ff.is_dir()
cc='/opt/homebrew/opt/llvm/bin/clang'
commands=[
    [cc,'-dynamiclib','-O2','-Wall','-Wextra','-I'+str(ff/'include'),str(E/'e21_parser_observer.c'),
     '-L'+str(ff/'lib'),'-lavcodec','-lavutil','-o',str(dest/'e21-parser-observer.dylib')],
    [cc,'-O2','-Wall','-Wextra','-I'+str(ff/'include'),str(E/'e21_isolation_test.c'),
     '-L'+str(ff/'lib'),'-lavcodec','-lavutil','-lavformat','-o',str(dest/'e21-isolation-test')],
]
save('parser-build-commands.json',dict(utc=utc(),commands=commands,parallelism='one compiler at a time; no Ninja or regeneration'))
for cmd in commands:subprocess.run(cmd,check=True,timeout=300)
save('parser-build.json',dict(utc=utc(),observer=pin(dest/'e21-parser-observer.dylib'),
    harness=pin(dest/'e21-isolation-test'),resources=sample()))
print('# E21 PARSER PREPARATION TAIL COMPLETE')
