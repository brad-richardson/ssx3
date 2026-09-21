/* References the COMPLETE FFmpeg API surface used by MPEG.cpp (FFmpeg-ON path).
 * Link-only: never executed. Proves the iOS subset archives satisfy the app. */
#include <stdio.h>
#include <libavcodec/avcodec.h>
#include <libavutil/error.h>
#include <libavutil/log.h>
#include <libswscale/swscale.h>
int main(void) {
    const AVCodec *codec = avcodec_find_decoder(AV_CODEC_ID_MPEG2VIDEO);
    AVCodecParserContext *parser = av_parser_init(AV_CODEC_ID_MPEG2VIDEO);
    AVCodecContext *ctx = avcodec_alloc_context3(codec);
    AVFrame *frame = av_frame_alloc();
    AVPacket *pkt = av_packet_alloc();
    ctx->thread_count = 1; ctx->pkt_timebase = (AVRational){1, 90000};
    ctx->skip_frame = AVDISCARD_DEFAULT; ctx->err_recognition = 0;
    int r = avcodec_open2(ctx, codec, NULL);
    uint8_t *pd = NULL; int psz = 0;
    uint8_t buf[64] = {0};
    r |= av_parser_parse2(parser, ctx, &pd, &psz, buf, 64, AV_NOPTS_VALUE, AV_NOPTS_VALUE, 0);
    r |= av_parser_parse2(parser, ctx, &pd, &psz, NULL, 0, AV_NOPTS_VALUE, AV_NOPTS_VALUE, 0);
    r |= av_new_packet(pkt, 16);
    r |= avcodec_send_packet(ctx, pkt);
    r |= avcodec_send_packet(ctx, NULL);
    r |= avcodec_receive_frame(ctx, frame);
    av_packet_unref(pkt);
    av_frame_unref(frame);
    struct SwsContext *sws = sws_getContext(16, 16, AV_PIX_FMT_YUV420P, 16, 16,
                                            AV_PIX_FMT_RGBA, SWS_BILINEAR, NULL, NULL, NULL);
    uint8_t *dd[4] = {0, 0, 0, 0}; int dl[4] = {0, 0, 0, 0};
    r |= sws_scale(sws, (const uint8_t *const *)frame->data, frame->linesize, 0, 16, dd, dl);
    sws_freeContext(sws);
    char ebuf[AV_ERROR_MAX_STRING_SIZE];
    r |= (int)av_strerror(r, ebuf, sizeof(ebuf));
    av_log(NULL, AV_LOG_ERROR, "%s", ebuf);
    av_frame_free(&frame);
    av_packet_free(&pkt);
    avcodec_free_context(&ctx);
    av_parser_close(parser);
    printf("%d\n", r);
    return 0;
}
