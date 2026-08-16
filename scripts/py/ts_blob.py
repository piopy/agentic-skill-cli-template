import base64
def varint(n):
    out=b""
    while True:
        b7=n&0x7f; n>>=7
        if n: out+=bytes([b7|0x80])
        else: out+=bytes([b7]); break
    return out
def _fld(f,w,v):
    if w==2: return varint(f<<3|w)+varint(len(v))+v
    return varint(f<<3|w)+varint(v)
def _dm(fn,y,m,d): return _fld(fn,2,_fld(1,0,y)+_fld(2,0,m)+_fld(3,0,d))
def build_ts(gaia,label,y1,m1,d1,y2,m2,d2):
    i2=_fld(1,0,3)
    inner_i2=_fld(1,2,i2)+_fld(1,2,i2)+_fld(2,0,0)
    place=_fld(2,2,_fld(6,2,gaia.encode())+_fld(7,2,label.encode()))+_fld(3,2,b"")
    dates=_fld(2,2,_dm(1,y1,m1,d1)+_dm(2,y2,m2,d2)+_fld(3,0,3))+_fld(6,2,_fld(1,0,1))
    room=_fld(1,2,place)+_fld(2,2,dates)
    cur=_fld(1,2,_fld(7,2,b"EUR")+_fld(12,2,_fld(1,0,1)))+_fld(3,2,b"")
    return base64.b64encode(_fld(1,0,1)+_fld(2,2,inner_i2)+_fld(3,2,room)+_fld(5,2,cur)).decode()
