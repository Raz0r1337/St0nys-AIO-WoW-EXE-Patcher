import struct,sys
d=open('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe','rb').read()
def ro2va(o): return o-0x5DD800+0x9DF000
def va2off(va):
    if 0x401000<=va<0x9DF000: return va-0x400C00
    if 0x9DF000<=va<0xAB6000: return va-0x9DF000+0x5DD800
    if 0xAB6000<=va<0xAB6000+0x78E00: return va-0xAB6000+0x6B4000
    return None
def refs(va):
    pat=struct.pack('<I',va); hits=[]; p=d.find(pat)
    while p>=0:
        if 0x400<=p<0x5DD800: hits.append(p+0x400C00)
        p=d.find(pat,p+1)
    return hits
def findstr(s):
    b=s.encode()+b'\0'; res=[]; o=d.find(b)
    while o>=0:
        if d[o-1]==0 or True: res.append(o)
        o=d.find(b,o+1)
    return res
if __name__=='__main__':
    for s in sys.argv[1:]:
        if s.startswith('0x'):
            print(s,[hex(h) for h in refs(int(s,16))]); continue
        for o in findstr(s):
            if 0x5DD800<=o<0x6B4000:
                va=ro2va(o); print(repr(s),hex(va),[hex(h) for h in refs(va)])
