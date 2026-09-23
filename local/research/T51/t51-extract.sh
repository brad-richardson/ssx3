#!/usr/bin/env bash
# T51 extract: pull T51 (+T50 dmareg context) lines from a capture emulog.
# PCSX2 emulog lines carry a "[ timestamp]" prefix: match unanchored, strip
# the prefix, then validate every line against the T51 grammars (rejects=0).
set -e
E=${1:-/home/brad/pcsx2-g7/dat-t50/PCSX2/logs/emulog.txt}
OUT=${2:-/home/brad/pcsx2-t4/t51-trace.txt}
grep -E 'st vsync=|sema vsync=|semaid vsync=|irq vsync=|gsreg vsync=|dmareg vsync=|T51_WINDOW|T51_ST_CAP|T51_SEMA_CAP|T51_IRQ_CAP|T51_GS_CAP|T50_DMAREG_CAP|T48_PATHS' "$E" | sed 's/^[^]]*] //' > "$OUT" || true
echo "=== rejects (must be 0) ==="
grep -vcE '^(st vsync=[0-9]+ addr=0x[0-9a-f]+ value=0x[0-9a-f]+ pc=0x[0-9a-f]+ ra=0x[0-9a-f]+ intc=[01]|sema vsync=[0-9]+ pc=0x[0-9a-f]+ ra=0x[0-9a-f]+ call=(SignalSema|iSignalSema|WaitSema|PollSema) id=[0-9]+ m=\+0x(28|2c|4c)|semaid vsync=[0-9]+ w28=0x[0-9a-f]+ w2c=0x[0-9a-f]+ w4c=0x[0-9a-f]+|irq vsync=[0-9]+ cause=0x[0-9a-f]+ ch=(intc|dmac):[0-9]+ handler=0x[0-9a-f]+|gsreg vsync=[0-9]+ reg=(SIGNAL|FINISH|LABEL)|dmareg vsync=[0-9]+ reg=D1_(CHCR|MADR|QWC|TADR) value=0x[0-9a-f]+ pc=0x[0-9a-f]+ ra=0x[0-9a-f]+ a0=|T51_WINDOW tu=(ee|hw|gs) vsync=[0-9]+|T51_(ST|SEMA|IRQ|GS)_CAP vsync=[0-9]+|T50_DMAREG_CAP vsync=[0-9]+|T48_PATHS vsync=[0-9]+ )' "$OUT" || true
echo "=== counts ==="
for pat in 'st vsync=' 'sema vsync=' 'semaid vsync=' 'irq vsync=' 'gsreg vsync=' 'dmareg vsync=' 'T51_WINDOW' 'T51_ST_CAP' 'T51_SEMA_CAP' 'T51_IRQ_CAP' 'T51_GS_CAP' 'T50_DMAREG_CAP'; do
  printf '%-16s %s\n' "$pat" "$(grep -cE "$pat" "$OUT" || true)"
done
echo "=== sha ==="
sha256sum "$OUT"
ls -la "$OUT" "$E"
echo T51_EXTRACT_DONE
