// E45 bench stubs: the bench programs contain no XGkick, so the GS/PS2Memory
// packet paths never execute. They exist only to satisfy the linker when
// building the three real VU1 core TUs standalone.
#include "runtime/gs/gs_frontend.h"
#include "runtime/gs/ps2_gif_arbiter.h"
#include "runtime/ps2_memory.h"

#include <cstdint>
#include <cstdio>
#include <cstdlib>

GS::GS() = default;

void GS::processGIFPacket(const uint8_t *, uint32_t)
{
    std::fprintf(stderr, "E45 bench: unexpected GS::processGIFPacket\n");
    std::abort();
}

void PS2Memory::submitGifPacket(GifPathId, const uint8_t *, uint32_t, bool, bool)
{
    std::fprintf(stderr, "E45 bench: unexpected PS2Memory::submitGifPacket\n");
    std::abort();
}
