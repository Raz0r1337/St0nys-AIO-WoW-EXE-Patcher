import sys,struct
ORI='/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe'
D=open(ORI,'rb').read()
base=0x400C00
for t in sys.argv[1:]:
    tgt=int(t,16); hits=[]
    for off in range(0x400,0x5F0000):
        if D[off]==0xE8:
            rel=struct.unpack_from('<i',D,off+1)[0]
            if off+base+5+rel==tgt: hits.append(off+base)
    print(t,[hex(h) for h in hits])
