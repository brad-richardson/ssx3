#import "DisplayPreferences.h"

NSString* const SSXDisplayOutputModeKey = @"SSXOutputMode";
NSString* const SSXDisplayInternalScaleKey = @"SSXInternalScale";

static BOOL ValidOutputMode(id value) {
  return [value isKindOfClass:NSString.class] &&
      ( [value isEqualToString:@"full"] || [value isEqualToString:@"three-quarter"] ||
        [value isEqualToString:@"match-internal"] || [value isEqualToString:@"half"] );
}

static BOOL ValidStoredScale(id value) {
  return [value isKindOfClass:NSNumber.class] &&
      CFGetTypeID((__bridge CFTypeRef)value) != CFBooleanGetTypeID() &&
      ([value isEqualToNumber:@1] || [value isEqualToNumber:@2]);
}

@interface SSXDisplayPreferences ()
@property(nonatomic, readwrite, copy) NSString* outputMode;
@property(nonatomic, readwrite) NSInteger internalScale;
@end

@implementation SSXDisplayPreferences {
  NSUserDefaults* _defaults;
}

- (instancetype)initWithDefaults:(NSUserDefaults*)defaults
                       arguments:(NSArray<NSString*>*)arguments {
  if (!(self = [super init])) return nil;
  // A missing store still permits safe process defaults/overrides. It cannot
  // silently redirect an explicit save into the app's standard preferences.
  _defaults = [defaults isKindOfClass:NSUserDefaults.class] ? defaults : nil;
  id output = [_defaults objectForKey:SSXDisplayOutputModeKey];
  id scale = [_defaults objectForKey:SSXDisplayInternalScaleKey];
  _outputMode = [ValidOutputMode(output) ? output : @"half" copy];
  _internalScale = ValidStoredScale(scale) ? [scale integerValue] : 2;

  if ([arguments isKindOfClass:NSArray.class]) {
    for (NSUInteger i = 0; i + 1 < arguments.count; ++i) {
      id flag = arguments[i], value = arguments[i + 1];
      if (![flag isKindOfClass:NSString.class]) continue;
      if ([flag isEqualToString:@"-ssxOutputScale"] && ValidOutputMode(value)) {
        _outputMode = [value copy];
        ++i;
      } else if ([flag isEqualToString:@"-ssxInternalScale"] &&
                 [value isKindOfClass:NSString.class] &&
                 ([value isEqualToString:@"1"] || [value isEqualToString:@"2"])) {
        _internalScale = [value isEqualToString:@"1"] ? 1 : 2;
        ++i;
      }
      // Invalid values are ignored. Do not consume a following option token;
      // the last valid occurrence of each setting wins independently.
    }
  }
  return self;
}

- (void)saveOutputMode:(NSString*)mode {
  if (!_defaults || !ValidOutputMode(mode)) return;
  NSString* saved = [mode copy];
  [_defaults setObject:saved forKey:SSXDisplayOutputModeKey];
  _outputMode = saved;
}

- (void)saveInternalScale:(NSInteger)scale {
  if (!_defaults || (scale != 1 && scale != 2)) return;
  [_defaults setInteger:scale forKey:SSXDisplayInternalScaleKey];
  _internalScale = scale;
}
@end
