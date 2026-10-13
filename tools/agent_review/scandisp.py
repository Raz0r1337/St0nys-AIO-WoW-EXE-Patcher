# scan .text of the original exe for instructions with memory displacement in a range
import sys, struct, capstone
from capstone import x86
ORI='/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe'
D=open(ORI,'rb').read()
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32); md.detail=True; md.skipdata=True
lo=int(sys.argv[1],16); hi=int(sys.argv[2],16)
ts=int(sys.argv[3],16) if len(sys.argv)>3 else 0x401000
te=int(sys.argv[4],16) if len(sys.argv)>4 else 0x9E0000
off=ts-0x400C00
for i in md.disasm(D[off:te-0x400C00], ts):
    if i.mnemonic=='.byte': continue
    for op in i.operands:
        if op.type==x86.X86_OP_MEM and op.mem.base!=0 and lo<=op.mem.disp<hi:
            print('%08X  %s %s'%(i.address,i.mnemonic,i.op_str)); break
