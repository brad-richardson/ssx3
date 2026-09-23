# pairsheet.py out.png scale x0,y0,x1,y1 tick...  -> rows: cpu | par (same box) per tick
import sys
from PIL import Image, ImageDraw
out, sc, box = sys.argv[1], float(sys.argv[2]), tuple(int(v) for v in sys.argv[3].split(','))
ticks = sys.argv[4:]
D = '/Users/brad/dev/ssx3-work/G46/run/' + __import__('os').environ.get('SH','shadow-g46a')
rows=[]
for t in ticks:
    a = Image.open(f'{D}/cpu-{t}.png').convert('RGB').crop(box)
    b = Image.open(f'{D}/par-{t}.png').convert('RGB').crop(box)
    rows.append((t,a,b))
w=int((box[2]-box[0])*sc); h=int((box[3]-box[1])*sc)
S=Image.new('RGB',(2*w+6,len(rows)*(h+14)),'black'); d=ImageDraw.Draw(S)
for i,(t,a,b) in enumerate(rows):
    y=i*(h+14); d.text((2,y),f'tick {t}: cpu | paraLLEl',fill='yellow')
    S.paste(a.resize((w,h),Image.NEAREST),(0,y+14)); S.paste(b.resize((w,h),Image.NEAREST),(w+6,y+14))
S.save(out)
