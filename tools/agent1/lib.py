import capstone, struct, re, sys, os
ORI='/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe'
OUT='/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/rev/out'
TABLE='/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/agent1/table.txt'
d=open(ORI,'rb').read()
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32); md.detail=True
TEXT_F=0x400; TEXT_VA=0x401000; TEXT_RAW=0x5DD400
SECS=[('.text',0x400,0x401000,0x5DD400),('.rdata',0x5DD800,0x9DF000,0xD6800),('.data',0x6B4000,0xAB6000,0x78E00)]
def f2v(o):
    for n,f,v,s in SECS:
        if f<=o<f+s: return v+o-f
    return None
def v2f(v):
    for n,f,va,s in SECS:
        if va<=v<va+s: return f+v-va
    return None
def cstr(buf,v):
    o=v2f(v)
    if o is None: return None
    e=buf.find(b'\0',o); s=buf[o:e]
    return s if 0<len(s)<200 and all(32<=c<127 for c in s) else None
def fmt(i,buf):
    s='%08X  %-24s %s %s'%(i.address,i.bytes.hex(),i.mnemonic,i.op_str)
    for tok in re.findall(r'0x[0-9a-fA-F]+',i.op_str):
        v=int(tok,16)
        if v>=0x9D0000:
            c=cstr(buf,v)
            if c: s+='   ; "%s"'%c.decode()
    return s
def find_func_start(buf,off,maxback=0x2000):
    """scan backwards from file offset off for int3 padding followed by code"""
    o=off
    while o>off-maxback and o>0:
        if buf[o-1]==0xCC and buf[o]!=0xCC: return o
        o-=1
    return None
def dis(buf,vstart,vend,mark=None):
    o=v2f(vstart); n=vend-vstart
    out=[]
    for i in md.disasm(buf[o:o+n+16],vstart):
        if i.address>=vend: break
        tag=''
        if mark:
            ms,me=mark
            if ms<=i.address<me or (i.address<ms<i.address+i.size): tag='*'
        out.append('%1s %s'%(tag,fmt(i,buf)))
    return out
def load_patched(n):
    return open(os.path.join(OUT,'%d.exe'%n),'rb').read()
def table():
    rows=[]
    for line in open(TABLE):
        line=line.strip()
        if not line or line.startswith('#') or line.startswith('$') or line.startswith("'@"): continue
        p=line.split(';')
        if len(p)!=4: continue
        rows.append((p[0],int(p[1],16),bytes.fromhex(p[2]),int(p[3])))
    return rows
def branch_targets_into(buf,lo,hi,strict_inside=False):
    """linear sweep .text for E8/E9 rel32, 0F8x rel32, 7x/EB rel8 whose target VA lies in [lo,hi) (VA). returns list"""
    res=[]
    f=TEXT_F; end=TEXT_F+TEXT_RAW
    for o in range(f,end):
        b=buf[o]
        va=f2v(o)
        t=None
        if b in (0xE8,0xE9) and o+5<=end:
            rel=struct.unpack_from('<i',buf,o+1)[0]; t=va+5+rel; ln=5
        elif b==0x0F and o+6<=end and 0x80<=buf[o+1]<=0x8F:
            rel=struct.unpack_from('<i',buf,o+2)[0]; t=va+6+rel; ln=6
        elif (0x70<=b<=0x7F or b==0xEB or b in (0xE3,0xE0,0xE1,0xE2)) and o+2<=end:
            rel=struct.unpack_from('<b',buf,o+1)[0]; t=va+2+rel; ln=2
        if t is not None:
            if strict_inside:
                if lo<t<hi: res.append((va,o,ln,t))
            else:
                if lo<=t<hi: res.append((va,o,ln,t))
    return res
