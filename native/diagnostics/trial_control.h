// Frontend controls for a bounded native trial. Atomics carry requests
// to the CPU thread; only that thread owns the game adapter and pose history.
// Smoothing trials inject extra renders with interpolated poses; F trials
// double the update cadence with halved dt and render normally (route F).
#pragma once
#include <atomic>
#include <string>
namespace NativeTrial {
enum class Status { Idle, Waiting, Running, Finished, Unavailable };
enum class Kind { Smoothing, F };
inline std::atomic<Status> status{Status::Idle};
inline std::atomic<Kind> kind{Kind::Smoothing};
inline std::atomic<bool> cancel{false};
inline std::atomic<bool> limited{false};
inline std::atomic<unsigned> frames{0}, extras{0}, updates_doubled{0};
inline std::string log_path; // set only while the runtime is stopped
inline double ends=0;       // CPU thread only
inline void Request() { cancel=false; limited=false; frames=0; extras=0; updates_doubled=0; kind=Kind::Smoothing; status=Status::Waiting; }
inline void RequestF() { cancel=false; limited=false; frames=0; extras=0; updates_doubled=0; kind=Kind::F; status=Status::Waiting; }
inline void Cancel() { cancel=true; }
inline bool Active(double now) {
 return status.load()==Status::Running && !cancel.load() && now<ends;
}
}
#ifdef SSX_NATIVE_TRIAL_APP
// Call while the old runtime has stopped, before constructing the next one.
extern "C" void SSXResetNativeTrial(const char* log_path);
#endif
