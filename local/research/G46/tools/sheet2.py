import sys
from PIL import Image, ImageDraw
out=sys.argv[1]; files=sys.argv[2:]; cols=2; w,h=512,384
rows=(len(files)+cols-1)//cols
S=Image.new('RGB',(cols*w,rows*(h+14)),'black'); d=ImageDraw.Draw(S)
for i,f in enumerate(files):
    im=Image.open(f).convert('RGB'); 
    x,y=(i%cols)*w,(i//cols)*(h+14)
    d.text((x+2,y),f.split('/')[-1]+' %dx%d'%im.size,fill='yellow')
    S.paste(im.resize((w,h)),(x,y+14))
S.save(out)
