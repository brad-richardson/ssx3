// Send an actual mouse-down/up pair to a named SSX control in our Simulator.
// The Simulator converts this to touch input, exercising UIControl handlers.
// Requires existing macOS accessibility permission; never requests it.
import AppKit
import ApplicationServices
import Foundation

func attribute(_ element: AXUIElement, _ key: String) -> CFTypeRef? {
    var result: CFTypeRef?
    AXUIElementCopyAttributeValue(element, key as CFString, &result)
    return result
}
func text(_ element: AXUIElement, _ key: String) -> String {
    attribute(element, key) as? String ?? ""
}
func find(_ element: AXUIElement, label: String, depth: Int = 0) -> AXUIElement? {
    if depth > 8 { return nil }
    if text(element, kAXRoleAttribute) == kAXButtonRole &&
        (text(element, kAXDescriptionAttribute) == label || text(element, kAXTitleAttribute) == label) {
        return element
    }
    for child in (attribute(element, kAXChildrenAttribute) as? [AXUIElement] ?? []).prefix(100) {
        if let result = find(child, label: label, depth: depth + 1) { return result }
    }
    return nil
}
let args = CommandLine.arguments
guard args.count == 3 || args.count == 5, args[1].hasPrefix("SSX "),
      let duration = Double(args[2]), duration.isFinite, duration >= 0.05, duration <= 5,
      let dragX = Double(args.count == 5 ? args[3] : "0"), let dragY = Double(args.count == 5 ? args[4] : "0"),
      abs(dragX) <= 120, abs(dragY) <= 120 else {
    fputs("usage: simulator_touch 'SSX Start' <hold-seconds, 0.05...5> [drag-dx drag-dy, screen points]\n", stderr)
    exit(2)
}
guard AXIsProcessTrusted() else {
    fputs("Existing accessibility permission is required.\n", stderr); exit(1)
}
guard let simulator = NSRunningApplication.runningApplications(withBundleIdentifier: "com.apple.iphonesimulator").first else {
    fputs("Simulator is not running.\n", stderr); exit(1)
}
let app = AXUIElementCreateApplication(simulator.processIdentifier)
let windows = attribute(app, kAXWindowsAttribute) as? [AXUIElement] ?? []
guard let window = windows.first(where: { text($0, kAXTitleAttribute).hasPrefix("SSX Native Test –") }),
      let button = find(window, label: args[1]),
      let rawPosition = attribute(button, kAXPositionAttribute),
      let rawSize = attribute(button, kAXSizeAttribute) else {
    fputs("Named SSX control is not visible in the dedicated test simulator.\n", stderr); exit(1)
}
var position = CGPoint.zero
var size = CGSize.zero
guard AXValueGetValue(rawPosition as! AXValue, .cgPoint, &position),
      AXValueGetValue(rawSize as! AXValue, .cgSize, &size), size.width > 0, size.height > 0 else {
    fputs("Control has no usable screen bounds.\n", stderr); exit(1)
}
func bounds(_ element: AXUIElement) -> CGRect? {
    guard let p = attribute(element, kAXPositionAttribute),
          let s = attribute(element, kAXSizeAttribute) else { return nil }
    var origin = CGPoint.zero, dimensions = CGSize.zero
    guard AXValueGetValue(p as! AXValue, .cgPoint, &origin),
          AXValueGetValue(s as! AXValue, .cgSize, &dimensions) else { return nil }
    return CGRect(origin: origin, size: dimensions)
}
guard let display = (attribute(window, kAXChildrenAttribute) as? [AXUIElement] ?? []).first(where: {
    text($0, kAXRoleAttribute) == kAXGroupRole && find($0, label: args[1]) != nil
}), let viewport = bounds(display), viewport.width > viewport.height else {
    fputs("Rotate the dedicated simulator window to landscape first.\n", stderr); exit(1)
}
var center = CGPoint(x: position.x + size.width / 2, y: position.y + size.height / 2)
// iOS 26's legacy-app accessibility bridge can apply the landscape transform
// twice. Detect this using A (which should be on the right), then undo the
// extra rotation for all controls. Never click outside the simulator display.
if let a = find(display, label: "SSX A"), let aBounds = bounds(a),
   !viewport.contains(CGPoint(x: aBounds.midX, y: aBounds.midY)) {
    center = CGPoint(x: viewport.minX + center.y - viewport.minY,
                     y: viewport.minY + viewport.width - (center.x - viewport.minX))
}
guard viewport.contains(center) else {
    fputs("Control coordinates fall outside the simulator display.\n", stderr); exit(1)
}
simulator.activate(options: [])
AXUIElementPerformAction(window, kAXRaiseAction as CFString)
Thread.sleep(forTimeInterval: 0.15)
let source = CGEventSource(stateID: .hidSystemState)
CGEvent(mouseEventSource: source, mouseType: .leftMouseDown, mouseCursorPosition: center,
        mouseButton: .left)?.post(tap: .cghidEventTap)
var end = center
if dragX != 0 || dragY != 0 {
    // Drag in a few steps so the app sees intermediate touchesMoved events.
    for step in 1...8 {
        end = CGPoint(x: center.x + dragX * Double(step) / 8, y: center.y + dragY * Double(step) / 8)
        Thread.sleep(forTimeInterval: 0.03)
        CGEvent(mouseEventSource: source, mouseType: .leftMouseDragged, mouseCursorPosition: end,
                mouseButton: .left)?.post(tap: .cghidEventTap)
    }
}
Thread.sleep(forTimeInterval: duration)
CGEvent(mouseEventSource: source, mouseType: .leftMouseUp, mouseCursorPosition: end,
        mouseButton: .left)?.post(tap: .cghidEventTap)
print("Touched \(args[1]) for \(duration)s at \(center.x),\(center.y) released at \(end.x),\(end.y)")
