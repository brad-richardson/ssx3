#!/usr/bin/env python3
"""Check and time an isolated, bit-exact split of generated float conversions.

The small common path is always inlined; exceptional inputs retain the exact
existing mapping in cold functions. This never rewrites generated/vendor files.
"""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import statistics
import subprocess

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / 'local/native/ssx3-module/codegen/generated/generated.h'
FLAGS = ['-std=c11', '-O2', '-flto=thin', '-ffp-contract=off', '-fno-fast-math']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_conversion_receipt(output, *, require_check=True):
    """Verify the frozen inputs and optionally their exact-binary passing check.

    The returned candidate-header SHA binds later module experiments to these
    tested bytes. The current tool revision need not equal the recorded one.
    """
    output = Path(output).resolve()
    if not output.is_relative_to(ROOT / 'local'):
        raise ValueError('Use evidence under local/')
    receipt = json.loads((output / 'build.json').read_text())
    for name, key in (('check', 'binary_sha256'), ('check.c', 'harness_sha256')):
        if sha(output / name) != receipt.get(key):
            raise ValueError('Built conversion harness changed: ' + name)
    for name, key in (('reference-generated.h', 'original_header_sha256'),
                      ('candidate-generated.h', 'candidate_header_sha256')):
        if sha(output / name) != receipt.get(key):
            raise ValueError('Conversion header receipt mismatch: ' + name)
    if require_check:
        try:
            correctness = json.loads((output / 'check.json').read_text())
        except FileNotFoundError:
            raise ValueError('Run a passing correctness check for this exact binary first') from None
        if correctness.get('passed') is not True or correctness.get('binary_sha256') != receipt['binary_sha256']:
            raise ValueError('Run a passing correctness check for this exact binary first')
    return receipt['candidate_header_sha256']


def helper_span(header):
    start = header.index('static inline f64 dolrecomp_f32_from_bits(u32 bits) {')
    end = header.index('static inline f64 dolrecomp_f64_from_bits(u64 bits) {', start)
    result = header[start:end]
    if result.count('static inline ') != 2 or result.count('dolrecomp_f32_to_bits') != 1:
        raise ValueError('Generated conversion helper seam changed')
    return start, end


def split_helpers(header):
    start, end = helper_span(header)
    slow = header[start:end].replace('static inline ',
                                     'static __attribute__((noinline, cold)) ')
    for name in ('from', 'to'):
        slow = slow.replace(f'dolrecomp_f32_{name}_bits', f'dolrecomp_f32_{name}_bits_slow')
    fast = r'''
static __attribute__((always_inline)) inline f64 dolrecomp_f32_from_bits(u32 bits) {
    u32 exp = (bits >> 23) & 255u;
    if (__builtin_expect(exp - 1u >= 254u, 0))
        return dolrecomp_f32_from_bits_slow(bits);
    u64 result = ((u64)(bits & 0x80000000u) << 32) |
                 ((u64)(exp + 896u) << 52) |
                 ((u64)(bits & 0x007fffffu) << 29);
    f64 value;
    memcpy(&value, &result, sizeof(value));
    return value;
}

static __attribute__((always_inline)) inline u32 dolrecomp_f32_to_bits(f64 value) {
    u64 bits;
    memcpy(&bits, &value, sizeof(bits));
    u32 exp = (u32)((bits >> 52) & 0x7ffu);
    if (__builtin_expect(exp - 874u <= 22u, 0))
        return dolrecomp_f32_to_bits_slow(value);
    return (u32)(((bits >> 32) & 0xc0000000u) |
                 ((bits >> 29) & 0x3fffffffu));
}

'''
    return header[:start] + slow + fast + header[end:]


HARNESS = r'''
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <inttypes.h>
#include <fenv.h>

static uint64_t as_bits(double x) { uint64_t u; memcpy(&u, &x, 8); return u; }
static double as_double(uint64_t u) { double x; memcpy(&x, &u, 8); return x; }
static uint64_t random64(uint64_t *state) {
    uint64_t x=*state; x^=x<<13; x^=x>>7; x^=x<<17; return *state=x;
}
static void check_to(uint64_t bits) {
    double x=as_double(bits);
    uint32_t a=ref_dolrecomp_f32_to_bits(x), b=cand_dolrecomp_f32_to_bits(x);
    if(a!=b) {
        fprintf(stderr,"to mismatch %016" PRIx64 " %08" PRIx32 " %08" PRIx32 "\n",bits,a,b);
        exit(2);
    }
}
static void check_from(uint32_t bits) {
    uint64_t a=as_bits(ref_dolrecomp_f32_from_bits(bits));
    uint64_t b=as_bits(cand_dolrecomp_f32_from_bits(bits));
    if(a!=b) {
        fprintf(stderr,"from mismatch %08" PRIx32 " %016" PRIx64 " %016" PRIx64 "\n",bits,a,b);
        exit(2);
    }
}
static int check(int exhaustive) {
    uint64_t total=exhaustive ? UINT64_C(0x100000000) : UINT64_C(0x1000000);
    for(uint64_t i=0;i<total;++i) {
        // Odd multiplication spans all u32 values in the exhaustive case;
        // quick checks still exercise both signs and every exponent.
        check_from((uint32_t)i*UINT32_C(2654435761));
        if(exhaustive && (i&UINT64_C(0xfffffff))==UINT64_C(0xfffffff)) {
            fprintf(stderr,"from checked %" PRIu64 "/%" PRIu64 "\n",i+1,total);
            fflush(stderr);
        }
    }
    // Explicit fraction boundaries, including every single-bit mantissa.
    const uint64_t mask=UINT64_C(0xfffffffffffff);
    uint64_t to_count=0;
    for(unsigned sign=0;sign<2;++sign) for(unsigned exp=0;exp<2048;++exp)
        for(unsigned bit=0;bit<52;++bit) for(unsigned pattern=0;pattern<4;++pattern) {
            uint64_t one=UINT64_C(1)<<bit;
            uint64_t fraction=pattern==0 ? one : pattern==1 ? one-1 : pattern==2 ? mask^one : mask;
            check_to(((uint64_t)sign<<63)|((uint64_t)exp<<52)|fraction);
            ++to_count;
        }
    // Bit mappings must remain exact under all supported host rounding modes.
    const int rounds[]={FE_TONEAREST,FE_TOWARDZERO,FE_UPWARD,FE_DOWNWARD};
    int old=fegetround();
    for(unsigned mode=0;mode<4;++mode) {
        if(fesetround(rounds[mode])) return 3;
        uint64_t state=UINT64_C(0x4d595df4d0f33173);
        for(unsigned i=0;i<1048576;++i) {
            uint64_t bits=random64(&state); check_to(bits); ++to_count;
            check_from((uint32_t)bits);
        }
    }
    if(fesetround(old)) return 3;
    printf("{\"passed\":true,\"from_u32_inputs\":%" PRIu64 ",\"additional_from_rounding_samples\":4194304,\"to_u64_samples\":%" PRIu64 ",\"host_rounding_modes\":4}\n",total,to_count);
    return 0;
}

enum { COUNT=16384 };
static uint32_t words[COUNT];
static double doubles[COUNT];
static volatile uint64_t sink;
#define KERNEL_FROM(NAME,FUNC) \
__attribute__((noinline)) static uint64_t NAME(uint64_t count) { \
    uint64_t sum=0; for(uint64_t i=0;i<count;++i) \
        sum+=as_bits(FUNC(words[i&(COUNT-1)])); return sum; }
#define KERNEL_TO(NAME,FUNC) \
__attribute__((noinline)) static uint64_t NAME(uint64_t count) { \
    uint64_t sum=0; for(uint64_t i=0;i<count;++i) \
        sum+=FUNC(doubles[i&(COUNT-1)]); return sum; }
KERNEL_FROM(ref_from,ref_dolrecomp_f32_from_bits)
KERNEL_FROM(cand_from,cand_dolrecomp_f32_from_bits)
KERNEL_FROM(boundary_from,boundary_dolrecomp_f32_from_bits)
KERNEL_TO(boundary_to,boundary_dolrecomp_f32_to_bits)
KERNEL_TO(ref_to,ref_dolrecomp_f32_to_bits)
KERNEL_TO(cand_to,cand_dolrecomp_f32_to_bits)
static double cpu_seconds(void) {
    struct timespec t; if(clock_gettime(CLOCK_THREAD_CPUTIME_ID,&t)) exit(4);
    return (double)t.tv_sec+(double)t.tv_nsec/1e9;
}
static int bench(uint64_t count) {
    const char *names[]={"finite","random_bits","subnormal","special"};
    for(unsigned corpus=0;corpus<4;++corpus) {
        uint64_t state=UINT64_C(0x4d595df4d0f33173);
        for(unsigned i=0;i<COUNT;++i) {
            uint64_t r=random64(&state); uint32_t x=(uint32_t)r;
            if(corpus==0) x=(x&0x807fffffu)|((96u+(x%64u))<<23);
            if(corpus==2) x=(x&0x807fffffu)|1u;
            if(corpus==3) x=i%3 ? x|0x7f800000u : x&0x80000000u;
            words[i]=x;
            doubles[i]=corpus==1 ? as_double(r) : ref_dolrecomp_f32_from_bits(x);
        }
        for(unsigned shape=0;shape<2;++shape) for(unsigned operation=0;operation<2;++operation) for(unsigned round=0;round<6;++round) {
            uint64_t sums[2];
            for(unsigned order=0;order<2;++order) {
                unsigned candidate=(round+order)&1u;
                uint64_t (*fn)(uint64_t)=operation ? (candidate?cand_to:(shape?boundary_to:ref_to)) :
                    (candidate?cand_from:(shape?boundary_from:ref_from));
                sink=fn(COUNT*4); // Identical bounded warmup outside timing.
                double start=cpu_seconds();
                uint64_t sum=fn(count); sink=sum;
                double duration=cpu_seconds()-start; sums[candidate]=sum;
                printf("{\"shape\":%u,\"corpus\":\"%s\",\"operation\":\"%s\",\"round\":%u,\"candidate\":%s,\"count\":%" PRIu64 ",\"cpu_seconds\":%.9f,\"checksum\":\"%016" PRIx64 "\"}\n",
                    shape,names[corpus],operation?"to":"from",round,candidate?"true":"false",count,duration,sum);
                fflush(stdout);
            }
            if(sums[0]!=sums[1]) return 5;
        }
    }
    return 0;
}
int main(int argc,char **argv) {
    if(argc<2) return 1;
    if(strcmp(argv[1],"check")==0) return check(argc>2 && strcmp(argv[2],"exhaustive")==0);
    if(strcmp(argv[1],"bench")==0) return bench(argc>2?strtoull(argv[2],NULL,10):UINT64_C(33554432));
    return 1;
}
'''


def prepare(output):
    output = Path(output).resolve()
    if not output.is_relative_to(ROOT / 'local'):
        raise ValueError('Use a fresh directory under local/')
    output.mkdir(parents=True, exist_ok=False)
    original = GENERATED.read_text()
    candidate = split_helpers(original)
    start, end = helper_span(original)
    cstart = candidate.index('static __attribute__((noinline, cold)) f64')
    cend = candidate.index('static inline f64 dolrecomp_f64_from_bits')
    reference_functions = original[start:end].replace('dolrecomp_', 'ref_dolrecomp_')
    candidate_functions = candidate[cstart:cend].replace('dolrecomp_', 'cand_dolrecomp_')
    boundary_functions = original[start:end].replace('dolrecomp_', 'boundary_dolrecomp_').replace(
        'static inline ', 'static __attribute__((noinline)) ')
    source = ('#include <stdint.h>\n#include <string.h>\n'
              'typedef uint32_t u32; typedef uint64_t u64; typedef double f64;\n' +
              reference_functions + boundary_functions + candidate_functions + HARNESS)
    (output / 'reference-generated.h').write_text(original)
    (output / 'candidate-generated.h').write_text(candidate)
    (output / 'check.c').write_text(source)
    compiler = Path('/usr/bin/clang')
    command = [str(compiler), *FLAGS, str(output / 'check.c'), '-o', str(output / 'check')]
    subprocess.run(command, check=True)
    record = dict(schema=1, platform=platform.platform(), command=command,
                  compiler_sha256=sha(compiler), compiler_version=subprocess.check_output(
                      [str(compiler), '--version'], text=True).splitlines()[0],
                  original_header_sha256=sha(GENERATED), candidate_header_sha256=sha(output / 'candidate-generated.h'),
                  harness_sha256=sha(output / 'check.c'), binary_sha256=sha(output / 'check'), tool_sha256=sha(__file__))
    (output / 'build.json').write_text(json.dumps(record, indent=2) + '\n')
    return record


def run(args):
    output = args.output.resolve()
    if not output.is_relative_to(ROOT / 'local'):
        raise ValueError('Use evidence under local/')
    verify_conversion_receipt(output, require_check=args.command != 'check')
    receipt = json.loads((output / 'build.json').read_text())
    if args.command == 'check':
        command = [str(output / 'check'), 'check'] + (['exhaustive'] if args.exhaustive else [])
        result = subprocess.check_output(command, text=True)
        record = json.loads(result)
    else:
        if not 1048576 <= args.iterations <= 268435456:
            raise ValueError('Use 2^20–2^28 iterations per timed case')
        command = [str(output / 'check'), 'bench', str(args.iterations)]
        with (output / 'bench.jsonl').open('w') as log:
            subprocess.run(command, stdout=log, check=True)
        rows = [json.loads(line) for line in (output / 'bench.jsonl').read_text().splitlines()]
        comparison = []
        for shape in (0, 1):
            for corpus in ('finite', 'random_bits', 'subnormal', 'special'):
                for op in ('from', 'to'):
                    values = {kind: [r['cpu_seconds'] for r in rows if r['shape'] == shape and
                                    r['corpus'] == corpus and r['operation'] == op and r['candidate'] == kind]
                              for kind in (False, True)}
                    if any(len(v) != 6 or min(v) <= 0 for v in values.values()):
                        raise ValueError('Incomplete or invalid timed comparison')
                    a, b = (statistics.median(values[k]) for k in (False, True))
                    paired = [next(r['cpu_seconds'] for r in rows if r['shape'] == shape and
                                   r['corpus'] == corpus and r['operation'] == op and r['round'] == n and r['candidate']) /
                              next(r['cpu_seconds'] for r in rows if r['shape'] == shape and
                                   r['corpus'] == corpus and r['operation'] == op and r['round'] == n and not r['candidate'])
                              for n in range(6)]
                    comparison.append(dict(shape='outlined_reference' if shape else 'compiler_choice',
                                           corpus=corpus, operation=op, reference_cpu_seconds=a,
                                           candidate_cpu_seconds=b, candidate_over_reference=b/a,
                                           paired_ratios=paired))
        record = dict(comparison=comparison, rows=len(rows), iterations=args.iterations,
                      limits='Synthetic equal-input kernels: compiler-choice and forced reference call-boundary shapes. '
                             'The latter models actual outlined calls observed in the hot game chunk. '
                             'No game or phone speedup established.')
    record['binary_sha256'] = receipt['binary_sha256']
    record['command'] = command
    (output / (args.command + '.json')).write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('prepare', 'check', 'bench'):
        child = sub.add_parser(name)
        child.add_argument('--output', type=Path, required=True)
        if name == 'check':
            child.add_argument('--exhaustive', action='store_true')
        if name == 'bench':
            child.add_argument('--iterations', type=int, default=33554432)
    args = parser.parse_args()
    if args.command == 'prepare':
        print(json.dumps(prepare(args.output), indent=2))
    else:
        run(args)
