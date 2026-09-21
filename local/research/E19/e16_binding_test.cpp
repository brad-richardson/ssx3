// Linked with all actual runner objects and registry. No ELF is loaded.
// The forcing case inspects PS2Runtime::run() output before destruction,
// then calls _Exit just like the unchanged runner main.
#include "e15_binding_test.cpp"
#include <cstdlib>
#include <fstream>
#include <memory>
#include <sstream>

namespace e16_fixture {
std::string mode;
bool guestFinished=false,shutdownSeen=false;
std::vector<uint8_t> stoppedRam;
R5900Context stoppedCpu{};
std::vector<std::pair<int,R5900Context>> stoppedThreads;
std::string stoppedSchedule;
unsigned guestCalls=0;
std::string schedule(PS2Runtime &r) {
    auto s=r.eeScheduler().snapshot();std::ostringstream o;
    o << s.sequence << ':' << s.eeCycle << ':' << s.sliceEndCycle << ':' << s.nextEventCycle << ':' << s.runningThreadId << ':' << s.threads.size();
    for(const auto &t:s.threads) o << '|' << t.id << ':' << static_cast<unsigned>(t.status)
        << ':' << t.initialPriority << ':' << t.currentPriority << ':' << t.pc << ':' << t.entry << ':' << t.stack << ':' << t.stackSize << ':' << t.gp
        << ':' << static_cast<unsigned>(t.waitReason) << ':' << t.waitId << ':' << t.suspendCount << ':' << t.wakeupCount;
    for(const auto &v:s.semaphores) o << "|s" << v.id << ':' << v.count << ':' << v.maxCount << ':' << v.waiters;
    for(const auto &v:s.eventFlags) o << "|e" << v.id << ':' << v.bits << ':' << v.initBits << ':' << v.attr << ':' << v.waiters;
    return o.str();
}
std::string readEvents() {
    const char *d=std::getenv("PS2X_E7_DIR");if(!d)return {};
    std::ifstream f(std::string(d)+"/e7-events.txt");
    return std::string(std::istreambuf_iterator<char>(f),{});
}
size_t count(const std::string &s,const std::string &needle) {
    size_t n=0,p=0;while((p=s.find(needle,p))!=std::string::npos){++n;p+=needle.size();}return n;
}
int fallbackError() {
    bool caught=false;
    try {
        PS2Runtime runtime;require(runtime.memory().initialize(),"fallback memory init");
        auto c=context(0x4027b8);auto *ram=runtime.memory().getRDRAM();
        SET_GPR_U32((&c),4,e15_fixture::Mpeg);SET_GPR_U32((&c),5,e15_fixture::Work);SET_GPR_U32((&c),6,0x10000);
        {
            ps2_e15::Trace trace("fixture-error-setup",0,ram,&c,0x4027b8,e15_fixture::Main,1);
            runtime.lookupFunction(0x4027b8)(ram,&c,&runtime);trace.finish(0);
        }
        throw std::runtime_error("intentional fixture caller error");
    } catch(const std::runtime_error &e) {
        caught=std::string(e.what())=="intentional fixture caller error";
    }
    const auto text=readEvents();
    require(caught && count(text,"# E15 CLOSURE")==1 && count(text,"# E7 SHUTDOWN")==1,"error-exit destructor fallback missing");
    std::printf("E16 DESTRUCTOR-FALLBACK callerErrorCaught=1 runCalled=0 realClosure=1 titleBoots=0\n");
    std::printf("E16 RUN-EXIT FIXTURE TAIL COMPLETE result=PASS mode=fallback-error\n");
    return 0;
}
void init(PS2Runtime&,void*) {}
void shutdown(PS2Runtime &r,void*) {
    require(guestFinished,"shutdown preceded game completion");
    // This is the final diagnostic producer, reached by run after join().
    if(mode!="unopened" && mode!="disabled")
        ps2_e7::event(r.memory().gs().vsyncTick.load(),"e16-final-producer","guestFinished=1 guestCalls=%u",guestCalls);
    stoppedRam.assign(r.memory().getRDRAM(),r.memory().getRDRAM()+PS2_RAM_SIZE);
    stoppedCpu=r.cpu();stoppedSchedule=schedule(r);shutdownSeen=true;
    for(const auto &t:r.eeScheduler().snapshot().threads) {
        const auto *thread=r.eeScheduler().thread(t.id);require(thread,"snapshot thread absent");
        stoppedThreads.emplace_back(t.id,thread->activeContext());
    }
}
void guest(uint8_t *ram,R5900Context *c,PS2Runtime *r) {
    ++guestCalls;
    if(mode!="unopened" && mode!="disabled") {
        r->memory().gs().vsyncTick.store(17);
        SET_GPR_U32(c,4,e15_fixture::Mpeg);SET_GPR_U32(c,5,e15_fixture::Work);SET_GPR_U32(c,6,0x10000);
        e15_fixture::api(r,ram,c,0x4027b8,e15_fixture::Resume);
        require(GPR_U32(c,2)!=0,"actual Create failed");
        SET_GPR_U32(c,4,e15_fixture::Mpeg);SET_GPR_U32(c,5,1);SET_GPR_U32(c,6,e15_fixture::Callback);SET_GPR_U32(c,7,e15_fixture::User);
        e15_fixture::api(r,ram,c,0x402c08,e15_fixture::Resume);
        require(GPR_U32(c,2)!=0,"actual AddCallback failed");
        if(mode=="window-complete") {
            r->memory().gs().vsyncTick.store(604);
            ps2_e7::event(604,"e16-window-end","completed=1");
        }
    }
    guestFinished=true;c->pc=0;r->requestStop();
}
int run(const std::string &arg) {
    mode=arg;
    auto runtime=std::make_unique<PS2Runtime>();
    runtime->setDebugUiCallbacks(init,nullptr,shutdown,nullptr);
    require(runtime->initialize("E16 non-title run-exit fixture"),"runtime initialize");
    require(!runtime->hasFunction(e15_fixture::Main),"synthetic entry conflicts");
    require(runtime->registerFunction(e15_fixture::Main,guest),"fixture registration");
    runtime->cpu().pc=e15_fixture::Main;
    runtime->run();
    require(guestCalls==1 && guestFinished && shutdownSeen,"run/join/final producer path missing");
    const bool ramSame=std::memcmp(stoppedRam.data(),runtime->memory().getRDRAM(),PS2_RAM_SIZE)==0;
    bool cpuSame=std::memcmp(&stoppedCpu,&runtime->cpu(),sizeof(stoppedCpu))==0;
    for(const auto &[id,c]:stoppedThreads) {
        const auto *thread=runtime->eeScheduler().thread(id);
        cpuSame=cpuSame && thread && std::memcmp(&c,&thread->activeContext(),sizeof(c))==0;
    }
    const bool scheduleSame=stoppedSchedule==schedule(*runtime);
    require(ramSame && cpuSame && scheduleSame,"closure changed guest state or scheduler snapshot");
    const auto text=readEvents();
    const bool silent=mode=="unopened" || mode=="disabled";
    const bool closed=silent?text.empty():(count(text,"# E15 CLOSURE")==1 && count(text,"# E7 SHUTDOWN")==1);
    std::printf("E16 RUN-EXIT mode=%s beforeDestructor=1 runReturned=1 gameJoined=1 finalProducer=1 ram32MiB-unchanged=%u fullContext-unchanged=%u schedule-unchanged=%u footers=%u guestCalls=%u titleBoots=0\n",
        mode.c_str(),ramSame,cpuSame,scheduleSame,closed,guestCalls);
    if(mode=="idempotent") {
        runtime.reset();require(readEvents()==text,"destructor duplicated or altered closure");
        std::printf("E16 IDEMPOTENCE destructorAfterRun=1 bytes-identical=1\n");
    }
    std::printf("E16 RUN-EXIT FIXTURE TAIL COMPLETE result=%s exit=_Exit destructorRequired=0\n",closed?"PASS":"FAIL-BEFORE");
    std::fflush(nullptr);
    std::_Exit(closed?0:1);
}
}
extern "C" int e16_binding_main(int argc,char **argv) {
    if(argc==2 && (std::string(argv[1])=="prior" || std::string(argv[1])=="input" || std::string(argv[1])=="no-input"))
        return e15_binding_main(argc,argv);
    try {
        require(argc==2,"fixture mode required");
        const std::string mode=argv[1];
        if(mode=="fallback-error")return e16_fixture::fallbackError();
        require(mode=="quiescent" || mode=="idempotent" || mode=="window-complete" || mode=="disabled" || mode=="unopened","unknown E16 mode");
        return e16_fixture::run(mode);
    } catch(const std::exception &e) {std::fprintf(stderr,"E16 FIXTURE ERROR: %s\n",e.what());std::fflush(nullptr);std::_Exit(2);}
}
