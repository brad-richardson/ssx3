// I26: click (= a touch in the iOS Simulator) at a point given as fractions
// of the Simulator device window's content, e.g. `swift simtap.swift 0.9 0.8 0.25`
// (x, y, hold seconds). Prints the window bounds it used. Needs the Simulator
// window on screen; posting needs Accessibility permission for the caller.
import CoreGraphics
import Foundation

let args = CommandLine.arguments
let fx = Double(args[1])!, fy = Double(args[2])!
let hold = args.count > 3 ? Double(args[3])! : 0.2
let list = CGWindowListCopyWindowInfo([.optionOnScreenOnly], kCGNullWindowID) as! [[String: Any]]
guard let w = list.first(where: { ($0[kCGWindowOwnerName as String] as? String) == "Simulator" && (($0[kCGWindowLayer as String] as? Int) ?? 1) == 0 }),
      let b = w[kCGWindowBounds as String] as? [String: Double] else {
    print("no Simulator window"); exit(2)
}
let x = b["X"]!, y = b["Y"]!, width = b["Width"]!, height = b["Height"]!
print("window x=\(x) y=\(y) w=\(width) h=\(height) name=\(w[kCGWindowName as String] ?? "")")
let p = CGPoint(x: x + fx * width, y: y + fy * height)
CGEvent(mouseEventSource: nil, mouseType: .leftMouseDown, mouseCursorPosition: p, mouseButton: .left)!.post(tap: .cghidEventTap)
usleep(useconds_t(hold * 1_000_000))
CGEvent(mouseEventSource: nil, mouseType: .leftMouseUp, mouseCursorPosition: p, mouseButton: .left)!.post(tap: .cghidEventTap)
print("tapped \(p)")
