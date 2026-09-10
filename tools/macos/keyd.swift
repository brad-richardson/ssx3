import AppKit
import CoreGraphics
// Key daemon: reads lines "down KEY" / "up KEY" / "tap KEY" / "quit" from stdin and posts them to PCSX2.
let matches = NSWorkspace.shared.runningApplications.filter { $0.localizedName == "PCSX2" }
guard matches.count == 1 else { fatalError("Expected one PCSX2 instance") }
let app = matches[0]
app.activate(options: [])
usleep(200000)
setbuf(stdout, nil)
func post(_ key: UInt16, _ down: Bool) {
    CGEvent(keyboardEventSource: nil, virtualKey: key, keyDown: down)?.postToPid(app.processIdentifier)
}
while let line = readLine() {
    let parts = line.split(separator: " ")
    if parts.isEmpty { continue }
    if parts[0] == "quit" { break }
    guard parts.count == 2, let key = UInt16(parts[1]) else { print("bad"); continue }
    switch parts[0] {
    case "down": post(key, true)
    case "up": post(key, false)
    case "tap": post(key, true); usleep(120000); post(key, false)
    default: print("bad")
    }
    print("ok")
}
