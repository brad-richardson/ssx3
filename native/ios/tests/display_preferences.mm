#import "DisplayPreferences.h"

static void Require(BOOL condition, NSString* message) {
  if (!condition) [NSException raise:@"DisplayPreferencesTestFailure" format:@"%@", message];
}

static void Check(SSXDisplayPreferences* prefs, NSString* output, NSInteger scale) {
  Require([prefs.outputMode isEqualToString:output], @"Unexpected effective output mode");
  Require(prefs.internalScale == scale, @"Unexpected effective internal scale");
}

int main() {
  @autoreleasepool {
    NSString* suite = [@"SSXDisplayPreferencesTest." stringByAppendingString:NSUUID.UUID.UUIDString];
    NSUserDefaults* defaults = [[NSUserDefaults alloc] initWithSuiteName:suite];
    [defaults removePersistentDomainForName:suite];
    @try {
      SSXDisplayPreferences* prefs = [[SSXDisplayPreferences alloc] initWithDefaults:defaults arguments:@[]];
      Check(prefs, @"half", 2);
      Require(![defaults objectForKey:SSXDisplayOutputModeKey] &&
              ![defaults objectForKey:SSXDisplayInternalScaleKey], @"Reading defaults wrote preferences");

      // Explicit full and 1 must override the different fresh-install defaults.
      prefs = [[SSXDisplayPreferences alloc] initWithDefaults:defaults
          arguments:@[@"app", @"-ssxOutputScale", @"full", @"-ssxInternalScale", @"1"]];
      Check(prefs, @"full", 1);
      Check([[SSXDisplayPreferences alloc] initWithDefaults:defaults arguments:@[]], @"half", 2);
      Require(![defaults objectForKey:SSXDisplayOutputModeKey] &&
              ![defaults objectForKey:SSXDisplayInternalScaleKey], @"Launch overrides wrote preferences");

      // Saving output must never save the active 1x launch override.
      [prefs saveOutputMode:@"three-quarter"];
      Check(prefs, @"three-quarter", 1);
      Check([[SSXDisplayPreferences alloc] initWithDefaults:defaults arguments:@[]], @"three-quarter", 2);
      Require(![defaults objectForKey:SSXDisplayInternalScaleKey], @"Output save leaked scale override");

      // Saving internal detail must never save the active Match launch override.
      prefs = [[SSXDisplayPreferences alloc] initWithDefaults:defaults
          arguments:@[@"-ssxOutputScale", @"match-internal", @"-ssxInternalScale", @"2"]];
      [prefs saveInternalScale:1];
      Check(prefs, @"match-internal", 1);
      NSUserDefaults* reopened = [[NSUserDefaults alloc] initWithSuiteName:suite];
      Check([[SSXDisplayPreferences alloc] initWithDefaults:reopened arguments:@[]], @"three-quarter", 1);

      for (NSString* output in @[@"full", @"three-quarter", @"match-internal", @"half"]) {
        [prefs saveOutputMode:output];
        Check(prefs, output, 1);
        Check([[SSXDisplayPreferences alloc] initWithDefaults:reopened arguments:@[]], output, 1);
      }
      [prefs saveInternalScale:2];
      Check(prefs, @"half", 2);
      Check([[SSXDisplayPreferences alloc] initWithDefaults:reopened arguments:@[]], @"half", 2);

      NSDictionary* before = [defaults persistentDomainForName:suite];
      for (id invalid in @[@"FULL", @"0.75", @"", @1, @[], @{}])
        [prefs saveOutputMode:invalid];
      [prefs saveOutputMode:nil];
      const NSInteger invalidScales[] = {0, -1, 3, 999};
      for (NSInteger invalid : invalidScales) [prefs saveInternalScale:invalid];
      Check(prefs, @"half", 2);
      Require([[defaults persistentDomainForName:suite] isEqual:before], @"Invalid save changed storage");

      // Invalid stored dimensions fall back independently, with no implicit repair write.
      [defaults setObject:@"full" forKey:SSXDisplayOutputModeKey];
      for (id invalid in @[@0, @3, @1.5, @YES, @"1", @[], @{}]) {
        [defaults setObject:invalid forKey:SSXDisplayInternalScaleKey];
        Check([[SSXDisplayPreferences alloc] initWithDefaults:defaults arguments:@[]], @"full", 2);
        Require([[defaults objectForKey:SSXDisplayInternalScaleKey] isEqual:invalid], @"Invalid scale was silently rewritten");
      }
      [defaults setInteger:1 forKey:SSXDisplayInternalScaleKey];
      for (id invalid in @[@"FULL", @"", @0, @[], @{}]) {
        [defaults setObject:invalid forKey:SSXDisplayOutputModeKey];
        Check([[SSXDisplayPreferences alloc] initWithDefaults:defaults arguments:@[]], @"half", 1);
      }
      [defaults setObject:@"three-quarter" forKey:SSXDisplayOutputModeKey];

      NSArray* malformed = @[
        @[@"-ssxOutputScale"], @[@"-ssxInternalScale"],
        @[@"-ssxOutputScale", @"FULL", @"-ssxInternalScale", @"1.0"],
        @[@"-ssxOutputScale", @1, @"-ssxInternalScale", @2],
        @[@"-ssxOutputScale", NSNull.null, @"-ssxInternalScale", @"3"],
        @[@1, @[], @"unrelated"], @[@"-ssxInternalScale", @""],
      ];
      for (NSArray* arguments in malformed)
        Check([[SSXDisplayPreferences alloc] initWithDefaults:defaults arguments:arguments], @"three-quarter", 1);
      Check([[SSXDisplayPreferences alloc] initWithDefaults:defaults arguments:nil], @"three-quarter", 1);
      Check([[SSXDisplayPreferences alloc] initWithDefaults:defaults arguments:(id)@"invalid"], @"three-quarter", 1);
      Check([[SSXDisplayPreferences alloc] initWithDefaults:defaults
          arguments:@[@"-ssxOutputScale", @"-ssxInternalScale", @"2"]], @"three-quarter", 2);
      Check([[SSXDisplayPreferences alloc] initWithDefaults:defaults
          arguments:@[@"-ssxOutputScale", @"full", @"-ssxOutputScale", @"match-internal",
                      @"-ssxInternalScale", @"2", @"-ssxInternalScale", @"bad"]], @"match-internal", 2);
      Check([[SSXDisplayPreferences alloc] initWithDefaults:reopened arguments:@[]], @"three-quarter", 1);

      // Mutable strings must not mutate the effective choice after validation.
      NSMutableString* output = [@"full" mutableCopy];
      [prefs saveOutputMode:output];
      [output setString:@"invalid"];
      Check(prefs, @"full", 2);
      Check([[SSXDisplayPreferences alloc] initWithDefaults:reopened arguments:@[]], @"full", 1);
      prefs = [[SSXDisplayPreferences alloc] initWithDefaults:nil arguments:@[]];
      [prefs saveOutputMode:@"full"]; [prefs saveInternalScale:1];
      Check(prefs, @"half", 2);
      puts("Display preferences: defaults, persistence, overrides, malformed input and independent saves passed");
    } @catch (NSException* exception) {
      fprintf(stderr, "%s\n", exception.description.UTF8String);
      return 1;
    } @finally {
      [defaults removePersistentDomainForName:suite];
    }
  }
}
