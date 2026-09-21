// Isolated entry tests linked with the ACTUAL runner objects and registry.
// No ELF boot, GUI, scheduler run, query replacement or handwritten guest body.
#include "ps2_runtime.h"
#include "ps2_runtime_macros.h"
#include <array>
#include <cstdio>
#include <cstring>
#include <stdexcept>
#include <string>
#include <vector>
#include <dlfcn.h>

static unsigned getInfoCalls=0;
static void unexpectedGetInfo(uint8_t*,R5900Context*,PS2Runtime*) {
    ++getInfoCalls; throw std::runtime_error("query called sceMcGetInfo");
}
static void require(bool yes,const char* name) {
    if (!yes) throw std::runtime_error(name);
}
static void put(uint8_t* ram,uint32_t addr,uint32_t value) { std::memcpy(ram+addr,&value,4); }
static const char* symbol(PS2Runtime::RecompiledFunction f) {
    Dl_info i{}; return dladdr(reinterpret_cast<void*>(f),&i) && i.dli_sname ? i.dli_sname : "unavailable";
}
static R5900Context context(uint32_t pc) {
    R5900Context c{};
    for (unsigned i=1;i<32;++i)c.r[i]=_mm_set_epi32(0x12340000+i,0x56780000+i,0x1234+i,0x4321+i);
    SET_GPR_U32((&c),29,0x100000); SET_GPR_U32((&c),31,0xf00000);
    SET_GPR_U32((&c),4,0x200000); c.pc=pc; return c;
}
extern "C" int e12_binding_main(int argc,char** argv) {
    try {
        const bool expected=argc==2 && std::string(argv[1])=="present";
        PS2Runtime runtime; require(runtime.memory().initialize(),"memory init");
        auto* ram=runtime.memory().getRDRAM();
        require(runtime.hasFunction(0x426230),"DROP handler absent");
        auto handler=runtime.lookupFunction(0x426230);
        auto h=context(0x426230); const auto original=h;
        put(ram,0x52bcd8,0x210000); ram[0x210000]=0; // Empty SDK command buffer.
        handler(ram,&h,&runtime);
        require(h.pc==0xf00000,"DROP handler did not return to RA");
        require(GPR_U32((&h),29)==0x100000,"DROP handler SP changed");
        require(GPR_U64((&h),16)==GPR_U64((&original),16),"DROP handler s0 changed");
        require(GPR_U32((&h),2)==0,"DROP empty-buffer result");
        std::printf("DROP actual-binding=%s pc=0x%x sp=0x%x v0=%u s0-preserved=1 normal-return=1\n",symbol(handler),h.pc,GPR_U32((&h),29),GPR_U32((&h),2));
        require(!runtime.hasFunction(0x2c5358),"out-of-scope sibling was registered");
        const bool found=runtime.hasFunction(0x2c5140);
        std::printf("QUERY hasFunction=%u expected=1\n",found);
        require(found,"busy query regression: entry absent");
        if (found) {
            auto fn=runtime.lookupFunction(0x2c5140);
            std::printf("QUERY actual-binding=%s\n",symbol(fn));
            auto old=runtime.lookupFunction(0x40a498);
            require(old!=nullptr,"GetInfo spy anchor absent");
            require(runtime.replaceFunction(0x40a498,unexpectedGetInfo),"GetInfo spy install");
            for (auto pair: {std::array<uint32_t,2>{0,0},{1,0},{0,1},{1,1}}) {
                put(ram,0x200000,0x486f78); put(ram,0x200004,pair[0]); put(ram,0x200040,pair[1]);
                std::vector<uint8_t> before(ram,ram+PS2_RAM_SIZE);
                auto c=context(0x2c5140); const auto saved=c;
                fn(ram,&c,&runtime);
                require(c.pc==0xf00000,"query did not return to supplied RA");
                require(GPR_U32((&c),29)==0x100000,"query SP changed");
                require(GPR_U32((&c),2)==(pair[0]||pair[1]),"query truth table");
                for(int i:{16,17,18,19,20,21,22,23,28,29,30,31})
                    require(std::memcmp(&c.r[i],&saved.r[i],sizeof(c.r[i]))==0,"query callee-save changed");
                require(std::memcmp(before.data(),ram,PS2_RAM_SIZE)==0,"query guest memory changed");
                require(getInfoCalls==0,"query called GetInfo");
                std::printf("QUERY state=%u outstanding=%u v0=%u pc=0x%x sp=0x%x saved128=1 ram32MiB-unchanged=1 GetInfoCalls=%u\n",pair[0],pair[1],GPR_U32((&c),2),c.pc,GPR_U32((&c),29),getInfoCalls);
            }
            require(runtime.replaceFunction(0x40a498,old),"GetInfo spy restore");
        }
        const bool predicateFound=runtime.hasFunction(0x2c5300);
        std::printf("PREDICATE hasFunction=%u expected=%u sibling5358=0\n",predicateFound,expected);
        require(predicateFound==expected,"predicate entry presence differs");
        if (predicateFound) {
            auto fn=runtime.lookupFunction(0x2c5300);
            std::printf("PREDICATE actual-binding=%s\n",symbol(fn));
            auto oldInfo=runtime.lookupFunction(0x40a498);
            auto oldSync=runtime.lookupFunction(0x40a360);
            require(oldInfo && oldSync,"API spy anchors absent");
            require(runtime.replaceFunction(0x40a498,unexpectedGetInfo),"GetInfo spy install");
            require(runtime.replaceFunction(0x40a360,unexpectedGetInfo),"Sync spy install");
            for (unsigned port: {0u,1u}) {
                for (auto pair: {std::array<int32_t,2>{-10002,0},{0,0},{1,0},{-10001,0},{-7,0},{0,-10002},{-10002,-10002}}) {
                    put(ram,0x200000,0x486f78);
                    put(ram,0x200184+port*0x14,static_cast<uint32_t>(pair[0]));
                    put(ram,0x200184+(1-port)*0x14,static_cast<uint32_t>(pair[1]));
                    std::vector<uint8_t> before(ram,ram+PS2_RAM_SIZE);
                    auto c=context(0x2c5300);SET_GPR_U32((&c),5,port);const auto saved=c;
                    fn(ram,&c,&runtime);
                    require(c.pc==0xf00000,"predicate did not return to supplied RA");
                    require(GPR_U32((&c),29)==0x100000,"predicate SP changed");
                    require(GPR_U32((&c),2)==static_cast<uint32_t>(pair[0]==-10002),"predicate truth/indexing");
                    for(int i:{16,17,18,19,20,21,22,23,28,29,30,31})
                        require(std::memcmp(&c.r[i],&saved.r[i],sizeof(c.r[i]))==0,"predicate callee-save changed");
                    require(std::memcmp(before.data(),ram,PS2_RAM_SIZE)==0,"predicate guest memory changed");
                    require(getInfoCalls==0,"predicate called memory-card API");
                    std::printf("PREDICATE port=%u selected=%d other=%d v0=%u pc=0x%x sp=0x%x saved128=1 ram32MiB-unchanged=1 GetInfoSyncCalls=%u\n",port,pair[0],pair[1],GPR_U32((&c),2),c.pc,GPR_U32((&c),29),getInfoCalls);
                }
            }
            require(runtime.replaceFunction(0x40a498,oldInfo),"GetInfo spy restore");
            require(runtime.replaceFunction(0x40a360,oldSync),"Sync spy restore");
        }
        std::puts("E12 ACTUAL BINDING TEST COMPLETE success=1 boot=0"); return 0;
    } catch(const std::exception& e) {
        std::fprintf(stderr,"E12 ACTUAL BINDING TEST FAILURE: %s\n",e.what()); return 1;
    }
}
