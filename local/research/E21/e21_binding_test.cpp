// Q1 only: feed labeled authored data through the actual AddBs generated wrapper.
// No ELF is loaded and no guest callback is replaced or manually invoked.
#include "e18_binding_test.cpp"
#include "e21_parser_observer.h"
#include <algorithm>

namespace e21_threshold {
int run(const char *path,bool bytewise) {
    std::ifstream f(path,std::ios::binary);
    std::vector<uint8_t> payload((std::istreambuf_iterator<char>(f)),{});
    require(payload.size()>=16384 && payload.size()<=65536,"labeled payload bounds");
    auto snapshot=reinterpret_cast<E21Snapshot>(dlsym(RTLD_DEFAULT,"e21_parser_snapshot"));
    auto mark=reinterpret_cast<E21Mark>(dlsym(RTLD_DEFAULT,"e21_parser_mark"));
    require(snapshot && mark,"real parser observer absent");
    PS2Runtime runtime;require(runtime.memory().initialize(),"threshold memory init");
    auto *ram=runtime.memory().getRDRAM();
    auto call=[&](uint32_t pc,uint32_t a1,uint32_t a2) {
        auto c=context(pc);SET_GPR_U32((&c),4,e15_fixture::Mpeg);SET_GPR_U32((&c),5,a1);SET_GPR_U32((&c),6,a2);
        SET_GPR_U32((&c),31,0x1f00100);const auto before=c;
        require(runtime.hasFunction(pc),"actual MPEG wrapper absent");
        runtime.lookupFunction(pc)(ram,&c,&runtime);
        require(c.pc==0x1f00100,"wrapper did not return to RA");
        for(int reg:{16,17,18,19,20,21,22,23,28,29,30,31})
            require(std::memcmp(&c.r[reg],&before.r[reg],sizeof(c.r[reg]))==0,"wrapper saved128 changed");
        return GPR_U32((&c),2);
    };
    require(call(0x4027b8,e15_fixture::Work,0x10000)!=0,"actual Create failed");
    uint64_t firstPacket=0,firstFrame=0,addBsCalls=0;
    size_t cursor=0;E21ParserStats last{};
    std::vector<size_t> marks={64,5040,8192,16384};
    if(payload.size()>16384)marks.push_back(payload.size());
    for(size_t end:marks) {
        while(cursor<end) {
            size_t chunk=bytewise && cursor>=64?1:end-cursor;
            std::memcpy(ram+e15_fixture::Input,payload.data()+cursor,chunk);
            uint32_t accepted=call(0x4029d0,e15_fixture::Input,static_cast<uint32_t>(chunk));
            require(accepted==chunk,"actual AddBs did not accept authored slice");
            cursor+=chunk;++addBsCalls;snapshot(&last);
            require(last.pending==0 && !last.textTruncated && !last.payloadTruncated && !last.ioErrors && !last.errors,"parser observation error");
            if(!firstPacket && last.packets)firstPacket=cursor;
            if(!firstFrame && last.frames)firstFrame=cursor;
            if(bytewise && firstPacket)break;
        }
        mark("cumulative",cursor);
        std::printf("THRESHOLD mode=%s bytes=%zu AddBsCalls=%llu consumed=%llu parserCalls=%llu packets=%llu frames=%llu firstPacketAtFed=%llu firstFrameAtFed=%llu eofSends=%llu\n",
            bytewise?"byte":"marks",cursor,(unsigned long long)addBsCalls,(unsigned long long)last.consumed,
            (unsigned long long)last.parseCalls,(unsigned long long)last.packets,(unsigned long long)last.frames,
            (unsigned long long)firstPacket,(unsigned long long)firstFrame,(unsigned long long)last.sendEof);
        if(bytewise && firstPacket)break;
    }
    require(last.parseCalls>0 && last.sendEof==0,"no actual parser calls or invented EOF");
    std::printf("# E21 ACTUAL PARSER FIXTURE TAIL COMPLETE boot=0 bytesFed=%zu available=%zu mode=%s saved128=1\n",cursor,payload.size(),bytewise?"byte":"marks");
    return 0;
}
}
extern "C" int e21_binding_main(int argc,char **argv) {
    try {
        if(argc==4 && std::string(argv[1])=="threshold")
            return e21_threshold::run(argv[2],std::string(argv[3])=="byte");
        return e18_binding_main(argc,argv);
    }catch(const std::exception &e) {std::fprintf(stderr,"E21 FIXTURE ERROR: %s\n",e.what());return 2;}
}
