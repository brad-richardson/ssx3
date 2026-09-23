# crop.py out.png scale  file:x0,y0,x1,y1[:W,H]  ...   (coords in the file's own pixels;
# W,H = logical size to resample the source to before cropping, e.g. 640,448 for 640x480 PCSX2)
import sys
from PIL import Image, ImageDraw
out=sys.argv[1]; sc=float(sys.argv[2]); tiles=[]
for spec in sys.argv[3:]:
    parts=spec.split(':'); f=parts[0]; box=tuple(int(v) for v in parts[1].split(','))
    im=Image.open(f).convert('RGB')
    if len(parts)>2:
        W,H=(int(v) for v in parts[2].split(',')); im=im.resize((W,H),Image.NEAREST)
    c=im.crop(box); c=c.resize((int(c.width*sc),int(c.height*sc)),Image.NEAREST); tiles.append((f.split('/')[-1],c))
W=max(t[1].width for t in tiles); H=sum(t[1].height+14 for t in tiles)
S=Image.new('RGB',(W,H),'black'); d=ImageDraw.Draw(S); y=0
for n,c in tiles:
    d.text((2,y),n,fill='yellow'); S.paste(c,(0,y+14)); y+=c.height+14
S.save(out)
