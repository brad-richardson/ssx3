# X5 Report — Sparse Qwen mechanical index for GB5 glyph replay (ticks 949-950)

## Date: 2026-09-24

## Source inputs

| Input | Size | SHA-256 |
|---|---|---|
| `gb4p4.capture.bin` | 2,752,955,786 bytes | `a6f75fb34fceccf6fd92ad65950d16f05a140cf38a3cc2f028be32e56ad51851` |
| `gb4p4.paths.txt` | 1,982,063 lines (indexed 0..1982062) | — |
| `pklog-gb4p4-1.txt` | 2,000,001 lines (1,989,364 `[pk]` entries) | — |

Path source file: `local/research/GB4/glyph-packet-p6.txt` (34 lines, defines packet 144266 probe).
Prefix checker: `~/dev/ssx3-work/GB4/run/check_packet_prefix_p2.py`.
Capture format: `~/dev/ssx3-work/GB4/PS2Recomp/ps2xRuntime/src/lib/gs/gs_stream_capture.cpp`, `packet()` at line 153-162, `record()` at line 86-121.

## Record layout (from `gs_stream_capture.cpp` lines 86-162)

Each record in the capture file (after 8-byte `"PS2XGSC1"` magic):

| Offset (in record) | Size | Field |
|---|---|---|
| 0 | 4 bytes | `payload_size` (LE32) — length of subsequent payload |
| 4 | 1 byte | `kind` — 1 = GIF packet, 2 = PrivWrite, 3 = Transfer, 4 = VBlank, 5 = NativeUpload, 6 = LocalToHost, 7 = ClearContext |
| 5 | 8 bytes | `tick` (LE64) |
| 13 | 1 byte | `path` (uint8, 0-7) — embedded PATH3 |
| 14 | 4 bytes | `data_size` (LE32) |
| 18 | `data_size` bytes | GIF data (FNV-1a hash is computed over these bytes only, matching `check_packet_prefix_p2.py` line 33: `fnv(rec[14:])`) |

Total record size = 4 (payload_size) + payload_size = 4 + (1 + 8 + 1 + 4 + data_size) = 18 + data_size bytes.

For GIF packet records (kind=1), the FNV-1a is over `rec[14:]` (data_size bytes of GIF payload).

## Path source

`gb4p4.paths.txt` — one line per index, format: `<index> <path>`. Indexed 0-based, exactly 1,982,063 lines. Corrects embedded path metadata defects (e.g., packet 144266: embedded_path=1, corrected_path=3 per `local/research/GB4/glyph-packet-p6.txt` line 8).

## Script invocation

```
python3 local/research/X5/index.py
```

Output (single summary line):

```
[X5] rows=922 first=143805 last=144726 ticks={949: 461, 950: 461} matches=922 mismatches=0 missing_pklog=0 sha_ok=OK paths_ok=OK
```

## Row counts

| Tick | Packets |
|---|---|
| 949 | 461 |
| 950 | 461 |
| **Total** | **922** |

First packet index: 143805. Last packet index: 144726.

## Cross-reference: CSV vs pklog

Comparison key: `(tick, fnv32, length, corrected_path)` matched against pklog tuple `(idx, tick, fnv, len, src)` at the same 0-based GIF packet index.

FNV-1a comparison normalizes pklog FNV strings to 8 lowercase hex digits (pklog omits leading zeros, e.g., `eb4606c` vs `0eb4606c`).

### Summary

| Metric | Count |
|---|---|
| Exact matches | 922 |
| Mismatches | 0 |
| Missing pklog rows | 0 |
| Gaps (missing packet indices in range) | 0 |

### Sample comparison table (first 3, packet 144266, last 3)

| packet_index | tick | record_offset | corrected_path | embedded_path | length | fnv32 (CSV) | pklog fnv | pklog tick | pklen | pksrc | status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 143805 | 949 | 158284846 | 3 | 1 | 1696 | cc6dd8df | cc6dd8df | 949 | 1696 | 3 | match |
| 143806 | 949 | 158286560 | 2 | 1 | 144 | 53ef76a6 | 53ef76a6 | 949 | 144 | 2 | match |
| 143807 | 949 | 158286722 | 2 | 1 | 128 | 67adc41e | 67adc41e | 949 | 128 | 2 | match |
| 144266 | 950 | 158919448 | 3 | 1 | 1696 | cc6dd8df | cc6dd8df | 950 | 1696 | 3 | match |
| 144724 | 950 | 159549385 | 2 | 1 | 48 | fe8f2d45 | fe8f2d45 | 950 | 48 | 2 | match |
| 144725 | 950 | 159549451 | 1 | 1 | 2560 | 0c5fc385 | 0c5fc385 | 950 | 2560 | 1 | match |
| 144726 | 950 | 159552029 | 1 | 1 | 1840 | 0701282f | 0701282f | 950 | 1840 | 1 | match |

### Packet 144266 (known tuple from brief)

| Field | Expected | Actual (CSV) | Match |
|---|---|---|---|
| packet_index | 144266 | 144266 | yes |
| tick | 950 | 950 | yes |
| length (GIF bytes) | 1696 | 1696 | yes |
| fnv32 | cc6dd8df | cc6dd8df | yes |
| corrected_path | 3 | 3 | yes |
| record_offset | — | 158919448 | — |
| embedded_path | 1 (defect) | 1 | yes |

All six fields match the known tuple. The embedded path is 1 (the known path metadata defect), while the corrected path from `gb4p4.paths.txt` is 3, matching `pklog src=3`.

## Full CSV

`local/research/X5/packets-949-950.csv` — 922 data rows, 7 columns: `packet_index, tick, record_offset, corrected_path, embedded_path, length, fnv32`. Sorted by packet index.

## Acceptance criteria

| Criterion | Result |
|---|---|
| Capture SHA matches expected | OK |
| All records length-bounded and reach EOF | OK (no truncation) |
| Paths file has exactly 1,982,063 indexed rows | OK (1,982,063) |
| Every selected CSV tuple matches same-index pklog tuple | 922/922 exact matches |
| Total CSV count is 922 | OK (922 rows) |
| Packet 144266 matches known tuple | OK (all 6 fields match) |
| Script exits nonzero on pin/count failure | Exits 0 (all pass) |
