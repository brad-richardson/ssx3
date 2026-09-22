#!/bin/bash
# I23 evidence extracts (I21 method). Full consoles stay on SSD; evidence gets extracts.
export COPYFILE_DISABLE=1
W="/Volumes/Extreme SSD/ps2x-i23"
E="local/research/I23/logs"
L="$W/logs/launch-v1-console.log"
D="$W/logs/launch-v1-dedup.log"
grep -v "GetWindowScaleDPI" "$L" | grep -v "diag:dormant" > "$D"
echo "dedup: $(wc -l < "$D") lines"
FULL_SHA=$(shasum -a 256 "$L" | cut -d' ' -f1)
DEDUP_SHA=$(shasum -a 256 "$D" | cut -d' ' -f1)
{ echo "# I23 probe-1 non-sema extract (deterministic): full=$FULL_SHA dedup=$DEDUP_SHA";
  echo "# method: grep -v GetWindowScaleDPI | grep -v diag:dormant | grep -v diag:sema";
  grep -v "diag:sema" "$D"; } > "$E/launch-v1-console.diag-extract.log"
{ echo "# I23 probe-1 creator transcript COMPLETE (39 lines): full=$FULL_SHA";
  grep -n "diag:sema-create" "$L"; } > "$E/launch-v1-console.create-extract.log"
{ echo "# I23 probe-1 sema extract: full=$FULL_SHA sema-total=$(grep -c 'diag:sema]' "$L")";
  echo "## Part A: complete non-31 (from dedup)";
  grep "diag:sema]" "$D" | grep -v "id=31 ";
  echo "## Part B: id=31 samples (head/tail 10 waits + 10 signals, full log)";
  grep "op=wait id=31 " "$L" | head -10; echo "..."; grep "op=wait id=31 " "$L" | tail -10;
  grep "op=signal id=31 " "$L" | head -10; echo "..."; grep "op=signal id=31 " "$L" | tail -10;
  echo "## Part C: full-log per-id counts + waker splits";
  grep -oE "op=(wait|signal) id=[0-9]+" "$L" | grep -oE "id=[0-9]+" | sort -t= -k2 -n | uniq -c;
  for id in 26 30 31 32; do echo "-- wakers id=$id"; grep "op=signal id=$id " "$L" | grep -oE "waker=-?[0-9]+" | sort | uniq -c; done; } > "$E/launch-v1-console.sema-extract.log"
{ echo "# I23 probe-1 vector + title-trace + delivery tails (with line numbers): full=$FULL_SHA";
  grep -n "MPEG:vector\|MPEG:feed-trace" "$L";
  grep -n "0x4029d0\|0x3b0b10\|0x3b0b40\|0x3b06b0" "$L" | cut -c1-400; } > "$E/launch-v1-delivery.log"
grep -h "diag:frame" "$L" > "$E/launch-v1-frame.log"
{ echo "full-sha=$FULL_SHA"; echo "dedup-sha=$DEDUP_SHA";
  wc -l "$L" "$D";
  for c in "diag:sema-create" "diag:sema]" "diag:cd" "cd:callback" "diag:dormant" "diag:stub]" "diag:syscall]" "diag:thread]" "diag:frame" "diag:stacks" "WARNING" "without FFmpeg" "sceCdSt" "0x4029d0" "0x3b1028" "MPEG:vector" "MPEG:feed-trace"; do printf "%s: " "$c"; grep -c "$c" "$L" || true; done; } > "$E/launch-v1-console.sizes"
L4="$W/logs/launch-v4-console.log"
V4_SHA=$(shasum -a 256 "$L4" | cut -d' ' -f1)
{ echo "# I23 probe-2 (V4) vector + title-trace (with line numbers): full=$V4_SHA lines=$(wc -l < "$L4")";
  grep -n "MPEG:vector\|MPEG:feed-trace" "$L4"; } > "$E/launch-v4-vector.log"
echo EXTRACTS-DONE
