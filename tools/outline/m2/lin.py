import capstone,struct,pickle,sys
d=open('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe','rb').read()
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32); md.detail=False
def sweep(a,b):
    out=[]
    va=a
    while va<b:
        o=va-0x400C00
        got=False
        for i in md.disasm(d[o:o+(b-va)],va):
            out.append((i.address,i.size,i.mnemonic,i.op_str)); va=i.address+i.size; got=True
        if va<b: va+=1
    return out
if __name__=='__main__':
    a=int(sys.argv[1],16); b=int(sys.argv[2],16)
    ins=sweep(a,b)
    pickle.dump(ins,open(sys.argv[3],'wb'))
    print(len(ins))
