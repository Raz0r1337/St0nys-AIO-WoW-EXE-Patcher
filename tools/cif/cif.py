import sys,struct,capstone
sys.path.insert(0,'/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/cif')
from parse import entries
W='/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe'
orig=open(W,'rb').read()
E=entries()
FIX={0x35813C: bytes.fromhex('01 99 6A 00 68 70 EB 5E 00 33 C2 8D 4D F8 51 2B C2 50 B9 28 D8 C5 00 C7 45 F8'.replace(' ',''))}
def build(fixes=FIX, skip=()):
    d=bytearray(orig)
    for off,old,new in E:
        if off in skip: continue
        new=fixes.get(off,new)
        d[off:off+len(new)]=new
    return bytes(d)
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
def va(fo): return fo+0x400C00
def fo(v): return v-0x400C00
def dis(data,vstart,n,mark=()):
    out=[]
    for i in md.disasm(data[fo(vstart):fo(vstart)+n],vstart):
        m='*' if any(a<=fo(i.address)<a+l or fo(i.address)<=a<fo(i.address)+i.size for a,l in mark) else ' '
        out.append('%s %08X  %-26s %s %s'%(m,i.address,i.bytes.hex(),i.mnemonic,i.op_str))
    return out
def func_start(v):
    o=fo(v)
    while o>0:
        if orig[o-1]==0xCC and orig[o]!=0xCC: return va(o)
        o-=1
def region(v0,v1,data,extra=24):
    s=func_start(v0)
    if v0-s>0x200: s=v0-0x40  # fallback
    lines=[]
    for i in md.disasm(data[fo(s):fo(v1)+extra],s):
        if i.address+i.size<=v0-24: continue
        mark='*' if any(off<=fo(i.address)+k<off+len(n) for off,_,n in E for k in range(i.size)) else ' '
        lines.append('%s %08X  %-24s %s %s'%(mark,i.address,i.bytes.hex(),i.mnemonic,i.op_str))
    return lines
def show(v0,v1,extra=24):
    P=build()
    a=region(v0,v1,orig,extra); b=region(v0,v1,P,extra)
    print('=== OLD'); print('\n'.join(a)); print('=== NEW'); print('\n'.join(b))
def show_from(s,v1,extra=24,data2=None):
    P=data2 if data2 is not None else build()
    for name,data in (('OLD',orig),('NEW',P)):
        print('===',name)
        for i in md.disasm(data[fo(s):fo(v1)+extra],s):
            mark='*' if any(off<=fo(i.address)+k<off+len(n) for off,_,n in E for k in range(i.size)) else ' '
            print('%s %08X  %-24s %s %s'%(mark,i.address,i.bytes.hex(),i.mnemonic,i.op_str))
def win(data,v,before=0x18,after=0x18):
    o=fo(v)
    for k in range(0x80,0,-1):
        ins=list(md.disasm(data[o-k:o+after+0x10],va(o-k)))
        if any(i.address==v for i in ins): break
    out=[]
    for i in ins:
        if v-before<=i.address<=v+after:
            mark='*' if any(off<=fo(i.address)+kk<off+len(n) for off,_,n in E for kk in range(i.size)) else ' '
            out.append('%s %08X  %-22s %s %s'%(mark,i.address,i.bytes.hex(),i.mnemonic,i.op_str))
    return out
def side(v,before=0x18,after=0x18,P=None):
    P=P or build()
    print('#### OLD'); print('\n'.join(win(orig,v,before,after)))
    print('#### NEW'); print('\n'.join(win(P,v,before,after)))
