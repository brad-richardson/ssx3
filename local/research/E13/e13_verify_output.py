#!/usr/bin/env python3
"""Verify the already-completed generation; never spawn or edit the generator."""
import gzip,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parent;OUT=Path('/tmp/ssx3-e13-leaf-codegen')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rec=json.loads((E/'entry-generation.json').read_text());assert rec['rc']==0 and not rec.get('bound')
rows=json.loads((E/'entry-output.json').read_text())
for r in rows:assert sha(OUT/r['name'])==r['sha256'],r['name']
text=(OUT/'register_functions.cpp').read_text()
selected={hex(pc):[l for l in text.splitlines() if l.rstrip().endswith(f'// 0x{pc:x}')] for pc in [0x426230,0x2c5140,0x2c5300,0x2c5358]}
for pc,name in [('0x426230','sub_00426230_0x426230'),('0x2c5140','sub_002C5140_0x2c5140'),('0x2c5300','sub_002C5300_0x2c5300'),('0x2c5358','sub_002C5358_0x2c5358')]:
    assert len(selected[pc])==1 and name in selected[pc][0]
p=(OUT/'sub_002C5358_0x2c5358.cpp').read_text()
assert 'ps2_stubs::' not in p and 'GuestBranchKind::DirectCall' not in p and 'GuestBranchKind::IndirectCall' not in p
assert p.count('dispatchGuestBranch')>=1 and 'GuestBranchKind::Return, "JR $ra"' in p
before={Path(r['path']).name:r['sha256'] for r in json.loads((E/'before/generated.json').read_text())}
generated={r['name']:r['sha256'] for r in rows if r['name'].endswith(('.cpp','.h'))}
added=sorted(set(generated)-set(before));deleted=sorted(set(before)-set(generated))
changed=sorted(n for n in before if before[n]!=generated.get(n))
assert added==['sub_002C5358_0x2c5358.cpp'] and not deleted
assert changed==['ps2_recompiled_functions.h','register_functions.cpp']
for name in ['sub_002C5140_0x2c5140.cpp','sub_002C52D8_0x2c52d8.cpp','sub_002C5338_0x2c5338.cpp','sub_002C5300_0x2c5300.cpp','sub_00426230_0x426230.cpp']:
    assert before[name]==generated[name]
(E/'entry-bindings.json').write_text(json.dumps(selected,indent=2)+'\n')
(E/'generation-scope-audit.json').write_text(json.dumps(dict(all_output_hashes_match=True,files=len(rows),added=added,deleted=deleted,changed_existing=changed,
    query_unchanged=True,drop_unchanged=True,predicate_owner_unchanged=True,leaf_owner_unchanged=True,prior_predicate_unchanged=True,leaf_present=True),indent=2)+'\n')
print('Output hashes complete; leaf exact; query/predicate/DROP/owners unchanged')
print('# E13 OUTPUT VERIFICATION TAIL COMPLETE; no generation repeated')
