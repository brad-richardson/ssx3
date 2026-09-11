// PS2 shoulder-button grabs translated to the GameCube build's L/R/Z grabs.
// PS2 combos come from the SSX 3 PS2 trick lists; GameCube combos from the
// GameCube build's guide and its own Controller Settings screen (L/R = grab,
// Z = grab board). Seven PS2 grabs exist on GameCube; the other eight map to
// the union of their constituent single-button grabs, which is the closest
// input the GameCube code accepts. Header-only so a host test can compile it.
#pragma once
#include <cstdint>

namespace ssx {
enum : uint8_t { PS2_L1 = 1, PS2_L2 = 2, PS2_R1 = 4, PS2_R2 = 8 };
enum : uint8_t { GC_L = 1, GC_R = 2, GC_Z = 4 };

struct GrabMapping {
  uint8_t ps2;
  uint8_t gc;
  const char* ps2_name;
  const char* gc_name;
  bool exact;
};

constexpr GrabMapping kGrabMappings[] = {
    {PS2_L1, GC_R, "Method", "Method", true},
    {PS2_L2, GC_L, "Mute", "Mute", true},
    {PS2_R1, GC_Z, "Stalefish", "Stalefish", true},
    {PS2_R2, GC_L | GC_R, "Indy", "Indy", true},
    {PS2_L1 | PS2_L2, GC_L | GC_Z, "Nosegrab", "Nosegrab", true},
    {PS2_R1 | PS2_R2, GC_R | GC_Z, "Tailgrab", "Tailgrab", true},
    {PS2_L1 | PS2_L2 | PS2_R1 | PS2_R2, GC_L | GC_R | GC_Z, "Shifty", "Shifty", true},
    // No GameCube equivalent; union of the single-button grabs.
    {PS2_L1 | PS2_R1, GC_R | GC_Z, "Melancholy", "Tailgrab", false},
    {PS2_L2 | PS2_R2, GC_L | GC_R, "Swiss Cheese", "Indy", false},
    {PS2_L1 | PS2_R2, GC_L | GC_R, "Stiffy", "Indy", false},
    {PS2_L2 | PS2_R1, GC_L | GC_Z, "Lein", "Nosegrab", false},
    {PS2_L1 | PS2_L2 | PS2_R1, GC_L | GC_R | GC_Z, "Stalemasky", "Shifty", false},
    {PS2_L1 | PS2_L2 | PS2_R2, GC_L | GC_R, "Seatbelt", "Indy", false},
    {PS2_L1 | PS2_R1 | PS2_R2, GC_L | GC_R | GC_Z, "Chicken Salad", "Shifty", false},
    {PS2_L2 | PS2_R1 | PS2_R2, GC_L | GC_R | GC_Z, "Spaghetti", "Shifty", false},
};

constexpr uint8_t GrabToGameCube(uint8_t ps2_mask)
{
  for (const auto& mapping : kGrabMappings)
    if (mapping.ps2 == ps2_mask) return mapping.gc;
  return 0;
}
}  // namespace ssx
