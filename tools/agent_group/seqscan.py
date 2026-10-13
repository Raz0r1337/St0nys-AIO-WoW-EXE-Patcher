import sys,capstone,re
ORI='/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe'
D=open(ORI,'rb').read()
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
lo=0x401000; hi=0x9DE000
off=lo-0x400C00; end=hi-0x400C00
ins=[]
while off<end:
    got=False
    for i in md.disasm(D[off:min(end,off+0x10000)],off+0x400C00):
        ins.append((i.address,i.mnemonic+' '+i.op_str))
        off=i.address+i.size-0x400C00; got=True
    if not got: off+=1
import pickle
pickle.dump(ins,open('ins.pkl','wb'))
print(len(ins))
