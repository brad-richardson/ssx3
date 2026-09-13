// Frontend controls for a bounded native rendering trial. Atomics carry requests
// to the CPU thread; only that thread owns the game adapter and pose history.
#pragma once
#include <atomic>
#include <string>
namespace NativeTrial {
enum class Status { Idle, Waiting, Running, Finished, Unavailable };
inline std::atomic<Status> status{Status::Idle};
inline std::atomic<bool> cancel{false};
inline std::atomic<bool> limited{false};
inline std::atomic<unsigned> frames{0}, extras{0};
inline std::string log_path; // set only while the runtime is stopped
inline double ends=0;       // CPU thread only
inline void Request() { cancel=false; limited=false; frames=0; extras=0; status=Status::Waiting; }
inline void Cancel() { cancel=true; }
inline bool Active(double now) {
 return status.load()==Status::Running && !cancel.load() && now<ends;
}
}
#ifdef SSX_NATIVE_TRIAL_APP
// Call while the old runtime has stopped, before constructing the next one.
extern "C" void SSXResetNativeTrial(const char* log_path);
#endif
