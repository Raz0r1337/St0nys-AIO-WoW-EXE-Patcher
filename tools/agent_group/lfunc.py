import sys,struct,re
ORI='/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe'
D=open(ORI,'rb').read()
def off2va(o):
    if 0x400<=o<0x5DD800: return o+0x400C00
    if 0x5DD800<=o<0x6B4000: return o-0x5DD800+0x9DF000
    if o>=0x6B4000: return o-0x6B4000+0xAB6000
def va2off(v):
    if 0x401000<=v<0x9DF000: return v-0x400C00
    if 0x9DF000<=v<0xAB6000: return v-0x9DF000+0x5DD800
    return v-0xAB6000+0x6B4000
for name in sys.argv[1:]:
    pat=b'\0'+name.encode()+b'\0'
    i=D.find(pat)
    if i<0: print(name,'notfound'); continue
    sva=off2va(i+1)
    t=struct.pack('<I',sva)
    j=0
    while True:
        j=D.find(t,j)
        if j<0: break
        nxt=struct.unpack_from('<I',D,j+4)[0]
        print('%-28s str %08X ref@%08X next=%08X'%(name,sva,off2va(j),nxt))
        j+=1
