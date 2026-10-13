import sys,struct
d=open('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe','rb').read()
t0,t1=0x400,0x5DD800
def callers(tgt):
    r=[]
    for o in range(t0,t1-5):
        if d[o]==0xE8:
            rel=struct.unpack_from('<i',d,o+1)[0]
            if o+0x400C00+5+rel==tgt: r.append(o+0x400C00)
    return r
for a in sys.argv[1:]:
    print(a,[hex(x) for x in callers(int(a,16))])
