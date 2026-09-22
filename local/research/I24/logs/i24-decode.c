/* Mirror of MPEG.cpp MpegFfmpegDecoder::feed/receive/convert (subset probe). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <libavcodec/avcodec.h>
#include <libswscale/swscale.h>
int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "rb");
    fseek(f, 0, SEEK_END); long n = ftell(f); fseek(f, 0, SEEK_SET);
    uint8_t *data = malloc(n); fread(data, 1, n, f); fclose(f);
    const AVCodec *codec = avcodec_find_decoder(AV_CODEC_ID_MPEG2VIDEO);
    AVCodecParserContext *parser = av_parser_init(AV_CODEC_ID_MPEG2VIDEO);
    AVCodecContext *ctx = avcodec_alloc_context3(codec);
    ctx->thread_count = 1; ctx->pkt_timebase = (AVRational){1, 90000};
    if (avcodec_open2(ctx, codec, NULL) < 0) { printf("open-fail\n"); return 2; }
    AVFrame *frame = av_frame_alloc(); AVPacket *pkt = av_packet_alloc();
    struct SwsContext *sws = NULL; int sw = 0, sh = 0, sfmt = -1;
    size_t parsed = 0, packets = 0, frames = 0;
    uint8_t *rgba_all = NULL; size_t rgba_len = 0;
    const uint8_t *cur = data; size_t rem = n;
    int flush_pass = 0;
    while (rem > 0 || !flush_pass) {
        uint8_t *pdata = NULL; int psize = 0;
        int used = 0;
        if (rem > 0) {
            used = av_parser_parse2(parser, ctx, &pdata, &psize, cur, (int)rem,
                                    AV_NOPTS_VALUE, AV_NOPTS_VALUE, 0);
            if (used < 0) { printf("parser-fail\n"); return 2; }
            if (used == 0 && psize == 0) { rem = 0; }
            parsed += used; cur += used; rem -= used;
        } else { flush_pass = 1; }
        if (psize > 0) {
            packets++;
            av_packet_unref(pkt); av_new_packet(pkt, psize);
            memcpy(pkt->data, pdata, psize);
            if (avcodec_send_packet(ctx, pkt) < 0) { printf("send-fail\n"); return 2; }
            av_packet_unref(pkt);
        }
        for (;;) {
            int r = avcodec_receive_frame(ctx, frame);
            if (r == AVERROR(EAGAIN) || r == AVERROR_EOF) break;
            if (r < 0) { printf("recv-fail\n"); return 2; }
            if (!sws || sw != frame->width || sh != frame->height || sfmt != frame->format) {
                if (sws) sws_freeContext(sws);
                sws = sws_getContext(frame->width, frame->height, frame->format,
                                     frame->width, frame->height, AV_PIX_FMT_RGBA,
                                     SWS_BILINEAR, NULL, NULL, NULL);
                sw = frame->width; sh = frame->height; sfmt = frame->format;
            }
            size_t row = (size_t)sw * 4, sz = row * (size_t)sh;
            rgba_all = realloc(rgba_all, rgba_len + sz);
            uint8_t *dst[4] = { rgba_all + rgba_len, 0, 0, 0 };
            int ls[4] = { (int)row, 0, 0, 0 };
            int rows = sws_scale(sws, (const uint8_t *const *)frame->data, frame->linesize,
                                 0, sh, dst, ls);
            if (rows <= 0) { printf("sws-fail\n"); return 2; }
            printf("frame%zu %dx%d fmt=%d\n", frames, sw, sh, sfmt);
            rgba_len += sz; frames++;
            av_frame_unref(frame);
        }
        if (flush_pass) break;
    }
    /* parser flush (mirrors MPEG.cpp flush()) then codec drain */
    {
        uint8_t *pdata = NULL; int psize = 0;
        av_parser_parse2(parser, ctx, &pdata, &psize, NULL, 0,
                         AV_NOPTS_VALUE, AV_NOPTS_VALUE, 0);
        if (psize > 0) {
            packets++;
            av_packet_unref(pkt); av_new_packet(pkt, psize);
            memcpy(pkt->data, pdata, psize);
            avcodec_send_packet(ctx, pkt);
            av_packet_unref(pkt);
        }
    }
    avcodec_send_packet(ctx, NULL);
    for (;;) {
        int r = avcodec_receive_frame(ctx, frame);
        if (r == AVERROR(EAGAIN) || r == AVERROR_EOF) break;
        if (r < 0) break;
        if (!sws || sw != frame->width || sh != frame->height || sfmt != frame->format) {
            if (sws) sws_freeContext(sws);
            sws = sws_getContext(frame->width, frame->height, frame->format, frame->width,
                                 frame->height, AV_PIX_FMT_RGBA, SWS_BILINEAR, NULL, NULL, NULL);
            sw = frame->width; sh = frame->height; sfmt = frame->format;
        }
        size_t row = (size_t)sw * 4, sz = row * (size_t)sh;
        rgba_all = realloc(rgba_all, rgba_len + sz);
        uint8_t *dst[4] = { rgba_all + rgba_len, 0, 0, 0 };
        int ls[4] = { (int)row, 0, 0, 0 };
        sws_scale(sws, (const uint8_t *const *)frame->data, frame->linesize, 0, sh, dst, ls);
        printf("frame%zu %dx%d fmt=%d (drain)\n", frames, sw, sh, sfmt);
        rgba_len += sz; frames++;
        av_frame_unref(frame);
    }
    printf("in=%ld parsed=%zu packets=%zu frames=%zu rgba=%zu\n", n, parsed, packets, frames, rgba_len);
    FILE *o = fopen(argv[2], "wb"); fwrite(rgba_all, 1, rgba_len, o); fclose(o);
    return 0;
}
