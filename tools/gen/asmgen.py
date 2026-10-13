import keystone,capstone,struct
ks=keystone.Ks(keystone.KS_ARCH_X86,keystone.KS_MODE_32)
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
B1=0x01000000; B2=0x02345000
def asm(src,base):
    enc,_=ks.asm(src,base); return bytes(enc)
def reloc(src):
    """assemble at two bases; return (template@B1, absfix, relfix)"""
    a=asm(src,B1); b=asm(src,B2)
    assert len(a)==len(b),(len(a),len(b))
    delta=B2-B1; absf=[]; relf=[]
    i=0
    diff=[k for k in range(len(a)) if a[k]!=b[k]]
    done=set()
    for k in diff:
        if k in done: continue
        # find a 4-byte window starting at k-? containing k such that difference is +-delta
        found=False
        for s in range(k-3,k+1):
            if s<0 or s+4>len(a): continue
            va=struct.unpack_from('<I',a,s)[0]; vb=struct.unpack_from('<I',b,s)[0]
            if (vb-va)&0xFFFFFFFF==delta&0xFFFFFFFF: absf.append(s); done.update(range(s,s+4)); found=True; break
            if (va-vb)&0xFFFFFFFF==delta&0xFFFFFFFF: relf.append(s); done.update(range(s,s+4)); found=True; break
        assert found,hex(k)
    return a,sorted(set(absf)),sorted(set(relf))
def dis(code,base):
    for i in md.disasm(code,base): print('  %08X  %-24s %s %s'%(i.address,i.bytes.hex(),i.mnemonic,i.op_str))
def relocate(tpl,absf,relf,base):
    c=bytearray(tpl); d=base-B1
    for s in absf: struct.pack_into('<I',c,s,(struct.unpack_from('<I',c,s)[0]+d)&0xFFFFFFFF)
    for s in relf: struct.pack_into('<I',c,s,(struct.unpack_from('<I',c,s)[0]-d)&0xFFFFFFFF)
    return bytes(c)
def label_offsets(src,base,names):
    """offset of labels relative to base: append 'call L' per label and decode rel32"""
    full=asm(src,base)
    ext=asm(src+'\n'+'\n'.join('call %s'%n for n in names)+'\n',base)
    assert ext[:len(full)]==full
    out={}
    for i,n in enumerate(names):
        p=len(full)+5*i; assert ext[p]==0xE8
        rel=struct.unpack_from('<i',ext,p+1)[0]
        out[n]=base+p+5+rel-base
    return out
