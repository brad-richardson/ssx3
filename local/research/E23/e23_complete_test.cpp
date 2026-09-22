// E23: complete-feed demand-cadence reference on the ACTUAL title wrappers.
// Same shape as the E15 actual-wrapper fixture, but the type-1 callback feeds a
// prefix of the R3 authored payload instead of 16 marker bytes, so the SAME
// registration/dispatch/AddBs/retry path can be observed on a feed that
// SUFFICES. No ELF is loaded, no callback is invoked manually, no policy added.
#include "e21_binding_test.cpp"
#include "e23_payload.inc"

namespace e23_complete {
using e15_fixture::Main; using e15_fixture::Resume; using e15_fixture::Observer;
using e15_fixture::Callback; using e15_fixture::Mpeg; using e15_fixture::Work;
using e15_fixture::Image; using e15_fixture::User; using e15_fixture::Input;

unsigned feedBytes=0,calls=0,addBsCalls=0,delivered=0,resumes=0,observations=0;
unsigned parked=0;
int resumeV0=0;
uint32_t width=0,height=0,pixel=0;
R5900Context requestContext{};

void requested(uint8_t *ram,R5900Context *c,PS2Runtime *r) {
    SET_GPR_U32(c,4,Mpeg);SET_GPR_U32(c,5,Image);SET_GPR_U32(c,6,0);
    SET_GPR_U32(c,31,Resume);requestContext=*c;
    e15_fixture::api(r,ram,c,0x402a10,Resume);
}
void resumed(uint8_t *ram,R5900Context *c,PS2Runtime *r) {
    ++resumes;resumeV0=static_cast<int>(GPR_U32(c,2));
    for(int i:{16,17,18,19,20,21,22,23,28,29,30,31})
        require(std::memcmp(&c->r[i],&requestContext.r[i],sizeof(c->r[i]))==0,"owner saved128 changed");
    width=ps2_e7::word(ram,Mpeg);height=ps2_e7::word(ram,Mpeg+4);pixel=ps2_e7::word(ram,Image);
    c->pc=0;r->requestStop();
}
// The registered type-1 producer. Feeds through the ACTUAL AddBs wrapper.
void guestCallback(uint8_t *ram,R5900Context *c,PS2Runtime *r) {
    ++calls;
    require(GPR_U32(c,4)==Mpeg && GPR_U32(c,6)==User,"type-1 original arguments");
    const auto cb=GPR_U32(c,5);require(ps2_e15::address(cb,4),"callback-data pointer");
    require(ps2_e7::word(ram,cb)==1,"type-1 callback type word");
    const auto saved=*c;const uint32_t destination=GPR_U32(c,31);
    SET_GPR_U32(c,4,Mpeg);SET_GPR_U32(c,5,Input);SET_GPR_U32(c,6,feedBytes);
    ++addBsCalls;e15_fixture::api(r,ram,c,0x4029d0,destination);delivered+=GPR_U32(c,2);
    for(int i:{16,17,18,19,20,21,22,23,28,29,30})
        require(std::memcmp(&c->r[i],&saved.r[i],sizeof(c->r[i]))==0,"callback ABI preservation");
    SET_GPR_U32(c,2,0);SET_GPR_U32(c,31,destination);c->pc=destination;
}
void observed(uint8_t*,R5900Context *c,PS2Runtime *r) {
    ++observations;const auto *main=r->eeScheduler().thread(1);require(main,"main thread missing");
    const bool waiting=main->wait.reason==EeWaitReason::Mpeg;
    parked+=waiting?1u:0u;
    std::printf("OBSERVE mainPC=0x%x waitReason=%u parked=%u callbacks=%u delivered=%u resumes=%u\n",
        main->context.pc,static_cast<unsigned>(main->wait.reason),waiting,calls,delivered,resumes);
    c->pc=0;
    // Only the stalled shape needs the observer to end the run; a served
    // picture ends it from its own resume, so never cut that short.
    if(waiting && resumes==0) r->requestStop();
}
int run(unsigned bytes) {
    require(bytes>0 && bytes<=sizeof(kE23CompletePayload),"feed size outside authored payload");
    feedBytes=bytes;
    PS2Runtime runtime;require(runtime.memory().initialize(),"memory init");
    auto *ram=runtime.memory().getRDRAM();
    for(uint32_t pc:{0x4027b8u,0x402c08u,0x402a10u,0x4029d0u,0x3b0b10u,0x3b0b40u,0x3b06b0u}) {
        require(runtime.hasFunction(pc),"actual binding absent");
        std::printf("BINDING pc=0x%x actual=%s\n",pc,symbol(runtime.lookupFunction(pc)));
    }
    for(auto pair:{std::pair<uint32_t,PS2Runtime::RecompiledFunction>{Main,requested},{Resume,resumed},
                   {Observer,observed},{Callback,guestCallback}}) {
        require(!runtime.hasFunction(pair.first),"fixture PC conflicts with guest registry");
        require(runtime.registerFunction(pair.first,pair.second),"fixture entry registration");
    }
    R5900Context main=context(Main);SET_GPR_U32((&main),29,0x1e00000);SET_GPR_U32((&main),31,Resume);
    auto &ee=runtime.eeScheduler();ee.reset(ram,main);
    auto setup=[&](uint32_t pc,R5900Context &c) {
        c.pc=pc;SET_GPR_U32((&c),31,0x1f00100);
        ps2_e15::Trace trace("fixture-setup",0,ram,&c,pc,Main,1);
        runtime.lookupFunction(pc)(ram,&c,&runtime);trace.finish(0);
        require(c.pc==0x1f00100,"setup wrapper did not return to RA");
    };
    auto create=context(0x4027b8);SET_GPR_U32((&create),4,Mpeg);SET_GPR_U32((&create),5,Work);
    SET_GPR_U32((&create),6,0x10000);setup(0x4027b8,create);
    require(GPR_U32((&create),2)!=0,"actual Create failed");
    auto add=context(0x402c08);SET_GPR_U32((&add),4,Mpeg);SET_GPR_U32((&add),5,1);
    SET_GPR_U32((&add),6,Callback);SET_GPR_U32((&add),7,User);setup(0x402c08,add);
    std::printf("REGISTER type=1 function=0x%x userdata=0x%x returned=0x%x createReturn=0x%x feedBytes=%u\n",
        Callback,User,GPR_U32((&add),2),GPR_U32((&create),2),feedBytes);
    std::memcpy(ram+Input,kE23CompletePayload,feedBytes);
    const int observer=ee.createThread(EeThreadCreateParams{0,Observer,0,0,0,10,0});
    require(observer>1,"observer creation");
    require(ee.startThread(observer,0,main,false)==0,"observer start");
    ee.run();
    auto &s=ps2_e15::state();
    std::printf("CADENCE feedBytes=%u selections=%llu invocations=%llu callbackCalls=%u AddBsCalls=%u "
        "deliveredBytes=%u resumes=%u resumeV0=%d parked=%u observations=%u width=%u height=%u pixel=0x%x\n",
        feedBytes,static_cast<unsigned long long>(s.selections),static_cast<unsigned long long>(s.invocations),
        calls,addBsCalls,delivered,resumes,resumeV0,parked,observations,width,height,pixel);
    // One registered producer: the reference cadence is one dispatch per request.
    const bool served=resumes==1 && resumeV0==0 && width==16 && height==16 && pixel!=0;
    const bool stalled=resumes==0 && parked>0;
    require(calls==1 && addBsCalls==1 && delivered==feedBytes,"one dispatch, one AddBs, all bytes accepted");
    require(served!=stalled,"run must either serve a picture or stall parked, not both");
    std::printf("# E23 COMPLETE FEED FIXTURE TAIL COMPLETE boot=0 feedBytes=%u outcome=%s "
        "producerFirings=%u saved128=1 manualCallbackCalls=0\n",
        feedBytes,served?"SERVED":"STALLED",calls);
    return 0;
}
}
extern "C" int e23_binding_main(int argc,char **argv) {
    try {
        if(argc==3 && std::string(argv[1])=="complete")
            return e23_complete::run(static_cast<unsigned>(std::stoul(argv[2],nullptr,0)));
        return e21_binding_main(argc,argv);
    }catch(const std::exception &e){std::fprintf(stderr,"E23 FIXTURE ERROR: %s\n",e.what());return 2;}
}
