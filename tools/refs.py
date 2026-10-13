import capstone,struct,sys
d=open('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe','rb').read()
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
def f2o(v):
    r=v-0x400000
    for va,vs,ra in [(0x1000,0x5dd3b3,0x400),(0x5df000,0xd6679,0x5dd800),(0x6b6000,0x78e00,0x6b4000)]:
        if va<=r<va+vs: return ra+r-va
def cstr(v):
    o=f2o(v)
    if o is None: return None
    e=d.find(b'\0',o); s=d[o:e]
    return s if 0<len(s)<160 and all(32<=c<127 or c in (9,10,13) for c in s) else None
def dis(vstart,n):
    o=vstart-0x400C00
    for i in md.disasm(d[o:o+n],vstart):
        s='  %08X  %-22s %s %s'%(i.address,i.bytes.hex(),i.mnemonic,i.op_str)
        for tok in i.op_str.replace('[',' ').replace(']',' ').replace(',',' ').split():
            if tok.startswith('0x'):
                v=int(tok,16); c=cstr(v) if v>0x9d0000 else None
                if c: s+='   ; "%s"'%c.decode()
        print(s)
if __name__=='__main__':
    for a in sys.argv[1:]:
        v,n=a.split(':'); print('---',v); dis(int(v,16),int(n))
