// MF1 iOS probe: headless MetalFX frame-interpolation measurement on device.
//
// Minimal UIKit app (no storyboard, classic lifecycle). On launch it runs the
// synthetic A/B/GT scene through MTLFXFrameInterpolator at two resolutions,
// writes mf1-result.json + raw frames to Documents/MF1/, writes DONE, exits.
// Host pulls via: devicectl device copy from --domain-type appDataContainer
//   --domain-identifier <bundle> --source Documents/MF1 --destination <dir>
//
// Bundle id must match the wildcard dev profile (LQ3V7772Q2.*).
#import <UIKit/UIKit.h>
#import <Metal/Metal.h>
#import <MetalFX/MetalFX.h>
#import <Foundation/Foundation.h>
#import "mf1_scene.h"

static NSString *docFile(NSString *name) {
    NSArray *dirs = NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES);
    NSString *mf1 = [[dirs firstObject] stringByAppendingPathComponent:@"MF1"];
    [[NSFileManager defaultManager] createDirectoryAtPath:mf1 withIntermediateDirectories:YES attributes:nil error:nil];
    return [mf1 stringByAppendingPathComponent:name];
}

static void writeData(NSString *name, const void *bytes, size_t len) {
    [[NSData dataWithBytes:bytes length:len] writeToFile:docFile(name) atomically:YES];
}

static MTLPixelFormat cf8(void) { return MTLPixelFormatBGRA8Unorm; }

// Run one config on a fresh interpolator. Returns result dict; writes raw frames.
static NSMutableDictionary *runConfig(id<MTLDevice> dev, id<MTLCommandQueue> q,
                                      int W, int H, int motionMode, int iters, NSString *tag) {
    const int S = 32;
    size_t px = (size_t)W * H;
    uint8_t *rgbaA = malloc(px * 4), *rgbaB = malloc(px * 4), *rgbaGT = malloc(px * 4);
    float *depthB = malloc(px * 4), *depthTmp = malloc(px * 4);
    uint16_t *motion = malloc(px * 4);
    float cxA = W / 2.0f - S / 2.0f - (W / 4) / 2.0f;
    float cxB = cxA + S;
    FrameCtx cA = {W, H, W, cxA}, cB = {W, H, W, cxB}, cG = {W, H, W, cxA + S / 2.0f};
    paintFrame(rgbaA, depthTmp, &cA, 0);
    paintFrame(rgbaB, depthB, &cB, 0);
    paintFrame(rgbaGT, depthTmp, &cG, 0);
    paintMotion(motion, W, H, cxB, S, motionMode);
    writeData([NSString stringWithFormat:@"%@-A.rgba", tag], rgbaA, px * 4);
    writeData([NSString stringWithFormat:@"%@-B.rgba", tag], rgbaB, px * 4);
    writeData([NSString stringWithFormat:@"%@-GT.rgba", tag], rgbaGT, px * 4);

    NSMutableDictionary *r = [NSMutableDictionary dictionary];
    r[@"tag"] = tag; r[@"width"] = @(W); r[@"height"] = @(H);
    r[@"motion"] = (@[@"exact", @"zero", @"uniform"])[motionMode];
    MTLFXFrameInterpolatorDescriptor *desc = [[MTLFXFrameInterpolatorDescriptor alloc] init];
    desc.colorTextureFormat = MTLPixelFormatBGRA8Unorm;
    desc.outputTextureFormat = MTLPixelFormatBGRA8Unorm;
    desc.depthTextureFormat = MTLPixelFormatDepth32Float;
    desc.motionTextureFormat = MTLPixelFormatRG16Float;
    desc.uiTextureFormat = MTLPixelFormatBGRA8Unorm;
    desc.inputWidth = W; desc.inputHeight = H;
    desc.outputWidth = W; desc.outputHeight = H;
    id<MTLFXFrameInterpolator> fx = [desc newFrameInterpolatorWithDevice:dev];
    if (!fx) { r[@"ok"] = @NO; return r; }
    MTLRegion region = MTLRegionMake2D(0, 0, W, H);
    id<MTLTexture> (^mk)(MTLPixelFormat, MTLTextureUsage, BOOL) = ^(MTLPixelFormat f, MTLTextureUsage u, BOOL priv) {
        MTLTextureDescriptor *td = [MTLTextureDescriptor texture2DDescriptorWithPixelFormat:f width:W height:H mipmapped:NO];
        // iOS: no Shared storage for most textures; use Shared where allowed else Private+blit fill.
        td.storageMode = MTLStorageModeShared;
        td.usage = u;
        id<MTLTexture> t = [dev newTextureWithDescriptor:td];
        if (!t && !priv) { // fall back to private; caller must blit-fill (not implemented: fail)
            return (id<MTLTexture>)nil;
        }
        return t;
    };
    id<MTLTexture> texA = mk(cf8(), fx.colorTextureUsage | MTLTextureUsageShaderRead, NO);
    id<MTLTexture> texB = mk(cf8(), fx.colorTextureUsage | MTLTextureUsageShaderRead, NO);
    id<MTLTexture> texDepth = mk(MTLPixelFormatDepth32Float, fx.depthTextureUsage, NO);
    id<MTLTexture> texMotion = mk(MTLPixelFormatRG16Float, fx.motionTextureUsage | MTLTextureUsageShaderRead, NO);
    MTLTextureDescriptor *od = [MTLTextureDescriptor texture2DDescriptorWithPixelFormat:cf8() width:W height:H mipmapped:NO];
    od.storageMode = MTLStorageModePrivate; od.usage = fx.outputTextureUsage;
    id<MTLTexture> texOut = [dev newTextureWithDescriptor:od];
    id<MTLTexture> texStage = mk(cf8(), MTLTextureUsageShaderRead, NO);
    if (!texA || !texB || !texDepth || !texMotion || !texOut || !texStage) {
        r[@"ok"] = @NO; r[@"reason"] = @"texture-alloc";
        return r;
    }
    [texA replaceRegion:region mipmapLevel:0 withBytes:rgbaA bytesPerRow:W * 4];
    [texB replaceRegion:region mipmapLevel:0 withBytes:rgbaB bytesPerRow:W * 4];
    [texDepth replaceRegion:region mipmapLevel:0 withBytes:depthB bytesPerRow:W * 4];
    [texMotion replaceRegion:region mipmapLevel:0 withBytes:motion bytesPerRow:W * 4];
    fx.motionVectorScaleX = 1.0f; fx.motionVectorScaleY = 1.0f;
    fx.deltaTime = 1.0f / 60.0f;
    fx.nearPlane = 0.1f; fx.farPlane = 100.0f;
    fx.fieldOfView = 60.0f; fx.aspectRatio = (float)W / (float)H;
    fx.jitterOffsetX = 0; fx.jitterOffsetY = 0;
    fx.depthReversed = YES;
    fx.uiTextureComposited = NO;
    fx.contentWidth = W; fx.contentHeight = H;
    fx.depthTexture = texDepth; fx.motionTexture = texMotion;
    fx.uiTexture = nil; fx.outputTexture = texOut;
    fx.shouldResetHistory = NO;

    // Quality: (A,A),(A,A) establish; 3rd encode (B,A) -> OUT.
    for (int k = 0; k < 2; k++) {
        fx.colorTexture = texA; fx.prevColorTexture = texA;
        id<MTLCommandBuffer> cb = [q commandBuffer];
        [fx encodeToCommandBuffer:cb];
        [cb commit]; [cb waitUntilCompleted];
        if (cb.status == MTLCommandBufferStatusError) { r[@"ok"] = @NO; r[@"reason"] = @"e0"; return r; }
    }
    fx.colorTexture = texB; fx.prevColorTexture = texA;
    id<MTLCommandBuffer> e1 = [q commandBuffer];
    [fx encodeToCommandBuffer:e1];
    [e1 commit]; [e1 waitUntilCompleted];
    if (e1.status == MTLCommandBufferStatusError) { r[@"ok"] = @NO; r[@"reason"] = @"e1"; return r; }
    id<MTLCommandBuffer> rb = [q commandBuffer];
    id<MTLBlitCommandEncoder> blit = [rb blitCommandEncoder];
    [blit copyFromTexture:texOut toTexture:texStage];
    [blit endEncoding];
    [rb commit]; [rb waitUntilCompleted];
    void *outBytes = malloc(px * 4);
    [texStage getBytes:outBytes bytesPerRow:W * 4 fromRegion:region mipmapLevel:0];
    writeData([NSString stringWithFormat:@"%@-OUT.rgba", tag], outBytes, px * 4);
    free(outBytes);

    // Timing: fresh instance, warmup, N timed steady-state (B,A) encodes.
    id<MTLFXFrameInterpolator> fx2 = [desc newFrameInterpolatorWithDevice:dev];
    fx2.motionVectorScaleX = 1.0f; fx2.motionVectorScaleY = 1.0f;
    fx2.deltaTime = 1.0f / 60.0f;
    fx2.nearPlane = 0.1f; fx2.farPlane = 100.0f;
    fx2.fieldOfView = 60.0f; fx2.aspectRatio = (float)W / (float)H;
    fx2.depthReversed = YES;
    fx2.contentWidth = W; fx2.contentHeight = H;
    fx2.depthTexture = texDepth; fx2.motionTexture = texMotion;
    fx2.outputTexture = texOut; fx2.shouldResetHistory = NO;
    for (int i = 0; i < 2; i++) {
        fx2.colorTexture = texA; fx2.prevColorTexture = texA;
        id<MTLCommandBuffer> w0 = [q commandBuffer];
        [fx2 encodeToCommandBuffer:w0]; [w0 commit]; [w0 waitUntilCompleted];
        fx2.colorTexture = texB; fx2.prevColorTexture = texA;
        id<MTLCommandBuffer> w1 = [q commandBuffer];
        [fx2 encodeToCommandBuffer:w1]; [w1 commit]; [w1 waitUntilCompleted];
    }
    double *gpu = malloc(sizeof(double) * iters), *wall = malloc(sizeof(double) * iters);
    for (int i = 0; i < iters; i++) {
        fx2.colorTexture = texB; fx2.prevColorTexture = texA;
        double t0 = nowSec();
        id<MTLCommandBuffer> cb = [q commandBuffer];
        [fx2 encodeToCommandBuffer:cb];
        [cb commit];
        double t1 = nowSec();
        [cb waitUntilCompleted];
        double t2 = nowSec();
        if (cb.status == MTLCommandBufferStatusError) { r[@"ok"] = @NO; r[@"reason"] = @"timed"; return r; }
        gpu[i] = (cb.GPUEndTime - cb.GPUStartTime) * 1000.0;
        wall[i] = (t2 - t0) * 1000.0;
        (void)t1;
    }
    qsort(gpu, iters, sizeof(double), cmpd);
    qsort(wall, iters, sizeof(double), cmpd);
    r[@"ok"] = @YES;
    r[@"gpu_ms_med"] = @(gpu[iters / 2]); r[@"gpu_ms_p95"] = @(gpu[(int)(iters * 0.95)]);
    r[@"gpu_ms_min"] = @(gpu[0]); r[@"gpu_ms_max"] = @(gpu[iters - 1]);
    r[@"wall_ms_med"] = @(wall[iters / 2]);
    free(gpu); free(wall);
    free(rgbaA); free(rgbaB); free(rgbaGT); free(depthB); free(depthTmp); free(motion);
    return r;
}

@interface MF1SceneDelegate : UIResponder <UIWindowSceneDelegate>
@property (strong, nonatomic) UIWindow *window;
@end

@implementation MF1SceneDelegate
- (void)scene:(UIScene *)scene willConnectToSession:(UISceneSession *)session
      options:(UISceneConnectionOptions *)options {
    UIWindowScene *ws = (UIWindowScene *)scene;
    self.window = [[UIWindow alloc] initWithWindowScene:ws];
    UILabel *label = [[UILabel alloc] initWithFrame:ws.screen.bounds];
    label.text = @"MF1 probe running...";
    label.textAlignment = NSTextAlignmentCenter;
    [self.window addSubview:label];
    [self.window makeKeyAndVisible];
    dispatch_async(dispatch_get_global_queue(QOS_CLASS_USER_INITIATED, 0), ^{
        @autoreleasepool {
            id<MTLDevice> dev = MTLCreateSystemDefaultDevice();
            NSMutableDictionary *res = [NSMutableDictionary dictionary];
            res[@"device"] = dev.name ?: @"?";
            res[@"supportsFrameInterp"] = @([MTLFXFrameInterpolatorDescriptor supportsDevice:dev]);
            res[@"configs"] = [NSMutableArray array];
            if ([res[@"supportsFrameInterp"] boolValue]) {
                id<MTLCommandQueue> q = [dev newCommandQueue];
                [res[@"configs"] addObject:runConfig(dev, q, 640, 528, 0, 30, @"ios528-exact")];
                [res[@"configs"] addObject:runConfig(dev, q, 640, 528, 1, 30, @"ios528-zero")];
                [res[@"configs"] addObject:runConfig(dev, q, 1280, 720, 0, 30, @"ios720-exact")];
            }
            NSData *js = [NSJSONSerialization dataWithJSONObject:res options:NSJSONWritingPrettyPrinted error:nil];
            writeData(@"mf1-result.json", js.bytes, js.length);
            writeData(@"DONE", "done", 4);
        }
        exit(0);
    });
}
@end

@interface MF1AppDelegate : UIResponder <UIApplicationDelegate>
@end

@implementation MF1AppDelegate
- (BOOL)application:(UIApplication *)app didFinishLaunchingWithOptions:(NSDictionary *)opts {
    return YES;
}
@end

int main(int argc, char *argv[]) {
    @autoreleasepool {
        return UIApplicationMain(argc, argv, nil, NSStringFromClass([MF1AppDelegate class]));
    }
}
