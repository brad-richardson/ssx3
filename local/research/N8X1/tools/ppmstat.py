import sys
def load(p):
    d=open(p,'rb').read(); parts=d.split(b'\n',3); w,h=map(int,parts[1].split()); return w,h,parts[3]
w,h,a=load(sys.argv[1])
nb=sum(1 for i in range(0,len(a),3) if a[i]|a[i+1]|a[i+2])
print(f"{sys.argv[1]} {w}x{h} nonblack={nb}/{w*h} ({nb/(w*h):.3f})", end='')
if len(sys.argv)>2:
    _,_,b=load(sys.argv[2]); eq=sum(1 for i in range(0,len(a),3) if a[i:i+3]==b[i:i+3]); print(f" equal_px={eq}/{w*h} ({eq/(w*h):.3f})")
else: print()
