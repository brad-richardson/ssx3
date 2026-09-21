"""Apply the one named observation-only runtime change after forcing failure."""
import gzip, subprocess
from e16_common import *

assert os.environ.get('COPYFILE_DISABLE')=='1'
resources=sample();save('repair-admission.json',resources);admission(resources)
failure=json.loads((E/'closure-before-validation.json').read_text())
assert len(failure['cases'])==1 and failure['cases'][0]['rc']==1
assert '# E15 CLOSURE' not in (E/'closure-before-quiescent-events.txt').read_text()
p=R/'ps2xRuntime/src/lib/ps2_runtime.cpp'
assert sha(p)=='f0f717fdc6160632154f7cc2306bb48cd9b0b807ed4576cd3566a3793cddbb76'
before=pin(p)
old='    RUNTIME_LOG("[run] exiting loop");\n}'
new='''    RUNTIME_LOG("[run] exiting loop");

    // The game thread and final host diagnostic producers have finished.
    // main uses _Exit after run(), so close observations here; the destructor
    // retains its safe fallback (shutdown closes the shared sink once).
    ps2_e15::closure(m_memory.gs().vsyncTick.load());
    ps2_e7::shutdown(m_memory.gs().vsyncTick.load());
}'''
text=p.read_text();assert text.count(old)==1
p.write_text(text.replace(old,new))
with gzip.open(E/'sources/runtime-after.cpp.gz','wb') as f:f.write(p.read_bytes())
diff=subprocess.run(['git','-C',str(R),'diff','--','ps2xRuntime/src/lib/ps2_runtime.cpp'],capture_output=True,text=True,check=True)
(E/'observation-repair.diff').write_text(diff.stdout)
record=dict(utc=utc(),class_='OBSERVATION',named_file=str(p),before=before,after=pin(p),added_lines=6,guest_state_writes_added=0,main_changed=False,mpeg_changed=False,destructor_fallback_retained=True)
save('repair.json',record)
print(diff.stdout);print('# E16 OBSERVATION REPAIR TAIL COMPLETE')
