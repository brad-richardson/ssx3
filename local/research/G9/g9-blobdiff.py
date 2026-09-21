import struct, sys
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
b = open(sys.argv[1],'rb').read(); n = len(b); o = 8
(ver, state_size, s_off, s_sz, crc, sw, sh, sh_off, sh_sz) = struct.unpack_from('<9I', b, o); o += 36
o += s_sz + sh_sz + state_size
blobs = [bytes(b[o:o+8192])]; o += 8192
while o < n:
    pid = b[o]; o += 1
    if pid == 0:
        o += 1; sz = u32(b,o); o += 4 + sz
    elif pid == 1: o += 1
    elif pid == 2: o += 4
    elif pid == 3: blobs.append(bytes(b[o:o+8192])); o += 8192
print(f"n_blobs={len(blobs)} (idx0=header regs0)")
for i in range(1, len(blobs)):
    a, r = blobs[0], blobs[i]
    diffs = [j for j in range(8192) if a[j] != r[j]]
    print(f"blob{i}: ndiff_bytes={len(diffs)} offsets={[hex(j) for j in diffs[:16]]}")
    for j in diffs[:8]:
        print(f"   off {hex(j)}: header=0x{a[j]:02x} blob{i}=0x{r[j]:02x}")
