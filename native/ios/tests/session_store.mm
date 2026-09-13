#import "SessionStore.h"

static void require(BOOL condition, NSString* message) {
  if (!condition) { fprintf(stderr, "%s\n", message.UTF8String); exit(1); }
}

int main() {
  @autoreleasepool {
    NSString* root = [NSTemporaryDirectory() stringByAppendingPathComponent:NSUUID.UUID.UUIDString];
    SSXSessionStore* store = [[SSXSessionStore alloc] initWithDirectory:root];
    NSDictionary* identity = @{@"assets":@"course-a", @"appBuild":@"build-a"};
    NSString* reason = nil;
    require(![store checkpointForIdentity:identity reason:&reason], @"Empty store must boot fresh");
    NSString* first = [store newCheckpointPath];
    NSMutableData* state = [NSMutableData dataWithLength:4096];
    [state writeToFile:first atomically:YES];
    require([store commitCheckpoint:first identity:identity], @"Commit failed");
    // Recreate the store to exercise persisted data, as on app relaunch.
    store = [[SSXSessionStore alloc] initWithDirectory:root];
    require([[store checkpointForIdentity:identity reason:&reason] isEqual:first], @"Relaunch lost checkpoint");
    require(![store checkpointForIdentity:@{@"assets":@"course-b", @"appBuild":@"build-a"} reason:&reason],
            @"Changed course must invalidate the snapshot");
    require(![store checkpointForIdentity:@{@"assets":@"course-a", @"appBuild":@"build-b"} reason:&reason],
            @"Changed app must invalidate the snapshot");
    NSString* incomplete = [store newCheckpointPath];
    [[NSData dataWithBytes:"partial" length:7] writeToFile:incomplete atomically:YES];
    require(![store commitCheckpoint:incomplete identity:identity], @"Partial save committed");
    require([[store checkpointForIdentity:identity reason:&reason] isEqual:first], @"Failed save replaced good checkpoint");
    NSString* second = [store newCheckpointPath];
    [state writeToFile:second atomically:YES];
    require([store commitCheckpoint:second identity:identity], @"Replacement save failed");
    require(![[NSFileManager defaultManager] fileExistsAtPath:first], @"Obsolete snapshot retained");
    ((char*)state.mutableBytes)[1024] = 1;
    [state writeToFile:second atomically:YES];
    require(![store checkpointForIdentity:identity reason:&reason], @"Corrupt save accepted");
    [store discardCheckpoint];
    require(![store checkpointForIdentity:identity reason:&reason], @"Full reset retained resume state");
    require(![[NSFileManager defaultManager] fileExistsAtPath:second], @"Full reset retained snapshot");
    [[NSFileManager defaultManager] removeItemAtPath:root error:nil];
    puts("Session store: relaunch, asset/app changes, interrupted save, corruption and reset passed");
  }
}
