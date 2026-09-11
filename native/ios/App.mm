// SSX development frontend. Runtime integration follows SunPad's Apple host;
// see native/ios/README.md for attribution and the validation boundary.
#import <UIKit/UIKit.h>
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
#include "moderngekko/runtime.hpp"
#include "GrabMap.h"
#include "Common/HookableEvent.h"
#include "Common/Logging/Log.h"
#include "AudioCommon/Mixer.h"
#include "Core/Core.h"
#include "Core/System.h"
#include "VideoCommon/PerformanceMetrics.h"
#include "VideoCommon/VideoEvents.h"

extern "C" const ModernGekkoModuleDesc* staticrecomp_get_module();
using Clock = std::chrono::steady_clock;

static NSString* Documents() {
  return NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES).firstObject;
}
static void WriteText(NSString* path, NSString* text) {
  [text writeToFile:path atomically:YES encoding:NSUTF8StringEncoding error:nil];
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
  UIButton* _stop;
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
  std::atomic<bool> _running;
  std::atomic<bool> _starting;
  std::atomic<bool> _stopRequested;
  Common::EventHook _frameHook;
  Clock::time_point _lastFrame;
  double _startTime;
  double _launchTime;
  double _systemPauseStart;
  double _lastMetric;
  double _lastCapture;
  double _duration;
  NSArray<NSDictionary*>* _sequence;
  NSUInteger _eventIndex;
  BOOL _active;
  BOOL _audioInterrupted;
  BOOL _pausedForSystem;
  int _pipe;
}
- (void)systemActive:(BOOL)active;
@end

@implementation SSXViewController
- (void)viewDidLoad {
  [super viewDidLoad];
  _pipe = -1;
  _active = YES;
  _controls = [NSMutableArray array];
  _pressed = [NSMutableSet set];
  _padButtons = [NSSet set];
  _touchDpad = [NSSet set];
  _overlayAlpha = 1;
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
  _stop = [UIButton buttonWithType:UIButtonTypeSystem];
  [_stop setTitle:@"Stop" forState:UIControlStateNormal];
  _stop.accessibilityLabel = @"SSX Stop";
  [_stop addTarget:self action:@selector(stopGame) forControlEvents:UIControlEventTouchUpInside];
  [self.view addSubview:_stop];
  [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(audioEvent:)
      name:AVAudioSessionInterruptionNotification object:nil];
  [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(controllersChanged:)
      name:GCControllerDidConnectNotification object:nil];
  [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(controllersChanged:)
      name:GCControllerDidDisconnectNotification object:nil];
  [self controllersChanged:nil];
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
  layer.contentsScale = self.view.window.screen.scale;
  layer.drawableSize = CGSizeMake(bounds.size.width * layer.contentsScale, bounds.size.height * layer.contentsScale);
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
  _stop.frame = CGRectMake(bounds.size.width-safe.right-70, top, 60, 32);
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
  NSString* game = [Documents() stringByAppendingPathComponent:@"Game"];
  if (![[NSFileManager defaultManager] fileExistsAtPath:[game stringByAppendingPathComponent:@"sys/main.dol"]] ||
      ![[NSFileManager defaultManager] fileExistsAtPath:[game stringByAppendingPathComponent:@"files/opening.bnr"]]) {
    _status.text = @"Game data isn't installed yet. Finish setup, then relaunch.";
    return;
  }
  _starting = true;
  _launchTime = CACurrentMediaTime();
  _stopRequested = false;
  NSString* user = [Documents() stringByAppendingPathComponent:@"User"];
  NSString* config = [user stringByAppendingPathComponent:@"Config"];
  NSString* pipes = [user stringByAppendingPathComponent:@"Pipes"];
  NSString* stamp = [NSString stringWithFormat:@"%.0f",NSDate.date.timeIntervalSince1970];
  _report = [[Documents() stringByAppendingPathComponent:@"Reports"] stringByAppendingPathComponent:stamp];
  for (NSString* path in @[config,pipes,_report])
    [[NSFileManager defaultManager] createDirectoryAtPath:path withIntermediateDirectories:YES attributes:nil error:nil];
  freopen([[_report stringByAppendingPathComponent:@"runtime.log"] fileSystemRepresentation], "a", stderr);
  setvbuf(stderr, nullptr, _IOLBF, 0);
  for (NSString* name in @[@"metrics.jsonl",@"input.jsonl"])
    [[NSFileManager defaultManager] createFileAtPath:[_report stringByAppendingPathComponent:name] contents:nil attributes:nil];
  _metricsFile = [NSFileHandle fileHandleForWritingAtPath:[_report stringByAppendingPathComponent:@"metrics.jsonl"]];
  _inputFile = [NSFileHandle fileHandleForWritingAtPath:[_report stringByAppendingPathComponent:@"input.jsonl"]];
  WriteText([config stringByAppendingPathComponent:@"Dolphin.ini"],
    @"[Core]\nCPUThread = False\nDSPHLE = True\nSkipIPL = True\nLargeEntryPointsMap = False\n[DSP]\nEnableJIT = False\nBackend = CoreAudio\n[Interface]\nConfirmStop = False\n");
  NSMutableString* mapping = [NSMutableString stringWithString:@"[GCPad1]\nDevice = Pipe/0/ssx3\nOptions/Always Connected = True\n"];
  for (NSString* key in @[@"A",@"B",@"X",@"Y",@"Z",@"Start"])
    [mapping appendFormat:@"Buttons/%@ = `Button %@`\n",key,key.uppercaseString];
  [mapping appendString:@"Main Stick/Up = `Axis MAIN Y +`\nMain Stick/Down = `Axis MAIN Y -`\nMain Stick/Left = `Axis MAIN X -`\nMain Stick/Right = `Axis MAIN X +`\nMain Stick/Calibration = 100.00\n"];
  [mapping appendString:@"C-Stick/Up = `Axis C Y +`\nC-Stick/Down = `Axis C Y -`\nC-Stick/Left = `Axis C X -`\nC-Stick/Right = `Axis C X +`\nC-Stick/Calibration = 100.00\n"];
  [mapping appendString:@"D-Pad/Up = `Button D_UP`\nD-Pad/Down = `Button D_DOWN`\nD-Pad/Left = `Button D_LEFT`\nD-Pad/Right = `Button D_RIGHT`\nTriggers/L = `Button L`\nTriggers/R = `Button R`\n"];
  WriteText([config stringByAppendingPathComponent:@"GCPadNew.ini"],mapping);
  NSString* fifo = [pipes stringByAppendingPathComponent:@"ssx3"];
  if (mkfifo(fifo.fileSystemRepresentation,0600) != 0 && errno != EEXIST) {
    _status.text = @"Could not create controller pipe"; _starting=false; return;
  }
  NSError* audioError;
  [AVAudioSession.sharedInstance setCategory:AVAudioSessionCategoryPlayback error:&audioError];
  [AVAudioSession.sharedInstance setPreferredIOBufferDuration:0.01 error:&audioError];
  [AVAudioSession.sharedInstance setActive:YES error:&audioError];
  if (audioError) fprintf(stderr,"[ssx-audio] %s\n",audioError.description.UTF8String);
  UIApplication.sharedApplication.idleTimerDisabled = YES;
  setenv("STATICRECOMP_NO_JIT","1",1);
  setenv("SSX3_NO_EXECUTABLE_MEMORY","1",1);
  setenv("STATICRECOMP_DISPATCH_SAMPLES","1",1);
  Common::Log::SetEmbedderLogCallback(RuntimeLog,nullptr);
  NSArray* args = NSProcessInfo.processInfo.arguments;
  if ([args containsObject:@"-ssxAutoTest"]) {
    NSString* sequencePath = [Documents() stringByAppendingPathComponent:@"test-sequence.json"];
    NSData* data = [NSData dataWithContentsOfFile:sequencePath];
    NSDictionary* test = data ? [NSJSONSerialization JSONObjectWithData:data options:0 error:nil] : nil;
    _sequence = test[@"events"] ?: @[];
    _duration = [test[@"duration"] doubleValue];
    fprintf(stderr,"[ssx-test] events=%lu duration=%.1f\n",(unsigned long)_sequence.count,_duration);
  }
  const auto* descriptor = staticrecomp_get_module();
  NSDictionary* metadata = @{@"disc":@"GXBE69", @"moduleABI":@(descriptor->abi_version),
    @"os":UIDevice.currentDevice.systemVersion, @"device":UIDevice.currentDevice.model,
    @"simulator":@(TARGET_OS_SIMULATOR), @"metalDevice":((CAMetalLayer*)_surface.layer).device.name ?: @"unknown",
    @"cpuJIT":@NO, @"executableAllocationGuard":@YES, @"vertexLoader":@"software",
    @"renderScale":@1, @"cpuThread":@NO, @"automated":@(_sequence!=nil)};
  [[NSJSONSerialization dataWithJSONObject:metadata options:NSJSONWritingPrettyPrinted error:nil]
    writeToFile:[_report stringByAppendingPathComponent:@"launch.json"] atomically:YES];
  std::thread([self,game,user,descriptor] {
    @autoreleasepool {
      moderngekko::RuntimeConfig options;
      options.game_root = game.fileSystemRepresentation;
      options.user_directory = user.fileSystemRepresentation;
      options.module = moderngekko::ModuleSource::AttachedDescriptor(descriptor);
      options.graphics.backend = "Metal";
      options.graphics.internal_resolution_scale = 1;
      options.audio.backend = "CoreAudio";
      options.input.background_input = true;
      options.show_fps_in_title = false;
      options.render_surface = (__bridge void*)self->_surface.layer;
      auto created = moderngekko::Runtime::Create(std::move(options));
      if (!created) {
        fprintf(stderr,"[ssx-app] create failed: %s\n",created.error->message.c_str());
        NSString* error = @(created.error->message.c_str());
        self->_starting=false;
        dispatch_async(dispatch_get_main_queue(), ^{ self->_status.text=error; });
        return;
      }
      {
        std::lock_guard lock(self->_runtimeMutex);
        self->_runtime = created.runtime.get();
      }
      self->_lastFrame = Clock::now();
      self->_frameHook = GetVideoEvents().after_frame_event.Register([self](Core::System&) {
        const auto now = Clock::now();
        std::lock_guard lock(self->_framesMutex);
        if (self->_frames.size()<10000)
          self->_frames.push_back(std::chrono::duration<double,std::milli>(now-self->_lastFrame).count());
        self->_lastFrame=now;
      });
      self->_running=true; self->_starting=false;
      auto result = self->_stopRequested ? moderngekko::RuntimeRunResult{} : created.runtime->Run();
      self->_running=false;
      self->_frameHook={};
      {
        std::lock_guard lock(self->_runtimeMutex);
        self->_runtime=nullptr;
      }
      fprintf(stderr,"[ssx-app] stopped error=%d\n",bool(result.error));
      dispatch_async(dispatch_get_main_queue(), ^{
        [self releaseControls];
        if (self->_pipe>=0) { close(self->_pipe); self->_pipe=-1; }
        self->_status.text = result.error ? @"Runtime stopped with an error; see Reports." : @"Stopped. Relaunch to ride again.";
        UIApplication.sharedApplication.idleTimerDisabled=NO;
        [self->_metricsFile synchronizeFile]; [self->_inputFile synchronizeFile];
      });
    }
  }).detach();
}
- (void)tick {
  if (_duration>0 && (_starting||_running) && CACurrentMediaTime()-_launchTime>_duration+120) {
    fprintf(stderr,"[ssx-test] wall-clock deadline reached\n");
    [self stopGame]; return;
  }
  if (!_running) return;
  if (_pipe<0) _pipe=open([[Documents() stringByAppendingPathComponent:@"User/Pipes/ssx3"] fileSystemRepresentation],O_WRONLY|O_NONBLOCK);
  if (Core::GetState(Core::System::GetInstance()) != Core::State::Running) return;
  if (!_startTime) {
    _startTime=CACurrentMediaTime();
    fprintf(stderr,"[ssx-app] running startup_seconds=%.3f\n",_startTime-_launchTime);
  }
  const double elapsed=CACurrentMediaTime()-_startTime;
  if (!_active || _audioInterrupted) { [self systemActive:_active]; return; }
  if (_pipe<0) return;
  while (_eventIndex<_sequence.count && [_sequence[_eventIndex][@"at"] doubleValue]<=elapsed) {
    [self send:_sequence[_eventIndex][@"commands"]]; ++_eventIndex;
  }
  if (elapsed-_lastMetric>=1) {
    _lastMetric=elapsed;
    std::vector<double> frames;
    { std::lock_guard lock(_framesMutex); frames.swap(_frames); }
    std::sort(frames.begin(),frames.end());
    const auto quantile=[&](double q){ return frames.empty()?0.0:frames[std::min(frames.size()-1,size_t(q*(frames.size()-1)))]; };
    task_vm_info_data_t vm={}; mach_msg_type_number_t count=TASK_VM_INFO_COUNT;
    task_info(mach_task_self(),TASK_VM_INFO,(task_info_t)&vm,&count);
    const auto& perf=Core::System::GetInstance().GetPerfMetrics();
    NSDictionary* row=@{@"seconds":@(elapsed),@"fps":@(perf.GetFPS()),@"vps":@(perf.GetVPS()),
      @"speed":@(perf.GetSpeed()),@"frameIntervalP50ms":@(quantile(.5)),@"frameIntervalP95ms":@(quantile(.95)),
      @"frameIntervalP99ms":@(quantile(.99)),@"frames":@(frames.size()),@"footprintBytes":@(vm.phys_footprint),
      @"thermalState":@(NSProcessInfo.processInfo.thermalState),@"eventIndex":@(_eventIndex),
      @"audioDMAEmptyDequeues":@(Mixer::GetDMAEmptyDequeues())};
    [_metricsFile writeData:[NSJSONSerialization dataWithJSONObject:row options:0 error:nil]];
    [_metricsFile writeData:[@"\n" dataUsingEncoding:NSUTF8StringEncoding]];
    _status.text=[NSString stringWithFormat:@"SSX 3 · %.1f FPS · %.0f%% speed · %.0f MB",perf.GetFPS(),perf.GetSpeed()*100,vm.phys_footprint/1048576.0];
  }
  if (_sequence && elapsed-_lastCapture>=15) { _lastCapture=elapsed; Core::SaveScreenShot(); }
  if (_duration>0 && elapsed>=_duration) [self stopGame];
}
- (void)stopGame {
  [self releaseControls]; _stopRequested=true;
  std::lock_guard lock(_runtimeMutex);
  if (_runtime) _runtime->RequestStop();
}
- (void)systemActive:(BOOL)active {
  _active=active;
  const BOOL pause=!active||_audioInterrupted;
  if (pause) [self releaseControls];
  std::lock_guard lock(_runtimeMutex);
  if (!_runtime || !_running) return;
  const auto state=Core::GetState(Core::System::GetInstance());
  if (pause && state==Core::State::Running) {
    _runtime->Pause(); _pausedForSystem=YES; _systemPauseStart=CACurrentMediaTime();
    fprintf(stderr,"[ssx-lifecycle] paused\n");
  }
  else if (!pause && _pausedForSystem && state==Core::State::Paused) {
    [AVAudioSession.sharedInstance setActive:YES error:nil];
    const double pauseDuration=CACurrentMediaTime()-_systemPauseStart;
    if (_startTime) _startTime+=pauseDuration;
    _launchTime+=pauseDuration;
    { std::lock_guard frameLock(_framesMutex); _frames.clear(); _lastFrame=Clock::now(); }
    _runtime->Resume(); _pausedForSystem=NO;
    fprintf(stderr,"[ssx-lifecycle] resumed after %.3f seconds\n",pauseDuration);
  }
}
- (void)audioEvent:(NSNotification*)event {
  _audioInterrupted=[event.userInfo[AVAudioSessionInterruptionTypeKey] unsignedIntegerValue]==AVAudioSessionInterruptionTypeBegan;
  [self systemActive:_active];
}
@end

@interface SSXAppDelegate : UIResponder<UIApplicationDelegate>
@property(nonatomic,strong) UIWindow* window;
@end
@implementation SSXAppDelegate
- (BOOL)application:(UIApplication*)app didFinishLaunchingWithOptions:(NSDictionary*)options {
  signal(SIGPIPE,SIG_IGN);
  self.window=[[UIWindow alloc] initWithFrame:UIScreen.mainScreen.bounds];
  self.window.rootViewController=[[SSXViewController alloc] init];
  [self.window makeKeyAndVisible]; return YES;
}
- (void)applicationWillResignActive:(UIApplication*)app { [(SSXViewController*)self.window.rootViewController systemActive:NO]; }
- (void)applicationDidBecomeActive:(UIApplication*)app { [(SSXViewController*)self.window.rootViewController systemActive:YES]; }
@end
int main(int argc,char** argv) {
  @autoreleasepool { return UIApplicationMain(argc,argv,nil,NSStringFromClass(SSXAppDelegate.class)); }
}
