#import <Foundation/Foundation.h>

FOUNDATION_EXPORT NSString* const SSXDisplayOutputModeKey;
FOUNDATION_EXPORT NSString* const SSXDisplayInternalScaleKey;

// Menu-owned display choices. Launch overrides affect this instance only;
// saving one choice never persists an override for the other choice.
@interface SSXDisplayPreferences : NSObject
@property(nonatomic, readonly, copy) NSString* outputMode;
@property(nonatomic, readonly) NSInteger internalScale;
- (instancetype)initWithDefaults:(NSUserDefaults*)defaults
                       arguments:(NSArray<NSString*>*)arguments;
- (void)saveOutputMode:(NSString*)mode;
- (void)saveInternalScale:(NSInteger)scale;
@end
