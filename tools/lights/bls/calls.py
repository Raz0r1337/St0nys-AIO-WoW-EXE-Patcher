import sys,struct
d=open('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe','rb').read()
t=d[0x400:0x5DD800]
for a in sys.argv[1:]:
    tgt=int(a,16); res=[]
    for i in range(len(t)-5):
        if t[i] in (0xe8,0xe9):
            src=i+0x400+0x400C00
            if src+5+struct.unpack_from('<i',t,i+1)[0]==tgt: res.append(hex(src)+('j' if t[i]==0xe9 else ''))
    # also absolute refs
    pat=struct.pack('<I',tgt); p=d.find(pat)
    while p>=0:
        res.append('abs@'+hex(p+0x400C00 if p<0x5DD800 else (p-0x5DD800+0x9DF000 if p<0x6B4000 else p-0x6B4000+0xAB6000))); p=d.find(pat,p+1)
    print(a,res)
