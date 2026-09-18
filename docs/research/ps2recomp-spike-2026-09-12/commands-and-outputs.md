
## [0] List workspace contents
```
ls -la; echo ---; ls -R | head -n 200
```
output:
```
total 2934988
drwxrwxr-x  2 brad brad       4096 Sep 12 00:14 .
drwxrwxr-x 46 brad brad       4096 Sep 11 23:21 ..
-rw-rw-r--  1 brad brad 3005415424 Sep 12 00:14 SSX 3 (USA).iso
---
.:
SSX 3 (USA).iso

```

## [1] Check extraction tool availability
```
command -v 7z; command -v 7zz; command -v isoinfo; command -v mcopy; command -v strings; command -v mipsel-linux-gnu-objdump; command -v mips64-elf-objdump; ls -lh
```
output:
```
/usr/bin/strings
total 2.8G
-rw-rw-r-- 1 brad brad 2.8G Sep 12 00:14 SSX 3 (USA).iso

```

## [2] Check Python and ISO tooling
```
python3 --version; pip --version; command -v python3; command -v file; command -v xxd; command -v od; ls /usr/bin/*iso* /usr/bin/*mips* 2>&1 | head; apt list --installed 2>/dev/null | grep -i -E "geniso|cdr|mtools" | head
```
output:
```
Python 3.12.3
/bin/sh: 1: pip: not found
/usr/bin/python3
/usr/bin/file
/usr/bin/xxd
/usr/bin/od
ls: cannot access '/usr/bin/*iso*': No such file or directory
ls: cannot access '/usr/bin/*mips*': No such file or directory

```

## [3] Probe ISO volume descriptor
```
python3 -c "import sys; print(sys.version)"; pip3 --version 2>&1; uv --version 2>&1; file "SSX 3 (USA).iso"; python3 -c "import struct; f=open('SSX 3 (USA).iso','rb'); f.seek(32*2048+40); print(repr(f.read(32))); f.seek(16*2048); print(repr(f.read(128)))"
```
output:
```
3.12.3 (main, Aug 31 2026, 10:18:26) [GCC 13.3.0]
/bin/sh: 1: pip3: not found
uv 0.11.26 (x86_64-unknown-linux-gnu)
SSX 3 (USA).iso: UDF filesystem data (version 1.5) 'SSX3'
b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x05\x01\x00\x01\x00\x02\x00\x02\x00\x01\x00\x00\x00\x01\x00\x00\x00'
b'\x01CD001\x01\x00PLAYSTATION                     SSX3                            \x00\x00\x00\x00\x00\x00\x00\x00`d\x16\x00\x00\x16d`\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x01\x01\x00\x00\x01'

```

## [4] List ISO root directory entries
```
python3 - <<'EOF'
import struct
# List root directory from ISO9660 PVD
with open('SSX 3 (USA).iso','rb') as f:
    f.seek(16*2048)
    pvd = f.read(2048)
    # root dir record at offset 156, len 34
    root = pvd[156:156+34]
    loc = struct.unpack('<I', root[2:6])[0]
    dlen = struct.unpack('<I', root[10:14])[0]
    print(f"root loc={loc} len={dlen}")
    f.seek(loc*2048)
    data = f.read(dlen)
    off=0
    while off < len(data):
        l = data[off]
        if l==0:
            # pad to sector boundary? just advance
            off+=1
            continue
        rec = data[off:off+l]
        flags = rec[25]
        namelen = rec[32]
        name = rec[33:33+namelen]
        extent = struct.unpack('<I', rec[2:6])[0]
        size = struct.unpack('<I', rec[10:14])[0]
        print(f"len={l} flags={flags} extent={extent} size={size} name={name!r}")
        off+=l
EOF
```
output:
```
root loc=261 len=488
len=48 flags=2 extent=261 size=488 name=b'\x00'
len=48 flags=2 extent=261 size=488 name=b'\x01'
len=60 flags=0 extent=483 size=49 name=b'SYSTEM.CNF;1'
len=60 flags=0 extent=484 size=3890784 name=b'SLUS_207.72;1'
len=58 flags=0 extent=2973 size=268435456 name=b'PAD1.000;1'
len=58 flags=0 extent=134045 size=268435456 name=b'PAD0.000;1'
len=50 flags=2 extent=262 size=276 name=b'CNF'
len=52 flags=2 extent=263 size=840 name=b'DATA'
len=54 flags=2 extent=264 size=612 name=b'NETGUI'

```

## [5] Recursively list ISO directories
```
python3 - <<'EOF'
import struct
def list_dir(extent, size, indent=""):
    with open('SSX 3 (USA).iso','rb') as f:
        f.seek(extent*2048)
        data = f.read(size)
    off=0
    entries=[]
    while off < len(data):
        l = data[off]
        if l==0:
            off+=1
            continue
        rec = data[off:off+l]
        if len(rec)<33:
            off+=l
            continue
        flags = rec[25]
        namelen = rec[32]
        name = rec[33:33+namelen].decode('ascii', errors='replace').rstrip(';1').rstrip('.') if namelen>2 else repr(rec[33:33+namelen])
        extent2 = struct.unpack('<I', rec[2:6])[0]
        size2 = struct.unpack('<I', rec[10:14])[0]
        print(f"{indent}flags={flags} extent={extent2} size={size2} name={name}")
        entries.append((name, flags, extent2, size2))
        off+=l
    return entries
root = list_dir(261, 488)
for name, flags, ext, sz in root:
    if flags==2 and name not in ("'\\x00'","'\\x01'"):
        print(f"--- {name} ---")
        subs = list_dir(ext, sz, "  ")
        for n2,f2,e2,s2 in subs:
            if f2==2 and n2 not in ("'\\x00'","'\\x01'"):
                print(f"--- {name}/{n2} ---")
                try:
                    list_dir(e2, s2, "    ")
                except Exception as ex:
                    print("err", ex)
EOF
```
output:
```
flags=2 extent=261 size=488 name=b'\x00'
flags=2 extent=261 size=488 name=b'\x01'
flags=0 extent=483 size=49 name=SYSTEM.CNF
flags=0 extent=484 size=3890784 name=SLUS_207.72
flags=0 extent=2973 size=268435456 name=PAD1.000
flags=0 extent=134045 size=268435456 name=PAD0.000
flags=2 extent=262 size=276 name=CNF
flags=2 extent=263 size=840 name=DATA
flags=2 extent=264 size=612 name=NETGUI
--- b'\x00' ---
  flags=2 extent=261 size=488 name=b'\x00'
  flags=2 extent=261 size=488 name=b'\x01'
  flags=0 extent=483 size=49 name=SYSTEM.CNF
  flags=0 extent=484 size=3890784 name=SLUS_207.72
  flags=0 extent=2973 size=268435456 name=PAD1.000
  flags=0 extent=134045 size=268435456 name=PAD0.000
  flags=2 extent=262 size=276 name=CNF
  flags=2 extent=263 size=840 name=DATA
  flags=2 extent=264 size=612 name=NETGUI
--- b'\x00'/b'\x00' ---
    flags=2 extent=261 size=488 name=b'\x00'
    flags=2 extent=261 size=488 name=b'\x01'
    flags=0 extent=483 size=49 name=SYSTEM.CNF
    flags=0 extent=484 size=3890784 name=SLUS_207.72
    flags=0 extent=2973 size=268435456 name=PAD1.000
    flags=0 extent=134045 size=268435456 name=PAD0.000
    flags=2 extent=262 size=276 name=CNF
    flags=2 extent=263 size=840 name=DATA
    flags=2 extent=264 size=612 name=NETGUI
--- b'\x00'/b'\x01' ---
    flags=2 extent=261 size=488 name=b'\x00'
    flags=2 extent=261 size=488 name=b'\x01'
    flags=0 extent=483 size=49 name=SYSTEM.CNF
    flags=0 extent=484 size=3890784 name=SLUS_207.72
    flags=0 extent=2973 size=268435456 name=PAD1.000
    flags=0 extent=134045 size=268435456 name=PAD0.000
    flags=2 extent=262 size=276 name=CNF
    flags=2 extent=263 size=840 name=DATA
    flags=2 extent=264 size=612 name=NETGUI
--- b'\x00'/CNF ---
    flags=2 extent=262 size=276 name=b'\x00'
    flags=2 extent=261 size=488 name=b'\x01'
    flags=0 extent=265117 size=812 name=DIAL_SPD.CNF
    flags=0 extent=265118 size=964 name=ICON.SYS
    flags=0 extent=265119 size=33688 name=SYS_NET.ICO
--- b'\x00'/DATA ---
    flags=2 extent=263 size=840 name=b'\x00'
    flags=2 extent=261 size=488 name=b'\x01'
    flags=2 extent=265 size=1072 name=AUDIO
    flags=2 extent=266 size=458 name=b'BE'
    flags=2 extent=267 size=1006 name=CHAR
    flags=2 extent=268 size=804 name=CONFIG
    flags=2 extent=269 size=570 name=FONTS
    flags=2 extent=270 size=154 name=ICON
    flags=2 extent=271 size=396 name=LOCALE
    flags=2 extent=272 size=158 name=MISSIONS
    flags=2 extent=273 size=1454 name=MODULES
    flags=2 extent
... [20118 chars]
```

## [6] Peek SYSTEM.CNF and ELF header
```
grep -a -o -m5 -E "BOOT2|cdrom0:|SLUS" "SSX 3 (USA).iso" | head; echo ---; dd if="SSX 3 (USA).iso" bs=2048 skip=483 count=1 2>/dev/null | head -c 200 | od -A x -t x1z | head
```
output:
```
SLUS
SLUS
BOOT2
cdrom0:
SLUS
cdrom0:
SLUS
---
000000 42 4f 4f 54 32 3d 63 64 72 6f 6d 30 3a 5c 53 4c  >BOOT2=cdrom0:\SL<
000010 55 53 5f 32 30 37 2e 37 32 3b 31 0d 0a 56 45 52  >US_207.72;1..VER<
000020 3d 31 2e 30 30 0d 0a 56 4d 4f 44 45 3d 4e 54 53  >=1.00..VMODE=NTS<
000030 43 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  >C...............<
000040 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  >................<
*
0000c0 00 00 00 00 00 00 00 00                          >........<
0000c8

```

## [7] Extract main ELF from ISO
```
python3 - <<'EOF'
with open('SSX 3 (USA).iso','rb') as f:
    f.seek(484*2048)
    data = f.read(3890784)
open('/tmp/SLUS_207.72','wb').write(data)
print(len(data), data[:4])
import struct
assert data[:4]==b'\x7fELF'
e_entry = struct.unpack('<I', data[24:28])[0]
e_phoff = struct.unpack('<I', data[28:32])[0]
e_phnum = struct.unpack('<H', data[44:46])[0]
print(f"entry={e_entry:08x} phoff={e_phoff} phnum={e_phnum}")
for i in range(e_phnum):
    ph = data[e_phoff+i*32:e_phoff+(i+1)*32]
    p_type,p_offset,p_vaddr,p_paddr,p_filesz,p_memsz,p_flags,p_align = struct.unpack('<IIIIIIII', ph)
    print(f"ph{i}: type={p_type} off={p_offset:08x} vaddr={p_vaddr:08x} filesz={p_filesz} memsz={p_memsz} flags={p_flags:x}")
EOF
ls -lh /tmp/SLUS_207.72
```
output:
```
3890784 b'\x7fELF'
entry=00100008 phoff=52 phnum=1
ph0: type=1 off=00001000 vaddr=00100000 filesz=3820532 memsz=4451036 flags=7
-rw-rw-r-- 1 brad brad 3.8M Sep 12 00:19 /tmp/SLUS_207.72

```

## [8] Fetch PS2Recomp README raw
```
curl -sL https://raw.githubusercontent.com/ran-j/PS2Recomp/main/README.md | head -n 300 || wget -qO- https://raw.githubusercontent.com/ran-j/PS2Recomp/main/README.md | head -n 300
```
output:
```
## PS2Recomp: PlayStation 2 Static Recompiler (Experimental)

[![Discord](https://img.shields.io/badge/Discord-Join%20Server-5865F2?logo=discord&logoColor=white)](https://discord.gg/JQ8mawxUEf)

Also check our [WIKI](https://github.com/ran-j/PS2Recomp/wiki)


This project statically recompiles PS2 ELF binaries into C++ and provides a runtime to execute the generated code.

### Modules

* `ps2xAnalyzer`: scans ELF/functions and writes TOML config (`stubs`, `skip`, instruction patches).
* `ps2xRecomp`: reads TOML + ELF, decodes R5900 instructions, and generates C++ output.
* `ps2xRuntime`: hosts memory, function registration, syscall dispatch, and hardware stubs.
* `ps2xIOP`: portable, instance-owned IOP HLE services, game profiles, and the C plugin ABI.

### Features

* Translates MIPS R5900 instructions to C++ code
* PS2-specific MMI and VU0 macro support.
* Single-file or multi-file output.
* Configurable stubs, skips, and instruction patches.
* Instruction-driven syscall handling.

### How It Works
PS2Recomp works by:

* Parsing a PS2 ELF file to extract functions, symbols, and relocations
* Decoding the MIPS R5900 instructions in each function
* Translating those instructions to equivalent C++ code
* Generating a runtime that can execute the recompiled code

The translated code is very literal, with each MIPS instruction mapping to a C++ operation. For example, `addiu $r4, $r4, 0x20` becomes `ctx->r4 = ADD32(ctx->r4, 0X20);`.

### Current Behavior

* `stubs` entries generate wrappers that call known runtime syscall/stub handlers by name.
* `stubs` also supports address bindings with `handler@0xADDRESS` for stripped games (for example `sceCdRead@0x00123456`).
* Address bindings also support generic return handlers for triage: `ret0`, `ret1`, `reta0`.
* Recompiler now tries relocation-symbol auto-binding at callsites (`J/JAL`) before raw address dispatch; when relocation symbol is known (for example `sceCdRead`), it can call runtime handlers without manual address mapping.
* Recompiler discovers additional internal static entry targets and emits `entry_...` wrappers for those addresses.
* For unresolved static `J/JAL` sites, generated code falls back to `runtime->lookupFunction(0x...)`.
* `skip` entries are not recompiled and generate explicit `ps2_stubs::TODO_NAMED(...)` wrappers.
* Recompiled `SYSCALL` now calls `runtime->handleSyscall(...)` with the encoded syscall immediate.
* Runtime syscall dispatch tries encoded syscall ID first, then falls back to
... [8108 chars]
```

## [9] Probe ELF sections and VU strings
```
python3 - <<'EOF'
import struct
with open('/tmp/SLUS_207.72','rb') as f:
    data = f.read()
print("size", len(data))
e_shoff = struct.unpack('<I', data[32:36])[0]
e_shentsize = struct.unpack('<H', data[46:48])[0]
e_shnum = struct.unpack('<H', data[48:50])[0]
e_shstrndx = struct.unpack('<H', data[50:52])[0]
print(f"shoff={e_shoff} shentsize={e_shentsize} shnum={e_shnum} shstrndx={e_shstrndx}")
# strings search
import re
for pat in [b'vu1', b'VU1', b'VIF', b'vif', b'MPG', b'mpg', b'.vsm', b'.vcl', b'microcode', b'DMA', b'sceVif', b'sceVu', b'sceDma', b'EAGL', b'RenderWare', b'RW']:
    idxs = [m.start() for m in re.finditer(re.escape(pat), data)]
    print(f"{pat!r}: {len(idxs)} {idxs[:10]}")
EOF
```
output:
```
size 3890784
shoff=3887544 shentsize=40 shnum=81 shstrndx=80
b'vu1': 0 []
b'VU1': 1 [3770263]
b'VIF': 2 [3770106, 3770215]
b'vif': 0 []
b'MPG': 0 []
b'mpg': 0 []
b'.vsm': 0 []
b'.vcl': 0 []
b'microcode': 0 []
b'DMA': 3 [3730074, 3769943, 3770167]
b'sceVif': 0 []
b'sceVu': 0 []
b'sceDma': 0 []
b'EAGL': 1 [3762104]
b'RenderWare': 0 []
b'RW': 3 [200188, 206960, 208416]

```

## [10] Clone PS2Recomp for coverage analysis
```
git clone --depth 1 https://github.com/ran-j/PS2Recomp.git /tmp/PS2Recomp 2>&1 | tail -5; ls -R /tmp/PS2Recomp | head -n 100
```
output:
```
Cloning into '/tmp/PS2Recomp'...
/tmp/PS2Recomp:
android
CMakeLists.txt
CMakeSettings.json
LICENSE
ps2xAnalyzer
ps2xIOP
ps2xRecomp
ps2xRuntime
ps2xStudio
ps2xTest
README.md
vita

/tmp/PS2Recomp/android:
app
build.gradle
gradle
gradle.properties
README.md
settings.gradle

/tmp/PS2Recomp/android/app:
build.gradle
src

/tmp/PS2Recomp/android/app/src:
main

/tmp/PS2Recomp/android/app/src/main:
AndroidManifest.xml

/tmp/PS2Recomp/android/gradle:
wrapper

/tmp/PS2Recomp/android/gradle/wrapper:
gradle-wrapper.properties

/tmp/PS2Recomp/ps2xAnalyzer:
CMakeLists.txt
include
Readme.md
src

/tmp/PS2Recomp/ps2xAnalyzer/include:
ps2recomp

/tmp/PS2Recomp/ps2xAnalyzer/include/ps2recomp:
analysis_passes.h
elf_analysis_context.h
elf_analyzer.h
function_classifier.h
sce_symbol_database_data.h
sce_symbol_scanner.h
toml_generator.h

/tmp/PS2Recomp/ps2xAnalyzer/src:
analysis_passes.cpp
analyzer_main.cpp
elf_analysis_context.cpp
elf_analyzer.cpp
function_classifier.cpp
sce_symbol_scanner.cpp
toml_generator.cpp

/tmp/PS2Recomp/ps2xIOP:
CMakeLists.txt
include
PluginExample.md
README.md
src

/tmp/PS2Recomp/ps2xIOP/include:
ps2x

/tmp/PS2Recomp/ps2xIOP/include/ps2x:
iop

/tmp/PS2Recomp/ps2xIOP/include/ps2x/iop:
iop_host.h
iop_subsystem.h
iop_types.h
plugin_api.h

/tmp/PS2Recomp/ps2xIOP/src:
builtin_profiles.cpp
iop_service.h
iop_subsystem.cpp
module_factories.h
modules
plugin_loader.cpp
plugin_loader.h

/tmp/PS2Recomp/ps2xIOP/src/modules:
clfile.cpp
cri_dtx.cpp
dbcman.cpp
libsd.cpp
mcserv.cpp
sdrdrv.cpp

```

## [11] List ELF section headers
```
python3 - <<'EOF'
import struct
with open('/tmp/SLUS_207.72','rb') as f:
    data = f.read()
e_shoff = struct.unpack('<I', data[32:36])[0]
e_shnum = struct.unpack('<H', data[48:50])[0]
e_shstrndx = struct.unpack('<H', data[50:52])[0]
shstr = data[e_shoff+e_shstrndx*40:e_shoff+(e_shstrndx+1)*40]
shstr_off = struct.unpack('<I', shstr[16:20])[0]
def getstr(off):
    end = data.index(b'\x00', shstr_off+off)
    return data[shstr_off+off:end].decode('ascii', errors='replace')
for i in range(e_shnum):
    sh = data[e_shoff+i*40:e_shoff+(i+1)*40]
    name, stype, flags, addr, off, size, link, info, align, entsz = struct.unpack('<IIIIIIIIII', sh)
    print(f"{i:2d} {getstr(name):22s} type={stype} flags={flags:x} addr={addr:08x} off={off:08x} size={size:8d} entsize={entsz}")
EOF
```
output:
```
 0                        type=0 flags=0 addr=00000000 off=00000000 size=       0 entsize=0
 1 .text                  type=1 flags=6 addr=00100000 off=00001000 size= 3334176 entsize=0
 2 .gnu.linkonce.t.CreateFrame__23PS2_SONY_CODEC_INTERNALUiUi type=1 flags=6 addr=0042e020 off=0032f020 size=     144 entsize=0
 3 .gnu.linkonce.t.__vd__23PS2_SONY_CODEC_INTERNALPvT1 type=1 flags=6 addr=0042e0b0 off=0032f0b0 size=       8 entsize=0
 4 .gnu.linkonce.t.__vn__23PS2_SONY_CODEC_INTERNALUiPv type=1 flags=6 addr=0042e0b8 off=0032f0b8 size=       8 entsize=0
 5 .gnu.linkonce.t.__dl__23PS2_SONY_CODEC_INTERNALPvT1 type=1 flags=6 addr=0042e0c0 off=0032f0c0 size=       8 entsize=0
 6 .gnu.linkonce.t.__nw__23PS2_SONY_CODEC_INTERNALUiPv type=1 flags=6 addr=0042e0c8 off=0032f0c8 size=       8 entsize=0
 7 .gnu.linkonce.t.__vd__23PS2_SONY_CODEC_INTERNALPv type=1 flags=6 addr=0042e0d0 off=0032f0d0 size=      36 entsize=0
 8 .gnu.linkonce.t.__dl__23PS2_SONY_CODEC_INTERNALPv type=1 flags=6 addr=0042e0f8 off=0032f0f8 size=      36 entsize=0
 9 .gnu.linkonce.t.__vn__23PS2_SONY_CODEC_INTERNALUiPCciii type=1 flags=6 addr=0042e120 off=0032f120 size=      44 entsize=0
10 .gnu.linkonce.t.__nw__23PS2_SONY_CODEC_INTERNALUiPCciii type=1 flags=6 addr=0042e150 off=0032f150 size=      44 entsize=0
11 .gnu.linkonce.t.__vn__23PS2_SONY_CODEC_INTERNALUi type=1 flags=6 addr=0042e180 off=0032f180 size=      60 entsize=0
12 .gnu.linkonce.t.__nw__23PS2_SONY_CODEC_INTERNALUi type=1 flags=6 addr=0042e1c0 off=0032f1c0 size=      60 entsize=0
13 .gnu.linkonce.t.__tf23PS2_SONY_CODEC_INTERNAL type=1 flags=6 addr=0042e200 off=0032f200 size=     120 entsize=0
14 .gnu.linkonce.t._$_Q24RCMP5CODEC type=1 flags=6 addr=0042e278 off=0032f278 size=      56 entsize=0
15 .gnu.linkonce.t.__tfQ24RCMP5CODEC type=1 flags=6 addr=0042e2b0 off=0032f2b0 size=      64 entsize=0
16 .gnu.linkonce.t.GetCodecIData__Q24RCMP7DECODER type=1 flags=6 addr=0042e2f0 off=0032f2f0 size=       8 entsize=0
17 .gnu.linkonce.t.HasCodec__Q24RCMP7DECODER type=1 flags=6 addr=0042e2f8 off=0032f2f8 size=      12 entsize=0
18 .gnu.linkonce.t.__vd__Q24RCMP7DECODERPvT1 type=1 flags=6 addr=0042e308 off=0032f308 size=       8 entsize=0
19 .gnu.linkonce.t.__vn__Q24RCMP7DECODERUiPv type=1 flags=6 addr=0042e310 off=0032f310 size=       8 entsize=0
20 .gnu.linkonce.t.__dl__Q24RCMP7DECODERPvT1 type=1 flags=6 addr=0042e318 off=0032f318 size=       8 entsize=0
21 .gnu.linkonce.t.__nw__Q24RCMP7DECODERUiPv type=1 flags=6 addr=0042e320 off=0032f320 size=      
... [8938 chars]
```

## [12] Dump string contexts in ELF
```
python3 - <<'EOF'
with open('/tmp/SLUS_207.72','rb') as f:
    data = f.read()
for addr in [3770263, 3770106, 3770215, 3730074, 3769943, 3770167, 3762104]:
    s = addr - 0x100000 + 0x1000  # file offset approx? vaddr base 0x100000 at file off 0x1000
    print(f"--- vaddr-approx {addr} -> fileoff {s} ---")
    print(repr(data[s-200:s+300]))
EOF
```
output:
```
--- vaddr-approx 3770263 -> fileoff 2725783 ---
b"\x14-\x10\x00\x02\x10^\x0e\x0ct\x00\x04&-\x80@\x00\x10\x00\x00\x12-\x10\x00\x00\x08\x00\x03\x8e\x00\x00\x00\x00-( \x02p\x00d\x84t\x00b\x8c\t\xf8@\x00! \x04\x02\x08\x00@T \x00\xb0{\x04\x00\x10\x8e\xc6]\x0e\x0c- \x00\x02\xf5\xff@P\x08\x00\x03\x8e-\x10\x00\x00 \x00\xb0{\x10\x00\xb1{\x00\x00\xbf\xdf\x08\x00\xe0\x030\x00\xbd'\xe0\xff\xbd'\x10\x00\xb0\x7f\x00\x00\xbf\xff\x10^\x0e\x0ct\x00\x84$-\x80@\x00\r\x00\x00R\x10\x00\xb0{\x08\x00\x02\x8e\x00\x00\x00\x00\x80\x00D\x84\x84\x00C\x8c\t\xf8`\x00! \x04\x02\x04\x00\x10\x8e\xc6]\x0e\x0c- \x00\x02\xf8\xff@P\x08\x00\x02\x8e\x10\x00\xb0{\x00\x00\xbf\xdf\x08\x00\xe0\x03 \x00\xbd'\x00\x00\x00\x00\xd0\xff\xbd' \x00\xb0\x7f\x10\x00\xbf\xff\x14\x00\x82\x8cC\x11\x02\x00\x01\x00B0\x0c\x00@T-\x10\x00\x00I\x00\x02<\x04\x00\xa5\xaf\xb8KB$I\x00\x10<\xe8L\x10&\x00\x00\xa2\xaft\x00\x84$~^\x0e\x0c-(\xa0\x03\x00\x00\xb0\xaf+\x10\x02\x00 \x00\xb0{\x10\x00\xbf\xdf\x08\x00\xe0\x030\x00\xbd'\x00\x00\x00\x00\xd0\xff\xbd't\x00\x84$\x10\x00\xb1\x7f \x00\xb0\x7f\x00\x00\xbf\xff\x10^\x0e\x0c-\x88\xa0\x00-\x80@\x00\x0e\x00\x00R \x00\xb0{\x07\x00\x00\x10\x00\x00\x00\x00-( \x02\x90\x00D\x84\x94\x00C\x8c\t\xf8`\x00! \x04\x02\x04\x00\x10\x8e\xc6]\x0e\x0c- \x00\x02\xf7\xff@P\x08\x00\x02\x8e \x00\xb0{\x10\x00\xb1{\x00\x00\xbf\xdf\x08\x00\xe0\x030\x00\xbd'\x00\x00\x00\x00\xc0\xff\xbd'\x10\x00\xb1\x7f8\x00\xb5\xe7-\x88\x80\x000\x00\xb4\xe7Fe\x00F \x00\xb0\x7f\x06m\x00F\x00\x00\xbf\xff\x10^\x0e\x0ct\x00$&-\x80@\x00\x16\x00\x00R \x00\xb0{\x14\x00\x02\x8e\x00\x00\x00\x00\x83\x11\x02\x00\x01\x00B0\x0b\x00@P\x04\x00\x10\x8e\x08\x00\x03\x8eD\x00,\xc6H\x00-"
--- vaddr-approx 3770106 -> fileoff 2725626 ---
b"\xbd'\x00\x00\x00\x00\xb0\xff\xbd'I\x00\x02<@\x00\xb0\x7f\x98KB$0\x00\xb1\x7f-\x80\xa0\x00 \x00\xb2\x7fI\x00\x11<-\x90\x80\x00\x10\x00\xbf\xff\xe8L1&\x04\x00\xb0\xaft\x00D&\x00\x00\xa2\xaf~^\x0e\x0c-(\xa0\x03\x14\x00C\x8e\xef\xff\x02$+\x80\x10\x00\x00\x00\xb1\xaf\x00\x81\x10\x00$\x18b\x00%\x18p\x000\x00\xb1{\x14\x00C\xae@\x00\xb0{ \x00\xb2{\x10\x00\xbf\xdf\x08\x00\xe0\x03P\x00\xbd'\xd0\xff\xbd' \x00\xb0\x7f\x10\x00\xb1\x7f-\x80\x80\x00\x00\x00\xbf\xff\xd8\x7f\x0e\x0c-\x88\xa0\x00\x15\x00@\x14-\x10\x00\x02\x10^\x0e\x0ct\x00\x04&-\x80@\x00\x10\x00\x00\x12-\x10\x00\x00\x08\x00\x03\x8e\x00\x00\x00\x00-( \x02p\x00d\x84t\x00b\x8c\t\xf8@\x00! \x04\x02\x08\x00@T \x00\xb0{\x04\x00\x10\x8e\xc6]\x0e\x0c- \x00\x02\xf5\xff@P\x08\x00\x03\x8e-\x10\x00\x00 \x00\xb0{\x10\x00\xb1{\x00\x00\xbf\xdf\x08\x00\xe0\x030\x00\xbd'\x
... [11588 chars]
```

## [13] Survey PS2Recomp VU-related files
```
ls -R /tmp/PS2Recomp/ps2xRecomp /tmp/PS2Recomp/ps2xRuntime 2>/dev/null | head -n 80; echo ===; grep -ri -l "vu1\|microcode\|vif\|VIF" /tmp/PS2Recomp --include="*.cpp" --include="*.h" --include="*.md" | head -n 30
```
output:
```
/tmp/PS2Recomp/ps2xRecomp:
CMakeLists.txt
include
src
tools

/tmp/PS2Recomp/ps2xRecomp/include:
ps2recomp

/tmp/PS2Recomp/ps2xRecomp/include/ps2recomp:
code_generator.h
codegen_helpers.h
config_manager.h
control_flow_analyzer.h
control_flow_utils.h
elf_parser.h
Emitters
gif_dma_kick_analyzer.h
instructions.h
ps2_recompiler.h
r5900_decoder.h
recompiler_reporter.h
Translators
types.h

/tmp/PS2Recomp/ps2xRecomp/include/ps2recomp/Emitters:
control_flow_emitter.h
function_emitter.h
function_table_emitter.h

/tmp/PS2Recomp/ps2xRecomp/include/ps2recomp/Translators:
cop0_translator.h
fpu_translator.h
instruction_translator.h
mmi_translator.h
regimm_translator.h
special_translator.h
vu_translator.h

/tmp/PS2Recomp/ps2xRecomp/src:
lib
runner

/tmp/PS2Recomp/ps2xRecomp/src/lib:
code_generator.cpp
config_manager.cpp
control_flow_analyzer.cpp
control_flow_emitter.cpp
cop0_translator.cpp
elf_parser.cpp
fpu_translator.cpp
function_emitter.cpp
function_table_emitter.cpp
gif_dma_kick_analyzer.cpp
instruction_translator.cpp
jump_table_switch_emitter.cpp
mmi_translation_helpers.cpp
mmi_translator.cpp
ps2_recompiler.cpp
r5900_decoder.cpp
recompiler_reporter.cpp
regimm_translator.cpp
special_translator.cpp
vu_translation_helpers.cpp
vu_translator.cpp

/tmp/PS2Recomp/ps2xRecomp/src/runner:
main.cpp

/tmp/PS2Recomp/ps2xRecomp/tools:
ghidra

/tmp/PS2Recomp/ps2xRecomp/tools/ghidra:
ExportPS2Functions.java

/tmp/PS2Recomp/ps2xRuntime:
cmake
CMakeLists.txt
include
Readme.md
===
/tmp/PS2Recomp/ps2xRecomp/include/ps2recomp/instructions.h
/tmp/PS2Recomp/ps2xRecomp/src/lib/r5900_decoder.cpp
/tmp/PS2Recomp/ps2xRecomp/src/lib/mmi_translator.cpp
/tmp/PS2Recomp/ps2xTest/src/ps2_vu1_tests.cpp
/tmp/PS2Recomp/ps2xTest/src/ps2_memory_tests.cpp
/tmp/PS2Recomp/ps2xTest/src/main.cpp
/tmp/PS2Recomp/ps2xTest/src/ps2_runtime_expansion_tests.cpp
/tmp/PS2Recomp/ps2xAnalyzer/include/ps2recomp/sce_symbol_database_data.h
/tmp/PS2Recomp/ps2xAnalyzer/src/function_classifier.cpp
/tmp/PS2Recomp/README.md
/tmp/PS2Recomp/ps2xRuntime/include/ps2_call_list.h
/tmp/PS2Recomp/ps2xRuntime/include/runtime/ps2_vu1.h
/tmp/PS2Recomp/ps2xRuntime/include/runtime/ps2_memory.h
/tmp/PS2Recomp/ps2xRuntime/include/runtime/ps2_address.h
/tmp/PS2Recomp/ps2xRuntime/include/ps2_runtime.h
/tmp/PS2Recomp/ps2xRuntime/src/lib/ps2_debug_panel.cpp
/tmp/PS2Recomp/ps2xRuntime/src/lib/ps2_vif1_interpreter.cpp
/tmp/PS2Recomp/ps2xRuntime/src/lib/ps2_runtime.cpp
/tmp/PS2Recomp/ps2xRuntime/src/lib/Kernel/Stubs/System.cpp
/tmp/PS2Recomp/ps2xRunt
... [2914 chars]
```

## [14] Dump VU string contexts correctly
```
python3 - <<'EOF'
import struct
with open('/tmp/SLUS_207.72','rb') as f:
    data = f.read()
# dump actual string file offsets
import re
for pat in [b'VU1', b'VIF1', b'VIF0', b'DMA', b'EAGL']:
    for m in re.finditer(re.escape(pat), data):
        o = m.start()
        print(f"--- {pat!r} @ fileoff {o} (0x{o:x}) ---")
        print(repr(data[o-160:o+240]))
        print()
EOF
```
output:
```
--- b'VU1' @ fileoff 3770263 (0x398797) ---
b'\x00\t<VIF1_STAT=%08x:\x00\x00\x00\x00\x00\x00\x00GIF_STAT=%08x>\r\n\x00\x00\x00\x00\x00\x00\x00\x00sceGsSyncPath: DMA Ch.2 does not terminate\r\n\x00\x00\x00\x00sceGsSyncPath: VIF1 does not terminate\r\n\x00\x00\x00\x00\x00\x00\x00\x00sceGsSyncPath: VU1 does not terminate\r\n\x00sceGsSyncPath: GIF does not terminate\r\n\x00libdma: sync timeout\n\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03\x00\x01\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0\xe6?\x00\xf4\xe6?\x00\xf4\xe6?\x00\xf0\xe6?\x00\xe4\xe6?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 \xec?\x00$\xec?\x00$\xec?\x00 \xec?\x00\x14\xec?\x00\x00\x00\x00'

--- b'VIF1' @ fileoff 3770106 (0x3986fa) ---
b' Ch.1 does not terminate\r\n\x00\x00\x00\x00\t<D1_CHCR=%08x:\x00D1_TADR=%08x:\x00\x00\x00D1_MADR=%08x:\x00\x00\x00D1_QWC=%08x>\r\n\x00\x00\t<D2_CHCR=%08x:\x00D2_TADR=%08x:\x00\x00\x00D2_MADR=%08x:\x00\x00\x00D2_QWC=%08x>\r\n\x00\x00\t<VIF1_STAT=%08x:\x00\x00\x00\x00\x00\x00\x00GIF_STAT=%08x>\r\n\x00\x00\x00\x00\x00\x00\x00\x00sceGsSyncPath: DMA Ch.2 does not terminate\r\n\x00\x00\x00\x00sceGsSyncPath: VIF1 does not terminate\r\n\x00\x00\x00\x00\x00\x00\x00\x00sceGsSyncPath: VU1 does not terminate\r\n\x00sceGsSyncPath: GIF does not terminate\r\n\x00libdma: sync timeo'

--- b'VIF1' @ fileoff 3770215 (0x398767) ---
b'\x00D2_TADR=%08x:\x00\x00\x00D2_MADR=%08x:\x00\x00\x00D2_QWC=%08x>\r\n\x00\x00\t<VIF1_STAT=%08x:\x00\x00\x00\x00\x00\x00\x00GIF_STAT=%08x>\r\n\x00\x00\x00\x00\x00\x00\x00\x00sceGsSyncPath: DMA Ch.2 does not terminate\r\n\x00\x00\x00\x00sceGsSyncPath: VIF1 does not terminate\r\n\x00\x00\x00\x00\x00\x00\x00\x00sceGsSyncPath: VU1 does not terminate\r\n\x00sceGsSyncPath: GIF does not terminate\r\n\x00libdma: sync timeout\n\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03\x00\x01\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0\xe6?\x00\xf4\xe6?'

--- b'DMA' @ file
... [5908 chars]
```

## [15] Measure VU runtime coverage files
```
wc -l /tmp/PS2Recomp/ps2xRuntime/src/lib/vu/*.cpp /tmp/PS2Recomp/ps2xRuntime/src/lib/vu/*.h /tmp/PS2Recomp/ps2xRuntime/src/lib/ps2_vif1_interpreter.cpp /tmp/PS2Recomp/ps2xRuntime/include/runtime/ps2_vu1.h /tmp/PS2Recomp/ps2xRecomp/src/lib/vu_translator.cpp /tmp/PS2Recomp/ps2xTest/src/ps2_vu1_tests.cpp; echo ===; grep -n "TODO\|unsupported\|not implemented\|Unimplemented\|stub" /tmp/PS2Recomp/ps2xRuntime/src/lib/vu/*.cpp /tmp/PS2Recomp/ps2xRuntime/src/lib/vu/*.h /tmp/PS2Recomp/ps2xRuntime/src/lib/ps2_vif1_interpreter.cpp | head -n 60
```
output:
```
  1838 /tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ps2_vu1_core.cpp
   789 /tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ps2_vu1_lower.cpp
   506 /tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ps2_vu1_upper.cpp
    29 /tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ps2_vu1_detail.h
   760 /tmp/PS2Recomp/ps2xRuntime/src/lib/ps2_vif1_interpreter.cpp
   299 /tmp/PS2Recomp/ps2xRuntime/include/runtime/ps2_vu1.h
   399 /tmp/PS2Recomp/ps2xRecomp/src/lib/vu_translator.cpp
  1716 /tmp/PS2Recomp/ps2xTest/src/ps2_vu1_tests.cpp
  6336 total
===

```

## [16] List VU1 upper/lower opcode dispatch
```
grep -n -E "case |Op[A-Z]|\"[A-Z_]+\ striking|exec[A-Z]" /tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ps2_vu1_upper.cpp | head -n 80; echo ===LOWER===; grep -n -E "case |Op[A-Z]" /tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ps2_vu1_lower.cpp | head -n 100
```
output:
```
24:void VU1Interpreter::execUpper(uint32_t instr)
53:    case 0x00:
54:    case 0x01:
55:    case 0x02:
56:    case 0x03: // ADDbc
64:    case 0x04:
65:    case 0x05:
66:    case 0x06:
67:    case 0x07: // SUBbc
75:    case 0x08:
76:    case 0x09:
77:    case 0x0A:
78:    case 0x0B: // MADDbc
86:    case 0x0C:
87:    case 0x0D:
88:    case 0x0E:
89:    case 0x0F: // MSUBbc
97:    case 0x10:
98:    case 0x11:
99:    case 0x12:
100:    case 0x13: // MAXbc
108:    case 0x14:
109:    case 0x15:
110:    case 0x16:
111:    case 0x17: // MINIbc
119:    case 0x18:
120:    case 0x19:
121:    case 0x1A:
122:    case 0x1B: // MULbc
130:    case 0x1C: // MULq
135:    case 0x1D: // MAXi
140:    case 0x1E: // MULi
145:    case 0x1F: // MINIi
150:    case 0x20: // ADDq
155:    case 0x21: // MADDq
160:    case 0x22: // ADDi
165:    case 0x23: // MADDi
170:    case 0x24: // SUBq
175:    case 0x25: // MSUBq
180:    case 0x26: // SUBi
185:    case 0x27: // MSUBi
190:    case 0x28: // ADD
195:    case 0x29: // MADD
200:    case 0x2A: // MUL
205:    case 0x2B: // MAX
210:    case 0x2C: // SUB
215:    case 0x2D: // MSUB
220:    case 0x2E: // OPMSUB
227:    case 0x2F: // MINI
237:    case 0x3C:
238:    case 0x3D:
239:    case 0x3E:
240:    case 0x3F:
247:        case 0x00:
248:        case 0x01:
249:        case 0x02:
250:        case 0x03: // ADDAbc
258:        case 0x04:
259:        case 0x05:
260:        case 0x06:
261:        case 0x07: // SUBAbc
269:        case 0x08:
270:        case 0x09:
271:        case 0x0A:
272:        case 0x0B: // MADDAbc
280:        case 0x0C:
281:        case 0x0D:
282:        case 0x0E:
283:        case 0x0F: // MSUBAbc
291:        case 0x10: // ITOF0
300:        case 0x11: // ITOF4
309:        case 0x12: // ITOF12
318:        case 0x13: // ITOF15
327:        case 0x14: // FTOI0
335:        case 0x15: // FTOI4
343:        case 0x16: // FTOI12
351:        case 0x17: // FTOI15
359:        case 0x18:
360:        case 0x19:
361:        case 0x1A:
===LOWER===
84:    case 0x00: // LQ (Load Quadword from VU data memory)
100:    case 0x01: // SQ (Store Quadword to VU data memory)
116:    case 0x04: // ILW (Integer Load Word from VU data memory)
142:    case 0x05: // ISW (Integer Store Word to VU data memory)
158:    case 0x08: // IADDIU
167:    case 0x09: // ISUBIU
176:    case 0x10: // FCEQ
183:    case 0x11: // FCSET
188:    case 0x12: // FCAND
195:    case 0x13: // FCOR
202:    case 0x14: // FSEQ
210:    case 0x15: // FSSET
216:    case 0x16: // FSAND
... [5110 chars]
```

## [17] Find unhandled VU/VIF paths
```
grep -n -E "default|Unhandled|unknown|Unknown|TODO|FIXME" /tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ps2_vu1_upper.cpp /tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ps2_vu1_lower.cpp /tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ps2_vu1_core.cpp /tmp/PS2Recomp/ps2xRuntime/src/lib/ps2_vif1_interpreter.cpp | head -n 40
```
output:
```
/tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ps2_vu1_upper.cpp:492:        default:
/tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ps2_vu1_upper.cpp:502:    default:
/tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ps2_vu1_lower.cpp:775:            default:
/tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ps2_vu1_lower.cpp:780:        default:
/tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ps2_vu1_lower.cpp:785:    default:
/tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ps2_vu1_core.cpp:320:            default:
/tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ps2_vu1_core.cpp:395:        default:
/tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ps2_vu1_core.cpp:1288:    default:
/tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ps2_vu1_core.cpp:1480:        default:
/tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ps2_vu1_core.cpp:1503:    default:
/tmp/PS2Recomp/ps2xRuntime/src/lib/ps2_vif1_interpreter.cpp:178:            default:
/tmp/PS2Recomp/ps2xRuntime/src/lib/ps2_vif1_interpreter.cpp:517:            default:
/tmp/PS2Recomp/ps2xRuntime/src/lib/ps2_vif1_interpreter.cpp:690:                    // Unknown compressed format fallback: preserve legacy raw-copy behavior.

```

## [18] Read VU upper dispatch header, search long-tail note
```
sed -n 1,60p /tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ps2_vu1_upper.cpp; echo =====; grep -rn -i "long tail\|not cover\|out of scope\|unsupported" /tmp/PS2Recomp --include="*.md" | head -n 20
```
output:
```
#include "runtime/ps2_vu1.h"
#include "ps2_vu1_detail.h"

#include <cmath>
#include <cstring>
#include <limits>

namespace
{
    int32_t vuFloatToInt(float value, float scale)
    {
        const double scaled = static_cast<double>(value) * static_cast<double>(scale);
        if (scaled >= static_cast<double>(std::numeric_limits<int32_t>::max()))
            return std::numeric_limits<int32_t>::max();
        if (scaled <= static_cast<double>(std::numeric_limits<int32_t>::min()))
            return std::numeric_limits<int32_t>::min();
        return static_cast<int32_t>(scaled);
    }
}

// ============================================================================
// Upper instructions (FMAC pipeline)
// ============================================================================
void VU1Interpreter::execUpper(uint32_t instr)
{
    m_currentUpperInstruction = instr;
    uint8_t dest = DEST(instr);
    uint8_t ft = FT(instr);
    uint8_t fs = FS(instr);
    uint8_t fd = FD(instr);
    uint8_t op = instr & 0x3F;

    float *vd = m_state.vf[fd];
    float normalizedVs[4];
    float normalizedVt[4];
    float normalizedAcc[4];
    for (uint32_t component = 0; component < 4u; ++component)
    {
        normalizedVs[component] = normalizeOperand(m_state.vf[fs][component]);
        normalizedVt[component] = normalizeOperand(m_state.vf[ft][component]);
        normalizedAcc[component] = normalizeOperand(m_state.acc[component]);
    }
    const float *vs = normalizedVs;
    const float *vt = normalizedVt;
    const float *acc = normalizedAcc;
    const float q = normalizeOperand(m_state.q);
    const float i = normalizeOperand(m_state.i);
    float result[4];

    // Upper opcode decoding (bits 5:0 of upper word)
    switch (op)
    {
    case 0x00:
    case 0x01:
    case 0x02:
    case 0x03: // ADDbc
    {
        float bc = broadcast(vt, op & 3);
        for (int c = 0; c < 4; c++)
            result[c] = vs[c] + bc;
=====
/tmp/PS2Recomp/ps2xIOP/README.md:156:incompatible ABI versions, malformed descriptors, and unsupported modules are
/tmp/PS2Recomp/ps2xIOP/PluginExample.md:90:        return PS2X_IOP_STATUS_UNSUPPORTED_V1;
/tmp/PS2Recomp/ps2xIOP/PluginExample.md:150:        return PS2X_IOP_STATUS_UNSUPPORTED_V1;

```

## [19] Extract VU sections to files
```
python3 - <<'EOF'
import struct
with open('/tmp/SLUS_207.72','rb') as f:
    data = f.read()
e_shoff = struct.unpack('<I', data[32:36])[0]
e_shnum = struct.unpack('<H', data[48:50])[0]
e_shstrndx = struct.unpack('<H', data[50:52])[0]
shstr_off = struct.unpack('<I', data[e_shoff+e_shstrndx*40+16:e_shoff+e_shstrndx*40+20])[0]
def secname(off):
    end = data.index(b'\x00', shstr_off+off)
    return data[shstr_off+off:end].decode('ascii', errors='replace')
import os
os.makedirs('/tmp/ssx3vu', exist_ok=True)
total=0
groups={}
for i in range(e_shnum):
    sh = data[e_shoff+i*40:e_shoff+(i+1)*40]
    name, stype, flags, addr, off, size, link, info, align, entsz = struct.unpack('<IIIIIIIIII', sh)
    n = secname(name)
    if n.startswith('.DVP') or n in ('.vutext','.vudata'):
        blob = data[off:off+size]
        fn = f"/tmp/ssx3vu/sec{i:02d}_{n.replace('/','_').replace(chr(0),'')}.bin"
        open(fn,'wb').write(blob)
        total+=size
        print(f"{i:2d} {n:45s} size={size:6d} -> {fn}")
        # group key: fields of overlay name
        parts = n.split('.')
        groups.setdefault(tuple(parts[2:5]), []).append((i,size))
print("total VU bytes:", total)
print()
for k,v in groups.items():
    print(k, f"{len(v)} sections, {sum(s for _,s in v)} bytes")
EOF
```
output:
```
32 .vutext                                       size= 59360 -> /tmp/ssx3vu/sec32_.vutext.bin
39 .vudata                                       size=     0 -> /tmp/ssx3vu/sec39_.vudata.bin
47 .DVP                                          size=  1557 -> /tmp/ssx3vu/sec47_.DVP.bin
48 .DVP.overlay..0x0.3337891.38.0                size=  2048 -> /tmp/ssx3vu/sec48_.DVP.overlay..0x0.3337891.38.0.bin
49 .DVP.overlay..0x800.3886870251.940.1          size=  2048 -> /tmp/ssx3vu/sec49_.DVP.overlay..0x800.3886870251.940.1.bin
50 .DVP.overlay..0x1000.3886870251.1477.2        size=  2048 -> /tmp/ssx3vu/sec50_.DVP.overlay..0x1000.3886870251.1477.2.bin
51 .DVP.overlay..0x1800.3886870251.2009.3        size=  2048 -> /tmp/ssx3vu/sec51_.DVP.overlay..0x1800.3886870251.2009.3.bin
52 .DVP.overlay..0x2000.3886870251.2588.4        size=  1184 -> /tmp/ssx3vu/sec52_.DVP.overlay..0x2000.3886870251.2588.4.bin
53 .DVP.overlay..0x0.26713891.32.0               size=  2048 -> /tmp/ssx3vu/sec53_.DVP.overlay..0x0.26713891.32.0.bin
54 .DVP.overlay..0x800.4091075227.14.1           size=  2048 -> /tmp/ssx3vu/sec54_.DVP.overlay..0x800.4091075227.14.1.bin
55 .DVP.overlay..0x1000.1030201195.1372.2        size=  2048 -> /tmp/ssx3vu/sec55_.DVP.overlay..0x1000.1030201195.1372.2.bin
56 .DVP.overlay..0x1800.1030201195.1761.3        size=  2048 -> /tmp/ssx3vu/sec56_.DVP.overlay..0x1800.1030201195.1761.3.bin
57 .DVP.overlay..0x2000.1030201195.2132.4        size=  2048 -> /tmp/ssx3vu/sec57_.DVP.overlay..0x2000.1030201195.2132.4.bin
58 .DVP.overlay..0x2800.1030201195.2786.5        size=  2048 -> /tmp/ssx3vu/sec58_.DVP.overlay..0x2800.1030201195.2786.5.bin
59 .DVP.overlay..0x3000.1030201195.3472.6        size=  2048 -> /tmp/ssx3vu/sec59_.DVP.overlay..0x3000.1030201195.3472.6.bin
60 .DVP.overlay..0x3800.1030201195.3990.7        size=  1704 -> /tmp/ssx3vu/sec60_.DVP.overlay..0x3800.1030201195.3990.7.bin
61 .DVP.overlay..0x0.108067.33.0                 size=  2048 -> /tmp/ssx3vu/sec61_.DVP.overlay..0x0.108067.33.0.bin
62 .DVP.overlay..0x800.4091089323.11.1           size=  2048 -> /tmp/ssx3vu/sec62_.DVP.overlay..0x800.4091089323.11.1.bin
63 .DVP.overlay..0x1000.3476914539.125.2         size=   512 -> /tmp/ssx3vu/sec63_.DVP.overlay..0x1000.3476914539.125.2.bin
64 .DVP.overlay..0x0.108323.38.0                 size=  2048 -> /tmp/ssx3vu/sec64_.DVP.overlay..0x0.108323.38.0.bin
65 .DVP.overlay..0x800.3887216411.266.1          size=  2048 -> /tmp/ssx3vu/sec65_.DVP.overlay..0x800.3887216411.266.1.bin
66 .DVP.overlay
... [4638 chars]
```

## [20] Histogram VU blobs vs recomp decoder
```
python3 /tmp/ssx3vu/histogram.py
```
output:
```
file                                instr   impl  resvd  Ebit
sec32_.vutext.bin                    7420  14792     48    44  (59360 bytes)
sec39_.vudata.bin                       0      0      0     0  (0 bytes)
sec47_.DVP.bin                        194    233    155     0  (1557 bytes)
sec48_.DVP.overlay..0x0.3337891.38    256    512      0     0  (2048 bytes)
sec49_.DVP.overlay..0x800.38868702    256    512      0     0  (2048 bytes)
sec50_.DVP.overlay..0x1000.3886870    256    512      0     0  (2048 bytes)
sec51_.DVP.overlay..0x1800.3886870    256    512      0     0  (2048 bytes)
sec52_.DVP.overlay..0x2000.3886870    148    296      0     0  (1184 bytes)
sec53_.DVP.overlay..0x0.26713891.3    256    512      0     0  (2048 bytes)
sec54_.DVP.overlay..0x800.40910752    256    512      0     0  (2048 bytes)
sec55_.DVP.overlay..0x1000.1030201    256    512      0     0  (2048 bytes)
sec56_.DVP.overlay..0x1800.1030201    256    512      0     0  (2048 bytes)
sec57_.DVP.overlay..0x2000.1030201    256    512      0     0  (2048 bytes)
sec58_.DVP.overlay..0x2800.1030201    256    512      0     0  (2048 bytes)
sec59_.DVP.overlay..0x3000.1030201    256    512      0     0  (2048 bytes)
sec60_.DVP.overlay..0x3800.1030201    213    426      0     0  (1704 bytes)
sec61_.DVP.overlay..0x0.108067.33.    256    512      0     0  (2048 bytes)
sec62_.DVP.overlay..0x800.40910893    256    512      0     0  (2048 bytes)
sec63_.DVP.overlay..0x1000.3476914     64    128      0     0  (512 bytes)
sec64_.DVP.overlay..0x0.108323.38.    256    512      0     0  (2048 bytes)
sec65_.DVP.overlay..0x800.38872164    256    512      0     0  (2048 bytes)
sec66_.DVP.overlay..0x1000.3476911    256    512      0     0  (2048 bytes)
sec67_.DVP.overlay..0x1800.3476911    256    512      0     0  (2048 bytes)
sec68_.DVP.overlay..0x2000.3476911    256    512      0     0  (2048 bytes)
sec69_.DVP.overlay..0x2800.3476911    256    512      0     0  (2048 bytes)
sec70_.DVP.overlay..0x3000.3476911    256    512      0     0  (2048 bytes)
sec71_.DVP.overlay..0x3800.3887078    193    386      0     0  (1544 bytes)
sec72_.DVP.overlay..0x0.114211.91.    256    512      0     0  (2048 bytes)
sec73_.DVP.overlay..0x800.38871889    256    512      0     0  (2048 bytes)
sec74_.DVP.overlay..0x1000.2663826    256    512      0     0  (2048 bytes)
sec75_.DVP.overlay..0x1800.3479152     36     72      0     0  (288 bytes)
sec76_.DVP.overlay..0x0.115107.53.    256    512      0     0  (2048 bytes)
sec77_.DVP
... [7006 chars]
```

## [21] Inspect vutext structure around anomalies
```
python3 - <<'EOF'
import struct
blob = open('/tmp/ssx3vu/sec32_.vutext.bin','rb').read()
n = len(blob)//8
def show(i):
    lo, hi = struct.unpack_from('<II', blob, i*8)
    e = 'E' if hi & 0x80000000 else '.'
    print(f"  #{i:5d} up={hi:08x} lo={lo:08x} {e}")
print("== start ==")
for i in range(0, 8): show(i)
print("== around 1182 ==")
for i in range(1179, 1187): show(i)
print("== around 3784 ==")
for i in range(3781, 3792): show(i)
print("== E-bit positions (first 40) ==")
eb = [i for i in range(n) if struct.unpack_from('<I', blob, i*8+4)[0] & 0x80000000]
print(eb[:40])
print("total E:", len(eb))
print("== 7385..7420 (tail) ==")
for i in range(7385, n): show(i)
EOF
```
output:
```
== start ==
  #    0 up=00000000 lo=6000024e .
  #    1 up=20000000 lo=01000404 .
  #    2 up=05000000 lo=00000000 .
  #    3 up=020000d8 lo=03000250 .
  #    4 up=4a000000 lo=00000000 .
  #    5 up=000002ff lo=800106bc .
  #    6 up=000002ff lo=0b0101fe .
  #    7 up=000002ff lo=10020004 .
== around 1182 ==
  # 1179 up=000002ff lo=48007000 .
  # 1180 up=000002ff lo=8000033c .
  # 1181 up=00000000 lo=00000000 .
  # 1182 up=00000000 lo=600003f0 .
  # 1183 up=20000000 lo=01000404 .
  # 1184 up=05000000 lo=00000000 .
  # 1185 up=020000d8 lo=03000250 .
  # 1186 up=4a000000 lo=00000000 .
== around 3784 ==
  # 3781 up=400002ff lo=03e00810 .
  # 3782 up=000002ff lo=8000033c .
  # 3783 up=00000000 lo=00000000 .
  # 3784 up=00000000 lo=600003e6 .
  # 3785 up=20000000 lo=01000404 .
  # 3786 up=05000000 lo=00000000 .
  # 3787 up=020001b6 lo=03000026 .
  # 3788 up=4a000000 lo=00000000 .
  # 3789 up=100002ff lo=8000033c .
  # 3790 up=000002ff lo=800c68f0 .
  # 3791 up=000002ff lo=81d26b7c .
== E-bit positions (first 40) ==
[106, 1261, 3328, 3478, 3583, 3767, 3874, 4075, 4872, 4876, 5523, 5795, 5829, 5870, 5873, 5903, 5955, 5957, 6027, 6030, 6061, 6114, 6116, 6160, 6162, 6190, 6193, 6223, 6276, 6278, 6335, 6347, 6362, 6364, 6394, 6452, 6461, 6465, 6544, 6741]
total E: 44
== 7385..7420 (tail) ==
  # 7385 up=000002ff lo=8000033c .
  # 7386 up=400002ff lo=10010002 .
  # 7387 up=000002ff lo=8000033c .
  # 7388 up=400002ff lo=10010000 .
  # 7389 up=000002ff lo=8000033c .
  # 7390 up=00000000 lo=70000000 .
  # 7391 up=00000000 lo=00000000 .
  # 7392 up=00000000 lo=70000000 .
  # 7393 up=00000000 lo=00000000 .
  # 7394 up=00000000 lo=1000000b .
  # 7395 up=00000000 lo=00000000 .
  # 7396 up=6c0a0010 lo=01000404 .
  # 7397 up=00000000 lo=00000000 .
  # 7398 up=3f800000 lo=00000000 .
  # 7399 up=3c4a4588 lo=3ab3cc07 .
  # 7400 up=3f800000 lo=3de38e39 .
  # 7401 up=3d4a4588 lo=3c33cc07 .
  # 7402 up=3f800000 lo=3e638e39 .
  # 7403 up=3de38e39 lo=3d17b426 .
  # 7404 up=3f800000 lo=3eaaaaaa .
  # 7405 up=3e4a4588 lo=3db3cc07 .
  # 7406 up=3f800000 lo=3ee38e39 .
  # 7407 up=3e9e0652 lo=3e2f953f .
  # 7408 up=3f800000 lo=3f0e38e3 .
  # 7409 up=3ee38e39 lo=3e97b426 .
  # 7410 up=3f800000 lo=3f2aaaaa .
  # 7411 up=3f1add3c lo=3ef0e65d .
  # 7412 up=3f800000 lo=3f471c71 .
  # 7413 up=3f4a4588 lo=3f33cc07 .
  # 7414 up=3f800000 lo=3f638e39 .
  # 7415 up=3f800000 lo=3f800000 .
  # 7416 up=3f800000 lo=3f800000 .
  # 7417 up=00000000 lo=00000000 .
  # 7418 up=00000000 lo=70000000 .
  # 7419
... [2527 chars]
```

## [22] Parse VIF stream, histogram true VU code
```
python3 /tmp/ssx3vu/parse_vif.py 2>&1 | head -n 120
```
output:
```
file                                instr   impl  resvd  Ebit
sec32_.vutext.bin                    7420  14792     48    44  (59360 bytes)
sec39_.vudata.bin                       0      0      0     0  (0 bytes)
sec47_.DVP.bin                        194    233    155     0  (1557 bytes)
sec48_.DVP.overlay..0x0.3337891.38    256    512      0     0  (2048 bytes)
sec49_.DVP.overlay..0x800.38868702    256    512      0     0  (2048 bytes)
sec50_.DVP.overlay..0x1000.3886870    256    512      0     0  (2048 bytes)
sec51_.DVP.overlay..0x1800.3886870    256    512      0     0  (2048 bytes)
sec52_.DVP.overlay..0x2000.3886870    148    296      0     0  (1184 bytes)
sec53_.DVP.overlay..0x0.26713891.3    256    512      0     0  (2048 bytes)
sec54_.DVP.overlay..0x800.40910752    256    512      0     0  (2048 bytes)
sec55_.DVP.overlay..0x1000.1030201    256    512      0     0  (2048 bytes)
sec56_.DVP.overlay..0x1800.1030201    256    512      0     0  (2048 bytes)
sec57_.DVP.overlay..0x2000.1030201    256    512      0     0  (2048 bytes)
sec58_.DVP.overlay..0x2800.1030201    256    512      0     0  (2048 bytes)
sec59_.DVP.overlay..0x3000.1030201    256    512      0     0  (2048 bytes)
sec60_.DVP.overlay..0x3800.1030201    213    426      0     0  (1704 bytes)
sec61_.DVP.overlay..0x0.108067.33.    256    512      0     0  (2048 bytes)
sec62_.DVP.overlay..0x800.40910893    256    512      0     0  (2048 bytes)
sec63_.DVP.overlay..0x1000.3476914     64    128      0     0  (512 bytes)
sec64_.DVP.overlay..0x0.108323.38.    256    512      0     0  (2048 bytes)
sec65_.DVP.overlay..0x800.38872164    256    512      0     0  (2048 bytes)
sec66_.DVP.overlay..0x1000.3476911    256    512      0     0  (2048 bytes)
sec67_.DVP.overlay..0x1800.3476911    256    512      0     0  (2048 bytes)
sec68_.DVP.overlay..0x2000.3476911    256    512      0     0  (2048 bytes)
sec69_.DVP.overlay..0x2800.3476911    256    512      0     0  (2048 bytes)
sec70_.DVP.overlay..0x3000.3476911    256    512      0     0  (2048 bytes)
sec71_.DVP.overlay..0x3800.3887078    193    386      0     0  (1544 bytes)
sec72_.DVP.overlay..0x0.114211.91.    256    512      0     0  (2048 bytes)
sec73_.DVP.overlay..0x800.38871889    256    512      0     0  (2048 bytes)
sec74_.DVP.overlay..0x1000.2663826    256    512      0     0  (2048 bytes)
sec75_.DVP.overlay..0x1800.3479152     36     72      0     0  (288 bytes)
sec76_.DVP.overlay..0x0.115107.53.    256    512      0     0  (2048 bytes)
sec77_.DVP
... [8544 chars]
```

## [23] Show MPG payload histogram results
```
python3 /tmp/ssx3vu/parse_vif.py 2>&1 | sed -n '/MPG payload/,$p' | head -n 100
```
output:
```
=== MPG payload: 7305 half-instructions ===
reserved hits: 16
  mpg@0100+121: 800002ff3f000000 L:RESERVED(ophi=0x1f)
  mpg@0600+192: 81102d8a3f000000 L:RESERVED(ophi=0x1f)
  mpg@0000+8: 81e590bebf3ae148 L:RESERVED(ophi=0x5f)
  mpg@0000+42: 81facc0b3de76c8b L:RESERVED(ophi=0x1e)
  mpg@0000+168: 800002ffbf3ae148 L:RESERVED(ophi=0x5f)
  mpg@0000+170: 810003623de76c8b L:RESERVED(ophi=0x1e)
  mpg@0100+70: 800002ffbf3ae148 L:RESERVED(ophi=0x5f)
  mpg@0100+72: 810003623de76c8b L:RESERVED(ophi=0x1e)
  mpg@0100+116: 81ce9e883b808081 L:RESERVED(ophi=0x1d)
  mpg@0100+232: 800002ffbf3ae148 L:RESERVED(ophi=0x5f)
  mpg@0100+234: 810003623de76c8b L:RESERVED(ophi=0x1e)
  mpg@0200+34: 81ce20be3f000000 L:RESERVED(ophi=0x1f)
  mpg@0200+160: 8020045e3fc00000 L:RESERVED(ophi=0x1f)
  mpg@0200+164: 8020041e3f85a5a5 L:RESERVED(ophi=0x1f)
  mpg@0000+132: 800002ff3f4ccccd L:RESERVED(ophi=0x1f)
  mpg@0000+138: 8020035e3e99999a L:RESERVED(ophi=0x1f)

=== opcode usage inside MPG payloads (top 40) ===
   4197  U:NOP
   2215  L:NOP
    983  L:LQ
    884  L:IADDIU
    611  U:MADDAbc
    429  U:MULAbc
    376  L:SQ
    356  U:MADDbc
    269  L:ILW
    253  L:SQI
    221  L:LQI
    182  L:IBNE
    180  L:BAL
    164  L:IADD
    160  U:ADDbc
    149  U:MUL
    147  U:MULq
    125  L:DIV
    125  L:IBEQ
    120  U:CLIP
    112  U:SUB
    108  L:ISUBIU
    102  U:MADD
     94  L:MOVE
     84  U:SUBbc
     83  L:ISW
     79  L:MFIR
     74  U:MAXbc
     74  U:FTOI4
     74  L:B
     72  U:MULbc
     70  L:JR
     70  L:FCOR
     70  U:ITOF15
     68  L:FCAND
     62  L:XTOP
     55  L:MTIR
     53  L:RNEXT
     52  L:IADDI
     47  L:XGKICK

 distinct implemented ops used: 85

```

## [24] Validate MPG payload window alignment
```
python3 - <<'EOF'
import struct
blob = open('/tmp/ssx3vu/sec32_.vutext.bin','rb').read()
words = struct.unpack(f'<{len(blob)//4}I', blob)
KNOWN = {0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x10,0x11,0x13,0x14,0x15,0x17,0x20,0x30,0x31,0x4A,0x50,0x51}
def isvif(w): return ((w>>24) in KNOWN) or (0x60 <= (w>>24) <= 0x7F)
for i,w in enumerate(words):
    if (w>>24) == 0x4A:
        num = (w>>16)&0xFF
        n = num if num else 256
        end = (i+1)+n*2  # word index after payload
        nxt = words[end] if end < len(words) else None
        nxt2 = words[end+1] if end+1 < len(words) else None
        print(f"MPG word#{i} num={n}: end_word#{end} = {nxt:08x} vif={isvif(nxt) if nxt is not None else '-'} next={nxt2:08x if nxt2 is not None else '-'}")
# also: what is word#522 (gap) and words around the float artifacts?
print()
print("word#522:", f"{words[522]:08x}")
for idx in [2373+1+42, 2373+1+132, 2373+1+168]:
    lo, hi = words[idx*2], words[idx*2+1]
    print(f"payload unit +{idx-2374}: up={hi:08x} lo={lo:08x}")
EOF
```
output:
```
Traceback (most recent call last):
  File "<stdin>", line 13, in <module>
ValueError: Invalid format specifier '08x if nxt2 is not None else '-'' for object of type 'int'

```

## [25] Validate MPG payload window alignment
```
python3 - <<'EOF'
import struct
blob = open('/tmp/ssx3vu/sec32_.vutext.bin','rb').read()
words = struct.unpack(f'<{len(blob)//4}I', blob)
KNOWN = {0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x10,0x11,0x13,0x14,0x15,0x17,0x20,0x30,0x31,0x4A,0x50,0x51}
def isvif(w): return ((w>>24) in KNOWN) or (0x60 <= (w>>24) <= 0x7F)
for i,w in enumerate(words):
    if (w>>24) == 0x4A:
        num = (w>>16)&0xFF
        n = num if num else 256
        end = (i+1)+n*2
        nxt = words[end] if end < len(words) else 0
        nxt2 = words[end+1] if end+1 < len(words) else 0
        print(f"MPG word#{i} num={n}: end_word#{end} = {nxt:08x} vif={isvif(nxt)} next2={nxt2:08x}")
print()
print("word#522:", f"{words[522]:08x}")
EOF
```
output:
```
MPG word#9 num=256: end_word#522 = 00000000 vif=True next2=4a000100
MPG word#523 num=256: end_word#1036 = 00000000 vif=True next2=4a000200
MPG word#1037 num=256: end_word#1550 = 00000000 vif=True next2=4a000300
MPG word#1551 num=256: end_word#2064 = 00000000 vif=True next2=4a940400
MPG word#2065 num=148: end_word#2362 = 00000000 vif=True next2=00000000
MPG word#2373 num=256: end_word#2886 = 00000000 vif=True next2=4a000100
MPG word#2887 num=256: end_word#3400 = 00000000 vif=True next2=4a000200
MPG word#3401 num=256: end_word#3914 = 00000000 vif=True next2=4a000300
MPG word#3915 num=256: end_word#4428 = 00000000 vif=True next2=4a000400
MPG word#4429 num=256: end_word#4942 = 00000000 vif=True next2=4a000500
MPG word#4943 num=256: end_word#5456 = 00000000 vif=True next2=4a000600
MPG word#5457 num=256: end_word#5970 = 00000000 vif=True next2=4ad50700
MPG word#5971 num=213: end_word#6398 = 00000000 vif=True next2=00000000
MPG word#6409 num=256: end_word#6922 = 00000000 vif=True next2=4a000100
MPG word#6923 num=256: end_word#7436 = 00000000 vif=True next2=4a400200
MPG word#7437 num=64: end_word#7566 = 00000000 vif=True next2=00000000
MPG word#7577 num=256: end_word#8090 = 00000000 vif=True next2=4a000100
MPG word#8091 num=256: end_word#8604 = 00000000 vif=True next2=4a000200
MPG word#8605 num=256: end_word#9118 = 00000000 vif=True next2=4a000300
MPG word#9119 num=256: end_word#9632 = 00000000 vif=True next2=4a000400
MPG word#9633 num=256: end_word#10146 = 00000000 vif=True next2=4a000500
MPG word#10147 num=256: end_word#10660 = 00000000 vif=True next2=4a000600
MPG word#10661 num=256: end_word#11174 = 00000000 vif=True next2=4ac10700
MPG word#11175 num=193: end_word#11562 = 00000000 vif=True next2=00000000
MPG word#11573 num=256: end_word#12086 = 00000000 vif=True next2=4a000100
MPG word#12087 num=256: end_word#12600 = 00000000 vif=True next2=4a000200
MPG word#12601 num=256: end_word#13114 = 00000000 vif=True next2=4a240300
MPG word#13115 num=36: end_word#13188 = 11000000 vif=True next2=00000000
MPG word#13217 num=256: end_word#13730 = 00000000 vif=True next2=4a130100
MPG word#13731 num=19: end_word#13770 = 00000000 vif=True next2=00000000
MPG word#13801 num=256: end_word#14314 = 00000000 vif=True next2=4ae80100
MPG word#14315 num=232: end_word#14780 = 70000000 vif=True next2=00000000

word#522: 00000000

```

## [26] Dump VU program context around float words
```
python3 - <<'EOF'
import struct, sys
sys.path.insert(0,'/tmp/ssx3vu')
from histogram import classify_upper, classify_lower
blob = open('/tmp/ssx3vu/sec32_.vutext.bin','rb').read()
words = struct.unpack(f'<{len(blob)//4}I', blob)
base = 2373  # MPG word# for group3 prog (load 0x0000)
def unit(k):
    wi = (base+1)+k*2
    lo, hi = words[wi], words[wi+1]
    ou, tu = classify_upper(hi); ol, tl = classify_lower(lo)
    e = 'E' if hi & 0x80000000 else '.'
    print(f"  +{k:3d} up={hi:08x} lo={lo:08x} {e}  {tu:12s} {tl:12s}")
print("group3 units +120..+180:")
for k in range(120,181): unit(k)
EOF
```
output:
```
file                                instr   impl  resvd  Ebit
sec32_.vutext.bin                    7420  14792     48    44  (59360 bytes)
sec39_.vudata.bin                       0      0      0     0  (0 bytes)
sec47_.DVP.bin                        194    233    155     0  (1557 bytes)
sec48_.DVP.overlay..0x0.3337891.38    256    512      0     0  (2048 bytes)
sec49_.DVP.overlay..0x800.38868702    256    512      0     0  (2048 bytes)
sec50_.DVP.overlay..0x1000.3886870    256    512      0     0  (2048 bytes)
sec51_.DVP.overlay..0x1800.3886870    256    512      0     0  (2048 bytes)
sec52_.DVP.overlay..0x2000.3886870    148    296      0     0  (1184 bytes)
sec53_.DVP.overlay..0x0.26713891.3    256    512      0     0  (2048 bytes)
sec54_.DVP.overlay..0x800.40910752    256    512      0     0  (2048 bytes)
sec55_.DVP.overlay..0x1000.1030201    256    512      0     0  (2048 bytes)
sec56_.DVP.overlay..0x1800.1030201    256    512      0     0  (2048 bytes)
sec57_.DVP.overlay..0x2000.1030201    256    512      0     0  (2048 bytes)
sec58_.DVP.overlay..0x2800.1030201    256    512      0     0  (2048 bytes)
sec59_.DVP.overlay..0x3000.1030201    256    512      0     0  (2048 bytes)
sec60_.DVP.overlay..0x3800.1030201    213    426      0     0  (1704 bytes)
sec61_.DVP.overlay..0x0.108067.33.    256    512      0     0  (2048 bytes)
sec62_.DVP.overlay..0x800.40910893    256    512      0     0  (2048 bytes)
sec63_.DVP.overlay..0x1000.3476914     64    128      0     0  (512 bytes)
sec64_.DVP.overlay..0x0.108323.38.    256    512      0     0  (2048 bytes)
sec65_.DVP.overlay..0x800.38872164    256    512      0     0  (2048 bytes)
sec66_.DVP.overlay..0x1000.3476911    256    512      0     0  (2048 bytes)
sec67_.DVP.overlay..0x1800.3476911    256    512      0     0  (2048 bytes)
sec68_.DVP.overlay..0x2000.3476911    256    512      0     0  (2048 bytes)
sec69_.DVP.overlay..0x2800.3476911    256    512      0     0  (2048 bytes)
sec70_.DVP.overlay..0x3000.3476911    256    512      0     0  (2048 bytes)
sec71_.DVP.overlay..0x3800.3887078    193    386      0     0  (1544 bytes)
sec72_.DVP.overlay..0x0.114211.91.    256    512      0     0  (2048 bytes)
sec73_.DVP.overlay..0x800.38871889    256    512      0     0  (2048 bytes)
sec74_.DVP.overlay..0x1000.2663826    256    512      0     0  (2048 bytes)
sec75_.DVP.overlay..0x1800.3479152     36     72      0     0  (288 bytes)
sec76_.DVP.overlay..0x0.115107.53.    256    512      0     0  (2048 bytes)
sec77_.DVP
... [10691 chars]
```

## [27] Check runtime LOI immediate support
```
grep -rn -i "loi\b\|0x8000033c\|load immediate" /tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ /tmp/PS2Recomp/ps2xRuntime/include/runtime/ps2_vu1.h /tmp/PS2Recomp/ps2xTest/src/ps2_vu1_tests.cpp | head -n 20; echo ===; grep -n "m_state.i" /tmp/PS2Recomp/ps2xRuntime/src/lib/vu/*.cpp | head -n 20
```
output:
```
/tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ps2_vu1_lower.cpp:75:    if (instr == 0x00000000 || instr == 0x8000033C) // NOP
/tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ps2_vu1_core.cpp:1162:    if (lower == 0u || lower == 0x8000033Cu)
/tmp/PS2Recomp/ps2xTest/src/ps2_vu1_tests.cpp:253:        tc.Run("LOI commits the lower immediate after the upper instruction", [](TestCase &t)
/tmp/PS2Recomp/ps2xTest/src/ps2_vu1_tests.cpp:276:                     "LOI should become visible after the upper from the same pair");
/tmp/PS2Recomp/ps2xTest/src/ps2_vu1_tests.cpp:283:            t.Equals(vu1.state().i, 7.0f, "LOI should commit lower immediate into I after upper execution");
===
/tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ps2_vu1_core.cpp:248:    const long double i = operand(m_state.i);
/tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ps2_vu1_core.cpp:469:            right = normalizeOperand(m_state.i);
/tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ps2_vu1_core.cpp:1600:    m_state.itop = itop;
/tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ps2_vu1_core.cpp:1617:    m_state.itop = itop;
/tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ps2_vu1_core.cpp:1698:            m_state.i = normalizeOperand(immediate);
/tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ps2_vu1_lower.cpp:664:                    m_state.vi[viT] = (int32_t)(m_state.itop & 0x3FFu);
/tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ps2_vu1_upper.cpp:47:    const float i = normalizeOperand(m_state.i);

```

## [28] Find I-bit decode rule in core
```
grep -n "iBit\|isLoi\|isLOI\|LOI" /tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ps2_vu1_core.cpp /tmp/PS2Recomp/ps2xRuntime/include/runtime/ps2_vu1.h | head; echo ===; sed -n '280,340p' /tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ps2_vu1_core.cpp
```
output:
```
/tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ps2_vu1_core.cpp:1515:    decoded.iBit = (decoded.upper & 0x80000000u) != 0u;
/tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ps2_vu1_core.cpp:1521:    if (!decoded.iBit)
/tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ps2_vu1_core.cpp:1693:        if (decoded.iBit)
/tmp/PS2Recomp/ps2xRuntime/include/runtime/ps2_vu1.h:111:        bool iBit = false;
===
                break;
            case 0x23u:
                result = acc(component) + vs(component) * i;
                break;
            case 0x24u:
                result = vs(component) - q;
                break;
            case 0x25u:
                result = acc(component) - vs(component) * q;
                break;
            case 0x26u:
                result = vs(component) - i;
                break;
            case 0x27u:
                result = acc(component) - vs(component) * i;
                break;
            case 0x28u:
                result = vs(component) + vt(component);
                break;
            case 0x29u:
                result = acc(component) + vs(component) * vt(component);
                break;
            case 0x2Au:
                result = vs(component) * vt(component);
                break;
            case 0x2Cu:
                result = vs(component) - vt(component);
                break;
            case 0x2Du:
                result = acc(component) - vs(component) * vt(component);
                break;
            case 0x2Eu:
            {
                static constexpr uint8_t left[4] = {1u, 2u, 0u, 3u};
                static constexpr uint8_t right[4] = {2u, 0u, 1u, 3u};
                result = component == 3u
                             ? 0.0L
                             : acc(component) - vs(left[component]) * vt(right[component]);
                break;
            }
            default:
                return false;
            }
        }
        return true;
    }

    if (special <= 0x03u)
        result = vs(component) + vt(special & 3u);
    else if (special <= 0x07u)
        result = vs(component) - vt(special & 3u);
    else if (special <= 0x0Bu)
        result = acc(component) + vs(component) * vt(special & 3u);
    else if (special <= 0x0Fu)
        result = acc(component) - vs(component) * vt(special & 3u);
    else if (special >= 0x18u && special <= 0x1Bu)
        result = vs(component) * vt(special & 3u);
    else
    {
        switch (special)
        {

```

## [29] Inspect instruction fetch and E/I bit handling
```
grep -n "0x80000000\|E-bit\|Ebit\|ebit\|programEnded\|upper =\s\|lower =\s\|upper(\|lower(" /tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ps2_vu1_core.cpp | head -n 40; echo ====; sed -n '1440,1560p' /tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ps2_vu1_core.cpp
```
output:
```
116:        bits &= 0x80000000u;
120:        bits = (bits & 0x80000000u) | 0x7F7FFFFFu;
130:    const uint32_t sign = bits & 0x80000000u;
222:    const uint32_t upper = m_currentUpperInstruction;
411:    uint32_t bits = negative ? 0x80000000u : 0u;
435:    const uint32_t upper = m_currentUpperInstruction;
1515:    decoded.iBit = (decoded.upper & 0x80000000u) != 0u;
1595:    m_state.ebit = false;
1635:    bool programEnded = false;
1803:            programEnded = true;
1805:        else if (m_state.ebit)
1806:            programEnded = true;
1811:            programEnded = true;
1814:            m_state.ebit = true;
1823:        if (programEnded)
1827:    if (programEnded)
1830:        m_state.ebit = false;
====
    case 0x78:
    case 0x79:
    case 0x7A:
    case 0x7C:
    case 0x7D:
        if (m_unit == Unit::VU0)
        {
            usage.reserved = true;
            break;
        }
        usage.pipeline = PipelineEfu;
        switch (special)
        {
        case 0x70:
            usage.latency = 11u;
            break;
        case 0x71:
        case 0x72:
        case 0x77:
            usage.latency = 18u;
            break;
        case 0x73:
            usage.latency = 24u;
            break;
        case 0x74:
        case 0x75:
        case 0x7C:
            usage.latency = 54u;
            break;
        case 0x76:
        case 0x78:
        case 0x7A:
            usage.latency = 12u;
            break;
        case 0x79:
            usage.latency = 29u;
            break;
        case 0x7D:
            usage.latency = 44u;
            break;
        default:
            break;
        }
        if (special >= 0x70u && special <= 0x73u)
            addVfRead(usage, vfS, 0xEu);
        else if (special == 0x74u)
            addVfRead(usage, vfS, 0xCu);
        else if (special == 0x75u)
            addVfRead(usage, vfS, 0xAu);
        else if (special == 0x76u)
            addVfRead(usage, vfS, 0xFu);
        else
            addVfRead(usage, vfS, laneForComponent((lower >> 21) & 3u));
        break;
    case 0x7B:
        if (m_unit == Unit::VU0)
        {
            usage.reserved = true;
            break;
        }
        usage.pipeline = PipelineEfu;
        usage.waitP = true;
        break;
    default:
        usage.reserved = true;
        break;
    }
    return usage;
}

VU1Interpreter::DecodedInstructionPair VU1Interpreter::decodeInstructionPair(const uint8_t *vuCode, uint32_t pc) const
{
    DecodedInstructionPair decoded;
 
... [4716 chars]
```

## [30] Rerun corrected histogram
```
python3 /tmp/ssx3vu/histogram.py 2>&1 | sed -n '/^file/,$p'
```
output:
```
file                                instr   impl  resvd   LOI  Ebit
sec32_.vutext.bin                    7420  14808     32    44   113  (59360 bytes)
sec39_.vudata.bin                       0      0      0     0     0  (0 bytes)
sec47_.DVP.bin                        194    233    155     0    41  (1557 bytes)
sec48_.DVP.overlay..0x0.3337891.38    256    512      0     0     0  (2048 bytes)
sec49_.DVP.overlay..0x800.38868702    256    512      0     0     0  (2048 bytes)
sec50_.DVP.overlay..0x1000.3886870    256    512      0     0     0  (2048 bytes)
sec51_.DVP.overlay..0x1800.3886870    256    512      0     0     0  (2048 bytes)
sec52_.DVP.overlay..0x2000.3886870    148    296      0     0     0  (1184 bytes)
sec53_.DVP.overlay..0x0.26713891.3    256    512      0     0     0  (2048 bytes)
sec54_.DVP.overlay..0x800.40910752    256    512      0     0     0  (2048 bytes)
sec55_.DVP.overlay..0x1000.1030201    256    512      0     0     0  (2048 bytes)
sec56_.DVP.overlay..0x1800.1030201    256    512      0     0     0  (2048 bytes)
sec57_.DVP.overlay..0x2000.1030201    256    512      0     0     0  (2048 bytes)
sec58_.DVP.overlay..0x2800.1030201    256    512      0     0     0  (2048 bytes)
sec59_.DVP.overlay..0x3000.1030201    256    512      0     0     0  (2048 bytes)
sec60_.DVP.overlay..0x3800.1030201    213    426      0     0     0  (1704 bytes)
sec61_.DVP.overlay..0x0.108067.33.    256    512      0     0     0  (2048 bytes)
sec62_.DVP.overlay..0x800.40910893    256    512      0     0     0  (2048 bytes)
sec63_.DVP.overlay..0x1000.3476914     64    128      0     0     0  (512 bytes)
sec64_.DVP.overlay..0x0.108323.38.    256    512      0     0     0  (2048 bytes)
sec65_.DVP.overlay..0x800.38872164    256    512      0     0     0  (2048 bytes)
sec66_.DVP.overlay..0x1000.3476911    256    512      0     0     0  (2048 bytes)
sec67_.DVP.overlay..0x1800.3476911    256    512      0     0     0  (2048 bytes)
sec68_.DVP.overlay..0x2000.3476911    256    512      0     0     0  (2048 bytes)
sec69_.DVP.overlay..0x2800.3476911    256    512      0     0     0  (2048 bytes)
sec70_.DVP.overlay..0x3000.3476911    256    512      0     0     0  (2048 bytes)
sec71_.DVP.overlay..0x3800.3887078    193    386      0     0     0  (1544 bytes)
sec72_.DVP.overlay..0x0.114211.91.    256    512      0     0     0  (2048 bytes)
sec73_.DVP.overlay..0x800.38871889    256    512      0     0     0  (2048 bytes)
sec74_.DVP.overlay..0x1000.2663826    256    512      0  
... [7146 chars]
```

## [31] Per-program VU opcode census
```
python3 /tmp/ssx3vu/census.py
```
output:
```
--- Program 0: 5 sections, 9376 bytes, 1172 instr, E-bits=0, reserved=0
    ops used: 2 | VU1-only-ops: {}
    top: 1172xU:ADDbc, 1172xL:NOP
--- Program 1: 8 sections, 16040 bytes, 2005 instr, E-bits=0, reserved=0
    ops used: 2 | VU1-only-ops: {}
    top: 2005xU:ADDbc, 2005xL:NOP
--- Program 2: 3 sections, 4608 bytes, 576 instr, E-bits=0, reserved=0
    ops used: 2 | VU1-only-ops: {}
    top: 576xU:ADDbc, 576xL:NOP
--- Program 3: 8 sections, 15880 bytes, 1985 instr, E-bits=0, reserved=0
    ops used: 2 | VU1-only-ops: {}
    top: 1985xU:ADDbc, 1985xL:NOP
--- Program 4: 4 sections, 6432 bytes, 804 instr, E-bits=0, reserved=0
    ops used: 2 | VU1-only-ops: {}
    top: 804xU:ADDbc, 804xL:NOP
--- Program 5: 2 sections, 2200 bytes, 275 instr, E-bits=0, reserved=0
    ops used: 2 | VU1-only-ops: {}
    top: 275xU:ADDbc, 275xL:NOP
--- Program 6: 2 sections, 3904 bytes, 488 instr, E-bits=0, reserved=0
    ops used: 2 | VU1-only-ops: {}
    top: 488xU:ADDbc, 488xL:NOP

```

## [32] Check if overlay sections are zero-filled
```
xxd /tmp/ssx3vu/sec48_.DVP.overlay..0x0.3337891.38.0.bin | head -5; echo ...; xxd /tmp/ssx3vu/sec48_.DVP.overlay..0x0.3337891.38.0.bin | tail -3; echo ===; python3 -c "
import glob
for p in sorted(glob.glob('/tmp/ssx3vu/sec*.bin')):
    b = open(p,'rb').read()
    nz = sum(1 for x in b if x != 0)
    print(f'{len(b):6d} bytes, {nz:6d} nonzero: {p.split(chr(47))[-1][:40]}')"
```
output:
```
00000000: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000010: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000020: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000030: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000040: 0000 0000 0000 0000 0000 0000 0000 0000  ................
...
000007d0: 0000 0000 0000 0000 0000 0000 0000 0000  ................
000007e0: 0000 0000 0000 0000 0000 0000 0000 0000  ................
000007f0: 0000 0000 0000 0000 0000 0000 0000 0000  ................
===
 59360 bytes,  45882 nonzero: sec32_.vutext.bin
     0 bytes,      0 nonzero: sec39_.vudata.bin
  1557 bytes,   1350 nonzero: sec47_.DVP.bin
  2048 bytes,      0 nonzero: sec48_.DVP.overlay..0x0.3337891.38.0.bin
  2048 bytes,      0 nonzero: sec49_.DVP.overlay..0x800.3886870251.940
  2048 bytes,      0 nonzero: sec50_.DVP.overlay..0x1000.3886870251.14
  2048 bytes,      0 nonzero: sec51_.DVP.overlay..0x1800.3886870251.20
  1184 bytes,      0 nonzero: sec52_.DVP.overlay..0x2000.3886870251.25
  2048 bytes,      0 nonzero: sec53_.DVP.overlay..0x0.26713891.32.0.bi
  2048 bytes,      0 nonzero: sec54_.DVP.overlay..0x800.4091075227.14.
  2048 bytes,      0 nonzero: sec55_.DVP.overlay..0x1000.1030201195.13
  2048 bytes,      0 nonzero: sec56_.DVP.overlay..0x1800.1030201195.17
  2048 bytes,      0 nonzero: sec57_.DVP.overlay..0x2000.1030201195.21
  2048 bytes,      0 nonzero: sec58_.DVP.overlay..0x2800.1030201195.27
  2048 bytes,      0 nonzero: sec59_.DVP.overlay..0x3000.1030201195.34
  1704 bytes,      0 nonzero: sec60_.DVP.overlay..0x3800.1030201195.39
  2048 bytes,      0 nonzero: sec61_.DVP.overlay..0x0.108067.33.0.bin
  2048 bytes,      0 nonzero: sec62_.DVP.overlay..0x800.4091089323.11.
   512 bytes,      0 nonzero: sec63_.DVP.overlay..0x1000.3476914539.12
  2048 bytes,      0 nonzero: sec64_.DVP.overlay..0x0.108323.38.0.bin
  2048 bytes,      0 nonzero: sec65_.DVP.overlay..0x800.3887216411.266
  2048 bytes,      0 nonzero: sec66_.DVP.overlay..0x1000.3476911979.61
  2048 bytes,      0 nonzero: sec67_.DVP.overlay..0x1800.3476911979.11
  2048 bytes,      0 nonzero: sec68_.DVP.overlay..0x2000.3476911979.16
  2048 bytes,      0 nonzero: sec69_.DVP.overlay..0x2800.3476911979.20
  2048 bytes,      0 nonzero: sec70_.DVP.overlay..0x3000.3476911979.23
  1544 bytes,      0 nonzero: sec71_.DVP.overlay..0x3800.3887078011.13
  2048 bytes,      0 nonzero: sec72_.DVP.overlay..0x0.114211.91.0.bin
  2048 bytes,      0 nonzero: sec73
... [2960 chars]
```

## [33] Full VU program census with correct decoder
```
python3 /tmp/ssx3vu/final_census.py
```
output:
```
32 MPG packets
7 programs

Program 0: 1172 instr (9376 B), E-bits=15, LOI=1, reserved=0
    distinct ops: 53
Program 1: 2005 instr (16040 B), E-bits=7, LOI=1, reserved=0
    distinct ops: 61
Program 2: 576 instr (4608 B), E-bits=9, LOI=4, reserved=0
    distinct ops: 44
Program 3: 1985 instr (15880 B), E-bits=13, LOI=5, reserved=0
    distinct ops: 71
Program 4: 804 instr (6432 B), E-bits=9, LOI=28, reserved=0
    distinct ops: 52
Program 5: 275 instr (2200 B), E-bits=2, LOI=4, reserved=0
    distinct ops: 41
Program 6: 488 instr (3904 B), E-bits=17, LOI=1, reserved=0
    distinct ops: 40

TOTAL programs=7 reserved hits=0

Combined distinct ops: 85
VU1-specialty ops present: {'L:XGKICK': 47, 'L:XTOP': 62, 'L:XITOP': 2, 'U:CLIP': 120, 'L:DIV': 125, 'L:RSQRT': 31, 'L:RNEXT': 53, 'L:RINIT': 29, 'L:ERLENG': 1, 'L:ESIN': 9, 'L:WAITP': 2, 'L:WAITQ': 37, 'L:MFP': 11}

Full usage:
   4197  U:NOP
   2215  L:NOP
    983  L:LQ
    884  L:IADDIU
    611  U:MADDAbc
    429  U:MULAbc
    376  L:SQ
    356  U:MADDbc
    269  L:ILW
    253  L:SQI
    221  L:LQI
    182  L:IBNE
    164  L:IADD
    160  U:ADDbc
    160  L:BAL
    149  U:MUL
    147  U:MULq
    125  L:DIV
    125  L:IBEQ
    120  U:CLIP
    112  U:SUB
    108  L:ISUBIU
    102  U:MADD
     94  L:MOVE
     84  U:SUBbc
     83  L:ISW
     79  L:MFIR
     74  U:MAXbc
     74  U:FTOI4
     72  U:MULbc
     70  L:JR
     70  L:FCOR
     70  U:ITOF15
     68  L:FCAND
     67  L:B
     62  L:XTOP
     55  L:MTIR
     53  L:RNEXT
     52  L:IADDI
     47  L:XGKICK
     47  L:FMAND
     44  L:LOI-imm
     44  U:ADDAbc
     42  U:ITOF0
     42  L:ISUB
     40  L:IAND
     38  L:IOR
     38  U:ITOF12
     38  U:MULi
     37  U:FTOI0
     37  L:WAITQ
     36  L:IBGTZ
     35  U:MADDA
     33  U:MINIi
     31  L:RSQRT
     30  U:MULA
     29  U:MAX
     29  L:RINIT
     27  U:MADDq
     26  U:ADD
     25  U:ADDq
     24  L:FCGET
     22  U:MSUBbc
     20  U:ADDi
     18  U:MSUBq
     18  L:MR32
     16  U:FTOI12
     16  U:MINIbc
     16  U:ABS
     13  U:OPMULA
     13  U:ADDA
     11  L:MFP
     11  L:IBGEZ
      9  L:ESIN
      9  L:FCSET
      5  L:IBLEZ
      4  U:OPMSUB
      4  L:FSAND
      3  U:MADDi
      2  L:WAITP
      2  L:XITOP
      1  L:ERLENG
      1  U:MAXi
      1  U:MINI
      1  U:SUBA

```

## [34] Check VIF command and XGKICK coverage
```
grep -n "case 0x\|VIF_\|unpack\|UNPACK\|MSCAL\|DIRECT" /tmp/PS2Recomp/ps2xRuntime/src/lib/ps2_vif1_interpreter.cpp | head -n 50; echo ===XGKICK===; grep -n "startXgkick" /tmp/PS2Recomp/ps2xRuntime/src/lib/vu/*.cpp /tmp/PS2Recomp/ps2xRuntime/src/lib/vu/*.h /tmp/PS2Recomp/ps2xRuntime/include/runtime/ps2_vu1.h | head
```
output:
```
7:    VIF_NOP = 0x00,
8:    VIF_STCYCL = 0x01,
9:    VIF_OFFSET = 0x02,
10:    VIF_BASE = 0x03,
11:    VIF_ITOP = 0x04,
12:    VIF_STMOD = 0x05,
13:    VIF_MSKPATH3 = 0x06,
14:    VIF_MARK = 0x07,
15:    VIF_FLUSHE = 0x10,
16:    VIF_FLUSH = 0x11,
17:    VIF_FLUSHA = 0x13,
18:    VIF_MSCAL = 0x14,
19:    VIF_MSCALF = 0x15,
20:    VIF_MSCNT = 0x17,
21:    VIF_STMASK = 0x20,
22:    VIF_STROW = 0x30,
23:    VIF_STCOL = 0x31,
24:    VIF_MPG = 0x4A,
25:    VIF_DIRECT = 0x50,
26:    VIF_DIRECTHL = 0x51,
82:        if (opcode == VIF_NOP)
86:        else if (opcode == VIF_STCYCL)
91:        else if (opcode == VIF_ITOP)
96:        else if (opcode == VIF_STMOD)
101:        else if (opcode == VIF_MARK)
107:        else if (opcode == VIF_FLUSHE || opcode == VIF_FLUSH || opcode == VIF_FLUSHA)
111:        else if (opcode == VIF_STMASK)
119:        else if (opcode == VIF_STROW)
127:        else if (opcode == VIF_STCOL)
135:        else if (opcode == VIF_MPG)
317:        if (opcode == VIF_NOP)
321:        else if (opcode == VIF_STCYCL)
326:        else if (opcode == VIF_OFFSET)
335:        else if (opcode == VIF_BASE)
337:            // BASE only updates the base register. TOPS changes on OFFSET/MSCAL.
341:        else if (opcode == VIF_ITOP)
343:            // ITOP VIFcode writes pending ITOPS; VU XITOP observes it after MSCAL/MSCNT.
347:        else if (opcode == VIF_STMOD)
352:        else if (opcode == VIF_MSKPATH3)
361:        else if (opcode == VIF_MARK)
367:        else if (opcode == VIF_FLUSHE || opcode == VIF_FLUSH || opcode == VIF_FLUSHA)
371:        else if (opcode == VIF_MSCAL || opcode == VIF_MSCALF)
375:            // Values visible to the VU program for this MSCAL.
394:        else if (opcode == VIF_MSCNT)
412:        else if (opcode == VIF_STMASK)
422:        else if (opcode == VIF_STROW)
430:        else if (opcode == VIF_STCOL)
438:        else if (opcode == VIF_MPG)
461:        else if (opcode == VIF_DIRECT || opcode == VIF_DIRECTHL)
473:                const bool directHl = (opcode == VIF_DIRECTHL);
===XGKICK===
/tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ps2_vu1_core.cpp:929:void VU1Interpreter::startXgkick(uint32_t qwordAddress)
/tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ps2_vu1_lower.cpp:668:                startXgkick(static_cast<uint32_t>(static_cast<uint16_t>(m_state.vi[viS])));
/tmp/PS2Recomp/ps2xRuntime/include/runtime/ps2_vu1.h:277:    void startXgkick(uint32_t qwordAddress);

```

## [35] Check build tool availability
```
command -v cmake g++ gcc ninja make 2>&1; cmake --version 2>&1 | head -1; g++ --version 2>&1 | head -1
```
output:
```
/usr/bin/cmake
cmake version 3.28.3
g++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0

```

## [36] Read XGKICK path and GS stub status
```
sed -n '929,990p' /tmp/PS2Recomp/ps2xRuntime/src/lib/vu/ps2_vu1_core.cpp; echo ===GS-stub-sample===; grep -n "TODO\|stub\|Stub\|STUB\|not implemented\|Unimplemented" /tmp/PS2Recomp/ps2xRuntime/src/lib/Kernel/Stubs/GS.cpp | head -n 20; wc -l /tmp/PS2Recomp/ps2xRuntime/src/lib/Kernel/Stubs/GS.cpp
```
output:
```
void VU1Interpreter::startXgkick(uint32_t qwordAddress)
{
    if (m_unit != Unit::VU1 || !m_activeVuData || m_activeVuDataSize < 16u)
        return;

    const uint32_t sourceAddress = (qwordAddress * 16u) % m_activeVuDataSize;
    m_xgkick = {};
    m_xgkick.active = true;
    m_xgkick.sourceAddress = sourceAddress;
    m_xgkick.cycleCredit = 1u; // XGKICK's issue cycle counts toward PATH1.
    m_xgkick.issueCycle = m_cycle;
}

void VU1Interpreter::advanceOneCycle()
{
    ++m_cycle;
    m_state.cycles = m_cycle;
    // LSU commits become visible at the cycle boundary before PATH1 consumes
    // its next qword from VU memory.
    commitReadyPipelines();
    progressXgkick();
}

void VU1Interpreter::advanceTo(uint64_t targetCycle)
{
    while (m_cycle < targetCycle)
        advanceOneCycle();
}

bool VU1Interpreter::pipelinesPending() const
{
    if (m_fdiv.valid || m_xgkick.active)
        return true;
    for (const ScalarPipelineEntry &entry : m_efu)
        if (entry.valid)
            return true;
    for (const FlagPipelineEntry &entry : m_flagPipeline)
        if (entry.valid)
            return true;
    for (const PendingStore &store : m_storePipeline)
        if (store.valid)
            return true;
    for (const PendingVfWrite &write : m_vfWritePipeline)
        if (write.valid)
            return true;
    for (const PendingViWrite &write : m_viWritePipeline)
        if (write.valid)
            return true;
    for (const PendingAccWrite &write : m_accWritePipeline)
        if (write.valid)
            return true;
    return false;
}

void VU1Interpreter::flushPipelines()
{
    while (pipelinesPending())
        advanceOneCycle();
}

uint64_t VU1Interpreter::calculatePairReadyCycle(const DecodedInstructionPair &decoded) const
{
===GS-stub-sample===
8:namespace ps2_stubs
1370:            RUNTIME_LOG("ps2_stub Ps2SwapDBuff");
1541 /tmp/PS2Recomp/ps2xRuntime/src/lib/Kernel/Stubs/GS.cpp

```

## [37] Check submodule dependencies for build
```
cat /tmp/PS2Recomp/.gitmodules 2>/dev/null; ls /tmp/PS2Recomp/ps2xRecomp 2>/dev/null; find /tmp/PS2Recomp -name "*.cmake" -maxdepth 2 | head; grep -rn "elfio\|toml11\|fmt" /tmp/PS2Recomp/CMakeLists.txt | head
```
output:
```
CMakeLists.txt
include
src
tools

```

## [38] Inspect CMake project structure
```
cat /tmp/PS2Recomp/CMakeLists.txt; echo =====; cat /tmp/PS2Recomp/ps2xRecomp/CMakeLists.txt 2>/dev/null | head -40; echo =====; cat /tmp/PS2Recomp/ps2xAnalyzer/CMakeLists.txt | head -30
```
output:
```
cmake_minimum_required(VERSION 3.21)

if(NOT DEFINED CMAKE_TOOLCHAIN_FILE AND DEFINED ENV{VITASDK})
    set(PS2X_VITA_TOOLCHAIN_FILE "$ENV{VITASDK}/share/vita.toolchain.cmake")
    if(EXISTS "${PS2X_VITA_TOOLCHAIN_FILE}")
        set(CMAKE_TOOLCHAIN_FILE "${PS2X_VITA_TOOLCHAIN_FILE}" CACHE PATH
            "Toolchain file used for cross-compiling" FORCE)
        message(STATUS "Using VitaSDK toolchain from VITASDK: ${CMAKE_TOOLCHAIN_FILE}")
    endif()
endif()

project(PS2RetroX)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

option(PS2X_BUILD_RECOMP "Build ps2xRecomp" ON)
option(PS2X_BUILD_RUNTIME "Build ps2xRuntime" ON)
option(PS2X_BUILD_ANALYZER "Build ps2xAnalyzer" ON)
option(PS2X_BUILD_TEST "Build ps2xTest" ON)
option(PS2X_BUILD_STUDIO "Build ps2xStudio" ON)

if(ANDROID)
    message(STATUS "Android target detected, building runtime only")
    set(PS2X_BUILD_RECOMP OFF)
    set(PS2X_BUILD_ANALYZER OFF)
    set(PS2X_BUILD_TEST OFF)
    set(PS2X_BUILD_STUDIO OFF)
endif()

set(PS2X_IS_ARM_TARGET OFF)
set(PS2X_IS_AARCH64_TARGET OFF)
if(CMAKE_SYSTEM_PROCESSOR MATCHES "arm64|aarch64|ARM64")
    set(PS2X_IS_ARM_TARGET ON)
    set(PS2X_IS_AARCH64_TARGET ON)
elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "^arm|^ARM")
    set(PS2X_IS_ARM_TARGET ON)
endif()

if((CMAKE_C_COMPILER MATCHES "arm-vita-eabi") OR
   (CMAKE_CXX_COMPILER MATCHES "arm-vita-eabi"))
    set(PS2X_IS_ARM_TARGET ON)
endif()

if(PS2X_IS_ARM_TARGET)
    message(STATUS "ARM target detected, fetching sse2neon")

    include(FetchContent)
    FetchContent_Declare(
        sse2neon
        GIT_REPOSITORY https://github.com/DLTcollab/sse2neon.git
        GIT_TAG v1.9.1
        GIT_SHALLOW TRUE
    )
    FetchContent_MakeAvailable(sse2neon)

    include_directories(${sse2neon_SOURCE_DIR})
    add_compile_definitions(USE_SSE2NEON)

    if(PS2X_IS_AARCH64_TARGET AND APPLE)
        # macOS ARM64 already uses optimal defaults
        message(STATUS "macOS ARM64 - using default compiler flags")
    elseif(PS2X_IS_AARCH64_TARGET AND MSVC)
        # Windows ARM64 - MSVC already uses optimal defaults
        message(STATUS "Windows ARM64 (MSVC) - using default compiler flags")
    elseif(PS2X_IS_AARCH64_TARGET)
        # Linux ARM64 - add NEON flags
        message(STATUS "Non-Apple ARM64 - adding NEON compiler flags")
        add_compile_options(-march=armv8-a+fp+simd)

        # Try to enable crypto and CRC extensions if supported
        include(CheckCXXCompilerFlag)
        check_cxx_compiler_flag("-march=armv8-a+fp+simd+
... [4813 chars]
```

## [39] Verify build generator availability
```
command -v make; command -v ninja; command -v gmake; echo "---"; ls /usr/bin | grep -i -E "^(make|ninja|g\\+\\+|gcc)" | head
```
output:
```
/usr/bin/make
/usr/bin/gmake
---
g++
g++-13
gcc
gcc-13
gcc-ar
gcc-ar-13
gcc-nm
gcc-nm-13
gcc-ranlib
gcc-ranlib-13

```

## [40] Configure PS2Recomp build
```
cmake -S /tmp/PS2Recomp -B /tmp/PS2Recomp/out/build -DPS2X_BUILD_STUDIO=OFF -DCMAKE_BUILD_TYPE=Release 2>&1 | tail -15
```
output:
```
-- Testing if -fno-strict-aliasing can be used -- compiles
-- Using raylib's GLFW
-- Performing Test CMAKE_HAVE_LIBC_PTHREAD
-- Performing Test CMAKE_HAVE_LIBC_PTHREAD - Success
-- Found Threads: TRUE  
-- Including X11 support
CMake Error at /usr/share/cmake-3.28/Modules/FindPackageHandleStandardArgs.cmake:230 (message):
  Could NOT find X11 (missing: X11_X11_INCLUDE_PATH X11_X11_LIB)
Call Stack (most recent call first):
  /usr/share/cmake-3.28/Modules/FindPackageHandleStandardArgs.cmake:600 (_FPHSA_FAILURE_MESSAGE)
  /usr/share/cmake-3.28/Modules/FindX11.cmake:665 (find_package_handle_standard_args)
  out/build/_deps/raylib-src/src/external/glfw/src/CMakeLists.txt:181 (find_package)


-- Configuring incomplete, errors occurred!

```

## [41] Configure analyzer+recompiler only
```
cmake -S /tmp/PS2Recomp -B /tmp/PS2Recomp/out/build -DPS2X_BUILD_STUDIO=OFF -DPS2X_BUILD_RUNTIME=OFF -DPS2X_BUILD_TEST=OFF -DCMAKE_BUILD_TYPE=Release 2>&1 | tail -8
```
output:
```
> Enabling optimization for: ps2_recomp_lib
> Enabling optimization for: ps2_recomp
-- Using the multi-header code from /tmp/PS2Recomp/out/build/_deps/nlohmann_json-src/include/
> Enabling optimization for: ps2_analyzer_lib
> Enabling optimization for: ps2_analyzer
-- Configuring done (9.4s)
-- Generating done (0.0s)
-- Build files have been written to: /tmp/PS2Recomp/out/build

```

## [42] Build analyzer and recompiler
```
cmake --build /tmp/PS2Recomp/out/build --config Release -j"$(nproc)" 2>&1 | tail -8
```
output:
```
[ 96%] Building CXX object ps2xAnalyzer/CMakeFiles/ps2_analyzer_lib.dir/src/sce_symbol_scanner.cpp.o
[ 97%] Linking CXX executable ps2_recomp
[ 97%] Built target ps2_recomp
[ 98%] Linking CXX static library libps2_analyzer_lib.a
[ 98%] Built target ps2_analyzer_lib
[ 99%] Building CXX object ps2xAnalyzer/CMakeFiles/ps2_analyzer.dir/src/analyzer_main.cpp.o
[100%] Linking CXX executable ps2_analyzer
[100%] Built target ps2_analyzer

```

## [43] Check analyzer usage
```
/tmp/PS2Recomp/out/build/ps2xAnalyzer/ps2_analyzer --help 2>&1 | head -30; echo ===; ls /tmp/PS2Recomp/out/build/ps2xAnalyzer/ /tmp/PS2Recomp/out/build/ps2xRecomp/ 2>/dev/null
```
output:
```
PS2 ELF Analyzer
A tool to analyze PS2 ELF files and generate TOML configuration for PS2Recomp

Usage: ps2_analyzer <input_elf> <output_toml> [sce_symbol_db_dir]
  input_elf    Path to the PS2 ELF file
  output_toml  Path to output TOML configuration file
  sce_symbol_db_dir  Optional override directory containing symbols.json and tree.json
                     If omitted, the embedded SCE symbol database is used
===
/tmp/PS2Recomp/out/build/ps2xAnalyzer/:
CMakeFiles
cmake_install.cmake
libps2_analyzer_lib.a
Makefile
ps2_analyzer

/tmp/PS2Recomp/out/build/ps2xRecomp/:
CMakeFiles
cmake_install.cmake
libps2_recomp_lib.a
librabbitizer.a
Makefile
ps2_recomp

```

## [44] Analyze SSX3 ELF for recomp config
```
cd /tmp && ./PS2Recomp/out/build/ps2xAnalyzer/ps2_analyzer /tmp/SLUS_207.72 /tmp/ssx3.toml 2>&1 | tail -40
```
output:
```
Function _kExitTLBHandler signature analysis:
  - Uses approximately 23 parameter(s)
  - Uses 64-bit operations
  - Returns a value
Function _kDebugException signature analysis:
  - Uses approximately 23 parameter(s)
  - Uses 64-bit operations
  - Returns a value
Function __fixdfdi signature analysis:
  - Uses approximately 1 parameter(s)
  - Uses 64-bit operations
Function __fixunsdfdi signature analysis:
  - Uses approximately 2 parameter(s)
  - Uses 64-bit operations
Function __moddi3 signature analysis:
  - Uses approximately 21 parameter(s)
  - Uses 64-bit operations
  - Returns a value
Function __umoddi3 signature analysis:
  - Uses approximately 10 parameter(s)
  - Uses 64-bit operations
  - Returns a value
Function sub_0042E508 signature analysis:
  - Uses approximately 13 parameter(s)
  - Uses 64-bit operations
  - Returns a value
Optimizing patches...
Analysis completed
- 180 library functions to stub
- 359 detected library functions without runtime handlers
- skip output retained for compatibility; analyzer does not auto-skip functions
- 0 potential patches identified
- 0 jump tables detected
Generated TOML configuration: /tmp/ssx3.toml

Analysis complete
TOML configuration has been written to: /tmp/ssx3.toml

You can now use this configuration with PS2Recomp:
  ps2recomp /tmp/ssx3.toml

```

## [45] Inspect generated TOML config
```
head -60 /tmp/ssx3.toml; echo ...; grep -c "" /tmp/ssx3.toml; echo ===; grep -n "stubs\|skip" /tmp/ssx3.toml | head -10
```
output:
```
# PS2Recomp configuration for: SLUS_207.72
# Generated by ElfAnalyzer

[general]
# Path to input ELF file
input = "/tmp/SLUS_207.72"

# Path to Ghidra exported function map (optional CSV)
ghidra_output = ""

# Path to output directory
output = "/tmp/output/"

# Single file output mode (recommended for large games)
single_file_output = false

# Patch policy (instruction-driven handling is preferred for syscalls)
patch_syscalls = false
patch_cop0 = true
patch_cache = true

# Functions to stub (only names with runtime syscall/stub handlers)
stubs = [
  "sceGsResetGraph@0x003FD910",
  "sceGsResetPath@0x003FDAB0",
  "sceGsSyncPath@0x003FDB18",
  "memclr@0x003FDF50",
  "sceDmaGetChan@0x003FDF88",
  "sceDmaReset@0x003FDFB0",
  "sceDmaPutEnv@0x003FE090",
  "sceDmaGetEnv@0x003FE268",
  "sceDmaSend@0x003FE2B8",
  "sceDmaSendN@0x003FE320",
  "sceDmaSendI@0x003FE398",
  "sceDmaRecv@0x003FE410",
  "sceDmaRecvN@0x003FE458",
  "sceDmaRecvI@0x003FE4D8",
  "sceDmaSync@0x003FE558",
  "sceDmaWatch@0x003FE590",
  "sceDmaPause@0x003FE5C8",
  "sceDevVif0Reset@0x003FF060",
  "scePadInit@0x003FF4A8",
  "scePadInit2@0x003FF5E8",
  "scePadEnd@0x003FF688",
  "scePadPortOpen@0x003FF708",
  "scePadPortClose@0x003FF8F0",
  "scePadGetDmaStr@0x003FF9A8",
  "scePadGetFrameCount@0x003FFA08",
  "scePadRead@0x003FFA58",
  "scePadGetState@0x003FFBC0",
  "scePadStateIntToStr@0x003FFC38",
  "scePadSetReqState@0x003FFC70",
  "scePadGetReqState@0x003FFCD8",
  "scePadInfoAct@0x003FFD60",
  "scePadInfoComb@0x003FFE80",
  "scePadInfoMode@0x003FFFA0",
  "scePadSetMainMode@0x004000D8",
  "scePadSetActDirect@0x00400190",
  "scePadSetActAlign@0x00400250",
  "scePadGetButtonMask@0x00400328",
...
1618
===
23:stubs = [
208:untracked_stubs = [
319:  "_skipMB0@0x00406510",
602:# Legacy compatibility field. The analyzer no longer auto-populates skip entries.
603:skip = []

```

## [46] Inspect untracked stubs section
```
sed -n '200,240p' /tmp/ssx3.toml; echo ...; grep -c "@0x" /tmp/ssx3.toml
```
output:
```
  "sceDeci2ExReqSend@0x0042C9D8",
  "sceDeci2ExLock@0x0042CA08",
  "sceDeci2ExUnLock@0x0042CA30",
  "InitTLB@0x0042CD58",
]

# Detected library-like functions without runtime handlers.
# This is informational only; PS2Recomp ignores this list and recompiles them normally.
untracked_stubs = [
  "_$_9type_info@0x001DCBD8",
  "_$_9type_info@0x001DCC78",
  "_$_9type_info@0x001E10B8",
  "_$_9type_info@0x00255638",
  "_$_9type_info@0x00267E18",
  "_$_9type_info@0x00267E98",
  "_$_9type_info@0x00267F28",
  "_$_9type_info@0x00267FB8",
  "_$_9type_info@0x00268210",
  "_$_9type_info@0x00268658",
  "_$_9type_info@0x002686F0",
  "_$_9type_info@0x00268790",
  "DPRINT@0x002B9100",
  "_$_9type_info@0x002C1460",
  "fiprintf@0x002C26D0",
  "_$_9type_info@0x002F7F30",
  "_$_9type_info@0x002F7F60",
  "_$_9type_info@0x002F8340",
  "fiprintf@0x003194A8",
  "_$_9type_info@0x00360C28",
  "_$_9type_info@0x00361488",
  "_$_9type_info@0x00385260",
  "_$_9type_info@0x00394B38",
  "DPRINT@0x003D1658",
  "DPRINT@0x003D1690",
  "fiprintf@0x003DC9F8",
  "fiprintf@0x003E5D30",
  "WaitDma@0x003FDE30",
  "WatchDma@0x003FDEA0",
  "CheckAddress@0x003FDF28",
  "sceDevVu0Pause@0x003FE6A8",
  "sceDevVu0PutDBit@0x003FE758",
...
571

```

## [47] Recompile SSX3 ELF to C++
```
cd /tmp && ./PS2Recomp/out/build/ps2xRecomp/ps2_recomp /tmp/ssx3.toml 2>&1 | tail -60
```
output:
```
  [warning] control-flow function=sub_003F4A78 addr=0x3f4b90 - unresolved JR/JALR at 0x3f4b90; promoted 124 fallback entries
  [warning] control-flow function=sub_003F5F88 addr=0x3f5ff4 - unresolved JR/JALR at 0x3f5ff4; promoted 46 fallback entries
  [warning] control-flow function=sub_003F63F0 addr=0x3f6458 - unresolved JR/JALR at 0x3f6458 0x3f647c; promoted 60 fallback entries
  [warning] control-flow function=sub_003F7DE0 addr=0x3f7e08 - unresolved JR/JALR at 0x3f7e08 0x3f7e24 0x3f7e3c; promoted 44 fallback entries
  [warning] control-flow function=sub_003F6E98 addr=0x3f6f3c - unresolved JR/JALR at 0x3f6f3c 0x3f6f4c 0x3f6fe4 0x3f7038 0x3f70a4 0x3f711c 0x3f7138 0x3f7180 0x3f7198 0x3f7250 0x3f7788 0x3f77c4; promoted 600 fallback entries
  [warning] control-flow function=sub_003F80E0 addr=0x3f8124 - unresolved JR/JALR at 0x3f8124; promoted 38 fallback entries
  [warning] control-flow function=sub_003F8720 addr=0x3f874c - unresolved JR/JALR at 0x3f874c; promoted 18 fallback entries
  [warning] control-flow function=sub_003F8768 addr=0x3f8794 - unresolved JR/JALR at 0x3f8794; promoted 18 fallback entries
  [warning] control-flow function=sub_003F9698 addr=0x3f97e4 - unresolved JR/JALR at 0x3f97e4; promoted 96 fallback entries
  [warning] control-flow function=sub_003F9B38 addr=0x3f9c28 - unresolved JR/JALR at 0x3f9c28; promoted 68 fallback entries
  [warning] control-flow function=sub_003F99B8 addr=0x3f9b04 - unresolved JR/JALR at 0x3f9b04; promoted 96 fallback entries
  [warning] control-flow function=sub_003F9818 addr=0x3f9988 - unresolved JR/JALR at 0x3f9988; promoted 104 fallback entries
  [warning] control-flow function=sub_003F9C48 addr=0x3f9d74 - unresolved JR/JALR at 0x3f9d74 0x3f9d98; promoted 94 fallback entries
  [warning] control-flow function=sub_003F9DC0 addr=0x3f9ed8 - unresolved JR/JALR at 0x3f9ed8; promoted 80 fallback entries
  [warning] control-flow function=sub_003F9F00 addr=0x3fa018 - unresolved JR/JALR at 0x3fa018; promoted 80 fallback entries
  [warning] control-flow function=sub_003F87B0 addr=0x3f87dc - unresolved JR/JALR at 0x3f87dc 0x3f8d04 0x3f8d58 0x3f8dc0 0x3f8df4 0x3f9084 0x3f90c8 0x3f91b4 0x3f91d0; promoted 662 fallback entries
  [warning] control-flow function=sub_003FA040 addr=0x3fa0a0 - unresolved JR/JALR at 0x3fa0a0 0x3fa0f8 0x3fa148; promoted 100 fallback entries
  [warning] control-flow function=sub_003FA818 addr=0x3fa970 - unresolved JR/JALR at 0x3fa970 0x3fa9b0 0x3faa0c 0x3faa50 0x3faaa8 0x3fab2c 0x3fab70 0x3fac0c 0x3fa
... [8315 chars]
```

## [48] Rerun recomp, extract summary stats
```
cd /tmp && ./PS2Recomp/out/build/ps2xRecomp/ps2_recomp /tmp/ssx3.toml > /tmp/recomp_log.txt 2>&1; echo "exit=$?"; grep -n -i -E "unhandled|unsupported|unknown instruction|failed|error|summary|total|functions|TODO" /tmp/recomp_log.txt | grep -v "control-flow" | head -n 40; echo ===; wc -l /tmp/recomp_log.txt; ls /tmp/output 2>/dev/null | head
```
output:
```
exit=0
3:[recompiler] extracted 8143 functions, 0 symbols, 81 sections, 0 relocations
4:[recompiler] recompiling 8143 functions
7:[recompiler] generated function header file: "/tmp/output/ps2_recompiled_functions.h"
10:[recompiler] generated function registration file: "/tmp/output/register_functions.cpp"
14:Functions discovered: 8143
16:Functions processed: 8143, recompiled: 8017, stubs: 126, skipped: 0, decode failures: 0
18:Generated functions: 8143
20:Unhandled instructions: 0
22:Warnings: 3594, errors: 0
===
3623 /tmp/recomp_log.txt
ps2_recompiled_functions.h
ps2_recompiled_stubs.h
register_functions.cpp
sub_00100008_0x100008.cpp
sub_001001C8_0x1001c8.cpp
sub_00100348_0x100348.cpp
sub_00100610_0x100610.cpp
sub_00100680_0x100680.cpp
sub_00101310_0x101310.cpp
sub_001013A8_0x1013a8.cpp

```

## [49] Show summary block and TODO inventory
```
sed -n '1,30p' /tmp/recomp_log.txt; echo ===; grep -r -o -h "TODO_NAMED([A-Za-z0-9_:]*)" /tmp/output/*.cpp 2>/dev/null | sort | uniq -c | sort -rn | head -n 25; echo ===; grep -r -l "TODO" /tmp/output/*.cpp 2>/dev/null | wc -l
```
output:
```
[recompiler] parsing config
[recompiler] parsing ELF
[recompiler] extracted 8143 functions, 0 symbols, 81 sections, 0 relocations
[recompiler] recompiling 8143 functions
[recompiler] collected 391176 resumable entry point(s) across 6732 owner function(s)
[recompiler] recompilation pass completed
[recompiler] generated function header file: "/tmp/output/ps2_recompiled_functions.h"
[recompiler] generating function output with 19 worker(s)
[recompiler] wrote individual function files to /tmp/output/
[recompiler] generated function registration file: "/tmp/output/register_functions.cpp"
[recompiler] generated stub header file: "/tmp/output/ps2_recompiled_stubs.h"

========== PS2Recomp report ==========
Functions discovered: 8143
Symbols: 0, sections: 81, relocations: 0
Functions processed: 8143, recompiled: 8017, stubs: 126, skipped: 0, decode failures: 0
Additional entrypoints: 391176
Generated functions: 8143
Indirect fallback promotions: 3594 (724768 fallback entries)
Unhandled instructions: 0
Correctness-critical guest fallbacks: 0, failures: 0
Warnings: 3594, errors: 0

Events:
  [info] config - Parsing toml file: /tmp/ssx3.toml
  [info] elf - ELF entry point: 0x100008
  [info] elf - BSS range: 0x4a4c00 - 0x53eadc (size 0x99edc), gp=0x0
  [warning] control-flow function=sub_00100348 addr=0x1003b0 - unresolved JR/JALR at 0x1003b0 0x1003f4; promoted 178 fallback entries
  [warning] control-flow function=sub_00100680 addr=0x100998 - unresolved JR/JALR at 0x100998 0x100c88 0x100d34 0x100d78 0x100f24 0x101078 0x1011ac; promoted 804 fallback entries
  [warning] control-flow function=sub_001013A8 addr=0x101470 - unresolved JR/JALR at 0x101470 0x1015c8 0x1015e8; promoted 184 fallback entries
===
===
1

```

## [50] Inventory runtime TODOs and COP2 use
```
grep -rl "TODO" /tmp/output/*.cpp | head; echo ===; grep -r -o -h "TODO[A-Za-z_]*([A-Za-z0-9_:]*)" /tmp/output/*.cpp /tmp/output/*.h 2>/dev/null | sort | uniq -c | sort -rn | head; echo ===COP2===; grep -r -l -i "cop2\|lqc2\|vadd\|vcallms\|qmfc2\|c2_" /tmp/output/*.cpp 2>/dev/null | wc -l; ls /tmp/output/*.cpp | wc -l
```
output:
```
/tmp/output/register_functions.cpp
===
===COP2===
476
8144

```

## [51] Check syscall path and VU0 macro usage
```
grep -n "TODO" /tmp/output/register_functions.cpp | head -5; echo ===; grep -r -o -h -i "handleSyscall([^)]*)" /tmp/output/sub_*.cpp 2>/dev/null | sort | uniq -c | sort -rn | head -8; echo ===COP2-sample===; grep -r -h -o -i "lqc2\|sqc2\|vadd\|vsub\|vmul\|vmadd\|vcallms\|vcallmsr\|c2_[a-z0-9_]*" /tmp/output/sub_00100008_0x100008.cpp 2>/dev/null | sort | uniq -c | head; echo; grep -c -i "cop2\|VU0\|VADD\|LQC2" /tmp/output/sub_*.cpp 2>/dev/null | grep -v ":0" | wc -l
```
output:
```
4:#include "ps2_recompiled_stubs.h"//this will give duplicated erros because runtime maybe has it define already, just delete the TODOS ones
===
    165 handleSyscall(rdram, ctx, 0x0u)
===COP2-sample===

484

```
