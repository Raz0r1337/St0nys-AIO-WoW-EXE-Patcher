import sys,capstone,struct
ORI='/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe'
D=open(ORI,'rb').read()
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
def va2off(va):
    if va>=0xAB6000: return va-0xAB6000+0x6B4000
    if va>=0x9DF000: return va-0x9DF000+0x5DD800
    return va-0x400C00
def rstr(va):
    try:
        o=va2off(va)
        if o<0 or o>=len(D): return None
        e=D.index(b'\0',o)
        s=D[o:e]
        if 3<=len(s)<80 and all(32<=c<127 for c in s): return s.decode()
    except Exception: return None
    return None
def dis(va,end):
    off=va2off(va)
    code=D[off:off+(end-va)]
    for i in md.disasm(code,va):
        ann=''
        import re
        for m in re.finditer(r'0x([0-9a-f]{6,8})',i.op_str):
            v=int(m.group(1),16)
            s=rstr(v)
            if s and 0x9DF000<=v<0xAB6000: ann+=' ; "%s"'%s
        print('%08X  %-20s %s %s%s'%(i.address,i.bytes.hex()[:20],i.mnemonic,i.op_str,ann))
a=int(sys.argv[1],16); b=int(sys.argv[2],16)
dis(a,b)
