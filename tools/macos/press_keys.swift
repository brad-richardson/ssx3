import AppKit
import CoreGraphics
let matches = NSWorkspace.shared.runningApplications.filter { $0.localizedName == "PCSX2" }
guard matches.count == 1 else { fatalError("Expected one PCSX2 instance") }
let app = matches[0]
app.activate(options: [])
usleep(300000)
for arg in CommandLine.arguments.dropFirst() {
    guard let key = UInt16(arg) else { fatalError("Expected key code") }
    CGEvent(keyboardEventSource: nil, virtualKey: key, keyDown: true)?.postToPid(app.processIdentifier)
    usleep(250000)
    CGEvent(keyboardEventSource: nil, virtualKey: key, keyDown: false)?.postToPid(app.processIdentifier)
    usleep(750000)
}
