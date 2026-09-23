#!/usr/bin/env bash
# T62 extract: appx + axfirst + v1b0 + extended appsum + T61 families + markers.
set -e
E=${1:-/home/brad/pcsx2-g7/dat-t57/PCSX2/logs/emulog.txt}
OUT=${2:-/home/brad/pcsx2-t4/t62-trace.txt}
grep -E 'appx vsync=|axfirst vsync=|v1b0 vsync=|app vsync=|appsum vsync=|apc vsync=|tpl vsync=|tplrearm vsync=|T60_CAP|T61_CAPSUM|T62_CAP|ebw vsync=|ebwlast vsync=|ebwend vsync=|T58_CAP|T58_CAPLAST|vu0call vsync=|vif0op vsync=|T57_CAP|T51C_WINDOW|T51C_CAP|T48_PATHS' "$E" | sed 's/^[^]]*] //' > "$OUT" || true
REGS14='a0=[0-9a-f]+ a1=[0-9a-f]+ a2=[0-9a-f]+ a3=[0-9a-f]+ v0=[0-9a-f]+ v1=[0-9a-f]+ s0=[0-9a-f]+ s1=[0-9a-f]+ s2=[0-9a-f]+ s3=[0-9a-f]+ s4=[0-9a-f]+ s5=[0-9a-f]+ s6=[0-9a-f]+ s7=[0-9a-f]+'
HIST='mode_hist=(-|[0-9]+:[0-9]+(,[0-9]+:[0-9]+)*)'
APCS='pc=0x[0-9a-f]+:[0-9]+(,pc=0x[0-9a-f]+:[0-9]+)*'
echo "=== rejects (want only bare-apc, see T61) ==="
grep -vE "^(appx vsync=[0-9]+ site=0x[0-9a-f]+ count=[0-9]+ t0=0x[0-9a-f]+ tw0=0x[0-9a-f]+ tw1=0x[0-9a-f]+ tw2=0x[0-9a-f]+ tw3=0x[0-9a-f]+ tw4=0x[0-9a-f]+ ra=0x[0-9a-f]+|axfirst vsync=[0-9]+ site=0x[0-9a-f]+ v1=[0-9]+ t0=0x[0-9a-f]+ tw0=0x[0-9a-f]+ tw1=0x[0-9a-f]+ tw2=0x[0-9a-f]+ s0=0x[0-9a-f]+ a0=0x[0-9a-f]+ ra=0x[0-9a-f]+|v1b0 vsync=[0-9]+ addr=0x[0-9a-f]+ vaddr=0x[0-9a-f]+ value=0x[0-9a-f]+ pc=0x[0-9a-f]+ ra=0x[0-9a-f]+ $REGS14|app vsync=[0-9]+ count=[0-9]+ t0=0x[0-9a-f]+ tw0=0x[0-9a-f]+ tw1=0x[0-9a-f]+ tw2=0x[0-9a-f]+ tw3=0x[0-9a-f]+ tw4=0x[0-9a-f]+ s4=0x[0-9a-f]+ t1=0x[0-9a-f]+ ra=0x[0-9a-f]+|appsum vsync=[0-9]+ n_app=[0-9]+ n_tpl=[0-9]+ $HIST ax=[0-9]+,[0-9]+,[0-9]+|apc vsync=[0-9]+ $APCS|tpl vsync=[0-9]+ addr=0x[0-9a-f]+ old=0x[0-9a-f]+ new=0x[0-9a-f]+ tw0=0x[0-9a-f]+ tw1=0x[0-9a-f]+ pc=0x[0-9a-f]+ ra=0x[0-9a-f]+ $REGS14|tplrearm vsync=[0-9]+ old=0x[0-9a-f]+ new=0x[0-9a-f]+|T60_CAPAPP vsync=[0-9]+|T60_CAPTPL vsync=[0-9]+|T61_CAPSUM vsync=[0-9]+|T62_CAPAX vsync=[0-9]+|T62_CAPV vsync=[0-9]+|ebw vsync=[0-9]+ addr=0x[0-9a-f]+ value=0x[0-9a-f]+ via=(store|spr-from|sif0|dma-ch7|dma-ch3) src=0x[0-9a-f]+ vaddr=0x[0-9a-f]+ pc=0x[0-9a-f]+ ra=0x[0-9a-f]+ $REGS24B|ebwlast vsync=[0-9]+ addr=0x[0-9a-f]+ value=0x[0-9a-f]+ via=(store|spr-from|sif0|dma-ch7|dma-ch3) pc=0x[0-9a-f]+ ra=0x[0-9a-f]+|ebwend vsync=[0-9]+ b0=(0x[0-9a-f]+ ){3}0x[0-9a-f]+ b1=(0x[0-9a-f]+ ){3}0x[0-9a-f]+|T58_CAP vsync=[0-9]+ addr=0x[0-9a-f]+|T58_CAPLAST vsync=[0-9]+|vu0call vsync=[0-9]+ caller_pc=0x[0-9a-f]+ via=(cop2|vif0|unknown) startPC=0x[0-9a-f]+ cycles=[0-9]+ vi1=0x[0-9a-f]+ vi2=0x[0-9a-f]+( ms=0x[0-9a-f]+)?( mark=sub_0037D968)?( end=abort)?|vif0op vsync=[0-9]+ op=[A-Z]+ n=[0-9]+|T57_CAP vsync=[0-9]+|T51C_WINDOW vsync=[0-9]+|T51C_CAP vsync=[0-9]+|T48_PATHS vsync=[0-9]+ )" "$OUT" || true
echo "=== counts ==="
for pat in 'appx vsync=' 'axfirst vsync=' 'v1b0 vsync=' 'app vsync=' 'appsum vsync=' 'apc vsync=' 'tpl vsync=' 'tplrearm vsync=' 'T60_CAP' 'T61_CAPSUM' 'T62_CAP' 'ebw vsync=' 'ebwlast vsync=' 'ebwend vsync=' 'vu0call vsync=' 'vif0op vsync=' 'T51C_WINDOW' 'T48_PATHS'; do
  printf '%-20s %s\n' "$pat" "$(grep -cE "$pat" "$OUT" || true)"
done
echo "=== sha ==="
sha256sum "$OUT"
ls -la "$OUT" "$E"
echo T62_EXTRACT_DONE
