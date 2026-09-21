import struct,hashlib
from e16_io import read_capture

def packet(path):
    data=read_capture(path); pos=0;tags=[];regs=[]
    while pos+16<=len(data):
        lo,hi=struct.unpack_from('<QQ',data,pos)
        nloop=lo&0x7fff;flg=(lo>>58)&3;nreg=(lo>>60)&15 or 16
        tag=dict(offset=pos,nloop=nloop,flg=flg,nreg=nreg,eop=(lo>>15)&1,lo=hex(lo),hi=hex(hi))
        tags.append(tag);pos+=16
        count=nloop*nreg
        if flg==0:
            end=pos+count*16
            if end>len(data): tag['truncated']=True;break
            for i in range(count):
                reg=(hi>>((i%nreg)*4))&15
                if reg==14:
                    value,address=struct.unpack_from('<QQ',data,pos+i*16)
                    item=dict(offset=pos+i*16,reg=hex(address&255),value=hex(value))
                    if address&255 in [0x4c,0x4d]: item.update(fbp=value&511,fbw=(value>>16)&63,psm=(value>>24)&63)
                    if address&255 in [0x06,0x07]: item.update(tbp=value&0x3fff,tbw=(value>>14)&63,psm=(value>>20)&63)
                    regs.append(item)
            pos=end
        elif flg==1: pos+=(count*8+15)&~15
        elif flg==2: pos+=nloop*16
        else: tag['unsupported']=True;break
    return dict(file=path.name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),parsed_end=pos,tags=tags,registers=regs)
