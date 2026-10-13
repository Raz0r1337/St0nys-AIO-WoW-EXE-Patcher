# find COM-style calls through the D3D device ([x+0x397C]) at a given vtable offset, in the whole .text
import sys, capstone
from capstone import x86
ORI='/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe'
D=open(ORI,'rb').read()
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32); md.detail=True; md.skipdata=True
offs=[int(a,16) for a in sys.argv[1:]]
ts=0x401000; te=0x9DE000
ins=list(md.disasm(D[ts-0x400C00:te-0x400C00], ts))
print(len(ins))
for k,i in enumerate(ins):
    if i.mnemonic=='.byte': continue
    hit=False
    for op in i.operands:
        if op.type==x86.X86_OP_MEM and op.mem.base!=0 and op.mem.index==0 and op.mem.disp in offs:
            hit=True
    if not hit: continue
    # look back up to 12 instr for 0x397c
    back=ins[max(0,k-12):k]
    if any('0x397c' in b.op_str for b in back):
        fwd=ins[k:k+6]
        if any(f.mnemonic=='call' for f in fwd):
            print('%08X  %s %s   | %s'%(i.address,i.mnemonic,i.op_str,' ; '.join('%s %s'%(b.mnemonic,b.op_str) for b in back[-6:])))
