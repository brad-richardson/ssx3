#!/usr/bin/env python3
"""Audit closed E8 hashes/caps, then require byte-identical offline miner replay."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]


def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def main():
    assert os.environ.get('COPYFILE_DISABLE')=='1'
    unique={};checks=[]
    for label in ['e8a','e8b']:
        manifest=json.loads((HERE/f'{label}-retained.json').read_text())
        end=json.loads((HERE/f'{label}-result.json').read_text())
        config=json.loads((HERE/f'{label}-config.json').read_text())
        caps=config['caps'];assert end['rc']==0 and end.get('release_utc')
        assert end['elapsed_s']<caps['wall_s'] and end['bind']['trace_lines']<caps['progress_lines']
        closed={k:0 for k in ['boot_log','trace','function_log','e4_dir','e7_dir','frames_dir','park_dir']}
        for row in manifest['files']:
            p=HERE/row['canonical'];unique[str(p.resolve())]=row
            original=Path(row['original']);parent=original.parent.name;name=original.name
            category='boot_log' if name==f'boot-{label}-1.log' else 'trace' if name==f'syscalls-{label}-on.txt' else 'function_log' if name==f'ps2_log-{label}-1.txt' else 'e4_dir' if parent==f'{label}-1' else 'e7_dir' if parent==f'{label}-join' else 'frames_dir' if parent==f'frames-{label}-1' else 'park_dir' if parent==f'park-{label}-1' else None
            assert category,(label,original)
            closed[category]+=row['bytes']
        closed['aggregate']=sum(closed.values())
        assert all(v<caps[k] for k,v in closed.items()),(label,closed,caps)
        for line in (HERE/f'{label}-liveness.txt').read_text().splitlines():
            item=json.loads(line)
            if 'bytes' in item:assert all(v<caps[k] for k,v in item['bytes'].items())
        checks.append(dict(label=label,wall=end['elapsed_s'],bound=end['bound'],closed_bytes=closed,release=end['release_utc']))
    for name,row in unique.items():
        p=Path(name);op=gzip.open if row['encoding']=='gzip' else open
        with op(p,'rb') as f:got=hashlib.file_digest(f,'sha256').hexdigest()
        assert got==row['sha256'],name
    artifacts=[HERE/f'{label}-{suffix}' for label in ['e8a','e8b'] for suffix in
               ['summary.json','frame.json','progress.json','function-census.json','watch-series.txt','burst-series.txt','missing-query.txt','progress-lines.txt']]
    artifacts += [HERE/n for n in ['e8-wall-dis.txt','e8-runtime-policy.txt','e8-join.txt']]
    before={p.name:sha(p) for p in artifacts}
    runs=[]
    for script,args in [('e8_mine.py',['a']),('e8_mine.py',['b']),('e8_frame.py',['a']),('e8_frame.py',['b']),
                        ('e8_progress.py',['a']),('e8_progress.py',['b']),('e8_wall.py',[]),('e8_join.py',[])]:
        cmd=[sys.executable,'-B',str(HERE/script),*args]
        run=subprocess.run(cmd,cwd=REPO,text=True,capture_output=True)
        assert run.returncode==0,(cmd,run.stdout,run.stderr)
        runs.append(dict(script=script,args=args,rc=run.returncode,tail=run.stdout.splitlines()[-1]))
    after={p.name:sha(p) for p in artifacts}
    assert before==after,{k:(before[k],after[k]) for k in before if before[k]!=after[k]}
    result=dict(caps=checks,canonical_payloads_verified=len(unique),miner_runs=runs,
                byte_identical_derived_files=after)
    (HERE/'e8-replay.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(canonical_payloads_verified=len(unique),byte_identical_derived_files=len(after),miner_runs=len(runs))))
    print('# E8 REPLAY TAIL COMPLETE: all canonical hashes, both cap envelopes and all offline miner outputs verified')


if __name__=='__main__':main()
