import struct,sys
d=open('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe','rb').read()
def f2v(o): return o+0x400C00 if o<0x5DD800 else (o-0x5DD800+0x9DF000 if o<0x6B4000 else o-0x6B4000+0xAB6000)
for a in sys.argv[1:]:
    va=int(a,16); pat=struct.pack('<I',va); p=d.find(pat); hits=[]
    while p>=0: hits.append(hex(f2v(p))); p=d.find(pat,p+1)
    print(a,hits)
