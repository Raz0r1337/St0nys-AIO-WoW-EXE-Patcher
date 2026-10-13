import struct,sys
d=open('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe','rb').read()
def ro2va(o): return o-0x5DD800+0x9DF000
for s in sys.argv[1:]:
    o=d.find(s.encode()+b'\0')
    while o>=0 and d[o-1]!=0: o=d.find(s.encode()+b'\0',o+1)
    va=ro2va(o); pat=struct.pack('<I',va)
    hits=[]; p=d.find(pat)
    while p>=0:
        if p<0x5DD800: hits.append(hex(p+0x400C00))
        p=d.find(pat,p+1)
    print(s,hex(va),hits)
