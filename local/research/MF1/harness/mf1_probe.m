// MF1 probe: experiment matrix for MTLFXFrameInterpolator engagement.
// Dumps output after EVERY encode in small sequences under varying settings,
// to find which configuration actually interpolates (vs bit-exact passthrough).
//
// Run: ./mf1_probe --out <dir> --exp <name> [--width W --height H]
// Experiments:
//   bgra-prime    BGRA8, prime(reset=YES,color=A) then interp(color=B,prev=A); dump OUT0,OUT1
//   bgra-noreset  BGRA8, e0(color=A,prev=A,reset=NO) e1(color=B,prev=A,reset=NO); dump OUT0,OUT1
//   bgra-seq      BGRA8, frames A,B,C continuing motion; e0 reset, e1, e2; dump OUT0,1,2
//   rgba16-prime  RGBA16F color/output, prime+interp; dump OUT0,OUT1 (+ OUT1.as16f raw halves)
//   rgba16-seq    RGBA16F, A,B,C sequence; dump OUT0,1,2
//   bgra-ndcmot   BGRA8, prime+interp, motion in NDC halves + scale=W/2,H/2
//   bgra-norev    BGRA8, prime+interp, depthReversed=NO + inverted depth values
#import <Metal/Metal.h>
#import <MetalFX/MetalFX.h>
#import <Foundation/Foundation.h>
#import "mf1_scene.h"

typedef struct {
    id<MTLDevice> dev;
    id<MTLCommandQueue> q;
    id<MTLFXFrameInterpolator> fx;
    id<MTLTexture> texOut, texStage;
    MTLRegion region;
    int W, H, bytesPerRow;
    MTLPixelFormat colorFmt;
} Ctx;

static id<MTLTexture> mkTex(Ctx *c, MTLPixelFormat fmt, MTLTextureUsage usage, int priv) {
    MTLTextureDescriptor *td = [MTLTextureDescriptor texture2DDescriptorWithPixelFormat:fmt
                                                                                 width:c->W height:c->H mipmapped:NO];
    td.storageMode = priv ? MTLStorageModePrivate : MTLStorageModeShared;
    td.usage = usage;
    return [c->dev newTextureWithDescriptor:td];
}

static double runEncode(Ctx *c, id<MTLTexture> color, id<MTLTexture> prev, BOOL reset, double *gpuMs) {
    c->fx.colorTexture = color;
    c->fx.prevColorTexture = prev;
    c->fx.shouldResetHistory = reset;
    c->fx.outputTexture = c->texOut;
    id<MTLCommandBuffer> cb = [c->q commandBuffer];
    [c->fx encodeToCommandBuffer:cb];
    [cb commit]; [cb waitUntilCompleted];
    if (cb.status == MTLCommandBufferStatusError) {
        fprintf(stderr, "encode error: %s\n", cb.error.localizedDescription.UTF8String); exit(1);
    }
    *gpuMs = (cb.GPUEndTime - cb.GPUStartTime) * 1000.0;
    return *gpuMs;
}

static void dumpOut(Ctx *c, const char *dir, const char *name) {
    id<MTLCommandBuffer> rb = [c->q commandBuffer];
    id<MTLBlitCommandEncoder> blit = [rb blitCommandEncoder];
    [blit copyFromTexture:c->texOut toTexture:c->texStage];
    [blit endEncoding];
    [rb commit]; [rb waitUntilCompleted];
    size_t px = (size_t)c->W * c->H;
    void *buf = malloc(px * 8);
    [c->texStage getBytes:buf bytesPerRow:c->bytesPerRow fromRegion:c->region mipmapLevel:0];
    writeRaw(dir, name, buf, px * (c->colorFmt == MTLPixelFormatRGBA16Float ? 8 : 4));
    free(buf);
}

int main(int argc, const char *argv[]) {
    int W = 640, H = 360;
    const char *outdir = NULL, *exp = NULL;
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--width") && i + 1 < argc) W = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--height") && i + 1 < argc) H = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--out") && i + 1 < argc) outdir = argv[++i];
        else if (!strcmp(argv[i], "--exp") && i + 1 < argc) exp = argv[++i];
    }
    if (!outdir || !exp) { fprintf(stderr, "usage: mf1_probe --out DIR --exp NAME\n"); return 2; }

    int use16 = (strstr(exp, "rgba16") != NULL);
    int seq3 = (strstr(exp, "-seq") != NULL);
    int noreset = (strstr(exp, "noreset") != NULL);
    int ndcmot = (strstr(exp, "ndcmot") != NULL);
    int norev = (strstr(exp, "norev") != NULL);
    int steady = (strstr(exp, "steady") != NULL);
    int recover = (strstr(exp, "recover") != NULL);
    int recover8 = (strstr(exp, "recover8") != NULL);

    @autoreleasepool {
        id<MTLDevice> dev = MTLCreateSystemDefaultDevice();
        if (![MTLFXFrameInterpolatorDescriptor supportsDevice:dev]) { printf("{\"ok\":false}\n"); return 0; }
        char mk[1024]; snprintf(mk, sizeof(mk), "mkdir -p %s", outdir);
        if (system(mk) != 0) return 1;

        const int S = 32;
        size_t px = (size_t)W * H;
        uint8_t *b8[4]; float *dep[4];
        for (int i = 0; i < 4; i++) { b8[i] = malloc(px * 4); dep[i] = malloc(px * 4); }
        float cxA = W / 2.0f - S - (W / 4) / 2.0f; // A left edge (room for C at +64)
        FrameCtx cs[4] = {{W, H, W, cxA}, {W, H, W, cxA + S}, {W, H, W, cxA + 2 * S}, {W, H, W, cxA + S / 2.0f}};
        const char *names[4] = {"A", "B", "C", "GT"};
        for (int i = 0; i < 4; i++) {
            paintFrame(b8[i], dep[i], &cs[i], 0);
            if (norev) for (size_t p = 0; p < px; p++) dep[i][p] = 1.0f - dep[i][p];
            char n[16]; snprintf(n, sizeof(n), "%s.rgba", names[i]);
            writeRaw(outdir, n, b8[i], px * 4);
        }
        // GT2 = middle of B,C
        uint8_t *bGT2 = malloc(px * 4); float *dGT2 = malloc(px * 4);
        FrameCtx cGT2 = {W, H, W, cxA + S + S / 2.0f};
        paintFrame(bGT2, dGT2, &cGT2, 0);
        writeRaw(outdir, "GT2.rgba", bGT2, px * 4);
        // D = continuing motion (+3S), GT3 = middle of C,D
        uint8_t *bD = malloc(px * 4); float *dD = malloc(px * 4);
        FrameCtx cD = {W, H, W, cxA + 3 * S};
        paintFrame(bD, dD, &cD, 0);
        if (norev) for (size_t p = 0; p < px; p++) dD[p] = 1.0f - dD[p];
        writeRaw(outdir, "D.rgba", bD, px * 4);
        uint8_t *bGT3 = malloc(px * 4); float *dGT3 = malloc(px * 4);
        FrameCtx cGT3 = {W, H, W, cxA + 2 * S + S / 2.0f};
        paintFrame(bGT3, dGT3, &cGT3, 0);
        writeRaw(outdir, "GT3.rgba", bGT3, px * 4);
        // Reference dump for BGRA8 D (16F exps compare numerically in python)
        uint16_t *motD = malloc(px * 4);
        paintMotionEx(motD, W, H, cxA + 3 * S, S, 0, ndcmot ? W / 2.0f : 1.0f);

        uint16_t *motB = malloc(px * 4), *motC = malloc(px * 4);
        paintMotionEx(motB, W, H, cxA + S, S, 0, ndcmot ? W / 2.0f : 1.0f);
        paintMotionEx(motC, W, H, cxA + 2 * S, S, 0, ndcmot ? W / 2.0f : 1.0f);

        Ctx c = {0};
        c.dev = dev; c.W = W; c.H = H;
        c.q = [dev newCommandQueue];
        c.region = MTLRegionMake2D(0, 0, W, H);
        c.colorFmt = use16 ? MTLPixelFormatRGBA16Float : MTLPixelFormatBGRA8Unorm;
        c.bytesPerRow = W * (use16 ? 8 : 4);

        MTLFXFrameInterpolatorDescriptor *desc = [[MTLFXFrameInterpolatorDescriptor alloc] init];
        desc.colorTextureFormat = c.colorFmt;
        desc.outputTextureFormat = c.colorFmt;
        desc.depthTextureFormat = MTLPixelFormatDepth32Float;
        desc.motionTextureFormat = MTLPixelFormatRG16Float;
        desc.uiTextureFormat = MTLPixelFormatBGRA8Unorm;
        desc.inputWidth = W; desc.inputHeight = H;
        desc.outputWidth = W; desc.outputHeight = H;
        c.fx = [desc newFrameInterpolatorWithDevice:dev];
        if (!c.fx) { printf("{\"ok\":false,\"reason\":\"alloc-nil\"}\n"); return 0; }

        id<MTLTexture> tcol[4], tdep[4], tmot[4];
        uint16_t *mots[4] = {motB, motB, motC, motD};
        for (int i = 0; i < 4; i++) {
            tcol[i] = mkTex(&c, c.colorFmt, c.fx.colorTextureUsage | MTLTextureUsageShaderRead, 0);
            tdep[i] = mkTex(&c, MTLPixelFormatDepth32Float, c.fx.depthTextureUsage, 0);
            tmot[i] = mkTex(&c, MTLPixelFormatRG16Float, c.fx.motionTextureUsage | MTLTextureUsageShaderRead, 0);
            uint8_t *src8 = (i < 3) ? b8[i] : bD;
            float *srcd = (i < 3) ? dep[i] : dD;
            if (use16) {
                uint16_t *h16 = malloc(px * 8);
                bgra8_to_rgba16f(h16, src8, px);
                [tcol[i] replaceRegion:c.region mipmapLevel:0 withBytes:h16 bytesPerRow:W * 8];
                free(h16);
            } else {
                [tcol[i] replaceRegion:c.region mipmapLevel:0 withBytes:src8 bytesPerRow:W * 4];
            }
            [tdep[i] replaceRegion:c.region mipmapLevel:0 withBytes:srcd bytesPerRow:W * 4];
            [tmot[i] replaceRegion:c.region mipmapLevel:0 withBytes:mots[i] bytesPerRow:W * 4];
        }
        c.texOut = mkTex(&c, c.colorFmt, c.fx.outputTextureUsage, 1);
        c.texStage = mkTex(&c, c.colorFmt, MTLTextureUsageShaderRead, 0);

        c.fx.depthTexture = tdep[1]; c.fx.motionTexture = tmot[1];
        c.fx.uiTexture = nil;
        if (ndcmot) { c.fx.motionVectorScaleX = W * 0.5f; c.fx.motionVectorScaleY = H * 0.5f; }
        else { c.fx.motionVectorScaleX = 1.0f; c.fx.motionVectorScaleY = 1.0f; }
        c.fx.deltaTime = 1.0f / 60.0f;
        c.fx.nearPlane = 0.1f; c.fx.farPlane = 100.0f;
        c.fx.fieldOfView = 60.0f; c.fx.aspectRatio = (float)W / (float)H;
        c.fx.jitterOffsetX = 0; c.fx.jitterOffsetY = 0;
        c.fx.depthReversed = norev ? NO : YES;
        c.fx.uiTextureComposited = NO;
        c.fx.contentWidth = W; c.fx.contentHeight = H;

        // Warmup pair so timed/observed encodes are post-compile.
        c.fx.depthTexture = tdep[0]; c.fx.motionTexture = tmot[1];
        double g;
        runEncode(&c, tcol[0], noreset ? tcol[0] : nil, noreset ? NO : YES, &g);
        c.fx.depthTexture = tdep[1]; c.fx.motionTexture = tmot[1];
        runEncode(&c, tcol[1], tcol[0], NO, &g);

        // Observed sequence. Each step: (color, prev, reset, depthMotion).
        // Default 2-step: (A,A|nil,R?) (B,A,NO). seq3 adds (C,B,NO).
        // steady 4-step: (A,A,NO) (B,A,NO) (C,B,NO) (D,C,NO).
        // recover 5-step: (A,A,NO) (B,A,NO) (B,B,YES) (C,B,NO) (D,C,NO).
        struct { int col, prv, rst; } steps[8]; int nsteps = 0;
        if (recover8) {
            struct { int col, prv, rst; } s[] = {{0,0,0},{1,0,0},{2,1,1},{3,2,0},{3,2,0},{3,2,0},{3,2,0},{3,2,0}};
            memcpy(steps, s, sizeof(s)); nsteps = 8;
        } else if (steady) {
            struct { int col, prv, rst; } s[] = {{0,0,0},{1,0,0},{2,1,0},{3,2,0}};
            memcpy(steps, s, sizeof(s)); nsteps = 4;
        } else if (recover) {
            struct { int col, prv, rst; } s[] = {{0,0,0},{1,0,0},{1,1,1},{2,1,0},{3,2,0}};
            memcpy(steps, s, sizeof(s)); nsteps = 5;
        } else {
            steps[0].col = 0; steps[0].prv = noreset ? 0 : -1; steps[0].rst = noreset ? 0 : 1;
            steps[1].col = 1; steps[1].prv = 0; steps[1].rst = 0;
            nsteps = 2;
            if (seq3) { steps[2].col = 2; steps[2].prv = 1; steps[2].rst = 0; nsteps = 3; }
        }
        char js[2048]; int o = 0;
        o += snprintf(js + o, sizeof(js) - o, "{\"ok\":true,\"exp\":\"%s\",\"w\":%d,\"h\":%d,\"gpu_ms\":[", exp, W, H);
        for (int i = 0; i < nsteps; i++) {
            c.fx.depthTexture = tdep[steps[i].col]; c.fx.motionTexture = tmot[steps[i].col];
            id<MTLTexture> prv = (steps[i].prv < 0) ? nil : tcol[steps[i].prv];
            runEncode(&c, tcol[steps[i].col], prv, steps[i].rst ? YES : NO, &g);
            o += snprintf(js + o, sizeof(js) - o, "%s%.4f", i ? "," : "", g);
            char nm[32]; snprintf(nm, sizeof(nm), use16 ? "OUT%d.as16f" : "OUT%d.rgba", i);
            dumpOut(&c, outdir, nm);
        }
        o += snprintf(js + o, sizeof(js) - o, "]}");
        printf("%s\n", js);
    }
    return 0;
}
