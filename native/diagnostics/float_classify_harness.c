// Isolated reference/candidate arithmetic checks. Never linked into the app.
#include "cpu_interpreter_private.h"
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define DECLARE(P) \
u32 P##_classify_f32(f32); u32 P##_classify_f64(f64); \
void P##_ppc_fpscr_control_updated(CPUState*); \
void P##_ppc_fadds(CPUState*,u8,u8,u8); \
void P##_ppc_fmuls(CPUState*,u8,u8,u8); \
bool P##_ppc_fma(CPUState*,f64,f64,f64,bool,bool,bool,f64*); \
void P##_ppc_fmadd_op(CPUState*,u8,u8,u8,u8,bool,bool,bool);
DECLARE(reference)
DECLARE(candidate)
DECLARE(scoped)

static uint64_t rng=UINT64_C(0xa5106b394f2d1738);
static uint64_t random_bits(void) {
  rng^=rng<<13; rng^=rng>>7; rng^=rng<<17; return rng;
}
static uint64_t fpcr(void) {
  uint64_t value=0;
#if defined(__aarch64__)
  __asm__ __volatile__("mrs %0, fpcr":"=r"(value));
#endif
  return value;
}
static void set_fpcr(uint64_t value) {
#if defined(__aarch64__)
  __asm__ __volatile__("msr fpcr, %0"::"r"(value));
#else
  (void)value;
#endif
}
static uint64_t fpsr(void) {
  uint64_t value=0;
#if defined(__aarch64__)
  __asm__ __volatile__("mrs %0, fpsr":"=r"(value));
#endif
  return value;
}
static void set_fpsr(uint64_t value) {
#if defined(__aarch64__)
  __asm__ __volatile__("msr fpsr, %0"::"r"(value));
#else
  (void)value;
#endif
}
static void die(const char* message) { fprintf(stderr,"%s\n",message);exit(1); }
static u32 expected_class(u32 sign,u32 exponent,u32 max_exponent,bool fraction) {
  if(exponent==max_exponent)return fraction?17:(sign?9:5);
  if(!exponent)return fraction?(sign?24:20):(sign?18:2);
  return sign?8:4;
}

static uint64_t classifiers(void) {
  uint64_t count=0;
  // Every sign/exponent and every single fraction bit plus zero/all-ones.
  // This covers all predicates used by the classifier, not all 2^32/2^64 inputs.
  for(u32 sign=0;sign<2;++sign)for(u32 exp=0;exp<256;++exp)for(u32 f=0;f<25;++f) {
    u32 fraction=f==0?0:f==24?0x7fffff:1u<<(f-1);
    u32 bits=sign<<31|exp<<23|fraction,expected=expected_class(sign,exp,255,fraction!=0);
    if(reference_classify_f32(f32_value(bits))!=expected || candidate_classify_f32(f32_value(bits))!=expected ||
       scoped_classify_f32(f32_value(bits))!=expected)
      die("f32 classifier differs from category oracle");
    ++count;
  }
  for(u32 sign=0;sign<2;++sign)for(u32 exp=0;exp<2048;++exp)for(u32 f=0;f<54;++f) {
    u64 fraction=f==0?0:f==53?UINT64_C(0xfffffffffffff):UINT64_C(1)<<(f-1);
    u64 bits=(u64)sign<<63|(u64)exp<<52|fraction;
    u32 expected=expected_class(sign,exp,2047,fraction!=0);
    if(reference_classify_f64(f64_value(bits))!=expected || candidate_classify_f64(f64_value(bits))!=expected ||
       scoped_classify_f64(f64_value(bits))!=expected)
      die("f64 classifier differs from category oracle");
    ++count;
  }
  return count;
}

typedef struct { bool wrote; u64 output; } Result;
#define APPLY(P) \
static Result apply_##P(CPUState* cpu,unsigned operation,const u8 regs[4]) { \
  const u8 d=regs[0],a=regs[1],b=regs[2],c=regs[3]; \
  Result result={true,UINT64_C(0x7ff8123456789abc)}; \
  if(operation==0)P##_ppc_fadds(cpu,d,a,b); \
  else if(operation==1)P##_ppc_fmuls(cpu,d,a,c); \
  else { \
    const unsigned flags=(operation-2)&7; \
    const bool single=flags&1,subtract=flags&2,negative=flags&4; \
    if(operation<10) { \
      f64 output=f64_value(result.output); \
      result.wrote=P##_ppc_fma(cpu,cpu->fpr[a],cpu->fpr[c],cpu->fpr[b],single,subtract,negative,&output); \
      result.output=f64_bits(output); \
      if(result.wrote) { cpu->fpr[d]=output; if(single)cpu->ps1[d]=output; } \
    } else P##_ppc_fmadd_op(cpu,d,a,c,b,single,subtract,negative); \
  } \
  return result; \
}
APPLY(reference)
APPLY(candidate)
APPLY(scoped)

static const u8 aliases[][4]={{0,1,2,3},{1,1,2,3},{2,1,2,3},{3,1,2,3},{3,3,3,3}};
static uint64_t arithmetic_cases=0;
static void check_case(u64 a,u64 b,u64 c,u32 initial_fpscr,unsigned alias) {
  CPUState initial;memset(&initial,0,sizeof(initial));
  for(unsigned i=0;i<32;++i) {
    initial.gpr[i]=0xa5a50000u+i;
    initial.fpr[i]=f64_value(UINT64_C(0x3ff0123400000000)+i);
    initial.ps1[i]=f64_value(UINT64_C(0xc001234000000000)+i);
  }
  initial.pc=0x8010550c;initial.lr=0x802197a0;initial.cr=0x12345678;
  initial.timebase=UINT64_C(0x123456789abcdef);initial.fpscr=initial_fpscr;
  initial.exception=0x4321;initial.downcount=-17;
  const u8* regs=aliases[alias];
  initial.fpr[regs[1]]=f64_value(a);initial.fpr[regs[2]]=f64_value(b);initial.fpr[regs[3]]=f64_value(c);
  for(unsigned operation=0;operation<18;++operation) {
    CPUState expected;
    memcpy(&expected,&initial,sizeof(initial));
    const u64 initial_fpsr=(arithmetic_cases/18)&1?UINT64_C(0x0800009f):0;
    reference_ppc_fpscr_control_updated(&expected);set_fpsr(initial_fpsr);
    Result r=apply_reference(&expected,operation,regs);u64 expected_fpsr=fpsr(),expected_fpcr=fpcr();
    for(unsigned variant=0;variant<2;++variant) {
      CPUState actual;memcpy(&actual,&initial,sizeof(initial));
      if(variant)scoped_ppc_fpscr_control_updated(&actual);else candidate_ppc_fpscr_control_updated(&actual);
      set_fpsr(initial_fpsr);
      Result s=variant?apply_scoped(&actual,operation,regs):apply_candidate(&actual,operation,regs);
      u64 actual_fpsr=fpsr(),actual_fpcr=fpcr();
      if(memcmp(&expected,&actual,sizeof(actual)) || r.wrote!=s.wrote || r.output!=s.output ||
         expected_fpsr!=actual_fpsr || expected_fpcr!=actual_fpcr) {
        fprintf(stderr,"Mismatch op=%u variant=%s alias=%u fpscr=%08x a=%016"PRIx64" b=%016"PRIx64" c=%016"PRIx64"\n",
                operation,variant?"scoped":"candidate",alias,initial_fpscr,a,b,c);
        exit(1);
      }
    }
    ++arithmetic_cases;
  }
}

static void differential(void) {
  const u64 edge[]={
    0,UINT64_C(0x8000000000000000),1,UINT64_C(0x8000000000000001),
    UINT64_C(0x000fffffffffffff),UINT64_C(0x0010000000000000),
    UINT64_C(0x380fffffe0000000),UINT64_C(0x3810000000000000),
    UINT64_C(0x36a0000000000000),UINT64_C(0x3690000000000000),
    UINT64_C(0x3ff0000000000000),UINT64_C(0xbff0000000000000),
    UINT64_C(0x4000000000000000),UINT64_C(0xc000000000000000),
    UINT64_C(0x3ff0000010000000),UINT64_C(0x3ff000000fffffff),UINT64_C(0x3ff0000010000001),
    UINT64_C(0x3ff0000007ffffff),UINT64_C(0x3ff0000008000000),UINT64_C(0x3ff0000008000001),
    UINT64_C(0x47efffffe0000000),UINT64_C(0x47effffff0000000),UINT64_C(0x47f0000000000000),
    UINT64_C(0x7fefffffffffffff),UINT64_C(0xffefffffffffffff),
    UINT64_C(0x7ff0000000000000),UINT64_C(0xfff0000000000000),
    UINT64_C(0x7ff8000012345678),UINT64_C(0xfff8000098765432),
    UINT64_C(0x7ff0000012345678),UINT64_C(0xfff0000098765432),
    UINT64_C(0x7ff0000000000001),UINT64_C(0x7fffffffffffffff)};
  const unsigned n=sizeof(edge)/sizeof(edge[0]);
  const u32 flags[]={0,FPSCR_VE_BIT,FPSCR_FI_BIT|FPSCR_FR_BIT,0xffffff80u};
  for(unsigned mode=0;mode<8;++mode)for(unsigned i=0;i<n;++i)for(unsigned j=0;j<n;++j)
    check_case(edge[i],edge[j],edge[(i*7+j*13)%n],flags[(i+j)%4]|mode,(i+j)%5);
  // Cross all mode/sticky-flag/alias combinations on deliberate exceptional triples.
  for(unsigned mode=0;mode<8;++mode)for(unsigned flag=0;flag<4;++flag)for(unsigned alias=0;alias<5;++alias)
    for(unsigned i=0;i<n;++i)check_case(edge[i],edge[(i+11)%n],edge[(i+25)%n],flags[flag]|mode,alias);
  for(unsigned i=0;i<10000;++i) {
    u64 a=random_bits(),b=random_bits(),c=random_bits();
    check_case(a,b,c,(u32)random_bits(),i%5);
  }
}

static double thread_seconds(void) {
  struct timespec value;
  if(clock_gettime(CLOCK_THREAD_CPUTIME_ID,&value))die("clock_gettime failed");
  return value.tv_sec+value.tv_nsec/1e9;
}
static uint64_t corpus[1024][3];
static void make_corpus(bool mixed) {
  rng=UINT64_C(0xa5106b394f2d1738);
  for(unsigned i=0;i<1024;++i)for(unsigned j=0;j<3;++j) {
    u32 bits=(u32)random_bits();
    bits=(bits&0x807fffffu)|((120u+(bits>>24)%15u)<<23);
    corpus[i][j]=f64_bits((f64)f32_value(bits));
  }
  // A separate stress corpus adds 1/64 special-input triples. It is not a
  // measured distribution from the game; the normal corpus is also synthetic.
  const u64 special[]={0,UINT64_C(0x8000000000000000),1,UINT64_C(0x7ff0000000000000),
    UINT64_C(0xfff0000000000000),UINT64_C(0x7ff8000012345678),
    UINT64_C(0x7ff0000012345678),UINT64_C(0x7fefffffffffffff)};
  if(mixed)for(unsigned i=0;i<1024;i+=64)for(unsigned j=0;j<3;++j)
    corpus[i][j]=special[(i/64+j*3)%8];
}

static uint64_t benchmark(unsigned variant,unsigned op,unsigned iterations,double* elapsed) {
  CPUState cpu={0};cpu.fpscr=0;reference_ppc_fpscr_control_updated(&cpu);
  const u8 regs[]={0,1,2,3};u64 sum=0;
  Result (*apply)(CPUState*,unsigned,const u8*)=variant==2?apply_scoped:variant==1?apply_candidate:apply_reference;
  const double start=thread_seconds();
  for(unsigned i=0;i<iterations;++i) {
    cpu.fpr[1]=f64_value(corpus[i&1023][0]);
    cpu.fpr[2]=f64_value(corpus[i&1023][1]);
    cpu.fpr[3]=f64_value(corpus[i&1023][2]);
    apply(&cpu,op,regs);
    sum^=f64_bits(cpu.fpr[0])+(u64)cpu.fpscr+i;
  }
  *elapsed=thread_seconds()-start;
  return sum;
}

int main(int argc,char** argv) {
  const u64 saved_fpcr=fpcr(),saved_fpsr=fpsr();
  if(argc==2 && !strcmp(argv[1],"check")) {
    uint64_t categories=classifiers();differential();
    set_fpcr(saved_fpcr);set_fpsr(saved_fpsr);
    printf("{\"passed\":true,\"classifier_category_cases\":%"PRIu64",\"arithmetic_cases\":%"PRIu64",\"candidate_comparisons\":%"PRIu64",\"cpu_state_bytes\":%zu,\"host_fpcr_fpsr_compared\":%s}\n",
           categories,arithmetic_cases,arithmetic_cases*2,sizeof(CPUState),
#if defined(__aarch64__)
           "true"
#else
           "false"
#endif
    );
  } else if(argc==4 && !strcmp(argv[1],"bench")) {
    unsigned variant=!strcmp(argv[2],"scoped")?2:!strcmp(argv[2],"candidate")?1:0;
    unsigned iterations=(unsigned)strtoul(argv[3],NULL,10);
    if((!variant && strcmp(argv[2],"reference")) || iterations<1000)die("Invalid benchmark arguments");
    const unsigned ops[]={0,1,3,2,11};
    const char* names[]={"fadds","fmuls","generated_fma_single","generated_fma_double","interpreter_fmadd_single"};
    printf("{\"variant\":\"%s\",\"cases\":[",argv[2]);
    for(unsigned mixed=0;mixed<2;++mixed) {
      make_corpus(mixed);
      for(unsigned i=0;i<5;++i) {
      double elapsed;benchmark(variant,ops[i],10000,&elapsed);
      u64 checksum=benchmark(variant,ops[i],iterations,&elapsed);
      printf("%s{\"operation\":\"%s\",\"corpus\":\"%s\",\"calls\":%u,\"thread_cpu_seconds\":%.9f,\"ns_per_call\":%.4f,\"checksum\":\"%016"PRIx64"\"}",
             i||mixed?",":"",names[i],mixed?"special_1_in_64":"normal_finite",
             iterations,elapsed,elapsed*1e9/iterations,checksum);
      }
    }
    set_fpcr(saved_fpcr);set_fpsr(saved_fpsr);puts("]}");
  } else die("Use check or bench reference|candidate|scoped ITERATIONS");
  return 0;
}
