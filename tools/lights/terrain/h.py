import capstone,struct,re,sys,os,pickle
D=open('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe','rb').read()
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32); md.detail=False
def v2o(va):
    if 0x401000<=va<0x9DF000: return va-0x400C00
    if 0x9DF000<=va<0xAB6000: return va-0x9DF000+0x5DD800
    if 0xAB6000<=va<0xAB6000+0x78E00: return va-0xAB6000+0x6B4000
    return None
def rd(va,n): o=v2o(va); return D[o:o+n]
def u32(va): return struct.unpack('<I',rd(va,4))[0]
def f32(va): return struct.unpack('<f',rd(va,4))[0]
def cstr(va):
    o=v2o(va)
    if o is None: return None
    e=D.find(b'\0',o); s=D[o:e][:80]
    return s if len(s)>1 and all(32<=c<127 or c in (9,10) for c in s) else None
TEXT=D[0x400:0x5DD800]
def dis(va,n,out=True):
    r=[]
    for i in md.disasm(rd(va,n),va):
        ann=''
        for tok in re.findall(r'0x[0-9a-f]+',i.op_str):
            v=int(tok,16)
            if v>=0x9DF000:
                c=cstr(v)
                if c: ann+='  ; "%s"'%c.decode(errors='replace')
        s='%08X  %-22s %s %s%s'%(i.address,i.bytes.hex(),i.mnemonic,i.op_str,ann)
        r.append(s)
        if out: print(s)
    return r
def calls_to(target):
    res=[]
    t=TEXT
    p=t.find(b'\xe8')
    # brute: scan all e8 positions
    import numpy as np
    return res
def find_bytes(b,start=0x401000,end=0x9DF000):
    res=[];o=v2o(start);oe=v2o(end-1)+1
    p=D.find(b,o)
    while 0<=p<oe:
        res.append(p+0x400C00 if p<0x5DD800 else None); p=D.find(b,p+1)
    return res
def xref_imm(val):
    """find code containing 4-byte LE val"""
    return find_bytes(struct.pack('<I',val))
def callers(target):
    res=[]
    o=0x400
    while True:
        o=D.find(b'\xe8',o,0x5DD800)
        if o<0: break
        va=o+0x400C00
        rel=struct.unpack('<i',D[o+1:o+5])[0]
        if va+5+rel==target: res.append(va)
        o+=1
    return res
def fstart(va):
    o=v2o(va)
    while o>0x400:
        if D[o-1] in (0xcc,0x90,0xc3) and D[o:o+3]==b'\x55\x8b\xec': return o+0x400C00
        if D[o-1]==0xcc and D[o-2]==0xcc and D[o]!=0xcc: return o+0x400C00
        o-=1
def insn_refs(val):
    out=[];seen=set()
    for x in xref_imm(val):
        if x is None: continue
        for back in range(1,9):
            for i in md.disasm(rd(x-back,16),x-back):
                if i.address+i.size>=x+4 and i.address<x and ('0x%x'%val) in i.op_str and i.address not in seen:
                    # validate by disassembling from function start? accept
                    seen.add(i.address); out.append(i)
                break
    return out
