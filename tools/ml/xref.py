import struct,sys
d=open('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe','rb').read()
for a in sys.argv[1:]:
    v=int(a,16); p=struct.pack('<I',v); o=0
    while True:
        o=d.find(p,o)
        if o<0: break
        va=o+0x400C00 if o<0x5DD800 else (o-0x5DD800+0x9DF000 if o<0x6B4000 else o-0x6B4000+0xAB6000)
        print(a,'ref at file',hex(o),'va',hex(va),d[o-2:o].hex())
        o+=1
