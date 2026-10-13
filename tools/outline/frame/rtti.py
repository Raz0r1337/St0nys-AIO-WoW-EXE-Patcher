import struct,sys
sys.path.insert(0,'/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/outline/frame')
from x import *
def off2va(o):
    if 0x400<=o<0x5DD800: return o+0x400C00
    if 0x5DD800<=o<0x6B4000: return o-0x5DD800+0x9DF000
    if 0x6B4000<=o<0x6B4000+0x78E00: return o-0x6B4000+0xAB6000
for name in sys.argv[1:]:
    o=d.find(name.encode()+b"\0")
    if o<0: print(name,"notfound"); continue
    td=off2va(o-8)
    print(name,'TD',hex(td))
    # COL: sig(0), off, cdOff, pTD, pCHD
    pat=struct.pack('<I',td); p=d.find(pat)
    while p>=0:
        if 0x5DD800<=p<0x6B4000:
            col=off2va(p-12)
            sig,off,cd=struct.unpack('<III',d[p-12:p])
            if sig==0:
                # find vtable: pointer to col
                q=d.find(struct.pack('<I',col))
                while q>=0:
                    vt=off2va(q+4)
                    ents=struct.unpack('<40I',d[q+4:q+4+160])
                    print('  COL',hex(col),'off',off,'vtable',hex(vt))
                    print('   ',' '.join('%d:%x'%(i,e) for i,e in enumerate(ents)))
                    q=d.find(struct.pack('<I',col),q+1)
        p=d.find(pat,p+1)
