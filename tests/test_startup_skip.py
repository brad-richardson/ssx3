import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


class StartupSkip(unittest.TestCase):
    @unittest.skipUnless(shutil.which('c++'),'requires a C++ compiler')
    def test_movie_ownership_readiness_and_bounded_input(self):
        source=r'''
#include "native/diagnostics/startup_skip.h"
#include <array>
#include <cassert>
#include <vector>
struct CPU { uint32_t pc=0,lr=0,gpr[32]{}; uint64_t timebase=123; unsigned char* ram; size_t ram_size; };
int main() {
 using namespace StartupBoot;
 std::vector<unsigned char> ram(4*1024*1024);
 CPU c{}; c.ram=ram.data();c.ram_size=ram.size();c.gpr[13]=SDA;c.gpr[3]=0x80010000;
 c.gpr[1]=0x80008000;c.lr=0x80123450;c.pc=FrontendUpdate;
 auto put=[&](uint32_t a,uint32_t v){for(int i=0;i<4;++i)ram[a-0x80000000+i]=v>>(24-8*i);};
 put(MovieMask,15);put(FrontendUpdate,0x9421ffc0);
 auto original=ram;
 Configure(nullptr,false);Step(c);assert(ram==original && phase==Phase::Disabled);
 Configure(nullptr,true);Step(c);
 assert(skipped && Word(c,MovieMask)==0 && phase==Phase::Frontend);
 assert(c.pc==FrontendUpdate && c.lr==0x80123450 && c.gpr[3]==0x80010000 && c.timebase==123);
 put(MovieMask,15);assert(ram==original); // Exactly the owned four-byte mask changed.
 Step(c);assert(Word(c,MovieMask)==15); // One shot: later attract movies remain untouched.
 for(auto mask:{1u,3u,16u}) {
   put(MovieMask,mask);Configure(nullptr,true);auto before=ram;Step(c);
   assert(phase==Phase::Failed && ram==before && !skipped);
 }
 put(MovieMask,15);put(0x80010000+MoviePointerOffset,0x80100000);
 Configure(nullptr,true);Step(c);assert(phase==Phase::Failed && Word(c,MovieMask)==15);
 put(0x80010000+MoviePointerOffset,0);put(FrontendUpdate,0);
 Configure(nullptr,true);Step(c);assert(phase==Phase::Failed && Word(c,MovieMask)==15);
 put(FrontendUpdate,0x9421ffc0);Configure(nullptr,true);Step(c);
 c.pc=0x800d27e4;c.gpr[3]=0x80100000;put(c.gpr[3],TitleVTable);Step(c);
 assert(phase==Phase::Title);
 c.pc=TitleUpdate;put(TitleUpdate,0x9421fff0);put(title+28,5u<<18);Step(c);
 assert(!active_return && phase==Phase::Title); // Active update alone cannot bypass resource readiness.
 c.pc=0x800d2710;Step(c);c.pc=c.lr;c.gpr[3]=1;Step(c);
 assert(phase==Phase::Title); // A ready return without a loaded UI is insufficient.
 c.pc=0x800d2710;c.gpr[3]=0x80100000;put(c.gpr[3]+64,0x80110000);Step(c);
 c.pc=c.lr;c.gpr[3]=1;c.gpr[1]+=16;Step(c);assert(phase==Phase::Title);
 c.gpr[1]-=16;Step(c);
 assert(phase==Phase::Title && title_resources_ready); // Assets ready is not input ready.
 put(TitleUpdate,0x9421fff0);
 c.pc=TitleUpdate;c.gpr[3]=title;c.lr=0x8023d718;
 put(title+28,3u<<18);Step(c); // State manager has not activated this title yet.
 c.pc=c.lr;Step(c);assert(phase==Phase::Title && !active_return);
 c.pc=TitleUpdate;put(title+28,5u<<18);put(TitleUpdate,0);Step(c);
 assert(!active_return); // The pinned active update entry must match.
 put(TitleUpdate,0x9421fff0);c.gpr[3]=title+4;Step(c);assert(!active_return);
 c.gpr[3]=title;Step(c);assert(active_return==c.lr && phase==Phase::Title);
 c.pc=c.lr;c.gpr[1]+=16;Step(c);assert(phase==Phase::Title && active_return);
 c.gpr[1]-=16;put(title+64,0);Step(c);assert(phase==Phase::Title && !active_return);
 put(title+64,0x80110000);c.pc=TitleUpdate;Step(c);
 c.pc=c.lr;put(MovieMask,4);Step(c);assert(phase==Phase::Title);
 put(MovieMask,0);c.pc=TitleUpdate;Step(c);
 c.pc=c.lr;put(title+28,6u<<18);Step(c);assert(phase==Phase::Title);
 put(title+28,5u<<18);c.pc=TitleUpdate;Step(c);
 auto active_before=ram;c.pc=c.lr;Step(c);
 assert(phase==Phase::TitleReady && ram==active_before); // Complete, still-active input pass.
 c.pc=0x800d23cc;c.gpr[3]=0x80120000;put(c.gpr[3],MainVTable);Step(c);
 c.pc=0x800d20bc;Step(c);assert(phase==Phase::MainMenuLoading);
 put(c.gpr[3]+64,0x80130000);Step(c);assert(phase==Phase::MainMenu && !observing);
 AdvanceInput input;
 assert(input.Update(Phase::Title,1,true)==InputAction::None);
 assert(input.Update(Phase::TitleReady,2,false)==InputAction::None);
 assert(input.Update(Phase::TitleReady,3,true)==InputAction::PressStart);
 assert(input.Update(Phase::TitleReady,3.5,true)==InputAction::None);
 assert(input.Update(Phase::MainMenuLoading,3.6,true)==InputAction::ReleaseStart);
 assert(input.Update(Phase::TitleReady,10,true)==InputAction::None); // Never button-mash/retry.
 input={};input.Update(Phase::TitleReady,0,true);
 assert(input.Update(Phase::TitleReady,2,true)==InputAction::ReleaseStart);
 input={};input.Update(Phase::TitleReady,0,true);
 assert(input.Update(Phase::TitleReady,.1,false)==InputAction::ReleaseStart);
 Configure(nullptr,false);
 assert(!title_resources_ready && !active_return); // No stale readiness across sessions.
}
'''
        with tempfile.TemporaryDirectory() as temporary:
            path=Path(temporary);(path/'test.cpp').write_text(source)
            subprocess.run(['c++','-std=c++17','-I',str(ROOT),str(path/'test.cpp'),'-o',str(path/'test')],check=True)
            subprocess.run([str(path/'test')],check=True)
