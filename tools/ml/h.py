import capstone,re,struct,sys
EXE='/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe'
d=open(EXE,'rb').read()
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
def v2f(va):
    if 0x401000<=va<0x9DE400: return va-0x400C00
    if 0x9DF000<=va<0xAB5800: return va-0x9DF000+0x5DD800
    return va-0xAB6000+0x6B4000
def cstr(va):
    o=va-0x9DF000+0x5DD800
    if not (0x5DD800<=o<0x6B4000): return None
    e=d.find(b'\0',o); s=d[o:e][:60]
    return s if len(s)>1 and all(32<=c<127 for c in s) else None
def dis(va,n,marks=(),data=None):
    data=data or d
    fs=v2f(va)
    for i in md.disasm(data[fs:fs+n],va):
        m='*' if any(a<=i.address<b or i.address<=a<i.address+i.size for a,b in marks) else ' '
        ann=''
        for tok in re.findall(r'0x[0-9a-f]+',i.op_str):
            v=int(tok,16)
            if v>0x9DF000:
                c=cstr(v)
                if c: ann+='  ; "%s"'%c.decode('latin1')
        print('%s %08X  %-22s %s %s%s'%(m,i.address,i.bytes.hex(),i.mnemonic,i.op_str,ann))
def fstart(va):
    o=v2f(va)
    while o>0:
        if d[o:o+3]==b'\x55\x8b\xec' and d[o-1] in (0xCC,0xC3,0x90): return o+0x400C00
        o-=1
def callers(tgt):
    t=d[0x400:0x5DD800]; res=[]
    for i in range(len(t)-5):
        if t[i] in (0xE8,0xE9):
            src=i+0x401000
            if src+5+struct.unpack_from('<i',t,i+1)[0]==tgt: res.append(src)
    return res
def refs(v):
    p=struct.pack('<I',v); o=0; r=[]
    while True:
        o=d.find(p,o)
        if o<0: break
        r.append(o+0x400C00 if o<0x5DD800 else o); o+=1
    return r
