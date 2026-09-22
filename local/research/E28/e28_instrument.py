"""Reuse the E21 parser observer by COPY + RE-SHA. Never rebuilt."""
import subprocess
from e28_common import *
assert os.environ.get('COPYFILE_DISABLE')=='1'
proven=json.loads((E.parent/'E21/parser-build.json').read_text())['observer']
src=E.parent/'E24/parser/e21-parser-observer.dylib'
dest=E/'parser';dest.mkdir(exist_ok=True)
dst=dest/'e21-parser-observer.dylib'
rc=subprocess.call(['cp','-p',str(src),str(dst)]);assert rc==0
got=sha(dst)
assert got==proven['sha256'],dict(expected=proven['sha256'],got=got)
save('instrument-reuse.json',dict(utc=utc(),source=str(src),dest=str(dst),
    expected_sha=proven['sha256'],actual_sha=got,bytes=dst.stat().st_size,
    rebuilt=False,method='cp -p then re-sha',chain='E21 built -> E22 -> E23 -> E24 -> E28, byte-identical throughout'))
print('observer reused',got,dst.stat().st_size,'B')
print('# E28 INSTRUMENT TAIL COMPLETE')
