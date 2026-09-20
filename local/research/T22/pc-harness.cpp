// T22 throwaway probe (NOT committed to the fork): drives the REAL
// TraceChannel.cpp emit path with a synthetic id/pc feed so the default-off
// byte shape and the pc= on-shape are proven without a boot (no lease).
// Stdin: lines "idHex pcHex". Env: PS2X_TRACE_SYSCALLS=<path> required;
// PS2X_TRACE_SYSCALLS_PC non-empty = pc= field on.
#include "TraceChannel.h"

#include <cstdint>
#include <cstdio>
#include <cstdlib>

int main()
{
    char line[256];
    unsigned long long id, pc;
    while (std::fgets(line, sizeof(line), stdin) != nullptr)
    {
        if (std::sscanf(line, "%llx %llx", &id, &pc) != 2)
        {
            continue;
        }
        ps2_syscalls::traceChannelEmit(static_cast<uint32_t>(id),
                                       static_cast<uint32_t>(pc));
    }
    return 0;
}
