#!/usr/bin/env python3
"""Commit only the five authorized observation files to the fork remote."""
import datetime,json,os,subprocess
from pathlib import Path
E=Path(__file__).resolve().parent
R=Path('/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp')
assert os.environ.get('COPYFILE_DISABLE')=='1'
assert not (E/'fork-commit.json').exists()
gate=json.loads((E/'entry-preflight.json').read_text())
assert gate['binding_rc']==gate['suite_rc']==0 and gate['leaf_cases']==24 and gate['mpeg_fail_before_cases']==2
commands=[]
def git(*args):
    p=subprocess.run(['git','-C',str(R),*args],capture_output=True,text=True)
    r=dict(argv=p.args,rc=p.returncode,stdout=p.stdout,stderr=p.stderr);commands.append(r)
    (E/'fork-commit-commands.json').write_text(json.dumps(commands,indent=2)+'\n')
    assert p.returncode==0,r
    return p.stdout.strip()
assert git('rev-parse','HEAD')=='83fb4d60904abb016522c477cce704c52118f95f'
assert git('branch','--show-current')=='ssx3'
assert not git('diff','--cached','--name-only')
assert git('remote','get-url','--push','fork')=='https://github.com/brad-richardson/PS2Recomp.git'
files=['ps2xRuntime/include/ps2_e4.h','ps2xRuntime/include/ps2_e7.h','ps2xRuntime/include/ps2_e15.h','ps2xRuntime/src/lib/ps2_runtime.cpp','ps2xRuntime/src/lib/Kernel/EeScheduler.cpp']
git('diff','--check','--',*files)
git('add','--',*files)
assert sorted(git('diff','--cached','--name-only').splitlines())==sorted(files)
git('commit','-m','Diagnostics: trace MPEG requests and align UI captures')
head=git('rev-parse','HEAD')
assert sorted(git('show','--format=','--name-only','HEAD').splitlines())==sorted(files)
git('push','fork','HEAD:ssx3')
remote=git('ls-remote','fork','refs/heads/ssx3').split()[0];assert remote==head
record=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),head=head,remote=remote,
            files=files,status=git('status','--short'),generated_staged=False,commands=commands)
(E/'fork-commit.json').write_text(json.dumps(record,indent=2)+'\n')
print('fork commit',head,'remote verified',remote)
print('# E15 FORK COMMIT TAIL COMPLETE; generated sources never staged')
