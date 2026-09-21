// Actual current runner objects and registry; no title ELF is loaded.
#include "e16_binding_test.cpp"
extern "C" int e17_binding_main(int argc,char** argv) {
    if (argc!=3) return e16_binding_main(argc,argv);
    try {
        const std::string mode=argv[1];
        require(mode=="check-present" || mode=="check-absent","unknown presence mode");
        const auto pc=static_cast<uint32_t>(std::stoul(argv[2],nullptr,0));
        require(pc==0x14f2a8 || pc==0x156750 || pc==0x243a80 || pc==0x395730 || pc==0x3a0158,"PC outside E17 scope");
        PS2Runtime runtime;require(runtime.memory().initialize(),"memory init");
        const bool want=mode=="check-present",found=runtime.hasFunction(pc);
        auto fn=runtime.lookupFunction(pc);
        std::printf("ABSORB pc=0x%x hasFunction=%u expected=%u actual-binding=%s\n",pc,found,want,fn?symbol(fn):"null");
        require(found==want,"absorb entry presence differs");
        if(found) {
            char name[64];std::snprintf(name,sizeof(name),"sub_%08X_0x%x",pc,pc);
            require(std::string(symbol(fn)).find(name)!=std::string::npos,"binding starts at owner instead of exact PC");
        }
        std::puts("E17 PRESENCE CHECK TAIL COMPLETE success=1 titleBoots=0");return 0;
    } catch(const std::exception& e) {
        std::fprintf(stderr,"E17 PRESENCE CHECK TAIL COMPLETE failure=%s titleBoots=0\n",e.what());return 1;
    }
}
