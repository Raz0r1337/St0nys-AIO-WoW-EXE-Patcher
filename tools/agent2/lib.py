import capstone, struct, sys, re
ORIG='/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe'
OUT='/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/rev/out'
PS1='/home/user/St0nys-WoW-EXE-Patcher/apply_patches.ps1'
orig=open(ORIG,'rb').read()
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32); md.detail=True
# (file_off, va, raw_size, vsize)
SECS={'.text':(0x400,0x401000,0x5DD400,0x5DD3B3),'.rdata':(0x5DD800,0x9DF000,0xD6800,0xD6679),'.data':(0x6B4000,0xAB6000,0x78E00,0x78E00),'.tls':(0x72DE00,0x9D2000,0x200,0x200),'.rsrc':(0x72E000,0x9D3000,0,0)}
def off2va(o):
    for n,(fo,va,rs,vs) in SECS.items():
        if fo<=o<fo+rs: return va+o-fo
    return None
def va2off(v):
    for n,(fo,va,rs,vs) in SECS.items():
        if va<=v<va+max(rs,vs): return fo+v-va
    return None
def cstr(d,v):
    o=va2off(v)
    if o is None: return None
    e=d.find(b'\0',o); s=d[o:e]
    return s if 0<len(s)<200 and all(32<=c<127 or c in (9,10,13) for c in s) else None
def load(n): return open(f'{OUT}/{n}.exe','rb').read()
def func_start(d,off,maxback=0x4000):
    """nearest preceding position p with d[p-1]==0xCC and d[p]!=0xCC"""
    p=off
    while p>off-maxback and p>0x400:
        if d[p-1]==0xCC and d[p]!=0xCC: return p
        p-=1
    return None
def func_end(d,off,maxfwd=0x8000):
    """first position q>=off with d[q]==0xCC (start of int3 padding run of len>=2) """
    q=off
    while q<off+maxfwd:
        if d[q]==0xCC and d[q+1]==0xCC: return q
        q+=1
    return None
def annot(d,i):
    s=''
    for tok in re.findall(r'0x[0-9a-fA-F]+',i.op_str):
        v=int(tok,16)
        if v>=0x9d0000:
            c=cstr(d,v)
            if c: s+='   ; "%s"'%c.decode()
    return s
def dis(d,start_off,end_off,marks=()):
    """linear disassemble file [start_off,end_off) ; marks=list of (a,b) file ranges to flag"""
    va=off2va(start_off)
    out=[]
    for i in md.disasm(d[start_off:end_off],va):
        o=va2off(i.address)
        flag=' '
        for a,b in marks:
            if a<=o<b or a<o+i.size<=b: flag='*'
        out.append('%s %08X (f%06X) %-24s %s %s%s'%(flag,i.address,o,i.bytes.hex(),i.mnemonic,i.op_str,annot(d,i)))
    return '\n'.join(out)
def table():
    src=open(PS1,encoding='utf-8',errors='replace').read()
    a=src.rindex('\n# BEGIN ORIGINAL-BYTES'); z=src.index('\n# END ORIGINAL-BYTES',a)
    rows=[]
    for line in src[a:z].splitlines():
        m=re.match(r'^(\w+);([0-9A-Fa-f]+);([0-9A-Fa-f]*);([01])$',line.strip())
        if m: rows.append((m.group(1),int(m.group(2),16),bytes.fromhex(m.group(3)),int(m.group(4))))
    return rows
