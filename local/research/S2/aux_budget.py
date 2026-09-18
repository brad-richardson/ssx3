#!/usr/bin/env python3
"""Offline confirmation of the S2 diagnosis: how many bytes one replay pops
out of Dolphin's 2 MiB FIFO aux buffer, and therefore at which replay an
unpaired RunFifo<false> loop runs off the end.

Parses a FifoDataFile v6 artefact (`EVENTS.jsonl.fifo` beside a capture trace)
and walks frame 0's GP command stream with a port of Dolphin's command-size
decoder (`VideoCommon/OpcodeDecoding.h` detail::RunCommand) plus the vertex
size tables (`VertexLoader_{Position,Normal,Color,TextCoord}.h`,
`VertexLoaderBase::GetVertexSize`). Read-only; prints a table.

In deterministic-GPU-thread mode the aux buffer is the ONLY source for
indexed-XF payloads and display-list bodies on the execute pass
(`XFStructs.cpp` LoadIndexedXF, `OpcodeDecoding.h` OnDisplayList), and
`FifoManager::PopFifoAuxBuffer` never bounds-checks or rewinds.
"""
import struct
import sys

FILE_ID = 0x0D01F1F0
FIFO_AUX_SIZE = 2 * 1024 * 1024

HEADER = struct.Struct("<3I QI QI QI QI QII QI II 8s 24s")
FRAME = struct.Struct("<QIII QI 32s")
MEMUPDATE = struct.Struct("<II QI B 3s")

MATINDEX_A, MATINDEX_B, VCD_LO, VCD_HI = 0x30, 0x40, 0x50, 0x60
VAT_A, VAT_B, VAT_C, ARRAY_BASE, ARRAY_STRIDE = 0x70, 0x80, 0x90, 0xA0, 0xB0

ELEM = {0: 1, 1: 1, 2: 2, 3: 2, 4: 4, 5: 4, 6: 4, 7: 4}  # ComponentFormat -> bytes
COLOR_DIRECT = {0: 2, 1: 3, 2: 4, 3: 2, 4: 3, 5: 4}      # ColorFormat -> bytes


def bits(value, lo, n):
    return (value >> lo) & ((1 << n) - 1)


class CP:
    """Just enough CPState to size vertices (CPMemory.h TVtxDesc / VAT)."""

    def __init__(self, cp_mem):
        self.vcd_lo = cp_mem[VCD_LO]
        self.vcd_hi = cp_mem[VCD_HI]
        self.vat = [[cp_mem[VAT_A + i], cp_mem[VAT_B + i], cp_mem[VAT_C + i]]
                    for i in range(8)]

    def load(self, sub_cmd, value):
        cmd, idx = sub_cmd & 0xF0, sub_cmd & 0x0F
        if cmd == VCD_LO:
            self.vcd_lo = value
        elif cmd == VCD_HI:
            self.vcd_hi = value
        elif cmd in (VAT_A, VAT_B, VAT_C) and idx < 8:
            self.vat[idx][(cmd - VAT_A) >> 4] = value

    def vertex_size(self, vat_index):
        g0, g1, g2 = self.vat[vat_index & 7]
        size = bin(self.vcd_lo & 0x1FF).count("1")  # PosMatIdx + 8 TexMatIdx

        pos = bits(self.vcd_lo, 9, 2)
        if pos:
            if pos == 1:
                size += (2 + bits(g0, 0, 1)) * ELEM[bits(g0, 1, 3)]
            else:
                size += 1 if pos == 2 else 2

        nrm = bits(self.vcd_lo, 11, 2)
        if nrm:
            ntb = bits(g0, 9, 1)
            index3 = bits(g0, 31, 1)
            if nrm == 1:
                size += (9 if ntb else 3) * ELEM[bits(g0, 10, 3)]
            else:
                unit = 1 if nrm == 2 else 2
                size += unit * (3 if (index3 and ntb) else 1)

        for i in range(2):
            col = bits(self.vcd_lo, 13 + 2 * i, 2)
            if col:
                fmt = bits(g0, 14 + 4 * i, 3)
                size += COLOR_DIRECT.get(fmt, 0) if col == 1 else (1 if col == 2 else 2)

        for i in range(8):
            tc = bits(self.vcd_hi, 2 * i, 2)
            if not tc:
                continue
            if i == 0:
                elements, fmt = bits(g0, 21, 1), bits(g0, 22, 3)
            elif i <= 3:
                off = 9 * (i - 1)
                elements, fmt = bits(g1, off, 1), bits(g1, off + 1, 3)
            elif i == 4:
                elements, fmt = bits(g1, 27, 1), bits(g1, 28, 3)
            else:
                off = 5 + 9 * (i - 5)
                elements, fmt = bits(g2, off, 1), bits(g2, off + 1, 3)
            size += (1 + elements) * ELEM[fmt] if tc == 1 else (1 if tc == 2 else 2)
        return size


def load_fifo(path):
    blob = open(path, "rb").read()
    h = HEADER.unpack_from(blob, 0)
    (file_id, version, min_loader, bp_off, bp_size, cp_off, cp_size, xf_off, xf_size,
     xfr_off, xfr_size, frame_off, frame_count, flags, tex_off, tex_size,
     mem1, mem2, gameid, _res) = h
    if file_id != FILE_ID:
        raise SystemExit(f"{path}: not a FifoDataFile ({file_id:#x})")
    cp_mem = list(struct.unpack_from(f"<{cp_size}I", blob, cp_off))
    f0 = FRAME.unpack_from(blob, frame_off)
    data_off, data_size, start, end, mu_off, mu_count, _ = f0
    updates = []
    for i in range(mu_count):
        fp, addr, doff, dsize, mtype, _ = MEMUPDATE.unpack_from(blob, mu_off + i * MEMUPDATE.size)
        updates.append((fp, addr, dsize, mtype))
    return dict(version=version, gameid=gameid.rstrip(b"\0").decode(errors="replace"),
                frames=frame_count, cp_mem=cp_mem,
                fifo=blob[data_off:data_off + data_size], start=start, end=end,
                updates=updates, mem1=mem1, mem2=mem2)


def walk(fifo, cp_mem):
    """Port of OpcodeDecoder detail::RunCommand sizing, counting aux traffic."""
    cp = CP(cp_mem)
    n = len(fifo)
    i = 0
    stats = dict(commands=0, nops=0, cp=0, xf=0, bp=0, prims=0, vertices=0,
                 indexed=0, indexed_bytes=0, dls=0, dl_bytes=0,
                 pe_bp=0, unknown=0)
    while i < n:
        op = fifo[i]
        avail = n - i
        if op == 0x00:
            j = i
            while j < n and fifo[j] == 0x00:
                j += 1
            stats["nops"] += j - i
            i = j
            continue
        if op == 0x08:                                   # GX_LOAD_CP_REG
            if avail < 6:
                break
            cp.load(fifo[i + 1], int.from_bytes(fifo[i + 2:i + 6], "big"))
            stats["cp"] += 1
            size = 6
        elif op == 0x10:                                 # GX_LOAD_XF_REG
            if avail < 5:
                break
            cmd2 = int.from_bytes(fifo[i + 1:i + 5], "big")
            stream = ((cmd2 >> 16) & 0xF) + 1
            if avail < 5 + stream * 4:
                break
            stats["xf"] += 1
            size = 5 + stream * 4
        elif op in (0x20, 0x28, 0x30, 0x38):             # GX_LOAD_INDX_A..D
            if avail < 5:
                break
            value = int.from_bytes(fifo[i + 1:i + 5], "big")
            words = ((value >> 12) & 0xF) + 1
            stats["indexed"] += 1
            stats["indexed_bytes"] += words * 4          # buf_size popped from aux
            size = 5
        elif op == 0x40:                                 # GX_CMD_CALL_DL
            if avail < 9:
                break
            dl_size = int.from_bytes(fifo[i + 5:i + 9], "big") & ~31
            stats["dls"] += 1
            stats["dl_bytes"] += dl_size                 # also popped from aux
            size = 9
        elif op == 0x61:                                 # GX_LOAD_BP_REG
            if avail < 5:
                break
            reg = fifo[i + 1]
            if reg in (0x45, 0x47, 0x48):                # SETDRAWDONE / PE_TOKEN / _INT
                stats["pe_bp"] += 1
            stats["bp"] += 1
            size = 5
        elif 0x80 <= op <= 0xBF:                         # primitive
            if avail < 3:
                break
            vsize = cp.vertex_size(op & 0x07)
            count = int.from_bytes(fifo[i + 1:i + 3], "big")
            if avail < 3 + count * vsize:
                break
            stats["prims"] += 1
            stats["vertices"] += count
            size = 3 + count * vsize
        elif op in (0x44, 0x48):                         # metrics / invalidate VC
            stats["commands"] += 1
            i += 1
            continue
        else:
            stats["unknown"] += 1
            i += 1
            continue
        stats["commands"] += 1
        i += size
    stats["consumed"] = i
    stats["total"] = n
    return stats


def main():
    for path in sys.argv[1:]:
        f = load_fifo(path)
        s = walk(f["fifo"], f["cp_mem"])
        aux = s["indexed_bytes"] + s["dl_bytes"]
        print(f"\n=== {path}")
        print(f"  game {f['gameid']!r}  fifo v{f['version']}  frames {f['frames']}  "
              f"frame0 {len(f['fifo'])} B  memory updates {len(f['updates'])}")
        print(f"  walk consumed {s['consumed']}/{s['total']} bytes  unknown opcodes {s['unknown']}")
        print(f"  commands {s['commands']}  prims {s['prims']} ({s['vertices']} verts)  "
              f"cp {s['cp']}  xf {s['xf']}  bp {s['bp']}")
        print(f"  indexed XF loads {s['indexed']} -> {s['indexed_bytes']} B popped from aux")
        print(f"  display lists {s['dls']} -> {s['dl_bytes']} B popped from aux")
        print(f"  PE BP writes (SETDRAWDONE/PE_TOKEN/PE_TOKEN_INT) {s['pe_bp']}")
        print(f"  AUX BYTES PER REPLAY = {aux} ({aux / 1024:.1f} KiB)")
        if aux:
            print(f"  2 MiB / {aux} B = {FIFO_AUX_SIZE / aux:.2f} replays before the "
                  f"unchecked read pointer leaves m_fifo_aux_data[{FIFO_AUX_SIZE}]")


if __name__ == "__main__":
    main()
