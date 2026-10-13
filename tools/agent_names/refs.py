import sys,struct
ORI='/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe'
D=open(ORI,'rb').read()
def off2va(o):
    if 0x400<=o<0x5DD800: return o+0x400C00
    if 0x5DD800<=o<0x6B4000: return o-0x5DD800+0x9DF000
    if o>=0x6B4000: return o-0x6B4000+0xAB6000
for a in sys.argv[1:]:
    t=struct.pack('<I',int(a,16))
    res=[]
    i=0
    while True:
        i=D.find(t,i)
        if i<0: break
        res.append('%08X'%off2va(i)); i+=1
    print(a,':',' '.join(res))
