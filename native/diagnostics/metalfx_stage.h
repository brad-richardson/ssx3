// Prototype MetalFX interpolation stage: PRESENT but BYPASSED until motion exists.
//
// MF2 wires the option plumbing (launch flag -> app config -> this switch) with
// no interpolator instance and no frame effect. The frontend sets `enabled` once
// from its launch flag and calls NotePresentBypassed() at the frame boundary;
// every call is a counted no-op. MF3 owns the real MTLFXFrameInterpolator
// insertion (pre-present, in the DiagnosticMTLGfx.mm local source copy) and the
// motion-vector source. No trial state is touched.
#pragma once
#include <atomic>
namespace NativeMetalFX {
inline std::atomic<bool> enabled{false};
inline std::atomic<unsigned long long> bypassed{0};
inline std::atomic<bool> announced{false};
// Count one bypassed present. Returns true exactly once per process (the first
// bypassed present) so the frontend logs a single stage event, not one per frame.
inline bool NotePresentBypassed() {
 bypassed.fetch_add(1);
 return !announced.exchange(true);
}
}
