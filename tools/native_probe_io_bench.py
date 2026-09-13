#!/usr/bin/env python3
"""Isolated CPU/storage bound for the actual native callback trace emitter.

This does not run the game, change runtime sources, or benchmark iPhone storage.
It preserves representative observed offset patterns, not unavailable snapshots.
"""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import shutil
import statistics
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT/'native/diagnostics/native_callback_trace.h'
COUNTERS = ('retries', 'camera_offsets', 'camera_restores', 'skipped_elapsed', 'skipped_queue',
            'queue_before', 'queue_after', 'view_matrix_calls', 'frame_end_calls',
            'elapsed_calls', 'queue_calls', 'gate_calls', 'gate_ready')
TIMING_FIELDS = ('wall', 'duration_ms', 'cpu_duration_ms')


HARNESS = r'''
#include <cstdint>
#include <fstream>
#include <iostream>
#include <sstream>
#include <vector>
#include <time.h>
using u32=uint32_t; using u64=uint64_t;
struct CPUState {u32 gpr[32]{},pc=0,lr=0;u64 timebase=0;unsigned char* ram=nullptr;u32 ram_size=0;};
static bool buffered=false;
static uint64_t flush_requests=0, actual_flush_calls=0;
static int ProbeFlush(FILE* f){++flush_requests;if(buffered)return 0;++actual_flush_calls;return std::fflush(f);}
#include "native_callback_trace.h"
struct Event {bool update=false;CPUState cpu{};NativeProbe::Active active{};NativeProbe::Snapshot after{};u32 counts[13]{};};
static double CpuSeconds(){timespec ts{};if(clock_gettime(CLOCK_PROCESS_CPUTIME_ID,&ts))std::abort();return ts.tv_sec+ts.tv_nsec/1e9;}
template<size_t N> static void Change(std::istringstream& input,std::array<unsigned char,N>& bytes){
 size_t n=0,offset=0;input>>n;for(size_t i=0;i<n;++i){input>>offset;if(offset>=N)std::abort();bytes[offset]^=1;}
}
int main(int argc,char** argv){
 if(argc!=5)return 2;
 std::ifstream input(argv[1]);std::vector<Event> events;std::string line;
 while(std::getline(input,line)){
  std::istringstream row(line);Event e;int update=0,repeat=0,moved=0,rng=0,same_rider=0,same_view=0;
  row>>update>>repeat>>e.cpu.gpr[3]>>e.active.tb>>e.cpu.timebase>>e.active.app
     >>e.after.rider>>same_rider>>e.after.view>>same_view>>e.active.before.state>>e.after.state>>moved>>rng;
  e.update=update;e.active.repeated=repeat;e.active.cpu_start=0;e.active.before.rider=e.after.rider+(same_rider?0:4);
  e.active.before.view=e.after.view+(same_view?0:4);e.active.before.app=e.after.app=e.active.app;
  for(auto& count:e.counts)row>>count;
  // Deterministic bytes: raw before/after RAM snapshots are absent from JSONL.
  for(size_t i=0;i<e.active.before.body.size();++i)e.active.before.body[i]=static_cast<unsigned char>(i*37);
  e.after.body=e.active.before.body;
  Change(row,e.after.body);Change(row,e.after.application);Change(row,e.after.camera);
  if(moved&&e.active.before.body[240]==e.after.body[240])e.after.body[240]^=1;
  if(rng)e.after.random[0]=1;
  if(!row)return 3;events.push_back(e);
 }
 if(events.empty())return 4;
 const int repetitions=std::stoi(argv[4]);if(repetitions<1)return 5;
 buffered=std::string(argv[3])=="buffered";
 FILE* output=std::fopen(argv[2],"wx");if(!output)return 6;
 if(buffered&&std::setvbuf(output,nullptr,_IOFBF,64*1024))return 7;
 NativeProbe::output_file=output;
 const auto wall_start=NativeProbe::Clock::now();const double cpu_start=CpuSeconds();
 for(int repeat=0;repeat<repetitions;++repeat)for(auto& e:events){
  NativeProbe::render.pending=!e.update;
  NativeProbe::retries=e.counts[0];NativeProbe::camera_offsets=e.counts[1];NativeProbe::camera_restores=e.counts[2];
  NativeProbe::skipped_elapsed=e.counts[3];NativeProbe::skipped_queue=e.counts[4];
  NativeProbe::queue_before=e.counts[5];NativeProbe::queue_after=e.counts[6];
  NativeProbe::view_matrix_calls=e.counts[7];NativeProbe::frame_end_calls=e.counts[8];
  NativeProbe::elapsed_calls=e.counts[9];NativeProbe::queue_calls=e.counts[10];
  NativeProbe::gate_calls=e.counts[11];NativeProbe::gate_ready=e.counts[12];
  NativeProbe::Emit(e.cpu,e.update?"update":"render",e.active,e.after);
 }
 ++actual_flush_calls;const int flushed=std::fflush(output);const int closed=std::fclose(output);
 const double cpu=CpuSeconds()-cpu_start;
 const double wall=std::chrono::duration<double>(NativeProbe::Clock::now()-wall_start).count();
 const auto count=events.size()*repetitions;
 std::cout<<"{\"events\":"<<count<<",\"cpu_seconds\":"<<cpu<<",\"wall_seconds\":"<<wall
          <<",\"flush_requests\":"<<flush_requests<<",\"explicit_fflush_calls\":"<<actual_flush_calls
          <<",\"final_flush_ok\":"<<(flushed==0?"true":"false")<<",\"close_ok\":"<<(closed==0?"true":"false")<<"}\n";
 return flushed||closed?8:0;
}
'''


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def instrument_header(source):
    marker = ' std::fflush(file);'
    if source.count(marker) != 1:
        raise ValueError('Expected exactly one callback Emit flush site; inspect changed source')
    return source.replace(marker, ' ProbeFlush(file);')


def recipes(rows, maximum=512):
    selected = [row for row in rows if row.get('event') in ('render', 'update')]
    if not selected or maximum < 1:
        raise ValueError('Need native callback observations and a positive sample limit')
    if len(selected) > maximum:
        selected = [selected[i*len(selected)//maximum] for i in range(maximum)]
    output = []
    for row in selected:
        fields = [int(row['event'] == 'update'), row['repeat'], row['result'], row['tb_start'], row['tb_end'],
                  row['app'], row['rider'], row['same_rider'], row['view'], row['same_view'],
                  row['state_before'], row['state_after'], row['position_changed'], row['rng_changed']]
        fields.extend(row[field] for field in COUNTERS)
        for field, bound in (('body_offsets', 0x800), ('app_offsets', 0x400), ('view_offsets', 0x100)):
            offsets = row[field]
            if any(not isinstance(value, int) or not 0 <= value < bound or value % 4 for value in offsets):
                raise ValueError('Invalid bounded watched offset: '+field)
            fields.extend([len(offsets), *offsets])
        if any(not isinstance(value, int) or value < 0 for value in fields):
            raise ValueError('Native emission recipe fields must be unsigned integers')
        output.append(' '.join(map(str, fields)))
    return output


def normalized_digest(path):
    text = Path(path).read_text()
    if not text.endswith('\n'):
        raise ValueError('Emitter output is incomplete')
    digest = hashlib.sha256()
    count = 0
    for line in text.splitlines():
        row = json.loads(line)
        for field in TIMING_FIELDS:
            row.pop(field, None)
        digest.update((json.dumps(row, sort_keys=True, separators=(',', ':'))+'\n').encode())
        count += 1
    return dict(sha256=digest.hexdigest(), events=count)


def prepare(trace, output):
    output = Path(output).resolve()
    if not output.is_relative_to(ROOT/'local'):
        raise ValueError('Keep benchmark artifacts under local/')
    output.mkdir(parents=True, exist_ok=False)
    raw = Path(trace).read_text()
    if not raw.endswith('\n'):
        raise ValueError('Use a complete native trace')
    rows = [json.loads(line) for line in raw.splitlines()]
    inputs = recipes(rows)
    (output/'events.txt').write_text('\n'.join(inputs)+'\n')
    source = HEADER.read_text()
    (output/'native_callback_trace.h').write_text(instrument_header(source))
    helpers = {}
    for path in HEADER.parent.glob('callback_timing.h'):
        copied = output/path.name
        copied.write_bytes(path.read_bytes())
        helpers[path.name] = sha(copied)
    stubs = output/'include/Core'
    stubs.mkdir(parents=True)
    (stubs/'Core.h').write_text('#pragma once\n#include <string>\nnamespace Core { inline void SaveScreenShot(const std::string&) {} }\n')
    (output/'bench.cpp').write_text(HARNESS)
    compiler = shutil.which('clang++')
    if compiler is None:
        raise ValueError('clang++ is required')
    command = [compiler, '-std=c++17', '-O3', '-I'+str(output/'include'), '-I'+str(HEADER.parent),
               str(output/'bench.cpp'), '-o', str(output/'bench')]
    subprocess.run(command, check=True)
    result = dict(schema=1, source_header=str(HEADER), source_sha256=hashlib.sha256(source.encode()).hexdigest(), trace=str(Path(trace).resolve()),
                  trace_sha256=sha(trace), selected_callbacks=len(inputs), compiler_command=command,
                  compiler_version=subprocess.check_output([compiler, '--version'], text=True).splitlines()[0],
                  binary_sha256=sha(output/'bench'), harness_sha256=sha(output/'bench.cpp'),
                  recipe_sha256=sha(output/'events.txt'), platform=platform.platform(),
                  helpers=helpers,
                  measurement='Actual Emit code with one instrumented flush site, stub CPU/Core types; no game execution.',
                  recipe_limits='Observed callback fields and offset patterns; original RAM bytes were not recorded. '
                                'Deterministic synthetic bytes exercise hashing/diff work, not a live state replay.')
    (output/'prepared.json').write_text(json.dumps(result, indent=2)+'\n')
    return result


def run(output, rounds=4, repetitions=8):
    output = Path(output).resolve()
    prepared = json.loads((output/'prepared.json').read_text())
    if rounds < 2 or repetitions < 1:
        raise ValueError('Use at least two alternating rounds and positive repetitions')
    if sha(output/'bench') != prepared['binary_sha256'] or sha(output/'events.txt') != prepared['recipe_sha256']:
        raise ValueError('Prepared benchmark identity changed')
    samples, reference = [], None
    for index in range(rounds):
        for mode in (('flush-each', 'buffered') if index % 2 == 0 else ('buffered', 'flush-each')):
            log = output/f'{index:02}-{mode}.jsonl'
            command = [str(output/'bench'), str(output/'events.txt'), str(log), mode, str(repetitions)]
            result = json.loads(subprocess.check_output(command, text=True))
            fidelity = normalized_digest(log)
            if reference is None:
                reference = fidelity
            if fidelity != reference or result['events'] != fidelity['events']:
                raise ValueError('Output changed or callback records were lost between modes')
            result.update(mode=mode, round=index, output_bytes=log.stat().st_size, fidelity=fidelity,
                          cpu_ms_per_callback=result['cpu_seconds']*1000/result['events'],
                          wall_ms_per_callback=result['wall_seconds']*1000/result['events'])
            samples.append(result)
    medians = {mode: {key: statistics.median(row[key] for row in samples if row['mode'] == mode)
                      for key in ('cpu_ms_per_callback', 'wall_ms_per_callback')}
               for mode in ('flush-each', 'buffered')}
    result = dict(prepared=prepared, samples=samples, medians=medians,
                  difference_ms_per_callback={key: medians['flush-each'][key]-medians['buffered'][key]
                                              for key in medians['flush-each']},
                  normalized_output_fidelity=True, kernel_write_syscalls=None,
                  limits=['Explicit fflush calls are counted, not kernel write syscalls; buffering can write on a full buffer.',
                          'fflush/close completion is checked; neither mode adds fsync or proves crash durability.',
                          'Buffered crash tails and trial-end visibility need explicit bounded flush policy before any live change.',
                          'Measures Mac emitter/storage cost with fixed representative data, not iPhone or whole callback cost.',
                          'Exclude concurrent builds/gameplay and repeat before attributing small timing differences.'])
    (output/'report.json').write_text(json.dumps(result, indent=2)+'\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('prepare')
    p.add_argument('--trace', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p = sub.add_parser('run')
    p.add_argument('output', type=Path)
    p.add_argument('--rounds', type=int, default=4)
    p.add_argument('--repetitions', type=int, default=8)
    args = parser.parse_args()
    try:
        result = prepare(args.trace, args.output) if args.command == 'prepare' else run(args.output, args.rounds, args.repetitions)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
