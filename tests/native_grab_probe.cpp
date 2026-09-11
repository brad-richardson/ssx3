// Prints every PS2 shoulder mask with its GameCube translation. No game data.
#include <cstdio>
#include "GrabMap.h"
int main()
{
  for (uint8_t mask = 0; mask < 16; ++mask) {
    const char* name = "";
    bool exact = false;
    for (const auto& m : ssx::kGrabMappings)
      if (m.ps2 == mask) { name = m.ps2_name; exact = m.exact; }
    std::printf("%u %u %d %s\n", mask, ssx::GrabToGameCube(mask), exact, name);
  }
}
