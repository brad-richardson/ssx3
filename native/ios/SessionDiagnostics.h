#pragma once
#include <cstdint>

// Called by the iOS-only source copies of Dolphin's state/Metal adapters.
// Never changes guest state, rendering configuration, or save outcomes.
void SSXCheckpointStage(const char* stage, const char* path, std::uint64_t bytes, int error);
void SSXRecompSample(std::uint64_t ticks, std::uint64_t native, std::uint64_t fallback,
                    std::uint64_t jit, std::uint64_t exceptions, std::uint64_t hle_returns,
                    std::uint64_t hle_vectors, std::uint64_t hle_rejects);

#ifdef __OBJC__
#import <Foundation/Foundation.h>
#import <Metal/Metal.h>
#import <QuartzCore/CAMetalLayer.h>

void SSXDiagnosticsBegin(NSString* report);
void SSXDiagnosticsFlush();
void SSXDiagnosticsEnd();
void SSXSessionEvent(NSString* event, NSDictionary* details);
void SSXDrawableAcquired(double start, bool acquired);
void SSXDrawableSubmitted(id<CAMetalDrawable> drawable, id<MTLCommandBuffer> buffer);
#endif
