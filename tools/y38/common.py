import struct,capstone,re
EXE='/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe'
d=open(EXE,'rb').read()
def va2fo(va):
    if 0x401000<=va<0x9DF000: return va-0x400C00
    if 0x9DF000<=va<0xAB6000: return va-0x9DF000+0x5DD800
    if 0xAB6000<=va<0xAB6000+0x78E00: return va-0xAB6000+0x6B4000
    return None
def fo2va(fo):
    if 0x400<=fo<0x5DD800: return fo+0x400C00
    if 0x5DD800<=fo<0x6B4000: return fo-0x5DD800+0x9DF000
    if 0x6B4000<=fo<0x6B4000+0x78E00: return fo-0x6B4000+0xAB6000
def cstr(va,maxl=80):
    o=va2fo(va)
    if o is None or not (0x5DD800<=o<0x6B4000+0x78E00): return None
    e=d.find(b'\0',o); s=d[o:e][:maxl]
    return s.decode() if len(s)>1 and all(32<=c<127 for c in s) else None
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
