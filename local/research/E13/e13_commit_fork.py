#!/usr/bin/env python3
"""Commit only the authorized map row and bounded observations, to fork only."""
import datetime,json,os,subprocess
from pathlib import Path
E=Path(__file__).resolve().parent
R=Path('/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp')
assert os.environ.get('COPYFILE_DISABLE')=='1'
assert not (E/'fork-commit.json').exists()
gate=json.loads((E/'entry-preflight.json').read_text())
assert gate['binding_rc']==gate['suite_rc']==0 and gate['leaf_cases']==24
commands=[]
def git(*args):
    p=subprocess.run(['git','-C',str(R),*args],capture_output=True,text=True)
    r=dict(argv=p.args,rc=p.returncode,stdout=p.stdout,stderr=p.stderr);commands.append(r)
    (E/'fork-commit-commands.json').write_text(json.dumps(commands,indent=2)+'\n')
    assert p.returncode==0,r
    return p.stdout.strip()
assert git('rev-parse','HEAD')=='9da21ff8aeb9529368b32d91b0eec6a82ba79344'
assert git('branch','--show-current')=='ssx3'
assert not git('diff','--cached','--name-only')
assert git('remote','get-url','--push','fork')=='https://github.com/brad-richardson/PS2Recomp.git'
files=['games/ssx3/ssx3-functions.sweep.csv','ps2xRuntime/include/ps2_e7.h','ps2xRuntime/src/lib/ps2_runtime.cpp']
git('diff','--check','--',*files)
git('add','--',*files)
assert sorted(git('diff','--cached','--name-only').splitlines())==sorted(files)
git('commit','-m','SSX3: restore the exact card-result leaf')
head=git('rev-parse','HEAD')
assert sorted(git('show','--format=','--name-only','HEAD').splitlines())==sorted(files)
git('push','fork','HEAD:ssx3')
remote=git('ls-remote','fork','refs/heads/ssx3').split()[0];assert remote==head
record=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),head=head,remote=remote,
            files=files,status=git('status','--short'),generated_staged=False,commands=commands)
(E/'fork-commit.json').write_text(json.dumps(record,indent=2)+'\n')
print('fork commit',head,'remote verified',remote)
print('# E13 FORK COMMIT TAIL COMPLETE; generated sources never staged')
