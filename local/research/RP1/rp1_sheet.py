import sys
from PIL import Image, ImageDraw
# usage: sheet.py out.png cols w h file...
out, cols, w, h = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
files = sys.argv[5:]
rows = (len(files) + cols - 1) // cols
S = Image.new('RGB', (cols * w, rows * (h + 14)), 'black')
d = ImageDraw.Draw(S)
for i, f in enumerate(files):
    im = Image.open(f).convert('RGB').resize((w, h), Image.BILINEAR)
    x, y = (i % cols) * w, (i // cols) * (h + 14)
    S.paste(im, (x, y + 14))
    d.text((x + 2, y + 1), f.split('/')[-1][:40], fill='yellow')
S.save(out)
