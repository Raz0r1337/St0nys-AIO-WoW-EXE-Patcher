import struct, capstone
ORI='/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe'
D=open(ORI,'rb').read()
F=lambda va: va-0x400C00
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
import sys
bt=int(sys.argv[1],16); dt=int(sys.argv[2],16); n=int(sys.argv[3],16)
cases={}
for i in range(n+1):
    b=D[F(bt)+i]; tgt=struct.unpack_from('<I',D,F(dt)+4*b)[0]
    cases.setdefault(tgt,[]).append(i)
for tgt in sorted(cases):
    idx=cases[tgt]
    ins=[]
    for k in md.disasm(D[F(tgt):F(tgt)+80],tgt):
        ins.append('%s %s'%(k.mnemonic,k.op_str))
        if k.mnemonic in ('ret','jmp') or len(ins)>=10: break
    rng='%X-%X'%(idx[0],idx[-1]) if len(idx)>1 else '%X'%idx[0]
    print('%08X [%s] n=%d: %s'%(tgt,rng,len(idx),' ; '.join(ins)))
