#include <stdio.h>
#include <libavcodec/avcodec.h>
#include <libswscale/swscale.h>
int main(void) {
    const AVCodec *c = avcodec_find_decoder(AV_CODEC_ID_MPEG2VIDEO);
    AVCodecParserContext *p = av_parser_init(AV_CODEC_ID_MPEG2VIDEO);
    struct SwsContext *s = sws_getContext(16, 16, AV_PIX_FMT_YUV420P, 16, 16,
                                          AV_PIX_FMT_RGBA, SWS_BILINEAR, 0, 0, 0);
    printf("%s %p %p\n", c ? c->name : "none", (void *)p, (void *)s);
    return (c && p && s) ? 0 : 1;
}
