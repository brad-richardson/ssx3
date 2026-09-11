# SSX 3 locale strings

The NTSC-U transport descriptions are UTF-16LE strings in
`DATA/LOCALE/CMNAMER.LOC`. Snow Jam's description is index **549**, hash
**0x0af521c1**, absolute locale-file byte offset **51,734**, with a **158-byte**
slot. Course names in the executable and this description are separate edits.

The parser in `tools/patch_locale.py` follows the pinned SSX-Library `LOC.cs`
layout and checks section sizes, string boundaries, hashes' indices and
terminators against the actual files. It successfully parses all five locale
files on the supplied disc:

| File | Strings |
| --- | ---: |
| CMNAMER.LOC | 1,386 |
| CRAMER.LOC | 160 |
| FEAMER.LOC | 829 |
| OVAMER.LOC | 800 |
| TOSAMER.LOC | 178 |

## Layout

- `LOCH`: 20 bytes; size at +4, unknown word at +8, version 1 at +12,
  absolute `LOCL` offset at +16.
- Optional `LOCT`: 16-byte header followed by pairs of little-endian u32
  `(hash, string_index)` up to the `LOCL` offset. Its size word is the header
  size, not the entire section size. Other header words remain untouched.
- `LOCL`: 16-byte header containing section size, unknown word and string
  count. Then one u32 offset per string, relative to the `LOCL` start.
- Nonempty strings are UTF-16LE followed by two zero code units (four zero
  bytes). Empty strings may occupy just one zero code unit (two bytes).
  Physical slot limits come from the next distinct offset, not index order.

The patcher accepts replacements only when they fit the existing slot, counting
UTF-16 bytes and both terminators. It preserves every index, hash and offset;
shared slots require every alias to be explicitly assigned the same text. A
new ISO is streamed and its full SHA-256 checked by readback. Existing outputs
are refused. Longer replacements need a future table-rebuild implementation.

```sh
python3 tools/patch_locale.py SSX3.iso --find 'Snow Jam'
python3 tools/patch_locale.py SSX3.iso --set '549=Garibaldi from SSX Tricky. Experimental terrain port; race setup in progress.' --output SSX3-description.iso
```

`tools/build_course_image.py` combines the locale edit, executable name edit
and a rebuilt world archive in one image copy. It uses explicit locale indices;
it does not infer which description belongs to an arbitrary event code.
