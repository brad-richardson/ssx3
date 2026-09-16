// SSX development frontend. Runtime integration follows SunPad's Apple host;
// see native/ios/README.md for attribution and the validation boundary.
#import <UIKit/UIKit.h>
#include <dirent.h>
#import <Metal/Metal.h>
#import <QuartzCore/CAMetalLayer.h>
#import <AVFAudio/AVFAudio.h>
#import <GameController/GameController.h>
#include <mach/mach.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#include <signal.h>
#include <atomic>
#include <chrono>
#include <mutex>
#include <thread>
#include <vector>
#include <algorithm>
#include <cmath>
#include "moderngekko/runtime.hpp"
#include "moderngekko/game.hpp"
#include "GrabMap.h"
#include "OutputSizing.h"
#import "SessionStore.h"
#import "SessionMenu.h"
#import "DisplayPreferences.h"
#import "SessionDiagnostics.h"
#include "SessionPause.h"
#include "../diagnostics/trial_control.h"
#include "../diagnostics/startup_skip.h"
#include "../diagnostics/callback_timer.h"
#include "dolphin_runtime_internal.hpp"
#include "Common/HookableEvent.h"
#include "Common/Logging/Log.h"
#include "AudioCommon/Mixer.h"
#include "Core/Core.h"
#include "Core/Boot/Boot.h"
#include "Core/Config/GraphicsSettings.h"
#include "Core/Config/MainSettings.h"
#include "Core/State.h"
#include "Core/System.h"
#include "VideoCommon/PerformanceMetrics.h"
#include "VideoCommon/Present.h"
#include "VideoCommon/VideoEvents.h"
#include "VideoCommon/Statistics.h"

extern "C" const ModernGekkoModuleDesc* staticrecomp_get_module();
using Clock = std::chrono::steady_clock;

static NSDictionary* RiderSummary(const CallbackTimer::RiderSample& r) {
  if (!r.valid) return @{@"valid":@NO, @"updates":@(r.updates)};
  return @{@"valid":@YES, @"pointer":@(r.rider), @"x":@(r.x), @"y":@(r.y), @"z":@(r.z), @"state":@(r.state),
           @"guestTimebase":@(r.timebase), @"updates":@(r.updates)};
}
static NSDictionary* CallbackSummary(const CallbackTimer::Summary& s) {
  const auto value=[](double v){ return v>=0 ? (id)@(v) : (id)NSNull.null; };
  return @{@"count":@(s.count), @"cpuMedianMs":value(s.cpu_median_ms), @"cpuP95Ms":value(s.cpu_p95_ms),
           @"wallMedianMs":value(s.wall_median_ms), @"wallP95Ms":value(s.wall_p95_ms)};
}

struct FrameWorkload {
  uint64_t samples=0, draw_calls=0, max_draw_calls=0, primitives=0, vertex_bytes=0, index_bytes=0;
  uint64_t efb_peeks=0, efb_pokes=0;
  int vertex_shaders=0, pixel_shaders=0, textures_created=0, textures_uploaded=0, textures_alive=0;
};

struct PresentedPicture {
  int width=0, height=0, target_width=0, target_height=0;
  uint32_t efb_width=0, efb_height=0;
  uint64_t frame=0;
  unsigned stable=0;
  double host=0;
};

static NSString* Documents() {
  return NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES).firstObject;
}
static void WriteText(NSString* path, NSString* text) {
  [text writeToFile:path atomically:YES encoding:NSUTF8StringEncoding error:nil];
}
static NSDictionary* ReadBuildInfo(NSString* path) {
  if (!path) return @{};
  NSData* data = [NSData dataWithContentsOfFile:path];
  id value = data ? [NSJSONSerialization JSONObjectWithData:data options:0 error:nil] : nil;
  return [value isKindOfClass:NSDictionary.class] ? value : @{};
}
static NSString* BuildDate(id value) {
  if (![value isKindOfClass:NSString.class]) return @"Date unavailable";
  NSDate* date = [[NSISO8601DateFormatter new] dateFromString:value];
  if (!date) return @"Date unavailable";
  NSDateFormatter* formatter = [NSDateFormatter new];
  formatter.dateStyle = NSDateFormatterMediumStyle;
  formatter.timeStyle = NSDateFormatterShortStyle;
  return [formatter stringFromDate:date];
}
static void RuntimeLog(Common::Log::LogLevel, Common::Log::LogType, const char* text, void*) {
  // Preserve warnings/errors in the runtime log, with a bound per message.
  fprintf(stderr, "[ssx-runtime] %.2048s\n", text);
}

@interface SSXMetalView : UIView
@end
@implementation SSXMetalView
+ (Class)layerClass { return CAMetalLayer.class; }
@end


// Virtual analog stick. Deflection maps to the GameCube main stick; the thumb
// re-centers on release. Full deflection is reached at 80% of the radius so a
// thumb never has to leave the pad to hit the rim.
@interface SSXStickView : UIView
@property(nonatomic,copy) void (^onChange)(double x, double y);  // -1..1, y up positive
- (void)reset;
@end
@implementation SSXStickView {
  UIView* _thumb;
  UITouch* _touch;
  double _lastX, _lastY;
}
- (instancetype)initWithFrame:(CGRect)frame {
  if ((self = [super initWithFrame:frame])) {
    self.backgroundColor = [UIColor colorWithWhite:0.15 alpha:0.45];
    self.layer.borderColor = [UIColor colorWithWhite:1 alpha:0.6].CGColor;
    self.layer.borderWidth = 1;
    self.multipleTouchEnabled = NO;
    self.isAccessibilityElement = YES;
    self.accessibilityLabel = @"SSX Stick";
    self.accessibilityTraits = UIAccessibilityTraitButton;
    _thumb = [[UIView alloc] init];
    _thumb.backgroundColor = [UIColor colorWithWhite:0.9 alpha:0.8];
    _thumb.userInteractionEnabled = NO;
    [self addSubview:_thumb];
  }
  return self;
}
- (void)layoutSubviews {
  [super layoutSubviews];
  const CGFloat r = self.bounds.size.width / 2, d = self.bounds.size.width * 0.4;
  self.layer.cornerRadius = r;
  _thumb.bounds = CGRectMake(0, 0, d, d);
  _thumb.layer.cornerRadius = d / 2;
  if (!_touch) _thumb.center = CGPointMake(r, r);
}
- (void)update:(UITouch*)touch {
  const CGPoint p = [touch locationInView:self];
  const CGFloat r = self.bounds.size.width / 2;
  double dx = (p.x - r) / (r * 0.8), dy = (p.y - r) / (r * 0.8);
  const double length = sqrt(dx * dx + dy * dy);
  if (length > 1) { dx /= length; dy /= length; }
  _thumb.center = CGPointMake(r + dx * r * 0.6, r + dy * r * 0.6);
  const double x = dx, y = -dy;
  if (fabs(x - _lastX) < 0.02 && fabs(y - _lastY) < 0.02) return;
  _lastX = x; _lastY = y;
  if (self.onChange) self.onChange(x, y);
}
- (void)touchesBegan:(NSSet<UITouch*>*)touches withEvent:(UIEvent*)event {
  if (_touch) return;
  _touch = touches.anyObject; _lastX = _lastY = NAN;
  [self update:_touch];
}
- (void)touchesMoved:(NSSet<UITouch*>*)touches withEvent:(UIEvent*)event {
  if (_touch && [touches containsObject:_touch]) [self update:_touch];
}
- (void)touchesEnded:(NSSet<UITouch*>*)touches withEvent:(UIEvent*)event {
  if (_touch && [touches containsObject:_touch]) [self reset];
}
- (void)touchesCancelled:(NSSet<UITouch*>*)touches withEvent:(UIEvent*)event {
  if (_touch && [touches containsObject:_touch]) [self reset];
}
- (void)reset {
  const BOOL deflected = _touch != nil || _lastX != 0 || _lastY != 0;
  _touch = nil; _lastX = _lastY = 0;
  const CGFloat r = self.bounds.size.width / 2;
  _thumb.center = CGPointMake(r, r);
  if (deflected && self.onChange) self.onChange(0, 0);
}
@end

@interface SSXViewController : UIViewController {
  SSXMetalView* _surface;
  UILabel* _status;
  UIButton* _menuButton;
  SSXSessionMenu* _sessionMenu;
  SSXDisplayPreferences* _displayPreferences;
  NSString* _menuStatus;
  NSString* _menuBuild;
  int _packInstalled;                       // -1 unknown, 0 no, 1 yes
  BOOL _preloadActive;                      // pack preloaded by this runtime
  NSArray<NSString*>* _coursesCache;
  BOOL _menuClosing;
  BOOL _trialAfterOutput;
  CGFloat _outputScale;
  BOOL _matchInternal;
  CGSize _matchedDrawable;
  double _internalConfiguredHost;
  double _outputResizedHost;
  int _internalScale;
  BOOL _simulatorNullAudio;
  BOOL _debugMainMenu;
  BOOL _cpuThread;        // mode of the running/next runtime; smoothing trial unavailable when on
  BOOL _remasterActive;   // whether the running runtime was configured with the texture pack
  NSString* _activeCourse; // manifest file the running runtime booted with, nil for stock
  int _cpuThreadOverride; // -1 saved preference, 0 -ssxSingleCore, 1 -ssxCPUThread (this process only)
  BOOL _fastDisc;         // launch-only Dolphin FastDiscSpeed comparison
  BOOL _dispatchSamples;  // launch-only dispatch-site sampling (diagnostic overhead)
  StartupBoot::AdvanceInput _startupInput;
  int _startupPhaseLogged;
  BOOL _sequenceFromMainMenu;
  double _sequenceStarted;
  SSXSessionStore* _sessionStore;
  NSDictionary* _sessionIdentity;
  NSString* _courseBuildDescription;
  NSString* _pendingCheckpoint;
  BOOL _checkpointAgain;
  double _checkpointDeadline;
  double _checkpointStarted;
  UIBackgroundTaskIdentifier _saveBackgroundTask;
  SSXSessionPause _pauseState;
  BOOL _restartRequested;
  CADisplayLink* _trialDisplayLink;
  NSMutableArray<UIButton*>* _controls;
  SSXStickView* _stick;
  SSXStickView* _cStick;
  NSMutableSet<NSString*>* _pressed;
  NSSet<NSString*>* _padButtons;      // GameCube buttons currently asserted by a physical controller
  NSSet<NSString*>* _touchDpad;       // D-pad directions asserted by the right touch stick
  double _padMain[2], _padC[2];       // last stick values sent from a physical controller (-1..1)
  CGFloat _overlayAlpha;
  NSTimer* _timer;
  NSString* _report;
  NSFileHandle* _metricsFile;
  NSFileHandle* _inputFile;
  moderngekko::Runtime* _runtime;
  std::mutex _runtimeMutex;
  std::mutex _framesMutex;
  std::vector<double> _frames;
  FrameWorkload _workload;
  uint32_t _efbWidth, _efbHeight;
  double _efbSampleHost;
  PresentedPicture _picture;
  std::atomic<bool> _running;
  std::atomic<bool> _starting;
  std::atomic<bool> _stopRequested;
  Common::EventHook _frameHook;
  Common::EventHook _presentHook;
  Clock::time_point _lastFrame;
  double _startTime;
  double _launchTime;
  double _systemPauseStart;
  double _lastMetric;
  double _lastDiagnosticFlush;
  double _lastTickHost;
  int _lastTrialStatus;
  BOOL _trialCancellationLogged;
  double _lastCapture;
  double _duration;
  double _scheduledTrialAt;
  NSArray<NSDictionary*>* _sequence;
  NSUInteger _eventIndex;
  BOOL _pausedForSystem;
  int _pipe;
}
- (void)systemActive:(BOOL)active;
- (void)logSessionEvent:(NSString*)event details:(NSDictionary*)details;
- (NSDictionary*)outputDetails;
- (BOOL)canChangeOutputScale;
- (BOOL)applyOutputScale:(CGFloat)scale;
- (SSXOutput::Size)matchedOutputSize;
- (BOOL)canApplyMatchedOutput;
- (void)applyMatchedOutput;
- (BOOL)applyInternalScale:(int)scale;
- (void)refreshSessionMenu;
- (void)dismissSessionMenuThen:(dispatch_block_t)completion;
- (BOOL)cpuThreadRequested;
- (BOOL)remasterRequested;
- (BOOL)remasterPackInstalled;
- (NSArray<NSString*>*)installedCourses;
- (nullable NSString*)chosenCourseFile;
@end

@implementation SSXViewController
// Launch trace: the session report only exists once a runtime starts, so a
// crash or a watchdog kill during UI setup leaves nothing behind. This appends
// one line per startup step to Documents/launch-trace.txt, which `collect`
// pulls, and is the only evidence available for a launch that never gets as
// far as starting the game.
static void SSXLaunchTrace(NSString* step) {
  NSString* path=[Documents() stringByAppendingPathComponent:@"launch-trace.txt"];
  NSString* line=[NSString stringWithFormat:@"%.3f %@\n", NSDate.date.timeIntervalSince1970, step];
  fprintf(stderr, "[ssx-launch] %s", line.UTF8String);
  fflush(stderr);
  if (FILE* file=fopen(path.fileSystemRepresentation, "a")) {
    fwrite(line.UTF8String, 1, strlen(line.UTF8String), file);
    fclose(file);
  }
}

- (void)viewDidLoad {
  SSXLaunchTrace(@"viewDidLoad enter");
  [super viewDidLoad];
  _pipe = -1;
  _packInstalled = -1;
  _pauseState.active = YES;
  _saveBackgroundTask = UIBackgroundTaskInvalid;
  _sessionStore = [[SSXSessionStore alloc] initWithDirectory:
      [Documents() stringByAppendingPathComponent:@"Resume"]];
  _controls = [NSMutableArray array];
  _pressed = [NSMutableSet set];
  _padButtons = [NSSet set];
  _touchDpad = [NSSet set];
  _overlayAlpha = 1;
  NSArray<NSString*>* launchArgs=NSProcessInfo.processInfo.arguments;
  _displayPreferences=[[SSXDisplayPreferences alloc] initWithDefaults:NSUserDefaults.standardUserDefaults
      arguments:launchArgs];
  NSString* outputMode=_displayPreferences.outputMode;
  _matchInternal=[outputMode isEqualToString:@"match-internal"];
  // Match holds this initial surface until a measured picture is available.
  _outputScale=[outputMode isEqualToString:@"full"] ? 1 :
      ([outputMode isEqualToString:@"three-quarter"] ? .75 : .5);
  _internalScale=(int)_displayPreferences.internalScale;
  [NSUserDefaults.standardUserDefaults registerDefaults:@{@"SSXDebugMainMenu":@YES}];
  _debugMainMenu=[NSUserDefaults.standardUserDefaults boolForKey:@"SSXDebugMainMenu"];
  if([launchArgs containsObject:@"-ssxDebugMainMenu"]) _debugMainMenu=YES;
  if([launchArgs containsObject:@"-ssxNormalBoot"]) _debugMainMenu=NO;
  [NSUserDefaults.standardUserDefaults registerDefaults:@{@"SSXCPUThread":@YES}];
  [NSUserDefaults.standardUserDefaults registerDefaults:@{@"SSXRemasterTextures":@NO}];
  [NSUserDefaults.standardUserDefaults registerDefaults:@{@"SSXPreloadTextures":@NO}];
  _cpuThreadOverride=[launchArgs containsObject:@"-ssxSingleCore"] ? 0 :
      ([launchArgs containsObject:@"-ssxCPUThread"] ? 1 : -1);
  _cpuThread=[self cpuThreadRequested];
  _fastDisc=[launchArgs containsObject:@"-ssxFastDisc"];
  _dispatchSamples=[launchArgs containsObject:@"-ssxDispatchSamples"];
  _simulatorNullAudio=NO;
#if TARGET_OS_SIMULATOR
  // Graphics-only escape hatch for Simulator RemoteIO RPC failures. This
  // branch does not exist on the phone and requires an automated session.
  _simulatorNullAudio=[launchArgs containsObject:@"-ssxAutoTest"] &&
      [launchArgs containsObject:@"-ssxNullAudio"];
#endif
  self.view.backgroundColor = UIColor.blackColor;
  _surface = [[SSXMetalView alloc] init];
  CAMetalLayer* layer = (CAMetalLayer*)_surface.layer;
  layer.device = MTLCreateSystemDefaultDevice();
  layer.pixelFormat = MTLPixelFormatBGRA8Unorm;
  layer.framebufferOnly = YES;
  [self.view addSubview:_surface];
  _status = [[UILabel alloc] init];
  _status.text = @"Starting SSX 3…";
  _status.textColor = UIColor.whiteColor;
  _status.font = [UIFont monospacedDigitSystemFontOfSize:12 weight:UIFontWeightMedium];
  _status.backgroundColor = [UIColor colorWithWhite:0 alpha:0.6];
  _status.numberOfLines = 2;
  [self.view addSubview:_status];
  // Labels follow Xbox positions; each maps to the GameCube input at that
  // position (bottom A=jump, right B=hand plant (GC X), left X=boost (GC B),
  // top Y=reset). accessibilityLabel/identifier carry the GameCube name.
  NSArray* labels = @[@"A", @"B", @"X", @"Y", @"LB", @"RB", @"Z", @"Start"];
  NSArray* gcNames = @[@"A", @"X", @"B", @"Y", @"L", @"R", @"Z", @"Start"];
  for (NSUInteger i = 0; i < labels.count; ++i) {
    NSString* name = gcNames[i];
    UIButton* button = [UIButton buttonWithType:UIButtonTypeCustom];
    [button setTitle:labels[i] forState:UIControlStateNormal];
    button.accessibilityIdentifier = name;
    button.accessibilityLabel = [@"SSX " stringByAppendingString:name];
    button.backgroundColor = [UIColor colorWithWhite:0.15 alpha:0.65];
    button.layer.cornerRadius = 22;
    button.layer.borderColor = [UIColor colorWithWhite:1 alpha:0.6].CGColor;
    button.layer.borderWidth = 1;
    button.titleLabel.font = [UIFont boldSystemFontOfSize:18];
    [button addTarget:self action:@selector(down:) forControlEvents:UIControlEventTouchDown];
    [button addTarget:self action:@selector(up:) forControlEvents:UIControlEventTouchUpInside|UIControlEventTouchUpOutside|UIControlEventTouchCancel];
    [_controls addObject:button];
    [self.view addSubview:button];
  }
  __weak SSXViewController* weakSelf = self;
  _stick = [[SSXStickView alloc] initWithFrame:CGRectZero];
  _stick.accessibilityLabel = @"SSX Stick";
  _stick.onChange = ^(double x, double y) {
    [weakSelf send:[NSString stringWithFormat:@"SET MAIN %.2f %.2f\n", 0.5 + x * 0.5, 0.5 + y * 0.5]];
  };
  [self.view addSubview:_stick];
  // The game's input map (data/config/input.map) spins and flips from the
  // D-pad only; the main stick turns, crouches and brakes. The right pad
  // therefore drives the D-pad so tricks are reachable on touch.
  _cStick = [[SSXStickView alloc] initWithFrame:CGRectZero];
  _cStick.accessibilityLabel = @"SSX Spin Stick";
  _cStick.onChange = ^(double x, double y) { [weakSelf sendDpadX:x y:y]; };
  [self.view addSubview:_cStick];
  _menuButton = [UIButton buttonWithType:UIButtonTypeSystem];
  [_menuButton setTitle:@"Menu" forState:UIControlStateNormal];
  _menuButton.accessibilityLabel = @"SSX Menu";
  _menuButton.enabled = NO;
  [_menuButton addTarget:self action:@selector(showSessionMenu) forControlEvents:UIControlEventTouchUpInside];
  [self.view addSubview:_menuButton];
  [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(audioEvent:)
      name:AVAudioSessionInterruptionNotification object:nil];
  [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(controllersChanged:)
      name:GCControllerDidConnectNotification object:nil];
  [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(controllersChanged:)
      name:GCControllerDidDisconnectNotification object:nil];
  [self controllersChanged:nil];
  SSXLaunchTrace(@"viewDidLoad starting tick timer");
  _timer = [NSTimer scheduledTimerWithTimeInterval:0.05 target:self selector:@selector(tick)
      userInfo:nil repeats:YES];
}
- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
  if (!_starting && !_running && !_report) [self startGame];
}
- (void)viewDidLayoutSubviews {
  [super viewDidLayoutSubviews];
  const CGRect bounds = self.view.bounds;
  const UIEdgeInsets safe = self.view.safeAreaInsets;
  _surface.frame = bounds;
  CAMetalLayer* layer = (CAMetalLayer*)_surface.layer;
  // Only the Metal game surface changes resolution. UIKit controls and text
  // retain the screen's normal content scale.
  layer.contentsScale = self.view.window.screen.scale * _outputScale;
  layer.drawableSize = _matchInternal && _matchedDrawable.width>0 ? _matchedDrawable :
      CGSizeMake((NSUInteger)(bounds.size.width * layer.contentsScale),
                 (NSUInteger)(bounds.size.height * layer.contentsScale));
  const CGFloat left = safe.left + 12, right = bounds.size.width - safe.right - 174;
  const CGFloat top = MAX(safe.top, 8), bottom = bounds.size.height - safe.bottom - 166;
  const CGPoint positions[] = {{right+56,bottom+112},{right+112,bottom+56},{right,bottom+56},{right+56,bottom},
    {left,top+36},{right+112,top+36},{right+40,top+36},{bounds.size.width/2-36,bounds.size.height-safe.bottom-54}};
  for (NSUInteger i=0; i<_controls.count; ++i)
    _controls[i].frame = CGRectMake(positions[i].x, positions[i].y, i==7?72:52, 48);
  _stick.frame = CGRectMake(left, bottom, 164, 164);
  // C-stick sits just inside the face-button diamond, smaller so a thumb can reach both.
  _cStick.frame = CGRectMake(right-140, bottom+40, 120, 120);
  _status.frame = CGRectMake(left, top, bounds.size.width-safe.left-safe.right-85, 32);
  _menuButton.frame = CGRectMake(bounds.size.width-safe.right-70, top, 60, 32);
}
- (BOOL)prefersStatusBarHidden { return YES; }
- (UIInterfaceOrientationMask)supportedInterfaceOrientations { return UIInterfaceOrientationMaskLandscape; }
- (void)send:(NSString*)commands {
  if (_pipe < 0) return;
  NSData* data = [commands dataUsingEncoding:NSASCIIStringEncoding];
  const ssize_t sent = write(_pipe, data.bytes, data.length);
  if (sent != (ssize_t)data.length) fprintf(stderr, "[ssx-input] write failed errno=%d\n", errno);
  NSDictionary* row = @{@"seconds":@(CACurrentMediaTime()-_startTime), @"commands":commands, @"delivered":@(sent==(ssize_t)data.length)};
  NSData* json = [NSJSONSerialization dataWithJSONObject:row options:0 error:nil];
  [_inputFile writeData:json]; [_inputFile writeData:[@"\n" dataUsingEncoding:NSUTF8StringEncoding]];
}
+ (NSSet<NSString*>*)dpadForX:(double)x y:(double)y {
  NSMutableSet* set = [NSMutableSet set];
  if (x >= 0.5) [set addObject:@"D_RIGHT"];
  if (x <= -0.5) [set addObject:@"D_LEFT"];
  if (y >= 0.5) [set addObject:@"D_UP"];
  if (y <= -0.5) [set addObject:@"D_DOWN"];
  return set;
}
- (void)sendDpadX:(double)x y:(double)y {
  NSSet<NSString*>* wanted = [SSXViewController dpadForX:x y:y];
  NSMutableString* commands = [NSMutableString string];
  for (NSString* d in _touchDpad) if (![wanted containsObject:d]) [commands appendFormat:@"RELEASE %@\n", d];
  for (NSString* d in wanted) if (![_touchDpad containsObject:d]) [commands appendFormat:@"PRESS %@\n", d];
  _touchDpad = wanted;
  if (commands.length) [self send:commands];
}
- (void)down:(UIButton*)button {
  if (_pauseState.WantsPause()) return;
  NSString* name = button.accessibilityIdentifier;
  [_pressed addObject:name];
  button.alpha = 0.5;
  [self send:[NSString stringWithFormat:@"PRESS %@\n",[name uppercaseString]]];
}
- (void)up:(UIButton*)button {
  NSString* name = button.accessibilityIdentifier;
  [_pressed removeObject:name]; button.alpha = _overlayAlpha;
  [self send:[NSString stringWithFormat:@"RELEASE %@\n",[name uppercaseString]]];
}
- (void)releaseControls {
  _startupInput.held=false;
  [_pressed removeAllObjects];
  _padButtons = [NSSet set];
  _touchDpad = [NSSet set];
  _padMain[0] = _padMain[1] = _padC[0] = _padC[1] = 0;
  for (UIButton* button in _controls) button.alpha = _overlayAlpha;
  [_stick reset]; [_cStick reset];
  [self send:@"SET MAIN 0.5 0.5\nSET C 0.5 0.5\nRELEASE A\nRELEASE B\nRELEASE X\nRELEASE Y\nRELEASE Z\nRELEASE L\nRELEASE R\nRELEASE START\nRELEASE D_UP\nRELEASE D_DOWN\nRELEASE D_LEFT\nRELEASE D_RIGHT\n"];
}
// Physical controllers use PS2 positions: cross/A jump, square/X boost+tweak,
// circle/B hand plant, triangle/Y reset, Options (Select) reset, Menu start.
// The four shoulders form a PS2 grab mask translated by GrabMap.h. Sticks and
// the D-pad pass straight through. The overlay dims while a pad is attached.
- (void)controllersChanged:(NSNotification*)note {
  BOOL attached = NO;
  for (GCController* controller in GCController.controllers) {
    GCExtendedGamepad* pad = controller.extendedGamepad;
    if (!pad) continue;
    attached = YES;
    __weak SSXViewController* weakSelf = self;
    pad.valueChangedHandler = ^(GCExtendedGamepad* gamepad, GCControllerElement* element) { [weakSelf applyPad:gamepad]; };
  }
  // Dim only after a pad actually sends input (see applyPad); the simulator
  // and some hosts list controllers that are never used.
  if (!attached) { _overlayAlpha = 1; [self releaseControls]; _stick.alpha = _cStick.alpha = 1; }
  fprintf(stderr, "[ssx-pad] physical controllers=%lu\n", (unsigned long)GCController.controllers.count);
}
- (void)applyPad:(GCExtendedGamepad*)g {
  if (_pauseState.WantsPause()) return;
  if (_overlayAlpha == 1) {
    _overlayAlpha = 0.25;
    for (UIButton* button in _controls) button.alpha = _overlayAlpha;
    _stick.alpha = _cStick.alpha = _overlayAlpha;
  }
  NSMutableSet<NSString*>* wanted = [NSMutableSet set];
  if (g.buttonA.pressed) [wanted addObject:@"A"];
  if (g.buttonX.pressed) [wanted addObject:@"B"];
  if (g.buttonB.pressed) [wanted addObject:@"X"];
  if (g.buttonY.pressed || g.buttonOptions.pressed) [wanted addObject:@"Y"];
  if (g.buttonMenu.pressed) [wanted addObject:@"START"];
  if (g.dpad.up.pressed) [wanted addObject:@"D_UP"];
  if (g.dpad.down.pressed) [wanted addObject:@"D_DOWN"];
  if (g.dpad.left.pressed) [wanted addObject:@"D_LEFT"];
  if (g.dpad.right.pressed) [wanted addObject:@"D_RIGHT"];
  // PS2 feel: the left stick both turns (main stick) and spins/flips (D-pad).
  [wanted unionSet:[SSXViewController dpadForX:g.leftThumbstick.xAxis.value y:g.leftThumbstick.yAxis.value]];
  const uint8_t ps2 = (g.leftShoulder.pressed ? ssx::PS2_L1 : 0) | (g.leftTrigger.pressed ? ssx::PS2_L2 : 0) |
                      (g.rightShoulder.pressed ? ssx::PS2_R1 : 0) | (g.rightTrigger.pressed ? ssx::PS2_R2 : 0);
  const uint8_t gc = ssx::GrabToGameCube(ps2);
  if (gc & ssx::GC_L) [wanted addObject:@"L"];
  if (gc & ssx::GC_R) [wanted addObject:@"R"];
  if (gc & ssx::GC_Z) [wanted addObject:@"Z"];
  NSMutableString* commands = [NSMutableString string];
  for (NSString* button in _padButtons) if (![wanted containsObject:button]) [commands appendFormat:@"RELEASE %@\n", button];
  for (NSString* button in wanted) if (![_padButtons containsObject:button]) [commands appendFormat:@"PRESS %@\n", button];
  _padButtons = wanted;
  const double main[2] = {g.leftThumbstick.xAxis.value, g.leftThumbstick.yAxis.value};
  const double c[2] = {g.rightThumbstick.xAxis.value, g.rightThumbstick.yAxis.value};
  if (fabs(main[0] - _padMain[0]) >= 0.02 || fabs(main[1] - _padMain[1]) >= 0.02) {
    _padMain[0] = main[0]; _padMain[1] = main[1];
    [commands appendFormat:@"SET MAIN %.2f %.2f\n", 0.5 + main[0] * 0.5, 0.5 + main[1] * 0.5];
  }
  if (fabs(c[0] - _padC[0]) >= 0.02 || fabs(c[1] - _padC[1]) >= 0.02) {
    _padC[0] = c[0]; _padC[1] = c[1];
    [commands appendFormat:@"SET C %.2f %.2f\n", 0.5 + c[0] * 0.5, 0.5 + c[1] * 0.5];
  }
  if (commands.length) [self send:commands];
}
- (void)startGame {
  _menuButton.enabled = NO;
  _pauseState.NewSession();
  _restartRequested = NO;
  _pausedForSystem = NO;
  _startTime = _lastMetric = _lastCapture = _duration = 0;
  _eventIndex = 0;
  _lastTickHost = _lastDiagnosticFlush = 0;
  _lastTrialStatus = -1;
  _startupInput={}; _startupPhaseLogged=-1; _sequenceStarted=-1; _sequenceFromMainMenu=NO;
  _trialCancellationLogged = NO;
  _trialAfterOutput = NO;
  { std::lock_guard lock(_framesMutex); _efbWidth=_efbHeight=0; _efbSampleHost=0; _picture={}; }
  _internalConfiguredHost=_outputResizedHost=0;
  _sequence = nil;
  _status.text = @"Starting SSX 3…";
  NSString* game = [Documents() stringByAppendingPathComponent:@"Game"];
  if (![[NSFileManager defaultManager] fileExistsAtPath:[game stringByAppendingPathComponent:@"sys/main.dol"]] ||
      ![[NSFileManager defaultManager] fileExistsAtPath:[game stringByAppendingPathComponent:@"files/opening.bnr"]]) {
    _status.text = @"Game data isn't installed yet. Finish setup, then relaunch.";
    return;
  }
  _starting = true;
  _launchTime = CACurrentMediaTime();
  _cpuThread=[self cpuThreadRequested];  // a changed menu choice applies to this new runtime
  _stopRequested = false;
  NSString* user = [Documents() stringByAppendingPathComponent:@"User"];
  NSString* config = [user stringByAppendingPathComponent:@"Config"];
  NSString* pipes = [user stringByAppendingPathComponent:@"Pipes"];
  NSString* stamp = [NSString stringWithFormat:@"%.3f",NSDate.date.timeIntervalSince1970];
  _report = [[Documents() stringByAppendingPathComponent:@"Reports"] stringByAppendingPathComponent:stamp];
  for (NSString* path in @[config,pipes,_report])
    [[NSFileManager defaultManager] createDirectoryAtPath:path withIntermediateDirectories:YES attributes:nil error:nil];
  freopen([[_report stringByAppendingPathComponent:@"runtime.log"] fileSystemRepresentation], "a", stderr);
  setvbuf(stderr, nullptr, _IOLBF, 0);
  SSXDiagnosticsBegin(_report);
  [self logSessionEvent:@"session_started" details:@{@"appBuild":@SSX_SESSION_BUILD_ID}];
  for (NSString* name in @[@"metrics.jsonl",@"input.jsonl"])
    [[NSFileManager defaultManager] createFileAtPath:[_report stringByAppendingPathComponent:name] contents:nil attributes:nil];
  _metricsFile = [NSFileHandle fileHandleForWritingAtPath:[_report stringByAppendingPathComponent:@"metrics.jsonl"]];
  _inputFile = [NSFileHandle fileHandleForWritingAtPath:[_report stringByAppendingPathComponent:@"input.jsonl"]];
  const char* audioBackend=_simulatorNullAudio ? BACKEND_NULLSOUND : BACKEND_COREAUDIO;
  WriteText([config stringByAppendingPathComponent:@"Dolphin.ini"],
    [NSString stringWithFormat:@"[Core]\nCPUThread = %s\nFastDiscSpeed = %s\nDSPHLE = True\nSkipIPL = True\nLargeEntryPointsMap = False\n[DSP]\nEnableJIT = False\nBackend = %s\n[Interface]\nConfirmStop = False\n",
      _cpuThread ? "True" : "False",_fastDisc ? "True" : "False",audioBackend]);
  WriteText([config stringByAppendingPathComponent:@"GFX.ini"],
    // AspectRatio 1 forces 16:9 output. The game's own Options > Widescreen setting
    // must be on so the 3D scene is rendered anamorphic; Auto detection is not
    // stable across menus and gameplay.
    @"[Hacks]\nImmediateXFBEnable = True\nCapImmediateXFB = False\n[Settings]\nMTLUsePresentDrawable = 1\nAspectRatio = 1\n");
  NSMutableString* mapping = [NSMutableString stringWithString:@"[GCPad1]\nDevice = Pipe/0/ssx3\nOptions/Always Connected = True\n"];
  for (NSString* key in @[@"A",@"B",@"X",@"Y",@"Z",@"Start"])
    [mapping appendFormat:@"Buttons/%@ = `Button %@`\n",key,key.uppercaseString];
  [mapping appendString:@"Main Stick/Up = `Axis MAIN Y +`\nMain Stick/Down = `Axis MAIN Y -`\nMain Stick/Left = `Axis MAIN X -`\nMain Stick/Right = `Axis MAIN X +`\nMain Stick/Calibration = 100.00\n"];
  [mapping appendString:@"C-Stick/Up = `Axis C Y +`\nC-Stick/Down = `Axis C Y -`\nC-Stick/Left = `Axis C X -`\nC-Stick/Right = `Axis C X +`\nC-Stick/Calibration = 100.00\n"];
  [mapping appendString:@"D-Pad/Up = `Button D_UP`\nD-Pad/Down = `Button D_DOWN`\nD-Pad/Left = `Button D_LEFT`\nD-Pad/Right = `Button D_RIGHT`\nTriggers/L = `Button L`\nTriggers/R = `Button R`\n"];
  WriteText([config stringByAppendingPathComponent:@"GCPadNew.ini"],mapping);
  // Remastered textures: the pack lives in User/Load/Textures/GXBE69 and is
  // switched on per game, not in GFX.ini — UICommon::Init rewrites base-layer
  // graphics settings at startup (docs/texture-remaster.md).
  //
  // CacheHiresTextures decides *when* the pack is paid for. Off, every texture
  // is read and PNG-decoded the first time it is drawn, so a burst of new art
  // - a crash, a camera cut, a new stretch of terrain - stalls the frame. On,
  // HiresTexture::Update() decodes the whole pack at startup and holds it, so
  // the stalls go away and the cost moves to boot time and resident memory
  // (about 894 MB decoded for pack-v8, which an 8 GB phone can hold).
  [self prunePackToInstalledFormat];
  NSString* settingsDir=[user stringByAppendingPathComponent:@"GameSettings"];
  [[NSFileManager defaultManager] createDirectoryAtPath:settingsDir
                            withIntermediateDirectories:YES attributes:nil error:nil];
  const BOOL remaster=[self remasterRequested];
  _remasterActive=remaster;  // a changed menu choice applies to the next runtime
  const BOOL preload=[self preloadRequested];
  _preloadActive=preload;
  WriteText([settingsDir stringByAppendingPathComponent:@"GXBE69.ini"],
    [NSString stringWithFormat:@"[Video_Settings]\nHiresTextures = %s\nCacheHiresTextures = %s\n",
      remaster ? "True" : "False", preload ? "True" : "False"]);
  [self logSessionEvent:@"texture_pack_state" details:@{
      @"requested":@(remaster), @"installed":@([self remasterPackInstalled]),
      @"preload":@(preload), @"supportsBC":@([self supportsBlockCompression])}];
  NSString* fifo = [pipes stringByAppendingPathComponent:@"ssx3"];
  if (mkfifo(fifo.fileSystemRepresentation,0600) != 0 && errno != EEXIST) {
    _status.text = @"Could not create controller pipe"; _starting=false; return;
  }
  if (!_simulatorNullAudio) {
    NSError* audioError=nil;
    [AVAudioSession.sharedInstance setCategory:AVAudioSessionCategoryPlayback error:&audioError];
    [AVAudioSession.sharedInstance setPreferredIOBufferDuration:0.01 error:&audioError];
    [AVAudioSession.sharedInstance setActive:YES error:&audioError];
    if (audioError) fprintf(stderr,"[ssx-audio] %s\n",audioError.description.UTF8String);
  } else {
    fprintf(stderr,"[ssx-test] Simulator Null audio: graphics diagnostic only\n");
  }
  UIApplication.sharedApplication.idleTimerDisabled = YES;
  setenv("STATICRECOMP_NO_JIT","1",1);
  setenv("SSX3_NO_EXECUTABLE_MEMORY","1",1);
  // Presence-based in the runtime: only a launch flag enables the per-dispatch sampling branch.
  if (_dispatchSamples) setenv("STATICRECOMP_DISPATCH_SAMPLES","1",1); else unsetenv("STATICRECOMP_DISPATCH_SAMPLES");
  // Course redirect: a manifest applied to the event table at boot
  // (docs/course-selection.md). -ssxCourseManifest <name> names one in
  // Documents/ and wins; otherwise the menu's chosen course names one in
  // Documents/Courses/. Both are bare file names, so neither a launch flag nor
  // a stored preference can reach outside the sandbox.
  {
    NSArray<NSString*>* launch = NSProcessInfo.processInfo.arguments;
    NSUInteger flag = [launch indexOfObject:@"-ssxCourseManifest"];
    unsetenv("SSX_COURSE_MANIFEST");
    NSString* path = nil;
    if (flag != NSNotFound && flag+1 < launch.count) {
      NSString* name = launch[flag+1];
      if ([name containsString:@"/"] || [name hasPrefix:@"."])
        fprintf(stderr,"[ssx3-course] ignoring -ssxCourseManifest %s: bare file name required\n",
                name.UTF8String);
      else
        path = [Documents() stringByAppendingPathComponent:name];
    } else if (NSString* chosen=[self chosenCourseFile]) {
      path = [[Documents() stringByAppendingPathComponent:@"Courses"] stringByAppendingPathComponent:chosen];
    }
    _activeCourse = nil;
    if (path) {
      if ([NSFileManager.defaultManager fileExistsAtPath:path]) {
        setenv("SSX_COURSE_MANIFEST",path.UTF8String,1);
        _activeCourse = path.lastPathComponent;
      } else {
        fprintf(stderr,"[ssx3-course] no manifest at %s\n",path.UTF8String);
      }
    }
    [self logSessionEvent:@"course_selection" details:@{
        @"manifest":_activeCourse ?: NSNull.null,
        @"source":flag!=NSNotFound ? @"launch flag" : (_activeCourse ? @"menu" : @"stock")}];
  }
  Common::Log::SetEmbedderLogCallback(RuntimeLog,nullptr);
  NSArray* args = NSProcessInfo.processInfo.arguments;
  _scheduledTrialAt=-1;
  if ([args containsObject:@"-ssxAutoTest"]) {
    NSString* sequencePath = [Documents() stringByAppendingPathComponent:@"test-sequence.json"];
    NSData* data = [NSData dataWithContentsOfFile:sequencePath];
    NSDictionary* test = data ? [NSJSONSerialization JSONObjectWithData:data options:0 error:nil] : nil;
    _sequence = test[@"events"] ?: @[];
    _sequenceFromMainMenu=[test[@"start_when"] isEqual:@"main_menu"];
    _duration = [test[@"duration"] doubleValue];
    fprintf(stderr,"[ssx-test] events=%lu duration=%.1f\n",(unsigned long)_sequence.count,_duration);
    NSUInteger trialArg=[args indexOfObject:@"-ssxSmoothingAt"];
    if (trialArg != NSNotFound && trialArg+1 < args.count) {
      NSScanner* scanner=[NSScanner scannerWithString:args[trialArg+1]];
      double requested=0;
      if ([scanner scanDouble:&requested] && scanner.isAtEnd && std::isfinite(requested) &&
          requested>=0 && requested<=_duration-40) _scheduledTrialAt=requested;
    }
  }
  const auto* descriptor = staticrecomp_get_module();
  NSMutableDictionary* metadata = [@{@"disc":@"GXBE69", @"moduleABI":@(descriptor->abi_version),
    @"os":UIDevice.currentDevice.systemVersion, @"device":UIDevice.currentDevice.model,
    @"simulator":@(TARGET_OS_SIMULATOR), @"metalDevice":((CAMetalLayer*)_surface.layer).device.name ?: @"unknown",
    // Whether a block-compressed texture pack is even possible on this GPU.
    // Dolphin gates bSupportsST3CTextures/bSupportsBPTC on exactly this
    // (MTLUtil.mm), and a BC pack would upload with no decode at an eighth of
    // RGBA8 - so record the answer rather than guessing from the chip family.
    @"supportsBCTextureCompression":@([self supportsBlockCompression]),
    @"cpuJIT":@NO, @"executableAllocationGuard":@YES, @"vertexLoader":@"software",
    @"renderScale":@(_internalScale), @"cpuThread":@(_cpuThread), @"fastDiscSpeed":@(_fastDisc),
    @"dispatchSamples":@(_dispatchSamples), @"automated":@(_sequence!=nil),
    @"audioEnabled":@(!_simulatorNullAudio), @"audioBackend":@(audioBackend),
    @"debugMainMenuRequested":@(_debugMainMenu),
    @"sequenceStart":_sequenceFromMainMenu ? @"main_menu" : @"runtime_running",
    @"scheduledSmoothingAt":_scheduledTrialAt>=0 ? @(_scheduledTrialAt) : NSNull.null,
    @"reportSchema":@2, @"appBuild":@SSX_SESSION_BUILD_ID,
    @"builtAt":ReadBuildInfo([NSBundle.mainBundle pathForResource:@"build-info" ofType:@"json"])[@"built_at"] ?: @"unknown",
    @"host_seconds":@(CACurrentMediaTime()), @"unix_seconds":@(NSDate.date.timeIntervalSince1970),
    @"presentationTrace":@"Metal drawable presentedTime; final command buffer GPU timing",
    @"presentationTimestampsSupported":@(!TARGET_OS_SIMULATOR)} mutableCopy];
  [metadata addEntriesFromDictionary:[self outputDetails]];
  [[NSJSONSerialization dataWithJSONObject:metadata options:NSJSONWritingPrettyPrinted error:nil]
    writeToFile:[_report stringByAppendingPathComponent:@"launch.json"] atomically:YES];
  const int internalScale=_internalScale;
  const BOOL debugMainMenu=_debugMainMenu;
  std::thread([self,game,user,descriptor,internalScale,debugMainMenu] {
    @autoreleasepool {
      SSXResetNativeTrial([[self->_report stringByAppendingPathComponent:@"native-trial.jsonl"] fileSystemRepresentation]);
      moderngekko::RuntimeConfig options;
      options.game_root = game.fileSystemRepresentation;
      options.user_directory = user.fileSystemRepresentation;
      options.module = moderngekko::ModuleSource::AttachedDescriptor(descriptor);
      options.graphics.backend = "Metal";
      options.graphics.internal_resolution_scale = internalScale;
      options.audio.backend = self->_simulatorNullAudio ? BACKEND_NULLSOUND : BACKEND_COREAUDIO;
      options.input.background_input = true;
      options.show_fps_in_title = false;
      options.render_surface = (__bridge void*)self->_surface.layer;
      auto created = moderngekko::Runtime::Create(std::move(options));
      if (!created) {
        fprintf(stderr,"[ssx-app] create failed: %s\n",created.error->message.c_str());
        NSString* error = @(created.error->message.c_str());
        self->_starting=false;
        dispatch_async(dispatch_get_main_queue(), ^{ self->_status.text=error; self->_menuButton.enabled=YES; });
        return;
      }
      const auto& inspected = created.runtime->GetGameMetadata();
      // Snapshot the loaded course identity. Reading the sidecar on each menu
      // opening would mislabel an old in-memory race after an asset-only push.
      NSDictionary* courseBuild = ReadBuildInfo([Documents() stringByAppendingPathComponent:@"course-build.json"]);
      const auto worldHash = moderngekko::HashFileSha256(
          [game stringByAppendingPathComponent:@"files/data/worlds/bam.big"].fileSystemRepresentation);
      NSString* courseDescription = @"Course build unavailable";
      if (worldHash) {
        NSString* hash = @(worldHash->c_str());
        if ([courseBuild[@"archive_sha256"] isEqual:hash] &&
            [courseBuild[@"build"] isKindOfClass:NSString.class]) {
          courseDescription = [NSString stringWithFormat:@"Course %@\nBuilt %@",
              courseBuild[@"build"], BuildDate(courseBuild[@"built_at"])];
        } else {
          courseDescription = [NSString stringWithFormat:@"Course %@", [hash substringToIndex:8]];
        }
      }
      NSDictionary* identity = @{@"disc":@(inspected.disc_id.c_str()),
        @"dol":@(inspected.dol_sha256.c_str()), @"assets":@(inspected.assets_sha256.c_str()),
        @"appBuild":@SSX_SESSION_BUILD_ID, @"moduleABI":@(descriptor->abi_version)};
      NSString* resumeReason = nil;
      NSString* checkpoint = self->_sequence ? nil : [self->_sessionStore checkpointForIdentity:identity reason:&resumeReason];
      if (checkpoint) {
        moderngekko::detail::SetBootSessionData(std::make_unique<BootSessionData>(
            std::string(checkpoint.fileSystemRepresentation), DeleteSavestateAfterBoot::No));
        fprintf(stderr,"[ssx-session] restoring %s\n",checkpoint.lastPathComponent.UTF8String);
      }
      StartupBoot::Configure(debugMainMenu && !checkpoint ?
          [[self->_report stringByAppendingPathComponent:@"startup.jsonl"] fileSystemRepresentation] : nullptr,
          debugMainMenu && !checkpoint);
      SSXSessionEvent(@"startup_mode", @{@"debugMainMenuRequested":@(debugMainMenu),
          @"debugMainMenuEnabled":@(debugMainMenu && !checkpoint), @"checkpointRestore":@(checkpoint!=nil)});
      SSXSessionEvent(@"runtime_identity", @{@"identity":identity,
        @"checkpoint":checkpoint.lastPathComponent ?: @"", @"resumeReason":resumeReason ?: @""});
      fprintf(stderr,"[ssx-startup] runtime_create_seconds=%.3f resume=%d\n",
              CACurrentMediaTime()-self->_launchTime,checkpoint!=nil);
      dispatch_async(dispatch_get_main_queue(), ^{
        self->_sessionIdentity = identity;
        self->_courseBuildDescription = courseDescription;
        self->_status.text = checkpoint ? @"Resuming your last session…" : (resumeReason ?: @"Starting SSX 3…");
      });
      {
        std::lock_guard lock(self->_runtimeMutex);
        self->_runtime = created.runtime.get();
      }
      self->_lastFrame = Clock::now();
      { std::lock_guard lock(self->_framesMutex); self->_workload={}; }
      self->_frameHook = GetVideoEvents().after_frame_event.Register([self](Core::System&) {
        const auto now = Clock::now();
        std::lock_guard lock(self->_framesMutex);
        if (self->_frames.size()<10000)
          self->_frames.push_back(std::chrono::duration<double,std::milli>(now-self->_lastFrame).count());
        self->_lastFrame=now;
        // Read renderer-owned statistics at its frame event, then transfer a
        // small aggregate under the existing lock. UIKit never reads g_stats.
        // EFB getters dereference renderer texture pointers, so capture here
        // too: a configuration change may destroy/recreate them on this thread.
        const auto& perf=Core::System::GetInstance().GetPerfMetrics();
        self->_efbWidth=perf.GetEFBWidth(); self->_efbHeight=perf.GetEFBHeight();
        self->_efbSampleHost=CACurrentMediaTime();
        auto& w=self->_workload;
        const auto& f=g_stats.this_frame;
        ++w.samples;
        w.draw_calls+=std::max(0,f.num_draw_calls);
        w.max_draw_calls=std::max(w.max_draw_calls,uint64_t(std::max(0,f.num_draw_calls)));
        w.primitives+=std::max(0,f.num_prims);
        w.vertex_bytes+=std::max(0,f.bytes_vertex_streamed);
        w.index_bytes+=std::max(0,f.bytes_index_streamed);
        w.efb_peeks+=std::max(0,f.num_efb_peeks); w.efb_pokes+=std::max(0,f.num_efb_pokes);
        w.vertex_shaders=g_stats.num_vertex_shaders_created;
        w.pixel_shaders=g_stats.num_pixel_shaders_created;
        w.textures_created=g_stats.num_textures_created;
        w.textures_uploaded=g_stats.num_textures_uploaded;
        w.textures_alive=g_stats.num_textures_alive;
      });
      self->_presentHook = GetVideoEvents().after_present_event.Register([self](PresentInfo& info) {
        // Present() has now updated the aspect-correct source suggestion. Copy
        // it on the renderer thread; UIKit reads no renderer-owned pointers.
        if (!g_presenter || info.reason==PresentInfo::PresentReason::VideoInterfaceDuplicate) return;
        const auto [width,height]=g_presenter->GetSuggestedWindowSize();
        const auto& target=g_presenter->GetTargetRectangle();
        const auto& perf=Core::System::GetInstance().GetPerfMetrics();
        std::lock_guard lock(self->_framesMutex);
        auto& p=self->_picture;
        const auto ew=perf.GetEFBWidth(), eh=perf.GetEFBHeight();
        const unsigned stable=p.width==width && p.height==height && p.efb_width==ew &&
            p.efb_height==eh && p.frame!=info.frame_count ? std::min(p.stable+1,3u) : 1;
        p={width,height,target.GetWidth(),target.GetHeight(),ew,eh,info.frame_count,stable,CACurrentMediaTime()};
      });
      self->_running=true; self->_starting=false;
      auto result = self->_stopRequested ? moderngekko::RuntimeRunResult{} : created.runtime->Run();
      self->_running=false;
      self->_frameHook={};
      self->_presentHook={};
      {
        std::lock_guard lock(self->_runtimeMutex);
        self->_runtime=nullptr;
      }
      // Destroy the singleton runtime before a queued Full Reset can create another.
      created.runtime.reset();
      fprintf(stderr,"[ssx-app] stopped error=%d\n",bool(result.error));
      dispatch_async(dispatch_get_main_queue(), ^{
        [self logSessionEvent:@"runtime_stopped" details:@{@"error":@(bool(result.error))}];
        SSXDiagnosticsEnd();
        [self releaseControls];
        if (self->_pipe>=0) { close(self->_pipe); self->_pipe=-1; }
        self->_status.text = result.error ? @"Runtime stopped with an error; see Reports." : @"Session stopped.";
        self->_menuButton.enabled = YES;
        UIApplication.sharedApplication.idleTimerDisabled=NO;
        [self->_metricsFile synchronizeFile]; [self->_inputFile synchronizeFile];
        [self->_metricsFile closeFile]; [self->_inputFile closeFile];
        self->_metricsFile = self->_inputFile = nil;
        if (self->_restartRequested) [self startGame];
      });
    }
  }).detach();
}
- (void)tick {
  static bool traced=false;
  if (!traced) { traced=true; SSXLaunchTrace(@"first tick"); }
  const double host=CACurrentMediaTime();
  if (_lastTickHost && host-_lastTickHost>2 && (_running || _pendingCheckpoint))
    [self logSessionEvent:@"tick_gap" details:@{@"gap_seconds":@(host-_lastTickHost)}];
  _lastTickHost=host;
  if (host-_lastDiagnosticFlush>=1) { SSXDiagnosticsFlush(); _lastDiagnosticFlush=host; }
  [self finishCheckpointIfReady];
  if (_duration>0 && (_starting||_running) && CACurrentMediaTime()-_launchTime>_duration+120) {
    fprintf(stderr,"[ssx-test] wall-clock deadline reached\n");
    [self stopGame]; return;
  }
  if (!_running) {
    static bool tracedMenu=false;
    if (!tracedMenu) { tracedMenu=true; SSXLaunchTrace(@"first menu refresh"); }
    [self refreshSessionMenu];
    static bool tracedMenuDone=false;
    if (!tracedMenuDone) { tracedMenuDone=true; SSXLaunchTrace(@"first menu refresh done"); }
    return;
  }
  [self updatePlayback];
  if (_matchInternal) [self applyMatchedOutput];
  if (_pauseState.NeedsMenu(!_starting) && !self.presentedViewController)
    [self showSessionMenu];
  if (_pauseState.WantsPause()) return;
  if (_pipe<0) _pipe=open([[Documents() stringByAppendingPathComponent:@"User/Pipes/ssx3"] fileSystemRepresentation],O_WRONLY|O_NONBLOCK);
  if (Core::GetState(Core::System::GetInstance()) != Core::State::Running) return;
  if (_trialAfterOutput && !_pendingCheckpoint) {
    BOOL fresh;
    {
      std::lock_guard lock(_framesMutex);
      fresh=SSXOutput::SourceReady(_picture.width,_picture.height,_picture.efb_width,_picture.efb_height,
          _picture.stable,_picture.host,std::max(_internalConfiguredHost,_outputResizedHost),_internalScale);
    }
    const auto matched=[self matchedOutputSize];
    const BOOL ready=fresh && (!_matchInternal || (matched.width && CGSizeEqualToSize(
        ((CAMetalLayer*)_surface.layer).drawableSize,CGSizeMake(matched.width,matched.height))));
    if (ready) {
      _trialAfterOutput=NO;
      [self logSessionEvent:@"trial_requested" details:@{}];
      NativeTrial::Request();
    }
  }
  if (!_startTime) {
    _startTime=CACurrentMediaTime();
    [self logSessionEvent:@"running" details:@{}];
    fprintf(stderr,"[ssx-app] running startup_seconds=%.3f\n",_startTime-_launchTime);
    _menuButton.enabled = YES;
  }
  const double elapsed=CACurrentMediaTime()-_startTime;
  if (_pipe<0) return;
  const auto startupPhase=StartupBoot::phase.load();
  if (_startupPhaseLogged!=static_cast<int>(startupPhase)) {
    _startupPhaseLogged=static_cast<int>(startupPhase);
    [self logSessionEvent:@"startup_phase" details:@{@"phase":@(_startupPhaseLogged)}];
  }
  const BOOL manualStart=[_pressed containsObject:@"Start"] || [_padButtons containsObject:@"START"];
  const auto startupAction=_startupInput.Update(startupPhase,host,!manualStart);
  if (startupAction==StartupBoot::InputAction::PressStart) {
    [self send:@"PRESS START\n"];
    [self logSessionEvent:@"startup_start_pressed" details:@{}];
  } else if(startupAction==StartupBoot::InputAction::ReleaseStart) {
    if(!manualStart) [self send:@"RELEASE START\n"];
    [self logSessionEvent:@"startup_start_released" details:@{}];
  }
  if(_sequenceFromMainMenu && _sequenceStarted<0 && startupPhase==StartupBoot::Phase::MainMenu) {
    _sequenceStarted=elapsed;
    [self logSessionEvent:@"sequence_started" details:@{@"anchor":@"main_menu"}];
  }
  const double sequenceElapsed=_sequenceFromMainMenu ? (_sequenceStarted<0 ? -1 : elapsed-_sequenceStarted) : elapsed;
  while (_eventIndex<_sequence.count && [_sequence[_eventIndex][@"at"] doubleValue]<=sequenceElapsed) {
    [self send:_sequence[_eventIndex][@"commands"]]; ++_eventIndex;
  }
  if (_scheduledTrialAt>=0 && sequenceElapsed>=_scheduledTrialAt) {
    const double requested=_scheduledTrialAt;
    _scheduledTrialAt=-1;
    const auto trial=NativeTrial::status.load();
    if (trial != NativeTrial::Status::Waiting && trial != NativeTrial::Status::Running) {
      _trialCancellationLogged=NO;
      [self logSessionEvent:@"trial_requested" details:@{@"automated":@YES, @"scheduledAt":@(requested)}];
      NativeTrial::Request();
    } else {
      [self logSessionEvent:@"scheduled_trial_skipped" details:@{@"reason":@"A trial is already pending or running."}];
    }
  }
  if (elapsed-_lastMetric>=1) {
    _lastMetric=elapsed;
    std::vector<double> frames;
    FrameWorkload workload;
    { std::lock_guard lock(_framesMutex); frames.swap(_frames); workload=_workload; _workload={}; }
    std::sort(frames.begin(),frames.end());
    const auto quantile=[&](double q){ return frames.empty()?0.0:frames[std::min(frames.size()-1,size_t(q*(frames.size()-1)))]; };
    task_vm_info_data_t vm={}; mach_msg_type_number_t count=TASK_VM_INFO_COUNT;
    task_info(mach_task_self(),TASK_VM_INFO,(task_info_t)&vm,&count);
    const auto& perf=Core::System::GetInstance().GetPerfMetrics();
    const double maxSpeed=perf.GetMaxSpeed();
    NSMutableDictionary* row=[@{@"seconds":@(elapsed),@"fps":@(perf.GetFPS()),@"vps":@(perf.GetVPS()),
      @"speed":@(perf.GetSpeed()),@"frameIntervalP50ms":@(quantile(.5)),@"frameIntervalP95ms":@(quantile(.95)),
      @"frameIntervalP99ms":@(quantile(.99)),@"frames":@(frames.size()),@"footprintBytes":@(vm.phys_footprint),
      @"thermalState":@(NSProcessInfo.processInfo.thermalState),@"eventIndex":@(_eventIndex),
      @"sequenceSeconds":sequenceElapsed>=0 ? @(sequenceElapsed) : NSNull.null,
      @"audioDMAEmptyDequeues":@(Mixer::GetDMAEmptyDequeues()), @"host_seconds":@(CACurrentMediaTime()),
      @"maxSpeedExcludingThrottle":std::isfinite(maxSpeed) ? @(maxSpeed) : NSNull.null,
      @"trialStatus":@(static_cast<int>(NativeTrial::status.load())),
      @"trialLimited":@(NativeTrial::limited.load()), @"trialExtras":@(NativeTrial::extras.load()),
      @"callbackTiming":@{@"update":CallbackSummary(CallbackTimer::Drain(CallbackTimer::update_ring)),
        @"render":CallbackSummary(CallbackTimer::Drain(CallbackTimer::render_ring)), @"cpuThread":@(_cpuThread)},
      @"rider":RiderSummary(CallbackTimer::ReadRider()),
      @"workload":@{@"frameEvents":@(workload.samples), @"drawCalls":@(workload.draw_calls),
        @"maxDrawCallsPerFrameEvent":@(workload.max_draw_calls), @"primitives":@(workload.primitives),
        @"vertexBytes":@(workload.vertex_bytes), @"indexBytes":@(workload.index_bytes),
        @"efbPeeks":@(workload.efb_peeks), @"efbPokes":@(workload.efb_pokes),
        @"vertexShadersCreated":@(workload.vertex_shaders), @"pixelShadersCreated":@(workload.pixel_shaders),
        @"texturesCreated":@(workload.textures_created), @"texturesUploaded":@(workload.textures_uploaded),
        @"texturesAlive":@(workload.textures_alive)}} mutableCopy];
    [row addEntriesFromDictionary:[self outputDetails]];
    [_metricsFile writeData:[NSJSONSerialization dataWithJSONObject:row options:0 error:nil]];
    [_metricsFile writeData:[@"\n" dataUsingEncoding:NSUTF8StringEncoding]];
    _status.text=[NSString stringWithFormat:@"SSX 3 · %.1f FPS · %.0f%% speed · %.0f MB",perf.GetFPS(),perf.GetSpeed()*100,vm.phys_footprint/1048576.0];
  }
  if (_sequence && elapsed-_lastCapture>=15) { _lastCapture=elapsed; Core::SaveScreenShot(); }
  if (_duration>0 && sequenceElapsed>=_duration) [self stopGame];
}
- (void)stopGame {
  _trialAfterOutput=NO;
  NativeTrial::Cancel();
  [self releaseControls]; _stopRequested=true;
  std::lock_guard lock(_runtimeMutex);
  if (_runtime) _runtime->RequestStop();
}
- (void)showSessionMenu {
  if (_pauseState.menu || _starting || self.presentedViewController) return;
  _pauseState.OpenMenu();
  [self logSessionEvent:@"menu_opened" details:@{@"cpuThread":@(_cpuThread), @"internalScale":@(_internalScale)}];
  [self updatePlayback];
  _menuStatus = _pendingCheckpoint ? @"Saving your place…" : @"Paused";
  NSDictionary* build=ReadBuildInfo([NSBundle.mainBundle pathForResource:@"build-info" ofType:@"json"]);
  NSString* version=[NSBundle.mainBundle objectForInfoDictionaryKey:@"CFBundleShortVersionString"] ?: @"0.1";
  _menuBuild=[NSString stringWithFormat:@"App %@ · %@ · Built %@\n%@",version,
      [@SSX_SESSION_BUILD_ID substringToIndex:8],BuildDate(build[@"built_at"]),
      _courseBuildDescription ?: @"Course not loaded"];
  _sessionMenu = [SSXSessionMenu new];
  __weak SSXViewController* weakSelf = self;
  _sessionMenu.onResume = ^{ [weakSelf resumeSession]; };
  _sessionMenu.onSmoothing = ^{
    SSXViewController* self=weakSelf;
    if (!self || ![self canChangeOutputScale]) return;
    [self dismissSessionMenuThen:^{
      SSXViewController* self=weakSelf;
      if (!self) return;
      // Let fresh frames settle a changed detail/Match selection before the
      // trial freezes output size. The pause loop cancels this intent as well.
      self->_trialCancellationLogged = NO;
      self->_trialAfterOutput=YES;
      [self logSessionEvent:@"trial_resume_requested" details:@{}];
      [self resumeSession];
    }];
  };
  _sessionMenu.onOutput = ^(NSString* mode) {
    SSXViewController* self=weakSelf;
    if (!self) return;
    const CGFloat scale=[mode isEqualToString:@"match-internal"] ? 0 :
        ([mode isEqualToString:@"half"] ? .5 : ([mode isEqualToString:@"three-quarter"] ? .75 : 1));
    [self logSessionEvent:@"output_resolution_requested" details:@{
        @"requestedOutputScale":scale ? @(scale) : NSNull.null,
        @"requestedOutputMode":scale ? @"fixed" : @"match-internal"}];
    const BOOL applied=[self applyOutputScale:scale];
    if (applied) [self->_displayPreferences saveOutputMode:mode];
    else self->_menuStatus=@"Still finishing the pause. Try again in a moment.";
    [self refreshSessionMenu];
  };
  _sessionMenu.onInternal = ^(NSInteger scale) {
    SSXViewController* self=weakSelf;
    if (!self) return;
    [self logSessionEvent:@"internal_resolution_requested" details:@{@"targetInternalScale":@(scale)}];
    const BOOL configured=[self applyInternalScale:(int)scale];
    if (configured) [self->_displayPreferences saveInternalScale:scale];
    else self->_menuStatus=@"Still finishing the pause. Try again in a moment.";
    [self refreshSessionMenu];
  };
  _sessionMenu.onFastStart = ^(BOOL enabled) {
    SSXViewController* self=weakSelf;
    if (!self) return;
    self->_debugMainMenu=enabled;
    [NSUserDefaults.standardUserDefaults setBool:enabled forKey:@"SSXDebugMainMenu"];
    [self logSessionEvent:@"startup_preference_changed" details:@{@"enabled":@(enabled)}];
    [self refreshSessionMenu];
  };
  _sessionMenu.onDualCore = ^(BOOL enabled) {
    SSXViewController* self=weakSelf;
    if (!self) return;
    [NSUserDefaults.standardUserDefaults setBool:enabled forKey:@"SSXCPUThread"];
    [self logSessionEvent:@"runtime_preference_changed" details:@{@"cpuThread":@(enabled), @"active":@(self->_cpuThread)}];
    [self refreshSessionMenu];
  };
  _sessionMenu.onPreload = ^(BOOL enabled) {
    SSXViewController* self=weakSelf;
    if (!self) return;
    [NSUserDefaults.standardUserDefaults setBool:enabled forKey:@"SSXPreloadTextures"];
    [self logSessionEvent:@"texture_preload_preference_changed" details:@{@"enabled":@(enabled)}];
    self->_menuStatus=enabled ? @"The pack will be decoded at startup; the next load is slower."
                              : @"The pack will be decoded while riding, as before.";
    [self refreshSessionMenu];
  };
  _sessionMenu.onRemaster = ^(BOOL enabled) {
    SSXViewController* self=weakSelf;
    if (!self) return;
    [NSUserDefaults.standardUserDefaults setBool:enabled forKey:@"SSXRemasterTextures"];
    [self logSessionEvent:@"texture_pack_preference_changed" details:@{
        @"enabled":@(enabled), @"installed":@([self remasterPackInstalled])}];
    self->_menuStatus=enabled ? @"Remastered textures apply after Full Reset or relaunch."
                              : @"The game's own textures apply after Full Reset or relaunch.";
    [self refreshSessionMenu];
  };
  _sessionMenu.onCourse = ^(NSString* course) {
    SSXViewController* self=weakSelf;
    if (!self) return;
    if (course) [NSUserDefaults.standardUserDefaults setObject:course forKey:@"SSXCourseManifest"];
    else [NSUserDefaults.standardUserDefaults removeObjectForKey:@"SSXCourseManifest"];
    [self logSessionEvent:@"course_preference_changed" details:@{@"manifest":course ?: NSNull.null}];
    self->_menuStatus=course ? [NSString stringWithFormat:@"%@ loads after Full Reset or relaunch.",
                                    course.stringByDeletingPathExtension]
                             : @"The stock event loads after Full Reset or relaunch.";
    [self refreshSessionMenu];
  };
  _sessionMenu.onReset = ^{
    SSXViewController* self=weakSelf;
    if (!self || self->_pendingCheckpoint || self->_starting || self->_stopRequested) return;
    const auto trial=NativeTrial::status.load();
    if (trial==NativeTrial::Status::Waiting || trial==NativeTrial::Status::Running) return;
    [self logSessionEvent:@"full_reset_requested" details:@{@"cpuThreadNext":@([self cpuThreadRequested])}];
    [self dismissSessionMenuThen:^{
      SSXViewController* self=weakSelf;
      if (!self) return;
      [self->_sessionStore discardCheckpoint];
      self->_pauseState.menu = NO;
      self->_restartRequested = YES;
      self->_menuButton.enabled = NO;
      self->_status.text = @"Restarting with the current game files…";
      if (!self->_running && !self->_starting) [self startGame];
      else [self stopGame];
    }];
  };
  [self refreshSessionMenu];
  [self presentViewController:_sessionMenu animated:YES completion:nil];
}
- (void)dismissSessionMenuThen:(dispatch_block_t)completion {
  if (_menuClosing) return;
  if (!_sessionMenu) { completion(); return; }
  // Keep pause intent until the animation finishes. Prevent repeated taps from
  // resuming or resetting a runtime twice while the modal is disappearing.
  _menuClosing=YES;
  _sessionMenu.view.userInteractionEnabled=NO;
  [self dismissViewControllerAnimated:YES completion:^{
    self->_sessionMenu=nil;
    self->_menuClosing=NO;
    completion();
  }];
}
- (void)resumeSession {
  __weak SSXViewController* weakSelf=self;
  [self dismissSessionMenuThen:^{
    SSXViewController* self=weakSelf;
    if (!self) return;
    NSError* error = nil;
    const BOOL activated = self->_simulatorNullAudio || [AVAudioSession.sharedInstance setActive:YES error:&error];
    self->_pauseState.RequestResume(UIApplication.sharedApplication.applicationState == UIApplicationStateActive, activated);
    if (!activated) fprintf(stderr,"[ssx-lifecycle] audio reactivation failed: %s\n",error.description.UTF8String);
    if (!self->_running && !self->_starting) [self startGame];
    else [self updatePlayback];
  }];
}
- (void)trialDisplayTick:(CADisplayLink*)link {
  // This is a refresh-rate hint. Display-link callbacks are not proof that a
  // new game frame reached the screen; the native trial logs render counts.
}
- (void)updateTrialDisplayLink {
  const BOOL running = NativeTrial::status.load() == NativeTrial::Status::Running && !_pauseState.WantsPause();
  if (running && !_trialDisplayLink) {
    _trialDisplayLink = [CADisplayLink displayLinkWithTarget:self selector:@selector(trialDisplayTick:)];
    const float maximum = self.view.window.screen.maximumFramesPerSecond;
    _trialDisplayLink.preferredFrameRateRange = CAFrameRateRangeMake(MIN(60,maximum),maximum,maximum);
    [_trialDisplayLink addToRunLoop:NSRunLoop.mainRunLoop forMode:NSRunLoopCommonModes];
  }
  if (!running && _trialDisplayLink) { [_trialDisplayLink invalidate]; _trialDisplayLink=nil; }
}
- (void)refreshSessionMenu {
  if (!_sessionMenu || _menuClosing) return;
  CAMetalLayer* layer=(CAMetalLayer*)_surface.layer;
  PresentedPicture picture;
  { std::lock_guard lock(_framesMutex); picture=_picture; }
  const BOOL fresh=SSXOutput::SourceReady(picture.width,picture.height,picture.efb_width,picture.efb_height,
      picture.stable,picture.host,_internalConfiguredHost,_internalScale);
  NSString* visible=fresh ? [NSString stringWithFormat:@"Visible image %d × %d",picture.width,picture.height] :
      @"Visible image updates on resume";
  const auto matched=[self matchedOutputSize];
  const BOOL pending=_matchInternal && (!matched.width ||
      !CGSizeEqualToSize(layer.drawableSize,CGSizeMake(matched.width,matched.height)));
  NSString* resolution=[NSString stringWithFormat:@"%@\nOutput %.0f × %.0f, including bars%@",visible,
      layer.drawableSize.width,layer.drawableSize.height,pending ? @" · Match updates on resume" : @""];
  NSString* mode=_matchInternal ? @"match-internal" :
      (_outputScale==1 ? @"full" : (_outputScale==.75 ? @"three-quarter" : @"half"));
  const auto trial=NativeTrial::status.load();
  const BOOL canConfigure=[self canChangeOutputScale];
  NSString* status=_pendingCheckpoint ? @"Saving your place…" : (_menuStatus ?: @"Paused");
  if (!_pendingCheckpoint && NativeTrial::limited.load())
    status=[status stringByAppendingString:@" · Smoothing ended to maintain game speed."];
  if ([NSUserDefaults.standardUserDefaults boolForKey:@"SSXCPUThread"]!=(BOOL)_cpuThread && _cpuThreadOverride<0)
    status=[status stringByAppendingString:@" · Dual-core change applies after Full Reset."];
  if ([self remasterRequested]!=_remasterActive)
    status=[status stringByAppendingString:@" · Texture change applies after Full Reset."];
  NSString* wantedCourse=[self chosenCourseFile];
  if (_running && ((wantedCourse==nil)!=(_activeCourse==nil) ||
                   (wantedCourse && ![wantedCourse isEqualToString:_activeCourse])))
    status=[status stringByAppendingString:@" · Course change applies after Full Reset."];
  [_sessionMenu updateWithStatus:status outputMode:mode internalScale:_internalScale resolution:resolution
      fastStart:_debugMainMenu dualCore:[NSUserDefaults.standardUserDefaults boolForKey:@"SSXCPUThread"]
      remaster:[self remasterRequested] remasterAvailable:[self remasterPackInstalled]
      preload:[NSUserDefaults.standardUserDefaults boolForKey:@"SSXPreloadTextures"]
      courses:[self installedCourses] course:[self chosenCourseFile]
      canConfigure:canConfigure canTrial:canConfigure
      canReset:(!_pendingCheckpoint && !_starting && !_stopRequested &&
          trial!=NativeTrial::Status::Waiting && trial!=NativeTrial::Status::Running) build:_menuBuild ?: @""];
}
- (NSDictionary*)outputDetails {
  CAMetalLayer* layer=(CAMetalLayer*)_surface.layer;
  const auto matched=[self matchedOutputSize];
  std::lock_guard lock(_framesMutex);
  return @{@"outputScale":@(_outputScale), @"screenScale":@(self.view.window.screen.scale),
    @"outputMode":_matchInternal ? @"match-internal" : @"fixed",
    @"matchPending":@(_matchInternal && (!matched.width ||
        !CGSizeEqualToSize(layer.drawableSize,CGSizeMake(matched.width,matched.height)))),
    @"matchCappedAtNative":@(_matchInternal && matched.capped),
    @"requestedInternalScale":@(_internalScale),
    @"internalConfiguredHostSeconds":@(_internalConfiguredHost),
    @"outputResizedHostSeconds":@(_outputResizedHost),
    @"efbWidth":_efbSampleHost ? @(_efbWidth) : NSNull.null,
    @"efbHeight":_efbSampleHost ? @(_efbHeight) : NSNull.null,
    @"efbSampleHostSeconds":_efbSampleHost ? @(_efbSampleHost) : NSNull.null,
    @"sourcePictureWidth":_picture.host ? @(_picture.width) : NSNull.null,
    @"sourcePictureHeight":_picture.host ? @(_picture.height) : NSNull.null,
    @"pictureTargetWidth":_picture.host ? @(_picture.target_width) : NSNull.null,
    @"pictureTargetHeight":_picture.host ? @(_picture.target_height) : NSNull.null,
    @"pictureSampleHostSeconds":_picture.host ? @(_picture.host) : NSNull.null,
    @"pictureFrame":_picture.host ? @(_picture.frame) : NSNull.null,
    @"pictureEFBWidth":_picture.host ? @(_picture.efb_width) : NSNull.null,
    @"pictureEFBHeight":_picture.host ? @(_picture.efb_height) : NSNull.null,
    @"outputWidth":@(layer.drawableSize.width), @"outputHeight":@(layer.drawableSize.height),
    @"drawableWidth":@(layer.drawableSize.width), @"drawableHeight":@(layer.drawableSize.height)};
}
- (BOOL)cpuThreadRequested {
  return _cpuThreadOverride>=0 ? _cpuThreadOverride==1 : [NSUserDefaults.standardUserDefaults boolForKey:@"SSXCPUThread"];
}
- (NSArray<NSString*>*)installedCourses {
  // Documents/Courses/*.txt, as written by tools/course_manifests.py. Cached
  // for the same reason as the pack check: the menu asks several times per
  // refresh and the set only changes when a new install restarts the app.
  if (_coursesCache) return _coursesCache;
  NSString* directory=[Documents() stringByAppendingPathComponent:@"Courses"];
  NSArray* entries=[[NSFileManager defaultManager] contentsOfDirectoryAtPath:directory error:nil];
  NSMutableArray* courses=[NSMutableArray array];
  for (NSString* name in [entries sortedArrayUsingSelector:@selector(compare:)])
    if ([name.pathExtension isEqualToString:@"txt"] && ![name hasPrefix:@"."])
      [courses addObject:name];
  _coursesCache = courses;
  return _coursesCache;
}
- (nullable NSString*)chosenCourseFile {
  NSString* chosen=[NSUserDefaults.standardUserDefaults stringForKey:@"SSXCourseManifest"];
  // A preference that names a manifest which is no longer installed reverts to
  // the stock event rather than failing the boot.
  return (chosen.length && [[self installedCourses] containsObject:chosen]) ? chosen : nil;
}
// Remove pack files of the format this container is not meant to hold.
//
// HiresTexture::Update searches one directory for both .png and .dds and keys
// what it finds on the file *stem*, so a stem present in both is resolved by
// whichever the search returns first - and pushing a DDS pack cannot remove the
// PNG pack it replaces, because devicectl copies and never deletes. The
// installer records the format it pushed in User/pack-format.txt; this is the
// only side that can act on it.
- (NSUInteger)prunePackToInstalledFormat {
  NSString* user=[Documents() stringByAppendingPathComponent:@"User"];
  NSString* marker=[user stringByAppendingPathComponent:@"pack-format.txt"];
  NSString* wanted=[[NSString stringWithContentsOfFile:marker encoding:NSUTF8StringEncoding
                                                 error:nil]
      stringByTrimmingCharactersInSet:NSCharacterSet.whitespaceAndNewlineCharacterSet];
  if (!wanted.length) return 0;
  NSString* stale=[wanted isEqualToString:@"dds"] ? @"png"
                 : ([wanted isEqualToString:@"png"] ? @"dds" : nil);
  if (!stale) return 0;
  NSString* pack=[user stringByAppendingPathComponent:@"Load/Textures/GXBE69"];
  NSFileManager* files=NSFileManager.defaultManager;
  NSUInteger removed=0;
  // Enumerated in batches rather than with contentsOfDirectoryAtPath: a stale
  // PNG pack is 8,806 names and this runs on the main thread before the boot.
  NSDirectoryEnumerator* walk=[files enumeratorAtURL:[NSURL fileURLWithPath:pack]
      includingPropertiesForKeys:nil options:NSDirectoryEnumerationSkipsHiddenFiles
                    errorHandler:nil];
  for (NSURL* url in walk) {
    if (![url.pathExtension.lowercaseString isEqualToString:stale]) continue;
    if (![url.lastPathComponent hasPrefix:@"tex1_"]) continue;
    if ([files removeItemAtURL:url error:nil]) removed++;
  }
  if (removed) {
    _packInstalled=-1;                  // the probe's answer may have changed
    [self logSessionEvent:@"texture_pack_pruned" details:@{
        @"format":wanted, @"removed":@(removed), @"removedExtension":stale}];
  }
  return removed;
}
- (BOOL)supportsBlockCompression {
  id<MTLDevice> device = ((CAMetalLayer*)_surface.layer).device;
  if (@available(iOS 16.4, macOS 11.0, *))
    return device && [device supportsBCTextureCompression];
  return NO;
}
- (BOOL)preloadRequested {
  return [NSUserDefaults.standardUserDefaults boolForKey:@"SSXPreloadTextures"]
      && [self remasterRequested] && [self remasterPackInstalled];
}
- (BOOL)remasterPackInstalled {
  // Dolphin reads Load/Textures/<game id>/; an empty directory is not a pack.
  //
  // This answer is cached and found by reading a single directory entry. The
  // first version listed the directory with contentsOfDirectoryAtPath:, which
  // builds an array of every name in it - fine for a handful of files, fatal
  // for a real pack: the 17-course pack is 8,904 files, the paused menu
  // refreshes at 20 Hz, and two calls per refresh starved the main thread
  // until the watchdog killed the app on launch.
  if (_packInstalled >= 0) return _packInstalled > 0;
  NSString* pack=[Documents() stringByAppendingPathComponent:@"User/Load/Textures/GXBE69"];
  _packInstalled = 0;
  if (DIR* directory=opendir(pack.fileSystemRepresentation)) {
    while (struct dirent* entry=readdir(directory)) {
      if (entry->d_name[0]=='.') continue;      // ".", "..", and dot files
      _packInstalled = 1;
      break;
    }
    closedir(directory);
  }
  return _packInstalled > 0;
}
- (BOOL)remasterRequested {
  return [self remasterPackInstalled] &&
      [NSUserDefaults.standardUserDefaults boolForKey:@"SSXRemasterTextures"];
}
- (BOOL)canChangeOutputScale {
  const auto trial=NativeTrial::status.load();
  return _running && !_starting && !_stopRequested && _pausedForSystem && _pauseState.WantsPause() &&
      Core::GetState(Core::System::GetInstance()) == Core::State::Paused && !_pendingCheckpoint &&
      trial != NativeTrial::Status::Waiting && trial != NativeTrial::Status::Running;
}
- (BOOL)applyOutputScale:(CGFloat)scale {
  // GetState(Paused) becomes true before the CPU/FIFO have actually stopped.
  // Synchronize using Dolphin's guard after the injected draw and checkpoint
  // capture have drained. The renderer rebuilds its backbuffer on its next
  // BindBackbuffer; UIKit never calls renderer methods that create GPU objects.
  std::lock_guard lock(_runtimeMutex);
  if (!_runtime || ![self canChangeOutputScale] || (scale != 0 && scale != 1 && scale != .75 && scale != .5)) {
    [self logSessionEvent:@"output_resolution_rejected" details:@{@"requestedOutputScale":@(scale)}];
    return NO;
  }
  {
    Core::CPUThreadGuard guard(Core::System::GetInstance());
    CAMetalLayer* layer=(CAMetalLayer*)_surface.layer;
    _matchInternal=scale==0;
    if (_matchInternal) {
      const auto size=[self matchedOutputSize];
      if (size.width>0) {
        _outputScale=size.scale;
        _matchedDrawable=CGSizeMake(size.width,size.height);
        layer.contentsScale=self.view.window.screen.scale * _outputScale;
        layer.drawableSize=_matchedDrawable;
      }
      // If the source is not ready, retain the current surface until a fresh
      // measured presentation arrives. No EFB-allocation-size guess is used.
    } else {
      _outputScale=scale; _matchedDrawable=CGSizeZero;
      layer.contentsScale=self.view.window.screen.scale * scale;
      layer.drawableSize=CGSizeMake((NSUInteger)(layer.bounds.size.width * layer.contentsScale),
                                   (NSUInteger)(layer.bounds.size.height * layer.contentsScale));
    }
    if (g_presenter) g_presenter->ResizeSurface();
    // The guard has drained earlier CPU/FIFO work. A later after-present
    // sample acknowledges this resize before smoothing can freeze the output.
    _outputResizedHost=CACurrentMediaTime();
  }
  [self logSessionEvent:@"output_resolution_applied" details:@{}];
  return YES;
}
- (SSXOutput::Size)matchedOutputSize {
  std::lock_guard lock(_framesMutex);
  if (!SSXOutput::SourceReady(_picture.width,_picture.height,_picture.efb_width,_picture.efb_height,
      _picture.stable,_picture.host,_internalConfiguredHost,_internalScale)) return {};
  const CGSize bounds=_surface.bounds.size;
  const double screenScale=self.view.window.screen.scale;
  return SSXOutput::Match(bounds.width*screenScale,bounds.height*screenScale,_picture.width,_picture.height);
}
- (BOOL)canApplyMatchedOutput {
  const auto trial=NativeTrial::status.load();
  if (!_matchInternal || !_running || _starting || _stopRequested || _pendingCheckpoint ||
      trial==NativeTrial::Status::Waiting || trial==NativeTrial::Status::Running ||
      UIApplication.sharedApplication.applicationState!=UIApplicationStateActive) return NO;
  return [self canChangeOutputScale] || (!_pausedForSystem && !_pauseState.WantsPause() &&
      Core::GetState(Core::System::GetInstance())==Core::State::Running);
}
- (void)applyMatchedOutput {
  if (![self canApplyMatchedOutput]) return;
  auto size=[self matchedOutputSize];
  CAMetalLayer* layer=(CAMetalLayer*)_surface.layer;
  if (!size.width || CGSizeEqualToSize(layer.drawableSize,CGSizeMake(size.width,size.height))) return;
  std::lock_guard lock(_runtimeMutex);
  if (!_runtime || ![self canApplyMatchedOutput]) return;
  {
    // Also safe for the first measured image during ordinary play: this guard
    // drains CPU/FIFO and restores their prior running state. Never hold the
    // frame snapshot mutex while acquiring it, or resize within a trial/save.
    Core::CPUThreadGuard guard(Core::System::GetInstance());
    size=[self matchedOutputSize];
    if (!size.width) return;
    _outputScale=size.scale;
    _matchedDrawable=CGSizeMake(size.width,size.height);
    layer.contentsScale=self.view.window.screen.scale * _outputScale;
    layer.drawableSize=_matchedDrawable;
    if (g_presenter) g_presenter->ResizeSurface();
    _outputResizedHost=CACurrentMediaTime();
  }
  [self logSessionEvent:@"output_resolution_applied" details:@{@"automatic":@YES,@"cappedAtNative":@(size.capped)}];
}
- (BOOL)applyInternalScale:(int)scale {
  std::lock_guard lock(_runtimeMutex);
  if (!_runtime || ![self canChangeOutputScale] || scale < 1 || scale > 4) {
    [self logSessionEvent:@"internal_resolution_rejected" details:@{@"targetInternalScale":@(scale)}];
    return NO;
  }
  {
    Core::CPUThreadGuard guard(Core::System::GetInstance());
    Config::SetBase(Config::GFX_EFB_SCALE, scale);
    _internalScale=scale;
    _internalConfiguredHost=CACurrentMediaTime();
  }
  // Configured is intentional: the EFB is recreated by VideoConfig's next
  // render-thread config check after Resume. Keep reporting the last measured
  // dimensions and their host timestamp until that renderer sample advances.
  [self logSessionEvent:@"internal_resolution_configured" details:@{}];
  return YES;
}
- (void)savePausedSession {
  if (_sequence || !_sessionIdentity || !_running || _stopRequested) return;
  if (_pendingCheckpoint) {
    _checkpointAgain = YES;
    [self logSessionEvent:@"checkpoint_deferred" details:@{}];
    return;
  }
  _pendingCheckpoint = [_sessionStore newCheckpointPath];
  _checkpointStarted = CACurrentMediaTime();
  _checkpointDeadline = _checkpointStarted + 20;
  __weak SSXViewController* weakSelf = self;
  _saveBackgroundTask = [UIApplication.sharedApplication beginBackgroundTaskWithName:@"Save paused SSX session" expirationHandler:^{
    [weakSelf logSessionEvent:@"checkpoint_background_expired" details:@{}];
    [weakSelf endSaveBackgroundTask];
  }];
  fprintf(stderr,"[ssx-session] save requested %s\n",_pendingCheckpoint.lastPathComponent.UTF8String);
  [self logSessionEvent:@"checkpoint_requested" details:@{@"deadline_host_seconds":@(_checkpointDeadline),
    @"backgroundTaskValid":@(_saveBackgroundTask!=UIBackgroundTaskInvalid)}];
  State::SaveAs(Core::System::GetInstance(), _pendingCheckpoint.fileSystemRepresentation);
}
- (void)endSaveBackgroundTask {
  if (_saveBackgroundTask != UIBackgroundTaskInvalid) {
    [UIApplication.sharedApplication endBackgroundTask:_saveBackgroundTask];
    _saveBackgroundTask = UIBackgroundTaskInvalid;
  }
}
- (void)finishCheckpointIfReady {
  if (!_pendingCheckpoint) return;
  const BOOL ready = [[NSFileManager defaultManager] fileExistsAtPath:_pendingCheckpoint];
  if (!ready && CACurrentMediaTime() < _checkpointDeadline) return;
  NSError* error = nil;
  const BOOL saved = ready && [_sessionStore commitCheckpoint:_pendingCheckpoint identity:_sessionIdentity error:&error];
  NSError* cause = error.userInfo[NSUnderlyingErrorKey];
  NSMutableArray* temporary = [NSMutableArray array];
  if (!saved) {
    NSString* parent=_pendingCheckpoint.stringByDeletingLastPathComponent;
    for (NSString* name in [[NSFileManager defaultManager] contentsOfDirectoryAtPath:parent error:nil]) {
      if ([name hasPrefix:_pendingCheckpoint.lastPathComponent] && [name.pathExtension isEqual:@"tmp"]) {
        NSDictionary* attributes=[[NSFileManager defaultManager] attributesOfItemAtPath:[parent stringByAppendingPathComponent:name] error:nil];
        [temporary addObject:@{@"file":name, @"bytes":@([attributes fileSize])}];
      }
    }
  }
  [self logSessionEvent:@"checkpoint_finished" details:@{@"saved":@(saved), @"fileExists":@(ready),
    @"duration_seconds":@(CACurrentMediaTime()-_checkpointStarted),
    @"reason":saved ? @"committed" : (ready ? (error.userInfo[@"stage"] ?: @"unknown_commit_failure") : @"file_timeout"),
    @"errorDomain":error.domain ?: @"", @"errorCode":@(error.code),
    @"underlyingDomain":cause.domain ?: @"", @"underlyingCode":@(cause.code), @"temporaryFiles":temporary}];
  fprintf(stderr,"[ssx-session] save complete=%d\n",saved);
  _pendingCheckpoint = nil;
  _menuStatus = saved ? @"Your place is saved" : @"Couldn’t save for next time. You can still resume.";
  [self refreshSessionMenu];
  [self endSaveBackgroundTask];
  // A second pause during compression must not leave the earlier position saved.
  if (_checkpointAgain) {
    _checkpointAgain = NO;
    if (_pausedForSystem) [self savePausedSession];
  }
}
- (void)systemActive:(BOOL)active {
  _pauseState.SetActive(active, _running || _starting);
  [self logSessionEvent:active ? @"system_active" : @"system_inactive" details:@{}];
  [self updatePlayback];
}
- (void)updatePlayback {
  const BOOL pause = _pauseState.WantsPause();
  if (pause && _trialAfterOutput) {
    _trialAfterOutput=NO;
    [self logSessionEvent:@"trial_cancel_before_start" details:@{}];
  }
  [self updateTrialDisplayLink];
  if (pause && !_pausedForSystem) [self releaseControls];
  std::lock_guard lock(_runtimeMutex);
  if (!_runtime || !_running || _stopRequested) return;
  const auto state = Core::GetState(Core::System::GetInstance());
  using Pause = SSXSessionPause;
  const auto runtimeState = state == Core::State::Running ? Pause::RuntimeState::Running :
      state == Core::State::Paused ? Pause::RuntimeState::Paused : Pause::RuntimeState::Unavailable;
  const auto action = _pauseState.Reconcile(runtimeState);
  const auto trial = NativeTrial::status.load();
  if (_lastTrialStatus != static_cast<int>(trial)) {
    _lastTrialStatus=static_cast<int>(trial);
    [self logSessionEvent:@"trial_status" details:@{}];
  }
  if (pause && (trial == NativeTrial::Status::Running || trial == NativeTrial::Status::Waiting)) {
      // A checkpoint cannot contain a half-finished injected render: its host
      // return context isn't part of the guest savestate. Cancel, let the CPU
      // reach its idle seam, then pause/save. Input has already been released.
      NativeTrial::Cancel();
      if (!_trialCancellationLogged) {
        _trialCancellationLogged=YES;
        [self logSessionEvent:@"trial_cancel_for_pause" details:@{}];
      }
      // An external pause may already have stopped the CPU inside the extra
      // draw. Briefly run it to the same safe seam before taking a checkpoint.
      if (runtimeState == Pause::RuntimeState::Paused) _runtime->Resume();
      if (_saveBackgroundTask == UIBackgroundTaskInvalid) {
        __weak SSXViewController* weakSelf = self;
        _saveBackgroundTask = [UIApplication.sharedApplication beginBackgroundTaskWithName:@"Finish native trial" expirationHandler:^{
          [weakSelf logSessionEvent:@"trial_background_expired" details:@{}];
          [weakSelf endSaveBackgroundTask];
        }];
      }
      __weak SSXViewController* weakSelf = self;
      dispatch_after(dispatch_time(DISPATCH_TIME_NOW,20*NSEC_PER_MSEC),dispatch_get_main_queue(),^{ [weakSelf updatePlayback]; });
      return;
  }
  if (action == Pause::Action::Pause) {
    [self endSaveBackgroundTask];
    if (_runtime->Pause()) return; // Retry on the next tick if startup is still finishing.
  } else if (action == Pause::Action::Resume) {
    if (_runtime->Resume()) return;
    fprintf(stderr,"[ssx-lifecycle] resumed\n");
    [self logSessionEvent:@"runtime_resumed" details:@{}];
  }
  // This flag accounts for elapsed time only. Runtime state, not ownership of a
  // previous Pause call, determines whether Resume is necessary.
  if (pause && !_pausedForSystem && runtimeState != Pause::RuntimeState::Unavailable) {
    _pausedForSystem = YES;
    _systemPauseStart = CACurrentMediaTime();
    [self savePausedSession];
    fprintf(stderr,"[ssx-lifecycle] paused\n");
    [self logSessionEvent:@"runtime_paused" details:@{}];
    SSXDiagnosticsFlush();
  } else if (!pause && _pausedForSystem && runtimeState != Pause::RuntimeState::Unavailable) {
    const double pauseDuration = CACurrentMediaTime() - _systemPauseStart;
    if (_startTime) _startTime += pauseDuration;
    _launchTime += pauseDuration;
    { std::lock_guard frameLock(_framesMutex); _frames.clear(); _workload={}; _lastFrame = Clock::now(); }
    _pausedForSystem = NO;
    [self logSessionEvent:@"pause_accounted" details:@{@"pause_seconds":@(pauseDuration)}];
  }
  [self refreshSessionMenu];
}
- (void)audioEvent:(NSNotification*)event {
  if (_simulatorNullAudio) return;
  const BOOL interrupted = [event.userInfo[AVAudioSessionInterruptionTypeKey] unsignedIntegerValue] == AVAudioSessionInterruptionTypeBegan;
  // Audio notifications may arrive away from the main queue. Keep all pause
  // intent and UIKit state serialized with application lifecycle callbacks.
  dispatch_async(dispatch_get_main_queue(), ^{
    self->_pauseState.SetAudioInterrupted(interrupted, self->_running || self->_starting);
    [self logSessionEvent:interrupted ? @"audio_interrupted" : @"audio_interruption_ended" details:@{}];
    [self updatePlayback];
  });
}
- (void)logSessionEvent:(NSString*)event details:(NSDictionary*)details {
  NSMutableDictionary* row=[details mutableCopy];
  [row addEntriesFromDictionary:[self outputDetails]];
  row[@"active"]=@(_pauseState.active); row[@"menu"]=@(_pauseState.menu);
  row[@"audioInterrupted"]=@(_pauseState.audio_interrupted);
  row[@"applicationState"]=@(UIApplication.sharedApplication.applicationState);
  row[@"runtimeState"]=@(static_cast<int>(Core::GetState(Core::System::GetInstance())));
  row[@"trialStatus"]=@(static_cast<int>(NativeTrial::status.load()));
  row[@"trialCancel"]=@(NativeTrial::cancel.load()); row[@"trialLimited"]=@(NativeTrial::limited.load());
  row[@"checkpoint"]=_pendingCheckpoint.lastPathComponent ?: @"";
  row[@"active_seconds"]=_startTime ? @(CACurrentMediaTime()-_startTime-(_pausedForSystem ? CACurrentMediaTime()-_systemPauseStart : 0)) : NSNull.null;
  SSXSessionEvent(event,row);
}
@end

// The iOS 26 SDK made UIScene adoption mandatory: UIKit traps in
// _UIApplicationEvaluateRuntimeIssueForNoSceneLifecycleAdoption when an app
// linked against it still builds its window from the app delegate, so the
// window and the active/inactive edges live on a scene delegate instead.
@interface SSXSceneDelegate : UIResponder<UIWindowSceneDelegate>
@property(nonatomic,strong) UIWindow* window;
@end
@implementation SSXSceneDelegate
- (void)scene:(UIScene*)scene willConnectToSession:(UISceneSession*)session options:(UISceneConnectionOptions*)options {
  SSXLaunchTrace(@"scene willConnect enter");
  if (![scene isKindOfClass:UIWindowScene.class]) return;
  self.window=[[UIWindow alloc] initWithWindowScene:(UIWindowScene*)scene];
  self.window.rootViewController=[[SSXViewController alloc] init];
  [self.window makeKeyAndVisible];
}
- (SSXViewController*)controller {
  UIViewController* root=self.window.rootViewController;
  return [root isKindOfClass:SSXViewController.class] ? (SSXViewController*)root : nil;
}
- (void)sceneWillResignActive:(UIScene*)scene { [self.controller systemActive:NO]; }
- (void)sceneDidBecomeActive:(UIScene*)scene { [self.controller systemActive:YES]; }
@end

@interface SSXAppDelegate : UIResponder<UIApplicationDelegate>
@end
@implementation SSXAppDelegate
- (BOOL)application:(UIApplication*)app didFinishLaunchingWithOptions:(NSDictionary*)options {
  SSXLaunchTrace(@"didFinishLaunching enter");
  signal(SIGPIPE,SIG_IGN);
  return YES;
}
@end
int main(int argc,char** argv) {
  @autoreleasepool { return UIApplicationMain(argc,argv,nil,NSStringFromClass(SSXAppDelegate.class)); }
}
