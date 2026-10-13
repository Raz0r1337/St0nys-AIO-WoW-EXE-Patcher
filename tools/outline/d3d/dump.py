import capstone
d=open('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe','rb').read()
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
md.skipdata=True
out=open('text.asm','w')
start=0x400; end=0x5DD800
pos=start
CH=0x10000
while pos<end:
    last=pos
    for i in md.disasm(d[pos:min(end,pos+CH+16)],pos+0x400C00):
        if i.address-0x400C00>=pos+CH: break
        out.write('%08X %s %s\n'%(i.address,i.mnemonic,i.op_str))
        last=i.address-0x400C00+i.size
    pos=last
out.close()
