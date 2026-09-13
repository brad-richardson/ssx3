#import "SessionStore.h"
#include "moderngekko/game.hpp"

@implementation SSXSessionStore {
  NSString* _directory;
  NSString* _manifest;
}
- (instancetype)initWithDirectory:(NSString*)directory {
  if ((self = [super init])) {
    _directory = [directory copy];
    _manifest = [_directory stringByAppendingPathComponent:@"resume.json"];
    [[NSFileManager defaultManager] createDirectoryAtPath:_directory withIntermediateDirectories:YES
                                              attributes:nil error:nil];
  }
  return self;
}
- (NSDictionary*)readManifest {
  NSData* data = [NSData dataWithContentsOfFile:_manifest];
  id value = data ? [NSJSONSerialization JSONObjectWithData:data options:0 error:nil] : nil;
  return [value isKindOfClass:NSDictionary.class] ? value : nil;
}
- (NSString*)checkpointForIdentity:(NSDictionary*)identity reason:(NSString**)reason {
  NSDictionary* manifest = [self readManifest];
  if (!manifest) return nil;
  if (![manifest[@"schema"] isEqual:@1]) return nil;
  if (![manifest[@"identity"] isEqual:identity]) {
    if (reason) *reason = @"Game files or app changed. Starting fresh.";
    return nil;
  }
  NSString* name = manifest[@"file"];
  if (![name isKindOfClass:NSString.class] || ![name.lastPathComponent isEqual:name] ||
      ![name.pathExtension isEqual:@"sav"]) return nil;
  NSString* path = [_directory stringByAppendingPathComponent:name];
  const auto hash = moderngekko::HashFileSha256(path.fileSystemRepresentation);
  if (!hash || ![manifest[@"sha256"] isEqual:@(hash->c_str())]) {
    if (reason) *reason = @"Saved session is incomplete. Starting fresh.";
    return nil;
  }
  return path;
}
- (NSString*)newCheckpointPath {
  return [_directory stringByAppendingPathComponent:
      [NSUUID.UUID.UUIDString stringByAppendingPathExtension:@"sav"]];
}
- (BOOL)commitCheckpoint:(NSString*)path identity:(NSDictionary*)identity {
  if (![path.stringByDeletingLastPathComponent isEqual:_directory]) return NO;
  NSDictionary* attributes = [[NSFileManager defaultManager] attributesOfItemAtPath:path error:nil];
  if ([attributes fileSize] < 64) return NO;
  const auto hash = moderngekko::HashFileSha256(path.fileSystemRepresentation);
  if (!hash) return NO;
  NSDictionary* manifest = @{@"schema":@1, @"file":path.lastPathComponent,
      @"sha256":@(hash->c_str()), @"identity":identity,
      @"savedAt":@(NSDate.date.timeIntervalSince1970)};
  NSData* data = [NSJSONSerialization dataWithJSONObject:manifest options:NSJSONWritingPrettyPrinted error:nil];
  if (![data writeToFile:_manifest options:NSDataWritingAtomic error:nil]) return NO;
  // Keep only the committed snapshot. A failed write above leaves the old one intact.
  for (NSString* file in [[NSFileManager defaultManager] contentsOfDirectoryAtPath:_directory error:nil]) {
    if ([file.pathExtension isEqual:@"sav"] && ![file isEqual:path.lastPathComponent])
      [[NSFileManager defaultManager] removeItemAtPath:[_directory stringByAppendingPathComponent:file] error:nil];
  }
  return YES;
}
- (void)discardCheckpoint {
  [[NSFileManager defaultManager] removeItemAtPath:_manifest error:nil];
  for (NSString* file in [[NSFileManager defaultManager] contentsOfDirectoryAtPath:_directory error:nil]) {
    if ([file.pathExtension isEqual:@"sav"])
      [[NSFileManager defaultManager] removeItemAtPath:[_directory stringByAppendingPathComponent:file] error:nil];
  }
}
@end
