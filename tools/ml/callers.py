import struct,sys
d=open('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe','rb').read()
t=d[0x400:0x5DD800]
for a in sys.argv[1:]:
    tgt=int(a,16)
    res=[]
    for i in range(len(t)-5):
        if t[i] in (0xE8,0xE9):
            src=i+0x400+0x400C00
            if src+5+struct.unpack_from('<i',t,i+1)[0]==tgt: res.append(('call' if t[i]==0xE8 else 'jmp')+' '+hex(src))
    print(a,res)
