/* E21 minimal non-title isolation harness. No guest runtime, no title boot.
 * Modes: feed <input> <result-out> | exitcode <status> | addrs
 * feed: parser+decoder over fixed chunks; canonical result record on stdout/file.
 * exitcode: one parse call then _Exit(status) to prove closure interception.
 * addrs: address-only mechanism comparison; never invokes any candidate.
 */
#include <libavcodec/avcodec.h>
#include <dlfcn.h>
#include <errno.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static uint64_t fnv(const uint8_t *p, size_t n) {
    uint64_t h = 14695981039346656037ull;
    for (size_t i = 0; i < n; i++) { h ^= p[i]; h *= 1099511628211ull; }
    return h;
}
static uint64_t frame_fnv(const AVFrame *f) {
    uint64_t h = 14695981039346656037ull;
    int planes = f->data[2] ? 3 : (f->data[1] ? 2 : 1);
    int hs = (planes == 3 && (f->format == AV_PIX_FMT_YUV420P || f->format == AV_PIX_FMT_YUVJ420P)) ? 2 : 1;
    for (int pl = 0; pl < planes; pl++) {
        int rows = (pl == 0) ? f->height : f->height / hs;
        int cols = (pl == 0) ? f->width : f->width / hs;
        for (int y = 0; y < rows; y++)
            for (int x = 0; x < cols; x++) { h ^= f->data[pl][y * f->linesize[pl] + x]; h *= 1099511628211ull; }
    }
    return h;
}
static const char *imgname(const void *p) {
    Dl_info i = {0};
    return (dladdr(p, &i) && i.dli_fname) ? i.dli_fname : "unresolved";
}

static int feed(const char *in, const char *out) {
    FILE *f = fopen(in, "rb");
    if (!f) { perror("open input"); return 2; }
    fseek(f, 0, SEEK_END);
    long n = ftell(f);
    fseek(f, 0, SEEK_SET);
    uint8_t *buf = malloc((size_t)n + 64);
    if (!buf) return 2;
    if (fread(buf, 1, (size_t)n, f) != (size_t)n) return 2;
    fclose(f);
    memset(buf + n, 0, 64);
    AVCodecParserContext *pc = av_parser_init(AV_CODEC_ID_MPEG2VIDEO);
    const AVCodec *dec = avcodec_find_decoder(AV_CODEC_ID_MPEG2VIDEO);
    AVCodecContext *cc = avcodec_alloc_context3(dec);
    if (!pc || !dec || !cc) return 2;
    if (avcodec_open2(cc, dec, NULL) < 0) return 2;
    AVPacket *pkt = av_packet_alloc();
    AVFrame *fr = av_frame_alloc();
    if (!pkt || !fr) return 2;
    FILE *o = fopen(out, "w");
    if (!o) return 2;
    long off = 0;
    int pi = 0, si = 0, ri = 0;
    const long CHUNK = 1000;
    while (off < n) {
        long want = n - off < CHUNK ? n - off : CHUNK;
        uint8_t *op = NULL;
        int osz = 0;
        int used = av_parser_parse2(pc, cc, &op, &osz, buf + off, (int)want,
                                    AV_NOPTS_VALUE, AV_NOPTS_VALUE, off);
        fprintf(o, "parse i=%d size=%ld used=%d packetSize=%d packetFNV=0x%016" PRIx64 "\n",
                pi++, want, used, osz, (osz > 0 && op) ? fnv(op, (size_t)osz) : 0);
        if (used < 0) { fclose(o); return 2; }
        off += used > 0 ? used : want;
        if (osz > 0 && op) {
            int src;
            if (av_new_packet(pkt, osz) < 0) { fclose(o); return 2; }
            memcpy(pkt->data, op, (size_t)osz);
            src = avcodec_send_packet(cc, pkt);
            av_packet_unref(pkt);
            fprintf(o, "send i=%d size=%d rc=%d\n", si++, osz, src);
            if (src == 0) {
                for (;;) {
                    int rrc = avcodec_receive_frame(cc, fr);
                    fprintf(o, "recv i=%d rc=%d w=%d h=%d fmt=%d fnv=0x%016" PRIx64 "\n",
                            ri++, rrc, rrc == 0 ? fr->width : 0, rrc == 0 ? fr->height : 0,
                            rrc == 0 ? fr->format : -1, rrc == 0 ? frame_fnv(fr) : 0);
                    if (rrc != 0) break;
                }
            }
        }
        if (used == 0 && osz == 0) break; /* no progress guard */
    }
    fprintf(o, "FEED TAIL COMPLETE parses=%d sends=%d recvs=%d\n", pi, si, ri);
    fclose(o);
    av_parser_close(pc);
    avcodec_free_context(&cc);
    av_packet_free(&pkt);
    av_frame_free(&fr);
    free(buf);
    return 0;
}

static int exitcode(int status) {
    AVCodecParserContext *pc = av_parser_init(AV_CODEC_ID_MPEG2VIDEO);
    const AVCodec *dec = avcodec_find_decoder(AV_CODEC_ID_MPEG2VIDEO);
    AVCodecContext *cc = avcodec_alloc_context3(dec);
    uint8_t *op = NULL;
    int osz = 0;
    static const uint8_t probe[64] = {0, 0, 1, 0xB3};
    if (pc && cc) av_parser_parse2(pc, cc, &op, &osz, probe, sizeof(probe),
                                   AV_NOPTS_VALUE, AV_NOPTS_VALUE, 0);
    _Exit(status);
}

static void one_addr(const char *api, void *direct) {
    void *next = dlsym(RTLD_NEXT, api);
    Dl_info di = {0};
    const char *dimg = (dladdr(direct, &di) && di.dli_fname) ? di.dli_fname : "unresolved";
    void *expl = NULL;
    void *h = dlopen(dimg, RTLD_NOW | RTLD_LOCAL | RTLD_FIRST);
    if (h) expl = dlsym(h, api);
    printf("addr api=%s direct=%p directImage=%s next=%p nextIsDirect=%d explicit=%p explicitIsDirect=%d\n",
           api, direct, dimg, next, next == direct, expl, expl == direct);
    if (h) dlclose(h);
}

int main(int argc, char **argv) {
    if (argc < 2) return 2;
    if (!strcmp(argv[1], "feed") && argc == 4) return feed(argv[2], argv[3]);
    if (!strcmp(argv[1], "exitcode") && argc == 3) return exitcode(atoi(argv[2]));
    if (!strcmp(argv[1], "addrs") && argc == 2) {
        printf("addrsImage=%s\n", imgname((const void *)main));
        one_addr("av_parser_parse2", (void *)av_parser_parse2);
        one_addr("avcodec_send_packet", (void *)avcodec_send_packet);
        one_addr("avcodec_receive_frame", (void *)avcodec_receive_frame);
        one_addr("_Exit", (void *)_Exit);
        printf("ADDRS TAIL COMPLETE\n");
        return 0;
    }
    return 2;
}
