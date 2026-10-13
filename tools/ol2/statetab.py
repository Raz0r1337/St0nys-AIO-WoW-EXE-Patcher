import sys, struct, capstone
D=open('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe','rb').read()
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
def off(va):
    # find section
    pe=struct.unpack_from('<I',D,0x3C)[0]; ns=struct.unpack_from('<H',D,pe+6)[0]; so=struct.unpack_from('<H',D,pe+20)[0]
    st=pe+24+so
    for i in range(ns):
        name,vs,vaddr,rs,ro=struct.unpack_from('<8sIIII',D,st+40*i)
        if vaddr+0x400000<=va<vaddr+0x400000+max(vs,rs): return va-0x400000-vaddr+ro
    raise Exception(hex(va))
BT=0x6A403C; JT=0x6A3FAC
handlers={}
for i in range(0xB6):
    h=D[off(BT+i)]
    a=struct.unpack_from('<I',D,off(JT+4*h))[0]
    handlers.setdefault(a,[]).append(i)
for a,idx in sorted(handlers.items()):
    ins=list(md.disasm(D[off(a):off(a)+60],a))[:12]
    txt='; '.join('%s %s'%(x.mnemonic,x.op_str) for x in ins)
    print('%08X idx=%s\n    %s'%(a,','.join('%X'%i for i in idx),txt))
