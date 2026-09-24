#!/usr/bin/env python3
"""Prepare the one N8D1 diagnostic source candidate in isolated WSL scratch."""
from pathlib import Path
import difflib
import hashlib
import json
import shutil
import subprocess

root = Path('/home/brad/n8d1')
old = Path('/home/brad/n8c2')
base = Path('/home/brad/n8b1')
pins = {
    'source_tar': (base / 'inputs/PS2Recomp-repair.tar', '6d091b62c1152f1c68488b853c42654ccab1b57e39795feef09285778d42a6a6'),
    'codegen': (base / 'codegen-ssx3/register_functions.cpp', '8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3'),
    'turnip': (old / 'jniLibs/arm64-v8a/libvulkan_freedreno.so', '717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d'),
    'shim': (old / 'jniLibs/arm64-v8a/libhardware.so', 'd7add7e8e2e31f3c49b83941c6686fa66ab3d844c650e8d70c93b026f90cafa0'),
    'wrapper': (old / 'PS2Recomp/android/gradle/wrapper/gradle-wrapper.jar', '498495120a03b9a6ab5d155f5de3c8f0d986a449153702fb80fc80e134484f17'),
    'source_cpp': (old / 'PS2Recomp/ps2xRuntime/src/lib/ps2_runtime.cpp', '68aa9c2ac559033b726b81948867a2ed1be581e30825291ef7b88241fd7d9f87'),
}

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

assert not (root / 'PS2Recomp').exists(), 'destination source already exists'
reads = {}
for name, (path, expected) in pins.items():
    reads[name] = [sha(path), sha(path)]
    assert reads[name] == [expected, expected], f'{name} pin mismatch'
root.mkdir(parents=True, exist_ok=True)
(root / 'input-hashes.json').write_text(json.dumps(reads, indent=2) + '\n')
subprocess.run(['rsync', '-a', '--exclude', '.cxx', '--exclude', 'build', '--exclude', '.gradle',
                str(old / 'PS2Recomp') + '/', str(root / 'PS2Recomp') + '/'], check=True)
shutil.copytree(old / 'jniLibs', root / 'jniLibs')
source = root / 'PS2Recomp/ps2xRuntime/src/lib/ps2_runtime.cpp'
assert sha(source) == pins['source_cpp'][1]
for name in ('turnip', 'shim', 'wrapper'):
    relative = {'turnip': root / 'jniLibs/arm64-v8a/libvulkan_freedreno.so',
                'shim': root / 'jniLibs/arm64-v8a/libhardware.so',
                'wrapper': root / 'PS2Recomp/android/gradle/wrapper/gradle-wrapper.jar'}[name]
    assert [sha(relative), sha(relative)] == [pins[name][1]] * 2
before = source.read_text()
assert before.count('ExportImage(img, pngPath);') == 2
needle = '    if (keep)\n    {\n        std::snprintf(pngPath, sizeof(pngPath), "%s/%s-%llu.png"'
helper = '''    auto writePngBytes = [&img](const char *path) {
        int encodedSize = 0;
        unsigned char *encoded = ExportImageToMemory(img, ".png", &encodedSize);
        bool ok = encoded && encodedSize > 0;
        if (ok)
        {
            std::ofstream out(path, std::ios::binary);
            if (out)
            {
                out.write(reinterpret_cast<const char *>(encoded), encodedSize);
                ok = out.good();
            }
            else
                ok = false;
        }
        if (encoded)
            MemFree(encoded);
        if (!ok)
        {
            static unsigned errors = 0;
            if (errors++ < 3u)
                std::cerr << "[frame:dump] PNG write failed path=" << path << std::endl;
        }
    };
'''
assert before.count(needle) == 1
after = before.replace(needle, helper + needle).replace('ExportImage(img, pngPath);', 'writePngBytes(pngPath);')
assert after.count('writePngBytes(pngPath);') == 2
source.write_text(after)
diff = ''.join(difflib.unified_diff(before.splitlines(keepends=True), after.splitlines(keepends=True),
                                    fromfile='N8C2/ps2_runtime.cpp', tofile='N8D1/ps2_runtime.cpp'))
(root / 'source.diff').write_text(diff)
(root / 'source-hashes.json').write_text(json.dumps({'before': pins['source_cpp'][1],
                                                     'after': [sha(source), sha(source)]}, indent=2) + '\n')
print(json.dumps({'input_hashes': reads, 'source_after': sha(source),
                  'source_diff_lines': len(diff.splitlines())}, indent=2))
