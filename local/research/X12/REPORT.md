# X12 — sparse Qwen exact rendering-path extraction

## Meta

- **Brief:** `local/muse/prompts/X12.md`
- **Worker:** opencode (local)
- **Pinned commit:** `17e90ded3689685ad359b76a9168c80a1f752e2d` (N8B1 worktree)
- **Worktree:** `/Users/brad/dev/ssx3-work/N8B1/PS2Recomp`
- **Elapsed:** ~2 minutes

## Wrong-pin trial error (before fix)

`rg` was run against `/Users/brad/dev/PS2Recomp` (unrelated checkout, HEAD `eac6cba6…`) instead of the N8B1 worktree. All 7 `rg -n` calls returned `IO error: No such file or directory`. The correct worktree path was supplied after this error.

## Command & result

```
python3 local/tooling/orch/check_x12.py local/research/X12/rows.tsv
```

Output: `X12 exact-line gate: 7/7, pinned source`

## LSP gap

All 7 `findReferences` calls (on `shot.image->get_width()`, `info.size =`, `cmd->copy_image_to_buffer(`, `m_device->map_host_buffer(`, `kStride = 640u`, `sourceRowBytes =`, `UpdateTexture(tex, s_uploadBuffer.data())`) returned **no results**. This is stated plainly; no further search was performed.

## rows.tsv

| id | file | line | source |
| --- | --- | --- | --- |
| `shot_width` | `ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp` | 268 | `const uint32_t w = shot.image->get_width();` |
| `buffer_bytes` | `ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp` | 280 | `info.size = static_cast<size_t>(w) * h * sizeof(uint32_t);` |
| `copy_extent` | `ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp` | 284 | `cmd->copy_image_to_buffer(*rb, *shot.image, 0, {}, {w, h, 1}, 0, 0,` |
| `host_map` | `ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp` | 291 | `m_device->map_host_buffer(*rb, Vulkan::MEMORY_ACCESS_READ_BIT));` |
| `backend_stride` | `ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp` | 298 | `constexpr uint32_t kStride = 640u;` |
| `frontend_stride` | `ps2xRuntime/src/lib/gs/gs_frontend.cpp` | 901 | `const size_t sourceRowBytes = static_cast<size_t>(kHostFrameWidth) * 4u;` |
| `texture_upload` | `ps2xRuntime/src/lib/ps2_runtime.cpp` | 799 | `UpdateTexture(tex, s_uploadBuffer.data());` |

## Tools used

- `git rev-parse` (2 invocations: wrong repo, correct repo)
- `git cat-file -t` (wrong repo, commit not found)
- `rg -n` (7 searches, all against correct worktree after pin fix)
- `read` (3 calls: lines 265-284, 898-907, 796-805 of worktree files)
- `lsp findReferences` (7 calls, all returned no results)
- `python3 check_x12.py` (1 call, passed 7/7)
