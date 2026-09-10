#!/usr/bin/env python3
"""Minimal read-only PINE client for a running PCSX2 (live EE memory reads).

PINE must be enabled in the emulator profile. Reads are batched into one request
per call. Addresses are EE physical offsets (0 .. 32 MiB), matching eeMemory.bin
offsets in save states. Nothing here writes emulator memory.
"""
import glob
import os
import socket
import struct

MAX_PACKET = 650000


def socket_path(slot=28011):
    suffix = "" if slot == 28011 else f".{slot}"
    for base in (os.environ.get("XDG_RUNTIME_DIR"), os.environ.get("TMPDIR"), "/tmp"):
        if base and os.path.exists(os.path.join(base, "pcsx2.sock" + suffix)):
            return os.path.join(base, "pcsx2.sock" + suffix)
    found = glob.glob("/var/folders/*/*/T/pcsx2.sock" + suffix) + glob.glob("/tmp/pcsx2.sock" + suffix)
    if not found:
        raise FileNotFoundError("PCSX2 PINE socket not found; is PINE enabled and PCSX2 running?")
    return found[0]


class Pine:
    def __init__(self, path=None):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(path or socket_path())
        self.sock.settimeout(10)

    def close(self):
        self.sock.close()

    def _request(self, body):
        packet = struct.pack("<I", len(body) + 4) + body
        if len(packet) > MAX_PACKET:
            raise ValueError("PINE packet too large")
        self.sock.sendall(packet)
        header = self._recv(4)
        size = struct.unpack("<I", header)[0]
        reply = self._recv(size - 4)
        if reply[0] != 0:
            raise RuntimeError("PINE request failed")
        return reply[1:]

    def _recv(self, n):
        chunks = bytearray()
        while len(chunks) < n:
            chunk = self.sock.recv(n - len(chunks))
            if not chunk:
                raise ConnectionError("PINE connection closed")
            chunks.extend(chunk)
        return bytes(chunks)

    def status(self):
        return {0: "running", 1: "paused", 2: "shutdown"}.get(struct.unpack("<I", self._request(b"\x0f"))[0])

    def title(self):
        return self._request(b"\x0b")[4:].split(b"\0")[0].decode()

    def game_id(self):
        return self._request(b"\x0c")[4:].split(b"\0")[0].decode()

    def read(self, address, length):
        """Read `length` bytes starting at EE offset `address` using batched 64-bit reads."""
        out = bytearray()
        start = address & ~7
        end = (address + length + 7) & ~7
        cursor = start
        while cursor < end:
            count = min((end - cursor) // 8, 32000)
            body = b"".join(b"\x03" + struct.pack("<I", cursor + 8 * i) for i in range(count))
            out.extend(self._request(body))
            cursor += 8 * count
        return bytes(out[address - start:address - start + length])

    def read_u32(self, address):
        return struct.unpack("<I", self._request(b"\x02" + struct.pack("<I", address)))[0]

    def read_floats(self, address, count):
        return struct.unpack(f"<{count}f", self.read(address, 4 * count))


if __name__ == "__main__":
    p = Pine()
    print(p.status(), p.game_id(), p.title())
