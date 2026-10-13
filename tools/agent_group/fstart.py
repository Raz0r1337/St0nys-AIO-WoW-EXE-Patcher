import sys
ORI='/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe'
D=open(ORI,'rb').read()
for a in sys.argv[1:]:
    v=int(a,16); o=v-0x400C00
    while o>0:
        if D[o-1]==0xCC and D[o]==0x55 and D[o+1]==0x8B and D[o+2]==0xEC: break
        if D[o-1]==0xCC and D[o]!=0xCC and D[o-2]==0xCC: break
        o-=1
    print(a,'-> %08X'%(o+0x400C00))
