#pragma once
#include <algorithm>
#include <cmath>

namespace SSXOutput {
struct Size {
  int width=0, height=0;
  double scale=0;
  bool capped=false;
};

// Source is Dolphin's aspect-correct suggested picture size, not the allocated
// EFB. Expand the surface around that picture to retain the screen's aspect;
// Dolphin fills the unused area with bars. The iOS compositor still scales this
// surface to the physical panel. Never allocate beyond native output here.
inline Size Match(double screen_width, double screen_height, int source_width, int source_height) {
  if (!std::isfinite(screen_width) || !std::isfinite(screen_height) ||
      screen_width < 1 || screen_height < 1 || screen_width > 16384 || screen_height > 16384 ||
      source_width < 1 || source_height < 1 || source_width > 16384 || source_height > 16384)
    return {};
  const double requested=std::max(source_width/screen_width, source_height/screen_height);
  const double scale=std::min(1.0,requested);
  return {std::max(1,int(std::lround(screen_width*scale))),
          std::max(1,int(std::lround(screen_height*scale))), scale, requested>1};
}
}  // namespace SSXOutput
