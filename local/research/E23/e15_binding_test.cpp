// Actual-wrapper fail-before fixture. Synthetic callbacks are NEVER called manually.
// Registration, picture request and optional callback AddBs re-entry use actual bindings.
#include "prior_binding_test.cpp"
#include "runtime/ee_scheduler.h"
#include "ps2_e15.h"

namespace e15_fixture {
constexpr uint32_t Main=0x00100040,Resume=0x00100050,Observer=0x00100060,Callback=0x00100070;
constexpr uint32_t Mpeg=0x150000,Work=0x160000,Image=0x200000,User=0x15f000,Input=0x15f100;
unsigned calls=0,noInputReturns=0,addBsCalls=0,delivered=0,resumes=0,observations=0;
bool feed=false;uint32_t resumeV0=0;R5900Context requestContext{};
std::vector<uint8_t> requestRam;
void api(PS2Runtime *r,uint8_t *ram,R5900Context *c,uint32_t target,uint32_t ra) {
    require(r->hasFunction(target),"actual MPEG wrapper missing");
    SET_GPR_U32(c,31,ra);
    r->dispatchGuestBranch(ram,c,target,Main,ra,PS2Runtime::GuestBranchKind::DirectCall,"E15 actual wrapper");
}
void requested(uint8_t *ram,R5900Context *c,PS2Runtime *r) {
    SET_GPR_U32(c,4,Mpeg);SET_GPR_U32(c,5,Image);SET_GPR_U32(c,6,0);
    SET_GPR_U32(c,31,Resume);requestContext=*c;requestRam.assign(ram,ram+PS2_RAM_SIZE);
    api(r,ram,c,0x402a10,Resume);
}
void resumed(uint8_t*,R5900Context *c,PS2Runtime *r) {
    ++resumes;resumeV0=GPR_U32(c,2);c->pc=0;r->requestStop();
}
void guestCallback(uint8_t *ram,R5900Context *c,PS2Runtime *r) {
    ++calls;
    require(GPR_U32(c,4)==Mpeg && GPR_U32(c,6)==User,"type-1 original arguments");
    const auto cb=GPR_U32(c,5);require(ps2_e15::address(cb,4),"callback-data pointer");
    require(ps2_e7::word(ram,cb)==1,"type-1 callback type word");
    const auto saved=*c;const uint32_t destination=GPR_U32(c,31);
    if(feed) {
        SET_GPR_U32(c,4,Mpeg);SET_GPR_U32(c,5,Input);SET_GPR_U32(c,6,16);
        ++addBsCalls;api(r,ram,c,0x4029d0,destination);delivered+=GPR_U32(c,2);
    } else ++noInputReturns;
    for(int i:{16,17,18,19,20,21,22,23,28,29,30})
        require(std::memcmp(&c->r[i],&saved.r[i],sizeof(c->r[i]))==0,"callback ABI preservation");
    SET_GPR_U32(c,2,0);SET_GPR_U32(c,31,destination);c->pc=destination;
}
void observed(uint8_t *ram,R5900Context *c,PS2Runtime *r) {
    ++observations;const auto *main=r->eeScheduler().thread(1);require(main,"main thread missing");
    const auto &m=main->context;
    const bool ramSame=requestRam.size()==PS2_RAM_SIZE && std::memcmp(ram,requestRam.data(),PS2_RAM_SIZE)==0;
    bool saved=true;for(int i:{16,17,18,19,20,21,22,23,28,29,30,31})saved&=std::memcmp(&m.r[i],&requestContext.r[i],sizeof(m.r[i]))==0;
    std::printf("REQUEST observer=1 mainPC=0x%x suppliedRA=0x%x sp=0x%x waitReason=%u status=%u saved128=%u ram32MiB-unchanged=%u callbacks=%u noInputReturns=%u AddBsCalls=%u delivered=%u resumed=%u\n",
        m.pc,getRegU32(&requestContext,31),getRegU32(&m,29),static_cast<unsigned>(main->wait.reason),static_cast<unsigned>(main->status),saved,ramSame,calls,noInputReturns,addBsCalls,delivered,resumes);
    require(saved,"request changed callee-saved state");
    if(calls==0) {
        require(ramSame,"undelivered picture request changed RAM");
        require(main->wait.reason==EeWaitReason::Mpeg && m.pc==Resume,"request did not reach typed MPEG wait");
    }
    c->pc=0;r->requestStop();
}
int run(bool wantsInput) {
    feed=wantsInput;PS2Runtime runtime;require(runtime.memory().initialize(),"memory init");auto *ram=runtime.memory().getRDRAM();
    for(uint32_t pc:{0x4027b8u,0x402c08u,0x402a10u,0x4029d0u,0x3b0b10u,0x3b0b40u,0x3b06b0u}) {
        require(runtime.hasFunction(pc),"actual binding absent");
        std::printf("BINDING pc=0x%x actual=%s\n",pc,symbol(runtime.lookupFunction(pc)));
    }
    for(auto pair:{std::pair<uint32_t,PS2Runtime::RecompiledFunction>{Main,requested},{Resume,resumed},{Observer,observed},{Callback,guestCallback}}) {
        require(!runtime.hasFunction(pair.first),"fixture PC conflicts with guest registry");
        require(runtime.registerFunction(pair.first,pair.second),"fixture entry registration");
    }
    R5900Context main=context(Main);SET_GPR_U32((&main),29,0x1e00000);SET_GPR_U32((&main),31,Resume);
    auto &ee=runtime.eeScheduler();ee.reset(ram,main);
    // These setup calls use the actual generated wrappers directly, with a Trace
    // around each to record original args without introducing a scheduler checkpoint.
    auto setup=[&](uint32_t pc,R5900Context &c) {
        c.pc=pc;SET_GPR_U32((&c),31,0x1f00100);
        ps2_e15::Trace trace("fixture-setup",0,ram,&c,pc,Main,1);
        runtime.lookupFunction(pc)(ram,&c,&runtime);trace.finish(0);
        require(c.pc==0x1f00100,"setup wrapper did not return to RA");
    };
    auto create=context(0x4027b8);SET_GPR_U32((&create),4,Mpeg);SET_GPR_U32((&create),5,Work);SET_GPR_U32((&create),6,0x10000);setup(0x4027b8,create);
    require(GPR_U32((&create),2)!=0,"actual Create failed");
    auto add=context(0x402c08);SET_GPR_U32((&add),4,Mpeg);SET_GPR_U32((&add),5,1);SET_GPR_U32((&add),6,Callback);SET_GPR_U32((&add),7,User);setup(0x402c08,add);
    std::printf("REGISTER type=1 function=0x%x userdata=0x%x returned=0x%x createReturn=0x%x mode=%s\n",Callback,User,GPR_U32((&add),2),GPR_U32((&create),2),feed?"input":"no-input");
    for(unsigned i=0;i<4;++i)put(ram,Input+i*4,0xb7010000u);
    const int observer=ee.createThread(EeThreadCreateParams{0,Observer,0,0,0,10,0});require(observer>1,"observer creation");
    require(ee.startThread(observer,0,main,false)==0,"observer start");ee.run();
    auto &s=ps2_e15::state();
    std::printf("DELIVERY mode=%s selections=%llu invocations=%llu callbackCalls=%u validNoInputReturns=%u AddBsCalls=%u deliveredBytes=%u resumes=%u resumeV0=%u observations=%u\n",
        feed?"input":"no-input",static_cast<unsigned long long>(s.selections),static_cast<unsigned long long>(s.invocations),calls,noInputReturns,addBsCalls,delivered,resumes,resumeV0,observations);
    const bool expected=calls>0 && (feed?(addBsCalls>0 && delivered==16):noInputReturns>0);
    std::printf("E15 ACTUAL WRAPPER FIXTURE TAIL COMPLETE expectedDelivery=%u result=%s boot=0 manualCallbackCalls=0\n",expected,expected?"PASS":"FAIL-BEFORE");
    return expected?0:1;
}
}
extern "C" int e15_binding_main(int argc,char **argv) {
    if(argc==2 && std::string(argv[1])=="prior") {char mode[]="present";char *args[]={argv[0],mode,nullptr};return e13_binding_main(2,args);}
    try {
        require(argc==2,"mode required: no-input or input");
        require(std::string(argv[1])=="input" || std::string(argv[1])=="no-input","unknown fixture mode");
        return e15_fixture::run(std::string(argv[1])=="input");
    } catch(const std::exception &e) {std::fprintf(stderr,"E15 FIXTURE ERROR: %s\n",e.what());return 2;}
}
