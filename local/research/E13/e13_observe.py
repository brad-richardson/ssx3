#!/usr/bin/env python3
"""Extend existing bounded E7 observations for leaf/consumer/flag/state joins."""
import hashlib,json,os
from pathlib import Path
E=Path(__file__).resolve().parent;R=Path('/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp')
def main():
    assert os.environ.get('COPYFILE_DISABLE')=='1'
    h=R/'ps2xRuntime/include/ps2_e7.h';cpp=R/'ps2xRuntime/src/lib/ps2_runtime.cpp'
    before={p:p.read_text() for p in [h,cpp]};texts=dict(before)
    changes=[
      (h,'address==ui+0x424u))','address==ui+0x424u || address==ui+0x43cu || address==ui+0x440u || address==ui+0x130u || address==ui+0xb8u || address==ui+0x748u))'),
      (h,'addr=0x%x width=%u value=0x%llx pc=0x%x thread=%d",\n              mc,ui,address,width,static_cast<unsigned long long>(lo),pc,thread);',
         'addr=0x%x width=%u old=0x%x value=0x%llx pc=0x%x thread=%d",\n              mc,ui,address,width,word(ram,address),static_cast<unsigned long long>(lo),pc,thread);'),
      (h,'inline bool cardTarget(uint32_t target)','inline bool cardTarget(uint32_t target, uint32_t source = 0u)'),
      (h,'target==0x2c4980u || target==0x2c50e0u || target==0x40a498u || target==0x40a360u;',
         'target==0x2c4980u || target==0x2c50e0u || target==0x40a498u || target==0x40a360u ||\n           target==0x2d3810u || target==0x241b20u || target==0x241cd8u || target==0x23e540u ||\n           target==0x23eb50u || target==0x23cf38u || target==0x23d570u ||\n           source==0x23eb68u || source==0x23e7e4u || source==0x23e800u || source==0x23e528u;'),
      (h,'!cardTarget(target))','!cardTarget(target,source))'),
      (h,'target==0x2c5140u || target==0x2c5358u) ? entryA0','target==0x2c5140u || target==0x2c5358u || target==0x2d3810u) ? entryA0'),
      (h,'    const uint32_t ui=cardUi().load(); const bool safe=cardAddress(mc);',
         '    const uint32_t ui=cardUi().load(); const bool safe=cardAddress(mc);\n    // E13: UI flags/state and route words, guarded separately for the larger object.\n    const bool uiSafe=ui && ui<=0x02000000u-0x750u;\n    const uint32_t route=uiSafe?word(ram,ui+0x748u):0u;\n    const bool routeSafe=route && route<=0x02000000u-0x10u;'),
      (h,'slot1=%d info=%u,%u,%u,%u",','slot1=%d info=%u,%u,%u,%u uiFlags=0x%x uiState=%u uiMode=%u uiRoute=0x%x uiRouteTarget=0x%x",'),
      (h,'word(ram,0x4a3938u),word(ram,0x4a393cu),word(ram,0x4a3940u),word(ram,0x4a3944u));',
         'word(ram,0x4a3938u),word(ram,0x4a393cu),word(ram,0x4a3940u),word(ram,0x4a3944u),\n          uiSafe?word(ram,ui+0x43cu):0u,uiSafe?word(ram,ui+0x130u):0u,uiSafe?word(ram,ui+0xb8u):0u,\n          route,routeSafe?word(ram,route+0xcu):0u);'),
      (cpp,'ps2_e7::cardTarget(targetPc);','ps2_e7::cardTarget(targetPc, sourcePc);'),
    ]
    for path,old,new in changes:
        assert texts[path].count(old)==1,(path,old)
        texts[path]=texts[path].replace(old,new)
    rows=[]
    for p,text in texts.items():
        side=p.with_name('._'+p.name);side_before=side.exists();p.write_text(text)
        removed=False
        if side.exists() and not side_before:side.unlink();removed=True
        rows.append(dict(path=str(p),before=hashlib.sha256(before[p].encode()).hexdigest(),after=hashlib.sha256(text.encode()).hexdigest(),sidecar_preexisting=side_before,removed_created_sidecar=removed))
    (E/'observation-install.json').write_text(json.dumps(dict(files=rows,window='existing E7 tick<=603 byte caps',
        new_targets=['0x2d3810','0x241b20','0x241cd8','0x23e540','0x23eb50','0x23cf38','0x23d570'],
        route_sources=['0x23eb68','0x23e7e4','0x23e800','0x23e528'],ui_offsets=['0x43c','0x440','0x130','0xb8','0x748'],
        preserved_original_arguments=['a0','a1'],behavior='read-only',consumer='actual wrapper return + flag-calculator return + old/new UI flag store'),indent=2)+'\n')
    print('# E13 OBSERVATION TAIL COMPLETE; no guest state or dispatch-result mutation')
if __name__=='__main__':main()
