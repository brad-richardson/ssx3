// Authored host-side transform history. No game memory or simulation changes.
#pragma once
#include <array>
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <unordered_map>

namespace RenderResearch {
using Matrix = std::array<float, 12>;
struct PoseKey {
  uint32_t source = 0, descriptor = 0, pass = 0, kind = 0;
  bool operator==(const PoseKey&) const = default;
};
struct PoseHash {
  size_t operator()(const PoseKey& k) const {
    size_t h = k.source;
    for (auto v : {k.descriptor, k.pass, k.kind}) h ^= v + 0x9e3779b9u + (h << 6) + (h >> 2);
    return h;
  }
};
inline bool Finite(const Matrix& m) {
  return std::all_of(m.begin(), m.end(), [](float f) { return std::isfinite(f); });
}
inline Matrix Blend(const Matrix& a, const Matrix& b, float alpha) {
  Matrix out;
  alpha = std::clamp(alpha, 0.f, 1.f);
  for (size_t i = 0; i < out.size(); ++i) out[i] = a[i] + (b[i] - a[i]) * alpha;
  return out;
}
inline Matrix Multiply(const Matrix& a, const Matrix& b) {
  Matrix out{};
  for (unsigned r = 0; r < 3; ++r) for (unsigned c = 0; c < 4; ++c) {
    double value = c == 3 ? a[r*4+3] : 0;
    for (unsigned k = 0; k < 3; ++k) value += double(a[r*4+k]) * b[k*4+c];
    out[r*4+c] = float(value);
  }
  return out;
}
inline bool Inverse(const Matrix& m, Matrix& out) {
  if (!Finite(m)) return false;
  const double a=m[0], b=m[1], c=m[2], d=m[4], e=m[5], f=m[6], g=m[8], h=m[9], i=m[10];
  const double det=a*(e*i-f*h)-b*(d*i-f*g)+c*(d*h-e*g);
  if (std::abs(det)<1e-8) return false;
  out = {float((e*i-f*h)/det),float((c*h-b*i)/det),float((b*f-c*e)/det),0,
         float((f*g-d*i)/det),float((a*i-c*g)/det),float((c*d-a*f)/det),0,
         float((d*h-e*g)/det),float((b*g-a*h)/det),float((a*e-b*d)/det),0};
  for (unsigned r=0;r<3;++r) out[r*4+3]=float(-double(out[r*4])*m[3]-double(out[r*4+1])*m[7]-double(out[r*4+2])*m[11]);
  return Finite(out);
}
// Small-step affine interpolation also accepts the game's weighted skinning
// matrices. It is not quaternion animation reconstruction. Reject large jumps
// and discontinuous scale/rotation instead of smearing an object across a cut.
inline bool Continuous(const Matrix& a, const Matrix& b) {
  if (!Finite(a) || !Finite(b)) return false;
  float linear = 0, delta = 0, translation = 0, distance = 0;
  for (size_t i = 0; i < a.size(); ++i) {
    const float d = b[i] - a[i];
    if (i % 4 == 3) { distance += d*d; translation += b[i]*b[i]; }
    else { linear += a[i]*a[i]; delta += d*d; }
  }
  return linear > 1e-8f && delta < linear * 0.04f &&
      distance < 1000.f*1000.f + translation * 0.04f;
}
class PoseHistory {
  struct Pose { Matrix matrix; bool valid; };
  using Map = std::unordered_map<PoseKey, Pose, PoseHash>;
  Map previous, current;
  uint64_t generation = 0;
  bool initialized = false, sealed = false, overflow = false;
public:
  static constexpr size_t Capacity = 8192;
  void Reset() { previous.clear(); current.clear(); initialized = sealed = overflow = false; }
  void ForgetPrevious() { previous.clear(); }
  void Begin(uint64_t next) {
    if (initialized && next == generation) { sealed = false; return; }
    if (initialized && next == generation + 1 && !overflow) previous = std::move(current);
    else previous.clear();
    current.clear(); generation = next; initialized = true; sealed = overflow = false;
  }
  void Add(PoseKey key, const Matrix& matrix) {
    if (sealed || overflow) return;
    auto found = current.find(key);
    if (found != current.end()) {
      // Ambiguous owners are rejected before any draw, including the first use.
      if (found->second.matrix != matrix) found->second.valid = false;
      return;
    }
    if (current.size() >= Capacity) { overflow = true; previous.clear(); return; }
    current.emplace(key, Pose{matrix, Finite(matrix)});
  }
  void Seal() { sealed = true; }
  bool Sample(PoseKey key, const Matrix& raw, float alpha, Matrix& out) const {
    if (!sealed || overflow || !std::isfinite(alpha)) return false;
    const auto a = previous.find(key), b = current.find(key);
    if (a == previous.end() || b == current.end() || !a->second.valid || !b->second.valid ||
        raw != b->second.matrix || !Continuous(a->second.matrix, raw)) return false;
    out = Blend(a->second.matrix, raw, alpha);
    return true;
  }
};
}
