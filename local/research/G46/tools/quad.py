import sys
from PIL import Image, ImageDraw
out=sys.argv[1]; items=[a.split('=',1) for a in sys.argv[2:]]
W,H=512,448
S=Image.new('RGB',(W*len(items),H+16),'black'); d=ImageDraw.Draw(S)
for i,(lab,p) in enumerate(items):
    im=Image.open(p).convert('RGB').resize((W,H))
    S.paste(im,(i*W,16)); d.text((i*W+4,2),lab,fill='yellow')
S.save(out, optimize=True)
