"""Analyze the one closed probe; preserve exact missing receipts on any gap."""
import subprocess,sys
from e17_common import *
end=json.loads((E/'e17a-result.json').read_text());assert end.get('release_utc')
results=[]
for script,args in [('e17_mine.py',[]),('e17_card.py',['a']),('e17_lifetime.py',[]),('e17_progress.py',['a'])]:
    argv=[sys.executable,'-B',str(E/script),*args];log=E/(script.removesuffix('.py')+'-analysis.txt')
    with log.open('w') as f:p=subprocess.run(argv,stdout=f,stderr=subprocess.STDOUT,timeout=120)
    results.append(dict(script=script,argv=argv,rc=p.returncode,log=log.name,tail=log.read_text().splitlines()[-6:]))
newrows=[]
if (E/'e17a-function-census.json').exists() and (E/'e17a-progress.json').exists():
    census=json.loads((E/'e17a-function-census.json').read_text());progress=json.loads((E/'e17a-progress.json').read_text())
    for r in json.loads((E/'row-verification.json').read_text())['rows']:
        name=f"sub_{int(r['start'],16):08X}_{r['start']}"
        newrows.append(dict(pc=r['start'],function_name=name,owner_entries=census['entries'].get(name,0),missing_records=sum(g['count'] for g in progress['missing_groups'] if g['target']==r['start'])))
record=dict(utc=utc(),results=results,all_miners_rc0=all(r['rc']==0 for r in results),new_row_trace_receipts=newrows,
    gaps=[dict(script=r['script'],log=r['log'],tail=r['tail']) for r in results if r['rc']!=0],title_boots=1,no_second_boot=True)
save('boot-analysis-summary.json',record)
print(json.dumps(record,indent=2));print('# E17 BOOT ANALYSIS TAIL COMPLETE')
