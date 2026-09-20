// MF1 isolated MetalFX frame-interpolation harness (macOS CLI).
//
// Standalone spike tool: renders synthetic frame pairs (A@t=0, B@t=1) with
// known motion + depth, runs MTLFXFrameInterpolator, dumps the interpolated
// output and a ground-truth middle frame (t=0.5) for offline comparison.
// Never touches vendor sources, the production player, or phone settings.
//
// Drive pattern (established by mf1_probe): NEVER set shouldResetHistory.
// A fresh instance needs two history-establishing encodes (outputs are
// passthrough/unreliable); interpolation engages on the 3rd encode and
// stays engaged: output N = interp(prev, color). A reset encode outputs
// color bit-exact, clears history, and the next two encodes also pass
// through; interpolation resumes on the 3rd post-reset encode. Quality OUT
// below is the 3rd encode (B,A) = mid(A,B); timing encodes are 5th+.
//
// Build: clang -fobjc-arc -framework Metal -framework MetalFX -framework Foundation \
//          -o mf1_interp mf1_interp.m
// Run: ./mf1_interp --out DIR --width 1280 --height 720 [--iters N]
//        [--motion exact|zero|uniform] [--ui none|composited|separate]
//        [--colorfmt bgra8|rgba16f]
#import <Metal/Metal.h>
#import <MetalFX/MetalFX.h>
#import <Foundation/Foundation.h>
#import "mf1_scene.h"

int main(int argc, const char *argv[]) {
    int W = 1280, H = 720, iters = 30;
    const char *outdir = NULL;
    int motionMode = 0; // exact
    int uiMode = 0;     // 0 none, 1 composited-in-color, 2 separate uiTexture
    int colorFmt = 0;   // 0 BGRA8Unorm, 1 RGBA16Float
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--width") && i + 1 < argc) W = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--height") && i + 1 < argc) H = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--out") && i + 1 < argc) outdir = argv[++i];
        else if (!strcmp(argv[i], "--iters") && i + 1 < argc) iters = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--motion") && i + 1 < argc) {
            const char *m = argv[++i];
            motionMode = !strcmp(m, "zero") ? 1 : !strcmp(m, "uniform") ? 2 : 0;
        } else if (!strcmp(argv[i], "--ui") && i + 1 < argc) {
            const char *m = argv[++i];
            uiMode = !strcmp(m, "composited") ? 1 : !strcmp(m, "separate") ? 2 : 0;
        } else if (!strcmp(argv[i], "--colorfmt") && i + 1 < argc) {
            const char *m = argv[++i];
            colorFmt = !strcmp(m, "rgba16f") ? 1 : 0;
        }
    }
    if (!outdir) { fprintf(stderr, "usage: mf1_interp --out DIR [opts]\n"); return 2; }

    @autoreleasepool {
        id<MTLDevice> dev = MTLCreateSystemDefaultDevice();
        if (!dev) { fprintf(stderr, "no Metal device\n"); return 1; }
        BOOL supported = [MTLFXFrameInterpolatorDescriptor supportsDevice:dev];
        char mk[1024]; snprintf(mk, sizeof(mk), "mkdir -p %s", outdir);
        if (system(mk) != 0) { fprintf(stderr, "mkdir failed\n"); return 1; }

        // Paint host-side frames. S=32px total A->B travel.
        const int S = 32;
        size_t px = (size_t)W * H;
        MTLPixelFormat cf = colorFmt ? MTLPixelFormatRGBA16Float : MTLPixelFormatBGRA8Unorm;
        size_t cbpp = colorFmt ? 8 : 4; // color bytes per pixel
        uint8_t *rgbaA = malloc(px * 4), *rgbaB = malloc(px * 4), *rgbaGT = malloc(px * 4);
        uint8_t *rgbaUI = malloc(px * 4);
        float *depthA = malloc(px * 4), *depthB = malloc(px * 4), *depthGT = malloc(px * 4);
        uint16_t *motion = malloc(px * 4);
        float cxA = W / 2.0f - S / 2.0f - (W / 4) / 2.0f;
        float cxB = cxA + S;
        FrameCtx cA = {W, H, W, cxA}, cB = {W, H, W, cxB}, cG = {W, H, W, cxA + S / 2.0f};
        int hudInColor = (uiMode == 1) ? 1 : 0;
        paintFrame(rgbaA, depthA, &cA, hudInColor);
        paintFrame(rgbaB, depthB, &cB, hudInColor);
        paintFrame(rgbaGT, depthGT, &cG, hudInColor);
        free(depthGT);
        if (uiMode == 2) paintUI(rgbaUI, W, H); else memset(rgbaUI, 0, px * 4);
        paintMotion(motion, W, H, cxB, S, motionMode);
        writeRaw(outdir, "A.rgba", rgbaA, px * 4);
        writeRaw(outdir, "B.rgba", rgbaB, px * 4);
        writeRaw(outdir, "GT.rgba", rgbaGT, px * 4);
        writeRaw(outdir, "UI.rgba", rgbaUI, px * 4);
        uint16_t *hA = NULL, *hB = NULL, *hUI = NULL;
        if (colorFmt) {
            hA = malloc(px * 8); hB = malloc(px * 8); hUI = malloc(px * 8);
            bgra8_to_rgba16f(hA, rgbaA, px);
            bgra8_to_rgba16f(hB, rgbaB, px);
            bgra8_to_rgba16f(hUI, rgbaUI, px);
        }

        uint64_t rssBefore = residentBytes();
        id<MTLCommandQueue> q = [dev newCommandQueue];
        MTLRegion region = MTLRegionMake2D(0, 0, W, H);

        // One interpolator instance + its textures, configured per args.
        // Instance Q (quality): fresh (A,A),(B,A) -> OUT. Instance T (timing):
        // warmed, then N timed (B,A) encodes (steady-state repeated-pair cost).
        unsigned long uColor = 0, uOut = 0, uDepth = 0, uMotion = 0, uUI = 0;
        uint64_t rssAfterAlloc = 0, rssAfterRun = 0;
        for (int inst = 0; inst < 2; inst++) {
            MTLFXFrameInterpolatorDescriptor *desc = [[MTLFXFrameInterpolatorDescriptor alloc] init];
            desc.colorTextureFormat = cf;
            desc.outputTextureFormat = cf;
            desc.depthTextureFormat = MTLPixelFormatDepth32Float;
            desc.motionTextureFormat = MTLPixelFormatRG16Float;
            desc.uiTextureFormat = MTLPixelFormatBGRA8Unorm;
            desc.inputWidth = W; desc.inputHeight = H;
            desc.outputWidth = W; desc.outputHeight = H;
            id<MTLFXFrameInterpolator> fx = supported ? [desc newFrameInterpolatorWithDevice:dev] : nil;
            if (!fx) {
                printf("{\"ok\":false,\"supported\":%s,\"width\":%d,\"height\":%d}\n",
                       supported ? "true" : "false", W, H);
                return 0; // tabled failure, not a crash
            }
            if (inst == 0) {
                rssAfterAlloc = residentBytes();
                uColor = fx.colorTextureUsage; uOut = fx.outputTextureUsage;
                uDepth = fx.depthTextureUsage; uMotion = fx.motionTextureUsage; uUI = fx.uiTextureUsage;
            }
            MTLTextureDescriptor *td = [MTLTextureDescriptor texture2DDescriptorWithPixelFormat:cf
                                                                                         width:W height:H mipmapped:NO];
            td.storageMode = MTLStorageModeShared;
            td.usage = fx.colorTextureUsage | MTLTextureUsageShaderRead;
            id<MTLTexture> texA = [dev newTextureWithDescriptor:td];
            id<MTLTexture> texB = [dev newTextureWithDescriptor:td];
            MTLTextureDescriptor *dd = [MTLTextureDescriptor texture2DDescriptorWithPixelFormat:MTLPixelFormatDepth32Float
                                                                                         width:W height:H mipmapped:NO];
            dd.storageMode = MTLStorageModeShared; dd.usage = fx.depthTextureUsage;
            id<MTLTexture> texDepth = [dev newTextureWithDescriptor:dd];
            MTLTextureDescriptor *md = [MTLTextureDescriptor texture2DDescriptorWithPixelFormat:MTLPixelFormatRG16Float
                                                                                         width:W height:H mipmapped:NO];
            md.storageMode = MTLStorageModeShared;
            md.usage = fx.motionTextureUsage | MTLTextureUsageShaderRead;
            id<MTLTexture> texMotion = [dev newTextureWithDescriptor:md];
            MTLTextureDescriptor *ud = [MTLTextureDescriptor texture2DDescriptorWithPixelFormat:MTLPixelFormatBGRA8Unorm
                                                                                         width:W height:H mipmapped:NO];
            ud.storageMode = MTLStorageModeShared;
            ud.usage = fx.uiTextureUsage | MTLTextureUsageShaderRead;
            id<MTLTexture> texUI = [dev newTextureWithDescriptor:ud];
            MTLTextureDescriptor *od = [MTLTextureDescriptor texture2DDescriptorWithPixelFormat:cf
                                                                                         width:W height:H mipmapped:NO];
            od.storageMode = MTLStorageModePrivate; od.usage = fx.outputTextureUsage;
            id<MTLTexture> texOut = [dev newTextureWithDescriptor:od];
            MTLTextureDescriptor *sd = [MTLTextureDescriptor texture2DDescriptorWithPixelFormat:cf
                                                                                         width:W height:H mipmapped:NO];
            sd.storageMode = MTLStorageModeShared; sd.usage = MTLTextureUsageShaderRead;
            id<MTLTexture> texStage = [dev newTextureWithDescriptor:sd];
            if (!texA || !texB || !texDepth || !texMotion || !texUI || !texOut || !texStage) {
                fprintf(stderr, "texture alloc failed (inst %d)\n", inst); return 1;
            }
            if (colorFmt) {
                [texA replaceRegion:region mipmapLevel:0 withBytes:hA bytesPerRow:W * 8];
                [texB replaceRegion:region mipmapLevel:0 withBytes:hB bytesPerRow:W * 8];
            } else {
                [texA replaceRegion:region mipmapLevel:0 withBytes:rgbaA bytesPerRow:W * 4];
                [texB replaceRegion:region mipmapLevel:0 withBytes:rgbaB bytesPerRow:W * 4];
            }
            // UI texture is always BGRA8 (descriptor uiTextureFormat), either way.
            [texUI replaceRegion:region mipmapLevel:0 withBytes:rgbaUI bytesPerRow:W * 4];
            [texDepth replaceRegion:region mipmapLevel:0 withBytes:depthB bytesPerRow:W * 4];
            [texMotion replaceRegion:region mipmapLevel:0 withBytes:motion bytesPerRow:W * 4];

            fx.motionVectorScaleX = 1.0f;
            fx.motionVectorScaleY = 1.0f;
            fx.deltaTime = 1.0f / 60.0f;
            fx.nearPlane = 0.1f; fx.farPlane = 100.0f;
            fx.fieldOfView = 60.0f; fx.aspectRatio = (float)W / (float)H;
            fx.jitterOffsetX = 0.0f; fx.jitterOffsetY = 0.0f;
            fx.depthReversed = YES;
            fx.uiTextureComposited = NO;
            fx.contentWidth = W; fx.contentHeight = H;
            fx.depthTexture = texDepth; fx.motionTexture = texMotion;
            fx.uiTexture = (uiMode == 2) ? texUI : nil;
            fx.outputTexture = texOut;
            fx.shouldResetHistory = NO; // never reset (see header note)

            if (inst == 0) {
                // Quality: (A,A),(A,A) establish history; 3rd encode (B,A) -> OUT.
                for (int k = 0; k < 2; k++) {
                    fx.colorTexture = texA; fx.prevColorTexture = texA;
                    id<MTLCommandBuffer> e0 = [q commandBuffer];
                    [fx encodeToCommandBuffer:e0];
                    [e0 commit]; [e0 waitUntilCompleted];
                    if (e0.status == MTLCommandBufferStatusError) { fprintf(stderr, "e0.%d: %s\n", k, e0.error.localizedDescription.UTF8String); return 1; }
                }
                fx.colorTexture = texB; fx.prevColorTexture = texA;
                id<MTLCommandBuffer> e1 = [q commandBuffer];
                [fx encodeToCommandBuffer:e1];
                [e1 commit]; [e1 waitUntilCompleted];
                if (e1.status == MTLCommandBufferStatusError) { fprintf(stderr, "e1: %s\n", e1.error.localizedDescription.UTF8String); return 1; }
                id<MTLCommandBuffer> rb = [q commandBuffer];
                id<MTLBlitCommandEncoder> blit = [rb blitCommandEncoder];
                [blit copyFromTexture:texOut toTexture:texStage];
                [blit endEncoding];
                [rb commit]; [rb waitUntilCompleted];
                void *outBytes = malloc(px * cbpp);
                [texStage getBytes:outBytes bytesPerRow:W * cbpp fromRegion:region mipmapLevel:0];
                writeRaw(outdir, colorFmt ? "OUT.as16f" : "OUT.rgba", outBytes, px * cbpp);
                free(outBytes);
            } else {
                // Timing: warmup then N timed steady-state (B,A) encodes.
                for (int i = 0; i < 2; i++) {
                    fx.colorTexture = texA; fx.prevColorTexture = texA;
                    id<MTLCommandBuffer> w0 = [q commandBuffer];
                    [fx encodeToCommandBuffer:w0];
                    [w0 commit]; [w0 waitUntilCompleted];
                    fx.colorTexture = texB; fx.prevColorTexture = texA;
                    id<MTLCommandBuffer> w1 = [q commandBuffer];
                    [fx encodeToCommandBuffer:w1];
                    [w1 commit]; [w1 waitUntilCompleted];
                }
                double *gpuMs = malloc(sizeof(double) * iters);
                double *wallMs = malloc(sizeof(double) * iters);
                double *submitMs = malloc(sizeof(double) * iters);
                for (int i = 0; i < iters; i++) {
                    fx.colorTexture = texB; fx.prevColorTexture = texA;
                    fx.outputTexture = texOut;
                    double t0 = nowSec();
                    id<MTLCommandBuffer> cb = [q commandBuffer];
                    [fx encodeToCommandBuffer:cb];
                    double t1 = nowSec();
                    [cb commit];
                    double t2 = nowSec();
                    [cb waitUntilCompleted];
                    double t3 = nowSec();
                    if (cb.status == MTLCommandBufferStatusError) { fprintf(stderr, "iter %d: %s\n", i, cb.error.localizedDescription.UTF8String); return 1; }
                    gpuMs[i] = (cb.GPUEndTime - cb.GPUStartTime) * 1000.0;
                    wallMs[i] = (t3 - t0) * 1000.0;
                    submitMs[i] = (t2 - t0) * 1000.0;
                    (void)t1;
                }
                rssAfterRun = residentBytes();
                qsort(gpuMs, iters, sizeof(double), cmpd);
                qsort(wallMs, iters, sizeof(double), cmpd);
                qsort(submitMs, iters, sizeof(double), cmpd);
                double med = gpuMs[iters / 2];
                double p95 = gpuMs[(int)(iters * 0.95) < iters ? (int)(iters * 0.95) : iters - 1];
                printf("{\"ok\":true,\"device\":\"%s\",\"width\":%d,\"height\":%d,\"iters\":%d,"
                       "\"gpu_ms_med\":%.4f,\"gpu_ms_p95\":%.4f,\"gpu_ms_min\":%.4f,\"gpu_ms_max\":%.4f,"
                       "\"wall_ms_med\":%.4f,\"submit_ms_med\":%.4f,"
                       "\"rss_before\":%llu,\"rss_after_alloc\":%llu,\"rss_after_run\":%llu,"
                       "\"usage\":{\"color\":%lu,\"output\":%lu,\"depth\":%lu,\"motion\":%lu,\"ui\":%lu}}\n",
                       dev.name.UTF8String, W, H, iters, med, p95, gpuMs[0], gpuMs[iters - 1],
                       wallMs[iters / 2], submitMs[iters / 2],
                       rssBefore, rssAfterAlloc, rssAfterRun,
                       uColor, uOut, uDepth, uMotion, uUI);
                free(gpuMs); free(wallMs); free(submitMs);
            }
        }
    }
    return 0;
}
