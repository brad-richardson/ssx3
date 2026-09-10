import CoreGraphics
import Foundation
let list = CGWindowListCopyWindowInfo([.optionOnScreenOnly, .excludeDesktopElements], kCGNullWindowID) as! [[String: Any]]
var best: (Int, Double) = (0, 0)
for w in list where (w["kCGWindowOwnerName"] as? String) == "PCSX2" {
    let b = w["kCGWindowBounds"] as! [String: Double]
    let area = b["Width"]! * b["Height"]!
    if area > best.1 { best = (w["kCGWindowNumber"] as! Int, area) }
}
if best.0 == 0 { exit(1) }
print(best.0)
