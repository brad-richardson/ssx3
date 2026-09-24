# X13B — sparse Qwen control

| Field | Value |
| --- | --- |
| Pin | `17e90ded3689685ad359b76a9168c80a1f752e2d` (N8B1/PS2Recomp, confirmed) |
| Excerpt | `local/research/X13/excerpt.txt` (4.3 KiB, source lines 236–310) |
| Checker | `python3 local/tooling/orch/check_x13.py local/research/X13B/rows.tsv` → **7/7** |
| Time | ~30 s (well under 5 min cap) |
| Context | ~4.3 KiB excerpt + 28-line checker + 7-line brief ≈ ~5.5 KiB (< 15k) |
| LSP | `goToDefinition` on `m_iface->vsync(vsync)` at line 253 → **empty** (N8B1 checkout not indexed by the LSP in this repo) |
| Gaps | LSP lookup could not resolve `vsync` — expected since the pinned source is a separate checkout; no inference drawn |

## rows.tsv

| stage | line | source |
| --- | --- | --- |
| scanout | 253 | `ParallelGS::ScanoutResult shot = m_iface->vsync(vsync);` |
| barrier | 275 | `cmd->image_barrier(*shot.image, VK_IMAGE_LAYOUT_READ_ONLY_OPTIMAL,` |
| copy | 284 | `cmd->copy_image_to_buffer(*rb, *shot.image, 0, {}, {w, h, 1}, 0, 0,` |
| submit | 288 | `m_device->submit(cmd);` |
| wait | 289 | `m_device->wait_idle();` |
| map | 291 | `m_device->map_host_buffer(*rb, Vulkan::MEMORY_ACCESS_READ_BIT));` |
| pack | 303 | `std::memcpy(out.pixels.data() + static_cast<size_t>(y) * kStride * 4u,` |
