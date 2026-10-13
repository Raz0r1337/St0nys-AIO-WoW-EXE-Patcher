import sys,capstone
ORI='/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe'
D=open(ORI,'rb').read()
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
def dis(va,n=40):
    off=va-0x400C00
    for i in md.disasm(D[off:off+n*8],va):
        print('%08X  %-24s %s %s'%(i.address,i.bytes.hex(),i.mnemonic,i.op_str)); n-=1
        if n<=0: break
for a in sys.argv[1:]:
    va,n=(a.split(':')+['30'])[:2]
    print('=== %s'%va); dis(int(va,16),int(n))
