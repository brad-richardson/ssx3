#!/usr/bin/env python3
"""Explain the missing boot footer without manufacturing a source receipt."""
import gzip,hashlib,json,subprocess
from pathlib import Path
from e15_io import read_capture
from e15_closed_events import tap
E=Path(__file__).resolve().parent
R=Path('/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp')
RUN=R.parent/'P1/run'
rel='ps2xRuntime/src/main.cpp';src=(R/rel).read_bytes()
baseline=subprocess.check_output(['git','-C',str(R),'show','83fb4d60904abb016522c477cce704c52118f95f:'+rel])
assert src==baseline
(E/'sources/main.cpp.gz').write_bytes(gzip.compress(src,mtime=0))
lines=src.decode().splitlines()
sites=[dict(line=i,text=l.strip()) for i,l in enumerate(lines,1) if any(x in l for x in ['PS2Runtime runtime;','runtime.run();','std::_Exit'])]
events=read_capture(RUN/'e15a-join/e7-events.txt')
assert events.endswith(b'\n') and b'# E7 SHUTDOWN' not in events and b'# E15 CLOSURE' not in events
try:tap(RUN/'e15a-join/e7-events.txt')
except AssertionError as exc:strict_failure=str(exc)
else:raise AssertionError('strict closure must fail')
result=json.loads((E/'e15a-result.json').read_text())
assert result['rc']==0 and result.get('release_utc')
row=dict(main_sha256=hashlib.sha256(src).hexdigest(),main_same_as_baseline=True,sites=sites,
    fork_observation_commit='67c0a632d44cad8c0e47b4e2c0ee3782b22fd467',
    boot_event_bytes=len(events),boot_event_sha256=hashlib.sha256(events).hexdigest(),
    last_event=events.decode().splitlines()[-1],strict_closure_failure=strict_failure,
    destructor_hook='ps2xRuntime/src/lib/ps2_runtime.cpp:698-699',
    fixture_footers='final-no-input-events.txt and final-input-events.txt: both destructor-scope fixtures have real source footers',
    explanation='Normal runner main calls std::_Exit(0) after runtime.run(); the automatic runtime destructor is bypassed. Its E15 closure hooks are therefore unreachable on this boot exit path.',
    unavailable=['final E15 counters','final pending count','registrationTruncated flag','E7 final byte counters and truncation flags'],
    limits='Observed sequence continuity and pairs, explicit E4 span completion, rc=0, pgrep=1 and lease release do not replace missing source counters.',
    next_measurement='Emit idempotent closure from the handwritten runtime run() exit after gameThread.join(), before control reaches main _Exit; retain destructor fallback. Test the real run-exit closure path, including quiescence and duplicate closure, before any separately authorized boot. No MPEG change or generated-TU rebuild required.')
(E/'exit-closure-audit.json').write_text(json.dumps(row,indent=2)+'\n')
print(json.dumps(row,indent=2));print('# E15 EXIT AUDIT TAIL COMPLETE: source closure absent, not synthesized')
