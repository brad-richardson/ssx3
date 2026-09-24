#include <arm_neon.h>
#include <chrono>
#include <cstdio>
#include <cstring>
#include <cstdint>
static inline float clampOp(float x){uint32_t u;memcpy(&u,&x,4); if((u&0x7F800000u)==0x7F800000u){u=(u&0x80000000u)|0x7F7FFFFFu;memcpy(&x,&u,4);} return x;}
static inline float32x4_t clampV(float32x4_t v){uint32x4_t u=vreinterpretq_u32_f32(v);uint32x4_t e=vandq_u32(u,vdupq_n_u32(0x7F800000u));uint32x4_t inf=vceqq_u32(e,vdupq_n_u32(0x7F800000u));uint32x4_t c=vorrq_u32(vandq_u32(u,vdupq_n_u32(0x80000000u)),vdupq_n_u32(0x7F7FFFFFu));return vreinterpretq_f32_u32(vbslq_u32(inf,c,u));}
int main(){
  const int N=4096, R=20000; static float a[N],b[N],o[N]; static float32x4_t va[N],vb[N],vo[N];
  for(int i=0;i<N;i++){a[i]=1.0f+i*1e-3f;b[i]=0.5f+i*1e-4f;va[i]=vdupq_n_f32(a[i]);vb[i]=vdupq_n_f32(b[i]);}
  auto t=[&](auto f){auto s=std::chrono::steady_clock::now();for(int r=0;r<R;r++){f();asm volatile(""::"r"(o),"r"(vo):"memory");}return std::chrono::duration<double>(std::chrono::steady_clock::now()-s).count()/(double(N)*R)*1e9;};
  double s0=t([&]{for(int i=0;i<N;i++)o[i]=a[i]*b[i]+o[i];});
  double s1=t([&]{for(int i=0;i<N;i++)o[i]=clampOp(clampOp(a[i])*clampOp(b[i]))+clampOp(o[i]);});
  double v0=t([&]{for(int i=0;i<N;i++)vo[i]=vaddq_f32(vmulq_f32(va[i],vb[i]),vo[i]);});
  double v1=t([&]{for(int i=0;i<N;i++)vo[i]=vaddq_f32(vmulq_f32(clampV(va[i]),clampV(vb[i])),clampV(vo[i]));});
  printf("scalar mul+add: %.3f ns/iter plain, %.3f clamped (x%.2f)\nvector mul+add: %.3f ns/iter plain, %.3f clamped (x%.2f)\n",s0,s1,s1/s0,v0,v1,v1/v0);
}
