/* Observation only: each intercepted call forwards the original arguments once
 * and returns its exact result. No parser flush, demand request or guest write.
 * _Exit is intercepted because the unchanged runner bypasses destructors.
 */
#include "e20_parser_observer.h"
#include <libavcodec/avcodec.h>
#include <libavutil/error.h>
#include <dlfcn.h>
#include <errno.h>
#include <inttypes.h>
#include <pthread.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

static pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
static FILE *logFile, *payloadFile;
static E20ParserStats stats;
static uint64_t seq, textBytes, payloadBytes, startNs;
static int enabled, closed, proof;
static _Thread_local unsigned parseDepth,sendDepth,receiveDepth,exitDepth;
enum { TEXT_CAP=12*1024*1024, PAYLOAD_CAP=2*1024*1024 };
static int (*real_parse)(AVCodecParserContext*,AVCodecContext*,uint8_t**,int*,const uint8_t*,int,int64_t,int64_t,int64_t);
static int (*real_send)(AVCodecContext*,const AVPacket*);
static int (*real_receive)(AVCodecContext*,AVFrame*);
static void (*real_Exit)(int);
static int observed_parse(AVCodecParserContext*,AVCodecContext*,uint8_t**,int*,const uint8_t*,int,int64_t,int64_t,int64_t);
static int observed_send(AVCodecContext*,const AVPacket*);
static int observed_receive(AVCodecContext*,AVFrame*);
__attribute__((noreturn)) static void observed_Exit(int);

static uint64_t now_ns(void) {
    struct timespec t; clock_gettime(CLOCK_MONOTONIC,&t);
    return (uint64_t)t.tv_sec*1000000000ull+t.tv_nsec;
}
static uint64_t tid(void) { uint64_t value=0; pthread_threadid_np(NULL,&value); return value; }
static uint64_t hash(const uint8_t *p,size_t n) {
    uint64_t h=14695981039346656037ull;
    for(size_t i=0;i<n;i++) { h^=p[i];h*=1099511628211ull; }
    return h;
}
/* Called with the observation mutex only; never held over a real API call. */
static void event(const char *format,...) {
    if(!enabled || closed)return;
    char line[2048];
    int base=snprintf(line,sizeof(line),"seq=%" PRIu64 " ns=%" PRIu64 " tid=%" PRIu64 " ",++seq,now_ns()-startNs,tid());
    va_list ap; va_start(ap,format);
    int n=vsnprintf(line+base,sizeof(line)-(size_t)base,format,ap);va_end(ap);
    if(n<0 || base+n+1>=(int)sizeof(line)) {stats.textTruncated=1;return;}
    size_t len=(size_t)(base+n);line[len++]='\n';
    if(textBytes+len>TEXT_CAP-4096) {stats.textTruncated=1;return;}
    if(fwrite(line,1,len,logFile)!=len || fflush(logFile)!=0)++stats.ioErrors;
    textBytes+=len;
}
static void binding(const char *api,void *original,void *replacement,const char *expectedImage) {
    Dl_info info={0};
    const int valid=original!=replacement && dladdr(original,&info) && info.dli_fname && strstr(info.dli_fname,expectedImage);
    /* These lookups are address-only controls. Never invoke either candidate. */
    void *next=dlsym(RTLD_NEXT,api),*handle=NULL,*explicitAddress=NULL;
    if(valid) {
        handle=dlopen(info.dli_fname,RTLD_NOW|RTLD_LOCAL|RTLD_FIRST);
        if(handle)explicitAddress=dlsym(handle,api);
    }
    event("kind=binding api=%s method=direct-import original=%p replacement=%p next=%p explicit=%p nextIsReplacement=%d explicitIsReplacement=%d valid=%d image=%s symbol=%s",
          api,original,replacement,next,explicitAddress,next==replacement,explicitAddress==replacement,valid,
          valid?info.dli_fname:"unresolved",valid&&info.dli_sname?info.dli_sname:"unresolved");
    if(handle)dlclose(handle);
    if(!valid)_exit(126);
    ++stats.bindingChecks;
}
__attribute__((constructor)) static void initialize(void) {
    /* dyld preserves original imports in the image containing __interpose.
     * Unlike dlsym's globally interposed result, these are the real bindings. */
    real_parse=av_parser_parse2;
    real_send=avcodec_send_packet;
    real_receive=avcodec_receive_frame;
    real_Exit=_Exit;
    if(!real_parse || !real_send || !real_receive || !real_Exit)_exit(126);
    const char *dir=getenv("PS2X_E20_PARSER_DIR");if(!dir)return;
    char path[4096];
    if(snprintf(path,sizeof(path),"%s/parser-events.txt",dir)>=(int)sizeof(path))_exit(126);
    logFile=fopen(path,"wx");if(!logFile)_exit(126);
    if(snprintf(path,sizeof(path),"%s/parser-input.bin",dir)>=(int)sizeof(path))_exit(126);
    payloadFile=fopen(path,"wx");if(!payloadFile)_exit(126);
    startNs=now_ns();enabled=1;proof=getenv("PS2X_E20_PROOF")!=NULL;
    event("kind=observer-open pid=%d schema=2 proof=%d textCap=%d payloadCap=%d",getpid(),proof,TEXT_CAP,PAYLOAD_CAP);
    binding("av_parser_parse2",(void*)real_parse,(void*)observed_parse,"/libavcodec.");
    binding("avcodec_send_packet",(void*)real_send,(void*)observed_send,"/libavcodec.");
    binding("avcodec_receive_frame",(void*)real_receive,(void*)observed_receive,"/libavcodec.");
    binding("_Exit",(void*)real_Exit,(void*)observed_Exit,"/usr/lib/system/");
}
void e20_parser_snapshot(E20ParserStats *out) {
    pthread_mutex_lock(&mutex);*out=stats;pthread_mutex_unlock(&mutex);
}
void e20_parser_mark(const char *label,uint64_t bytes) {
    pthread_mutex_lock(&mutex);
    event("kind=mark label=%s bytes=%" PRIu64 " parseCalls=%" PRIu64 " consumed=%" PRIu64 " packets=%" PRIu64 " frames=%" PRIu64,
          label,bytes,stats.parseCalls,stats.consumed,stats.packets,stats.frames);
    pthread_mutex_unlock(&mutex);
}
static void close_observation(const char *reason,int rc) {
    pthread_mutex_lock(&mutex);
    if(enabled && !closed) {
        if(fflush(payloadFile)!=0)++stats.ioErrors;
        char line[2048];
        int n=snprintf(line,sizeof(line),"# E20 PARSER CLOSURE source=API-interposer reason=%s rc=%d ns=%" PRIu64
            " events=%" PRIu64 " parseCalls=%" PRIu64 " offered=%" PRIu64 " consumed=%" PRIu64 " packets=%" PRIu64 " packetBytes=%" PRIu64
            " sendCalls=%" PRIu64 " sendEof=%" PRIu64 " receiveCalls=%" PRIu64 " frames=%" PRIu64 " errors=%" PRIu64
            " returned=%" PRIu64 " pending=%" PRIu64 " textTruncated=%" PRIu64 " payloadTruncated=%" PRIu64 " ioErrors=%" PRIu64
            " eventBytes=%" PRIu64 " payloadBytes=%" PRIu64 " backendParse=%" PRIu64 " backendSend=%" PRIu64 " backendReceive=%" PRIu64
            " bindingChecks=%" PRIu64 " recursionGuards=%" PRIu64 " proof=%d\n",
            reason,rc,now_ns()-startNs,seq,stats.parseCalls,stats.offered,stats.consumed,stats.packets,stats.packetBytes,
            stats.sendCalls,stats.sendEof,stats.receiveCalls,stats.frames,stats.errors,stats.returned,stats.pending,
            stats.textTruncated,stats.payloadTruncated,stats.ioErrors,textBytes,payloadBytes,
            stats.backendParse,stats.backendSend,stats.backendReceive,stats.bindingChecks,stats.recursionGuards,proof);
        if(n>0 && n<(int)sizeof(line))fwrite(line,1,(size_t)n,logFile);
        fflush(logFile);closed=1;fclose(payloadFile);fclose(logFile);
    }
    pthread_mutex_unlock(&mutex);
}
__attribute__((destructor)) static void finish(void) {close_observation("destructor",0);}
static int observed_parse(AVCodecParserContext *parser,AVCodecContext *codec,uint8_t **output,int *outputSize,
                          const uint8_t *input,int size,int64_t pts,int64_t dts,int64_t pos) {
    const int savedErrno=errno;
    if(parseDepth++)_exit(125); /* A failed forwarding proof must not recurse. */
    uint64_t call=0;
    if(enabled) {
        pthread_mutex_lock(&mutex);call=++stats.parseCalls;++stats.pending;
        uint64_t offset=payloadBytes,kept=0,fnv=0;
        char first[129]={0};
        if(input && size>0) {
            stats.offered+=(uint64_t)size;fnv=hash(input,(size_t)size);
            size_t n=(size_t)size<64?(size_t)size:64;
            for(size_t i=0;i<n;i++)snprintf(first+2*i,3,"%02x",input[i]);
            kept=(uint64_t)size;
            if(kept>PAYLOAD_CAP-payloadBytes) {kept=PAYLOAD_CAP-payloadBytes;stats.payloadTruncated=1;}
            if(kept && (fwrite(input,1,(size_t)kept,payloadFile)!=kept || fflush(payloadFile)!=0))++stats.ioErrors;
            payloadBytes+=kept;
        }
        event("kind=parse-enter call=%" PRIu64 " parser=%p codec=%p size=%d pts=%" PRId64 " dts=%" PRId64 " pos=%" PRId64
              " payloadOffset=%" PRIu64 " kept=%" PRIu64 " fnv64=0x%016" PRIx64 " first64=%s",call,(void*)parser,(void*)codec,size,pts,dts,pos,offset,kept,fnv,first);
        ++stats.backendParse;
        if(proof)event("kind=backend-enter api=parse call=%" PRIu64 " function=%p parser=%p codec=%p output=%p outputSize=%p input=%p size=%d pts=%" PRId64 " dts=%" PRId64 " pos=%" PRId64,
            call,(void*)real_parse,(void*)parser,(void*)codec,(void*)output,(void*)outputSize,(void*)input,size,pts,dts,pos);
        pthread_mutex_unlock(&mutex);
    }
    errno=savedErrno;
    int result=real_parse(parser,codec,output,outputSize,input,size,pts,dts,pos),afterErrno=errno;
    if(enabled) {
        pthread_mutex_lock(&mutex);--stats.pending;++stats.returned;
        if(result>0)stats.consumed+=(uint64_t)result;
        if(result<0)++stats.errors;
        if(*outputSize>0) {++stats.packets;stats.packetBytes+=(uint64_t)*outputSize;}
        event("kind=parse-return call=%" PRIu64 " used=%d packetSize=%d consumed=%" PRIu64 " packets=%" PRIu64 " packetFNV64=0x%016" PRIx64,
              call,result,*outputSize,stats.consumed,stats.packets,(*output && *outputSize>0)?hash(*output,(size_t)*outputSize):0);
        pthread_mutex_unlock(&mutex);
    }
    --parseDepth;errno=afterErrno;return result;
}
static int observed_send(AVCodecContext *codec,const AVPacket *packet) {
    int before=errno;uint64_t call=0;
    if(sendDepth++)_exit(125);
    if(enabled) {pthread_mutex_lock(&mutex);call=++stats.sendCalls;++stats.pending;if(!packet)++stats.sendEof;
        event("kind=send-enter call=%" PRIu64 " codec=%p size=%d eof=%d",call,(void*)codec,packet?packet->size:0,!packet);
        ++stats.backendSend;
        if(proof)event("kind=backend-enter api=send call=%" PRIu64 " function=%p codec=%p packet=%p",call,(void*)real_send,(void*)codec,(void*)packet);
        pthread_mutex_unlock(&mutex);}
    errno=before;int result=real_send(codec,packet),after=errno;
    if(enabled) {pthread_mutex_lock(&mutex);--stats.pending;++stats.returned;
        if(result<0 && result!=AVERROR(EAGAIN) && result!=AVERROR_EOF)++stats.errors;
        event("kind=send-return call=%" PRIu64 " rc=%d",call,result);pthread_mutex_unlock(&mutex);}
    --sendDepth;errno=after;return result;
}
static int observed_receive(AVCodecContext *codec,AVFrame *frame) {
    int before=errno;uint64_t call=0;
    if(receiveDepth++)_exit(125);
    if(enabled) {pthread_mutex_lock(&mutex);call=++stats.receiveCalls;++stats.pending;++stats.backendReceive;
        if(proof)event("kind=backend-enter api=receive call=%" PRIu64 " function=%p codec=%p frame=%p",call,(void*)real_receive,(void*)codec,(void*)frame);
        pthread_mutex_unlock(&mutex);}
    errno=before;int result=real_receive(codec,frame),after=errno;
    if(enabled) {pthread_mutex_lock(&mutex);--stats.pending;++stats.returned;if(result==0)++stats.frames;
        if(result<0 && result!=AVERROR(EAGAIN) && result!=AVERROR_EOF)++stats.errors;
        event("kind=receive-return call=%" PRIu64 " codec=%p rc=%d width=%d height=%d frames=%" PRIu64,
              call,(void*)codec,result,result==0?frame->width:0,result==0?frame->height:0,stats.frames);pthread_mutex_unlock(&mutex);}
    --receiveDepth;errno=after;return result;
}
__attribute__((noreturn)) static void observed_Exit(int status) {
    int saved=errno;if(exitDepth++)_exit(125);
    close_observation("_Exit",status);errno=saved;real_Exit(status);__builtin_unreachable();
}
#define INTERPOSE(replacement,original) \
    __attribute__((used)) static const struct {const void *replacement;const void *original;} \
    interpose_##original __attribute__((section("__DATA,__interpose"))) = {(const void*)&replacement,(const void*)&original}
INTERPOSE(observed_parse,av_parser_parse2);
INTERPOSE(observed_send,avcodec_send_packet);
INTERPOSE(observed_receive,avcodec_receive_frame);
INTERPOSE(observed_Exit,_Exit);
