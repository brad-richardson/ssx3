# E30 Mission 1 — predictions (written before any harness run)

Source facts (from bytes + `MPEG.cpp` at `3adc0478`, read-only):
- Feed vector `local/research/E22/observed/parser-input.bin`: 5,040 B,
  sha256 `cde8a830…2a1c875a`. Start-code scan: seq_hdr@0 (512x448,
  framerate_code 4), ext, GOP@68, picture@76 (temporal_ref 0, type 3 = B),
  slices 0x01..0x1c (28/28 rows present), chunk ends mid-frame; last 12 B
  are the guest's zero padding (5,028 ES + 12 zeros, E24/E27).
- No pack (BA), system (BB), program-end (B9), PES (BD/E0-EF) codes: the
  input is raw elementary stream. `sceMpegAddBs` -> `feedElementaryStream`
  -> FFmpeg `mplex2video` parser is the correct path, not a mis-framing.
- E26: the terminating start code `00 00 01 00` sits at guest `0xd49b1c`,
  i.e. inside chunk 2 (the queue head `0xd49b14`, E27/E28).
- FFmpeg `mpegvideo` parser emits a packet only when the next start code
  after a picture start delimits the frame. An unterminated final picture
  is held: consumed == offered, packets == 0.

## Candidate verdicts predicted

| ID | Candidate | Prediction |
|----|-----------|------------|
| (a) | parser needs more bytes; second chunk never requested (host latch) | SUPPORTED: H1 reproduces 5040/0/0; H2 (vector + terminator) yields >= 1 packet. Latch side already in E27 + boot logs (feedES x1, GetPicture x1 per movie). |
| (b) | ES-vs-PS mis-framing | EXCLUDED by the scan above (pure ES) + code path. Harness cross-check: H2 packets >= 1 with the ES parser proves the parser choice right. |
| (c) | no-FFmpeg stub build | EXCLUDED twice: E18 `configure-command.json` has `PS2X_ENABLE_FFMPEG=ON` and E29 built on that recipe; `[MPEG:feed]` lines exist in e29b boot log and that format string exists ONLY in the `#if PS2X_HAS_FFMPEG` branch. Harness N/A (would print "built without FFmpeg" instead). |
| (d) | correct behavior (movie really needs more data first) | SUPPORTED as the parser half: 0 packets from one unterminated chunk is what a correct parser does. The DEFECT is (a): the runtime never feeds chunk 2. (a)+(d) jointly, not either alone. |

## Harness runs (standalone copy of `MpegFfmpegDecoder::feed`, logic-identical)

| Run | Input | parsed | packets | frames | note |
|-----|-------|--------|---------|--------|------|
| H1 | vector (5,040 B) | 5040 | 0 | 0 | reproduces the boot closure |
| H2a | vector + `00 00 01 00` + 64 zero bytes | 5108 | >= 1 | 0 | terminator releases packet 1; B-frame with no refs yields no frame |
| H2b | vector + `00 00 01 00` + pic-hdr + `00 00 01 01` + 128 zero bytes | 5176+ | >= 1 | 0 | second frame incomplete -> still held |
| H3 | vector, then `flush()` | 5040 | (1 interned) | 0 or 1 | SPLIT: 0 if decoder drops unreferenced B, 1 if drain forces it out (I24 "flush-serve" leans 1). Settles a fix-design question, not (a)/(d). |
| H4 | vector split 2500/2540 in two `feed()` calls | 5040 | 0 | 0 | chunking is irrelevant; only the terminator matters |

Falsifiers: H1 packets > 0 kills (d) and reopens (b). H2 packets == 0 kills
"parser healthy" and reopens parser misconfiguration. H4 != H1 implicates
the `feed()` loop itself (cursor/remaining accounting).
