import sys,struct,re
ORI='/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe'
D=open(ORI,'rb').read()
def off2va(o):
    if 0x400<=o<0x5DD800: return o+0x400C00
    if 0x5DD800<=o<0x6B4000: return o-0x5DD800+0x9DF000
    if o>=0x6B4000: return o-0x6B4000+0xAB6000
pat=sys.argv[1].encode()
for m in re.finditer(re.escape(pat),D):
    o=m.start()
    # print the full C string around
    s=o
    while s>0 and D[s-1]!=0: s-=1
    e=D.index(b'\0',o)
    va=off2va(s)
    print('%08X  %r'%(va,D[s:e]))
