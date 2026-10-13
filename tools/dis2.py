import capstone,sys,re
d=open('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe','rb').read()
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
def cstr(va):
    o=va-0x9DF000+0x5DD800
    if not (0x5DD800<=o<0x6B4000): return None
    e=d.find(b'\0',o); s=d[o:e][:50]
    return s if len(s)>1 and all(32<=c<127 for c in s) else None
def dis(data,fs,n,marks=()):
    for i in md.disasm(data[fs:fs+n],fs+0x400C00):
        fo=i.address-0x400C00
        m='*' if any(a<=fo<b or fo<=a<fo+i.size for a,b in marks) else ' '
        ann=''
        for tok in re.findall(r'0x[0-9a-f]+',i.op_str):
            v=int(tok,16)
            if v>0x9DF000:
                c=cstr(v)
                if c: ann+='  ; "%s"'%c.decode()
        print('%s %08X  %-20s %s %s%s'%(m,i.address,i.bytes.hex(),i.mnemonic,i.op_str,ann))
if __name__=='__main__':
    data=d
    if sys.argv[1]!='-': data=open(sys.argv[1],'rb').read()
    for a in sys.argv[2:]:
        va,n=a.split(':'); fs=int(va,16)-0x400C00; print('--- %s'%va); dis(data,fs,int(n))
