#import <UIKit/UIKit.h>

NS_ASSUME_NONNULL_BEGIN

// Presentation only. The owner applies settings and decides when to dismiss.
// All callbacks and updates run on the main thread.
@interface SSXSessionMenu : UIViewController
@property(nonatomic, copy, nullable) void (^onResume)(void);
@property(nonatomic, copy, nullable) void (^onSmoothing)(void);
@property(nonatomic, copy, nullable) void (^onReset)(void);
@property(nonatomic, copy, nullable) void (^onOutput)(NSString* mode);
@property(nonatomic, copy, nullable) void (^onInternal)(NSInteger scale);
@property(nonatomic, copy, nullable) void (^onFastStart)(BOOL enabled);
@property(nonatomic, copy, nullable) void (^onDualCore)(BOOL enabled);
@property(nonatomic, copy, nullable) void (^onRemaster)(BOOL enabled);

// Output modes: full, three-quarter, match-internal, half.
// Resolution is user-facing picture/output information supplied by the owner.
- (void)updateWithStatus:(NSString*)status
             outputMode:(NSString*)mode
          internalScale:(NSInteger)scale
             resolution:(NSString*)resolution
              fastStart:(BOOL)fastStart
               dualCore:(BOOL)dualCore
               remaster:(BOOL)remaster
        remasterAvailable:(BOOL)remasterAvailable
           canConfigure:(BOOL)canConfigure
               canTrial:(BOOL)canTrial
               canReset:(BOOL)canReset
                  build:(NSString*)build;
@end

NS_ASSUME_NONNULL_END
