#!/usr/bin/env python3
"""Extend E11's bounded read-only taps for predicate arguments and UI stores."""
import hashlib,json,os
from pathlib import Path
E=Path(__file__).resolve().parent;R=Path('/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp')
def main():
    assert os.environ.get('COPYFILE_DISABLE')=='1'
    h=R/'ps2xRuntime/include/ps2_e7.h';cpp=R/'ps2xRuntime/src/lib/ps2_runtime.cpp'
    before={p:p.read_text() for p in [h,cpp]};texts=dict(before)
    changes=[
        (h,'(ui && address==ui+0x338u)', '(ui && (address==ui+0x338u || address==ui+0x344u || address==ui+0x424u))'),
        (h,'return target==0x2c5140u || target==0x2c5358u', 'return target==0x2c5300u || target==0x2c5140u || target==0x2c5358u'),
        (h,'uint32_t target, uint32_t source, uint32_t entryA0,', 'uint32_t target, uint32_t source, uint32_t entryA0, uint32_t entryA1,'),
        (h,'(target==0x2c5140u || target==0x2c5358u) ? entryA0', '(target==0x2c5300u || target==0x2c5140u || target==0x2c5358u) ? entryA0'),
        (h,'a0=0x%x a1=0x%x a2=0x%x', 'a0=0x%x a1=0x%x a1Now=0x%x a2=0x%x'),
        (h,'target,source,entryA0,a1,a2,a3,pc,v0', 'target,source,entryA0,entryA1,a1,a2,a3,pc,v0'),
        (cpp,'    const uint32_t cardA0 = cardObservation ? getRegU32(ctx, 4) : 0u;',
             '    const uint32_t cardA0 = cardObservation ? getRegU32(ctx, 4) : 0u;\n    // E12: retain original port across predicate execution (observation only).\n    const uint32_t cardA1 = cardObservation ? getRegU32(ctx, 5) : 0u;'),
        (cpp,'targetPc, sourcePc, cardA0, ctx->pc, getRegU32(ctx, 2),',
             'targetPc, sourcePc, cardA0, cardA1, ctx->pc, getRegU32(ctx, 2),'),
        (cpp,'targetPc, sourcePc, getRegU32(ctx,4), ctx->pc, getRegU32(ctx,2),',
             'targetPc, sourcePc, getRegU32(ctx,4), getRegU32(ctx,5), ctx->pc, getRegU32(ctx,2),'),
    ]
    for path,old,new in changes:
        assert texts[path].count(old)==1,(path,old)
        texts[path]=texts[path].replace(old,new)
    rows=[]
    for p,text in texts.items():
        side=p.with_name('._'+p.name);side_before=side.exists()
        p.write_text(text)
        removed=False
        if side.exists() and not side_before:side.unlink();removed=True
        rows.append(dict(path=str(p),before=hashlib.sha256(before[p].encode()).hexdigest(),after=hashlib.sha256(text.encode()).hexdigest(),sidecar_preexisting=side_before,removed_created_sidecar=removed))
    (E/'observation-install.json').write_text(json.dumps(dict(files=rows,window='existing E7 boot/boundary budget, card tick <=603',new_targets=['0x2c5300'],ui_offsets=['0x344','0x424'],preserved_original_arguments=['a0','a1'],behavior='read-only'),indent=2)+'\n')
    print('# E12 OBSERVATION TAIL COMPLETE; no guest state or dispatch-result mutation')
if __name__=='__main__':main()
