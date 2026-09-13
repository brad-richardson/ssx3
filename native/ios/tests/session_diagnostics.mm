#import "SessionDiagnostics.h"
#import <QuartzCore/QuartzCore.h>
#include <cstdio>
#include <cstdlib>

static void require(BOOL condition, NSString* message) {
  if (!condition) { fprintf(stderr,"%s\n",message.UTF8String); exit(1); }
}
// Protocol-shaped fakes exercise delayed callback ownership without a GPU.
@interface TestDrawable : NSObject
@property(nonatomic,copy) MTLDrawablePresentedHandler handler;
@property(nonatomic) double presentedTime;
- (id<MTLTexture>)texture;
- (void)addPresentedHandler:(MTLDrawablePresentedHandler)handler;
@end
@implementation TestDrawable
- (id<MTLTexture>)texture { return nil; }
- (void)addPresentedHandler:(MTLDrawablePresentedHandler)handler { self.handler=handler; }
@end
@interface TestCommandBuffer : NSObject
@property(nonatomic,copy) MTLCommandBufferHandler handler;
- (double)GPUStartTime;
- (double)GPUEndTime;
- (MTLCommandBufferStatus)status;
- (void)addCompletedHandler:(MTLCommandBufferHandler)handler;
@end
@implementation TestCommandBuffer
- (double)GPUStartTime { return 10; }
- (double)GPUEndTime { return 10.003; }
- (MTLCommandBufferStatus)status { return MTLCommandBufferStatusCompleted; }
- (void)addCompletedHandler:(MTLCommandBufferHandler)handler { self.handler=handler; }
@end
static NSString* read(NSString* dir, NSString* file) {
  return [NSString stringWithContentsOfFile:[dir stringByAppendingPathComponent:file] encoding:NSUTF8StringEncoding error:nil];
}
int main() {
  @autoreleasepool {
    NSString* root=[NSTemporaryDirectory() stringByAppendingPathComponent:NSUUID.UUID.UUIDString];
    NSString* first=[root stringByAppendingPathComponent:@"first"];
    NSString* second=[root stringByAppendingPathComponent:@"second"];
    for (NSString* path in @[first,second])
      [[NSFileManager defaultManager] createDirectoryAtPath:path withIntermediateDirectories:YES attributes:nil error:nil];
    SSXDiagnosticsBegin(first);
    SSXCheckpointStage("serialize_failed", "/private/test.sav", 0, 0);
    SSXDrawableAcquired(CACurrentMediaTime(), true);
    TestDrawable* drawable=[TestDrawable new];
    TestCommandBuffer* buffer=[TestCommandBuffer new];
    SSXDrawableSubmitted((id<CAMetalDrawable>)drawable,(id<MTLCommandBuffer>)buffer);
    SSXDiagnosticsEnd();
    SSXDiagnosticsBegin(second);
    // Delivered after reset: these events must still belong to the first file.
    drawable.presentedTime=10.01;
    drawable.handler((id<MTLDrawable>)drawable);
    buffer.handler((id<MTLCommandBuffer>)buffer);
    drawable.handler=nil; buffer.handler=nil;
    NSString* events=read(first,@"present.csv");
    require([events containsString:@"submit,1,"] && [events containsString:@"display,1,"] &&
            [events containsString:@"gpu,1,"], @"Late callbacks lost their original session");
    require(![read(second,@"present.csv") containsString:@"display,"], @"Old callback contaminated new session");
    NSString* stage=read(first,@"lifecycle.jsonl");
    NSDictionary* row=[NSJSONSerialization JSONObjectWithData:[stage dataUsingEncoding:NSUTF8StringEncoding] options:0 error:nil];
    require([row[@"stage"] isEqual:@"serialize_failed"] && [row[@"file"] isEqual:@"test.sav"] &&
            [row[@"host_seconds"] doubleValue]>0, @"Save diagnostic lost its stage or clock");
    for (int i=0;i<8200;++i) SSXDrawableAcquired(CACurrentMediaTime(),false);
    SSXDiagnosticsFlush();
    require([read(second,@"present.csv") containsString:@",8,0\n"], @"Overflow must explicitly report eight dropped events");
    TestDrawable* unknown=[TestDrawable new];
    TestCommandBuffer* last=[TestCommandBuffer new];
    SSXDrawableSubmitted((id<CAMetalDrawable>)unknown,(id<MTLCommandBuffer>)last);
    unknown.handler((id<MTLDrawable>)unknown); last.handler((id<MTLCommandBuffer>)last);
    unknown.handler=nil; last.handler=nil;
    SSXDiagnosticsEnd();
    require([read(second,@"present.csv") containsString:@",0.000000000,0.000000000\n"], @"Unknown presentation timestamp must be retained");
    [[NSFileManager defaultManager] removeItemAtPath:root error:nil];
    puts("Session diagnostics: delayed callbacks, reset, missing timestamps and bounded overflow passed");
  }
}
