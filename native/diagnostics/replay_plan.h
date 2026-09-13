// Asset-independent memory ordering for a captured FIFO audit. This helper
// owns its RAM: no address can resolve into the running emulated machine.
#pragma once
#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>

namespace ReplayResearch {
inline size_t AllocatedBankSize(const void* data, size_t configured_size) {
  return data ? configured_size : 0;
}
struct MemoryUpdate {
  uint32_t position = 0, address = 0;
  std::vector<uint8_t> data;
};

class ShadowMemory {
public:
  ShadowMemory(size_t ram_size, uint32_t ram_mask_value, size_t exram_size, uint32_t exram_mask_value)
      : ram(ram_size), exram(exram_size), ram_mask(ram_mask_value), exram_mask(exram_mask_value) {}
  uint8_t* Resolve(uint32_t address, size_t size) {
    auto& bank = (address & 0x10000000u) ? exram : ram;
    const size_t offset = address & ((address & 0x10000000u) ? exram_mask : ram_mask);
    if (offset >= bank.size() || size > bank.size() - offset) return nullptr;
    return bank.data() + offset;
  }
  bool Apply(const MemoryUpdate& update) {
    auto* dest = Resolve(update.address, update.data.size());
    if (!dest) return false;
    std::copy(update.data.begin(), update.data.end(), dest);
    return true;
  }
  // FifoRecorder starts its shadow banks at zero, including unchanged ranges.
  void Reset() {
    std::fill(ram.begin(), ram.end(), 0);
    std::fill(exram.begin(), exram.end(), 0);
  }
private:
  std::vector<uint8_t> ram, exram;
  const uint32_t ram_mask, exram_mask;
};

// Validate every write before decoding anything. The decoder must consume
// each complete segment, which rejects updates in the middle of a command.
// Equal positions deliberately preserve recorder order (overlapping writes).
template <class Decode>
bool DecodeOrdered(size_t fifo_size, const std::vector<MemoryUpdate>& updates,
                   ShadowMemory& memory, Decode decode, std::string& error) {
  size_t previous = 0;
  for (const auto& update : updates) {
    if (update.position < previous || update.position > fifo_size) {
      error = "invalid_update_position";
      return false;
    }
    if (!memory.Resolve(update.address, update.data.size())) {
      error = "invalid_update_range";
      return false;
    }
    previous = update.position;
  }
  size_t position = 0;
  for (const auto& update : updates) {
    if (position < update.position && !decode(position, update.position)) {
      error = "invalid_fifo_segment";
      return false;
    }
    position = update.position;
    memory.Apply(update);
  }
  if (position < fifo_size && !decode(position, fifo_size)) {
    error = "invalid_fifo_segment";
    return false;
  }
  return true;
}
} // namespace ReplayResearch
