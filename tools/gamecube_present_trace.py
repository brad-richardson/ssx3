#!/usr/bin/env python3
"""Build an isolated Metal presentation observer using existing native libraries.

No game or production runtime files are edited. Run the resulting player with
SSX_PRESENT_TRACE=/absolute/new.csv to capture acquire/submit/GPU/display events.
GPU timestamps describe the final render command buffer, not total frame cost.
"""
import argparse
import sys,shlex,subprocess,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
from gamecube_draw_trace import compile_copy,sha,BUILD,VENDOR
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',required=True,type=Path)
args=parser.parse_args()
out=args.output.resolve()
if not out.is_relative_to(ROOT/'local'):
 parser.error('Diagnostic outputs must remain under local/')
out.mkdir(parents=True,exist_ok=False)
production_sha=sha(BUILD/'moderngekko-run')
commands=subprocess.check_output([str(ROOT/'local/tooling/ninja'),'-C',str(BUILD),'-t','commands','moderngekko-run'],text=True).splitlines()
original=VENDOR/'vendor/dolphin/Source/Core/VideoBackends/Metal/MTLGfx.mm'
s=original.read_text()
for marker in ['#include <fstream>', '    m_drawable = MRCRetain([m_layer nextDrawable]);']:
 if s.count(marker)!=1: raise ValueError(f'Presentation injection point changed: {marker}')
s=s.replace('#include <fstream>', '''#include <fstream>
#include <atomic>
#include <cstdio>
#include <cstdlib>
#include <mutex>
static std::atomic<unsigned long long> trace_frame{0};
static void PresentTrace(const char* event, unsigned long long frame, double a, double b) {
  static auto* mutex = new std::mutex;
  static FILE* file = [] { const char* p = std::getenv("SSX_PRESENT_TRACE"); return p ? std::fopen(p,"wx") : nullptr; }();
  if (!file) return;
  std::lock_guard lock(*mutex);
  std::fprintf(file,"%s,%llu,%.9f,%.9f,%.9f\\n",event,frame,CACurrentMediaTime(),a,b);
  std::fflush(file);
}
''')
s=s.replace('    m_drawable = MRCRetain([m_layer nextDrawable]);','''    const double acquire_start = CACurrentMediaTime();
    m_drawable = MRCRetain([m_layer nextDrawable]);
    PresentTrace("acquire",trace_frame.load()+1,CACurrentMediaTime()-acquire_start,0);''')
marker='''    if (m_drawable)
    {''';assert s.count(marker)==1
s=s.replace(marker,marker+'''
      const auto frame = ++trace_frame;
      PresentTrace("submit",frame,[[m_drawable texture] width],[[m_drawable texture] height]);
      [m_drawable addPresentedHandler:^(id<MTLDrawable> drawable) {
        PresentTrace("display",frame,[drawable presentedTime],0);
      }];
      [g_state_tracker->GetRenderCmdBuf() addCompletedHandler:^(id<MTLCommandBuffer> buffer) {
        PresentTrace("gpu",frame,[buffer GPUStartTime],[buffer GPUEndTime]);
      }];''')
src=out/'MTLGfx.mm';src.write_text(s);obj=out/'MTLGfx.o'
cmd=compile_copy(next(c for c in commands if c.endswith('/MTLGfx.mm')),src,obj)
subprocess.run(cmd,cwd=BUILD,check=True)
link=shlex.split(next(c for c in commands if ' -o moderngekko-run ' in c));link=link[2:link.index('&&',2)];link[link.index('-o')+1]=str(out/'player');link.insert(link.index('libmoderngekko.a'),str(obj));subprocess.run(link,cwd=BUILD,check=True)
if sha(BUILD/'moderngekko-run')!=production_sha:
 raise RuntimeError('Production player changed during diagnostic build')
(out/'build.json').write_text(json.dumps({'source_sha256':sha(original),'player_sha256':sha(out/'player'),'production_player_sha256':sha(BUILD/'moderngekko-run')},indent=2)+'\n')

print(out/'player')
