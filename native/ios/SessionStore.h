#import <Foundation/Foundation.h>

FOUNDATION_EXPORT NSString* const SSXSessionStoreErrorDomain;
typedef NS_ENUM(NSInteger, SSXSessionStoreError) {
  SSXCheckpointPathError = 1, SSXCheckpointStatError, SSXCheckpointSizeError,
  SSXCheckpointHashError, SSXCheckpointEncodingError, SSXCheckpointManifestError
};

// Atomic resume manifest. Game memory is saved by Dolphin to a unique file;
// only a completed, hashed file can become the next launch's checkpoint.
@interface SSXSessionStore : NSObject
- (instancetype)initWithDirectory:(NSString*)directory;
- (NSString*)checkpointForIdentity:(NSDictionary*)identity reason:(NSString**)reason;
- (NSString*)newCheckpointPath;
- (BOOL)commitCheckpoint:(NSString*)path identity:(NSDictionary*)identity;
- (BOOL)commitCheckpoint:(NSString*)path identity:(NSDictionary*)identity error:(NSError**)error;
- (void)discardCheckpoint;
@end
