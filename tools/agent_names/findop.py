import sys,capstone,re
ORI='/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe'
D=open(ORI,'rb').read()
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
pat=re.compile(sys.argv[1])
lo=int(sys.argv[2],16) if len(sys.argv)>2 else 0x401000
hi=int(sys.argv[3],16) if len(sys.argv)>3 else 0x9DE000
# linear sweep with resync: disassemble from every function-ish start? do naive: sweep, on failure skip a byte
off=lo-0x400C00; end=hi-0x400C00
while off<end:
    got=False
    for i in md.disasm(D[off:min(end,off+0x1000)],off+0x400C00):
        s='%s %s'%(i.mnemonic,i.op_str)
        if pat.search(s): print('%08X  %s'%(i.address,s))
        off=i.address+i.size-0x400C00
        got=True
    if not got: off+=1
