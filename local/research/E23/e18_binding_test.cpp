// Actual-runner ownership audit plus unchanged E17/E16/E15 binding fixtures.
#include "e17_binding_test.cpp"

namespace e18_ownership {
constexpr uint32_t Main=e15_fixture::Main, Resume=e15_fixture::Resume, Callback=e15_fixture::Callback;
bool direct=false,park=false;
int caller=0,observed=0;
uint32_t callerSp=0,observedSp=0;
unsigned calls=0,completions=0,resumes=0;
R5900Context parentBefore{};
void callback(uint8_t*,R5900Context *c,PS2Runtime *r) {
    ++calls;observed=r->eeScheduler().currentThreadId();observedSp=GPR_U32(c,29);
    require(GPR_U32(c,4)==0x150000 && GPR_U32(c,5)==0x151000 && GPR_U32(c,6)==0x152000,"copied invocation args");
    c->r[16]=_mm_set_epi64x(0x1122334455667788LL,0x8877665544332211ULL);
    SET_GPR_U32(c,2,0xfedcba98);c->pc=0;
}
void main(uint8_t*,R5900Context *c,PS2Runtime *r) {
    auto &ee=r->eeScheduler();caller=ee.currentThreadId();callerSp=GPR_U32(c,29);
    c->pc=Resume;parentBefore=*c;
    GuestInvocation invocation{};invocation.kind=direct?GuestInvocationKind::HleCall:GuestInvocationKind::RpcCallback;
    invocation.context=*c;invocation.context.pc=Callback;
    SET_GPR_U32(&invocation.context,4,0x150000);SET_GPR_U32(&invocation.context,5,0x151000);SET_GPR_U32(&invocation.context,6,0x152000);
    if(!direct)SET_GPR_U32(&invocation.context,29,0);
    SET_GPR_U32(&invocation.context,31,0);
    invocation.onComplete=[r](const R5900Context&,R5900Context &parent) {
        ++completions;
        if(direct)require(std::memcmp(&parent,&parentBefore,sizeof(parent))==0,"current invocation did not restore full parent context");
        if(park)r->eeScheduler().completeExternalWait(0xe18,0xe18,0);
    };
    if(direct)ee.invokeCurrent(std::move(invocation));
    ee.queueInvocation(std::move(invocation));
    if(park)ee.waitExternal(EeWaitReason::External,0xe18,0xe18);
}
void resume(uint8_t*,R5900Context *c,PS2Runtime *r) {
    ++resumes;
    for(int reg:{16,17,18,19,20,21,22,23,28,29,30,31})
        require(std::memcmp(&c->r[reg],&parentBefore.r[reg],sizeof(c->r[reg]))==0,"owner saved128 changed");
    c->pc=0;r->requestStop();
}
int run(const std::string &mode) {
    direct=mode=="ownership-current";park=mode=="ownership-queued-park";
    PS2Runtime r;require(r.memory().initialize(),"ownership memory init");auto *ram=r.memory().getRDRAM();
    for(auto pair:{std::pair<uint32_t,PS2Runtime::RecompiledFunction>{Main,main},{Resume,resume},{Callback,callback}}) {
        require(!r.hasFunction(pair.first),"ownership fixture PC occupied");require(r.registerFunction(pair.first,pair.second),"ownership fixture registration");
    }
    auto c=context(Main);SET_GPR_U32(&c,29,0x1e00000);SET_GPR_U32(&c,31,Resume);
    r.eeScheduler().reset(ram,c);r.eeScheduler().run();
    require(calls==1 && completions==1 && resumes==1,"ownership control flow");
    if(direct)require(observed==caller && observedSp==callerSp,"current ownership mismatch");
    else require(observedSp!=callerSp,"queue stack should show different ownership shape");
    if(park)require(observed<0 && observed!=caller,"parked queue owner should be synthetic");
    std::printf("OWNERSHIP mode=%s callerTid=%d callbackTid=%d callerSP=0x%x callbackSP=0x%x sameThread=%u sameStack=%u args=1 saved128=1 callbacks=%u completions=%u resumes=%u\n",
        mode.c_str(),caller,observed,callerSp,observedSp,caller==observed,callerSp==observedSp,calls,completions,resumes);
    std::puts("# E18 OWNERSHIP FIXTURE TAIL COMPLETE boot=0");return 0;
}
}
extern "C" int e18_binding_main(int argc,char **argv) {
    try {
        if(argc==2 && std::string(argv[1]).starts_with("ownership-"))return e18_ownership::run(argv[1]);
        return e17_binding_main(argc,argv);
    }catch(const std::exception &e){std::fprintf(stderr,"E18 FIXTURE ERROR: %s\n",e.what());return 2;}
}
