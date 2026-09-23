import sys, glob, os
from PIL import Image, ImageDraw
files = sys.argv[2:]
cols = 4; w, h = 256, 224
rows = (len(files)+cols-1)//cols
S = Image.new('RGB', (cols*w, rows*(h+14)), 'black')
d = ImageDraw.Draw(S)
for i, f in enumerate(files):
    im = Image.open(f).convert('RGB').resize((w, h))
    x, y = (i%cols)*w, (i//cols)*(h+14)
    S.paste(im, (x, y+14))
    t = open(f[:-4]+'.txt').read() if os.path.exists(f[:-4]+'.txt') else ''
    import re
    m = re.search(r'tick=(\d+)', t)
    d.text((x+2, y), os.path.basename(f)+' '+(m.group(0) if m else ''), fill='yellow')
S.save(sys.argv[1])
