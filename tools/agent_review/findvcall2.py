# faster: only scan 0x680000-0x6B0000 and report all D3D device calls by vtable offset
import sys, capstone, collections
from capstone import x86
ORI='/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe'
D=open(ORI,'rb').read()
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32); md.detail=True; md.skipdata=True
ts=int(sys.argv[1],16); te=int(sys.argv[2],16)
ins=list(md.disasm(D[ts-0x400C00:te-0x400C00], ts))
res=collections.defaultdict(list)
for k,i in enumerate(ins):
    if i.mnemonic=='.byte': continue
    if i.mnemonic not in ('mov','call'): continue
    for op in i.operands:
        if op.type==x86.X86_OP_MEM and op.mem.base!=0 and op.mem.index==0 and 0<=op.mem.disp<0x200 and op.mem.disp%4==0:
            back=ins[max(0,k-10):k]
            if any('0x397c' in b.op_str for b in back):
                fwd=ins[k:k+8]
                if i.mnemonic=='call' or any(f.mnemonic=='call' for f in fwd):
                    res[op.mem.disp].append(i.address)
            break
for d in sorted(res): print('%03X'%d, ' '.join('%X'%a for a in res[d]))
