"""Five actual-registry absent/present expectations; no title execution."""
import sys
from e17_common import *
from e17_validate import logged
phase=sys.argv[1];assert phase in ('before','after')
attempt=sys.argv[2] if len(sys.argv)>2 else 'complete'
binary=P/'e17-fixtures'/phase/'binding-test';records=[]
for row in json.loads((E/'row-verification.json').read_text())['rows']:
    for mode in ('check-absent','check-present'):
        expected=0 if (mode=='check-absent')==(phase=='before') else 1
        env={k:v for k,v in os.environ.items() if not k.startswith('PS2X_')}
        dest=P/'e17-fixtures'/('presence-'+phase+'-'+attempt)/(row['start']+'-'+mode);dest.mkdir(parents=True,exist_ok=False)
        log=E/f"{phase}-{attempt}-{row['start']}-{mode}.txt"
        rc,txt,rec=logged([str(binary),mode,row['start']],env,dest,log)
        rec.update(pc=row['start'],mode=mode,rc=rc,expected_rc=expected,stdout=log.name)
        records.append(rec);save(phase+'-presence.json',dict(utc=utc(),binary=pin(binary),cases=records))
        assert rc==expected and 'titleBoots=0' in txt,rec
        if phase=='after':assert f"sub_{int(row['start'],16):08X}_{row['start']}" in txt
        else:assert 'hasFunction=0' in txt and 'No exact recompiled function' in txt
        print(row['start'],mode,'rc',rc,'expected',expected)
print('# E17 FIVE PRESENCE CHECKS TAIL COMPLETE phase='+phase)
