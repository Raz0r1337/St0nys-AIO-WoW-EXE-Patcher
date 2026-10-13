import sys, struct
D=open('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe','rb').read()
# .text: file off = va-0x400C00 ; scan E8/E9 rel32
lo=0x1000-0xC00+0x400C00
for t in [int(a,16) for a in sys.argv[1:]]:
    res=[]
    for o in range(0x400, 0x5A0000):
        b=D[o]
        if b in (0xE8,0xE9):
            va=o+0x400C00
            r=struct.unpack_from('<i',D,o+1)[0]
            if va+5+r==t: res.append('%s%08X'%('c' if b==0xE8 else 'j',va))
    print('%08X:'%t,' '.join(res))
