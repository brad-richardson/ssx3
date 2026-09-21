#!/usr/bin/env python3
"""Derive the authorized leaf row from the ELF and emitted owner, without editing."""
import hashlib,json,re
from pathlib import Path
from e13_static import Elf,ROOT
E=Path(__file__).resolve().parent;R=ROOT.parent/'PS2Recomp'
elf=Elf(ROOT);start=0x2c5358
csv=(R/'games/ssx3/ssx3-functions.sweep.csv').read_bytes()
owner=b'sub_002C5338,0x2c5338,0x2c53b0,0x78\n'
assert csv.count(owner)==1 and b'sub_002C5358,' not in csv
end=int(owner.decode().split(',')[2],16)
body=R/'ps2xRuntime/src/runner/sub_002C5338_0x2c5338.cpp'
words={int(a,16):int(w,16) for a,w in re.findall(r'// (0x[0-9a-f]+): (0x[0-9a-f]+)',body.read_text())}
omitted=[pc for pc in range(start,end,4) if pc not in words]
assert all(elf.word(pc)==0 for pc in omitted), 'Only elided NOPs may lack source comments'
assert all(words[pc]==elf.word(pc) for pc in range(start,end,4) if pc in words)
assert elf.word(0x2c53a0)==elf.word(0x2c53a8)==0x03e00008 and elf.word(0x2c53ac)==0
row=f'sub_{start:08X},{start:#x},{end:#x},{end-start:#x}\n'.encode()
expected='0c6085744ab1a2afd60170a18ac261db02472441fa1d343ffd6756026e92d9f4'
predicted=hashlib.sha256(csv.replace(owner,owner+row)).hexdigest()
rec=dict(row=row.decode().strip(),row_hex=row.hex(),owner=owner.decode().strip(),
         start=hex(start),end=hex(end),instructions=(end-start)//4,emitted_annotation_count=(end-start)//4-len(omitted),elided_zero_word_nops=[hex(pc) for pc in omitted],
         elf_sha256=hashlib.sha256(elf.data).hexdigest(),owner_sha256=hashlib.sha256(body.read_bytes()).hexdigest(),
         before_csv_sha256=hashlib.sha256(csv).hexdigest(),predicted_csv_sha256=predicted,
         expected_csv_sha256=expected,prediction_matches=predicted==expected,csv_modified=False)
(E/'row-derivation.json').write_text(json.dumps(rec,indent=2)+'\n')
print(json.dumps(rec,indent=2));assert rec['prediction_matches']
print('# E13 ROW DERIVATION TAIL COMPLETE; raw/emitted instructions agree; omitted NOPs pinned as zero; no CSV mutation')
