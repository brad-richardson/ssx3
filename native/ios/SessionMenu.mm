#import "SessionMenu.h"

static UILabel* MenuLabel(UIFontTextStyle style, UIColor* color) {
  UILabel* label=[[UILabel alloc] init];
  label.font=[UIFont preferredFontForTextStyle:style];
  label.adjustsFontForContentSizeCategory=YES;
  label.textColor=color;
  label.numberOfLines=0;
  return label;
}

static UIStackView* MenuStack(NSArray<UIView*>* views, UILayoutConstraintAxis axis, CGFloat spacing) {
  UIStackView* stack=[[UIStackView alloc] initWithArrangedSubviews:views];
  stack.axis=axis;
  stack.spacing=spacing;
  return stack;
}

static void SetLabel(UILabel* label, NSString* text) {
  if (![label.text isEqualToString:text]) label.text=text;
  label.hidden=text.length==0;
}

@interface SSXSessionMenu () <UIAdaptivePresentationControllerDelegate> {
  UILabel* _statusLabel;
  UILabel* _resolutionLabel;
  UILabel* _buildLabel;
  UISegmentedControl* _output;
  UISegmentedControl* _detail;
  UISwitch* _fastStart;
  UISwitch* _dualCore;
  UIButton* _resume;
  UIButton* _smoothing;
  UIButton* _reset;
}
@end

@implementation SSXSessionMenu
- (instancetype)init {
  if ((self=[super initWithNibName:nil bundle:nil])) {
    self.modalPresentationStyle=UIModalPresentationOverFullScreen;
    self.modalTransitionStyle=UIModalTransitionStyleCrossDissolve;
    self.modalInPresentation=YES;
    self.overrideUserInterfaceStyle=UIUserInterfaceStyleDark;
  }
  return self;
}

- (void)viewDidLoad {
  [super viewDidLoad];
  self.view.backgroundColor=[UIColor colorWithWhite:0 alpha:0.58];
  self.view.accessibilityViewIsModal=YES;
  self.presentationController.delegate=self;

  UIView* panel=[[UIView alloc] init];
  panel.translatesAutoresizingMaskIntoConstraints=NO;
  panel.backgroundColor=UIColor.secondarySystemBackgroundColor;
  panel.layer.cornerRadius=18;
  panel.layer.cornerCurve=kCACornerCurveContinuous;
  panel.layer.shadowColor=UIColor.blackColor.CGColor;
  panel.layer.shadowOpacity=0.3;
  panel.layer.shadowRadius=24;
  panel.layer.shadowOffset=CGSizeMake(0,8);
  [self.view addSubview:panel];

  UILabel* title=MenuLabel(UIFontTextStyleTitle2,UIColor.labelColor);
  title.text=@"Paused";
  title.accessibilityTraits|=UIAccessibilityTraitHeader;
  _reset=[UIButton buttonWithType:UIButtonTypeSystem];
  [_reset setTitle:@"Full Reset" forState:UIControlStateNormal];
  [_reset setTitleColor:UIColor.systemRedColor forState:UIControlStateNormal];
  _reset.titleLabel.font=[UIFont preferredFontForTextStyle:UIFontTextStyleSubheadline];
  _reset.titleLabel.adjustsFontForContentSizeCategory=YES;
  _reset.accessibilityIdentifier=@"SSX Full Reset";
  [_reset addTarget:self action:@selector(resetPressed) forControlEvents:UIControlEventTouchUpInside];
  [_reset.heightAnchor constraintGreaterThanOrEqualToConstant:44].active=YES;
  [_reset setContentHuggingPriority:UILayoutPriorityRequired forAxis:UILayoutConstraintAxisHorizontal];
  UIStackView* header=MenuStack(@[title,_reset],UILayoutConstraintAxisHorizontal,16);
  header.alignment=UIStackViewAlignmentCenter;

  _statusLabel=MenuLabel(UIFontTextStyleSubheadline,UIColor.labelColor);
  _resolutionLabel=MenuLabel(UIFontTextStyleFootnote,UIColor.secondaryLabelColor);
  _buildLabel=MenuLabel(UIFontTextStyleCaption2,UIColor.tertiaryLabelColor);

  UILabel* outputLabel=MenuLabel(UIFontTextStyleSubheadline,UIColor.labelColor);
  outputLabel.text=@"Output";
  [outputLabel.widthAnchor constraintGreaterThanOrEqualToConstant:66].active=YES;
  [outputLabel setContentHuggingPriority:UILayoutPriorityDefaultHigh forAxis:UILayoutConstraintAxisHorizontal];
  _output=[[UISegmentedControl alloc] initWithItems:@[@"Half",@"75%",@"Full",@"Match"]];
  _output.accessibilityLabel=@"Render output";
  _output.accessibilityIdentifier=@"SSX Render Output";
  [_output addTarget:self action:@selector(outputChanged) forControlEvents:UIControlEventValueChanged];
  UIStackView* outputRow=MenuStack(@[outputLabel,_output],UILayoutConstraintAxisHorizontal,12);
  outputRow.alignment=UIStackViewAlignmentCenter;

  UILabel* detailLabel=MenuLabel(UIFontTextStyleSubheadline,UIColor.labelColor);
  detailLabel.text=@"Detail";
  _detail=[[UISegmentedControl alloc] initWithItems:@[@"1×",@"2×",@"3×",@"4×"]];
  _detail.accessibilityLabel=@"Internal detail";
  _detail.accessibilityIdentifier=@"SSX Internal Detail";
  [_detail.widthAnchor constraintEqualToConstant:200].active=YES;
  [_detail addTarget:self action:@selector(detailChanged) forControlEvents:UIControlEventValueChanged];
  UIView* spacer=[[UIView alloc] init];
  [spacer setContentHuggingPriority:UILayoutPriorityDefaultLow forAxis:UILayoutConstraintAxisHorizontal];
  UILabel* fastLabel=MenuLabel(UIFontTextStyleSubheadline,UIColor.labelColor);
  fastLabel.text=@"Fast start";
  [fastLabel setContentHuggingPriority:UILayoutPriorityRequired forAxis:UILayoutConstraintAxisHorizontal];
  _fastStart=[[UISwitch alloc] init];
  _fastStart.accessibilityLabel=@"Fast start";
  _fastStart.accessibilityIdentifier=@"SSX Fast Start";
  _fastStart.accessibilityHint=@"Skip the intro on the next cold start.";
  [_fastStart addTarget:self action:@selector(fastStartChanged) forControlEvents:UIControlEventValueChanged];
  UIStackView* detailRow=MenuStack(@[detailLabel,_detail,spacer,fastLabel,_fastStart],
                                  UILayoutConstraintAxisHorizontal,12);
  detailRow.alignment=UIStackViewAlignmentCenter;
  UILabel* dualLabel=MenuLabel(UIFontTextStyleSubheadline,UIColor.labelColor);
  dualLabel.text=@"Dual-core";
  [dualLabel setContentHuggingPriority:UILayoutPriorityRequired forAxis:UILayoutConstraintAxisHorizontal];
  _dualCore=[[UISwitch alloc] init];
  _dualCore.accessibilityLabel=@"Dual-core";
  _dualCore.accessibilityIdentifier=@"SSX Dual Core";
  _dualCore.accessibilityHint=@"Run graphics decoding on a second thread. Applies after Full Reset or relaunch.";
  [_dualCore addTarget:self action:@selector(dualCoreChanged) forControlEvents:UIControlEventValueChanged];
  UILabel* dualNote=MenuLabel(UIFontTextStyleFootnote,UIColor.secondaryLabelColor);
  dualNote.text=@"Applies after Full Reset or relaunch";
  UIView* dualSpacer=[[UIView alloc] init];
  [dualSpacer setContentHuggingPriority:UILayoutPriorityDefaultLow forAxis:UILayoutConstraintAxisHorizontal];
  UIStackView* runtimeRow=MenuStack(@[dualLabel,_dualCore,dualNote,dualSpacer],UILayoutConstraintAxisHorizontal,12);
  runtimeRow.alignment=UIStackViewAlignmentCenter;

  UIStackView* content=MenuStack(@[_statusLabel,outputRow,detailRow,runtimeRow,_resolutionLabel,_buildLabel],
                                UILayoutConstraintAxisVertical,12);
  content.translatesAutoresizingMaskIntoConstraints=NO;
  UIScrollView* scroll=[[UIScrollView alloc] init];
  scroll.translatesAutoresizingMaskIntoConstraints=NO;
  scroll.alwaysBounceVertical=NO;
  scroll.showsHorizontalScrollIndicator=NO;
  scroll.contentInsetAdjustmentBehavior=UIScrollViewContentInsetAdjustmentNever;
  [scroll addSubview:content];

  _resume=[UIButton buttonWithType:UIButtonTypeSystem];
  UIButtonConfiguration* resumeConfig=[UIButtonConfiguration filledButtonConfiguration];
  resumeConfig.title=@"Resume";
  resumeConfig.baseBackgroundColor=UIColor.systemBlueColor;
  resumeConfig.cornerStyle=UIButtonConfigurationCornerStyleMedium;
  _resume.configuration=resumeConfig;
  _resume.accessibilityIdentifier=@"SSX Resume";
  [_resume addTarget:self action:@selector(resumePressed) forControlEvents:UIControlEventTouchUpInside];

  _smoothing=[UIButton buttonWithType:UIButtonTypeSystem];
  UIButtonConfiguration* smoothingConfig=[UIButtonConfiguration tintedButtonConfiguration];
  smoothingConfig.title=@"Try smoothing";
  smoothingConfig.subtitle=@"Up to 35 seconds";
  smoothingConfig.baseForegroundColor=UIColor.labelColor;
  smoothingConfig.cornerStyle=UIButtonConfigurationCornerStyleMedium;
  _smoothing.configuration=smoothingConfig;
  _smoothing.accessibilityIdentifier=@"SSX Try Smoothing";
  [_smoothing addTarget:self action:@selector(smoothingPressed) forControlEvents:UIControlEventTouchUpInside];
  UIStackView* actions=MenuStack(@[_smoothing,_resume],UILayoutConstraintAxisHorizontal,12);
  actions.distribution=UIStackViewDistributionFillEqually;
  [actions.heightAnchor constraintGreaterThanOrEqualToConstant:48].active=YES;

  UIStackView* layout=MenuStack(@[header,scroll,actions],UILayoutConstraintAxisVertical,12);
  layout.translatesAutoresizingMaskIntoConstraints=NO;
  [panel addSubview:layout];
  UILayoutGuide* safe=self.view.safeAreaLayoutGuide;
  NSLayoutConstraint* width=[panel.widthAnchor constraintEqualToAnchor:safe.widthAnchor constant:-28];
  width.priority=UILayoutPriorityDefaultHigh;
  NSLayoutConstraint* height=[panel.heightAnchor constraintEqualToConstant:412];
  height.priority=UILayoutPriorityDefaultHigh;
  [NSLayoutConstraint activateConstraints:@[
    // Cross-row constraints require the completed common content hierarchy.
    [detailLabel.widthAnchor constraintEqualToAnchor:outputLabel.widthAnchor],
    width,height,
    [panel.widthAnchor constraintLessThanOrEqualToConstant:820],
    [panel.leadingAnchor constraintGreaterThanOrEqualToAnchor:safe.leadingAnchor constant:14],
    [panel.trailingAnchor constraintLessThanOrEqualToAnchor:safe.trailingAnchor constant:-14],
    [panel.topAnchor constraintGreaterThanOrEqualToAnchor:safe.topAnchor constant:12],
    [panel.bottomAnchor constraintLessThanOrEqualToAnchor:safe.bottomAnchor constant:-12],
    [panel.centerXAnchor constraintEqualToAnchor:safe.centerXAnchor],
    [panel.centerYAnchor constraintEqualToAnchor:safe.centerYAnchor],
    [layout.leadingAnchor constraintEqualToAnchor:panel.leadingAnchor constant:18],
    [layout.trailingAnchor constraintEqualToAnchor:panel.trailingAnchor constant:-18],
    [layout.topAnchor constraintEqualToAnchor:panel.topAnchor constant:10],
    [layout.bottomAnchor constraintEqualToAnchor:panel.bottomAnchor constant:-16],
    [scroll.heightAnchor constraintGreaterThanOrEqualToConstant:40],
    [content.leadingAnchor constraintEqualToAnchor:scroll.contentLayoutGuide.leadingAnchor],
    [content.trailingAnchor constraintEqualToAnchor:scroll.contentLayoutGuide.trailingAnchor],
    [content.topAnchor constraintEqualToAnchor:scroll.contentLayoutGuide.topAnchor],
    [content.bottomAnchor constraintEqualToAnchor:scroll.contentLayoutGuide.bottomAnchor],
    [content.widthAnchor constraintEqualToAnchor:scroll.frameLayoutGuide.widthAnchor],
  ]];
}

- (BOOL)presentationControllerShouldDismiss:(UIPresentationController*)presentationController {
  return NO;
}
- (BOOL)accessibilityPerformEscape {
  // VoiceOver escape is an explicit Resume, never an untracked dismissal.
  if (!self.onResume) return NO;
  self.onResume();
  return YES;
}
- (void)resumePressed { if (self.onResume) self.onResume(); }
- (void)smoothingPressed { if (self.onSmoothing) self.onSmoothing(); }
- (void)resetPressed { if (self.onReset) self.onReset(); }
- (void)outputChanged {
  NSArray<NSString*>* modes=@[@"half",@"three-quarter",@"full",@"match-internal"];
  NSInteger index=_output.selectedSegmentIndex;
  if (index>=0 && index<(NSInteger)modes.count && self.onOutput) self.onOutput(modes[index]);
}
- (void)detailChanged {
  NSInteger index=_detail.selectedSegmentIndex;
  if (index>=0 && index<4 && self.onInternal) self.onInternal(index+1);
}
- (void)fastStartChanged { if (self.onFastStart) self.onFastStart(_fastStart.on); }
- (void)dualCoreChanged { if (self.onDualCore) self.onDualCore(_dualCore.on); }

- (void)updateWithStatus:(NSString*)status outputMode:(NSString*)mode internalScale:(NSInteger)scale
             resolution:(NSString*)resolution fastStart:(BOOL)fastStart dualCore:(BOOL)dualCore
           canConfigure:(BOOL)canConfigure
               canTrial:(BOOL)canTrial canReset:(BOOL)canReset build:(NSString*)build {
  NSAssert(NSThread.isMainThread,@"Session menu updates require the main thread");
  [self loadViewIfNeeded];
  SetLabel(_statusLabel,status);
  SetLabel(_resolutionLabel,resolution);
  SetLabel(_buildLabel,build);
  NSUInteger outputIndex=[@[@"half",@"three-quarter",@"full",@"match-internal"] indexOfObject:mode];
  NSInteger selected=outputIndex==NSNotFound ? UISegmentedControlNoSegment : (NSInteger)outputIndex;
  if (!_output.tracking && _output.selectedSegmentIndex!=selected) _output.selectedSegmentIndex=selected;
  selected=(scale>=1 && scale<=4) ? scale-1 : UISegmentedControlNoSegment;
  if (!_detail.tracking && _detail.selectedSegmentIndex!=selected) _detail.selectedSegmentIndex=selected;
  if (!_fastStart.tracking && _fastStart.on!=fastStart) [_fastStart setOn:fastStart animated:NO];
  if (!_dualCore.tracking && _dualCore.on!=dualCore) [_dualCore setOn:dualCore animated:NO];
  _output.enabled=canConfigure;
  _detail.enabled=canConfigure;
  _fastStart.enabled=canConfigure;
  _dualCore.enabled=canConfigure;
  _smoothing.enabled=canTrial;
  _reset.enabled=canReset;
}
@end
