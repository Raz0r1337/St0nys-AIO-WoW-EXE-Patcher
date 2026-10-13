import struct
from asmgen import md,B1
def hx(bs): return ', '.join('0x%02X'%b for b in bs)
def emit(code, code_base_off, src, absf, relf, var='$c', extern_names=None, data_names=None, labels=None, comment_src=None):
    """code assembled at B1+code_base_off. absf/relf are section offsets. Returns PS lines."""
    extern_names=extern_names or {}; data_names=data_names or {}
    srclines=[l for l in src.strip('\n').split('\n')]
    cml=[l for l in (comment_src or src).strip('\n').split('\n')]
    assert len(cml)==len(srclines)
    insns=list(md.disasm(code,B1+code_base_off))
    assert sum(i.size for i in insns)==len(code)
    out=[]; k=0
    absset=set(absf); relset=set(relf)
    for li,l in enumerate(srclines):
        t=l.strip()
        if not t: continue
        if t.endswith(':'):
            out.append('    # %s'%t); continue
        i=insns[k]; k+=1
        off=i.address-B1  # section offset
        b=bytes(i.bytes)
        fix=None
        for j in range(len(b)-3):
            if off+j in absset: fix=('abs',j)
            if off+j in relset: fix=('rel',j)
        cm=' '.join(cml[li].strip().split())
        if fix is None:
            stmt='AddRaw %s @(%s)'%(var,hx(b))
        else:
            kind,j=fix
            v=struct.unpack_from('<I',b,j)[0]
            if kind=='abs':
                expr='($CAVE + 0x%X)'%(v-B1)
            else:
                tgt=(i.address+j+4+struct.unpack_from('<i',b,j)[0])&0xFFFFFFFF
                # rel to external at assemble-time base -> keep target, compute at patch time
                expr='(0x%X - ($CAVE + 0x%X))'%(tgt,off+j+4)
            parts=[]
            if j>0: parts.append('AddRaw %s @(%s)'%(var,hx(b[:j])))
            parts.append('AddLE32 %s %s'%(var,expr))
            if j+4<len(b): parts.append('AddRaw %s @(%s)'%(var,hx(b[j+4:])))
            stmt='; '.join(parts)
        out.append('    %-58s # %s'%(stmt,cm))
    assert k==len(insns)
    return out
