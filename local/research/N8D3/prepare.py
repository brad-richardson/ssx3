#!/usr/bin/env python3
"""Make the isolated N8D3 WSL copy and its one diagnostic source edit."""
from pathlib import Path
import difflib
import hashlib
import json
import shutil
import subprocess

old = Path('/home/brad/n8d1')
root = Path('/home/brad/n8d3')
assert not root.exists(), 'N8D3 WSL scratch already exists'
root.mkdir()
subprocess.run(['rsync', '-a', '--exclude', '.cxx', '--exclude', 'build', '--exclude', '.gradle',
                '--exclude', '/ps2xRuntime/src/runner/',
                str(old / 'PS2Recomp') + '/', str(root / 'PS2Recomp') + '/'], check=True)
shutil.copytree(old / 'jniLibs', root / 'jniLibs')
source = root / 'PS2Recomp/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp'
before = source.read_text()
needle = '''        // Frontend contract: 640-pixel row stride (kHostFrameWidth), rows
        // of `width` valid pixels, height <= 512.
'''
assert before.count(needle) == 1
before_copy = '''        const char *n8d3Flag = std::getenv("PS2X_N8D3_RAW_CAPTURE");
        const bool n8d3Capture = n8d3Flag && std::strcmp(n8d3Flag, "1") == 0 &&
                                 request.vsyncTick == 2050u;
        const size_t n8d3RawBytes = static_cast<size_t>(w) * h * 4u;
        const char *n8d3Dir = n8d3Capture ? std::getenv("PS2X_FRAME_DUMP_DIR") : nullptr;
        auto n8d3Write = [](const std::string &path, const uint8_t *data, size_t count) {
            std::ofstream file(path, std::ios::binary | std::ios::trunc);
            if (!file) return false;
            file.write(reinterpret_cast<const char *>(data), static_cast<std::streamsize>(count));
            file.close();
            return file.good();
        };
        bool n8d3RawOk = false;
        if (n8d3Capture && n8d3Dir && n8d3RawBytes <= 4096u * 4096u * 4u)
            n8d3RawOk = n8d3Write(std::string(n8d3Dir) + "/n8d3-raw.bin", px, n8d3RawBytes);

'''
assert before.count('        out.displayFbp = static_cast<uint32_t>(m_priv ? (m_priv->dispfb1 & 0x1FFu) : 0u);') == 1
after_copy = '''        if (n8d3Capture)
        {
            bool packedOk = false;
            if (n8d3Dir && n8d3RawOk && out.width == w && out.height == h)
            {
                std::vector<uint8_t> packed(n8d3RawBytes);
                for (uint32_t y = 0; y < h; ++y)
                    std::memcpy(packed.data() + static_cast<size_t>(y) * w * 4u,
                                out.pixels.data() + static_cast<size_t>(y) * kStride * 4u,
                                static_cast<size_t>(w) * 4u);
                packedOk = n8d3Write(std::string(n8d3Dir) + "/n8d3-packed.bin",
                                      packed.data(), packed.size());
            }
            const VkFormat format = shot.image->get_format();
            if (n8d3Dir)
            {
                std::ofstream meta(std::string(n8d3Dir) + "/n8d3-stage.txt", std::ios::trunc);
                if (meta)
                {
                    meta << "tick=" << request.vsyncTick << " width=" << w << " height=" << h
                         << " format=" << static_cast<uint32_t>(format)
                         << " raw_bytes=" << n8d3RawBytes << " packed_width=" << out.width
                         << " packed_height=" << out.height << " packed_stride=" << kStride
                         << " displayFbp=" << out.displayFbp << " sourceFbp=" << out.sourceFbp
                         << " raw_write=" << (n8d3RawOk ? 1 : 0)
                         << " packed_write=" << (packedOk ? 1 : 0) << '\\n';
                    meta.close();
                    if (!meta.good()) std::cerr << "[n8d3] metadata write failed" << std::endl;
                }
                else std::cerr << "[n8d3] metadata open failed" << std::endl;
            }
            std::cerr << "[n8d3] tick=" << request.vsyncTick << " raw=" << n8d3RawOk
                      << " packed=" << packedOk << " format=" << static_cast<uint32_t>(format)
                      << " size=" << w << "x" << h << " fbp=" << out.displayFbp << std::endl;
        }

'''
after = before.replace(needle, before_copy + needle)
anchor = '''        out.sourceFbp = out.displayFbp;

        const uint64_t t1 = nowNanos();'''
assert after.count(anchor) == 1
after = after.replace(anchor, '''        out.sourceFbp = out.displayFbp;
'''+after_copy+'''        const uint64_t t1 = nowNanos();''')
assert after.count('#include <iostream>') == 1
after = after.replace('#include <iostream>', '#include <iostream>\n#include <fstream>\n#include <string>')
source.write_text(after)
diff = ''.join(difflib.unified_diff(before.splitlines(keepends=True), after.splitlines(keepends=True),
                                    fromfile='N8D1/ps2_gs_parallel_backend.cpp',
                                    tofile='N8D3/ps2_gs_parallel_backend.cpp'))
(root / 'source.diff').write_text(diff)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
(root / 'source-hashes.json').write_text(json.dumps({'n8d1': sha(old / 'PS2Recomp/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp'),
                                                    'n8d3': [sha(source), sha(source)]}, indent=2) + '\n')
print((root / 'source-hashes.json').read_text())
