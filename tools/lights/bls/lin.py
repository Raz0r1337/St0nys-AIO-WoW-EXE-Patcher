import capstone,pickle
d=open('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe','rb').read()
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
md.skipdata=True
out=[]
for i in md.disasm(d[0x400:0x5DD800],0x401000):
    out.append((i.address,i.size,i.mnemonic,i.op_str))
pickle.dump(out,open('lin.pkl','wb'))
print(len(out))
