import capstone,sys,re,struct
d=open('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe','rb').read()
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
TEXT0=0x400; TEXT1=0x5DD800
def va2off(va):
    if 0x401000<=va<0x9DF000: return va-0x400C00
    if 0x9DF000<=va<0xAB5679: return va-0x9DF000+0x5DD800
    if 0xAB6000<=va<0xAB6000+0x78E00: return va-0xAB6000+0x6B4000
    return None
def off2va(o):
    if TEXT0<=o<TEXT1: return o+0x400C00
    if 0x5DD800<=o<0x6B4000: return o-0x5DD800+0x9DF000
    if 0x6B4000<=o<0x6B4000+0x78E00: return o-0x6B4000+0xAB6000
def cstr(va):
    o=va2off(va)
    if o is None or not (0x5DD800<=o<0x6B4000+0x78E00): return None
    e=d.find(b'\0',o); s=d[o:e][:60]
    return s if len(s)>1 and all(32<=c<127 for c in s) else None
def u32(va): return struct.unpack('<I',d[va2off(va):va2off(va)+4])[0]
def dis(va,n,out=True):
    o=va2off(va); res=[]
    for i in md.disasm(d[o:o+n],va):
        ann=''
        for tok in re.findall(r'0x[0-9a-f]+',i.op_str):
            v=int(tok,16)
            if v>=0x9DF000:
                c=cstr(v)
                if c: ann+='  ; "%s"'%c.decode()
        line='%08X  %-22s %s %s%s'%(i.address,i.bytes.hex(),i.mnemonic,i.op_str,ann)
        res.append(line)
        if out: print(line)
        if i.mnemonic=='int3' and out: pass
    return res
def strva(s):
    b=s.encode()+b'\0'; r=[]
    o=d.find(b)
    while o>=0:
        if d[o-1]==0: r.append(off2va(o))
        o=d.find(b,o+1)
    return r
def refs(val, text_only=True):
    pat=struct.pack('<I',val); r=[]; p=d.find(pat)
    while p>=0:
        if (not text_only) or TEXT0<=p<TEXT1: r.append(off2va(p))
        p=d.find(pat,p+1)
    return r
def calls(target):
    r=[]
    # E8 rel32
    T=d[TEXT0:TEXT1]
    import re as _re
    for m in _re.finditer(b'\xe8',T):
        p=m.start()
        va=p+TEXT0+0x400C00
        rel=struct.unpack('<i',T[p+1:p+5])[0] if p+5<=len(T) else None
        if rel is not None and (va+5+rel)&0xffffffff==target: r.append(va)
    for m in _re.finditer(b'\xe9',T):
        p=m.start(); va=p+TEXT0+0x400C00
        rel=struct.unpack('<i',T[p+1:p+5])[0] if p+5<=len(T) else None
        if rel is not None and (va+5+rel)&0xffffffff==target: r.append(('jmp',va))
    return r
def fstart(va):
    # scan back for CC/90 padding boundary
    o=va2off(va)
    while o>TEXT0:
        if d[o-1] in (0xCC,0x90) and d[o-2] in (0xCC,0x90,0xC3,0xC2) : return off2va(o)
        if d[o-1]==0xC3 and d[o] in (0x55,0x56,0x53,0x57,0x83,0x8B,0x6A,0x51,0x81,0xA1,0xD9,0x68,0xB8,0x33,0xE8) and o!=va2off(va): 
            pass
        o-=1
if __name__=='__main__':
    cmd=sys.argv[1]
    if cmd=='d':
        for a in sys.argv[2:]:
            va,n=a.split(':'); print('---',va); dis(int(va,16),int(n,16) if n.startswith('0x') else int(n))
    elif cmd=='s':
        for s in sys.argv[2:]:
            for v in strva(s): print(s,hex(v),[hex(x) for x in refs(v)])
    elif cmd=='r':
        for a in sys.argv[2:]: print(a,[hex(x) for x in refs(int(a,16))])
    elif cmd=='c':
        for a in sys.argv[2:]: print(a,[hex(x) if isinstance(x,int) else (x[0],hex(x[1])) for x in calls(int(a,16))])
    elif cmd=='f':
        for a in sys.argv[2:]: print(a,hex(fstart(int(a,16))))
