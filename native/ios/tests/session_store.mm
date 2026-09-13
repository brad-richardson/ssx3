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
    NSError* error=nil;
    require(![store commitCheckpoint:incomplete identity:identity error:&error] &&
            error.code==SSXCheckpointStatError && error.userInfo[NSUnderlyingErrorKey],
            @"Missing file must report its filesystem error");
    [[NSData dataWithBytes:"partial" length:7] writeToFile:incomplete atomically:YES];
    require(![store commitCheckpoint:incomplete identity:identity error:&error] &&
            error.code==SSXCheckpointSizeError, @"Partial save must report its size failure");
    require([[store checkpointForIdentity:identity reason:&reason] isEqual:first], @"Failed save replaced good checkpoint");
    NSString* second = [store newCheckpointPath];
    [state writeToFile:second atomically:YES];
    NSString* manifest=[root stringByAppendingPathComponent:@"resume.json"];
    NSData* committed=[NSData dataWithContentsOfFile:manifest];
    [[NSFileManager defaultManager] removeItemAtPath:manifest error:nil];
    [[NSFileManager defaultManager] createDirectoryAtPath:manifest withIntermediateDirectories:NO attributes:nil error:nil];
    require(![store commitCheckpoint:second identity:identity error:&error] &&
            error.code==SSXCheckpointManifestError && error.userInfo[NSUnderlyingErrorKey],
            @"Manifest write failure must preserve its cause");
    require([[NSFileManager defaultManager] fileExistsAtPath:first], @"Manifest failure deleted the old snapshot");
    [[NSFileManager defaultManager] removeItemAtPath:manifest error:nil];
    [committed writeToFile:manifest atomically:YES];
    require([[store checkpointForIdentity:identity reason:&reason] isEqual:first], @"Old checkpoint cannot be recovered");
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
