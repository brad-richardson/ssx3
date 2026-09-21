#!/usr/bin/env python3
"""Install the named E15 read-only observation extension; no generated/MPEG edits."""
import os
from pathlib import Path
R=Path('/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp/ps2xRuntime')
E=Path(__file__).resolve().parent
def change(path,old,new):
    p=R/path;s=p.read_text()
    if new in s: return
    if old.startswith('    std::sort(completed.begin()'):
        start=s.index('void EeScheduler::completeExternalWait(')
        prefix,s=s[:start],s[start:]
    else: prefix=''
    assert s.count(old)==1,(path,old[:80],s.count(old));p.write_text(prefix+s.replace(old,new))
def main():
    assert os.environ.get('COPYFILE_DISABLE')=='1'
    change('include/ps2_e7.h','inline bool window(uint64_t tick) { return tick >= 599u && tick <= 603u; }', '''// E15 opt-in alignment uses only diagnostic atomics; no guest writes.
inline bool aligned() { static const bool yes = [] { const char *p=std::getenv("PS2X_E15_ALIGN"); return p && std::strcmp(p,"1")==0; }(); return yes; }
inline std::atomic<uint64_t> &alignedArm() { static std::atomic<uint64_t> value{UINT64_MAX}; return value; }
inline bool window(uint64_t tick) {
    const uint64_t a=alignedArm().load();
    return aligned() ? (a!=UINT64_MAX && tick>=a && tick<=a+1u) : (tick>=599u && tick<=603u);
}''')
    change('include/ps2_e7.h','boundary 599..603; byte caps','boundary 599..603 unless E15 aligned trigger; byte caps')
    change('include/ps2_e7.h','bool opened = false, finished = false, packetTruncated = false;','bool opened = false, finished = false, closed = false, packetTruncated = false;')
    change('include/ps2_e7.h','if (!s.file || s.finished) return;','if (!s.file || s.finished || s.closed) return;')
    change('include/ps2_e7.h','inline void packet(uint64_t tick,', '''inline void shutdown(uint64_t tick)
{
    if (!enabled()) return;
    Sink &s=sink(); std::lock_guard<std::mutex> lock(s.mutex);
    if (!s.file || s.closed) return;
    std::fprintf(s.file,"# E7 SHUTDOWN tick=%llu events=%llu bootBytes=%llu boundaryBytes=%llu packetBytes=%llu packetFiles=%llu bootTruncated=%d boundaryTruncated=%d packetTruncated=%d windowComplete=%d aligned=%d arm=%llu\\n",
        static_cast<unsigned long long>(tick),static_cast<unsigned long long>(s.seq),
        static_cast<unsigned long long>(s.budget.boot),static_cast<unsigned long long>(s.budget.boundary),
        static_cast<unsigned long long>(s.packetBytes),static_cast<unsigned long long>(s.packets),
        s.budget.bootTruncated,s.budget.boundaryTruncated,s.packetTruncated,s.finished,aligned(),
        static_cast<unsigned long long>(alignedArm().load()));
    std::fflush(s.file); std::fclose(s.file); s.file=nullptr; s.closed=true;
}
inline void packet(uint64_t tick,''')
    change('include/ps2_e7.h','if (size > kPacketBytes - s.packetBytes) { s.packetTruncated = true; return; }','if (size > kPacketBytes - s.packetBytes || (aligned() && s.packets>=16u)) { s.packetTruncated = true; return; }')
    change('include/ps2_e7.h','const uint32_t ui=cardUi().load();\n    const uint32_t off=address-mc;', '''const uint32_t ui=cardUi().load();
    if (aligned() && ui && cardAddress(ui) && cardAddress(mc) && word(ram,mc)==0x486f78u &&
        word(ram,ui+0x434u)==mc && address==ui+0x130u && width==4u &&
        word(ram,address)==3u && lo==6u)
    {
        uint64_t unset=UINT64_MAX;
        if (alignedArm().compare_exchange_strong(unset,tick+1u))
            event(tick,"e15-align","UI=0x%x MC=0x%x old=3 new=6 pc=0x%x arm=%llu freeze=%llu guard=1",
                ui,mc,pc,static_cast<unsigned long long>(tick+1u),static_cast<unsigned long long>(tick+2u));
    }
    const uint32_t off=address-mc;''')
    change('include/ps2_e4.h','#include "runtime/gs/gs_frontend.h"','#include "ps2_e7.h"\n#include "runtime/gs/gs_frontend.h"')
    change('include/ps2_e4.h','inline uint64_t armTickRaw()\n{','inline uint64_t armTickRaw()\n{\n    if (ps2_e7::aligned()) return ps2_e7::alignedArm().load();')
    change('include/ps2_e4.h','inline uint64_t freezeTickRaw()\n{','inline uint64_t freezeTickRaw()\n{\n    if (ps2_e7::aligned()) { const auto a=armTickRaw(); return a==kNoTick ? kNoTick : a+1u; }')
    (R/'include/ps2_e15.h').write_text((E/'ps2_e15.h').read_text())
    change('src/lib/ps2_runtime.cpp','#include "ps2_e7.h"','#include "ps2_e7.h"\n#include "ps2_e15.h"')
    change('src/lib/ps2_runtime.cpp','    noteCardCall("mc-call");\n    targetFn(rdram, ctx, this);\n    noteCardCall("mc-return");','''    noteCardCall("mc-call");
    ps2_e15::Trace mpegTrace("branch",m_memory.gs().vsyncTick.load(),rdram,ctx,targetPc,sourcePc,
                            g_diagWatchThreadId.load(std::memory_order_relaxed));
    targetFn(rdram, ctx, this);
    mpegTrace.finish(m_memory.gs().vsyncTick.load());
    noteCardCall("mc-return");''')
    change('src/lib/ps2_runtime.cpp','        std::cerr << "[~PS2Runtime] cleanup exception: unknown" << std::endl;\n    }\n}', '''        std::cerr << "[~PS2Runtime] cleanup exception: unknown" << std::endl;
    }
    ps2_e15::closure(m_memory.gs().vsyncTick.load());
    ps2_e7::shutdown(m_memory.gs().vsyncTick.load());
}''')
    change('src/lib/Kernel/EeScheduler.cpp','#include "ps2_e4.h"','#include "ps2_e4.h"\n#include "ps2_e15.h"')
    change('src/lib/Kernel/EeScheduler.cpp','            function(m_rdram, &context, &m_runtime);','''            ps2_e15::Trace mpegTrace("scheduler",m_vsyncTick,m_rdram,&context,context.pc,0u,m_currentThreadId);
            function(m_rdram, &context, &m_runtime);
            mpegTrace.finish(m_vsyncTick);''')
    change('src/lib/Kernel/EeScheduler.cpp','void EeScheduler::queueInvocation(GuestInvocation invocation)\n{\n    assertExecutor();','''void EeScheduler::queueInvocation(GuestInvocation invocation)
{
    assertExecutor();
    ps2_e15::selection(m_vsyncTick,"queue",invocation.context.pc,&invocation.context,m_currentThreadId);''')
    change('src/lib/Kernel/EeScheduler.cpp','[[noreturn]] void EeScheduler::invokeCurrent(GuestInvocation invocation)\n{\n    assertExecutor();','''[[noreturn]] void EeScheduler::invokeCurrent(GuestInvocation invocation)
{
    assertExecutor();
    ps2_e15::selection(m_vsyncTick,"direct",invocation.context.pc,&invocation.context,m_currentThreadId);''')
    change('src/lib/Kernel/EeScheduler.cpp','    for (auto it = invocations.rbegin(); it != invocations.rend(); ++it)\n    {','''    for (auto it = invocations.rbegin(); it != invocations.rend(); ++it)
    {
        ps2_e15::selection(m_vsyncTick,"sequence",it->context.pc,&it->context,m_currentThreadId);''')
    change('src/lib/Kernel/EeScheduler.cpp','    std::sort(completed.begin(), completed.end());\n    for (const int id : completed)','''    std::sort(completed.begin(), completed.end());
    if (ps2_e15::enabled() && type==1u)
        ps2_e7::event(m_vsyncTick,"mpeg-complete","type=%u token=0x%llx result=%d matched=%zu thread=%d",
            type,static_cast<unsigned long long>(token),result,completed.size(),m_currentThreadId);
    for (const int id : completed)''')
    change('src/lib/Kernel/EeScheduler.cpp','    EeWaitState wait{reason, EeExternalWait{type, token}, std::move(completion)};', '''    if (ps2_e15::enabled() && reason==EeWaitReason::Mpeg)
    {
        const auto *c=currentContext();
        ps2_e7::event(m_vsyncTick,"mpeg-wait","type=%u token=0x%llx thread=%d pc=0x%x ra=0x%x sp=0x%x reason=%u",
            type,static_cast<unsigned long long>(token),m_currentThreadId,c?c->pc:0u,
            c?getRegU32(c,31):0u,c?getRegU32(c,29):0u,static_cast<unsigned>(reason));
    }
    EeWaitState wait{reason, EeExternalWait{type, token}, std::move(completion)};''')
    change('src/lib/ps2_runtime.cpp','    const bool keep = fallback ? (s_fallbackKeep++ < 2u) : (s_successKeep++ < 2u);',(E/'aligned-upload.patch').read_text().rstrip('\n'))
    print('E15 TAP INSTALL TAIL COMPLETE; five named files, no MPEG/generated edits')
if __name__=='__main__': main()
