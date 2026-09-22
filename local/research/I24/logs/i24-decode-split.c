/* I24 split-phase probe: mirrors MPEG.cpp MpegFfmpegDecoder::feed then ::flush
 * separately (same call shapes: whole-remaining parse chunks, EAGAIN retry in
 * sendPacket, parser NULL-flush + codec NULL-send in flush, SWS_BILINEAR to
 * RGBA). Prints per-phase counts so the stall-or-serve shape is exact. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <libavcodec/avcodec.h>
#include <libswscale/swscale.h>

static AVCodecContext *ctx;
static AVCodecParserContext *parser;
static AVFrame *frame;
static AVPacket *pkt;
static struct SwsContext *sws = NULL;
static int sw = 0, sh = 0, sfmt = -1;
static uint8_t *rgba_all = NULL;
static size_t rgba_len = 0, frames = 0;

static int convert_frame(const char *phase) {
    int w = frame->width, h = frame->height, fmt = frame->format;
    if (!sws || sw != w || sh != h || sfmt != fmt) {
        if (sws) sws_freeContext(sws);
        sws = sws_getContext(w, h, fmt, w, h, AV_PIX_FMT_RGBA,
                             SWS_BILINEAR, NULL, NULL, NULL);
        if (!sws) return -1;
        sw = w; sh = h; sfmt = fmt;
    }
    size_t row = (size_t)sw * 4, sz = row * (size_t)sh;
    rgba_all = realloc(rgba_all, rgba_len + sz);
    uint8_t *dst[4] = { rgba_all + rgba_len, 0, 0, 0 };
    int ls[4] = { (int)row, 0, 0, 0 };
    int rows = sws_scale(sws, (const uint8_t *const *)frame->data,
                         frame->linesize, 0, sh, dst, ls);
    if (rows <= 0) return -1;
    printf("frame%zu %dx%d fmt=%d (%s)\n", frames, sw, sh, sfmt, phase);
    rgba_len += sz; frames++;
    return 0;
}

static int receive_frames(const char *phase) {
    for (;;) {
        int r = avcodec_receive_frame(ctx, frame);
        if (r == AVERROR(EAGAIN) || r == AVERROR_EOF) return 0;
        if (r < 0) return 0; /* MPEG.cpp: log + drop, keep going */
        if (convert_frame(phase) < 0) { av_frame_unref(frame); return -1; }
        av_frame_unref(frame);
    }
}

static int send_packet(const uint8_t *data, int size) {
    if (!data || size == 0) return 0;
    av_packet_unref(pkt);
    if (av_new_packet(pkt, size) < 0) return -1;
    memcpy(pkt->data, data, size);
    pkt->pts = parser->pts; pkt->dts = parser->dts;
    int ret = avcodec_send_packet(ctx, pkt);
    if (ret == AVERROR(EAGAIN)) {
        if (receive_frames("feed-eagain") < 0) { av_packet_unref(pkt); return -1; }
        ret = avcodec_send_packet(ctx, pkt);
    }
    av_packet_unref(pkt);
    if (ret < 0 && ret != AVERROR(EAGAIN)) return 0; /* MPEG.cpp: drop, keep going */
    return receive_frames("feed");
}

int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "rb");
    fseek(f, 0, SEEK_END); long n = ftell(f); fseek(f, 0, SEEK_SET);
    uint8_t *data = malloc(n); fread(data, 1, n, f); fclose(f);
    const AVCodec *codec = avcodec_find_decoder(AV_CODEC_ID_MPEG2VIDEO);
    parser = av_parser_init(AV_CODEC_ID_MPEG2VIDEO);
    ctx = avcodec_alloc_context3(codec);
    frame = av_frame_alloc(); pkt = av_packet_alloc();
    ctx->thread_count = 1; ctx->pkt_timebase = (AVRational){1, 90000};
    ctx->skip_frame = AVDISCARD_DEFAULT; ctx->err_recognition = 0;
    if (avcodec_open2(ctx, codec, NULL) < 0) { printf("open-fail\n"); return 2; }

    /* FEED phase (mirrors MpegFfmpegDecoder::feed, pts/dts NOPTS) */
    size_t parsed = 0, feed_packets = 0;
    size_t frames_before = frames;
    const uint8_t *cur = data; size_t rem = n;
    int feed_ok = 1;
    while (rem > 0) {
        uint8_t *pdata = NULL; int psize = 0;
        int used = av_parser_parse2(parser, ctx, &pdata, &psize, cur, (int)rem,
                                    AV_NOPTS_VALUE, AV_NOPTS_VALUE, 0);
        if (used < 0) { printf("parser-fail\n"); return 2; }
        if (used == 0 && psize == 0) break;
        parsed += used; cur += used; rem -= used;
        if (psize > 0) {
            feed_packets++;
            if (send_packet(pdata, psize) < 0) { feed_ok = 0; break; }
        }
    }
    printf("[feed] inSize=%ld parsed=%zu packets=%zu newFrames=%zu totalFrames=%zu ok=%d\n",
           n, parsed, feed_packets, frames - frames_before, frames, feed_ok);

    /* FLUSH phase (mirrors MpegFfmpegDecoder::flush) */
    size_t flush_packets = 0;
    frames_before = frames;
    uint8_t *pdata = NULL; int psize = 0;
    av_parser_parse2(parser, ctx, &pdata, &psize, NULL, 0,
                     AV_NOPTS_VALUE, AV_NOPTS_VALUE, 0);
    int flush_ok = 1;
    if (psize > 0) {
        flush_packets++;
        if (send_packet(pdata, psize) < 0) flush_ok = 0;
    }
    int sendRet = avcodec_send_packet(ctx, NULL);
    if (sendRet < 0 && sendRet != AVERROR_EOF) flush_ok = 0;
    if (receive_frames("flush-drain") < 0) flush_ok = 0;
    printf("[flush] packets=%zu newFrames=%zu totalFrames=%zu ok=%d\n",
           flush_packets, frames - frames_before, frames, flush_ok);
    printf("in=%ld parsed=%zu packets=%zu frames=%zu rgba=%zu\n",
           n, parsed, feed_packets + flush_packets, frames, rgba_len);
    FILE *o = fopen(argv[2], "wb");
    if (rgba_len) fwrite(rgba_all, 1, rgba_len, o);
    fclose(o);
    return 0;
}
