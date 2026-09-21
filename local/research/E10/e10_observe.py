#!/usr/bin/env python3
"""Install E10's bounded read-only extension of the existing E7 sink."""
import os
from pathlib import Path
E=Path(__file__).resolve().parent
R=Path('/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp')
def main():
    assert os.environ.get('COPYFILE_DISABLE')=='1'
    header=R/'ps2xRuntime/include/ps2_e7.h';s=header.read_text();assert 'cardObject()' not in s
    s=s.replace('#include <cstdarg>','#include <atomic>\n#include <cstdarg>')
    anchor='inline void fields(uint64_t tick,';assert s.count(anchor)==1
    s=s.replace(anchor,(E/'e10_card_observe.inc').read_text()+'\n'+anchor)
    anchor='    if (!enabled() || !ram) return;\n    const uint32_t s = word(ram, 0x4a289cu);';assert s.count(anchor)==1
    s=s.replace(anchor,'    if (!enabled() || !ram) return;\n    cardWrite(tick, ram, address, width, lo, pc, thread);\n    const uint32_t s = word(ram, 0x4a289cu);')
    header.write_text(s)
    source=R/'ps2xRuntime/src/lib/ps2_runtime.cpp';s=source.read_text()
    anchor='    const uint32_t entryPc = ctx->pc;\n    targetFn(rdram, ctx, this);';assert s.count(anchor)==1
    replacement='''    const uint32_t entryPc = ctx->pc;
    // E10: preserve entry a0 across the call for dynamic query-object joins.
    // Observation only, sharing the existing E7 window and byte budgets.
    const bool cardObservation = ps2_e7::enabled() && ps2_e7::cardTarget(targetPc);
    const uint32_t cardA0 = cardObservation ? getRegU32(ctx, 4) : 0u;
    auto noteCardCall = [&](const char *phase) {
        if (cardObservation)
            ps2_e7::cardCall(m_memory.gs().vsyncTick.load(), phase, rdram,
                targetPc, sourcePc, cardA0, ctx->pc, getRegU32(ctx, 2),
                getRegU32(ctx, 5), getRegU32(ctx, 6), getRegU32(ctx, 7),
                getRegU32(ctx, 29), getRegU32(ctx, 31),
                g_diagWatchThreadId.load(std::memory_order_relaxed));
    };
    noteCardCall("mc-call");
    targetFn(rdram, ctx, this);
    noteCardCall("mc-return");'''
    s=s.replace(anchor,replacement)
    anchor='    const MissingFunctionPolicy policy = missingFunctionPolicy();\n    const bool firstReport ='
    assert s.count(anchor)==1
    s=s.replace(anchor,'''    // E10: retain inputs to the already-reached sibling residual; no dispatch or result change.
    if (ps2_e7::enabled() && targetPc == 0x2c5358u)
        ps2_e7::cardCall(m_memory.gs().vsyncTick.load(), "mc-missing", rdram,
            targetPc, sourcePc, getRegU32(ctx,4), ctx->pc, getRegU32(ctx,2),
            getRegU32(ctx,5), getRegU32(ctx,6), getRegU32(ctx,7),
            getRegU32(ctx,29), getRegU32(ctx,31),
            g_diagWatchThreadId.load(std::memory_order_relaxed));
'''+anchor)
    source.write_text(s)
    # Byte writes can still create provenance sidecars on ExFAT. Keep them out
    # of source globs; touch only the metadata companions of these two edits.
    for edited in [header,source]:
        side=edited.with_name('._'+edited.name)
        if side.exists():side.unlink()
    print('# E10 observation extension installed; no generated source mutation')
if __name__=='__main__':main()
