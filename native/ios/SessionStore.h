#import <Foundation/Foundation.h>

// Atomic resume manifest. Game memory is saved by Dolphin to a unique file;
// only a completed, hashed file can become the next launch's checkpoint.
@interface SSXSessionStore : NSObject
- (instancetype)initWithDirectory:(NSString*)directory;
- (NSString*)checkpointForIdentity:(NSDictionary*)identity reason:(NSString**)reason;
- (NSString*)newCheckpointPath;
- (BOOL)commitCheckpoint:(NSString*)path identity:(NSDictionary*)identity;
- (void)discardCheckpoint;
@end
